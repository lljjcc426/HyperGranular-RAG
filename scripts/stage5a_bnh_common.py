"""Shared deterministic contracts for Stage5A-BNH."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Iterable

from stage4h_cbe_common import (
    assert_file_identity,
    assert_implementation_binding,
    assert_no_gold_fields,
    file_identity,
    id_digest,
    load_json,
    load_jsonl,
    path_from_config,
    render_json,
    render_jsonl,
    require_finite_number,
    require_json_bool,
    require_json_int,
    require_native_string,
    sha256_bytes,
    sha256_file,
    validate_sha256,
    validate_snapshot,
    write_new_files_atomically,
)


SCHEMA_VERSION = "stage5a_bnh_v1"
HOTPOT_DATASET = "hotpotqa_train_distractor_v1_1"
MUSIQUE_DATASET = "musique_ans_v1_0_train"
DATASETS = (HOTPOT_DATASET, MUSIQUE_DATASET)
DATASET_KEYS = {HOTPOT_DATASET: "hotpotqa", MUSIQUE_DATASET: "musique"}
BOUNDARIES = ("development", "confirmation")
SAMPLE_SIZES = {
    "development": {HOTPOT_DATASET: 500, MUSIQUE_DATASET: 750},
    "confirmation": {HOTPOT_DATASET: 1000, MUSIQUE_DATASET: 1500},
}
SELECTION_SALTS = {
    "development": "stage5a_bnh_development_v1\0",
    "confirmation": "stage5a_bnh_confirmation_v1\0",
}
RERUN_SALTS = {
    "development": "stage5a_bnh_development_rerun_v1\0",
    "confirmation": "stage5a_bnh_confirmation_rerun_v1\0",
}
RERUN_QUERIES_PER_DATASET = {
    "development": 50,
    "confirmation": 100,
}
BOOTSTRAP_SEED = 20260727
BOOTSTRAP_ITERATIONS = 10_000

BGE_ID = "BAAI/bge-large-en-v1.5"
BGE_REVISION = "d4aa6901d3a41ba39fb536a557fa166f842b0e09"
BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
GENERATOR_ID = "Qwen/Qwen2.5-1.5B-Instruct"
GENERATOR_REVISION = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"

BASELINE_METHOD = "BGE_TOP20"
CONFIRMATION_METHODS = (
    BASELINE_METHOD,
    "BGE_NATIVE_HGRAG_PROTECTED_TOP20",
    "BGE_NATIVE_HGRAG_UNPROTECTED_TOP20",
    "BGE_NATIVE_HGRAG_NO_FACET_TOP20",
)

SYSTEM_MESSAGE = (
    "Answer the question using only the provided evidence. Return only the "
    "shortest final answer. If the evidence is insufficient, return UNKNOWN."
)


def selection_key(
    boundary: str, dataset_key: str, native_id: str
) -> tuple[str, str]:
    if boundary not in BOUNDARIES:
        raise ValueError(f"unknown Stage5A boundary: {boundary}")
    dataset_key = require_native_string(dataset_key, "dataset_key")
    native_id = require_native_string(native_id, "native_id")
    digest = hashlib.sha256(
        (
            SELECTION_SALTS[boundary]
            + dataset_key
            + "\0"
            + native_id
        ).encode("utf-8")
    ).hexdigest()
    return digest, native_id


def rerun_selection_key(
    boundary: str, dataset: str, query_id: str
) -> tuple[str, str]:
    if boundary not in BOUNDARIES:
        raise ValueError(f"unknown Stage5A boundary: {boundary}")
    dataset = require_native_string(dataset, "dataset")
    query_id = require_native_string(query_id, "query_id")
    digest = hashlib.sha256(
        (RERUN_SALTS[boundary] + dataset + "\0" + query_id).encode("utf-8")
    ).hexdigest()
    return digest, query_id


def development_method(config_id: str) -> str:
    config_id = require_native_string(config_id, "config_id")
    if re.fullmatch(r"C[0-9]{2}", config_id) is None:
        raise ValueError(f"invalid Stage5A config ID: {config_id}")
    return f"BNH_{config_id}_PROTECTED_TOP20"


def deterministic_method_order(
    query_id: str, methods: Iterable[str], namespace: str
) -> tuple[str, ...]:
    query_id = require_native_string(query_id, "query_id")
    namespace = require_native_string(namespace, "namespace")
    values = tuple(require_native_string(value, "method") for value in methods)
    if not values or len(values) != len(set(values)):
        raise ValueError("method order input must be non-empty and unique")
    digest = hashlib.sha256(
        (namespace + "\0" + query_id).encode("utf-8")
    ).digest()
    offset = int.from_bytes(digest[:2], "big") % len(values)
    ordered = values[offset:] + values[:offset]
    return tuple(reversed(ordered)) if digest[2] & 1 else ordered


def load_parent_config(config: dict[str, Any]) -> dict[str, Any]:
    binding = config.get("frozen_stage4h_parent")
    if not isinstance(binding, dict):
        raise ValueError("frozen_stage4h_parent binding is missing")
    path = Path(
        require_native_string(binding.get("path"), "frozen_stage4h_parent.path")
    )
    assert_file_identity(path, binding, "frozen_stage4h_parent")
    parent = load_json(path)
    if not isinstance(parent, dict):
        raise ValueError("Stage4H parent config must be an object")
    return parent


def validate_authorization(config: dict[str, Any]) -> None:
    if config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Stage5A config schema differs")
    authorization = config.get("official_execution")
    if not isinstance(authorization, dict) or require_json_bool(
        authorization.get("authorized"), "official_execution.authorized"
    ) is not True:
        raise PermissionError("STAGE5A_BNH_EXECUTION_NOT_AUTHORIZED")


def assert_bound(config: dict[str, Any], key: str) -> Path:
    path = path_from_config(config, key)
    expected = config.get("inputs", {}).get(key)
    if not isinstance(expected, dict):
        raise ValueError(f"inputs.{key} binding is missing")
    assert_file_identity(path, expected, f"inputs.{key}")
    return path


def validate_candidate_configs(config: dict[str, Any]) -> list[dict[str, Any]]:
    values = config.get("candidate_configs")
    if not isinstance(values, list) or not values or len(values) > 16:
        raise ValueError("candidate_configs must contain 1..16 rows")
    seen: set[str] = set()
    expected_keys = {
        "config_id",
        "facet_gate",
        "insert_budget",
        "leaf_size",
        "unit_score_percentile",
    }
    output: list[dict[str, Any]] = []
    for index, row in enumerate(values):
        if not isinstance(row, dict) or set(row) != expected_keys:
            raise ValueError(f"candidate_configs[{index}] schema differs")
        config_id = require_native_string(
            row["config_id"], f"candidate_configs[{index}].config_id"
        )
        if re.fullmatch(r"C[0-9]{2}", config_id) is None or config_id in seen:
            raise ValueError(f"candidate_configs[{index}].config_id differs")
        seen.add(config_id)
        leaf_size = require_json_int(
            row["leaf_size"], f"candidate_configs[{index}].leaf_size"
        )
        budget = require_json_int(
            row["insert_budget"], f"candidate_configs[{index}].insert_budget"
        )
        percentile = require_finite_number(
            row["unit_score_percentile"],
            f"candidate_configs[{index}].unit_score_percentile",
        )
        gate = require_native_string(
            row["facet_gate"], f"candidate_configs[{index}].facet_gate"
        )
        if leaf_size not in {4, 6}:
            raise ValueError("Stage5A leaf_size must be 4 or 6")
        if budget not in {2, 4}:
            raise ValueError("Stage5A insert_budget must be 2 or 4")
        if percentile not in {0.50, 0.75}:
            raise ValueError("Stage5A unit_score_percentile must be 0.50 or 0.75")
        if gate not in {"BROAD", "STRICT"}:
            raise ValueError("Stage5A facet_gate must be BROAD or STRICT")
        output.append(dict(row))
    if [row["config_id"] for row in output] != sorted(seen):
        raise ValueError("candidate_configs must be ordered by config_id")
    return output


__all__ = [
    "BASELINE_METHOD",
    "BGE_ID",
    "BGE_QUERY_PREFIX",
    "BGE_REVISION",
    "BOOTSTRAP_ITERATIONS",
    "BOOTSTRAP_SEED",
    "BOUNDARIES",
    "CONFIRMATION_METHODS",
    "DATASETS",
    "DATASET_KEYS",
    "GENERATOR_ID",
    "GENERATOR_REVISION",
    "HOTPOT_DATASET",
    "MUSIQUE_DATASET",
    "RERUN_QUERIES_PER_DATASET",
    "SAMPLE_SIZES",
    "SCHEMA_VERSION",
    "SYSTEM_MESSAGE",
    "assert_bound",
    "assert_file_identity",
    "assert_implementation_binding",
    "assert_no_gold_fields",
    "deterministic_method_order",
    "development_method",
    "file_identity",
    "id_digest",
    "load_json",
    "load_jsonl",
    "load_parent_config",
    "path_from_config",
    "render_json",
    "render_jsonl",
    "require_finite_number",
    "require_json_bool",
    "require_json_int",
    "require_native_string",
    "rerun_selection_key",
    "selection_key",
    "sha256_bytes",
    "sha256_file",
    "validate_authorization",
    "validate_candidate_configs",
    "validate_sha256",
    "validate_snapshot",
    "write_new_files_atomically",
]
