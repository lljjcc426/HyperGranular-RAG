"""Run the frozen Stage4A-R2 official event-rate estimation experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from datetime import date
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np

from stage2_dense_replication import (
    load_jsonl,
    load_or_build_embeddings,
    normalize_matrix,
)
from stage4a_2wiki_feasibility import (
    Q25_FLOOR,
    aggregate,
    run_queries,
    summary_row,
    write_csv,
)


EXPECTED_QUERIES = 4500
BOOTSTRAP_ITERATIONS = 10000
BOOTSTRAP_SEED = 20260712
TARGET_HALFWIDTH = 0.005
EXPECTED_SAMPLE_PLAN_SHA256 = "5C43CA352900B559EE3A71975BFD018854B0E8E66CC98B29D7A1710C751DD73D"
EXPECTED_ARCHIVE_SHA256 = "95DF2BF56FDABE034E27AEBC580E02264232203CF52552F9EFE8A919E5529EEF"
EXPECTED_DEV_SHA256 = "79F77AE104088EA8E25B1A65DBECE768D45771194663BC5660EC9A98070DADF5"


def digest_ids(ids: list[str]) -> str:
    payload = "\n".join(sorted(ids)) + "\n"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def preflight(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    source_audit: dict[str, Any],
) -> dict[str, Any]:
    query_ids = [str(row["query_id"]) for row in queries]
    sample_ids = [str(row["sample_id"]) for row in queries]
    unit_query_ids = {str(row["query_id"]) for row in units}
    datasets = Counter(str(row["dataset"]) for row in queries)
    question_types = Counter(
        str(row.get("metadata", {}).get("type")) for row in queries
    )
    missing_gold = sum(1 for row in queries if not row.get("gold_unit_ids"))
    development_digest = digest_ids(sample_ids)
    boundary = source_audit["data_boundary"]
    mapping = source_audit["mapping"]
    official = source_audit["official_archive"]

    if len(queries) != EXPECTED_QUERIES:
        raise ValueError(f"Expected {EXPECTED_QUERIES} Stage4A-R2 queries")
    if datasets != Counter({"2wikimultihopqa": EXPECTED_QUERIES}):
        raise ValueError(f"Unexpected dataset counts: {dict(datasets)}")
    if len(query_ids) != len(set(query_ids)) or len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Duplicate Stage4A-R2 query or sample IDs")
    if unit_query_ids != set(query_ids):
        raise ValueError("Stage4A-R2 unit/query ID sets differ")
    if missing_gold:
        raise ValueError(f"Stage4A-R2 queries missing mapped gold: {missing_gold}")
    if source_audit.get("provenance_status") != "OFFICIAL_APRIL7_ARCHIVE":
        raise ValueError("Stage4A-R2 requires official April 7 provenance")
    if official["sha256"] != EXPECTED_ARCHIVE_SHA256 or official["dev_json_sha256"] != EXPECTED_DEV_SHA256:
        raise ValueError("Stage4A-R2 official source hashes differ from protocol")
    if development_digest != boundary["development_query_id_sha256"]:
        raise ValueError("Development ID digest differs from source audit")
    if boundary["development_queries"] != EXPECTED_QUERIES:
        raise ValueError("Source audit development count differs")
    if boundary["reservation_queries"] != EXPECTED_QUERIES:
        raise ValueError("Source audit reservation count differs")
    if boundary["development_reservation_overlap"] != 0:
        raise ValueError("Source audit reports development/reservation overlap")
    if boundary["reservation_content_written"] is not False:
        raise ValueError("Source audit does not preserve reservation boundary")
    if mapping["queries"] != EXPECTED_QUERIES:
        raise ValueError("Source audit mapping count differs")
    if mapping["supporting_fact_mapping_rate"] != 1.0 or mapping["queries_missing_gold"] != 0:
        raise ValueError("Source audit mapping integrity failed")
    if dict(sorted(question_types.items())) != mapping["question_types"]:
        raise ValueError("Question-type counts differ from source audit")

    return {
        "queries": len(queries),
        "units": len(units),
        "gold_units": sum(len(row["gold_unit_ids"]) for row in queries),
        "queries_missing_gold": missing_gold,
        "question_types": dict(sorted(question_types.items())),
        "development_query_id_sha256": development_digest,
        "reservation_query_id_sha256": boundary["reservation_query_id_sha256"],
        "mapping_rate": float(mapping["supporting_fact_mapping_rate"]),
        "provenance_status": source_audit["provenance_status"],
    }


def chunked_bootstrap(
    rows: list[dict[str, Any]],
    iterations: int,
    seed: int,
    chunk_size: int = 250,
) -> list[dict[str, Any]]:
    prefixes = {
        "dense_fixed": "dense",
        "allquery_unfiltered_p10_i4": "unfiltered",
        "allquery_q25_p10_i4": "q25",
    }
    comparisons = (
        ("q25_vs_dense", "allquery_q25_p10_i4", "dense_fixed"),
        ("unfiltered_vs_dense", "allquery_unfiltered_p10_i4", "dense_fixed"),
        ("q25_vs_unfiltered", "allquery_q25_p10_i4", "allquery_unfiltered_p10_i4"),
    )
    specs = []
    for comparison_id, strategy_a, strategy_b in comparisons:
        for metric, suffix in (
            ("evidence_recall_at_20", "er20"),
            ("chain_recall_at_20", "cr20"),
        ):
            values_a = np.array(
                [row[f"{prefixes[strategy_a]}_{suffix}"] for row in rows],
                dtype="float64",
            )
            values_b = np.array(
                [row[f"{prefixes[strategy_b]}_{suffix}"] for row in rows],
                dtype="float64",
            )
            specs.append(
                {
                    "comparison_id": comparison_id,
                    "strategy_a": strategy_a,
                    "strategy_b": strategy_b,
                    "metric": metric,
                    "values_a": values_a,
                    "values_b": values_b,
                    "deltas": values_a - values_b,
                    "samples": np.empty(iterations, dtype="float64"),
                }
            )

    rng = np.random.default_rng(seed)
    for start in range(0, iterations, chunk_size):
        stop = min(start + chunk_size, iterations)
        indices = rng.integers(
            0,
            len(rows),
            size=(stop - start, len(rows)),
            dtype=np.int32,
        )
        for spec in specs:
            spec["samples"][start:stop] = spec["deltas"][indices].mean(axis=1)

    output = []
    for spec in specs:
        deltas = spec["deltas"]
        output.append(
            {
                "comparison_id": spec["comparison_id"],
                "strategy_a": spec["strategy_a"],
                "strategy_b": spec["strategy_b"],
                "metric": spec["metric"],
                "queries": len(rows),
                "iterations": iterations,
                "seed": seed,
                "observed_a": float(spec["values_a"].mean()),
                "observed_b": float(spec["values_b"].mean()),
                "observed_delta": float(deltas.mean()),
                "ci95_low": float(np.quantile(spec["samples"], 0.025)),
                "ci95_high": float(np.quantile(spec["samples"], 0.975)),
                "improved": int(np.sum(deltas > 1e-12)),
                "same": int(np.sum(np.abs(deltas) <= 1e-12)),
                "regressed": int(np.sum(deltas < -1e-12)),
            }
        )
    return output


def exact_mcnemar_pvalue(gains: int, harms: int) -> float:
    discordant = gains + harms
    if discordant == 0:
        return 1.0
    tail = min(gains, harms)
    probability = sum(
        math.comb(discordant, value) * 0.5**discordant
        for value in range(tail + 1)
    )
    return min(1.0, 2.0 * probability)


def build_inference(
    summaries: list[dict[str, Any]],
    audit: dict[str, Any],
) -> dict[str, Any]:
    dense = summary_row(summaries, "dense_fixed")
    q25 = summary_row(summaries, "allquery_q25_p10_i4")
    gain_halfwidth = (q25["gain_wilson95_high"] - q25["gain_wilson95_low"]) / 2.0
    harm_halfwidth = (q25["harm_wilson95_high"] - q25["harm_wilson95_low"]) / 2.0
    integrity_gates = {
        "official_provenance": audit["provenance_status"] == "OFFICIAL_APRIL7_ARCHIVE",
        "development_queries": audit["queries"] == EXPECTED_QUERIES,
        "mapping_complete": audit["mapping_rate"] == 1.0 and audit["queries_missing_gold"] == 0,
        "reservation_locked": bool(audit["reservation_query_id_sha256"]),
    }
    precision_gates = {
        "gain_halfwidth_at_most_0.005": gain_halfwidth <= TARGET_HALFWIDTH + 1e-15,
        "harm_halfwidth_at_most_0.005": harm_halfwidth <= TARGET_HALFWIDTH + 1e-15,
    }
    if not all(integrity_gates.values()):
        decision = "INTEGRITY_FAILURE"
    elif all(precision_gates.values()):
        decision = "ESTIMATION_COMPLETE"
    else:
        decision = "ESTIMATION_PRECISION_NOT_MET"
    gains = int(q25["gain_events"])
    harms = int(q25["harm_events"])
    return {
        "protocol": "docs/STAGE4A_R2_PROTOCOL.md",
        "primary": {
            "q25_gain": {
                "events": gains,
                "queries": EXPECTED_QUERIES,
                "prevalence": q25["gain_prevalence"],
                "wilson95_low": q25["gain_wilson95_low"],
                "wilson95_high": q25["gain_wilson95_high"],
                "halfwidth": gain_halfwidth,
            },
            "q25_harm": {
                "events": harms,
                "queries": EXPECTED_QUERIES,
                "prevalence": q25["harm_prevalence"],
                "wilson95_low": q25["harm_wilson95_low"],
                "wilson95_high": q25["harm_wilson95_high"],
                "halfwidth": harm_halfwidth,
            },
        },
        "secondary": {
            "dense_cr20": dense["chain_recall_at_20"],
            "q25_cr20": q25["chain_recall_at_20"],
            "cr20_delta": q25["chain_recall_at_20"] - dense["chain_recall_at_20"],
            "discordant_queries": gains + harms,
            "gain_events": gains,
            "harm_events": harms,
            "exact_conditional_mcnemar_two_sided_p": exact_mcnemar_pvalue(gains, harms),
            "alpha": 0.05,
        },
        "integrity_gates": integrity_gates,
        "precision_gates": precision_gates,
        "decision": decision,
        "controller_training_authorized": False,
        "reservation_metrics_authorized": False,
    }


def write_inference(path: Path, inference: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(inference, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(
    path: Path,
    audit: dict[str, Any],
    summaries: list[dict[str, Any]],
    bootstrap_rows: list[dict[str, Any]],
    inference: dict[str, Any],
    args: argparse.Namespace,
    duration: float,
) -> None:
    dense = summary_row(summaries, "dense_fixed")
    unfiltered = summary_row(summaries, "allquery_unfiltered_p10_i4")
    q25 = summary_row(summaries, "allquery_q25_p10_i4")
    query_path = args.output_dir / "stage4a_r2_query_audit.csv"
    summary_path = args.output_dir / "stage4a_r2_strategy_summary.csv"
    bootstrap_path = args.output_dir / "stage4a_r2_bootstrap.csv"
    inference_path = args.output_dir / "stage4a_r2_inference.json"
    lines = [
        "# 超粒球RAG Stage4A-R2 官方事件率估计报告",
        "",
        "## Material Passport",
        "",
        "- Origin Skill: academic-research-suite / experiment-agent",
        "- Origin Mode: run",
        f"- Origin Date: {date.today().isoformat()}",
        "- Verification Status: UNVERIFIED",
        "- Version Label: exp_result_r2_v1",
        "- Protocol: `docs/STAGE4A_R2_PROTOCOL.md`, committed before official row extraction",
        "- Provenance: official April 7 archive",
        "- Gold labels used for retrieval decisions: No",
        "- Controller fitting: No",
        "- Generator used: No",
        "",
        "## Run Record",
        "",
        f"- Duration: {duration:.2f} seconds",
        "- Exit Code: 0",
        f"- Queries / units / gold units: {audit['queries']} / {audit['units']} / {audit['gold_units']}",
        f"- Development ID SHA256: `{audit['development_query_id_sha256']}`",
        f"- Reservation ID SHA256: `{audit['reservation_query_id_sha256']}`",
        f"- Frozen q25 floor: {args.q25_floor:.16f}",
        f"- Embedding model / max length: `{args.model_name}` / {args.max_length}",
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
    gain = inference["primary"]["q25_gain"]
    harm = inference["primary"]["q25_harm"]
    secondary = inference["secondary"]
    lines.extend(
        [
            "",
            "## Primary Event-rate Estimates",
            "",
            f"- Gain: {gain['events']}/{gain['queries']} = {gain['prevalence']:.6f}; Wilson 95% [{gain['wilson95_low']:.6f}, {gain['wilson95_high']:.6f}], half-width {gain['halfwidth']:.6f}.",
            f"- Harm: {harm['events']}/{harm['queries']} = {harm['prevalence']:.6f}; Wilson 95% [{harm['wilson95_low']:.6f}, {harm['wilson95_high']:.6f}], half-width {harm['halfwidth']:.6f}.",
            f"- Precision decision: `{inference['decision']}`.",
            "",
            "## Secondary Paired Analysis",
            "",
            f"- q25 minus dense CR@20: {secondary['cr20_delta']:.6f}.",
            f"- Discordant queries: {secondary['discordant_queries']} ({secondary['gain_events']} gains, {secondary['harm_events']} harms).",
            f"- Exact conditional two-sided McNemar p-value: {secondary['exact_conditional_mcnemar_two_sided_p']:.8g}.",
            f"- Paired bootstrap: {len(bootstrap_rows)} rows, {BOOTSTRAP_ITERATIONS} resamples, seed {BOOTSTRAP_SEED}.",
            "",
            "## Interpretation Boundary",
            "",
            "- Primary inference is the official gain/harm prevalence with interval precision, not the p-value.",
            "- Question-type rows are descriptive and are not separate confirmatory tests.",
            "- No q25 tuning, boundary-rule repair, controller fitting, or reservation metrics are authorized by this stage.",
            "- Stage3B remains locked.",
            "",
            "## Outputs",
            "",
            "| File | Bytes |",
            "|---|---:|",
            f"| `{query_path}` | {query_path.stat().st_size} |",
            f"| `{summary_path}` | {summary_path.stat().st_size} |",
            f"| `{bootstrap_path}` | {bootstrap_path.stat().st_size} |",
            f"| `{inference_path}` | {inference_path.stat().st_size} |",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", required=True, type=Path)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--source-audit", required=True, type=Path)
    parser.add_argument("--sample-plan", required=True, type=Path)
    parser.add_argument("--embedding-cache", required=True, type=Path)
    parser.add_argument("--output-dir", default=Path("results"), type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--model-name", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--max-length", type=int, default=192)
    parser.add_argument("--bootstrap-iterations", type=int, default=BOOTSTRAP_ITERATIONS)
    parser.add_argument("--bootstrap-seed", type=int, default=BOOTSTRAP_SEED)
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
    if args.bootstrap_iterations != BOOTSTRAP_ITERATIONS or args.bootstrap_seed != BOOTSTRAP_SEED:
        raise ValueError("Stage4A-R2 bootstrap configuration differs from protocol")
    if not math.isclose(args.q25_floor, Q25_FLOOR, abs_tol=1e-15):
        raise ValueError(f"Stage4A-R2 q25 floor must remain {Q25_FLOOR}")
    if args.max_length != 192:
        raise ValueError("Stage4A-R2 maximum sequence length must remain 192")
    sample_plan = json.loads(args.sample_plan.read_text(encoding="utf-8"))
    if sha256_file(args.sample_plan) != EXPECTED_SAMPLE_PLAN_SHA256:
        raise ValueError("Stage4A-R2 sample-plan SHA differs from protocol")
    if sample_plan["status"] != "FROZEN_APPROVED_BEFORE_OFFICIAL_ROW_EXTRACTION":
        raise ValueError("Stage4A-R2 sample plan is not frozen")
    if sample_plan["primary_design"]["development_n"] != EXPECTED_QUERIES:
        raise ValueError("Stage4A-R2 sample plan query count differs")

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
        raise ValueError("Stage4A-R2 embedding/corpus dimensions differ")

    rows = run_queries(units, queries, unit_embeddings, query_embeddings, args)
    summaries = aggregate(rows)
    r2_roles = {
        "dense_fixed": "official saturation baseline",
        "allquery_unfiltered_p10_i4": "official candidate-availability control",
        "allquery_q25_p10_i4": "official frozen transferred policy",
    }
    for row in summaries:
        row["role"] = r2_roles[row["strategy_id"]]
    bootstrap_rows = chunked_bootstrap(rows, args.bootstrap_iterations, args.bootstrap_seed)
    inference = build_inference(summaries, audit)
    query_path = args.output_dir / "stage4a_r2_query_audit.csv"
    summary_path = args.output_dir / "stage4a_r2_strategy_summary.csv"
    bootstrap_path = args.output_dir / "stage4a_r2_bootstrap.csv"
    inference_path = args.output_dir / "stage4a_r2_inference.json"
    write_csv(query_path, rows)
    write_csv(summary_path, summaries)
    write_csv(bootstrap_path, bootstrap_rows)
    write_inference(inference_path, inference)
    write_report(
        args.report,
        audit,
        summaries,
        bootstrap_rows,
        inference,
        args,
        perf_counter() - start,
    )
    print(
        json.dumps(
            {
                "audit": audit,
                "inference": inference,
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
