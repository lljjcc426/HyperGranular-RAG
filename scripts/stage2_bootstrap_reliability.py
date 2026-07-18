import csv
import json
import random
from pathlib import Path
from typing import Any


ROOT = Path(r"E:\SCIENCE")
PROCESSED_DIR = ROOT / "超粒球RAG_数据" / "processed"
REPORT_DIR = ROOT / "超粒球RAG_数据" / "reports"

DETAILS = {
    "tfidf": PROCESSED_DIR / "stage1_tfidf_details.jsonl",
    "stage1e_facet": PROCESSED_DIR / "stage1_facet_fill_e2_b2_s010_details.jsonl",
    "stage1f_gate": PROCESSED_DIR / "stage1_fg_boundary_size8_score12_details.jsonl",
}

METRICS = [
    "evidence_recall_at_5",
    "chain_recall_at_5",
    "evidence_recall_at_10",
    "chain_recall_at_10",
]

COMPARISONS = [
    ("stage1e_facet", "tfidf"),
    ("stage1f_gate", "tfidf"),
    ("stage1f_gate", "stage1e_facet"),
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["query_id"]: row for row in rows}


def mean(values: list[float]) -> float:
    return sum(values) / max(len(values), 1)


def percentile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    pos = (len(sorted_values) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = pos - lo
    return sorted_values[lo] * (1.0 - frac) + sorted_values[hi] * frac


def bootstrap_delta(
    query_ids: list[str],
    rows_a: dict[str, dict[str, Any]],
    rows_b: dict[str, dict[str, Any]],
    metric: str,
    iterations: int,
    seed: int,
) -> dict[str, float]:
    rng = random.Random(seed)
    observed = mean([float(rows_a[qid][metric]) - float(rows_b[qid][metric]) for qid in query_ids])
    samples: list[float] = []
    n = len(query_ids)
    for _ in range(iterations):
        total = 0.0
        for _ in range(n):
            qid = query_ids[rng.randrange(n)]
            total += float(rows_a[qid][metric]) - float(rows_b[qid][metric])
        samples.append(total / n)
    samples.sort()
    p_positive = sum(1 for value in samples if value > 0.0) / iterations
    p_negative = sum(1 for value in samples if value < 0.0) / iterations
    return {
        "observed_delta": observed,
        "ci95_low": percentile(samples, 0.025),
        "ci95_high": percentile(samples, 0.975),
        "p_bootstrap_positive": p_positive,
        "p_bootstrap_negative": p_negative,
    }


def fmt(value: float) -> str:
    return f"{value:.4f}"


def main() -> None:
    detail_rows = {name: by_id(read_jsonl(path)) for name, path in DETAILS.items()}
    query_ids = sorted(detail_rows["tfidf"])
    for name, rows in detail_rows.items():
        if set(rows) != set(query_ids):
            raise ValueError(f"Query ids do not align for {name}")

    dataset_query_ids: dict[str, list[str]] = {"ALL": query_ids}
    for qid in query_ids:
        dataset = detail_rows["tfidf"][qid]["dataset"]
        dataset_query_ids.setdefault(dataset, []).append(qid)

    out_rows: list[dict[str, str]] = []
    iterations = 5000
    for dataset in ["ALL", "hotpotqa", "musique"]:
        ids = dataset_query_ids[dataset]
        for method_a, method_b in COMPARISONS:
            for metric in METRICS:
                result = bootstrap_delta(
                    ids,
                    detail_rows[method_a],
                    detail_rows[method_b],
                    metric,
                    iterations,
                    seed=20260709 + len(out_rows),
                )
                out_rows.append(
                    {
                        "dataset": dataset,
                        "method_a": method_a,
                        "method_b": method_b,
                        "metric": metric,
                        "queries": str(len(ids)),
                        "iterations": str(iterations),
                        "observed_delta": fmt(result["observed_delta"]),
                        "ci95_low": fmt(result["ci95_low"]),
                        "ci95_high": fmt(result["ci95_high"]),
                        "p_bootstrap_positive": fmt(result["p_bootstrap_positive"]),
                        "p_bootstrap_negative": fmt(result["p_bootstrap_negative"]),
                    }
                )

    csv_path = REPORT_DIR / "stage2_bootstrap_reliability.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)

    def row_for(dataset: str, method_a: str, method_b: str, metric: str) -> dict[str, str]:
        for row in out_rows:
            if row["dataset"] == dataset and row["method_a"] == method_a and row["method_b"] == method_b and row["metric"] == metric:
                return row
        raise KeyError((dataset, method_a, method_b, metric))

    md_path = ROOT / "超粒球RAG_Stage2A统计可靠性报告.md"
    lines = [
        "# 超粒球RAG Stage2A 统计可靠性报告",
        "",
        "## Material Passport",
        "",
        "- Artifact: Stage2A paired bootstrap reliability report",
        "- Status: ANALYZED",
        "- Input: aligned per-query retrieval details for TF-IDF, Stage1E facet-aware, Stage1F noise-gated",
        "- Bootstrap: paired query resampling, 5000 iterations, fixed seeds",
        "- Generated by: stage2_bootstrap_reliability.py",
        "",
        "## Key Bootstrap Results",
        "",
        "| Dataset | Comparison | Metric | Delta | 95% CI | P(delta > 0) |",
        "|---|---|---|---:|---:|---:|",
    ]
    key_rows = [
        ("ALL", "stage1f_gate", "tfidf", "chain_recall_at_10"),
        ("hotpotqa", "stage1f_gate", "tfidf", "chain_recall_at_10"),
        ("musique", "stage1f_gate", "tfidf", "chain_recall_at_10"),
        ("ALL", "stage1f_gate", "stage1e_facet", "chain_recall_at_10"),
        ("ALL", "stage1f_gate", "tfidf", "evidence_recall_at_10"),
        ("musique", "stage1f_gate", "tfidf", "evidence_recall_at_10"),
    ]
    for dataset, method_a, method_b, metric in key_rows:
        row = row_for(dataset, method_a, method_b, metric)
        lines.append(
            f"| {dataset} | {method_a} - {method_b} | {metric} | {row['observed_delta']} | "
            f"[{row['ci95_low']}, {row['ci95_high']}] | {row['p_bootstrap_positive']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    all_cr = row_for("ALL", "stage1f_gate", "tfidf", "chain_recall_at_10")
    musique_cr = row_for("musique", "stage1f_gate", "tfidf", "chain_recall_at_10")
    hotpot_cr = row_for("hotpotqa", "stage1f_gate", "tfidf", "chain_recall_at_10")
    f_vs_e = row_for("ALL", "stage1f_gate", "stage1e_facet", "chain_recall_at_10")
    lines.extend(
        [
            f"- ALL CR@10 delta Stage1F-vs-TFIDF = {all_cr['observed_delta']} with 95% CI [{all_cr['ci95_low']}, {all_cr['ci95_high']}].",
            f"- MuSiQue CR@10 delta Stage1F-vs-TFIDF = {musique_cr['observed_delta']} with 95% CI [{musique_cr['ci95_low']}, {musique_cr['ci95_high']}].",
            f"- HotpotQA CR@10 delta Stage1F-vs-TFIDF = {hotpot_cr['observed_delta']} with 95% CI [{hotpot_cr['ci95_low']}, {hotpot_cr['ci95_high']}].",
            f"- Stage1F-vs-Stage1E ALL CR@10 delta = {f_vs_e['observed_delta']} with 95% CI [{f_vs_e['ci95_low']}, {f_vs_e['ci95_high']}]; this supports framing Stage1F as noise reduction at similar chain recall, not as recall improvement over Stage1E.",
            "- Use these intervals as descriptive bootstrap evidence, not a final statistical proof; the current sample is 400 queries and was not pre-registered.",
            "",
            f"CSV output: `{csv_path}`",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
