"""Development selection and frozen confirmation evaluation for Stage5A."""

from __future__ import annotations

import argparse
import re
import string
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from stage5a_bnh_common import (
    BASELINE_METHOD,
    BOOTSTRAP_ITERATIONS,
    BOOTSTRAP_SEED,
    CONFIRMATION_METHODS,
    DATASETS,
    HOTPOT_DATASET,
    MUSIQUE_DATASET,
    SCHEMA_VERSION,
    assert_bound,
    assert_implementation_binding,
    development_method,
    load_json,
    load_jsonl,
    path_from_config,
    render_json,
    render_jsonl,
    require_json_int,
    validate_authorization,
    validate_candidate_configs,
    write_new_files_atomically,
)


PROTECTED_METHOD = "BGE_NATIVE_HGRAG_PROTECTED_TOP20"
UNPROTECTED_METHOD = "BGE_NATIVE_HGRAG_UNPROTECTED_TOP20"
NO_FACET_METHOD = "BGE_NATIVE_HGRAG_NO_FACET_TOP20"


def normalize_answer(value: str) -> str:
    def remove_articles(text: str) -> str:
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def remove_punctuation(text: str) -> str:
        return "".join(character for character in text if character not in string.punctuation)

    return " ".join(remove_articles(remove_punctuation(value.lower())).split())


def answer_scores(prediction: str, answers: list[str]) -> tuple[float, float]:
    if not isinstance(prediction, str) or not isinstance(answers, list) or not answers:
        raise ValueError("answer score inputs differ")
    normalized_prediction = normalize_answer(prediction)
    prediction_tokens = normalized_prediction.split()
    best_em = 0.0
    best_f1 = 0.0
    for answer in answers:
        if not isinstance(answer, str):
            raise ValueError("Gold answers must be strings")
        normalized_answer = normalize_answer(answer)
        best_em = max(best_em, float(normalized_prediction == normalized_answer))
        answer_tokens = normalized_answer.split()
        common = Counter(prediction_tokens) & Counter(answer_tokens)
        overlap = sum(common.values())
        if not prediction_tokens or not answer_tokens:
            f1 = float(prediction_tokens == answer_tokens)
        elif overlap == 0:
            f1 = 0.0
        else:
            precision = overlap / len(prediction_tokens)
            recall = overlap / len(answer_tokens)
            f1 = 2.0 * precision * recall / (precision + recall)
        best_f1 = max(best_f1, f1)
    return best_em, best_f1


def _pair_map(
    rows: list[dict[str, Any]], label: str
) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"{label}[{index}] must be an object")
        query_id = row.get("query_id")
        method = row.get("method")
        if not isinstance(query_id, str) or not query_id:
            raise ValueError(f"{label}[{index}].query_id differs")
        if not isinstance(method, str) or not method:
            raise ValueError(f"{label}[{index}].method differs")
        key = (query_id, method)
        if key in result:
            raise ValueError(f"{label}: duplicate query/method pair")
        result[key] = row
    return result


