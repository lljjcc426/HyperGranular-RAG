"""Gold evaluation, paired bootstrap, and frozen decision for Stage4F-XDR."""

from __future__ import annotations

import argparse
import collections
import re
import string
import sys
from pathlib import Path
from typing import Any, Callable

import numpy as np

from stage4f_xdr_common import (
    BOOTSTRAP_ITERATIONS,
    BOOTSTRAP_SEED,
    SAMPLE_SIZE,
    SCHEMA_VERSION,
    assert_file_identity,
    assert_implementation_binding,
    assert_no_gold_fields,
    load_json,
    load_jsonl,
    render_json,
    render_jsonl,
    require_json_bool,
    require_json_int,
    require_native_string,
    write_new_files_atomically,
)


METHODS = ("DENSE_TOP20", "STATIC_Q25_TOP20")
_UNIT_PARAGRAPH_RE = re.compile(r"::p([0-9]+)::s[0-9]+$")


def _path(config: dict[str, Any], key: str) -> Path:
    return Path(require_native_string(config.get("paths", {}).get(key), f"paths.{key}"))


def _assert_bound(config: dict[str, Any], key: str) -> Path:
    path = _path(config, key)
    expected = config.get("inputs", {}).get(key)
    if not isinstance(expected, dict):
        raise ValueError(f"inputs.{key} identity is missing")
    assert_file_identity(path, expected, f"inputs.{key}")
    return path


def _require_artifact(config: dict[str, Any], key: str) -> Path:
    path = _path(config, key)
    if not path.is_file():
        raise FileNotFoundError(f"Required Stage4F artifact is missing: {path}")
    return path


def _validate_authorization(config: dict[str, Any]) -> None:
    if config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Stage4F config schema differs")
    authorization = config.get("gold_evaluation")
    if not isinstance(authorization, dict) or require_json_bool(
        authorization.get("authorized"), "gold_evaluation.authorized"
    ) is not True:
        raise PermissionError("STAGE4F_GOLD_EVALUATION_NOT_AUTHORIZED")


def normalize_answer(value: str) -> str:
    """Exact MuSiQue official answer normalization from metrics/answer.py."""
    value = value.lower()
    value = "".join(character for character in value if character not in set(string.punctuation))
    value = re.sub(r"\b(a|an|the)\b", " ", value, flags=re.UNICODE)
    return " ".join(value.split())


def _metric_max(metric: Callable[[str, str], float], prediction: str, answers: list[str]) -> float:
    if not answers:
        raise ValueError("At least one official answer is required")
    return max(metric(prediction, answer) for answer in answers)


def _exact(prediction: str, answer: str) -> float:
    return float(normalize_answer(prediction) == normalize_answer(answer))


def _f1(prediction: str, answer: str) -> float:
    predicted_tokens = normalize_answer(prediction).split()
    answer_tokens = normalize_answer(answer).split()
    common = collections.Counter(predicted_tokens) & collections.Counter(answer_tokens)
    same = sum(common.values())
    if not predicted_tokens or not answer_tokens:
        return float(predicted_tokens == answer_tokens)
    if same == 0:
        return 0.0
    precision = same / len(predicted_tokens)
    recall = same / len(answer_tokens)
    return 2.0 * precision * recall / (precision + recall)


def answer_scores(prediction: str, answers: list[str]) -> tuple[float, float]:
    prediction = require_native_string(prediction, "prediction")
    answers = [require_native_string(value, "answer") for value in answers]
    return _metric_max(_exact, prediction, answers), _metric_max(_f1, prediction, answers)


