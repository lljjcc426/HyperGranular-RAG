"""Shared contracts for Stage4G generator-transfer replication.

This module contains only deterministic serialization, strict schema helpers,
frozen-input reconstruction, and the pre-registered statistical primitives.
It never opens Gold unless a caller explicitly passes a Gold path.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


SCHEMA_VERSION = "stage4g_gtr_v1"
SYSTEM_MESSAGE = (
    "Answer the question using only the provided evidence. "
    "Return only the shortest final answer. "
    "If the evidence is insufficient, return UNKNOWN."
)
METHODS = ("DENSE_TOP20", "STATIC_Q25_TOP20")
DATASETS = ("hotpotqa_train_distractor_v1_1", "musique_ans_v1_0_train")
TOKEN_CAP = 4096
MAX_NEW_TOKENS = 32
BOOTSTRAP_ITERATIONS = 10_000
BOOTSTRAP_SEED = 20260724
RERUN_SUBSET_PER_DATASET = 100
RERUN_SALT = "stage4g_gtr_rerun_v1\0"
PROHIBITED_KEYS = {
    "answer", "answers", "gold", "label", "labels", "supporting_facts",
    "supporting_paragraph_indices", "supporting_unit_ids", "method",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def file_identity(path: Path) -> dict[str, Any]:
    return {"bytes": path.stat().st_size, "sha256": sha256_file(path)}


def render_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def render_jsonl(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(
        (
            json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
            + "\n"
        ).encode("utf-8")
        for row in rows
    )


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.endswith("\n"):
                raise ValueError(f"{path} line {line_number} lacks LF terminator")
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path} line {line_number} must be a JSON object")
            rows.append(value)
    return rows


def require_string(value: Any, label: str, *, nonempty: bool = True) -> str:
    if not isinstance(value, str) or (nonempty and not value.strip()):
        raise ValueError(f"{label} must be a native non-empty JSON string")
    return value


def require_int(value: Any, label: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be a JSON integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be >= {minimum}")
    return value


def require_number(value: Any, label: str, *, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a JSON number")
    result = float(value)
    if not math.isfinite(result) or (minimum is not None and result < minimum):
        raise ValueError(f"{label} must be finite" + (f" and >= {minimum}" if minimum is not None else ""))
    return result


def assert_identity(path: Path, expected: dict[str, Any], label: str) -> None:
    if not path.is_file():
        raise ValueError(f"{label} is missing: {path}")
    actual = file_identity(path)
    if actual != {"bytes": expected.get("bytes"), "sha256": expected.get("sha256")}:
        raise ValueError(f"{label} identity differs: expected={expected}, actual={actual}")


def assert_no_gold_or_method(value: Any, label: str) -> None:
    def walk(item: Any, position: str) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                if str(key).lower() in PROHIBITED_KEYS:
                    raise ValueError(f"{label} contains prohibited field at {position}.{key}")
                walk(child, f"{position}.{key}")
        elif isinstance(item, list):
            for index, child in enumerate(item):
                walk(child, f"{position}[{index}]")
    walk(value, label)


def write_new_files_atomically(outputs: Sequence[tuple[Path, bytes]]) -> None:
    if not outputs:
        raise ValueError("No outputs supplied")
    targets = [path for path, _ in outputs]
    if len(targets) != len(set(targets)):
        raise ValueError("Duplicate output path")
    pending = [path.with_name(path.name + ".pending") for path in targets]
    for path in targets + pending:
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite artifact: {path}")
    promoted: list[Path] = []
    try:
        for path, (_, payload) in zip(pending, outputs, strict=True):
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        for path, target in zip(pending, targets, strict=True):
            path.replace(target)
            promoted.append(target)
    except Exception:
        for path in pending:
            path.unlink(missing_ok=True)
        for path in promoted:
            path.unlink(missing_ok=True)
        raise


def assert_implementation_binding(config: dict[str, Any], root: Path) -> None:
    implementation = config.get("implementation")
    if not isinstance(implementation, dict):
        raise ValueError("implementation binding is missing")
    commit = implementation.get("code_commit")
    if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise ValueError("implementation.code_commit must be a full lowercase Git SHA")
    files = implementation.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("implementation.files is missing")
    for relative, expected in sorted(files.items()):
        relative = require_string(relative, "implementation file path")
        path = root / relative
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ValueError(f"Invalid implementation path: {relative}")
        if not path.is_file() or sha256_file(path) != expected:
            raise ValueError(f"Implementation binding differs: {relative}")


def method_order(query_id: str) -> tuple[str, str]:
    query_id = require_string(query_id, "query_id")
    return METHODS if (hashlib.sha256(query_id.encode("utf-8")).digest()[0] & 1) == 0 else METHODS[::-1]


def rerun_selection_key(dataset: str, query_id: str) -> tuple[bytes, str]:
    dataset = require_string(dataset, "dataset")
    query_id = require_string(query_id, "query_id")
    return hashlib.sha256((RERUN_SALT + dataset + "\0" + query_id).encode("utf-8")).digest(), query_id


def select_rerun_query_ids(queries: Sequence[dict[str, Any]]) -> dict[str, list[str]]:
    selected: dict[str, list[str]] = {}
    for dataset in DATASETS:
        ids = [row["query_id"] for row in queries if row["dataset"] == dataset]
        if len(ids) < RERUN_SUBSET_PER_DATASET or len(ids) != len(set(ids)):
            raise ValueError(f"{dataset} cannot supply the frozen rerun subset")
        selected[dataset] = sorted(ids, key=lambda value: rerun_selection_key(dataset, value))[
            :RERUN_SUBSET_PER_DATASET
        ]
    return selected


def id_digest(values: Iterable[str]) -> str:
    payload = b"".join(require_string(value, "identity").encode("utf-8") + b"\n" for value in values)
    return sha256_bytes(payload)


def ranking_digest(unit_ids: Sequence[str]) -> str:
    return sha256_bytes(render_json(list(unit_ids)))


def semantic_prompt_digest(
    question: str,
    included_units: Sequence[dict[str, Any]],
    rendered_evidence_lines: Sequence[str],
) -> str:
    if len(included_units) != len(rendered_evidence_lines):
        raise ValueError("Semantic prompt inputs differ in length")
    payload = {
        "evidence": [
            {
                "rendered": line,
                "text": unit["text"],
                "title": unit["title"],
                "unit_id": unit["unit_id"],
            }
            for unit, line in zip(included_units, rendered_evidence_lines, strict=True)
        ],
        "question": require_string(question, "question"),
        "system": SYSTEM_MESSAGE,
        "user_contract": "Evidence:<ranked units>\\n\\nQuestion:<question>\\nFinal answer:",
    }
    assert_no_gold_or_method(payload, "semantic prompt")
    return sha256_bytes(render_json(payload))


def load_frozen_dataset(
    dataset: str,
    blind_path: Path,
    ranking_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    blind = load_jsonl(blind_path)
    rankings = load_jsonl(ranking_path)
    if len(blind) != len(rankings):
        raise ValueError(f"{dataset}: blind/ranking row counts differ")
    assert_no_gold_or_method(blind, f"{dataset} blind")
    ranking_by_query: dict[str, dict[str, Any]] = {}
    units_by_query: dict[str, dict[str, Any]] = {}
    queries: list[dict[str, Any]] = []
    for index, (blind_row, ranking_row) in enumerate(zip(blind, rankings, strict=True)):
        query_id = require_string(blind_row.get("query_id"), f"{dataset}.blind[{index}].query_id")
        sample_id = require_string(blind_row.get("sample_id"), f"{dataset}.blind[{index}].sample_id")
        question = require_string(blind_row.get("question"), f"{dataset}.blind[{index}].question")
        if blind_row.get("dataset") != dataset or query_id != f"{dataset}::{sample_id}":
            raise ValueError(f"{dataset}.blind[{index}] identity differs")
        if ranking_row.get("dataset") != dataset or ranking_row.get("query_id") != query_id or ranking_row.get("sample_id") != sample_id:
            raise ValueError(f"{dataset}.rankings[{index}] identity/order differs")
        unit_map: dict[str, dict[str, Any]] = {}
        if dataset == DATASETS[0]:
            contexts = blind_row.get("context")
            if not isinstance(contexts, list) or not contexts:
                raise ValueError(f"{query_id}: context must be non-empty")
            for context_index, context in enumerate(contexts):
                if context.get("context_index") != context_index:
                    raise ValueError(f"{query_id}: context order differs")
                title = require_string(context.get("title"), f"{query_id}.title")
                sentences = context.get("sentences")
                if not isinstance(sentences, list):
                    raise ValueError(f"{query_id}: sentences must be a list")
                for sentence_index, sentence in enumerate(sentences):
                    if not isinstance(sentence, str):
                        raise ValueError(f"{query_id}: sentence must be a string")
                    text = " ".join(sentence.split())
                    if not text:
                        continue
                    unit_id = f"{query_id}::c{context_index}::s{sentence_index}"
                    unit_map[unit_id] = {"unit_id": unit_id, "title": title, "text": text}
        else:
            candidate_units = blind_row.get("candidate_units")
            if not isinstance(candidate_units, list) or not candidate_units:
                raise ValueError(f"{query_id}: candidate_units must be non-empty")
            for unit in candidate_units:
                if not isinstance(unit, dict):
                    raise ValueError(f"{query_id}: candidate unit must be an object")
                unit_id = require_string(unit.get("unit_id"), f"{query_id}.unit_id")
                if unit.get("dataset") != dataset or unit.get("query_id") != query_id or unit.get("sample_id") != sample_id:
                    raise ValueError(f"{unit_id}: candidate unit identity differs")
                unit_map[unit_id] = {
                    "unit_id": unit_id,
                    "title": require_string(unit.get("title"), f"{unit_id}.title"),
                    "text": require_string(unit.get("text"), f"{unit_id}.text"),
                }
        if query_id in ranking_by_query:
            raise ValueError(f"Duplicate query: {query_id}")
        for key in ("dense_top20_unit_ids", "static_q25_top20_unit_ids"):
            ids = ranking_row.get(key)
            if not isinstance(ids, list) or not 1 <= len(ids) <= 20 or len(ids) != len(set(ids)):
                raise ValueError(f"{query_id}.{key} must contain 1..20 unique effective-K IDs")
            for unit_id in ids:
                require_string(unit_id, f"{query_id}.{key}")
                if unit_id not in unit_map:
                    raise ValueError(f"{query_id}.{key} contains a non-candidate unit")
        queries.append({"dataset": dataset, "query_id": query_id, "question": question, "sample_id": sample_id})
        ranking_by_query[query_id] = ranking_row
        units_by_query[query_id] = unit_map
    return queries, ranking_by_query, units_by_query


def percentile_summary(values: np.ndarray, point: float) -> dict[str, float]:
    lower, upper = np.percentile(values, [2.5, 97.5], method="linear")
    return {"lower_95": float(lower), "point": float(point), "upper_95": float(upper)}


def paired_bootstrap(delta: np.ndarray, *, seed: int = BOOTSTRAP_SEED) -> dict[str, float]:
    delta = np.asarray(delta, dtype="float64")
    if delta.ndim != 1 or delta.size == 0 or not np.isfinite(delta).all():
        raise ValueError("paired bootstrap requires one finite non-empty vector")
    rng = np.random.Generator(np.random.PCG64(seed))
    draws = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    for index in range(BOOTSTRAP_ITERATIONS):
        selected = rng.integers(0, delta.size, size=delta.size)
        draws[index] = float(np.mean(delta[selected]))
    return percentile_summary(draws, float(np.mean(delta)))


def stratified_equal_weight_bootstrap(
    hotpot_delta: np.ndarray,
    musique_delta: np.ndarray,
    *,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, float]:
    hotpot = np.asarray(hotpot_delta, dtype="float64")
    musique = np.asarray(musique_delta, dtype="float64")
    if hotpot.ndim != 1 or musique.ndim != 1 or hotpot.size == 0 or musique.size == 0:
        raise ValueError("stratified bootstrap requires two non-empty vectors")
    if not np.isfinite(hotpot).all() or not np.isfinite(musique).all():
        raise ValueError("stratified bootstrap inputs must be finite")
    rng = np.random.Generator(np.random.PCG64(seed))
    draws = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    for index in range(BOOTSTRAP_ITERATIONS):
        h = rng.integers(0, hotpot.size, size=hotpot.size)
        m = rng.integers(0, musique.size, size=musique.size)
        draws[index] = (float(np.mean(hotpot[h])) + float(np.mean(musique[m]))) / 2.0
    point = (float(np.mean(hotpot)) + float(np.mean(musique))) / 2.0
    return percentile_summary(draws, point)


def scientific_decision(
    dataset_summaries: dict[str, dict[str, Any]],
    equal_weight: dict[str, Any],
) -> str:
    hotpot = dataset_summaries[DATASETS[0]]["bootstrap"]
    musique = dataset_summaries[DATASETS[1]]["bootstrap"]
    pooled_f1 = equal_weight["delta_answer_f1"]
    pooled_em = equal_weight["delta_answer_em"]
    if (
        pooled_f1["point"] >= 0.010
        and pooled_f1["lower_95"] > 0.0
        and hotpot["delta_answer_f1"]["point"] > 0.0
        and musique["delta_answer_f1"]["point"] > 0.0
        and pooled_em["lower_95"] >= -0.010
        and hotpot["delta_answer_em"]["upper_95"] >= -0.010
        and musique["delta_answer_em"]["upper_95"] >= -0.010
    ):
        return "GENERATOR_TRANSFER_SUPPORTED"
    if (
        pooled_f1["upper_95"] < 0.0
        or hotpot["delta_answer_f1"]["upper_95"] < 0.0
        or musique["delta_answer_f1"]["upper_95"] < 0.0
        or pooled_em["upper_95"] < -0.010
        or hotpot["delta_answer_em"]["upper_95"] < -0.010
        or musique["delta_answer_em"]["upper_95"] < -0.010
    ):
        return "GENERATOR_TRANSFER_NEGATIVE"
    return "GENERATOR_TRANSFER_INCONCLUSIVE"
