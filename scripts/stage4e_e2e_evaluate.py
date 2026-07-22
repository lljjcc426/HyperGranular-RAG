"""Gold evaluator for frozen Stage4E predictions.

The authorization gate and main/rerun identity checks occur before the Gold
target is opened.  Descriptive metadata is opened only after the primary
decision has been computed.
"""

from __future__ import annotations

import argparse
import re
import string
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from stage4e_e2e_common import (
    BOOTSTRAP_ITERATIONS,
    BOOTSTRAP_SEED,
    DATASET,
    SCHEMA_VERSION,
    assert_implementation_binding,
    assert_file_identity,
    load_json,
    load_jsonl,
    render_json,
    render_jsonl,
    require_json_bool,
    require_native_string,
    write_new_files_atomically,
)


OFFICIAL_EVALUATOR_COMMIT = "3635853403a8735609ee997664e1528f4480762a"
OFFICIAL_EVALUATOR_SHA256 = "D35FC91A6DB21D791DBDDA11DAF3856E9359F5701D54E3EEFBA20D88FECC02C0"
PREDICTION_KEYS = {"dataset", "method", "prediction", "query_id", "sample_id"}
METHODS = ("DENSE_TOP20", "STATIC_Q25_TOP20")


def normalize_answer(value: str) -> str:
    """Exact answer normalization from pinned HotpotQA evaluation source."""

    def remove_articles(text: str) -> str:
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text: str) -> str:
        return " ".join(text.split())

    def remove_punc(text: str) -> str:
        exclude = set(string.punctuation)
        return "".join(character for character in text if character not in exclude)

    return white_space_fix(remove_articles(remove_punc(value.lower())))


def answer_scores(prediction: str, ground_truth: str) -> tuple[float, float]:
    normalized_prediction = normalize_answer(prediction)
    normalized_ground_truth = normalize_answer(ground_truth)
    em = float(normalized_prediction == normalized_ground_truth)
    if (
        normalized_prediction in {"yes", "no", "noanswer"}
        and normalized_prediction != normalized_ground_truth
    ) or (
        normalized_ground_truth in {"yes", "no", "noanswer"}
        and normalized_prediction != normalized_ground_truth
    ):
        return em, 0.0
    prediction_tokens = normalized_prediction.split()
    ground_truth_tokens = normalized_ground_truth.split()
    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return em, 0.0
    precision = num_same / len(prediction_tokens)
    recall = num_same / len(ground_truth_tokens)
    return em, 2 * precision * recall / (precision + recall)


def paired_bootstrap(
    dense_f1: np.ndarray,
    q25_f1: np.ndarray,
    dense_em: np.ndarray,
    q25_em: np.ndarray,
    *,
    seed: int = BOOTSTRAP_SEED,
    iterations: int = BOOTSTRAP_ITERATIONS,
) -> dict[str, Any]:
    arrays = (dense_f1, q25_f1, dense_em, q25_em)
    if len({len(value) for value in arrays}) != 1 or len(dense_f1) == 0:
        raise ValueError("Paired bootstrap arrays must have one non-empty shared length")
    if not all(np.isfinite(value).all() for value in arrays):
        raise ValueError("Paired bootstrap inputs must be finite")
    rng = np.random.default_rng(seed)
    f1_delta = np.asarray(q25_f1 - dense_f1, dtype="float64")
    em_delta = np.asarray(q25_em - dense_em, dtype="float64")
    f1_draws = np.empty(iterations, dtype="float64")
    em_draws = np.empty(iterations, dtype="float64")
    for index in range(iterations):
        draw = rng.integers(0, len(f1_delta), size=len(f1_delta))
        f1_draws[index] = float(np.mean(f1_delta[draw]))
        em_draws[index] = float(np.mean(em_delta[draw]))
    return {
        "iterations": iterations,
        "numpy_generator": "PCG64",
        "percentile_method": "linear",
        "seed": seed,
        "delta_answer_f1": {
            "lower_95": float(np.quantile(f1_draws, 0.025, method="linear")),
            "point": float(np.mean(f1_delta)),
            "upper_95": float(np.quantile(f1_draws, 0.975, method="linear")),
        },
        "delta_answer_em": {
            "lower_95": float(np.quantile(em_draws, 0.025, method="linear")),
            "point": float(np.mean(em_delta)),
            "upper_95": float(np.quantile(em_draws, 0.975, method="linear")),
        },
    }


