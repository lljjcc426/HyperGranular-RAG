from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from stage2_dense_replication import fixed_retrieve as legacy_fixed_retrieve  # noqa: E402
from stage2d_protected_rerank import (  # noqa: E402
    expansion_candidates as legacy_expansion_candidates,
    protected_rerank as legacy_protected_rerank,
)
from stage4b_u1_common import (  # noqa: E402
    FROZEN_BATCH_SIZE,
    FROZEN_MAX_LENGTH,
    FROZEN_MODEL_NAME,
    IMPLEMENTATION_CHECKPOINT,
    OFFICIAL_V2_3_1_ARTIFACT_PATHS,
    assert_no_prohibited_keys,
    id_digest,
    load_json,
    load_jsonl,
    sha256_file,
    write_json,
    write_jsonl,
)
from stage4b_u1_evaluate import (  # noqa: E402
    baseline_metrics,
    evaluate_rows,
    run_evaluation,
)
from stage4b_u1_goldfree_controller import (  # noqa: E402
    promote_pending_outputs,
    run_controller,
    validate_controller_inputs,
    validate_policy_equivalence,
)
import stage4b_u1_goldfree_controller as controller_module  # noqa: E402
from stage4b_u1_goldfree_retrieval import (  # noqa: E402
    RetrievalConfig,
    allocate_budget,
    decision_from_balls,
    ecdf_midrank,
    expansion_candidates_goldfree,
    fixed_retrieve_goldfree,
    protected_rerank_goldfree,
)
from stage4b_u1_prepare_channels import (  # noqa: E402
    prepare_channels,
    validate_execution_boundary,
)
from stage4b_u1_verify import (  # noqa: E402
    run_verification,
    validate_candidate_pools,
    verify_effective_k_structure,
)
from stage4b_u1_run_synthetic_verification import (  # noqa: E402
    validate_governance_bindings,
)


def normalized(vector: list[float]) -> np.ndarray:
    value = np.asarray(vector, dtype="float32")
    return value / np.linalg.norm(value)


def synthetic_labeled_rows() -> tuple[list[dict], list[dict], np.ndarray, np.ndarray]:
    group_vectors = [
        [1.0, 1.0, 0.0, 0.0, 0.1, 0.0],
        [1.0, 0.8, 0.2, 0.0, 0.0, 0.1],
        [0.8, 0.1, 1.0, 0.0, 0.1, 0.0],
        [0.7, 0.1, 0.0, 1.0, 0.0, 0.1],
        [0.6, 0.0, 0.8, 0.2, 0.1, 0.0],
        [0.6, 0.0, 0.2, 0.8, 0.0, 0.1],
        [0.5, 0.2, 0.6, 0.4, 0.1, 0.0],
        [0.5, 0.2, 0.4, 0.6, 0.0, 0.1],
    ]
    group_text = [
        "alpha beta seed",
        "alpha beta anchor",
        "gamma evidence",
        "delta evidence",
        "epsilon gamma",
        "epsilon delta",
        "gamma delta bridge",
        "epsilon bridge relation",
    ]
    query_vector = normalized([1.0, 1.0, 1.0, 1.0, 0.0, 0.0])
    units: list[dict] = []
    queries: list[dict] = []
    embeddings: list[np.ndarray] = []
    query_embeddings: list[np.ndarray] = []
    for query_number in range(4):
        query_id = f"synthetic::q{query_number}"
        sample_id = f"q{query_number}"
        query_unit_ids: list[str] = []
        for group, base_vector in enumerate(group_vectors):
            for member in range(3):
                unit_id = f"{query_id}::g{group}::u{member}"
                query_unit_ids.append(unit_id)
                units.append(
                    {
                        "unit_id": unit_id,
                        "query_id": query_id,
                        "dataset": "synthetic",
                        "sample_id": sample_id,
                        "doc_id": f"doc-{group}",
                        "title": f"title {group}",
                        "context_index": group,
                        "sentence_id": member,
                        "text": f"{group_text[group]} member{member}",
                        "is_gold": False,
                    }
                )
                jitter = np.zeros(6, dtype="float32")
                jitter[(group + member) % 6] = 0.002 * member
                embeddings.append(normalized((np.asarray(base_vector) + jitter).tolist()))
        gold_ids = [query_unit_ids[0], query_unit_ids[-1]]
        for row in units[-24:]:
            row["is_gold"] = row["unit_id"] in gold_ids
        queries.append(
            {
                "query_id": query_id,
                "dataset": "synthetic",
                "sample_id": sample_id,
                "question": "alpha beta gamma delta epsilon bridge relation",
                "answer": "synthetic answer",
                "gold_unit_ids": gold_ids,
                "num_candidate_units": 24,
                "num_gold_units": 2,
                "metadata": {"type": ["comparison", "inference"][query_number % 2]},
            }
        )
        query_embeddings.append(query_vector)
    return (
        units,
        queries,
        np.vstack(embeddings).astype("float32"),
        np.vstack(query_embeddings).astype("float32"),
    )


def formal_query_rows() -> list[dict]:
    _, queries, _, _ = synthetic_labeled_rows()
    formal = copy.deepcopy(queries)
    for row in formal:
        row["dataset"] = "2wikimultihopqa"
        row["query_id"] = f"2wikimultihopqa::{row['sample_id']}"
    return formal


