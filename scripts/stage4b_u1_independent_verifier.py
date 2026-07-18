"""Independent pre-Gold verifier for the simplified Stage4B-U1-D route."""

from __future__ import annotations

import argparse
import json
import subprocess
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
from stage4b_u1_goldfree_retrieval import RetrievalConfig
from stage4b_u1_goldfree_controller import write_json_in_existing_directory
from stage4b_u1_simplified_preflight import (
    EXECUTION_PROFILE,
    SIMPLIFIED_PROTOCOL_PATH,
    SIMPLIFIED_RUNNER_PATH,
    SIMPLIFIED_VERIFIER_PATH,
    implementation_hash_map,
    resolve_path,
    run_preflight,
)
from stage4b_u1_verify import (
    validate_candidate_pools,
    verify_policy_and_rankings,
    verify_static_controller_boundary,
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
CHECK_KEYS = {
    "identity",
    "input_schema",
    "output_schema",
    "numeric_finiteness",
    "ecdf_and_score",
    "allocation_and_trigger",
    "effective_k",
    "ranking_membership",
    "protected_prefix_and_inserts",
    "final_selector",
    "ranking_query_set",
    "committed_artifact_set",
    "gold_isolation",
}


def _reject_constant(value: str) -> None:
    raise ValueError(f"Non-finite JSON constant is forbidden: {value}")


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_strict_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(
            stream,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def load_strict_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                raise ValueError(f"Blank JSONL line is forbidden: {path}:{line_number}")
            value = json.loads(
                line,
                object_pairs_hook=_strict_object,
                parse_constant=_reject_constant,
            )
            if not isinstance(value, dict):
                raise ValueError(f"Expected JSON object: {path}:{line_number}")
            rows.append(value)
    return rows


def _config_display_path(config_path: Path, repo_root: Path) -> str:
    try:
        return config_path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(config_path.resolve())


def _assert_policy_bindings(
    policy: dict[str, Any],
    *,
    context: Any,
    decisions_path: Path,
    rankings_path: Path,
    synthetic_test_mode: bool,
) -> None:
    if set(policy) != POLICY_KEYS:
        raise ValueError(f"Policy schema differs: {sorted(set(policy) ^ POLICY_KEYS)}")
    expected_status = "SYNTHETIC_TEST_ONLY" if synthetic_test_mode else "POLICY_FROZEN_BEFORE_EVALUATION"
    expected_scalars = {
        "schema_version": SCHEMA_VERSION,
        "implementation_checkpoint": IMPLEMENTATION_CHECKPOINT,
        "execution_profile": EXECUTION_PROFILE,
        "protocol": PROTOCOL_RELATIVE_PATH,
        "protocol_sha256": sha256_file(context.repo_root / PROTOCOL_RELATIVE_PATH),
        "simplified_execution_protocol": SIMPLIFIED_PROTOCOL_PATH,
        "simplified_execution_protocol_sha256": context.config["protocol"]["sha256"],
        "execution_config": _config_display_path(context.config_path, context.repo_root),
        "execution_config_sha256": context.config_sha256,
        "status": expected_status,
        "run_role": "development",
        "code_commit_sha": context.config["implementation"]["code_commit"],
        "queries": len(context.queries),
        "units": len(context.units),
        "model_name": context.config["retrieval"]["model_name"],
        "max_length": context.config["retrieval"]["max_length"],
        "batch_size": context.config["retrieval"]["batch_size"],
        "parent_development_policy_sha256": None,
        "evaluation_labels_loaded": False,
    }
    for key, expected in expected_scalars.items():
        if policy.get(key) != expected:
            raise ValueError(f"Policy binding differs at {key}")
    query_ids = [str(row["query_id"]) for row in context.queries]
    if policy["sample_id_sha256"] != id_digest(str(row["sample_id"]) for row in context.queries):
        raise ValueError("Policy sample-ID digest differs")
    if policy["query_id_sha256"] != id_digest(query_ids):
        raise ValueError("Policy query-ID digest differs")
    if policy["retrieval_config"] != RetrievalConfig().to_dict():
        raise ValueError("Policy retrieval semantics differ")
    expected_inputs = {
        "unlabeled_units": sha256_file(context.units_path),
        "unlabeled_queries": sha256_file(context.queries_path),
        "channel_audit": sha256_file(context.channel_audit_path),
        "embedding_cache": sha256_file(context.cache_path),
    }
    if policy["input_hashes"] != expected_inputs:
        raise ValueError("Policy input hashes differ")
    if policy["output_hashes"] != {
        "decisions": sha256_file(decisions_path),
        "rankings": sha256_file(rankings_path),
    }:
        raise ValueError("Policy output hashes differ")
    hashes = implementation_hash_map(context.config)
    if policy["implementation_hashes"] != hashes:
        raise ValueError("Policy implementation hashes differ")
    if policy["controller_source_sha256"] != hashes[SIMPLIFIED_RUNNER_PATH]:
        raise ValueError("Policy simplified-runner source hash differs")
    assert_no_prohibited_keys(policy, "simplified_verifier.policy")


def _assert_row_contracts(
    decisions: list[dict[str, Any]],
    rankings: list[dict[str, Any]],
    query_ids: list[str],
) -> None:
    if [str(row.get("query_id")) for row in decisions] != query_ids:
        raise ValueError("Decision query order differs")
    if [str(row.get("query_id")) for row in rankings] != query_ids:
        raise ValueError("Ranking query order differs")
    for row in decisions:
        if set(row) != DECISION_KEYS:
            raise ValueError(f"Decision schema differs: {row.get('query_id')}")
    for row in rankings:
        if set(row) != RANKING_KEYS:
            raise ValueError(f"Ranking schema differs: {row.get('query_id')}")
    assert_no_prohibited_keys(decisions, "simplified_verifier.decisions")
    assert_no_prohibited_keys(rankings, "simplified_verifier.rankings")


def _git_output_commit_gate(
    repo_root: Path,
    paths: list[Path],
    *,
    policy_execution_commit: str,
) -> str:
    head = git_head(repo_root)
    relative: list[str] = []
    for path in paths:
        try:
            relative.append(path.resolve().relative_to(repo_root.resolve()).as_posix())
        except ValueError as error:
            raise ValueError(f"Formal artifact is outside the repository: {path}") from error
    changed = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    if set(changed) != set(relative) or len(changed) != len(relative):
        raise ValueError("Artifact commit must contain exactly decisions/rankings/policy")
    for relative_path, path in zip(relative, paths, strict=True):
        if subprocess.run(
            ["git", "cat-file", "-e", f"HEAD:{relative_path}"], cwd=repo_root
        ).returncode != 0:
            raise ValueError(f"Artifact is not tracked at HEAD: {relative_path}")
        if subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", relative_path], cwd=repo_root
        ).returncode != 0:
            raise ValueError(f"Artifact differs from HEAD: {relative_path}")
        payload = subprocess.run(
            ["git", "show", f"HEAD:{relative_path}"],
            cwd=repo_root,
            check=True,
            capture_output=True,
        ).stdout
        import hashlib

        if hashlib.sha256(payload).hexdigest().upper() != sha256_file(path):
            raise ValueError(f"Artifact Git blob hash differs: {relative_path}")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", policy_execution_commit, head],
        cwd=repo_root,
    ).returncode != 0:
        raise ValueError("Policy execution commit is not an ancestor of artifact HEAD")
    return head


