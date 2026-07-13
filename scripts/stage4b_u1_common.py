"""Shared deterministic I/O and integrity helpers for Stage4B-U1."""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "stage4b_u1_v2"
IMPLEMENTATION_CHECKPOINT = "stage4b_u1_v2_3"
TIE_SALT = "stage4b_u1_v2"
Q25_FLOOR = 0.1957079917192459
BUDGET_FRACTION = 0.60
PROTECT_N = 10
INSERT_BUDGET = 4
MAX_K = 20
OFFICIAL_DEVELOPMENT_QUERIES = 4500
OFFICIAL_DEVELOPMENT_DATASET = "2wikimultihopqa"
OFFICIAL_DEVELOPMENT_SAMPLE_ID_SHA256 = (
    "6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2"
)
OFFICIAL_DEVELOPMENT_QUERY_ID_SHA256 = (
    "8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6"
)
STAGE4A_R2_SOURCE_AUDIT_SHA256 = (
    "1496FF0CE08093AD38258FD5049068D6C4ED74FCEBF63E94E6E486F3478C7AEE"
)
STAGE4A_R2_VERIFICATION_SHA256 = (
    "0AD9A7B218A19297070E05F2BF7C04786165378E14990C343A0B8B8EFD8CCAD0"
)
STAGE4A_R2_STRATEGY_SUMMARY_SHA256 = (
    "7BF79CC057CDD0565100B1D95F35C95BFBEAA338E9B1EF63D9E81F029BB42B12"
)
FROZEN_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
FROZEN_MAX_LENGTH = 192
FROZEN_BATCH_SIZE = 64
PROTOCOL_RELATIVE_PATH = "docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md"
POLICY_IMPLEMENTATION_FILES = {
    "common_source_sha256": "scripts/stage4b_u1_common.py",
    "retrieval_source_sha256": "scripts/stage4b_u1_goldfree_retrieval.py",
    "controller_source_sha256": "scripts/stage4b_u1_goldfree_controller.py",
    "channel_preparer_source_sha256": "scripts/stage4b_u1_prepare_channels.py",
    "verifier_source_sha256": "scripts/stage4b_u1_verify.py",
}

PROHIBITED_CONTROLLER_KEYS = frozenset(
    {
        "answer",
        "supporting_facts",
        "gold_evidence",
        "gold_unit_ids",
        "num_gold_units",
        "is_gold",
        "gold_units",
        "inserted_gold_units",
        "inserted_non_gold_units",
        "gain_event",
        "harm_event",
        "question_type",
        "type",
        "evidences",
    }
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def git_head(repo_root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_blob_sha256(repo_root: Path, commit: str, relative_path: str) -> str:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{relative_path}"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    return sha256_bytes(completed.stdout)


def assert_files_match_git_commit(
    repo_root: Path, commit: str, relative_paths: Iterable[str]
) -> None:
    for relative_path in relative_paths:
        tracked = subprocess.run(
            ["git", "cat-file", "-e", f"{commit}:{relative_path}"],
            cwd=repo_root,
            capture_output=True,
        )
        unchanged = subprocess.run(
            ["git", "diff", "--quiet", commit, "--", relative_path],
            cwd=repo_root,
        )
        if tracked.returncode != 0 or unchanged.returncode != 0:
            raise ValueError(
                f"Working file differs from git commit {commit}: {relative_path}"
            )


def implementation_hashes(repo_root: Path) -> dict[str, str]:
    return {
        field: sha256_file(repo_root / relative_path)
        for field, relative_path in POLICY_IMPLEMENTATION_FILES.items()
    }


def id_digest(ids: Iterable[str]) -> str:
    payload = "\n".join(sorted(str(item) for item in ids)) + "\n"
    return sha256_bytes(payload.encode("utf-8"))


def tie_hash(query_id: str) -> str:
    return hashlib.sha256(f"{TIE_SALT}::{query_id}".encode("utf-8")).hexdigest().upper()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected JSON object")
            rows.append(value)
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def assert_finite(value: float, label: str) -> float:
    converted = float(value)
    if not math.isfinite(converted):
        raise ValueError(f"Non-finite {label}: {converted}")
    return converted


def assert_no_prohibited_keys(value: Any, location: str = "root") -> None:
    if isinstance(value, dict):
        forbidden = sorted(PROHIBITED_CONTROLLER_KEYS & set(value))
        if forbidden:
            raise ValueError(f"Prohibited controller keys at {location}: {forbidden}")
        for key, nested in value.items():
            assert_no_prohibited_keys(nested, f"{location}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            assert_no_prohibited_keys(nested, f"{location}[{index}]")


def validate_unique_ids(rows: list[dict[str, Any]], field: str, label: str) -> list[str]:
    ids = [str(row[field]) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate {label} {field} values")
    return ids


def exact_mcnemar_two_sided_pvalue(gains: int, harms: int) -> float:
    discordant = gains + harms
    if discordant == 0:
        return 1.0
    tail = sum(math.comb(discordant, value) for value in range(0, min(gains, harms) + 1))
    return min(1.0, 2.0 * tail / (2.0**discordant))


def fisher_greater_pvalue(selected_gains: int, gains: int, selected_harms: int, harms: int) -> float:
    if gains <= 0 or harms <= 0:
        return 1.0
    selected_total = selected_gains + selected_harms
    population = gains + harms
    lower = max(0, selected_total - harms)
    upper = min(gains, selected_total)
    denominator = math.comb(population, selected_total)
    return sum(
        math.comb(gains, value) * math.comb(harms, selected_total - value) / denominator
        for value in range(max(selected_gains, lower), upper + 1)
    )
