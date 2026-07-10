"""Stage2F frozen-threshold validation on unseen HyperGranular-RAG queries."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np

from stage2_dense_replication import (
    evaluate_query,
    fixed_retrieve,
    load_jsonl,
    load_or_build_embeddings,
    normalize_matrix,
)
from stage2d_protected_rerank import expansion_candidates, protected_rerank


@dataclass(frozen=True)
class Strategy:
    strategy_id: str
    score_floor: float | None
    protect_n: int
    insert_budget: int
    role: str


@dataclass(frozen=True)
class Comparison:
    comparison_id: str
    strategy_a: str
    strategy_b: str
    metrics: tuple[str, ...]


COMPARISONS = (
    Comparison(
        "stage2d_reference_vs_fixed",
        "unfiltered_p5_i2",
        "dense_fixed",
        ("evidence_recall_at_10", "chain_recall_at_10", "evidence_recall_at_20", "chain_recall_at_20"),
    ),
    Comparison(
        "primary_q25_p5_i4_vs_fixed",
        "score_q25_p5_i4",
        "dense_fixed",
        ("evidence_recall_at_10", "chain_recall_at_10", "evidence_recall_at_20", "chain_recall_at_20"),
    ),
    Comparison(
        "q25_filter_p5_i4",
        "score_q25_p5_i4",
        "unfiltered_p5_i4",
        (
            "evidence_recall_at_10",
            "chain_recall_at_10",
            "evidence_recall_at_20",
            "chain_recall_at_20",
            "false_insert_rate",
            "avg_inserted_units",
        ),
    ),
    Comparison(
        "q25_p10_i4_vs_fixed",
        "score_q25_p10_i4",
        "dense_fixed",
        ("evidence_recall_at_20", "chain_recall_at_20"),
    ),
    Comparison(
        "q25_filter_p10_i4",
        "score_q25_p10_i4",
        "unfiltered_p10_i4",
        ("chain_recall_at_20", "false_insert_rate", "avg_inserted_units"),
    ),
    Comparison(
        "q50_filter_p5_i2",
        "score_q50_p5_i2",
        "unfiltered_p5_i2",
        ("evidence_recall_at_10", "chain_recall_at_10", "false_insert_rate", "avg_inserted_units"),
    ),
)


def load_calibration_floor(path: Path, filter_name: str) -> float:
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = [
            row
            for row in csv.DictReader(stream)
            if row["dataset"] == "ALL"
            and row["method"] == "gated"
            and row["filter_name"] == filter_name
            and row["score_floor"]
        ]
    if not rows:
        raise ValueError(f"Calibration floor not found for {filter_name}: {path}")
    values = [float(row["score_floor"]) for row in rows]
    if max(values) - min(values) > 1e-12:
        raise ValueError(f"Calibration floor is inconsistent for {filter_name}: {values}")
    return values[0]


def build_strategies(q25_floor: float, q50_floor: float) -> tuple[Strategy, ...]:
    return (
        Strategy("dense_fixed", None, 0, 0, "primary baseline"),
        Strategy("unfiltered_p5_i2", None, 5, 2, "Stage2D reference"),
        Strategy("unfiltered_p5_i4", None, 5, 4, "matched q25 Top-10 control"),
        Strategy("score_q25_p5_i4", q25_floor, 5, 4, "primary frozen strategy"),
        Strategy("unfiltered_p10_i4", None, 10, 4, "matched q25 Top-20 control"),
        Strategy("score_q25_p10_i4", q25_floor, 10, 4, "secondary long-context strategy"),
        Strategy("score_q50_p5_i2", q50_floor, 5, 2, "secondary noise-control strategy"),
    )


def preflight_audit(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    calibration_queries: list[dict[str, Any]],
) -> dict[str, Any]:
    query_ids = [row["query_id"] for row in queries]
    calibration_ids = {row["query_id"] for row in calibration_queries}
    duplicates = len(query_ids) - len(set(query_ids))
    overlap = set(query_ids) & calibration_ids
    datasets = Counter(row["dataset"] for row in queries)
    missing_gold = sum(1 for row in queries if not row.get("gold_unit_ids"))
    unit_query_ids = {row["query_id"] for row in units}
    missing_unit_groups = set(query_ids) - unit_query_ids
    foreign_unit_groups = unit_query_ids - set(query_ids)
    if len(queries) != 400:
        raise ValueError(f"Expected 400 test queries, found {len(queries)}")
    if datasets != Counter({"hotpotqa": 200, "musique": 200}):
        raise ValueError(f"Unexpected dataset counts: {dict(datasets)}")
    if duplicates:
        raise ValueError(f"Duplicate test query ids: {duplicates}")
    if overlap:
        raise ValueError(f"Calibration/test query overlap: {sorted(overlap)[:5]}")
    if missing_gold:
        raise ValueError(f"Test queries without mapped gold evidence: {missing_gold}")
    if missing_unit_groups or foreign_unit_groups:
        raise ValueError(
            f"Unit/query mismatch: missing={len(missing_unit_groups)}, foreign={len(foreign_unit_groups)}"
        )
    return {
        "test_queries": len(queries),
        "test_units": len(units),
        "test_gold_units": sum(len(row["gold_unit_ids"]) for row in queries),
        "dataset_counts": dict(datasets),
        "duplicate_query_ids": duplicates,
        "calibration_overlap": len(overlap),
        "queries_missing_gold": missing_gold,
    }


def apply_score_floor(candidates: list[dict[str, Any]], floor: float | None) -> list[dict[str, Any]]:
    if floor is None:
        return candidates
    return [row for row in candidates if row["score"] >= floor]


def aggregate(rows: list[dict[str, Any]], strategies: tuple[Strategy, ...], k_values: list[int]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["dataset"], row["strategy_id"])].append(row)
        grouped[("ALL", row["strategy_id"])].append(row)
    strategy_by_id = {row.strategy_id: row for row in strategies}
    output: list[dict[str, Any]] = []
    for (dataset, strategy_id), items in grouped.items():
        strategy = strategy_by_id[strategy_id]
        denom = len(items)
        inserted = sum(row["inserted_units"] for row in items)
        inserted_gold = sum(row["inserted_gold_units"] for row in items)
        candidate_count = sum(row["candidate_count"] for row in items)
        filtered_count = sum(row["filtered_candidate_count"] for row in items)
        summary: dict[str, Any] = {
            "dataset": dataset,
            "strategy_id": strategy_id,
            "role": strategy.role,
            "score_floor": strategy.score_floor,
            "protect_n": strategy.protect_n,
            "insert_budget": strategy.insert_budget,
            "queries": denom,
            "avg_mrr": sum(row["mrr"] for row in items) / denom,
            "boundary_rate": sum(row["is_boundary"] for row in items) / denom,
            "hyperedge_rate": sum(1.0 if row["selected_edge_count"] > 0 else 0.0 for row in items) / denom,
            "avg_selected_edges": sum(row["selected_edge_count"] for row in items) / denom,
            "avg_candidates": candidate_count / denom,
            "avg_filtered_candidates": filtered_count / denom,
            "candidate_retention": filtered_count / max(candidate_count, 1),
            "avg_inserted_units": inserted / denom,
            "budget_fill_rate": inserted / max(strategy.insert_budget * denom, 1),
            "insert_yield": inserted_gold / max(inserted, 1),
            "false_insert_rate": (inserted - inserted_gold) / max(inserted, 1),
        }
        for k in k_values:
            for metric in ("evidence_recall", "hit", "chain_recall", "context_units", "context_tokens"):
                key = f"{metric}_at_{k}"
                summary[key] = sum(row[key] for row in items) / denom
        output.append(summary)
    return output


def write_summary(path: Path, rows: list[dict[str, Any]], k_values: list[int]) -> None:
    fields = [
        "dataset",
        "strategy_id",
        "role",
        "score_floor",
        "protect_n",
        "insert_budget",
        "queries",
        "avg_mrr",
        "boundary_rate",
        "hyperedge_rate",
        "avg_selected_edges",
        "avg_candidates",
        "avg_filtered_candidates",
        "candidate_retention",
        "avg_inserted_units",
        "budget_fill_rate",
        "insert_yield",
        "false_insert_rate",
    ]
    for k in k_values:
        fields.extend(
            [
                f"evidence_recall_at_{k}",
                f"hit_at_{k}",
                f"chain_recall_at_{k}",
                f"context_units_at_{k}",
                f"context_tokens_at_{k}",
            ]
        )
    ordered = sorted(rows, key=lambda row: (row["dataset"] != "ALL", row["dataset"], row["strategy_id"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(ordered)


def build_row_maps(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    output: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        output[row["strategy_id"]][row["query_id"]] = row
    return output


def safe_ratio(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    return np.divide(numerator, denominator, out=np.zeros_like(numerator, dtype="float64"), where=denominator > 0)


def bootstrap_metric(
    dataset: str,
    strategy_a: str,
    strategy_b: str,
    metric: str,
    ids_by_dataset: dict[str, list[str]],
    rows_by_strategy: dict[str, dict[str, dict[str, Any]]],
    resamples: dict[str, np.ndarray],
) -> dict[str, Any]:
    strata = sorted(ids_by_dataset) if dataset == "ALL" else [dataset]
    if metric == "false_insert_rate":
        observed_num_a = observed_den_a = observed_num_b = observed_den_b = 0.0
        sampled_num_a = sampled_den_a = sampled_num_b = sampled_den_b = None
        for stratum in strata:
            ids = ids_by_dataset[stratum]
            a_non_gold = np.array([rows_by_strategy[strategy_a][qid]["inserted_non_gold_units"] for qid in ids], dtype="float64")
            a_inserted = np.array([rows_by_strategy[strategy_a][qid]["inserted_units"] for qid in ids], dtype="float64")
            b_non_gold = np.array([rows_by_strategy[strategy_b][qid]["inserted_non_gold_units"] for qid in ids], dtype="float64")
            b_inserted = np.array([rows_by_strategy[strategy_b][qid]["inserted_units"] for qid in ids], dtype="float64")
            indices = resamples[stratum]
            observed_num_a += float(a_non_gold.sum())
            observed_den_a += float(a_inserted.sum())
            observed_num_b += float(b_non_gold.sum())
            observed_den_b += float(b_inserted.sum())
            part_num_a = a_non_gold[indices].sum(axis=1)
            part_den_a = a_inserted[indices].sum(axis=1)
            part_num_b = b_non_gold[indices].sum(axis=1)
            part_den_b = b_inserted[indices].sum(axis=1)
            sampled_num_a = part_num_a if sampled_num_a is None else sampled_num_a + part_num_a
            sampled_den_a = part_den_a if sampled_den_a is None else sampled_den_a + part_den_a
            sampled_num_b = part_num_b if sampled_num_b is None else sampled_num_b + part_num_b
            sampled_den_b = part_den_b if sampled_den_b is None else sampled_den_b + part_den_b
        observed_a = observed_num_a / max(observed_den_a, 1.0)
        observed_b = observed_num_b / max(observed_den_b, 1.0)
        samples = safe_ratio(sampled_num_a, sampled_den_a) - safe_ratio(sampled_num_b, sampled_den_b)
        improved = same = regressed = ""
    else:
        row_key = "inserted_units" if metric == "avg_inserted_units" else metric
        observed_sum_a = observed_sum_b = 0.0
        sampled_delta_sum = None
        improved_count = same_count = regressed_count = 0
        total_queries = 0
        for stratum in strata:
            ids = ids_by_dataset[stratum]
            values_a = np.array([rows_by_strategy[strategy_a][qid][row_key] for qid in ids], dtype="float64")
            values_b = np.array([rows_by_strategy[strategy_b][qid][row_key] for qid in ids], dtype="float64")
            deltas = values_a - values_b
            indices = resamples[stratum]
            observed_sum_a += float(values_a.sum())
            observed_sum_b += float(values_b.sum())
            total_queries += len(ids)
            part = deltas[indices].sum(axis=1)
            sampled_delta_sum = part if sampled_delta_sum is None else sampled_delta_sum + part
            improved_count += int(np.sum(deltas > 1e-12))
            same_count += int(np.sum(np.abs(deltas) <= 1e-12))
            regressed_count += int(np.sum(deltas < -1e-12))
        observed_a = observed_sum_a / total_queries
        observed_b = observed_sum_b / total_queries
        samples = sampled_delta_sum / total_queries
        improved, same, regressed = improved_count, same_count, regressed_count
    observed_delta = observed_a - observed_b
    return {
        "observed_a": observed_a,
        "observed_b": observed_b,
        "observed_delta": observed_delta,
        "ci95_low": float(np.quantile(samples, 0.025)),
        "ci95_high": float(np.quantile(samples, 0.975)),
        "improved": improved,
        "same": same,
        "regressed": regressed,
    }


def bootstrap_comparisons(
    rows: list[dict[str, Any]],
    iterations: int,
    seed: int,
) -> list[dict[str, Any]]:
    rows_by_strategy = build_row_maps(rows)
    reference_rows = rows_by_strategy["dense_fixed"]
    ids_by_dataset: dict[str, list[str]] = defaultdict(list)
    for query_id, row in reference_rows.items():
        ids_by_dataset[row["dataset"]].append(query_id)
    for ids in ids_by_dataset.values():
        ids.sort()
    expected_ids = set(reference_rows)
    for strategy_id, strategy_rows in rows_by_strategy.items():
        if set(strategy_rows) != expected_ids:
            raise ValueError(f"Query alignment failed for {strategy_id}")
    rng = np.random.default_rng(seed)
    resamples = {
        dataset: rng.integers(0, len(ids), size=(iterations, len(ids)), dtype=np.int32)
        for dataset, ids in sorted(ids_by_dataset.items())
    }
    output: list[dict[str, Any]] = []
    for dataset in ("ALL", "hotpotqa", "musique"):
        query_count = sum(len(ids) for ids in ids_by_dataset.values()) if dataset == "ALL" else len(ids_by_dataset[dataset])
        for comparison in COMPARISONS:
            for metric in comparison.metrics:
                result = bootstrap_metric(
                    dataset,
                    comparison.strategy_a,
                    comparison.strategy_b,
                    metric,
                    ids_by_dataset,
                    rows_by_strategy,
                    resamples,
                )
                output.append(
                    {
                        "dataset": dataset,
                        "comparison_id": comparison.comparison_id,
                        "strategy_a": comparison.strategy_a,
                        "strategy_b": comparison.strategy_b,
                        "metric": metric,
                        "queries": query_count,
                        "iterations": iterations,
                        "seed": seed,
                        **result,
                    }
                )
    return output


def write_bootstrap(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "dataset",
        "comparison_id",
        "strategy_a",
        "strategy_b",
        "metric",
        "queries",
        "iterations",
        "seed",
        "observed_a",
        "observed_b",
        "observed_delta",
        "ci95_low",
        "ci95_high",
        "improved",
        "same",
        "regressed",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def find_summary(rows: list[dict[str, Any]], dataset: str, strategy_id: str) -> dict[str, Any]:
    return next(row for row in rows if row["dataset"] == dataset and row["strategy_id"] == strategy_id)


def find_bootstrap(rows: list[dict[str, Any]], comparison_id: str, metric: str) -> dict[str, Any]:
    return next(
        row
        for row in rows
        if row["dataset"] == "ALL" and row["comparison_id"] == comparison_id and row["metric"] == metric
    )


def gate_label(value: bool) -> str:
    return "SUPPORTED" if value else "NOT SUPPORTED"


def write_report(
    path: Path,
    summaries: list[dict[str, Any]],
    bootstrap_rows: list[dict[str, Any]],
    audit: dict[str, Any],
    q25_floor: float,
    q50_floor: float,
    args: argparse.Namespace,
    duration_seconds: float,
) -> None:
    primary = find_bootstrap(bootstrap_rows, "primary_q25_p5_i4_vs_fixed", "chain_recall_at_10")
    q25_noise = find_bootstrap(bootstrap_rows, "q25_filter_p5_i4", "false_insert_rate")
    q25_cr10 = find_bootstrap(bootstrap_rows, "q25_filter_p5_i4", "chain_recall_at_10")
    long_context = find_bootstrap(bootstrap_rows, "q25_p10_i4_vs_fixed", "chain_recall_at_20")
    q50_noise = find_bootstrap(bootstrap_rows, "q50_filter_p5_i2", "false_insert_rate")
    q50_cr10 = find_bootstrap(bootstrap_rows, "q50_filter_p5_i2", "chain_recall_at_10")
    primary_supported = primary["observed_delta"] > 0 and primary["ci95_low"] >= 0
    q25_noise_supported = q25_noise["observed_delta"] < 0 and q25_cr10["observed_delta"] >= 0
    long_supported = long_context["observed_delta"] > 0 and long_context["ci95_low"] >= 0
    summary_path = args.output_dir / "stage2f_frozen_threshold_summary.csv"
    bootstrap_path = args.output_dir / "stage2f_frozen_threshold_bootstrap.csv"
    lines = [
        "# Stage2F Frozen-Threshold Independent Validation Report",
        "",
        "## Material Passport",
        "",
        "- Origin Skill: academic-research-suite / experiment-agent",
        "- Origin Mode: run",
        f"- Origin Date: {date.today().isoformat()}",
        "- Verification Status: UNVERIFIED",
        "- Version Label: exp_result_v1",
        "- Protocol: `docs/STAGE2F_PROTOCOL.md` committed before test evaluation",
        "- Gold labels used for indexing, filtering, ranking, or threshold selection: No",
        "- Generator used: No",
        "",
        "## Experiment Result",
        "",
        "- ID: stage2f_frozen_threshold_unseen400",
        "- Type: analysis",
        "- Status: completed",
        f"- Command: `python scripts/stage2f_frozen_threshold_validation.py --units \"{args.units}\" --queries \"{args.queries}\" --calibration-queries \"{args.calibration_queries}\" --calibration-summary \"{args.calibration_summary}\" --embedding-cache \"{args.embedding_cache}\" --output-dir \"{args.output_dir}\" --report \"{path}\" --expand-boundary-only`",
        f"- Working Directory: `{Path.cwd()}`",
        f"- Duration: {duration_seconds:.2f} seconds",
        "- Exit Code: 0",
        "",
        "### Output Files",
        "",
        "| File | Size |",
        "|---|---:|",
        f"| `{summary_path}` | {summary_path.stat().st_size} bytes |",
        f"| `{bootstrap_path}` | {bootstrap_path.stat().st_size} bytes |",
        "",
        "### Anomalies Detected",
        "",
        "None during the completed run.",
        "",
        "## Independent-Test Audit",
        "",
        f"- Test queries: {audit['test_queries']} ({audit['dataset_counts']['hotpotqa']} HotpotQA, {audit['dataset_counts']['musique']} MuSiQue)",
        f"- Test retrieval units: {audit['test_units']}",
        f"- Test gold units: {audit['test_gold_units']}",
        f"- Calibration/test query-ID overlap: {audit['calibration_overlap']}",
        f"- Queries missing mapped gold: {audit['queries_missing_gold']}",
        f"- Frozen q25/q50 score floors: {q25_floor:.10f} / {q50_floor:.10f}",
        "",
        "## ALL Strategy Summary",
        "",
        "| Strategy | Protect | Insert | Retain | Avg inserted | ER@10 | CR@10 | ER@20 | CR@20 | False insert |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for strategy_id in (
        "dense_fixed",
        "unfiltered_p5_i2",
        "unfiltered_p5_i4",
        "score_q25_p5_i4",
        "unfiltered_p10_i4",
        "score_q25_p10_i4",
        "score_q50_p5_i2",
    ):
        row = find_summary(summaries, "ALL", strategy_id)
        lines.append(
            f"| {strategy_id} | {row['protect_n']} | {row['insert_budget']} | {row['candidate_retention']:.4f} | "
            f"{row['avg_inserted_units']:.4f} | {row['evidence_recall_at_10']:.4f} | "
            f"{row['chain_recall_at_10']:.4f} | {row['evidence_recall_at_20']:.4f} | "
            f"{row['chain_recall_at_20']:.4f} | {row['false_insert_rate']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Dataset Split",
            "",
            "| Dataset | Strategy | ER@10 | CR@10 | ER@20 | CR@20 | False insert |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for dataset in ("hotpotqa", "musique"):
        for strategy_id in ("dense_fixed", "score_q25_p5_i4", "score_q25_p10_i4", "score_q50_p5_i2"):
            row = find_summary(summaries, dataset, strategy_id)
            lines.append(
                f"| {dataset} | {strategy_id} | {row['evidence_recall_at_10']:.4f} | "
                f"{row['chain_recall_at_10']:.4f} | {row['evidence_recall_at_20']:.4f} | "
                f"{row['chain_recall_at_20']:.4f} | {row['false_insert_rate']:.4f} |"
            )
    lines.extend(
        [
            "",
            "## Pre-Registered Decision Gates",
            "",
            "| Gate | Delta | 95% CI | Decision |",
            "|---|---:|---:|---|",
            f"| Primary: q25 p5/i4 vs fixed CR@10 | {primary['observed_delta']:.4f} | [{primary['ci95_low']:.4f}, {primary['ci95_high']:.4f}] | {gate_label(primary_supported)} |",
            f"| Noise: q25 p5/i4 vs unfiltered false insert | {q25_noise['observed_delta']:.4f} | [{q25_noise['ci95_low']:.4f}, {q25_noise['ci95_high']:.4f}] | {gate_label(q25_noise_supported)}; CR@10 delta={q25_cr10['observed_delta']:.4f} |",
            f"| Long context: q25 p10/i4 vs fixed CR@20 | {long_context['observed_delta']:.4f} | [{long_context['ci95_low']:.4f}, {long_context['ci95_high']:.4f}] | {gate_label(long_supported)} |",
            f"| Exploratory q50 p5/i2 vs unfiltered false insert | {q50_noise['observed_delta']:.4f} | [{q50_noise['ci95_low']:.4f}, {q50_noise['ci95_high']:.4f}] | descriptive; CR@10 delta={q50_cr10['observed_delta']:.4f} |",
            "",
            "## Interpretation Boundary",
            "",
            "- The primary and secondary gate labels follow the rules frozen in the protocol; they are not selected after seeing test results.",
            "- Bootstrap intervals use 10,000 paired resamples with dataset-stratified resampling for ALL.",
            "- False insert is the aggregate share of inserted units that are not labelled gold, not a hallucination metric.",
            "- This is independent query-level validation within HotpotQA and MuSiQue using the same encoder. It does not establish cross-dataset, cross-encoder, or answer-generation generalization.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", required=True, type=Path)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--calibration-queries", required=True, type=Path)
    parser.add_argument("--calibration-summary", required=True, type=Path)
    parser.add_argument("--embedding-cache", required=True, type=Path)
    parser.add_argument("--output-dir", default=Path("results"), type=Path)
    parser.add_argument("--report", default=Path("reports/超粒球RAG_Stage2F_FrozenThreshold验证报告.md"), type=Path)
    parser.add_argument("--model-name", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--max-length", type=int, default=192)
    parser.add_argument("--k", nargs="+", type=int, default=[1, 3, 5, 10, 15, 20])
    parser.add_argument("--bootstrap-iterations", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260710)
    parser.add_argument("--expected-q25-floor", type=float, default=0.1957079917192459)
    parser.add_argument("--expected-q50-floor", type=float, default=0.31666630506515503)
    parser.add_argument("--min-size", type=int, default=2)
    parser.add_argument("--max-size", type=int, default=3)
    parser.add_argument("--radius-threshold", type=float, default=0.78)
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--boundary-width", type=float, default=0.2)
    parser.add_argument("--top-center-terms", type=int, default=8)
    parser.add_argument("--seed-balls", type=int, default=2)
    parser.add_argument("--top-facet-edges", type=int, default=2)
    parser.add_argument("--max-expanded-balls", type=int, default=2)
    parser.add_argument("--min-new-terms", type=int, default=1)
    parser.add_argument("--min-facet-score", type=float, default=0.10)
    parser.add_argument("--decision-boundary-margin", type=float, default=0.50)
    parser.add_argument("--decision-score-margin", type=float, default=0.10)
    parser.add_argument("--decision-min-ball-score", type=float, default=0.20)
    parser.add_argument("--expand-boundary-only", action="store_true")
    parser.add_argument("--max-candidate-ball-size", type=int, default=8)
    parser.add_argument("--min-ball-score", type=float, default=0.12)
    parser.add_argument("--min-seed-similarity", type=float, default=0.05)
    parser.add_argument("--max-units-per-new-term", type=float, default=6.0)
    parser.add_argument("--max-redundancy", type=float, default=0.90)
    parser.add_argument("--w-new", type=float, default=0.45)
    parser.add_argument("--w-total", type=float, default=0.20)
    parser.add_argument("--w-ball", type=float, default=0.20)
    parser.add_argument("--w-diversity", type=float, default=0.15)
    parser.add_argument("--w-redundancy", type=float, default=0.20)
    parser.add_argument("--w-size", type=float, default=0.05)
    parser.add_argument("--w-facet-unit-bonus", type=float, default=0.0)
    args = parser.parse_args()
    start_time = perf_counter()

    if not args.expand_boundary_only:
        raise ValueError("Stage2F protocol requires --expand-boundary-only")
    if args.bootstrap_iterations != 10000 or args.bootstrap_seed != 20260710:
        raise ValueError("Stage2F protocol requires 10000 bootstrap iterations and seed 20260710")
    q25_floor = load_calibration_floor(args.calibration_summary, "score_q25")
    q50_floor = load_calibration_floor(args.calibration_summary, "score_q50")
    if not math.isclose(q25_floor, args.expected_q25_floor, abs_tol=1e-12):
        raise ValueError(f"q25 floor differs from frozen protocol: {q25_floor}")
    if not math.isclose(q50_floor, args.expected_q50_floor, abs_tol=1e-12):
        raise ValueError(f"q50 floor differs from frozen protocol: {q50_floor}")

    units = load_jsonl(args.units)
    queries = load_jsonl(args.queries)
    calibration_queries = load_jsonl(args.calibration_queries)
    audit = preflight_audit(units, queries, calibration_queries)
    strategies = build_strategies(q25_floor, q50_floor)
    k_values = sorted(set(args.k))
    max_k = max(k_values)
    unit_embeddings, query_embeddings = load_or_build_embeddings(
        args.embedding_cache,
        units,
        queries,
        args.model_name,
        args.batch_size,
        args.max_length,
    )
    unit_embeddings = normalize_matrix(unit_embeddings.astype("float32"))
    query_embeddings = normalize_matrix(query_embeddings.astype("float32"))
    if unit_embeddings.shape[0] != len(units) or query_embeddings.shape[0] != len(queries):
        raise ValueError(
            f"Embedding/corpus mismatch: units={unit_embeddings.shape[0]}/{len(units)}, "
            f"queries={query_embeddings.shape[0]}/{len(queries)}"
        )

    indices_by_query: dict[str, list[int]] = defaultdict(list)
    for index, unit in enumerate(units):
        indices_by_query[unit["query_id"]].append(index)
    query_index = {query["query_id"]: index for index, query in enumerate(queries)}
    rows: list[dict[str, Any]] = []
    for query in queries:
        query_embedding = query_embeddings[query_index[query["query_id"]]]
        candidate_indices = indices_by_query[query["query_id"]]
        fixed_ranked = fixed_retrieve(query_embedding, candidate_indices, units, unit_embeddings, max_k)
        expanded, selected, info, expansion_stats = expansion_candidates(
            query,
            query_embedding,
            candidate_indices,
            units,
            unit_embeddings,
            args,
            "gated",
        )
        for strategy in strategies:
            if strategy.strategy_id == "dense_fixed":
                ranked = fixed_ranked
                insert_stats = {"inserted_units": 0, "inserted_gold_units": 0, "inserted_non_gold_units": 0}
                filtered = []
            else:
                filtered = apply_score_floor(expanded, strategy.score_floor)
                ranked, insert_stats = protected_rerank(
                    fixed_ranked,
                    filtered,
                    strategy.protect_n,
                    strategy.insert_budget,
                    max_k,
                )
            row = evaluate_query(query, ranked, k_values)
            row.pop("top_units", None)
            row.update(info if strategy.strategy_id != "dense_fixed" else {})
            row.update(expansion_stats if strategy.strategy_id != "dense_fixed" else {})
            row.update(insert_stats)
            row.update(
                {
                    "strategy_id": strategy.strategy_id,
                    "score_floor": strategy.score_floor,
                    "protect_n": strategy.protect_n,
                    "insert_budget": strategy.insert_budget,
                    "is_boundary": info["is_boundary"] if strategy.strategy_id != "dense_fixed" else 0.0,
                    "selected_edge_count": len(selected) if strategy.strategy_id != "dense_fixed" else 0,
                    "candidate_count": len(expanded) if strategy.strategy_id != "dense_fixed" else 0,
                    "filtered_candidate_count": len(filtered),
                }
            )
            rows.append(row)

    summaries = aggregate(rows, strategies, k_values)
    bootstrap_rows = bootstrap_comparisons(rows, args.bootstrap_iterations, args.bootstrap_seed)
    summary_path = args.output_dir / "stage2f_frozen_threshold_summary.csv"
    bootstrap_path = args.output_dir / "stage2f_frozen_threshold_bootstrap.csv"
    write_summary(summary_path, summaries, k_values)
    write_bootstrap(bootstrap_path, bootstrap_rows)
    write_report(
        args.report,
        summaries,
        bootstrap_rows,
        audit,
        q25_floor,
        q50_floor,
        args,
        perf_counter() - start_time,
    )
    print(
        json.dumps(
            {
                "audit": audit,
                "q25_floor": q25_floor,
                "q50_floor": q50_floor,
                "summary": str(summary_path),
                "bootstrap": str(bootstrap_path),
                "report": str(args.report),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
