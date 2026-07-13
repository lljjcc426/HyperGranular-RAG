"""Construct and freeze the Stage4B-U1 policy without loading evaluation labels."""

from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from stage4b_u1_common import (
    FROZEN_BATCH_SIZE,
    FROZEN_MAX_LENGTH,
    FROZEN_MODEL_NAME,
    IMPLEMENTATION_CHECKPOINT,
    OFFICIAL_CACHE_MEMBERS,
    OFFICIAL_DEVELOPMENT_DATASET,
    OFFICIAL_DEVELOPMENT_QUERIES,
    OFFICIAL_DEVELOPMENT_QUERY_ID_SHA256,
    OFFICIAL_DEVELOPMENT_SAMPLE_ID_SHA256,
    OFFICIAL_EMBEDDING_DTYPE,
    OFFICIAL_EMBEDDING_NORM_TOLERANCE,
    OFFICIAL_ID_BOUND_CACHE_BYTES,
    OFFICIAL_ID_BOUND_CACHE_PATH,
    OFFICIAL_ID_BOUND_CACHE_SHA256,
    OFFICIAL_QUERY_EMBEDDING_SHAPE,
    OFFICIAL_UNIT_EMBEDDING_SHAPE,
    OFFICIAL_V2_3_1_ARTIFACT_PATHS,
    POLICY_IMPLEMENTATION_FILES,
    PROTOCOL_RELATIVE_PATH,
    SCHEMA_VERSION,
    STAGE4A_R2_SOURCE_AUDIT_SHA256,
    V2_2_DECISIONS_SHA256,
    V2_2_POLICY_PATH,
    V2_2_POLICY_SHA256,
    V2_2_RANKINGS_SHA256,
    assert_files_match_git_commit,
    assert_no_prohibited_keys,
    git_head,
    id_digest,
    implementation_hashes,
    load_json,
    load_jsonl,
    sha256_file,
    validate_unique_ids,
    write_json,
    write_jsonl,
)
from stage4b_u1_goldfree_retrieval import (
    RetrievalConfig,
    allocate_budget,
    build_query_decisions,
    fit_ecdf_references,
    normalize_matrix,
    score_rows,
    validate_ecdf_references,
)


UNIT_KEYS = {
    "unit_id",
    "query_id",
    "dataset",
    "sample_id",
    "doc_id",
    "title",
    "context_index",
    "sentence_id",
    "text",
}
QUERY_KEYS = {
    "query_id",
    "dataset",
    "sample_id",
    "question",
    "num_candidate_units",
}
CACHE_MODES = frozenset({"load-or-build", "require-existing"})
POLICY_ALLOWED_DRIFT_PATHS = (
    ("implementation_checkpoint",),
    ("git_commit_sha",),
    ("protocol_sha256",),
    ("implementation_hashes", "common_source_sha256"),
    ("implementation_hashes", "controller_source_sha256"),
    ("implementation_hashes", "verifier_source_sha256"),
    ("controller_source_sha256",),
    ("input_hashes", "channel_audit"),
)


def query_identity_digests(queries: list[dict[str, Any]]) -> tuple[str, str]:
    query_ids = [str(row["query_id"]) for row in queries]
    sample_ids = [str(row["sample_id"]) for row in queries]
    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Unlabeled sample IDs are not unique")
    for row, query_id, sample_id in zip(queries, query_ids, sample_ids, strict=True):
        dataset = str(row["dataset"])
        if query_id != f"{dataset}::{sample_id}":
            raise ValueError("Unlabeled query_id does not equal dataset::sample_id")
    return id_digest(sample_ids), id_digest(query_ids)


