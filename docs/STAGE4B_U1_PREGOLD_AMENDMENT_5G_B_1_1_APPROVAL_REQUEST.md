# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1 Approval Request

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Request date: 2026-07-15
- Request ID: STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_VALIDATOR_SEMANTICS_HARNESS_EXPECTED_REJECTION_AND_NATIVE_TRANSPORT_ONLY
- Manifest: docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_MANIFEST.json
- Current state: RETURN_FOR_AMENDMENT_5G_B_1_1_PACKAGE
- Requested mode: FROZEN_VALIDATOR_SEMANTICS_HARNESS_EXECUTION_AND_EVIDENCE_ONLY
- Package itself authorizes implementation or execution: No
- Official execution: NOT_APPROVED
- Other project conversations, thread tools, and global memory used: No

## Binding History

    corrected 5G-B.1 package:
    48a9c1438166eaf895104358b2d8cd8c9b043020

    5G-B.1 approval governance:
    0e28fba6647bfd98634ebb8d1565e862dcf16920

    Hard Failure 11 checkpoint:
    d2aadb2f03f4388d71ddf70fcfb116c92fe4b008

    Hard Failure 10 checkpoint:
    aab591b92804fd1226a62751c38d056918f71b41

Any future approval must explicitly bind the package commit containing this Request and Manifest. Approval of the earlier 5G-B.1 package cannot be reused.

## Accepted Hard Failure 11 Boundary

Hard Failure 11 Review 1 accepts the audit, confirms the one-time gate was consumed and accepts the fail-closed stop. The review is:

    docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_11_REVIEW_1.md
    bytes: 4012
    SHA-256:
    2ECBC6D9E2987C19DB8724608AAC6D2918514C7D704A570B91608D0F9CEDBD2D

The direct observation was a single Python process emitting stderr at string-source line 6 and Windows PowerShell terminating the wrapper as NativeCommandError. Line alignment supports, but does not fully prove, that an expected duplicate-key ValueError escaped the negative-fixture harness and was converted into native stderr.

No semantics result was accepted. Synthetic runs, real-validator invocations and fresh direct-child commits remained zero. Three fresh paths remained absent and the historical 5G-B artifacts remained frozen.

## Frozen Real Validator Remains Out Of Scope

The real precommit validator remains unchanged and unrequested:

    lines: 195
    bytes: 15966
    SHA-256:
    0F066387B8523B0EA387444076A1113913082D283C28C2DE3FFB33872D558249

This Amendment does not modify or execute it.

## Fully Frozen Embedded Python Semantics Source

The exact Python standard-library source is stored as Manifest source_lines joined by LF with no trailing newline:

    lines: 46
    bytes: 2284
    SHA-256:
    D0D3D6FC37AD0C2649A7A7F88EFA944C357033E3F0E956BE0E27C4374653D602

Expected negative exceptions are caught inside the process. A rejection counts as passed only when its message contains the exact expected fragment. The process emits no traceback for expected rejection.

The exact successful stdout is:

    bytes: 269
    SHA-256:
    1A72C50B283F41C8799D80B3573E6A5B97CD2B592396E760E1B7826462DE3F28

Required process outcome:

    raw JSON fixtures: 2/2
    exit code: 0
    stderr bytes: 0
    stdout: exact frozen JSON

## Fully Frozen PowerShell Wrapper

The exact Windows PowerShell 5.1 wrapper is stored as Manifest source_lines joined by LF with no trailing newline:

    lines: 122
    bytes: 7890
    SHA-256:
    DFA95A904CE371F283B8DBA8BB4D98CC048F345F536C0E7D0D6DB8073DF9E16C

The embedded Python here-string is byte-identical to the separately frozen Python source.

The wrapper uses System.Diagnostics.Process with:

    UseShellExecute = false
    RedirectStandardInput = true
    RedirectStandardOutput = true
    RedirectStandardError = true
    CreateNoWindow = true

Python source is transported in one process-only environment variable. Native stderr is read as ordinary string data and cannot become a PowerShell NativeCommandError before exit-code inspection.