def paired_bootstrap(
    dense_f1: np.ndarray,
    q25_f1: np.ndarray,
    dense_em: np.ndarray,
    q25_em: np.ndarray,
    *,
    seed: int = BOOTSTRAP_SEED,
    iterations: int = BOOTSTRAP_ITERATIONS,
) -> dict[str, Any]:
    arrays = [np.asarray(value, dtype="float64") for value in (dense_f1, q25_f1, dense_em, q25_em)]
    if not arrays[0].size or any(value.shape != arrays[0].shape for value in arrays):
        raise ValueError("Paired bootstrap arrays must be non-empty and shape-identical")
    if any(not np.isfinite(value).all() for value in arrays):
        raise ValueError("Paired bootstrap arrays must be finite")
    if isinstance(iterations, bool) or not isinstance(iterations, int) or iterations <= 0:
        raise ValueError("iterations must be a positive integer")
    rng = np.random.Generator(np.random.PCG64(seed))
    f1_delta = arrays[1] - arrays[0]
    em_delta = arrays[3] - arrays[2]
    f1_samples = np.empty(iterations, dtype="float64")
    em_samples = np.empty(iterations, dtype="float64")
    for index in range(iterations):
        sampled = rng.integers(0, f1_delta.size, size=f1_delta.size)
        f1_samples[index] = np.mean(f1_delta[sampled])
        em_samples[index] = np.mean(em_delta[sampled])
    def summary(point: float, values: np.ndarray) -> dict[str, float]:
        lower, upper = np.percentile(values, [2.5, 97.5], method="linear")
        return {"lower_95": float(lower), "point": float(point), "upper_95": float(upper)}
    return {
        "delta_answer_em": summary(float(np.mean(em_delta)), em_samples),
        "delta_answer_f1": summary(float(np.mean(f1_delta)), f1_samples),
        "iterations": iterations,
        "numpy_generator": "PCG64",
        "percentile_method": "linear",
        "seed": seed,
    }


def scientific_decision(bootstrap: dict[str, Any]) -> str:
    f1 = bootstrap["delta_answer_f1"]
    em = bootstrap["delta_answer_em"]
    if f1["point"] >= 0.010 and f1["lower_95"] > 0.0 and em["lower_95"] >= -0.010:
        return "STATIC_HGRAG_XDR_SUPPORTED"
    if f1["upper_95"] < 0.0 or em["upper_95"] < -0.010:
        return "STATIC_HGRAG_XDR_NEGATIVE"
    return "STATIC_HGRAG_XDR_INCONCLUSIVE"


def _paragraph_indices(unit_ids: list[str], label: str) -> set[int]:
    result = set()
    for index, value in enumerate(unit_ids):
        value = require_native_string(value, f"{label}[{index}]")
        match = _UNIT_PARAGRAPH_RE.search(value)
        if match is None:
            raise ValueError(f"{label}[{index}] unit ID has no paragraph identity")
        result.add(int(match.group(1)))
    return result


def _indexed_pairs(rows: list[dict[str, Any]], label: str) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(rows):
        query_id = require_native_string(row.get("query_id"), f"{label}[{index}].query_id")
        method = require_native_string(row.get("method"), f"{label}[{index}].method")
        if method not in METHODS or (query_id, method) in result:
            raise ValueError(f"{label} method pairing differs")
        result[(query_id, method)] = row
    return result


def require_complete_pairs(
    rows: list[dict[str, Any]], query_ids: list[str], label: str
) -> dict[tuple[str, str], dict[str, Any]]:
    indexed = _indexed_pairs(rows, label)
    expected = {(query_id, method) for query_id in query_ids for method in METHODS}
    if set(indexed) != expected:
        raise ValueError(f"{label} must pair every query across both arms")
    return indexed


