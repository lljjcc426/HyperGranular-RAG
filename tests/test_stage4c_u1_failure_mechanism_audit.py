from __future__ import annotations

import copy
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import stage4c_u1_failure_mechanism_audit as fma  # noqa: E402


def synthetic_triplet(
    index: int,
    label: str,
    *,
    trigger: int,
    question_type: str = "bridge_comparison",
) -> tuple[dict, dict, dict]:
    query_id = f"q-{index}"
    sample_id = f"sample-{index}"
    dense = [f"d-{index}-{unit}" for unit in range(12)]
    inserted = f"x-{index}"
    q25 = dense[:10] + [inserted, dense[10]]
    final = q25 if trigger else dense
    dense_cr20, q25_cr20 = {
        "GAIN": (0, 1),
        "HARM": (1, 0),
        "NEUTRAL": (1, 1),
    }[label]
    gold = int(label == "GAIN")
    non_gold = 1 - gold
    u1_cr20 = q25_cr20 if trigger else dense_cr20
    u_margin = 0.2 + index * 0.001
    u_boundary = 0.4 + index * 0.001
    uncertainty = (u_margin + u_boundary) / 2.0
    r_edge = 0.25
    r_candidate = 1.0
    readiness = math.sqrt(r_edge * r_candidate)
    score = uncertainty * readiness
    decision = {
        "ball_score_margin": 0.1 + index * 0.001,
        "boundary_margin": 0.2 + index * 0.001,
        "dataset": "2wikimultihopqa",
        "feasible": 1,
        "ordered_rank": index + 1,
        "planned_insert_count": 1,
        "query_id": query_id,
        "r_candidate": r_candidate,
        "r_edge": r_edge,
        "readiness": readiness,
        "sample_id": sample_id,
        "score": score,
        "selected_edge_count": 2,
        "tie_hash": f"tie-{index}",
        "trigger_u1": trigger,
        "u_boundary": u_boundary,
        "u_margin": u_margin,
        "uncertainty": uncertainty,
    }
    ranking = {
        "dataset": "2wikimultihopqa",
        "dense_top20_unit_ids": dense,
        "final_inserted_unit_ids": [inserted] if trigger else [],
        "final_top20_unit_ids": final,
        "planned_insert_count": 1,
        "q25_inserted_unit_ids": [inserted],
        "q25_top20_unit_ids": q25,
        "query_id": query_id,
        "sample_id": sample_id,
        "trigger_u1": trigger,
    }
    audit = {
        "dataset": "2wikimultihopqa",
        "dense_cr20": dense_cr20,
        "dense_er20": 0.5 + 0.1 * dense_cr20,
        "planned_insert_count": 1,
        "q25_cr20": q25_cr20,
        "q25_er20": 0.5 + 0.1 * q25_cr20,
        "q25_gain_event": int(label == "GAIN"),
        "q25_harm_event": int(label == "HARM"),
        "q25_inserted_gold_units": gold,
        "q25_inserted_non_gold_units": non_gold,
        "q25_inserted_units": 1,
        "query_id": query_id,
        "question_type": question_type,
        "sample_id": sample_id,
        "trigger_u1": trigger,
        "u1_cr20": u1_cr20,
        "u1_er20": 0.5 + 0.1 * u1_cr20,
        "u1_gain_event": int(trigger == 1 and label == "GAIN"),
        "u1_harm_event": int(trigger == 1 and label == "HARM"),
        "u1_inserted_gold_units": gold if trigger else 0,
        "u1_inserted_non_gold_units": non_gold if trigger else 0,
        "u1_inserted_units": trigger,
    }
    return decision, ranking, audit


def three_row_inputs() -> tuple[list[dict], list[dict], list[dict]]:
    triplets = [
        synthetic_triplet(0, "GAIN", trigger=1),
        synthetic_triplet(1, "HARM", trigger=0),
        synthetic_triplet(2, "NEUTRAL", trigger=0),
    ]
    return tuple([copy.deepcopy(row[index]) for row in triplets] for index in range(3))


def joined_three_rows() -> list[dict]:
    decisions, rankings, audits = three_row_inputs()
    return fma.validate_and_join(decisions, rankings, audits, enforce_official_counts=False)


def panel_summary(*, auc: float, interval: list[float], folds_above: int, stable: bool) -> dict:
    return {
        "auroc": auc,
        "auroc_percentile95": interval,
        "fold_auroc_above_0_5": folds_above,
        "stable_gain_harm_signal": stable,
    }


