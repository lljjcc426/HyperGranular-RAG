from __future__ import annotations

import ast
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import stage4f_xdr_common as common
import stage4f_xdr_evaluate as evaluator
import stage4f_xdr_independent_verifier as verifier
import stage4f_xdr_prepare as prepare
import stage4f_xdr_retrieval as retrieval
import stage4f_xdr_retrieve_generate as runner


def source_row(native_id: str = "2hop__1_2") -> dict:
    paragraphs = []
    for index in range(20):
        paragraphs.append(
            {
                "idx": index,
                "is_supporting": index in {0, 1},
                "paragraph_text": f"Alpha sentence {index}. Beta sentence {index}.",
                "title": f"Title {index}",
            }
        )
    return {
        "answer": "Alpha",
        "answer_aliases": ["The Alpha"],
        "answerable": True,
        "id": native_id,
        "paragraphs": paragraphs,
        "question": f"Question {native_id}?",
        "question_decomposition": [
            {"answer": "x", "id": 1, "paragraph_support_idx": 0, "question": "step1"},
            {"answer": "Alpha", "id": 2, "paragraph_support_idx": 1, "question": "step2"},
        ],
    }


def frozen_blind(native_id: str = "2hop__1_2") -> dict:
    blind, _, _ = prepare.build_channels_for_row(0, source_row(native_id))
    return blind


class FakeTokenizer:
    def apply_chat_template(self, messages, *, tokenize, add_generation_prompt):
        text = "|".join(row["content"] for row in messages) + "|assistant:"
        if not tokenize:
            return text
        values = list(text.encode("utf-8"))
        return {"input_ids": values, "attention_mask": [1] * len(values)}

    def encode(self, text, *, add_special_tokens):
        return list(text.encode("utf-8"))

    def decode(self, values, **kwargs):
        return bytes(values).decode("utf-8", errors="ignore")


class SelectionAndChannelTests(unittest.TestCase):
    def test_01_deterministic_id_selection(self) -> None:
        rows = [source_row("2hop__1_2"), source_row("2hop__3_4"), source_row("2hop__5_6")]
        first = prepare.select_rows(rows, set(), 2)
        second = prepare.select_rows(rows, set(), 2)
        self.assertEqual([row[1]["id"] for row in first], [row[1]["id"] for row in second])

    def test_02_historical_overlap_rejected(self) -> None:
        rows = [source_row("2hop__1_2"), source_row("2hop__3_4")]
        selected = prepare.select_rows(rows, set(), 1)[0][1]["id"]
        with self.assertRaisesRegex(ValueError, "overlap historical"):
            prepare.select_rows(rows, {selected}, 1)

    def test_03_gold_is_stripped_from_blind_channel(self) -> None:
        blind, gold, metadata = prepare.build_channels_for_row(0, source_row())
        common.assert_no_gold_fields(blind, "blind")
        self.assertIn("answers", gold)
        self.assertIn("hop_count", metadata)
        self.assertNotIn("answer", json.dumps(blind))

    def test_04_ambiguous_support_mapping_fails_closed(self) -> None:
        row = source_row()
        row["question_decomposition"] = row["question_decomposition"][:1]
        with self.assertRaisesRegex(ValueError, "mapping is ambiguous"):
            prepare.build_channels_for_row(0, row)

    def test_05_empty_candidate_pool_fails_closed(self) -> None:
        blind = frozen_blind()
        blind["candidate_units"] = []
        with self.assertRaisesRegex(ValueError, "non-empty"):
            runner.build_units_queries([blind])


