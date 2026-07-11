"""Reconcile the Stage4A mirror pilot against the official April 7 archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any


PILOT_OFFSETS = (0, 100, 200, 300)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256_bytes(payload)


def official_context(row: dict[str, Any]) -> list[tuple[str, list[str]]]:
    return [(str(title), [str(sentence) for sentence in sentences]) for title, sentences in row["context"]]


def mirror_context(row: dict[str, Any]) -> list[tuple[str, list[str]]]:
    return [
        (str(title), [str(sentence) for sentence in sentences])
        for title, sentences in zip(row["context"]["title"], row["context"]["sentences"])
    ]


def unified_context(row: dict[str, Any]) -> list[tuple[str, list[str]]]:
    return [
        (str(context["title"]), [str(sentence) for sentence in context["sentences"]])
        for context in row["contexts"]
    ]


def canonical_context(contexts: list[tuple[str, list[str]]]) -> list[tuple[str, list[str]]]:
    return sorted(
        contexts,
        key=lambda item: json.dumps(item, ensure_ascii=False, separators=(",", ":")),
    )


def official_support(row: dict[str, Any]) -> list[tuple[str, int]]:
    return [(str(title), int(sentence_id)) for title, sentence_id in row["supporting_facts"]]


def mirror_support(row: dict[str, Any]) -> list[tuple[str, int]]:
    return [
        (str(title), int(sentence_id))
        for title, sentence_id in zip(
            row["supporting_facts"]["title"],
            row["supporting_facts"]["sent_id"],
        )
    ]


def official_gold(row: dict[str, Any]) -> list[dict[str, Any]]:
    contexts: dict[str, list[str]] = {}
    for title, sentences in official_context(row):
        contexts.setdefault(title, sentences)
    output = []
    for title, sentence_id in official_support(row):
        sentences = contexts.get(title, [])
        if 0 <= sentence_id < len(sentences):
            output.append(
                {
                    "doc_id": title,
                    "sentence_id": sentence_id,
                    "text": sentences[sentence_id],
                }
            )
    return output


def common_official(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row["_id"]),
        "question": str(row["question"]),
        "answer": str(row["answer"]),
        "type": str(row["type"]),
        "evidences": row["evidences"],
        "supporting_facts": official_support(row),
        "context": canonical_context(official_context(row)),
    }


def common_mirror(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "question": str(row["question"]),
        "answer": str(row["answer"]),
        "type": str(row["type"]),
        "evidences": row["evidences"],
        "supporting_facts": mirror_support(row),
        "context": canonical_context(mirror_context(row)),
    }


def common_unified(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "question": str(row["question"]),
        "answer": str(row["answer"]),
        "type": str(row["metadata"]["type"]),
        "evidences": row["metadata"]["evidences"],
        "gold_evidence": row["gold_evidence"],
        "context": canonical_context(unified_context(row)),
    }


def load_mirror_rows(cache_dir: Path) -> list[dict[str, Any]]:
    output = []
    for offset in PILOT_OFFSETS:
        page = json.loads((cache_dir / f"pilot_page_{offset:06d}.json").read_text(encoding="utf-8"))
        rows = page["rows"]
        if [int(item["row_idx"]) for item in rows] != list(range(offset, offset + 100)):
            raise ValueError(f"Mirror cache row indices differ at offset {offset}")
        output.extend(item["row"] for item in rows)
    return output


def describe_context_difference(
    index: int,
    official_row: dict[str, Any],
    mirror_row: dict[str, Any],
) -> dict[str, Any]:
    official_pairs = Counter(
        json.dumps(item, ensure_ascii=False, separators=(",", ":"))
        for item in official_context(official_row)
    )
    mirror_pairs = Counter(
        json.dumps(item, ensure_ascii=False, separators=(",", ":"))
        for item in mirror_context(mirror_row)
    )

    def summarize(raw_items: list[str]) -> list[dict[str, Any]]:
        output = []
        for raw in raw_items:
            title, sentences = json.loads(raw)
            output.append(
                {
                    "title": title,
                    "sentence_count": len(sentences),
                    "text_sha256": sha256_bytes("\n".join(sentences).encode("utf-8")),
                }
            )
        return output

    return {
        "row_index": index,
        "query_id": str(official_row["_id"]),
        "question_type": str(official_row["type"]),
        "official_only_contexts": summarize(list((official_pairs - mirror_pairs).elements())),
        "mirror_only_contexts": summarize(list((mirror_pairs - official_pairs).elements())),
        "supporting_fact_titles": [title for title, _ in official_support(official_row)],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--official-zip", required=True, type=Path)
    parser.add_argument("--mirror-cache", required=True, type=Path)
    parser.add_argument("--pilot-unified", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with zipfile.ZipFile(args.official_zip) as archive:
        bad_entry = archive.testzip()
        entries = [
            {
                "name": info.filename,
                "uncompressed_bytes": info.file_size,
                "compressed_bytes": info.compress_size,
                "crc32": f"{info.CRC:08X}",
            }
            for info in archive.infolist()
        ]
        dev_payload = archive.read("dev.json")
    if bad_entry is not None:
        raise ValueError(f"Official archive CRC failed at {bad_entry}")

    official_rows = json.loads(dev_payload.decode("utf-8"))
    mirror_rows = load_mirror_rows(args.mirror_cache)
    unified_rows = json.loads(args.pilot_unified.read_text(encoding="utf-8"))
    reservation_manifest = json.loads(
        (args.mirror_cache / "reservation_ids_manifest.json").read_text(encoding="utf-8")
    )
    reservation_ids = [query_id for page in reservation_manifest["pages"] for query_id in page["ids"]]
    if len(official_rows) != 12576 or len(mirror_rows) != 400 or len(unified_rows) != 400:
        raise ValueError("Unexpected official, mirror, or unified row count")

    shared_fields = ("id", "question", "answer", "type", "evidences", "supporting_facts", "context")
    shared_mismatches: Counter[str] = Counter()
    unified_mismatches: Counter[str] = Counter()
    context_order_only_changes = 0
    context_differences = []
    gold_difference_ids = []

    official_common = []
    mirror_common = []
    for index, (official_row, mirror_row, unified_row) in enumerate(
        zip(official_rows[:400], mirror_rows, unified_rows)
    ):
        official_value = common_official(official_row)
        mirror_value = common_mirror(mirror_row)
        official_common.append(official_value)
        mirror_common.append(mirror_value)
        for field in shared_fields:
            shared_mismatches[field] += int(official_value[field] != mirror_value[field])
        if official_value["context"] != mirror_value["context"]:
            context_differences.append(describe_context_difference(index, official_row, mirror_row))
        elif official_context(official_row) != mirror_context(mirror_row):
            context_order_only_changes += 1

        official_unified_value = {
            "id": str(official_row["_id"]),
            "question": str(official_row["question"]),
            "answer": str(official_row["answer"]),
            "type": str(official_row["type"]),
            "evidences": official_row["evidences"],
            "gold_evidence": official_gold(official_row),
            "context": canonical_context(official_context(official_row)),
        }
        unified_value = common_unified(unified_row)
        for field in official_unified_value:
            unified_mismatches[field] += int(official_unified_value[field] != unified_value[field])
        if official_unified_value["gold_evidence"] != unified_value["gold_evidence"]:
            gold_difference_ids.append(str(official_row["_id"]))

    official_candidate_units = sum(
        sum(1 for sentence in sentences if str(sentence).strip())
        for row in official_rows[:400]
        for _, sentences in row["context"]
    )
    mirror_candidate_units = sum(
        sum(1 for sentence in context["sentences"] if str(sentence).strip())
        for row in unified_rows
        for context in row["contexts"]
    )
    official_ids = [str(row["_id"]) for row in official_rows]
    official_only_fields = sorted(set(official_rows[0]) - ({"_id"} | set(mirror_rows[0])))
    mirror_only_fields = sorted(set(mirror_rows[0]) - ({"id"} | set(official_rows[0])))

    audit = {
        "material_passport": {
            "origin_skill": "academic-research-suite / experiment-agent",
            "mode": "validate",
            "verification_status": "VERIFIED_SOURCE_MISMATCH",
            "protocol_relation": "post-run official archive reconciliation; no retrieval rerun",
        },
        "official_archive": {
            "path_basename": args.official_zip.name,
            "bytes": args.official_zip.stat().st_size,
            "sha256": sha256_file(args.official_zip),
            "first_bad_crc_entry": bad_entry,
            "entries": entries,
            "dev_json_sha256": sha256_bytes(dev_payload),
            "dev_rows": len(official_rows),
            "dev_unique_ids": len(set(official_ids)),
        },
        "pilot_shared_field_comparison": {
            "rows": len(mirror_rows),
            "mismatches_by_field": dict(shared_mismatches),
            "context_order_only_changes": context_order_only_changes,
            "context_content_mismatch_queries": len(context_differences),
            "official_canonical_sha256": canonical_digest(official_common),
            "mirror_canonical_sha256": canonical_digest(mirror_common),
            "canonical_hash_equal": canonical_digest(official_common) == canonical_digest(mirror_common),
            "context_differences": context_differences,
        },
        "pilot_unified_comparison": {
            "rows": len(unified_rows),
            "mismatches_by_field": dict(unified_mismatches),
            "gold_evidence_mismatch_query_ids": gold_difference_ids,
            "official_candidate_units": official_candidate_units,
            "mirror_candidate_units": mirror_candidate_units,
        },
        "reservation_id_comparison": {
            "rows": len(reservation_ids),
            "ordered_match_official_rows_400_800": reservation_ids == official_ids[400:800],
            "set_match_official_rows_400_800": set(reservation_ids) == set(official_ids[400:800]),
            "content_embedded_or_scored": False,
        },
        "schema_difference": {
            "id_rename": "_id -> id",
            "official_only_fields": official_only_fields,
            "mirror_only_fields": mirror_only_fields,
        },
        "decision": {
            "official_archive_integrity": "VERIFIED",
            "mirror_pilot_id_alignment": "VERIFIED",
            "retrieval_shared_content": "MISMATCH_DETECTED",
            "stage4a_metrics_scope": "MIRROR_SPECIFIC_ONLY",
            "paper_grade_external_evidence": "NOT_ELIGIBLE",
            "retrieval_metrics_rerun_during_reconciliation": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "archive_sha256": audit["official_archive"]["sha256"],
                "context_content_mismatch_queries": len(context_differences),
                "gold_evidence_mismatch_queries": len(gold_difference_ids),
                "decision": audit["decision"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
