"""Direct Gold-free controller for the simplified Stage4B-U1-D route."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
from typing import Any

from stage4b_u1_common import (
    IMPLEMENTATION_CHECKPOINT,
    PROTOCOL_RELATIVE_PATH,
    SCHEMA_VERSION,
    assert_no_prohibited_keys,
    git_head,
    id_digest,
    sha256_file,
)
from stage4b_u1_goldfree_controller import (
    assert_cache_fingerprint_unchanged,
    promote_pending_outputs,
    remove_outputs_created_by_this_run,
    validate_pending_output_targets,
    write_json_in_existing_directory,
    write_jsonl_in_existing_directory,
)
from stage4b_u1_goldfree_retrieval import (
    RetrievalConfig,
    allocate_budget,
    build_query_decisions,
    fit_ecdf_references,
    score_rows,
)
from stage4b_u1_simplified_preflight import (
    EXECUTION_PROFILE,
    SIMPLIFIED_PROTOCOL_PATH,
    SIMPLIFIED_RUNNER_PATH,
    implementation_hash_map,
    resolve_path,
    run_preflight,
)


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
POLICY_KEYS = {
    "schema_version",
    "implementation_checkpoint",
    "execution_profile",
    "protocol",
    "protocol_sha256",
    "simplified_execution_protocol",
    "simplified_execution_protocol_sha256",
    "execution_config",
    "execution_config_sha256",
    "status",
    "run_role",
    "git_commit_sha",
    "code_commit_sha",
    "sample_id_sha256",
    "query_id_sha256",
    "queries",
    "units",
    "model_name",
    "max_length",
    "batch_size",
    "retrieval_config",
    "ecdf_definition",
    "ecdf_references",
    "allocation",
    "input_hashes",
    "output_hashes",
    "implementation_hashes",
    "controller_source_sha256",
    "parent_development_policy_sha256",
    "evaluation_labels_loaded",
}


def _retrieval_config(config: dict[str, Any]) -> RetrievalConfig:
    values = {
        key: config["retrieval"][key]
        for key in RetrievalConfig().to_dict()
    }
    return RetrievalConfig(**values)


def _config_display_path(config_path: Path, repo_root: Path) -> str:
    try:
        return config_path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(config_path.resolve())


def validate_pending_semantics(
    decisions: list[dict[str, Any]],
    rankings: list[dict[str, Any]],
    policy: dict[str, Any],
    query_ids: list[str],
) -> None:
    if len(decisions) != len(query_ids) or len(rankings) != len(query_ids):
        raise ValueError("Pending output row counts differ from the query boundary")
    if [str(row.get("query_id")) for row in decisions] != query_ids:
        raise ValueError("Pending decision query order differs")
    if [str(row.get("query_id")) for row in rankings] != query_ids:
        raise ValueError("Pending ranking query order differs")
    for row in decisions:
        if set(row) != DECISION_KEYS:
            raise ValueError(f"Pending decision schema differs: {row.get('query_id')}")
    for row in rankings:
        if set(row) != RANKING_KEYS:
            raise ValueError(f"Pending ranking schema differs: {row.get('query_id')}")
    if set(policy) != POLICY_KEYS:
        raise ValueError(f"Pending policy schema differs: {sorted(set(policy) ^ POLICY_KEYS)}")
    assert_no_prohibited_keys(decisions, "simplified_runner.decisions")
    assert_no_prohibited_keys(rankings, "simplified_runner.rankings")
    assert_no_prohibited_keys(policy, "simplified_runner.policy")


def run_simplified_controller(
    config_path: Path,
    *,
    repo_root: Path | None = None,
    synthetic_test_mode: bool = False,
    verify_git_binding: bool | None = None,
) -> dict[str, Any]:
    context = run_preflight(
        config_path,
        repo_root=repo_root,
        synthetic_test_mode=synthetic_test_mode,
        phase="runner",
        verify_git_binding=verify_git_binding,
    )
    config = context.config
    retrieval = _retrieval_config(config)
    rows = build_query_decisions(
        context.units,
        context.queries,
        context.unit_embeddings,
        context.query_embeddings,
        retrieval,
    )
    references = fit_ecdf_references(rows)
    score_rows(rows, references)
    allocation = allocate_budget(rows, retrieval.budget_fraction)
    decisions = [{key: row[key] for key in DECISION_KEYS} for row in rows]
    rankings = [
        {
            "query_id": row["query_id"],
            "dataset": row["dataset"],
            "sample_id": row["sample_id"],
            "trigger_u1": row["trigger_u1"],
            "planned_insert_count": row["planned_insert_count"],
            "dense_top20_unit_ids": row["dense_top20_unit_ids"],
            "q25_top20_unit_ids": row["q25_top20_unit_ids"],
            "q25_inserted_unit_ids": row["q25_inserted_unit_ids"],
            "final_top20_unit_ids": row["final_top20_unit_ids"],
            "final_inserted_unit_ids": row["final_inserted_unit_ids"],
        }
        for row in rows
    ]
    query_ids = [str(row["query_id"]) for row in context.queries]
    outputs = {
        key: resolve_path(context.repo_root, value)
        for key, value in config["outputs"].items()
    }
    targets = [outputs["decisions"], outputs["rankings"], outputs["policy"]]
    validate_pending_output_targets(targets)
    parents = {path.parent.resolve() for path in targets}
    if len(parents) != 1:
        raise ValueError("Simplified controller outputs must share one filesystem directory")
    output_parent = next(iter(parents))
    implementation_hashes = implementation_hash_map(config)
    legacy_protocol_sha = sha256_file(context.repo_root / PROTOCOL_RELATIVE_PATH)
    execution_head = git_head(context.repo_root)

    with tempfile.TemporaryDirectory(
        prefix="stage4b_u1_simplified_pending_", dir=output_parent
    ) as directory:
        pending_root = Path(directory)
        pending_decisions = pending_root / "decisions.jsonl"
        pending_rankings = pending_root / "rankings.jsonl"
        pending_policy = pending_root / "policy.json"
        write_jsonl_in_existing_directory(pending_decisions, decisions)
        write_jsonl_in_existing_directory(pending_rankings, rankings)
        policy = {
            "schema_version": SCHEMA_VERSION,
            "implementation_checkpoint": IMPLEMENTATION_CHECKPOINT,
            "execution_profile": EXECUTION_PROFILE,
            "protocol": PROTOCOL_RELATIVE_PATH,
            "protocol_sha256": legacy_protocol_sha,
            "simplified_execution_protocol": SIMPLIFIED_PROTOCOL_PATH,
            "simplified_execution_protocol_sha256": config["protocol"]["sha256"],
            "execution_config": _config_display_path(context.config_path, context.repo_root),
            "execution_config_sha256": context.config_sha256,
            "status": (
                "SYNTHETIC_TEST_ONLY"
                if synthetic_test_mode
                else "POLICY_FROZEN_BEFORE_EVALUATION"
            ),
            "run_role": "development",
            "git_commit_sha": execution_head,
            "code_commit_sha": config["implementation"]["code_commit"],
            "sample_id_sha256": id_digest(str(row["sample_id"]) for row in context.queries),
            "query_id_sha256": id_digest(query_ids),
            "queries": len(context.queries),
            "units": len(context.units),
            "model_name": config["retrieval"]["model_name"],
            "max_length": config["retrieval"]["max_length"],
            "batch_size": config["retrieval"]["batch_size"],
            "retrieval_config": retrieval.to_dict(),
            "ecdf_definition": (
                "(count_less + 0.5 * count_equal) / n using exact float64 equality"
            ),
            "ecdf_references": references,
            "allocation": allocation,
            "input_hashes": {
                "unlabeled_units": sha256_file(context.units_path),
                "unlabeled_queries": sha256_file(context.queries_path),
                "channel_audit": sha256_file(context.channel_audit_path),
                "embedding_cache": sha256_file(context.cache_path),
            },
            "output_hashes": {
                "decisions": sha256_file(pending_decisions),
                "rankings": sha256_file(pending_rankings),
            },
            "implementation_hashes": implementation_hashes,
            "controller_source_sha256": implementation_hashes[SIMPLIFIED_RUNNER_PATH],
            "parent_development_policy_sha256": None,
            "evaluation_labels_loaded": False,
        }
        validate_pending_semantics(decisions, rankings, policy, query_ids)
        write_json_in_existing_directory(pending_policy, policy)
        assert_cache_fingerprint_unchanged(
            context.cache_path,
            context.cache_fingerprint,
            "after simplified controller computation",
        )
        pairs = [
            (pending_decisions, outputs["decisions"]),
            (pending_rankings, outputs["rankings"]),
            (pending_policy, outputs["policy"]),
        ]
        try:
            promote_pending_outputs(pairs)
            assert_cache_fingerprint_unchanged(
                context.cache_path,
                context.cache_fingerprint,
                "after simplified output promotion",
            )
        except Exception:
            remove_outputs_created_by_this_run(targets)
            raise
    return policy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--synthetic-test-mode", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    policy = run_simplified_controller(
        args.config,
        synthetic_test_mode=args.synthetic_test_mode,
    )
    print(
        "STAGE4B_U1_SIMPLIFIED_CONTROLLER_PASS "
        f"queries={policy['queries']} selected={policy['allocation']['selected_queries']}"
    )


if __name__ == "__main__":
    main()
