from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import stage4b_u1_gold_evaluation_verifier as verifier


def ranking_row(query_id: str, *, gain: bool) -> dict[str, object]:
    prefix = [f"u{index}" for index in range(10)]
    if gain:
        dense = prefix + ["u10", "u11"]
        q25 = prefix + ["gold", "u10"]
    else:
        dense = prefix + ["gold", "u11"]
        q25 = prefix + ["x", "u11"]
    return {
        "query_id": query_id,
        "dataset": "synthetic",
        "sample_id": query_id,
        "dense_top20_unit_ids": dense,
        "q25_top20_unit_ids": q25,
        "final_top20_unit_ids": q25,
        "q25_inserted_unit_ids": [q25[10]],
        "final_inserted_unit_ids": [q25[10]],
        "planned_insert_count": 1,
        "trigger_u1": 1,
    }


class GoldEvaluationVerifierTests(unittest.TestCase):
    def test_independent_query_audit_recomputation(self) -> None:
        rankings = [ranking_row("q-gain", gain=True), ranking_row("q-harm", gain=False)]
        gold_map = {
            "queries": [
                {"query_id": "q-gain", "gold_unit_ids": ["gold"], "question_type": "gain"},
                {"query_id": "q-harm", "gold_unit_ids": ["gold"], "question_type": "harm"},
            ]
        }
        rows = verifier.derive_query_audit(rankings, gold_map)
        self.assertEqual(rows[0]["q25_gain_event"], 1)
        self.assertEqual(rows[0]["u1_gain_event"], 1)
        self.assertEqual(rows[1]["q25_harm_event"], 1)
        self.assertEqual(rows[1]["u1_harm_event"], 1)

    def test_summary_and_decision_are_independent(self) -> None:
        rankings = [ranking_row("q-gain", gain=True), ranking_row("q-harm", gain=False)]
        gold_map = {
            "queries": [
                {"query_id": "q-gain", "gold_unit_ids": ["gold"]},
                {"query_id": "q-harm", "gold_unit_ids": ["gold"]},
            ]
        }
        summary = verifier.summarize(verifier.derive_query_audit(rankings, gold_map), "ALL")
        self.assertEqual(summary["q25_gain_events"], 1)
        self.assertEqual(summary["q25_harm_events"], 1)
        self.assertEqual(summary["retention_gap"], 0.0)
        decision = verifier.build_decision(summary)
        self.assertFalse(decision["passed"])
        self.assertEqual(decision["decision"], "STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED")

    def test_effective_k_structure_rejects_wrong_final_selector(self) -> None:
        row = ranking_row("q", gain=True)
        row["final_top20_unit_ids"] = row["dense_top20_unit_ids"]
        with self.assertRaises(ValueError):
            verifier.derive_inserted_ids(row)

    def test_deterministic_rerun_requires_exact_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            left = Path(temp_dir) / "left.json"
            right = Path(temp_dir) / "right.json"
            left.write_bytes(b"{\"a\":1}\n")
            right.write_bytes(b"{\"a\":1}\r\n")
            with self.assertRaises(ValueError):
                verifier.verify_exact_repeat(left, right, "fixture")


if __name__ == "__main__":
    unittest.main()
