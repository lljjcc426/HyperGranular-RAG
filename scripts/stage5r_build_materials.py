#!/usr/bin/env python3
"""Build Stage5R paper figures and tables from frozen Stage4E-Stage5A evidence.

This is a document build only.  It performs no retrieval, generation, Gold
evaluation, bootstrap, configuration search, or scientific re-analysis.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable

os.environ.setdefault("SOURCE_DATE_EPOCH", "1785024000")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from stage5_pmc_build_figures import INPUTS as STAGE4_INPUTS


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "figures_stage5r"
SOURCE = OUT / "source_data"
TABLES = ROOT / "paper" / "STAGE5R_CORE_TABLES.md"
OLD_BUILDER = ROOT / "scripts" / "stage5_pmc_build_figures.py"
OLD_BUILDER_SHA256 = "3940976AD7E57443AFE3EF78BFF42316BFD965EED2C76991C23ACF46EED8CD46"

STAGE5A_INPUTS = {
    "stage5a_equal": (
        ROOT / "results" / "stage5a_bnh_confirmation_equal_weight_summary.json",
        "D38608EB73FF1A7741A6EBE2DE2E08B0F7FC7D0305067F6FE7D60F8B8C83983F",
    ),
    "stage5a_datasets": (
        ROOT / "results" / "stage5a_bnh_confirmation_dataset_summaries.json",
        "F4893C526AC45C5622A93B44BDCFAA50A484C896F4F7984AF0E4150F79763546",
    ),
    "stage5a_mechanism": (
        ROOT / "results" / "stage5a_bnh_confirmation_mechanism_audit.json",
        "0AEEA7C41680E10A417E036CD1C6DC2D86BF60BAAD337218AE07F6DE697027F1",
    ),
    "stage5a_efficiency": (
        ROOT / "results" / "stage5a_bnh_confirmation_efficiency_summary.json",
        "A79140BC374A12F9EF887DFEEA32042F45E6FEDC3E31A1072B445194BACCE1D8",
    ),
    "stage5a_ledger": (
        ROOT / "results" / "stage5a_bnh_evidence_ledger.json",
        "9D97B4100C9BCD31E421595EC18BA2C7318D9E6709AE9106446388C9CA63ABE4",
    ),
    "stage5a_final_verification": (
        ROOT / "results" / "stage5a_bnh_final_verification.json",
        "145B51FB194BA0DE5B00D294FE4D8F8EAC9FD9D2E7C1F39F741D7AFEDDF0BA09",
    ),
}
INPUTS = {**STAGE4_INPUTS, **STAGE5A_INPUTS}

COLORS = {
    "dense": "#4C78A8",
    "hgrag": "#F2A65A",
    "bge": "#355C7D",
    "protected": "#3A7D44",
    "unprotected": "#B24C4C",
    "facet": "#7B61A8",
    "inconclusive": "#777777",
    "undefined": "#A88B32",
    "not_evaluated": "#6F7B86",
    "ink": "#202830",
    "grid": "#D9DEE3",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def load_inputs() -> dict[str, Any]:
    if sha256(OLD_BUILDER) != OLD_BUILDER_SHA256:
        raise RuntimeError("Frozen Stage5-PMC builder identity mismatch")
    loaded: dict[str, Any] = {}
    for label, (path, expected) in INPUTS.items():
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(
                f"Frozen input mismatch for {label}: expected {expected}, got {actual}"
            )
        loaded[label] = json.loads(path.read_text(encoding="utf-8"))
    return loaded


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def configure() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "axes.linewidth": 0.7,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "svg.fonttype": "none",
            "svg.hashsalt": "stage5r-pmr-v1",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def save(fig: plt.Figure, stem: str) -> list[Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    paths = [OUT / f"{stem}.{suffix}" for suffix in ("svg", "pdf", "tiff", "png")]
    fig.savefig(paths[0], metadata={"Date": None})
    svg = paths[0].read_text(encoding="utf-8")
    paths[0].write_text(
        "\n".join(line.rstrip() for line in svg.splitlines()) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    fig.savefig(
        paths[1],
        metadata={
            "CreationDate": None,
            "ModDate": None,
            "Creator": "stage5r_build_materials.py",
            "Producer": "Matplotlib",
        },
    )
    fig.savefig(paths[2], dpi=600, pil_kwargs={"compression": "tiff_lzw"})
    fig.savefig(paths[3], dpi=300, metadata={"Software": "Matplotlib"})
    plt.close(fig)
    return paths


def box(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    color: str,
    dashed: bool = False,
) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.012,rounding_size=0.018",
            facecolor=color,
            edgecolor="#52606B",
            linestyle="--" if dashed else "-",
            linewidth=0.8,
        )
    )
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=COLORS["ink"])


def arrow(ax: plt.Axes, a: tuple[float, float], b: tuple[float, float]) -> None:
    ax.add_patch(
        FancyArrowPatch(
            a,
            b,
            arrowstyle="-|>",
            mutation_scale=8,
            linewidth=0.9,
            color="#66727C",
        )
    )


def metric(d: dict[str, Any], stage: str) -> tuple[float, float, float]:
    if stage in {"4e", "4f", "4g"}:
        return float(d["point"]), float(d["lower_95"]), float(d["upper_95"])
    return float(d["point"]), float(d["ci95_lower"]), float(d["ci95_upper"])


def effect_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    h = data["stage4h_equal"]["comparisons"]
    i = data["stage4i_equal"]["comparisons"]
    a = data["stage5a_equal"]["comparisons"]
    source = [
        (
            "Compact / HotpotQA",
            "Full − Dense (Stage4E)",
            metric(data["stage4e_summary"]["bootstrap"]["delta_answer_f1"], "4e"),
            "SUPPORTED",
            "CONFIRMATION",
        ),
        (
            "Compact / MuSiQue",
            "Full − Dense (Stage4F)",
            metric(data["stage4f_summary"]["bootstrap"]["delta_answer_f1"], "4f"),
            "SUPPORTED",
            "CONFIRMATION",
        ),
        (
            "Generator transfer",
            "Full − Dense (Gemma)",
            metric(data["stage4g_equal"]["bootstrap"]["delta_answer_f1"], "4g"),
            "INCONCLUSIVE",
            "CONFIRMATION",
        ),
        (
            "Compact / joint",
            "Full − Dense (Stage4H)",
            metric(h["DENSE_TOP20"]["dataset_equal_weight"]["delta_answer_f1"], "4h"),
            "SUPPORTED",
            "CONFIRMATION",
        ),
        (
            "Strong baseline",
            "Full − BGE",
            metric(h["STRONG_DENSE_TOP20"]["dataset_equal_weight"]["delta_answer_f1"], "4h"),
            "NEGATIVE",
            "CONFIRMATION",
        ),
        (
            "Compact component",
            "Full − NoFacet",
            metric(h["Q25_NO_FACET_HYPEREDGE"]["dataset_equal_weight"]["delta_answer_f1"], "4h"),
            "SUPPORTED",
            "CONFIRMATION",
        ),
        (
            "Cross-space sidecar",
            "Protected − BGE",
            metric(i["protected_minus_bge"]["dataset_equal_weight"]["delta_answer_f1"], "4i"),
            "INCONCLUSIVE",
            "CONFIRMATION",
        ),
        (
            "Cross-space placement",
            "Protected − Unprotected",
            metric(i["protected_minus_unprotected"]["dataset_equal_weight"]["delta_answer_f1"], "4i"),
            "SUPPORTED",
            "CONFIRMATION",
        ),
        (
            "BGE-native",
            "Protected − BGE",
            metric(a["protected_minus_bge"]["dataset_equal_weight"]["delta_answer_f1"], "5a"),
            "INCONCLUSIVE",
            "CONFIRMATION",
        ),
        (
            "BGE-native placement",
            "Protected − Unprotected",
            metric(a["protected_minus_unprotected"]["dataset_equal_weight"]["delta_answer_f1"], "5a"),
            "INCONCLUSIVE",
            "CONFIRMATION",
        ),
        (
            "BGE-native facet",
            "Protected − NoFacet",
            metric(a["protected_minus_no_facet"]["dataset_equal_weight"]["delta_answer_f1"], "5a"),
            "INCONCLUSIVE",
            "CONFIRMATION",
        ),
    ]
    return [
        {
            "evidence_family": family,
            "contrast": contrast,
            "delta_answer_f1": point,
            "ci95_lower": low,
            "ci95_upper": high,
            "status": status,
            "evidence_role": role,
        }
        for family, contrast, (point, low, high), status, role in source
    ]


def figure1() -> list[Path]:
    rows = [
        {"step": 1, "component": "Compact dense or BGE backbone", "role": "ranked evidence"},
        {"step": 2, "component": "Adaptive granular balls", "role": "local organization"},
        {"step": 3, "component": "Query-aware facet hyperedges", "role": "high-order links"},
        {"step": 4, "component": "Protected bounded insertion", "role": "Top-k completion"},
        {"step": 5, "component": "Generator", "role": "answer prediction"},
        {"step": 6, "component": "BGE cross-space sidecar", "role": "inconclusive variant"},
        {"step": 7, "component": "BGE-native reconstruction", "role": "inconclusive variant"},
    ]
    write_csv(SOURCE / "figure1_method_overview.csv", list(rows[0]), rows)
    fig, ax = plt.subplots(figsize=(8.4, 3.4))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    xs = [0.03, 0.22, 0.41, 0.60, 0.79]
    labels = [
        "Dense\nTop-20",
        "Adaptive\ngranular balls",
        "Facet\nhyperedges",
        "Protected\nbounded insertion",
        "Generator\nanswer",
    ]
    colors = ["#D8E7F3", "#FDE5C6", "#E7DDF4", "#D9ECD9", "#E5E8EA"]
    for x, label, color in zip(xs, labels, colors):
        box(ax, x, 0.56, 0.15, 0.20, label, color)
    for x in xs[:-1]:
        arrow(ax, (x + 0.15, 0.66), (x + 0.19, 0.66))
    box(ax, 0.12, 0.13, 0.28, 0.17, "BGE cross-space sidecar\nMiniLM structural space", "#EEF1F4", True)
    box(ax, 0.60, 0.13, 0.28, 0.17, "BGE-native reconstruction\nBGE structural space", "#EEF1F4", True)
    arrow(ax, (0.40, 0.215), (0.60, 0.56))
    arrow(ax, (0.74, 0.30), (0.69, 0.56))
    ax.text(
        0.5,
        0.93,
        "HyperGranular-RAG: protected high-order evidence completion under a fixed Top-k budget",
        ha="center",
        va="center",
        fontsize=10,
        weight="bold",
    )
    ax.text(
        0.5,
        0.04,
        "Dashed variants were evaluated; neither established incremental answer-quality gain over BGE.",
        ha="center",
        color=COLORS["inconclusive"],
    )
    fig.tight_layout()
    return save(fig, "figure1_method_overview")


def figure2(rows: list[dict[str, Any]]) -> list[Path]:
    write_csv(SOURCE / "figure2_effect_size_forest.csv", list(rows[0]), rows)
    fig, ax = plt.subplots(figsize=(8.2, 5.6))
    y = np.arange(len(rows))[::-1]
    points = np.array([r["delta_answer_f1"] for r in rows])
    lows = np.array([r["ci95_lower"] for r in rows])
    highs = np.array([r["ci95_upper"] for r in rows])
    color_map = {
        "SUPPORTED": COLORS["protected"],
        "NEGATIVE": COLORS["unprotected"],
        "INCONCLUSIVE": COLORS["inconclusive"],
    }
    for idx, (row, yy) in enumerate(zip(rows, y)):
        ax.errorbar(
            points[idx],
            yy,
            xerr=[[points[idx] - lows[idx]], [highs[idx] - points[idx]]],
            fmt="o",
            markersize=4.5,
            color=color_map[row["status"]],
            capsize=2,
        )
    ax.axvline(0, color="#222222", linewidth=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([f'{r["evidence_family"]}: {r["contrast"]}' for r in rows])
    ax.set_xlabel("Paired difference in answer F1 (95% bootstrap CI)")
    ax.set_title("Frozen effect-size evidence across compact, transfer, and strong-retriever boundaries")
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.6)
    ax.set_xlim(-0.06, 0.035)
    fig.tight_layout()
    return save(fig, "figure2_effect_size_forest")


def absolute_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    specs = [
        ("Stage4H original", "BGE", "stage4h_datasets", "STRONG_DENSE_TOP20"),
        ("Stage4H original", "Original Full", "stage4h_datasets", "STATIC_Q25_FULL"),
        ("Stage4I cross-space", "BGE", "stage4i_datasets", "BGE_TOP20"),
        (
            "Stage4I cross-space",
            "MiniLM sidecar Protected",
            "stage4i_datasets",
            "BGE_HGRAG_PROTECTED_TOP20",
        ),
        ("Stage5A BGE-native", "BGE", "stage5a_datasets", "BGE_TOP20"),
        (
            "Stage5A BGE-native",
            "Native Protected",
            "stage5a_datasets",
            "BGE_NATIVE_HGRAG_PROTECTED_TOP20",
        ),
    ]
    rows = []
    for boundary, method, source, key in specs:
        d = data[source]
        if source in {"stage4h_datasets", "stage4i_datasets"}:
            hp = d["hotpotqa_train_distractor_v1_1"]["methods"][key]["answer_f1"]
            mq = d["musique_ans_v1_0_train"]["methods"][key]["answer_f1"]
        else:
            hp = d["hotpotqa_train_distractor_v1_1"]["methods"][key]["answer_f1"]
            mq = d["musique_ans_v1_0_train"]["methods"][key]["answer_f1"]
        rows.append(
            {
                "frozen_boundary": boundary,
                "method": method,
                "hotpotqa_answer_f1": hp,
                "musique_answer_f1": mq,
                "dataset_equal_weight_answer_f1": (hp + mq) / 2,
                "comparability_note": "compare only within the same frozen boundary",
            }
        )
    return rows


def displacement_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    specs = [
        (
            "Stage4I cross-space sidecar",
            data["stage4i_evidence"],
            "BGE_HGRAG_PROTECTED_TOP20",
        ),
        (
            "Stage5A BGE-native",
            data["stage5a_mechanism"],
            "BGE_NATIVE_HGRAG_PROTECTED_TOP20",
        ),
    ]
    rows = []
    for boundary, source, method in specs:
        for dataset, short in [
            ("hotpotqa_train_distractor_v1_1", "HotpotQA"),
            ("musique_ans_v1_0_train", "MuSiQue"),
        ]:
            item = source["datasets"][dataset][method]
            rows.append(
                {
                    "frozen_boundary": boundary,
                    "dataset": short,
                    "added_gold": item["added_gold_evidence_total"],
                    "displaced_gold": item["displaced_bge_gold_evidence_total"],
                    "net_gold": item["net_gold_evidence_change_total"],
                    "evidence_role": "POST_DECISION_DESCRIPTIVE_ONLY",
                }
            )
    return rows


def figure3(abs_rows: list[dict[str, Any]], disp_rows: list[dict[str, Any]]) -> list[Path]:
    write_csv(SOURCE / "figure3a_strong_dense_boundary.csv", list(abs_rows[0]), abs_rows)
    write_csv(SOURCE / "figure3b_evidence_displacement.csv", list(disp_rows[0]), disp_rows)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 4.2), gridspec_kw={"width_ratios": [1.2, 1]})
    x = np.arange(3)
    width = 0.34
    base = [abs_rows[0], abs_rows[2], abs_rows[4]]
    ext = [abs_rows[1], abs_rows[3], abs_rows[5]]
    ax1.bar(x - width / 2, [r["dataset_equal_weight_answer_f1"] for r in base], width, label="BGE", color=COLORS["bge"])
    ax1.bar(x + width / 2, [r["dataset_equal_weight_answer_f1"] for r in ext], width, label="Structural method", color=COLORS["hgrag"])
    ax1.set_xticks(x)
    ax1.set_xticklabels(["Original\nFull", "Cross-space\nsidecar", "BGE-native\nProtected"])
    ax1.set_ylabel("Dataset-equal-weight answer F1")
    ax1.set_ylim(0.30, 0.38)
    ax1.set_title("A. Strong-retriever boundary\n(separate frozen boundaries; not pooled)")
    ax1.grid(axis="y", color=COLORS["grid"], linewidth=0.6)
    ax1.legend(frameon=False)

    labels = [f'{r["frozen_boundary"].replace("Stage", "S")}\n{r["dataset"]}' for r in disp_rows]
    y = np.arange(len(disp_rows))
    ax2.barh(y, [r["added_gold"] for r in disp_rows], color=COLORS["protected"], label="Added Gold")
    ax2.barh(y, [-r["displaced_gold"] for r in disp_rows], color=COLORS["unprotected"], label="Displaced Gold")
    for yy, r in zip(y, disp_rows):
        ax2.text(1, yy, f'net {r["net_gold"]:+d}', va="center", fontsize=7, weight="bold")
    ax2.axvline(0, color="#222222", linewidth=0.7)
    ax2.set_yticks(y)
    ax2.set_yticklabels(labels)
    ax2.set_xlabel("Gold evidence count (post-decision descriptive)")
    ax2.set_title("B. Added and displaced Gold evidence")
    ax2.grid(axis="x", color=COLORS["grid"], linewidth=0.6)
    ax2.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    return save(fig, "figure3_strong_dense_and_displacement")


def evidence_map_rows() -> list[dict[str, Any]]:
    return [
        {"claim": "Compact Full > Dense (three frozen boundaries)", "status": "SUPPORTED", "scope": "MiniLM, Qwen, closed-candidate Top-20"},
        {"claim": "Facet increment in frozen MiniLM system", "status": "SUPPORTED", "scope": "Stage4H only"},
        {"claim": "Protected placement with identical sidecar insertions", "status": "SUPPORTED", "scope": "Stage4I only"},
        {"claim": "Original Full > strong BGE", "status": "NEGATIVE", "scope": "Stage4H"},
        {"claim": "Cross-space sidecar > BGE", "status": "INCONCLUSIVE", "scope": "Stage4I"},
        {"claim": "BGE-native Protected > BGE", "status": "INCONCLUSIVE", "scope": "Stage5A"},
        {"claim": "BGE-native placement increment", "status": "INCONCLUSIVE", "scope": "Stage5A"},
        {"claim": "BGE-native facet increment", "status": "INCONCLUSIVE", "scope": "Stage5A"},
        {"claim": "Additional-generator transfer", "status": "INCONCLUSIVE", "scope": "one Gemma mobile-QAT setting"},
        {"claim": "Flat granular-ball control", "status": "NOT_FAIRLY_DEFINED", "scope": "no scientifically matched contrast"},
    ]


def figure4(rows: list[dict[str, Any]]) -> list[Path]:
    write_csv(SOURCE / "figure4_evidence_map.csv", list(rows[0]), rows)
    status_order = ["SUPPORTED", "NEGATIVE", "INCONCLUSIVE", "NOT_FAIRLY_DEFINED"]
    color = {
        "SUPPORTED": COLORS["protected"],
        "NEGATIVE": COLORS["unprotected"],
        "INCONCLUSIVE": COLORS["inconclusive"],
        "NOT_FAIRLY_DEFINED": COLORS["undefined"],
    }
    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    y = np.arange(len(rows))[::-1]
    x = [status_order.index(r["status"]) for r in rows]
    for xx, yy, row in zip(x, y, rows):
        ax.scatter(xx, yy, s=90, color=color[row["status"]], edgecolor="white", linewidth=0.8)
        ax.text(xx + 0.08, yy, row["scope"], va="center", fontsize=7, color="#4E5962")
    ax.set_yticks(y)
    ax.set_yticklabels([r["claim"] for r in rows])
    ax.set_xticks(range(4))
    ax.set_xticklabels(status_order)
    ax.set_xlim(-0.25, 4.45)
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.6)
    ax.set_title("Evidence-state map: uncertainty is neither equivalence nor failure")
    fig.tight_layout()
    return save(fig, "figure4_evidence_map")


def applicability_rows() -> list[dict[str, Any]]:
    return [
        {"boundary": "Compact MiniLM Dense", "status": "SUPPORTED", "conclusion": "repeated small positive evidence"},
        {"boundary": "Strong BGE baseline", "status": "NEGATIVE", "conclusion": "original Full underperforms BGE"},
        {"boundary": "Cross-space BGE sidecar", "status": "INCONCLUSIVE", "conclusion": "no confirmed incremental answer-quality gain"},
        {"boundary": "BGE-native HGRAG", "status": "INCONCLUSIVE", "conclusion": "no confirmed gain, harm, or equivalence"},
        {"boundary": "Additional generator", "status": "INCONCLUSIVE", "conclusion": "one Gemma mobile-QAT configuration"},
        {"boundary": "Full-wiki / open-domain", "status": "NOT_EVALUATED", "conclusion": "outside the frozen evidence"},
    ]


def figure5(rows: list[dict[str, Any]]) -> list[Path]:
    write_csv(SOURCE / "figure5_applicability_boundary.csv", list(rows[0]), rows)
    color = {
        "SUPPORTED": COLORS["protected"],
        "NEGATIVE": COLORS["unprotected"],
        "INCONCLUSIVE": COLORS["inconclusive"],
        "NOT_EVALUATED": COLORS["not_evaluated"],
    }
    fig, ax = plt.subplots(figsize=(9.2, 4.3))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    for idx, row in enumerate(rows):
        col = idx % 3
        r = idx // 3
        x = 0.03 + col * 0.32
        y = 0.56 - r * 0.38
        box(ax, x, y, 0.29, 0.24, f'{row["boundary"]}\n{row["status"]}\n{row["conclusion"]}', "#F7F8F9")
        ax.add_patch(plt.Rectangle((x, y), 0.012, 0.24, color=color[row["status"]], clip_on=False))
    ax.text(0.5, 0.94, "Applicability boundary of the frozen evidence", ha="center", fontsize=10, weight="bold")
    fig.tight_layout()
    return save(fig, "figure5_applicability_boundary")


def fmt_effect(point: float, low: float, high: float) -> str:
    return f"{point:+.5f} [{low:.5f}, {high:.5f}]"


def make_table_rows(data: dict[str, Any], effects: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    table1 = [
        {
            "boundary": r["evidence_family"],
            "contrast": r["contrast"],
            "delta_f1_ci": fmt_effect(r["delta_answer_f1"], r["ci95_lower"], r["ci95_upper"]),
            "status": r["status"],
        }
        for r in effects
        if r["evidence_family"] in {"Compact / HotpotQA", "Compact / MuSiQue", "Compact / joint"}
    ]
    table2 = [
        {
            "boundary": r["evidence_family"],
            "contrast": r["contrast"],
            "delta_f1_ci": fmt_effect(r["delta_answer_f1"], r["ci95_lower"], r["ci95_upper"]),
            "status": r["status"],
        }
        for r in effects
        if r["evidence_family"] in {"Strong baseline", "Cross-space sidecar", "BGE-native", "Generator transfer"}
    ]
    table3 = [
        {
            "boundary": r["evidence_family"],
            "contrast": r["contrast"],
            "delta_f1_ci": fmt_effect(r["delta_answer_f1"], r["ci95_lower"], r["ci95_upper"]),
            "status": r["status"],
        }
        for r in effects
        if r["evidence_family"] in {"Compact component", "Cross-space placement", "BGE-native placement", "BGE-native facet"}
    ]
    table3.append(
        {
            "boundary": "Granular-ball control",
            "contrast": "Full − FlatBalls",
            "delta_f1_ci": "not estimable",
            "status": "NOT_FAIRLY_DEFINED",
        }
    )
    eff = data["stage5a_efficiency"]
    table4 = [
        {"item": "Stage5A retrieval reconstruction", "value": f'{eff["retrieval_reconstruction_seconds"]:.3f} s', "role": "descriptive"},
        {"item": "Stage5A BGE generation", "value": f'{eff["generation_seconds_by_method"]["BGE_TOP20"]:.3f} s', "role": "descriptive"},
        {"item": "Stage5A native Protected generation", "value": f'{eff["generation_seconds_by_method"]["BGE_NATIVE_HGRAG_PROTECTED_TOP20"]:.3f} s', "role": "descriptive"},
        {"item": "Stage5A GPU peak memory", "value": f'{eff["gpu_peak_memory_bytes"] / 2**30:.3f} GiB', "role": "descriptive"},
        {"item": "Bootstrap", "value": "10,000 iterations per frozen decision", "role": "confirmatory"},
        {"item": "Build policy", "value": "two byte-identical Stage5R builds", "role": "integrity"},
        {"item": "Gold policy", "value": "Gold isolated until frozen rankings/predictions", "role": "integrity"},
        {"item": "Verification", "value": "independent final verifiers passed", "role": "integrity"},
    ]
    table5 = [
        {"claim": r["claim"], "evidence_state": r["status"], "boundary": r["scope"]}
        for r in evidence_map_rows()
    ]
    return {"table1": table1, "table2": table2, "table3": table3, "table4": table4, "table5": table5}


def markdown_table(rows: list[dict[str, Any]]) -> str:
    fields = list(rows[0])
    out = [
        "| " + " | ".join(field.replace("_", " ").title() for field in fields) + " |",
        "|" + "|".join("---" for _ in fields) + "|",
    ]
    out.extend("| " + " | ".join(str(row[field]) for field in fields) + " |" for row in rows)
    return "\n".join(out)


def write_tables(data: dict[str, Any], effects: list[dict[str, Any]]) -> list[Path]:
    tables = make_table_rows(data, effects)
    csv_paths = []
    for name, rows in tables.items():
        path = SOURCE / f"{name}_core.csv"
        write_csv(path, list(rows[0]), rows)
        csv_paths.append(path)
    text = """# Stage5R Core Tables

