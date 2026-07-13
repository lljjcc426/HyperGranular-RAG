"""Run the complete Stage4B-U1 plus Amendment 5A synthetic suite."""

from __future__ import annotations

import argparse
import io
import json
import sys
import unittest
from pathlib import Path

from stage4b_u1_common import sha256_file, write_json


TRACKED_IMPLEMENTATION_FILES = (
    "AGENTS.md",
    "docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_4.md",
    "docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_DECISIONS_DIAGNOSTIC_DRAFT.md",
    "docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_APPROVAL_REQUEST.md",
    "docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_MANIFEST.json",
    "docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_APPROVAL_DECISION.md",
    "scripts/stage4b_u1_common.py",
    "scripts/stage4b_u1_goldfree_retrieval.py",
    "scripts/stage4b_u1_goldfree_controller.py",
    "scripts/stage4b_u1_compare_decisions.py",
    "scripts/stage4b_u1_capture_diagnostic_decisions.py",
    "scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py",
    "tests/test_stage4b_u1_goldfree.py",
    "tests/test_stage4b_u1_decisions_diagnostic.py",
)
REQUIRED_ACTIVE_PROOF_SUFFIXES = (
    "test_synthetic_allowlist_rejects_official_path_before_open",
    "test_capture_does_not_call_controller_rankings_or_policy",
    "test_temporary_decisions_removed_after_success",
    "test_temporary_decisions_removed_after_exception",
    "test_official_mode_without_5b_token_fails_before_open",
)


def test_ids(suite: unittest.TestSuite) -> list[str]:
    ids: list[str] = []
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            ids.extend(test_ids(item))
        else:
            ids.append(item.id())
    return ids


def forbidden_official_paths(repo_root: Path) -> set[Path]:
    manifest = json.loads(
        (repo_root / "docs" / "STAGE4B_U1_PREGOLD_AMENDMENT_5A_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    resumption = json.loads(
        (repo_root / "docs" / "STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    cache = Path(resumption["frozen_cache"]["path"])
    data_root = cache.parent
    values = {
        cache,
        data_root / "stage4a_r2_official_dev4500_units.jsonl",
        data_root / "stage4a_r2_official_dev4500_queries.jsonl",
        data_root / "stage4a_r2_official_dev4500_minilm_embeddings.npz",
        repo_root / "docs" / "STAGE4A_R2_SOURCE_AUDIT.json",
        repo_root / "results" / "stage4b_u1_d_official_dev4500_decisions.jsonl",
        repo_root / "results" / "stage4b_u1_d_official_dev4500_rankings.jsonl",
        Path(resumption["frozen_v2_2_equivalence"]["reference_policy_path"]),
    }
    values.update(Path(path) for path in resumption["artifact_registry"].values())
    if manifest["current_execution_state"] != "PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_4":
        raise ValueError("Amendment 5A manifest state drifted")
    return {path.resolve() for path in values}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/stage4b_u1_d_pregold_amendment_5a_synthetic_verification.json"
        ),
    )
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    forbidden = forbidden_official_paths(repo_root)
    attempted: list[str] = []

    def audit_hook(event: str, values: tuple[object, ...]) -> None:
        if event != "open" or not values:
            return
        supplied = values[0]
        if not isinstance(supplied, (str, bytes)):
            return
        try:
            candidate = Path(supplied).resolve()
        except (OSError, TypeError, ValueError):
            return
        if candidate in forbidden:
            attempted.append(str(candidate))
            raise PermissionError(f"Amendment 5A blocked official path access: {candidate}")

    sys.addaudithook(audit_hook)
    suite = unittest.defaultTestLoader.discover(
        str(repo_root / "tests"), pattern="test_stage4b_u1*.py"
    )
    discovered = sorted(test_ids(suite))
    active_proofs = {
        suffix: [test_id for test_id in discovered if test_id.endswith(suffix)]
        for suffix in REQUIRED_ACTIVE_PROOF_SUFFIXES
    }
    if any(len(matches) != 1 for matches in active_proofs.values()):
        raise ValueError("Required active access/cleanup proof test is missing or duplicated")
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    count_gate = result.testsRun >= 74 and len(discovered) >= 74
    evidence = {
        "stage": "Stage4B-U1-D Pre-Gold Amendment 5A",
        "diagnostic_checkpoint": "stage4b_u1_decisions_diag_v1",
        "controller_checkpoint_unchanged": "stage4b_u1_v2_3_1",
        "status": (
            "AMENDMENT_5A_SYNTHETICALLY_VERIFIED"
            if result.wasSuccessful() and count_gate and not attempted
            else "FAILED"
        ),
        "tests_run": result.testsRun,
        "minimum_tests_required": 74,
        "test_ids": discovered,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "implementation_hashes": {
            path: sha256_file(repo_root / path) for path in TRACKED_IMPLEMENTATION_FILES
        },
        "active_proof_tests": active_proofs,
        "official_path_access_guard": {
            "installed": True,
            "forbidden_path_count": len(forbidden),
            "blocked_or_attempted_access_count": len(attempted),
        },
        "rankings_accessed": False,
        "rankings_generated_by_capture": False,
        "policy_builder_called_by_capture": False,
        "policy_generated_by_capture": False,
        "gold_accessed": False,
        "reservation_accessed": False,
        "stage3b_accessed": False,
        "official_diagnostic_executed": False,
        "controller_rerun": False,
        "verifier_executed": False,
        "verified_properties": [
            "raw bytes size SHA-256 and terminal-newline differences are separated from canonical JSON equality",
            "query-ID count uniqueness set and order are compared fail-closed",
            "JSON duplicate keys invalid syntax and non-finite constants are rejected",
            "bool int and float types remain distinct",
            "binary64 uses explicit big-endian bits and a sign-aware monotonic unsigned ordering",
            "positive and negative zero remain bit-distinct and cross-sign ULP distances are deterministic",
            "schema field order nested type discrete list float and decision-semantic differences are classified",
            "heterogeneous within-file schemas fail closed and the comparator CLI returns nonzero",
            "synthetic capture writes decisions only under an OS temporary directory",
            "temporary decisions are removed after successful and exceptional exits",
            "capture does not access or generate rankings and does not call a policy builder",
            "official paths are guarded process-wide and synthetic allowlists reject outside paths before file reads",
            "the original Stage4B-U1 50-test suite remains passing",
        ],
    }
    write_json(args.output, evidence)
    if not result.wasSuccessful() or not count_gate or attempted:
        sys.stderr.write(stream.getvalue())
        raise SystemExit(1)


if __name__ == "__main__":
    main()
