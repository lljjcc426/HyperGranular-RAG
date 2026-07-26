#!/usr/bin/env python3
"""Read-only joint evidence/citation/figure verifier for Stage5R-PMR."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from stage5r_build_materials import MANIFEST_INPUTS, OUT, ROOT, SOURCE


REQUIRED_FILES = [
    ROOT / "paper" / "MANUSCRIPT_CORE_DRAFT_STAGE5R.md",
    ROOT / "paper" / "STAGE5R_MANUSCRIPT_BLUEPRINT.md",
    ROOT / "paper" / "STAGE5R_CORE_TABLES.md",
    ROOT / "paper" / "STAGE5R_PRE_SUBMISSION_AUDIT.md",
    ROOT / "paper" / "references" / "VERIFIED_LITERATURE_CORPUS.md",
    ROOT / "paper" / "references" / "verified_references.bib",
    ROOT / "paper" / "references" / "CITATION_CLAIM_MAP.md",
    ROOT / "paper" / "supplementary" / "SUPPLEMENTARY_MATERIAL_DRAFT.md",
    ROOT / "paper" / "submission" / "VENUE_TARGET_MATRIX.md",
    ROOT / "paper" / "submission" / "AUTHOR_METADATA_TEMPLATE.md",
    ROOT / "paper" / "submission" / "LICENSE_AND_AVAILABILITY.md",
    ROOT / "paper" / "submission" / "SUBMISSION_BLOCKERS.md",
    OUT / "FIGURE_CONTRACTS_AND_CAPTIONS.md",
    OUT / "STAGE5R_FIGURE_MANIFEST.json",
]
MANUSCRIPT = REQUIRED_FILES[0]
BIB = ROOT / "paper" / "references" / "verified_references.bib"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def verify_frozen_inputs() -> None:
    for label, (path, expected) in MANIFEST_INPUTS.items():
        require(path.is_file(), f"missing frozen input: {label}")
        require(sha256(path) == expected, f"frozen input SHA mismatch: {label}")


def verify_required_files() -> None:
    for path in REQUIRED_FILES:
        require(path.is_file(), f"missing Stage5R file: {path}")
        require(path.stat().st_size > 0, f"empty Stage5R file: {path}")


def verify_manifest() -> dict[str, Any]:
    path = OUT / "STAGE5R_FIGURE_MANIFEST.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    require(
        manifest["status"]
        == "STAGE5R_FIGURES_BUILT_FROM_FROZEN_STAGE4E_STAGE5A_EVIDENCE",
        "unexpected Stage5R manifest status",
    )
    require(manifest["scientific_reanalysis"] is False, "scientific_reanalysis must be false")
    require(
        len(manifest["inputs"]) == len(MANIFEST_INPUTS),
        "manifest input count mismatch",
    )
    for item in manifest["inputs"]:
        item_path = ROOT / item["path"]
        require(item_path.stat().st_size == item["bytes"], f"input byte mismatch: {item_path}")
        require(sha256(item_path) == item["sha256"], f"input SHA mismatch: {item_path}")
    for item in manifest["derived_files"]:
        item_path = ROOT / item["path"]
        require(item_path.is_file(), f"missing derived file: {item_path}")
        require(item_path.stat().st_size == item["bytes"], f"derived byte mismatch: {item_path}")
        require(sha256(item_path) == item["sha256"], f"derived SHA mismatch: {item_path}")

    stems = [
        "figure1_method_overview",
        "figure2_effect_size_forest",
        "figure3_strong_dense_and_displacement",
        "figure4_evidence_map",
        "figure5_applicability_boundary",
    ]
    for stem in stems:
        for suffix in ("svg", "pdf", "tiff", "png"):
            require((OUT / f"{stem}.{suffix}").is_file(), f"missing figure export: {stem}.{suffix}")
        svg = (OUT / f"{stem}.svg").read_text(encoding="utf-8")
        require("<text" in svg, f"SVG text is not editable: {stem}")
    require(len(list(SOURCE.glob("*.csv"))) == 12, "expected twelve Stage5R source CSVs")
    return manifest


def read_csv(name: str) -> list[dict[str, str]]:
    with (SOURCE / name).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def close(actual: str, expected: float, tolerance: float = 5e-9) -> bool:
    return abs(float(actual) - expected) <= tolerance


def verify_figure_and_table_sources() -> None:
    forest = read_csv("figure2_effect_size_forest.csv")
    require(len(forest) == 11, "effect forest must contain eleven frozen contrasts")
    by_key = {(r["evidence_family"], r["contrast"]): r for r in forest}
    expected = {
        ("Strong baseline", "Full − BGE"): (-0.03997911063667102, -0.05393311667777282, -0.026211352078037622, "NEGATIVE"),
        ("Cross-space sidecar", "Protected − BGE"): (-0.002563487034017898, -0.009981696740290903, 0.0045765019549832385, "INCONCLUSIVE"),
        ("BGE-native", "Protected − BGE"): (-0.0030458201219070785, -0.006879831388418345, 0.0006312558576688999, "INCONCLUSIVE"),
        ("BGE-native placement", "Protected − Unprotected"): (0.003367058043988329, -0.0012851527336356795, 0.008025643021968454, "INCONCLUSIVE"),
        ("BGE-native facet", "Protected − NoFacet"): (0.0006309544782878872, -0.0042201766774451, 0.005364560771923123, "INCONCLUSIVE"),
    }
    for key, (point, low, high, status) in expected.items():
        require(key in by_key, f"missing forest contrast: {key}")
        row = by_key[key]
        require(close(row["delta_answer_f1"], point), f"point mismatch: {key}")
        require(close(row["ci95_lower"], low), f"lower CI mismatch: {key}")
        require(close(row["ci95_upper"], high), f"upper CI mismatch: {key}")
        require(row["status"] == status, f"status mismatch: {key}")

    displacement = read_csv("figure3b_evidence_displacement.csv")
    require(len(displacement) == 4, "expected four post-decision displacement rows")
    got = {
        (r["frozen_boundary"], r["dataset"]): (
            int(r["added_gold"]),
            int(r["displaced_gold"]),
            int(r["net_gold"]),
            r["evidence_role"],
        )
        for r in displacement
    }
    require(
        got[("Stage5A BGE-native", "HotpotQA")]
        == (3, 2, 1, "POST_DECISION_DESCRIPTIVE_ONLY"),
        "Stage5A HotpotQA displacement mismatch",
    )
    require(
        got[("Stage5A BGE-native", "MuSiQue")]
        == (16, 15, 1, "POST_DECISION_DESCRIPTIVE_ONLY"),
        "Stage5A MuSiQue displacement mismatch",
    )
    require(
        got[("Stage4I cross-space sidecar", "HotpotQA")]
        == (21, 29, -8, "POST_DECISION_DESCRIPTIVE_ONLY"),
        "Stage4I HotpotQA displacement mismatch",
    )
    require(
        got[("Stage4I cross-space sidecar", "MuSiQue")]
        == (59, 50, 9, "POST_DECISION_DESCRIPTIVE_ONLY"),
        "Stage4I MuSiQue displacement mismatch",
    )

    tables = (ROOT / "paper" / "STAGE5R_CORE_TABLES.md").read_text(encoding="utf-8")
    for value in [
        "+0.01478 [0.00020, 0.02988]",
        "+0.01140 [0.00450, 0.01835]",
        "+0.01357 [0.00491, 0.02233]",
        "-0.03998 [-0.05393, -0.02621]",
        "-0.00256 [-0.00998, 0.00458]",
        "-0.00305 [-0.00688, 0.00063]",
        "+0.00337 [-0.00129, 0.00803]",
        "+0.00063 [-0.00422, 0.00536]",
        "NOT_FAIRLY_DEFINED",
    ]:
        require(value in tables, f"core tables missing value/status: {value}")

    compact = read_csv("table1_core.csv")
    require(len(compact) == 3, "expected three compact absolute-result rows")
    compact_by_boundary = {row["boundary"]: row for row in compact}
    hotpot = compact_by_boundary["MiniLM / HotpotQA confirmation"]
    require(hotpot["dense_f1"] == "0.42150", "Hotpot Dense absolute F1 mismatch")
    require(hotpot["full_f1"] == "0.43628", "Hotpot Full absolute F1 mismatch")
    require(hotpot["avg_inserted_units"] == "1.9300", "Hotpot insertion mean mismatch")
    require(hotpot["f1_gain_harm_queries"] == "47/34", "Hotpot F1 gain/harm mismatch")
    musique = compact_by_boundary["MiniLM / MuSiQue confirmation"]
    require(musique["dense_f1"] == "0.13595", "MuSiQue Dense absolute F1 mismatch")
    require(musique["full_f1"] == "0.14735", "MuSiQue Full absolute F1 mismatch")
    require(musique["avg_inserted_units"] == "2.4110", "MuSiQue insertion mean mismatch")
    require(musique["f1_gain_harm_queries"] == "125/77", "MuSiQue F1 gain/harm mismatch")
    joint = compact_by_boundary["MiniLM / joint component confirmation"]
    require(joint["dense_f1"] == "0.30446", "Joint Dense absolute F1 mismatch")
    require(joint["full_f1"] == "0.31803", "Joint Full absolute F1 mismatch")
    require(joint["avg_inserted_units"] == "2.1628", "Joint insertion mean mismatch")
    require(joint["f1_gain_harm_queries"] == "102/73", "Joint F1 gain/harm mismatch")

    strong = read_csv("table6_core.csv")
    require(len(strong) == 6, "expected six strong-boundary absolute-result rows")
    strong_by_key = {(row["boundary"], row["method"]): row for row in strong}
    require(
        strong_by_key[("Stage4H original", "BGE")]["equal_weight_f1"]
        == "0.35801",
        "Stage4H BGE absolute F1 mismatch",
    )
    require(
        strong_by_key[("Stage5A BGE-native", "Native Protected")][
            "equal_weight_f1"
        ]
        == "0.34264",
        "Stage5A native absolute F1 mismatch",
    )


def bib_keys() -> set[str]:
    text = BIB.read_text(encoding="utf-8")
    return set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", text))


def verify_citations() -> None:
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    corpus = (ROOT / "paper" / "references" / "VERIFIED_LITERATURE_CORPUS.md").read_text(encoding="utf-8")
    require("{{CITE" not in manuscript, "unresolved citation placeholder in manuscript")
    citation_groups = re.findall(r"\[(@[A-Za-z0-9_:-]+(?:\s*;\s*@[A-Za-z0-9_:-]+)*)\]", manuscript)
    cited = {
        key
        for group in citation_groups
        for key in re.findall(r"@([A-Za-z0-9_:-]+)", group)
    }
    keys = bib_keys()
    require(cited, "manuscript contains no machine-auditable citations")
    require(cited <= keys, f"undefined BibTeX keys: {sorted(cited - keys)}")
    require(len(keys) >= 20, "verified bibliography is unexpectedly small")
    for key in cited:
        require(f"`{key}`" in corpus, f"cited work missing from verified corpus: {key}")
    doi_values = re.findall(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b", BIB.read_text(encoding="utf-8"))
    require(len(doi_values) == len(set(doi_values)), "duplicate DOI found in bibliography")


def verify_claim_boundaries() -> None:
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    normalized_manuscript = re.sub(r"\s+", " ", manuscript)
    required = [
        "-0.03998 [-0.05393, -0.02621]",
        "-0.00256 [-0.00998, 0.00458]",
        "-0.003046 [-0.006880, 0.000631]",
        "-0.003667 [-0.007667, 0.000004]",
        "-0.002907 [-0.008682, 0.002652]",
        "-0.003184 [-0.008486, 0.001863]",
        "+0.003367 [-0.001285, 0.008026]",
        "+0.000631 [-0.004220, 0.005365]",
        "+0.003143",
        "We use this development result only to select C10",
        "no statistically resolved answer-quality improvement over BGE",
        "full-wiki or open-domain",
        "no unique matched counterparts at the unit level",
        "post-decision descriptive",
        "structured evidence-completion layer",
        "marginal value contracts with a stronger retriever",
    ]
    for value in required:
        normalized_value = re.sub(r"\s+", " ", value)
        require(
            normalized_value in normalized_manuscript,
            f"manuscript missing claim boundary: {value}",
        )
    lowered = manuscript.lower()
    prohibited = [
        "hypergranular-rag is a universal",
        "hypergranular-rag outperforms strong",
        "bge-native hgrag is equivalent",
        "sidecar is equivalent",
        "gemma is unsuitable for rag",
        "full-wiki effectiveness is established",
        "state-of-the-art performance",
    ]
    for phrase in prohibited:
        require(phrase not in lowered, f"prohibited overclaim detected: {phrase}")
    require(
        lowered.count("inconclusive") + lowered.count("statistically unresolved") >= 8,
        "statistically unresolved evidence is not sufficiently explicit",
    )


def verify_submission_boundaries() -> None:
    metadata = (ROOT / "paper" / "submission" / "AUTHOR_METADATA_TEMPLATE.md").read_text(encoding="utf-8")
    blockers = (ROOT / "paper" / "submission" / "SUBMISSION_BLOCKERS.md").read_text(encoding="utf-8")
    license_text = (ROOT / "paper" / "submission" / "LICENSE_AND_AVAILABILITY.md").read_text(encoding="utf-8")
    require("[REQUIRED]" in metadata, "author placeholders must remain explicit")
    require("SUBMISSION_READY = FALSE" in blockers, "submission package must not be marked ready")
    root_license = any((ROOT / name).exists() for name in ("LICENSE", "LICENSE.txt", "LICENSE.md"))
    if root_license:
        require(
            "NO_REPOSITORY_LICENSE_DECLARED" not in license_text,
            "license statement is stale after repository license appeared",
        )
    else:
        require(
            "NO_REPOSITORY_LICENSE_DECLARED" in license_text,
            "missing no-license disclosure",
        )


def verify_links() -> None:
    markdown = list((ROOT / "paper").rglob("*.md"))
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in markdown:
        text = path.read_text(encoding="utf-8")
        for raw in pattern.findall(text):
            target = raw.split("#", 1)[0].strip()
            if (
                not target
                or "://" in target
                or target.startswith("mailto:")
                or target.startswith("#")
            ):
                continue
            linked = (path.parent / target).resolve()
            require(linked.exists(), f"broken local link in {path}: {raw}")


def verify_stage5_pmc_regression() -> None:
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "stage5_pmc_verify_materials.py")],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    require(completed.returncode == 0, f"Stage5-PMC verifier failed: {completed.stderr}")
    require("STAGE5_PMC_MATERIALS_VERIFIED" in completed.stdout, "unexpected Stage5-PMC verifier output")


def main() -> None:
    verify_frozen_inputs()
    verify_required_files()
    manifest = verify_manifest()
    verify_figure_and_table_sources()
    verify_citations()
    verify_claim_boundaries()
    verify_submission_boundaries()
    verify_links()
    verify_stage5_pmc_regression()
    print(
        json.dumps(
            {
                "status": "STAGE5R_PMR_MATERIALS_VERIFIED",
                "frozen_inputs": len(MANIFEST_INPUTS),
                "derived_files": len(manifest["derived_files"]),
                "figure_groups": 5,
                "figure_exports": 20,
                "source_csv": len(list(SOURCE.glob("*.csv"))),
                "bibliography_entries": len(bib_keys()),
                "scientific_reanalysis": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
