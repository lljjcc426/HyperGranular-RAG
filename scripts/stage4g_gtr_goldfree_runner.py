"""Gold-free Stage4G inference with the frozen Gemma mobile-QAT snapshot."""

from __future__ import annotations

import argparse
import gc
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Iterable

from stage4g_gtr_common import (
    DATASETS,
    MAX_NEW_TOKENS,
    METHODS,
    SCHEMA_VERSION,
    SYSTEM_MESSAGE,
    TOKEN_CAP,
    assert_identity,
    assert_implementation_binding,
    file_identity,
    load_frozen_dataset,
    load_json,
    method_order,
    ranking_digest,
    render_json,
    render_jsonl,
    require_int,
    require_string,
    select_rerun_query_ids,
    semantic_prompt_digest,
    write_new_files_atomically,
)


ROOT = Path(__file__).resolve().parents[1]


def _path(config: dict[str, Any], key: str) -> Path:
    value = config.get("paths", {}).get(key)
    return Path(require_string(value, f"paths.{key}"))


def _set_determinism(config: dict[str, Any]) -> None:
    environment = config["environment"]["variables"]
    for key, expected in environment.items():
        os.environ[key] = str(expected)
    import torch

    torch.manual_seed(0)
    torch.cuda.manual_seed_all(0)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False


def validate_snapshot(snapshot: Path, model: dict[str, Any]) -> None:
    if snapshot.name != model["revision"]:
        raise ValueError("Gemma snapshot revision path differs")
    files = model.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("Gemma file binding is missing")
    for relative, expected in files.items():
        assert_identity(snapshot / relative, expected, f"Gemma snapshot {relative}")


def _messages(question: str, evidence_lines: Iterable[str]) -> list[dict[str, str]]:
    evidence = "\n".join(evidence_lines)
    return [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": f"Evidence:\n{evidence}\n\nQuestion: {question}\nFinal answer:"},
    ]


class GemmaAdapter:
    def __init__(self, snapshot: Path, config: dict[str, Any]):
        _set_determinism(config)
        import torch
        from transformers import AutoModelForMultimodalLM, AutoProcessor

        self.frontend = AutoProcessor.from_pretrained(snapshot, local_files_only=True)
        self.model = AutoModelForMultimodalLM.from_pretrained(
            snapshot,
            local_files_only=True,
            device_map={"": 0},
        ).eval()
        devices = {str(parameter.device) for parameter in self.model.parameters()}
        if devices != {"cuda:0"}:
            raise RuntimeError(f"Gemma must run entirely on cuda:0, got {sorted(devices)}")
        self.tokenizer = self.frontend.tokenizer
        self.torch = torch

    def template(self, messages: list[dict[str, str]], *, tokenize: bool) -> Any:
        kwargs: dict[str, Any] = {
            "tokenize": tokenize,
            "add_generation_prompt": True,
            "enable_thinking": False,
        }
        if tokenize:
            kwargs.update(return_dict=True, return_tensors="pt")
        return self.frontend.apply_chat_template(messages, **kwargs)

    def token_ids(self, messages: list[dict[str, str]]) -> list[int]:
        value = self.template(messages, tokenize=True)["input_ids"]
        values = value.tolist()
        if values and isinstance(values[0], list):
            values = values[0]
        return [int(item) for item in values]

    def generate(self, messages: list[dict[str, str]]) -> tuple[str, list[int]]:
        inputs = self.template(messages, tokenize=True).to("cuda")
        input_length = int(inputs["input_ids"].shape[-1])
        with self.torch.inference_mode():
            output = self.model.generate(
                **inputs,
                do_sample=False,
                num_beams=1,
                max_new_tokens=MAX_NEW_TOKENS,
                use_cache=True,
            )
        completion_ids = [int(value) for value in output[0, input_length:].tolist()]
        prediction = self.frontend.decode(completion_ids, skip_special_tokens=True).strip()
        return prediction, completion_ids


