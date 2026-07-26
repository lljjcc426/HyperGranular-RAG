"""Matched Qwen3 ranking and structural-selection methods for Stage6A."""

from __future__ import annotations

import heapq
import math
from collections import defaultdict
from typing import Any

import numpy as np

from stage4h_cbe_common import normalize_sentence
from stage5a_bnh_retrieval import _content_tokens, build_bge_native_balls
from stage6a_smc_common import (
    BALL_FAMILY,
    BASELINE_METHOD,
    DATASETS,
    GENERIC_FAMILIES,
    HGRAG_FAMILY,
    NON_BALL_FAMILIES,
    assert_no_gold_fields,
    development_methods,
    parse_method,
    require_json_int,
    require_native_string,
)


TOP_K = 20
PROTECTED_PREFIX = 8
COMMON_POOL_CAP = 100
STRUCTURAL_SELECTION_BUDGET = 4
MATCHED_CONTROL_LEAF_TARGET = 6
MAX_KMEANS_ITERATIONS = 100
BLIND_KEYS = {"candidate_units", "dataset", "query_id", "question", "sample_id"}
UNIT_KEYS = {
    "dataset",
    "document_id",
    "paragraph_index",
    "query_id",
    "sample_id",
    "sentence_index",
    "text",
    "title",
    "unit_id",
}


