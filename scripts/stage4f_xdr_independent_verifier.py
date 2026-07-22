"""Independent source, artifact, and scientific verification for Stage4F-XDR."""

from __future__ import annotations

import argparse
import collections
import json
import re
import string
import sys
from pathlib import Path
from typing import Any

import numpy as np

from stage4f_xdr_common import (
    BOOTSTRAP_ITERATIONS,
    BOOTSTRAP_SEED,
    DATASET,
    ENCODER_ID,
    ENCODER_REVISION,
    GENERATOR_ID,
    GENERATOR_REVISION,
    SAMPLE_SIZE,
    SCHEMA_VERSION,
    SOURCE_BYTES,
    SOURCE_SHA256,
    SOURCE_ZIP_BYTES,
    SOURCE_ZIP_SHA256,
    assert_file_identity,
    assert_implementation_binding,
    assert_no_gold_fields,
    file_identity,
    id_digest,
    load_json,
    load_jsonl,
    render_json,
    render_jsonl,
    require_finite_number,
    require_json_bool,
    require_json_int,
    require_native_string,
    selection_key,
    split_sentences,
    validate_sha256,
    write_new_files_atomically,
)
from stage4f_xdr_retrieval import RetrievalConfig, build_query_decisions, dot


METHODS = ("DENSE_TOP20", "STATIC_Q25_TOP20")
PREGOLD_ARTIFACT_KEYS = (
    "embedding_cache", "rankings", "predictions_main", "predictions_rerun",
    "prompt_audit_main", "prompt_audit_rerun",
)
OFFICIAL_OUTPUT_KEYS = (
    "embedding_cache", "rankings", "predictions_main", "predictions_rerun",
    "prompt_audit_main", "prompt_audit_rerun", "telemetry_main", "telemetry_rerun",
    "query_audit", "evaluation_summary", "scientific_decision", "descriptive_subgroups",
    "verified_pregold", "final_verification",
)


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


def _load_history(path: Path) -> list[dict[str, Any]]:
    value = load_json(path) if path.suffix.lower() == ".json" else load_jsonl(path)
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise ValueError("Historical input schema differs")
    return value


