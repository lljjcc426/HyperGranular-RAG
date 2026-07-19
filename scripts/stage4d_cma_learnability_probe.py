"""Fixed Stage4D-CMA grouped out-of-fold logistic probe."""

from __future__ import annotations

import argparse
import csv
import importlib.metadata
import io
import math
import os
import platform
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


THREAD_SETTINGS = {
    "PYTHONHASHSEED": "0",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "BLIS_NUM_THREADS": "1",
}

for _name, _expected in THREAD_SETTINGS.items():
    if os.environ.get(_name) != _expected:
        raise RuntimeError(
            f"{_name}={_expected} must be set before importing the Stage4D probe"
        )

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold

from stage4d_cma_candidate_trace import (
    _atomic_promote,
    load_json,
    load_jsonl,
    render_json,
)
from stage4d_cma_candidate_trace_verifier import verify_channel_a_traces


SEED = 20260719
PROBE_AUTH_ENV = "STAGE4D_PROBE_EXECUTION_AUTHORIZED"
PROBE_AUTH_VALUE = "AUTHORIZED_STAGE4D_PROBE"
FOLDS_NAME = "stage4d_cma_fold_assignments.json"
OOF_NAME = "stage4d_cma_oof_predictions.csv"
METRICS_NAME = "stage4d_cma_metrics.json"

EXPECTED_VERSIONS = {
    "joblib": "1.5.3",
    "narwhals": "2.24.0",
    "numpy": "2.5.1",
    "scikit-learn": "1.9.0",
    "scipy": "1.18.0",
    "threadpoolctl": "3.6.0",
}

PANELS = {
    "RELEVANCE_RANK_8": (
        "dense_score",
        "q25_floor_margin",
        "candidate_rank_percentile",
        "dense_rank_percentile",
        "rank_disagreement",
        "facet_score",
        "source_ball_score",
        "seed_candidate_similarity",
    ),
    "SUPPORT_STRUCTURE_10": (
        "supporting_seed_count",
        "source_ball_size",
        "source_ball_radius",
        "source_ball_compactness",
        "source_ball_boundary_fraction",
        "source_new_term_count",
        "source_shared_term_count",
        "source_facet_term_count",
        "source_redundancy",
        "source_units_per_new_term",
    ),
    "COMPLEMENTARITY_RISK_10": (
        "max_similarity_to_protected_top10",
        "mean_similarity_to_protected_top10",
        "eligible_peer_count",
        "max_similarity_to_eligible_peers",
        "mean_similarity_to_eligible_peers",
        "candidate_novel_query_facet_count",
        "has_displaced_unit",
        "displaced_unit_dense_score",
        "candidate_displaced_score_margin",
        "candidate_displaced_similarity",
    ),
}
PANELS["COMBINED_DEPLOYABLE_28"] = tuple(
    feature
    for panel in (
        "RELEVANCE_RANK_8",
        "SUPPORT_STRUCTURE_10",
        "COMPLEMENTARITY_RISK_10",
    )
    for feature in PANELS[panel]
)

TASKS = {
    "TASK_A_GAIN_VS_ALL": ("MARGINAL_GAIN", None),
    "TASK_B_HARM_VS_ALL": ("DISPLACEMENT_HARM", None),
    "TASK_C_GAIN_VS_HARM": ("MARGINAL_GAIN", "DISPLACEMENT_HARM"),
}

PRIMARY_LABELS = {
    "MARGINAL_GAIN",
    "DISPLACEMENT_HARM",
    "EVIDENCE_GAIN_ONLY",
    "EVIDENCE_HARM_ONLY",
    "INTERACTION_DEPENDENT",
    "REDUNDANT_GOLD",
    "NEUTRAL_NOISE",
}

FORBIDDEN_FEATURES = {
    "candidate_is_gold",
    "candidate_unit_id",
    "dataset",
    "delta_loo_no_backfill_cr",
    "delta_loo_no_backfill_er",
    "delta_loo_with_backfill_cr",
    "delta_loo_with_backfill_er",
    "delta_standardized_single_cr",
    "delta_standardized_single_er",
    "displaced_unit_id",
    "marginal_label",
    "original_u1_score",
    "query_id",
    "question_type",
    "sample_id",
    "source_ball_id",
    "source_edge_id",
    "trigger_u1",
}


