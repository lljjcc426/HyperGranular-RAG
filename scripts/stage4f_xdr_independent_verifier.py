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
    assert_file_identity,
    assert_implementation_binding,
    assert_no_gold_fields,
    file_identity,
    id_digest,
    load_json,
    load_jsonl,
    render_json,
    render_jsonl,
    require_json_bool,
    require_json_int,
    require_native_string,
    selection_key,
    split_sentences,
    write_new_files_atomically,
)
from stage4f_xdr_retrieval import RetrievalConfig, build_query_decisions, dot


METHODS = ("DENSE_TOP20", "STATIC_Q25_TOP20")
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


def verify_postgold(config: dict[str, Any]) -> dict[str, Any]:
    gold = load_jsonl(_assert_bound(config, "gold"))
    predictions = load_jsonl(_require_artifact(config, "predictions_main"))
    prediction_map = {(row["query_id"], row["method"]): row for row in predictions}
    metrics = {method: {"em": [], "f1": []} for method in METHODS}
    for row in gold:
        for method in METHODS:
            prediction = prediction_map.get((row["query_id"], method))
            if prediction is None:
                raise ValueError("Gold/prediction pairing differs")
            em, f1 = _scores(prediction["prediction"], row["answers"])
            metrics[method]["em"].append(em)
            metrics[method]["f1"].append(f1)
    bootstrap = _bootstrap(
        np.asarray(metrics["DENSE_TOP20"]["f1"]), np.asarray(metrics["STATIC_Q25_TOP20"]["f1"]),
        np.asarray(metrics["DENSE_TOP20"]["em"]), np.asarray(metrics["STATIC_Q25_TOP20"]["em"]),
    )
    summary = load_json(_path(config, "evaluation_summary"))
    decision = load_json(_path(config, "scientific_decision"))
    if summary.get("bootstrap") != bootstrap or decision.get("decision") != _decision(bootstrap):
        raise ValueError("Gold summary or decision differs from independent reconstruction")
    return {
        "decision": decision["decision"], "queries": len(gold),
        "schema_version": SCHEMA_VERSION, "status": "STAGE4F_FINAL_VERIFICATION_PASS",
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