class LabelsAndContractsTests(unittest.TestCase):
    def test_exact_label_definitions(self) -> None:
        self.assertEqual(fma.derive_label(0, 1), "GAIN")
        self.assertEqual(fma.derive_label(1, 0), "HARM")
        self.assertEqual(fma.derive_label(0, 0), "NEUTRAL")
        self.assertEqual(fma.derive_label(1, 1), "NEUTRAL")

    def test_strict_join_and_frozen_count_reconciliation(self) -> None:
        decisions, rankings, audits = three_row_inputs()
        with mock.patch.multiple(
            fma,
            QUERY_COUNT=3,
            GAIN_COUNT=1,
            HARM_COUNT=1,
            RETAINED_GAIN_COUNT=1,
            RETAINED_HARM_COUNT=0,
        ):
            rows = fma.validate_and_join(
                decisions, rankings, audits, enforce_official_counts=True
            )
        self.assertEqual([row["label"] for row in rows], ["GAIN", "HARM", "NEUTRAL"])
        self.assertEqual(rows[0]["final_cr20"], rows[0]["u1_cr20"])

    def test_duplicates_missing_identity_and_types_are_rejected(self) -> None:
        decisions, rankings, audits = three_row_inputs()
        duplicate = copy.deepcopy(decisions)
        duplicate[1]["query_id"] = duplicate[0]["query_id"]
        with self.assertRaises(ValueError):
            fma.validate_and_join(duplicate, rankings, audits, enforce_official_counts=False)
        with self.assertRaises(ValueError):
            fma.validate_and_join(decisions, rankings[:-1], audits, enforce_official_counts=False)
        bad_identity = copy.deepcopy(rankings)
        bad_identity[0]["sample_id"] = "wrong"
        with self.assertRaises(ValueError):
            fma.validate_and_join(decisions, bad_identity, audits, enforce_official_counts=False)
        bad_tie = copy.deepcopy(decisions)
        bad_tie[0]["tie_hash"] = 123
        with self.assertRaises(ValueError):
            fma.validate_and_join(bad_tie, rankings, audits, enforce_official_counts=False)
        bad_trigger = copy.deepcopy(audits)
        bad_trigger[0]["trigger_u1"] = True
        with self.assertRaises(ValueError):
            fma.validate_and_join(decisions, rankings, bad_trigger, enforce_official_counts=False)
        bad_planned = copy.deepcopy(rankings)
        bad_planned[0]["planned_insert_count"] = 1.0
        with self.assertRaises(ValueError):
            fma.validate_and_join(decisions, bad_planned, audits, enforce_official_counts=False)

    def test_formula_and_nonfinite_rejection(self) -> None:
        decisions, rankings, audits = three_row_inputs()
        bad_score = copy.deepcopy(decisions)
        bad_score[0]["score"] += 0.01
        with self.assertRaises(ValueError):
            fma.validate_and_join(bad_score, rankings, audits, enforce_official_counts=False)
        bad_number = copy.deepcopy(decisions)
        bad_number[0]["ball_score_margin"] = float("inf")
        with self.assertRaises(ValueError):
            fma.validate_and_join(bad_number, rankings, audits, enforce_official_counts=False)

    def test_frozen_summary_reconciliation_and_tamper_rejection(self) -> None:
        rows = joined_three_rows()
        overall = fma.aggregate_frozen_metrics(rows, "ALL")
        question = fma.aggregate_frozen_metrics(rows, "bridge_comparison")
        baseline_fields = {
            name: overall[name]
            for name in (
                "queries",
                "q25_gain_events",
                "q25_harm_events",
                "dense_er20",
                "dense_cr20",
                "q25_er20",
                "q25_cr20",
            )
        }
        summary = {
            "overall": overall,
            "question_types": [question],
            "baseline_equivalence": {"observed": baseline_fields},
        }
        hashes = {
            "primary_query_audit": fma.INPUT_SPECS["query_audit"]["sha256"],
            "primary_summary": fma.INPUT_SPECS["gold_summary"]["sha256"],
            "rerun_query_audit": fma.INPUT_SPECS["query_audit"]["sha256"],
            "rerun_summary": fma.INPUT_SPECS["gold_summary"]["sha256"],
        }
        post_gold = {"queries": 3, "output_hashes": hashes}
        fma.verify_frozen_summary(rows, summary, post_gold)
        tampered = copy.deepcopy(summary)
        tampered["overall"]["q25_inserted_units"] += 1
        with self.assertRaises(ValueError):
            fma.verify_frozen_summary(rows, tampered, post_gold)