def run_gold(config: dict[str, Any]) -> None:
    _validate_authorization(config)
    assert_implementation_binding(config, Path(__file__).resolve().parents[1])
    predictions_main = _require_artifact(config, "predictions_main")
    predictions_rerun = _require_artifact(config, "predictions_rerun")
    prompt_main = _require_artifact(config, "prompt_audit_main")
    prompt_rerun = _require_artifact(config, "prompt_audit_rerun")
    rankings_path = _require_artifact(config, "rankings")
    if predictions_main.read_bytes() != predictions_rerun.read_bytes():
        raise ValueError("Main/rerun prediction bytes differ")
    if prompt_main.read_bytes() != prompt_rerun.read_bytes():
        raise ValueError("Main/rerun prompt-audit bytes differ")
    rankings = load_jsonl(rankings_path)
    predictions = load_jsonl(predictions_main)
    prompts = load_jsonl(prompt_main)
    assert_no_gold_fields(rankings, "rankings")
    assert_no_gold_fields(predictions, "predictions")
    assert_no_gold_fields(prompts, "prompt audits")
    gold = load_jsonl(_assert_bound(config, "gold"))
    if len(gold) != SAMPLE_SIZE or len(rankings) != SAMPLE_SIZE:
        raise ValueError("Official Stage4F query count differs")
    gold_query_ids = [
        require_native_string(row.get("query_id"), f"gold[{index}].query_id")
        for index, row in enumerate(gold)
    ]
    prediction_map = require_complete_pairs(predictions, gold_query_ids, "predictions")
    prompt_map = require_complete_pairs(prompts, gold_query_ids, "prompts")
    ranking_map = {row["query_id"]: row for row in rankings}
    if len(ranking_map) != SAMPLE_SIZE:
        raise ValueError("Ranking query identities duplicate")
    metrics = {
        method: {"answer_em": [], "answer_f1": [], "retrieval_cr20": [], "retrieval_er20": [], "unknown": []}
        for method in METHODS
    }
    audits: list[dict[str, Any]] = []
    effect_counts = {"gain": 0, "harm": 0, "same": 0}
    for gold_index, gold_row in enumerate(gold):
        query_id = require_native_string(gold_row.get("query_id"), f"gold[{gold_index}].query_id")
        if query_id not in ranking_map:
            raise ValueError("Gold/ranking query identity differs")
        answers = gold_row.get("answers")
        supporting = gold_row.get("supporting_paragraph_indices")
        if not isinstance(answers, list) or not answers or not isinstance(supporting, list) or not supporting:
            raise ValueError("Gold answer/support schema differs")
        supporting_set = {
            require_json_int(value, f"{query_id}: supporting paragraph") for value in supporting
        }
        ranking = ranking_map[query_id]
        row_audit: dict[str, Any] = {
            "dataset": gold_row["dataset"], "query_id": query_id,
            "sample_id": gold_row["sample_id"],
        }
        for method, ranking_key in (
            ("DENSE_TOP20", "dense_top20_unit_ids"),
            ("STATIC_Q25_TOP20", "static_q25_top20_unit_ids"),
        ):
            prediction_row = prediction_map.get((query_id, method))
            prompt_row = prompt_map.get((query_id, method))
            if prediction_row is None or prompt_row is None:
                raise ValueError("All queries must be paired across both arms")
            ranked_ids = ranking.get(ranking_key)
            if not isinstance(ranked_ids, list) or not ranked_ids:
                raise ValueError("Ranking list is empty")
            evidence_ids = prompt_row.get("evidence_unit_ids")
            if not isinstance(evidence_ids, list) or evidence_ids != ranked_ids[: len(evidence_ids)]:
                raise ValueError("Prompt evidence is not a ranking prefix")
            em, f1 = answer_scores(prediction_row["prediction"], answers)
            retrieved_paragraphs = _paragraph_indices(ranked_ids, ranking_key)
            overlap = len(supporting_set & retrieved_paragraphs)
            er = overlap / len(supporting_set)
            cr = float(overlap == len(supporting_set))
            unknown = float(prediction_row["prediction"].strip().upper() == "UNKNOWN")
            for key, value in (("answer_em", em), ("answer_f1", f1), ("retrieval_er20", er), ("retrieval_cr20", cr), ("unknown", unknown)):
                metrics[method][key].append(value)
            row_audit[method.lower()] = {
                "answer_em": em, "answer_f1": f1,
                "input_token_count": prompt_row["input_token_count"],
                "included_evidence_units": len(evidence_ids),
                "rank1_truncated": prompt_row["rank1_truncated"],
                "retrieval_cr20": cr, "retrieval_er20": er, "unknown": unknown,
            }
        delta = row_audit["static_q25_top20"]["answer_f1"] - row_audit["dense_top20"]["answer_f1"]
        effect_counts["gain" if delta > 0 else "harm" if delta < 0 else "same"] += 1
        audits.append(row_audit)
    dense = metrics["DENSE_TOP20"]
    q25 = metrics["STATIC_Q25_TOP20"]
    bootstrap = paired_bootstrap(
        np.asarray(dense["answer_f1"]), np.asarray(q25["answer_f1"]),
        np.asarray(dense["answer_em"]), np.asarray(q25["answer_em"]),
    )
    decision = scientific_decision(bootstrap)
    summary = {
        "bootstrap": bootstrap,
        "evidence_label_granularity": "official_supporting_paragraph",
        "insertion_effect_queries": effect_counts,
        "methods": {
            method: {key: float(np.mean(values)) for key, values in rows.items()}
            for method, rows in metrics.items()
        },
        "official_answer_evaluator": config["evaluation"]["official_answer_evaluator"],
        "queries": len(audits),
        "schema_version": SCHEMA_VERSION,
        "supporting_fact_sentence_recall": {
            "available": False,
            "reason": "MuSiQue v1.0 provides supporting-paragraph, not supporting-sentence, labels",
        },
        "status": "STAGE4F_GOLD_EVALUATION_COMPLETE_PENDING_INDEPENDENT_VERIFICATION",
    }
    decision_row = {
        "decision": decision,
        "gates": config["evaluation"]["decision_gates"],
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4F_SCIENTIFIC_DECISION_PENDING_INDEPENDENT_VERIFICATION",
    }
    write_new_files_atomically(
        (
            (_path(config, "query_audit"), render_jsonl(audits)),
            (_path(config, "evaluation_summary"), render_json(summary)),
            (_path(config, "scientific_decision"), render_json(decision_row)),
        )
    )
    print(decision)


