"""Gold-free Stage4F Dense/static-q25 retrieval and Qwen generation transaction."""

from __future__ import annotations

import argparse
import gc
import importlib.metadata
import json
import os
import platform
import sys
import time
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from stage4f_xdr_common import (
    DATASET,
    ENCODER_ID,
    ENCODER_REVISION,
    GENERATOR_ID,
    GENERATOR_REVISION,
    SAMPLE_SIZE,
    SCHEMA_VERSION,
    assert_file_identity,
    assert_implementation_binding,
    assert_no_gold_fields,
    file_identity,
    id_digest,
    load_json,
    load_jsonl,
    method_order,
    render_json,
    render_jsonl,
    require_json_bool,
    require_json_int,
    require_native_string,
    sha256_bytes,
    write_new_files_atomically,
)
from stage4f_xdr_retrieval import RetrievalConfig, build_query_decisions


SYSTEM_MESSAGE = (
    "Answer the question using only the provided evidence. Return only the "
    "shortest final answer. If the evidence is insufficient, return UNKNOWN."
)
METHODS = ("DENSE_TOP20", "STATIC_Q25_TOP20")
BLIND_KEYS = {"candidate_units", "dataset", "query_id", "question", "sample_id"}
UNIT_KEYS = {
    "dataset", "paragraph_index", "query_id", "sample_id", "sentence_index",
    "text", "title", "unit_id",
}
GENERATOR_KWARGS = {
    "do_sample": False,
    "max_new_tokens": 32,
    "num_beams": 1,
    "use_cache": True,
}


def _path(config: dict[str, Any], key: str) -> Path:
    return Path(require_native_string(config.get("paths", {}).get(key), f"paths.{key}"))


def _validate_authorization(config: dict[str, Any]) -> None:
    if config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Stage4F config schema differs")
    authorization = config.get("official_execution")
    if not isinstance(authorization, dict) or require_json_bool(
        authorization.get("authorized"), "official_execution.authorized"
    ) is not True:
        raise PermissionError("STAGE4F_OFFICIAL_EXECUTION_NOT_AUTHORIZED")


def _assert_bound_file(config: dict[str, Any], key: str) -> Path:
    path = _path(config, key)
    expected = config.get("inputs", {}).get(key)
    if not isinstance(expected, dict):
        raise ValueError(f"inputs.{key} identity is missing")
    assert_file_identity(path, expected, f"inputs.{key}")
    return path


def validate_snapshot(snapshot: Path, model: dict[str, Any], label: str) -> None:
    files = model.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError(f"{label}.files binding is missing")
    for index, row in enumerate(files):
        if not isinstance(row, dict) or set(row) != {"bytes", "path", "sha256"}:
            raise ValueError(f"{label}.files[{index}] schema differs")
        relative = require_native_string(row["path"], f"{label}.files[{index}].path")
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ValueError(f"{label}.files[{index}].path is unsafe")
        assert_file_identity(snapshot / relative, row, f"{label}.files[{index}]")


