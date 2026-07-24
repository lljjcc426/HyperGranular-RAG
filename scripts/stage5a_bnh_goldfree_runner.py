"""Stage5A BGE-native Gold-free geometry, rankings, and generation."""

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
    _set_determinism,
)
from stage4i_sdc_goldfree_runner import build_or_load_exact_embeddings
from stage5a_bnh_common import (
    BASELINE_METHOD,
    BGE_ID,
    BGE_REVISION,
    CONFIRMATION_METHODS,
    DATASETS,
    GENERATOR_ID,
    GENERATOR_REVISION,
    RERUN_QUERIES_PER_DATASET,
    SAMPLE_SIZES,
    SCHEMA_VERSION,
    assert_bound,
    assert_implementation_binding,
    deterministic_method_order,
    development_method,
    file_identity,
    load_json,
    load_jsonl,
    load_parent_config,
    path_from_config,
    render_json,
    render_jsonl,
    rerun_selection_key,
    sha256_bytes,
    validate_authorization,
    validate_candidate_configs,
    validate_snapshot,
    write_new_files_atomically,
)
from stage5a_bnh_retrieval import (
    build_confirmation_rankings,
    build_development_rankings,
    build_units_queries,
    summarize_geometry_feasibility,
)


def _environment_and_models(
    config: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], Path, Path]:
    parent = load_parent_config(config)
    environment_path = Path(parent["paths"]["environment_manifest"])
    environment = load_json(environment_path)
    if not isinstance(environment, dict):
        raise ValueError("inherited environment manifest differs")
    _set_determinism(environment)
    models = parent.get("models")
    if not isinstance(models, dict):
        raise ValueError("Stage4H parent model binding is missing")
    bge = models.get("strong_dense")
    generator = models.get("generator")
    if not isinstance(bge, dict) or not isinstance(generator, dict):
        raise ValueError("Stage4H parent BGE/generator binding is incomplete")
    if (bge.get("model_id"), bge.get("revision")) != (BGE_ID, BGE_REVISION):
        raise ValueError("frozen BGE identity differs")
    if (generator.get("model_id"), generator.get("revision")) != (
        GENERATOR_ID,
        GENERATOR_REVISION,
    ):
        raise ValueError("frozen generator identity differs")
    bge_snapshot = Path(parent["paths"]["strong_dense_snapshot"])
    generator_snapshot = Path(parent["paths"]["generator_snapshot"])
    validate_snapshot(bge_snapshot, bge, "stage5a.bge")
    validate_snapshot(generator_snapshot, generator, "stage5a.generator")
    return bge, generator, bge_snapshot, generator_snapshot


def _load_boundary_context(
    config: dict[str, Any],
    boundary: str,
    allow_cache_build: bool,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    np.ndarray,
    np.ndarray,
    float,
    Path,
]:
    if boundary not in {"development", "confirmation"}:
        raise ValueError("unknown Stage5A boundary")
    bge, _, bge_snapshot, generator_snapshot = _environment_and_models(config)
    blind = load_jsonl(assert_bound(config, f"{boundary}_blind"))
    units, queries = build_units_queries(blind)
    if len(queries) != sum(SAMPLE_SIZES[boundary].values()):
        raise ValueError(f"{boundary}: query count differs")
    unit_embeddings, query_embeddings, seconds = build_or_load_exact_embeddings(
        path_from_config(config, f"{boundary}_bge_embedding_cache"),
        units,
        queries,
        bge,
        bge_snapshot,
        "strong",
        allow_cache_build,
    )
    return (
        units,
        queries,
        unit_embeddings,
        query_embeddings,
        seconds,
        generator_snapshot,
    )


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
        )[:RERUN_QUERIES_PER_DATASET[boundary]]
        if len(rows) != RERUN_QUERIES_PER_DATASET[boundary]:
            raise ValueError(f"{boundary}/{dataset}: insufficient rerun subset")
        selected.update(row["query_id"] for row in rows)
    return [row for row in queries if row["query_id"] in selected]


