"""Independent pre-Gold and final verifier for Stage4I-SDC.

This module deliberately does not import Stage4I retrieval, runner, or evaluator
code.  It reconstructs the frozen experiment from lower-level Stage4F/Stage4H
primitives and independently recomputes every Gold-side statistic.
"""

from __future__ import annotations

import argparse
import json
import re
import string
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from stage4e_e2e_goldfree_runner import build_prompt
from stage4f_xdr_retrieval import RetrievalConfig, expansion_candidates_goldfree
from stage4h_cbe_retrieval import (
    build_units_queries,
    centroid_only_expansion,
    rank_from_scores,
)
from stage4i_sdc_common import (
    BOOTSTRAP_ITERATIONS,
    BOOTSTRAP_SEED,
    CORE_LEFT,
    CORE_RIGHT,
    DATASETS,
    DATASET_KEYS,
    HOTPOT_DATASET,
    METHODS,
    MUSIQUE_DATASET,
    RERUN_QUERIES_PER_DATASET,
    SAMPLE_SIZES,
    SCHEMA_VERSION,
    assert_bound,
    assert_file_identity,
    assert_implementation_binding,
    assert_no_gold_fields,
    assert_parent_stage4h_artifacts,
    file_identity,
    id_digest,
    load_json,
    load_jsonl,
    path_from_config,
    render_json,
    render_jsonl,
    require_json_int,
    require_native_string,
    rerun_selection_key,
    selection_key,
    sha256_bytes,
    validate_authorization,
    validate_inherited_models,
    write_new_files_atomically,
)


COMPARISONS = {
    "protected_minus_bge": (CORE_LEFT, CORE_RIGHT),
    "protected_minus_unprotected": (
        CORE_LEFT,
        "BGE_HGRAG_UNPROTECTED_TOP20",
    ),
    "unprotected_minus_bge": ("BGE_HGRAG_UNPROTECTED_TOP20", CORE_RIGHT),
    "protected_minus_no_facet": (
        CORE_LEFT,
        "BGE_HGRAG_NO_FACET_TOP20",
    ),
}


def _rows(path: Path) -> list[dict[str, Any]]:
    rows = load_jsonl(path) if path.suffix.lower() == ".jsonl" else load_json(path)
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"{path}: row source differs")
    return rows


def _source_native_ids(path: Path, key: str) -> list[str]:
    values = [
        require_native_string(row.get(key), f"{path}[{index}].{key}")
        for index, row in enumerate(_rows(path))
    ]
    if len(values) != len(set(values)):
        raise ValueError(f"{path}: duplicate source IDs")
    return values


def _historical_ids(
    bindings: list[dict[str, Any]],
) -> tuple[dict[str, set[str]], list[dict[str, Any]]]:
    result = {dataset: set() for dataset in DATASETS}
    audit: list[dict[str, Any]] = []
    for index, binding in enumerate(bindings):
        if not isinstance(binding, dict):
            raise ValueError(f"historical[{index}] binding differs")
        path = Path(
            require_native_string(binding.get("path"), f"historical[{index}].path")
        )
        assert_file_identity(path, binding, f"historical[{index}]")
        rows = _rows(path)
        counts = {dataset: 0 for dataset in DATASETS}
        for row_index, row in enumerate(rows):
            raw_dataset = row.get("dataset")
            hint = (
                raw_dataset.lower()
                if isinstance(raw_dataset, str)
                else path.name.lower()
            )
            dataset = (
                HOTPOT_DATASET
                if "hotpot" in hint
                else MUSIQUE_DATASET
                if "musique" in hint
                else None
            )
            if dataset is None:
                continue
            native_id = next(
                (
                    row[key]
                    for key in ("sample_id", "_id", "id")
                    if isinstance(row.get(key), str) and row[key].strip()
                ),
                None,
            )
            value = require_native_string(
                native_id, f"{path}[{row_index}].native_id"
            )
            result[dataset].add(value)
            counts[dataset] += 1
        audit.append(
            {
                "bytes": binding["bytes"],
                "path": str(path),
                "rows": len(rows),
                "sha256": binding["sha256"],
                "usable_rows": counts,
            }
        )
    return result, audit


