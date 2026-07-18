"""Join frozen Stage4B-U1 rankings with the evaluator-only label channel."""

from __future__ import annotations

import argparse
import csv
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from stage4b_u1_common import (
    IMPLEMENTATION_CHECKPOINT,
    INSERT_BUDGET,
    MAX_K,
    PROTECT_N,
    PROTOCOL_RELATIVE_PATH,
    SCHEMA_VERSION,
    STAGE4A_R2_STRATEGY_SUMMARY_SHA256,
    STAGE4A_R2_VERIFICATION_SHA256,
    assert_files_match_git_commit,
    exact_mcnemar_two_sided_pvalue,
    fisher_greater_pvalue,
    git_head,
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


def derive_inserted_ids(ranking: dict[str, Any]) -> tuple[list[str], list[str]]:
    query_id = str(ranking["query_id"])
    dense = [str(value) for value in ranking["dense_top20_unit_ids"]]
    q25 = [str(value) for value in ranking["q25_top20_unit_ids"]]
    final = [str(value) for value in ranking["final_top20_unit_ids"]]
    planned = int(ranking["planned_insert_count"])
    trigger = int(ranking["trigger_u1"])
    effective_k = len(dense)
    if effective_k < 1 or effective_k > MAX_K:
        raise ValueError(f"Evaluator effective-K is outside [1,{MAX_K}]: {query_id}")
    for label, values in (("dense", dense), ("q25", q25), ("final", final)):
        if len(values) != effective_k:
            raise ValueError(f"Evaluator {label} effective-K length differs: {query_id}")
        if len(set(values)) != effective_k:
            raise ValueError(f"Evaluator {label} effective-K IDs are not unique: {query_id}")
        if any(not unit_id for unit_id in values):
            raise ValueError(f"Evaluator {label} effective-K contains an empty ID: {query_id}")
    effective_protect_n = min(PROTECT_N, effective_k)
    if q25[:effective_protect_n] != dense[:effective_protect_n]:
        raise ValueError(f"Evaluator q25 violates effective protected prefix: {query_id}")
    maximum_planned = min(INSERT_BUDGET, effective_k - effective_protect_n)
    if planned < 0 or planned > maximum_planned:
        raise ValueError(
            f"Evaluator planned insert count is outside effective range "
            f"[0,{maximum_planned}]: {query_id}"
        )
    q25_inserted = q25[effective_protect_n : effective_protect_n + planned]
    if [str(value) for value in ranking["q25_inserted_unit_ids"]] != q25_inserted:
        raise ValueError(f"Evaluator q25 inserted IDs differ from effective-K: {query_id}")
    if trigger not in (0, 1):
        raise ValueError(f"Evaluator trigger is outside {{0,1}}: {query_id}")
    expected_final = q25 if trigger else dense
    final_inserted = q25_inserted if trigger else []
    if final != expected_final:
        raise ValueError(f"Evaluator final ranking violates on/off selection: {query_id}")
    if [str(value) for value in ranking["final_inserted_unit_ids"]] != final_inserted:
        raise ValueError(f"Evaluator final inserted IDs differ from derived inserts: {query_id}")
    if any(unit_id in set(dense[:effective_protect_n]) for unit_id in q25_inserted):
        raise ValueError(f"Evaluator inserted ID enters protected prefix: {query_id}")
    return q25_inserted, final_inserted


def assert_verified_ranking_structure(pre_gold: dict[str, Any]) -> None:
    checks = pre_gold.get("policy_and_ranking")
    if not isinstance(checks, dict) or checks.get("ranking_structure_check") is not True:
        raise ValueError(
            "Pre-Gold verification lacks independent effective-K, uniqueness, "
            "and candidate-membership attestation"
        )


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
        q25_inserted, final_inserted = derive_inserted_ids(row)
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


def baseline_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    if n == 0:
        raise ValueError("Cannot compute baseline equivalence on an empty evaluation")
    return {
        "queries": n,
        "dense_er20": sum(float(row["dense_er20"]) for row in rows) / n,
        "dense_cr20": sum(float(row["dense_cr20"]) for row in rows) / n,
        "q25_er20": sum(float(row["q25_er20"]) for row in rows) / n,
        "q25_cr20": sum(float(row["q25_cr20"]) for row in rows) / n,
        "q25_gain_events": sum(int(row["q25_gain_event"]) for row in rows),
        "q25_harm_events": sum(int(row["q25_harm_event"]) for row in rows),
    }


def load_official_baseline_reference(
    verification_path: Path, strategy_summary_path: Path
) -> dict[str, Any]:
    if sha256_file(verification_path) != STAGE4A_R2_VERIFICATION_SHA256:
        raise ValueError("Stage4A-R2 verification artifact SHA-256 differs")
    if sha256_file(strategy_summary_path) != STAGE4A_R2_STRATEGY_SUMMARY_SHA256:
        raise ValueError("Stage4A-R2 strategy-summary SHA-256 differs")
    verification = load_json(verification_path)
    if verification.get("status") != "VERIFIED_OFFICIAL_INTERNAL_METRICS":
        raise ValueError("Stage4A-R2 verification status differs")
    if (
        verification.get("sha256", {}).get("strategy_summary")
        != STAGE4A_R2_STRATEGY_SUMMARY_SHA256
    ):
        raise ValueError("Stage4A-R2 verification does not bind the strategy summary")
    with strategy_summary_path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    by_strategy = {
        str(row["strategy_id"]): row
        for row in rows
        if str(row["slice"]) == "ALL"
    }
    dense = by_strategy.get("dense_fixed")
    q25 = by_strategy.get("allquery_q25_p10_i4")
    if dense is None or q25 is None:
        raise ValueError("Stage4A-R2 ALL baseline rows are missing")
    return {
        "queries": int(dense["queries"]),
        "dense_er20": float(dense["evidence_recall_at_20"]),
        "dense_cr20": float(dense["chain_recall_at_20"]),
        "q25_er20": float(q25["evidence_recall_at_20"]),
        "q25_cr20": float(q25["chain_recall_at_20"]),
        "q25_gain_events": int(q25["gain_events"]),
        "q25_harm_events": int(q25["harm_events"]),
    }


def verify_baseline_equivalence(
    rows: list[dict[str, Any]],
    reference_path: Path,
    strategy_summary_path: Path | None,
    synthetic_test_mode: bool,
) -> dict[str, Any]:
    observed = baseline_metrics(rows)
    if synthetic_test_mode:
        reference = load_json(reference_path)
        if reference.get("status") != "SYNTHETIC_BASELINE_REFERENCE":
            raise ValueError("Synthetic baseline reference status differs")
        expected = reference.get("expected")
    else:
        if strategy_summary_path is None:
            raise ValueError("Formal evaluation requires the Stage4A-R2 strategy summary")
        expected = load_official_baseline_reference(reference_path, strategy_summary_path)
    if observed != expected:
        raise ValueError(
            f"HARD_FAILURE_IMPLEMENTATION_DRIFT: Stage4A-R2 baseline differs; "
            f"observed={observed}, expected={expected}"
        )
    return {
        "status": "STAGE4A_R2_BASELINE_EQUIVALENCE",
        "passed": True,
        "observed": observed,
        "reference_sha256": sha256_file(reference_path),
        "strategy_summary_sha256": (
            sha256_file(strategy_summary_path) if strategy_summary_path else None
        ),
    }


def assert_commit_is_ancestor(repo_root: Path, commit: str) -> None:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"], cwd=repo_root
    )
    if completed.returncode != 0:
        raise ValueError("Pre-Gold frozen commit is not an ancestor of evaluation HEAD")


