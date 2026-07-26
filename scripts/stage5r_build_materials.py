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
import re
import statistics
import textwrap
from collections import Counter, defaultdict
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
DATA_ROOT = ROOT.parent / "超粒球RAG_数据"
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
PAPER_JSONL_INPUTS = {
    "stage4e_rankings": (
        ROOT / "results" / "stage4e_e2e_official_train1000_v1_rankings.jsonl",
        "AA6CBAD5D37BD66424DCAC6472FEBA8AC5FBAA769B789D968103AAB7CFDD1455",
    ),
    "stage4e_query_audit": (
        ROOT / "results" / "stage4e_e2e_official_train1000_v1_query_audit.jsonl",
        "ACDB9D22C14B9D10FEA0867DFFB2B87DBD4D1B4E07FCDBA8277638E3AB638C19",
    ),
    "stage4f_rankings": (
        ROOT / "results" / "stage4f_xdr_musique_train3000_v1_rankings.jsonl",
        "732A10DE74E8F97E5CECFDBFBBC3B49E5EF053C6F190948CD5C0B66D71D6AEDD",
    ),
    "stage4f_query_audit": (
        ROOT / "results" / "stage4f_xdr_musique_train3000_v1_query_audit.jsonl",
        "EA7634EE7354A959A1D03D1E9DD7A220BA39F3F7CF2D6F168D17E3EC53C66ADF",
    ),
    "stage4h_rankings": (
        ROOT / "results" / "stage4h_cbe_hotpot1000_musique1500_v1_rankings.jsonl",
        "EAECD420CEDDFD0E670892E9B78B0D6D02BB3E9BE2A84BC36631C1D985C49822",
    ),
    "stage4h_query_audit": (
        ROOT / "results" / "stage4h_cbe_hotpot1000_musique1500_v1_query_audit.jsonl",
        "6232260E8D91D070E8A28B96A4F179538D2EB300F16FE28DB3B24168ADBD4CA9",
    ),
    "stage4h_predictions": (
        ROOT / "results" / "stage4h_cbe_hotpot1000_musique1500_v1_predictions_main.jsonl",
        "52B9276E93AF19820B8F2E358F54BE9CDF88D4A8C6A34020AF3EDC153470E310",
    ),
    "stage4h_trace": (
        ROOT / "results" / "stage4h_cbe_hotpot1000_musique1500_v1_retrieval_trace.jsonl",
        "308D3FCF9B0D517548542C33BB241B2824446B68453697F83BC5CAA13796087F",
    ),
    "stage4i_trace": (
        ROOT / "results" / "stage4i_sdc_hotpot1000_musique1500_v1_candidate_trace.jsonl",
        "62AC7A2FD91997FFC72E2F0A2A0F9945D2056C0670C299CC002917B2EC4D9DA7",
    ),
    "stage5a_trace": (
        ROOT
        / "results"
        / "stage5a_bnh_confirmation_hotpot1000_musique1500_v1_candidate_trace.jsonl",
        "226BA734FAB41E8941259109529B93DA8A3E951B7E7AF3F700147BDFF38B00CB",
    ),
    "stage4h_blind_queries": (
        DATA_ROOT
        / "processed"
        / "stage4h_cbe_hotpot1000_musique1500_v1_blind_queries.jsonl",
        "19E2659B190E91A4FC6350698C921C8F3FFA86B793BA89F3D726C004C5EA9B64",
    ),
    "stage4h_gold_targets": (
        DATA_ROOT
        / "processed"
        / "stage4h_cbe_hotpot1000_musique1500_v1_gold_targets.jsonl",
        "02407A306C0728024CB3D515C7427610C2AFB4898C75FEE9EDA9BA890A22B92F",
    ),
}
MANIFEST_INPUTS = {**INPUTS, **PAPER_JSONL_INPUTS}

COLORS = {
    "dense": "#7A7F87",
    "hgrag": "#0072B2",
    "bge": "#484878",
    "protected": "#2E8B57",
    "unprotected": "#D55E00",
    "facet": "#8C6BB1",
    "inconclusive": "#8A8A8A",
    "undefined": "#A88B32",
    "not_evaluated": "#6F7B86",
    "ink": "#263238",
    "grid": "#D9DEE3",
    "pale_blue": "#E8F3F8",
    "pale_violet": "#F1ECF7",
    "pale_orange": "#FBEDE4",
    "pale_gray": "#F3F4F5",
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
    for label, (path, expected) in PAPER_JSONL_INPUTS.items():
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(
                f"Frozen paper-audit input mismatch for {label}: "
                f"expected {expected}, got {actual}"
            )
        loaded[label] = path
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
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
            "font.size": 7.5,
            "axes.titlesize": 8.2,
            "axes.labelsize": 7.5,
            "xtick.labelsize": 6.7,
            "ytick.labelsize": 6.7,
            "legend.fontsize": 6.7,
            "axes.linewidth": 0.7,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "legend.frameon": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "svg.fonttype": "none",
            "svg.hashsalt": "stage5r-pmr-figure-redesign-v2",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def save(fig: plt.Figure, stem: str) -> list[Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    paths = [OUT / f"{stem}.{suffix}" for suffix in ("svg", "pdf", "tiff", "png")]
    fig.savefig(paths[0], metadata={"Date": None}, bbox_inches="tight")
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
        bbox_inches="tight",
    )
    fig.savefig(
        paths[2],
        dpi=600,
        bbox_inches="tight",
        pil_kwargs={"compression": "tiff_lzw"},
    )
    fig.savefig(
        paths[3],
        dpi=300,
        bbox_inches="tight",
        metadata={"Software": "Matplotlib"},
    )
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
            "Compact protection",
            "Full − NoProtection",
            metric(h["Q25_NO_PROTECTION"]["dataset_equal_weight"]["delta_answer_f1"], "4h"),
            "INCONCLUSIVE",
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
            "Cross-space facet",
            "Protected − NoFacet",
            metric(i["protected_minus_no_facet"]["dataset_equal_weight"]["delta_answer_f1"], "4i"),
            "INCONCLUSIVE",
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
                "dataset_equal_weight_answer_em": (
                    d["hotpotqa_train_distractor_v1_1"]["methods"][key]["answer_em"]
                    + d["musique_ans_v1_0_train"]["methods"][key]["answer_em"]
                )
                / 2,
                "dataset_equal_weight_retrieval_cr20": (
                    d["hotpotqa_train_distractor_v1_1"]["methods"][key]["retrieval_cr20"]
                    + d["musique_ans_v1_0_train"]["methods"][key]["retrieval_cr20"]
                )
                / 2,
                "dataset_equal_weight_retrieval_er20": (
                    d["hotpotqa_train_distractor_v1_1"]["methods"][key]["retrieval_er20"]
                    + d["musique_ans_v1_0_train"]["methods"][key]["retrieval_er20"]
                )
                / 2,
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


def add_panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        -0.10,
        1.04,
        label,
        transform=ax.transAxes,
        fontsize=8.5,
        fontweight="bold",
        ha="left",
        va="bottom",
        color=COLORS["ink"],
    )


