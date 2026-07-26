"""Independent input, pre-Gold, and final verifier for Stage6A."""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from stage5a_bnh_common import deterministic_method_order
from stage6a_smc_common import (
    BASELINE_METHOD,
    BOUNDARIES,
    DATASETS,
    SAMPLE_SIZES,
    TWOWIKI_DATASET,
    assert_bound,
    assert_file_identity,
    assert_implementation_binding,
    assert_no_gold_fields,
    development_methods,
    file_identity,
    load_json,
    load_jsonl,
    path_from_config,
    render_json,
    render_jsonl,
    require_native_string,
    validate_authorization,
    validate_confirmation_methods,
    write_new_files_atomically,
)
from stage6a_smc_independent_retrieval import independent_query_rankings
from stage6a_smc_models import (
    embedding_cache_metadata,
    load_embedding_cache,
    set_frozen_runtime,
    validate_models,
)
from stage6a_smc_retrieval import build_units_queries, dense_common_pool


FORBIDDEN_BLIND_KEYS = {
    "answer",
    "answers",
    "gold",
    "gold_evidence",
    "supporting_facts",
    "supporting_paragraph_indices",
    "supporting_unit_ids",
    "type",
    "hop_count",
}


def _strict_blind_rows(
    rows: list[dict[str, Any]], boundary: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    expected = sum(SAMPLE_SIZES[boundary].values())
    if len(rows) != expected:
        raise ValueError(f"{boundary}: blind row count differs")
    counts = defaultdict(int)
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {
            "candidate_units",
            "dataset",
            "query_id",
            "question",
            "sample_id",
        }:
            raise ValueError(f"{boundary}.blind[{index}] schema differs")
        assert_no_gold_fields(row, f"{boundary}.blind[{index}]")
        if FORBIDDEN_BLIND_KEYS & set(row):
            raise ValueError(f"{boundary}.blind[{index}] leaks Gold/metadata")
        for key in ("dataset", "query_id", "question", "sample_id"):
            require_native_string(row[key], f"{boundary}.blind[{index}].{key}")
        if row["query_id"] in seen:
            raise ValueError(f"{boundary}: duplicate query identity")
        seen.add(row["query_id"])
        counts[row["dataset"]] += 1
        candidates = row["candidate_units"]
        if not isinstance(candidates, list) or not candidates:
            raise ValueError(f"{boundary}.blind[{index}] candidates differ")
        unit_ids: set[str] = set()
        for unit_index, unit in enumerate(candidates):
            if not isinstance(unit, dict):
                raise ValueError("candidate unit must be an object")
            for key in (
                "dataset",
                "document_id",
                "query_id",
                "sample_id",
                "text",
                "title",
                "unit_id",
            ):
                require_native_string(
                    unit.get(key),
                    f"{boundary}.blind[{index}].candidate[{unit_index}].{key}",
                )
            if (
                unit["dataset"] != row["dataset"]
                or unit["query_id"] != row["query_id"]
                or unit["sample_id"] != row["sample_id"]
            ):
                raise ValueError("candidate row identity differs")
            if unit["unit_id"] in unit_ids:
                raise ValueError("candidate unit identity duplicates")
            unit_ids.add(unit["unit_id"])
    if dict(counts) != SAMPLE_SIZES[boundary]:
        raise ValueError(f"{boundary}: dataset sample sizes differ")
    units, queries = build_units_queries(rows)
    return units, queries


def verify_inputs(config: dict[str, Any]) -> dict[str, Any]:
    manifest = load_json(path_from_config(config, "input_manifest"))
    source_manifest = load_json(
        path_from_config(config, "source_model_environment_manifest")
    )
    if not isinstance(manifest, dict) or manifest.get("status") != (
        "STAGE6A_INPUT_CHANNELS_BUILT_PENDING_INDEPENDENT_VERIFICATION"
    ):
        raise ValueError("Stage6A input manifest differs")
    if not isinstance(source_manifest, dict) or source_manifest.get("status") != (
        "STAGE6A_SOURCE_MODEL_ENVIRONMENT_INPUTS_BOUND"
    ):
        raise ValueError("Stage6A source/model/environment manifest differs")
    all_ids: dict[str, set[str]] = {}
    boundaries = {}
    for boundary in BOUNDARIES:
        blind_path = assert_bound(config, f"{boundary}_blind")
        gold_path = assert_bound(config, f"{boundary}_gold")
        metadata_path = assert_bound(config, f"{boundary}_metadata")
        blind = load_jsonl(blind_path)
        units, queries = _strict_blind_rows(blind, boundary)
        gold = load_jsonl(gold_path)
        metadata = load_jsonl(metadata_path)
        if len(gold) != len(queries) or len(metadata) != len(queries):
            raise ValueError(f"{boundary}: channel row counts differ")
        for index, (query, gold_row, metadata_row) in enumerate(
            zip(queries, gold, metadata, strict=True)
        ):
            for row, label in ((gold_row, "gold"), (metadata_row, "metadata")):
                if (
                    not isinstance(row, dict)
                    or row.get("query_id") != query["query_id"]
                    or row.get("dataset") != query["dataset"]
                    or row.get("sample_id") != query["sample_id"]
                ):
                    raise ValueError(f"{boundary}.{label}[{index}] identity differs")
            if query["dataset"] == TWOWIKI_DATASET:
                source_row_index = metadata_row.get("source_row_index")
                if (
                    isinstance(source_row_index, bool)
                    or not isinstance(source_row_index, int)
                    or not 9819 <= source_row_index < 12576
                ):
                    raise ValueError("2Wiki fresh-pool source row differs")
        all_ids[boundary] = {row["query_id"] for row in queries}
        boundaries[boundary] = {
            "candidate_units": len(units),
            "queries": len(queries),
        }
    if all_ids["development"] & all_ids["confirmation"]:
        raise ValueError("development/confirmation identity overlap")
    checks = manifest.get("checks")
    if not isinstance(checks, dict) or checks != {
        "development_confirmation_overlap": 0,
        "gold_fields_in_blind": False,
        "historical_overlap": 0,
        "selection_used_gold_or_metadata": False,
        "twowiki_reservation_rows_read_for_content": False,
    }:
        raise ValueError("input manifest checks differ")
    return {
        "boundaries": boundaries,
        "development_confirmation_overlap": 0,
        "status": "STAGE6A_INPUT_CHANNELS_VERIFIED",
    }


def _methods(config: dict[str, Any], boundary: str) -> tuple[str, ...]:
    if boundary == "development":
        return development_methods()
    lock = load_json(path_from_config(config, "development_selection_lock"))
    if not isinstance(lock, dict):
        raise ValueError("development selection lock differs")
    return validate_confirmation_methods(lock.get("confirmation_methods"))


def _row_map(rows: list[dict[str, Any]], label: str) -> dict[str, dict[str, Any]]:
    output = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"{label}[{index}] must be an object")
        query_id = require_native_string(row.get("query_id"), f"{label}.query_id")
        if query_id in output:
            raise ValueError(f"{label}: duplicate query identity")
        output[query_id] = row
    return output


