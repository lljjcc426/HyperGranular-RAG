"""Build a deterministic, value-free schema inventory for decisions JSONL."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, BinaryIO


SCHEMA_INVENTORY_VERSION = "stage4b_u1_reference_schema_inventory_v1"
FROZEN_FUTURE_REFERENCE_PATH = Path(
    r"E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_decisions.jsonl"
)
FROZEN_FUTURE_REFERENCE_SHA256 = (
    "6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7"
)
FUTURE_5C_B_AUTHORIZATION_TOKEN = (
    "APPROVE_STAGE4B_U1_D_AMENDMENT_5C_B_SINGLE_REFERENCE_SCHEMA_SCAN"
)
STAGING_PREFIX = ".stage4b_u1_schema_inventory_"
_SHA256_PATTERN = re.compile(r"[0-9A-Fa-f]{64}")


class SchemaInventoryError(ValueError):
    """Raised when input or output violates the frozen inventory contract."""


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SchemaInventoryError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonfinite_constant(token: str) -> None:
    raise SchemaInventoryError(f"Non-finite JSON number is prohibited: {token}")


def _validate_json_value(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, (bool, str, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise SchemaInventoryError(f"Non-finite number at {path}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_value(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _validate_json_value(item, f"{path}/{_pointer_escape(key)}")
        return
    raise SchemaInventoryError(f"Unsupported JSON value type at {path}")


def strict_json_object(raw: str, line_number: int) -> dict[str, Any]:
    if not raw.strip():
        raise SchemaInventoryError(f"Blank JSONL line at line {line_number}")
    try:
        value = json.loads(
            raw,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_nonfinite_constant,
        )
    except SchemaInventoryError:
        raise
    except json.JSONDecodeError as exc:
        raise SchemaInventoryError(
            f"Invalid JSON at line {line_number}: column {exc.colno}"
        ) from exc
    if not isinstance(value, dict):
        raise SchemaInventoryError(f"Non-object JSONL row at line {line_number}")
    _validate_json_value(value)
    return value


def canonical_schema_bytes(schema: dict[str, Any]) -> bytes:
    return json.dumps(
        schema,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def schema_digest(schema: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_schema_bytes(schema)).hexdigest().upper()


def _schema_node(value: Any, *, order_sensitive: bool) -> dict[str, Any]:
    if value is None:
        return {"type": "null"}
    if isinstance(value, bool):
        return {"type": "bool"}
    if isinstance(value, int):
        return {"type": "integer"}
    if isinstance(value, float):
        if not math.isfinite(value):
            raise SchemaInventoryError("Non-finite number reached schema builder")
        return {"type": "finite_number"}
    if isinstance(value, str):
        return {"type": "string"}
    if isinstance(value, list):
        unique: dict[bytes, dict[str, Any]] = {}
        for item in value:
            node = _schema_node(item, order_sensitive=order_sensitive)
            unique[canonical_schema_bytes(node)] = node
        keys = sorted(unique)
        return {
            "type": "array",
            "empty": not keys,
            "element_schemas": [unique[key] for key in keys],
        }
    if isinstance(value, dict):
        fields = [
            {
                "name": key,
                "schema": _schema_node(item, order_sensitive=order_sensitive),
            }
            for key, item in value.items()
        ]
        if not order_sensitive:
            fields.sort(key=lambda item: item["name"])
        return {"type": "object", "fields": fields}
    raise SchemaInventoryError("Unsupported value reached schema builder")


def _to_structural(schema: dict[str, Any]) -> dict[str, Any]:
    schema_type = schema["type"]
    if schema_type == "object":
        fields = [
            {"name": item["name"], "schema": _to_structural(item["schema"])}
            for item in schema["fields"]
        ]
        fields.sort(key=lambda item: item["name"])
        return {"type": "object", "fields": fields}
    if schema_type == "array":
        unique: dict[bytes, dict[str, Any]] = {}
        for item in schema["element_schemas"]:
            structural = _to_structural(item)
            unique[canonical_schema_bytes(structural)] = structural
        keys = sorted(unique)
        return {
            "type": "array",
            "empty": schema["empty"],
            "element_schemas": [unique[key] for key in keys],
        }
    return {"type": schema_type}


def _pointer_escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _array_element_path(parent: str, schema: dict[str, Any]) -> str:
    return f"{parent}/*:{schema_digest(_to_structural(schema))}"


def _flatten_fields(
    schema: dict[str, Any], path: str = "$"
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    if schema["type"] == "object":
        for item in schema["fields"]:
            child_path = f"{path}/{_pointer_escape(item['name'])}"
            result[child_path] = item["schema"]
            result.update(_flatten_fields(item["schema"], child_path))
    elif schema["type"] == "array":
        for item in schema["element_schemas"]:
            result.update(_flatten_fields(item, _array_element_path(path, item)))
    return result


def _collect_object_orders(
    schema: dict[str, Any], path: str = "$"
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    if schema["type"] == "object":
        result[path] = {
            "field_order": [item["name"] for item in schema["fields"]],
            "structural_digest": schema_digest(_to_structural(schema)),
        }
        for item in schema["fields"]:
            child_path = f"{path}/{_pointer_escape(item['name'])}"
            result.update(_collect_object_orders(item["schema"], child_path))
    elif schema["type"] == "array":
        for item in schema["element_schemas"]:
            result.update(
                _collect_object_orders(item, _array_element_path(path, item))
            )
    return result


def _schema_differences(
    main_schema: dict[str, Any], current_schema: dict[str, Any]
) -> dict[str, list[str]]:
    main_structural = _to_structural(main_schema)
    current_structural = _to_structural(current_schema)
    main_fields = _flatten_fields(main_structural)
    current_fields = _flatten_fields(current_structural)
    main_paths = set(main_fields)
    current_paths = set(current_fields)
    type_changed: list[str] = []
    nesting_changed: list[str] = []
    for path in sorted(main_paths & current_paths):
        main_node = main_fields[path]
        current_node = current_fields[path]
        if main_node["type"] != current_node["type"]:
            type_changed.append(path)
        elif main_node["type"] in {"object", "array"} and schema_digest(
            main_node
        ) != schema_digest(current_node):
            nesting_changed.append(path)

    main_orders = _collect_object_orders(main_schema)
    current_orders = _collect_object_orders(current_schema)
    order_only: list[str] = []
    for path in sorted(set(main_orders) & set(current_orders)):
        main_entry = main_orders[path]
        current_entry = current_orders[path]
        if (
            main_entry["structural_digest"] == current_entry["structural_digest"]
            and main_entry["field_order"] != current_entry["field_order"]
        ):
            order_only.append(path)
    return {
        "added_fields": sorted(current_paths - main_paths),
        "removed_fields": sorted(main_paths - current_paths),
        "type_changed_fields": type_changed,
        "nesting_changed_fields": nesting_changed,
        "order_only_fields": order_only,
    }


def _top_level_field_metadata(
    ordered_schema: dict[str, Any], structural_schema: dict[str, Any]
) -> tuple[list[str], list[str], dict[str, str], dict[str, dict[str, Any]]]:
    ordered_names = [item["name"] for item in ordered_schema["fields"]]
    structural_fields = {
        item["name"]: item["schema"] for item in structural_schema["fields"]
    }
    field_types = {
        name: structural_fields[name]["type"] for name in sorted(structural_fields)
    }
    field_schemas = {name: structural_fields[name] for name in sorted(structural_fields)}
    return ordered_names, sorted(structural_fields), field_types, field_schemas


def inventory_jsonl(path: Path) -> dict[str, Any]:
    aggregates: dict[str, dict[str, Any]] = {}
    total_rows = 0
    try:
        with path.open("r", encoding="utf-8", errors="strict", newline="") as handle:
            for line_number, raw in enumerate(handle, start=1):
                row = strict_json_object(raw, line_number)
                ordered_schema = _schema_node(row, order_sensitive=True)
                structural_schema = _schema_node(row, order_sensitive=False)
                ordered_signature = schema_digest(ordered_schema)
                structural_signature = schema_digest(structural_schema)
                entry = aggregates.setdefault(
                    ordered_signature,
                    {
                        "ordered_schema": ordered_schema,
                        "structural_schema": structural_schema,
                        "structural_signature": structural_signature,
                        "row_count": 0,
                        "first_line": line_number,
                        "last_line": line_number,
                    },
                )
                entry["row_count"] += 1
                entry["last_line"] = line_number
                total_rows += 1
    except UnicodeDecodeError as exc:
        raise SchemaInventoryError("Input is not valid UTF-8") from exc
    if total_rows == 0:
        raise SchemaInventoryError("JSONL input contains no rows")

    main_signature = min(
        aggregates,
        key=lambda signature: (-aggregates[signature]["row_count"], signature),
    )
    main_schema = aggregates[main_signature]["ordered_schema"]
    schemas: list[dict[str, Any]] = []
    for ordered_signature in sorted(aggregates):
        entry = aggregates[ordered_signature]
        field_names, field_name_set, field_types, field_schemas = (
            _top_level_field_metadata(
                entry["ordered_schema"], entry["structural_schema"]
            )
        )
        schemas.append(
            {
                "ordered_signature": ordered_signature,
                "structural_signature": entry["structural_signature"],
                "row_count": entry["row_count"],
                "first_line": entry["first_line"],
                "last_line": entry["last_line"],
                "field_names": field_names,
                "field_name_set": field_name_set,
                "field_types": field_types,
                "field_schemas": field_schemas,
                "ordered_schema": entry["ordered_schema"],
                "structural_schema": entry["structural_schema"],
                "differences_from_main": _schema_differences(
                    main_schema, entry["ordered_schema"]
                ),
            }
        )
    return {
        "schema_inventory_version": SCHEMA_INVENTORY_VERSION,
        "status": "SCHEMA_INVENTORY_COMPLETE",
        "value_free_schema_metadata": True,
        "total_rows": total_rows,
        "distinct_ordered_schema_signatures": len(aggregates),
        "distinct_structural_schema_signatures": len(
            {entry["structural_signature"] for entry in aggregates.values()}
        ),
        "main_ordered_signature": main_signature,
        "main_schema_selection": (
            "MAX_ROW_COUNT_OVER_ORDERED_SIGNATURE_THEN_LEXICOGRAPHIC_ORDERED_SIGNATURE"
        ),
        "schemas": schemas,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _normalized_path(path: Path) -> str:
    return os.path.normcase(os.path.abspath(os.fspath(path)))


def _normalize_expected_sha256(value: str | None) -> str | None:
    if value is None:
        return None
    if not _SHA256_PATTERN.fullmatch(value):
        raise SchemaInventoryError("Expected SHA-256 must contain exactly 64 hex digits")
    return value.upper()


def _validate_access_boundary(
    input_path: Path,
    expected_sha256: str | None,
    official_authorization_token: str | None,
) -> str | None:
    expected = _normalize_expected_sha256(expected_sha256)
    is_official = _normalized_path(input_path) == _normalized_path(
        FROZEN_FUTURE_REFERENCE_PATH
    )
    if is_official:
        if official_authorization_token != FUTURE_5C_B_AUTHORIZATION_TOKEN:
            raise SchemaInventoryError(
                "Official reference schema scan is not authorized under Amendment 5C-A"
            )
        if expected != FROZEN_FUTURE_REFERENCE_SHA256:
            raise SchemaInventoryError("Official reference SHA-256 is not frozen exactly")
    elif official_authorization_token is not None:
        raise SchemaInventoryError("Official authorization token cannot be used synthetically")
    return expected


def _copy_staged_file(staged_path: Path, output_handle: BinaryIO) -> None:
    with staged_path.open("rb") as staged_handle:
        for chunk in iter(lambda: staged_handle.read(1024 * 1024), b""):
            output_handle.write(chunk)


def exclusive_write_json(path: Path, payload: dict[str, Any]) -> None:
    if not path.parent.is_dir():
        raise SchemaInventoryError("Output parent must already exist as a directory")
    if path.exists() or path.is_symlink():
        raise SchemaInventoryError("Output path must not already exist")
    encoded = (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        + "\n"
    ).encode("utf-8")
    staged_path: Path | None = None
    output_created = False
    open_fd: int | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=STAGING_PREFIX,
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as staged_handle:
            staged_path = Path(staged_handle.name)
            staged_handle.write(encoded)
            staged_handle.flush()
            os.fsync(staged_handle.fileno())
        open_fd = os.open(
            path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0),
            0o600,
        )
        output_created = True
        with os.fdopen(open_fd, "wb") as output_handle:
            open_fd = None
            _copy_staged_file(staged_path, output_handle)
            output_handle.flush()
            os.fsync(output_handle.fileno())
    except Exception:
        if open_fd is not None:
            os.close(open_fd)
        if output_created:
            path.unlink(missing_ok=True)
        raise
    finally:
        if staged_path is not None:
            staged_path.unlink(missing_ok=True)


def run_schema_inventory(
    input_path: Path,
    output_path: Path,
    *,
    expected_input_sha256: str | None = None,
    official_authorization_token: str | None = None,
) -> dict[str, Any]:
    expected = _validate_access_boundary(
        input_path, expected_input_sha256, official_authorization_token
    )
    if _normalized_path(input_path) == _normalized_path(output_path):
        raise SchemaInventoryError("Input and output paths must differ")
    if output_path.exists() or output_path.is_symlink():
        raise SchemaInventoryError("Output path must be absent before input access")
    if input_path.is_symlink() or not input_path.is_file():
        raise SchemaInventoryError("Input must exist as a regular non-symlink file")
    before_sha256 = sha256_file(input_path)
    if expected is not None and before_sha256 != expected:
        raise SchemaInventoryError("Input SHA-256 does not match the expected value")
    inventory = inventory_jsonl(input_path)
    after_sha256 = sha256_file(input_path)
    if after_sha256 != before_sha256:
        raise SchemaInventoryError("Input SHA-256 changed during schema inventory")
    if expected is not None and after_sha256 != expected:
        raise SchemaInventoryError("Input SHA-256 drifted from the expected value")
    inventory["source_integrity"] = {
        "sha256_before": before_sha256,
        "sha256_after": after_sha256,
        "unchanged": True,
    }
    inventory["output_integrity"] = {
        "exclusive_create": True,
        "temporary_staging_cleaned": True,
    }
    exclusive_write_json(output_path, inventory)
    return inventory


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-input-sha256")
    parser.add_argument("--official-authorization-token")
    args = parser.parse_args()
    try:
        run_schema_inventory(
            args.input,
            args.output,
            expected_input_sha256=args.expected_input_sha256,
            official_authorization_token=args.official_authorization_token,
        )
    except (OSError, SchemaInventoryError) as exc:
        sys.stderr.write(f"Schema inventory failed: {exc}\n")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
