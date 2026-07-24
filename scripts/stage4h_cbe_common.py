"""Shared deterministic contracts for Stage4H-CBE."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Iterable, Sequence


SCHEMA_VERSION = "stage4h_cbe_v1"
ARTIFACT_STEM = "stage4h_cbe_hotpot1000_musique1500_v1"
HOTPOT_DATASET = "hotpotqa_train_distractor_v1_1"
MUSIQUE_DATASET = "musique_ans_v1_0_train"
DATASETS = (HOTPOT_DATASET, MUSIQUE_DATASET)
DATASET_KEYS = {HOTPOT_DATASET: "hotpotqa", MUSIQUE_DATASET: "musique"}
SAMPLE_SIZES = {HOTPOT_DATASET: 1000, MUSIQUE_DATASET: 1500}
SELECTION_SALT = "stage4h_cbe_v1\0"
RERUN_SALT = "stage4h_cbe_rerun_v1\0"
RERUN_QUERIES_PER_DATASET = 100
BOOTSTRAP_SEED = 20260725
BOOTSTRAP_ITERATIONS = 10_000

METHODS = (
    "DENSE_TOP20",
    "STATIC_Q25_FULL",
    "Q25_NO_PROTECTION",
    "Q25_NO_FACET_HYPEREDGE",
    "BM25_TOP20",
    "DENSE_BM25_HYBRID_TOP20",
    "STRONG_DENSE_TOP20",
)
PRIMARY_COMPARATORS = (
    "DENSE_TOP20",
    "STRONG_DENSE_TOP20",
    "Q25_NO_PROTECTION",
    "Q25_NO_FACET_HYPEREDGE",
)

MINILM_ID = "sentence-transformers/all-MiniLM-L6-v2"
MINILM_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
STRONG_DENSE_ID = "BAAI/bge-large-en-v1.5"
STRONG_DENSE_REVISION = "d4aa6901d3a41ba39fb536a557fa166f842b0e09"
STRONG_DENSE_QUERY_PREFIX = (
    "Represent this sentence for searching relevant passages: "
)
GENERATOR_ID = "Qwen/Qwen2.5-1.5B-Instruct"
GENERATOR_REVISION = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"

SYSTEM_MESSAGE = (
    "Answer the question using only the provided evidence. Return only the "
    "shortest final answer. If the evidence is insufficient, return UNKNOWN."
)

BLIND_PROHIBITED_KEYS = {
    "answer",
    "answers",
    "answer_aliases",
    "decomposition",
    "difficulty",
    "gold",
    "gold_answer",
    "gold_evidence",
    "gold_unit_ids",
    "hop_count",
    "is_gold",
    "is_supporting",
    "level",
    "question_decomposition",
    "supporting_facts",
    "supporting_paragraph_indices",
    "supporting_unit_ids",
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
                raise ValueError(f"{path}:{line_number}: row must be a JSON object")
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


def validate_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9A-Fa-f]{64}", value) is None:
        raise ValueError(f"{label} must be a 64-character SHA-256")
    return value.upper()


def assert_file_identity(path: Path, expected: dict[str, Any], label: str) -> None:
    if not isinstance(expected, dict) or set(expected) < {"bytes", "sha256"}:
        raise ValueError(f"{label} identity must contain bytes and sha256")
    expected_bytes = require_json_int(expected["bytes"], f"{label}.bytes")
    expected_sha = validate_sha256(expected["sha256"], f"{label}.sha256")
    actual = file_identity(path)
    if actual != {"bytes": expected_bytes, "sha256": expected_sha}:
        raise ValueError(f"{label} identity mismatch: expected={expected}, actual={actual}")


def id_digest(values: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(require_native_string(value, "ID").encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest().upper()


def selection_key(dataset: str, native_id: str) -> tuple[str, str]:
    dataset = require_native_string(dataset, "dataset key")
    native_id = require_native_string(native_id, "native ID")
    digest = hashlib.sha256(
        (SELECTION_SALT + dataset + "\0" + native_id).encode("utf-8")
    ).hexdigest()
    return digest, native_id


def rerun_selection_key(dataset: str, query_id: str) -> tuple[str, str]:
    dataset = require_native_string(dataset, "dataset")
    query_id = require_native_string(query_id, "query_id")
    digest = hashlib.sha256(
        (RERUN_SALT + dataset + "\0" + query_id).encode("utf-8")
    ).hexdigest()
    return digest, query_id


def method_order(query_id: str) -> tuple[str, ...]:
    query_id = require_native_string(query_id, "query_id")
    digest = hashlib.sha256(query_id.encode("utf-8")).digest()
    offset = digest[0] % len(METHODS)
    ordered = METHODS[offset:] + METHODS[:offset]
    return tuple(reversed(ordered)) if digest[1] & 1 else ordered


def assert_no_gold_fields(value: Any, label: str) -> None:
    def recurse(item: Any, path: str) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                if not isinstance(key, str):
                    raise ValueError(f"{label} contains non-string key at {path}")
                if key.lower() in BLIND_PROHIBITED_KEYS:
                    raise ValueError(f"{label} contains prohibited field at {path}.{key}")
                recurse(child, f"{path}.{key}")
        elif isinstance(item, list):
            for index, child in enumerate(item):
                recurse(child, f"{path}[{index}]")

    recurse(value, label)


def normalize_sentence(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("sentence must be a native JSON string")
    return " ".join(value.split())


def path_from_config(config: dict[str, Any], key: str) -> Path:
    paths = config.get("paths")
    if not isinstance(paths, dict):
        raise ValueError("config.paths must be an object")
    return Path(require_native_string(paths.get(key), f"paths.{key}"))


def validate_snapshot(snapshot: Path, model: dict[str, Any], label: str) -> None:
    files = model.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError(f"{label}.files must be non-empty")
    expected_manifest_sha = validate_sha256(
        model.get("files_sha256"), f"{label}.files_sha256"
    )
    if sha256_bytes(render_json(files)) != expected_manifest_sha:
        raise ValueError(f"{label}.files_sha256 differs from the file manifest")
    for index, row in enumerate(files):
        if not isinstance(row, dict) or set(row) != {"bytes", "path", "sha256"}:
            raise ValueError(f"{label}.files[{index}] contract differs")
        relative = require_native_string(row["path"], f"{label}.files[{index}].path")
        relative_path = Path(relative)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ValueError(f"{label}.files[{index}].path is unsafe")
        assert_file_identity(
            snapshot / relative_path,
            {"bytes": row["bytes"], "sha256": row["sha256"]},
            f"{label}.files[{index}]",
        )


def assert_implementation_binding(
    config: dict[str, Any], repository_root: Path
) -> None:
    implementation = config.get("implementation")
    if not isinstance(implementation, dict):
        raise ValueError("implementation binding is missing")
    commit = implementation.get("code_commit")
    if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise ValueError("implementation.code_commit must be a full Git SHA")
    files = implementation.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("implementation.files binding is missing")
    for relative, expected_sha in sorted(files.items()):
        relative = require_native_string(relative, "implementation path")
        relative_path = Path(relative)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ValueError(f"unsafe implementation path: {relative}")
        expected_sha = validate_sha256(expected_sha, f"implementation.{relative}")
        actual = repository_root / relative_path
        if not actual.is_file() or sha256_file(actual) != expected_sha:
            raise ValueError(f"implementation binding differs: {relative}")


def write_new_files_atomically(files: Sequence[tuple[Path, bytes]]) -> None:
    if not files:
        raise ValueError("empty artifact transaction")
    targets = [path for path, _ in files]
    if len(targets) != len(set(targets)):
        raise ValueError("artifact transaction has duplicate targets")
    for target in targets:
        if target.exists():
            raise FileExistsError(f"Refusing to overwrite artifact: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
    pending = [target.with_name(target.name + ".pending") for target in targets]
    for path in pending:
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite pending artifact: {path}")
    promoted: list[Path] = []
    try:
        for path, (_, payload) in zip(pending, files, strict=True):
            with path.open("xb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        for path, (_, payload) in zip(pending, files, strict=True):
            if file_identity(path) != {
                "bytes": len(payload),
                "sha256": sha256_bytes(payload),
            }:
                raise RuntimeError(f"pending artifact identity differs: {path}")
        for path, target in zip(pending, targets, strict=True):
            os.replace(path, target)
            promoted.append(target)
    except Exception:
        for path in pending:
            path.unlink(missing_ok=True)
        for path in promoted:
            path.unlink(missing_ok=True)
        raise
