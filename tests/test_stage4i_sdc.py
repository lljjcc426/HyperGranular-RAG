from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import stage4h_cbe_prepare as stage4h_prepare
import stage4i_sdc_common as common
import stage4i_sdc_evaluate as evaluator
import stage4i_sdc_independent_verifier as verifier
import stage4i_sdc_prepare as prepare
import stage4i_sdc_retrieval as retrieval


def hotpot_row(native_id: str) -> dict:
    context = [
        [
            f"Title {paragraph}",
            [
                f"Alpha evidence sentence {paragraph}.",
                f"Beta evidence sentence {paragraph}.",
                f"Gamma evidence sentence {paragraph}.",
            ],
        ]
        for paragraph in range(10)
    ]
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
    return {
        "answer": "Alpha",
        "answer_aliases": ["The Alpha"],
        "id": native_id,
        "paragraphs": [
            {
                "idx": paragraph,
                "is_supporting": paragraph in {0, 1},
                "paragraph_text": (
                    f"Alpha evidence sentence {paragraph}. "
                    f"Beta evidence sentence {paragraph}. "
                    f"Gamma evidence sentence {paragraph}."
                ),
                "title": f"Title {paragraph}",
            }
            for paragraph in range(10)
        ],
        "question": f"Which alpha belongs to {native_id}?",
        "question_decomposition": [
            {"paragraph_support_idx": 0},
            {"paragraph_support_idx": 1},
        ],
    }


def trace(dataset: str, insertable: bool, full_budget: bool = False) -> dict:
    inserted = 4 if full_budget else 1 if insertable else 0
    return {
        "dataset": dataset,
        "full_eligible_count": 3 if insertable else 0,
        "full_insert_count": inserted,
        "full_overlap_bge_top10_count": 0,
        "full_overlap_bge_top20_count": 1 if insertable else 0,
        "full_post_dedup_count": inserted,
    }


def decision_summary(
    *,
    pooled_f1: tuple[float, float, float],
    pooled_em: tuple[float, float, float] = (0.0, 0.0, 0.0),
    dataset_points: tuple[float, float] = (0.01, 0.01),
    dataset_uppers: tuple[float, float] = (0.02, 0.02),
) -> dict:
    return {
        "dataset_equal_weight": {
            "delta_answer_f1": {
                "ci95_lower": pooled_f1[0],
                "ci95_upper": pooled_f1[1],
                "point": pooled_f1[2],
            },
            "delta_answer_em": {
                "ci95_lower": pooled_em[0],
                "ci95_upper": pooled_em[1],
                "point": pooled_em[2],
            },
        },
        "datasets": {
            dataset: {
                "delta_answer_f1": {
                    "ci95_lower": -0.01,
                    "ci95_upper": dataset_uppers[index],
                    "point": dataset_points[index],
                }
            }
            for index, dataset in enumerate(common.DATASETS)
        },
    }


def evaluation_fixture() -> tuple[list[dict], list[dict], list[dict], list[dict], list[dict]]:
    specs = [
        (
            common.HOTPOT_DATASET,
            "hp-1",
            ["hp-1::p0::s0", "hp-1::p1::s0"],
            None,
        ),
        (
            common.MUSIQUE_DATASET,
            "2hop__1_2",
            None,
            [0, 1],
        ),
    ]
    gold: list[dict] = []
    queries: list[dict] = []
    rankings: list[dict] = []
    predictions: list[dict] = []
    prompts: list[dict] = []
    for dataset, sample_id, hotpot_targets, musique_targets in specs:
        query_id = f"{dataset}::{sample_id}"
        query = {
            "dataset": dataset,
            "num_candidate_units": 4,
            "query_id": query_id,
            "question": "What is the answer?",
            "sample_id": sample_id,
        }
        queries.append(query)
        bge = [
            f"{sample_id}::p0::s0",
            f"{sample_id}::p2::s0",
            f"{sample_id}::p3::s0",
        ]
        protected = [
            f"{sample_id}::p0::s0",
            f"{sample_id}::p1::s0",
            f"{sample_id}::p3::s0",
        ]
        unprotected = [
            f"{sample_id}::p1::s0",
            f"{sample_id}::p0::s0",
            f"{sample_id}::p3::s0",
        ]
        methods = {
            "BGE_TOP20": bge,
            "BGE_HGRAG_PROTECTED_TOP20": protected,
            "BGE_HGRAG_UNPROTECTED_TOP20": unprotected,
            "BGE_HGRAG_NO_FACET_TOP20": bge,
        }
        rankings.append(
            {
                "dataset": dataset,
                "effective_k": 3,
                "full_inserted_unit_ids": [f"{sample_id}::p1::s0"],
                "methods": methods,
                "no_facet_inserted_unit_ids": [],
                "query_id": query_id,
                "sample_id": sample_id,
            }
        )
        gold_row = {
            "answers": ["Alpha"],
            "dataset": dataset,
            "query_id": query_id,
            "sample_id": sample_id,
        }
        if dataset == common.HOTPOT_DATASET:
            gold_row.update(
                {
                    "evidence_granularity": "official_supporting_sentence",
                    "supporting_unit_ids": hotpot_targets,
                }
            )
        else:
            gold_row.update(
                {
                    "evidence_granularity": "official_supporting_paragraph",
                    "supporting_paragraph_indices": musique_targets,
                }
            )
        gold.append(gold_row)
        for method in common.METHODS:
            prediction = "Alpha" if method != "BGE_TOP20" else "UNKNOWN"
            predictions.append(
                {
                    "dataset": dataset,
                    "method": method,
                    "prediction": prediction,
                    "query_id": query_id,
                    "sample_id": sample_id,
                }
            )
            prompts.append(
                {
                    "dataset": dataset,
                    "evidence_unit_ids": methods[method],
                    "input_token_count": 100,
                    "method": method,
                    "prompt_sha256": "A" * 64,
                    "query_id": query_id,
                    "rank1_truncated": False,
                    "sample_id": sample_id,
                }
            )
    return gold, queries, predictions, prompts, rankings


