"""Freeze zero-overlap Stage4I blind, Gold, and metadata channels."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from stage4h_cbe_prepare import (
    _rows,
    _validate_source_ids,
    build_hotpot_channels,
    build_musique_channels,
    historical_ids,
)
from stage4i_sdc_common import (
    DATASET_KEYS,
    DATASETS,
    HOTPOT_DATASET,
    MUSIQUE_DATASET,
    SAMPLE_SIZES,
    SCHEMA_VERSION,
    assert_file_identity,
    assert_implementation_binding,
    assert_no_gold_fields,
    id_digest,
    load_json,
    load_parent_config,
    path_from_config,
    render_json,
    render_jsonl,
    require_native_string,
    selection_key,
    sha256_bytes,
    validate_authorization,
    write_new_files_atomically,
)


def select_rows(
    rows: list[dict[str, Any]],
    dataset: str,
    excluded: set[str],
    sample_size: int,
) -> list[tuple[int, str, dict[str, Any]]]:
    candidates = [
        row for row in _validate_source_ids(rows, dataset) if row[1] not in excluded
    ]
    if len(candidates) < sample_size:
        raise ValueError(f"{dataset}: fewer eligible source rows than requested")
    return sorted(
        candidates,
        key=lambda row: selection_key(DATASET_KEYS[dataset], row[1]),
    )[:sample_size]


def build_channels(
    hotpot_rows: list[dict[str, Any]],
    musique_rows: list[dict[str, Any]],
    history: dict[str, set[str]],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
]:
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
    for dataset in DATASETS:
        for source_row_index, sample_id, source_row in selected[dataset]:
            if dataset == HOTPOT_DATASET:
                blind, gold, metadata = build_hotpot_channels(
                    source_row_index, sample_id, source_row
                )
            else:
                blind, gold, metadata = build_musique_channels(
                    source_row_index, sample_id, source_row
                )
            assert_no_gold_fields(blind, f"blind[{blind['query_id']}]")
            if not blind["candidate_units"]:
                raise ValueError(f"{blind['query_id']}: empty candidate pool")
            blind_rows.append(blind)
            gold_rows.append(gold)
            metadata_rows.append(metadata)
            selection_rows.append(
                {
                    "dataset": dataset,
                    "query_id": blind["query_id"],
                    "sample_id": sample_id,
                    "selection_key": selection_key(
                        DATASET_KEYS[dataset], sample_id
                    )[0],
                }
            )
    if len({row["query_id"] for row in blind_rows}) != sum(SAMPLE_SIZES.values()):
        raise ValueError("Stage4I query identities are not unique")
    manifest = {
        "candidate_units": {
            dataset: {
                "maximum": max(
                    len(row["candidate_units"])
                    for row in blind_rows
                    if row["dataset"] == dataset
                ),
                "minimum": min(
                    len(row["candidate_units"])
                    for row in blind_rows
                    if row["dataset"] == dataset
                ),
                "total": sum(
                    len(row["candidate_units"])
                    for row in blind_rows
                    if row["dataset"] == dataset
                ),
            }
            for dataset in DATASETS
        },
        "checks": {
            "gold_fields_in_blind": False,
            "historical_overlap": 0,
            "selection_used_gold_or_metadata": False,
        },
        "historical_native_ids": {
            dataset: {
                "count": len(history[dataset]),
                "sha256": id_digest(sorted(history[dataset])),
            }
            for dataset in DATASETS
        },
        "query_id_sha256": id_digest(row["query_id"] for row in blind_rows),
        "sample_id_sha256": id_digest(row["sample_id"] for row in blind_rows),
        "schema_version": SCHEMA_VERSION,
        "selection": selection_rows,
        "selection_contract": (
            "SHA256(stage4i_sdc_v1\\0 + dataset_key + NUL + native_id), native_id"
        ),
        "status": "STAGE4I_INPUT_CHANNELS_BUILT_PENDING_VERIFICATION",
    }
    return blind_rows, gold_rows, metadata_rows, manifest


def run(config: dict[str, Any]) -> None:
    validate_authorization(config)
    assert_implementation_binding(config, Path(__file__).resolve().parents[1])
    parent = load_parent_config(config)
    sources = parent.get("sources")
    if not isinstance(sources, dict):
        raise ValueError("Stage4H parent source bindings are missing")
    source_rows: dict[str, list[dict[str, Any]]] = {}
    for key, dataset in (("hotpotqa", HOTPOT_DATASET), ("musique", MUSIQUE_DATASET)):
        binding = sources.get(key)
        if not isinstance(binding, dict):
            raise ValueError(f"parent sources.{key} binding is missing")
        path = Path(require_native_string(binding.get("path"), f"sources.{key}.path"))
        assert_file_identity(path, binding, f"sources.{key}")
        source_rows[dataset] = _rows(path)
    parent_history = parent.get("historical_inputs")
    additional = config.get("additional_historical_inputs")
    if (
        not isinstance(parent_history, list)
        or not isinstance(additional, list)
        or not additional
    ):
        raise ValueError("Stage4I historical bindings are incomplete")
    history, history_audit = historical_ids(parent_history + additional)
    blind, gold, metadata, manifest = build_channels(
        source_rows[HOTPOT_DATASET],
        source_rows[MUSIQUE_DATASET],
        history,
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
        "STAGE4I_INPUT_CHANNELS_BUILT_PENDING_VERIFICATION "
        f"queries={len(blind)} hotpot={SAMPLE_SIZES[HOTPOT_DATASET]} "
        f"musique={SAMPLE_SIZES[MUSIQUE_DATASET]} overlap=0"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage4I config must be an object")
    run(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE4I_PREPARE_FAIL: {exc}", file=sys.stderr)
        raise
