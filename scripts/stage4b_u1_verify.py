"""Independent integrity verifier for Stage4B-U1 channels, policy, and evaluation."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

from stage4b_u1_common import (
    BUDGET_FRACTION,
    SCHEMA_VERSION,
    assert_no_prohibited_keys,
    id_digest,
    load_json,
    load_jsonl,
    sha256_file,
    write_json,
)


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=tolerance)


def verify_static_controller_boundary(controller_source: Path) -> dict[str, Any]:
    text = controller_source.read_text(encoding="utf-8")
    forbidden_fragments = (
        "--gold-map",
        "stage4b_u1_evaluate",
        "stage4b_u1_prepare_channels",
        "load_gold",
    )
    present = [fragment for fragment in forbidden_fragments if fragment in text]
    if present:
        raise ValueError(f"Controller source crosses the evaluation boundary: {present}")
    return {
        "controller_source_sha256": sha256_file(controller_source),
        "forbidden_interface_fragments_absent": True,
    }


def verify_policy_and_rankings(
    decisions: list[dict[str, Any]],
    rankings: list[dict[str, Any]],
    policy: dict[str, Any],
) -> dict[str, Any]:
    assert_no_prohibited_keys(decisions, "verifier.decisions")
    assert_no_prohibited_keys(rankings, "verifier.rankings")
    if policy.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Policy schema differs")
    if bool(policy.get("evaluation_labels_loaded")):
        raise ValueError("Policy reports evaluation-label access")
    decisions_by_query = {str(row["query_id"]): row for row in decisions}
    rankings_by_query = {str(row["query_id"]): row for row in rankings}
    if len(decisions_by_query) != len(decisions) or len(rankings_by_query) != len(rankings):
        raise ValueError("Duplicate decision or ranking query IDs")
    if set(decisions_by_query) != set(rankings_by_query):
        raise ValueError("Decision/ranking query sets differ")

    feasible = [row for row in decisions if int(row["feasible"]) == 1]
    ordered = sorted(feasible, key=lambda row: (-float(row["score"]), str(row["tie_hash"])))
    allquery_planned = sum(int(row["planned_insert_count"]) for row in feasible)
    budget_units = math.floor(allquery_planned * BUDGET_FRACTION)
    cumulative = 0
    selected = 0
    for row in ordered:
        cost = int(row["planned_insert_count"])
        if cumulative + cost > budget_units:
            break
        cumulative += cost
        selected += 1
    expected_selected = {str(row["query_id"]) for row in ordered[:selected]}
    observed_selected = {
        str(row["query_id"]) for row in decisions if int(row["trigger_u1"]) == 1
    }
    if expected_selected != observed_selected:
        raise ValueError("Trigger set differs from the unique ordered-prefix allocation")
    allocation = policy["allocation"]
    expected_allocation = {
        "n_feasible": len(feasible),
        "allquery_planned_inserts": allquery_planned,
        "budget_units": budget_units,
        "selected_queries": selected,
        "selected_planned_inserts": cumulative,
    }
    for key, value in expected_allocation.items():
        if int(allocation[key]) != value:
            raise ValueError(f"Policy allocation differs at {key}")
    if float(allocation["budget_fraction"]) != BUDGET_FRACTION:
        raise ValueError("Policy budget fraction differs")

    for query_id, ranking in rankings_by_query.items():
        decision = decisions_by_query[query_id]
        trigger = int(decision["trigger_u1"])
        if int(ranking["trigger_u1"]) != trigger:
            raise ValueError(f"Decision/ranking trigger differs: {query_id}")
        if int(ranking["planned_insert_count"]) != len(ranking["q25_inserted_unit_ids"]):
            raise ValueError(f"Planned/q25 inserted count differs: {query_id}")
        expected_final = (
            ranking["q25_top20_unit_ids"] if trigger else ranking["dense_top20_unit_ids"]
        )
        expected_inserted = ranking["q25_inserted_unit_ids"] if trigger else []
        if ranking["final_top20_unit_ids"] != expected_final:
            raise ValueError(f"Final ranking violates the on/off selector: {query_id}")
        if ranking["final_inserted_unit_ids"] != expected_inserted:
            raise ValueError(f"Final inserted units violate the on/off selector: {query_id}")
    return {
        "queries": len(rankings),
        "n_feasible": len(feasible),
        "selected_queries": selected,
        "allquery_planned_inserts": allquery_planned,
        "selected_planned_inserts": cumulative,
        "resource_reduction": 1.0 - cumulative / allquery_planned,
        "ranking_subset_check": True,
        "ordered_prefix_check": True,
    }


def verify_evaluation(
    rankings: list[dict[str, Any]],
    query_audit: list[dict[str, Any]],
    summary: dict[str, Any],
) -> dict[str, Any]:
    ranking_by_query = {str(row["query_id"]): row for row in rankings}
    audit_by_query = {str(row["query_id"]): row for row in query_audit}
    if set(ranking_by_query) != set(audit_by_query):
        raise ValueError("Ranking/evaluation query sets differ")
    for query_id, row in audit_by_query.items():
        trigger = int(ranking_by_query[query_id]["trigger_u1"])
        if int(row["trigger_u1"]) != trigger:
            raise ValueError(f"Evaluation trigger differs: {query_id}")
        if int(row["u1_gain_event"]) != int(row["q25_gain_event"] and trigger):
            raise ValueError(f"U1 gain is not a q25 gain subset: {query_id}")
        if int(row["u1_harm_event"]) != int(row["q25_harm_event"] and trigger):
            raise ValueError(f"U1 harm is not a q25 harm subset: {query_id}")

    n = len(query_audit)
    overall = summary["overall"]
    recomputed = {
        "u1_cr20": sum(float(row["u1_cr20"]) for row in query_audit) / n,
        "u1_cr20_delta_vs_dense": sum(
            float(row["u1_cr20"]) - float(row["dense_cr20"]) for row in query_audit
        )
        / n,
        "u1_cr20_delta_vs_q25": sum(
            float(row["u1_cr20"]) - float(row["q25_cr20"]) for row in query_audit
        )
        / n,
        "q25_inserted_units": sum(int(row["q25_inserted_units"]) for row in query_audit),
        "u1_inserted_units": sum(int(row["u1_inserted_units"]) for row in query_audit),
        "q25_gain_events": sum(int(row["q25_gain_event"]) for row in query_audit),
        "q25_harm_events": sum(int(row["q25_harm_event"]) for row in query_audit),
        "retained_gain_events": sum(
            int(row["q25_gain_event"]) * int(row["trigger_u1"]) for row in query_audit
        ),
        "retained_harm_events": sum(
            int(row["q25_harm_event"]) * int(row["trigger_u1"]) for row in query_audit
        ),
    }
    for key, value in recomputed.items():
        observed = overall[key]
        if isinstance(value, float):
            if not close(observed, value):
                raise ValueError(f"Evaluation summary differs at {key}")
        elif int(observed) != value:
            raise ValueError(f"Evaluation summary differs at {key}")
    return {
        "queries": n,
        "gain_subset_check": True,
        "harm_subset_check": True,
        "summary_recomputation_check": True,
    }


def run_verification(
    *,
    units_path: Path,
    queries_path: Path,
    channel_audit_path: Path,
    decisions_path: Path,
    rankings_path: Path,
    policy_path: Path,
    controller_source: Path,
    gold_map_path: Path | None,
    evaluator_audit_path: Path | None,
    query_audit_path: Path | None,
    summary_path: Path | None,
    output_path: Path,
) -> dict[str, Any]:
    units = load_jsonl(units_path)
    queries = load_jsonl(queries_path)
    assert_no_prohibited_keys(units, "verifier.units")
    assert_no_prohibited_keys(queries, "verifier.queries")
    channel_audit = load_json(channel_audit_path)
    assert_no_prohibited_keys(channel_audit, "verifier.controller_channel_audit")
    if channel_audit.get("status") != "CONTROLLER_CHANNEL_PREPARED_NO_RETRIEVAL_METRICS":
        raise ValueError("Verifier controller-channel audit status differs")
    if channel_audit["channel_hashes"]["unlabeled_units"] != sha256_file(units_path):
        raise ValueError("Verifier unlabeled-unit hash differs")
    if channel_audit["channel_hashes"]["unlabeled_queries"] != sha256_file(queries_path):
        raise ValueError("Verifier unlabeled-query hash differs")
    if channel_audit["query_id_sha256"] != id_digest(row["query_id"] for row in queries):
        raise ValueError("Verifier channel query digest differs")

    decisions = load_jsonl(decisions_path)
    rankings = load_jsonl(rankings_path)
    policy = load_json(policy_path)
    if policy["output_hashes"]["decisions"] != sha256_file(decisions_path):
        raise ValueError("Verifier decision hash differs from policy")
    if policy["output_hashes"]["rankings"] != sha256_file(rankings_path):
        raise ValueError("Verifier ranking hash differs from policy")
    static = verify_static_controller_boundary(controller_source)
    if static["controller_source_sha256"] != policy["controller_source_sha256"]:
        raise ValueError("Controller source differs from the frozen policy")
    policy_checks = verify_policy_and_rankings(decisions, rankings, policy)

    evaluation_checks: dict[str, Any] | None = None
    if any(
        path is not None
        for path in (gold_map_path, evaluator_audit_path, query_audit_path, summary_path)
    ):
        if not all(
            path is not None
            for path in (gold_map_path, evaluator_audit_path, query_audit_path, summary_path)
        ):
            raise ValueError("Evaluation verification requires all evaluator artifacts")
        assert gold_map_path is not None
        assert evaluator_audit_path is not None
        assert query_audit_path is not None
        assert summary_path is not None
        summary = load_json(summary_path)
        if summary["ranking_sha256"] != sha256_file(rankings_path):
            raise ValueError("Evaluation summary ranking hash differs")
        if summary["gold_map_sha256"] != sha256_file(gold_map_path):
            raise ValueError("Evaluation summary Gold-map hash differs")
        if summary["evaluator_audit_sha256"] != sha256_file(evaluator_audit_path):
            raise ValueError("Evaluation summary evaluator-audit hash differs")
        if summary["query_audit_sha256"] != sha256_file(query_audit_path):
            raise ValueError("Evaluation summary query-audit hash differs")
        evaluation_checks = verify_evaluation(
            rankings, load_jsonl(query_audit_path), summary
        )

    result = {
        "schema_version": SCHEMA_VERSION,
        "status": "VERIFIED",
        "static_controller_boundary": static,
        "policy_and_ranking": policy_checks,
        "evaluation": evaluation_checks,
        "artifact_hashes": {
            "channel_audit": sha256_file(channel_audit_path),
            "decisions": sha256_file(decisions_path),
            "rankings": sha256_file(rankings_path),
            "policy": sha256_file(policy_path),
        },
    }
    write_json(output_path, result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", required=True, type=Path)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--channel-audit", required=True, type=Path)
    parser.add_argument("--decisions", required=True, type=Path)
    parser.add_argument("--rankings", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--controller-source", required=True, type=Path)
    parser.add_argument("--gold-map", type=Path)
    parser.add_argument("--evaluator-audit", type=Path)
    parser.add_argument("--query-audit", type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_verification(
        units_path=args.units,
        queries_path=args.queries,
        channel_audit_path=args.channel_audit,
        decisions_path=args.decisions,
        rankings_path=args.rankings,
        policy_path=args.policy,
        controller_source=args.controller_source,
        gold_map_path=args.gold_map,
        evaluator_audit_path=args.evaluator_audit,
        query_audit_path=args.query_audit,
        summary_path=args.summary,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
