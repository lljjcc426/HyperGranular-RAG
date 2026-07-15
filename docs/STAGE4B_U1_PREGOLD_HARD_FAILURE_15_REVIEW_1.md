# Stage4B-U1-D Pre-Gold Hard Failure 15 Review 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review date: 2026-07-15
- Reviewed checkpoint: 95f68e7b2afdf6ed46c4eebe604d13744b26760a
- Decision: ACCEPT_HARD_FAILURE_15_AUDIT
- Preserved evidence: ACCEPT_PRESERVED_RAW_MACHINE_EVIDENCE
- Stop boundary: CONFIRM_FAIL_CLOSED_STOP_BOUNDARY
- Recovery: RETURN_FOR_AMENDMENT_5G_B_1_1_1_1_2_FULL_TRANSPORT_RECOVERY_PACKAGE_ONLY
- Recovery execution authorized: No
- Official execution authorized: No
- Other project conversations, thread tools and global memory used: No

## Bound Commits

    diagnostic package:
    d6d8a76abcb903b74307ed68f5ceabc42d8be8e3

    approval governance:
    ee84988fa6ccf5e7f3524bc2c2a5f94065abf918

    Hard Failure 15 checkpoint:
    95f68e7b2afdf6ed46c4eebe604d13744b26760a

The chain is accepted. Approval governance is the exact two-path direct child of the diagnostic package. Hard Failure 15 is its direct child and preserves the three machine files, creates the failure audit and updates governance without creating the approved success narrative.

The Markdown trailing-blank-line correction occurred before checkpoint commit creation. It changed no machine evidence and did not rerun any process.

## Accepted Machine Evidence

| Path | Bytes | SHA-256 |
|---|---:|---|
| `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stdout.bin` | 122 | `BCDF0010147E5952AD0372ADF39EDA0A18D349B02107C340DEF05BAFE18C0F09` |
| `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stderr.bin` | 382 | `4F2B6B3ED9201CA459DB2DD042E0A137C4E58BFE8E15A068E45AD8535FA5B1EF` |
| `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_diagnostic.json` | 944 | `F4022C8B4DF507D9A63085698B846358FF6D33F2A67B55B0C54EB871E8EB101B` |

The metadata and failure audit agree on byte counts, SHA-256 values, exit code, strict UTF-8 status, stdout equality, stderr non-emptiness and zero downstream counts. These three files are frozen historical evidence and must not be deleted, renamed, overwritten or repurposed as future success evidence.

The success narrative remains absent. All four old and target semantics paths remained absent at verification.

## Established Root Cause

The preserved 382-byte stderr is a Windows PowerShell CLIXML progress record containing the CP936/GBK message:

    正在准备首次使用模块。

Its frozen identity is:

    bytes: 382
    SHA-256: 4F2B6B3ED9201CA459DB2DD042E0A137C4E58BFE8E15A068E45AD8535FA5B1EF
    strict UTF-8 valid: false
    Base64 characters: 512
    Base64 SHA-256: 1A3D87C52A5EB3036EE762D586A05D21A3080106A0E38AE3B75DC0C44BC8700B

    Base64:
    IzwgQ0xJWE1MDQo8T2JqcyBWZXJzaW9uPSIxLjEuMC4xIiB4bWxucz0iaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS9wb3dlcnNoZWxsLzIwMDQvMDQiPjxPYmogUz0icHJvZ3Jlc3MiIFJlZklkPSIwIj48VE4gUmVmSWQ9IjAiPjxUPlN5c3RlbS5NYW5hZ2VtZW50LkF1dG9tYXRpb24uUFNDdXN0b21PYmplY3Q8L1Q+PFQ+U3lzdGVtLk9iamVjdDwvVD48L1ROPjxNUz48STY0IE49IlNvdXJjZUlkIj4xPC9JNjQ+PFBSIE49IlJlY29yZCI+PEFWPtX91NrXvLG4yte0zsq508PEo7/poaM8L0FWPjxBST4wPC9BST48TmlsIC8+PFBJPi0xPC9QST48UEM+LTE8L1BDPjxUPkNvbXBsZXRlZDwvVD48U1I+LTE8L1NSPjxTRD4gPC9TRD48L1BSPjwvTVM+PC9PYmo+PC9PYmpzPg==

