from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import stage4h_cbe_prepare as stage4h_prepare
import stage5a_bnh_common as common
import stage5a_bnh_evaluate as evaluator
import stage5a_bnh_goldfree_runner as runner
import stage5a_bnh_independent_retrieval as independent
import stage5a_bnh_prepare as prepare
import stage5a_bnh_retrieval as retrieval


def hotpot_row(native_id: str) -> dict:
    return {
        "_id": native_id,
        "answer": "Alpha",
        "context": [
            [
                f"Title {paragraph}",
                [
                    f"Alpha evidence sentence {paragraph}.",
                    f"Gamma relation sentence {paragraph}.",
                    f"Delta context sentence {paragraph}.",
                ],
            ]
            for paragraph in range(10)
        ],
        "level": "medium",
        "question": f"Which alpha gamma relation belongs to {native_id}?",
        "supporting_facts": [["Title 0", 0], ["Title 1", 1]],
        "type": "bridge",
    }


def configs() -> list[dict]:
    rows: list[dict] = []
    index = 1
    for leaf_size in (4, 6):
        for gate in ("BROAD", "STRICT"):
            for percentile in (0.50, 0.75):
                for budget in (2, 4):
                    rows.append(
                        {
                            "config_id": f"C{index:02d}",
                            "facet_gate": gate,
                            "insert_budget": budget,
                            "leaf_size": leaf_size,
                            "unit_score_percentile": percentile,
                        }
                    )
                    index += 1
    return rows