def build_units_queries(
    blind_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    assert_no_gold_fields(blind_rows, "Stage4F blind input")
    units: list[dict[str, Any]] = []
    queries: list[dict[str, Any]] = []
    seen_query_ids: set[str] = set()
    seen_unit_ids: set[str] = set()
    for row_index, row in enumerate(blind_rows):
        if set(row) != BLIND_KEYS:
            raise ValueError(f"blind[{row_index}] key contract differs")
        dataset = require_native_string(row["dataset"], f"blind[{row_index}].dataset")
        sample_id = require_native_string(row["sample_id"], f"blind[{row_index}].sample_id")
        query_id = require_native_string(row["query_id"], f"blind[{row_index}].query_id")
        question = require_native_string(row["question"], f"blind[{row_index}].question")
        if dataset != DATASET or query_id != f"{dataset}::{sample_id}":
            raise ValueError(f"blind[{row_index}] identity contract differs")
        if query_id in seen_query_ids:
            raise ValueError("Blind query identities must be unique")
        seen_query_ids.add(query_id)
        candidate_units = row["candidate_units"]
        if not isinstance(candidate_units, list) or not candidate_units:
            raise ValueError(f"{query_id}: candidate_units must be non-empty")
        for unit_index, unit in enumerate(candidate_units):
            if not isinstance(unit, dict) or set(unit) != UNIT_KEYS:
                raise ValueError(f"{query_id}: candidate_units[{unit_index}] schema differs")
            unit_id = require_native_string(unit["unit_id"], f"{query_id}: unit_id")
            if (
                unit["dataset"] != dataset
                or unit["query_id"] != query_id
                or unit["sample_id"] != sample_id
                or unit_id in seen_unit_ids
            ):
                raise ValueError(f"{query_id}: candidate unit belongs to another query or duplicates")
            paragraph_index = require_json_int(unit["paragraph_index"], "paragraph_index")
            sentence_index = require_json_int(unit["sentence_index"], "sentence_index")
            expected_id = f"{query_id}::p{paragraph_index}::s{sentence_index}"
            if unit_id != expected_id:
                raise ValueError(f"{query_id}: candidate-unit identity differs")
            require_native_string(unit["title"], f"{unit_id}: title")
            require_native_string(unit["text"], f"{unit_id}: text")
            seen_unit_ids.add(unit_id)
            units.append(dict(unit))
        queries.append(
            {
                "dataset": dataset,
                "num_candidate_units": len(candidate_units),
                "query_id": query_id,
                "question": question,
                "sample_id": sample_id,
            }
        )
    return units, queries


def _set_determinism(environment: dict[str, Any]) -> None:
    variables = environment.get("environment_variables")
    if not isinstance(variables, dict) or not variables:
        raise ValueError("Frozen environment variables are missing")
    for name, expected in variables.items():
        if os.environ.get(name) != expected:
            raise RuntimeError(f"Frozen environment variable differs: {name}")
    import torch

    packages = environment.get("packages")
    if not isinstance(packages, dict) or not packages:
        raise ValueError("Frozen package binding is missing")
    for name, expected in packages.items():
        if importlib.metadata.version(name) != expected:
            raise RuntimeError(f"Frozen package version differs: {name}")
    python = environment.get("python")
    runtime = environment.get("runtime")
    gpu = environment.get("gpu")
    if not all(isinstance(value, dict) for value in (python, runtime, gpu)):
        raise ValueError("Frozen runtime binding is missing")
    if platform.python_version() != python["version"] or Path(sys.executable) != Path(python["executable"]):
        raise RuntimeError("Frozen Python runtime differs")
    if (
        torch.__version__ != runtime["torch"]
        or torch.version.cuda != runtime["cuda"]
        or int(torch.backends.cudnn.version()) != runtime["cudnn"]
        or platform.platform() != runtime["platform"]
    ):
        raise RuntimeError("Frozen torch/CUDA/platform differs")
    if not torch.cuda.is_available() or torch.cuda.get_device_name(0) != gpu["name"]:
        raise RuntimeError("Frozen CUDA device differs")
    if int(torch.cuda.get_device_properties(0).total_memory) != gpu["total_memory_bytes"]:
        raise RuntimeError("Frozen CUDA memory identity differs")
    torch.manual_seed(0)
    torch.cuda.manual_seed_all(0)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False


def embed_texts(texts: list[str], snapshot: Path, batch_size: int = 64) -> np.ndarray:
    import torch
    from transformers import AutoModel, AutoTokenizer

    if not torch.cuda.is_available():
        raise RuntimeError("Frozen Stage4F environment requires CUDA; CPU offload is prohibited")
    tokenizer = AutoTokenizer.from_pretrained(snapshot, local_files_only=True)
    model = AutoModel.from_pretrained(snapshot, local_files_only=True)
    model.eval().to("cuda")
    chunks: list[np.ndarray] = []
    with torch.no_grad():
        for start in range(0, len(texts), batch_size):
            encoded = tokenizer(
                texts[start : start + batch_size], padding=True, truncation=True,
                max_length=192, return_tensors="pt",
            )
            encoded = {key: value.to("cuda") for key, value in encoded.items()}
            output = model(**encoded)
            mask = encoded["attention_mask"].unsqueeze(-1).expand(
                output.last_hidden_state.size()
            ).float()
            pooled = torch.sum(output.last_hidden_state * mask, dim=1) / torch.clamp(
                mask.sum(dim=1), min=1e-9
            )
            chunks.append(
                torch.nn.functional.normalize(pooled, p=2, dim=1)
                .cpu().numpy().astype("float32")
            )
    del model, tokenizer
    gc.collect()
    torch.cuda.empty_cache()
    result = np.vstack(chunks)
    if result.dtype != np.float32 or not np.isfinite(result).all():
        raise ValueError("Embedding matrix is not finite float32")
    return result


def _embedding_metadata(
    units: list[dict[str, Any]], queries: list[dict[str, Any]], model: dict[str, Any]
) -> dict[str, Any]:
    return {
        "encoder_model_id": ENCODER_ID,
        "encoder_revision": ENCODER_REVISION,
        "encoder_snapshot_files_sha256": model["files_sha256"],
        "max_length": 192,
        "query_id_sha256": id_digest(row["query_id"] for row in queries),
        "unit_id_sha256": id_digest(row["unit_id"] for row in units),
    }


def _write_embedding_cache(
    path: Path,
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
    metadata: dict[str, Any],
) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite embedding cache: {path}")
    pending = path.with_name(path.name + ".pending")
    if pending.exists():
        raise FileExistsError(f"Refusing to overwrite pending cache: {pending}")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with pending.open("xb") as handle:
            np.savez(
                handle,
                unit_ids=np.asarray([row["unit_id"] for row in units]),
                query_ids=np.asarray([row["query_id"] for row in queries]),
                unit_embeddings=unit_embeddings,
                query_embeddings=query_embeddings,
                metadata_json=np.asarray(json.dumps(metadata, sort_keys=True)),
            )
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(pending, path)
    except Exception:
        pending.unlink(missing_ok=True)
        raise


def _load_embedding_cache(
    path: Path,
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray]:
    with np.load(path, allow_pickle=False) as cache:
        required = {"metadata_json", "query_embeddings", "query_ids", "unit_embeddings", "unit_ids"}
        if set(cache.files) != required or json.loads(str(cache["metadata_json"].item())) != metadata:
            raise ValueError("Embedding-cache schema or metadata differs")
        if cache["unit_ids"].tolist() != [row["unit_id"] for row in units]:
            raise ValueError("Embedding-cache unit identity/order differs")
        if cache["query_ids"].tolist() != [row["query_id"] for row in queries]:
            raise ValueError("Embedding-cache query identity/order differs")
        unit_embeddings = np.asarray(cache["unit_embeddings"], dtype="float32")
        query_embeddings = np.asarray(cache["query_embeddings"], dtype="float32")
    if not np.isfinite(unit_embeddings).all() or not np.isfinite(query_embeddings).all():
        raise ValueError("Embedding cache contains non-finite values")
    return unit_embeddings, query_embeddings


def build_or_load_embeddings(
    path: Path,
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    snapshot: Path,
    model: dict[str, Any],
    *,
    allow_build: bool,
) -> tuple[np.ndarray, np.ndarray]:
    metadata = _embedding_metadata(units, queries, model)
    if path.exists():
        return _load_embedding_cache(path, units, queries, metadata)
    if not allow_build:
        raise FileNotFoundError("Rerun requires the frozen main embedding cache")
    unit_embeddings = embed_texts(
        [(row["title"] + ". " + row["text"]).strip() for row in units], snapshot
    )
    query_embeddings = embed_texts([row["question"] for row in queries], snapshot)
    _write_embedding_cache(
        path, units, queries, unit_embeddings, query_embeddings, metadata
    )
    return unit_embeddings, query_embeddings


def build_rankings(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
) -> list[dict[str, Any]]:
    decisions = build_query_decisions(
        units, queries, unit_embeddings, query_embeddings, RetrievalConfig()
    )
    return [
        {
            "dataset": query["dataset"],
            "dense_top20_unit_ids": decision["dense_top20_unit_ids"],
            "q25_inserted_unit_ids": decision["q25_inserted_unit_ids"],
            "query_id": query["query_id"],
            "sample_id": query["sample_id"],
            "static_q25_top20_unit_ids": decision["q25_top20_unit_ids"],
        }
        for query, decision in zip(queries, decisions, strict=True)
    ]


def _chat_ids(tokenizer: Any, messages: list[dict[str, str]]) -> list[int]:
    values = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True)
    if hasattr(values, "keys") and "input_ids" in values:
        values = values["input_ids"]
    return values.tolist() if hasattr(values, "tolist") else list(values)


