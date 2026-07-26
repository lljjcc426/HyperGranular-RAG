from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from stage6a_smc_common import (  # noqa: E402
    BASELINE_METHOD,
    HGRAG_FAMILY,
    config_method,
    development_methods,
    parse_method,
    selection_key,
)
from stage6a_smc_independent_retrieval import (  # noqa: E402
    independent_query_rankings,
)
from stage6a_smc_prepare import build_twowiki_channels  # noqa: E402
from stage6a_smc_retrieval import (  # noqa: E402
    PROTECTED_PREFIX,
    build_query_rankings,
    build_units_queries,
    hierarchical_groups,
    spherical_kmeans_groups,
)


def synthetic_context(count: int = 30):
    query_id = "synthetic::q1"
    units = []
    for index in range(count):
        units.append(
            {
                "dataset": "synthetic",
                "document_id": f"{query_id}::p{index // 3}",
                "paragraph_index": index // 3,
                "query_id": query_id,
                "sample_id": "q1",
                "sentence_index": index % 3,
                "text": (
                    f"alpha bridge evidence {index}"
                    if index % 2 == 0
                    else f"beta relation detail {index}"
                ),
                "title": f"Document {index // 3}",
                "unit_id": f"{query_id}::p{index // 3}::s{index % 3}",
            }
        )
    rng = np.random.default_rng(17)
    embeddings = rng.normal(size=(count, 16)).astype("float32")
    embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
    query_embedding = rng.normal(size=(16,)).astype("float32")
    query_embedding /= np.linalg.norm(query_embedding)
    query = {
        "dataset": "synthetic",
        "question": "Which alpha bridge connects beta evidence?",
        "query_id": query_id,
        "sample_id": "q1",
    }
    scores = np.linspace(0.98, 0.05, count, dtype="float32").tolist()
    return query, units, embeddings, query_embedding, scores


def test_frozen_method_family_is_complete_and_canonical():
    methods = development_methods()
    assert len(methods) == 21
    assert methods[0] == BASELINE_METHOD
    assert len(set(methods)) == len(methods)
    method = config_method(HGRAG_FAMILY, 0.85, 6)
    assert parse_method(method) == (HGRAG_FAMILY, 0.85, 6)


def test_selection_key_binds_source_row_without_gold():
    first = selection_key("hotpotqa", "native-id", 12)
    second = selection_key("hotpotqa", "native-id", 13)
    assert first != second
    assert first[1] == second[1] == "native-id"
    with pytest.raises(ValueError):
        selection_key("hotpotqa", "native-id", True)


def test_matched_cluster_controls_have_requested_group_count():
    _, units, embeddings, _, _ = synthetic_context()
    pool = list(range(len(units)))
    spherical = spherical_kmeans_groups(pool, units, embeddings, 7)
    hierarchical = hierarchical_groups(pool, units, embeddings, 7)
    assert len(set(spherical.values())) == 7
    assert len(set(hierarchical.values())) == 7
    assert set(spherical) == set(hierarchical) == set(pool)


def test_production_and_independent_selectors_match_all_frozen_methods():
    query, units, embeddings, query_embedding, scores = synthetic_context()
    methods = development_methods()
    production, trace = build_query_rankings(
        query,
        0,
        list(range(len(units))),
        units,
        embeddings,
        np.asarray([query_embedding], dtype="float32"),
        list(range(len(units))),
        scores,
        methods,
    )
    independent = independent_query_rankings(
        query,
        list(range(len(units))),
        scores,
        units,
        embeddings,
        methods,
    )
    assert production == independent
    assert set(production) == set(methods)
    baseline_prefix = production[BASELINE_METHOD][:PROTECTED_PREFIX]
    for method, ranking in production.items():
        assert len(ranking) == 20
        assert len(ranking) == len(set(ranking))
        if method != BASELINE_METHOD:
            assert ranking[:PROTECTED_PREFIX] == baseline_prefix
    assert trace["common_pool_size"] == len(units)


def test_twowiki_channel_maps_supporting_sentence_and_keeps_metadata_sealed():
    row = {
        "_id": "abc123",
        "answer": "Answer",
        "context": [
            ["Alpha", ["First sentence.", "Supporting sentence."]],
            ["Beta", ["Other evidence."]],
        ],
        "evidences": [["Alpha", "relation", "Beta"]],
        "question": "What is supported?",
        "supporting_facts": [["Alpha", 1]],
        "type": "inference",
    }
    blind, gold, metadata = build_twowiki_channels(10000, "abc123", row)
    assert blind["query_id"] == "2wikimultihopqa_official_dev::abc123"
    assert "answer" not in blind
    assert "type" not in blind
    assert gold["supporting_unit_ids"] == [
        "2wikimultihopqa_official_dev::abc123::p0::s1"
    ]
    assert metadata["source_row_index"] == 10000


def test_twowiki_channel_rejects_unmappable_support():
    row = {
        "_id": "abc123",
        "answer": "Answer",
        "context": [["Alpha", ["Only sentence."]]],
        "evidences": [],
        "question": "What is supported?",
        "supporting_facts": [["Missing", 0]],
        "type": "inference",
    }
    with pytest.raises(ValueError):
        build_twowiki_channels(10000, "abc123", row)


def test_twowiki_duplicate_title_uses_frozen_first_context_mapping():
    row = {
        "_id": "abc123",
        "answer": "Answer",
        "context": [
            ["Alpha", ["Official supporting sentence."]],
            ["Alpha", ["Duplicate-title distractor."]],
        ],
        "evidences": [],
        "question": "What is supported?",
        "supporting_facts": [["Alpha", 0]],
        "type": "inference",
    }
    blind, gold, _ = build_twowiki_channels(10000, "abc123", row)
    assert len(blind["candidate_units"]) == 2
    assert gold["supporting_unit_ids"] == [
        "2wikimultihopqa_official_dev::abc123::p0::s0"
    ]


def test_stage6_flatten_contract_accepts_twowiki_dataset():
    row = {
        "_id": "abc123",
        "answer": "Answer",
        "context": [["Alpha", ["Official supporting sentence."]]],
        "evidences": [],
        "question": "What is supported?",
        "supporting_facts": [["Alpha", 0]],
        "type": "inference",
    }
    blind, _, _ = build_twowiki_channels(10000, "abc123", row)
    units, queries = build_units_queries([blind])
    assert len(units) == 1
    assert queries == [
        {
            "dataset": "2wikimultihopqa_official_dev",
            "num_candidate_units": 1,
            "query_id": "2wikimultihopqa_official_dev::abc123",
            "question": "What is supported?",
            "sample_id": "abc123",
        }
    ]
