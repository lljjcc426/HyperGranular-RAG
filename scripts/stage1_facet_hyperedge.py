"""Facet-aware hyperedge construction for Stage 1E.

This variant builds query-conditioned hyperedges by asking whether a candidate
granular ball contributes new query facets beyond the seed balls. It is still
unsupervised: gold labels are used only for evaluation.
"""

from __future__ import annotations

import argparse
import csv
import json
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
    tokenize,
    vectorize,
    write_jsonl,
)
from stage1_hyperedge_retrieval import STOPWORDS, content_tokens, decision_from_balls, enrich_balls, is_boundary_query


def query_terms(question: str) -> set[str]:
    return {token for token in tokenize(question) if len(token) > 2 and token not in STOPWORDS}


def ball_terms(ball: dict[str, Any], units_by_id: dict[str, dict[str, Any]], top_center_terms: int) -> set[str]:
    terms: set[str] = set()
    for unit_id in ball["unit_ids"]:
        unit = units_by_id[unit_id]
        terms.update(content_tokens(unit.get("title", "")))
        terms.update(content_tokens(unit.get("text", "")))
    center_terms = {term for term, _ in sorted(ball["center"].items(), key=lambda item: (-item[1], item[0]))[:top_center_terms]}
    terms.update(center_terms)
    return terms


def enrich_facets(
    balls: list[dict[str, Any]],
    units_by_id: dict[str, dict[str, Any]],
    terms: set[str],
    top_center_terms: int,
) -> None:
    for ball in balls:
        terms_in_ball = ball_terms(ball, units_by_id, top_center_terms)
        ball["all_terms"] = terms_in_ball
        ball["facet_terms"] = terms_in_ball & terms


