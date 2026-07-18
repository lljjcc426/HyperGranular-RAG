from __future__ import annotations

import copy
import importlib.metadata
import json
import shutil
import subprocess
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

from stage4b_u1_common import (  # noqa: E402
    FROZEN_BATCH_SIZE,
    FROZEN_MAX_LENGTH,
    OFFICIAL_CACHE_MEMBERS,
    id_digest,
    load_json,
    load_jsonl,
    sha256_file,
    write_json,
    write_jsonl,
)
from stage4b_u1_evaluate import validate_pre_gold_verification  # noqa: E402
from stage4b_u1_goldfree_retrieval import RetrievalConfig  # noqa: E402
from stage4b_u1_independent_verifier import run_independent_verifier  # noqa: E402
from stage4b_u1_simplified_preflight import (  # noqa: E402
    CONFIG_SCHEMA_VERSION,
    EVALUATOR_PATH,
    IMPLEMENTATION_PATHS,
    RUN_ID,
    SIMPLIFIED_PROTOCOL_PATH,
    SIMPLIFIED_RUNNER_PATH,
    SIMPLIFIED_VERIFIER_PATH,
    load_strict_json,
    run_preflight,
)
from stage4b_u1_simplified_runner import run_simplified_controller  # noqa: E402
from test_stage4b_u1_goldfree import build_synthetic_pipeline  # noqa: E402


def make_synthetic_config(root: Path, paths: dict[str, Path]) -> tuple[Path, dict]:
    output_root = root / "simplified"
    output_root.mkdir()
    decisions = output_root / "decisions.jsonl"
    rankings = output_root / "rankings.jsonl"
    policy = output_root / "policy.json"
    verified = output_root / "verified_pre_gold.json"
    with np.load(paths["cache"], allow_pickle=False) as cache:
        unit_shape = list(cache["unit_embeddings"].shape)
        query_shape = list(cache["query_embeddings"].shape)
        model_name = str(cache["model_name"].reshape(-1)[0])
    units = load_jsonl(paths["units"])
    queries = load_jsonl(paths["queries"])
    config = {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "run_id": RUN_ID,
        "mode": "development",
        "protocol": {
            "path": SIMPLIFIED_PROTOCOL_PATH,
            "sha256": sha256_file(REPO_ROOT / SIMPLIFIED_PROTOCOL_PATH),
        },
        "implementation": {
            "code_commit": subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip(),
            "files": [
                {"path": path, "sha256": sha256_file(REPO_ROOT / path)}
                for path in IMPLEMENTATION_PATHS
            ],
        },
        "environment": {
            "python_executable": sys.executable,
            "python_version": ".".join(str(value) for value in sys.version_info[:3]),
            "required_packages": {"numpy": importlib.metadata.version("numpy")},
        },
        "inputs": {
            "unlabeled_units": {
                "path": str(paths["units"]),
                "sha256": sha256_file(paths["units"]),
            },
            "unlabeled_queries": {
                "path": str(paths["queries"]),
                "sha256": sha256_file(paths["queries"]),
            },
            "channel_audit": {
                "path": str(paths["channel"]),
                "sha256": sha256_file(paths["channel"]),
            },
            "query_count": len(queries),
            "unit_count": len(units),
            "sample_id_sha256": id_digest(str(row["sample_id"]) for row in queries),
            "query_id_sha256": id_digest(str(row["query_id"]) for row in queries),
            "query_id_namespace_rule": 'query_id == dataset + "::" + sample_id',
        },
        "embedding_cache": {
            "path": str(paths["cache"]),
            "sha256": sha256_file(paths["cache"]),
            "bytes": paths["cache"].stat().st_size,
            "members": sorted(OFFICIAL_CACHE_MEMBERS),
            "unit_embeddings_shape": unit_shape,
            "query_embeddings_shape": query_shape,
            "dtype": "float32",
            "model_name": model_name,
            "max_length": FROZEN_MAX_LENGTH,
        },
        "retrieval": {
            **RetrievalConfig().to_dict(),
            "model_name": model_name,
            "max_length": FROZEN_MAX_LENGTH,
            "batch_size": FROZEN_BATCH_SIZE,
            "embedding_dtype": "float32",
            "scalar_dtype": "float64",
        },
        "controller": {
            "script": SIMPLIFIED_RUNNER_PATH,
            "embedding_cache_mode": "require-existing",
            "evaluation_labels_loaded": False,
        },
        "outputs": {
            "decisions": str(decisions),
            "rankings": str(rankings),
            "policy": str(policy),
        },
        "verification": {
            "script": SIMPLIFIED_VERIFIER_PATH,
            "decisions_input": str(decisions),
            "rankings_input": str(rankings),
            "policy_input": str(policy),
            "output": str(verified),
        },
        "evaluation_contract": {
            "authorized": False,
            "evaluator_script": EVALUATOR_PATH,
            "evaluator_script_sha256": sha256_file(REPO_ROOT / EVALUATOR_PATH),
            "inputs": {
                "rankings": str(rankings),
                "policy": str(policy),
                "verified_pre_gold": str(verified),
            },
            "outputs": {
                "query_audit": str(output_root / "query_audit.jsonl"),
                "evaluation_summary": str(output_root / "evaluation_summary.json"),
            },
        },
        "retry_policy": {"automatic_retries": 0},
    }
    config_path = root / "synthetic_config.json"
    write_json(config_path, config)
    return config_path, config


