"""Deterministic Stage4C-U1-FMA exploratory failure-mechanism audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


SCHEMA_VERSION = "stage4c_u1_fma_v1"
PROTOCOL_PATH = "docs/STAGE4C_U1_FAILURE_MECHANISM_AUDIT_PROTOCOL.md"
PROTOCOL_COMMIT = "2e925063175a6402a21ade3fc0ab4a27faaa6dd7"
PROTOCOL_SHA256 = "7F1C3F78BFA5C9D36A4EA318394E8E791476215AEBAA73DFEA1B40B6D5FDD383"
QUERY_COUNT = 4500
GAIN_COUNT = 94
HARM_COUNT = 69
RETAINED_GAIN_COUNT = 47
RETAINED_HARM_COUNT = 53
BOOTSTRAP_ITERATIONS = 10_000
BOOTSTRAP_SEED = 20_260_718
FOLDS = 5
LOGISTIC_L2 = 1.0
LOGISTIC_MAX_ITERATIONS = 100
LOGISTIC_TOLERANCE = 1e-8

INPUT_SPECS: dict[str, dict[str, Any]] = {
    "decisions": {
        "path": "results/stage4b_u1_d_official_dev4500_simplified_v1_decisions.jsonl",
        "bytes": 2_684_439,
        "sha256": "4B2AD2E5707B20FD46B6250FDA5395433F52E55FB1281F1499412C8C749A456A",
    },
    "rankings": {
        "path": "results/stage4b_u1_d_official_dev4500_simplified_v1_rankings.jsonl",
        "bytes": 18_235_604,
        "sha256": "ED289D234F6F4FEC58A48168CB6CA78950489CD5F5640E977068CA6A786E03CB",
    },
    "policy": {
        "path": "results/stage4b_u1_d_official_dev4500_simplified_v1_policy.json",
        "bytes": 261_587,
        "sha256": "657E5F25A94224D8B020780F3E7335942B16BC6D8C7939FB74D1BBAA9A9D868B",
    },
    "pre_gold": {
        "path": "results/stage4b_u1_d_official_dev4500_simplified_v1_verified_pre_gold.json",
        "bytes": 3_479,
        "sha256": "39EAD86A3A835983DCB67BAF656255F51569BCEE5B9AC2E16FACF404281D7818",
    },
    "query_audit": {
        "path": "results/stage4b_u1_d_official_dev4500_simplified_v1_query_audit.jsonl",
        "bytes": 2_600_121,
        "sha256": "8616C28C71D190E3287CCE3725EDC0B1FD0DFB41DF47C739F4A84A573F938313",
    },
    "gold_summary": {
        "path": "results/stage4b_u1_d_official_dev4500_simplified_v1_evaluation_summary.json",
        "bytes": 7_662,
        "sha256": "7F82056FB14F9D8D73E668A82CB5304B28385E62A01C428599F23260AB7F89DE",
    },
    "post_gold": {
        "path": "results/stage4b_u1_d_official_dev4500_simplified_v1_verified_post_gold.json",
        "bytes": 2_293,
        "sha256": "44BF3E8B0B036958633E237186A458B13090D8073F587657D831656FB7720ECD",
    },
}

OUTPUT_NAMES = {
    "query_features": "stage4c_u1_fma_query_features.csv",
    "feature_separability": "stage4c_u1_fma_feature_separability.csv",
    "score_deciles": "stage4c_u1_fma_score_deciles.csv",
    "candidate_mechanisms": "stage4c_u1_fma_candidate_mechanisms.csv",
    "oof_predictions": "stage4c_u1_fma_oof_predictions.csv",
    "summary": "stage4c_u1_fma_summary.json",
}

QUERY_FEATURES = [
    "ball_score_margin",
    "boundary_margin",
    "selected_edge_count",
    "planned_insert_count",
    "u_margin",
    "u_boundary",
    "r_edge",
    "r_candidate",
    "uncertainty",
    "readiness",
    "score",
    "ordered_rank",
]

ORIGINAL_PANEL = [
    "ball_score_margin",
    "boundary_margin",
    "selected_edge_count",
    "planned_insert_count",
    "uncertainty",
    "readiness",
    "score",
    "feasible",
]
RANK_PANEL = [
    "q25_eligible_count",
    "q25_insert_position_min",
    "q25_insert_position_mean",
    "q25_insert_position_max",
    "q25_inserted_dense20_overlap_count",
    "dense_q25_top20_jaccard",
]
FEATURE_PANELS = {
    "ORIGINAL_U1_8": ORIGINAL_PANEL,
    "RANK_STRUCTURE_6": RANK_PANEL,
    "COMBINED_14": ORIGINAL_PANEL + RANK_PANEL,
}

FORBIDDEN_PROBE_FEATURES = {
    "query_id",
    "sample_id",
    "dataset",
    "question_type",
    "label",
    "dense_cr20",
    "q25_cr20",
    "u1_cr20",
    "dense_er20",
    "q25_er20",
    "u1_er20",
    "q25_inserted_gold_units",
    "q25_inserted_non_gold_units",
    "u1_inserted_gold_units",
    "u1_inserted_non_gold_units",
    "trigger_u1",
    "ordered_rank",
}

DECISION_KEYS = {
    "ball_score_margin",
    "boundary_margin",
    "dataset",
    "feasible",
    "ordered_rank",
    "planned_insert_count",
    "query_id",
    "r_candidate",
    "r_edge",
    "readiness",
    "sample_id",
    "score",
    "selected_edge_count",
    "tie_hash",
    "trigger_u1",
    "u_boundary",
    "u_margin",
    "uncertainty",
}
RANKING_KEYS = {
    "dataset",
    "dense_top20_unit_ids",
    "final_inserted_unit_ids",
    "final_top20_unit_ids",
    "planned_insert_count",
    "q25_inserted_unit_ids",
    "q25_top20_unit_ids",
    "query_id",
    "sample_id",
    "trigger_u1",
}
AUDIT_KEYS = {
    "dataset",
    "dense_cr20",
    "dense_er20",
    "planned_insert_count",
    "q25_cr20",
    "q25_er20",
    "q25_gain_event",
    "q25_harm_event",
    "q25_inserted_gold_units",
    "q25_inserted_non_gold_units",
    "q25_inserted_units",
    "query_id",
    "question_type",
    "sample_id",
    "trigger_u1",
    "u1_cr20",
    "u1_er20",
    "u1_gain_event",
    "u1_harm_event",
    "u1_inserted_gold_units",
    "u1_inserted_non_gold_units",
    "u1_inserted_units",
}

QUERY_COLUMNS = [
    "query_id",
    "dataset",
    "sample_id",
    "question_type",
    "label",
    "feasible",
    "trigger_u1",
    "ordered_rank",
    *[feature for feature in QUERY_FEATURES if feature != "ordered_rank"],
    "dense_er20",
    "dense_cr20",
    "q25_er20",
    "q25_cr20",
    "u1_er20",
    "u1_cr20",
    "final_cr20",
    "q25_inserted_units",
    "q25_inserted_gold_units",
    "q25_inserted_non_gold_units",
    "u1_inserted_units",
    "u1_inserted_gold_units",
    "u1_inserted_non_gold_units",
    "q25_eligible_count",
    "q25_insert_position_min",
    "q25_insert_position_mean",
    "q25_insert_position_max",
    "q25_inserted_dense20_overlap_count",
    "q25_inserted_protected_overlap_count",
    "dense_q25_top20_jaccard",
]

SEPARABILITY_COLUMNS = [
    "row_type",
    "feature",
    "group",
    "n_total",
    "n_finite",
    "missing_count",
    "nonfinite_count",
    "mean",
    "std",
    "median",
    "q10",
    "q25",
    "q50",
    "q75",
    "q90",
    "mean_ci_low",
    "mean_ci_high",
    "median_ci_low",
    "median_ci_high",
    "overlap_20bin",
    "auroc_gain_high",
    "auroc_ci_low",
    "auroc_ci_high",
    "average_precision_gain_high",
    "ap_ci_low",
    "ap_ci_high",
    "direction",
    "status",
]

DECILE_COLUMNS = [
    "decile",
    "rank_start",
    "rank_end",
    "queries",
    "gains",
    "harms",
    "gain_rate",
    "harm_rate",
    "actual_triggered_queries",
    "actual_triggered_inserted_units",
    "cumulative_queries",
    "cumulative_gains",
    "cumulative_harms",
    "cumulative_gain_retention",
    "cumulative_harm_retention",
    "cumulative_retention_gap",
    "cumulative_inserted_units",
    "cumulative_cr20_delta_vs_dense",
    "cumulative_cr20_delta_vs_q25",
]

MECHANISM_COLUMNS = [
    "query_id",
    "question_type",
    "label",
    "mechanism_category",
    "composition",
    "trigger_u1",
    "q25_eligible_count",
    "q25_inserted_gold_units",
    "q25_inserted_non_gold_units",
    "q25_insert_position_min",
    "q25_insert_position_mean",
    "q25_insert_position_max",
    "q25_inserted_dense20_overlap_count",
    "q25_inserted_protected_overlap_count",
    "dense_q25_top20_jaccard",
    "final_inserted_count",
    "candidate_gold_rank_available",
    "candidate_gold_rank_status",
]

OOF_COLUMNS = [
    "task",
    "feature_panel",
    "query_id",
    "question_type",
    "binary_label",
    "fold",
    "probability",
    "prediction_at_0_5",
    "original_u1_score",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def stable_seed(label: str) -> int:
    digest = hashlib.sha256(f"{BOOTSTRAP_SEED}::{label}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                raise ValueError(f"Blank JSONL row at {path}:{line_number}")
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"Expected JSON object at {path}:{line_number}")
            rows.append(value)
    return rows


def require_keys(row: dict[str, Any], expected: set[str], label: str) -> None:
    if set(row) != expected:
        raise ValueError(f"{label} key contract mismatch")


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value


def require_int(value: Any, label: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be a JSON integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be >= {minimum}")
    return value


def require_binary(value: Any, label: str) -> int:
    converted = require_int(value, label)
    if converted not in {0, 1}:
        raise ValueError(f"{label} must be 0 or 1")
    return converted


def require_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a JSON number")
    converted = float(value)
    if not math.isfinite(converted):
        raise ValueError(f"{label} must be finite")
    return converted


def require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    output = [require_string(item, f"{label}[]") for item in value]
    if len(output) != len(set(output)):
        raise ValueError(f"{label} must contain unique IDs")
    return output


def derive_label(dense_cr20: int, q25_cr20: int) -> str:
    dense = require_binary(dense_cr20, "dense_cr20")
    q25 = require_binary(q25_cr20, "q25_cr20")
    if dense == 0 and q25 == 1:
        return "GAIN"
    if dense == 1 and q25 == 0:
        return "HARM"
    return "NEUTRAL"


def rankdata_average(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    order = np.argsort(array, kind="mergesort")
    ranks = np.empty(len(array), dtype=np.float64)
    start = 0
    while start < len(array):
        end = start + 1
        while end < len(array) and array[order[end]] == array[order[start]]:
            end += 1
        ranks[order[start:end]] = ((start + 1) + end) / 2.0
        start = end
    return ranks


def auroc(y_true: Sequence[int], scores: Sequence[float]) -> float | None:
    y = np.asarray(y_true, dtype=np.int64)
    s = np.asarray(scores, dtype=np.float64)
    positives = int(np.sum(y == 1))
    negatives = int(np.sum(y == 0))
    if positives == 0 or negatives == 0:
        return None
    ranks = rankdata_average(s)
    rank_sum = float(np.sum(ranks[y == 1]))
    return (rank_sum - positives * (positives + 1) / 2.0) / (positives * negatives)


def average_precision(y_true: Sequence[int], scores: Sequence[float]) -> float | None:
    y = np.asarray(y_true, dtype=np.int64)
    s = np.asarray(scores, dtype=np.float64)
    positives = int(np.sum(y == 1))
    if positives == 0:
        return None
    order = np.argsort(-s, kind="mergesort")
    sorted_scores = s[order]
    sorted_y = y[order]
    cumulative_positive = 0
    cumulative_total = 0
    ap = 0.0
    start = 0
    while start < len(sorted_y):
        end = start + 1
        while end < len(sorted_y) and sorted_scores[end] == sorted_scores[start]:
            end += 1
        group_positive = int(np.sum(sorted_y[start:end] == 1))
        cumulative_positive += group_positive
        cumulative_total += end - start
        if group_positive:
            ap += (group_positive / positives) * (cumulative_positive / cumulative_total)
        start = end
    return ap


def percentile_interval(values: Sequence[float]) -> list[float]:
    array = np.asarray(values, dtype=np.float64)
    return [
        float(np.quantile(array, 0.025, method="linear")),
        float(np.quantile(array, 0.975, method="linear")),
    ]


def bootstrap_mean_median(
    values: np.ndarray, iterations: int, seed_label: str
) -> tuple[list[float], list[float]]:
    array = np.asarray(values, dtype=np.float64)
    if len(array) == 0:
        return [math.nan, math.nan], [math.nan, math.nan]
    rng = np.random.default_rng(stable_seed(seed_label))
    means = np.empty(iterations, dtype=np.float64)
    medians = np.empty(iterations, dtype=np.float64)
    offset = 0
    batch_size = 128
    while offset < iterations:
        count = min(batch_size, iterations - offset)
        indices = rng.integers(0, len(array), size=(count, len(array)))
        samples = array[indices]
        means[offset : offset + count] = np.mean(samples, axis=1)
        medians[offset : offset + count] = np.median(samples, axis=1)
        offset += count
    return percentile_interval(means), percentile_interval(medians)


def bootstrap_binary_metrics(
    y_true: Sequence[int],
    scores: Sequence[float],
    iterations: int,
    seed_label: str,
    include_brier: bool = False,
) -> dict[str, list[float]]:
    y = np.asarray(y_true, dtype=np.int64)
    s = np.asarray(scores, dtype=np.float64)
    positive = np.flatnonzero(y == 1)
    negative = np.flatnonzero(y == 0)
    if not len(positive) or not len(negative):
        raise ValueError("Bootstrap requires both classes")
    rng = np.random.default_rng(stable_seed(seed_label))
    auc_values: list[float] = []
    ap_values: list[float] = []
    brier_values: list[float] = []
    for _ in range(iterations):
        indices = np.concatenate(
            [
                rng.choice(positive, size=len(positive), replace=True),
                rng.choice(negative, size=len(negative), replace=True),
            ]
        )
        sampled_y = y[indices]
        sampled_s = s[indices]
        auc_values.append(float(auroc(sampled_y, sampled_s)))
        ap_values.append(float(average_precision(sampled_y, sampled_s)))
        if include_brier:
            brier_values.append(float(np.mean((sampled_s - sampled_y) ** 2)))
    result = {
        "auroc": percentile_interval(auc_values),
        "average_precision": percentile_interval(ap_values),
    }
    if include_brier:
        result["brier"] = percentile_interval(brier_values)
    return result


def distribution_overlap(gain: np.ndarray, harm: np.ndarray) -> float:
    combined = np.concatenate([gain, harm])
    minimum = float(np.min(combined))
    maximum = float(np.max(combined))
    if minimum == maximum:
        return 1.0
    gain_hist, edges = np.histogram(gain, bins=20, range=(minimum, maximum))
    harm_hist, _ = np.histogram(harm, bins=edges)
    gain_mass = gain_hist / len(gain)
    harm_mass = harm_hist / len(harm)
    return float(np.sum(np.minimum(gain_mass, harm_mass)))


def spearman(values_a: Sequence[float], values_b: Sequence[float]) -> float | None:
    a = np.asarray(values_a, dtype=np.float64)
    b = np.asarray(values_b, dtype=np.float64)
    mask = np.isfinite(a) & np.isfinite(b)
    if int(np.sum(mask)) < 2:
        return None
    rank_a = rankdata_average(a[mask])
    rank_b = rankdata_average(b[mask])
    if np.std(rank_a) == 0 or np.std(rank_b) == 0:
        return 0.0
    return float(np.corrcoef(rank_a, rank_b)[0, 1])


def fixed_decile(ordered_rank: int, feasible_count: int) -> int:
    rank = require_int(ordered_rank, "ordered_rank", 1)
    count = require_int(feasible_count, "feasible_count", 1)
    if rank > count:
        raise ValueError("ordered_rank exceeds feasible_count")
    return min(10, ((rank - 1) * 10 // count) + 1)


def mechanism_category(label: str, gold: int, non_gold: int) -> str:
    g = require_int(gold, "inserted gold", 0)
    n = require_int(non_gold, "inserted non-gold", 0)
    total = g + n
    if label == "HARM":
        if total == 0:
            raise ValueError("HARM query has zero q25 insertions")
        return "DISPLACEMENT_HARM_QUERY"
    if label == "GAIN":
        if g <= 0:
            raise ValueError("GAIN query has no inserted gold unit")
        return "PURE_GAIN_QUERY" if n == 0 else "MIXED_GAIN_NOISE_QUERY"
    if label != "NEUTRAL":
        raise ValueError(f"Unknown label: {label}")
    if total > 0 and g == 0 and n == total:
        return "PURE_NOISE_QUERY"
    return "NO_EFFECT_QUERY"


def composition(gold: int, non_gold: int) -> str:
    if gold == 0 and non_gold == 0:
        return "NO_INSERT"
    if gold > 0 and non_gold == 0:
        return "GOLD_ONLY"
    if gold > 0 and non_gold > 0:
        return "MIXED_GOLD_NON_GOLD"
    return "NON_GOLD_ONLY"


def validate_probe_features() -> None:
    for panel, features in FEATURE_PANELS.items():
        if len(features) != len(set(features)):
            raise ValueError(f"Duplicate feature in panel {panel}")
        forbidden = sorted(set(features) & FORBIDDEN_PROBE_FEATURES)
        if forbidden:
            raise ValueError(f"Forbidden probe features in {panel}: {forbidden}")


def git_head(repo_root: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def verify_protocol_and_repository(repo_root: Path) -> None:
    protocol = repo_root / PROTOCOL_PATH
    if sha256_file(protocol) != PROTOCOL_SHA256:
        raise ValueError("Stage4C protocol working bytes mismatch")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", PROTOCOL_COMMIT, "HEAD"],
        cwd=repo_root,
    )
    if ancestor.returncode != 0:
        raise ValueError("Stage4C protocol commit is not an ancestor of HEAD")
    dirty = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if dirty.strip():
        raise ValueError("Official Stage4C run requires a clean worktree")


def verify_input_files(repo_root: Path) -> dict[str, dict[str, Any]]:
    identities: dict[str, dict[str, Any]] = {}
    for name, spec in INPUT_SPECS.items():
        path = repo_root / spec["path"]
        if not path.is_file():
            raise ValueError(f"Missing frozen input: {spec['path']}")
        size = path.stat().st_size
        digest = sha256_file(path)
        if size != spec["bytes"] or digest != spec["sha256"]:
            raise ValueError(f"Frozen input identity mismatch: {spec['path']}")
        tracked = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", spec["path"]],
            cwd=repo_root,
        )
        if tracked.returncode != 0:
            raise ValueError(f"Frozen input differs from HEAD: {spec['path']}")
        identities[name] = {
            "path": spec["path"],
            "bytes": size,
            "sha256": digest,
            "git_blob": subprocess.run(
                ["git", "rev-parse", f"HEAD:{spec['path']}"],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip(),
        }
    return identities


def validate_and_join(
    decisions: list[dict[str, Any]],
    rankings: list[dict[str, Any]],
    audits: list[dict[str, Any]],
    *,
    enforce_official_counts: bool,
) -> list[dict[str, Any]]:
    if not (len(decisions) == len(rankings) == len(audits)):
        raise ValueError("Input row counts differ")
    if enforce_official_counts and len(decisions) != QUERY_COUNT:
        raise ValueError("Official query count mismatch")

    def index_rows(rows: list[dict[str, Any]], label: str) -> dict[str, dict[str, Any]]:
        output: dict[str, dict[str, Any]] = {}
        for index, row in enumerate(rows):
            query_id = require_string(row.get("query_id"), f"{label}[{index}].query_id")
            if query_id in output:
                raise ValueError(f"Duplicate {label} query_id: {query_id}")
            output[query_id] = row
        return output

    ranking_by_id = index_rows(rankings, "ranking")
    audit_by_id = index_rows(audits, "audit")
    if set(ranking_by_id) != set(audit_by_id):
        raise ValueError("Ranking/audit query sets differ")

    joined: list[dict[str, Any]] = []
    seen: set[str] = set()
    feasible_ranks: list[int] = []
    for row_index, decision in enumerate(decisions):
        require_keys(decision, DECISION_KEYS, f"decision[{row_index}]")
        query_id = require_string(decision["query_id"], "decision.query_id")
        if query_id in seen:
            raise ValueError(f"Duplicate decision query_id: {query_id}")
        seen.add(query_id)
        if query_id not in ranking_by_id or query_id not in audit_by_id:
            raise ValueError(f"Missing joined row: {query_id}")
        ranking = ranking_by_id[query_id]
        audit = audit_by_id[query_id]
        require_keys(ranking, RANKING_KEYS, f"ranking[{query_id}]")
        require_keys(audit, AUDIT_KEYS, f"audit[{query_id}]")

        dataset = require_string(decision["dataset"], "decision.dataset")
        sample_id = require_string(decision["sample_id"], "decision.sample_id")
        for source, source_row in (("ranking", ranking), ("audit", audit)):
            if source_row["query_id"] != query_id:
                raise ValueError(f"{source} query identity mismatch")
            if require_string(source_row["dataset"], f"{source}.dataset") != dataset:
                raise ValueError(f"{source} dataset mismatch")
            if require_string(source_row["sample_id"], f"{source}.sample_id") != sample_id:
                raise ValueError(f"{source} sample_id mismatch")

        feasible = require_binary(decision["feasible"], "feasible")
        trigger = require_binary(decision["trigger_u1"], "trigger_u1")
        planned = require_int(decision["planned_insert_count"], "planned_insert_count", 0)
        selected_edges = require_int(decision["selected_edge_count"], "selected_edge_count", 0)
        ball_margin = require_number(decision["ball_score_margin"], "ball_score_margin")
        boundary_margin = require_number(decision["boundary_margin"], "boundary_margin")
        require_string(decision["tie_hash"], "tie_hash")
        ranking_trigger = require_binary(ranking["trigger_u1"], "ranking.trigger_u1")
        audit_trigger = require_binary(audit["trigger_u1"], "audit.trigger_u1")
        ranking_planned = require_int(
            ranking["planned_insert_count"], "ranking.planned_insert_count", 0
        )
        audit_planned = require_int(
            audit["planned_insert_count"], "audit.planned_insert_count", 0
        )
        if ranking_trigger != trigger or audit_trigger != trigger:
            raise ValueError("trigger_u1 mismatch")
        if ranking_planned != planned or audit_planned != planned:
            raise ValueError("planned_insert_count mismatch")

        derived_names = [
            "u_margin",
            "u_boundary",
            "r_edge",
            "r_candidate",
            "uncertainty",
            "readiness",
            "score",
        ]
        derived: dict[str, float | None] = {}
        if feasible:
            rank = require_int(decision["ordered_rank"], "ordered_rank", 1)
            feasible_ranks.append(rank)
            for name in derived_names:
                derived[name] = require_number(decision[name], name)
            if abs(derived["uncertainty"] - (derived["u_margin"] + derived["u_boundary"]) / 2.0) > 1e-12:
                raise ValueError("uncertainty formula mismatch")
            expected_readiness = math.sqrt(derived["r_edge"] * derived["r_candidate"])
            if abs(derived["readiness"] - expected_readiness) > 1e-12:
                raise ValueError("readiness formula mismatch")
            if abs(derived["score"] - derived["uncertainty"] * derived["readiness"]) > 1e-12:
                raise ValueError("score formula mismatch")
        else:
            rank = None
            if decision["ordered_rank"] is not None:
                raise ValueError("Infeasible ordered_rank must be null")
            for name in derived_names:
                if decision[name] is not None:
                    raise ValueError(f"Infeasible {name} must be null")
                derived[name] = None

        dense_ids = require_string_list(ranking["dense_top20_unit_ids"], "dense_top20_unit_ids")
        q25_ids = require_string_list(ranking["q25_top20_unit_ids"], "q25_top20_unit_ids")
        final_ids = require_string_list(ranking["final_top20_unit_ids"], "final_top20_unit_ids")
        q25_inserted_ids = require_string_list(ranking["q25_inserted_unit_ids"], "q25_inserted_unit_ids")
        final_inserted_ids = require_string_list(ranking["final_inserted_unit_ids"], "final_inserted_unit_ids")
        if not (1 <= len(dense_ids) <= 20) or len(q25_ids) != len(dense_ids) or len(final_ids) != len(dense_ids):
            raise ValueError("Ranking effective-K contract mismatch")
        if any(unit_id not in q25_ids for unit_id in q25_inserted_ids):
            raise ValueError("q25 inserted ID missing from q25 ranking")
        if any(unit_id not in final_ids for unit_id in final_inserted_ids):
            raise ValueError("final inserted ID missing from final ranking")

        binary_fields = [
            "dense_cr20",
            "q25_cr20",
            "u1_cr20",
            "q25_gain_event",
            "q25_harm_event",
            "u1_gain_event",
            "u1_harm_event",
        ]
        for name in binary_fields:
            require_binary(audit[name], name)
        for name in ("dense_er20", "q25_er20", "u1_er20"):
            require_number(audit[name], name)
        count_fields = [
            "q25_inserted_gold_units",
            "q25_inserted_non_gold_units",
            "q25_inserted_units",
            "u1_inserted_gold_units",
            "u1_inserted_non_gold_units",
            "u1_inserted_units",
        ]
        for name in count_fields:
            require_int(audit[name], name, 0)
        if audit["q25_inserted_gold_units"] + audit["q25_inserted_non_gold_units"] != audit["q25_inserted_units"]:
            raise ValueError("q25 inserted composition mismatch")
        if audit["u1_inserted_gold_units"] + audit["u1_inserted_non_gold_units"] != audit["u1_inserted_units"]:
            raise ValueError("U1 inserted composition mismatch")
        if len(q25_inserted_ids) != audit["q25_inserted_units"]:
            raise ValueError("q25 inserted ID/count mismatch")
        if len(final_inserted_ids) != audit["u1_inserted_units"]:
            raise ValueError("final inserted ID/count mismatch")

        label = derive_label(audit["dense_cr20"], audit["q25_cr20"])
        if audit["q25_gain_event"] != int(label == "GAIN") or audit["q25_harm_event"] != int(label == "HARM"):
            raise ValueError("Frozen q25 event label mismatch")
        if audit["u1_gain_event"] != int(trigger == 1 and label == "GAIN"):
            raise ValueError("Frozen U1 gain-event subset mismatch")
        if audit["u1_harm_event"] != int(trigger == 1 and label == "HARM"):
            raise ValueError("Frozen U1 harm-event subset mismatch")

        q25_positions = [q25_ids.index(unit_id) + 1 for unit_id in q25_inserted_ids]
        dense_set = set(dense_ids)
        q25_set = set(q25_ids)
        union = dense_set | q25_set
        q25_dense_overlap = sum(unit_id in dense_set for unit_id in q25_inserted_ids)
        q25_protected_overlap = sum(unit_id in set(dense_ids[: min(10, len(dense_ids))]) for unit_id in q25_inserted_ids)
        if q25_protected_overlap:
            raise ValueError("q25 inserted ID overlaps Dense protected prefix")

        question_type = require_string(audit["question_type"], "question_type")
        query_row: dict[str, Any] = {
            "query_id": query_id,
            "dataset": dataset,
            "sample_id": sample_id,
            "question_type": question_type,
            "label": label,
            "feasible": feasible,
            "trigger_u1": trigger,
            "ordered_rank": rank,
            "ball_score_margin": ball_margin,
            "boundary_margin": boundary_margin,
            "selected_edge_count": selected_edges,
            "planned_insert_count": planned,
            **derived,
            "dense_er20": float(audit["dense_er20"]),
            "dense_cr20": audit["dense_cr20"],
            "q25_er20": float(audit["q25_er20"]),
            "q25_cr20": audit["q25_cr20"],
            "u1_er20": float(audit["u1_er20"]),
            "u1_cr20": audit["u1_cr20"],
            "final_cr20": audit["u1_cr20"],
            "q25_inserted_units": audit["q25_inserted_units"],
            "q25_inserted_gold_units": audit["q25_inserted_gold_units"],
            "q25_inserted_non_gold_units": audit["q25_inserted_non_gold_units"],
            "u1_inserted_units": audit["u1_inserted_units"],
            "u1_inserted_gold_units": audit["u1_inserted_gold_units"],
            "u1_inserted_non_gold_units": audit["u1_inserted_non_gold_units"],
            "q25_eligible_count": len(q25_inserted_ids),
            "q25_insert_position_min": min(q25_positions) if q25_positions else None,
            "q25_insert_position_mean": float(np.mean(q25_positions)) if q25_positions else None,
            "q25_insert_position_max": max(q25_positions) if q25_positions else None,
            "q25_inserted_dense20_overlap_count": q25_dense_overlap,
            "q25_inserted_protected_overlap_count": q25_protected_overlap,
            "dense_q25_top20_jaccard": len(dense_set & q25_set) / len(union) if union else 1.0,
            "final_inserted_count": len(final_inserted_ids),
        }
        joined.append(query_row)

    if set(seen) != set(ranking_by_id) or set(seen) != set(audit_by_id):
        raise ValueError("Joined query sets differ")
    if feasible_ranks and sorted(feasible_ranks) != list(range(1, len(feasible_ranks) + 1)):
        raise ValueError("Feasible ordered ranks must be unique and contiguous")

    counts = Counter(row["label"] for row in joined)
    retained_gain = sum(row["trigger_u1"] for row in joined if row["label"] == "GAIN")
    retained_harm = sum(row["trigger_u1"] for row in joined if row["label"] == "HARM")
    if enforce_official_counts:
        if counts["GAIN"] != GAIN_COUNT or counts["HARM"] != HARM_COUNT:
            raise ValueError("Frozen gain/harm counts mismatch")
        if retained_gain != RETAINED_GAIN_COUNT or retained_harm != RETAINED_HARM_COUNT:
            raise ValueError("Frozen retained gain/harm counts mismatch")
    return joined


def aggregate_frozen_metrics(rows: list[dict[str, Any]], slice_name: str) -> dict[str, Any]:
    if not rows:
        raise ValueError(f"Cannot aggregate empty frozen slice: {slice_name}")
    queries = len(rows)
    q25_inserted = sum(row["q25_inserted_units"] for row in rows)
    u1_inserted = sum(row["u1_inserted_units"] for row in rows)
    q25_non_gold = sum(row["q25_inserted_non_gold_units"] for row in rows)
    u1_non_gold = sum(row["u1_inserted_non_gold_units"] for row in rows)
    gain_events = sum(row["label"] == "GAIN" for row in rows)
    harm_events = sum(row["label"] == "HARM" for row in rows)
    retained_gain = sum(row["trigger_u1"] for row in rows if row["label"] == "GAIN")
    retained_harm = sum(row["trigger_u1"] for row in rows if row["label"] == "HARM")
    gain_retention = retained_gain / gain_events if gain_events else 0.0
    harm_retention = retained_harm / harm_events if harm_events else 0.0
    dense_cr20 = sum(row["dense_cr20"] for row in rows) / queries
    q25_cr20 = sum(row["q25_cr20"] for row in rows) / queries
    u1_cr20 = sum(row["u1_cr20"] for row in rows) / queries
    return {
        "slice": slice_name,
        "queries": queries,
        "dense_er20": sum(row["dense_er20"] for row in rows) / queries,
        "dense_cr20": dense_cr20,
        "q25_er20": sum(row["q25_er20"] for row in rows) / queries,
        "q25_cr20": q25_cr20,
        "u1_er20": sum(row["u1_er20"] for row in rows) / queries,
        "u1_cr20": u1_cr20,
        "q25_gain_events": gain_events,
        "q25_harm_events": harm_events,
        "retained_gain_events": retained_gain,
        "retained_harm_events": retained_harm,
        "gain_retention": gain_retention,
        "harm_retention": harm_retention,
        "retention_gap": gain_retention - harm_retention,
        "q25_inserted_units": q25_inserted,
        "u1_inserted_units": u1_inserted,
        "inserted_unit_reduction": 1.0 - (u1_inserted / q25_inserted),
        "q25_conditional_false_insert_rate": q25_non_gold / q25_inserted,
        "u1_conditional_false_insert_rate": u1_non_gold / u1_inserted,
        "u1_cr20_delta_vs_dense": u1_cr20 - dense_cr20,
        "u1_cr20_delta_vs_q25": u1_cr20 - q25_cr20,
    }


SUMMARY_INTEGER_FIELDS = {
    "queries",
    "q25_gain_events",
    "q25_harm_events",
    "retained_gain_events",
    "retained_harm_events",
    "q25_inserted_units",
    "u1_inserted_units",
}
SUMMARY_FLOAT_FIELDS = {
    "dense_er20",
    "dense_cr20",
    "q25_er20",
    "q25_cr20",
    "u1_er20",
    "u1_cr20",
    "gain_retention",
    "harm_retention",
    "retention_gap",
    "inserted_unit_reduction",
    "q25_conditional_false_insert_rate",
    "u1_conditional_false_insert_rate",
    "u1_cr20_delta_vs_dense",
    "u1_cr20_delta_vs_q25",
}


def verify_metric_block(observed: Any, expected: dict[str, Any], label: str) -> None:
    if not isinstance(observed, dict):
        raise ValueError(f"{label} must be an object")
    if require_string(observed.get("slice"), f"{label}.slice") != expected["slice"]:
        raise ValueError(f"{label}.slice mismatch")
    for name in sorted(SUMMARY_INTEGER_FIELDS):
        value = require_int(observed.get(name), f"{label}.{name}", 0)
        if value != expected[name]:
            raise ValueError(f"{label}.{name} mismatch")
    for name in sorted(SUMMARY_FLOAT_FIELDS):
        value = require_number(observed.get(name), f"{label}.{name}")
        if not math.isclose(value, expected[name], rel_tol=0.0, abs_tol=1e-12):
            raise ValueError(f"{label}.{name} mismatch")


def verify_frozen_summary(
    rows: list[dict[str, Any]], gold_summary: Any, post_gold: Any
) -> None:
    if not isinstance(gold_summary, dict) or not isinstance(post_gold, dict):
        raise ValueError("Frozen Gold verification artifacts must be objects")
    overall = aggregate_frozen_metrics(rows, "ALL")
    verify_metric_block(gold_summary.get("overall"), overall, "gold_summary.overall")

    question_types = gold_summary.get("question_types")
    if not isinstance(question_types, list):
        raise ValueError("gold_summary.question_types must be an array")
    observed_by_type: dict[str, dict[str, Any]] = {}
    for index, block in enumerate(question_types):
        if not isinstance(block, dict):
            raise ValueError(f"gold_summary.question_types[{index}] must be an object")
        name = require_string(block.get("slice"), f"gold_summary.question_types[{index}].slice")
        if name in observed_by_type:
            raise ValueError(f"Duplicate Gold summary question type: {name}")
        observed_by_type[name] = block
    expected_types = sorted({row["question_type"] for row in rows})
    if sorted(observed_by_type) != expected_types:
        raise ValueError("Gold summary question-type set mismatch")
    for question_type in expected_types:
        expected = aggregate_frozen_metrics(
            [row for row in rows if row["question_type"] == question_type], question_type
        )
        verify_metric_block(
            observed_by_type[question_type], expected, f"gold_summary.question_types.{question_type}"
        )

    baseline = gold_summary.get("baseline_equivalence", {}).get("observed")
    if not isinstance(baseline, dict):
        raise ValueError("Gold summary baseline equivalence block missing")
    for name in ("queries", "q25_gain_events", "q25_harm_events"):
        if require_int(baseline.get(name), f"baseline_equivalence.{name}", 0) != overall[name]:
            raise ValueError(f"baseline_equivalence.{name} mismatch")
    for name in ("dense_er20", "dense_cr20", "q25_er20", "q25_cr20"):
        value = require_number(baseline.get(name), f"baseline_equivalence.{name}")
        if not math.isclose(value, overall[name], rel_tol=0.0, abs_tol=1e-12):
            raise ValueError(f"baseline_equivalence.{name} mismatch")

    if require_int(post_gold.get("queries"), "post_gold.queries", 0) != len(rows):
        raise ValueError("Frozen post-Gold query count mismatch")
    expected_hashes = {
        "primary_query_audit": INPUT_SPECS["query_audit"]["sha256"],
        "primary_summary": INPUT_SPECS["gold_summary"]["sha256"],
        "rerun_query_audit": INPUT_SPECS["query_audit"]["sha256"],
        "rerun_summary": INPUT_SPECS["gold_summary"]["sha256"],
    }
    if post_gold.get("output_hashes") != expected_hashes:
        raise ValueError("Frozen post-Gold output hash bindings mismatch")


def distribution_row(feature: str, group: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    raw = [row[feature] for row in rows]
    finite = np.asarray(
        [float(value) for value in raw if value is not None and math.isfinite(float(value))],
        dtype=np.float64,
    )
    missing = sum(value is None for value in raw)
    nonfinite = len(raw) - missing - len(finite)
    result = {column: None for column in SEPARABILITY_COLUMNS}
    result.update(
        {
            "row_type": "DISTRIBUTION",
            "feature": feature,
            "group": group,
            "n_total": len(raw),
            "n_finite": len(finite),
            "missing_count": missing,
            "nonfinite_count": nonfinite,
            "status": "PASS" if len(finite) else "NO_FINITE_VALUES",
        }
    )
    if len(finite):
        quantiles = np.quantile(finite, [0.10, 0.25, 0.50, 0.75, 0.90], method="linear")
        mean_ci, median_ci = bootstrap_mean_median(
            finite, BOOTSTRAP_ITERATIONS, f"distribution::{feature}::{group}"
        )
        result.update(
            {
                "mean": float(np.mean(finite)),
                "std": float(np.std(finite, ddof=1)) if len(finite) > 1 else 0.0,
                "median": float(np.median(finite)),
                "q10": float(quantiles[0]),
                "q25": float(quantiles[1]),
                "q50": float(quantiles[2]),
                "q75": float(quantiles[3]),
                "q90": float(quantiles[4]),
                "mean_ci_low": mean_ci[0],
                "mean_ci_high": mean_ci[1],
                "median_ci_low": median_ci[0],
                "median_ci_high": median_ci[1],
            }
        )
    return result


def separability_row(feature: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    gain = [row for row in rows if row["label"] == "GAIN" and row[feature] is not None]
    harm = [row for row in rows if row["label"] == "HARM" and row[feature] is not None]
    gain_values = np.asarray([float(row[feature]) for row in gain], dtype=np.float64)
    harm_values = np.asarray([float(row[feature]) for row in harm], dtype=np.float64)
    result = {column: None for column in SEPARABILITY_COLUMNS}
    result.update(
        {
            "row_type": "SEPARABILITY",
            "feature": feature,
            "group": "GAIN_VS_HARM",
            "n_total": GAIN_COUNT + HARM_COUNT,
            "n_finite": len(gain_values) + len(harm_values),
            "missing_count": GAIN_COUNT + HARM_COUNT - len(gain_values) - len(harm_values),
            "nonfinite_count": 0,
        }
    )
    if len(gain_values) < 20 or len(harm_values) < 20:
        result["status"] = "INSUFFICIENT_FINITE_EVENTS"
        return result
    y = np.concatenate(
        [np.ones(len(gain_values), dtype=np.int64), np.zeros(len(harm_values), dtype=np.int64)]
    )
    values = np.concatenate([gain_values, harm_values])
    auc = float(auroc(y, values))
    ap = float(average_precision(y, values))
    intervals = bootstrap_binary_metrics(
        y,
        values,
        BOOTSTRAP_ITERATIONS,
        f"separability::{feature}",
    )
    result.update(
        {
            "overlap_20bin": distribution_overlap(gain_values, harm_values),
            "auroc_gain_high": auc,
            "auroc_ci_low": intervals["auroc"][0],
            "auroc_ci_high": intervals["auroc"][1],
            "average_precision_gain_high": ap,
            "ap_ci_low": intervals["average_precision"][0],
            "ap_ci_high": intervals["average_precision"][1],
            "direction": "GAIN_HIGH" if auc > 0.5 else "HARM_HIGH" if auc < 0.5 else "NO_DIRECTION",
            "status": "PASS",
        }
    )
    return result


def build_feature_separability(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    output: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}
    for feature in QUERY_FEATURES:
        for group in ("GAIN", "HARM", "NEUTRAL"):
            output.append(distribution_row(feature, group, [row for row in rows if row["label"] == group]))
        separation = separability_row(feature, rows)
        output.append(separation)
        summary[feature] = {
            key: separation[key]
            for key in (
                "n_finite",
                "missing_count",
                "overlap_20bin",
                "auroc_gain_high",
                "auroc_ci_low",
                "auroc_ci_high",
                "average_precision_gain_high",
                "ap_ci_low",
                "ap_ci_high",
                "direction",
                "status",
            )
        }
    return output, summary


def build_deciles(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], str]:
    feasible = sorted(
        [row for row in rows if row["feasible"] == 1], key=lambda row: int(row["ordered_rank"])
    )
    feasible_count = len(feasible)
    by_decile: dict[int, list[dict[str, Any]]] = {value: [] for value in range(1, 11)}
    for row in feasible:
        by_decile[fixed_decile(int(row["ordered_rank"]), feasible_count)].append(row)
    all_q25_net = sum(row["q25_cr20"] - row["dense_cr20"] for row in rows)
    output: list[dict[str, Any]] = []
    cumulative: list[dict[str, Any]] = []
    for decile in range(1, 11):
        group = by_decile[decile]
        cumulative.extend(group)
        gains = sum(row["label"] == "GAIN" for row in group)
        harms = sum(row["label"] == "HARM" for row in group)
        cumulative_gains = sum(row["label"] == "GAIN" for row in cumulative)
        cumulative_harms = sum(row["label"] == "HARM" for row in cumulative)
        gain_retention = cumulative_gains / GAIN_COUNT
        harm_retention = cumulative_harms / HARM_COUNT
        cumulative_net = sum(row["q25_cr20"] - row["dense_cr20"] for row in cumulative)
        output.append(
            {
                "decile": decile,
                "rank_start": min((row["ordered_rank"] for row in group), default=None),
                "rank_end": max((row["ordered_rank"] for row in group), default=None),
                "queries": len(group),
                "gains": gains,
                "harms": harms,
                "gain_rate": gains / len(group) if group else None,
                "harm_rate": harms / len(group) if group else None,
                "actual_triggered_queries": sum(row["trigger_u1"] for row in group),
                "actual_triggered_inserted_units": sum(
                    row["q25_inserted_units"] for row in group if row["trigger_u1"]
                ),
                "cumulative_queries": len(cumulative),
                "cumulative_gains": cumulative_gains,
                "cumulative_harms": cumulative_harms,
                "cumulative_gain_retention": gain_retention,
                "cumulative_harm_retention": harm_retention,
                "cumulative_retention_gap": gain_retention - harm_retention,
                "cumulative_inserted_units": sum(row["q25_inserted_units"] for row in cumulative),
                "cumulative_cr20_delta_vs_dense": cumulative_net / QUERY_COUNT,
                "cumulative_cr20_delta_vs_q25": (cumulative_net - all_q25_net) / QUERY_COUNT,
            }
        )
    actual_gain_retention = RETAINED_GAIN_COUNT / GAIN_COUNT
    actual_harm_retention = RETAINED_HARM_COUNT / HARM_COUNT
    if any(row["cumulative_retention_gap"] > 0 for row in output[:3]) and actual_gain_retention - actual_harm_retention < 0:
        pattern = "B_HIGH_SIGNAL_THEN_BUDGET_DEGRADATION"
    elif output[0]["harms"] >= output[0]["gains"] and output[1]["cumulative_retention_gap"] <= 0:
        pattern = "A_HIGH_SCORE_HARM_DOMINANT"
    elif sum(abs(row["gain_rate"] - row["harm_rate"]) < 0.01 for row in output) >= 8:
        pattern = "C_NEAR_NO_SEPARATION"
    else:
        pattern = "D_LOCALIZED_OR_IRREGULAR_SIGNAL"
    return output, pattern


def build_mechanisms(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int], bool]:
    output: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    for row in rows:
        category = mechanism_category(
            row["label"], row["q25_inserted_gold_units"], row["q25_inserted_non_gold_units"]
        )
        counts[category] += 1
        output.append(
            {
                "query_id": row["query_id"],
                "question_type": row["question_type"],
                "label": row["label"],
                "mechanism_category": category,
                "composition": composition(
                    row["q25_inserted_gold_units"], row["q25_inserted_non_gold_units"]
                ),
                "trigger_u1": row["trigger_u1"],
                "q25_eligible_count": row["q25_eligible_count"],
                "q25_inserted_gold_units": row["q25_inserted_gold_units"],
                "q25_inserted_non_gold_units": row["q25_inserted_non_gold_units"],
                "q25_insert_position_min": row["q25_insert_position_min"],
                "q25_insert_position_mean": row["q25_insert_position_mean"],
                "q25_insert_position_max": row["q25_insert_position_max"],
                "q25_inserted_dense20_overlap_count": row[
                    "q25_inserted_dense20_overlap_count"
                ],
                "q25_inserted_protected_overlap_count": row[
                    "q25_inserted_protected_overlap_count"
                ],
                "dense_q25_top20_jaccard": row["dense_q25_top20_jaccard"],
                "final_inserted_count": row["final_inserted_count"],
                "candidate_gold_rank_available": 0,
                "candidate_gold_rank_status": "NOT_AVAILABLE_IN_FROZEN_ALLOWED_ARTIFACTS",
            }
        )
    mixed = counts["MIXED_GAIN_NOISE_QUERY"]
    displacement = counts["DISPLACEMENT_HARM_QUERY"]
    limitation = mixed + displacement >= 33 and mixed >= 10 and displacement >= 10
    return output, dict(sorted(counts.items())), limitation


def stratified_fold_ids(y_true: Sequence[int], folds: int, seed: int) -> np.ndarray:
    y = np.asarray(y_true, dtype=np.int64)
    assignments = np.full(len(y), -1, dtype=np.int64)
    rng = np.random.default_rng(seed)
    for class_value in (0, 1):
        indices = np.flatnonzero(y == class_value)
        shuffled = indices.copy()
        rng.shuffle(shuffled)
        for position, index in enumerate(shuffled):
            assignments[index] = position % folds
    if np.any(assignments < 0):
        raise ValueError("Incomplete fold assignment")
    return assignments


def preprocess_train_test(
    train: np.ndarray, test: np.ndarray
) -> tuple[np.ndarray, np.ndarray, dict[str, list[float]]]:
    train_values = np.asarray(train, dtype=np.float64).copy()
    test_values = np.asarray(test, dtype=np.float64).copy()
    medians = np.zeros(train_values.shape[1], dtype=np.float64)
    means = np.zeros(train_values.shape[1], dtype=np.float64)
    stds = np.ones(train_values.shape[1], dtype=np.float64)
    for column in range(train_values.shape[1]):
        finite = train_values[np.isfinite(train_values[:, column]), column]
        median = float(np.median(finite)) if len(finite) else 0.0
        medians[column] = median
        train_values[~np.isfinite(train_values[:, column]), column] = median
        test_values[~np.isfinite(test_values[:, column]), column] = median
        means[column] = float(np.mean(train_values[:, column]))
        standard = float(np.std(train_values[:, column], ddof=0))
        stds[column] = standard if standard > 0 else 1.0
        train_values[:, column] = (train_values[:, column] - means[column]) / stds[column]
        test_values[:, column] = (test_values[:, column] - means[column]) / stds[column]
    return train_values, test_values, {
        "medians": medians.tolist(),
        "means": means.tolist(),
        "stds": stds.tolist(),
    }


def sigmoid(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(values, -35.0, 35.0)
    return 1.0 / (1.0 + np.exp(-clipped))


def fit_logistic_irls(
    x_train: np.ndarray,
    y_train: np.ndarray,
    l2: float = LOGISTIC_L2,
    max_iterations: int = LOGISTIC_MAX_ITERATIONS,
    tolerance: float = LOGISTIC_TOLERANCE,
) -> tuple[np.ndarray, int, bool]:
    x = np.column_stack([np.ones(len(x_train), dtype=np.float64), x_train])
    y = np.asarray(y_train, dtype=np.float64)
    beta = np.zeros(x.shape[1], dtype=np.float64)
    penalty = np.eye(x.shape[1], dtype=np.float64) * l2
    penalty[0, 0] = 0.0
    converged = False
    for iteration in range(1, max_iterations + 1):
        probability = sigmoid(x @ beta)
        weights = np.clip(probability * (1.0 - probability), 1e-9, None)
        gradient = x.T @ (probability - y) + penalty @ beta
        hessian = x.T @ (weights[:, None] * x) + penalty
        try:
            step = np.linalg.solve(hessian, gradient)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(hessian, gradient, rcond=None)[0]
        beta -= step
        if float(np.max(np.abs(step))) < tolerance:
            converged = True
            return beta, iteration, converged
    return beta, max_iterations, converged


def predict_logistic(beta: np.ndarray, x_values: np.ndarray) -> np.ndarray:
    x = np.column_stack([np.ones(len(x_values), dtype=np.float64), x_values])
    return sigmoid(x @ beta)


def calibration_summary(y_true: np.ndarray, probabilities: np.ndarray) -> dict[str, Any]:
    bins: list[dict[str, Any]] = []
    ece = 0.0
    for index in range(10):
        low = index / 10.0
        high = (index + 1) / 10.0
        if index == 9:
            mask = (probabilities >= low) & (probabilities <= high)
        else:
            mask = (probabilities >= low) & (probabilities < high)
        count = int(np.sum(mask))
        mean_probability = float(np.mean(probabilities[mask])) if count else None
        observed_rate = float(np.mean(y_true[mask])) if count else None
        if count:
            ece += (count / len(y_true)) * abs(mean_probability - observed_rate)
        bins.append(
            {
                "bin": index + 1,
                "low": low,
                "high": high,
                "count": count,
                "mean_probability": mean_probability,
                "observed_rate": observed_rate,
            }
        )
    return {"expected_calibration_error": ece, "bins": bins}


def confusion_at_half(y_true: np.ndarray, probabilities: np.ndarray) -> dict[str, int]:
    prediction = (probabilities >= 0.5).astype(np.int64)
    return {
        "tn": int(np.sum((y_true == 0) & (prediction == 0))),
        "fp": int(np.sum((y_true == 0) & (prediction == 1))),
        "fn": int(np.sum((y_true == 1) & (prediction == 0))),
        "tp": int(np.sum((y_true == 1) & (prediction == 1))),
    }


def task_rows(rows: list[dict[str, Any]], task: str) -> tuple[list[dict[str, Any]], np.ndarray]:
    if task == "TASK_A_GAIN_VS_HARM":
        selected = [row for row in rows if row["label"] in {"GAIN", "HARM"}]
        y = np.asarray([int(row["label"] == "GAIN") for row in selected], dtype=np.int64)
    elif task == "TASK_B_GAIN_VS_NON_GAIN":
        selected = list(rows)
        y = np.asarray([int(row["label"] == "GAIN") for row in selected], dtype=np.int64)
    elif task == "TASK_C_HARM_VS_NON_HARM":
        selected = list(rows)
        y = np.asarray([int(row["label"] == "HARM") for row in selected], dtype=np.int64)
    else:
        raise ValueError(f"Unknown task: {task}")
    return selected, y


def run_oof_panel(
    selected_rows: list[dict[str, Any]],
    y: np.ndarray,
    task: str,
    panel_name: str,
    features: list[str],
) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]], dict[str, Any]]:
    matrix = np.asarray(
        [
            [float(row[feature]) if row[feature] is not None else math.nan for feature in features]
            for row in selected_rows
        ],
        dtype=np.float64,
    )
    fold_ids = stratified_fold_ids(y, FOLDS, BOOTSTRAP_SEED)
    probabilities = np.empty(len(y), dtype=np.float64)
    fold_metrics: list[dict[str, Any]] = []
    preprocess_audit: list[dict[str, Any]] = []
    for fold in range(FOLDS):
        test_mask = fold_ids == fold
        train_mask = ~test_mask
        train_x, test_x, preprocessing = preprocess_train_test(matrix[train_mask], matrix[test_mask])
        beta, iterations, converged = fit_logistic_irls(train_x, y[train_mask])
        probabilities[test_mask] = predict_logistic(beta, test_x)
        fold_y = y[test_mask]
        fold_p = probabilities[test_mask]
        fold_metrics.append(
            {
                "fold": fold,
                "queries": int(np.sum(test_mask)),
                "positives": int(np.sum(fold_y == 1)),
                "negatives": int(np.sum(fold_y == 0)),
                "auroc": auroc(fold_y, fold_p),
                "average_precision": average_precision(fold_y, fold_p),
                "brier": float(np.mean((fold_p - fold_y) ** 2)),
                "iterations": iterations,
                "converged": converged,
            }
        )
        preprocess_audit.append({"fold": fold, **preprocessing})
    if not np.all(np.isfinite(probabilities)):
        raise ValueError("Non-finite OOF probability")
    overall_auc = float(auroc(y, probabilities))
    overall_ap = float(average_precision(y, probabilities))
    brier = float(np.mean((probabilities - y) ** 2))
    intervals = bootstrap_binary_metrics(
        y,
        probabilities,
        BOOTSTRAP_ITERATIONS,
        f"oof::{task}::{panel_name}",
        include_brier=True,
    )
    original_indices = [index for index, row in enumerate(selected_rows) if row["score"] is not None]
    original_y = y[original_indices]
    original_score = np.asarray([selected_rows[index]["score"] for index in original_indices], dtype=np.float64)
    summary: dict[str, Any] = {
        "features": features,
        "queries": len(y),
        "positives": int(np.sum(y == 1)),
        "positive_prevalence": float(np.mean(y)),
        "auroc": overall_auc,
        "auroc_percentile95": intervals["auroc"],
        "average_precision": overall_ap,
        "average_precision_percentile95": intervals["average_precision"],
        "brier": brier,
        "brier_percentile95": intervals["brier"],
        "confusion_at_0_5": confusion_at_half(y, probabilities),
        "calibration": calibration_summary(y, probabilities),
        "folds": fold_metrics,
        "preprocessing_audit": preprocess_audit,
        "original_u1_score_complete_cases": len(original_indices),
        "original_u1_score_auroc": auroc(original_y, original_score),
        "original_u1_score_average_precision": average_precision(original_y, original_score),
    }
    if task == "TASK_A_GAIN_VS_HARM":
        type_metrics: dict[str, Any] = {}
        for question_type in sorted({row["question_type"] for row in selected_rows}):
            indices = [index for index, row in enumerate(selected_rows) if row["question_type"] == question_type]
            type_y = y[indices]
            type_metrics[question_type] = {
                "queries": len(indices),
                "positives": int(np.sum(type_y == 1)),
                "negatives": int(np.sum(type_y == 0)),
                "auroc": auroc(type_y, probabilities[indices])
                if int(np.sum(type_y == 1)) >= 5 and int(np.sum(type_y == 0)) >= 5
                else None,
                "average_precision": average_precision(type_y, probabilities[indices])
                if int(np.sum(type_y == 1)) >= 5 and int(np.sum(type_y == 0)) >= 5
                else None,
            }
        leave_one_out: dict[str, Any] = {}
        for question_type in sorted(type_metrics):
            indices = [index for index, row in enumerate(selected_rows) if row["question_type"] != question_type]
            leave_y = y[indices]
            leave_one_out[question_type] = {
                "queries": len(indices),
                "auroc": auroc(leave_y, probabilities[indices]),
                "average_precision": average_precision(leave_y, probabilities[indices]),
            }
        folds_above = sum(
            metric["auroc"] is not None and metric["auroc"] > 0.5 for metric in fold_metrics
        )
        eligible_leave_auc = [
            value["auroc"] for value in leave_one_out.values() if value["auroc"] is not None
        ]
        prevalence = float(np.mean(y))
        stable = (
            overall_auc >= 0.65
            and intervals["auroc"][0] > 0.5
            and overall_ap >= prevalence + 0.05
            and intervals["average_precision"][0] > prevalence
            and folds_above >= 4
            and bool(eligible_leave_auc)
            and all(value > 0.55 for value in eligible_leave_auc)
        )
        summary.update(
            {
                "question_type_metrics": type_metrics,
                "leave_one_question_type_out": leave_one_out,
                "fold_auroc_above_0_5": folds_above,
                "stable_gain_harm_signal": stable,
            }
        )
    return probabilities, fold_ids, fold_metrics, summary


def build_oof(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    validate_probe_features()
    output: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}
    for task in (
        "TASK_A_GAIN_VS_HARM",
        "TASK_B_GAIN_VS_NON_GAIN",
        "TASK_C_HARM_VS_NON_HARM",
    ):
        selected_rows, y = task_rows(rows, task)
        summary[task] = {}
        for panel_name, features in FEATURE_PANELS.items():
            probabilities, fold_ids, _, panel_summary = run_oof_panel(
                selected_rows, y, task, panel_name, features
            )
            summary[task][panel_name] = panel_summary
            for index, row in enumerate(selected_rows):
                output.append(
                    {
                        "task": task,
                        "feature_panel": panel_name,
                        "query_id": row["query_id"],
                        "question_type": row["question_type"],
                        "binary_label": int(y[index]),
                        "fold": int(fold_ids[index]),
                        "probability": float(probabilities[index]),
                        "prediction_at_0_5": int(probabilities[index] >= 0.5),
                        "original_u1_score": row["score"],
                    }
                )
    return output, summary


def mechanism_decomposition(
    rows: list[dict[str, Any]],
    feature_summary: dict[str, Any],
    deciles: list[dict[str, Any]],
) -> dict[str, Any]:
    readiness = feature_summary["readiness"]
    uncertainty = feature_summary["uncertainty"]
    score = feature_summary["score"]
    readiness_harm = (
        readiness["status"] == "PASS"
        and readiness["auroc_gain_high"] < 0.5
        and readiness["auroc_ci_high"] < 0.5
    )
    # Paired query bootstrap for the AUROC difference uses identical complete-case class resamples.
    event_rows = [
        row
        for row in rows
        if row["label"] in {"GAIN", "HARM"}
        and row["score"] is not None
        and row["uncertainty"] is not None
        and math.isfinite(float(row["score"]))
        and math.isfinite(float(row["uncertainty"]))
    ]
    gain_indices = np.asarray(
        [index for index, row in enumerate(event_rows) if row["label"] == "GAIN"], dtype=np.int64
    )
    harm_indices = np.asarray(
        [index for index, row in enumerate(event_rows) if row["label"] == "HARM"], dtype=np.int64
    )
    difference_interval: list[float] | None = None
    if len(gain_indices) >= 20 and len(harm_indices) >= 20:
        rng = np.random.default_rng(stable_seed("score_minus_uncertainty"))
        differences: list[float] = []
        for _ in range(BOOTSTRAP_ITERATIONS):
            indices = np.concatenate(
                [
                    rng.choice(gain_indices, len(gain_indices), replace=True),
                    rng.choice(harm_indices, len(harm_indices), replace=True),
                ]
            )
            y = np.asarray([int(event_rows[index]["label"] == "GAIN") for index in indices])
            score_values = np.asarray(
                [event_rows[index]["score"] for index in indices], dtype=np.float64
            )
            uncertainty_values = np.asarray(
                [event_rows[index]["uncertainty"] for index in indices], dtype=np.float64
            )
            differences.append(
                float(auroc(y, score_values)) - float(auroc(y, uncertainty_values))
            )
        difference_interval = percentile_interval(differences)
    decile_difference = [row["gain_rate"] - row["harm_rate"] for row in deciles]
    scale_diagnostics: dict[str, Any] = {}
    for feature in ("selected_edge_count", "planned_insert_count"):
        feature_result = feature_summary[feature]
        correlation = spearman(
            [row[feature] for row in rows],
            [row["q25_inserted_units"] for row in rows],
        )
        interval_contains_half = (
            feature_result["status"] == "PASS"
            and feature_result["auroc_ci_low"] <= 0.5 <= feature_result["auroc_ci_high"]
        )
        scale_diagnostics[feature] = {
            "auroc_gain_high": feature_result["auroc_gain_high"],
            "auroc_percentile95": [
                feature_result["auroc_ci_low"],
                feature_result["auroc_ci_high"],
            ],
            "auroc_interval_contains_0_5": interval_contains_half,
            "spearman_with_q25_inserted_count": correlation,
            "expansion_scale_not_benefit_signal": interval_contains_half
            and correlation is not None
            and abs(correlation) >= 0.5,
        }
    multiplication_flag = (
        readiness_harm
        and difference_interval is not None
        and difference_interval[1] < 0
    )
    return {
        "uncertainty_auroc_gain_high": uncertainty["auroc_gain_high"],
        "readiness_auroc_gain_high": readiness["auroc_gain_high"],
        "score_auroc_gain_high": score["auroc_gain_high"],
        "readiness_pushes_harm_high": readiness_harm,
        "score_minus_uncertainty_complete_case_gain": len(gain_indices),
        "score_minus_uncertainty_complete_case_harm": len(harm_indices),
        "score_minus_uncertainty_auroc_percentile95": difference_interval,
        "multiplication_amplifies_wrong_direction": multiplication_flag,
        "score_decile_gain_minus_harm_spearman": spearman(
            list(range(1, 11)), decile_difference
        ),
        "expansion_scale_diagnostics": scale_diagnostics,
    }


def assign_decision(
    oof_summary: dict[str, Any],
    all_on_off_limitation: bool,
    finite_feature_coverage_adequate: bool,
) -> tuple[str, dict[str, Any]]:
    task_a = oof_summary["TASK_A_GAIN_VS_HARM"]
    stable_panels = sorted(
        panel for panel, value in task_a.items() if value["stable_gain_harm_signal"]
    )
    weak_panels: list[str] = []
    for panel, value in task_a.items():
        interval = value["auroc_percentile95"]
        weak = (
            (value["auroc"] <= 0.60 or interval[0] <= 0.5 <= interval[1])
            and value["fold_auroc_above_0_5"] <= 2
        )
        if weak:
            weak_panels.append(panel)
    if not finite_feature_coverage_adequate:
        decision = "MECHANISM_EVIDENCE_INCONCLUSIVE"
    elif stable_panels and all_on_off_limitation:
        decision = "PROCEED_TO_U2_CANDIDATE_LEVEL_PROTOCOL_DESIGN"
    elif not stable_panels and len(weak_panels) == len(task_a) and not all_on_off_limitation:
        decision = "INSUFFICIENT_SIGNAL_STOP_CONTROLLER_LINE"
    else:
        decision = "MECHANISM_EVIDENCE_INCONCLUSIVE"
    return decision, {
        "stable_panels": stable_panels,
        "weak_panels": sorted(weak_panels),
        "all_on_off_limitation_evidence": all_on_off_limitation,
        "finite_feature_coverage_adequate": finite_feature_coverage_adequate,
    }


def finite_json(value: Any, location: str = "root") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            finite_json(nested, f"{location}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            finite_json(nested, f"{location}[{index}]")
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"Non-finite JSON value at {location}")


def csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Cannot write non-finite CSV value")
        return format(value, ".12g")
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return value


def render_csv(rows: Iterable[dict[str, Any]], columns: list[str]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    for row in rows:
        writer.writerow({column: csv_value(row.get(column)) for column in columns})
    return stream.getvalue().encode("utf-8")


def render_json(value: Any) -> bytes:
    finite_json(value)
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def validate_csv_bytes(payload: bytes, columns: list[str], expected_rows: int) -> None:
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8")))
    if reader.fieldnames != columns:
        raise ValueError("CSV column contract mismatch")
    rows = list(reader)
    if len(rows) != expected_rows:
        raise ValueError(f"CSV row count mismatch: {len(rows)} != {expected_rows}")


def build_artifacts(
    rows: list[dict[str, Any]],
    identities: dict[str, dict[str, Any]],
    repo_root: Path,
) -> tuple[dict[str, bytes], dict[str, Any]]:
    feature_rows, feature_summary = build_feature_separability(rows)
    decile_rows, decile_pattern = build_deciles(rows)
    mechanism_rows, mechanism_counts, limitation = build_mechanisms(rows)
    oof_rows, oof_summary = build_oof(rows)
    decomposition = mechanism_decomposition(rows, feature_summary, decile_rows)
    finite_feature_coverage_adequate = all(
        value["status"] == "PASS" for value in feature_summary.values()
    )
    decision, decision_evidence = assign_decision(
        oof_summary, limitation, finite_feature_coverage_adequate
    )

    artifacts: dict[str, bytes] = {
        "query_features": render_csv(rows, QUERY_COLUMNS),
        "feature_separability": render_csv(feature_rows, SEPARABILITY_COLUMNS),
        "score_deciles": render_csv(decile_rows, DECILE_COLUMNS),
        "candidate_mechanisms": render_csv(mechanism_rows, MECHANISM_COLUMNS),
        "oof_predictions": render_csv(oof_rows, OOF_COLUMNS),
    }
    counts = Counter(row["label"] for row in rows)
    summary = {
        "schema_version": SCHEMA_VERSION,
        "stage": "Stage4C-U1-FMA",
        "study_role": "post-Gold exploratory diagnosis",
        "protocol": {
            "path": PROTOCOL_PATH,
            "commit": PROTOCOL_COMMIT,
            "sha256": PROTOCOL_SHA256,
        },
        "implementation": {
            "path": "scripts/stage4c_u1_failure_mechanism_audit.py",
            "sha256": sha256_file(Path(__file__).resolve()),
            "git_head": git_head(repo_root),
            "numpy_version": np.__version__,
        },
        "inputs": identities,
        "frozen_reconciliation": {
            "queries": len(rows),
            "gain": counts["GAIN"],
            "harm": counts["HARM"],
            "neutral": counts["NEUTRAL"],
            "retained_gain": sum(
                row["trigger_u1"] for row in rows if row["label"] == "GAIN"
            ),
            "retained_harm": sum(
                row["trigger_u1"] for row in rows if row["label"] == "HARM"
            ),
            "stage4b_decision": "STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED",
        },
        "feature_separability": feature_summary,
        "ranking_deciles": {
            "feasible_queries": sum(row["feasible"] for row in rows),
            "pattern": decile_pattern,
        },
        "mechanism_categories": mechanism_counts,
        "all_on_off_limitation_evidence": limitation,
        "candidate_level_availability": {
            "candidate_gold_identity": False,
            "candidate_gold_rank": False,
            "candidate_numeric_scores": False,
            "support_similarity_facet_hyperedge_features": False,
            "available_rank_structure_features": RANK_PANEL,
            "status": "PARTIAL_QUERY_LEVEL_COMPOSITION_ONLY",
        },
        "uncertainty_readiness_decomposition": decomposition,
        "oof_probes": oof_summary,
        "decision": decision,
        "decision_evidence": decision_evidence,
        "evidence_boundaries": {
            "exploratory_only": True,
            "question_type_used_as_model_feature": False,
            "gold_used_as_model_feature": False,
            "reservation_accessed": False,
            "stage3b_accessed": False,
            "stage4b_controller_rerun": False,
            "stage4b_evaluator_rerun": False,
            "new_controller_efficacy_established": False,
            "stage4b_u1_d_negative_result_preserved": True,
        },
        "parameters": {
            "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "folds": FOLDS,
            "logistic_l2": LOGISTIC_L2,
            "logistic_max_iterations": LOGISTIC_MAX_ITERATIONS,
            "logistic_tolerance": LOGISTIC_TOLERANCE,
            "decision_threshold": 0.5,
        },
        "output_hashes": {
            OUTPUT_NAMES[name]: sha256_bytes(payload) for name, payload in artifacts.items()
        },
    }
    artifacts["summary"] = render_json(summary)

    validate_csv_bytes(artifacts["query_features"], QUERY_COLUMNS, len(rows))
    validate_csv_bytes(
        artifacts["feature_separability"], SEPARABILITY_COLUMNS, len(QUERY_FEATURES) * 4
    )
    validate_csv_bytes(artifacts["score_deciles"], DECILE_COLUMNS, 10)
    validate_csv_bytes(artifacts["candidate_mechanisms"], MECHANISM_COLUMNS, len(rows))
    expected_oof = 3 * (GAIN_COUNT + HARM_COUNT) + 3 * QUERY_COUNT + 3 * QUERY_COUNT
    validate_csv_bytes(artifacts["oof_predictions"], OOF_COLUMNS, expected_oof)
    parsed_summary = json.loads(artifacts["summary"])
    if parsed_summary["decision"] not in {
        "PROCEED_TO_U2_CANDIDATE_LEVEL_PROTOCOL_DESIGN",
        "INSUFFICIENT_SIGNAL_STOP_CONTROLLER_LINE",
        "MECHANISM_EVIDENCE_INCONCLUSIVE",
    }:
        raise ValueError("Invalid Stage4C decision")
    return artifacts, summary


def load_official_rows(repo_root: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    identities = verify_input_files(repo_root)
    policy = load_json(repo_root / INPUT_SPECS["policy"]["path"])
    pre_gold = load_json(repo_root / INPUT_SPECS["pre_gold"]["path"])
    gold_summary = load_json(repo_root / INPUT_SPECS["gold_summary"]["path"])
    post_gold = load_json(repo_root / INPUT_SPECS["post_gold"]["path"])
    if policy.get("evaluation_labels_loaded") is not False:
        raise ValueError("Frozen policy Gold boundary mismatch")
    if pre_gold.get("status") != "VERIFIED_PRE_GOLD" or pre_gold.get("gold_inputs_loaded") is not False:
        raise ValueError("Frozen pre-Gold verification mismatch")
    if post_gold.get("status") != "VERIFIED_POST_GOLD":
        raise ValueError("Frozen post-Gold verification mismatch")
    expected_decision = "STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED"
    if gold_summary.get("decision", {}).get("decision") != expected_decision:
        raise ValueError("Frozen Gold summary decision mismatch")
    if post_gold.get("decision", {}).get("decision") != expected_decision:
        raise ValueError("Frozen post-Gold decision mismatch")
    rows = validate_and_join(
        load_jsonl(repo_root / INPUT_SPECS["decisions"]["path"]),
        load_jsonl(repo_root / INPUT_SPECS["rankings"]["path"]),
        load_jsonl(repo_root / INPUT_SPECS["query_audit"]["path"]),
        enforce_official_counts=True,
    )
    verify_frozen_summary(rows, gold_summary, post_gold)
    return rows, identities


def promote_artifacts(output_dir: Path, artifacts: dict[str, bytes]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    final_paths = {name: output_dir / filename for name, filename in OUTPUT_NAMES.items()}
    existing = [str(path) for path in final_paths.values() if path.exists()]
    if existing:
        raise ValueError(f"Stage4C outputs already exist: {existing}")
    pending = output_dir / ".stage4c_u1_fma.pending"
    if pending.exists():
        raise ValueError(f"Pending Stage4C directory already exists: {pending}")
    pending.mkdir()
    promoted: list[Path] = []
    try:
        pending_paths: dict[str, Path] = {}
        for name, filename in OUTPUT_NAMES.items():
            path = pending / filename
            path.write_bytes(artifacts[name])
            pending_paths[name] = path
        for name, path in pending_paths.items():
            if path.read_bytes() != artifacts[name]:
                raise ValueError(f"Pending artifact byte mismatch: {name}")
        for name in OUTPUT_NAMES:
            destination = final_paths[name]
            os.replace(pending_paths[name], destination)
            promoted.append(destination)
    except Exception:
        for path in promoted:
            path.unlink(missing_ok=True)
        raise
    finally:
        if pending.exists():
            shutil.rmtree(pending)


def run_official(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    if output_dir.resolve() != (repo_root / "results").resolve():
        raise ValueError("Official Stage4C output directory must be repository results/")
    verify_protocol_and_repository(repo_root)
    rows, identities = load_official_rows(repo_root)
    artifacts, summary = build_artifacts(rows, identities, repo_root)
    promote_artifacts(output_dir, artifacts)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="results")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    summary = run_official(repo_root, (repo_root / args.output_dir).resolve())
    print(
        "STAGE4C_U1_FMA_PASS "
        f"queries={summary['frozen_reconciliation']['queries']} "
        f"decision={summary['decision']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
