"""Fail-closed typed capture-argument policy for Stage4B-U1 preflight."""

from __future__ import annotations

import ntpath
from collections.abc import Sequence


FIXED_EXECUTABLE = "python"
FIXED_CAPTURE_SCRIPT = "scripts/stage4b_u1_capture_diagnostic_decisions.py"
EXPECTED_ARGV_ELEMENTS = 32
ORDERED_FLAGS = (
    "--units",
    "--queries",
    "--channel-audit",
    "--embedding-cache",
    "--reference-decisions",
    "--audit-output",
    "--temp-parent",
    "--model-name",
    "--batch-size",
    "--max-length",
    "--expected-units-sha256",
    "--expected-queries-sha256",
    "--expected-channel-audit-sha256",
    "--expected-embedding-cache-sha256",
    "--official-authorization-token",
)
PATH_FLAGS = frozenset(
    {
        "--units",
        "--queries",
        "--channel-audit",
        "--embedding-cache",
        "--reference-decisions",
        "--audit-output",
        "--temp-parent",
    }
)
POSITIVE_DECIMAL_FLAGS = frozenset({"--batch-size", "--max-length"})
SHA256_FLAGS = frozenset(
    {
        "--expected-units-sha256",
        "--expected-queries-sha256",
        "--expected-channel-audit-sha256",
        "--expected-embedding-cache-sha256",
    }
)
EXACT_TEXT_FLAGS = frozenset(
    {"--model-name", "--official-authorization-token"}
)
PROHIBITED_FLAGS = frozenset(
    {
        "--rankings",
        "--policy",
        "--gold-map",
        "--source-audit",
        "--evaluator",
        "--reservation",
        "--stage3b",
    }
)
_UPPER_HEX = frozenset("0123456789ABCDEF")


class CaptureArgumentPolicyError(ValueError):
    """Raised when capture arguments do not satisfy the frozen typed policy."""


def _argv_tuple(argv: Sequence[str], label: str) -> tuple[str, ...]:
    if isinstance(argv, (str, bytes, bytearray)) or not isinstance(argv, Sequence):
        raise CaptureArgumentPolicyError(f"{label} must be a sequence of text items")
    values = tuple(argv)
    if any(not isinstance(value, str) or not value for value in values):
        raise CaptureArgumentPolicyError(
            f"{label} must contain only non-empty text items"
        )
    return values


def _is_absolute_windows_path(value: str) -> bool:
    drive, _ = ntpath.splitdrive(value)
    return bool(drive) and ntpath.isabs(value)


def _is_canonical_positive_decimal(value: str) -> bool:
    return (
        bool(value)
        and all(character in "0123456789" for character in value)
        and value[0] != "0"
    )


def _is_upper_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in _UPPER_HEX for character in value)


def _validate_typed_value(flag: str, value: str, label: str) -> None:
    if flag in PATH_FLAGS:
        if not _is_absolute_windows_path(value):
            raise CaptureArgumentPolicyError(
                f"{label} {flag} must be an absolute Windows path string"
            )
        return
    if flag in POSITIVE_DECIMAL_FLAGS:
        if not _is_canonical_positive_decimal(value):
            raise CaptureArgumentPolicyError(
                f"{label} {flag} must be a canonical positive decimal string"
            )
        return
    if flag in SHA256_FLAGS:
        if not _is_upper_sha256(value):
            raise CaptureArgumentPolicyError(
                f"{label} {flag} must be a 64-character uppercase SHA-256 string"
            )
        return
    if flag in EXACT_TEXT_FLAGS:
        if not value:
            raise CaptureArgumentPolicyError(f"{label} {flag} must be non-empty")
        return
    raise CaptureArgumentPolicyError(f"{label} contains an untyped role: {flag}")


def _validate_structure(argv: tuple[str, ...], label: str) -> dict[str, str]:
    if len(argv) != EXPECTED_ARGV_ELEMENTS:
        raise CaptureArgumentPolicyError(
            f"{label} must contain exactly {EXPECTED_ARGV_ELEMENTS} elements"
        )
    if argv[0] != FIXED_EXECUTABLE:
        raise CaptureArgumentPolicyError(f"{label} executable is not approved")
    if argv[1] != FIXED_CAPTURE_SCRIPT:
        raise CaptureArgumentPolicyError(f"{label} capture script is not approved")

    values: dict[str, str] = {}
    for position, expected_flag in enumerate(ORDERED_FLAGS):
        offset = 2 + 2 * position
        supplied_flag = argv[offset]
        supplied_value = argv[offset + 1]
        if supplied_flag in PROHIBITED_FLAGS:
            raise CaptureArgumentPolicyError(
                f"{label} contains prohibited role: {supplied_flag}"
            )
        if supplied_flag in values:
            raise CaptureArgumentPolicyError(
                f"{label} contains duplicate role: {supplied_flag}"
            )
        if supplied_flag != expected_flag:
            if supplied_flag in ORDERED_FLAGS:
                raise CaptureArgumentPolicyError(
                    f"{label} role order differs at position {position}"
                )
            if supplied_flag.startswith("--"):
                raise CaptureArgumentPolicyError(
                    f"{label} contains unknown role: {supplied_flag}"
                )
            raise CaptureArgumentPolicyError(
                f"{label} contains an extra positional argument"
            )
        _validate_typed_value(supplied_flag, supplied_value, label)
        values[supplied_flag] = supplied_value

    if tuple(values) != ORDERED_FLAGS:
        raise CaptureArgumentPolicyError(f"{label} role set or order is incomplete")
    return values


def _reject_nonidentical(
    actual: tuple[str, ...], approved: tuple[str, ...]
) -> None:
    approved_values = _validate_structure(approved, "approved argv")
    actual_values = _validate_structure(actual, "actual argv")
    for flag in ORDERED_FLAGS:
        if actual_values[flag] != approved_values[flag]:
            raise CaptureArgumentPolicyError(
                f"actual argv value is not exactly bound for role: {flag}"
            )
    raise CaptureArgumentPolicyError("actual argv is not exactly equal to approved argv")


def validate_capture_argv(
    actual_argv: Sequence[str], approved_argv: Sequence[str]
) -> dict[str, bool | int | str]:
    """Validate exact capture arguments without reading paths or executing commands."""

    actual = _argv_tuple(actual_argv, "actual argv")
    approved = _argv_tuple(approved_argv, "approved argv")

    if actual != approved:
        _reject_nonidentical(actual, approved)

    approved_values = _validate_structure(approved, "approved argv")
    actual_values = _validate_structure(actual, "actual argv")
    for flag in ORDERED_FLAGS:
        if actual_values[flag] != approved_values[flag]:
            raise CaptureArgumentPolicyError(
                f"actual argv value is not exactly bound for role: {flag}"
            )

    return {
        "status": "VALID",
        "exact_argv_equal": True,
        "argv_elements": len(actual),
        "flag_count": len(ORDERED_FLAGS),
        "path_role_count": len(PATH_FLAGS),
        "prohibited_role_count": 0,
        "filesystem_accessed": False,
        "command_executed": False,
        "authorization_token_used": False,
    }