def scientific_decision(bootstrap: dict[str, Any]) -> str:
    f1 = bootstrap["delta_answer_f1"]
    em = bootstrap["delta_answer_em"]
    if f1["point"] >= 0.010 and f1["lower_95"] > 0 and em["lower_95"] >= -0.010:
        return "STATIC_HGRAG_E2E_SUPPORTED"
    if f1["upper_95"] < 0 or em["upper_95"] < -0.010:
        return "STATIC_HGRAG_E2E_NEGATIVE"
    return "STATIC_HGRAG_E2E_INCONCLUSIVE"


def _validate_authorization(config: dict[str, Any]) -> None:
    if config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Stage4E config schema_version differs")
    authorization = config.get("gold_evaluation")
    if not isinstance(authorization, dict):
        raise ValueError("gold_evaluation must be an object")
    if require_json_bool(authorization.get("authorized"), "gold_evaluation.authorized") is not True:
        raise PermissionError("STAGE4E_GOLD_EVALUATION_NOT_AUTHORIZED")


def _path(config: dict[str, Any], key: str) -> Path:
    return Path(require_native_string(config.get("paths", {}).get(key), f"paths.{key}"))


def _load_predictions(path: Path) -> list[dict[str, Any]]:
    rows = load_jsonl(path)
    seen: set[tuple[str, str]] = set()
    for index, row in enumerate(rows):
        if set(row) != PREDICTION_KEYS:
            raise ValueError(f"predictions[{index}] key contract differs")
        dataset = require_native_string(row["dataset"], f"predictions[{index}].dataset")
        query_id = require_native_string(row["query_id"], f"predictions[{index}].query_id")
        sample_id = require_native_string(row["sample_id"], f"predictions[{index}].sample_id")
        method = require_native_string(row["method"], f"predictions[{index}].method")
        if not isinstance(row["prediction"], str):
            raise ValueError(f"predictions[{index}].prediction must be a native string")
        if dataset != DATASET or query_id != f"{dataset}::{sample_id}" or method not in METHODS:
            raise ValueError(f"predictions[{index}] identity/method contract differs")
        identity = (query_id, method)
        if identity in seen:
            raise ValueError(f"Duplicate prediction identity: {identity}")
        seen.add(identity)
    if len(rows) != 2000:
        raise ValueError("Official Stage4E predictions must contain 2,000 rows")
    return rows


def _load_gold(path: Path, expected: dict[str, Any]) -> list[dict[str, Any]]:
    assert_file_identity(path, expected, "inputs.gold")
    rows = load_jsonl(path)
    required = {"answer", "dataset", "query_id", "sample_id", "supporting_facts"}
    for index, row in enumerate(rows):
        if set(row) != required:
            raise ValueError(f"gold[{index}] key contract differs")
        require_native_string(row["answer"], f"gold[{index}].answer")
        if not isinstance(row["supporting_facts"], list) or not row["supporting_facts"]:
            raise ValueError(f"gold[{index}].supporting_facts must be non-empty")
    if len(rows) != 1000:
        raise ValueError("Official Stage4E Gold channel must contain 1,000 rows")
    return rows


