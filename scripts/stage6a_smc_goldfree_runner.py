"""Execute Stage6A Gold-free retrieval, matched selection, and generation."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from stage5a_bnh_goldfree_runner import generate_predictions
from stage6a_smc_common import (
    DATASETS,
    GENERATOR_ID,
    GENERATOR_REVISION,
    RERUN_QUERIES_PER_DATASET,
    SAMPLE_SIZES,
    assert_bound,
    assert_implementation_binding,
    development_methods,
    file_identity,
    load_json,
    load_jsonl,
    path_from_config,
    render_json,
    render_jsonl,
    rerun_selection_key,
    validate_authorization,
    validate_confirmation_methods,
    validate_snapshot,
    write_new_files_atomically,
)
from stage6a_smc_models import (
    build_or_load_embeddings,
    build_reranker_rows,
    set_frozen_runtime,
    validate_models,
)
from stage6a_smc_retrieval import build_rankings, build_units_queries


def select_rerun_queries(
    queries: list[dict[str, Any]], boundary: str
) -> list[dict[str, Any]]:
    by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in queries:
        by_dataset[row["dataset"]].append(row)
    selected: set[str] = set()
    for dataset in DATASETS:
        rows = sorted(
            by_dataset[dataset],
            key=lambda row: rerun_selection_key(
                boundary, dataset, row["query_id"]
            ),
        )[: RERUN_QUERIES_PER_DATASET[boundary]]
        if len(rows) != RERUN_QUERIES_PER_DATASET[boundary]:
            raise ValueError(f"{boundary}/{dataset}: insufficient rerun queries")
        selected.update(row["query_id"] for row in rows)
    return [row for row in queries if row["query_id"] in selected]


def _generator(config: dict[str, Any]) -> Path:
    binding = config.get("models", {}).get("generator")
    if not isinstance(binding, dict) or (
        binding.get("model_id"),
        binding.get("revision"),
    ) != (GENERATOR_ID, GENERATOR_REVISION):
        raise ValueError("frozen generator identity differs")
    snapshot = Path(binding["snapshot_path"])
    validate_snapshot(snapshot, binding, "stage6a.generator")
    return snapshot


def _methods(config: dict[str, Any], boundary: str) -> tuple[str, ...]:
    if boundary == "development":
        return development_methods()
    lock_path = path_from_config(config, "development_selection_lock")
    lock = load_json(lock_path)
    if not isinstance(lock, dict) or lock.get("status") != (
        "STAGE6A_DEVELOPMENT_SELECTION_LOCKED_FOR_CONFIRMATION"
    ):
        raise ValueError("development selection lock is absent or invalid")
    return validate_confirmation_methods(lock.get("confirmation_methods"))


def _load_reranker_rows(path: Path) -> list[dict[str, Any]]:
    rows = load_jsonl(path)
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"{path}: reranker trace differs")
    return rows


def run(
    config: dict[str, Any],
    boundary: str,
    run_id: str,
    process_call_limit: int | None,
) -> None:
    if boundary not in {"development", "confirmation"}:
        raise ValueError("unknown Stage6A boundary")
    if run_id not in {"main", "rerun"}:
        raise ValueError("run_id must be main or rerun")
    validate_authorization(config)
    repository_root = Path(__file__).resolve().parents[1]
    assert_implementation_binding(config, repository_root)
    set_frozen_runtime(config["runtime"])
    embedding_binding, _, embedding_snapshot, reranker_snapshot = validate_models(
        config
    )
    generator_snapshot = _generator(config)
    blind = load_jsonl(assert_bound(config, f"{boundary}_blind"))
    units, all_queries = build_units_queries(blind)
    expected = sum(SAMPLE_SIZES[boundary].values())
    if len(all_queries) != expected:
        raise ValueError(f"{boundary}: query count differs")
    methods = _methods(config, boundary)

    embedding_path = path_from_config(config, f"{boundary}_embedding_cache")
    unit_embeddings, query_embeddings, embedding_telemetry = (
        build_or_load_embeddings(
            embedding_path,
            units,
            all_queries,
            embedding_binding,
            embedding_snapshot,
            allow_build=run_id == "main",
        )
    )
    reranker_path = path_from_config(config, f"{boundary}_reranker_trace")
    if reranker_path.is_file():
        reranker_rows = _load_reranker_rows(reranker_path)
        reranker_telemetry = {
            "cache_loaded": True,
            "gpu_peak_memory_bytes": 0,
            "pair_count": sum(
                len(row["common_pool_unit_ids"]) for row in reranker_rows
            ),
            "seconds": 0.0,
        }
    else:
        if run_id != "main":
            raise FileNotFoundError("rerun requires frozen reranker trace")
        reranker_rows, reranker_telemetry = build_reranker_rows(
            units,
            all_queries,
            unit_embeddings,
            query_embeddings,
            reranker_snapshot,
        )
        write_new_files_atomically(
            [(reranker_path, render_jsonl(reranker_rows))]
        )
        reranker_telemetry["cache_loaded"] = False

    rankings, traces = build_rankings(
        units,
        all_queries,
        unit_embeddings,
        query_embeddings,
        reranker_rows,
        methods,
    )
    if run_id == "rerun":
        selected_queries = select_rerun_queries(all_queries, boundary)
        selected_ids = {row["query_id"] for row in selected_queries}
        queries = selected_queries
        rankings = [row for row in rankings if row["query_id"] in selected_ids]
        traces = [row for row in traces if row["query_id"] in selected_ids]
    else:
        queries = all_queries

    checkpoint_path = path_from_config(
        config, f"{boundary}_{run_id}_generation_checkpoint"
    )
    predictions, audits, generation_telemetry = generate_predictions(
        queries,
        units,
        rankings,
        methods,
        generator_snapshot,
        checkpoint_path,
        f"stage6a::{boundary}",
        process_call_limit=process_call_limit,
    )
    telemetry = {
        "boundary": boundary,
        "embedding": embedding_telemetry,
        "embedding_cache": file_identity(embedding_path),
        "generation": generation_telemetry,
        "method_count": len(methods),
        "methods": list(methods),
        "query_count": len(queries),
        "reranker": reranker_telemetry,
        "reranker_trace": file_identity(reranker_path),
        "run_id": run_id,
        "status": "STAGE6A_GOLDFREE_RUN_COMPLETE",
    }
    outputs = [
        (
            path_from_config(config, f"{boundary}_{run_id}_rankings"),
            render_jsonl(rankings),
        ),
        (
            path_from_config(config, f"{boundary}_{run_id}_candidate_trace"),
            render_jsonl(traces),
        ),
        (
            path_from_config(config, f"{boundary}_{run_id}_predictions"),
            render_jsonl(predictions),
        ),
        (
            path_from_config(config, f"{boundary}_{run_id}_prompt_audit"),
            render_jsonl(audits),
        ),
        (
            path_from_config(config, f"{boundary}_{run_id}_telemetry"),
            render_json(telemetry),
        ),
    ]
    write_new_files_atomically(outputs)
    print(
        "STAGE6A_GOLDFREE_RUN_COMPLETE "
        f"boundary={boundary} run={run_id} queries={len(queries)} "
        f"methods={len(methods)} calls={len(predictions)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument(
        "--boundary", required=True, choices=("development", "confirmation")
    )
    parser.add_argument("--run-id", required=True, choices=("main", "rerun"))
    parser.add_argument("--process-call-limit", type=int)
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage6A config must be an object")
    run(config, args.boundary, args.run_id, args.process_call_limit)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE6A_GOLDFREE_FAIL: {exc}", file=sys.stderr)
        raise
