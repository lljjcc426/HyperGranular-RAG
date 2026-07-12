"""Split labeled Stage4B input into controller-only and evaluator-only channels."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from stage4b_u1_common import (
    SCHEMA_VERSION,
    assert_no_prohibited_keys,
    id_digest,
    load_jsonl,
    sha256_file,
    validate_unique_ids,
    write_json,
    write_jsonl,
)


UNIT_FIELDS = (
    "unit_id",
    "query_id",
    "dataset",
    "sample_id",
    "doc_id",
    "title",
    "context_index",
    "sentence_id",
    "text",
)
QUERY_FIELDS = (
    "query_id",
    "dataset",
    "sample_id",
    "question",
    "num_candidate_units",
)


def project_fields(row: dict[str, Any], fields: tuple[str, ...], label: str) -> dict[str, Any]:
    missing = [field for field in fields if field not in row]
    if missing:
        raise ValueError(f"{label} missing required fields: {missing}")
    return {field: row[field] for field in fields}


def prepare_channels(
    labeled_units: list[dict[str, Any]],
    labeled_queries: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    query_ids = validate_unique_ids(labeled_queries, "query_id", "query")
    unit_ids = validate_unique_ids(labeled_units, "unit_id", "unit")
    query_set = set(query_ids)
    units_by_query: dict[str, list[dict[str, Any]]] = {query_id: [] for query_id in query_ids}
    unit_query: dict[str, str] = {}
    for unit in labeled_units:
        query_id = str(unit["query_id"])
        if query_id not in query_set:
            raise ValueError(f"Unit references unknown query: {query_id}")
        units_by_query[query_id].append(unit)
        unit_query[str(unit["unit_id"])] = query_id

    unlabeled_units = [project_fields(row, UNIT_FIELDS, "unit") for row in labeled_units]
    unlabeled_queries = [project_fields(row, QUERY_FIELDS, "query") for row in labeled_queries]
    assert_no_prohibited_keys(unlabeled_units, "unlabeled_units")
    assert_no_prohibited_keys(unlabeled_queries, "unlabeled_queries")

    gold_rows: list[dict[str, Any]] = []
    for query in labeled_queries:
        query_id = str(query["query_id"])
        gold_ids = [str(value) for value in query.get("gold_unit_ids", [])]
        if not gold_ids:
            raise ValueError(f"Query has no Gold IDs: {query_id}")
        if len(gold_ids) != len(set(gold_ids)):
            raise ValueError(f"Query has duplicate Gold IDs: {query_id}")
        for unit_id in gold_ids:
            if unit_id not in unit_query or unit_query[unit_id] != query_id:
                raise ValueError(f"Gold unit does not belong to query {query_id}: {unit_id}")
        expected = set(gold_ids)
        labeled_flags = {
            str(unit["unit_id"])
            for unit in units_by_query[query_id]
            if bool(unit.get("is_gold"))
        }
        if expected != labeled_flags:
            raise ValueError(f"Unit/query Gold labels disagree for {query_id}")
        question_type = str(query.get("metadata", {}).get("type", "unknown"))
        gold_rows.append(
            {
                "query_id": query_id,
                "gold_unit_ids": sorted(gold_ids),
                "question_type": question_type,
            }
        )

    gold_map = {
        "schema_version": SCHEMA_VERSION,
        "query_id_sha256": id_digest(query_ids),
        "queries": gold_rows,
    }
    return unlabeled_units, unlabeled_queries, gold_map


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labeled-units", required=True, type=Path)
    parser.add_argument("--labeled-queries", required=True, type=Path)
    parser.add_argument("--unlabeled-units-output", required=True, type=Path)
    parser.add_argument("--unlabeled-queries-output", required=True, type=Path)
    parser.add_argument("--gold-map-output", required=True, type=Path)
    parser.add_argument("--controller-audit-output", required=True, type=Path)
    parser.add_argument("--evaluator-audit-output", required=True, type=Path)
    parser.add_argument("--expected-query-id-sha256")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    labeled_units = load_jsonl(args.labeled_units)
    labeled_queries = load_jsonl(args.labeled_queries)
    unlabeled_units, unlabeled_queries, gold_map = prepare_channels(
        labeled_units, labeled_queries
    )
    query_digest = gold_map["query_id_sha256"]
    if args.expected_query_id_sha256 and query_digest != args.expected_query_id_sha256.upper():
        raise ValueError("Query ID digest differs from the frozen boundary")

    write_jsonl(args.unlabeled_units_output, unlabeled_units)
    write_jsonl(args.unlabeled_queries_output, unlabeled_queries)
    write_json(args.gold_map_output, gold_map)
    controller_audit = {
        "schema_version": SCHEMA_VERSION,
        "status": "CONTROLLER_CHANNEL_PREPARED_NO_RETRIEVAL_METRICS",
        "queries": len(unlabeled_queries),
        "units": len(unlabeled_units),
        "query_id_sha256": query_digest,
        "channel_hashes": {
            "unlabeled_units": sha256_file(args.unlabeled_units_output),
            "unlabeled_queries": sha256_file(args.unlabeled_queries_output),
        },
        "controller_prohibited_keys_absent": True,
        "retrieval_metrics_computed": False,
    }
    evaluator_audit = {
        "schema_version": SCHEMA_VERSION,
        "status": "EVALUATOR_CHANNEL_PREPARED_NO_RETRIEVAL_METRICS",
        "queries": len(unlabeled_queries),
        "query_id_sha256": query_digest,
        "source_hashes": {
            "labeled_units": sha256_file(args.labeled_units),
            "labeled_queries": sha256_file(args.labeled_queries),
        },
        "evaluator_channel_hashes": {
            "gold_map": sha256_file(args.gold_map_output),
        },
        "retrieval_metrics_computed": False,
    }
    write_json(args.controller_audit_output, controller_audit)
    write_json(args.evaluator_audit_output, evaluator_audit)


if __name__ == "__main__":
    main()
