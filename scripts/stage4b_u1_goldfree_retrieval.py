"""Gold-free granular-ball, hyperedge, and budget-allocation logic for U1."""

from __future__ import annotations

import bisect
import hashlib
import math
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from stage4b_u1_common import (
    BUDGET_FRACTION,
    INSERT_BUDGET,
    MAX_K,
    PROTECT_N,
    Q25_FLOOR,
    assert_finite,
    tie_hash,
)


TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "is", "it",
    "of", "on", "or", "that", "the", "to", "was", "were", "who", "what", "when", "where",
    "which", "with",
}


@dataclass(frozen=True)
class RetrievalConfig:
    min_size: int = 2
    max_size: int = 3
    radius_threshold: float = 0.78
    max_depth: int = 6
    boundary_width: float = 0.2
    top_center_terms: int = 8
    seed_balls: int = 2
    top_facet_edges: int = 2
    max_expanded_balls: int = 2
    min_new_terms: int = 1
    min_facet_score: float = 0.10
    max_candidate_ball_size: int = 8
    min_ball_score: float = 0.12
    min_seed_similarity: float = 0.05
    max_units_per_new_term: float = 6.0
    max_redundancy: float = 0.90
    w_new: float = 0.45
    w_total: float = 0.20
    w_ball: float = 0.20
    w_diversity: float = 0.15
    w_redundancy: float = 0.20
    w_size: float = 0.05
    w_facet_unit_bonus: float = 0.0
    q25_floor: float = Q25_FLOOR
    protect_n: int = PROTECT_N
    insert_budget: int = INSERT_BUDGET
    max_k: int = MAX_K
    budget_fraction: float = BUDGET_FRACTION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def content_tokens(text: str) -> set[str]:
    return {
        token
        for token in TOKEN_RE.findall(text.lower())
        if len(token) > 2 and token not in STOPWORDS
    }


def normalize_matrix(matrix: np.ndarray) -> np.ndarray:
    matrix = np.asarray(matrix, dtype="float32")
    if matrix.ndim != 2 or not np.isfinite(matrix).all():
        raise ValueError("Embedding matrix must be finite and two-dimensional")
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    result = (matrix / norms).astype("float32")
    if not np.isfinite(result).all():
        raise ValueError("Normalized embedding matrix is not finite")
    return result


def normalize_vector(vector: np.ndarray) -> np.ndarray:
    vector = np.asarray(vector, dtype="float32")
    norm = float(np.linalg.norm(vector))
    if not math.isfinite(norm):
        raise ValueError("Vector norm is not finite")
    return vector if norm == 0.0 else (vector / norm).astype("float32")


def dot(left: np.ndarray, right: np.ndarray) -> float:
    return assert_finite(float(np.dot(left, right)), "dot product")


def centroid(indices: list[int], embeddings: np.ndarray) -> np.ndarray:
    if not indices:
        raise ValueError("Cannot compute an empty granular-ball centroid")
    return normalize_vector(np.mean(embeddings[indices], axis=0).astype("float32"))


def describe_ball(
    ball_id: str,
    query_id: str,
    indices: list[int],
    center: np.ndarray,
    embeddings: np.ndarray,
    depth: int,
    boundary_width: float,
) -> dict[str, Any]:
    distances = [assert_finite(1.0 - dot(embeddings[index], center), "ball distance") for index in indices]
    radius = max(distances)
    mean_distance = sum(distances) / len(distances)
    threshold = radius * (1.0 - boundary_width)
    return {
        "ball_id": ball_id,
        "query_id": query_id,
        "indices": indices,
        "center": center,
        "size": len(indices),
        "radius": assert_finite(radius, "ball radius"),
        "mean_distance": assert_finite(mean_distance, "mean ball distance"),
        "compactness": assert_finite(1.0 - mean_distance, "ball compactness"),
        "boundary_count": sum(
            1 for distance in distances if radius > 0 and distance >= threshold
        ),
        "depth": depth,
    }


def split_ball(
    indices: list[int], embeddings: np.ndarray, center: np.ndarray
) -> tuple[list[int], list[int]]:
    if len(indices) < 2:
        return indices, []
    seed_a = max(indices, key=lambda index: 1.0 - dot(embeddings[index], center))
    seed_b = min(indices, key=lambda index: dot(embeddings[index], embeddings[seed_a]))
    if seed_a == seed_b:
        midpoint = len(indices) // 2
        return indices[:midpoint], indices[midpoint:]
    left: list[int] = []
    right: list[int] = []
    for index in indices:
        if dot(embeddings[index], embeddings[seed_a]) >= dot(
            embeddings[index], embeddings[seed_b]
        ):
            left.append(index)
        else:
            right.append(index)
    if not left or not right:
        midpoint = len(indices) // 2
        return indices[:midpoint], indices[midpoint:]
    return left, right