Status: `TABLES_AUTOMATICALLY_REBUILT_FROM_FROZEN_STAGE4E_STAGE5A_JSON`

All numerical entries below are generated by
`scripts/stage5r_build_materials.py`. Development evidence is not pooled with
confirmation evidence. Confidence intervals crossing zero are labelled
`INCONCLUSIVE`, not equivalent or ineffective.

## Table 1. Repeated compact-dense results

{table1}

## Table 2. Strong-retriever boundary and generator transfer

{table2}

## Table 3. Component and placement evidence

{table3}

## Table 4. Efficiency, integrity, and deterministic verification

{table4}

The time and memory entries are descriptive for the recorded hardware and
frozen transactions; they are not claims of cross-device efficiency.

## Table 5. Claim-evidence-boundary summary

{table5}

Source CSV files are stored in
[`paper/figures_stage5r/source_data`](figures_stage5r/source_data/).
""".format(**{name: markdown_table(rows) for name, rows in tables.items()})
    TABLES.write_text(text, encoding="utf-8", newline="\n")
    return [TABLES, *csv_paths]


def write_captions() -> Path:
    path = OUT / "FIGURE_CONTRACTS_AND_CAPTIONS.md"
    text = """# Stage5R Figure Contracts and Captions

## Figure 1

**HyperGranular-RAG method overview.** The compact system organizes locally
related evidence as adaptive granular balls, links query-relevant facets across
balls with high-order hyperedges, and inserts bounded candidates after a
protected prefix under the same Top-k budget. The dashed cross-space and
BGE-native variants are evaluated configurations, not validated improvements
over BGE.