def normalized_random(rows: int, columns: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    matrix = rng.normal(size=(rows, columns)).astype("float32")
    matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix


class InputAndContractTests(unittest.TestCase):
    def test_boundary_selection_is_id_only_deterministic_and_excludes_history(
        self,
    ) -> None:
        rows = [hotpot_row(f"hp-{index}") for index in range(40)]
        first = prepare.select_rows(
            rows,
            common.HOTPOT_DATASET,
            {"hp-0", "hp-3"},
            10,
            "development",
        )
        second = prepare.select_rows(
            rows,
            common.HOTPOT_DATASET,
            {"hp-0", "hp-3"},
            10,
            "development",
        )
        confirmation = prepare.select_rows(
            rows,
            common.HOTPOT_DATASET,
            {"hp-0", "hp-3"} | {row[1] for row in first},
            10,
            "confirmation",
        )
        self.assertEqual([row[1] for row in first], [row[1] for row in second])
        self.assertFalse({row[1] for row in first} & {row[1] for row in confirmation})
        self.assertFalse({"hp-0", "hp-3"} & {row[1] for row in first + confirmation})

    def test_frozen_candidate_family_is_complete_and_bounded(self) -> None:
        values = common.validate_candidate_configs({"candidate_configs": configs()})
        self.assertEqual(len(values), 16)
        self.assertEqual(values[0]["config_id"], "C01")
        self.assertEqual(values[-1]["config_id"], "C16")
        with self.assertRaisesRegex(ValueError, "1..16"):
            common.validate_candidate_configs(
                {"candidate_configs": values + [{**values[-1], "config_id": "C17"}]}
            )


class RetrievalTests(unittest.TestCase):
    def setUp(self) -> None:
        blind, _, _ = stage4h_prepare.build_hotpot_channels(
            0, "hp-synthetic", hotpot_row("hp-synthetic")
        )
        self.units, self.queries = retrieval.build_units_queries([blind])
        self.unit_embeddings = normalized_random(len(self.units), 24, 71)
        self.query_embeddings = normalized_random(1, 24, 72)
        self.config = {"candidate_configs": configs()}

    def test_adaptive_balls_partition_pool_and_are_deterministic(self) -> None:
        indices = list(range(len(self.units)))
        first, first_trace = retrieval.build_bge_native_balls(
            self.queries[0],
            indices,
            self.units,
            self.unit_embeddings,
            4,
        )
        second, second_trace = retrieval.build_bge_native_balls(
            self.queries[0],
            indices,
            self.units,
            self.unit_embeddings,
            4,
        )
        self.assertEqual(
            [[unit for unit in row["indices"]] for row in first],
            [[unit for unit in row["indices"]] for row in second],
        )
        self.assertEqual(first_trace, second_trace)
        self.assertEqual(
            sorted(index for row in first for index in row["indices"]),
            indices,
        )

    def test_independent_development_reconstruction_is_byte_identical(self) -> None:
        rankings, traces, _ = retrieval.build_development_rankings(
            self.units,
            self.queries,
            self.unit_embeddings,
            self.query_embeddings,
            self.config,
        )
        independent_rankings, independent_traces = (
            independent.independent_development_rankings(
                self.units,
                self.queries,
                self.unit_embeddings,
                self.query_embeddings,
                self.config,
            )
        )
        self.assertEqual(
            common.render_jsonl(rankings),
            common.render_jsonl(independent_rankings),
        )
        self.assertEqual(
            common.render_jsonl(traces),
            common.render_jsonl(independent_traces),
        )
        self.assertEqual(len(rankings[0]["methods"]), 17)

    def test_confirmation_arms_share_inserted_set_for_placement(self) -> None:
        selected = configs()[0]
        rankings, traces, _ = retrieval.build_confirmation_rankings(
            self.units,
            self.queries,
            self.unit_embeddings,
            self.query_embeddings,
            selected,
        )
        independent_rankings, independent_traces = (
            independent.independent_confirmation_rankings(
                self.units,
                self.queries,
                self.unit_embeddings,
                self.query_embeddings,
                selected,
            )
        )
        self.assertEqual(rankings, independent_rankings)
        self.assertEqual(traces, independent_traces)
        row = rankings[0]
        self.assertEqual(set(row["methods"]), set(common.CONFIRMATION_METHODS))
        protected = row["methods"]["BGE_NATIVE_HGRAG_PROTECTED_TOP20"]
        unprotected = row["methods"]["BGE_NATIVE_HGRAG_UNPROTECTED_TOP20"]
        baseline = row["methods"][common.BASELINE_METHOD]
        inserted = row["inserted_unit_ids"]
        self.assertEqual(set(protected), set(unprotected))
        self.assertEqual(set(protected) - set(baseline), set(inserted))
        self.assertEqual(protected[10 : 10 + len(inserted)], inserted)
        self.assertEqual(unprotected[: len(inserted)], inserted)

    def test_geometry_gate_is_blind_and_stratified(self) -> None:
        trace_rows = []
        for dataset in common.DATASETS:
            for query_index in range(10):
                trace_rows.append(
                    {
                        "configs": {
                            row["config_id"]: {
                                "facet": {"eligible_ball_count": 2},
                                "inserted_unit_ids": (
                                    ["u1"] if query_index < 5 else []
                                ),
                            }
                            for row in configs()
                        },
                        "dataset": dataset,
                        "query_id": f"{dataset}::{query_index}",
                        "sample_id": str(query_index),
                    }
                )
        summary = retrieval.summarize_geometry_feasibility(
            trace_rows, configs()
        )
        self.assertTrue(summary["gate"]["pass"])
        self.assertEqual(
            summary["interpretation"],
            "BLIND_ONLY_FEASIBILITY_NOT_ANSWER_QUALITY_OR_POWER_GUARANTEE",
        )


class SelectionAndDecisionTests(unittest.TestCase):
    def test_development_near_tie_prefers_lower_cost_then_simpler(self) -> None:
        candidate_configs = configs()[:2]
        methods = [
            common.BASELINE_METHOD,
            *(common.development_method(row["config_id"]) for row in candidate_configs),
        ]
        audits = []
        for dataset in common.DATASETS:
            method_values = {
                methods[0]: {
                    "answer_em": 0.5,
                    "answer_f1": 0.5,
                    "evidence_count": 20,
                    "input_token_count": 100,
                    "unknown": 0.0,
                },
                methods[1]: {
                    "answer_em": 0.51,
                    "answer_f1": 0.510,
                    "evidence_count": 20,
                    "input_token_count": 105,
                    "unknown": 0.0,
                },
                methods[2]: {
                    "answer_em": 0.51,
                    "answer_f1": 0.511,
                    "evidence_count": 20,
                    "input_token_count": 110,
                    "unknown": 0.0,
                },
            }
            audits.append(
                {
                    "dataset": dataset,
                    "methods": method_values,
                    "query_id": f"{dataset}::q",
                    "sample_id": "q",
                }
            )
        geometry = {
            "config_summaries": {
                row["config_id"]: {"feasible": True} for row in candidate_configs
            }
        }
        _, selected = evaluator.development_summary_and_selection(
            audits, candidate_configs, geometry
        )
        self.assertEqual(selected["selected_config"]["config_id"], "C01")

    def test_core_decision_priority(self) -> None:
        def summary(
            f1: tuple[float, float, float],
            em: tuple[float, float, float] = (0.0, 0.0, 0.0),
            points: tuple[float, float] = (0.02, 0.02),
            uppers: tuple[float, float] = (0.03, 0.03),
        ) -> dict:
            return {
                "dataset_equal_weight": {
                    "delta_answer_f1": {
                        "ci95_lower": f1[0],
                        "ci95_upper": f1[1],
                        "point": f1[2],
                    },
                    "delta_answer_em": {
                        "ci95_lower": em[0],
                        "ci95_upper": em[1],
                        "point": em[2],
                    },
                },
                "datasets": {
                    dataset: {
                        "delta_answer_f1": {
                            "ci95_lower": -0.01,
                            "ci95_upper": uppers[index],
                            "point": points[index],
                        }
                    }
                    for index, dataset in enumerate(common.DATASETS)
                },
            }

        self.assertEqual(
            evaluator.core_decision(summary((-0.03, -0.01, -0.02))),
            "BGE_NATIVE_HGRAG_NEGATIVE",
        )
        self.assertEqual(
            evaluator.core_decision(
                summary((-0.01, 0.02, 0.005), points=(-0.01, 0.02))
            ),
            "BGE_NATIVE_HGRAG_CROSS_DATASET_HETEROGENEOUS",
        )
        self.assertEqual(
            evaluator.core_decision(
                summary((0.002, 0.03, 0.015), em=(-0.005, 0.01, 0.0))
            ),
            "BGE_NATIVE_HGRAG_SUPPORTED",
        )
        self.assertEqual(
            evaluator.core_decision(
                summary((0.001, 0.009, 0.005), em=(-0.005, 0.01, 0.0))
            ),
            "BGE_NATIVE_HGRAG_SUPPORTED_SMALL_EFFECT",
        )
        self.assertEqual(
            evaluator.core_decision(summary((-0.002, 0.01, 0.004))),
            "BGE_NATIVE_HGRAG_INCONCLUSIVE",
        )

    def test_checkpoint_must_be_exact_task_plan_prefix(self) -> None:
        tasks = [("q1", "m1"), ("q1", "m2")]
        bad = {
            "audit": {
                "dataset": "d",
                "method": "m2",
                "query_id": "q1",
                "sample_id": "s",
            },
            "prediction": {
                "dataset": "d",
                "method": "m2",
                "prediction": "x",
                "query_id": "q1",
                "sample_id": "s",
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.jsonl"
            path.write_text(json.dumps(bad) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "legal plan prefix"):
                runner._load_prefix_checkpoint(path, tasks)


if __name__ == "__main__":
    unittest.main()
