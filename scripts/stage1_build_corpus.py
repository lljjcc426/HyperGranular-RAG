"""Build retrieval units and query files for Stage 1 retrieval experiments."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SPACE_RE = re.compile(r"\s+")


def norm_text(text: str) -> str:
    return SPACE_RE.sub(" ", text.strip())


def load_json(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON list: {path}")
    return data


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_from_sample(sample_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = load_json(sample_path)
    units: list[dict[str, Any]] = []
    queries: list[dict[str, Any]] = []

    for sample in rows:
        dataset = sample["dataset"]
        sample_id = str(sample["id"])
        query_id = f"{dataset}::{sample_id}"
        sample_units: list[dict[str, Any]] = []

        for ctx_idx, ctx in enumerate(sample.get("contexts", [])):
            for sent_idx, sentence in enumerate(ctx.get("sentences", [])):
                text = norm_text(str(sentence))
                if not text:
                    continue
                unit_id = f"{query_id}::c{ctx_idx}::s{sent_idx}"
                unit = {
                    "unit_id": unit_id,
                    "query_id": query_id,
                    "dataset": dataset,
                    "sample_id": sample_id,
                    "doc_id": str(ctx.get("doc_id", "")),
                    "title": str(ctx.get("title", "")),
                    "context_index": ctx_idx,
                    "sentence_id": sent_idx,
                    "text": text,
                    "is_gold": False,
                }
                sample_units.append(unit)

        gold_unit_ids: list[str] = []
        used_unit_ids: set[str] = set()
        for evidence in sample.get("gold_evidence", []):
            ev_doc = str(evidence.get("doc_id", ""))
            ev_sent = evidence.get("sentence_id")
            ev_text = norm_text(str(evidence.get("text", "")))
            chosen_unit = None

            for unit in sample_units:
                if unit["unit_id"] in used_unit_ids:
                    continue
                if unit["doc_id"] == ev_doc and unit["sentence_id"] == ev_sent and unit["text"] == ev_text:
                    chosen_unit = unit
                    break

            if chosen_unit is None:
                for unit in sample_units:
                    if unit["unit_id"] in used_unit_ids:
                        continue
                    if unit["doc_id"] == ev_doc and unit["text"] == ev_text:
                        chosen_unit = unit
                        break

            if chosen_unit is None:
                for unit in sample_units:
                    if unit["unit_id"] in used_unit_ids:
                        continue
                    if unit["text"] == ev_text:
                        chosen_unit = unit
                        break

            if chosen_unit is not None:
                chosen_unit["is_gold"] = True
                used_unit_ids.add(chosen_unit["unit_id"])
                gold_unit_ids.append(chosen_unit["unit_id"])

        units.extend(sample_units)
        queries.append(
            {
                "query_id": query_id,
                "dataset": dataset,
                "sample_id": sample_id,
                "question": sample.get("question", ""),
                "answer": sample.get("answer", ""),
                "gold_unit_ids": gold_unit_ids,
                "num_candidate_units": len(sample_units),
                "num_gold_units": len(gold_unit_ids),
                "metadata": sample.get("metadata", {}),
            }
        )

    return units, queries


def summarize(units: list[dict[str, Any]], queries: list[dict[str, Any]]) -> dict[str, Any]:
    by_dataset: dict[str, dict[str, Any]] = {}
    for query in queries:
        item = by_dataset.setdefault(
            query["dataset"],
            {
                "queries": 0,
                "candidate_units": 0,
                "gold_units": 0,
                "queries_missing_gold": 0,
            },
        )
        item["queries"] += 1
        item["candidate_units"] += query["num_candidate_units"]
        item["gold_units"] += query["num_gold_units"]
        if query["num_gold_units"] == 0:
            item["queries_missing_gold"] += 1

    return {
        "datasets": by_dataset,
        "total_queries": len(queries),
        "total_units": len(units),
        "total_gold_units": sum(1 for unit in units if unit["is_gold"]),
    }


def write_report(path: Path, inputs: list[Path], summary: dict[str, Any]) -> None:
    lines = [
        "# Stage 1 Corpus Build Report",
        "",
        "## Material Passport",
        "",
        "- Stage: Stage 1 Retrieval-only MVP",
        "- Artifact: retrieval units and query gold labels",
        "- Input files:",
    ]
    lines.extend([f"  - `{p}`" for p in inputs])
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Total queries: {summary['total_queries']}",
            f"- Total retrieval units: {summary['total_units']}",
            f"- Total gold units: {summary['total_gold_units']}",
            "",
            "| Dataset | Queries | Candidate Units | Gold Units | Queries Missing Gold |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for dataset, item in sorted(summary["datasets"].items()):
        lines.append(
            f"| {dataset} | {item['queries']} | {item['candidate_units']} | "
            f"{item['gold_units']} | {item['queries_missing_gold']} |"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+", required=True, type=Path)
    parser.add_argument("--units-output", required=True, type=Path)
    parser.add_argument("--queries-output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()

    all_units: list[dict[str, Any]] = []
    all_queries: list[dict[str, Any]] = []
    for sample_path in args.inputs:
        units, queries = build_from_sample(sample_path)
        all_units.extend(units)
        all_queries.extend(queries)

    write_jsonl(args.units_output, all_units)
    write_jsonl(args.queries_output, all_queries)
    summary = summarize(all_units, all_queries)
    write_report(args.report, args.inputs, summary)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
