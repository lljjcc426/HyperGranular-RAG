"""Stage 0 dataset probe for Hyper-Granular-Ball RAG.

This script inspects raw multi-hop QA datasets and exports a small unified
sample plus a Markdown field report. It does not modify raw files.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def flatten_context(context: Any) -> list[dict[str, Any]]:
    contexts: list[dict[str, Any]] = []
    if isinstance(context, list):
        for item in context:
            if isinstance(item, list) and len(item) >= 2:
                title, sentences = item[0], item[1]
                contexts.append(
                    {
                        "doc_id": str(title),
                        "title": str(title),
                        "sentences": [str(s) for s in sentences],
                    }
                )
            elif isinstance(item, dict):
                title = item.get("title") or item.get("doc_id") or item.get("id") or ""
                sentences = item.get("sentences") or item.get("paragraph_text") or item.get("text") or []
                if isinstance(sentences, str):
                    sentences = [sentences]
                contexts.append(
                    {
                        "doc_id": str(title),
                        "title": str(title),
                        "sentences": [str(s) for s in sentences],
                    }
                )
    return contexts


def normalize_hotpot(row: dict[str, Any]) -> dict[str, Any]:
    contexts = flatten_context(row.get("context", []))
    gold = []
    for item in row.get("supporting_facts", []):
        if isinstance(item, list) and len(item) >= 2:
            title, sent_id = item[0], item[1]
            text = ""
            for ctx in contexts:
                if ctx["title"] == title and isinstance(sent_id, int) and sent_id < len(ctx["sentences"]):
                    text = ctx["sentences"][sent_id]
                    break
            gold.append(
                {
                    "doc_id": str(title),
                    "sentence_id": sent_id,
                    "text": text,
                }
            )
    return {
        "id": str(row.get("_id", "")),
        "dataset": "hotpotqa",
        "question": str(row.get("question", "")),
        "answer": str(row.get("answer", "")),
        "contexts": contexts,
        "gold_evidence": gold,
        "metadata": {
            "type": row.get("type"),
            "level": row.get("level"),
        },
    }


def normalize_musique(row: dict[str, Any]) -> dict[str, Any]:
    paragraphs = row.get("paragraphs") or row.get("contexts") or []
    contexts = []
    gold = []
    for idx, paragraph in enumerate(paragraphs):
        if not isinstance(paragraph, dict):
            continue
        title = paragraph.get("title") or paragraph.get("idx") or f"paragraph_{idx}"
        text = paragraph.get("paragraph_text") or paragraph.get("text") or ""
        sentences = [str(text)] if isinstance(text, str) else [str(s) for s in text]
        is_support = bool(paragraph.get("is_supporting") or paragraph.get("supporting"))
        contexts.append(
            {
                "doc_id": str(title),
                "title": str(title),
                "sentences": sentences,
            }
        )
        if is_support:
            gold.append(
                {
                    "doc_id": str(title),
                    "sentence_id": 0,
                    "text": " ".join(sentences),
                }
            )
    return {
        "id": str(row.get("id", "")),
        "dataset": "musique",
        "question": str(row.get("question", "")),
        "answer": str(row.get("answer", "")),
        "contexts": contexts,
        "gold_evidence": gold,
        "metadata": {
            "answer_aliases": row.get("answer_aliases"),
            "question_decomposition": row.get("question_decomposition"),
        },
    }


def normalize_row(dataset: str, row: dict[str, Any]) -> dict[str, Any]:
    if dataset == "hotpotqa":
        return normalize_hotpot(row)
    if dataset == "musique":
        return normalize_musique(row)
    raise ValueError(f"Unsupported dataset: {dataset}")


def field_counter(rows: list[dict[str, Any]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in rows:
        for key in row.keys():
            counter[key] += 1
    return counter


def write_report(
    report_path: Path,
    dataset: str,
    source_path: Path,
    rows: list[dict[str, Any]],
    unified: list[dict[str, Any]],
) -> None:
    keys = field_counter(rows)
    context_counts = [len(item["contexts"]) for item in unified]
    evidence_counts = [len(item["gold_evidence"]) for item in unified]
    lines = [
        f"# Stage 0 Dataset Probe: {dataset}",
        "",
        "## Material Passport",
        "",
        f"- Source file: `{source_path}`",
        f"- Dataset: `{dataset}`",
        f"- Raw rows inspected: {len(rows)}",
        f"- Unified sample rows: {len(unified)}",
        "",
        "## Raw Field Coverage",
        "",
        "| Field | Rows |",
        "|---|---:|",
    ]
    for key, count in keys.most_common():
        lines.append(f"| `{key}` | {count} |")
    lines.extend(
        [
            "",
            "## Unified Format Diagnostics",
            "",
            f"- Avg contexts per sample: {sum(context_counts) / max(len(context_counts), 1):.2f}",
            f"- Avg gold evidence per sample: {sum(evidence_counts) / max(len(evidence_counts), 1):.2f}",
            f"- Samples missing gold evidence: {sum(1 for n in evidence_counts if n == 0)}",
            "",
            "## First Unified Sample",
            "",
            "```json",
            json.dumps(unified[0] if unified else {}, ensure_ascii=False, indent=2)[:4000],
            "```",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["hotpotqa", "musique"], required=True)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()

    if args.input.suffix.lower() == ".jsonl":
        raw_rows = load_jsonl(args.input)
    else:
        loaded = load_json(args.input)
        raw_rows = loaded if isinstance(loaded, list) else loaded.get("data", [])

    if not raw_rows:
        raise RuntimeError(f"No rows found in {args.input}")

    sample = raw_rows[: args.limit]
    unified = [normalize_row(args.dataset, row) for row in sample]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(unified, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(args.report, args.dataset, args.input, raw_rows, unified)

    print(f"dataset={args.dataset}")
    print(f"raw_rows={len(raw_rows)}")
    print(f"sample_rows={len(unified)}")
    print(f"output={args.output}")
    print(f"report={args.report}")


if __name__ == "__main__":
    main()
