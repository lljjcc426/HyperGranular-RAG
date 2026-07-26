"""Build the frozen Stage6A development/confirmation channel transaction."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from stage4a_r2_extract_official import fully_mappable, normalize_record
from stage4h_cbe_prepare import (
    _rows,
    _unit,
    build_hotpot_channels,
    build_musique_channels,
)
from stage6a_smc_common import (
    BOUNDARIES,
    DATASETS,
    DATASET_KEYS,
    HOTPOT_DATASET,
    MUSIQUE_DATASET,
    SAMPLE_SIZES,
    SCHEMA_VERSION,
    TWOWIKI_DATASET,
    assert_file_identity,
    assert_implementation_binding,
    assert_no_gold_fields,
    file_identity,
    id_digest,
    load_json,
    path_from_config,
    render_json,
    render_jsonl,
    require_json_int,
    require_native_string,
    selection_key,
    sha256_bytes,
    validate_authorization,
    write_new_files_atomically,
)


TWOWIKI_START = 9819
TWOWIKI_END = 12576
TWOWIKI_EXPECTED_ROWS = 12576


def _native_source_id(row: dict[str, Any], dataset: str, label: str) -> str:
    keys = {
        HOTPOT_DATASET: ("sample_id", "_id", "id"),
        MUSIQUE_DATASET: ("sample_id", "id", "_id"),
        TWOWIKI_DATASET: ("sample_id", "_id", "id"),
    }[dataset]
    for key in keys:
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value
    raise ValueError(f"{label}: no native non-empty string ID")


def _dataset_from_history(row: dict[str, Any], path: Path) -> str | None:
    value = row.get("dataset")
    text = value.lower() if isinstance(value, str) else path.name.lower()
    if "hotpot" in text:
        return HOTPOT_DATASET
    if "musique" in text:
        return MUSIQUE_DATASET
    if "2wiki" in text or "wikimultihop" in text:
        return TWOWIKI_DATASET
    return None


def historical_ids(
    bindings: list[dict[str, Any]],
) -> tuple[dict[str, set[str]], list[dict[str, Any]]]:
    result = {dataset: set() for dataset in DATASETS}
    audits: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for index, binding in enumerate(bindings):
        if not isinstance(binding, dict):
            raise ValueError(f"historical_inputs[{index}] must be an object")
        path = Path(
            require_native_string(binding.get("path"), f"historical_inputs[{index}].path")
        )
        resolved = path.resolve()
        if resolved in seen:
            raise ValueError(f"duplicate historical input: {path}")
        seen.add(resolved)
        assert_file_identity(path, binding, f"historical_inputs[{index}]")
        counts: Counter[str] = Counter()
        for row_index, row in enumerate(_rows(path)):
            dataset = _dataset_from_history(row, path)
            if dataset is None:
                continue
            native_id = _native_source_id(
                row, dataset, f"{path}[{row_index}]"
            )
            result[dataset].add(native_id)
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
    rows: list[dict[str, Any]], dataset: str, start: int = 0, end: int | None = None
) -> list[tuple[int, str, dict[str, Any]]]:
    end = len(rows) if end is None else end
    seen: set[str] = set()
    result: list[tuple[int, str, dict[str, Any]]] = []
    for source_row_index in range(start, end):
        row = rows[source_row_index]
        native_id = _native_source_id(
            row, dataset, f"{dataset}[{source_row_index}]"
        )
        if native_id in seen:
            raise ValueError(f"{dataset}: duplicate source ID: {native_id}")
        seen.add(native_id)
        if dataset == TWOWIKI_DATASET:
            _, diagnostics = normalize_record(row)
            if not fully_mappable(diagnostics):
                continue
        result.append((source_row_index, native_id, row))
    return result


def select_partitions(
    source_rows: dict[str, list[dict[str, Any]]],
    excluded: dict[str, set[str]],
) -> dict[str, dict[str, list[tuple[int, str, dict[str, Any]]]]]:
    output = {boundary: {} for boundary in BOUNDARIES}
    for dataset in DATASETS:
        start, end = (
            (TWOWIKI_START, TWOWIKI_END)
            if dataset == TWOWIKI_DATASET
            else (0, len(source_rows[dataset]))
        )
        eligible = [
            item
            for item in _validate_source_ids(source_rows[dataset], dataset, start, end)
            if item[1] not in excluded[dataset]
        ]
        ordered = sorted(
            eligible,
            key=lambda item: selection_key(
                DATASET_KEYS[dataset], item[1], item[0]
            ),
        )
        development_n = SAMPLE_SIZES["development"][dataset]
        confirmation_n = SAMPLE_SIZES["confirmation"][dataset]
        if len(ordered) < development_n + confirmation_n:
            raise ValueError(f"{dataset}: insufficient eligible source rows")
        output["development"][dataset] = ordered[:development_n]
        output["confirmation"][dataset] = ordered[
            development_n : development_n + confirmation_n
        ]
    return output


def build_twowiki_channels(
    source_row_index: int, sample_id: str, row: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    normalized, diagnostics = normalize_record(row)
    if not fully_mappable(diagnostics):
        raise ValueError(f"{sample_id}: official supporting evidence is not mappable")
    if normalized["id"] != sample_id:
        raise ValueError(f"{sample_id}: normalized identity differs")
    query_id = f"{TWOWIKI_DATASET}::{sample_id}"
    units: list[dict[str, Any]] = []
    support_map: dict[tuple[str, int], str] = {}
    for paragraph_index, context in enumerate(normalized["contexts"]):
        title = require_native_string(context.get("title"), f"{sample_id}.title")
        sentences = context.get("sentences")
        if not isinstance(sentences, list) or not sentences:
            raise ValueError(f"{sample_id}: context sentences differ")
        for sentence_index, sentence in enumerate(sentences):
            text = require_native_string(sentence, f"{sample_id}.sentence")
            unit = _unit(
                TWOWIKI_DATASET,
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
                raise ValueError(f"{sample_id}: ambiguous supporting target {key}")
            support_map[key] = unit["unit_id"]
    supporting_unit_ids = []
    for item in row.get("supporting_facts") or []:
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError(f"{sample_id}: malformed supporting fact")
        title = require_native_string(item[0], f"{sample_id}.support.title")
        sentence_index = require_json_int(item[1], f"{sample_id}.support.index")
        unit_id = support_map.get((title, sentence_index))
        if unit_id is None:
            raise ValueError(f"{sample_id}: supporting target absent")
        supporting_unit_ids.append(unit_id)
    if not supporting_unit_ids or len(supporting_unit_ids) != len(
        set(supporting_unit_ids)
    ):
        raise ValueError(f"{sample_id}: supporting identity differs")
    blind = {
        "candidate_units": units,
        "dataset": TWOWIKI_DATASET,
        "query_id": query_id,
        "question": require_native_string(row.get("question"), f"{sample_id}.question"),
        "sample_id": sample_id,
    }
    gold = {
        "answers": [require_native_string(row.get("answer"), f"{sample_id}.answer")],
        "dataset": TWOWIKI_DATASET,
        "evidence_granularity": "official_supporting_sentence",
        "query_id": query_id,
        "sample_id": sample_id,
        "supporting_unit_ids": supporting_unit_ids,
    }
    metadata = {
        "candidate_unit_count": len(units),
        "dataset": TWOWIKI_DATASET,
        "query_id": query_id,
        "sample_id": sample_id,
        "source_row_index": source_row_index,
        "source_split": "dev",
        "supporting_evidence_count": len(supporting_unit_ids),
        "type": require_native_string(row.get("type"), f"{sample_id}.type"),
    }
    return blind, gold, metadata


def build_boundary(
    selected: dict[str, list[tuple[int, str, dict[str, Any]]]]
) -> dict[str, list[dict[str, Any]]]:
    result = {"blind": [], "gold": [], "metadata": [], "selection": []}
    for dataset in DATASETS:
        for source_row_index, sample_id, row in selected[dataset]:
            if dataset == HOTPOT_DATASET:
                blind, gold, metadata = build_hotpot_channels(
                    source_row_index, sample_id, row
                )
            elif dataset == MUSIQUE_DATASET:
                blind, gold, metadata = build_musique_channels(
                    source_row_index, sample_id, row
                )
            else:
                blind, gold, metadata = build_twowiki_channels(
                    source_row_index, sample_id, row
                )
            assert_no_gold_fields(blind, f"blind[{blind['query_id']}]")
            if not blind["candidate_units"]:
                raise ValueError(f"{blind['query_id']}: empty candidate pool")
            result["blind"].append(blind)
            result["gold"].append(gold)
            result["metadata"].append(metadata)
            result["selection"].append(
                {
                    "dataset": dataset,
                    "query_id": blind["query_id"],
                    "sample_id": sample_id,
                    "selection_key": selection_key(
                        DATASET_KEYS[dataset], sample_id, source_row_index
                    )[0],
                    "source_row_index": source_row_index,
                }
            )
    return result


def run(config: dict[str, Any]) -> None:
    validate_authorization(config)
    repository_root = Path(__file__).resolve().parents[1]
    assert_implementation_binding(config, repository_root)
    sources = config.get("sources")
    if not isinstance(sources, dict):
        raise ValueError("sources binding is missing")
    source_rows: dict[str, list[dict[str, Any]]] = {}
    for key, dataset in (
        ("hotpotqa", HOTPOT_DATASET),
        ("musique", MUSIQUE_DATASET),
        ("twowiki", TWOWIKI_DATASET),
    ):
        binding = sources.get(key)
        if not isinstance(binding, dict):
            raise ValueError(f"sources.{key} binding is missing")
        path = Path(require_native_string(binding.get("path"), f"sources.{key}.path"))
        assert_file_identity(path, binding, f"sources.{key}")
        source_rows[dataset] = _rows(path)
    if len(source_rows[TWOWIKI_DATASET]) != TWOWIKI_EXPECTED_ROWS:
        raise ValueError("2Wiki official dev row count differs")

    history_binding = config.get("historical_inputs")
    if not isinstance(history_binding, list) or not history_binding:
        raise ValueError("historical_inputs binding is missing")
    history, history_audit = historical_ids(history_binding)
    original_history = {dataset: set(values) for dataset, values in history.items()}
    partitions = select_partitions(source_rows, history)
    channels = {
        boundary: build_boundary(partitions[boundary]) for boundary in BOUNDARIES
    }

    all_selected: set[str] = set()
    for boundary in BOUNDARIES:
        expected = sum(SAMPLE_SIZES[boundary].values())
        blind = channels[boundary]["blind"]
        if len(blind) != expected or len({row["query_id"] for row in blind}) != expected:
            raise ValueError(f"{boundary}: query identities differ")
        for row in blind:
            if row["sample_id"] in original_history[row["dataset"]]:
                raise ValueError(f"{boundary}: historical overlap")
            if row["query_id"] in all_selected:
                raise ValueError("development/confirmation overlap")
            all_selected.add(row["query_id"])

    outputs: list[tuple[Path, bytes]] = []
    manifest: dict[str, Any] = {
        "boundaries": {},
        "checks": {
            "development_confirmation_overlap": 0,
            "gold_fields_in_blind": False,
            "historical_overlap": 0,
            "selection_used_gold_or_metadata": False,
            "twowiki_reservation_rows_read_for_content": False,
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
            "SHA256(stage_salt + dataset_key + NUL + native_id + NUL + "
            "source_row_index), native_id"
        ),
        "status": "STAGE6A_INPUT_CHANNELS_BUILT_PENDING_INDEPENDENT_VERIFICATION",
        "twowiki_source_boundary": {
            "fresh_pool_rows": "[9819:12576)",
            "reservation_rows": "[5300:9800)",
            "replacement_rows": "[9800:9819)",
        },
    }
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
                (path_from_config(config, f"{boundary}_blind"), payloads["blind"]),
                (path_from_config(config, f"{boundary}_gold"), payloads["gold"]),
                (
                    path_from_config(config, f"{boundary}_metadata"),
                    payloads["metadata"],
                ),
            )
        )
    source_manifest = {
        "models": config["models"],
        "runtime": config["runtime"],
        "schema_version": SCHEMA_VERSION,
        "sources": {
            key: {
                **file_identity(Path(value["path"])),
                "path": value["path"],
                "revision": value.get("revision"),
                "source_url": value.get("source_url"),
            }
            for key, value in sources.items()
        },
        "status": "STAGE6A_SOURCE_MODEL_ENVIRONMENT_INPUTS_BOUND",
    }
    outputs.extend(
        (
            (path_from_config(config, "input_manifest"), render_json(manifest)),
            (
                path_from_config(config, "source_model_environment_manifest"),
                render_json(source_manifest),
            ),
        )
    )
    write_new_files_atomically(outputs)
    print(
        "STAGE6A_INPUT_CHANNELS_BUILT_PENDING_INDEPENDENT_VERIFICATION "
        "development=1400 confirmation=2800 historical_overlap=0 "
        "development_confirmation_overlap=0"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage6A config must be an object")
    run(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE6A_PREPARE_FAIL: {exc}", file=sys.stderr)
        raise
