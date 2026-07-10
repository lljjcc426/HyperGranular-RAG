"""Query-aware hyperedge expansion for Stage 1D.

Compared with Stage 1C, this script scores candidate hyperedges with the query
before expansion and applies an explicit expansion budget.
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
from stage1_hyperedge_retrieval import (
    STOPWORDS,
    build_hyperedges,
    content_tokens,
    decision_from_balls,
    enrich_balls,
    is_boundary_query,
)


def query_tokens(question: str) -> set[str]:
    return {token for token in tokenize(question) if len(token) > 2 and token not in STOPWORDS}


def edge_query_score(
    edge: dict[str, Any],
    query_terms: set[str],
    ball_scores: dict[str, float],
    args: argparse.Namespace,
) -> float:
    title_terms = set(edge.get("title_overlap", []))
    keyword_terms = set(edge.get("keyword_overlap", []))
    edge_terms = title_terms | keyword_terms
    query_match = len(edge_terms & query_terms) / max(len(query_terms), 1)
    title_score = min(len(title_terms) / max(args.title_norm, 1), 1.0)
    keyword_score = min(len(keyword_terms) / max(args.keyword_norm, 1), 1.0)
    center_score = float(edge.get("center_similarity", 0.0))
    incident_ball_score = max(ball_scores.get(ball_id, 0.0) for ball_id in edge.get("ball_ids", []))
    return (
        args.w_query * query_match
        + args.w_title * title_score
        + args.w_keyword * keyword_score
        + args.w_center * center_score
        + args.w_ball * incident_ball_score
    )


def select_expansion_balls(
    seed_ball_ids: set[str],
    edges: list[dict[str, Any]],
    query_terms: set[str],
    ball_scores: dict[str, float],
    args: argparse.Namespace,
) -> tuple[set[str], list[dict[str, Any]]]:
    candidate_edges = []
    for edge in edges:
        edge_ball_ids = set(edge["ball_ids"])
        if not (edge_ball_ids & seed_ball_ids):
            continue
        new_ball_ids = sorted(edge_ball_ids - seed_ball_ids)
        if not new_ball_ids:
            continue
        score = edge_query_score(edge, query_terms, ball_scores, args)
        if score < args.min_edge_score:
            continue
        candidate_edges.append((score, edge, new_ball_ids))

    candidate_edges.sort(key=lambda item: (-item[0], item[1]["edge_id"]))
    expanded_ball_ids: set[str] = set()
    selected_edges: list[dict[str, Any]] = []
    for score, edge, new_ball_ids in candidate_edges[: args.top_edges]:
        accepted = []
        for ball_id in new_ball_ids:
            if ball_id in expanded_ball_ids:
                continue
            if len(expanded_ball_ids) >= args.max_expanded_balls:
                break
            expanded_ball_ids.add(ball_id)
            accepted.append(ball_id)
        if accepted:
            selected_edge = dict(edge)
            selected_edge["query_aware_score"] = score
            selected_edge["accepted_ball_ids"] = accepted
            selected_edges.append(selected_edge)
        if len(expanded_ball_ids) >= args.max_expanded_balls:
            break
    return expanded_ball_ids, selected_edges


def retrieve_query_aware(
    query: dict[str, Any],
    query_units: list[dict[str, Any]],
    units_by_id: dict[str, dict[str, Any]],
    vectors: dict[str, dict[str, float]],
    idf: dict[str, float],
    balls: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    max_k: int,
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    decision = decision_from_balls(query, balls, idf)
    scored_balls = decision["scored_balls"]
    boundary = is_boundary_query(decision, args)
    seed_balls = [ball for _, ball in scored_balls[: args.seed_balls]]
    seed_ball_ids = {ball["ball_id"] for ball in seed_balls}
    ball_scores = {ball["ball_id"]: score for score, ball in scored_balls}

    expanded_ball_ids: set[str] = set()
    selected_edges: list[dict[str, Any]] = []
    if boundary:
        expanded_ball_ids, selected_edges = select_expansion_balls(
            seed_ball_ids,
            edges,
            query_tokens(query["question"]),
            ball_scores,
            args,
        )

    selected_ball_ids = seed_ball_ids | expanded_ball_ids
    selected_unit_ids = []
    for ball in balls:
        if ball["ball_id"] in selected_ball_ids:
            selected_unit_ids.extend(ball["unit_ids"])

    query_vector = vectorize(query["question"], idf)
    ranked = []
    edge_bonus_by_unit: dict[str, float] = {}
    for edge in selected_edges:
        for ball_id in edge["accepted_ball_ids"]:
            for ball in balls:
                if ball["ball_id"] == ball_id:
                    for unit_id in ball["unit_ids"]:
                        edge_bonus_by_unit[unit_id] = max(edge_bonus_by_unit.get(unit_id, 0.0), edge["query_aware_score"])

    for unit_id in set(selected_unit_ids):
        unit = units_by_id[unit_id]
        base_score = dot(query_vector, vectors[unit_id])
        score = base_score + args.w_edge_unit_bonus * edge_bonus_by_unit.get(unit_id, 0.0)
        ranked.append(
            {
                "unit_id": unit_id,
                "score": score,
                "base_score": base_score,
                "edge_bonus": edge_bonus_by_unit.get(unit_id, 0.0),
                "is_gold": unit["is_gold"],
                "title": unit["title"],
                "text": unit["text"],
                "tokens": len(unit["text"].split()),
            }
        )
    ranked.sort(key=lambda row: (-row["score"], row["unit_id"]))

    if len(ranked) < max_k and args.fill_with_fixed:
        seen = {row["unit_id"] for row in ranked}
        fixed = retrieve_fixed_units(query, query_units, vectors, idf, max_k)
        for row in fixed:
            if row["unit_id"] not in seen:
                ranked.append(row)
                seen.add(row["unit_id"])
            if len(ranked) >= max_k:
                break

    info = {
        **{key: value for key, value in decision.items() if key != "scored_balls"},
        "is_boundary": 1.0 if boundary else 0.0,
        "used_hyperedge": 1.0 if selected_edges else 0.0,
        "seed_ball_count": len(seed_ball_ids),
        "expanded_ball_count": len(expanded_ball_ids),
        "selected_edge_count": len(selected_edges),
        "candidate_edge_count": len(edges),
    }
    return ranked[:max_k], info, selected_edges


def aggregate(results: list[dict[str, Any]], k_values: list[int]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in results:
        grouped.setdefault(row["dataset"], []).append(row)
    grouped["ALL"] = results

    summary: dict[str, Any] = {}
    for dataset, rows in grouped.items():
        item: dict[str, Any] = {"queries": len(rows)}
        denom = max(len(rows), 1)
        item["avg_mrr"] = sum(row["mrr"] for row in rows) / denom
        item["boundary_rate"] = sum(row["is_boundary"] for row in rows) / denom
        item["hyperedge_rate"] = sum(row["used_hyperedge"] for row in rows) / denom
        item["avg_candidate_edges"] = sum(row["candidate_edge_count"] for row in rows) / denom
        item["avg_selected_edges"] = sum(row["selected_edge_count"] for row in rows) / denom
        item["avg_expanded_balls"] = sum(row["expanded_ball_count"] for row in rows) / denom
        expansion_units = sum(row["expansion_units"] for row in rows)
        item["expansion_yield"] = sum(row["expansion_gold_units"] for row in rows) / max(expansion_units, 1)
        item["false_expansion_rate"] = sum(row["expansion_non_gold_units"] for row in rows) / max(expansion_units, 1)
        for k in k_values:
            for metric in ["evidence_recall", "hit", "chain_recall", "context_units", "context_tokens"]:
                key = f"{metric}_at_{k}"
                item[key] = sum(row[key] for row in rows) / denom
        summary[dataset] = item
    return summary


def write_summary_csv(path: Path, summary: dict[str, Any], k_values: list[int]) -> None:
    fields = [
        "dataset",
        "queries",
        "avg_mrr",
        "boundary_rate",
        "hyperedge_rate",
        "avg_candidate_edges",
        "avg_selected_edges",
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
        "# Stage 1D Query-Aware Hyperedge Retrieval Report",
        "",
        "## Material Passport",
        "",
        "- Stage: Stage 1D Retrieval-only MVP",
        "- Method: granular balls + query-aware hyperedge scoring + expansion budget",
        "- Gold labels used for indexing: No",
        "- Generator used: No",
        "",
        "## Parameters",
        "",
        f"- seed_balls: {args.seed_balls}",
        f"- top_edges: {args.top_edges}",
        f"- max_expanded_balls: {args.max_expanded_balls}",
        f"- min_edge_score: {args.min_edge_score}",
        f"- fill_with_fixed: {args.fill_with_fixed}",
        f"- weights: query={args.w_query}, title={args.w_title}, keyword={args.w_keyword}, center={args.w_center}, ball={args.w_ball}, unit_bonus={args.w_edge_unit_bonus}",
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
                f"- Boundary rate: {item['boundary_rate']:.4f}",
                f"- Hyperedge trigger rate: {item['hyperedge_rate']:.4f}",
                f"- Avg candidate edges/query: {item['avg_candidate_edges']:.2f}",
                f"- Avg selected edges/query: {item['avg_selected_edges']:.2f}",
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", required=True, type=Path)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--details-output", required=True, type=Path)
    parser.add_argument("--selected-edges-output", required=True, type=Path)
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
    parser.add_argument("--keyword-overlap-min", type=int, default=4)
    parser.add_argument("--center-similarity-min", type=float, default=0.45)
    parser.add_argument("--seed-balls", type=int, default=2)
    parser.add_argument("--top-edges", type=int, default=2)
    parser.add_argument("--max-expanded-balls", type=int, default=2)
    parser.add_argument("--min-edge-score", type=float, default=0.35)
    parser.add_argument("--decision-boundary-margin", type=float, default=0.50)
    parser.add_argument("--decision-score-margin", type=float, default=0.10)
    parser.add_argument("--decision-min-ball-score", type=float, default=0.20)
    parser.add_argument("--title-norm", type=int, default=3)
    parser.add_argument("--keyword-norm", type=int, default=5)
    parser.add_argument("--w-query", type=float, default=0.35)
    parser.add_argument("--w-title", type=float, default=0.15)
    parser.add_argument("--w-keyword", type=float, default=0.20)
    parser.add_argument("--w-center", type=float, default=0.15)
    parser.add_argument("--w-ball", type=float, default=0.15)
    parser.add_argument("--w-edge-unit-bonus", type=float, default=0.0)
    parser.add_argument("--fill-with-fixed", action="store_true")
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
    selected_edges_out: list[dict[str, Any]] = []

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
        ranked, info, selected_edges = retrieve_query_aware(
            query,
            query_units,
            units_by_id,
            vectors,
            idf,
            balls,
            edges,
            max_k,
            args,
        )
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
        for edge in selected_edges:
            selected_edges_out.append(edge)

    summary = aggregate(details, k_values)
    baseline = load_baseline_summary(args.baseline_summary)
    write_jsonl(args.details_output, details)
    write_jsonl(args.selected_edges_output, selected_edges_out)
    write_summary_csv(args.summary_output, summary, k_values)
    write_report(args.report, summary, baseline, k_values, args)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
