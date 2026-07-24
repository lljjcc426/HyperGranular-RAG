#!/usr/bin/env python3
"""Build the frozen Stage5-PMC manuscript figures from tracked Stage4E-I evidence.

This script performs no model inference, retrieval, bootstrap, or scientific
re-analysis. It verifies the SHA-256 identity of the frozen result files,
extracts already-frozen statistics, writes compact source-data CSV files, and
renders publication figures with a Python-only Matplotlib backend.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR = ROOT / "paper" / "figures"
SOURCE_DIR = FIGURE_DIR / "source_data"

INPUTS = {
    "stage4e_summary": (
        ROOT / "results" / "stage4e_e2e_official_train1000_v1_evaluation_summary.json",
        "BC6D6EF89A47B7314AEA12966894750E5733449ED76241582116451E4BFFF05E",
    ),
    "stage4e_telemetry": (
        ROOT / "results" / "stage4e_e2e_official_train1000_v1_telemetry_main.json",
        "D9971191A45F4F2BA2F6BA61716BBF9ACA707FACD66528778E73D3B203D39385",
    ),
    "stage4f_summary": (
        ROOT / "results" / "stage4f_xdr_musique_train3000_v1_evaluation_summary.json",
        "839E946A5BA5AEB5502D10867647B26B9DBA1001BF7BC27EF740056312CE6C50",
    ),
    "stage4f_telemetry": (
        ROOT / "results" / "stage4f_xdr_musique_train3000_v1_telemetry_main.json",
        "D5988004E2D3DA8E5116F3DF094B8277C60198E3CAE8A726A75B40AE5377BCA3",
    ),
    "stage4g_datasets": (
        ROOT
        / "results"
        / "stage4g_gtr_gemma_hotpot1000_musique3000_v1_dataset_summaries.json",
        "1656CEAC063EB53D4854481C83A1A4046D6257B442A3C376EDC851B5436D6E3B",
    ),
    "stage4g_equal": (
        ROOT
        / "results"
        / "stage4g_gtr_gemma_hotpot1000_musique3000_v1_equal_weight_summary.json",
        "0BF7E2658521510438545BC077DBAA1EA7C902C2FD35FFBE4013D209D7890239",
    ),
    "stage4g_telemetry": (
        ROOT
        / "results"
        / "stage4g_gtr_gemma_hotpot1000_musique3000_v1_telemetry_main.json",
        "F4B5B8E49149C692993EE4023C80A443AE608C2BBF34E627CBF256F41BDB0BA9",
    ),
    "stage4h_datasets": (
        ROOT
        / "results"
        / "stage4h_cbe_hotpot1000_musique1500_v1_dataset_summaries.json",
        "C9B2E163A46FE41B458321C8292CCF21A99C5B6AC666E3E28BA6798E013CB85B",
    ),
    "stage4h_equal": (
        ROOT
        / "results"
        / "stage4h_cbe_hotpot1000_musique1500_v1_equal_weight_summary.json",
        "0C8677960F2CB07526B36264CE58883ED28D12C0016F6EAD8A036D3DD0BE7FA4",
    ),
    "stage4h_telemetry": (
        ROOT / "results" / "stage4h_cbe_hotpot1000_musique1500_v1_telemetry_main.json",
        "5B69B732D19A0C04337AFB05FA44362BF43977C2AB1BFD6ACF4D4DAC1520E164",
    ),
    "stage4i_datasets": (
        ROOT
        / "results"
        / "stage4i_sdc_hotpot1000_musique1500_v1_dataset_summaries.json",
        "4487349198E34F0DA99A91423EDC991315909947036D6D2E11F3BCFD14DF95DF",
    ),
    "stage4i_equal": (
        ROOT
        / "results"
        / "stage4i_sdc_hotpot1000_musique1500_v1_equal_weight_summary.json",
        "EC1AF7077CDC6858CE39B76FE842E60283EB9BF19068C6384CDF8C282C9E1717",
    ),
    "stage4i_evidence": (
        ROOT
        / "results"
        / "stage4i_sdc_hotpot1000_musique1500_v1_evidence_transition_audit.json",
        "3DE05CBDAEC38EE216C9C0D5DC8834B6B6EC1726E4CDDC37B0A1132DC8611BE2",
    ),
    "stage4i_telemetry": (
        ROOT / "results" / "stage4i_sdc_hotpot1000_musique1500_v1_telemetry_main.json",
        "4B7BA469098AE1FD6805FAE724B10A89F7916B939ECDD2DBE47B416BC656E52B",
    ),
}

COLORS = {
    "dense": "#4C78A8",
    "hgrag": "#F2A65A",
    "bge": "#355C7D",
    "protected": "#62A87C",
    "unprotected": "#D98C8C",
    "no_facet": "#9C89B8",
    "positive": "#3A7D44",
    "negative": "#B24C4C",
    "inconclusive": "#8A8A8A",
    "undefined": "#B8A35D",
    "deferred": "#7C8798",
    "ink": "#263238",
    "grid": "#D9DEE3",
    "paper": "#FAFAF8",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def load_inputs() -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    for label, (path, expected_sha) in INPUTS.items():
        actual_sha = sha256(path)
        if actual_sha != expected_sha:
            raise RuntimeError(
                f"Frozen input identity mismatch for {path}: "
                f"expected {expected_sha}, got {actual_sha}"
            )
        loaded[label] = json.loads(path.read_text(encoding="utf-8"))
    return loaded


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def configure_matplotlib() -> None:
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
            "lines.linewidth": 1.2,
            "patch.linewidth": 0.7,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "svg.fonttype": "none",
            "svg.hashsalt": "stage5-pmc-v1",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def save_figure(fig: plt.Figure, stem: str) -> list[Path]:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    outputs = [
        FIGURE_DIR / f"{stem}.svg",
        FIGURE_DIR / f"{stem}.pdf",
        FIGURE_DIR / f"{stem}.tiff",
        FIGURE_DIR / f"{stem}.png",
    ]
    fig.savefig(outputs[0], metadata={"Date": None})
    svg_text = outputs[0].read_text(encoding="utf-8")
    outputs[0].write_text(
        "\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    fig.savefig(
        outputs[1],
        metadata={
            "CreationDate": None,
            "ModDate": None,
            "Creator": "stage5_pmc_build_figures.py",
        },
    )
    fig.savefig(
        outputs[2],
        dpi=600,
        pil_kwargs={"compression": "tiff_lzw"},
    )
    fig.savefig(outputs[3], dpi=300, metadata={"Software": "Matplotlib"})
    plt.close(fig)
    return outputs


def rounded_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    text: str,
    facecolor: str,
    edgecolor: str = "#5A646E",
    fontsize: float = 7.5,
) -> None:
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.018,rounding_size=0.02",
        facecolor=facecolor,
        edgecolor=edgecolor,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        color=COLORS["ink"],
        fontsize=fontsize,
    )


def arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    color: str = "#68737D",
    style: str = "-|>",
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=8,
            linewidth=0.9,
            color=color,
            connectionstyle="arc3,rad=0.0",
        )
    )


def figure_method_overview() -> tuple[list[Path], list[dict[str, Any]]]:
    source_rows = [
        {
            "component": "Compact dense backbone",
            "frozen_value": "MiniLM-L6-v2 cosine ranking",
            "role": "base relevance order",
        },
        {
            "component": "Adaptive granular balls",
            "frozen_value": "local sentence-unit groups",
            "role": "structured evidence units",
        },
        {
            "component": "Facet hyperedges",
            "frozen_value": "query-aware cross-ball relation",
            "role": "higher-order evidence expansion",
        },
        {
            "component": "Protected insertion",
            "frozen_value": "protect Dense top-10; at most 4 inserts; final top-20",
            "role": "bounded placement",
        },
    ]
    write_csv(
        SOURCE_DIR / "figure1_method_overview.csv",
        ["component", "frozen_value", "role"],
        source_rows,
    )

    fig, axes = plt.subplots(1, 3, figsize=(7.2047, 2.65))
    for ax in axes:
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

    axes[0].set_title("a  Compact dense retrieval", loc="left", fontweight="bold")
    rounded_box(axes[0], (0.05, 0.72), 0.34, 0.14, "Question", "#E8F0F7")
    rounded_box(axes[0], (0.58, 0.72), 0.36, 0.14, "Sentence units", "#F4F0E8")
    arrow(axes[0], (0.39, 0.79), (0.58, 0.79))
    y_positions = [0.52, 0.40, 0.28, 0.16]
    for index, y in enumerate(y_positions, start=1):
        rounded_box(
            axes[0],
            (0.18, y),
            0.64,
            0.085,
            f"Dense rank {index}",
            "#DDEAF4" if index <= 2 else "#EDF2F5",
            fontsize=6.8,
        )
    axes[0].text(0.5, 0.05, "Base relevance order", ha="center", color="#56616B")

    axes[1].set_title("b  Structured evidence expansion", loc="left", fontweight="bold")
    ball_centers = [(0.22, 0.68), (0.53, 0.67), (0.35, 0.31), (0.72, 0.34)]
    for idx, (x, y) in enumerate(ball_centers, start=1):
        circle = plt.Circle(
            (x, y),
            0.115,
            facecolor="#F3E7D3" if idx % 2 else "#E4E9F5",
            edgecolor="#6B7480",
        )
        axes[1].add_patch(circle)
        axes[1].text(x, y, f"Ball {idx}", ha="center", va="center", fontsize=6.7)
    axes[1].plot(
        [ball_centers[0][0], ball_centers[1][0], ball_centers[3][0]],
        [ball_centers[0][1], ball_centers[1][1], ball_centers[3][1]],
        color=COLORS["hgrag"],
        linewidth=2.0,
    )
    axes[1].plot(
        [ball_centers[0][0], ball_centers[2][0], ball_centers[3][0]],
        [ball_centers[0][1], ball_centers[2][1], ball_centers[3][1]],
        color=COLORS["hgrag"],
        linewidth=2.0,
        linestyle="--",
    )
    axes[1].text(
        0.54,
        0.91,
        "Query-aware facet hyperedges",
        ha="center",
        color=COLORS["hgrag"],
        fontweight="bold",
    )
    axes[1].text(
        0.5,
        0.08,
        "Candidate expansion is Gold-free",
        ha="center",
        color="#56616B",
    )

    axes[2].set_title("c  Protected top-k placement", loc="left", fontweight="bold")
    ys = np.linspace(0.86, 0.12, 13)
    for index, y in enumerate(ys, start=1):
        if index <= 10:
            face = "#DDEAF4"
            label = f"Dense {index}"
        elif index in (11, 13):
            face = "#F8D8AE"
            label = "HGRAG insert"
        else:
            face = "#EDF2F5"
            label = "Dense 11"
        rounded_box(axes[2], (0.22, y), 0.56, 0.041, label, face, fontsize=5.5)
    axes[2].add_patch(
        FancyBboxPatch(
            (0.16, 0.29),
            0.68,
            0.62,
            boxstyle="round,pad=0.01",
            fill=False,
            edgecolor=COLORS["dense"],
            linestyle="--",
        )
    )
    axes[2].text(
        0.5,
        0.94,
        "Protected Dense prefix",
        ha="center",
        color=COLORS["dense"],
        fontweight="bold",
    )
    axes[2].text(
        0.5,
        0.035,
        "At most 4 inserts; effective K ≤ 20",
        ha="center",
        color="#56616B",
    )
    fig.tight_layout(w_pad=1.1)
    return save_figure(fig, "figure1_method_overview"), source_rows


def extract_effect_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    e = data["stage4e_summary"]["bootstrap"]["delta_answer_f1"]
    f = data["stage4f_summary"]["bootstrap"]["delta_answer_f1"]
    g_ds = data["stage4g_datasets"]["datasets"]
    g_hp = g_ds["hotpotqa_train_distractor_v1_1"]["bootstrap"]["delta_answer_f1"]
    g_mu = g_ds["musique_ans_v1_0_train"]["bootstrap"]["delta_answer_f1"]
    h = data["stage4h_equal"]["comparisons"]
    i = data["stage4i_equal"]["comparisons"]

    def row(
        study: str,
        contrast: str,
        point: float,
        lower: float,
        upper: float,
        outcome: str,
    ) -> dict[str, Any]:
        return {
            "study": study,
            "contrast": contrast,
            "point": point,
            "ci95_lower": lower,
            "ci95_upper": upper,
            "outcome": outcome,
        }

    return [
        row("Stage4E / HotpotQA / Qwen", "Static q25 − MiniLM Dense", e["point"], e["lower_95"], e["upper_95"], "positive"),
        row("Stage4F / MuSiQue / Qwen", "Static q25 − MiniLM Dense", f["point"], f["lower_95"], f["upper_95"], "positive"),
        row("Stage4G / HotpotQA / Gemma mobile-QAT", "Static q25 − MiniLM Dense", g_hp["point"], g_hp["lower_95"], g_hp["upper_95"], "inconclusive"),
        row("Stage4G / MuSiQue / Gemma mobile-QAT", "Static q25 − MiniLM Dense", g_mu["point"], g_mu["lower_95"], g_mu["upper_95"], "inconclusive"),
        row(
            "Stage4H / equal-weight",
            "Full − MiniLM Dense",
            h["DENSE_TOP20"]["dataset_equal_weight"]["delta_answer_f1"]["point"],
            h["DENSE_TOP20"]["dataset_equal_weight"]["delta_answer_f1"]["ci95_lower"],
            h["DENSE_TOP20"]["dataset_equal_weight"]["delta_answer_f1"]["ci95_upper"],
            "positive",
        ),
        row(
            "Stage4H / equal-weight",
            "Full − BGE strong dense",
            h["STRONG_DENSE_TOP20"]["dataset_equal_weight"]["delta_answer_f1"]["point"],
            h["STRONG_DENSE_TOP20"]["dataset_equal_weight"]["delta_answer_f1"]["ci95_lower"],
            h["STRONG_DENSE_TOP20"]["dataset_equal_weight"]["delta_answer_f1"]["ci95_upper"],
            "negative",
        ),
        row(
            "Stage4H / equal-weight",
            "Full − no facet",
            h["Q25_NO_FACET_HYPEREDGE"]["dataset_equal_weight"]["delta_answer_f1"]["point"],
            h["Q25_NO_FACET_HYPEREDGE"]["dataset_equal_weight"]["delta_answer_f1"]["ci95_lower"],
            h["Q25_NO_FACET_HYPEREDGE"]["dataset_equal_weight"]["delta_answer_f1"]["ci95_upper"],
            "positive",
        ),
        row(
            "Stage4H / equal-weight",
            "Full − no protection",
            h["Q25_NO_PROTECTION"]["dataset_equal_weight"]["delta_answer_f1"]["point"],
            h["Q25_NO_PROTECTION"]["dataset_equal_weight"]["delta_answer_f1"]["ci95_lower"],
            h["Q25_NO_PROTECTION"]["dataset_equal_weight"]["delta_answer_f1"]["ci95_upper"],
            "inconclusive",
        ),
        row(
            "Stage4I / equal-weight",
            "Protected sidecar − BGE",
            i["protected_minus_bge"]["dataset_equal_weight"]["delta_answer_f1"]["point"],
            i["protected_minus_bge"]["dataset_equal_weight"]["delta_answer_f1"]["ci95_lower"],
            i["protected_minus_bge"]["dataset_equal_weight"]["delta_answer_f1"]["ci95_upper"],
            "inconclusive",
        ),
        row(
            "Stage4I / equal-weight",
            "Protected − unprotected placement",
            i["protected_minus_unprotected"]["dataset_equal_weight"]["delta_answer_f1"]["point"],
            i["protected_minus_unprotected"]["dataset_equal_weight"]["delta_answer_f1"]["ci95_lower"],
            i["protected_minus_unprotected"]["dataset_equal_weight"]["delta_answer_f1"]["ci95_upper"],
            "positive",
        ),
        row(
            "Stage4I / equal-weight",
            "Protected − no facet sidecar",
            i["protected_minus_no_facet"]["dataset_equal_weight"]["delta_answer_f1"]["point"],
            i["protected_minus_no_facet"]["dataset_equal_weight"]["delta_answer_f1"]["ci95_lower"],
            i["protected_minus_no_facet"]["dataset_equal_weight"]["delta_answer_f1"]["ci95_upper"],
            "inconclusive",
        ),
    ]


def figure_effect_forest(data: dict[str, Any]) -> tuple[list[Path], list[dict[str, Any]]]:
    rows = extract_effect_rows(data)
    write_csv(
        SOURCE_DIR / "figure2_effect_size_forest.csv",
        ["study", "contrast", "point", "ci95_lower", "ci95_upper", "outcome"],
        rows,
    )
    display = list(reversed(rows))
    fig, ax = plt.subplots(figsize=(7.2047, 4.55))
    y = np.arange(len(display))
    for idx, row in enumerate(display):
        color = COLORS[row["outcome"]]
        ax.errorbar(
            row["point"],
            idx,
            xerr=[
                [row["point"] - row["ci95_lower"]],
                [row["ci95_upper"] - row["point"]],
            ],
            fmt="o",
            markersize=4.2,
            color=color,
            ecolor=color,
            capsize=2.3,
            zorder=3,
        )
    labels = [f"{row['study']}\n{row['contrast']}" for row in display]
    ax.set_yticks(y, labels)
    ax.axvline(0, color="#66717A", linewidth=0.9)
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.6, alpha=0.8)
    ax.set_xlabel("Paired answer-F1 difference (95% bootstrap interval)")
    ax.set_title(
        "Stage4E–4I frozen answer-quality effects",
        loc="left",
        fontweight="bold",
    )
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(-0.062, 0.042)
    fig.subplots_adjust(left=0.41, right=0.98, top=0.92, bottom=0.11)
    return save_figure(fig, "figure2_effect_size_forest"), rows


def figure_strong_dense_and_displacement(
    data: dict[str, Any],
) -> tuple[list[Path], list[dict[str, Any]], list[dict[str, Any]]]:
    dataset_map = {
        "hotpotqa_train_distractor_v1_1": "HotpotQA",
        "musique_ans_v1_0_train": "MuSiQue",
    }
    method_map = {
        "BGE_TOP20": "BGE",
        "BGE_HGRAG_PROTECTED_TOP20": "Protected",
        "BGE_HGRAG_UNPROTECTED_TOP20": "Unprotected",
    }
    absolute_rows: list[dict[str, Any]] = []
    for dataset_key, dataset_label in dataset_map.items():
        methods = data["stage4i_datasets"][dataset_key]["methods"]
        for method_key, method_label in method_map.items():
            absolute_rows.append(
                {
                    "dataset": dataset_label,
                    "method": method_label,
                    "answer_f1": methods[method_key]["answer_f1"],
                    "answer_em": methods[method_key]["answer_em"],
                    "retrieval_cr20": methods[method_key]["retrieval_cr20"],
                    "retrieval_er20": methods[method_key]["retrieval_er20"],
                }
            )
    write_csv(
        SOURCE_DIR / "figure3a_strong_dense_absolute_metrics.csv",
        ["dataset", "method", "answer_f1", "answer_em", "retrieval_cr20", "retrieval_er20"],
        absolute_rows,
    )

    evidence_rows: list[dict[str, Any]] = []
    audit = data["stage4i_evidence"]["datasets"]
    for dataset_key, dataset_label in dataset_map.items():
        for method_key, method_label in method_map.items():
            if method_key == "BGE_TOP20":
                added = displaced = net = 0
            else:
                values = audit[dataset_key][method_key]
                added = values["added_gold_evidence_total"]
                displaced = values["displaced_bge_gold_evidence_total"]
                net = values["net_gold_evidence_change_total"]
            evidence_rows.append(
                {
                    "dataset": dataset_label,
                    "method": method_label,
                    "added_gold": added,
                    "displaced_gold": displaced,
                    "net_gold": net,
                    "interpretation": "post-decision descriptive only",
                }
            )
    write_csv(
        SOURCE_DIR / "figure3b_evidence_displacement.csv",
        ["dataset", "method", "added_gold", "displaced_gold", "net_gold", "interpretation"],
        evidence_rows,
    )

    fig, axes = plt.subplots(1, 2, figsize=(7.2047, 3.0))
    methods = ["BGE", "Protected", "Unprotected"]
    method_colors = [COLORS["bge"], COLORS["protected"], COLORS["unprotected"]]
    x = np.arange(2)
    width = 0.23
    for offset, (method, color) in enumerate(zip(methods, method_colors)):
        vals = [
            next(
                row["answer_f1"]
                for row in absolute_rows
                if row["dataset"] == dataset and row["method"] == method
            )
            for dataset in ("HotpotQA", "MuSiQue")
        ]
        axes[0].bar(x + (offset - 1) * width, vals, width, color=color, label=method)
    axes[0].set_xticks(x, ["HotpotQA", "MuSiQue"])
    axes[0].set_ylabel("Answer F1")
    axes[0].set_title("a  Strong-dense placement comparison", loc="left", fontweight="bold")
    axes[0].legend(frameon=False, ncol=1, loc="upper right")
    axes[0].spines[["top", "right"]].set_visible(False)
    axes[0].grid(axis="y", color=COLORS["grid"], linewidth=0.5)
    axes[0].set_ylim(0, 0.58)

    dataset_x = {"HotpotQA": 0, "MuSiQue": 1}
    plot_rows = [row for row in evidence_rows if row["method"] != "BGE"]
    for method_idx, method in enumerate(("Protected", "Unprotected")):
        subset = [row for row in plot_rows if row["method"] == method]
        positions = np.array([dataset_x[row["dataset"]] for row in subset], dtype=float)
        positions += (-0.16 if method_idx == 0 else 0.16)
        added = np.array([row["added_gold"] for row in subset])
        displaced = np.array([row["displaced_gold"] for row in subset])
        axes[1].bar(
            positions,
            added,
            0.27,
            color=method_colors[method_idx + 1],
            alpha=0.82,
            label=f"{method}: added",
        )
        axes[1].bar(
            positions,
            -displaced,
            0.27,
            color=method_colors[method_idx + 1],
            alpha=0.35,
            hatch="//",
            label=f"{method}: displaced",
        )
        for position, row in zip(positions, subset):
            axes[1].text(
                position,
                -row["displaced_gold"] - 4,
                f"net {row['net_gold']:+d}",
                ha="center",
                va="top",
                fontsize=6.3,
                color=COLORS["ink"],
            )
    axes[1].axhline(0, color="#66717A", linewidth=0.8)
    axes[1].set_xticks(x, ["HotpotQA", "MuSiQue"])
    axes[1].set_ylabel("Gold evidence transitions")
    axes[1].set_title("b  Added and displaced Gold evidence", loc="left", fontweight="bold")
    axes[1].spines[["top", "right"]].set_visible(False)
    axes[1].grid(axis="y", color=COLORS["grid"], linewidth=0.5)
    axes[1].set_ylim(-66, 64)
    axes[1].legend(frameon=False, ncol=2, loc="upper left", fontsize=6.1)
    axes[1].text(
        0.5,
        -0.28,
        "Post-decision descriptive audit; not a confirmatory endpoint",
        transform=axes[1].transAxes,
        ha="center",
        fontsize=6.3,
        color="#68737D",
    )
    fig.tight_layout(w_pad=1.5)
    return (
        save_figure(fig, "figure3_strong_dense_and_displacement"),
        absolute_rows,
        evidence_rows,
    )


def evidence_map_rows() -> list[dict[str, str]]:
    return [
        {"evidence": "Static q25 vs MiniLM Dense (HotpotQA/Qwen)", "result": "Positive", "scope": "closed candidate"},
        {"evidence": "Static q25 vs MiniLM Dense (MuSiQue/Qwen)", "result": "Positive", "scope": "closed candidate"},
        {"evidence": "Generator transfer to Gemma mobile-QAT", "result": "Inconclusive", "scope": "one additional configuration"},
        {"evidence": "Full vs BGE strong dense", "result": "Negative", "scope": "closed candidate"},
        {"evidence": "Facet hyperedge within MiniLM system", "result": "Positive", "scope": "Stage4H frozen system"},
        {"evidence": "Protected insertion independent ablation", "result": "Inconclusive", "scope": "Stage4H frozen system"},
        {"evidence": "HGRAG sidecar vs BGE", "result": "Inconclusive", "scope": "one frozen BGE backbone"},
        {"evidence": "Protected vs unprotected placement", "result": "Positive", "scope": "same inserted set"},
        {"evidence": "Facet increment on BGE sidecar", "result": "Inconclusive", "scope": "one frozen BGE backbone"},
        {"evidence": "Granular-ball flat-unit ablation", "result": "Undefined", "scope": "no fair control"},
    ]


def figure_evidence_map() -> tuple[list[Path], list[dict[str, str]]]:
    rows = evidence_map_rows()
    write_csv(
        SOURCE_DIR / "figure4_evidence_map.csv",
        ["evidence", "result", "scope"],
        rows,
    )
    categories = ["Positive", "Negative", "Inconclusive", "Undefined"]
    category_x = {label: idx for idx, label in enumerate(categories)}
    result_color = {
        "Positive": COLORS["positive"],
        "Negative": COLORS["negative"],
        "Inconclusive": COLORS["inconclusive"],
        "Undefined": COLORS["undefined"],
    }
    fig, ax = plt.subplots(figsize=(7.2047, 4.05))
    for idx, row in enumerate(reversed(rows)):
        x = category_x[row["result"]]
        ax.scatter(x, idx, s=48, color=result_color[row["result"]], zorder=3)
        ax.text(
            x + 0.09,
            idx,
            row["evidence"],
            va="center",
            ha="left",
            fontsize=6.8,
            color=COLORS["ink"],
        )
    ax.set_xlim(-0.35, 4.7)
    ax.set_ylim(-0.8, len(rows) - 0.2)
    ax.set_xticks(range(len(categories)), categories)
    ax.set_yticks([])
    ax.set_title("Evidence map: positive, negative, inconclusive and undefined results", loc="left", fontweight="bold")
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.6)
    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax.tick_params(axis="x", length=0)
    fig.tight_layout()
    return save_figure(fig, "figure4_evidence_map"), rows


def applicability_rows() -> list[dict[str, str]]:
    return [
        {
            "boundary": "Compact MiniLM dense / closed candidate / Qwen",
            "evidence": "Supported answer-F1 gain",
            "paper_claim": "Core supported scope",
            "status": "supported",
        },
        {
            "boundary": "BGE strong dense as replacement",
            "evidence": "Full method lower than BGE",
            "paper_claim": "Explicit negative boundary",
            "status": "negative",
        },
        {
            "boundary": "BGE strong dense + HGRAG sidecar",
            "evidence": "Interval crosses zero",
            "paper_claim": "Complementarity uncertain",
            "status": "inconclusive",
        },
        {
            "boundary": "Additional Gemma mobile-QAT generator",
            "evidence": "Joint transfer gate not passed",
            "paper_claim": "Generator transfer uncertain",
            "status": "inconclusive",
        },
        {
            "boundary": "Full-wiki / open-domain retrieval",
            "evidence": "Not evaluated",
            "paper_claim": "Deferred future work",
            "status": "deferred",
        },
    ]


def figure_applicability_boundary() -> tuple[list[Path], list[dict[str, str]]]:
    rows = applicability_rows()
    write_csv(
        SOURCE_DIR / "figure5_applicability_boundary.csv",
        ["boundary", "evidence", "paper_claim", "status"],
        rows,
    )
    fig, ax = plt.subplots(figsize=(7.2047, 3.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title(
        "Applicability boundary of the frozen evidence",
        loc="left",
        fontweight="bold",
    )
    y_positions = np.linspace(0.81, 0.14, len(rows))
    status_colors = {
        "supported": "#DDEDDC",
        "negative": "#F2D5D5",
        "inconclusive": "#E5E5E5",
        "deferred": "#DDE3EA",
    }
    for y, row in zip(y_positions, rows):
        rounded_box(
            ax,
            (0.03, y - 0.055),
            0.37,
            0.105,
            row["boundary"],
            status_colors[row["status"]],
            fontsize=6.7,
        )
        arrow(ax, (0.41, y), (0.57, y))
        rounded_box(
            ax,
            (0.58, y - 0.055),
            0.39,
            0.105,
            row["paper_claim"],
            status_colors[row["status"]],
            fontsize=6.9,
        )
    ax.text(0.215, 0.94, "Evaluated boundary", ha="center", fontweight="bold")
    ax.text(0.775, 0.94, "Permitted interpretation", ha="center", fontweight="bold")
    fig.tight_layout()
    return save_figure(fig, "figure5_applicability_boundary"), rows


def write_efficiency_source(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        {
            "stage": "Stage4E",
            "queries": 1000,
            "methods": 2,
            "generation_calls": data["stage4e_telemetry"]["generation_calls"],
            "failed_calls": data["stage4e_telemetry"]["failed_calls"],
            "wall_time_seconds": data["stage4e_telemetry"]["wall_time_seconds"],
            "gpu_peak_memory_bytes": data["stage4e_telemetry"]["gpu_peak_memory_bytes"],
            "determinism": "full main/rerun byte identity",
        },
        {
            "stage": "Stage4F",
            "queries": 3000,
            "methods": 2,
            "generation_calls": data["stage4f_telemetry"]["generation_calls"],
            "failed_calls": data["stage4f_telemetry"]["failed_calls"],
            "wall_time_seconds": data["stage4f_telemetry"]["wall_time_seconds"],
            "gpu_peak_memory_bytes": data["stage4f_telemetry"]["gpu_peak_memory_bytes"],
            "determinism": "full main/rerun byte identity",
        },
        {
            "stage": "Stage4G",
            "queries": 4000,
            "methods": 2,
            "generation_calls": data["stage4g_telemetry"]["generation_calls"],
            "failed_calls": data["stage4g_telemetry"]["failed_calls"],
            "wall_time_seconds": data["stage4g_telemetry"]["wall_time_seconds"],
            "gpu_peak_memory_bytes": data["stage4g_telemetry"]["gpu_peak_memory_bytes"],
            "determinism": "400-call pre-hash subset exact",
        },
        {
            "stage": "Stage4H",
            "queries": 2500,
            "methods": 7,
            "generation_calls": data["stage4h_telemetry"]["generation_calls"],
            "failed_calls": data["stage4h_telemetry"]["failed_calls"],
            "wall_time_seconds": data["stage4h_telemetry"]["wall_time_seconds_this_process"],
            "gpu_peak_memory_bytes": data["stage4h_telemetry"]["gpu_peak_memory_bytes"],
            "determinism": "1,400-call pre-hash subset exact",
        },
        {
            "stage": "Stage4I",
            "queries": 2500,
            "methods": 4,
            "generation_calls": data["stage4i_telemetry"]["generation_calls"],
            "failed_calls": data["stage4i_telemetry"]["failed_calls"],
            "wall_time_seconds": data["stage4i_telemetry"]["wall_time_seconds_this_process"],
            "gpu_peak_memory_bytes": data["stage4i_telemetry"]["gpu_peak_memory_bytes"],
            "determinism": "800-call pre-hash subset exact",
        },
    ]
    write_csv(
        SOURCE_DIR / "table4_efficiency_and_integrity.csv",
        [
            "stage",
            "queries",
            "methods",
            "generation_calls",
            "failed_calls",
            "wall_time_seconds",
            "gpu_peak_memory_bytes",
            "determinism",
        ],
        rows,
    )
    return rows


def write_manifest(outputs: list[Path], source_files: list[Path]) -> Path:
    manifest = {
        "schema_version": "stage5_pmc_figure_manifest_v1",
        "status": "STAGE5_PMC_FIGURES_BUILT_FROM_FROZEN_STAGE4E_I_EVIDENCE",
        "backend": {
            "language": "Python",
            "python": sys.version.split()[0],
            "matplotlib": matplotlib.__version__,
            "numpy": np.__version__,
            "svg_text": "editable",
        },
        "scientific_scope": (
            "Derived visualization only; no retrieval, inference, bootstrap, "
            "thresholding, or scientific-semantic modification."
        ),
        "inputs": [
            {
                "label": label,
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "bytes": path.stat().st_size,
                "sha256": expected_sha,
            }
            for label, (path, expected_sha) in INPUTS.items()
        ],
        "derived_files": [
            {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in sorted(outputs + source_files)
        ],
    }
    path = FIGURE_DIR / "STAGE5_PMC_FIGURE_MANIFEST.json"
    path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def main() -> None:
    configure_matplotlib()
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    data = load_inputs()

    outputs: list[Path] = []
    outputs.extend(figure_method_overview()[0])
    outputs.extend(figure_effect_forest(data)[0])
    outputs.extend(figure_strong_dense_and_displacement(data)[0])
    outputs.extend(figure_evidence_map()[0])
    outputs.extend(figure_applicability_boundary()[0])
    write_efficiency_source(data)

    source_files = sorted(SOURCE_DIR.glob("*.csv"))
    manifest_path = write_manifest(outputs, source_files)
    print(
        json.dumps(
            {
                "status": "STAGE5_PMC_FIGURES_BUILT",
                "figure_files": len(outputs),
                "source_data_files": len(source_files),
                "manifest": str(manifest_path.relative_to(ROOT)).replace("\\", "/"),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