class InputBoundaryTests(unittest.TestCase):
    def test_id_only_selection_excludes_history_before_hash_ranking(self) -> None:
        rows = [hotpot_row(f"hp-{index}") for index in range(8)]
        first = prepare.select_rows(
            rows, common.HOTPOT_DATASET, {"hp-0", "hp-2"}, 4
        )
        second = prepare.select_rows(
            rows, common.HOTPOT_DATASET, {"hp-0", "hp-2"}, 4
        )
        self.assertEqual([row[1] for row in first], [row[1] for row in second])
        self.assertFalse({"hp-0", "hp-2"} & {row[1] for row in first})

    def test_blind_channels_contain_no_gold_or_metadata(self) -> None:
        hotpot_blind, hotpot_gold, _ = stage4h_prepare.build_hotpot_channels(
            0, "hp-1", hotpot_row("hp-1")
        )
        musique_blind, musique_gold, _ = stage4h_prepare.build_musique_channels(
            0, "2hop__1_2", musique_row("2hop__1_2")
        )
        common.assert_no_gold_fields([hotpot_blind, musique_blind], "blind")
        serialized = json.dumps([hotpot_blind, musique_blind])
        self.assertNotIn('"answer"', serialized)
        self.assertEqual(
            hotpot_gold["evidence_granularity"],
            "official_supporting_sentence",
        )
        self.assertEqual(
            musique_gold["evidence_granularity"],
            "official_supporting_paragraph",
        )

    def test_gold_identity_mismatch_fails_closed(self) -> None:
        gold, queries, _, _, _ = evaluation_fixture()
        gold[0]["sample_id"] = "wrong"
        with self.assertRaisesRegex(ValueError, "sample_id differs"):
            verifier._validated_gold(gold, queries)