def build_balls(
    query_id: str,
    indices: list[int],
    embeddings: np.ndarray,
    config: RetrievalConfig,
) -> list[dict[str, Any]]:
    if not indices:
        raise ValueError(f"{query_id}: no candidate units")
    balls: list[dict[str, Any]] = []
    serial = 0

    def recurse(current: list[int], depth: int) -> None:
        nonlocal serial
        center = centroid(current, embeddings)
        ball = describe_ball(
            f"{query_id}::dball{serial}",
            query_id,
            current,
            center,
            embeddings,
            depth,
            config.boundary_width,
        )
        should_split = (
            depth < config.max_depth
            and len(current) >= 2 * config.min_size
            and (len(current) > config.max_size or ball["radius"] > config.radius_threshold)
        )
        if should_split:
            left, right = split_ball(current, embeddings, center)
            if len(left) >= config.min_size and len(right) >= config.min_size:
                recurse(left, depth + 1)
                recurse(right, depth + 1)
                return
        serial += 1
        balls.append(ball)

    recurse(indices, 0)
    if not balls:
        raise ValueError(f"{query_id}: granular-ball construction returned no balls")
    return balls


def enrich_balls_goldfree(balls: list[dict[str, Any]], units: list[dict[str, Any]]) -> None:
    for ball in balls:
        terms: set[str] = set()
        for index in ball["indices"]:
            unit = units[index]
            terms.update(content_tokens(str(unit.get("title", ""))))
            terms.update(content_tokens(str(unit.get("text", ""))))
        ball["all_terms"] = terms


def decision_from_balls(query_embedding: np.ndarray, balls: list[dict[str, Any]]) -> dict[str, Any]:
    if not balls:
        raise ValueError("Cannot make a decision from an empty ball list")
    scored = sorted(
        ((dot(query_embedding, ball["center"]), ball) for ball in balls),
        key=lambda item: (-item[0], item[1]["ball_id"]),
    )
    top_score = assert_finite(scored[0][0], "top ball score")
    second_score = assert_finite(scored[1][0] if len(scored) > 1 else -1.0, "second ball score")
    top_ball = scored[0][1]
    top_distance = assert_finite(1.0 - top_score, "query-to-ball distance")
    top_radius = assert_finite(top_ball["radius"], "top ball radius")
    boundary_margin = (
        assert_finite(
            abs(top_radius - top_distance) / (top_radius + 1e-9),
            "boundary margin",
        )
        if top_radius > 0
        else 999.0
    )
    return {
        "scored_balls": scored,
        "top_ball_score": top_score,
        "ball_score_margin": assert_finite(top_score - second_score, "ball score margin"),
        "top_ball_radius": top_radius,
        "query_to_top_ball_distance": top_distance,
        "boundary_margin": boundary_margin,
    }


