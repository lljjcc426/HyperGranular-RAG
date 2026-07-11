"""Stage3A development of a utility-calibrated protected-insertion controller."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
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
from stage2f_frozen_threshold_validation import load_calibration_floor
from stage2h_boundary_failure_diagnosis import binary_auroc, binary_average_precision


FEATURES = (
    "top_ball_score",
    "ball_score_margin",
    "top_ball_radius",
    "query_to_top_ball_distance",
    "boundary_margin",
    "log1p_num_candidates",
    "log1p_selected_edge_count",
    "log1p_raw_candidate_count",
    "log1p_filtered_candidate_count",
)

STRATEGIES = (
    "dense_fixed",
    "allquery_q25_p10_i4",
    "stage2g_or_q25_p10_i4",
    "score_margin_q25_p10_i4",
    "utility_controller_q25_p10_i4",
)

QUERY_FIELDS = (
    "partition",
    "dataset",
    "query_id",
    "num_candidates",
    "top_ball_score",
    "ball_score_margin",
    "top_ball_radius",
    "query_to_top_ball_distance",
    "boundary_margin",
    "selected_edge_count",
    "raw_candidate_count",
    "filtered_candidate_count",
    "criterion_stage2g_or",
    "criterion_score_margin",
    "triggered_allquery",
    "inserted_units_allquery",
    "inserted_gold_units_allquery",
    "inserted_non_gold_units_allquery",
    "baseline_evidence_recall_at_20",
    "expanded_evidence_recall_at_20",
    "delta_evidence_recall_at_20",
    "baseline_chain_recall_at_20",
    "expanded_chain_recall_at_20",
    "delta_chain_recall_at_20",
    "gain_label",
    "harm_label",
    "gain_probability",
    "harm_probability",
    "utility_score",
    "decision_allquery",
    "decision_stage2g_or",
    "decision_score_margin",
    "decision_utility_controller",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def id_digest(ids: set[str] | list[str]) -> str:
    payload = "\n".join(sorted(ids)) + "\n"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str] | tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def source_query_ids(hotpot_path: Path, musique_path: Path, start: int, stop: int) -> set[str]:
    hotpot = load_json(hotpot_path)
    musique = load_jsonl(musique_path)
    return {f"hotpotqa::{row['_id']}" for row in hotpot[start:stop]} | {
        f"musique::{row['id']}" for row in musique[start:stop]
    }


def assign_partitions(query_ids: set[str]) -> dict[str, str]:
    assignment: dict[str, str] = {}
    for dataset in ("hotpotqa", "musique"):
        prefix = f"{dataset}::"
        ids = sorted(
            (query_id for query_id in query_ids if query_id.startswith(prefix)),
            key=lambda query_id: hashlib.sha256(
                f"stage3a_split_20260713::{query_id}".encode("utf-8")
            ).hexdigest(),
        )
        if len(ids) != 400:
            raise ValueError(f"Expected 400 Stage3A {dataset} queries, found {len(ids)}")
        for query_id in ids[:240]:
            assignment[query_id] = "fitting"
        for query_id in ids[240:]:
            assignment[query_id] = "threshold_selection"
    return assignment


def preflight_audit(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    prior_paths: list[Path],
    hotpot_path: Path,
    musique_path: Path,
    reservation_path: Path,
) -> tuple[dict[str, Any], dict[str, str]]:
    reservation = load_json(reservation_path)
    source_specs = reservation["sources"]
    source_hashes = {
        "hotpotqa": sha256_file(hotpot_path),
        "musique": sha256_file(musique_path),
    }
    for dataset in ("hotpotqa", "musique"):
        if source_hashes[dataset] != source_specs[dataset]["sha256"]:
            raise ValueError(f"{dataset} source hash differs from reservation")

    query_ids = [row["query_id"] for row in queries]
    query_set = set(query_ids)
    datasets = Counter(row["dataset"] for row in queries)
    unit_query_ids = {row["query_id"] for row in units}
    missing_gold = sum(1 for row in queries if not row.get("gold_unit_ids"))
    if len(queries) != 800 or datasets != Counter({"hotpotqa": 400, "musique": 400}):
        raise ValueError(f"Unexpected Stage3A query counts: total={len(queries)}, datasets={dict(datasets)}")
    if len(query_ids) != len(query_set):
        raise ValueError("Duplicate Stage3A query IDs")
    if missing_gold:
        raise ValueError(f"Stage3A queries missing mapped gold: {missing_gold}")
    if unit_query_ids != query_set:
        raise ValueError("Stage3A unit/query ID mismatch")

    planned_dev = source_query_ids(hotpot_path, musique_path, 600, 1000)
    reserved_test = source_query_ids(hotpot_path, musique_path, 1000, 1400)
    if query_set != planned_dev:
        raise ValueError("Stage3A query IDs differ from frozen [600:1000) rows")
    if id_digest(query_set) != reservation["stage3a_development"]["query_id_sha256"]:
        raise ValueError("Stage3A query digest differs from reservation")
    if id_digest(reserved_test) != reservation["stage3b_frozen_test"]["query_id_sha256"]:
        raise ValueError("Stage3B reservation digest differs from source rows")
    if query_set & reserved_test:
        raise ValueError("Stage3A overlaps Stage3B reserved test")

    prior_sets = [{row["query_id"] for row in load_jsonl(path)} for path in prior_paths]
    overlaps = [len(query_set & prior) for prior in prior_sets]
    reserved_overlaps = [len(reserved_test & prior) for prior in prior_sets]
    if any(overlaps) or any(reserved_overlaps):
        raise ValueError(f"Stage3 overlap audit failed: development={overlaps}, reserved={reserved_overlaps}")

    assignment = assign_partitions(query_set)
    fitting_ids = {query_id for query_id, part in assignment.items() if part == "fitting"}
    selection_ids = query_set - fitting_ids
    if id_digest(fitting_ids) != reservation["stage3a_development"]["fitting_query_id_sha256"]:
        raise ValueError("Fitting partition digest differs from reservation")
    if id_digest(selection_ids) != reservation["stage3a_development"]["threshold_selection_query_id_sha256"]:
        raise ValueError("Threshold-selection partition digest differs from reservation")

    return (
        {
            "queries": len(queries),
            "units": len(units),
            "gold_units": sum(len(row["gold_unit_ids"]) for row in queries),
            "dataset_counts": dict(datasets),
            "queries_missing_gold": missing_gold,
            "prior_overlap": overlaps,
            "stage3b_overlap": len(query_set & reserved_test),
            "stage3b_prior_overlap": reserved_overlaps,
            "development_query_id_sha256": id_digest(query_set),
            "fitting_query_id_sha256": id_digest(fitting_ids),
            "threshold_selection_query_id_sha256": id_digest(selection_ids),
            "stage3b_reserved_query_id_sha256": id_digest(reserved_test),
            "source_hashes": source_hashes,
            "stage3b_metrics_computed": False,
        },
        assignment,
    )


def zero_insert_stats() -> dict[str, int]:
    return {"inserted_units": 0, "inserted_gold_units": 0, "inserted_non_gold_units": 0}


def build_query_rows(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    assignment: dict[str, str],
    cache_path: Path,
    q25_floor: float,
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
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
        raise ValueError("Stage3A embedding/corpus dimension mismatch")

    indices_by_query: dict[str, list[int]] = defaultdict(list)
    for index, unit in enumerate(units):
        indices_by_query[unit["query_id"]].append(index)
    query_index = {query["query_id"]: index for index, query in enumerate(queries)}
    all_query_args = copy.copy(args)
    all_query_args.expand_boundary_only = False
    rows: list[dict[str, Any]] = []

    for query in queries:
        query_id = query["query_id"]
        query_embedding = query_embeddings[query_index[query_id]]
        candidate_indices = indices_by_query[query_id]
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
        filtered = [candidate for candidate in expanded if candidate["score"] >= q25_floor]
        expanded_ranked, insert_stats = protected_rerank(fixed_ranked, filtered, 10, 4, 20)
        expanded_metrics = evaluate_query(query, expanded_ranked, [20])
        triggered = int(insert_stats["inserted_units"] > 0)
        criterion_radius = int(info["boundary_margin"] <= args.decision_boundary_margin)
        criterion_score = int(info["ball_score_margin"] <= args.decision_score_margin)
        criterion_top = int(info["top_ball_score"] < args.decision_min_ball_score)
        delta_chain = expanded_metrics["chain_recall_at_20"] - baseline["chain_recall_at_20"]
        rows.append(
            {
                "partition": assignment[query_id],
                "dataset": query["dataset"],
                "query_id": query_id,
                "num_candidates": len(candidate_indices),
                "top_ball_score": info["top_ball_score"],
                "ball_score_margin": info["ball_score_margin"],
                "top_ball_radius": info["top_ball_radius"],
                "query_to_top_ball_distance": info["query_to_top_ball_distance"],
                "boundary_margin": info["boundary_margin"],
                "selected_edge_count": len(selected),
                "raw_candidate_count": len(expanded),
                "filtered_candidate_count": len(filtered),
                "criterion_stage2g_or": int(bool(criterion_radius or criterion_score or criterion_top)),
                "criterion_score_margin": criterion_score,
                "triggered_allquery": triggered,
                "inserted_units_allquery": insert_stats["inserted_units"],
                "inserted_gold_units_allquery": insert_stats["inserted_gold_units"],
                "inserted_non_gold_units_allquery": insert_stats["inserted_non_gold_units"],
                "baseline_evidence_recall_at_20": baseline["evidence_recall_at_20"],
                "expanded_evidence_recall_at_20": expanded_metrics["evidence_recall_at_20"],
                "delta_evidence_recall_at_20": (
                    expanded_metrics["evidence_recall_at_20"] - baseline["evidence_recall_at_20"]
                ),
                "baseline_chain_recall_at_20": baseline["chain_recall_at_20"],
                "expanded_chain_recall_at_20": expanded_metrics["chain_recall_at_20"],
                "delta_chain_recall_at_20": delta_chain,
                "gain_label": int(delta_chain > 0),
                "harm_label": int(delta_chain < 0),
            }
        )
    return rows


def feature_matrix(rows: list[dict[str, Any]]) -> np.ndarray:
    return np.asarray(
        [
            [
                row["top_ball_score"],
                row["ball_score_margin"],
                row["top_ball_radius"],
                row["query_to_top_ball_distance"],
                row["boundary_margin"],
                math.log1p(row["num_candidates"]),
                math.log1p(row["selected_edge_count"]),
                math.log1p(row["raw_candidate_count"]),
                math.log1p(row["filtered_candidate_count"]),
            ]
            for row in rows
        ],
        dtype="float64",
    )


def sigmoid(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-values))


def fit_logistic_head(
    matrix: np.ndarray,
    labels: np.ndarray,
    regularization: float = 1.0,
    max_iterations: int = 100,
    tolerance: float = 1e-9,
) -> dict[str, Any]:
    positives = int(labels.sum())
    negatives = len(labels) - positives
    if positives < 5 or negatives < 5:
        probability = (positives + 1.0) / (len(labels) + 2.0)
        return {
            "fallback": True,
            "fallback_probability": probability,
            "coefficients": [math.log(probability / (1.0 - probability))] + [0.0] * matrix.shape[1],
            "iterations": 0,
            "converged": True,
            "positives": positives,
            "negatives": negatives,
        }

    design = np.column_stack([np.ones(len(matrix)), matrix])
    coefficients = np.zeros(design.shape[1], dtype="float64")
    penalty = np.diag([0.0] + [regularization] * matrix.shape[1])
    converged = False
    iteration = 0
    for iteration in range(1, max_iterations + 1):
        probabilities = sigmoid(design @ coefficients)
        weights = probabilities * (1.0 - probabilities)
        gradient = design.T @ (probabilities - labels) + penalty @ coefficients
        hessian = design.T @ (design * weights[:, None]) + penalty
        try:
            step = np.linalg.solve(hessian, gradient)
        except np.linalg.LinAlgError as error:
            raise RuntimeError("Logistic Newton system is singular") from error
        updated = coefficients - step
        if float(np.max(np.abs(updated - coefficients))) < tolerance:
            coefficients = updated
            converged = True
            break
        coefficients = updated
    if not converged:
        raise RuntimeError(f"Logistic head did not converge within {max_iterations} iterations")
    return {
        "fallback": False,
        "fallback_probability": None,
        "coefficients": coefficients.tolist(),
        "iterations": iteration,
        "converged": converged,
        "positives": positives,
        "negatives": negatives,
    }


def predict_head(matrix: np.ndarray, model: dict[str, Any]) -> np.ndarray:
    if model["fallback"]:
        return np.full(len(matrix), model["fallback_probability"], dtype="float64")
    design = np.column_stack([np.ones(len(matrix)), matrix])
    return sigmoid(design @ np.asarray(model["coefficients"], dtype="float64"))


def fit_controller(rows: list[dict[str, Any]]) -> dict[str, Any]:
    matrix = feature_matrix(rows)
    fit_indices = np.asarray([index for index, row in enumerate(rows) if row["partition"] == "fitting"])
    fit_matrix = matrix[fit_indices]
    means = fit_matrix.mean(axis=0)
    scales = fit_matrix.std(axis=0)
    zero_variance = scales == 0
    scales[zero_variance] = 1.0
    standardized = (matrix - means) / scales
    standardized[:, zero_variance] = 0.0
    gain_labels = np.asarray([row["gain_label"] for row in rows], dtype="float64")
    harm_labels = np.asarray([row["harm_label"] for row in rows], dtype="float64")
    gain_model = fit_logistic_head(standardized[fit_indices], gain_labels[fit_indices])
    harm_model = fit_logistic_head(standardized[fit_indices], harm_labels[fit_indices])
    gain_probability = predict_head(standardized, gain_model)
    harm_probability = predict_head(standardized, harm_model)
    utility_score = gain_probability - harm_probability
    for index, row in enumerate(rows):
        row["gain_probability"] = gain_probability[index]
        row["harm_probability"] = harm_probability[index]
        row["utility_score"] = utility_score[index]
    return {
        "feature_order": list(FEATURES),
        "means": means.tolist(),
        "scales": scales.tolist(),
        "zero_variance_features": [FEATURES[index] for index in np.flatnonzero(zero_variance)],
        "regularization_lambda": 1.0,
        "optimizer": "Newton",
        "max_iterations": 100,
        "tolerance": 1e-9,
        "gain_head": gain_model,
        "harm_head": harm_model,
    }


def threshold_stats(rows: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    selected = [
        row
        for row in rows
        if row["triggered_allquery"] and row["utility_score"] >= threshold
    ]
    allquery_gains = sum(row["gain_label"] for row in rows)
    selected_gains = sum(row["gain_label"] for row in selected)
    return {
        "threshold": threshold,
        "selected_gains": selected_gains,
        "allquery_gains": allquery_gains,
        "gain_retention": selected_gains / max(allquery_gains, 1),
        "inserted_non_gold_units": sum(row["inserted_non_gold_units_allquery"] for row in selected),
        "harm_events": sum(row["harm_label"] for row in selected),
        "triggered_queries": len(selected),
    }


def select_threshold(rows: list[dict[str, Any]]) -> dict[str, Any]:
    selection = [row for row in rows if row["partition"] == "threshold_selection"]
    unique_scores = sorted({float(row["utility_score"]) for row in selection})
    if not unique_scores:
        raise ValueError("No threshold-selection utility scores")
    finite_thresholds = unique_scores[1:]
    eligible: list[dict[str, Any]] = []
    for threshold in finite_thresholds:
        stats = threshold_stats(selection, threshold)
        if stats["allquery_gains"] > 0 and stats["gain_retention"] >= 0.80:
            eligible.append(stats)
    if not eligible:
        stats = threshold_stats(selection, -math.inf)
        stats.update({"mode": "expand_all", "development_failed": True})
        return stats
    chosen = min(
        eligible,
        key=lambda row: (
            row["inserted_non_gold_units"],
            row["harm_events"],
            -row["selected_gains"],
            row["triggered_queries"],
            -row["threshold"],
        ),
    )
    chosen.update({"mode": "finite", "development_failed": False})
    return chosen


def apply_decisions(rows: list[dict[str, Any]], threshold: float) -> None:
    for row in rows:
        triggered = bool(row["triggered_allquery"])
        row["decision_allquery"] = int(triggered)
        row["decision_stage2g_or"] = int(triggered and row["criterion_stage2g_or"])
        row["decision_score_margin"] = int(triggered and row["criterion_score_margin"])
        row["decision_utility_controller"] = int(triggered and row["utility_score"] >= threshold)


def decision_key(strategy_id: str) -> str | None:
    return {
        "dense_fixed": None,
        "allquery_q25_p10_i4": "decision_allquery",
        "stage2g_or_q25_p10_i4": "decision_stage2g_or",
        "score_margin_q25_p10_i4": "decision_score_margin",
        "utility_controller_q25_p10_i4": "decision_utility_controller",
    }[strategy_id]


def selected(row: dict[str, Any], strategy_id: str) -> bool:
    key = decision_key(strategy_id)
    return bool(key and row[key])


def strategy_value(row: dict[str, Any], strategy_id: str, metric: str) -> float:
    use_expansion = selected(row, strategy_id)
    if metric == "evidence_recall_at_20":
        return row["expanded_evidence_recall_at_20"] if use_expansion else row["baseline_evidence_recall_at_20"]
    if metric == "chain_recall_at_20":
        return row["expanded_chain_recall_at_20"] if use_expansion else row["baseline_chain_recall_at_20"]
    if metric == "trigger":
        return float(use_expansion)
    if metric == "inserted_units":
        return float(row["inserted_units_allquery"] if use_expansion else 0)
    if metric == "inserted_gold_units":
        return float(row["inserted_gold_units_allquery"] if use_expansion else 0)
    if metric == "inserted_non_gold_units":
        return float(row["inserted_non_gold_units_allquery"] if use_expansion else 0)
    raise KeyError(metric)


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for partition in ("fitting", "threshold_selection"):
        partition_rows = [row for row in rows if row["partition"] == partition]
        scopes = [("ALL", partition_rows)] + [
            (dataset, [row for row in partition_rows if row["dataset"] == dataset])
            for dataset in ("hotpotqa", "musique")
        ]
        for dataset, items in scopes:
            allquery_gains = sum(row["gain_label"] for row in items)
            for strategy_id in STRATEGIES:
                n = len(items)
                evidence = sum(strategy_value(row, strategy_id, "evidence_recall_at_20") for row in items) / n
                chain = sum(strategy_value(row, strategy_id, "chain_recall_at_20") for row in items) / n
                baseline_evidence = sum(row["baseline_evidence_recall_at_20"] for row in items) / n
                baseline_chain = sum(row["baseline_chain_recall_at_20"] for row in items) / n
                inserted = sum(strategy_value(row, strategy_id, "inserted_units") for row in items)
                inserted_gold = sum(strategy_value(row, strategy_id, "inserted_gold_units") for row in items)
                inserted_non_gold = inserted - inserted_gold
                triggered_queries = int(sum(strategy_value(row, strategy_id, "trigger") for row in items))
                gains = sum(row["gain_label"] for row in items if selected(row, strategy_id))
                harms = sum(row["harm_label"] for row in items if selected(row, strategy_id))
                output.append(
                    {
                        "partition": partition,
                        "dataset": dataset,
                        "strategy_id": strategy_id,
                        "queries": n,
                        "triggered_queries": triggered_queries,
                        "trigger_rate": triggered_queries / n,
                        "avg_inserted_units": inserted / n,
                        "inserted_gold_per_query": inserted_gold / n,
                        "inserted_non_gold_per_query": inserted_non_gold / n,
                        "insert_yield": inserted_gold / max(inserted, 1.0),
                        "false_insert_rate": inserted_non_gold / max(inserted, 1.0),
                        "evidence_recall_at_20": evidence,
                        "chain_recall_at_20": chain,
                        "delta_evidence_recall_vs_dense": evidence - baseline_evidence,
                        "delta_chain_recall_vs_dense": chain - baseline_chain,
                        "successful_improvements": gains,
                        "harm_events": harms,
                        "net_completed_chain_change": gains - harms,
                        "allquery_successful_improvements": allquery_gains,
                        "gain_retention": gains / max(allquery_gains, 1),
                    }
                )
    return output


def model_metrics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for partition in ("fitting", "threshold_selection"):
        partition_rows = [row for row in rows if row["partition"] == partition]
        scopes = [("ALL", partition_rows)] + [
            (dataset, [row for row in partition_rows if row["dataset"] == dataset])
            for dataset in ("hotpotqa", "musique")
        ]
        for dataset, items in scopes:
            for head, label_key, score_key in (
                ("gain", "gain_label", "gain_probability"),
                ("harm", "harm_label", "harm_probability"),
            ):
                labels = np.asarray([row[label_key] for row in items], dtype="int64")
                scores = np.asarray([row[score_key] for row in items], dtype="float64")
                output.append(
                    {
                        "partition": partition,
                        "dataset": dataset,
                        "head": head,
                        "queries": len(items),
                        "positives": int(labels.sum()),
                        "auroc": binary_auroc(labels, scores),
                        "average_precision": binary_average_precision(labels, scores),
                    }
                )
    return output


def metric_stat(items: list[dict[str, Any]], strategy_id: str, metric: str) -> float:
    if metric == "false_insert_rate":
        inserted = sum(strategy_value(row, strategy_id, "inserted_units") for row in items)
        non_gold = sum(strategy_value(row, strategy_id, "inserted_non_gold_units") for row in items)
        return non_gold / max(inserted, 1.0)
    return sum(strategy_value(row, strategy_id, metric) for row in items) / len(items)


def bootstrap_comparisons(
    rows: list[dict[str, Any]], iterations: int, seed: int
) -> list[dict[str, Any]]:
    selection = [row for row in rows if row["partition"] == "threshold_selection"]
    by_dataset = {
        dataset: [row for row in selection if row["dataset"] == dataset]
        for dataset in ("hotpotqa", "musique")
    }
    rng = np.random.default_rng(seed)
    samples = {
        dataset: rng.integers(0, len(items), size=(iterations, len(items)), dtype=np.int32)
        for dataset, items in by_dataset.items()
    }
    comparisons = (
        ("utility_vs_allquery", "utility_controller_q25_p10_i4", "allquery_q25_p10_i4"),
        ("utility_vs_dense", "utility_controller_q25_p10_i4", "dense_fixed"),
    )
    metrics = (
        "chain_recall_at_20",
        "evidence_recall_at_20",
        "trigger",
        "inserted_non_gold_units",
        "false_insert_rate",
    )
    output: list[dict[str, Any]] = []
    for comparison_id, strategy_a, strategy_b in comparisons:
        for metric in metrics:
            observed_a = metric_stat(selection, strategy_a, metric)
            observed_b = metric_stat(selection, strategy_b, metric)
            deltas = np.empty(iterations, dtype="float64")
            for iteration in range(iterations):
                sampled: list[dict[str, Any]] = []
                for dataset in ("hotpotqa", "musique"):
                    items = by_dataset[dataset]
                    sampled.extend(items[index] for index in samples[dataset][iteration])
                deltas[iteration] = metric_stat(sampled, strategy_a, metric) - metric_stat(
                    sampled, strategy_b, metric
                )
            output.append(
                {
                    "comparison_id": comparison_id,
                    "strategy_a": strategy_a,
                    "strategy_b": strategy_b,
                    "metric": metric,
                    "observed_a": observed_a,
                    "observed_b": observed_b,
                    "observed_delta": observed_a - observed_b,
                    "ci_low": float(np.quantile(deltas, 0.025)),
                    "ci_high": float(np.quantile(deltas, 0.975)),
                    "iterations": iterations,
                    "seed": seed,
                    "status": "DESCRIPTIVE_DEVELOPMENT",
                }
            )
    return output


def find_summary(
    summaries: list[dict[str, Any]], partition: str, dataset: str, strategy_id: str
) -> dict[str, Any]:
    return next(
        row
        for row in summaries
        if row["partition"] == partition
        and row["dataset"] == dataset
        and row["strategy_id"] == strategy_id
    )


def promotion_decision(
    summaries: list[dict[str, Any]], threshold: dict[str, Any], model: dict[str, Any]
) -> dict[str, Any]:
    utility = find_summary(
        summaries, "threshold_selection", "ALL", "utility_controller_q25_p10_i4"
    )
    allquery = find_summary(summaries, "threshold_selection", "ALL", "allquery_q25_p10_i4")
    non_gold_reduction = 1.0 - utility["inserted_non_gold_per_query"] / max(
        allquery["inserted_non_gold_per_query"], 1e-12
    )
    checks = {
        "gain_retention_at_least_0_80": utility["gain_retention"] >= 0.80,
        "non_gold_reduction_at_least_0_20": non_gold_reduction >= 0.20,
        "cr20_gap_at_least_minus_0_01": (
            utility["chain_recall_at_20"] - allquery["chain_recall_at_20"] >= -0.01
        ),
        "positive_net_completed_chain_change": utility["net_completed_chain_change"] > 0,
        "not_expand_all": threshold["mode"] != "expand_all",
        "no_sparse_target_fallback": not model["gain_head"]["fallback"]
        and not model["harm_head"]["fallback"],
    }
    return {
        "checks": checks,
        "passed": all(checks.values()),
        "gain_retention": utility["gain_retention"],
        "non_gold_reduction": non_gold_reduction,
        "cr20_gap_vs_allquery": utility["chain_recall_at_20"] - allquery["chain_recall_at_20"],
        "net_completed_chain_change": utility["net_completed_chain_change"],
    }


def write_report(
    path: Path,
    audit: dict[str, Any],
    q25_floor: float,
    model: dict[str, Any],
    metrics: list[dict[str, Any]],
    threshold: dict[str, Any],
    summaries: list[dict[str, Any]],
    bootstrap: list[dict[str, Any]],
    promotion: dict[str, Any],
    duration: float,
) -> None:
    selection_summaries = [
        row for row in summaries if row["partition"] == "threshold_selection" and row["dataset"] == "ALL"
    ]
    metric_rows = [row for row in metrics if row["partition"] == "threshold_selection" and row["dataset"] == "ALL"]
    lines = [
        "# Stage3A Utility-Calibrated Controller Development Report",
        "",
        "## Material Passport",
        "",
        "- Origin Skill: academic-research-suite / experiment-agent",
        "- Origin Mode: run",
        f"- Origin Date: {date.today().isoformat()}",
        "- Verification Status: UNVERIFIED",
        "- Version Label: exp_result_v1",
        "- Analysis Status: DEVELOPMENT; NOT CONFIRMATORY",
        "- Protocol: `docs/STAGE3A_PROTOCOL.md`",
        "- Stage3B metrics computed: No",
        "",
        "## Experiment Result",
        "",
        "- ID: stage3a_utility_controller_dev800",
        "- Type: analysis",
        "- Status: completed",
        f"- Duration: {duration:.2f} seconds",
        "- Exit Code: 0",
        "",
        "## Data Audit",
        "",
        f"- Queries/units/gold units: {audit['queries']}/{audit['units']}/{audit['gold_units']}",
        f"- Prior overlap: {audit['prior_overlap']}",
        f"- Stage3B overlap: {audit['stage3b_overlap']}",
        f"- Frozen q25 floor: {q25_floor:.10f}",
        f"- Development query digest: `{audit['development_query_id_sha256']}`",
        f"- Reserved Stage3B query digest: `{audit['stage3b_reserved_query_id_sha256']}`",
        "",
        "## Model Audit",
        "",
        f"- Gain head positives/negatives: {model['gain_head']['positives']}/{model['gain_head']['negatives']}",
        f"- Harm head positives/negatives: {model['harm_head']['positives']}/{model['harm_head']['negatives']}",
        f"- Gain fallback: {model['gain_head']['fallback']}",
        f"- Harm fallback: {model['harm_head']['fallback']}",
        f"- Threshold mode/value: {threshold['mode']} / {threshold['threshold']}",
        "",
        "| Head | AUROC | Average precision | Positives |",
        "|---|---:|---:|---:|",
    ]
    for row in metric_rows:
        auroc = "NA" if row["auroc"] is None else f"{row['auroc']:.4f}"
        ap = "NA" if row["average_precision"] is None else f"{row['average_precision']:.4f}"
        lines.append(f"| {row['head']} | {auroc} | {ap} | {row['positives']} |")
    lines.extend(
        [
            "",
            "## Threshold-Selection Results",
            "",
            "| Strategy | Trigger | Non-gold/query | ER@20 | CR@20 | Gains | Harms | Net | Gain retention |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in selection_summaries:
        lines.append(
            f"| {row['strategy_id']} | {row['trigger_rate']:.4f} | "
            f"{row['inserted_non_gold_per_query']:.4f} | {row['evidence_recall_at_20']:.4f} | "
            f"{row['chain_recall_at_20']:.4f} | {row['successful_improvements']} | "
            f"{row['harm_events']} | {row['net_completed_chain_change']} | {row['gain_retention']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Promotion Gate",
            "",
            f"- Decision: {'PASS' if promotion['passed'] else 'FAIL'}",
        ]
    )
    for name, passed in promotion["checks"].items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    lines.extend(
        [
            "",
            "## Bootstrap Boundary",
            "",
            f"- Descriptive paired bootstrap rows: {len(bootstrap)}",
            "- The threshold was selected on the same 320-query partition; intervals are not confirmatory.",
            "",
            "## Interpretation Boundary",
            "",
            "Stage3A may freeze a controller for later testing, but it cannot establish generalization. "
            "Stage3B remains locked and no Stage3B embeddings or retrieval metrics were produced.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", required=True, type=Path)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--prior-queries", nargs=3, required=True, type=Path)
    parser.add_argument("--hotpot-source", required=True, type=Path)
    parser.add_argument("--musique-source", required=True, type=Path)
    parser.add_argument("--reservation", default=Path("docs/STAGE3_DATA_RESERVATION.json"), type=Path)
    parser.add_argument("--calibration-summary", required=True, type=Path)
    parser.add_argument("--embedding-cache", required=True, type=Path)
    parser.add_argument("--output-dir", default=Path("results"), type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--model-name", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--max-length", type=int, default=192)
    parser.add_argument("--bootstrap-iterations", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260713)
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start = perf_counter()
    if args.bootstrap_iterations != 10000 or args.bootstrap_seed != 20260713:
        raise ValueError("Stage3A protocol requires 10000 bootstrap iterations and seed 20260713")
    q25_floor = load_calibration_floor(args.calibration_summary, "score_q25")
    if not math.isclose(q25_floor, args.expected_q25_floor, abs_tol=1e-12):
        raise ValueError(f"q25 floor differs from Stage3A protocol: {q25_floor}")

    units = load_jsonl(args.units)
    queries = load_jsonl(args.queries)
    audit, assignment = preflight_audit(
        units,
        queries,
        args.prior_queries,
        args.hotpot_source,
        args.musique_source,
        args.reservation,
    )
    rows = build_query_rows(units, queries, assignment, args.embedding_cache, q25_floor, args)
    model = fit_controller(rows)
    threshold = select_threshold(rows)
    model["selected_threshold"] = threshold
    apply_decisions(rows, threshold["threshold"])
    summaries = summarize(rows)
    metrics = model_metrics(rows)
    bootstrap = bootstrap_comparisons(rows, args.bootstrap_iterations, args.bootstrap_seed)
    promotion = promotion_decision(summaries, threshold, model)
    model["predictive_metrics"] = metrics
    model["promotion"] = promotion
    model["protocol"] = "docs/STAGE3A_PROTOCOL.md"
    model["reservation"] = str(args.reservation)
    model["q25_floor"] = q25_floor
    model["model_name"] = args.model_name

    query_path = args.output_dir / "stage3a_utility_controller_query_audit.csv"
    model_path = args.output_dir / "stage3a_utility_controller_model.json"
    summary_path = args.output_dir / "stage3a_utility_controller_summary.csv"
    bootstrap_path = args.output_dir / "stage3a_utility_controller_bootstrap.csv"
    write_csv(query_path, rows, QUERY_FIELDS)
    write_csv(summary_path, summaries, list(summaries[0]))
    write_csv(bootstrap_path, bootstrap, list(bootstrap[0]))
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.write_text(json.dumps(model, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    write_report(
        args.report,
        audit,
        q25_floor,
        model,
        metrics,
        threshold,
        summaries,
        bootstrap,
        promotion,
        perf_counter() - start,
    )
    print(
        json.dumps(
            {
                "audit": audit,
                "threshold": threshold,
                "promotion": promotion,
                "query_audit": str(query_path),
                "model": str(model_path),
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