class RetrievalAndEligibilityTests(unittest.TestCase):
    def test_protected_and_unprotected_share_inserted_set_only_placement_differs(
        self,
    ) -> None:
        bge = [f"u{index}" for index in range(20)]
        inserted = ["u20", "u21", "u22"]
        protected = retrieval.place_protected(bge, inserted, 20, 10)
        unprotected = retrieval.place_unprotected(bge, inserted, 20)
        self.assertEqual(protected[10:13], inserted)
        self.assertEqual(unprotected[:3], inserted)
        self.assertEqual(set(protected), set(unprotected))
        self.assertEqual(set(protected) - set(bge), set(inserted))

    def test_sidecar_duplicate_with_bge_fails_closed(self) -> None:
        bge = [f"u{index}" for index in range(20)]
        with self.assertRaisesRegex(ValueError, "absent from BGE"):
            retrieval.place_protected(bge, ["u1"], 20)

    def test_eligibility_gate_is_stratified_and_deterministic(self) -> None:
        traces = []
        for dataset in common.DATASETS:
            traces.extend(
                [
                    trace(dataset, True, True),
                    trace(dataset, False),
                    trace(dataset, True),
                    trace(dataset, False),
                ]
            )
        first = retrieval.summarize_eligibility(traces, 0.25, 0.25)
        second = verifier.independent_eligibility(traces, 0.25, 0.25)
        self.assertEqual(first, second)
        self.assertTrue(first["gate"]["pass"])
        self.assertEqual(
            first["interpretation"],
            "BLIND_ONLY_FEASIBILITY_NOT_POWER_GUARANTEE",
        )

    def test_eligibility_gate_requires_every_dataset(self) -> None:
        traces = [
            trace(common.HOTPOT_DATASET, True),
            trace(common.HOTPOT_DATASET, True),
            trace(common.MUSIQUE_DATASET, False),
            trace(common.MUSIQUE_DATASET, False),
        ]
        result = retrieval.summarize_eligibility(traces, 0.10, 0.15)
        self.assertFalse(result["gate"]["pass"])
        self.assertEqual(
            result["gate"]["status"],
            "STAGE4I_SIDECAR_ACTIVATION_DEGENERATE",
        )

    def test_near_all_open_is_caution_not_retuning(self) -> None:
        traces = [
            trace(dataset, True, True)
            for dataset in common.DATASETS
            for _ in range(2)
        ]
        result = retrieval.summarize_eligibility(traces, 0.10, 0.15)
        self.assertTrue(result["gate"]["pass"])
        self.assertTrue(result["near_all_open_caution"])

    def test_four_arm_rankings_are_complete_unique_and_in_pool(self) -> None:
        blind, _, _ = stage4h_prepare.build_hotpot_channels(
            0, "hp-1", hotpot_row("hp-1")
        )
        units, queries = retrieval.build_units_queries([blind])
        rng = np.random.default_rng(17)
        minilm_unit = rng.normal(size=(len(units), 16)).astype("float32")
        minilm_query = rng.normal(size=(1, 16)).astype("float32")
        strong_unit = rng.normal(size=(len(units), 24)).astype("float32")
        strong_query = rng.normal(size=(1, 24)).astype("float32")
        for matrix in (minilm_unit, minilm_query, strong_unit, strong_query):
            matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)
        rankings, traces, _ = retrieval.build_rankings(
            units,
            queries,
            minilm_unit,
            minilm_query,
            strong_unit,
            strong_query,
        )
        self.assertEqual(set(rankings[0]["methods"]), set(common.METHODS))
        pool = {unit["unit_id"] for unit in units}
        for values in rankings[0]["methods"].values():
            self.assertEqual(len(values), 20)
            self.assertEqual(len(values), len(set(values)))
            self.assertLessEqual(set(values), pool)
        self.assertEqual(
            rankings[0]["full_inserted_unit_ids"],
            traces[0]["full_inserted_unit_ids"],
        )