def _load_prefix_checkpoint(
    path: Path, task_keys: list[tuple[str, str]]
) -> dict[tuple[str, str], dict[str, Any]]:
    if not path.is_file():
        return {}
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict) or set(row) != {"audit", "prediction"}:
            raise ValueError(f"{path}:{line_number}: checkpoint schema differs")
        rows.append(row)
    if len(rows) > len(task_keys):
        raise ValueError("checkpoint exceeds frozen task plan")
    expected_prefix = task_keys[: len(rows)]
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for index, (row, expected_key) in enumerate(
        zip(rows, expected_prefix, strict=True), 1
    ):
        prediction = row["prediction"]
        audit = row["audit"]
        if not isinstance(prediction, dict) or not isinstance(audit, dict):
            raise ValueError(f"{path}:{index}: checkpoint row differs")
        key = (prediction.get("query_id"), prediction.get("method"))
        if key != expected_key or (
            audit.get("query_id"),
            audit.get("method"),
        ) != expected_key:
            raise ValueError(f"{path}:{index}: checkpoint is not a legal plan prefix")
        if (
            prediction.get("dataset") != audit.get("dataset")
            or prediction.get("sample_id") != audit.get("sample_id")
        ):
            raise ValueError(f"{path}:{index}: checkpoint identity differs")
        result[key] = row
    return result


def generate_predictions(
    queries: list[dict[str, Any]],
    units: list[dict[str, Any]],
    rankings: list[dict[str, Any]],
    methods: tuple[str, ...],
    generator_snapshot: Path,
    checkpoint_path: Path,
    namespace: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    ranking_by_query = {row["query_id"]: row for row in rankings}
    if len(ranking_by_query) != len(rankings):
        raise ValueError("ranking query identities duplicate")
    units_by_id = {row["unit_id"]: row for row in units}
    tasks = [
        (query, method)
        for query in queries
        for method in deterministic_method_order(
            query["query_id"], methods, namespace
        )
    ]
    task_keys = [(query["query_id"], method) for query, method in tasks]
    checkpoint = _load_prefix_checkpoint(checkpoint_path, task_keys)
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
        for task_index, (query, method) in enumerate(tasks, 1):
            key = (query["query_id"], method)
            if key in checkpoint:
                continue
            ranking_row = ranking_by_query.get(query["query_id"])
            if not isinstance(ranking_row, dict):
                raise ValueError(f"{query['query_id']}: ranking row missing")
            ranking = ranking_row["methods"].get(method)
            if not isinstance(ranking, list):
                raise ValueError(f"{query['query_id']}/{method}: ranking missing")
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
                    "STAGE5A_GENERATION_PROGRESS "
                    f"namespace={namespace} completed={len(checkpoint)}/{len(tasks)}"
                )
    if list(checkpoint) != task_keys:
        raise RuntimeError("Stage5A generation checkpoint is not the full task plan")
    predictions = [checkpoint[key]["prediction"] for key in task_keys]
    audits = [checkpoint[key]["audit"] for key in task_keys]
    telemetry = {
        "failed_calls": 0,
        "generated_in_this_process": generated_now,
        "generation_calls": len(predictions),
        "generation_seconds_by_method": {
            method: generation_seconds[method] for method in methods
        },
        "gpu_peak_memory_bytes": int(torch.cuda.max_memory_allocated()),
        "wall_time_seconds_this_process": time.perf_counter() - started,
    }
    del model, tokenizer
    gc.collect()
    torch.cuda.empty_cache()
    return predictions, audits, telemetry


