from __future__ import annotations

import ast
import builtins
import hashlib
import inspect
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import stage4b_u1_preflight_argument_policy as argument_policy  # noqa: E402
import stage4b_u1_preflight_path_equivalence as path_equivalence  # noqa: E402
from stage4b_u1_preflight_argument_policy import (  # noqa: E402
    CaptureArgumentPolicyError,
    validate_capture_argv,
)


def synthetic_approved_argv() -> list[str]:
    return [
        "python",
        "scripts/stage4b_u1_capture_diagnostic_decisions.py",
        "--units",
        r"C:\synthetic\units.jsonl",
        "--queries",
        r"C:\synthetic\queries.jsonl",
        "--channel-audit",
        r"C:\synthetic\channel_audit.json",
        "--embedding-cache",
        r"C:\synthetic\embeddings.npz",
        "--reference-decisions",
        r"C:\synthetic\reference_decisions.jsonl",
        "--audit-output",
        r"C:\synthetic\stage4b_u1_pregold_diagnostic.json",
        "--temp-parent",
        r"C:\synthetic\temp",
        "--model-name",
        "synthetic/model",
        "--batch-size",
        "64",
        "--max-length",
        "192",
        "--expected-units-sha256",
        "A" * 64,
        "--expected-queries-sha256",
        "B" * 64,
        "--expected-channel-audit-sha256",
        "C" * 64,
        "--expected-embedding-cache-sha256",
        "D" * 64,
        "--official-authorization-token",
        "SYNTHETIC_NON_AUTHORIZING_TOKEN",
    ]


def value_index(argv: list[str], flag: str) -> int:
    return argv.index(flag) + 1