def require_official_probe_authorization() -> None:
    if os.environ.get(PROBE_AUTH_ENV) != PROBE_AUTH_VALUE:
        raise PermissionError(
            "Official Stage4D probe is not authorized; no input was opened"
        )


def validate_runtime_environment() -> dict[str, Any]:
    if platform.python_version() != "3.12.0":
        raise RuntimeError(f"Python version differs: {platform.python_version()}")
    versions = {
        package: importlib.metadata.version(package) for package in EXPECTED_VERSIONS
    }
    if versions != EXPECTED_VERSIONS:
        raise RuntimeError(f"Stage4D package versions differ: {versions}")
    actual_threads = {name: os.environ.get(name) for name in THREAD_SETTINGS}
    if actual_threads != THREAD_SETTINGS:
        raise RuntimeError(f"Stage4D thread settings differ: {actual_threads}")
    return {
        "packages": versions,
        "python": platform.python_version(),
        "thread_settings": actual_threads,
    }


def validate_feature_panels() -> None:
    if len(PANELS["COMBINED_DEPLOYABLE_28"]) != 28:
        raise ValueError("combined panel must contain 28 fields")
    if len(set(PANELS["COMBINED_DEPLOYABLE_28"])) != 28:
        raise ValueError("combined panel contains duplicate fields")
    for panel, features in PANELS.items():
        forbidden = set(features) & FORBIDDEN_FEATURES
        if forbidden:
            raise ValueError(f"{panel} contains forbidden fields: {sorted(forbidden)}")


def build_fold_assignments(query_ids: Iterable[str], *, n_splits: int = 5) -> dict[str, int]:
    ordered: list[str] = []
    seen: set[str] = set()
    for query_id in query_ids:
        if not isinstance(query_id, str) or not query_id:
            raise ValueError("query IDs must be native non-empty strings")
        if query_id not in seen:
            seen.add(query_id)
            ordered.append(query_id)
    if len(ordered) < n_splits:
        raise ValueError("fewer query clusters than folds")
    values = np.arange(len(ordered), dtype=np.int64).reshape(-1, 1)
    groups = np.asarray(ordered, dtype=object)
    splitter = GroupKFold(n_splits=n_splits, shuffle=True, random_state=SEED)
    assignments: dict[str, int] = {}
    for fold, (_, test_indices) in enumerate(splitter.split(values, groups=groups)):
        for index in test_indices:
            assignments[ordered[int(index)]] = fold
    if set(assignments) != set(ordered):
        raise ValueError("fold assignment does not cover every query")
    return assignments


def _joined_rows(
    candidate_rows: list[dict[str, Any]], label_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    labels: dict[tuple[str, str], dict[str, Any]] = {}
    for row in label_rows:
        key = (row.get("query_id"), row.get("candidate_unit_id"))
        if not all(isinstance(value, str) and value for value in key) or key in labels:
            raise ValueError("invalid or duplicate label identity")
        if row.get("marginal_label") not in PRIMARY_LABELS:
            raise ValueError(f"unknown marginal label: {row.get('marginal_label')}")
        labels[key] = row
    result: list[dict[str, Any]] = []
    for candidate in candidate_rows:
        key = (candidate.get("query_id"), candidate.get("candidate_unit_id"))
        label = labels.pop(key, None)
        if label is None:
            raise ValueError(f"missing label for candidate {key}")
        for identity in ("dataset", "sample_id", "candidate_budget_region"):
            if candidate.get(identity) != label.get(identity):
                raise ValueError(f"candidate/label {identity} differs: {key}")
        result.append({**candidate, **label})
    if labels:
        raise ValueError("label rows contain unknown candidates")
    return result


def _task_rows(rows: list[dict[str, Any]], task: str) -> tuple[list[dict[str, Any]], np.ndarray]:
    positive, negative = TASKS[task]
    if negative is None:
        selected = list(rows)
        y = np.asarray(
            [int(row["marginal_label"] == positive) for row in selected],
            dtype=np.int64,
        )
    else:
        selected = [
            row for row in rows if row["marginal_label"] in {positive, negative}
        ]
        y = np.asarray(
            [int(row["marginal_label"] == positive) for row in selected],
            dtype=np.int64,
        )
    return selected, y


def _matrix(rows: list[dict[str, Any]], features: tuple[str, ...]) -> np.ndarray:
    matrix = np.empty((len(rows), len(features)), dtype=np.float64)
    for row_index, row in enumerate(rows):
        for column, feature in enumerate(features):
            value = row.get(feature)
            if value is None:
                matrix[row_index, column] = np.nan
            elif isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"feature {feature} must be a JSON number or null")
            else:
                number = float(value)
                if not math.isfinite(number):
                    raise ValueError(f"feature {feature} must be finite")
                matrix[row_index, column] = number
    return matrix


