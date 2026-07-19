"""Stage4D-CMA Channel A: deterministic Gold-free candidate trace construction."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

from stage4b_u1_goldfree_retrieval import (
    RetrievalConfig,
    build_balls,
    content_tokens,
    dot,
    enrich_balls_goldfree,
    normalize_matrix,
    select_facet_edges_goldfree,
)


SCHEMA_VERSION = "stage4d_cma_v1"
CHANNEL_A_AUTH_ENV = "STAGE4D_CHANNEL_A_EXECUTION_AUTHORIZED"
CHANNEL_A_AUTH_VALUE = "AUTHORIZED_STAGE4D_CHANNEL_A"
RELOCATION_FROM = r"E:\科研"
RELOCATION_TO = r"E:\SCIENCE"
OFFICIAL_CONFIG_SHA256 = (
    "176FF6747680DD597DB01E174619CABF7112BF4B91FF8BF2402F5B02754A5F58"
)
FROZEN_REPOSITORY_INPUTS = {
    "results/stage4b_u1_d_official_dev4500_v2_3_1_controller_channel_audit.json":
        "D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA",
    "results/stage4b_u1_d_official_dev4500_simplified_v1_rankings.jsonl":
        "ED289D234F6F4FEC58A48168CB6CA78950489CD5F5640E977068CA6A786E03CB",
    "results/stage4b_u1_d_official_dev4500_simplified_v1_verified_pre_gold.json":
        "39EAD86A3A835983DCB67BAF656255F51569BCEE5B9AC2E16FACF404281D7818",
    "results/stage4b_u1_d_official_dev4500_simplified_v1_decisions.jsonl":
        "4B2AD2E5707B20FD46B6250FDA5395433F52E55FB1281F1499412C8C749A456A",
}
QUERY_TRACE_NAME = "stage4d_cma_query_trace.jsonl"
CANDIDATE_TRACE_NAME = "stage4d_cma_candidate_trace.jsonl"
MANIFEST_NAME = "stage4d_cma_candidate_trace_manifest.json"
VERIFICATION_NAME = "stage4d_cma_verified_channel_a.json"

NOT_AVAILABLE_FIELDS = {
    "bridge_entity_overlap": "no frozen entity or bridge annotation",
    "cross_ball_support_count": "no frozen cross-ball support relation",
    "entity_new_coverage": "no frozen entity linker or entity vocabulary",
    "independent_facet_support_count": "facet terms are lexical, not independent facet nodes",
    "path_length": "no explicit multi-edge path object",
    "path_position": "no explicit multi-edge path object",
    "path_support_strength": "no explicit multi-edge path object",
    "support_source_entropy": "no multi-source support distribution",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def render_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def render_jsonl(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(
        (
            json.dumps(
                row,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
        for row in rows
    )


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"{path}:{line_number}: JSONL row must be an object")
                rows.append(value)
    return rows


def registered_path(value: str) -> Path:
    if value == RELOCATION_FROM:
        value = RELOCATION_TO
    elif value.startswith(RELOCATION_FROM + "\\"):
        value = RELOCATION_TO + value[len(RELOCATION_FROM) :]
    return Path(value)


def require_official_channel_a_authorization() -> None:
    if os.environ.get(CHANNEL_A_AUTH_ENV) != CHANNEL_A_AUTH_VALUE:
        raise PermissionError(
            "Official Stage4D Channel A is not authorized; no input was opened"
        )


def _native_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a native non-empty string")
    return value


def _finite(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise ValueError(f"{label} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def _unit_tokens(unit: dict[str, Any]) -> set[str]:
    return content_tokens(str(unit.get("title", ""))) | content_tokens(
        str(unit.get("text", ""))
    )


def _rank_with_insertions(
    dense_ids: Sequence[str],
    inserted_ids: Sequence[str],
    *,
    protect_n: int,
    effective_k: int,
) -> list[str]:
    protected = list(dense_ids[:protect_n])
    seen = set(protected)
    ranking = list(protected)
    for unit_id in inserted_ids:
        if unit_id not in seen and len(ranking) < effective_k:
            ranking.append(unit_id)
            seen.add(unit_id)
    for unit_id in dense_ids:
        if len(ranking) >= effective_k:
            break
        if unit_id not in seen:
            ranking.append(unit_id)
            seen.add(unit_id)
    if len(ranking) != effective_k or len(set(ranking)) != effective_k:
        raise ValueError("Effective ranking reconstruction failed")
    return ranking


def _validate_inputs(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
) -> tuple[list[str], list[str]]:
    if unit_embeddings.shape[0] != len(units) or query_embeddings.shape[0] != len(queries):
        raise ValueError("Embedding row counts differ from input rows")
    if unit_embeddings.ndim != 2 or query_embeddings.ndim != 2:
        raise ValueError("Embedding matrices must be two-dimensional")
    if unit_embeddings.shape[1] != query_embeddings.shape[1]:
        raise ValueError("Unit/query embedding dimensions differ")
    if not np.isfinite(unit_embeddings).all() or not np.isfinite(query_embeddings).all():
        raise ValueError("Embedding matrices must be finite")
    unit_ids = [_native_string(row.get("unit_id"), "unit.unit_id") for row in units]
    query_ids = [_native_string(row.get("query_id"), "query.query_id") for row in queries]
    if len(unit_ids) != len(set(unit_ids)):
        raise ValueError("Unit IDs are not unique")
    if len(query_ids) != len(set(query_ids)):
        raise ValueError("Query IDs are not unique")
    query_set = set(query_ids)
    if {_native_string(row.get("query_id"), "unit.query_id") for row in units} != query_set:
        raise ValueError("Unit/query ID sets differ")
    for row in queries:
        dataset = _native_string(row.get("dataset"), "query.dataset")
        sample_id = _native_string(row.get("sample_id"), "query.sample_id")
        if row["query_id"] != f"{dataset}::{sample_id}":
            raise ValueError("query_id must equal dataset::sample_id")
    return unit_ids, query_ids


def build_channel_a_traces(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
    config: RetrievalConfig,
    *,
    frozen_rankings: dict[str, dict[str, Any]] | None = None,
    u1_scores: dict[str, float | None] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Build Channel A traces entirely from caller-supplied Gold-free arrays."""

    unit_embeddings = normalize_matrix(np.asarray(unit_embeddings, dtype="float32"))
    query_embeddings = normalize_matrix(np.asarray(query_embeddings, dtype="float32"))
    _, query_ids = _validate_inputs(units, queries, unit_embeddings, query_embeddings)
    if config.w_facet_unit_bonus != 0.0:
        raise ValueError("Stage4D v1 requires frozen w_facet_unit_bonus=0.0")

    indices_by_query: dict[str, list[int]] = defaultdict(list)
    index_by_unit_id: dict[str, int] = {}
    for index, unit in enumerate(units):
        query_id = str(unit["query_id"])
        indices_by_query[query_id].append(index)
        index_by_unit_id[str(unit["unit_id"])] = index

    query_trace: list[dict[str, Any]] = []
    candidate_trace: list[dict[str, Any]] = []

    for query_index, query in enumerate(queries):
        query_id = query_ids[query_index]
        dataset = _native_string(query["dataset"], f"{query_id}.dataset")
        sample_id = _native_string(query["sample_id"], f"{query_id}.sample_id")
        candidate_indices = indices_by_query[query_id]
        expected_count = query.get("num_candidate_units")
        if isinstance(expected_count, bool) or not isinstance(expected_count, int):
            raise ValueError(f"{query_id}: num_candidate_units must be an integer")
        if expected_count != len(candidate_indices) or expected_count < 1:
            raise ValueError(f"{query_id}: candidate count differs")

        query_embedding = query_embeddings[query_index]
        dense_full = [
            {
                "unit_index": index,
                "unit_id": str(units[index]["unit_id"]),
                "score": dot(query_embedding, unit_embeddings[index]),
            }
            for index in candidate_indices
        ]
        dense_full.sort(key=lambda row: (-row["score"], row["unit_id"]))
        effective_k = min(config.max_k, len(dense_full))
        protect_n = min(config.protect_n, effective_k)
        insert_budget = min(config.insert_budget, effective_k - protect_n)
        dense_top = dense_full[:effective_k]
        dense_ids = [str(row["unit_id"]) for row in dense_top]
        dense_rank = {
            str(row["unit_id"]): rank
            for rank, row in enumerate(dense_full, start=1)
        }
        dense_score = {str(row["unit_id"]): float(row["score"]) for row in dense_full}

        balls = build_balls(query_id, candidate_indices, unit_embeddings, config)
        enrich_balls_goldfree(balls, units)
        selected_edges, _ = select_facet_edges_goldfree(
            query, query_embedding, balls, config
        )
        ball_by_id = {str(ball["ball_id"]): ball for ball in balls}
        scored_balls = sorted(
            ((dot(query_embedding, ball["center"]), ball) for ball in balls),
            key=lambda item: (-item[0], item[1]["ball_id"]),
        )
        seed_balls = [ball for _, ball in scored_balls[: config.seed_balls]]
        selected_by_ball = {
            str(edge["accepted_ball_ids"][0]): edge for edge in selected_edges
        }

        expanded_by_unit: dict[str, dict[str, Any]] = {}
        for ball_id, edge in selected_by_ball.items():
            ball = ball_by_id[ball_id]
            facet_bonus = _finite(edge["facet_score"], f"{query_id}.facet_score")
            for index in ball["indices"]:
                unit_id = str(units[index]["unit_id"])
                base_score = dot(query_embedding, unit_embeddings[index])
                rerank_score = _finite(
                    base_score + config.w_facet_unit_bonus * facet_bonus,
                    f"{query_id}.{unit_id}.q25_score",
                )
                row = {
                    "unit_index": index,
                    "unit_id": unit_id,
                    "dense_score": base_score,
                    "q25_score": rerank_score,
                    "ball_id": ball_id,
                    "edge": edge,
                    "ball": ball,
                }
                previous = expanded_by_unit.get(unit_id)
                if previous is None or rerank_score > float(previous["q25_score"]):
                    expanded_by_unit[unit_id] = row

        ordered_expanded = sorted(
            expanded_by_unit.values(),
            key=lambda row: (-float(row["q25_score"]), str(row["unit_id"])),
        )
        protected_set = set(dense_ids[:protect_n])
        eligible = [
            row
            for row in ordered_expanded
            if float(row["dense_score"]) >= config.q25_floor
            and str(row["unit_id"]) not in protected_set
        ]
        eligible_ids = [str(row["unit_id"]) for row in eligible]
        if len(eligible_ids) != len(set(eligible_ids)):
            raise ValueError(f"{query_id}: duplicate eligible candidate")
        inserted_count = min(insert_budget, len(eligible_ids))
        inserted_ids = eligible_ids[:inserted_count]
        q25_ids = _rank_with_insertions(
            dense_ids,
            inserted_ids,
            protect_n=protect_n,
            effective_k=effective_k,
        )

        if frozen_rankings is not None:
            frozen = frozen_rankings.get(query_id)
            if frozen is None:
                raise ValueError(f"{query_id}: missing frozen ranking")
            for key in ("query_id", "dataset", "sample_id"):
                if _native_string(frozen.get(key), f"{query_id}.frozen.{key}") != query[key]:
                    raise ValueError(f"{query_id}: frozen ranking identity differs")
            frozen_dense = [
                _native_string(value, f"{query_id}.frozen.dense[]")
                for value in frozen["dense_top20_unit_ids"]
            ]
            frozen_q25 = [
                _native_string(value, f"{query_id}.frozen.q25[]")
                for value in frozen["q25_top20_unit_ids"]
            ]
            frozen_inserted = [
                _native_string(value, f"{query_id}.frozen.inserted[]")
                for value in frozen["q25_inserted_unit_ids"]
            ]
            if frozen_dense != dense_ids:
                raise ValueError(f"{query_id}: Dense reconstruction differs")
            if frozen_q25 != q25_ids:
                raise ValueError(f"{query_id}: q25 reconstruction differs")
            if frozen_inserted != inserted_ids:
                raise ValueError(f"{query_id}: q25 insert reconstruction differs")

        query_trace.append(
            {
                "candidate_count": len(eligible_ids),
                "dataset": dataset,
                "dense_topk_unit_ids": dense_ids,
                "effective_k": effective_k,
                "eligible_candidate_unit_ids": eligible_ids,
                "original_u1_score": (
                    None
                    if u1_scores is None or u1_scores.get(query_id) is None
                    else _finite(u1_scores[query_id], f"{query_id}.u1_score")
                ),
                "planned_insert_budget": insert_budget,
                "protect_n": protect_n,
                "q25_inserted_unit_ids": inserted_ids,
                "q25_topk_unit_ids": q25_ids,
                "query_id": query_id,
                "sample_id": sample_id,
            }
        )

        protected_indices = [index_by_unit_id[unit_id] for unit_id in dense_ids[:protect_n]]
        protected_embeddings = unit_embeddings[protected_indices]
        query_terms = content_tokens(str(query["question"]))
        protected_query_facets: set[str] = set()
        for index in protected_indices:
            protected_query_facets.update(_unit_tokens(units[index]) & query_terms)

        eligible_indices = [int(row["unit_index"]) for row in eligible]
        candidate_pool_size = len(candidate_indices)
        for eligible_offset, row in enumerate(eligible):
            rank = eligible_offset + 1
            unit_id = str(row["unit_id"])
            unit_index = int(row["unit_index"])
            ball = row["ball"]
            edge = row["edge"]
            embedding = unit_embeddings[unit_index]

            protected_sims = [
                dot(embedding, protected_embeddings[index])
                for index in range(len(protected_indices))
            ]
            peer_sims = [
                dot(embedding, unit_embeddings[peer_index])
                for peer_index in eligible_indices
                if peer_index != unit_index
            ]
            seed_sims = [dot(embedding, seed["center"]) for seed in seed_balls]
            candidate_facets = _unit_tokens(units[unit_index]) & query_terms
            covered_facets = candidate_facets & protected_query_facets
            novel_facets = candidate_facets - protected_query_facets

            standardized = _rank_with_insertions(
                dense_ids,
                [unit_id],
                protect_n=protect_n,
                effective_k=effective_k,
            )
            displaced = list(set(dense_ids) - set(standardized))
            if len(displaced) > 1:
                raise ValueError(f"{query_id}:{unit_id}: multiple displaced units")
            displaced_id = displaced[0] if displaced else None
            if displaced_id is None:
                displaced_rank = 0
                displaced_score = 0.0
                displaced_margin = 0.0
                displaced_similarity = 0.0
            else:
                displaced_rank = dense_ids.index(displaced_id) + 1
                displaced_score = dense_score[displaced_id]
                displaced_margin = float(row["dense_score"]) - displaced_score
                displaced_similarity = dot(
                    embedding, unit_embeddings[index_by_unit_id[displaced_id]]
                )

            candidate_rank_percentile = (rank - 1) / max(len(eligible) - 1, 1)
            dense_rank_percentile = (dense_rank[unit_id] - 1) / max(
                candidate_pool_size - 1, 1
            )
            in_original = int(rank <= inserted_count)
            boundary_fraction = float(ball["boundary_count"]) / float(ball["size"])

            candidate_trace.append(
                {
                    "candidate_budget_region": (
                        "ORIGINAL_INSERT_SET"
                        if in_original
                        else "BEYOND_ORIGINAL_BUDGET"
                    ),
                    "candidate_covered_query_facet_count": len(covered_facets),
                    "candidate_displaced_score_margin": displaced_margin,
                    "candidate_displaced_similarity": displaced_similarity,
                    "candidate_novel_query_facet_count": len(novel_facets),
                    "candidate_proposed_insert_position": (
                        protect_n + rank if rank <= insert_budget else None
                    ),
                    "candidate_rank_in_eligible_slice": rank,
                    "candidate_rank_percentile": candidate_rank_percentile,
                    "candidate_source_type": "Q25_EXPANDED_BALL",
                    "candidate_unit_id": unit_id,
                    "dataset": dataset,
                    "dense_rank_in_full_candidate_pool": dense_rank[unit_id],
                    "dense_rank_percentile": dense_rank_percentile,
                    "dense_score": float(row["dense_score"]),
                    "displaced_unit_dense_score": displaced_score,
                    "displaced_unit_id": displaced_id,
                    "displaced_unit_rank": displaced_rank,
                    "effective_k": effective_k,
                    "eligible_peer_count": len(peer_sims),
                    "facet_score": float(edge["facet_score"]),
                    "has_displaced_unit": int(displaced_id is not None),
                    "is_in_original_q25_insert_set": in_original,
                    "max_similarity_to_eligible_peers": (
                        max(peer_sims) if peer_sims else 0.0
                    ),
                    "max_similarity_to_protected_top10": max(protected_sims),
                    "mean_similarity_to_eligible_peers": (
                        float(np.mean(peer_sims)) if peer_sims else 0.0
                    ),
                    "mean_similarity_to_protected_top10": float(
                        np.mean(protected_sims)
                    ),
                    "planned_insert_budget": insert_budget,
                    "protect_n": protect_n,
                    "q25_floor_margin": float(row["dense_score"]) - config.q25_floor,
                    "q25_score": float(row["q25_score"]),
                    "query_id": query_id,
                    "rank_disagreement": (
                        dense_rank_percentile - candidate_rank_percentile
                    ),
                    "sample_id": sample_id,
                    "seed_candidate_similarity": max(seed_sims) if seed_sims else 0.0,
                    "source_ball_boundary_fraction": boundary_fraction,
                    "source_ball_compactness": float(ball["compactness"]),
                    "source_ball_id": str(ball["ball_id"]),
                    "source_ball_radius": float(ball["radius"]),
                    "source_ball_score": float(edge["ball_score"]),
                    "source_ball_size": int(ball["size"]),
                    "source_diversity": float(edge["diversity"]),
                    "source_edge_id": str(edge["edge_id"]),
                    "source_facet_term_count": len(edge["facet_terms"]),
                    "source_new_term_count": len(edge["new_terms"]),
                    "source_redundancy": float(edge["redundancy"]),
                    "source_shared_term_count": len(edge["shared_terms"]),
                    "source_units_per_new_term": float(edge["units_per_new_term"]),
                    "supporting_ball_count": 1,
                    "supporting_hyperedge_count": 1,
                    "supporting_seed_count": sum(
                        similarity >= config.min_seed_similarity
                        for similarity in seed_sims
                    ),
                }
            )

    manifest = {
        "candidate_rows": len(candidate_trace),
        "candidate_schema_version": SCHEMA_VERSION,
        "channel": "A_GOLD_FREE",
        "not_available": {
            key: {"reason": NOT_AVAILABLE_FIELDS[key], "status": "NOT_AVAILABLE"}
            for key in sorted(NOT_AVAILABLE_FIELDS)
        },
        "queries": len(query_trace),
        "query_id_sha256": hashlib.sha256(
            "\n".join(query_ids).encode("utf-8")
        ).hexdigest().upper(),
        "status": "CANDIDATE_TRACE_BUILT_PENDING_VERIFICATION",
    }
    return query_trace, candidate_trace, manifest


