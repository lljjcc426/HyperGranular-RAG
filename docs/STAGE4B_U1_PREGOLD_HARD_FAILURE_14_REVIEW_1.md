# Stage4B-U1-D Pre-Gold Hard Failure 14 Review 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review date: 2026-07-15
- Reviewed checkpoint: e12b0961492897d1940cf0cf2ce45fa45abb99b8
- Decision: ACCEPT_HARD_FAILURE_14_AUDIT
- Recovery: RETURN_FOR_AMENDMENT_5G_B_1_1_1_1_1_RAW_STREAM_DIAGNOSTIC_PACKAGE_ONLY
- Diagnostic execution authorized: No
- Official execution authorized: No
- Other project conversations, thread tools and global memory used: No

## Bound Commits

    corrected package:
    3d37c8a65888c2093403a71375bfa94dd51bac2e

    approval governance:
    ba50d75e41f6046c2b0380462c3d7480542e15c4

    Hard Failure 14 checkpoint:
    e12b0961492897d1940cf0cf2ce45fa45abb99b8

The commit order is accepted as corrected package, approval governance and Hard Failure 14 checkpoint. The approval-governance commit is the direct child of the corrected package and changes exactly `AGENTS.md` and the corrected approval decision.

## Accepted Failure Boundary

The audit correctly records that the 74-line pre-execution verifier source and its complete transport passed static reconstruction before process start. The frozen identities were:

    source lines: 74
    source UTF-8 bytes: 4114
    source SHA-256: 4A5A4BBE08661D588673C4B4A1A7ABAB88FEB2999699658CBC91E8081266EB66
    UTF-16LE bytes: 8188
    Base64 characters: 10920
    Base64 SHA-256: 3A70D85BDB66451877CD7000C1B7278D84E9A8952D61330D3CC8973956660F5D
    complete arguments characters: 10971
    complete arguments SHA-256: 1ED8A00D773578DD5EBCE903CE8FF4E2413E18D9FA7E82DB4D2268A0CE62C4C5

Exactly one original pre-verifier PowerShell process was started. Its exit code was zero, but the next outer gate found non-empty stderr. Stdout validation was not reached. The raw stdout and stderr payloads were not persisted and are now unrecoverable.

The only accepted runtime statement is:

    pre verifier processes: 1
    pre verifier exit code: 0
    stderr: non-empty
    internal Git child count: UNCONFIRMED
    accepted exact 122-byte successes: 0
    pre-execution synchronization: NOT_VERIFIED

The root cause is not established. Exit zero must not be upgraded to a claim of five completed Git children, exact success stdout or verified three-way synchronization.

## Accepted Zero Boundary

The following counts remain zero:

    static bootstrap reconstruction: 0
    bootstrap: 0
    recovery harness: 0
    compatible verifier: 0
    semantics wrapper: 0
    Python: 0
    machine evidence: 0
    narrative evidence: 0
    evidence commit: 0
    post verifier: 0
    official access/token/capture: 0
    automatic retries: 0

All four old and target semantics-evidence paths remain absent. No script, test, dataset, cache, official artifact, historical evidence or prior failure record was modified or deleted.

## Recovery Decision

The corrected 5G-B.1.1.1.1 approval is consumed and cannot be reused. This review permits only assembly of a new governance package for one future controlled raw-stream diagnostic. It does not authorize the diagnostic launcher, another original verifier process, bootstrap, semantics, evidence creation or any official operation.

The future package must preserve the 74-line pre verifier, 107-line post verifier, 58-line bootstrap, 77-line harness, 59-line compatible verifier, 122-line wrapper, 46-line embedded Python and 195-line real validator byte-for-byte.

The package must freeze a launcher that concurrently drains `StandardOutput.BaseStream` and `StandardError.BaseStream`, saves both raw byte streams with `FileMode.CreateNew` before interpretation or comparison, and then writes value-free metadata containing process exit code, byte counts, SHA-256 values, strict UTF-8 validity, exact 122-byte stdout equality and stderr emptiness.

## Current State

    HARD_FAILURE_14_AUDIT_ACCEPTED
    HARD_FAILURE_14_CHECKPOINT_FROZEN
    ROOT_CAUSE_NOT_ESTABLISHED
    PRE_EXECUTION_SYNCHRONIZATION_NOT_VERIFIED

    RETURN_FOR_AMENDMENT_5G_B_1_1_1_1_1_RAW_STREAM_DIAGNOSTIC_PACKAGE

    CURRENT_APPROVAL_CONSUMED
    PRE_SYNC_RETRY_NOT_APPROVED
    RAW_STREAM_DIAGNOSTIC_NOT_APPROVED
    BOOTSTRAP_NOT_APPROVED
    SEMANTICS_SEQUENCE_NOT_APPROVED
    EVIDENCE_CREATION_NOT_APPROVED
    POST_EVIDENCE_SYNC_NOT_APPROVED
    OFFICIAL_EXECUTION_NOT_APPROVED
