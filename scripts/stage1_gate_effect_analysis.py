import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(r"E:\科研")
PROCESSED_DIR = ROOT / "超粒球RAG_数据" / "processed"
REPORT_DIR = ROOT / "超粒球RAG_数据" / "reports"

QUERY_PATH = PROCESSED_DIR / "stage1_sample400_queries.jsonl"
STAGE1E_DETAILS = PROCESSED_DIR / "stage1_facet_fill_e2_b2_s010_details.jsonl"
STAGE1E_EDGES = PROCESSED_DIR / "stage1_facet_fill_e2_b2_s010_edges.jsonl"
STAGE1F_DETAILS = PROCESSED_DIR / "stage1_fg_boundary_size8_score12_details.jsonl"
STAGE1F_EDGES = PROCESSED_DIR / "stage1_fg_boundary_size8_score12_edges.jsonl"

CSV_PATH = REPORT_DIR / "stage1_gate_effect_analysis.csv"
MD_PATH = ROOT / "超粒球RAG_Stage1G门控效应分析.md"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["query_id"]: row for row in rows}


def edge_groups(path: Path) -> dict[str, dict[str, dict[str, Any]]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for edge in read_jsonl(path):
        query_id = edge["query_id"]
        for ball_id in edge.get("accepted_ball_ids", []):
            grouped[query_id][ball_id] = edge
    return grouped


def f(row: dict[str, Any], key: str) -> float:
    return float(row.get(key, 0.0))


def compact(text: str, limit: int = 135) -> str:
    text = " ".join(str(text).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def titles(row: dict[str, Any], limit: int = 10) -> str:
    hits = []
    for unit in row.get("top_units", [])[:limit]:
        if unit.get("is_gold"):
            hits.append(f'{unit.get("rank")}:{unit.get("title", "")}')
    return " / ".join(hits)


def edge_stats(edges: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "count": len(edges),
        "gold_sum": sum(int(edge.get("gold_units", 0)) for edge in edges),
        "zero_gold": sum(1 for edge in edges if int(edge.get("gold_units", 0)) == 0),
        "terms": "; ".join(
            ",".join(edge.get("new_terms", [])[:4])
            for edge in edges[:4]
            if edge.get("new_terms")
        ),
    }


def relation(after: float, before: float) -> str:
    if after > before:
        return "improved"
    if after < before:
        return "regressed"
    return "same"


def main() -> None:
    queries = by_id(read_jsonl(QUERY_PATH))
    e_details = by_id(read_jsonl(STAGE1E_DETAILS))
    f_details = by_id(read_jsonl(STAGE1F_DETAILS))
    e_edges = edge_groups(STAGE1E_EDGES)
    f_edges = edge_groups(STAGE1F_EDGES)

    if set(e_details) != set(f_details):
        raise ValueError("Stage1E and Stage1F detail query ids do not align.")

    rows: list[dict[str, Any]] = []
    for query_id in sorted(e_details):
        e_row = e_details[query_id]
        f_row = f_details[query_id]
        q = queries.get(query_id, {})
        e_ball_ids = set(e_edges.get(query_id, {}))
        f_ball_ids = set(f_edges.get(query_id, {}))
        kept_edges = [e_edges[query_id][ball_id] for ball_id in sorted(e_ball_ids & f_ball_ids)] if query_id in e_edges else []
        blocked_edges = [e_edges[query_id][ball_id] for ball_id in sorted(e_ball_ids - f_ball_ids)] if query_id in e_edges else []
        added_edges = [f_edges[query_id][ball_id] for ball_id in sorted(f_ball_ids - e_ball_ids)] if query_id in f_edges else []
        kept = edge_stats(kept_edges)
        blocked = edge_stats(blocked_edges)
        added = edge_stats(added_edges)

        delta_non_gold = int(f_row.get("expansion_non_gold_units", 0)) - int(e_row.get("expansion_non_gold_units", 0))
        delta_gold = int(f_row.get("expansion_gold_units", 0)) - int(e_row.get("expansion_gold_units", 0))
        delta_units = int(f_row.get("expansion_units", 0)) - int(e_row.get("expansion_units", 0))
        delta_cr10 = f(f_row, "chain_recall_at_10") - f(e_row, "chain_recall_at_10")
        delta_er10 = f(f_row, "evidence_recall_at_10") - f(e_row, "evidence_recall_at_10")

        if delta_non_gold < 0 and delta_gold == 0 and delta_cr10 >= 0:
            effect_class = "clean_noise_prune"
        elif delta_non_gold < 0 and delta_cr10 >= 0:
            effect_class = "noise_prune_with_gold_change"
        elif delta_cr10 < 0:
            effect_class = "retrieval_regression"
        elif delta_cr10 > 0:
            effect_class = "retrieval_improvement"
        elif delta_non_gold == 0 and delta_gold == 0:
            effect_class = "unchanged"
        else:
            effect_class = "mixed"

        rows.append(
            {
                "query_id": query_id,
                "dataset": e_row["dataset"],
                "question": q.get("question", ""),
                "answer": q.get("answer", ""),
                "effect_class": effect_class,
                "stage1e_edges": len(e_ball_ids),
                "stage1f_edges": len(f_ball_ids),
                "kept_edges": kept["count"],
                "blocked_edges": blocked["count"],
                "blocked_zero_gold_edges": blocked["zero_gold"],
                "blocked_gold_units": blocked["gold_sum"],
                "added_edges": added["count"],
                "added_zero_gold_edges": added["zero_gold"],
                "added_gold_units": added["gold_sum"],
                "blocked_new_terms": blocked["terms"],
                "added_new_terms": added["terms"],
                "stage1e_expansion_units": e_row.get("expansion_units", 0),
                "stage1f_expansion_units": f_row.get("expansion_units", 0),
                "delta_expansion_units": delta_units,
                "stage1e_expansion_gold_units": e_row.get("expansion_gold_units", 0),
                "stage1f_expansion_gold_units": f_row.get("expansion_gold_units", 0),
                "delta_expansion_gold_units": delta_gold,
                "stage1e_expansion_non_gold_units": e_row.get("expansion_non_gold_units", 0),
                "stage1f_expansion_non_gold_units": f_row.get("expansion_non_gold_units", 0),
                "delta_expansion_non_gold_units": delta_non_gold,
                "stage1e_er10": f(e_row, "evidence_recall_at_10"),
                "stage1f_er10": f(f_row, "evidence_recall_at_10"),
                "delta_er10": delta_er10,
                "stage1e_cr10": f(e_row, "chain_recall_at_10"),
                "stage1f_cr10": f(f_row, "chain_recall_at_10"),
                "delta_cr10": delta_cr10,
                "stage1e_gold_hits_top10": titles(e_row),
                "stage1f_gold_hits_top10": titles(f_row),
                "gate_reject_size": f_row.get("gate_reject_size", 0),
                "gate_reject_anchor": f_row.get("gate_reject_anchor", 0),
                "gate_reject_ratio": f_row.get("gate_reject_ratio", 0),
                "gate_reject_score": f_row.get("gate_reject_score", 0),
            }
        )

    with CSV_PATH.open("w", encoding="utf-8", newline="") as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    class_counts: dict[str, Counter[str]] = defaultdict(Counter)
    relation_counts: dict[str, Counter[str]] = defaultdict(Counter)
    sums: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        dataset = row["dataset"]
        for scope in [dataset, "ALL"]:
            class_counts[scope][row["effect_class"]] += 1
            relation_counts[scope][relation(float(row["stage1f_cr10"]), float(row["stage1e_cr10"]))] += 1
            sums[scope]["stage1e_edges"] += int(row["stage1e_edges"])
            sums[scope]["stage1f_edges"] += int(row["stage1f_edges"])
            sums[scope]["blocked_edges"] += int(row["blocked_edges"])
            sums[scope]["blocked_zero_gold_edges"] += int(row["blocked_zero_gold_edges"])
            sums[scope]["blocked_gold_units"] += int(row["blocked_gold_units"])
            sums[scope]["added_edges"] += int(row["added_edges"])
            sums[scope]["added_zero_gold_edges"] += int(row["added_zero_gold_edges"])
            sums[scope]["added_gold_units"] += int(row["added_gold_units"])
            sums[scope]["delta_expansion_units"] += int(row["delta_expansion_units"])
            sums[scope]["delta_expansion_gold_units"] += int(row["delta_expansion_gold_units"])
            sums[scope]["delta_expansion_non_gold_units"] += int(row["delta_expansion_non_gold_units"])
            sums[scope]["gate_reject_size"] += int(row["gate_reject_size"])
            sums[scope]["gate_reject_anchor"] += int(row["gate_reject_anchor"])
            sums[scope]["gate_reject_ratio"] += int(row["gate_reject_ratio"])
            sums[scope]["gate_reject_score"] += int(row["gate_reject_score"])

    def case_table(case_rows: list[dict[str, Any]], title: str, limit: int = 6) -> list[str]:
        lines = [f"### {title}", ""]
        if not case_rows:
            lines.extend(["未发现该类样例。", ""])
            return lines
        lines.append("| 数据集 | Query ID | 问题 | Δnon-gold | Δgold | ΔER@10 | ΔCR@10 | blocked gold/zero | E gold@10 | F gold@10 |")
        lines.append("|---|---|---|---:|---:|---:|---:|---:|---|---|")
        for row in case_rows[:limit]:
            lines.append(
                "| {dataset} | `{qid}` | {question} | {dng} | {dg} | {der:.4f} | {dcr:.4f} | {bg}/{bz} | {egold} | {fgold} |".format(
                    dataset=row["dataset"],
                    qid=row["query_id"],
                    question=compact(row["question"]),
                    dng=row["delta_expansion_non_gold_units"],
                    dg=row["delta_expansion_gold_units"],
                    der=float(row["delta_er10"]),
                    dcr=float(row["delta_cr10"]),
                    bg=row["blocked_gold_units"],
                    bz=row["blocked_zero_gold_edges"],
                    egold=row["stage1e_gold_hits_top10"] or "-",
                    fgold=row["stage1f_gold_hits_top10"] or "-",
                )
            )
        lines.append("")
        return lines

    clean_prunes = sorted(
        [row for row in rows if row["effect_class"] == "clean_noise_prune"],
        key=lambda row: int(row["delta_expansion_non_gold_units"]),
    )
    regressions = sorted(
        [row for row in rows if row["effect_class"] == "retrieval_regression"],
        key=lambda row: (float(row["delta_cr10"]), float(row["delta_er10"])),
    )
    improvements = sorted(
        [row for row in rows if row["effect_class"] == "retrieval_improvement"],
        key=lambda row: (-float(row["delta_cr10"]), -float(row["delta_er10"])),
    )
    gold_prunes = sorted(
        [row for row in rows if int(row["delta_expansion_gold_units"]) < 0],
        key=lambda row: (int(row["delta_expansion_gold_units"]), float(row["delta_cr10"])),
    )

    lines = [
        "# 超粒球RAG Stage1G 门控效应分析",
        "",
        "## Material Passport",
        "",
        "- Artifact: Stage1G gate-effect analysis",
        "- Status: ANALYZED",
        "- Compared methods: Stage1E facet-aware e2/b2/s010 vs Stage1F boundary-only size8 score12",
        "- Unit of analysis: 400 aligned queries",
        "- Gold labels used for indexing: No; gold labels used for post-hoc evaluation only",
        "- Generated by: stage1_gate_effect_analysis.py",
        "",
        "## 总体门控效果",
        "",
        "| 数据集 | E edges | F edges | blocked | blocked zero-gold | blocked gold units | added | added zero-gold | added gold units | Δexp units | Δgold units | Δnon-gold units |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for dataset in ["ALL", "hotpotqa", "musique"]:
        item = sums[dataset]
        lines.append(
            f"| {dataset} | {item['stage1e_edges']} | {item['stage1f_edges']} | {item['blocked_edges']} | "
            f"{item['blocked_zero_gold_edges']} | {item['blocked_gold_units']} | {item['added_edges']} | "
            f"{item['added_zero_gold_edges']} | {item['added_gold_units']} | {item['delta_expansion_units']} | "
            f"{item['delta_expansion_gold_units']} | {item['delta_expansion_non_gold_units']} |"
        )

    lines.extend(
        [
            "",
            "## Query 级分类",
            "",
            "| 数据集 | clean noise prune | noise prune with gold change | unchanged | mixed | retrieval improvement | retrieval regression |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for dataset in ["ALL", "hotpotqa", "musique"]:
        c = class_counts[dataset]
        lines.append(
            f"| {dataset} | {c['clean_noise_prune']} | {c['noise_prune_with_gold_change']} | {c['unchanged']} | "
            f"{c['mixed']} | {c['retrieval_improvement']} | {c['retrieval_regression']} |"
        )

    lines.extend(
        [
            "",
            "## CR@10 变化",
            "",
            "| 数据集 | improved | same | regressed |",
            "|---|---:|---:|---:|",
        ]
    )
    for dataset in ["ALL", "hotpotqa", "musique"]:
        c = relation_counts[dataset]
        lines.append(f"| {dataset} | {c['improved']} | {c['same']} | {c['regressed']} |")

    lines.extend(
        [
            "",
            "## 门控拒绝原因累计",
            "",
            "| 数据集 | size | anchor | ratio | score |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for dataset in ["ALL", "hotpotqa", "musique"]:
        item = sums[dataset]
        lines.append(
            f"| {dataset} | {item['gate_reject_size']} | {item['gate_reject_anchor']} | "
            f"{item['gate_reject_ratio']} | {item['gate_reject_score']} |"
        )

    all_sum = sums["ALL"]
    hotpot_sum = sums["hotpotqa"]
    musique_sum = sums["musique"]
    net_edge_change = all_sum["stage1f_edges"] - all_sum["stage1e_edges"]
    nongold_per_gold = abs(all_sum["delta_expansion_non_gold_units"]) / max(abs(all_sum["delta_expansion_gold_units"]), 1)
    lines.extend(
        [
            "",
            "## 证据解读",
            "",
            f"- Stage1F 相比 Stage1E 净变化为 {net_edge_change} 条扩展边；具体是 blocked {all_sum['blocked_edges']} 条、added {all_sum['added_edges']} 条，因此它是“过滤+替换”，不是简单截断。",
            f"- ALL 层面 expansion units 减少 {abs(all_sum['delta_expansion_units'])}，其中 non-gold units 减少 {abs(all_sum['delta_expansion_non_gold_units'])}，gold units 也减少 {abs(all_sum['delta_expansion_gold_units'])}。",
            f"- 以扩展单元计，当前门控大约每减少 1 个 gold expansion，同时减少 {nongold_per_gold:.2f} 个 non-gold expansion；这是有效降噪，但不是零代价降噪。",
            f"- HotpotQA: non-gold units 减少 {abs(hotpot_sum['delta_expansion_non_gold_units'])}，gold units 减少 {abs(hotpot_sum['delta_expansion_gold_units'])}；CR@10 improved/regressed 均为 {relation_counts['hotpotqa']['improved']}/{relation_counts['hotpotqa']['regressed']}，说明局部进退相抵。",
            f"- MuSiQue: non-gold units 减少 {abs(musique_sum['delta_expansion_non_gold_units'])}，gold units 减少 {abs(musique_sum['delta_expansion_gold_units'])}；CR@10 improved/regressed 为 {relation_counts['musique']['improved']}/{relation_counts['musique']['regressed']}，所以链路召回整体保持稳定。",
            "- 可支持的结论：Stage1F 的门控明显降低扩展噪声，并保持聚合 CR@10；但它仍会误伤部分 gold 扩展，后续需要研究 gold-preserving gate，而不是宣称门控无损。",
            "",
        ]
    )
    lines.extend(case_table(clean_prunes, "干净降噪样例"))
    lines.extend(case_table(gold_prunes, "可能误伤 gold 扩展的样例"))
    lines.extend(case_table(improvements, "Stage1F 相比 Stage1E 的检索改进样例"))
    lines.extend(case_table(regressions, "Stage1F 相比 Stage1E 的检索退化样例"))
    lines.extend(
        [
            "## 输出文件",
            "",
            f"- Per-query CSV: `{CSV_PATH}`",
            "",
        ]
    )
    MD_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {CSV_PATH}")
    print(f"Wrote {MD_PATH}")
    print("Class counts:")
    for dataset in ["ALL", "hotpotqa", "musique"]:
        print(dataset, dict(class_counts[dataset]), "cr10", dict(relation_counts[dataset]), "sums", dict(sums[dataset]))


if __name__ == "__main__":
    main()
