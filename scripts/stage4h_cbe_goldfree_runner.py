"""Stage4H Gold-free retrieval, generation, and deterministic subset rerun."""

from __future__ import annotations

import argparse
import gc
import importlib.metadata
import json
import os
import platform
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from stage4e_e2e_goldfree_runner import build_prompt
from stage4h_cbe_common import (
    DATASETS,
    GENERATOR_ID,
    GENERATOR_REVISION,
    METHODS,
    MINILM_ID,
    MINILM_REVISION,
    RERUN_QUERIES_PER_DATASET,
    SCHEMA_VERSION,
    STRONG_DENSE_ID,
    STRONG_DENSE_QUERY_PREFIX,
    STRONG_DENSE_REVISION,
    assert_file_identity,
    assert_implementation_binding,
    file_identity,
    id_digest,
    load_json,
    load_jsonl,
    method_order,
    path_from_config,
    render_json,
    render_jsonl,
    require_json_bool,
    require_native_string,
    rerun_selection_key,
    sha256_bytes,
    validate_snapshot,
    write_new_files_atomically,
)
from stage4h_cbe_retrieval import build_rankings, build_units_queries


GENERATION_KWARGS = {
    "do_sample": False,
    "max_new_tokens": 32,
    "num_beams": 1,
    "use_cache": True,
}


def _validate_authorization(config: dict[str, Any]) -> None:
    if config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Stage4H config schema differs")
    authorization = config.get("official_execution")
    if not isinstance(authorization, dict) or require_json_bool(
        authorization.get("authorized"), "official_execution.authorized"
    ) is not True:
        raise PermissionError("STAGE4H_EXECUTION_NOT_AUTHORIZED")


def _assert_bound_path(config: dict[str, Any], key: str) -> Path:
    path = path_from_config(config, key)
    expected = config.get("inputs", {}).get(key)
    if not isinstance(expected, dict):
        raise ValueError(f"inputs.{key} binding is missing")
    assert_file_identity(path, expected, f"inputs.{key}")
    return path


def _set_determinism(environment: dict[str, Any]) -> None:
    required_environment = environment.get("environment_variables")
    if not isinstance(required_environment, dict) or not required_environment:
        raise ValueError("environment_variables binding is missing")
    for name, expected in required_environment.items():
        if os.environ.get(name) != expected:
            raise RuntimeError(f"Frozen environment variable differs: {name}")
    import torch

    packages = environment.get("packages")
    if not isinstance(packages, dict) or not packages:
        raise ValueError("package binding is missing")
    for name, expected in packages.items():
        if importlib.metadata.version(name) != expected:
            raise RuntimeError(f"Frozen package version differs: {name}")
    python = environment.get("python")
    runtime = environment.get("runtime")
    gpu = environment.get("gpu")
    if not all(isinstance(value, dict) for value in (python, runtime, gpu)):
        raise ValueError("runtime binding is incomplete")
    if platform.python_version() != python["version"] or Path(sys.executable) != Path(
        python["executable"]
    ):
        raise RuntimeError("Frozen Python runtime differs")
    if (
        torch.__version__ != runtime["torch"]
        or torch.version.cuda != runtime["cuda"]
        or int(torch.backends.cudnn.version()) != runtime["cudnn"]
        or platform.platform() != runtime["platform"]
    ):
        raise RuntimeError("Frozen torch/CUDA runtime differs")
    if not torch.cuda.is_available() or torch.cuda.get_device_name(0) != gpu["name"]:
        raise RuntimeError("Frozen GPU differs")
    if int(torch.cuda.get_device_properties(0).total_memory) != gpu["total_memory_bytes"]:
        raise RuntimeError("Frozen GPU memory identity differs")
    torch.manual_seed(0)
    torch.cuda.manual_seed_all(0)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False


