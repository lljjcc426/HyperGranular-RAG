"""Independent integrity verifier for Stage4B-U1 policy and ranking artifacts."""

from __future__ import annotations

import argparse
import bisect
import hashlib
import math
import subprocess
from pathlib import Path
from typing import Any

from stage4b_u1_common import (
    BUDGET_FRACTION,
    FROZEN_BATCH_SIZE,
    FROZEN_MAX_LENGTH,
    FROZEN_MODEL_NAME,
    IMPLEMENTATION_CHECKPOINT,
    OFFICIAL_DEVELOPMENT_QUERIES,
    OFFICIAL_DEVELOPMENT_QUERY_ID_SHA256,
    POLICY_IMPLEMENTATION_FILES,
    PROTOCOL_RELATIVE_PATH,
    PROTECT_N,
    SCHEMA_VERSION,
    STAGE4A_R2_SOURCE_AUDIT_SHA256,
    assert_files_match_git_commit,
    assert_no_prohibited_keys,
    git_head,
    id_digest,
    implementation_hashes,
    load_json,
    load_jsonl,
    sha256_file,
    write_json,
)
from stage4b_u1_goldfree_retrieval import RetrievalConfig


DECISION_KEYS = {
    "query_id",
    "dataset",
    "sample_id",
    "ball_score_margin",
    "boundary_margin",
    "selected_edge_count",
    "planned_insert_count",
    "feasible",
    "u_margin",
    "u_boundary",
    "r_edge",
    "r_candidate",
    "uncertainty",
    "readiness",
    "score",
    "tie_hash",
    "ordered_rank",
    "trigger_u1",
}
RANKING_KEYS = {
    "query_id",
    "dataset",
    "sample_id",
    "trigger_u1",
    "planned_insert_count",
    "dense_top20_unit_ids",
    "q25_top20_unit_ids",
    "q25_inserted_unit_ids",
    "final_top20_unit_ids",
    "final_inserted_unit_ids",
}
ECDF_KEYS = {
    "ball_score_margin",
    "boundary_margin",
    "log1p_selected_edge_count",
    "log1p_planned_insert_count",
}


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=tolerance)


def finite(value: Any, label: str) -> float:
    converted = float(value)
    if not math.isfinite(converted):
        raise ValueError(f"Non-finite verifier value for {label}")
    return converted


def independent_tie_hash(query_id: str) -> str:
    return hashlib.sha256(f"stage4b_u1_v2::{query_id}".encode("utf-8")).hexdigest().upper()


def independent_ecdf(reference: list[float], value: float) -> float:
    if not reference:
        raise ValueError("Verifier ECDF reference is empty")
    checked = [finite(item, "ECDF reference") for item in reference]
    if checked != sorted(checked):
        raise ValueError("Verifier ECDF reference is not sorted")
    value = finite(value, "ECDF value")
    left = bisect.bisect_left(checked, value)
    right = bisect.bisect_right(checked, value)
    return (left + 0.5 * (right - left)) / len(checked)


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


def verify_references(
    decisions: list[dict[str, Any]], policy: dict[str, Any]
) -> dict[str, list[float]]:
    references = policy.get("ecdf_references")
    if not isinstance(references, dict) or set(references) != ECDF_KEYS:
        raise ValueError("Policy ECDF reference keys differ")
    checked: dict[str, list[float]] = {}
    for key, values in references.items():
        if not isinstance(values, list) or not values:
            raise ValueError(f"Policy ECDF reference is empty: {key}")
        checked[key] = [finite(value, f"ECDF {key}") for value in values]
        if checked[key] != sorted(checked[key]):
            raise ValueError(f"Policy ECDF reference is unsorted: {key}")

    if policy.get("run_role") == "development":
        feasible = [row for row in decisions if int(row["feasible"]) == 1]
        expected = {
            "ball_score_margin": sorted(float(row["ball_score_margin"]) for row in feasible),
            "boundary_margin": sorted(float(row["boundary_margin"]) for row in feasible),
            "log1p_selected_edge_count": sorted(
                math.log1p(int(row["selected_edge_count"])) for row in feasible
            ),
            "log1p_planned_insert_count": sorted(
                math.log1p(int(row["planned_insert_count"])) for row in feasible
            ),
        }
        if checked != expected:
            raise ValueError("Development ECDF references differ from independent fitting")
    return checked


