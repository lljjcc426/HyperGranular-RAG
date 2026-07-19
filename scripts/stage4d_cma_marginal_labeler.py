"""Stage4D-CMA Channel B: Gold-only counterfactual labels.

Gold is accepted only by the in-memory labeling function and is used solely to
construct targets.  The future file-reading entry point fails before opening
any input unless Channel B receives a separate authorization.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from stage4d_cma_candidate_trace import load_json, load_jsonl
from stage4d_cma_candidate_trace_verifier import verify_channel_a_traces


CHANNEL_B_AUTH_ENV = "STAGE4D_CHANNEL_B_EXECUTION_AUTHORIZED"
CHANNEL_B_AUTH_VALUE = "AUTHORIZED_STAGE4D_CHANNEL_B"
GOLD_MAP_SHA256 = "76D15A88C218C9EDF36A9F9F52B0D2D9877463E5653EC8AB1E5C94542E99B30B"
EVALUATOR_AUDIT_SHA256 = "220FD7310AA187840A5E9D95174EBAF5BD4BDF6097BC58BACD28413D85377C17"

PRIMARY_LABELS = (
    "MARGINAL_GAIN",
    "DISPLACEMENT_HARM",
    "EVIDENCE_GAIN_ONLY",
    "EVIDENCE_HARM_ONLY",
    "INTERACTION_DEPENDENT",
    "REDUNDANT_GOLD",
    "NEUTRAL_NOISE",
)


def require_official_channel_b_authorization() -> None:
    if os.environ.get(CHANNEL_B_AUTH_ENV) != CHANNEL_B_AUTH_VALUE:
        raise PermissionError(
            "Official Stage4D Channel B is not authorized; no input was opened"
        )


def _id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a native non-empty string")
    return value


def _id_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, (list, set, tuple)):
        raise ValueError(f"{label} must be a list of IDs")
    result = [_id(item, f"{label}[]") for item in value]
    if len(result) != len(set(result)):
        raise ValueError(f"{label} contains duplicate IDs")
    return result


def _ranking(
    dense: list[str], inserted: Iterable[str], protect_n: int, effective_k: int
) -> list[str]:
    ranking = list(dense[:protect_n])
    seen = set(ranking)
    for unit_id in inserted:
        if unit_id not in seen and len(ranking) < effective_k:
            ranking.append(unit_id)
            seen.add(unit_id)
    for unit_id in dense:
        if len(ranking) >= effective_k:
            break
        if unit_id not in seen:
            ranking.append(unit_id)
            seen.add(unit_id)
    if len(ranking) != effective_k or len(set(ranking)) != effective_k:
        raise ValueError("counterfactual ranking reconstruction failed")
    return ranking


def _metrics(ranking: list[str], gold: set[str]) -> tuple[int, float]:
    if not gold:
        raise ValueError("Gold unit set must be non-empty")
    retrieved = set(ranking)
    er = len(retrieved & gold) / len(gold)
    cr = int(gold.issubset(retrieved))
    return cr, er


def _difference(left: int | float, right: int | float) -> int | float:
    value = left - right
    if isinstance(left, int) and isinstance(right, int):
        return int(value)
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("counterfactual delta must be finite")
    return 0.0 if result == 0.0 else result


def _primary_label(
    *,
    single_cr: int,
    single_er: float,
    loo_cr: int | None,
    loo_er: float | None,
    in_original: bool,
    candidate_is_gold: bool,
) -> str:
    if single_cr > 0:
        return "MARGINAL_GAIN"
    if single_cr < 0:
        return "DISPLACEMENT_HARM"
    if single_er > 0:
        return "EVIDENCE_GAIN_ONLY"
    if single_er < 0:
        return "EVIDENCE_HARM_ONLY"
    no_backfill_nonzero = (loo_cr not in (None, 0)) or (loo_er not in (None, 0.0))
    if in_original and no_backfill_nonzero:
        return "INTERACTION_DEPENDENT"
    return "REDUNDANT_GOLD" if candidate_is_gold else "NEUTRAL_NOISE"


def _replacement_subtype(cr_delta: int | None, er_delta: float | None) -> str:
    if cr_delta is None or er_delta is None:
        return "NOT_APPLICABLE"
    direction = cr_delta if cr_delta != 0 else er_delta
    if direction > 0:
        return "REPLACEMENT_BETTER_THAN_NEXT"
    if direction < 0:
        return "REPLACEMENT_WORSE_THAN_NEXT"
    return "REPLACEMENT_EQUIVALENT_TO_NEXT"


def _distribution(values: Iterable[int | float | None]) -> dict[str, Any]:
    finite = [float(value) for value in values if value is not None]
    if not finite:
        return {
            "count": 0,
            "maximum": None,
            "mean": None,
            "median": None,
            "minimum": None,
            "nonzero_count": 0,
        }
    if not all(math.isfinite(value) for value in finite):
        raise ValueError("summary distribution contains a non-finite value")
    return {
        "count": len(finite),
        "maximum": max(finite),
        "mean": statistics.fmean(finite),
        "median": statistics.median(finite),
        "minimum": min(finite),
        "nonzero_count": sum(value != 0.0 for value in finite),
    }


def label_candidates(
    query_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    gold_by_query: dict[str, list[str] | set[str] | tuple[str, ...]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Compute the frozen standardized-single and dual-LOO targets in memory."""

    if not isinstance(gold_by_query, dict):
        raise ValueError("gold_by_query must be an object")
    queries: dict[str, dict[str, Any]] = {}
    ordered_query_ids: list[str] = []
    for row in query_rows:
        query_id = _id(row.get("query_id"), "query_id")
        if query_id in queries:
            raise ValueError(f"duplicate query: {query_id}")
        queries[query_id] = row
        ordered_query_ids.append(query_id)
    if set(gold_by_query) != set(queries):
        raise ValueError("Gold/query ID sets differ")
    gold_sets = {
        query_id: set(_id_list(gold_by_query[query_id], f"{query_id}.gold"))
        for query_id in ordered_query_ids
    }
    if any(not values for values in gold_sets.values()):
        raise ValueError("every query requires at least one Gold unit")

    candidates_by_query: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in candidate_rows:
        query_id = _id(row.get("query_id"), "candidate.query_id")
        if query_id not in queries:
            raise ValueError(f"unknown candidate query: {query_id}")
        candidates_by_query[query_id].append(row)

    labels: list[dict[str, Any]] = []
    query_outcomes: dict[str, dict[str, Any]] = {}
    for query_id in ordered_query_ids:
        query = queries[query_id]
        dense = _id_list(query["dense_topk_unit_ids"], f"{query_id}.dense")
        eligible = _id_list(
            query["eligible_candidate_unit_ids"], f"{query_id}.eligible"
        )
        original = _id_list(query["q25_inserted_unit_ids"], f"{query_id}.inserted")
        q25 = _id_list(query["q25_topk_unit_ids"], f"{query_id}.q25")
        effective_k = query["effective_k"]
        protect_n = query["protect_n"]
        budget = query["planned_insert_budget"]
        if any(isinstance(value, bool) or not isinstance(value, int) for value in (effective_k, protect_n, budget)):
            raise ValueError(f"{query_id}: ranking scalars must be JSON integers")
        if original != eligible[: min(budget, len(eligible))]:
            raise ValueError(f"{query_id}: original insert prefix differs")
        if q25 != _ranking(dense, original, protect_n, effective_k):
            raise ValueError(f"{query_id}: q25 reconstruction differs")
        protected = set(dense[:protect_n])
        if protected & set(eligible):
            raise ValueError(f"{query_id}: protected-prefix candidate is invalid")
        rows = sorted(
            candidates_by_query.get(query_id, []),
            key=lambda row: row["candidate_rank_in_eligible_slice"],
        )
        if [row.get("candidate_unit_id") for row in rows] != eligible:
            raise ValueError(f"{query_id}: candidate trace does not cover full E_q")

        gold = gold_sets[query_id]
        dense_cr, dense_er = _metrics(dense, gold)
        q25_cr, q25_er = _metrics(q25, gold)
        query_outcomes[query_id] = {
            "dense_cr20": dense_cr,
            "dense_er20": dense_er,
            "q25_cr20": q25_cr,
            "q25_er20": q25_er,
        }

        for row in rows:
            unit_id = _id(row["candidate_unit_id"], f"{query_id}.candidate_unit_id")
            in_original = unit_id in set(original)
            original_flag = row["is_in_original_q25_insert_set"]
            if isinstance(original_flag, bool) or original_flag not in {0, 1}:
                raise ValueError(f"{query_id}:{unit_id}: original-set flag must be integer 0/1")
            if bool(original_flag) != in_original:
                raise ValueError(f"{query_id}:{unit_id}: original-set flag differs")

            single_ranking = _ranking(dense, [unit_id], protect_n, effective_k)
            single_cr, single_er = _metrics(single_ranking, gold)
            single_delta_cr = _difference(single_cr, dense_cr)
            single_delta_er = _difference(single_er, dense_er)

            removed = list(set(dense) - set(single_ranking))
            if len(removed) > 1:
                raise ValueError(f"{query_id}:{unit_id}: ambiguous displacement")
            displaced_id = removed[0] if removed else None
            if displaced_id != row["displaced_unit_id"]:
                raise ValueError(f"{query_id}:{unit_id}: displacement trace differs")

            if in_original:
                without_no_backfill = [item for item in original if item != unit_id]
                no_backfill_ranking = _ranking(
                    dense, without_no_backfill, protect_n, effective_k
                )
                no_backfill_cr, no_backfill_er = _metrics(no_backfill_ranking, gold)
                loo_no_cr: int | None = int(_difference(q25_cr, no_backfill_cr))
                loo_no_er: float | None = float(_difference(q25_er, no_backfill_er))

                without_candidate = [item for item in eligible if item != unit_id]
                replacement = without_candidate[: min(budget, len(without_candidate))]
                with_backfill_ranking = _ranking(
                    dense, replacement, protect_n, effective_k
                )
                with_backfill_cr, with_backfill_er = _metrics(
                    with_backfill_ranking, gold
                )
                loo_with_cr: int | None = int(_difference(q25_cr, with_backfill_cr))
                loo_with_er: float | None = float(_difference(q25_er, with_backfill_er))
            else:
                loo_no_cr = None
                loo_no_er = None
                loo_with_cr = None
                loo_with_er = None

            candidate_is_gold = unit_id in gold
            primary = _primary_label(
                single_cr=int(single_delta_cr),
                single_er=float(single_delta_er),
                loo_cr=loo_no_cr,
                loo_er=loo_no_er,
                in_original=in_original,
                candidate_is_gold=candidate_is_gold,
            )
            if primary not in PRIMARY_LABELS:
                raise AssertionError("unreachable label")
            labels.append(
                {
                    "candidate_budget_region": row["candidate_budget_region"],
                    "candidate_is_gold": int(candidate_is_gold),
                    "candidate_unit_id": unit_id,
                    "dataset": row["dataset"],
                    "delta_loo_no_backfill_cr": loo_no_cr,
                    "delta_loo_no_backfill_er": loo_no_er,
                    "delta_loo_with_backfill_cr": loo_with_cr,
                    "delta_loo_with_backfill_er": loo_with_er,
                    "delta_standardized_single_cr": int(single_delta_cr),
                    "delta_standardized_single_er": float(single_delta_er),
                    "displaced_unit_is_gold": int(displaced_id in gold if displaced_id else False),
                    "marginal_label": primary,
                    "provides_previously_unretrieved_gold": int(
                        candidate_is_gold and unit_id not in set(dense)
                    ),
                    "query_id": query_id,
                    "removes_previously_retrieved_gold": int(
                        displaced_id in gold if displaced_id else False
                    ),
                    "replacement_subtype": _replacement_subtype(
                        loo_with_cr, loo_with_er
                    ),
                    "sample_id": row["sample_id"],
                    "standardized_single_cr20": single_cr,
                    "standardized_single_er20": single_er,
                }
            )

    label_counts = Counter(row["marginal_label"] for row in labels)
    cluster_sets: dict[str, set[str]] = defaultdict(set)
    strata_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in labels:
        cluster_sets[row["marginal_label"]].add(row["query_id"])
        strata_counts[row["candidate_budget_region"]][row["marginal_label"]] += 1
    q25_gain = sum(
        outcome["q25_cr20"] > outcome["dense_cr20"]
        for outcome in query_outcomes.values()
    )
    q25_harm = sum(
        outcome["q25_cr20"] < outcome["dense_cr20"]
        for outcome in query_outcomes.values()
    )
    labels_by_query: dict[str, set[str]] = defaultdict(set)
    rows_by_query: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in labels:
        labels_by_query[row["query_id"]].add(row["marginal_label"])
        rows_by_query[row["query_id"]].append(row)
    direct_labels = {
        "MARGINAL_GAIN",
        "DISPLACEMENT_HARM",
        "EVIDENCE_GAIN_ONLY",
        "EVIDENCE_HARM_ONLY",
    }
    interaction_only_queries = sum(
        (
            outcome["q25_cr20"] != outcome["dense_cr20"]
            or outcome["q25_er20"] != outcome["dense_er20"]
        )
        and "INTERACTION_DEPENDENT" in labels_by_query.get(query_id, set())
        and not (labels_by_query.get(query_id, set()) & direct_labels)
        for query_id, outcome in query_outcomes.items()
    )
    delta_fields = (
        "delta_standardized_single_cr",
        "delta_standardized_single_er",
        "delta_loo_no_backfill_cr",
        "delta_loo_no_backfill_er",
        "delta_loo_with_backfill_cr",
        "delta_loo_with_backfill_er",
    )
    summary = {
        "budget_region_label_counts": {
            region: {label: int(counts.get(label, 0)) for label in PRIMARY_LABELS}
            for region, counts in sorted(strata_counts.items())
        },
        "candidate_rows": len(labels),
        "candidate_rows_per_query": _distribution(
            len(rows_by_query.get(query_id, [])) for query_id in ordered_query_ids
        ),
        "delta_distributions": {
            field: _distribution(row[field] for row in labels)
            for field in delta_fields
        },
        "delta_distributions_by_budget_region": {
            region: {
                field: _distribution(
                    row[field]
                    for row in labels
                    if row["candidate_budget_region"] == region
                )
                for field in delta_fields
            }
            for region in ("ORIGINAL_INSERT_SET", "BEYOND_ORIGINAL_BUDGET")
        },
        "interaction_only_q25_effect_queries": interaction_only_queries,
        "label_counts": {label: int(label_counts.get(label, 0)) for label in PRIMARY_LABELS},
        "label_query_cluster_counts": {
            label: len(cluster_sets.get(label, set())) for label in PRIMARY_LABELS
        },
        "q25_cr_gain_queries": q25_gain,
        "q25_cr_harm_queries": q25_harm,
        "queries_with_mixed_candidate_labels": sum(
            len(values) > 1 for values in labels_by_query.values()
        ),
        "queries": len(query_rows),
        "status": "CHANNEL_B_LABELS_BUILT_PENDING_VERIFICATION",
    }
    return labels, summary


