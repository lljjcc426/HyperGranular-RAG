#!/usr/bin/env python3
"""Read-only consistency verifier for the Stage5-PMC manuscript package."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from stage5_pmc_build_figures import INPUTS, ROOT


FIGURE_DIR = ROOT / "paper" / "figures"
CORE_TABLES = ROOT / "paper" / "SUBMISSION_CORE_TABLES.md"
BLUEPRINT = ROOT / "paper" / "STAGE5_PMC_MANUSCRIPT_BLUEPRINT.md"
CARD = ROOT / "docs" / "STAGE5_PMC_PAPER_MANUSCRIPT_CONSOLIDATION_CARD.md"
AUDIT = ROOT / "paper" / "STAGE5_PMC_PRE_SUBMISSION_AUDIT.md"
CORE_DRAFT = ROOT / "paper" / "MANUSCRIPT_CORE_DRAFT.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def verify_frozen_inputs() -> None:
    for label, (path, expected_sha) in INPUTS.items():
        require(path.is_file(), f"Missing frozen input: {label}: {path}")
        require(
            sha256(path) == expected_sha,
            f"Frozen input SHA mismatch: {label}: {path}",
        )


def verify_core_table_contract() -> None:
    text = CORE_TABLES.read_text(encoding="utf-8")
    required_strings = [
        "+0.01478 [0.00020, 0.02988]",
        "+0.01140 [0.00450, 0.01835]",
        "+0.01357 [0.00491, 0.02233]",
        "+0.00516 [-0.00262, 0.01295]",
        "-0.03998 [-0.05393, -0.02621]",
        "-0.00256 [-0.00998, 0.00458]",
        "+0.01336 [0.00341, 0.02343]",
        "+0.00354 [-0.00675, 0.01389]",
        "+0.01122 [0.00129, 0.02104]",
        "-0.00743 [-0.01616, 0.00132]",
        "`NOT_FAIRLY_DEFINED`",
        "`GENERATOR_TRANSFER_INCONCLUSIVE`",
        "`STRONG_DENSE_COMPLEMENTARITY_INCONCLUSIVE`",
    ]
    for value in required_strings:
        require(value in text, f"Core table is missing frozen value/status: {value}")


def verify_claim_boundary_contract() -> None:
    card = CARD.read_text(encoding="utf-8")
    blueprint = BLUEPRINT.read_text(encoding="utf-8")
    audit = AUDIT.read_text(encoding="utf-8")
    draft = CORE_DRAFT.read_text(encoding="utf-8")
    for value in [
        "STAGE4I_CLOSED_AND_FROZEN",
        "CORE_EXPERIMENTAL_PROGRAM_COMPLETE",
        "FULL_WIKI = OPTIONAL_AND_DEFERRED",
        "NEW_MODEL_SEARCH = NOT_AUTHORIZED",
        "CONTROLLER_LINE = CLOSED",
        "RESERVATION = LOCKED",
        "STAGE3B = LOCKED",
        "U2 = NOT_AUTHORIZED",
    ]:
        require(value in card, f"Stage5 card is missing state: {value}")
    require(
        "structured evidence-completion layer for compact dense backbones" in blueprint,
        "Blueprint is missing the bounded central thesis.",
    )
    require(
        "not as a universal replacement for strong dense retrieval" in blueprint,
        "Blueprint is missing the strong-dense claim boundary.",
    )
    require(
        "MANUSCRIPT_NOT_YET_SUBMISSION_READY" in audit,
        "Audit must not mark the package submission ready before metadata/citations.",
    )
    require(
        "NO_NEW_EXPERIMENT_REQUIRED_BY_CURRENT_EVIDENCE_AUDIT" in audit,
        "Audit is missing the frozen experimental-program conclusion.",
    )
    require(
        "EXTERNAL_CITATIONS_NOT_YET_BOUND" in draft
        and "{{CITE:" in draft
        and "NOT_SUBMISSION_READY" in draft,
        "Core draft must expose unresolved citations and non-submission status.",
    )
    require(
        "not as a universal replacement for strong dense retrieval" in draft,
        "Core draft is missing the strong-dense boundary.",
    )


def verify_figure_manifest() -> dict[str, Any]:
    manifest_path = FIGURE_DIR / "STAGE5_PMC_FIGURE_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(
        manifest["status"]
        == "STAGE5_PMC_FIGURES_BUILT_FROM_FROZEN_STAGE4E_I_EVIDENCE",
        "Unexpected figure manifest status.",
    )
    require(len(manifest["inputs"]) == len(INPUTS), "Figure manifest input count mismatch.")
    for item in manifest["inputs"]:
        path = ROOT / item["path"]
        require(path.stat().st_size == item["bytes"], f"Input byte mismatch: {path}")
        require(sha256(path) == item["sha256"], f"Input SHA mismatch: {path}")
    for item in manifest["derived_files"]:
        path = ROOT / item["path"]
        require(path.stat().st_size == item["bytes"], f"Derived byte mismatch: {path}")
        require(sha256(path) == item["sha256"], f"Derived SHA mismatch: {path}")

    stems = [
        "figure1_method_overview",
        "figure2_effect_size_forest",
        "figure3_strong_dense_and_displacement",
        "figure4_evidence_map",
        "figure5_applicability_boundary",
    ]
    for stem in stems:
        for suffix in (".svg", ".pdf", ".tiff", ".png"):
            require((FIGURE_DIR / f"{stem}{suffix}").is_file(), f"Missing export: {stem}{suffix}")
        svg = (FIGURE_DIR / f"{stem}.svg").read_text(encoding="utf-8")
        require("<text" in svg, f"SVG text was not preserved as editable text: {stem}")
    require(
        len(list((FIGURE_DIR / "source_data").glob("*.csv"))) == 7,
        "Expected seven Stage5 source-data CSV files.",
    )
    return manifest


def verify_new_markdown_links() -> None:
    markdown_files = [
        CARD,
        BLUEPRINT,
        CORE_TABLES,
        CORE_DRAFT,
        AUDIT,
        FIGURE_DIR / "FIGURE_CONTRACTS_AND_CAPTIONS.md",
    ]
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for markdown_path in markdown_files:
        text = markdown_path.read_text(encoding="utf-8")
        for raw_target in pattern.findall(text):
            target = raw_target.split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            linked = (markdown_path.parent / target).resolve()
            require(linked.exists(), f"Broken local link in {markdown_path}: {raw_target}")


def main() -> None:
    verify_frozen_inputs()
    verify_core_table_contract()
    verify_claim_boundary_contract()
    manifest = verify_figure_manifest()
    verify_new_markdown_links()
    print(
        json.dumps(
            {
                "status": "STAGE5_PMC_MATERIALS_VERIFIED",
                "frozen_inputs": len(INPUTS),
                "derived_files": len(manifest["derived_files"]),
                "figure_groups": 5,
                "source_data_csv": 7,
                "scientific_reanalysis": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
