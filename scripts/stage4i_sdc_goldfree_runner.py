"""Stage4I blind eligibility, four-arm generation, and subset rerun."""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from stage4e_e2e_goldfree_runner import build_prompt
from stage4h_cbe_goldfree_runner import (
    GENERATION_KWARGS,
    _load_checkpoint,
    _set_determinism,
    build_or_load_embeddings,
)
from stage4i_sdc_common import (
    DATASETS,
    METHODS,
    RERUN_QUERIES_PER_DATASET,
    SAMPLE_SIZES,
    SCHEMA_VERSION,
    assert_bound,
    assert_implementation_binding,
    assert_parent_stage4h_artifacts,
    file_identity,
    load_json,
    load_jsonl,
    method_order,
    path_from_config,
    render_json,
    render_jsonl,
    rerun_selection_key,
    sha256_bytes,
    validate_authorization,
    validate_inherited_models,
    write_new_files_atomically,
)
from stage4i_sdc_retrieval import (
    build_rankings,
    build_units_queries,
    summarize_eligibility,
)


def build_or_load_exact_embeddings(
    path: Path,
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    binding: dict[str, Any],
    snapshot: Path,
    kind: str,
    allow_build: bool,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Validate with the inherited loader but preserve frozen float32 cache bytes.

    The inherited loader re-normalizes an already-normalized cache on every
    read.  That non-idempotent float32 transform can reorder near ties.  A new
    cache build still returns the exact matrices used to write the cache; a
    cache read validates the inherited schema/metadata and then returns the
    stored finite, L2-normalized matrices without a second transformation.
    """

    cache_existed = path.is_file()
    unit, query, seconds = build_or_load_embeddings(
        path,
        units,
        queries,
        binding,
        snapshot,
        kind,
        allow_build,
    )
    if not cache_existed:
        return unit, query, seconds
    with np.load(path, allow_pickle=False) as cache:
        raw_unit = np.asarray(cache["unit_embeddings"], dtype="float32")
        raw_query = np.asarray(cache["query_embeddings"], dtype="float32")
    for matrix, expected_rows, label in (
        (raw_unit, len(units), f"{kind}.unit_embeddings"),
        (raw_query, len(queries), f"{kind}.query_embeddings"),
    ):
        if (
            matrix.ndim != 2
            or matrix.shape[0] != expected_rows
            or not np.isfinite(matrix).all()
        ):
            raise ValueError(f"{label}: frozen cache matrix differs")
        norms = np.linalg.norm(matrix, axis=1)
        if np.any(norms <= 0.0) or not np.allclose(
            norms, 1.0, atol=1e-5, rtol=0.0
        ):
            raise ValueError(f"{label}: frozen cache is not L2-normalized")
    return raw_unit, raw_query, seconds


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
            raise ValueError(f"{dataset}: insufficient deterministic subset")
        selected.update(row["query_id"] for row in rows)
    return [row for row in queries if row["query_id"] in selected]


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
                    "STAGE4I_GENERATION_PROGRESS "
                    f"completed={len(checkpoint)}/{len(tasks)}"
                )
    if set(checkpoint) != set(task_keys):
        raise RuntimeError("Stage4I generation checkpoint is incomplete")
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


def _context(
    config: dict[str, Any],
    allow_cache_build: bool,
) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, float],
    dict[str, float],
]:
    validate_authorization(config)
    assert_implementation_binding(config, Path(__file__).resolve().parents[1])
    parent = validate_inherited_models(config)
    assert_parent_stage4h_artifacts(parent)
    environment_path = Path(parent["paths"]["environment_manifest"])
    environment = load_json(environment_path)
    if not isinstance(environment, dict):
        raise ValueError("inherited environment manifest differs")
    _set_determinism(environment)
    blind = load_jsonl(assert_bound(config, "blind"))
    units, queries = build_units_queries(blind)
    if len(queries) != sum(SAMPLE_SIZES.values()):
        raise ValueError("Stage4I query count differs")
    minilm_binding = parent["models"]["minilm"]
    strong_binding = parent["models"]["strong_dense"]
    minilm_unit, minilm_query, minilm_seconds = build_or_load_exact_embeddings(
        path_from_config(config, "minilm_embedding_cache"),
        units,
        queries,
        minilm_binding,
        Path(parent["paths"]["minilm_snapshot"]),
        "minilm",
        allow_cache_build,
    )
    strong_unit, strong_query, strong_seconds = build_or_load_exact_embeddings(
        path_from_config(config, "strong_embedding_cache"),
        units,
        queries,
        strong_binding,
        Path(parent["paths"]["strong_dense_snapshot"]),
        "strong",
        allow_cache_build,
    )
    rankings, traces, retrieval_seconds = build_rankings(
        units,
        queries,
        minilm_unit,
        minilm_query,
        strong_unit,
        strong_query,
    )
    return (
        parent,
        units,
        queries,
        rankings,
        traces,
        retrieval_seconds,
        {"minilm": minilm_seconds, "strong_dense": strong_seconds},
    )


def run_eligibility(config: dict[str, Any]) -> None:
    (
        _,
        _,
        queries,
        rankings,
        traces,
        retrieval_seconds,
        embedding_seconds,
    ) = _context(config, allow_cache_build=True)
    gate = config.get("eligibility_gate")
    if not isinstance(gate, dict):
        raise ValueError("eligibility_gate is missing")
    audit = summarize_eligibility(
        traces,
        float(gate["minimum_insertable_query_rate_each_dataset"]),
        float(gate["minimum_insertable_query_rate_combined"]),
    )
    audit["embedding_cache"] = {
        "minilm": file_identity(path_from_config(config, "minilm_embedding_cache")),
        "strong_dense": file_identity(
            path_from_config(config, "strong_embedding_cache")
        ),
    }
    audit["embedding_load_or_build_seconds"] = embedding_seconds
    audit["retrieval_seconds"] = retrieval_seconds
    write_new_files_atomically(
        (
            (path_from_config(config, "rankings"), render_jsonl(rankings)),
            (path_from_config(config, "candidate_trace"), render_jsonl(traces)),
            (path_from_config(config, "eligibility_audit"), render_json(audit)),
        )
    )
    print(
        f"{audit['gate']['status']} queries={len(queries)} "
        f"combined_insertable={audit['combined_insertable_query_rate']:.6f}"
    )
    if audit["gate"]["pass"] is not True:
        raise RuntimeError("STAGE4I_SIDECAR_ACTIVATION_DEGENERATE")


def run_generation(config: dict[str, Any], run_id: str) -> None:
    if run_id not in {"main", "rerun_subset"}:
        raise ValueError("run-id must be main or rerun_subset")
    (
        parent,
        units,
        queries,
        rankings,
        traces,
        retrieval_seconds,
        embedding_seconds,
    ) = _context(config, allow_cache_build=False)
    rankings_payload = render_jsonl(rankings)
    traces_payload = render_jsonl(traces)
    if assert_bound(config, "rankings").read_bytes() != rankings_payload:
        raise ValueError("frozen Stage4I rankings differ from reconstruction")
    if assert_bound(config, "candidate_trace").read_bytes() != traces_payload:
        raise ValueError("frozen Stage4I candidate trace differs")
    audit = load_json(assert_bound(config, "eligibility_audit"))
    if (
        not isinstance(audit, dict)
        or audit.get("gate", {}).get("status")
        != "STAGE4I_SIDECAR_ELIGIBILITY_GATE_PASS"
    ):
        raise RuntimeError("Stage4I eligibility gate has not passed")
    run_queries = queries if run_id == "main" else select_rerun_queries(queries)
    predictions, prompts, telemetry = generate_predictions(
        run_queries,
        units,
        rankings,
        Path(parent["paths"]["generator_snapshot"]),
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
            "embedding_load_seconds": embedding_seconds,
            "query_count": len(run_queries),
            "retrieval_seconds": retrieval_seconds,
            "run_id": run_id,
            "schema_version": SCHEMA_VERSION,
            "status": "STAGE4I_GOLDFREE_RUN_COMPLETE_PENDING_VERIFICATION",
        }
    )
    write_new_files_atomically(
        (
            (
                path_from_config(config, f"predictions_{run_id}"),
                render_jsonl(predictions),
            ),
            (
                path_from_config(config, f"prompt_audit_{run_id}"),
                render_jsonl(prompts),
            ),
            (
                path_from_config(config, f"telemetry_{run_id}"),
                render_json(telemetry),
            ),
        )
    )
    print(
        "STAGE4I_GOLDFREE_RUN_COMPLETE_PENDING_VERIFICATION "
        f"run={run_id} queries={len(run_queries)} calls={len(predictions)} "
        f"rankings_sha256={sha256_bytes(rankings_payload)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument(
        "--mode", required=True, choices=("eligibility", "main", "rerun_subset")
    )
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage4I config must be an object")
    if args.mode == "eligibility":
        run_eligibility(config)
    else:
        run_generation(config, args.mode)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE4I_GOLDFREE_RUN_FAIL: {exc}", file=sys.stderr)
        raise
