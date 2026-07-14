# Stage4B-U1-D Pre-Gold Hard Failure 6 Review 1

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Review date: 2026-07-14
- Reviewed commit: `bebfeb5664f26795b8d3472f3729ca1bb9abf889`
- Decision: `ACCEPT_HARD_FAILURE_6_AUDIT`
- Next gate: `RETURN_FOR_AMENDMENT_5E_A_PACKAGE`
- Other project conversations, thread tools, and global memory used: No

## Review Decision

Hard Failure 6 stopping behavior is accepted. The only Amendment 5D-B formal preflight invocation is consumed. No second 5D-B preflight and no direct capture are permitted.

Current authorization state:

```text
ACCEPT_HARD_FAILURE_6_AUDIT
RETURN_FOR_AMENDMENT_5E_A_PACKAGE

PATH_EQUIVALENCE_FIX_NOT_APPROVED
FORMAL_PREFLIGHT_RETRY_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

## Confirmed Failure Boundary

The preflight passed project governance, commit binding, implementation hashes, exact-command registration, output absence, and temporary-residue checks. It then failed before regular-file checks, SHA reads, or semantic parsing of any of the five official inputs.

Capture invocation count remains zero. No new experimental result exists and Hard Failure 4 remains unclassified. The final Hard Failure 6 commit modified only governance and audit files; it did not modify code, data, model, parameters, comparator semantics, byte equivalence, cache, or official artifacts.

## Direct Cause

The failed expression compared these two strings after `GetFullPath` but before trailing-separator normalization:

```powershell
[System.IO.Path]::GetFullPath($tempParent) -eq
  [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
```

The Manifest path omitted a final separator while `.NET GetTempPath()` returned one. The strings identify the same directory but were treated as unequal. This is a preflight path-equivalence implementation defect, not evidence of official input, cache, comparator, capture, or controller drift.

## Required Amendment Split

The next package must be Amendment 5E-A and may request only a tracked Windows OS-temp path-equivalence helper, synthetic tests, deterministic-runner binding, implementation audit, and deterministic evidence. It must not request official access, formal preflight, token use, capture, controller, verifier, or Gold.

Only after 5E-A implementation/evidence is independently reviewed may a separate Amendment 5E-B request one new formal preflight and, conditionally, one unchanged exact capture command.

## Frozen 5E-A Design Boundary

The helper must:

- require absolute existing directory paths;
- reject files, missing paths, relative paths, symlinks, junctions, and reparse points;
- canonicalize full paths and trim trailing separators for comparison only;
- compare Windows paths with ordinal case-insensitive semantics;
- accept the exact directory with slash, case, separator-direction, and `.` spelling variants;
- reject parents, children, siblings such as `Temp2`, and unrelated temp directories;
- never use prefix matching;
- never modify the exact official capture command or broaden the official input boundary.

The current 143 tests are the baseline. At least 12 new path-equivalence/preflight tests are required, so the complete deterministic suite must contain at least 155 tests and run twice with zero failure/error/skip/official access and byte-identical evidence.

## Current State

```text
HARD_FAILURE_6_AUDIT_ACCEPTED
AMENDMENT_5E_A_PACKAGE_REQUIRED
HARD_FAILURE_4_DIAGNOSIS_INCOMPLETE

FORMAL_PREFLIGHT_RETRY_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
