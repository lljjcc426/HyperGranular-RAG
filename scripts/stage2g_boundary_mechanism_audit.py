"""Stage2G boundary-trigger mechanism audit on a third unseen query slice."""

from __future__ import annotations

import argparse
import copy
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
from stage2f_frozen_threshold_validation import load_calibration_floor, safe_ratio


@dataclass(frozen=True)
class Strategy:
    strategy_id: str
    boundary_policy: str
    protect_n: int
    insert_budget: int
    role: str


@dataclass(frozen=True)
class PolicyComparison:
    comparison_id: str
    strategy_a: str
    strategy_b: str
    metrics: tuple[str, ...]


STRATEGIES = (
    Strategy("dense_fixed", "none", 0, 0, "retrieval baseline"),
    Strategy("allquery_q25_p5_i4", "all-query", 5, 4, "Top-10 matched control"),
    Strategy("boundary_q25_p5_i4", "boundary-only", 5, 4, "Top-10 boundary policy"),
    Strategy("allquery_q25_p10_i4", "all-query", 10, 4, "Top-20 matched control"),
    Strategy("boundary_q25_p10_i4", "boundary-only", 10, 4, "primary boundary policy"),
)


POLICY_COMPARISONS = (
    PolicyComparison(
        "primary_boundary_p10_vs_all",
        "boundary_q25_p10_i4",
        "allquery_q25_p10_i4",
        (
            "false_insert_rate",
            "chain_recall_at_20",
            "evidence_recall_at_20",
            "avg_inserted_units",
            "trigger_rate",
            "completion_precision_at_20",
            "harm_rate_at_20",
        ),
    ),
    PolicyComparison(
        "secondary_boundary_p5_vs_all",
        "boundary_q25_p5_i4",
        "allquery_q25_p5_i4",
        (
            "false_insert_rate",
            "chain_recall_at_10",
            "evidence_recall_at_10",
            "avg_inserted_units",
            "trigger_rate",
            "completion_precision_at_10",
            "harm_rate_at_10",
        ),
    ),
    PolicyComparison(
        "allquery_p10_vs_fixed",
        "allquery_q25_p10_i4",
        "dense_fixed",
        ("chain_recall_at_20", "evidence_recall_at_20"),
    ),
    PolicyComparison(
        "boundary_p10_vs_fixed",
        "boundary_q25_p10_i4",
        "dense_fixed",
        ("chain_recall_at_20", "evidence_recall_at_20"),
    ),
)


RATIO_COMPONENTS = {
    "false_insert_rate": ("inserted_non_gold_units", "inserted_units"),
    "completion_precision_at_10": ("completion_success_at_10", "completion_opportunity_at_10"),
    "completion_precision_at_20": ("completion_success_at_20", "completion_opportunity_at_20"),
    "harm_rate_at_10": ("harm_event_at_10", "harm_opportunity_at_10"),
    "harm_rate_at_20": ("harm_event_at_20", "harm_opportunity_at_20"),
}


def preflight_audit(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    prior_query_sets: list[list[dict[str, Any]]],
) -> dict[str, Any]:
    query_ids = [row["query_id"] for row in queries]
    test_ids = set(query_ids)
    prior_ids = [{row["query_id"] for row in rows} for rows in prior_query_sets]
    overlaps = [len(test_ids & ids) for ids in prior_ids]
    datasets = Counter(row["dataset"] for row in queries)
    duplicates = len(query_ids) - len(test_ids)
    missing_gold = sum(1 for row in queries if not row.get("gold_unit_ids"))
    unit_query_ids = {row["query_id"] for row in units}
    if len(queries) != 400:
        raise ValueError(f"Expected 400 Stage2G queries, found {len(queries)}")
    if datasets != Counter({"hotpotqa": 200, "musique": 200}):
        raise ValueError(f"Unexpected dataset counts: {dict(datasets)}")
    if duplicates:
        raise ValueError(f"Duplicate Stage2G query ids: {duplicates}")
    if any(overlaps):
        raise ValueError(f"Prior-slice overlap counts: {overlaps}")
    if missing_gold:
        raise ValueError(f"Queries without mapped gold evidence: {missing_gold}")
    if unit_query_ids != test_ids:
        raise ValueError(
            f"Unit/query mismatch: missing={len(test_ids - unit_query_ids)}, foreign={len(unit_query_ids - test_ids)}"
        )
    return {
        "test_queries": len(queries),
        "test_units": len(units),
        "test_gold_units": sum(len(row["gold_unit_ids"]) for row in queries),
        "dataset_counts": dict(datasets),
        "duplicate_query_ids": duplicates,
        "prior_overlap_counts": overlaps,
        "queries_missing_gold": missing_gold,
    }


