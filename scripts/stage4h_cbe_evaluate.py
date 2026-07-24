"""Gold-only Stage4H answer/evidence evaluation and frozen statistics."""

from __future__ import annotations

import argparse
import math
import re
import string
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from stage4h_cbe_common import (
    BOOTSTRAP_ITERATIONS,
    BOOTSTRAP_SEED,
    DATASETS,
    HOTPOT_DATASET,
    METHODS,
    MUSIQUE_DATASET,
    PRIMARY_COMPARATORS,
    SCHEMA_VERSION,
    assert_file_identity,
    file_identity,
    load_json,
    load_jsonl,
    path_from_config,
    render_json,
    render_jsonl,
    require_finite_number,
    require_json_bool,
    require_json_int,
    require_native_string,
    write_new_files_atomically,
)


PREDICTION_KEYS = {"dataset", "method", "prediction", "query_id", "sample_id"}
PROMPT_KEYS = {
    "dataset",
    "evidence_unit_ids",
    "input_token_count",
    "method",
    "prompt_sha256",
    "query_id",
    "rank1_truncated",
    "sample_id",
}


def normalize_answer(value: str) -> str:
    value = value.lower()
    value = "".join(character for character in value if character not in string.punctuation)
    value = re.sub(r"\b(a|an|the)\b", " ", value)
    return " ".join(value.split())


def answer_scores(prediction: str, answers: list[str]) -> tuple[float, float]:
    prediction = require_native_string(prediction, "prediction")
    if not answers:
        raise ValueError("answers must be non-empty")
    normalized_prediction = normalize_answer(prediction)
    best_em = 0.0
    best_f1 = 0.0
    for answer in answers:
        normalized_answer = normalize_answer(require_native_string(answer, "answer"))
        em = float(normalized_prediction == normalized_answer)
        prediction_tokens = normalized_prediction.split()
        answer_tokens = normalized_answer.split()
        if not prediction_tokens or not answer_tokens:
            f1 = float(prediction_tokens == answer_tokens)
        else:
            common = Counter(prediction_tokens) & Counter(answer_tokens)
            overlap = sum(common.values())
            if overlap == 0:
                f1 = 0.0
            else:
                precision = overlap / len(prediction_tokens)
                recall = overlap / len(answer_tokens)
                f1 = 2.0 * precision * recall / (precision + recall)
        best_em = max(best_em, em)
        best_f1 = max(best_f1, f1)
    return best_em, best_f1


def _assert_bound(config: dict[str, Any], key: str) -> Path:
    path = path_from_config(config, key)
    binding = config.get("inputs", {}).get(key)
    if not isinstance(binding, dict):
        raise ValueError(f"inputs.{key} binding is missing")
    assert_file_identity(path, binding, f"inputs.{key}")
    return path


def _validate_authorization(config: dict[str, Any]) -> None:
    if config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Stage4H config schema differs")
    authorization = config.get("official_execution")
    if not isinstance(authorization, dict) or require_json_bool(
        authorization.get("authorized"), "official_execution.authorized"
    ) is not True:
        raise PermissionError("STAGE4H_GOLD_NOT_AUTHORIZED")
    verified = load_json(_assert_bound(config, "verified_pregold"))
    if (
        not isinstance(verified, dict)
        or verified.get("status") != "STAGE4H_PRE_GOLD_VERIFICATION_PASS"
    ):
        raise PermissionError("STAGE4H_PRE_GOLD_VERIFICATION_REQUIRED")


def _prediction_map(
    rows: list[dict[str, Any]],
    label: str,
) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if set(row) != PREDICTION_KEYS:
            raise ValueError(f"{label}[{index}] key contract differs")
        dataset = require_native_string(row["dataset"], f"{label}.dataset")
        method = require_native_string(row["method"], f"{label}.method")
        query_id = require_native_string(row["query_id"], f"{label}.query_id")
        sample_id = require_native_string(row["sample_id"], f"{label}.sample_id")
        require_native_string(row["prediction"], f"{label}.prediction")
        if dataset not in DATASETS or method not in METHODS:
            raise ValueError(f"{label}[{index}] dataset/method differs")
        if query_id != f"{dataset}::{sample_id}":
            raise ValueError(f"{label}[{index}] identity differs")
        key = (query_id, method)
        if key in result:
            raise ValueError(f"{label}: duplicate pair {key}")
        result[key] = row
    return result


