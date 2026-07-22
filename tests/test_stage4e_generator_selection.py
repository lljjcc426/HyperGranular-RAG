from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


selection = load_module("stage4e_generator_selection_tested", SCRIPTS / "stage4e_generator_selection.py")


class FakeAdapter:
    def token_ids(self, messages):
        return list(range(len(self.prompt_text(messages).split())))

    def prompt_text(self, messages):
        return " ".join(message["content"] for message in messages)

    def encode_line(self, line):
        return list(range(len(line.split())))

    def decode_line(self, token_ids):
        return "x " * len(token_ids)


class GeneratorSelectionTests(unittest.TestCase):
    def test_split_rows_strips_gold_from_blind(self):
        source = [{
            "id": "x1",
            "dataset": "hotpotqa",
            "question": "Where?",
            "answer": "Here",
            "contexts": [{"title": "T", "sentences": [" A   sentence. "]}],
        }]
        blind, gold = selection.split_rows(source)
        self.assertNotIn("answer", blind[0])
        self.assertEqual(gold[0]["answer"], "Here")
        self.assertEqual(blind[0]["units"][0]["text"], "A sentence.")
        self.assertEqual(blind[0]["query_id"], "hotpotqa::x1")

    def test_hotpot_answer_scoring_matches_expected(self):
        self.assertEqual(selection.answer_scores("The Eiffel Tower", "Eiffel Tower"), (1.0, 1.0))
        self.assertEqual(selection.answer_scores("yes", "no"), (0.0, 0.0))
        em, f1 = selection.answer_scores("Paris France", "Paris")
        self.assertEqual(em, 0.0)
        self.assertAlmostEqual(f1, 2 / 3)

    def test_paired_bootstrap_is_deterministic(self):
        qwen = np.zeros(selection.QUERY_COUNT, dtype="float64")
        gemma = np.ones(selection.QUERY_COUNT, dtype="float64")
        first = selection.paired_bootstrap(qwen, gemma)
        second = selection.paired_bootstrap(qwen, gemma)
        self.assertEqual(first, second)
        self.assertEqual(first["point"], 1.0)

    def test_primary_f1_rule_selects_gemma(self):
        telemetry = {
            "qwen": [{"wall_time_seconds": 1.0, "gpu_peak_memory_bytes": 1}],
            "gemma": [{"wall_time_seconds": 2.0, "gpu_peak_memory_bytes": 2}],
        }
        winner, reason = selection._winner(0.40, 0.42, 0.30, 0.30, telemetry)
        self.assertEqual((winner, reason), ("gemma", "PRIMARY_F1_DIFFERENCE_AT_LEAST_0_010"))

    def test_wall_time_breaks_near_quality_tie(self):
        telemetry = {
            "qwen": [{"wall_time_seconds": 1.0, "gpu_peak_memory_bytes": 2}],
            "gemma": [{"wall_time_seconds": 2.0, "gpu_peak_memory_bytes": 1}],
        }
        winner, reason = selection._winner(0.40, 0.405, 0.30, 0.305, telemetry)
        self.assertEqual((winner, reason), ("qwen", "WALL_TIME_TIEBREAKER"))

    def test_prompt_uses_prefix_and_respects_cap(self):
        original_cap = selection.TOKEN_CAP
        selection.TOKEN_CAP = 35
        try:
            units = [
                {"unit_id": f"u{i}", "title": "T", "text": "one two three four five"}
                for i in range(20)
            ]
            prompt = selection.build_prompt(FakeAdapter(), "Q?", units)
            self.assertLessEqual(prompt["input_token_count"], 35)
            self.assertEqual(prompt["evidence_unit_ids"], [f"u{i}" for i in range(len(prompt["evidence_unit_ids"]))])
        finally:
            selection.TOKEN_CAP = original_cap

    def test_blind_loader_rejects_numeric_identity(self):
        row = {
            "dataset": "hotpotqa",
            "query_id": "hotpotqa::x",
            "question": "Q",
            "sample_id": 1,
            "units": [{"text": "A", "title": "T", "unit_id": "u"}],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "blind.jsonl"
            path.write_text((json.dumps(row) + "\n") * selection.QUERY_COUNT, encoding="utf-8", newline="")
            with self.assertRaises(ValueError):
                selection._load_blind(path)


if __name__ == "__main__":
    unittest.main()
