# Stage4B-U1-D Pre-Gold Hard Failure 11

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Failure date: 2026-07-15
- Corrected package: 48a9c1438166eaf895104358b2d8cd8c9b043020
- Approval governance: 0e28fba6647bfd98634ebb8d1565e862dcf16920
- Failure status: AMENDMENT_5G_B_1_VALIDATOR_SEMANTICS_STOPPED_HARD_FAILURE_11
- Failure boundary: ONE_IN_MEMORY_VALIDATOR_SEMANTICS_CHECK
- Synthetic rebinding: NOT_STARTED
- Real frozen precommit validator: NOT_STARTED
- Fresh direct-child: NOT_CREATED
- Official execution: NOT_STARTED
- Other project conversations, thread tools, and global memory used: No

## Approval-Governance Gate

The approval-governance commit was created as the direct child of the corrected package:

    approval:
    0e28fba6647bfd98634ebb8d1565e862dcf16920

    parent:
    48a9c1438166eaf895104358b2d8cd8c9b043020

Its changed-path set was exactly:

    AGENTS.md
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_APPROVAL_DECISION.md

Before the semantics wrapper, local HEAD, origin/main and GitHub main all equaled the approval commit and the worktree was clean.

## Consumed Semantics Invocation

The approved semantics wrapper was invoked exactly once. It defined all seven PowerShell key-set fixtures in memory and launched exactly one approved Python parser process for the two raw-JSON fixtures.

The PowerShell portion reached the Python launch without throwing. No separate result was accepted for those seven fixtures because the approved gate required one successful wrapper covering all nine fixtures.

The Python process emitted stderr and PowerShell terminated the wrapper as a NativeCommandError. The captured output began:

    python.exe :   File "<string>", line 6
    CategoryInfo : NotSpecified
    FullyQualifiedErrorId : NativeCommandError

The wrapper exited nonzero before producing the required nine-fixture success summary. The captured output did not include the remainder of the Python diagnostic, so the underlying parser error is not confirmed by this checkpoint. The directly observed failure is the single parser process emitting stderr at its string source line 6 and the wrapper terminating on that native stderr.

The semantics wrapper was not corrected or rerun. No second Python parser process was started.

## One-Time Counts

    semantics wrapper invocations: 1
    Python raw-parser processes: 1
    successful nine-fixture summaries: 0
    complete synthetic runs: 0
    frozen real validator invocations: 0
    fresh direct-child commits: 0
    automatic retries: 0

The semantics authorization is consumed.

## Failure-Side-Effect Audit

Immediately after the failed wrapper:

    HEAD:
    0e28fba6647bfd98634ebb8d1565e862dcf16920

    origin/main:
    0e28fba6647bfd98634ebb8d1565e862dcf16920

    worktree status lines:
    0

All three fresh paths remained absent:

    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_SYNTHETIC_REBINDING_AUDIT.md
    results/stage4b_u1_d_pregold_amendment_5g_b_1_governance_binding.json
    results/stage4b_u1_d_pregold_amendment_5g_b_1_synthetic_rebinding.json

The three historical 5G-B artifacts remained frozen:

| Path | Bytes | SHA-256 |
|---|---:|---|
| docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_SYNTHETIC_REBINDING_AUDIT.md | 3973 | 50D125193CDD49B2A33ADF4EFC3A5F4A0F74A4029EE640AA032B4FEE990B3054 |
| results/stage4b_u1_d_pregold_amendment_5g_b_governance_binding.json | 5317 | 12BF30F3EF70D0420237DCF0A6C6D5D06C05990DDF637EA4CF31B7C3C7655730 |
| results/stage4b_u1_d_pregold_amendment_5g_b_synthetic_rebinding.json | 69144 | 00281BED7BC0DF10D47382CC47D0884BFCD331F0CB92EFC0B51F0FF176827A2A |

No code, test, results file, cache, official artifact or historical evidence was modified or deleted. No official input, project helper, authorization token, capture, controller, verifier, evaluator/Gold, rankings, policy, source audit, 5C-B inventory, reservation or Stage3B was accessed by the semantics wrapper.

## Stop Boundary

The following approved steps were not started and are no longer authorized under the consumed approval:

    two fresh complete synthetic rebinding runs
    fresh three-artifact creation
    frozen real precommit validator
    exact-three-path direct-child

Derived execution-HEAD validation, formal preflight and all official actions were never approved and remain locked.

## Required Next Governance Gate

An independent review must evaluate this checkpoint and decide whether a new implementation/synthetic-only Amendment is required for the semantics wrapper or its native-process error handling. The current approval cannot be reused.

Until a new package-bound approval:

    AMENDMENT_5G_B_1_VALIDATOR_SEMANTICS_STOPPED_HARD_FAILURE_11
    VALIDATOR_SEMANTICS_CHECK_INCOMPLETE
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