def verify_derived_decisions(
    decisions: list[dict[str, Any]], references: dict[str, list[float]]
) -> list[dict[str, Any]]:
    for row in decisions:
        if set(row) != DECISION_KEYS:
            raise ValueError(f"Decision schema differs: {row.get('query_id')}")
        query_id = str(row["query_id"])
        if str(row["tie_hash"]) != independent_tie_hash(query_id):
            raise ValueError(f"Decision tie hash differs: {query_id}")
        planned = int(row["planned_insert_count"])
        selected_edges = int(row["selected_edge_count"])
        expected_feasible = int(selected_edges > 0 and planned > 0)
        if int(row["feasible"]) != expected_feasible:
            raise ValueError(f"Decision feasibility differs: {query_id}")
        finite(row["ball_score_margin"], f"ball margin {query_id}")
        finite(row["boundary_margin"], f"boundary margin {query_id}")
        if not expected_feasible:
            for key in (
                "u_margin",
                "u_boundary",
                "r_edge",
                "r_candidate",
                "uncertainty",
                "readiness",
                "score",
                "ordered_rank",
            ):
                if row[key] is not None:
                    raise ValueError(f"Infeasible decision has derived value {key}: {query_id}")
            continue
        expected = {
            "u_margin": 1.0
            - independent_ecdf(references["ball_score_margin"], row["ball_score_margin"]),
            "u_boundary": 1.0
            - independent_ecdf(references["boundary_margin"], row["boundary_margin"]),
            "r_edge": independent_ecdf(
                references["log1p_selected_edge_count"], math.log1p(selected_edges)
            ),
            "r_candidate": independent_ecdf(
                references["log1p_planned_insert_count"], math.log1p(planned)
            ),
        }
        expected["uncertainty"] = (expected["u_margin"] + expected["u_boundary"]) / 2.0
        expected["readiness"] = math.sqrt(expected["r_edge"] * expected["r_candidate"])
        expected["score"] = expected["uncertainty"] * expected["readiness"]
        for key, value in expected.items():
            if not close(row[key], value):
                raise ValueError(f"Decision independently recomputed {key} differs: {query_id}")

    ordered = sorted(
        (row for row in decisions if int(row["feasible"]) == 1),
        key=lambda row: (-float(row["score"]), independent_tie_hash(str(row["query_id"]))),
    )
    for rank, row in enumerate(ordered, start=1):
        if int(row["ordered_rank"]) != rank:
            raise ValueError(f"Decision ordered rank differs: {row['query_id']}")
    return ordered


def derive_q25_inserted(ranking: dict[str, Any]) -> list[str]:
    query_id = str(ranking["query_id"])
    dense = [str(value) for value in ranking["dense_top20_unit_ids"]]
    q25 = [str(value) for value in ranking["q25_top20_unit_ids"]]
    planned = int(ranking["planned_insert_count"])
    if len(dense) != 20 or len(q25) != 20:
        raise ValueError(f"Top-20 length differs: {query_id}")
    if len(set(dense)) != 20 or len(set(q25)) != 20:
        raise ValueError(f"Top-20 IDs are not unique: {query_id}")
    if q25[:PROTECT_N] != dense[:PROTECT_N]:
        raise ValueError(f"q25 ranking violates dense Top-10 protection: {query_id}")
    if planned < 0 or planned > 4:
        raise ValueError(f"Planned insert count is outside [0,4]: {query_id}")
    derived = q25[PROTECT_N : PROTECT_N + planned]
    if any(unit_id in set(dense[:PROTECT_N]) for unit_id in derived):
        raise ValueError(f"q25 inserted ID enters dense Top-10: {query_id}")
    return derived


