"""Pure-value execution-HEAD binding checks for Stage4B-U1 governance."""

from __future__ import annotations

from collections.abc import Mapping, Sequence


REQUIRED_ARTIFACT_KEYS = (
    "rebinding_evidence",
    "governance_binding",
    "rebinding_audit",
)
_LOWER_HEX = frozenset("0123456789abcdef")


class ExecutionHeadBindingError(ValueError):
    """Raised when caller-supplied execution-HEAD facts fail closed."""


def _full_sha(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 40
        or any(character not in _LOWER_HEX for character in value)
    ):
        raise ExecutionHeadBindingError(
            f"{label} must be a full lowercase 40-character hexadecimal SHA"
        )
    return value


def _text_sequence(values: object, label: str) -> tuple[str, ...]:
    if (
        isinstance(values, (str, bytes, bytearray))
        or not isinstance(values, Sequence)
    ):
        raise ExecutionHeadBindingError(f"{label} must be a sequence of text values")
    result = tuple(values)
    if any(not isinstance(value, str) or not value for value in result):
        raise ExecutionHeadBindingError(
            f"{label} must contain only non-empty text values"
        )
    if len(set(result)) != len(result):
        raise ExecutionHeadBindingError(f"{label} must not contain duplicates")
    return result


def _repository_path(value: str, label: str) -> str:
    if value != value.strip() or "\x00" in value:
        raise ExecutionHeadBindingError(f"{label} contains an invalid path")
    if value.startswith("/") or "\\" in value or ":" in value:
        raise ExecutionHeadBindingError(f"{label} must be repository-relative")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ExecutionHeadBindingError(
            f"{label} must not contain empty dot or parent-traversal segments"
        )
    return value


def _path_set(values: object, label: str) -> frozenset[str]:
    paths = _text_sequence(values, label)
    return frozenset(_repository_path(path, label) for path in paths)


def _sha_set(values: object, label: str) -> frozenset[str]:
    commits = _text_sequence(values, label)
    return frozenset(_full_sha(commit, label) for commit in commits)


def _governance_binding(
    value: object,
    expected_package_commit: str,
    expected_approval_commit: str,
) -> int:
    if not isinstance(value, Mapping):
        raise ExecutionHeadBindingError("governance_binding must be a mapping")
    package_commit = _full_sha(
        value.get("package_commit"), "governance_binding package_commit"
    )
    approval_commit = _full_sha(
        value.get("approval_commit"), "governance_binding approval_commit"
    )
    if package_commit != expected_package_commit:
        raise ExecutionHeadBindingError("governance package commit does not match")
    if approval_commit != expected_approval_commit:
        raise ExecutionHeadBindingError("governance approval commit does not match")
    artifacts = value.get("artifacts_present")
    if not isinstance(artifacts, Mapping):
        raise ExecutionHeadBindingError("governance artifact presence is required")
    for key in REQUIRED_ARTIFACT_KEYS:
        if artifacts.get(key) is not True:
            raise ExecutionHeadBindingError(
                f"required governance artifact is not present: {key}"
            )
    return len(REQUIRED_ARTIFACT_KEYS)


def validate_execution_head_binding(
    local_head: str,
    origin_main: str,
    github_main: str,
    head_parent: str,
    approval_governance_commit: str,
    changed_paths: Sequence[str],
    allowed_rebinding_paths: Sequence[str],
    required_ancestor_commits: Sequence[str],
    observed_ancestor_commits: Sequence[str],
    worktree_clean: bool,
    governance_binding: Mapping[str, object],
    expected_package_commit: str,
    expected_approval_commit: str,
) -> dict[str, object]:
    """Validate caller-supplied relations and derive the synchronized current HEAD."""

    local = _full_sha(local_head, "local_head")
    origin = _full_sha(origin_main, "origin_main")
    github = _full_sha(github_main, "github_main")
    parent = _full_sha(head_parent, "head_parent")
    approval = _full_sha(
        approval_governance_commit, "approval_governance_commit"
    )
    package = _full_sha(expected_package_commit, "expected_package_commit")
    expected_approval = _full_sha(
        expected_approval_commit, "expected_approval_commit"
    )

    if not (local == origin == github):
        raise ExecutionHeadBindingError(
            "local origin and GitHub execution HEAD values must match exactly"
        )
    if parent != approval:
        raise ExecutionHeadBindingError(
            "execution HEAD direct parent must equal the approval governance commit"
        )
    if approval != expected_approval:
        raise ExecutionHeadBindingError(
            "approval governance commit does not match the expected approval commit"
        )

    changed = _path_set(changed_paths, "changed_paths")
    allowed = _path_set(allowed_rebinding_paths, "allowed_rebinding_paths")
    if changed != allowed:
        raise ExecutionHeadBindingError(
            "changed paths must exactly equal the governance-allowed path set"
        )

    required = _sha_set(required_ancestor_commits, "required_ancestor_commits")
    observed = _sha_set(observed_ancestor_commits, "observed_ancestor_commits")
    if not required.issubset(observed):
        raise ExecutionHeadBindingError("a required ancestor commit is missing")
    if type(worktree_clean) is not bool or not worktree_clean:
        raise ExecutionHeadBindingError("worktree must be reported clean")

    artifact_count = _governance_binding(
        governance_binding,
        expected_package_commit=package,
        expected_approval_commit=expected_approval,
    )
    return {
        "status": "VALIDATED_EXECUTION_HEAD_BINDING",
        "validated_execution_head": local,
        "head_sources_equal": True,
        "direct_parent_verified": True,
        "changed_path_set_verified": True,
        "changed_path_count": len(changed),
        "required_ancestor_count": len(required),
        "required_artifact_count": artifact_count,
        "worktree_clean": True,
    }
