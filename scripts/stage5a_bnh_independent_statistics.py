"""Independent Stage5A answer, bootstrap, decision, and mechanism rebuild."""

from __future__ import annotations

import re
import string
from collections import Counter
from typing import Any

import numpy as np

from stage5a_bnh_common import (
    BASELINE_METHOD,
    BOOTSTRAP_ITERATIONS,
    BOOTSTRAP_SEED,
    CONFIRMATION_METHODS,
    DATASETS,
    HOTPOT_DATASET,
    SCHEMA_VERSION,
    development_method,
    require_json_int,
)


PROTECTED = "BGE_NATIVE_HGRAG_PROTECTED_TOP20"
UNPROTECTED = "BGE_NATIVE_HGRAG_UNPROTECTED_TOP20"
NO_FACET = "BGE_NATIVE_HGRAG_NO_FACET_TOP20"


def _normalize(value: str) -> str:
    lowered = value.lower()
    without_punctuation = "".join(
        character for character in lowered if character not in string.punctuation
    )
    without_articles = re.sub(r"\b(a|an|the)\b", " ", without_punctuation)
    return " ".join(without_articles.split())


def _answer_scores(prediction: str, answers: list[str]) -> tuple[float, float]:
    if not isinstance(prediction, str) or not isinstance(answers, list) or not answers:
        raise ValueError("independent answer score inputs differ")
    prediction_value = _normalize(prediction)
    prediction_tokens = prediction_value.split()
    em_values: list[float] = []
    f1_values: list[float] = []
    for answer in answers:
        if not isinstance(answer, str):
            raise ValueError("independent Gold answer type differs")
        answer_value = _normalize(answer)
        answer_tokens = answer_value.split()
        em_values.append(float(prediction_value == answer_value))
        overlap = sum((Counter(prediction_tokens) & Counter(answer_tokens)).values())
        if not prediction_tokens or not answer_tokens:
            f1 = float(prediction_tokens == answer_tokens)
        elif overlap == 0:
            f1 = 0.0
        else:
            precision = overlap / len(prediction_tokens)
            recall = overlap / len(answer_tokens)
            f1 = 2.0 * precision * recall / (precision + recall)
        f1_values.append(f1)
    return max(em_values), max(f1_values)


def _pairs(
    rows: list[dict[str, Any]], label: str
) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(rows):
        query_id = row.get("query_id")
        method = row.get("method")
        if (
            not isinstance(query_id, str)
            or not query_id
            or not isinstance(method, str)
            or not method
        ):
            raise ValueError(f"{label}[{index}] identity differs")
        key = (query_id, method)
        if key in result:
            raise ValueError(f"{label}: duplicate pair")
        result[key] = row
    return result


