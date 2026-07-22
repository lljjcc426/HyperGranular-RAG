"""Gold-only Stage4G evaluation and frozen generator-transfer decision."""

from __future__ import annotations

import argparse
import collections
import re
import string
from pathlib import Path
from typing import Any, Callable

import numpy as np

from stage4g_gtr_common import (
    BOOTSTRAP_ITERATIONS,
    BOOTSTRAP_SEED,
    DATASETS,
    METHODS,
    SCHEMA_VERSION,
    assert_identity,
    load_json,
    load_jsonl,
    paired_bootstrap,
    render_json,
    render_jsonl,
    require_string,
    scientific_decision,
    stratified_equal_weight_bootstrap,
    write_new_files_atomically,
)


def _path(config: dict[str, Any], key: str) -> Path:
    return Path(require_string(config["paths"].get(key), f"paths.{key}"))


def _normalize(value: str) -> str:
    value = value.lower()
    value = "".join(character for character in value if character not in set(string.punctuation))
    value = re.sub(r"\b(a|an|the)\b", " ", value, flags=re.UNICODE)
    return " ".join(value.split())


def _exact(prediction: str, answer: str) -> float:
    return float(_normalize(prediction) == _normalize(answer))


def _f1(prediction: str, answer: str, *, hotpot: bool) -> float:
    prediction = _normalize(prediction)
    answer = _normalize(answer)
    if hotpot and (
        (prediction in {"yes", "no", "noanswer"} and prediction != answer)
        or (answer in {"yes", "no", "noanswer"} and prediction != answer)
    ):
        return 0.0
    predicted_tokens = prediction.split()
    answer_tokens = answer.split()
    common = collections.Counter(predicted_tokens) & collections.Counter(answer_tokens)
    same = sum(common.values())
    if not predicted_tokens or not answer_tokens:
        return float(predicted_tokens == answer_tokens)
    if same == 0:
        return 0.0
    precision = same / len(predicted_tokens)
    recall = same / len(answer_tokens)
    return 2.0 * precision * recall / (precision + recall)


def answer_scores(dataset: str, prediction: str, answers: list[str]) -> tuple[float, float]:
    prediction = require_string(prediction, "prediction", nonempty=False)
    if not answers or any(not isinstance(answer, str) for answer in answers):
        raise ValueError("Gold answers must be a non-empty string list")
    hotpot = dataset == DATASETS[0]
    return (
        max(_exact(prediction, answer) for answer in answers),
        max(_f1(prediction, answer, hotpot=hotpot) for answer in answers),
    )


def _pair_index(rows: list[dict[str, Any]], label: str) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for row_number, row in enumerate(rows):
        query_id = require_string(row.get("query_id"), f"{label}[{row_number}].query_id")
        method = require_string(row.get("method"), f"{label}[{row_number}].method")
        if method not in METHODS or (query_id, method) in index:
            raise ValueError(f"{label}[{row_number}] duplicate or invalid method")
        index[(query_id, method)] = row
    return index