def _ranking_map(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        query_id = row.get("query_id")
        if not isinstance(query_id, str) or not query_id or query_id in result:
            raise ValueError(f"rankings[{index}].query_id differs")
        result[query_id] = row
    return result


def _validated_gold(
    rows: list[dict[str, Any]],
    rankings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_query = _ranking_map(rankings)
    if len(rows) != len(rankings):
        raise ValueError("Gold/ranking row count differs")
    output: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"gold[{index}] must be an object")
        query_id = row.get("query_id")
        ranking = by_query.get(query_id)
        if ranking is None:
            raise ValueError(f"gold[{index}].query_id differs")
        if (
            row.get("dataset") != ranking.get("dataset")
            or row.get("sample_id") != ranking.get("sample_id")
        ):
            raise ValueError(f"gold[{index}] row identity differs")
        answers = row.get("answers")
        if (
            not isinstance(answers, list)
            or not answers
            or any(not isinstance(value, str) or not value.strip() for value in answers)
        ):
            raise ValueError(f"gold[{index}].answers differs")
        output.append(row)
    if {row["query_id"] for row in output} != set(by_query):
        raise ValueError("Gold query coverage differs")
    return output


def evaluate_answer_rows(
    gold_rows: list[dict[str, Any]],
    prediction_rows: list[dict[str, Any]],
    prompt_rows: list[dict[str, Any]],
    ranking_rows: list[dict[str, Any]],
    methods: tuple[str, ...],
) -> list[dict[str, Any]]:
    gold_rows = _validated_gold(gold_rows, ranking_rows)
    predictions = _pair_map(prediction_rows, "predictions")
    prompts = _pair_map(prompt_rows, "prompts")
    rankings = _ranking_map(ranking_rows)
    expected_pairs = {
        (row["query_id"], method) for row in gold_rows for method in methods
    }
    if set(predictions) != expected_pairs or set(prompts) != expected_pairs:
        raise ValueError("prediction/prompt pair coverage differs")
    audits: list[dict[str, Any]] = []
    for gold in gold_rows:
        query_id = gold["query_id"]
        ranking_row = rankings[query_id]
        if set(ranking_row.get("methods", {})) != set(methods):
            raise ValueError(f"{query_id}: ranking method set differs")
        method_results: dict[str, Any] = {}
        for method in methods:
            prediction = predictions[(query_id, method)]
            prompt = prompts[(query_id, method)]
            if (
                prediction.get("dataset") != gold["dataset"]
                or prediction.get("sample_id") != gold["sample_id"]
                or prompt.get("dataset") != gold["dataset"]
                or prompt.get("sample_id") != gold["sample_id"]
            ):
                raise ValueError(f"{query_id}/{method}: row identity differs")
            ranking = ranking_row["methods"][method]
            evidence_ids = prompt.get("evidence_unit_ids")
            if (
                not isinstance(evidence_ids, list)
                or evidence_ids != ranking[: len(evidence_ids)]
            ):
                raise ValueError(f"{query_id}/{method}: prompt is not ranking prefix")
            em, f1 = answer_scores(prediction.get("prediction"), gold["answers"])
            method_results[method] = {
                "answer_em": em,
                "answer_f1": f1,
                "evidence_count": len(evidence_ids),
                "input_token_count": require_json_int(
                    prompt.get("input_token_count"), "input_token_count"
                ),
                "unknown": float(
                    prediction["prediction"].strip().upper() == "UNKNOWN"
                ),
            }
        audits.append(
            {
                "dataset": gold["dataset"],
                "methods": method_results,
                "query_id": query_id,
                "sample_id": gold["sample_id"],
            }
        )
    return audits


def development_summary_and_selection(
    audits: list[dict[str, Any]],
    candidate_configs: list[dict[str, Any]],
    geometry_audit: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    by_dataset = {
        dataset: [row for row in audits if row["dataset"] == dataset]
        for dataset in DATASETS
    }
    if any(not rows for rows in by_dataset.values()):
        raise ValueError("development dataset rows are incomplete")
    geometry_configs = geometry_audit.get("config_summaries")
    if not isinstance(geometry_configs, dict):
        raise ValueError("geometry audit config summaries are missing")
    summaries: dict[str, Any] = {}
    eligible: list[dict[str, Any]] = []
    for config_row in candidate_configs:
        config_id = config_row["config_id"]
        method = development_method(config_id)
        datasets: dict[str, Any] = {}
        f1_deltas: list[float] = []
        em_deltas: list[float] = []
        token_deltas: list[float] = []
        for dataset in DATASETS:
            rows = by_dataset[dataset]
            protected_f1 = float(
                np.mean([row["methods"][method]["answer_f1"] for row in rows])
            )
            baseline_f1 = float(
                np.mean(
                    [row["methods"][BASELINE_METHOD]["answer_f1"] for row in rows]
                )
            )
            protected_em = float(
                np.mean([row["methods"][method]["answer_em"] for row in rows])
            )
            baseline_em = float(
                np.mean(
                    [row["methods"][BASELINE_METHOD]["answer_em"] for row in rows]
                )
            )
            token_delta = float(
                np.mean(
                    [
                        row["methods"][method]["input_token_count"]
                        - row["methods"][BASELINE_METHOD]["input_token_count"]
                        for row in rows
                    ]
                )
            )
            f1_delta = protected_f1 - baseline_f1
            em_delta = protected_em - baseline_em
            f1_deltas.append(f1_delta)
            em_deltas.append(em_delta)
            token_deltas.append(token_delta)
            datasets[dataset] = {
                "baseline_answer_em": baseline_em,
                "baseline_answer_f1": baseline_f1,
                "delta_answer_em": em_delta,
                "delta_answer_f1": f1_delta,
                "mean_incremental_input_tokens": token_delta,
                "protected_answer_em": protected_em,
                "protected_answer_f1": protected_f1,
                "query_count": len(rows),
            }
        equal_f1 = float(np.mean(f1_deltas))
        equal_em = float(np.mean(em_deltas))
        directional_conflict = f1_deltas[0] * f1_deltas[1] < 0.0
        geometry_feasible = bool(
            geometry_configs.get(config_id, {}).get("feasible")
        )
        em_guard_pass = equal_em >= -0.010
        selection_eligible = (
            geometry_feasible and not directional_conflict and em_guard_pass
        )
        summary = {
            "config": config_row,
            "dataset_equal_weight_delta_answer_em": equal_em,
            "dataset_equal_weight_delta_answer_f1": equal_f1,
            "datasets": datasets,
            "directional_conflict": directional_conflict,
            "em_guard_pass": em_guard_pass,
            "geometry_feasible": geometry_feasible,
            "mean_incremental_input_tokens": float(np.mean(token_deltas)),
            "selection_eligible": selection_eligible,
        }
        summaries[config_id] = summary
        if selection_eligible:
            eligible.append(summary)
    if not eligible:
        raise RuntimeError("STAGE5A_DEVELOPMENT_NO_SELECTION_ELIGIBLE_CONFIGURATION")
    best_f1 = max(
        row["dataset_equal_weight_delta_answer_f1"] for row in eligible
    )
    near_tie = [
        row
        for row in eligible
        if row["dataset_equal_weight_delta_answer_f1"] >= best_f1 - 0.002
    ]
    selected = min(
        near_tie,
        key=lambda row: (
            row["mean_incremental_input_tokens"],
            row["config"]["insert_budget"],
            -row["config"]["leaf_size"],
            0 if row["config"]["facet_gate"] == "STRICT" else 1,
            -float(row["config"]["unit_score_percentile"]),
            row["config"]["config_id"],
        ),
    )
    selected_config = selected["config"]
    summary = {
        "candidate_config_count": len(candidate_configs),
        "config_summaries": summaries,
        "development_selection_hierarchy": [
            "integrity_and_determinism_pass",
            "geometry_feasible",
            "no_opposite_dataset_f1_point_signs",
            "dataset_equal_weight_delta_answer_em_at_least_minus_0_010",
            "maximum_dataset_equal_weight_delta_answer_f1",
            "within_0_002_choose_lower_token_cost_then_simpler_configuration",
            "config_id_lexical_tie_break",
        ],
        "eligible_config_count": len(eligible),
        "near_tie_config_ids": [
            row["config"]["config_id"] for row in near_tie
        ],
        "schema_version": SCHEMA_VERSION,
        "selected_config_id": selected_config["config_id"],
        "status": "STAGE5A_DEVELOPMENT_EVALUATION_COMPLETE",
    }
    manifest = {
        "development_summary_status": summary["status"],
        "selection_reconstruction": {
            "best_equal_weight_f1": best_f1,
            "near_tie_threshold": 0.002,
            "selected_equal_weight_em": selected[
                "dataset_equal_weight_delta_answer_em"
            ],
            "selected_equal_weight_f1": selected[
                "dataset_equal_weight_delta_answer_f1"
            ],
            "selected_mean_incremental_input_tokens": selected[
                "mean_incremental_input_tokens"
            ],
        },
        "selected_config": selected_config,
        "status": "STAGE5A_DEVELOPMENT_UNIQUE_CONFIGURATION_FROZEN",
    }
    return summary, manifest


def _paragraph_indices(unit_ids: list[str]) -> set[int]:
    values: set[int] = set()
    for unit_id in unit_ids:
        if not isinstance(unit_id, str) or not unit_id:
            raise ValueError("unit ID differs")
        match = re.search(r"::p([0-9]+)::s[0-9]+$", unit_id)
        if match is None:
            raise ValueError(f"cannot parse paragraph from unit_id: {unit_id}")
        values.add(int(match.group(1)))
    return values


def _gold_unit_membership(gold: dict[str, Any], unit_ids: list[str]) -> set[str]:
    if gold["dataset"] == HOTPOT_DATASET:
        targets = set(gold["supporting_unit_ids"])
        return {unit_id for unit_id in unit_ids if unit_id in targets}
    targets = set(gold["supporting_paragraph_indices"])
    return {
        unit_id
        for unit_id in unit_ids
        if next(iter(_paragraph_indices([unit_id]))) in targets
    }


def evaluate_confirmation(
    gold_rows: list[dict[str, Any]],
    prediction_rows: list[dict[str, Any]],
    prompt_rows: list[dict[str, Any]],
    ranking_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    audits = evaluate_answer_rows(
        gold_rows,
        prediction_rows,
        prompt_rows,
        ranking_rows,
        CONFIRMATION_METHODS,
    )
    gold_by_query = {
        row["query_id"]: row for row in _validated_gold(gold_rows, ranking_rows)
    }
    ranking_by_query = _ranking_map(ranking_rows)
    for audit in audits:
        query_id = audit["query_id"]
        gold = gold_by_query[query_id]
        ranking_row = ranking_by_query[query_id]
        for method in CONFIRMATION_METHODS:
            ranking = ranking_row["methods"][method]
            if gold["dataset"] == HOTPOT_DATASET:
                targets = set(gold["supporting_unit_ids"])
                retrieved = set(ranking)
            else:
                targets = set(gold["supporting_paragraph_indices"])
                retrieved = _paragraph_indices(ranking)
            overlap = len(targets & retrieved)
            audit["methods"][method].update(
                {
                    "retrieval_cr20": float(overlap == len(targets)),
                    "retrieval_er20": overlap / len(targets),
                }
            )
        baseline = ranking_row["methods"][BASELINE_METHOD]
        transitions: dict[str, Any] = {}
        for method in CONFIRMATION_METHODS:
            if method == BASELINE_METHOD:
                continue
            method_ids = ranking_row["methods"][method]
            added_units = [unit_id for unit_id in method_ids if unit_id not in baseline]
            displaced_units = [
                unit_id for unit_id in baseline if unit_id not in method_ids
            ]
            added_gold_units = _gold_unit_membership(gold, added_units)
            displaced_gold_units = _gold_unit_membership(gold, displaced_units)
            if gold["dataset"] == HOTPOT_DATASET:
                targets = set(gold["supporting_unit_ids"])
                baseline_gold = set(baseline) & targets
                method_gold = set(method_ids) & targets
            else:
                targets = set(gold["supporting_paragraph_indices"])
                baseline_gold = _paragraph_indices(baseline) & targets
                method_gold = _paragraph_indices(method_ids) & targets
            added_gold = len(method_gold - baseline_gold)
            displaced_gold = len(baseline_gold - method_gold)
            answer_delta = (
                audit["methods"][method]["answer_f1"]
                - audit["methods"][BASELINE_METHOD]["answer_f1"]
            )
            transitions[method] = {
                "added_gold_evidence": added_gold,
                "added_gold_unit_count": len(added_gold_units),
                "added_non_gold_units": len(added_units) - len(added_gold_units),
                "added_unit_count": len(added_units),
                "answer_change": (
                    "GAIN"
                    if answer_delta > 0
                    else "HARM"
                    if answer_delta < 0
                    else "SAME"
                ),
                "displaced_bge_gold_evidence": displaced_gold,
                "displaced_gold_unit_count": len(displaced_gold_units),
                "displaced_non_gold_units": (
                    len(displaced_units) - len(displaced_gold_units)
                ),
                "displaced_unit_count": len(displaced_units),
                "net_gold_evidence_change": added_gold - displaced_gold,
            }
        audit["transitions_relative_to_bge"] = transitions
    return audits


def _interval(point: float, samples: np.ndarray) -> dict[str, float]:
    return {
        "ci95_lower": float(np.percentile(samples, 2.5, method="linear")),
        "ci95_upper": float(np.percentile(samples, 97.5, method="linear")),
        "point": float(point),
    }


def paired_bootstrap(
    left_f1: np.ndarray,
    right_f1: np.ndarray,
    left_em: np.ndarray,
    right_em: np.ndarray,
    seed: int,
) -> dict[str, Any]:
    arrays = (left_f1, right_f1, left_em, right_em)
    if any(
        array.ndim != 1
        or len(array) == 0
        or len(array) != len(left_f1)
        or not np.isfinite(array).all()
        for array in arrays
    ):
        raise ValueError("paired bootstrap arrays differ")
    rng = np.random.default_rng(seed)
    f1_delta = left_f1 - right_f1
    em_delta = left_em - right_em
    f1_samples = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    em_samples = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    for index in range(BOOTSTRAP_ITERATIONS):
        sample = rng.integers(0, len(f1_delta), len(f1_delta))
        f1_samples[index] = float(np.mean(f1_delta[sample]))
        em_samples[index] = float(np.mean(em_delta[sample]))
    f1 = _interval(float(np.mean(f1_delta)), f1_samples)
    em = _interval(float(np.mean(em_delta)), em_samples)
    f1["one_sided_positive_p"] = float(
        (1 + np.count_nonzero(f1_samples <= 0.0))
        / (BOOTSTRAP_ITERATIONS + 1)
    )
    return {"delta_answer_em": em, "delta_answer_f1": f1}


def equal_weight_bootstrap(
    values: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
    seed: int,
) -> dict[str, Any]:
    if set(values) != set(DATASETS):
        raise ValueError("equal-weight bootstrap datasets differ")
    rng = np.random.default_rng(seed)
    deltas = {
        dataset: (values[dataset][0] - values[dataset][1], values[dataset][2] - values[dataset][3])
        for dataset in DATASETS
    }
    f1_samples = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    em_samples = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    for index in range(BOOTSTRAP_ITERATIONS):
        f1_means: list[float] = []
        em_means: list[float] = []
        for dataset in DATASETS:
            f1_delta, em_delta = deltas[dataset]
            sample = rng.integers(0, len(f1_delta), len(f1_delta))
            f1_means.append(float(np.mean(f1_delta[sample])))
            em_means.append(float(np.mean(em_delta[sample])))
        f1_samples[index] = float(np.mean(f1_means))
        em_samples[index] = float(np.mean(em_means))
    f1_point = float(np.mean([np.mean(deltas[d][0]) for d in DATASETS]))
    em_point = float(np.mean([np.mean(deltas[d][1]) for d in DATASETS]))
    f1 = _interval(f1_point, f1_samples)
    em = _interval(em_point, em_samples)
    f1["one_sided_positive_p"] = float(
        (1 + np.count_nonzero(f1_samples <= 0.0))
        / (BOOTSTRAP_ITERATIONS + 1)
    )
    return {"delta_answer_em": em, "delta_answer_f1": f1}


def _comparison(
    by_dataset: dict[str, list[dict[str, Any]]],
    left: str,
    right: str,
    seed_offset: int,
) -> dict[str, Any]:
    datasets: dict[str, Any] = {}
    inputs: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
    for dataset_index, dataset in enumerate(DATASETS):
        rows = by_dataset[dataset]
        arrays = tuple(
            np.asarray(
                [row["methods"][method][metric] for row in rows],
                dtype="float64",
            )
            for method, metric in (
                (left, "answer_f1"),
                (right, "answer_f1"),
                (left, "answer_em"),
                (right, "answer_em"),
            )
        )
        inputs[dataset] = arrays  # type: ignore[assignment]
        datasets[dataset] = paired_bootstrap(
            *arrays, BOOTSTRAP_SEED + seed_offset * 100 + dataset_index
        )
    return {
        "contrast": f"{left} - {right}",
        "dataset_equal_weight": equal_weight_bootstrap(
            inputs, BOOTSTRAP_SEED + 1000 + seed_offset
        ),
        "datasets": datasets,
    }


def core_decision(summary: dict[str, Any]) -> str:
    pooled = summary["dataset_equal_weight"]
    f1 = pooled["delta_answer_f1"]
    em = pooled["delta_answer_em"]
    dataset_points = [
        summary["datasets"][dataset]["delta_answer_f1"]["point"]
        for dataset in DATASETS
    ]
    dataset_uppers = [
        summary["datasets"][dataset]["delta_answer_f1"]["ci95_upper"]
        for dataset in DATASETS
    ]
    if f1["ci95_upper"] < 0.0 or em["ci95_upper"] < -0.010:
        return "BGE_NATIVE_HGRAG_NEGATIVE"
    if (
        dataset_points[0] * dataset_points[1] < 0.0
        or any(value < 0.0 for value in dataset_uppers)
    ):
        return "BGE_NATIVE_HGRAG_CROSS_DATASET_HETEROGENEOUS"
    support = (
        f1["ci95_lower"] > 0.0
        and all(value > 0.0 for value in dataset_points)
        and em["ci95_lower"] >= -0.010
    )
    if support and f1["point"] >= 0.010:
        return "BGE_NATIVE_HGRAG_SUPPORTED"
    if support and 0.0 < f1["point"] < 0.010:
        return "BGE_NATIVE_HGRAG_SUPPORTED_SMALL_EFFECT"
    return "BGE_NATIVE_HGRAG_INCONCLUSIVE"


def supportive_state(summary: dict[str, Any], prefix: str) -> str:
    pooled = summary["dataset_equal_weight"]
    f1 = pooled["delta_answer_f1"]
    em = pooled["delta_answer_em"]
    if f1["ci95_lower"] > 0.0 and em["ci95_lower"] >= -0.010:
        return f"{prefix}_SUPPORTED"
    if f1["ci95_upper"] < 0.0 or em["ci95_upper"] < -0.010:
        return f"{prefix}_NEGATIVE"
    return f"{prefix}_INCONCLUSIVE"


def summarize_confirmation(
    audits: list[dict[str, Any]], telemetry: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    by_dataset = {
        dataset: [row for row in audits if row["dataset"] == dataset]
        for dataset in DATASETS
    }
    dataset_summaries: dict[str, Any] = {}
    metrics = (
        "answer_em",
        "answer_f1",
        "evidence_count",
        "input_token_count",
        "retrieval_cr20",
        "retrieval_er20",
        "unknown",
    )
    for dataset, rows in by_dataset.items():
        dataset_summaries[dataset] = {
            "methods": {
                method: {
                    metric: float(
                        np.mean(
                            [row["methods"][method][metric] for row in rows]
                        )
                    )
                    for metric in metrics
                }
                for method in CONFIRMATION_METHODS
            },
            "query_count": len(rows),
        }
    comparisons = {
        "protected_minus_bge": _comparison(
            by_dataset, PROTECTED_METHOD, BASELINE_METHOD, 0
        ),
        "protected_minus_unprotected": _comparison(
            by_dataset, PROTECTED_METHOD, UNPROTECTED_METHOD, 1
        ),
        "protected_minus_no_facet": _comparison(
            by_dataset, PROTECTED_METHOD, NO_FACET_METHOD, 2
        ),
        "unprotected_minus_bge": _comparison(
            by_dataset, UNPROTECTED_METHOD, BASELINE_METHOD, 3
        ),
    }
    decision = {
        "core_state": core_decision(comparisons["protected_minus_bge"]),
        "facet_state": supportive_state(
            comparisons["protected_minus_no_facet"], "BGE_NATIVE_FACET_INCREMENT"
        ),
        "interpretation_boundary": (
            "One frozen BGE-large-en-v1.5 backbone on closed-candidate Top-20 "
            "HotpotQA/MuSiQue confirmation IDs; no universal strong-retriever "
            "or full-wiki claim."
        ),
        "placement_state": supportive_state(
            comparisons["protected_minus_unprotected"],
            "BGE_NATIVE_PROTECTED_PLACEMENT",
        ),
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE5A_SCIENTIFIC_DECISION_FROZEN_PENDING_FINAL_VERIFICATION",
    }
    equal_weight = {
        "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "comparisons": comparisons,
        "dataset_weights": {dataset: 0.5 for dataset in DATASETS},
        "primary_comparison": "protected_minus_bge",
        "status": "STAGE5A_CONFIRMATION_STATISTICS_COMPLETE_PENDING_VERIFICATION",
    }
    core_f1 = comparisons["protected_minus_bge"]["dataset_equal_weight"][
        "delta_answer_f1"
    ]["point"]
    generation_seconds = telemetry.get("generation_seconds_by_method", {})
    incremental_seconds = float(
        generation_seconds.get(PROTECTED_METHOD, 0.0)
        - generation_seconds.get(BASELINE_METHOD, 0.0)
    )
    efficiency = {
        "embedding_cache": telemetry.get("embedding_cache"),
        "generation_seconds_by_method": generation_seconds,
        "gpu_peak_memory_bytes": telemetry.get("gpu_peak_memory_bytes"),
        "incremental_generation_seconds_protected_minus_bge": incremental_seconds,
        "incremental_seconds_per_equal_weight_f1_point": (
            incremental_seconds / core_f1 if core_f1 != 0.0 else None
        ),
        "interpretation": "DESCRIPTIVE_COST_CAUTION_ONLY_NO_DECISION_RETUNING",
        "retrieval_reconstruction_seconds": telemetry.get(
            "retrieval_reconstruction_seconds"
        ),
        "status": "STAGE5A_EFFICIENCY_SUMMARY_COMPLETE",
    }
    return dataset_summaries, equal_weight, decision, efficiency


def evidence_transition_summary(audits: list[dict[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for dataset in DATASETS:
        rows = [row for row in audits if row["dataset"] == dataset]
        output[dataset] = {}
        for method in CONFIRMATION_METHODS:
            if method == BASELINE_METHOD:
                continue
            transitions = [
                row["transitions_relative_to_bge"][method] for row in rows
            ]
            cross_tab: Counter[str] = Counter()
            for row in transitions:
                net = row["net_gold_evidence_change"]
                net_label = (
                    "POSITIVE" if net > 0 else "NEGATIVE" if net < 0 else "ZERO"
                )
                cross_tab[f"{row['answer_change']}|{net_label}"] += 1
            output[dataset][method] = {
                "added_gold_evidence_total": sum(
                    row["added_gold_evidence"] for row in transitions
                ),
                "added_non_gold_units_total": sum(
                    row["added_non_gold_units"] for row in transitions
                ),
                "answer_change_by_net_gold": dict(sorted(cross_tab.items())),
                "displaced_bge_gold_evidence_total": sum(
                    row["displaced_bge_gold_evidence"] for row in transitions
                ),
                "displaced_non_gold_units_total": sum(
                    row["displaced_non_gold_units"] for row in transitions
                ),
                "net_gold_evidence_change_total": sum(
                    row["net_gold_evidence_change"] for row in transitions
                ),
                "query_count": len(transitions),
            }
    return {
        "datasets": output,
        "interpretation": "POST_DECISION_DESCRIPTIVE_ONLY_NO_RETUNING_OR_ADVANCEMENT",
        "status": "STAGE5A_POST_GOLD_MECHANISM_AUDIT_COMPLETE",
    }


def _require_pregold(config: dict[str, Any], boundary: str) -> None:
    marker = load_json(assert_bound(config, f"{boundary}_verified_pregold"))
    expected = (
        "STAGE5A_DEVELOPMENT_PRE_GOLD_VERIFICATION_PASS"
        if boundary == "development"
        else "STAGE5A_CONFIRMATION_PRE_GOLD_VERIFICATION_PASS"
    )
    if not isinstance(marker, dict) or marker.get("status") != expected:
        raise PermissionError(f"{boundary}: pre-Gold verification has not passed")


def run_development(config: dict[str, Any]) -> None:
    _require_pregold(config, "development")
    candidate_configs = validate_candidate_configs(config)
    methods = (BASELINE_METHOD,) + tuple(
        development_method(row["config_id"]) for row in candidate_configs
    )
    rankings = load_jsonl(assert_bound(config, "development_rankings"))
    audits = evaluate_answer_rows(
        load_jsonl(assert_bound(config, "development_gold")),
        load_jsonl(assert_bound(config, "development_predictions_main")),
        load_jsonl(assert_bound(config, "development_prompt_audit_main")),
        rankings,
        methods,
    )
    geometry = load_json(assert_bound(config, "geometry_feasibility_audit"))
    if not isinstance(geometry, dict) or geometry.get("gate", {}).get("pass") is not True:
        raise PermissionError("Stage5A geometry feasibility gate has not passed")
    summary, selected = development_summary_and_selection(
        audits, candidate_configs, geometry
    )
    write_new_files_atomically(
        (
            (
                path_from_config(config, "development_query_audit"),
                render_jsonl(audits),
            ),
            (
                path_from_config(config, "development_summary"),
                render_json(summary),
            ),
            (
                path_from_config(config, "development_selected_config"),
                render_json(selected),
            ),
        )
    )
    print(
        "STAGE5A_DEVELOPMENT_UNIQUE_CONFIGURATION_FROZEN "
        f"selected={selected['selected_config']['config_id']} "
        f"eligible={summary['eligible_config_count']}"
    )


def run_confirmation(config: dict[str, Any]) -> None:
    _require_pregold(config, "confirmation")
    rankings = load_jsonl(assert_bound(config, "confirmation_rankings"))
    audits = evaluate_confirmation(
        load_jsonl(assert_bound(config, "confirmation_gold")),
        load_jsonl(assert_bound(config, "confirmation_predictions_main")),
        load_jsonl(assert_bound(config, "confirmation_prompt_audit_main")),
        rankings,
    )
    telemetry = load_json(assert_bound(config, "confirmation_telemetry_main"))
    if not isinstance(telemetry, dict):
        raise ValueError("confirmation telemetry differs")
    dataset, equal_weight, decision, efficiency = summarize_confirmation(
        audits, telemetry
    )
    evidence = evidence_transition_summary(audits)
    write_new_files_atomically(
        (
            (
                path_from_config(config, "confirmation_query_audit"),
                render_jsonl(audits),
            ),
            (
                path_from_config(config, "confirmation_dataset_summaries"),
                render_json(dataset),
            ),
            (
                path_from_config(config, "confirmation_equal_weight_summary"),
                render_json(equal_weight),
            ),
            (
                path_from_config(config, "confirmation_mechanism_audit"),
                render_json(evidence),
            ),
            (
                path_from_config(config, "confirmation_efficiency_summary"),
                render_json(efficiency),
            ),
            (
                path_from_config(config, "scientific_decision"),
                render_json(decision),
            ),
        )
    )
    print(
        "STAGE5A_CONFIRMATION_EVALUATION_COMPLETE_PENDING_FINAL_VERIFICATION "
        f"core={decision['core_state']} placement={decision['placement_state']} "
        f"facet={decision['facet_state']}"
    )


def run(config: dict[str, Any], mode: str) -> None:
    validate_authorization(config)
    assert_implementation_binding(config, Path(__file__).resolve().parents[1])
    if mode == "development":
        run_development(config)
    elif mode == "confirmation":
        run_confirmation(config)
    else:
        raise ValueError(f"unknown evaluation mode: {mode}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("development", "confirmation"))
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage5A config must be an object")
    run(config, args.mode)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE5A_EVALUATE_FAIL: {exc}", file=sys.stderr)
        raise