def select_facet_expansions(
    query: dict[str, Any],
    balls: list[dict[str, Any]],
    idf: dict[str, float],
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    decision = decision_from_balls(query, balls, idf)
    scored_balls = decision["scored_balls"]
    q_terms = query_terms(query["question"])
    seed_balls = [ball for _, ball in scored_balls[: args.seed_balls]]
    seed_ids = {ball["ball_id"] for ball in seed_balls}
    covered_terms = set().union(*(ball["facet_terms"] for ball in seed_balls)) if seed_balls else set()
    seed_vectors = [ball["center"] for ball in seed_balls]

    candidates = []
    ball_score_by_id = {ball["ball_id"]: score for score, ball in scored_balls}
    for score, ball in scored_balls:
        if ball["ball_id"] in seed_ids:
            continue
        new_terms = ball["facet_terms"] - covered_terms
        shared_terms = ball["facet_terms"] & covered_terms
        if len(new_terms) < args.min_new_terms:
            if not (args.allow_high_score_no_new and score >= args.high_score_no_new_threshold):
                continue
        max_seed_sim = max((dot(ball["center"], seed_vec) for seed_vec in seed_vectors), default=0.0)
        new_ratio = len(new_terms) / max(len(q_terms), 1)
        total_ratio = len(ball["facet_terms"]) / max(len(q_terms), 1)
        redundancy = len(shared_terms) / max(len(ball["facet_terms"]), 1)
        diversity = 1.0 - max_seed_sim
        facet_score = (
            args.w_new * new_ratio
            + args.w_total * total_ratio
            + args.w_ball * score
            + args.w_diversity * diversity
            - args.w_redundancy * redundancy
        )
        if facet_score < args.min_facet_score:
            continue
        candidates.append(
            {
                "edge_id": f"{query['query_id']}::facet::{ball['ball_id']}",
                "query_id": query["query_id"],
                "seed_ball_ids": sorted(seed_ids),
                "accepted_ball_ids": [ball["ball_id"]],
                "new_terms": sorted(new_terms),
                "shared_terms": sorted(shared_terms),
                "facet_terms": sorted(ball["facet_terms"]),
                "ball_score": score,
                "facet_score": facet_score,
                "diversity": diversity,
                "redundancy": redundancy,
                "gold_units": ball.get("gold_units", 0),
            }
        )
    candidates.sort(key=lambda row: (-row["facet_score"], row["edge_id"]))

    selected: list[dict[str, Any]] = []
    selected_ball_ids: set[str] = set()
    dynamic_budget = args.max_expanded_balls
    if args.dynamic_budget and is_boundary_query(decision, args):
        dynamic_budget = min(args.max_expanded_balls + args.boundary_extra_balls, args.max_dynamic_expanded_balls)
    for candidate in candidates:
        ball_id = candidate["accepted_ball_ids"][0]
        if ball_id in selected_ball_ids:
            continue
        if len(selected_ball_ids) >= dynamic_budget:
            break
        selected.append(candidate)
        selected_ball_ids.add(ball_id)
        covered_terms.update(candidate["new_terms"])
        if len(selected) >= args.top_facet_edges:
            break

    info = {
        **{key: value for key, value in decision.items() if key != "scored_balls"},
        "is_boundary": 1.0 if is_boundary_query(decision, args) else 0.0,
        "seed_ball_count": len(seed_ids),
        "expanded_ball_count": len(selected_ball_ids),
        "selected_edge_count": len(selected),
        "query_facet_count": len(q_terms),
        "seed_facet_count": len(set().union(*(ball["facet_terms"] for ball in seed_balls)) if seed_balls else set()),
        "final_facet_count": len(covered_terms),
    }
    return selected, info


def retrieve_with_facets(
    query: dict[str, Any],
    query_units: list[dict[str, Any]],
    units_by_id: dict[str, dict[str, Any]],
    vectors: dict[str, dict[str, float]],
    idf: dict[str, float],
    balls: list[dict[str, Any]],
    selected_edges: list[dict[str, Any]],
    max_k: int,
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    decision = decision_from_balls(query, balls, idf)
    scored_balls = decision["scored_balls"]
    seed_ball_ids = {ball["ball_id"] for _, ball in scored_balls[: args.seed_balls]}
    expanded_ball_ids = {ball_id for edge in selected_edges for ball_id in edge["accepted_ball_ids"]}
    selected_ball_ids = seed_ball_ids | expanded_ball_ids
    query_vector = vectorize(query["question"], idf)

    edge_bonus_by_ball = {ball_id: edge["facet_score"] for edge in selected_edges for ball_id in edge["accepted_ball_ids"]}
    ranked = []
    for ball in balls:
        if ball["ball_id"] not in selected_ball_ids:
            continue
        ball_bonus = edge_bonus_by_ball.get(ball["ball_id"], 0.0)
        for unit_id in ball["unit_ids"]:
            unit = units_by_id[unit_id]
            base_score = dot(query_vector, vectors[unit_id])
            score = base_score + args.w_facet_unit_bonus * ball_bonus
            ranked.append(
                {
                    "unit_id": unit_id,
                    "score": score,
                    "base_score": base_score,
                    "facet_bonus": ball_bonus,
                    "is_gold": unit["is_gold"],
                    "title": unit["title"],
                    "text": unit["text"],
                    "tokens": len(unit["text"].split()),
                }
            )
    ranked.sort(key=lambda row: (-row["score"], row["unit_id"]))

    if args.merge_fixed:
        fixed = retrieve_fixed_units(query, query_units, vectors, idf, max_k)
        by_id = {row["unit_id"]: row for row in ranked}
        for row in fixed:
            by_id.setdefault(row["unit_id"], row)
        ranked = list(by_id.values())
        ranked.sort(key=lambda row: (-row["score"], row["unit_id"]))
    elif len(ranked) < max_k and args.fill_with_fixed:
        seen = {row["unit_id"] for row in ranked}
        fixed = retrieve_fixed_units(query, query_units, vectors, idf, max_k)
        for row in fixed:
            if row["unit_id"] not in seen:
                ranked.append(row)
                seen.add(row["unit_id"])
            if len(ranked) >= max_k:
                break
    return ranked[:max_k]


def aggregate(rows: list[dict[str, Any]], k_values: list[int]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["dataset"], []).append(row)
    grouped["ALL"] = rows

    summary: dict[str, Any] = {}
    for dataset, items in grouped.items():
        denom = max(len(items), 1)
        out: dict[str, Any] = {"queries": len(items)}
        out["avg_mrr"] = sum(row["mrr"] for row in items) / denom
        out["boundary_rate"] = sum(row["is_boundary"] for row in items) / denom
        out["hyperedge_rate"] = sum(1.0 if row["selected_edge_count"] > 0 else 0.0 for row in items) / denom
        out["avg_selected_edges"] = sum(row["selected_edge_count"] for row in items) / denom
        out["avg_expanded_balls"] = sum(row["expanded_ball_count"] for row in items) / denom
        out["avg_seed_facet_count"] = sum(row["seed_facet_count"] for row in items) / denom
        out["avg_final_facet_count"] = sum(row["final_facet_count"] for row in items) / denom
        out["facet_gain"] = out["avg_final_facet_count"] - out["avg_seed_facet_count"]
        expansion_units = sum(row["expansion_units"] for row in items)
        out["expansion_yield"] = sum(row["expansion_gold_units"] for row in items) / max(expansion_units, 1)
        out["false_expansion_rate"] = sum(row["expansion_non_gold_units"] for row in items) / max(expansion_units, 1)
        for k in k_values:
            for metric in ["evidence_recall", "hit", "chain_recall", "context_units", "context_tokens"]:
                key = f"{metric}_at_{k}"
                out[key] = sum(row[key] for row in items) / denom
        summary[dataset] = out
    return summary


def write_summary_csv(path: Path, summary: dict[str, Any], k_values: list[int]) -> None:
    fields = [
        "dataset",
        "queries",
        "avg_mrr",
        "boundary_rate",
        "hyperedge_rate",
        "avg_selected_edges",
        "avg_expanded_balls",
        "avg_seed_facet_count",
        "avg_final_facet_count",
        "facet_gain",
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


def write_report(path: Path, summary: dict[str, Any], baseline: dict[str, dict[str, float]], k_values: list[int], args: argparse.Namespace) -> None:
    lines = [
        "# Stage 1E Facet-Aware Hyperedge Retrieval Report",
        "",
        "## Material Passport",
        "",
        "- Stage: Stage 1E Retrieval-only MVP",
        "- Method: granular balls + facet-aware hyperedge construction",
        "- Gold labels used for indexing: No",
        "- Generator used: No",
        "",
        "## Parameters",
        "",
        f"- seed_balls: {args.seed_balls}",
        f"- top_facet_edges: {args.top_facet_edges}",
        f"- max_expanded_balls: {args.max_expanded_balls}",
        f"- min_new_terms: {args.min_new_terms}",
        f"- min_facet_score: {args.min_facet_score}",
        f"- fill_with_fixed: {args.fill_with_fixed}",
        f"- merge_fixed: {args.merge_fixed}",
        "",
        "## Key Metrics",
        "",
    ]
    for dataset in sorted(summary):
        item = summary[dataset]
        lines.extend(
            [
                f"### {dataset}",
                "",
                f"- Queries: {item['queries']}",
                f"- Hyperedge trigger rate: {item['hyperedge_rate']:.4f}",
                f"- Avg selected edges/query: {item['avg_selected_edges']:.2f}",
                f"- Avg expanded balls/query: {item['avg_expanded_balls']:.2f}",
                f"- Avg facet gain/query: {item['facet_gain']:.2f}",
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", required=True, type=Path)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--details-output", required=True, type=Path)
    parser.add_argument("--facet-edges-output", required=True, type=Path)
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
    parser.add_argument("--seed-balls", type=int, default=2)
    parser.add_argument("--top-facet-edges", type=int, default=3)
    parser.add_argument("--max-expanded-balls", type=int, default=3)
    parser.add_argument("--min-new-terms", type=int, default=1)
    parser.add_argument("--min-facet-score", type=float, default=0.10)
    parser.add_argument("--allow-high-score-no-new", action="store_true")
    parser.add_argument("--high-score-no-new-threshold", type=float, default=0.25)
    parser.add_argument("--dynamic-budget", action="store_true")
    parser.add_argument("--boundary-extra-balls", type=int, default=1)
    parser.add_argument("--max-dynamic-expanded-balls", type=int, default=5)
    parser.add_argument("--decision-boundary-margin", type=float, default=0.50)
    parser.add_argument("--decision-score-margin", type=float, default=0.10)
    parser.add_argument("--decision-min-ball-score", type=float, default=0.20)
    parser.add_argument("--w-new", type=float, default=0.45)
    parser.add_argument("--w-total", type=float, default=0.20)
    parser.add_argument("--w-ball", type=float, default=0.20)
    parser.add_argument("--w-diversity", type=float, default=0.15)
    parser.add_argument("--w-redundancy", type=float, default=0.20)
    parser.add_argument("--w-facet-unit-bonus", type=float, default=0.0)
    parser.add_argument("--fill-with-fixed", action="store_true")
    parser.add_argument("--merge-fixed", action="store_true")
    args = parser.parse_args()

    units = load_jsonl(args.units)
    queries = load_jsonl(args.queries)
    k_values = sorted(set(args.k))
    max_k = max(k_values)
    idf = build_idf(units)
    vectors = {unit["unit_id"]: vectorize(unit["text"], idf) for unit in units}
    units_by_id = {unit["unit_id"]: unit for unit in units}
    units_by_query: dict[str, list[dict[str, Any]]] = {}
    for unit in units:
        units_by_query.setdefault(unit["query_id"], []).append(unit)

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
        enrich_facets(balls, units_by_id, query_terms(query["question"]), args.top_center_terms)
        selected_edges, info = select_facet_expansions(query, balls, idf, args)
        ranked = retrieve_with_facets(query, query_units, units_by_id, vectors, idf, balls, selected_edges, max_k, args)
        row = evaluate_query(query, ranked, k_values)
        row.update(info)

        expanded_ball_ids = {ball_id for edge in selected_edges for ball_id in edge["accepted_ball_ids"]}
        expanded_unit_ids = {
            unit_id
            for ball in balls
            if ball["ball_id"] in expanded_ball_ids
            for unit_id in ball["unit_ids"]
        }
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
        details.append(row)
        all_edges.extend(selected_edges)

    summary = aggregate(details, k_values)
    baseline = load_baseline_summary(args.baseline_summary)
    write_jsonl(args.details_output, details)
    write_jsonl(args.facet_edges_output, all_edges)
    write_summary_csv(args.summary_output, summary, k_values)
    write_report(args.report, summary, baseline, k_values, args)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
