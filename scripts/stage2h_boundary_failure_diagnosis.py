"""Stage2H exploratory diagnosis of the failed OR-composed boundary rule."""

from __future__ import annotations

import argparse
import copy
import csv
import json
import math
from collections import Counter, defaultdict
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


COMPONENTS = (
    ("radius", "criterion_radius"),
    ("score_margin", "criterion_score_margin"),
    ("low_top_score", "criterion_low_top_score"),
    ("or_gate", "criterion_or_gate"),
)


CONTINUOUS_PREDICTORS = (
    ("neg_boundary_margin", "uncertainty_boundary_margin"),
    ("neg_ball_score_margin", "uncertainty_score_margin"),
    ("neg_top_ball_score", "uncertainty_top_score"),
)


RATIO_OUTCOMES = {
    "completion_precision_at_20": ("completion_success_at_20", "completion_opportunity_at_20"),
    "harm_rate_at_20": ("harm_event_at_20", "harm_opportunity_at_20"),
    "false_insert_rate": ("inserted_non_gold_units", "inserted_units"),
}


def binary_auroc(labels: np.ndarray, scores: np.ndarray) -> float | None:
    positives = int(labels.sum())
    negatives = len(labels) - positives
    if positives == 0 or negatives == 0:
        return None
    order = np.argsort(scores, kind="mergesort")
    sorted_scores = scores[order]
    ranks = np.empty(len(scores), dtype="float64")
    start = 0
    while start < len(scores):
        end = start + 1
        while end < len(scores) and sorted_scores[end] == sorted_scores[start]:
            end += 1
        ranks[order[start:end]] = (start + 1 + end) / 2.0
        start = end
    positive_rank_sum = float(ranks[labels == 1].sum())
    return (positive_rank_sum - positives * (positives + 1) / 2.0) / (positives * negatives)


def binary_average_precision(labels: np.ndarray, scores: np.ndarray) -> float | None:
    positives = int(labels.sum())
    if positives == 0:
        return None
    order = np.argsort(-scores, kind="mergesort")
    sorted_scores = scores[order]
    sorted_labels = labels[order]
    true_positives = false_positives = 0
    previous_recall = 0.0
    average_precision = 0.0
    start = 0
    while start < len(scores):
        end = start + 1
        while end < len(scores) and sorted_scores[end] == sorted_scores[start]:
            end += 1
        group = sorted_labels[start:end]
        true_positives += int(group.sum())
        false_positives += len(group) - int(group.sum())
        recall = true_positives / positives
        precision = true_positives / max(true_positives + false_positives, 1)
        average_precision += (recall - previous_recall) * precision
        previous_recall = recall
        start = end
    return average_precision


QUERY_FIELDS = [
    "slice_id",
    "dataset",
    "query_id",
    "num_gold",
    "num_candidates",
    "top_ball_score",
    "ball_score_margin",
    "top_ball_radius",
    "query_to_top_ball_distance",
    "boundary_margin",
    "uncertainty_boundary_margin",
    "uncertainty_score_margin",
    "uncertainty_top_score",
    "criterion_radius",
    "criterion_score_margin",
    "criterion_low_top_score",
    "criterion_or_gate",
    "component_mask",
    "selected_edge_count",
    "raw_candidate_count",
    "filtered_candidate_count",
    "triggered",
    "inserted_units",
    "inserted_gold_units",
    "inserted_non_gold_units",
    "baseline_evidence_recall_at_20",
    "strategy_evidence_recall_at_20",
    "delta_evidence_recall_at_20",
    "baseline_chain_recall_at_20",
    "strategy_chain_recall_at_20",
    "delta_chain_recall_at_20",
    "completion_opportunity_at_20",
    "completion_success_at_20",
    "harm_opportunity_at_20",
    "harm_event_at_20",
]


