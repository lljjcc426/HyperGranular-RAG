"""Independent Stage6A selector reconstruction.

This module deliberately does not call ``build_query_rankings`` or
``build_rankings`` from the production implementation.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

import numpy as np

from stage5a_bnh_retrieval import _content_tokens
from stage6a_smc_common import (
    BALL_FAMILY,
    BASELINE_METHOD,
    GENERIC_FAMILIES,
    HGRAG_FAMILY,
    NON_BALL_FAMILIES,
    parse_method,
)
from stage6a_smc_retrieval import (
    MATCHED_CONTROL_LEAF_TARGET,
    PROTECTED_PREFIX,
    STRUCTURAL_SELECTION_BUDGET,
    TOP_K,
    adaptive_ball_groups,
    fixed_window_groups,
    hierarchical_groups,
    reranker_order,
    spherical_kmeans_groups,
)


def _dot(left: np.ndarray, right: np.ndarray) -> float:
    value = float(np.dot(left, right))
    if not math.isfinite(value):
        raise ValueError("independent non-finite similarity")
    return value


def _mean(indices: list[int], embeddings: np.ndarray) -> np.ndarray:
    value = np.mean(embeddings[indices], axis=0, dtype="float64")
    norm = float(np.linalg.norm(value))
    if not math.isfinite(norm) or norm <= 0.0:
        raise ValueError("independent degenerate centroid")
    return value / norm


def _ecdf(indices: list[int], scores: list[float]) -> dict[int, float]:
    ordered = sorted(float(value) for value in scores)
    output = {}
    for index, value in zip(indices, scores, strict=True):
        output[index] = sum(candidate <= value for candidate in ordered) / len(
            ordered
        )
    return output


def _terms(
    index: int, units: list[dict[str, Any]], question_terms: set[str]
) -> set[str]:
    return question_terms & _content_tokens(
        units[index]["title"] + " " + units[index]["text"]
    )


def _components(
    candidate: int,
    selected: list[int],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    question_terms: set[str],
) -> tuple[float, float]:
    diversity = 1.0 - max(
        _dot(embeddings[candidate], embeddings[value]) for value in selected
    )
    covered = set().union(
        *[_terms(value, units, question_terms) for value in selected]
    )
    coverage = len(
        _terms(candidate, units, question_terms) - covered
    ) / max(1, len(question_terms))
    return max(0.0, min(1.0, diversity)), coverage


def _group_data(
    mapping: dict[int, str],
    pool: list[int],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    question_terms: set[str],
) -> dict[str, Any]:
    members: dict[str, list[int]] = defaultdict(list)
    for index in pool:
        members[mapping[index]].append(index)
    facets = {
        group: set().union(
            *[_terms(index, units, question_terms) for index in indices]
        )
        for group, indices in members.items()
    }
    edges = {
        term: {
            group for group, values in facets.items() if term in values
        }
        for term in question_terms
    }
    return {
        "centroids": {
            group: _mean(indices, embeddings)
            for group, indices in members.items()
        },
        "edges": {
            term: groups for term, groups in edges.items() if len(groups) >= 2
        },
        "facets": facets,
        "mapping": mapping,
    }


def _structure_value(
    candidate: int,
    selected: list[int],
    data: dict[str, Any],
    question_terms: set[str],
    use_hyperedge: bool,
) -> float:
    group = data["mapping"][candidate]
    represented = {data["mapping"][index] for index in selected}
    group_new = float(group not in represented)
    distance = (
        1.0
        if not represented
        else (
            1.0
            - max(
                _dot(data["centroids"][group], data["centroids"][other])
                for other in represented
            )
        )
        / 2.0
    )
    novelty = 0.5 * group_new + 0.5 * max(0.0, min(1.0, distance))
    if not use_hyperedge:
        return novelty
    covered = set().union(
        *[data["facets"][value] for value in represented]
    ) if represented else set()
    facet_gain = len(data["facets"][group] - covered) / max(
        1, len(question_terms)
    )
    incident = [
        groups for groups in data["edges"].values() if group in groups
    ]
    newly_activated = sum(
        len(groups & represented) < 2
        and len(groups & (represented | {group})) >= 2
        for groups in incident
    )
    bridge = newly_activated / max(1, len(incident))
    return (novelty + facet_gain + bridge) / 3.0


def independent_query_rankings(
    query: dict[str, Any],
    pool: list[int],
    reranker_scores: list[float],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    methods: tuple[str, ...],
) -> dict[str, list[str]]:
    reranked = reranker_order(pool, reranker_scores, units)
    effective_k = min(TOP_K, len(reranked))
    result = {
        BASELINE_METHOD: [
            units[index]["unit_id"] for index in reranked[:effective_k]
        ]
    }
    percentiles = _ecdf(pool, reranker_scores)
    question_terms = _content_tokens(query["question"])
    required_leafs = {
        leaf
        for method in methods
        for family, _, leaf in [parse_method(method)]
        if family in (BALL_FAMILY, HGRAG_FAMILY) and leaf is not None
    } | {MATCHED_CONTROL_LEAF_TARGET}
    ball = {
        leaf: adaptive_ball_groups(query, pool, units, embeddings, leaf)
        for leaf in required_leafs
    }
    reference_mapping, _ = ball[MATCHED_CONTROL_LEAF_TARGET]
    group_count = len(set(reference_mapping.values()))
    non_ball = {
        NON_BALL_FAMILIES[0]: fixed_window_groups(pool, units),
        NON_BALL_FAMILIES[1]: spherical_kmeans_groups(
            pool, units, embeddings, group_count
        ),
        NON_BALL_FAMILIES[2]: hierarchical_groups(
            pool, units, embeddings, group_count
        ),
    }
    for method in methods:
        if method == BASELINE_METHOD:
            continue
        family, lambda_value, leaf = parse_method(method)
        assert lambda_value is not None
        selected = list(reranked[: min(PROTECTED_PREFIX, effective_k)])
        if family in GENERIC_FAMILIES:
            target = effective_k
            structure = None
            use_hyperedge = False
        else:
            target = min(
                effective_k, len(selected) + STRUCTURAL_SELECTION_BUDGET
            )
            if family in NON_BALL_FAMILIES:
                mapping = non_ball[family]
                use_hyperedge = True
            else:
                assert leaf is not None
                mapping = ball[leaf][0]
                use_hyperedge = family == HGRAG_FAMILY
            structure = _group_data(
                mapping, pool, units, embeddings, question_terms
            )
        while len(selected) < target:
            candidates = []
            for candidate in reranked:
                if candidate in selected:
                    continue
                diversity, coverage = _components(
                    candidate,
                    selected,
                    units,
                    embeddings,
                    question_terms,
                )
                if family == GENERIC_FAMILIES[0]:
                    secondary = diversity
                elif family == GENERIC_FAMILIES[1]:
                    secondary = coverage
                elif family == GENERIC_FAMILIES[2]:
                    secondary = 0.5 * diversity + 0.5 * coverage
                else:
                    assert structure is not None
                    group_score = _structure_value(
                        candidate,
                        selected,
                        structure,
                        question_terms,
                        use_hyperedge,
                    )
                    secondary = (
                        0.25 * diversity
                        + 0.25 * coverage
                        + 0.50 * group_score
                    )
                score = (
                    lambda_value * percentiles[candidate]
                    + (1.0 - lambda_value) * secondary
                )
                candidates.append(
                    (-score, units[candidate]["unit_id"], candidate)
                )
            if not candidates:
                break
            selected.append(min(candidates)[2])
        if family not in GENERIC_FAMILIES:
            selected_set = set(selected)
            selected.extend(
                index for index in reranked if index not in selected_set
            )
        selected = selected[:effective_k]
        result[method] = [units[index]["unit_id"] for index in selected]
    return result


__all__ = ["independent_query_rankings"]