def add_mechanism_events(
    row: dict[str, Any],
    baseline: dict[str, Any],
    triggered: int,
    k_values: list[int],
) -> None:
    for k in k_values:
        metric = f"chain_recall_at_{k}"
        baseline_complete = baseline[metric] > 0.5
        strategy_complete = row[metric] > 0.5
        completion_opportunity = int(bool(triggered) and not baseline_complete)
        harm_opportunity = int(bool(triggered) and baseline_complete)
        row[f"completion_opportunity_at_{k}"] = completion_opportunity
        row[f"completion_success_at_{k}"] = int(bool(completion_opportunity) and strategy_complete)
        row[f"harm_opportunity_at_{k}"] = harm_opportunity
        row[f"harm_event_at_{k}"] = int(bool(harm_opportunity) and not strategy_complete)


def aggregate(rows: list[dict[str, Any]], k_values: list[int]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["dataset"], row["strategy_id"])].append(row)
        grouped[("ALL", row["strategy_id"])].append(row)
    strategy_by_id = {row.strategy_id: row for row in STRATEGIES}
    output: list[dict[str, Any]] = []
    for (dataset, strategy_id), items in grouped.items():
        strategy = strategy_by_id[strategy_id]
        denom = len(items)
        inserted = sum(row["inserted_units"] for row in items)
        inserted_gold = sum(row["inserted_gold_units"] for row in items)
        policy_candidates = sum(row["policy_candidate_count"] for row in items)
        filtered_candidates = sum(row["filtered_candidate_count"] for row in items)
        summary: dict[str, Any] = {
            "dataset": dataset,
            "strategy_id": strategy_id,
            "boundary_policy": strategy.boundary_policy,
            "role": strategy.role,
            "protect_n": strategy.protect_n,
            "insert_budget": strategy.insert_budget,
            "queries": denom,
            "boundary_rate": sum(row["is_boundary"] for row in items) / denom,
            "trigger_rate": sum(row["triggered"] for row in items) / denom,
            "hyperedge_rate": sum(1.0 if row["selected_edge_count"] > 0 else 0.0 for row in items) / denom,
            "avg_selected_edges": sum(row["selected_edge_count"] for row in items) / denom,
            "avg_raw_candidates": sum(row["raw_candidate_count"] for row in items) / denom,
            "avg_policy_candidates": policy_candidates / denom,
            "avg_filtered_candidates": filtered_candidates / denom,
            "candidate_retention": filtered_candidates / max(policy_candidates, 1),
            "avg_inserted_units": inserted / denom,
            "budget_fill_rate": inserted / max(strategy.insert_budget * denom, 1),
            "insert_yield": inserted_gold / max(inserted, 1),
            "false_insert_rate": (inserted - inserted_gold) / max(inserted, 1),
            "avg_mrr": sum(row["mrr"] for row in items) / denom,
        }
        for k in k_values:
            for metric in ("evidence_recall", "hit", "chain_recall", "context_units", "context_tokens"):
                key = f"{metric}_at_{k}"
                summary[key] = sum(row[key] for row in items) / denom
            completion_den = sum(row[f"completion_opportunity_at_{k}"] for row in items)
            harm_den = sum(row[f"harm_opportunity_at_{k}"] for row in items)
            summary[f"completion_opportunities_at_{k}"] = completion_den
            summary[f"completion_precision_at_{k}"] = (
                sum(row[f"completion_success_at_{k}"] for row in items) / max(completion_den, 1)
            )
            summary[f"harm_opportunities_at_{k}"] = harm_den
            summary[f"harm_rate_at_{k}"] = sum(row[f"harm_event_at_{k}"] for row in items) / max(harm_den, 1)
        output.append(summary)
    return output