def _prompt_map(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if set(row) != PROMPT_KEYS:
            raise ValueError(f"prompt[{index}] key contract differs")
        dataset = require_native_string(row["dataset"], "prompt.dataset")
        method = require_native_string(row["method"], "prompt.method")
        query_id = require_native_string(row["query_id"], "prompt.query_id")
        sample_id = require_native_string(row["sample_id"], "prompt.sample_id")
        if (
            dataset not in DATASETS
            or method not in METHODS
            or query_id != f"{dataset}::{sample_id}"
        ):
            raise ValueError(f"prompt[{index}] identity differs")
        ids = row["evidence_unit_ids"]
        if not isinstance(ids, list) or any(
            not isinstance(value, str) or not value for value in ids
        ):
            raise ValueError(f"prompt[{index}].evidence_unit_ids differs")
        count = require_json_int(row["input_token_count"], "input_token_count")
        if count <= 0 or count > 4096:
            raise ValueError(f"prompt[{index}] token count differs")
        if not isinstance(row["rank1_truncated"], bool):
            raise ValueError(f"prompt[{index}].rank1_truncated differs")
        key = (query_id, method)
        if key in result:
            raise ValueError(f"prompt duplicate pair {key}")
        result[key] = row
    return result


def _ranking_map(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        required = {
            "dataset",
            "effective_k",
            "full_inserted_unit_ids",
            "methods",
            "no_facet_inserted_unit_ids",
            "query_id",
            "sample_id",
        }
        if set(row) != required:
            raise ValueError(f"ranking[{index}] key contract differs")
        query_id = require_native_string(row["query_id"], "ranking.query_id")
        if query_id in result:
            raise ValueError(f"ranking duplicate query: {query_id}")
        methods = row["methods"]
        if not isinstance(methods, dict) or set(methods) != set(METHODS):
            raise ValueError(f"ranking[{index}] method contract differs")
        effective_k = require_json_int(row["effective_k"], "effective_k")
        for method, values in methods.items():
            if (
                not isinstance(values, list)
                or len(values) != effective_k
                or len(values) != len(set(values))
                or any(not isinstance(value, str) or not value for value in values)
            ):
                raise ValueError(f"ranking[{index}].{method} differs")
        result[query_id] = row
    return result


def _gold_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    for index, row in enumerate(rows):
        dataset = require_native_string(row.get("dataset"), f"gold[{index}].dataset")
        query_id = require_native_string(row.get("query_id"), f"gold[{index}].query_id")
        sample_id = require_native_string(row.get("sample_id"), f"gold[{index}].sample_id")
        if dataset not in DATASETS or query_id != f"{dataset}::{sample_id}" or query_id in seen:
            raise ValueError(f"gold[{index}] identity differs")
        seen.add(query_id)
        answers = row.get("answers")
        if not isinstance(answers, list) or not answers or any(
            not isinstance(value, str) or not value.strip() for value in answers
        ):
            raise ValueError(f"gold[{index}].answers differs")
        if dataset == HOTPOT_DATASET:
            if set(row) != {
                "answers",
                "dataset",
                "evidence_granularity",
                "query_id",
                "sample_id",
                "supporting_unit_ids",
            } or row["evidence_granularity"] != "official_supporting_sentence":
                raise ValueError(f"gold[{index}] Hotpot contract differs")
            values = row["supporting_unit_ids"]
            if (
                not isinstance(values, list)
                or not values
                or len(values) != len(set(values))
                or any(not isinstance(value, str) or not value for value in values)
            ):
                raise ValueError(f"gold[{index}] Hotpot support values differ")
        else:
            if set(row) != {
                "answers",
                "dataset",
                "evidence_granularity",
                "query_id",
                "sample_id",
                "supporting_paragraph_indices",
            } or row["evidence_granularity"] != "official_supporting_paragraph":
                raise ValueError(f"gold[{index}] MuSiQue contract differs")
            values = row["supporting_paragraph_indices"]
            if (
                not isinstance(values, list)
                or not values
                or len(values) != len(set(values))
                or any(
                    isinstance(value, bool)
                    or not isinstance(value, int)
                    or value < 0
                    for value in values
                )
            ):
                raise ValueError(f"gold[{index}] MuSiQue support values differ")
    return rows


def _paragraph_indices(unit_ids: list[str]) -> set[int]:
    result: set[int] = set()
    for unit_id in unit_ids:
        match = re.search(r"::p([0-9]+)::s[0-9]+$", unit_id)
        if match is None:
            raise ValueError(f"MuSiQue unit ID cannot be parsed: {unit_id}")
        result.add(int(match.group(1)))
    return result


def evaluate_queries(
    gold_rows: list[dict[str, Any]],
    predictions: dict[tuple[str, str], dict[str, Any]],
    prompts: dict[tuple[str, str], dict[str, Any]],
    rankings: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    expected_pairs = {
        (row["query_id"], method) for row in gold_rows for method in METHODS
    }
    if set(predictions) != expected_pairs or set(prompts) != expected_pairs:
        raise ValueError("prediction/prompt pair coverage differs from Gold")
    if set(rankings) != {row["query_id"] for row in gold_rows}:
        raise ValueError("ranking query coverage differs from Gold")
    audits: list[dict[str, Any]] = []
    for gold in gold_rows:
        query_id = gold["query_id"]
        methods: dict[str, Any] = {}
        for method in METHODS:
            prediction = predictions[(query_id, method)]
            prompt = prompts[(query_id, method)]
            ranking = rankings[query_id]["methods"][method]
            if prompt["evidence_unit_ids"] != ranking[: len(prompt["evidence_unit_ids"])]:
                raise ValueError(f"{query_id}/{method}: prompt is not ranking prefix")
            em, f1 = answer_scores(prediction["prediction"], gold["answers"])
            if gold["dataset"] == HOTPOT_DATASET:
                targets = set(gold["supporting_unit_ids"])
                retrieved = set(ranking)
            else:
                targets = set(gold["supporting_paragraph_indices"])
                retrieved = _paragraph_indices(ranking)
            overlap = len(targets & retrieved)
            er = overlap / len(targets)
            cr = float(overlap == len(targets))
            methods[method] = {
                "answer_em": em,
                "answer_f1": f1,
                "evidence_count": len(prompt["evidence_unit_ids"]),
                "input_token_count": prompt["input_token_count"],
                "retrieval_cr20": cr,
                "retrieval_er20": er,
                "unknown": float(prediction["prediction"].strip().upper() == "UNKNOWN"),
            }
        audits.append(
            {
                "dataset": gold["dataset"],
                "methods": methods,
                "query_id": query_id,
                "sample_id": gold["sample_id"],
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
        values.ndim != 1
        or len(values) == 0
        or len(values) != len(left_f1)
        or not np.isfinite(values).all()
        for values in arrays
    ):
        raise ValueError("paired bootstrap arrays differ")
    rng = np.random.default_rng(seed)
    f1_delta = left_f1 - right_f1
    em_delta = left_em - right_em
    f1_samples = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    em_samples = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    for index in range(BOOTSTRAP_ITERATIONS):
        sample = rng.integers(0, len(f1_delta), size=len(f1_delta))
        f1_samples[index] = float(np.mean(f1_delta[sample]))
        em_samples[index] = float(np.mean(em_delta[sample]))
    f1 = _interval(float(np.mean(f1_delta)), f1_samples)
    em = _interval(float(np.mean(em_delta)), em_samples)
    f1["one_sided_positive_p"] = float(
        (1 + np.count_nonzero(f1_samples <= 0.0)) / (BOOTSTRAP_ITERATIONS + 1)
    )
    return {"delta_answer_em": em, "delta_answer_f1": f1}


def stratified_equal_weight_bootstrap(
    values: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
    seed: int,
) -> dict[str, Any]:
    if set(values) != set(DATASETS):
        raise ValueError("stratified bootstrap datasets differ")
    rng = np.random.default_rng(seed)
    f1_samples = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    em_samples = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    f1_points: list[float] = []
    em_points: list[float] = []
    deltas: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for dataset in DATASETS:
        left_f1, right_f1, left_em, right_em = values[dataset]
        if any(
            array.ndim != 1
            or len(array) == 0
            or len(array) != len(left_f1)
            or not np.isfinite(array).all()
            for array in (left_f1, right_f1, left_em, right_em)
        ):
            raise ValueError(f"{dataset}: stratified arrays differ")
        f1_delta = left_f1 - right_f1
        em_delta = left_em - right_em
        deltas[dataset] = f1_delta, em_delta
        f1_points.append(float(np.mean(f1_delta)))
        em_points.append(float(np.mean(em_delta)))
    for index in range(BOOTSTRAP_ITERATIONS):
        f1_means: list[float] = []
        em_means: list[float] = []
        for dataset in DATASETS:
            f1_delta, em_delta = deltas[dataset]
            sample = rng.integers(0, len(f1_delta), size=len(f1_delta))
            f1_means.append(float(np.mean(f1_delta[sample])))
            em_means.append(float(np.mean(em_delta[sample])))
        f1_samples[index] = float(np.mean(f1_means))
        em_samples[index] = float(np.mean(em_means))
    f1 = _interval(float(np.mean(f1_points)), f1_samples)
    em = _interval(float(np.mean(em_points)), em_samples)
    f1["one_sided_positive_p"] = float(
        (1 + np.count_nonzero(f1_samples <= 0.0)) / (BOOTSTRAP_ITERATIONS + 1)
    )
    return {"delta_answer_em": em, "delta_answer_f1": f1}


def holm_adjust(raw_p: dict[str, float]) -> dict[str, float]:
    ordered = sorted(raw_p.items(), key=lambda item: (item[1], item[0]))
    adjusted: dict[str, float] = {}
    previous = 0.0
    count = len(ordered)
    for index, (label, value) in enumerate(ordered):
        current = min(1.0, (count - index) * value)
        previous = max(previous, current)
        adjusted[label] = previous
    return adjusted


def outcome(summary: dict[str, Any], adjusted_p: float) -> str:
    f1 = summary["delta_answer_f1"]
    em = summary["delta_answer_em"]
    if (
        adjusted_p <= 0.05
        and f1["ci95_lower"] > 0.0
        and em["ci95_lower"] >= -0.01
    ):
        return "SUPPORTED"
    if f1["ci95_upper"] < 0.0 or em["ci95_upper"] < -0.01:
        return "NEGATIVE"
    return "INCONCLUSIVE"


def summarize(
    audits: list[dict[str, Any]],
    telemetry: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    by_dataset = {
        dataset: [row for row in audits if row["dataset"] == dataset]
        for dataset in DATASETS
    }
    dataset_summaries: dict[str, Any] = {}
    for dataset, rows in by_dataset.items():
        methods: dict[str, Any] = {}
        for method in METHODS:
            metrics = {
                key: float(np.mean([row["methods"][method][key] for row in rows]))
                for key in (
                    "answer_em",
                    "answer_f1",
                    "evidence_count",
                    "input_token_count",
                    "retrieval_cr20",
                    "retrieval_er20",
                    "unknown",
                )
            }
            methods[method] = metrics
        gain_same_harm: dict[str, Any] = {}
        for comparator in METHODS:
            if comparator == "STATIC_Q25_FULL":
                continue
            deltas = [
                row["methods"]["STATIC_Q25_FULL"]["answer_f1"]
                - row["methods"][comparator]["answer_f1"]
                for row in rows
            ]
            gain_same_harm[comparator] = {
                "full_gain_queries": sum(value > 0 for value in deltas),
                "full_harm_queries": sum(value < 0 for value in deltas),
                "same_queries": sum(value == 0 for value in deltas),
            }
        dataset_summaries[dataset] = {
            "gain_same_harm_relative_to_full": gain_same_harm,
            "methods": methods,
            "query_count": len(rows),
        }

    comparison_summaries: dict[str, Any] = {}
    raw_p: dict[str, float] = {}
    supporting_comparators = ("BM25_TOP20", "DENSE_BM25_HYBRID_TOP20")
    all_comparators = PRIMARY_COMPARATORS + supporting_comparators
    for comparison_index, comparator in enumerate(all_comparators):
        dataset_results: dict[str, Any] = {}
        inputs: dict[
            str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
        ] = {}
        for dataset_index, dataset in enumerate(DATASETS):
            rows = by_dataset[dataset]
            left_f1 = np.asarray(
                [row["methods"]["STATIC_Q25_FULL"]["answer_f1"] for row in rows],
                dtype="float64",
            )
            right_f1 = np.asarray(
                [row["methods"][comparator]["answer_f1"] for row in rows],
                dtype="float64",
            )
            left_em = np.asarray(
                [row["methods"]["STATIC_Q25_FULL"]["answer_em"] for row in rows],
                dtype="float64",
            )
            right_em = np.asarray(
                [row["methods"][comparator]["answer_em"] for row in rows],
                dtype="float64",
            )
            inputs[dataset] = left_f1, right_f1, left_em, right_em
            dataset_results[dataset] = paired_bootstrap(
                left_f1,
                right_f1,
                left_em,
                right_em,
                BOOTSTRAP_SEED + 100 * comparison_index + dataset_index,
            )
        pooled = stratified_equal_weight_bootstrap(
            inputs, BOOTSTRAP_SEED + 1000 + comparison_index
        )
        all_left_f1 = np.concatenate([inputs[dataset][0] for dataset in DATASETS])
        all_right_f1 = np.concatenate([inputs[dataset][1] for dataset in DATASETS])
        all_left_em = np.concatenate([inputs[dataset][2] for dataset in DATASETS])
        all_right_em = np.concatenate([inputs[dataset][3] for dataset in DATASETS])
        query_weighted = {
            "delta_answer_em_point": float(np.mean(all_left_em - all_right_em)),
            "delta_answer_f1_point": float(np.mean(all_left_f1 - all_right_f1)),
            "interpretation": "DESCRIPTIVE_ONLY",
        }
        comparison_summaries[comparator] = {
            "contrast": f"STATIC_Q25_FULL - {comparator}",
            "dataset_equal_weight": pooled,
            "datasets": dataset_results,
            "query_weighted": query_weighted,
        }
        if comparator in PRIMARY_COMPARATORS:
            raw_p[comparator] = pooled["delta_answer_f1"]["one_sided_positive_p"]
    adjusted = holm_adjust(raw_p)
    for comparator in PRIMARY_COMPARATORS:
        comparison_summaries[comparator]["dataset_equal_weight"][
            "delta_answer_f1"
        ]["holm_adjusted_p"] = adjusted[comparator]
        comparison_summaries[comparator]["outcome"] = outcome(
            comparison_summaries[comparator]["dataset_equal_weight"],
            adjusted[comparator],
        )
    for comparator in supporting_comparators:
        comparison_summaries[comparator]["outcome"] = (
            "FULL_REPORT_SUPPORTING_NO_ADVANCEMENT"
        )

    equal_weight = {
        "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "comparisons": comparison_summaries,
        "dataset_weights": {dataset: 0.5 for dataset in DATASETS},
        "holm_family": list(PRIMARY_COMPARATORS),
        "status": "STAGE4H_STATISTICS_COMPLETE_PENDING_VERIFICATION",
    }
    decisions = {
        "FACET_HYPEREDGE_ABLATION": comparison_summaries[
            "Q25_NO_FACET_HYPEREDGE"
        ]["outcome"],
        "FULL_METHOD_VS_DENSE": comparison_summaries["DENSE_TOP20"]["outcome"],
        "FULL_METHOD_VS_STRONG_DENSE": comparison_summaries[
            "STRONG_DENSE_TOP20"
        ]["outcome"],
        "GRANULAR_BALL_ABLATION": "NOT_FAIRLY_DEFINED",
        "PROTECTED_INSERTION_ABLATION": comparison_summaries[
            "Q25_NO_PROTECTION"
        ]["outcome"],
    }
    scientific_decision = {
        "decisions": decisions,
        "flat_unit_reason": (
            "No unique seed, edge-budget, radius, compactness, or boundary mapping "
            "exists from frozen granular balls to flat units."
        ),
        "interpretation_boundary": (
            "Closed-candidate HotpotQA/MuSiQue with fixed Qwen generator; no "
            "full-wiki, open-domain, reservation, Stage3B, U2, or controller inference."
        ),
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4H_SCIENTIFIC_DECISION_FROZEN_PENDING_FINAL_VERIFICATION",
    }
    dataset_summaries["_resource"] = {
        "embedding_cache": telemetry.get("embedding_cache"),
        "generation_seconds_by_method": telemetry.get(
            "generation_seconds_by_method"
        ),
        "gpu_peak_memory_bytes": telemetry.get("gpu_peak_memory_bytes"),
        "retrieval_seconds_by_method": telemetry.get(
            "retrieval_seconds_by_method"
        ),
    }
    return dataset_summaries, equal_weight, scientific_decision


def descriptive_metadata(
    metadata_rows: list[dict[str, Any]],
    audits: list[dict[str, Any]],
) -> dict[str, Any]:
    audit_by_query = {row["query_id"]: row for row in audits}
    if set(audit_by_query) != {row["query_id"] for row in metadata_rows}:
        raise ValueError("metadata/query audit identity differs")
    groups: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in metadata_rows:
        dataset = row["dataset"]
        if dataset == HOTPOT_DATASET:
            labels = (f"level={row['level']}", f"type={row['type']}")
        else:
            labels = (f"hop_count={row['hop_count']}",)
        for label in labels:
            groups[dataset][label].append(audit_by_query[row["query_id"]])
    output: dict[str, Any] = {}
    for dataset, dataset_groups in groups.items():
        output[dataset] = {}
        for label, rows in sorted(dataset_groups.items()):
            output[dataset][label] = {
                "count": len(rows),
                "method_answer_f1": {
                    method: float(
                        np.mean([row["methods"][method]["answer_f1"] for row in rows])
                    )
                    for method in METHODS
                },
            }
    return {
        "groups": output,
        "interpretation": "POST_DECISION_DESCRIPTIVE_ONLY_NO_SUBGROUP_CONFIRMATION",
        "status": "STAGE4H_CHANNEL_C_DESCRIPTIVE_COMPLETE",
    }


def run(config: dict[str, Any]) -> None:
    _validate_authorization(config)
    gold = _gold_rows(load_jsonl(_assert_bound(config, "gold")))
    predictions = _prediction_map(
        load_jsonl(_assert_bound(config, "predictions_main")), "predictions"
    )
    prompts = _prompt_map(load_jsonl(_assert_bound(config, "prompt_audit_main")))
    rankings = _ranking_map(load_jsonl(_assert_bound(config, "rankings")))
    telemetry = load_json(_assert_bound(config, "telemetry_main"))
    if not isinstance(telemetry, dict):
        raise ValueError("telemetry must be an object")
    audits = evaluate_queries(gold, predictions, prompts, rankings)
    dataset_summaries, equal_weight, decision = summarize(audits, telemetry)
    # Channel C is opened only after the frozen scientific decision above exists in memory.
    metadata = load_jsonl(_assert_bound(config, "metadata"))
    descriptive = descriptive_metadata(metadata, audits)
    write_new_files_atomically(
        (
            (path_from_config(config, "query_audit"), render_jsonl(audits)),
            (
                path_from_config(config, "dataset_summaries"),
                render_json(dataset_summaries),
            ),
            (
                path_from_config(config, "equal_weight_summary"),
                render_json(equal_weight),
            ),
            (
                path_from_config(config, "scientific_decision"),
                render_json(decision),
            ),
            (
                path_from_config(config, "descriptive_metadata"),
                render_json(descriptive),
            ),
        )
    )
    print(
        "STAGE4H_GOLD_EVALUATION_COMPLETE_PENDING_FINAL_VERIFICATION "
        f"queries={len(audits)} decisions={decision['decisions']}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage4H config must be an object")
    run(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE4H_EVALUATION_FAIL: {exc}", file=sys.stderr)
        raise
