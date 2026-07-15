# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1.1 Approval Request

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Request date: 2026-07-15
- Requested decision: APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_1_FROZEN_PRE_SYNC_RAW_STREAM_DIAGNOSTIC_ONLY
- Current checkpoint: e12b0961492897d1940cf0cf2ce45fa45abb99b8
- Package execution authority: NONE UNTIL A NEW APPROVAL BINDS THE FUTURE PACKAGE COMMIT
- Official execution: NOT_REQUESTED
- Other project conversations, thread tools and global memory used: No

## Review Basis

Hard Failure 14 Review 1 accepts the failure audit, approval-governance commit, static pre-verifier reconstruction and fail-closed stop. One original pre-verifier process was consumed and exited zero, but the outer empty-stderr gate failed before stdout validation. The raw streams were not persisted, the payloads are unrecoverable, the internal Git-child count remains unconfirmed and the root cause is not established.

The consumed corrected 5G-B.1.1.1.1 approval cannot be reused. This package requests only one future raw-stream diagnostic to preserve the missing evidence before any interpretation. It does not request synchronization acceptance or recovery.

## Bound Commits And Files

    corrected 5G-B.1.1.1.1 package:
    3d37c8a65888c2093403a71375bfa94dd51bac2e

    corrected approval governance:
    ba50d75e41f6046c2b0380462c3d7480542e15c4

    Hard Failure 14 checkpoint:
    e12b0961492897d1940cf0cf2ce45fa45abb99b8

    corrected 5G-B.1.1.1.1 Manifest:
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_MANIFEST.json
    31197 bytes
    ABA9C4E453BC3DE852B8AF9433E3E0BB837A7E2D0B4F5C313E00464B7B368919

    Hard Failure 14 audit:
    docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_14.md
    7012 bytes
    68151184F1D80EEBE2F0E92B01DD4526D36E7E705D3A50B3788D6184F361B23B

Any approval that does not explicitly bind the future package commit containing this Request and its Manifest is invalid.

## Unchanged Frozen Sources

The diagnostic must not modify any existing executable source:

| Frozen object | Lines | Bytes | SHA-256 |
|---|---:|---:|---|
| Pre-execution verifier | 74 | 4,114 | `4A5A4BBE08661D588673C4B4A1A7ABAB88FEB2999699658CBC91E8081266EB66` |
| Post-evidence verifier | 107 | 7,130 | `8877E18F75A94EE6DA326B09C3791E6641B6B9B32D42744BA23E033A20735A67` |
| Bootstrap | 58 | 3,909 | `F8A452CEBEC06326E1D8BA4DEB4FC8915210F3FF9BBF53DA2D22B9675773C81D` |
| Recovery harness | 77 | 6,246 | `B34E7AE012AC0314AD44590603575194C8881CE58C17E6C8ED6568A5FA373048` |
| Compatible verifier | 59 | 3,512 | `1A30DC70AD0C01CDACBC3279F1CFD707EA4DAB457BE9C6C30A5C6D6495FA81BF` |
| Semantics wrapper | 122 | 7,890 | `DFA95A904CE371F283B8DBA8BB4D98CC048F345F536C0E7D0D6DB8073DF9E16C` |
| Embedded Python | 46 | 2,284 | `D0D3D6FC37AD0C2649A7A7F88EFA944C357033E3F0E956BE0E27C4374653D602` |
| Real precommit validator | 195 | 15,966 | `0F066387B8523B0EA387444076A1113913082D283C28C2DE3FFB33872D558249` |

The original pre-verifier child must retain the exact Windows PowerShell 5.1 executable, working directory, 74-line source, UTF-16LE EncodedCommand and 10,971-character complete arguments whose SHA-256 is `1ED8A00D773578DD5EBCE903CE8FF4E2413E18D9FA7E82DB4D2268A0CE62C4C5`.

## Frozen Diagnostic Launcher

The complete launcher source is frozen in the machine-readable Manifest. It must run under Windows PowerShell 5.1 Desktop through `-NoLogo -NoProfile -NonInteractive -EncodedCommand <UTF-16LE Base64>` with fixed redirected/no-window ProcessStartInfo fields.

Its package-assembly fingerprints are:

    source lines: 161
    source UTF-8 bytes: 9684
    source SHA-256: 4FA9DABF8701F67554F6D0D100EFD72DF78477F80F600057F5C26A9886471DD6
    UTF-16LE source bytes: 19288
    Base64 characters: 25720
    Base64 SHA-256: F8095A51A5A4C550383112D13A335EB44B9B06E7F8655D5DA6441D201A1C97D5
    complete arguments characters: 25771
    complete arguments SHA-256: 86E326DBB39ED099A5AA4BD8CA46002656D2766768C731A88F15C784F88946C1
    fixed launcher success stdout bytes: 122
    fixed launcher success stdout SHA-256: 4B7803B9C64F467F42356292B015BE1866156F2F22111E6393B913B1CEF8B80C

Static Windows PowerShell parsing reported zero syntax errors. Neither the launcher nor the original pre verifier was invoked during package assembly.

Before process start, the launcher must:

1. require all four new diagnostic paths and all four old/target semantics-evidence paths to be absent;
2. verify the corrected Manifest as exactly 31,197 bytes and SHA-256 `ABA9C4E4...8919`;
3. reconstruct the original 74-line verifier from that Manifest;
4. verify its source, UTF-16LE/Base64 transport, complete arguments and fixed 122-byte success stdout fingerprints;
5. start no process if any gate fails.

