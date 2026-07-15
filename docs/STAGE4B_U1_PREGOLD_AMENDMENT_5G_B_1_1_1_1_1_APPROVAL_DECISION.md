# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1.1 Approval Decision

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Approval date: 2026-07-15
- Decision: APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_1_FROZEN_PRE_SYNC_RAW_STREAM_DIAGNOSTIC_ONLY
- Package: d6d8a76abcb903b74307ed68f5ceabc42d8be8e3
- Hard Failure 14 checkpoint: e12b0961492897d1940cf0cf2ce45fa45abb99b8
- Three-way synchronization acceptance: NOT_APPROVED
- Bootstrap and semantics: NOT_APPROVED
- Official execution: NOT_APPROVED
- Other project conversations, thread tools and global memory used: No

## Frozen Governance Trust Root

This approval strictly binds:

    package:
    d6d8a76abcb903b74307ed68f5ceabc42d8be8e3

    Hard Failure 14 checkpoint:
    e12b0961492897d1940cf0cf2ce45fa45abb99b8

    package Manifest:
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_1_MANIFEST.json
    23126 bytes
    F745AB5C5B07B7DD836A5039DD726625A9D855DEDFF7A2E8CC9F1861178C3A36

    corrected execution Manifest:
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_MANIFEST.json
    31197 bytes
    ABA9C4E453BC3DE852B8AF9433E3E0BB837A7E2D0B4F5C313E00464B7B368919

The package commit, package Manifest and frozen launcher source are the complete governance trust root. No dynamic launcher verifier or alternate executable source may be introduced.

## Approval-Governance Commit

The first commit must be the direct child of `d6d8a76abcb903b74307ed68f5ceabc42d8be8e3` and change exactly:

    AGENTS.md
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_1_APPROVAL_DECISION.md

It must be pushed before static launcher reconstruction. After push, the worktree must be clean and all four diagnostic paths plus all four semantics-evidence paths must be absent.

## Unchanged Original Pre Verifier

The original child remains frozen as:

    runtime:
    C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
    Windows PowerShell 5.1 Desktop

    working directory:
    E:\科研\HyperGranular-RAG

    source lines: 74
    source UTF-8 bytes: 4114
    source SHA-256: 4A5A4BBE08661D588673C4B4A1A7ABAB88FEB2999699658CBC91E8081266EB66
    UTF-16LE bytes: 8188
    Base64 characters: 10920
    Base64 SHA-256: 3A70D85BDB66451877CD7000C1B7278D84E9A8952D61330D3CC8973956660F5D
    complete arguments characters: 10971
    complete arguments SHA-256: 1ED8A00D773578DD5EBCE903CE8FF4E2413E18D9FA7E82DB4D2268A0CE62C4C5
    fixed success stdout bytes: 122
    fixed success stdout SHA-256: BCDF0010147E5952AD0372ADF39EDA0A18D349B02107C340DEF05BAFE18C0F09

The 74-line source, executable, working directory, EncodedCommand arguments and ProcessStartInfo fields must remain unchanged. At most five original Git children are allowed. Their actual count must remain unconfirmed unless the diagnostic evidence independently proves it.

## Frozen Raw-Stream Diagnostic Launcher

The launcher is frozen as:

    source lines: 161
    source UTF-8 bytes: 9684
    source SHA-256: 4FA9DABF8701F67554F6D0D100EFD72DF78477F80F600057F5C26A9886471DD6
    UTF-16LE bytes: 19288
    Base64 characters: 25720
    Base64 SHA-256: F8095A51A5A4C550383112D13A335EB44B9B06E7F8655D5DA6441D201A1C97D5
    complete arguments characters: 25771
    complete arguments SHA-256: 86E326DBB39ED099A5AA4BD8CA46002656D2766768C731A88F15C784F88946C1

Its fixed success stdout is:

    {"status":"RAW_STREAM_DIAGNOSTIC_PRESERVED","raw_streams_persisted":true,"metadata_persisted":true,"downstream_actions":0}

Its identity is:

    stdout bytes: 122
    stdout SHA-256: 4B7803B9C64F467F42356292B015BE1866156F2F22111E6393B913B1CEF8B80C
    stderr bytes: 0
    exit code: 0

One static reconstruction of the launcher source and complete EncodedCommand is authorized after approval-governance push. Exactly one launcher process is authorized if and only if all frozen fingerprints pass.

## Raw-Stream Capture And Persistence

The launcher must start exactly one unchanged original pre-verifier process, close child stdin immediately and concurrently drain:

    StandardOutput.BaseStream
    StandardError.BaseStream

Both `CopyToAsync` tasks and the child process must complete before the byte arrays are used. The launcher must then use `FileMode.CreateNew` in this order:

1. `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stdout.bin`
2. `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stderr.bin`
3. `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_diagnostic.json`