def select_facet_edges_goldfree(
    query: dict[str, Any],
    query_embedding: np.ndarray,
    balls: list[dict[str, Any]],
    config: RetrievalConfig,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    decision = decision_from_balls(query_embedding, balls)
    scored_balls = decision["scored_balls"]
    query_term_set = content_tokens(str(query["question"]))
    for ball in balls:
        ball["facet_terms"] = ball["all_terms"] & query_term_set
    seed_balls = [ball for _, ball in scored_balls[: config.seed_balls]]
    seed_ids = {ball["ball_id"] for ball in seed_balls}
    covered = set().union(*(ball["facet_terms"] for ball in seed_balls)) if seed_balls else set()
    seed_centers = [ball["center"] for ball in seed_balls]
    candidates: list[dict[str, Any]] = []
    reject_counts: Counter[str] = Counter()

    for score, ball in scored_balls:
        if ball["ball_id"] in seed_ids:
            continue
        new_terms = ball["facet_terms"] - covered
        shared_terms = ball["facet_terms"] & covered
        if len(new_terms) < config.min_new_terms:
            continue
        max_seed_similarity = max(
            (dot(ball["center"], center) for center in seed_centers), default=0.0
        )
        ball_size = len(ball["indices"])
        units_per_new_term = ball_size / max(len(new_terms), 1)
        redundancy = len(shared_terms) / max(len(ball["facet_terms"]), 1)
        if config.max_candidate_ball_size > 0 and ball_size > config.max_candidate_ball_size:
            reject_counts["gate_reject_size"] += 1
            continue
        if not (score >= config.min_ball_score or max_seed_similarity >= config.min_seed_similarity):
            reject_counts["gate_reject_anchor"] += 1
            continue
        if config.max_units_per_new_term > 0 and units_per_new_term > config.max_units_per_new_term:
            reject_counts["gate_reject_ratio"] += 1
            continue
        if redundancy > config.max_redundancy:
            reject_counts["gate_reject_redundancy"] += 1
            continue
        diversity = 1.0 - max_seed_similarity
        new_ratio = len(new_terms) / max(len(query_term_set), 1)
        total_ratio = len(ball["facet_terms"]) / max(len(query_term_set), 1)
        size_penalty = (
            ball_size / config.max_candidate_ball_size
            if config.max_candidate_ball_size > 0
            else 0.0
        )
        facet_score = assert_finite(
            config.w_new * new_ratio
            + config.w_total * total_ratio
            + config.w_ball * score
            + config.w_diversity * diversity
            - config.w_redundancy * redundancy
            - config.w_size * size_penalty,
            "facet score",
        )
        if facet_score < config.min_facet_score:
            reject_counts["gate_reject_score"] += 1
            continue
        candidates.append(
            {
                "edge_id": f"{query['query_id']}::dense_facet::{ball['ball_id']}",
                "query_id": query["query_id"],
                "accepted_ball_ids": [ball["ball_id"]],
                "new_terms": sorted(new_terms),
                "shared_terms": sorted(shared_terms),
                "facet_terms": sorted(ball["facet_terms"]),
                "ball_score": score,
                "facet_score": facet_score,
                "diversity": diversity,
                "redundancy": redundancy,
                "ball_size": ball_size,
                "units_per_new_term": units_per_new_term,
                "max_seed_similarity": max_seed_similarity,
            }
        )
    candidates.sort(key=lambda row: (-row["facet_score"], row["edge_id"]))
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    for candidate in candidates:
        ball_id = candidate["accepted_ball_ids"][0]
        if ball_id in selected_ids:
            continue
        if len(selected_ids) >= config.max_expanded_balls:
            break
        selected.append(candidate)
        selected_ids.add(ball_id)
        covered.update(candidate["new_terms"])
        if len(selected) >= config.top_facet_edges:
            break
    info = {
        **{key: value for key, value in decision.items() if key != "scored_balls"},
        "seed_ball_count": len(seed_ids),
        "expanded_ball_count": len(selected_ids),
        "selected_edge_count": len(selected),
        "query_facet_count": len(query_term_set),
        **{key: reject_counts[key] for key in sorted(reject_counts)},
    }
    return selected, info


def fixed_retrieve_goldfree(
    query_embedding: np.ndarray,
    candidate_indices: list[int],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    max_k: int,
) -> list[dict[str, Any]]:
    ranked = [
        {
            "unit_index": index,
            "unit_id": str(units[index]["unit_id"]),
            "score": dot(query_embedding, embeddings[index]),
        }
        for index in candidate_indices
    ]
    ranked.sort(key=lambda row: (-row["score"], row["unit_id"]))
    return ranked[:max_k]


def expansion_candidates_goldfree(
    query: dict[str, Any],
    query_embedding: np.ndarray,
    candidate_indices: list[int],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    config: RetrievalConfig,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    balls = build_balls(str(query["query_id"]), candidate_indices, embeddings, config)
    enrich_balls_goldfree(balls, units)
    selected, info = select_facet_edges_goldfree(query, query_embedding, balls, config)
    expanded_ball_ids = {
        ball_id for edge in selected for ball_id in edge["accepted_ball_ids"]
    }
    bonus_by_ball = {
        ball_id: edge["facet_score"]
        for edge in selected
        for ball_id in edge["accepted_ball_ids"]
    }
    candidates_by_unit: dict[str, dict[str, Any]] = {}
    for ball in balls:
        if ball["ball_id"] not in expanded_ball_ids:
            continue
        bonus = bonus_by_ball.get(ball["ball_id"], 0.0)
        for index in ball["indices"]:
            unit_id = str(units[index]["unit_id"])
            base_score = dot(query_embedding, embeddings[index])
            row = {
                "unit_index": index,
                "unit_id": unit_id,
                "score": base_score,
                "rerank_score": assert_finite(
                    base_score + config.w_facet_unit_bonus * bonus,
                    "candidate rerank score",
                ),
                "facet_bonus": bonus,
            }
            previous = candidates_by_unit.get(unit_id)
            if previous is None or row["rerank_score"] > previous["rerank_score"]:
                candidates_by_unit[unit_id] = row
    candidates = sorted(
        candidates_by_unit.values(),
        key=lambda row: (-row["rerank_score"], row["unit_id"]),
    )
    return candidates, selected, info


def protected_rerank_goldfree(
    dense_ranked: list[dict[str, Any]],
    expanded_ranked: list[dict[str, Any]],
    protect_n: int,
    insert_budget: int,
    max_k: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    protected = dense_ranked[:protect_n]
    seen = {row["unit_id"] for row in protected}
    inserted: list[dict[str, Any]] = []
    for row in expanded_ranked:
        if len(inserted) >= insert_budget:
            break
        if row["unit_id"] in seen:
            continue
        inserted.append(row)
        seen.add(row["unit_id"])
    ranked = protected + inserted
    for row in dense_ranked:
        if len(ranked) >= max_k:
            break
        if row["unit_id"] in seen:
            continue
        ranked.append(row)
        seen.add(row["unit_id"])
    for row in expanded_ranked:
        if len(ranked) >= max_k:
            break
        if row["unit_id"] in seen:
            continue
        ranked.append(row)
        seen.add(row["unit_id"])
    return ranked[:max_k], [str(row["unit_id"]) for row in inserted]


def build_query_decisions(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
    config: RetrievalConfig,
) -> list[dict[str, Any]]:
    if unit_embeddings.shape[0] != len(units) or query_embeddings.shape[0] != len(queries):
        raise ValueError("Embedding/corpus dimensions differ")
    indices_by_query: dict[str, list[int]] = defaultdict(list)
    for index, unit in enumerate(units):
        indices_by_query[str(unit["query_id"])].append(index)
    rows: list[dict[str, Any]] = []
    for query_index, query in enumerate(queries):
        query_id = str(query["query_id"])
        candidate_indices = indices_by_query.get(query_id, [])
        if len(candidate_indices) != int(query["num_candidate_units"]):
            raise ValueError(f"{query_id}: candidate count differs from query schema")
        query_embedding = query_embeddings[query_index]
        dense = fixed_retrieve_goldfree(
            query_embedding, candidate_indices, units, unit_embeddings, config.max_k
        )
        expanded, selected, info = expansion_candidates_goldfree(
            query,
            query_embedding,
            candidate_indices,
            units,
            unit_embeddings,
            config,
        )
        filtered = [row for row in expanded if row["score"] >= config.q25_floor]
        q25, inserted_ids = protected_rerank_goldfree(
            dense,
            filtered,
            config.protect_n,
            config.insert_budget,
            config.max_k,
        )
        planned = len(inserted_ids)
        feasible = int(len(selected) > 0 and planned > 0)
        rows.append(
            {
                "query_id": query_id,
                "dataset": str(query["dataset"]),
                "sample_id": str(query["sample_id"]),
                "ball_score_margin": assert_finite(info["ball_score_margin"], "ball score margin"),
                "boundary_margin": assert_finite(info["boundary_margin"], "boundary margin"),
                "selected_edge_count": len(selected),
                "planned_insert_count": planned,
                "feasible": feasible,
                "dense_top20_unit_ids": [str(row["unit_id"]) for row in dense],
                "q25_top20_unit_ids": [str(row["unit_id"]) for row in q25],
                "q25_inserted_unit_ids": inserted_ids,
            }
        )
    return rows


def ecdf_midrank(reference: list[float], value: float) -> float:
    if not reference:
        raise ValueError("ECDF reference is empty")
    value = assert_finite(value, "ECDF value")
    left = bisect.bisect_left(reference, value)
    right = bisect.bisect_right(reference, value)
    return assert_finite((left + 0.5 * (right - left)) / len(reference), "ECDF output")


def fit_ecdf_references(rows: list[dict[str, Any]]) -> dict[str, list[float]]:
    feasible = [row for row in rows if int(row["feasible"]) == 1]
    if not feasible:
        raise ValueError("No feasible queries for ECDF fitting")
    values = {
        "ball_score_margin": [float(row["ball_score_margin"]) for row in feasible],
        "boundary_margin": [float(row["boundary_margin"]) for row in feasible],
        "log1p_selected_edge_count": [math.log1p(int(row["selected_edge_count"])) for row in feasible],
        "log1p_planned_insert_count": [math.log1p(int(row["planned_insert_count"])) for row in feasible],
    }
    references: dict[str, list[float]] = {}
    for key, items in values.items():
        checked = [assert_finite(item, key) for item in items]
        references[key] = sorted(checked)
    return references


def validate_ecdf_references(references: dict[str, list[float]]) -> None:
    expected = {
        "ball_score_margin",
        "boundary_margin",
        "log1p_selected_edge_count",
        "log1p_planned_insert_count",
    }
    if set(references) != expected:
        raise ValueError("ECDF reference keys differ from the protocol")
    for key, items in references.items():
        if not items or items != sorted(items):
            raise ValueError(f"ECDF reference is empty or unsorted: {key}")
        for item in items:
            assert_finite(item, f"ECDF reference {key}")


def score_rows(
    rows: list[dict[str, Any]], references: dict[str, list[float]]
) -> None:
    validate_ecdf_references(references)
    for row in rows:
        row["tie_hash"] = tie_hash(str(row["query_id"]))
        if not int(row["feasible"]):
            row.update(
                {
                    "u_margin": None,
                    "u_boundary": None,
                    "r_edge": None,
                    "r_candidate": None,
                    "uncertainty": None,
                    "readiness": None,
                    "score": None,
                }
            )
            continue
        u_margin = 1.0 - ecdf_midrank(
            references["ball_score_margin"], float(row["ball_score_margin"])
        )
        u_boundary = 1.0 - ecdf_midrank(
            references["boundary_margin"], float(row["boundary_margin"])
        )
        r_edge = ecdf_midrank(
            references["log1p_selected_edge_count"],
            math.log1p(int(row["selected_edge_count"])),
        )
        r_candidate = ecdf_midrank(
            references["log1p_planned_insert_count"],
            math.log1p(int(row["planned_insert_count"])),
        )
        uncertainty = assert_finite((u_margin + u_boundary) / 2.0, "uncertainty")
        readiness = assert_finite(math.sqrt(r_edge * r_candidate), "readiness")
        score = assert_finite(uncertainty * readiness, "controller score")
        row.update(
            {
                "u_margin": u_margin,
                "u_boundary": u_boundary,
                "r_edge": r_edge,
                "r_candidate": r_candidate,
                "uncertainty": uncertainty,
                "readiness": readiness,
                "score": score,
            }
        )


def allocate_budget(
    rows: list[dict[str, Any]], budget_fraction: float = BUDGET_FRACTION
) -> dict[str, Any]:
    if budget_fraction != BUDGET_FRACTION:
        raise ValueError("Stage4B-U1 budget fraction must remain 0.60")
    feasible = [row for row in rows if int(row["feasible"]) == 1]
    if not feasible:
        raise ValueError("No feasible queries for budget allocation")
    ordered = sorted(feasible, key=lambda row: (-float(row["score"]), row["tie_hash"]))
    for row in rows:
        row["ordered_rank"] = None
    for rank, row in enumerate(ordered, start=1):
        row["ordered_rank"] = rank
    allquery_planned = sum(int(row["planned_insert_count"]) for row in feasible)
    budget_units = math.floor(allquery_planned * budget_fraction)
    if budget_units < 1:
        raise ValueError("Planned-insert budget is empty")
    cumulative = 0
    selected = 0
    for row in ordered:
        cost = int(row["planned_insert_count"])
        if cumulative + cost > budget_units:
            break
        cumulative += cost
        selected += 1
    if selected == 0:
        raise ValueError("No non-empty ordered prefix fits the planned-insert budget")
    selected_ids = {str(row["query_id"]) for row in ordered[:selected]}
    for row in rows:
        trigger = int(str(row["query_id"]) in selected_ids)
        row["trigger_u1"] = trigger
        row["final_top20_unit_ids"] = (
            list(row["q25_top20_unit_ids"])
            if trigger
            else list(row["dense_top20_unit_ids"])
        )
        row["final_inserted_unit_ids"] = (
            list(row["q25_inserted_unit_ids"]) if trigger else []
        )
    cutoff = ordered[selected - 1]
    return {
        "budget_fraction": budget_fraction,
        "n_feasible": len(feasible),
        "allquery_planned_inserts": allquery_planned,
        "budget_units": budget_units,
        "selected_queries": selected,
        "selected_planned_inserts": cumulative,
        "cutoff_score": float(cutoff["score"]),
        "cutoff_hash": str(cutoff["tie_hash"]),
        "score_direction": "descending",
        "selection_operator": "ordered_prefix_cumulative_cost_lte_budget",
    }
