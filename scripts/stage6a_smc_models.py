"""Frozen Qwen3 embedding/reranking runtime for Stage6A."""

from __future__ import annotations

import gc
import importlib.metadata
import json
import math
import os
import platform
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from stage6a_smc_common import (
    EMBEDDING_ID,
    EMBEDDING_REVISION,
    RERANKER_ID,
    RERANKER_REVISION,
    RETRIEVAL_INSTRUCTION,
    id_digest,
    require_native_string,
    validate_snapshot,
)
from stage6a_smc_retrieval import dense_common_pool


EMBEDDING_MAX_LENGTH = 512
EMBEDDING_BATCH_SIZE = 16
RERANKER_MAX_LENGTH = 512
RERANKER_BATCH_SIZE = 16
RERANKER_PREFIX = (
    '<|im_start|>system\nJudge whether the Document meets the requirements '
    'based on the Query and the Instruct provided. Note that the answer can '
    'only be "yes" or "no".<|im_end|>\n<|im_start|>user\n'
)
RERANKER_SUFFIX = (
    "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
)


def set_frozen_runtime(environment: dict[str, Any]) -> None:
    required = environment.get("environment_variables")
    if not isinstance(required, dict) or not required:
        raise ValueError("environment variable binding is missing")
    for name, expected in required.items():
        if os.environ.get(name) != expected:
            raise RuntimeError(f"frozen environment variable differs: {name}")
    packages = environment.get("packages")
    if not isinstance(packages, dict) or not packages:
        raise ValueError("package binding is missing")
    for name, expected in packages.items():
        if importlib.metadata.version(name) != expected:
            raise RuntimeError(f"frozen package differs: {name}")
    python = environment.get("python")
    runtime = environment.get("runtime")
    gpu = environment.get("gpu")
    if not all(isinstance(value, dict) for value in (python, runtime, gpu)):
        raise ValueError("runtime binding is incomplete")
    import torch

    if (
        platform.python_version() != python["version"]
        or Path(sys.executable) != Path(python["executable"])
    ):
        raise RuntimeError("frozen Python runtime differs")
    if (
        torch.__version__ != runtime["torch"]
        or torch.version.cuda != runtime["cuda"]
        or int(torch.backends.cudnn.version()) != runtime["cudnn"]
        or platform.platform() != runtime["platform"]
    ):
        raise RuntimeError("frozen torch/CUDA runtime differs")
    if (
        not torch.cuda.is_available()
        or torch.cuda.get_device_name(0) != gpu["name"]
        or int(torch.cuda.get_device_properties(0).total_memory)
        != gpu["total_memory_bytes"]
    ):
        raise RuntimeError("frozen GPU identity differs")
    torch.manual_seed(0)
    torch.cuda.manual_seed_all(0)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False


def validate_models(
    config: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], Path, Path]:
    models = config.get("models")
    if not isinstance(models, dict):
        raise ValueError("models binding is missing")
    embedding = models.get("embedding")
    reranker = models.get("reranker")
    if not isinstance(embedding, dict) or not isinstance(reranker, dict):
        raise ValueError("Qwen3 model bindings are incomplete")
    if (embedding.get("model_id"), embedding.get("revision")) != (
        EMBEDDING_ID,
        EMBEDDING_REVISION,
    ):
        raise ValueError("embedding model identity differs")
    if (reranker.get("model_id"), reranker.get("revision")) != (
        RERANKER_ID,
        RERANKER_REVISION,
    ):
        raise ValueError("reranker model identity differs")
    embedding_snapshot = Path(
        require_native_string(embedding.get("snapshot_path"), "embedding.snapshot_path")
    )
    reranker_snapshot = Path(
        require_native_string(reranker.get("snapshot_path"), "reranker.snapshot_path")
    )
    validate_snapshot(embedding_snapshot, embedding, "stage6a.embedding")
    validate_snapshot(reranker_snapshot, reranker, "stage6a.reranker")
    return embedding, reranker, embedding_snapshot, reranker_snapshot


def _normalize(matrix: Any) -> np.ndarray:
    output = np.asarray(matrix, dtype="float32")
    if output.ndim != 2 or not np.isfinite(output).all():
        raise ValueError("embedding matrix must be finite float32")
    norms = np.linalg.norm(output, axis=1, keepdims=True)
    if np.any(norms <= 0.0):
        raise ValueError("embedding matrix contains zero vectors")
    output = np.asarray(output / norms, dtype="float32")
    if not np.isfinite(output).all():
        raise ValueError("normalized embeddings are non-finite")
    return output


def _query_text(question: str) -> str:
    return f"Instruct: {RETRIEVAL_INSTRUCTION}\nQuery:{question}"


