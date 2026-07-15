# Stage4B-U1-D Pre-Gold Hard Failure 15

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Failure date: 2026-07-15
- Amendment 5G-B.1.1.1.1.1 package: d6d8a76abcb903b74307ed68f5ceabc42d8be8e3
- Approval governance: ee84988fa6ccf5e7f3524bc2c2a5f94065abf918
- Failure status: AMENDMENT_5G_B_1_1_1_1_1_RAW_STREAM_DIAGNOSTIC_STOPPED_HARD_FAILURE_15
- Failure boundary: DIAGNOSTIC_LAUNCHER_STDERR_GATE
- Diagnostic launcher processes: 1
- Original pre-verifier processes: 1
- Automatic retries: 0
- Other project conversations, thread tools, and global memory used: No

## Approval-Governance Gate

The package-bound approval was recorded in the exact two-path approval-governance commit and pushed before any launcher reconstruction:

    approval governance:
    ee84988fa6ccf5e7f3524bc2c2a5f94065abf918

    direct parent:
    d6d8a76abcb903b74307ed68f5ceabc42d8be8e3

    changed paths:
    AGENTS.md
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_1_APPROVAL_DECISION.md

The local HEAD and upstream tracking ref both equaled the approval-governance commit. The worktree was clean and all four proposed diagnostic paths and all four semantics paths were absent before reconstruction.

## Single Static Reconstruction

The host reconstructed the approved launcher exactly once from the package Manifest with LF separators and no trailing newline. Every frozen pre-start gate passed:

    package Manifest bytes: 23126
    package Manifest SHA-256: F745AB5C5B07B7DD836A5039DD726625A9D855DEDFF7A2E8CC9F1861178C3A36

    corrected execution Manifest bytes: 31197
    corrected execution Manifest SHA-256: ABA9C4E453BC3DE852B8AF9433E3E0BB837A7E2D0B4F5C313E00464B7B368919

    launcher source lines: 161
    launcher source UTF-8 bytes: 9684
    launcher source SHA-256: 4FA9DABF8701F67554F6D0D100EFD72DF78477F80F600057F5C26A9886471DD6
    launcher static parse errors: 0

    launcher UTF-16LE bytes: 19288
    launcher Base64 characters: 25720
    launcher Base64 SHA-256: F8095A51A5A4C550383112D13A335EB44B9B06E7F8655D5DA6441D201A1C97D5
    launcher complete arguments characters: 25771
    launcher complete arguments SHA-256: 86E326DBB39ED099A5AA4BD8CA46002656D2766768C731A88F15C784F88946C1

    expected launcher stdout bytes: 122
    expected launcher stdout SHA-256: 4B7803B9C64F467F42356292B015BE1866156F2F22111E6393B913B1CEF8B80C

No source, transport, path or governance mismatch occurred before the one authorized launcher process start.

## Failed Launcher Output Gate

The host started exactly one approved Windows PowerShell launcher. The launcher started exactly one unchanged original pre verifier, concurrently drained its raw stdout and stderr, and created the three machine paths before emitting its fixed output.

The outer launcher process returned:

    launcher exit code: 0
    launcher stdout bytes: 122
    launcher stdout SHA-256: 4B7803B9C64F467F42356292B015BE1866156F2F22111E6393B913B1CEF8B80C
    launcher stdout exact frozen bytes: true
    launcher stderr bytes: 382
    launcher stderr SHA-256: 4F2B6B3ED9201CA459DB2DD042E0A137C4E58BFE8E15A068E45AD8535FA5B1EF

The exit and stdout checks matched the frozen contract, but the launcher stderr-empty contract required zero bytes. The actual 382-byte stderr therefore triggered the hard-failure gate. The ordered authorization was consumed at this point.

No narrative success audit was created. No four-path success evidence commit was attempted. The launcher, original pre verifier and any internal Git child were not rerun, replaced or repaired.

The outer launcher stderr payload was not decoded or interpreted. Its byte count and SHA-256 are recorded only as gate evidence. Root cause is not established, and the launcher output cannot be accepted as an exact launcher success while its stderr contract is false.

## Partial-Path Preservation Audit

The approval required every created path to remain byte-for-byte unchanged after any failure. Read-only post-failure fingerprinting found:

| Proposed path | Exists | Bytes | SHA-256 |
|---|---:|---:|---|
| `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stdout.bin` | yes | 122 | `BCDF0010147E5952AD0372ADF39EDA0A18D349B02107C340DEF05BAFE18C0F09` |
| `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stderr.bin` | yes | 382 | `4F2B6B3ED9201CA459DB2DD042E0A137C4E58BFE8E15A068E45AD8535FA5B1EF` |
| `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_diagnostic.json` | yes | 944 | `F4022C8B4DF507D9A63085698B846358FF6D33F2A67B55B0C54EB871E8EB101B` |
| `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_14_PRE_SYNC_DIAGNOSTIC_AUDIT.md` | no | n/a | n/a |

