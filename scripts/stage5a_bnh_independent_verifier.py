"""Independent Stage5A input, retrieval, prompt, statistic, and artifact verifier."""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from stage4e_e2e_goldfree_runner import build_prompt
from stage4h_cbe_retrieval import build_units_queries
from stage5a_bnh_common import (
    BASELINE_METHOD,
    CONFIRMATION_METHODS,
    DATASETS,
    DATASET_KEYS,
    HOTPOT_DATASET,
    MUSIQUE_DATASET,
    RERUN_QUERIES_PER_DATASET,
    SAMPLE_SIZES,
    SCHEMA_VERSION,
    assert_bound,
    assert_file_identity,
    assert_implementation_binding,
    assert_no_gold_fields,
    deterministic_method_order,
    development_method,
    file_identity,
    id_digest,
    load_json,
    load_jsonl,
    load_parent_config,
    path_from_config,
    render_json,
    render_jsonl,
    rerun_selection_key,
    selection_key,
    validate_authorization,
    validate_candidate_configs,
    write_new_files_atomically,
)
from stage5a_bnh_independent_retrieval import (
    independent_confirmation_rankings,
    independent_development_rankings,
)
from stage5a_bnh_independent_statistics import (
    independent_answer_audit,
    independent_confirmation_audit,
    independent_confirmation_outputs,
    independent_development_outputs,
)


def _object_rows(path: Path) -> list[dict[str, Any]]:
    value = load_jsonl(path) if path.suffix.lower() == ".jsonl" else load_json(path)
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise ValueError(f"{path}: expected object-row list")
    return value


def _history_dataset(row: dict[str, Any], path: Path) -> str | None:
    dataset = row.get("dataset")
    if isinstance(dataset, str):
        lowered = dataset.lower()
        if "hotpot" in lowered:
            return HOTPOT_DATASET
        if "musique" in lowered:
            return MUSIQUE_DATASET
    name = path.name.lower()
    if "hotpot" in name:
        return HOTPOT_DATASET
    if "musique" in name:
        return MUSIQUE_DATASET
    return None


