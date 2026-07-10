import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(r"E:\科研")
REPORT_DIR = ROOT / "超粒球RAG_数据" / "reports"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def pick(rows: list[dict[str, str]], **conds: str) -> dict[str, str]:
    for row in rows:
        if all(row.get(key) == value for key, value in conds.items()):
            return row
    raise KeyError(conds)


def f(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    if value == "":
        return 0.0
    return float(value)


def fmt(value: float) -> str:
    return f"{value:.4f}"


def main() -> None:
    ablation = read_csv(REPORT_DIR / "stage1_consolidated_ablation.csv")
    noise = read_csv(REPORT_DIR / "stage1_noise_gate_compare.csv")
    gate_effect = read_csv(REPORT_DIR / "stage1_gate_effect_analysis.csv")
    edge_audit = read_csv(REPORT_DIR / "stage1_gate_edge_audit.csv")
    gold_preserve = read_csv(REPORT_DIR / "stage1_gold_preserve_compare.csv")

    tfidf_all = pick(ablation, method_id="fixed_tfidf", dataset="ALL")
    gb_all = pick(ablation, method_id="gb_only", dataset="ALL")
    naive_he_all = pick(ablation, method_id="naive_hyperedge", dataset="ALL")
    query_he_all = pick(ablation, method_id="query_aware_hyperedge", dataset="ALL")
    facet_e_all = pick(ablation, method_id="facet_aware_hyperedge", dataset="ALL")
    facet_f_all = pick(noise, method_id="fg_boundary_size8_score12", dataset="ALL")
    facet_f_hotpot = pick(noise, method_id="fg_boundary_size8_score12", dataset="hotpotqa")
    facet_f_musique = pick(noise, method_id="fg_boundary_size8_score12", dataset="musique")
    stage1e_all = pick(noise, method_id="facet_e2_b2", dataset="ALL")
    gp_size12_all = pick(gold_preserve, method_id="gp_size12", dataset="ALL")
    gp_nonew020_all = pick(gold_preserve, method_id="gp_nonew020", dataset="ALL")

    effect_counts = Counter(row["effect_class"] for row in gate_effect)
    cr_counts = Counter()
    sums = defaultdict(int)
    for row in gate_effect:
        cr_delta = f(row, "stage1f_cr10") - f(row, "stage1e_cr10")
        if cr_delta > 0:
            cr_counts["improved"] += 1
        elif cr_delta < 0:
            cr_counts["regressed"] += 1
        else:
            cr_counts["same"] += 1
        for key in [
            "stage1e_edges",
            "stage1f_edges",
            "blocked_edges",
            "blocked_zero_gold_edges",
            "blocked_gold_units",
            "added_edges",
            "added_zero_gold_edges",
            "added_gold_units",
            "delta_expansion_units",
            "delta_expansion_gold_units",
            "delta_expansion_non_gold_units",
        ]:
            sums[key] += int(float(row[key]))

    edge_status = Counter(row["status"] for row in edge_audit)
    edge_gold = Counter((row["status"], row["gold_class"]) for row in edge_audit)

    claims = [
        {
            "claim_id": "C1",
            "claim": "Boundary-triggered, facet-aware hyperedge retrieval improves multi-hop chain recall over fixed TF-IDF retrieval in the current retrieval-only benchmark.",
            "evidence": f"ALL CR@10 {tfidf_all['chain_recall_at_10']} -> {facet_f_all['chain_recall_at_10']}; MuSiQue CR@10 {pick(ablation, method_id='fixed_tfidf', dataset='musique')['chain_recall_at_10']} -> {facet_f_musique['chain_recall_at_10']}.",
            "status": "supported",
            "caveat": "Only retrieval metrics on 400 sampled queries; no generator or answer accuracy yet.",
        },
        {
            "claim_id": "C2",
            "claim": "Adaptive granular balls alone are not sufficient; the useful gain comes from uncertainty-triggered cross-ball expansion and gating.",
            "evidence": f"Granular-ball-only ALL CR@10 = {gb_all['chain_recall_at_10']}, below fixed TF-IDF {tfidf_all['chain_recall_at_10']}; Stage1F best ALL CR@10 = {facet_f_all['chain_recall_at_10']}.",
            "status": "supported",
            "caveat": "Granular-ball construction is still TF-IDF based; embedding-based balls are untested.",
        },
        {
            "claim_id": "C3",
            "claim": "Facet-aware expansion is better motivated than query-aware ranking alone because it preserves chain recall while reducing expansion noise.",
            "evidence": f"Query-aware ALL CR@10 = {query_he_all['chain_recall_at_10']}; Stage1E facet-aware ALL CR@10 = {facet_e_all['chain_recall_at_10']}; Stage1F false expansion {stage1e_all['false_expansion_rate']} -> {facet_f_all['false_expansion_rate']}.",
            "status": "supported",
            "caveat": "False expansion remains high, so the contribution should be framed as noise reduction, not noise elimination.",
        },
        {
            "claim_id": "C4",
            "claim": "Noise gating is not lossless: it removes much more non-gold expansion than gold expansion, but does prune some gold-bearing candidates.",
            "evidence": f"Expansion units delta = {sums['delta_expansion_units']}; non-gold delta = {sums['delta_expansion_non_gold_units']}; gold delta = {sums['delta_expansion_gold_units']}; CR@10 improved/same/regressed = {cr_counts['improved']}/{cr_counts['same']}/{cr_counts['regressed']}.",
            "status": "supported_with_caveat",
            "caveat": "Must not claim a no-cost gate; report gold-prune cases explicitly.",
        },
        {
            "claim_id": "C5",
            "claim": "Simple gold-preserving relaxations do not improve the current system.",
            "evidence": f"allow-high-score-no-new score>=0.20: CR@10 = {gp_nonew020_all['chain_recall_at_10']}, false = {gp_nonew020_all['false_expansion_rate']}; size12: CR@10 = {gp_size12_all['chain_recall_at_10']}, false = {gp_size12_all['false_expansion_rate']}. Stage1F best CR@10 = {facet_f_all['chain_recall_at_10']}, false = {facet_f_all['false_expansion_rate']}.",
            "status": "negative_result",
            "caveat": "Useful as design evidence; not a final method component.",
        },
    ]

    matrix_path = REPORT_DIR / "stage2_claim_evidence_matrix.csv"
    with matrix_path.open("w", encoding="utf-8", newline="") as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=["claim_id", "claim", "evidence", "status", "caveat"])
        writer.writeheader()
        writer.writerows(claims)

    md_path = ROOT / "超粒球RAG_Stage2研究推进包.md"
    lines = [
        "# 超粒球RAG Stage2 研究推进包",
        "",
        "## Material Passport",
        "",
        "- Artifact: Stage2 research-to-paper handoff",
        "- Status: ANALYZED",
        "- Input artifacts: Stage1 consolidated ablation, Stage1F noise gate comparison, Stage1G gate audits, Stage1H negative scan",
        "- Scope: retrieval-only MVP on HotpotQA sample200 + MuSiQue sample200",
        "- Generated by: stage2_research_handoff.py",
        "",
        "## RQ Brief",
        "",
        "**Research Question**: How can adaptive granular balls be used as RAG knowledge units, and how can boundary uncertainty guide hyperedge-based retrieval so that multi-hop evidence recall improves while expansion noise is controlled?",
        "",
        "**Sub-Questions**:",
        "1. Do adaptive granular balls alone outperform fixed sentence units for multi-hop retrieval?",
        "2. When should retrieval expand across granular balls rather than stay within the top local ball?",
        "3. Can facet-aware hyperedges improve chain recall compared with fixed retrieval and query-aware expansion?",
        "4. How much noise does hyperedge expansion introduce, and can unsupervised gates reduce it?",
        "5. What failure modes remain before moving to generator-level RAG evaluation?",
        "",
        "**Scope**:",
        "- In scope: retrieval-only RAG indexing/retrieval, adaptive granular balls, boundary uncertainty, facet-aware hyperedge expansion, multi-hop QA evidence recall.",
        "- Out of scope for current evidence: LLM generation quality, answer EM/F1, dense embedding models, full HotpotQA/MuSiQue training-scale claims, real-time production indexing.",
        "- Datasets used so far: HotpotQA dev distractor sample200 and MuSiQue answerable dev sample200.",
        "- Methodology type: quantitative retrieval experiment + ablation + error analysis.",
        "",
        "## Claim-Evidence Matrix",
        "",
        "| ID | Claim | Evidence | Status | Caveat |",
        "|---|---|---|---|---|",
    ]
    for item in claims:
        lines.append(f"| {item['claim_id']} | {item['claim']} | {item['evidence']} | {item['status']} | {item['caveat']} |")

    lines.extend(
        [
            "",
            "## Main Experimental Facts",
            "",
            f"- Fixed TF-IDF ALL: ER@10 = {tfidf_all['evidence_recall_at_10']}, CR@10 = {tfidf_all['chain_recall_at_10']}.",
            f"- Granular-ball-only ALL: ER@10 = {gb_all['evidence_recall_at_10']}, CR@10 = {gb_all['chain_recall_at_10']}.",
            f"- Naive hyperedge ALL: CR@10 = {naive_he_all['chain_recall_at_10']}, false expansion = {naive_he_all['false_expansion_rate']}.",
            f"- Stage1E facet-aware ALL: CR@10 = {stage1e_all['chain_recall_at_10']}, false expansion = {stage1e_all['false_expansion_rate']}.",
            f"- Stage1F best ALL: ER@10 = {facet_f_all['evidence_recall_at_10']}, CR@10 = {facet_f_all['chain_recall_at_10']}, false expansion = {facet_f_all['false_expansion_rate']}.",
            f"- Stage1F best HotpotQA: CR@10 = {facet_f_hotpot['chain_recall_at_10']}, false expansion = {facet_f_hotpot['false_expansion_rate']}.",
            f"- Stage1F best MuSiQue: CR@10 = {facet_f_musique['chain_recall_at_10']}, false expansion = {facet_f_musique['false_expansion_rate']}.",
            "",
            "## Gate Audit Facts",
            "",
            f"- Stage1E selected edges: {sums['stage1e_edges']}; Stage1F selected edges: {sums['stage1f_edges']}; net change: {sums['stage1f_edges'] - sums['stage1e_edges']}.",
            f"- Blocked Stage1E edges: {sums['blocked_edges']}; blocked zero-gold edges: {sums['blocked_zero_gold_edges']}; blocked gold units: {sums['blocked_gold_units']}.",
            f"- Added Stage1F edges: {sums['added_edges']}; added zero-gold edges: {sums['added_zero_gold_edges']}; added gold units: {sums['added_gold_units']}.",
            f"- Query-level effect classes: clean_noise_prune={effect_counts['clean_noise_prune']}, noise_prune_with_gold_change={effect_counts['noise_prune_with_gold_change']}, unchanged={effect_counts['unchanged']}, mixed={effect_counts['mixed']}, retrieval_regression={effect_counts['retrieval_regression']}.",
            f"- Edge-level kept/blocked/added counts: kept={edge_status['e_kept']}, blocked={edge_status['e_blocked']}, added={edge_status['f_added']}; blocked gold edges={edge_gold[('e_blocked', 'gold')]}, blocked zero-gold edges={edge_gold[('e_blocked', 'zero_gold')]}.",
            "",
            "## What We Must Not Claim Yet",
            "",
            "- Do not claim end-to-end QA improvement: no generator has been evaluated.",
            "- Do not claim granular balls are intrinsically better than chunks: granular-ball-only underperforms fixed TF-IDF on ALL CR@10.",
            "- Do not claim hyperedge expansion is low-noise: best false expansion is still above 0.83.",
            "- Do not claim gold-preserving gating is solved: Stage1G shows gold pruning, and Stage1H simple relaxations did not help.",
            "- Do not claim dense semantic generality: current experiments use pure Python TF-IDF vectors.",
            "",
            "## Paper Contribution Framing",
            "",
            "1. **Representation**: Treat adaptive granular balls as variable-size knowledge units for RAG retrieval.",
            "2. **Decision**: Use boundary uncertainty to decide when local retrieval is insufficient and cross-ball expansion should be triggered.",
            "3. **Relation**: Express cross-ball high-order relations through facet-aware hyperedges rather than pairwise chunk similarity only.",
            "4. **Control**: Add unsupervised noise gates to reduce non-gold expansion while preserving aggregate chain recall.",
            "5. **Audit**: Provide edge-level and query-level gate audits, including negative results, to avoid overclaiming.",
            "",
            "## Recommended Next Experiments",
            "",
            "1. **Stage2A statistical reliability**: bootstrap confidence intervals for ER@10/CR@10 deltas between TF-IDF, Stage1E, and Stage1F.",
            "2. **Stage2B dense embedding replication**: replace TF-IDF vectors with a sentence embedding model and rerun fixed, ball-only, Stage1E, Stage1F.",
            "3. **Stage2C generator-level smoke test**: feed top-k evidence into a small answer generator or evaluator and report answer EM/F1 plus citation-support diagnostics.",
            "4. **Stage2D dataset expansion**: add 2WikiMultiHopQA or MultiHop-RAG to test whether the MuSiQue pattern generalizes.",
            "5. **Stage2E gold-preserving gate design**: move beyond global threshold relaxation; test rank-aware or missing-facet-aware replacement policies.",
            "",
            "## Draft Paper Skeleton",
            "",
            "1. Introduction: multi-hop RAG retrieval suffers from fixed chunk granularity and uncontrolled expansion.",
            "2. Related Work: RAG retrieval units, granular-ball computing, hypergraph/hyperedge retrieval, uncertainty-aware retrieval.",
            "3. Method: adaptive granular-ball index, boundary uncertainty decision, facet-aware hyperedge construction, noise-gated retrieval.",
            "4. Experimental Setup: HotpotQA/MuSiQue samples, retrieval-only metrics, implementation details, baselines.",
            "5. Results: ablation table, dataset split, gate audit, negative Stage1H results.",
            "6. Discussion: why MuSiQue benefits more, why granular balls alone fail, remaining false expansion.",
            "7. Limitations and Future Work: dense embeddings, generator evaluation, larger datasets, statistical tests.",
            "",
            f"CSV output: `{matrix_path}`",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {matrix_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
