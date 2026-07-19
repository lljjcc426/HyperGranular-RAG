from __future__ import annotations

import copy
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


for name, value in {
    "PYTHONHASHSEED": "0",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "BLIS_NUM_THREADS": "1",
}.items():
    os.environ[name] = value

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import numpy as np

import stage4d_cma_candidate_trace as trace
import stage4d_cma_candidate_trace_verifier as trace_verifier
import stage4d_cma_learnability_probe as probe
from stage4b_u1_goldfree_retrieval import RetrievalConfig
from stage4d_cma_candidate_trace_verifier import verify_channel_a_traces
from stage4d_cma_independent_verifier import (
    verify_candidate_labels,
    verify_probe_outputs,
)
from stage4d_cma_marginal_labeler import (
    PRIMARY_LABELS,
    frozen_gold_targets,
    label_candidates,
    run_official_channel_b,
)


def _rank(dense: list[str], inserted: list[str], protect_n: int, k: int) -> list[str]:
    result = list(dense[:protect_n])
    seen = set(result)
    for unit_id in inserted:
        if unit_id not in seen and len(result) < k:
            result.append(unit_id)
            seen.add(unit_id)
    for unit_id in dense:
        if len(result) >= k:
            break
        if unit_id not in seen:
            result.append(unit_id)
            seen.add(unit_id)
    return result


def _manual_query(
    sample: str,
    dense: list[str],
    eligible: list[str],
    budget: int,
    *,
    protect_n: int = 1,
) -> tuple[dict, list[dict]]:
    query_id = f"toy::{sample}"
    k = len(dense)
    inserted = eligible[: min(budget, len(eligible))]
    query = {
        "candidate_count": len(eligible),
        "dataset": "toy",
        "dense_topk_unit_ids": dense,
        "effective_k": k,
        "eligible_candidate_unit_ids": eligible,
        "original_u1_score": 0.25,
        "planned_insert_budget": budget,
        "protect_n": protect_n,
        "q25_inserted_unit_ids": inserted,
        "q25_topk_unit_ids": _rank(dense, inserted, protect_n, k),
        "query_id": query_id,
        "sample_id": sample,
    }
    rows = []
    for rank_index, unit_id in enumerate(eligible, start=1):
        standardized = _rank(dense, [unit_id], protect_n, k)
        displaced = list(set(dense) - set(standardized))
        rows.append(
            {
                "candidate_budget_region": (
                    "ORIGINAL_INSERT_SET" if rank_index <= len(inserted) else "BEYOND_ORIGINAL_BUDGET"
                ),
                "candidate_rank_in_eligible_slice": rank_index,
                "candidate_unit_id": unit_id,
                "dataset": "toy",
                "displaced_unit_id": displaced[0] if displaced else None,
                "is_in_original_q25_insert_set": int(rank_index <= len(inserted)),
                "query_id": query_id,
                "sample_id": sample,
            }
        )
    return query, rows


