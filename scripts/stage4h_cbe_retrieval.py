"""Gold-free Stage4H retrieval arms and frozen component ablations."""

from __future__ import annotations

import math
import re
import time
from collections import Counter, defaultdict
from typing import Any

import numpy as np

from stage4f_xdr_retrieval import (
    RetrievalConfig,
    build_balls,
    build_query_decisions,
    decision_from_balls,
    dot,
    enrich_balls_goldfree,
    protected_rerank_goldfree,
)
from stage4h_cbe_common import (
    DATASETS,
    METHODS,
    assert_no_gold_fields,
    normalize_sentence,
    require_json_int,
    require_native_string,
)


TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
BM25_K1 = 1.5
BM25_B = 0.75
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
    assert_no_gold_fields(blind_rows, "Stage4H blind input")
    units: list[dict[str, Any]] = []
    queries: list[dict[str, Any]] = []
    seen_query_ids: set[str] = set()
    for row_index, row in enumerate(blind_rows):
        if not isinstance(row, dict) or set(row) != BLIND_KEYS:
            raise ValueError(f"blind[{row_index}] key contract differs")
        dataset = require_native_string(row["dataset"], f"blind[{row_index}].dataset")
        if dataset not in DATASETS:
            raise ValueError(f"blind[{row_index}].dataset differs")
        query_id = require_native_string(row["query_id"], f"blind[{row_index}].query_id")
        sample_id = require_native_string(row["sample_id"], f"blind[{row_index}].sample_id")
        question = require_native_string(row["question"], f"blind[{row_index}].question")
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
            text = normalize_sentence(unit["text"])
            if not text:
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
        if len({unit["unit_id"] for unit in candidate_units}) != len(candidate_units):
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


def _tokens(value: str) -> list[str]:
    return TOKEN_RE.findall(value.lower())


def bm25_scores(query: str, documents: list[str]) -> np.ndarray:
    if not documents:
        raise ValueError("BM25 document collection is empty")
    document_tokens = [_tokens(value) for value in documents]
    query_terms = _tokens(query)
    lengths = np.asarray([len(tokens) for tokens in document_tokens], dtype="float64")
    average_length = float(np.mean(lengths))
    if average_length <= 0:
        return np.zeros(len(documents), dtype="float64")
    frequencies = [Counter(tokens) for tokens in document_tokens]
    document_frequency = Counter(
        term for counts in frequencies for term in counts
    )
    scores = np.zeros(len(documents), dtype="float64")
    for term in query_terms:
        df = document_frequency.get(term, 0)
        if df == 0:
            continue
        idf = math.log(1.0 + (len(documents) - df + 0.5) / (df + 0.5))
        for index, counts in enumerate(frequencies):
            frequency = counts.get(term, 0)
            if frequency == 0:
                continue
            denominator = frequency + BM25_K1 * (
                1.0 - BM25_B + BM25_B * lengths[index] / average_length
            )
            scores[index] += idf * frequency * (BM25_K1 + 1.0) / denominator
    if not np.isfinite(scores).all():
        raise ValueError("BM25 produced non-finite scores")
    return scores


def minmax(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype="float64")
    if values.ndim != 1 or not np.isfinite(values).all():
        raise ValueError("minmax input must be a finite vector")
    lower = float(np.min(values))
    upper = float(np.max(values))
    if upper == lower:
        return np.zeros_like(values)
    result = (values - lower) / (upper - lower)
    if not np.isfinite(result).all():
        raise ValueError("minmax output is not finite")
    return result


def rank_from_scores(
    candidate_indices: list[int],
    units: list[dict[str, Any]],
    scores: np.ndarray,
    max_k: int,
) -> list[str]:
    if len(candidate_indices) != len(scores):
        raise ValueError("score/candidate length differs")
    rows = [
        (float(score), require_native_string(units[index]["unit_id"], "unit_id"))
        for index, score in zip(candidate_indices, scores, strict=True)
    ]
    if any(not math.isfinite(score) for score, _ in rows):
        raise ValueError("ranking score is not finite")
    rows.sort(key=lambda item: (-item[0], item[1]))
    return [unit_id for _, unit_id in rows[:max_k]]


def no_protection_ranking(
    dense_ids: list[str],
    full_q25_ids: list[str],
    inserted_ids: list[str],
    max_k: int,
) -> list[str]:
    if len(inserted_ids) != len(set(inserted_ids)):
        raise ValueError("full insertion IDs duplicate")
    ranked = list(inserted_ids)
    seen = set(ranked)
    for source in (dense_ids, full_q25_ids):
        for unit_id in source:
            if unit_id not in seen:
                ranked.append(unit_id)
                seen.add(unit_id)
            if len(ranked) >= max_k:
                return ranked[:max_k]
    return ranked