def _fit_preprocess(train: np.ndarray, test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    medians = np.nanmedian(train, axis=0)
    if np.isnan(medians).any():
        raise ValueError("feature is entirely null in a training fold")
    train_imputed = np.where(np.isnan(train), medians, train)
    test_imputed = np.where(np.isnan(test), medians, test)
    means = train_imputed.mean(axis=0, dtype=np.float64)
    scales = train_imputed.std(axis=0, dtype=np.float64)
    scales = np.where(scales == 0.0, 1.0, scales)
    return (train_imputed - means) / scales, (test_imputed - means) / scales


def _calibration(y: np.ndarray, probabilities: np.ndarray) -> dict[str, Any]:
    if len(np.unique(y)) != 2:
        return {"intercept": None, "reason": "one outcome class", "slope": None}
    clipped = np.clip(probabilities, 1e-6, 1.0 - 1e-6)
    logits = np.log(clipped / (1.0 - clipped)).reshape(-1, 1)
    try:
        model = LogisticRegression(
            C=np.inf,
            l1_ratio=0.0,
            solver="lbfgs",
            max_iter=1000,
            tol=1e-8,
            fit_intercept=True,
        )
        model.fit(logits, y)
        return {
            "intercept": float(model.intercept_[0]),
            "reason": None,
            "slope": float(model.coef_[0, 0]),
        }
    except Exception as error:
        return {
            "intercept": None,
            "reason": f"degenerate recalibration: {type(error).__name__}",
            "slope": None,
        }


def _metric_block(y: np.ndarray, probabilities: np.ndarray) -> dict[str, Any]:
    unique = np.unique(y)
    auc = float(roc_auc_score(y, probabilities)) if len(unique) == 2 else None
    ap = float(average_precision_score(y, probabilities)) if len(unique) == 2 else None
    matrix = confusion_matrix(y, probabilities >= 0.5, labels=[0, 1])
    return {
        "ap": ap,
        "auroc": auc,
        "brier": float(brier_score_loss(y, probabilities)),
        "calibration": _calibration(y, probabilities),
        "confusion_matrix": {
            "fn": int(matrix[1, 0]),
            "fp": int(matrix[0, 1]),
            "tn": int(matrix[0, 0]),
            "tp": int(matrix[1, 1]),
        },
        "negative_rows": int((y == 0).sum()),
        "positive_rows": int((y == 1).sum()),
        "prevalence": float(y.mean()),
    }


def _cluster_counts(rows: list[dict[str, Any]], y: np.ndarray) -> dict[str, int]:
    return {
        "negative_query_clusters": len(
            {row["query_id"] for row, value in zip(rows, y, strict=True) if value == 0}
        ),
        "positive_query_clusters": len(
            {row["query_id"] for row, value in zip(rows, y, strict=True) if value == 1}
        ),
    }


def task_feasibility(
    rows: list[dict[str, Any]],
    y: np.ndarray,
    assignments: dict[str, int],
    *,
    minimum_clusters: int = 30,
    minimum_per_fold: int = 5,
) -> dict[str, Any]:
    overall = _cluster_counts(rows, y)
    folds: dict[str, dict[str, int]] = {}
    eligible = (
        overall["positive_query_clusters"] >= minimum_clusters
        and overall["negative_query_clusters"] >= minimum_clusters
    )
    for fold in range(5):
        indices = [
            index for index, row in enumerate(rows) if assignments[row["query_id"]] == fold
        ]
        selected_rows = [rows[index] for index in indices]
        counts = _cluster_counts(selected_rows, y[indices])
        folds[str(fold)] = counts
        eligible = eligible and all(value >= minimum_per_fold for value in counts.values())
    return {
        "eligible": bool(eligible),
        "fold_query_cluster_counts": folds,
        "minimum_clusters": minimum_clusters,
        "minimum_per_fold": minimum_per_fold,
        **overall,
        "threshold_interpretation": "minimum feasibility threshold, not a power guarantee",
    }


def _bootstrap(
    rows: list[dict[str, Any]],
    y: np.ndarray,
    probabilities: np.ndarray,
    baseline_scores: np.ndarray | None,
    *,
    iterations: int,
) -> dict[str, Any]:
    if iterations < 1:
        raise ValueError("bootstrap iterations must be positive")
    by_query: dict[str, list[int]] = defaultdict(list)
    query_order: list[str] = []
    for index, row in enumerate(rows):
        query_id = row["query_id"]
        if query_id not in by_query:
            query_order.append(query_id)
        by_query[query_id].append(index)
    rng = np.random.default_rng(SEED)
    samples: dict[str, list[float]] = defaultdict(list)
    for _ in range(iterations):
        sampled_queries = rng.choice(query_order, size=len(query_order), replace=True)
        indices = np.asarray(
            [index for query_id in sampled_queries for index in by_query[str(query_id)]],
            dtype=np.int64,
        )
        sampled_y = y[indices]
        if len(np.unique(sampled_y)) != 2:
            continue
        sampled_probabilities = probabilities[indices]
        samples["auroc"].append(float(roc_auc_score(sampled_y, sampled_probabilities)))
        samples["ap"].append(float(average_precision_score(sampled_y, sampled_probabilities)))
        samples["brier"].append(float(brier_score_loss(sampled_y, sampled_probabilities)))
        if baseline_scores is not None:
            difference = roc_auc_score(sampled_y, sampled_probabilities) - roc_auc_score(
                sampled_y, baseline_scores[indices]
            )
            samples["auroc_minus_original_u1"].append(float(difference))
    result: dict[str, Any] = {"iterations_requested": iterations}
    for metric in ("auroc", "ap", "brier", "auroc_minus_original_u1"):
        values = samples.get(metric, [])
        result[metric] = (
            None
            if not values
            else {
                "lower": float(np.percentile(values, 2.5)),
                "samples": len(values),
                "upper": float(np.percentile(values, 97.5)),
            }
        )
    return result


def _baseline_metrics(
    rows: list[dict[str, Any]], y: np.ndarray, prevalence_probabilities: np.ndarray
) -> tuple[dict[str, Any], np.ndarray | None]:
    result: dict[str, Any] = {}
    for name, values in (
        ("dense_score", [row["dense_score"] for row in rows]),
        ("negative_eligible_rank", [-row["candidate_rank_in_eligible_slice"] for row in rows]),
        ("facet_score", [row["facet_score"] for row in rows]),
    ):
        array = np.asarray(values, dtype=np.float64)
        result[name] = {
            "ap": float(average_precision_score(y, array)),
            "auroc": float(roc_auc_score(y, array)),
        }
    u1_values = [row.get("original_u1_score") for row in rows]
    u1: np.ndarray | None = None
    if all(
        value is not None
        and not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
        for value in u1_values
    ):
        u1 = np.asarray(u1_values, dtype=np.float64)
        result["original_u1_score"] = {
            "ap": float(average_precision_score(y, u1)),
            "auroc": float(roc_auc_score(y, u1)),
        }
    else:
        result["original_u1_score"] = {"ap": None, "auroc": None, "reason": "null baseline"}
    result["training_prevalence"] = _metric_block(y, prevalence_probabilities)
    return result, u1


def run_synthetic_probe(
    candidate_rows: list[dict[str, Any]],
    label_rows: list[dict[str, Any]],
    query_rows: list[dict[str, Any]],
    *,
    bootstrap_iterations: int = 10_000,
    minimum_clusters: int = 30,
    minimum_per_fold: int = 5,
) -> dict[str, Any]:
    """Run fixed probes on caller-supplied rows; the name prevents official ambiguity."""

    environment = validate_runtime_environment()
    validate_feature_panels()
    joined = _joined_rows(candidate_rows, label_rows)
    query_ids = [row["query_id"] for row in query_rows]
    if len(query_ids) != len(set(query_ids)):
        raise ValueError("query trace contains duplicate IDs")
    query_u1 = {row["query_id"]: row.get("original_u1_score") for row in query_rows}
    candidate_query_ids = {row["query_id"] for row in joined}
    if not candidate_query_ids.issubset(query_u1):
        raise ValueError("candidate query IDs are missing from query trace")
    for row in joined:
        row["original_u1_score"] = query_u1[row["query_id"]]
    assignments = build_fold_assignments((row["query_id"] for row in joined))

    results: dict[str, Any] = {}
    prediction_rows: list[dict[str, Any]] = []
    for task in TASKS:
        task_rows, y = _task_rows(joined, task)
        feasibility = task_feasibility(
            task_rows,
            y,
            assignments,
            minimum_clusters=minimum_clusters,
            minimum_per_fold=minimum_per_fold,
        )
        task_result: dict[str, Any] = {"feasibility": feasibility, "panels": {}}
        if not feasibility["eligible"]:
            results[task] = task_result
            continue
        for panel, features in PANELS.items():
            x = _matrix(task_rows, features)
            probabilities = np.full(len(task_rows), np.nan, dtype=np.float64)
            prevalence_probabilities = np.full(len(task_rows), np.nan, dtype=np.float64)
            fold_metrics: dict[str, Any] = {}
            for fold in range(5):
                test = np.asarray(
                    [assignments[row["query_id"]] == fold for row in task_rows],
                    dtype=bool,
                )
                train = ~test
                if len(np.unique(y[train])) != 2:
                    raise ValueError(f"{task}/{panel}/fold{fold}: one training class")
                train_x, test_x = _fit_preprocess(x[train], x[test])
                model = LogisticRegression(
                    C=1.0,
                    l1_ratio=0.0,
                    solver="lbfgs",
                    max_iter=1000,
                    tol=1e-8,
                    fit_intercept=True,
                    class_weight=None,
                )
                model.fit(train_x, y[train])
                probabilities[test] = model.predict_proba(test_x)[:, 1]
                prevalence_probabilities[test] = float(y[train].mean())
                fold_metrics[str(fold)] = {
                    **_metric_block(y[test], probabilities[test]),
                    **_cluster_counts(
                        [row for row, selected in zip(task_rows, test, strict=True) if selected],
                        y[test],
                    ),
                }
            if not np.isfinite(probabilities).all() or not np.isfinite(prevalence_probabilities).all():
                raise ValueError(f"{task}/{panel}: incomplete OOF predictions")
            metrics = _metric_block(y, probabilities)
            baselines, u1 = _baseline_metrics(task_rows, y, prevalence_probabilities)
            metrics["baselines"] = baselines
            metrics["folds"] = fold_metrics
            metrics["query_clusters"] = len({row["query_id"] for row in task_rows})
            metrics["bootstrap"] = _bootstrap(
                task_rows,
                y,
                probabilities,
                u1,
                iterations=bootstrap_iterations,
            )
            if u1 is not None:
                metrics["auroc_minus_original_u1"] = float(
                    metrics["auroc"] - roc_auc_score(y, u1)
                )
            else:
                metrics["auroc_minus_original_u1"] = None
            strata: dict[str, Any] = {}
            for region in ("ORIGINAL_INSERT_SET", "BEYOND_ORIGINAL_BUDGET"):
                mask = np.asarray(
                    [row["candidate_budget_region"] == region for row in task_rows],
                    dtype=bool,
                )
                if not mask.any():
                    strata[region] = {
                        "candidate_rows": 0,
                        "metrics": None,
                        "negative_query_clusters": 0,
                        "positive_query_clusters": 0,
                    }
                else:
                    region_rows = [
                        row
                        for row, selected in zip(task_rows, mask, strict=True)
                        if selected
                    ]
                    region_u1 = u1[mask] if u1 is not None else None
                    strata[region] = {
                        "candidate_rows": int(mask.sum()),
                        "metrics": _metric_block(y[mask], probabilities[mask]),
                        "bootstrap": _bootstrap(
                            region_rows,
                            y[mask],
                            probabilities[mask],
                            region_u1,
                            iterations=bootstrap_iterations,
                        ),
                        **_cluster_counts(
                            region_rows,
                            y[mask],
                        ),
                    }
            metrics["candidate_budget_regions"] = strata
            task_result["panels"][panel] = metrics
            for row, outcome, probability in zip(task_rows, y, probabilities, strict=True):
                prediction_rows.append(
                    {
                        "candidate_budget_region": row["candidate_budget_region"],
                        "candidate_unit_id": row["candidate_unit_id"],
                        "fold": assignments[row["query_id"]],
                        "label": int(outcome),
                        "panel": panel,
                        "probability": float(probability),
                        "query_id": row["query_id"],
                        "task": task,
                    }
                )
        results[task] = task_result

    combined_c = results["TASK_C_GAIN_VS_HARM"]["panels"].get(
        "COMBINED_DEPLOYABLE_28"
    )
    beyond_driven = False
    if combined_c is not None and combined_c["auroc"] >= 0.65:
        original_region = combined_c["candidate_budget_regions"][
            "ORIGINAL_INSERT_SET"
        ]
        original = original_region["metrics"]
        interval = original_region.get("bootstrap", {}).get("auroc")
        beyond_driven = (
            original is None
            or original["auroc"] is None
            or original["auroc"] <= 0.55
            or interval is None
            or interval["lower"] <= 0.50 <= interval["upper"]
        )
    return {
        "beyond_budget_driven_signal": bool(beyond_driven),
        "environment": environment,
        "fold_assignments": assignments,
        "oof_predictions": prediction_rows,
        "results": results,
        "status": "SYNTHETIC_STAGE4D_PROBE_COMPLETE",
    }


def assign_scientific_decision(
    probe_result: dict[str, Any],
    *,
    integrity_passed: bool,
    feature_reproducible: bool,
    attribution_integrity_passed: bool,
    q25_gain_queries: int,
    q25_harm_queries: int,
) -> dict[str, Any]:
    """Apply the frozen combined-only advancement and panel-wide stop rules."""

    if not all((integrity_passed, feature_reproducible, attribution_integrity_passed)):
        return {
            "decision": "PAUSE_WITHOUT_SCIENTIFIC_DECISION",
            "reason": "integrity_or_reproducibility_failure",
        }
    if q25_gain_queries != 94 or q25_harm_queries != 69:
        return {
            "decision": "PAUSE_WITHOUT_SCIENTIFIC_DECISION",
            "reason": "q25_counterfactual_reconciliation_failure",
        }
    task_c = probe_result["results"]["TASK_C_GAIN_VS_HARM"]
    if not task_c["feasibility"]["eligible"]:
        return {
            "decision": "CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE",
            "reason": "task_c_event_feasibility_failed",
        }
    panels = task_c["panels"]
    if set(panels) != set(PANELS):
        return {
            "decision": "PAUSE_WITHOUT_SCIENTIFIC_DECISION",
            "reason": "fixed_panel_set_incomplete",
        }

    combined = panels["COMBINED_DEPLOYABLE_28"]
    combined_bootstrap = combined["bootstrap"]
    fold_aurocs = [combined["folds"][str(fold)]["auroc"] for fold in range(5)]
    prevalence_brier = combined["baselines"]["training_prevalence"]["brier"]
    proceed = all(
        (
            combined["auroc"] >= 0.65,
            combined_bootstrap["auroc"] is not None
            and combined_bootstrap["auroc"]["lower"] > 0.50,
            combined["ap"] >= combined["prevalence"] + 0.05,
            combined_bootstrap["ap"] is not None
            and combined_bootstrap["ap"]["lower"] > combined["prevalence"],
            combined["auroc_minus_original_u1"] is not None
            and combined["auroc_minus_original_u1"] >= 0.05,
            combined_bootstrap["auroc_minus_original_u1"] is not None
            and combined_bootstrap["auroc_minus_original_u1"]["lower"] > 0.0,
            sum(value is not None and value > 0.50 for value in fold_aurocs) >= 4,
            all(value is not None and value >= 0.45 for value in fold_aurocs),
            combined["brier"] <= prevalence_brier,
        )
    )
    if proceed:
        return {
            "beyond_budget_driven_signal": bool(
                probe_result["beyond_budget_driven_signal"]
            ),
            "decision": "PROCEED_TO_STAGE5A_U2_PROTOCOL_DESIGN",
            "reason": "combined_advancement_panel_passed_all_frozen_gates",
        }

    stop_panels = []
    for panel in PANELS:
        result = panels[panel]
        interval = result["bootstrap"]["auroc"]
        fold_values = [result["folds"][str(fold)]["auroc"] for fold in range(5)]
        stop_panels.append(
            result["auroc"] <= 0.55
            and interval is not None
            and interval["lower"] <= 0.50 <= interval["upper"]
            and result["ap"] <= result["prevalence"] + 0.05
            and sum(value is not None and value > 0.50 for value in fold_values) <= 2
        )
    if all(stop_panels):
        return {
            "decision": "STOP_ADAPTIVE_CONTROLLER_LINE",
            "reason": "all_fixed_panels_met_frozen_stop_rule",
        }
    return {
        "decision": "CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE",
        "reason": "valid_result_missed_proceed_and_stop_rules",
    }


def render_oof_csv(rows: list[dict[str, Any]]) -> bytes:
    columns = (
        "task",
        "panel",
        "query_id",
        "candidate_unit_id",
        "candidate_budget_region",
        "fold",
        "label",
        "probability",
    )
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                **{column: row[column] for column in columns if column != "probability"},
                "probability": format(row["probability"], ".17g"),
            }
        )
    return buffer.getvalue().encode("utf-8")


