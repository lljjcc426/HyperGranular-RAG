"""Frozen Stage4E generator-selection development experiment.

The Gold-bearing source is split before generation.  ``run`` receives only the
blind question/context channel; ``evaluate`` opens Gold only after both models'
main/rerun prediction and audit artifacts are byte-identical.
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from stage4e_e2e_common import (
    file_identity,
    normalize_sentence,
    render_json,
    render_jsonl,
    sha256_bytes,
    sha256_file,
    write_new_files_atomically,
)


SCHEMA_VERSION = "stage4e_generator_selection_v1"
DATASET = "hotpotqa"
SOURCE_BYTES = 1_699_596
SOURCE_SHA256 = "0818FCB2E130C3BCC207912F59F9ACE14B534321AD93686378E6923FF7405AC5"
QUERY_COUNT = 200
BOOTSTRAP_SEED = 20260722
BOOTSTRAP_ITERATIONS = 10_000
TOKEN_CAP = 4096
MAX_NEW_TOKENS = 32
SYSTEM_MESSAGE = (
    "Answer the question using only the provided evidence. "
    "Return only the shortest final answer. "
    "If the evidence is insufficient, return UNKNOWN."
)
MODEL_SPECS: dict[str, dict[str, Any]] = {
    "qwen": {
        "model_id": "Qwen/Qwen2.5-1.5B-Instruct",
        "revision": "989aa7980e4cf806f80c7fef2b1adb7bc71aa306",
        "runtime_format": "cuda_fp16",
        "files": {
            "config.json": (660, "98D2FF8CC47488D08A2B0B3ACF4EB99EF210779B42BD48605F6B8E36ACDBF670"),
            "generation_config.json": (242, "E558847A8B4402616F1273797B015104DC266FE4B520056FCA88823BA8F8EBE6"),
            "merges.txt": (1_671_839, "599BAB54075088774B1733FDE865D5BD747CBCC7A547C5BC12610E874E26F5E3"),
            "model.safetensors": (3_087_467_144, "DD924A11B4C220F385B51FFA522DAEA7C9F3D850E31B162BB5661DF483C6D3EE"),
            "tokenizer.json": (7_031_645, "C0382117EA329CDF097041132F6D735924B697924D6F6FC3945713E96CE87539"),
            "tokenizer_config.json": (7_305, "5B5D4F65D0ACD3B2D56A35B56D374A36CBC1C8FA5CF3B3FEBBBFABF22F359583"),
            "vocab.json": (2_776_833, "CA10D7E9FB3ED18575DD1E277A2579C16D108E32F27439684AFA0E10B1440910"),
        },
    },
    "gemma": {
        "model_id": "google/gemma-4-E2B-it",
        "snapshot_id": "google/gemma-4-E2B-it-qat-mobile-transformers",
        "revision": "dd693ff40353f057ca5f07e945ad867f4afbf2ec",
        "runtime_format": "official_mobile_qat_transformers",
        "files": {
            "chat_template.jinja": (18_569, "0A2C8073C878AB1DA004BEE933A998606537BBB62016310352C7285C3F01C5B5"),
            "config.json": (6_204, "CF6D7DC22738B5E6BEB364BAC833D78B869F5A6FFD57DFC96C6BE3F2ABC80424"),
            "generation_config.json": (209, "FB53F4C64E58896A63472E8EB304397DB4A39453E1DA0F5D57625EC5A8C1050E"),
            "model.safetensors": (2_458_111_846, "EFAB429012B97AB986C4D4838A46FF3AD95D618B42CE514771CA40FADC76A9A4"),
            "preprocessor_config.json": (511, "EA2AE257E901064ABDD98DCEB19F2B0DA06AF600BED15E0F99F5C85C37EE9D78"),
            "processor_config.json": (1_689, "32BDF45D2AD4CC29A0822DDD157A182DE76644F0419A6228D151495256E9813C"),
            "tokenizer.json": (32_169_626, "CC8D3A0CE36466CCC1278BF987DF5F71DB1719B9CA6B4118264F45CB627BFE0F"),
            "tokenizer_config.json": (3_082, "E1362EA24E613159D88C857B109C03D0F4E9E5134D3F6DBDC46A2A45CAA8BECF"),
        },
    },
}


def _native_string(value: Any, label: str, *, nonempty: bool = True) -> str:
    if not isinstance(value, str) or (nonempty and not value.strip()):
        raise ValueError(f"{label} must be a native non-empty string")
    return value


def _validate_source(path: Path) -> list[dict[str, Any]]:
    if not path.is_file() or path.stat().st_size != SOURCE_BYTES or sha256_file(path) != SOURCE_SHA256:
        raise ValueError("Generator-selection source identity differs")
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or len(rows) != QUERY_COUNT:
        raise ValueError("Generator-selection source must contain exactly 200 rows")
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"source[{index}] must be an object")
        sample_id = _native_string(row.get("id"), f"source[{index}].id")
        if sample_id in seen:
            raise ValueError(f"Duplicate source id: {sample_id}")
        seen.add(sample_id)
        if row.get("dataset") != DATASET:
            raise ValueError(f"source[{index}].dataset differs")
        _native_string(row.get("question"), f"source[{index}].question")
        _native_string(row.get("answer"), f"source[{index}].answer", nonempty=False)
        if not isinstance(row.get("contexts"), list) or not row["contexts"]:
            raise ValueError(f"source[{index}].contexts must be non-empty")
    return rows


def split_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    blind: list[dict[str, Any]] = []
    gold: list[dict[str, Any]] = []
    for row in rows:
        sample_id = row["id"]
        query_id = f"{DATASET}::{sample_id}"
        units: list[dict[str, str]] = []
        for context_index, context in enumerate(row["contexts"]):
            if not isinstance(context, dict):
                raise ValueError(f"{query_id} context must be an object")
            title = _native_string(context.get("title"), f"{query_id}.context.title")
            sentences = context.get("sentences")
            if not isinstance(sentences, list):
                raise ValueError(f"{query_id}.context.sentences must be a list")
            for sentence_index, raw_sentence in enumerate(sentences):
                text = normalize_sentence(raw_sentence)
                if not text:
                    continue
                units.append({
                    "text": text,
                    "title": title,
                    "unit_id": f"{sample_id}::{context_index:02d}::{sentence_index:03d}",
                })
        if not units:
            raise ValueError(f"{query_id} has no normalized evidence units")
        blind.append({
            "dataset": DATASET,
            "query_id": query_id,
            "question": row["question"],
            "sample_id": sample_id,
            "units": units,
        })
        gold.append({
            "answer": row["answer"],
            "dataset": DATASET,
            "query_id": query_id,
            "sample_id": sample_id,
        })
    return blind, gold


def prepare(source: Path, blind_output: Path, gold_output: Path) -> None:
    blind, gold = split_rows(_validate_source(source))
    write_new_files_atomically([
        (blind_output, render_jsonl(blind)),
        (gold_output, render_jsonl(gold)),
    ])
    print(f"STAGE4E_GENERATOR_SELECTION_CHANNELS_PREPARED queries={len(blind)}")


def _validate_snapshot(snapshot: Path, model_key: str) -> dict[str, Any]:
    spec = MODEL_SPECS[model_key]
    if snapshot.name != spec["revision"]:
        raise ValueError(f"{model_key} snapshot revision path differs")
    for relative, (expected_bytes, expected_sha) in spec["files"].items():
        path = snapshot / relative
        if not path.is_file() or path.stat().st_size != expected_bytes or sha256_file(path) != expected_sha:
            raise ValueError(f"{model_key} snapshot file differs: {relative}")
    return spec


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.endswith("\n"):
                raise ValueError(f"{path} line {line_number} lacks LF terminator")
            rows.append(json.loads(line))
    return rows


def _load_blind(path: Path) -> list[dict[str, Any]]:
    rows = _load_jsonl(path)
    if len(rows) != QUERY_COUNT:
        raise ValueError("Blind channel must contain exactly 200 rows")
    expected_keys = {"dataset", "query_id", "question", "sample_id", "units"}
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if set(row) != expected_keys:
            raise ValueError(f"blind[{index}] key contract differs")
        sample_id = _native_string(row["sample_id"], f"blind[{index}].sample_id")
        query_id = _native_string(row["query_id"], f"blind[{index}].query_id")
        if row["dataset"] != DATASET or query_id != f"{DATASET}::{sample_id}" or query_id in seen:
            raise ValueError(f"blind[{index}] identity contract differs")
        seen.add(query_id)
        _native_string(row["question"], f"blind[{index}].question")
        if not isinstance(row["units"], list) or not row["units"]:
            raise ValueError(f"blind[{index}].units must be non-empty")
        for unit_index, unit in enumerate(row["units"]):
            if not isinstance(unit, dict) or set(unit) != {"text", "title", "unit_id"}:
                raise ValueError(f"blind[{index}].units[{unit_index}] contract differs")
            for key in ("text", "title", "unit_id"):
                _native_string(unit[key], f"blind[{index}].units[{unit_index}].{key}")
    return rows


def _set_determinism() -> None:
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    os.environ["PYTHONHASHSEED"] = "0"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    import torch

    torch.manual_seed(0)
    torch.cuda.manual_seed_all(0)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False


def _messages(question: str, evidence_lines: Iterable[str]) -> list[dict[str, str]]:
    evidence = "\n".join(evidence_lines)
    return [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": f"Evidence:\n{evidence}\n\nQuestion: {question}\nFinal answer:"},
    ]


class GeneratorAdapter:
    def __init__(self, model_key: str, snapshot: Path):
        _set_determinism()
        import torch

        self.model_key = model_key
        self.spec = _validate_snapshot(snapshot, model_key)
        if model_key == "qwen":
            from transformers import AutoModelForCausalLM, AutoTokenizer

            self.frontend = AutoTokenizer.from_pretrained(snapshot, local_files_only=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                snapshot, local_files_only=True, dtype=torch.float16,
            ).eval().to("cuda")
        elif model_key == "gemma":
            from transformers import AutoModelForMultimodalLM, AutoProcessor

            self.frontend = AutoProcessor.from_pretrained(snapshot, local_files_only=True)
            self.model = AutoModelForMultimodalLM.from_pretrained(
                snapshot, local_files_only=True, device_map={"": 0},
            ).eval()
        else:
            raise ValueError(f"Unknown model: {model_key}")
        devices = {str(parameter.device) for parameter in self.model.parameters()}
        if devices != {"cuda:0"}:
            raise RuntimeError(f"{model_key} must run entirely on cuda:0, got {sorted(devices)}")
        self.tokenizer = getattr(self.frontend, "tokenizer", self.frontend)

    def _template(self, messages: list[dict[str, str]], *, tokenize: bool) -> Any:
        kwargs: dict[str, Any] = {
            "tokenize": tokenize,
            "add_generation_prompt": True,
        }
        if self.model_key == "gemma":
            kwargs["enable_thinking"] = False
            if tokenize:
                kwargs.update(return_dict=True, return_tensors="pt")
        return self.frontend.apply_chat_template(messages, **kwargs)

    def token_ids(self, messages: list[dict[str, str]]) -> list[int]:
        rendered = self._template(messages, tokenize=True)
        if self.model_key == "gemma":
            return [int(value) for value in rendered["input_ids"][0].tolist()]
        if rendered and isinstance(rendered[0], list):
            rendered = rendered[0]
        return [int(value) for value in rendered]

    def prompt_text(self, messages: list[dict[str, str]]) -> str:
        value = self._template(messages, tokenize=False)
        if not isinstance(value, str):
            raise TypeError("Chat template text must be a string")
        return value

    def encode_line(self, line: str) -> list[int]:
        return [int(value) for value in self.tokenizer.encode(line, add_special_tokens=False)]

    def decode_line(self, token_ids: list[int]) -> str:
        return self.tokenizer.decode(
            token_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False,
        )

    def generate(self, messages: list[dict[str, str]]) -> tuple[str, list[int]]:
        import torch

        if self.model_key == "gemma":
            inputs = self._template(messages, tokenize=True).to("cuda")
            input_len = int(inputs["input_ids"].shape[-1])
            with torch.inference_mode():
                output = self.model.generate(
                    **inputs,
                    do_sample=False,
                    num_beams=1,
                    max_new_tokens=MAX_NEW_TOKENS,
                    use_cache=True,
                )
            completion_ids = [int(value) for value in output[0, input_len:].tolist()]
            completion = self.frontend.decode(completion_ids, skip_special_tokens=True).strip()
        else:
            input_ids = torch.tensor([self.token_ids(messages)], dtype=torch.long, device="cuda")
            attention_mask = torch.ones_like(input_ids)
            with torch.inference_mode():
                output = self.model.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    do_sample=False,
                    num_beams=1,
                    max_new_tokens=MAX_NEW_TOKENS,
                    pad_token_id=self.tokenizer.eos_token_id,
                    use_cache=True,
                )
            completion_ids = [int(value) for value in output[0, input_ids.shape[1]:].tolist()]
            completion = self.tokenizer.decode(completion_ids, skip_special_tokens=True).strip()
        return completion, completion_ids


def build_prompt(adapter: GeneratorAdapter, question: str, units: list[dict[str, str]]) -> dict[str, Any]:
    base_ids = adapter.token_ids(_messages(question, []))
    if len(base_ids) > TOKEN_CAP:
        raise ValueError("Question and template alone exceed token cap")
    lines: list[str] = []
    included: list[str] = []
    rank1_truncated = False
    for rank, unit in enumerate(units, start=1):
        line = f"[{rank}] {unit['title']}: {unit['text']}"
        candidate = lines + [line]
        if len(adapter.token_ids(_messages(question, candidate))) <= TOKEN_CAP:
            lines = candidate
            included.append(unit["unit_id"])
            continue
        if rank > 1:
            break
        line_tokens = adapter.encode_line(line)
        while line_tokens:
            shortened = adapter.decode_line(line_tokens)
            if len(adapter.token_ids(_messages(question, [shortened]))) <= TOKEN_CAP:
                lines = [shortened]
                included = [unit["unit_id"]]
                rank1_truncated = True
                break
            line_tokens.pop()
        if not lines:
            raise ValueError("Rank-1 evidence cannot fit within token cap")
        break
    messages = _messages(question, lines)
    input_token_count = len(adapter.token_ids(messages))
    if input_token_count > TOKEN_CAP:
        raise AssertionError("Prompt cap enforcement failed")
    return {
        "evidence_unit_ids": included,
        "input_token_count": input_token_count,
        "messages": messages,
        "prompt_sha256": sha256_bytes(adapter.prompt_text(messages).encode("utf-8")),
        "rank1_truncated": rank1_truncated,
    }


def run_model(
    blind_path: Path,
    snapshot: Path,
    model_key: str,
    run_id: str,
    predictions_output: Path,
    audit_output: Path,
    telemetry_output: Path,
) -> None:
    if run_id not in {"main", "rerun"}:
        raise ValueError("run-id must be main or rerun")
    rows = _load_blind(blind_path)
    import torch
    import transformers

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    adapter = GeneratorAdapter(model_key, snapshot)
    predictions: list[dict[str, Any]] = []
    audits: list[dict[str, Any]] = []
    output_token_count = 0
    started = time.perf_counter()
    for index, row in enumerate(rows, start=1):
        prompt = build_prompt(adapter, row["question"], row["units"])
        completion, completion_ids = adapter.generate(prompt["messages"])
        output_token_count += len(completion_ids)
        predictions.append({
            "dataset": DATASET,
            "model": model_key,
            "prediction": completion,
            "query_id": row["query_id"],
            "sample_id": row["sample_id"],
        })
        audits.append({
            "completion_token_ids": completion_ids,
            "dataset": DATASET,
            "evidence_unit_ids": prompt["evidence_unit_ids"],
            "input_token_count": prompt["input_token_count"],
            "model": model_key,
            "prompt_sha256": prompt["prompt_sha256"],
            "query_id": row["query_id"],
            "rank1_truncated": prompt["rank1_truncated"],
            "sample_id": row["sample_id"],
        })
        if index % 10 == 0:
            print(f"{model_key} {run_id}: {index}/{QUERY_COUNT}", file=sys.stderr, flush=True)
    wall_time = time.perf_counter() - started
    telemetry = {
        "cuda_devices": sorted({str(parameter.device) for parameter in adapter.model.parameters()}),
        "failed_calls": 0,
        "generation_calls": len(predictions),
        "gpu_peak_memory_bytes": int(torch.cuda.max_memory_allocated()),
        "model": model_key,
        "model_id": adapter.spec["model_id"],
        "output_token_count": output_token_count,
        "python": sys.version.split()[0],
        "run_id": run_id,
        "runtime_format": adapter.spec["runtime_format"],
        "schema_version": SCHEMA_VERSION,
        "snapshot": file_identity(snapshot / "model.safetensors"),
        "torch": torch.__version__,
        "torchvision": __import__("torchvision").__version__,
        "transformers": transformers.__version__,
        "wall_time_seconds": wall_time,
    }
    del adapter
    gc.collect()
    torch.cuda.empty_cache()
    write_new_files_atomically([
        (predictions_output, render_jsonl(predictions)),
        (audit_output, render_jsonl(audits)),
        (telemetry_output, render_json(telemetry)),
    ])
    print(f"STAGE4E_GENERATOR_SELECTION_RUN_COMPLETE model={model_key} run={run_id}")


def normalize_answer(value: str) -> str:
    import re
    import string

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
    num_same = sum(common.values())
    if num_same == 0:
        return em, 0.0
    precision = num_same / len(prediction_tokens)
    recall = num_same / len(ground_truth_tokens)
    return em, 2 * precision * recall / (precision + recall)


def paired_bootstrap(qwen: np.ndarray, gemma: np.ndarray) -> dict[str, float]:
    if qwen.shape != (QUERY_COUNT,) or gemma.shape != (QUERY_COUNT,):
        raise ValueError("Bootstrap arrays must contain 200 values")
    delta = np.asarray(gemma - qwen, dtype="float64")
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


def _prediction_map(path: Path, model_key: str) -> dict[str, dict[str, Any]]:
    rows = _load_jsonl(path)
    expected = {"dataset", "model", "prediction", "query_id", "sample_id"}
    if len(rows) != QUERY_COUNT:
        raise ValueError(f"{model_key} predictions must contain 200 rows")
    result: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if set(row) != expected or row["dataset"] != DATASET or row["model"] != model_key:
            raise ValueError(f"{model_key} predictions[{index}] contract differs")
        sample_id = _native_string(row["sample_id"], f"predictions[{index}].sample_id")
        query_id = _native_string(row["query_id"], f"predictions[{index}].query_id")
        if query_id != f"{DATASET}::{sample_id}" or query_id in result:
            raise ValueError(f"{model_key} predictions[{index}] identity differs")
        if not isinstance(row["prediction"], str):
            raise ValueError(f"{model_key} predictions[{index}].prediction must be a string")
        result[query_id] = row
    return result


def _load_telemetry(path: Path, model_key: str, run_id: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        value.get("model") != model_key
        or value.get("run_id") != run_id
        or value.get("generation_calls") != QUERY_COUNT
        or value.get("failed_calls") != 0
        or value.get("cuda_devices") != ["cuda:0"]
    ):
        raise ValueError(f"{model_key} {run_id} telemetry feasibility contract differs")
    for key in ("wall_time_seconds", "gpu_peak_memory_bytes", "output_token_count"):
        if isinstance(value.get(key), bool) or not isinstance(value.get(key), (int, float)):
            raise ValueError(f"{model_key} {run_id} telemetry.{key} must be numeric")
        if not math.isfinite(float(value[key])) or float(value[key]) < 0:
            raise ValueError(f"{model_key} {run_id} telemetry.{key} must be finite/non-negative")
    return value


def _winner(
    qwen_f1: float,
    gemma_f1: float,
    qwen_em: float,
    gemma_em: float,
    telemetry: dict[str, list[dict[str, Any]]],
) -> tuple[str, str]:
    delta_f1 = gemma_f1 - qwen_f1
    if abs(delta_f1) >= 0.010:
        return ("gemma" if delta_f1 > 0 else "qwen", "PRIMARY_F1_DIFFERENCE_AT_LEAST_0_010")
    delta_em = gemma_em - qwen_em
    if abs(delta_em) >= 0.010:
        return ("gemma" if delta_em > 0 else "qwen", "SECONDARY_EM_DIFFERENCE_AT_LEAST_0_010")
    times = {
        model: float(np.mean([run["wall_time_seconds"] for run in runs]))
        for model, runs in telemetry.items()
    }
    relative = abs(times["gemma"] - times["qwen"]) / max(times.values())
    if relative >= 0.01:
        return (min(times, key=times.get), "WALL_TIME_TIEBREAKER")
    peaks = {
        model: max(int(run["gpu_peak_memory_bytes"]) for run in runs)
        for model, runs in telemetry.items()
    }
    return (min(peaks, key=peaks.get), "PEAK_GPU_MEMORY_TIEBREAKER")


def evaluate(
    gold_path: Path,
    qwen_main: Path,
    qwen_rerun: Path,
    gemma_main: Path,
    gemma_rerun: Path,
    qwen_audit_main: Path,
    qwen_audit_rerun: Path,
    gemma_audit_main: Path,
    gemma_audit_rerun: Path,
    telemetry_paths: dict[str, tuple[Path, Path]],
    scores_output: Path,
    summary_output: Path,
) -> None:
    pairs = (
        (qwen_main, qwen_rerun, "qwen predictions"),
        (gemma_main, gemma_rerun, "gemma predictions"),
        (qwen_audit_main, qwen_audit_rerun, "qwen audits"),
        (gemma_audit_main, gemma_audit_rerun, "gemma audits"),
    )
    for main, rerun, label in pairs:
        if main.read_bytes() != rerun.read_bytes():
            raise ValueError(f"{label} main/rerun bytes differ")
    predictions = {
        "qwen": _prediction_map(qwen_main, "qwen"),
        "gemma": _prediction_map(gemma_main, "gemma"),
    }
    gold_rows = _load_jsonl(gold_path)
    if len(gold_rows) != QUERY_COUNT:
        raise ValueError("Gold channel must contain 200 rows")
    score_rows: list[dict[str, Any]] = []
    values = {model: {"f1": [], "em": []} for model in MODEL_SPECS}
    for index, gold in enumerate(gold_rows):
        if set(gold) != {"answer", "dataset", "query_id", "sample_id"}:
            raise ValueError(f"gold[{index}] key contract differs")
        query_id = _native_string(gold["query_id"], f"gold[{index}].query_id")
        if gold["dataset"] != DATASET or query_id != f"{DATASET}::{gold['sample_id']}":
            raise ValueError(f"gold[{index}] identity differs")
        row: dict[str, Any] = {"query_id": query_id, "sample_id": gold["sample_id"]}
        for model_key in MODEL_SPECS:
            prediction = predictions[model_key].get(query_id)
            if prediction is None:
                raise ValueError(f"Missing {model_key} prediction for {query_id}")
            em, f1 = answer_scores(prediction["prediction"], gold["answer"])
            values[model_key]["f1"].append(f1)
            values[model_key]["em"].append(em)
            row[model_key] = {"answer_em": em, "answer_f1": f1, "prediction": prediction["prediction"]}
        score_rows.append(row)
    telemetry = {
        model: [
            _load_telemetry(paths[0], model, "main"),
            _load_telemetry(paths[1], model, "rerun"),
        ]
        for model, paths in telemetry_paths.items()
    }
    arrays = {
        model: {
            metric: np.asarray(metric_values, dtype="float64")
            for metric, metric_values in metrics.items()
        }
        for model, metrics in values.items()
    }
    means = {
        model: {metric: float(np.mean(metric_values)) for metric, metric_values in metrics.items()}
        for model, metrics in arrays.items()
    }
    winner, reason = _winner(
        means["qwen"]["f1"], means["gemma"]["f1"],
        means["qwen"]["em"], means["gemma"]["em"], telemetry,
    )
    summary = {
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
                "runtime_format": MODEL_SPECS[model]["runtime_format"],
                "wall_time_seconds_mean": float(np.mean([run["wall_time_seconds"] for run in telemetry[model]])),
            }
            for model in MODEL_SPECS
        },
        "query_count": QUERY_COUNT,
        "schema_version": SCHEMA_VERSION,
        "source": {"bytes": SOURCE_BYTES, "sha256": SOURCE_SHA256},
        "status": "STAGE4E_GENERATOR_SELECTION_COMPLETE_PENDING_INDEPENDENT_VERIFICATION",
    }
    write_new_files_atomically([
        (scores_output, render_jsonl(score_rows)),
        (summary_output, render_json(summary)),
    ])
    print(f"STAGE4E_GENERATOR_SELECTION_EVALUATED winner={winner} reason={reason}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--source", type=Path, required=True)
    prepare_parser.add_argument("--blind-output", type=Path, required=True)
    prepare_parser.add_argument("--gold-output", type=Path, required=True)
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--blind", type=Path, required=True)
    run_parser.add_argument("--snapshot", type=Path, required=True)
    run_parser.add_argument("--model", choices=sorted(MODEL_SPECS), required=True)
    run_parser.add_argument("--run-id", choices=("main", "rerun"), required=True)
    run_parser.add_argument("--predictions-output", type=Path, required=True)
    run_parser.add_argument("--audit-output", type=Path, required=True)
    run_parser.add_argument("--telemetry-output", type=Path, required=True)
    evaluate_parser = subparsers.add_parser("evaluate")
    evaluate_parser.add_argument("--gold", type=Path, required=True)
    for model in ("qwen", "gemma"):
        for run_id in ("main", "rerun"):
            evaluate_parser.add_argument(f"--{model}-{run_id}", type=Path, required=True)
            evaluate_parser.add_argument(f"--{model}-audit-{run_id}", type=Path, required=True)
            evaluate_parser.add_argument(f"--{model}-telemetry-{run_id}", type=Path, required=True)
    evaluate_parser.add_argument("--scores-output", type=Path, required=True)
    evaluate_parser.add_argument("--summary-output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "prepare":
        prepare(args.source, args.blind_output, args.gold_output)
    elif args.command == "run":
        run_model(
            args.blind, args.snapshot, args.model, args.run_id,
            args.predictions_output, args.audit_output, args.telemetry_output,
        )
    elif args.command == "evaluate":
        evaluate(
            args.gold,
            args.qwen_main, args.qwen_rerun, args.gemma_main, args.gemma_rerun,
            args.qwen_audit_main, args.qwen_audit_rerun,
            args.gemma_audit_main, args.gemma_audit_rerun,
            {
                "qwen": (args.qwen_telemetry_main, args.qwen_telemetry_rerun),
                "gemma": (args.gemma_telemetry_main, args.gemma_telemetry_rerun),
            },
            args.scores_output, args.summary_output,
        )
    else:
        raise AssertionError("Unreachable command")


if __name__ == "__main__":
    main()