class StatisticsTests(unittest.TestCase):
    def test_tie_aware_auroc_ap_and_overlap(self) -> None:
        self.assertEqual(fma.auroc([1, 0, 1, 0], [1.0, 0.0, 1.0, 0.0]), 1.0)
        self.assertEqual(fma.average_precision([1, 0, 1, 0], [1.0, 0.0, 1.0, 0.0]), 1.0)
        self.assertEqual(fma.auroc([1, 0, 1, 0], [0.5, 0.5, 0.5, 0.5]), 0.5)
        self.assertEqual(fma.average_precision([1, 0, 1, 0], [0.5, 0.5, 0.5, 0.5]), 0.5)
        self.assertEqual(fma.distribution_overlap(np.array([1.0]), np.array([1.0])), 1.0)
        self.assertEqual(
            fma.distribution_overlap(np.array([0.0, 0.1]), np.array([0.9, 1.0])), 0.0
        )

    def test_quantiles_and_bootstrap_are_deterministic(self) -> None:
        rows = [{"label": "GAIN", "x": value} for value in (1.0, 2.0, 3.0, 4.0)]
        with mock.patch.object(fma, "BOOTSTRAP_ITERATIONS", 100):
            first = fma.distribution_row("x", "GAIN", rows)
            second = fma.distribution_row("x", "GAIN", rows)
        self.assertAlmostEqual(first["q10"], 1.3)
        self.assertEqual(first, second)

    def test_fixed_decile_boundaries_and_cumulative_arithmetic(self) -> None:
        self.assertEqual(fma.fixed_decile(1, 100), 1)
        self.assertEqual(fma.fixed_decile(10, 100), 1)
        self.assertEqual(fma.fixed_decile(11, 100), 2)
        self.assertEqual(fma.fixed_decile(100, 100), 10)
        rows = []
        for index in range(20):
            rows.append(
                {
                    "feasible": 1,
                    "ordered_rank": index + 1,
                    "label": "GAIN" if index == 0 else "HARM" if index == 1 else "NEUTRAL",
                    "trigger_u1": int(index == 0),
                    "q25_inserted_units": 1,
                    "q25_cr20": int(index == 0),
                    "dense_cr20": int(index == 1),
                }
            )
        with mock.patch.multiple(
            fma,
            QUERY_COUNT=20,
            GAIN_COUNT=1,
            HARM_COUNT=1,
            RETAINED_GAIN_COUNT=1,
            RETAINED_HARM_COUNT=0,
        ):
            deciles, _ = fma.build_deciles(rows)
        self.assertEqual(deciles[0]["queries"], 2)
        self.assertEqual(deciles[0]["cumulative_gains"], 1)
        self.assertEqual(deciles[0]["cumulative_harms"], 1)
        self.assertEqual(deciles[-1]["cumulative_inserted_units"], 20)

    def test_mechanism_category_priority(self) -> None:
        self.assertEqual(fma.mechanism_category("HARM", 1, 1), "DISPLACEMENT_HARM_QUERY")
        self.assertEqual(fma.mechanism_category("GAIN", 1, 0), "PURE_GAIN_QUERY")
        self.assertEqual(fma.mechanism_category("GAIN", 1, 2), "MIXED_GAIN_NOISE_QUERY")
        self.assertEqual(fma.mechanism_category("NEUTRAL", 0, 2), "PURE_NOISE_QUERY")
        self.assertEqual(fma.mechanism_category("NEUTRAL", 1, 0), "NO_EFFECT_QUERY")
        with self.assertRaises(ValueError):
            fma.mechanism_category("HARM", 0, 0)