def main_performance_rows(
    compact_rows: list[dict[str, Any]],
    strong_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    compact_labels = ["HotpotQA", "MuSiQue", "Joint"]
    for label, row in zip(compact_labels, compact_rows):
        rows.append(
            {
                "setting_group": "Compact MiniLM",
                "boundary": label,
                "baseline_method": "Dense",
                "structural_method": "Full",
                "baseline_f1": float(row["dense_f1"]),
                "structural_f1": float(row["full_f1"]),
                "baseline_em": float(row["dense_em"]),
                "structural_em": float(row["full_em"]),
                "comparability_note": "matched within the same frozen boundary",
            }
        )
    for label, base, structural in zip(
        ["Original Full", "Cross-space sidecar", "BGE-native"],
        strong_rows[0::2],
        strong_rows[1::2],
    ):
        rows.append(
            {
                "setting_group": "Strong BGE",
                "boundary": label,
                "baseline_method": "BGE",
                "structural_method": structural["method"],
                "baseline_f1": base["dataset_equal_weight_answer_f1"],
                "structural_f1": structural["dataset_equal_weight_answer_f1"],
                "baseline_em": base["dataset_equal_weight_answer_em"],
                "structural_em": structural["dataset_equal_weight_answer_em"],
                "comparability_note": "matched within boundary; strong rows are not pooled",
            }
        )
    return rows


def draw_dumbbell(
    ax: plt.Axes,
    rows: list[dict[str, Any]],
    title: str,
    baseline_label: str,
    structural_label: str,
) -> None:
    y = np.arange(len(rows))[::-1]
    baseline = np.array([float(row["baseline_f1"]) for row in rows])
    structural = np.array([float(row["structural_f1"]) for row in rows])
    for yy, base, full in zip(y, baseline, structural):
        ax.plot([base, full], [yy, yy], color="#B7BDC3", linewidth=1.4, zorder=1)
        ax.scatter(
            base,
            yy,
            s=26,
            marker="o",
            color=COLORS["dense"] if baseline_label == "Dense" else COLORS["bge"],
            edgecolor="white",
            linewidth=0.6,
            zorder=3,
        )
        ax.scatter(
            full,
            yy,
            s=30,
            marker="D",
            color=COLORS["hgrag"],
            edgecolor="white",
            linewidth=0.6,
            zorder=3,
        )
        delta = full - base
        ax.text(
            max(base, full) + 0.004,
            yy,
            f"{delta:+.4f}",
            fontsize=6.4,
            va="center",
            color=COLORS["protected"] if delta > 0 else COLORS["unprotected"],
            fontweight="bold",
        )
    ax.set_yticks(y)
    ax.set_yticklabels([row["boundary"] for row in rows])
    lo = min(baseline.min(), structural.min())
    hi = max(baseline.max(), structural.max())
    ax.set_xlim(lo - 0.025, hi + 0.045)
    ax.set_ylim(-0.58, len(rows) - 0.48)
    ax.set_xlabel("Answer F1")
    ax.set_title(title, loc="left", fontweight="bold")
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.45)
    handles = [
        plt.Line2D(
            [0],
            [0],
            marker="o",
            linestyle="",
            markerfacecolor=COLORS["dense"] if baseline_label == "Dense" else COLORS["bge"],
            markeredgecolor="white",
            markersize=5,
            label=baseline_label,
        ),
        plt.Line2D(
            [0],
            [0],
            marker="D",
            linestyle="",
            markerfacecolor=COLORS["hgrag"],
            markeredgecolor="white",
            markersize=5,
            label=structural_label,
        ),
    ]
    ax.legend(
        handles=handles,
        loc="lower right",
        ncol=2,
        handletextpad=0.3,
        columnspacing=0.7,
        borderaxespad=0.2,
        fontsize=6.0,
    )


def figure2_redesigned(
    effects: list[dict[str, Any]],
    compact_rows: list[dict[str, Any]],
    strong_rows: list[dict[str, Any]],
) -> list[Path]:
    performance = main_performance_rows(compact_rows, strong_rows)
    write_csv(
        SOURCE / "figure2_main_performance.csv",
        list(performance[0]),
        performance,
    )
    write_csv(
        SOURCE / "figure2_effect_size_forest.csv",
        list(effects[0]),
        effects,
    )

    fig = plt.figure(figsize=(10.2, 6.1))
    grid = fig.add_gridspec(
        2,
        2,
        width_ratios=[0.92, 1.70],
        height_ratios=[1, 1],
        wspace=0.48,
        hspace=0.55,
    )
    ax_compact = fig.add_subplot(grid[0, 0])
    ax_strong = fig.add_subplot(grid[1, 0])
    ax_forest = fig.add_subplot(grid[:, 1])

    draw_dumbbell(
        ax_compact,
        performance[:3],
        "Compact MiniLM boundaries",
        "Dense",
        "Full",
    )
    draw_dumbbell(
        ax_strong,
        performance[3:],
        "Strong-BGE boundaries (not pooled)",
        "BGE",
        "Structural variant",
    )
    add_panel_label(ax_compact, "a")
    add_panel_label(ax_strong, "b")

    family_order = [
        "Compact / HotpotQA",
        "Compact / MuSiQue",
        "Compact / joint",
        "Compact component",
        "Compact protection",
        "Cross-space placement",
        "Cross-space facet",
        "BGE-native placement",
        "BGE-native facet",
        "Generator transfer",
        "Strong baseline",
        "Cross-space sidecar",
        "BGE-native",
    ]
    by_family = {row["evidence_family"]: row for row in effects}
    ordered = [by_family[name] for name in family_order]
    labels = {
        "Compact / HotpotQA": "HotpotQA: Full - Dense",
        "Compact / MuSiQue": "MuSiQue: Full - Dense",
        "Compact / joint": "Joint: Full - Dense",
        "Compact component": "MiniLM: Full - NoFacet",
        "Compact protection": "MiniLM: Full - NoProtection",
        "Cross-space placement": "Sidecar: Protected - Unprotected",
        "Cross-space facet": "Sidecar: Protected - NoFacet",
        "BGE-native placement": "Native: Protected - Unprotected",
        "BGE-native facet": "Native: Protected - NoFacet",
        "Generator transfer": "Gemma: Full - Dense",
        "Strong baseline": "Original Full - BGE",
        "Cross-space sidecar": "Sidecar Protected - BGE",
        "BGE-native": "Native Protected - BGE",
    }
    y = np.arange(len(ordered))[::-1]
    group_spans = [
        (0, 2, COLORS["pale_blue"], "compact effectiveness"),
        (3, 8, COLORS["pale_violet"], "component / placement"),
        (9, 9, COLORS["pale_gray"], "generator transfer"),
        (10, 12, COLORS["pale_orange"], "strong-retriever boundary"),
    ]
    for start, end, color, group_label in group_spans:
        y_high = y[start] + 0.48
        y_low = y[end] - 0.48
        ax_forest.axhspan(y_low, y_high, color=color, alpha=0.62, zorder=0)
        ax_forest.text(
            -0.059,
            y_high - 0.12,
            group_label,
            fontsize=5.9,
            color="#5D6870",
            va="top",
        )

    for yy, row in zip(y, ordered):
        point = float(row["delta_answer_f1"])
        low = float(row["ci95_lower"])
        high = float(row["ci95_upper"])
        status = row["status"]
        if status == "SUPPORTED":
            marker, color, face = "o", COLORS["protected"], COLORS["protected"]
        elif status == "NEGATIVE":
            marker, color, face = "D", COLORS["unprotected"], COLORS["unprotected"]
        else:
            marker, color, face = "o", COLORS["inconclusive"], "white"
        ax_forest.plot([low, high], [yy, yy], color=color, linewidth=1.25, zorder=2)
        ax_forest.plot(
            point,
            yy,
            marker=marker,
            markersize=4.8,
            markerfacecolor=face,
            markeredgecolor=color,
            markeredgewidth=1.0,
            linestyle="",
            zorder=3,
        )
        ax_forest.text(
            0.036,
            yy,
            f"{point:+.4f} [{low:+.4f}, {high:+.4f}]",
            fontsize=5.8,
            va="center",
            ha="left",
            clip_on=False,
            color=COLORS["ink"],
        )
    ax_forest.axvline(0, color=COLORS["ink"], linewidth=0.8, linestyle="--")
    ax_forest.set_yticks(y)
    ax_forest.set_yticklabels([labels[row["evidence_family"]] for row in ordered])
    ax_forest.set_xlim(-0.060, 0.035)
    ax_forest.set_xlabel("Paired answer-F1 difference (95% bootstrap CI)")
    ax_forest.set_title("All confirmatory answer-F1 effects", loc="left", fontweight="bold")
    ax_forest.grid(axis="x", color=COLORS["grid"], linewidth=0.45)
    add_panel_label(ax_forest, "c")
    fig.subplots_adjust(left=0.10, right=0.86, top=0.96, bottom=0.09)
    return save(fig, "figure2_main_performance_and_effects")


