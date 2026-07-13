"""Run only the Stage4B-U1 synthetic test suite and write deterministic evidence."""

from __future__ import annotations

import argparse
import io
import sys
import unittest
from pathlib import Path

from stage4b_u1_common import sha256_file, write_json


TRACKED_IMPLEMENTATION_FILES = (
    "AGENTS.md",
    "docs/STAGE4B_U1_EXECUTION_PACKAGE_REVIEW_1.md",
    "docs/STAGE4B_U1_EXECUTION_HARDENING_V2_1.md",
    "docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md",
    "docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_3.md",
    "docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_DRAFT.md",
    "docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_APPROVAL_REQUEST.md",
    "docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_MANIFEST.json",
    "docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_APPROVAL_DECISION.md",
    "scripts/stage4b_u1_common.py",
    "scripts/stage4b_u1_prepare_channels.py",
    "scripts/stage4b_u1_goldfree_retrieval.py",
    "scripts/stage4b_u1_goldfree_controller.py",
    "scripts/stage4b_u1_evaluate.py",
    "scripts/stage4b_u1_verify.py",
    "scripts/stage4b_u1_run_synthetic_verification.py",
    "tests/test_stage4b_u1_goldfree.py",
)


def test_ids(suite: unittest.TestSuite) -> list[str]:
    ids: list[str] = []
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            ids.extend(test_ids(item))
        else:
            ids.append(item.id())
    return ids


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/stage4b_u1_d_pregold_amendment_3_synthetic_verification.json"
        ),
    )
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    suite = unittest.defaultTestLoader.discover(
        str(repo_root / "tests"), pattern="test_stage4b_u1_goldfree.py"
    )
    discovered = sorted(test_ids(suite))
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    evidence = {
        "stage": "Stage4B-U1-D Pre-Gold Amendment 3",
        "protocol_architecture": "docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md",
        "hardening_specification": "docs/STAGE4B_U1_EXECUTION_HARDENING_V2_1.md",
        "trigger_review": "docs/STAGE4B_U1_EXECUTION_PACKAGE_REVIEW_1.md",
        "status": (
            "AMENDMENT_3_EFFECTIVE_K_SYNTHETICALLY_HARDENED_AWAITING_OFFICIAL_RESUMPTION_APPROVAL"
            if result.wasSuccessful()
            else "FAILED"
        ),
        "tests_run": result.testsRun,
        "test_ids": discovered,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "official_development_data_accessed": False,
        "reservation_data_accessed": False,
        "stage3b_accessed": False,
        "official_source_audit_loaded_by_tests": False,
        "synthetic_artifacts_persisted": False,
        "implementation_hashes": {
            path: sha256_file(repo_root / path) for path in TRACKED_IMPLEMENTATION_FILES
        },
        "verified_properties": [
            "controller and evaluator channels are separate files and processes",
            "controller channel contains no evaluation-label fields or Gold-map metadata",
            "controller rejects reintroduced prohibited fields",
            "single-ball, zero-radius, empty-ball, and ECDF boundary rules are deterministic",
            "Gold-free dense, hyperedge-candidate, and q25 rankings match the legacy frozen algorithm on synthetic input",
            "allocation is the largest score/hash prefix within 60 percent planned-insert cost",
            "U1 ranking is exactly dense or frozen q25 according to the trigger",
            "reservation mode reuses the frozen development ECDF references",
            "official channel preparation requires the frozen Stage4A-R2 source audit and development boundary",
            "sample IDs and namespaced runtime query IDs have separate frozen digests and an exact per-row relation",
            "preparer, controller, and verifier reject dual-ID boundary drift",
            "formal model name, max length, batch size, and run role are frozen",
            "independent verifier recomputes tie hash, ECDF values, scores, order, cutoff, and budget",
            "effective-K is min(20, candidate pool size) and the effective protected prefix is min(10, effective-K)",
            "effective-K verifier rejects empty pools, count drift, wrong lengths, duplicate or non-candidate IDs, protected-prefix drift, and insertion drift",
            "effective-K structure determines q25 and final inserted-unit IDs",
            "policy binds the protocol, implementation files, inputs, embedding cache, source audit, and git commit",
            "evaluator requires a VERIFIED_PRE_GOLD artifact before loading Gold",
            "Stage4A-R2 baseline drift stops before U1 summary generation",
            "all required corruption injections are rejected after internal hashes are refreshed where applicable",
            "two complete synthetic controller runs are byte-identical",
        ],
    }
    write_json(args.output, evidence)
    if not result.wasSuccessful():
        sys.stderr.write(stream.getvalue())
        raise SystemExit(1)


if __name__ == "__main__":
    main()