def run_metadata(config: dict[str, Any]) -> None:
    _validate_authorization(config)
    summary = load_json(_path(config, "evaluation_summary"))
    decision = load_json(_path(config, "scientific_decision"))
    if summary.get("status") != "STAGE4F_GOLD_EVALUATION_COMPLETE_PENDING_INDEPENDENT_VERIFICATION":
        raise ValueError("Primary summary must be frozen before Channel C opens")
    if decision.get("decision") not in {
        "STATIC_HGRAG_XDR_SUPPORTED", "STATIC_HGRAG_XDR_NEGATIVE", "STATIC_HGRAG_XDR_INCONCLUSIVE"
    }:
        raise ValueError("Scientific decision must be frozen before Channel C opens")
    metadata = load_jsonl(_assert_bound(config, "metadata"))
    audit = load_jsonl(_path(config, "query_audit"))
    audit_map = {row["query_id"]: row for row in audit}
    if [row["query_id"] for row in metadata] != [row["query_id"] for row in audit]:
        raise ValueError("Channel C identity/order differs")
    groups: dict[int, list[dict[str, Any]]] = {}
    for row in metadata:
        hop_count = require_json_int(row.get("hop_count"), "metadata.hop_count")
        groups.setdefault(hop_count, []).append(audit_map[row["query_id"]])
    rows = [
        {
            "caution": "SUBGROUP_CAUTION",
            "dense_answer_f1": float(np.mean([item["dense_top20"]["answer_f1"] for item in values])),
            "dimension": "hop_count",
            "queries": len(values),
            "static_q25_answer_f1": float(np.mean([item["static_q25_top20"]["answer_f1"] for item in values])),
            "value": hop_count,
        }
        for hop_count, values in sorted(groups.items())
    ]
    write_new_files_atomically(
        ((_path(config, "descriptive_subgroups"), render_json({
            "rows": rows, "schema_version": SCHEMA_VERSION,
            "status": "STAGE4F_DESCRIPTIVE_SUBGROUPS_FROZEN_AFTER_PRIMARY_DECISION",
        })),)
    )
    print("STAGE4F_DESCRIPTIVE_SUBGROUPS_FROZEN_AFTER_PRIMARY_DECISION")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--phase", required=True, choices=("gold", "metadata"))
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage4F config must be an object")
    (run_gold if args.phase == "gold" else run_metadata)(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE4F_EVALUATION_FAIL: {exc}", file=sys.stderr)
        raise
