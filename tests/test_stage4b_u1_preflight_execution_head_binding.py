from __future__ import annotations

import ast
import builtins
import inspect
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import stage4b_u1_preflight_execution_head_binding as head_binding  # noqa: E402
from stage4b_u1_preflight_execution_head_binding import (  # noqa: E402
    ExecutionHeadBindingError,
    validate_execution_head_binding,
)


class Stage4BU1PreflightExecutionHeadBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.head = "a" * 40
        self.approval = "b" * 40
        self.package = "c" * 40
        self.history = "d" * 40
        self.allowed_paths = [
            "AGENTS.md",
            "docs/synthetic_approval_decision.md",
            "docs/synthetic_rebinding_audit.md",
        ]
        self.arguments: dict[str, object] = {
            "local_head": self.head,
            "origin_main": self.head,
            "github_main": self.head,
            "head_parent": self.approval,
            "approval_governance_commit": self.approval,
            "changed_paths": list(self.allowed_paths),
            "allowed_rebinding_paths": list(self.allowed_paths),
            "required_ancestor_commits": [self.package, self.approval, self.history],
            "observed_ancestor_commits": [
                self.head,
                self.package,
                self.approval,
                self.history,
            ],
            "worktree_clean": True,
            "governance_binding": {
                "package_commit": self.package,
                "approval_commit": self.approval,
                "artifacts_present": {
                    "rebinding_evidence": True,
                    "governance_binding": True,
                    "rebinding_audit": True,
                },
            },
            "expected_package_commit": self.package,
            "expected_approval_commit": self.approval,
        }

    def validate(self, **overrides: object) -> dict[str, object]:
        arguments = dict(self.arguments)
        arguments.update(overrides)
        return validate_execution_head_binding(**arguments)

    def assert_rejected(self, **overrides: object) -> None:
        with self.assertRaises(ExecutionHeadBindingError):
            self.validate(**overrides)

    def test_identical_full_local_origin_github_sha_values_pass(self) -> None:
        result = self.validate()
        self.assertEqual(result["validated_execution_head"], self.head)
        self.assertTrue(result["head_sources_equal"])

    def test_local_head_drift_is_rejected(self) -> None:
        self.assert_rejected(local_head="e" * 40)

    def test_origin_main_drift_is_rejected(self) -> None:
        self.assert_rejected(origin_main="e" * 40)

    def test_github_main_drift_is_rejected(self) -> None:
        self.assert_rejected(github_main="e" * 40)

    def test_shared_short_prefix_with_different_full_sha_is_rejected(self) -> None:
        self.assert_rejected(github_main=("a" * 39) + "b")

    def test_39_character_sha_is_rejected(self) -> None:
        self.assert_rejected(local_head="a" * 39)

    def test_41_character_sha_is_rejected(self) -> None:
        self.assert_rejected(local_head="a" * 41)

    def test_uppercase_sha_is_rejected(self) -> None:
        self.assert_rejected(local_head="A" * 40)

    def test_nonhex_sha_is_rejected(self) -> None:
        self.assert_rejected(local_head="g" * 40)

    def test_empty_sha_is_rejected(self) -> None:
        self.assert_rejected(local_head="")

    def test_nontext_sha_is_rejected(self) -> None:
        self.assert_rejected(local_head=123)

    def test_parent_mismatch_is_rejected(self) -> None:
        self.assert_rejected(head_parent="e" * 40)

    def test_extra_intermediate_commit_is_rejected_by_direct_parent_gate(self) -> None:
        self.assert_rejected(head_parent="f" * 40)

    def test_exact_changed_path_set_passes_independent_of_order(self) -> None:
        result = self.validate(changed_paths=list(reversed(self.allowed_paths)))
        self.assertTrue(result["changed_path_set_verified"])
        self.assertEqual(result["changed_path_count"], len(self.allowed_paths))

    def test_missing_changed_path_is_rejected(self) -> None:
        self.assert_rejected(changed_paths=self.allowed_paths[:-1])

    def test_extra_changed_path_is_rejected(self) -> None:
        self.assert_rejected(changed_paths=[*self.allowed_paths, "docs/extra.md"])

    def test_duplicate_changed_path_is_rejected(self) -> None:
        self.assert_rejected(changed_paths=[*self.allowed_paths, self.allowed_paths[0]])

    def test_duplicate_allowed_path_is_rejected(self) -> None:
        self.assert_rejected(
            allowed_rebinding_paths=[*self.allowed_paths, self.allowed_paths[0]]
        )

    def test_absolute_path_is_rejected(self) -> None:
        path = "C:\\synthetic\\approval.md"
        self.assert_rejected(changed_paths=[*self.allowed_paths, path])

    def test_parent_traversal_path_is_rejected(self) -> None:
        self.assert_rejected(changed_paths=[*self.allowed_paths, "docs/../scripts/x.py"])

    def test_code_path_is_rejected_when_not_governance_allowed(self) -> None:
        self.assert_rejected(changed_paths=[*self.allowed_paths, "scripts/code.py"])

    def test_existing_test_path_is_rejected_when_not_governance_allowed(self) -> None:
        self.assert_rejected(changed_paths=[*self.allowed_paths, "tests/test_existing.py"])

    def test_result_path_is_rejected_when_not_governance_allowed(self) -> None:
        self.assert_rejected(changed_paths=[*self.allowed_paths, "results/output.json"])

    def test_cache_path_is_rejected_when_not_governance_allowed(self) -> None:
        self.assert_rejected(changed_paths=[*self.allowed_paths, "cache/embed.npz"])

    def test_experiment_path_is_rejected_when_not_governance_allowed(self) -> None:
        self.assert_rejected(changed_paths=[*self.allowed_paths, "experiments/run.json"])

    def test_missing_required_ancestor_is_rejected(self) -> None:
        self.assert_rejected(observed_ancestor_commits=[self.package, self.approval])

    def test_duplicate_required_ancestor_is_rejected(self) -> None:
        self.assert_rejected(
            required_ancestor_commits=[self.package, self.approval, self.package]
        )

    def test_dirty_worktree_is_rejected(self) -> None:
        self.assert_rejected(worktree_clean=False)

    def test_nonboolean_clean_fact_is_rejected(self) -> None:
        self.assert_rejected(worktree_clean=1)

    def test_governance_package_mismatch_is_rejected(self) -> None:
        binding = dict(self.arguments["governance_binding"])
        binding["package_commit"] = "e" * 40
        self.assert_rejected(governance_binding=binding)

    def test_governance_approval_mismatch_is_rejected(self) -> None:
        binding = dict(self.arguments["governance_binding"])
        binding["approval_commit"] = "e" * 40
        self.assert_rejected(governance_binding=binding)

    def test_execution_head_missing_governance_binding_is_rejected(self) -> None:
        self.assert_rejected(governance_binding=None)

    def test_missing_rebinding_evidence_is_rejected(self) -> None:
        binding = dict(self.arguments["governance_binding"])
        artifacts = dict(binding["artifacts_present"])
        artifacts["rebinding_evidence"] = False
        binding["artifacts_present"] = artifacts
        self.assert_rejected(governance_binding=binding)

    def test_missing_governance_binding_artifact_is_rejected(self) -> None:
        binding = dict(self.arguments["governance_binding"])
        artifacts = dict(binding["artifacts_present"])
        artifacts.pop("governance_binding")
        binding["artifacts_present"] = artifacts
        self.assert_rejected(governance_binding=binding)

    def test_missing_rebinding_audit_is_rejected(self) -> None:
        binding = dict(self.arguments["governance_binding"])
        artifacts = dict(binding["artifacts_present"])
        artifacts["rebinding_audit"] = None
        binding["artifacts_present"] = artifacts
        self.assert_rejected(governance_binding=binding)

    def test_public_api_has_no_pretranscribed_execution_head_parameter(self) -> None:
        names = set(inspect.signature(validate_execution_head_binding).parameters)
        self.assertNotIn("expected_head", names)
        self.assertNotIn("future_head", names)
        self.assertNotIn("rebinding_head", names)

    def test_helper_source_has_no_fixed_future_rebinding_sha(self) -> None:
        source = inspect.getsource(head_binding)
        literals = [
            node.value
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        ]
        self.assertFalse(
            any(re.fullmatch(r"[0-9a-f]{40}", value) for value in literals)
        )

    def test_execution_head_helper_uses_only_python_standard_library(self) -> None:
        tree = ast.parse(inspect.getsource(head_binding))
        imports = {
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        self.assertEqual(imports, {"__future__", "collections"})

    def test_helper_has_no_filesystem_git_subprocess_or_helper_calls(self) -> None:
        source = inspect.getsource(head_binding).lower()
        for prohibited in (
            "open(",
            "stat(",
            "lstat(",
            "subprocess",
            "git ",
            "github api",
            "validate_capture_argv",
            "windows_directories_equivalent",
            "official_authorization_token",
            "capture_diagnostic",
            "compare_decisions",
        ):
            self.assertNotIn(prohibited, source)

    def test_runtime_validation_performs_no_io_or_execution(self) -> None:
        with (
            patch.object(builtins, "open", side_effect=AssertionError("open")),
            patch.object(os, "stat", side_effect=AssertionError("stat")),
            patch.object(os, "lstat", side_effect=AssertionError("lstat")),
            patch.object(subprocess, "run", side_effect=AssertionError("run")),
            patch.object(
                subprocess, "check_output", side_effect=AssertionError("check_output")
            ),
            patch.object(subprocess, "Popen", side_effect=AssertionError("Popen")),
        ):
            result = self.validate()
        self.assertEqual(result["status"], "VALIDATED_EXECUTION_HEAD_BINDING")

    def test_output_is_value_free_except_required_validated_head(self) -> None:
        secret_path = "docs/synthetic_secret_governance_name.md"
        allowed = [*self.allowed_paths, secret_path]
        binding = dict(self.arguments["governance_binding"])
        binding["untrusted_content"] = "SYNTHETIC_GOVERNANCE_SECRET"
        result = self.validate(
            changed_paths=allowed,
            allowed_rebinding_paths=allowed,
            governance_binding=binding,
        )
        rendered = repr(result)
        self.assertEqual(result["validated_execution_head"], self.head)
        self.assertNotIn(secret_path, rendered)
        self.assertNotIn("SYNTHETIC_GOVERNANCE_SECRET", rendered)
        self.assertNotIn(self.package, rendered)
        self.assertNotIn(self.approval, rendered)


if __name__ == "__main__":
    unittest.main()