def _pair_map(
    rows: list[dict[str, Any]], label: str
) -> dict[tuple[str, str], dict[str, Any]]:
    output = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"{label}[{index}] must be an object")
        key = (
            require_native_string(row.get("query_id"), f"{label}.query_id"),
            require_native_string(row.get("method"), f"{label}.method"),
        )
        if key in output:
            raise ValueError(f"{label}: duplicate query/method")
        output[key] = row
    return output


def verify_pregold(config: dict[str, Any], boundary: str) -> dict[str, Any]:
    input_verification = load_json(path_from_config(config, "input_verification"))
    if not isinstance(input_verification, dict) or input_verification.get(
        "status"
    ) != "STAGE6A_INPUT_CHANNELS_VERIFIED":
        raise ValueError("input verification is absent")
    set_frozen_runtime(config["runtime"])
    embedding_binding, _, _, _ = validate_models(config)
    blind = load_jsonl(assert_bound(config, f"{boundary}_blind"))
    units, queries = _strict_blind_rows(blind, boundary)
    cache_path = path_from_config(config, f"{boundary}_embedding_cache")
    metadata = embedding_cache_metadata(units, queries, embedding_binding)
    unit_embeddings, query_embeddings = load_embedding_cache(
        cache_path, units, queries, metadata
    )
    reranker_rows = load_jsonl(
        path_from_config(config, f"{boundary}_reranker_trace")
    )
    reranker_map = _row_map(reranker_rows, "reranker")
    rankings = load_jsonl(
        path_from_config(config, f"{boundary}_main_rankings")
    )
    ranking_map = _row_map(rankings, "rankings")
    traces = load_jsonl(
        path_from_config(config, f"{boundary}_main_candidate_trace")
    )
    trace_map = _row_map(traces, "trace")
    methods = _methods(config, boundary)
    by_query: dict[str, list[int]] = defaultdict(list)
    unit_lookup: dict[str, int] = {}
    for index, unit in enumerate(units):
        by_query[unit["query_id"]].append(index)
        unit_lookup[unit["unit_id"]] = index
    for query_index, query in enumerate(queries):
        query_id = query["query_id"]
        reranker = reranker_map.get(query_id)
        ranking = ranking_map.get(query_id)
        trace = trace_map.get(query_id)
        if not all(isinstance(value, dict) for value in (reranker, ranking, trace)):
            raise ValueError(f"{query_id}: formal row missing")
        if (
            reranker["dataset"] != query["dataset"]
            or reranker["sample_id"] != query["sample_id"]
            or ranking["dataset"] != query["dataset"]
            or ranking["sample_id"] != query["sample_id"]
        ):
            raise ValueError(f"{query_id}: formal row identity differs")
        expected_pool, _ = dense_common_pool(
            by_query[query_id],
            units,
            unit_embeddings,
            query_embeddings[query_index],
        )
        observed_ids = reranker.get("common_pool_unit_ids")
        if observed_ids != [units[index]["unit_id"] for index in expected_pool]:
            raise ValueError(f"{query_id}: common pool reconstruction differs")
        scores = reranker.get("reranker_scores")
        if (
            not isinstance(scores, list)
            or len(scores) != len(expected_pool)
            or any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
                for value in scores
            )
        ):
            raise ValueError(f"{query_id}: reranker scores differ")
        independently_rebuilt = independent_query_rankings(
            query,
            expected_pool,
            [float(value) for value in scores],
            units,
            unit_embeddings,
            methods,
        )
        if ranking.get("methods") != independently_rebuilt:
            raise ValueError(f"{query_id}: independent ranking reconstruction differs")
        if trace.get("dense_top20_unit_ids") != independently_rebuilt[
            BASELINE_METHOD
        ]:
            raise ValueError(f"{query_id}: candidate trace baseline differs")

    predictions = load_jsonl(
        path_from_config(config, f"{boundary}_main_predictions")
    )
    prompts = load_jsonl(
        path_from_config(config, f"{boundary}_main_prompt_audit")
    )
    prediction_pairs = _pair_map(predictions, "predictions")
    prompt_pairs = _pair_map(prompts, "prompts")
    expected_pairs = {
        (query["query_id"], method) for query in queries for method in methods
    }
    if set(prediction_pairs) != expected_pairs or set(prompt_pairs) != expected_pairs:
        raise ValueError("main prediction/prompt coverage differs")
    for query in queries:
        for method in methods:
            prompt = prompt_pairs[(query["query_id"], method)]
            if prompt.get("evidence_unit_ids") != ranking_map[
                query["query_id"]
            ]["methods"][method][: len(prompt.get("evidence_unit_ids", []))]:
                raise ValueError("prompt is not an exact ranking prefix")

    rerun_rankings = load_jsonl(
        path_from_config(config, f"{boundary}_rerun_rankings")
    )
    rerun_predictions = load_jsonl(
        path_from_config(config, f"{boundary}_rerun_predictions")
    )
    rerun_prompts = load_jsonl(
        path_from_config(config, f"{boundary}_rerun_prompt_audit")
    )
    rerun_traces = load_jsonl(
        path_from_config(config, f"{boundary}_rerun_candidate_trace")
    )
    rerun_ids = [row["query_id"] for row in rerun_rankings]
    generation_namespace = f"stage6a::{boundary}"
    if (
        render_jsonl([ranking_map[value] for value in rerun_ids])
        != render_jsonl(rerun_rankings)
        or render_jsonl(
            [
                prediction_pairs[(value, method)]
                for value in rerun_ids
                for method in deterministic_method_order(
                    value, methods, generation_namespace
                )
            ]
        )
        != render_jsonl(rerun_predictions)
        or render_jsonl(
            [
                prompt_pairs[(value, method)]
                for value in rerun_ids
                for method in deterministic_method_order(
                    value, methods, generation_namespace
                )
            ]
        )
        != render_jsonl(rerun_prompts)
        or render_jsonl([trace_map[value] for value in rerun_ids])
        != render_jsonl(rerun_traces)
    ):
        raise ValueError("main/rerun deterministic subset differs")
    expected_rerun = {
        "development": 40,
        "confirmation": 80,
    }[boundary] * len(DATASETS)
    if len(rerun_ids) != expected_rerun:
        raise ValueError("rerun query count differs")
    return {
        "boundary": boundary,
        "embedding_cache": file_identity(cache_path),
        "independent_ranking_reconstruction": "PASS",
        "main_rerun_byte_identity": "PASS",
        "methods": list(methods),
        "queries": len(queries),
        "rerun_queries": len(rerun_ids),
        "status": f"STAGE6A_{boundary.upper()}_PRE_GOLD_VERIFICATION_PASS",
    }


