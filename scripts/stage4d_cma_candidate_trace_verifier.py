"""Independent strict verifier for Stage4D-CMA Gold-free Channel A traces."""

from __future__ import annotations

import math
import hashlib
from collections import defaultdict
from typing import Any, Iterable

import numpy as np

from stage4b_u1_goldfree_retrieval import (
    build_balls,
    content_tokens,
    dot,
    enrich_balls_goldfree,
    normalize_matrix,
    select_facet_edges_goldfree,
)


SCHEMA_VERSION = "stage4d_cma_v1"
Q25_FLOOR = 0.1957079917192459
NOT_AVAILABLE_KEYS = {
    "bridge_entity_overlap",
    "cross_ball_support_count",
    "entity_new_coverage",
    "independent_facet_support_count",
    "path_length",
    "path_position",
    "path_support_strength",
    "support_source_entropy",
}

QUERY_KEYS = {
    "candidate_count",
    "dataset",
    "dense_topk_unit_ids",
    "effective_k",
    "eligible_candidate_unit_ids",
    "original_u1_score",
    "planned_insert_budget",
    "protect_n",
    "q25_inserted_unit_ids",
    "q25_topk_unit_ids",
    "query_id",
    "sample_id",
}

CANDIDATE_KEYS = {
    "candidate_budget_region",
    "candidate_covered_query_facet_count",
    "candidate_displaced_score_margin",
    "candidate_displaced_similarity",
    "candidate_novel_query_facet_count",
    "candidate_proposed_insert_position",
    "candidate_rank_in_eligible_slice",
    "candidate_rank_percentile",
    "candidate_source_type",
    "candidate_unit_id",
    "dataset",
    "dense_rank_in_full_candidate_pool",
    "dense_rank_percentile",
    "dense_score",
    "displaced_unit_dense_score",
    "displaced_unit_id",
    "displaced_unit_rank",
    "effective_k",
    "eligible_peer_count",
    "facet_score",
    "has_displaced_unit",
    "is_in_original_q25_insert_set",
    "max_similarity_to_eligible_peers",
    "max_similarity_to_protected_top10",
    "mean_similarity_to_eligible_peers",
    "mean_similarity_to_protected_top10",
    "planned_insert_budget",
    "protect_n",
    "q25_floor_margin",
    "q25_score",
    "query_id",
    "rank_disagreement",
    "sample_id",
    "seed_candidate_similarity",
    "source_ball_boundary_fraction",
    "source_ball_compactness",
    "source_ball_id",
    "source_ball_radius",
    "source_ball_score",
    "source_ball_size",
    "source_diversity",
    "source_edge_id",
    "source_facet_term_count",
    "source_new_term_count",
    "source_redundancy",
    "source_shared_term_count",
    "source_units_per_new_term",
    "supporting_ball_count",
    "supporting_hyperedge_count",
    "supporting_seed_count",
}

INTEGER_FIELDS = {
    "candidate_covered_query_facet_count",
    "candidate_novel_query_facet_count",
    "candidate_rank_in_eligible_slice",
    "dense_rank_in_full_candidate_pool",
    "displaced_unit_rank",
    "effective_k",
    "eligible_peer_count",
    "has_displaced_unit",
    "is_in_original_q25_insert_set",
    "planned_insert_budget",
    "protect_n",
    "source_ball_size",
    "source_facet_term_count",
    "source_new_term_count",
    "source_shared_term_count",
    "supporting_ball_count",
    "supporting_hyperedge_count",
    "supporting_seed_count",
}

FLOAT_FIELDS = CANDIDATE_KEYS - INTEGER_FIELDS - {
    "candidate_budget_region",
    "candidate_proposed_insert_position",
    "candidate_source_type",
    "candidate_unit_id",
    "dataset",
    "displaced_unit_id",
    "query_id",
    "sample_id",
    "source_ball_id",
    "source_edge_id",
}

FORBIDDEN_EXACT = {
    "candidate_is_gold",
    "dense_cr20",
    "dense_er20",
    "delta_loo_no_backfill_cr",
    "delta_loo_no_backfill_er",
    "delta_loo_with_backfill_cr",
    "delta_loo_with_backfill_er",
    "delta_standardized_single_cr",
    "delta_standardized_single_er",
    "final_cr20",
    "final_er20",
    "gold_map",
    "marginal_label",
    "q25_cr20",
    "q25_er20",
    "question_type",
    "reservation",
    "stage3b",
    "supporting_fact_identity",
    "trigger_u1",
}


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a native non-empty string")
    return value


