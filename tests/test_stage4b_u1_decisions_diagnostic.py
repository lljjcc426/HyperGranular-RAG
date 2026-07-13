from __future__ import annotations

import copy
import json
import math
import subprocess
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
TESTS = REPO_ROOT / "tests"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(TESTS))

import stage4b_u1_capture_diagnostic_decisions as capture_module  # noqa: E402
import stage4b_u1_goldfree_controller as controller_module  # noqa: E402
from stage4b_u1_capture_diagnostic_decisions import (  # noqa: E402
    DECISION_FIELDS,
    compute_decisions_only,
    generate_decisions_only_from_inputs,
    run_diagnostic_capture,
    validate_synthetic_path_allowlist,
)
from stage4b_u1_common import (  # noqa: E402
    IMPLEMENTATION_CHECKPOINT,
    id_digest,
    sha256_file,
    write_json,
    write_jsonl,
)
from stage4b_u1_compare_decisions import (  # noqa: E402
    DecisionsDiagnosticError,
    binary64_bits,
    binary64_order_key,
    binary64_ulp_distance,
    canonical_json_bytes,
    compare_decisions_files,
    strict_json_loads,
    validate_json_value,
)
from stage4b_u1_goldfree_retrieval import (  # noqa: E402
    RetrievalConfig,
    allocate_budget,
    build_query_decisions,
    fit_ecdf_references,
    normalize_matrix,
    score_rows,
)
from stage4b_u1_prepare_channels import prepare_channels  # noqa: E402
from test_stage4b_u1_goldfree import synthetic_labeled_rows  # noqa: E402


def decision(query_id: str = "synthetic::q0") -> dict:
    return {
        "query_id": query_id,
        "dataset": "synthetic",
        "sample_id": query_id.split("::")[-1],
        "ball_score_margin": 0.125,
        "boundary_margin": 0.25,
        "selected_edge_count": 2,
        "planned_insert_count": 1,
        "feasible": True,
        "u_margin": 0.5,
        "u_boundary": 0.75,
        "r_edge": 0.25,
        "r_candidate": 0.5,
        "uncertainty": 0.625,
        "readiness": 0.375,
        "score": 0.125,
        "tie_hash": "A" * 64,
        "ordered_rank": 0,
        "trigger_u1": True,
    }


def write_rows(
    path: Path,
    rows: list[dict],
    *,
    sort_keys: bool = False,
    indent: int | None = None,
    spaced: bool = False,
    terminal_newline: bool = True,
) -> None:
    separators = None if indent is not None else ((", ", ": ") if spaced else (",", ":"))
    payload = "\n".join(
        json.dumps(
            row,
            ensure_ascii=False,
            sort_keys=sort_keys,
            indent=indent,
            separators=separators,
            allow_nan=True,
        )
        for row in rows
    )
    if terminal_newline:
        payload += "\n"
    path.write_text(payload, encoding="utf-8", newline="\n")


def compare_pair(
    root: Path,
    left_rows: list[dict],
    right_rows: list[dict],
    **right_options: object,
) -> dict:
    left = root / "left.jsonl"
    right = root / "right.jsonl"
    write_rows(left, left_rows)
    write_rows(right, right_rows, **right_options)
    return compare_decisions_files(left, right)


