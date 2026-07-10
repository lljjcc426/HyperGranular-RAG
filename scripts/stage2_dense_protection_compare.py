from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


REPORT_DIR = Path(r"E:\科研\超粒球RAG_数据\reports")
OUT_CSV = REPORT_DIR / "stage2_dense_protection_compare.csv"
OUT_REPORT = Path(r"E:\科研\超粒球RAG_Stage2C_Dense保护策略报告.md")

STRATEGIES = {
    "original": "stage2_dense_allminilm",
    "fill": "stage2_dense_allminilm_fill",
    "merge": "stage2_dense_allminilm_merge",
    "protect10_fill": "stage2_dense_allminilm_protect10",
}
METHODS = ["fixed", "ball", "facet", "gated"]
DATASETS = ["ALL", "hotpotqa", "musique"]
METRICS = [
    "avg_mrr",
    "evidence_recall_at_10",
    "chain_recall_at_10",
    "evidence_recall_at_20",
    "chain_recall_at_20",
    "context_units_at_20",
    "hyperedge_rate",
    "expansion_yield",
    "false_expansion_rate",
]


def f(value: Any) -> float:
    return float(value)


def load_summary(prefix: str, method: str) -> dict[str, dict[str, str]]:
    path = REPORT_DIR / f"{prefix}_{method}_summary.csv"
    with path.open("r", encoding="utf-8", newline="") as stream:
        return {row["dataset"]: row for row in csv.DictReader(stream)}


def load_details(prefix: str, method: str) -> list[dict[str, Any]]:
    path = REPORT_DIR / f"{prefix}_{method}_details.jsonl"
    rows = []
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def query_delta_counts(base_rows: list[dict[str, Any]], test_rows: list[dict[str, Any]], metric: str) -> dict[str, int]:
    base = {row["query_id"]: float(row[metric]) for row in base_rows}
    counts = {"improved": 0, "same": 0, "regressed": 0}
    for row in test_rows:
        delta = float(row[metric]) - base[row["query_id"]]
        if delta > 1e-9:
            counts["improved"] += 1
        elif delta < -1e-9:
            counts["regressed"] += 1
        else:
            counts["same"] += 1
    return counts


