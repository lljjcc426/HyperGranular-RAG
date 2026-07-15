# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1 Approval Decision

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Approval date: 2026-07-15
- Decision: APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_FROZEN_VALIDATOR_SEMANTICS_HARNESS_ONLY
- Package commit: c4101cfafbc08d518cd4b56e5d199f9d5937294b
- Hard Failure 11 checkpoint: d2aadb2f03f4388d71ddf70fcfb116c92fe4b008
- Official execution: NOT_APPROVED
- Other project conversations, thread tools, and global memory used: No

## Frozen Package Binding

This approval strictly binds:

    package commit:
    c4101cfafbc08d518cd4b56e5d199f9d5937294b

    PowerShell wrapper source lines:
    122

    PowerShell wrapper source bytes:
    7890

    PowerShell wrapper source SHA-256:
    DFA95A904CE371F283B8DBA8BB4D98CC048F345F536C0E7D0D6DB8073DF9E16C

    embedded Python source lines:
    46

    embedded Python source bytes:
    2284

    embedded Python source SHA-256:
    D0D3D6FC37AD0C2649A7A7F88EFA944C357033E3F0E956BE0E27C4374653D602

    expected PowerShell wrapper stdout bytes:
    789

    expected PowerShell wrapper stdout SHA-256:
    EDBD4614B790256E314F4A8963128A5FB5A190FAC197437FB349D4C33C606135

The sources must be reconstructed from the package Manifest by joining the registered source lines with LF and no trailing newline. The embedded Python bytes in the wrapper must equal the separately frozen Python source bytes. No wrapper expression, temporary try/catch, redirection, diagnostic output, replacement source or additional parser call may be added.

The real precommit validator remains frozen and unexecuted:

    source lines:
    195

    source bytes:
    15966

    source SHA-256:
    0F066387B8523B0EA387444076A1113913082D283C28C2DE3FFB33872D558249

## Approval-Governance Boundary

This approval-governance commit must be the direct child of `c4101cfafbc08d518cd4b56e5d199f9d5937294b` and must change exactly:

    AGENTS.md
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_APPROVAL_DECISION.md

Before the semantics harness is invoked, local HEAD, origin/main and GitHub main must equal this approval-governance commit, the worktree must be clean, and both future evidence paths must be absent.

## Authorized Sequence

Only the following sequence is approved:

1. Commit and push this approval decision and the matching `AGENTS.md` state update as the exact two-path direct child of the package commit.
2. Confirm local/origin/GitHub equality, clean worktree and absence of both future evidence paths.
3. Reconstruct and independently verify the frozen PowerShell and Python source line counts, bytes and SHA-256 values; verify the embedded Python source is byte-identical.
4. Invoke the frozen PowerShell wrapper exactly once. It may start exactly one Python process.
5. Require exact success: PowerShell fixtures 7/7, raw JSON fixtures 2/2, total 9/9, passed 9, Python exit 0, stderr 0, stdout 789 bytes and stdout SHA-256 `EDBD4614B790256E314F4A8963128A5FB5A190FAC197437FB349D4C33C606135`.
6. Require zero harness counters for filesystem, Git/GitHub, helper, official path, token and capture access.
7. Exclusive-create the exact machine evidence and narrative audit paths.
8. Commit exactly those two paths as the direct child of this approval-governance commit, push, confirm three-way synchronization and a clean worktree, then stop immediately.

One-time limits:

    approval-governance commits = 1
    semantics wrapper invocations = 1
    Python processes = 1
    semantics evidence commits = 1
    complete synthetic runs = 0
    real precommit validator invocations = 0
    fresh three-path direct-child commits = 0
    derived execution-head helper calls = 0
    formal preflight invocations = 0
    official input access = 0
    token uses = 0
    capture invocations = 0
    automatic retry = false

Any gate failure consumes the relevant one-time authorization and requires a new Hard Failure checkpoint. Same-approval repair or retry is forbidden.

## Fresh Evidence Boundary

The only approved fresh evidence paths are:

    results/stage4b_u1_d_pregold_amendment_5g_b_1_1_validator_semantics.json
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_VALIDATOR_SEMANTICS_AUDIT.md

The machine evidence must be byte-identical to the exact 789-byte wrapper stdout, with no reserialization, indentation or trailing newline. The evidence commit must contain exactly these two paths and must not update any governance or status file.

## Explicitly Not Authorized

- complete synthetic rebinding;
- real precommit validator execution;
- 5G-B.1 fresh three-path artifacts or direct-child;
- derived execution-HEAD helper;
- formal preflight or typed/path helper official call;
- official input, authorization token or official capture;
- controller, verifier, evaluator/Gold, rankings, policy or source audit;
- 5C-B inventory, reservation or Stage3B;
- code, tests, scientific parameters or historical artifact changes;
- reset, rebase, force-push, history rewrite, retry or automatic continuation after the evidence commit.

## Approved Completion State

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
