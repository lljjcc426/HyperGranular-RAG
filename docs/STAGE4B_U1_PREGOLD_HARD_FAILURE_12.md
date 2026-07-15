# Stage4B-U1-D Pre-Gold Hard Failure 12

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Failure date: 2026-07-15
- Amendment 5G-B.1.1 package: c4101cfafbc08d518cd4b56e5d199f9d5937294b
- Approval governance: e18dcb13b64e8a50d764fc9eacbabcdea7c5393f
- Failure status: AMENDMENT_5G_B_1_1_SOURCE_HASH_VERIFICATION_STOPPED_HARD_FAILURE_12
- Failure boundary: PRE_EXECUTION_SOURCE_HASH_HEX_ENCODING
- Frozen wrapper invocation: NOT_STARTED
- Python process: NOT_STARTED
- Semantics evidence: NOT_CREATED
- Official execution: NOT_STARTED
- Other project conversations, thread tools, and global memory used: No

## Approval-Governance Gate

The approval-governance commit was created as the direct child of the approved package:

    approval governance:
    e18dcb13b64e8a50d764fc9eacbabcdea7c5393f

    parent:
    c4101cfafbc08d518cd4b56e5d199f9d5937294b

Its changed-path set was exactly:

    AGENTS.md
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_APPROVAL_DECISION.md

The commit was pushed. Before source verification, local HEAD, origin/main and GitHub main all equaled the approval-governance commit, the worktree was clean, and both fresh semantics evidence paths were absent.

## Failed Pre-Execution Gate

The approved sequence required reconstructing and independently checking the frozen source line counts, UTF-8 byte counts and SHA-256 values before the one-time wrapper invocation.

The read-only PowerShell gate loaded only the Amendment 5G-B.1.1 Manifest and reconstructed the registered Python and PowerShell sources with LF and no trailing newline. The following checks completed before failure:

    Python source lines: 46
    Python source UTF-8 bytes: 2284

The gate then computed the Python SHA-256 bytes and attempted to convert them to uppercase hexadecimal with:

    [System.Convert]::ToHexString(...)

The active Windows PowerShell 5.1 runtime does not provide that method. PowerShell terminated with:

    Method invocation failed because [System.Convert] does not contain a method named 'ToHexString'.
    FullyQualifiedErrorId : MethodNotFound

This is a verification-command runtime compatibility failure. It is not an observed source hash mismatch and does not establish a defect in the frozen PowerShell wrapper, embedded Python source or real precommit validator.

The following source gates were not reached in this invocation:

    Python SHA-256 equality
    PowerShell source line/byte/SHA-256 equality
    embedded Python byte equality
    expected wrapper stdout byte/SHA-256 equality

The frozen wrapper was not part of the failed command and was not invoked. No Python process was started.

## One-Time Counts

    approval-governance commits: 1
    source-verification attempts: 1
    frozen wrapper invocations: 0
    Python processes: 0
    successful nine-fixture summaries: 0
    complete synthetic runs: 0
    real precommit validator invocations: 0
    fresh evidence commits: 0
    fresh three-path direct-child commits: 0
    formal preflight invocations: 0
    official input accesses: 0
    token uses: 0
    capture invocations: 0
    automatic retries: 0

No compatible replacement hex conversion was substituted after the error. The source-verification command and wrapper were not retried.

## Failure-Side-Effect Audit

Immediately after failure:

    HEAD:
    e18dcb13b64e8a50d764fc9eacbabcdea7c5393f

    origin/main:
    e18dcb13b64e8a50d764fc9eacbabcdea7c5393f

The two approved success-only evidence paths remained absent:

    results/stage4b_u1_d_pregold_amendment_5g_b_1_1_validator_semantics.json
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_VALIDATOR_SEMANTICS_AUDIT.md

No scripts, tests, results, cache, official artifacts, historical evidence or frozen validator source were modified or deleted. No complete synthetic runner, real precommit validator, execution-head helper, formal preflight, typed/path helper official call, official input, authorization token, capture, controller, verifier, evaluator/Gold, rankings, policy, source audit, 5C-B inventory, reservation or Stage3B action occurred.

## Stop Boundary

The Amendment 5G-B.1.1 execution sequence is stopped before the frozen wrapper. Although the wrapper and Python counters remain zero, the failed required pre-execution gate cannot be repaired and continued under the same approval.

An independent review must decide whether a minimal package-bound recovery may replace only the SHA-byte-to-hex conversion with a Windows PowerShell 5.1-compatible, deterministically frozen implementation and reauthorize source verification plus the single semantics wrapper.

Until a new approval:

    AMENDMENT_5G_B_1_1_SOURCE_HASH_VERIFICATION_STOPPED_HARD_FAILURE_12
    VALIDATOR_SEMANTICS_CHECK_NOT_STARTED
    REAL_PRECOMMIT_VALIDATOR_REMAINS_FROZEN

    SOURCE_VERIFICATION_RETRY_NOT_APPROVED
    VALIDATOR_SEMANTICS_WRAPPER_NOT_APPROVED
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
