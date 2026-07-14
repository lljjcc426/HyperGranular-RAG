"""Fail-closed Windows directory equivalence for Stage4B-U1 preflight."""

from __future__ import annotations

import ctypes
import ntpath
import os
import stat
from ctypes import wintypes
from typing import TypeAlias


PathInput: TypeAlias = str | os.PathLike[str]
_CSTR_EQUAL = 2
_REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


class PathEquivalenceError(ValueError):
    """Raised when a directory-equivalence input cannot be validated safely."""


def _absolute_path_text(value: PathInput, label: str) -> str:
    try:
        text = os.fspath(value)
    except TypeError as exc:
        raise PathEquivalenceError(f"{label} must be a string-like path") from exc
    if not isinstance(text, str) or not text:
        raise PathEquivalenceError(f"{label} must be a non-empty text path")
    if not ntpath.isabs(text):
        raise PathEquivalenceError(f"{label} must be absolute before normalization")
    return text


def _leaf_is_reparse_point(status: os.stat_result) -> bool:
    attributes = getattr(status, "st_file_attributes", 0)
    return bool(attributes & _REPARSE_POINT)


def _require_existing_plain_directory(path: str, label: str) -> None:
    try:
        status = os.lstat(path)
    except OSError as exc:
        raise PathEquivalenceError(f"{label} must exist at comparison time") from exc
    if stat.S_ISLNK(status.st_mode) or _leaf_is_reparse_point(status):
        raise PathEquivalenceError(f"{label} must not be a reparse-point leaf")
    if not stat.S_ISDIR(status.st_mode):
        raise PathEquivalenceError(f"{label} must be a directory")


def _trim_ending_directory_separators(path: str) -> str:
    drive, tail = ntpath.splitdrive(path)
    rooted = tail[:1] in ("\\", "/")
    minimum_length = len(drive) + (1 if rooted else 0)
    while len(path) > minimum_length and path[-1:] in ("\\", "/"):
        path = path[:-1]
    return path


def _canonical_comparison_path(path: str) -> str:
    try:
        canonical = ntpath.abspath(ntpath.normpath(path))
    except (OSError, TypeError, ValueError) as exc:
        raise PathEquivalenceError("Path canonicalization failed") from exc
    return _trim_ending_directory_separators(ntpath.normpath(canonical))


def _ordinal_ignore_case_equal(left: str, right: str) -> bool:
    if os.name != "nt":
        raise PathEquivalenceError("Windows ordinal comparison is unavailable")
    compare = ctypes.WinDLL("kernel32", use_last_error=True).CompareStringOrdinal
    compare.argtypes = (
        wintypes.LPCWSTR,
        ctypes.c_int,
        wintypes.LPCWSTR,
        ctypes.c_int,
        wintypes.BOOL,
    )
    compare.restype = ctypes.c_int
    result = compare(left, len(left), right, len(right), True)
    if result == 0:
        raise PathEquivalenceError(
            f"Windows ordinal comparison failed with error {ctypes.get_last_error()}"
        )
    return result == _CSTR_EQUAL


def windows_directories_equivalent(actual: PathInput, expected: PathInput) -> bool:
    """Return exact Windows directory equality after fail-closed leaf validation."""

    actual_text = _absolute_path_text(actual, "actual path")
    expected_text = _absolute_path_text(expected, "expected path")
    _require_existing_plain_directory(actual_text, "actual path")
    _require_existing_plain_directory(expected_text, "expected path")
    actual_canonical = _canonical_comparison_path(actual_text)
    expected_canonical = _canonical_comparison_path(expected_text)
    return _ordinal_ignore_case_equal(actual_canonical, expected_canonical)