def legacy_inline_decisions(
    units: list[dict],
    queries: list[dict],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
) -> list[dict]:
    config = RetrievalConfig()
    rows = build_query_decisions(
        units, queries, unit_embeddings, query_embeddings, config
    )
    references = fit_ecdf_references(rows)
    score_rows(rows, references)
    allocate_budget(rows, config.budget_fraction)
    legacy_fields = {
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
    return [{key: row[key] for key in legacy_fields} for row in rows]


def build_capture_fixture(root: Path) -> dict[str, Path]:
    labeled_units, labeled_queries, unit_embeddings, query_embeddings = (
        synthetic_labeled_rows()
    )
    units, queries, _ = prepare_channels(labeled_units, labeled_queries)
    paths = {
        "units": root / "unlabeled_units.jsonl",
        "queries": root / "unlabeled_queries.jsonl",
        "channel": root / "channel_audit.json",
        "cache": root / "cache.npz",
        "reference": root / "reference_decisions.jsonl",
        "audit": root / "diagnostic_audit.json",
        "temp_parent": root / "temp",
    }
    paths["temp_parent"].mkdir()
    write_jsonl(paths["units"], units)
    write_jsonl(paths["queries"], queries)
    np.savez_compressed(
        paths["cache"],
        unit_embeddings=unit_embeddings,
        query_embeddings=query_embeddings,
        unit_ids=np.asarray([row["unit_id"] for row in units]),
        query_ids=np.asarray([row["query_id"] for row in queries]),
        model_name=np.asarray(["synthetic-model"]),
        max_length=np.asarray([192], dtype="int64"),
    )
    write_json(
        paths["channel"],
        {
            "implementation_checkpoint": IMPLEMENTATION_CHECKPOINT,
            "status": "CONTROLLER_CHANNEL_PREPARED_NO_RETRIEVAL_METRICS",
            "run_role": "development",
            "synthetic_test_mode": True,
            "boundary_status": "SYNTHETIC_TEST_BOUNDARY",
            "sample_id_sha256": id_digest(row["sample_id"] for row in queries),
            "query_id_sha256": id_digest(row["query_id"] for row in queries),
            "channel_hashes": {
                "unlabeled_units": sha256_file(paths["units"]),
                "unlabeled_queries": sha256_file(paths["queries"]),
            },
            "retrieval_metrics_computed": False,
        },
    )
    reference = compute_decisions_only(
        units,
        queries,
        normalize_matrix(unit_embeddings),
        normalize_matrix(query_embeddings),
        RetrievalConfig(),
    )
    write_jsonl(paths["reference"], reference)
    return paths


def capture_kwargs(paths: dict[str, Path], root: Path) -> dict:
    return {
        "units_path": paths["units"],
        "queries_path": paths["queries"],
        "channel_audit_path": paths["channel"],
        "embedding_cache_path": paths["cache"],
        "reference_decisions_path": paths["reference"],
        "audit_output_path": paths["audit"],
        "temp_parent": paths["temp_parent"],
        "model_name": "synthetic-model",
        "batch_size": 64,
        "max_length": 192,
        "expected_embedding_cache_sha256": sha256_file(paths["cache"]),
        "synthetic_test_mode": True,
        "synthetic_root": root,
    }


class Stage4BU1DecisionsComparatorTests(unittest.TestCase):
    def test_identical_raw_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(Path(directory), [decision()], [decision()])
        self.assertEqual(report["status"], "IDENTICAL_BYTES")
        self.assertTrue(report["byte_equivalent"])

    def test_terminal_newline_only_difference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(
                Path(directory), [decision()], [decision()], terminal_newline=False
            )
        self.assertEqual(report["status"], "CANONICAL_EQUAL_RAW_DIFFERENT")
        self.assertFalse(report["byte_equivalent"])
        self.assertTrue(report["canonical_equal"])

    def test_whitespace_only_difference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(
                Path(directory), [decision()], [decision()], spaced=True
            )
        self.assertTrue(report["canonical_equal"])
        self.assertFalse(report["byte_equivalent"])

    def test_json_field_order_only_difference(self) -> None:
        row = decision()
        reversed_row = dict(reversed(list(row.items())))
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(Path(directory), [row], [reversed_row])
        self.assertTrue(report["canonical_equal"])
        self.assertEqual(
            report["comparison_layers"]["schema"]["field_order_difference_query_count"],
            1,
        )

    def test_row_count_difference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(
                Path(directory),
                [decision("synthetic::q0")],
                [decision("synthetic::q0"), decision("synthetic::q1")],
            )
        self.assertEqual(report["comparison_layers"]["row_identity"]["left_rows"], 1)
        self.assertEqual(report["comparison_layers"]["row_identity"]["right_rows"], 2)

    def test_query_id_order_difference(self) -> None:
        rows = [decision("synthetic::q0"), decision("synthetic::q1")]
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(Path(directory), rows, list(reversed(rows)))
        self.assertTrue(report["comparison_layers"]["row_identity"]["query_id_set_equal"])
        self.assertFalse(report["comparison_layers"]["row_identity"]["query_id_order_equal"])

    def test_query_id_missing_or_extra(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(
                Path(directory),
                [decision("synthetic::q0")],
                [decision("synthetic::q1")],
            )
        layer = report["comparison_layers"]["row_identity"]
        self.assertEqual(layer["missing_from_left_count"], 1)
        self.assertEqual(layer["missing_from_right_count"], 1)

    def test_duplicate_query_id_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            left = root / "left.jsonl"
            right = root / "right.jsonl"
            write_rows(left, [decision(), decision()])
            write_rows(right, [decision()])
            with self.assertRaisesRegex(DecisionsDiagnosticError, "Duplicate query_id"):
                compare_decisions_files(left, right)

    def test_missing_query_id_rejected(self) -> None:
        row = decision()
        del row["query_id"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            left = root / "left.jsonl"
            right = root / "right.jsonl"
            write_rows(left, [row])
            write_rows(right, [decision()])
            with self.assertRaisesRegex(DecisionsDiagnosticError, "Missing query_id"):
                compare_decisions_files(left, right)

    def test_invalid_json_rejected(self) -> None:
        with self.assertRaises(DecisionsDiagnosticError):
            strict_json_loads('{"query_id":')

    def test_duplicate_json_key_rejected(self) -> None:
        with self.assertRaisesRegex(DecisionsDiagnosticError, "Duplicate JSON object key"):
            strict_json_loads('{"query_id":"q","query_id":"q"}')

    def test_schema_missing_field(self) -> None:
        right = decision()
        del right["score"]
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(Path(directory), [decision()], [right])
        self.assertEqual(
            report["comparison_layers"]["schema"]["field_set_difference_query_count"],
            1,
        )

    def test_schema_extra_field(self) -> None:
        right = decision()
        right["extra_synthetic_field"] = "x"
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(Path(directory), [decision()], [right])
        self.assertEqual(
            report["comparison_layers"]["schema"]["field_set_difference_query_count"],
            1,
        )

    def test_incomparable_heterogeneous_file_schema_rejected(self) -> None:
        first = decision("synthetic::q0")
        second = decision("synthetic::q1")
        second["score"] = "not-a-float"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            left = root / "left.jsonl"
            right = root / "right.jsonl"
            output = root / "report.json"
            write_rows(left, [first, second])
            write_rows(right, [first, second])
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "stage4b_u1_compare_decisions.py"),
                    "--left-decisions",
                    str(left),
                    "--right-decisions",
                    str(right),
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(output.exists())
            self.assertIn("Incomparable heterogeneous decisions schema", completed.stderr)

    def test_bool_and_int_are_distinct(self) -> None:
        right = decision()
        right["feasible"] = 1
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(Path(directory), [decision()], [right])
        self.assertEqual(
            report["comparison_layers"]["schema"]["type_or_structure_difference_query_count"],
            1,
        )

    def test_int_and_float_are_distinct(self) -> None:
        right = decision()
        right["planned_insert_count"] = 1.0
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(Path(directory), [decision()], [right])
        self.assertEqual(
            report["comparison_layers"]["schema"]["type_or_structure_difference_query_count"],
            1,
        )

    def test_discrete_scalar_difference(self) -> None:
        right = decision()
        right["tie_hash"] = "B" * 64
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(Path(directory), [decision()], [right])
        self.assertEqual(report["comparison_layers"]["discrete_values"]["tie_hash"], 1)

    def test_id_list_element_difference(self) -> None:
        left = decision()
        right = decision()
        left["synthetic_ids"] = ["u1", "u2"]
        right["synthetic_ids"] = ["u1", "u3"]
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(Path(directory), [left], [right])
        self.assertEqual(
            report["comparison_layers"]["discrete_values"]["synthetic_ids"], 1
        )

    def test_id_list_order_difference(self) -> None:
        left = decision()
        right = decision()
        left["synthetic_ids"] = ["u1", "u2"]
        right["synthetic_ids"] = ["u2", "u1"]
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(Path(directory), [left], [right])
        self.assertEqual(
            report["comparison_layers"]["discrete_values"]["synthetic_ids"], 1
        )

    def test_float_exact_equality(self) -> None:
        self.assertEqual(binary64_ulp_distance(0.125, 0.125), 0)
        self.assertEqual(binary64_bits(1.0), 0x3FF0000000000000)

    def test_float_absolute_difference(self) -> None:
        right = decision()
        right["score"] = math.nextafter(0.125, math.inf)
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(Path(directory), [decision()], [right])
        details = report["comparison_layers"]["finite_float"]["score"]
        self.assertGreater(details["max_absolute_error"], 0.0)

    def test_float_ulp_distance(self) -> None:
        self.assertEqual(binary64_ulp_distance(1.0, math.nextafter(1.0, math.inf)), 1)

    def test_signed_zero_binary64_is_distinct(self) -> None:
        self.assertNotEqual(binary64_bits(0.0), binary64_bits(-0.0))
        self.assertEqual(binary64_ulp_distance(-0.0, 0.0), 1)
        self.assertEqual(binary64_order_key(-0.0) + 1, binary64_order_key(0.0))

    def test_signed_zero_is_reported(self) -> None:
        left = decision()
        right = decision()
        left["score"] = -0.0
        right["score"] = 0.0
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(Path(directory), [left], [right])
        details = report["comparison_layers"]["finite_float"]["score"]
        self.assertEqual(details["signed_zero_difference_count"], 1)
        self.assertEqual(details["max_ulp_distance"], 1)

    def test_cross_sign_ulp_order_is_monotonic(self) -> None:
        left = -math.nextafter(0.0, 1.0)
        right = math.nextafter(0.0, 1.0)
        self.assertLess(binary64_order_key(left), binary64_order_key(-0.0))
        self.assertLess(binary64_order_key(-0.0), binary64_order_key(0.0))
        self.assertLess(binary64_order_key(0.0), binary64_order_key(right))
        self.assertEqual(binary64_ulp_distance(left, right), 3)

    def test_nan_rejected(self) -> None:
        with self.assertRaisesRegex(DecisionsDiagnosticError, "Non-finite"):
            strict_json_loads('{"query_id":"q","score":NaN}')

    def test_positive_infinity_rejected(self) -> None:
        with self.assertRaisesRegex(DecisionsDiagnosticError, "Non-finite"):
            strict_json_loads('{"query_id":"q","score":Infinity}')

    def test_negative_infinity_rejected(self) -> None:
        with self.assertRaisesRegex(DecisionsDiagnosticError, "Non-finite"):
            strict_json_loads('{"query_id":"q","score":-Infinity}')

    def test_unknown_value_type_rejected(self) -> None:
        with self.assertRaisesRegex(DecisionsDiagnosticError, "Unsupported JSON value type"):
            validate_json_value({"query_id": "q", "bad": object()})

    def test_planned_insert_count_semantic_difference(self) -> None:
        right = decision()
        right["planned_insert_count"] = 2
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(Path(directory), [decision()], [right])
        self.assertEqual(
            report["comparison_layers"]["decision_semantics"]["planned_insert_count"],
            1,
        )

    def test_ordered_rank_semantic_difference(self) -> None:
        right = decision()
        right["ordered_rank"] = 3
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(Path(directory), [decision()], [right])
        self.assertEqual(
            report["comparison_layers"]["decision_semantics"]["ordered_rank"], 1
        )

    def test_trigger_u1_semantic_difference(self) -> None:
        right = decision()
        right["trigger_u1"] = False
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(Path(directory), [decision()], [right])
        self.assertEqual(
            report["comparison_layers"]["decision_semantics"]["trigger_u1"], 1
        )

    def test_report_does_not_emit_raw_query_ids_or_rows(self) -> None:
        right = decision()
        right["score"] = 0.5
        with tempfile.TemporaryDirectory() as directory:
            report = compare_pair(Path(directory), [decision()], [right])
        serialized = json.dumps(report, sort_keys=True)
        self.assertNotIn("synthetic::q0", serialized)
        self.assertFalse(report["raw_query_ids_emitted"])
        self.assertFalse(report["raw_decision_rows_emitted"])

    def test_canonical_json_is_deterministic(self) -> None:
        left = decision()
        right = dict(reversed(list(left.items())))
        self.assertEqual(canonical_json_bytes(left), canonical_json_bytes(right))


class Stage4BU1DiagnosticCaptureTests(unittest.TestCase):
    def test_extracted_decisions_match_legacy_inline_canonical_bytes_and_fields(self) -> None:
        labeled_units, labeled_queries, unit_embeddings, query_embeddings = (
            synthetic_labeled_rows()
        )
        units, queries, _ = prepare_channels(labeled_units, labeled_queries)
        expected = legacy_inline_decisions(
            units, queries, unit_embeddings, query_embeddings
        )
        actual = compute_decisions_only(
            units,
            queries,
            unit_embeddings,
            query_embeddings,
            RetrievalConfig(),
        )
        self.assertEqual(expected, actual)
        expected_bytes = b"".join(canonical_json_bytes(row) + b"\n" for row in expected)
        actual_bytes = b"".join(canonical_json_bytes(row) + b"\n" for row in actual)
        self.assertEqual(expected_bytes, actual_bytes)
        self.assertEqual(set(actual[0]), DECISION_FIELDS)

    def test_temporary_decisions_removed_after_success(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = build_capture_fixture(root)
            report = run_diagnostic_capture(**capture_kwargs(paths, root))
            self.assertTrue(report["temporary_decisions_cleaned"])
            self.assertEqual(list(paths["temp_parent"].iterdir()), [])

    def test_temporary_decisions_removed_after_exception(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = build_capture_fixture(root)
            with patch.object(
                capture_module,
                "compare_decisions_files",
                side_effect=RuntimeError("synthetic comparator failure"),
            ):
                with self.assertRaisesRegex(RuntimeError, "synthetic comparator failure"):
                    run_diagnostic_capture(**capture_kwargs(paths, root))
            self.assertEqual(list(paths["temp_parent"].iterdir()), [])
            self.assertFalse(paths["audit"].exists())

    def test_synthetic_allowlist_rejects_official_path_before_open(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "synthetic"
            root.mkdir()
            outside = Path(directory) / "official_units.jsonl"
            with patch("builtins.open", side_effect=AssertionError("path was opened")):
                with self.assertRaisesRegex(ValueError, "outside the allowlist root"):
                    generate_decisions_only_from_inputs(
                        units_path=outside,
                        queries_path=root / "queries.jsonl",
                        channel_audit_path=root / "audit.json",
                        embedding_cache_path=root / "cache.npz",
                        model_name="synthetic-model",
                        batch_size=64,
                        max_length=192,
                        expected_embedding_cache_sha256="0" * 64,
                        synthetic_test_mode=True,
                        synthetic_root=root,
                    )

    def test_official_mode_without_5b_token_fails_before_open(self) -> None:
        bogus = Path("never-opened-official-input.jsonl")
        with patch("builtins.open", side_effect=AssertionError("path was opened")):
            with self.assertRaisesRegex(PermissionError, "locked pending Amendment 5B"):
                generate_decisions_only_from_inputs(
                    units_path=bogus,
                    queries_path=bogus,
                    channel_audit_path=bogus,
                    embedding_cache_path=bogus,
                    model_name="synthetic-model",
                    batch_size=64,
                    max_length=192,
                    expected_embedding_cache_sha256="0" * 64,
                    synthetic_test_mode=False,
                    synthetic_root=None,
                )

    def test_capture_does_not_call_controller_rankings_or_policy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = build_capture_fixture(root)
            original_open = Path.open

            def guarded_open(path: Path, *args: object, **kwargs: object):
                if path.name in {"rankings.jsonl", "policy.json"}:
                    raise AssertionError("ranking or policy path accessed")
                return original_open(path, *args, **kwargs)

            with patch.object(
                controller_module,
                "run_controller",
                side_effect=AssertionError("full controller called"),
            ), patch.object(Path, "open", new=guarded_open):
                report = run_diagnostic_capture(**capture_kwargs(paths, root))
            self.assertFalse(report["rankings_accessed"])
            self.assertFalse(report["rankings_generated"])
            self.assertFalse(report["policy_builder_called"])
            self.assertFalse(report["policy_generated"])

    def test_capture_is_byte_identical_to_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = build_capture_fixture(root)
            report = run_diagnostic_capture(**capture_kwargs(paths, root))
        self.assertTrue(report["byte_equivalent"])
        self.assertEqual(report["status"], "IDENTICAL_BYTES")

    def test_allowlist_rejects_missing_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing"
            with self.assertRaisesRegex(ValueError, "root must exist"):
                validate_synthetic_path_allowlist({}, missing)

    def test_capture_requires_positive_batch_size(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = build_capture_fixture(root)
            kwargs = capture_kwargs(paths, root)
            kwargs["batch_size"] = 0
            with self.assertRaisesRegex(ValueError, "must be positive"):
                run_diagnostic_capture(**kwargs)
            self.assertEqual(list(paths["temp_parent"].iterdir()), [])

    def test_capture_audit_contains_no_ranking_policy_or_gold_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = build_capture_fixture(root)
            run_diagnostic_capture(**capture_kwargs(paths, root))
            audit = json.loads(paths["audit"].read_text(encoding="utf-8"))
        self.assertFalse(audit["rankings_accessed"])
        self.assertFalse(audit["policy_generated"])
        self.assertFalse(audit["gold_accessed"])
        self.assertNotIn("question", json.dumps(audit, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
