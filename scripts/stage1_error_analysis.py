import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(r"E:\科研")
PROCESSED_DIR = ROOT / "超粒球RAG_数据" / "processed"
REPORT_DIR = ROOT / "超粒球RAG_数据" / "reports"


QUERY_PATH = PROCESSED_DIR / "stage1_sample400_queries.jsonl"
BASELINE_PATH = PROCESSED_DIR / "stage1_tfidf_details.jsonl"
METHOD_PATH = PROCESSED_DIR / "stage1_facet_fill_e2_b2_s010_details.jsonl"
CSV_PATH = REPORT_DIR / "stage1_error_analysis_facet_vs_tfidf.csv"
MD_PATH = ROOT / "超粒球RAG_Stage1错误分析报告.md"


def read_jsonl(path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def by_id(rows):
    return {row["query_id"]: row for row in rows}


def f(row, key):
    return float(row.get(key, 0.0))


def titles(row, limit=10):
    return " / ".join(unit.get("title", "") for unit in row.get("top_units", [])[:limit])


def gold_titles(row, limit=10):
    hits = []
    for unit in row.get("top_units", [])[:limit]:
        if unit.get("is_gold"):
            hits.append(f'{unit.get("rank")}:{unit.get("title", "")}')
    return " / ".join(hits)


def relation(method_value, base_value):
    if method_value > base_value:
        return "improved"
    if method_value < base_value:
        return "regressed"
    return "same"


def compact(text, max_len=140):
    text = " ".join(str(text).split())
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def main():
    queries = by_id(read_jsonl(QUERY_PATH))
    baseline = by_id(read_jsonl(BASELINE_PATH))
    method = by_id(read_jsonl(METHOD_PATH))

    if set(baseline) != set(method):
        missing_base = sorted(set(method) - set(baseline))[:5]
        missing_method = sorted(set(baseline) - set(method))[:5]
        raise ValueError(f"Detail files do not align. missing_base={missing_base} missing_method={missing_method}")

    rows = []
    for query_id in sorted(baseline):
        q = queries.get(query_id, {})
        b = baseline[query_id]
        m = method[query_id]
        row = {
            "query_id": query_id,
            "dataset": b["dataset"],
            "question": q.get("question", ""),
            "answer": q.get("answer", ""),
            "num_gold": b.get("num_gold", ""),
            "base_er5": f(b, "evidence_recall_at_5"),
            "facet_er5": f(m, "evidence_recall_at_5"),
            "delta_er5": f(m, "evidence_recall_at_5") - f(b, "evidence_recall_at_5"),
            "base_cr5": f(b, "chain_recall_at_5"),
            "facet_cr5": f(m, "chain_recall_at_5"),
            "delta_cr5": f(m, "chain_recall_at_5") - f(b, "chain_recall_at_5"),
            "base_er10": f(b, "evidence_recall_at_10"),
            "facet_er10": f(m, "evidence_recall_at_10"),
            "delta_er10": f(m, "evidence_recall_at_10") - f(b, "evidence_recall_at_10"),
            "base_cr10": f(b, "chain_recall_at_10"),
            "facet_cr10": f(m, "chain_recall_at_10"),
            "delta_cr10": f(m, "chain_recall_at_10") - f(b, "chain_recall_at_10"),
            "chain10_relation": relation(f(m, "chain_recall_at_10"), f(b, "chain_recall_at_10")),
            "evidence10_relation": relation(f(m, "evidence_recall_at_10"), f(b, "evidence_recall_at_10")),
            "base_gold_hits_top10": gold_titles(b, 10),
            "facet_gold_hits_top10": gold_titles(m, 10),
            "base_top_titles": titles(b, 10),
            "facet_top_titles": titles(m, 10),
            "is_boundary": m.get("is_boundary", ""),
            "seed_ball_count": m.get("seed_ball_count", ""),
            "expanded_ball_count": m.get("expanded_ball_count", ""),
            "selected_edge_count": m.get("selected_edge_count", ""),
            "query_facet_count": m.get("query_facet_count", ""),
            "seed_facet_count": m.get("seed_facet_count", ""),
            "final_facet_count": m.get("final_facet_count", ""),
            "expansion_gold_units": m.get("expansion_gold_units", ""),
            "expansion_non_gold_units": m.get("expansion_non_gold_units", ""),
        }
        rows.append(row)

    fieldnames = list(rows[0].keys())
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    counts = defaultdict(Counter)
    for row in rows:
        dataset = row["dataset"]
        for scope in [dataset, "ALL"]:
            counts[(scope, "chain10")][row["chain10_relation"]] += 1
            counts[(scope, "evidence10")][row["evidence10_relation"]] += 1

    improved_chain = [r for r in rows if r["chain10_relation"] == "improved"]
    regressed_chain = [r for r in rows if r["chain10_relation"] == "regressed"]
    improved_evidence = sorted([r for r in rows if r["delta_er10"] > 0], key=lambda r: r["delta_er10"], reverse=True)
    regressed_evidence = sorted([r for r in rows if r["delta_er10"] < 0], key=lambda r: r["delta_er10"])

    def case_table(case_rows, title, max_cases=6):
        lines = [f"### {title}", ""]
        if not case_rows:
            lines.append("未发现该类样例。")
            lines.append("")
            return lines
        lines.append("| 数据集 | Query ID | 问题 | TF-IDF gold@10 | Facet gold@10 | ΔER@10 | ΔCR@10 | 扩展gold/non-gold |")
        lines.append("|---|---|---|---|---|---:|---:|---:|")
        for row in case_rows[:max_cases]:
            lines.append(
                "| {dataset} | `{qid}` | {question} | {base_hits} | {facet_hits} | {der:.4f} | {dcr:.4f} | {eg}/{en} |".format(
                    dataset=row["dataset"],
                    qid=row["query_id"],
                    question=compact(row["question"]),
                    base_hits=row["base_gold_hits_top10"] or "-",
                    facet_hits=row["facet_gold_hits_top10"] or "-",
                    der=row["delta_er10"],
                    dcr=row["delta_cr10"],
                    eg=row["expansion_gold_units"],
                    en=row["expansion_non_gold_units"],
                )
            )
        lines.append("")
        return lines

    lines = []
    lines.append("# 超粒球RAG Stage1 错误分析报告")
    lines.append("")
    lines.append("## Material Passport")
    lines.append("")
    lines.append("- Artifact: Stage1 error analysis")
    lines.append("- Status: ANALYZED")
    lines.append("- Baseline: Fixed TF-IDF sentence unit")
    lines.append("- Compared method: Facet-aware hyperedge expansion, e2/b2/s010")
    lines.append("- Unit of analysis: 400 queries from HotpotQA sample200 + MuSiQue sample200")
    lines.append("- Generated by: stage1_error_analysis.py")
    lines.append("")
    lines.append("## 数量统计")
    lines.append("")
    lines.append("| 数据集 | Chain@10 improved | Chain@10 same | Chain@10 regressed | ER@10 improved | ER@10 same | ER@10 regressed |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for dataset in ["ALL", "hotpotqa", "musique"]:
        c_chain = counts[(dataset, "chain10")]
        c_er = counts[(dataset, "evidence10")]
        lines.append(
            f"| {dataset} | {c_chain['improved']} | {c_chain['same']} | {c_chain['regressed']} | "
            f"{c_er['improved']} | {c_er['same']} | {c_er['regressed']} |"
        )
    lines.append("")
    lines.append("## 读数")
    lines.append("")
    lines.append("- Chain@10 层面：Facet-aware 相比 fixed TF-IDF 有改进样例，也有退化样例；净收益来自改进数和改进幅度覆盖退化。")
    lines.append("- ER@10 层面：对 MuSiQue 的收益更集中，和 Stage1 总消融表中的 MuSiQue CR@10 提升一致。")
    lines.append("- 机制层面：报告中的 `扩展gold/non-gold` 可以直接定位超边扩展的噪声来源；当前 false expansion 仍高，因此后续要减少 non-gold expansion。")
    lines.append("")
    lines.extend(case_table(improved_chain, "Chain@10 改进样例"))
    lines.extend(case_table(regressed_chain, "Chain@10 退化样例"))
    lines.extend(case_table(improved_evidence, "ER@10 改进幅度最大的样例"))
    lines.extend(case_table(regressed_evidence, "ER@10 退化幅度最大的样例"))
    lines.append("## 输出文件")
    lines.append("")
    lines.append(f"- Per-query CSV: `{CSV_PATH}`")
    lines.append("")
    MD_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {CSV_PATH}")
    print(f"Wrote {MD_PATH}")
    print("Counts:")
    for dataset in ["ALL", "hotpotqa", "musique"]:
        print(dataset, "chain10", dict(counts[(dataset, "chain10")]), "evidence10", dict(counts[(dataset, "evidence10")]))


if __name__ == "__main__":
    main()
