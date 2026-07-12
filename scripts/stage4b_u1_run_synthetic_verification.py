"""Run only the Stage4B-U1 synthetic test suite and write deterministic evidence."""

from __future__ import annotations

import argparse
import io
import sys
import unittest
from pathlib import Path

from stage4b_u1_common import sha256_file, write_json


TRACKED_IMPLEMENTATION_FILES = (
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
        default=Path("results/stage4b_u1_synthetic_verification.json"),
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
        "stage": "Stage4B-U1",
        "protocol": "docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md",
        "status": "SYNTHETIC_IMPLEMENTATION_VERIFIED" if result.wasSuccessful() else "FAILED",
        "tests_run": result.testsRun,
        "test_ids": discovered,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "official_development_data_accessed": False,
        "reservation_data_accessed": False,
        "stage3b_accessed": False,
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
            "independent verifier detects a corrupted final ranking",
            "two complete synthetic controller runs are byte-identical",
        ],
    }
    write_json(args.output, evidence)
    if not result.wasSuccessful():
        sys.stderr.write(stream.getvalue())
        raise SystemExit(1)


if __name__ == "__main__":
    main()
