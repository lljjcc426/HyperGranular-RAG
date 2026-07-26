"""Gold-only development selection and confirmation statistics for Stage6A."""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from stage5a_bnh_evaluate import evaluate_answer_rows
from stage6a_smc_common import (
    BALL_FAMILY,
    BASELINE_METHOD,
    BOOTSTRAP_ITERATIONS,
    BOOTSTRAP_SEED,
    DATASETS,
    GENERIC_FAMILIES,
    HGRAG_FAMILY,
    NON_BALL_FAMILIES,
    TWOWIKI_DATASET,
    assert_bound,
    assert_implementation_binding,
    development_methods,
    family_from_method,
    load_json,
    load_jsonl,
    parse_method,
    path_from_config,
    render_json,
    render_jsonl,
    validate_authorization,
    validate_confirmation_methods,
    write_new_files_atomically,
)


def _require_pregold(config: dict[str, Any], boundary: str) -> None:
    value = load_json(path_from_config(config, f"{boundary}_pregold_verification"))
    expected = f"STAGE6A_{boundary.upper()}_PRE_GOLD_VERIFICATION_PASS"
    if not isinstance(value, dict) or value.get("status") != expected:
        raise PermissionError(f"{boundary} pre-Gold verification is absent")


def _dataset_rows(
    audits: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    output = {
        dataset: [row for row in audits if row["dataset"] == dataset]
        for dataset in DATASETS
    }
    if any(not rows for rows in output.values()):
        raise ValueError("Stage6A dataset rows are incomplete")
    return output


def _method_summary(
    audits: list[dict[str, Any]], method: str
) -> dict[str, Any]:
    by_dataset = _dataset_rows(audits)
    datasets: dict[str, Any] = {}
    for dataset, rows in by_dataset.items():
        f1 = np.asarray(
            [row["methods"][method]["answer_f1"] for row in rows],
            dtype="float64",
        )
        em = np.asarray(
            [row["methods"][method]["answer_em"] for row in rows],
            dtype="float64",
        )
        tokens = np.asarray(
            [row["methods"][method]["input_token_count"] for row in rows],
            dtype="float64",
        )
        baseline_f1 = np.asarray(
            [row["methods"][BASELINE_METHOD]["answer_f1"] for row in rows],
            dtype="float64",
        )
        baseline_em = np.asarray(
            [row["methods"][BASELINE_METHOD]["answer_em"] for row in rows],
            dtype="float64",
        )
        delta = f1 - baseline_f1
        datasets[dataset] = {
            "answer_em": float(np.mean(em)),
            "answer_f1": float(np.mean(f1)),
            "delta_answer_em": float(np.mean(em - baseline_em)),
            "delta_answer_f1": float(np.mean(delta)),
            "gain_queries": int(np.sum(delta > 0)),
            "harm_queries": int(np.sum(delta < 0)),
            "input_tokens": float(np.mean(tokens)),
            "queries": len(rows),
            "same_queries": int(np.sum(delta == 0)),
        }
    return {
        "dataset_equal_weight": {
            key: float(np.mean([datasets[value][key] for value in DATASETS]))
            for key in (
                "answer_em",
                "answer_f1",
                "delta_answer_em",
                "delta_answer_f1",
                "input_tokens",
            )
        },
        "datasets": datasets,
    }


def _eligible(summary: dict[str, Any]) -> bool:
    f1_deltas = [
        summary["datasets"][dataset]["delta_answer_f1"] for dataset in DATASETS
    ]
    opposite = min(f1_deltas) < 0.0 < max(f1_deltas)
    return (
        not opposite
        and summary["dataset_equal_weight"]["delta_answer_em"] >= -0.010
    )


def _selection_key(method: str, summary: dict[str, Any]) -> tuple[Any, ...]:
    family, lambda_value, leaf_target = parse_method(method)
    return (
        -(lambda_value or 0.0),
        -(leaf_target or 0),
        method,
    )


def _best(
    methods: list[str], summaries: dict[str, Any], label: str
) -> str:
    eligible = [method for method in methods if _eligible(summaries[method])]
    if not eligible:
        raise RuntimeError(f"{label}: no eligible development configuration")
    maximum = max(
        summaries[method]["dataset_equal_weight"]["answer_f1"]
        for method in eligible
    )
    near = [
        method
        for method in eligible
        if maximum
        - summaries[method]["dataset_equal_weight"]["answer_f1"]
        <= 0.002
    ]
    return min(near, key=lambda method: _selection_key(method, summaries[method]))


def run_development(config: dict[str, Any]) -> None:
    _require_pregold(config, "development")
    methods = development_methods()
    gold = load_jsonl(assert_bound(config, "development_gold"))
    predictions = load_jsonl(
        path_from_config(config, "development_main_predictions")
    )
    prompts = load_jsonl(path_from_config(config, "development_main_prompt_audit"))
    rankings = load_jsonl(path_from_config(config, "development_main_rankings"))
    audits = evaluate_answer_rows(gold, predictions, prompts, rankings, methods)
    summaries = {method: _method_summary(audits, method) for method in methods}

    generic = _best(
        [
            method
            for method in methods
            if family_from_method(method) in GENERIC_FAMILIES
        ],
        summaries,
        "generic selector",
    )
    non_ball = _best(
        [
            method
            for method in methods
            if family_from_method(method) in NON_BALL_FAMILIES
        ],
        summaries,
        "non-ball structure",
    )
    ball = _best(
        [
            method
            for method in methods
            if family_from_method(method) == BALL_FAMILY
        ],
        summaries,
        "granular-ball no-hyperedge",
    )
    hgrag = _best(
        [
            method
            for method in methods
            if family_from_method(method) == HGRAG_FAMILY
        ],
        summaries,
        "HGRAG joint",
    )
    confirmation_methods = [BASELINE_METHOD, generic, non_ball, ball, hgrag]
    lock = {
        "confirmation_methods": confirmation_methods,
        "development_only": True,
        "selection_order": [
            "QWEN3_RERANK_TOP20",
            "BEST_GENERIC_SELECTOR",
            "BEST_NON_BALL_STRUCTURE",
            "BEST_GRANULAR_BALL_NO_HYPEREDGE",
            "BEST_HGRAG_JOINT",
        ],
        "status": "STAGE6A_DEVELOPMENT_SELECTION_LOCKED_FOR_CONFIRMATION",
    }
    summary = {
        "confirmation_methods": confirmation_methods,
        "methods": summaries,
        "primary_endpoint": "dataset_equal_weight_answer_f1",
        "query_scores_path": str(
            path_from_config(config, "development_query_scores")
        ),
        "status": "STAGE6A_DEVELOPMENT_GOLD_EVALUATION_COMPLETE",
    }
    write_new_files_atomically(
        [
            (
                path_from_config(config, "development_query_scores"),
                render_jsonl(audits),
            ),
            (
                path_from_config(config, "development_evaluation_summary"),
                render_json(summary),
            ),
            (
                path_from_config(config, "development_selection_lock"),
                render_json(lock),
            ),
        ]
    )
    print(
        "STAGE6A_DEVELOPMENT_SELECTION_LOCKED_FOR_CONFIRMATION "
        + " ".join(confirmation_methods)
    )


def _gold_membership(gold: dict[str, Any], ranking: list[str]) -> tuple[int, int]:
    if "supporting_unit_ids" in gold:
        targets = set(gold["supporting_unit_ids"])
        found = targets & set(ranking)
        return len(found), len(targets)
    paragraphs = set(gold.get("supporting_paragraph_indices", []))
    found: set[int] = set()
    for unit_id in ranking:
        match = re.search(r"::p([0-9]+)::s[0-9]+$", unit_id)
        if match is not None and int(match.group(1)) in paragraphs:
            found.add(int(match.group(1)))
    return len(found), len(paragraphs)


def _augment_retrieval_scores(
    audits: list[dict[str, Any]],
    gold_rows: list[dict[str, Any]],
    rankings: list[dict[str, Any]],
    methods: tuple[str, ...],
) -> None:
    gold_by_id = {row["query_id"]: row for row in gold_rows}
    ranking_by_id = {row["query_id"]: row for row in rankings}
    for audit in audits:
        gold = gold_by_id[audit["query_id"]]
        row = ranking_by_id[audit["query_id"]]
        for method in methods:
            found, total = _gold_membership(gold, row["methods"][method])
            audit["methods"][method]["complete_recall_at_20"] = float(
                total > 0 and found == total
            )
            audit["methods"][method]["evidence_recall_at_20"] = found / max(
                1, total
            )


def _bootstrap(
    audits: list[dict[str, Any]], left: str, right: str, metric: str
) -> dict[str, Any]:
    rng = np.random.Generator(np.random.PCG64(BOOTSTRAP_SEED))
    datasets = {}
    samples_by_dataset = []
    for dataset in DATASETS:
        rows = [row for row in audits if row["dataset"] == dataset]
        deltas = np.asarray(
            [
                row["methods"][left][metric] - row["methods"][right][metric]
                for row in rows
            ],
            dtype="float64",
        )
        indices = rng.integers(
            0, len(deltas), size=(BOOTSTRAP_ITERATIONS, len(deltas))
        )
        samples = np.mean(deltas[indices], axis=1)
        samples_by_dataset.append(samples)
        datasets[dataset] = {
            "ci95": [
                float(np.percentile(samples, 2.5, method="linear")),
                float(np.percentile(samples, 97.5, method="linear")),
            ],
            "point": float(np.mean(deltas)),
            "queries": len(rows),
        }
    combined_samples = np.mean(np.stack(samples_by_dataset, axis=1), axis=1)
    point = float(np.mean([datasets[value]["point"] for value in DATASETS]))
    return {
        "ci95": [
            float(np.percentile(combined_samples, 2.5, method="linear")),
            float(np.percentile(combined_samples, 97.5, method="linear")),
        ],
        "datasets": datasets,
        "one_sided_p_nonpositive": float(
            (1 + np.sum(combined_samples <= 0.0))
            / (BOOTSTRAP_ITERATIONS + 1)
        ),
        "point": point,
    }


def _holm(p_values: list[float]) -> list[float]:
    order = sorted(range(len(p_values)), key=lambda index: p_values[index])
    adjusted = [0.0] * len(p_values)
    running = 0.0
    count = len(p_values)
    for rank, index in enumerate(order):
        running = max(running, min(1.0, (count - rank) * p_values[index]))
        adjusted[index] = running
    return adjusted


def _summary_for_method(
    audits: list[dict[str, Any]], method: str
) -> dict[str, Any]:
    by_dataset = _dataset_rows(audits)
    datasets = {}
    for dataset, rows in by_dataset.items():
        datasets[dataset] = {
            key: float(np.mean([row["methods"][method][key] for row in rows]))
            for key in (
                "answer_em",
                "answer_f1",
                "complete_recall_at_20",
                "evidence_recall_at_20",
                "input_token_count",
                "unknown",
            )
        }
    return {
        "dataset_equal_weight": {
            key: float(np.mean([datasets[value][key] for value in DATASETS]))
            for key in next(iter(datasets.values()))
        },
        "datasets": datasets,
    }


def run_confirmation(config: dict[str, Any]) -> None:
    _require_pregold(config, "confirmation")
    lock = load_json(path_from_config(config, "development_selection_lock"))
    if not isinstance(lock, dict):
        raise ValueError("development selection lock differs")
    methods = validate_confirmation_methods(lock.get("confirmation_methods"))
    gold = load_jsonl(assert_bound(config, "confirmation_gold"))
    predictions = load_jsonl(
        path_from_config(config, "confirmation_main_predictions")
    )
    prompts = load_jsonl(path_from_config(config, "confirmation_main_prompt_audit"))
    rankings = load_jsonl(path_from_config(config, "confirmation_main_rankings"))
    audits = evaluate_answer_rows(gold, predictions, prompts, rankings, methods)
    _augment_retrieval_scores(audits, gold, rankings, methods)
    hgrag = methods[4]
    primary_right = (methods[0], methods[1], methods[2])
    f1_contrasts = [
        _bootstrap(audits, hgrag, right, "answer_f1")
        for right in primary_right
    ]
    adjusted = _holm(
        [row["one_sided_p_nonpositive"] for row in f1_contrasts]
    )
    em_contrasts = [
        _bootstrap(audits, hgrag, right, "answer_em")
        for right in primary_right
    ]
    contrast_rows = {}
    for right, f1, em, p_adjusted in zip(
        primary_right, f1_contrasts, em_contrasts, adjusted, strict=True
    ):
        contrast_rows[f"{hgrag}_MINUS_{right}"] = {
            "answer_em": em,
            "answer_f1": {
                **f1,
                "holm_adjusted_one_sided_p": p_adjusted,
            },
        }
    supporting = {
        f"{hgrag}_MINUS_{methods[3]}": {
            "answer_em": _bootstrap(audits, hgrag, methods[3], "answer_em"),
            "answer_f1": _bootstrap(audits, hgrag, methods[3], "answer_f1"),
        }
    }

    baseline = contrast_rows[f"{hgrag}_MINUS_{methods[0]}"]
    all_primary = list(contrast_rows.values())
    full_support = (
        baseline["answer_f1"]["point"] >= 0.010
        and all(row["answer_f1"]["ci95"][0] > 0.0 for row in all_primary)
        and all(
            row["answer_f1"]["holm_adjusted_one_sided_p"] <= 0.05
            for row in all_primary
        )
        and all(
            baseline["answer_f1"]["datasets"][dataset]["point"] > 0.0
            for dataset in DATASETS
        )
        and all(
            baseline["answer_f1"]["datasets"][dataset]["ci95"][1] >= 0.0
            for dataset in DATASETS
        )
        and all(row["answer_em"]["ci95"][0] >= -0.010 for row in all_primary)
    )
    if full_support:
        decision = "STRONG_BACKBONE_AND_STRUCTURAL_VALUE_SUPPORTED"
    elif baseline["answer_f1"]["ci95"][1] < 0.0:
        decision = "STRONG_BACKBONE_INCREMENT_NEGATIVE"
    elif (
        baseline["answer_f1"]["ci95"][0] > 0.0
        and baseline["answer_f1"]["holm_adjusted_one_sided_p"] <= 0.05
        and any(
            row["answer_f1"]["ci95"][0] <= 0.0 for row in all_primary[1:]
        )
    ):
        decision = "INCREMENT_SUPPORTED_STRUCTURE_NOT_ISOLATED"
    elif min(
        baseline["answer_f1"]["datasets"][dataset]["point"]
        for dataset in DATASETS
    ) < 0.0 < max(
        baseline["answer_f1"]["datasets"][dataset]["point"]
        for dataset in DATASETS
    ):
        decision = "CROSS_DATASET_HETEROGENEOUS"
    else:
        decision = "STAGE6A_EVIDENCE_INCONCLUSIVE"

    summary = {
        "bootstrap": {
            "generator": "NumPy PCG64",
            "iterations": BOOTSTRAP_ITERATIONS,
            "percentile": "linear",
            "seed": BOOTSTRAP_SEED,
        },
        "confirmation_methods": list(methods),
        "decision": decision,
        "methods": {
            method: _summary_for_method(audits, method) for method in methods
        },
        "primary_contrasts": contrast_rows,
        "status": "STAGE6A_CONFIRMATION_GOLD_EVALUATION_COMPLETE",
        "supporting_contrasts": supporting,
    }
    decision_row = {
        "decision": decision,
        "stage6b_authorized": decision
        == "STRONG_BACKBONE_AND_STRUCTURAL_VALUE_SUPPORTED",
        "stage6c_authorized": decision
        == "STRONG_BACKBONE_AND_STRUCTURAL_VALUE_SUPPORTED",
        "status": "STAGE6A_SCIENTIFIC_DECISION_FROZEN",
    }
    write_new_files_atomically(
        [
            (
                path_from_config(config, "confirmation_query_scores"),
                render_jsonl(audits),
            ),
            (
                path_from_config(config, "confirmation_evaluation_summary"),
                render_json(summary),
            ),
            (
                path_from_config(config, "scientific_decision"),
                render_json(decision_row),
            ),
        ]
    )
    print(f"STAGE6A_SCIENTIFIC_DECISION_FROZEN decision={decision}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument(
        "--mode", required=True, choices=("development", "confirmation")
    )
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage6A config must be an object")
    validate_authorization(config)
    assert_implementation_binding(config, Path(__file__).resolve().parents[1])
    if args.mode == "development":
        run_development(config)
    else:
        run_confirmation(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE6A_EVALUATION_FAIL: {exc}", file=sys.stderr)
        raise