def build_prompt(
    adapter: GemmaAdapter,
    question: str,
    ranked_units: list[dict[str, Any]],
) -> dict[str, Any]:
    if not ranked_units:
        raise ValueError("Cannot build a prompt from an empty ranking")
    if len(adapter.token_ids(_messages(question, []))) > TOKEN_CAP:
        raise ValueError("Question and template exceed the token cap")
    lines: list[str] = []
    included_units: list[dict[str, Any]] = []
    rank1_truncated = False
    for rank, unit in enumerate(ranked_units, start=1):
        line = f"[{rank}] {unit['title']}: {unit['text']}"
        if len(adapter.token_ids(_messages(question, lines + [line]))) <= TOKEN_CAP:
            lines.append(line)
            included_units.append(unit)
            continue
        if rank > 1:
            break
        tokens = list(adapter.tokenizer.encode(line, add_special_tokens=False))
        for kept in range(len(tokens), -1, -1):
            shortened = adapter.tokenizer.decode(
                tokens[:kept],
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False,
            )
            if len(adapter.token_ids(_messages(question, [shortened]))) <= TOKEN_CAP:
                lines = [shortened]
                included_units = [unit]
                rank1_truncated = True
                break
        if not lines:
            raise ValueError("Rank-1 evidence cannot fit within token cap")
        break
    messages = _messages(question, lines)
    input_token_count = len(adapter.token_ids(messages))
    if input_token_count > TOKEN_CAP:
        raise AssertionError("Prompt cap enforcement failed")
    return {
        "evidence_unit_ids": [unit["unit_id"] for unit in included_units],
        "input_token_count": input_token_count,
        "messages": messages,
        "prompt_semantic_content_sha256": semantic_prompt_digest(question, included_units, lines),
        "rank1_truncated": rank1_truncated,
    }


def _bundles(config: dict[str, Any]) -> tuple[
    list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]
]:
    all_queries: list[dict[str, Any]] = []
    all_rankings: dict[str, dict[str, Any]] = {}
    all_units: dict[str, dict[str, Any]] = {}
    for dataset in DATASETS:
        entry = config["inputs"][dataset]
        blind = Path(entry["blind"]["path"])
        rankings = Path(entry["rankings"]["path"])
        assert_identity(blind, entry["blind"], f"{dataset} blind")
        assert_identity(rankings, entry["rankings"], f"{dataset} rankings")
        queries, ranking_map, unit_maps = load_frozen_dataset(dataset, blind, rankings)
        expected_rows = require_int(entry["query_count"], f"{dataset}.query_count", minimum=1)
        if len(queries) != expected_rows:
            raise ValueError(f"{dataset} query count differs")
        all_queries.extend(queries)
        all_rankings.update(ranking_map)
        all_units.update(unit_maps)
    return all_queries, all_rankings, all_units


def planned_pairs(
    queries: list[dict[str, Any]],
    run_id: str,
) -> list[tuple[dict[str, Any], str]]:
    selected = select_rerun_query_ids(queries)
    selected_sets = {dataset: set(values) for dataset, values in selected.items()}
    result: list[tuple[dict[str, Any], str]] = []
    for query in queries:
        if run_id == "rerun_subset" and query["query_id"] not in selected_sets[query["dataset"]]:
            continue
        for method in method_order(query["query_id"]):
            result.append((query, method))
    return result


def _load_checkpoint(path: Path, plan: list[tuple[dict[str, Any], str]]) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for index, line in enumerate(handle):
            if index >= len(plan) or not line.endswith("\n"):
                raise ValueError("Stage4G checkpoint is not a valid plan prefix")
            row = json.loads(line)
            query, method = plan[index]
            if row.get("query_id") != query["query_id"] or row.get("method") != method:
                raise ValueError("Stage4G checkpoint identity/order differs")
            if not isinstance(row.get("prediction"), dict) or not isinstance(row.get("audit"), dict):
                raise ValueError("Stage4G checkpoint payload differs")
            rows.append(row)
    return rows


