"""Join frozen Stage4B-U1 rankings with the evaluator-only label channel."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from stage4b_u1_common import (
    SCHEMA_VERSION,
    exact_mcnemar_two_sided_pvalue,
    fisher_greater_pvalue,
    id_digest,
    load_json,
    load_jsonl,
    sha256_file,
    validate_unique_ids,
    write_json,
    write_jsonl,
)


def retrieval_metrics(ranking: list[str], gold: set[str]) -> tuple[float, int]:
    retrieved = set(ranking[:20]) & gold
    evidence_recall = len(retrieved) / max(len(gold), 1)
    chain_recall = int(bool(gold) and gold.issubset(retrieved))
    return evidence_recall, chain_recall


def evaluate_rows(
    rankings: list[dict[str, Any]], gold_map: dict[str, Any]
) -> list[dict[str, Any]]:
    gold_by_query = {
        str(row["query_id"]): {
            "gold": set(str(value) for value in row["gold_unit_ids"]),
            "question_type": str(row.get("question_type", "unknown")),
        }
        for row in gold_map["queries"]
    }
    if set(gold_by_query) != {str(row["query_id"]) for row in rankings}:
        raise ValueError("Ranking/Gold query ID sets differ")
    output: list[dict[str, Any]] = []
    for row in rankings:
        query_id = str(row["query_id"])
        gold = gold_by_query[query_id]["gold"]
        if not gold:
            raise ValueError(f"Evaluator received an empty Gold set: {query_id}")
        dense_er, dense_cr = retrieval_metrics(row["dense_top20_unit_ids"], gold)
        q25_er, q25_cr = retrieval_metrics(row["q25_top20_unit_ids"], gold)
        final_er, final_cr = retrieval_metrics(row["final_top20_unit_ids"], gold)
        q25_inserted = [str(value) for value in row["q25_inserted_unit_ids"]]
        final_inserted = [str(value) for value in row["final_inserted_unit_ids"]]
        q25_inserted_gold = len(set(q25_inserted) & gold)
        final_inserted_gold = len(set(final_inserted) & gold)
        output.append(
            {
                "query_id": query_id,
                "dataset": str(row["dataset"]),
                "sample_id": str(row["sample_id"]),
                "question_type": gold_by_query[query_id]["question_type"],
                "trigger_u1": int(row["trigger_u1"]),
                "planned_insert_count": int(row["planned_insert_count"]),
                "dense_er20": dense_er,
                "dense_cr20": dense_cr,
                "q25_er20": q25_er,
                "q25_cr20": q25_cr,
                "u1_er20": final_er,
                "u1_cr20": final_cr,
                "q25_gain_event": int(dense_cr == 0 and q25_cr == 1),
                "q25_harm_event": int(dense_cr == 1 and q25_cr == 0),
                "u1_gain_event": int(dense_cr == 0 and final_cr == 1),
                "u1_harm_event": int(dense_cr == 1 and final_cr == 0),
                "q25_inserted_units": len(q25_inserted),
                "q25_inserted_gold_units": q25_inserted_gold,
                "q25_inserted_non_gold_units": len(q25_inserted) - q25_inserted_gold,
                "u1_inserted_units": len(final_inserted),
                "u1_inserted_gold_units": final_inserted_gold,
                "u1_inserted_non_gold_units": len(final_inserted) - final_inserted_gold,
            }
        )
    return output


def summarize(items: list[dict[str, Any]], label: str) -> dict[str, Any]:
    n = len(items)
    if n == 0:
        return {"slice": label, "queries": 0}
    q25_gains = sum(row["q25_gain_event"] for row in items)
    q25_harms = sum(row["q25_harm_event"] for row in items)
    retained_gains = sum(row["q25_gain_event"] * row["trigger_u1"] for row in items)
    retained_harms = sum(row["q25_harm_event"] * row["trigger_u1"] for row in items)
    gain_retention = retained_gains / q25_gains if q25_gains else None
    harm_retention = retained_harms / q25_harms if q25_harms else None
    retention_gap = (
        gain_retention - harm_retention
        if gain_retention is not None and harm_retention is not None
        else None
    )
    q25_inserted = sum(row["q25_inserted_units"] for row in items)
    u1_inserted = sum(row["u1_inserted_units"] for row in items)
    q25_non_gold = sum(row["q25_inserted_non_gold_units"] for row in items)
    u1_non_gold = sum(row["u1_inserted_non_gold_units"] for row in items)
    return {
        "slice": label,
        "queries": n,
        "dense_er20": sum(row["dense_er20"] for row in items) / n,
        "dense_cr20": sum(row["dense_cr20"] for row in items) / n,
        "q25_er20": sum(row["q25_er20"] for row in items) / n,
        "q25_cr20": sum(row["q25_cr20"] for row in items) / n,
        "u1_er20": sum(row["u1_er20"] for row in items) / n,
        "u1_cr20": sum(row["u1_cr20"] for row in items) / n,
        "u1_cr20_delta_vs_dense": sum(row["u1_cr20"] - row["dense_cr20"] for row in items) / n,
        "u1_cr20_delta_vs_q25": sum(row["u1_cr20"] - row["q25_cr20"] for row in items) / n,
        "q25_gain_events": q25_gains,
        "q25_harm_events": q25_harms,
        "retained_gain_events": retained_gains,
        "retained_harm_events": retained_harms,
        "gain_retention": gain_retention,
        "harm_retention": harm_retention,
        "retention_gap": retention_gap,
        "fisher_greater_pvalue": fisher_greater_pvalue(
            retained_gains, q25_gains, retained_harms, q25_harms
        ),
        "mcnemar_two_sided_pvalue": exact_mcnemar_two_sided_pvalue(
            sum(row["u1_gain_event"] for row in items),
            sum(row["u1_harm_event"] for row in items),
        ),
        "q25_inserted_units": q25_inserted,
        "u1_inserted_units": u1_inserted,
        "inserted_unit_reduction": 1.0 - u1_inserted / q25_inserted if q25_inserted else None,
        "q25_conditional_false_insert_rate": q25_non_gold / q25_inserted if q25_inserted else None,
        "u1_conditional_false_insert_rate": u1_non_gold / u1_inserted if u1_inserted else None,
    }


def percentile_interval(values: list[float]) -> list[float] | None:
    if not values:
        return None
    return [float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))]


def bootstrap(
    rows: list[dict[str, Any]], iterations: int, seed: int
) -> dict[str, Any]:
    if iterations <= 0:
        return {"iterations": 0, "seed": seed}
    rng = np.random.default_rng(seed)
    cr_dense: list[float] = []
    cr_q25: list[float] = []
    retention: list[float] = []
    for _ in range(iterations):
        sample = [rows[index] for index in rng.integers(0, len(rows), size=len(rows))]
        summary = summarize(sample, "BOOTSTRAP")
        cr_dense.append(float(summary["u1_cr20_delta_vs_dense"]))
        cr_q25.append(float(summary["u1_cr20_delta_vs_q25"]))
        if summary["retention_gap"] is not None:
            retention.append(float(summary["retention_gap"]))
    return {
        "iterations": iterations,
        "seed": seed,
        "u1_cr20_delta_vs_dense_percentile95": percentile_interval(cr_dense),
        "u1_cr20_delta_vs_q25_percentile95": percentile_interval(cr_q25),
        "retention_gap_percentile95": percentile_interval(retention),
    }


def build_decision(summary: dict[str, Any], run_role: str) -> dict[str, Any]:
    false_insert_delta = None
    if (
        summary["u1_conditional_false_insert_rate"] is not None
        and summary["q25_conditional_false_insert_rate"] is not None
    ):
        false_insert_delta = (
            summary["u1_conditional_false_insert_rate"]
            - summary["q25_conditional_false_insert_rate"]
        )
    common = {
        "resource_reduction_at_least_0_40": (
            summary["inserted_unit_reduction"] is not None
            and summary["inserted_unit_reduction"] >= 0.40
        ),
        "retention_gap_at_least_0_15": (
            summary["retention_gap"] is not None and summary["retention_gap"] >= 0.15
        ),
        "fisher_zero_null_rejected": summary["fisher_greater_pvalue"] < 0.05,
        "observed_cr20_delta_vs_dense_at_least_0_005": (
            summary["u1_cr20_delta_vs_dense"] >= 0.005
        ),
    }
    if run_role == "development":
        checks = {
            **common,
            "observed_cr20_delta_vs_q25_at_least_minus_0_005": (
                summary["u1_cr20_delta_vs_q25"] >= -0.005
            ),
            "false_insert_rate_not_worse_by_more_than_0_01": (
                false_insert_delta is not None and false_insert_delta <= 0.01
            ),
        }
        return {
            "run_role": run_role,
            "checks": checks,
            "passed": all(checks.values()),
            "decision": "ELIGIBLE_FOR_U1_R_APPROVAL_REQUEST"
            if all(checks.values())
            else "STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED",
        }
    checks = {
        **common,
        "mcnemar_zero_null_rejected": summary["mcnemar_two_sided_pvalue"] < 0.05,
    }
    return {
        "run_role": run_role,
        "testing_framework": "intersection-union test for one joint claim",
        "checks": checks,
        "passed": all(checks.values()),
        "decision": "CONFIRMED_JOINT_CLAIM"
        if all(checks.values())
        else "JOINT_CLAIM_NOT_CONFIRMED",
        "claim_language": (
            "Both zero-null components have statistical evidence and the observed effects meet "
            "the preregistered practical gates. The practical margins themselves were not tested."
        ),
    }


def run_evaluation(
    *,
    rankings_path: Path,
    policy_path: Path,
    gold_map_path: Path,
    evaluator_audit_path: Path,
    query_audit_output: Path,
    summary_output: Path,
    run_role: str,
    bootstrap_iterations: int,
    bootstrap_seed: int,
    synthetic_test_mode: bool = False,
) -> dict[str, Any]:
    policy = load_json(policy_path)
    if policy.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Policy schema differs")
    if policy.get("run_role") != run_role:
        raise ValueError("Policy/evaluator run roles differ")
    if policy.get("status") == "SYNTHETIC_TEST_ONLY" and not synthetic_test_mode:
        raise ValueError("Synthetic policy requires explicit synthetic-test evaluator mode")
    if policy.get("status") != "SYNTHETIC_TEST_ONLY" and synthetic_test_mode:
        raise ValueError("Synthetic-test evaluator mode cannot evaluate a formal policy")
    ranking_sha = sha256_file(rankings_path)
    if policy.get("output_hashes", {}).get("rankings") != ranking_sha:
        raise ValueError("Ranking digest is not frozen by the policy")
    if bool(policy.get("evaluation_labels_loaded")):
        raise ValueError("Policy reports that evaluation labels were loaded")
    rankings = load_jsonl(rankings_path)
    validate_unique_ids(rankings, "query_id", "ranking")
    evaluator_audit = load_json(evaluator_audit_path)
    if evaluator_audit.get("status") != "EVALUATOR_CHANNEL_PREPARED_NO_RETRIEVAL_METRICS":
        raise ValueError("Evaluator channel audit status differs")
    if bool(evaluator_audit.get("retrieval_metrics_computed")):
        raise ValueError("Evaluator channel audit reports retrieval metrics")
    if evaluator_audit.get("evaluator_channel_hashes", {}).get("gold_map") != sha256_file(
        gold_map_path
    ):
        raise ValueError("Gold-map hash differs from evaluator channel audit")
    gold_map = load_json(gold_map_path)
    if gold_map.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Gold-map schema differs")
    if gold_map.get("query_id_sha256") != id_digest(row["query_id"] for row in rankings):
        raise ValueError("Gold-map/ranking query digest differs")
    rows = evaluate_rows(rankings, gold_map)
    write_jsonl(query_audit_output, rows)
    overall = summarize(rows, "ALL")
    type_summaries = [
        summarize(
            [row for row in rows if row["question_type"] == question_type],
            question_type,
        )
        for question_type in sorted({row["question_type"] for row in rows})
    ]
    subgroup_caution = [
        row["slice"]
        for row in type_summaries
        if row["queries"] > 0
        and (
            row["u1_cr20_delta_vs_dense"] <= -0.02
            or row["retained_harm_events"] > row["retained_gain_events"]
        )
    ]
    summary = {
        "schema_version": SCHEMA_VERSION,
        "protocol": "docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md",
        "run_role": run_role,
        "policy_sha256": sha256_file(policy_path),
        "ranking_sha256": ranking_sha,
        "gold_map_sha256": sha256_file(gold_map_path),
        "evaluator_audit_sha256": sha256_file(evaluator_audit_path),
        "query_audit_sha256": sha256_file(query_audit_output),
        "overall": overall,
        "question_types": type_summaries,
        "subgroup_caution": subgroup_caution,
        "subgroup_interpretation": "Descriptive only; overall success does not imply efficacy in every type.",
        "bootstrap": bootstrap(rows, bootstrap_iterations, bootstrap_seed),
        "decision": build_decision(overall, run_role),
    }
    write_json(summary_output, summary)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rankings", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--gold-map", required=True, type=Path)
    parser.add_argument("--evaluator-audit", required=True, type=Path)
    parser.add_argument("--query-audit-output", required=True, type=Path)
    parser.add_argument("--summary-output", required=True, type=Path)
    parser.add_argument("--run-role", required=True, choices=("development", "reservation"))
    parser.add_argument("--bootstrap-iterations", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260712)
    parser.add_argument("--synthetic-test-mode", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_evaluation(
        rankings_path=args.rankings,
        policy_path=args.policy,
        gold_map_path=args.gold_map,
        evaluator_audit_path=args.evaluator_audit,
        query_audit_output=args.query_audit_output,
        summary_output=args.summary_output,
        run_role=args.run_role,
        bootstrap_iterations=args.bootstrap_iterations,
        bootstrap_seed=args.bootstrap_seed,
        synthetic_test_mode=args.synthetic_test_mode,
    )


if __name__ == "__main__":
    main()
