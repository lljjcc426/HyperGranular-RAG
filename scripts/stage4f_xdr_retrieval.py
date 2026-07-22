"""Frozen Gold-free Dense and static-q25 retrieval for Stage4F.

The scientific operations are copied from the accepted Stage4E retrieval path,
but this module has no U1/controller dependency or invocation.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np


TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "is", "it",
    "of", "on", "or", "that", "the", "to", "was", "were", "who", "what", "when", "where",
    "which", "with",
}


def assert_finite(value: float, label: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


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
    q25_floor: float = 0.1957079917192459
    protect_n: int = 10
    insert_budget: int = 4
    max_k: int = 20

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def content_tokens(text: str) -> set[str]:
    return {
        token for token in TOKEN_RE.findall(text.lower())
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
    distances = [
        assert_finite(1.0 - dot(embeddings[index], center), "ball distance")
        for index in indices
    ]
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


def enrich_balls_goldfree(
    balls: list[dict[str, Any]], units: list[dict[str, Any]]
) -> None:
    for ball in balls:
        terms: set[str] = set()
        for index in ball["indices"]:
            unit = units[index]
            terms.update(content_tokens(str(unit.get("title", ""))))
            terms.update(content_tokens(str(unit.get("text", ""))))
        ball["all_terms"] = terms


def decision_from_balls(
    query_embedding: np.ndarray, balls: list[dict[str, Any]]
) -> dict[str, Any]:
    if not balls:
        raise ValueError("Cannot make a decision from an empty ball list")
    scored = sorted(
        ((dot(query_embedding, ball["center"]), ball) for ball in balls),
        key=lambda item: (-item[0], item[1]["ball_id"]),
    )
    top_score = assert_finite(scored[0][0], "top ball score")
    second_score = assert_finite(
        scored[1][0] if len(scored) > 1 else -1.0, "second ball score"
    )
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
            if config.max_candidate_ball_size > 0 else 0.0
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
                "accepted_ball_ids": [ball["ball_id"]],
                "facet_score": facet_score,
                "new_terms": sorted(new_terms),
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
        "selected_edge_count": len(selected),
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
        for edge in selected for ball_id in edge["accepted_ball_ids"]
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
            }
            previous = candidates_by_unit.get(unit_id)
            if previous is None or row["rerank_score"] > previous["rerank_score"]:
                candidates_by_unit[unit_id] = row
    candidates = sorted(
        candidates_by_unit.values(), key=lambda row: (-row["rerank_score"], row["unit_id"])
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
            query, query_embedding, candidate_indices, units, unit_embeddings, config
        )
        filtered = [row for row in expanded if row["score"] >= config.q25_floor]
        q25, inserted_ids = protected_rerank_goldfree(
            dense, filtered, config.protect_n, config.insert_budget, config.max_k
        )
        rows.append(
            {
                "query_id": query_id,
                "dataset": str(query["dataset"]),
                "sample_id": str(query["sample_id"]),
                "selected_edge_count": len(selected),
                "planned_insert_count": len(inserted_ids),
                "dense_top20_unit_ids": [str(row["unit_id"]) for row in dense],
                "q25_top20_unit_ids": [str(row["unit_id"]) for row in q25],
                "q25_inserted_unit_ids": inserted_ids,
                "ball_score_margin": assert_finite(info["ball_score_margin"], "ball score margin"),
                "boundary_margin": assert_finite(info["boundary_margin"], "boundary margin"),
            }
        )
    return rows

