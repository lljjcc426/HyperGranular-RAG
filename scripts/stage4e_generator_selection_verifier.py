"""Independent verifier for the frozen Stage4E generator-selection experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import string
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import numpy as np


SCHEMA_VERSION = "stage4e_generator_selection_v1"
DATASET = "hotpotqa"
SOURCE_BYTES = 1_699_596
SOURCE_SHA256 = "0818FCB2E130C3BCC207912F59F9ACE14B534321AD93686378E6923FF7405AC5"
QUERY_COUNT = 200
BOOTSTRAP_SEED = 20260722
BOOTSTRAP_ITERATIONS = 10_000
TOKEN_CAP = 4096
MODELS = ("qwen", "gemma")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def render_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def render_jsonl(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(
        (json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")
        for row in rows
    )


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.endswith("\n"):
                raise ValueError(f"{path} line {line_number} lacks LF terminator")
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path} line {line_number} must be an object")
            rows.append(value)
    return rows


def reconstruct_channels(source: Path) -> tuple[bytes, bytes, dict[str, list[str]]]:
    if not source.is_file() or source.stat().st_size != SOURCE_BYTES or sha256_file(source) != SOURCE_SHA256:
        raise ValueError("Source identity differs")
    source_rows = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(source_rows, list) or len(source_rows) != QUERY_COUNT:
        raise ValueError("Source row count differs")
    blind: list[dict[str, Any]] = []
    gold: list[dict[str, Any]] = []
    unit_orders: dict[str, list[str]] = {}
    seen: set[str] = set()
    for index, row in enumerate(source_rows):
        if not isinstance(row, dict):
            raise ValueError(f"source[{index}] must be an object")
        sample_id = row.get("id")
        if not isinstance(sample_id, str) or not sample_id or sample_id in seen:
            raise ValueError(f"source[{index}] id contract differs")
        seen.add(sample_id)
        if row.get("dataset") != DATASET or not isinstance(row.get("question"), str) or not isinstance(row.get("answer"), str):
            raise ValueError(f"source[{index}] identity/text contract differs")
        units: list[dict[str, str]] = []
        for context_index, context in enumerate(row.get("contexts", [])):
            if not isinstance(context, dict) or not isinstance(context.get("title"), str) or not context["title"]:
                raise ValueError(f"source[{index}] context contract differs")
            if not isinstance(context.get("sentences"), list):
                raise ValueError(f"source[{index}] sentence list differs")
            for sentence_index, sentence in enumerate(context["sentences"]):
                if not isinstance(sentence, str):
                    raise ValueError(f"source[{index}] sentence type differs")
                text = " ".join(sentence.split())
                if text:
                    units.append({
                        "text": text,
                        "title": context["title"],
                        "unit_id": f"{sample_id}::{context_index:02d}::{sentence_index:03d}",
                    })
        if not units:
            raise ValueError(f"source[{index}] has no units")
        query_id = f"{DATASET}::{sample_id}"
        blind.append({"dataset": DATASET, "query_id": query_id, "question": row["question"], "sample_id": sample_id, "units": units})
        gold.append({"answer": row["answer"], "dataset": DATASET, "query_id": query_id, "sample_id": sample_id})
        unit_orders[query_id] = [unit["unit_id"] for unit in units]
    return render_jsonl(blind), render_jsonl(gold), unit_orders


def normalize_answer(value: str) -> str:
    text = value.lower()
    text = "".join(character for character in text if character not in set(string.punctuation))
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    return " ".join(text.split())


def answer_scores(prediction: str, ground_truth: str) -> tuple[float, float]:
    prediction = normalize_answer(prediction)
    ground_truth = normalize_answer(ground_truth)
    em = float(prediction == ground_truth)
    if (
        prediction in {"yes", "no", "noanswer"} and prediction != ground_truth
    ) or (
        ground_truth in {"yes", "no", "noanswer"} and prediction != ground_truth
    ):
        return em, 0.0
    prediction_tokens = prediction.split()
    ground_truth_tokens = ground_truth.split()
    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    same = sum(common.values())
    if same == 0:
        return em, 0.0
    precision = same / len(prediction_tokens)
    recall = same / len(ground_truth_tokens)
    return em, 2 * precision * recall / (precision + recall)


def paired_bootstrap(qwen: np.ndarray, gemma: np.ndarray) -> dict[str, float]:
    delta = np.asarray(gemma - qwen, dtype="float64")
    if delta.shape != (QUERY_COUNT,) or not np.isfinite(delta).all():
        raise ValueError("Bootstrap inputs differ")
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draws = np.empty(BOOTSTRAP_ITERATIONS, dtype="float64")
    for index in range(BOOTSTRAP_ITERATIONS):
        selected = rng.integers(0, QUERY_COUNT, size=QUERY_COUNT)
        draws[index] = float(np.mean(delta[selected]))
    return {
        "lower_95": float(np.quantile(draws, 0.025, method="linear")),
        "point": float(np.mean(delta)),
        "upper_95": float(np.quantile(draws, 0.975, method="linear")),
    }


def load_predictions(path: Path, model: str) -> list[dict[str, Any]]:
    rows = load_jsonl(path)
    expected = {"dataset", "model", "prediction", "query_id", "sample_id"}
    if len(rows) != QUERY_COUNT:
        raise ValueError(f"{model} prediction count differs")
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if set(row) != expected or row["dataset"] != DATASET or row["model"] != model:
            raise ValueError(f"{model} prediction[{index}] contract differs")
        if not all(isinstance(row[key], str) for key in ("prediction", "query_id", "sample_id")):
            raise ValueError(f"{model} prediction[{index}] string type differs")
        if row["query_id"] != f"{DATASET}::{row['sample_id']}" or row["query_id"] in seen:
            raise ValueError(f"{model} prediction[{index}] identity differs")
        seen.add(row["query_id"])
    return rows


def validate_audits(path: Path, model: str, unit_orders: dict[str, list[str]]) -> None:
    rows = load_jsonl(path)
    expected = {
        "completion_token_ids", "dataset", "evidence_unit_ids", "input_token_count",
        "model", "prompt_sha256", "query_id", "rank1_truncated", "sample_id",
    }
    if len(rows) != QUERY_COUNT:
        raise ValueError(f"{model} audit count differs")
    for index, row in enumerate(rows):
        if set(row) != expected or row["dataset"] != DATASET or row["model"] != model:
            raise ValueError(f"{model} audit[{index}] contract differs")
        if row["query_id"] != f"{DATASET}::{row['sample_id']}" or row["query_id"] not in unit_orders:
            raise ValueError(f"{model} audit[{index}] identity differs")
        count = row["input_token_count"]
        if isinstance(count, bool) or not isinstance(count, int) or not (1 <= count <= TOKEN_CAP):
            raise ValueError(f"{model} audit[{index}] token count differs")
        if not isinstance(row["rank1_truncated"], bool):
            raise ValueError(f"{model} audit[{index}] truncation type differs")
        completion = row["completion_token_ids"]
        if not isinstance(completion, list) or len(completion) > 32 or any(isinstance(value, bool) or not isinstance(value, int) for value in completion):
            raise ValueError(f"{model} audit[{index}] completion tokens differ")
        included = row["evidence_unit_ids"]
        if not isinstance(included, list) or not included or any(not isinstance(value, str) or not value for value in included):
            raise ValueError(f"{model} audit[{index}] evidence ids differ")
        expected_prefix = unit_orders[row["query_id"]][:len(included)]
        if included != expected_prefix:
            raise ValueError(f"{model} audit[{index}] evidence order is not the frozen prefix")
        prompt_sha = row["prompt_sha256"]
        if not isinstance(prompt_sha, str) or not re.fullmatch(r"[0-9A-F]{64}", prompt_sha):
            raise ValueError(f"{model} audit[{index}] prompt SHA differs")


def load_telemetry(path: Path, model: str, run_id: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        not isinstance(value, dict)
        or value.get("schema_version") != SCHEMA_VERSION
        or value.get("model") != model
        or value.get("run_id") != run_id
        or value.get("generation_calls") != QUERY_COUNT
        or value.get("failed_calls") != 0
        or value.get("cuda_devices") != ["cuda:0"]
    ):
        raise ValueError(f"{model} {run_id} telemetry differs")
    for key in ("wall_time_seconds", "gpu_peak_memory_bytes", "output_token_count"):
        number = value.get(key)
        if isinstance(number, bool) or not isinstance(number, (int, float)) or not math.isfinite(float(number)) or float(number) < 0:
            raise ValueError(f"{model} {run_id} telemetry {key} differs")
    return value


def select_winner(means: dict[str, dict[str, float]], telemetry: dict[str, list[dict[str, Any]]]) -> tuple[str, str]:
    delta_f1 = means["gemma"]["f1"] - means["qwen"]["f1"]
    if abs(delta_f1) >= 0.010:
        return ("gemma" if delta_f1 > 0 else "qwen", "PRIMARY_F1_DIFFERENCE_AT_LEAST_0_010")
    delta_em = means["gemma"]["em"] - means["qwen"]["em"]
    if abs(delta_em) >= 0.010:
        return ("gemma" if delta_em > 0 else "qwen", "SECONDARY_EM_DIFFERENCE_AT_LEAST_0_010")
    times = {model: float(np.mean([run["wall_time_seconds"] for run in runs])) for model, runs in telemetry.items()}
    if abs(times["gemma"] - times["qwen"]) / max(times.values()) >= 0.01:
        return min(times, key=times.get), "WALL_TIME_TIEBREAKER"
    peaks = {model: max(int(run["gpu_peak_memory_bytes"]) for run in runs) for model, runs in telemetry.items()}
    return min(peaks, key=peaks.get), "PEAK_GPU_MEMORY_TIEBREAKER"


def verify(args: argparse.Namespace) -> None:
    expected_blind, expected_gold, unit_orders = reconstruct_channels(args.source)
    if args.blind.read_bytes() != expected_blind or args.gold.read_bytes() != expected_gold:
        raise ValueError("Prepared blind/Gold channels differ from independent reconstruction")
    predictions: dict[str, list[dict[str, Any]]] = {}
    telemetry: dict[str, list[dict[str, Any]]] = {}
    for model in MODELS:
        main = getattr(args, f"{model}_main")
        rerun = getattr(args, f"{model}_rerun")
        audit_main = getattr(args, f"{model}_audit_main")
        audit_rerun = getattr(args, f"{model}_audit_rerun")
        if main.read_bytes() != rerun.read_bytes() or audit_main.read_bytes() != audit_rerun.read_bytes():
            raise ValueError(f"{model} main/rerun bytes differ")
        predictions[model] = load_predictions(main, model)
        validate_audits(audit_main, model, unit_orders)
        telemetry[model] = [
            load_telemetry(getattr(args, f"{model}_telemetry_main"), model, "main"),
            load_telemetry(getattr(args, f"{model}_telemetry_rerun"), model, "rerun"),
        ]
    gold = load_jsonl(args.gold)
    prediction_maps = {model: {row["query_id"]: row for row in rows} for model, rows in predictions.items()}
    values = {model: {"f1": [], "em": []} for model in MODELS}
    score_rows: list[dict[str, Any]] = []
    for row in gold:
        query_id = row["query_id"]
        score_row: dict[str, Any] = {"query_id": query_id, "sample_id": row["sample_id"]}
        for model in MODELS:
            prediction = prediction_maps[model][query_id]["prediction"]
            em, f1 = answer_scores(prediction, row["answer"])
            values[model]["em"].append(em)
            values[model]["f1"].append(f1)
            score_row[model] = {"answer_em": em, "answer_f1": f1, "prediction": prediction}
        score_rows.append(score_row)
    if args.scores.read_bytes() != render_jsonl(score_rows):
        raise ValueError("Score rows differ from independent reconstruction")
    arrays = {model: {metric: np.asarray(numbers, dtype="float64") for metric, numbers in metrics.items()} for model, metrics in values.items()}
    means = {model: {metric: float(np.mean(numbers)) for metric, numbers in metrics.items()} for model, metrics in arrays.items()}
    winner, reason = select_winner(means, telemetry)
    expected_summary = {
        "bootstrap": {
            "answer_em_gemma_minus_qwen": paired_bootstrap(arrays["qwen"]["em"], arrays["gemma"]["em"]),
            "answer_f1_gemma_minus_qwen": paired_bootstrap(arrays["qwen"]["f1"], arrays["gemma"]["f1"]),
            "iterations": BOOTSTRAP_ITERATIONS,
            "seed": BOOTSTRAP_SEED,
        },
        "decision": {"reason": reason, "selected_model": winner},
        "models": {
            model: {
                "answer_em": means[model]["em"],
                "answer_f1": means[model]["f1"],
                "main_rerun_audit_byte_identical": True,
                "main_rerun_prediction_byte_identical": True,
                "peak_gpu_memory_bytes": max(int(run["gpu_peak_memory_bytes"]) for run in telemetry[model]),
                "runtime_format": "cuda_fp16" if model == "qwen" else "official_mobile_qat_transformers",
                "wall_time_seconds_mean": float(np.mean([run["wall_time_seconds"] for run in telemetry[model]])),
            }
            for model in MODELS
        },
        "query_count": QUERY_COUNT,
        "schema_version": SCHEMA_VERSION,
        "source": {"bytes": SOURCE_BYTES, "sha256": SOURCE_SHA256},
        "status": "STAGE4E_GENERATOR_SELECTION_COMPLETE_PENDING_INDEPENDENT_VERIFICATION",
    }
    if args.summary.read_bytes() != render_json(expected_summary):
        raise ValueError("Summary differs from independent reconstruction")
    verification = {
        "artifact_identities": {
            "scores": {"bytes": args.scores.stat().st_size, "sha256": sha256_file(args.scores)},
            "summary": {"bytes": args.summary.stat().st_size, "sha256": sha256_file(args.summary)},
        },
        "query_count": QUERY_COUNT,
        "schema_version": SCHEMA_VERSION,
        "selected_model": winner,
        "status": "STAGE4E_GENERATOR_SELECTION_VERIFIED",
    }
    if args.verification_output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.verification_output}")
    args.verification_output.write_bytes(render_json(verification))
    print(f"STAGE4E_GENERATOR_SELECTION_VERIFIED winner={winner}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--blind", type=Path, required=True)
    parser.add_argument("--gold", type=Path, required=True)
    for model in MODELS:
        for run_id in ("main", "rerun"):
            parser.add_argument(f"--{model}-{run_id}", type=Path, required=True)
            parser.add_argument(f"--{model}-audit-{run_id}", type=Path, required=True)
            parser.add_argument(f"--{model}-telemetry-{run_id}", type=Path, required=True)
    parser.add_argument("--scores", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--verification-output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    verify(parse_args())
