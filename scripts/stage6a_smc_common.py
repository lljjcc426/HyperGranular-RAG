"""Frozen shared contracts for Stage6A-SMC."""

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


SCHEMA_VERSION = "stage6a_smc_v1"
HOTPOT_DATASET = "hotpotqa_train_distractor_v1_1"
MUSIQUE_DATASET = "musique_ans_v1_0_train"
TWOWIKI_DATASET = "2wikimultihopqa_official_dev"
DATASETS = (HOTPOT_DATASET, MUSIQUE_DATASET, TWOWIKI_DATASET)
DATASET_KEYS = {
    HOTPOT_DATASET: "hotpotqa",
    MUSIQUE_DATASET: "musique",
    TWOWIKI_DATASET: "2wikimultihopqa",
}
BOUNDARIES = ("development", "confirmation")
SAMPLE_SIZES = {
    "development": {
        HOTPOT_DATASET: 400,
        MUSIQUE_DATASET: 600,
        TWOWIKI_DATASET: 400,
    },
    "confirmation": {
        HOTPOT_DATASET: 800,
        MUSIQUE_DATASET: 1200,
        TWOWIKI_DATASET: 800,
    },
}
SELECTION_SALT = "stage6a_smc_v1\0"
RERUN_SALTS = {
    "development": "stage6a_smc_development_rerun_v1\0",
    "confirmation": "stage6a_smc_confirmation_rerun_v1\0",
}
RERUN_QUERIES_PER_DATASET = {"development": 40, "confirmation": 80}

EMBEDDING_ID = "Qwen/Qwen3-Embedding-0.6B"
EMBEDDING_REVISION = "97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3"
RERANKER_ID = "Qwen/Qwen3-Reranker-0.6B"
RERANKER_REVISION = "e61197ed45024b0ed8a2d74b80b4d909f1255473"
GENERATOR_ID = "Qwen/Qwen2.5-1.5B-Instruct"
GENERATOR_REVISION = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
RETRIEVAL_INSTRUCTION = (
    "Given a web search query, retrieve relevant passages that answer the query"
)

BASELINE_METHOD = "QWEN3_RERANK_TOP20"
GENERIC_FAMILIES = (
    "MMR_TOP20",
    "MAX_QUERY_COVERAGE_TOP20",
    "RELEVANCE_DIVERSITY_COVERAGE_TOP20",
)
NON_BALL_FAMILIES = (
    "FIXED_WINDOW_STRUCTURE_TOP20",
    "SPHERICAL_KMEANS_STRUCTURE_TOP20",
    "HIERARCHICAL_CLUSTER_STRUCTURE_TOP20",
)
BALL_FAMILY = "GRANULAR_BALL_NO_HYPEREDGE_TOP20"
HGRAG_FAMILY = "HGRAG_JOINT_TOP20"
LAMBDAS = (0.70, 0.85)
LEAF_TARGETS = (4, 6)

BOOTSTRAP_ITERATIONS = 10_000
BOOTSTRAP_SEED = 20260728


def selection_key(
    dataset_key: str, native_id: str, source_row_index: int
) -> tuple[str, str]:
    dataset_key = require_native_string(dataset_key, "dataset_key")
    native_id = require_native_string(native_id, "native_id")
    source_row_index = require_json_int(source_row_index, "source_row_index")
    if source_row_index < 0:
        raise ValueError("source_row_index must be non-negative")
    digest = hashlib.sha256(
        (
            SELECTION_SALT
            + dataset_key
            + "\0"
            + native_id
            + "\0"
            + str(source_row_index)
        ).encode("utf-8")
    ).hexdigest()
    return digest, native_id


def rerun_selection_key(
    boundary: str, dataset: str, query_id: str
) -> tuple[str, str]:
    if boundary not in BOUNDARIES:
        raise ValueError(f"unknown Stage6A boundary: {boundary}")
    dataset = require_native_string(dataset, "dataset")
    query_id = require_native_string(query_id, "query_id")
    digest = hashlib.sha256(
        (RERUN_SALTS[boundary] + dataset + "\0" + query_id).encode("utf-8")
    ).hexdigest()
    return digest, query_id


def config_method(family: str, lambda_value: float, leaf_target: int | None) -> str:
    if family not in GENERIC_FAMILIES + NON_BALL_FAMILIES + (
        BALL_FAMILY,
        HGRAG_FAMILY,
    ):
        raise ValueError(f"unknown Stage6A family: {family}")
    if lambda_value not in LAMBDAS:
        raise ValueError("lambda differs from frozen family")
    suffix = f"L{int(round(lambda_value * 100)):03d}"
    if family in (BALL_FAMILY, HGRAG_FAMILY):
        if leaf_target not in LEAF_TARGETS:
            raise ValueError("leaf target differs from frozen family")
        suffix += f"_T{leaf_target}"
    elif leaf_target is not None:
        raise ValueError("generic/non-ball method may not carry leaf target")
    return f"{family}__{suffix}"