def validate_pre_gold_verification(
    *,
    pre_gold_path: Path,
    policy: dict[str, Any],
    policy_path: Path,
    rankings_path: Path,
    evaluator_source: Path,
    synthetic_test_mode: bool,
) -> dict[str, Any]:
    pre_gold = load_json(pre_gold_path)
    if pre_gold.get("status") != "VERIFIED_PRE_GOLD":
        raise ValueError("Evaluator requires a VERIFIED_PRE_GOLD artifact")
    if pre_gold.get("evaluation") is not None:
        raise ValueError("Pre-Gold verification evaluation field must be null")
    assert_verified_ranking_structure(pre_gold)
    if bool(pre_gold.get("synthetic_test_mode")) != synthetic_test_mode:
        raise ValueError("Pre-Gold verification/evaluator synthetic modes differ")
    hashes = pre_gold.get("artifact_hashes", {})
    if hashes.get("policy") != sha256_file(policy_path):
        raise ValueError("Pre-Gold policy hash differs")
    if hashes.get("rankings") != sha256_file(rankings_path):
        raise ValueError("Pre-Gold ranking hash differs")
    if hashes.get("decisions") != policy.get("output_hashes", {}).get("decisions"):
        raise ValueError("Pre-Gold decision hash differs from policy")
    if hashes.get("channel_audit") != policy.get("input_hashes", {}).get("channel_audit"):
        raise ValueError("Pre-Gold channel-audit hash differs from policy")
    if pre_gold.get("implementation_hashes") != policy.get("implementation_hashes"):
        raise ValueError("Pre-Gold implementation hashes differ from policy")
    frozen_commit = str(pre_gold.get("frozen_commit_sha", ""))
    if not frozen_commit:
        raise ValueError("Pre-Gold verification lacks frozen_commit_sha")
    if not synthetic_test_mode:
        repo_root = evaluator_source.resolve().parents[1]
        assert_commit_is_ancestor(repo_root, frozen_commit)
        head = git_head(repo_root)
        try:
            relative = pre_gold_path.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError as error:
            raise ValueError("Formal pre-Gold verification is outside the repository") from error
        assert_files_match_git_commit(repo_root, head, [relative, "scripts/stage4b_u1_evaluate.py"])
    return pre_gold


