"""Fetch and map the pinned Stage4A 2Wiki pilot without storing reservation content."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any


DATASET = "framolfese/2WikiMultihopQA"
CONFIG = "default"
SPLIT = "validation"
EXPECTED_MIRROR_SHA = "fe713bfbd1afbca1a65246741a75890405d56a3a"
OFFICIAL_REPO_SHA = "13800e5be57df1b4040b9b1588c6c811779e69e9"
VALIDATION_PARQUET_OID = "5db5d6e1162d08d05f2d2a72aa0d9736b70dd1c6"
PAGE_SIZE = 100


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def id_digest(ids: list[str]) -> str:
    payload = "\n".join(sorted(ids)) + "\n"
    return sha256_bytes(payload.encode("utf-8"))


def fetch_json(url: str) -> tuple[bytes, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "HyperGranular-RAG-Stage4A/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()
    return payload, json.loads(payload.decode("utf-8"))


def mirror_sha() -> tuple[bytes, str]:
    payload, metadata = fetch_json(f"https://huggingface.co/api/datasets/{DATASET}")
    return payload, str(metadata["sha"])


def rows_url(offset: int) -> str:
    params = urllib.parse.urlencode(
        {
            "dataset": DATASET,
            "config": CONFIG,
            "split": SPLIT,
            "offset": offset,
            "length": PAGE_SIZE,
        }
    )
    return f"https://datasets-server.huggingface.co/rows?{params}"


def fetch_page(offset: int) -> tuple[bytes, list[dict[str, Any]], dict[str, Any]]:
    payload, response = fetch_json(rows_url(offset))
    rows = response.get("rows", [])
    if len(rows) != PAGE_SIZE:
        raise ValueError(f"Offset {offset}: expected {PAGE_SIZE} rows, found {len(rows)}")
    expected_indices = list(range(offset, offset + PAGE_SIZE))
    actual_indices = [int(item["row_idx"]) for item in rows]
    if actual_indices != expected_indices:
        raise ValueError(f"Offset {offset}: unexpected row indices")
    if any(item.get("truncated_cells") for item in rows):
        raise ValueError(f"Offset {offset}: Dataset Viewer returned truncated cells")
    return payload, [item["row"] for item in rows], response


def normalize_record(row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
    context = row.get("context") or {}
    titles = list(context.get("title") or [])
    sentences = list(context.get("sentences") or [])
    if len(titles) != len(sentences):
        raise ValueError(f"{row.get('id')}: context title/sentence array mismatch")
    contexts = []
    title_to_indices: dict[str, list[int]] = {}
    for index, (title, sentence_list) in enumerate(zip(titles, sentences)):
        title = str(title)
        title_to_indices.setdefault(title, []).append(index)
        contexts.append(
            {
                "doc_id": title,
                "title": title,
                "sentences": [str(sentence) for sentence in sentence_list],
            }
        )

    supporting = row.get("supporting_facts") or {}
    support_titles = list(supporting.get("title") or [])
    support_sent_ids = list(supporting.get("sent_id") or [])
    if len(support_titles) != len(support_sent_ids):
        raise ValueError(f"{row.get('id')}: supporting-fact arrays mismatch")
    gold_evidence = []
    missing_title = out_of_range = duplicate_refs = 0
    seen_refs: set[tuple[str, int]] = set()
    for title_value, sent_value in zip(support_titles, support_sent_ids):
        title = str(title_value)
        sent_id = int(sent_value)
        key = (title, sent_id)
        if key in seen_refs:
            duplicate_refs += 1
        seen_refs.add(key)
        indices = title_to_indices.get(title, [])
        if not indices:
            missing_title += 1
            continue
        context_index = indices[0]
        context_sentences = contexts[context_index]["sentences"]
        if sent_id < 0 or sent_id >= len(context_sentences):
            out_of_range += 1
            continue
        gold_evidence.append(
            {
                "doc_id": title,
                "sentence_id": sent_id,
                "text": context_sentences[sent_id],
            }
        )

    normalized = {
        "id": str(row["id"]),
        "dataset": "2wikimultihopqa",
        "question": str(row.get("question", "")),
        "answer": str(row.get("answer", "")),
        "contexts": contexts,
        "gold_evidence": gold_evidence,
        "metadata": {
            "type": row.get("type"),
            "evidences": row.get("evidences") or [],
            "source_split": SPLIT,
            "provenance_status": "PROVENANCE_DOWNGRADED",
        },
    }
    return normalized, {
        "supporting_facts": len(support_titles),
        "mapped_supporting_facts": len(gold_evidence),
        "missing_support_titles": missing_title,
        "out_of_range_support_sentences": out_of_range,
        "duplicate_supporting_fact_refs": duplicate_refs,
        "duplicate_context_titles": sum(max(len(indices) - 1, 0) for indices in title_to_indices.values()),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-output", required=True, type=Path)
    parser.add_argument("--source-audit", required=True, type=Path)
    parser.add_argument("--pilot-offset", type=int, default=0)
    parser.add_argument("--pilot-count", type=int, default=400)
    parser.add_argument("--reservation-offset", type=int, default=400)
    parser.add_argument("--reservation-count", type=int, default=400)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if (args.pilot_offset, args.pilot_count, args.reservation_offset, args.reservation_count) != (0, 400, 400, 400):
        raise ValueError("Stage4A protocol requires pilot [0:400) and reservation [400:800)")

    before_payload, before_sha = mirror_sha()
    if before_sha != EXPECTED_MIRROR_SHA:
        raise ValueError(f"Mirror SHA drift before extraction: {before_sha}")
    size_url = f"https://datasets-server.huggingface.co/size?dataset={urllib.parse.quote(DATASET, safe='')}"
    size_payload, size_response = fetch_json(size_url)
    validation_rows = next(
        int(item["num_rows"])
        for item in size_response["size"]["splits"]
        if item["config"] == CONFIG and item["split"] == SPLIT
    )
    if validation_rows != 12576:
        raise ValueError(f"Unexpected mirror validation rows: {validation_rows}")

    pilot_rows: list[dict[str, Any]] = []
    reservation_ids: list[str] = []
    page_audit: list[dict[str, Any]] = []
    for role, start, count in (
        ("pilot", args.pilot_offset, args.pilot_count),
        ("reservation_ids_only", args.reservation_offset, args.reservation_count),
    ):
        for offset in range(start, start + count, PAGE_SIZE):
            payload, rows, _ = fetch_page(offset)
            page_audit.append(
                {
                    "role": role,
                    "offset": offset,
                    "rows": len(rows),
                    "response_sha256": sha256_bytes(payload),
                }
            )
            if role == "pilot":
                pilot_rows.extend(rows)
            else:
                reservation_ids.extend(str(row["id"]) for row in rows)

    after_payload, after_sha = mirror_sha()
    if after_sha != before_sha:
        raise ValueError(f"Mirror SHA drift during extraction: before={before_sha}, after={after_sha}")

    pilot_ids = [str(row["id"]) for row in pilot_rows]
    if len(pilot_ids) != 400 or len(set(pilot_ids)) != 400:
        raise ValueError("Pilot IDs are not 400 unique values")
    if len(reservation_ids) != 400 or len(set(reservation_ids)) != 400:
        raise ValueError("Reservation IDs are not 400 unique values")
    overlap = set(pilot_ids) & set(reservation_ids)
    if overlap:
        raise ValueError(f"Pilot/reservation overlap: {sorted(overlap)[:5]}")

    normalized_rows = []
    mapping_totals: Counter[str] = Counter()
    question_types: Counter[str] = Counter()
    missing_gold_queries = 0
    for row in pilot_rows:
        normalized, diagnostics = normalize_record(row)
        normalized_rows.append(normalized)
        mapping_totals.update(diagnostics)
        question_types[str(normalized["metadata"].get("type"))] += 1
        if not normalized["gold_evidence"]:
            missing_gold_queries += 1

    supporting_facts = mapping_totals["supporting_facts"]
    mapped_facts = mapping_totals["mapped_supporting_facts"]
    mapping_rate = mapped_facts / max(supporting_facts, 1)
    args.pilot_output.parent.mkdir(parents=True, exist_ok=True)
    args.pilot_output.write_text(
        json.dumps(normalized_rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    audit = {
        "protocol": "docs/STAGE4A_PROTOCOL.md",
        "provenance_status": "PROVENANCE_DOWNGRADED",
        "official": {
            "repository": "https://github.com/Alab-NII/2wikimultihop",
            "repository_sha": OFFICIAL_REPO_SHA,
            "license": "Apache-2.0 repository license",
            "corrected_archive": "data_ids_april7.zip",
            "archive_download_status": "UNREACHABLE_FROM_EXPERIMENT_SHELL",
            "archive_checksum_status": "NOT_PUBLISHED",
        },
        "mirror": {
            "dataset": DATASET,
            "repository_sha_before": before_sha,
            "repository_sha_after": after_sha,
            "metadata_sha256_before": sha256_bytes(before_payload),
            "metadata_sha256_after": sha256_bytes(after_payload),
            "size_response_sha256": sha256_bytes(size_payload),
            "validation_rows": validation_rows,
            "validation_parquet_oid": VALIDATION_PARQUET_OID,
        },
        "data_boundary": {
            "pilot_rows": "[0:400)",
            "pilot_queries": len(pilot_ids),
            "pilot_query_id_sha256": id_digest(pilot_ids),
            "reservation_rows": "[400:800)",
            "reservation_queries": len(reservation_ids),
            "reservation_query_id_sha256": id_digest(reservation_ids),
            "pilot_reservation_overlap": len(overlap),
            "reservation_content_written": False,
        },
        "page_audit": page_audit,
        "mapping": {
            "queries": len(normalized_rows),
            "question_types": dict(sorted(question_types.items())),
            "supporting_facts": supporting_facts,
            "mapped_supporting_facts": mapped_facts,
            "supporting_fact_mapping_rate": mapping_rate,
            "queries_missing_gold": missing_gold_queries,
            **{
                key: mapping_totals[key]
                for key in (
                    "missing_support_titles",
                    "out_of_range_support_sentences",
                    "duplicate_supporting_fact_refs",
                    "duplicate_context_titles",
                )
            },
        },
        "local_outputs": {
            "pilot_unified_file": args.pilot_output.name,
            "reservation_file": None,
        },
    }
    args.source_audit.parent.mkdir(parents=True, exist_ok=True)
    args.source_audit.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "pilot_output": str(args.pilot_output),
                "source_audit": str(args.source_audit),
                "pilot_query_id_sha256": audit["data_boundary"]["pilot_query_id_sha256"],
                "reservation_query_id_sha256": audit["data_boundary"]["reservation_query_id_sha256"],
                "mapping": audit["mapping"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