def _atomic_promote(output_dir: Path, artifacts: dict[str, bytes]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    targets = {name: output_dir / name for name in artifacts}
    existing = [str(path) for path in targets.values() if path.exists()]
    if existing:
        raise FileExistsError(f"Stage4D Channel A outputs already exist: {existing}")
    with tempfile.TemporaryDirectory(
        prefix="stage4d_cma_channel_a_pending_", dir=output_dir
    ) as directory:
        pending = Path(directory)
        for name, payload in artifacts.items():
            (pending / name).write_bytes(payload)
        for name, payload in artifacts.items():
            if (pending / name).read_bytes() != payload:
                raise ValueError(f"Pending Channel A bytes differ: {name}")
        promoted: list[Path] = []
        try:
            for name, target in targets.items():
                os.replace(pending / name, target)
                promoted.append(target)
        except Exception:
            for path in promoted:
                path.unlink(missing_ok=True)
            raise


def run_official_channel_a(config_path: Path, output_dir: Path) -> dict[str, Any]:
    """Future official entry point; authorization is checked before every input read."""

    require_official_channel_a_authorization()
    repo_root = Path(__file__).resolve().parents[1]
    if sha256_file(config_path) != OFFICIAL_CONFIG_SHA256:
        raise ValueError("Official Stage4D config hash differs")
    config = load_json(config_path)
    for relative_path, expected_sha in FROZEN_REPOSITORY_INPUTS.items():
        path = repo_root / relative_path
        if sha256_file(path) != expected_sha:
            raise ValueError(f"Frozen Stage4B repository input hash differs: {relative_path}")
    units_path = registered_path(str(config["inputs"]["unlabeled_units"]["path"]))
    queries_path = registered_path(str(config["inputs"]["unlabeled_queries"]["path"]))
    cache_path = registered_path(str(config["embedding_cache"]["path"]))
    for path, expected in (
        (units_path, config["inputs"]["unlabeled_units"]["sha256"]),
        (queries_path, config["inputs"]["unlabeled_queries"]["sha256"]),
        (cache_path, config["embedding_cache"]["sha256"]),
    ):
        if sha256_file(path) != str(expected):
            raise ValueError(f"Frozen Channel A input hash differs: {path}")

    units = load_jsonl(units_path)
    queries = load_jsonl(queries_path)
    with np.load(cache_path, allow_pickle=False) as cache:
        unit_embeddings = np.asarray(cache["unit_embeddings"], dtype="float32")
        query_embeddings = np.asarray(cache["query_embeddings"], dtype="float32")
        if not np.array_equal(
            cache["unit_ids"].astype(str),
            np.asarray([str(row["unit_id"]) for row in units]),
        ):
            raise ValueError("Embedding cache unit IDs differ")
        if not np.array_equal(
            cache["query_ids"].astype(str),
            np.asarray([str(row["query_id"]) for row in queries]),
        ):
            raise ValueError("Embedding cache query IDs differ")

    ranking_rows = load_jsonl(repo_root / next(
        path for path in FROZEN_REPOSITORY_INPUTS if path.endswith("rankings.jsonl")
    ))
    decision_rows = load_jsonl(repo_root / next(
        path for path in FROZEN_REPOSITORY_INPUTS if path.endswith("decisions.jsonl")
    ))
    frozen_rankings = {
        _native_string(row.get("query_id"), "ranking.query_id"): row
        for row in ranking_rows
    }
    if len(frozen_rankings) != len(ranking_rows):
        raise ValueError("Frozen ranking query IDs are not unique")
    u1_scores = {
        _native_string(row.get("query_id"), "decision.query_id"): (
            None
            if row.get("score") is None
            else _finite(row["score"], "decision.score")
        )
        for row in decision_rows
    }
    if len(u1_scores) != len(decision_rows) or set(u1_scores) != set(frozen_rankings):
        raise ValueError("Frozen decision/ranking query IDs differ or are duplicated")
    retrieval = RetrievalConfig(
        **{
            key: config["retrieval"][key]
            for key in RetrievalConfig().to_dict()
        }
    )

    first = build_channel_a_traces(
        units,
        queries,
        unit_embeddings,
        query_embeddings,
        retrieval,
        frozen_rankings=frozen_rankings,
        u1_scores=u1_scores,
    )
    second = build_channel_a_traces(
        units,
        queries,
        unit_embeddings,
        query_embeddings,
        retrieval,
        frozen_rankings=frozen_rankings,
        u1_scores=u1_scores,
    )
    first_artifacts = {
        QUERY_TRACE_NAME: render_jsonl(first[0]),
        CANDIDATE_TRACE_NAME: render_jsonl(first[1]),
        MANIFEST_NAME: render_json(first[2]),
    }
    second_artifacts = {
        QUERY_TRACE_NAME: render_jsonl(second[0]),
        CANDIDATE_TRACE_NAME: render_jsonl(second[1]),
        MANIFEST_NAME: render_json(second[2]),
    }
    if first_artifacts != second_artifacts:
        raise ValueError("Channel A deterministic rerun bytes differ")

    from stage4d_cma_candidate_trace_verifier import (
        verify_channel_a_reconstruction,
        verify_channel_a_traces,
    )

    verification = verify_channel_a_traces(first[0], first[1], first[2])
    verification["independent_reconstruction"] = verify_channel_a_reconstruction(
        units,
        queries,
        unit_embeddings,
        query_embeddings,
        retrieval,
        first[0],
        first[1],
        first[2],
    )
    first_artifacts[VERIFICATION_NAME] = render_json(verification)
    _atomic_promote(output_dir, first_artifacts)
    return first[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--official-config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_official_channel_a(args.official_config, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
