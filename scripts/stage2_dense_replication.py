"""Dense-embedding replication for the hyper-granular-ball RAG Stage2B.

Uses a Hugging Face transformer with mean pooling. This script is intentionally
self-contained and does not depend on sklearn or sentence-transformers.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer


TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "is", "it", "of",
    "on", "or", "that", "the", "to", "was", "were", "who", "what", "when", "where", "which", "with",
}


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def content_tokens(text: str) -> set[str]:
    return {token for token in tokenize(text) if len(token) > 2 and token not in STOPWORDS}


def query_terms(question: str) -> set[str]:
    return content_tokens(question)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def normalize_matrix(x: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return x / norms


def normalize_vec(x: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(x))
    if norm == 0.0:
        return x
    return x / norm


def mean_pool(last_hidden: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    mask = attention_mask.unsqueeze(-1).expand(last_hidden.size()).float()
    summed = torch.sum(last_hidden * mask, dim=1)
    counts = torch.clamp(mask.sum(dim=1), min=1e-9)
    return summed / counts


def embed_texts(texts: list[str], model_name: str, batch_size: int, max_length: int) -> np.ndarray:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    chunks: list[np.ndarray] = []
    with torch.no_grad():
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            encoded = tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=max_length,
                return_tensors="pt",
            )
            encoded = {key: value.to(device) for key, value in encoded.items()}
            output = model(**encoded)
            pooled = mean_pool(output.last_hidden_state, encoded["attention_mask"])
            pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
            chunks.append(pooled.cpu().numpy().astype("float32"))
            print(f"embedded {min(start + batch_size, len(texts))}/{len(texts)}")
    return np.vstack(chunks)


def load_or_build_embeddings(
    cache_path: Path,
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    model_name: str,
    batch_size: int,
    max_length: int,
) -> tuple[np.ndarray, np.ndarray]:
    if cache_path.exists():
        data = np.load(cache_path)
        return data["unit_embeddings"], data["query_embeddings"]
    unit_texts = [(unit.get("title", "") + ". " + unit.get("text", "")).strip() for unit in units]
    query_texts = [query["question"] for query in queries]
    unit_embeddings = embed_texts(unit_texts, model_name, batch_size, max_length)
    query_embeddings = embed_texts(query_texts, model_name, batch_size, max_length)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        cache_path,
        unit_embeddings=unit_embeddings.astype("float32"),
        query_embeddings=query_embeddings.astype("float32"),
        model_name=np.array([model_name]),
    )
    return unit_embeddings, query_embeddings


def dot(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))


def centroid(indices: list[int], embeddings: np.ndarray) -> np.ndarray:
    if not indices:
        return np.zeros((embeddings.shape[1],), dtype="float32")
    return normalize_vec(np.mean(embeddings[indices], axis=0).astype("float32"))


def describe_ball(ball_id: str, query_id: str, indices: list[int], center: np.ndarray, embeddings: np.ndarray, depth: int, boundary_width: float) -> dict[str, Any]:
    distances = [1.0 - dot(embeddings[index], center) for index in indices]
    radius = max(distances) if distances else 0.0
    mean_distance = sum(distances) / max(len(distances), 1)
    threshold = radius * (1.0 - boundary_width)
    boundary_count = sum(1 for distance in distances if radius > 0 and distance >= threshold)
    return {
        "ball_id": ball_id,
        "query_id": query_id,
        "indices": indices,
        "center": center,
        "size": len(indices),
        "radius": radius,
        "mean_distance": mean_distance,
        "compactness": 1.0 - mean_distance,
        "boundary_count": boundary_count,
        "depth": depth,
    }


def split_ball(indices: list[int], embeddings: np.ndarray, center: np.ndarray) -> tuple[list[int], list[int]]:
    if len(indices) < 2:
        return indices, []
    seed_a = max(indices, key=lambda idx: 1.0 - dot(embeddings[idx], center))
    seed_b = min(indices, key=lambda idx: dot(embeddings[idx], embeddings[seed_a]))
    if seed_a == seed_b:
        mid = len(indices) // 2
        return indices[:mid], indices[mid:]
    left, right = [], []
    for idx in indices:
        if dot(embeddings[idx], embeddings[seed_a]) >= dot(embeddings[idx], embeddings[seed_b]):
            left.append(idx)
        else:
            right.append(idx)
    if not left or not right:
        mid = len(indices) // 2
        return indices[:mid], indices[mid:]
    return left, right


def build_balls(query_id: str, indices: list[int], embeddings: np.ndarray, min_size: int, max_size: int, radius_threshold: float, max_depth: int, boundary_width: float) -> list[dict[str, Any]]:
    balls: list[dict[str, Any]] = []
    serial = 0

    def recurse(current: list[int], depth: int) -> None:
        nonlocal serial
        center = centroid(current, embeddings)
        temp = describe_ball(f"{query_id}::dball{serial}", query_id, current, center, embeddings, depth, boundary_width)
        should_split = (
            depth < max_depth
            and len(current) >= 2 * min_size
            and (len(current) > max_size or temp["radius"] > radius_threshold)
        )
        if should_split:
            left, right = split_ball(current, embeddings, center)
            if len(left) >= min_size and len(right) >= min_size:
                recurse(left, depth + 1)
                recurse(right, depth + 1)
                return
        serial += 1
        balls.append(temp)

    recurse(indices, 0)
    return balls


def enrich_balls(balls: list[dict[str, Any]], units: list[dict[str, Any]], top_terms: int) -> None:
    for ball in balls:
        terms = set()
        gold_units = 0
        for idx in ball["indices"]:
            unit = units[idx]
            terms.update(content_tokens(unit.get("title", "")))
            terms.update(content_tokens(unit.get("text", "")))
            if unit.get("is_gold"):
                gold_units += 1
        ball["all_terms"] = terms
        ball["gold_units"] = gold_units


def enrich_facets(balls: list[dict[str, Any]], q_terms: set[str]) -> None:
    for ball in balls:
        ball["facet_terms"] = ball["all_terms"] & q_terms


def decision_from_balls(query_embedding: np.ndarray, balls: list[dict[str, Any]]) -> dict[str, Any]:
    scored = sorted(((dot(query_embedding, ball["center"]), ball) for ball in balls), key=lambda item: (-item[0], item[1]["ball_id"]))
    top_score = scored[0][0] if scored else 0.0
    second_score = scored[1][0] if len(scored) > 1 else -1.0
    top_ball = scored[0][1] if scored else None
    top_distance = 1.0 - top_score
    top_radius = top_ball["radius"] if top_ball is not None else 0.0
    boundary_margin = abs(top_radius - top_distance) / (top_radius + 1e-9) if top_radius > 0 else 999.0
    return {
        "scored_balls": scored,
        "top_ball_score": top_score,
        "ball_score_margin": top_score - second_score,
        "top_ball_radius": top_radius,
        "query_to_top_ball_distance": top_distance,
        "boundary_margin": boundary_margin,
    }


def is_boundary(decision: dict[str, Any], args: argparse.Namespace) -> bool:
    return (
        decision["boundary_margin"] <= args.decision_boundary_margin
        or decision["ball_score_margin"] <= args.decision_score_margin
        or decision["top_ball_score"] < args.decision_min_ball_score
    )


def fixed_retrieve(query_embedding: np.ndarray, candidate_indices: list[int], units: list[dict[str, Any]], embeddings: np.ndarray, max_k: int) -> list[dict[str, Any]]:
    ranked = []
    for idx in candidate_indices:
        unit = units[idx]
        ranked.append(
            {
                "unit_index": idx,
                "unit_id": unit["unit_id"],
                "score": dot(query_embedding, embeddings[idx]),
                "is_gold": unit["is_gold"],
                "title": unit["title"],
                "text": unit["text"],
                "tokens": len(unit["text"].split()),
            }
        )
    ranked.sort(key=lambda row: (-row["score"], row["unit_id"]))
    return ranked[:max_k]


def select_facet_edges(query: dict[str, Any], query_embedding: np.ndarray, balls: list[dict[str, Any]], args: argparse.Namespace, gated: bool) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    decision = decision_from_balls(query_embedding, balls)
    boundary = is_boundary(decision, args)
    scored_balls = decision["scored_balls"]
    q_terms = query_terms(query["question"])
    seed_balls = [ball for _, ball in scored_balls[: args.seed_balls]]
    seed_ids = {ball["ball_id"] for ball in seed_balls}
    covered = set().union(*(ball["facet_terms"] for ball in seed_balls)) if seed_balls else set()
    seed_centers = [ball["center"] for ball in seed_balls]

    candidates = []
    reject_counts = Counter()
    for score, ball in scored_balls:
        if ball["ball_id"] in seed_ids:
            continue
        new_terms = ball["facet_terms"] - covered
        shared_terms = ball["facet_terms"] & covered
        if len(new_terms) < args.min_new_terms:
            continue
        max_seed_sim = max((dot(ball["center"], center) for center in seed_centers), default=0.0)
        ball_size = len(ball["indices"])
        units_per_new_term = ball_size / max(len(new_terms), 1)
        redundancy = len(shared_terms) / max(len(ball["facet_terms"]), 1)
        if gated:
            if args.expand_boundary_only and not boundary:
                continue
            if args.max_candidate_ball_size > 0 and ball_size > args.max_candidate_ball_size:
                reject_counts["gate_reject_size"] += 1
                continue
            if not (score >= args.min_ball_score or max_seed_sim >= args.min_seed_similarity):
                reject_counts["gate_reject_anchor"] += 1
                continue
            if args.max_units_per_new_term > 0 and units_per_new_term > args.max_units_per_new_term:
                reject_counts["gate_reject_ratio"] += 1
                continue
            if redundancy > args.max_redundancy:
                reject_counts["gate_reject_redundancy"] += 1
                continue
        diversity = 1.0 - max_seed_sim
        new_ratio = len(new_terms) / max(len(q_terms), 1)
        total_ratio = len(ball["facet_terms"]) / max(len(q_terms), 1)
        size_penalty = ball_size / max(args.max_candidate_ball_size, 1) if gated and args.max_candidate_ball_size > 0 else 0.0
        facet_score = (
            args.w_new * new_ratio
            + args.w_total * total_ratio
            + args.w_ball * score
            + args.w_diversity * diversity
            - args.w_redundancy * redundancy
            - (args.w_size * size_penalty if gated else 0.0)
        )
        if facet_score < args.min_facet_score:
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
                "max_seed_similarity": max_seed_sim,
                "gold_units": ball["gold_units"],
            }
        )
    candidates.sort(key=lambda row: (-row["facet_score"], row["edge_id"]))
    selected = []
    selected_ids = set()
    for candidate in candidates:
        ball_id = candidate["accepted_ball_ids"][0]
        if ball_id in selected_ids:
            continue
        if len(selected_ids) >= args.max_expanded_balls:
            break
        selected.append(candidate)
        selected_ids.add(ball_id)
        covered.update(candidate["new_terms"])
        if len(selected) >= args.top_facet_edges:
            break
    info = {
        **{key: value for key, value in decision.items() if key != "scored_balls"},
        "is_boundary": 1.0 if boundary else 0.0,
        "seed_ball_count": len(seed_ids),
        "expanded_ball_count": len(selected_ids),
        "selected_edge_count": len(selected),
        "query_facet_count": len(q_terms),
        "seed_facet_count": len(set().union(*(ball["facet_terms"] for ball in seed_balls)) if seed_balls else set()),
        "final_facet_count": len(covered),
        "gate_reject_size": reject_counts["gate_reject_size"],
        "gate_reject_anchor": reject_counts["gate_reject_anchor"],
        "gate_reject_ratio": reject_counts["gate_reject_ratio"],
        "gate_reject_redundancy": reject_counts["gate_reject_redundancy"],
        "gate_reject_score": reject_counts["gate_reject_score"],
    }
    return selected, info


def retrieve_from_selected_balls(
    query_embedding: np.ndarray,
    balls: list[dict[str, Any]],
    selected_edges: list[dict[str, Any]],
    units: list[dict[str, Any]],
    embeddings: np.ndarray,
    max_k: int,
    args: argparse.Namespace,
    candidate_indices: list[int] | None = None,
) -> list[dict[str, Any]]:
    decision = decision_from_balls(query_embedding, balls)
    scored_balls = decision["scored_balls"]
    seed_ids = {ball["ball_id"] for _, ball in scored_balls[: args.seed_balls]}
    expanded_ids = {ball_id for edge in selected_edges for ball_id in edge["accepted_ball_ids"]}
    selected_ids = seed_ids | expanded_ids
    bonus_by_ball = {ball_id: edge["facet_score"] for edge in selected_edges for ball_id in edge["accepted_ball_ids"]}
    ranked = []
    for ball in balls:
        if ball["ball_id"] not in selected_ids:
            continue
        bonus = bonus_by_ball.get(ball["ball_id"], 0.0)
        for idx in ball["indices"]:
            unit = units[idx]
            base = dot(query_embedding, embeddings[idx])
            ranked.append(
                {
                    "unit_index": idx,
                    "unit_id": unit["unit_id"],
                    "score": base + args.w_facet_unit_bonus * bonus,
                    "base_score": base,
                    "facet_bonus": bonus,
                    "is_gold": unit["is_gold"],
                    "title": unit["title"],
                    "text": unit["text"],
                    "tokens": len(unit["text"].split()),
                }
            )
    ranked.sort(key=lambda row: (-row["score"], row["unit_id"]))
    fixed_ranked = fixed_retrieve(query_embedding, candidate_indices, units, embeddings, max_k) if candidate_indices else []
    if args.merge_fixed:
        merged_by_unit = {row["unit_id"]: row for row in ranked}
        for row in fixed_ranked:
            merged_by_unit.setdefault(row["unit_id"], row)
        ranked = sorted(merged_by_unit.values(), key=lambda row: (-row["score"], row["unit_id"]))
    elif args.protect_fixed_top_n > 0:
        protected = fixed_ranked[: args.protect_fixed_top_n]
        seen = {row["unit_id"] for row in protected}
        protected.extend(row for row in ranked if row["unit_id"] not in seen)
        ranked = protected
    if args.fill_with_fixed:
        seen = {row["unit_id"] for row in ranked}
        ranked.extend(row for row in fixed_ranked if row["unit_id"] not in seen)
    return ranked[:max_k]


def evaluate_query(query: dict[str, Any], ranked: list[dict[str, Any]], k_values: list[int]) -> dict[str, Any]:
    gold = set(query["gold_unit_ids"])
    row: dict[str, Any] = {
        "query_id": query["query_id"],
        "dataset": query["dataset"],
        "num_gold": len(gold),
        "num_candidates": query["num_candidate_units"],
    }
    first_gold_rank = None
    for rank, item in enumerate(ranked, start=1):
        if item["unit_id"] in gold:
            first_gold_rank = rank
            break
    row["mrr"] = 1.0 / first_gold_rank if first_gold_rank else 0.0
    for k in k_values:
        top = ranked[:k]
        retrieved_gold = {item["unit_id"] for item in top if item["unit_id"] in gold}
        row[f"evidence_recall_at_{k}"] = len(retrieved_gold) / max(len(gold), 1)
        row[f"hit_at_{k}"] = 1.0 if retrieved_gold else 0.0
        row[f"chain_recall_at_{k}"] = 1.0 if gold and gold.issubset(retrieved_gold) else 0.0
        row[f"context_units_at_{k}"] = len(top)
        row[f"context_tokens_at_{k}"] = sum(item["tokens"] for item in top)
    row["top_units"] = [
        {
            "rank": rank,
            "unit_id": item["unit_id"],
            "score": item["score"],
            "is_gold": item["is_gold"],
            "title": item["title"],
        }
        for rank, item in enumerate(ranked, start=1)
    ]
    return row


def aggregate(rows: list[dict[str, Any]], k_values: list[int]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["dataset"], []).append(row)
    grouped["ALL"] = rows
    summary = {}
    for dataset, items in grouped.items():
        denom = max(len(items), 1)
        out: dict[str, Any] = {"queries": len(items), "avg_mrr": sum(row["mrr"] for row in items) / denom}
        optional = [
            "boundary_rate", "hyperedge_rate", "avg_selected_edges", "avg_expanded_balls",
            "facet_gain", "expansion_yield", "false_expansion_rate",
            "gate_reject_size", "gate_reject_anchor", "gate_reject_ratio", "gate_reject_redundancy", "gate_reject_score",
        ]
        out["boundary_rate"] = sum(row.get("is_boundary", 0.0) for row in items) / denom
        out["hyperedge_rate"] = sum(1.0 if row.get("selected_edge_count", 0) > 0 else 0.0 for row in items) / denom
        out["avg_selected_edges"] = sum(row.get("selected_edge_count", 0) for row in items) / denom
        out["avg_expanded_balls"] = sum(row.get("expanded_ball_count", 0) for row in items) / denom
        out["facet_gain"] = (
            sum(row.get("final_facet_count", 0) for row in items) / denom
            - sum(row.get("seed_facet_count", 0) for row in items) / denom
        )
        expansion_units = sum(row.get("expansion_units", 0) for row in items)
        out["expansion_yield"] = sum(row.get("expansion_gold_units", 0) for row in items) / max(expansion_units, 1)
        out["false_expansion_rate"] = sum(row.get("expansion_non_gold_units", 0) for row in items) / max(expansion_units, 1)
        for key in ["gate_reject_size", "gate_reject_anchor", "gate_reject_ratio", "gate_reject_redundancy", "gate_reject_score"]:
            out[key] = sum(row.get(key, 0) for row in items) / denom
        for k in k_values:
            for metric in ["evidence_recall", "hit", "chain_recall", "context_units", "context_tokens"]:
                key = f"{metric}_at_{k}"
                out[key] = sum(row[key] for row in items) / denom
        summary[dataset] = out
    return summary


def write_summary(path: Path, summary: dict[str, dict[str, Any]], k_values: list[int]) -> None:
    fields = [
        "dataset", "queries", "avg_mrr", "boundary_rate", "hyperedge_rate", "avg_selected_edges",
        "avg_expanded_balls", "facet_gain", "expansion_yield", "false_expansion_rate",
        "gate_reject_size", "gate_reject_anchor", "gate_reject_ratio", "gate_reject_redundancy", "gate_reject_score",
    ]
    for k in k_values:
        fields.extend([f"evidence_recall_at_{k}", f"hit_at_{k}", f"chain_recall_at_{k}", f"context_units_at_{k}", f"context_tokens_at_{k}"])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for dataset, item in summary.items():
            writer.writerow({"dataset": dataset, **item})


def run_method(method: str, units: list[dict[str, Any]], queries: list[dict[str, Any]], unit_embeddings: np.ndarray, query_embeddings: np.ndarray, args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    k_values = sorted(set(args.k))
    max_k = max(k_values)
    unit_index_by_id = {unit["unit_id"]: idx for idx, unit in enumerate(units)}
    unit_indices_by_query: dict[str, list[int]] = defaultdict(list)
    for idx, unit in enumerate(units):
        unit_indices_by_query[unit["query_id"]].append(idx)
    query_index_by_id = {query["query_id"]: idx for idx, query in enumerate(queries)}
    details = []
    edges = []
    for query in queries:
        q_emb = query_embeddings[query_index_by_id[query["query_id"]]]
        candidate_indices = unit_indices_by_query[query["query_id"]]
        if method == "fixed":
            ranked = fixed_retrieve(q_emb, candidate_indices, units, unit_embeddings, max_k)
            row = evaluate_query(query, ranked, k_values)
        else:
            balls = build_balls(
                query["query_id"], candidate_indices, unit_embeddings, args.min_size, args.max_size,
                args.radius_threshold, args.max_depth, args.boundary_width,
            )
            enrich_balls(balls, units, args.top_center_terms)
            enrich_facets(balls, query_terms(query["question"]))
            if method == "ball":
                decision = decision_from_balls(q_emb, balls)
                ranked = retrieve_from_selected_balls(q_emb, balls, [], units, unit_embeddings, max_k, args, candidate_indices)
                row = evaluate_query(query, ranked, k_values)
                row.update({key: value for key, value in decision.items() if key != "scored_balls"})
                row.update({"is_boundary": 1.0 if is_boundary(decision, args) else 0.0, "selected_edge_count": 0, "expanded_ball_count": 0, "seed_facet_count": 0, "final_facet_count": 0})
            else:
                selected, info = select_facet_edges(query, q_emb, balls, args, gated=(method == "gated"))
                ranked = retrieve_from_selected_balls(q_emb, balls, selected, units, unit_embeddings, max_k, args, candidate_indices)
                row = evaluate_query(query, ranked, k_values)
                row.update(info)
                expanded_ball_ids = {ball_id for edge in selected for ball_id in edge["accepted_ball_ids"]}
                expanded_indices = {idx for ball in balls if ball["ball_id"] in expanded_ball_ids for idx in ball["indices"]}
                row["expansion_units"] = len(expanded_indices)
                row["expansion_gold_units"] = sum(1 for idx in expanded_indices if units[idx]["is_gold"])
                row["expansion_non_gold_units"] = row["expansion_units"] - row["expansion_gold_units"]
                edges.extend(selected)
        details.append(row)
    return details, edges, aggregate(details, k_values)


def write_report(path: Path, summaries: dict[str, dict[str, dict[str, Any]]], args: argparse.Namespace) -> None:
    lines = [
        "# Stage2B Dense Embedding Replication Report",
        "",
        "## Material Passport",
        "",
        "- Stage: Stage2B dense replication",
        f"- Embedding model: {args.model_name}",
        "- Sentence embedding: transformer mean pooling over title + text for units; question for queries",
        "- Gold labels used for indexing: No",
        "- Generator used: No",
        "- Environment note: transformers loaded with NumPy/numexpr compatibility warnings in this environment; metrics below are produced by completed runs.",
        "",
        "## ALL Summary",
        "",
        "| Method | ER@5 | CR@5 | ER@10 | CR@10 | HE rate | Yield | False expansion |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for method in ["fixed", "ball", "facet", "gated"]:
        item = summaries[method]["ALL"]
        lines.append(
            f"| dense_{method} | {item['evidence_recall_at_5']:.4f} | {item['chain_recall_at_5']:.4f} | "
            f"{item['evidence_recall_at_10']:.4f} | {item['chain_recall_at_10']:.4f} | "
            f"{item['hyperedge_rate']:.4f} | {item['expansion_yield']:.4f} | {item['false_expansion_rate']:.4f} |"
        )
    lines.extend(["", "## Dataset Split", "", "| Dataset | Method | ER@10 | CR@10 | False expansion |", "|---|---|---:|---:|---:|"])
    for dataset in ["hotpotqa", "musique"]:
        for method in ["fixed", "ball", "facet", "gated"]:
            item = summaries[method][dataset]
            lines.append(f"| {dataset} | dense_{method} | {item['evidence_recall_at_10']:.4f} | {item['chain_recall_at_10']:.4f} | {item['false_expansion_rate']:.4f} |")
    lines.extend([
        "",
        "## Reading Notes",
        "",
        "- This is a replication in dense embedding space, not a replacement for the TF-IDF experiments.",
        "- If dense_fixed is already much stronger than TF-IDF, method claims must be phrased as gains over the dense baseline, not only over TF-IDF.",
        "- If dense_gated preserves dense_facet CR@10 while lowering false expansion, Stage1F's noise-control claim generalizes across vector spaces.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", required=True, type=Path)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--output-prefix", required=True, type=Path)
    parser.add_argument("--embedding-cache", required=True, type=Path)
    parser.add_argument("--model-name", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--max-length", type=int, default=192)
    parser.add_argument("--k", nargs="+", type=int, default=[1, 3, 5, 10, 20])
    parser.add_argument("--min-size", type=int, default=2)
    parser.add_argument("--max-size", type=int, default=3)
    parser.add_argument("--radius-threshold", type=float, default=0.78)
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--boundary-width", type=float, default=0.2)
    parser.add_argument("--top-center-terms", type=int, default=8)
    parser.add_argument("--seed-balls", type=int, default=2)
    parser.add_argument("--top-facet-edges", type=int, default=2)
    parser.add_argument("--max-expanded-balls", type=int, default=2)
    parser.add_argument("--min-new-terms", type=int, default=1)
    parser.add_argument("--min-facet-score", type=float, default=0.10)
    parser.add_argument("--decision-boundary-margin", type=float, default=0.50)
    parser.add_argument("--decision-score-margin", type=float, default=0.10)
    parser.add_argument("--decision-min-ball-score", type=float, default=0.20)
    parser.add_argument("--expand-boundary-only", action="store_true")
    parser.add_argument("--max-candidate-ball-size", type=int, default=8)
    parser.add_argument("--min-ball-score", type=float, default=0.12)
    parser.add_argument("--min-seed-similarity", type=float, default=0.05)
    parser.add_argument("--max-units-per-new-term", type=float, default=6.0)
    parser.add_argument("--max-redundancy", type=float, default=0.90)
    parser.add_argument("--w-new", type=float, default=0.45)
    parser.add_argument("--w-total", type=float, default=0.20)
    parser.add_argument("--w-ball", type=float, default=0.20)
    parser.add_argument("--w-diversity", type=float, default=0.15)
    parser.add_argument("--w-redundancy", type=float, default=0.20)
    parser.add_argument("--w-size", type=float, default=0.05)
    parser.add_argument("--w-facet-unit-bonus", type=float, default=0.0)
    parser.add_argument("--fill-with-fixed", action="store_true")
    parser.add_argument("--merge-fixed", action="store_true")
    parser.add_argument("--protect-fixed-top-n", type=int, default=0)
    args = parser.parse_args()

    units = load_jsonl(args.units)
    queries = load_jsonl(args.queries)
    unit_embeddings, query_embeddings = load_or_build_embeddings(args.embedding_cache, units, queries, args.model_name, args.batch_size, args.max_length)
    unit_embeddings = normalize_matrix(unit_embeddings.astype("float32"))
    query_embeddings = normalize_matrix(query_embeddings.astype("float32"))

    summaries = {}
    for method in ["fixed", "ball", "facet", "gated"]:
        print(f"running dense_{method}")
        details, edges, summary = run_method(method, units, queries, unit_embeddings, query_embeddings, args)
        summaries[method] = summary
        write_jsonl(args.output_prefix.parent / f"{args.output_prefix.name}_{method}_details.jsonl", details)
        if edges:
            write_jsonl(args.output_prefix.parent / f"{args.output_prefix.name}_{method}_edges.jsonl", edges)
        write_summary(args.output_prefix.parent / f"{args.output_prefix.name}_{method}_summary.csv", summary, sorted(set(args.k)))
    write_report(args.output_prefix.parent / f"{args.output_prefix.name}_report.md", summaries, args)
    print(json.dumps({method: summaries[method]["ALL"] for method in summaries}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