def validate_controller_inputs(
    units: list[dict[str, Any]], queries: list[dict[str, Any]]
) -> tuple[list[str], list[str]]:
    assert_no_prohibited_keys(units, "controller.units")
    assert_no_prohibited_keys(queries, "controller.queries")
    for row in units:
        if set(row) != UNIT_KEYS:
            raise ValueError(f"Unlabeled unit schema differs: {sorted(set(row) ^ UNIT_KEYS)}")
    for row in queries:
        if set(row) != QUERY_KEYS:
            raise ValueError(f"Unlabeled query schema differs: {sorted(set(row) ^ QUERY_KEYS)}")
    unit_ids = validate_unique_ids(units, "unit_id", "unlabeled unit")
    query_ids = validate_unique_ids(queries, "query_id", "unlabeled query")
    query_identity_digests(queries)
    query_set = set(query_ids)
    if {str(row["query_id"]) for row in units} != query_set:
        raise ValueError("Unlabeled unit/query ID sets differ")
    return unit_ids, query_ids


def embed_texts(
    texts: list[str], model_name: str, batch_size: int, max_length: int
) -> np.ndarray:
    import torch
    from transformers import AutoModel, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    chunks: list[np.ndarray] = []
    with torch.no_grad():
        for start in range(0, len(texts), batch_size):
            encoded = tokenizer(
                texts[start : start + batch_size],
                padding=True,
                truncation=True,
                max_length=max_length,
                return_tensors="pt",
            )
            encoded = {key: value.to(device) for key, value in encoded.items()}
            output = model(**encoded)
            mask = encoded["attention_mask"].unsqueeze(-1).expand(output.last_hidden_state.size()).float()
            pooled = torch.sum(output.last_hidden_state * mask, dim=1) / torch.clamp(
                mask.sum(dim=1), min=1e-9
            )
            pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
            chunks.append(pooled.cpu().numpy().astype("float32"))
    return np.vstack(chunks)


def validate_sha256(value: str | None, label: str) -> str:
    normalized = str(value or "").upper()
    if re.fullmatch(r"[0-9A-F]{64}", normalized) is None:
        raise ValueError(f"{label} must be a 64-character SHA-256")
    return normalized


def cache_fingerprint(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"Required embedding cache is not a regular file: {path}")
    try:
        with np.load(path, allow_pickle=False) as cache:
            members = sorted(str(value) for value in cache.files)
    except Exception as exc:
        raise ValueError(f"Embedding cache is not a readable NPZ: {path}") from exc
    return {
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
        "members": members,
    }