def _rankings(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        query_id = row.get("query_id")
        if not isinstance(query_id, str) or not query_id or query_id in result:
            raise ValueError(f"rankings[{index}] identity differs")
        result[query_id] = row
    return result


def independent_answer_audit(
    gold_rows: list[dict[str, Any]],
    prediction_rows: list[dict[str, Any]],
    prompt_rows: list[dict[str, Any]],
    ranking_rows: list[dict[str, Any]],
    methods: tuple[str, ...],
) -> list[dict[str, Any]]:
    ranking_map = _rankings(ranking_rows)
    prediction_map = _pairs(prediction_rows, "predictions")
    prompt_map = _pairs(prompt_rows, "prompts")
    if len(gold_rows) != len(ranking_rows):
        raise ValueError("independent Gold/ranking count differs")
    expected = {
        (row["query_id"], method) for row in gold_rows for method in methods
    }
    if set(prediction_map) != expected or set(prompt_map) != expected:
        raise ValueError("independent prediction/prompt coverage differs")
    audits: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, gold in enumerate(gold_rows):
        query_id = gold.get("query_id")
        ranking_row = ranking_map.get(query_id)
        if (
            ranking_row is None
            or query_id in seen
            or gold.get("dataset") != ranking_row.get("dataset")
            or gold.get("sample_id") != ranking_row.get("sample_id")
        ):
            raise ValueError(f"gold[{index}] independent identity differs")
        seen.add(query_id)
        answers = gold.get("answers")
        if (
            not isinstance(answers, list)
            or not answers
            or any(not isinstance(answer, str) or not answer.strip() for answer in answers)
        ):
            raise ValueError(f"gold[{index}] answers differ")
        if set(ranking_row.get("methods", {})) != set(methods):
            raise ValueError(f"{query_id}: independent method set differs")
        output_methods: dict[str, Any] = {}
        for method in methods:
            prediction = prediction_map[(query_id, method)]
            prompt = prompt_map[(query_id, method)]
            if (
                prediction.get("dataset") != gold["dataset"]
                or prediction.get("sample_id") != gold["sample_id"]
                or prompt.get("dataset") != gold["dataset"]
                or prompt.get("sample_id") != gold["sample_id"]
            ):
                raise ValueError(f"{query_id}/{method}: independent identity differs")
            evidence = prompt.get("evidence_unit_ids")
            ranking = ranking_row["methods"][method]
            if not isinstance(evidence, list) or evidence != ranking[: len(evidence)]:
                raise ValueError(f"{query_id}/{method}: prompt prefix differs")
            em, f1 = _answer_scores(prediction.get("prediction"), answers)
            output_methods[method] = {
                "answer_em": em,
                "answer_f1": f1,
                "evidence_count": len(evidence),
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
                "methods": output_methods,
                "query_id": query_id,
                "sample_id": gold["sample_id"],
            }
        )
    if seen != set(ranking_map):
        raise ValueError("independent Gold coverage differs")
    return audits


