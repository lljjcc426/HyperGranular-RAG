"""Construct and freeze the Stage4B-U1 policy without loading evaluation labels."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np

from stage4b_u1_common import (
    SCHEMA_VERSION,
    assert_no_prohibited_keys,
    id_digest,
    load_json,
    load_jsonl,
    sha256_file,
    validate_unique_ids,
    write_json,
    write_jsonl,
)
from stage4b_u1_goldfree_retrieval import (
    RetrievalConfig,
    allocate_budget,
    build_query_decisions,
    fit_ecdf_references,
    normalize_matrix,
    score_rows,
    validate_ecdf_references,
)


UNIT_KEYS = {
    "unit_id",
    "query_id",
    "dataset",
    "sample_id",
    "doc_id",
    "title",
    "context_index",
    "sentence_id",
    "text",
}
QUERY_KEYS = {
    "query_id",
    "dataset",
    "sample_id",
    "question",
    "num_candidate_units",
}


def validate_controller_inputs(
    units: list[dict[str, Any]], queries: list[dict[str, Any]]
) -> tuple[list[str], list[str]]:
    assert_no_prohibited_keys(units, "controller.units")
    assert_no_prohibited_keys(queries, "controller.queries")
    for row in units:
        if set(row) != UNIT_KEYS:
            raise ValueError(f"Unlabeled unit schema differs: {sorted(set(row) ^ UNIT_KEYS)}")
    for row in queries:
        if set(row) != QUERY_KEYS:
            raise ValueError(f"Unlabeled query schema differs: {sorted(set(row) ^ QUERY_KEYS)}")
    unit_ids = validate_unique_ids(units, "unit_id", "unlabeled unit")
    query_ids = validate_unique_ids(queries, "query_id", "unlabeled query")
    query_set = set(query_ids)
    if {str(row["query_id"]) for row in units} != query_set:
        raise ValueError("Unlabeled unit/query ID sets differ")
    return unit_ids, query_ids


def embed_texts(
    texts: list[str], model_name: str, batch_size: int, max_length: int
) -> np.ndarray:
    import torch
    from transformers import AutoModel, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
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
            encoded = {key: value.to(device) for key, value in encoded.items()}
            output = model(**encoded)
            mask = encoded["attention_mask"].unsqueeze(-1).expand(output.last_hidden_state.size()).float()
            pooled = torch.sum(output.last_hidden_state * mask, dim=1) / torch.clamp(
                mask.sum(dim=1), min=1e-9
            )
            pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
            chunks.append(pooled.cpu().numpy().astype("float32"))
    return np.vstack(chunks)


def load_or_build_embeddings(
    path: Path,
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    model_name: str,
    batch_size: int,
    max_length: int,
) -> tuple[np.ndarray, np.ndarray]:
    unit_ids = np.asarray([str(row["unit_id"]) for row in units])
    query_ids = np.asarray([str(row["query_id"]) for row in queries])
    if path.exists():
        cache = np.load(path, allow_pickle=False)
        required = {"unit_embeddings", "query_embeddings", "unit_ids", "query_ids", "model_name", "max_length"}
        if not required.issubset(cache.files):
            raise ValueError("Gold-free embedding cache lacks ID-bound metadata")
        if not np.array_equal(cache["unit_ids"].astype(str), unit_ids):
            raise ValueError("Embedding cache unit order differs")
        if not np.array_equal(cache["query_ids"].astype(str), query_ids):
            raise ValueError("Embedding cache query order differs")
        if str(cache["model_name"][0]) != model_name or int(cache["max_length"][0]) != max_length:
            raise ValueError("Embedding cache model metadata differs")
        return normalize_matrix(cache["unit_embeddings"]), normalize_matrix(cache["query_embeddings"])

    unit_texts = [
        (str(row.get("title", "")) + ". " + str(row.get("text", ""))).strip()
        for row in units
    ]
    query_texts = [str(row["question"]) for row in queries]
    unit_embeddings = normalize_matrix(embed_texts(unit_texts, model_name, batch_size, max_length))
    query_embeddings = normalize_matrix(embed_texts(query_texts, model_name, batch_size, max_length))
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        unit_embeddings=unit_embeddings,
        query_embeddings=query_embeddings,
        unit_ids=unit_ids,
        query_ids=query_ids,
        model_name=np.asarray([model_name]),
        max_length=np.asarray([max_length], dtype="int64"),
    )
    return unit_embeddings, query_embeddings


def validate_channel_audit(
    audit: dict[str, Any],
    units_path: Path,
    queries_path: Path,
    query_ids: list[str],
) -> None:
    if audit.get("status") != "CONTROLLER_CHANNEL_PREPARED_NO_RETRIEVAL_METRICS":
        raise ValueError("Channel audit status differs")
    if bool(audit.get("retrieval_metrics_computed")):
        raise ValueError("Channel audit reports retrieval metrics")
    if audit.get("query_id_sha256") != id_digest(query_ids):
        raise ValueError("Channel audit query digest differs")
    hashes = audit.get("channel_hashes", {})
    if hashes.get("unlabeled_units") != sha256_file(units_path):
        raise ValueError("Unlabeled-unit hash differs from channel audit")
    if hashes.get("unlabeled_queries") != sha256_file(queries_path):
        raise ValueError("Unlabeled-query hash differs from channel audit")


def run_controller(
    *,
    units_path: Path,
    queries_path: Path,
    channel_audit_path: Path,
    embedding_cache: Path,
    decisions_output: Path,
    rankings_output: Path,
    policy_output: Path,
    mode: str,
    policy_input: Path | None,
    model_name: str,
    batch_size: int,
    max_length: int,
    config: RetrievalConfig,
    controller_source: Path,
    synthetic_test_mode: bool = False,
) -> dict[str, Any]:
    if mode not in {"development", "reservation"}:
        raise ValueError(f"Unknown controller mode: {mode}")
    if not synthetic_test_mode and config != RetrievalConfig():
        raise ValueError("Official Stage4B-U1 runs must use the frozen retrieval configuration")
    units = load_jsonl(units_path)
    queries = load_jsonl(queries_path)
    _, query_ids = validate_controller_inputs(units, queries)
    validate_channel_audit(load_json(channel_audit_path), units_path, queries_path, query_ids)
    unit_embeddings, query_embeddings = load_or_build_embeddings(
        embedding_cache, units, queries, model_name, batch_size, max_length
    )
    rows = build_query_decisions(
        units, queries, unit_embeddings, query_embeddings, config
    )

    parent_policy_sha: str | None = None
    if mode == "development":
        references = fit_ecdf_references(rows)
    else:
        if policy_input is None:
            raise ValueError("Reservation mode requires the frozen development policy")
        parent = load_json(policy_input)
        if parent.get("run_role") != "development":
            raise ValueError("Reservation parent policy is not a development policy")
        if parent.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("Reservation parent policy schema differs")
        if parent.get("retrieval_config") != config.to_dict():
            raise ValueError("Reservation retrieval config differs from the frozen policy")
        references = parent["ecdf_references"]
        validate_ecdf_references(references)
        parent_policy_sha = sha256_file(policy_input)
    score_rows(rows, references)
    allocation = allocate_budget(rows, config.budget_fraction)

    decision_fields = {
        "query_id",
        "dataset",
        "sample_id",
        "ball_score_margin",
        "boundary_margin",
        "selected_edge_count",
        "planned_insert_count",
        "feasible",
        "u_margin",
        "u_boundary",
        "r_edge",
        "r_candidate",
        "uncertainty",
        "readiness",
        "score",
        "tie_hash",
        "trigger_u1",
    }
    decisions = [{key: row[key] for key in decision_fields} for row in rows]
    rankings = [
        {
            "query_id": row["query_id"],
            "dataset": row["dataset"],
            "sample_id": row["sample_id"],
            "trigger_u1": row["trigger_u1"],
            "planned_insert_count": row["planned_insert_count"],
            "dense_top20_unit_ids": row["dense_top20_unit_ids"],
            "q25_top20_unit_ids": row["q25_top20_unit_ids"],
            "q25_inserted_unit_ids": row["q25_inserted_unit_ids"],
            "final_top20_unit_ids": row["final_top20_unit_ids"],
            "final_inserted_unit_ids": row["final_inserted_unit_ids"],
        }
        for row in rows
    ]
    assert_no_prohibited_keys(decisions, "controller.decisions")
    assert_no_prohibited_keys(rankings, "controller.rankings")
    write_jsonl(decisions_output, decisions)
    write_jsonl(rankings_output, rankings)
    policy = {
        "schema_version": SCHEMA_VERSION,
        "protocol": "docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md",
        "status": "SYNTHETIC_TEST_ONLY" if synthetic_test_mode else "POLICY_FROZEN_BEFORE_EVALUATION",
        "run_role": mode,
        "query_id_sha256": id_digest(query_ids),
        "queries": len(queries),
        "units": len(units),
        "model_name": model_name,
        "max_length": max_length,
        "retrieval_config": config.to_dict(),
        "ecdf_definition": "(count_less + 0.5 * count_equal) / n using exact float64 equality",
        "ecdf_references": references,
        "allocation": allocation,
        "input_hashes": {
            "unlabeled_units": sha256_file(units_path),
            "unlabeled_queries": sha256_file(queries_path),
            "channel_audit": sha256_file(channel_audit_path),
            "embedding_cache": sha256_file(embedding_cache),
        },
        "output_hashes": {
            "decisions": sha256_file(decisions_output),
            "rankings": sha256_file(rankings_output),
        },
        "controller_source_sha256": sha256_file(controller_source),
        "parent_development_policy_sha256": parent_policy_sha,
        "evaluation_labels_loaded": False,
    }
    write_json(policy_output, policy)
    return policy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", required=True, type=Path)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--channel-audit", required=True, type=Path)
    parser.add_argument("--embedding-cache", required=True, type=Path)
    parser.add_argument("--decisions-output", required=True, type=Path)
    parser.add_argument("--rankings-output", required=True, type=Path)
    parser.add_argument("--policy-output", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("development", "reservation"))
    parser.add_argument("--policy-input", type=Path)
    parser.add_argument("--model-name", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--max-length", type=int, default=192)
    parser.add_argument("--synthetic-test-mode", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_controller(
        units_path=args.units,
        queries_path=args.queries,
        channel_audit_path=args.channel_audit,
        embedding_cache=args.embedding_cache,
        decisions_output=args.decisions_output,
        rankings_output=args.rankings_output,
        policy_output=args.policy_output,
        mode=args.mode,
        policy_input=args.policy_input,
        model_name=args.model_name,
        batch_size=args.batch_size,
        max_length=args.max_length,
        config=RetrievalConfig(),
        controller_source=Path(__file__),
        synthetic_test_mode=args.synthetic_test_mode,
    )


if __name__ == "__main__":
    main()
