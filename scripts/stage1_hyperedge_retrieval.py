"""Hyperedge-aware granular-ball retrieval for Stage 1C.

This MVP builds unsupervised hyperedges among granular balls using title-token
overlap, center-keyword overlap, and ball-center similarity. Boundary queries
expand from seed balls to hyperedge-connected balls before ranking units.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from stage1_granular_ball_baseline import (
    build_balls_for_query,
    build_idf,
    dot,
    evaluate_query,
    load_baseline_summary,
    load_jsonl,
    retrieve_fixed_units,
    retrieve_from_balls,
    tokenize,
    vectorize,
    write_jsonl,
)


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "were",
    "who",
    "what",
    "when",
    "where",
    "which",
    "with",
}


def content_tokens(text: str) -> set[str]:
    return {token for token in tokenize(text) if len(token) > 2 and token not in STOPWORDS}


def top_terms(center: dict[str, float], n: int) -> set[str]:
    return {term for term, _ in sorted(center.items(), key=lambda item: (-item[1], item[0]))[:n]}


def enrich_balls(
    balls: list[dict[str, Any]],
    units_by_id: dict[str, dict[str, Any]],
    top_n_terms: int,
) -> None:
    for ball in balls:
        title_tokens: set[str] = set()
        gold_units = 0
        for unit_id in ball["unit_ids"]:
            unit = units_by_id[unit_id]
            title_tokens.update(content_tokens(unit.get("title", "")))
            if unit.get("is_gold"):
                gold_units += 1
        ball["title_tokens"] = title_tokens
        ball["keyword_tokens"] = top_terms(ball["center"], top_n_terms)
        ball["gold_units"] = gold_units


def build_hyperedges(
    query_id: str,
    balls: list[dict[str, Any]],
    title_overlap_min: int,
    keyword_overlap_min: int,
    center_similarity_min: float,
) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    serial = 0
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            left = balls[i]
            right = balls[j]
            title_overlap = left["title_tokens"] & right["title_tokens"]
            keyword_overlap = left["keyword_tokens"] & right["keyword_tokens"]
            center_similarity = dot(left["center"], right["center"])
            reasons = []
            if len(title_overlap) >= title_overlap_min:
                reasons.append("title_overlap")
            if len(keyword_overlap) >= keyword_overlap_min:
                reasons.append("keyword_overlap")
            if center_similarity >= center_similarity_min:
                reasons.append("center_similarity")
            if not reasons:
                continue
            edges.append(
                {
                    "edge_id": f"{query_id}::he{serial}",
                    "query_id": query_id,
                    "ball_ids": [left["ball_id"], right["ball_id"]],
                    "arity": 2,
                    "reasons": reasons,
                    "title_overlap": sorted(title_overlap),
                    "keyword_overlap": sorted(keyword_overlap),
                    "center_similarity": center_similarity,
                    "gold_units": left["gold_units"] + right["gold_units"],
                }
            )
            serial += 1
    return edges


def adjacency_from_edges(edges: list[dict[str, Any]]) -> dict[str, set[str]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        ball_ids = edge["ball_ids"]
        for left in ball_ids:
            for right in ball_ids:
                if left != right:
                    adjacency[left].add(right)
    return adjacency


def decision_from_balls(query: dict[str, Any], balls: list[dict[str, Any]], idf: dict[str, float]) -> dict[str, Any]:
    query_vector = vectorize(query["question"], idf)
    scored = sorted(((dot(query_vector, ball["center"]), ball) for ball in balls), key=lambda item: (-item[0], item[1]["ball_id"]))
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


def is_boundary_query(decision: dict[str, Any], args: argparse.Namespace) -> bool:
    return (
        decision["boundary_margin"] <= args.decision_boundary_margin
        or decision["ball_score_margin"] <= args.decision_score_margin
        or decision["top_ball_score"] < args.decision_min_ball_score
    )


def hyperedge_retrieve(
    query: dict[str, Any],
    query_units: list[dict[str, Any]],
    units_by_id: dict[str, dict[str, Any]],
    vectors: dict[str, dict[str, float]],
    idf: dict[str, float],
    balls: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    max_k: int,
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    decision = decision_from_balls(query, balls, idf)
    scored_balls = decision["scored_balls"]
    boundary = is_boundary_query(decision, args)

    if args.policy == "fallback" and boundary:
        ranked = retrieve_fixed_units(query, query_units, vectors, idf, max_k)
        return ranked, {
            **{key: value for key, value in decision.items() if key != "scored_balls"},
            "used_fallback": 1.0,
            "used_hyperedge": 0.0,
            "seed_ball_count": 0,
            "expanded_ball_count": 0,
            "candidate_unit_count": len(query_units),
        }

    seed_balls = [ball for _, ball in scored_balls[: args.seed_balls]]
    selected_ids = {ball["ball_id"] for ball in seed_balls}
    seed_ids = set(selected_ids)
    used_hyperedge = 0.0
    if boundary:
        adjacency = adjacency_from_edges(edges)
        frontier = set(seed_ids)
        for _ in range(args.expansion_hops):
            next_frontier: set[str] = set()
            for ball_id in frontier:
                for neighbor in adjacency.get(ball_id, set()):
                    if neighbor not in selected_ids:
                        next_frontier.add(neighbor)
            selected_ids.update(next_frontier)
            frontier = next_frontier
        if selected_ids != seed_ids:
            used_hyperedge = 1.0

    selected_balls = [ball for _, ball in scored_balls if ball["ball_id"] in selected_ids]
    selected_unit_ids = []
    for ball in selected_balls:
        selected_unit_ids.extend(ball["unit_ids"])
    selected_unit_set = set(selected_unit_ids)

    query_vector = vectorize(query["question"], idf)
    ranked = []
    for unit_id in selected_unit_set:
        unit = units_by_id[unit_id]
        ranked.append(
            {
                "unit_id": unit_id,
                "score": dot(query_vector, vectors[unit_id]),
                "is_gold": unit["is_gold"],
                "title": unit["title"],
                "text": unit["text"],
                "tokens": len(unit["text"].split()),
            }
        )
    ranked.sort(key=lambda row: (-row["score"], row["unit_id"]))

    if len(ranked) < max_k:
        seen = {row["unit_id"] for row in ranked}
        fixed = retrieve_fixed_units(query, query_units, vectors, idf, max_k)
        for row in fixed:
            if row["unit_id"] not in seen:
                ranked.append(row)
                seen.add(row["unit_id"])
            if len(ranked) >= max_k:
                break

    return ranked[:max_k], {
        **{key: value for key, value in decision.items() if key != "scored_balls"},
        "used_fallback": 0.0,
        "used_hyperedge": used_hyperedge,
        "seed_ball_count": len(seed_ids),
        "expanded_ball_count": max(len(selected_ids) - len(seed_ids), 0),
        "candidate_unit_count": len(selected_unit_set),
    }


def aggregate(results: list[dict[str, Any]], k_values: list[int]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in results:
        grouped[row["dataset"]].append(row)
    grouped["ALL"] = results

    summary: dict[str, Any] = {}
    for dataset, rows in grouped.items():
        item: dict[str, Any] = {"queries": len(rows)}
        item["avg_mrr"] = sum(row["mrr"] for row in rows) / max(len(rows), 1)
        item["fallback_rate"] = sum(row["used_fallback"] for row in rows) / max(len(rows), 1)
        item["hyperedge_rate"] = sum(row["used_hyperedge"] for row in rows) / max(len(rows), 1)
        item["avg_edges"] = sum(row["edge_count"] for row in rows) / max(len(rows), 1)
        item["avg_expanded_balls"] = sum(row["expanded_ball_count"] for row in rows) / max(len(rows), 1)
        item["expansion_yield"] = sum(row["expansion_gold_units"] for row in rows) / max(sum(row["expansion_units"] for row in rows), 1)
        item["false_expansion_rate"] = sum(row["expansion_non_gold_units"] for row in rows) / max(sum(row["expansion_units"] for row in rows), 1)
        for k in k_values:
            for metric in ["evidence_recall", "hit", "chain_recall", "context_units", "context_tokens"]:
                key = f"{metric}_at_{k}"
                item[key] = sum(row[key] for row in rows) / max(len(rows), 1)
        summary[dataset] = item
    return summary


def write_summary_csv(path: Path, summary: dict[str, Any], k_values: list[int]) -> None:
    fields = [
        "dataset",
        "queries",
        "avg_mrr",
        "fallback_rate",
        "hyperedge_rate",
        "avg_edges",
        "avg_expanded_balls",
        "expansion_yield",
        "false_expansion_rate",
    ]
    for k in k_values:
        fields.extend(
            [
                f"evidence_recall_at_{k}",
                f"hit_at_{k}",
                f"chain_recall_at_{k}",
                f"context_units_at_{k}",
                f"context_tokens_at_{k}",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for dataset, item in summary.items():
            writer.writerow({"dataset": dataset, **item})


def write_report(
    path: Path,
    summary: dict[str, Any],
    baseline: dict[str, dict[str, float]],
    k_values: list[int],
    args: argparse.Namespace,
) -> None:
    lines = [
        "# Stage 1C Hyperedge-Aware Retrieval Report",
        "",
        "## Material Passport",
        "",
        "- Stage: Stage 1C Retrieval-only MVP",
        "- Method: granular balls + unsupervised hyperedge expansion",
        "- Gold labels used for indexing: No",
        "- Generator used: No",
        "",
        "## Parameters",
        "",
        f"- policy: {args.policy}",
        f"- seed_balls: {args.seed_balls}",
        f"- expansion_hops: {args.expansion_hops}",
        f"- title_overlap_min: {args.title_overlap_min}",
        f"- keyword_overlap_min: {args.keyword_overlap_min}",
        f"- center_similarity_min: {args.center_similarity_min}",
        f"- decision_boundary_margin: {args.decision_boundary_margin}",
        f"- decision_score_margin: {args.decision_score_margin}",
        f"- decision_min_ball_score: {args.decision_min_ball_score}",
        "",
        "## Key Metrics",
        "",
    ]
    for dataset in sorted(summary.keys()):
        item = summary[dataset]
        lines.extend(
            [
                f"### {dataset}",
                "",
                f"- Queries: {item['queries']}",
                f"- Avg MRR: {item['avg_mrr']:.4f}",
                f"- Hyperedge trigger rate: {item['hyperedge_rate']:.4f}",
                f"- Fallback rate: {item['fallback_rate']:.4f}",
                f"- Avg hyperedges/query: {item['avg_edges']:.2f}",
                f"- Avg expanded balls/query: {item['avg_expanded_balls']:.2f}",
                f"- Expansion yield: {item['expansion_yield']:.4f}",
                f"- False expansion rate: {item['false_expansion_rate']:.4f}",
                "",
                "| k | Evidence Recall | delta vs TF-IDF | Chain Recall | delta vs TF-IDF | Avg Tokens |",
                "|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for k in k_values:
            er = item[f"evidence_recall_at_{k}"]
            cr = item[f"chain_recall_at_{k}"]
            base = baseline.get(dataset, {})
            lines.append(
                f"| {k} | {er:.4f} | {er - base.get(f'evidence_recall_at_{k}', 0.0):+.4f} | "
                f"{cr:.4f} | {cr - base.get(f'chain_recall_at_{k}', 0.0):+.4f} | "
                f"{item[f'context_tokens_at_{k}']:.2f} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Interpretation Boundary",
            "",
            "- Hyperedges are unsupervised and based only on candidate text metadata/statistics.",
            "- This is still per-query candidate retrieval, not full-corpus indexing.",
            "- The useful signal is whether boundary expansion improves chain recall without excessive false expansion.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", required=True, type=Path)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--details-output", required=True, type=Path)
    parser.add_argument("--hyperedges-output", required=True, type=Path)
    parser.add_argument("--summary-output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--baseline-summary", type=Path)
    parser.add_argument("--k", nargs="+", type=int, default=[1, 3, 5, 10, 20])
    parser.add_argument("--min-size", type=int, default=2)
    parser.add_argument("--max-size", type=int, default=3)
    parser.add_argument("--radius-threshold", type=float, default=0.78)
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--boundary-width", type=float, default=0.2)
    parser.add_argument("--top-center-terms", type=int, default=8)
    parser.add_argument("--title-overlap-min", type=int, default=1)
    parser.add_argument("--keyword-overlap-min", type=int, default=2)
    parser.add_argument("--center-similarity-min", type=float, default=0.3)
    parser.add_argument("--policy", choices=["hyperedge", "fallback"], default="hyperedge")
    parser.add_argument("--seed-balls", type=int, default=1)
    parser.add_argument("--expansion-hops", type=int, default=1)
    parser.add_argument("--decision-boundary-margin", type=float, default=0.5)
    parser.add_argument("--decision-score-margin", type=float, default=0.1)
    parser.add_argument("--decision-min-ball-score", type=float, default=0.2)
    args = parser.parse_args()

    units = load_jsonl(args.units)
    queries = load_jsonl(args.queries)
    k_values = sorted(set(args.k))
    max_k = max(k_values)

    idf = build_idf(units)
    vectors = {unit["unit_id"]: vectorize(unit["text"], idf) for unit in units}
    units_by_id = {unit["unit_id"]: unit for unit in units}
    units_by_query: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for unit in units:
        units_by_query[unit["query_id"]].append(unit)

    details: list[dict[str, Any]] = []
    all_edges: list[dict[str, Any]] = []

    for query in queries:
        query_units = units_by_query[query["query_id"]]
        unit_ids = [unit["unit_id"] for unit in query_units]
        balls = build_balls_for_query(
            query["query_id"],
            unit_ids,
            vectors,
            args.min_size,
            args.max_size,
            args.radius_threshold,
            args.max_depth,
            args.boundary_width,
        )
        enrich_balls(balls, units_by_id, args.top_center_terms)
        edges = build_hyperedges(
            query["query_id"],
            balls,
            args.title_overlap_min,
            args.keyword_overlap_min,
            args.center_similarity_min,
        )
        all_edges.extend(edges)
        ranked, decision = hyperedge_retrieve(query, query_units, units_by_id, vectors, idf, balls, edges, max_k, args)
        row = evaluate_query(query, ranked, k_values)
        row.update(decision)
        row["edge_count"] = len(edges)
        row["ball_count"] = len(balls)

        seed_count = row["seed_ball_count"]
        expanded_count = row["expanded_ball_count"]
        seed_unit_ids = set()
        expanded_unit_ids = set()
        decision_info = decision_from_balls(query, balls, idf)
        scored_balls = [ball for _, ball in decision_info["scored_balls"]]
        seed_ball_ids = {ball["ball_id"] for ball in scored_balls[: args.seed_balls]}
        adjacency = adjacency_from_edges(edges)
        selected_ball_ids = set(seed_ball_ids)
        frontier = set(seed_ball_ids)
        for _ in range(args.expansion_hops):
            next_frontier = set()
            for ball_id in frontier:
                next_frontier.update(adjacency.get(ball_id, set()) - selected_ball_ids)
            selected_ball_ids.update(next_frontier)
            frontier = next_frontier
        for ball in balls:
            if ball["ball_id"] in seed_ball_ids:
                seed_unit_ids.update(ball["unit_ids"])
            elif row["used_hyperedge"] and ball["ball_id"] in selected_ball_ids:
                expanded_unit_ids.update(ball["unit_ids"])
        row["seed_unit_count"] = len(seed_unit_ids)
        row["expansion_units"] = len(expanded_unit_ids)
        row["expansion_gold_units"] = sum(1 for unit_id in expanded_unit_ids if units_by_id[unit_id]["is_gold"])
        row["expansion_non_gold_units"] = row["expansion_units"] - row["expansion_gold_units"]
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
        row["debug_seed_count"] = seed_count
        row["debug_expanded_count"] = expanded_count
        details.append(row)

    summary = aggregate(details, k_values)
    baseline = load_baseline_summary(args.baseline_summary)
    write_jsonl(args.details_output, details)
    write_jsonl(args.hyperedges_output, all_edges)
    write_summary_csv(args.summary_output, summary, k_values)
    write_report(args.report, summary, baseline, k_values, args)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