def command(*parts: object, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *[str(part) for part in parts]],
        check=check,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def build_synthetic_pipeline(root: Path, suffix: str = "") -> dict[str, Path]:
    units, queries, unit_embeddings, query_embeddings = synthetic_labeled_rows()
    paths = {
        "labeled_units": root / f"labeled_units{suffix}.jsonl",
        "labeled_queries": root / f"labeled_queries{suffix}.jsonl",
        "units": root / f"unlabeled_units{suffix}.jsonl",
        "queries": root / f"unlabeled_queries{suffix}.jsonl",
        "gold": root / f"gold_map{suffix}.json",
        "channel": root / f"channel_audit{suffix}.json",
        "evaluator_channel": root / f"evaluator_audit{suffix}.json",
        "cache": root / f"embeddings{suffix}.npz",
        "decisions": root / f"decisions{suffix}.jsonl",
        "rankings": root / f"rankings{suffix}.jsonl",
        "policy": root / f"policy{suffix}.json",
        "pre_gold": root / f"pre_gold{suffix}.json",
        "baseline": root / f"baseline{suffix}.json",
    }
    write_jsonl(paths["labeled_units"], units)
    write_jsonl(paths["labeled_queries"], queries)
    command(
        SCRIPTS / "stage4b_u1_prepare_channels.py",
        "--labeled-units", paths["labeled_units"],
        "--labeled-queries", paths["labeled_queries"],
        "--unlabeled-units-output", paths["units"],
        "--unlabeled-queries-output", paths["queries"],
        "--gold-map-output", paths["gold"],
        "--controller-audit-output", paths["channel"],
        "--evaluator-audit-output", paths["evaluator_channel"],
        "--mode", "development",
        "--synthetic-test-mode",
    )
    split_units = load_jsonl(paths["units"])
    split_queries = load_jsonl(paths["queries"])
    np.savez_compressed(
        paths["cache"],
        unit_embeddings=unit_embeddings,
        query_embeddings=query_embeddings,
        unit_ids=np.asarray([row["unit_id"] for row in split_units]),
        query_ids=np.asarray([row["query_id"] for row in split_queries]),
        model_name=np.asarray(["synthetic-model"]),
        max_length=np.asarray([192], dtype="int64"),
    )
    command(
        SCRIPTS / "stage4b_u1_goldfree_controller.py",
        "--units", paths["units"],
        "--queries", paths["queries"],
        "--channel-audit", paths["channel"],
        "--embedding-cache", paths["cache"],
        "--decisions-output", paths["decisions"],
        "--rankings-output", paths["rankings"],
        "--policy-output", paths["policy"],
        "--mode", "development",
        "--model-name", "synthetic-model",
        "--synthetic-test-mode",
    )
    run_synthetic_verifier(paths, paths["pre_gold"])
    rows = evaluate_rows(load_jsonl(paths["rankings"]), load_json(paths["gold"]))
    write_json(
        paths["baseline"],
        {"status": "SYNTHETIC_BASELINE_REFERENCE", "expected": baseline_metrics(rows)},
    )
    return paths


def run_synthetic_verifier(paths: dict[str, Path], output: Path) -> dict:
    return run_verification(
        units_path=paths["units"],
        queries_path=paths["queries"],
        channel_audit_path=paths["channel"],
        embedding_cache_path=paths["cache"],
        decisions_path=paths["decisions"],
        rankings_path=paths["rankings"],
        policy_path=paths["policy"],
        controller_source=SCRIPTS / "stage4b_u1_goldfree_controller.py",
        source_audit_path=None,
        gold_map_path=None,
        evaluator_audit_path=None,
        query_audit_path=None,
        summary_path=None,
        output_path=output,
        synthetic_test_mode=True,
    )


def refresh_policy_output_hash(paths: dict[str, Path], key: str) -> None:
    policy = load_json(paths["policy"])
    policy["output_hashes"][key] = sha256_file(paths[key])
    write_json(paths["policy"], policy)