def write_summary(path: Path, rows: list[dict[str, Any]], k_values: list[int]) -> None:
    fields = [
        "dataset",
        "strategy_id",
        "boundary_policy",
        "role",
        "protect_n",
        "insert_budget",
        "queries",
        "boundary_rate",
        "trigger_rate",
        "hyperedge_rate",
        "avg_selected_edges",
        "avg_raw_candidates",
        "avg_policy_candidates",
        "avg_filtered_candidates",
        "candidate_retention",
        "avg_inserted_units",
        "budget_fill_rate",
        "insert_yield",
        "false_insert_rate",
        "avg_mrr",
    ]
    for k in k_values:
        fields.extend(
            [
                f"evidence_recall_at_{k}",
                f"hit_at_{k}",
                f"chain_recall_at_{k}",
                f"context_units_at_{k}",
                f"context_tokens_at_{k}",
                f"completion_opportunities_at_{k}",
                f"completion_precision_at_{k}",
                f"harm_opportunities_at_{k}",
                f"harm_rate_at_{k}",
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


def bootstrap_policy_metric(
    dataset: str,
    strategy_a: str,
    strategy_b: str,
    metric: str,
    ids_by_dataset: dict[str, list[str]],
    rows_by_strategy: dict[str, dict[str, dict[str, Any]]],
    resamples: dict[str, np.ndarray],
) -> dict[str, Any]:
    strata = sorted(ids_by_dataset) if dataset == "ALL" else [dataset]
    if metric in RATIO_COMPONENTS:
        numerator_key, denominator_key = RATIO_COMPONENTS[metric]
        observed_num_a = observed_den_a = observed_num_b = observed_den_b = 0.0
        sampled_num_a = sampled_den_a = sampled_num_b = sampled_den_b = None
        for stratum in strata:
            ids = ids_by_dataset[stratum]
            indices = resamples[stratum]
            a_num = np.array([rows_by_strategy[strategy_a][qid][numerator_key] for qid in ids], dtype="float64")
            a_den = np.array([rows_by_strategy[strategy_a][qid][denominator_key] for qid in ids], dtype="float64")
            b_num = np.array([rows_by_strategy[strategy_b][qid][numerator_key] for qid in ids], dtype="float64")
            b_den = np.array([rows_by_strategy[strategy_b][qid][denominator_key] for qid in ids], dtype="float64")
            observed_num_a += float(a_num.sum())
            observed_den_a += float(a_den.sum())
            observed_num_b += float(b_num.sum())
            observed_den_b += float(b_den.sum())
            part_num_a = a_num[indices].sum(axis=1)
            part_den_a = a_den[indices].sum(axis=1)
            part_num_b = b_num[indices].sum(axis=1)
            part_den_b = b_den[indices].sum(axis=1)
            sampled_num_a = part_num_a if sampled_num_a is None else sampled_num_a + part_num_a
            sampled_den_a = part_den_a if sampled_den_a is None else sampled_den_a + part_den_a
            sampled_num_b = part_num_b if sampled_num_b is None else sampled_num_b + part_num_b
            sampled_den_b = part_den_b if sampled_den_b is None else sampled_den_b + part_den_b
        observed_a = observed_num_a / max(observed_den_a, 1.0)
        observed_b = observed_num_b / max(observed_den_b, 1.0)
        samples = safe_ratio(sampled_num_a, sampled_den_a) - safe_ratio(sampled_num_b, sampled_den_b)
        improved = same = regressed = ""
        denominator_a, denominator_b = observed_den_a, observed_den_b
    else:
        row_key = "inserted_units" if metric == "avg_inserted_units" else metric
        if metric == "trigger_rate":
            row_key = "triggered"
        observed_sum_a = observed_sum_b = 0.0
        sampled_delta_sum = None
        improved_count = same_count = regressed_count = 0
        total_queries = 0
        for stratum in strata:
            ids = ids_by_dataset[stratum]
            indices = resamples[stratum]
            values_a = np.array([rows_by_strategy[strategy_a][qid][row_key] for qid in ids], dtype="float64")
            values_b = np.array([rows_by_strategy[strategy_b][qid][row_key] for qid in ids], dtype="float64")
            deltas = values_a - values_b
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
        denominator_a = denominator_b = total_queries
    return {
        "observed_a": observed_a,
        "observed_b": observed_b,
        "observed_delta": observed_a - observed_b,
        "ci95_low": float(np.quantile(samples, 0.025)),
        "ci95_high": float(np.quantile(samples, 0.975)),
        "denominator_a": denominator_a,
        "denominator_b": denominator_b,
        "improved": improved,
        "same": same,
        "regressed": regressed,
    }


def bootstrap_predictive_metric(
    dataset: str,
    metric: str,
    ids_by_dataset: dict[str, list[str]],
    rows: dict[str, dict[str, Any]],
    resamples: dict[str, np.ndarray],
) -> dict[str, Any]:
    numerator_key, denominator_key = RATIO_COMPONENTS[metric]
    strata = sorted(ids_by_dataset) if dataset == "ALL" else [dataset]
    observed_num_boundary = observed_den_boundary = 0.0
    observed_num_nonboundary = observed_den_nonboundary = 0.0
    sampled_num_boundary = sampled_den_boundary = sampled_num_nonboundary = sampled_den_nonboundary = None
    for stratum in strata:
        ids = ids_by_dataset[stratum]
        indices = resamples[stratum]
        boundary = np.array([rows[qid]["is_boundary"] for qid in ids], dtype="float64")
        nonboundary = 1.0 - boundary
        numerator = np.array([rows[qid][numerator_key] for qid in ids], dtype="float64")
        denominator = np.array([rows[qid][denominator_key] for qid in ids], dtype="float64")
        boundary_num = numerator * boundary
        boundary_den = denominator * boundary
        nonboundary_num = numerator * nonboundary
        nonboundary_den = denominator * nonboundary
        observed_num_boundary += float(boundary_num.sum())
        observed_den_boundary += float(boundary_den.sum())
        observed_num_nonboundary += float(nonboundary_num.sum())
        observed_den_nonboundary += float(nonboundary_den.sum())
        part_num_boundary = boundary_num[indices].sum(axis=1)
        part_den_boundary = boundary_den[indices].sum(axis=1)
        part_num_nonboundary = nonboundary_num[indices].sum(axis=1)
        part_den_nonboundary = nonboundary_den[indices].sum(axis=1)
        sampled_num_boundary = (
            part_num_boundary if sampled_num_boundary is None else sampled_num_boundary + part_num_boundary
        )
        sampled_den_boundary = (
            part_den_boundary if sampled_den_boundary is None else sampled_den_boundary + part_den_boundary
        )
        sampled_num_nonboundary = (
            part_num_nonboundary if sampled_num_nonboundary is None else sampled_num_nonboundary + part_num_nonboundary
        )
        sampled_den_nonboundary = (
            part_den_nonboundary if sampled_den_nonboundary is None else sampled_den_nonboundary + part_den_nonboundary
        )
    observed_boundary = observed_num_boundary / max(observed_den_boundary, 1.0)
    observed_nonboundary = observed_num_nonboundary / max(observed_den_nonboundary, 1.0)
    samples = safe_ratio(sampled_num_boundary, sampled_den_boundary) - safe_ratio(
        sampled_num_nonboundary, sampled_den_nonboundary
    )
    return {
        "observed_a": observed_boundary,
        "observed_b": observed_nonboundary,
        "observed_delta": observed_boundary - observed_nonboundary,
        "ci95_low": float(np.quantile(samples, 0.025)),
        "ci95_high": float(np.quantile(samples, 0.975)),
        "denominator_a": observed_den_boundary,
        "denominator_b": observed_den_nonboundary,
        "improved": "",
        "same": "",
        "regressed": "",
    }


def bootstrap_audit(rows: list[dict[str, Any]], iterations: int, seed: int) -> list[dict[str, Any]]:
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
        for comparison in POLICY_COMPARISONS:
            for metric in comparison.metrics:
                result = bootstrap_policy_metric(
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
        for metric in ("completion_precision_at_20", "harm_rate_at_20"):
            result = bootstrap_predictive_metric(
                dataset,
                metric,
                ids_by_dataset,
                rows_by_strategy["allquery_q25_p10_i4"],
                resamples,
            )
            output.append(
                {
                    "dataset": dataset,
                    "comparison_id": "predictive_boundary_vs_nonboundary_p10",
                    "strategy_a": "boundary queries under allquery_q25_p10_i4",
                    "strategy_b": "non-boundary queries under allquery_q25_p10_i4",
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
        "denominator_a",
        "denominator_b",
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


def decision_label(value: bool) -> str:
    return "SUPPORTED" if value else "NOT SUPPORTED"


def write_report(
    path: Path,
    summaries: list[dict[str, Any]],
    bootstrap_rows: list[dict[str, Any]],
    audit: dict[str, Any],
    q25_floor: float,
    args: argparse.Namespace,
    duration_seconds: float,
) -> None:
    primary_false = find_bootstrap(bootstrap_rows, "primary_boundary_p10_vs_all", "false_insert_rate")
    primary_cr = find_bootstrap(bootstrap_rows, "primary_boundary_p10_vs_all", "chain_recall_at_20")
    secondary_false = find_bootstrap(bootstrap_rows, "secondary_boundary_p5_vs_all", "false_insert_rate")
    secondary_cr = find_bootstrap(bootstrap_rows, "secondary_boundary_p5_vs_all", "chain_recall_at_10")
    predictive = find_bootstrap(
        bootstrap_rows,
        "predictive_boundary_vs_nonboundary_p10",
        "completion_precision_at_20",
    )
    primary_supported = (
        primary_false["observed_delta"] < 0
        and primary_false["ci95_high"] < 0
        and primary_cr["ci95_low"] >= -0.01
    )
    secondary_supported = (
        secondary_false["observed_delta"] < 0
        and secondary_false["ci95_high"] < 0
        and secondary_cr["ci95_low"] >= -0.01
    )
    predictive_supported = predictive["observed_delta"] > 0 and predictive["ci95_low"] >= 0
    summary_path = args.output_dir / "stage2g_boundary_mechanism_summary.csv"
    bootstrap_path = args.output_dir / "stage2g_boundary_mechanism_bootstrap.csv"
    lines = [
        "# Stage2G Boundary-Decision Mechanism Audit Report",
        "",
        "## Material Passport",
        "",
        "- Origin Skill: academic-research-suite / experiment-agent",
        "- Origin Mode: run",
        f"- Origin Date: {date.today().isoformat()}",
        "- Verification Status: UNVERIFIED",
        "- Version Label: exp_result_v1",
        "- Protocol: `docs/STAGE2G_PROTOCOL.md` committed before Stage2G test extraction and evaluation",
        "- Gold labels used for indexing, boundary classification, filtering, ranking, or threshold selection: No",
        "- Generator used: No",
        "",
        "## Experiment Result",
        "",
        "- ID: stage2g_boundary_mechanism_unseen400",
        "- Type: analysis",
        "- Status: completed",
        f"- Command: `python scripts/stage2g_boundary_mechanism_audit.py --units \"{args.units}\" --queries \"{args.queries}\" --prior-queries ... --calibration-summary \"{args.calibration_summary}\" --embedding-cache \"{args.embedding_cache}\" --output-dir \"{args.output_dir}\" --report \"{path}\"`",
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
        f"- Prior-slice query-ID overlaps: {audit['prior_overlap_counts']}",
        f"- Queries missing mapped gold: {audit['queries_missing_gold']}",
        f"- Frozen q25 score floor: {q25_floor:.10f}",
        "",
        "## ALL Strategy Summary",
        "",
        "| Strategy | Boundary policy | Trigger | Avg inserted | CR@10 | CR@20 | False insert | Complete P@20 | Harm@20 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for strategy in STRATEGIES:
        row = find_summary(summaries, "ALL", strategy.strategy_id)
        lines.append(
            f"| {strategy.strategy_id} | {strategy.boundary_policy} | {row['trigger_rate']:.4f} | "
            f"{row['avg_inserted_units']:.4f} | {row['chain_recall_at_10']:.4f} | "
            f"{row['chain_recall_at_20']:.4f} | {row['false_insert_rate']:.4f} | "
            f"{row['completion_precision_at_20']:.4f} | {row['harm_rate_at_20']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Dataset Split",
            "",
            "| Dataset | Strategy | Boundary rate | Trigger | CR@10 | CR@20 | False insert |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for dataset in ("hotpotqa", "musique"):
        for strategy_id in (
            "dense_fixed",
            "allquery_q25_p5_i4",
            "boundary_q25_p5_i4",
            "allquery_q25_p10_i4",
            "boundary_q25_p10_i4",
        ):
            row = find_summary(summaries, dataset, strategy_id)
            lines.append(
                f"| {dataset} | {strategy_id} | {row['boundary_rate']:.4f} | {row['trigger_rate']:.4f} | "
                f"{row['chain_recall_at_10']:.4f} | {row['chain_recall_at_20']:.4f} | "
                f"{row['false_insert_rate']:.4f} |"
            )
    lines.extend(
        [
            "",
            "## Pre-Registered Decision Gates",
            "",
            "| Gate | False-insert delta [95% CI] | Recall delta [95% CI] | Decision |",
            "|---|---:|---:|---|",
            f"| Primary p10/i4 boundary vs all | {primary_false['observed_delta']:.4f} [{primary_false['ci95_low']:.4f}, {primary_false['ci95_high']:.4f}] | CR@20 {primary_cr['observed_delta']:.4f} [{primary_cr['ci95_low']:.4f}, {primary_cr['ci95_high']:.4f}] | {decision_label(primary_supported)} |",
            f"| Secondary p5/i4 boundary vs all | {secondary_false['observed_delta']:.4f} [{secondary_false['ci95_low']:.4f}, {secondary_false['ci95_high']:.4f}] | CR@10 {secondary_cr['observed_delta']:.4f} [{secondary_cr['ci95_low']:.4f}, {secondary_cr['ci95_high']:.4f}] | {decision_label(secondary_supported)} |",
            "",
            "## Predictive Mechanism Gate",
            "",
            f"- Boundary completion precision@20: {predictive['observed_a']:.4f} ({int(predictive['denominator_a'])} opportunities).",
            f"- Non-boundary completion precision@20: {predictive['observed_b']:.4f} ({int(predictive['denominator_b'])} opportunities).",
            f"- Boundary-minus-non-boundary delta: {predictive['observed_delta']:.4f}, 95% CI [{predictive['ci95_low']:.4f}, {predictive['ci95_high']:.4f}].",
            f"- Decision: {decision_label(predictive_supported)}.",
            "",
            "## Interpretation Boundary",
            "",
            "- Policy comparisons differ only in whether non-boundary queries may expand; score floor, candidate construction, ranking, and budgets are identical.",
            "- Completion precision is conditional on a triggered query whose dense-fixed chain is incomplete at the target K.",
            "- False insert is not a hallucination metric, and the audit does not evaluate answer generation.",
            "- A failed predictive gate means the current boundary rule is not validated as a benefit predictor; it does not prove that all uncertainty signals are useless.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", required=True, type=Path)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--prior-queries", required=True, nargs="+", type=Path)
    parser.add_argument("--calibration-summary", required=True, type=Path)
    parser.add_argument("--embedding-cache", required=True, type=Path)
    parser.add_argument("--output-dir", default=Path("results"), type=Path)
    parser.add_argument("--report", default=Path("reports/超粒球RAG_Stage2G_BoundaryMechanism报告.md"), type=Path)
    parser.add_argument("--model-name", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--max-length", type=int, default=192)
    parser.add_argument("--k", nargs="+", type=int, default=[1, 3, 5, 10, 15, 20])
    parser.add_argument("--bootstrap-iterations", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260711)
    parser.add_argument("--expected-q25-floor", type=float, default=0.1957079917192459)
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

    if args.bootstrap_iterations != 10000 or args.bootstrap_seed != 20260711:
        raise ValueError("Stage2G protocol requires 10000 bootstrap iterations and seed 20260711")
    q25_floor = load_calibration_floor(args.calibration_summary, "score_q25")
    if not math.isclose(q25_floor, args.expected_q25_floor, abs_tol=1e-12):
        raise ValueError(f"q25 floor differs from frozen protocol: {q25_floor}")

    units = load_jsonl(args.units)
    queries = load_jsonl(args.queries)
    prior_query_sets = [load_jsonl(path) for path in args.prior_queries]
    audit = preflight_audit(units, queries, prior_query_sets)
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
    all_query_args = copy.copy(args)
    all_query_args.expand_boundary_only = False
    rows: list[dict[str, Any]] = []
    for query in queries:
        query_embedding = query_embeddings[query_index[query["query_id"]]]
        candidate_indices = indices_by_query[query["query_id"]]
        fixed_ranked = fixed_retrieve(query_embedding, candidate_indices, units, unit_embeddings, max_k)
        baseline = evaluate_query(query, fixed_ranked, k_values)
        baseline.pop("top_units", None)
        expanded, selected, info, expansion_stats = expansion_candidates(
            query,
            query_embedding,
            candidate_indices,
            units,
            unit_embeddings,
            all_query_args,
            "gated",
        )
        filtered_all = [row for row in expanded if row["score"] >= q25_floor]
        for strategy in STRATEGIES:
            if strategy.strategy_id == "dense_fixed":
                ranked = fixed_ranked
                insert_stats = {"inserted_units": 0, "inserted_gold_units": 0, "inserted_non_gold_units": 0}
                policy_candidates: list[dict[str, Any]] = []
                filtered: list[dict[str, Any]] = []
                selected_edge_count = 0
            else:
                policy_active = strategy.boundary_policy == "all-query" or info["is_boundary"] > 0.5
                policy_candidates = expanded if policy_active else []
                filtered = filtered_all if policy_active else []
                selected_edge_count = len(selected) if policy_active else 0
                ranked, insert_stats = protected_rerank(
                    fixed_ranked,
                    filtered,
                    strategy.protect_n,
                    strategy.insert_budget,
                    max_k,
                )
            row = evaluate_query(query, ranked, k_values)
            row.pop("top_units", None)
            row.update(expansion_stats if strategy.strategy_id != "dense_fixed" else {})
            row.update(insert_stats)
            triggered = int(insert_stats["inserted_units"] > 0)
            add_mechanism_events(row, baseline, triggered, k_values)
            row.update(
                {
                    "strategy_id": strategy.strategy_id,
                    "boundary_policy": strategy.boundary_policy,
                    "protect_n": strategy.protect_n,
                    "insert_budget": strategy.insert_budget,
                    "is_boundary": info["is_boundary"],
                    "triggered": triggered,
                    "selected_edge_count": selected_edge_count,
                    "raw_candidate_count": len(expanded) if strategy.strategy_id != "dense_fixed" else 0,
                    "policy_candidate_count": len(policy_candidates),
                    "filtered_candidate_count": len(filtered),
                }
            )
            rows.append(row)

    summaries = aggregate(rows, k_values)
    bootstrap_rows = bootstrap_audit(rows, args.bootstrap_iterations, args.bootstrap_seed)
    summary_path = args.output_dir / "stage2g_boundary_mechanism_summary.csv"
    bootstrap_path = args.output_dir / "stage2g_boundary_mechanism_bootstrap.csv"
    write_summary(summary_path, summaries, k_values)
    write_bootstrap(bootstrap_path, bootstrap_rows)
    write_report(
        args.report,
        summaries,
        bootstrap_rows,
        audit,
        q25_floor,
        args,
        perf_counter() - start_time,
    )
    print(
        json.dumps(
            {
                "audit": audit,
                "q25_floor": q25_floor,
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