def verify_input_selection(
    config: dict[str, Any],
    parent: dict[str, Any],
    blind_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    parent_history = parent.get("historical_inputs")
    additional = config.get("additional_historical_inputs")
    if not isinstance(parent_history, list) or not isinstance(additional, list):
        raise ValueError("historical input bindings differ")
    history, _ = _historical_ids(parent_history + additional)
    actual = {dataset: [] for dataset in DATASETS}
    for index, row in enumerate(blind_rows):
        dataset = require_native_string(row.get("dataset"), f"blind[{index}].dataset")
        if dataset not in DATASETS:
            raise ValueError(f"blind[{index}].dataset differs")
        actual[dataset].append(
            require_native_string(row.get("sample_id"), f"blind[{index}].sample_id")
        )
    source_specs = (
        ("hotpotqa", HOTPOT_DATASET, "_id"),
        ("musique", MUSIQUE_DATASET, "id"),
    )
    checks: dict[str, Any] = {}
    sources = parent.get("sources")
    if not isinstance(sources, dict):
        raise ValueError("parent source bindings differ")
    for key, dataset, id_key in source_specs:
        binding = sources.get(key)
        if not isinstance(binding, dict):
            raise ValueError(f"parent sources.{key} differs")
        path = Path(
            require_native_string(binding.get("path"), f"parent sources.{key}.path")
        )
        assert_file_identity(path, binding, f"parent sources.{key}")
        eligible = [
            value
            for value in _source_native_ids(path, id_key)
            if value not in history[dataset]
        ]
        expected = sorted(
            eligible, key=lambda value: selection_key(DATASET_KEYS[dataset], value)
        )[: SAMPLE_SIZES[dataset]]
        if actual[dataset] != expected:
            raise ValueError(f"{dataset}: zero-overlap ID-only selection differs")
        if set(actual[dataset]) & history[dataset]:
            raise ValueError(f"{dataset}: historical overlap is nonzero")
        checks[dataset] = {
            "eligible_source_ids": len(eligible),
            "historical_ids": len(history[dataset]),
            "historical_id_sha256": id_digest(sorted(history[dataset])),
            "sample_ids": len(actual[dataset]),
            "sample_id_sha256": id_digest(actual[dataset]),
        }
    return checks


def _validated_cache_matrix(
    matrix: np.ndarray, expected_rows: int, label: str
) -> np.ndarray:
    matrix = np.asarray(matrix, dtype="float32")
    if (
        matrix.ndim != 2
        or matrix.shape[0] != expected_rows
        or not np.isfinite(matrix).all()
    ):
        raise ValueError(f"{label}: cache matrix differs")
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    if np.any(norms <= 0.0) or not np.allclose(
        norms[:, 0], 1.0, atol=1e-5, rtol=0.0
    ):
        raise ValueError(f"{label}: cache embeddings are not L2-normalized")
    return matrix


def _load_embedding_cache(
    path: Path,
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    with np.load(path, allow_pickle=False) as cache:
        required = {
            "metadata_json",
            "query_embeddings",
            "query_ids",
            "unit_embeddings",
            "unit_ids",
        }
        if set(cache.files) != required:
            raise ValueError(f"{path}: cache member contract differs")
        if cache["unit_ids"].tolist() != [row["unit_id"] for row in units]:
            raise ValueError(f"{path}: cache unit identity/order differs")
        if cache["query_ids"].tolist() != [row["query_id"] for row in queries]:
            raise ValueError(f"{path}: cache query identity/order differs")
        unit = np.asarray(cache["unit_embeddings"], dtype="float32")
        query = np.asarray(cache["query_embeddings"], dtype="float32")
        metadata = json.loads(str(cache["metadata_json"].item()))
    if not isinstance(metadata, dict):
        raise ValueError(f"{path}: cache metadata differs")
    return (
        _validated_cache_matrix(unit, len(units), f"{path}.unit"),
        _validated_cache_matrix(query, len(queries), f"{path}.query"),
        metadata,
    )


def _place_protected(
    bge_ids: list[str], inserted: list[str], effective_k: int, protect_n: int
) -> list[str]:
    if len(inserted) != len(set(inserted)) or set(inserted) & set(bge_ids):
        raise ValueError("independent protected placement input differs")
    result = bge_ids[:protect_n] + inserted + bge_ids[protect_n:]
    if len(result) < effective_k:
        raise ValueError("independent protected placement is short")
    return result[:effective_k]


def _place_unprotected(
    bge_ids: list[str], inserted: list[str], effective_k: int
) -> list[str]:
    if len(inserted) != len(set(inserted)) or set(inserted) & set(bge_ids):
        raise ValueError("independent unprotected placement input differs")
    result = inserted + bge_ids
    if len(result) < effective_k:
        raise ValueError("independent unprotected placement is short")
    return result[:effective_k]


def independent_rankings(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    minilm_unit: np.ndarray,
    minilm_query: np.ndarray,
    strong_unit: np.ndarray,
    strong_query: np.ndarray,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    indices_by_query: dict[str, list[int]] = defaultdict(list)
    for index, unit in enumerate(units):
        indices_by_query[unit["query_id"]].append(index)
    retrieval = RetrievalConfig()
    rankings: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    for query_index, query in enumerate(queries):
        query_id = query["query_id"]
        candidate_indices = indices_by_query[query_id]
        effective_k = min(retrieval.max_k, len(candidate_indices))
        bge_scores = np.asarray(
            [
                float(np.dot(strong_query[query_index], strong_unit[index]))
                for index in candidate_indices
            ],
            dtype="float64",
        )
        bge_ids = rank_from_scores(
            candidate_indices, units, bge_scores, retrieval.max_k
        )
        facet_candidates, selected_edges, facet_info = (
            expansion_candidates_goldfree(
                query,
                minilm_query[query_index],
                candidate_indices,
                units,
                minilm_unit,
                retrieval,
            )
        )
        facet_eligible = [
            require_native_string(row.get("unit_id"), "facet candidate unit_id")
            for row in facet_candidates
            if row["score"] >= retrieval.q25_floor
        ]
        facet_post_dedup = [
            unit_id for unit_id in facet_eligible if unit_id not in bge_ids
        ]
        inserted = facet_post_dedup[: retrieval.insert_budget]
        protected = _place_protected(
            bge_ids, inserted, effective_k, retrieval.protect_n
        )
        unprotected = _place_unprotected(bge_ids, inserted, effective_k)

        nofacet_candidates, nofacet_info = centroid_only_expansion(
            query,
            minilm_query[query_index],
            candidate_indices,
            units,
            minilm_unit,
            retrieval,
        )
        nofacet_eligible = [
            require_native_string(row.get("unit_id"), "no-facet candidate unit_id")
            for row in nofacet_candidates
            if row["score"] >= retrieval.q25_floor
        ]
        nofacet_post_dedup = [
            unit_id for unit_id in nofacet_eligible if unit_id not in bge_ids
        ]
        nofacet_inserted = nofacet_post_dedup[: retrieval.insert_budget]
        nofacet = _place_protected(
            bge_ids, nofacet_inserted, effective_k, retrieval.protect_n
        )
        methods = {
            "BGE_TOP20": bge_ids,
            "BGE_HGRAG_PROTECTED_TOP20": protected,
            "BGE_HGRAG_UNPROTECTED_TOP20": unprotected,
            "BGE_HGRAG_NO_FACET_TOP20": nofacet,
        }
        if set(methods) != set(METHODS):
            raise ValueError(f"{query_id}: method contract differs")
        candidate_ids = {units[index]["unit_id"] for index in candidate_indices}
        for method, values in methods.items():
            if (
                len(values) != effective_k
                or len(values) != len(set(values))
                or not set(values) <= candidate_ids
            ):
                raise ValueError(f"{query_id}/{method}: ranking contract differs")
        if protected[retrieval.protect_n : retrieval.protect_n + len(inserted)] != inserted:
            raise ValueError(f"{query_id}: protected placement differs")
        if unprotected[: len(inserted)] != inserted:
            raise ValueError(f"{query_id}: unprotected placement differs")
        rankings.append(
            {
                "dataset": query["dataset"],
                "effective_k": effective_k,
                "full_inserted_unit_ids": inserted,
                "methods": methods,
                "no_facet_inserted_unit_ids": nofacet_inserted,
                "query_id": query_id,
                "sample_id": query["sample_id"],
            }
        )
        traces.append(
            {
                "dataset": query["dataset"],
                "effective_k": effective_k,
                "full_eligible_count": len(facet_eligible),
                "full_eligible_unit_ids": facet_eligible,
                "full_insert_count": len(inserted),
                "full_inserted_unit_ids": inserted,
                "full_overlap_bge_top10_count": len(
                    set(facet_eligible) & set(bge_ids[: retrieval.protect_n])
                ),
                "full_overlap_bge_top20_count": len(
                    set(facet_eligible) & set(bge_ids)
                ),
                "full_post_dedup_count": len(facet_post_dedup),
                "full_post_dedup_unit_ids": facet_post_dedup,
                "full_selected_edge_count": len(selected_edges),
                "full_selected_edge_ids": [row["edge_id"] for row in selected_edges],
                "no_facet_eligible_count": len(nofacet_eligible),
                "no_facet_insert_count": len(nofacet_inserted),
                "no_facet_inserted_unit_ids": nofacet_inserted,
                "no_facet_post_dedup_count": len(nofacet_post_dedup),
                "query_id": query_id,
                "sample_id": query["sample_id"],
                "sidecar_score_space": "MINILM_COSINE_Q25_ELIGIBILITY",
                "strong_backbone": "BGE_LARGE_EN_V1_5_TOP20",
                "full_ball_score_margin": float(facet_info["ball_score_margin"]),
                "full_boundary_margin": float(facet_info["boundary_margin"]),
                "no_facet_ball_score_margin": float(
                    nofacet_info["ball_score_margin"]
                ),
                "no_facet_boundary_margin": float(nofacet_info["boundary_margin"]),
            }
        )
    return rankings, traces


def _distribution(values: list[int]) -> dict[str, float | int]:
    if not values:
        raise ValueError("cannot summarize an empty distribution")
    array = np.asarray(values, dtype="float64")
    return {
        "maximum": int(np.max(array)),
        "mean": float(np.mean(array)),
        "median": float(np.median(array)),
        "minimum": int(np.min(array)),
        "p25": float(np.percentile(array, 25, method="linear")),
        "p75": float(np.percentile(array, 75, method="linear")),
    }


def independent_eligibility(
    traces: list[dict[str, Any]], minimum_each: float, minimum_combined: float
) -> dict[str, Any]:
    datasets: dict[str, Any] = {}
    total_insertable = 0
    for dataset in DATASETS:
        rows = [row for row in traces if row["dataset"] == dataset]
        query_count = len(rows)
        if query_count == 0:
            raise ValueError(f"{dataset}: eligibility audit has no rows")
        eligible_count = sum(row["full_eligible_count"] > 0 for row in rows)
        insertable_count = sum(row["full_post_dedup_count"] > 0 for row in rows)
        full_budget_count = sum(row["full_insert_count"] == 4 for row in rows)
        total_insertable += insertable_count
        datasets[dataset] = {
            "eligible_candidate_count": _distribution(
                [row["full_eligible_count"] for row in rows]
            ),
            "eligible_query_count": eligible_count,
            "eligible_query_rate": eligible_count / query_count,
            "full_budget_query_count": full_budget_count,
            "full_budget_query_rate": full_budget_count / query_count,
            "insertable_query_count": insertable_count,
            "insertable_query_rate": insertable_count / query_count,
            "overlap_bge_protected_count": _distribution(
                [row["full_overlap_bge_top10_count"] for row in rows]
            ),
            "overlap_bge_top20_count": _distribution(
                [row["full_overlap_bge_top20_count"] for row in rows]
            ),
            "post_dedup_candidate_count": _distribution(
                [row["full_post_dedup_count"] for row in rows]
            ),
            "query_count": query_count,
            "realized_insertion_count": _distribution(
                [row["full_insert_count"] for row in rows]
            ),
            "zero_insertion_query_count": query_count - insertable_count,
            "zero_insertion_query_rate": 1.0 - insertable_count / query_count,
        }
    combined = total_insertable / len(traces)
    passed = (
        all(
            datasets[dataset]["insertable_query_rate"] >= minimum_each
            for dataset in DATASETS
        )
        and combined >= minimum_combined
    )
    return {
        "combined_insertable_query_rate": combined,
        "datasets": datasets,
        "gate": {
            "minimum_insertable_query_rate_combined": minimum_combined,
            "minimum_insertable_query_rate_each_dataset": minimum_each,
            "pass": passed,
            "status": (
                "STAGE4I_SIDECAR_ELIGIBILITY_GATE_PASS"
                if passed
                else "STAGE4I_SIDECAR_ACTIVATION_DEGENERATE"
            ),
        },
        "interpretation": "BLIND_ONLY_FEASIBILITY_NOT_POWER_GUARANTEE",
        "near_all_open_caution": any(
            datasets[dataset]["eligible_query_rate"] >= 0.95
            for dataset in DATASETS
        ),
        "query_count": len(traces),
        "status": "STAGE4I_BLIND_ELIGIBILITY_AUDIT_COMPLETE",
    }


def _query_map(queries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, query in enumerate(queries):
        query_id = require_native_string(query.get("query_id"), f"queries[{index}]")
        if query_id in result:
            raise ValueError("duplicate query identity")
        result[query_id] = query
    return result


def _pair_map(
    rows: list[dict[str, Any]],
    queries: dict[str, dict[str, Any]],
    label: str,
) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"{label}[{index}] must be an object")
        query_id = require_native_string(row.get("query_id"), f"{label}.query_id")
        method = require_native_string(row.get("method"), f"{label}.method")
        query = queries.get(query_id)
        if query is None or method not in METHODS:
            raise ValueError(f"{label}[{index}] identity differs")
        if (
            row.get("dataset") != query["dataset"]
            or row.get("sample_id") != query["sample_id"]
        ):
            raise ValueError(f"{label}[{index}] row identity differs")
        key = query_id, method
        if key in result:
            raise ValueError(f"{label}: duplicate pair {key}")
        result[key] = row
    return result


def _subset_query_ids(queries: list[dict[str, Any]]) -> set[str]:
    by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in queries:
        by_dataset[row["dataset"]].append(row)
    selected: set[str] = set()
    for dataset in DATASETS:
        rows = sorted(
            by_dataset[dataset],
            key=lambda row: rerun_selection_key(dataset, row["query_id"]),
        )[:RERUN_QUERIES_PER_DATASET]
        if len(rows) != RERUN_QUERIES_PER_DATASET:
            raise ValueError(f"{dataset}: deterministic subset differs")
        selected.update(row["query_id"] for row in rows)
    return selected


def verify_deterministic_subset(
    queries: list[dict[str, Any]],
    predictions_main: list[dict[str, Any]],
    predictions_subset: list[dict[str, Any]],
    prompts_main: list[dict[str, Any]],
    prompts_subset: list[dict[str, Any]],
) -> dict[str, Any]:
    query_by_id = _query_map(queries)
    subset_ids = _subset_query_ids(queries)
    expected_pairs = {
        (query_id, method) for query_id in subset_ids for method in METHODS
    }
    main_predictions = _pair_map(predictions_main, query_by_id, "predictions_main")
    subset_predictions = _pair_map(
        predictions_subset, query_by_id, "predictions_subset"
    )
    main_prompts = _pair_map(prompts_main, query_by_id, "prompts_main")
    subset_prompts = _pair_map(prompts_subset, query_by_id, "prompts_subset")
    if set(subset_predictions) != expected_pairs or set(subset_prompts) != expected_pairs:
        raise ValueError("deterministic subset coverage differs")
    for key in expected_pairs:
        if subset_predictions[key] != main_predictions[key]:
            raise ValueError(f"subset prediction differs: {key}")
        if subset_prompts[key] != main_prompts[key]:
            raise ValueError(f"subset prompt differs: {key}")
    return {
        "pairs": len(expected_pairs),
        "predictions_identical": True,
        "prompts_identical": True,
        "queries": len(subset_ids),
    }


def _prompt_projection(row: dict[str, Any]) -> dict[str, Any]:
    evidence_ids = row.get("evidence_unit_ids")
    if (
        not isinstance(evidence_ids, list)
        or any(not isinstance(value, str) or not value for value in evidence_ids)
    ):
        raise ValueError("prompt evidence_unit_ids differ")
    return {
        "evidence_unit_ids": evidence_ids,
        "input_token_count": require_json_int(
            row.get("input_token_count"), "prompt.input_token_count"
        ),
        "prompt_sha256": require_native_string(
            row.get("prompt_sha256"), "prompt.prompt_sha256"
        ),
        "rank1_truncated": row.get("rank1_truncated"),
    }


def verify_prompts(
    parent: dict[str, Any],
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    rankings: list[dict[str, Any]],
    prompt_rows: list[dict[str, Any]],
) -> None:
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        Path(parent["paths"]["generator_snapshot"]), local_files_only=True
    )
    query_by_id = _query_map(queries)
    prompt_map = _pair_map(prompt_rows, query_by_id, "prompt_audit_main")
    expected_pairs = {
        (query["query_id"], method) for query in queries for method in METHODS
    }
    if set(prompt_map) != expected_pairs:
        raise ValueError("main prompt coverage differs")
    unit_by_id = {row["unit_id"]: row for row in units}
    ranking_by_id = {row["query_id"]: row for row in rankings}
    for query in queries:
        for method in METHODS:
            evidence = ranking_by_id[query["query_id"]]["methods"][method]
            expected = _prompt_projection(
                build_prompt(
                    tokenizer,
                    query["question"],
                    [unit_by_id[unit_id] for unit_id in evidence],
                    4096,
                )
            )
            actual = _prompt_projection(prompt_map[(query["query_id"], method)])
            if actual != expected:
                raise ValueError(
                    f"{query['query_id']}/{method}: prompt reconstruction differs"
                )


def verify_pregold(config: dict[str, Any]) -> dict[str, Any]:
    validate_authorization(config)
    assert_implementation_binding(config, Path(__file__).resolve().parents[1])
    parent = validate_inherited_models(config)
    parent_artifacts = assert_parent_stage4h_artifacts(parent)
    blind_path = assert_bound(config, "blind")
    blind = load_jsonl(blind_path)
    assert_no_gold_fields(blind, "Stage4I blind channel")
    units, queries = build_units_queries(blind)
    if len(queries) != sum(SAMPLE_SIZES.values()):
        raise ValueError("Stage4I query count differs")
    selection = verify_input_selection(config, parent, blind)
    manifest = load_json(assert_bound(config, "input_manifest"))
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema_version") != SCHEMA_VERSION
        or manifest.get("status")
        != "STAGE4I_INPUT_CHANNELS_BUILT_PENDING_VERIFICATION"
        or manifest.get("query_id_sha256")
        != id_digest(row["query_id"] for row in blind)
        or manifest.get("sample_id_sha256")
        != id_digest(row["sample_id"] for row in blind)
    ):
        raise ValueError("Stage4I input manifest differs")
    channel = manifest.get("channels", {}).get("blind")
    if (
        not isinstance(channel, dict)
        or channel.get("bytes") != blind_path.stat().st_size
        or channel.get("sha256") != file_identity(blind_path)["sha256"]
        or channel.get("rows") != len(blind)
    ):
        raise ValueError("Stage4I blind manifest identity differs")

    minilm_unit, minilm_query, minilm_metadata = _load_embedding_cache(
        assert_bound(config, "minilm_embedding_cache"), units, queries
    )
    strong_unit, strong_query, strong_metadata = _load_embedding_cache(
        assert_bound(config, "strong_embedding_cache"), units, queries
    )
    rankings, traces = independent_rankings(
        units,
        queries,
        minilm_unit,
        minilm_query,
        strong_unit,
        strong_query,
    )
    if assert_bound(config, "rankings").read_bytes() != render_jsonl(rankings):
        raise ValueError("independent four-arm ranking reconstruction differs")
    if assert_bound(config, "candidate_trace").read_bytes() != render_jsonl(traces):
        raise ValueError("independent sidecar candidate reconstruction differs")
    gate = config.get("eligibility_gate")
    if not isinstance(gate, dict):
        raise ValueError("eligibility gate config differs")
    expected_eligibility = independent_eligibility(
        traces,
        float(gate["minimum_insertable_query_rate_each_dataset"]),
        float(gate["minimum_insertable_query_rate_combined"]),
    )
    actual_eligibility = load_json(assert_bound(config, "eligibility_audit"))
    if not isinstance(actual_eligibility, dict):
        raise ValueError("eligibility audit differs")
    deterministic_actual = {
        key: actual_eligibility.get(key) for key in expected_eligibility
    }
    if deterministic_actual != expected_eligibility:
        raise ValueError("independent eligibility reconstruction differs")
    if expected_eligibility["gate"]["pass"] is not True:
        raise RuntimeError("STAGE4I_SIDECAR_ACTIVATION_DEGENERATE")

    predictions_main = load_jsonl(assert_bound(config, "predictions_main"))
    predictions_subset = load_jsonl(
        assert_bound(config, "predictions_rerun_subset")
    )
    prompts_main = load_jsonl(assert_bound(config, "prompt_audit_main"))
    prompts_subset = load_jsonl(
        assert_bound(config, "prompt_audit_rerun_subset")
    )
    query_by_id = _query_map(queries)
    expected_pairs = {
        (query["query_id"], method) for query in queries for method in METHODS
    }
    prediction_pairs = _pair_map(predictions_main, query_by_id, "predictions_main")
    if set(prediction_pairs) != expected_pairs:
        raise ValueError("main prediction coverage differs")
    if any(
        not isinstance(row.get("prediction"), str) for row in predictions_main
    ):
        raise ValueError("prediction value must be a native string")
    verify_prompts(parent, units, queries, rankings, prompts_main)
    subset = verify_deterministic_subset(
        queries,
        predictions_main,
        predictions_subset,
        prompts_main,
        prompts_subset,
    )
    for key in ("telemetry_main", "telemetry_rerun_subset"):
        telemetry = load_json(assert_bound(config, key))
        if (
            not isinstance(telemetry, dict)
            or telemetry.get("failed_calls") != 0
            or telemetry.get("status")
            != "STAGE4I_GOLDFREE_RUN_COMPLETE_PENDING_VERIFICATION"
        ):
            raise ValueError(f"{key} status differs")
    artifact_keys = (
        "blind",
        "input_manifest",
        "minilm_embedding_cache",
        "strong_embedding_cache",
        "eligibility_audit",
        "rankings",
        "candidate_trace",
        "predictions_main",
        "prompt_audit_main",
        "telemetry_main",
        "predictions_rerun_subset",
        "prompt_audit_rerun_subset",
        "telemetry_rerun_subset",
    )
    verification = {
        "artifacts": {
            key: file_identity(assert_bound(config, key)) for key in artifact_keys
        },
        "checks": {
            "blind_gold_fields_absent": True,
            "candidate_units": len(units),
            "eligibility_reconstruction": True,
            "four_arm_ranking_reconstruction": True,
            "input_selection": selection,
            "main_pairs": len(expected_pairs),
            "minilm_cache_metadata": minilm_metadata,
            "parent_stage4h_artifact_count": len(parent_artifacts),
            "prompt_reconstruction": True,
            "q25_applied_only_in_minilm_sidecar_space": True,
            "strong_cache_metadata": strong_metadata,
            "subset_determinism": subset,
        },
        "query_count": len(queries),
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4I_PRE_GOLD_VERIFICATION_PASS",
    }
    write_new_files_atomically(
        ((path_from_config(config, "verified_pregold"), render_json(verification)),)
    )
    return verification


def _normalize_answer(value: str) -> str:
    value = value.lower()
    value = "".join(character for character in value if character not in string.punctuation)
    value = re.sub(r"\b(a|an|the)\b", " ", value)
    return " ".join(value.split())


def _answer_scores(prediction: str, answers: list[str]) -> tuple[float, float]:
    normalized_prediction = _normalize_answer(prediction)
    best_em = 0.0
    best_f1 = 0.0
    for answer in answers:
        normalized_answer = _normalize_answer(answer)
        em = float(normalized_prediction == normalized_answer)
        predicted_tokens = normalized_prediction.split()
        answer_tokens = normalized_answer.split()
        if not predicted_tokens or not answer_tokens:
            f1 = float(predicted_tokens == answer_tokens)
        else:
            overlap = sum(
                (Counter(predicted_tokens) & Counter(answer_tokens)).values()
            )
            if overlap == 0:
                f1 = 0.0
            else:
                precision = overlap / len(predicted_tokens)
                recall = overlap / len(answer_tokens)
                f1 = 2.0 * precision * recall / (precision + recall)
        best_em = max(best_em, em)
        best_f1 = max(best_f1, f1)
    return best_em, best_f1


def _paragraph_indices(unit_ids: list[str]) -> set[int]:
    result: set[int] = set()
    for unit_id in unit_ids:
        match = re.search(r"::p([0-9]+)::s[0-9]+$", unit_id)
        if match is None:
            raise ValueError(f"cannot parse paragraph from unit_id: {unit_id}")
        result.add(int(match.group(1)))
    return result


def _gold_unit_membership(gold: dict[str, Any], unit_ids: list[str]) -> set[str]:
    if gold["dataset"] == HOTPOT_DATASET:
        targets = set(gold["supporting_unit_ids"])
        return {unit_id for unit_id in unit_ids if unit_id in targets}
    targets = set(gold["supporting_paragraph_indices"])
    return {
        unit_id
        for unit_id in unit_ids
        if next(iter(_paragraph_indices([unit_id]))) in targets
    }


def _validated_gold(
    rows: list[dict[str, Any]],
    queries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if len(rows) != len(queries):
        raise ValueError("Gold row count differs")
    for index, (gold, query) in enumerate(zip(rows, queries)):
        for key in ("query_id", "dataset", "sample_id"):
            value = require_native_string(gold.get(key), f"gold[{index}].{key}")
            if value != query[key]:
                raise ValueError(f"gold[{index}].{key} differs")
        answers = gold.get("answers")
        if (
            not isinstance(answers, list)
            or not answers
            or any(not isinstance(value, str) or not value.strip() for value in answers)
        ):
            raise ValueError(f"gold[{index}].answers differ")
        if gold["dataset"] == HOTPOT_DATASET:
            supports = gold.get("supporting_unit_ids")
            if (
                gold.get("evidence_granularity")
                != "official_supporting_sentence"
                or not isinstance(supports, list)
                or not supports
                or any(not isinstance(value, str) or not value for value in supports)
            ):
                raise ValueError(f"gold[{index}] Hotpot support contract differs")
        else:
            supports = gold.get("supporting_paragraph_indices")
            if (
                gold.get("evidence_granularity")
                != "official_supporting_paragraph"
                or not isinstance(supports, list)
                or not supports
                or any(
                    isinstance(value, bool) or not isinstance(value, int) or value < 0
                    for value in supports
                )
            ):
                raise ValueError(f"gold[{index}] MuSiQue support contract differs")
    return rows


def independent_query_audit(
    gold_rows: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    prediction_rows: list[dict[str, Any]],
    prompt_rows: list[dict[str, Any]],
    ranking_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    query_by_id = _query_map(queries)
    predictions = _pair_map(prediction_rows, query_by_id, "predictions")
    prompts = _pair_map(prompt_rows, query_by_id, "prompts")
    ranking_by_id = {row["query_id"]: row for row in ranking_rows}
    expected_pairs = {
        (row["query_id"], method) for row in gold_rows for method in METHODS
    }
    if set(predictions) != expected_pairs or set(prompts) != expected_pairs:
        raise ValueError("Gold evaluation pair coverage differs")
    if set(ranking_by_id) != {row["query_id"] for row in gold_rows}:
        raise ValueError("Gold ranking coverage differs")
    audits: list[dict[str, Any]] = []
    for gold in gold_rows:
        query_id = gold["query_id"]
        ranking_row = ranking_by_id[query_id]
        methods: dict[str, Any] = {}
        for method in METHODS:
            prediction = predictions[(query_id, method)]
            prompt = prompts[(query_id, method)]
            ranking = ranking_row["methods"][method]
            if prompt.get("evidence_unit_ids") != ranking[
                : len(prompt.get("evidence_unit_ids", []))
            ]:
                raise ValueError(f"{query_id}/{method}: prompt is not ranking prefix")
            em, f1 = _answer_scores(prediction["prediction"], gold["answers"])
            if gold["dataset"] == HOTPOT_DATASET:
                targets = set(gold["supporting_unit_ids"])
                retrieved = set(ranking)
            else:
                targets = set(gold["supporting_paragraph_indices"])
                retrieved = _paragraph_indices(ranking)
            overlap = len(targets & retrieved)
            methods[method] = {
                "answer_em": em,
                "answer_f1": f1,
                "evidence_count": len(prompt["evidence_unit_ids"]),
                "input_token_count": require_json_int(
                    prompt.get("input_token_count"), "prompt.input_token_count"
                ),
                "retrieval_cr20": float(overlap == len(targets)),
                "retrieval_er20": overlap / len(targets),
                "unknown": float(
                    prediction["prediction"].strip().upper() == "UNKNOWN"
                ),
            }
        bge_ids = ranking_row["methods"][CORE_RIGHT]
        transitions: dict[str, Any] = {}
        for method in METHODS:
            if method == CORE_RIGHT:
                continue
            method_ids = ranking_row["methods"][method]
            added_units = [value for value in method_ids if value not in bge_ids]
            displaced_units = [value for value in bge_ids if value not in method_ids]
            added_gold_units = _gold_unit_membership(gold, added_units)
            displaced_gold_units = _gold_unit_membership(gold, displaced_units)
            if gold["dataset"] == HOTPOT_DATASET:
                targets = set(gold["supporting_unit_ids"])
                bge_gold = set(bge_ids) & targets
                method_gold = set(method_ids) & targets
            else:
                targets = set(gold["supporting_paragraph_indices"])
                bge_gold = _paragraph_indices(bge_ids) & targets
                method_gold = _paragraph_indices(method_ids) & targets
            added_gold = len(method_gold - bge_gold)
            displaced_gold = len(bge_gold - method_gold)
            answer_delta = (
                methods[method]["answer_f1"] - methods[CORE_RIGHT]["answer_f1"]
            )
            transitions[method] = {
                "added_gold_evidence": added_gold,
                "added_gold_unit_count": len(added_gold_units),
                "added_non_gold_units": len(added_units) - len(added_gold_units),
                "added_unit_count": len(added_units),
                "answer_change": (
                    "GAIN"
                    if answer_delta > 0
                    else "HARM"
                    if answer_delta < 0
                    else "SAME"
                ),
                "displaced_bge_gold_evidence": displaced_gold,
                "displaced_gold_unit_count": len(displaced_gold_units),
                "displaced_non_gold_units": (
                    len(displaced_units) - len(displaced_gold_units)
                ),
                "displaced_unit_count": len(displaced_units),
                "net_gold_evidence_change": added_gold - displaced_gold,
            }
        audits.append(
            {
                "dataset": gold["dataset"],
                "methods": methods,
                "query_id": query_id,
                "sample_id": gold["sample_id"],
                "transitions_relative_to_bge": transitions,
            }
        )
    return audits


def _interval(point: float, samples: np.ndarray) -> dict[str, float]:
    return {
        "ci95_lower": float(np.percentile(samples, 2.5, method="linear")),
        "ci95_upper": float(np.percentile(samples, 97.5, method="linear")),
        "point": float(point),
    }


def _paired_bootstrap(
    left_f1: np.ndarray,
    right_f1: np.ndarray,
    left_em: np.ndarray,
    right_em: np.ndarray,
    seed: int,
) -> dict[str, Any]:
    arrays = (left_f1, right_f1, left_em, right_em)
    if any(
        array.ndim != 1
        or len(array) == 0
        or len(array) != len(left_f1)
        or not np.isfinite(array).all()
        for array in arrays
    ):
        raise ValueError("paired bootstrap arrays differ")
    rng = np.random.default_rng(seed)
    f1_delta = left_f1 - right_f1
    em_delta = left_em - right_em
    f1_samples = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    em_samples = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    for index in range(BOOTSTRAP_ITERATIONS):
        sample = rng.integers(0, len(f1_delta), len(f1_delta))
        f1_samples[index] = float(np.mean(f1_delta[sample]))
        em_samples[index] = float(np.mean(em_delta[sample]))
    f1 = _interval(float(np.mean(f1_delta)), f1_samples)
    em = _interval(float(np.mean(em_delta)), em_samples)
    f1["one_sided_positive_p"] = float(
        (1 + np.count_nonzero(f1_samples <= 0.0))
        / (BOOTSTRAP_ITERATIONS + 1)
    )
    return {"delta_answer_em": em, "delta_answer_f1": f1}


def _equal_weight_bootstrap(
    values: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
    seed: int,
) -> dict[str, Any]:
    if set(values) != set(DATASETS):
        raise ValueError("equal-weight bootstrap datasets differ")
    rng = np.random.default_rng(seed)
    deltas = {
        dataset: (values[dataset][0] - values[dataset][1], values[dataset][2] - values[dataset][3])
        for dataset in DATASETS
    }
    f1_samples = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    em_samples = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    for index in range(BOOTSTRAP_ITERATIONS):
        f1_means: list[float] = []
        em_means: list[float] = []
        for dataset in DATASETS:
            f1_delta, em_delta = deltas[dataset]
            sample = rng.integers(0, len(f1_delta), len(f1_delta))
            f1_means.append(float(np.mean(f1_delta[sample])))
            em_means.append(float(np.mean(em_delta[sample])))
        f1_samples[index] = float(np.mean(f1_means))
        em_samples[index] = float(np.mean(em_means))
    f1 = _interval(
        float(np.mean([np.mean(deltas[dataset][0]) for dataset in DATASETS])),
        f1_samples,
    )
    em = _interval(
        float(np.mean([np.mean(deltas[dataset][1]) for dataset in DATASETS])),
        em_samples,
    )
    f1["one_sided_positive_p"] = float(
        (1 + np.count_nonzero(f1_samples <= 0.0))
        / (BOOTSTRAP_ITERATIONS + 1)
    )
    return {"delta_answer_em": em, "delta_answer_f1": f1}


def _comparison(
    by_dataset: dict[str, list[dict[str, Any]]],
    left: str,
    right: str,
    seed_offset: int,
) -> dict[str, Any]:
    datasets: dict[str, Any] = {}
    inputs: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
    for dataset_index, dataset in enumerate(DATASETS):
        rows = by_dataset[dataset]
        arrays = tuple(
            np.asarray(
                [row["methods"][method][metric] for row in rows],
                dtype="float64",
            )
            for method, metric in (
                (left, "answer_f1"),
                (right, "answer_f1"),
                (left, "answer_em"),
                (right, "answer_em"),
            )
        )
        inputs[dataset] = arrays  # type: ignore[assignment]
        datasets[dataset] = _paired_bootstrap(
            *arrays, BOOTSTRAP_SEED + seed_offset * 100 + dataset_index
        )
    return {
        "contrast": f"{left} - {right}",
        "dataset_equal_weight": _equal_weight_bootstrap(
            inputs, BOOTSTRAP_SEED + 1000 + seed_offset
        ),
        "datasets": datasets,
    }


def _core_decision(summary: dict[str, Any]) -> str:
    pooled = summary["dataset_equal_weight"]
    f1 = pooled["delta_answer_f1"]
    em = pooled["delta_answer_em"]
    dataset_points = [
        summary["datasets"][dataset]["delta_answer_f1"]["point"]
        for dataset in DATASETS
    ]
    dataset_uppers = [
        summary["datasets"][dataset]["delta_answer_f1"]["ci95_upper"]
        for dataset in DATASETS
    ]
    if f1["ci95_upper"] < 0.0 or em["ci95_upper"] < -0.010:
        return "STRONG_DENSE_COMPLEMENTARITY_NEGATIVE"
    if (
        dataset_points[0] * dataset_points[1] < 0.0
        or any(value < 0.0 for value in dataset_uppers)
    ):
        return "STRONG_DENSE_COMPLEMENTARITY_CROSS_DATASET_HETEROGENEOUS"
    supported = (
        f1["ci95_lower"] > 0.0
        and all(value > 0.0 for value in dataset_points)
        and em["ci95_lower"] >= -0.010
    )
    if supported and f1["point"] >= 0.010:
        return "STRONG_DENSE_COMPLEMENTARITY_SUPPORTED"
    if supported and 0.0 < f1["point"] < 0.010:
        return "STRONG_DENSE_COMPLEMENTARITY_SUPPORTED_SMALL_EFFECT"
    return "STRONG_DENSE_COMPLEMENTARITY_INCONCLUSIVE"


def _supportive_state(summary: dict[str, Any], prefix: str) -> str:
    pooled = summary["dataset_equal_weight"]
    f1 = pooled["delta_answer_f1"]
    em = pooled["delta_answer_em"]
    if f1["ci95_lower"] > 0.0 and em["ci95_lower"] >= -0.010:
        return f"{prefix}_SUPPORTED"
    if f1["ci95_upper"] < 0.0 or em["ci95_upper"] < -0.010:
        return f"{prefix}_NEGATIVE"
    return f"{prefix}_INCONCLUSIVE"


def independent_summaries(
    audits: list[dict[str, Any]], telemetry: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    by_dataset = {
        dataset: [row for row in audits if row["dataset"] == dataset]
        for dataset in DATASETS
    }
    datasets: dict[str, Any] = {}
    for dataset, rows in by_dataset.items():
        methods = {
            method: {
                metric: float(
                    np.mean([row["methods"][method][metric] for row in rows])
                )
                for metric in (
                    "answer_em",
                    "answer_f1",
                    "evidence_count",
                    "input_token_count",
                    "retrieval_cr20",
                    "retrieval_er20",
                    "unknown",
                )
            }
            for method in METHODS
        }
        change: dict[str, Any] = {}
        for method in METHODS:
            if method == CORE_RIGHT:
                continue
            values = [
                row["methods"][method]["answer_f1"]
                - row["methods"][CORE_RIGHT]["answer_f1"]
                for row in rows
            ]
            change[method] = {
                "gain_queries": sum(value > 0 for value in values),
                "harm_queries": sum(value < 0 for value in values),
                "same_queries": sum(value == 0 for value in values),
            }
        datasets[dataset] = {
            "gain_same_harm_relative_to_bge": change,
            "methods": methods,
            "query_count": len(rows),
        }
    comparisons = {
        label: _comparison(by_dataset, left, right, index)
        for index, (label, (left, right)) in enumerate(COMPARISONS.items())
    }
    core = _core_decision(comparisons["protected_minus_bge"])
    placement_state = _supportive_state(
        comparisons["protected_minus_unprotected"], "PROTECTED_PLACEMENT"
    )
    facet_state = _supportive_state(
        comparisons["protected_minus_no_facet"], "BGE_FACET_INCREMENT"
    )
    equal_weight = {
        "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "comparisons": comparisons,
        "dataset_weights": {dataset: 0.5 for dataset in DATASETS},
        "primary_comparison": "protected_minus_bge",
        "status": "STAGE4I_STATISTICS_COMPLETE_PENDING_VERIFICATION",
    }
    placement = {
        "comparisons": {
            key: comparisons[key]
            for key in (
                "protected_minus_bge",
                "unprotected_minus_bge",
                "protected_minus_unprotected",
            )
        },
        "interpretation": "SUPPORTING_NO_CORE_ADVANCEMENT",
        "state": placement_state,
        "status": "STAGE4I_PLACEMENT_ANALYSIS_COMPLETE",
    }
    facet = {
        "comparison": comparisons["protected_minus_no_facet"],
        "interpretation": "SUPPORTING_NO_CORE_ADVANCEMENT",
        "state": facet_state,
        "status": "STAGE4I_FACET_ANALYSIS_COMPLETE",
    }
    decision = {
        "core_state": core,
        "facet_state": facet_state,
        "interpretation_boundary": (
            "One pre-specified BGE large-en-v1.5 backbone on new closed-candidate "
            "HotpotQA/MuSiQue IDs; no universal strong-retriever or full-wiki claim."
        ),
        "placement_state": placement_state,
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4I_SCIENTIFIC_DECISION_FROZEN_PENDING_FINAL_VERIFICATION",
    }
    datasets["_resource"] = {
        "embedding_cache": telemetry.get("embedding_cache"),
        "generation_seconds_by_method": telemetry.get("generation_seconds_by_method"),
        "gpu_peak_memory_bytes": telemetry.get("gpu_peak_memory_bytes"),
        "retrieval_seconds": telemetry.get("retrieval_seconds"),
    }
    return datasets, equal_weight, placement, facet, decision


def independent_evidence_summary(audits: list[dict[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for dataset in DATASETS:
        rows = [row for row in audits if row["dataset"] == dataset]
        output[dataset] = {}
        for method in METHODS:
            if method == CORE_RIGHT:
                continue
            transitions = [
                row["transitions_relative_to_bge"][method] for row in rows
            ]
            cross_tab: Counter[str] = Counter()
            for row in transitions:
                net = row["net_gold_evidence_change"]
                net_label = (
                    "POSITIVE" if net > 0 else "NEGATIVE" if net < 0 else "ZERO"
                )
                cross_tab[f"{row['answer_change']}|{net_label}"] += 1
            output[dataset][method] = {
                "added_gold_evidence_total": sum(
                    row["added_gold_evidence"] for row in transitions
                ),
                "added_non_gold_units_total": sum(
                    row["added_non_gold_units"] for row in transitions
                ),
                "answer_change_by_net_gold": dict(sorted(cross_tab.items())),
                "displaced_bge_gold_evidence_total": sum(
                    row["displaced_bge_gold_evidence"] for row in transitions
                ),
                "displaced_non_gold_units_total": sum(
                    row["displaced_non_gold_units"] for row in transitions
                ),
                "net_gold_evidence_change_total": sum(
                    row["net_gold_evidence_change"] for row in transitions
                ),
                "query_count": len(transitions),
            }
    return {
        "datasets": output,
        "interpretation": "POST_DECISION_DESCRIPTIVE_ONLY_NO_RETUNING_OR_ADVANCEMENT",
        "status": "STAGE4I_POST_GOLD_EVIDENCE_TRANSITION_AUDIT_COMPLETE",
    }


def verify_final(config: dict[str, Any]) -> dict[str, Any]:
    validate_authorization(config)
    assert_implementation_binding(config, Path(__file__).resolve().parents[1])
    parent = validate_inherited_models(config)
    parent_artifacts = assert_parent_stage4h_artifacts(parent)
    pregold = load_json(assert_bound(config, "verified_pregold"))
    if (
        not isinstance(pregold, dict)
        or pregold.get("status") != "STAGE4I_PRE_GOLD_VERIFICATION_PASS"
    ):
        raise PermissionError("Stage4I pre-Gold verification is absent")
    blind = load_jsonl(assert_bound(config, "blind"))
    _, queries = build_units_queries(blind)
    gold = _validated_gold(load_jsonl(assert_bound(config, "gold")), queries)
    rankings = load_jsonl(assert_bound(config, "rankings"))
    predictions = load_jsonl(assert_bound(config, "predictions_main"))
    prompts = load_jsonl(assert_bound(config, "prompt_audit_main"))
    audits = independent_query_audit(
        gold, queries, predictions, prompts, rankings
    )
    expected = {
        "query_audit": render_jsonl(audits),
    }
    telemetry = load_json(assert_bound(config, "telemetry_main"))
    if not isinstance(telemetry, dict):
        raise ValueError("telemetry_main differs")
    dataset, equal_weight, placement, facet, decision = independent_summaries(
        audits, telemetry
    )
    expected.update(
        {
            "dataset_summaries": render_json(dataset),
            "equal_weight_summary": render_json(equal_weight),
            "placement_summary": render_json(placement),
            "facet_summary": render_json(facet),
            "evidence_transition_audit": render_json(
                independent_evidence_summary(audits)
            ),
            "scientific_decision": render_json(decision),
        }
    )
    for key, payload in expected.items():
        if assert_bound(config, key).read_bytes() != payload:
            raise ValueError(f"{key}: independent reconstruction differs")
    locks = config.get("locks")
    if (
        not isinstance(locks, dict)
        or locks.get("reservation") != "LOCKED"
        or locks.get("stage3b") != "LOCKED"
        or locks.get("u2") != "NOT_AUTHORIZED"
        or locks.get("controller_branch") != "FROZEN_CLOSED"
    ):
        raise ValueError("Stage4I locked boundaries differ")
    artifact_keys = (
        "input_manifest",
        "eligibility_audit",
        "rankings",
        "candidate_trace",
        "predictions_main",
        "prompt_audit_main",
        "telemetry_main",
        "predictions_rerun_subset",
        "prompt_audit_rerun_subset",
        "telemetry_rerun_subset",
        "verified_pregold",
        "query_audit",
        "dataset_summaries",
        "equal_weight_summary",
        "placement_summary",
        "facet_summary",
        "evidence_transition_audit",
        "scientific_decision",
    )
    artifacts = {
        key: file_identity(assert_bound(config, key)) for key in artifact_keys
    }
    final = {
        "artifacts": artifacts,
        "checks": {
            "artifact_identities": True,
            "bootstrap_and_decision_reconstruction": True,
            "evidence_transition_reconstruction": True,
            "parent_stage4h_artifact_count": len(parent_artifacts),
            "query_metric_reconstruction": True,
            "reservation_locked": True,
            "stage3b_locked": True,
            "u2_not_authorized": True,
        },
        "core_state": decision["core_state"],
        "facet_state": decision["facet_state"],
        "placement_state": decision["placement_state"],
        "query_count": len(audits),
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4I_FINAL_VERIFICATION_PASS",
    }
    final_payload = render_json(final)
    manifest = {
        "artifact_count": len(artifacts) + 1,
        "artifacts": {
            **artifacts,
            "final_verification": {
                "bytes": len(final_payload),
                "sha256": sha256_bytes(final_payload),
            },
        },
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4I_ARTIFACT_MANIFEST_FROZEN",
    }
    write_new_files_atomically(
        (
            (path_from_config(config, "final_verification"), final_payload),
            (path_from_config(config, "artifact_manifest"), render_json(manifest)),
        )
    )
    return final


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("pregold", "final"))
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage4I config must be an object")
    result = (
        verify_pregold(config) if args.mode == "pregold" else verify_final(config)
    )
    print(f"{result['status']} queries={result['query_count']}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE4I_VERIFIER_FAIL: {exc}", file=sys.stderr)
        raise