def embed_texts(texts: list[str], snapshot: Path) -> tuple[np.ndarray, int, float]:
    import torch
    from transformers import AutoModel, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        snapshot, local_files_only=True, padding_side="left"
    )
    model = AutoModel.from_pretrained(
        snapshot, local_files_only=True, dtype=torch.float16
    )
    model.eval().to("cuda")
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    chunks: list[np.ndarray] = []
    with torch.no_grad():
        for start in range(0, len(texts), EMBEDDING_BATCH_SIZE):
            encoded = tokenizer(
                texts[start : start + EMBEDDING_BATCH_SIZE],
                padding=True,
                truncation=True,
                max_length=EMBEDDING_MAX_LENGTH,
                return_tensors="pt",
            )
            encoded = {key: value.to("cuda") for key, value in encoded.items()}
            output = model(**encoded).last_hidden_state
            if bool(torch.all(encoded["attention_mask"][:, -1] == 1)):
                pooled = output[:, -1]
            else:
                positions = encoded["attention_mask"].sum(dim=1) - 1
                pooled = output[
                    torch.arange(output.shape[0], device=output.device),
                    positions,
                ]
            pooled = torch.nn.functional.normalize(pooled.float(), p=2, dim=1)
            chunks.append(pooled.cpu().numpy().astype("float32"))
    seconds = time.perf_counter() - started
    peak = int(torch.cuda.max_memory_allocated())
    del model, tokenizer
    gc.collect()
    torch.cuda.empty_cache()
    return _normalize(np.vstack(chunks)), peak, seconds


def embedding_cache_metadata(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    binding: dict[str, Any],
) -> dict[str, Any]:
    return {
        "batch_size": EMBEDDING_BATCH_SIZE,
        "document_input": "title + '. ' + unit_text",
        "dtype": "float16_model_float32_output",
        "instruction": RETRIEVAL_INSTRUCTION,
        "max_length": EMBEDDING_MAX_LENGTH,
        "model_id": EMBEDDING_ID,
        "pooling": "last_non_padding_token_then_l2",
        "query_input": "Instruct: <instruction>\\nQuery:<question>",
        "query_id_sha256": id_digest(row["query_id"] for row in queries),
        "revision": EMBEDDING_REVISION,
        "snapshot_files_sha256": binding["files_sha256"],
        "unit_id_sha256": id_digest(row["unit_id"] for row in units),
    }


def write_embedding_cache(
    path: Path,
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
    metadata: dict[str, Any],
) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite embedding cache: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(path.name + ".pending")
    if pending.exists():
        raise FileExistsError(f"refusing to overwrite pending cache: {pending}")
    try:
        with pending.open("xb") as handle:
            np.savez(
                handle,
                metadata_json=np.asarray(json.dumps(metadata, sort_keys=True)),
                query_embeddings=query_embeddings,
                query_ids=np.asarray([row["query_id"] for row in queries]),
                unit_embeddings=unit_embeddings,
                unit_ids=np.asarray([row["unit_id"] for row in units]),
            )
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(pending, path)
    except Exception:
        pending.unlink(missing_ok=True)
        raise


def load_embedding_cache(
    path: Path,
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray]:
    with np.load(path, allow_pickle=False) as cache:
        required = {
            "metadata_json",
            "query_embeddings",
            "query_ids",
            "unit_embeddings",
            "unit_ids",
        }
        if set(cache.files) != required:
            raise ValueError(f"{path}: embedding cache schema differs")
        if json.loads(str(cache["metadata_json"].item())) != metadata:
            raise ValueError(f"{path}: embedding cache metadata differs")
        if cache["unit_ids"].tolist() != [row["unit_id"] for row in units]:
            raise ValueError(f"{path}: embedding unit order differs")
        if cache["query_ids"].tolist() != [row["query_id"] for row in queries]:
            raise ValueError(f"{path}: embedding query order differs")
        unit_embeddings = _normalize(cache["unit_embeddings"])
        query_embeddings = _normalize(cache["query_embeddings"])
    return unit_embeddings, query_embeddings