def run_independent_verifier(
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
        phase="verifier",
        verify_git_binding=verify_git_binding,
    )
    decisions_path = resolve_path(context.repo_root, context.config["outputs"]["decisions"])
    rankings_path = resolve_path(context.repo_root, context.config["outputs"]["rankings"])
    policy_path = resolve_path(context.repo_root, context.config["outputs"]["policy"])
    output_path = resolve_path(context.repo_root, context.config["verification"]["output"])
    decisions = load_strict_jsonl(decisions_path)
    rankings = load_strict_jsonl(rankings_path)
    policy = load_strict_json(policy_path)
    query_ids = [str(row["query_id"]) for row in context.queries]
    _assert_row_contracts(decisions, rankings, query_ids)
    _assert_policy_bindings(
        policy,
        context=context,
        decisions_path=decisions_path,
        rankings_path=rankings_path,
        synthetic_test_mode=synthetic_test_mode,
    )
    candidate_ids = validate_candidate_pools(context.units, context.queries)
    policy_and_ranking = verify_policy_and_rankings(
        decisions,
        rankings,
        policy,
        candidate_ids,
    )
    runner_path = context.repo_root / SIMPLIFIED_RUNNER_PATH
    static_boundary = verify_static_controller_boundary(runner_path)
    static_boundary["execution_config_gold_field_scan"] = True
    if synthetic_test_mode:
        frozen_commit = git_head(context.repo_root)
    else:
        frozen_commit = _git_output_commit_gate(
            context.repo_root,
            [decisions_path, rankings_path, policy_path],
            policy_execution_commit=str(policy["git_commit_sha"]),
        )
    checks = {key: "PASS" for key in CHECK_KEYS}
    implementation_hashes = implementation_hash_map(context.config)
    result = {
        "schema_version": SCHEMA_VERSION,
        "implementation_checkpoint": IMPLEMENTATION_CHECKPOINT,
        "execution_profile": EXECUTION_PROFILE,
        "status": "VERIFIED_PRE_GOLD",
        "synthetic_test_mode": synthetic_test_mode,
        "frozen_commit_sha": frozen_commit,
        "simplified_execution_protocol": SIMPLIFIED_PROTOCOL_PATH,
        "simplified_execution_protocol_sha256": context.config["protocol"]["sha256"],
        "execution_config": _config_display_path(context.config_path, context.repo_root),
        "execution_config_sha256": context.config_sha256,
        "code_commit_sha": context.config["implementation"]["code_commit"],
        "independent_verifier_source": SIMPLIFIED_VERIFIER_PATH,
        "independent_verifier_source_sha256": implementation_hashes[SIMPLIFIED_VERIFIER_PATH],
        "static_controller_boundary": static_boundary,
        "implementation_hashes": implementation_hashes,
        "identity_boundary": {
            "queries": len(context.queries),
            "units": len(context.units),
            "sample_id_sha256": id_digest(str(row["sample_id"]) for row in context.queries),
            "query_id_sha256": id_digest(query_ids),
            "namespace_relation_check": True,
        },
        "policy_and_ranking": policy_and_ranking,
        "checks": checks,
        "gold_inputs_loaded": False,
        "evaluation": None,
        "artifact_hashes": {
            "channel_audit": sha256_file(context.channel_audit_path),
            "decisions": sha256_file(decisions_path),
            "rankings": sha256_file(rankings_path),
            "policy": sha256_file(policy_path),
        },
    }
    if output_path.exists() or not output_path.parent.is_dir():
        raise ValueError("Verified-pre-Gold target must be absent with an existing parent")
    write_json_in_existing_directory(output_path, result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--synthetic-test-mode", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_independent_verifier(
        args.config,
        synthetic_test_mode=args.synthetic_test_mode,
    )
    print(
        "STAGE4B_U1_SIMPLIFIED_VERIFIER_PASS "
        f"queries={result['identity_boundary']['queries']} status={result['status']}"
    )


if __name__ == "__main__":
    main()
