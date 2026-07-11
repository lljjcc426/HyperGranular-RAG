"""Independently recompute and verify tracked Stage4A result artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


PREFIXES = {
    "dense_fixed": "dense",
    "allquery_unfiltered_p10_i4": "unfiltered",
    "allquery_q25_p10_i4": "q25",
}
ITERATIONS = 10000
SEED = 20260714


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def close(actual: float | str, expected: float, label: str) -> None:
    if not math.isclose(float(actual), expected, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError(f"{label}: actual={actual}, expected={expected}")


def wilson(successes: int, total: int) -> tuple[float, float]:
    z = 1.959963984540054
    p = successes / total
    denominator = 1.0 + z * z / total
    center = (p + z * z / (2.0 * total)) / denominator
    spread = z * math.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total * total)) / denominator
    return max(0.0, center - spread), min(1.0, center + spread)


def verify_query_rows(rows: list[dict[str, str]], source_audit: dict[str, Any]) -> dict[str, Any]:
    if len(rows) != 400 or len({row["query_id"] for row in rows}) != 400:
        raise ValueError("Query audit must contain 400 unique query IDs")
    type_counts = Counter(row["question_type"] for row in rows)
    if dict(sorted(type_counts.items())) != source_audit["mapping"]["question_types"]:
        raise ValueError("Query-audit type counts differ from source audit")
    for row in rows:
        dense_cr = int(float(row["dense_cr20"]) > 0.5)
        for prefix in PREFIXES.values():
            strategy_cr = int(float(row[f"{prefix}_cr20"]) > 0.5)
            triggered = int(int(row[f"{prefix}_inserted_units"]) > 0)
            expected_gain = int(dense_cr == 0 and strategy_cr == 1)
            expected_harm = int(dense_cr == 1 and strategy_cr == 0)
            expected_opportunity = int(triggered and dense_cr == 0)
            if int(row[f"{prefix}_gain_event"]) != expected_gain:
                raise ValueError(f"Gain-event mismatch: {row['query_id']} {prefix}")
            if int(row[f"{prefix}_harm_event"]) != expected_harm:
                raise ValueError(f"Harm-event mismatch: {row['query_id']} {prefix}")
            if int(row[f"{prefix}_completion_opportunity"]) != expected_opportunity:
                raise ValueError(f"Completion-opportunity mismatch: {row['query_id']} {prefix}")
            removed = int(row[f"{prefix}_raw_candidate_count"]) - int(row[f"{prefix}_filtered_candidate_count"])
            if int(row[f"{prefix}_score_floor_removed"]) != removed:
                raise ValueError(f"Score-floor removal mismatch: {row['query_id']} {prefix}")
    return {"query_rows": len(rows), "unique_query_ids": 400, "question_types": dict(sorted(type_counts.items()))}


def verify_summary(query_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> dict[str, Any]:
    expected_slices = ["ALL", *sorted({row["question_type"] for row in query_rows})]
    if len(summary_rows) != len(expected_slices) * len(PREFIXES):
        raise ValueError("Unexpected Stage4A summary row count")
    index = {(row["slice"], row["strategy_id"]): row for row in summary_rows}
    for slice_name in expected_slices:
        items = query_rows if slice_name == "ALL" else [row for row in query_rows if row["question_type"] == slice_name]
        n = len(items)
        for strategy_id, prefix in PREFIXES.items():
            actual = index[(slice_name, strategy_id)]
            inserted = sum(int(row[f"{prefix}_inserted_units"]) for row in items)
            inserted_gold = sum(int(row[f"{prefix}_inserted_gold_units"]) for row in items)
            gains = sum(int(row[f"{prefix}_gain_event"]) for row in items)
            harms = sum(int(row[f"{prefix}_harm_event"]) for row in items)
            opportunities = sum(int(row[f"{prefix}_completion_opportunity"]) for row in items)
            gain_low, gain_high = wilson(gains, n)
            harm_low, harm_high = wilson(harms, n)
            expected = {
                "queries": float(n),
                "evidence_recall_at_20": sum(float(row[f"{prefix}_er20"]) for row in items) / n,
                "chain_recall_at_20": sum(float(row[f"{prefix}_cr20"]) for row in items) / n,
                "trigger_rate": sum(int(row[f"{prefix}_triggered"]) for row in items) / n,
                "avg_inserted_units": inserted / n,
                "insert_yield": inserted_gold / max(inserted, 1),
                "conditional_false_insert_rate": (inserted - inserted_gold) / max(inserted, 1),
                "raw_candidates": float(sum(int(row[f"{prefix}_raw_candidate_count"]) for row in items)),
                "filtered_candidates": float(sum(int(row[f"{prefix}_filtered_candidate_count"]) for row in items)),
                "score_floor_removed": float(sum(int(row[f"{prefix}_score_floor_removed"]) for row in items)),
                "gain_events": float(gains),
                "harm_events": float(harms),
                "net_completed_chain_change": float(gains - harms),
                "gain_prevalence": gains / n,
                "gain_wilson95_low": gain_low,
                "gain_wilson95_high": gain_high,
                "harm_prevalence": harms / n,
                "harm_wilson95_low": harm_low,
                "harm_wilson95_high": harm_high,
                "completion_opportunities": float(opportunities),
                "completion_precision": gains / max(opportunities, 1),
            }
            for metric, value in expected.items():
                close(actual[metric], value, f"{slice_name}/{strategy_id}/{metric}")
    return {"summary_rows": len(summary_rows), "verified_slices": expected_slices}


def verify_bootstrap(query_rows: list[dict[str, str]], bootstrap_rows: list[dict[str, str]]) -> dict[str, Any]:
    if len(bootstrap_rows) != 6:
        raise ValueError("Stage4A bootstrap must contain six comparison rows")
    indices = np.random.default_rng(SEED).integers(
        0, len(query_rows), size=(ITERATIONS, len(query_rows)), dtype=np.int32
    )
    comparisons = (
        ("q25_vs_dense", "q25", "dense"),
        ("unfiltered_vs_dense", "unfiltered", "dense"),
        ("q25_vs_unfiltered", "q25", "unfiltered"),
    )
    index = {(row["comparison_id"], row["metric"]): row for row in bootstrap_rows}
    for comparison_id, prefix_a, prefix_b in comparisons:
        for metric, suffix in (("evidence_recall_at_20", "er20"), ("chain_recall_at_20", "cr20")):
            actual = index[(comparison_id, metric)]
            a = np.array([float(row[f"{prefix_a}_{suffix}"]) for row in query_rows], dtype="float64")
            b = np.array([float(row[f"{prefix_b}_{suffix}"]) for row in query_rows], dtype="float64")
            delta = a - b
            sampled = delta[indices].mean(axis=1)
            expected = {
                "observed_a": float(a.mean()),
                "observed_b": float(b.mean()),
                "observed_delta": float(delta.mean()),
                "ci95_low": float(np.quantile(sampled, 0.025)),
                "ci95_high": float(np.quantile(sampled, 0.975)),
                "improved": float(np.sum(delta > 1e-12)),
                "same": float(np.sum(np.abs(delta) <= 1e-12)),
                "regressed": float(np.sum(delta < -1e-12)),
            }
            for field, value in expected.items():
                close(actual[field], value, f"{comparison_id}/{metric}/{field}")
            if int(actual["iterations"]) != ITERATIONS or int(actual["seed"]) != SEED:
                raise ValueError("Bootstrap iterations or seed differ from protocol")
    return {"bootstrap_rows": len(bootstrap_rows), "iterations": ITERATIONS, "seed": SEED}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query-audit", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--bootstrap", required=True, type=Path)
    parser.add_argument("--source-audit", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    source_audit = json.loads(args.source_audit.read_text(encoding="utf-8"))
    query_rows = read_csv(args.query_audit)
    summary_rows = read_csv(args.summary)
    bootstrap_rows = read_csv(args.bootstrap)
    checks = {
        "query_audit": verify_query_rows(query_rows, source_audit),
        "summary": verify_summary(query_rows, summary_rows),
        "bootstrap": verify_bootstrap(query_rows, bootstrap_rows),
    }
    all_summary = {row["strategy_id"]: row for row in summary_rows if row["slice"] == "ALL"}
    q25 = all_summary["allquery_q25_p10_i4"]
    dense = all_summary["dense_fixed"]
    gates = {
        "mapping": source_audit["mapping"]["supporting_fact_mapping_rate"] >= 0.99
        and source_audit["mapping"]["queries_missing_gold"] == 0,
        "dense_not_saturated": float(dense["chain_recall_at_20"]) < 0.95,
        "q25_trigger": float(q25["trigger_rate"]) >= 0.10,
        "q25_gain_events": int(q25["gain_events"]) >= 10,
        "q25_positive_net": int(q25["net_completed_chain_change"]) > 0,
        "q25_filter_active": int(q25["score_floor_removed"]) > 0,
    }
    decision = "PROMOTE" if all(gates.values()) else "STOP"
    report_text = args.report.read_text(encoding="utf-8")
    if f"decision: {decision}." not in report_text:
        raise ValueError(f"Report does not contain the recomputed {decision} decision")
    report_text = report_text.replace(
        "- Verification Status: UNVERIFIED",
        "- Verification Status: VERIFIED_BY_STAGE4A_OUTPUT_AUDIT",
    )
    args.report.write_text(report_text, encoding="utf-8")

    verification = {
        "status": "VERIFIED_INTERNAL_METRICS",
        "scope": "PINNED_MIRROR_ONLY",
        "official_archive_reconciliation": "NOT_PART_OF_THIS_VERIFIER",
        "decision": decision,
        "scientific_conclusion": "INCONCLUSIVE_PENDING_STAGE4R",
        "gates": gates,
        "checks": checks,
        "sha256": {
            "query_audit": sha256(args.query_audit),
            "strategy_summary": sha256(args.summary),
            "bootstrap": sha256(args.bootstrap),
            "source_audit": sha256(args.source_audit),
            "verified_report": sha256(args.report),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(verification, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
