"""Independent reconstruction of the frozen Stage5A BGE-native retrieval."""

from __future__ import annotations

import hashlib
import math
import re
from collections import defaultdict
from typing import Any

import numpy as np

from stage4h_cbe_retrieval import build_units_queries
from stage5a_bnh_common import (
    BASELINE_METHOD,
    CONFIRMATION_METHODS,
    development_method,
    require_native_string,
    validate_candidate_configs,
)


TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
STOPWORDS = {
    "about", "after", "also", "and", "are", "been", "before", "being",
    "between", "both", "but", "did", "does", "for", "from", "had", "has",
    "have", "how", "into", "its", "not", "that", "the", "their", "then",
    "there", "these", "they", "this", "those", "was", "were", "what", "when",
    "where", "which", "while", "who", "whose", "why", "will", "with",
}
TOP_K = 20
PROTECTED_PREFIX = 10
SEED_BALLS = 2
MAX_EXPANDED_BALLS = 4
MAX_DEPTH = 8
MIN_CHILD_FRACTION = 0.20
MIN_COMPACTNESS_GAIN = 1e-10
FACET_GATES = {
    "BROAD": {"query_score_ecdf": 0.35, "density_ecdf": 0.25},
    "STRICT": {"query_score_ecdf": 0.50, "density_ecdf": 0.50},
}


def _similarity(left: np.ndarray, right: np.ndarray) -> float:
    result = float(np.dot(left, right))
    if not math.isfinite(result):
        raise ValueError("independent reconstruction found non-finite similarity")
    return result


def _center(members: list[int], embeddings: np.ndarray) -> np.ndarray:
    value = np.mean(embeddings[members], axis=0, dtype="float64")
    norm = float(np.linalg.norm(value))
    if not math.isfinite(norm) or norm <= 0.0:
        value = np.asarray(embeddings[members[0]], dtype="float64")
        norm = float(np.linalg.norm(value))
    if not math.isfinite(norm) or norm <= 0.0:
        raise ValueError("independent ball center is degenerate")
    return np.asarray(value / norm, dtype="float64")


def _terms(value: str) -> set[str]:
    return {
        token
        for token in TOKEN_RE.findall(value.lower())
        if len(token) >= 3 and token not in STOPWORDS
    }


def _partition(
    ball_id: str,
    members: list[int],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
) -> tuple[list[int], list[int], float]:
    parent_center = _center(members, embeddings)
    first = min(
        members,
        key=lambda index: (
            _similarity(parent_center, embeddings[index]),
            units[index]["unit_id"],
        ),
    )
    second = min(
        (index for index in members if index != first),
        key=lambda index: (
            _similarity(embeddings[first], embeddings[index]),
            units[index]["unit_id"],
        ),
    )
    children: tuple[list[int], list[int]] = ([], [])
    for index in members:
        left = _similarity(embeddings[index], embeddings[first])
        right = _similarity(embeddings[index], embeddings[second])
        if left > right:
            children[0].append(index)
        elif right > left:
            children[1].append(index)
        else:
            side = hashlib.sha256(
                (ball_id + "\0" + units[index]["unit_id"]).encode("utf-8")
            ).digest()[0] & 1
            children[side].append(index)
    if not children[0] or not children[1]:
        ordered = sorted(members, key=lambda index: units[index]["unit_id"])
        midpoint = len(ordered) // 2
        children = (ordered[:midpoint], ordered[midpoint:])
    parent_compactness = float(
        np.mean(
            [
                _similarity(parent_center, embeddings[index])
                for index in members
            ]
        )
    )
    weighted = 0.0
    for child in children:
        child_center = _center(child, embeddings)
        weighted += len(child) * float(
            np.mean(
                [
                    _similarity(child_center, embeddings[index])
                    for index in child
                ]
            )
        )
    return children[0], children[1], weighted / len(members) - parent_compactness


def _leaf(
    ball_id: str,
    members: list[int],
    depth: int,
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    question_terms: set[str],
) -> dict[str, Any]:
    center = _center(members, embeddings)
    similarities = np.asarray(
        [_similarity(center, embeddings[index]) for index in members],
        dtype="float64",
    )
    facets: set[str] = set()
    for index in members:
        facets.update(
            question_terms
            & _terms(units[index]["title"] + " " + units[index]["text"])
        )
    return {
        "ball_id": ball_id,
        "center": center,
        "compactness": float(np.mean(similarities)),
        "depth": depth,
        "facets": tuple(sorted(facets)),
        "indices": list(members),
        "radius": float(np.max(1.0 - similarities)),
    }


