from __future__ import annotations

import ast
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import stage4b_u1_inventory_decision_schemas as inventory_module  # noqa: E402
from stage4b_u1_inventory_decision_schemas import (  # noqa: E402
    FROZEN_FUTURE_REFERENCE_PATH,
    STAGING_PREFIX,
    SchemaInventoryError,
    inventory_jsonl,
    run_schema_inventory,
)


def write_raw(path: Path, rows: list[str], *, terminal_newline: bool = True) -> None:
    payload = "\n".join(rows)
    if terminal_newline:
        payload += "\n"
    path.write_text(payload, encoding="utf-8", newline="\n")


def inventory_for(root: Path, rows: list[str]) -> dict:
    path = root / "input.jsonl"
    write_raw(path, rows)
    return inventory_jsonl(path)


def schema_by_count(result: dict, count: int) -> dict:
    matches = [schema for schema in result["schemas"] if schema["row_count"] == count]
    if len(matches) != 1:
        raise AssertionError(f"Expected one schema with count {count}, got {len(matches)}")
    return matches[0]


class DecisionSchemaInventoryTests(unittest.TestCase):
    def test_homogeneous_flat_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = inventory_for(
                Path(tmp),
                ['{"a":1,"b":true,"c":"x"}', '{"a":2,"b":false,"c":"y"}'],
            )
        self.assertEqual(result["total_rows"], 2)
        self.assertEqual(result["distinct_ordered_schema_signatures"], 1)
        schema = result["schemas"][0]
        self.assertEqual(schema["field_types"], {"a": "integer", "b": "bool", "c": "string"})

    def test_field_additions_and_removals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = inventory_for(
                Path(tmp),
                ['{"a":1,"b":true}', '{"a":2,"b":false}', '{"a":3,"c":"x"}'],
            )
        variant = schema_by_count(result, 1)
        self.assertEqual(variant["differences_from_main"]["added_fields"], ["$/c"])
        self.assertEqual(variant["differences_from_main"]["removed_fields"], ["$/b"])

    def test_field_order_only_difference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = inventory_for(Path(tmp), ['{"a":1,"b":"x"}', '{"b":"y","a":2}'])
        self.assertEqual(result["distinct_ordered_schema_signatures"], 2)
        self.assertEqual(result["distinct_structural_schema_signatures"], 1)
        non_main = next(
            schema
            for schema in result["schemas"]
            if schema["ordered_signature"] != result["main_ordered_signature"]
        )
        self.assertEqual(non_main["differences_from_main"]["order_only_fields"], ["$"])

    def test_bool_integer_and_finite_number_are_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = inventory_for(Path(tmp), ['{"x":true}', '{"x":1}', '{"x":1.0}'])
        types = {schema["field_types"]["x"] for schema in result["schemas"]}
        self.assertEqual(types, {"bool", "integer", "finite_number"})

    def test_nested_object_and_array_element_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = inventory_for(
                Path(tmp),
                [
                    '{"meta":{"a":1},"items":[{"x":1}]}',
                    '{"meta":{"a":2},"items":[{"x":2}]}',
                    '{"meta":{"a":"s"},"items":[{"y":1}]}',
                ],
            )
        variant = schema_by_count(result, 1)
        differences = variant["differences_from_main"]
        self.assertIn("$/meta/a", differences["type_changed_fields"])
        self.assertTrue(differences["nesting_changed_fields"])

    def test_array_ignores_values_order_multiplicity_and_length(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = inventory_for(
                Path(tmp), ['{"x":[1,"a",1]}', '{"x":["b",2]}']
            )
        self.assertEqual(result["distinct_ordered_schema_signatures"], 1)
        array_schema = result["schemas"][0]["field_schemas"]["x"]
        self.assertFalse(array_schema["empty"])
        self.assertEqual(
            {item["type"] for item in array_schema["element_schemas"]},
            {"integer", "string"},
        )

    def test_empty_array_has_separate_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = inventory_for(Path(tmp), ['{"x":[]}', '{"x":[1]}'])
        self.assertEqual(result["distinct_ordered_schema_signatures"], 2)
        markers = {
            schema["field_schemas"]["x"]["empty"] for schema in result["schemas"]
        }
        self.assertEqual(markers, {True, False})

    def test_duplicate_top_level_key_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.jsonl"
            write_raw(path, ['{"a":1,"a":2}'])
            with self.assertRaisesRegex(SchemaInventoryError, "Duplicate JSON key"):
                inventory_jsonl(path)

    def test_duplicate_nested_key_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.jsonl"
            write_raw(path, ['{"a":{"b":1,"b":2}}'])
            with self.assertRaisesRegex(SchemaInventoryError, "Duplicate JSON key"):
                inventory_jsonl(path)

    def test_invalid_json_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.jsonl"
            write_raw(path, ['{"a":'])
            with self.assertRaisesRegex(SchemaInventoryError, "Invalid JSON"):
                inventory_jsonl(path)

    def test_blank_line_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.jsonl"
            write_raw(path, ['{"a":1}', "", '{"a":2}'])
            with self.assertRaisesRegex(SchemaInventoryError, "Blank JSONL line"):
                inventory_jsonl(path)

    def test_non_object_row_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.jsonl"
            write_raw(path, ["[1,2]"])
            with self.assertRaisesRegex(SchemaInventoryError, "Non-object JSONL row"):
                inventory_jsonl(path)

    def test_nonfinite_constants_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "input.jsonl"
                write_raw(path, [f'{{"x":{token}}}'])
                with self.assertRaisesRegex(SchemaInventoryError, "Non-finite"):
                    inventory_jsonl(path)

    def test_overflow_float_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.jsonl"
            write_raw(path, ['{"x":1e999}'])
            with self.assertRaisesRegex(SchemaInventoryError, "Non-finite"):
                inventory_jsonl(path)

    def test_invalid_utf8_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.jsonl"
            path.write_bytes(b'{"x":"\xff"}\n')
            with self.assertRaisesRegex(SchemaInventoryError, "valid UTF-8"):
                inventory_jsonl(path)

    def test_value_and_id_content_not_leaked(self) -> None:
        secrets = ["SECRET_QUERY_ID_7831", "SECRET_QUESTION_TEXT_9245", "98765.4321"]
        with tempfile.TemporaryDirectory() as tmp:
            result = inventory_for(
                Path(tmp),
                [
                    json.dumps(
                        {
                            "query_id": secrets[0],
                            "question": secrets[1],
                            "score": 98765.4321,
                        }
                    )
                ],
            )
        encoded = json.dumps(result, ensure_ascii=False, sort_keys=True)
        for secret in secrets:
            self.assertNotIn(secret, encoded)

    def test_main_schema_count_and_lexicographic_tie_break(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            majority = inventory_for(
                Path(tmp), ['{"a":1}', '{"a":2}', '{"b":true}']
            )
        count_two = schema_by_count(majority, 2)
        self.assertEqual(majority["main_ordered_signature"], count_two["ordered_signature"])
        with tempfile.TemporaryDirectory() as tmp:
            tied = inventory_for(Path(tmp), ['{"z":1}', '{"a":1}'])
        signatures = [schema["ordered_signature"] for schema in tied["schemas"]]
        self.assertEqual(tied["main_ordered_signature"], min(signatures))

    def test_deterministic_inventory_bytes(self) -> None:
        rows = ['{"b":[1,"x"],"a":{"q":true}}', '{"a":{"q":false},"b":["y",2]}']
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = inventory_for(root, rows)
            second = inventory_jsonl(root / "input.jsonl")
        first_bytes = json.dumps(first, ensure_ascii=True, sort_keys=True).encode()
        second_bytes = json.dumps(second, ensure_ascii=True, sort_keys=True).encode()
        self.assertEqual(first_bytes, second_bytes)

    def test_success_cleans_staging_file_and_writes_exclusive_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_path = root / "input.jsonl"
            output_path = root / "audit.json"
            write_raw(input_path, ['{"a":1}'])
            expected = hashlib.sha256(input_path.read_bytes()).hexdigest().upper()
            result = run_schema_inventory(
                input_path, output_path, expected_input_sha256=expected
            )
            self.assertTrue(output_path.is_file())
            self.assertTrue(result["output_integrity"]["temporary_staging_cleaned"])
            self.assertEqual(list(root.glob(f"{STAGING_PREFIX}*")), [])

    def test_write_failure_cleans_staging_and_partial_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_path = root / "input.jsonl"
            output_path = root / "audit.json"
            write_raw(input_path, ['{"a":1}'])
            with patch.object(
                inventory_module, "_copy_staged_file", side_effect=OSError("injected")
            ):
                with self.assertRaises(OSError):
                    run_schema_inventory(input_path, output_path)
            self.assertFalse(output_path.exists())
            self.assertEqual(list(root.glob(f"{STAGING_PREFIX}*")), [])

    def test_input_hash_drift_leaves_no_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_path = root / "input.jsonl"
            output_path = root / "audit.json"
            write_raw(input_path, ['{"a":1}'])
            with patch.object(
                inventory_module,
                "sha256_file",
                side_effect=["A" * 64, "B" * 64],
            ):
                with self.assertRaisesRegex(SchemaInventoryError, "changed"):
                    run_schema_inventory(input_path, output_path)
            self.assertFalse(output_path.exists())
            self.assertEqual(list(root.glob(f"{STAGING_PREFIX}*")), [])

    def test_existing_output_rejected_before_input_open(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_path = root / "input.jsonl"
            output_path = root / "audit.json"
            write_raw(input_path, ['{"a":1}'])
            output_path.write_text("occupied", encoding="utf-8")
            with patch.object(inventory_module, "sha256_file") as hash_mock:
                with self.assertRaisesRegex(SchemaInventoryError, "absent"):
                    run_schema_inventory(input_path, output_path)
            hash_mock.assert_not_called()

    def test_official_reference_path_blocked_before_open(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "audit.json"
            with patch("pathlib.Path.open", side_effect=AssertionError("must not open")):
                with self.assertRaisesRegex(SchemaInventoryError, "not authorized"):
                    run_schema_inventory(FROZEN_FUTURE_REFERENCE_PATH, output_path)

    def test_inventory_has_no_prohibited_import_or_call(self) -> None:
        source = Path(inventory_module.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported: set[str] = set()
        names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
            elif isinstance(node, ast.Name):
                names.add(node.id)
        prohibited_modules = {
            "stage4b_u1_compare_decisions",
            "stage4b_u1_capture_diagnostic_decisions",
            "stage4b_u1_goldfree_controller",
            "stage4b_u1_goldfree_retrieval",
        }
        prohibited_calls = {
            "compare_decisions_files",
            "run_diagnostic_capture",
            "compute_decisions_only",
            "build_query_decisions",
            "prepare_channels",
        }
        self.assertTrue(imported.isdisjoint(prohibited_modules))
        self.assertTrue(names.isdisjoint(prohibited_calls))


if __name__ == "__main__":
    unittest.main()