def coverage_utility_rows(
    compact_rows: list[dict[str, Any]],
    strong_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for label, row in zip(["HotpotQA", "MuSiQue", "Joint"], compact_rows):
        rows.append(
            {
                "setting_group": "Compact MiniLM",
                "boundary": label,
                "delta_answer_f1": float(row["full_f1"]) - float(row["dense_f1"]),
                "delta_cr20": float(row["full_cr20"]) - float(row["dense_cr20"]),
                "delta_er20": float(row["full_er20"]) - float(row["dense_er20"]),
                "comparability_note": "matched within the same frozen boundary",
            }
        )
    for label, base, structural in zip(
        ["Original Full", "Cross-space sidecar", "BGE-native"],
        strong_rows[0::2],
        strong_rows[1::2],
    ):
        rows.append(
            {
                "setting_group": "Strong BGE",
                "boundary": label,
                "delta_answer_f1": (
                    structural["dataset_equal_weight_answer_f1"]
                    - base["dataset_equal_weight_answer_f1"]
                ),
                "delta_cr20": (
                    structural["dataset_equal_weight_retrieval_cr20"]
                    - base["dataset_equal_weight_retrieval_cr20"]
                ),
                "delta_er20": (
                    structural["dataset_equal_weight_retrieval_er20"]
                    - base["dataset_equal_weight_retrieval_er20"]
                ),
                "comparability_note": "matched within boundary; strong rows are not pooled",
            }
        )
    return rows


def figure3_redesigned(
    effects: list[dict[str, Any]],
    compact_rows: list[dict[str, Any]],
    strong_rows: list[dict[str, Any]],
    displacement: list[dict[str, Any]],
) -> list[Path]:
    coverage = coverage_utility_rows(compact_rows, strong_rows)
    component_families = {
        "Compact component",
        "Compact protection",
        "Cross-space placement",
        "Cross-space facet",
        "BGE-native placement",
        "BGE-native facet",
    }
    components = [
        row for row in effects if row["evidence_family"] in component_families
    ]
    query_counts = {"HotpotQA": 1000, "MuSiQue": 1500}
    displacement_norm = []
    for row in displacement:
        n = query_counts[row["dataset"]]
        displacement_norm.append(
            {
                **row,
                "queries": n,
                "added_gold_per_1000_queries": 1000 * row["added_gold"] / n,
                "displaced_gold_per_1000_queries": 1000
                * row["displaced_gold"]
                / n,
                "net_gold_per_1000_queries": 1000 * row["net_gold"] / n,
            }
        )
    write_csv(
        SOURCE / "figure3a_coverage_utility.csv",
        list(coverage[0]),
        coverage,
    )
    write_csv(
        SOURCE / "figure3b_component_effects.csv",
        list(components[0]),
        components,
    )
    write_csv(
        SOURCE / "figure3c_evidence_displacement.csv",
        list(displacement_norm[0]),
        displacement_norm,
    )

    fig, axes = plt.subplots(2, 2, figsize=(8.5, 6.2))
    ax_cr, ax_er, ax_component, ax_disp = axes.ravel()
    short = {
        "HotpotQA": "HP",
        "MuSiQue": "MQ",
        "Joint": "Joint",
        "Original Full": "Original",
        "Cross-space sidecar": "Sidecar",
        "BGE-native": "Native",
    }
    for ax, x_field, x_label, panel in [
        (ax_cr, "delta_cr20", "Change in CR@20", "a"),
        (ax_er, "delta_er20", "Change in ER@20", "b"),
    ]:
        for idx, row in enumerate(coverage):
            compact = row["setting_group"] == "Compact MiniLM"
            ax.scatter(
                row[x_field],
                row["delta_answer_f1"],
                s=36,
                marker="o" if compact else "D",
                facecolor=COLORS["hgrag"] if compact else COLORS["facet"],
                edgecolor="white",
                linewidth=0.7,
                zorder=3,
            )
            ax.annotate(
                short[row["boundary"]],
                (row[x_field], row["delta_answer_f1"]),
                xytext=(4, 5 if idx % 2 == 0 else -9),
                textcoords="offset points",
                fontsize=6.1,
                color=COLORS["ink"],
            )
        ax.axhline(0, color="#7A7F87", linewidth=0.7, linestyle="--")
        ax.axvline(0, color="#7A7F87", linewidth=0.7, linestyle="--")
        ax.set_xlabel(x_label)
        ax.set_ylabel("Change in answer F1")
        ax.grid(color=COLORS["grid"], linewidth=0.4)
        add_panel_label(ax, panel)
    ax_cr.set_title("Coverage change vs answer utility", loc="left", fontweight="bold")
    ax_er.set_title("Evidence-recall change vs answer utility", loc="left", fontweight="bold")

    component_order = [
        "Compact component",
        "Compact protection",
        "Cross-space placement",
        "Cross-space facet",
        "BGE-native placement",
        "BGE-native facet",
    ]
    component_by = {row["evidence_family"]: row for row in components}
    component_rows = [component_by[name] for name in component_order]
    component_labels = [
        "MiniLM facet",
        "MiniLM protection",
        "Sidecar placement",
        "Sidecar facet",
        "Native placement",
        "Native facet",
    ]
    y = np.arange(len(component_rows))[::-1]
    for yy, row in zip(y, component_rows):
        point = row["delta_answer_f1"]
        low = row["ci95_lower"]
        high = row["ci95_upper"]
        resolved = row["status"] == "SUPPORTED"
        color = COLORS["protected"] if resolved else COLORS["inconclusive"]
        ax_component.plot([low, high], [yy, yy], color=color, linewidth=1.25)
        ax_component.plot(
            point,
            yy,
            "o",
            markersize=4.8,
            markerfacecolor=color if resolved else "white",
            markeredgecolor=color,
        )
    ax_component.axvline(0, color=COLORS["ink"], linewidth=0.8, linestyle="--")
    ax_component.set_yticks(y)
    ax_component.set_yticklabels(component_labels)
    ax_component.set_xlim(-0.022, 0.028)
    ax_component.set_xlabel("Paired answer-F1 difference (95% CI)")
    ax_component.set_title("Matched component effects", loc="left", fontweight="bold")
    ax_component.grid(axis="x", color=COLORS["grid"], linewidth=0.4)
    add_panel_label(ax_component, "c")

    y = np.arange(len(displacement_norm))[::-1]
    for yy, row in zip(y, displacement_norm):
        added = row["added_gold_per_1000_queries"]
        displaced = row["displaced_gold_per_1000_queries"]
        ax_disp.plot([added, displaced], [yy, yy], color="#B7BDC3", linewidth=1.2)
        ax_disp.plot(added, yy, "o", color=COLORS["hgrag"], markersize=4.8)
        ax_disp.plot(displaced, yy, "D", color=COLORS["unprotected"], markersize=4.5)
        ax_disp.text(
            max(added, displaced) + 1.0,
            yy,
            f'net {row["net_gold_per_1000_queries"]:+.1f}',
            fontsize=6.1,
            va="center",
        )
    ax_disp.set_yticks(y)
    ax_disp.set_yticklabels(
        [
            f'{row["frozen_boundary"].replace("Stage", "S")}\n{row["dataset"]}'
            for row in displacement_norm
        ]
    )
    ax_disp.set_xlabel("Gold evidence events per 1,000 queries")
    ax_disp.set_title("Post-decision evidence turnover", loc="left", fontweight="bold")
    ax_disp.grid(axis="x", color=COLORS["grid"], linewidth=0.4)
    handles = [
        plt.Line2D([0], [0], marker="o", linestyle="", color=COLORS["hgrag"], label="added"),
        plt.Line2D([0], [0], marker="D", linestyle="", color=COLORS["unprotected"], label="displaced"),
    ]
    ax_disp.legend(handles=handles, loc="lower right", ncol=2)
    add_panel_label(ax_disp, "d")
    fig.tight_layout(pad=1.1, w_pad=2.0, h_pad=2.0)
    return save(fig, "figure3_coverage_utility_and_ablation")


def equal_weight_cell_percentages(
    rows: list[dict[str, Any]],
    row_key,
    column_key,
    row_categories: list[str],
    column_categories: list[str],
) -> tuple[list[dict[str, Any]], np.ndarray]:
    by_dataset: dict[str, Counter[tuple[str, str]]] = defaultdict(Counter)
    totals: Counter[str] = Counter()
    for row in rows:
        dataset = row["dataset"]
        by_dataset[dataset][(row_key(row), column_key(row))] += 1
        totals[dataset] += 1
    output: list[dict[str, Any]] = []
    matrix = np.zeros((len(row_categories), len(column_categories)))
    datasets = sorted(by_dataset)
    for i, row_category in enumerate(row_categories):
        for j, column_category in enumerate(column_categories):
            percentages = []
            for dataset in datasets:
                percent = (
                    100
                    * by_dataset[dataset][(row_category, column_category)]
                    / totals[dataset]
                )
                percentages.append(percent)
                output.append(
                    {
                        "dataset": dataset,
                        "row_category": row_category,
                        "column_category": column_category,
                        "query_percent": percent,
                    }
                )
            matrix[i, j] = sum(percentages) / len(percentages)
            output.append(
                {
                    "dataset": "DATASET_EQUAL_WEIGHT",
                    "row_category": row_category,
                    "column_category": column_category,
                    "query_percent": matrix[i, j],
                }
            )
    return output, matrix


def figure4_redesigned(data: dict[str, Any]) -> list[Path]:
    stage4h = list(jsonl_rows(data["stage4h_trace"]))
    stage4i = list(jsonl_rows(data["stage4i_trace"]))
    stage5a = list(jsonl_rows(data["stage5a_trace"]))

    edge_categories = ["0", "1", "2", "3+"]
    insert_categories = ["0", "1", "2", "3", "4"]
    edge_rows, edge_matrix = equal_weight_cell_percentages(
        stage4h,
        lambda row: str(row["full_selected_edge_count"])
        if row["full_selected_edge_count"] < 3
        else "3+",
        lambda row: str(min(row["full_insert_count"], 4)),
        edge_categories,
        insert_categories,
    )

    def facet_bin(value: int) -> str:
        if value <= 3:
            return "0-3"
        if value <= 6:
            return "4-6"
        if value <= 9:
            return "7-9"
        return "10+"

    facet_categories = ["0-3", "4-6", "7-9", "10+"]
    eligible_categories = ["0", "1", "2", "3", "4+"]
    facet_rows, facet_matrix = equal_weight_cell_percentages(
        stage5a,
        lambda row: facet_bin(int(row["topology"]["query_facet_count"])),
        lambda row: (
            str(row["facet"]["eligible_candidate_count"])
            if row["facet"]["eligible_candidate_count"] < 4
            else "4+"
        ),
        facet_categories,
        eligible_categories,
    )

    insertion_specs = [
        (
            "Compact Full",
            stage4h,
            lambda row: int(row["full_insert_count"]),
        ),
        (
            "Cross-space sidecar",
            stage4i,
            lambda row: int(row["full_insert_count"]),
        ),
        (
            "BGE-native",
            stage5a,
            lambda row: len(row["inserted_unit_ids"]),
        ),
    ]
    insertion_rows: list[dict[str, Any]] = []
    for setting, records, getter in insertion_specs:
        by_dataset: dict[str, Counter[int]] = defaultdict(Counter)
        totals: Counter[str] = Counter()
        for row in records:
            dataset = row["dataset"]
            by_dataset[dataset][min(getter(row), 4)] += 1
            totals[dataset] += 1
        for count in range(5):
            percentages = []
            for dataset in sorted(by_dataset):
                percent = 100 * by_dataset[dataset][count] / totals[dataset]
                percentages.append(percent)
                insertion_rows.append(
                    {
                        "setting": setting,
                        "dataset": dataset,
                        "inserted_unit_count": count,
                        "query_percent": percent,
                    }
                )
            insertion_rows.append(
                {
                    "setting": setting,
                    "dataset": "DATASET_EQUAL_WEIGHT",
                    "inserted_unit_count": count,
                    "query_percent": sum(percentages) / len(percentages),
                }
            )

    overlap_rows = []
    for dataset in sorted({row["dataset"] for row in stage4i}):
        selected = [row for row in stage4i if row["dataset"] == dataset]
        top10 = sum(int(row["full_overlap_bge_top10_count"]) for row in selected)
        top20 = sum(int(row["full_overlap_bge_top20_count"]) for row in selected)
        eligible = sum(int(row["full_eligible_count"]) for row in selected)
        counts = {
            "already in BGE Top-10": top10,
            "only in BGE ranks 11-20": max(top20 - top10, 0),
            "beyond BGE Top-20": max(eligible - top20, 0),
        }
        total = sum(counts.values())
        for region, count in counts.items():
            overlap_rows.append(
                {
                    "dataset": dataset,
                    "candidate_region": region,
                    "candidate_count": count,
                    "candidate_percent": 100 * count / total if total else 0.0,
                    "evidence_role": "GOLD_FREE_DESCRIPTIVE",
                }
            )

    write_csv(
        SOURCE / "figure4a_edge_insertion_matrix.csv",
        list(edge_rows[0]),
        edge_rows,
    )
    write_csv(
        SOURCE / "figure4b_facet_supply_matrix.csv",
        list(facet_rows[0]),
        facet_rows,
    )
    write_csv(
        SOURCE / "figure4c_insertion_distribution.csv",
        list(insertion_rows[0]),
        insertion_rows,
    )
    write_csv(
        SOURCE / "figure4d_sidecar_overlap.csv",
        list(overlap_rows[0]),
        overlap_rows,
    )

    fig, axes = plt.subplots(2, 2, figsize=(8.4, 6.3))
    ax_edge, ax_facet, ax_insert, ax_overlap = axes.ravel()
    cmap_blue = matplotlib.colors.LinearSegmentedColormap.from_list(
        "hgrag_blue",
        ["#F7FAFC", "#A9D4E8", COLORS["hgrag"]],
    )
    cmap_violet = matplotlib.colors.LinearSegmentedColormap.from_list(
        "hgrag_violet",
        ["#FBF9FD", "#D6C5E5", COLORS["facet"]],
    )
    for ax, matrix, xlabels, ylabels, cmap, panel, title in [
        (
            ax_edge,
            edge_matrix,
            insert_categories,
            edge_categories,
            cmap_blue,
            "a",
            "Facet-hyperedge selection and insertion",
        ),
        (
            ax_facet,
            facet_matrix,
            eligible_categories,
            facet_categories,
            cmap_violet,
            "b",
            "Query facets and eligible candidates",
        ),
    ]:
        image = ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0)
        for (i, j), value in np.ndenumerate(matrix):
            ax.text(
                j,
                i,
                f"{value:.1f}",
                ha="center",
                va="center",
                fontsize=6.1,
                color="white" if value > matrix.max() * 0.58 else COLORS["ink"],
            )
        ax.set_xticks(range(len(xlabels)))
        ax.set_xticklabels(xlabels)
        ax.set_yticks(range(len(ylabels)))
        ax.set_yticklabels(ylabels)
        ax.set_title(title, loc="left", fontweight="bold")
        ax.set_frame_on(False)
        cbar = fig.colorbar(image, ax=ax, fraction=0.045, pad=0.03)
        cbar.set_label("Dataset-equal-weight query share (%)", fontsize=6.2)
        cbar.ax.tick_params(labelsize=5.8)
        add_panel_label(ax, panel)
    ax_edge.set_xlabel("Inserted units")
    ax_edge.set_ylabel("Selected hyperedges")
    ax_facet.set_xlabel("Eligible structural candidates")
    ax_facet.set_ylabel("Query-facet count")

    setting_colors = {
        "Compact Full": COLORS["hgrag"],
        "Cross-space sidecar": COLORS["facet"],
        "BGE-native": COLORS["bge"],
    }
    for setting in setting_colors:
        subset = [
            row
            for row in insertion_rows
            if row["setting"] == setting
            and row["dataset"] == "DATASET_EQUAL_WEIGHT"
        ]
        ax_insert.plot(
            [row["inserted_unit_count"] for row in subset],
            [row["query_percent"] for row in subset],
            marker="o",
            linewidth=1.4,
            markersize=4.2,
            color=setting_colors[setting],
            label=setting,
        )
    ax_insert.set_xticks(range(5))
    ax_insert.set_xlabel("Inserted units per query")
    ax_insert.set_ylabel("Dataset-equal-weight query share (%)")
    ax_insert.set_title("Bounded insertion remains sparse", loc="left", fontweight="bold")
    ax_insert.grid(axis="y", color=COLORS["grid"], linewidth=0.4)
    ax_insert.legend(loc="upper right")
    add_panel_label(ax_insert, "c")

    dataset_labels = {
        "hotpotqa_train_distractor_v1_1": "HotpotQA",
        "musique_ans_v1_0_train": "MuSiQue",
    }
    regions = [
        "already in BGE Top-10",
        "only in BGE ranks 11-20",
        "beyond BGE Top-20",
    ]
    region_colors = [COLORS["bge"], "#8EA0C7", COLORS["hgrag"]]
    datasets = sorted(dataset_labels, key=lambda value: dataset_labels[value])
    left = np.zeros(len(datasets))
    for region, color in zip(regions, region_colors):
        values = [
            next(
                row["candidate_percent"]
                for row in overlap_rows
                if row["dataset"] == dataset
                and row["candidate_region"] == region
            )
            for dataset in datasets
        ]
        ax_overlap.barh(
            np.arange(len(datasets)),
            values,
            left=left,
            color=color,
            edgecolor="white",
            linewidth=0.5,
            label=region,
        )
        left += np.array(values)
    ax_overlap.set_yticks(np.arange(len(datasets)))
    ax_overlap.set_yticklabels([dataset_labels[dataset] for dataset in datasets])
    ax_overlap.set_xlim(0, 100)
    ax_overlap.set_xlabel("Sidecar eligible-candidate share (%)")
    ax_overlap.set_title("Candidate overlap with BGE", loc="left", fontweight="bold")
    ax_overlap.legend(loc="lower center", bbox_to_anchor=(0.5, -0.45), ncol=1)
    add_panel_label(ax_overlap, "d")
    fig.tight_layout(pad=1.1, w_pad=1.8, h_pad=2.0)
    return save(fig, "figure4_mechanism_analysis")