class RetrievalContractTests(unittest.TestCase):
    def test_06_dense_tie_break_is_deterministic(self) -> None:
        units = [{"unit_id": "b"}, {"unit_id": "a"}]
        embeddings = np.asarray([[1.0, 0.0], [1.0, 0.0]], dtype="float32")
        ranked = retrieval.fixed_retrieve_goldfree(
            np.asarray([1.0, 0.0], dtype="float32"), [0, 1], units, embeddings, 20
        )
        self.assertEqual([row["unit_id"] for row in ranked], ["a", "b"])

    def test_07_q25_preserves_protected_prefix(self) -> None:
        dense = [{"unit_id": f"u{index:02d}", "score": 1 - index / 100} for index in range(20)]
        expanded = [{"unit_id": "extra", "score": 0.5, "rerank_score": 0.5}]
        ranked, inserted = retrieval.protected_rerank_goldfree(dense, expanded, 10, 4, 20)
        self.assertEqual([row["unit_id"] for row in ranked[:10]], [row["unit_id"] for row in dense[:10]])
        self.assertEqual(inserted, ["extra"])

    def test_08_q25_insertion_budget_is_bounded(self) -> None:
        dense = [{"unit_id": f"u{index:02d}", "score": 1 - index / 100} for index in range(20)]
        expanded = [{"unit_id": f"x{index}", "score": .5, "rerank_score": .5} for index in range(10)]
        _, inserted = retrieval.protected_rerank_goldfree(dense, expanded, 10, 4, 20)
        self.assertEqual(len(inserted), 4)

    def test_09_production_has_no_u1_or_controller_import(self) -> None:
        for filename in ("stage4f_xdr_retrieval.py", "stage4f_xdr_retrieve_generate.py"):
            tree = ast.parse((SCRIPTS / filename).read_text(encoding="utf-8"))
            imported = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imported.append(node.module or "")
            joined = " ".join(imported).lower()
            for prohibited in ("stage4b", "stage4d", "u1", "controller"):
                self.assertNotIn(prohibited, joined)


class PromptAndGenerationTests(unittest.TestCase):
    def test_10_prompt_evidence_is_frozen_ranking_prefix(self) -> None:
        units = [
            {"title": "A", "text": "first", "unit_id": "u1"},
            {"title": "B", "text": "second", "unit_id": "u2"},
        ]
        prompt = runner.build_prompt(FakeTokenizer(), "Question?", units, 1000)
        self.assertEqual(prompt["evidence_unit_ids"], ["u1", "u2"])

    def test_11_token_cap_is_deterministic(self) -> None:
        units = [{"title": "A", "text": "x" * 500, "unit_id": "u1"}]
        first = runner.build_prompt(FakeTokenizer(), "Question?", units, 260)
        second = runner.build_prompt(FakeTokenizer(), "Question?", units, 260)
        self.assertEqual(first, second)
        self.assertLessEqual(first["input_token_count"], 260)

    def test_12_rank1_truncation_contract(self) -> None:
        units = [
            {"title": "A", "text": "x" * 500, "unit_id": "u1"},
            {"title": "B", "text": "short", "unit_id": "u2"},
        ]
        prompt = runner.build_prompt(FakeTokenizer(), "Question?", units, 260)
        self.assertTrue(prompt["rank1_truncated"])
        self.assertEqual(prompt["evidence_unit_ids"], ["u1"])

    def test_13_generator_kwargs_are_fixed(self) -> None:
        self.assertEqual(
            runner.GENERATOR_KWARGS,
            {"do_sample": False, "max_new_tokens": 32, "num_beams": 1, "use_cache": True},
        )

    def test_14_main_rerun_payloads_are_byte_identical(self) -> None:
        rows = [
            {"dataset": common.DATASET, "method": method, "prediction": "x", "query_id": "q", "sample_id": "s"}
            for method in runner.METHODS
        ]
        self.assertEqual(common.render_jsonl(rows), common.render_jsonl(rows))


