# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1 Approval Request

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Request date: 2026-07-15
- Requested decision: APPROVE_CORRECTED_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_FROZEN_BOOTSTRAP_RECOVERY_EXECUTION_HARNESS_SOURCE_VERIFICATION_AND_SEMANTICS_ONLY
- Current checkpoint: 8002dac6fa37e0009f0e0bc78858b467bbff675e
- Package execution authority: NONE UNTIL A NEW APPROVAL BINDS THE FUTURE PACKAGE COMMIT
- Official execution: NOT_REQUESTED
- Other project conversations, thread tools, and global memory used: No

## Review Basis

Hard Failure 12 review accepts the audit and confirms that the 5G-B.1.1 approval-governance gate passed. The required source-verification command then failed before wrapper execution because Windows PowerShell 5.1 does not implement `[System.Convert]::ToHexString(...)`.

The observed failure is strictly:

    SOURCE_HASH_HEX_ENCODING_COMPATIBILITY_FAILURE

It is not evidence of:

    source hash mismatch
    PowerShell wrapper drift
    embedded Python drift
    fixture failure
    real precommit validator defect

The prior ordered approval is consumed even though wrapper and Python counts remain zero. It must not be reused.

## Package Review 1 And Supersession

Package commit `d1876bd9ccc198285808795f7f1809c4d1a48e1c` is not approvable because it froze the 59-line verifier but not the verifier bootstrap, child-process transport or raw stdout-to-evidence path. This corrected package explicitly supersedes that commit while retaining its statically accepted verifier content.

