from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import stage4g_gtr_common as common
import stage4g_gtr_evaluate as evaluate


class Stage4GTests(unittest.TestCase):
    def test_rerun_subset_is_stratified_deterministic_and_gold_free(self):
        queries = [
            {"dataset": dataset, "query_id": f"{dataset}::q{i}"}
            for dataset in common.DATASETS
            for i in range(150)
        ]
        first = common.select_rerun_query_ids(queries)
        second = common.select_rerun_query_ids(list(reversed(queries)))
        self.assertEqual(first, second)
        self.assertEqual({key: len(value) for key, value in first.items()}, {key: 100 for key in common.DATASETS})

    def test_semantic_prompt_digest_does_not_accept_method_or_gold(self):
        units = [{"unit_id": "u1", "title": "T", "text": "Evidence"}]
        digest = common.semantic_prompt_digest("Question?", units, ["[1] T: Evidence"])
        self.assertEqual(len(digest), 64)
        with self.assertRaises(ValueError):
            common.assert_no_gold_or_method({"answer": "leak"}, "prompt")
        with self.assertRaises(ValueError):
            common.assert_no_gold_or_method({"method": "DENSE_TOP20"}, "prompt")

    def test_dataset_specific_answer_scoring(self):
        self.assertEqual(evaluate.answer_scores(common.DATASETS[0], "The Eiffel Tower", ["Eiffel Tower"]), (1.0, 1.0))
        self.assertEqual(evaluate.answer_scores(common.DATASETS[0], "yes", ["no"]), (0.0, 0.0))
        em, f1 = evaluate.answer_scores(common.DATASETS[1], "Paris France", ["Paris", "Lyon"])
        self.assertEqual(em, 0.0)
        self.assertAlmostEqual(f1, 2 / 3)

    def test_stratified_bootstrap_is_equal_weight_and_deterministic(self):
        hotpot = np.ones(10, dtype="float64")
        musique = np.zeros(30, dtype="float64")
        first = common.stratified_equal_weight_bootstrap(hotpot, musique)
        second = common.stratified_equal_weight_bootstrap(hotpot, musique)
        self.assertEqual(first, second)
        self.assertEqual(first["point"], 0.5)

    def test_decision_supported_requires_both_dataset_directions(self):
        def interval(point=0.02, lower=0.01, upper=0.03):
            return {"point": point, "lower_95": lower, "upper_95": upper}
        datasets = {
            dataset: {"bootstrap": {"delta_answer_f1": interval(), "delta_answer_em": interval(0.0, -0.005, 0.005)}}
            for dataset in common.DATASETS
        }
        pooled = {"delta_answer_f1": interval(), "delta_answer_em": interval(0.0, -0.005, 0.005)}
        self.assertEqual(common.scientific_decision(datasets, pooled), "GENERATOR_TRANSFER_SUPPORTED")
        datasets[common.DATASETS[1]]["bootstrap"]["delta_answer_f1"] = interval(-0.001, -0.01, 0.01)
        self.assertEqual(common.scientific_decision(datasets, pooled), "GENERATOR_TRANSFER_INCONCLUSIVE")

    def test_decision_negative_uses_any_dataset_upper_bound(self):
        positive = {"point": 0.02, "lower_95": 0.01, "upper_95": 0.03}
        neutral_em = {"point": 0.0, "lower_95": -0.005, "upper_95": 0.005}
        datasets = {
            dataset: {"bootstrap": {"delta_answer_f1": dict(positive), "delta_answer_em": dict(neutral_em)}}
            for dataset in common.DATASETS
        }
        datasets[common.DATASETS[0]]["bootstrap"]["delta_answer_f1"] = {"point": -0.02, "lower_95": -0.03, "upper_95": -0.01}
        pooled = {"delta_answer_f1": dict(positive), "delta_answer_em": dict(neutral_em)}
        self.assertEqual(common.scientific_decision(datasets, pooled), "GENERATOR_TRANSFER_NEGATIVE")

    def test_strict_integer_rejects_bool_and_float(self):
        for value in (True, 1.0, "1"):
            with self.assertRaises(ValueError):
                common.require_int(value, "value")

    def test_ranking_digest_preserves_effective_k_order(self):
        self.assertEqual(common.ranking_digest(["u1", "u2"]), common.ranking_digest(["u1", "u2"]))
        self.assertNotEqual(common.ranking_digest(["u1", "u2"]), common.ranking_digest(["u2", "u1"]))


if __name__ == "__main__":
    unittest.main()
