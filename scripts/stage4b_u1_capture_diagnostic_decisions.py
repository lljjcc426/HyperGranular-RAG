"""Capture decisions only in an OS temporary directory for Amendment 5 diagnostics."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
from typing import Any

from stage4b_u1_common import (
    FROZEN_BATCH_SIZE,
    FROZEN_MAX_LENGTH,
    FROZEN_MODEL_NAME,
    assert_no_prohibited_keys,
    load_json,
    load_jsonl,
    sha256_file,
    write_json,
    write_jsonl,
)
from stage4b_u1_compare_decisions import (
    DIAGNOSTIC_CHECKPOINT,
    compare_decisions_files,
)
from stage4b_u1_goldfree_controller import (
    load_or_build_embeddings,
    validate_channel_audit,
    validate_controller_inputs,
)
from stage4b_u1_goldfree_retrieval import (
    RetrievalConfig,
    allocate_budget,
    build_query_decisions,
    fit_ecdf_references,
    score_rows,
)


OFFICIAL_5B_AUTHORIZATION_TOKEN = (
    "APPROVE_STAGE4B_U1_D_AMENDMENT_5B_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC"
)
DECISION_FIELDS = {
    "query_id",
    "dataset",
    "sample_id",
    "ball_score_margin",
    "boundary_margin",
    "selected_edge_count",
    "planned_insert_count",
    "feasible",
    "u_margin",
    "u_boundary",
    "r_edge",
    "r_candidate",
    "uncertainty",
    "readiness",
    "score",
    "tie_hash",
    "ordered_rank",
    "trigger_u1",
}


def _assert_under_root(path: Path, root: Path, label: str) -> None:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"Synthetic {label} path is outside the allowlist root") from exc


def validate_synthetic_path_allowlist(paths: dict[str, Path], root: Path) -> None:
    if not root.is_dir():
        raise ValueError("Synthetic allowlist root must exist")
    for label, path in paths.items():
        _assert_under_root(path, root, label)


def compute_decisions_only(
    units: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    unit_embeddings: Any,
    query_embeddings: Any,
    config: RetrievalConfig,
) -> list[dict[str, Any]]:
    """Mirror the existing development decisions computation without rankings/policy."""
    rows = build_query_decisions(
        units, queries, unit_embeddings, query_embeddings, config
    )
    references = fit_ecdf_references(rows)
    score_rows(rows, references)
    allocate_budget(rows, config.budget_fraction)
    decisions = [{key: row[key] for key in DECISION_FIELDS} for row in rows]
    assert_no_prohibited_keys(decisions, "diagnostic.decisions")
    return decisions


def generate_decisions_only_from_inputs(
    *,
    units_path: Path,
    queries_path: Path,
    channel_audit_path: Path,
    embedding_cache_path: Path,
    model_name: str,
    batch_size: int,
    max_length: int,
    expected_embedding_cache_sha256: str,
    synthetic_test_mode: bool,
    synthetic_root: Path | None,
    official_authorization_token: str | None = None,
) -> list[dict[str, Any]]:
    if synthetic_test_mode:
        if synthetic_root is None:
            raise ValueError("Synthetic diagnostic capture requires an allowlist root")
        validate_synthetic_path_allowlist(
            {
                "units": units_path,
                "queries": queries_path,
                "channel_audit": channel_audit_path,
                "embedding_cache": embedding_cache_path,
            },
            synthetic_root,
        )
    elif official_authorization_token != OFFICIAL_5B_AUTHORIZATION_TOKEN:
        raise PermissionError(
            "Official decisions diagnostic capture is locked pending Amendment 5B"
        )
    if batch_size <= 0:
        raise ValueError("Embedding batch size must be positive")
    if not synthetic_test_mode:
        if model_name != FROZEN_MODEL_NAME:
            raise ValueError("Official diagnostic model differs")
        if batch_size != FROZEN_BATCH_SIZE or max_length != FROZEN_MAX_LENGTH:
            raise ValueError("Official diagnostic encoder configuration differs")

    units = load_jsonl(units_path)
    queries = load_jsonl(queries_path)
    validate_controller_inputs(units, queries)
    validate_channel_audit(
        load_json(channel_audit_path),
        units_path,
        queries_path,
        queries,
        mode="development",
        source_audit_path=None,
        synthetic_test_mode=synthetic_test_mode,
    )
    unit_embeddings, query_embeddings, _ = load_or_build_embeddings(
        embedding_cache_path,
        units,
        queries,
        model_name,
        batch_size,
        max_length,
        cache_mode="require-existing",
        expected_sha256=expected_embedding_cache_sha256,
        synthetic_test_mode=synthetic_test_mode,
    )
    return compute_decisions_only(
        units,
        queries,
        unit_embeddings,
        query_embeddings,
        RetrievalConfig(),
    )


def run_diagnostic_capture(
    *,
    units_path: Path,
    queries_path: Path,
    channel_audit_path: Path,
    embedding_cache_path: Path,
    reference_decisions_path: Path,
    audit_output_path: Path,
    temp_parent: Path,
    model_name: str,
    batch_size: int,
    max_length: int,
    expected_embedding_cache_sha256: str,
    synthetic_test_mode: bool,
    synthetic_root: Path | None,
    official_authorization_token: str | None = None,
) -> dict[str, Any]:
    if synthetic_test_mode:
        if synthetic_root is None:
            raise ValueError("Synthetic diagnostic capture requires an allowlist root")
        validate_synthetic_path_allowlist(
            {
                "reference_decisions": reference_decisions_path,
                "audit_output": audit_output_path,
                "temp_parent": temp_parent,
            },
            synthetic_root,
        )
    elif official_authorization_token != OFFICIAL_5B_AUTHORIZATION_TOKEN:
        raise PermissionError(
            "Official decisions diagnostic capture is locked pending Amendment 5B"
        )

    captured_path: Path | None = None
    with tempfile.TemporaryDirectory(
        prefix="stage4b_u1_decisions_diag_", dir=temp_parent
    ) as directory:
        captured_path = Path(directory) / "diagnostic_decisions.jsonl"
        decisions = generate_decisions_only_from_inputs(
            units_path=units_path,
            queries_path=queries_path,
            channel_audit_path=channel_audit_path,
            embedding_cache_path=embedding_cache_path,
            model_name=model_name,
            batch_size=batch_size,
            max_length=max_length,
            expected_embedding_cache_sha256=expected_embedding_cache_sha256,
            synthetic_test_mode=synthetic_test_mode,
            synthetic_root=synthetic_root,
            official_authorization_token=official_authorization_token,
        )
        write_jsonl(captured_path, decisions)
        report = compare_decisions_files(reference_decisions_path, captured_path)
        report.update(
            {
                "diagnostic_checkpoint": DIAGNOSTIC_CHECKPOINT,
                "captured_decisions_sha256": sha256_file(captured_path),
                "rankings_accessed": False,
                "rankings_generated": False,
                "policy_builder_called": False,
                "policy_generated": False,
                "gold_accessed": False,
                "reservation_accessed": False,
                "stage3b_accessed": False,
            }
        )
    if captured_path is None or captured_path.exists():
        raise RuntimeError("Temporary diagnostic decisions were not cleaned")
    report["temporary_decisions_cleaned"] = True
    write_json(audit_output_path, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", required=True, type=Path)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--channel-audit", required=True, type=Path)
    parser.add_argument("--embedding-cache", required=True, type=Path)
    parser.add_argument("--reference-decisions", required=True, type=Path)
    parser.add_argument("--audit-output", required=True, type=Path)
    parser.add_argument("--temp-parent", required=True, type=Path)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--batch-size", required=True, type=int)
    parser.add_argument("--max-length", required=True, type=int)
    parser.add_argument("--expected-embedding-cache-sha256", required=True)
    parser.add_argument("--synthetic-test-mode", action="store_true")
    parser.add_argument("--synthetic-root", type=Path)
    parser.add_argument("--official-authorization-token")
    args = parser.parse_args()
    run_diagnostic_capture(
        units_path=args.units,
        queries_path=args.queries,
        channel_audit_path=args.channel_audit,
        embedding_cache_path=args.embedding_cache,
        reference_decisions_path=args.reference_decisions,
        audit_output_path=args.audit_output,
        temp_parent=args.temp_parent,
        model_name=args.model_name,
        batch_size=args.batch_size,
        max_length=args.max_length,
        expected_embedding_cache_sha256=args.expected_embedding_cache_sha256,
        synthetic_test_mode=args.synthetic_test_mode,
        synthetic_root=args.synthetic_root,
        official_authorization_token=args.official_authorization_token,
    )


if __name__ == "__main__":
    main()
