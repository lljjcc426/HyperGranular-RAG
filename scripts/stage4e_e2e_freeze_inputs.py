"""Freeze the Stage4E HotpotQA ID boundary and isolated blind/Gold channels."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Sequence

from stage4e_e2e_common import (
    BLIND_PROHIBITED_KEYS,
    DATASET,
    SAMPLE_SIZE,
    SCHEMA_VERSION,
    SELECTION_SALT,
    SOURCE_BYTES,
    SOURCE_CANONICAL_URL,
    SOURCE_SHA256,
    SOURCE_TRANSPORT_REVISION,
    SOURCE_TRANSPORT_URL,
    assert_no_prohibited_keys,
    file_identity,
    id_digest,
    load_json,
    load_jsonl,
    normalize_sentence,
    query_id,
    render_json,
    render_jsonl,
    require_json_int,
    require_native_string,
    selection_key,
    sha256_bytes,
    write_new_files_atomically,
)


def _validate_source_row(row: Any, index: int) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise ValueError(f"source[{index}] must be an object")
    required = {"_id", "question", "answer", "supporting_facts", "context", "type", "level"}
    missing = required - set(row)
    if missing:
        raise ValueError(f"source[{index}] missing fields: {sorted(missing)}")
    require_native_string(row["_id"], f"source[{index}]._id")
    require_native_string(row["question"], f"source[{index}].question")
    require_native_string(row["answer"], f"source[{index}].answer")
    require_native_string(row["type"], f"source[{index}].type")
    require_native_string(row["level"], f"source[{index}].level")
    if not isinstance(row["context"], list) or not row["context"]:
        raise ValueError(f"source[{index}].context must be a non-empty list")
    if not isinstance(row["supporting_facts"], list) or not row["supporting_facts"]:
        raise ValueError(f"source[{index}].supporting_facts must be a non-empty list")
    return row


def _historical_sample_ids(paths: Sequence[Path]) -> tuple[set[str], list[dict[str, Any]]]:
    values: set[str] = set()
    audits: list[dict[str, Any]] = []
    for path in paths:
        rows = load_jsonl(path)
        file_values: set[str] = set()
        for index, row in enumerate(rows):
            dataset = require_native_string(row.get("dataset"), f"{path}:{index}.dataset")
            if "hotpot" not in dataset.casefold():
                continue
            sample_id = require_native_string(row.get("sample_id"), f"{path}:{index}.sample_id")
            file_values.add(sample_id)
            values.add(sample_id)
        ordered = sorted(file_values)
        audits.append(
            {
                "path": str(path),
                **file_identity(path),
                "hotpotqa_sample_ids": len(ordered),
                "hotpotqa_sample_id_sha256": id_digest(ordered),
            }
        )
    return values, audits


def _build_channels_for_row(row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    sample_id = require_native_string(row["_id"], "_id")
    qid = query_id(sample_id)
    contexts: list[dict[str, Any]] = []
    unit_by_support_key: dict[tuple[str, int], str] = {}

    for context_index, raw_context in enumerate(row["context"]):
        if not isinstance(raw_context, list) or len(raw_context) != 2:
            raise ValueError(f"{qid}: context[{context_index}] must be [title, sentences]")
        title = require_native_string(raw_context[0], f"{qid}: context title")
        raw_sentences = raw_context[1]
        if not isinstance(raw_sentences, list) or not raw_sentences:
            raise ValueError(f"{qid}: context[{context_index}] sentences must be non-empty")
        sentences: list[str] = []
        for sentence_index, raw_sentence in enumerate(raw_sentences):
            sentence = normalize_sentence(raw_sentence)
            sentences.append(sentence)
            if not sentence:
                continue
            key = (title, sentence_index)
            if key in unit_by_support_key:
                raise ValueError(f"{qid}: ambiguous title/sentence mapping: {key}")
            unit_by_support_key[key] = f"{qid}::c{context_index}::s{sentence_index}"
        contexts.append(
            {
                "context_index": context_index,
                "sentences": sentences,
                "title": title,
            }
        )

    supporting_facts: list[dict[str, Any]] = []
    seen_support: set[tuple[str, int]] = set()
    for support_index, raw_support in enumerate(row["supporting_facts"]):
        if not isinstance(raw_support, list) or len(raw_support) != 2:
            raise ValueError(f"{qid}: supporting_facts[{support_index}] must be [title, index]")
        title = require_native_string(raw_support[0], f"{qid}: support title")
        sentence_index = require_json_int(raw_support[1], f"{qid}: support sentence index")
        if sentence_index < 0:
            raise ValueError(f"{qid}: support sentence index must be non-negative")
        key = (title, sentence_index)
        if key in seen_support:
            raise ValueError(f"{qid}: duplicate supporting fact: {key}")
        if key not in unit_by_support_key:
            raise ValueError(f"{qid}: supporting fact has no unique unit mapping: {key}")
        seen_support.add(key)
        supporting_facts.append(
            {
                "sentence_index": sentence_index,
                "title": title,
                "unit_id": unit_by_support_key[key],
            }
        )

    blind = {
        "context": contexts,
        "dataset": DATASET,
        "query_id": qid,
        "question": require_native_string(row["question"], f"{qid}: question"),
        "sample_id": sample_id,
    }
    assert_no_prohibited_keys(blind, f"blind[{qid}]")
    gold = {
        "answer": require_native_string(row["answer"], f"{qid}: answer"),
        "dataset": DATASET,
        "query_id": qid,
        "sample_id": sample_id,
        "supporting_facts": supporting_facts,
    }
    metadata = {
        "dataset": DATASET,
        "level": require_native_string(row["level"], f"{qid}: level"),
        "query_id": qid,
        "sample_id": sample_id,
        "type": require_native_string(row["type"], f"{qid}: type"),
    }
    return blind, gold, metadata


def build_frozen_channels(
    source_rows: list[Any], historical_query_paths: Sequence[Path]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if len(source_rows) < SAMPLE_SIZE:
        raise ValueError(f"Source has fewer than {SAMPLE_SIZE} rows")
    validated = [_validate_source_row(row, index) for index, row in enumerate(source_rows)]
    sample_ids = [str(row["_id"]) for row in validated]
    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Source contains duplicate _id values")

    ranked = sorted(validated, key=lambda row: (selection_key(str(row["_id"])), str(row["_id"])))
    selected = ranked[:SAMPLE_SIZE]
    historical_ids, historical_audit = _historical_sample_ids(historical_query_paths)
    selected_ids = [str(row["_id"]) for row in selected]
    overlap = sorted(set(selected_ids) & historical_ids)
    if overlap:
        raise ValueError(f"Selected IDs overlap historical HotpotQA IDs: {overlap[:5]}")

    blind_rows: list[dict[str, Any]] = []
    gold_rows: list[dict[str, Any]] = []
    metadata_rows: list[dict[str, Any]] = []
    selections: list[dict[str, str]] = []
    for row in selected:
        blind, gold, metadata = _build_channels_for_row(row)
        blind_rows.append(blind)
        gold_rows.append(gold)
        metadata_rows.append(metadata)
        selections.append(
            {
                "query_id": blind["query_id"],
                "sample_id": blind["sample_id"],
                "selection_key": selection_key(blind["sample_id"]),
            }
        )

    blind_payload = render_jsonl(blind_rows)
    gold_payload = render_jsonl(gold_rows)
    metadata_payload = render_jsonl(metadata_rows)
    manifest = {
        "channels": {
            "blind": {"bytes": len(blind_payload), "rows": len(blind_rows), "sha256": sha256_bytes(blind_payload)},
            "descriptive_metadata": {"bytes": len(metadata_payload), "rows": len(metadata_rows), "sha256": sha256_bytes(metadata_payload)},
            "gold_targets": {"bytes": len(gold_payload), "rows": len(gold_rows), "sha256": sha256_bytes(gold_payload)},
        },
        "checks": {
            "blind_prohibited_keys": sorted(BLIND_PROHIBITED_KEYS),
            "blind_prohibited_keys_absent": True,
            "historical_hotpotqa_overlap": 0,
            "official_metrics_computed": False,
            "retrieval_embedding_generation_executed": False,
            "source_rows": len(validated),
        },
        "dataset": DATASET,
        "historical_inputs": historical_audit,
        "schema_version": SCHEMA_VERSION,
        "selection": {
            "query_id_sha256": id_digest(row["query_id"] for row in selections),
            "rows": selections,
            "salt": SELECTION_SALT,
            "sample_id_sha256": id_digest(row["sample_id"] for row in selections),
            "sample_size": SAMPLE_SIZE,
        },
        "source": {
            "bytes": SOURCE_BYTES,
            "canonical_url": SOURCE_CANONICAL_URL,
            "download_date": "2026-07-20",
            "license": "CC BY-SA 4.0",
            "license_evidence_url": (
                "https://github.com/hotpotqa/hotpot/blob/"
                "3635853403a8735609ee997664e1528f4480762a/README.md"
            ),
            "official_homepage": "https://hotpotqa.github.io/",
            "retrieval_note": (
                "Canonical host timed out in three bounded attempts; an exact-revision "
                "transport mirror was accepted only after canonical byte/SHA matching."
            ),
            "sha256": SOURCE_SHA256,
            "transport_revision": SOURCE_TRANSPORT_REVISION,
            "transport_url": SOURCE_TRANSPORT_URL,
        },
        "status": "STAGE4E_INPUT_CHANNELS_FROZEN_NO_RETRIEVAL_OR_GENERATION",
    }
    return blind_rows, gold_rows, metadata_rows, manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--historical-query", action="append", required=True, type=Path)
    parser.add_argument("--blind-output", required=True, type=Path)
    parser.add_argument("--gold-output", required=True, type=Path)
    parser.add_argument("--metadata-output", required=True, type=Path)
    parser.add_argument("--manifest-output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_identity = file_identity(args.source)
    if source_identity != {"bytes": SOURCE_BYTES, "sha256": SOURCE_SHA256}:
        raise ValueError(f"Source identity differs from canonical HotpotQA train: {source_identity}")
    source_rows = load_json(args.source)
    if not isinstance(source_rows, list):
        raise ValueError("HotpotQA source must be a JSON list")
    blind, gold, metadata, manifest = build_frozen_channels(
        source_rows, args.historical_query
    )
    files = (
        (args.blind_output, render_jsonl(blind)),
        (args.gold_output, render_jsonl(gold)),
        (args.metadata_output, render_jsonl(metadata)),
        (args.manifest_output, render_json(manifest)),
    )
    write_new_files_atomically(files)
    print(
        "STAGE4E_INPUT_FREEZE_PASS "
        f"queries={len(blind)} source_rows={len(source_rows)} overlap=0"
    )


if __name__ == "__main__":
    main()