def _messages(question: str, evidence_lines: Iterable[str]) -> list[dict[str, str]]:
    evidence = "\n".join(evidence_lines)
    return [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": f"Evidence:\n{evidence}\n\nQuestion: {question}\nFinal answer:"},
    ]


def build_prompt(
    tokenizer: Any,
    question: str,
    ranked_units: list[dict[str, Any]],
    token_cap: int = 4096,
) -> dict[str, Any]:
    if not ranked_units:
        raise ValueError("Cannot build a prompt from an empty ranking")
    if len(_chat_ids(tokenizer, _messages(question, []))) > token_cap:
        raise ValueError("Question and chat template exceed token cap")
    lines: list[str] = []
    included: list[str] = []
    truncated = False
    for rank, unit in enumerate(ranked_units, start=1):
        line = f"[{rank}] {unit['title']}: {unit['text']}"
        if len(_chat_ids(tokenizer, _messages(question, lines + [line]))) <= token_cap:
            lines.append(line)
            included.append(unit["unit_id"])
            continue
        if rank > 1:
            break
        line_tokens = list(tokenizer.encode(line, add_special_tokens=False))
        for kept in range(len(line_tokens), -1, -1):
            shortened = tokenizer.decode(
                line_tokens[:kept], skip_special_tokens=True,
                clean_up_tokenization_spaces=False,
            )
            if len(_chat_ids(tokenizer, _messages(question, [shortened]))) <= token_cap:
                lines = [shortened]
                included = [unit["unit_id"]]
                truncated = True
                break
        if not lines:
            raise ValueError("Rank-1 evidence cannot fit within token cap")
        break
    messages = _messages(question, lines)
    input_ids = _chat_ids(tokenizer, messages)
    prompt_text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    if len(input_ids) > token_cap:
        raise AssertionError("Prompt cap enforcement failed")
    return {
        "evidence_unit_ids": included,
        "input_ids": input_ids,
        "input_token_count": len(input_ids),
        "prompt_sha256": sha256_bytes(prompt_text.encode("utf-8")),
        "rank1_truncated": truncated,
    }