def centroid_only_expansion(
    query: dict[str, Any],
    query_embedding: np.ndarray,
    candidate_indices: list[int],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    config: RetrievalConfig,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    balls = build_balls(query["query_id"], candidate_indices, embeddings, config)
    enrich_balls_goldfree(balls, units)
    decision = decision_from_balls(query_embedding, balls)
    scored_balls = decision["scored_balls"]
    seed_balls = [ball for _, ball in scored_balls[: config.seed_balls]]
    seed_ids = {ball["ball_id"] for ball in seed_balls}
    seed_centers = [ball["center"] for ball in seed_balls]
    eligible: list[tuple[float, dict[str, Any]]] = []
    for score, ball in scored_balls:
        if ball["ball_id"] in seed_ids:
            continue
        if len(ball["indices"]) > config.max_candidate_ball_size:
            continue
        maximum_seed_similarity = max(
            (dot(ball["center"], center) for center in seed_centers), default=0.0
        )
        if score < config.min_ball_score and maximum_seed_similarity < config.min_seed_similarity:
            continue
        eligible.append((score, ball))
    eligible.sort(key=lambda item: (-item[0], item[1]["ball_id"]))
    selected = [ball for _, ball in eligible[: config.max_expanded_balls]]
    candidates: dict[str, dict[str, Any]] = {}
    for ball in selected:
        for index in ball["indices"]:
            unit_id = require_native_string(units[index]["unit_id"], "unit_id")
            score = dot(query_embedding, embeddings[index])
            row = {
                "unit_id": unit_id,
                "unit_index": index,
                "score": score,
                "rerank_score": score,
            }
            previous = candidates.get(unit_id)
            if previous is None or row["score"] > previous["score"]:
                candidates[unit_id] = row
    ranked = sorted(
        candidates.values(), key=lambda row: (-row["rerank_score"], row["unit_id"])
    )
    return ranked, {
        "ball_score_margin": float(decision["ball_score_margin"]),
        "boundary_margin": float(decision["boundary_margin"]),
        "eligible_ball_count": len(eligible),
        "selected_ball_count": len(selected),
        "selected_ball_ids": [ball["ball_id"] for ball in selected],
    }


def build_rankings(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    minilm_unit_embeddings: np.ndarray,
    minilm_query_embeddings: np.ndarray,
    strong_unit_embeddings: np.ndarray,
    strong_query_embeddings: np.ndarray,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, float]]:
    arrays = (
        (minilm_unit_embeddings, len(units), "MiniLM unit"),
        (minilm_query_embeddings, len(queries), "MiniLM query"),
        (strong_unit_embeddings, len(units), "strong unit"),
        (strong_query_embeddings, len(queries), "strong query"),
    )
    for matrix, expected, label in arrays:
        if matrix.ndim != 2 or matrix.shape[0] != expected or not np.isfinite(matrix).all():
            raise ValueError(f"{label} embedding matrix differs")
    config = RetrievalConfig()
    started = time.perf_counter()
    full_decisions = build_query_decisions(
        units,
        queries,
        minilm_unit_embeddings,
        minilm_query_embeddings,
        config,
    )
    full_seconds = time.perf_counter() - started
    indices_by_query: dict[str, list[int]] = defaultdict(list)
    for index, unit in enumerate(units):
        indices_by_query[unit["query_id"]].append(index)
    rankings: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    bm25_seconds = 0.0
    hybrid_seconds = 0.0
    strong_seconds = 0.0
    nofacet_seconds = 0.0
    for query_index, (query, full) in enumerate(
        zip(queries, full_decisions, strict=True)
    ):
        candidate_indices = indices_by_query[query["query_id"]]
        effective_k = min(config.max_k, len(candidate_indices))
        dense_ids = full["dense_top20_unit_ids"]
        full_ids = full["q25_top20_unit_ids"]
        inserted_ids = full["q25_inserted_unit_ids"]
        no_protection_ids = no_protection_ranking(
            dense_ids, full_ids, inserted_ids, effective_k
        )

        started = time.perf_counter()
        centroid_candidates, centroid_info = centroid_only_expansion(
            query,
            minilm_query_embeddings[query_index],
            candidate_indices,
            units,
            minilm_unit_embeddings,
            config,
        )
        filtered_centroid = [
            row for row in centroid_candidates if row["score"] >= config.q25_floor
        ]
        dense_rows = [
            {
                "unit_id": unit_id,
                "unit_index": next(
                    index
                    for index in candidate_indices
                    if units[index]["unit_id"] == unit_id
                ),
                "score": dot(
                    minilm_query_embeddings[query_index],
                    minilm_unit_embeddings[
                        next(
                            index
                            for index in candidate_indices
                            if units[index]["unit_id"] == unit_id
                        )
                    ],
                ),
            }
            for unit_id in dense_ids
        ]
        nofacet_rows, nofacet_inserted = protected_rerank_goldfree(
            dense_rows,
            filtered_centroid,
            config.protect_n,
            config.insert_budget,
            config.max_k,
        )
        nofacet_ids = [row["unit_id"] for row in nofacet_rows]
        nofacet_seconds += time.perf_counter() - started

        documents = [
            (units[index]["title"] + ". " + units[index]["text"]).strip()
            for index in candidate_indices
        ]
        started = time.perf_counter()
        lexical_scores = bm25_scores(query["question"], documents)
        bm25_ids = rank_from_scores(
            candidate_indices, units, lexical_scores, config.max_k
        )
        bm25_seconds += time.perf_counter() - started

        started = time.perf_counter()
        dense_scores = np.asarray(
            [
                dot(
                    minilm_query_embeddings[query_index],
                    minilm_unit_embeddings[index],
                )
                for index in candidate_indices
            ],
            dtype="float64",
        )
        hybrid_scores = 0.5 * minmax(dense_scores) + 0.5 * minmax(lexical_scores)
        hybrid_ids = rank_from_scores(
            candidate_indices, units, hybrid_scores, config.max_k
        )
        hybrid_seconds += time.perf_counter() - started

        started = time.perf_counter()
        strong_scores = np.asarray(
            [
                dot(
                    strong_query_embeddings[query_index],
                    strong_unit_embeddings[index],
                )
                for index in candidate_indices
            ],
            dtype="float64",
        )
        strong_ids = rank_from_scores(
            candidate_indices, units, strong_scores, config.max_k
        )
        strong_seconds += time.perf_counter() - started

        methods = {
            "DENSE_TOP20": dense_ids,
            "STATIC_Q25_FULL": full_ids,
            "Q25_NO_PROTECTION": no_protection_ids,
            "Q25_NO_FACET_HYPEREDGE": nofacet_ids,
            "BM25_TOP20": bm25_ids,
            "DENSE_BM25_HYBRID_TOP20": hybrid_ids,
            "STRONG_DENSE_TOP20": strong_ids,
        }
        if set(methods) != set(METHODS):
            raise AssertionError("Internal Stage4H method set differs")
        candidate_id_set = {units[index]["unit_id"] for index in candidate_indices}
        for method, values in methods.items():
            if (
                len(values) != effective_k
                or len(values) != len(set(values))
                or not set(values) <= candidate_id_set
            ):
                raise ValueError(f"{query['query_id']}: {method} ranking invalid")
        rankings.append(
            {
                "dataset": query["dataset"],
                "effective_k": effective_k,
                "full_inserted_unit_ids": inserted_ids,
                "methods": methods,
                "no_facet_inserted_unit_ids": [
                    row["unit_id"] for row in nofacet_inserted
                ],
                "query_id": query["query_id"],
                "sample_id": query["sample_id"],
            }
        )
        traces.append(
            {
                "ball_score_margin": full["ball_score_margin"],
                "boundary_margin": full["boundary_margin"],
                "dataset": query["dataset"],
                "full_insert_count": len(inserted_ids),
                "full_selected_edge_count": full["selected_edge_count"],
                "no_facet_eligible_ball_count": centroid_info["eligible_ball_count"],
                "no_facet_insert_count": len(nofacet_inserted),
                "no_facet_selected_ball_count": centroid_info["selected_ball_count"],
                "no_facet_selected_ball_ids": centroid_info["selected_ball_ids"],
                "query_id": query["query_id"],
                "sample_id": query["sample_id"],
            }
        )
    return rankings, traces, {
        "BM25_TOP20": bm25_seconds,
        "DENSE_BM25_HYBRID_TOP20": hybrid_seconds,
        "Q25_NO_FACET_HYPEREDGE": nofacet_seconds,
        "STATIC_Q25_FULL_AND_DENSE_TOP20": full_seconds,
        "STRONG_DENSE_TOP20": strong_seconds,
    }
