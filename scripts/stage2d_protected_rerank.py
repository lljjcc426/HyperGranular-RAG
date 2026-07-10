"""Stage2D protected dense reranking for HyperGranular-RAG.

The experiment keeps a dense-fixed prefix, inserts a small budget of hyperedge
expansion units immediately after that protected prefix, then fills the rest
with the original dense ranking. This tests whether hyperedge expansion is
useful as protected evidence completion rather than a full dense-rank
replacement.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from stage2_dense_replication import (
    build_balls,
    dot,
    enrich_balls,
    enrich_facets,
    evaluate_query,
    fixed_retrieve,
    load_jsonl,
    load_or_build_embeddings,
    normalize_matrix,
    query_terms,
    select_facet_edges,
)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def expansion_candidates(
    query: dict[str, Any],
    q_emb: np.ndarray,
    candidate_indices: list[int],
    units: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    args: argparse.Namespace,
    method: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, int]]:
    balls = build_balls(
        query["query_id"],
        candidate_indices,
        unit_embeddings,
        args.min_size,
        args.max_size,
        args.radius_threshold,
        args.max_depth,
        args.boundary_width,
    )
    enrich_balls(balls, units, args.top_center_terms)
    enrich_facets(balls, query_terms(query["question"]))
    selected, info = select_facet_edges(query, q_emb, balls, args, gated=(method == "gated"))
    expanded_ball_ids = {ball_id for edge in selected for ball_id in edge["accepted_ball_ids"]}
    bonus_by_ball = {ball_id: edge["facet_score"] for edge in selected for ball_id in edge["accepted_ball_ids"]}
    candidates_by_unit: dict[str, dict[str, Any]] = {}
    expanded_indices = set()
    for ball in balls:
        if ball["ball_id"] not in expanded_ball_ids:
            continue
        bonus = bonus_by_ball.get(ball["ball_id"], 0.0)
        for idx in ball["indices"]:
            expanded_indices.add(idx)
            unit = units[idx]
            row = {
                "unit_index": idx,
                "unit_id": unit["unit_id"],
                "score": dot(q_emb, unit_embeddings[idx]),
                "rerank_score": dot(q_emb, unit_embeddings[idx]) + args.w_facet_unit_bonus * bonus,
                "facet_bonus": bonus,
                "is_gold": unit["is_gold"],
                "title": unit["title"],
                "text": unit["text"],
                "tokens": len(unit["text"].split()),
                "source": method,
            }
            old = candidates_by_unit.get(unit["unit_id"])
            if old is None or row["rerank_score"] > old["rerank_score"]:
                candidates_by_unit[unit["unit_id"]] = row
    candidates = sorted(candidates_by_unit.values(), key=lambda row: (-row["rerank_score"], row["unit_id"]))
    expansion_stats = {
        "expansion_units": len(expanded_indices),
        "expansion_gold_units": sum(1 for idx in expanded_indices if units[idx]["is_gold"]),
    }
    expansion_stats["expansion_non_gold_units"] = expansion_stats["expansion_units"] - expansion_stats["expansion_gold_units"]
    return candidates, selected, info, expansion_stats


def protected_rerank(
    fixed_ranked: list[dict[str, Any]],
    expanded_ranked: list[dict[str, Any]],
    protect_n: int,
    insert_budget: int,
    max_k: int,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    protected = fixed_ranked[:protect_n]
    seen = {row["unit_id"] for row in protected}
    inserted = []
    for row in expanded_ranked:
        if len(inserted) >= insert_budget:
            break
        if row["unit_id"] in seen:
            continue
        inserted.append(row)
        seen.add(row["unit_id"])
    ranked = protected + inserted
    for row in fixed_ranked:
        if len(ranked) >= max_k:
            break
        if row["unit_id"] in seen:
            continue
        ranked.append(row)
        seen.add(row["unit_id"])
    for row in expanded_ranked:
        if len(ranked) >= max_k:
            break
        if row["unit_id"] in seen:
            continue
        ranked.append(row)
        seen.add(row["unit_id"])
    inserted_gold = sum(1 for row in inserted if row["is_gold"])
    return ranked[:max_k], {
        "inserted_units": len(inserted),
        "inserted_gold_units": inserted_gold,
        "inserted_non_gold_units": len(inserted) - inserted_gold,
    }


def aggregate(rows: list[dict[str, Any]], k_values: list[int]) -> dict[tuple[str, str, str, int, int], dict[str, Any]]:
    grouped: dict[tuple[str, str, str, int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["dataset"], row["strategy"], row["method"], row["protect_n"], row["insert_budget"])].append(row)
        grouped[("ALL", row["strategy"], row["method"], row["protect_n"], row["insert_budget"])].append(row)
    out = {}
    for key, items in grouped.items():
        denom = max(len(items), 1)
        summary: dict[str, Any] = {
            "dataset": key[0],
            "strategy": key[1],
            "method": key[2],
            "protect_n": key[3],
            "insert_budget": key[4],
            "queries": len(items),
            "avg_mrr": sum(row["mrr"] for row in items) / denom,
            "boundary_rate": sum(row.get("is_boundary", 0.0) for row in items) / denom,
            "hyperedge_rate": sum(1.0 if row.get("selected_edge_count", 0) > 0 else 0.0 for row in items) / denom,
            "avg_selected_edges": sum(row.get("selected_edge_count", 0) for row in items) / denom,
            "avg_inserted_units": sum(row.get("inserted_units", 0) for row in items) / denom,
        }
        inserted_units = sum(row.get("inserted_units", 0) for row in items)
        expansion_units = sum(row.get("expansion_units", 0) for row in items)
        summary["insert_yield"] = sum(row.get("inserted_gold_units", 0) for row in items) / max(inserted_units, 1)
        summary["false_insert_rate"] = sum(row.get("inserted_non_gold_units", 0) for row in items) / max(inserted_units, 1)
        summary["expansion_yield"] = sum(row.get("expansion_gold_units", 0) for row in items) / max(expansion_units, 1)
        summary["false_expansion_rate"] = sum(row.get("expansion_non_gold_units", 0) for row in items) / max(expansion_units, 1)
        for k in k_values:
            for metric in ["evidence_recall", "hit", "chain_recall", "context_units", "context_tokens"]:
                metric_key = f"{metric}_at_{k}"
                summary[metric_key] = sum(row[metric_key] for row in items) / denom
        out[key] = summary
    return out


def write_summary(path: Path, summaries: dict[tuple[str, str, str, int, int], dict[str, Any]], k_values: list[int]) -> None:
    fields = [
        "dataset", "strategy", "method", "protect_n", "insert_budget", "queries", "avg_mrr",
        "boundary_rate", "hyperedge_rate", "avg_selected_edges", "avg_inserted_units",
        "insert_yield", "false_insert_rate", "expansion_yield", "false_expansion_rate",
    ]
    for k in k_values:
        fields.extend([f"evidence_recall_at_{k}", f"hit_at_{k}", f"chain_recall_at_{k}", f"context_units_at_{k}", f"context_tokens_at_{k}"])
    ordered = sorted(summaries.values(), key=lambda row: (row["dataset"] != "ALL", row["dataset"], row["method"], row["protect_n"], row["insert_budget"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(ordered)


def delta_counts(rows: list[dict[str, Any]], baseline_by_query: dict[str, dict[str, Any]], k_values: list[int]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["strategy"] == "fixed":
            continue
        grouped[(row["method"], row["strategy"], row["protect_n"], row["insert_budget"])].append(row)
    out = []
    for key, items in sorted(grouped.items()):
        for k in k_values:
            metric = f"chain_recall_at_{k}"
            counts = {"improved": 0, "same": 0, "regressed": 0}
            for row in items:
                delta = row[metric] - baseline_by_query[row["query_id"]][metric]
                if delta > 1e-9:
                    counts["improved"] += 1
                elif delta < -1e-9:
                    counts["regressed"] += 1
                else:
                    counts["same"] += 1
            out.append({
                "method": key[0],
                "strategy": key[1],
                "protect_n": key[2],
                "insert_budget": key[3],
                "metric": metric,
                **counts,
            })
    return out


def write_delta(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = ["method", "strategy", "protect_n", "insert_budget", "metric", "improved", "same", "regressed"]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: Path, summary_rows: list[dict[str, Any]], delta_rows: list[dict[str, Any]], args: argparse.Namespace) -> None:
    all_rows = [row for row in summary_rows if row["dataset"] == "ALL"]
    best_cr10 = max(all_rows, key=lambda row: row["chain_recall_at_10"])
    best_cr20 = max(all_rows, key=lambda row: row["chain_recall_at_20"])
    baseline = next(row for row in all_rows if row["strategy"] == "fixed")
    selected = [
        baseline,
        best_cr10,
        best_cr20,
        *[
            row for row in all_rows
            if row["method"] == "gated" and row["protect_n"] in {5, 10} and row["insert_budget"] in {2, 4}
        ],
    ]
    seen = set()
    compact = []
    for row in selected:
        key = (row["strategy"], row["method"], row["protect_n"], row["insert_budget"])
        if key not in seen:
            compact.append(row)
            seen.add(key)

    lines = [
        "# Stage2D Protected Dense Reranking Report",
        "",
        "## Material Passport",
        "",
        "- Stage: Stage2D protected dense reranking",
        f"- Units: `{args.units}`",
        f"- Queries: `{args.queries}`",
        f"- Embedding cache: `{args.embedding_cache}`",
        "- Gold labels used for indexing: No",
        "- Generator used: No",
        "- Strategy: preserve dense-fixed prefix, insert a budgeted number of hyperedge expansion units, then fill with dense-fixed ranking.",
        "",
        "## ALL Summary",
        "",
        "| Strategy | Method | Protect | Insert | ER@10 | CR@10 | ER@15 | CR@15 | ER@20 | CR@20 | False insert |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in compact:
        lines.append(
            f"| {row['strategy']} | {row['method']} | {row['protect_n']} | {row['insert_budget']} | "
            f"{row['evidence_recall_at_10']:.4f} | {row['chain_recall_at_10']:.4f} | "
            f"{row['evidence_recall_at_15']:.4f} | {row['chain_recall_at_15']:.4f} | "
            f"{row['evidence_recall_at_20']:.4f} | {row['chain_recall_at_20']:.4f} | "
            f"{row['false_insert_rate']:.4f} |"
        )
    lines.extend([
        "",
        "## Best Observed Rows",
        "",
        f"- Best ALL CR@10: {best_cr10['strategy']} / {best_cr10['method']} / protect={best_cr10['protect_n']} / insert={best_cr10['insert_budget']} / CR@10={best_cr10['chain_recall_at_10']:.4f}.",
        f"- Best ALL CR@20: {best_cr20['strategy']} / {best_cr20['method']} / protect={best_cr20['protect_n']} / insert={best_cr20['insert_budget']} / CR@20={best_cr20['chain_recall_at_20']:.4f}.",
        "",
        "## Query-Level CR Delta vs Dense Fixed",
        "",
        "| Method | Protect | Insert | Metric | Improved | Same | Regressed |",
        "|---|---:|---:|---|---:|---:|---:|",
    ])
    for row in delta_rows:
        if row["method"] == "gated" and row["protect_n"] in {5, 10} and row["insert_budget"] in {2, 4}:
            lines.append(
                f"| {row['method']} | {row['protect_n']} | {row['insert_budget']} | {row['metric']} | "
                f"{row['improved']} | {row['same']} | {row['regressed']} |"
            )
    lines.extend([
        "",
        "## Evidence-Grounded Reading",
        "",
        "- This report only describes the produced CSV metrics; it does not claim generator answer quality.",
        "- A protected-prefix strategy is useful only if its chain recall does not regress against dense fixed at the target K.",
        "- If protect=10, CR@10 is structurally constrained to equal dense fixed because no inserted unit can enter Top-10.",
        "- False insert rate measures inserted non-gold units among inserted units, not among all expanded candidates.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", required=True, type=Path)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--embedding-cache", required=True, type=Path)
    parser.add_argument("--output-dir", default=Path("results"), type=Path)
    parser.add_argument("--report", default=Path("reports/超粒球RAG_Stage2D_ProtectedDenseRerank报告.md"), type=Path)
    parser.add_argument("--model-name", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--max-length", type=int, default=192)
    parser.add_argument("--k", nargs="+", type=int, default=[1, 3, 5, 10, 15, 20])
    parser.add_argument("--protect-n", nargs="+", type=int, default=[5, 10])
    parser.add_argument("--insert-budget", nargs="+", type=int, default=[1, 2, 4, 8])
    parser.add_argument("--methods", nargs="+", default=["facet", "gated"], choices=["facet", "gated"])
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
    parser.add_argument("--write-details", action="store_true")
    args = parser.parse_args()

    k_values = sorted(set(args.k))
    max_k = max(k_values)
    units = load_jsonl(args.units)
    queries = load_jsonl(args.queries)
    unit_embeddings, query_embeddings = load_or_build_embeddings(
        args.embedding_cache,
        units,
        queries,
        args.model_name,
        args.batch_size,
        args.max_length,
    )
    unit_embeddings = normalize_matrix(unit_embeddings.astype("float32"))
    query_embeddings = normalize_matrix(query_embeddings.astype("float32"))

    unit_indices_by_query: dict[str, list[int]] = defaultdict(list)
    for idx, unit in enumerate(units):
        unit_indices_by_query[unit["query_id"]].append(idx)
    query_index_by_id = {query["query_id"]: idx for idx, query in enumerate(queries)}

    rows: list[dict[str, Any]] = []
    baseline_by_query: dict[str, dict[str, Any]] = {}
    for query in queries:
        q_emb = query_embeddings[query_index_by_id[query["query_id"]]]
        candidate_indices = unit_indices_by_query[query["query_id"]]
        fixed_ranked = fixed_retrieve(q_emb, candidate_indices, units, unit_embeddings, max_k)
        base = evaluate_query(query, fixed_ranked, k_values)
        base.update({"strategy": "fixed", "method": "fixed", "protect_n": 0, "insert_budget": 0})
        rows.append(base)
        baseline_by_query[query["query_id"]] = base
        for method in args.methods:
            expanded_ranked, selected, info, expansion_stats = expansion_candidates(query, q_emb, candidate_indices, units, unit_embeddings, args, method)
            for protect_n in args.protect_n:
                for insert_budget in args.insert_budget:
                    ranked, insert_stats = protected_rerank(fixed_ranked, expanded_ranked, protect_n, insert_budget, max_k)
                    row = evaluate_query(query, ranked, k_values)
                    row.update(info)
                    row.update(expansion_stats)
                    row.update(insert_stats)
                    row.update({
                        "strategy": "protected_insert",
                        "method": method,
                        "protect_n": protect_n,
                        "insert_budget": insert_budget,
                        "selected_edge_count": len(selected),
                    })
                    rows.append(row)

    summaries = aggregate(rows, k_values)
    summary_path = args.output_dir / "stage2d_protected_rerank_summary.csv"
    delta_path = args.output_dir / "stage2d_protected_rerank_delta.csv"
    detail_path = args.output_dir / "stage2d_protected_rerank_details.jsonl"
    summary_rows = list(summaries.values())
    delta_rows = delta_counts(rows, baseline_by_query, k_values)
    write_summary(summary_path, summaries, k_values)
    write_delta(delta_path, delta_rows)
    write_report(args.report, summary_rows, delta_rows, args)
    if args.write_details:
        write_jsonl(detail_path, rows)
    print(json.dumps({
        "summary": str(summary_path),
        "delta": str(delta_path),
        "report": str(args.report),
        "detail": str(detail_path) if args.write_details else None,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
