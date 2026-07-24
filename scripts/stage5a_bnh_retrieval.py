"""BGE-native adaptive balls, facet hyperedges, and frozen retrieval arms."""

from __future__ import annotations

import hashlib
import math
import re
import time
from collections import defaultdict
from typing import Any

import numpy as np

from stage4h_cbe_retrieval import build_units_queries, rank_from_scores
from stage5a_bnh_common import (
    BASELINE_METHOD,
    CONFIRMATION_METHODS,
    DATASETS,
    development_method,
    require_native_string,
    validate_candidate_configs,
)


TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
STOPWORDS = {
    "about",
    "after",
    "also",
    "and",
    "are",
    "been",
    "before",
    "being",
    "between",
    "both",
    "but",
    "did",
    "does",
    "for",
    "from",
    "had",
    "has",
    "have",
    "how",
    "into",
    "its",
    "not",
    "that",
    "the",
    "their",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "was",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "whose",
    "why",
    "will",
    "with",
}

PROTECTED_PREFIX = 10
TOP_K = 20
SEED_BALLS = 2
MAX_EXPANDED_BALLS = 4
MAX_DEPTH = 8
MIN_CHILD_FRACTION = 0.20
MIN_COMPACTNESS_GAIN = 1e-10
FACET_GATES = {
    "BROAD": {"query_score_ecdf": 0.35, "density_ecdf": 0.25},
    "STRICT": {"query_score_ecdf": 0.50, "density_ecdf": 0.50},
}


def _dot(left: np.ndarray, right: np.ndarray) -> float:
    value = float(np.dot(left, right))
    if not math.isfinite(value):
        raise ValueError("non-finite BGE similarity")
    return value


def _normalized_mean(indices: list[int], embeddings: np.ndarray) -> np.ndarray:
    center = np.mean(embeddings[indices], axis=0, dtype="float64")
    norm = float(np.linalg.norm(center))
    if not math.isfinite(norm) or norm <= 0.0:
        center = np.asarray(embeddings[indices[0]], dtype="float64")
        norm = float(np.linalg.norm(center))
    if not math.isfinite(norm) or norm <= 0.0:
        raise ValueError("BGE-native ball center is degenerate")
    result = np.asarray(center / norm, dtype="float64")
    if not np.isfinite(result).all():
        raise ValueError("BGE-native ball center is non-finite")
    return result


def _tie_partition(ball_id: str, unit_id: str) -> int:
    return hashlib.sha256(
        (ball_id + "\0" + unit_id).encode("utf-8")
    ).digest()[0] & 1


def _split_ball(
    ball_id: str,
    indices: list[int],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
) -> tuple[list[int], list[int], float]:
    center = _normalized_mean(indices, embeddings)
    seed_a = min(
        indices,
        key=lambda index: (
            _dot(center, embeddings[index]),
            units[index]["unit_id"],
        ),
    )
    seed_b = min(
        (index for index in indices if index != seed_a),
        key=lambda index: (
            _dot(embeddings[seed_a], embeddings[index]),
            units[index]["unit_id"],
        ),
    )
    left: list[int] = []
    right: list[int] = []
    for index in indices:
        left_score = _dot(embeddings[index], embeddings[seed_a])
        right_score = _dot(embeddings[index], embeddings[seed_b])
        if left_score > right_score:
            left.append(index)
        elif right_score > left_score:
            right.append(index)
        elif _tie_partition(ball_id, units[index]["unit_id"]) == 0:
            left.append(index)
        else:
            right.append(index)
    if not left or not right:
        ordered = sorted(indices, key=lambda index: units[index]["unit_id"])
        midpoint = len(ordered) // 2
        left, right = ordered[:midpoint], ordered[midpoint:]
    parent_compactness = float(
        np.mean([_dot(center, embeddings[index]) for index in indices])
    )
    child_compactness = 0.0
    for child in (left, right):
        child_center = _normalized_mean(child, embeddings)
        child_compactness += len(child) * float(
            np.mean([_dot(child_center, embeddings[index]) for index in child])
        )
    child_compactness /= len(indices)
    return left, right, child_compactness - parent_compactness


def _content_tokens(value: str) -> set[str]:
    return {
        token
        for token in TOKEN_RE.findall(value.lower())
        if len(token) >= 3 and token not in STOPWORDS
    }


