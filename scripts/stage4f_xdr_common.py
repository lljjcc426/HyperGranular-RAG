"""Shared contracts for Stage4F-XDR cross-dataset replication."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "stage4f_xdr_v1"
DATASET = "musique_ans_v1_0_train"
SELECTION_SALT = "stage4f_xdr_v1\0"
SAMPLE_SIZE = 3000
BOOTSTRAP_SEED = 20260723
BOOTSTRAP_ITERATIONS = 10_000

SOURCE_BYTES = 241_046_755
SOURCE_SHA256 = "83A75B1E11E4E9BB8F8308E72AC40CA617AE4431B3A0D955B61CAB259248490A"
SOURCE_ZIP_BYTES = 272_049_578
SOURCE_ZIP_SHA256 = "98F839BF2FD5319F5C688AED77901A6D5C30B3B9F9F691AB9A8ECAFB045EE0CD"
SOURCE_REPOSITORY_COMMIT = "922ac98f19a201998dbdae6d7f2887a5258dbdeb"
OFFICIAL_EVALUATOR_SHA256 = "F5FE66AE61DBEA5172CBA9D428D9924A5811F3457EDC945FC1D81369C30E74B7"
OFFICIAL_ANSWER_METRIC_SHA256 = "10368F619B4D5EF5D83748C05A96C0AFD332A14AB5C010740C98D58DFAEFE974"

ENCODER_ID = "sentence-transformers/all-MiniLM-L6-v2"
ENCODER_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
GENERATOR_ID = "Qwen/Qwen2.5-1.5B-Instruct"
GENERATOR_REVISION = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"

GOLD_FIELD_NAMES = {
    "answer",
    "answer_aliases",
    "answers",
    "gold",
    "gold_answer",
    "gold_evidence",
    "gold_unit_ids",
    "is_gold",
    "is_supporting",
    "paragraph_support_idx",
    "question_decomposition",
    "supporting_evidence",
    "supporting_facts",
    "supporting_paragraph_indices",
    "supporting_unit_ids",
}

_SENTENCE_BOUNDARY_RE = re.compile(
    r'([.!?][\"”’]?)\s+(?=(?:[\"“‘]?[A-Z0-9]))'
)
_SHA256_RE = re.compile(r"[0-9A-F]{64}")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_identity(path: Path) -> dict[str, Any]:
    return {"bytes": path.stat().st_size, "sha256": sha256_file(path)}


def validate_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value.upper()) is None:
        raise ValueError(f"{label} must be a SHA-256 string")
    return value.upper()


def assert_file_identity(path: Path, expected: dict[str, Any], label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"{label} is missing: {path}")
    expected_bytes = require_json_int(expected.get("bytes"), f"{label}.bytes")
    expected_sha = validate_sha256(expected.get("sha256"), f"{label}.sha256")
    actual = file_identity(path)
    if actual != {"bytes": expected_bytes, "sha256": expected_sha}:
        raise ValueError(f"{label} identity differs: {actual}")


def render_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def render_jsonl(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(
        (
            json.dumps(
                row,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
        for row in rows
    )


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number} must be a JSON object")
            rows.append(value)
    return rows


def require_native_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty JSON string")
    return value


def require_json_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be a JSON integer")
    return value


def require_json_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be a JSON boolean")
    return value


def require_finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a JSON number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def normalize_space(value: Any, label: str) -> str:
    return " ".join(require_native_string(value, label).split())


def split_sentences(value: Any, label: str) -> list[str]:
    """Pinned regex splitter v1; it uses source text only and never Gold labels."""
    text = normalize_space(value, label)
    marked = _SENTENCE_BOUNDARY_RE.sub(r"\1\n", text)
    return [part.strip() for part in marked.split("\n") if part.strip()]


def selection_key(native_query_id: str) -> tuple[bytes, str]:
    native_query_id = require_native_string(native_query_id, "native_query_id")
    payload = f"{SELECTION_SALT}{DATASET}\0{native_query_id}".encode("utf-8")
    return hashlib.sha256(payload).digest(), native_query_id


def id_digest(values: Iterable[str]) -> str:
    return sha256_bytes(("\n".join(values) + "\n").encode("utf-8"))


def assert_no_gold_fields(value: Any, label: str) -> None:
    if isinstance(value, dict):
        forbidden = sorted(set(value) & GOLD_FIELD_NAMES)
        if forbidden:
            raise ValueError(f"{label} contains prohibited Gold fields: {forbidden}")
        for key, child in value.items():
            assert_no_gold_fields(child, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_no_gold_fields(child, f"{label}[{index}]")


def method_order(query_id: str) -> tuple[str, str]:
    digest = hashlib.sha256(require_native_string(query_id, "query_id").encode()).digest()
    return (
        ("DENSE_TOP20", "STATIC_Q25_TOP20")
        if digest[0] % 2 == 0
        else ("STATIC_Q25_TOP20", "DENSE_TOP20")
    )


def write_new_files_atomically(outputs: Iterable[tuple[Path, bytes]]) -> None:
    pairs = list(outputs)
    if not pairs:
        raise ValueError("No outputs were declared")
    targets = [path.resolve() for path, _ in pairs]
    if len(set(targets)) != len(targets):
        raise ValueError("Duplicate output path")
    pending_paths = [path.with_name(path.name + ".pending") for path, _ in pairs]
    for path, pending in zip((path for path, _ in pairs), pending_paths, strict=True):
        if path.exists() or pending.exists():
            raise FileExistsError(f"Refusing to overwrite artifact: {path}")
    promoted: list[Path] = []
    try:
        for (path, payload), pending in zip(pairs, pending_paths, strict=True):
            path.parent.mkdir(parents=True, exist_ok=True)
            with pending.open("xb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        for (path, _), pending in zip(pairs, pending_paths, strict=True):
            os.replace(pending, path)
            promoted.append(path)
    except Exception:
        for pending in pending_paths:
            pending.unlink(missing_ok=True)
        for path in promoted:
            path.unlink(missing_ok=True)
        raise


def assert_implementation_binding(config: dict[str, Any], root: Path) -> None:
    binding = config.get("implementation")
    if not isinstance(binding, dict):
        raise ValueError("implementation binding is missing")
    files = binding.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("implementation.files binding is missing")
    for relative, expected_sha in files.items():
        relative = require_native_string(relative, "implementation path")
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ValueError("implementation path is unsafe")
        path = root / relative
        expected_sha = validate_sha256(expected_sha, f"implementation.files.{relative}")
        if sha256_file(path) != expected_sha:
            raise ValueError(f"implementation file differs: {relative}")

