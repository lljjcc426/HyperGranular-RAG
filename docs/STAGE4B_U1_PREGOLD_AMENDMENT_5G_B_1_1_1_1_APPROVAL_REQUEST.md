# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1 Approval Request

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Request date: 2026-07-15
- Requested decision: APPROVE_CORRECTED_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_FROZEN_PRE_AND_POST_SYNCHRONIZATION_RECOVERY_AND_UNCHANGED_BOOTSTRAP_SEMANTICS_ONLY
- Current checkpoint: 93cc76ae97043077d2d3dae93e2569833ea3ab59
- Package execution authority: NONE UNTIL A NEW APPROVAL BINDS THE FUTURE PACKAGE COMMIT
- Official execution: NOT_REQUESTED
- Other project conversations, thread tools, and global memory used: No

## Review Basis

Hard Failure 13 Review 1 accepts the fail-closed stop and confirms that the corrected 5G-B.1.1.1 approval-governance commit is valid and was retrospectively observed on GitHub. Runtime three-way verification nevertheless did not pass because its separate GitHub-main command depended on unavailable `gh`.

The prior ordered approval is consumed. This request does not reuse it and does not treat retrospective GitHub evidence as a runtime gate result.

Package Review 1 accepts the original package scope and the complete 74-line pre-execution verifier, but rejects package `93cc76ae97043077d2d3dae93e2569833ea3ab59` because the required post-evidence synchronization gate was not frozen and the invocation-count wording was inconsistent. This corrected package supersedes that unapproved commit and adds only a separately frozen post-evidence verifier plus governance updates.

## Bound Commits

This request binds:

    corrected 5G-B.1.1.1 package:
    e37400707a65d11c9f038d13e7be0ec2a19d27a4

    corrected 5G-B.1.1.1 approval governance:
    f46afbf565beca5672ef443bccb67c33ebd26876

    Hard Failure 13 checkpoint:
    e159558b621f516598dc4fd2aede151c84472950

    superseded unapproved 5G-B.1.1.1.1 package:
    93cc76ae97043077d2d3dae93e2569833ea3ab59

    frozen semantics implementation:
    48a9c1438166eaf895104358b2d8cd8c9b043020

Any approval that does not explicitly bind the future package commit containing this Request and its Manifest is invalid.

## Frozen Corrected Manifest

The unchanged bootstrap, recovery harness, compatible verifier and semantics chain remain governed by:

    E:\科研\HyperGranular-RAG\docs\STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_MANIFEST.json

Its externally frozen identity is:

    bytes:
    30174

    SHA-256:
    A5AA1E9B4CB022AFCCF401E9C2193FC06FD45830151154E049DC7B59BB77E6AE

The new synchronization verifier does not modify or execute any source from this Manifest. The future bootstrap continues to read this exact corrected Manifest after synchronization succeeds.

## Frozen Pre-Execution Synchronization Verifier

The complete pre-reconstruction verifier is frozen in the new Manifest by LF-joined source lines with no trailing newline:

    runtime:
    Windows PowerShell 5.1 Desktop

    source lines:
    74

    source UTF-8 bytes:
    4114

    source SHA-256:
    4A5A4BBE08661D588673C4B4A1A7ABAB88FEB2999699658CBC91E8081266EB66

Package assembly performed only static PowerShell parsing; syntax-error count was zero. The verifier has not been invoked.

Its PowerShell transport is also frozen:

    executable:
    C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe

    arguments prefix:
    -NoLogo -NoProfile -NonInteractive -EncodedCommand

The registered arguments prefix includes one trailing U+0020 space after `-EncodedCommand`; the Markdown display line above omits that trailing whitespace.

    UTF-16LE source bytes:
    8188

    Base64 characters:
    10920

    Base64 ASCII SHA-256:
    3A70D85BDB66451877CD7000C1B7278D84E9A8952D61330D3CC8973956660F5D

    complete arguments characters:
    10971

    complete arguments ASCII SHA-256:
    1ED8A00D773578DD5EBCE903CE8FF4E2413E18D9FA7E82DB4D2268A0CE62C4C5

The parent ProcessStartInfo must use `UseShellExecute=false`, redirected standard input/output/error, `CreateNoWindow=true`, UTF-8 stdout/stderr decoding and immediate standard-input close. Temporary `.ps1` files are forbidden.

## Frozen Five-Process Git Contract

The synchronization verifier uses only:

    git executable:
    C:\Program Files\Git\cmd\git.exe

    working directory:
    E:\科研\HyperGranular-RAG

