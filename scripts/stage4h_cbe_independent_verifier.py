"""Independent Stage4H pre-Gold and final scientific verifier."""

from __future__ import annotations

import argparse
import json
import re
import string
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from stage4e_e2e_goldfree_runner import build_prompt
from stage4h_cbe_common import (
    DATASET_KEYS,
    DATASETS,
    HOTPOT_DATASET,
    METHODS,
    MUSIQUE_DATASET,
    RERUN_QUERIES_PER_DATASET,
    SAMPLE_SIZES,
    SCHEMA_VERSION,
    assert_file_identity,
    assert_implementation_binding,
    assert_no_gold_fields,
    file_identity,
    id_digest,
    load_json,
    load_jsonl,
    path_from_config,
    render_json,
    render_jsonl,
    require_json_int,
    require_native_string,
    rerun_selection_key,
    selection_key,
    sha256_bytes,
    validate_snapshot,
    write_new_files_atomically,
)
from stage4h_cbe_evaluate import summarize
from stage4h_cbe_retrieval import build_rankings, build_units_queries


def _assert_bound(config: dict[str, Any], key: str) -> Path:
    path = path_from_config(config, key)
    binding = config.get("inputs", {}).get(key)
    if not isinstance(binding, dict):
        raise ValueError(f"inputs.{key} binding is missing")
    assert_file_identity(path, binding, f"inputs.{key}")
    return path


def _source_native_ids(path: Path, key: str) -> list[str]:
    rows = load_jsonl(path) if path.suffix.lower() == ".jsonl" else load_json(path)
    if not isinstance(rows, list):
        raise ValueError(f"{path}: source rows differ")
    result: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"{path}[{index}] must be an object")
        result.append(require_native_string(row.get(key), f"{path}[{index}].{key}"))
    if len(result) != len(set(result)):
        raise ValueError(f"{path}: duplicate source IDs")
    return result


def _history_ids(config: dict[str, Any]) -> dict[str, set[str]]:
    result = {HOTPOT_DATASET: set(), MUSIQUE_DATASET: set()}
    for index, binding in enumerate(config.get("historical_inputs", [])):
        if not isinstance(binding, dict):
            raise ValueError("historical input binding differs")
        path = Path(require_native_string(binding.get("path"), "historical path"))
        assert_file_identity(path, binding, f"historical_inputs[{index}]")
        rows = load_jsonl(path) if path.suffix.lower() == ".jsonl" else load_json(path)
        if not isinstance(rows, list):
            raise ValueError(f"{path}: historical rows differ")
        for row_index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise ValueError(f"{path}[{row_index}] differs")
            dataset = row.get("dataset")
            lowered = dataset.lower() if isinstance(dataset, str) else path.name.lower()
            target = (
                HOTPOT_DATASET
                if "hotpot" in lowered
                else MUSIQUE_DATASET
                if "musique" in lowered
                else None
            )
            if target is None:
                continue
            value = next(
                (
                    row[key]
                    for key in ("sample_id", "_id", "id")
                    if isinstance(row.get(key), str) and row[key].strip()
                ),
                None,
            )
            result[target].add(
                require_native_string(value, f"{path}[{row_index}].native_id")
            )
    return result


