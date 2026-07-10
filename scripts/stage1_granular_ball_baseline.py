"""Granular-ball retrieval baseline for Stage 1.

This script builds adaptive granular balls over each query's candidate evidence
units in the same pure-Python TF-IDF space used by the fixed-unit baseline.
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


def normalize(vector: dict[str, float]) -> dict[str, float]:
    norm = math.sqrt(sum(value * value for value in vector.values()))
    if norm == 0:
        return {}
    return {term: value / norm for term, value in vector.items()}


def vectorize(text: str, idf: dict[str, float]) -> dict[str, float]:
    counts = Counter(tokenize(text))
    if not counts:
        return {}
    total = sum(counts.values())
    return normalize({term: (count / total) * idf.get(term, 0.0) for term, count in counts.items()})


def dot(a: dict[str, float], b: dict[str, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(value * b.get(term, 0.0) for term, value in a.items())


def centroid(unit_ids: list[str], vectors: dict[str, dict[str, float]]) -> dict[str, float]:
    acc: dict[str, float] = defaultdict(float)
    for unit_id in unit_ids:
        for term, value in vectors[unit_id].items():
            acc[term] += value
    if not unit_ids:
        return {}
    inv = 1.0 / len(unit_ids)
    return normalize({term: value * inv for term, value in acc.items()})


def approx_tokens(text: str) -> int:
    return len(text.split())


def describe_ball(
    ball_id: str,
    query_id: str,
    unit_ids: list[str],
    center: dict[str, float],
    vectors: dict[str, dict[str, float]],
    depth: int,
    boundary_width: float,
) -> dict[str, Any]:
    distances = [1.0 - dot(vectors[unit_id], center) for unit_id in unit_ids]
    radius = max(distances) if distances else 0.0
    mean_distance = sum(distances) / max(len(distances), 1)
    threshold = radius * (1.0 - boundary_width)
    boundary_count = sum(1 for distance in distances if radius > 0 and distance >= threshold)
    return {
        "ball_id": ball_id,
        "query_id": query_id,
        "unit_ids": unit_ids,
        "center": center,
        "size": len(unit_ids),
        "radius": radius,
        "mean_distance": mean_distance,
        "compactness": 1.0 - mean_distance,
        "boundary_count": boundary_count,
        "depth": depth,
    }


def split_ball(
    unit_ids: list[str],
    vectors: dict[str, dict[str, float]],
    center: dict[str, float],
) -> tuple[list[str], list[str]]:
    if len(unit_ids) < 2:
        return unit_ids, []

    seed_a = max(unit_ids, key=lambda unit_id: 1.0 - dot(vectors[unit_id], center))
    seed_b = min(unit_ids, key=lambda unit_id: dot(vectors[unit_id], vectors[seed_a]))
    if seed_a == seed_b:
        mid = len(unit_ids) // 2
        return unit_ids[:mid], unit_ids[mid:]

    left: list[str] = []
    right: list[str] = []
    for unit_id in unit_ids:
        if dot(vectors[unit_id], vectors[seed_a]) >= dot(vectors[unit_id], vectors[seed_b]):
            left.append(unit_id)
        else:
            right.append(unit_id)
    if not left or not right:
        mid = len(unit_ids) // 2
        return unit_ids[:mid], unit_ids[mid:]
    return left, right


def build_balls_for_query(
    query_id: str,
    unit_ids: list[str],
    vectors: dict[str, dict[str, float]],
    min_size: int,
    max_size: int,
    radius_threshold: float,
    max_depth: int,
    boundary_width: float,
) -> list[dict[str, Any]]:
    balls: list[dict[str, Any]] = []
    serial = 0

    def recurse(current_ids: list[str], depth: int) -> None:
        nonlocal serial
        current_center = centroid(current_ids, vectors)
        temp = describe_ball(
            f"{query_id}::ball{serial}",
            query_id,
            current_ids,
            current_center,
            vectors,
            depth,
            boundary_width,
        )
        should_split = (
            depth < max_depth
            and len(current_ids) >= 2 * min_size
            and (len(current_ids) > max_size or temp["radius"] > radius_threshold)
        )
        if should_split:
            left, right = split_ball(current_ids, vectors, current_center)
            if len(left) >= min_size and len(right) >= min_size:
                recurse(left, depth + 1)
                recurse(right, depth + 1)
                return
        serial += 1
        balls.append(temp)

    recurse(unit_ids, 0)
    return balls


def retrieve_from_balls(
    query: dict[str, Any],
    balls: list[dict[str, Any]],
    units_by_id: dict[str, dict[str, Any]],
    vectors: dict[str, dict[str, float]],
    idf: dict[str, float],
    max_k: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    query_vector = vectorize(query["question"], idf)
    scored_balls = []
    for ball in balls:
        scored_balls.append((dot(query_vector, ball["center"]), ball))
    scored_balls.sort(key=lambda item: (-item[0], item[1]["ball_id"]))
    top_score = scored_balls[0][0] if scored_balls else 0.0
    second_score = scored_balls[1][0] if len(scored_balls) > 1 else -1.0
    top_ball = scored_balls[0][1] if scored_balls else None
    top_distance = 1.0 - top_score
    top_radius = top_ball["radius"] if top_ball is not None else 0.0
    boundary_margin = abs(top_radius - top_distance) / (top_radius + 1e-9) if top_radius > 0 else 999.0

    ranked: list[dict[str, Any]] = []
    seen: set[str] = set()
    for ball_score, ball in scored_balls:
        members = []
        for unit_id in ball["unit_ids"]:
            unit = units_by_id[unit_id]
            members.append((dot(query_vector, vectors[unit_id]), unit))
        members.sort(key=lambda item: (-item[0], item[1]["unit_id"]))
        for unit_score, unit in members:
            if unit["unit_id"] in seen:
                continue
            seen.add(unit["unit_id"])
            ranked.append(
                {
                    "unit_id": unit["unit_id"],
                    "score": unit_score,
                    "ball_score": ball_score,
                    "ball_id": ball["ball_id"],
                    "ball_radius": ball["radius"],
                    "ball_size": ball["size"],
                    "is_gold": unit["is_gold"],
                    "title": unit["title"],
                    "text": unit["text"],
                    "tokens": approx_tokens(unit["text"]),
                }
            )
            if len(ranked) >= max_k:
                return ranked, {
                    "top_ball_score": top_score,
                    "ball_score_margin": top_score - second_score,
                    "top_ball_radius": top_radius,
                    "query_to_top_ball_distance": top_distance,
                    "boundary_margin": boundary_margin,
                }
    return ranked, {
        "top_ball_score": top_score,
        "ball_score_margin": top_score - second_score,
        "top_ball_radius": top_radius,
        "query_to_top_ball_distance": top_distance,
        "boundary_margin": boundary_margin,
    }


def retrieve_fixed_units(
    query: dict[str, Any],
    candidate_units: list[dict[str, Any]],
    vectors: dict[str, dict[str, float]],
    idf: dict[str, float],
    max_k: int,
) -> list[dict[str, Any]]:
    query_vector = vectorize(query["question"], idf)
    ranked = []
    for unit in candidate_units:
        ranked.append(
            {
                "unit_id": unit["unit_id"],
                "score": dot(query_vector, vectors[unit["unit_id"]]),
                "ball_score": None,
                "ball_id": None,
                "ball_radius": None,
                "ball_size": None,
                "is_gold": unit["is_gold"],
                "title": unit["title"],
                "text": unit["text"],
                "tokens": approx_tokens(unit["text"]),
            }
        )
    ranked.sort(key=lambda row: (-row["score"], row["unit_id"]))
    return ranked[:max_k]


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
        item["avg_balls"] = sum(row["ball_count"] for row in rows) / max(len(rows), 1)
        item["avg_ball_size"] = sum(row["avg_ball_size"] for row in rows) / max(len(rows), 1)
        item["avg_ball_radius"] = sum(row["avg_ball_radius"] for row in rows) / max(len(rows), 1)
        item["avg_boundary_units"] = sum(row["boundary_units"] for row in rows) / max(len(rows), 1)
        item["fallback_rate"] = sum(row.get("used_fallback", 0.0) for row in rows) / max(len(rows), 1)
        for k in k_values:
            for metric in ["evidence_recall", "hit", "chain_recall", "context_units", "context_tokens"]:
                key = f"{metric}_at_{k}"
                item[key] = sum(row[key] for row in rows) / max(len(rows), 1)
        summary[dataset] = item
    return summary


def load_baseline_summary(path: Path | None) -> dict[str, dict[str, float]]:
    if path is None:
        return {}
    rows: dict[str, dict[str, float]] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dataset = row["dataset"]
            rows[dataset] = {}
            for key, value in row.items():
                if key == "dataset":
                    continue
                try:
                    rows[dataset][key] = float(value)
                except (TypeError, ValueError):
                    rows[dataset][key] = 0.0
    return rows


def write_summary_csv(path: Path, summary: dict[str, Any], k_values: list[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "dataset",
        "queries",
        "avg_mrr",
        "avg_balls",
        "avg_ball_size",
        "avg_ball_radius",
        "avg_boundary_units",
        "fallback_rate",
    ]
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
            writer.writerow({"dataset": dataset, **item})


def write_report(
    path: Path,
    summary: dict[str, Any],
    baseline: dict[str, dict[str, float]],
    k_values: list[int],
    units_path: Path,
    queries_path: Path,
    params: argparse.Namespace,
) -> None:
    lines = [
        "# Stage 1 Granular-Ball Retrieval Baseline Report",
        "",
        "## Material Passport",
        "",
        "- Stage: Stage 1 Retrieval-only MVP",
        "- Baseline: adaptive granular-ball retrieval in pure-Python TF-IDF space",
        "- Retrieval pool: per-query candidate contexts",
        f"- Units input: `{units_path}`",
        f"- Queries input: `{queries_path}`",
        "",
        "## Granular-Ball Parameters",
        "",
        f"- min_size: {params.min_size}",
        f"- max_size: {params.max_size}",
        f"- radius_threshold: {params.radius_threshold}",
        f"- max_depth: {params.max_depth}",
        f"- boundary_width: {params.boundary_width}",
        f"- policy: {params.policy}",
        f"- decision_boundary_margin: {params.decision_boundary_margin}",
        f"- decision_score_margin: {params.decision_score_margin}",
        f"- decision_min_ball_score: {params.decision_min_ball_score}",
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
                f"- Avg balls/query: {item['avg_balls']:.2f}",
                f"- Avg ball size: {item['avg_ball_size']:.2f}",
                f"- Avg ball radius: {item['avg_ball_radius']:.4f}",
                f"- Avg boundary units/query: {item['avg_boundary_units']:.2f}",
                f"- Fallback rate: {item.get('fallback_rate', 0.0):.4f}",
                "",
                "| k | Evidence Recall | Δ vs TF-IDF | Full Chain Recall | Δ vs TF-IDF | Avg Tokens |",
                "|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for k in k_values:
            er = item[f"evidence_recall_at_{k}"]
            cr = item[f"chain_recall_at_{k}"]
            base = baseline.get(dataset, {})
            delta_er = er - base.get(f"evidence_recall_at_{k}", 0.0)
            delta_cr = cr - base.get(f"chain_recall_at_{k}", 0.0)
            lines.append(
                f"| {k} | {er:.4f} | {delta_er:+.4f} | {cr:.4f} | {delta_cr:+.4f} | "
                f"{item[f'context_tokens_at_{k}']:.2f} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Interpretation Boundary",
            "",
            "- This is not yet the final proposed method. It tests whether granular grouping and boundary decisions change retrieval behavior.",
            "- Balls are built per query over the candidate context list, so this remains a controlled MVP rather than full-corpus indexing.",
            "- The next version should add boundary-uncertainty-driven expansion instead of always expanding high-score balls.",
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
    parser.add_argument("--balls-output", required=True, type=Path)
    parser.add_argument("--summary-output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--baseline-summary", type=Path)
    parser.add_argument("--k", nargs="+", type=int, default=[1, 3, 5, 10, 20])
    parser.add_argument("--min-size", type=int, default=2)
    parser.add_argument("--max-size", type=int, default=5)
    parser.add_argument("--radius-threshold", type=float, default=0.78)
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--boundary-width", type=float, default=0.2)
    parser.add_argument("--policy", choices=["ball", "boundary_fallback"], default="ball")
    parser.add_argument("--decision-boundary-margin", type=float, default=0.25)
    parser.add_argument("--decision-score-margin", type=float, default=0.05)
    parser.add_argument("--decision-min-ball-score", type=float, default=0.12)
    args = parser.parse_args()

    units = load_jsonl(args.units)
    queries = load_jsonl(args.queries)
    k_values = sorted(set(args.k))
    max_k = max(k_values)

    idf = build_idf(units)
    vectors = {unit["unit_id"]: vectorize(unit["text"], idf) for unit in units}
    units_by_id = {unit["unit_id"]: unit for unit in units}
    units_by_query: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for unit in units:
        units_by_query[unit["query_id"]].append(unit)

    details: list[dict[str, Any]] = []
    all_balls_for_output: list[dict[str, Any]] = []

    for query in queries:
        query_units = units_by_query[query["query_id"]]
        unit_ids = [unit["unit_id"] for unit in query_units]
        balls = build_balls_for_query(
            query["query_id"],
            unit_ids,
            vectors,
            args.min_size,
            args.max_size,
            args.radius_threshold,
            args.max_depth,
            args.boundary_width,
        )
        ball_ranked, decision = retrieve_from_balls(query, balls, units_by_id, vectors, idf, max_k)
        use_fallback = False
        if args.policy == "boundary_fallback":
            use_fallback = (
                decision["boundary_margin"] <= args.decision_boundary_margin
                or decision["ball_score_margin"] <= args.decision_score_margin
                or decision["top_ball_score"] < args.decision_min_ball_score
            )
        ranked = retrieve_fixed_units(query, query_units, vectors, idf, max_k) if use_fallback else ball_ranked
        row = evaluate_query(query, ranked, k_values)
        row["ball_count"] = len(balls)
        row["avg_ball_size"] = sum(ball["size"] for ball in balls) / max(len(balls), 1)
        row["avg_ball_radius"] = sum(ball["radius"] for ball in balls) / max(len(balls), 1)
        row["boundary_units"] = sum(ball["boundary_count"] for ball in balls)
        row["used_fallback"] = 1.0 if use_fallback else 0.0
        row.update(decision)
        row["top_units"] = [
            {
                "rank": rank,
                "unit_id": item["unit_id"],
                "score": item["score"],
                "ball_score": item["ball_score"],
                "ball_id": item["ball_id"],
                "is_gold": item["is_gold"],
                "title": item["title"],
            }
            for rank, item in enumerate(ranked, start=1)
        ]
        details.append(row)

        for ball in balls:
            all_balls_for_output.append(
                {
                    "ball_id": ball["ball_id"],
                    "query_id": ball["query_id"],
                    "size": ball["size"],
                    "radius": ball["radius"],
                    "mean_distance": ball["mean_distance"],
                    "compactness": ball["compactness"],
                    "boundary_count": ball["boundary_count"],
                    "depth": ball["depth"],
                    "gold_units": sum(1 for unit_id in ball["unit_ids"] if units_by_id[unit_id]["is_gold"]),
                    "unit_ids": ball["unit_ids"],
                }
            )

    summary = aggregate(details, k_values)
    baseline = load_baseline_summary(args.baseline_summary)

    write_jsonl(args.details_output, details)
    write_jsonl(args.balls_output, all_balls_for_output)
    write_summary_csv(args.summary_output, summary, k_values)
    write_report(args.report, summary, baseline, k_values, args.units, args.queries, args)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
