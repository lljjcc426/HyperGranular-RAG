"""Gold-free retrieval and generation runner for the frozen Stage4E protocol.

This entry point can read only the blind channel.  It deliberately has no
argument for the Gold or descriptive-metadata channels.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from stage4b_u1_goldfree_retrieval import RetrievalConfig, build_query_decisions
from stage4e_e2e_common import (
    DATASET,
    ENCODER_ID,
    ENCODER_REVISION,
    GENERATOR_ID,
    GENERATOR_REVISION,
    SCHEMA_VERSION,
    assert_implementation_binding,
    assert_file_identity,
    assert_no_prohibited_keys,
    file_identity,
    id_digest,
    load_json,
    load_jsonl,
    method_order,
    normalize_sentence,
    render_json,
    render_jsonl,
    require_json_bool,
    require_json_int,
    require_native_string,
    sha256_bytes,
    sha256_file,
    validate_sha256,
    write_new_files_atomically,
)


SYSTEM_MESSAGE = (
    "Answer the question using only the provided evidence. Return only the "
    "shortest final answer. If the evidence is insufficient, return UNKNOWN."
)
METHODS = ("DENSE_TOP20", "STATIC_Q25_TOP20")
BLIND_KEYS = {"context", "dataset", "query_id", "question", "sample_id"}
CONTEXT_KEYS = {"context_index", "sentences", "title"}
UNIT_KEYS = {
    "context_index",
    "dataset",
    "doc_id",
    "query_id",
    "sample_id",
    "sentence_id",
    "text",
    "title",
    "unit_id",
}


def _path(config: dict[str, Any], key: str) -> Path:
    value = config.get("paths", {}).get(key)
    return Path(require_native_string(value, f"paths.{key}"))


def _validate_authorization(config: dict[str, Any], confirmed_command_sha256: str) -> None:
    if config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Stage4E config schema_version differs")
    authorization = config.get("official_execution")
    if not isinstance(authorization, dict):
        raise ValueError("official_execution must be an object")
    if require_json_bool(authorization.get("authorized"), "official_execution.authorized") is not True:
        raise PermissionError("STAGE4E_OFFICIAL_EXECUTION_NOT_AUTHORIZED")
    expected = validate_sha256(
        authorization.get("confirmed_command_sha256"),
        "official_execution.confirmed_command_sha256",
    )
    supplied = validate_sha256(confirmed_command_sha256, "--confirmed-command-sha256")
    if supplied != expected:
        raise PermissionError("Exact official command confirmation SHA differs")


def _assert_bound_file(config: dict[str, Any], key: str) -> Path:
    path = _path(config, key)
    expected = config.get("inputs", {}).get(key)
    if not isinstance(expected, dict):
        raise ValueError(f"inputs.{key} identity is missing")
    assert_file_identity(path, expected, f"inputs.{key}")
    return path


def validate_snapshot(snapshot: Path, model: dict[str, Any], label: str) -> None:
    require_native_string(model.get("model_id"), f"{label}.model_id")
    require_native_string(model.get("revision"), f"{label}.revision")
    files = model.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError(f"{label}.files must be a non-empty list")
    expected_list_digest = validate_sha256(
        model.get("files_sha256"), f"{label}.files_sha256"
    )
    if sha256_bytes(render_json(files)) != expected_list_digest:
        raise ValueError(f"{label}.files_sha256 differs from the file manifest")
    seen: set[str] = set()
    for index, row in enumerate(files):
        if not isinstance(row, dict) or set(row) != {"bytes", "path", "sha256"}:
            raise ValueError(f"{label}.files[{index}] schema differs")
        relative = require_native_string(row["path"], f"{label}.files[{index}].path")
        if relative in seen or Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ValueError(f"{label}.files[{index}].path is invalid or duplicate")
        seen.add(relative)
        assert_file_identity(
            snapshot / relative,
            {"bytes": row["bytes"], "sha256": row["sha256"]},
            f"{label}.files[{index}]",
        )


def build_units_queries(
    blind_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    assert_no_prohibited_keys(blind_rows, "stage4e blind input")
    units: list[dict[str, Any]] = []
    queries: list[dict[str, Any]] = []
    seen_queries: set[str] = set()
    seen_samples: set[str] = set()
    for row_index, row in enumerate(blind_rows):
        if set(row) != BLIND_KEYS:
            raise ValueError(f"blind[{row_index}] key contract differs")
        dataset = require_native_string(row["dataset"], f"blind[{row_index}].dataset")
        sample_id = require_native_string(row["sample_id"], f"blind[{row_index}].sample_id")
        query_id = require_native_string(row["query_id"], f"blind[{row_index}].query_id")
        question = require_native_string(row["question"], f"blind[{row_index}].question")
        if dataset != DATASET or query_id != f"{dataset}::{sample_id}":
            raise ValueError(f"blind[{row_index}] identity contract differs")
        if query_id in seen_queries or sample_id in seen_samples:
            raise ValueError("Blind query/sample identities must be unique")
        seen_queries.add(query_id)
        seen_samples.add(sample_id)
        contexts = row["context"]
        if not isinstance(contexts, list) or not contexts:
            raise ValueError(f"{query_id}: context must be a non-empty list")
        query_units: list[dict[str, Any]] = []
        for context_index, context in enumerate(contexts):
            if not isinstance(context, dict) or set(context) != CONTEXT_KEYS:
                raise ValueError(f"{query_id}: context[{context_index}] key contract differs")
            bound_index = require_json_int(
                context["context_index"], f"{query_id}: context_index"
            )
            if bound_index != context_index:
                raise ValueError(f"{query_id}: context index/order differs")
            title = require_native_string(context["title"], f"{query_id}: context title")
            sentences = context["sentences"]
            if not isinstance(sentences, list) or not sentences:
                raise ValueError(f"{query_id}: sentences must be a non-empty list")
            for sentence_index, raw_sentence in enumerate(sentences):
                sentence = normalize_sentence(raw_sentence)
                if not sentence:
                    continue
                unit_id = f"{query_id}::c{context_index}::s{sentence_index}"
                query_units.append(
                    {
                        "context_index": context_index,
                        "dataset": dataset,
                        "doc_id": f"{query_id}::c{context_index}",
                        "query_id": query_id,
                        "sample_id": sample_id,
                        "sentence_id": sentence_index,
                        "text": sentence,
                        "title": title,
                        "unit_id": unit_id,
                    }
                )
        if not query_units:
            raise ValueError(f"{query_id}: no non-empty candidate units")
        if any(set(unit) != UNIT_KEYS for unit in query_units):
            raise AssertionError("Internal Stage4E unit schema error")
        units.extend(query_units)
        queries.append(
            {
                "dataset": dataset,
                "num_candidate_units": len(query_units),
                "query_id": query_id,
                "question": question,
                "sample_id": sample_id,
            }
        )
    return units, queries


def _set_determinism() -> None:
    required_environment = {
        "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
        "MKL_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "PYTHONHASHSEED": "0",
        "TOKENIZERS_PARALLELISM": "false",
    }
    for name, expected in required_environment.items():
        if os.environ.get(name) != expected:
            raise RuntimeError(f"Frozen environment variable differs: {name}")
    import torch

    torch.manual_seed(0)
    torch.cuda.manual_seed_all(0)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False


def embed_texts(
    texts: list[str], snapshot: Path, batch_size: int, max_length: int
) -> np.ndarray:
    import torch
    from transformers import AutoModel, AutoTokenizer

    if not torch.cuda.is_available():
        raise RuntimeError("Frozen Stage4E environment requires CUDA")
    tokenizer = AutoTokenizer.from_pretrained(snapshot, local_files_only=True)
    model = AutoModel.from_pretrained(snapshot, local_files_only=True)
    model.eval().to("cuda")
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
            encoded = {key: value.to("cuda") for key, value in encoded.items()}
            output = model(**encoded)
            mask = encoded["attention_mask"].unsqueeze(-1).expand(
                output.last_hidden_state.size()
            ).float()
            pooled = torch.sum(output.last_hidden_state * mask, dim=1) / torch.clamp(
                mask.sum(dim=1), min=1e-9
            )
            pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
            chunks.append(pooled.cpu().numpy().astype("float32"))
    del model, tokenizer
    gc.collect()
    torch.cuda.empty_cache()
    result = np.vstack(chunks)
    if result.dtype != np.float32 or not np.isfinite(result).all():
        raise ValueError("Embedding matrix is not finite float32")
    return result


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
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(path.name + ".pending")
    if pending.exists():
        raise FileExistsError(f"Refusing to overwrite pending cache: {pending}")
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
        required = {
            "metadata_json",
            "query_embeddings",
            "query_ids",
            "unit_embeddings",
            "unit_ids",
        }
        if set(cache.files) != required:
            raise ValueError("Embedding cache member contract differs")
        cached_metadata = json.loads(str(cache["metadata_json"].item()))
        if cached_metadata != metadata:
            raise ValueError("Embedding cache metadata differs")
        if cache["unit_ids"].tolist() != [row["unit_id"] for row in units]:
            raise ValueError("Embedding cache unit identity/order differs")
        if cache["query_ids"].tolist() != [row["query_id"] for row in queries]:
            raise ValueError("Embedding cache query identity/order differs")
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
    encoder_binding: dict[str, Any],
    *,
    allow_build: bool,
) -> tuple[np.ndarray, np.ndarray]:
    metadata = {
        "encoder_model_id": ENCODER_ID,
        "encoder_revision": ENCODER_REVISION,
        "encoder_snapshot_files_sha256": encoder_binding["files_sha256"],
        "max_length": 192,
        "query_id_sha256": id_digest(row["query_id"] for row in queries),
        "unit_id_sha256": id_digest(row["unit_id"] for row in units),
    }
    if path.exists():
        return _load_embedding_cache(path, units, queries, metadata)
    if not allow_build:
        raise FileNotFoundError("Rerun requires the frozen main embedding cache")
    unit_embeddings = embed_texts(
        [(row["title"] + ". " + row["text"]).strip() for row in units],
        snapshot,
        64,
        192,
    )
    query_embeddings = embed_texts(
        [row["question"] for row in queries], snapshot, 64, 192
    )
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
    rows: list[dict[str, Any]] = []
    for query, decision in zip(queries, decisions, strict=True):
        rows.append(
            {
                "dataset": query["dataset"],
                "dense_top20_unit_ids": decision["dense_top20_unit_ids"],
                "q25_inserted_unit_ids": decision["q25_inserted_unit_ids"],
                "query_id": query["query_id"],
                "sample_id": query["sample_id"],
                "static_q25_top20_unit_ids": decision["q25_top20_unit_ids"],
            }
        )
    return rows


def _chat_ids(tokenizer: Any, messages: list[dict[str, str]]) -> list[int]:
    values = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True
    )
    if hasattr(values, "keys") and "input_ids" in values:
        values = values["input_ids"]
    return values.tolist() if hasattr(values, "tolist") else list(values)


def _messages(question: str, evidence_lines: Iterable[str]) -> list[dict[str, str]]:
    evidence = "\n".join(evidence_lines)
    user = f"Evidence:\n{evidence}\n\nQuestion: {question}\nFinal answer:"
    return [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": user},
    ]


def build_prompt(
    tokenizer: Any,
    question: str,
    ranked_units: list[dict[str, Any]],
    token_cap: int = 4096,
) -> dict[str, Any]:
    if not ranked_units:
        raise ValueError("Cannot build a prompt from an empty ranking")
    base = _messages(question, [])
    if len(_chat_ids(tokenizer, base)) > token_cap:
        raise ValueError("Question and chat template alone exceed the token cap")
    lines: list[str] = []
    included: list[str] = []
    truncated = False
    for rank, unit in enumerate(ranked_units, start=1):
        line = f"[{rank}] {unit['title']}: {unit['text']}"
        candidate = lines + [line]
        candidate_ids = _chat_ids(tokenizer, _messages(question, candidate))
        if len(candidate_ids) <= token_cap:
            lines = candidate
            included.append(unit["unit_id"])
            continue
        if rank > 1:
            break
        line_tokens = list(tokenizer.encode(line, add_special_tokens=False))
        kept = len(line_tokens)
        while kept >= 0:
            shortened = tokenizer.decode(
                line_tokens[:kept], skip_special_tokens=True,
                clean_up_tokenization_spaces=False,
            )
            candidate_ids = _chat_ids(tokenizer, _messages(question, [shortened]))
            if len(candidate_ids) <= token_cap:
                lines = [shortened]
                included = [unit["unit_id"]]
                truncated = True
                break
            kept -= 1
        if not lines:
            raise ValueError("Rank-1 evidence cannot fit within the token cap")
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
        generator_snapshot,
        local_files_only=True,
        dtype=torch.float16,
    )
    model.eval().to("cuda")
    torch.cuda.reset_peak_memory_stats()
    units_by_id = {row["unit_id"]: row for row in units}
    ranking_by_query = {row["query_id"]: row for row in rankings}
    predictions: list[dict[str, Any]] = []
    audits: list[dict[str, Any]] = []
    started = time.perf_counter()
    for query in queries:
        query_id = query["query_id"]
        ranking = ranking_by_query[query_id]
        for method in method_order(query_id):
            ids = (
                ranking["dense_top20_unit_ids"]
                if method == "DENSE_TOP20"
                else ranking["static_q25_top20_unit_ids"]
            )
            ranked_units = [units_by_id[value] for value in ids]
            prompt = build_prompt(tokenizer, query["question"], ranked_units, 4096)
            input_ids = torch.tensor([prompt["input_ids"]], dtype=torch.long, device="cuda")
            attention_mask = torch.ones_like(input_ids)
            with torch.no_grad():
                output = model.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    do_sample=False,
                    num_beams=1,
                    max_new_tokens=32,
                    pad_token_id=tokenizer.eos_token_id,
                    use_cache=True,
                )
            completion = tokenizer.decode(
                output[0, input_ids.shape[1] :], skip_special_tokens=True
            ).strip()
            predictions.append(
                {
                    "dataset": query["dataset"],
                    "method": method,
                    "prediction": completion,
                    "query_id": query_id,
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
                    "query_id": query_id,
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


def _require_rankings(path: Path, expected_payload: bytes) -> None:
    if not path.is_file():
        raise FileNotFoundError("Rerun requires frozen main rankings")
    actual = path.read_bytes()
    if actual != expected_payload:
        raise ValueError("Frozen main rankings differ from independent reconstruction")


def run(config: dict[str, Any], run_id: str, confirmed_command_sha256: str) -> None:
    _validate_authorization(config, confirmed_command_sha256)
    assert_implementation_binding(config, Path(__file__).resolve().parents[1])
    if run_id not in {"main", "rerun"}:
        raise ValueError("run-id must be main or rerun")
    _set_determinism()

    blind_path = _assert_bound_file(config, "blind")
    blind_rows = load_jsonl(blind_path)
    units, queries = build_units_queries(blind_rows)
    if len(queries) != 1000:
        raise ValueError("Official Stage4E query count must equal 1000")

    models = config.get("models")
    if not isinstance(models, dict):
        raise ValueError("models binding is missing")
    encoder = models.get("encoder")
    generator = models.get("generator")
    if not isinstance(encoder, dict) or not isinstance(generator, dict):
        raise ValueError("encoder/generator bindings are missing")
    if (encoder.get("model_id"), encoder.get("revision")) != (ENCODER_ID, ENCODER_REVISION):
        raise ValueError("Encoder identity differs from the frozen protocol")
    if (generator.get("model_id"), generator.get("revision")) != (
        GENERATOR_ID,
        GENERATOR_REVISION,
    ):
        raise ValueError("Generator identity differs from the frozen protocol")
    encoder_snapshot = _path(config, "encoder_snapshot")
    generator_snapshot = _path(config, "generator_snapshot")
    validate_snapshot(encoder_snapshot, encoder, "models.encoder")
    validate_snapshot(generator_snapshot, generator, "models.generator")

    unit_embeddings, query_embeddings = build_or_load_embeddings(
        _path(config, "embedding_cache"),
        units,
        queries,
        encoder_snapshot,
        encoder,
        allow_build=run_id == "main",
    )
    rankings = build_rankings(units, queries, unit_embeddings, query_embeddings)
    rankings_payload = render_jsonl(rankings)
    rankings_path = _path(config, "rankings")
    if run_id == "rerun":
        _require_rankings(rankings_path, rankings_payload)

    predictions, prompt_audit, telemetry = generate_predictions(
        queries, units, rankings, generator_snapshot
    )
    telemetry.update(
        {
            "embedding_cache": file_identity(_path(config, "embedding_cache")),
            "run_id": run_id,
            "schema_version": SCHEMA_VERSION,
            "status": "STAGE4E_GOLDFREE_RUN_COMPLETE_PENDING_VERIFICATION",
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
    print(
        "STAGE4E_GOLDFREE_RUN_COMPLETE_PENDING_VERIFICATION "
        f"run={run_id} queries={len(queries)} calls={len(predictions)}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--run-id", required=True, choices=("main", "rerun"))
    parser.add_argument("--confirmed-command-sha256", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage4E config must be an object")
    run(config, args.run_id, args.confirmed_command_sha256)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE4E_GOLDFREE_RUN_FAIL: {exc}", file=sys.stderr)
        raise