def _validate_models(
    config: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    models = config.get("models")
    if not isinstance(models, dict):
        raise ValueError("models binding is missing")
    minilm = models.get("minilm")
    strong = models.get("strong_dense")
    generator = models.get("generator")
    if not all(isinstance(value, dict) for value in (minilm, strong, generator)):
        raise ValueError("model bindings are incomplete")
    expected = (
        (minilm, MINILM_ID, MINILM_REVISION, "minilm", "minilm_snapshot"),
        (
            strong,
            STRONG_DENSE_ID,
            STRONG_DENSE_REVISION,
            "strong_dense",
            "strong_dense_snapshot",
        ),
        (
            generator,
            GENERATOR_ID,
            GENERATOR_REVISION,
            "generator",
            "generator_snapshot",
        ),
    )
    for binding, model_id, revision, label, path_key in expected:
        if (binding.get("model_id"), binding.get("revision")) != (model_id, revision):
            raise ValueError(f"{label} identity differs")
        snapshot = path_from_config(config, path_key)
        if str(snapshot.resolve()) != binding.get("snapshot_path"):
            raise ValueError(f"{label} snapshot path differs")
        validate_snapshot(snapshot, binding, label)
    return minilm, strong, generator


def _normalize_embeddings(matrix: Any) -> np.ndarray:
    result = np.asarray(matrix, dtype="float32")
    if result.ndim != 2 or not np.isfinite(result).all():
        raise ValueError("embedding matrix must be finite float32")
    norms = np.linalg.norm(result, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    result = (result / norms).astype("float32")
    if not np.isfinite(result).all():
        raise ValueError("normalized embedding matrix is not finite")
    return result


def embed_minilm(texts: list[str], snapshot: Path) -> np.ndarray:
    import torch
    from transformers import AutoModel, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(snapshot, local_files_only=True)
    model = AutoModel.from_pretrained(snapshot, local_files_only=True)
    model.eval().to("cuda")
    chunks: list[np.ndarray] = []
    with torch.no_grad():
        for start in range(0, len(texts), 64):
            encoded = tokenizer(
                texts[start : start + 64],
                padding=True,
                truncation=True,
                max_length=192,
                return_tensors="pt",
            )
            encoded = {key: value.to("cuda") for key, value in encoded.items()}
            output = model(**encoded)
            mask = encoded["attention_mask"].unsqueeze(-1).expand(
                output.last_hidden_state.shape
            ).float()
            pooled = torch.sum(output.last_hidden_state * mask, dim=1) / torch.clamp(
                mask.sum(dim=1), min=1e-9
            )
            pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
            chunks.append(pooled.cpu().numpy().astype("float32"))
    del model, tokenizer
    gc.collect()
    torch.cuda.empty_cache()
    return _normalize_embeddings(np.vstack(chunks))


def embed_strong_dense(texts: list[str], snapshot: Path) -> np.ndarray:
    import torch
    from transformers import AutoModel, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(snapshot, local_files_only=True)
    model = AutoModel.from_pretrained(
        snapshot, local_files_only=True, dtype=torch.float16
    )
    model.eval().to("cuda")
    chunks: list[np.ndarray] = []
    with torch.no_grad():
        for start in range(0, len(texts), 32):
            encoded = tokenizer(
                texts[start : start + 32],
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )
            encoded = {key: value.to("cuda") for key, value in encoded.items()}
            output = model(**encoded)
            pooled = torch.nn.functional.normalize(
                output.last_hidden_state[:, 0].float(), p=2, dim=1
            )
            chunks.append(pooled.cpu().numpy().astype("float32"))
    del model, tokenizer
    gc.collect()
    torch.cuda.empty_cache()
    return _normalize_embeddings(np.vstack(chunks))


def _cache_metadata(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    binding: dict[str, Any],
    kind: str,
) -> dict[str, Any]:
    if kind == "minilm":
        return {
            "document_input": "title + '. ' + sentence",
            "max_length": 192,
            "model_id": MINILM_ID,
            "pooling": "attention_mask_mean_then_l2",
            "query_input": "question",
            "revision": MINILM_REVISION,
            "snapshot_files_sha256": binding["files_sha256"],
            "unit_id_sha256": id_digest(row["unit_id"] for row in units),
            "query_id_sha256": id_digest(row["query_id"] for row in queries),
        }
    if kind == "strong":
        return {
            "document_input": "title + '. ' + sentence",
            "max_length": 512,
            "model_id": STRONG_DENSE_ID,
            "pooling": "CLS_then_l2",
            "query_input": STRONG_DENSE_QUERY_PREFIX + "<question>",
            "revision": STRONG_DENSE_REVISION,
            "snapshot_files_sha256": binding["files_sha256"],
            "unit_id_sha256": id_digest(row["unit_id"] for row in units),
            "query_id_sha256": id_digest(row["query_id"] for row in queries),
        }
    raise ValueError(f"Unknown embedding kind: {kind}")


def _write_cache(
    path: Path,
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
    metadata: dict[str, Any],
) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite embedding cache: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(path.name + ".pending")
    if pending.exists():
        raise FileExistsError(f"Refusing to overwrite pending cache: {pending}")
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


def _load_cache(
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
            raise ValueError(f"{path}: cache schema differs")
        if json.loads(str(cache["metadata_json"].item())) != metadata:
            raise ValueError(f"{path}: cache metadata differs")
        if cache["unit_ids"].tolist() != [row["unit_id"] for row in units]:
            raise ValueError(f"{path}: cache unit order differs")
        if cache["query_ids"].tolist() != [row["query_id"] for row in queries]:
            raise ValueError(f"{path}: cache query order differs")
        unit_embeddings = _normalize_embeddings(cache["unit_embeddings"])
        query_embeddings = _normalize_embeddings(cache["query_embeddings"])
    return unit_embeddings, query_embeddings


def build_or_load_embeddings(
    path: Path,
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    binding: dict[str, Any],
    snapshot: Path,
    kind: str,
    allow_build: bool,
) -> tuple[np.ndarray, np.ndarray, float]:
    metadata = _cache_metadata(units, queries, binding, kind)
    started = time.perf_counter()
    if path.is_file():
        unit_embeddings, query_embeddings = _load_cache(
            path, units, queries, metadata
        )
        return unit_embeddings, query_embeddings, time.perf_counter() - started
    if not allow_build:
        raise FileNotFoundError(f"{kind} rerun requires frozen embedding cache")
    documents = [
        (row["title"] + ". " + row["text"]).strip()
        for row in units
    ]
    if kind == "minilm":
        unit_embeddings = embed_minilm(documents, snapshot)
        query_embeddings = embed_minilm(
            [row["question"] for row in queries], snapshot
        )
    elif kind == "strong":
        unit_embeddings = embed_strong_dense(documents, snapshot)
        query_embeddings = embed_strong_dense(
            [STRONG_DENSE_QUERY_PREFIX + row["question"] for row in queries],
            snapshot,
        )
    else:
        raise ValueError(f"Unknown embedding kind: {kind}")
    _write_cache(
        path,
        units,
        queries,
        unit_embeddings,
        query_embeddings,
        metadata,
    )
    return unit_embeddings, query_embeddings, time.perf_counter() - started


def select_rerun_queries(queries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in queries:
        by_dataset[row["dataset"]].append(row)
    selected: set[str] = set()
    for dataset in DATASETS:
        rows = sorted(
            by_dataset[dataset],
            key=lambda row: rerun_selection_key(dataset, row["query_id"]),
        )[:RERUN_QUERIES_PER_DATASET]
        if len(rows) != RERUN_QUERIES_PER_DATASET:
            raise ValueError(f"{dataset}: insufficient rerun subset")
        selected.update(row["query_id"] for row in rows)
    return [row for row in queries if row["query_id"] in selected]


def _load_checkpoint(
    path: Path,
    task_keys: list[tuple[str, str]],
) -> dict[tuple[str, str], dict[str, Any]]:
    if not path.is_file():
        return {}
    allowed = set(task_keys)
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict) or set(row) != {"audit", "prediction"}:
            raise ValueError(f"{path}:{line_number}: checkpoint schema differs")
        prediction = row["prediction"]
        audit = row["audit"]
        if not isinstance(prediction, dict) or not isinstance(audit, dict):
            raise ValueError(f"{path}:{line_number}: checkpoint row differs")
        key = (prediction.get("query_id"), prediction.get("method"))
        if key not in allowed or key in result:
            raise ValueError(f"{path}:{line_number}: checkpoint identity differs")
        if (audit.get("query_id"), audit.get("method")) != key:
            raise ValueError(f"{path}:{line_number}: checkpoint pair differs")
        result[key] = row
    return result


def generate_predictions(
    queries: list[dict[str, Any]],
    units: list[dict[str, Any]],
    rankings: list[dict[str, Any]],
    generator_snapshot: Path,
    checkpoint_path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    ranking_by_query = {row["query_id"]: row for row in rankings}
    units_by_id = {row["unit_id"]: row for row in units}
    tasks = [
        (query, method)
        for query in queries
        for method in method_order(query["query_id"])
    ]
    task_keys = [(query["query_id"], method) for query, method in tasks]
    checkpoint = _load_checkpoint(checkpoint_path, task_keys)
    tokenizer = AutoTokenizer.from_pretrained(
        generator_snapshot, local_files_only=True
    )
    model = AutoModelForCausalLM.from_pretrained(
        generator_snapshot, local_files_only=True, dtype=torch.float16
    )
    model.eval().to("cuda")
    torch.cuda.reset_peak_memory_stats()
    generation_seconds = defaultdict(float)
    generated_now = 0
    started = time.perf_counter()
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    with checkpoint_path.open("a", encoding="utf-8", newline="\n") as handle:
        for task_index, (query, method) in enumerate(tasks, start=1):
            key = (query["query_id"], method)
            if key in checkpoint:
                continue
            ranking = ranking_by_query[query["query_id"]]["methods"][method]
            prompt = build_prompt(
                tokenizer,
                query["question"],
                [units_by_id[unit_id] for unit_id in ranking],
                4096,
            )
            input_ids = torch.tensor(
                [prompt["input_ids"]], dtype=torch.long, device="cuda"
            )
            attention_mask = torch.ones_like(input_ids)
            torch.cuda.synchronize()
            call_started = time.perf_counter()
            with torch.no_grad():
                output = model.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    pad_token_id=tokenizer.eos_token_id,
                    **GENERATION_KWARGS,
                )
            torch.cuda.synchronize()
            generation_seconds[method] += time.perf_counter() - call_started
            completion = tokenizer.decode(
                output[0, input_ids.shape[1] :], skip_special_tokens=True
            ).strip()
            prediction = {
                "dataset": query["dataset"],
                "method": method,
                "prediction": completion,
                "query_id": query["query_id"],
                "sample_id": query["sample_id"],
            }
            audit = {
                "dataset": query["dataset"],
                "evidence_unit_ids": prompt["evidence_unit_ids"],
                "input_token_count": prompt["input_token_count"],
                "method": method,
                "prompt_sha256": prompt["prompt_sha256"],
                "query_id": query["query_id"],
                "rank1_truncated": prompt["rank1_truncated"],
                "sample_id": query["sample_id"],
            }
            row = {"audit": audit, "prediction": prediction}
            handle.write(
                json.dumps(
                    row,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                    allow_nan=False,
                )
                + "\n"
            )
            handle.flush()
            checkpoint[key] = row
            generated_now += 1
            if task_index % 250 == 0:
                print(
                    "STAGE4H_GENERATION_PROGRESS "
                    f"completed={len(checkpoint)}/{len(tasks)}"
                )
    if set(checkpoint) != set(task_keys):
        raise RuntimeError("Stage4H generation checkpoint is incomplete")
    predictions = [checkpoint[key]["prediction"] for key in task_keys]
    audits = [checkpoint[key]["audit"] for key in task_keys]
    telemetry = {
        "failed_calls": 0,
        "generated_in_this_process": generated_now,
        "generation_calls": len(predictions),
        "generation_seconds_by_method": {
            method: generation_seconds[method] for method in METHODS
        },
        "gpu_peak_memory_bytes": int(torch.cuda.max_memory_allocated()),
        "wall_time_seconds_this_process": time.perf_counter() - started,
    }
    del model, tokenizer
    gc.collect()
    torch.cuda.empty_cache()
    return predictions, audits, telemetry


def run(config: dict[str, Any], run_id: str) -> None:
    _validate_authorization(config)
    assert_implementation_binding(config, Path(__file__).resolve().parents[1])
    if run_id not in {"main", "rerun_subset"}:
        raise ValueError("run-id must be main or rerun_subset")
    environment_path = _assert_bound_path(config, "environment_manifest")
    environment = load_json(environment_path)
    if not isinstance(environment, dict):
        raise ValueError("environment manifest must be an object")
    _set_determinism(environment)
    minilm_binding, strong_binding, _ = _validate_models(config)
    blind = load_jsonl(_assert_bound_path(config, "blind"))
    units, queries = build_units_queries(blind)
    if len(queries) != sum(config["sample_sizes"].values()):
        raise ValueError("Stage4H query count differs")

    allow_build = run_id == "main"
    minilm_unit, minilm_query, minilm_seconds = build_or_load_embeddings(
        path_from_config(config, "minilm_embedding_cache"),
        units,
        queries,
        minilm_binding,
        path_from_config(config, "minilm_snapshot"),
        "minilm",
        allow_build,
    )
    strong_unit, strong_query, strong_seconds = build_or_load_embeddings(
        path_from_config(config, "strong_embedding_cache"),
        units,
        queries,
        strong_binding,
        path_from_config(config, "strong_dense_snapshot"),
        "strong",
        allow_build,
    )
    rankings, traces, retrieval_seconds = build_rankings(
        units,
        queries,
        minilm_unit,
        minilm_query,
        strong_unit,
        strong_query,
    )
    rankings_payload = render_jsonl(rankings)
    traces_payload = render_jsonl(traces)
    rankings_path = path_from_config(config, "rankings")
    traces_path = path_from_config(config, "retrieval_trace")
    if run_id == "rerun_subset":
        if not rankings_path.is_file() or rankings_path.read_bytes() != rankings_payload:
            raise ValueError("Frozen main rankings differ from rerun reconstruction")
        if not traces_path.is_file() or traces_path.read_bytes() != traces_payload:
            raise ValueError("Frozen main retrieval trace differs")
        run_queries = select_rerun_queries(queries)
    else:
        run_queries = queries
    predictions, audits, telemetry = generate_predictions(
        run_queries,
        units,
        rankings,
        path_from_config(config, "generator_snapshot"),
        path_from_config(config, f"checkpoint_{run_id}"),
    )
    telemetry.update(
        {
            "embedding_cache": {
                "minilm": file_identity(
                    path_from_config(config, "minilm_embedding_cache")
                ),
                "strong_dense": file_identity(
                    path_from_config(config, "strong_embedding_cache")
                ),
            },
            "embedding_load_or_build_seconds": {
                "minilm": minilm_seconds,
                "strong_dense": strong_seconds,
            },
            "query_count": len(run_queries),
            "retrieval_seconds_by_method": retrieval_seconds,
            "run_id": run_id,
            "schema_version": SCHEMA_VERSION,
            "status": "STAGE4H_GOLDFREE_RUN_COMPLETE_PENDING_VERIFICATION",
        }
    )
    outputs: list[tuple[Path, bytes]] = []
    if run_id == "main":
        outputs.extend(
            [
                (rankings_path, rankings_payload),
                (traces_path, traces_payload),
            ]
        )
    outputs.extend(
        [
            (
                path_from_config(config, f"predictions_{run_id}"),
                render_jsonl(predictions),
            ),
            (
                path_from_config(config, f"prompt_audit_{run_id}"),
                render_jsonl(audits),
            ),
            (
                path_from_config(config, f"telemetry_{run_id}"),
                render_json(telemetry),
            ),
        ]
    )
    write_new_files_atomically(outputs)
    print(
        "STAGE4H_GOLDFREE_RUN_COMPLETE_PENDING_VERIFICATION "
        f"run={run_id} queries={len(run_queries)} calls={len(predictions)} "
        f"rankings_sha256={sha256_bytes(rankings_payload)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--run-id", required=True, choices=("main", "rerun_subset"))
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage4H config must be an object")
    run(config, args.run_id)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE4H_GOLDFREE_RUN_FAIL: {exc}", file=sys.stderr)
        raise
