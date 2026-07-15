# Stage4B-U1-D Pre-Gold Amendment 5G-B.1 Approval Decision

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Approval date: 2026-07-15
- Decision: APPROVE_CORRECTED_AMENDMENT_5G_B_1_GOVERNANCE_VALIDATOR_AND_FRESH_REBINDING_DIRECT_CHILD_ONLY
- Corrected package commit: 48a9c1438166eaf895104358b2d8cd8c9b043020
- Superseded package commit: 9536ffb4ce845aeff9db3552f890612ca6e9e2a3 (NOT_APPROVABLE, NOT_REUSABLE)
- Official execution: NOT_APPROVED
- Other project conversations, thread tools, and global memory used: No

## Frozen Validator Binding

This approval binds the complete real precommit validator stored in the corrected Manifest with the following exact values:

    corrected package:
    48a9c1438166eaf895104358b2d8cd8c9b043020

    validator source lines:
    195

    validator source bytes:
    15966

    validator source SHA-256:
    0F066387B8523B0EA387444076A1113913082D283C28C2DE3FFB33872D558249

The source must be reconstructed by joining the Manifest source_lines with LF and no trailing newline. No wrapper expression, source extension, replacement validator or post-approval check may be added.

## Approval-Governance Boundary

This approval-governance commit must be the direct child of 48a9c1438166eaf895104358b2d8cd8c9b043020 and must change exactly:

    AGENTS.md
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_APPROVAL_DECISION.md

Before semantics or synthetic execution, local HEAD, origin/main and GitHub main must equal this commit and the worktree must be clean.

## Authorized Sequence

Only the following sequence is approved:

1. One in-memory semantics wrapper invocation covering all nine Manifest fixtures, using exactly one frozen Python parser process and no other subprocess or access.
2. Exactly two complete frozen runner invocations on identical tracked bytes: run 1 to one unique OS-temp file and run 2 to the fresh registered evidence path.
3. Direct byte comparison of both complete evidence files; delete run 1 only after every gate passes.
4. Exclusive-create the fresh narrative audit and fresh governance binding.
5. Reconstruct, hash-check and invoke the frozen real precommit validator exactly once.
6. If and only if the validator succeeds, create and push one direct-child commit containing exactly the three fresh registered paths.
7. Confirm local/origin/GitHub equality and clean worktree, then stop immediately.

One-time limits:

    semantics wrapper invocations = 1
    Python raw-parser processes = 1
    complete synthetic runs = 2
    real frozen validator invocations = 1
    fresh direct-child commits = 1
    automatic retry = false

Any gate failure consumes that authorization, requires a new Hard Failure checkpoint and forbids same-approval repair or retry.

## Required Zero Counters

At approval time and throughout this approval boundary:

    execution-head helper calls = 0
    formal preflight = 0
    official input access = 0
    token = 0
    capture = 0

## Explicitly Not Authorized

- code or test modification;
- historical 5G-B artifact modification, deletion, migration or active reuse;
- execution-HEAD helper, formal preflight or typed/path helper official calls;
- official input, authorization token or official capture;
- controller, verifier, evaluator/Gold, rankings, policy or source audit;
- 5C-B inventory, reservation or Stage3B;
- reset, rebase, force-push, history rewrite or automatic continuation after the fresh direct-child.

## Approved Completion State

    AMENDMENT_5G_B_1_FRESH_REBINDING_DIRECT_CHILD_COMPLETE_AWAITING_REVIEW
    HARD_FAILURE_10_DIRECT_CAUSE_CONFIRMED
    HISTORICAL_5G_B_ARTIFACTS_FROZEN

    DERIVED_EXECUTION_HEAD_VALIDATION_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_INPUT_ACCESS_NOT_APPROVED
    AUTHORIZATION_TOKEN_USE_NOT_APPROVED
    OFFICIAL_CAPTURE_NOT_APPROVED
    CONTROLLER_RERUN_NOT_APPROVED
    VERIFIER_NOT_APPROVED
    GOLD_NOT_APPROVED
