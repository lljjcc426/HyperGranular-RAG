from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import stage4h_cbe_common as common
import stage4h_cbe_evaluate as evaluator
import stage4h_cbe_goldfree_runner as runner
import stage4h_cbe_prepare as prepare
import stage4h_cbe_retrieval as retrieval


def hotpot_row(native_id: str) -> dict:
    context = []
    for index in range(10):
        context.append(
            [
                f"Title {index}",
                [
                    f"Alpha evidence sentence {index}.",
                    f"Beta evidence sentence {index}.",
                    f"Gamma evidence sentence {index}.",
                ],
            ]
        )
    return {
        "_id": native_id,
        "answer": "Alpha",
        "context": context,
        "level": "medium",
        "question": f"Which alpha belongs to {native_id}?",
        "supporting_facts": [["Title 0", 0], ["Title 1", 1]],
        "type": "bridge",
    }


def musique_row(native_id: str) -> dict:
    paragraphs = []
    for index in range(10):
        paragraphs.append(
            {
                "idx": index,
                "is_supporting": index in {0, 1},
                "paragraph_text": (
                    f"Alpha evidence sentence {index}. "
                    f"Beta evidence sentence {index}. "
                    f"Gamma evidence sentence {index}."
                ),
                "title": f"Title {index}",
            }
        )
    return {
        "answer": "Alpha",
        "answer_aliases": ["The Alpha"],
        "id": native_id,
        "paragraphs": paragraphs,
        "question": f"Which alpha belongs to {native_id}?",
        "question_decomposition": [
            {"paragraph_support_idx": 0},
            {"paragraph_support_idx": 1},
        ],
    }


def synthetic_blind() -> list[dict]:
    blind, _, _ = prepare.build_hotpot_channels(0, "hp-1", hotpot_row("hp-1"))
    return [blind]


class InputBoundaryTests(unittest.TestCase):
    def test_id_only_selection_excludes_history_before_hash_ranking(self) -> None:
        rows = [hotpot_row(f"hp-{index}") for index in range(6)]
        first = prepare.select_rows(
            rows, common.HOTPOT_DATASET, {"hp-0", "hp-2"}, 3
        )
        second = prepare.select_rows(
            rows, common.HOTPOT_DATASET, {"hp-0", "hp-2"}, 3
        )
        self.assertEqual(
            [item[1] for item in first],
            [item[1] for item in second],
        )
        self.assertFalse({"hp-0", "hp-2"} & {item[1] for item in first})

    def test_hotpot_blind_channel_contains_no_gold(self) -> None:
        blind, gold, metadata = prepare.build_hotpot_channels(
            0, "hp-1", hotpot_row("hp-1")
        )
        common.assert_no_gold_fields(blind, "blind")
        self.assertEqual(gold["evidence_granularity"], "official_supporting_sentence")
        self.assertIn("level", metadata)
        self.assertNotIn("answer", json.dumps(blind))

    def test_musique_uses_paragraph_gold_only(self) -> None:
        blind, gold, metadata = prepare.build_musique_channels(
            0, "2hop__1_2", musique_row("2hop__1_2")
        )
        common.assert_no_gold_fields(blind, "blind")
        self.assertEqual(
            gold["evidence_granularity"], "official_supporting_paragraph"
        )
        self.assertEqual(gold["supporting_paragraph_indices"], [0, 1])
        self.assertNotIn("supporting_unit_ids", gold)
        self.assertEqual(metadata["hop_count"], 2)

    def test_support_identity_mismatch_fails_closed(self) -> None:
        row = hotpot_row("hp-1")
        row["supporting_facts"][0] = ["Missing", 0]
        with self.assertRaisesRegex(ValueError, "support target"):
            prepare.build_hotpot_channels(0, "hp-1", row)


