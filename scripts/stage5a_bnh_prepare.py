"""Freeze zero-overlap Stage5A development and confirmation channels."""

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
from stage5a_bnh_common import (
    BOUNDARIES,
    DATASET_KEYS,
    DATASETS,
    HOTPOT_DATASET,
    MUSIQUE_DATASET,
    SAMPLE_SIZES,
    SCHEMA_VERSION,
    assert_file_identity,
    assert_implementation_binding,
    assert_no_gold_fields,
    file_identity,
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
    boundary: str,
) -> list[tuple[int, str, dict[str, Any]]]:
    candidates = [
        row for row in _validate_source_ids(rows, dataset) if row[1] not in excluded
    ]
    if len(candidates) < sample_size:
        raise ValueError(f"{dataset}/{boundary}: insufficient eligible source rows")
    return sorted(
        candidates,
        key=lambda row: selection_key(
            boundary, DATASET_KEYS[dataset], row[1]
        ),
    )[:sample_size]


def build_boundary(
    boundary: str,
    source_rows: dict[str, list[dict[str, Any]]],
    excluded: dict[str, set[str]],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, str]],
]:
    selected = {
        dataset: select_rows(
            source_rows[dataset],
            dataset,
            excluded[dataset],
            SAMPLE_SIZES[boundary][dataset],
            boundary,
        )
        for dataset in DATASETS
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
            assert_no_gold_fields(blind, f"{boundary}.blind[{blind['query_id']}]")
            if not blind["candidate_units"]:
                raise ValueError(f"{blind['query_id']}: empty candidate pool")
            blind_rows.append(blind)
            gold_rows.append(gold)
            metadata_rows.append(metadata)
            selection_rows.append(
                {
                    "boundary": boundary,
                    "dataset": dataset,
                    "query_id": blind["query_id"],
                    "sample_id": sample_id,
                    "selection_key": selection_key(
                        boundary, DATASET_KEYS[dataset], sample_id
                    )[0],
                }
            )
    expected = sum(SAMPLE_SIZES[boundary].values())
    if len(blind_rows) != expected or len(
        {row["query_id"] for row in blind_rows}
    ) != expected:
        raise ValueError(f"{boundary}: query identities differ")
    return blind_rows, gold_rows, metadata_rows, selection_rows


def frozen_preexisting_manifest(
    repository_root: Path, patterns: list[str]
) -> dict[str, Any]:
    if not patterns or any(not isinstance(value, str) or not value for value in patterns):
        raise ValueError("frozen_preexisting_globs must be non-empty strings")
    paths: set[Path] = set()
    for pattern in patterns:
        for path in repository_root.glob(pattern):
            if path.is_file():
                paths.add(path)
    if not paths:
        raise ValueError("frozen pre-existing artifact set is empty")
    rows = []
    for path in sorted(paths):
        relative = path.relative_to(repository_root).as_posix()
        identity = file_identity(path)
        rows.append({"path": relative, **identity})
    return {
        "files": rows,
        "file_count": len(rows),
        "scope": "STAGE4E_THROUGH_STAGE4I_AND_STAGE5_PMC_FROZEN_BASELINE",
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE5A_PREEXISTING_ARTIFACT_BASELINE_FROZEN",
    }


def run(config: dict[str, Any]) -> None:
    validate_authorization(config)
    repository_root = Path(__file__).resolve().parents[1]
    assert_implementation_binding(config, repository_root)
    parent = load_parent_config(config)
    sources = parent.get("sources")
    if not isinstance(sources, dict):
        raise ValueError("Stage4H parent sources binding is missing")
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
        or len(additional) != 2
    ):
        raise ValueError("Stage5A historical bindings are incomplete")
    history, history_audit = historical_ids(parent_history + additional)
    original_history = {dataset: set(values) for dataset, values in history.items()}

    channels: dict[str, dict[str, Any]] = {}
    selected_ids = {dataset: set() for dataset in DATASETS}
    for boundary in BOUNDARIES:
        blind, gold, metadata, selection = build_boundary(
            boundary, source_rows, history
        )
        for row in blind:
            if row["sample_id"] in history[row["dataset"]]:
                raise ValueError(f"{boundary}: selected historical overlap")
            history[row["dataset"]].add(row["sample_id"])
            selected_ids[row["dataset"]].add(row["sample_id"])
        channels[boundary] = {
            "blind": blind,
            "gold": gold,
            "metadata": metadata,
            "selection": selection,
        }

    development_ids = {
        row["sample_id"] for row in channels["development"]["blind"]
    }
    confirmation_ids = {
        row["sample_id"] for row in channels["confirmation"]["blind"]
    }
    if development_ids & confirmation_ids:
        raise ValueError("Stage5A development/confirmation overlap")

    manifest: dict[str, Any] = {
        "boundaries": {},
        "checks": {
            "development_confirmation_overlap": 0,
            "gold_fields_in_blind": False,
            "historical_overlap": 0,
            "selection_used_gold_or_metadata": False,
        },
        "historical_files": history_audit,
        "historical_native_ids": {
            dataset: {
                "count": len(original_history[dataset]),
                "sha256": id_digest(sorted(original_history[dataset])),
            }
            for dataset in DATASETS
        },
        "schema_version": SCHEMA_VERSION,
        "selection_contract": (
            "SHA256(boundary_salt + dataset_key + NUL + native_id), native_id"
        ),
        "status": "STAGE5A_INPUT_CHANNELS_BUILT_PENDING_INDEPENDENT_VERIFICATION",
    }
    outputs: list[tuple[Path, bytes]] = []
    for boundary in BOUNDARIES:
        payloads = {
            key: render_jsonl(channels[boundary][key])
            for key in ("blind", "gold", "metadata")
        }
        manifest["boundaries"][boundary] = {
            "candidate_units": {
                dataset: {
                    "maximum": max(
                        len(row["candidate_units"])
                        for row in channels[boundary]["blind"]
                        if row["dataset"] == dataset
                    ),
                    "minimum": min(
                        len(row["candidate_units"])
                        for row in channels[boundary]["blind"]
                        if row["dataset"] == dataset
                    ),
                    "total": sum(
                        len(row["candidate_units"])
                        for row in channels[boundary]["blind"]
                        if row["dataset"] == dataset
                    ),
                }
                for dataset in DATASETS
            },
            "channels": {
                key: {
                    "bytes": len(payload),
                    "rows": len(channels[boundary]["blind"]),
                    "sha256": sha256_bytes(payload),
                }
                for key, payload in payloads.items()
            },
            "query_id_sha256": id_digest(
                row["query_id"] for row in channels[boundary]["blind"]
            ),
            "sample_sizes": SAMPLE_SIZES[boundary],
            "selected_native_id_sha256": {
                dataset: id_digest(
                    sorted(
                        row["sample_id"]
                        for row in channels[boundary]["blind"]
                        if row["dataset"] == dataset
                    )
                )
                for dataset in DATASETS
            },
            "selection_rows": channels[boundary]["selection"],
        }
        outputs.extend(
            (
                (
                    path_from_config(config, f"{boundary}_blind"),
                    payloads["blind"],
                ),
                (
                    path_from_config(config, f"{boundary}_gold"),
                    payloads["gold"],
                ),
                (
                    path_from_config(config, f"{boundary}_metadata"),
                    payloads["metadata"],
                ),
            )
        )

    frozen_manifest = frozen_preexisting_manifest(
        repository_root, config.get("frozen_preexisting_globs", [])
    )
    outputs.extend(
        (
            (path_from_config(config, "input_manifest"), render_json(manifest)),
            (
                path_from_config(config, "preexisting_frozen_manifest"),
                render_json(frozen_manifest),
            ),
        )
    )
    write_new_files_atomically(outputs)
    print(
        "STAGE5A_INPUT_CHANNELS_BUILT_PENDING_INDEPENDENT_VERIFICATION "
        "development=1250 confirmation=2500 historical_overlap=0 "
        "development_confirmation_overlap=0"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage5A config must be an object")
    run(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE5A_PREPARE_FAIL: {exc}", file=sys.stderr)
        raise