def frozen_gold_targets(
    gold_map: dict[str, Any], expected_query_ids: list[str]
) -> dict[str, list[str]]:
    """Validate the frozen Stage4B Gold schema while dropping question type."""

    if not isinstance(gold_map, dict) or gold_map.get("schema_version") != "stage4b_u1_v2":
        raise ValueError("frozen Gold map schema version differs")
    rows = gold_map.get("queries")
    if not isinstance(rows, list):
        raise ValueError("frozen Gold map queries must be an array")
    targets: dict[str, list[str]] = {}
    ordered_ids: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"Gold row {index} must be an object")
        query_id = _id(row.get("query_id"), f"gold[{index}].query_id")
        if query_id in targets:
            raise ValueError(f"duplicate Gold query: {query_id}")
        if not isinstance(row.get("gold_unit_ids"), list):
            raise ValueError(f"gold[{index}].gold_unit_ids must be a JSON array")
        targets[query_id] = _id_list(
            row.get("gold_unit_ids"), f"gold[{index}].gold_unit_ids"
        )
        if not targets[query_id]:
            raise ValueError(f"empty Gold set: {query_id}")
        ordered_ids.append(query_id)
    if ordered_ids != expected_query_ids:
        raise ValueError("Gold/query row order or identity differs")
    digest_payload = "\n".join(sorted(ordered_ids)) + "\n"
    digest = hashlib.sha256(digest_payload.encode("utf-8")).hexdigest().upper()
    if gold_map.get("query_id_sha256") != digest:
        raise ValueError("frozen Gold query digest differs")
    return targets


