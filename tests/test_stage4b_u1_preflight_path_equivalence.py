from __future__ import annotations

import ast
import inspect
import ntpath
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import stage4b_u1_preflight_path_equivalence as path_equivalence  # noqa: E402
from stage4b_u1_preflight_path_equivalence import (  # noqa: E402
    PathEquivalenceError,
    windows_directories_equivalent,
)


class Stage4BU1PreflightPathEquivalenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="stage4b_u1_5e_a_")
        self.base = Path(self.temp.name)
        self.actual = self.base / "CaseProbe"
        self.actual.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_same_absolute_directory_is_accepted(self) -> None:
        self.assertTrue(
            windows_directories_equivalent(str(self.actual), str(self.actual))
        )

    def test_trailing_separator_is_accepted(self) -> None:
        self.assertTrue(
            windows_directories_equivalent(
                str(self.actual) + "\\", str(self.actual)
            )
        )

    def test_windows_case_variant_is_accepted(self) -> None:
        self.assertTrue(
            windows_directories_equivalent(
                str(self.actual).swapcase(), str(self.actual)
            )
        )

    def test_forward_slash_variant_is_accepted(self) -> None:
        self.assertTrue(
            windows_directories_equivalent(
                str(self.actual).replace("\\", "/"), str(self.actual)
            )
        )

    def test_terminal_dot_segment_is_accepted(self) -> None:
        self.assertTrue(
            windows_directories_equivalent(
                str(self.actual) + "\\.", str(self.actual)
            )
        )

    def test_parent_directory_is_rejected(self) -> None:
        self.assertFalse(
            windows_directories_equivalent(str(self.actual), str(self.base))
        )

    def test_child_directory_is_rejected(self) -> None:
        child = self.actual / "child"
        child.mkdir()
        self.assertFalse(
            windows_directories_equivalent(str(self.actual), str(child))
        )

    def test_prefix_collision_directory_is_rejected(self) -> None:
        collision = self.base / "CaseProbe2"
        collision.mkdir()
        self.assertFalse(
            windows_directories_equivalent(str(self.actual), str(collision))
        )

    def test_unrelated_directory_is_rejected(self) -> None:
        unrelated = self.base / "Elsewhere"
        unrelated.mkdir()
        self.assertFalse(
            windows_directories_equivalent(str(self.actual), str(unrelated))
        )

    def test_relative_path_is_rejected_before_normalization(self) -> None:
        with self.assertRaisesRegex(PathEquivalenceError, "must be absolute"):
            windows_directories_equivalent("CaseProbe", str(self.actual))

    def test_nonexistent_path_is_rejected(self) -> None:
        missing = self.base / "missing"
        with self.assertRaisesRegex(PathEquivalenceError, "must exist"):
            windows_directories_equivalent(str(missing), str(self.actual))

    def test_file_path_is_rejected(self) -> None:
        file_path = self.base / "not_a_directory.txt"
        file_path.write_text("synthetic", encoding="ascii")
        with self.assertRaisesRegex(PathEquivalenceError, "must be a directory"):
            windows_directories_equivalent(str(file_path), str(self.actual))

    def test_leaf_reparse_point_is_rejected_without_skip(self) -> None:
        with patch.object(
            path_equivalence, "_leaf_is_reparse_point", return_value=True
        ):
            with self.assertRaisesRegex(PathEquivalenceError, "reparse-point"):
                windows_directories_equivalent(str(self.actual), str(self.actual))

    def test_exact_comparison_has_no_prefix_acceptance_call(self) -> None:
        tree = ast.parse(inspect.getsource(path_equivalence))
        prefix_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "startswith"
        ]
        self.assertEqual(prefix_calls, [])

    def test_helper_uses_only_python_standard_library(self) -> None:
        tree = ast.parse(inspect.getsource(path_equivalence))
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".", 1)[0])
        self.assertEqual(
            imports,
            {"__future__", "ctypes", "ntpath", "os", "stat", "typing"},
        )

    def test_helper_has_no_command_token_or_execution_logic(self) -> None:
        source = inspect.getsource(path_equivalence).lower()
        for forbidden in ("--temp-parent", "authorization", "capture", "token"):
            self.assertNotIn(forbidden, source)

    def test_leaf_probes_are_limited_to_supplied_synthetic_paths(self) -> None:
        observed: list[str] = []
        original = path_equivalence._require_existing_plain_directory

        def record(path: str, label: str) -> None:
            observed.append(ntpath.normcase(ntpath.abspath(path)))
            original(path, label)

        with patch.object(
            path_equivalence,
            "_require_existing_plain_directory",
            side_effect=record,
        ):
            self.assertTrue(
                windows_directories_equivalent(str(self.actual), str(self.actual))
            )
        expected = ntpath.normcase(ntpath.abspath(str(self.actual)))
        self.assertEqual(observed, [expected, expected])

    def test_invalid_non_text_path_is_rejected(self) -> None:
        with self.assertRaisesRegex(PathEquivalenceError, "string-like path"):
            windows_directories_equivalent(123, str(self.actual))  # type: ignore[arg-type]