def evaluate_rows(
    predictions: list[dict[str, Any]],
    rankings: list[dict[str, Any]],
    gold_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    prediction_map = {
        (row["query_id"], row["method"]): row["prediction"] for row in predictions
    }
    ranking_map = {row["query_id"]: row for row in rankings}
    audits: list[dict[str, Any]] = []
    values: dict[str, dict[str, list[float]]] = {
        method: defaultdict(list) for method in METHODS
    }
    insertion_effect = Counter()
    for gold in gold_rows:
        query_id = require_native_string(gold["query_id"], "gold.query_id")
        ranking = ranking_map.get(query_id)
        if ranking is None:
            raise ValueError(f"Missing ranking for {query_id}")
        gold_units = {
            require_native_string(row.get("unit_id"), f"{query_id}.supporting_facts.unit_id")
            for row in gold["supporting_facts"]
            if isinstance(row, dict)
        }
        if len(gold_units) != len(gold["supporting_facts"]):
            raise ValueError(f"{query_id}: Gold unit IDs are missing or duplicated")
        method_cr: dict[str, float] = {}
        method_rows: dict[str, dict[str, Any]] = {}
        for method, ranking_key in (
            ("DENSE_TOP20", "dense_top20_unit_ids"),
            ("STATIC_Q25_TOP20", "static_q25_top20_unit_ids"),
        ):
            prediction = prediction_map.get((query_id, method))
            if prediction is None:
                raise ValueError(f"Missing prediction for {(query_id, method)}")
            em, f1 = answer_scores(prediction, gold["answer"])
            retrieved = ranking.get(ranking_key)
            if not isinstance(retrieved, list) or not retrieved:
                raise ValueError(f"{query_id}: {ranking_key} is invalid")
            hits = len(gold_units & set(retrieved))
            er = hits / len(gold_units)
            cr = float(hits == len(gold_units))
            method_cr[method] = cr
            values[method]["answer_em"].append(em)
            values[method]["answer_f1"].append(f1)
            values[method]["retrieval_cr20"].append(cr)
            values[method]["retrieval_er20"].append(er)
            values[method]["unknown"].append(float(prediction.casefold() == "unknown"))
            method_rows[method] = {
                "answer_em": em,
                "answer_f1": f1,
                "prediction": prediction,
                "retrieval_cr20": cr,
                "retrieval_er20": er,
            }
        difference = method_cr["STATIC_Q25_TOP20"] - method_cr["DENSE_TOP20"]
        insertion_effect["gain" if difference > 0 else "harm" if difference < 0 else "same"] += 1
        audits.append(
            {
                "answer": gold["answer"],
                "dataset": gold["dataset"],
                "dense": method_rows["DENSE_TOP20"],
                "query_id": query_id,
                "sample_id": gold["sample_id"],
                "static_q25": method_rows["STATIC_Q25_TOP20"],
            }
        )

    dense_f1 = np.asarray(values["DENSE_TOP20"]["answer_f1"], dtype="float64")
    q25_f1 = np.asarray(values["STATIC_Q25_TOP20"]["answer_f1"], dtype="float64")
    dense_em = np.asarray(values["DENSE_TOP20"]["answer_em"], dtype="float64")
    q25_em = np.asarray(values["STATIC_Q25_TOP20"]["answer_em"], dtype="float64")
    bootstrap = paired_bootstrap(dense_f1, q25_f1, dense_em, q25_em)
    decision = scientific_decision(bootstrap)
    summary = {
        "bootstrap": bootstrap,
        "insertion_effect_queries": dict(sorted(insertion_effect.items())),
        "methods": {
            method: {
                key: float(np.mean(value)) for key, value in sorted(metrics.items())
            }
            for method, metrics in values.items()
        },
        "queries": len(gold_rows),
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4E_GOLD_EVALUATION_COMPLETE_PENDING_INDEPENDENT_VERIFICATION",
    }
    decision_row = {
        "decision": decision,
        "gates": {
            "em_interval_lower_minimum": -0.010,
            "f1_interval_lower_strictly_positive": True,
            "minimum_delta_answer_f1": 0.010,
            "negative_em_interval_upper_below": -0.010,
            "negative_f1_interval_upper_below": 0.0,
        },
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4E_SCIENTIFIC_DECISION_PENDING_INDEPENDENT_VERIFICATION",
    }
    return audits, summary, decision_row


def _descriptive_subgroups(
    audits: list[dict[str, Any]], metadata_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    audit_map = {row["query_id"]: row for row in audits}
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in metadata_rows:
        query_id = require_native_string(row.get("query_id"), "metadata.query_id")
        if query_id not in audit_map:
            raise ValueError(f"Metadata identity absent from audit: {query_id}")
        groups[(require_native_string(row.get("type"), "metadata.type"), "type")].append(
            audit_map[query_id]
        )
        groups[(require_native_string(row.get("level"), "metadata.level"), "level")].append(
            audit_map[query_id]
        )
    result: list[dict[str, Any]] = []
    for (value, dimension), rows in sorted(groups.items()):
        result.append(
            {
                "caution": "SUBGROUP_CAUTION",
                "dense_answer_f1": float(np.mean([row["dense"]["answer_f1"] for row in rows])),
                "dimension": dimension,
                "queries": len(rows),
                "static_q25_answer_f1": float(
                    np.mean([row["static_q25"]["answer_f1"] for row in rows])
                ),
                "value": value,
            }
        )
    return result


def run(config: dict[str, Any]) -> None:
    _validate_authorization(config)
    assert_implementation_binding(config, Path(__file__).resolve().parents[1])

    main_path = _path(config, "predictions_main")
    rerun_path = _path(config, "predictions_rerun")
    if main_path.read_bytes() != rerun_path.read_bytes():
        raise ValueError("Main/rerun predictions are not byte-identical")
    if _path(config, "prompt_audit_main").read_bytes() != _path(
        config, "prompt_audit_rerun"
    ).read_bytes():
        raise ValueError("Main/rerun prompt audits are not byte-identical")
    pregold_verification = load_json(_path(config, "verified_pregold"))
    if pregold_verification.get("status") != "STAGE4E_PRE_GOLD_ARTIFACTS_VERIFIED":
        raise ValueError("Independent pre-Gold verification has not passed")
    predictions = _load_predictions(main_path)
    rankings = load_jsonl(_path(config, "rankings"))

    gold_binding = config.get("inputs", {}).get("gold")
    if not isinstance(gold_binding, dict):
        raise ValueError("inputs.gold identity is missing")
    gold_rows = _load_gold(_path(config, "gold"), gold_binding)
    audits, summary, decision = evaluate_rows(predictions, rankings, gold_rows)

    # Protocol boundary: metadata is not opened until aggregate metrics,
    # bootstrap, and the primary scientific decision are already frozen in memory.
    metadata_binding = config.get("inputs", {}).get("metadata")
    if not isinstance(metadata_binding, dict):
        raise ValueError("inputs.metadata identity is missing")
    metadata_path = _path(config, "metadata")
    assert_file_identity(metadata_path, metadata_binding, "inputs.metadata")
    metadata_rows = load_jsonl(metadata_path)
    summary["descriptive_subgroups"] = _descriptive_subgroups(audits, metadata_rows)
    summary["official_answer_evaluator"] = {
        "commit": OFFICIAL_EVALUATOR_COMMIT,
        "sha256": OFFICIAL_EVALUATOR_SHA256,
        "source": (
            "https://github.com/hotpotqa/hotpot/blob/"
            f"{OFFICIAL_EVALUATOR_COMMIT}/hotpot_evaluate_v1.py"
        ),
    }
    write_new_files_atomically(
        (
            (_path(config, "query_audit"), render_jsonl(audits)),
            (_path(config, "evaluation_summary"), render_json(summary)),
            (_path(config, "scientific_decision"), render_json(decision)),
        )
    )
    print(
        "STAGE4E_GOLD_EVALUATION_COMPLETE_PENDING_INDEPENDENT_VERIFICATION "
        f"decision={decision['decision']} queries={len(audits)}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage4E config must be an object")
    run(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE4E_GOLD_EVALUATION_FAIL: {exc}", file=sys.stderr)
        raise
