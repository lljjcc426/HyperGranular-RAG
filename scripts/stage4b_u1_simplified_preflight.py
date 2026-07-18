"""Strict config loader and read-only preflight for simplified Stage4B-U1-D."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from stage4b_u1_common import (
    FROZEN_BATCH_SIZE,
    FROZEN_MAX_LENGTH,
    FROZEN_MODEL_NAME,
    IMPLEMENTATION_CHECKPOINT,
    OFFICIAL_CACHE_MEMBERS,
    OFFICIAL_DEVELOPMENT_QUERY_ID_SHA256,
    OFFICIAL_DEVELOPMENT_QUERIES,
    OFFICIAL_DEVELOPMENT_SAMPLE_ID_SHA256,
    OFFICIAL_EMBEDDING_DTYPE,
    OFFICIAL_ID_BOUND_CACHE_BYTES,
    OFFICIAL_ID_BOUND_CACHE_PATH,
    OFFICIAL_ID_BOUND_CACHE_SHA256,
    OFFICIAL_QUERY_EMBEDDING_SHAPE,
    OFFICIAL_UNIT_EMBEDDING_SHAPE,
    PROTOCOL_RELATIVE_PATH,
    STAGE4A_R2_SOURCE_AUDIT_SHA256,
    assert_no_prohibited_keys,
    git_blob_sha256,
    id_digest,
    load_jsonl,
    sha256_file,
)
from stage4b_u1_goldfree_controller import (
    query_identity_digests,
    validate_controller_inputs,
    validate_existing_embedding_cache,
)
from stage4b_u1_goldfree_retrieval import RetrievalConfig


CONFIG_SCHEMA_VERSION = "stage4b_u1_simplified_execution_v1"
RUN_ID = "stage4b_u1_d_official_dev4500_simplified_v1"
EXECUTION_PROFILE = "stage4b_u1_simplified_v1"
SIMPLIFIED_PROTOCOL_PATH = "docs/STAGE4B_U1_SIMPLIFIED_EXECUTION_PROTOCOL_V1.md"
OFFICIAL_CONFIG_PATH = "configs/stage4b_u1_d_official.json"
LEGACY_CONTROLLER_PATH = "scripts/stage4b_u1_goldfree_controller.py"
SIMPLIFIED_PREFLIGHT_PATH = "scripts/stage4b_u1_simplified_preflight.py"
SIMPLIFIED_RUNNER_PATH = "scripts/stage4b_u1_simplified_runner.py"
SIMPLIFIED_VERIFIER_PATH = "scripts/stage4b_u1_independent_verifier.py"
EVALUATOR_PATH = "scripts/stage4b_u1_evaluate.py"
LEGACY_IMPLEMENTATION_PATHS = (
    "scripts/stage4b_u1_common.py",
    "scripts/stage4b_u1_goldfree_retrieval.py",
    LEGACY_CONTROLLER_PATH,
    "scripts/stage4b_u1_verify.py",
)
IMPLEMENTATION_PATHS = (
    *LEGACY_IMPLEMENTATION_PATHS,
    SIMPLIFIED_PREFLIGHT_PATH,
    SIMPLIFIED_RUNNER_PATH,
    SIMPLIFIED_VERIFIER_PATH,
)
TOP_LEVEL_KEYS = {
    "schema_version",
    "run_id",
    "mode",
    "protocol",
    "implementation",
    "environment",
    "inputs",
    "embedding_cache",
    "retrieval",
    "controller",
    "outputs",
    "verification",
    "evaluation_contract",
    "retry_policy",
}
OFFICIAL_INPUTS = {
    "unlabeled_units": {
        "path": (
            "E:\\科研\\超粒球RAG_数据\\processed\\"
            "stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_units.jsonl"
        ),
        "sha256": "114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA",
    },
    "unlabeled_queries": {
        "path": (
            "E:\\科研\\超粒球RAG_数据\\processed\\"
            "stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_queries.jsonl"
        ),
        "sha256": "6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B",
    },
    "channel_audit": {
        "path": "results/stage4b_u1_d_official_dev4500_v2_3_1_controller_channel_audit.json",
        "sha256": "D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA",
    },
}
OFFICIAL_OUTPUTS = {
    "decisions": "results/stage4b_u1_d_official_dev4500_simplified_v1_decisions.jsonl",
    "rankings": "results/stage4b_u1_d_official_dev4500_simplified_v1_rankings.jsonl",
    "policy": "results/stage4b_u1_d_official_dev4500_simplified_v1_policy.json",
}
OFFICIAL_VERIFIED_PRE_GOLD = (
    "results/stage4b_u1_d_official_dev4500_simplified_v1_verified_pre_gold.json"
)
OFFICIAL_EVALUATION_OUTPUTS = {
    "query_audit": "results/stage4b_u1_d_official_dev4500_simplified_v1_query_audit.jsonl",
    "evaluation_summary": (
        "results/stage4b_u1_d_official_dev4500_simplified_v1_evaluation_summary.json"
    ),
}
SHA256_RE = re.compile(r"[0-9A-F]{64}")


@dataclass(frozen=True)
class RuntimeContext:
    config_path: Path
    config: dict[str, Any]
    config_sha256: str
    repo_root: Path
    units_path: Path
    queries_path: Path
    channel_audit_path: Path
    cache_path: Path
    units: list[dict[str, Any]]
    queries: list[dict[str, Any]]
    unit_embeddings: np.ndarray
    query_embeddings: np.ndarray
    cache_fingerprint: dict[str, Any]


def _reject_constant(value: str) -> None:
    raise ValueError(f"Non-finite JSON constant is forbidden: {value}")


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_strict_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(
            stream,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    if not isinstance(value, dict):
        raise ValueError("Execution config must be a JSON object")
    return value


def _exact_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    if set(value) != expected:
        raise ValueError(f"{label} key set differs: {sorted(set(value) ^ expected)}")
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _integer(value: Any, label: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    return value


def _sha256(value: Any, label: str) -> str:
    text = _string(value, label)
    if SHA256_RE.fullmatch(text) is None:
        raise ValueError(f"{label} must be an uppercase SHA-256")
    return text


def _assert_no_placeholders(value: Any, location: str = "config") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            _assert_no_placeholders(nested, f"{location}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _assert_no_placeholders(nested, f"{location}[{index}]")
    elif isinstance(value, str):
        normalized = value.strip().upper()
        if normalized in {"TBD", "TO_BE_BOUND"} or normalized == "0" * 64:
            raise ValueError(f"Placeholder value is forbidden at {location}")


def _retrieval_values(config: dict[str, Any]) -> dict[str, Any]:
    expected = {
        **RetrievalConfig().to_dict(),
        "model_name": FROZEN_MODEL_NAME,
        "max_length": FROZEN_MAX_LENGTH,
        "batch_size": FROZEN_BATCH_SIZE,
        "embedding_dtype": OFFICIAL_EMBEDDING_DTYPE,
        "scalar_dtype": "float64",
    }
    _exact_keys(config, set(expected), "retrieval")
    return expected


def validate_config_structure(
    config: dict[str, Any], *, synthetic_test_mode: bool = False
) -> None:
    _exact_keys(config, TOP_LEVEL_KEYS, "config")
    _assert_no_placeholders(config)
    assert_no_prohibited_keys(config, "execution_config")
    if config["schema_version"] != CONFIG_SCHEMA_VERSION:
        raise ValueError("Config schema_version differs")
    if config["run_id"] != RUN_ID or config["mode"] != "development":
        raise ValueError("Config run identity differs")

    protocol = _exact_keys(config["protocol"], {"path", "sha256"}, "protocol")
    if protocol["path"] != SIMPLIFIED_PROTOCOL_PATH:
        raise ValueError("Simplified protocol path differs")
    _sha256(protocol["sha256"], "protocol.sha256")

    implementation = _exact_keys(
        config["implementation"], {"code_commit", "files"}, "implementation"
    )
    commit = _string(implementation["code_commit"], "implementation.code_commit")
    if re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise ValueError("implementation.code_commit must be a full lowercase Git SHA")
    files = implementation["files"]
    if not isinstance(files, list) or len(files) != len(IMPLEMENTATION_PATHS):
        raise ValueError("implementation.files must bind exactly seven files")
    bound_paths: list[str] = []
    for index, item in enumerate(files):
        entry = _exact_keys(item, {"path", "sha256"}, f"implementation.files[{index}]")
        bound_paths.append(_string(entry["path"], f"implementation.files[{index}].path"))
        _sha256(entry["sha256"], f"implementation.files[{index}].sha256")
    if tuple(bound_paths) != IMPLEMENTATION_PATHS:
        raise ValueError("implementation.files path/order differs from the frozen seven")

    environment = _exact_keys(
        config["environment"],
        {"python_executable", "python_version", "required_packages"},
        "environment",
    )
    packages = _exact_keys(
        environment["required_packages"], {"numpy"}, "environment.required_packages"
    )
    _string(environment["python_executable"], "environment.python_executable")
    _string(environment["python_version"], "environment.python_version")
    _string(packages["numpy"], "environment.required_packages.numpy")
    if not synthetic_test_mode and environment != {
        "python_executable": "D:\\Users\\cc\\AppData\\Local\\Programs\\Python\\Python312\\python.exe",
        "python_version": "3.12.0",
        "required_packages": {"numpy": "2.5.1"},
    }:
        raise ValueError("Formal environment binding differs")

    inputs = _exact_keys(
        config["inputs"],
        {
            "unlabeled_units",
            "unlabeled_queries",
            "channel_audit",
            "query_count",
            "unit_count",
            "sample_id_sha256",
            "query_id_sha256",
            "query_id_namespace_rule",
        },
        "inputs",
    )
    for key in ("unlabeled_units", "unlabeled_queries", "channel_audit"):
        entry = _exact_keys(inputs[key], {"path", "sha256"}, f"inputs.{key}")
        _string(entry["path"], f"inputs.{key}.path")
        _sha256(entry["sha256"], f"inputs.{key}.sha256")
    _integer(inputs["query_count"], "inputs.query_count", minimum=1)
    _integer(inputs["unit_count"], "inputs.unit_count", minimum=1)
    _sha256(inputs["sample_id_sha256"], "inputs.sample_id_sha256")
    _sha256(inputs["query_id_sha256"], "inputs.query_id_sha256")
    if inputs["query_id_namespace_rule"] != "query_id == dataset + \"::\" + sample_id":
        raise ValueError("Query namespace rule differs")
    if not synthetic_test_mode:
        for key, expected in OFFICIAL_INPUTS.items():
            if inputs[key] != expected:
                raise ValueError(f"Formal inputs.{key} binding differs")
        if (
            inputs["query_count"] != OFFICIAL_DEVELOPMENT_QUERIES
            or inputs["unit_count"] != OFFICIAL_UNIT_EMBEDDING_SHAPE[0]
            or inputs["sample_id_sha256"] != OFFICIAL_DEVELOPMENT_SAMPLE_ID_SHA256
            or inputs["query_id_sha256"] != OFFICIAL_DEVELOPMENT_QUERY_ID_SHA256
        ):
            raise ValueError("Formal input identity boundary differs")

    cache = _exact_keys(
        config["embedding_cache"],
        {
            "path",
            "sha256",
            "bytes",
            "members",
            "unit_embeddings_shape",
            "query_embeddings_shape",
            "dtype",
            "model_name",
            "max_length",
        },
        "embedding_cache",
    )
    _string(cache["path"], "embedding_cache.path")
    _sha256(cache["sha256"], "embedding_cache.sha256")
    _integer(cache["bytes"], "embedding_cache.bytes", minimum=1)
    if not isinstance(cache["members"], list) or set(cache["members"]) != OFFICIAL_CACHE_MEMBERS:
        raise ValueError("Embedding cache members differ")
    for key in ("unit_embeddings_shape", "query_embeddings_shape"):
        shape = cache[key]
        if (
            not isinstance(shape, list)
            or len(shape) != 2
            or any(isinstance(value, bool) or not isinstance(value, int) or value <= 0 for value in shape)
        ):
            raise ValueError(f"embedding_cache.{key} must be a positive two-dimensional shape")
    if cache["dtype"] != OFFICIAL_EMBEDDING_DTYPE or cache["max_length"] != FROZEN_MAX_LENGTH:
        raise ValueError("Embedding cache dtype/max_length differs")
    _string(cache["model_name"], "embedding_cache.model_name")
    if not synthetic_test_mode and cache != {
        "path": OFFICIAL_ID_BOUND_CACHE_PATH,
        "sha256": OFFICIAL_ID_BOUND_CACHE_SHA256,
        "bytes": OFFICIAL_ID_BOUND_CACHE_BYTES,
        "members": sorted(OFFICIAL_CACHE_MEMBERS),
        "unit_embeddings_shape": list(OFFICIAL_UNIT_EMBEDDING_SHAPE),
        "query_embeddings_shape": list(OFFICIAL_QUERY_EMBEDDING_SHAPE),
        "dtype": OFFICIAL_EMBEDDING_DTYPE,
        "model_name": FROZEN_MODEL_NAME,
        "max_length": FROZEN_MAX_LENGTH,
    }:
        raise ValueError("Formal embedding-cache binding differs")

    retrieval = _exact_keys(config["retrieval"], set(_retrieval_values(config["retrieval"])), "retrieval")
    expected_retrieval = _retrieval_values(retrieval)
    for key, expected in expected_retrieval.items():
        if synthetic_test_mode and key == "model_name":
            _string(retrieval[key], "retrieval.model_name")
        elif retrieval[key] != expected:
            raise ValueError(f"Frozen retrieval value differs: {key}")
    if retrieval["model_name"] != cache["model_name"]:
        raise ValueError("Retrieval/cache model names differ")

    controller = _exact_keys(
        config["controller"],
        {"script", "embedding_cache_mode", "evaluation_labels_loaded"},
        "controller",
    )
    if controller != {
        "script": SIMPLIFIED_RUNNER_PATH,
        "embedding_cache_mode": "require-existing",
        "evaluation_labels_loaded": False,
    }:
        raise ValueError("Controller contract differs")

    outputs = _exact_keys(config["outputs"], set(OFFICIAL_OUTPUTS), "outputs")
    for key, value in outputs.items():
        _string(value, f"outputs.{key}")
    if not synthetic_test_mode and outputs != OFFICIAL_OUTPUTS:
        raise ValueError("Formal output paths differ")

    verification = _exact_keys(
        config["verification"],
        {"script", "decisions_input", "rankings_input", "policy_input", "output"},
        "verification",
    )
    if verification["script"] != SIMPLIFIED_VERIFIER_PATH:
        raise ValueError("Independent verifier path differs")
    for output_key, input_key in (
        ("decisions", "decisions_input"),
        ("rankings", "rankings_input"),
        ("policy", "policy_input"),
    ):
        if verification[input_key] != outputs[output_key]:
            raise ValueError(f"verification.{input_key} differs from outputs.{output_key}")
    _string(verification["output"], "verification.output")
    if not synthetic_test_mode and verification["output"] != OFFICIAL_VERIFIED_PRE_GOLD:
        raise ValueError("Formal verified-pre-Gold path differs")

    evaluation = _exact_keys(
        config["evaluation_contract"],
        {"authorized", "evaluator_script", "evaluator_script_sha256", "inputs", "outputs"},
        "evaluation_contract",
    )
    if evaluation["authorized"] is not False or evaluation["evaluator_script"] != EVALUATOR_PATH:
        raise ValueError("Evaluator must remain unauthorized and separately bound")
    _sha256(evaluation["evaluator_script_sha256"], "evaluation_contract.evaluator_script_sha256")
    evaluation_inputs = _exact_keys(
        evaluation["inputs"], {"rankings", "policy", "verified_pre_gold"}, "evaluation_contract.inputs"
    )
    if evaluation_inputs != {
        "rankings": outputs["rankings"],
        "policy": outputs["policy"],
        "verified_pre_gold": verification["output"],
    }:
        raise ValueError("Evaluator inputs differ from frozen pre-Gold outputs")
    evaluation_outputs = _exact_keys(
        evaluation["outputs"], {"query_audit", "evaluation_summary"}, "evaluation_contract.outputs"
    )
    for key, value in evaluation_outputs.items():
        _string(value, f"evaluation_contract.outputs.{key}")
    if not synthetic_test_mode and evaluation_outputs != OFFICIAL_EVALUATION_OUTPUTS:
        raise ValueError("Formal evaluator output paths differ")

    retry = _exact_keys(config["retry_policy"], {"automatic_retries"}, "retry_policy")
    if retry["automatic_retries"] != 0:
        raise ValueError("Automatic retries must be zero")


def resolve_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def implementation_hash_map(config: dict[str, Any]) -> dict[str, str]:
    return {
        str(item["path"]): str(item["sha256"])
        for item in config["implementation"]["files"]
    }


def _assert_commit_ancestor(repo_root: Path, commit: str) -> None:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"], cwd=repo_root
    )
    if result.returncode != 0:
        raise ValueError("Bound implementation commit is not an ancestor of HEAD")


def validate_code_bindings(
    config: dict[str, Any],
    repo_root: Path,
    *,
    verify_git_binding: bool,
) -> None:
    protocol_path = repo_root / config["protocol"]["path"]
    if sha256_file(protocol_path) != config["protocol"]["sha256"]:
        raise ValueError("Simplified protocol SHA-256 differs")
    for relative_path, expected_sha in implementation_hash_map(config).items():
        path = repo_root / relative_path
        if not path.is_file() or sha256_file(path) != expected_sha:
            raise ValueError(f"Implementation SHA-256 differs: {relative_path}")
        if verify_git_binding:
            commit = config["implementation"]["code_commit"]
            if git_blob_sha256(repo_root, commit, relative_path) != expected_sha:
                raise ValueError(f"Implementation Git blob differs: {relative_path}")
    evaluator = repo_root / config["evaluation_contract"]["evaluator_script"]
    if sha256_file(evaluator) != config["evaluation_contract"]["evaluator_script_sha256"]:
        raise ValueError("Evaluator SHA-256 differs")
    if verify_git_binding:
        _assert_commit_ancestor(repo_root, config["implementation"]["code_commit"])


def validate_formal_tracked_bindings(
    config_path: Path, config: dict[str, Any], repo_root: Path
) -> None:
    expected_config = (repo_root / OFFICIAL_CONFIG_PATH).resolve()
    if config_path.resolve() != expected_config:
        raise ValueError("Formal execution config path differs")
    expected = {
        OFFICIAL_CONFIG_PATH: sha256_file(config_path),
        config["protocol"]["path"]: config["protocol"]["sha256"],
        config["evaluation_contract"]["evaluator_script"]: config[
            "evaluation_contract"
        ]["evaluator_script_sha256"],
    }
    for relative_path, expected_sha in expected.items():
        try:
            tracked_sha = git_blob_sha256(repo_root, "HEAD", relative_path)
        except subprocess.CalledProcessError as error:
            raise ValueError(f"Formal binding is not tracked at HEAD: {relative_path}") from error
        if tracked_sha != expected_sha:
            raise ValueError(f"Formal tracked binding differs: {relative_path}")


def _validate_environment(config: dict[str, Any], *, synthetic_test_mode: bool) -> None:
    if synthetic_test_mode:
        return
    expected = config["environment"]
    if Path(sys.executable).resolve() != Path(expected["python_executable"]).resolve():
        raise ValueError("Runtime Python executable differs")
    version = ".".join(str(value) for value in sys.version_info[:3])
    if version != expected["python_version"]:
        raise ValueError("Runtime Python version differs")
    if importlib.metadata.version("numpy") != expected["required_packages"]["numpy"]:
        raise ValueError("Runtime NumPy version differs")


def _validate_channel_audit(
    audit: dict[str, Any],
    *,
    config: dict[str, Any],
    units_path: Path,
    queries_path: Path,
    sample_digest: str,
    query_digest: str,
    synthetic_test_mode: bool,
) -> None:
    assert_no_prohibited_keys(audit, "controller_channel_audit")
    expected_common = {
        "status": "CONTROLLER_CHANNEL_PREPARED_NO_RETRIEVAL_METRICS",
        "implementation_checkpoint": IMPLEMENTATION_CHECKPOINT,
        "run_role": "development",
        "sample_id_sha256": sample_digest,
        "query_id_sha256": query_digest,
    }
    for key, expected in expected_common.items():
        if audit.get(key) != expected:
            raise ValueError(f"Channel audit differs at {key}")
    if bool(audit.get("retrieval_metrics_computed")):
        raise ValueError("Channel audit reports retrieval metrics")
    if bool(audit.get("synthetic_test_mode")) != synthetic_test_mode:
        raise ValueError("Channel audit synthetic mode differs")
    hashes = audit.get("channel_hashes", {})
    if hashes.get("unlabeled_units") != sha256_file(units_path):
        raise ValueError("Channel audit unit hash differs")
    if hashes.get("unlabeled_queries") != sha256_file(queries_path):
        raise ValueError("Channel audit query hash differs")
    if synthetic_test_mode:
        if audit.get("boundary_status") != "SYNTHETIC_TEST_BOUNDARY":
            raise ValueError("Synthetic channel boundary differs")
    else:
        if audit.get("boundary_status") != "OFFICIAL_DEVELOPMENT_BOUNDARY_VERIFIED":
            raise ValueError("Official channel boundary differs")
        if audit.get("source_audit_sha256") != STAGE4A_R2_SOURCE_AUDIT_SHA256:
            raise ValueError("Channel audit source identity differs")
        if (
            audit.get("expected_sample_id_sha256") != config["inputs"]["sample_id_sha256"]
            or audit.get("expected_query_id_sha256") != config["inputs"]["query_id_sha256"]
        ):
            raise ValueError("Channel audit expected ID identities differ")


def _registered_paths(config: dict[str, Any], repo_root: Path) -> dict[str, Path]:
    return {
        "decisions": resolve_path(repo_root, config["outputs"]["decisions"]),
        "rankings": resolve_path(repo_root, config["outputs"]["rankings"]),
        "policy": resolve_path(repo_root, config["outputs"]["policy"]),
        "verified_pre_gold": resolve_path(repo_root, config["verification"]["output"]),
        "query_audit": resolve_path(
            repo_root, config["evaluation_contract"]["outputs"]["query_audit"]
        ),
        "evaluation_summary": resolve_path(
            repo_root, config["evaluation_contract"]["outputs"]["evaluation_summary"]
        ),
    }


def _validate_output_state(config: dict[str, Any], repo_root: Path, phase: str) -> None:
    paths = _registered_paths(config, repo_root)
    if len({path.resolve() for path in paths.values()}) != len(paths):
        raise ValueError("Registered future output paths are not distinct")
    if phase in {"preflight", "runner"}:
        forbidden = paths
    elif phase == "verifier":
        for key in ("decisions", "rankings", "policy"):
            if not paths[key].is_file():
                raise ValueError(f"Verifier input is absent: {paths[key]}")
        forbidden = {key: value for key, value in paths.items() if key not in {"decisions", "rankings", "policy"}}
    else:
        raise ValueError(f"Unknown preflight phase: {phase}")
    for path in forbidden.values():
        if path.exists():
            raise ValueError(f"Registered future output already exists: {path}")


def run_preflight(
    config_path: Path,
    *,
    repo_root: Path | None = None,
    synthetic_test_mode: bool = False,
    phase: str = "preflight",
    verify_git_binding: bool | None = None,
) -> RuntimeContext:
    root = (repo_root or Path(__file__).resolve().parents[1]).resolve()
    config_path = config_path.resolve()
    config = load_strict_json(config_path)
    validate_config_structure(config, synthetic_test_mode=synthetic_test_mode)
    validate_code_bindings(
        config,
        root,
        verify_git_binding=(not synthetic_test_mode if verify_git_binding is None else verify_git_binding),
    )
    if not synthetic_test_mode:
        validate_formal_tracked_bindings(config_path, config, root)
    _validate_environment(config, synthetic_test_mode=synthetic_test_mode)
    _validate_output_state(config, root, phase)

    units_path = resolve_path(root, config["inputs"]["unlabeled_units"]["path"])
    queries_path = resolve_path(root, config["inputs"]["unlabeled_queries"]["path"])
    channel_path = resolve_path(root, config["inputs"]["channel_audit"]["path"])
    cache_path = resolve_path(root, config["embedding_cache"]["path"])
    for label, path, expected_sha in (
        ("unlabeled units", units_path, config["inputs"]["unlabeled_units"]["sha256"]),
        ("unlabeled queries", queries_path, config["inputs"]["unlabeled_queries"]["sha256"]),
        ("channel audit", channel_path, config["inputs"]["channel_audit"]["sha256"]),
        ("embedding cache", cache_path, config["embedding_cache"]["sha256"]),
    ):
        if not path.is_file() or sha256_file(path) != expected_sha:
            raise ValueError(f"Frozen {label} SHA-256 differs")

    units = load_jsonl(units_path)
    queries = load_jsonl(queries_path)
    validate_controller_inputs(units, queries)
    sample_digest, query_digest = query_identity_digests(queries)
    if len(queries) != config["inputs"]["query_count"] or len(units) != config["inputs"]["unit_count"]:
        raise ValueError("Runtime input counts differ")
    if sample_digest != config["inputs"]["sample_id_sha256"]:
        raise ValueError("Runtime sample-ID digest differs")
    if query_digest != config["inputs"]["query_id_sha256"]:
        raise ValueError("Runtime query-ID digest differs")
    with channel_path.open("r", encoding="utf-8") as stream:
        audit = json.load(stream, object_pairs_hook=_strict_object, parse_constant=_reject_constant)
    _validate_channel_audit(
        audit,
        config=config,
        units_path=units_path,
        queries_path=queries_path,
        sample_digest=sample_digest,
        query_digest=query_digest,
        synthetic_test_mode=synthetic_test_mode,
    )

    unit_embeddings, query_embeddings, fingerprint = validate_existing_embedding_cache(
        cache_path,
        units,
        queries,
        config["embedding_cache"]["model_name"],
        config["embedding_cache"]["max_length"],
        config["embedding_cache"]["sha256"],
        synthetic_test_mode=synthetic_test_mode,
    )
    if fingerprint["bytes"] != config["embedding_cache"]["bytes"]:
        raise ValueError("Embedding cache byte count differs")
    if fingerprint["members"] != sorted(config["embedding_cache"]["members"]):
        raise ValueError("Embedding cache member list differs")
    if list(unit_embeddings.shape) != config["embedding_cache"]["unit_embeddings_shape"]:
        raise ValueError("Unit embedding shape differs")
    if list(query_embeddings.shape) != config["embedding_cache"]["query_embeddings_shape"]:
        raise ValueError("Query embedding shape differs")
    if not np.isfinite(unit_embeddings).all() or not np.isfinite(query_embeddings).all():
        raise ValueError("Embedding cache contains non-finite values")
    return RuntimeContext(
        config_path=config_path,
        config=config,
        config_sha256=sha256_file(config_path),
        repo_root=root,
        units_path=units_path,
        queries_path=queries_path,
        channel_audit_path=channel_path,
        cache_path=cache_path,
        units=units,
        queries=queries,
        unit_embeddings=unit_embeddings,
        query_embeddings=query_embeddings,
        cache_fingerprint=fingerprint,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--synthetic-test-mode", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    context = run_preflight(
        args.config,
        synthetic_test_mode=args.synthetic_test_mode,
        phase="preflight",
    )
    print(
        "STAGE4B_U1_SIMPLIFIED_PREFLIGHT_PASS "
        f"config_sha256={context.config_sha256}"
    )


if __name__ == "__main__":
    main()