def generate_predictions(
    queries: list[dict[str, Any]],
    units: list[dict[str, Any]],
    rankings: list[dict[str, Any]],
    generator_snapshot: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(generator_snapshot, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        generator_snapshot, local_files_only=True, dtype=torch.float16
    )
    model.eval().to("cuda")
    torch.cuda.reset_peak_memory_stats()
    units_by_id = {row["unit_id"]: row for row in units}
    ranking_by_query = {row["query_id"]: row for row in rankings}
    predictions: list[dict[str, Any]] = []
    audits: list[dict[str, Any]] = []
    started = time.perf_counter()
    for query in queries:
        ranking = ranking_by_query[query["query_id"]]
        for method in method_order(query["query_id"]):
            ids = (
                ranking["dense_top20_unit_ids"]
                if method == "DENSE_TOP20" else ranking["static_q25_top20_unit_ids"]
            )
            prompt = build_prompt(
                tokenizer, query["question"], [units_by_id[value] for value in ids], 4096
            )
            input_ids = torch.tensor([prompt["input_ids"]], dtype=torch.long, device="cuda")
            attention_mask = torch.ones_like(input_ids)
            with torch.no_grad():
                output = model.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    pad_token_id=tokenizer.eos_token_id,
                    **GENERATOR_KWARGS,
                )
            completion = tokenizer.decode(
                output[0, input_ids.shape[1] :], skip_special_tokens=True
            ).strip()
            predictions.append(
                {
                    "dataset": query["dataset"], "method": method,
                    "prediction": completion, "query_id": query["query_id"],
                    "sample_id": query["sample_id"],
                }
            )
            audits.append(
                {
                    "dataset": query["dataset"],
                    "evidence_unit_ids": prompt["evidence_unit_ids"],
                    "input_token_count": prompt["input_token_count"],
                    "method": method,
                    "prompt_sha256": prompt["prompt_sha256"],
                    "query_id": query["query_id"],
                    "rank1_truncated": prompt["rank1_truncated"],
                    "sample_id": query["sample_id"],
                }
            )
    telemetry = {
        "failed_calls": 0,
        "generation_calls": len(predictions),
        "gpu_peak_memory_bytes": int(torch.cuda.max_memory_allocated()),
        "wall_time_seconds": time.perf_counter() - started,
    }
    del model, tokenizer
    gc.collect()
    torch.cuda.empty_cache()
    return predictions, audits, telemetry