def independent_balls(
    query: dict[str, Any],
    candidate_indices: list[int],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    leaf_size: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    pending = [(f"{query['query_id']}::ball", list(candidate_indices), 0)]
    leaves: list[dict[str, Any]] = []
    question_terms = _terms(query["question"])
    accepted = 0
    rejected_balance = 0
    rejected_gain = 0
    while pending:
        ball_id, members, depth = pending.pop()
        if len(members) <= leaf_size or depth >= MAX_DEPTH:
            leaves.append(
                _leaf(
                    ball_id,
                    members,
                    depth,
                    units,
                    embeddings,
                    question_terms,
                )
            )
            continue
        left, right, gain = _partition(ball_id, members, units, embeddings)
        if min(len(left), len(right)) / len(members) < MIN_CHILD_FRACTION:
            rejected_balance += 1
            leaves.append(
                _leaf(
                    ball_id,
                    members,
                    depth,
                    units,
                    embeddings,
                    question_terms,
                )
            )
        elif gain <= MIN_COMPACTNESS_GAIN:
            rejected_gain += 1
            leaves.append(
                _leaf(
                    ball_id,
                    members,
                    depth,
                    units,
                    embeddings,
                    question_terms,
                )
            )
        else:
            accepted += 1
            pending.append((ball_id + "R", right, depth + 1))
            pending.append((ball_id + "L", left, depth + 1))
    leaves.sort(key=lambda row: row["ball_id"])
    if sorted(index for row in leaves for index in row["indices"]) != sorted(
        candidate_indices
    ):
        raise ValueError("independent balls do not partition candidates")
    return leaves, {
        "accepted_split_count": accepted,
        "leaf_ball_count": len(leaves),
        "query_facet_count": len(question_terms),
        "rejected_balance_count": rejected_balance,
        "rejected_compactness_gain_count": rejected_gain,
    }


def _percentiles(values: list[float]) -> list[float]:
    if not values or any(not math.isfinite(value) for value in values):
        raise ValueError("independent ECDF values differ")
    ordered = sorted(values)
    return [
        sum(candidate <= value for candidate in ordered) / len(ordered)
        for value in values
    ]


def _add_statistics(
    balls: list[dict[str, Any]], query_embedding: np.ndarray
) -> None:
    query_scores = [
        _similarity(query_embedding, ball["center"]) for ball in balls
    ]
    radii = [float(ball["radius"]) for ball in balls]
    compactness = [float(ball["compactness"]) for ball in balls]
    densities = [
        len(ball["indices"]) / max(float(ball["radius"]), 1e-12)
        for ball in balls
    ]
    query_ecdf = _percentiles(query_scores)
    radius_ecdf = _percentiles(radii)
    compactness_ecdf = _percentiles(compactness)
    density_ecdf = _percentiles(densities)
    for index, ball in enumerate(balls):
        ball.update(
            {
                "query_score": query_scores[index],
                "query_score_ecdf": query_ecdf[index],
                "radius_ecdf": radius_ecdf[index],
                "compactness_ecdf": compactness_ecdf[index],
                "density_ecdf": density_ecdf[index],
            }
        )


def _rank_dense(
    indices: list[int],
    units: list[dict[str, Any]],
    query_embedding: np.ndarray,
    unit_embeddings: np.ndarray,
) -> list[str]:
    rows = [
        (
            _similarity(query_embedding, unit_embeddings[index]),
            require_native_string(units[index]["unit_id"], "unit_id"),
        )
        for index in indices
    ]
    rows.sort(key=lambda item: (-item[0], item[1]))
    return [unit_id for _, unit_id in rows[:TOP_K]]


def _eligible_balls(
    balls: list[dict[str, Any]], gate_name: str, facet: bool
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], set[str]]:
    gate = FACET_GATES[gate_name]
    seeds = sorted(
        balls,
        key=lambda ball: (
            -ball["query_score_ecdf"],
            -ball["density_ecdf"],
            ball["ball_id"],
        ),
    )[:SEED_BALLS]
    seed_ids = {ball["ball_id"] for ball in seeds}
    covered = {term for ball in seeds for term in ball["facets"]}
    eligible: list[dict[str, Any]] = []
    for ball in balls:
        if ball["ball_id"] in seed_ids:
            continue
        if (
            ball["query_score_ecdf"] < gate["query_score_ecdf"]
            or ball["density_ecdf"] < gate["density_ecdf"]
        ):
            continue
        new_facets = set(ball["facets"]) - covered
        if facet and not new_facets:
            continue
        row = dict(ball)
        row["new_facets"] = tuple(sorted(new_facets))
        row["selection_score"] = (
            0.55 * ball["query_score_ecdf"]
            + 0.25 * ball["density_ecdf"]
            + 0.15 * ball["compactness_ecdf"]
            + (0.05 * min(len(new_facets), 3) / 3 if facet else 0.0)
        )
        eligible.append(row)
    eligible.sort(key=lambda row: (-row["selection_score"], row["ball_id"]))
    return seeds, eligible, covered


