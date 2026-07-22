"""Independent input, pre-Gold, and post-Gold verification for Stage4G."""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import re
import string
import sys
from pathlib import Path
from typing import Any

import numpy as np

from stage4g_gtr_common import (
    BOOTSTRAP_ITERATIONS,
    BOOTSTRAP_SEED,
    DATASETS,
    MAX_NEW_TOKENS,
    METHODS,
    RERUN_SALT,
    RERUN_SUBSET_PER_DATASET,
    SCHEMA_VERSION,
    SYSTEM_MESSAGE,
    TOKEN_CAP,
    assert_identity,
    assert_implementation_binding,
    file_identity,
    id_digest,
    load_json,
    load_jsonl,
    ranking_digest,
    render_json,
    require_int,
    require_number,
    require_string,
    sha256_bytes,
    sha256_file,
    write_new_files_atomically,
)


ROOT = Path(__file__).resolve().parents[1]


def _path(config: dict[str, Any], key: str) -> Path:
    return Path(require_string(config["paths"].get(key), f"paths.{key}"))


def _load_bound_inputs(config: dict[str, Any]) -> tuple[
    list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, dict[str, str]]]
]:
    queries: list[dict[str, Any]] = []
    rankings: dict[str, dict[str, Any]] = {}
    units: dict[str, dict[str, dict[str, str]]] = {}
    for dataset in DATASETS:
        bound = config["inputs"][dataset]
        blind_path, ranking_path = Path(bound["blind"]["path"]), Path(bound["rankings"]["path"])
        assert_identity(blind_path, bound["blind"], f"{dataset} blind")
        assert_identity(ranking_path, bound["rankings"], f"{dataset} rankings")
        blind_rows, ranking_rows = load_jsonl(blind_path), load_jsonl(ranking_path)
        if len(blind_rows) != bound["query_count"] or len(ranking_rows) != len(blind_rows):
            raise ValueError(f"{dataset} frozen row counts differ")
        for row_index, (blind, ranking) in enumerate(zip(blind_rows, ranking_rows, strict=True)):
            query_id = require_string(blind.get("query_id"), f"{dataset}.blind[{row_index}].query_id")
            sample_id = require_string(blind.get("sample_id"), f"{dataset}.blind[{row_index}].sample_id")
            question = require_string(blind.get("question"), f"{dataset}.blind[{row_index}].question")
            if blind.get("dataset") != dataset or query_id != f"{dataset}::{sample_id}":
                raise ValueError(f"{dataset}.blind[{row_index}] identity differs")
            lower_keys = {str(key).lower() for key in blind}
            if lower_keys.intersection({"answer", "answers", "gold", "method", "label", "labels"}):
                raise ValueError(f"{query_id}: blind row contains prohibited data")
            if ranking.get("dataset") != dataset or ranking.get("query_id") != query_id or ranking.get("sample_id") != sample_id:
                raise ValueError(f"{dataset}.ranking[{row_index}] identity/order differs")
            unit_map: dict[str, dict[str, str]] = {}
            if dataset == DATASETS[0]:
                contexts = blind.get("context")
                if not isinstance(contexts, list) or not contexts:
                    raise ValueError(f"{query_id}: context is missing")
                for context_index, context in enumerate(contexts):
                    if context.get("context_index") != context_index:
                        raise ValueError(f"{query_id}: context order differs")
                    title = require_string(context.get("title"), f"{query_id}.title")
                    sentences = context.get("sentences")
                    if not isinstance(sentences, list):
                        raise ValueError(f"{query_id}: sentences must be a list")
                    for sentence_index, sentence in enumerate(sentences):
                        if not isinstance(sentence, str):
                            raise ValueError(f"{query_id}: sentence must be a string")
                        text = " ".join(sentence.split())
                        if text:
                            unit_id = f"{query_id}::c{context_index}::s{sentence_index}"
                            unit_map[unit_id] = {"unit_id": unit_id, "title": title, "text": text}
            else:
                candidates = blind.get("candidate_units")
                if not isinstance(candidates, list) or not candidates:
                    raise ValueError(f"{query_id}: candidate units are missing")
                for candidate in candidates:
                    unit_id = require_string(candidate.get("unit_id"), f"{query_id}.unit_id")
                    if candidate.get("dataset") != dataset or candidate.get("query_id") != query_id or candidate.get("sample_id") != sample_id:
                        raise ValueError(f"{unit_id}: candidate identity differs")
                    unit_map[unit_id] = {
                        "unit_id": unit_id,
                        "title": require_string(candidate.get("title"), f"{unit_id}.title"),
                        "text": require_string(candidate.get("text"), f"{unit_id}.text"),
                    }
            for key in ("dense_top20_unit_ids", "static_q25_top20_unit_ids"):
                ids = ranking.get(key)
                if not isinstance(ids, list) or not 1 <= len(ids) <= 20 or len(set(ids)) != len(ids):
                    raise ValueError(f"{query_id}.{key} must contain 1..20 unique effective-K IDs")
                if any(not isinstance(value, str) or not value or value not in unit_map for value in ids):
                    raise ValueError(f"{query_id}.{key} violates candidate membership")
            if query_id in rankings:
                raise ValueError(f"Duplicate query: {query_id}")
            queries.append({"dataset": dataset, "query_id": query_id, "question": question, "sample_id": sample_id})
            rankings[query_id] = ranking
            units[query_id] = unit_map
    if len(queries) != 4_000:
        raise ValueError("Stage4G query universe must contain 4,000 rows")
    return queries, rankings, units