class StatisticsAndMechanismTests(unittest.TestCase):
    def test_frozen_cache_validation_preserves_float32_bytes(self) -> None:
        matrix = np.asarray([[0.70710677, 0.70710677]], dtype="float32")
        rebuilt = verifier._validated_cache_matrix(matrix, 1, "synthetic")
        np.testing.assert_array_equal(rebuilt, matrix)
        self.assertFalse(
            np.array_equal(
                rebuilt,
                (matrix / np.linalg.norm(matrix, axis=1, keepdims=True)).astype(
                    "float32"
                ),
            )
        )

    def test_runner_exact_cache_helper_is_used_for_both_embedding_spaces(
        self,
    ) -> None:
        source = (SCRIPTS / "stage4i_sdc_goldfree_runner.py").read_text(
            encoding="utf-8"
        )
        self.assertEqual(source.count("build_or_load_exact_embeddings("), 3)
        self.assertIn("return raw_unit, raw_query, seconds", source)

    def test_core_decision_priority_and_all_states(self) -> None:
        cases = (
            (
                decision_summary(
                    pooled_f1=(-0.03, -0.01, -0.02),
                    dataset_points=(-0.02, 0.01),
                ),
                "STRONG_DENSE_COMPLEMENTARITY_NEGATIVE",
            ),
            (
                decision_summary(
                    pooled_f1=(-0.01, 0.02, 0.005),
                    dataset_points=(-0.01, 0.02),
                ),
                "STRONG_DENSE_COMPLEMENTARITY_CROSS_DATASET_HETEROGENEOUS",
            ),
            (
                decision_summary(
                    pooled_f1=(0.002, 0.03, 0.015),
                    pooled_em=(-0.005, 0.01, 0.0),
                ),
                "STRONG_DENSE_COMPLEMENTARITY_SUPPORTED",
            ),
            (
                decision_summary(
                    pooled_f1=(0.001, 0.009, 0.005),
                    pooled_em=(-0.005, 0.01, 0.0),
                ),
                "STRONG_DENSE_COMPLEMENTARITY_SUPPORTED_SMALL_EFFECT",
            ),
            (
                decision_summary(
                    pooled_f1=(-0.002, 0.01, 0.004),
                    pooled_em=(-0.005, 0.01, 0.0),
                ),
                "STRONG_DENSE_COMPLEMENTARITY_INCONCLUSIVE",
            ),
        )
        for summary, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(evaluator.core_decision(summary), expected)
                self.assertEqual(verifier._core_decision(summary), expected)

    def test_supportive_state_keeps_em_guard(self) -> None:
        supported = decision_summary(
            pooled_f1=(0.001, 0.02, 0.01),
            pooled_em=(-0.005, 0.01, 0.0),
        )
        negative = decision_summary(
            pooled_f1=(0.001, 0.02, 0.01),
            pooled_em=(-0.03, -0.02, -0.025),
        )
        self.assertEqual(
            evaluator.supportive_state(supported, "PLACEMENT"),
            "PLACEMENT_SUPPORTED",
        )
        self.assertEqual(
            evaluator.supportive_state(negative, "PLACEMENT"),
            "PLACEMENT_NEGATIVE",
        )

    def test_answer_and_evidence_audit_matches_independent_verifier(self) -> None:
        gold, queries, predictions, prompts, rankings = evaluation_fixture()
        evaluator_rows = evaluator.evaluate_queries(
            gold, predictions, prompts, rankings
        )
        verifier_rows = verifier.independent_query_audit(
            gold, queries, predictions, prompts, rankings
        )
        self.assertEqual(evaluator_rows, verifier_rows)
        transition = evaluator_rows[0]["transitions_relative_to_bge"][
            "BGE_HGRAG_PROTECTED_TOP20"
        ]
        self.assertEqual(transition["added_gold_evidence"], 1)
        self.assertEqual(transition["displaced_bge_gold_evidence"], 0)
        self.assertEqual(transition["net_gold_evidence_change"], 1)

    def test_bootstrap_and_all_summary_bytes_match_independent_implementation(
        self,
    ) -> None:
        gold, queries, predictions, prompts, rankings = evaluation_fixture()
        audits = verifier.independent_query_audit(
            gold, queries, predictions, prompts, rankings
        )
        telemetry = {
            "embedding_cache": {"minilm": {}, "strong_dense": {}},
            "generation_seconds_by_method": {
                method: 1.0 for method in common.METHODS
            },
            "gpu_peak_memory_bytes": 123,
            "retrieval_seconds": {"BGE_TOP20": 0.1},
        }
        with (
            patch.object(evaluator, "BOOTSTRAP_ITERATIONS", 100),
            patch.object(verifier, "BOOTSTRAP_ITERATIONS", 100),
        ):
            actual = evaluator.summarize(audits, telemetry)
            independent = verifier.independent_summaries(audits, telemetry)
        self.assertEqual(actual, independent)
        self.assertEqual(
            evaluator.evidence_transition_summary(audits),
            verifier.independent_evidence_summary(audits),
        )

    def test_strict_prompt_integer_rejects_bool_and_float(self) -> None:
        base = {
            "evidence_unit_ids": ["u1"],
            "input_token_count": 1,
            "prompt_sha256": "A" * 64,
            "rank1_truncated": False,
        }
        for invalid in (True, 1.0):
            row = dict(base, input_token_count=invalid)
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    verifier._prompt_projection(row)


class IndependenceAndFrozenContractTests(unittest.TestCase):
    def test_verifier_does_not_import_stage4i_runner_retrieval_or_evaluator(
        self,
    ) -> None:
        source = (SCRIPTS / "stage4i_sdc_independent_verifier.py").read_text(
            encoding="utf-8"
        )
        forbidden = (
            "from stage4i_sdc_retrieval",
            "from stage4i_sdc_goldfree_runner",
            "from stage4i_sdc_evaluate",
            "import stage4i_sdc_retrieval",
            "import stage4i_sdc_goldfree_runner",
            "import stage4i_sdc_evaluate",
        )
        self.assertFalse(any(value in source for value in forbidden))

    def test_q25_is_declared_sidecar_only_and_no_score_fusion_exists(self) -> None:
        config = common.load_json(ROOT / "configs" / "stage4i_sdc_official.json")
        self.assertEqual(
            config["retrieval"]["q25_role"],
            "SIDECAR_ELIGIBILITY_ONLY_NOT_BGE_SCORE",
        )
        source = (SCRIPTS / "stage4i_sdc_retrieval.py").read_text(encoding="utf-8")
        self.assertNotIn("score_fusion", source.lower())
        self.assertNotIn("bge_threshold", source.lower())

    def test_protocol_freezes_exact_four_arms_and_locks(self) -> None:
        config = common.load_json(ROOT / "configs" / "stage4i_sdc_official.json")
        self.assertEqual(tuple(config["methods"]), common.METHODS)
        self.assertEqual(config["locks"]["reservation"], "LOCKED")
        self.assertEqual(config["locks"]["stage3b"], "LOCKED")
        self.assertEqual(config["locks"]["u2"], "NOT_AUTHORIZED")
        self.assertEqual(config["locks"]["controller_branch"], "FROZEN_CLOSED")


if __name__ == "__main__":
    unittest.main()
