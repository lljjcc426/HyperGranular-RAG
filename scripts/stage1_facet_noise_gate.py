"""Noise-gated facet hyperedge retrieval for Stage 1F.

This script keeps the Stage 1E facet-aware retrieval pipeline, but adds
unsupervised gates before accepting an expanded granular ball. Gold labels are
used only for evaluation.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from stage1_facet_hyperedge import (
    aggregate,
    enrich_facets,
    query_terms,
    retrieve_with_facets,
    write_summary_csv,
)
from stage1_granular_ball_baseline import (
    build_balls_for_query,
    build_idf,
    dot,
    evaluate_query,
    load_baseline_summary,
    load_jsonl,
    vectorize,
    write_jsonl,
)
from stage1_hyperedge_retrieval import decision_from_balls, enrich_balls, is_boundary_query


def select_noise_gated_expansions(
    query: dict[str, Any],
    balls: list[dict[str, Any]],
    idf: dict[str, float],
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    decision = decision_from_balls(query, balls, idf)
    boundary = is_boundary_query(decision, args)
    scored_balls = decision["scored_balls"]
    q_terms = query_terms(query["question"])
    seed_balls = [ball for _, ball in scored_balls[: args.seed_balls]]
    seed_ids = {ball["ball_id"] for ball in seed_balls}
    covered_terms = set().union(*(ball["facet_terms"] for ball in seed_balls)) if seed_balls else set()
    seed_vectors = [ball["center"] for ball in seed_balls]

    if args.expand_boundary_only and not boundary:
        return [], [], {
            **{key: value for key, value in decision.items() if key != "scored_balls"},
            "is_boundary": 0.0,
            "seed_ball_count": len(seed_ids),
            "expanded_ball_count": 0,
            "selected_edge_count": 0,
            "query_facet_count": len(q_terms),
            "seed_facet_count": len(covered_terms),
            "final_facet_count": len(covered_terms),
            "gate_reject_size": 0,
            "gate_reject_anchor": 0,
            "gate_reject_ratio": 0,
            "gate_reject_redundancy": 0,
            "gate_reject_score": 0,
        }

    reject_counts = {
        "gate_reject_size": 0,
        "gate_reject_anchor": 0,
        "gate_reject_ratio": 0,
        "gate_reject_redundancy": 0,
        "gate_reject_score": 0,
    }
    candidates: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    def reject(ball: dict[str, Any], reason: str, score: float, new_terms: set[str], shared_terms: set[str], extra: dict[str, Any] | None = None) -> None:
        row = {
            "edge_id": f"{query['query_id']}::rejected::{reason}::{ball['ball_id']}",
            "query_id": query["query_id"],
            "accepted_ball_ids": [ball["ball_id"]],
            "reject_reason": reason,
            "new_terms": sorted(new_terms),
            "shared_terms": sorted(shared_terms),
            "facet_terms": sorted(ball["facet_terms"]),
            "ball_score": score,
            "ball_size": len(ball["unit_ids"]),
            "gold_units": ball.get("gold_units", 0),
        }
        if extra:
            row.update(extra)
        rejected.append(row)

    for score, ball in scored_balls:
        if ball["ball_id"] in seed_ids:
            continue
        new_terms = ball["facet_terms"] - covered_terms
        shared_terms = ball["facet_terms"] & covered_terms
        if len(new_terms) < args.min_new_terms:
            if not (args.allow_high_score_no_new and score >= args.high_score_no_new_threshold):
                reject(ball, "min_new_terms", score, new_terms, shared_terms)
                continue

        ball_size = len(ball["unit_ids"])
        if args.max_candidate_ball_size > 0 and ball_size > args.max_candidate_ball_size:
            reject_counts["gate_reject_size"] += 1
            reject(ball, "size", score, new_terms, shared_terms)
            continue

        max_seed_sim = max((dot(ball["center"], seed_vec) for seed_vec in seed_vectors), default=0.0)
        anchored = score >= args.min_ball_score or max_seed_sim >= args.min_seed_similarity
        if not anchored:
            reject_counts["gate_reject_anchor"] += 1
            reject(ball, "anchor", score, new_terms, shared_terms, {"max_seed_similarity": max_seed_sim})
            continue

        units_per_new_term = ball_size / max(len(new_terms), 1)
        if args.max_units_per_new_term > 0 and units_per_new_term > args.max_units_per_new_term:
            reject_counts["gate_reject_ratio"] += 1
            reject(ball, "units_per_new_term", score, new_terms, shared_terms, {"units_per_new_term": units_per_new_term})
            continue

        redundancy = len(shared_terms) / max(len(ball["facet_terms"]), 1)
        if redundancy > args.max_redundancy:
            reject_counts["gate_reject_redundancy"] += 1
            reject(ball, "redundancy", score, new_terms, shared_terms, {"redundancy": redundancy})
            continue

        diversity = 1.0 - max_seed_sim
        new_ratio = len(new_terms) / max(len(q_terms), 1)
        total_ratio = len(ball["facet_terms"]) / max(len(q_terms), 1)
        size_penalty = ball_size / max(args.max_candidate_ball_size, 1) if args.max_candidate_ball_size > 0 else 0.0
        facet_score = (
            args.w_new * new_ratio
            + args.w_total * total_ratio
            + args.w_ball * score
            + args.w_diversity * diversity
            - args.w_redundancy * redundancy
            - args.w_size * size_penalty
        )
        if facet_score < args.min_facet_score:
            reject_counts["gate_reject_score"] += 1
            reject(
                ball,
                "facet_score",
                score,
                new_terms,
                shared_terms,
                {
                    "facet_score": facet_score,
                    "diversity": diversity,
                    "redundancy": redundancy,
                    "units_per_new_term": units_per_new_term,
                    "max_seed_similarity": max_seed_sim,
                },
            )
            continue

        candidates.append(
            {
                "edge_id": f"{query['query_id']}::facet_gate::{ball['ball_id']}",
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
                "ball_size": ball_size,
                "units_per_new_term": units_per_new_term,
                "max_seed_similarity": max_seed_sim,
                "gold_units": ball.get("gold_units", 0),
            }
        )

    candidates.sort(key=lambda row: (-row["facet_score"], row["edge_id"]))

    selected: list[dict[str, Any]] = []
    selected_ball_ids: set[str] = set()
    dynamic_budget = args.max_expanded_balls
    if args.dynamic_budget and boundary:
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
        "is_boundary": 1.0 if boundary else 0.0,
        "seed_ball_count": len(seed_ids),
        "expanded_ball_count": len(selected_ball_ids),
        "selected_edge_count": len(selected),
        "query_facet_count": len(q_terms),
        "seed_facet_count": len(set().union(*(ball["facet_terms"] for ball in seed_balls)) if seed_balls else set()),
        "final_facet_count": len(covered_terms),
        **reject_counts,
    }
    return selected, rejected, info


def write_noise_gate_summary_csv(path: Path, summary: dict[str, Any], k_values: list[int]) -> None:
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
        "gate_reject_size",
        "gate_reject_anchor",
        "gate_reject_ratio",
        "gate_reject_redundancy",
        "gate_reject_score",
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


def aggregate_with_gates(rows: list[dict[str, Any]], k_values: list[int]) -> dict[str, Any]:
    summary = aggregate(rows, k_values)
    for dataset, item in summary.items():
        group = rows if dataset == "ALL" else [row for row in rows if row["dataset"] == dataset]
        denom = max(len(group), 1)
        for key in [
            "gate_reject_size",
            "gate_reject_anchor",
            "gate_reject_ratio",
            "gate_reject_redundancy",
            "gate_reject_score",
        ]:
            item[key] = sum(row.get(key, 0) for row in group) / denom
    return summary


def write_report(path: Path, summary: dict[str, Any], baseline: dict[str, dict[str, float]], k_values: list[int], args: argparse.Namespace) -> None:
    lines = [
        "# Stage 1F Noise-Gated Facet Hyperedge Retrieval Report",
        "",
        "## Material Passport",
        "",
        "- Stage: Stage 1F Retrieval-only MVP",
        "- Method: granular balls + facet-aware hyperedge expansion + unsupervised noise gates",
        "- Gold labels used for indexing: No",
        "- Generator used: No",
        "",
        "## Parameters",
        "",
        f"- seed_balls: {args.seed_balls}",
        f"- top_facet_edges: {args.top_facet_edges}",
        f"- max_expanded_balls: {args.max_expanded_balls}",
        f"- expand_boundary_only: {args.expand_boundary_only}",
        f"- max_candidate_ball_size: {args.max_candidate_ball_size}",
        f"- min_ball_score: {args.min_ball_score}",
        f"- min_seed_similarity: {args.min_seed_similarity}",
        f"- max_units_per_new_term: {args.max_units_per_new_term}",
        f"- max_redundancy: {args.max_redundancy}",
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
                f"- Gate rejects/query: size={item['gate_reject_size']:.2f}, anchor={item['gate_reject_anchor']:.2f}, ratio={item['gate_reject_ratio']:.2f}, redundancy={item['gate_reject_redundancy']:.2f}, score={item['gate_reject_score']:.2f}",
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
    parser.add_argument("--rejected-edges-output", type=Path)
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
    parser.add_argument("--top-facet-edges", type=int, default=2)
    parser.add_argument("--max-expanded-balls", type=int, default=2)
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
    parser.add_argument("--expand-boundary-only", action="store_true")
    parser.add_argument("--max-candidate-ball-size", type=int, default=8)
    parser.add_argument("--min-ball-score", type=float, default=0.08)
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
    all_rejected_edges: list[dict[str, Any]] = []
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
        selected_edges, rejected_edges, info = select_noise_gated_expansions(query, balls, idf, args)
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
        if args.rejected_edges_output:
            for rejected_edge in rejected_edges:
                rejected_edge["dataset"] = query.get("dataset")
            all_rejected_edges.extend(rejected_edges)

    summary = aggregate_with_gates(details, k_values)
    baseline = load_baseline_summary(args.baseline_summary)
    write_jsonl(args.details_output, details)
    write_jsonl(args.facet_edges_output, all_edges)
    if args.rejected_edges_output:
        write_jsonl(args.rejected_edges_output, all_rejected_edges)
    write_noise_gate_summary_csv(args.summary_output, summary, k_values)
    write_report(args.report, summary, baseline, k_values, args)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