It starts exactly these five child processes, in order, with exact `Arguments` strings:

| Order | Arguments |
|---:|---|
| 1 | `fetch origin main --quiet` |
| 2 | `rev-parse HEAD` |
| 3 | `rev-parse refs/remotes/origin/main` |
| 4 | `ls-remote --exit-code origin refs/heads/main` |
| 5 | `status --porcelain=v1` |

Each child uses the same fixed ProcessStartInfo fields as registered in the Manifest. Standard input is closed immediately after start. All five children must exit 0 and emit empty stderr.

Fetch stdout and status stdout must be zero bytes. Both revision outputs must match exactly one lowercase 40-character SHA plus one LF or CRLF terminator. Direct remote stdout must match exactly one lowercase 40-character SHA, one TAB, `refs/heads/main`, and one LF or CRLF terminator. Multiline output, extra refs, uppercase SHA, substring matches and missing terminators are rejected.

The three SHAs must be identical. The approval-governance parent/path gate outside this verifier must already have established that local HEAD is the newly approved exact-two-path governance commit. The verifier also checks all four old/target evidence paths before and after Git execution and rejects either a file or directory collision.

The exact fixed success stdout is:

    {"status":"THREE_WAY_SYNC_VERIFIED","git_processes":5,"all_equal":true,"worktree_clean":true,"evidence_paths_absent":true}

Its identity is:

    stdout bytes:
    122

    stdout SHA-256:
    BCDF0010147E5952AD0372ADF39EDA0A18D349B02107C340DEF05BAFE18C0F09

    stderr bytes:
    0

    exit code:
    0

No `gh`, REST API, browser, remote fallback, extra Git command or automatic retry is allowed.

## Frozen Post-Evidence Synchronization Verifier

The corrected package separately freezes a post-evidence verifier by LF-joined source lines with no trailing newline:

    runtime:
    Windows PowerShell 5.1 Desktop

    source lines:
    107

    source UTF-8 bytes:
    7130

    source SHA-256:
    8877E18F75A94EE6DA326B09C3791E6641B6B9B32D42744BA23E033A20735A67

Static PowerShell parsing reports zero syntax errors. The source has not been invoked.

Its parent transport is frozen as:

    executable:
    C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe

    arguments prefix:
    -NoLogo -NoProfile -NonInteractive -EncodedCommand

The post-evidence registered arguments prefix also includes one trailing U+0020 space after `-EncodedCommand`; the Markdown display line above omits that trailing whitespace.

    UTF-16LE source bytes:
    14220

    Base64 characters:
    18960

    Base64 ASCII SHA-256:
    89F51EC73B762A7E8E9E661D0D2B81CAF6EB330A3C4C4789B375E72F2930DDE1

    complete arguments characters:
    19011

    complete arguments ASCII SHA-256:
    17327F58C123664224B95FABD85E7553B3E32F4F86659D9A17D13C68AD9FEB02

The parent ProcessStartInfo must set the process-scoped environment variable `HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT` to the exact newly created approval-governance commit SHA. The value must be lowercase 40-character hexadecimal. The verifier rejects a missing or malformed value and requires `git rev-parse HEAD^` to equal it exactly.

The verifier starts exactly seven Git children in this order:

| Order | Arguments |
|---:|---|
| 1 | `fetch origin main --quiet` |
| 2 | `rev-parse HEAD` |
| 3 | `rev-parse refs/remotes/origin/main` |
| 4 | `ls-remote --exit-code origin refs/heads/main` |
| 5 | `status --porcelain=v1` |
| 6 | `rev-parse HEAD^` |
| 7 | `diff-tree --no-commit-id --name-only -r HEAD` |

All seven use `C:\Program Files\Git\cmd\git.exe`, working directory `E:\科研\HyperGranular-RAG`, the same frozen redirected/no-window UTF-8 ProcessStartInfo fields, immediate stdin close, exit 0 and empty stderr.

Before and after Git execution, the verifier requires the two target evidence paths to exist as regular files and both older 5G-B.1.1 paths to remain absent. Machine evidence must remain exactly 789 bytes with SHA-256 `EDBD4614B790256E314F4A8963128A5FB5A190FAC197437FB349D4C33C606135`; narrative audit must be non-empty. Pre/post byte count and SHA must remain identical for both files.

The evidence commit changed-path output must contain exactly the target narrative and machine paths, in either of their two possible complete two-line orders, with no additional path. Local HEAD, fetched origin and direct remote SHA must match exactly, and worktree status must be empty.