Independent byte reconstruction under CP936 reproduces the exact length and SHA. The root cause is therefore accepted as:

    POWERSHELL_STARTUP_PROGRESS_CLIXML_ON_STDERR

It is not classified as Git stderr, a Git failure, a three-way SHA mismatch, a dirty worktree, a verifier exception or transport corruption.

## Accepted Pre-Verifier Core Result

The preserved stdout is the exact frozen 122-byte success payload:

    {"status":"THREE_WAY_SYNC_VERIFIED","git_processes":5,"all_equal":true,"worktree_clean":true,"evidence_paths_absent":true}

The unchanged 74-line verifier can emit this payload only after all five Git children exit zero with empty Git stderr, local/fetched-origin/direct-remote SHA equality, a clean worktree and all four semantics paths absent before and after. This review therefore accepts, specifically for approval commit `ee84988fa6ccf5e7f3524bc2c2a5f94065abf918`:

    pre-verifier core result: passed
    internal Git children: 5
    three-way SHA equality: proven
    worktree clean: proven
    semantics path absence: proven

This does not retroactively convert the old launcher contract into success. Its required zero-byte outer stderr gate failed, the approval was consumed and no bootstrap continuation is authorized.

## Frozen Classifier Rule

For an approved Windows PowerShell child only, stderr may be:

1. exactly zero bytes; or
2. byte-for-byte equal to the frozen 382-byte payload above.

Exact byte equality is mandatory. Substring matching, decoded-text matching, byte-count-only checks and hash-only checks are forbidden. Two concatenated payloads, a field-modified CLIXML record, extra whitespace/newlines, Git warnings, PowerShell exceptions and tracebacks must fail.

The classifier may apply only to these future Windows PowerShell boundaries:

- pre-verifier host and unchanged pre verifier;
- revised bootstrap and revised recovery harness;
- unchanged compatible verifier and semantics wrapper;
- post-verifier host and unchanged post verifier.

Git children, the embedded Python child, official helpers, official capture and every non-PowerShell child retain strict zero-byte stderr.

## Recovery Decision

Hard Failure 15 does not need another raw diagnostic. The current approval is consumed. This review permits only assembly and submission of Amendment 5G-B.1.1.1.1.2 as a complete transport-recovery governance package.

The future package must keep the 74-line pre verifier, 107-line post verifier, 59-line compatible verifier, 122-line semantics wrapper, 46-line embedded Python and 195-line real validator byte-for-byte unchanged. It must freeze new pre/post host classifiers and revised bootstrap/harness parent envelopes, including every source, LF/no-trailing-newline identity, UTF-16LE/Base64 transport, complete arguments, ProcessStartInfo field, expected stdout, stderr classifier and process count.

The synchronization proof for `ee84988...` cannot be reused for a future approval commit. A future package-bound approval must create and push a new approval-governance commit and then run one new pre-verification sequence against that new HEAD.

## Current State

    HARD_FAILURE_15_AUDIT_ACCEPTED
    HARD_FAILURE_15_CHECKPOINT_FROZEN
    RAW_MACHINE_EVIDENCE_ACCEPTED
    ROOT_CAUSE_ESTABLISHED
    POWERSHELL_STARTUP_PROGRESS_CLIXML_ON_STDERR

    PRE_VERIFIER_CORE_RESULT_PROVEN
    INTERNAL_GIT_CHILD_COUNT_PROVEN_5
    THREE_WAY_SYNC_FOR_EE84988_PROVEN
    OLD_OUTER_LAUNCHER_CONTRACT_FAILED

    RETURN_FOR_AMENDMENT_5G_B_1_1_1_1_2_PACKAGE

    CURRENT_APPROVAL_CONSUMED
    DIAGNOSTIC_RETRY_NOT_APPROVED
    DIRECT_BOOTSTRAP_CONTINUATION_NOT_APPROVED
    SEMANTICS_SEQUENCE_NOT_APPROVED
    SEMANTICS_EVIDENCE_NOT_APPROVED
    POST_EVIDENCE_SYNC_NOT_APPROVED
    SYNTHETIC_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_EXECUTION_NOT_APPROVED
