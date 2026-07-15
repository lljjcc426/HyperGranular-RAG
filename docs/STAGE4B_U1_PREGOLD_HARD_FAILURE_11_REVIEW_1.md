# Stage4B-U1-D Pre-Gold Hard Failure 11 Review 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review date: 2026-07-15
- Corrected 5G-B.1 package: 48a9c1438166eaf895104358b2d8cd8c9b043020
- Approval governance: 0e28fba6647bfd98634ebb8d1565e862dcf16920
- Hard Failure 11 checkpoint: d2aadb2f03f4388d71ddf70fcfb116c92fe4b008
- Decision: ACCEPT_HARD_FAILURE_11_AUDIT
- Next action: RETURN_FOR_AMENDMENT_5G_B_1_1_SEMANTICS_HARNESS_PACKAGE
- Current 5G-B.1 approval reusable: No
- Official execution authorized: No
- Other project conversations, thread tools, and global memory used: No

## Accepted Findings

The approval-governance commit was the exact two-path direct child of the corrected package and was synchronized across local, origin and GitHub with a clean worktree before semantics execution.

The one-time semantics gate was consumed:

    wrapper invocations: 1
    Python processes: 1
    successful nine-fixture summaries: 0
    complete synthetic runs: 0
    real validator invocations: 0
    fresh direct-child commits: 0
    retries: 0

The fail-closed stop was correct. The current approval cannot be reused.

## Probable Direct Cause

The directly observed output identified Python string-source line 6, which aligns with the duplicate-key parser's expected ValueError. The probable explanation is that an expected negative-fixture rejection escaped as an unhandled Python exception and native stderr was then promoted to a terminating Windows PowerShell NativeCommandError.

This is recorded as:

    PROBABLE_DIRECT_CAUSE_CONFIRMED_BY_LINE_ALIGNMENT
    NOT_FULLY_PROVEN_FROM_COMPLETE_TRACEBACK

The complete traceback was not preserved, so the deeper exception path remains unproven. The real precommit validator is not declared defective by this review and remains frozen at:

    lines: 195
    bytes: 15966
    SHA-256: 0F066387B8523B0EA387444076A1113913082D283C28C2DE3FFB33872D558249

## Side-Effect Boundary

After failure, the three fresh 5G-B.1 paths were absent and all three historical 5G-B artifacts retained their frozen bytes and SHA values. No code, test, results, cache, official artifact or historical evidence was modified or deleted. No official input, helper, token, capture, controller, verifier or Gold access occurred.

## Required Amendment 5G-B.1.1

The next package is limited to a fully frozen semantics harness and native-process transport verification. It must freeze:

- complete PowerShell wrapper source lines, bytes and SHA-256;
- embedded Python semantics source lines, bytes and SHA-256;
- exact nine fixture names and expected results;
- deterministic stdout schema and exact values;
- Python exit-code and empty-stderr gates;
- one wrapper invocation and one Python process;
- two fresh semantics-only output paths.

Expected negative raw-JSON exceptions must be caught inside Python and converted to structured passed results. Native stderr must be isolated as data using System.Diagnostics.Process rather than PowerShell's native pipeline.

The package may request a later approval for one semantics-only execution, evidence/audit submission and immediate stop. It must not request fresh synthetic rebinding, the real validator, direct-child recovery or any official action.

## Current State

    HARD_FAILURE_11_AUDIT_ACCEPTED
    HARD_FAILURE_11_CHECKPOINT_FROZEN
    SEMANTICS_GATE_CONSUMED
    PROBABLE_EXPECTED_REJECTION_HANDLING_DEFECT
    COMPLETE_TRACEBACK_NOT_AVAILABLE
    REAL_PRECOMMIT_VALIDATOR_REMAINS_FROZEN
    RETURN_FOR_AMENDMENT_5G_B_1_1_PACKAGE

    CURRENT_5G_B_1_APPROVAL_CONSUMED
    VALIDATOR_SEMANTICS_CHECK_NOT_APPROVED
    FRESH_SYNTHETIC_REBINDING_NOT_APPROVED
    FRESH_THREE_PATH_DIRECT_CHILD_NOT_APPROVED
    DERIVED_EXECUTION_HEAD_VALIDATION_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_INPUT_ACCESS_NOT_APPROVED
    AUTHORIZATION_TOKEN_USE_NOT_APPROVED
    OFFICIAL_CAPTURE_NOT_APPROVED
    CONTROLLER_RERUN_NOT_APPROVED
    VERIFIER_NOT_APPROVED
    GOLD_NOT_APPROVED