def main() -> None:
    summaries = {
        strategy: {method: load_summary(prefix, method) for method in METHODS}
        for strategy, prefix in STRATEGIES.items()
    }
    base_fixed = summaries["original"]["fixed"]

    fields = ["strategy", "method", "dataset"] + METRICS + [
        "delta_er10_vs_original_fixed",
        "delta_cr10_vs_original_fixed",
        "delta_er20_vs_original_fixed",
        "delta_cr20_vs_original_fixed",
    ]
    rows = []
    for strategy in STRATEGIES:
        for method in METHODS:
            for dataset in DATASETS:
                item = summaries[strategy][method][dataset]
                base = base_fixed[dataset]
                row = {
                    "strategy": strategy,
                    "method": method,
                    "dataset": dataset,
                    **{metric: item[metric] for metric in METRICS},
                    "delta_er10_vs_original_fixed": f(item["evidence_recall_at_10"]) - f(base["evidence_recall_at_10"]),
                    "delta_cr10_vs_original_fixed": f(item["chain_recall_at_10"]) - f(base["chain_recall_at_10"]),
                    "delta_er20_vs_original_fixed": f(item["evidence_recall_at_20"]) - f(base["evidence_recall_at_20"]),
                    "delta_cr20_vs_original_fixed": f(item["chain_recall_at_20"]) - f(base["chain_recall_at_20"]),
                }
                rows.append(row)

    with OUT_CSV.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    original_fixed_details = load_details(STRATEGIES["original"], "fixed")
    query_counts = {}
    for strategy in ["fill", "merge", "protect10_fill"]:
        for method in ["facet", "gated"]:
            details = load_details(STRATEGIES[strategy], method)
            query_counts[(strategy, method, "cr10")] = query_delta_counts(original_fixed_details, details, "chain_recall_at_10")
            query_counts[(strategy, method, "cr20")] = query_delta_counts(original_fixed_details, details, "chain_recall_at_20")

    def metric_line(strategy: str, method: str) -> str:
        item = summaries[strategy][method]["ALL"]
        return (
            f"| {strategy} | {method} | {f(item['evidence_recall_at_10']):.4f} | "
            f"{f(item['chain_recall_at_10']):.4f} | {f(item['evidence_recall_at_20']):.4f} | "
            f"{f(item['chain_recall_at_20']):.4f} | {f(item['context_units_at_20']):.4f} | "
            f"{f(item['false_expansion_rate']):.4f} | {f(item['chain_recall_at_10']) - f(base_fixed['ALL']['chain_recall_at_10']):+.4f} | "
            f"{f(item['chain_recall_at_20']) - f(base_fixed['ALL']['chain_recall_at_20']):+.4f} |"
        )

    lines = [
        "# Stage2C Dense Protection Strategy Report",
        "",
        "## Material Passport",
        "",
        "- Stage: Stage2C dense protection recalibration",
        "- Corpus: HotpotQA sample200 + MuSiQue sample200, 400 queries, 12,304 candidate units",
        "- Embedding cache: `E:\\科研\\超粒球RAG_数据\\processed\\stage2_dense_allminilm_embeddings.npz`",
        "- Gold labels used for indexing: No",
        "- Generator used: No",
        "- Scripts changed: `E:\\科研\\超粒球RAG_实验脚本\\stage2_dense_replication.py`",
        "- New comparison script: `E:\\科研\\超粒球RAG_实验脚本\\stage2_dense_protection_compare.py`",
        "- Environment note: runs completed with the same NumPy/numexpr/pandas compatibility warnings observed in Stage2B.",
        "",
        "## ALL Metrics",
        "",
        "| Strategy | Method | ER@10 | CR@10 | ER@20 | CR@20 | Ctx@20 | False expansion | Delta CR@10 vs dense_fixed | Delta CR@20 vs dense_fixed |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for strategy, method in [
        ("original", "fixed"),
        ("original", "facet"),
        ("original", "gated"),
        ("fill", "facet"),
        ("fill", "gated"),
        ("merge", "facet"),
        ("merge", "gated"),
        ("protect10_fill", "facet"),
        ("protect10_fill", "gated"),
    ]:
        lines.append(metric_line(strategy, method))

    lines.extend([
        "",
        "## Query-Level Delta Counts vs Original Dense Fixed",
        "",
        "| Strategy | Method | Metric | Improved | Same | Regressed |",
        "|---|---|---|---:|---:|---:|",
    ])
    for strategy in ["fill", "merge", "protect10_fill"]:
        for method in ["facet", "gated"]:
            for metric in ["cr10", "cr20"]:
                counts = query_counts[(strategy, method, metric)]
                lines.append(
                    f"| {strategy} | {method} | {metric.upper()} | "
                    f"{counts['improved']} | {counts['same']} | {counts['regressed']} |"
                )

    lines.extend([
        "",
        "## Evidence-Grounded Reading",
        "",
        "- `merge-fixed` at ER/CR@10 and @20 is identical to original dense fixed in ALL metrics, because selected hyperedge units are merged and then re-sorted by the same dense score.",
        "- `fill-with-fixed` repairs the Stage2B truncation problem: context_units@20 becomes 19.965 for ball/facet/gated instead of the earlier ball-only 7.9225.",
        "- `fill + facet` gives the strongest ALL recall here: CR@10 0.5925 and CR@20 0.9000, but its false expansion rate is 0.9054.",
        "- `fill + gated` reduces false expansion to 0.8857 and keeps CR@20 at 0.8900, but CR@10 is only 0.5650, barely above dense_fixed 0.5625.",
        "- `protect10 + fill` forces Top-10 to match dense_fixed, so CR@10 cannot show hyperedge gains; its value is mainly in Top-20 evidence completion.",
        "",
        "## Next Gate",
        "",
        "Stage2C supports a narrower claim: dense-space hyperedge expansion is useful as a protected Top-20 supplement, not as a replacement for dense fixed Top-10 ranking. The next experiment should test a reranking rule that inserts only high-confidence expanded units into ranks 6-20, then reports budgeted context performance at K=10/15/20.",
    ])
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
