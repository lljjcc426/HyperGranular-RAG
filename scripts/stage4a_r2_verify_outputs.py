"""Independently verify Stage4A-R2 tracked outputs from query-level rows."""

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
EXPECTED_QUERIES = 4500
ITERATIONS = 10000
SEED = 20260712
TARGET_HALFWIDTH = 0.005
EXPECTED_ARCHIVE_SHA256 = "95DF2BF56FDABE034E27AEBC580E02264232203CF52552F9EFE8A919E5529EEF"
EXPECTED_DEV_SHA256 = "79F77AE104088EA8E25B1A65DBECE768D45771194663BC5660EC9A98070DADF5"


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
    spread = z * math.sqrt(
        p * (1.0 - p) / total + z * z / (4.0 * total * total)
    ) / denominator
    return max(0.0, center - spread), min(1.0, center + spread)


def exact_mcnemar_pvalue(gains: int, harms: int) -> float:
    discordant = gains + harms
    if discordant == 0:
        return 1.0
    tail = min(gains, harms)
    one_sided = sum(
        math.comb(discordant, value) * 0.5**discordant
        for value in range(tail + 1)
    )
    return min(1.0, 2.0 * one_sided)


def verify_query_rows(
    rows: list[dict[str, str]],
    source_audit: dict[str, Any],
) -> dict[str, Any]:
    if len(rows) != EXPECTED_QUERIES or len({row["query_id"] for row in rows}) != EXPECTED_QUERIES:
        raise ValueError("Stage4A-R2 query audit must contain 4,500 unique IDs")
    type_counts = Counter(row["question_type"] for row in rows)
    if dict(sorted(type_counts.items())) != source_audit["mapping"]["question_types"]:
        raise ValueError("Stage4A-R2 question types differ from source audit")
    for row in rows:
        dense_cr = int(float(row["dense_cr20"]) > 0.5)
        for prefix in PREFIXES.values():
            strategy_cr = int(float(row[f"{prefix}_cr20"]) > 0.5)
            inserted = int(row[f"{prefix}_inserted_units"])
            expected_gain = int(dense_cr == 0 and strategy_cr == 1)
            expected_harm = int(dense_cr == 1 and strategy_cr == 0)
            expected_opportunity = int(inserted > 0 and dense_cr == 0)
            if int(row[f"{prefix}_gain_event"]) != expected_gain:
                raise ValueError(f"Gain mismatch: {row['query_id']} {prefix}")
            if int(row[f"{prefix}_harm_event"]) != expected_harm:
                raise ValueError(f"Harm mismatch: {row['query_id']} {prefix}")
            if int(row[f"{prefix}_completion_opportunity"]) != expected_opportunity:
                raise ValueError(f"Opportunity mismatch: {row['query_id']} {prefix}")
            removed = int(row[f"{prefix}_raw_candidate_count"]) - int(
                row[f"{prefix}_filtered_candidate_count"]
            )
            if int(row[f"{prefix}_score_floor_removed"]) != removed:
                raise ValueError(f"Removal mismatch: {row['query_id']} {prefix}")
    return {
        "query_rows": len(rows),
        "unique_query_ids": len({row["query_id"] for row in rows}),
        "question_types": dict(sorted(type_counts.items())),
    }


