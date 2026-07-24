"""Gold-free BGE backbone plus frozen MiniLM-HGRAG sidecar retrieval."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

import numpy as np

from stage4f_xdr_retrieval import (
    RetrievalConfig,
    expansion_candidates_goldfree,
)
from stage4h_cbe_retrieval import (
    build_units_queries,
    centroid_only_expansion,
    rank_from_scores,
)
from stage4i_sdc_common import DATASETS, METHODS, require_native_string


def place_protected(
    bge_ids: list[str],
    inserted_ids: list[str],
    effective_k: int,
    protect_n: int = 10,
) -> list[str]:
    if len(inserted_ids) != len(set(inserted_ids)):
        raise ValueError("sidecar insertion IDs duplicate")
    if set(inserted_ids) & set(bge_ids):
        raise ValueError("sidecar insertion IDs must be absent from BGE Top-20")
    ranked = bge_ids[:protect_n] + inserted_ids + bge_ids[protect_n:]
    if len(ranked) < effective_k:
        raise ValueError("protected placement cannot fill effective-K")
    return ranked[:effective_k]


def place_unprotected(
    bge_ids: list[str],
    inserted_ids: list[str],
    effective_k: int,
) -> list[str]:
    if len(inserted_ids) != len(set(inserted_ids)):
        raise ValueError("sidecar insertion IDs duplicate")
    if set(inserted_ids) & set(bge_ids):
        raise ValueError("sidecar insertion IDs must be absent from BGE Top-20")
    ranked = inserted_ids + bge_ids
    if len(ranked) < effective_k:
        raise ValueError("unprotected placement cannot fill effective-K")
    return ranked[:effective_k]


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


def summarize_eligibility(
    traces: list[dict[str, Any]],
    minimum_each: float,
    minimum_combined: float,
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    all_insertable = 0
    for dataset in DATASETS:
        rows = [row for row in traces if row["dataset"] == dataset]
        if not rows:
            raise ValueError(f"{dataset}: eligibility audit has no rows")
        query_count = len(rows)
        eligible_count = sum(row["full_eligible_count"] > 0 for row in rows)
        insertable_count = sum(row["full_post_dedup_count"] > 0 for row in rows)
        full_budget_count = sum(row["full_insert_count"] == 4 for row in rows)
        all_insertable += insertable_count
        output[dataset] = {
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
    combined_rate = all_insertable / len(traces)
    each_pass = all(
        output[dataset]["insertable_query_rate"] >= minimum_each
        for dataset in DATASETS
    )
    gate_pass = each_pass and combined_rate >= minimum_combined
    return {
        "combined_insertable_query_rate": combined_rate,
        "datasets": output,
        "gate": {
            "minimum_insertable_query_rate_combined": minimum_combined,
            "minimum_insertable_query_rate_each_dataset": minimum_each,
            "pass": gate_pass,
            "status": (
                "STAGE4I_SIDECAR_ELIGIBILITY_GATE_PASS"
                if gate_pass
                else "STAGE4I_SIDECAR_ACTIVATION_DEGENERATE"
            ),
        },
        "interpretation": "BLIND_ONLY_FEASIBILITY_NOT_POWER_GUARANTEE",
        "near_all_open_caution": any(
            output[dataset]["eligible_query_rate"] >= 0.95 for dataset in DATASETS
        ),
        "query_count": len(traces),
        "status": "STAGE4I_BLIND_ELIGIBILITY_AUDIT_COMPLETE",
    }


def build_rankings(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    minilm_unit_embeddings: np.ndarray,
    minilm_query_embeddings: np.ndarray,
    strong_unit_embeddings: np.ndarray,
    strong_query_embeddings: np.ndarray,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, float]]:
    for matrix, count, label in (
        (minilm_unit_embeddings, len(units), "MiniLM units"),
        (minilm_query_embeddings, len(queries), "MiniLM queries"),
        (strong_unit_embeddings, len(units), "BGE units"),
        (strong_query_embeddings, len(queries), "BGE queries"),
    ):
        if matrix.ndim != 2 or matrix.shape[0] != count or not np.isfinite(matrix).all():
            raise ValueError(f"{label} embedding matrix differs")
    indices_by_query: dict[str, list[int]] = defaultdict(list)
    for index, unit in enumerate(units):
        indices_by_query[unit["query_id"]].append(index)
    config = RetrievalConfig()
    rankings: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    seconds = defaultdict(float)
    for query_index, query in enumerate(queries):
        query_id = query["query_id"]
        candidate_indices = indices_by_query[query_id]
        effective_k = min(config.max_k, len(candidate_indices))

        started = time.perf_counter()
        bge_scores = np.asarray(
            [
                float(
                    np.dot(
                        strong_query_embeddings[query_index],
                        strong_unit_embeddings[index],
                    )
                )
                for index in candidate_indices
            ],
            dtype="float64",
        )
        bge_ids = rank_from_scores(
            candidate_indices, units, bge_scores, config.max_k
        )
        seconds["BGE_TOP20"] += time.perf_counter() - started

        started = time.perf_counter()
        full_candidates, selected_edges, full_info = expansion_candidates_goldfree(
            query,
            minilm_query_embeddings[query_index],
            candidate_indices,
            units,
            minilm_unit_embeddings,
            config,
        )
        full_eligible = [
            require_native_string(row["unit_id"], "full candidate unit_id")
            for row in full_candidates
            if row["score"] >= config.q25_floor
        ]
        full_post_dedup = [unit_id for unit_id in full_eligible if unit_id not in bge_ids]
        full_inserted = full_post_dedup[: config.insert_budget]
        protected = place_protected(
            bge_ids, full_inserted, effective_k, config.protect_n
        )
        unprotected = place_unprotected(bge_ids, full_inserted, effective_k)
        seconds["HGRAG_FACET_SIDECAR"] += time.perf_counter() - started

        started = time.perf_counter()
        nofacet_candidates, nofacet_info = centroid_only_expansion(
            query,
            minilm_query_embeddings[query_index],
            candidate_indices,
            units,
            minilm_unit_embeddings,
            config,
        )
        nofacet_eligible = [
            require_native_string(row["unit_id"], "no-facet candidate unit_id")
            for row in nofacet_candidates
            if row["score"] >= config.q25_floor
        ]
        nofacet_post_dedup = [
            unit_id for unit_id in nofacet_eligible if unit_id not in bge_ids
        ]
        nofacet_inserted = nofacet_post_dedup[: config.insert_budget]
        nofacet = place_protected(
            bge_ids, nofacet_inserted, effective_k, config.protect_n
        )
        seconds["HGRAG_NO_FACET_SIDECAR"] += time.perf_counter() - started

        methods = {
            "BGE_TOP20": bge_ids,
            "BGE_HGRAG_PROTECTED_TOP20": protected,
            "BGE_HGRAG_UNPROTECTED_TOP20": unprotected,
            "BGE_HGRAG_NO_FACET_TOP20": nofacet,
        }
        if set(methods) != set(METHODS):
            raise ValueError(f"{query_id}: four-arm method contract differs")
        candidate_ids = {units[index]["unit_id"] for index in candidate_indices}
        for method, values in methods.items():
            if (
                method not in METHODS
                or len(values) != effective_k
                or len(values) != len(set(values))
                or not set(values) <= candidate_ids
            ):
                raise ValueError(f"{query_id}/{method}: ranking contract differs")
        if protected[config.protect_n : config.protect_n + len(full_inserted)] != full_inserted:
            raise ValueError(f"{query_id}: protected placement differs")
        if unprotected[: len(full_inserted)] != full_inserted:
            raise ValueError(f"{query_id}: unprotected placement differs")
        rankings.append(
            {
                "dataset": query["dataset"],
                "effective_k": effective_k,
                "full_inserted_unit_ids": full_inserted,
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
                "full_eligible_count": len(full_eligible),
                "full_eligible_unit_ids": full_eligible,
                "full_insert_count": len(full_inserted),
                "full_inserted_unit_ids": full_inserted,
                "full_overlap_bge_top10_count": len(
                    set(full_eligible) & set(bge_ids[: config.protect_n])
                ),
                "full_overlap_bge_top20_count": len(
                    set(full_eligible) & set(bge_ids)
                ),
                "full_post_dedup_count": len(full_post_dedup),
                "full_post_dedup_unit_ids": full_post_dedup,
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
                "full_ball_score_margin": float(full_info["ball_score_margin"]),
                "full_boundary_margin": float(full_info["boundary_margin"]),
                "no_facet_ball_score_margin": float(
                    nofacet_info["ball_score_margin"]
                ),
                "no_facet_boundary_margin": float(nofacet_info["boundary_margin"]),
            }
        )
    return rankings, traces, dict(seconds)


__all__ = [
    "build_rankings",
    "build_units_queries",
    "place_protected",
    "place_unprotected",
    "summarize_eligibility",
]