def component_mask(radius: int, score_margin: int, low_top_score: int) -> str:
    labels = []
    if radius:
        labels.append("R")
    if score_margin:
        labels.append("S")
    if low_top_score:
        labels.append("L")
    return "".join(labels) if labels else "none"


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def validate_corpora(corpora: list[tuple[str, list[dict[str, Any]], list[dict[str, Any]]]]) -> dict[str, Any]:
    seen: set[str] = set()
    audit: dict[str, Any] = {"slices": {}, "pairwise_overlap": 0}
    for slice_id, units, queries in corpora:
        ids = [row["query_id"] for row in queries]
        id_set = set(ids)
        datasets = Counter(row["dataset"] for row in queries)
        unit_query_ids = {row["query_id"] for row in units}
        missing_gold = sum(1 for row in queries if not row.get("gold_unit_ids"))
        overlap = seen & id_set
        if len(queries) != 400:
            raise ValueError(f"{slice_id}: expected 400 queries, found {len(queries)}")
        if datasets != Counter({"hotpotqa": 200, "musique": 200}):
            raise ValueError(f"{slice_id}: unexpected dataset counts {dict(datasets)}")
        if len(ids) != len(id_set):
            raise ValueError(f"{slice_id}: duplicate query ids")
        if overlap:
            raise ValueError(f"{slice_id}: overlap with earlier slices: {sorted(overlap)[:5]}")
        if missing_gold:
            raise ValueError(f"{slice_id}: queries missing mapped gold: {missing_gold}")
        if unit_query_ids != id_set:
            raise ValueError(f"{slice_id}: unit/query id mismatch")
        audit["slices"][slice_id] = {
            "queries": len(queries),
            "units": len(units),
            "gold_units": sum(len(row["gold_unit_ids"]) for row in queries),
            "datasets": dict(datasets),
            "missing_gold": missing_gold,
            "overlap_with_previous": len(overlap),
        }
        seen.update(id_set)
    audit["total_queries"] = len(seen)
    audit["slice_count"] = len(corpora)
    return audit