class ProtocolAndEnvironmentTests(unittest.TestCase):
    def test_level_a_protocol_promoted_and_corrected(self) -> None:
        accepted = ROOT / "docs" / "STAGE4D_CANDIDATE_MARGINAL_UTILITY_AUDIT_PROTOCOL.md"
        draft = ROOT / "docs" / "STAGE4D_CANDIDATE_MARGINAL_UTILITY_AUDIT_PROTOCOL_DRAFT.md"
        text = accepted.read_text(encoding="utf-8")
        self.assertTrue(accepted.is_file())
        self.assertFalse(draft.exists())
        for token in (
            "STAGE4D_IMPLEMENTATION_READY",
            "STAGE4D_SYNTHETIC_TESTS_PASSED",
            "candidate_budget_region",
            "BEYOND_ORIGINAL_BUDGET",
            "delta_standardized_single_cr",
            "LOO_NO_BACKFILL",
            "LOO_WITH_BACKFILL",
            "EVIDENCE_GAIN_ONLY",
            "EVIDENCE_HARM_ONLY",
            "COMBINED_DEPLOYABLE_28",
            "minimum feasibility threshold, not a power guarantee",
            "scikit-learn == 1.9.0",
        ):
            self.assertIn(token, text)

    def test_exact_runtime_binding(self) -> None:
        runtime = probe.validate_runtime_environment()
        self.assertEqual(runtime["python"], "3.12.0")
        self.assertEqual(runtime["packages"], probe.EXPECTED_VERSIONS)
        requirements = (ROOT / "requirements-stage4d.txt").read_text(encoding="utf-8")
        for package, version in probe.EXPECTED_VERSIONS.items():
            self.assertIn(f"{package}=={version}", requirements)

    def test_official_entry_points_fail_before_input_open(self) -> None:
        missing = ROOT / "definitely_absent_official_input.json"
        with mock.patch.dict(os.environ, {trace.CHANNEL_A_AUTH_ENV: ""}, clear=False):
            with self.assertRaisesRegex(PermissionError, "no input was opened"):
                trace.run_official_channel_a(missing, ROOT / "results")
        with mock.patch.dict(
            os.environ,
            {"STAGE4D_CHANNEL_B_EXECUTION_AUTHORIZED": ""},
            clear=False,
        ):
            with self.assertRaisesRegex(PermissionError, "no input was opened"):
                run_official_channel_b(
                    missing, missing, missing, missing, missing, missing
                )
        with mock.patch.dict(os.environ, {probe.PROBE_AUTH_ENV: ""}, clear=False):
            with self.assertRaisesRegex(PermissionError, "no input was opened"):
                probe.require_official_probe_authorization()