class Stage4BU1PreflightArgumentPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.approved = synthetic_approved_argv()

    def assert_role_drift_rejected(self, flag: str, replacement: str) -> None:
        actual = list(self.approved)
        actual[value_index(actual, flag)] = replacement
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "exactly bound"):
            validate_capture_argv(actual, self.approved)

    def assert_prohibited_role_rejected(self, prohibited: str) -> None:
        actual = list(self.approved)
        actual[actual.index("--units")] = prohibited
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "prohibited role"):
            validate_capture_argv(actual, self.approved)

    def test_exact_approved_argv_is_accepted(self) -> None:
        result = validate_capture_argv(self.approved, self.approved)
        self.assertEqual(result["status"], "VALID")
        self.assertTrue(result["exact_argv_equal"])
        self.assertEqual(result["argv_elements"], 32)
        self.assertEqual(result["flag_count"], 15)

    def test_pregold_audit_output_is_accepted(self) -> None:
        result = validate_capture_argv(self.approved, self.approved)
        self.assertEqual(result["path_role_count"], 7)

    def test_gold_in_ordinary_value_is_not_role_denied(self) -> None:
        approved = list(self.approved)
        approved[value_index(approved, "--model-name")] = "synthetic-gold-model"
        self.assertEqual(validate_capture_argv(approved, approved)["status"], "VALID")

    def test_validation_metadata_is_value_free(self) -> None:
        result = validate_capture_argv(self.approved, self.approved)
        rendered = json.dumps(result, sort_keys=True)
        for flag in argument_policy.ORDERED_FLAGS:
            self.assertNotIn(flag, rendered)
        for value in self.approved[3::2]:
            self.assertNotIn(value, rendered)

    def test_unknown_flag_is_rejected(self) -> None:
        actual = list(self.approved)
        actual[actual.index("--units")] = "--unknown-input"
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "unknown role"):
            validate_capture_argv(actual, self.approved)

    def test_duplicate_flag_is_rejected(self) -> None:
        actual = list(self.approved)
        actual[actual.index("--queries")] = "--units"
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "duplicate role"):
            validate_capture_argv(actual, self.approved)

    def test_missing_flag_value_is_rejected(self) -> None:
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "exactly 32"):
            validate_capture_argv(self.approved[:-2], self.approved)

    def test_missing_value_is_rejected(self) -> None:
        actual = list(self.approved)
        del actual[value_index(actual, "--max-length")]
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "exactly 32"):
            validate_capture_argv(actual, self.approved)

    def test_extra_positional_argument_is_rejected(self) -> None:
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "exactly 32"):
            validate_capture_argv([*self.approved, "extra"], self.approved)

    def test_argument_order_drift_is_rejected(self) -> None:
        actual = list(self.approved)
        actual[2:6] = actual[4:6] + actual[2:4]
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "role order"):
            validate_capture_argv(actual, self.approved)

    def test_executable_drift_is_rejected(self) -> None:
        actual = list(self.approved)
        actual[0] = "python3"
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "executable"):
            validate_capture_argv(actual, self.approved)

    def test_capture_script_drift_is_rejected(self) -> None:
        actual = list(self.approved)
        actual[1] = "scripts/other.py"
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "capture script"):
            validate_capture_argv(actual, self.approved)

    def test_units_path_drift_is_rejected(self) -> None:
        self.assert_role_drift_rejected("--units", r"C:\drift\units.jsonl")

    def test_queries_path_drift_is_rejected(self) -> None:
        self.assert_role_drift_rejected("--queries", r"C:\drift\queries.jsonl")

    def test_channel_audit_path_drift_is_rejected(self) -> None:
        self.assert_role_drift_rejected(
            "--channel-audit", r"C:\drift\channel_audit.json"
        )

    def test_embedding_cache_path_drift_is_rejected(self) -> None:
        self.assert_role_drift_rejected(
            "--embedding-cache", r"C:\drift\embeddings.npz"
        )

    def test_reference_decisions_path_drift_is_rejected(self) -> None:
        self.assert_role_drift_rejected(
            "--reference-decisions", r"C:\drift\reference.jsonl"
        )

    def test_audit_output_path_drift_is_rejected(self) -> None:
        self.assert_role_drift_rejected(
            "--audit-output", r"C:\drift\pregold_audit.json"
        )

    def test_temp_parent_path_drift_is_rejected(self) -> None:
        self.assert_role_drift_rejected("--temp-parent", r"C:\drift\temp")

    def test_relative_windows_path_is_rejected(self) -> None:
        actual = list(self.approved)
        actual[value_index(actual, "--units")] = r"relative\units.jsonl"
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "absolute Windows"):
            validate_capture_argv(actual, self.approved)

    def test_model_value_drift_is_rejected(self) -> None:
        self.assert_role_drift_rejected("--model-name", "synthetic/other-model")

    def test_token_drift_is_rejected(self) -> None:
        self.assert_role_drift_rejected(
            "--official-authorization-token", "SYNTHETIC_DIFFERENT_TOKEN"
        )

    def test_zero_batch_size_is_rejected(self) -> None:
        actual = list(self.approved)
        actual[value_index(actual, "--batch-size")] = "0"
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "positive decimal"):
            validate_capture_argv(actual, self.approved)

    def test_leading_zero_batch_size_is_rejected(self) -> None:
        actual = list(self.approved)
        actual[value_index(actual, "--batch-size")] = "064"
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "positive decimal"):
            validate_capture_argv(actual, self.approved)

    def test_non_decimal_max_length_is_rejected(self) -> None:
        actual = list(self.approved)
        actual[value_index(actual, "--max-length")] = "+192"
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "positive decimal"):
            validate_capture_argv(actual, self.approved)

    def test_lowercase_units_sha_is_rejected(self) -> None:
        actual = list(self.approved)
        actual[value_index(actual, "--expected-units-sha256")] = "a" * 64
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "uppercase SHA-256"):
            validate_capture_argv(actual, self.approved)

    def test_short_queries_sha_is_rejected(self) -> None:
        actual = list(self.approved)
        actual[value_index(actual, "--expected-queries-sha256")] = "B" * 63
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "uppercase SHA-256"):
            validate_capture_argv(actual, self.approved)

    def test_nonhex_channel_sha_is_rejected(self) -> None:
        actual = list(self.approved)
        actual[value_index(actual, "--expected-channel-audit-sha256")] = "G" * 64
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "uppercase SHA-256"):
            validate_capture_argv(actual, self.approved)

    def test_spaced_cache_sha_is_rejected(self) -> None:
        actual = list(self.approved)
        actual[value_index(actual, "--expected-embedding-cache-sha256")] = (
            "D" * 63 + " "
        )
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "uppercase SHA-256"):
            validate_capture_argv(actual, self.approved)

    def test_rankings_role_is_rejected(self) -> None:
        self.assert_prohibited_role_rejected("--rankings")

    def test_policy_role_is_rejected(self) -> None:
        self.assert_prohibited_role_rejected("--policy")

    def test_gold_map_role_is_rejected(self) -> None:
        self.assert_prohibited_role_rejected("--gold-map")

    def test_source_audit_role_is_rejected(self) -> None:
        self.assert_prohibited_role_rejected("--source-audit")

    def test_evaluator_role_is_rejected(self) -> None:
        self.assert_prohibited_role_rejected("--evaluator")

    def test_reservation_role_is_rejected(self) -> None:
        self.assert_prohibited_role_rejected("--reservation")

    def test_stage3b_role_is_rejected(self) -> None:
        self.assert_prohibited_role_rejected("--stage3b")

    def test_nonsequence_argv_is_rejected(self) -> None:
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "sequence"):
            validate_capture_argv("python", self.approved)  # type: ignore[arg-type]

    def test_nontext_argv_item_is_rejected(self) -> None:
        actual: list[object] = list(self.approved)
        actual[3] = 123
        with self.assertRaisesRegex(CaptureArgumentPolicyError, "non-empty text"):
            validate_capture_argv(actual, self.approved)  # type: ignore[arg-type]

    def test_argument_policy_uses_only_python_standard_library(self) -> None:
        tree = ast.parse(inspect.getsource(argument_policy))
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".", 1)[0])
        self.assertEqual(imports, {"__future__", "collections", "ntpath"})

    def test_argument_policy_has_no_filesystem_hash_or_execution_calls(self) -> None:
        tree = ast.parse(inspect.getsource(argument_policy))
        forbidden_names = {"open", "exec", "eval", "compile", "__import__"}
        forbidden_attributes = {
            "open",
            "stat",
            "lstat",
            "read_text",
            "read_bytes",
            "sha256",
            "run",
            "Popen",
            "system",
        }
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, forbidden_names)
            elif isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr, forbidden_attributes)

    def test_argument_policy_has_no_capture_or_path_helper_import(self) -> None:
        tree = ast.parse(inspect.getsource(argument_policy))
        modules: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module)
        self.assertNotIn("stage4b_u1_capture_diagnostic_decisions", modules)
        self.assertNotIn("stage4b_u1_preflight_path_equivalence", modules)

    def test_argument_policy_has_no_raw_gold_value_substring_denylist(self) -> None:
        tree = ast.parse(inspect.getsource(argument_policy))
        bare_constants = [
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and node.value.casefold() == "gold"
        ]
        forbidden_methods = {
            "find",
            "index",
            "lower",
            "casefold",
            "split",
            "encode",
            "decode",
            "search",
            "match",
            "fullmatch",
        }
        calls = [
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        ]
        self.assertEqual(bare_constants, [])
        self.assertTrue(forbidden_methods.isdisjoint(calls))

    def test_runtime_validation_does_not_use_filesystem_hash_or_subprocess(self) -> None:
        def blocked(*_args: object, **_kwargs: object) -> object:
            raise AssertionError("forbidden runtime call")

        with (
            patch.object(builtins, "open", side_effect=blocked),
            patch.object(os, "stat", side_effect=blocked),
            patch.object(os, "lstat", side_effect=blocked),
            patch.object(Path, "stat", side_effect=blocked),
            patch.object(hashlib, "sha256", side_effect=blocked),
            patch.object(subprocess, "run", side_effect=blocked),
            patch.object(subprocess, "Popen", side_effect=blocked),
        ):
            result = validate_capture_argv(self.approved, self.approved)
        self.assertFalse(result["filesystem_accessed"])
        self.assertFalse(result["command_executed"])

    def test_runtime_validation_does_not_call_capture_or_path_helper(self) -> None:
        original_import = builtins.__import__

        def guarded_import(name: str, *args: object, **kwargs: object) -> object:
            if name == "stage4b_u1_capture_diagnostic_decisions":
                raise AssertionError("capture import attempted")
            return original_import(name, *args, **kwargs)

        with (
            patch.object(builtins, "__import__", side_effect=guarded_import),
            patch.object(
                path_equivalence,
                "windows_directories_equivalent",
                side_effect=AssertionError("path helper called"),
            ),
        ):
            result = validate_capture_argv(self.approved, self.approved)
        self.assertFalse(result["authorization_token_used"])


if __name__ == "__main__":
    unittest.main()
