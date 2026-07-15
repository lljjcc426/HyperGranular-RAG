# Stage4B-U1-D Pre-Gold Hard Failure 14

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Failure date: 2026-07-15
- Corrected Amendment 5G-B.1.1.1.1 package: 3d37c8a65888c2093403a71375bfa94dd51bac2e
- Approval governance: ba50d75e41f6046c2b0380462c3d7480542e15c4
- Failure status: CORRECTED_AMENDMENT_5G_B_1_1_1_1_PRE_EXECUTION_SYNC_STOPPED_HARD_FAILURE_14
- Failure boundary: PRE_EXECUTION_SYNCHRONIZATION_VERIFIER_STDERR_GATE
- Static bootstrap reconstruction: NOT_STARTED
- Bootstrap process: NOT_STARTED
- Evidence: NOT_CREATED
- Official execution: NOT_STARTED
- Other project conversations, thread tools, and global memory used: No

## Approval-Governance Gate

The approval-governance commit was created as the exact two-path direct child of the corrected package:

    approval governance:
    ba50d75e41f6046c2b0380462c3d7480542e15c4

    parent:
    3d37c8a65888c2093403a71375bfa94dd51bac2e

    changed paths:
    AGENTS.md
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_APPROVAL_DECISION.md

The commit and push succeeded. The worktree was clean before pre-execution source reconstruction.

## Static Pre-Execution Reconstruction

The approved pre-execution verifier was reconstructed from the corrected Manifest with LF and no trailing newline. Before process start, the host independently checked and passed:

    source lines: 74
    source UTF-8 bytes: 4114
    source SHA-256: 4A5A4BBE08661D588673C4B4A1A7ABAB88FEB2999699658CBC91E8081266EB66

    UTF-16LE source bytes: 8188
    Base64 characters: 10920
    Base64 SHA-256: 3A70D85BDB66451877CD7000C1B7278D84E9A8952D61330D3CC8973956660F5D

    complete arguments characters: 10971
    complete arguments SHA-256: 1ED8A00D773578DD5EBCE903CE8FF4E2413E18D9FA7E82DB4D2268A0CE62C4C5

    expected stdout bytes: 122
    expected stdout SHA-256: BCDF0010147E5952AD0372ADF39EDA0A18D349B02107C340DEF05BAFE18C0F09

No source or transport mismatch was observed before the one authorized process start.

## Failed Runtime Gate

The host launched exactly one pre-execution Windows PowerShell verifier through the frozen ProcessStartInfo contract. It closed standard input immediately and captured standard output, standard error and exit code in memory.

The post-process checks were ordered as:

1. exit code must equal zero;
2. stderr byte length must equal zero;
3. stdout length, SHA-256 and exact bytes must match the frozen 122-byte success output.

The exit-code check passed, establishing:

    verifier exit code: 0

The next check found non-empty stderr and raised:

    Pre verifier stderr was non-empty

The ordered gate stopped there. The stdout byte-count, SHA-256 and exact-content comparisons were not executed after this failure and cannot be recorded as passed.

The outer host did not persist verifier stdout or stderr to a file. Because the command threw before emitting its summary and the process cannot be retried, the exact stderr bytes/content and the captured stdout bytes/content are unavailable for this checkpoint. No claim is made about whether the non-empty stderr was transport metadata, a warning or another payload.

The verifier's internal Git-child count is not independently recoverable from the failed outer report. The approved maximum was five. The process exit was zero, but exact 5/5 child completion and the verifier's exact success stdout are not accepted without the failed stderr/stdout gates.

## One-Time Counts

    approval-governance commits: 1
    approval-governance pushes: 1
    pre-execution static source/transport reconstructions: 1
    pre-execution synchronization-verifier PowerShell processes: 1
    pre-execution Git children: UNCONFIRMED, authorized maximum 5
    accepted exact 122-byte pre-verifier successes: 0
    static bootstrap reconstruction attempts: 0
    bootstrap PowerShell processes: 0
    recovery-harness PowerShell processes: 0
    compatible-verifier PowerShell processes: 0
    semantics-wrapper PowerShell processes: 0
    Python processes: 0
    machine evidence creations: 0
    narrative evidence creations: 0
    evidence commits: 0
    post-evidence synchronization-verifier PowerShell processes: 0
    post-evidence Git children: 0
    complete synthetic runs: 0
    real precommit validator invocations: 0
    formal preflight invocations: 0
    official input accesses: 0
    authorization token uses: 0
    capture invocations: 0
    automatic retries: 0

No alternate PowerShell runtime, `gh`, REST, browser, direct Git fallback or second verifier invocation was used.

## Failure-Side-Effect Audit

Immediately after failure, read-only local checks confirmed:

    local HEAD:
    ba50d75e41f6046c2b0380462c3d7480542e15c4

    origin/main tracking ref:
    ba50d75e41f6046c2b0380462c3d7480542e15c4

    worktree:
    clean

All four evidence paths remained absent:

    results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_validator_semantics.json
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_VALIDATOR_SEMANTICS_AUDIT.md
    results/stage4b_u1_d_pregold_amendment_5g_b_1_1_validator_semantics.json
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_VALIDATOR_SEMANTICS_AUDIT.md

No bootstrap, harness, compatible verifier, semantics wrapper, Python or post-evidence verifier was started. No machine or narrative evidence was created.

No script, test, dataset, cache, official artifact, historical evidence or prior failure record was modified or deleted. No synthetic, real validator, fresh direct-child, helper, preflight, official input, token, capture, controller, verifier, evaluator/Gold, rankings, policy, source audit, 5C-B inventory, reservation or Stage3B action occurred.

## Stop Boundary

The corrected Amendment 5G-B.1.1.1.1 ordered execution is consumed and stopped at the pre-execution verifier stderr gate. Static bootstrap reconstruction and all downstream semantics actions remain unstarted.

Independent review must determine whether a new diagnostic Amendment should preserve exact stdout/stderr bytes from a controlled pre-verifier run before any further recovery is proposed. The current approval cannot be reused, even though the verifier process exited zero.

Until a new approval:

    CORRECTED_AMENDMENT_5G_B_1_1_1_1_PRE_EXECUTION_SYNC_STOPPED_HARD_FAILURE_14
    PRE_EXECUTION_SYNCHRONIZATION_NOT_VERIFIED
    STATIC_BOOTSTRAP_RECONSTRUCTION_NOT_STARTED
    REAL_PRECOMMIT_VALIDATOR_REMAINS_FROZEN

    PRE_EXECUTION_SYNC_DIAGNOSTIC_NOT_APPROVED
    PRE_EXECUTION_SYNC_RETRY_NOT_APPROVED
    STATIC_SOURCE_RECONSTRUCTION_NOT_APPROVED
    BOOTSTRAP_NOT_APPROVED
    VALIDATOR_SEMANTICS_WRAPPER_NOT_APPROVED
    EVIDENCE_CREATION_NOT_APPROVED
    POST_EVIDENCE_SYNC_NOT_APPROVED
    FRESH_SYNTHETIC_REBINDING_NOT_APPROVED
    FRESH_THREE_PATH_DIRECT_CHILD_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_INPUT_ACCESS_NOT_APPROVED
    AUTHORIZATION_TOKEN_USE_NOT_APPROVED
    OFFICIAL_CAPTURE_NOT_APPROVED
    CONTROLLER_RERUN_NOT_APPROVED
    VERIFIER_NOT_APPROVED
    GOLD_NOT_APPROVED
