import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(r"E:\科研")
PROCESSED_DIR = ROOT / "超粒球RAG_数据" / "processed"
REPORT_DIR = ROOT / "超粒球RAG_数据" / "reports"

E_EDGES = PROCESSED_DIR / "stage1_facet_fill_e2_b2_s010_edges.jsonl"
F_EDGES = PROCESSED_DIR / "stage1_fg_boundary_size8_score12_edges.jsonl"
CSV_PATH = REPORT_DIR / "stage1_gate_edge_audit.csv"
MD_PATH = ROOT / "超粒球RAG_Stage1G边级审计.md"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def edge_key(edge: dict[str, Any]) -> tuple[str, str]:
    return edge["query_id"], edge["accepted_ball_ids"][0]


def f(edge: dict[str, Any], key: str) -> float:
    value = edge.get(key)
    if value is None or value == "":
        return 0.0
    return float(value)


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def avg(key: str) -> float:
        values = [f(row, key) for row in rows]
        return mean(values) if values else 0.0

    return {
        "edges": len(rows),
        "zero_gold_edges": sum(1 for row in rows if int(row.get("gold_units", 0)) == 0),
        "gold_edges": sum(1 for row in rows if int(row.get("gold_units", 0)) > 0),
        "gold_units": sum(int(row.get("gold_units", 0)) for row in rows),
        "avg_new_terms": mean([len(row.get("new_terms", [])) for row in rows]) if rows else 0.0,
        "avg_shared_terms": mean([len(row.get("shared_terms", [])) for row in rows]) if rows else 0.0,
        "avg_ball_score": avg("ball_score"),
        "avg_facet_score": avg("facet_score"),
        "avg_diversity": avg("diversity"),
        "avg_redundancy": avg("redundancy"),
        "avg_ball_size": avg("ball_size"),
        "avg_units_per_new_term": avg("units_per_new_term"),
        "avg_max_seed_similarity": avg("max_seed_similarity"),
    }


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def main() -> None:
    e_edges = read_jsonl(E_EDGES)
    f_edges = read_jsonl(F_EDGES)
    f_by_key = {edge_key(edge): edge for edge in f_edges}
    e_by_key = {edge_key(edge): edge for edge in e_edges}

    rows: list[dict[str, Any]] = []
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in e_edges:
        key = edge_key(edge)
        status = "e_kept" if key in f_by_key else "e_blocked"
        gold_class = "gold" if int(edge.get("gold_units", 0)) > 0 else "zero_gold"
        row = {
            "status": status,
            "gold_class": gold_class,
            "query_id": edge["query_id"],
            "ball_id": key[1],
            "gold_units": int(edge.get("gold_units", 0)),
            "new_terms_count": len(edge.get("new_terms", [])),
            "shared_terms_count": len(edge.get("shared_terms", [])),
            "ball_score": f(edge, "ball_score"),
            "facet_score": f(edge, "facet_score"),
            "diversity": f(edge, "diversity"),
            "redundancy": f(edge, "redundancy"),
            "new_terms": ",".join(edge.get("new_terms", [])),
        }
        rows.append(row)
        groups[f"{status}:{gold_class}"].append(edge)
        groups[status].append(edge)

    for edge in f_edges:
        key = edge_key(edge)
        if key in e_by_key:
            continue
        gold_class = "gold" if int(edge.get("gold_units", 0)) > 0 else "zero_gold"
        row = {
            "status": "f_added",
            "gold_class": gold_class,
            "query_id": edge["query_id"],
            "ball_id": key[1],
            "gold_units": int(edge.get("gold_units", 0)),
            "new_terms_count": len(edge.get("new_terms", [])),
            "shared_terms_count": len(edge.get("shared_terms", [])),
            "ball_score": f(edge, "ball_score"),
            "facet_score": f(edge, "facet_score"),
            "diversity": f(edge, "diversity"),
            "redundancy": f(edge, "redundancy"),
            "ball_size": f(edge, "ball_size"),
            "units_per_new_term": f(edge, "units_per_new_term"),
            "max_seed_similarity": f(edge, "max_seed_similarity"),
            "new_terms": ",".join(edge.get("new_terms", [])),
        }
        rows.append(row)
        groups[f"f_added:{gold_class}"].append(edge)
        groups["f_added"].append(edge)

    with CSV_PATH.open("w", encoding="utf-8", newline="") as f_csv:
        fieldnames = [
            "status",
            "gold_class",
            "query_id",
            "ball_id",
            "gold_units",
            "new_terms_count",
            "shared_terms_count",
            "ball_score",
            "facet_score",
            "diversity",
            "redundancy",
            "ball_size",
            "units_per_new_term",
            "max_seed_similarity",
            "new_terms",
        ]
        writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    summaries = {name: summarize(items) for name, items in groups.items()}
    status_counts = Counter(row["status"] for row in rows)
    gold_counts = Counter((row["status"], row["gold_class"]) for row in rows)

    lines = [
        "# 超粒球RAG Stage1G 边级审计",
        "",
        "## Material Passport",
        "",
        "- Artifact: Stage1G edge-level gate audit",
        "- Status: ANALYZED",
        "- Compared methods: Stage1E facet-aware e2/b2/s010 vs Stage1F boundary-only size8 score12",
        "- Unit of analysis: selected facet hyperedge candidate",
        "- Generated by: stage1_gate_edge_audit.py",
        "",
        "## 边状态计数",
        "",
        "| 状态 | 总边数 | zero-gold | gold | gold units |",
        "|---|---:|---:|---:|---:|",
    ]
    for status in ["e_kept", "e_blocked", "f_added"]:
        summary = summaries.get(status, summarize([]))
        lines.append(
            f"| {status} | {status_counts[status]} | {gold_counts[(status, 'zero_gold')]} | "
            f"{gold_counts[(status, 'gold')]} | {summary['gold_units']} |"
        )

    lines.extend(
        [
            "",
            "## 关键分布",
            "",
            "| 分组 | edges | zero-gold | gold units | avg new terms | avg ball score | avg facet score | avg redundancy | avg diversity | avg ball size | avg units/new term |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for name in [
        "e_kept",
        "e_blocked",
        "e_blocked:zero_gold",
        "e_blocked:gold",
        "f_added",
        "f_added:zero_gold",
        "f_added:gold",
    ]:
        summary = summaries.get(name, summarize([]))
        lines.append(
            "| {name} | {edges} | {zero} | {gold_units} | {new_terms} | {ball_score} | {facet_score} | {redundancy} | {diversity} | {ball_size} | {units_per_new} |".format(
                name=name,
                edges=summary["edges"],
                zero=summary["zero_gold_edges"],
                gold_units=summary["gold_units"],
                new_terms=fmt(summary["avg_new_terms"]),
                ball_score=fmt(summary["avg_ball_score"]),
                facet_score=fmt(summary["avg_facet_score"]),
                redundancy=fmt(summary["avg_redundancy"]),
                diversity=fmt(summary["avg_diversity"]),
                ball_size=fmt(summary["avg_ball_size"]),
                units_per_new=fmt(summary["avg_units_per_new_term"]),
            )
        )

    blocked_zero = summaries.get("e_blocked:zero_gold", summarize([]))
    blocked_gold = summaries.get("e_blocked:gold", summarize([]))
    kept = summaries.get("e_kept", summarize([]))
    lines.extend(
        [
            "",
            "## 证据解读",
            "",
            f"- 被 Stage1F 挡掉的 Stage1E 边共 {summaries['e_blocked']['edges']} 条，其中 zero-gold {blocked_zero['edges']} 条，gold {blocked_gold['edges']} 条。",
            f"- 被挡掉的 zero-gold 边 avg facet_score = {blocked_zero['avg_facet_score']:.4f}，被挡掉的 gold 边 avg facet_score = {blocked_gold['avg_facet_score']:.4f}；两者在 facet_score 上不可完全分开。",
            f"- 保留下来的 Stage1E 边 avg ball_score = {kept['avg_ball_score']:.4f}，被挡掉边 avg ball_score = {summaries['e_blocked']['avg_ball_score']:.4f}，说明 query-ball 锚定对过滤有实际作用。",
            f"- 新增的 Stage1F 边共 {summaries['f_added']['edges']} 条，其中 zero-gold {summaries['f_added:zero_gold']['edges']} 条、gold {summaries['f_added:gold']['edges']} 条；替换仍会引入噪声。",
            "- 当前证据支持加入 gold-preserving gate：只靠 score/size/ratio 门控可以降噪，但无法稳定区分 gold-bearing hyperedge 与 zero-gold hyperedge。",
            "",
            f"CSV output: `{CSV_PATH}`",
        ]
    )
    MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {CSV_PATH}")
    print(f"Wrote {MD_PATH}")
    print("Status counts:", dict(status_counts))
    print("Gold counts:", {str(key): value for key, value in gold_counts.items()})


if __name__ == "__main__":
    main()
