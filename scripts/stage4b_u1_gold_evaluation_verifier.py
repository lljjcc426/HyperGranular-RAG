"""Independently verify the authorized Stage4B-U1-D Gold evaluation outputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "stage4b_u1_v2"
IMPLEMENTATION_CHECKPOINT = "stage4b_u1_v2_3_1"
SCIENTIFIC_PROTOCOL = "docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md"
MAX_K = 20
PROTECT_N = 10
INSERT_BUDGET = 4


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream, object_pairs_hook=reject_duplicate_keys)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            value = json.loads(line, object_pairs_hook=reject_duplicate_keys)
            if not isinstance(value, dict):
                raise ValueError(f"Expected a JSON object at {path}:{line_number}")
            rows.append(value)
    return rows


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def resolve_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def require_exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise ValueError(f"{label} keys differ: {sorted(actual ^ expected)}")


def require_json_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be a JSON integer")
    return value


def verify_bound_file(repo_root: Path, binding: dict[str, Any], label: str) -> Path:
    require_exact_keys(binding, {"path", "sha256", "bytes"}, label)
    path = resolve_path(repo_root, str(binding["path"]))
    if not path.is_file():
        raise ValueError(f"{label} is missing: {path}")
    if path.stat().st_size != require_json_int(binding["bytes"], f"{label}.bytes"):
        raise ValueError(f"{label} byte length differs")
    if sha256_file(path) != str(binding["sha256"]):
        raise ValueError(f"{label} SHA-256 differs")
    return path


def validate_authorization_config(
    config_path: Path, *, require_outputs_absent: bool
) -> tuple[Path, dict[str, Any], dict[str, Path], dict[str, Path]]:
    repo_root = config_path.resolve().parents[1]
    config = load_json(config_path)
    require_exact_keys(
        config,
        {
            "schema_version",
            "run_id",
            "authorization",
            "runtime",
            "protocols",
            "implementation",
            "inputs",
            "parameters",
            "outputs",
            "commands",
            "advancement_gates",
            "stop_rules",
        },
        "config",
    )
    if config["schema_version"] != "stage4b_u1_gold_evaluation_v1":
        raise ValueError("Gold authorization schema differs")
    authorization = config["authorization"]
    if authorization.get("status") != "GRANTED":
        raise ValueError("Gold evaluation is not authorized")
    if authorization.get("scope") != "Stage4B-U1-D development Gold evaluation only":
        raise ValueError("Gold authorization scope differs")
    if bool(authorization.get("reservation_authorized")):
        raise ValueError("Reservation must remain unauthorized")

    runtime = config["runtime"]
    require_exact_keys(runtime, {"python_executable", "python_version"}, "runtime")

    bound_paths: dict[str, Path] = {}
    for group_name in ("protocols", "implementation", "inputs"):
        group = config[group_name]
        if not isinstance(group, dict) or not group:
            raise ValueError(f"{group_name} must be a non-empty object")
        for name, binding in group.items():
            if name == "evaluator_commit":
                continue
            if not isinstance(binding, dict):
                raise ValueError(f"{group_name}.{name} must be an object")
            bound_paths[f"{group_name}.{name}"] = verify_bound_file(
                repo_root, binding, f"{group_name}.{name}"
            )

    evaluator_commit = str(config["implementation"].get("evaluator_commit", ""))
    if len(evaluator_commit) != 40:
        raise ValueError("Evaluator commit must be a full Git SHA")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", evaluator_commit, "HEAD"],
        cwd=repo_root,
        check=False,
    )
    if ancestor.returncode != 0:
        raise ValueError("Evaluator commit is not an ancestor of HEAD")

    parameters = config["parameters"]
    require_exact_keys(
        parameters, {"run_role", "bootstrap_iterations", "bootstrap_seed"}, "parameters"
    )
    if parameters["run_role"] != "development":
        raise ValueError("Only development Gold evaluation is authorized")
    if require_json_int(parameters["bootstrap_iterations"], "bootstrap_iterations") != 10000:
        raise ValueError("Bootstrap iterations differ")
    if require_json_int(parameters["bootstrap_seed"], "bootstrap_seed") != 20260712:
        raise ValueError("Bootstrap seed differs")

    output_paths = {
        name: resolve_path(repo_root, str(value))
        for name, value in config["outputs"].items()
    }
    if set(output_paths) != {
        "primary_query_audit",
        "primary_summary",
        "rerun_query_audit",
        "rerun_summary",
        "verification",
    }:
        raise ValueError("Gold output path set differs")
    if len({path.resolve() for path in output_paths.values()}) != len(output_paths):
        raise ValueError("Gold output paths are not unique")
    if require_outputs_absent:
        existing = [str(path) for path in output_paths.values() if path.exists()]
        if existing:
            raise ValueError(f"Registered Gold output already exists: {existing}")
    return repo_root, config, bound_paths, output_paths


def retrieval_metrics(ranking: list[str], gold: set[str]) -> tuple[float, int]:
    retrieved = set(ranking[:20]) & gold
    return len(retrieved) / len(gold), int(gold.issubset(retrieved))


def derive_inserted_ids(ranking: dict[str, Any]) -> tuple[list[str], list[str]]:
    query_id = str(ranking["query_id"])
    dense = [str(value) for value in ranking["dense_top20_unit_ids"]]
    q25 = [str(value) for value in ranking["q25_top20_unit_ids"]]
    final = [str(value) for value in ranking["final_top20_unit_ids"]]
    planned = require_json_int(ranking["planned_insert_count"], f"planned {query_id}")
    trigger = require_json_int(ranking["trigger_u1"], f"trigger {query_id}")
    effective_k = len(dense)
    if not 1 <= effective_k <= MAX_K:
        raise ValueError(f"Effective-K differs: {query_id}")
    for label, values in (("dense", dense), ("q25", q25), ("final", final)):
        if len(values) != effective_k or len(set(values)) != effective_k:
            raise ValueError(f"{label} effective-K structure differs: {query_id}")
    protect = min(PROTECT_N, effective_k)
    if q25[:protect] != dense[:protect]:
        raise ValueError(f"Protected prefix differs: {query_id}")
    if not 0 <= planned <= min(INSERT_BUDGET, effective_k - protect):
        raise ValueError(f"Planned inserts differ: {query_id}")
    q25_inserted = q25[protect : protect + planned]
    if [str(value) for value in ranking["q25_inserted_unit_ids"]] != q25_inserted:
        raise ValueError(f"q25 inserted IDs differ: {query_id}")
    if trigger not in (0, 1):
        raise ValueError(f"Trigger differs: {query_id}")
    expected_final = q25 if trigger else dense
    final_inserted = q25_inserted if trigger else []
    if final != expected_final:
        raise ValueError(f"Final selector differs: {query_id}")
    if [str(value) for value in ranking["final_inserted_unit_ids"]] != final_inserted:
        raise ValueError(f"Final inserted IDs differ: {query_id}")
    return q25_inserted, final_inserted


def derive_query_audit(
    rankings: list[dict[str, Any]], gold_map: dict[str, Any]
) -> list[dict[str, Any]]:
    gold_by_query: dict[str, tuple[set[str], str]] = {}
    for row in gold_map["queries"]:
        query_id = str(row["query_id"])
        if query_id in gold_by_query:
            raise ValueError(f"Duplicate Gold query ID: {query_id}")
        gold = {str(value) for value in row["gold_unit_ids"]}
        if not gold:
            raise ValueError(f"Empty Gold set: {query_id}")
        gold_by_query[query_id] = (gold, str(row.get("question_type", "unknown")))
    if set(gold_by_query) != {str(row["query_id"]) for row in rankings}:
        raise ValueError("Ranking/Gold query ID sets differ")

    output: list[dict[str, Any]] = []
    for ranking in rankings:
        query_id = str(ranking["query_id"])
        gold, question_type = gold_by_query[query_id]
        dense_er, dense_cr = retrieval_metrics(ranking["dense_top20_unit_ids"], gold)
        q25_er, q25_cr = retrieval_metrics(ranking["q25_top20_unit_ids"], gold)
        u1_er, u1_cr = retrieval_metrics(ranking["final_top20_unit_ids"], gold)
        q25_inserted, u1_inserted = derive_inserted_ids(ranking)
        q25_inserted_gold = len(set(q25_inserted) & gold)
        u1_inserted_gold = len(set(u1_inserted) & gold)
        output.append(
            {
                "query_id": query_id,
                "dataset": str(ranking["dataset"]),
                "sample_id": str(ranking["sample_id"]),
                "question_type": question_type,
                "trigger_u1": int(ranking["trigger_u1"]),
                "planned_insert_count": int(ranking["planned_insert_count"]),
                "dense_er20": dense_er,
                "dense_cr20": dense_cr,
                "q25_er20": q25_er,
                "q25_cr20": q25_cr,
                "u1_er20": u1_er,
                "u1_cr20": u1_cr,
                "q25_gain_event": int(dense_cr == 0 and q25_cr == 1),
                "q25_harm_event": int(dense_cr == 1 and q25_cr == 0),
                "u1_gain_event": int(dense_cr == 0 and u1_cr == 1),
                "u1_harm_event": int(dense_cr == 1 and u1_cr == 0),
                "q25_inserted_units": len(q25_inserted),
                "q25_inserted_gold_units": q25_inserted_gold,
                "q25_inserted_non_gold_units": len(q25_inserted) - q25_inserted_gold,
                "u1_inserted_units": len(u1_inserted),
                "u1_inserted_gold_units": u1_inserted_gold,
                "u1_inserted_non_gold_units": len(u1_inserted) - u1_inserted_gold,
            }
        )
    return output


def exact_mcnemar_two_sided_pvalue(gains: int, harms: int) -> float:
    discordant = gains + harms
    if discordant == 0:
        return 1.0
    tail = sum(math.comb(discordant, value) for value in range(min(gains, harms) + 1))
    return min(1.0, 2.0 * tail / (2.0**discordant))


def fisher_greater_pvalue(
    selected_gains: int, gains: int, selected_harms: int, harms: int
) -> float:
    if gains <= 0 or harms <= 0:
        return 1.0
    selected_total = selected_gains + selected_harms
    population = gains + harms
    lower = max(0, selected_total - harms)
    upper = min(gains, selected_total)
    denominator = math.comb(population, selected_total)
    return sum(
        math.comb(gains, value) * math.comb(harms, selected_total - value) / denominator
        for value in range(max(selected_gains, lower), upper + 1)
    )


def summarize(items: list[dict[str, Any]], label: str) -> dict[str, Any]:
    n = len(items)
    if n == 0:
        return {"slice": label, "queries": 0}
    q25_gains = sum(int(row["q25_gain_event"]) for row in items)
    q25_harms = sum(int(row["q25_harm_event"]) for row in items)
    retained_gains = sum(int(row["q25_gain_event"]) * int(row["trigger_u1"]) for row in items)
    retained_harms = sum(int(row["q25_harm_event"]) * int(row["trigger_u1"]) for row in items)
    gain_retention = retained_gains / q25_gains if q25_gains else None
    harm_retention = retained_harms / q25_harms if q25_harms else None
    retention_gap = (
        gain_retention - harm_retention
        if gain_retention is not None and harm_retention is not None
        else None
    )
    q25_inserted = sum(int(row["q25_inserted_units"]) for row in items)
    u1_inserted = sum(int(row["u1_inserted_units"]) for row in items)
    q25_non_gold = sum(int(row["q25_inserted_non_gold_units"]) for row in items)
    u1_non_gold = sum(int(row["u1_inserted_non_gold_units"]) for row in items)
    return {
        "slice": label,
        "queries": n,
        "dense_er20": sum(float(row["dense_er20"]) for row in items) / n,
        "dense_cr20": sum(float(row["dense_cr20"]) for row in items) / n,
        "q25_er20": sum(float(row["q25_er20"]) for row in items) / n,
        "q25_cr20": sum(float(row["q25_cr20"]) for row in items) / n,
        "u1_er20": sum(float(row["u1_er20"]) for row in items) / n,
        "u1_cr20": sum(float(row["u1_cr20"]) for row in items) / n,
        "u1_cr20_delta_vs_dense": sum(
            float(row["u1_cr20"]) - float(row["dense_cr20"]) for row in items
        )
        / n,
        "u1_cr20_delta_vs_q25": sum(
            float(row["u1_cr20"]) - float(row["q25_cr20"]) for row in items
        )
        / n,
        "q25_gain_events": q25_gains,
        "q25_harm_events": q25_harms,
        "retained_gain_events": retained_gains,
        "retained_harm_events": retained_harms,
        "gain_retention": gain_retention,
        "harm_retention": harm_retention,
        "retention_gap": retention_gap,
        "fisher_greater_pvalue": fisher_greater_pvalue(
            retained_gains, q25_gains, retained_harms, q25_harms
        ),
        "mcnemar_two_sided_pvalue": exact_mcnemar_two_sided_pvalue(
            sum(int(row["u1_gain_event"]) for row in items),
            sum(int(row["u1_harm_event"]) for row in items),
        ),
        "q25_inserted_units": q25_inserted,
        "u1_inserted_units": u1_inserted,
        "inserted_unit_reduction": 1.0 - u1_inserted / q25_inserted if q25_inserted else None,
        "q25_conditional_false_insert_rate": q25_non_gold / q25_inserted if q25_inserted else None,
        "u1_conditional_false_insert_rate": u1_non_gold / u1_inserted if u1_inserted else None,
    }


def build_decision(summary: dict[str, Any]) -> dict[str, Any]:
    false_insert_delta = None
    if (
        summary["u1_conditional_false_insert_rate"] is not None
        and summary["q25_conditional_false_insert_rate"] is not None
    ):
        false_insert_delta = (
            summary["u1_conditional_false_insert_rate"]
            - summary["q25_conditional_false_insert_rate"]
        )
    checks = {
        "resource_reduction_at_least_0_40": summary["inserted_unit_reduction"] is not None
        and summary["inserted_unit_reduction"] >= 0.40,
        "retention_gap_at_least_0_15": summary["retention_gap"] is not None
        and summary["retention_gap"] >= 0.15,
        "fisher_zero_null_rejected": summary["fisher_greater_pvalue"] < 0.05,
        "observed_cr20_delta_vs_dense_at_least_0_005": summary[
            "u1_cr20_delta_vs_dense"
        ]
        >= 0.005,
        "observed_cr20_delta_vs_q25_at_least_minus_0_005": summary[
            "u1_cr20_delta_vs_q25"
        ]
        >= -0.005,
        "false_insert_rate_not_worse_by_more_than_0_01": false_insert_delta is not None
        and false_insert_delta <= 0.01,
    }
    passed = all(checks.values())
    return {
        "run_role": "development",
        "checks": checks,
        "passed": passed,
        "decision": "ELIGIBLE_FOR_U1_R_APPROVAL_REQUEST"
        if passed
        else "STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED",
    }


def baseline_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    return {
        "queries": n,
        "dense_er20": sum(float(row["dense_er20"]) for row in rows) / n,
        "dense_cr20": sum(float(row["dense_cr20"]) for row in rows) / n,
        "q25_er20": sum(float(row["q25_er20"]) for row in rows) / n,
        "q25_cr20": sum(float(row["q25_cr20"]) for row in rows) / n,
        "q25_gain_events": sum(int(row["q25_gain_event"]) for row in rows),
        "q25_harm_events": sum(int(row["q25_harm_event"]) for row in rows),
    }


def load_stage4a_reference(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    by_strategy = {
        str(row["strategy_id"]): row for row in rows if str(row["slice"]) == "ALL"
    }
    dense = by_strategy["dense_fixed"]
    q25 = by_strategy["allquery_q25_p10_i4"]
    return {
        "queries": int(dense["queries"]),
        "dense_er20": float(dense["evidence_recall_at_20"]),
        "dense_cr20": float(dense["chain_recall_at_20"]),
        "q25_er20": float(q25["evidence_recall_at_20"]),
        "q25_cr20": float(q25["chain_recall_at_20"]),
        "q25_gain_events": int(q25["gain_events"]),
        "q25_harm_events": int(q25["harm_events"]),
    }


def verify_exact_repeat(primary: Path, rerun: Path, label: str) -> None:
    if primary.read_bytes() != rerun.read_bytes():
        raise ValueError(f"Deterministic rerun bytes differ: {label}")


def write_json_exclusive(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")


def verify_outputs(config_path: Path) -> dict[str, Any]:
    repo_root, config, bound, outputs = validate_authorization_config(
        config_path, require_outputs_absent=False
    )
    for name in (
        "primary_query_audit",
        "primary_summary",
        "rerun_query_audit",
        "rerun_summary",
    ):
        if not outputs[name].is_file():
            raise ValueError(f"Gold output is missing: {name}")
    if outputs["verification"].exists():
        raise ValueError("Gold verification output already exists")

    verify_exact_repeat(
        outputs["primary_query_audit"], outputs["rerun_query_audit"], "query audit"
    )
    verify_exact_repeat(outputs["primary_summary"], outputs["rerun_summary"], "summary")

    rankings = load_jsonl(bound["inputs.rankings"])
    gold_map = load_json(bound["inputs.gold_map"])
    expected_rows = derive_query_audit(rankings, gold_map)
    actual_rows = load_jsonl(outputs["primary_query_audit"])
    if actual_rows != expected_rows:
        raise ValueError("Independent query-audit recomputation differs")

    summary = load_json(outputs["primary_summary"])
    expected_overall = summarize(expected_rows, "ALL")
    if summary.get("overall") != expected_overall:
        raise ValueError("Independent overall summary differs")
    question_types = sorted({str(row["question_type"]) for row in expected_rows})
    expected_types = [
        summarize(
            [row for row in expected_rows if row["question_type"] == question_type],
            question_type,
        )
        for question_type in question_types
    ]
    if summary.get("question_types") != expected_types:
        raise ValueError("Independent question-type summaries differ")
    expected_caution = [
        row["slice"]
        for row in expected_types
        if row["queries"] > 0
        and (
            row["u1_cr20_delta_vs_dense"] <= -0.02
            or row["retained_harm_events"] > row["retained_gain_events"]
        )
    ]
    if summary.get("subgroup_caution") != expected_caution:
        raise ValueError("Independent subgroup-caution derivation differs")

    expected_hashes = {
        "ranking_sha256": sha256_file(bound["inputs.rankings"]),
        "policy_sha256": sha256_file(bound["inputs.policy"]),
        "pre_gold_verification_sha256": sha256_file(bound["inputs.pre_gold_verification"]),
        "gold_map_sha256": sha256_file(bound["inputs.gold_map"]),
        "evaluator_audit_sha256": sha256_file(bound["inputs.evaluator_audit"]),
        "query_audit_sha256": sha256_file(outputs["primary_query_audit"]),
        "evaluator_source_sha256": sha256_file(bound["implementation.evaluator"]),
    }
    for key, expected in expected_hashes.items():
        if summary.get(key) != expected:
            raise ValueError(f"Evaluation summary binding differs: {key}")
    if summary.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Evaluation summary schema differs")
    if summary.get("implementation_checkpoint") != IMPLEMENTATION_CHECKPOINT:
        raise ValueError("Evaluation implementation checkpoint differs")
    if summary.get("protocol") != SCIENTIFIC_PROTOCOL:
        raise ValueError("Evaluation scientific protocol differs")
    if summary.get("run_role") != "development":
        raise ValueError("Evaluation run role differs")

    observed_baseline = baseline_metrics(expected_rows)
    stage4a_reference = load_stage4a_reference(bound["inputs.stage4a_r2_strategy_summary"])
    if observed_baseline != stage4a_reference:
        raise ValueError("Independent Stage4A-R2 baseline equivalence differs")
    baseline = summary.get("baseline_equivalence", {})
    if baseline.get("passed") is not True or baseline.get("observed") != observed_baseline:
        raise ValueError("Evaluation baseline-equivalence record differs")
    if baseline.get("reference_sha256") != sha256_file(
        bound["inputs.stage4a_r2_verification"]
    ):
        raise ValueError("Stage4A-R2 verification binding differs")
    if baseline.get("strategy_summary_sha256") != sha256_file(
        bound["inputs.stage4a_r2_strategy_summary"]
    ):
        raise ValueError("Stage4A-R2 strategy-summary binding differs")

    parameters = config["parameters"]
    bootstrap = summary.get("bootstrap", {})
    if bootstrap.get("iterations") != parameters["bootstrap_iterations"]:
        raise ValueError("Bootstrap iterations differ")
    if bootstrap.get("seed") != parameters["bootstrap_seed"]:
        raise ValueError("Bootstrap seed differs")
    expected_decision = build_decision(expected_overall)
    if summary.get("decision") != expected_decision:
        raise ValueError("Independent advancement decision differs")

    output_hashes = {
        name: sha256_file(path)
        for name, path in outputs.items()
        if name != "verification"
    }
    result = {
        "schema_version": "stage4b_u1_gold_evaluation_verification_v1",
        "status": "VERIFIED_POST_GOLD",
        "authorization_config": config_path.resolve().relative_to(repo_root).as_posix(),
        "authorization_config_sha256": sha256_file(config_path),
        "queries": len(expected_rows),
        "checks": {
            "input_bindings": "PASS",
            "deterministic_rerun_byte_equality": "PASS",
            "query_audit_independent_recomputation": "PASS",
            "overall_summary_independent_recomputation": "PASS",
            "question_type_summary_independent_recomputation": "PASS",
            "subgroup_caution_independent_recomputation": "PASS",
            "stage4a_r2_baseline_equivalence": "PASS",
            "bootstrap_identity": "PASS",
            "advancement_decision_independent_recomputation": "PASS",
        },
        "input_hashes": {
            name.split(".", 1)[1]: sha256_file(path)
            for name, path in bound.items()
            if name.startswith("inputs.")
        },
        "output_hashes": output_hashes,
        "decision": expected_decision,
    }
    write_json_exclusive(outputs["verification"], result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--preflight-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.preflight_only:
        validate_authorization_config(args.config, require_outputs_absent=True)
        print("STAGE4B_U1_GOLD_AUTHORIZATION_PREFLIGHT_PASS")
        return
    result = verify_outputs(args.config)
    print(
        "STAGE4B_U1_GOLD_INDEPENDENT_VERIFICATION_PASS "
        f"queries={result['queries']} decision={result['decision']['decision']}"
    )


if __name__ == "__main__":
    main()