def qualitative_case_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    audits = {row["query_id"]: row for row in jsonl_rows(data["stage4h_query_audit"])}
    rankings = {row["query_id"]: row for row in jsonl_rows(data["stage4h_rankings"])}
    blind = {row["query_id"]: row for row in jsonl_rows(data["stage4h_blind_queries"])}
    gold = {row["query_id"]: row for row in jsonl_rows(data["stage4h_gold_targets"])}
    predictions = {
        (row["query_id"], row["method"]): row["prediction"]
        for row in jsonl_rows(data["stage4h_predictions"])
    }
    query_ids = sorted(
        query_id
        for query_id in set(audits) & set(rankings) & set(blind) & set(gold)
        if isinstance(gold[query_id].get("supporting_unit_ids"), list)
    )
    success_candidates = []
    failure_candidates = []
    for query_id in query_ids:
        audit = audits[query_id]["methods"]
        ranking = rankings[query_id]
        methods = ranking["methods"]
        supporting = set(gold[query_id]["supporting_unit_ids"])
        inserted = set(ranking["full_inserted_unit_ids"])
        success_delta = (
            audit["STATIC_Q25_FULL"]["answer_f1"]
            - audit["DENSE_TOP20"]["answer_f1"]
        )
        if (
            success_delta > 0
            and audit["STATIC_Q25_FULL"]["retrieval_cr20"]
            > audit["DENSE_TOP20"]["retrieval_cr20"]
            and inserted & supporting
        ):
            success_candidates.append((success_delta, query_id))

        failure_delta = (
            audit["STATIC_Q25_FULL"]["answer_f1"]
            - audit["STRONG_DENSE_TOP20"]["answer_f1"]
        )
        displaced_support = supporting & (
            set(methods["STRONG_DENSE_TOP20"]) - set(methods["STATIC_Q25_FULL"])
        )
        if failure_delta < 0 and displaced_support:
            failure_candidates.append((failure_delta, query_id))
    if not success_candidates or not failure_candidates:
        raise RuntimeError("No deterministic qualitative success/failure case is available")

    def median_case(candidates: list[tuple[float, str]]) -> str:
        median_delta = statistics.median(value for value, _ in candidates)
        return min(candidates, key=lambda item: (abs(item[0] - median_delta), item[1]))[1]

    selected = [
        ("Representative success", median_case(success_candidates)),
        ("Representative failure", median_case(failure_candidates)),
    ]
    output = []
    for case_type, query_id in selected:
        audit = audits[query_id]["methods"]
        ranking = rankings[query_id]
        methods = ranking["methods"]
        blind_row = blind[query_id]
        gold_row = gold[query_id]
        unit_by_id = {unit["unit_id"]: unit for unit in blind_row["candidate_units"]}
        supporting = set(gold_row["supporting_unit_ids"])
        inserted_ids = list(ranking["full_inserted_unit_ids"])
        if case_type == "Representative success":
            baseline_key = "DENSE_TOP20"
            baseline_name = "Dense"
            proposed_key = "STATIC_Q25_FULL"
            proposed_name = "Full"
            added_id = next(unit_id for unit_id in inserted_ids if unit_id in supporting)
            retained = [
                unit_id
                for unit_id in methods[baseline_key]
                if unit_id in supporting
            ]
            baseline_evidence_id = retained[0] if retained else methods[baseline_key][0]
        else:
            baseline_key = "STRONG_DENSE_TOP20"
            baseline_name = "BGE"
            proposed_key = "STATIC_Q25_FULL"
            proposed_name = "Original Full"
            displaced = [
                unit_id
                for unit_id in methods[baseline_key]
                if unit_id in supporting
                and unit_id not in set(methods[proposed_key])
            ]
            baseline_evidence_id = displaced[0]
            added_id = inserted_ids[0] if inserted_ids else methods[proposed_key][10]
        displaced_ids = [
            unit_id
            for unit_id in methods[baseline_key]
            if unit_id not in set(methods[proposed_key])
        ]
        displaced_id = (
            baseline_evidence_id
            if baseline_evidence_id in displaced_ids
            else (displaced_ids[0] if displaced_ids else "")
        )

        def unit_fields(unit_id: str, ranking_ids: list[str]) -> tuple[Any, ...]:
            if not unit_id:
                return ("", "", "", "")
            unit = unit_by_id[unit_id]
            rank = ranking_ids.index(unit_id) + 1 if unit_id in ranking_ids else ""
            return rank, unit["title"], unit["text"], int(unit_id in supporting)

        base_rank, base_title, base_text, base_support = unit_fields(
            baseline_evidence_id,
            methods[baseline_key],
        )
        added_rank, added_title, added_text, added_support = unit_fields(
            added_id,
            methods[proposed_key],
        )
        displaced_rank, displaced_title, displaced_text, displaced_support = unit_fields(
            displaced_id,
            methods[baseline_key],
        )
        output.append(
            {
                "case_type": case_type,
                "selection_rule": "closest to the within-event median delta F1; query_id tie-break",
                "query_id": query_id,
                "dataset": blind_row["dataset"],
                "question": blind_row["question"],
                "baseline_method": baseline_name,
                "baseline_answer": predictions[(query_id, baseline_key)],
                "baseline_f1": audit[baseline_key]["answer_f1"],
                "proposed_method": proposed_name,
                "proposed_answer": predictions[(query_id, proposed_key)],
                "proposed_f1": audit[proposed_key]["answer_f1"],
                "delta_answer_f1": (
                    audit[proposed_key]["answer_f1"]
                    - audit[baseline_key]["answer_f1"]
                ),
                "reference_answer": gold_row["answers"][0],
                "baseline_evidence_rank": base_rank,
                "baseline_evidence_title": base_title,
                "baseline_evidence_text": base_text,
                "baseline_evidence_supporting": base_support,
                "added_evidence_rank": added_rank,
                "added_evidence_title": added_title,
                "added_evidence_text": added_text,
                "added_evidence_supporting": added_support,
                "displaced_evidence_rank": displaced_rank,
                "displaced_evidence_title": displaced_title,
                "displaced_evidence_text": displaced_text,
                "displaced_evidence_supporting": displaced_support,
                "evidence_role": "POST_DECISION_DESCRIPTIVE_ONLY",
            }
        )
    return output