Package Review 1 is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_PACKAGE_REVIEW_1.md`. The corrected package adds no script, test or result implementation. It freezes the previously missing execution envelope entirely inside the Request and Manifest.

## Bound Commits

This request binds:

    5G-B.1.1 package:
    c4101cfafbc08d518cd4b56e5d199f9d5937294b

    5G-B.1.1 approval governance:
    e18dcb13b64e8a50d764fc9eacbabcdea7c5393f

    Hard Failure 12 checkpoint:
    8002dac6fa37e0009f0e0bc78858b467bbff675e

    Hard Failure 11 checkpoint:
    d2aadb2f03f4388d71ddf70fcfb116c92fe4b008

    frozen semantics implementation:
    48a9c1438166eaf895104358b2d8cd8c9b043020

Any approval that does not explicitly bind the future package commit containing this Request and its Manifest is invalid.

## Frozen Prior Manifest

The compatible source verifier may read only:

    E:\科研\HyperGranular-RAG\docs\STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_MANIFEST.json

Its externally frozen identity is:

    bytes:
    24248

    SHA-256:
    B5953058270B4A8C715D38D5CF92CC65DCB7F90C6149EA1DC5B3E02C14B1A68E

The verifier must validate this file before JSON parsing. It may not read another project or official input path.

## Windows PowerShell 5.1-Compatible Source Verifier

The complete verifier is frozen in the Manifest by LF-joined source lines with no trailing newline:

    runtime executable:
    C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe

    PSEdition:
    Desktop

    version:
    5.1

    source lines:
    59

    source bytes:
    3512

    source SHA-256:
    1A30DC70AD0C01CDACBC3279F1CFD707EA4DAB457BE9C6C30A5C6D6495FA81BF

The verifier must reject any other runtime, including `pwsh.exe`. Its `Get-Sha256Hex` implementation uses `System.Security.Cryptography.SHA256`, `System.BitConverter`, and `.Replace('-', '')`, producing deterministic uppercase 64-character hexadecimal without `Convert.ToHexString()`.

The verifier may read only the frozen prior Manifest and must invoke no project helper. It must check:

| Frozen object | Lines | Bytes | SHA-256 |
|---|---:|---:|---|
| Embedded Python source | 46 | 2,284 | D0D3D6FC37AD0C2649A7A7F88EFA944C357033E3F0E956BE0E27C4374653D602 |
| PowerShell semantics wrapper | 122 | 7,890 | DFA95A904CE371F283B8DBA8BB4D98CC048F345F536C0E7D0D6DB8073DF9E16C |
| Expected wrapper stdout | n/a | 789 | EDBD4614B790256E314F4A8963128A5FB5A190FAC197437FB349D4C33C606135 |

It must also prove that the embedded Python block occurs exactly once in the PowerShell source and is byte-identical to the separately frozen Python source.

The verifier's exact success stdout is:

    {"status":"SOURCE_VERIFICATION_PASSED","powershell_lines":122,"powershell_bytes":7890,"python_lines":46,"python_bytes":2284,"embedded_python_byte_identical":true,"expected_stdout_bytes":789}

Its frozen identity is:

    stdout bytes:
    190

    stdout SHA-256:
    D05B3B2A147C51FB3A9FFFC3BEB802439E01AEFC34B708FE14C298978F2BFBB3

    stderr bytes:
    0

    exit code:
    0

## Unchanged Semantics Harness

This recovery does not modify the semantics wrapper, embedded Python, fixtures or expected semantics output. They remain frozen as:

    PowerShell wrapper:
    122 lines
    7890 bytes
    DFA95A904CE371F283B8DBA8BB4D98CC048F345F536C0E7D0D6DB8073DF9E16C

    embedded Python:
    46 lines
    2284 bytes
    D0D3D6FC37AD0C2649A7A7F88EFA944C357033E3F0E956BE0E27C4374653D602

    exact semantics stdout:
    789 bytes
    EDBD4614B790256E314F4A8963128A5FB5A190FAC197437FB349D4C33C606135

The real precommit validator also remains frozen and unexecuted at 195 lines, 15,966 bytes and SHA-256 `0F066387B8523B0EA387444076A1113913082D283C28C2DE3FFB33872D558249`.

## Frozen Recovery Execution Harness

The complete recovery harness is frozen in the corrected Manifest:

    source lines: 77
    source bytes: 6246
    source SHA-256: B34E7AE012AC0314AD44590603575194C8881CE58C17E6C8ED6568A5FA373048

The harness runs under Windows PowerShell 5.1 Desktop. It reads only the corrected governance Manifest and frozen prior Manifest. It reconstructs and verifies the accepted 59-line compatible verifier, starts it once in a child Windows PowerShell process, and requires exact 190-byte stdout, empty stderr and exit 0.

Only after that success does it reconstruct and verify the unchanged 122-line semantics wrapper, start it once in a second Windows PowerShell child and require the exact 789-byte output and all nine fixture/zero-access counters. The wrapper child may start exactly one Python process.

Both child processes use exactly:

    executable: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
    arguments prefix: "-NoLogo -NoProfile -NonInteractive -EncodedCommand "
    source transport: UTF-16LE then Base64
    UseShellExecute = false
    RedirectStandardInput = true
    RedirectStandardOutput = true
    RedirectStandardError = true
    CreateNoWindow = true
    StandardOutputEncoding = UTF-8
    StandardErrorEncoding = UTF-8

No temporary `.ps1` file is allowed. Standard input is closed immediately after process start. The harness itself emits the validated raw 789-byte wrapper stdout without reserialization or a trailing newline.

The exact derived child transports are also frozen:

| Child source | UTF-16LE bytes | Base64 chars | Base64 SHA-256 | Complete arguments SHA-256 |
|---|---:|---:|---|---|
| Recovery harness | 12,468 | 16,624 | D43444B6F7C4FFB5EF73548FB72F1A80C83FA663680197B99758BBF125EC567D | 19842E8DAB9CD94C4404DAC97989388B614462DDDC098A4590DA38D31F6B127B |
| Compatible verifier | 7,016 | 9,356 | A448D02B3E04A5D73F0E46F091496A2220A290A85C043538F7DB12739C91353F | DD57FC57342776A74FF4563D39BBD56AD64AFDB76B980202285ACECBB9E82026 |
| Semantics wrapper | 15,780 | 21,040 | 15E3C4B219109715BCAD0EE4510C1F19F219D2032BCC2AF08DC0BE3AD64FA888 | 0E1CCE9C1DE11C964356F4A508F330C169F255E3CCEA460D65417D3E923D42D5 |

## Frozen Bootstrap And Trust Root

The complete bootstrap is frozen as:

    source lines: 58
    source bytes: 3909
    source SHA-256: F8A452CEBEC06326E1D8BA4DEB4FC8915210F3FF9BBF53DA2D22B9675773C81D

The corrected package commit, Manifest and frozen bootstrap source are the explicit recursion terminus. The bootstrap is not subjected to another dynamically generated verifier. It uses the compatible SHA256 + BitConverter method to reconstruct and hash-check the recovery harness, then starts exactly one harness child with the same fixed ProcessStartInfo contract.

Bootstrap transport is independently frozen:

    bootstrap UTF-16LE source bytes: 7770
    EncodedCommand Base64 characters: 10360
    EncodedCommand ASCII SHA-256: 06CD60CDBD63E5AB9B017487285077C68581829D4309DC1AD6C964F22B9236C2
    complete arguments characters: 10411
    complete arguments ASCII SHA-256: 5EF7120B1005A027D408CF7DCAB525768376F2DAD213D91E69D73E1326D6F05D

The bootstrap separately captures harness stdout/stderr and exit code. After exact 789-byte success, it exclusive-creates the versioned machine evidence directly from the captured bytes using `FileMode.CreateNew`; this closes the raw-output-to-evidence identity chain. It then writes the same bytes to its own stdout.

## Requested Approval-Governance Commit

If approved, the first commit must be the direct child of the future package commit and change exactly:

    AGENTS.md
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_APPROVAL_DECISION.md

The decision must bind the package commit, verifier source line/byte/SHA values, verifier stdout byte/SHA values and all unchanged semantics fingerprints. The commit must be pushed and synchronized across local, origin and GitHub, with a clean worktree, before any verifier or wrapper invocation.

## Requested One-Time Sequence

Only the following future sequence is requested:

1. Create and push the exact two-path approval-governance direct child.
2. Confirm local/origin/GitHub equality, clean worktree and absence of all four old/new semantics evidence paths.
3. Reconstruct the 58-line frozen bootstrap and derive its UTF-16LE Base64 EncodedCommand; verify the registered source, Base64 and complete-arguments fingerprints without invoking it.
4. Launch the bootstrap exactly once through the registered no-profile ProcessStartInfo contract.
5. The bootstrap reconstructs and hash-checks the 77-line recovery harness, then launches exactly one harness PowerShell child.
6. The harness reconstructs and hash-checks the compatible verifier, launches exactly one verifier PowerShell child, and requires exit 0, stderr 0 and exact 190-byte stdout.
7. Only after verifier success, the harness reconstructs and launches the unchanged semantics wrapper in exactly one second PowerShell child.
8. Allow exactly one Python process and require PowerShell 7/7, raw JSON 2/2, total 9/9, passed 9, Python exit 0, stderr 0, exact 789-byte stdout and all zero-access counters.
9. Require empty stderr and exit 0 at verifier, wrapper, harness and bootstrap layers.
10. The bootstrap exclusive-creates the versioned machine evidence directly from its captured 789 raw bytes; after bootstrap success, exclusive-create the narrative audit.
11. Commit exactly those two paths as the direct child of approval governance, push, confirm three-way synchronization and clean worktree, then stop immediately.

One-time limits:

    approval-governance commits = 1
    bootstrap invocations = 1
    recovery-harness PowerShell processes = 1
    compatible source-verifier invocations = 1
    compatible-verifier PowerShell processes = 1
    semantics wrapper invocations = 1
    semantics-wrapper PowerShell processes = 1
    Python processes = 1
    evidence commits = 1
    complete synthetic runs = 0
    real precommit validator invocations = 0
    fresh three-path direct-child commits = 0
    formal preflight invocations = 0
    official input accesses = 0
    token uses = 0
    capture invocations = 0
    automatic retry = false

Any failure stops the sequence. No replacement conversion, runtime switch, wrapper edit or same-approval retry is allowed.

## Versioned Evidence Boundary

Only the following fresh paths are requested:

    results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_validator_semantics.json
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_VALIDATOR_SEMANTICS_AUDIT.md

The ungenerated 5G-B.1.1 paths must remain absent and must not be reused. The bootstrap writes the machine evidence itself from captured harness stdout through `FileMode.CreateNew`, so the committed file must be byte-identical to the unchanged 789-byte semantics-wrapper stdout. The narrative audit must record bootstrap, harness, verifier and wrapper fingerprints, exact process arguments, outputs, invocation counts and zero-access counters without raw fixture payloads or traceback content.

## Explicitly Not Requested

- execution during package assembly;
- reuse of the consumed 5G-B.1.1 approval or output paths;
- semantics wrapper, Python source, fixture, expected-output or real-validator modification;
- scripts, tests, results, historical failure or historical artifact changes;
- complete synthetic rebinding;
- real precommit validator or fresh three-path direct-child;
- execution-HEAD helper, formal preflight or typed/path helper official call;
- official input, token, capture, controller, verifier or evaluator/Gold;
- rankings, policy, source audit, 5C-B inventory, reservation or Stage3B;
- retry, reset, rebase, force-push or automatic continuation.

## Requested Completion State

    AMENDMENT_5G_B_1_1_1_VALIDATOR_SEMANTICS_VERIFIED_AWAITING_REVIEW
    HARD_FAILURE_12_AUDIT_ACCEPTED
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

    CORRECTED_AMENDMENT_5G_B_1_1_1_PACKAGE_AWAITING_APPROVAL
    SOURCE_VERIFICATION_RETRY_NOT_APPROVED
    VALIDATOR_SEMANTICS_WRAPPER_NOT_APPROVED
    OFFICIAL_EXECUTION_NOT_APPROVED