def run_evaluation(
    *,
    rankings_path: Path,
    policy_path: Path,
    pre_gold_verification_path: Path,
    gold_map_path: Path,
    evaluator_audit_path: Path,
    stage4a_r2_verification_path: Path,
    stage4a_r2_strategy_summary_path: Path | None,
    query_audit_output: Path,
    summary_output: Path,
    run_role: str,
    bootstrap_iterations: int,
    bootstrap_seed: int,
    evaluator_source: Path,
    synthetic_test_mode: bool = False,
) -> dict[str, Any]:
    policy = load_json(policy_path)
    if policy.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Policy schema differs")
    if policy.get("implementation_checkpoint") != IMPLEMENTATION_CHECKPOINT:
        raise ValueError("Policy implementation checkpoint differs")
    if policy.get("protocol") != PROTOCOL_RELATIVE_PATH:
        raise ValueError("Policy protocol path differs")
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
    pre_gold = validate_pre_gold_verification(
        pre_gold_path=pre_gold_verification_path,
        policy=policy,
        policy_path=policy_path,
        rankings_path=rankings_path,
        evaluator_source=evaluator_source,
        synthetic_test_mode=synthetic_test_mode,
    )
    evaluator_audit = load_json(evaluator_audit_path)
    if evaluator_audit.get("status") != "EVALUATOR_CHANNEL_PREPARED_NO_RETRIEVAL_METRICS":
        raise ValueError("Evaluator channel audit status differs")
    if bool(evaluator_audit.get("retrieval_metrics_computed")):
        raise ValueError("Evaluator channel audit reports retrieval metrics")
    if bool(evaluator_audit.get("synthetic_test_mode")) != synthetic_test_mode:
        raise ValueError("Evaluator audit/evaluator synthetic modes differ")
    if evaluator_audit.get("run_role") != run_role:
        raise ValueError("Evaluator audit/evaluator run roles differ")
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
    baseline_equivalence = verify_baseline_equivalence(
        rows,
        stage4a_r2_verification_path,
        stage4a_r2_strategy_summary_path,
        synthetic_test_mode,
    )
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
        "implementation_checkpoint": IMPLEMENTATION_CHECKPOINT,
        "protocol": PROTOCOL_RELATIVE_PATH,
        "run_role": run_role,
        "policy_sha256": sha256_file(policy_path),
        "pre_gold_verification_sha256": sha256_file(pre_gold_verification_path),
        "pre_gold_frozen_commit_sha": pre_gold["frozen_commit_sha"],
        "ranking_sha256": ranking_sha,
        "gold_map_sha256": sha256_file(gold_map_path),
        "evaluator_audit_sha256": sha256_file(evaluator_audit_path),
        "query_audit_sha256": sha256_file(query_audit_output),
        "evaluator_source_sha256": sha256_file(evaluator_source),
        "baseline_equivalence": baseline_equivalence,
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
    parser.add_argument("--pre-gold-verification", required=True, type=Path)
    parser.add_argument("--gold-map", required=True, type=Path)
    parser.add_argument("--evaluator-audit", required=True, type=Path)
    parser.add_argument("--stage4a-r2-verification", required=True, type=Path)
    parser.add_argument("--stage4a-r2-strategy-summary", type=Path)
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
        pre_gold_verification_path=args.pre_gold_verification,
        gold_map_path=args.gold_map,
        evaluator_audit_path=args.evaluator_audit,
        stage4a_r2_verification_path=args.stage4a_r2_verification,
        stage4a_r2_strategy_summary_path=args.stage4a_r2_strategy_summary,
        query_audit_output=args.query_audit_output,
        summary_output=args.summary_output,
        run_role=args.run_role,
        bootstrap_iterations=args.bootstrap_iterations,
        bootstrap_seed=args.bootstrap_seed,
        evaluator_source=Path(__file__),
        synthetic_test_mode=args.synthetic_test_mode,
    )


if __name__ == "__main__":
    main()