def run_official_channel_b(
    query_trace_path: Path,
    candidate_trace_path: Path,
    channel_a_manifest_path: Path,
    channel_a_verification_path: Path,
    gold_map_path: Path,
    evaluator_audit_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Future official entry point; authorization precedes every file read."""

    require_official_channel_b_authorization()
    from stage4d_cma_candidate_trace import sha256_file

    if sha256_file(gold_map_path) != GOLD_MAP_SHA256:
        raise ValueError("frozen development Gold map hash differs")
    if sha256_file(evaluator_audit_path) != EVALUATOR_AUDIT_SHA256:
        raise ValueError("frozen evaluator channel audit hash differs")
    query_rows = load_jsonl(query_trace_path)
    candidate_rows = load_jsonl(candidate_trace_path)
    manifest = load_json(channel_a_manifest_path)
    verify_channel_a_traces(query_rows, candidate_rows, manifest)
    channel_a_verification = load_json(channel_a_verification_path)
    if (
        channel_a_verification.get("status") != "CHANNEL_A_TRACE_VERIFIED"
        or channel_a_verification.get("independent_reconstruction", {}).get("status")
        != "CHANNEL_A_INDEPENDENT_RECONSTRUCTION_VERIFIED"
    ):
        raise ValueError("committed Channel A verification status differs")
    evaluator_audit = load_json(evaluator_audit_path)
    if evaluator_audit.get("evaluator_channel_hashes", {}).get("gold_map") != GOLD_MAP_SHA256:
        raise ValueError("evaluator audit does not bind the frozen Gold map")
    raw_gold = load_json(gold_map_path)
    targets = frozen_gold_targets(
        raw_gold, [row["query_id"] for row in query_rows]
    )
    return label_candidates(query_rows, candidate_rows, targets)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query-trace", type=Path, required=True)
    parser.add_argument("--candidate-trace", type=Path, required=True)
    parser.add_argument("--channel-a-manifest", type=Path, required=True)
    parser.add_argument("--channel-a-verification", type=Path, required=True)
    parser.add_argument("--gold-map", type=Path, required=True)
    parser.add_argument("--evaluator-audit", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows, summary = run_official_channel_b(
        args.query_trace,
        args.candidate_trace,
        args.channel_a_manifest,
        args.channel_a_verification,
        args.gold_map,
        args.evaluator_audit,
    )
    print(json.dumps({"candidate_rows": len(rows), "summary": summary}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
