from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


for name, value in {
    "PYTHONHASHSEED": "0",
    "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}.items():
    os.environ[name] = value

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import stage4e_e2e_common as common
import stage4e_e2e_evaluate as evaluator
import stage4e_e2e_freeze_inputs as freeze
import stage4e_e2e_goldfree_runner as runner
import stage4e_e2e_independent_verifier as verifier


def _source_row(sample_id: str, *, sent_index: int = 0) -> dict:
    return {
        "_id": sample_id,
        "answer": f"answer {sample_id}",
        "context": [
            ["Alpha", [f"Alpha evidence {sample_id}.", "Another alpha sentence."]],
            ["Beta", [f"Beta evidence {sample_id}.", "Another beta sentence."]],
        ],
        "level": "hard",
        "question": f"Question {sample_id}?",
        "supporting_facts": [["Alpha", sent_index], ["Beta", 0]],
        "type": "bridge",
    }


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


class ProtocolAndInputFreezeTests(unittest.TestCase):
    def test_level_a_protocol_is_promoted_and_execution_remains_locked(self) -> None:
        accepted = ROOT / "docs" / "STAGE4E_STATIC_HGRAG_E2E_ANSWER_QUALITY_LEVEL_A_PROTOCOL.md"
        draft = ROOT / "docs" / "STAGE4E_STATIC_HGRAG_E2E_ANSWER_QUALITY_LEVEL_A_PROTOCOL_DRAFT.md"
        text = accepted.read_text(encoding="utf-8")
        self.assertTrue(accepted.is_file())
        self.assertFalse(draft.exists())
        for token in (
            "LEVEL_A_ACCEPTED_FOR_INPUT_BINDING_AND_LEVEL_B_IMPLEMENTATION",
            "STAGE4E_OFFICIAL_EXECUTION_NOT_AUTHORIZED",
            "STATIC_Q25_TOP20",
            "delta_answer_f1",
            "10,000",
            "11 类统计谬误预防",
        ):
            self.assertIn(token, text)

    def test_channel_freeze_is_deterministic_and_gold_isolated(self) -> None:
        rows = [_source_row("a"), _source_row("b"), _source_row("c")]
        with tempfile.TemporaryDirectory() as tmp:
            historical = Path(tmp) / "history.jsonl"
            _write_jsonl(
                historical,
                [{"dataset": "hotpotqa", "query_id": "hotpotqa::old", "sample_id": "old"}],
            )
            with mock.patch.object(freeze, "SAMPLE_SIZE", 2):
                first = freeze.build_frozen_channels(rows, [historical])
                second = freeze.build_frozen_channels(rows, [historical])
        self.assertEqual(common.render_jsonl(first[0]), common.render_jsonl(second[0]))
        self.assertEqual(common.render_json(first[3]), common.render_json(second[3]))
        blind, gold, metadata, manifest = first
        self.assertEqual(len(blind), 2)
        self.assertEqual(len(gold), 2)
        self.assertEqual(len(metadata), 2)
        self.assertEqual(manifest["checks"]["historical_hotpotqa_overlap"], 0)
        self.assertFalse(manifest["checks"]["official_metrics_computed"])
        for row in blind:
            common.assert_no_prohibited_keys(row, "blind")
            self.assertNotIn("answer", row)
            self.assertNotIn("type", row)
        self.assertIn("answer", gold[0])
        self.assertIn("supporting_facts", gold[0])
        self.assertIn("type", metadata[0])
        self.assertIn("level", metadata[0])

    def test_historical_overlap_fails_closed(self) -> None:
        rows = [_source_row("a"), _source_row("b")]
        selected = min(("a", "b"), key=common.selection_key)
        with tempfile.TemporaryDirectory() as tmp:
            historical = Path(tmp) / "history.jsonl"
            _write_jsonl(
                historical,
                [{"dataset": "hotpotqa", "query_id": f"hotpotqa::{selected}", "sample_id": selected}],
            )
            with mock.patch.object(freeze, "SAMPLE_SIZE", 1):
                with self.assertRaisesRegex(ValueError, "overlap historical"):
                    freeze.build_frozen_channels(rows, [historical])

    def test_support_index_bool_and_ambiguous_mapping_fail_closed(self) -> None:
        invalid_type = _source_row("bad")
        invalid_type["supporting_facts"][0][1] = True
        with self.assertRaisesRegex(ValueError, "JSON integer"):
            freeze._build_channels_for_row(invalid_type)

        ambiguous = _source_row("ambiguous")
        ambiguous["context"][1][0] = "Alpha"
        with self.assertRaisesRegex(ValueError, "ambiguous title/sentence"):
            freeze._build_channels_for_row(ambiguous)

    def test_empty_non_gold_sentence_preserves_index_but_has_no_unit_mapping(self) -> None:
        row = _source_row("empty")
        row["context"][0][1][1] = "   "
        blind, gold, _ = freeze._build_channels_for_row(row)
        self.assertEqual(blind["context"][0]["sentences"][1], "")
        self.assertNotIn("::c0::s1", {fact["unit_id"] for fact in gold["supporting_facts"]})

        row["supporting_facts"][0][1] = 1
        with self.assertRaisesRegex(ValueError, "no unique unit mapping"):
            freeze._build_channels_for_row(row)

    def test_atomic_write_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "artifact.json"
            common.write_new_files_atomically(((target, b"{}\n"),))
            self.assertEqual(target.read_bytes(), b"{}\n")

    def test_atomic_multi_file_failure_rolls_back_promoted_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.json"
            second = Path(tmp) / "second.json"
            real_replace = common.os.replace
            calls = 0

            def fail_second(source: Path, target: Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("synthetic promotion failure")
                real_replace(source, target)

            with mock.patch.object(common.os, "replace", side_effect=fail_second):
                with self.assertRaisesRegex(OSError, "synthetic promotion failure"):
                    common.write_new_files_atomically(
                        ((first, b"first\n"), (second, b"second\n"))
                    )
            self.assertFalse(first.exists())
            self.assertFalse(second.exists())
            self.assertFalse(first.with_name(first.name + ".pending").exists())
            self.assertFalse(second.with_name(second.name + ".pending").exists())


class RunnerContractTests(unittest.TestCase):
    def _blind_row(self) -> dict:
        return {
            "context": [
                {
                    "context_index": 0,
                    "sentences": ["One sentence.", "   ", "Third sentence."],
                    "title": "Title",
                }
            ],
            "dataset": common.DATASET,
            "query_id": f"{common.DATASET}::sample",
            "question": "What is tested?",
            "sample_id": "sample",
        }

    def test_unit_builder_preserves_source_sentence_indices(self) -> None:
        units, queries = runner.build_units_queries([self._blind_row()])
        self.assertEqual(
            [row["unit_id"] for row in units],
            [
                f"{common.DATASET}::sample::c0::s0",
                f"{common.DATASET}::sample::c0::s2",
            ],
        )
        self.assertEqual(queries[0]["num_candidate_units"], 2)

    def test_goldfree_authorization_fails_before_input_or_cuda(self) -> None:
        config = {
            "schema_version": common.SCHEMA_VERSION,
            "official_execution": {"authorized": False},
        }
        with mock.patch.object(runner, "_set_determinism") as determinism:
            with self.assertRaisesRegex(PermissionError, "NOT_AUTHORIZED"):
                runner.run(config, "main", "0" * 64)
        determinism.assert_not_called()

    def test_method_order_is_deterministic_and_balanced_by_hash_parity(self) -> None:
        first = common.method_order("query-a")
        self.assertEqual(first, common.method_order("query-a"))
        self.assertEqual(set(first), set(runner.METHODS))

    def test_prompt_cap_and_first_rank_truncation_are_deterministic(self) -> None:
        class FakeTokenizer:
            def __init__(self) -> None:
                self.last_text = ""

            def apply_chat_template(self, messages, *, tokenize, add_generation_prompt):
                text = "|".join(row["content"] for row in messages) + "|assistant:"
                self.last_text = text
                if not tokenize:
                    return text
                values = list(text.encode("utf-8"))
                return {"input_ids": values, "attention_mask": [1] * len(values)}

            def encode(self, text, *, add_special_tokens):
                return list(text.encode("utf-8"))

            def decode(self, values, **kwargs):
                return bytes(values).decode("utf-8", errors="ignore")

        tokenizer = FakeTokenizer()
        units = [
            {"title": "Alpha", "text": "x" * 500, "unit_id": "u1"},
            {"title": "Beta", "text": "short", "unit_id": "u2"},
        ]
        first = runner.build_prompt(tokenizer, "Question?", units, token_cap=260)
        second = runner.build_prompt(tokenizer, "Question?", units, token_cap=260)
        self.assertEqual(first, second)
        self.assertTrue(first["rank1_truncated"])
        self.assertEqual(first["evidence_unit_ids"], ["u1"])
        self.assertLessEqual(first["input_token_count"], 260)
        self.assertNotIn("DENSE_TOP20", tokenizer.last_text)
        self.assertNotIn("STATIC_Q25_TOP20", tokenizer.last_text)


class EvaluationAndVerificationTests(unittest.TestCase):
    def test_official_answer_scoring_examples(self) -> None:
        self.assertEqual(evaluator.answer_scores("The Eiffel Tower", "Eiffel Tower"), (1.0, 1.0))
        self.assertEqual(evaluator.answer_scores("yes", "no"), (0.0, 0.0))
        em, f1 = evaluator.answer_scores("red blue", "red green")
        self.assertEqual(em, 0.0)
        self.assertAlmostEqual(f1, 0.5)

    def test_independent_answer_scoring_matches_without_importing_evaluator(self) -> None:
        cases = (("The answer", "answer"), ("yes", "no"), ("a b", "b c"), ("", ""))
        for prediction, gold in cases:
            self.assertEqual(
                verifier._scores(prediction, gold),
                evaluator.answer_scores(prediction, gold),
            )

    def test_paired_bootstrap_is_deterministic(self) -> None:
        dense_f1 = evaluator.np.asarray([0.0, 0.5, 1.0])
        q25_f1 = evaluator.np.asarray([0.5, 0.5, 1.0])
        dense_em = evaluator.np.asarray([0.0, 0.0, 1.0])
        q25_em = evaluator.np.asarray([0.0, 1.0, 1.0])
        first = evaluator.paired_bootstrap(
            dense_f1, q25_f1, dense_em, q25_em, seed=7, iterations=100
        )
        second = evaluator.paired_bootstrap(
            dense_f1, q25_f1, dense_em, q25_em, seed=7, iterations=100
        )
        self.assertEqual(first, second)

    def test_scientific_decision_gates(self) -> None:
        supported = {
            "delta_answer_f1": {"point": 0.02, "lower_95": 0.001, "upper_95": 0.03},
            "delta_answer_em": {"point": 0.0, "lower_95": -0.005, "upper_95": 0.01},
        }
        negative = {
            "delta_answer_f1": {"point": -0.02, "lower_95": -0.03, "upper_95": -0.001},
            "delta_answer_em": {"point": 0.0, "lower_95": -0.01, "upper_95": 0.01},
        }
        inconclusive = {
            "delta_answer_f1": {"point": 0.005, "lower_95": -0.01, "upper_95": 0.02},
            "delta_answer_em": {"point": 0.0, "lower_95": -0.01, "upper_95": 0.01},
        }
        self.assertEqual(evaluator.scientific_decision(supported), "STATIC_HGRAG_E2E_SUPPORTED")
        self.assertEqual(evaluator.scientific_decision(negative), "STATIC_HGRAG_E2E_NEGATIVE")
        self.assertEqual(evaluator.scientific_decision(inconclusive), "STATIC_HGRAG_E2E_INCONCLUSIVE")

    def test_gold_authorization_fails_before_prediction_or_gold_open(self) -> None:
        config = {
            "schema_version": common.SCHEMA_VERSION,
            "gold_evaluation": {"authorized": False},
        }
        with mock.patch.object(evaluator, "_path") as path_lookup:
            with self.assertRaisesRegex(PermissionError, "NOT_AUTHORIZED"):
                evaluator.run(config, "0" * 64)
        path_lookup.assert_not_called()

    def test_input_verifier_rejects_ambiguous_source_title_index(self) -> None:
        row = _source_row("ambiguous")
        row["context"][1][0] = "Alpha"
        with self.assertRaisesRegex(ValueError, "ambiguous source support key"):
            verifier._source_context(row, "qid")
            with self.assertRaises(FileExistsError):
                common.write_new_files_atomically(((target, b"changed\n"),))
            self.assertEqual(target.read_bytes(), b"{}\n")


if __name__ == "__main__":
    unittest.main()