def family_from_method(method: str) -> str:
    method = require_native_string(method, "method")
    if method == BASELINE_METHOD:
        return method
    family = method.split("__", 1)[0]
    if family not in GENERIC_FAMILIES + NON_BALL_FAMILIES + (
        BALL_FAMILY,
        HGRAG_FAMILY,
    ):
        raise ValueError(f"unknown Stage6A method: {method}")
    return family


def development_methods() -> tuple[str, ...]:
    methods = [BASELINE_METHOD]
    for family in GENERIC_FAMILIES + NON_BALL_FAMILIES:
        methods.extend(config_method(family, value, None) for value in LAMBDAS)
    for family in (BALL_FAMILY, HGRAG_FAMILY):
        methods.extend(
            config_method(family, value, leaf)
            for value in LAMBDAS
            for leaf in LEAF_TARGETS
        )
    return tuple(methods)


def deterministic_method_order(
    query_id: str, methods: Iterable[str], namespace: str
) -> tuple[str, ...]:
    query_id = require_native_string(query_id, "query_id")
    namespace = require_native_string(namespace, "namespace")
    values = tuple(require_native_string(value, "method") for value in methods)
    if not values or len(values) != len(set(values)):
        raise ValueError("method order input must be non-empty and unique")
    digest = hashlib.sha256((namespace + "\0" + query_id).encode("utf-8")).digest()
    offset = int.from_bytes(digest[:2], "big") % len(values)
    ordered = values[offset:] + values[:offset]
    return tuple(reversed(ordered)) if digest[2] & 1 else ordered


def validate_authorization(config: dict[str, Any]) -> None:
    if config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Stage6A config schema differs")
    authorization = config.get("official_execution")
    if not isinstance(authorization, dict) or require_json_bool(
        authorization.get("authorized"), "official_execution.authorized"
    ) is not True:
        raise PermissionError("STAGE6A_SMC_EXECUTION_NOT_AUTHORIZED")


def assert_bound(config: dict[str, Any], key: str) -> Path:
    path = path_from_config(config, key)
    expected = config.get("inputs", {}).get(key)
    if not isinstance(expected, dict):
        raise ValueError(f"inputs.{key} binding is missing")
    assert_file_identity(path, expected, f"inputs.{key}")
    return path


def validate_confirmation_methods(values: Any) -> tuple[str, ...]:
    if not isinstance(values, list) or len(values) != 5:
        raise ValueError("confirmation_methods must contain five methods")
    methods = tuple(require_native_string(value, "confirmation_method") for value in values)
    if len(set(methods)) != 5 or methods[0] != BASELINE_METHOD:
        raise ValueError("confirmation method identity/order differs")
    expected_families = (
        BASELINE_METHOD,
        "GENERIC",
        "NON_BALL",
        BALL_FAMILY,
        HGRAG_FAMILY,
    )
    actual = [BASELINE_METHOD]
    for method in methods[1:]:
        family = family_from_method(method)
        if family in GENERIC_FAMILIES:
            actual.append("GENERIC")
        elif family in NON_BALL_FAMILIES:
            actual.append("NON_BALL")
        else:
            actual.append(family)
    if tuple(actual) != expected_families:
        raise ValueError("confirmation family order differs")
    return methods


def parse_method(method: str) -> tuple[str, float | None, int | None]:
    family = family_from_method(method)
    if family == BASELINE_METHOD:
        return family, None, None
    match = re.search(r"__L([0-9]{3})(?:_T([46]))?$", method)
    if match is None:
        raise ValueError(f"malformed Stage6A method: {method}")
    lambda_value = int(match.group(1)) / 100.0
    leaf_target = int(match.group(2)) if match.group(2) else None
    expected = config_method(family, lambda_value, leaf_target)
    if expected != method:
        raise ValueError(f"non-canonical Stage6A method: {method}")
    return family, lambda_value, leaf_target


__all__ = [
    "BALL_FAMILY",
    "BASELINE_METHOD",
    "BOOTSTRAP_ITERATIONS",
    "BOOTSTRAP_SEED",
    "BOUNDARIES",
    "DATASETS",
    "DATASET_KEYS",
    "EMBEDDING_ID",
    "EMBEDDING_REVISION",
    "GENERATOR_ID",
    "GENERATOR_REVISION",
    "GENERIC_FAMILIES",
    "HGRAG_FAMILY",
    "HOTPOT_DATASET",
    "LAMBDAS",
    "LEAF_TARGETS",
    "MUSIQUE_DATASET",
    "NON_BALL_FAMILIES",
    "RERANKER_ID",
    "RERANKER_REVISION",
    "RERUN_QUERIES_PER_DATASET",
    "RETRIEVAL_INSTRUCTION",
    "SAMPLE_SIZES",
    "SCHEMA_VERSION",
    "TWOWIKI_DATASET",
    "assert_bound",
    "assert_file_identity",
    "assert_implementation_binding",
    "assert_no_gold_fields",
    "config_method",
    "deterministic_method_order",
    "development_methods",
    "family_from_method",
    "file_identity",
    "id_digest",
    "load_json",
    "load_jsonl",
    "parse_method",
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
    "validate_confirmation_methods",
    "validate_sha256",
    "validate_snapshot",
    "write_new_files_atomically",
]
