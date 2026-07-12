from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from stage4b_u1_common import (  # noqa: E402
    assert_no_prohibited_keys,
    id_digest,
    load_json,
    load_jsonl,
    sha256_file,
    write_jsonl,
)
from stage4b_u1_goldfree_retrieval import (  # noqa: E402
    RetrievalConfig,
    allocate_budget,
    decision_from_balls,
    ecdf_midrank,
    expansion_candidates_goldfree,
    fixed_retrieve_goldfree,
    protected_rerank_goldfree,
)
from stage4b_u1_goldfree_controller import validate_controller_inputs  # noqa: E402
from stage4b_u1_prepare_channels import prepare_channels  # noqa: E402
from stage4b_u1_verify import (  # noqa: E402
    verify_policy_and_rankings,
)
from stage2_dense_replication import fixed_retrieve as legacy_fixed_retrieve  # noqa: E402
from stage2d_protected_rerank import (  # noqa: E402
    expansion_candidates as legacy_expansion_candidates,
    protected_rerank as legacy_protected_rerank,
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


class Stage4BU1GoldFreeTests(unittest.TestCase):
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
        ball = {
            "ball_id": "only",
            "center": normalized([1.0, 0.0]),
            "radius": 0.0,
        }
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
            {
                "query_id": "a",
                "feasible": 1,
                "score": 3.0,
                "tie_hash": "A",
                "planned_insert_count": 4,
                "q25_top20_unit_ids": ["a"],
                "dense_top20_unit_ids": ["d-a"],
                "q25_inserted_unit_ids": ["1", "2", "3", "4"],
            },
            {
                "query_id": "b",
                "feasible": 1,
                "score": 2.0,
                "tie_hash": "B",
                "planned_insert_count": 4,
                "q25_top20_unit_ids": ["b"],
                "dense_top20_unit_ids": ["d-b"],
                "q25_inserted_unit_ids": ["5", "6", "7", "8"],
            },
            {
                "query_id": "c",
                "feasible": 1,
                "score": 1.0,
                "tie_hash": "C",
                "planned_insert_count": 1,
                "q25_top20_unit_ids": ["c"],
                "dense_top20_unit_ids": ["d-c"],
                "q25_inserted_unit_ids": ["9"],
            },
        ]
        allocation = allocate_budget(rows)
        self.assertEqual(allocation["budget_units"], 5)
        self.assertEqual(allocation["selected_queries"], 1)
        self.assertEqual([row["trigger_u1"] for row in rows], [1, 0, 0])

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
            query,
            query_embedding,
            candidate_indices,
            units,
            unit_embeddings,
            args,
            "gated",
        )
        goldfree_expanded, goldfree_selected, _ = expansion_candidates_goldfree(
            query,
            query_embedding,
            candidate_indices,
            units,
            unit_embeddings,
            config,
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
            legacy_dense,
            legacy_filtered,
            config.protect_n,
            config.insert_budget,
            config.max_k,
        )
        goldfree_q25, goldfree_inserted = protected_rerank_goldfree(
            goldfree_dense,
            goldfree_filtered,
            config.protect_n,
            config.insert_budget,
            config.max_k,
        )
        self.assertEqual(
            [row["unit_id"] for row in legacy_q25],
            [row["unit_id"] for row in goldfree_q25],
        )
        self.assertEqual(legacy_insert["inserted_units"], len(goldfree_inserted))

    def test_synthetic_pipeline_is_gold_free_deterministic_and_verified(self) -> None:
        units, queries, unit_embeddings, query_embeddings = synthetic_labeled_rows()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            labeled_units = root / "labeled_units.jsonl"
            labeled_queries = root / "labeled_queries.jsonl"
            unlabeled_units = root / "unlabeled_units.jsonl"
            unlabeled_queries = root / "unlabeled_queries.jsonl"
            gold_map_path = root / "gold_map.json"
            channel_audit_path = root / "channel_audit.json"
            evaluator_audit_path = root / "evaluator_audit.json"
            cache_path = root / "embeddings.npz"
            write_jsonl(labeled_units, units)
            write_jsonl(labeled_queries, queries)
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "stage4b_u1_prepare_channels.py"),
                    "--labeled-units",
                    str(labeled_units),
                    "--labeled-queries",
                    str(labeled_queries),
                    "--unlabeled-units-output",
                    str(unlabeled_units),
                    "--unlabeled-queries-output",
                    str(unlabeled_queries),
                    "--gold-map-output",
                    str(gold_map_path),
                    "--controller-audit-output",
                    str(channel_audit_path),
                    "--evaluator-audit-output",
                    str(evaluator_audit_path),
                    "--expected-query-id-sha256",
                    id_digest(row["query_id"] for row in queries),
                ],
                check=True,
                cwd=REPO_ROOT,
            )
            split_units = load_jsonl(unlabeled_units)
            split_queries = load_jsonl(unlabeled_queries)
            self.assertNotIn(
                "gold", json.dumps(load_json(channel_audit_path), sort_keys=True).lower()
            )
            np.savez_compressed(
                cache_path,
                unit_embeddings=unit_embeddings,
                query_embeddings=query_embeddings,
                unit_ids=np.asarray([row["unit_id"] for row in split_units]),
                query_ids=np.asarray([row["query_id"] for row in split_queries]),
                model_name=np.asarray(["synthetic-model"]),
                max_length=np.asarray([192], dtype="int64"),
            )
            outputs = []
            for run in (1, 2):
                decisions = root / f"decisions_{run}.jsonl"
                rankings = root / f"rankings_{run}.jsonl"
                policy = root / f"policy_{run}.json"
                subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPTS / "stage4b_u1_goldfree_controller.py"),
                        "--units",
                        str(unlabeled_units),
                        "--queries",
                        str(unlabeled_queries),
                        "--channel-audit",
                        str(channel_audit_path),
                        "--embedding-cache",
                        str(cache_path),
                        "--decisions-output",
                        str(decisions),
                        "--rankings-output",
                        str(rankings),
                        "--policy-output",
                        str(policy),
                        "--mode",
                        "development",
                        "--model-name",
                        "synthetic-model",
                        "--synthetic-test-mode",
                    ],
                    check=True,
                    cwd=REPO_ROOT,
                )
                outputs.append((decisions, rankings, policy))
            for index in range(3):
                self.assertEqual(
                    sha256_file(outputs[0][index]), sha256_file(outputs[1][index])
                )

            decisions_path, rankings_path, policy_path = outputs[0]
            policy = load_json(policy_path)
            self.assertEqual(policy["allocation"]["allquery_planned_inserts"], 16)
            self.assertEqual(policy["allocation"]["budget_units"], 9)
            self.assertEqual(policy["allocation"]["selected_planned_inserts"], 8)
            self.assertGreaterEqual(
                1.0
                - policy["allocation"]["selected_planned_inserts"]
                / policy["allocation"]["allquery_planned_inserts"],
                0.40,
            )

            reservation_decisions = root / "reservation_decisions.jsonl"
            reservation_rankings = root / "reservation_rankings.jsonl"
            reservation_policy = root / "reservation_policy.json"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "stage4b_u1_goldfree_controller.py"),
                    "--units",
                    str(unlabeled_units),
                    "--queries",
                    str(unlabeled_queries),
                    "--channel-audit",
                    str(channel_audit_path),
                    "--embedding-cache",
                    str(cache_path),
                    "--decisions-output",
                    str(reservation_decisions),
                    "--rankings-output",
                    str(reservation_rankings),
                    "--policy-output",
                    str(reservation_policy),
                    "--mode",
                    "reservation",
                    "--policy-input",
                    str(policy_path),
                    "--model-name",
                    "synthetic-model",
                    "--synthetic-test-mode",
                ],
                check=True,
                cwd=REPO_ROOT,
            )
            frozen_reservation_policy = load_json(reservation_policy)
            self.assertEqual(
                frozen_reservation_policy["parent_development_policy_sha256"],
                sha256_file(policy_path),
            )
            self.assertEqual(
                frozen_reservation_policy["ecdf_references"], policy["ecdf_references"]
            )

            query_audit = root / "query_audit.jsonl"
            summary_path = root / "summary.json"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "stage4b_u1_evaluate.py"),
                    "--rankings",
                    str(rankings_path),
                    "--policy",
                    str(policy_path),
                    "--gold-map",
                    str(gold_map_path),
                    "--evaluator-audit",
                    str(evaluator_audit_path),
                    "--query-audit-output",
                    str(query_audit),
                    "--summary-output",
                    str(summary_path),
                    "--run-role",
                    "development",
                    "--bootstrap-iterations",
                    "40",
                    "--synthetic-test-mode",
                ],
                check=True,
                cwd=REPO_ROOT,
            )
            verification_path = root / "verification.json"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "stage4b_u1_verify.py"),
                    "--units",
                    str(unlabeled_units),
                    "--queries",
                    str(unlabeled_queries),
                    "--channel-audit",
                    str(channel_audit_path),
                    "--decisions",
                    str(decisions_path),
                    "--rankings",
                    str(rankings_path),
                    "--policy",
                    str(policy_path),
                    "--controller-source",
                    str(SCRIPTS / "stage4b_u1_goldfree_controller.py"),
                    "--gold-map",
                    str(gold_map_path),
                    "--evaluator-audit",
                    str(evaluator_audit_path),
                    "--query-audit",
                    str(query_audit),
                    "--summary",
                    str(summary_path),
                    "--output",
                    str(verification_path),
                ],
                check=True,
                cwd=REPO_ROOT,
            )
            verification = load_json(verification_path)
            self.assertEqual(verification["status"], "VERIFIED")
            self.assertTrue(verification["policy_and_ranking"]["ranking_subset_check"])

            corrupted = copy.deepcopy(load_jsonl(rankings_path))
            first = corrupted[0]
            first["final_top20_unit_ids"] = list(reversed(first["final_top20_unit_ids"]))
            with self.assertRaisesRegex(ValueError, "on/off selector"):
                verify_policy_and_rankings(load_jsonl(decisions_path), corrupted, policy)


if __name__ == "__main__":
    unittest.main()