The exact successful wrapper stdout is:

    bytes: 789
    SHA-256:
    EDBD4614B790256E314F4A8963128A5FB5A190FAC197437FB349D4C33C606135

## Nine Frozen Fixtures

The single wrapper must produce exactly:

    PowerShell fixtures: 7/7
    raw JSON fixtures: 2/2
    total: 9/9

The exact fixture names are:

    exact_expected_key_set
    missing_key
    extra_key
    duplicate_actual_key
    duplicate_expected_key
    case_only_actual_key_drift
    case_only_expected_key_collision
    raw_json_duplicate_bound_files_key
    raw_json_case_only_bound_files_collision

Every result must have passed=true. The wrapper must report one wrapper invocation, one Python process, exit code zero, empty stderr and zero filesystem/Git/GitHub/helper/official/token/capture access.

## Requested Future Approval-Governance Commit

A future explicit package-bound approval may first authorize one approval-governance commit whose changed-path set is exactly:

    AGENTS.md
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_APPROVAL_DECISION.md

The approval decision must bind:

    future package commit
    wrapper bytes 7890 and SHA DFA95A904CE371F283B8DBA8BB4D98CC048F345F536C0E7D0D6DB8073DF9E16C
    Python bytes 2284 and SHA D0D3D6FC37AD0C2649A7A7F88EFA944C357033E3F0E956BE0E27C4374653D602
    expected wrapper stdout SHA EDBD4614B790256E314F4A8963128A5FB5A190FAC197437FB349D4C33C606135

The approval commit must be pushed and synchronized across local, origin and GitHub with a clean worktree before source reconstruction or execution.

## Requested One-Time Semantics-Only Execution

Only after a future package-bound approval:

1. Reconstruct both source strings from the Manifest.
2. Verify both line counts, bytes and SHA-256 values.
3. Verify the wrapper's embedded Python is exactly equal to the registered Python source.
4. Invoke the wrapper exactly once.
5. Permit exactly one Python process.
6. Require exact wrapper stdout, empty stderr and nine of nine passed.
7. Exclusive-create the two fresh evidence paths.
8. Commit only those two paths as the approval-governance direct child.
9. Push, confirm local/origin/GitHub equality and clean worktree.
10. Stop immediately for independent review.

No post-approval try/catch, stderr redirection, diagnostic print, wrapper expression, parser call, repair or retry may be added.

## Fresh Evidence Paths

The only future outputs are:

    results/stage4b_u1_d_pregold_amendment_5g_b_1_1_validator_semantics.json
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_VALIDATOR_SEMANTICS_AUDIT.md

Both must be absent before execution and exclusive-created. Machine evidence must equal the 789 frozen wrapper-stdout bytes. The future evidence commit must change exactly these two paths and be the direct child of approval governance.

## Explicitly Not Requested Or Authorized

- any command before a new package-bound approval;
- modifications to scripts, tests, results, Hard Failure 10/11 or historical 5G-B artifacts during package assembly;
- modification or execution of the real precommit validator;
- complete synthetic rebinding or 5G-B.1 fresh three-path creation;
- execution-HEAD helper, formal preflight, typed/path helper official calls;
- official input, token, capture, controller, verifier, evaluator/Gold;
- rankings, policy, source audit, 5C-B inventory, reservation or Stage3B;
- a second wrapper or Python process;
- reset, rebase, force-push, history rewrite or automatic continuation.

## Requested Completion State

    AMENDMENT_5G_B_1_1_VALIDATOR_SEMANTICS_VERIFIED_AWAITING_REVIEW
    HARD_FAILURE_11_AUDIT_ACCEPTED
    REAL_PRECOMMIT_VALIDATOR_REMAINS_FROZEN

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

Until a new approval binds the future package commit:

    AMENDMENT_5G_B_1_1_PACKAGE_AWAITING_APPROVAL
    VALIDATOR_SEMANTICS_CHECK_NOT_APPROVED