def _sequence(
    balls: list[dict[str, Any]],
    query_embedding: np.ndarray,
    candidate_indices: list[int],
    dense_top20: list[str],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    gate_name: str,
    unit_threshold: float,
    facet: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    seeds, eligible, covered = _eligible_balls(balls, gate_name, facet)
    selected = eligible[:MAX_EXPANDED_BALLS]
    scores = {
        index: _similarity(query_embedding, embeddings[index])
        for index in candidate_indices
    }
    values = [scores[index] for index in candidate_indices]
    ecdf_values = _percentiles(values)
    unit_ecdf = {
        index: ecdf_values[position]
        for position, index in enumerate(candidate_indices)
    }
    dense_set = set(dense_top20)
    candidates: dict[str, dict[str, Any]] = {}
    for ball in selected:
        new_fraction = min(len(ball["new_facets"]), 3) / 3
        for index in ball["indices"]:
            unit_id = units[index]["unit_id"]
            if unit_id in dense_set or unit_ecdf[index] < unit_threshold:
                continue
            if facet:
                score = (
                    0.45 * unit_ecdf[index]
                    + 0.25 * ball["query_score_ecdf"]
                    + 0.15 * ball["density_ecdf"]
                    + 0.10 * ball["compactness_ecdf"]
                    + 0.05 * new_fraction
                )
            else:
                score = (
                    0.50 * unit_ecdf[index]
                    + 0.30 * ball["query_score_ecdf"]
                    + 0.10 * ball["density_ecdf"]
                    + 0.10 * ball["compactness_ecdf"]
                )
            row = {
                "ball_id": ball["ball_id"],
                "query_score": scores[index],
                "rerank_score": float(score),
                "unit_id": unit_id,
                "unit_index": index,
                "unit_score_ecdf": unit_ecdf[index],
            }
            previous = candidates.get(unit_id)
            if previous is None or (
                row["rerank_score"], row["ball_id"]
            ) > (
                previous["rerank_score"], previous["ball_id"]
            ):
                candidates[unit_id] = row
    ordered = sorted(
        candidates.values(),
        key=lambda row: (-row["rerank_score"], row["unit_id"]),
    )
    return ordered, {
        "covered_seed_facets": sorted(covered),
        "eligible_ball_count": len(eligible),
        "eligible_candidate_count": len(ordered),
        "seed_ball_ids": [ball["ball_id"] for ball in seeds],
        "selected_ball_ids": [ball["ball_id"] for ball in selected],
    }


def _protected(dense: list[str], inserted: list[str], k: int) -> list[str]:
    if len(inserted) != len(set(inserted)) or set(inserted) & set(dense):
        raise ValueError("independent inserted IDs differ")
    output = list(dense[: min(PROTECTED_PREFIX, len(dense))]) + list(inserted)
    seen = set(output)
    output.extend(unit_id for unit_id in dense if unit_id not in seen)
    return output[:k]


def _unprotected(dense: list[str], inserted: list[str], k: int) -> list[str]:
    if len(inserted) != len(set(inserted)) or set(inserted) & set(dense):
        raise ValueError("independent inserted IDs differ")
    output = list(inserted)
    seen = set(output)
    output.extend(unit_id for unit_id in dense if unit_id not in seen)
    return output[:k]


def _config_result(
    config_row: dict[str, Any],
    balls: list[dict[str, Any]],
    topology: dict[str, Any],
    query_embedding: np.ndarray,
    indices: list[int],
    dense: list[str],
    effective_k: int,
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
) -> tuple[dict[str, list[str]], dict[str, Any]]:
    full, full_info = _sequence(
        balls,
        query_embedding,
        indices,
        dense,
        units,
        embeddings,
        config_row["facet_gate"],
        float(config_row["unit_score_percentile"]),
        True,
    )
    nofacet, nofacet_info = _sequence(
        balls,
        query_embedding,
        indices,
        dense,
        units,
        embeddings,
        config_row["facet_gate"],
        float(config_row["unit_score_percentile"]),
        False,
    )
    budget = int(config_row["insert_budget"])
    inserted = [row["unit_id"] for row in full[:budget]]
    nofacet_inserted = [row["unit_id"] for row in nofacet[:budget]]
    return {
        "protected": _protected(dense, inserted, effective_k),
        "unprotected": _unprotected(dense, inserted, effective_k),
        "no_facet": _protected(dense, nofacet_inserted, effective_k),
        "inserted": inserted,
        "no_facet_inserted": nofacet_inserted,
    }, {
        "config_id": config_row["config_id"],
        "facet": full_info,
        "inserted_unit_ids": inserted,
        "no_facet": nofacet_info,
        "no_facet_inserted_unit_ids": nofacet_inserted,
        "topology": topology,
    }


def independent_development_rankings(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    configs = validate_candidate_configs(config)
    by_query: dict[str, list[int]] = defaultdict(list)
    for index, unit in enumerate(units):
        by_query[unit["query_id"]].append(index)
    rankings: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    for query_index, query in enumerate(queries):
        indices = by_query[query["query_id"]]
        dense = _rank_dense(
            indices, units, query_embeddings[query_index], unit_embeddings
        )
        effective_k = min(TOP_K, len(indices))
        ball_cache: dict[int, tuple[list[dict[str, Any]], dict[str, Any]]] = {}
        for leaf_size in sorted({row["leaf_size"] for row in configs}):
            balls, topology = independent_balls(
                query, indices, units, unit_embeddings, leaf_size
            )
            _add_statistics(balls, query_embeddings[query_index])
            ball_cache[leaf_size] = balls, topology
        methods = {BASELINE_METHOD: dense}
        config_traces: dict[str, Any] = {}
        for row in configs:
            balls, topology = ball_cache[row["leaf_size"]]
            result, trace = _config_result(
                row,
                balls,
                topology,
                query_embeddings[query_index],
                indices,
                dense,
                effective_k,
                units,
                unit_embeddings,
            )
            methods[development_method(row["config_id"])] = result["protected"]
            config_traces[row["config_id"]] = trace
        rankings.append(
            {
                "dataset": query["dataset"],
                "effective_k": effective_k,
                "methods": methods,
                "query_id": query["query_id"],
                "sample_id": query["sample_id"],
            }
        )
        traces.append(
            {
                "configs": config_traces,
                "dataset": query["dataset"],
                "query_id": query["query_id"],
                "sample_id": query["sample_id"],
            }
        )
    return rankings, traces


def independent_confirmation_rankings(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
    selected: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    validate_candidate_configs({"candidate_configs": [selected]})
    by_query: dict[str, list[int]] = defaultdict(list)
    for index, unit in enumerate(units):
        by_query[unit["query_id"]].append(index)
    rankings: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    for query_index, query in enumerate(queries):
        indices = by_query[query["query_id"]]
        dense = _rank_dense(
            indices, units, query_embeddings[query_index], unit_embeddings
        )
        effective_k = min(TOP_K, len(indices))
        balls, topology = independent_balls(
            query, indices, units, unit_embeddings, selected["leaf_size"]
        )
        _add_statistics(balls, query_embeddings[query_index])
        result, trace = _config_result(
            selected,
            balls,
            topology,
            query_embeddings[query_index],
            indices,
            dense,
            effective_k,
            units,
            unit_embeddings,
        )
        methods = {
            BASELINE_METHOD: dense,
            "BGE_NATIVE_HGRAG_PROTECTED_TOP20": result["protected"],
            "BGE_NATIVE_HGRAG_UNPROTECTED_TOP20": result["unprotected"],
            "BGE_NATIVE_HGRAG_NO_FACET_TOP20": result["no_facet"],
        }
        if tuple(methods) != CONFIRMATION_METHODS:
            raise AssertionError("independent confirmation method order differs")
        rankings.append(
            {
                "dataset": query["dataset"],
                "effective_k": effective_k,
                "inserted_unit_ids": result["inserted"],
                "methods": methods,
                "no_facet_inserted_unit_ids": result["no_facet_inserted"],
                "query_id": query["query_id"],
                "sample_id": query["sample_id"],
                "selected_config_id": selected["config_id"],
            }
        )
        traces.append(
            {
                **trace,
                "dataset": query["dataset"],
                "query_id": query["query_id"],
                "sample_id": query["sample_id"],
            }
        )
    return rankings, traces