The fixed success stdout is:

    {"status":"POST_EVIDENCE_SYNC_VERIFIED","git_processes":7,"all_equal":true,"worktree_clean":true,"evidence_commit_parent_bound":true,"evidence_paths_exact":true,"machine_evidence_verified":true}

Its identity is:

    stdout bytes:
    194

    stdout SHA-256:
    2ED3F942961C4DA1F7A9D71C3B8A50E6E00275DBBE4038C594B8834B7499AB0F

    stderr bytes:
    0

    exit code:
    0

No pre-execution path-absence rule is reused after evidence creation. The post-evidence verifier has its own source, fingerprint, process count and evidence-presence contract.

## Unchanged Bootstrap And Semantics Chain

No source in the existing chain changes:

| Frozen object | Lines | Bytes | SHA-256 |
|---|---:|---:|---|
| Bootstrap | 58 | 3,909 | F8A452CEBEC06326E1D8BA4DEB4FC8915210F3FF9BBF53DA2D22B9675773C81D |
| Recovery harness | 77 | 6,246 | B34E7AE012AC0314AD44590603575194C8881CE58C17E6C8ED6568A5FA373048 |
| Compatible verifier | 59 | 3,512 | 1A30DC70AD0C01CDACBC3279F1CFD707EA4DAB457BE9C6C30A5C6D6495FA81BF |
| Semantics wrapper | 122 | 7,890 | DFA95A904CE371F283B8DBA8BB4D98CC048F345F536C0E7D0D6DB8073DF9E16C |
| Embedded Python | 46 | 2,284 | D0D3D6FC37AD0C2649A7A7F88EFA944C357033E3F0E956BE0E27C4374653D602 |
| Real precommit validator | 195 | 15,966 | 0F066387B8523B0EA387444076A1113913082D283C28C2DE3FFB33872D558249 |

Compatible-verifier stdout remains 190 bytes with SHA-256 `D05B3B2A147C51FB3A9FFFC3BEB802439E01AEFC34B708FE14C298978F2BFBB3`. Final semantics stdout remains 789 bytes with SHA-256 `EDBD4614B790256E314F4A8963128A5FB5A190FAC197437FB349D4C33C606135`.

The bootstrap, harness, compatible-verifier and wrapper complete-arguments SHA-256 values remain respectively:

    5EF7120B1005A027D408CF7DCAB525768376F2DAD213D91E69D73E1326D6F05D
    19842E8DAB9CD94C4404DAC97989388B614462DDDC098A4590DA38D31F6B127B
    DD57FC57342776A74FF4563D39BBD56AD64AFDB76B980202285ACECBB9E82026
    0E1CCE9C1DE11C964356F4A508F330C169F255E3CCEA460D65417D3E923D42D5

## Requested Approval-Governance Commit

If approved, the first commit must be the direct child of the future package commit and change exactly:

    AGENTS.md
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_APPROVAL_DECISION.md

It must be pushed before the synchronization verifier is invoked. Before the process starts, the host must independently prove the direct-parent and exact changed-path contract and reconstruct the verifier plus its EncodedCommand transport from the package Manifest.

## Requested One-Time Sequence

Only the following future sequence is requested:

1. Create and push the exact-two-path approval-governance direct child.
2. Statically reconstruct and fingerprint the 74-line pre-execution synchronization verifier and its complete transport without starting a process.
3. Launch exactly one pre-execution synchronization-verifier Windows PowerShell process.
4. Allow exactly five registered Git children and require exact success stdout, empty stderr, exit 0, three-way SHA equality, clean worktree and four absent evidence paths.
5. Statically reconstruct and verify the unchanged bootstrap plus all registered downstream transports from the corrected Manifest.
6. Launch the unchanged bootstrap exactly once.
7. Continue through exactly one recovery-harness PowerShell, one compatible-verifier PowerShell, one semantics-wrapper PowerShell and one Python process.
8. Require exact 190-byte source-verifier success and exact 789-byte 9/9 semantics success, with empty stderr and exit 0 at every layer.
9. Let the unchanged bootstrap exclusive-create the target machine evidence directly from captured raw stdout; then exclusive-create the narrative audit.
10. Commit exactly the two evidence paths as the direct child of approval governance and push.
11. Statically reconstruct the 107-line post-evidence verifier, set its one frozen process-scoped approval-parent environment binding, and launch exactly one post-evidence verifier PowerShell process.
12. Allow exactly seven registered post-evidence Git children and require exact fixed success stdout, empty stderr, exit 0, three-way SHA equality, clean worktree, exact evidence parent/path set, target-file stability and exact machine evidence fingerprint.
13. Stop immediately.