The launcher must start exactly one original pre-verifier PowerShell process. It must immediately close child stdin and concurrently drain:

    StandardOutput.BaseStream
    StandardError.BaseStream

The launcher must not decode, normalize, classify, compare or throw on either captured payload before persisting both raw byte arrays.

## Persistence Order And Paths

The launcher must use `FileMode.CreateNew` in this order:

1. `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stdout.bin`
2. `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stderr.bin`
3. `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_diagnostic.json`

Only after both raw streams are written may it compute and persist metadata. The metadata must record, without embedding decoded payloads:

- original child process exit code;
- stdout and stderr byte counts and SHA-256 values;
- strict UTF-8 decoding success/failure for each stream;
- whether raw stdout exactly equals the frozen 122-byte success payload;
- whether raw stderr is empty;
- original verifier process count as one;
- internal Git-child count as `null` and `UNCONFIRMED_PENDING_INDEPENDENT_REVIEW`;
- accepted synchronization successes as zero;
- all downstream process and official-operation counts as zero.

After launcher success, the host may exclusive-create:

    docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_14_PRE_SYNC_DIAGNOSTIC_AUDIT.md

The narrative must report only the raw fingerprints and execution boundary. It must not interpret payload bytes beyond properties already frozen in metadata or claim synchronization success.

## Requested Approval-Governance Commit

If approved, the first future commit must be the direct child of the future package commit and change exactly:

    AGENTS.md
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_1_APPROVAL_DECISION.md

It must be pushed before static launcher reconstruction or any diagnostic process. The worktree must then be clean and all eight evidence/diagnostic paths absent.

## Requested One-Time Sequence

1. Create and push the exact-two-path approval-governance direct child.
2. Reconstruct and fingerprint the frozen launcher and its complete EncodedCommand without executing it.
3. Reconfirm the corrected Manifest identity and absence of all eight paths.
4. Launch exactly one diagnostic-launcher PowerShell process.
5. Let it launch exactly one unchanged original pre-verifier PowerShell process and up to five original Git children.
6. Concurrently drain both child raw streams and persist stdout then stderr before interpretation or comparison.
7. Persist value-free metadata after both raw files exist.
8. Require the launcher's fixed success stdout, empty launcher stderr and exit zero.
9. Verify the three machine paths, unchanged absence of all four semantics paths and no downstream action.
10. Exclusive-create the narrative diagnostic audit.
11. Commit exactly the four diagnostic evidence paths as the direct child of approval governance, push and stop immediately.

Any fingerprint, path, process-start, stream-copy, persistence, launcher-output, changed-path, commit or push failure consumes the ordered authorization. Repair, replacement, fallback or retry is forbidden.

## Requested Counts

    approval-governance commits: 1
    diagnostic-launcher PowerShell processes: 1
    original pre-verifier PowerShell processes: 1
    original pre-verifier Git children: maximum 5; actual count only after independent proof
    raw stdout CreateNew: 1
    raw stderr CreateNew: 1
    metadata CreateNew: 1
    narrative audit CreateNew: 1
    diagnostic evidence commits: 1

    bootstrap: 0
    recovery harness: 0
    compatible verifier: 0
    semantics wrapper: 0
    Python: 0
    semantics evidence: 0
    post-evidence verifier: 0
    synthetic: 0
    formal preflight: 0
    official operations: 0
    automatic retry: 0

Diagnostic completion means only that one process ran and both raw streams, the exit code and their fingerprints were preserved. It is not a three-way synchronization success.

## Exact Diagnostic Evidence Commit

The future evidence commit must be the direct child of approval governance and change exactly:

    docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_14_PRE_SYNC_DIAGNOSTIC_AUDIT.md
    results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_diagnostic.json
    results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stderr.bin
    results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stdout.bin

It must not update `AGENTS.md`, README, ROADMAP, REPRODUCIBILITY or any implementation path. Push must be followed by immediate stop for independent review.

## Explicitly Not Requested

- reuse of the consumed corrected 5G-B.1.1.1.1 approval;
- execution during package assembly;
- modification of the original pre/post verifier or any semantics-chain source;
- acceptance of non-empty stderr or weakening of any prior gate;
- declaration that three-way synchronization passed;
- bootstrap, harness, compatible verifier, semantics wrapper or Python;
- semantics evidence or post-evidence synchronization;
- synthetic rebinding, real validator or fresh three-path direct-child;
- formal preflight, official input, token, capture, controller, verifier or evaluator/Gold;
- rankings, policy, source audit, 5C-B inventory, reservation or Stage3B;
- retry, command replacement, runtime switching, reset, rebase or force-push.

## Current Stop State

This Request and Manifest are governance materials only. Until an independent approval explicitly binds their future package commit:

    AMENDMENT_5G_B_1_1_1_1_1_RAW_STREAM_DIAGNOSTIC_PACKAGE_AWAITING_APPROVAL
    HARD_FAILURE_14_AUDIT_ACCEPTED
    ROOT_CAUSE_NOT_ESTABLISHED
    RAW_STREAM_DIAGNOSTIC_NOT_APPROVED
    PRE_SYNC_RETRY_NOT_APPROVED
    BOOTSTRAP_NOT_APPROVED
    SEMANTICS_SEQUENCE_NOT_APPROVED
    POST_EVIDENCE_SYNC_NOT_APPROVED
    OFFICIAL_EXECUTION_NOT_APPROVED