def _gold_map(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for dataset in DATASETS:
        entry = config["inputs"][dataset]["gold"]
        path = Path(entry["path"])
        assert_identity(path, entry, f"{dataset} Gold")
        for row_number, row in enumerate(load_jsonl(path)):
            query_id = require_string(row.get("query_id"), f"{dataset}.gold[{row_number}].query_id")
            sample_id = require_string(row.get("sample_id"), f"{dataset}.gold[{row_number}].sample_id")
            if row.get("dataset") != dataset or query_id != f"{dataset}::{sample_id}" or query_id in result:
                raise ValueError(f"{dataset}.gold[{row_number}] identity differs")
            answers = [row["answer"]] if dataset == DATASETS[0] else row["answers"]
            if not isinstance(answers, list) or not answers:
                raise ValueError(f"{query_id}: Gold answers are missing")
            result[query_id] = {"answers": answers, "dataset": dataset, "sample_id": sample_id}
    if len(result) != 4_000:
        raise ValueError("Stage4G Gold union must contain 4,000 queries")
    return result


def _qwen_deltas(config: dict[str, Any]) -> dict[str, dict[str, tuple[float, float]]]:
    result: dict[str, dict[str, tuple[float, float]]] = {}
    for dataset in DATASETS:
        entry = config["inputs"][dataset]["qwen_query_audit"]
        path = Path(entry["path"])
        assert_identity(path, entry, f"{dataset} frozen Qwen query audit")
        mapping: dict[str, tuple[float, float]] = {}
        for row in load_jsonl(path):
            query_id = require_string(row.get("query_id"), f"{dataset} Qwen query_id")
            if row.get("dataset") != dataset or query_id in mapping:
                raise ValueError(f"{dataset} Qwen query audit identity differs")
            if dataset == DATASETS[0]:
                dense, q25 = row["dense"], row["static_q25"]
            else:
                dense, q25 = row["dense_top20"], row["static_q25_top20"]
            mapping[query_id] = (
                float(q25["answer_f1"]) - float(dense["answer_f1"]),
                float(q25["answer_em"]) - float(dense["answer_em"]),
            )
        if len(mapping) != config["inputs"][dataset]["query_count"]:
            raise ValueError(f"{dataset} frozen Qwen query audit count differs")
        result[dataset] = mapping
    return result


def _method_summary(score_rows: list[dict[str, Any]], audit_rows: list[dict[str, Any]], method: str) -> dict[str, float]:
    scores = [row["methods"][method] for row in score_rows]
    audits = [row for row in audit_rows if row["method"] == method]
    return {
        "answer_em": float(np.mean([row["answer_em"] for row in scores])),
        "answer_f1": float(np.mean([row["answer_f1"] for row in scores])),
        "completion_tokens_mean": float(np.mean([len(row["completion_token_ids"]) for row in audits])),
        "included_evidence_units_mean": float(np.mean([len(row["evidence_unit_ids"]) for row in audits])),
        "input_tokens_mean": float(np.mean([row["input_token_count"] for row in audits])),
        "truncation_rate": float(np.mean([row["rank1_truncated"] for row in audits])),
        "unknown_rate": float(np.mean([row["prediction"].strip().upper() == "UNKNOWN" for row in audits])),
    }


def run(config: dict[str, Any]) -> None:
    if config.get("gold_evaluation", {}).get("authorized") is not True:
        raise PermissionError("Stage4G Gold evaluation is not authorized")
    verified = load_json(_path(config, "verified_pregold"))
    if verified.get("status") != "STAGE4G_GTR_PRE_GOLD_VERIFIED":
        raise ValueError("Stage4G pre-Gold verification has not passed")
    predictions_path = _path(config, "predictions_main")
    audits_path = _path(config, "prompt_audit_main")
    predictions = load_jsonl(predictions_path)
    audits = load_jsonl(audits_path)
    from stage4g_gtr_common import file_identity
    for key in (
        "predictions_main", "predictions_rerun_subset", "prompt_audit_main",
        "prompt_audit_rerun_subset", "telemetry_main", "telemetry_rerun_subset",
    ):
        if verified["artifacts"].get(key) != file_identity(_path(config, key)):
            raise ValueError(f"{key} changed after pre-Gold verification")
    prediction_index = _pair_index(predictions, "predictions")
    audit_index = _pair_index(audits, "prompt audits")
    if set(prediction_index) != set(audit_index) or len(prediction_index) != 8_000:
        raise ValueError("Stage4G prediction/audit pair universe differs")
    gold = _gold_map(config)
    qwen = _qwen_deltas(config)
    query_scores: list[dict[str, Any]] = []
    by_dataset: dict[str, list[dict[str, Any]]] = {dataset: [] for dataset in DATASETS}
    for query_id, target in gold.items():
        methods: dict[str, dict[str, Any]] = {}
        for method in METHODS:
            prediction = prediction_index[(query_id, method)]
            if prediction.get("dataset") != target["dataset"] or prediction.get("sample_id") != target["sample_id"]:
                raise ValueError(f"{query_id}: prediction identity differs from Gold")
            em, f1 = answer_scores(target["dataset"], prediction["prediction"], target["answers"])
            methods[method] = {
                "answer_em": em,
                "answer_f1": f1,
                "prediction": prediction["prediction"],
            }
        row = {
            "dataset": target["dataset"],
            "methods": methods,
            "query_id": query_id,
            "sample_id": target["sample_id"],
        }
        query_scores.append(row)
        by_dataset[target["dataset"]].append(row)
    dataset_summaries: dict[str, dict[str, Any]] = {}
    deltas: dict[str, dict[str, np.ndarray]] = {}
    interactions: dict[str, dict[str, np.ndarray]] = {}
    for dataset in DATASETS:
        rows = by_dataset[dataset]
        dense_f1 = np.asarray([row["methods"][METHODS[0]]["answer_f1"] for row in rows], dtype="float64")
        q25_f1 = np.asarray([row["methods"][METHODS[1]]["answer_f1"] for row in rows], dtype="float64")
        dense_em = np.asarray([row["methods"][METHODS[0]]["answer_em"] for row in rows], dtype="float64")
        q25_em = np.asarray([row["methods"][METHODS[1]]["answer_em"] for row in rows], dtype="float64")
        f1_delta, em_delta = q25_f1 - dense_f1, q25_em - dense_em
        qwen_f1 = np.asarray([qwen[dataset][row["query_id"]][0] for row in rows], dtype="float64")
        qwen_em = np.asarray([qwen[dataset][row["query_id"]][1] for row in rows], dtype="float64")
        deltas[dataset] = {"f1": f1_delta, "em": em_delta}
        interactions[dataset] = {"f1": f1_delta - qwen_f1, "em": em_delta - qwen_em}
        dataset_audits = [row for row in audits if row["dataset"] == dataset]
        dataset_summaries[dataset] = {
            "bootstrap": {
                "delta_answer_em": paired_bootstrap(em_delta),
                "delta_answer_f1": paired_bootstrap(f1_delta),
                "iterations": BOOTSTRAP_ITERATIONS,
                "numpy_generator": "PCG64",
                "percentile_method": "linear",
                "seed": BOOTSTRAP_SEED,
            },
            "generator_interaction": {
                "answer_em": paired_bootstrap(interactions[dataset]["em"]),
                "answer_f1": paired_bootstrap(interactions[dataset]["f1"]),
                "definition": "second_generator_retrieval_delta_minus_frozen_qwen_retrieval_delta",
                "decision_role": "DESCRIPTIVE_ONLY",
            },
            "methods": {
                method: _method_summary(rows, dataset_audits, method) for method in METHODS
            },
            "queries": len(rows),
        }
    equal_weight = {
        "bootstrap": {
            "delta_answer_em": stratified_equal_weight_bootstrap(
                deltas[DATASETS[0]]["em"], deltas[DATASETS[1]]["em"]
            ),
            "delta_answer_f1": stratified_equal_weight_bootstrap(
                deltas[DATASETS[0]]["f1"], deltas[DATASETS[1]]["f1"]
            ),
            "iterations": BOOTSTRAP_ITERATIONS,
            "numpy_generator": "PCG64",
            "percentile_method": "linear",
            "seed": BOOTSTRAP_SEED,
            "weighting": "DATASET_EQUAL_WEIGHT",
        },
        "generator_interaction": {
            "answer_em": stratified_equal_weight_bootstrap(
                interactions[DATASETS[0]]["em"], interactions[DATASETS[1]]["em"]
            ),
            "answer_f1": stratified_equal_weight_bootstrap(
                interactions[DATASETS[0]]["f1"], interactions[DATASETS[1]]["f1"]
            ),
            "decision_role": "DESCRIPTIVE_ONLY",
        },
        "query_weighted_descriptive": {
            "delta_answer_em": float(np.mean(np.concatenate([deltas[value]["em"] for value in DATASETS]))),
            "delta_answer_f1": float(np.mean(np.concatenate([deltas[value]["f1"] for value in DATASETS]))),
            "musique_weight": 0.75,
            "decision_role": "DESCRIPTIVE_ONLY",
        },
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4G_EQUAL_WEIGHT_SUMMARY_PENDING_INDEPENDENT_VERIFICATION",
    }
    decision = scientific_decision(
        dataset_summaries,
        {
            "delta_answer_f1": equal_weight["bootstrap"]["delta_answer_f1"],
            "delta_answer_em": equal_weight["bootstrap"]["delta_answer_em"],
        },
    )
    decision_payload = {
        "decision": decision,
        "generator": {
            "model_id": config["generator"]["model_id"],
            "revision": config["generator"]["revision"],
            "runtime_format": config["generator"]["runtime_format"],
        },
        "locks": config["locks"],
        "schema_version": SCHEMA_VERSION,
        "scope": "ONE_ADDITIONAL_PRE_SPECIFIED_GENERATOR_CONFIGURATION",
        "status": "STAGE4G_SCIENTIFIC_DECISION_PENDING_FINAL_VERIFICATION",
    }
    dataset_payload = {
        "datasets": dataset_summaries,
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4G_DATASET_SUMMARIES_PENDING_INDEPENDENT_VERIFICATION",
    }
    write_new_files_atomically([
        (_path(config, "query_scores"), render_jsonl(query_scores)),
        (_path(config, "dataset_summaries"), render_json(dataset_payload)),
        (_path(config, "equal_weight_summary"), render_json(equal_weight)),
        (_path(config, "scientific_decision"), render_json(decision_payload)),
    ])
    print(f"STAGE4G_GTR_GOLD_EVALUATION_COMPLETE decision={decision}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    run(load_json(args.config))


if __name__ == "__main__":
    main()
