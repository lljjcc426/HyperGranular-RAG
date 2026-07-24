"""Shared deterministic contracts for Stage4I-SDC."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from stage4h_cbe_common import (
    assert_file_identity,
    assert_implementation_binding,
    assert_no_gold_fields,
    file_identity,
    id_digest,
    load_json,
    load_jsonl,
    normalize_sentence,
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


SCHEMA_VERSION = "stage4i_sdc_v1"
ARTIFACT_STEM = "stage4i_sdc_hotpot1000_musique1500_v1"
HOTPOT_DATASET = "hotpotqa_train_distractor_v1_1"
MUSIQUE_DATASET = "musique_ans_v1_0_train"
DATASETS = (HOTPOT_DATASET, MUSIQUE_DATASET)
DATASET_KEYS = {HOTPOT_DATASET: "hotpotqa", MUSIQUE_DATASET: "musique"}
SAMPLE_SIZES = {HOTPOT_DATASET: 1000, MUSIQUE_DATASET: 1500}
SELECTION_SALT = "stage4i_sdc_v1\0"
RERUN_SALT = "stage4i_sdc_rerun_v1\0"
RERUN_QUERIES_PER_DATASET = 100
BOOTSTRAP_SEED = 20260726
BOOTSTRAP_ITERATIONS = 10_000

METHODS = (
    "BGE_TOP20",
    "BGE_HGRAG_PROTECTED_TOP20",
    "BGE_HGRAG_UNPROTECTED_TOP20",
    "BGE_HGRAG_NO_FACET_TOP20",
)
CORE_LEFT = "BGE_HGRAG_PROTECTED_TOP20"
CORE_RIGHT = "BGE_TOP20"

MINILM_ID = "sentence-transformers/all-MiniLM-L6-v2"
MINILM_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
STRONG_DENSE_ID = "BAAI/bge-large-en-v1.5"
STRONG_DENSE_REVISION = "d4aa6901d3a41ba39fb536a557fa166f842b0e09"
GENERATOR_ID = "Qwen/Qwen2.5-1.5B-Instruct"
GENERATOR_REVISION = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"


def selection_key(dataset: str, native_id: str) -> tuple[str, str]:
    digest = hashlib.sha256(
        (
            SELECTION_SALT
            + require_native_string(dataset, "dataset")
            + "\0"
            + require_native_string(native_id, "native_id")
        ).encode("utf-8")
    ).hexdigest()
    return digest, native_id


def rerun_selection_key(dataset: str, query_id: str) -> tuple[str, str]:
    digest = hashlib.sha256(
        (
            RERUN_SALT
            + require_native_string(dataset, "dataset")
            + "\0"
            + require_native_string(query_id, "query_id")
        ).encode("utf-8")
    ).hexdigest()
    return digest, query_id


def method_order(query_id: str) -> tuple[str, ...]:
    digest = hashlib.sha256(
        require_native_string(query_id, "query_id").encode("utf-8")
    ).digest()
    offset = digest[0] % len(METHODS)
    ordered = METHODS[offset:] + METHODS[:offset]
    return tuple(reversed(ordered)) if digest[1] & 1 else ordered


def load_parent_config(config: dict[str, Any]) -> dict[str, Any]:
    binding = config.get("frozen_parent")
    if not isinstance(binding, dict):
        raise ValueError("frozen_parent binding is missing")
    path = Path(require_native_string(binding.get("path"), "frozen_parent.path"))
    assert_file_identity(path, binding, "frozen_parent")
    parent = load_json(path)
    if (
        not isinstance(parent, dict)
        or parent.get("schema_version") != "stage4h_cbe_v1"
        or parent.get("status") != "STAGE4H_COMPLETE_FINAL_VERIFICATION_PASS"
    ):
        raise ValueError("frozen Stage4H parent config differs")
    return parent


def validate_authorization(config: dict[str, Any]) -> None:
    if config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Stage4I config schema differs")
    authorization = config.get("official_execution")
    if not isinstance(authorization, dict) or require_json_bool(
        authorization.get("authorized"), "official_execution.authorized"
    ) is not True:
        raise PermissionError("STAGE4I_EXECUTION_NOT_AUTHORIZED")


def assert_bound(config: dict[str, Any], key: str) -> Path:
    path = path_from_config(config, key)
    expected = config.get("inputs", {}).get(key)
    if not isinstance(expected, dict):
        raise ValueError(f"inputs.{key} binding is missing")
    assert_file_identity(path, expected, f"inputs.{key}")
    return path


def validate_inherited_models(config: dict[str, Any]) -> dict[str, Any]:
    parent = load_parent_config(config)
    requested = config.get("models")
    if not isinstance(requested, dict):
        raise ValueError("Stage4I model declarations are missing")
    expected = {
        "minilm": (MINILM_ID, MINILM_REVISION),
        "strong_dense": (STRONG_DENSE_ID, STRONG_DENSE_REVISION),
        "generator": (GENERATOR_ID, GENERATOR_REVISION),
    }
    for key, identity in expected.items():
        declaration = requested.get(key)
        inherited = parent.get("models", {}).get(key)
        if (
            not isinstance(declaration, dict)
            or not isinstance(inherited, dict)
            or (declaration.get("model_id"), declaration.get("revision")) != identity
            or (inherited.get("model_id"), inherited.get("revision")) != identity
        ):
            raise ValueError(f"models.{key} identity differs")
        snapshot = Path(
            require_native_string(inherited.get("snapshot_path"), f"{key}.snapshot_path")
        )
        validate_snapshot(snapshot, inherited, key)
    return parent


def assert_parent_stage4h_artifacts(parent: dict[str, Any]) -> dict[str, Any]:
    inputs = parent.get("inputs")
    paths = parent.get("paths")
    if not isinstance(inputs, dict) or not isinstance(paths, dict):
        raise ValueError("Stage4H parent artifact bindings are incomplete")
    checked: dict[str, Any] = {}
    for key, identity in sorted(inputs.items()):
        path_value = paths.get(key)
        if not isinstance(path_value, str):
            raise ValueError(f"Stage4H parent path is missing for {key}")
        path = Path(path_value)
        assert_file_identity(path, identity, f"Stage4H parent inputs.{key}")
        checked[key] = identity
    return checked


__all__ = [
    "ARTIFACT_STEM",
    "BOOTSTRAP_ITERATIONS",
    "BOOTSTRAP_SEED",
    "CORE_LEFT",
    "CORE_RIGHT",
    "DATASETS",
    "DATASET_KEYS",
    "GENERATOR_ID",
    "GENERATOR_REVISION",
    "HOTPOT_DATASET",
    "METHODS",
    "MINILM_ID",
    "MINILM_REVISION",
    "MUSIQUE_DATASET",
    "RERUN_QUERIES_PER_DATASET",
    "SAMPLE_SIZES",
    "SCHEMA_VERSION",
    "STRONG_DENSE_ID",
    "STRONG_DENSE_REVISION",
    "assert_bound",
    "assert_file_identity",
    "assert_implementation_binding",
    "assert_no_gold_fields",
    "assert_parent_stage4h_artifacts",
    "file_identity",
    "id_digest",
    "load_json",
    "load_jsonl",
    "load_parent_config",
    "method_order",
    "normalize_sentence",
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
    "validate_inherited_models",
    "validate_sha256",
    "write_new_files_atomically",
]