class EvaluationTests(unittest.TestCase):
    def test_15_official_answer_evaluator_known_examples(self) -> None:
        self.assertEqual(evaluator.answer_scores("The Eiffel Tower", ["Eiffel Tower"]), (1.0, 1.0))
        self.assertEqual(evaluator.answer_scores("yes", ["no"]), (0.0, 0.0))
        self.assertEqual(evaluator.answer_scores("alias", ["answer", "The alias"]), (1.0, 1.0))

    def test_16_paired_bootstrap_is_deterministic(self) -> None:
        arrays = [np.asarray([0.0, 0.5, 1.0]), np.asarray([0.5, 0.5, 1.0]), np.asarray([0.0, 0.0, 1.0]), np.asarray([0.0, 1.0, 1.0])]
        first = evaluator.paired_bootstrap(*arrays, seed=7, iterations=100)
        second = evaluator.paired_bootstrap(*arrays, seed=7, iterations=100)
        self.assertEqual(first, second)

    def test_17_scientific_decision_rules(self) -> None:
        supported = {"delta_answer_f1": {"point": .02, "lower_95": .001, "upper_95": .03}, "delta_answer_em": {"point": 0, "lower_95": -.005, "upper_95": .01}}
        negative = {"delta_answer_f1": {"point": -.02, "lower_95": -.03, "upper_95": -.001}, "delta_answer_em": {"point": 0, "lower_95": -.01, "upper_95": .01}}
        inconclusive = {"delta_answer_f1": {"point": .005, "lower_95": -.01, "upper_95": .02}, "delta_answer_em": {"point": 0, "lower_95": -.01, "upper_95": .01}}
        self.assertEqual(evaluator.scientific_decision(supported), "STATIC_HGRAG_XDR_SUPPORTED")
        self.assertEqual(evaluator.scientific_decision(negative), "STATIC_HGRAG_XDR_NEGATIVE")
        self.assertEqual(evaluator.scientific_decision(inconclusive), "STATIC_HGRAG_XDR_INCONCLUSIVE")

    def test_18_subgroup_channel_stays_sealed_without_authorization(self) -> None:
        config = {"schema_version": common.SCHEMA_VERSION, "gold_evaluation": {"authorized": False}}
        with mock.patch.object(evaluator, "load_jsonl") as metadata_open:
            with self.assertRaisesRegex(PermissionError, "NOT_AUTHORIZED"):
                evaluator.run_metadata(config)
        metadata_open.assert_not_called()


class IntegrityTests(unittest.TestCase):
    def test_19_atomic_promotion_rolls_back(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first, second = Path(tmp) / "a", Path(tmp) / "b"
            real_replace = common.os.replace
            calls = 0
            def fail_second(source, target):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("synthetic failure")
                real_replace(source, target)
            with mock.patch.object(common.os, "replace", side_effect=fail_second):
                with self.assertRaisesRegex(OSError, "synthetic failure"):
                    common.write_new_files_atomically(((first, b"a"), (second, b"b")))
            self.assertFalse(first.exists())
            self.assertFalse(second.exists())

    def test_20_no_overwrite_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "artifact"
            common.write_new_files_atomically(((target, b"original"),))
            with self.assertRaises(FileExistsError):
                common.write_new_files_atomically(((target, b"changed"),))
            self.assertEqual(target.read_bytes(), b"original")

    def test_21_independent_verifier_detects_tampering(self) -> None:
        blind = frozen_blind()
        blind["candidate_units"][0]["query_id"] = "tampered"
        with self.assertRaisesRegex(ValueError, "another query"):
            verifier._units_queries([blind])

    def test_22_candidate_ids_belong_to_same_query_pool(self) -> None:
        blind = frozen_blind()
        blind["candidate_units"][0]["unit_id"] = "other::p0::s0"
        with self.assertRaisesRegex(ValueError, "identity differs"):
            runner.build_units_queries([blind])

    def test_23_no_gold_fields_in_rankings_predictions_or_prompts(self) -> None:
        safe = [
            {"query_id": "q", "dense_top20_unit_ids": ["u"]},
            {"query_id": "q", "method": "DENSE_TOP20", "prediction": "x"},
            {"query_id": "q", "method": "DENSE_TOP20", "evidence_unit_ids": ["u"]},
        ]
        for index, row in enumerate(safe):
            common.assert_no_gold_fields(row, f"artifact[{index}]")
        with self.assertRaisesRegex(ValueError, "Gold fields"):
            common.assert_no_gold_fields({"answer": "leak"}, "tampered")

    def test_24_every_query_is_paired_across_two_arms(self) -> None:
        rows = [{"query_id": "q", "method": "DENSE_TOP20"}]
        with self.assertRaisesRegex(ValueError, "pair every query"):
            evaluator.require_complete_pairs(rows, ["q"], "predictions")


if __name__ == "__main__":
    unittest.main()
