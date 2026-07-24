"""Freeze zero-overlap Stage4H blind, Gold, and metadata channels."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from stage4f_xdr_common import split_sentences
from stage4h_cbe_common import (
    DATASET_KEYS,
    HOTPOT_DATASET,
    MUSIQUE_DATASET,
    SAMPLE_SIZES,
    SCHEMA_VERSION,
    assert_file_identity,
    assert_no_gold_fields,
    file_identity,
    id_digest,
    load_json,
    load_jsonl,
    normalize_sentence,
    path_from_config,
    render_json,
    render_jsonl,
    require_json_bool,
    require_json_int,
    require_native_string,
    selection_key,
    sha256_bytes,
    write_new_files_atomically,
)


BLIND_KEYS = {"candidate_units", "dataset", "query_id", "question", "sample_id"}
UNIT_KEYS = {
    "dataset",
    "document_id",
    "paragraph_index",
    "query_id",
    "sample_id",
    "sentence_index",
    "text",
    "title",
    "unit_id",
}


def _rows(path: Path) -> list[dict[str, Any]]:
    value = load_jsonl(path) if path.suffix.lower() == ".jsonl" else load_json(path)
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise ValueError(f"Expected object-row list: {path}")
    return value


def _history_dataset(row: dict[str, Any], path: Path) -> str | None:
    dataset = row.get("dataset")
    if isinstance(dataset, str):
        lowered = dataset.lower()
        if "hotpot" in lowered:
            return HOTPOT_DATASET
        if "musique" in lowered:
            return MUSIQUE_DATASET
    lowered_name = path.name.lower()
    if "hotpot" in lowered_name:
        return HOTPOT_DATASET
    if "musique" in lowered_name:
        return MUSIQUE_DATASET
    return None


def _native_id(row: dict[str, Any], label: str) -> str:
    for key in ("sample_id", "_id", "id"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value
    raise ValueError(f"{label} has no native string ID")


def historical_ids(
    bindings: list[dict[str, Any]],
) -> tuple[dict[str, set[str]], list[dict[str, Any]]]:
    result = {HOTPOT_DATASET: set(), MUSIQUE_DATASET: set()}
    audits: list[dict[str, Any]] = []
    seen_paths: set[Path] = set()
    for index, binding in enumerate(bindings):
        if not isinstance(binding, dict):
            raise ValueError(f"historical_inputs[{index}] must be an object")
        path = Path(
            require_native_string(binding.get("path"), f"historical_inputs[{index}].path")
        )
        resolved = path.resolve()
        if resolved in seen_paths:
            raise ValueError(f"Duplicate historical input binding: {path}")
        seen_paths.add(resolved)
        assert_file_identity(path, binding, f"historical_inputs[{index}]")
        counts: Counter[str] = Counter()
        for row_index, row in enumerate(_rows(path)):
            dataset = _history_dataset(row, path)
            if dataset is None:
                continue
            value = _native_id(row, f"{path}[{row_index}]")
            result[dataset].add(value)
            counts[dataset] += 1
        audits.append(
            {
                "bytes": binding["bytes"],
                "dataset_rows": dict(sorted(counts.items())),
                "path": str(path),
                "sha256": binding["sha256"],
            }
        )
    return result, audits


def _validate_source_ids(
    rows: list[dict[str, Any]], dataset: str
) -> list[tuple[int, str, dict[str, Any]]]:
    key = "_id" if dataset == HOTPOT_DATASET else "id"
    seen: set[str] = set()
    result: list[tuple[int, str, dict[str, Any]]] = []
    for row_index, row in enumerate(rows):
        native_id = require_native_string(row.get(key), f"{dataset}[{row_index}].{key}")
        if native_id in seen:
            raise ValueError(f"{dataset}: duplicate source ID: {native_id}")
        seen.add(native_id)
        result.append((row_index, native_id, row))
    return result


def select_rows(
    rows: list[dict[str, Any]],
    dataset: str,
    excluded: set[str],
    sample_size: int,
) -> list[tuple[int, str, dict[str, Any]]]:
    candidates = [
        item for item in _validate_source_ids(rows, dataset) if item[1] not in excluded
    ]
    if len(candidates) < sample_size:
        raise ValueError(f"{dataset}: fewer eligible rows than sample size")
    dataset_key = DATASET_KEYS[dataset]
    return sorted(candidates, key=lambda item: selection_key(dataset_key, item[1]))[
        :sample_size
    ]


def _unit(
    dataset: str,
    query_id: str,
    sample_id: str,
    paragraph_index: int,
    sentence_index: int,
    title: str,
    text: str,
) -> dict[str, Any]:
    unit_id = f"{query_id}::p{paragraph_index}::s{sentence_index}"
    return {
        "dataset": dataset,
        "document_id": f"{query_id}::p{paragraph_index}",
        "paragraph_index": paragraph_index,
        "query_id": query_id,
        "sample_id": sample_id,
        "sentence_index": sentence_index,
        "text": text,
        "title": title,
        "unit_id": unit_id,
    }


def build_hotpot_channels(
    row_index: int, sample_id: str, row: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    query_id = f"{HOTPOT_DATASET}::{sample_id}"
    question = require_native_string(row.get("question"), f"{sample_id}.question")
    context = row.get("context")
    if not isinstance(context, list) or not context:
        raise ValueError(f"{sample_id}: context must be non-empty")
    units: list[dict[str, Any]] = []
    support_map: dict[tuple[str, int], str] = {}
    for paragraph_index, item in enumerate(context):
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError(f"{sample_id}: context[{paragraph_index}] contract differs")
        title = require_native_string(item[0], f"{sample_id}.context.title")
        sentences = item[1]
        if not isinstance(sentences, list) or not sentences:
            raise ValueError(f"{sample_id}: context sentences must be non-empty")
        for sentence_index, raw_sentence in enumerate(sentences):
            text = normalize_sentence(raw_sentence)
            if not text:
                continue
            unit = _unit(
                HOTPOT_DATASET,
                query_id,
                sample_id,
                paragraph_index,
                sentence_index,
                title,
                text,
            )
            units.append(unit)
            key = (title, sentence_index)
            if key in support_map:
                raise ValueError(f"{sample_id}: ambiguous support mapping {key}")
            support_map[key] = unit["unit_id"]
    supporting = row.get("supporting_facts")
    if not isinstance(supporting, list) or not supporting:
        raise ValueError(f"{sample_id}: supporting_facts missing")
    supporting_unit_ids: list[str] = []
    for support_index, item in enumerate(supporting):
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError(f"{sample_id}: supporting_facts[{support_index}] differs")
        title = require_native_string(item[0], f"{sample_id}.support.title")
        sentence_index = require_json_int(item[1], f"{sample_id}.support.index")
        key = (title, sentence_index)
        if key not in support_map:
            raise ValueError(f"{sample_id}: support target is absent from candidates")
        supporting_unit_ids.append(support_map[key])
    if len(supporting_unit_ids) != len(set(supporting_unit_ids)):
        raise ValueError(f"{sample_id}: duplicate supporting unit")
    blind = {
        "candidate_units": units,
        "dataset": HOTPOT_DATASET,
        "query_id": query_id,
        "question": question,
        "sample_id": sample_id,
    }
    gold = {
        "answers": [require_native_string(row.get("answer"), f"{sample_id}.answer")],
        "dataset": HOTPOT_DATASET,
        "evidence_granularity": "official_supporting_sentence",
        "query_id": query_id,
        "sample_id": sample_id,
        "supporting_unit_ids": supporting_unit_ids,
    }
    metadata = {
        "candidate_unit_count": len(units),
        "dataset": HOTPOT_DATASET,
        "level": require_native_string(row.get("level"), f"{sample_id}.level"),
        "query_id": query_id,
        "sample_id": sample_id,
        "source_row_index": row_index,
        "source_split": "train",
        "supporting_evidence_count": len(supporting_unit_ids),
        "type": require_native_string(row.get("type"), f"{sample_id}.type"),
    }
    return blind, gold, metadata


def build_musique_channels(
    row_index: int, sample_id: str, row: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    query_id = f"{MUSIQUE_DATASET}::{sample_id}"
    question = require_native_string(row.get("question"), f"{sample_id}.question")
    paragraphs = row.get("paragraphs")
    if not isinstance(paragraphs, list) or not paragraphs:
        raise ValueError(f"{sample_id}: paragraphs must be non-empty")
    units: list[dict[str, Any]] = []
    supporting_paragraph_indices: list[int] = []
    for paragraph_index, paragraph in enumerate(paragraphs):
        if not isinstance(paragraph, dict):
            raise ValueError(f"{sample_id}: paragraph must be an object")
        if require_json_int(paragraph.get("idx"), f"{sample_id}.paragraph.idx") != paragraph_index:
            raise ValueError(f"{sample_id}: paragraph identity/order differs")
        title = require_native_string(paragraph.get("title"), f"{sample_id}.paragraph.title")
        sentences = split_sentences(
            paragraph.get("paragraph_text"), f"{sample_id}.paragraph.text"
        )
        for sentence_index, text in enumerate(sentences):
            units.append(
                _unit(
                    MUSIQUE_DATASET,
                    query_id,
                    sample_id,
                    paragraph_index,
                    sentence_index,
                    title,
                    text,
                )
            )
        if require_json_bool(
            paragraph.get("is_supporting"), f"{sample_id}.paragraph.is_supporting"
        ):
            supporting_paragraph_indices.append(paragraph_index)
    if not supporting_paragraph_indices:
        raise ValueError(f"{sample_id}: no official supporting paragraph")
    answer = require_native_string(row.get("answer"), f"{sample_id}.answer")
    aliases = row.get("answer_aliases")
    if not isinstance(aliases, list) or any(not isinstance(item, str) for item in aliases):
        raise ValueError(f"{sample_id}: answer_aliases must be strings")
    decomposition = row.get("question_decomposition")
    if not isinstance(decomposition, list) or not decomposition:
        raise ValueError(f"{sample_id}: question_decomposition missing")
    decomposition_support_values: list[int] = []
    for item in decomposition:
        if not isinstance(item, dict):
            raise ValueError(f"{sample_id}: decomposition item must be an object")
        decomposition_support_values.append(
            require_json_int(item.get("paragraph_support_idx"), "paragraph_support_idx")
        )
    decomposition_support = sorted(set(decomposition_support_values))
    if decomposition_support != sorted(supporting_paragraph_indices):
        raise ValueError(f"{sample_id}: decomposition/support mapping differs")
    blind = {
        "candidate_units": units,
        "dataset": MUSIQUE_DATASET,
        "query_id": query_id,
        "question": question,
        "sample_id": sample_id,
    }
    gold = {
        "answers": [answer] + [item for item in aliases if item.strip()],
        "dataset": MUSIQUE_DATASET,
        "evidence_granularity": "official_supporting_paragraph",
        "query_id": query_id,
        "sample_id": sample_id,
        "supporting_paragraph_indices": supporting_paragraph_indices,
    }
    metadata = {
        "answer_alias_count": len(gold["answers"]) - 1,
        "candidate_unit_count": len(units),
        "dataset": MUSIQUE_DATASET,
        "hop_count": len(decomposition),
        "query_id": query_id,
        "sample_id": sample_id,
        "source_row_index": row_index,
        "source_split": "train",
        "supporting_evidence_count": len(supporting_paragraph_indices),
    }
    return blind, gold, metadata


def build_all_channels(
    hotpot_rows: list[dict[str, Any]],
    musique_rows: list[dict[str, Any]],
    history: dict[str, set[str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    selected = {
        HOTPOT_DATASET: select_rows(
            hotpot_rows,
            HOTPOT_DATASET,
            history[HOTPOT_DATASET],
            SAMPLE_SIZES[HOTPOT_DATASET],
        ),
        MUSIQUE_DATASET: select_rows(
            musique_rows,
            MUSIQUE_DATASET,
            history[MUSIQUE_DATASET],
            SAMPLE_SIZES[MUSIQUE_DATASET],
        ),
    }
    blind_rows: list[dict[str, Any]] = []
    gold_rows: list[dict[str, Any]] = []
    metadata_rows: list[dict[str, Any]] = []
    selection_rows: list[dict[str, str]] = []
    for dataset in (HOTPOT_DATASET, MUSIQUE_DATASET):
        for row_index, sample_id, row in selected[dataset]:
            if dataset == HOTPOT_DATASET:
                blind, gold, metadata = build_hotpot_channels(row_index, sample_id, row)
            else:
                blind, gold, metadata = build_musique_channels(row_index, sample_id, row)
            if set(blind) != BLIND_KEYS or any(set(unit) != UNIT_KEYS for unit in blind["candidate_units"]):
                raise AssertionError("Internal blind/unit schema error")
            if not blind["candidate_units"]:
                raise ValueError(f"{blind['query_id']}: empty candidate pool")
            assert_no_gold_fields(blind, f"blind[{blind['query_id']}]")
            blind_rows.append(blind)
            gold_rows.append(gold)
            metadata_rows.append(metadata)
            selection_rows.append(
                {
                    "dataset": dataset,
                    "query_id": blind["query_id"],
                    "sample_id": sample_id,
                    "selection_key": selection_key(DATASET_KEYS[dataset], sample_id)[0],
                }
            )
    if len({row["query_id"] for row in blind_rows}) != len(blind_rows):
        raise ValueError("Combined query IDs are not unique")
    manifest = {
        "candidate_units": {
            dataset: {
                "maximum": max(
                    row["candidate_unit_count"]
                    for row in metadata_rows
                    if row["dataset"] == dataset
                ),
                "minimum": min(
                    row["candidate_unit_count"]
                    for row in metadata_rows
                    if row["dataset"] == dataset
                ),
                "total": sum(
                    row["candidate_unit_count"]
                    for row in metadata_rows
                    if row["dataset"] == dataset
                ),
            }
            for dataset in (HOTPOT_DATASET, MUSIQUE_DATASET)
        },
        "checks": {
            "gold_fields_in_blind": False,
            "historical_overlap": 0,
            "sample_selection_used_gold_or_metadata": False,
        },
        "historical_native_ids": {
            dataset: {
                "count": len(history[dataset]),
                "sha256": id_digest(sorted(history[dataset])),
            }
            for dataset in (HOTPOT_DATASET, MUSIQUE_DATASET)
        },
        "query_id_sha256": id_digest(row["query_id"] for row in blind_rows),
        "sample_id_sha256": id_digest(row["sample_id"] for row in blind_rows),
        "schema_version": SCHEMA_VERSION,
        "selection": selection_rows,
        "selection_contract": (
            "SHA256(stage4h_cbe_v1\\0 + dataset_key + NUL + native_id), native_id"
        ),
        "status": "STAGE4H_INPUT_CHANNELS_BUILT_PENDING_VERIFICATION",
    }
    return blind_rows, gold_rows, metadata_rows, manifest


def run(config: dict[str, Any]) -> None:
    if config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Stage4H config schema differs")
    authorization = config.get("official_execution")
    if not isinstance(authorization, dict) or require_json_bool(
        authorization.get("authorized"), "official_execution.authorized"
    ) is not True:
        raise PermissionError("STAGE4H_EXECUTION_NOT_AUTHORIZED")
    sources = config.get("sources")
    if not isinstance(sources, dict):
        raise ValueError("sources binding is missing")
    source_rows: dict[str, list[dict[str, Any]]] = {}
    for key, dataset in (("hotpotqa", HOTPOT_DATASET), ("musique", MUSIQUE_DATASET)):
        binding = sources.get(key)
        if not isinstance(binding, dict):
            raise ValueError(f"sources.{key} binding is missing")
        path = Path(require_native_string(binding.get("path"), f"sources.{key}.path"))
        assert_file_identity(path, binding, f"sources.{key}")
        source_rows[dataset] = _rows(path)
    history_bindings = config.get("historical_inputs")
    if not isinstance(history_bindings, list) or not history_bindings:
        raise ValueError("historical_inputs binding is missing")
    history, history_audit = historical_ids(history_bindings)
    blind, gold, metadata, manifest = build_all_channels(
        source_rows[HOTPOT_DATASET], source_rows[MUSIQUE_DATASET], history
    )
    manifest["history_files"] = history_audit
    manifest["sources"] = {
        key: {
            "bytes": sources[key]["bytes"],
            "path": sources[key]["path"],
            "rows": len(source_rows[dataset]),
            "sha256": sources[key]["sha256"],
        }
        for key, dataset in (("hotpotqa", HOTPOT_DATASET), ("musique", MUSIQUE_DATASET))
    }
    payloads = {
        "blind": render_jsonl(blind),
        "gold": render_jsonl(gold),
        "metadata": render_jsonl(metadata),
    }
    manifest["channels"] = {
        key: {
            "bytes": len(payload),
            "rows": len(blind),
            "sha256": sha256_bytes(payload),
        }
        for key, payload in payloads.items()
    }
    write_new_files_atomically(
        (
            (path_from_config(config, "blind"), payloads["blind"]),
            (path_from_config(config, "gold"), payloads["gold"]),
            (path_from_config(config, "metadata"), payloads["metadata"]),
            (path_from_config(config, "input_manifest"), render_json(manifest)),
        )
    )
    print(
        "STAGE4H_INPUT_CHANNELS_BUILT_PENDING_VERIFICATION "
        f"queries={len(blind)} hotpot={SAMPLE_SIZES[HOTPOT_DATASET]} "
        f"musique={SAMPLE_SIZES[MUSIQUE_DATASET]} overlap=0"
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
        print(f"STAGE4H_PREPARE_FAIL: {exc}", file=sys.stderr)
        raise