def verify_summary(
    query_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> dict[str, Any]:
    expected_slices = ["ALL", *sorted({row["question_type"] for row in query_rows})]
    if len(summary_rows) != len(expected_slices) * len(PREFIXES):
        raise ValueError("Unexpected Stage4A-R2 summary row count")
    index = {(row["slice"], row["strategy_id"]): row for row in summary_rows}
    for slice_name in expected_slices:
        items = query_rows if slice_name == "ALL" else [
            row for row in query_rows if row["question_type"] == slice_name
        ]
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


def verify_bootstrap(
    query_rows: list[dict[str, str]],
    bootstrap_rows: list[dict[str, str]],
    chunk_size: int = 250,
) -> dict[str, Any]:
    if len(bootstrap_rows) != 6:
        raise ValueError("Stage4A-R2 bootstrap must contain six rows")
    comparisons = (
        ("q25_vs_dense", "q25", "dense"),
        ("unfiltered_vs_dense", "unfiltered", "dense"),
        ("q25_vs_unfiltered", "q25", "unfiltered"),
    )
    specs = []
    index = {(row["comparison_id"], row["metric"]): row for row in bootstrap_rows}
    for comparison_id, prefix_a, prefix_b in comparisons:
        for metric, suffix in (
            ("evidence_recall_at_20", "er20"),
            ("chain_recall_at_20", "cr20"),
        ):
            a = np.array([float(row[f"{prefix_a}_{suffix}"]) for row in query_rows])
            b = np.array([float(row[f"{prefix_b}_{suffix}"]) for row in query_rows])
            specs.append(
                {
                    "comparison_id": comparison_id,
                    "metric": metric,
                    "a": a,
                    "b": b,
                    "delta": a - b,
                    "samples": np.empty(ITERATIONS, dtype="float64"),
                }
            )
    rng = np.random.default_rng(SEED)
    for start in range(0, ITERATIONS, chunk_size):
        stop = min(start + chunk_size, ITERATIONS)
        indices = rng.integers(
            0,
            len(query_rows),
            size=(stop - start, len(query_rows)),
            dtype=np.int32,
        )
        for spec in specs:
            spec["samples"][start:stop] = spec["delta"][indices].mean(axis=1)
    for spec in specs:
        actual = index[(spec["comparison_id"], spec["metric"])]
        delta = spec["delta"]
        expected = {
            "observed_a": float(spec["a"].mean()),
            "observed_b": float(spec["b"].mean()),
            "observed_delta": float(delta.mean()),
            "ci95_low": float(np.quantile(spec["samples"], 0.025)),
            "ci95_high": float(np.quantile(spec["samples"], 0.975)),
            "improved": float(np.sum(delta > 1e-12)),
            "same": float(np.sum(np.abs(delta) <= 1e-12)),
            "regressed": float(np.sum(delta < -1e-12)),
        }
        for field, value in expected.items():
            close(actual[field], value, f"{spec['comparison_id']}/{spec['metric']}/{field}")
        if int(actual["iterations"]) != ITERATIONS or int(actual["seed"]) != SEED:
            raise ValueError("Stage4A-R2 bootstrap configuration differs")
    return {"bootstrap_rows": len(bootstrap_rows), "iterations": ITERATIONS, "seed": SEED}


def verify_inference(
    summary_rows: list[dict[str, str]],
    inference: dict[str, Any],
) -> dict[str, Any]:
    all_rows = {row["strategy_id"]: row for row in summary_rows if row["slice"] == "ALL"}
    dense = all_rows["dense_fixed"]
    q25 = all_rows["allquery_q25_p10_i4"]
    gains = int(q25["gain_events"])
    harms = int(q25["harm_events"])
    gain_low, gain_high = wilson(gains, EXPECTED_QUERIES)
    harm_low, harm_high = wilson(harms, EXPECTED_QUERIES)
    expected = {
        "gain_prevalence": gains / EXPECTED_QUERIES,
        "gain_low": gain_low,
        "gain_high": gain_high,
        "gain_halfwidth": (gain_high - gain_low) / 2.0,
        "harm_prevalence": harms / EXPECTED_QUERIES,
        "harm_low": harm_low,
        "harm_high": harm_high,
        "harm_halfwidth": (harm_high - harm_low) / 2.0,
        "dense_cr20": float(dense["chain_recall_at_20"]),
        "q25_cr20": float(q25["chain_recall_at_20"]),
        "cr20_delta": float(q25["chain_recall_at_20"]) - float(dense["chain_recall_at_20"]),
        "mcnemar_p": exact_mcnemar_pvalue(gains, harms),
    }
    close(inference["primary"]["q25_gain"]["prevalence"], expected["gain_prevalence"], "gain prevalence")
    close(inference["primary"]["q25_gain"]["wilson95_low"], expected["gain_low"], "gain low")
    close(inference["primary"]["q25_gain"]["wilson95_high"], expected["gain_high"], "gain high")
    close(inference["primary"]["q25_gain"]["halfwidth"], expected["gain_halfwidth"], "gain halfwidth")
    close(inference["primary"]["q25_harm"]["prevalence"], expected["harm_prevalence"], "harm prevalence")
    close(inference["primary"]["q25_harm"]["wilson95_low"], expected["harm_low"], "harm low")
    close(inference["primary"]["q25_harm"]["wilson95_high"], expected["harm_high"], "harm high")
    close(inference["primary"]["q25_harm"]["halfwidth"], expected["harm_halfwidth"], "harm halfwidth")
    close(inference["secondary"]["cr20_delta"], expected["cr20_delta"], "CR20 delta")
    close(inference["secondary"]["dense_cr20"], expected["dense_cr20"], "dense CR20")
    close(inference["secondary"]["q25_cr20"], expected["q25_cr20"], "q25 CR20")
    close(inference["secondary"]["exact_conditional_mcnemar_two_sided_p"], expected["mcnemar_p"], "McNemar p")
    precision_pass = expected["gain_halfwidth"] <= TARGET_HALFWIDTH and expected["harm_halfwidth"] <= TARGET_HALFWIDTH
    expected_decision = "ESTIMATION_COMPLETE" if precision_pass else "ESTIMATION_PRECISION_NOT_MET"
    if inference["decision"] != expected_decision:
        raise ValueError(f"Inference decision mismatch: {inference['decision']} vs {expected_decision}")
    if inference["controller_training_authorized"] is not False:
        raise ValueError("Stage4A-R2 cannot authorize controller training")
    return {"decision": expected_decision, "values": expected}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query-audit", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--bootstrap", required=True, type=Path)
    parser.add_argument("--inference", required=True, type=Path)
    parser.add_argument("--source-audit", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    source_audit = json.loads(args.source_audit.read_text(encoding="utf-8"))
    query_rows = read_csv(args.query_audit)
    summary_rows = read_csv(args.summary)
    bootstrap_rows = read_csv(args.bootstrap)
    inference = json.loads(args.inference.read_text(encoding="utf-8"))
    if source_audit["provenance_status"] != "OFFICIAL_APRIL7_ARCHIVE":
        raise ValueError("Verifier requires official source audit")
    official = source_audit["official_archive"]
    if official["sha256"] != EXPECTED_ARCHIVE_SHA256 or official["dev_json_sha256"] != EXPECTED_DEV_SHA256:
        raise ValueError("Verifier source hashes differ from protocol")
    boundary = source_audit["data_boundary"]
    if boundary["development_rows"] != "[800:5300)" or boundary["reservation_rows"] != "[5300:9800)":
        raise ValueError("Verifier source boundary differs from protocol")
    if source_audit["data_boundary"]["reservation_content_written"] is not False:
        raise ValueError("Reservation content boundary failed")
    checks = {
        "query_audit": verify_query_rows(query_rows, source_audit),
        "summary": verify_summary(query_rows, summary_rows),
        "bootstrap": verify_bootstrap(query_rows, bootstrap_rows),
        "inference": verify_inference(summary_rows, inference),
    }
    report_text = args.report.read_text(encoding="utf-8")
    if f"Precision decision: `{inference['decision']}`." not in report_text:
        raise ValueError("Report decision differs from inference")
    report_text = report_text.replace(
        "- Verification Status: UNVERIFIED",
        "- Verification Status: VERIFIED_BY_STAGE4A_R2_OUTPUT_AUDIT",
    )
    args.report.write_text(report_text, encoding="utf-8")
    verification = {
        "status": "VERIFIED_OFFICIAL_INTERNAL_METRICS",
        "scope": "OFFICIAL_APRIL7_ROWS_800_5300_ONLY",
        "decision": inference["decision"],
        "controller_training_authorized": False,
        "reservation_metrics_accessed": False,
        "checks": checks,
        "sha256": {
            "query_audit": sha256(args.query_audit),
            "strategy_summary": sha256(args.summary),
            "bootstrap": sha256(args.bootstrap),
            "inference": sha256(args.inference),
            "source_audit": sha256(args.source_audit),
            "verified_report": sha256(args.report),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(verification, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(verification, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
