"""Independent verifier for Stage4E input, pre-Gold, and post-Gold phases.

This module intentionally does not import the Stage4E runner or evaluator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import string
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from stage4b_u1_goldfree_retrieval import RetrievalConfig, build_query_decisions
from stage4e_e2e_common import (
    BLIND_PROHIBITED_KEYS,
    BOOTSTRAP_ITERATIONS,
    BOOTSTRAP_SEED,
    DATASET,
    SAMPLE_SIZE,
    SCHEMA_VERSION,
    SOURCE_BYTES,
    SOURCE_SHA256,
    assert_file_identity,
    assert_implementation_binding,
    assert_no_prohibited_keys,
    file_identity,
    id_digest,
    load_json,
    load_jsonl,
    method_order,
    normalize_sentence,
    render_json,
    render_jsonl,
    require_json_int,
    require_native_string,
    selection_key,
    sha256_bytes,
    write_new_files_atomically,
)


METHODS = ("DENSE_TOP20", "STATIC_Q25_TOP20")
SYSTEM_MESSAGE = (
    "Answer the question using only the provided evidence. Return only the "
    "shortest final answer. If the evidence is insufficient, return UNKNOWN."
)


def _path(config: dict[str, Any], key: str) -> Path:
    return Path(require_native_string(config.get("paths", {}).get(key), f"paths.{key}"))


def _assert_bound(config: dict[str, Any], key: str) -> Path:
    path = _path(config, key)
    expected = config.get("inputs", {}).get(key)
    if not isinstance(expected, dict):
        raise ValueError(f"inputs.{key} binding is missing")
    assert_file_identity(path, expected, f"inputs.{key}")
    return path


def _source_context(row: dict[str, Any], query_id: str) -> tuple[list[dict[str, Any]], dict[tuple[str, int], str]]:
    contexts: list[dict[str, Any]] = []
    support_map: dict[tuple[str, int], str] = {}
    raw_contexts = row.get("context")
    if not isinstance(raw_contexts, list) or not raw_contexts:
        raise ValueError(f"{query_id}: source context is invalid")
    for context_index, raw_context in enumerate(raw_contexts):
        if not isinstance(raw_context, list) or len(raw_context) != 2:
            raise ValueError(f"{query_id}: source context row is invalid")
        title = require_native_string(raw_context[0], f"{query_id}: source title")
        if not isinstance(raw_context[1], list) or not raw_context[1]:
            raise ValueError(f"{query_id}: source sentences are invalid")
        sentences: list[str] = []
        for sentence_index, raw_sentence in enumerate(raw_context[1]):
            sentence = normalize_sentence(raw_sentence)
            sentences.append(sentence)
            if sentence:
                key = (title, sentence_index)
                if key in support_map:
                    raise ValueError(f"{query_id}: ambiguous source support key")
                support_map[key] = f"{query_id}::c{context_index}::s{sentence_index}"
        contexts.append(
            {"context_index": context_index, "sentences": sentences, "title": title}
        )
    return contexts, support_map


def verify_inputs(config: dict[str, Any]) -> dict[str, Any]:
    source_path = _assert_bound(config, "source")
    if file_identity(source_path) != {"bytes": SOURCE_BYTES, "sha256": SOURCE_SHA256}:
        raise ValueError("Source identity differs from the canonical frozen identity")
    manifest_path = _assert_bound(config, "input_manifest")
    blind_path = _assert_bound(config, "blind")
    gold_path = _assert_bound(config, "gold")
    metadata_path = _assert_bound(config, "metadata")

    source = load_json(source_path)
    if not isinstance(source, list):
        raise ValueError("Source must be a JSON list")
    source_by_id: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(source):
        if not isinstance(row, dict):
            raise ValueError(f"source[{index}] must be an object")
        sample_id = require_native_string(row.get("_id"), f"source[{index}]._id")
        if sample_id in source_by_id:
            raise ValueError("Source sample IDs are not unique")
        source_by_id[sample_id] = row
    selected = sorted(source_by_id, key=lambda value: (selection_key(value), value))[:SAMPLE_SIZE]

    manifest = load_json(manifest_path)
    if not isinstance(manifest, dict) or manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Input manifest schema differs")
    selection = manifest.get("selection")
    if not isinstance(selection, dict) or selection.get("sample_size") != SAMPLE_SIZE:
        raise ValueError("Input manifest selection contract differs")
    expected_rows = [
        {
            "query_id": f"{DATASET}::{sample_id}",
            "sample_id": sample_id,
            "selection_key": selection_key(sample_id),
        }
        for sample_id in selected
    ]
    if selection.get("rows") != expected_rows:
        raise ValueError("Input manifest selection rows differ from reconstruction")
    if selection.get("sample_id_sha256") != id_digest(selected):
        raise ValueError("Selected sample ID digest differs")
    if selection.get("query_id_sha256") != id_digest(row["query_id"] for row in expected_rows):
        raise ValueError("Selected query ID digest differs")

    blind = load_jsonl(blind_path)
    gold = load_jsonl(gold_path)
    metadata = load_jsonl(metadata_path)
    if not (len(blind) == len(gold) == len(metadata) == SAMPLE_SIZE):
        raise ValueError("Input channels do not contain exactly 1,000 aligned rows")
    assert_no_prohibited_keys(blind, "verified blind channel")
    for index, (sample_id, blind_row, gold_row, metadata_row) in enumerate(
        zip(selected, blind, gold, metadata, strict=True)
    ):
        query_id = f"{DATASET}::{sample_id}"
        identity = {"dataset": DATASET, "query_id": query_id, "sample_id": sample_id}
        for label, channel in (
            ("blind", blind_row), ("gold", gold_row), ("metadata", metadata_row)
        ):
            for key, value in identity.items():
                if channel.get(key) != value or not isinstance(channel.get(key), str):
                    raise ValueError(f"{label}[{index}] identity differs")
        if set(blind_row) != {"context", "dataset", "query_id", "question", "sample_id"}:
            raise ValueError(f"blind[{index}] key contract differs")
        if set(gold_row) != {"answer", "dataset", "query_id", "sample_id", "supporting_facts"}:
            raise ValueError(f"gold[{index}] key contract differs")
        if set(metadata_row) != {"dataset", "level", "query_id", "sample_id", "type"}:
            raise ValueError(f"metadata[{index}] key contract differs")
        source_row = source_by_id[sample_id]
        contexts, support_map = _source_context(source_row, query_id)
        if blind_row["question"] != source_row.get("question") or blind_row["context"] != contexts:
            raise ValueError(f"blind[{index}] content differs from source")
        expected_support: list[dict[str, Any]] = []
        for raw_support in source_row.get("supporting_facts", []):
            if not isinstance(raw_support, list) or len(raw_support) != 2:
                raise ValueError(f"{query_id}: source supporting fact is invalid")
            title = require_native_string(raw_support[0], f"{query_id}: support title")
            sentence_index = require_json_int(raw_support[1], f"{query_id}: support index")
            unit_id = support_map.get((title, sentence_index))
            if unit_id is None:
                raise ValueError(f"{query_id}: supporting fact has no unique unit")
            expected_support.append(
                {"sentence_index": sentence_index, "title": title, "unit_id": unit_id}
            )
        if gold_row["answer"] != source_row.get("answer") or gold_row["supporting_facts"] != expected_support:
            raise ValueError(f"gold[{index}] content differs from source")
        if metadata_row["type"] != source_row.get("type") or metadata_row["level"] != source_row.get("level"):
            raise ValueError(f"metadata[{index}] content differs from source")

    historical_ids: set[str] = set()
    for raw_path in config.get("historical_query_paths", []):
        path = Path(require_native_string(raw_path, "historical_query_paths[]"))
        for row in load_jsonl(path):
            if "hotpot" in str(row.get("dataset", "")).casefold():
                historical_ids.add(require_native_string(row.get("sample_id"), "historical sample_id"))
    overlap = sorted(set(selected) & historical_ids)
    if overlap:
        raise ValueError(f"Selected IDs overlap historical HotpotQA identities: {overlap[:5]}")
    checks = manifest.get("checks")
    if not isinstance(checks, dict) or checks.get("historical_hotpotqa_overlap") != 0:
        raise ValueError("Manifest historical-overlap assertion differs")
    if checks.get("retrieval_embedding_generation_executed") is not False:
        raise ValueError("Input manifest incorrectly records retrieval/generation")
    if checks.get("official_metrics_computed") is not False:
        raise ValueError("Input manifest incorrectly records official metrics")
    return {
        "channels": {
            "blind": file_identity(blind_path),
            "gold": file_identity(gold_path),
            "metadata": file_identity(metadata_path),
        },
        "historical_hotpotqa_overlap": 0,
        "input_manifest": file_identity(manifest_path),
        "queries": SAMPLE_SIZE,
        "schema_version": SCHEMA_VERSION,
        "source": file_identity(source_path),
        "status": "STAGE4E_INPUT_CHANNELS_VERIFIED",
    }


def _build_units(blind: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    units: list[dict[str, Any]] = []
    queries: list[dict[str, Any]] = []
    for row in blind:
        query_id = require_native_string(row.get("query_id"), "blind.query_id")
        sample_id = require_native_string(row.get("sample_id"), "blind.sample_id")
        dataset = require_native_string(row.get("dataset"), "blind.dataset")
        query_units: list[dict[str, Any]] = []
        for context_index, context in enumerate(row.get("context", [])):
            if context.get("context_index") != context_index:
                raise ValueError(f"{query_id}: context order differs")
            title = require_native_string(context.get("title"), f"{query_id}: title")
            for sentence_index, raw_sentence in enumerate(context.get("sentences", [])):
                sentence = normalize_sentence(raw_sentence)
                if not sentence:
                    continue
                query_units.append(
                    {
                        "context_index": context_index,
                        "dataset": dataset,
                        "doc_id": f"{query_id}::c{context_index}",
                        "query_id": query_id,
                        "sample_id": sample_id,
                        "sentence_id": sentence_index,
                        "text": sentence,
                        "title": title,
                        "unit_id": f"{query_id}::c{context_index}::s{sentence_index}",
                    }
                )
        units.extend(query_units)
        queries.append(
            {
                "dataset": dataset,
                "num_candidate_units": len(query_units),
                "query_id": query_id,
                "question": require_native_string(row.get("question"), f"{query_id}: question"),
                "sample_id": sample_id,
            }
        )
    return units, queries


def _load_cache(path: Path, units: list[dict[str, Any]], queries: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
    with np.load(path, allow_pickle=False) as cache:
        if cache["unit_ids"].tolist() != [row["unit_id"] for row in units]:
            raise ValueError("Embedding-cache unit IDs/order differ")
        if cache["query_ids"].tolist() != [row["query_id"] for row in queries]:
            raise ValueError("Embedding-cache query IDs/order differ")
        unit_embeddings = np.asarray(cache["unit_embeddings"], dtype="float32")
        query_embeddings = np.asarray(cache["query_embeddings"], dtype="float32")
    if not np.isfinite(unit_embeddings).all() or not np.isfinite(query_embeddings).all():
        raise ValueError("Embedding cache is non-finite")
    return unit_embeddings, query_embeddings


def _chat_messages(question: str, lines: list[str]) -> list[dict[str, str]]:
    evidence = "\n".join(lines)
    return [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {
            "role": "user",
            "content": (
                f"Evidence:\n{evidence}\n\nQuestion: {question}\nFinal answer:"
            ),
        },
    ]


def _chat_ids(tokenizer: Any, messages: list[dict[str, str]]) -> list[int]:
    result = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True)
    if hasattr(result, "keys") and "input_ids" in result:
        result = result["input_ids"]
    return result.tolist() if hasattr(result, "tolist") else list(result)


def _prompt_audit(tokenizer: Any, question: str, ranked_units: list[dict[str, Any]]) -> dict[str, Any]:
    lines: list[str] = []
    included: list[str] = []
    truncated = False
    for rank, unit in enumerate(ranked_units, start=1):
        line = f"[{rank}] {unit['title']}: {unit['text']}"
        if len(_chat_ids(tokenizer, _chat_messages(question, lines + [line]))) <= 4096:
            lines.append(line)
            included.append(unit["unit_id"])
            continue
        if rank > 1:
            break
        tokens = list(tokenizer.encode(line, add_special_tokens=False))
        for kept in range(len(tokens), -1, -1):
            shortened = tokenizer.decode(
                tokens[:kept], skip_special_tokens=True, clean_up_tokenization_spaces=False
            )
            if len(_chat_ids(tokenizer, _chat_messages(question, [shortened]))) <= 4096:
                lines = [shortened]
                included = [unit["unit_id"]]
                truncated = True
                break
        if not lines:
            raise ValueError("Independent rank-1 prompt truncation failed")
        break
    messages = _chat_messages(question, lines)
    ids = _chat_ids(tokenizer, messages)
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return {
        "evidence_unit_ids": included,
        "input_token_count": len(ids),
        "prompt_sha256": sha256_bytes(text.encode("utf-8")),
        "rank1_truncated": truncated,
    }


def verify_pregold(config: dict[str, Any]) -> dict[str, Any]:
    if _path(config, "predictions_main").read_bytes() != _path(config, "predictions_rerun").read_bytes():
        raise ValueError("Main/rerun predictions are not byte-identical")
    if _path(config, "prompt_audit_main").read_bytes() != _path(config, "prompt_audit_rerun").read_bytes():
        raise ValueError("Main/rerun prompt audits are not byte-identical")
    blind = load_jsonl(_assert_bound(config, "blind"))
    assert_no_prohibited_keys(blind, "pre-Gold blind input")
    units, queries = _build_units(blind)
    unit_embeddings, query_embeddings = _load_cache(
        _path(config, "embedding_cache"), units, queries
    )
    decisions = build_query_decisions(
        units, queries, unit_embeddings, query_embeddings, RetrievalConfig()
    )
    expected_rankings = [
        {
            "dataset": query["dataset"],
            "dense_top20_unit_ids": decision["dense_top20_unit_ids"],
            "q25_inserted_unit_ids": decision["q25_inserted_unit_ids"],
            "query_id": query["query_id"],
            "sample_id": query["sample_id"],
            "static_q25_top20_unit_ids": decision["q25_top20_unit_ids"],
        }
        for query, decision in zip(queries, decisions, strict=True)
    ]
    if _path(config, "rankings").read_bytes() != render_jsonl(expected_rankings):
        raise ValueError("Rankings differ from independent reconstruction")

    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        _path(config, "generator_snapshot"), local_files_only=True
    )
    units_by_id = {row["unit_id"]: row for row in units}
    ranking_by_query = {row["query_id"]: row for row in expected_rankings}
    expected_audits: list[dict[str, Any]] = []
    expected_prediction_order: list[tuple[str, str]] = []
    for query in queries:
        ranking = ranking_by_query[query["query_id"]]
        for method in method_order(query["query_id"]):
            ids = (
                ranking["dense_top20_unit_ids"]
                if method == "DENSE_TOP20"
                else ranking["static_q25_top20_unit_ids"]
            )
            audit = _prompt_audit(
                tokenizer, query["question"], [units_by_id[value] for value in ids]
            )
            expected_audits.append(
                {
                    "dataset": query["dataset"],
                    **audit,
                    "method": method,
                    "query_id": query["query_id"],
                    "sample_id": query["sample_id"],
                }
            )
            expected_prediction_order.append((query["query_id"], method))
    if _path(config, "prompt_audit_main").read_bytes() != render_jsonl(expected_audits):
        raise ValueError("Prompt audit differs from independent reconstruction")
    predictions = load_jsonl(_path(config, "predictions_main"))
    actual_order: list[tuple[str, str]] = []
    for row in predictions:
        if set(row) != {"dataset", "method", "prediction", "query_id", "sample_id"}:
            raise ValueError("Prediction key contract differs")
        if not isinstance(row["prediction"], str):
            raise ValueError("Prediction must be a native string")
        actual_order.append((row["query_id"], row["method"]))
    if actual_order != expected_prediction_order:
        raise ValueError("Prediction identity/method order differs")
    return {
        "embedding_cache": file_identity(_path(config, "embedding_cache")),
        "predictions": file_identity(_path(config, "predictions_main")),
        "queries": len(queries),
        "rankings": file_identity(_path(config, "rankings")),
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4E_PRE_GOLD_ARTIFACTS_VERIFIED",
    }


def _normalize_answer(value: str) -> str:
    without_punctuation = "".join(ch for ch in value.lower() if ch not in set(string.punctuation))
    without_articles = re.sub(r"\b(a|an|the)\b", " ", without_punctuation)
    return " ".join(without_articles.split())


def _scores(prediction: str, gold: str) -> tuple[float, float]:
    prediction_value = _normalize_answer(prediction)
    gold_value = _normalize_answer(gold)
    em = float(prediction_value == gold_value)
    if (
        prediction_value in {"yes", "no", "noanswer"} and prediction_value != gold_value
    ) or (gold_value in {"yes", "no", "noanswer"} and prediction_value != gold_value):
        return em, 0.0
    common = Counter(prediction_value.split()) & Counter(gold_value.split())
    same = sum(common.values())
    if same == 0:
        return em, 0.0
    precision = same / len(prediction_value.split())
    recall = same / len(gold_value.split())
    return em, 2 * precision * recall / (precision + recall)


def _bootstrap(f1_delta: np.ndarray, em_delta: np.ndarray) -> dict[str, Any]:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    f1_draws = np.empty(BOOTSTRAP_ITERATIONS)
    em_draws = np.empty(BOOTSTRAP_ITERATIONS)
    for index in range(BOOTSTRAP_ITERATIONS):
        draw = rng.integers(0, len(f1_delta), len(f1_delta))
        f1_draws[index] = np.mean(f1_delta[draw])
        em_draws[index] = np.mean(em_delta[draw])
    return {
        "iterations": BOOTSTRAP_ITERATIONS,
        "numpy_generator": "PCG64",
        "percentile_method": "linear",
        "seed": BOOTSTRAP_SEED,
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


def _decision(bootstrap: dict[str, Any]) -> str:
    f1 = bootstrap["delta_answer_f1"]
    em = bootstrap["delta_answer_em"]
    if f1["point"] >= 0.010 and f1["lower_95"] > 0 and em["lower_95"] >= -0.010:
        return "STATIC_HGRAG_E2E_SUPPORTED"
    if f1["upper_95"] < 0 or em["upper_95"] < -0.010:
        return "STATIC_HGRAG_E2E_NEGATIVE"
    return "STATIC_HGRAG_E2E_INCONCLUSIVE"


def verify_postgold(config: dict[str, Any]) -> dict[str, Any]:
    predictions = load_jsonl(_path(config, "predictions_main"))
    rankings = load_jsonl(_path(config, "rankings"))
    gold = load_jsonl(_assert_bound(config, "gold"))
    prediction_map = {(row["query_id"], row["method"]): row["prediction"] for row in predictions}
    ranking_map = {row["query_id"]: row for row in rankings}
    audits: list[dict[str, Any]] = []
    metrics: dict[str, dict[str, list[float]]] = {method: defaultdict(list) for method in METHODS}
    insertion = Counter()
    for target in gold:
        query_id = target["query_id"]
        gold_units = {row["unit_id"] for row in target["supporting_facts"]}
        method_rows: dict[str, Any] = {}
        cr_values: dict[str, float] = {}
        for method, key in (
            ("DENSE_TOP20", "dense_top20_unit_ids"),
            ("STATIC_Q25_TOP20", "static_q25_top20_unit_ids"),
        ):
            prediction = prediction_map[(query_id, method)]
            em, f1 = _scores(prediction, target["answer"])
            ranking_ids = ranking_map[query_id][key]
            hits = len(gold_units & set(ranking_ids))
            er = hits / len(gold_units)
            cr = float(hits == len(gold_units))
            cr_values[method] = cr
            metrics[method]["answer_em"].append(em)
            metrics[method]["answer_f1"].append(f1)
            metrics[method]["retrieval_cr20"].append(cr)
            metrics[method]["retrieval_er20"].append(er)
            metrics[method]["unknown"].append(float(prediction.casefold() == "unknown"))
            method_rows[method] = {
                "answer_em": em,
                "answer_f1": f1,
                "prediction": prediction,
                "retrieval_cr20": cr,
                "retrieval_er20": er,
            }
        delta = cr_values["STATIC_Q25_TOP20"] - cr_values["DENSE_TOP20"]
        insertion["gain" if delta > 0 else "harm" if delta < 0 else "same"] += 1
        audits.append(
            {
                "answer": target["answer"],
                "dataset": target["dataset"],
                "dense": method_rows["DENSE_TOP20"],
                "query_id": query_id,
                "sample_id": target["sample_id"],
                "static_q25": method_rows["STATIC_Q25_TOP20"],
            }
        )
    f1_delta = np.asarray(metrics["STATIC_Q25_TOP20"]["answer_f1"]) - np.asarray(
        metrics["DENSE_TOP20"]["answer_f1"]
    )
    em_delta = np.asarray(metrics["STATIC_Q25_TOP20"]["answer_em"]) - np.asarray(
        metrics["DENSE_TOP20"]["answer_em"]
    )
    bootstrap = _bootstrap(f1_delta, em_delta)
    decision = _decision(bootstrap)
    expected_decision = load_json(_path(config, "scientific_decision"))
    frozen_decision = {
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
    if expected_decision != frozen_decision:
        raise ValueError("Scientific decision differs from independent reconstruction")
    if _path(config, "query_audit").read_bytes() != render_jsonl(audits):
        raise ValueError("Query audit differs from independent reconstruction")
    summary = load_json(_path(config, "evaluation_summary"))
    if summary.get("bootstrap") != bootstrap:
        raise ValueError("Bootstrap summary differs from independent reconstruction")
    expected_methods = {
        method: {key: float(np.mean(values)) for key, values in sorted(rows.items())}
        for method, rows in metrics.items()
    }
    if summary.get("methods") != expected_methods:
        raise ValueError("Aggregate method metrics differ from independent reconstruction")
    if summary.get("insertion_effect_queries") != dict(sorted(insertion.items())):
        raise ValueError("Insertion-effect counts differ from independent reconstruction")
    if summary.get("queries") != len(audits) or summary.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Evaluation summary identity/count differs")
    if summary.get("status") != "STAGE4E_GOLD_EVALUATION_COMPLETE_PENDING_INDEPENDENT_VERIFICATION":
        raise ValueError("Evaluation summary status differs")
    expected_evaluator = {
        "commit": "3635853403a8735609ee997664e1528f4480762a",
        "sha256": "D35FC91A6DB21D791DBDDA11DAF3856E9359F5701D54E3EEFBA20D88FECC02C0",
        "source": (
            "https://github.com/hotpotqa/hotpot/blob/"
            "3635853403a8735609ee997664e1528f4480762a/hotpot_evaluate_v1.py"
        ),
    }
    if summary.get("official_answer_evaluator") != expected_evaluator:
        raise ValueError("Official answer-evaluator provenance differs")
    # Metadata is touched only after the independent aggregate decision is frozen.
    metadata = load_jsonl(_assert_bound(config, "metadata"))
    if [row["query_id"] for row in metadata] != [row["query_id"] for row in audits]:
        raise ValueError("Metadata identity/order differs")
    audit_map = {row["query_id"]: row for row in audits}
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in metadata:
        groups[(require_native_string(row.get("type"), "metadata.type"), "type")].append(
            audit_map[row["query_id"]]
        )
        groups[(require_native_string(row.get("level"), "metadata.level"), "level")].append(
            audit_map[row["query_id"]]
        )
    subgroups = [
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
        for (value, dimension), rows in sorted(groups.items())
    ]
    if summary.get("descriptive_subgroups") != subgroups:
        raise ValueError("Descriptive subgroup rows differ from independent reconstruction")
    artifact_keys = (
        "rankings", "predictions_main", "predictions_rerun", "prompt_audit_main",
        "prompt_audit_rerun", "query_audit", "evaluation_summary", "scientific_decision",
    )
    return {
        "artifacts": {key: file_identity(_path(config, key)) for key in artifact_keys},
        "decision": decision,
        "queries": len(audits),
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4E_FINAL_VERIFICATION_PASS",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--phase", required=True, choices=("input", "pregold", "postgold"))
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict) or config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Stage4E config schema differs")
    assert_implementation_binding(config, Path(__file__).resolve().parents[1])
    result = (
        verify_inputs(config)
        if args.phase == "input"
        else verify_pregold(config)
        if args.phase == "pregold"
        else verify_postgold(config)
    )
    write_new_files_atomically(((args.output, render_json(result)),))
    print(result["status"])


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE4E_INDEPENDENT_VERIFICATION_FAIL: {exc}", file=sys.stderr)
        raise