class ChannelATraceTests(unittest.TestCase):
    def _inputs(self):
        query = {
            "dataset": "toy",
            "num_candidate_units": 6,
            "query_id": "toy::1",
            "question": "alpha bridge target",
            "sample_id": "1",
        }
        units = [
            {
                "query_id": "toy::1",
                "text": f"alpha bridge evidence {index}",
                "title": f"unit {index}",
                "unit_id": f"u{index}",
            }
            for index in range(1, 7)
        ]
        embeddings = np.asarray(
            [[1.0, 0.0], [0.99, 0.05], [0.96, 0.10], [0.92, 0.16], [0.86, 0.22], [0.80, 0.28]],
            dtype=np.float32,
        )
        query_embeddings = np.asarray([[1.0, 0.0]], dtype=np.float32)

        def balls(*_args):
            return [
                {
                    "ball_id": "ball-1",
                    "boundary_count": 2,
                    "center": np.asarray([1.0, 0.0], dtype=np.float32),
                    "compactness": 0.75,
                    "indices": list(range(6)),
                    "radius": 0.2,
                    "size": 6,
                }
            ]

        edge = {
            "accepted_ball_ids": ["ball-1"],
            "ball_score": 0.8,
            "diversity": 0.4,
            "edge_id": "edge-1",
            "facet_score": 0.7,
            "facet_terms": ["alpha", "bridge"],
            "new_terms": ["bridge"],
            "redundancy": 0.1,
            "shared_terms": ["alpha"],
            "units_per_new_term": 6.0,
        }
        config = RetrievalConfig(max_k=4, protect_n=1, insert_budget=2)
        return query, units, embeddings, query_embeddings, balls, edge, config

    def _build(self):
        query, units, embeddings, query_embeddings, balls, edge, config = self._inputs()
        with mock.patch.object(trace, "build_balls", side_effect=balls), mock.patch.object(
            trace, "enrich_balls_goldfree", return_value=None
        ), mock.patch.object(trace, "select_facet_edges_goldfree", return_value=([edge], {})):
            return trace.build_channel_a_traces(
                units,
                [query],
                embeddings,
                query_embeddings,
                config,
                u1_scores={"toy::1": 0.2},
            )

    def test_complete_candidate_pool_budget_regions_and_determinism(self) -> None:
        first = self._build()
        second = self._build()
        self.assertEqual(trace.render_jsonl(first[0]), trace.render_jsonl(second[0]))
        self.assertEqual(trace.render_jsonl(first[1]), trace.render_jsonl(second[1]))
        query_rows, candidate_rows, manifest = first
        verification = verify_channel_a_traces(query_rows, candidate_rows, manifest)
        self.assertEqual(query_rows[0]["candidate_count"], 5)
        self.assertEqual(verification["original_insert_set_rows"], 2)
        self.assertEqual(verification["beyond_original_budget_rows"], 3)
        self.assertEqual(
            [row["candidate_budget_region"] for row in candidate_rows],
            ["ORIGINAL_INSERT_SET", "ORIGINAL_INSERT_SET"]
            + ["BEYOND_ORIGINAL_BUDGET"] * 3,
        )
        query, units, embeddings, query_embeddings, balls, edge, config = self._inputs()
        with mock.patch.object(
            trace_verifier, "build_balls", side_effect=balls
        ), mock.patch.object(
            trace_verifier, "enrich_balls_goldfree", return_value=None
        ), mock.patch.object(
            trace_verifier,
            "select_facet_edges_goldfree",
            return_value=([edge], {}),
        ):
            independent = trace_verifier.verify_channel_a_reconstruction(
                units,
                [query],
                embeddings,
                query_embeddings,
                config,
                query_rows,
                candidate_rows,
                manifest,
            )
        self.assertEqual(
            independent["status"], "CHANNEL_A_INDEPENDENT_RECONSTRUCTION_VERIFIED"
        )

    def test_strict_schema_types_identity_and_leakage(self) -> None:
        query_rows, candidate_rows, manifest = self._build()
        cases = []
        wrong_dataset = copy.deepcopy(candidate_rows)
        wrong_dataset[0]["dataset"] = "wrong"
        cases.append(wrong_dataset)
        bool_rank = copy.deepcopy(candidate_rows)
        bool_rank[0]["candidate_rank_in_eligible_slice"] = True
        cases.append(bool_rank)
        leaked = copy.deepcopy(candidate_rows)
        leaked[0]["candidate_is_gold"] = 1
        cases.append(leaked)
        numeric_id = copy.deepcopy(candidate_rows)
        numeric_id[0]["candidate_unit_id"] = 12
        cases.append(numeric_id)
        for rows in cases:
            with self.subTest(case=rows[0]):
                with self.assertRaises(ValueError):
                    verify_channel_a_traces(query_rows, rows, manifest)

    def test_atomic_promotion_is_no_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            trace._atomic_promote(target, {"synthetic.json": b"one\n"})
            with self.assertRaises(FileExistsError):
                trace._atomic_promote(target, {"synthetic.json": b"two\n"})
            self.assertEqual((target / "synthetic.json").read_bytes(), b"one\n")


