# Stage4B-U1-D Pre-Gold Hard Failure 16

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Failure date: 2026-07-15
- Second corrected package: 945f655b95cfee9e55ad2d20e7bd5018f9aee1e2
- Approval governance: 72783071c17f6e3cab347823a8da080171c1a883
- Failure status: AMENDMENT_5G_B_1_1_1_1_2_PRE_RUNNER_START_STOPPED_HARD_FAILURE_16
- Failure boundary: PRE_AND_SEMANTICS_OUTER_RUNNER_PROCESS_START
- Pre/semantics outer-runner source reconstructions: 1
- Process-start attempts: 1
- Pre/semantics outer-runner processes started: 0
- Automatic retries: 0
- Other project conversations, thread tools and global memory used: No

## Approval-Governance Gate

The package-bound approval was recorded and pushed before any source reconstruction:

    approval governance:
    72783071c17f6e3cab347823a8da080171c1a883

    direct parent:
    945f655b95cfee9e55ad2d20e7bd5018f9aee1e2

    changed paths:
    AGENTS.md
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_2_APPROVAL_DECISION.md

The commit was pushed successfully. A subsequent read-only gate found local HEAD, fetched `origin/main` and direct GitHub main all equal to `72783071c17f6e3cab347823a8da080171c1a883`. The worktree was clean, the three historical machine files retained their frozen identities, and all four semantics paths plus both post-sync audit paths were absent.

## Single Static Reconstruction

The host reconstructed the approved pre/semantics outer runner exactly once from the package Manifest with LF separators and no trailing newline. Every frozen pre-start identity gate passed:

    Manifest bytes: 227242
    Manifest SHA-256: 69CA3DAD8664F12213933A603D0AE0955C8AC17E483E5DC433859839AD49086E

    source lines: 194
    source UTF-8 bytes: 14491
    source SHA-256: 6B24A6F25B5ABF4212A14D16E58EB569015C1D41EEB5587E70C9CD6C5E3CE124
    static parser errors: 0

    complete arguments characters: 38599
    complete arguments SHA-256: 53D27DD17FC3D4E6E8708E970C2BEFA4932AAE511A99D6EDF4A0BDFA9B498753

    expected stdout bytes: 170
    expected stdout SHA-256: E9AF80CBD27E3CE3D04FE6ED8FD2E81102E53AA0D33663E4B1BF203C40BC8F29

The executable and invocation fields were the frozen values:

    C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
    -NoLogo -NoProfile -NonInteractive -EncodedCommand <frozen UTF-16LE Base64>
    working directory: E:\科研\HyperGranular-RAG

No source, parser, Manifest, complete-arguments or expected-stdout mismatch occurred before the one authorized process-start attempt.

## Failed Process-Start Gate

The first and only call to `System.Diagnostics.Process.Start()` failed before a PowerShell process was created. The observed exception was:

    exception category: System.ComponentModel.Win32Exception
    message: The filename or extension is too long

The failure occurred with the exact frozen 38,599-character arguments. No shorter arguments, temporary script, alternate transport, runtime switch or source modification was attempted. The process never acquired a PID, so the accurate output boundary is:

    process-start attempts: 1
    pre/semantics outer-runner processes started: 0
    exit code: NOT_AVAILABLE_PROCESS_NOT_CREATED
    stdout: NOT_AVAILABLE_PROCESS_NOT_CREATED
    stderr: NOT_AVAILABLE_PROCESS_NOT_CREATED
    accepted exact successes: 0

The direct observed cause is `FROZEN_38599_CHARACTER_ENCODED_COMMAND_REJECTED_BY_PROCESS_START_AS_TOO_LONG`. This establishes a frozen outer transport start defect; it does not establish any defect in the pre host, pre verifier, bootstrap, harness, compatible verifier, wrapper, embedded Python or their outputs because none ran.

## Post-Failure Preservation Audit

The three historical machine files remained unchanged:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stdout.bin` | 122 | `BCDF0010147E5952AD0372ADF39EDA0A18D349B02107C340DEF05BAFE18C0F09` |
| `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stderr.bin` | 382 | `4F2B6B3ED9201CA459DB2DD042E0A137C4E58BFE8E15A068E45AD8535FA5B1EF` |
| `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_diagnostic.json` | 944 | `F4022C8B4DF507D9A63085698B846358FF6D33F2A67B55B0C54EB871E8EB101B` |

All six future paths remained absent:

    results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_validator_semantics.json
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_VALIDATOR_SEMANTICS_AUDIT.md
    results/stage4b_u1_d_pregold_amendment_5g_b_1_1_validator_semantics.json
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_VALIDATOR_SEMANTICS_AUDIT.md
    results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_post_sync_transport_attestation.json
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_POST_SYNC_TRANSPORT_AUDIT.md

No partial semantics or post-sync artifact exists to clean, overwrite, normalize or commit.

## One-Time Counts

    approval-governance commits: 1
    approval-governance pushes: 1
    pre/semantics outer-runner static reconstructions: 1
    pre/semantics outer-runner process-start attempts: 1
    pre/semantics outer-runner processes started: 0
    pre-host processes: 0
    unchanged pre-verifier processes: 0
    frozen-chain Git children: 0
    bootstrap processes: 0
    harness processes: 0
    compatible-verifier processes: 0
    semantics-wrapper processes: 0
    embedded Python processes: 0
    semantics evidence creations: 0
    semantics evidence commits: 0
    post-sync outer-runner reconstructions/processes: 0
    post-host/post-verifier processes: 0
    post-sync audit creations/commits: 0
    final-host/final-verifier processes: 0
    final-verifier Git children: 0
    complete synthetic runs: 0
    real validator invocations: 0
    formal preflight invocations: 0
    official input accesses: 0
    authorization token uses: 0
    official captures: 0
    controller/verifier/Gold operations: 0
    automatic retries: 0

The package-assembly read-only helper counts remain historical package metadata and are not part of this frozen execution attempt.

## Stop Boundary

The ordered authorization was consumed at the first pre/semantics outer-runner process-start gate. No retry, fallback, transport repair, temporary file, alternate executable, reset, rebase or cleanup occurred.

Independent review is required before any transport change or new attempt. Until a new package-bound approval:

    AMENDMENT_5G_B_1_1_1_1_2_PRE_RUNNER_START_STOPPED_HARD_FAILURE_16
    APPROVAL_GOVERNANCE_COMMITTED_AND_PUSHED
    PRE_RUNNER_SOURCE_AND_TRANSPORT_FINGERPRINTS_PASSED
    PRE_RUNNER_PROCESS_NOT_CREATED
    PRE_EXECUTION_SYNC_NOT_VERIFIED
    VALIDATOR_SEMANTICS_NOT_RUN
    SEMANTICS_EVIDENCE_NOT_CREATED
    POST_EVIDENCE_SYNC_NOT_RUN
    POST_SYNC_AUDIT_NOT_CREATED
    FINAL_POST_SYNC_AUDIT_COMMIT_VERIFIER_NOT_RUN

    TRANSPORT_RETRY_NOT_APPROVED
    TRANSPORT_REPAIR_OR_REPLACEMENT_NOT_APPROVED
    SYNTHETIC_REBINDING_NOT_APPROVED
    REAL_PRECOMMIT_VALIDATOR_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_EXECUTION_NOT_APPROVED
    GOLD_NOT_APPROVED
    RESERVATION_NOT_APPROVED
    STAGE3B_NOT_APPROVED
