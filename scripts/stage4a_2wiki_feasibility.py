"""Run the frozen Stage4A 2WikiMultiHopQA feasibility pilot."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
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


Q25_FLOOR = 0.1957079917192459
EXPECTED_PILOT_ID_SHA256 = "6E00E3FA59C930DB1ABDA099A90A919A0FA4C1F6C8FA816812ABFD51FC9CA2F4"


@dataclass(frozen=True)
class Strategy:
    strategy_id: str
    score_floor: float | None
    protect_n: int
    insert_budget: int
    role: str


STRATEGIES = (
    Strategy("dense_fixed", None, 0, 0, "saturation baseline"),
    Strategy("allquery_unfiltered_p10_i4", None, 10, 4, "candidate-availability control"),
    Strategy("allquery_q25_p10_i4", Q25_FLOOR, 10, 4, "transferred protected-insertion pilot"),
)


def digest_ids(ids: list[str]) -> str:
    payload = "\n".join(sorted(ids)) + "\n"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        return 0.0, 0.0
    p = successes / total
    denominator = 1.0 + z * z / total
    center = (p + z * z / (2.0 * total)) / denominator
    spread = z * math.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total * total)) / denominator
    return max(0.0, center - spread), min(1.0, center + spread)


def preflight(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    source_audit: dict[str, Any],
) -> dict[str, Any]:
    query_ids = [str(row["query_id"]) for row in queries]
    sample_ids = [str(row["sample_id"]) for row in queries]
    unit_query_ids = {str(row["query_id"]) for row in units}
    question_types = Counter(str(row.get("metadata", {}).get("type")) for row in queries)
    datasets = Counter(str(row["dataset"]) for row in queries)
    missing_gold = sum(1 for row in queries if not row.get("gold_unit_ids"))
    duplicate_query_ids = len(query_ids) - len(set(query_ids))
    pilot_digest = digest_ids(sample_ids)

    if len(queries) != 400:
        raise ValueError(f"Expected 400 Stage4A queries, found {len(queries)}")
    if datasets != Counter({"2wikimultihopqa": 400}):
        raise ValueError(f"Unexpected dataset counts: {dict(datasets)}")
    if duplicate_query_ids:
        raise ValueError(f"Duplicate Stage4A query IDs: {duplicate_query_ids}")
    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Duplicate Stage4A sample IDs")
    if missing_gold:
        raise ValueError(f"Queries without mapped gold: {missing_gold}")
    if unit_query_ids != set(query_ids):
        raise ValueError(
            f"Unit/query mismatch: missing={len(set(query_ids) - unit_query_ids)}, "
            f"foreign={len(unit_query_ids - set(query_ids))}"
        )
    if pilot_digest != EXPECTED_PILOT_ID_SHA256:
        raise ValueError(f"Pilot ID digest mismatch: {pilot_digest}")
    if pilot_digest != source_audit["data_boundary"]["pilot_query_id_sha256"]:
        raise ValueError("Pilot ID digest differs from source audit")
    if source_audit["data_boundary"]["reservation_content_written"] is not False:
        raise ValueError("Source audit does not preserve the reservation-content boundary")
    mapping = source_audit["mapping"]
    if mapping["queries"] != 400 or mapping["queries_missing_gold"] != 0:
        raise ValueError("Source-audit mapping count or missing-gold count failed")
    if mapping["supporting_fact_mapping_rate"] < 0.99:
        raise ValueError("Source-audit supporting-fact mapping rate is below 0.99")
    if dict(sorted(question_types.items())) != mapping["question_types"]:
        raise ValueError("Question-type counts differ from source audit")

    return {
        "queries": len(queries),
        "units": len(units),
        "gold_units": sum(len(row["gold_unit_ids"]) for row in queries),
        "queries_missing_gold": missing_gold,
        "duplicate_query_ids": duplicate_query_ids,
        "question_types": dict(sorted(question_types.items())),
        "pilot_query_id_sha256": pilot_digest,
        "mapping_rate": float(mapping["supporting_fact_mapping_rate"]),
        "provenance_status": source_audit["provenance_status"],
    }


def strategy_metrics(
    query: dict[str, Any],
    ranked: list[dict[str, Any]],
    inserted: dict[str, int],
    raw_candidates: int,
    filtered_candidates: int,
) -> dict[str, Any]:
    evaluated = evaluate_query(query, ranked, [20])
    return {
        "er20": evaluated["evidence_recall_at_20"],
        "cr20": evaluated["chain_recall_at_20"],
        "triggered": int(inserted["inserted_units"] > 0),
        **inserted,
        "raw_candidate_count": raw_candidates,
        "filtered_candidate_count": filtered_candidates,
        "score_floor_removed": raw_candidates - filtered_candidates,
    }


def run_queries(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    indices_by_query: dict[str, list[int]] = defaultdict(list)
    for index, unit in enumerate(units):
        indices_by_query[str(unit["query_id"])].append(index)
    query_index = {str(query["query_id"]): index for index, query in enumerate(queries)}
    expansion_args = copy.copy(args)
    expansion_args.expand_boundary_only = False
    rows: list[dict[str, Any]] = []
    zero_insert = {"inserted_units": 0, "inserted_gold_units": 0, "inserted_non_gold_units": 0}

    for query in queries:
        query_id = str(query["query_id"])
        query_embedding = query_embeddings[query_index[query_id]]
        candidate_indices = indices_by_query[query_id]
        fixed_ranked = fixed_retrieve(query_embedding, candidate_indices, units, unit_embeddings, 20)
        expanded, selected_edges, _, _ = expansion_candidates(
            query,
            query_embedding,
            candidate_indices,
            units,
            unit_embeddings,
            expansion_args,
            "gated",
        )
        q25_candidates = [candidate for candidate in expanded if candidate["score"] >= args.q25_floor]
        unfiltered_ranked, unfiltered_insert = protected_rerank(fixed_ranked, expanded, 10, 4, 20)
        q25_ranked, q25_insert = protected_rerank(fixed_ranked, q25_candidates, 10, 4, 20)
        metrics = {
            "dense": strategy_metrics(query, fixed_ranked, zero_insert, 0, 0),
            "unfiltered": strategy_metrics(
                query, unfiltered_ranked, unfiltered_insert, len(expanded), len(expanded)
            ),
            "q25": strategy_metrics(query, q25_ranked, q25_insert, len(expanded), len(q25_candidates)),
        }
        dense_cr = int(metrics["dense"]["cr20"] > 0.5)
        row: dict[str, Any] = {
            "query_id": query_id,
            "sample_id": str(query["sample_id"]),
            "question_type": str(query.get("metadata", {}).get("type")),
            "num_candidate_units": int(query["num_candidate_units"]),
            "num_gold_units": int(query["num_gold_units"]),
            "selected_edge_count": len(selected_edges),
        }
        for prefix, values in metrics.items():
            for key, value in values.items():
                row[f"{prefix}_{key}"] = value
            strategy_cr = int(values["cr20"] > 0.5)
            row[f"{prefix}_gain_event"] = int(dense_cr == 0 and strategy_cr == 1)
            row[f"{prefix}_harm_event"] = int(dense_cr == 1 and strategy_cr == 0)
            row[f"{prefix}_completion_opportunity"] = int(values["triggered"] > 0 and dense_cr == 0)
        rows.append(row)
    return rows


def summarize_slice(items: list[dict[str, Any]], slice_name: str, strategy: Strategy) -> dict[str, Any]:
    prefix = {
        "dense_fixed": "dense",
        "allquery_unfiltered_p10_i4": "unfiltered",
        "allquery_q25_p10_i4": "q25",
    }[strategy.strategy_id]
    n = len(items)
    inserted = sum(int(row[f"{prefix}_inserted_units"]) for row in items)
    inserted_gold = sum(int(row[f"{prefix}_inserted_gold_units"]) for row in items)
    gains = sum(int(row[f"{prefix}_gain_event"]) for row in items)
    harms = sum(int(row[f"{prefix}_harm_event"]) for row in items)
    opportunities = sum(int(row[f"{prefix}_completion_opportunity"]) for row in items)
    gain_low, gain_high = wilson_interval(gains, n)
    harm_low, harm_high = wilson_interval(harms, n)
    return {
        "slice": slice_name,
        "strategy_id": strategy.strategy_id,
        "role": strategy.role,
        "score_floor": "" if strategy.score_floor is None else strategy.score_floor,
        "protect_n": strategy.protect_n,
        "insert_budget": strategy.insert_budget,
        "queries": n,
        "evidence_recall_at_20": sum(float(row[f"{prefix}_er20"]) for row in items) / n,
        "chain_recall_at_20": sum(float(row[f"{prefix}_cr20"]) for row in items) / n,
        "trigger_rate": sum(int(row[f"{prefix}_triggered"]) for row in items) / n,
        "avg_inserted_units": inserted / n,
        "insert_yield": inserted_gold / max(inserted, 1),
        "conditional_false_insert_rate": (inserted - inserted_gold) / max(inserted, 1),
        "raw_candidates": sum(int(row[f"{prefix}_raw_candidate_count"]) for row in items),
        "filtered_candidates": sum(int(row[f"{prefix}_filtered_candidate_count"]) for row in items),
        "score_floor_removed": sum(int(row[f"{prefix}_score_floor_removed"]) for row in items),
        "gain_events": gains,
        "harm_events": harms,
        "net_completed_chain_change": gains - harms,
        "gain_prevalence": gains / n,
        "gain_wilson95_low": gain_low,
        "gain_wilson95_high": gain_high,
        "harm_prevalence": harms / n,
        "harm_wilson95_low": harm_low,
        "harm_wilson95_high": harm_high,
        "completion_opportunities": opportunities,
        "completion_precision": gains / max(opportunities, 1),
    }


def aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    slices: list[tuple[str, list[dict[str, Any]]]] = [("ALL", rows)]
    for question_type in sorted({str(row["question_type"]) for row in rows}):
        slices.append((question_type, [row for row in rows if row["question_type"] == question_type]))
    return [summarize_slice(items, name, strategy) for name, items in slices for strategy in STRATEGIES]


def bootstrap(rows: list[dict[str, Any]], iterations: int, seed: int) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(rows), size=(iterations, len(rows)), dtype=np.int32)
    prefixes = {"dense_fixed": "dense", "allquery_unfiltered_p10_i4": "unfiltered", "allquery_q25_p10_i4": "q25"}
    comparisons = (
        ("q25_vs_dense", "allquery_q25_p10_i4", "dense_fixed"),
        ("unfiltered_vs_dense", "allquery_unfiltered_p10_i4", "dense_fixed"),
        ("q25_vs_unfiltered", "allquery_q25_p10_i4", "allquery_unfiltered_p10_i4"),
    )
    output: list[dict[str, Any]] = []
    for comparison_id, strategy_a, strategy_b in comparisons:
        for metric, suffix in (("evidence_recall_at_20", "er20"), ("chain_recall_at_20", "cr20")):
            values_a = np.array([row[f"{prefixes[strategy_a]}_{suffix}"] for row in rows], dtype="float64")
            values_b = np.array([row[f"{prefixes[strategy_b]}_{suffix}"] for row in rows], dtype="float64")
            deltas = values_a - values_b
            samples = deltas[indices].mean(axis=1)
            output.append(
                {
                    "comparison_id": comparison_id,
                    "strategy_a": strategy_a,
                    "strategy_b": strategy_b,
                    "metric": metric,
                    "queries": len(rows),
                    "iterations": iterations,
                    "seed": seed,
                    "observed_a": float(values_a.mean()),
                    "observed_b": float(values_b.mean()),
                    "observed_delta": float(deltas.mean()),
                    "ci95_low": float(np.quantile(samples, 0.025)),
                    "ci95_high": float(np.quantile(samples, 0.975)),
                    "improved": int(np.sum(deltas > 1e-12)),
                    "same": int(np.sum(np.abs(deltas) <= 1e-12)),
                    "regressed": int(np.sum(deltas < -1e-12)),
                }
            )
    return output


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summary_row(rows: list[dict[str, Any]], strategy_id: str) -> dict[str, Any]:
    return next(row for row in rows if row["slice"] == "ALL" and row["strategy_id"] == strategy_id)


def write_report(
    path: Path,
    audit: dict[str, Any],
    summaries: list[dict[str, Any]],
    bootstrap_rows: list[dict[str, Any]],
    source_audit: dict[str, Any],
    args: argparse.Namespace,
    duration: float,
) -> None:
    dense = summary_row(summaries, "dense_fixed")
    unfiltered = summary_row(summaries, "allquery_unfiltered_p10_i4")
    q25 = summary_row(summaries, "allquery_q25_p10_i4")
    gates = [
        ("Mapping >= 0.99 and zero missing gold", audit["mapping_rate"] >= 0.99 and audit["queries_missing_gold"] == 0),
        ("Dense CR@20 < 0.95", dense["chain_recall_at_20"] < 0.95),
        ("q25 trigger rate >= 0.10", q25["trigger_rate"] >= 0.10),
        ("q25 gain events >= 10", q25["gain_events"] >= 10),
        ("q25 net completed-chain change > 0", q25["net_completed_chain_change"] > 0),
        ("q25 score floor removes candidates", q25["score_floor_removed"] > 0),
    ]
    promoted = all(result for _, result in gates)
    summary_path = args.output_dir / "stage4a_2wiki_strategy_summary.csv"
    bootstrap_path = args.output_dir / "stage4a_2wiki_bootstrap.csv"
    query_path = args.output_dir / "stage4a_2wiki_query_audit.csv"
    lines = [
        "# Stage4A 2Wiki Feasibility Pilot Report",
        "",
        "## Material Passport",
        "",
        "- Origin Skill: academic-research-suite / experiment-agent",
        "- Origin Mode: run",
        f"- Origin Date: {date.today().isoformat()}",
        "- Verification Status: UNVERIFIED",
        "- Version Label: exp_result_v1",
        "- Protocol: `docs/STAGE4A_PROTOCOL.md`, committed before data extraction and metrics",
        f"- Provenance status: {source_audit['provenance_status']}",
        "- Gold labels used for indexing, ranking, score filtering, expansion, or threshold selection: No",
        "- Controller fitting: No",
        "- Generator used: No",
        "",
        "## Run Record",
        "",
        f"- Duration: {duration:.2f} seconds",
        "- Exit Code: 0",
        f"- Queries / units / gold units: {audit['queries']} / {audit['units']} / {audit['gold_units']}",
        f"- Pilot ID SHA256: `{audit['pilot_query_id_sha256']}`",
        f"- Frozen q25 floor: {args.q25_floor:.16f}",
        f"- Embedding model / max length: `{args.model_name}` / {args.max_length}",
        "",
        "## Outputs",
        "",
        "| File | Bytes |",
        "|---|---:|",
        f"| `{query_path}` | {query_path.stat().st_size} |",
        f"| `{summary_path}` | {summary_path.stat().st_size} |",
        f"| `{bootstrap_path}` | {bootstrap_path.stat().st_size} |",
        "",
        "## Overall Results",
        "",
        "| Strategy | ER@20 | CR@20 | Trigger | Avg insert | Gain | Harm | Net | Removed |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in (dense, unfiltered, q25):
        lines.append(
            f"| {row['strategy_id']} | {row['evidence_recall_at_20']:.4f} | "
            f"{row['chain_recall_at_20']:.4f} | {row['trigger_rate']:.4f} | "
            f"{row['avg_inserted_units']:.4f} | {row['gain_events']} | {row['harm_events']} | "
            f"{row['net_completed_chain_change']} | {row['score_floor_removed']} |"
        )
    lines.extend(["", "## Promotion Gate", "", "| Condition | Result |", "|---|---|"])
    lines.extend(f"| {label} | {'PASS' if result else 'FAIL'} |" for label, result in gates)
    lines.extend(
        [
            "",
            f"- Overall Stage4B development-branch decision: {'PROMOTE' if promoted else 'STOP'}.",
            "",
            "## Wilson Intervals",
            "",
            f"- q25 gain prevalence: {q25['gain_prevalence']:.4f}, 95% Wilson [{q25['gain_wilson95_low']:.4f}, {q25['gain_wilson95_high']:.4f}].",
            f"- q25 harm prevalence: {q25['harm_prevalence']:.4f}, 95% Wilson [{q25['harm_wilson95_low']:.4f}, {q25['harm_wilson95_high']:.4f}].",
            f"- q25 completion precision among {q25['completion_opportunities']} triggered baseline-incomplete queries: {q25['completion_precision']:.4f}.",
            "",
            "## Bootstrap Boundary",
            "",
            f"- Paired bootstrap rows: {len(bootstrap_rows)}; 10,000 resamples; seed {args.bootstrap_seed}.",
            "- Intervals are descriptive pilot estimates; no p-values or confirmatory significance claims are made.",
            "",
            "## Interpretation Boundary",
            "",
            "- This pilot evaluates mapping, saturation, and gain-event availability only; it does not validate a controller.",
            "- The reserved Stage4B slice was not embedded or evaluated.",
            "- Results remain provenance-downgraded until reconciliation with the official archive.",
            "- Stage3B remains locked and is not affected by this pilot.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", required=True, type=Path)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--source-audit", default=Path("docs/STAGE4A_SOURCE_AUDIT.json"), type=Path)
    parser.add_argument("--embedding-cache", required=True, type=Path)
    parser.add_argument("--output-dir", default=Path("results"), type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--model-name", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--max-length", type=int, default=192)
    parser.add_argument("--bootstrap-iterations", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260714)
    parser.add_argument("--q25-floor", type=float, default=Q25_FLOOR)
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start = perf_counter()
    if args.bootstrap_iterations != 10000 or args.bootstrap_seed != 20260714:
        raise ValueError("Stage4A requires 10,000 bootstrap iterations and seed 20260714")
    if not math.isclose(args.q25_floor, Q25_FLOOR, abs_tol=1e-15):
        raise ValueError(f"Stage4A q25 floor must remain {Q25_FLOOR}")
    if args.max_length != 192:
        raise ValueError("Stage4A maximum sequence length must remain 192")

    units = load_jsonl(args.units)
    queries = load_jsonl(args.queries)
    source_audit = json.loads(args.source_audit.read_text(encoding="utf-8"))
    audit = preflight(units, queries, source_audit)
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
    if unit_embeddings.shape[0] != len(units) or query_embeddings.shape[0] != len(queries):
        raise ValueError(
            f"Embedding/corpus mismatch: units={unit_embeddings.shape[0]}/{len(units)}, "
            f"queries={query_embeddings.shape[0]}/{len(queries)}"
        )

    rows = run_queries(units, queries, unit_embeddings, query_embeddings, args)
    summaries = aggregate(rows)
    bootstrap_rows = bootstrap(rows, args.bootstrap_iterations, args.bootstrap_seed)
    query_path = args.output_dir / "stage4a_2wiki_query_audit.csv"
    summary_path = args.output_dir / "stage4a_2wiki_strategy_summary.csv"
    bootstrap_path = args.output_dir / "stage4a_2wiki_bootstrap.csv"
    write_csv(query_path, rows)
    write_csv(summary_path, summaries)
    write_csv(bootstrap_path, bootstrap_rows)
    write_report(
        args.report,
        audit,
        summaries,
        bootstrap_rows,
        source_audit,
        args,
        perf_counter() - start,
    )
    print(
        json.dumps(
            {
                "audit": audit,
                "query_audit": str(query_path),
                "strategy_summary": str(summary_path),
                "bootstrap": str(bootstrap_path),
                "report": str(args.report),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