def figure5_redesigned(data: dict[str, Any]) -> list[Path]:
    rows = qualitative_case_rows(data)
    write_csv(
        SOURCE / "figure5_qualitative_cases.csv",
        list(rows[0]),
        rows,
    )

    fig, ax = plt.subplots(figsize=(8.5, 5.7))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    columns = [
        (0.015, 0.215, "Question"),
        (0.235, 0.215, "Baseline evidence and answer"),
        (0.455, 0.285, "Structural change"),
        (0.745, 0.24, "Full output"),
    ]

    def display_text(value: Any) -> str:
        """Keep raw CSV text intact while avoiding unavailable Khmer glyphs in plots."""
        rendered = re.sub(
            r"Khmer:\s*[\u1780-\u17ff\s]+(?=;)",
            "Khmer: [Khmer script] ",
            str(value),
        )
        return re.sub(r"[\u1780-\u17ff]+", "[Khmer script]", rendered)
    for x, width, title in columns:
        ax.text(
            x + width / 2,
            0.985,
            title,
            ha="center",
            va="top",
            fontsize=7.1,
            fontweight="bold",
            color=COLORS["ink"],
        )

    def card(
        x: float,
        y: float,
        width: float,
        height: float,
        facecolor: str,
        title: str,
        body: str,
    ) -> None:
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                width,
                height,
                boxstyle="round,pad=0.008,rounding_size=0.012",
                facecolor=facecolor,
                edgecolor="#B9C0C5",
                linewidth=0.7,
            )
        )
        ax.text(
            x + 0.012,
            y + height - 0.025,
            title,
            ha="left",
            va="top",
            fontsize=6.5,
            fontweight="bold",
            color=COLORS["ink"],
        )
        ax.text(
            x + 0.012,
            y + height - 0.065,
            body,
            ha="left",
            va="top",
            fontsize=5.8,
            color=COLORS["ink"],
            linespacing=1.25,
        )

    for idx, row in enumerate(rows):
        y = 0.525 if idx == 0 else 0.055
        height = 0.395
        accent = COLORS["protected"] if idx == 0 else COLORS["unprotected"]
        ax.add_patch(plt.Rectangle((0.006, y), 0.006, height, color=accent))
        ax.text(
            0.016,
            y + height + 0.012,
            f'{"a" if idx == 0 else "b"}  {row["case_type"]} '
            f'(delta F1 {row["delta_answer_f1"]:+.2f})',
            fontsize=7.2,
            fontweight="bold",
            color=accent,
            va="bottom",
        )
        dataset = "HotpotQA" if "hotpotqa" in row["dataset"] else "MuSiQue"
        card(
            columns[0][0],
            y,
            columns[0][1],
            height,
            COLORS["pale_gray"],
            dataset,
            textwrap.fill(display_text(row["question"]), width=33),
        )
        baseline_body = (
            f'Rank {row["baseline_evidence_rank"]}: '
            f'{textwrap.shorten(display_text(row["baseline_evidence_title"]), 34)}\n'
            f'{textwrap.fill(textwrap.shorten(display_text(row["baseline_evidence_text"]), 175), 34)}\n\n'
            f'Answer: {textwrap.shorten(display_text(row["baseline_answer"]), 40)}\n'
            f'F1 = {row["baseline_f1"]:.2f}'
        )
        card(
            columns[1][0],
            y,
            columns[1][1],
            height,
            "#EEF0F2",
            row["baseline_method"],
            baseline_body,
        )
        added = (
            f'ADDED (rank {row["added_evidence_rank"]}; '
            f'supporting={bool(row["added_evidence_supporting"])})\n'
            f'{textwrap.shorten(display_text(row["added_evidence_title"]), 42)}\n'
            f'{textwrap.fill(textwrap.shorten(display_text(row["added_evidence_text"]), 150), 42)}'
        )
        displaced = (
            f'\n\nDISPLACED'
            + (
                f' (rank {row["displaced_evidence_rank"]}; '
                f'supporting={bool(row["displaced_evidence_supporting"])})\n'
                f'{textwrap.shorten(display_text(row["displaced_evidence_title"]), 42)}\n'
                f'{textwrap.fill(textwrap.shorten(display_text(row["displaced_evidence_text"]), 120), 42)}'
                if row["displaced_evidence_title"]
                else ": none shown"
            )
        )
        card(
            columns[2][0],
            y,
            columns[2][1],
            height,
            COLORS["pale_blue"] if idx == 0 else COLORS["pale_orange"],
            "Evidence completion",
            added + displaced,
        )
        output_body = (
            f'Answer: {textwrap.fill(display_text(row["proposed_answer"]), 34)}\n'
            f'F1 = {row["proposed_f1"]:.2f}\n\n'
            f'Reference:\n{textwrap.fill(display_text(row["reference_answer"]), 34)}'
        )
        card(
            columns[3][0],
            y,
            columns[3][1],
            height,
            "#EDF5FA" if idx == 0 else "#F9EEE7",
            row["proposed_method"],
            output_body,
        )
    fig.tight_layout(pad=0.4)
    return save(fig, "figure5_qualitative_cases")


