"""Gold-only evaluation and frozen decisions for Stage4I-SDC."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from stage4h_cbe_evaluate import answer_scores
from stage4i_sdc_common import (
    BOOTSTRAP_ITERATIONS,
    BOOTSTRAP_SEED,
    CORE_LEFT,
    CORE_RIGHT,
    DATASETS,
    HOTPOT_DATASET,
    METHODS,
    SCHEMA_VERSION,
    assert_bound,
    load_json,
    load_jsonl,
    path_from_config,
    render_json,
    render_jsonl,
    require_json_int,
    require_native_string,
    validate_authorization,
    write_new_files_atomically,
)


COMPARISONS = {
    "protected_minus_bge": (CORE_LEFT, CORE_RIGHT),
    "protected_minus_unprotected": (
        CORE_LEFT,
        "BGE_HGRAG_UNPROTECTED_TOP20",
    ),
    "unprotected_minus_bge": ("BGE_HGRAG_UNPROTECTED_TOP20", CORE_RIGHT),
    "protected_minus_no_facet": (
        CORE_LEFT,
        "BGE_HGRAG_NO_FACET_TOP20",
    ),
}


def _pair_map(rows: list[dict[str, Any]], label: str) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"{label}[{index}] must be an object")
        query_id = require_native_string(row.get("query_id"), f"{label}.query_id")
        method = require_native_string(row.get("method"), f"{label}.method")
        if method not in METHODS:
            raise ValueError(f"{label}[{index}].method differs")
        key = (query_id, method)
        if key in result:
            raise ValueError(f"{label}: duplicate pair {key}")
        result[key] = row
    return result


def _ranking_map(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        query_id = require_native_string(row.get("query_id"), f"rankings[{index}]")
        if query_id in result or set(row.get("methods", {})) != set(METHODS):
            raise ValueError("ranking identity/method contract differs")
        result[query_id] = row
    return result


def _gold_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    for index, row in enumerate(rows):
        query_id = require_native_string(row.get("query_id"), f"gold[{index}].query_id")
        dataset = require_native_string(row.get("dataset"), f"gold[{index}].dataset")
        if query_id in seen or dataset not in DATASETS:
            raise ValueError("Gold identity differs")
        seen.add(query_id)
        answers = row.get("answers")
        if (
            not isinstance(answers, list)
            or not answers
            or any(not isinstance(value, str) or not value.strip() for value in answers)
        ):
            raise ValueError(f"gold[{index}].answers differ")
        if dataset == HOTPOT_DATASET:
            supports = row.get("supporting_unit_ids")
            if (
                row.get("evidence_granularity") != "official_supporting_sentence"
                or not isinstance(supports, list)
                or not supports
                or any(not isinstance(value, str) or not value for value in supports)
            ):
                raise ValueError(f"gold[{index}] Hotpot support contract differs")
        else:
            supports = row.get("supporting_paragraph_indices")
            if (
                row.get("evidence_granularity") != "official_supporting_paragraph"
                or not isinstance(supports, list)
                or not supports
                or any(
                    isinstance(value, bool) or not isinstance(value, int) or value < 0
                    for value in supports
                )
            ):
                raise ValueError(f"gold[{index}] MuSiQue support contract differs")
    return rows


def _paragraph_indices(unit_ids: list[str]) -> set[int]:
    values: set[int] = set()
    for unit_id in unit_ids:
        match = re.search(r"::p([0-9]+)::s[0-9]+$", unit_id)
        if match is None:
            raise ValueError(f"cannot parse paragraph from unit_id: {unit_id}")
        values.add(int(match.group(1)))
    return values


def _gold_unit_membership(gold: dict[str, Any], unit_ids: list[str]) -> set[str]:
    if gold["dataset"] == HOTPOT_DATASET:
        targets = set(gold["supporting_unit_ids"])
        return {unit_id for unit_id in unit_ids if unit_id in targets}
    target_paragraphs = set(gold["supporting_paragraph_indices"])
    return {
        unit_id
        for unit_id in unit_ids
        if next(iter(_paragraph_indices([unit_id]))) in target_paragraphs
    }


def evaluate_queries(
    gold_rows: list[dict[str, Any]],
    prediction_rows: list[dict[str, Any]],
    prompt_rows: list[dict[str, Any]],
    ranking_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    predictions = _pair_map(prediction_rows, "predictions")
    prompts = _pair_map(prompt_rows, "prompts")
    rankings = _ranking_map(ranking_rows)
    expected_pairs = {
        (row["query_id"], method) for row in gold_rows for method in METHODS
    }
    if set(predictions) != expected_pairs or set(prompts) != expected_pairs:
        raise ValueError("prediction/prompt pair coverage differs")
    if set(rankings) != {row["query_id"] for row in gold_rows}:
        raise ValueError("ranking query coverage differs")
    audits: list[dict[str, Any]] = []
    for gold in gold_rows:
        query_id = gold["query_id"]
        ranking_row = rankings[query_id]
        methods: dict[str, Any] = {}
        for method in METHODS:
            prediction = predictions[(query_id, method)]
            prompt = prompts[(query_id, method)]
            ranking = ranking_row["methods"][method]
            if prompt.get("evidence_unit_ids") != ranking[: len(prompt.get("evidence_unit_ids", []))]:
                raise ValueError(f"{query_id}/{method}: prompt is not a ranking prefix")
            em, f1 = answer_scores(prediction["prediction"], gold["answers"])
            if gold["dataset"] == HOTPOT_DATASET:
                targets = set(gold["supporting_unit_ids"])
                retrieved = set(ranking)
            else:
                targets = set(gold["supporting_paragraph_indices"])
                retrieved = _paragraph_indices(ranking)
            overlap = len(targets & retrieved)
            methods[method] = {
                "answer_em": em,
                "answer_f1": f1,
                "evidence_count": len(prompt["evidence_unit_ids"]),
                "input_token_count": require_json_int(
                    prompt["input_token_count"], "input_token_count"
                ),
                "retrieval_cr20": float(overlap == len(targets)),
                "retrieval_er20": overlap / len(targets),
                "unknown": float(
                    prediction["prediction"].strip().upper() == "UNKNOWN"
                ),
            }
        bge_ids = ranking_row["methods"][CORE_RIGHT]
        transitions: dict[str, Any] = {}
        for method in METHODS:
            if method == CORE_RIGHT:
                continue
            method_ids = ranking_row["methods"][method]
            added_units = [unit_id for unit_id in method_ids if unit_id not in bge_ids]
            displaced_units = [unit_id for unit_id in bge_ids if unit_id not in method_ids]
            added_gold_units = _gold_unit_membership(gold, added_units)
            displaced_gold_units = _gold_unit_membership(gold, displaced_units)
            if gold["dataset"] == HOTPOT_DATASET:
                bge_gold = set(bge_ids) & set(gold["supporting_unit_ids"])
                method_gold = set(method_ids) & set(gold["supporting_unit_ids"])
            else:
                target_paragraphs = set(gold["supporting_paragraph_indices"])
                bge_gold = _paragraph_indices(bge_ids) & target_paragraphs
                method_gold = _paragraph_indices(method_ids) & target_paragraphs
            added_gold = len(method_gold - bge_gold)
            displaced_gold = len(bge_gold - method_gold)
            answer_delta = (
                methods[method]["answer_f1"] - methods[CORE_RIGHT]["answer_f1"]
            )
            transitions[method] = {
                "added_gold_evidence": added_gold,
                "added_gold_unit_count": len(added_gold_units),
                "added_non_gold_units": len(added_units) - len(added_gold_units),
                "added_unit_count": len(added_units),
                "answer_change": (
                    "GAIN" if answer_delta > 0 else "HARM" if answer_delta < 0 else "SAME"
                ),
                "displaced_bge_gold_evidence": displaced_gold,
                "displaced_gold_unit_count": len(displaced_gold_units),
                "displaced_non_gold_units": (
                    len(displaced_units) - len(displaced_gold_units)
                ),
                "displaced_unit_count": len(displaced_units),
                "net_gold_evidence_change": added_gold - displaced_gold,
            }
        audits.append(
            {
                "dataset": gold["dataset"],
                "methods": methods,
                "query_id": query_id,
                "sample_id": gold["sample_id"],
                "transitions_relative_to_bge": transitions,
            }
        )
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
        (1 + np.count_nonzero(f1_samples <= 0.0)) / (BOOTSTRAP_ITERATIONS + 1)
    )
    return {"delta_answer_em": em, "delta_answer_f1": f1}


def equal_weight_bootstrap(
    values: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
    seed: int,
) -> dict[str, Any]:
    if set(values) != set(DATASETS):
        raise ValueError("equal-weight bootstrap datasets differ")
    rng = np.random.default_rng(seed)
    deltas: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for dataset in DATASETS:
        left_f1, right_f1, left_em, right_em = values[dataset]
        deltas[dataset] = left_f1 - right_f1, left_em - right_em
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
        (1 + np.count_nonzero(f1_samples <= 0.0)) / (BOOTSTRAP_ITERATIONS + 1)
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
                [row["methods"][method][metric] for row in rows], dtype="float64"
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
        return "STRONG_DENSE_COMPLEMENTARITY_NEGATIVE"
    if (
        dataset_points[0] * dataset_points[1] < 0.0
        or any(value < 0.0 for value in dataset_uppers)
    ):
        return "STRONG_DENSE_COMPLEMENTARITY_CROSS_DATASET_HETEROGENEOUS"
    common_support = (
        f1["ci95_lower"] > 0.0
        and all(value > 0.0 for value in dataset_points)
        and em["ci95_lower"] >= -0.010
    )
    if common_support and f1["point"] >= 0.010:
        return "STRONG_DENSE_COMPLEMENTARITY_SUPPORTED"
    if common_support and 0.0 < f1["point"] < 0.010:
        return "STRONG_DENSE_COMPLEMENTARITY_SUPPORTED_SMALL_EFFECT"
    return "STRONG_DENSE_COMPLEMENTARITY_INCONCLUSIVE"


def supportive_state(summary: dict[str, Any], prefix: str) -> str:
    pooled = summary["dataset_equal_weight"]
    f1 = pooled["delta_answer_f1"]
    em = pooled["delta_answer_em"]
    if f1["ci95_lower"] > 0.0 and em["ci95_lower"] >= -0.010:
        return f"{prefix}_SUPPORTED"
    if f1["ci95_upper"] < 0.0 or em["ci95_upper"] < -0.010:
        return f"{prefix}_NEGATIVE"
    return f"{prefix}_INCONCLUSIVE"


def summarize(
    audits: list[dict[str, Any]], telemetry: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    by_dataset = {
        dataset: [row for row in audits if row["dataset"] == dataset]
        for dataset in DATASETS
    }
    dataset_summaries: dict[str, Any] = {}
    for dataset, rows in by_dataset.items():
        methods = {
            method: {
                metric: float(np.mean([row["methods"][method][metric] for row in rows]))
                for metric in (
                    "answer_em",
                    "answer_f1",
                    "evidence_count",
                    "input_token_count",
                    "retrieval_cr20",
                    "retrieval_er20",
                    "unknown",
                )
            }
            for method in METHODS
        }
        gain_same_harm: dict[str, Any] = {}
        for method in METHODS:
            if method == CORE_RIGHT:
                continue
            values = [
                row["methods"][method]["answer_f1"]
                - row["methods"][CORE_RIGHT]["answer_f1"]
                for row in rows
            ]
            gain_same_harm[method] = {
                "gain_queries": sum(value > 0 for value in values),
                "harm_queries": sum(value < 0 for value in values),
                "same_queries": sum(value == 0 for value in values),
            }
        dataset_summaries[dataset] = {
            "gain_same_harm_relative_to_bge": gain_same_harm,
            "methods": methods,
            "query_count": len(rows),
        }
    comparisons = {
        label: _comparison(by_dataset, left, right, index)
        for index, (label, (left, right)) in enumerate(COMPARISONS.items())
    }
    core = comparisons["protected_minus_bge"]
    decision_status = core_decision(core)
    placement_state = supportive_state(
        comparisons["protected_minus_unprotected"], "PROTECTED_PLACEMENT"
    )
    facet_state = supportive_state(
        comparisons["protected_minus_no_facet"], "BGE_FACET_INCREMENT"
    )
    equal_weight = {
        "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "comparisons": comparisons,
        "dataset_weights": {dataset: 0.5 for dataset in DATASETS},
        "primary_comparison": "protected_minus_bge",
        "status": "STAGE4I_STATISTICS_COMPLETE_PENDING_VERIFICATION",
    }
    placement = {
        "comparisons": {
            key: comparisons[key]
            for key in (
                "protected_minus_bge",
                "unprotected_minus_bge",
                "protected_minus_unprotected",
            )
        },
        "interpretation": "SUPPORTING_NO_CORE_ADVANCEMENT",
        "state": placement_state,
        "status": "STAGE4I_PLACEMENT_ANALYSIS_COMPLETE",
    }
    facet = {
        "comparison": comparisons["protected_minus_no_facet"],
        "interpretation": "SUPPORTING_NO_CORE_ADVANCEMENT",
        "state": facet_state,
        "status": "STAGE4I_FACET_ANALYSIS_COMPLETE",
    }
    decision = {
        "core_state": decision_status,
        "facet_state": facet_state,
        "interpretation_boundary": (
            "One pre-specified BGE large-en-v1.5 backbone on new closed-candidate "
            "HotpotQA/MuSiQue IDs; no universal strong-retriever or full-wiki claim."
        ),
        "placement_state": placement_state,
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4I_SCIENTIFIC_DECISION_FROZEN_PENDING_FINAL_VERIFICATION",
    }
    dataset_summaries["_resource"] = {
        "embedding_cache": telemetry.get("embedding_cache"),
        "generation_seconds_by_method": telemetry.get("generation_seconds_by_method"),
        "gpu_peak_memory_bytes": telemetry.get("gpu_peak_memory_bytes"),
        "retrieval_seconds": telemetry.get("retrieval_seconds"),
    }
    return dataset_summaries, equal_weight, placement, facet, decision


def evidence_transition_summary(audits: list[dict[str, Any]]) -> dict[str, Any]:
    methods = [method for method in METHODS if method != CORE_RIGHT]
    output: dict[str, Any] = {}
    for dataset in DATASETS:
        rows = [row for row in audits if row["dataset"] == dataset]
        output[dataset] = {}
        for method in methods:
            transitions = [
                row["transitions_relative_to_bge"][method] for row in rows
            ]
            cross_tab: Counter[str] = Counter()
            for row in transitions:
                net = row["net_gold_evidence_change"]
                net_label = "POSITIVE" if net > 0 else "NEGATIVE" if net < 0 else "ZERO"
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
        "status": "STAGE4I_POST_GOLD_EVIDENCE_TRANSITION_AUDIT_COMPLETE",
    }


def run(config: dict[str, Any]) -> None:
    validate_authorization(config)
    pregold = load_json(assert_bound(config, "verified_pregold"))
    if (
        not isinstance(pregold, dict)
        or pregold.get("status") != "STAGE4I_PRE_GOLD_VERIFICATION_PASS"
    ):
        raise PermissionError("Stage4I pre-Gold verification has not passed")
    gold = _gold_rows(load_jsonl(assert_bound(config, "gold")))
    predictions = load_jsonl(assert_bound(config, "predictions_main"))
    prompts = load_jsonl(assert_bound(config, "prompt_audit_main"))
    rankings = load_jsonl(assert_bound(config, "rankings"))
    telemetry = load_json(assert_bound(config, "telemetry_main"))
    if not isinstance(telemetry, dict):
        raise ValueError("Stage4I telemetry differs")
    audits = evaluate_queries(gold, predictions, prompts, rankings)
    dataset, equal_weight, placement, facet, decision = summarize(audits, telemetry)
    evidence = evidence_transition_summary(audits)
    write_new_files_atomically(
        (
            (path_from_config(config, "query_audit"), render_jsonl(audits)),
            (path_from_config(config, "dataset_summaries"), render_json(dataset)),
            (
                path_from_config(config, "equal_weight_summary"),
                render_json(equal_weight),
            ),
            (path_from_config(config, "placement_summary"), render_json(placement)),
            (path_from_config(config, "facet_summary"), render_json(facet)),
            (
                path_from_config(config, "evidence_transition_audit"),
                render_json(evidence),
            ),
            (
                path_from_config(config, "scientific_decision"),
                render_json(decision),
            ),
        )
    )
    print(
        "STAGE4I_GOLD_EVALUATION_COMPLETE_PENDING_FINAL_VERIFICATION "
        f"queries={len(audits)} core={decision['core_state']} "
        f"placement={decision['placement_state']} facet={decision['facet_state']}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage4I config must be an object")
    run(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE4I_EVALUATION_FAIL: {exc}", file=sys.stderr)
        raise