Raw stdout and raw stderr must both be written before any SHA, strict UTF-8, exact-success or stderr-empty calculation. The metadata must not embed a decoded or reserialized payload. It may record only the approved paths, exit code, byte counts, SHA-256 values, strict UTF-8 validity, exact 122-byte stdout equality, stderr emptiness, one original verifier process, null/unconfirmed internal Git-child count, zero accepted synchronization successes and zero downstream counts.

## Host Narrative And Evidence Commit

Only after exact launcher success may the host exclusive-create:

    docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_14_PRE_SYNC_DIAGNOSTIC_AUDIT.md

The narrative must preserve the metadata boundary and must not upgrade diagnostic completion to synchronization acceptance.

The diagnostic evidence commit must be the direct child of this approval-governance commit and change exactly:

    docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_14_PRE_SYNC_DIAGNOSTIC_AUDIT.md
    results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_diagnostic.json
    results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stderr.bin
    results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stdout.bin

It must not change `AGENTS.md`, README, ROADMAP, REPRODUCIBILITY or any implementation path. It must be pushed and followed by immediate stop for independent raw-evidence review.

## Unique Authorized Sequence

1. Create and push the exact-two-path approval-governance direct child.
2. Confirm clean worktree and absence of all eight diagnostic/semantics paths.
3. Statically reconstruct the frozen launcher and complete EncodedCommand exactly once.
4. Require all package-bound launcher fingerprints to pass.
5. Start exactly one diagnostic-launcher PowerShell process.
6. Let it start exactly one unchanged original pre-verifier PowerShell process and at most five unchanged Git children.
7. Concurrently drain both child raw streams.
8. CreateNew raw stdout, then raw stderr, then value-free metadata.
9. Require launcher exit zero, empty stderr and exact 122-byte fixed success stdout.
10. Verify all three machine paths, continued absence of all four semantics paths and zero downstream action.
11. Exclusive-create the narrative audit.
12. Commit exactly the four diagnostic evidence paths as the direct child of approval governance.
13. Push and stop immediately.

Any fingerprint, path, start, stream-copy, persistence, launcher-output, validation, commit or push failure consumes the ordered authorization. No cleanup, overwrite, repair, replacement, fallback or retry is allowed.

## Failure Preservation Rule

If a failure occurs after any raw or metadata path is created, every created path must remain byte-for-byte unchanged. The failure audit must record for each proposed path whether it exists and, if present, its byte count and SHA-256. Partial files must not be deleted or overwritten.

## Authorized Counts

    approval-governance commits: 1
    static launcher reconstructions: 1
    diagnostic-launcher PowerShell processes: 1
    unchanged original pre-verifier PowerShell processes: 1
    original Git children: maximum 5
    raw stdout CreateNew: 1
    raw stderr CreateNew: 1
    metadata CreateNew: 1
    narrative CreateNew: 1
    diagnostic evidence commits: 1

    bootstrap: 0
    recovery harness: 0
    compatible verifier: 0
    semantics wrapper: 0
    Python: 0
    semantics evidence: 0
    post-evidence sync: 0
    synthetic rebinding: 0
    real precommit validator: 0
    formal preflight: 0
    official input/token/capture: 0
    controller/verifier/Gold: 0
    automatic retries: 0

## Explicitly Not Authorized

- three-way synchronization acceptance or pre-sync recovery;
- reuse of the consumed corrected 5G-B.1.1.1.1 approval;
- modification of the pre/post verifier or any bootstrap/semantics source;
- weakening the empty-stderr or exact-stdout contracts;
- bootstrap, harness, compatible verifier, semantics wrapper or Python;
- semantics evidence or post-evidence synchronization;
- synthetic rebinding, real precommit validator or fresh three-path direct-child;
- formal preflight, official input, token, capture, controller, verifier or evaluator/Gold;
- rankings, policy, source audit, 5C-B inventory, reservation or Stage3B;
- retry, command replacement, runtime switch, reset, rebase or force-push.

## Approved Completion State

Diagnostic completion means only that one process ran and the raw streams, exit code and fingerprints were preserved. Even if the child exit is zero, stdout is exact and stderr is empty, the only completion state is:

    AMENDMENT_5G_B_1_1_1_1_1_RAW_STREAM_DIAGNOSTIC_PRESERVED_AWAITING_REVIEW
    HARD_FAILURE_14_AUDIT_ACCEPTED
    ROOT_CAUSE_NOT_ESTABLISHED
    PRE_EXECUTION_SYNCHRONIZATION_NOT_VERIFIED

    BOOTSTRAP_NOT_APPROVED
    SEMANTICS_SEQUENCE_NOT_APPROVED
    SEMANTICS_EVIDENCE_NOT_APPROVED
    POST_EVIDENCE_SYNC_NOT_APPROVED
    FRESH_SYNTHETIC_REBINDING_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_INPUT_ACCESS_NOT_APPROVED
    AUTHORIZATION_TOKEN_USE_NOT_APPROVED
    OFFICIAL_CAPTURE_NOT_APPROVED
    CONTROLLER_RERUN_NOT_APPROVED
    VERIFIER_NOT_APPROVED
    GOLD_NOT_APPROVED
