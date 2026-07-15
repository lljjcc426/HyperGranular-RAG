# Stage4B-U1-D Pre-Gold Hard Failure 13 Review 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review date: 2026-07-15
- Reviewed checkpoint: e159558b621f516598dc4fd2aede151c84472950
- Decision: ACCEPT_HARD_FAILURE_13_AUDIT
- Recovery: RETURN_FOR_AMENDMENT_5G_B_1_1_1_1_SYNC_VERIFICATION_RECOVERY_PACKAGE
- Execution authorized: No
- Other project conversations, thread tools, and global memory used: No

## Bound History

    corrected package:
    e37400707a65d11c9f038d13e7be0ec2a19d27a4

    approval governance:
    f46afbf565beca5672ef443bccb67c33ebd26876

    Hard Failure 13 checkpoint:
    e159558b621f516598dc4fd2aede151c84472950

The approval-governance commit is the exact two-path direct child of the corrected package. Independent retrospective GitHub history confirms that it was pushed and is in the direct history of the Hard Failure 13 checkpoint. This retrospective evidence does not convert the failed runtime three-way gate into a pass.

## Accepted Failure Classification

Hard Failure 13 occurred before static source reconstruction. The required GitHub-main check attempted to call `gh`, which is unavailable in the active environment, and stopped with `CommandNotFoundException`.

The direct cause is:

    LOCAL_VERIFICATION_TOOL_AVAILABILITY_FAILURE

It is not evidence of:

    network failure
    push failure
    GitHub main SHA mismatch
    local/origin divergence
    source reconstruction failure
    bootstrap or semantics defect

The push and fetch succeeded, and local HEAD plus fetched `origin/main` equaled the approval-governance commit. The separately required direct GitHub-main value was not obtained at runtime, so fail-closed stopping was correct.

## Accepted Zero-Execution Boundary

    static reconstruction attempts: 0
    bootstrap invocations: 0
    recovery-harness PowerShell processes: 0
    compatible-verifier PowerShell processes: 0
    semantics-wrapper PowerShell processes: 0
    Python processes: 0
    machine evidence creations: 0
    narrative evidence creations: 0
    synthetic runs: 0
    real validator invocations: 0
    official input accesses: 0
    authorization token uses: 0
    capture invocations: 0
    automatic retries: 0

All four old/target evidence paths remained absent. No script, test, dataset, cache, official artifact, historical evidence or failure record was modified or deleted.

## Required Recovery Package

Amendment 5G-B.1.1.1.1 must freeze a pre-reconstruction synchronization verifier that uses the already available `git.exe`, not `gh`, REST, browser automation or an installation step.

The verifier must start exactly five Git child processes through a frozen `.NET ProcessStartInfo` contract:

    fetch origin main --quiet
    rev-parse HEAD
    rev-parse refs/remotes/origin/main
    ls-remote --exit-code origin refs/heads/main
    status --porcelain=v1

Every child must exit 0 with empty stderr. Fetch and status stdout must be empty. Both revision outputs must be one lowercase 40-character SHA line. Direct remote output must be exactly one `<sha><TAB>refs/heads/main` line. Local HEAD, fetched `origin/main` and direct remote SHA must be identical, the worktree must be clean, and all four evidence paths must remain absent.

The package must freeze source lines, UTF-8 bytes, source SHA-256, PowerShell transport, Git executable, working directory, exact child arguments, ProcessStartInfo fields, output grammar, process count and fixed success stdout.

## Unchanged Chain

The following content must remain unchanged:

    58-line bootstrap
    77-line recovery harness
    59-line compatible verifier
    122-line semantics wrapper
    46-line embedded Python
    195-line real precommit validator

The new package may request a future ordered execution beginning with a fresh exact-two-path approval-governance commit, one synchronization-verifier process and five Git children. Only after synchronization success may it continue through the previously frozen static reconstruction, bootstrap, harness, verifier, wrapper and Python sequence.

## Current State

    HARD_FAILURE_13_AUDIT_ACCEPTED
    HARD_FAILURE_13_CHECKPOINT_FROZEN
    APPROVAL_GOVERNANCE_COMMIT_VALID
    APPROVAL_PUSH_RETROSPECTIVELY_CONFIRMED_ON_GITHUB
    RUNTIME_THREE_WAY_GATE_NOT_COMPLETED

    RETURN_FOR_AMENDMENT_5G_B_1_1_1_1_PACKAGE
    CURRENT_CORRECTED_5G_B_1_1_1_APPROVAL_CONSUMED
    THREE_WAY_SYNC_VERIFICATION_RETRY_NOT_APPROVED
    STATIC_SOURCE_RECONSTRUCTION_NOT_APPROVED
    BOOTSTRAP_NOT_APPROVED
    VALIDATOR_SEMANTICS_WRAPPER_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_INPUT_ACCESS_NOT_APPROVED
    AUTHORIZATION_TOKEN_USE_NOT_APPROVED
    OFFICIAL_CAPTURE_NOT_APPROVED
    CONTROLLER_RERUN_NOT_APPROVED
    VERIFIER_NOT_APPROVED
    GOLD_NOT_APPROVED