def verify_final(config: dict[str, Any]) -> dict[str, Any]:
    pregold = load_json(path_from_config(config, "confirmation_pregold_verification"))
    if not isinstance(pregold, dict) or pregold.get("status") != (
        "STAGE6A_CONFIRMATION_PRE_GOLD_VERIFICATION_PASS"
    ):
        raise ValueError("confirmation pre-Gold verification is absent")
    summary = load_json(path_from_config(config, "confirmation_evaluation_summary"))
    decision = load_json(path_from_config(config, "scientific_decision"))
    scores = load_jsonl(path_from_config(config, "confirmation_query_scores"))
    if not isinstance(summary, dict) or summary.get("status") != (
        "STAGE6A_CONFIRMATION_GOLD_EVALUATION_COMPLETE"
    ):
        raise ValueError("confirmation evaluation summary differs")
    if not isinstance(decision, dict) or decision.get("status") != (
        "STAGE6A_SCIENTIFIC_DECISION_FROZEN"
    ):
        raise ValueError("scientific decision differs")
    if summary.get("decision") != decision.get("decision"):
        raise ValueError("summary/decision status differs")
    methods = validate_confirmation_methods(summary.get("confirmation_methods"))
    if len(scores) != sum(SAMPLE_SIZES["confirmation"].values()):
        raise ValueError("confirmation query score count differs")
    for index, row in enumerate(scores):
        if not isinstance(row, dict) or set(row.get("methods", {})) != set(methods):
            raise ValueError(f"query_scores[{index}] method coverage differs")
    artifacts = {}
    for key in config.get("final_artifact_keys", []):
        path = path_from_config(config, key)
        artifacts[key] = {"path": str(path), **file_identity(path)}
    return {
        "artifacts": artifacts,
        "decision": decision["decision"],
        "gold_isolation": "PASS",
        "query_scores": len(scores),
        "status": "STAGE6A_FINAL_VERIFICATION_PASS",
    }


def run(config: dict[str, Any], mode: str, boundary: str | None) -> None:
    validate_authorization(config)
    assert_implementation_binding(config, Path(__file__).resolve().parents[1])
    if mode == "inputs":
        result = verify_inputs(config)
        output = path_from_config(config, "input_verification")
    elif mode == "pregold":
        if boundary not in BOUNDARIES:
            raise ValueError("pregold mode requires boundary")
        result = verify_pregold(config, boundary)
        output = path_from_config(config, f"{boundary}_pregold_verification")
    elif mode == "final":
        result = verify_final(config)
        output = path_from_config(config, "final_verification")
    else:
        raise ValueError("unknown verifier mode")
    write_new_files_atomically([(output, render_json(result))])
    print(result["status"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("inputs", "pregold", "final"))
    parser.add_argument("--boundary", choices=BOUNDARIES)
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage6A config must be an object")
    run(config, args.mode, args.boundary)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE6A_INDEPENDENT_VERIFIER_FAIL: {exc}", file=sys.stderr)
        raise