def _native_id(row: dict[str, Any], label: str) -> str:
    for key in ("sample_id", "_id", "id"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value
    raise ValueError(f"{label}: native ID missing")


def _historical_ids(
    bindings: list[dict[str, Any]],
) -> dict[str, set[str]]:
    result = {dataset: set() for dataset in DATASETS}
    seen_paths: set[Path] = set()
    for index, binding in enumerate(bindings):
        if not isinstance(binding, dict):
            raise ValueError(f"history[{index}] binding differs")
        path_value = binding.get("path")
        if not isinstance(path_value, str) or not path_value:
            raise ValueError(f"history[{index}].path differs")
        path = Path(path_value)
        resolved = path.resolve()
        if resolved in seen_paths:
            raise ValueError("historical path duplicates")
        seen_paths.add(resolved)
        assert_file_identity(path, binding, f"history[{index}]")
        for row_index, row in enumerate(_object_rows(path)):
            dataset = _history_dataset(row, path)
            if dataset is not None:
                result[dataset].add(
                    _native_id(row, f"history[{index}][{row_index}]")
                )
    return result


def _source_ids(rows: list[dict[str, Any]], dataset: str) -> list[str]:
    key = "_id" if dataset == HOTPOT_DATASET else "id"
    result: list[str] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        value = row.get(key)
        if not isinstance(value, str) or not value.strip() or value in seen:
            raise ValueError(f"{dataset}[{index}].{key} differs")
        seen.add(value)
        result.append(value)
    return result


def verify_input_selection(config: dict[str, Any]) -> dict[str, Any]:
    parent = load_parent_config(config)
    sources = parent.get("sources")
    parent_history = parent.get("historical_inputs")
    additional = config.get("additional_historical_inputs")
    if (
        not isinstance(sources, dict)
        or not isinstance(parent_history, list)
        or not isinstance(additional, list)
        or len(additional) != 2
    ):
        raise ValueError("Stage5A source/history bindings differ")
    source_ids: dict[str, list[str]] = {}
    for key, dataset in (("hotpotqa", HOTPOT_DATASET), ("musique", MUSIQUE_DATASET)):
        binding = sources.get(key)
        if not isinstance(binding, dict):
            raise ValueError(f"sources.{key} differs")
        path = Path(binding["path"])
        assert_file_identity(path, binding, f"sources.{key}")
        source_ids[dataset] = _source_ids(_object_rows(path), dataset)
    history = _historical_ids(parent_history + additional)
    original = {dataset: set(values) for dataset, values in history.items()}
    boundary_ids: dict[str, dict[str, list[str]]] = {}
    for boundary in ("development", "confirmation"):
        expected: dict[str, list[str]] = {}
        for dataset in DATASETS:
            candidates = [
                native_id
                for native_id in source_ids[dataset]
                if native_id not in history[dataset]
            ]
            ordered = sorted(
                candidates,
                key=lambda native_id: selection_key(
                    boundary, DATASET_KEYS[dataset], native_id
                ),
            )
            expected[dataset] = ordered[:SAMPLE_SIZES[boundary][dataset]]
            if len(expected[dataset]) != SAMPLE_SIZES[boundary][dataset]:
                raise ValueError(f"{boundary}/{dataset}: source rows insufficient")
        blind = load_jsonl(assert_bound(config, f"{boundary}_blind"))
        assert_no_gold_fields(blind, f"{boundary}.blind")
        actual = {
            dataset: [
                row["sample_id"] for row in blind if row.get("dataset") == dataset
            ]
            for dataset in DATASETS
        }
        if actual != expected:
            raise ValueError(f"{boundary}: ID-only selection differs")
        for dataset in DATASETS:
            history[dataset].update(expected[dataset])
        boundary_ids[boundary] = expected
    if any(
        set(boundary_ids["development"][dataset])
        & set(boundary_ids["confirmation"][dataset])
        for dataset in DATASETS
    ):
        raise ValueError("development/confirmation overlap")
    return {
        "boundaries": {
            boundary: {
                dataset: {
                    "count": len(boundary_ids[boundary][dataset]),
                    "native_id_sha256": id_digest(
                        sorted(boundary_ids[boundary][dataset])
                    ),
                }
                for dataset in DATASETS
            }
            for boundary in ("development", "confirmation")
        },
        "development_confirmation_overlap": 0,
        "historical_native_ids": {
            dataset: {
                "count": len(original[dataset]),
                "sha256": id_digest(sorted(original[dataset])),
            }
            for dataset in DATASETS
        },
        "historical_overlap": 0,
        "status": "STAGE5A_INPUT_SELECTION_INDEPENDENTLY_VERIFIED",
    }


def verify_preexisting_frozen(config: dict[str, Any]) -> dict[str, Any]:
    manifest = load_json(assert_bound(config, "preexisting_frozen_manifest"))
    if (
        not isinstance(manifest, dict)
        or manifest.get("status")
        != "STAGE5A_PREEXISTING_ARTIFACT_BASELINE_FROZEN"
    ):
        raise ValueError("pre-existing frozen manifest differs")
    repository_root = Path(__file__).resolve().parents[1]
    rows = manifest.get("files")
    if not isinstance(rows, list) or manifest.get("file_count") != len(rows):
        raise ValueError("pre-existing frozen manifest row count differs")
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {"bytes", "path", "sha256"}:
            raise ValueError(f"pre-existing frozen row[{index}] differs")
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("pre-existing frozen path is unsafe")
        assert_file_identity(
            repository_root / relative,
            row,
            f"pre-existing frozen file[{index}]",
        )
    return {
        "file_count": len(rows),
        "status": "STAGE4E_THROUGH_STAGE5_PMC_FROZEN_ARTIFACTS_UNCHANGED",
    }


def _load_cache(
    config: dict[str, Any],
    boundary: str,
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
) -> tuple[np.ndarray, np.ndarray]:
    path = assert_bound(config, f"{boundary}_bge_embedding_cache")
    with np.load(path, allow_pickle=False) as cache:
        required = {
            "metadata_json",
            "query_embeddings",
            "query_ids",
            "unit_embeddings",
            "unit_ids",
        }
        if set(cache.files) != required:
            raise ValueError(f"{boundary}: cache schema differs")
        metadata = json.loads(str(cache["metadata_json"].item()))
        if (
            metadata.get("model_id") != "BAAI/bge-large-en-v1.5"
            or metadata.get("revision")
            != "d4aa6901d3a41ba39fb536a557fa166f842b0e09"
            or metadata.get("pooling") != "CLS_then_l2"
            or metadata.get("max_length") != 512
            or metadata.get("unit_id_sha256")
            != id_digest(row["unit_id"] for row in units)
            or metadata.get("query_id_sha256")
            != id_digest(row["query_id"] for row in queries)
        ):
            raise ValueError(f"{boundary}: cache metadata differs")
        if cache["unit_ids"].tolist() != [row["unit_id"] for row in units]:
            raise ValueError(f"{boundary}: cache unit order differs")
        if cache["query_ids"].tolist() != [row["query_id"] for row in queries]:
            raise ValueError(f"{boundary}: cache query order differs")
        unit_embeddings = np.asarray(cache["unit_embeddings"], dtype="float32")
        query_embeddings = np.asarray(cache["query_embeddings"], dtype="float32")
    for matrix, count, label in (
        (unit_embeddings, len(units), "unit"),
        (query_embeddings, len(queries), "query"),
    ):
        if (
            matrix.ndim != 2
            or matrix.shape[0] != count
            or not np.isfinite(matrix).all()
        ):
            raise ValueError(f"{boundary}: cache {label} matrix differs")
        norms = np.linalg.norm(matrix, axis=1)
        if np.any(norms <= 0.0) or not np.allclose(
            norms, 1.0, atol=1e-5, rtol=0.0
        ):
            raise ValueError(f"{boundary}: cache {label} matrix is not normalized")
    return unit_embeddings, query_embeddings


def _geometry_summary(
    traces: list[dict[str, Any]], configs: list[dict[str, Any]]
) -> dict[str, Any]:
    summaries: dict[str, Any] = {}
    eligible: list[str] = []
    by_id = {row["config_id"]: row for row in configs}
    for config_id, config_row in by_id.items():
        datasets: dict[str, Any] = {}
        combined: list[dict[str, Any]] = []
        for dataset in DATASETS:
            values = [
                row["configs"][config_id]
                for row in traces
                if row["dataset"] == dataset
            ]
            combined.extend(values)
            counts = [len(value["inserted_unit_ids"]) for value in values]
            datasets[dataset] = {
                "insertable_query_count": sum(count > 0 for count in counts),
                "insertable_query_rate": sum(count > 0 for count in counts) / len(counts),
                "mean_eligible_ball_count": float(
                    np.mean(
                        [value["facet"]["eligible_ball_count"] for value in values]
                    )
                ),
                "mean_insert_count": float(np.mean(counts)),
                "query_count": len(values),
            }
        combined_rate = sum(
            bool(value["inserted_unit_ids"]) for value in combined
        ) / len(combined)
        feasible = (
            all(
                datasets[dataset]["insertable_query_rate"] >= 0.10
                for dataset in DATASETS
            )
            and combined_rate >= 0.15
        )
        if feasible:
            eligible.append(config_id)
        summaries[config_id] = {
            "combined_insertable_query_rate": combined_rate,
            "config": config_row,
            "datasets": datasets,
            "feasible": feasible,
        }
    pass_gate = (
        len(eligible) >= 4
        and {by_id[config_id]["leaf_size"] for config_id in eligible} == {4, 6}
    )
    return {
        "candidate_config_count": len(configs),
        "config_summaries": summaries,
        "eligible_config_count": len(eligible),
        "eligible_config_ids": eligible,
        "gate": {
            "minimum_eligible_configs": 4,
            "minimum_insertable_query_rate_combined": 0.15,
            "minimum_insertable_query_rate_each_dataset": 0.10,
            "requires_both_leaf_sizes": True,
            "pass": pass_gate,
            "status": (
                "STAGE5A_BGE_NATIVE_GEOMETRY_FEASIBILITY_PASS"
                if pass_gate
                else "STAGE5A_BGE_NATIVE_GEOMETRY_DEGENERATE"
            ),
        },
        "interpretation": "BLIND_ONLY_FEASIBILITY_NOT_ANSWER_QUALITY_OR_POWER_GUARANTEE",
        "schema_version": SCHEMA_VERSION,
    }


def _selected_config(config: dict[str, Any]) -> dict[str, Any]:
    manifest = load_json(assert_bound(config, "development_selected_config"))
    if (
        not isinstance(manifest, dict)
        or manifest.get("status")
        != "STAGE5A_DEVELOPMENT_UNIQUE_CONFIGURATION_FROZEN"
        or not isinstance(manifest.get("selected_config"), dict)
    ):
        raise ValueError("selected configuration manifest differs")
    selected = manifest["selected_config"]
    family = {
        row["config_id"]: row for row in validate_candidate_configs(config)
    }
    if family.get(selected.get("config_id")) != selected:
        raise ValueError("selected configuration is outside frozen family")
    return selected


def verify_rankings(
    config: dict[str, Any], boundary: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    blind = load_jsonl(assert_bound(config, f"{boundary}_blind"))
    units, queries = build_units_queries(blind)
    unit_embeddings, query_embeddings = _load_cache(
        config, boundary, units, queries
    )
    if boundary == "development":
        rankings, traces = independent_development_rankings(
            units, queries, unit_embeddings, query_embeddings, config
        )
    else:
        rankings, traces = independent_confirmation_rankings(
            units,
            queries,
            unit_embeddings,
            query_embeddings,
            _selected_config(config),
        )
    if assert_bound(config, f"{boundary}_rankings").read_bytes() != render_jsonl(
        rankings
    ):
        raise ValueError(f"{boundary}: rankings differ from independent rebuild")
    if assert_bound(
        config, f"{boundary}_candidate_trace"
    ).read_bytes() != render_jsonl(traces):
        raise ValueError(f"{boundary}: trace differs from independent rebuild")
    if boundary == "development":
        actual = load_json(assert_bound(config, "geometry_feasibility_audit"))
        expected = _geometry_summary(traces, validate_candidate_configs(config))
        if not isinstance(actual, dict):
            raise ValueError("geometry feasibility audit differs")
        for key, value in expected.items():
            if actual.get(key) != value:
                raise ValueError(
                    f"geometry feasibility audit independent field differs: {key}"
                )
    return units, queries, rankings


def _pair_map(
    rows: list[dict[str, Any]], label: str
) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(rows):
        query_id = row.get("query_id")
        method = row.get("method")
        if (
            not isinstance(query_id, str)
            or not query_id
            or not isinstance(method, str)
            or not method
            or (query_id, method) in result
        ):
            raise ValueError(f"{label}[{index}] pair differs")
        result[(query_id, method)] = row
    return result


def _subset_queries(
    queries: list[dict[str, Any]], boundary: str
) -> list[dict[str, Any]]:
    by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for query in queries:
        by_dataset[query["dataset"]].append(query)
    selected: set[str] = set()
    for dataset in DATASETS:
        rows = sorted(
            by_dataset[dataset],
            key=lambda row: rerun_selection_key(
                boundary, dataset, row["query_id"]
            ),
        )[:RERUN_QUERIES_PER_DATASET[boundary]]
        selected.update(row["query_id"] for row in rows)
    return [row for row in queries if row["query_id"] in selected]


def verify_predictions_and_prompts(
    config: dict[str, Any],
    boundary: str,
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    rankings: list[dict[str, Any]],
) -> dict[str, Any]:
    from transformers import AutoTokenizer

    parent = load_parent_config(config)
    generator_snapshot = Path(parent["paths"]["generator_snapshot"])
    if boundary == "development":
        methods = (BASELINE_METHOD,) + tuple(
            development_method(row["config_id"])
            for row in validate_candidate_configs(config)
        )
    else:
        methods = CONFIRMATION_METHODS
    rankings_by_query = {row["query_id"]: row for row in rankings}
    units_by_id = {row["unit_id"]: row for row in units}
    main_predictions = load_jsonl(
        assert_bound(config, f"{boundary}_predictions_main")
    )
    main_prompts = load_jsonl(
        assert_bound(config, f"{boundary}_prompt_audit_main")
    )
    rerun_predictions = load_jsonl(
        assert_bound(config, f"{boundary}_predictions_rerun_subset")
    )
    rerun_prompts = load_jsonl(
        assert_bound(config, f"{boundary}_prompt_audit_rerun_subset")
    )
    main_prediction_map = _pair_map(main_predictions, "main_predictions")
    main_prompt_map = _pair_map(main_prompts, "main_prompts")
    rerun_prediction_map = _pair_map(rerun_predictions, "rerun_predictions")
    rerun_prompt_map = _pair_map(rerun_prompts, "rerun_prompts")
    expected_main_order = [
        (query["query_id"], method)
        for query in queries
        for method in deterministic_method_order(
            query["query_id"],
            methods,
            f"stage5a_bnh_{boundary}_main_v1",
        )
    ]
    subset = _subset_queries(queries, boundary)
    expected_rerun_order = [
        (query["query_id"], method)
        for query in subset
        for method in deterministic_method_order(
            query["query_id"],
            methods,
            f"stage5a_bnh_{boundary}_rerun_subset_v1",
        )
    ]
    if [(row["query_id"], row["method"]) for row in main_predictions] != expected_main_order:
        raise ValueError(f"{boundary}: main prediction plan order differs")
    if [(row["query_id"], row["method"]) for row in main_prompts] != expected_main_order:
        raise ValueError(f"{boundary}: main prompt plan order differs")
    if [(row["query_id"], row["method"]) for row in rerun_predictions] != expected_rerun_order:
        raise ValueError(f"{boundary}: rerun prediction plan order differs")
    if [(row["query_id"], row["method"]) for row in rerun_prompts] != expected_rerun_order:
        raise ValueError(f"{boundary}: rerun prompt plan order differs")
    if set(rerun_prediction_map) != set(expected_rerun_order):
        raise ValueError(f"{boundary}: rerun coverage differs")
    for key in expected_rerun_order:
        if rerun_prediction_map[key] != main_prediction_map[key]:
            raise ValueError(f"{boundary}/{key}: deterministic prediction differs")
        if rerun_prompt_map[key] != main_prompt_map[key]:
            raise ValueError(f"{boundary}/{key}: deterministic prompt differs")
    tokenizer = AutoTokenizer.from_pretrained(
        generator_snapshot, local_files_only=True
    )
    for query in queries:
        ranking_row = rankings_by_query[query["query_id"]]
        for method in methods:
            key = (query["query_id"], method)
            prediction = main_prediction_map[key]
            audit = main_prompt_map[key]
            if set(prediction) != {
                "dataset",
                "method",
                "prediction",
                "query_id",
                "sample_id",
            }:
                raise ValueError(f"{boundary}/{key}: prediction schema differs")
            if set(audit) != {
                "dataset",
                "evidence_unit_ids",
                "input_token_count",
                "method",
                "prompt_sha256",
                "query_id",
                "rank1_truncated",
                "sample_id",
            }:
                raise ValueError(f"{boundary}/{key}: prompt schema differs")
            rebuilt = build_prompt(
                tokenizer,
                query["question"],
                [
                    units_by_id[unit_id]
                    for unit_id in ranking_row["methods"][method]
                ],
                4096,
            )
            expected_audit = {
                "dataset": query["dataset"],
                "evidence_unit_ids": rebuilt["evidence_unit_ids"],
                "input_token_count": rebuilt["input_token_count"],
                "method": method,
                "prompt_sha256": rebuilt["prompt_sha256"],
                "query_id": query["query_id"],
                "rank1_truncated": rebuilt["rank1_truncated"],
                "sample_id": query["sample_id"],
            }
            if audit != expected_audit:
                raise ValueError(f"{boundary}/{key}: prompt rebuild differs")
    return {
        "full_main_calls": len(main_predictions),
        "main_subset_prediction_identity": True,
        "prompt_reconstruction": "PASS",
        "rerun_calls": len(rerun_predictions),
        "subset_query_count": len(subset),
    }


def verify_pregold(config: dict[str, Any], boundary: str) -> dict[str, Any]:
    if boundary == "confirmation":
        development_verification = load_json(
            assert_bound(config, "development_final_verification")
        )
        if (
            not isinstance(development_verification, dict)
            or development_verification.get("status")
            != "STAGE5A_DEVELOPMENT_SELECTION_INDEPENDENT_VERIFICATION_PASS"
        ):
            raise PermissionError(
                "confirmation boundary requires verified development selection"
            )
    input_audit = verify_input_selection(config)
    frozen_audit = verify_preexisting_frozen(config)
    units, queries, rankings = verify_rankings(config, boundary)
    prompt_audit = verify_predictions_and_prompts(
        config, boundary, units, queries, rankings
    )
    return {
        "boundary": boundary,
        "embedding_cache": file_identity(
            assert_bound(config, f"{boundary}_bge_embedding_cache")
        ),
        "frozen_preexisting": frozen_audit,
        "input_selection": input_audit,
        "prompt_and_determinism": prompt_audit,
        "rankings": file_identity(
            assert_bound(config, f"{boundary}_rankings")
        ),
        "schema_version": SCHEMA_VERSION,
        "status": (
            "STAGE5A_DEVELOPMENT_PRE_GOLD_VERIFICATION_PASS"
            if boundary == "development"
            else "STAGE5A_CONFIRMATION_PRE_GOLD_VERIFICATION_PASS"
        ),
    }


def verify_development_final(config: dict[str, Any]) -> dict[str, Any]:
    marker = load_json(assert_bound(config, "development_verified_pregold"))
    if marker.get("status") != "STAGE5A_DEVELOPMENT_PRE_GOLD_VERIFICATION_PASS":
        raise PermissionError("development pre-Gold marker differs")
    configs = validate_candidate_configs(config)
    methods = (BASELINE_METHOD,) + tuple(
        development_method(row["config_id"]) for row in configs
    )
    rankings = load_jsonl(assert_bound(config, "development_rankings"))
    audits = independent_answer_audit(
        load_jsonl(assert_bound(config, "development_gold")),
        load_jsonl(assert_bound(config, "development_predictions_main")),
        load_jsonl(assert_bound(config, "development_prompt_audit_main")),
        rankings,
        methods,
    )
    geometry = load_json(assert_bound(config, "geometry_feasibility_audit"))
    summary, selected = independent_development_outputs(
        audits, configs, geometry
    )
    if load_jsonl(assert_bound(config, "development_query_audit")) != audits:
        raise ValueError("development query audit differs independently")
    if load_json(assert_bound(config, "development_summary")) != summary:
        raise ValueError("development summary differs independently")
    if load_json(assert_bound(config, "development_selected_config")) != selected:
        raise ValueError("development selected config differs independently")
    return {
        "query_count": len(audits),
        "selected_config_id": selected["selected_config"]["config_id"],
        "status": "STAGE5A_DEVELOPMENT_SELECTION_INDEPENDENT_VERIFICATION_PASS",
    }


def verify_confirmation_final(config: dict[str, Any]) -> dict[str, Any]:
    marker = load_json(assert_bound(config, "confirmation_verified_pregold"))
    if marker.get("status") != "STAGE5A_CONFIRMATION_PRE_GOLD_VERIFICATION_PASS":
        raise PermissionError("confirmation pre-Gold marker differs")
    rankings = load_jsonl(assert_bound(config, "confirmation_rankings"))
    audits = independent_confirmation_audit(
        load_jsonl(assert_bound(config, "confirmation_gold")),
        load_jsonl(assert_bound(config, "confirmation_predictions_main")),
        load_jsonl(assert_bound(config, "confirmation_prompt_audit_main")),
        rankings,
    )
    telemetry = load_json(assert_bound(config, "confirmation_telemetry_main"))
    dataset, equal_weight, decision, efficiency, mechanism = (
        independent_confirmation_outputs(audits, telemetry)
    )
    comparisons = (
        ("confirmation_query_audit", audits),
        ("confirmation_dataset_summaries", dataset),
        ("confirmation_equal_weight_summary", equal_weight),
        ("scientific_decision", decision),
        ("confirmation_efficiency_summary", efficiency),
        ("confirmation_mechanism_audit", mechanism),
    )
    for key, expected in comparisons:
        actual = (
            load_jsonl(assert_bound(config, key))
            if key == "confirmation_query_audit"
            else load_json(assert_bound(config, key))
        )
        if actual != expected:
            raise ValueError(f"{key} differs from independent reconstruction")
    frozen = verify_preexisting_frozen(config)
    return {
        "core_state": decision["core_state"],
        "facet_state": decision["facet_state"],
        "frozen_preexisting": frozen,
        "placement_state": decision["placement_state"],
        "query_count": len(audits),
        "status": "STAGE5A_FINAL_INDEPENDENT_VERIFICATION_PASS",
    }


def run(config: dict[str, Any], mode: str) -> None:
    validate_authorization(config)
    assert_implementation_binding(config, Path(__file__).resolve().parents[1])
    if mode == "development_pregold":
        result = verify_pregold(config, "development")
        path = path_from_config(config, "development_verified_pregold")
    elif mode == "development_final":
        result = verify_development_final(config)
        path = path_from_config(config, "development_final_verification")
    elif mode == "confirmation_pregold":
        result = verify_pregold(config, "confirmation")
        path = path_from_config(config, "confirmation_verified_pregold")
    elif mode == "confirmation_final":
        result = verify_confirmation_final(config)
        path = path_from_config(config, "final_verification")
    else:
        raise ValueError(f"unknown verifier mode: {mode}")
    write_new_files_atomically(((path, render_json(result)),))
    print(result["status"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument(
        "--mode",
        required=True,
        choices=(
            "development_pregold",
            "development_final",
            "confirmation_pregold",
            "confirmation_final",
        ),
    )
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage5A config must be an object")
    run(config, args.mode)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE5A_INDEPENDENT_VERIFIER_FAIL: {exc}", file=sys.stderr)
        raise