def cache_payload(path: Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as cache:
        return {name: np.asarray(cache[name]) for name in cache.files}


def write_cache_payload(path: Path, payload: dict[str, np.ndarray]) -> None:
    np.savez_compressed(path, **payload)


def require_existing_output_paths(output_root: Path, suffix: str = "") -> dict[str, Path]:
    return {
        "decisions": output_root / f"require-decisions{suffix}.jsonl",
        "rankings": output_root / f"require-rankings{suffix}.jsonl",
        "policy": output_root / f"require-policy{suffix}.json",
    }


def run_require_existing_synthetic_controller(
    paths: dict[str, Path],
    output_root: Path,
    *,
    cache_path: Path | None = None,
    expected_sha256: str | None = None,
    suffix: str = "",
) -> dict[str, Path]:
    selected_cache = cache_path or paths["cache"]
    outputs = require_existing_output_paths(output_root, suffix)
    run_controller(
        units_path=paths["units"],
        queries_path=paths["queries"],
        channel_audit_path=paths["channel"],
        embedding_cache=selected_cache,
        decisions_output=outputs["decisions"],
        rankings_output=outputs["rankings"],
        policy_output=outputs["policy"],
        mode="development",
        policy_input=None,
        model_name="synthetic-model",
        batch_size=FROZEN_BATCH_SIZE,
        max_length=FROZEN_MAX_LENGTH,
        config=RetrievalConfig(),
        controller_source=SCRIPTS / "stage4b_u1_goldfree_controller.py",
        source_audit_path=None,
        synthetic_test_mode=True,
        embedding_cache_mode="require-existing",
        expected_embedding_cache_sha256=(
            expected_sha256 or sha256_file(selected_cache)
        ),
        reference_policy_path=None,
    )
    return outputs


def effective_k_ranking(candidate_count: int, planned: int) -> tuple[dict, set[str]]:
    candidate_ids = [f"synthetic::short::u{index}" for index in range(candidate_count)]
    effective_k = min(20, candidate_count)
    protect_n = min(10, effective_k)
    dense = candidate_ids[:effective_k]
    q25 = list(dense)
    if planned:
        insertion = q25[protect_n + planned : protect_n + 2 * planned]
        displaced = q25[protect_n : protect_n + planned]
        q25[protect_n : protect_n + 2 * planned] = insertion + displaced
    inserted = q25[protect_n : protect_n + planned]
    return (
        {
            "query_id": "synthetic::short",
            "planned_insert_count": planned,
            "dense_top20_unit_ids": dense,
            "q25_top20_unit_ids": q25,
            "q25_inserted_unit_ids": inserted,
            "final_top20_unit_ids": q25,
        },
        set(candidate_ids),
    )


class Stage4BU1CoreTests(unittest.TestCase):
    def test_effective_k_17_is_accepted(self) -> None:
        ranking, candidates = effective_k_ranking(17, 2)
        self.assertEqual(
            verify_effective_k_structure(ranking, candidates),
            ranking["q25_inserted_unit_ids"],
        )

    def test_effective_k_10_is_accepted_and_insertion_is_bounded(self) -> None:
        ranking, candidates = effective_k_ranking(10, 0)
        self.assertEqual(verify_effective_k_structure(ranking, candidates), [])
        ranking["planned_insert_count"] = 1
        with self.assertRaisesRegex(ValueError, "effective range"):
            verify_effective_k_structure(ranking, candidates)

    def test_effective_k_wrong_length_is_rejected(self) -> None:
        ranking, candidates = effective_k_ranking(17, 2)
        ranking["dense_top20_unit_ids"].pop()
        with self.assertRaisesRegex(ValueError, "effective-K length differs"):
            verify_effective_k_structure(ranking, candidates)

    def test_effective_k_duplicate_unit_id_is_rejected(self) -> None:
        ranking, candidates = effective_k_ranking(17, 2)
        ranking["q25_top20_unit_ids"][-1] = ranking["q25_top20_unit_ids"][-2]
        with self.assertRaisesRegex(ValueError, "not unique"):
            verify_effective_k_structure(ranking, candidates)

    def test_effective_k_non_candidate_unit_id_is_rejected(self) -> None:
        ranking, candidates = effective_k_ranking(17, 2)
        ranking["final_top20_unit_ids"][-1] = "synthetic::outside"
        with self.assertRaisesRegex(ValueError, "non-candidate"):
            verify_effective_k_structure(ranking, candidates)

    def test_candidate_count_drift_is_rejected(self) -> None:
        queries = [{"query_id": "synthetic::short", "num_candidate_units": 2}]
        units = [{"query_id": "synthetic::short", "unit_id": "u0"}]
        with self.assertRaisesRegex(ValueError, "candidate count differs"):
            validate_candidate_pools(units, queries)

    def test_empty_candidate_pool_is_rejected(self) -> None:
        queries = [{"query_id": "synthetic::short", "num_candidate_units": 0}]
        with self.assertRaisesRegex(ValueError, "candidate pool is empty"):
            validate_candidate_pools([], queries)

    def test_effective_protected_prefix_drift_is_rejected(self) -> None:
        ranking, candidates = effective_k_ranking(17, 2)
        ranking["q25_top20_unit_ids"][0], ranking["q25_top20_unit_ids"][10] = (
            ranking["q25_top20_unit_ids"][10],
            ranking["q25_top20_unit_ids"][0],
        )
        with self.assertRaisesRegex(ValueError, "effective protected prefix"):
            verify_effective_k_structure(ranking, candidates)

    def test_effective_k_insertion_derivation_drift_is_rejected(self) -> None:
        ranking, candidates = effective_k_ranking(17, 2)
        ranking["q25_inserted_unit_ids"] = list(
            reversed(ranking["q25_inserted_unit_ids"])
        )
        with self.assertRaisesRegex(ValueError, "effective-K structure"):
            verify_effective_k_structure(ranking, candidates)

    def test_channel_split_removes_all_controller_labels(self) -> None:
        units, queries, _, _ = synthetic_labeled_rows()
        unlabeled_units, unlabeled_queries, gold_map = prepare_channels(units, queries)
        assert_no_prohibited_keys(unlabeled_units)
        assert_no_prohibited_keys(unlabeled_queries)
        self.assertNotIn("is_gold", unlabeled_units[0])
        self.assertNotIn("answer", unlabeled_queries[0])
        self.assertNotIn("metadata", unlabeled_queries[0])
        self.assertEqual(len(gold_map["queries"]), 4)

    def test_channel_split_rejects_inconsistent_gold(self) -> None:
        units, queries, _, _ = synthetic_labeled_rows()
        units[0]["is_gold"] = False
        with self.assertRaisesRegex(ValueError, "Gold labels disagree"):
            prepare_channels(units, queries)

    def test_controller_rejects_a_reintroduced_label_field(self) -> None:
        units, queries, _, _ = synthetic_labeled_rows()
        unlabeled_units, unlabeled_queries, _ = prepare_channels(units, queries)
        unlabeled_units[0]["is_gold"] = False
        with self.assertRaisesRegex(ValueError, "Prohibited controller keys"):
            validate_controller_inputs(unlabeled_units, unlabeled_queries)

    def test_numeric_boundary_and_ecdf_rules(self) -> None:
        ball = {"ball_id": "only", "center": normalized([1.0, 0.0]), "radius": 0.0}
        decision = decision_from_balls(normalized([1.0, 0.0]), [ball])
        self.assertEqual(decision["boundary_margin"], 999.0)
        self.assertAlmostEqual(decision["ball_score_margin"], 2.0)
        self.assertAlmostEqual(ecdf_midrank([1.0, 1.0, 3.0], 1.0), 1.0 / 3.0)
        self.assertEqual(ecdf_midrank([1.0, 2.0], 0.0), 0.0)
        self.assertEqual(ecdf_midrank([1.0, 2.0], 3.0), 1.0)
        with self.assertRaisesRegex(ValueError, "empty ball list"):
            decision_from_balls(normalized([1.0, 0.0]), [])

    def test_budget_uses_largest_prefix_without_skipping(self) -> None:
        rows = [
            {"query_id": "a", "feasible": 1, "score": 3.0, "tie_hash": "A", "planned_insert_count": 4,
             "q25_top20_unit_ids": ["a"], "dense_top20_unit_ids": ["d-a"], "q25_inserted_unit_ids": ["1", "2", "3", "4"]},
            {"query_id": "b", "feasible": 1, "score": 2.0, "tie_hash": "B", "planned_insert_count": 4,
             "q25_top20_unit_ids": ["b"], "dense_top20_unit_ids": ["d-b"], "q25_inserted_unit_ids": ["5", "6", "7", "8"]},
            {"query_id": "c", "feasible": 1, "score": 1.0, "tie_hash": "C", "planned_insert_count": 1,
             "q25_top20_unit_ids": ["c"], "dense_top20_unit_ids": ["d-c"], "q25_inserted_unit_ids": ["9"]},
        ]
        allocation = allocate_budget(rows)
        self.assertEqual(allocation["budget_units"], 5)
        self.assertEqual(allocation["selected_queries"], 1)
        self.assertEqual([row["trigger_u1"] for row in rows], [1, 0, 0])
        self.assertEqual([row["ordered_rank"] for row in rows], [1, 2, 3])

    def test_goldfree_rewrite_matches_legacy_frozen_ranking_on_synthetic_input(self) -> None:
        units, queries, unit_embeddings, query_embeddings = synthetic_labeled_rows()
        query = queries[0]
        candidate_indices = list(range(24))
        query_embedding = query_embeddings[0]
        config = RetrievalConfig()
        args = SimpleNamespace(
            **config.to_dict(),
            expand_boundary_only=False,
            decision_boundary_margin=0.50,
            decision_score_margin=0.10,
            decision_min_ball_score=0.20,
        )
        legacy_dense = legacy_fixed_retrieve(
            query_embedding, candidate_indices, units, unit_embeddings, config.max_k
        )
        goldfree_dense = fixed_retrieve_goldfree(
            query_embedding, candidate_indices, units, unit_embeddings, config.max_k
        )
        self.assertEqual(
            [row["unit_id"] for row in legacy_dense],
            [row["unit_id"] for row in goldfree_dense],
        )
        legacy_expanded, legacy_selected, _, _ = legacy_expansion_candidates(
            query, query_embedding, candidate_indices, units, unit_embeddings, args, "gated"
        )
        goldfree_expanded, goldfree_selected, _ = expansion_candidates_goldfree(
            query, query_embedding, candidate_indices, units, unit_embeddings, config
        )
        self.assertEqual(
            [row["edge_id"] for row in legacy_selected],
            [row["edge_id"] for row in goldfree_selected],
        )
        self.assertEqual(
            [row["unit_id"] for row in legacy_expanded],
            [row["unit_id"] for row in goldfree_expanded],
        )
        legacy_filtered = [row for row in legacy_expanded if row["score"] >= config.q25_floor]
        goldfree_filtered = [row for row in goldfree_expanded if row["score"] >= config.q25_floor]
        legacy_q25, legacy_insert = legacy_protected_rerank(
            legacy_dense, legacy_filtered, config.protect_n, config.insert_budget, config.max_k
        )
        goldfree_q25, goldfree_inserted = protected_rerank_goldfree(
            goldfree_dense, goldfree_filtered, config.protect_n, config.insert_budget, config.max_k
        )
        self.assertEqual(
            [row["unit_id"] for row in legacy_q25],
            [row["unit_id"] for row in goldfree_q25],
        )
        self.assertEqual(legacy_insert["inserted_units"], len(goldfree_inserted))


class Stage4BU1CacheFailClosedTests(unittest.TestCase):
    def test_require_existing_valid_cache_passes_without_build_or_mkdir(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = build_synthetic_pipeline(root)
            with patch(
                "stage4b_u1_goldfree_controller.embed_texts",
                side_effect=AssertionError("embed_texts must not run"),
            ) as embed_mock, patch(
                "stage4b_u1_goldfree_controller.np.savez_compressed",
                side_effect=AssertionError("cache writes must not run"),
            ) as save_mock, patch.object(
                Path,
                "mkdir",
                side_effect=AssertionError("Path.mkdir must not run"),
            ) as mkdir_mock:
                outputs = run_require_existing_synthetic_controller(
                    paths, root, suffix="-valid"
                )
            embed_mock.assert_not_called()
            save_mock.assert_not_called()
            mkdir_mock.assert_not_called()
            self.assertTrue(all(path.is_file() for path in outputs.values()))
            self.assertEqual(
                load_json(outputs["policy"])["implementation_checkpoint"],
                IMPLEMENTATION_CHECKPOINT,
            )

    def test_require_existing_missing_cache_fails_before_outputs_or_embedding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = build_synthetic_pipeline(root)
            missing = root / "missing-cache.npz"
            outputs = require_existing_output_paths(root, "-missing")
            with patch(
                "stage4b_u1_goldfree_controller.embed_texts",
                side_effect=AssertionError("embed_texts must not run"),
            ) as embed_mock, self.assertRaisesRegex(ValueError, "not a regular file"):
                run_require_existing_synthetic_controller(
                    paths,
                    root,
                    cache_path=missing,
                    expected_sha256="0" * 64,
                    suffix="-missing",
                )
            embed_mock.assert_not_called()
            self.assertFalse(any(path.exists() for path in outputs.values()))

    def test_require_existing_wrong_sha_fails_before_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = build_synthetic_pipeline(root)
            outputs = require_existing_output_paths(root, "-sha")
            with self.assertRaisesRegex(ValueError, "SHA-256 differs"):
                run_require_existing_synthetic_controller(
                    paths, root, expected_sha256="0" * 64, suffix="-sha"
                )
            self.assertFalse(any(path.exists() for path in outputs.values()))

    def test_require_existing_member_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = build_synthetic_pipeline(root)
            changed_cache = root / "member-drift.npz"
            payload = cache_payload(paths["cache"])
            payload["unexpected"] = np.asarray([1], dtype="int64")
            write_cache_payload(changed_cache, payload)
            with self.assertRaisesRegex(ValueError, "exact frozen six"):
                run_require_existing_synthetic_controller(
                    paths, root, cache_path=changed_cache, suffix="-members"
                )

    def test_require_existing_id_order_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = build_synthetic_pipeline(root)
            original = cache_payload(paths["cache"])
            for field, message in (
                ("unit_ids", "unit order differs"),
                ("query_ids", "query order differs"),
            ):
                with self.subTest(field=field):
                    changed_cache = root / f"{field}-order-drift.npz"
                    payload = {
                        key: np.array(value, copy=True)
                        for key, value in original.items()
                    }
                    payload[field] = payload[field][::-1]
                    write_cache_payload(changed_cache, payload)
                    with self.assertRaisesRegex(ValueError, message):
                        run_require_existing_synthetic_controller(
                            paths,
                            root,
                            cache_path=changed_cache,
                            suffix=f"-{field}",
                        )

    def test_require_existing_metadata_and_array_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = build_synthetic_pipeline(root)
            original = cache_payload(paths["cache"])
            cases = (
                "model",
                "max_length",
                "dtype",
                "shape",
                "nonfinite",
                "normalization",
            )
            for case in cases:
                with self.subTest(case=case):
                    payload = {
                        key: np.array(value, copy=True) for key, value in original.items()
                    }
                    if case == "model":
                        payload["model_name"] = np.asarray(["wrong-model"])
                    elif case == "max_length":
                        payload["max_length"] = np.asarray([191], dtype="int64")
                    elif case == "dtype":
                        payload["unit_embeddings"] = payload["unit_embeddings"].astype(
                            "float64"
                        )
                    elif case == "shape":
                        payload["unit_embeddings"] = payload["unit_embeddings"][:-1]
                    elif case == "nonfinite":
                        payload["unit_embeddings"][0, 0] = np.nan
                    elif case == "normalization":
                        payload["unit_embeddings"][0] *= 2.0
                    changed_cache = root / f"{case}-drift.npz"
                    write_cache_payload(changed_cache, payload)
                    with self.assertRaises(ValueError):
                        run_require_existing_synthetic_controller(
                            paths,
                            root,
                            cache_path=changed_cache,
                            suffix=f"-{case}",
                        )

    def test_require_existing_byte_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = build_synthetic_pipeline(root)
            changed_cache = root / "byte-drift.npz"
            changed_cache.write_bytes(paths["cache"].read_bytes() + b"drift")
            outputs = require_existing_output_paths(root, "-bytes")
            with self.assertRaises(ValueError):
                run_require_existing_synthetic_controller(
                    paths,
                    root,
                    cache_path=changed_cache,
                    expected_sha256=sha256_file(paths["cache"]),
                    suffix="-bytes",
                )
            self.assertFalse(any(path.exists() for path in outputs.values()))

    def test_post_fingerprint_drift_prevents_output_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = build_synthetic_pipeline(root)
            outputs = require_existing_output_paths(root, "-post")
            original_builder = controller_module.build_query_decisions

            def mutate_cache_after_computation(*args: object, **kwargs: object) -> list[dict]:
                rows = original_builder(*args, **kwargs)
                with paths["cache"].open("ab") as stream:
                    stream.write(b"post-fingerprint-drift")
                return rows

            with patch(
                "stage4b_u1_goldfree_controller.build_query_decisions",
                side_effect=mutate_cache_after_computation,
            ), patch(
                "stage4b_u1_goldfree_controller.embed_texts",
                side_effect=AssertionError("embed_texts must not run"),
            ) as embed_mock, self.assertRaises(ValueError):
                run_require_existing_synthetic_controller(
                    paths, root, suffix="-post"
                )
            embed_mock.assert_not_called()
            self.assertFalse(any(path.exists() for path in outputs.values()))

    def test_formal_controller_rejects_load_or_build_mode_before_input_reads(self) -> None:
        with self.assertRaisesRegex(ValueError, "existing-cache-only mode"):
            run_controller(
                units_path=Path("missing-units"),
                queries_path=Path("missing-queries"),
                channel_audit_path=Path("missing-audit"),
                embedding_cache=Path("missing-cache"),
                decisions_output=Path("missing-decisions"),
                rankings_output=Path("missing-rankings"),
                policy_output=Path("missing-policy"),
                mode="development",
                policy_input=None,
                model_name=FROZEN_MODEL_NAME,
                batch_size=FROZEN_BATCH_SIZE,
                max_length=FROZEN_MAX_LENGTH,
                config=RetrievalConfig(),
                controller_source=SCRIPTS / "stage4b_u1_goldfree_controller.py",
                source_audit_path=None,
                synthetic_test_mode=False,
            )

    def test_policy_equivalence_allows_only_registered_binding_drift(self) -> None:
        reference = {
            "implementation_checkpoint": "old",
            "git_commit_sha": "old-commit",
            "protocol_sha256": "old-protocol",
            "implementation_hashes": {
                "common_source_sha256": "old-common",
                "controller_source_sha256": "old-controller",
                "verifier_source_sha256": "old-verifier",
                "retrieval_source_sha256": "same-retrieval",
            },
            "controller_source_sha256": "old-controller",
            "input_hashes": {
                "channel_audit": "old-channel",
                "embedding_cache": "same-cache",
            },
            "stable": {"score": "same"},
        }
        current = copy.deepcopy(reference)
        current["implementation_checkpoint"] = "new"
        current["git_commit_sha"] = "new-commit"
        current["protocol_sha256"] = "new-protocol"
        current["implementation_hashes"]["common_source_sha256"] = "new-common"
        current["implementation_hashes"]["controller_source_sha256"] = "new-controller"
        current["implementation_hashes"]["verifier_source_sha256"] = "new-verifier"
        current["controller_source_sha256"] = "new-controller"
        current["input_hashes"]["channel_audit"] = "new-channel"
        validate_policy_equivalence(current, reference)
        current["stable"]["score"] = "changed"
        with self.assertRaisesRegex(ValueError, "outside the registered"):
            validate_policy_equivalence(current, reference)

    def test_partial_promotion_failure_rolls_back_current_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pending = root / "pending.json"
            target = root / "target.json"
            pending.write_bytes(b"complete-pending-output")

            def fail_after_partial_copy(
                source: object, destination: object, length: int
            ) -> None:
                del length
                destination.write(source.read(4))
                raise OSError("synthetic copy failure")

            with patch(
                "stage4b_u1_goldfree_controller.shutil.copyfileobj",
                side_effect=fail_after_partial_copy,
            ), self.assertRaisesRegex(OSError, "synthetic copy failure"):
                promote_pending_outputs([(pending, target)])
            self.assertFalse(target.exists())

    def test_registered_governance_binding_is_hashed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            allowed = root / "docs" / "allowed.md"
            allowed.parent.mkdir()
            allowed.write_text("approved\n", encoding="utf-8")
            result = validate_governance_bindings(
                root,
                ["docs/allowed.md"],
                allowed_paths=frozenset({"docs/allowed.md"}),
                require_committed=False,
            )
            self.assertEqual(result, {"docs/allowed.md": sha256_file(allowed)})

    def test_missing_governance_binding_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "is missing"):
                validate_governance_bindings(
                    Path(directory),
                    ["docs/missing.md"],
                    allowed_paths=frozenset({"docs/missing.md"}),
                    require_committed=False,
                )

    def test_outside_repository_governance_binding_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            outside = Path(directory) / "outside.md"
            outside.write_text("outside\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "outside the repository"):
                validate_governance_bindings(
                    root,
                    ["../outside.md"],
                    allowed_paths=frozenset({"../outside.md"}),
                    require_committed=False,
                )

    def test_duplicate_governance_binding_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            allowed = root / "docs" / "allowed.md"
            allowed.parent.mkdir()
            allowed.write_text("approved\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate governance binding"):
                validate_governance_bindings(
                    root,
                    ["docs/allowed.md", "docs/allowed.md"],
                    allowed_paths=frozenset({"docs/allowed.md"}),
                    require_committed=False,
                )

    def test_unregistered_governance_binding_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            unregistered = root / "docs" / "unregistered.md"
            unregistered.parent.mkdir()
            unregistered.write_text("not registered\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Unregistered governance binding"):
                validate_governance_bindings(
                    root,
                    ["docs/unregistered.md"],
                    allowed_paths=frozenset({"docs/allowed.md"}),
                    require_committed=False,
                )

    def test_manifest_artifact_registry_matches_shared_constants(self) -> None:
        manifest = load_json(
            REPO_ROOT / "docs" / "STAGE4B_U1_PREGOLD_AMENDMENT_4_MANIFEST.json"
        )
        self.assertEqual(len(manifest["artifact_registry"]), 10)
        self.assertEqual(
            manifest["artifact_registry"], OFFICIAL_V2_3_1_ARTIFACT_PATHS
        )


class Stage4BU1HardeningTests(unittest.TestCase):
    def test_official_channel_omitting_source_audit_hard_fails(self) -> None:
        units, queries, _, _ = synthetic_labeled_rows()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            labeled_units = root / "units.jsonl"
            labeled_queries = root / "queries.jsonl"
            write_jsonl(labeled_units, units)
            write_jsonl(labeled_queries, queries)
            result = command(
                SCRIPTS / "stage4b_u1_prepare_channels.py",
                "--labeled-units", labeled_units,
                "--labeled-queries", labeled_queries,
                "--unlabeled-units-output", root / "u.jsonl",
                "--unlabeled-queries-output", root / "q.jsonl",
                "--gold-map-output", root / "g.json",
                "--controller-audit-output", root / "c.json",
                "--evaluator-audit-output", root / "e.json",
                "--mode", "development",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("requires --source-audit", result.stderr)

    def test_wrong_development_digest_hard_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            queries = formal_query_rows()
            sample_digest = id_digest(str(row["sample_id"]) for row in queries)
            query_digest = id_digest(str(row["query_id"]) for row in queries)
            audit = Path(directory) / "bad_source_audit.json"
            write_json(
                audit,
                {"data_boundary": {"development_queries": 4, "development_query_id_sha256": "BAD"}},
            )
            with patch(
                "stage4b_u1_prepare_channels.STAGE4A_R2_SOURCE_AUDIT_SHA256",
                sha256_file(audit),
            ), patch(
                "stage4b_u1_prepare_channels.OFFICIAL_DEVELOPMENT_QUERIES", 4
            ), patch(
                "stage4b_u1_prepare_channels.OFFICIAL_DEVELOPMENT_SAMPLE_ID_SHA256",
                sample_digest,
            ), patch(
                "stage4b_u1_prepare_channels.OFFICIAL_DEVELOPMENT_QUERY_ID_SHA256",
                query_digest,
            ):
                with self.assertRaisesRegex(ValueError, "sample-ID digest differs"):
                    validate_execution_boundary(
                        mode="development",
                        queries=queries,
                        source_audit_path=audit,
                        synthetic_test_mode=False,
                    )

    def test_wrong_formal_sample_id_digest_hard_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            queries = formal_query_rows()
            sample_digest = id_digest(str(row["sample_id"]) for row in queries)
            query_digest = id_digest(str(row["query_id"]) for row in queries)
            audit = Path(directory) / "source_audit.json"
            write_json(
                audit,
                {
                    "data_boundary": {
                        "development_queries": 4,
                        "development_query_id_sha256": sample_digest,
                    }
                },
            )
            changed = copy.deepcopy(queries)
            changed[0]["sample_id"] = "changed-sample"
            changed[0]["query_id"] = "2wikimultihopqa::changed-sample"
            with patch(
                "stage4b_u1_prepare_channels.STAGE4A_R2_SOURCE_AUDIT_SHA256",
                sha256_file(audit),
            ), patch(
                "stage4b_u1_prepare_channels.OFFICIAL_DEVELOPMENT_QUERIES", 4
            ), patch(
                "stage4b_u1_prepare_channels.OFFICIAL_DEVELOPMENT_SAMPLE_ID_SHA256",
                sample_digest,
            ), patch(
                "stage4b_u1_prepare_channels.OFFICIAL_DEVELOPMENT_QUERY_ID_SHA256",
                query_digest,
            ):
                with self.assertRaisesRegex(ValueError, "sample IDs differ"):
                    validate_execution_boundary(
                        mode="development",
                        queries=changed,
                        source_audit_path=audit,
                        synthetic_test_mode=False,
                    )

    def test_wrong_formal_runtime_query_id_digest_hard_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            queries = formal_query_rows()
            sample_digest = id_digest(str(row["sample_id"]) for row in queries)
            audit = Path(directory) / "source_audit.json"
            write_json(
                audit,
                {
                    "data_boundary": {
                        "development_queries": 4,
                        "development_query_id_sha256": sample_digest,
                    }
                },
            )
            with patch(
                "stage4b_u1_prepare_channels.STAGE4A_R2_SOURCE_AUDIT_SHA256",
                sha256_file(audit),
            ), patch(
                "stage4b_u1_prepare_channels.OFFICIAL_DEVELOPMENT_QUERIES", 4
            ), patch(
                "stage4b_u1_prepare_channels.OFFICIAL_DEVELOPMENT_SAMPLE_ID_SHA256",
                sample_digest,
            ), patch(
                "stage4b_u1_prepare_channels.OFFICIAL_DEVELOPMENT_QUERY_ID_SHA256",
                "F" * 64,
            ):
                with self.assertRaisesRegex(ValueError, "runtime query-ID digest differs"):
                    validate_execution_boundary(
                        mode="development",
                        queries=queries,
                        source_audit_path=audit,
                        synthetic_test_mode=False,
                    )

    def test_malformed_query_namespace_relation_hard_fails(self) -> None:
        queries = formal_query_rows()
        queries[0]["query_id"] = "wrong-namespace::q0"
        with self.assertRaisesRegex(ValueError, "does not equal dataset::sample_id"):
            validate_execution_boundary(
                mode="development",
                queries=queries,
                source_audit_path=Path("not-reached"),
                synthetic_test_mode=False,
            )

    def test_controller_audit_dual_digest_drift_hard_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = build_synthetic_pipeline(Path(directory))
            original = load_json(paths["channel"])
            for field, message in (
                ("sample_id_sha256", "sample digest differs"),
                ("query_id_sha256", "query digest differs"),
            ):
                changed = copy.deepcopy(original)
                changed[field] = "0" * 64
                write_json(paths["channel"], changed)
                with self.assertRaisesRegex(ValueError, message):
                    run_controller(
                        units_path=paths["units"],
                        queries_path=paths["queries"],
                        channel_audit_path=paths["channel"],
                        embedding_cache=paths["cache"],
                        decisions_output=Path(directory) / f"controller-{field}.jsonl",
                        rankings_output=Path(directory) / f"rankings-{field}.jsonl",
                        policy_output=Path(directory) / f"policy-{field}.json",
                        mode="development",
                        policy_input=None,
                        model_name="synthetic-model",
                        batch_size=FROZEN_BATCH_SIZE,
                        max_length=FROZEN_MAX_LENGTH,
                        config=RetrievalConfig(),
                        controller_source=SCRIPTS / "stage4b_u1_goldfree_controller.py",
                        source_audit_path=None,
                        synthetic_test_mode=True,
                    )
                with self.assertRaisesRegex(ValueError, message):
                    run_synthetic_verifier(paths, Path(directory) / f"bad-{field}.json")
            write_json(paths["channel"], original)

    def test_wrong_formal_model_name_hard_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "encoder differs"):
            run_controller(
                units_path=Path("missing"), queries_path=Path("missing"),
                channel_audit_path=Path("missing"), embedding_cache=Path("missing"),
                decisions_output=Path("missing"), rankings_output=Path("missing"),
                policy_output=Path("missing"), mode="development", policy_input=None,
                model_name="wrong-model", batch_size=FROZEN_BATCH_SIZE,
                max_length=FROZEN_MAX_LENGTH, config=RetrievalConfig(),
                controller_source=SCRIPTS / "stage4b_u1_goldfree_controller.py",
                source_audit_path=None, synthetic_test_mode=False,
            )

    def test_wrong_formal_max_length_hard_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "max length differs"):
            run_controller(
                units_path=Path("missing"), queries_path=Path("missing"),
                channel_audit_path=Path("missing"), embedding_cache=Path("missing"),
                decisions_output=Path("missing"), rankings_output=Path("missing"),
                policy_output=Path("missing"), mode="development", policy_input=None,
                model_name=FROZEN_MODEL_NAME, batch_size=FROZEN_BATCH_SIZE,
                max_length=191, config=RetrievalConfig(),
                controller_source=SCRIPTS / "stage4b_u1_goldfree_controller.py",
                source_audit_path=None, synthetic_test_mode=False,
            )

    def test_modified_tie_hash_rejected_after_output_hash_refresh(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = build_synthetic_pipeline(Path(directory))
            rows = load_jsonl(paths["decisions"])
            rows[0]["tie_hash"] = "0" * 64
            write_jsonl(paths["decisions"], rows)
            refresh_policy_output_hash(paths, "decisions")
            with self.assertRaisesRegex(ValueError, "tie hash differs"):
                run_synthetic_verifier(paths, Path(directory) / "bad.json")

    def test_modified_score_rejected_after_internal_hash_refresh(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = build_synthetic_pipeline(Path(directory))
            rows = load_jsonl(paths["decisions"])
            rows[0]["score"] = float(rows[0]["score"]) + 1e-6
            write_jsonl(paths["decisions"], rows)
            refresh_policy_output_hash(paths, "decisions")
            with self.assertRaisesRegex(ValueError, "recomputed score differs"):
                run_synthetic_verifier(paths, Path(directory) / "bad.json")

    def test_modified_ecdf_reference_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = build_synthetic_pipeline(Path(directory))
            policy_data = load_json(paths["policy"])
            values = policy_data["ecdf_references"]["ball_score_margin"]
            values[-1] = float(values[-1]) + 1e-6
            write_json(paths["policy"], policy_data)
            with self.assertRaisesRegex(ValueError, "ECDF references differ"):
                run_synthetic_verifier(paths, Path(directory) / "bad.json")

    def test_modified_q25_and_final_ranking_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = build_synthetic_pipeline(Path(directory))
            rows = load_jsonl(paths["rankings"])
            target = next(row for row in rows if int(row["trigger_u1"]) == 1)
            target["q25_top20_unit_ids"][10], target["q25_top20_unit_ids"][11] = (
                target["q25_top20_unit_ids"][11], target["q25_top20_unit_ids"][10]
            )
            target["final_top20_unit_ids"] = list(target["q25_top20_unit_ids"])
            write_jsonl(paths["rankings"], rows)
            refresh_policy_output_hash(paths, "rankings")
            with self.assertRaisesRegex(ValueError, "inserted IDs differ from effective-K structure"):
                run_synthetic_verifier(paths, Path(directory) / "bad.json")

    def test_modified_inserted_list_rejected_when_top20_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = build_synthetic_pipeline(Path(directory))
            rows = load_jsonl(paths["rankings"])
            target = next(row for row in rows if int(row["trigger_u1"]) == 1)
            target["q25_inserted_unit_ids"] = list(reversed(target["q25_inserted_unit_ids"]))
            target["final_inserted_unit_ids"] = list(target["q25_inserted_unit_ids"])
            write_jsonl(paths["rankings"], rows)
            refresh_policy_output_hash(paths, "rankings")
            with self.assertRaisesRegex(ValueError, "inserted IDs differ from effective-K structure"):
                run_synthetic_verifier(paths, Path(directory) / "bad.json")

    def test_evaluator_without_pre_gold_verification_hard_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = build_synthetic_pipeline(Path(directory))
            result = command(
                SCRIPTS / "stage4b_u1_evaluate.py",
                "--rankings", paths["rankings"],
                "--policy", paths["policy"],
                "--gold-map", paths["gold"],
                "--evaluator-audit", paths["evaluator_channel"],
                "--stage4a-r2-verification", paths["baseline"],
                "--query-audit-output", Path(directory) / "audit.jsonl",
                "--summary-output", Path(directory) / "summary.json",
                "--run-role", "development",
                "--synthetic-test-mode",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--pre-gold-verification", result.stderr)

    def test_policy_implementation_hash_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = build_synthetic_pipeline(Path(directory))
            policy_data = load_json(paths["policy"])
            policy_data["implementation_hashes"]["common_source_sha256"] = "F" * 64
            write_json(paths["policy"], policy_data)
            with self.assertRaisesRegex(ValueError, "implementation file hash mismatch"):
                run_synthetic_verifier(paths, Path(directory) / "bad.json")

    def test_baseline_drift_stops_before_u1_summary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = build_synthetic_pipeline(Path(directory))
            reference = load_json(paths["baseline"])
            reference["expected"]["q25_gain_events"] += 1
            write_json(paths["baseline"], reference)
            with self.assertRaisesRegex(ValueError, "HARD_FAILURE_IMPLEMENTATION_DRIFT"):
                run_evaluation(
                    rankings_path=paths["rankings"], policy_path=paths["policy"],
                    pre_gold_verification_path=paths["pre_gold"], gold_map_path=paths["gold"],
                    evaluator_audit_path=paths["evaluator_channel"],
                    stage4a_r2_verification_path=paths["baseline"],
                    stage4a_r2_strategy_summary_path=None,
                    query_audit_output=Path(directory) / "audit.jsonl",
                    summary_output=Path(directory) / "summary.json", run_role="development",
                    bootstrap_iterations=0, bootstrap_seed=1,
                    evaluator_source=SCRIPTS / "stage4b_u1_evaluate.py",
                    synthetic_test_mode=True,
                )
            self.assertFalse((Path(directory) / "audit.jsonl").exists())
            self.assertFalse((Path(directory) / "summary.json").exists())


class Stage4BU1EndToEndTests(unittest.TestCase):
    def test_synthetic_reservation_reuses_development_ecdf(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = build_synthetic_pipeline(root)
            reservation_channel = root / "reservation_channel.json"
            reservation_channel_data = load_json(paths["channel"])
            reservation_channel_data["run_role"] = "reservation"
            write_json(reservation_channel, reservation_channel_data)
            reservation_decisions = root / "reservation_decisions.jsonl"
            reservation_rankings = root / "reservation_rankings.jsonl"
            reservation_policy = root / "reservation_policy.json"
            command(
                SCRIPTS / "stage4b_u1_goldfree_controller.py",
                "--units", paths["units"],
                "--queries", paths["queries"],
                "--channel-audit", reservation_channel,
                "--embedding-cache", paths["cache"],
                "--decisions-output", reservation_decisions,
                "--rankings-output", reservation_rankings,
                "--policy-output", reservation_policy,
                "--mode", "reservation",
                "--policy-input", paths["policy"],
                "--model-name", "synthetic-model",
                "--synthetic-test-mode",
            )
            development = load_json(paths["policy"])
            reservation = load_json(reservation_policy)
            self.assertEqual(
                reservation["parent_development_policy_sha256"],
                sha256_file(paths["policy"]),
            )
            self.assertEqual(reservation["ecdf_references"], development["ecdf_references"])

    def test_synthetic_pipeline_is_deterministic_pre_gold_verified_and_evaluable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = build_synthetic_pipeline(root, "_1")
            second = build_synthetic_pipeline(root, "_2")
            for key in ("decisions", "rankings", "policy", "pre_gold"):
                self.assertEqual(sha256_file(first[key]), sha256_file(second[key]))
            channel_text = json.dumps(load_json(first["channel"]), sort_keys=True).lower()
            self.assertNotIn("gold_map", channel_text)
            policy = load_json(first["policy"])
            self.assertEqual(policy["allocation"]["allquery_planned_inserts"], 16)
            self.assertEqual(policy["allocation"]["budget_units"], 9)
            self.assertEqual(policy["allocation"]["selected_planned_inserts"], 8)
            pre_gold = load_json(first["pre_gold"])
            self.assertEqual(pre_gold["status"], "VERIFIED_PRE_GOLD")
            self.assertIsNone(pre_gold["evaluation"])

            query_audit = root / "query_audit.jsonl"
            summary_path = root / "summary.json"
            summary = run_evaluation(
                rankings_path=first["rankings"], policy_path=first["policy"],
                pre_gold_verification_path=first["pre_gold"], gold_map_path=first["gold"],
                evaluator_audit_path=first["evaluator_channel"],
                stage4a_r2_verification_path=first["baseline"],
                stage4a_r2_strategy_summary_path=None,
                query_audit_output=query_audit, summary_output=summary_path,
                run_role="development", bootstrap_iterations=40, bootstrap_seed=20260712,
                evaluator_source=SCRIPTS / "stage4b_u1_evaluate.py",
                synthetic_test_mode=True,
            )
            self.assertTrue(summary["baseline_equivalence"]["passed"])
            post = run_verification(
                units_path=first["units"], queries_path=first["queries"],
                channel_audit_path=first["channel"], embedding_cache_path=first["cache"],
                decisions_path=first["decisions"], rankings_path=first["rankings"],
                policy_path=first["policy"],
                controller_source=SCRIPTS / "stage4b_u1_goldfree_controller.py",
                source_audit_path=None, gold_map_path=first["gold"],
                evaluator_audit_path=first["evaluator_channel"],
                query_audit_path=query_audit, summary_path=summary_path,
                output_path=root / "post.json", synthetic_test_mode=True,
            )
            self.assertEqual(post["status"], "VERIFIED_POST_GOLD")
            self.assertTrue(post["policy_and_ranking"]["independent_score_recomputation_check"])


if __name__ == "__main__":
    unittest.main()