def validate_existing_embedding_cache(
    path: Path,
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    model_name: str,
    max_length: int,
    expected_sha256: str,
    *,
    synthetic_test_mode: bool,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    expected_sha = validate_sha256(expected_sha256, "Expected embedding cache SHA-256")
    fingerprint = cache_fingerprint(path)
    if fingerprint["sha256"] != expected_sha:
        raise ValueError("Embedding cache SHA-256 differs from the frozen value")
    if set(fingerprint["members"]) != OFFICIAL_CACHE_MEMBERS:
        raise ValueError("Embedding cache members differ from the exact frozen six")
    if not synthetic_test_mode:
        if path.resolve() != Path(OFFICIAL_ID_BOUND_CACHE_PATH).resolve():
            raise ValueError("Official embedding cache path differs from the frozen value")
        if expected_sha != OFFICIAL_ID_BOUND_CACHE_SHA256:
            raise ValueError("Official expected embedding cache SHA-256 differs")
        if int(fingerprint["bytes"]) != OFFICIAL_ID_BOUND_CACHE_BYTES:
            raise ValueError("Official embedding cache byte size differs")

    unit_ids = np.asarray([str(row["unit_id"]) for row in units])
    query_ids = np.asarray([str(row["query_id"]) for row in queries])
    with np.load(path, allow_pickle=False) as cache:
        cached_unit_ids = cache["unit_ids"].astype(str)
        cached_query_ids = cache["query_ids"].astype(str)
        cached_model = cache["model_name"].reshape(-1)
        cached_max_length = cache["max_length"].reshape(-1)
        unit_embeddings = np.asarray(cache["unit_embeddings"])
        query_embeddings = np.asarray(cache["query_embeddings"])

    if not np.array_equal(cached_unit_ids, unit_ids):
        raise ValueError("Embedding cache unit order differs")
    if not np.array_equal(cached_query_ids, query_ids):
        raise ValueError("Embedding cache query order differs")
    if len(cached_model) != 1 or str(cached_model[0]) != model_name:
        raise ValueError("Embedding cache model metadata differs")
    if len(cached_max_length) != 1 or int(cached_max_length[0]) != max_length:
        raise ValueError("Embedding cache max-length metadata differs")
    if unit_embeddings.dtype != np.dtype(OFFICIAL_EMBEDDING_DTYPE):
        raise ValueError("Embedding cache unit dtype differs from float32")
    if query_embeddings.dtype != np.dtype(OFFICIAL_EMBEDDING_DTYPE):
        raise ValueError("Embedding cache query dtype differs from float32")
    if unit_embeddings.ndim != 2 or query_embeddings.ndim != 2:
        raise ValueError("Embedding cache arrays must be two-dimensional")
    if unit_embeddings.shape[0] != len(unit_ids):
        raise ValueError("Embedding cache unit shape differs")
    if query_embeddings.shape[0] != len(query_ids):
        raise ValueError("Embedding cache query shape differs")
    if unit_embeddings.shape[1] <= 0 or unit_embeddings.shape[1] != query_embeddings.shape[1]:
        raise ValueError("Embedding cache dimensions differ")
    if not synthetic_test_mode:
        if tuple(unit_embeddings.shape) != OFFICIAL_UNIT_EMBEDDING_SHAPE:
            raise ValueError("Official unit embedding shape differs")
        if tuple(query_embeddings.shape) != OFFICIAL_QUERY_EMBEDDING_SHAPE:
            raise ValueError("Official query embedding shape differs")
    if not np.isfinite(unit_embeddings).all() or not np.isfinite(query_embeddings).all():
        raise ValueError("Embedding cache contains non-finite values")
    for label, matrix in (
        ("unit", unit_embeddings),
        ("query", query_embeddings),
    ):
        norms = np.linalg.norm(matrix.astype("float64"), axis=1)
        if np.max(np.abs(norms - 1.0)) > OFFICIAL_EMBEDDING_NORM_TOLERANCE:
            raise ValueError(f"Embedding cache {label} vectors are not normalized")
    return (
        normalize_matrix(unit_embeddings),
        normalize_matrix(query_embeddings),
        fingerprint,
    )


def load_or_build_embeddings(
    path: Path,
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    model_name: str,
    batch_size: int,
    max_length: int,
    *,
    cache_mode: str = "load-or-build",
    expected_sha256: str | None = None,
    synthetic_test_mode: bool = False,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any] | None]:
    if cache_mode not in CACHE_MODES:
        raise ValueError(f"Unknown embedding cache mode: {cache_mode}")
    if cache_mode == "require-existing":
        if expected_sha256 is None:
            raise ValueError("require-existing cache mode requires an expected SHA-256")
        return validate_existing_embedding_cache(
            path,
            units,
            queries,
            model_name,
            max_length,
            expected_sha256,
            synthetic_test_mode=synthetic_test_mode,
        )

    unit_ids = np.asarray([str(row["unit_id"]) for row in units])
    query_ids = np.asarray([str(row["query_id"]) for row in queries])
    if path.exists():
        with np.load(path, allow_pickle=False) as cache:
            required = set(OFFICIAL_CACHE_MEMBERS)
            if not required.issubset(cache.files):
                raise ValueError("Gold-free embedding cache lacks ID-bound metadata")
            if not np.array_equal(cache["unit_ids"].astype(str), unit_ids):
                raise ValueError("Embedding cache unit order differs")
            if not np.array_equal(cache["query_ids"].astype(str), query_ids):
                raise ValueError("Embedding cache query order differs")
            if str(cache["model_name"][0]) != model_name or int(cache["max_length"][0]) != max_length:
                raise ValueError("Embedding cache model metadata differs")
            return (
                normalize_matrix(cache["unit_embeddings"]),
                normalize_matrix(cache["query_embeddings"]),
                None,
            )

    unit_texts = [
        (str(row.get("title", "")) + ". " + str(row.get("text", ""))).strip()
        for row in units
    ]
    query_texts = [str(row["question"]) for row in queries]
    unit_embeddings = normalize_matrix(embed_texts(unit_texts, model_name, batch_size, max_length))
    query_embeddings = normalize_matrix(embed_texts(query_texts, model_name, batch_size, max_length))
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        unit_embeddings=unit_embeddings,
        query_embeddings=query_embeddings,
        unit_ids=unit_ids,
        query_ids=query_ids,
        model_name=np.asarray([model_name]),
        max_length=np.asarray([max_length], dtype="int64"),
    )
    return unit_embeddings, query_embeddings, None