def verify_policy_and_rankings(
    decisions: list[dict[str, Any]],
    rankings: list[dict[str, Any]],
    policy: dict[str, Any],
    valid_unit_ids_by_query: dict[str, set[str]] | None = None,
) -> dict[str, Any]:
    assert_no_prohibited_keys(decisions, "verifier.decisions")
    assert_no_prohibited_keys(rankings, "verifier.rankings")
    if policy.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Policy schema differs")
    if policy.get("implementation_checkpoint") != IMPLEMENTATION_CHECKPOINT:
        raise ValueError("Policy implementation checkpoint differs")
    if bool(policy.get("evaluation_labels_loaded")):
        raise ValueError("Policy reports evaluation-label access")
    if policy.get("retrieval_config") != RetrievalConfig().to_dict():
        raise ValueError("Policy retrieval config differs from the frozen configuration")

    decisions_by_query = {str(row["query_id"]): row for row in decisions}
    rankings_by_query = {str(row["query_id"]): row for row in rankings}
    if len(decisions_by_query) != len(decisions) or len(rankings_by_query) != len(rankings):
        raise ValueError("Duplicate decision or ranking query IDs")
    if set(decisions_by_query) != set(rankings_by_query):
        raise ValueError("Decision/ranking query sets differ")

    references = verify_references(decisions, policy)
    ordered = verify_derived_decisions(decisions, references)
    allquery_planned = sum(int(row["planned_insert_count"]) for row in ordered)
    budget_units = math.floor(allquery_planned * BUDGET_FRACTION)
    cumulative = 0
    selected = 0
    for row in ordered:
        cost = int(row["planned_insert_count"])
        if cumulative + cost > budget_units:
            break
        cumulative += cost
        selected += 1
    if selected == 0:
        raise ValueError("Independent allocation found no non-empty prefix")
    selected_ids = {str(row["query_id"]) for row in ordered[:selected]}
    for row in decisions:
        expected_trigger = int(str(row["query_id"]) in selected_ids)
        if int(row["trigger_u1"]) != expected_trigger:
            raise ValueError(f"Trigger differs from independent ordered prefix: {row['query_id']}")

    cutoff = ordered[selected - 1]
    allocation = policy.get("allocation", {})
    expected_allocation = {
        "budget_fraction": BUDGET_FRACTION,
        "n_feasible": len(ordered),
        "allquery_planned_inserts": allquery_planned,
        "budget_units": budget_units,
        "selected_queries": selected,
        "selected_planned_inserts": cumulative,
        "cutoff_score": float(cutoff["score"]),
        "cutoff_hash": independent_tie_hash(str(cutoff["query_id"])),
        "score_direction": "descending",
        "selection_operator": "ordered_prefix_cumulative_cost_lte_budget",
    }
    if set(allocation) != set(expected_allocation):
        raise ValueError("Policy allocation schema differs")
    for key, value in expected_allocation.items():
        observed = allocation[key]
        if isinstance(value, float):
            if not close(observed, value):
                raise ValueError(f"Policy allocation differs at {key}")
        elif observed != value:
            raise ValueError(f"Policy allocation differs at {key}")

    for query_id, ranking in rankings_by_query.items():
        if set(ranking) != RANKING_KEYS:
            raise ValueError(f"Ranking schema differs: {query_id}")
        decision = decisions_by_query[query_id]
        if int(ranking["trigger_u1"]) != int(decision["trigger_u1"]):
            raise ValueError(f"Decision/ranking trigger differs: {query_id}")
        if int(ranking["planned_insert_count"]) != int(decision["planned_insert_count"]):
            raise ValueError(f"Decision/ranking planned inserts differ: {query_id}")
        derived_inserted = derive_q25_inserted(ranking)
        provided_inserted = [str(value) for value in ranking["q25_inserted_unit_ids"]]
        if provided_inserted != derived_inserted:
            raise ValueError(f"q25 inserted IDs differ from Top-20 structure: {query_id}")
        trigger = int(decision["trigger_u1"])
        expected_final = (
            ranking["q25_top20_unit_ids"] if trigger else ranking["dense_top20_unit_ids"]
        )
        expected_final_inserted = derived_inserted if trigger else []
        if ranking["final_top20_unit_ids"] != expected_final:
            raise ValueError(f"Final ranking violates the on/off selector: {query_id}")
        if [str(value) for value in ranking["final_inserted_unit_ids"]] != expected_final_inserted:
            raise ValueError(f"Final inserted IDs differ from derived on/off inserts: {query_id}")
        if valid_unit_ids_by_query is not None:
            allowed = valid_unit_ids_by_query[query_id]
            if not set(str(value) for value in expected_final).issubset(allowed):
                raise ValueError(f"Ranking references an unknown query unit: {query_id}")
    return {
        "queries": len(rankings),
        "n_feasible": len(ordered),
        "selected_queries": selected,
        "allquery_planned_inserts": allquery_planned,
        "selected_planned_inserts": cumulative,
        "resource_reduction": 1.0 - cumulative / allquery_planned,
        "independent_score_recomputation_check": True,
        "independent_cutoff_check": True,
        "ranking_structure_check": True,
        "ordered_prefix_check": True,
    }


def verify_evaluation(
    rankings: list[dict[str, Any]], query_audit: list[dict[str, Any]], summary: dict[str, Any]
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
        ) / n,
        "u1_cr20_delta_vs_q25": sum(
            float(row["u1_cr20"]) - float(row["q25_cr20"]) for row in query_audit
        ) / n,
        "q25_inserted_units": sum(int(row["q25_inserted_units"]) for row in query_audit),
        "u1_inserted_units": sum(int(row["u1_inserted_units"]) for row in query_audit),
        "q25_gain_events": sum(int(row["q25_gain_event"]) for row in query_audit),
        "q25_harm_events": sum(int(row["q25_harm_event"]) for row in query_audit),
    }
    for key, value in recomputed.items():
        observed = overall[key]
        if isinstance(value, float) and not close(observed, value):
            raise ValueError(f"Evaluation summary differs at {key}")
        if isinstance(value, int) and int(observed) != value:
            raise ValueError(f"Evaluation summary differs at {key}")
    return {"queries": n, "event_subset_check": True, "summary_recomputation_check": True}