def _historical_ids(config: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    values = config.get("historical_inputs")
    if not isinstance(values, list) or not values:
        raise ValueError("historical_inputs binding is missing")
    for index, item in enumerate(values):
        if not isinstance(item, dict):
            raise ValueError("historical_inputs row differs")
        path = Path(require_native_string(item.get("path"), f"historical_inputs[{index}].path"))
        assert_file_identity(path, item, f"historical_inputs[{index}]")
        for row in _load_history(path):
            if row.get("dataset") == "musique":
                result.add(require_native_string(row.get("id", row.get("sample_id")), "history.id"))
    return result


def _independent_channels(
    source_rows: list[dict[str, Any]], history_ids: set[str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    seen: set[str] = set()
    indexed: list[tuple[int, dict[str, Any]]] = []
    for row_index, row in enumerate(source_rows):
        if not isinstance(row, dict):
            raise ValueError("Source row must be an object")
        native_id = require_native_string(row.get("id"), "source.id")
        require_native_string(row.get("question"), "source.question")
        if native_id in seen:
            raise ValueError("Duplicate source native ID")
        seen.add(native_id)
        paragraphs = row.get("paragraphs")
        if not isinstance(paragraphs, list) or not paragraphs:
            raise ValueError("Source paragraphs are missing")
        for paragraph_index, paragraph in enumerate(paragraphs):
            if not isinstance(paragraph, dict) or require_json_int(paragraph.get("idx"), "paragraph.idx") != paragraph_index:
                raise ValueError("Source paragraph identity/order differs")
            require_native_string(paragraph.get("title"), "paragraph.title")
            split_sentences(paragraph.get("paragraph_text"), "paragraph.text")
        indexed.append((row_index, row))
    selected = sorted(indexed, key=lambda pair: selection_key(pair[1]["id"]))[:SAMPLE_SIZE]
    selected_ids = {row["id"] for _, row in selected}
    if selected_ids & history_ids:
        raise ValueError("Stage4F selected IDs overlap historical MuSiQue IDs")
    blind_rows: list[dict[str, Any]] = []
    gold_rows: list[dict[str, Any]] = []
    metadata_rows: list[dict[str, Any]] = []
    for source_row_index, row in selected:
        native_id = row["id"]
        query_id = f"{DATASET}::{native_id}"
        units: list[dict[str, Any]] = []
        support_indices: list[int] = []
        support_unit_ids: list[str] = []
        for paragraph_index, paragraph in enumerate(row["paragraphs"]):
            sentences = split_sentences(paragraph["paragraph_text"], "paragraph.text")
            paragraph_ids = []
            for sentence_index, text in enumerate(sentences):
                unit_id = f"{query_id}::p{paragraph_index}::s{sentence_index}"
                paragraph_ids.append(unit_id)
                units.append(
                    {
                        "dataset": DATASET, "paragraph_index": paragraph_index,
                        "query_id": query_id, "sample_id": native_id,
                        "sentence_index": sentence_index, "text": text,
                        "title": paragraph["title"], "unit_id": unit_id,
                    }
                )
            flag = require_json_bool(paragraph.get("is_supporting"), "is_supporting")
            if flag:
                if not paragraph_ids:
                    raise ValueError("Supporting paragraph has no candidate units")
                support_indices.append(paragraph_index)
                support_unit_ids.extend(paragraph_ids)
        if len(units) < 21 or not support_indices:
            raise ValueError("Selected candidate/evidence boundary is incompatible")
        decomposition = row.get("question_decomposition")
        if not isinstance(decomposition, list) or not decomposition:
            raise ValueError("Question decomposition is missing")
        decomposition_indices = [
            require_json_int(item.get("paragraph_support_idx"), "paragraph_support_idx")
            for item in decomposition if isinstance(item, dict)
        ]
        if len(decomposition_indices) != len(decomposition) or sorted(set(decomposition_indices)) != sorted(support_indices):
            raise ValueError("Supporting-evidence mapping differs")
        answer = require_native_string(row.get("answer"), "answer")
        aliases = row.get("answer_aliases")
        if not isinstance(aliases, list) or any(not isinstance(value, str) for value in aliases):
            raise ValueError("Answer aliases differ")
        answers = [answer] + [value for value in aliases if value.strip()]
        blind_rows.append(
            {"candidate_units": units, "dataset": DATASET, "query_id": query_id,
             "question": row["question"], "sample_id": native_id}
        )
        gold_rows.append(
            {"answers": answers, "dataset": DATASET, "query_id": query_id,
             "sample_id": native_id, "supporting_paragraph_indices": support_indices,
             "supporting_unit_ids": support_unit_ids}
        )
        metadata_rows.append(
            {"answer_alias_count": len(answers) - 1, "candidate_unit_count": len(units),
             "dataset": DATASET, "hop_count": len(decomposition), "query_id": query_id,
             "sample_id": native_id, "source_row_index": source_row_index,
             "source_split": "train", "supporting_paragraph_count": len(support_indices)}
        )
    assert_no_gold_fields(blind_rows, "independent blind")
    return blind_rows, gold_rows, metadata_rows


def _validate_model_environment(config: dict[str, Any]) -> dict[str, Any]:
    environment_path = _assert_bound(config, "environment_manifest")
    model_path = _assert_bound(config, "model_manifest")
    requirements_path = _assert_bound(config, "requirements")
    environment = load_json(environment_path)
    model_manifest = load_json(model_path)
    models = model_manifest.get("models")
    if not isinstance(models, dict):
        raise ValueError("Model manifest schema differs")
    encoder, generator = models.get("encoder"), models.get("generator")
    if not isinstance(encoder, dict) or not isinstance(generator, dict):
        raise ValueError("Encoder/generator binding is missing")
    if (encoder.get("model_id"), encoder.get("revision")) != (ENCODER_ID, ENCODER_REVISION):
        raise ValueError("Encoder identity differs")
    if (generator.get("model_id"), generator.get("revision")) != (GENERATOR_ID, GENERATOR_REVISION):
        raise ValueError("Generator identity differs")
    for label, model, key in (
        ("encoder", encoder, "encoder_snapshot"),
        ("generator", generator, "generator_snapshot"),
    ):
        snapshot = _path(config, key)
        if str(snapshot.resolve()) != model.get("snapshot_path"):
            raise ValueError(f"{label} snapshot path differs")
        files = model.get("files")
        if not isinstance(files, list) or not files:
            raise ValueError(f"{label} file manifest differs")
        for file_index, row in enumerate(files):
            relative = require_native_string(row.get("path"), f"{label}.files[{file_index}].path")
            assert_file_identity(snapshot / relative, row, f"{label}.files[{file_index}]")
    return {
        "environment_manifest": file_identity(environment_path),
        "model_manifest": file_identity(model_path),
        "requirements": file_identity(requirements_path),
    }


def verify_inputs(config: dict[str, Any]) -> dict[str, Any]:
    source_path = _path(config, "source")
    assert_file_identity(source_path, {"bytes": SOURCE_BYTES, "sha256": SOURCE_SHA256}, "source")
    assert_file_identity(
        _path(config, "source_zip"),
        {"bytes": SOURCE_ZIP_BYTES, "sha256": SOURCE_ZIP_SHA256},
        "source_zip",
    )
    history = _historical_ids(config)
    blind, gold, metadata = _independent_channels(load_jsonl(source_path), history)
    expected = {
        "blind": render_jsonl(blind), "gold": render_jsonl(gold),
        "metadata": render_jsonl(metadata),
    }
    for key, payload in expected.items():
        path = _assert_bound(config, key)
        if path.read_bytes() != payload:
            raise ValueError(f"{key} differs from independent source reconstruction")
    manifest = load_json(_assert_bound(config, "input_manifest"))
    if manifest.get("sample_size") != SAMPLE_SIZE or manifest.get("checks", {}).get("historical_musique_overlap") != 0:
        raise ValueError("Input manifest identity or overlap differs")
    if manifest.get("query_id_sha256") != id_digest(row["query_id"] for row in blind):
        raise ValueError("Input manifest query digest differs")
    model_environment = _validate_model_environment(config)
    present = [key for key in OFFICIAL_OUTPUT_KEYS if _path(config, key).exists()]
    if present:
        raise ValueError(f"Formal Stage4F outputs must be absent before authorization: {present}")
    return {
        "artifacts": {key: file_identity(_path(config, key)) for key in ("blind", "gold", "metadata", "input_manifest")},
        "historical_musique_ids": len(history),
        "historical_overlap": 0,
        "model_environment": model_environment,
        "queries": len(blind),
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4F_INPUT_BOUNDARY_VERIFIED",
    }


def _units_queries(blind: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    assert_no_gold_fields(blind, "blind")
    units: list[dict[str, Any]] = []
    queries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in blind:
        query_id = require_native_string(row.get("query_id"), "blind.query_id")
        candidate_units = row.get("candidate_units")
        if not isinstance(candidate_units, list) or not candidate_units:
            raise ValueError("Blind candidate pool is empty")
        for unit in candidate_units:
            if unit.get("query_id") != query_id or unit.get("unit_id") in seen:
                raise ValueError("Candidate belongs to another query or duplicates")
            seen.add(unit["unit_id"])
            units.append(dict(unit))
        queries.append(
            {"dataset": row["dataset"], "num_candidate_units": len(candidate_units),
             "query_id": query_id, "question": row["question"], "sample_id": row["sample_id"]}
        )
    return units, queries


def _load_embeddings(path: Path, units: list[dict[str, Any]], queries: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
    with np.load(path, allow_pickle=False) as cache:
        if cache["unit_ids"].tolist() != [row["unit_id"] for row in units] or cache["query_ids"].tolist() != [row["query_id"] for row in queries]:
            raise ValueError("Embedding-cache identity/order differs")
        unit_embeddings = np.asarray(cache["unit_embeddings"], dtype="float32")
        query_embeddings = np.asarray(cache["query_embeddings"], dtype="float32")
    return unit_embeddings, query_embeddings


def verify_pregold(config: dict[str, Any]) -> dict[str, Any]:
    blind = load_jsonl(_assert_bound(config, "blind"))
    units, queries = _units_queries(blind)
    unit_embeddings, query_embeddings = _load_embeddings(
        _path(config, "embedding_cache"), units, queries
    )
    decisions = build_query_decisions(
        units, queries, unit_embeddings, query_embeddings, RetrievalConfig()
    )
    expected_rankings = [
        {"dataset": query["dataset"], "dense_top20_unit_ids": decision["dense_top20_unit_ids"],
         "q25_inserted_unit_ids": decision["q25_inserted_unit_ids"], "query_id": query["query_id"],
         "sample_id": query["sample_id"], "static_q25_top20_unit_ids": decision["q25_top20_unit_ids"]}
        for query, decision in zip(queries, decisions, strict=True)
    ]
    rankings_path = _path(config, "rankings")
    if rankings_path.read_bytes() != render_jsonl(expected_rankings):
        raise ValueError("Ranking differs from Gold-free reconstruction")
    predictions_main = _path(config, "predictions_main")
    predictions_rerun = _path(config, "predictions_rerun")
    prompt_main = _path(config, "prompt_audit_main")
    prompt_rerun = _path(config, "prompt_audit_rerun")
    if predictions_main.read_bytes() != predictions_rerun.read_bytes() or prompt_main.read_bytes() != prompt_rerun.read_bytes():
        raise ValueError("Main/rerun bytes differ")
    predictions = load_jsonl(predictions_main)
    prompts = load_jsonl(prompt_main)
    assert_no_gold_fields(expected_rankings, "rankings")
    assert_no_gold_fields(predictions, "predictions")
    assert_no_gold_fields(prompts, "prompt audits")
    expected_pairs = {(row["query_id"], method) for row in queries for method in METHODS}
    if {(row.get("query_id"), row.get("method")) for row in predictions} != expected_pairs:
        raise ValueError("Prediction cross-arm pairing differs")
    if {(row.get("query_id"), row.get("method")) for row in prompts} != expected_pairs:
        raise ValueError("Prompt cross-arm pairing differs")
    return {
        "artifacts": {key: file_identity(_path(config, key)) for key in (
            "embedding_cache", "rankings", "predictions_main", "predictions_rerun",
            "prompt_audit_main", "prompt_audit_rerun")},
        "queries": len(queries), "schema_version": SCHEMA_VERSION,
        "status": "STAGE4F_PRE_GOLD_ARTIFACTS_VERIFIED",
    }


def _normalize(value: str) -> str:
    value = value.lower()
    value = "".join(character for character in value if character not in set(string.punctuation))
    value = re.sub(r"\b(a|an|the)\b", " ", value, flags=re.UNICODE)
    return " ".join(value.split())


def _scores(prediction: str, answers: list[str]) -> tuple[float, float]:
    def one(answer: str) -> tuple[float, float]:
        p, g = _normalize(prediction).split(), _normalize(answer).split()
        em = float(_normalize(prediction) == _normalize(answer))
        common = collections.Counter(p) & collections.Counter(g)
        same = sum(common.values())
        if not p or not g:
            f1 = float(p == g)
        elif same == 0:
            f1 = 0.0
        else:
            precision, recall = same / len(p), same / len(g)
            f1 = 2.0 * precision * recall / (precision + recall)
        return em, f1
    values = [one(answer) for answer in answers]
    return max(value[0] for value in values), max(value[1] for value in values)


def _bootstrap(dense_f1: np.ndarray, q25_f1: np.ndarray, dense_em: np.ndarray, q25_em: np.ndarray) -> dict[str, Any]:
    rng = np.random.Generator(np.random.PCG64(BOOTSTRAP_SEED))
    f1_delta, em_delta = q25_f1 - dense_f1, q25_em - dense_em
    f1_samples = np.empty(BOOTSTRAP_ITERATIONS)
    em_samples = np.empty(BOOTSTRAP_ITERATIONS)
    for index in range(BOOTSTRAP_ITERATIONS):
        sample = rng.integers(0, f1_delta.size, size=f1_delta.size)
        f1_samples[index], em_samples[index] = np.mean(f1_delta[sample]), np.mean(em_delta[sample])
    def row(point: float, samples: np.ndarray) -> dict[str, float]:
        lower, upper = np.percentile(samples, [2.5, 97.5], method="linear")
        return {"lower_95": float(lower), "point": float(point), "upper_95": float(upper)}
    return {"delta_answer_em": row(float(np.mean(em_delta)), em_samples),
            "delta_answer_f1": row(float(np.mean(f1_delta)), f1_samples),
            "iterations": BOOTSTRAP_ITERATIONS, "numpy_generator": "PCG64",
            "percentile_method": "linear", "seed": BOOTSTRAP_SEED}


def _decision(bootstrap: dict[str, Any]) -> str:
    f1, em = bootstrap["delta_answer_f1"], bootstrap["delta_answer_em"]
    if f1["point"] >= .010 and f1["lower_95"] > 0 and em["lower_95"] >= -.010:
        return "STATIC_HGRAG_XDR_SUPPORTED"
    if f1["upper_95"] < 0 or em["upper_95"] < -.010:
        return "STATIC_HGRAG_XDR_NEGATIVE"
    return "STATIC_HGRAG_XDR_INCONCLUSIVE"


def _paragraph_indices(unit_ids: list[str], label: str) -> set[int]:
    result: set[int] = set()
    for index, unit_id in enumerate(unit_ids):
        unit_id = require_native_string(unit_id, f"{label}[{index}]")
        match = re.search(r"::p(\d+)::s\d+$", unit_id)
        if match is None:
            raise ValueError(f"{label}[{index}] unit ID schema differs")
        result.add(int(match.group(1)))
    return result


def _validate_telemetry_row(
    row: dict[str, Any], run_id: str, embedding_identity: dict[str, Any]
) -> None:
    expected_keys = {
        "embedding_cache", "failed_calls", "generation_calls",
        "gpu_peak_memory_bytes", "run_id", "schema_version", "status",
        "wall_time_seconds",
    }
    if not isinstance(row, dict) or set(row) != expected_keys:
        raise ValueError(f"{run_id} telemetry schema differs")
    if row["run_id"] != run_id or row["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"{run_id} telemetry identity differs")
    if row["status"] != "STAGE4F_GOLDFREE_RUN_COMPLETE_PENDING_VERIFICATION":
        raise ValueError(f"{run_id} telemetry status differs")
    if row["embedding_cache"] != embedding_identity:
        raise ValueError(f"{run_id} embedding-cache identity differs")
    if require_json_int(row["generation_calls"], f"{run_id}.generation_calls") != SAMPLE_SIZE * len(METHODS):
        raise ValueError(f"{run_id} generation call count differs")
    if require_json_int(row["failed_calls"], f"{run_id}.failed_calls") != 0:
        raise ValueError(f"{run_id} reports failed generation calls")
    if require_json_int(row["gpu_peak_memory_bytes"], f"{run_id}.gpu_peak_memory_bytes") <= 0:
        raise ValueError(f"{run_id} GPU peak memory must be positive")
    if require_finite_number(row["wall_time_seconds"], f"{run_id}.wall_time_seconds") <= 0:
        raise ValueError(f"{run_id} wall time must be positive")


def _pair_index(
    rows: list[dict[str, Any]],
    identities: dict[str, tuple[str, str]],
    label: str,
    expected_keys: set[str],
) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != expected_keys:
            raise ValueError(f"{label}[{index}] schema differs")
        query_id = require_native_string(row["query_id"], f"{label}[{index}].query_id")
        method = require_native_string(row["method"], f"{label}[{index}].method")
        dataset = require_native_string(row["dataset"], f"{label}[{index}].dataset")
        sample_id = require_native_string(row["sample_id"], f"{label}[{index}].sample_id")
        if method not in METHODS or identities.get(query_id) != (dataset, sample_id):
            raise ValueError(f"{label}[{index}] row identity differs")
        key = (query_id, method)
        if key in result:
            raise ValueError(f"{label} pair identities duplicate")
        result[key] = row
    expected = {(query_id, method) for query_id in identities for method in METHODS}
    if set(result) != expected:
        raise ValueError(f"{label} must pair every query across both arms")
    return result


def _validate_prompt_contract(
    row: dict[str, Any], ranked_ids: list[str], token_cap: int, label: str
) -> None:
    evidence = row["evidence_unit_ids"]
    if not isinstance(evidence, list) or not evidence:
        raise ValueError(f"{label}.evidence_unit_ids must be non-empty")
    evidence = [
        require_native_string(value, f"{label}.evidence_unit_ids[{index}]")
        for index, value in enumerate(evidence)
    ]
    if evidence != ranked_ids[: len(evidence)]:
        raise ValueError(f"{label} evidence is not the frozen ranking prefix")
    token_count = require_json_int(row["input_token_count"], f"{label}.input_token_count")
    if token_count <= 0 or token_count > token_cap:
        raise ValueError(f"{label} input token cap differs")
    require_json_bool(row["rank1_truncated"], f"{label}.rank1_truncated")
    validate_sha256(row["prompt_sha256"], f"{label}.prompt_sha256")


def _verify_frozen_boundaries(config: dict[str, Any]) -> dict[str, Any]:
    source_path = _assert_bound(config, "source")
    source_zip_path = _assert_bound(config, "source_zip")
    history = _historical_ids(config)
    blind, gold, metadata = _independent_channels(load_jsonl(source_path), history)
    for key, rows in (("blind", blind), ("gold", gold), ("metadata", metadata)):
        path = _assert_bound(config, key)
        if path.read_bytes() != render_jsonl(rows):
            raise ValueError(f"{key} differs from independent source reconstruction")
    manifest_path = _assert_bound(config, "input_manifest")
    verified_input_path = _assert_bound(config, "verified_input")
    verified_input = load_json(verified_input_path)
    if verified_input.get("status") != "STAGE4F_INPUT_BOUNDARY_VERIFIED":
        raise ValueError("Verified input status differs")
    return {
        "channels": {
            key: file_identity(_path(config, key))
            for key in ("blind", "gold", "metadata", "input_manifest", "verified_input")
        },
        "historical_overlap": len({row["sample_id"] for row in blind} & history),
        "model_environment": _validate_model_environment(config),
        "source": file_identity(source_path),
        "source_zip": file_identity(source_zip_path),
    }


def verify_postgold(config: dict[str, Any]) -> dict[str, Any]:
    if require_json_bool(config.get("official_execution", {}).get("authorized"), "official_execution.authorized") is not True:
        raise PermissionError("STAGE4F_OFFICIAL_EXECUTION_NOT_AUTHORIZED")
    if require_json_bool(config.get("gold_evaluation", {}).get("authorized"), "gold_evaluation.authorized") is not True:
        raise PermissionError("STAGE4F_GOLD_EVALUATION_NOT_AUTHORIZED")
    frozen_boundaries = _verify_frozen_boundaries(config)
    pregold_path = _require_artifact(config, "verified_pregold")
    pregold = load_json(pregold_path)
    if pregold.get("status") != "STAGE4F_PRE_GOLD_ARTIFACTS_VERIFIED":
        raise ValueError("Pre-Gold verifier status differs")
    if set(pregold.get("artifacts", {})) != set(PREGOLD_ARTIFACT_KEYS):
        raise ValueError("Pre-Gold artifact manifest differs")
    for key in PREGOLD_ARTIFACT_KEYS:
        if pregold["artifacts"][key] != file_identity(_require_artifact(config, key)):
            raise ValueError(f"Pre-Gold artifact identity changed: {key}")

    predictions_main_path = _require_artifact(config, "predictions_main")
    predictions_rerun_path = _require_artifact(config, "predictions_rerun")
    prompt_main_path = _require_artifact(config, "prompt_audit_main")
    prompt_rerun_path = _require_artifact(config, "prompt_audit_rerun")
    if predictions_main_path.read_bytes() != predictions_rerun_path.read_bytes():
        raise ValueError("Main/rerun prediction bytes differ")
    if prompt_main_path.read_bytes() != prompt_rerun_path.read_bytes():
        raise ValueError("Main/rerun prompt-audit bytes differ")
    embedding_identity = file_identity(_require_artifact(config, "embedding_cache"))
    for run_id in ("main", "rerun"):
        _validate_telemetry_row(
            load_json(_require_artifact(config, f"telemetry_{run_id}")),
            run_id,
            embedding_identity,
        )

    gold = load_jsonl(_assert_bound(config, "gold"))
    if len(gold) != SAMPLE_SIZE:
        raise ValueError("Official Stage4F Gold query count differs")
    identities: dict[str, tuple[str, str]] = {}
    for index, row in enumerate(gold):
        expected_keys = {
            "answers", "dataset", "query_id", "sample_id",
            "supporting_paragraph_indices", "supporting_unit_ids",
        }
        if set(row) != expected_keys:
            raise ValueError(f"gold[{index}] schema differs")
        dataset = require_native_string(row["dataset"], f"gold[{index}].dataset")
        query_id = require_native_string(row["query_id"], f"gold[{index}].query_id")
        sample_id = require_native_string(row["sample_id"], f"gold[{index}].sample_id")
        if dataset != DATASET or query_id != f"{dataset}::{sample_id}" or query_id in identities:
            raise ValueError(f"gold[{index}] identity differs")
        answers = row["answers"]
        if not isinstance(answers, list) or not answers:
            raise ValueError(f"gold[{index}].answers must be non-empty")
        for answer_index, answer in enumerate(answers):
            require_native_string(answer, f"gold[{index}].answers[{answer_index}]")
        supporting = row["supporting_paragraph_indices"]
        if not isinstance(supporting, list) or not supporting:
            raise ValueError(f"gold[{index}].supporting_paragraph_indices must be non-empty")
        supporting_set = {
            require_json_int(value, f"gold[{index}].supporting_paragraph_indices")
            for value in supporting
        }
        support_units = row["supporting_unit_ids"]
        if not isinstance(support_units, list) or not support_units:
            raise ValueError(f"gold[{index}].supporting_unit_ids must be non-empty")
        if _paragraph_indices(support_units, f"gold[{index}].supporting_unit_ids") != supporting_set:
            raise ValueError(f"gold[{index}] supporting unit mapping differs")
        identities[query_id] = (dataset, sample_id)

    rankings = load_jsonl(_require_artifact(config, "rankings"))
    if len(rankings) != SAMPLE_SIZE or [row.get("query_id") for row in rankings] != list(identities):
        raise ValueError("Ranking query identity/order differs")
    ranking_map: dict[str, dict[str, Any]] = {}
    ranking_keys = {
        "dataset", "dense_top20_unit_ids", "q25_inserted_unit_ids",
        "query_id", "sample_id", "static_q25_top20_unit_ids",
    }
    for index, row in enumerate(rankings):
        if set(row) != ranking_keys:
            raise ValueError(f"rankings[{index}] schema differs")
        query_id = require_native_string(row["query_id"], f"rankings[{index}].query_id")
        if identities.get(query_id) != (row["dataset"], row["sample_id"]):
            raise ValueError(f"rankings[{index}] identity differs")
        for key in ("dense_top20_unit_ids", "static_q25_top20_unit_ids", "q25_inserted_unit_ids"):
            values = row[key]
            if not isinstance(values, list):
                raise ValueError(f"rankings[{index}].{key} must be a list")
            native_values = [require_native_string(value, f"rankings[{index}].{key}") for value in values]
            if len(native_values) != len(set(native_values)):
                raise ValueError(f"rankings[{index}].{key} duplicates")
        if not row["dense_top20_unit_ids"] or not row["static_q25_top20_unit_ids"]:
            raise ValueError(f"rankings[{index}] effective-K is empty")
        ranking_map[query_id] = row

    predictions = load_jsonl(predictions_main_path)
    prompts = load_jsonl(prompt_main_path)
    assert_no_gold_fields(rankings, "rankings")
    assert_no_gold_fields(predictions, "predictions")
    assert_no_gold_fields(prompts, "prompt audits")
    prediction_map = _pair_index(
        predictions, identities, "predictions",
        {"dataset", "method", "prediction", "query_id", "sample_id"},
    )
    prompt_map = _pair_index(
        prompts, identities, "prompt audits",
        {"dataset", "evidence_unit_ids", "input_token_count", "method", "prompt_sha256", "query_id", "rank1_truncated", "sample_id"},
    )
    generation = config.get("generation")
    if not isinstance(generation, dict) or generation.get("input_token_cap") != 4096:
        raise ValueError("Frozen generation contract differs")
    for key, expected in (("batch_size", 1), ("do_sample", False), ("max_new_tokens", 32), ("num_beams", 1), ("use_cache", True)):
        if generation.get(key) != expected or type(generation.get(key)) is not type(expected):
            raise ValueError(f"Frozen generation field differs: {key}")

    metric_keys = ("answer_em", "answer_f1", "retrieval_cr20", "retrieval_er20", "unknown")
    metrics = {method: {key: [] for key in metric_keys} for method in METHODS}
    audits: list[dict[str, Any]] = []
    effect_counts = {"gain": 0, "harm": 0, "same": 0}
    for row in gold:
        query_id = row["query_id"]
        ranking = ranking_map[query_id]
        supporting_set = set(row["supporting_paragraph_indices"])
        audit: dict[str, Any] = {
            "dataset": row["dataset"], "query_id": query_id, "sample_id": row["sample_id"],
        }
        for method, ranking_key in (
            ("DENSE_TOP20", "dense_top20_unit_ids"),
            ("STATIC_Q25_TOP20", "static_q25_top20_unit_ids"),
        ):
            ranked_ids = ranking[ranking_key]
            prediction = prediction_map[(query_id, method)]["prediction"]
            if not isinstance(prediction, str):
                raise ValueError(f"{query_id}/{method} prediction must be a JSON string")
            prompt = prompt_map[(query_id, method)]
            _validate_prompt_contract(prompt, ranked_ids, 4096, f"{query_id}/{method}")
            em, f1 = _scores(prediction, row["answers"])
            retrieved = _paragraph_indices(ranked_ids, f"{query_id}/{method}.ranking")
            overlap = len(supporting_set & retrieved)
            er = overlap / len(supporting_set)
            cr = float(overlap == len(supporting_set))
            unknown = float(prediction.strip().upper() == "UNKNOWN")
            values = {
                "answer_em": em, "answer_f1": f1, "retrieval_cr20": cr,
                "retrieval_er20": er, "unknown": unknown,
            }
            for key, value in values.items():
                metrics[method][key].append(value)
            audit[method.lower()] = {
                **values,
                "included_evidence_units": len(prompt["evidence_unit_ids"]),
                "input_token_count": prompt["input_token_count"],
                "rank1_truncated": prompt["rank1_truncated"],
            }
        delta = audit["static_q25_top20"]["answer_f1"] - audit["dense_top20"]["answer_f1"]
        effect_counts["gain" if delta > 0 else "harm" if delta < 0 else "same"] += 1
        audits.append(audit)

    query_audit_path = _require_artifact(config, "query_audit")
    if query_audit_path.read_bytes() != render_jsonl(audits):
        raise ValueError("Query audit differs from independent reconstruction")
    bootstrap = _bootstrap(
        np.asarray(metrics["DENSE_TOP20"]["answer_f1"]), np.asarray(metrics["STATIC_Q25_TOP20"]["answer_f1"]),
        np.asarray(metrics["DENSE_TOP20"]["answer_em"]), np.asarray(metrics["STATIC_Q25_TOP20"]["answer_em"]),
    )
    expected_summary = {
        "bootstrap": bootstrap,
        "evidence_label_granularity": "official_supporting_paragraph",
        "insertion_effect_queries": effect_counts,
        "methods": {
            method: {key: float(np.mean(values)) for key, values in rows.items()}
            for method, rows in metrics.items()
        },
        "official_answer_evaluator": config["evaluation"]["official_answer_evaluator"],
        "queries": SAMPLE_SIZE,
        "schema_version": SCHEMA_VERSION,
        "supporting_fact_sentence_recall": {
            "available": False,
            "reason": "MuSiQue v1.0 provides supporting-paragraph, not supporting-sentence, labels",
        },
        "status": "STAGE4F_GOLD_EVALUATION_COMPLETE_PENDING_INDEPENDENT_VERIFICATION",
    }
    summary_path = _require_artifact(config, "evaluation_summary")
    if load_json(summary_path) != expected_summary:
        raise ValueError("Gold summary differs from independent reconstruction")
    expected_decision = {
        "decision": _decision(bootstrap),
        "gates": config["evaluation"]["decision_gates"],
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4F_SCIENTIFIC_DECISION_PENDING_INDEPENDENT_VERIFICATION",
    }
    decision_path = _require_artifact(config, "scientific_decision")
    if load_json(decision_path) != expected_decision:
        raise ValueError("Scientific decision differs from independent reconstruction")
    artifact_keys = PREGOLD_ARTIFACT_KEYS + (
        "telemetry_main", "telemetry_rerun", "verified_pregold", "query_audit",
        "evaluation_summary", "scientific_decision",
    )
    return {
        "artifacts": {key: file_identity(_require_artifact(config, key)) for key in artifact_keys},
        "bootstrap": bootstrap,
        "decision": expected_decision["decision"],
        "frozen_boundaries": frozen_boundaries,
        "gold_isolation": "PASS",
        "implementation": config["implementation"],
        "main_rerun_determinism": {
            "predictions_byte_identical": True,
            "prompt_audit_byte_identical": True,
        },
        "methods": expected_summary["methods"],
        "queries": len(gold),
        "query_audit_reconstructed": True,
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4F_FINAL_VERIFICATION_PASS",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--phase", required=True, choices=("input", "pregold", "postgold"))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict) or config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Stage4F config schema differs")
    assert_implementation_binding(config, Path(__file__).resolve().parents[1])
    result = (
        verify_inputs(config) if args.phase == "input"
        else verify_pregold(config) if args.phase == "pregold"
        else verify_postgold(config)
    )
    expected_key = {"input": "verified_input", "pregold": "verified_pregold", "postgold": "final_verification"}[args.phase]
    if args.output.resolve() != _path(config, expected_key).resolve():
        raise ValueError("Verifier output path differs from frozen config")
    write_new_files_atomically(((args.output, render_json(result)),))
    print(result["status"])


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE4F_INDEPENDENT_VERIFICATION_FAIL: {exc}", file=sys.stderr)
        raise