def verify_input_selection(
    config: dict[str, Any],
    blind_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    history = _history_ids(config)
    selected_by_dataset: dict[str, list[str]] = defaultdict(list)
    for row in blind_rows:
        selected_by_dataset[row["dataset"]].append(row["sample_id"])
    sources = config.get("sources")
    if not isinstance(sources, dict):
        raise ValueError("source binding differs")
    source_specs = (
        ("hotpotqa", HOTPOT_DATASET, "_id"),
        ("musique", MUSIQUE_DATASET, "id"),
    )
    checks: dict[str, Any] = {}
    for source_key, dataset, id_key in source_specs:
        binding = sources.get(source_key)
        if not isinstance(binding, dict):
            raise ValueError(f"sources.{source_key} differs")
        path = Path(require_native_string(binding.get("path"), f"sources.{source_key}.path"))
        assert_file_identity(path, binding, f"sources.{source_key}")
        all_ids = _source_native_ids(path, id_key)
        eligible = [value for value in all_ids if value not in history[dataset]]
        expected = sorted(
            eligible,
            key=lambda value: selection_key(DATASET_KEYS[dataset], value),
        )[: SAMPLE_SIZES[dataset]]
        actual = selected_by_dataset[dataset]
        if actual != expected:
            raise ValueError(f"{dataset}: zero-overlap ID-only selection differs")
        checks[dataset] = {
            "eligible_source_ids": len(eligible),
            "historical_ids": len(history[dataset]),
            "historical_id_sha256": id_digest(sorted(history[dataset])),
            "sample_ids": len(actual),
            "sample_id_sha256": id_digest(actual),
        }
    return checks


def _renormalize_cache_matrix(
    matrix: np.ndarray, expected_rows: int, label: str
) -> np.ndarray:
    matrix = np.asarray(matrix, dtype="float32")
    if (
        matrix.ndim != 2
        or matrix.shape[0] != expected_rows
        or not np.isfinite(matrix).all()
    ):
        raise ValueError(f"{label}: cache matrix differs")
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    if np.any(norms <= 0.0) or not np.allclose(
        norms[:, 0], 1.0, atol=1e-5, rtol=0.0
    ):
        raise ValueError(f"{label}: cache embeddings are not L2-normalized")
    rebuilt = (matrix / norms).astype("float32")
    if not np.isfinite(rebuilt).all():
        raise ValueError(f"{label}: normalized cache matrix is not finite")
    return rebuilt


def _load_embedding_cache(
    path: Path,
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    with np.load(path, allow_pickle=False) as cache:
        required = {
            "metadata_json",
            "query_embeddings",
            "query_ids",
            "unit_embeddings",
            "unit_ids",
        }
        if set(cache.files) != required:
            raise ValueError(f"{path}: cache member contract differs")
        if cache["unit_ids"].tolist() != [row["unit_id"] for row in units]:
            raise ValueError(f"{path}: cache unit identity/order differs")
        if cache["query_ids"].tolist() != [row["query_id"] for row in queries]:
            raise ValueError(f"{path}: cache query identity/order differs")
        unit = np.asarray(cache["unit_embeddings"], dtype="float32")
        query = np.asarray(cache["query_embeddings"], dtype="float32")
        metadata = json.loads(str(cache["metadata_json"].item()))
    normalized = (
        _renormalize_cache_matrix(unit, len(units), str(path)),
        _renormalize_cache_matrix(query, len(queries), str(path)),
    )
    if not isinstance(metadata, dict):
        raise ValueError(f"{path}: cache metadata differs")
    return normalized[0], normalized[1], metadata


def _pair_map(
    rows: list[dict[str, Any]], label: str
) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(rows):
        query_id = require_native_string(row.get("query_id"), f"{label}.query_id")
        method = require_native_string(row.get("method"), f"{label}.method")
        if method not in METHODS:
            raise ValueError(f"{label}[{index}] method differs")
        key = query_id, method
        if key in result:
            raise ValueError(f"{label}: duplicate pair {key}")
        result[key] = row
    return result


def _subset_query_ids(queries: list[dict[str, Any]]) -> set[str]:
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
            raise ValueError(f"{dataset}: rerun subset differs")
        selected.update(row["query_id"] for row in rows)
    return selected


def verify_deterministic_subset(
    queries: list[dict[str, Any]],
    predictions_main: list[dict[str, Any]],
    predictions_subset: list[dict[str, Any]],
    prompts_main: list[dict[str, Any]],
    prompts_subset: list[dict[str, Any]],
) -> dict[str, Any]:
    subset_ids = _subset_query_ids(queries)
    expected_pairs = {(query_id, method) for query_id in subset_ids for method in METHODS}
    main_predictions = _pair_map(predictions_main, "predictions_main")
    subset_predictions = _pair_map(predictions_subset, "predictions_subset")
    main_prompts = _pair_map(prompts_main, "prompts_main")
    subset_prompts = _pair_map(prompts_subset, "prompts_subset")
    if set(subset_predictions) != expected_pairs or set(subset_prompts) != expected_pairs:
        raise ValueError("rerun subset pair coverage differs")
    for key in expected_pairs:
        if subset_predictions[key] != main_predictions[key]:
            raise ValueError(f"prediction subset differs from main: {key}")
        if subset_prompts[key] != main_prompts[key]:
            raise ValueError(f"prompt subset differs from main: {key}")
    return {
        "queries": len(subset_ids),
        "pairs": len(expected_pairs),
        "predictions_identical": True,
        "prompts_identical": True,
    }


def verify_prompts(
    config: dict[str, Any],
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    rankings: list[dict[str, Any]],
    prompt_rows: list[dict[str, Any]],
) -> None:
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        path_from_config(config, "generator_snapshot"), local_files_only=True
    )
    units_by_id = {row["unit_id"]: row for row in units}
    ranking_by_query = {row["query_id"]: row for row in rankings}
    prompt_map = _pair_map(prompt_rows, "prompt_audit_main")
    expected_pairs = {
        (query["query_id"], method) for query in queries for method in METHODS
    }
    if set(prompt_map) != expected_pairs:
        raise ValueError("main prompt pair coverage differs")
    for query in queries:
        for method in METHODS:
            ranked_ids = ranking_by_query[query["query_id"]]["methods"][method]
            expected = build_prompt(
                tokenizer,
                query["question"],
                [units_by_id[value] for value in ranked_ids],
                4096,
            )
            actual = prompt_map[(query["query_id"], method)]
            projected = {
                "evidence_unit_ids": actual.get("evidence_unit_ids"),
                "input_token_count": actual.get("input_token_count"),
                "prompt_sha256": actual.get("prompt_sha256"),
                "rank1_truncated": actual.get("rank1_truncated"),
            }
            if projected != expected:
                raise ValueError(f"{query['query_id']}/{method}: prompt reconstruction differs")


def verify_models(config: dict[str, Any]) -> None:
    for model_key, path_key in (
        ("minilm", "minilm_snapshot"),
        ("strong_dense", "strong_dense_snapshot"),
        ("generator", "generator_snapshot"),
    ):
        binding = config.get("models", {}).get(model_key)
        if not isinstance(binding, dict):
            raise ValueError(f"models.{model_key} binding differs")
        snapshot = path_from_config(config, path_key)
        if str(snapshot.resolve()) != binding.get("snapshot_path"):
            raise ValueError(f"models.{model_key} path differs")
        validate_snapshot(snapshot, binding, model_key)


def verify_pregold(config: dict[str, Any]) -> dict[str, Any]:
    if config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Stage4H schema differs")
    assert_implementation_binding(config, Path(__file__).resolve().parents[1])
    verify_models(config)
    strong_selection = load_json(_assert_bound(config, "strong_dense_selection_manifest"))
    if (
        not isinstance(strong_selection, dict)
        or strong_selection.get("status")
        != "STAGE4H_STRONG_DENSE_SELECTED_AND_SYNTHETICALLY_QUALIFIED"
        or strong_selection.get("selection_used_stage4h_gold") is not False
    ):
        raise ValueError("strong-dense selection manifest differs")
    blind_path = _assert_bound(config, "blind")
    manifest_path = _assert_bound(config, "input_manifest")
    blind_rows = load_jsonl(blind_path)
    assert_no_gold_fields(blind_rows, "Stage4H blind channel")
    units, queries = build_units_queries(blind_rows)
    if len(queries) != sum(SAMPLE_SIZES.values()):
        raise ValueError("Stage4H blind query count differs")
    selection_checks = verify_input_selection(config, blind_rows)
    manifest = load_json(manifest_path)
    if (
        not isinstance(manifest, dict)
        or manifest.get("status")
        != "STAGE4H_INPUT_CHANNELS_BUILT_PENDING_VERIFICATION"
    ):
        raise ValueError("input manifest status differs")
    if manifest.get("query_id_sha256") != id_digest(
        row["query_id"] for row in blind_rows
    ):
        raise ValueError("input manifest query digest differs")
    minilm_unit, minilm_query, minilm_metadata = _load_embedding_cache(
        _assert_bound(config, "minilm_embedding_cache"), units, queries
    )
    strong_unit, strong_query, strong_metadata = _load_embedding_cache(
        _assert_bound(config, "strong_embedding_cache"), units, queries
    )
    rankings, traces, _ = build_rankings(
        units,
        queries,
        minilm_unit,
        minilm_query,
        strong_unit,
        strong_query,
    )
    rankings_path = _assert_bound(config, "rankings")
    trace_path = _assert_bound(config, "retrieval_trace")
    if rankings_path.read_bytes() != render_jsonl(rankings):
        raise ValueError("ranking reconstruction differs")
    if trace_path.read_bytes() != render_jsonl(traces):
        raise ValueError("retrieval trace reconstruction differs")
    predictions_main_path = _assert_bound(config, "predictions_main")
    predictions_subset_path = _assert_bound(config, "predictions_rerun_subset")
    prompts_main_path = _assert_bound(config, "prompt_audit_main")
    prompts_subset_path = _assert_bound(config, "prompt_audit_rerun_subset")
    predictions_main = load_jsonl(predictions_main_path)
    predictions_subset = load_jsonl(predictions_subset_path)
    prompts_main = load_jsonl(prompts_main_path)
    prompts_subset = load_jsonl(prompts_subset_path)
    all_pairs = _pair_map(predictions_main, "predictions_main")
    expected_all_pairs = {
        (query["query_id"], method) for query in queries for method in METHODS
    }
    if set(all_pairs) != expected_all_pairs:
        raise ValueError("main prediction pair coverage differs")
    verify_prompts(config, units, queries, rankings, prompts_main)
    subset = verify_deterministic_subset(
        queries,
        predictions_main,
        predictions_subset,
        prompts_main,
        prompts_subset,
    )
    for key in ("telemetry_main", "telemetry_rerun_subset"):
        telemetry = load_json(_assert_bound(config, key))
        if (
            not isinstance(telemetry, dict)
            or telemetry.get("failed_calls") != 0
            or telemetry.get("status")
            != "STAGE4H_GOLDFREE_RUN_COMPLETE_PENDING_VERIFICATION"
        ):
            raise ValueError(f"{key} status differs")
    verification = {
        "artifacts": {
            key: file_identity(_assert_bound(config, key))
            for key in (
                "blind",
                "input_manifest",
                "strong_dense_selection_manifest",
                "minilm_embedding_cache",
                "strong_embedding_cache",
                "rankings",
                "retrieval_trace",
                "predictions_main",
                "prompt_audit_main",
                "telemetry_main",
                "predictions_rerun_subset",
                "prompt_audit_rerun_subset",
                "telemetry_rerun_subset",
            )
        },
        "checks": {
            "blind_gold_fields_absent": True,
            "candidate_units": len(units),
            "input_selection": selection_checks,
            "main_pairs": len(expected_all_pairs),
            "minilm_cache_metadata": minilm_metadata,
            "ranking_reconstruction": True,
            "strong_cache_metadata": strong_metadata,
            "subset_determinism": subset,
        },
        "query_count": len(queries),
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4H_PRE_GOLD_VERIFICATION_PASS",
    }
    write_new_files_atomically(
        ((path_from_config(config, "verified_pregold"), render_json(verification)),)
    )
    return verification


def _normalize_answer(value: str) -> str:
    value = value.lower()
    value = "".join(character for character in value if character not in string.punctuation)
    value = re.sub(r"\b(a|an|the)\b", " ", value)
    return " ".join(value.split())


def _answer_scores(prediction: str, answers: list[str]) -> tuple[float, float]:
    normalized_prediction = _normalize_answer(prediction)
    best_em = 0.0
    best_f1 = 0.0
    for answer in answers:
        normalized_answer = _normalize_answer(answer)
        em = float(normalized_prediction == normalized_answer)
        predicted_tokens = normalized_prediction.split()
        answer_tokens = normalized_answer.split()
        if not predicted_tokens or not answer_tokens:
            f1 = float(predicted_tokens == answer_tokens)
        else:
            overlap = sum((Counter(predicted_tokens) & Counter(answer_tokens)).values())
            if overlap == 0:
                f1 = 0.0
            else:
                precision = overlap / len(predicted_tokens)
                recall = overlap / len(answer_tokens)
                f1 = 2.0 * precision * recall / (precision + recall)
        best_em = max(best_em, em)
        best_f1 = max(best_f1, f1)
    return best_em, best_f1


def independent_query_audit(
    gold_rows: list[dict[str, Any]],
    prediction_rows: list[dict[str, Any]],
    prompt_rows: list[dict[str, Any]],
    ranking_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    predictions = _pair_map(prediction_rows, "predictions")
    prompts = _pair_map(prompt_rows, "prompts")
    rankings = {row["query_id"]: row for row in ranking_rows}
    audits: list[dict[str, Any]] = []
    for gold in gold_rows:
        query_id = gold["query_id"]
        methods: dict[str, Any] = {}
        for method in METHODS:
            prediction = predictions[(query_id, method)]
            prompt = prompts[(query_id, method)]
            ranked = rankings[query_id]["methods"][method]
            em, f1 = _answer_scores(prediction["prediction"], gold["answers"])
            if gold["dataset"] == HOTPOT_DATASET:
                targets = set(gold["supporting_unit_ids"])
                retrieved = set(ranked)
            else:
                targets = set(gold["supporting_paragraph_indices"])
                retrieved = {
                    int(match.group(1))
                    for unit_id in ranked
                    if (match := re.search(r"::p([0-9]+)::s[0-9]+$", unit_id))
                    is not None
                }
            overlap = len(targets & retrieved)
            methods[method] = {
                "answer_em": em,
                "answer_f1": f1,
                "evidence_count": len(prompt["evidence_unit_ids"]),
                "input_token_count": prompt["input_token_count"],
                "retrieval_cr20": float(overlap == len(targets)),
                "retrieval_er20": overlap / len(targets),
                "unknown": float(prediction["prediction"].strip().upper() == "UNKNOWN"),
            }
        audits.append(
            {
                "dataset": gold["dataset"],
                "methods": methods,
                "query_id": query_id,
                "sample_id": gold["sample_id"],
            }
        )
    return audits


def verify_final(config: dict[str, Any]) -> dict[str, Any]:
    pregold = load_json(_assert_bound(config, "verified_pregold"))
    if (
        not isinstance(pregold, dict)
        or pregold.get("status") != "STAGE4H_PRE_GOLD_VERIFICATION_PASS"
    ):
        raise PermissionError("Stage4H pre-Gold verification is absent")
    gold = load_jsonl(_assert_bound(config, "gold"))
    rankings = load_jsonl(_assert_bound(config, "rankings"))
    predictions = load_jsonl(_assert_bound(config, "predictions_main"))
    prompts = load_jsonl(_assert_bound(config, "prompt_audit_main"))
    independently_audited = independent_query_audit(
        gold, predictions, prompts, rankings
    )
    query_audit_path = _assert_bound(config, "query_audit")
    if query_audit_path.read_bytes() != render_jsonl(independently_audited):
        raise ValueError("independent query metric reconstruction differs")
    telemetry = load_json(_assert_bound(config, "telemetry_main"))
    dataset_summaries, equal_weight, decision = summarize(
        independently_audited, telemetry
    )
    expected_outputs = {
        "dataset_summaries": render_json(dataset_summaries),
        "equal_weight_summary": render_json(equal_weight),
        "scientific_decision": render_json(decision),
    }
    for key, payload in expected_outputs.items():
        path = _assert_bound(config, key)
        if path.read_bytes() != payload:
            raise ValueError(f"{key} reconstruction differs")
    required_decisions = {
        "FACET_HYPEREDGE_ABLATION",
        "FULL_METHOD_VS_DENSE",
        "FULL_METHOD_VS_STRONG_DENSE",
        "GRANULAR_BALL_ABLATION",
        "PROTECTED_INSERTION_ABLATION",
    }
    if set(decision["decisions"]) != required_decisions:
        raise ValueError("decision key contract differs")
    if decision["decisions"]["GRANULAR_BALL_ABLATION"] != "NOT_FAIRLY_DEFINED":
        raise ValueError("granular-ball status differs from the frozen card")
    result_artifact_keys = (
        "input_manifest",
        "rankings",
        "retrieval_trace",
        "predictions_main",
        "prompt_audit_main",
        "telemetry_main",
        "predictions_rerun_subset",
        "prompt_audit_rerun_subset",
        "telemetry_rerun_subset",
        "verified_pregold",
        "query_audit",
        "dataset_summaries",
        "equal_weight_summary",
        "scientific_decision",
        "descriptive_metadata",
    )
    artifacts = {
        key: file_identity(_assert_bound(config, key)) for key in result_artifact_keys
    }
    final = {
        "artifacts": artifacts,
        "checks": {
            "artifact_identities": True,
            "decision_reconstruction": True,
            "holm_and_bootstrap_reconstruction": True,
            "query_metric_reconstruction": True,
            "reservation_locked": config.get("locks", {}).get("reservation")
            == "LOCKED",
            "stage3b_locked": config.get("locks", {}).get("stage3b") == "LOCKED",
            "u2_not_authorized": config.get("locks", {}).get("u2")
            == "NOT_AUTHORIZED",
        },
        "decisions": decision["decisions"],
        "query_count": len(independently_audited),
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4H_FINAL_VERIFICATION_PASS",
    }
    final_payload = render_json(final)
    manifest = {
        "artifacts": {
            **artifacts,
            "final_verification": {
                "bytes": len(final_payload),
                "sha256": sha256_bytes(final_payload),
            },
        },
        "artifact_count": len(artifacts) + 1,
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4H_ARTIFACT_MANIFEST_FROZEN",
    }
    write_new_files_atomically(
        (
            (path_from_config(config, "final_verification"), final_payload),
            (path_from_config(config, "artifact_manifest"), render_json(manifest)),
        )
    )
    return final


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("pregold", "final"))
    args = parser.parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict):
        raise ValueError("Stage4H config must be an object")
    result = verify_pregold(config) if args.mode == "pregold" else verify_final(config)
    print(f"{result['status']} queries={result['query_count']}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STAGE4H_VERIFIER_FAIL: {exc}", file=sys.stderr)
        raise