def fmt_effect(point: float, low: float, high: float) -> str:
    return f"{point:+.5f} [{low:.5f}, {high:.5f}]"


def jsonl_rows(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            row = json.loads(line)
            if not isinstance(row, dict):
                raise RuntimeError(f"{path.name}:{line_number} is not a JSON object")
            yield row


def insertion_and_f1_counts(
    ranking_path: Path,
    query_audit_path: Path,
    insertion_key: str,
    dense_key: str,
    full_key: str,
    nested_methods: bool,
) -> dict[str, Any]:
    insert_counts: list[int] = []
    for row in jsonl_rows(ranking_path):
        inserted = row.get(insertion_key)
        if not isinstance(inserted, list):
            raise RuntimeError(f"{ranking_path.name}: invalid {insertion_key}")
        insert_counts.append(len(inserted))

    gain = harm = same = 0
    for row in jsonl_rows(query_audit_path):
        methods = row.get("methods") if nested_methods else row
        if not isinstance(methods, dict):
            raise RuntimeError(f"{query_audit_path.name}: invalid methods object")
        dense = methods[dense_key]["answer_f1"]
        full = methods[full_key]["answer_f1"]
        if full > dense:
            gain += 1
        elif full < dense:
            harm += 1
        else:
            same += 1

    if len(insert_counts) != gain + harm + same:
        raise RuntimeError("Ranking and query-audit row counts differ")
    return {
        "queries": len(insert_counts),
        "avg_inserted_units": sum(insert_counts) / len(insert_counts),
        "inserted_queries": sum(value > 0 for value in insert_counts),
        "f1_gain_queries": gain,
        "f1_harm_queries": harm,
        "f1_same_queries": same,
    }


def compact_absolute_rows(data: dict[str, Any], effects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    effect_by_boundary = {row["evidence_family"]: row for row in effects}
    specs: list[tuple[str, str, dict[str, Any], dict[str, Any]]] = []

    stage4e = data["stage4e_summary"]["methods"]
    specs.append(
        (
            "MiniLM / HotpotQA confirmation",
            "Compact / HotpotQA",
            stage4e["DENSE_TOP20"],
            stage4e["STATIC_Q25_TOP20"],
        )
    )
    stage4f = data["stage4f_summary"]["methods"]
    specs.append(
        (
            "MiniLM / MuSiQue confirmation",
            "Compact / MuSiQue",
            stage4f["DENSE_TOP20"],
            stage4f["STATIC_Q25_TOP20"],
        )
    )

    stage4h = data["stage4h_datasets"]
    dataset_names = (
        "hotpotqa_train_distractor_v1_1",
        "musique_ans_v1_0_train",
    )

    def equal_weight(method: str) -> dict[str, float]:
        return {
            metric_name: sum(
                float(stage4h[dataset]["methods"][method][metric_name])
                for dataset in dataset_names
            )
            / len(dataset_names)
            for metric_name in (
                "answer_f1",
                "answer_em",
                "retrieval_cr20",
                "retrieval_er20",
            )
        }

    specs.append(
        (
            "MiniLM / joint component confirmation",
            "Compact / joint",
            equal_weight("DENSE_TOP20"),
            equal_weight("STATIC_Q25_FULL"),
        )
    )

    diagnostics = [
        insertion_and_f1_counts(
            data["stage4e_rankings"],
            data["stage4e_query_audit"],
            "q25_inserted_unit_ids",
            "dense",
            "static_q25",
            False,
        ),
        insertion_and_f1_counts(
            data["stage4f_rankings"],
            data["stage4f_query_audit"],
            "q25_inserted_unit_ids",
            "dense_top20",
            "static_q25_top20",
            False,
        ),
        insertion_and_f1_counts(
            data["stage4h_rankings"],
            data["stage4h_query_audit"],
            "full_inserted_unit_ids",
            "DENSE_TOP20",
            "STATIC_Q25_FULL",
            True,
        ),
    ]

    rows = []
    for (boundary, effect_key, dense, full), diag in zip(specs, diagnostics):
        effect = effect_by_boundary[effect_key]
        rows.append(
            {
                "boundary": boundary,
                "queries": diag["queries"],
                "dense_f1": f'{dense["answer_f1"]:.5f}',
                "full_f1": f'{full["answer_f1"]:.5f}',
                "dense_em": f'{dense["answer_em"]:.5f}',
                "full_em": f'{full["answer_em"]:.5f}',
                "dense_cr20": f'{dense["retrieval_cr20"]:.5f}',
                "full_cr20": f'{full["retrieval_cr20"]:.5f}',
                "dense_er20": f'{dense["retrieval_er20"]:.5f}',
                "full_er20": f'{full["retrieval_er20"]:.5f}',
                "avg_inserted_units": f'{diag["avg_inserted_units"]:.4f}',
                "f1_gain_harm_queries": (
                    f'{diag["f1_gain_queries"]}/{diag["f1_harm_queries"]}'
                ),
                "delta_f1_ci": fmt_effect(
                    effect["delta_answer_f1"],
                    effect["ci95_lower"],
                    effect["ci95_upper"],
                ),
            }
        )
    return rows


def make_table_rows(data: dict[str, Any], effects: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    table1 = compact_absolute_rows(data, effects)
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
        if r["evidence_family"]
        in {
            "Compact component",
            "Compact protection",
            "Cross-space placement",
            "Cross-space facet",
            "BGE-native placement",
            "BGE-native facet",
        }
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
    table6 = []
    for row in absolute_rows(data):
        table6.append(
            {
                "boundary": row["frozen_boundary"],
                "method": row["method"],
                "equal_weight_f1": f'{row["dataset_equal_weight_answer_f1"]:.5f}',
                "equal_weight_em": f'{row["dataset_equal_weight_answer_em"]:.5f}',
                "equal_weight_cr20": f'{row["dataset_equal_weight_retrieval_cr20"]:.5f}',
                "equal_weight_er20": f'{row["dataset_equal_weight_retrieval_er20"]:.5f}',
            }
        )
    return {
        "table1": table1,
        "table2": table2,
        "table3": table3,
        "table4": table4,
        "table5": table5,
        "table6": table6,
    }


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

## Table 1. Absolute compact-dense results and paired effects

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

## Table 6. Absolute strong-retriever boundary metrics

{table6}

Source CSV files are stored in
[`paper/figures_stage5r/source_data`](figures_stage5r/source_data/).
""".format(**{name: markdown_table(rows) for name, rows in tables.items()})
    TABLES.write_text(text, encoding="utf-8", newline="\n")
    return [TABLES, *csv_paths]


def write_captions() -> Path:
    path = OUT / "FIGURE_CONTRACTS_AND_CAPTIONS.md"
    text = """# Stage5R Figure Contracts and Captions

## Figure contract

- **Core conclusion:** structured evidence completion repeatedly improves the
  compact MiniLM retriever, whereas the evaluated strong-BGE extensions do not
  establish incremental answer-quality gains.
- **Archetype:** Figure 2 is a quantitative hero composite; Figures 3 and 4 are
  quantitative grids; Figure 5 is an asymmetric qualitative comparison.
- **Backend:** Python/Matplotlib only.
- **Target:** ACL/EMNLP Findings, double-column figures at approximately 175 mm.
- **Statistics:** confirmatory answer-F1 panels report the frozen paired 10,000
  sample bootstrap 95% confidence intervals. Mechanism and qualitative panels
  are explicitly descriptive.
- **Reviewer risk:** Stage4H, Stage4I, and Stage5A strong-retriever rows are
  separate frozen boundaries and are never pooled or connected as a monotonic
  retriever-strength experiment.

## Figure 1

**Overview of HyperGranular-RAG and the evaluated retrieval variants.**
Candidate units are ranked by a fixed dense retriever, organized into adaptive
granular balls, connected through query-aware facet hyperedges, and inserted
under a protected, bounded Top-k policy before answer generation. Compact,
cross-space sidecar, and BGE-native variants are evaluated separately rather
than pooled.

## Figure 2

**Main performance and paired answer-F1 effects.** Panels a and b use paired
dumbbells to compare absolute answer F1 only within each frozen boundary.
Panel c reports all confirmatory paired answer-F1 differences with 95%
bootstrap confidence intervals. Hollow points denote intervals crossing zero;
they are not equivalence claims. Strong-retriever boundaries are shown as
separate settings rather than a connected trend.

## Figure 3

**Coverage, answer utility, components, and evidence turnover.** Panels a and b
relate matched changes in CR@20 and ER@20 to answer-F1 changes without fitting a
trend line. Panel c reports matched component effects with frozen 95%
confidence intervals. Panel d normalizes post-decision added and displaced
Gold evidence events per 1,000 queries; raw counts and query denominators remain
in the source CSV. Panel d is descriptive and did not control selection.

## Figure 4

**Gold-free retrieval mechanism.** Panels a and b show dataset-equal-weight
query percentages for facet-hyperedge selection, insertion, query-facet supply,
and eligible structural candidates. Panel c reports bounded insertion-count
distributions separately for compact, sidecar, and BGE-native settings. Panel d
decomposes sidecar-eligible candidates by overlap with BGE Top-20. These panels
describe frozen retrieval behavior and do not establish causal mediation.

## Figure 5

**Representative success and failure cases.** The success case requires a
positive Full-minus-Dense answer-F1 change, a CR@20 increase, and insertion of a
supporting unit. The failure case requires a negative Original-Full-minus-BGE
answer-F1 change and displacement of a supporting unit. Within each eligible
HotpotQA sentence-level event set, the query closest to the median answer-F1
change is selected, with query ID as a deterministic tie-break. These examples
are post-decision descriptive illustrations, not confirmatory evidence. The
source CSV preserves the frozen text verbatim; the rendered panel replaces
Khmer-script spans with a neutral script label when the publication font lacks
those glyphs.

Each figure is exported as editable SVG, PDF, 600-dpi TIFF, and 300-dpi PNG.
Every plotted value has a CSV source file, and every export is byte/SHA bound in
`STAGE5R_FIGURE_MANIFEST.json`.
"""
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def write_manifest(derived: list[Path]) -> Path:
    path = OUT / "STAGE5R_FIGURE_MANIFEST.json"

    def manifest_path(item: Path) -> str:
        try:
            return item.relative_to(ROOT).as_posix()
        except ValueError:
            return item.as_posix()

    manifest = {
        "schema_version": "stage5r_pmr_figure_manifest_v2",
        "status": "STAGE5R_FIGURES_BUILT_FROM_FROZEN_STAGE4E_STAGE5A_EVIDENCE",
        "scientific_reanalysis": False,
        "descriptive_derivations_added": True,
        "confirmatory_claims_unchanged": True,
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
                "path": manifest_path(path_),
                "bytes": path_.stat().st_size,
                "sha256": sha256(path_),
            }
            for label, (path_, _) in sorted(MANIFEST_INPUTS.items())
        ],
        "builder": {
            "path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "old_frozen_builder_path": OLD_BUILDER.relative_to(ROOT).as_posix(),
            "old_frozen_builder_sha256": OLD_BUILDER_SHA256,
        },
        "figure1_replacement": {
            "active_asset": "paper/figures_stage5r/figure1_method_overview.png",
            "latex_inclusion": "PNG_WITH_BOTTOM_EMBEDDED_CAPTION_CLIPPED; ACL_CAPTION_RENDERED_ONCE",
            "scientific_reanalysis": False,
            "source_sha256": sha256(OUT / "figure1_method_overview.png"),
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
    abs_rows = absolute_rows(data)
    compact_rows = compact_absolute_rows(data, effects)
    disp_rows = displacement_rows(data)
    derived: list[Path] = []
    derived += [
        OUT / f"figure1_method_overview.{suffix}"
        for suffix in ("svg", "pdf", "tiff", "png")
    ]
    derived += figure2_redesigned(effects, compact_rows, abs_rows)
    derived += figure3_redesigned(effects, compact_rows, abs_rows, disp_rows)
    derived += figure4_redesigned(data)
    derived += figure5_redesigned(data)
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
