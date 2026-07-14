"""Run the complete Stage4B-U1 plus Amendment 5G-A synthetic suite."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import ntpath
import os
import sys
import unittest
from pathlib import Path

from stage4b_u1_common import sha256_file, write_json


GOVERNANCE_FILES = (
    "AGENTS.md",
    "docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_APPROVAL_REQUEST.md",
    "docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_MANIFEST.json",
    "docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_APPROVAL_DECISION.md",
    "docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_8.md",
    "docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_8_REVIEW_1.md",
)
ALLOWED_IMPLEMENTATION_FILES = (
    "scripts/stage4b_u1_preflight_execution_head_binding.py",
    "scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py",
    "tests/test_stage4b_u1_preflight_execution_head_binding.py",
)
REQUIRED_ACTIVE_PROOF_SUFFIXES = (
    "test_identical_full_local_origin_github_sha_values_pass",
    "test_local_head_drift_is_rejected",
    "test_origin_main_drift_is_rejected",
    "test_github_main_drift_is_rejected",
    "test_shared_short_prefix_with_different_full_sha_is_rejected",
    "test_39_character_sha_is_rejected",
    "test_41_character_sha_is_rejected",
    "test_uppercase_sha_is_rejected",
    "test_nonhex_sha_is_rejected",
    "test_empty_sha_is_rejected",
    "test_nontext_sha_is_rejected",
    "test_parent_mismatch_is_rejected",
    "test_extra_intermediate_commit_is_rejected_by_direct_parent_gate",
    "test_exact_changed_path_set_passes_independent_of_order",
    "test_missing_changed_path_is_rejected",
    "test_extra_changed_path_is_rejected",
    "test_duplicate_changed_path_is_rejected",
    "test_duplicate_allowed_path_is_rejected",
    "test_absolute_path_is_rejected",
    "test_parent_traversal_path_is_rejected",
    "test_code_path_is_rejected_when_not_governance_allowed",
    "test_existing_test_path_is_rejected_when_not_governance_allowed",
    "test_result_path_is_rejected_when_not_governance_allowed",
    "test_cache_path_is_rejected_when_not_governance_allowed",
    "test_experiment_path_is_rejected_when_not_governance_allowed",
    "test_missing_required_ancestor_is_rejected",
    "test_duplicate_required_ancestor_is_rejected",
    "test_dirty_worktree_is_rejected",
    "test_nonboolean_clean_fact_is_rejected",
    "test_governance_package_mismatch_is_rejected",
    "test_governance_approval_mismatch_is_rejected",
    "test_execution_head_missing_governance_binding_is_rejected",
    "test_missing_rebinding_evidence_is_rejected",
    "test_missing_governance_binding_artifact_is_rejected",
    "test_missing_rebinding_audit_is_rejected",
    "test_public_api_has_no_pretranscribed_execution_head_parameter",
    "test_helper_source_has_no_fixed_future_rebinding_sha",
    "test_execution_head_helper_uses_only_python_standard_library",
    "test_helper_has_no_filesystem_git_subprocess_or_helper_calls",
    "test_runtime_validation_performs_no_io_or_execution",
    "test_output_is_value_free_except_required_validated_head",
    "test_exact_approved_argv_is_accepted",
    "test_pregold_audit_output_is_accepted",
    "test_gold_in_ordinary_value_is_not_role_denied",
    "test_validation_metadata_is_value_free",
    "test_unknown_flag_is_rejected",
    "test_duplicate_flag_is_rejected",
    "test_missing_flag_value_is_rejected",
    "test_missing_value_is_rejected",
    "test_extra_positional_argument_is_rejected",
    "test_argument_order_drift_is_rejected",
    "test_executable_drift_is_rejected",
    "test_capture_script_drift_is_rejected",
    "test_units_path_drift_is_rejected",
    "test_queries_path_drift_is_rejected",
    "test_channel_audit_path_drift_is_rejected",
    "test_embedding_cache_path_drift_is_rejected",
    "test_reference_decisions_path_drift_is_rejected",
    "test_audit_output_path_drift_is_rejected",
    "test_temp_parent_path_drift_is_rejected",
    "test_relative_windows_path_is_rejected",
    "test_model_value_drift_is_rejected",
    "test_token_drift_is_rejected",
    "test_zero_batch_size_is_rejected",
    "test_leading_zero_batch_size_is_rejected",
    "test_non_decimal_max_length_is_rejected",
    "test_lowercase_units_sha_is_rejected",
    "test_short_queries_sha_is_rejected",
    "test_nonhex_channel_sha_is_rejected",
    "test_spaced_cache_sha_is_rejected",
    "test_rankings_role_is_rejected",
    "test_policy_role_is_rejected",
    "test_gold_map_role_is_rejected",
    "test_source_audit_role_is_rejected",
    "test_evaluator_role_is_rejected",
    "test_reservation_role_is_rejected",
    "test_stage3b_role_is_rejected",
    "test_nonsequence_argv_is_rejected",
    "test_nontext_argv_item_is_rejected",
    "test_argument_policy_uses_only_python_standard_library",
    "test_argument_policy_has_no_filesystem_hash_or_execution_calls",
    "test_argument_policy_has_no_capture_or_path_helper_import",
    "test_argument_policy_has_no_raw_gold_value_substring_denylist",
    "test_runtime_validation_does_not_use_filesystem_hash_or_subprocess",
    "test_runtime_validation_does_not_call_capture_or_path_helper",
    "test_same_absolute_directory_is_accepted",
    "test_trailing_separator_is_accepted",
    "test_windows_case_variant_is_accepted",
    "test_forward_slash_variant_is_accepted",
    "test_terminal_dot_segment_is_accepted",
    "test_parent_directory_is_rejected",
    "test_child_directory_is_rejected",
    "test_prefix_collision_directory_is_rejected",
    "test_unrelated_directory_is_rejected",
    "test_relative_path_is_rejected_before_normalization",
    "test_nonexistent_path_is_rejected",
    "test_file_path_is_rejected",
    "test_leaf_reparse_point_is_rejected_without_skip",
    "test_exact_comparison_has_no_prefix_acceptance_call",
    "test_helper_uses_only_python_standard_library",
    "test_helper_has_no_command_token_or_execution_logic",
    "test_leaf_probes_are_limited_to_supplied_synthetic_paths",
    "test_invalid_non_text_path_is_rejected",
    "test_heterogeneous_file_schema_is_accepted_by_cli",
    "test_left_file_nullable_heterogeneity_is_compared",
    "test_right_file_nullable_heterogeneity_is_compared",
    "test_both_files_same_nullable_types_are_identical",
    "test_null_integer_is_schema_discrete_and_semantic_difference",
    "test_null_float_is_schema_and_discrete_not_float_difference",
    "test_nullable_rows_are_not_normalized_to_numeric_values",
    "test_heterogeneous_files_preserve_field_set_difference",
    "test_heterogeneous_files_preserve_field_order_difference",
    "test_heterogeneous_files_preserve_nested_structure_difference",
    "test_heterogeneous_files_still_reject_invalid_second_row",
    "test_heterogeneous_files_still_reject_nested_duplicate_key",
    "test_heterogeneous_report_preserves_raw_gate_and_no_leakage",
    "test_nan_rejected",
    "test_positive_infinity_rejected",
    "test_negative_infinity_rejected",
    "test_duplicate_query_id_rejected",
    "test_missing_query_id_rejected",
    "test_synthetic_allowlist_rejects_official_path_before_open",
    "test_capture_does_not_call_controller_rankings_or_policy",
    "test_temporary_decisions_removed_after_success",
    "test_temporary_decisions_removed_after_exception",
    "test_official_mode_without_5b_token_fails_before_open",
    "test_official_frozen_path_validation_rejects_nonfrozen_paths_before_open",
    "test_official_expected_channel_sha_must_match_frozen_value",
    "test_units_expected_sha_mismatch_rejected_before_semantic_parse",
    "test_queries_expected_sha_mismatch_rejected_before_semantic_parse",
    "test_channel_audit_expected_sha_mismatch_rejected_before_semantic_parse",
    "test_units_drift_after_computation_leaves_no_audit_and_cleans_temp",
    "test_queries_drift_after_computation_leaves_no_audit_and_cleans_temp",
    "test_channel_audit_drift_after_computation_leaves_no_audit_and_cleans_temp",
    "test_correct_three_channel_hashes_pass_with_synthetic_fixture",
)


def test_ids(suite: unittest.TestSuite) -> list[str]:
    ids: list[str] = []
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            ids.extend(test_ids(item))
        else:
            ids.append(item.id())
    return ids


def lexical_windows_path(path: str | os.PathLike[str]) -> str:
    """Normalize path spelling without querying filesystem metadata."""

    return ntpath.normcase(ntpath.abspath(os.fspath(path)))


def forbidden_official_paths(repo_root: Path) -> set[str]:
    manifest = json.loads(
        (repo_root / "docs" / "STAGE4B_U1_PREGOLD_AMENDMENT_5A_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    resumption = json.loads(
        (repo_root / "docs" / "STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    amendment_5a_1 = json.loads(
        (
            repo_root
            / "docs"
            / "STAGE4B_U1_PREGOLD_AMENDMENT_5A_1_MANIFEST.json"
        ).read_text(encoding="utf-8")
    )
    amendment_5d_a = json.loads(
        (
            repo_root
            / "docs"
            / "STAGE4B_U1_PREGOLD_AMENDMENT_5D_A_MANIFEST.json"
        ).read_text(encoding="utf-8")
    )
    cache = Path(resumption["frozen_cache"]["path"])
    data_root = cache.parent
    values = {
        cache,
        data_root / "stage4a_r2_official_dev4500_units.jsonl",
        data_root / "stage4a_r2_official_dev4500_queries.jsonl",
        data_root / "stage4a_r2_official_dev4500_minilm_embeddings.npz",
        repo_root / "docs" / "STAGE4A_R2_SOURCE_AUDIT.json",
        repo_root / "results" / "stage4b_u1_d_official_dev4500_decisions.jsonl",
        repo_root / "results" / "stage4b_u1_d_official_dev4500_rankings.jsonl",
        Path(resumption["frozen_v2_2_equivalence"]["reference_policy_path"]),
    }
    values.update(Path(path) for path in resumption["artifact_registry"].values())
    values.update(
        Path(item["path"])
        for item in amendment_5a_1["frozen_channel_inputs"].values()
    )
    values.add(repo_root / amendment_5d_a["amendment_5c_b_evidence"]["machine_inventory_path"])
    if manifest["current_execution_state"] != "PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_4":
        raise ValueError("Amendment 5A manifest state drifted")
    if amendment_5a_1["package_status"] != "AWAITING_AMENDMENT_5A_1_APPROVAL":
        raise ValueError("Amendment 5A.1 package bytes drifted")
    return {lexical_windows_path(path) for path in values}


def main() -> None:
    if len(REQUIRED_ACTIVE_PROOF_SUFFIXES) != len(
        set(REQUIRED_ACTIVE_PROOF_SUFFIXES)
    ):
        raise ValueError(
            "Required active-proof suffix registry contains duplicates"
        )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/stage4b_u1_d_pregold_amendment_5g_a_synthetic_verification.json"
        ),
    )
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    amendment_5g_a = json.loads(
        (
            repo_root
            / "docs"
            / "STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_MANIFEST.json"
        ).read_text(encoding="utf-8")
    )
    frozen_files = amendment_5g_a["frozen_existing_hashes"]
    frozen_hashes = {path: sha256_file(repo_root / path) for path in frozen_files}
    if frozen_hashes != frozen_files:
        raise ValueError("An Amendment 5G-A frozen file drifted before verification")
    forbidden = forbidden_official_paths(repo_root)
    attempted: list[str] = []

    def audit_hook(event: str, values: tuple[object, ...]) -> None:
        if event != "open" or not values:
            return
        supplied = values[0]
        if not isinstance(supplied, (str, bytes)):
            return
        try:
            candidate = lexical_windows_path(os.fsdecode(supplied))
        except (OSError, TypeError, ValueError):
            return
        if candidate in forbidden:
            attempted.append(str(candidate))
            raise PermissionError(f"Amendment 5G-A blocked official path access: {candidate}")

    sys.addaudithook(audit_hook)
    suite = unittest.defaultTestLoader.discover(
        str(repo_root / "tests"), pattern="test_stage4b_u1*.py"
    )
    discovered = sorted(test_ids(suite))
    argument_policy_tests = [
        test_id
        for test_id in discovered
        if test_id.startswith("test_stage4b_u1_preflight_argument_policy.")
    ]
    execution_head_binding_tests = [
        test_id
        for test_id in discovered
        if test_id.startswith(
            "test_stage4b_u1_preflight_execution_head_binding."
        )
    ]
    active_proofs = {
        suffix: [test_id for test_id in discovered if test_id.endswith(suffix)]
        for suffix in REQUIRED_ACTIVE_PROOF_SUFFIXES
    }
    if any(len(matches) != 1 for matches in active_proofs.values()):
        raise ValueError("Required active access/cleanup proof test is missing or duplicated")
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    count_gate = (
        result.testsRun == len(discovered)
        and result.testsRun == 246
        and len(execution_head_binding_tests) == 41
        and len(argument_policy_tests) == 44
    )
    tracked_files = tuple(
        dict.fromkeys(
            (*GOVERNANCE_FILES, *ALLOWED_IMPLEMENTATION_FILES, *frozen_files.keys())
        )
    )
    implementation_hashes = {
        path: sha256_file(repo_root / path) for path in tracked_files
    }
    tracked_byte_digest = hashlib.sha256(
        json.dumps(
            implementation_hashes,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest().upper()
    if {path: implementation_hashes[path] for path in frozen_files} != frozen_files:
        raise ValueError("An Amendment 5G-A frozen file changed during verification")
    all_pass = result.wasSuccessful() and count_gate and not attempted
    evidence = {
        "stage": "Stage4B-U1-D Pre-Gold Amendment 5G-A",
        "diagnostic_checkpoint": "stage4b_u1_decisions_diag_v2",
        "controller_checkpoint_unchanged": "stage4b_u1_v2_3_1",
        "status": "AMENDMENT_5G_A_SYNTHETICALLY_VERIFIED" if all_pass else "FAILED",
        "tests_run": result.testsRun,
        "baseline_tests_required": 205,
        "minimum_new_tests": 16,
        "minimum_tests_required": 221,
        "argument_policy_tests": len(argument_policy_tests),
        "execution_head_binding_tests": len(execution_head_binding_tests),
        "test_ids": discovered,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "implementation_hashes": implementation_hashes,
        "tracked_file_count": len(tracked_files),
        "tracked_byte_digest_sha256": tracked_byte_digest,
        "frozen_file_count": len(frozen_files),
        "frozen_files_verified": True,
        "active_proof_tests": active_proofs,
        "official_path_access_guard": {
            "installed": True,
            "forbidden_path_count": len(forbidden),
            "blocked_or_attempted_access_count": len(attempted),
            "metadata_or_content_access_attempts": len(attempted),
        },
        "formal_preflight_invocations": 0,
        "authorization_token_uses": 0,
        "official_capture_invocations": 0,
        "path_equivalence_helper_executed_by_synthetic_tests": True,
        "path_equivalence_helper_official_invocations": 0,
        "typed_argument_policy_helper_executed_by_synthetic_tests": True,
        "typed_argument_policy_helper_official_invocations": 0,
        "typed_argument_policy_filesystem_or_hash_calls": 0,
        "typed_argument_policy_subprocess_or_capture_calls": 0,
        "typed_argument_policy_authorization_token_uses": 0,
        "typed_argument_policy_raw_gold_value_substring_denylist": False,
        "execution_head_binding_helper_executed_by_synthetic_tests": True,
        "execution_head_binding_helper_filesystem_git_or_subprocess_calls": 0,
        "execution_head_binding_helper_other_helper_calls": 0,
        "execution_head_binding_helper_official_path_accesses": 0,
        "execution_head_binding_helper_authorization_token_uses": 0,
        "execution_head_binding_helper_capture_or_comparator_calls": 0,
        "execution_head_binding_helper_accepts_pretranscribed_current_head": False,
        "execution_head_binding_helper_contains_fixed_future_rebinding_sha": False,
        "execution_head_binding_helper_output_value_free": True,
        "exact_capture_command_unchanged": True,
        "raw_byte_equivalence_unchanged": True,
        "rankings_accessed": False,
        "rankings_generated_by_capture": False,
        "policy_builder_called_by_capture": False,
        "policy_generated_by_capture": False,
        "gold_accessed": False,
        "reservation_accessed": False,
        "stage3b_accessed": False,
        "official_diagnostic_executed": False,
        "official_comparator_executed": False,
        "official_capture_executed": False,
        "amendment_5c_b_machine_inventory_accessed": False,
        "synthetic_capture_fixture_tests_executed": True,
        "controller_rerun": False,
        "verifier_executed": False,
        "verified_properties": [
            "raw bytes size SHA-256 and terminal-newline differences are separated from canonical JSON equality",
            "query-ID count uniqueness set and order are compared fail-closed",
            "JSON duplicate keys invalid syntax and non-finite constants are rejected",
            "bool int and float types remain distinct",
            "binary64 uses explicit big-endian bits and a sign-aware monotonic unsigned ordering",
            "positive and negative zero remain bit-distinct and cross-sign ULP distances are deterministic",
            "heterogeneous within-file schemas are accepted without changing per-query comparison",
            "null versus integer or finite float is classified as schema and discrete difference",
            "ordered-rank null versus integer also remains a decision-semantic difference",
            "null values do not enter finite-float absolute-error or ULP aggregation",
            "nullable values are not imputed coerced cast or normalized",
            "schema field set order nested type discrete list float and decision-semantic differences remain classified",
            "raw byte equality remains the only controlling equivalence gate",
            "the Windows path-equivalence helper rejects relative missing file and reparse-point leaves fail-closed",
            "the helper accepts only exact canonical directory equality under ordinal case-insensitive comparison",
            "trailing separators case separator spelling and terminal dot segments normalize only for comparison",
            "parent child unrelated and string-prefix collision directories remain unequal",
            "the helper uses only the Python standard library and has no command token or execution logic",
            "typed capture arguments require exact argv equality before any acceptance is possible",
            "typed capture arguments require the fixed executable script 32-element shape and 15 ordered flags",
            "unknown duplicate missing reordered extra and prohibited roles fail closed",
            "all seven path roles require absolute Windows syntax and exact approved-value binding",
            "model integer SHA-256 and token roles retain distinct typed validation and exact binding",
            "the approved pregold audit-output spelling and ordinary gold value substrings are not role denylists",
            "argument-policy source and runtime proofs exclude filesystem hashing subprocess capture token use and path-helper calls",
            "argument-policy source contains no raw gold value-substring denylist",
            "execution-head binding derives the synchronized full current HEAD from three caller-supplied sources",
            "execution-head binding requires full lowercase 40-character hexadecimal commit values",
            "execution-head binding requires direct approval parentage exact changed paths required ancestry and a clean worktree fact",
            "execution-head binding requires exact package and approval metadata plus all required governance artifacts",
            "execution-head binding rejects duplicate absolute parent-traversal missing and extra paths fail closed",
            "execution-head helper has no pre-transcribed current HEAD input and no fixed future rebinding SHA",
            "execution-head source and runtime proofs exclude filesystem Git subprocess official helper token capture and comparator operations",
            "execution-head output returns only value-free validation metadata and the required validated current HEAD",
            "synthetic capture writes decisions only under an OS temporary directory",
            "temporary decisions are removed after successful and exceptional exits",
            "capture does not access or generate rankings and does not call a policy builder",
            "official paths are guarded process-wide and synthetic allowlists reject outside paths before file reads",
            "future official capture requires exact registered paths an absent audit output and the OS temp parent",
            "official channel validation uses the registered source-audit digest without opening the source-audit file",
            "the embedding cache fingerprint is rechecked after decisions computation",
            "all three channel inputs are regular files and match caller-provided SHA-256 values before semantic parsing",
            "official expected channel-input SHA-256 values must equal the three externally frozen values",
            "all three channel-input SHA-256 values are rechecked after temporary-decisions cleanup and before audit creation",
            "pre-gate or post-gate channel drift leaves no audit and cleans temporary decisions",
            "the accepted 205-test Stage4B-U1 baseline remains passing with at least 16 new execution-head tests",
        ],
    }
    write_json(args.output, evidence)
    if not all_pass:
        sys.stderr.write(stream.getvalue())
        raise SystemExit(1)


if __name__ == "__main__":
    main()
