"""Run the complete Stage4B-U1 plus Amendment 5C-A synthetic suite."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
import unittest
from pathlib import Path


FROZEN_EXISTING_HASHES = {
    "scripts/stage4b_u1_compare_decisions.py": "FF4D623DF86FE42EB4ACDFF9D3321FCA768E03B64597C6CC88931359CEDB2DD4",
    "scripts/stage4b_u1_capture_diagnostic_decisions.py": "7C7B159911384B436FDCC1B20D26F2F545F2DC55EAD1F7B2B134B273110ED40A",
    "scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py": "776AAF0DF8884E79647B144A88416EFAFFFA51AFDA43520203FB7FC745A88989",
    "scripts/stage4b_u1_goldfree_controller.py": "C18AD3B672649BA846C5E191D0DBBAC7644A926D4B8CCD39176127175BBA7C1F",
    "scripts/stage4b_u1_goldfree_retrieval.py": "3B50FAFD057E2565167ED09288D61829B3FBD044991F139F734F819955038A3B",
    "scripts/stage4b_u1_common.py": "CDF7EAD6007DABE389ED0BD18983496F75290C32243FE6DF84716810CDE92CE4",
    "tests/test_stage4b_u1_decisions_diagnostic.py": "C1A7B25D1F69E58812E994B0F8ECA7BAAE38EF50DE8BFA9246F4DF1EBF038D1C",
    "tests/test_stage4b_u1_goldfree.py": "CA61B466C7DDF583D827FD2D99C024D646BA3962C80B9137D480C84DEA374C71",
}
TRACKED_IMPLEMENTATION_FILES = (
    "AGENTS.md",
    "docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_5.md",
    "docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_5_REVIEW_1.md",
    "docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_APPROVAL_REQUEST.md",
    "docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_MANIFEST.json",
    "docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_APPROVAL_DECISION.md",
    "scripts/stage4b_u1_inventory_decision_schemas.py",
    "scripts/stage4b_u1_run_schema_inventory_synthetic_verification.py",
    "tests/test_stage4b_u1_decision_schema_inventory.py",
    *FROZEN_EXISTING_HASHES.keys(),
)
REQUIRED_ACTIVE_PROOF_SUFFIXES = (
    "test_homogeneous_flat_schema",
    "test_field_additions_and_removals",
    "test_field_order_only_difference",
    "test_bool_integer_and_finite_number_are_distinct",
    "test_nested_object_and_array_element_structure",
    "test_duplicate_top_level_key_rejected",
    "test_duplicate_nested_key_rejected",
    "test_invalid_json_rejected",
    "test_blank_line_rejected",
    "test_non_object_row_rejected",
    "test_nonfinite_constants_rejected",
    "test_value_and_id_content_not_leaked",
    "test_main_schema_count_and_lexicographic_tie_break",
    "test_success_cleans_staging_file_and_writes_exclusive_output",
    "test_write_failure_cleans_staging_and_partial_output",
    "test_official_reference_path_blocked_before_open",
    "test_inventory_has_no_prohibited_import_or_call",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def test_ids(suite: unittest.TestSuite) -> list[str]:
    ids: list[str] = []
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            ids.extend(test_ids(item))
        else:
            ids.append(item.id())
    return ids


def _path_key(path: Path) -> str:
    return os.path.normcase(os.path.abspath(os.fspath(path)))


def forbidden_official_paths(repo_root: Path) -> set[str]:
    amendment = json.loads(
        (repo_root / "docs" / "STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    amendment_5a_1 = json.loads(
        (repo_root / "docs" / "STAGE4B_U1_PREGOLD_AMENDMENT_5A_1_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    amendment_5b_v2 = json.loads(
        (repo_root / "docs" / "STAGE4B_U1_PREGOLD_AMENDMENT_5B_V2_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    resumption = json.loads(
        (repo_root / "docs" / "STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    values = {
        Path(amendment["frozen_future_5c_b_reference"]["path"]),
        Path(amendment_5b_v2["embedding_cache"]["path"]),
        Path(amendment_5b_v2["reference_decisions"]["path"]),
        repo_root / "docs" / "STAGE4A_R2_SOURCE_AUDIT.json",
    }
    values.update(
        Path(item["path"])
        for item in amendment_5a_1["frozen_channel_inputs"].values()
    )
    values.update(Path(path) for path in resumption["artifact_registry"].values())
    values.update(
        Path(path)
        for path in amendment_5b_v2["formal_outputs_that_must_remain_absent"]
    )
    return {_path_key(path) for path in values}


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/stage4b_u1_d_pregold_amendment_5c_a_synthetic_verification.json"
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
            candidate = _path_key(Path(supplied))
        except (OSError, TypeError, ValueError):
            return
        if candidate in forbidden:
            attempted.append(candidate)
            raise PermissionError(f"Amendment 5C-A blocked official path access: {candidate}")

    sys.addaudithook(audit_hook)
    frozen_hashes = {
        path: sha256_file(repo_root / path) for path in FROZEN_EXISTING_HASHES
    }
    if frozen_hashes != FROZEN_EXISTING_HASHES:
        raise ValueError("A frozen existing implementation or test file drifted")

    suite = unittest.defaultTestLoader.discover(
        str(repo_root / "tests"), pattern="test_stage4b_u1*.py"
    )
    discovered = sorted(test_ids(suite))
    inventory_tests = [
        test_id
        for test_id in discovered
        if test_id.startswith("test_stage4b_u1_decision_schema_inventory.")
    ]
    active_proofs = {
        suffix: [test_id for test_id in inventory_tests if test_id.endswith(suffix)]
        for suffix in REQUIRED_ACTIVE_PROOF_SUFFIXES
    }
    if any(len(matches) != 1 for matches in active_proofs.values()):
        raise ValueError("A required schema inventory proof test is missing or duplicated")

    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    count_gate = (
        result.testsRun == len(discovered)
        and result.testsRun >= 119
        and len(inventory_tests) >= 12
    )
    all_pass = (
        result.wasSuccessful()
        and not result.failures
        and not result.errors
        and not result.skipped
        and count_gate
        and not attempted
    )
    implementation_hashes = {
        path: sha256_file(repo_root / path) for path in TRACKED_IMPLEMENTATION_FILES
    }
    if {
        path: implementation_hashes[path] for path in FROZEN_EXISTING_HASHES
    } != FROZEN_EXISTING_HASHES:
        raise ValueError("A frozen file changed during synthetic verification")
    evidence: dict[str, object] = {
        "stage": "Stage4B-U1-D Pre-Gold Amendment 5C-A",
        "inventory_checkpoint": "stage4b_u1_reference_schema_inventory_v1",
        "status": "AMENDMENT_5C_A_SYNTHETICALLY_VERIFIED" if all_pass else "FAILED",
        "tests_run": result.testsRun,
        "existing_tests_required": 107,
        "minimum_new_inventory_tests": 12,
        "minimum_complete_tests": 119,
        "inventory_tests_run": len(inventory_tests),
        "test_ids": discovered,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "implementation_hashes": implementation_hashes,
        "frozen_existing_hashes_verified": True,
        "active_proof_tests": active_proofs,
        "official_path_access_guard": {
            "installed": True,
            "forbidden_path_count": len(forbidden),
            "blocked_or_attempted_access_count": len(attempted),
        },
        "schema_inventory_scope": {
            "value_free": True,
            "imports_or_calls_existing_comparator": False,
            "calls_existing_capture": False,
            "calls_existing_controller": False,
        },
        "official_reference_accessed": False,
        "official_schema_scan_executed": False,
        "official_capture_executed": False,
        "controller_rerun": False,
        "rankings_accessed": False,
        "policy_accessed": False,
        "verifier_executed": False,
        "evaluator_executed": False,
        "gold_accessed": False,
        "reservation_accessed": False,
        "stage3b_accessed": False,
        "verified_properties": [
            "UTF-8 JSONL requires one nonblank object per line",
            "duplicate keys fail closed at every object nesting level",
            "invalid JSON non-object rows and non-finite numbers fail closed",
            "null bool integer finite number string array and object remain distinct",
            "array schema excludes values order multiplicity and length",
            "ordered and order-insensitive signatures are deterministic",
            "field-order-only differences are separate from structural differences",
            "main ordered schema uses row-count mode and lexicographic tie-break",
            "schema output contains no fixture values raw IDs or salted IDs",
            "exclusive output and staging cleanup hold on success and failure",
            "future official reference path is rejected before open without 5C-B authorization",
            "the inventory module has no prohibited import or call",
            "all 107 prior Stage4B-U1 tests remain passing",
        ],
    }
    write_json(args.output, evidence)
    if not all_pass:
        sys.stderr.write(stream.getvalue())
        raise SystemExit(1)


if __name__ == "__main__":
    main()