class RetrievalTests(unittest.TestCase):
    def test_bm25_prefers_matching_document(self) -> None:
        scores = retrieval.bm25_scores(
            "alpha bridge",
            ["unrelated text", "alpha bridge evidence", "alpha only"],
        )
        self.assertEqual(int(np.argmax(scores)), 1)
        self.assertTrue(np.isfinite(scores).all())

    def test_minmax_constant_is_zero(self) -> None:
        np.testing.assert_array_equal(
            retrieval.minmax(np.asarray([3.0, 3.0, 3.0])),
            np.zeros(3),
        )

    def test_no_protection_changes_only_placement(self) -> None:
        dense = [f"u{index}" for index in range(20)]
        inserted = ["u21", "u22"]
        full = dense[:10] + inserted + dense[10:18]
        actual = retrieval.no_protection_ranking(dense, full, inserted, 20)
        self.assertEqual(actual[:2], inserted)
        self.assertEqual(set(actual), set(full))

    def test_all_seven_rankings_are_complete_and_unique(self) -> None:
        units, queries = retrieval.build_units_queries(synthetic_blind())
        rng = np.random.default_rng(7)
        minilm_unit = rng.normal(size=(len(units), 16)).astype("float32")
        minilm_query = rng.normal(size=(len(queries), 16)).astype("float32")
        strong_unit = rng.normal(size=(len(units), 24)).astype("float32")
        strong_query = rng.normal(size=(len(queries), 24)).astype("float32")
        for array in (minilm_unit, minilm_query, strong_unit, strong_query):
            array /= np.linalg.norm(array, axis=1, keepdims=True)
        rankings, traces, _ = retrieval.build_rankings(
            units,
            queries,
            minilm_unit,
            minilm_query,
            strong_unit,
            strong_query,
        )
        self.assertEqual(len(rankings), 1)
        self.assertEqual(len(traces), 1)
        self.assertEqual(set(rankings[0]["methods"]), set(common.METHODS))
        for values in rankings[0]["methods"].values():
            self.assertEqual(len(values), 20)
            self.assertEqual(len(values), len(set(values)))

    def test_flat_ablation_is_frozen_not_fairly_defined(self) -> None:
        config = common.load_json(ROOT / "configs" / "stage4h_cbe_official.json")
        self.assertEqual(
            config["ablations"]["FLAT_UNIT_PROTECTED_INSERTION"],
            "NOT_FAIRLY_DEFINED",
        )


class DeterminismAndStatisticsTests(unittest.TestCase):
    def test_rerun_selection_is_deterministic_and_stratified(self) -> None:
        queries = []
        for dataset in common.DATASETS:
            for index in range(120):
                queries.append(
                    {
                        "dataset": dataset,
                        "query_id": f"{dataset}::q{index}",
                        "sample_id": f"q{index}",
                    }
                )
        first = runner.select_rerun_queries(queries)
        second = runner.select_rerun_queries(queries)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 200)
        self.assertEqual(
            {dataset: sum(row["dataset"] == dataset for row in first) for dataset in common.DATASETS},
            {dataset: 100 for dataset in common.DATASETS},
        )

    def test_answer_metric_alias_max(self) -> None:
        em, f1 = evaluator.answer_scores("the alpha", ["beta", "Alpha"])
        self.assertEqual(em, 1.0)
        self.assertEqual(f1, 1.0)

    def test_holm_step_down_is_monotone(self) -> None:
        adjusted = evaluator.holm_adjust({"a": 0.001, "b": 0.02, "c": 0.03, "d": 0.5})
        self.assertAlmostEqual(adjusted["a"], 0.004)
        self.assertGreaterEqual(adjusted["b"], adjusted["a"])
        self.assertGreaterEqual(adjusted["c"], adjusted["b"])

    def test_outcome_does_not_call_crossing_zero_no_effect(self) -> None:
        summary = {
            "delta_answer_f1": {
                "ci95_lower": -0.01,
                "ci95_upper": 0.02,
                "point": 0.005,
            },
            "delta_answer_em": {
                "ci95_lower": -0.005,
                "ci95_upper": 0.01,
                "point": 0.0,
            },
        }
        self.assertEqual(evaluator.outcome(summary, 0.2), "INCONCLUSIVE")


if __name__ == "__main__":
    unittest.main()