One-time limits:

    approval-governance commits: 1
    pre-execution synchronization-verifier PowerShell processes: 1
    pre-execution synchronization-verifier Git child processes: 5
    post-evidence synchronization-verifier PowerShell processes: 1
    post-evidence synchronization-verifier Git child processes: 7
    static bootstrap reconstruction attempts: 1
    bootstrap PowerShell processes: 1
    recovery-harness PowerShell processes: 1
    compatible-verifier PowerShell processes: 1
    semantics-wrapper PowerShell processes: 1
    Python processes: 1
    evidence commits: 1
    complete synthetic runs: 0
    real precommit validator invocations: 0
    formal preflight invocations: 0
    official input accesses: 0
    authorization token uses: 0
    capture invocations: 0
    automatic retries: 0

Any failure stops the sequence. A failed pre-execution verifier consumes the pre-execution position and the ordered approval; a failed post-evidence verifier consumes the post-evidence position and the ordered approval. The two sources and counters are independent. Runtime substitution, repair or retry is forbidden.

## Evidence Boundary

The unchanged bootstrap continues to target the still-absent paths:

    results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_validator_semantics.json
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_VALIDATOR_SEMANTICS_AUDIT.md

The two older 5G-B.1.1 paths must also remain absent. This recovery requests new package-bound authority for the unchanged bootstrap to create the still-uncreated target paths; it does not reuse the consumed approval.

## Package Assembly Audit

The first pre-commit ancestry-check command incorrectly treated the empty stdout of successful `git merge-base --is-ancestor` as a PowerShell Boolean and raised `Corrected package ancestry mismatch`. The command stopped before `git add`; no path was staged, committed or pushed, and no synchronization verifier or frozen semantics source was invoked.

This was a package-assembly check defect, not Git ancestry evidence. The corrective read-only check uses the Git process exit code directly. It does not alter the frozen verifier source, transport, Git child contract or requested execution counts.

During corrected-package assembly, two full consistency commands stopped at `git diff --check` on the same unresolved post-evidence Markdown trailing-space line. The first corrective patch matched the earlier pre-execution display occurrence because its context was not unique, so the post-evidence line remained and the second command stopped at the same gate. A direct all-line trailing-whitespace scan then identified exactly that one remaining line. No later check, staging, commit, push or verifier invocation occurred in either command. Both display lines now omit trailing whitespace; the required U+0020 remains machine-frozen in both Manifest `arguments_prefix` values, and no source or transport fingerprint changed.

## Explicitly Not Requested

- package-assembly execution of the synchronization verifier or any frozen semantics source;
- installation or use of `gh`, REST, browser automation or another remote fallback;
- reuse of the consumed corrected 5G-B.1.1.1 approval;
- modification of bootstrap, harness, compatible verifier, wrapper, Python, fixtures, expected output or real validator;
- scripts, tests, results, historical evidence, failure-record or official-artifact changes;
- complete synthetic rebinding, real validator or fresh three-path direct-child;
- formal preflight, official input, token, capture, controller, verifier or evaluator/Gold;
- rankings, policy, source audit, 5C-B inventory, reservation or Stage3B;
- reset, rebase, force-push, retry or automatic continuation.

## Requested Completion State

    AMENDMENT_5G_B_1_1_1_1_VALIDATOR_SEMANTICS_VERIFIED_AWAITING_REVIEW
    HARD_FAILURE_13_AUDIT_ACCEPTED
    PRE_EXECUTION_THREE_WAY_GITHUB_MAIN_SYNCHRONIZATION_VERIFIED
    POST_EVIDENCE_THREE_WAY_GITHUB_MAIN_SYNCHRONIZATION_VERIFIED
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

## Current Stop State

This Request and Manifest are governance materials only. Until an independent approval explicitly binds their future package commit:

    CORRECTED_AMENDMENT_5G_B_1_1_1_1_PACKAGE_AWAITING_APPROVAL
    PRE_EXECUTION_SYNC_VERIFICATION_NOT_APPROVED
    POST_EVIDENCE_SYNC_VERIFICATION_NOT_APPROVED
    STATIC_SOURCE_RECONSTRUCTION_NOT_APPROVED
    BOOTSTRAP_NOT_APPROVED
    VALIDATOR_SEMANTICS_WRAPPER_NOT_APPROVED
    OFFICIAL_EXECUTION_NOT_APPROVED