def build_query_rows(
    corpus_specs: list[tuple[str, Path, Path, Path]],
    q25_floor: float,
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    loaded: list[tuple[str, list[dict[str, Any]], list[dict[str, Any]]]] = []
    for slice_id, units_path, queries_path, _ in corpus_specs:
        loaded.append((slice_id, load_jsonl(units_path), load_jsonl(queries_path)))
    audit = validate_corpora(loaded)
    rows: list[dict[str, Any]] = []
    all_query_args = copy.copy(args)
    all_query_args.expand_boundary_only = False
    for (slice_id, units, queries), (_, _, _, cache_path) in zip(loaded, corpus_specs):
        unit_embeddings, query_embeddings = load_or_build_embeddings(
            cache_path,
            units,
            queries,
            args.model_name,
            args.batch_size,
            args.max_length,
        )
        unit_embeddings = normalize_matrix(unit_embeddings.astype("float32"))
        query_embeddings = normalize_matrix(query_embeddings.astype("float32"))
        if unit_embeddings.shape[0] != len(units) or query_embeddings.shape[0] != len(queries):
            raise ValueError(f"{slice_id}: embedding/corpus dimension mismatch")
        indices_by_query: dict[str, list[int]] = defaultdict(list)
        for index, unit in enumerate(units):
            indices_by_query[unit["query_id"]].append(index)
        query_index = {query["query_id"]: index for index, query in enumerate(queries)}
        for query in queries:
            query_embedding = query_embeddings[query_index[query["query_id"]]]
            candidate_indices = indices_by_query[query["query_id"]]
            fixed_ranked = fixed_retrieve(query_embedding, candidate_indices, units, unit_embeddings, 20)
            baseline = evaluate_query(query, fixed_ranked, [20])
            expanded, selected, info, _ = expansion_candidates(
                query,
                query_embedding,
                candidate_indices,
                units,
                unit_embeddings,
                all_query_args,
                "gated",
            )
            filtered = [row for row in expanded if row["score"] >= q25_floor]
            ranked, insert_stats = protected_rerank(fixed_ranked, filtered, 10, 4, 20)
            strategy = evaluate_query(query, ranked, [20])
            radius = int(info["boundary_margin"] <= args.decision_boundary_margin)
            score_margin = int(info["ball_score_margin"] <= args.decision_score_margin)
            low_top_score = int(info["top_ball_score"] < args.decision_min_ball_score)
            gate = int(bool(radius or score_margin or low_top_score))
            triggered = int(insert_stats["inserted_units"] > 0)
            baseline_complete = baseline["chain_recall_at_20"] > 0.5
            strategy_complete = strategy["chain_recall_at_20"] > 0.5
            completion_opportunity = int(bool(triggered) and not baseline_complete)
            harm_opportunity = int(bool(triggered) and baseline_complete)
            rows.append(
                {
                    "slice_id": slice_id,
                    "dataset": query["dataset"],
                    "query_id": query["query_id"],
                    "num_gold": len(query["gold_unit_ids"]),
                    "num_candidates": len(candidate_indices),
                    "top_ball_score": info["top_ball_score"],
                    "ball_score_margin": info["ball_score_margin"],
                    "top_ball_radius": info["top_ball_radius"],
                    "query_to_top_ball_distance": info["query_to_top_ball_distance"],
                    "boundary_margin": info["boundary_margin"],
                    "uncertainty_boundary_margin": -info["boundary_margin"],
                    "uncertainty_score_margin": -info["ball_score_margin"],
                    "uncertainty_top_score": -info["top_ball_score"],
                    "criterion_radius": radius,
                    "criterion_score_margin": score_margin,
                    "criterion_low_top_score": low_top_score,
                    "criterion_or_gate": gate,
                    "component_mask": component_mask(radius, score_margin, low_top_score),
                    "selected_edge_count": len(selected),
                    "raw_candidate_count": len(expanded),
                    "filtered_candidate_count": len(filtered),
                    "triggered": triggered,
                    **insert_stats,
                    "baseline_evidence_recall_at_20": baseline["evidence_recall_at_20"],
                    "strategy_evidence_recall_at_20": strategy["evidence_recall_at_20"],
                    "delta_evidence_recall_at_20": strategy["evidence_recall_at_20"] - baseline["evidence_recall_at_20"],
                    "baseline_chain_recall_at_20": baseline["chain_recall_at_20"],
                    "strategy_chain_recall_at_20": strategy["chain_recall_at_20"],
                    "delta_chain_recall_at_20": strategy["chain_recall_at_20"] - baseline["chain_recall_at_20"],
                    "completion_opportunity_at_20": completion_opportunity,
                    "completion_success_at_20": int(bool(completion_opportunity) and strategy_complete),
                    "harm_opportunity_at_20": harm_opportunity,
                    "harm_event_at_20": int(bool(harm_opportunity) and not strategy_complete),
                }
            )
    return rows, audit


def scopes(rows: list[dict[str, Any]]) -> list[tuple[str, str, list[dict[str, Any]]]]:
    output = [("ALL", "ALL", rows)]
    for dataset in ("hotpotqa", "musique"):
        output.append(("dataset", dataset, [row for row in rows if row["dataset"] == dataset]))
    for slice_id in sorted({row["slice_id"] for row in rows}):
        output.append(("slice", slice_id, [row for row in rows if row["slice_id"] == slice_id]))
    return output


def summarize_group(
    scope_type: str,
    scope_value: str,
    group_type: str,
    group_name: str,
    group_value: str,
    items: list[dict[str, Any]],
    scope_count: int,
) -> dict[str, Any]:
    n = len(items)
    inserted = sum(row["inserted_units"] for row in items)
    inserted_gold = sum(row["inserted_gold_units"] for row in items)
    completion_den = sum(row["completion_opportunity_at_20"] for row in items)
    harm_den = sum(row["harm_opportunity_at_20"] for row in items)
    return {
        "scope_type": scope_type,
        "scope_value": scope_value,
        "group_type": group_type,
        "group_name": group_name,
        "group_value": group_value,
        "queries": n,
        "prevalence": n / max(scope_count, 1),
        "trigger_rate": sum(row["triggered"] for row in items) / max(n, 1),
        "avg_inserted_units": inserted / max(n, 1),
        "insert_yield": inserted_gold / max(inserted, 1),
        "false_insert_rate": (inserted - inserted_gold) / max(inserted, 1),
        "baseline_cr20": sum(row["baseline_chain_recall_at_20"] for row in items) / max(n, 1),
        "strategy_cr20": sum(row["strategy_chain_recall_at_20"] for row in items) / max(n, 1),
        "delta_cr20": sum(row["delta_chain_recall_at_20"] for row in items) / max(n, 1),
        "improved_queries": sum(row["delta_chain_recall_at_20"] > 0 for row in items),
        "same_queries": sum(abs(row["delta_chain_recall_at_20"]) <= 1e-12 for row in items),
        "regressed_queries": sum(row["delta_chain_recall_at_20"] < 0 for row in items),
        "completion_opportunities": completion_den,
        "completion_precision": sum(row["completion_success_at_20"] for row in items) / max(completion_den, 1),
        "harm_opportunities": harm_den,
        "harm_rate": sum(row["harm_event_at_20"] for row in items) / max(harm_den, 1),
        "avg_boundary_margin": sum(row["boundary_margin"] for row in items) / max(n, 1),
        "avg_ball_score_margin": sum(row["ball_score_margin"] for row in items) / max(n, 1),
        "avg_top_ball_score": sum(row["top_ball_score"] for row in items) / max(n, 1),
    }


def component_summaries(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    masks = sorted({row["component_mask"] for row in rows})
    for scope_type, scope_value, scope_rows in scopes(rows):
        for component_name, key in COMPONENTS:
            for value in (1, 0):
                items = [row for row in scope_rows if row[key] == value]
                output.append(
                    summarize_group(
                        scope_type,
                        scope_value,
                        "component",
                        component_name,
                        str(value),
                        items,
                        len(scope_rows),
                    )
                )
        for mask in masks:
            items = [row for row in scope_rows if row["component_mask"] == mask]
            if items:
                output.append(
                    summarize_group(
                        scope_type,
                        scope_value,
                        "overlap_mask",
                        "component_mask",
                        mask,
                        items,
                        len(scope_rows),
                    )
                )
    return output


def stratified_resamples(
    rows: list[dict[str, Any]], iterations: int, seed: int
) -> tuple[dict[tuple[str, str], list[dict[str, Any]]], dict[tuple[str, str], np.ndarray]]:
    by_stratum: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_stratum[(row["slice_id"], row["dataset"])].append(row)
    for items in by_stratum.values():
        items.sort(key=lambda row: row["query_id"])
    rng = np.random.default_rng(seed)
    resamples = {
        key: rng.integers(0, len(items), size=(iterations, len(items)), dtype=np.int32)
        for key, items in sorted(by_stratum.items())
    }
    return by_stratum, resamples


def scope_strata(scope_type: str, scope_value: str, keys: list[tuple[str, str]]) -> list[tuple[str, str]]:
    if scope_type == "ALL":
        return keys
    if scope_type == "dataset":
        return [key for key in keys if key[1] == scope_value]
    return [key for key in keys if key[0] == scope_value]


def bootstrap_component_contrast(
    component_key: str,
    outcome: str,
    selected_strata: list[tuple[str, str]],
    by_stratum: dict[tuple[str, str], list[dict[str, Any]]],
    resamples: dict[tuple[str, str], np.ndarray],
) -> dict[str, Any]:
    numerator_key, denominator_key = RATIO_OUTCOMES[outcome]
    observed_num_true = observed_den_true = observed_num_false = observed_den_false = 0.0
    sampled_num_true = sampled_den_true = sampled_num_false = sampled_den_false = None
    for key in selected_strata:
        items = by_stratum[key]
        indices = resamples[key]
        group = np.array([row[component_key] for row in items], dtype="float64")
        inverse = 1.0 - group
        numerator = np.array([row[numerator_key] for row in items], dtype="float64")
        denominator = np.array([row[denominator_key] for row in items], dtype="float64")
        true_num = numerator * group
        true_den = denominator * group
        false_num = numerator * inverse
        false_den = denominator * inverse
        observed_num_true += float(true_num.sum())
        observed_den_true += float(true_den.sum())
        observed_num_false += float(false_num.sum())
        observed_den_false += float(false_den.sum())
        part_num_true = true_num[indices].sum(axis=1)
        part_den_true = true_den[indices].sum(axis=1)
        part_num_false = false_num[indices].sum(axis=1)
        part_den_false = false_den[indices].sum(axis=1)
        sampled_num_true = part_num_true if sampled_num_true is None else sampled_num_true + part_num_true
        sampled_den_true = part_den_true if sampled_den_true is None else sampled_den_true + part_den_true
        sampled_num_false = part_num_false if sampled_num_false is None else sampled_num_false + part_num_false
        sampled_den_false = part_den_false if sampled_den_false is None else sampled_den_false + part_den_false
    observed_true = observed_num_true / max(observed_den_true, 1.0)
    observed_false = observed_num_false / max(observed_den_false, 1.0)
    samples = safe_ratio(sampled_num_true, sampled_den_true) - safe_ratio(sampled_num_false, sampled_den_false)
    return {
        "observed_true": observed_true,
        "observed_false": observed_false,
        "observed_delta": observed_true - observed_false,
        "ci95_low": float(np.quantile(samples, 0.025)),
        "ci95_high": float(np.quantile(samples, 0.975)),
        "denominator_true": observed_den_true,
        "denominator_false": observed_den_false,
    }


def predictive_metrics(rows: list[dict[str, Any]], iterations: int, seed: int) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    by_stratum, resamples = stratified_resamples(rows, iterations, seed)
    keys = sorted(by_stratum)
    for scope_type, scope_value, scope_rows in scopes(rows):
        opportunities = [row for row in scope_rows if row["completion_opportunity_at_20"]]
        labels = np.array([row["completion_success_at_20"] for row in opportunities], dtype="int32")
        for predictor_name, predictor_key in CONTINUOUS_PREDICTORS:
            scores = np.array([row[predictor_key] for row in opportunities], dtype="float64")
            auc = binary_auroc(labels, scores)
            ap = binary_average_precision(labels, scores)
            output.append(
                {
                    "scope_type": scope_type,
                    "scope_value": scope_value,
                    "analysis_type": "continuous_predictor",
                    "predictor": predictor_name,
                    "outcome": "completion_success_at_20",
                    "queries": len(opportunities),
                    "positives": int(labels.sum()),
                    "estimate": auc,
                    "secondary_estimate": ap,
                    "observed_true": "",
                    "observed_false": "",
                    "observed_delta": "",
                    "ci95_low": "",
                    "ci95_high": "",
                    "denominator_true": "",
                    "denominator_false": "",
                    "iterations": "",
                    "seed": "",
                }
            )
        total_successes = sum(row["completion_success_at_20"] for row in opportunities)
        for component_name, component_key in COMPONENTS:
            predicted = [row for row in opportunities if row[component_key]]
            true_positives = sum(row["completion_success_at_20"] for row in predicted)
            precision = true_positives / max(len(predicted), 1)
            recall = true_positives / max(total_successes, 1)
            output.append(
                {
                    "scope_type": scope_type,
                    "scope_value": scope_value,
                    "analysis_type": "binary_predictor",
                    "predictor": component_name,
                    "outcome": "completion_success_at_20",
                    "queries": len(opportunities),
                    "positives": total_successes,
                    "estimate": precision,
                    "secondary_estimate": recall,
                    "observed_true": "",
                    "observed_false": "",
                    "observed_delta": "",
                    "ci95_low": "",
                    "ci95_high": "",
                    "denominator_true": len(predicted),
                    "denominator_false": len(opportunities) - len(predicted),
                    "iterations": "",
                    "seed": "",
                }
            )
        selected_strata = scope_strata(scope_type, scope_value, keys)
        for component_name, component_key in COMPONENTS:
            for outcome in RATIO_OUTCOMES:
                result = bootstrap_component_contrast(
                    component_key,
                    outcome,
                    selected_strata,
                    by_stratum,
                    resamples,
                )
                output.append(
                    {
                        "scope_type": scope_type,
                        "scope_value": scope_value,
                        "analysis_type": "bootstrap_true_minus_false",
                        "predictor": component_name,
                        "outcome": outcome,
                        "queries": len(scope_rows),
                        "positives": "",
                        "estimate": "",
                        "secondary_estimate": "",
                        **result,
                        "iterations": iterations,
                        "seed": seed,
                    }
                )
    return output


def find_component_summary(
    rows: list[dict[str, Any]], group_type: str, group_name: str, group_value: str
) -> dict[str, Any]:
    return next(
        row
        for row in rows
        if row["scope_type"] == "ALL"
        and row["scope_value"] == "ALL"
        and row["group_type"] == group_type
        and row["group_name"] == group_name
        and row["group_value"] == group_value
    )


def find_predictive(
    rows: list[dict[str, Any]], analysis_type: str, predictor: str, outcome: str
) -> dict[str, Any]:
    return next(
        row
        for row in rows
        if row["scope_type"] == "ALL"
        and row["scope_value"] == "ALL"
        and row["analysis_type"] == analysis_type
        and row["predictor"] == predictor
        and row["outcome"] == outcome
    )


def write_report(
    path: Path,
    query_rows: list[dict[str, Any]],
    summaries: list[dict[str, Any]],
    predictive: list[dict[str, Any]],
    audit: dict[str, Any],
    q25_floor: float,
    args: argparse.Namespace,
    duration_seconds: float,
) -> None:
    query_path = args.output_dir / "stage2h_boundary_query_audit.csv"
    summary_path = args.output_dir / "stage2h_boundary_component_summary.csv"
    predictive_path = args.output_dir / "stage2h_boundary_predictive_metrics.csv"
    component_true = {
        name: find_component_summary(summaries, "component", name, "1") for name, _ in COMPONENTS
    }
    masks = [
        row
        for row in summaries
        if row["scope_type"] == "ALL"
        and row["scope_value"] == "ALL"
        and row["group_type"] == "overlap_mask"
    ]
    masks.sort(key=lambda row: row["queries"], reverse=True)
    dominant = max((name for name, _ in COMPONENTS[:-1]), key=lambda name: component_true[name]["prevalence"])
    lines = [
        "# Stage2H Boundary-Rule Failure Diagnosis Report",
        "",
        "## Material Passport",
        "",
        "- Origin Skill: academic-research-suite / experiment-agent",
        "- Origin Mode: run",
        f"- Origin Date: {date.today().isoformat()}",
        "- Verification Status: UNVERIFIED",
        "- Version Label: exp_result_v1",
        "- Analysis Status: EXPLORATORY POST-HOC DIAGNOSIS",
        "- Plan: `docs/STAGE2H_DIAGNOSTIC_PLAN.md`",
        "- Gold labels used for ranking or boundary classification: No",
        "- Generator used: No",
        "",
        "## Experiment Result",
        "",
        "- ID: stage2h_boundary_failure_diagnosis_1200",
        "- Type: analysis",
        "- Status: completed",
        f"- Working Directory: `{Path.cwd()}`",
        f"- Duration: {duration_seconds:.2f} seconds",
        "- Exit Code: 0",
        "",
        "### Output Files",
        "",
        "| File | Size |",
        "|---|---:|",
        f"| `{query_path}` | {query_path.stat().st_size} bytes |",
        f"| `{summary_path}` | {summary_path.stat().st_size} bytes |",
        f"| `{predictive_path}` | {predictive_path.stat().st_size} bytes |",
        "",
        "### Anomalies Detected",
        "",
        "None during the completed run.",
        "",
        "## Corpus Audit",
        "",
        f"- Slices: {audit['slice_count']}",
        f"- Total pairwise-disjoint queries: {audit['total_queries']}",
        f"- Frozen q25 score floor: {q25_floor:.10f}",
    ]
    for slice_id, item in audit["slices"].items():
        lines.append(
            f"- {slice_id}: {item['queries']} queries, {item['units']} units, {item['gold_units']} gold units, overlap={item['overlap_with_previous']}."
        )
    lines.extend(
        [
            "",
            "## OR-Component Coverage",
            "",
            "| Component | Queries | Prevalence | Trigger | Completion P@20 | Harm@20 | False insert |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for component_name, _ in COMPONENTS:
        row = component_true[component_name]
        lines.append(
            f"| {component_name} | {row['queries']} | {row['prevalence']:.4f} | {row['trigger_rate']:.4f} | "
            f"{row['completion_precision']:.4f} | {row['harm_rate']:.4f} | {row['false_insert_rate']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Exclusive Overlap Masks",
            "",
            "| Mask | Queries | Prevalence | Completion P@20 | Harm@20 | False insert |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in masks:
        lines.append(
            f"| {row['group_value']} | {row['queries']} | {row['prevalence']:.4f} | "
            f"{row['completion_precision']:.4f} | {row['harm_rate']:.4f} | {row['false_insert_rate']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Continuous Predictive Audit",
            "",
            "AUROC and average precision use triggered queries whose dense-fixed chain is incomplete at 20.",
            "",
            "| Predictor | Opportunities | Positives | AUROC | Average precision |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for predictor_name, _ in CONTINUOUS_PREDICTORS:
        row = find_predictive(predictive, "continuous_predictor", predictor_name, "completion_success_at_20")
        auc = "-" if row["estimate"] in (None, "") else f"{float(row['estimate']):.4f}"
        ap = "-" if row["secondary_estimate"] in (None, "") else f"{float(row['secondary_estimate']):.4f}"
        lines.append(f"| {predictor_name} | {row['queries']} | {row['positives']} | {auc} | {ap} |")
    lines.extend(
        [
            "",
            "## Component Contrasts",
            "",
            "| Component | Outcome | True | False | Delta | 95% CI |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for component_name, _ in COMPONENTS:
        for outcome in RATIO_OUTCOMES:
            row = find_predictive(predictive, "bootstrap_true_minus_false", component_name, outcome)
            lines.append(
                f"| {component_name} | {outcome} | {float(row['observed_true']):.4f} | "
                f"{float(row['observed_false']):.4f} | {float(row['observed_delta']):.4f} | "
                f"[{float(row['ci95_low']):.4f}, {float(row['ci95_high']):.4f}] |"
            )
    lines.extend(
        [
            "",
            "## Evidence-Grounded Diagnosis",
            "",
            f"- The highest-coverage individual component is `{dominant}` with prevalence {component_true[dominant]['prevalence']:.4f}.",
            f"- The current OR gate covers {component_true['or_gate']['prevalence']:.4f} of the 1,200 diagnostic queries.",
            "- Predictive metrics and bootstrap contrasts are descriptive. They do not validate a replacement gate or justify selecting a new threshold on these labels.",
            "",
            "## Interpretation Boundary",
            "",
            "- Stage2H reuses labels already observed in Stage2E-F-G and is therefore post-hoc.",
            "- A component with a favorable descriptive association still requires development on new data and a separately reserved frozen test.",
            "- False insert is not a hallucination metric, and no answer generator is evaluated.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--corpus",
        action="append",
        nargs=4,
        required=True,
        metavar=("SLICE_ID", "UNITS", "QUERIES", "EMBEDDING_CACHE"),
    )
    parser.add_argument("--calibration-summary", required=True, type=Path)
    parser.add_argument("--output-dir", default=Path("results"), type=Path)
    parser.add_argument("--report", default=Path("reports/超粒球RAG_Stage2H_BoundaryFailureDiagnosis报告.md"), type=Path)
    parser.add_argument("--model-name", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--max-length", type=int, default=192)
    parser.add_argument("--bootstrap-iterations", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260712)
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

    if args.bootstrap_iterations != 10000 or args.bootstrap_seed != 20260712:
        raise ValueError("Stage2H plan requires 10000 bootstrap iterations and seed 20260712")
    q25_floor = load_calibration_floor(args.calibration_summary, "score_q25")
    if not math.isclose(q25_floor, args.expected_q25_floor, abs_tol=1e-12):
        raise ValueError(f"q25 floor differs from diagnostic plan: {q25_floor}")
    corpus_specs = [
        (slice_id, Path(units), Path(queries), Path(cache))
        for slice_id, units, queries, cache in args.corpus
    ]
    if len(corpus_specs) != 3 or len({row[0] for row in corpus_specs}) != 3:
        raise ValueError("Stage2H requires exactly three uniquely named corpus slices")
    query_rows, audit = build_query_rows(corpus_specs, q25_floor, args)
    summaries = component_summaries(query_rows)
    predictive = predictive_metrics(query_rows, args.bootstrap_iterations, args.bootstrap_seed)
    query_path = args.output_dir / "stage2h_boundary_query_audit.csv"
    summary_path = args.output_dir / "stage2h_boundary_component_summary.csv"
    predictive_path = args.output_dir / "stage2h_boundary_predictive_metrics.csv"
    summary_fields = list(summaries[0].keys())
    predictive_fields = list(predictive[0].keys())
    write_csv(query_path, query_rows, QUERY_FIELDS)
    write_csv(summary_path, summaries, summary_fields)
    write_csv(predictive_path, predictive, predictive_fields)
    write_report(
        args.report,
        query_rows,
        summaries,
        predictive,
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
                "query_audit": str(query_path),
                "component_summary": str(summary_path),
                "predictive_metrics": str(predictive_path),
                "report": str(args.report),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
