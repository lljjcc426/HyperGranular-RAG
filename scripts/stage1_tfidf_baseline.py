"""Pure-Python TF-IDF retrieval baseline for Stage 1.

The baseline retrieves over each question's candidate context units. This fits
HotpotQA distractor-style and MuSiQue paragraph-list evaluation before moving to
full-corpus retrieval.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_idf(units: list[dict[str, Any]]) -> dict[str, float]:
    df: Counter[str] = Counter()
    for unit in units:
        df.update(set(tokenize(unit["text"])))
    n_docs = len(units)
    return {term: math.log((n_docs + 1) / (freq + 1)) + 1.0 for term, freq in df.items()}


def vectorize(text: str, idf: dict[str, float]) -> dict[str, float]:
    counts = Counter(tokenize(text))
    if not counts:
        return {}
    total = sum(counts.values())
    vector = {term: (count / total) * idf.get(term, 0.0) for term, count in counts.items()}
    norm = math.sqrt(sum(value * value for value in vector.values()))
    if norm == 0:
        return {}
    return {term: value / norm for term, value in vector.items()}


def dot(a: dict[str, float], b: dict[str, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(value * b.get(term, 0.0) for term, value in a.items())


def approx_tokens(text: str) -> int:
    return len(text.split())


def retrieve(
    query: dict[str, Any],
    candidate_units: list[dict[str, Any]],
    unit_vectors: dict[str, dict[str, float]],
    idf: dict[str, float],
    max_k: int,
) -> list[dict[str, Any]]:
    query_vector = vectorize(query["question"], idf)
    scored = []
    for unit in candidate_units:
        scored.append(
            {
                "unit_id": unit["unit_id"],
                "score": dot(query_vector, unit_vectors[unit["unit_id"]]),
                "is_gold": unit["is_gold"],
                "title": unit["title"],
                "text": unit["text"],
                "tokens": approx_tokens(unit["text"]),
            }
        )
    scored.sort(key=lambda row: (-row["score"], row["unit_id"]))
    return scored[:max_k]


def evaluate_query(query: dict[str, Any], ranked: list[dict[str, Any]], k_values: list[int]) -> dict[str, Any]:
    gold = set(query["gold_unit_ids"])
    result: dict[str, Any] = {
        "query_id": query["query_id"],
        "dataset": query["dataset"],
        "num_gold": len(gold),
        "num_candidates": query["num_candidate_units"],
    }
    first_gold_rank = None
    for idx, row in enumerate(ranked, start=1):
        if row["unit_id"] in gold:
            first_gold_rank = idx
            break
    result["mrr"] = 0.0 if first_gold_rank is None else 1.0 / first_gold_rank

    for k in k_values:
        top = ranked[:k]
        retrieved = {row["unit_id"] for row in top}
        found = len(gold & retrieved)
        result[f"evidence_recall_at_{k}"] = found / len(gold) if gold else 0.0
        result[f"hit_at_{k}"] = 1.0 if found > 0 else 0.0
        result[f"chain_recall_at_{k}"] = 1.0 if gold and found == len(gold) else 0.0
        result[f"context_units_at_{k}"] = len(top)
        result[f"context_tokens_at_{k}"] = sum(row["tokens"] for row in top)
    return result


def aggregate(results: list[dict[str, Any]], k_values: list[int]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in results:
        grouped[row["dataset"]].append(row)
    grouped["ALL"] = results

    summary: dict[str, Any] = {}
    for dataset, rows in grouped.items():
        item: dict[str, Any] = {"queries": len(rows)}
        item["avg_mrr"] = sum(row["mrr"] for row in rows) / max(len(rows), 1)
        for k in k_values:
            for metric in ["evidence_recall", "hit", "chain_recall", "context_units", "context_tokens"]:
                key = f"{metric}_at_{k}"
                item[key] = sum(row[key] for row in rows) / max(len(rows), 1)
        summary[dataset] = item
    return summary


def write_summary_csv(path: Path, summary: dict[str, Any], k_values: list[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["dataset", "queries", "avg_mrr"]
    for k in k_values:
        fields.extend(
            [
                f"evidence_recall_at_{k}",
                f"hit_at_{k}",
                f"chain_recall_at_{k}",
                f"context_units_at_{k}",
                f"context_tokens_at_{k}",
            ]
        )
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for dataset, item in summary.items():
            row = {"dataset": dataset, **item}
            writer.writerow(row)


def write_report(path: Path, summary: dict[str, Any], k_values: list[int], units_path: Path, queries_path: Path) -> None:
    lines = [
        "# Stage 1 TF-IDF Retrieval Baseline Report",
        "",
        "## Material Passport",
        "",
        "- Stage: Stage 1 Retrieval-only MVP",
        "- Baseline: Pure-Python TF-IDF",
        "- Retrieval pool: per-query candidate contexts",
        f"- Units input: `{units_path}`",
        f"- Queries input: `{queries_path}`",
        "",
        "## Key Metrics",
        "",
    ]
    for dataset in sorted(summary.keys()):
        item = summary[dataset]
        lines.extend(
            [
                f"### {dataset}",
                "",
                f"- Queries: {item['queries']}",
                f"- Avg MRR: {item['avg_mrr']:.4f}",
                "",
                "| k | Evidence Recall | Hit Rate | Full Chain Recall | Avg Units | Avg Tokens |",
                "|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for k in k_values:
            lines.append(
                f"| {k} | {item[f'evidence_recall_at_{k}']:.4f} | "
                f"{item[f'hit_at_{k}']:.4f} | {item[f'chain_recall_at_{k}']:.4f} | "
                f"{item[f'context_units_at_{k}']:.2f} | {item[f'context_tokens_at_{k}']:.2f} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Interpretation Boundary",
            "",
            "- This is a lexical retrieval baseline over each question's candidate context list, not full-corpus retrieval.",
            "- The result is a lower engineering baseline for testing the evaluation pipeline before granular-ball indexing.",
            "- No generator or LLM is used in this stage.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", required=True, type=Path)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--details-output", required=True, type=Path)
    parser.add_argument("--summary-output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--k", nargs="+", type=int, default=[1, 3, 5, 10, 20])
    args = parser.parse_args()

    units = load_jsonl(args.units)
    queries = load_jsonl(args.queries)
    k_values = sorted(set(args.k))
    max_k = max(k_values)

    idf = build_idf(units)
    unit_vectors = {unit["unit_id"]: vectorize(unit["text"], idf) for unit in units}
    units_by_query: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for unit in units:
        units_by_query[unit["query_id"]].append(unit)

    details: list[dict[str, Any]] = []
    for query in queries:
        ranked = retrieve(query, units_by_query[query["query_id"]], unit_vectors, idf, max_k)
        row = evaluate_query(query, ranked, k_values)
        row["top_units"] = [
            {
                "rank": rank,
                "unit_id": item["unit_id"],
                "score": item["score"],
                "is_gold": item["is_gold"],
                "title": item["title"],
            }
            for rank, item in enumerate(ranked, start=1)
        ]
        details.append(row)

    summary = aggregate(details, k_values)
    write_jsonl(args.details_output, details)
    write_summary_csv(args.summary_output, summary, k_values)
    write_report(args.report, summary, k_values, args.units, args.queries)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