def assert_commit_is_ancestor(repo_root: Path, commit: str) -> None:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"], cwd=repo_root
    )
    if completed.returncode != 0:
        raise ValueError("Policy git commit is not an ancestor of the verification commit")


def relative_repo_paths(repo_root: Path, paths: list[Path]) -> list[str]:
    relative: list[str] = []
    for path in paths:
        try:
            relative.append(path.resolve().relative_to(repo_root.resolve()).as_posix())
        except ValueError as error:
            raise ValueError(f"Formal pre-Gold artifact is outside the repository: {path}") from error
    return relative


def run_verification(
    *,
    units_path: Path,
    queries_path: Path,
    channel_audit_path: Path,
    embedding_cache_path: Path,
    decisions_path: Path,
    rankings_path: Path,
    policy_path: Path,
    controller_source: Path,
    source_audit_path: Path | None,
    gold_map_path: Path | None,
    evaluator_audit_path: Path | None,
    query_audit_path: Path | None,
    summary_path: Path | None,
    output_path: Path,
    synthetic_test_mode: bool = False,
) -> dict[str, Any]:
    units = load_jsonl(units_path)
    queries = load_jsonl(queries_path)
    assert_no_prohibited_keys(units, "verifier.units")
    assert_no_prohibited_keys(queries, "verifier.queries")
    query_ids = [str(row["query_id"]) for row in queries]
    unit_ids_by_query: dict[str, set[str]] = {query_id: set() for query_id in query_ids}
    for unit in units:
        unit_ids_by_query[str(unit["query_id"])].add(str(unit["unit_id"]))

    channel_audit = load_json(channel_audit_path)
    assert_no_prohibited_keys(channel_audit, "verifier.controller_channel_audit")
    if channel_audit.get("status") != "CONTROLLER_CHANNEL_PREPARED_NO_RETRIEVAL_METRICS":
        raise ValueError("Verifier controller-channel audit status differs")
    if bool(channel_audit.get("synthetic_test_mode")) != synthetic_test_mode:
        raise ValueError("Verifier/channel synthetic modes differ")
    if channel_audit["channel_hashes"]["unlabeled_units"] != sha256_file(units_path):
        raise ValueError("Verifier unlabeled-unit hash differs")
    if channel_audit["channel_hashes"]["unlabeled_queries"] != sha256_file(queries_path):
        raise ValueError("Verifier unlabeled-query hash differs")
    if channel_audit["query_id_sha256"] != id_digest(query_ids):
        raise ValueError("Verifier channel query digest differs")

    decisions = load_jsonl(decisions_path)
    rankings = load_jsonl(rankings_path)
    policy = load_json(policy_path)
    expected_status = "SYNTHETIC_TEST_ONLY" if synthetic_test_mode else "POLICY_FROZEN_BEFORE_EVALUATION"
    if policy.get("status") != expected_status:
        raise ValueError("Policy status differs from verifier mode")
    if policy.get("output_hashes", {}).get("decisions") != sha256_file(decisions_path):
        raise ValueError("Verifier decision hash differs from policy")
    if policy.get("output_hashes", {}).get("rankings") != sha256_file(rankings_path):
        raise ValueError("Verifier ranking hash differs from policy")
    expected_inputs = {
        "unlabeled_units": sha256_file(units_path),
        "unlabeled_queries": sha256_file(queries_path),
        "channel_audit": sha256_file(channel_audit_path),
        "embedding_cache": sha256_file(embedding_cache_path),
        "source_audit": sha256_file(source_audit_path) if source_audit_path else None,
    }
    if policy.get("input_hashes") != expected_inputs:
        raise ValueError("Policy input hashes differ from verifier inputs")

    repo_root = controller_source.resolve().parents[1]
    static = verify_static_controller_boundary(controller_source)
    current_hashes = implementation_hashes(repo_root)
    if policy.get("implementation_hashes") != current_hashes:
        raise ValueError("Policy implementation file hash mismatch")
    if static["controller_source_sha256"] != current_hashes["controller_source_sha256"]:
        raise ValueError("Static controller hash differs from implementation binding")
    protocol_sha = sha256_file(repo_root / PROTOCOL_RELATIVE_PATH)
    if policy.get("protocol") != PROTOCOL_RELATIVE_PATH or policy.get("protocol_sha256") != protocol_sha:
        raise ValueError("Policy protocol binding differs")

    frozen_commit_sha = git_head(repo_root)
    if not synthetic_test_mode:
        if policy.get("run_role") != "development":
            raise ValueError("Formal verifier currently permits only U1-D development")
        if len(query_ids) != OFFICIAL_DEVELOPMENT_QUERIES or id_digest(query_ids) != OFFICIAL_DEVELOPMENT_QUERY_ID_SHA256:
            raise ValueError("Formal verifier development boundary differs")
        if source_audit_path is None or sha256_file(source_audit_path) != STAGE4A_R2_SOURCE_AUDIT_SHA256:
            raise ValueError("Formal verifier source-audit binding differs")
        if (
            policy.get("model_name") != FROZEN_MODEL_NAME
            or int(policy.get("max_length", -1)) != FROZEN_MAX_LENGTH
            or int(policy.get("batch_size", -1)) != FROZEN_BATCH_SIZE
        ):
            raise ValueError("Formal verifier encoder configuration differs")
        policy_commit = str(policy.get("git_commit_sha", ""))
        assert_commit_is_ancestor(repo_root, policy_commit)
        assert_files_match_git_commit(
            repo_root,
            frozen_commit_sha,
            relative_repo_paths(
                repo_root,
                [channel_audit_path, decisions_path, rankings_path, policy_path],
            ),
        )
        assert_files_match_git_commit(
            repo_root,
            policy_commit,
            [*POLICY_IMPLEMENTATION_FILES.values(), PROTOCOL_RELATIVE_PATH],
        )

    policy_checks = verify_policy_and_rankings(
        decisions, rankings, policy, unit_ids_by_query
    )

    evaluation_checks: dict[str, Any] | None = None
    evaluation_paths = (gold_map_path, evaluator_audit_path, query_audit_path, summary_path)
    if any(path is not None for path in evaluation_paths):
        if not all(path is not None for path in evaluation_paths):
            raise ValueError("Evaluation verification requires all evaluator artifacts")
        assert gold_map_path and evaluator_audit_path and query_audit_path and summary_path
        summary = load_json(summary_path)
        if summary["ranking_sha256"] != sha256_file(rankings_path):
            raise ValueError("Evaluation summary ranking hash differs")
        if summary["gold_map_sha256"] != sha256_file(gold_map_path):
            raise ValueError("Evaluation summary Gold-map hash differs")
        if summary["evaluator_audit_sha256"] != sha256_file(evaluator_audit_path):
            raise ValueError("Evaluation summary evaluator-audit hash differs")
        if summary["query_audit_sha256"] != sha256_file(query_audit_path):
            raise ValueError("Evaluation summary query-audit hash differs")
        evaluation_checks = verify_evaluation(rankings, load_jsonl(query_audit_path), summary)

    status = "VERIFIED_PRE_GOLD" if evaluation_checks is None else "VERIFIED_POST_GOLD"
    result = {
        "schema_version": SCHEMA_VERSION,
        "implementation_checkpoint": IMPLEMENTATION_CHECKPOINT,
        "status": status,
        "synthetic_test_mode": synthetic_test_mode,
        "frozen_commit_sha": frozen_commit_sha,
        "static_controller_boundary": static,
        "implementation_hashes": current_hashes,
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
    parser.add_argument("--embedding-cache", required=True, type=Path)
    parser.add_argument("--decisions", required=True, type=Path)
    parser.add_argument("--rankings", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--controller-source", required=True, type=Path)
    parser.add_argument("--source-audit", type=Path)
    parser.add_argument("--gold-map", type=Path)
    parser.add_argument("--evaluator-audit", type=Path)
    parser.add_argument("--query-audit", type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--synthetic-test-mode", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_verification(
        units_path=args.units,
        queries_path=args.queries,
        channel_audit_path=args.channel_audit,
        embedding_cache_path=args.embedding_cache,
        decisions_path=args.decisions,
        rankings_path=args.rankings,
        policy_path=args.policy,
        controller_source=args.controller_source,
        source_audit_path=args.source_audit,
        gold_map_path=args.gold_map,
        evaluator_audit_path=args.evaluator_audit,
        query_audit_path=args.query_audit,
        summary_path=args.summary,
        output_path=args.output,
        synthetic_test_mode=args.synthetic_test_mode,
    )


if __name__ == "__main__":
    main()