def _selected(queries: list[dict[str, Any]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for dataset in DATASETS:
        values = [row["query_id"] for row in queries if row["dataset"] == dataset]
        def key(query_id: str) -> tuple[bytes, str]:
            return hashlib.sha256((RERUN_SALT + dataset + "\0" + query_id).encode("utf-8")).digest(), query_id
        result[dataset] = sorted(values, key=key)[:RERUN_SUBSET_PER_DATASET]
    return result


def _method_order(query_id: str) -> tuple[str, str]:
    return METHODS if (hashlib.sha256(query_id.encode("utf-8")).digest()[0] & 1) == 0 else METHODS[::-1]


def _plan(queries: list[dict[str, Any]], run_id: str) -> list[tuple[dict[str, Any], str]]:
    chosen = {dataset: set(values) for dataset, values in _selected(queries).items()}
    return [
        (query, method)
        for query in queries
        if run_id == "main" or query["query_id"] in chosen[query["dataset"]]
        for method in _method_order(query["query_id"])
    ]


def _validate_snapshot_and_environment(config: dict[str, Any]) -> dict[str, Any]:
    snapshot = _path(config, "generator_snapshot")
    if snapshot.name != config["generator"]["revision"]:
        raise ValueError("Gemma revision path differs")
    files: dict[str, dict[str, Any]] = {}
    for relative, expected in config["generator"]["files"].items():
        path = snapshot / relative
        assert_identity(path, expected, f"Gemma {relative}")
        files[relative] = file_identity(path)
    packages = {
        name: importlib.metadata.version(name)
        for name in config["environment"]["packages"]
    }
    if packages != config["environment"]["packages"]:
        raise ValueError(f"Stage4G package environment differs: {packages}")
    if platform.python_version() != config["environment"]["python"]:
        raise ValueError("Stage4G Python version differs")
    return {
        "generator_files": files,
        "packages": packages,
        "platform": platform.platform(),
        "python": platform.python_version(),
    }


def verify_inputs(config: dict[str, Any]) -> None:
    assert_implementation_binding(config, ROOT)
    queries, _, _ = _load_bound_inputs(config)
    environment = _validate_snapshot_and_environment(config)
    selected = _selected(queries)
    payload = {
        "config": file_identity(_path(config, "config")),
        "datasets": {
            dataset: {
                "blind": file_identity(Path(config["inputs"][dataset]["blind"]["path"])),
                "query_count": sum(row["dataset"] == dataset for row in queries),
                "query_id_sha256": id_digest(row["query_id"] for row in queries if row["dataset"] == dataset),
                "rankings": file_identity(Path(config["inputs"][dataset]["rankings"]["path"])),
            }
            for dataset in DATASETS
        },
        "determinism": {
            "contract": "B_FULL_MAIN_PLUS_PREHASH_STRATIFIED_SUBSET_RERUN",
            "evidence_level": "LOWER_THAN_FULL_RERUN",
            "rerun_query_ids": selected,
            "rerun_query_id_sha256": {dataset: id_digest(values) for dataset, values in selected.items()},
            "rerun_queries_per_dataset": RERUN_SUBSET_PER_DATASET,
            "selection_uses_gold": False,
        },
        "environment": environment,
        "generator": {
            "model_id": config["generator"]["model_id"],
            "revision": config["generator"]["revision"],
            "runtime_format": config["generator"]["runtime_format"],
            "thinking": "disabled",
        },
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4G_GTR_INPUT_MODEL_BINDING_VERIFIED_NO_GOLD_OPENED",
    }
    write_new_files_atomically([(_path(config, "input_model_manifest"), render_json(payload))])
    print("STAGE4G_GTR_INPUT_MODEL_BINDING_VERIFIED_NO_GOLD_OPENED")


def _messages(question: str, lines: list[str]) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": f"Evidence:\n{'\n'.join(lines)}\n\nQuestion: {question}\nFinal answer:"},
    ]


def _template(frontend: Any, messages: list[dict[str, str]], *, tokenize: bool) -> Any:
    kwargs: dict[str, Any] = {"tokenize": tokenize, "add_generation_prompt": True, "enable_thinking": False}
    if tokenize:
        kwargs.update(return_dict=True, return_tensors="pt")
    return frontend.apply_chat_template(messages, **kwargs)


def _token_ids(frontend: Any, messages: list[dict[str, str]]) -> list[int]:
    values = _template(frontend, messages, tokenize=True)["input_ids"].tolist()
    if values and isinstance(values[0], list):
        values = values[0]
    return [int(value) for value in values]


def _semantic_digest(question: str, included: list[dict[str, str]], lines: list[str]) -> str:
    payload = {
        "evidence": [
            {"rendered": line, "text": unit["text"], "title": unit["title"], "unit_id": unit["unit_id"]}
            for unit, line in zip(included, lines, strict=True)
        ],
        "question": question,
        "system": SYSTEM_MESSAGE,
        "user_contract": "Evidence:<ranked units>\\n\\nQuestion:<question>\\nFinal answer:",
    }
    if any(key in payload for key in ("gold", "answer", "method")):
        raise AssertionError("Semantic prompt contains a prohibited key")
    return sha256_bytes(render_json(payload))


def _prompt(frontend: Any, question: str, ranked: list[dict[str, str]]) -> dict[str, Any]:
    if len(_token_ids(frontend, _messages(question, []))) > TOKEN_CAP:
        raise ValueError("Template alone exceeds token cap")
    full_lines = [f"[{rank}] {unit['title']}: {unit['text']}" for rank, unit in enumerate(ranked, start=1)]
    full_count = len(_token_ids(frontend, _messages(question, full_lines)))
    if full_count <= TOKEN_CAP:
        return {
            "evidence_unit_ids": [unit["unit_id"] for unit in ranked],
            "input_token_count": full_count,
            "prompt_semantic_content_sha256": _semantic_digest(question, ranked, full_lines),
            "rank1_truncated": False,
        }
    lines: list[str] = []
    included: list[dict[str, str]] = []
    truncated = False
    for rank, unit in enumerate(ranked, start=1):
        line = f"[{rank}] {unit['title']}: {unit['text']}"
        if len(_token_ids(frontend, _messages(question, lines + [line]))) <= TOKEN_CAP:
            lines.append(line)
            included.append(unit)
            continue
        if rank > 1:
            break
        tokens = list(frontend.tokenizer.encode(line, add_special_tokens=False))
        for kept in range(len(tokens), -1, -1):
            shortened = frontend.tokenizer.decode(tokens[:kept], skip_special_tokens=True, clean_up_tokenization_spaces=False)
            if len(_token_ids(frontend, _messages(question, [shortened]))) <= TOKEN_CAP:
                lines, included, truncated = [shortened], [unit], True
                break
        if not lines:
            raise ValueError("Rank-1 evidence cannot fit")
        break
    return {
        "evidence_unit_ids": [unit["unit_id"] for unit in included],
        "input_token_count": len(_token_ids(frontend, _messages(question, lines))),
        "prompt_semantic_content_sha256": _semantic_digest(question, included, lines),
        "rank1_truncated": truncated,
    }


def _validate_rows(
    config: dict[str, Any],
    frontend: Any,
    queries: list[dict[str, Any]],
    rankings: dict[str, dict[str, Any]],
    units: dict[str, dict[str, dict[str, str]]],
    run_id: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    predictions = load_jsonl(_path(config, f"predictions_{run_id}"))
    audits = load_jsonl(_path(config, f"prompt_audit_{run_id}"))
    plan = _plan(queries, run_id)
    if len(predictions) != len(plan) or len(audits) != len(plan):
        raise ValueError(f"{run_id}: output count differs")
    prediction_keys = {"dataset", "method", "prediction", "query_id", "sample_id"}
    audit_keys = {
        "completion_token_ids", "dataset", "evidence_unit_ids", "input_token_count", "method",
        "prediction", "prompt_semantic_content_sha256", "query_id", "rank1_truncated",
        "ranking_source_sha256", "ranking_unit_ids_sha256", "sample_id",
    }
    for index, ((query, method), prediction, audit) in enumerate(zip(plan, predictions, audits, strict=True)):
        if set(prediction) != prediction_keys or set(audit) != audit_keys:
            raise ValueError(f"{run_id}[{index}] key contract differs")
        identity = (query["dataset"], query["query_id"], query["sample_id"], method)
        if (prediction["dataset"], prediction["query_id"], prediction["sample_id"], prediction["method"]) != identity:
            raise ValueError(f"{run_id}[{index}] prediction identity differs")
        if (audit["dataset"], audit["query_id"], audit["sample_id"], audit["method"]) != identity:
            raise ValueError(f"{run_id}[{index}] audit identity differs")
        require_string(prediction["prediction"], f"{run_id}[{index}].prediction", nonempty=False)
        if audit["prediction"] != prediction["prediction"]:
            raise ValueError(f"{run_id}[{index}] audit prediction differs")
        completion = audit["completion_token_ids"]
        if not isinstance(completion, list) or len(completion) > MAX_NEW_TOKENS:
            raise ValueError(f"{run_id}[{index}] completion token list differs")
        for token_index, token in enumerate(completion):
            require_int(token, f"{run_id}[{index}].completion[{token_index}]", minimum=0)
        decoded = frontend.decode(completion, skip_special_tokens=True).strip()
        if decoded != prediction["prediction"]:
            raise ValueError(f"{run_id}[{index}] completion tokens do not decode to prediction")
        key = "dense_top20_unit_ids" if method == METHODS[0] else "static_q25_top20_unit_ids"
        ranking_ids = rankings[query["query_id"]][key]
        ranked = [units[query["query_id"]][unit_id] for unit_id in ranking_ids]
        expected = _prompt(frontend, query["question"], ranked)
        if any(audit[name] != expected[name] for name in expected):
            raise ValueError(f"{run_id}[{index}] prompt reconstruction differs")
        if audit["ranking_source_sha256"] != config["inputs"][query["dataset"]]["rankings"]["sha256"]:
            raise ValueError(f"{run_id}[{index}] ranking source identity differs")
        if audit["ranking_unit_ids_sha256"] != ranking_digest(ranking_ids):
            raise ValueError(f"{run_id}[{index}] ranking list identity differs")
        if audit["evidence_unit_ids"] != ranking_ids[: len(audit["evidence_unit_ids"])]:
            raise ValueError(f"{run_id}[{index}] evidence is not a ranking prefix")
        if audit["input_token_count"] > TOKEN_CAP or not isinstance(audit["rank1_truncated"], bool):
            raise ValueError(f"{run_id}[{index}] token/truncation contract differs")
    return predictions, audits


def _validate_telemetry(config: dict[str, Any], run_id: str, expected_calls: int) -> dict[str, Any]:
    telemetry = load_json(_path(config, f"telemetry_{run_id}"))
    if telemetry.get("run_id") != run_id or telemetry.get("generation_calls") != expected_calls or telemetry.get("failed_calls") != 0:
        raise ValueError(f"{run_id} telemetry call contract differs")
    if telemetry.get("cuda_devices") != ["cuda:0"] or telemetry.get("runtime_format") != config["generator"]["runtime_format"]:
        raise ValueError(f"{run_id} telemetry device/runtime differs")
    if telemetry.get("python") != config["environment"]["python"] or telemetry.get("gpu_name") != config["environment"]["gpu_name"]:
        raise ValueError(f"{run_id} telemetry Python/GPU differs")
    require_number(telemetry.get("wall_time_seconds"), f"{run_id}.wall_time", minimum=0)
    require_int(telemetry.get("gpu_peak_memory_bytes"), f"{run_id}.gpu_peak", minimum=0)
    return telemetry


def verify_pregold(config: dict[str, Any]) -> None:
    manifest = load_json(_path(config, "input_model_manifest"))
    if manifest.get("status") != "STAGE4G_GTR_INPUT_MODEL_BINDING_VERIFIED_NO_GOLD_OPENED":
        raise ValueError("Input/model binding is not verified")
    queries, rankings, units = _load_bound_inputs(config)
    _validate_snapshot_and_environment(config)
    from transformers import AutoProcessor
    frontend = AutoProcessor.from_pretrained(_path(config, "generator_snapshot"), local_files_only=True)
    main_predictions, main_audits = _validate_rows(config, frontend, queries, rankings, units, "main")
    rerun_predictions, rerun_audits = _validate_rows(config, frontend, queries, rankings, units, "rerun_subset")
    main_map = {(row["query_id"], row["method"]): row for row in main_predictions}
    main_audit_map = {(row["query_id"], row["method"]): row for row in main_audits}
    for prediction, audit in zip(rerun_predictions, rerun_audits, strict=True):
        key = prediction["query_id"], prediction["method"]
        if prediction != main_map[key] or audit != main_audit_map[key]:
            raise ValueError(f"Determinism subset mismatch: {key}")
    _validate_telemetry(config, "main", 8_000)
    _validate_telemetry(config, "rerun_subset", 400)
    payload = {
        "artifacts": {
            key: file_identity(_path(config, key))
            for key in (
                "predictions_main", "predictions_rerun_subset", "prompt_audit_main",
                "prompt_audit_rerun_subset", "telemetry_main", "telemetry_rerun_subset",
            )
        },
        "determinism": {
            "contract": "B_FULL_MAIN_PLUS_PREHASH_STRATIFIED_SUBSET_RERUN",
            "main_calls": 8_000,
            "rerun_subset_calls": 400,
            "subset_prediction_and_audit_exact_match": True,
            "verification_level": "STRATIFIED_SUBSET_NOT_FULL_RERUN",
        },
        "gold_opened": False,
        "prompt_contract": {
            "completion_tokens_verified": True,
            "gold_or_method_inside_prompt": False,
            "ranking_prefixes_verified": True,
            "semantic_content_reconstructed": True,
        },
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4G_GTR_PRE_GOLD_VERIFIED",
    }
    write_new_files_atomically([(_path(config, "verified_pregold"), render_json(payload))])
    print("STAGE4G_GTR_PRE_GOLD_VERIFIED")


def _normalize(value: str) -> str:
    value = value.lower()
    value = "".join(character for character in value if character not in set(string.punctuation))
    value = re.sub(r"\b(a|an|the)\b", " ", value, flags=re.UNICODE)
    return " ".join(value.split())


def _score(dataset: str, prediction: str, answers: list[str]) -> tuple[float, float]:
    exacts: list[float] = []
    f1s: list[float] = []
    for answer in answers:
        p, a = _normalize(prediction), _normalize(answer)
        exacts.append(float(p == a))
        if dataset == DATASETS[0] and ((p in {"yes", "no", "noanswer"} and p != a) or (a in {"yes", "no", "noanswer"} and p != a)):
            f1s.append(0.0)
            continue
        p_tokens, a_tokens = p.split(), a.split()
        same = sum((collections.Counter(p_tokens) & collections.Counter(a_tokens)).values())
        if not p_tokens or not a_tokens:
            f1s.append(float(p_tokens == a_tokens))
        elif same == 0:
            f1s.append(0.0)
        else:
            precision, recall = same / len(p_tokens), same / len(a_tokens)
            f1s.append(2 * precision * recall / (precision + recall))
    return max(exacts), max(f1s)


def _bootstrap(delta: np.ndarray) -> dict[str, float]:
    rng = np.random.Generator(np.random.PCG64(BOOTSTRAP_SEED))
    draws = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    for index in range(BOOTSTRAP_ITERATIONS):
        draw = rng.integers(0, len(delta), size=len(delta))
        draws[index] = float(np.mean(delta[draw]))
    lower, upper = np.percentile(draws, [2.5, 97.5], method="linear")
    return {"lower_95": float(lower), "point": float(np.mean(delta)), "upper_95": float(upper)}


def _stratified(hotpot: np.ndarray, musique: np.ndarray) -> dict[str, float]:
    rng = np.random.Generator(np.random.PCG64(BOOTSTRAP_SEED))
    draws = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    for index in range(BOOTSTRAP_ITERATIONS):
        h = rng.integers(0, len(hotpot), size=len(hotpot))
        m = rng.integers(0, len(musique), size=len(musique))
        draws[index] = (float(np.mean(hotpot[h])) + float(np.mean(musique[m]))) / 2
    lower, upper = np.percentile(draws, [2.5, 97.5], method="linear")
    return {"lower_95": float(lower), "point": (float(np.mean(hotpot)) + float(np.mean(musique))) / 2, "upper_95": float(upper)}


def _assert_close(actual: Any, expected: Any, label: str) -> None:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            raise ValueError(f"{label} must be an object")
        for key, value in expected.items():
            if key not in actual:
                raise ValueError(f"{label}.{key} is missing")
            _assert_close(actual[key], value, f"{label}.{key}")
    elif isinstance(expected, float):
        if not isinstance(actual, (int, float)) or isinstance(actual, bool) or not math.isclose(float(actual), expected, rel_tol=0, abs_tol=1e-15):
            raise ValueError(f"{label} differs: actual={actual}, expected={expected}")
    elif actual != expected:
        raise ValueError(f"{label} differs: actual={actual}, expected={expected}")


def _decision(dataset_summaries: dict[str, Any], pooled: dict[str, Any]) -> str:
    h, m = dataset_summaries[DATASETS[0]]["bootstrap"], dataset_summaries[DATASETS[1]]["bootstrap"]
    f1, em = pooled["delta_answer_f1"], pooled["delta_answer_em"]
    if f1["point"] >= .010 and f1["lower_95"] > 0 and h["delta_answer_f1"]["point"] > 0 and m["delta_answer_f1"]["point"] > 0 and em["lower_95"] >= -.010 and h["delta_answer_em"]["upper_95"] >= -.010 and m["delta_answer_em"]["upper_95"] >= -.010:
        return "GENERATOR_TRANSFER_SUPPORTED"
    if f1["upper_95"] < 0 or h["delta_answer_f1"]["upper_95"] < 0 or m["delta_answer_f1"]["upper_95"] < 0 or em["upper_95"] < -.010 or h["delta_answer_em"]["upper_95"] < -.010 or m["delta_answer_em"]["upper_95"] < -.010:
        return "GENERATOR_TRANSFER_NEGATIVE"
    return "GENERATOR_TRANSFER_INCONCLUSIVE"


def verify_postgold(config: dict[str, Any]) -> None:
    verified_pregold = load_json(_path(config, "verified_pregold"))
    if verified_pregold.get("status") != "STAGE4G_GTR_PRE_GOLD_VERIFIED":
        raise ValueError("Pre-Gold verification is absent")
    for key in (
        "predictions_main", "predictions_rerun_subset", "prompt_audit_main",
        "prompt_audit_rerun_subset", "telemetry_main", "telemetry_rerun_subset",
    ):
        if verified_pregold["artifacts"].get(key) != file_identity(_path(config, key)):
            raise ValueError(f"{key} changed after pre-Gold verification")
    predictions = {(row["query_id"], row["method"]): row for row in load_jsonl(_path(config, "predictions_main"))}
    score_rows = load_jsonl(_path(config, "query_scores"))
    if len(score_rows) != 4_000:
        raise ValueError("Stage4G query score count differs")
    gold: dict[str, tuple[str, str, list[str]]] = {}
    qwen: dict[str, dict[str, tuple[float, float]]] = {}
    for dataset in DATASETS:
        gold_bound = config["inputs"][dataset]["gold"]
        gold_path = Path(gold_bound["path"])
        assert_identity(gold_path, gold_bound, f"{dataset} Gold")
        for row in load_jsonl(gold_path):
            answers = [row["answer"]] if dataset == DATASETS[0] else row["answers"]
            gold[row["query_id"]] = (dataset, row["sample_id"], answers)
        qwen_bound = config["inputs"][dataset]["qwen_query_audit"]
        qwen_path = Path(qwen_bound["path"])
        assert_identity(qwen_path, qwen_bound, f"{dataset} Qwen audit")
        qwen[dataset] = {}
        for row in load_jsonl(qwen_path):
            dense, q25 = (row["dense"], row["static_q25"]) if dataset == DATASETS[0] else (row["dense_top20"], row["static_q25_top20"])
            qwen[dataset][row["query_id"]] = (
                float(q25["answer_f1"]) - float(dense["answer_f1"]),
                float(q25["answer_em"]) - float(dense["answer_em"]),
            )
        if len(qwen[dataset]) != config["inputs"][dataset]["query_count"]:
            raise ValueError(f"{dataset} frozen Qwen audit count differs")
    deltas: dict[str, dict[str, list[float]]] = {dataset: {"f1": [], "em": [], "if1": [], "iem": []} for dataset in DATASETS}
    seen: set[str] = set()
    for row_index, row in enumerate(score_rows):
        if set(row) != {"dataset", "methods", "query_id", "sample_id"}:
            raise ValueError(f"scores[{row_index}] key contract differs")
        query_id = require_string(row.get("query_id"), f"scores[{row_index}].query_id")
        if query_id in seen or query_id not in gold:
            raise ValueError(f"scores[{row_index}] identity differs")
        seen.add(query_id)
        dataset, sample_id, answers = gold[query_id]
        if row.get("dataset") != dataset or row.get("sample_id") != sample_id or set(row.get("methods", {})) != set(METHODS):
            raise ValueError(f"scores[{row_index}] row contract differs")
        values: dict[str, tuple[float, float]] = {}
        for method in METHODS:
            prediction = predictions[(query_id, method)]["prediction"]
            em, f1 = _score(dataset, prediction, answers)
            expected = {"answer_em": em, "answer_f1": f1, "prediction": prediction}
            _assert_close(row["methods"][method], expected, f"scores[{row_index}].{method}")
            values[method] = f1, em
        f1_delta = values[METHODS[1]][0] - values[METHODS[0]][0]
        em_delta = values[METHODS[1]][1] - values[METHODS[0]][1]
        deltas[dataset]["f1"].append(f1_delta)
        deltas[dataset]["em"].append(em_delta)
        deltas[dataset]["if1"].append(f1_delta - qwen[dataset][query_id][0])
        deltas[dataset]["iem"].append(em_delta - qwen[dataset][query_id][1])
    if set(gold) != seen:
        raise ValueError("Stage4G score universe is incomplete")
    dataset_payload = load_json(_path(config, "dataset_summaries"))
    expected_dataset_bootstrap: dict[str, Any] = {}
    arrays: dict[str, dict[str, np.ndarray]] = {}
    for dataset in DATASETS:
        arrays[dataset] = {key: np.asarray(value, dtype="float64") for key, value in deltas[dataset].items()}
        expected = {
            "delta_answer_em": _bootstrap(arrays[dataset]["em"]),
            "delta_answer_f1": _bootstrap(arrays[dataset]["f1"]),
            "iterations": BOOTSTRAP_ITERATIONS,
            "numpy_generator": "PCG64",
            "percentile_method": "linear",
            "seed": BOOTSTRAP_SEED,
        }
        _assert_close(dataset_payload["datasets"][dataset]["bootstrap"], expected, f"dataset.{dataset}.bootstrap")
        _assert_close(dataset_payload["datasets"][dataset]["generator_interaction"]["answer_f1"], _bootstrap(arrays[dataset]["if1"]), f"dataset.{dataset}.interaction.f1")
        _assert_close(dataset_payload["datasets"][dataset]["generator_interaction"]["answer_em"], _bootstrap(arrays[dataset]["iem"]), f"dataset.{dataset}.interaction.em")
        expected_dataset_bootstrap[dataset] = {"bootstrap": expected}
    equal = load_json(_path(config, "equal_weight_summary"))
    expected_pooled = {
        "delta_answer_f1": _stratified(arrays[DATASETS[0]]["f1"], arrays[DATASETS[1]]["f1"]),
        "delta_answer_em": _stratified(arrays[DATASETS[0]]["em"], arrays[DATASETS[1]]["em"]),
    }
    _assert_close(equal["bootstrap"], expected_pooled, "equal_weight.bootstrap")
    _assert_close(equal["generator_interaction"]["answer_f1"], _stratified(arrays[DATASETS[0]]["if1"], arrays[DATASETS[1]]["if1"]), "equal_weight.interaction.f1")
    _assert_close(equal["generator_interaction"]["answer_em"], _stratified(arrays[DATASETS[0]]["iem"], arrays[DATASETS[1]]["iem"]), "equal_weight.interaction.em")
    decision = _decision(expected_dataset_bootstrap, expected_pooled)
    decision_payload = load_json(_path(config, "scientific_decision"))
    if decision_payload.get("decision") != decision or decision_payload.get("scope") != "ONE_ADDITIONAL_PRE_SPECIFIED_GENERATOR_CONFIGURATION":
        raise ValueError("Stage4G scientific decision/scope differs")
    payload = {
        "artifacts": {
            key: file_identity(_path(config, key))
            for key in (
                "input_model_manifest", "verified_pregold", "query_scores", "dataset_summaries",
                "equal_weight_summary", "scientific_decision",
            )
        },
        "bootstrap_reconstructed": True,
        "decision": decision,
        "gold_identity_and_pairing_verified": True,
        "generator_interaction_reconstructed": True,
        "locks": config["locks"],
        "query_scores_reconstructed": 4_000,
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4G_GTR_FINAL_VERIFICATION_PASS",
    }
    write_new_files_atomically([(_path(config, "final_verification"), render_json(payload))])
    print(f"STAGE4G_GTR_FINAL_VERIFICATION_PASS decision={decision}")


def write_manifest(config: dict[str, Any]) -> None:
    if load_json(_path(config, "final_verification")).get("status") != "STAGE4G_GTR_FINAL_VERIFICATION_PASS":
        raise ValueError("Final verification must pass before manifest promotion")
    artifact_keys = [
        "input_model_manifest", "predictions_main", "predictions_rerun_subset", "prompt_audit_main",
        "prompt_audit_rerun_subset", "telemetry_main", "telemetry_rerun_subset", "verified_pregold",
        "query_scores", "dataset_summaries", "equal_weight_summary", "scientific_decision", "final_verification",
    ]
    payload = {
        "artifacts": {key: {"path": str(_path(config, key)), **file_identity(_path(config, key))} for key in artifact_keys},
        "artifact_count": len(artifact_keys),
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4G_GTR_ARTIFACT_MANIFEST_FROZEN",
    }
    write_new_files_atomically([(_path(config, "artifact_manifest"), render_json(payload))])
    print("STAGE4G_GTR_ARTIFACT_MANIFEST_FROZEN")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify-inputs", "verify-pregold", "verify-postgold", "write-manifest"))
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config = load_json(args.config)
    if args.command == "verify-inputs":
        verify_inputs(config)
    elif args.command == "verify-pregold":
        verify_pregold(config)
    elif args.command == "verify-postgold":
        verify_postgold(config)
    else:
        write_manifest(config)


if __name__ == "__main__":
    main()