def independent_development_outputs(
    audits: list[dict[str, Any]],
    candidate_configs: list[dict[str, Any]],
    geometry: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    by_dataset = {
        dataset: [row for row in audits if row["dataset"] == dataset]
        for dataset in DATASETS
    }
    geometry_configs = geometry.get("config_summaries")
    if not isinstance(geometry_configs, dict):
        raise ValueError("independent geometry summaries differ")
    summaries: dict[str, Any] = {}
    eligible: list[dict[str, Any]] = []
    for config in candidate_configs:
        config_id = config["config_id"]
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
                np.mean([row["methods"][BASELINE_METHOD]["answer_f1"] for row in rows])
            )
            protected_em = float(
                np.mean([row["methods"][method]["answer_em"] for row in rows])
            )
            baseline_em = float(
                np.mean([row["methods"][BASELINE_METHOD]["answer_em"] for row in rows])
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
        summary = {
            "config": config,
            "dataset_equal_weight_delta_answer_em": equal_em,
            "dataset_equal_weight_delta_answer_f1": equal_f1,
            "datasets": datasets,
            "directional_conflict": f1_deltas[0] * f1_deltas[1] < 0.0,
            "em_guard_pass": equal_em >= -0.010,
            "geometry_feasible": bool(
                geometry_configs.get(config_id, {}).get("feasible")
            ),
            "mean_incremental_input_tokens": float(np.mean(token_deltas)),
        }
        summary["selection_eligible"] = (
            summary["geometry_feasible"]
            and not summary["directional_conflict"]
            and summary["em_guard_pass"]
        )
        summaries[config_id] = summary
        if summary["selection_eligible"]:
            eligible.append(summary)
    if not eligible:
        raise RuntimeError("independent development found no eligible config")
    best = max(row["dataset_equal_weight_delta_answer_f1"] for row in eligible)
    near = [
        row
        for row in eligible
        if row["dataset_equal_weight_delta_answer_f1"] >= best - 0.002
    ]
    selected = min(
        near,
        key=lambda row: (
            row["mean_incremental_input_tokens"],
            row["config"]["insert_budget"],
            -row["config"]["leaf_size"],
            0 if row["config"]["facet_gate"] == "STRICT" else 1,
            -float(row["config"]["unit_score_percentile"]),
            row["config"]["config_id"],
        ),
    )
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
        "near_tie_config_ids": [row["config"]["config_id"] for row in near],
        "schema_version": SCHEMA_VERSION,
        "selected_config_id": selected["config"]["config_id"],
        "status": "STAGE5A_DEVELOPMENT_EVALUATION_COMPLETE",
    }
    manifest = {
        "development_summary_status": summary["status"],
        "selection_reconstruction": {
            "best_equal_weight_f1": best,
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
        "selected_config": selected["config"],
        "status": "STAGE5A_DEVELOPMENT_UNIQUE_CONFIGURATION_FROZEN",
    }
    return summary, manifest


def _paragraphs(unit_ids: list[str]) -> set[int]:
    result: set[int] = set()
    for unit_id in unit_ids:
        match = re.search(r"::p([0-9]+)::s[0-9]+$", unit_id)
        if not isinstance(unit_id, str) or match is None:
            raise ValueError("independent unit identity differs")
        result.add(int(match.group(1)))
    return result


def _gold_units(gold: dict[str, Any], unit_ids: list[str]) -> set[str]:
    if gold["dataset"] == HOTPOT_DATASET:
        targets = set(gold["supporting_unit_ids"])
        return {unit_id for unit_id in unit_ids if unit_id in targets}
    targets = set(gold["supporting_paragraph_indices"])
    return {
        unit_id
        for unit_id in unit_ids
        if next(iter(_paragraphs([unit_id]))) in targets
    }


def independent_confirmation_audit(
    gold_rows: list[dict[str, Any]],
    prediction_rows: list[dict[str, Any]],
    prompt_rows: list[dict[str, Any]],
    ranking_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    audits = independent_answer_audit(
        gold_rows,
        prediction_rows,
        prompt_rows,
        ranking_rows,
        CONFIRMATION_METHODS,
    )
    gold_map = {row["query_id"]: row for row in gold_rows}
    ranking_map = _rankings(ranking_rows)
    for audit in audits:
        gold = gold_map[audit["query_id"]]
        ranking_row = ranking_map[audit["query_id"]]
        for method in CONFIRMATION_METHODS:
            ranking = ranking_row["methods"][method]
            if gold["dataset"] == HOTPOT_DATASET:
                targets = set(gold["supporting_unit_ids"])
                retrieved = set(ranking)
            else:
                targets = set(gold["supporting_paragraph_indices"])
                retrieved = _paragraphs(ranking)
            overlap = len(targets & retrieved)
            audit["methods"][method].update(
                {
                    "retrieval_cr20": float(overlap == len(targets)),
                    "retrieval_er20": overlap / len(targets),
                }
            )
        baseline = ranking_row["methods"][BASELINE_METHOD]
        transitions: dict[str, Any] = {}
        for method in CONFIRMATION_METHODS[1:]:
            method_ids = ranking_row["methods"][method]
            added = [unit_id for unit_id in method_ids if unit_id not in baseline]
            displaced = [unit_id for unit_id in baseline if unit_id not in method_ids]
            added_gold_units = _gold_units(gold, added)
            displaced_gold_units = _gold_units(gold, displaced)
            if gold["dataset"] == HOTPOT_DATASET:
                targets = set(gold["supporting_unit_ids"])
                baseline_gold = set(baseline) & targets
                method_gold = set(method_ids) & targets
            else:
                targets = set(gold["supporting_paragraph_indices"])
                baseline_gold = _paragraphs(baseline) & targets
                method_gold = _paragraphs(method_ids) & targets
            added_gold = len(method_gold - baseline_gold)
            displaced_gold = len(baseline_gold - method_gold)
            answer_delta = (
                audit["methods"][method]["answer_f1"]
                - audit["methods"][BASELINE_METHOD]["answer_f1"]
            )
            transitions[method] = {
                "added_gold_evidence": added_gold,
                "added_gold_unit_count": len(added_gold_units),
                "added_non_gold_units": len(added) - len(added_gold_units),
                "added_unit_count": len(added),
                "answer_change": (
                    "GAIN"
                    if answer_delta > 0
                    else "HARM"
                    if answer_delta < 0
                    else "SAME"
                ),
                "displaced_bge_gold_evidence": displaced_gold,
                "displaced_gold_unit_count": len(displaced_gold_units),
                "displaced_non_gold_units": len(displaced) - len(displaced_gold_units),
                "displaced_unit_count": len(displaced),
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


def _paired(
    arrays: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    seed: int,
) -> dict[str, Any]:
    left_f1, right_f1, left_em, right_em = arrays
    f1_delta = left_f1 - right_f1
    em_delta = left_em - right_em
    rng = np.random.default_rng(seed)
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


def _equal_weight(
    values: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
    seed: int,
) -> dict[str, Any]:
    deltas = {
        dataset: (
            values[dataset][0] - values[dataset][1],
            values[dataset][2] - values[dataset][3],
        )
        for dataset in DATASETS
    }
    rng = np.random.default_rng(seed)
    f1_samples = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    em_samples = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    for index in range(BOOTSTRAP_ITERATIONS):
        f1_values: list[float] = []
        em_values: list[float] = []
        for dataset in DATASETS:
            f1_delta, em_delta = deltas[dataset]
            sample = rng.integers(0, len(f1_delta), len(f1_delta))
            f1_values.append(float(np.mean(f1_delta[sample])))
            em_values.append(float(np.mean(em_delta[sample])))
        f1_samples[index] = float(np.mean(f1_values))
        em_samples[index] = float(np.mean(em_values))
    f1 = _interval(
        float(np.mean([np.mean(deltas[d][0]) for d in DATASETS])),
        f1_samples,
    )
    em = _interval(
        float(np.mean([np.mean(deltas[d][1]) for d in DATASETS])),
        em_samples,
    )
    f1["one_sided_positive_p"] = float(
        (1 + np.count_nonzero(f1_samples <= 0.0))
        / (BOOTSTRAP_ITERATIONS + 1)
    )
    return {"delta_answer_em": em, "delta_answer_f1": f1}


def _comparison(
    by_dataset: dict[str, list[dict[str, Any]]],
    left: str,
    right: str,
    offset: int,
) -> dict[str, Any]:
    inputs: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
    datasets: dict[str, Any] = {}
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
        datasets[dataset] = _paired(
            arrays, BOOTSTRAP_SEED + offset * 100 + dataset_index
        )
    return {
        "contrast": f"{left} - {right}",
        "dataset_equal_weight": _equal_weight(
            inputs, BOOTSTRAP_SEED + 1000 + offset
        ),
        "datasets": datasets,
    }


def _core(summary: dict[str, Any]) -> str:
    pooled = summary["dataset_equal_weight"]
    f1 = pooled["delta_answer_f1"]
    em = pooled["delta_answer_em"]
    points = [
        summary["datasets"][dataset]["delta_answer_f1"]["point"]
        for dataset in DATASETS
    ]
    uppers = [
        summary["datasets"][dataset]["delta_answer_f1"]["ci95_upper"]
        for dataset in DATASETS
    ]
    if f1["ci95_upper"] < 0.0 or em["ci95_upper"] < -0.010:
        return "BGE_NATIVE_HGRAG_NEGATIVE"
    if points[0] * points[1] < 0.0 or any(value < 0.0 for value in uppers):
        return "BGE_NATIVE_HGRAG_CROSS_DATASET_HETEROGENEOUS"
    supported = (
        f1["ci95_lower"] > 0.0
        and all(value > 0.0 for value in points)
        and em["ci95_lower"] >= -0.010
    )
    if supported and f1["point"] >= 0.010:
        return "BGE_NATIVE_HGRAG_SUPPORTED"
    if supported and 0.0 < f1["point"] < 0.010:
        return "BGE_NATIVE_HGRAG_SUPPORTED_SMALL_EFFECT"
    return "BGE_NATIVE_HGRAG_INCONCLUSIVE"


def _support(summary: dict[str, Any], prefix: str) -> str:
    f1 = summary["dataset_equal_weight"]["delta_answer_f1"]
    em = summary["dataset_equal_weight"]["delta_answer_em"]
    if f1["ci95_lower"] > 0.0 and em["ci95_lower"] >= -0.010:
        return f"{prefix}_SUPPORTED"
    if f1["ci95_upper"] < 0.0 or em["ci95_upper"] < -0.010:
        return f"{prefix}_NEGATIVE"
    return f"{prefix}_INCONCLUSIVE"


def independent_confirmation_outputs(
    audits: list[dict[str, Any]], telemetry: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    by_dataset = {
        dataset: [row for row in audits if row["dataset"] == dataset]
        for dataset in DATASETS
    }
    metrics = (
        "answer_em", "answer_f1", "evidence_count", "input_token_count",
        "retrieval_cr20", "retrieval_er20", "unknown",
    )
    dataset_summary = {
        dataset: {
            "methods": {
                method: {
                    metric: float(
                        np.mean([row["methods"][method][metric] for row in rows])
                    )
                    for metric in metrics
                }
                for method in CONFIRMATION_METHODS
            },
            "query_count": len(rows),
        }
        for dataset, rows in by_dataset.items()
    }
    comparisons = {
        "protected_minus_bge": _comparison(
            by_dataset, PROTECTED, BASELINE_METHOD, 0
        ),
        "protected_minus_unprotected": _comparison(
            by_dataset, PROTECTED, UNPROTECTED, 1
        ),
        "protected_minus_no_facet": _comparison(
            by_dataset, PROTECTED, NO_FACET, 2
        ),
        "unprotected_minus_bge": _comparison(
            by_dataset, UNPROTECTED, BASELINE_METHOD, 3
        ),
    }
    equal_weight = {
        "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "comparisons": comparisons,
        "dataset_weights": {dataset: 0.5 for dataset in DATASETS},
        "primary_comparison": "protected_minus_bge",
        "status": "STAGE5A_CONFIRMATION_STATISTICS_COMPLETE_PENDING_VERIFICATION",
    }
    decision = {
        "core_state": _core(comparisons["protected_minus_bge"]),
        "facet_state": _support(
            comparisons["protected_minus_no_facet"],
            "BGE_NATIVE_FACET_INCREMENT",
        ),
        "interpretation_boundary": (
            "One frozen BGE-large-en-v1.5 backbone on closed-candidate Top-20 "
            "HotpotQA/MuSiQue confirmation IDs; no universal strong-retriever "
            "or full-wiki claim."
        ),
        "placement_state": _support(
            comparisons["protected_minus_unprotected"],
            "BGE_NATIVE_PROTECTED_PLACEMENT",
        ),
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE5A_SCIENTIFIC_DECISION_FROZEN_PENDING_FINAL_VERIFICATION",
    }
    core_f1 = comparisons["protected_minus_bge"]["dataset_equal_weight"][
        "delta_answer_f1"
    ]["point"]
    generation_seconds = telemetry.get("generation_seconds_by_method", {})
    incremental_seconds = float(
        generation_seconds.get(PROTECTED, 0.0)
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
    mechanism_datasets: dict[str, Any] = {}
    for dataset in DATASETS:
        rows = by_dataset[dataset]
        mechanism_datasets[dataset] = {}
        for method in CONFIRMATION_METHODS[1:]:
            transitions = [
                row["transitions_relative_to_bge"][method] for row in rows
            ]
            cross_tab: Counter[str] = Counter()
            for row in transitions:
                net = row["net_gold_evidence_change"]
                label = "POSITIVE" if net > 0 else "NEGATIVE" if net < 0 else "ZERO"
                cross_tab[f"{row['answer_change']}|{label}"] += 1
            mechanism_datasets[dataset][method] = {
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
    mechanism = {
        "datasets": mechanism_datasets,
        "interpretation": "POST_DECISION_DESCRIPTIVE_ONLY_NO_RETUNING_OR_ADVANCEMENT",
        "status": "STAGE5A_POST_GOLD_MECHANISM_AUDIT_COMPLETE",
    }
    return dataset_summary, equal_weight, decision, efficiency, mechanism