def build_or_load_embeddings(
    path: Path,
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    binding: dict[str, Any],
    snapshot: Path,
    allow_build: bool,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    metadata = embedding_cache_metadata(units, queries, binding)
    if path.is_file():
        started = time.perf_counter()
        unit, query = load_embedding_cache(path, units, queries, metadata)
        return unit, query, {
            "cache_loaded": True,
            "gpu_peak_memory_bytes": 0,
            "seconds": time.perf_counter() - started,
        }
    if not allow_build:
        raise FileNotFoundError("rerun requires frozen Stage6A embedding cache")
    documents = [
        (row["title"] + ". " + row["text"]).strip() for row in units
    ]
    unit, unit_peak, unit_seconds = embed_texts(documents, snapshot)
    query, query_peak, query_seconds = embed_texts(
        [_query_text(row["question"]) for row in queries], snapshot
    )
    write_embedding_cache(path, units, queries, unit, query, metadata)
    return unit, query, {
        "cache_loaded": False,
        "gpu_peak_memory_bytes": max(unit_peak, query_peak),
        "seconds": unit_seconds + query_seconds,
    }


def _reranker_inputs(
    tokenizer: Any, pairs: list[tuple[str, str]]
) -> dict[str, Any]:
    prefix_tokens = tokenizer.encode(RERANKER_PREFIX, add_special_tokens=False)
    suffix_tokens = tokenizer.encode(RERANKER_SUFFIX, add_special_tokens=False)
    bodies = [
        (
            f"<Instruct>: {RETRIEVAL_INSTRUCTION}\n"
            f"<Query>: {query}\n<Document>: {document}"
        )
        for query, document in pairs
    ]
    inputs = tokenizer(
        bodies,
        padding=False,
        truncation="longest_first",
        return_attention_mask=False,
        max_length=RERANKER_MAX_LENGTH - len(prefix_tokens) - len(suffix_tokens),
    )
    for index, value in enumerate(inputs["input_ids"]):
        inputs["input_ids"][index] = prefix_tokens + value + suffix_tokens
    return tokenizer.pad(inputs, padding=True, return_tensors="pt")


def rerank_pairs(
    pairs: list[tuple[str, str]], snapshot: Path
) -> tuple[list[float], int, float]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        snapshot, local_files_only=True, padding_side="left"
    )
    model = AutoModelForCausalLM.from_pretrained(
        snapshot, local_files_only=True, dtype=torch.float16
    )
    model.eval().to("cuda")
    false_id = tokenizer.convert_tokens_to_ids("no")
    true_id = tokenizer.convert_tokens_to_ids("yes")
    if false_id == tokenizer.unk_token_id or true_id == tokenizer.unk_token_id:
        raise ValueError("reranker yes/no token identity differs")
    scores: list[float] = []
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    with torch.no_grad():
        for start in range(0, len(pairs), RERANKER_BATCH_SIZE):
            inputs = _reranker_inputs(
                tokenizer, pairs[start : start + RERANKER_BATCH_SIZE]
            )
            inputs = {key: value.to("cuda") for key, value in inputs.items()}
            logits = model(**inputs).logits[:, -1, :]
            pair_logits = torch.stack(
                [logits[:, false_id], logits[:, true_id]], dim=1
            )
            probabilities = torch.softmax(pair_logits.float(), dim=1)[:, 1]
            scores.extend(
                float(value)
                for value in probabilities.cpu().numpy().astype("float32")
            )
    seconds = time.perf_counter() - started
    peak = int(torch.cuda.max_memory_allocated())
    del model, tokenizer
    gc.collect()
    torch.cuda.empty_cache()
    if len(scores) != len(pairs) or any(not math.isfinite(value) for value in scores):
        raise ValueError("reranker output differs")
    return scores, peak, seconds


def build_reranker_rows(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
    snapshot: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_query: dict[str, list[int]] = defaultdict(list)
    for index, unit in enumerate(units):
        by_query[unit["query_id"]].append(index)
    pool_by_query: list[list[int]] = []
    pairs: list[tuple[str, str]] = []
    for query_index, query in enumerate(queries):
        pool, _ = dense_common_pool(
            by_query[query["query_id"]],
            units,
            unit_embeddings,
            query_embeddings[query_index],
        )
        pool_by_query.append(pool)
        pairs.extend(
            (
                query["question"],
                (units[index]["title"] + ". " + units[index]["text"]).strip(),
            )
            for index in pool
        )
    scores, peak, seconds = rerank_pairs(pairs, snapshot)
    rows: list[dict[str, Any]] = []
    offset = 0
    for query, pool in zip(queries, pool_by_query, strict=True):
        query_scores = scores[offset : offset + len(pool)]
        offset += len(pool)
        rows.append(
            {
                "common_pool_unit_ids": [
                    units[index]["unit_id"] for index in pool
                ],
                "dataset": query["dataset"],
                "query_id": query["query_id"],
                "reranker_scores": query_scores,
                "sample_id": query["sample_id"],
            }
        )
    if offset != len(scores):
        raise ValueError("reranker score partition differs")
    return rows, {
        "gpu_peak_memory_bytes": peak,
        "pair_count": len(pairs),
        "seconds": seconds,
    }


__all__ = [
    "EMBEDDING_BATCH_SIZE",
    "EMBEDDING_MAX_LENGTH",
    "RERANKER_BATCH_SIZE",
    "RERANKER_MAX_LENGTH",
    "build_or_load_embeddings",
    "build_reranker_rows",
    "embedding_cache_metadata",
    "rerank_pairs",
    "set_frozen_runtime",
    "validate_models",
]