def run(config: dict[str, Any], run_id: str) -> None:
    _validate_authorization(config)
    assert_implementation_binding(config, Path(__file__).resolve().parents[1])
    if run_id not in {"main", "rerun"}:
        raise ValueError("run_id must be main or rerun")
    verified_input = load_json(_assert_bound_file(config, "verified_input"))
    if verified_input.get("status") != "STAGE4F_INPUT_BOUNDARY_VERIFIED":
        raise ValueError("Official execution requires verified Stage4F input boundary")
    environment = load_json(_assert_bound_file(config, "environment_manifest"))
    model_manifest = load_json(_assert_bound_file(config, "model_manifest"))
    _set_determinism(environment)
    blind_rows = load_jsonl(_assert_bound_file(config, "blind"))
    units, queries = build_units_queries(blind_rows)
    if len(queries) != SAMPLE_SIZE:
        raise ValueError("Official Stage4F query count differs")
    models = model_manifest.get("models")
    if not isinstance(models, dict):
        raise ValueError("Model manifest differs")
    encoder, generator = models.get("encoder"), models.get("generator")
    if not isinstance(encoder, dict) or not isinstance(generator, dict):
        raise ValueError("Model binding is missing")
    if (encoder.get("model_id"), encoder.get("revision")) != (ENCODER_ID, ENCODER_REVISION):
        raise ValueError("Frozen encoder differs")
    if (generator.get("model_id"), generator.get("revision")) != (GENERATOR_ID, GENERATOR_REVISION):
        raise ValueError("Frozen generator differs")
    encoder_snapshot = _path(config, "encoder_snapshot")
    generator_snapshot = _path(config, "generator_snapshot")
    validate_snapshot(encoder_snapshot, encoder, "encoder")
    validate_snapshot(generator_snapshot, generator, "generator")
    unit_embeddings, query_embeddings = build_or_load_embeddings(
        _path(config, "embedding_cache"), units, queries, encoder_snapshot, encoder,
        allow_build=run_id == "main",
    )
    rankings = build_rankings(units, queries, unit_embeddings, query_embeddings)
    rankings_payload = render_jsonl(rankings)
    rankings_path = _path(config, "rankings")
    if run_id == "rerun":
        if not rankings_path.is_file() or rankings_path.read_bytes() != rankings_payload:
            raise ValueError("Rerun ranking differs from frozen main ranking")
    predictions, prompt_audit, telemetry = generate_predictions(
        queries, units, rankings, generator_snapshot
    )
    telemetry.update(
        {
            "embedding_cache": file_identity(_path(config, "embedding_cache")),
            "run_id": run_id,
            "schema_version": SCHEMA_VERSION,
            "status": "STAGE4F_GOLDFREE_RUN_COMPLETE_PENDING_VERIFICATION",
        }
    )
    outputs: list[tuple[Path, bytes]] = []
    if run_id == "main":
        outputs.append((rankings_path, rankings_payload))
    outputs.extend(
        [
            (_path(config, f"predictions_{run_id}"), render_jsonl(predictions)),
            (_path(config, f"prompt_audit_{run_id}"), render_jsonl(prompt_audit)),
            (_path(config, f"telemetry_{run_id}"), render_json(telemetry)),
        ]
    )
    write_new_files_atomically(outputs)
    print(f"STAGE4F_GOLDFREE_RUN_COMPLETE_PENDING_VERIFICATION run={run_id}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--run-id", required=True, choices=("main", "rerun"))
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage4F config must be an object")
    run(config, args.run_id)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE4F_GOLDFREE_RUN_FAIL: {exc}", file=sys.stderr)
        raise