def validate_channel_audit(
    audit: dict[str, Any],
    units_path: Path,
    queries_path: Path,
    queries: list[dict[str, Any]],
    *,
    mode: str,
    source_audit_path: Path | None,
    synthetic_test_mode: bool,
) -> None:
    query_ids = [str(row["query_id"]) for row in queries]
    sample_digest, query_digest = query_identity_digests(queries)
    if audit.get("status") != "CONTROLLER_CHANNEL_PREPARED_NO_RETRIEVAL_METRICS":
        raise ValueError("Channel audit status differs")
    if bool(audit.get("retrieval_metrics_computed")):
        raise ValueError("Channel audit reports retrieval metrics")
    if audit.get("implementation_checkpoint") != IMPLEMENTATION_CHECKPOINT:
        raise ValueError("Channel audit implementation checkpoint differs")
    if audit.get("run_role") != mode:
        raise ValueError("Channel audit/controller run roles differ")
    if bool(audit.get("synthetic_test_mode")) != synthetic_test_mode:
        raise ValueError("Channel audit/controller synthetic modes differ")
    if audit.get("sample_id_sha256") != sample_digest:
        raise ValueError("Channel audit sample digest differs")
    if audit.get("query_id_sha256") != query_digest:
        raise ValueError("Channel audit query digest differs")
    hashes = audit.get("channel_hashes", {})
    if hashes.get("unlabeled_units") != sha256_file(units_path):
        raise ValueError("Unlabeled-unit hash differs from channel audit")
    if hashes.get("unlabeled_queries") != sha256_file(queries_path):
        raise ValueError("Unlabeled-query hash differs from channel audit")
    if synthetic_test_mode:
        if audit.get("boundary_status") != "SYNTHETIC_TEST_BOUNDARY":
            raise ValueError("Synthetic channel boundary status differs")
        return
    if mode != "development":
        raise ValueError("Official Stage4B-U1-D controller mode must be development")
    if source_audit_path is None:
        raise ValueError("Official controller requires --source-audit")
    source_sha = sha256_file(source_audit_path)
    if source_sha != STAGE4A_R2_SOURCE_AUDIT_SHA256:
        raise ValueError("Controller source-audit SHA-256 differs from the frozen value")
    if audit.get("source_audit_sha256") != source_sha:
        raise ValueError("Channel audit source-audit SHA-256 differs")
    if audit.get("boundary_status") != "OFFICIAL_DEVELOPMENT_BOUNDARY_VERIFIED":
        raise ValueError("Official development boundary was not verified by the preparer")
    if len(query_ids) != OFFICIAL_DEVELOPMENT_QUERIES:
        raise ValueError("Official controller requires exactly 4,500 development queries")
    if {str(row["dataset"]) for row in queries} != {OFFICIAL_DEVELOPMENT_DATASET}:
        raise ValueError("Official controller dataset differs")
    if sample_digest != OFFICIAL_DEVELOPMENT_SAMPLE_ID_SHA256:
        raise ValueError("Official controller development sample-ID digest differs")
    if query_digest != OFFICIAL_DEVELOPMENT_QUERY_ID_SHA256:
        raise ValueError("Official controller development runtime query-ID digest differs")
    if audit.get("expected_sample_id_sha256") != OFFICIAL_DEVELOPMENT_SAMPLE_ID_SHA256:
        raise ValueError("Channel audit expected sample-ID digest differs")
    if audit.get("expected_query_id_sha256") != OFFICIAL_DEVELOPMENT_QUERY_ID_SHA256:
        raise ValueError("Channel audit expected runtime query-ID digest differs")