The three existing machine files were created by the frozen launcher with `FileMode.CreateNew`. This checkpoint does not overwrite, normalize, decode or reserialize them.

The value-free metadata records:

    diagnostic status: RAW_STREAMS_PRESERVED_AWAITING_INDEPENDENT_REVIEW
    original pre-verifier processes: 1
    original pre-verifier exit code: 0
    stdout bytes / SHA match preserved file: true
    stdout strict UTF-8 valid: true
    stdout exact frozen 122-byte success: true
    stderr bytes / SHA match preserved file: true
    stderr strict UTF-8 valid: false
    stderr empty: false
    internal Git-child count: null
    internal Git-child count status: UNCONFIRMED_PENDING_INDEPENDENT_REVIEW
    accepted three-way synchronization successes: 0
    bootstrap / semantics / post-evidence / synthetic / official operations: 0
    automatic retries: 0

These metadata facts do not establish three-way synchronization, internal Git-child completion or a recovery result.

## Locked-Path Audit

All four semantics evidence paths remained absent after failure:

    results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_validator_semantics.json
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_VALIDATOR_SEMANTICS_AUDIT.md
    results/stage4b_u1_d_pregold_amendment_5g_b_1_1_validator_semantics.json
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_VALIDATOR_SEMANTICS_AUDIT.md

No bootstrap, harness, compatible verifier, wrapper, Python, semantics process, post-evidence verifier, synthetic suite, real validator, formal preflight, official input, authorization token, capture, controller, verifier, evaluator/Gold, reservation or Stage3B action occurred.

## One-Time Counts

    approval-governance commits: 1
    approval-governance pushes: 1
    launcher static reconstructions: 1
    launcher PowerShell processes: 1
    original pre-verifier PowerShell processes: 1
    original pre-verifier internal Git children: UNCONFIRMED, authorized maximum 5
    raw stdout CreateNew: 1
    raw stderr CreateNew: 1
    value-free metadata CreateNew: 1
    narrative audit CreateNew: 0
    accepted launcher exact successes: 0
    accepted three-way synchronization successes: 0
    semantics processes: 0
    semantics evidence creations: 0
    post-evidence verifier processes: 0
    complete synthetic runs: 0
    real validator invocations: 0
    formal preflight invocations: 0
    official input accesses: 0
    authorization token uses: 0
    official captures: 0
    automatic retries: 0

## Checkpoint Commit Preflight

The first staged `git diff --cached --check` found one extra blank line at the end of this new audit file and stopped before commit creation or push. The Markdown-only trailing blank line was removed, the exact path set was restaged, and the preflight was repeated. This did not modify any preserved machine file and did not rerun the launcher, original pre verifier or any downstream process.

## Stop Boundary

Amendment 5G-B.1.1.1.1.1 authorization is consumed and stopped at the diagnostic launcher stderr gate. The preserved raw streams and metadata are failure evidence only; they are not a completed four-path diagnostic evidence set and do not validate three-way synchronization.

Independent review is required before any further interpretation, launcher change, diagnostic, retry or recovery proposal. Until a new package-bound approval:

    AMENDMENT_5G_B_1_1_1_1_1_RAW_STREAM_DIAGNOSTIC_STOPPED_HARD_FAILURE_15
    RAW_STREAM_MACHINE_EVIDENCE_PRESERVED_UNDER_FAILURE
    DIAGNOSTIC_NARRATIVE_NOT_CREATED
    PRE_EXECUTION_SYNCHRONIZATION_NOT_VERIFIED
    ROOT_CAUSE_NOT_ESTABLISHED

    DIAGNOSTIC_RETRY_NOT_APPROVED
    LAUNCHER_RECONSTRUCTION_NOT_APPROVED
    LAUNCHER_REPAIR_OR_REPLACEMENT_NOT_APPROVED
    BOOTSTRAP_NOT_APPROVED
    VALIDATOR_SEMANTICS_NOT_APPROVED
    SUCCESS_EVIDENCE_COMMIT_NOT_APPROVED
    POST_EVIDENCE_SYNC_NOT_APPROVED
    SYNTHETIC_NOT_APPROVED
    REAL_VALIDATOR_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_INPUT_ACCESS_NOT_APPROVED
    AUTHORIZATION_TOKEN_USE_NOT_APPROVED
    OFFICIAL_CAPTURE_NOT_APPROVED
    CONTROLLER_RERUN_NOT_APPROVED
    VERIFIER_NOT_APPROVED
    GOLD_NOT_APPROVED
