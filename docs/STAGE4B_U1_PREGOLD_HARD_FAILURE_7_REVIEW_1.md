# Stage4B-U1-D Pre-Gold Hard Failure 7 Review 1

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Review date: 2026-07-14
- Reviewed commit: `f18d551b17f1bbed645ac159ebe52b7d6b9d8e54`
- Decision: `ACCEPT_HARD_FAILURE_7_AUDIT`
- Next gate: `RETURN_FOR_AMENDMENT_5F_A_PACKAGE`
- Other project conversations, thread tools, and global memory used: No

## Review Decision

Hard Failure 7 stopping behavior and audit are accepted. The single Amendment 5E-B formal preflight invocation is consumed. No argument-policy correction, second preflight, helper official-boundary check, token use, or capture is permitted under 5E-B.

Current authorization state:

```text
ACCEPT_HARD_FAILURE_7_AUDIT
RETURN_FOR_AMENDMENT_5F_A_PACKAGE

ARGUMENT_POLICY_FIX_NOT_APPROVED
FORMAL_PREFLIGHT_RETRY_NOT_APPROVED
HELPER_OFFICIAL_BOUNDARY_CHECK_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

## Confirmed Failure Boundary

The preflight A gate verified the synchronized clean commit, governance ancestry, 23 implementation hashes, exact capture argv, and helper file status. The B gate first confirmed that the machine and narrative audits, five formal outputs, and diagnostic temporary residue were absent. It then failed on the prohibited-argument classifier.

The C path-equivalence helper gate and D official-input gate were never entered. Helper invocation, official input metadata/content access, authorization-token use, and official capture invocation all remained zero. No new diagnostic or scientific result exists, and Hard Failure 4 remains unclassified.

The commit range from `3185c3bd4ffd3eb2bc61b52fdf18a3367b9dca76` to `f18d551b17f1bbed645ac159ebe52b7d6b9d8e54` changes only the Hard Failure 7 audit and governance/status documentation. It does not change implementation, data, model, parameters, cache, or experimental artifacts.

## Direct Cause

The failed policy treated every argv value as an untyped string and applied a raw case-insensitive substring check equivalent to:

```powershell
$value.IndexOf('gold', [StringComparison]::OrdinalIgnoreCase) -ge 0
```

That check cannot distinguish a prohibited Gold input role from the allowed protocol term `pregold` in the exact frozen machine-audit output path. The A gate had already proved element-by-element equality with the approved exact capture command, so no new Gold argument was supplied.

This is a preflight argument-classification defect. It is not evidence of official-input, helper, capture, comparator, controller, cache, data, model, or parameter drift.

## Required Amendment Split

The next package must be Amendment 5F-A and may request only a tracked typed capture-argument policy helper, synthetic tests, deterministic-runner binding, implementation audit, deterministic evidence, and a later implementation-bound 5F-B package. It must not request official metadata/content access, a real OS-temp helper check, formal preflight, token use, capture, controller, verifier, or Gold.

Only after 5F-A implementation/evidence is independently reviewed may a separate Amendment 5F-B request a new preflight and conditionally one unchanged exact capture.

## Frozen 5F-A Design Boundary

The typed helper must use this control structure:

```text
exact argv equality
typed flag allowlist
per-role exact value binding
explicit prohibited-role rejection
```

It must parse executable, capture script, ordered flag/value pairs, roles, and value types. It must reject unknown, duplicate, missing, reordered, or extra arguments and explicitly prohibited roles. It must accept the exact frozen `--audit-output` path containing `pregold` and must not use a raw `gold` substring denylist.

The helper must be deterministic and standard-library-only. It must not access the filesystem, execute commands, use the token, invoke capture, or contain official execution authority.

The current 161 tests are the baseline. At least 16 new argument-policy tests are required, so the complete deterministic suite must contain at least 177 tests and run twice with zero failure/error/skip/official access/path-helper official invocation/preflight/token/capture and byte-identical evidence.

## Current State

```text
HARD_FAILURE_7_AUDIT_ACCEPTED
AMENDMENT_5F_A_PACKAGE_REQUIRED
HARD_FAILURE_4_DIAGNOSIS_INCOMPLETE

FORMAL_PREFLIGHT_RETRY_NOT_APPROVED
HELPER_OFFICIAL_BOUNDARY_CHECK_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