def assert_same_path(actual: Path, expected: str, label: str) -> None:
    if actual.resolve() != Path(expected).resolve():
        raise ValueError(f"{label} differs from the frozen v2.3.1 path")


def validate_formal_paths(
    *,
    units_path: Path,
    queries_path: Path,
    channel_audit_path: Path,
    embedding_cache: Path,
    decisions_output: Path,
    rankings_output: Path,
    policy_output: Path,
    reference_policy_path: Path | None,
) -> None:
    assert_same_path(
        units_path, OFFICIAL_V2_3_1_ARTIFACT_PATHS["unlabeled_units"], "Unlabeled units path"
    )
    assert_same_path(
        queries_path,
        OFFICIAL_V2_3_1_ARTIFACT_PATHS["unlabeled_queries"],
        "Unlabeled queries path",
    )
    assert_same_path(
        channel_audit_path,
        OFFICIAL_V2_3_1_ARTIFACT_PATHS["controller_channel_audit"],
        "Controller channel-audit path",
    )
    assert_same_path(
        embedding_cache, OFFICIAL_ID_BOUND_CACHE_PATH, "Embedding cache path"
    )
    assert_same_path(
        decisions_output, OFFICIAL_V2_3_1_ARTIFACT_PATHS["decisions"], "Decisions path"
    )
    assert_same_path(
        rankings_output, OFFICIAL_V2_3_1_ARTIFACT_PATHS["rankings"], "Rankings path"
    )
    assert_same_path(
        policy_output, OFFICIAL_V2_3_1_ARTIFACT_PATHS["policy"], "Policy path"
    )
    if reference_policy_path is None:
        raise ValueError("Official require-existing mode requires the frozen v2.2 policy")
    assert_same_path(reference_policy_path, V2_2_POLICY_PATH, "Reference policy path")


def validate_pending_output_targets(paths: list[Path]) -> None:
    if len({path.resolve() for path in paths}) != len(paths):
        raise ValueError("Controller output paths must be distinct")
    for path in paths:
        if path.exists():
            raise ValueError(f"Formal controller output path already exists: {path}")
        if not path.parent.is_dir():
            raise ValueError(f"Formal controller output parent does not exist: {path.parent}")


