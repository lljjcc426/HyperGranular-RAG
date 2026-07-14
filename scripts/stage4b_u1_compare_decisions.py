"""Fail-closed, decisions-only JSONL comparison for Amendment 5A."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "stage4b_u1_decisions_diagnostic_v2"
DIAGNOSTIC_CHECKPOINT = "stage4b_u1_decisions_diag_v2"
QUERY_HASH_SALT = "stage4b-u1-decisions-diagnostic-v1"
SEMANTIC_FIELDS = ("planned_insert_count", "ordered_rank", "trigger_u1")
UINT64_MASK = (1 << 64) - 1
UINT64_SIGN = 1 << 63


class DecisionsDiagnosticError(ValueError):
    """Raised when an input cannot be compared without weakening a hard gate."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def _reject_constant(value: str) -> None:
    raise DecisionsDiagnosticError(f"Non-finite JSON constant is prohibited: {value}")


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DecisionsDiagnosticError(f"Duplicate JSON object key: {key}")
        result[key] = value
    return result


def strict_json_loads(value: str) -> dict[str, Any]:
    try:
        parsed = json.loads(
            value,
            parse_constant=_reject_constant,
            object_pairs_hook=_strict_object,
        )
    except DecisionsDiagnosticError:
        raise
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise DecisionsDiagnosticError(f"Invalid decisions JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise DecisionsDiagnosticError("Each decisions JSONL row must be an object")
    validate_json_value(parsed)
    return parsed


def json_type_name(value: Any) -> str:
    value_type = type(value)
    if value is None:
        return "null"
    if value_type is bool:
        return "bool"
    if value_type is int:
        return "int"
    if value_type is float:
        return "float"
    if value_type is str:
        return "string"
    if value_type is list:
        return "array"
    if value_type is dict:
        return "object"
    raise DecisionsDiagnosticError(
        f"Unsupported JSON value type: {value_type.__module__}.{value_type.__qualname__}"
    )


def validate_json_value(value: Any, location: str = "root") -> None:
    kind = json_type_name(value)
    if kind == "float" and not math.isfinite(value):
        raise DecisionsDiagnosticError(f"Non-finite float at {location}")
    if kind == "array":
        for index, nested in enumerate(value):
            validate_json_value(nested, f"{location}[{index}]")
    elif kind == "object":
        for key, nested in value.items():
            if type(key) is not str:
                raise DecisionsDiagnosticError(f"Non-string object key at {location}")
            validate_json_value(nested, f"{location}.{key}")


def canonical_json_bytes(value: dict[str, Any]) -> bytes:
    validate_json_value(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def binary64_bits(value: float) -> int:
    if type(value) is not float or not math.isfinite(value):
        raise DecisionsDiagnosticError("ULP input must be a finite binary64 float")
    return struct.unpack(">Q", struct.pack(">d", value))[0]


def binary64_order_key(value: float) -> int:
    """Map big-endian IEEE-754 bits to an unsigned monotonic total-order key."""
    bits = binary64_bits(value)
    if bits & UINT64_SIGN:
        return (~bits) & UINT64_MASK
    return bits | UINT64_SIGN


def binary64_ulp_distance(left: float, right: float) -> int:
    return abs(binary64_order_key(left) - binary64_order_key(right))


def binary64_exact_equal(left: float, right: float) -> bool:
    return binary64_bits(left) == binary64_bits(right)


def _schema_signature(value: Any, *, preserve_order: bool) -> Any:
    kind = json_type_name(value)
    if kind == "object":
        items = value.items() if preserve_order else sorted(value.items())
        return ["object", [[key, _schema_signature(nested, preserve_order=preserve_order)] for key, nested in items]]
    if kind == "array":
        return ["array", [_schema_signature(nested, preserve_order=preserve_order) for nested in value]]
    return kind


def typed_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if type(left) is float:
        return binary64_exact_equal(left, right)
    if type(left) is list:
        return len(left) == len(right) and all(
            typed_equal(a, b) for a, b in zip(left, right, strict=True)
        )
    if type(left) is dict:
        return set(left) == set(right) and all(
            typed_equal(left[key], right[key]) for key in left
        )
    return left == right


def _salted_query_hash(query_id: str) -> str:
    return sha256_bytes(f"{QUERY_HASH_SALT}::{query_id}".encode("utf-8"))


def load_decisions_jsonl(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DecisionsDiagnosticError(f"Decisions file is not UTF-8: {exc}") from exc
    physical_lines = text.splitlines()
    if not physical_lines:
        raise DecisionsDiagnosticError("Decisions file is empty")
    rows: list[dict[str, Any]] = []
    query_ids: list[str] = []
    by_query: dict[str, dict[str, Any]] = {}
    for line_number, line in enumerate(physical_lines, start=1):
        if not line.strip():
            raise DecisionsDiagnosticError(f"Blank JSONL row at line {line_number}")
        row = strict_json_loads(line)
        if "query_id" not in row:
            raise DecisionsDiagnosticError(f"Missing query_id at line {line_number}")
        query_id = row["query_id"]
        if type(query_id) is not str or not query_id:
            raise DecisionsDiagnosticError(f"query_id must be a non-empty string at line {line_number}")
        if query_id in by_query:
            raise DecisionsDiagnosticError(f"Duplicate query_id at line {line_number}")
        rows.append(row)
        query_ids.append(query_id)
        by_query[query_id] = row
    canonical_rows = [canonical_json_bytes(row) + b"\n" for row in rows]
    return {
        "raw": raw,
        "raw_sha256": sha256_bytes(raw),
        "bytes": len(raw),
        "terminal_newline": raw.endswith(b"\n"),
        "rows": rows,
        "query_ids": query_ids,
        "by_query": by_query,
        "canonical_sha256": sha256_bytes(b"".join(canonical_rows)),
    }


def compare_decisions_files(left_path: Path, right_path: Path) -> dict[str, Any]:
    left = load_decisions_jsonl(left_path)
    right = load_decisions_jsonl(right_path)
    left_ids = left["query_ids"]
    right_ids = right["query_ids"]
    left_set = set(left_ids)
    right_set = set(right_ids)
    common_ids = sorted(left_set & right_set)

    field_set_difference_queries = 0
    field_order_difference_queries = 0
    schema_type_difference_queries = 0
    canonical_row_difference_queries = 0
    discrete_differences: dict[str, int] = {}
    float_differences: dict[str, dict[str, Any]] = {}
    semantic_differences = {field: 0 for field in SEMANTIC_FIELDS}
    differing_query_ids: set[str] = set(left_set ^ right_set)

    for query_id in common_ids:
        left_row = left["by_query"][query_id]
        right_row = right["by_query"][query_id]
        if canonical_json_bytes(left_row) != canonical_json_bytes(right_row):
            canonical_row_difference_queries += 1
            differing_query_ids.add(query_id)
        left_fields = set(left_row)
        right_fields = set(right_row)
        if left_fields != right_fields:
            field_set_difference_queries += 1
        if left_fields == right_fields and list(left_row) != list(right_row):
            field_order_difference_queries += 1
        if _schema_signature(left_row, preserve_order=False) != _schema_signature(
            right_row, preserve_order=False
        ):
            schema_type_difference_queries += 1

        for field in sorted(left_fields & right_fields):
            left_value = left_row[field]
            right_value = right_row[field]
            if field in SEMANTIC_FIELDS and not typed_equal(left_value, right_value):
                semantic_differences[field] += 1
            if type(left_value) is float and type(right_value) is float:
                if not binary64_exact_equal(left_value, right_value):
                    details = float_differences.setdefault(
                        field,
                        {
                            "count": 0,
                            "max_absolute_error": 0.0,
                            "max_ulp_distance": 0,
                            "signed_zero_difference_count": 0,
                        },
                    )
                    details["count"] += 1
                    details["max_absolute_error"] = max(
                        details["max_absolute_error"], abs(left_value - right_value)
                    )
                    details["max_ulp_distance"] = max(
                        details["max_ulp_distance"],
                        binary64_ulp_distance(left_value, right_value),
                    )
                    if left_value == 0.0 and right_value == 0.0:
                        details["signed_zero_difference_count"] += 1
            elif not typed_equal(left_value, right_value):
                discrete_differences[field] = discrete_differences.get(field, 0) + 1

    raw_equal = left["raw"] == right["raw"]
    canonical_equal = left["canonical_sha256"] == right["canonical_sha256"]
    query_order_equal = left_ids == right_ids
    query_set_equal = left_set == right_set
    first_difference_hash = (
        _salted_query_hash(sorted(differing_query_ids)[0])
        if differing_query_ids
        else None
    )
    if raw_equal:
        status = "IDENTICAL_BYTES"
    elif canonical_equal:
        status = "CANONICAL_EQUAL_RAW_DIFFERENT"
    else:
        status = "DECISIONS_DIFFERENT"
    return {
        "schema_version": SCHEMA_VERSION,
        "diagnostic_checkpoint": DIAGNOSTIC_CHECKPOINT,
        "status": status,
        "byte_equivalent": raw_equal,
        "canonical_equal": canonical_equal,
        "comparison_layers": {
            "raw_file": {
                "left_sha256": left["raw_sha256"],
                "right_sha256": right["raw_sha256"],
                "left_bytes": left["bytes"],
                "right_bytes": right["bytes"],
                "left_terminal_newline": left["terminal_newline"],
                "right_terminal_newline": right["terminal_newline"],
            },
            "row_identity": {
                "left_rows": len(left_ids),
                "right_rows": len(right_ids),
                "query_id_set_equal": query_set_equal,
                "query_id_order_equal": query_order_equal,
                "missing_from_left_count": len(right_set - left_set),
                "missing_from_right_count": len(left_set - right_set),
            },
            "canonical_json": {
                "left_sha256": left["canonical_sha256"],
                "right_sha256": right["canonical_sha256"],
                "different_query_count": canonical_row_difference_queries,
            },
            "schema": {
                "field_set_difference_query_count": field_set_difference_queries,
                "field_order_difference_query_count": field_order_difference_queries,
                "type_or_structure_difference_query_count": schema_type_difference_queries,
            },
            "discrete_values": dict(sorted(discrete_differences.items())),
            "finite_float": dict(sorted(float_differences.items())),
            "decision_semantics": semantic_differences,
        },
        "first_difference_query_id_salted_sha256": first_difference_hash,
        "raw_query_ids_emitted": False,
        "raw_decision_rows_emitted": False,
        "rankings_accessed": False,
        "policy_accessed": False,
        "gold_accessed": False,
        "byte_equivalence_gate_relaxed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left-decisions", required=True, type=Path)
    parser.add_argument("--right-decisions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = compare_decisions_files(args.left_decisions, args.right_decisions)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