def run_official_probe_transaction(
    query_trace_path: Path,
    candidate_trace_path: Path,
    channel_a_manifest_path: Path,
    channel_a_verification_path: Path,
    label_path: Path,
    counterfactual_summary_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    """Future official probe transaction; authorization precedes every read."""

    require_official_probe_authorization()
    query_rows = load_jsonl(query_trace_path)
    candidate_rows = load_jsonl(candidate_trace_path)
    manifest = load_json(channel_a_manifest_path)
    verify_channel_a_traces(query_rows, candidate_rows, manifest)
    channel_a_verification = load_json(channel_a_verification_path)
    if (
        channel_a_verification.get("status") != "CHANNEL_A_TRACE_VERIFIED"
        or channel_a_verification.get("independent_reconstruction", {}).get("status")
        != "CHANNEL_A_INDEPENDENT_RECONSTRUCTION_VERIFIED"
    ):
        raise ValueError("committed Channel A verification status differs")
    label_rows = load_jsonl(label_path)
    summary = load_json(counterfactual_summary_path)
    if summary.get("status") != "CHANNEL_B_LABELS_BUILT_PENDING_VERIFICATION":
        raise ValueError("Channel B counterfactual summary status differs")

    first = run_synthetic_probe(candidate_rows, label_rows, query_rows)
    second = run_synthetic_probe(candidate_rows, label_rows, query_rows)
    first["status"] = "OFFICIAL_STAGE4D_PROBE_COMPLETE_PENDING_FINAL_VERIFICATION"
    second["status"] = "OFFICIAL_STAGE4D_PROBE_COMPLETE_PENDING_FINAL_VERIFICATION"
    first_metrics = {
        key: value
        for key, value in first.items()
        if key not in {"fold_assignments", "oof_predictions"}
    }
    second_metrics = {
        key: value
        for key, value in second.items()
        if key not in {"fold_assignments", "oof_predictions"}
    }
    first_artifacts = {
        FOLDS_NAME: render_json(first["fold_assignments"]),
        OOF_NAME: render_oof_csv(first["oof_predictions"]),
        METRICS_NAME: render_json(first_metrics),
    }
    second_artifacts = {
        FOLDS_NAME: render_json(second["fold_assignments"]),
        OOF_NAME: render_oof_csv(second["oof_predictions"]),
        METRICS_NAME: render_json(second_metrics),
    }
    if first_artifacts != second_artifacts:
        raise ValueError("official probe deterministic rerun bytes differ")

    from stage4d_cma_independent_verifier import verify_probe_outputs

    verification = verify_probe_outputs(candidate_rows, label_rows, first)
    if verification.get("status") != "STAGE4D_PROBE_VERIFIED":
        raise ValueError("independent probe verification failed")
    _atomic_promote(output_dir, first_artifacts)
    return {
        "candidate_rows": summary["candidate_rows"],
        "metrics_status": first_metrics["status"],
        "verification": verification,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query-trace", type=Path, required=True)
    parser.add_argument("--candidate-trace", type=Path, required=True)
    parser.add_argument("--channel-a-manifest", type=Path, required=True)
    parser.add_argument("--channel-a-verification", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--counterfactual-summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_official_probe_transaction(
        args.query_trace,
        args.candidate_trace,
        args.channel_a_manifest,
        args.channel_a_verification,
        args.labels,
        args.counterfactual_summary,
        args.output_dir,
    )
    print(result["metrics_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
