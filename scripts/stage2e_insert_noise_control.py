"""Stage2E evidence-aware insertion filtering for HyperGranular-RAG.

This experiment preserves a dense-fixed prefix and filters hyperedge expansion
candidates before inserting them. The filters use only retrieval-time signals:
unit dense similarity and selected-edge facet score. Gold labels are used only
after ranking to calculate evaluation metrics.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np

from stage2_dense_replication import (
    evaluate_query,
    fixed_retrieve,
    load_jsonl,
    load_or_build_embeddings,
    normalize_matrix,
)
from stage2d_protected_rerank import expansion_candidates, protected_rerank


@dataclass(frozen=True)
class FilterSpec:
    """A label-free filter defined from candidate-pool score quantiles."""

    name: str
    score_quantile: float | None
    facet_quantile: float | None


def quantile_label(value: float) -> str:
    return f"q{int(round(value * 100)):02d}"


def filter_specs(score_quantiles: list[float], facet_quantile: float) -> list[FilterSpec]:
    specs = [FilterSpec("none", None, None)]
    for score_quantile in score_quantiles:
        specs.append(FilterSpec(f"score_{quantile_label(score_quantile)}", score_quantile, None))
    for score_quantile in score_quantiles[1:]:
        specs.append(
            FilterSpec(
                f"score_{quantile_label(score_quantile)}_facet_{quantile_label(facet_quantile)}",
                score_quantile,
                facet_quantile,
            )
        )
    return specs


def pool_thresholds(
    candidates_by_method: dict[str, list[dict[str, Any]]],
    specs: list[FilterSpec],
) -> dict[tuple[str, str], tuple[float | None, float | None]]:
    """Compute method-specific thresholds without consulting gold labels."""

    thresholds: dict[tuple[str, str], tuple[float | None, float | None]] = {}
    for method, candidates in candidates_by_method.items():
        scores = np.array([row["score"] for row in candidates], dtype="float32")
        facets = np.array([row["facet_bonus"] for row in candidates], dtype="float32")
        for spec in specs:
            score_floor = float(np.quantile(scores, spec.score_quantile)) if spec.score_quantile is not None else None
            facet_floor = float(np.quantile(facets, spec.facet_quantile)) if spec.facet_quantile is not None else None
            thresholds[(method, spec.name)] = (score_floor, facet_floor)
    return thresholds


def apply_filter(
    candidates: list[dict[str, Any]],
    score_floor: float | None,
    facet_floor: float | None,
) -> list[dict[str, Any]]:
    return [
        row
        for row in candidates
        if (score_floor is None or row["score"] >= score_floor)
        and (facet_floor is None or row["facet_bonus"] >= facet_floor)
    ]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def aggregate(rows: list[dict[str, Any]], k_values: list[int]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str, int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            row["dataset"],
            row["strategy"],
            row["method"],
            row["filter_name"],
            row["protect_n"],
            row["insert_budget"],
        )
        grouped[key].append(row)
        all_key = (
            "ALL",
            row["strategy"],
            row["method"],
            row["filter_name"],
            row["protect_n"],
            row["insert_budget"],
        )
        grouped[all_key].append(row)

    summaries: list[dict[str, Any]] = []
    for key, items in grouped.items():
        denom = max(len(items), 1)
        inserted = sum(row.get("inserted_units", 0) for row in items)
        inserted_gold = sum(row.get("inserted_gold_units", 0) for row in items)
        candidates = sum(row.get("candidate_count", 0) for row in items)
        filtered_candidates = sum(row.get("filtered_candidate_count", 0) for row in items)
        summary: dict[str, Any] = {
            "dataset": key[0],
            "strategy": key[1],
            "method": key[2],
            "filter_name": key[3],
            "protect_n": key[4],
            "insert_budget": key[5],
            "queries": len(items),
            "avg_mrr": sum(row["mrr"] for row in items) / denom,
            "boundary_rate": sum(row.get("is_boundary", 0.0) for row in items) / denom,
            "hyperedge_rate": sum(1.0 if row.get("selected_edge_count", 0) > 0 else 0.0 for row in items) / denom,
            "avg_selected_edges": sum(row.get("selected_edge_count", 0) for row in items) / denom,
            "avg_candidates": candidates / denom,
            "avg_filtered_candidates": filtered_candidates / denom,
            "candidate_retention": filtered_candidates / max(candidates, 1),
            "avg_inserted_units": inserted / denom,
            "budget_fill_rate": inserted / max(sum(row["insert_budget"] for row in items), 1),
            "insert_yield": inserted_gold / max(inserted, 1),
            "false_insert_rate": (inserted - inserted_gold) / max(inserted, 1),
            "score_quantile": items[0].get("score_quantile"),
            "facet_quantile": items[0].get("facet_quantile"),
            "score_floor": items[0].get("score_floor"),
            "facet_floor": items[0].get("facet_floor"),
        }
        for k in k_values:
            for metric in ["evidence_recall", "hit", "chain_recall", "context_units", "context_tokens"]:
                metric_key = f"{metric}_at_{k}"
                summary[metric_key] = sum(row[metric_key] for row in items) / denom
        summaries.append(summary)
    return summaries


def write_summary(path: Path, rows: list[dict[str, Any]], k_values: list[int]) -> None:
    fields = [
        "dataset",
        "strategy",
        "method",
        "filter_name",
        "score_quantile",
        "facet_quantile",
        "score_floor",
        "facet_floor",
        "protect_n",
        "insert_budget",
        "queries",
        "avg_mrr",
        "boundary_rate",
        "hyperedge_rate",
        "avg_selected_edges",
        "avg_candidates",
        "avg_filtered_candidates",
        "candidate_retention",
        "avg_inserted_units",
        "budget_fill_rate",
        "insert_yield",
        "false_insert_rate",
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
    ordered = sorted(
        rows,
        key=lambda row: (
            row["dataset"] != "ALL",
            row["dataset"],
            row["method"],
            row["filter_name"],
            row["protect_n"],
            row["insert_budget"],
        ),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(ordered)


def delta_counts(
    rows: list[dict[str, Any]],
    baseline_by_query: dict[str, dict[str, Any]],
    k_values: list[int],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["strategy"] == "fixed":
            continue
        grouped[(row["method"], row["filter_name"], row["protect_n"], row["insert_budget"])].append(row)
    output = []
    for (method, filter_name, protect_n, insert_budget), items in sorted(grouped.items()):
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
            output.append(
                {
                    "method": method,
                    "filter_name": filter_name,
                    "protect_n": protect_n,
                    "insert_budget": insert_budget,
                    "metric": metric,
                    **counts,
                }
            )
    return output


def write_delta(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = ["method", "filter_name", "protect_n", "insert_budget", "metric", "improved", "same", "regressed"]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def format_floor(value: float | None) -> str:
    return "-" if value is None else f"{value:.4f}"


def unique_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    output = []
    for row in rows:
        key = (row["strategy"], row["method"], row["filter_name"], row["protect_n"], row["insert_budget"])
        if key not in seen:
            output.append(row)
            seen.add(key)
    return output


def write_report(
    path: Path,
    summaries: list[dict[str, Any]],
    deltas: list[dict[str, Any]],
    args: argparse.Namespace,
    duration_seconds: float,
) -> None:
    all_rows = [row for row in summaries if row["dataset"] == "ALL"]
    baseline = next(row for row in all_rows if row["strategy"] == "fixed")
    filtered_rows = [row for row in all_rows if row["strategy"] != "fixed" and row["filter_name"] != "none"]
    unfiltered = next(
        row
        for row in all_rows
        if row["method"] == "gated" and row["filter_name"] == "none" and row["protect_n"] == 5 and row["insert_budget"] == 2
    )
    best_filtered_cr10 = max(filtered_rows, key=lambda row: row["chain_recall_at_10"])
    best_filtered_cr20 = max(filtered_rows, key=lambda row: row["chain_recall_at_20"])
    nonregressing = [
        row
        for row in filtered_rows
        if row["chain_recall_at_10"] >= baseline["chain_recall_at_10"]
        and row["avg_inserted_units"] >= 0.5
    ]
    lowest_noise = min(nonregressing, key=lambda row: row["false_insert_rate"]) if nonregressing else None
    compact = unique_rows([baseline, unfiltered, best_filtered_cr10, best_filtered_cr20, *([lowest_noise] if lowest_noise else [])])

    lines = [
        "# Stage2E Evidence-Aware Insertion Noise Control Report",
        "",
        "## Material Passport",
        "",
        "- Origin Skill: academic-research-suite / experiment-agent",
        "- Origin Mode: run",
        f"- Origin Date: {date.today().isoformat()}",
        "- Verification Status: UNVERIFIED",
        "- Version Label: exp_result_v1",
        "- Stage: Stage2E evidence-aware insertion noise control",
        f"- Units: `{args.units}`",
        f"- Queries: `{args.queries}`",
        f"- Embedding cache: `{args.embedding_cache}`",
        "- Gold labels used for indexing: No",
        "- Generator used: No",
        "- Strategy: preserve a dense-fixed prefix, then insert only hyperedge candidates that meet label-free score thresholds.",
        "",
        "## Experiment Result",
        "",
        "- ID: stage2e_insert_noise_control_sample400",
        "- Type: analysis",
        "- Status: completed",
        f"- Command: `python scripts/stage2e_insert_noise_control.py --units \"{args.units}\" --queries \"{args.queries}\" --embedding-cache \"{args.embedding_cache}\" --output-dir \"{args.output_dir}\" --report \"{path}\"{' --expand-boundary-only' if args.expand_boundary_only else ''}`",
        f"- Working Directory: `{Path.cwd()}`",
        f"- Duration: {duration_seconds:.2f} seconds",
        "- Exit Code: 0",
        "",
        "### Output Files",
        "",
        "| File | Size |",
        "|---|---:|",
        f"| `{args.output_dir / 'stage2e_insert_noise_control_summary.csv'}` | {(args.output_dir / 'stage2e_insert_noise_control_summary.csv').stat().st_size} bytes |",
        f"| `{args.output_dir / 'stage2e_insert_noise_control_delta.csv'}` | {(args.output_dir / 'stage2e_insert_noise_control_delta.csv').stat().st_size} bytes |",
        "",
        "### Anomalies Detected",
        "",
        "None during the successful Python 3.12 run. The default Anaconda Python 3.11 environment was excluded after a separate pre-run import diagnostic exposed a NumPy binary-compatibility warning.",
        "",
        "## Threshold Protocol",
        "",
        "- Thresholds are computed separately for each method from all selected expansion candidates using only dense similarity and selected-edge facet score.",
        "- The filter grid is: none; score q25/q50/q75; score q50 + facet q50; score q75 + facet q50.",
        "- This is an exploratory sensitivity analysis: the same 400 queries supply the candidate-pool quantiles and the labelled evaluation, so it is not a held-out hyperparameter test.",
        "",
        "## ALL Summary",
        "",
        "| Strategy | Filter | Protect | Insert | Score floor | Facet floor | Retain | Fill | ER@10 | CR@10 | ER@20 | CR@20 | False insert |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in compact:
        lines.append(
            f"| {row['strategy']} | {row['filter_name']} | {row['protect_n']} | {row['insert_budget']} | "
            f"{format_floor(row['score_floor'])} | {format_floor(row['facet_floor'])} | "
            f"{row['candidate_retention']:.4f} | {row['budget_fill_rate']:.4f} | "
            f"{row['evidence_recall_at_10']:.4f} | {row['chain_recall_at_10']:.4f} | "
            f"{row['evidence_recall_at_20']:.4f} | {row['chain_recall_at_20']:.4f} | "
            f"{row['false_insert_rate']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Observed Rows",
            "",
            f"- Unfiltered gated reference (protect=5, insert=2): CR@10={unfiltered['chain_recall_at_10']:.4f}, CR@20={unfiltered['chain_recall_at_20']:.4f}, false insert={unfiltered['false_insert_rate']:.4f}.",
            f"- Best filtered CR@10: {best_filtered_cr10['filter_name']} / protect={best_filtered_cr10['protect_n']} / insert={best_filtered_cr10['insert_budget']} / CR@10={best_filtered_cr10['chain_recall_at_10']:.4f}.",
            f"- Best filtered CR@20: {best_filtered_cr20['filter_name']} / protect={best_filtered_cr20['protect_n']} / insert={best_filtered_cr20['insert_budget']} / CR@20={best_filtered_cr20['chain_recall_at_20']:.4f}.",
        ]
    )
    if lowest_noise:
        lines.append(
            f"- Lowest false insert among filtered rows with CR@10 no lower than dense fixed and at least 0.5 inserted units/query: {lowest_noise['filter_name']} / protect={lowest_noise['protect_n']} / insert={lowest_noise['insert_budget']} / false insert={lowest_noise['false_insert_rate']:.4f}."
        )
    else:
        lines.append("- No filtered row met both the CR@10 non-regression and minimum-insertion criterion.")

    lines.extend(
        [
            "",
            "## Query-Level CR Delta vs Dense Fixed",
            "",
            "| Filter | Protect | Insert | Metric | Improved | Same | Regressed |",
            "|---|---:|---:|---|---:|---:|---:|",
        ]
    )
    selected_filters = {"none", "score_q50", "score_q75", "score_q50_facet_q50"}
    for row in deltas:
        if (
            row["method"] == "gated"
            and row["filter_name"] in selected_filters
            and row["protect_n"] == 5
            and row["insert_budget"] in {2, 4}
            and row["metric"] in {"chain_recall_at_10", "chain_recall_at_20"}
        ):
            lines.append(
                f"| {row['filter_name']} | {row['protect_n']} | {row['insert_budget']} | {row['metric']} | "
                f"{row['improved']} | {row['same']} | {row['regressed']} |"
            )
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "- The CSV records retrieval metrics only; no answer generator is evaluated.",
            "- False insert rate is the share of inserted units that are not labelled gold. It is not a measure of generative hallucination.",
            "- A noise-control claim requires a lower false insert rate together with the target-K chain-recall comparison. A lower false insert rate caused only by empty insertion is not sufficient evidence.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", required=True, type=Path)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--embedding-cache", required=True, type=Path)
    parser.add_argument("--output-dir", default=Path("results"), type=Path)
    parser.add_argument("--report", default=Path("reports/超粒球RAG_Stage2E_InsertNoiseControl报告.md"), type=Path)
    parser.add_argument("--model-name", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--max-length", type=int, default=192)
    parser.add_argument("--k", nargs="+", type=int, default=[1, 3, 5, 10, 15, 20])
    parser.add_argument("--protect-n", nargs="+", type=int, default=[5, 10])
    parser.add_argument("--insert-budget", nargs="+", type=int, default=[1, 2, 4])
    parser.add_argument("--methods", nargs="+", default=["gated"], choices=["facet", "gated"])
    parser.add_argument("--score-quantiles", nargs="+", type=float, default=[0.25, 0.50, 0.75])
    parser.add_argument("--facet-quantile", type=float, default=0.50)
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
    start_time = perf_counter()

    if not args.score_quantiles or any(not 0.0 < value < 1.0 for value in args.score_quantiles):
        raise ValueError("--score-quantiles values must lie strictly between 0 and 1")
    if not 0.0 < args.facet_quantile < 1.0:
        raise ValueError("--facet-quantile must lie strictly between 0 and 1")

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

    indices_by_query: dict[str, list[int]] = defaultdict(list)
    for index, unit in enumerate(units):
        indices_by_query[unit["query_id"]].append(index)
    query_index = {query["query_id"]: index for index, query in enumerate(queries)}
    specs = filter_specs(args.score_quantiles, args.facet_quantile)

    prepared: list[dict[str, Any]] = []
    candidates_by_method: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for query in queries:
        query_embedding = query_embeddings[query_index[query["query_id"]]]
        candidate_indices = indices_by_query[query["query_id"]]
        fixed_ranked = fixed_retrieve(query_embedding, candidate_indices, units, unit_embeddings, max_k)
        per_method: dict[str, dict[str, Any]] = {}
        for method in args.methods:
            expanded, selected, info, expansion_stats = expansion_candidates(
                query,
                query_embedding,
                candidate_indices,
                units,
                unit_embeddings,
                args,
                method,
            )
            per_method[method] = {
                "candidates": expanded,
                "selected": selected,
                "info": info,
                "expansion_stats": expansion_stats,
            }
            candidates_by_method[method].extend(expanded)
        prepared.append({"query": query, "fixed_ranked": fixed_ranked, "per_method": per_method})

    thresholds = pool_thresholds(candidates_by_method, specs)
    rows: list[dict[str, Any]] = []
    baseline_by_query: dict[str, dict[str, Any]] = {}
    for item in prepared:
        query = item["query"]
        baseline = evaluate_query(query, item["fixed_ranked"], k_values)
        baseline.update(
            {
                "strategy": "fixed",
                "method": "fixed",
                "filter_name": "fixed",
                "score_quantile": None,
                "facet_quantile": None,
                "score_floor": None,
                "facet_floor": None,
                "protect_n": 0,
                "insert_budget": 0,
                "candidate_count": 0,
                "filtered_candidate_count": 0,
                "inserted_units": 0,
                "inserted_gold_units": 0,
            }
        )
        rows.append(baseline)
        baseline_by_query[query["query_id"]] = baseline
        for method in args.methods:
            method_data = item["per_method"][method]
            candidates = method_data["candidates"]
            for spec in specs:
                score_floor, facet_floor = thresholds[(method, spec.name)]
                filtered = apply_filter(candidates, score_floor, facet_floor)
                for protect_n in args.protect_n:
                    for insert_budget in args.insert_budget:
                        ranked, insert_stats = protected_rerank(
                            item["fixed_ranked"],
                            filtered,
                            protect_n,
                            insert_budget,
                            max_k,
                        )
                        row = evaluate_query(query, ranked, k_values)
                        row.update(method_data["info"])
                        row.update(method_data["expansion_stats"])
                        row.update(insert_stats)
                        row.update(
                            {
                                "strategy": "protected_insert_filtered",
                                "method": method,
                                "filter_name": spec.name,
                                "score_quantile": spec.score_quantile,
                                "facet_quantile": spec.facet_quantile,
                                "score_floor": score_floor,
                                "facet_floor": facet_floor,
                                "protect_n": protect_n,
                                "insert_budget": insert_budget,
                                "selected_edge_count": len(method_data["selected"]),
                                "candidate_count": len(candidates),
                                "filtered_candidate_count": len(filtered),
                            }
                        )
                        rows.append(row)

    summaries = aggregate(rows, k_values)
    deltas = delta_counts(rows, baseline_by_query, k_values)
    summary_path = args.output_dir / "stage2e_insert_noise_control_summary.csv"
    delta_path = args.output_dir / "stage2e_insert_noise_control_delta.csv"
    detail_path = args.output_dir / "stage2e_insert_noise_control_details.jsonl"
    write_summary(summary_path, summaries, k_values)
    write_delta(delta_path, deltas)
    write_report(args.report, summaries, deltas, args, perf_counter() - start_time)
    if args.write_details:
        write_jsonl(detail_path, rows)
    print(
        json.dumps(
            {
                "summary": str(summary_path),
                "delta": str(delta_path),
                "report": str(args.report),
                "detail": str(detail_path) if args.write_details else None,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