def run_development_geometry(config: dict[str, Any]) -> None:
    candidate_configs = validate_candidate_configs(config)
    (
        units,
        queries,
        unit_embeddings,
        query_embeddings,
        embedding_seconds,
        _,
    ) = _load_boundary_context(config, "development", True)
    rankings, traces, retrieval_seconds = build_development_rankings(
        units,
        queries,
        unit_embeddings,
        query_embeddings,
        config,
    )
    audit = summarize_geometry_feasibility(traces, candidate_configs)
    audit.update(
        {
            "embedding_cache": file_identity(
                path_from_config(config, "development_bge_embedding_cache")
            ),
            "embedding_load_or_build_seconds": embedding_seconds,
            "query_count": len(queries),
            "retrieval_seconds": retrieval_seconds,
        }
    )
    write_new_files_atomically(
        (
            (
                path_from_config(config, "development_rankings"),
                render_jsonl(rankings),
            ),
            (
                path_from_config(config, "development_candidate_trace"),
                render_jsonl(traces),
            ),
            (
                path_from_config(config, "geometry_feasibility_audit"),
                render_json(audit),
            ),
        )
    )
    print(
        f"{audit['gate']['status']} queries={len(queries)} "
        f"eligible_configs={audit['eligible_config_count']}"
    )
    if audit["gate"]["pass"] is not True:
        raise RuntimeError("STAGE5A_BGE_NATIVE_GEOMETRY_DEGENERATE")


def _selected_config(config: dict[str, Any]) -> dict[str, Any]:
    verification = load_json(
        assert_bound(config, "development_final_verification")
    )
    if (
        not isinstance(verification, dict)
        or verification.get("status")
        != "STAGE5A_DEVELOPMENT_SELECTION_INDEPENDENT_VERIFICATION_PASS"
    ):
        raise PermissionError(
            "Stage5A development selection is not independently verified"
        )
    manifest = load_json(assert_bound(config, "development_selected_config"))
    if (
        not isinstance(manifest, dict)
        or manifest.get("status")
        != "STAGE5A_DEVELOPMENT_UNIQUE_CONFIGURATION_FROZEN"
    ):
        raise PermissionError("Stage5A development configuration is not frozen")
    selected = manifest.get("selected_config")
    if not isinstance(selected, dict):
        raise ValueError("selected_config row is missing")
    candidates = {
        row["config_id"]: row for row in validate_candidate_configs(config)
    }
    if candidates.get(selected.get("config_id")) != selected:
        raise ValueError("selected config differs from preregistered family")
    return selected


def run_confirmation_rankings(config: dict[str, Any]) -> None:
    selected = _selected_config(config)
    (
        units,
        queries,
        unit_embeddings,
        query_embeddings,
        embedding_seconds,
        _,
    ) = _load_boundary_context(config, "confirmation", True)
    rankings, traces, retrieval_seconds = build_confirmation_rankings(
        units,
        queries,
        unit_embeddings,
        query_embeddings,
        selected,
    )
    telemetry = {
        "embedding_cache": file_identity(
            path_from_config(config, "confirmation_bge_embedding_cache")
        ),
        "embedding_load_or_build_seconds": embedding_seconds,
        "query_count": len(queries),
        "retrieval_seconds": retrieval_seconds,
        "schema_version": SCHEMA_VERSION,
        "selected_config_id": selected["config_id"],
        "status": "STAGE5A_CONFIRMATION_RANKINGS_FROZEN_PENDING_VERIFICATION",
    }
    write_new_files_atomically(
        (
            (
                path_from_config(config, "confirmation_rankings"),
                render_jsonl(rankings),
            ),
            (
                path_from_config(config, "confirmation_candidate_trace"),
                render_jsonl(traces),
            ),
            (
                path_from_config(config, "confirmation_retrieval_telemetry"),
                render_json(telemetry),
            ),
        )
    )
    print(
        "STAGE5A_CONFIRMATION_RANKINGS_FROZEN_PENDING_VERIFICATION "
        f"queries={len(queries)} selected_config={selected['config_id']}"
    )


