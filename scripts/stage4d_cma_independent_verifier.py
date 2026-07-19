"""Independent recomputation checks for Stage4D-CMA labels and OOF outputs."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Iterable

import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import GroupKFold

from stage4d_cma_candidate_trace_verifier import verify_channel_a_traces


SEED = 20260719
PANELS = (
    "RELEVANCE_RANK_8",
    "SUPPORT_STRUCTURE_10",
    "COMPLEMENTARITY_RISK_10",
    "COMBINED_DEPLOYABLE_28",
)
TASK_LABELS = {
    "TASK_A_GAIN_VS_ALL": ("MARGINAL_GAIN", None),
    "TASK_B_HARM_VS_ALL": ("DISPLACEMENT_HARM", None),
    "TASK_C_GAIN_VS_HARM": ("MARGINAL_GAIN", "DISPLACEMENT_HARM"),
}
PRIMARY_LABELS = {
    "MARGINAL_GAIN",
    "DISPLACEMENT_HARM",
    "EVIDENCE_GAIN_ONLY",
    "EVIDENCE_HARM_ONLY",
    "INTERACTION_DEPENDENT",
    "REDUNDANT_GOLD",
    "NEUTRAL_NOISE",
}
PREDICTION_KEYS = {
    "candidate_budget_region",
    "candidate_unit_id",
    "fold",
    "label",
    "panel",
    "probability",
    "query_id",
    "task",
}


def _ids(value: Any, label: str) -> list[str]:
    if not isinstance(value, (list, set, tuple)):
        raise ValueError(f"{label} must be a list")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item:
            raise ValueError(f"{label} contains a non-string ID")
        result.append(item)
    if len(result) != len(set(result)):
        raise ValueError(f"{label} contains duplicate IDs")
    return result


def _ranking(dense: list[str], inserted: Iterable[str], protect_n: int, k: int) -> list[str]:
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


def _metrics(ranking: list[str], gold: set[str]) -> tuple[int, float]:
    retrieved = set(ranking)
    return int(gold.issubset(retrieved)), len(retrieved & gold) / len(gold)


def _replacement(cr_delta: int | None, er_delta: float | None) -> str:
    if cr_delta is None or er_delta is None:
        return "NOT_APPLICABLE"
    direction = cr_delta if cr_delta else er_delta
    if direction > 0:
        return "REPLACEMENT_BETTER_THAN_NEXT"
    if direction < 0:
        return "REPLACEMENT_WORSE_THAN_NEXT"
    return "REPLACEMENT_EQUIVALENT_TO_NEXT"


def _label(single_cr: int, single_er: float, loo_cr: int | None, loo_er: float | None, in_original: bool, is_gold: bool) -> str:
    if single_cr > 0:
        return "MARGINAL_GAIN"
    if single_cr < 0:
        return "DISPLACEMENT_HARM"
    if single_er > 0:
        return "EVIDENCE_GAIN_ONLY"
    if single_er < 0:
        return "EVIDENCE_HARM_ONLY"
    if in_original and ((loo_cr not in (None, 0)) or (loo_er not in (None, 0.0))):
        return "INTERACTION_DEPENDENT"
    return "REDUNDANT_GOLD" if is_gold else "NEUTRAL_NOISE"


def verify_candidate_labels(
    query_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    label_rows: list[dict[str, Any]],
    gold_by_query: dict[str, list[str] | set[str] | tuple[str, ...]],
) -> dict[str, Any]:
    queries = {row["query_id"]: row for row in query_rows}
    candidates = {
        (row["query_id"], row["candidate_unit_id"]): row for row in candidate_rows
    }
    labels = {(row["query_id"], row["candidate_unit_id"]): row for row in label_rows}
    if len(candidates) != len(candidate_rows) or len(labels) != len(label_rows):
        raise ValueError("duplicate candidate or label identity")
    if set(labels) != set(candidates):
        raise ValueError("candidate/label identity sets differ")
    if set(gold_by_query) != set(queries):
        raise ValueError("Gold/query identity sets differ")

    for query_id, query in queries.items():
        dense = _ids(query["dense_topk_unit_ids"], f"{query_id}.dense")
        eligible = _ids(query["eligible_candidate_unit_ids"], f"{query_id}.eligible")
        original = _ids(query["q25_inserted_unit_ids"], f"{query_id}.inserted")
        gold = set(_ids(gold_by_query[query_id], f"{query_id}.gold"))
        if not gold:
            raise ValueError(f"{query_id}: empty Gold set")
        protect_n = query["protect_n"]
        budget = query["planned_insert_budget"]
        k = query["effective_k"]
        q25 = _ranking(dense, original, protect_n, k)
        dense_cr, dense_er = _metrics(dense, gold)
        q25_cr, q25_er = _metrics(q25, gold)
        for unit_id in eligible:
            candidate = candidates[(query_id, unit_id)]
            observed = labels[(query_id, unit_id)]
            in_original = unit_id in original
            single = _ranking(dense, [unit_id], protect_n, k)
            single_cr_value, single_er_value = _metrics(single, gold)
            single_cr = single_cr_value - dense_cr
            single_er = single_er_value - dense_er
            displaced = list(set(dense) - set(single))
            if len(displaced) > 1 or (displaced[0] if displaced else None) != candidate["displaced_unit_id"]:
                raise ValueError(f"{query_id}:{unit_id}: displacement recomputation differs")
            if in_original:
                no_backfill = _ranking(
                    dense, [item for item in original if item != unit_id], protect_n, k
                )
                no_cr_value, no_er_value = _metrics(no_backfill, gold)
                loo_no_cr: int | None = q25_cr - no_cr_value
                loo_no_er: float | None = q25_er - no_er_value
                eligible_without = [item for item in eligible if item != unit_id]
                with_backfill = _ranking(
                    dense, eligible_without[: min(budget, len(eligible_without))], protect_n, k
                )
                with_cr_value, with_er_value = _metrics(with_backfill, gold)
                loo_with_cr: int | None = q25_cr - with_cr_value
                loo_with_er: float | None = q25_er - with_er_value
            else:
                loo_no_cr = loo_no_er = loo_with_cr = loo_with_er = None
            expected = {
                "candidate_is_gold": int(unit_id in gold),
                "delta_loo_no_backfill_cr": loo_no_cr,
                "delta_loo_no_backfill_er": loo_no_er,
                "delta_loo_with_backfill_cr": loo_with_cr,
                "delta_loo_with_backfill_er": loo_with_er,
                "delta_standardized_single_cr": single_cr,
                "delta_standardized_single_er": single_er,
                "marginal_label": _label(
                    single_cr, single_er, loo_no_cr, loo_no_er, in_original, unit_id in gold
                ),
                "replacement_subtype": _replacement(loo_with_cr, loo_with_er),
            }
            for field, value in expected.items():
                if observed.get(field) != value:
                    raise ValueError(f"{query_id}:{unit_id}: {field} differs")
            if observed["marginal_label"] not in PRIMARY_LABELS:
                raise ValueError(f"{query_id}:{unit_id}: unknown primary label")
    return {"candidate_rows": len(label_rows), "status": "CHANNEL_B_LABELS_VERIFIED"}


def _independent_folds(query_ids: list[str]) -> dict[str, int]:
    unique = list(dict.fromkeys(query_ids))
    x = np.arange(len(unique), dtype=np.int64).reshape(-1, 1)
    groups = np.asarray(unique, dtype=object)
    assignments: dict[str, int] = {}
    splitter = GroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    for fold, (_, test) in enumerate(splitter.split(x, groups=groups)):
        for index in test:
            assignments[unique[int(index)]] = fold
    return assignments


def _metric_subset(y: np.ndarray, p: np.ndarray) -> dict[str, float | None]:
    return {
        "ap": float(average_precision_score(y, p)) if len(np.unique(y)) == 2 else None,
        "auroc": float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None,
        "brier": float(brier_score_loss(y, p)),
    }


def verify_probe_outputs(
    candidate_rows: list[dict[str, Any]],
    label_rows: list[dict[str, Any]],
    probe: dict[str, Any],
) -> dict[str, Any]:
    if probe.get("status") not in {
        "SYNTHETIC_STAGE4D_PROBE_COMPLETE",
        "OFFICIAL_STAGE4D_PROBE_COMPLETE_PENDING_FINAL_VERIFICATION",
    }:
        raise ValueError("probe status differs")
    identities = {
        (row["query_id"], row["candidate_unit_id"]): row for row in label_rows
    }
    regions = {
        (row["query_id"], row["candidate_unit_id"]): row["candidate_budget_region"]
        for row in candidate_rows
    }
    folds = _independent_folds([row["query_id"] for row in candidate_rows])
    if probe.get("fold_assignments") != folds:
        raise ValueError("independent fold assignment differs")
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    seen: set[tuple[str, str, str, str]] = set()
    for row in probe.get("oof_predictions", []):
        if not isinstance(row, dict) or set(row) != PREDICTION_KEYS:
            raise ValueError("OOF prediction schema differs")
        key = (row["query_id"], row["candidate_unit_id"])
        if key not in identities or regions[key] != row["candidate_budget_region"]:
            raise ValueError("OOF prediction identity/region differs")
        if row["fold"] != folds[row["query_id"]]:
            raise ValueError("OOF row/query fold differs")
        if row["task"] not in TASK_LABELS or row["panel"] not in PANELS:
            raise ValueError("OOF task/panel differs")
        probability = row["probability"]
        if isinstance(probability, bool) or not isinstance(probability, float) or not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
            raise ValueError("OOF probability contract differs")
        unique_key = (row["task"], row["panel"], *key)
        if unique_key in seen:
            raise ValueError("duplicate OOF prediction")
        seen.add(unique_key)
        positive, negative = TASK_LABELS[row["task"]]
        label_name = identities[key]["marginal_label"]
        if negative is not None and label_name not in {positive, negative}:
            raise ValueError("Task C contains an ER-only/other label")
        expected_label = int(label_name == positive)
        if isinstance(row["label"], bool) or row["label"] != expected_label:
            raise ValueError("OOF binary label differs")
        grouped[(row["task"], row["panel"])].append(row)

    results = probe.get("results")
    if not isinstance(results, dict) or set(results) != set(TASK_LABELS):
        raise ValueError("probe task result set differs")
    for task, task_result in results.items():
        panels = task_result.get("panels")
        if not task_result["feasibility"]["eligible"]:
            if panels:
                raise ValueError("ineligible task unexpectedly has fitted panels")
            continue
        if set(panels) != set(PANELS):
            raise ValueError("eligible task does not report all fixed panels")
        for panel in PANELS:
            rows = grouped[(task, panel)]
            y = np.asarray([row["label"] for row in rows], dtype=np.int64)
            p = np.asarray([row["probability"] for row in rows], dtype=np.float64)
            expected = _metric_subset(y, p)
            observed = panels[panel]
            for metric, value in expected.items():
                if observed.get(metric) != value:
                    raise ValueError(f"{task}/{panel}: {metric} differs")
            for region in ("ORIGINAL_INSERT_SET", "BEYOND_ORIGINAL_BUDGET"):
                mask = np.asarray(
                    [row["candidate_budget_region"] == region for row in rows], dtype=bool
                )
                observed_region = observed["candidate_budget_regions"][region]
                if not mask.any():
                    if observed_region["metrics"] is not None:
                        raise ValueError(f"{task}/{panel}/{region}: empty stratum differs")
                else:
                    expected_region = _metric_subset(y[mask], p[mask])
                    for metric, value in expected_region.items():
                        if observed_region["metrics"].get(metric) != value:
                            raise ValueError(f"{task}/{panel}/{region}: {metric} differs")
    return {
        "oof_prediction_rows": len(probe.get("oof_predictions", [])),
        "status": "STAGE4D_PROBE_VERIFIED",
    }


def verify_synthetic_stage4d(
    query_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    manifest: dict[str, Any],
    label_rows: list[dict[str, Any]],
    gold_by_query: dict[str, list[str] | set[str] | tuple[str, ...]],
    probe: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = {
        "channel_a": verify_channel_a_traces(query_rows, candidate_rows, manifest),
        "channel_b": verify_candidate_labels(
            query_rows, candidate_rows, label_rows, gold_by_query
        ),
    }
    if probe is not None:
        result["probe"] = verify_probe_outputs(candidate_rows, label_rows, probe)
    result["status"] = "STAGE4D_SYNTHETIC_INDEPENDENT_VERIFICATION_PASSED"
    return result