class CounterfactualLabelTests(unittest.TestCase):
    def _fixture(self):
        specifications = [
            ("gain", ["p", "a", "b", "n"], ["g"], 1, {"g"}),
            ("harm", ["p", "a", "b", "g"], ["x"], 1, {"g"}),
            ("er_gain", ["p", "g1", "a", "n"], ["g2"], 1, {"g1", "g2", "g3"}),
            ("er_harm", ["p", "g1", "a", "g2"], ["x"], 1, {"g1", "g2", "g3"}),
            (
                "interaction",
                ["p", "g2", "n", "g1"],
                ["x", "c", "y"],
                2,
                {"g1", "g2", "c", "y"},
            ),
            ("redundant", ["p", "g", "a", "n"], ["g"], 0, {"g"}),
            ("neutral", ["p", "a", "x", "n"], ["x"], 0, {"p"}),
        ]
        queries = []
        candidates = []
        gold = {}
        for sample, dense, eligible, budget, gold_set in specifications:
            query, rows = _manual_query(sample, dense, eligible, budget)
            queries.append(query)
            candidates.extend(rows)
            gold[query["query_id"]] = gold_set
        return queries, candidates, gold

    def test_all_seven_labels_and_dual_loo(self) -> None:
        queries, candidates, gold = self._fixture()
        labels, summary = label_candidates(queries, candidates, gold)
        observed = {row["marginal_label"] for row in labels}
        self.assertEqual(observed, set(PRIMARY_LABELS))
        interaction = next(
            row
            for row in labels
            if row["query_id"] == "toy::interaction" and row["candidate_unit_id"] == "c"
        )
        self.assertEqual(interaction["marginal_label"], "INTERACTION_DEPENDENT")
        self.assertGreater(interaction["delta_loo_no_backfill_er"], 0.0)
        self.assertEqual(interaction["delta_loo_with_backfill_er"], 0.0)
        self.assertEqual(
            interaction["replacement_subtype"], "REPLACEMENT_EQUIVALENT_TO_NEXT"
        )
        self.assertEqual(summary["candidate_rows"], len(labels))
        verified = verify_candidate_labels(queries, candidates, labels, gold)
        self.assertEqual(verified["status"], "CHANNEL_B_LABELS_VERIFIED")

    def test_beyond_budget_loo_is_null_and_tamper_is_rejected(self) -> None:
        queries, candidates, gold = self._fixture()
        labels, _ = label_candidates(queries, candidates, gold)
        beyond = next(
            row
            for row in labels
            if row["query_id"] == "toy::interaction" and row["candidate_unit_id"] == "y"
        )
        self.assertIsNone(beyond["delta_loo_no_backfill_cr"])
        self.assertIsNone(beyond["delta_loo_with_backfill_er"])
        tampered = copy.deepcopy(labels)
        tampered[0]["delta_standardized_single_cr"] = 99
        with self.assertRaises(ValueError):
            verify_candidate_labels(queries, candidates, tampered, gold)

    def test_frozen_gold_schema_drops_question_type(self) -> None:
        query_ids = ["toy::a", "toy::b"]
        import hashlib

        digest = hashlib.sha256(("\n".join(sorted(query_ids)) + "\n").encode()).hexdigest().upper()
        gold_map = {
            "queries": [
                {"gold_unit_ids": ["g1"], "query_id": "toy::a", "question_type": "bridge"},
                {"gold_unit_ids": ["g2"], "query_id": "toy::b", "question_type": "comparison"},
            ],
            "query_id_sha256": digest,
            "schema_version": "stage4b_u1_v2",
        }
        targets = frozen_gold_targets(gold_map, query_ids)
        self.assertEqual(targets, {"toy::a": ["g1"], "toy::b": ["g2"]})
        self.assertNotIn("question_type", str(targets))


def _probe_fixture(query_count: int = 40):
    candidates = []
    labels = []
    queries = []
    feature_names = probe.PANELS["COMBINED_DEPLOYABLE_28"]
    classes = (
        ("gain", "MARGINAL_GAIN", 1.0),
        ("harm", "DISPLACEMENT_HARM", -1.0),
        ("evidence", "EVIDENCE_GAIN_ONLY", 0.1),
    )
    for query_index in range(query_count):
        query_id = f"synthetic::{query_index:03d}"
        queries.append({"original_u1_score": query_index / query_count, "query_id": query_id})
        for class_index, (suffix, label, signal) in enumerate(classes):
            unit_id = f"{query_id}:{suffix}"
            region = "ORIGINAL_INSERT_SET" if class_index != 1 else "BEYOND_ORIGINAL_BUDGET"
            row = {
                "candidate_budget_region": region,
                "candidate_rank_in_eligible_slice": class_index + 1,
                "candidate_unit_id": unit_id,
                "dataset": "synthetic",
                "query_id": query_id,
                "sample_id": f"{query_index:03d}",
            }
            for feature_index, feature in enumerate(feature_names):
                row[feature] = float(
                    signal * (1.0 + feature_index / 100.0)
                    + query_index / 10_000.0
                )
            candidates.append(row)
            labels.append(
                {
                    "candidate_budget_region": region,
                    "candidate_unit_id": unit_id,
                    "dataset": "synthetic",
                    "marginal_label": label,
                    "query_id": query_id,
                    "sample_id": f"{query_index:03d}",
                }
            )
    return candidates, labels, queries


class LearnabilityProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidates, cls.labels, cls.queries = _probe_fixture()
        cls.first = probe.run_synthetic_probe(
            cls.candidates,
            cls.labels,
            cls.queries,
            bootstrap_iterations=20,
            minimum_clusters=1,
            minimum_per_fold=1,
        )

    def test_group_folds_reused_and_task_c_excludes_er_only(self) -> None:
        assignments = self.first["fold_assignments"]
        self.assertEqual(set(assignments.values()), set(range(5)))
        task_c = [
            row
            for row in self.first["oof_predictions"]
            if row["task"] == "TASK_C_GAIN_VS_HARM"
        ]
        self.assertEqual(len(task_c), 40 * 2 * 4)
        evidence_ids = {
            row["candidate_unit_id"]
            for row in self.labels
            if row["marginal_label"] == "EVIDENCE_GAIN_ONLY"
        }
        self.assertFalse(evidence_ids & {row["candidate_unit_id"] for row in task_c})
        for row in self.first["oof_predictions"]:
            self.assertEqual(row["fold"], assignments[row["query_id"]])

    def test_all_panels_same_oof_predictions_stratified_and_verified(self) -> None:
        for task in probe.TASKS:
            result = self.first["results"][task]
            self.assertTrue(result["feasibility"]["eligible"])
            self.assertEqual(set(result["panels"]), set(probe.PANELS))
            for panel_result in result["panels"].values():
                self.assertIn("ORIGINAL_INSERT_SET", panel_result["candidate_budget_regions"])
                self.assertIn("BEYOND_ORIGINAL_BUDGET", panel_result["candidate_budget_regions"])
        verified = verify_probe_outputs(self.candidates, self.labels, self.first)
        self.assertEqual(verified["status"], "STAGE4D_PROBE_VERIFIED")

    def test_byte_identical_synthetic_rerun(self) -> None:
        second = probe.run_synthetic_probe(
            self.candidates,
            self.labels,
            self.queries,
            bootstrap_iterations=20,
            minimum_clusters=1,
            minimum_per_fold=1,
        )
        self.assertEqual(trace.render_json(self.first), trace.render_json(second))

    def test_task_c_minimum_is_feasibility_not_power_claim(self) -> None:
        text = self.first["results"]["TASK_C_GAIN_VS_HARM"]["feasibility"][
            "threshold_interpretation"
        ]
        self.assertEqual(text, "minimum feasibility threshold, not a power guarantee")

    def test_probe_tamper_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.first)
        tampered["oof_predictions"][0]["fold"] = (
            tampered["oof_predictions"][0]["fold"] + 1
        ) % 5
        with self.assertRaises(ValueError):
            verify_probe_outputs(self.candidates, self.labels, tampered)

    def test_only_combined_panel_can_trigger_advancement(self) -> None:
        accepted = probe.assign_scientific_decision(
            self.first,
            integrity_passed=True,
            feature_reproducible=True,
            attribution_integrity_passed=True,
            q25_gain_queries=94,
            q25_harm_queries=69,
        )
        self.assertEqual(
            accepted["decision"], "PROCEED_TO_STAGE5A_U2_PROTOCOL_DESIGN"
        )
        combined_failed = copy.deepcopy(self.first)
        combined = combined_failed["results"]["TASK_C_GAIN_VS_HARM"]["panels"][
            "COMBINED_DEPLOYABLE_28"
        ]
        combined["auroc"] = 0.60
        combined["bootstrap"]["auroc"] = {
            "lower": 0.45,
            "samples": 20,
            "upper": 0.75,
        }
        rejected = probe.assign_scientific_decision(
            combined_failed,
            integrity_passed=True,
            feature_reproducible=True,
            attribution_integrity_passed=True,
            q25_gain_queries=94,
            q25_harm_queries=69,
        )
        self.assertNotEqual(
            rejected["decision"], "PROCEED_TO_STAGE5A_U2_PROTOCOL_DESIGN"
        )


if __name__ == "__main__":
    unittest.main()