class OofTests(unittest.TestCase):
    def test_stratified_folds_are_deterministic_and_balanced(self) -> None:
        y = np.asarray([0] * 31 + [1] * 24)
        first = fma.stratified_fold_ids(y, 5, fma.BOOTSTRAP_SEED)
        second = fma.stratified_fold_ids(y, 5, fma.BOOTSTRAP_SEED)
        np.testing.assert_array_equal(first, second)
        for value in (0, 1):
            counts = [int(np.sum((y == value) & (first == fold))) for fold in range(5)]
            self.assertLessEqual(max(counts) - min(counts), 1)

    def test_preprocessing_uses_training_fold_only(self) -> None:
        train = np.asarray([[0.0], [2.0], [math.nan]])
        test = np.asarray([[100.0], [math.nan]])
        train_scaled, test_scaled, audit = fma.preprocess_train_test(train, test)
        self.assertEqual(audit["medians"], [1.0])
        self.assertEqual(audit["means"], [1.0])
        self.assertAlmostEqual(float(np.mean(train_scaled)), 0.0)
        self.assertEqual(test_scaled[1, 0], 0.0)
        self.assertGreater(test_scaled[0, 0], 50.0)

    def test_logistic_oof_calibration_and_deterministic_bytes(self) -> None:
        rows = []
        y = np.asarray([0] * 25 + [1] * 25, dtype=np.int64)
        for index in range(50):
            rows.append(
                {
                    "query_id": f"q-{index}",
                    "question_type": "bridge_comparison" if index % 2 else "comparison",
                    "score": float(index),
                }
            )
        with mock.patch.object(fma, "BOOTSTRAP_ITERATIONS", 50):
            first = fma.run_oof_panel(rows, y, "TASK_A_GAIN_VS_HARM", "ONE", ["score"])
            second = fma.run_oof_panel(rows, y, "TASK_A_GAIN_VS_HARM", "ONE", ["score"])
        np.testing.assert_array_equal(first[0], second[0])
        self.assertEqual(sum(bin_["count"] for bin_ in first[3]["calibration"]["bins"]), 50)
        self.assertGreater(first[3]["auroc"], 0.9)
        rendered = []
        for probabilities, folds, _, _ in (first, second):
            output = [
                {
                    "task": "TASK_A_GAIN_VS_HARM",
                    "feature_panel": "ONE",
                    "query_id": row["query_id"],
                    "question_type": row["question_type"],
                    "binary_label": int(y[index]),
                    "fold": int(folds[index]),
                    "probability": float(probabilities[index]),
                    "prediction_at_0_5": int(probabilities[index] >= 0.5),
                    "original_u1_score": row["score"],
                }
                for index, row in enumerate(rows)
            ]
            rendered.append(fma.render_csv(output, fma.OOF_COLUMNS))
        self.assertEqual(rendered[0], rendered[1])

    def test_decision_rules(self) -> None:
        stable = {
            name: panel_summary(auc=0.70, interval=[0.55, 0.80], folds_above=4, stable=True)
            for name in fma.FEATURE_PANELS
        }
        summary = {"TASK_A_GAIN_VS_HARM": stable}
        self.assertEqual(
            fma.assign_decision(summary, True, True)[0],
            "PROCEED_TO_U2_CANDIDATE_LEVEL_PROTOCOL_DESIGN",
        )
        weak = {
            name: panel_summary(auc=0.55, interval=[0.45, 0.65], folds_above=2, stable=False)
            for name in fma.FEATURE_PANELS
        }
        summary = {"TASK_A_GAIN_VS_HARM": weak}
        self.assertEqual(
            fma.assign_decision(summary, False, True)[0],
            "INSUFFICIENT_SIGNAL_STOP_CONTROLLER_LINE",
        )
        self.assertEqual(
            fma.assign_decision(summary, False, False)[0],
            "MECHANISM_EVIDENCE_INCONCLUSIVE",
        )


class BoundaryAndAtomicityTests(unittest.TestCase):
    def test_forbidden_features_and_exact_input_allowlist(self) -> None:
        fma.validate_probe_features()
        with mock.patch.dict(
            fma.FEATURE_PANELS,
            {"BAD": ["score", "question_type"]},
            clear=True,
        ):
            with self.assertRaises(ValueError):
                fma.validate_probe_features()
        expected = {
            "results/stage4b_u1_d_official_dev4500_simplified_v1_decisions.jsonl",
            "results/stage4b_u1_d_official_dev4500_simplified_v1_rankings.jsonl",
            "results/stage4b_u1_d_official_dev4500_simplified_v1_policy.json",
            "results/stage4b_u1_d_official_dev4500_simplified_v1_verified_pre_gold.json",
            "results/stage4b_u1_d_official_dev4500_simplified_v1_query_audit.jsonl",
            "results/stage4b_u1_d_official_dev4500_simplified_v1_evaluation_summary.json",
            "results/stage4b_u1_d_official_dev4500_simplified_v1_verified_post_gold.json",
        }
        paths = {spec["path"] for spec in fma.INPUT_SPECS.values()}
        self.assertEqual(paths, expected)
        self.assertFalse(
            any(token in path.lower() for path in paths for token in ("reservation", "stage3b", "gold_map"))
        )

    def test_atomic_no_overwrite_promotion(self) -> None:
        artifacts = {name: f"payload::{name}\n".encode() for name in fma.OUTPUT_NAMES}
        with tempfile.TemporaryDirectory() as temporary:
            output_dir = Path(temporary) / "results"
            fma.promote_artifacts(output_dir, artifacts)
            for name, filename in fma.OUTPUT_NAMES.items():
                self.assertEqual((output_dir / filename).read_bytes(), artifacts[name])
            with self.assertRaises(ValueError):
                fma.promote_artifacts(output_dir, artifacts)
            self.assertFalse((output_dir / ".stage4c_u1_fma.pending").exists())

    def test_json_rendering_is_deterministic_and_rejects_nonfinite(self) -> None:
        value = {"z": 1, "a": [True, None, 0.5]}
        self.assertEqual(fma.render_json(value), fma.render_json(copy.deepcopy(value)))
        self.assertEqual(list(json.loads(fma.render_json(value))), ["a", "z"])
        with self.assertRaises(ValueError):
            fma.render_json({"bad": float("nan")})


if __name__ == "__main__":
    unittest.main()