def write_jsonl_in_existing_directory(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_json_in_existing_directory(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def assert_cache_fingerprint_unchanged(
    path: Path, expected: dict[str, Any], label: str
) -> None:
    actual = cache_fingerprint(path)
    if actual != expected:
        raise ValueError(f"Embedding cache fingerprint drifted {label}")


def remove_policy_path(value: dict[str, Any], path: tuple[str, ...]) -> None:
    current: dict[str, Any] = value
    for key in path[:-1]:
        nested = current.get(key)
        if not isinstance(nested, dict):
            raise ValueError(f"Policy lacks registered drift path: {'.'.join(path)}")
        current = nested
    if path[-1] not in current:
        raise ValueError(f"Policy lacks registered drift path: {'.'.join(path)}")
    del current[path[-1]]


def validate_policy_equivalence(
    current_policy: dict[str, Any], reference_policy: dict[str, Any]
) -> None:
    current = copy.deepcopy(current_policy)
    reference = copy.deepcopy(reference_policy)
    for path in POLICY_ALLOWED_DRIFT_PATHS:
        remove_policy_path(current, path)
        remove_policy_path(reference, path)
    if current != reference:
        raise ValueError("v2.3.1 policy differs outside the registered binding fields")


def validate_formal_pending_equivalence(
    *,
    decisions_path: Path,
    rankings_path: Path,
    policy: dict[str, Any],
    reference_policy_path: Path,
) -> None:
    if sha256_file(decisions_path) != V2_2_DECISIONS_SHA256:
        raise ValueError("v2.3.1 decisions differ from the frozen v2.2 bytes")
    if sha256_file(rankings_path) != V2_2_RANKINGS_SHA256:
        raise ValueError("v2.3.1 rankings differ from the frozen v2.2 bytes")
    if sha256_file(reference_policy_path) != V2_2_POLICY_SHA256:
        raise ValueError("Reference v2.2 policy SHA-256 differs")
    validate_policy_equivalence(policy, load_json(reference_policy_path))


def remove_outputs_created_by_this_run(paths: list[Path]) -> None:
    for path in paths:
        if path.exists():
            path.unlink()


def promote_pending_outputs(pairs: list[tuple[Path, Path]]) -> None:
    targets = [target for _, target in pairs]
    validate_pending_output_targets(targets)
    created: list[Path] = []
    try:
        for pending, target in pairs:
            with pending.open("rb") as source, target.open("xb") as destination:
                created.append(target)
                shutil.copyfileobj(source, destination, length=1024 * 1024)
            if sha256_file(target) != sha256_file(pending):
                raise ValueError(f"Promoted controller output hash differs: {target}")
    except Exception:
        remove_outputs_created_by_this_run(created)
        raise


def run_controller(
    *,
    units_path: Path,
    queries_path: Path,
    channel_audit_path: Path,
    embedding_cache: Path,
    decisions_output: Path,
    rankings_output: Path,
    policy_output: Path,
    mode: str,
    policy_input: Path | None,
    model_name: str,
    batch_size: int,
    max_length: int,
    config: RetrievalConfig,
    controller_source: Path,
    source_audit_path: Path | None = None,
    synthetic_test_mode: bool = False,
    embedding_cache_mode: str = "load-or-build",
    expected_embedding_cache_sha256: str | None = None,
    reference_policy_path: Path | None = None,
) -> dict[str, Any]:
    if mode not in {"development", "reservation"}:
        raise ValueError(f"Unknown controller mode: {mode}")
    if batch_size <= 0:
        raise ValueError("Embedding batch size must be positive")
    if not synthetic_test_mode:
        if mode != "development":
            raise ValueError("Official Stage4B-U1-D controller mode must be development")
        if model_name != FROZEN_MODEL_NAME:
            raise ValueError("Official Stage4B-U1 encoder differs from the frozen model")
        if max_length != FROZEN_MAX_LENGTH:
            raise ValueError("Official Stage4B-U1 max length differs from 192")
        if batch_size != FROZEN_BATCH_SIZE:
            raise ValueError("Official Stage4B-U1 batch size differs from 64")
        if config != RetrievalConfig():
            raise ValueError("Official Stage4B-U1 runs must use the frozen retrieval configuration")
        if embedding_cache_mode != "require-existing":
            raise ValueError("Official Stage4B-U1 requires existing-cache-only mode")
        expected_sha = validate_sha256(
            expected_embedding_cache_sha256,
            "Official expected embedding cache SHA-256",
        )
        if expected_sha != OFFICIAL_ID_BOUND_CACHE_SHA256:
            raise ValueError("Official expected embedding cache SHA-256 differs")
        validate_formal_paths(
            units_path=units_path,
            queries_path=queries_path,
            channel_audit_path=channel_audit_path,
            embedding_cache=embedding_cache,
            decisions_output=decisions_output,
            rankings_output=rankings_output,
            policy_output=policy_output,
            reference_policy_path=reference_policy_path,
        )
        validate_pending_output_targets(
            [decisions_output, rankings_output, policy_output]
        )
    units = load_jsonl(units_path)
    queries = load_jsonl(queries_path)
    _, query_ids = validate_controller_inputs(units, queries)
    validate_channel_audit(
        load_json(channel_audit_path),
        units_path,
        queries_path,
        queries,
        mode=mode,
        source_audit_path=source_audit_path,
        synthetic_test_mode=synthetic_test_mode,
    )
    unit_embeddings, query_embeddings, initial_cache_fingerprint = load_or_build_embeddings(
        embedding_cache,
        units,
        queries,
        model_name,
        batch_size,
        max_length,
        cache_mode=embedding_cache_mode,
        expected_sha256=expected_embedding_cache_sha256,
        synthetic_test_mode=synthetic_test_mode,
    )
    rows = build_query_decisions(
        units, queries, unit_embeddings, query_embeddings, config
    )

    parent_policy_sha: str | None = None
    if mode == "development":
        references = fit_ecdf_references(rows)
    else:
        if policy_input is None:
            raise ValueError("Reservation mode requires the frozen development policy")
        parent = load_json(policy_input)
        if parent.get("run_role") != "development":
            raise ValueError("Reservation parent policy is not a development policy")
        if parent.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("Reservation parent policy schema differs")
        if parent.get("retrieval_config") != config.to_dict():
            raise ValueError("Reservation retrieval config differs from the frozen policy")
        references = parent["ecdf_references"]
        validate_ecdf_references(references)
        parent_policy_sha = sha256_file(policy_input)
    score_rows(rows, references)
    allocation = allocate_budget(rows, config.budget_fraction)

    decision_fields = {
        "query_id",
        "dataset",
        "sample_id",
        "ball_score_margin",
        "boundary_margin",
        "selected_edge_count",
        "planned_insert_count",
        "feasible",
        "u_margin",
        "u_boundary",
        "r_edge",
        "r_candidate",
        "uncertainty",
        "readiness",
        "score",
        "tie_hash",
        "ordered_rank",
        "trigger_u1",
    }
    decisions = [{key: row[key] for key in decision_fields} for row in rows]
    rankings = [
        {
            "query_id": row["query_id"],
            "dataset": row["dataset"],
            "sample_id": row["sample_id"],
            "trigger_u1": row["trigger_u1"],
            "planned_insert_count": row["planned_insert_count"],
            "dense_top20_unit_ids": row["dense_top20_unit_ids"],
            "q25_top20_unit_ids": row["q25_top20_unit_ids"],
            "q25_inserted_unit_ids": row["q25_inserted_unit_ids"],
            "final_top20_unit_ids": row["final_top20_unit_ids"],
            "final_inserted_unit_ids": row["final_inserted_unit_ids"],
        }
        for row in rows
    ]
    assert_no_prohibited_keys(decisions, "controller.decisions")
    assert_no_prohibited_keys(rankings, "controller.rankings")
    repo_root = controller_source.resolve().parents[1]
    commit_sha = git_head(repo_root)
    bound_files = [*POLICY_IMPLEMENTATION_FILES.values(), PROTOCOL_RELATIVE_PATH]
    if not synthetic_test_mode:
        assert_files_match_git_commit(repo_root, commit_sha, bound_files)
    source_hashes = implementation_hashes(repo_root)
    protocol_sha = sha256_file(repo_root / PROTOCOL_RELATIVE_PATH)
    source_audit_sha = (
        sha256_file(source_audit_path) if source_audit_path is not None else None
    )

    def build_policy(decisions_path: Path, rankings_path: Path) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "implementation_checkpoint": IMPLEMENTATION_CHECKPOINT,
            "protocol": PROTOCOL_RELATIVE_PATH,
            "protocol_sha256": protocol_sha,
            "status": (
                "SYNTHETIC_TEST_ONLY"
                if synthetic_test_mode
                else "POLICY_FROZEN_BEFORE_EVALUATION"
            ),
            "run_role": mode,
            "git_commit_sha": commit_sha,
            "sample_id_sha256": id_digest(str(row["sample_id"]) for row in queries),
            "query_id_sha256": id_digest(query_ids),
            "queries": len(queries),
            "units": len(units),
            "model_name": model_name,
            "max_length": max_length,
            "batch_size": batch_size,
            "retrieval_config": config.to_dict(),
            "ecdf_definition": (
                "(count_less + 0.5 * count_equal) / n using exact float64 equality"
            ),
            "ecdf_references": references,
            "allocation": allocation,
            "input_hashes": {
                "unlabeled_units": sha256_file(units_path),
                "unlabeled_queries": sha256_file(queries_path),
                "channel_audit": sha256_file(channel_audit_path),
                "embedding_cache": sha256_file(embedding_cache),
                "source_audit": source_audit_sha,
            },
            "output_hashes": {
                "decisions": sha256_file(decisions_path),
                "rankings": sha256_file(rankings_path),
            },
            "implementation_hashes": source_hashes,
            "controller_source_sha256": source_hashes["controller_source_sha256"],
            "parent_development_policy_sha256": parent_policy_sha,
            "evaluation_labels_loaded": False,
        }

    if embedding_cache_mode != "require-existing":
        write_jsonl(decisions_output, decisions)
        write_jsonl(rankings_output, rankings)
        policy = build_policy(decisions_output, rankings_output)
        write_json(policy_output, policy)
        return policy

    if initial_cache_fingerprint is None:
        raise ValueError("require-existing cache mode lacks an initial fingerprint")
    targets = [decisions_output, rankings_output, policy_output]
    validate_pending_output_targets(targets)
    with tempfile.TemporaryDirectory(prefix="stage4b_u1_v2_3_1_pending_") as directory:
        pending_root = Path(directory)
        pending_decisions = pending_root / "decisions.jsonl"
        pending_rankings = pending_root / "rankings.jsonl"
        pending_policy = pending_root / "policy.json"
        write_jsonl_in_existing_directory(pending_decisions, decisions)
        write_jsonl_in_existing_directory(pending_rankings, rankings)
        policy = build_policy(pending_decisions, pending_rankings)
        write_json_in_existing_directory(pending_policy, policy)

        assert_cache_fingerprint_unchanged(
            embedding_cache, initial_cache_fingerprint, "after controller computation"
        )
        if not synthetic_test_mode:
            if reference_policy_path is None:
                raise ValueError("Official policy equivalence requires a reference policy")
            validate_formal_pending_equivalence(
                decisions_path=pending_decisions,
                rankings_path=pending_rankings,
                policy=policy,
                reference_policy_path=reference_policy_path,
            )
        assert_cache_fingerprint_unchanged(
            embedding_cache, initial_cache_fingerprint, "after equivalence checks"
        )

        pairs = [
            (pending_decisions, decisions_output),
            (pending_rankings, rankings_output),
            (pending_policy, policy_output),
        ]
        promote_pending_outputs(pairs)
        try:
            assert_cache_fingerprint_unchanged(
                embedding_cache, initial_cache_fingerprint, "after output promotion"
            )
        except Exception:
            remove_outputs_created_by_this_run(targets)
            raise
    return policy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", required=True, type=Path)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--channel-audit", required=True, type=Path)
    parser.add_argument("--embedding-cache", required=True, type=Path)
    parser.add_argument("--decisions-output", required=True, type=Path)
    parser.add_argument("--rankings-output", required=True, type=Path)
    parser.add_argument("--policy-output", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("development", "reservation"))
    parser.add_argument("--policy-input", type=Path)
    parser.add_argument("--source-audit", type=Path)
    parser.add_argument("--model-name", default=FROZEN_MODEL_NAME)
    parser.add_argument("--batch-size", type=int, default=FROZEN_BATCH_SIZE)
    parser.add_argument("--max-length", type=int, default=FROZEN_MAX_LENGTH)
    parser.add_argument(
        "--embedding-cache-mode",
        choices=tuple(sorted(CACHE_MODES)),
        default="load-or-build",
    )
    parser.add_argument("--expected-embedding-cache-sha256")
    parser.add_argument("--reference-policy", type=Path)
    parser.add_argument("--synthetic-test-mode", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_controller(
        units_path=args.units,
        queries_path=args.queries,
        channel_audit_path=args.channel_audit,
        embedding_cache=args.embedding_cache,
        decisions_output=args.decisions_output,
        rankings_output=args.rankings_output,
        policy_output=args.policy_output,
        mode=args.mode,
        policy_input=args.policy_input,
        model_name=args.model_name,
        batch_size=args.batch_size,
        max_length=args.max_length,
        config=RetrievalConfig(),
        controller_source=Path(__file__),
        source_audit_path=args.source_audit,
        synthetic_test_mode=args.synthetic_test_mode,
        embedding_cache_mode=args.embedding_cache_mode,
        expected_embedding_cache_sha256=args.expected_embedding_cache_sha256,
        reference_policy_path=args.reference_policy,
    )


if __name__ == "__main__":
    main()