def _append_checkpoint(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    with path.open("a", encoding="utf-8", newline="") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def run(config: dict[str, Any], run_id: str) -> None:
    if config.get("official_execution", {}).get("authorized") is not True:
        raise PermissionError("Stage4G official execution is not authorized")
    if run_id not in {"main", "rerun_subset"}:
        raise ValueError("run_id must be main or rerun_subset")
    assert_implementation_binding(config, ROOT)
    snapshot = _path(config, "generator_snapshot")
    validate_snapshot(snapshot, config["generator"])
    queries, rankings, units = _bundles(config)
    plan = planned_pairs(queries, run_id)
    expected = 8_000 if run_id == "main" else 400
    if len(plan) != expected:
        raise ValueError(f"Stage4G {run_id} expected {expected} calls, got {len(plan)}")
    predictions_output = _path(config, f"predictions_{run_id}")
    audits_output = _path(config, f"prompt_audit_{run_id}")
    telemetry_output = _path(config, f"telemetry_{run_id}")
    for output in (predictions_output, audits_output, telemetry_output):
        if output.exists():
            raise FileExistsError(f"Refusing to overwrite Stage4G artifact: {output}")
    checkpoint = _path(config, f"checkpoint_{run_id}")
    completed = _load_checkpoint(checkpoint, plan)
    previous_elapsed = float(completed[-1]["elapsed_seconds"]) if completed else 0.0
    previous_peak = int(completed[-1]["peak_gpu_memory_bytes"]) if completed else 0
    import torch
    import transformers

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    adapter = GemmaAdapter(snapshot, config)
    segment_started = time.perf_counter()
    ranking_sources = {
        dataset: config["inputs"][dataset]["rankings"]["sha256"] for dataset in DATASETS
    }
    for index in range(len(completed), len(plan)):
        query, method = plan[index]
        key = "dense_top20_unit_ids" if method == METHODS[0] else "static_q25_top20_unit_ids"
        ranked_ids = rankings[query["query_id"]][key]
        ranked_units = [units[query["query_id"]][unit_id] for unit_id in ranked_ids]
        prompt = build_prompt(adapter, query["question"], ranked_units)
        prediction, completion_ids = adapter.generate(prompt["messages"])
        prediction_row = {
            "dataset": query["dataset"],
            "method": method,
            "prediction": prediction,
            "query_id": query["query_id"],
            "sample_id": query["sample_id"],
        }
        audit_row = {
            "completion_token_ids": completion_ids,
            "dataset": query["dataset"],
            "evidence_unit_ids": prompt["evidence_unit_ids"],
            "input_token_count": prompt["input_token_count"],
            "method": method,
            "prediction": prediction,
            "prompt_semantic_content_sha256": prompt["prompt_semantic_content_sha256"],
            "query_id": query["query_id"],
            "rank1_truncated": prompt["rank1_truncated"],
            "ranking_source_sha256": ranking_sources[query["dataset"]],
            "ranking_unit_ids_sha256": ranking_digest(ranked_ids),
            "sample_id": query["sample_id"],
        }
        elapsed = previous_elapsed + (time.perf_counter() - segment_started)
        peak = max(previous_peak, int(torch.cuda.max_memory_allocated()))
        checkpoint_row = {
            "audit": audit_row,
            "elapsed_seconds": elapsed,
            "method": method,
            "peak_gpu_memory_bytes": peak,
            "prediction": prediction_row,
            "query_id": query["query_id"],
        }
        _append_checkpoint(checkpoint, checkpoint_row)
        completed.append(checkpoint_row)
        if (index + 1) % 100 == 0:
            print(f"stage4g {run_id}: {index + 1}/{len(plan)}", file=sys.stderr, flush=True)
    prediction_rows = [row["prediction"] for row in completed]
    audit_rows = [row["audit"] for row in completed]
    groups: dict[str, dict[str, Any]] = {}
    for dataset in DATASETS:
        for method in METHODS:
            rows = [row for row in audit_rows if row["dataset"] == dataset and row["method"] == method]
            groups[f"{dataset}|{method}"] = {
                "calls": len(rows),
                "completion_tokens": sum(len(row["completion_token_ids"]) for row in rows),
                "included_evidence_units_mean": sum(len(row["evidence_unit_ids"]) for row in rows) / len(rows),
                "input_tokens_mean": sum(row["input_token_count"] for row in rows) / len(rows),
                "truncated_calls": sum(int(row["rank1_truncated"]) for row in rows),
                "unknown_calls": sum(int(row["prediction"].strip().upper() == "UNKNOWN") for row in rows),
            }
    telemetry = {
        "cuda_devices": sorted({str(parameter.device) for parameter in adapter.model.parameters()}),
        "determinism_contract": "B_FULL_MAIN_PLUS_PREHASH_STRATIFIED_SUBSET_RERUN",
        "failed_calls": 0,
        "generation_calls": len(completed),
        "groups": groups,
        "gpu_peak_memory_bytes": int(completed[-1]["peak_gpu_memory_bytes"]),
        "model_id": config["generator"]["model_id"],
        "python": sys.version.split()[0],
        "revision": config["generator"]["revision"],
        "run_id": run_id,
        "runtime_format": config["generator"]["runtime_format"],
        "schema_version": SCHEMA_VERSION,
        "snapshot_weight": file_identity(snapshot / "model.safetensors"),
        "torch": torch.__version__,
        "torchvision": __import__("torchvision").__version__,
        "transformers": transformers.__version__,
        "gpu_name": torch.cuda.get_device_name(0),
        "wall_time_seconds": float(completed[-1]["elapsed_seconds"]),
    }
    del adapter
    gc.collect()
    torch.cuda.empty_cache()
    write_new_files_atomically([
        (predictions_output, render_jsonl(prediction_rows)),
        (audits_output, render_jsonl(audit_rows)),
        (telemetry_output, render_json(telemetry)),
    ])
    checkpoint.unlink()
    print(f"STAGE4G_GTR_{run_id.upper()}_COMPLETE calls={len(completed)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-id", choices=("main", "rerun_subset"), required=True)
    args = parser.parse_args()
    config = load_json(args.config)
    run(config, args.run_id)


if __name__ == "__main__":
    main()