def _frozen_rankings(
    config: dict[str, Any],
    boundary: str,
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    unit_embeddings: np.ndarray,
    query_embeddings: np.ndarray,
) -> tuple[list[dict[str, Any]], tuple[str, ...], float]:
    if boundary == "development":
        rankings, traces, seconds = build_development_rankings(
            units, queries, unit_embeddings, query_embeddings, config
        )
        methods = (BASELINE_METHOD,) + tuple(
            development_method(row["config_id"])
            for row in validate_candidate_configs(config)
        )
    else:
        selected = _selected_config(config)
        rankings, traces, seconds = build_confirmation_rankings(
            units, queries, unit_embeddings, query_embeddings, selected
        )
        methods = CONFIRMATION_METHODS
    frozen_rankings = assert_bound(config, f"{boundary}_rankings")
    frozen_traces = assert_bound(config, f"{boundary}_candidate_trace")
    if frozen_rankings.read_bytes() != render_jsonl(rankings):
        raise ValueError(f"{boundary}: frozen rankings differ from reconstruction")
    if frozen_traces.read_bytes() != render_jsonl(traces):
        raise ValueError(f"{boundary}: frozen candidate trace differs")
    return rankings, methods, seconds


def run_generation(
    config: dict[str, Any], boundary: str, run_id: str
) -> None:
    if run_id not in {"main", "rerun_subset"}:
        raise ValueError("run_id must be main or rerun_subset")
    (
        units,
        queries,
        unit_embeddings,
        query_embeddings,
        embedding_seconds,
        generator_snapshot,
    ) = _load_boundary_context(config, boundary, False)
    rankings, methods, retrieval_seconds = _frozen_rankings(
        config,
        boundary,
        units,
        queries,
        unit_embeddings,
        query_embeddings,
    )
    run_queries = (
        queries
        if run_id == "main"
        else select_rerun_queries(queries, boundary)
    )
    namespace = f"stage5a_bnh_{boundary}_{run_id}_v1"
    predictions, prompts, telemetry = generate_predictions(
        run_queries,
        units,
        rankings,
        methods,
        generator_snapshot,
        path_from_config(config, f"{boundary}_checkpoint_{run_id}"),
        namespace,
    )
    telemetry.update(
        {
            "boundary": boundary,
            "embedding_cache": file_identity(
                path_from_config(config, f"{boundary}_bge_embedding_cache")
            ),
            "embedding_load_seconds": embedding_seconds,
            "query_count": len(run_queries),
            "retrieval_reconstruction_seconds": retrieval_seconds,
            "run_id": run_id,
            "schema_version": SCHEMA_VERSION,
            "status": "STAGE5A_GOLDFREE_GENERATION_COMPLETE_PENDING_VERIFICATION",
        }
    )
    write_new_files_atomically(
        (
            (
                path_from_config(
                    config, f"{boundary}_predictions_{run_id}"
                ),
                render_jsonl(predictions),
            ),
            (
                path_from_config(
                    config, f"{boundary}_prompt_audit_{run_id}"
                ),
                render_jsonl(prompts),
            ),
            (
                path_from_config(config, f"{boundary}_telemetry_{run_id}"),
                render_json(telemetry),
            ),
        )
    )
    print(
        "STAGE5A_GOLDFREE_GENERATION_COMPLETE_PENDING_VERIFICATION "
        f"boundary={boundary} run={run_id} queries={len(run_queries)} "
        f"calls={len(predictions)} "
        f"rankings_sha256={sha256_bytes(render_jsonl(rankings))}"
    )


def run(config: dict[str, Any], mode: str) -> None:
    validate_authorization(config)
    assert_implementation_binding(config, Path(__file__).resolve().parents[1])
    if mode == "development_geometry":
        run_development_geometry(config)
    elif mode == "confirmation_rankings":
        run_confirmation_rankings(config)
    elif mode in {
        "development_main",
        "development_rerun_subset",
        "confirmation_main",
        "confirmation_rerun_subset",
    }:
        boundary, suffix = mode.split("_", 1)
        run_generation(config, boundary, suffix)
    else:
        raise ValueError(f"unknown Stage5A mode: {mode}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument(
        "--mode",
        required=True,
        choices=(
            "development_geometry",
            "development_main",
            "development_rerun_subset",
            "confirmation_rankings",
            "confirmation_main",
            "confirmation_rerun_subset",
        ),
    )
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage5A config must be an object")
    run(config, args.mode)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE5A_GOLDFREE_RUN_FAIL: {exc}", file=sys.stderr)
        raise