## Figure 2

**Frozen answer-F1 effect sizes.** Points are paired answer-F1 differences and
bars are the pre-specified 95% bootstrap confidence intervals. The zero line is
shown explicitly and the x-axis is not truncated around positive effects.
`INCONCLUSIVE` means that the interval crosses zero; it is not an equivalence
claim.

## Figure 3

**Strong-retriever boundary and evidence displacement.** Panel A compares each
structural method only with BGE inside its own frozen Stage4H, Stage4I, or
Stage5A boundary; the three groups are not pooled or treated as a common
head-to-head sample. Panel B reports post-decision descriptive Gold evidence
added and displaced. These counts did not control selection or advancement and
do not replace end-to-end answer evaluation.

## Figure 4

**Evidence-state map.** Supported, negative, inconclusive, and not-fairly-defined
outcomes are kept distinct. Component findings are system-dependent and are not
transported across semantic spaces without confirmation.

## Figure 5

**Applicability boundary.** Repeated small gains are established only for the
historical compact MiniLM backbone under closed-candidate Top-20 evaluation.
The original system is negative against strong BGE, the tested sidecar and
BGE-native extensions are inconclusive, and full-wiki/open-domain operation was
not evaluated.

Each figure is exported as editable SVG, PDF, 600-dpi TIFF, and 300-dpi PNG.
Every plotted value has a CSV source file, and every export is byte/SHA bound in
`STAGE5R_FIGURE_MANIFEST.json`.
"""
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def write_manifest(derived: list[Path]) -> Path:
    path = OUT / "STAGE5R_FIGURE_MANIFEST.json"
    manifest = {
        "schema_version": "stage5r_pmr_figure_manifest_v1",
        "status": "STAGE5R_FIGURES_BUILT_FROM_FROZEN_STAGE4E_STAGE5A_EVIDENCE",
        "scientific_reanalysis": False,
        "backend": {
            "python": os.sys.version.split()[0],
            "matplotlib": matplotlib.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": scipy.__version__,
            "source_date_epoch": os.environ["SOURCE_DATE_EPOCH"],
        },
        "inputs": [
            {
                "label": label,
                "path": path_.relative_to(ROOT).as_posix(),
                "bytes": path_.stat().st_size,
                "sha256": sha256(path_),
            }
            for label, (path_, _) in sorted(INPUTS.items())
        ],
        "builder": {
            "path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "old_frozen_builder_path": OLD_BUILDER.relative_to(ROOT).as_posix(),
            "old_frozen_builder_sha256": OLD_BUILDER_SHA256,
        },
        "derived_files": [
            {
                "path": item.relative_to(ROOT).as_posix(),
                "bytes": item.stat().st_size,
                "sha256": sha256(item),
            }
            for item in sorted(set(derived), key=lambda p: p.as_posix())
            if item != path
        ],
    }
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return path


def main() -> None:
    data = load_inputs()
    configure()
    SOURCE.mkdir(parents=True, exist_ok=True)
    effects = effect_rows(data)
    derived: list[Path] = []
    derived += figure1()
    derived += figure2(effects)
    abs_rows = absolute_rows(data)
    disp_rows = displacement_rows(data)
    derived += figure3(abs_rows, disp_rows)
    derived += figure4(evidence_map_rows())
    derived += figure5(applicability_rows())
    derived += list(SOURCE.glob("figure*.csv"))
    derived += write_tables(data, effects)
    derived.append(write_captions())
    manifest = write_manifest(derived)
    print(
        json.dumps(
            {
                "status": "STAGE5R_FIGURES_AND_TABLES_BUILT",
                "figure_groups": 5,
                "exports": 20,
                "source_csv": len(list(SOURCE.glob("*.csv"))),
                "manifest": manifest.relative_to(ROOT).as_posix(),
                "scientific_reanalysis": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