class Stage4BU1SimplifiedTests(unittest.TestCase):
    def build(self, root: Path) -> tuple[dict[str, Path], Path, dict]:
        paths = build_synthetic_pipeline(root)
        config_path, config = make_synthetic_config(root, paths)
        return paths, config_path, config

    def assert_verifier_rejects_mutation(
        self,
        root: Path,
        artifact: str,
        mutate: object,
        expected_error: str,
    ) -> None:
        _, config_path, config = self.build(root)
        run_simplified_controller(config_path, synthetic_test_mode=True)
        artifact_path = Path(config["outputs"][artifact])
        rows = load_jsonl(artifact_path)
        mutate(rows)
        write_jsonl(artifact_path, rows)
        policy_path = Path(config["outputs"]["policy"])
        policy = load_json(policy_path)
        policy["output_hashes"][artifact] = sha256_file(artifact_path)
        write_json(policy_path, policy)
        with self.assertRaisesRegex(ValueError, expected_error):
            run_independent_verifier(config_path, synthetic_test_mode=True)
        self.assertFalse(Path(config["verification"]["output"]).exists())

    def test_end_to_end_semantic_equivalence_and_independent_verifier(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            baseline, config_path, config = self.build(root)
            context = run_preflight(config_path, synthetic_test_mode=True)
            self.assertEqual(context.config_sha256, sha256_file(config_path))
            policy = run_simplified_controller(config_path, synthetic_test_mode=True)
            self.assertEqual(
                load_jsonl(Path(config["outputs"]["decisions"])),
                load_jsonl(baseline["decisions"]),
            )
            self.assertEqual(
                load_jsonl(Path(config["outputs"]["rankings"])),
                load_jsonl(baseline["rankings"]),
            )
            self.assertFalse(policy["evaluation_labels_loaded"])
            result = run_independent_verifier(config_path, synthetic_test_mode=True)
            self.assertEqual(result["status"], "VERIFIED_PRE_GOLD")
            self.assertTrue(result["policy_and_ranking"]["ranking_structure_check"])
            validate_pre_gold_verification(
                pre_gold_path=Path(config["verification"]["output"]),
                policy=load_json(Path(config["outputs"]["policy"])),
                policy_path=Path(config["outputs"]["policy"]),
                rankings_path=Path(config["outputs"]["rankings"]),
                evaluator_source=REPO_ROOT / EVALUATOR_PATH,
                synthetic_test_mode=True,
            )

    def test_duplicate_config_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"schema_version":"a","schema_version":"b"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
                load_strict_json(path)

    def test_nonfinite_config_value_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nan.json"
            path.write_text('{"value":NaN}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Non-finite JSON constant"):
                load_strict_json(path)

    def test_unknown_or_gold_config_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, config_path, config = self.build(root)
            config["gold_map"] = "forbidden.json"
            write_json(config_path, config)
            with self.assertRaisesRegex(ValueError, "config key set differs"):
                run_preflight(config_path, synthetic_test_mode=True)

    def test_implementation_hash_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, config_path, config = self.build(root)
            config["implementation"]["files"][0]["sha256"] = "A" * 64
            write_json(config_path, config)
            with self.assertRaisesRegex(ValueError, "Implementation SHA-256 differs"):
                run_preflight(config_path, synthetic_test_mode=True)

    def test_missing_require_existing_cache_leaves_outputs_absent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, config_path, config = self.build(root)
            config["embedding_cache"]["path"] = str(root / "missing.npz")
            config["embedding_cache"]["sha256"] = "A" * 64
            write_json(config_path, config)
            with self.assertRaisesRegex(ValueError, "Frozen embedding cache SHA-256 differs"):
                run_simplified_controller(config_path, synthetic_test_mode=True)
            self.assertTrue(all(not Path(value).exists() for value in config["outputs"].values()))

    def test_preexisting_output_is_rejected_before_controller(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, config_path, config = self.build(root)
            Path(config["outputs"]["decisions"]).write_text("occupied", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Registered future output already exists"):
                run_simplified_controller(config_path, synthetic_test_mode=True)

    def test_partial_promotion_is_rolled_back(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, config_path, config = self.build(root)

            def partial(pairs: list[tuple[Path, Path]]) -> None:
                shutil.copyfile(pairs[0][0], pairs[0][1])
                raise OSError("synthetic partial promotion")

            with mock.patch(
                "stage4b_u1_simplified_runner.promote_pending_outputs", side_effect=partial
            ):
                with self.assertRaisesRegex(OSError, "synthetic partial promotion"):
                    run_simplified_controller(config_path, synthetic_test_mode=True)
            self.assertTrue(all(not Path(value).exists() for value in config["outputs"].values()))

    def test_verifier_rejects_non_candidate_ranking(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, config_path, config = self.build(root)
            run_simplified_controller(config_path, synthetic_test_mode=True)
            rankings_path = Path(config["outputs"]["rankings"])
            rankings = load_jsonl(rankings_path)
            rankings[0]["dense_top20_unit_ids"][-1] = "synthetic::not-a-candidate"
            write_jsonl(rankings_path, rankings)
            policy_path = Path(config["outputs"]["policy"])
            policy = load_json(policy_path)
            policy["output_hashes"]["rankings"] = sha256_file(rankings_path)
            write_json(policy_path, policy)
            with self.assertRaisesRegex(ValueError, "non-candidate"):
                run_independent_verifier(config_path, synthetic_test_mode=True)
            self.assertFalse(Path(config["verification"]["output"]).exists())

    def test_verifier_rejects_final_selector_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, config_path, config = self.build(root)
            run_simplified_controller(config_path, synthetic_test_mode=True)
            rankings_path = Path(config["outputs"]["rankings"])
            rankings = load_jsonl(rankings_path)
            row = next(value for value in rankings if int(value["trigger_u1"]) == 1)
            row["final_top20_unit_ids"] = list(row["dense_top20_unit_ids"])
            write_jsonl(rankings_path, rankings)
            policy_path = Path(config["outputs"]["policy"])
            policy = load_json(policy_path)
            policy["output_hashes"]["rankings"] = sha256_file(rankings_path)
            write_json(policy_path, policy)
            with self.assertRaisesRegex(ValueError, "Final ranking violates"):
                run_independent_verifier(config_path, synthetic_test_mode=True)

    def test_verifier_rejects_execution_config_binding_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, config_path, config = self.build(root)
            run_simplified_controller(config_path, synthetic_test_mode=True)
            policy_path = Path(config["outputs"]["policy"])
            policy = copy.deepcopy(load_json(policy_path))
            policy["execution_config_sha256"] = "A" * 64
            write_json(policy_path, policy)
            with self.assertRaisesRegex(ValueError, "execution_config_sha256"):
                run_independent_verifier(config_path, synthetic_test_mode=True)

    def test_verifier_rejects_decision_sample_id_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assert_verifier_rejects_mutation(
                Path(directory),
                "decisions",
                lambda rows: rows[0].__setitem__("sample_id", "wrong-sample"),
                "Decision row identity differs at sample_id",
            )

    def test_verifier_rejects_ranking_dataset_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assert_verifier_rejects_mutation(
                Path(directory),
                "rankings",
                lambda rows: rows[0].__setitem__("dataset", "wrong-dataset"),
                "Ranking row identity differs at dataset",
            )

    def test_verifier_rejects_float_planned_insert_count(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assert_verifier_rejects_mutation(
                Path(directory),
                "decisions",
                lambda rows: rows[0].__setitem__("planned_insert_count", 1.0),
                "planned_insert_count must be a JSON integer",
            )

    def test_verifier_rejects_boolean_trigger(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assert_verifier_rejects_mutation(
                Path(directory),
                "decisions",
                lambda rows: rows[0].__setitem__("trigger_u1", True),
                "trigger_u1 must be a JSON integer",
            )

    def test_verifier_rejects_numeric_ranking_unit_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assert_verifier_rejects_mutation(
                Path(directory),
                "rankings",
                lambda rows: rows[0]["dense_top20_unit_ids"].__setitem__(-1, 123),
                "dense_top20_unit_ids.*must be a non-empty JSON string",
            )

    def test_verifier_rejects_infeasible_non_null_score(self) -> None:
        def mutate(rows: list[dict]) -> None:
            row = rows[0]
            row["selected_edge_count"] = 0
            row["planned_insert_count"] = 0
            row["feasible"] = 0
            row["trigger_u1"] = 0
            row["ordered_rank"] = None
            for field in (
                "u_margin",
                "u_boundary",
                "r_edge",
                "r_candidate",
                "uncertainty",
                "readiness",
            ):
                row[field] = None
            row["score"] = 0.0

        with tempfile.TemporaryDirectory() as directory:
            self.assert_verifier_rejects_mutation(
                Path(directory),
                "decisions",
                mutate,
                "Infeasible decision.*score must be null",
            )

    def test_verifier_rejects_boolean_feasible_ordered_rank(self) -> None:
        def mutate(rows: list[dict]) -> None:
            row = next(value for value in rows if int(value["feasible"]) == 1)
            row["ordered_rank"] = True

        with tempfile.TemporaryDirectory() as directory:
            self.assert_verifier_rejects_mutation(
                Path(directory),
                "decisions",
                mutate,
                "ordered_rank must be a JSON integer",
            )


if __name__ == "__main__":
    unittest.main()
