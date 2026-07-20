"""Shared deterministic contracts for Stage4E static-HGRAG E2E evaluation."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Iterable, Sequence


SCHEMA_VERSION = "stage4e_e2e_v1"
DATASET = "hotpotqa_train_distractor_v1_1"
SELECTION_SALT = "stage4e_e2e_v1\0"
SAMPLE_SIZE = 1000
BOOTSTRAP_SEED = 20260720
BOOTSTRAP_ITERATIONS = 10_000

SOURCE_BYTES = 566_426_227
SOURCE_SHA256 = "26650CF50234EF5FB2E664ED70BBECDFD87815E6BFFC257E068EFEA5CF7CD316"
SOURCE_CANONICAL_URL = (
    "http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_train_v1.1.json"
)
SOURCE_TRANSPORT_URL = (
    "https://huggingface.co/datasets/namlh2004/hotpotqa/resolve/"
    "7e54db4656209750ff487f6fdf8e39a66dba136b/hotpot_train_v1.json?download=true"
)
SOURCE_TRANSPORT_REVISION = "7e54db4656209750ff487f6fdf8e39a66dba136b"

ENCODER_ID = "sentence-transformers/all-MiniLM-L6-v2"
ENCODER_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
GENERATOR_ID = "Qwen/Qwen2.5-1.5B-Instruct"
GENERATOR_REVISION = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"

BLIND_PROHIBITED_KEYS = {
    "answer",
    "answers",
    "gold",
    "gold_answer",
    "gold_evidence",
    "gold_unit_ids",
    "is_gold",
    "level",
    "supporting_facts",
    "type",
}


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


def render_json(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
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
                raise ValueError(f"{path}:{line_number}: JSONL row must be an object")
            rows.append(value)
    return rows


def require_native_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a native non-empty string")
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
        raise ValueError(f"{label} must be a finite JSON number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def id_digest(values: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(require_native_string(value, "ID digest value").encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest().upper()


def validate_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9A-Fa-f]{64}", value) is None:
        raise ValueError(f"{label} must be a 64-character SHA-256")
    return value.upper()


def assert_file_identity(path: Path, expected: dict[str, Any], label: str) -> None:
    if set(expected) != {"bytes", "sha256"}:
        raise ValueError(f"{label} identity must contain exactly bytes and sha256")
    expected_bytes = require_json_int(expected["bytes"], f"{label}.bytes")
    if expected_bytes < 0:
        raise ValueError(f"{label}.bytes must be non-negative")
    expected_sha = validate_sha256(expected["sha256"], f"{label}.sha256")
    actual = file_identity(path)
    if actual != {"bytes": expected_bytes, "sha256": expected_sha}:
        raise ValueError(f"{label} identity mismatch: expected={expected}, actual={actual}")


def method_order(query_id_value: str) -> tuple[str, str]:
    query_id_value = require_native_string(query_id_value, "query_id")
    parity = hashlib.sha256(query_id_value.encode("utf-8")).digest()[0] & 1
    return (
        ("DENSE_TOP20", "STATIC_Q25_TOP20")
        if parity == 0
        else ("STATIC_Q25_TOP20", "DENSE_TOP20")
    )


def assert_implementation_binding(config: dict[str, Any], repository_root: Path) -> None:
    implementation = config.get("implementation")
    if not isinstance(implementation, dict):
        raise ValueError("implementation binding is missing")
    commit = implementation.get("code_commit")
    if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise ValueError("implementation.code_commit must be a full lowercase Git SHA")
    files = implementation.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("implementation.files binding is missing")
    for relative, expected_sha in sorted(files.items()):
        relative = require_native_string(relative, "implementation file path")
        relative_path = Path(relative)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ValueError(f"Invalid implementation file path: {relative}")
        expected = validate_sha256(expected_sha, f"implementation.files.{relative}")
        path = repository_root / relative_path
        if not path.is_file() or sha256_file(path) != expected:
            raise ValueError(f"Implementation file binding differs: {relative}")


def selection_key(sample_id: str) -> str:
    sample_id = require_native_string(sample_id, "sample_id")
    return hashlib.sha256((SELECTION_SALT + sample_id).encode("utf-8")).hexdigest().upper()


def query_id(sample_id: str) -> str:
    return f"{DATASET}::{require_native_string(sample_id, 'sample_id')}"


def normalize_sentence(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("sentence must be a native JSON string")
    return " ".join(value.split())


def assert_no_prohibited_keys(value: Any, label: str) -> None:
    def recurse(item: Any, path: str) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                if str(key).lower() in BLIND_PROHIBITED_KEYS:
                    raise ValueError(f"{label} contains prohibited key at {path}.{key}")
                recurse(child, f"{path}.{key}")
        elif isinstance(item, list):
            for index, child in enumerate(item):
                recurse(child, f"{path}[{index}]")

    recurse(value, label)


def write_new_files_atomically(files: Sequence[tuple[Path, bytes]]) -> None:
    """Write a no-overwrite multi-file transaction with adjacent pending files."""

    if not files:
        raise ValueError("Atomic write transaction is empty")
    targets = [path for path, _ in files]
    if len(targets) != len(set(targets)):
        raise ValueError("Atomic write transaction has duplicate targets")
    for target in targets:
        if target.exists():
            raise FileExistsError(f"Refusing to overwrite existing artifact: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
    pending = [target.with_name(target.name + ".pending") for target in targets]
    for path in pending:
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite existing pending artifact: {path}")

    promoted: list[Path] = []
    try:
        for path, (_, payload) in zip(pending, files, strict=True):
            with path.open("xb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        for path, (_, payload) in zip(pending, files, strict=True):
            if path.stat().st_size != len(payload) or sha256_file(path) != sha256_bytes(payload):
                raise RuntimeError(f"Pending artifact identity mismatch: {path}")
        for path, target in zip(pending, targets, strict=True):
            os.replace(path, target)
            promoted.append(target)
    except Exception:
        for path in pending:
            path.unlink(missing_ok=True)
        for target in promoted:
            target.unlink(missing_ok=True)
        raise