def _integer(value: Any, label: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be a JSON integer")
    if value < minimum:
        raise ValueError(f"{label} must be >= {minimum}")
    return value


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a JSON number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def _id_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a JSON array")
    result = [_string(item, f"{label}[]") for item in value]
    if len(result) != len(set(result)):
        raise ValueError(f"{label} contains duplicate IDs")
    return result


def _scan_forbidden(value: Any, location: str = "root") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = _string(key, f"{location}.key")
            lowered = key_text.lower()
            if lowered in FORBIDDEN_EXACT or "gold_map" in lowered:
                raise ValueError(f"Forbidden Channel A key: {location}.{key_text}")
            _scan_forbidden(item, f"{location}.{key_text}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _scan_forbidden(item, f"{location}[{index}]")
    elif isinstance(value, str):
        lowered = value.lower().replace("\\", "/")
        if "/reservation" in lowered or "/stage3b" in lowered or "gold_map" in lowered:
            raise ValueError(f"Forbidden Channel A path/value at {location}")


def _reconstruct(
    dense_ids: list[str], inserted_ids: Iterable[str], protect_n: int, effective_k: int
) -> list[str]:
    result = list(dense_ids[:protect_n])
    seen = set(result)
    for unit_id in inserted_ids:
        if unit_id not in seen and len(result) < effective_k:
            result.append(unit_id)
            seen.add(unit_id)
    for unit_id in dense_ids:
        if len(result) >= effective_k:
            break
        if unit_id not in seen:
            result.append(unit_id)
            seen.add(unit_id)
    return result


def verify_channel_a_traces(
    query_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Validate exact schema, identity, complete-pool and reconstruction contracts."""

    _scan_forbidden(query_rows, "query_trace")
    _scan_forbidden(candidate_rows, "candidate_trace")
    _scan_forbidden(manifest, "manifest")
    if not isinstance(query_rows, list) or not query_rows:
        raise ValueError("query trace must be a non-empty list")
    if not isinstance(candidate_rows, list):
        raise ValueError("candidate trace must be a list")
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be an object")

    queries: dict[str, dict[str, Any]] = {}
    for row_index, row in enumerate(query_rows):
        if not isinstance(row, dict) or set(row) != QUERY_KEYS:
            raise ValueError(f"query[{row_index}] key contract differs")
        query_id = _string(row["query_id"], f"query[{row_index}].query_id")
        dataset = _string(row["dataset"], f"{query_id}.dataset")
        sample_id = _string(row["sample_id"], f"{query_id}.sample_id")
        if query_id != f"{dataset}::{sample_id}" or query_id in queries:
            raise ValueError(f"{query_id}: invalid or duplicate query identity")
        dense = _id_list(row["dense_topk_unit_ids"], f"{query_id}.dense")
        eligible = _id_list(
            row["eligible_candidate_unit_ids"], f"{query_id}.eligible"
        )
        inserted = _id_list(row["q25_inserted_unit_ids"], f"{query_id}.inserted")
        q25 = _id_list(row["q25_topk_unit_ids"], f"{query_id}.q25")
        candidate_count = _integer(row["candidate_count"], f"{query_id}.count")
        effective_k = _integer(row["effective_k"], f"{query_id}.effective_k", minimum=1)
        protect_n = _integer(row["protect_n"], f"{query_id}.protect_n")
        budget = _integer(row["planned_insert_budget"], f"{query_id}.budget")
        if len(dense) != effective_k or len(q25) != effective_k:
            raise ValueError(f"{query_id}: effective-K ranking length differs")
        if candidate_count != len(eligible):
            raise ValueError(f"{query_id}: complete candidate count differs")
        if protect_n > effective_k or budget > effective_k - protect_n:
            raise ValueError(f"{query_id}: invalid protection/budget")
        expected_inserted = eligible[: min(budget, len(eligible))]
        if inserted != expected_inserted:
            raise ValueError(f"{query_id}: original insert prefix differs")
        if q25 != _reconstruct(dense, inserted, protect_n, effective_k):
            raise ValueError(f"{query_id}: q25 reconstruction differs")
        if row["original_u1_score"] is not None:
            _number(row["original_u1_score"], f"{query_id}.original_u1_score")
        queries[query_id] = row

    by_query: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen_pairs: set[tuple[str, str]] = set()
    for row_index, row in enumerate(candidate_rows):
        if not isinstance(row, dict) or set(row) != CANDIDATE_KEYS:
            raise ValueError(f"candidate[{row_index}] key contract differs")
        query_id = _string(row["query_id"], f"candidate[{row_index}].query_id")
        unit_id = _string(
            row["candidate_unit_id"], f"candidate[{row_index}].candidate_unit_id"
        )
        if query_id not in queries or (query_id, unit_id) in seen_pairs:
            raise ValueError(f"{query_id}:{unit_id}: unknown query or duplicate row")
        seen_pairs.add((query_id, unit_id))
        query = queries[query_id]
        for key in ("dataset", "sample_id"):
            if _string(row[key], f"{query_id}:{unit_id}.{key}") != query[key]:
                raise ValueError(f"{query_id}:{unit_id}: row identity differs")
        for key in ("source_ball_id", "source_edge_id"):
            _string(row[key], f"{query_id}:{unit_id}.{key}")
        if row["candidate_source_type"] != "Q25_EXPANDED_BALL":
            raise ValueError(f"{query_id}:{unit_id}: source type differs")
        for key in INTEGER_FIELDS:
            _integer(row[key], f"{query_id}:{unit_id}.{key}")
        position = row["candidate_proposed_insert_position"]
        if position is not None:
            _integer(position, f"{query_id}:{unit_id}.candidate_proposed_insert_position", minimum=1)
        for key in FLOAT_FIELDS:
            _number(row[key], f"{query_id}:{unit_id}.{key}")
        if row["has_displaced_unit"] not in {0, 1}:
            raise ValueError(f"{query_id}:{unit_id}: has_displaced_unit must be 0/1")
        if row["is_in_original_q25_insert_set"] not in {0, 1}:
            raise ValueError(f"{query_id}:{unit_id}: insert flag must be 0/1")
        displaced_id = row["displaced_unit_id"]
        if row["has_displaced_unit"]:
            _string(displaced_id, f"{query_id}:{unit_id}.displaced_unit_id")
            if row["displaced_unit_rank"] < 1:
                raise ValueError(f"{query_id}:{unit_id}: displaced rank must be positive")
        elif displaced_id is not None or any(
            row[key] != 0 and row[key] != 0.0
            for key in (
                "displaced_unit_rank",
                "displaced_unit_dense_score",
                "candidate_displaced_score_margin",
                "candidate_displaced_similarity",
            )
        ):
            raise ValueError(f"{query_id}:{unit_id}: zero-displacement contract differs")
        by_query[query_id].append(row)

    original_rows = 0
    beyond_rows = 0
    for query_id, query in queries.items():
        rows = by_query.get(query_id, [])
        eligible = query["eligible_candidate_unit_ids"]
        rows.sort(key=lambda row: row["candidate_rank_in_eligible_slice"])
        if [row["candidate_rank_in_eligible_slice"] for row in rows] != list(
            range(1, len(eligible) + 1)
        ):
            raise ValueError(f"{query_id}: candidate ranks are not contiguous")
        if [row["candidate_unit_id"] for row in rows] != eligible:
            raise ValueError(f"{query_id}: candidate row order/IDs differ")
        for rank, row in enumerate(rows, start=1):
            expected_in = int(rank <= min(query["planned_insert_budget"], len(rows)))
            expected_region = (
                "ORIGINAL_INSERT_SET" if expected_in else "BEYOND_ORIGINAL_BUDGET"
            )
            if row["candidate_budget_region"] != expected_region:
                raise ValueError(f"{query_id}: budget region differs")
            if row["is_in_original_q25_insert_set"] != expected_in:
                raise ValueError(f"{query_id}: original insert flag differs")
            expected_position = query["protect_n"] + rank if expected_in else None
            if row["candidate_proposed_insert_position"] != expected_position:
                raise ValueError(f"{query_id}: proposed insert position differs")
            if row["effective_k"] != query["effective_k"] or row["protect_n"] != query["protect_n"]:
                raise ValueError(f"{query_id}: query/candidate scalar binding differs")
            if row["planned_insert_budget"] != query["planned_insert_budget"]:
                raise ValueError(f"{query_id}: candidate budget binding differs")
            if row["supporting_ball_count"] != 1 or row["supporting_hyperedge_count"] != 1:
                raise ValueError(f"{query_id}: terminal-ball support count differs")
            if row["q25_score"] != row["dense_score"]:
                raise ValueError(f"{query_id}: q25/dense semantic equality differs")
            if row["q25_floor_margin"] != row["dense_score"] - Q25_FLOOR:
                raise ValueError(f"{query_id}: q25 floor margin differs")
            expected_percentile = (rank - 1) / max(len(rows) - 1, 1)
            if row["candidate_rank_percentile"] != expected_percentile:
                raise ValueError(f"{query_id}: candidate rank percentile differs")
            if row["rank_disagreement"] != row["dense_rank_percentile"] - expected_percentile:
                raise ValueError(f"{query_id}: rank disagreement differs")
            if expected_in:
                original_rows += 1
            else:
                beyond_rows += 1

    if manifest.get("candidate_schema_version") != SCHEMA_VERSION:
        raise ValueError("manifest schema version differs")
    if manifest.get("channel") != "A_GOLD_FREE":
        raise ValueError("manifest channel differs")
    if manifest.get("status") != "CANDIDATE_TRACE_BUILT_PENDING_VERIFICATION":
        raise ValueError("manifest status differs")
    if manifest.get("queries") != len(query_rows) or manifest.get("candidate_rows") != len(candidate_rows):
        raise ValueError("manifest row counts differ")
    expected_query_digest = hashlib.sha256(
        "\n".join(row["query_id"] for row in query_rows).encode("utf-8")
    ).hexdigest().upper()
    if manifest.get("query_id_sha256") != expected_query_digest:
        raise ValueError("manifest query identity digest differs")
    unavailable = manifest.get("not_available")
    if not isinstance(unavailable, dict) or set(unavailable) != NOT_AVAILABLE_KEYS:
        raise ValueError("manifest NOT_AVAILABLE declaration missing")
    for key, entry in unavailable.items():
        _string(key, "not_available key")
        if not isinstance(entry, dict) or entry.get("status") != "NOT_AVAILABLE":
            raise ValueError("manifest NOT_AVAILABLE status differs")
        _string(entry.get("reason"), f"not_available.{key}.reason")

    return {
        "beyond_original_budget_rows": beyond_rows,
        "candidate_rows": len(candidate_rows),
        "original_insert_set_rows": original_rows,
        "queries": len(query_rows),
        "status": "CHANNEL_A_TRACE_VERIFIED",
    }


def _tokens(unit: dict[str, Any]) -> set[str]:
    return content_tokens(str(unit.get("title", ""))) | content_tokens(
        str(unit.get("text", ""))
    )


def verify_channel_a_reconstruction(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
    config: Any,
    query_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Independently rebuild candidate availability, rankings and numeric features."""

    verify_channel_a_traces(query_rows, candidate_rows, manifest)
    unit_embeddings = normalize_matrix(np.asarray(unit_embeddings, dtype="float32"))
    query_embeddings = normalize_matrix(np.asarray(query_embeddings, dtype="float32"))
    if unit_embeddings.ndim != 2 or query_embeddings.ndim != 2:
        raise ValueError("reconstruction embeddings must be matrices")
    if unit_embeddings.shape[0] != len(units) or query_embeddings.shape[0] != len(queries):
        raise ValueError("reconstruction embedding row counts differ")
    if unit_embeddings.shape[1] != query_embeddings.shape[1]:
        raise ValueError("reconstruction embedding dimensions differ")
    if not np.isfinite(unit_embeddings).all() or not np.isfinite(query_embeddings).all():
        raise ValueError("reconstruction embeddings must be finite")

    query_trace = {row["query_id"]: row for row in query_rows}
    candidates_by_query: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in candidate_rows:
        candidates_by_query[row["query_id"]].append(row)
    unit_index = {
        _string(row.get("unit_id"), "unit.unit_id"): index
        for index, row in enumerate(units)
    }
    if len(unit_index) != len(units):
        raise ValueError("reconstruction unit IDs are duplicated")
    indices_by_query: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(units):
        indices_by_query[_string(row.get("query_id"), "unit.query_id")].append(index)

    checked_candidates = 0
    for query_index, query in enumerate(queries):
        query_id = _string(query.get("query_id"), "query.query_id")
        if query_id not in query_trace:
            raise ValueError(f"{query_id}: missing reconstructed query trace")
        observed_query = query_trace[query_id]
        candidate_indices = indices_by_query[query_id]
        query_embedding = query_embeddings[query_index]
        dense_full = [
            {
                "index": index,
                "score": dot(query_embedding, unit_embeddings[index]),
                "unit_id": units[index]["unit_id"],
            }
            for index in candidate_indices
        ]
        dense_full.sort(key=lambda row: (-row["score"], row["unit_id"]))
        k = min(config.max_k, len(dense_full))
        protect_n = min(config.protect_n, k)
        budget = min(config.insert_budget, k - protect_n)
        dense = [row["unit_id"] for row in dense_full[:k]]
        dense_scores = {row["unit_id"]: float(row["score"]) for row in dense_full}
        dense_ranks = {
            row["unit_id"]: rank for rank, row in enumerate(dense_full, start=1)
        }

        balls = build_balls(query_id, candidate_indices, unit_embeddings, config)
        enrich_balls_goldfree(balls, units)
        selected_edges, _ = select_facet_edges_goldfree(
            query, query_embedding, balls, config
        )
        balls_by_id = {ball["ball_id"]: ball for ball in balls}
        selected_by_ball = {
            edge["accepted_ball_ids"][0]: edge for edge in selected_edges
        }
        expanded: list[dict[str, Any]] = []
        for ball_id, edge in selected_by_ball.items():
            ball = balls_by_id[ball_id]
            for index in ball["indices"]:
                unit_id = units[index]["unit_id"]
                dense_score = dot(query_embedding, unit_embeddings[index])
                expanded.append(
                    {
                        "ball": ball,
                        "dense_score": dense_score,
                        "edge": edge,
                        "index": index,
                        "q25_score": dense_score
                        + config.w_facet_unit_bonus * float(edge["facet_score"]),
                        "unit_id": unit_id,
                    }
                )
        expanded.sort(key=lambda row: (-row["q25_score"], row["unit_id"]))
        protected_set = set(dense[:protect_n])
        eligible = [
            row
            for row in expanded
            if row["dense_score"] >= config.q25_floor
            and row["unit_id"] not in protected_set
        ]
        eligible_ids = [row["unit_id"] for row in eligible]
        inserted = eligible_ids[: min(budget, len(eligible_ids))]
        q25 = _reconstruct(dense, inserted, protect_n, k)
        if observed_query["dense_topk_unit_ids"] != dense:
            raise ValueError(f"{query_id}: independent Dense reconstruction differs")
        if observed_query["eligible_candidate_unit_ids"] != eligible_ids:
            raise ValueError(f"{query_id}: independent complete E_q differs")
        if observed_query["q25_inserted_unit_ids"] != inserted:
            raise ValueError(f"{query_id}: independent insert prefix differs")
        if observed_query["q25_topk_unit_ids"] != q25:
            raise ValueError(f"{query_id}: independent q25 reconstruction differs")

        seed_balls = [
            ball
            for _, ball in sorted(
                ((dot(query_embedding, ball["center"]), ball) for ball in balls),
                key=lambda item: (-item[0], item[1]["ball_id"]),
            )[: config.seed_balls]
        ]
        protected_indices = [unit_index[unit_id] for unit_id in dense[:protect_n]]
        protected_embeddings = unit_embeddings[protected_indices]
        query_terms = content_tokens(str(query["question"]))
        protected_facets: set[str] = set()
        for index in protected_indices:
            protected_facets.update(_tokens(units[index]) & query_terms)
        eligible_indices = [int(row["index"]) for row in eligible]
        observed_candidates = sorted(
            candidates_by_query.get(query_id, []),
            key=lambda row: row["candidate_rank_in_eligible_slice"],
        )
        if len(observed_candidates) != len(eligible):
            raise ValueError(f"{query_id}: independent candidate row count differs")

        for rank, (source, observed) in enumerate(
            zip(eligible, observed_candidates, strict=True), start=1
        ):
            unit_id = source["unit_id"]
            index = int(source["index"])
            ball = source["ball"]
            edge = source["edge"]
            embedding = unit_embeddings[index]
            protected_sims = [dot(embedding, value) for value in protected_embeddings]
            peer_sims = [
                dot(embedding, unit_embeddings[peer])
                for peer in eligible_indices
                if peer != index
            ]
            seed_sims = [dot(embedding, ball_value["center"]) for ball_value in seed_balls]
            facets = _tokens(units[index]) & query_terms
            standardized = _reconstruct(dense, [unit_id], protect_n, k)
            displaced = list(set(dense) - set(standardized))
            displaced_id = displaced[0] if displaced else None
            if displaced_id is None:
                displacement = (0, 0.0, 0.0, 0.0)
            else:
                displacement = (
                    dense.index(displaced_id) + 1,
                    dense_scores[displaced_id],
                    float(source["dense_score"]) - dense_scores[displaced_id],
                    dot(embedding, unit_embeddings[unit_index[displaced_id]]),
                )
            candidate_percentile = (rank - 1) / max(len(eligible) - 1, 1)
            dense_percentile = (dense_ranks[unit_id] - 1) / max(
                len(candidate_indices) - 1, 1
            )
            expected: dict[str, Any] = {
                "candidate_covered_query_facet_count": len(facets & protected_facets),
                "candidate_displaced_score_margin": displacement[2],
                "candidate_displaced_similarity": displacement[3],
                "candidate_novel_query_facet_count": len(facets - protected_facets),
                "candidate_rank_percentile": candidate_percentile,
                "candidate_unit_id": unit_id,
                "dense_rank_in_full_candidate_pool": dense_ranks[unit_id],
                "dense_rank_percentile": dense_percentile,
                "dense_score": float(source["dense_score"]),
                "displaced_unit_dense_score": displacement[1],
                "displaced_unit_id": displaced_id,
                "displaced_unit_rank": displacement[0],
                "eligible_peer_count": len(peer_sims),
                "facet_score": float(edge["facet_score"]),
                "has_displaced_unit": int(displaced_id is not None),
                "max_similarity_to_eligible_peers": max(peer_sims) if peer_sims else 0.0,
                "max_similarity_to_protected_top10": max(protected_sims),
                "mean_similarity_to_eligible_peers": float(np.mean(peer_sims)) if peer_sims else 0.0,
                "mean_similarity_to_protected_top10": float(np.mean(protected_sims)),
                "q25_floor_margin": float(source["dense_score"]) - config.q25_floor,
                "q25_score": float(source["q25_score"]),
                "rank_disagreement": dense_percentile - candidate_percentile,
                "seed_candidate_similarity": max(seed_sims) if seed_sims else 0.0,
                "source_ball_boundary_fraction": float(ball["boundary_count"]) / float(ball["size"]),
                "source_ball_compactness": float(ball["compactness"]),
                "source_ball_id": ball["ball_id"],
                "source_ball_radius": float(ball["radius"]),
                "source_ball_score": float(edge["ball_score"]),
                "source_ball_size": int(ball["size"]),
                "source_diversity": float(edge["diversity"]),
                "source_edge_id": edge["edge_id"],
                "source_facet_term_count": len(edge["facet_terms"]),
                "source_new_term_count": len(edge["new_terms"]),
                "source_redundancy": float(edge["redundancy"]),
                "source_shared_term_count": len(edge["shared_terms"]),
                "source_units_per_new_term": float(edge["units_per_new_term"]),
                "supporting_seed_count": sum(
                    similarity >= config.min_seed_similarity
                    for similarity in seed_sims
                ),
            }
            for field, value in expected.items():
                if observed[field] != value:
                    raise ValueError(
                        f"{query_id}:{unit_id}: independent {field} differs"
                    )
            checked_candidates += 1
    if len(query_trace) != len(queries) or checked_candidates != len(candidate_rows):
        raise ValueError("independent reconstruction coverage differs")
    return {
        "candidate_rows": checked_candidates,
        "queries": len(queries),
        "status": "CHANNEL_A_INDEPENDENT_RECONSTRUCTION_VERIFIED",
    }
