"""Stage3C retrospective target-feasibility audit for observed retrieval events."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def wilson_interval(events: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        return 0.0, 0.0
    proportion = events / total
    z2 = z * z
    denominator = 1.0 + z2 / total
    center = (proportion + z2 / (2.0 * total)) / denominator
    half = z * math.sqrt(proportion * (1.0 - proportion) / total + z2 / (4.0 * total * total)) / denominator
    return max(0.0, center - half), min(1.0, center + half)


def projected_queries(target_events: int, events: int, queries: int) -> int | None:
    if events <= 0 or queries <= 0:
        return None
    return math.ceil(target_events / (events / queries))


def normalize_stage2h(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        baseline = float(row["baseline_chain_recall_at_20"])
        expanded = float(row["strategy_chain_recall_at_20"])
        triggered = int(row["triggered"])
        output.append(
            {
                "observed_partition": row["slice_id"],
                "source_stage": "stage2h",
                "dataset": row["dataset"],
                "query_id": row["query_id"],
                "triggered": triggered,
                "baseline_cr20": baseline,
                "expanded_cr20": expanded,
                "completion_opportunity": int(triggered and baseline < 0.5),
                "gain_event": int(expanded - baseline > 0.5),
                "harm_opportunity": int(triggered and baseline > 0.5),
                "harm_event": int(baseline - expanded > 0.5),
                "inserted_units": int(row["inserted_units"]),
                "inserted_non_gold_units": int(row["inserted_non_gold_units"]),
            }
        )
    return output


def normalize_stage3a(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        baseline = float(row["baseline_chain_recall_at_20"])
        expanded = float(row["expanded_chain_recall_at_20"])
        triggered = int(row["triggered_allquery"])
        output.append(
            {
                "observed_partition": f"stage3a_{row['partition']}",
                "source_stage": "stage3a",
                "dataset": row["dataset"],
                "query_id": row["query_id"],
                "triggered": triggered,
                "baseline_cr20": baseline,
                "expanded_cr20": expanded,
                "completion_opportunity": int(triggered and baseline < 0.5),
                "gain_event": int(row["gain_label"]),
                "harm_opportunity": int(triggered and baseline > 0.5),
                "harm_event": int(row["harm_label"]),
                "inserted_units": int(row["inserted_units_allquery"]),
                "inserted_non_gold_units": int(row["inserted_non_gold_units_allquery"]),
            }
        )
    return output


def validate_inputs(
    stage2h: list[dict[str, str]],
    stage3a: list[dict[str, str]],
    normalized: list[dict[str, Any]],
    reservation: dict[str, Any],
) -> dict[str, Any]:
    if len(stage2h) != 1200:
        raise ValueError(f"Expected 1200 Stage2H rows, found {len(stage2h)}")
    if len(stage3a) != 800:
        raise ValueError(f"Expected 800 Stage3A rows, found {len(stage3a)}")
    stage2h_ids = {row["query_id"] for row in stage2h}
    stage3a_ids = {row["query_id"] for row in stage3a}
    if len(stage2h_ids) != 1200 or len(stage3a_ids) != 800:
        raise ValueError("Duplicate query IDs in Stage2H or Stage3A audit")
    overlap = stage2h_ids & stage3a_ids
    if overlap:
        raise ValueError(f"Stage2H/Stage3A overlap: {sorted(overlap)[:5]}")
    expected_partitions = Counter(
        {
            "stage2e": 400,
            "stage2f": 400,
            "stage2g": 400,
            "stage3a_fitting": 480,
            "stage3a_threshold_selection": 320,
        }
    )
    actual_partitions = Counter(row["observed_partition"] for row in normalized)
    if actual_partitions != expected_partitions:
        raise ValueError(f"Unexpected partition counts: {dict(actual_partitions)}")
    if not reservation["stage3b_frozen_test"]["metrics_locked"]:
        raise ValueError("Stage3B reservation is not locked")
    return {
        "stage2h_rows": len(stage2h),
        "stage3a_rows": len(stage3a),
        "total_rows": len(normalized),
        "stage2h_stage3a_overlap": len(overlap),
        "partition_counts": dict(actual_partitions),
        "dataset_counts": dict(Counter(row["dataset"] for row in normalized)),
        "stage3b_metrics_locked": True,
        "stage3b_metrics_read": False,
        "stage3b_query_id_sha256": reservation["stage3b_frozen_test"]["query_id_sha256"],
    }


def summarize_scope(
    scope_type: str,
    scope_value: str,
    dataset: str,
    items: list[dict[str, Any]],
) -> dict[str, Any]:
    queries = len(items)
    triggered = sum(row["triggered"] for row in items)
    gains = sum(row["gain_event"] for row in items)
    harms = sum(row["harm_event"] for row in items)
    completion_opportunities = sum(row["completion_opportunity"] for row in items)
    harm_opportunities = sum(row["harm_opportunity"] for row in items)
    inserted = sum(row["inserted_units"] for row in items)
    non_gold = sum(row["inserted_non_gold_units"] for row in items)
    gain_low, gain_high = wilson_interval(gains, queries)
    harm_low, harm_high = wilson_interval(harms, queries)
    baseline_cr20 = sum(row["baseline_cr20"] for row in items) / queries
    expanded_cr20 = sum(row["expanded_cr20"] for row in items) / queries
    return {
        "scope_type": scope_type,
        "scope_value": scope_value,
        "dataset": dataset,
        "queries": queries,
        "triggered_queries": triggered,
        "trigger_rate": triggered / queries,
        "baseline_cr20": baseline_cr20,
        "expanded_cr20": expanded_cr20,
        "delta_cr20": expanded_cr20 - baseline_cr20,
        "completion_opportunities": completion_opportunities,
        "gain_events": gains,
        "gain_prevalence": gains / queries,
        "gain_prevalence_ci_low": gain_low,
        "gain_prevalence_ci_high": gain_high,
        "completion_precision": gains / max(completion_opportunities, 1),
        "harm_opportunities": harm_opportunities,
        "harm_events": harms,
        "harm_prevalence": harms / queries,
        "harm_prevalence_ci_low": harm_low,
        "harm_prevalence_ci_high": harm_high,
        "harm_rate": harms / max(harm_opportunities, 1),
        "inserted_units": inserted,
        "inserted_non_gold_per_query": non_gold / queries,
        "false_insert_rate": non_gold / max(inserted, 1),
        "saturated_cr20": int(baseline_cr20 >= 0.95),
        "projected_queries_for_20_gains": projected_queries(20, gains, queries),
        "projected_queries_for_50_gains": projected_queries(50, gains, queries),
        "projected_queries_for_20_harms": projected_queries(20, harms, queries),
        "projected_queries_for_50_harms": projected_queries(50, harms, queries),
    }


def build_summaries(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for partition in sorted({row["observed_partition"] for row in rows}):
        partition_rows = [row for row in rows if row["observed_partition"] == partition]
        output.append(summarize_scope("observed_partition", partition, "ALL", partition_rows))
        for dataset in ("hotpotqa", "musique"):
            items = [row for row in partition_rows if row["dataset"] == dataset]
            output.append(summarize_scope("observed_partition", partition, dataset, items))
    for dataset in ("hotpotqa", "musique"):
        items = [row for row in rows if row["dataset"] == dataset]
        output.append(summarize_scope("dataset_total", dataset, dataset, items))
    output.append(summarize_scope("full_audit", "ALL", "ALL", rows))
    return output


def scope_decision(
    items: list[dict[str, Any]],
    partition_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    gains = sum(row["gain_event"] for row in items)
    harms = sum(row["harm_event"] for row in items)
    harm_partitions = [row["scope_value"] for row in partition_rows if row["harm_events"] >= 5]
    risk_feasible = gains >= 20 and harms >= 20 and len(harm_partitions) >= 2
    gain_feasible = gains >= 20
    if risk_feasible:
        decision = "RISK_AWARE_EXPECTED_UTILITY_EVENT_FEASIBLE"
    elif gain_feasible:
        decision = "BUDGET_AWARE_GAIN_SELECTION_EVENT_FEASIBLE"
    else:
        decision = "CURRENT_CONTROLLER_LEARNING_EVENT_INFEASIBLE"
    return {
        "queries": len(items),
        "gain_events": gains,
        "harm_events": harms,
        "partitions_with_at_least_5_harms": harm_partitions,
        "risk_aware_event_feasible": risk_feasible,
        "budget_aware_gain_event_feasible": gain_feasible and not risk_feasible,
        "decision": decision,
    }


def build_decision(
    rows: list[dict[str, Any]],
    summaries: list[dict[str, Any]],
    model: dict[str, Any],
    audit: dict[str, Any],
    inputs: dict[str, str],
) -> dict[str, Any]:
    partition_all = [
        row
        for row in summaries
        if row["scope_type"] == "observed_partition" and row["dataset"] == "ALL"
    ]
    decisions: dict[str, Any] = {}
    decisions["ALL"] = scope_decision(rows, partition_all)
    for dataset in ("hotpotqa", "musique"):
        items = [row for row in rows if row["dataset"] == dataset]
        dataset_partitions = [
            row
            for row in summaries
            if row["scope_type"] == "observed_partition" and row["dataset"] == dataset
        ]
        decisions[dataset] = scope_decision(items, dataset_partitions)
    return {
        "protocol": "docs/STAGE3C_PROTOCOL.md",
        "analysis_status": "EXPLORATORY_RETROSPECTIVE",
        "input_sha256": inputs,
        "audit": audit,
        "stage3a_model_fallback": {
            "gain_head": bool(model["gain_head"]["fallback"]),
            "harm_head": bool(model["harm_head"]["fallback"]),
        },
        "scope_decisions": decisions,
        "stage3b_action": "KEEP_LOCKED",
        "new_model_fitted": False,
    }


def format_rate(value: float) -> str:
    return f"{value:.4f}"


def write_report(
    path: Path,
    audit: dict[str, Any],
    summaries: list[dict[str, Any]],
    decision: dict[str, Any],
) -> None:
    full = next(row for row in summaries if row["scope_type"] == "full_audit")
    datasets = [row for row in summaries if row["scope_type"] == "dataset_total"]
    lines = [
        "# Stage3C Target-Feasibility Audit Report",
        "",
        "## Material Passport",
        "",
        "- Origin Skill: academic-research-suite / experiment-agent",
        "- Origin Mode: run",
        f"- Origin Date: {date.today().isoformat()}",
        "- Verification Status: UNVERIFIED",
        "- Version Label: exp_result_v1",
        "- Analysis Status: EXPLORATORY RETROSPECTIVE FEASIBILITY AUDIT",
        "- Protocol: `docs/STAGE3C_PROTOCOL.md`",
        "- Stage3B metrics read: No",
        "",
        "## Input Audit",
        "",
        f"- Stage2H/Stage3A rows: {audit['stage2h_rows']}/{audit['stage3a_rows']}",
        f"- Total observed queries: {audit['total_rows']}",
        f"- Query-ID overlap: {audit['stage2h_stage3a_overlap']}",
        f"- Stage3B action: {decision['stage3b_action']}",
        "",
        "## Pooled Event Audit",
        "",
        "| Scope | Queries | Dense CR@20 | Gain events | Gain prevalence | Harm events | Harm prevalence | Saturated |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        f"| ALL | {full['queries']} | {format_rate(full['baseline_cr20'])} | {full['gain_events']} | "
        f"{format_rate(full['gain_prevalence'])} | {full['harm_events']} | "
        f"{format_rate(full['harm_prevalence'])} | {full['saturated_cr20']} |",
    ]
    for row in datasets:
        lines.append(
            f"| {row['dataset']} | {row['queries']} | {format_rate(row['baseline_cr20'])} | "
            f"{row['gain_events']} | {format_rate(row['gain_prevalence'])} | {row['harm_events']} | "
            f"{format_rate(row['harm_prevalence'])} | {row['saturated_cr20']} |"
        )
    lines.extend(
        [
            "",
            "## Feasibility Decision",
            "",
        ]
    )
    for scope, item in decision["scope_decisions"].items():
        lines.append(
            f"- {scope}: `{item['decision']}` ({item['gain_events']} gains, {item['harm_events']} harms)."
        )
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "This report diagnoses event availability in already observed data. It does not validate a controller, "
            "does not estimate Stage3B performance, and does not make a confirmatory cross-dataset claim.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage2h-audit", required=True, type=Path)
    parser.add_argument("--stage3a-audit", required=True, type=Path)
    parser.add_argument("--stage3a-model", required=True, type=Path)
    parser.add_argument("--reservation", required=True, type=Path)
    parser.add_argument("--summary-output", required=True, type=Path)
    parser.add_argument("--decision-output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stage2h_raw = load_csv(args.stage2h_audit)
    stage3a_raw = load_csv(args.stage3a_audit)
    model = load_json(args.stage3a_model)
    reservation = load_json(args.reservation)
    rows = normalize_stage2h(stage2h_raw) + normalize_stage3a(stage3a_raw)
    audit = validate_inputs(stage2h_raw, stage3a_raw, rows, reservation)
    summaries = build_summaries(rows)
    input_hashes = {
        "stage2h_query_audit": file_sha256(args.stage2h_audit),
        "stage3a_query_audit": file_sha256(args.stage3a_audit),
        "stage3a_model": file_sha256(args.stage3a_model),
        "stage3_reservation": file_sha256(args.reservation),
    }
    decision = build_decision(rows, summaries, model, audit, input_hashes)
    write_csv(args.summary_output, summaries)
    args.decision_output.parent.mkdir(parents=True, exist_ok=True)
    args.decision_output.write_text(
        json.dumps(decision, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    write_report(args.report, audit, summaries, decision)
    print(
        json.dumps(
            {
                "audit": audit,
                "full_decision": decision["scope_decisions"]["ALL"],
                "summary": str(args.summary_output),
                "decision": str(args.decision_output),
                "report": str(args.report),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
