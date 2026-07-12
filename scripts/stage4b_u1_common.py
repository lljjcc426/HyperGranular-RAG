"""Shared deterministic I/O and integrity helpers for Stage4B-U1."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "stage4b_u1_v2"
TIE_SALT = "stage4b_u1_v2"
Q25_FLOOR = 0.1957079917192459
BUDGET_FRACTION = 0.60
PROTECT_N = 10
INSERT_BUDGET = 4
MAX_K = 20

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
