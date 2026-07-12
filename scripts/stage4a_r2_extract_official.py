"""Extract the frozen Stage4A-R2 development slice from the official archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any


EXPECTED_ARCHIVE_SHA256 = "95DF2BF56FDABE034E27AEBC580E02264232203CF52552F9EFE8A919E5529EEF"
EXPECTED_DEV_SHA256 = "79F77AE104088EA8E25B1A65DBECE768D45771194663BC5660EC9A98070DADF5"
EXPECTED_DEV_ROWS = 12576
DEVELOPMENT_START = 800
DEVELOPMENT_END = 5300
RESERVATION_START = 5300
RESERVATION_END = 9800


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def id_digest(ids: list[str]) -> str:
    return sha256_bytes(("\n".join(sorted(ids)) + "\n").encode("utf-8"))


def normalize_record(row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
    contexts = []
    title_to_indices: dict[str, list[int]] = {}
    for context_index, raw_context in enumerate(row.get("context") or []):
        if not isinstance(raw_context, list) or len(raw_context) != 2:
            raise ValueError(f"{row.get('_id')}: malformed official context")
        title = str(raw_context[0])
        sentences = [str(sentence) for sentence in raw_context[1]]
        title_to_indices.setdefault(title, []).append(context_index)
        contexts.append(
            {
                "doc_id": title,
                "title": title,
                "sentences": sentences,
            }
        )

    gold_evidence = []
    missing_title = 0
    out_of_range = 0
    duplicate_refs = 0
    seen_refs: set[tuple[str, int]] = set()
    supporting_facts = row.get("supporting_facts") or []
    for raw_support in supporting_facts:
        if not isinstance(raw_support, list) or len(raw_support) != 2:
            raise ValueError(f"{row.get('_id')}: malformed official supporting fact")
        title = str(raw_support[0])
        sentence_id = int(raw_support[1])
        key = (title, sentence_id)
        if key in seen_refs:
            duplicate_refs += 1
        seen_refs.add(key)
        context_indices = title_to_indices.get(title, [])
        if not context_indices:
            missing_title += 1
            continue
        sentences = contexts[context_indices[0]]["sentences"]
        if sentence_id < 0 or sentence_id >= len(sentences):
            out_of_range += 1
            continue
        gold_evidence.append(
            {
                "doc_id": title,
                "sentence_id": sentence_id,
                "text": sentences[sentence_id],
            }
        )

    normalized = {
        "id": str(row["_id"]),
        "dataset": "2wikimultihopqa",
        "question": str(row.get("question", "")),
        "answer": str(row.get("answer", "")),
        "contexts": contexts,
        "gold_evidence": gold_evidence,
        "metadata": {
            "type": row.get("type"),
            "evidences": row.get("evidences") or [],
            "source_split": "dev",
            "source_row_range": "[800:5300)",
            "provenance_status": "OFFICIAL_APRIL7_ARCHIVE",
        },
    }
    return normalized, {
        "supporting_facts": len(supporting_facts),
        "mapped_supporting_facts": len(gold_evidence),
        "missing_support_titles": missing_title,
        "out_of_range_support_sentences": out_of_range,
        "duplicate_supporting_fact_refs": duplicate_refs,
        "duplicate_context_titles": sum(
            max(len(indices) - 1, 0) for indices in title_to_indices.values()
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--official-zip", required=True, type=Path)
    parser.add_argument("--development-output", required=True, type=Path)
    parser.add_argument("--source-audit", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    archive_sha = sha256_file(args.official_zip)
    if archive_sha != EXPECTED_ARCHIVE_SHA256:
        raise ValueError(f"Official archive SHA mismatch: {archive_sha}")

    with zipfile.ZipFile(args.official_zip) as archive:
        bad_entry = archive.testzip()
        if bad_entry is not None:
            raise ValueError(f"Official archive CRC failed at {bad_entry}")
        dev_payload = archive.read("dev.json")
        entries = [
            {
                "name": info.filename,
                "uncompressed_bytes": info.file_size,
                "compressed_bytes": info.compress_size,
                "crc32": f"{info.CRC:08X}",
            }
            for info in archive.infolist()
        ]
    dev_sha = sha256_bytes(dev_payload)
    if dev_sha != EXPECTED_DEV_SHA256:
        raise ValueError(f"Official dev.json SHA mismatch: {dev_sha}")
    rows = json.loads(dev_payload.decode("utf-8"))
    if len(rows) != EXPECTED_DEV_ROWS:
        raise ValueError(f"Expected {EXPECTED_DEV_ROWS} dev rows, found {len(rows)}")

    all_ids = [str(row["_id"]) for row in rows]
    if len(set(all_ids)) != len(all_ids):
        raise ValueError("Official dev IDs are not unique")
    development_rows = rows[DEVELOPMENT_START:DEVELOPMENT_END]
    reservation_ids = [
        str(row["_id"]) for row in rows[RESERVATION_START:RESERVATION_END]
    ]
    development_ids = [str(row["_id"]) for row in development_rows]
    if len(development_ids) != 4500 or len(reservation_ids) != 4500:
        raise ValueError("Stage4A-R2 development/reservation counts differ from protocol")
    overlap = set(development_ids) & set(reservation_ids)
    if overlap:
        raise ValueError(f"Development/reservation ID overlap: {sorted(overlap)[:5]}")

    normalized_rows = []
    mapping_totals: Counter[str] = Counter()
    question_types: Counter[str] = Counter()
    missing_gold_queries = 0
    for row in development_rows:
        normalized, diagnostics = normalize_record(row)
        normalized_rows.append(normalized)
        mapping_totals.update(diagnostics)
        question_types[str(normalized["metadata"].get("type"))] += 1
        if not normalized["gold_evidence"]:
            missing_gold_queries += 1

    supporting_facts = mapping_totals["supporting_facts"]
    mapped_facts = mapping_totals["mapped_supporting_facts"]
    mapping_rate = mapped_facts / max(supporting_facts, 1)
    if mapping_rate != 1.0 or missing_gold_queries != 0:
        raise ValueError(
            f"Official mapping failure: rate={mapping_rate}, missing={missing_gold_queries}"
        )

    args.development_output.parent.mkdir(parents=True, exist_ok=True)
    args.development_output.write_text(
        json.dumps(normalized_rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    audit = {
        "protocol": "docs/STAGE4A_R2_PROTOCOL.md",
        "provenance_status": "OFFICIAL_APRIL7_ARCHIVE",
        "official_archive": {
            "path_basename": args.official_zip.name,
            "bytes": args.official_zip.stat().st_size,
            "sha256": archive_sha,
            "dev_json_sha256": dev_sha,
            "dev_rows": len(rows),
            "dev_unique_ids": len(set(all_ids)),
            "first_bad_crc_entry": bad_entry,
            "entries": entries,
        },
        "data_boundary": {
            "excluded_rows": "[0:800)",
            "development_rows": "[800:5300)",
            "development_queries": len(development_ids),
            "development_query_id_sha256": id_digest(development_ids),
            "reservation_rows": "[5300:9800)",
            "reservation_queries": len(reservation_ids),
            "reservation_query_id_sha256": id_digest(reservation_ids),
            "development_reservation_overlap": len(overlap),
            "reservation_content_written": False,
            "unused_rows": "[9800:12576)",
        },
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
            "development_unified_file": args.development_output.name,
            "reservation_file": None,
        },
    }
    args.source_audit.parent.mkdir(parents=True, exist_ok=True)
    args.source_audit.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "development_output": str(args.development_output),
                "source_audit": str(args.source_audit),
                "development_query_id_sha256": audit["data_boundary"]["development_query_id_sha256"],
                "reservation_query_id_sha256": audit["data_boundary"]["reservation_query_id_sha256"],
                "mapping": audit["mapping"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
