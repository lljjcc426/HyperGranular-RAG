"""Audit the exact Stage4E CUDA environment with synthetic-only reruns."""

from __future__ import annotations

import argparse
import gc
import importlib.metadata
import os
import platform
import sys
from pathlib import Path
from typing import Any

import numpy as np

from stage4e_e2e_common import SCHEMA_VERSION, render_json, sha256_bytes, write_new_files_atomically
from stage4e_e2e_goldfree_runner import embed_texts


REQUIRED_ENVIRONMENT = {
    "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "PYTHONHASHSEED": "0",
    "TOKENIZERS_PARALLELISM": "false",
}
PACKAGE_NAMES = (
    "accelerate",
    "filelock",
    "fsspec",
    "huggingface-hub",
    "jinja2",
    "markupsafe",
    "mpmath",
    "networkx",
    "numpy",
    "packaging",
    "psutil",
    "pyyaml",
    "regex",
    "requests",
    "safetensors",
    "setuptools",
    "sympy",
    "tokenizers",
    "torch",
    "tqdm",
    "transformers",
    "typing-extensions",
)


def _package_versions() -> dict[str, str]:
    result: dict[str, str] = {}
    for name in PACKAGE_NAMES:
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError as exc:
            raise RuntimeError(f"Required Stage4E package is absent: {name}") from exc
    return result


def _generator_synthetic_rerun(snapshot: Path) -> dict[str, Any]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(snapshot, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        snapshot, local_files_only=True, dtype=torch.float16
    )
    model.eval().to("cuda")
    messages = [
        {"role": "system", "content": "Return only the requested token."},
        {"role": "user", "content": "Return only: OK"},
    ]
    prompt_ids = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True
    )
    if hasattr(prompt_ids, "keys") and "input_ids" in prompt_ids:
        prompt_ids = prompt_ids["input_ids"]
    prompt = torch.tensor([prompt_ids], dtype=torch.long, device="cuda")
    attention_mask = torch.ones_like(prompt)
    outputs: list[bytes] = []
    with torch.no_grad():
        for _ in range(2):
            result = model.generate(
                input_ids=prompt,
                attention_mask=attention_mask,
                do_sample=False,
                num_beams=1,
                max_new_tokens=8,
                pad_token_id=tokenizer.eos_token_id,
            )
            tokens = result[0, prompt.shape[1] :].detach().cpu().numpy().astype("int64")
            outputs.append(tokens.tobytes())
    del model, tokenizer, prompt, attention_mask
    gc.collect()
    torch.cuda.empty_cache()
    if outputs[0] != outputs[1]:
        raise RuntimeError("Synthetic generator rerun is not token-identical")
    return {
        "completion_token_bytes_sha256": sha256_bytes(outputs[0]),
        "rerun_token_identical": True,
    }


def audit(encoder_snapshot: Path, generator_snapshot: Path) -> dict[str, Any]:
    for name, expected in REQUIRED_ENVIRONMENT.items():
        if os.environ.get(name) != expected:
            raise RuntimeError(f"Frozen environment variable differs: {name}")
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable in the Stage4E environment")
    torch.manual_seed(0)
    torch.cuda.manual_seed_all(0)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False

    texts = ["Synthetic encoder sentence one.", "Synthetic encoder sentence two."]
    encoder_first = embed_texts(texts, encoder_snapshot, 2, 192)
    encoder_second = embed_texts(texts, encoder_snapshot, 2, 192)
    if encoder_first.dtype != np.float32 or encoder_first.tobytes() != encoder_second.tobytes():
        raise RuntimeError("Synthetic encoder rerun is not byte-identical float32")
    generator = _generator_synthetic_rerun(generator_snapshot)
    properties = torch.cuda.get_device_properties(0)
    return {
        "determinism": {
            "encoder_embedding_sha256": sha256_bytes(encoder_first.tobytes()),
            "encoder_rerun_byte_identical": True,
            **generator,
            "torch_deterministic_algorithms": True,
        },
        "environment_variables": REQUIRED_ENVIRONMENT,
        "gpu": {
            "name": torch.cuda.get_device_name(0),
            "total_memory_bytes": int(properties.total_memory),
        },
        "packages": _package_versions(),
        "python": {
            "executable": sys.executable,
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
        },
        "runtime": {
            "cuda": torch.version.cuda,
            "cudnn": int(torch.backends.cudnn.version()),
            "platform": platform.platform(),
            "torch": torch.__version__,
        },
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4E_SYNTHETIC_CUDA_ENVIRONMENT_VERIFIED_NO_OFFICIAL_DATA",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--encoder-snapshot", required=True, type=Path)
    parser.add_argument("--generator-snapshot", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = audit(args.encoder_snapshot, args.generator_snapshot)
    write_new_files_atomically(((args.output, render_json(result)),))
    print(result["status"])


if __name__ == "__main__":
    main()