def _ball_record(
    ball_id: str,
    indices: list[int],
    depth: int,
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    query_facets: set[str],
) -> dict[str, Any]:
    center = _normalized_mean(indices, embeddings)
    similarities = np.asarray(
        [_dot(center, embeddings[index]) for index in indices],
        dtype="float64",
    )
    radius = float(np.max(1.0 - similarities))
    compactness = float(np.mean(similarities))
    facets: set[str] = set()
    for index in indices:
        facets.update(
            query_facets
            & _content_tokens(units[index]["title"] + " " + units[index]["text"])
        )
    return {
        "ball_id": ball_id,
        "center": center,
        "compactness": compactness,
        "depth": depth,
        "facets": tuple(sorted(facets)),
        "indices": list(indices),
        "radius": radius,
    }


def build_bge_native_balls(
    query: dict[str, Any],
    candidate_indices: list[int],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    leaf_size: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if leaf_size not in {4, 6}:
        raise ValueError("leaf_size differs from frozen family")
    if not candidate_indices:
        raise ValueError("empty candidate index set")
    query_facets = _content_tokens(query["question"])
    pending: list[tuple[str, list[int], int]] = [
        (f"{query['query_id']}::ball", list(candidate_indices), 0)
    ]
    leaves: list[dict[str, Any]] = []
    accepted_splits = 0
    rejected_balance = 0
    rejected_gain = 0
    while pending:
        ball_id, indices, depth = pending.pop()
        if len(indices) <= leaf_size or depth >= MAX_DEPTH:
            leaves.append(
                _ball_record(
                    ball_id,
                    indices,
                    depth,
                    units,
                    embeddings,
                    query_facets,
                )
            )
            continue
        left, right, compactness_gain = _split_ball(
            ball_id, indices, units, embeddings
        )
        balance = min(len(left), len(right)) / len(indices)
        if balance < MIN_CHILD_FRACTION:
            rejected_balance += 1
            leaves.append(
                _ball_record(
                    ball_id,
                    indices,
                    depth,
                    units,
                    embeddings,
                    query_facets,
                )
            )
            continue
        if compactness_gain <= MIN_COMPACTNESS_GAIN:
            rejected_gain += 1
            leaves.append(
                _ball_record(
                    ball_id,
                    indices,
                    depth,
                    units,
                    embeddings,
                    query_facets,
                )
            )
            continue
        accepted_splits += 1
        pending.append((ball_id + "R", right, depth + 1))
        pending.append((ball_id + "L", left, depth + 1))
    leaves.sort(key=lambda row: row["ball_id"])
    if sorted(index for ball in leaves for index in ball["indices"]) != sorted(
        candidate_indices
    ):
        raise ValueError("BGE-native balls do not partition the candidate pool")
    return leaves, {
        "accepted_split_count": accepted_splits,
        "leaf_ball_count": len(leaves),
        "query_facet_count": len(query_facets),
        "rejected_balance_count": rejected_balance,
        "rejected_compactness_gain_count": rejected_gain,
    }


def _ecdf(values: list[float]) -> list[float]:
    if not values or any(not math.isfinite(value) for value in values):
        raise ValueError("ECDF requires finite values")
    ordered = sorted(values)
    return [
        sum(candidate <= value for candidate in ordered) / len(ordered)
        for value in values
    ]


def _enrich_ball_statistics(
    balls: list[dict[str, Any]],
    query_embedding: np.ndarray,
) -> None:
    query_scores = [_dot(query_embedding, ball["center"]) for ball in balls]
    radii = [float(ball["radius"]) for ball in balls]
    compactness = [float(ball["compactness"]) for ball in balls]
    densities = [
        len(ball["indices"]) / max(float(ball["radius"]), 1e-12)
        for ball in balls
    ]
    for index, ball in enumerate(balls):
        ball["query_score"] = query_scores[index]
        ball["query_score_ecdf"] = _ecdf(query_scores)[index]
        ball["radius_ecdf"] = _ecdf(radii)[index]
        ball["compactness_ecdf"] = _ecdf(compactness)[index]
        ball["density_ecdf"] = _ecdf(densities)[index]


def _unit_score_ecdf(
    candidate_indices: list[int],
    query_embedding: np.ndarray,
    embeddings: np.ndarray,
) -> tuple[dict[int, float], dict[int, float]]:
    scores = {
        index: _dot(query_embedding, embeddings[index])
        for index in candidate_indices
    }
    values = [scores[index] for index in candidate_indices]
    percentiles = _ecdf(values)
    return scores, {
        index: percentiles[position]
        for position, index in enumerate(candidate_indices)
    }


def _selected_balls(
    balls: list[dict[str, Any]],
    gate_name: str,
    use_facet: bool,
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
    covered_facets = {
        facet for ball in seeds for facet in ball["facets"]
    }
    eligible: list[dict[str, Any]] = []
    for ball in balls:
        if ball["ball_id"] in seed_ids:
            continue
        if (
            ball["query_score_ecdf"] < gate["query_score_ecdf"]
            or ball["density_ecdf"] < gate["density_ecdf"]
        ):
            continue
        new_facets = set(ball["facets"]) - covered_facets
        if use_facet and not new_facets:
            continue
        item = dict(ball)
        item["new_facets"] = tuple(sorted(new_facets))
        item["selection_score"] = (
            0.55 * ball["query_score_ecdf"]
            + 0.25 * ball["density_ecdf"]
            + 0.15 * ball["compactness_ecdf"]
            + (0.05 * min(len(new_facets), 3) / 3 if use_facet else 0.0)
        )
        eligible.append(item)
    eligible.sort(
        key=lambda ball: (-ball["selection_score"], ball["ball_id"])
    )
    return seeds, eligible, covered_facets


def _candidate_sequence(
    balls: list[dict[str, Any]],
    query_embedding: np.ndarray,
    candidate_indices: list[int],
    dense_top20: list[str],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    gate_name: str,
    unit_percentile: float,
    use_facet: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    seeds, eligible_balls, covered_facets = _selected_balls(
        balls, gate_name, use_facet
    )
    selected_balls = eligible_balls[:MAX_EXPANDED_BALLS]
    scores, percentiles = _unit_score_ecdf(
        candidate_indices, query_embedding, embeddings
    )
    dense_set = set(dense_top20)
    candidates: dict[str, dict[str, Any]] = {}
    for ball in selected_balls:
        new_facet_fraction = min(len(ball["new_facets"]), 3) / 3
        for index in ball["indices"]:
            unit_id = require_native_string(units[index]["unit_id"], "unit_id")
            if unit_id in dense_set or percentiles[index] < unit_percentile:
                continue
            if use_facet:
                rerank_score = (
                    0.45 * percentiles[index]
                    + 0.25 * ball["query_score_ecdf"]
                    + 0.15 * ball["density_ecdf"]
                    + 0.10 * ball["compactness_ecdf"]
                    + 0.05 * new_facet_fraction
                )
            else:
                rerank_score = (
                    0.50 * percentiles[index]
                    + 0.30 * ball["query_score_ecdf"]
                    + 0.10 * ball["density_ecdf"]
                    + 0.10 * ball["compactness_ecdf"]
                )
            row = {
                "ball_id": ball["ball_id"],
                "query_score": scores[index],
                "rerank_score": float(rerank_score),
                "unit_id": unit_id,
                "unit_index": index,
                "unit_score_ecdf": percentiles[index],
            }
            previous = candidates.get(unit_id)
            if previous is None or (
                row["rerank_score"], row["ball_id"]
            ) > (
                previous["rerank_score"],
                previous["ball_id"],
            ):
                candidates[unit_id] = row
    ordered = sorted(
        candidates.values(),
        key=lambda row: (-row["rerank_score"], row["unit_id"]),
    )
    return ordered, {
        "covered_seed_facets": sorted(covered_facets),
        "eligible_ball_count": len(eligible_balls),
        "eligible_candidate_count": len(ordered),
        "seed_ball_ids": [ball["ball_id"] for ball in seeds],
        "selected_ball_ids": [ball["ball_id"] for ball in selected_balls],
    }


def place_protected(
    dense_ids: list[str],
    inserted_ids: list[str],
    effective_k: int,
    protected_prefix: int = PROTECTED_PREFIX,
) -> list[str]:
    if len(inserted_ids) != len(set(inserted_ids)) or set(inserted_ids) & set(
        dense_ids
    ):
        raise ValueError("inserted IDs must be unique and absent from BGE Top-20")
    prefix = dense_ids[: min(protected_prefix, len(dense_ids))]
    output = list(prefix) + list(inserted_ids)
    seen = set(output)
    output.extend(unit_id for unit_id in dense_ids if unit_id not in seen)
    return output[:effective_k]


def place_unprotected(
    dense_ids: list[str], inserted_ids: list[str], effective_k: int
) -> list[str]:
    if len(inserted_ids) != len(set(inserted_ids)) or set(inserted_ids) & set(
        dense_ids
    ):
        raise ValueError("inserted IDs must be unique and absent from BGE Top-20")
    output = list(inserted_ids)
    seen = set(output)
    output.extend(unit_id for unit_id in dense_ids if unit_id not in seen)
    return output[:effective_k]


def _query_context(
    query: dict[str, Any],
    query_index: int,
    indices: list[int],
    units: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
    leaf_sizes: set[int],
) -> dict[str, Any]:
    scores = np.asarray(
        [
            _dot(query_embeddings[query_index], unit_embeddings[index])
            for index in indices
        ],
        dtype="float64",
    )
    effective_k = min(TOP_K, len(indices))
    dense = rank_from_scores(indices, units, scores, TOP_K)
    balls: dict[int, tuple[list[dict[str, Any]], dict[str, Any]]] = {}
    for leaf_size in sorted(leaf_sizes):
        leaf_balls, topology = build_bge_native_balls(
            query, indices, units, unit_embeddings, leaf_size
        )
        _enrich_ball_statistics(leaf_balls, query_embeddings[query_index])
        balls[leaf_size] = leaf_balls, topology
    return {
        "balls": balls,
        "dense": dense,
        "effective_k": effective_k,
        "indices": indices,
    }


def _ranking_for_config(
    config_row: dict[str, Any],
    context: dict[str, Any],
    query_embedding: np.ndarray,
    units: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
) -> tuple[dict[str, list[str]], dict[str, Any]]:
    balls, topology = context["balls"][config_row["leaf_size"]]
    full_candidates, full_info = _candidate_sequence(
        balls,
        query_embedding,
        context["indices"],
        context["dense"],
        units,
        unit_embeddings,
        config_row["facet_gate"],
        float(config_row["unit_score_percentile"]),
        True,
    )
    nofacet_candidates, nofacet_info = _candidate_sequence(
        balls,
        query_embedding,
        context["indices"],
        context["dense"],
        units,
        unit_embeddings,
        config_row["facet_gate"],
        float(config_row["unit_score_percentile"]),
        False,
    )
    budget = int(config_row["insert_budget"])
    inserted = [row["unit_id"] for row in full_candidates[:budget]]
    nofacet_inserted = [
        row["unit_id"] for row in nofacet_candidates[:budget]
    ]
    effective_k = context["effective_k"]
    return {
        "protected": place_protected(
            context["dense"], inserted, effective_k
        ),
        "unprotected": place_unprotected(
            context["dense"], inserted, effective_k
        ),
        "no_facet": place_protected(
            context["dense"], nofacet_inserted, effective_k
        ),
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


def _validate_matrices(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
) -> None:
    for matrix, rows, label in (
        (unit_embeddings, len(units), "unit"),
        (query_embeddings, len(queries), "query"),
    ):
        if (
            matrix.ndim != 2
            or matrix.shape[0] != rows
            or not np.isfinite(matrix).all()
        ):
            raise ValueError(f"BGE {label} embedding matrix differs")


def _validate_methods(
    query: dict[str, Any],
    context: dict[str, Any],
    methods: dict[str, list[str]],
    units: list[dict[str, Any]],
) -> None:
    candidate_ids = {
        units[index]["unit_id"] for index in context["indices"]
    }
    for method, ranking in methods.items():
        if (
            len(ranking) != context["effective_k"]
            or len(ranking) != len(set(ranking))
            or not set(ranking) <= candidate_ids
        ):
            raise ValueError(f"{query['query_id']}/{method}: ranking invalid")


def build_development_rankings(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], float]:
    _validate_matrices(units, queries, unit_embeddings, query_embeddings)
    candidate_configs = validate_candidate_configs(config)
    leaf_sizes = {row["leaf_size"] for row in candidate_configs}
    indices_by_query: dict[str, list[int]] = defaultdict(list)
    for index, unit in enumerate(units):
        indices_by_query[unit["query_id"]].append(index)
    started = time.perf_counter()
    rankings: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    for query_index, query in enumerate(queries):
        context = _query_context(
            query,
            query_index,
            indices_by_query[query["query_id"]],
            units,
            unit_embeddings,
            query_embeddings,
            leaf_sizes,
        )
        methods = {BASELINE_METHOD: context["dense"]}
        config_traces: dict[str, Any] = {}
        for config_row in candidate_configs:
            result, trace = _ranking_for_config(
                config_row,
                context,
                query_embeddings[query_index],
                units,
                unit_embeddings,
            )
            methods[development_method(config_row["config_id"])] = result[
                "protected"
            ]
            config_traces[config_row["config_id"]] = trace
        _validate_methods(query, context, methods, units)
        rankings.append(
            {
                "dataset": query["dataset"],
                "effective_k": context["effective_k"],
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
    return rankings, traces, time.perf_counter() - started


def build_confirmation_rankings(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
    selected_config: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], float]:
    _validate_matrices(units, queries, unit_embeddings, query_embeddings)
    validate_candidate_configs({"candidate_configs": [selected_config]})
    indices_by_query: dict[str, list[int]] = defaultdict(list)
    for index, unit in enumerate(units):
        indices_by_query[unit["query_id"]].append(index)
    started = time.perf_counter()
    rankings: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    for query_index, query in enumerate(queries):
        context = _query_context(
            query,
            query_index,
            indices_by_query[query["query_id"]],
            units,
            unit_embeddings,
            query_embeddings,
            {selected_config["leaf_size"]},
        )
        result, trace = _ranking_for_config(
            selected_config,
            context,
            query_embeddings[query_index],
            units,
            unit_embeddings,
        )
        methods = {
            BASELINE_METHOD: context["dense"],
            "BGE_NATIVE_HGRAG_PROTECTED_TOP20": result["protected"],
            "BGE_NATIVE_HGRAG_UNPROTECTED_TOP20": result["unprotected"],
            "BGE_NATIVE_HGRAG_NO_FACET_TOP20": result["no_facet"],
        }
        if tuple(methods) != CONFIRMATION_METHODS:
            raise AssertionError("Stage5A confirmation method order differs")
        _validate_methods(query, context, methods, units)
        rankings.append(
            {
                "dataset": query["dataset"],
                "effective_k": context["effective_k"],
                "inserted_unit_ids": result["inserted"],
                "methods": methods,
                "no_facet_inserted_unit_ids": result["no_facet_inserted"],
                "query_id": query["query_id"],
                "sample_id": query["sample_id"],
                "selected_config_id": selected_config["config_id"],
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
    return rankings, traces, time.perf_counter() - started


def summarize_geometry_feasibility(
    traces: list[dict[str, Any]], candidate_configs: list[dict[str, Any]]
) -> dict[str, Any]:
    by_id = {row["config_id"]: row for row in candidate_configs}
    summaries: dict[str, Any] = {}
    eligible_configs: list[str] = []
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
            insert_counts = [len(value["inserted_unit_ids"]) for value in values]
            datasets[dataset] = {
                "insertable_query_count": sum(count > 0 for count in insert_counts),
                "insertable_query_rate": (
                    sum(count > 0 for count in insert_counts) / len(insert_counts)
                ),
                "mean_eligible_ball_count": float(
                    np.mean(
                        [
                            value["facet"]["eligible_ball_count"]
                            for value in values
                        ]
                    )
                ),
                "mean_insert_count": float(np.mean(insert_counts)),
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
            eligible_configs.append(config_id)
        summaries[config_id] = {
            "combined_insertable_query_rate": combined_rate,
            "config": config_row,
            "datasets": datasets,
            "feasible": feasible,
        }
    represented_leaf_sizes = {
        by_id[config_id]["leaf_size"] for config_id in eligible_configs
    }
    gate_pass = len(eligible_configs) >= 4 and represented_leaf_sizes == {4, 6}
    return {
        "candidate_config_count": len(candidate_configs),
        "config_summaries": summaries,
        "eligible_config_count": len(eligible_configs),
        "eligible_config_ids": eligible_configs,
        "gate": {
            "minimum_eligible_configs": 4,
            "minimum_insertable_query_rate_combined": 0.15,
            "minimum_insertable_query_rate_each_dataset": 0.10,
            "requires_both_leaf_sizes": True,
            "pass": gate_pass,
            "status": (
                "STAGE5A_BGE_NATIVE_GEOMETRY_FEASIBILITY_PASS"
                if gate_pass
                else "STAGE5A_BGE_NATIVE_GEOMETRY_DEGENERATE"
            ),
        },
        "interpretation": "BLIND_ONLY_FEASIBILITY_NOT_ANSWER_QUALITY_OR_POWER_GUARANTEE",
        "schema_version": "stage5a_bnh_v1",
    }