def build_units_queries(
    blind_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Validate and flatten the three-dataset Stage6A blind channel."""
    assert_no_gold_fields(blind_rows, "Stage6A blind input")
    units: list[dict[str, Any]] = []
    queries: list[dict[str, Any]] = []
    seen_query_ids: set[str] = set()
    for row_index, row in enumerate(blind_rows):
        if not isinstance(row, dict) or set(row) != BLIND_KEYS:
            raise ValueError(f"blind[{row_index}] key contract differs")
        dataset = require_native_string(
            row["dataset"], f"blind[{row_index}].dataset"
        )
        if dataset not in DATASETS:
            raise ValueError(f"blind[{row_index}].dataset differs")
        query_id = require_native_string(
            row["query_id"], f"blind[{row_index}].query_id"
        )
        sample_id = require_native_string(
            row["sample_id"], f"blind[{row_index}].sample_id"
        )
        question = require_native_string(
            row["question"], f"blind[{row_index}].question"
        )
        if query_id != f"{dataset}::{sample_id}" or query_id in seen_query_ids:
            raise ValueError(f"blind[{row_index}] identity differs or duplicates")
        seen_query_ids.add(query_id)
        candidate_units = row["candidate_units"]
        if not isinstance(candidate_units, list) or not candidate_units:
            raise ValueError(f"{query_id}: candidate_units must be non-empty")
        for unit_index, unit in enumerate(candidate_units):
            if not isinstance(unit, dict) or set(unit) != UNIT_KEYS:
                raise ValueError(f"{query_id}: unit[{unit_index}] key contract differs")
            if (
                unit["dataset"] != dataset
                or unit["query_id"] != query_id
                or unit["sample_id"] != sample_id
            ):
                raise ValueError(f"{query_id}: unit[{unit_index}] identity differs")
            require_native_string(unit["document_id"], f"{query_id}.document_id")
            require_native_string(unit["unit_id"], f"{query_id}.unit_id")
            require_native_string(unit["title"], f"{query_id}.title")
            if not normalize_sentence(unit["text"]):
                raise ValueError(f"{query_id}: unit[{unit_index}] text is empty")
            paragraph_index = require_json_int(
                unit["paragraph_index"], f"{query_id}.paragraph_index"
            )
            sentence_index = require_json_int(
                unit["sentence_index"], f"{query_id}.sentence_index"
            )
            if paragraph_index < 0 or sentence_index < 0:
                raise ValueError(f"{query_id}: negative unit index")
            units.append(unit)
        if len({unit["unit_id"] for unit in candidate_units}) != len(
            candidate_units
        ):
            raise ValueError(f"{query_id}: duplicate unit_id")
        queries.append(
            {
                "dataset": dataset,
                "num_candidate_units": len(candidate_units),
                "query_id": query_id,
                "question": question,
                "sample_id": sample_id,
            }
        )
    return units, queries


def _dot(left: np.ndarray, right: np.ndarray) -> float:
    value = float(np.dot(left, right))
    if not math.isfinite(value):
        raise ValueError("non-finite Stage6A similarity")
    return value


def _normalized_mean(indices: list[int], embeddings: np.ndarray) -> np.ndarray:
    result = np.mean(embeddings[indices], axis=0, dtype="float64")
    norm = float(np.linalg.norm(result))
    if not math.isfinite(norm) or norm <= 0.0:
        result = np.asarray(embeddings[indices[0]], dtype="float64")
        norm = float(np.linalg.norm(result))
    if not math.isfinite(norm) or norm <= 0.0:
        raise ValueError("degenerate Stage6A group centroid")
    result = np.asarray(result / norm, dtype="float64")
    if not np.isfinite(result).all():
        raise ValueError("non-finite Stage6A group centroid")
    return result


def _ecdf(values: list[float]) -> list[float]:
    if not values or any(not math.isfinite(value) for value in values):
        raise ValueError("ECDF requires finite values")
    ordered = sorted(values)
    output: list[float] = []
    for value in values:
        low, high = 0, len(ordered)
        while low < high:
            middle = (low + high) // 2
            if ordered[middle] <= value:
                low = middle + 1
            else:
                high = middle
        output.append(low / len(ordered))
    return output


def dense_common_pool(
    indices: list[int],
    units: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embedding: np.ndarray,
) -> tuple[list[int], list[float]]:
    scored = [
        (
            -_dot(query_embedding, unit_embeddings[index]),
            require_native_string(units[index]["unit_id"], "unit_id"),
            index,
        )
        for index in indices
    ]
    scored.sort()
    selected = scored[: min(COMMON_POOL_CAP, len(scored))]
    return [row[2] for row in selected], [-row[0] for row in selected]


def reranker_order(
    pool_indices: list[int],
    scores: list[float],
    units: list[dict[str, Any]],
) -> list[int]:
    if len(pool_indices) != len(scores) or any(
        not math.isfinite(float(value)) for value in scores
    ):
        raise ValueError("reranker score vector differs")
    return [
        index
        for _, _, index in sorted(
            (
                -float(score),
                require_native_string(units[index]["unit_id"], "unit_id"),
                index,
            )
            for index, score in zip(pool_indices, scores, strict=True)
        )
    ]


def fixed_window_groups(
    pool_indices: list[int], units: list[dict[str, Any]]
) -> dict[int, str]:
    return {
        index: (
            f"window::{units[index]['document_id']}::"
            f"{int(units[index]['paragraph_index'])}::"
            f"{int(units[index]['sentence_index']) // 4}"
        )
        for index in pool_indices
    }


def adaptive_ball_groups(
    query: dict[str, Any],
    pool_indices: list[int],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    leaf_target: int,
) -> tuple[dict[int, str], dict[str, Any]]:
    balls, topology = build_bge_native_balls(
        query, pool_indices, units, embeddings, leaf_target
    )
    mapping = {
        index: ball["ball_id"] for ball in balls for index in ball["indices"]
    }
    if set(mapping) != set(pool_indices):
        raise ValueError("adaptive-ball grouping is not a partition")
    return mapping, topology


def spherical_kmeans_groups(
    pool_indices: list[int],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    group_count: int,
) -> dict[int, str]:
    if group_count <= 0 or group_count > len(pool_indices):
        raise ValueError("spherical k-means group count differs")
    global_center = _normalized_mean(pool_indices, embeddings)
    first = min(
        pool_indices,
        key=lambda index: (
            _dot(global_center, embeddings[index]),
            units[index]["unit_id"],
        ),
    )
    centers = [np.asarray(embeddings[first], dtype="float64")]
    center_indices = {first}
    while len(centers) < group_count:
        candidate = min(
            (index for index in pool_indices if index not in center_indices),
            key=lambda index: (
                max(_dot(embeddings[index], center) for center in centers),
                units[index]["unit_id"],
            ),
        )
        center_indices.add(candidate)
        centers.append(np.asarray(embeddings[candidate], dtype="float64"))

    assignment: dict[int, int] = {}
    for _ in range(MAX_KMEANS_ITERATIONS):
        updated: dict[int, int] = {}
        for index in pool_indices:
            similarities = [_dot(embeddings[index], center) for center in centers]
            best = max(similarities)
            updated[index] = min(
                position
                for position, value in enumerate(similarities)
                if value == best
            )
        counts = {cluster: 0 for cluster in range(group_count)}
        for cluster in updated.values():
            counts[cluster] += 1
        for empty in [key for key, count in counts.items() if count == 0]:
            largest = min(
                (
                    (-count, cluster)
                    for cluster, count in counts.items()
                    if count > 1
                )
            )[1]
            members = [
                index for index, cluster in updated.items() if cluster == largest
            ]
            center = _normalized_mean(members, embeddings)
            moved = min(
                members,
                key=lambda index: (
                    _dot(center, embeddings[index]),
                    units[index]["unit_id"],
                ),
            )
            updated[moved] = empty
            counts[largest] -= 1
            counts[empty] += 1
        new_centers = [
            _normalized_mean(
                [index for index, value in updated.items() if value == cluster],
                embeddings,
            )
            for cluster in range(group_count)
        ]
        if updated == assignment:
            assignment = updated
            centers = new_centers
            break
        assignment = updated
        centers = new_centers
    members_by_cluster: dict[int, list[int]] = defaultdict(list)
    for index, cluster in assignment.items():
        members_by_cluster[cluster].append(index)
    label = {
        cluster: (
            "spherical::"
            + min(units[index]["unit_id"] for index in members)
        )
        for cluster, members in members_by_cluster.items()
    }
    return {index: label[cluster] for index, cluster in assignment.items()}


def hierarchical_groups(
    pool_indices: list[int],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    group_count: int,
) -> dict[int, str]:
    if group_count <= 0 or group_count > len(pool_indices):
        raise ValueError("hierarchical group count differs")
    next_id = len(pool_indices)
    members: dict[int, tuple[int, ...]] = {
        position: (index,) for position, index in enumerate(pool_indices)
    }
    sizes = {position: 1 for position in members}
    active = set(members)
    distances: dict[tuple[int, int], float] = {}
    heap: list[tuple[float, str, str, int, int]] = []

    def member_bounds(cluster: int) -> tuple[str, str]:
        ids = sorted(units[index]["unit_id"] for index in members[cluster])
        return ids[0], ids[-1]

    def push(left: int, right: int, distance: float) -> None:
        if left > right:
            left, right = right, left
        key = (left, right)
        distances[key] = distance
        lo = min(member_bounds(left)[0], member_bounds(right)[0])
        hi = max(member_bounds(left)[1], member_bounds(right)[1])
        heapq.heappush(heap, (distance, lo, hi, left, right))

    for left in range(len(pool_indices)):
        for right in range(left + 1, len(pool_indices)):
            push(
                left,
                right,
                1.0
                - _dot(
                    embeddings[pool_indices[left]],
                    embeddings[pool_indices[right]],
                ),
            )
    while len(active) > group_count:
        while True:
            distance, _, _, left, right = heapq.heappop(heap)
            if left in active and right in active and distances.get(
                (min(left, right), max(left, right))
            ) == distance:
                break
        others = sorted(active - {left, right})
        new_cluster = next_id
        next_id += 1
        members[new_cluster] = tuple(sorted(members[left] + members[right]))
        sizes[new_cluster] = sizes[left] + sizes[right]
        active.remove(left)
        active.remove(right)
        active.add(new_cluster)
        for other in others:
            left_key = (min(left, other), max(left, other))
            right_key = (min(right, other), max(right, other))
            merged_distance = (
                sizes[left] * distances[left_key]
                + sizes[right] * distances[right_key]
            ) / (sizes[left] + sizes[right])
            push(new_cluster, other, float(merged_distance))
    output: dict[int, str] = {}
    for cluster in sorted(active, key=lambda value: member_bounds(value)):
        label = "hierarchical::" + member_bounds(cluster)[0]
        for index in members[cluster]:
            output[index] = label
    if set(output) != set(pool_indices):
        raise ValueError("hierarchical grouping is not a partition")
    return output


def _coverage_terms(
    index: int, units: list[dict[str, Any]], query_terms: set[str]
) -> set[str]:
    return query_terms & _content_tokens(
        units[index]["title"] + " " + units[index]["text"]
    )


def _candidate_components(
    candidate: int,
    selected: list[int],
    unit_embeddings: np.ndarray,
    units: list[dict[str, Any]],
    query_terms: set[str],
    covered_terms: set[str],
) -> tuple[float, float]:
    diversity = (
        1.0
        if not selected
        else 1.0
        - max(
            _dot(unit_embeddings[candidate], unit_embeddings[index])
            for index in selected
        )
    )
    diversity = max(0.0, min(1.0, diversity))
    coverage = len(
        _coverage_terms(candidate, units, query_terms) - covered_terms
    ) / max(1, len(query_terms))
    return diversity, coverage


def _group_context(
    mapping: dict[int, str],
    pool_indices: list[int],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    query_terms: set[str],
) -> dict[str, Any]:
    members: dict[str, list[int]] = defaultdict(list)
    for index in pool_indices:
        members[mapping[index]].append(index)
    centroids = {
        group: _normalized_mean(indices, embeddings)
        for group, indices in members.items()
    }
    facets = {
        group: set().union(
            *[
                _coverage_terms(index, units, query_terms)
                for index in indices
            ]
        )
        if indices
        else set()
        for group, indices in members.items()
    }
    hyperedges = {
        term: {
            group for group, values in facets.items() if term in values
        }
        for term in query_terms
    }
    hyperedges = {
        term: values for term, values in hyperedges.items() if len(values) >= 2
    }
    return {
        "centroids": centroids,
        "facets": facets,
        "hyperedges": hyperedges,
        "mapping": mapping,
        "members": members,
    }


def _group_score(
    candidate: int,
    selected: list[int],
    group_context: dict[str, Any],
    query_terms: set[str],
    use_hyperedge: bool,
) -> float:
    mapping = group_context["mapping"]
    group = mapping[candidate]
    selected_groups = {mapping[index] for index in selected}
    first = 1.0 if group not in selected_groups else 0.0
    if not selected_groups:
        second = 1.0
    else:
        second = (
            1.0
            - max(
                _dot(
                    group_context["centroids"][group],
                    group_context["centroids"][other],
                )
                for other in selected_groups
            )
        ) / 2.0
    novelty = 0.5 * first + 0.5 * max(0.0, min(1.0, second))
    if not use_hyperedge:
        return novelty
    covered_facets = set().union(
        *[group_context["facets"][value] for value in selected_groups]
    ) if selected_groups else set()
    facet_gain = len(
        group_context["facets"][group] - covered_facets
    ) / max(1, len(query_terms))
    incident = [
        edge
        for edge, groups in group_context["hyperedges"].items()
        if group in groups
    ]
    activated = 0
    for edge in incident:
        groups = group_context["hyperedges"][edge]
        before = len(groups & selected_groups) >= 2
        after = len(groups & (selected_groups | {group})) >= 2
        if not before and after:
            activated += 1
    bridge_gain = activated / max(1, len(incident))
    return (novelty + facet_gain + bridge_gain) / 3.0


def _greedy_generic(
    family: str,
    lambda_value: float,
    reranked: list[int],
    reranker_ecdf: dict[int, float],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    query_terms: set[str],
    effective_k: int,
) -> tuple[list[int], dict[str, Any]]:
    selected = list(reranked[: min(PROTECTED_PREFIX, effective_k)])
    covered_terms = set().union(
        *[_coverage_terms(index, units, query_terms) for index in selected]
    ) if selected else set()
    while len(selected) < effective_k:
        rows = []
        for candidate in reranked:
            if candidate in selected:
                continue
            diversity, coverage = _candidate_components(
                candidate,
                selected,
                embeddings,
                units,
                query_terms,
                covered_terms,
            )
            if family == GENERIC_FAMILIES[0]:
                secondary = diversity
            elif family == GENERIC_FAMILIES[1]:
                secondary = coverage
            else:
                secondary = 0.5 * diversity + 0.5 * coverage
            score = lambda_value * reranker_ecdf[candidate] + (
                1.0 - lambda_value
            ) * secondary
            rows.append((-score, units[candidate]["unit_id"], candidate))
        if not rows:
            break
        _, _, chosen = min(rows)
        selected.append(chosen)
        covered_terms.update(_coverage_terms(chosen, units, query_terms))
    return selected, {
        "protected_prefix": min(PROTECTED_PREFIX, effective_k),
        "structural_selection_budget": 0,
    }


def _greedy_structural(
    lambda_value: float,
    reranked: list[int],
    reranker_ecdf: dict[int, float],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    query_terms: set[str],
    group_context: dict[str, Any],
    use_hyperedge: bool,
    effective_k: int,
) -> tuple[list[int], dict[str, Any]]:
    selected = list(reranked[: min(PROTECTED_PREFIX, effective_k)])
    covered_terms = set().union(
        *[_coverage_terms(index, units, query_terms) for index in selected]
    ) if selected else set()
    structural_picks: list[int] = []
    target = min(effective_k, len(selected) + STRUCTURAL_SELECTION_BUDGET)
    while len(selected) < target:
        rows = []
        for candidate in reranked:
            if candidate in selected:
                continue
            diversity, coverage = _candidate_components(
                candidate,
                selected,
                embeddings,
                units,
                query_terms,
                covered_terms,
            )
            group_score = _group_score(
                candidate,
                selected,
                group_context,
                query_terms,
                use_hyperedge,
            )
            secondary = 0.25 * diversity + 0.25 * coverage + 0.50 * group_score
            score = lambda_value * reranker_ecdf[candidate] + (
                1.0 - lambda_value
            ) * secondary
            rows.append((-score, units[candidate]["unit_id"], candidate))
        if not rows:
            break
        _, _, chosen = min(rows)
        selected.append(chosen)
        structural_picks.append(chosen)
        covered_terms.update(_coverage_terms(chosen, units, query_terms))
    selected_set = set(selected)
    selected.extend(
        index
        for index in reranked
        if index not in selected_set
    )
    selected = selected[:effective_k]
    return selected, {
        "eligible_hyperedge_count": len(group_context["hyperedges"]),
        "group_count": len(group_context["members"]),
        "protected_prefix": min(PROTECTED_PREFIX, effective_k),
        "structural_pick_unit_ids": [
            units[index]["unit_id"] for index in structural_picks
        ],
        "structural_selection_budget": STRUCTURAL_SELECTION_BUDGET,
    }


def build_query_rankings(
    query: dict[str, Any],
    query_index: int,
    candidate_indices: list[int],
    units: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
    pool_indices: list[int],
    reranker_scores: list[float],
    methods: tuple[str, ...],
) -> tuple[dict[str, list[str]], dict[str, Any]]:
    if not pool_indices or not set(pool_indices).issubset(set(candidate_indices)):
        raise ValueError("common pool differs from query candidates")
    reranked = reranker_order(pool_indices, reranker_scores, units)
    effective_k = min(TOP_K, len(reranked))
    baseline = reranked[:effective_k]
    values = [float(value) for value in reranker_scores]
    percentiles = _ecdf(values)
    reranker_ecdf = {
        index: percentiles[position]
        for position, index in enumerate(pool_indices)
    }
    query_terms = _content_tokens(query["question"])
    ball_groups: dict[int, tuple[dict[int, str], dict[str, Any]]] = {}
    required_leafs = {
        leaf
        for method in methods
        for family, _, leaf in [parse_method(method)]
        if family in (BALL_FAMILY, HGRAG_FAMILY) and leaf is not None
    }
    required_leafs.add(MATCHED_CONTROL_LEAF_TARGET)
    for leaf in sorted(required_leafs):
        ball_groups[leaf] = adaptive_ball_groups(
            query, pool_indices, units, unit_embeddings, leaf
        )
    reference_mapping, reference_topology = ball_groups[
        MATCHED_CONTROL_LEAF_TARGET
    ]
    matched_count = len(set(reference_mapping.values()))
    groupings: dict[str, dict[int, str]] = {
        NON_BALL_FAMILIES[0]: fixed_window_groups(pool_indices, units),
        NON_BALL_FAMILIES[1]: spherical_kmeans_groups(
            pool_indices, units, unit_embeddings, matched_count
        ),
        NON_BALL_FAMILIES[2]: hierarchical_groups(
            pool_indices, units, unit_embeddings, matched_count
        ),
    }
    rankings: dict[str, list[str]] = {
        BASELINE_METHOD: [units[index]["unit_id"] for index in baseline]
    }
    traces: dict[str, Any] = {
        BASELINE_METHOD: {
            "protected_prefix": effective_k,
            "structural_selection_budget": 0,
        }
    }
    for method in methods:
        if method == BASELINE_METHOD:
            continue
        family, lambda_value, leaf_target = parse_method(method)
        assert lambda_value is not None
        if family in GENERIC_FAMILIES:
            selected, trace = _greedy_generic(
                family,
                lambda_value,
                reranked,
                reranker_ecdf,
                units,
                unit_embeddings,
                query_terms,
                effective_k,
            )
        else:
            if family in NON_BALL_FAMILIES:
                mapping = groupings[family]
                use_hyperedge = True
                topology = reference_topology
            else:
                assert leaf_target is not None
                mapping, topology = ball_groups[leaf_target]
                use_hyperedge = family == HGRAG_FAMILY
            context = _group_context(
                mapping, pool_indices, units, unit_embeddings, query_terms
            )
            selected, trace = _greedy_structural(
                lambda_value,
                reranked,
                reranker_ecdf,
                units,
                unit_embeddings,
                query_terms,
                context,
                use_hyperedge,
                effective_k,
            )
            trace["topology"] = topology
        ids = [units[index]["unit_id"] for index in selected]
        if len(ids) != effective_k or len(ids) != len(set(ids)):
            raise ValueError(f"{query['query_id']}/{method}: ranking contract differs")
        if ids[: min(PROTECTED_PREFIX, effective_k)] != rankings[
            BASELINE_METHOD
        ][: min(PROTECTED_PREFIX, effective_k)]:
            raise ValueError(f"{query['query_id']}/{method}: protected prefix differs")
        rankings[method] = ids
        traces[method] = trace
    return rankings, {
        "common_pool_size": len(pool_indices),
        "dense_top20_unit_ids": rankings[BASELINE_METHOD],
        "effective_k": effective_k,
        "matched_control_leaf_target": MATCHED_CONTROL_LEAF_TARGET,
        "matched_group_count": matched_count,
        "methods": traces,
        "query_facet_count": len(query_terms),
    }


def build_rankings(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
    reranker_rows: list[dict[str, Any]],
    methods: tuple[str, ...] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    methods = development_methods() if methods is None else methods
    if (
        unit_embeddings.ndim != 2
        or unit_embeddings.shape[0] != len(units)
        or query_embeddings.ndim != 2
        or query_embeddings.shape[0] != len(queries)
        or not np.isfinite(unit_embeddings).all()
        or not np.isfinite(query_embeddings).all()
    ):
        raise ValueError("Stage6A embedding matrices differ")
    by_query: dict[str, list[int]] = defaultdict(list)
    for index, unit in enumerate(units):
        by_query[unit["query_id"]].append(index)
    reranker_by_query = {
        row["query_id"]: row for row in reranker_rows
    }
    if len(reranker_by_query) != len(reranker_rows):
        raise ValueError("duplicate reranker query identity")
    rankings: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    for query_index, query in enumerate(queries):
        row = reranker_by_query.get(query["query_id"])
        if not isinstance(row, dict):
            raise ValueError(f"{query['query_id']}: reranker row missing")
        if (
            row.get("dataset") != query["dataset"]
            or row.get("sample_id") != query["sample_id"]
        ):
            raise ValueError(f"{query['query_id']}: reranker identity differs")
        local_indices = by_query[query["query_id"]]
        unit_index = {units[index]["unit_id"]: index for index in local_indices}
        pool_ids = row.get("common_pool_unit_ids")
        scores = row.get("reranker_scores")
        if (
            not isinstance(pool_ids, list)
            or not isinstance(scores, list)
            or len(pool_ids) != len(scores)
            or any(
                not isinstance(value, str) or not value
                for value in pool_ids
            )
            or len(pool_ids) != len(set(pool_ids))
        ):
            raise ValueError(f"{query['query_id']}: reranker row schema differs")
        try:
            pool_indices = [unit_index[value] for value in pool_ids]
        except KeyError as exc:
            raise ValueError(
                f"{query['query_id']}: common pool member absent"
            ) from exc
        method_rankings, trace = build_query_rankings(
            query,
            query_index,
            local_indices,
            units,
            unit_embeddings,
            query_embeddings,
            pool_indices,
            [float(value) for value in scores],
            methods,
        )
        rankings.append(
            {
                "dataset": query["dataset"],
                "methods": method_rankings,
                "query_id": query["query_id"],
                "sample_id": query["sample_id"],
            }
        )
        traces.append(
            {
                "dataset": query["dataset"],
                "query_id": query["query_id"],
                "sample_id": query["sample_id"],
                **trace,
            }
        )
    return rankings, traces


__all__ = [
    "COMMON_POOL_CAP",
    "MATCHED_CONTROL_LEAF_TARGET",
    "PROTECTED_PREFIX",
    "STRUCTURAL_SELECTION_BUDGET",
    "TOP_K",
    "adaptive_ball_groups",
    "build_query_rankings",
    "build_rankings",
    "build_units_queries",
    "dense_common_pool",
    "fixed_window_groups",
    "hierarchical_groups",
    "reranker_order",
    "spherical_kmeans_groups",
]
