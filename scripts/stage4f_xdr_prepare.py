"""Freeze Stage4F MuSiQue source rows into blind, Gold, and sealed metadata channels."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from stage4f_xdr_common import (
    DATASET,
    SAMPLE_SIZE,
    SCHEMA_VERSION,
    SOURCE_BYTES,
    SOURCE_SHA256,
    assert_file_identity,
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
    sha256_bytes,
    split_sentences,
    write_new_files_atomically,
)


BLIND_KEYS = {"candidate_units", "dataset", "query_id", "question", "sample_id"}
UNIT_KEYS = {
    "dataset",
    "paragraph_index",
    "query_id",
    "sample_id",
    "sentence_index",
    "text",
    "title",
    "unit_id",
}


def _load_history(path: Path) -> list[dict[str, Any]]:
    value = load_json(path) if path.suffix.lower() == ".json" else load_jsonl(path)
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise ValueError(f"Historical query file must contain object rows: {path}")
    return value


def historical_native_ids(paths: list[Path]) -> set[str]:
    identities: set[str] = set()
    for path in paths:
        for index, row in enumerate(_load_history(path)):
            dataset = row.get("dataset")
            if dataset != "musique":
                continue
            value = row.get("id", row.get("sample_id"))
            identities.add(require_native_string(value, f"{path}[{index}].id"))
    return identities


def _validate_blind_source_row(row: dict[str, Any], row_index: int) -> str:
    native_id = require_native_string(row.get("id"), f"source[{row_index}].id")
    require_native_string(row.get("question"), f"source[{row_index}].question")
    paragraphs = row.get("paragraphs")
    if not isinstance(paragraphs, list) or not paragraphs:
        raise ValueError(f"{native_id}: paragraphs must be a non-empty list")
    for paragraph_index, paragraph in enumerate(paragraphs):
        if not isinstance(paragraph, dict):
            raise ValueError(f"{native_id}: paragraph must be an object")
        bound_index = require_json_int(
            paragraph.get("idx"), f"{native_id}: paragraph.idx"
        )
        if bound_index != paragraph_index:
            raise ValueError(f"{native_id}: paragraph identity/order differs")
        require_native_string(paragraph.get("title"), f"{native_id}: paragraph.title")
        split_sentences(
            paragraph.get("paragraph_text"), f"{native_id}: paragraph.paragraph_text"
        )
    return native_id


def select_rows(
    rows: list[dict[str, Any]], history_ids: set[str], sample_size: int = SAMPLE_SIZE
) -> list[tuple[int, dict[str, Any]]]:
    if isinstance(sample_size, bool) or not isinstance(sample_size, int) or sample_size <= 0:
        raise ValueError("sample_size must be a positive integer")
    seen: set[str] = set()
    candidates: list[tuple[int, dict[str, Any]]] = []
    for row_index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"source[{row_index}] must be an object")
        native_id = _validate_blind_source_row(row, row_index)
        if native_id in seen:
            raise ValueError(f"Duplicate source query ID: {native_id}")
        seen.add(native_id)
        candidates.append((row_index, row))
    if len(candidates) < sample_size:
        raise ValueError("Official source has fewer rows than the frozen sample size")
    selected = sorted(candidates, key=lambda pair: selection_key(pair[1]["id"]))[:sample_size]
    overlap = sorted({row["id"] for _, row in selected} & history_ids)
    if overlap:
        raise ValueError(f"Selected Stage4F IDs overlap historical MuSiQue IDs: {overlap[:3]}")
    return selected


def build_channels_for_row(
    source_row_index: int, row: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    native_id = require_native_string(row.get("id"), "source.id")
    query_id = f"{DATASET}::{native_id}"
    question = require_native_string(row.get("question"), f"{native_id}: question")
    candidate_units: list[dict[str, Any]] = []
    supporting_indices: list[int] = []
    supporting_unit_ids: list[str] = []
    paragraphs = row["paragraphs"]
    for paragraph_index, paragraph in enumerate(paragraphs):
        if require_json_int(paragraph.get("idx"), "paragraph.idx") != paragraph_index:
            raise ValueError(f"{native_id}: paragraph identity/order differs")
        title = require_native_string(paragraph.get("title"), "paragraph.title")
        sentences = split_sentences(paragraph.get("paragraph_text"), "paragraph.text")
        is_supporting = require_json_bool(
            paragraph.get("is_supporting"), "paragraph.is_supporting"
        )
        paragraph_unit_ids = []
        for sentence_index, text in enumerate(sentences):
            unit_id = f"{query_id}::p{paragraph_index}::s{sentence_index}"
            paragraph_unit_ids.append(unit_id)
            candidate_units.append(
                {
                    "dataset": DATASET,
                    "paragraph_index": paragraph_index,
                    "query_id": query_id,
                    "sample_id": native_id,
                    "sentence_index": sentence_index,
                    "text": text,
                    "title": title,
                    "unit_id": unit_id,
                }
            )
        if is_supporting:
            if not paragraph_unit_ids:
                raise ValueError(f"{native_id}: supporting paragraph has no candidate units")
            supporting_indices.append(paragraph_index)
            supporting_unit_ids.extend(paragraph_unit_ids)
    if len(candidate_units) < 21:
        raise ValueError(f"{native_id}: candidate pool is incompatible with Top-20 comparison")
    if any(set(unit) != UNIT_KEYS for unit in candidate_units):
        raise AssertionError("Internal candidate-unit schema error")
    if not supporting_indices:
        raise ValueError(f"{native_id}: no official supporting paragraphs")
    answer = require_native_string(row.get("answer"), f"{native_id}: answer")
    aliases = row.get("answer_aliases")
    if not isinstance(aliases, list) or any(not isinstance(value, str) for value in aliases):
        raise ValueError(f"{native_id}: answer_aliases must contain strings")
    answers = [answer] + [value for value in aliases if value.strip()]
    decomposition = row.get("question_decomposition")
    if not isinstance(decomposition, list) or not decomposition:
        raise ValueError(f"{native_id}: question_decomposition is missing")
    decomposition_indices: list[int] = []
    for item in decomposition:
        if not isinstance(item, dict):
            raise ValueError(f"{native_id}: decomposition item must be an object")
        decomposition_indices.append(
            require_json_int(item.get("paragraph_support_idx"), "paragraph_support_idx")
        )
    if sorted(set(decomposition_indices)) != sorted(supporting_indices):
        raise ValueError(f"{native_id}: supporting-evidence mapping is ambiguous")
    blind = {
        "candidate_units": candidate_units,
        "dataset": DATASET,
        "query_id": query_id,
        "question": question,
        "sample_id": native_id,
    }
    gold = {
        "answers": answers,
        "dataset": DATASET,
        "query_id": query_id,
        "sample_id": native_id,
        "supporting_paragraph_indices": supporting_indices,
        "supporting_unit_ids": supporting_unit_ids,
    }
    metadata = {
        "answer_alias_count": len(answers) - 1,
        "candidate_unit_count": len(candidate_units),
        "dataset": DATASET,
        "hop_count": len(decomposition),
        "query_id": query_id,
        "sample_id": native_id,
        "source_row_index": source_row_index,
        "source_split": "train",
        "supporting_paragraph_count": len(supporting_indices),
    }
    if set(blind) != BLIND_KEYS:
        raise AssertionError("Internal blind-channel schema error")
    assert_no_gold_fields(blind, f"blind[{query_id}]")
    return blind, gold, metadata


def build_frozen_channels(
    rows: list[dict[str, Any]], history_ids: set[str], sample_size: int = SAMPLE_SIZE
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    selected = select_rows(rows, history_ids, sample_size)
    blind: list[dict[str, Any]] = []
    gold: list[dict[str, Any]] = []
    metadata: list[dict[str, Any]] = []
    for source_row_index, row in selected:
        blind_row, gold_row, metadata_row = build_channels_for_row(source_row_index, row)
        blind.append(blind_row)
        gold.append(gold_row)
        metadata.append(metadata_row)
    query_ids = [row["query_id"] for row in blind]
    sample_ids = [row["sample_id"] for row in blind]
    manifest = {
        "candidate_units": {
            "maximum": max(row["candidate_unit_count"] for row in metadata),
            "minimum": min(row["candidate_unit_count"] for row in metadata),
            "total": sum(row["candidate_unit_count"] for row in metadata),
        },
        "checks": {
            "formal_metrics_computed": False,
            "gold_fields_in_blind": False,
            "historical_musique_overlap": 0,
            "sample_selection_used_gold": False,
        },
        "historical_native_id_count": len(history_ids),
        "historical_native_id_sha256": id_digest(sorted(history_ids)),
        "query_id_sha256": id_digest(query_ids),
        "sample_id_sha256": id_digest(sample_ids),
        "sample_size": len(blind),
        "schema_version": SCHEMA_VERSION,
        "selection_order": "(SHA256(stage4f_xdr_v1\\0 + dataset + \\0 + native_id), native_id)",
        "sentence_splitter": "stage4f_regex_sentence_splitter_v1",
        "source": {"bytes": SOURCE_BYTES, "rows": len(rows), "sha256": SOURCE_SHA256},
        "status": "STAGE4F_INPUT_CHANNELS_BUILT_PENDING_INDEPENDENT_VERIFICATION",
    }
    return blind, gold, metadata, manifest


def _path(config: dict[str, Any], key: str) -> Path:
    return Path(require_native_string(config.get("paths", {}).get(key), f"paths.{key}"))


def run(config: dict[str, Any]) -> None:
    if config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Stage4F config schema differs")
    binding = config.get("input_binding")
    if not isinstance(binding, dict) or require_json_bool(
        binding.get("authorized"), "input_binding.authorized"
    ) is not True:
        raise PermissionError("STAGE4F_INPUT_BINDING_NOT_AUTHORIZED")
    source_path = _path(config, "source")
    assert_file_identity(source_path, {"bytes": SOURCE_BYTES, "sha256": SOURCE_SHA256}, "source")
    history_config = config.get("historical_inputs")
    if not isinstance(history_config, list) or not history_config:
        raise ValueError("historical_inputs binding is missing")
    history_paths: list[Path] = []
    for index, item in enumerate(history_config):
        if not isinstance(item, dict):
            raise ValueError("historical_inputs row must be an object")
        path = Path(require_native_string(item.get("path"), f"historical_inputs[{index}].path"))
        assert_file_identity(path, item, f"historical_inputs[{index}]")
        history_paths.append(path)
    rows = load_jsonl(source_path)
    blind, gold, metadata, manifest = build_frozen_channels(
        rows, historical_native_ids(history_paths), SAMPLE_SIZE
    )
    blind_payload = render_jsonl(blind)
    gold_payload = render_jsonl(gold)
    metadata_payload = render_jsonl(metadata)
    manifest["channels"] = {
        "blind": {"bytes": len(blind_payload), "sha256": sha256_bytes(blind_payload)},
        "gold": {"bytes": len(gold_payload), "rows": len(gold), "sha256": sha256_bytes(gold_payload)},
        "metadata": {"bytes": len(metadata_payload), "rows": len(metadata), "sha256": sha256_bytes(metadata_payload)},
    }
    write_new_files_atomically(
        (
            (_path(config, "blind"), blind_payload),
            (_path(config, "gold"), gold_payload),
            (_path(config, "metadata"), metadata_payload),
            (_path(config, "input_manifest"), render_json(manifest)),
        )
    )
    print(f"STAGE4F_INPUT_CHANNELS_BUILT_PENDING_VERIFICATION queries={len(blind)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage4F config must be an object")
    run(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE4F_PREPARE_FAIL: {exc}", file=sys.stderr)
        raise
