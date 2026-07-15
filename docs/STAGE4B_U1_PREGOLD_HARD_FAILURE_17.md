# Stage4B-U1-D Pre-Gold Hard Failure 17

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Failure date: 2026-07-16
- Approved second-corrected package: `ef87f0379f4f31c54881c4a0e23a3f7ad8c8c35b`
- Approval governance: `1afdd8075169e70d385e617ade480880cf3eb718`
- Manifest: 323607 bytes / `804B4F8607532D6CE17EDE043D5A9511C7E855F4EB444C25F461381B6EDDA73D`
- Failure status: `AMENDMENT_5G_B_1_1_1_1_3_PRE_PARENT_MODELED_COMMAND_GATE_STOPPED_HARD_FAILURE_17`
- Failure boundary: `PRE_PARENT_STATIC_MODELED_COMMAND_TEXT_GATE_BEFORE_PROCESS_START`
- Registered failure: `PRE_PARENT_MODELED_COMMAND_TEXT_MISMATCH`
- Process-start attempts: 0
- Actual PRE parent processes started: 0
- Automatic retries: 0
- Other project conversations, thread tools, and global memory used: No

## Approval-governance Gate

The package-bound approval was recorded as exact two-path commit:

    approval governance:
    1afdd8075169e70d385e617ade480880cf3eb718

    direct parent:
    ef87f0379f4f31c54881c4a0e23a3f7ad8c8c35b

    changed paths:
    AGENTS.md
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_APPROVAL_DECISION.md

The commit was pushed successfully. Before the approved PRE reconstruction, local HEAD, tracked `origin/main`, and direct GitHub main all equaled `1afdd8075169e70d385e617ade480880cf3eb718`; the worktree was clean; all six future evidence paths were absent; and all three historical machine-evidence files matched their frozen byte counts and SHA-256 identities.

## Static Reconstruction Boundary

The approved PRE helper reconstructed the registered parent source in memory with LF joining and no trailing newline. These gates passed:

    source lines: 96
    source UTF-8 bytes: 7922
    source SHA-256: 8F11033CD306D118C4211109EACF8F0C1E9A90BCAEA8E19F99C933DC1C0858A7
    static parser errors: 0

    complete arguments characters: 21115
    complete arguments SHA-256: 00B201AA16F7A1CF106ADACADBE35DDF44FF67E08FE4A2A8434A8912F4106E67

It then constructed a candidate modeled command line from the wrong Manifest fields and compared that candidate to a schema descriptor as though the descriptor were literal command text. The gate raised:

    PRE_PARENT_MODELED_COMMAND_TEXT_MISMATCH

The exception occurred before construction of `ProcessStartInfo` was completed and before any call to `Process.Start()`.

## Established Orchestration Root Cause

The Manifest fields have distinct roles:

    pre parent runtime label:
    Windows PowerShell 5.1 Desktop

    process_start_info_contract.file_name:
    C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe

    modeled_createprocess_command_line schema descriptor:
    QUOTED_FILE_NAME_SPACE_ARGUMENTS_TERMINAL_NULL

The helper incorrectly treated the runtime label as an executable path and treated the schema descriptor as literal modeled command text. This is frozen as:

    ORCHESTRATOR_SCHEMA_DESCRIPTOR_MISINTERPRETATION

A post-stop read-only diagnostic used the registered executable path, one space, the already registered complete arguments, and a terminal null. It recomputed:

    modeled command-line characters including terminal null: 21176
    modeled command-line SHA-256 including terminal null:
    E8247D1AF7D1CC5F6FEBF32F9102D49A37076FA19602906D7C9121E45EC808F0

Both values exactly match the Manifest. Therefore this run does not establish a defect in the frozen package source, arguments, or bounded command-line design. It establishes a defect in the local orchestration helper used to interpret the Manifest schema.

## Read-only Helper Record

Before approval-governance creation, a package-inspection helper joined and parsed the nine registered `source_lines` arrays, including the PRE parent source, then stopped at a PowerShell strict-mode empty-collection `.Count` check before checking any encoded envelope. It launched no process and wrote no file. Because it preceded the governance commit, it is preserved here as a sequencing limitation and must not be represented as the approved PRE reconstruction.

Other read-only helpers stopped on an incorrect Manifest path, unavailable `rg.exe`, and two additional PowerShell strict-mode empty-collection checks. A post-stop diagnostic printed the schema descriptor and then stopped on an invalid negative substring length before the corrected diagnostic was run. None called a frozen source, `Process.Start()`, Git mutation, Python, official input, or evidence writer. These helper failures are disclosed; they are not retries of a started PRE process.

The first Hard Failure 17 audit-path verifier also stopped because its expected culture-sensitive sort order placed `README.md` before `docs/*`, while PowerShell returned the same exact five-path set with `README.md` last. It performed no mutation; the path set itself was not discrepant.

## Exact Execution Boundary

    approval-governance commits: 1
    approval-governance pushes: 1
    pre-governance package source inspections: 9
    pre-governance PRE parent source inspections: 1
    approved PRE parent static reconstructions: 1
    approved PRE Process.Start attempts: 0
    approved PRE parent processes started: 0
    pre stdin-loader processes: 0
    pre target ScriptBlock invocations: 0
    pre hosts: 0
    pre verifiers: 0
    pre-verifier Git children: 0
    bootstrap processes: 0
    harness processes: 0
    compatible-verifier processes: 0
    semantics-wrapper processes: 0
    embedded Python processes: 0
    semantics machine creations: 0
    semantics narrative creations: 0
    semantics evidence commits: 0
    post parent reconstructions/processes: 0
    post loader/target/host/verifier processes: 0
    post Git children: 0
    post machine/narrative creations: 0
    post audit commits: 0
    final parent reconstructions/processes: 0
    final loader/verifier processes: 0
    final Git children: 0
    synthetic rebinding: 0
    real precommit validator: 0
    formal preflight: 0
    official input accesses: 0
    authorization-token uses: 0
    official captures: 0
    controller/verifier/Gold operations: 0
    automatic retries of any frozen process: 0

No process was created, so PID, exit code, raw stdout, raw stderr, and registered success class are all:

    NOT_AVAILABLE_PROCESS_NOT_STARTED

## Post-failure Preservation Audit

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

There is no partial evidence to delete, overwrite, normalize, or commit. The repository remained at the pushed approval-governance commit until this audit was written.

## Stop Boundary

The approval explicitly classifies command-line identity failure as consuming the corresponding one-pass authorization. The PRE/POST/FINAL chain therefore stopped before `Process.Start()` and no corrected orchestration was attempted.

No retry, fallback, temporary `.ps1`, `-File`, StreamWriter, source replacement, runtime switch, partial-evidence cleanup, reset, rebase, or force-push occurred. Independent review and a new Amendment/package-bound approval are required before any further source or command reconstruction.

    AMENDMENT_5G_B_1_1_1_1_3_PRE_PARENT_MODELED_COMMAND_GATE_STOPPED_HARD_FAILURE_17
    APPROVAL_GOVERNANCE_COMMITTED_AND_PUSHED
    PRE_PARENT_SOURCE_PARSER_ARGUMENT_IDENTITIES_PASSED
    PRE_PARENT_MODELED_COMMAND_GATE_FAILED_IN_ORCHESTRATOR
    PRE_PARENT_PROCESS_NOT_STARTED
    VALIDATOR_SEMANTICS_NOT_RUN
    SEMANTICS_EVIDENCE_NOT_CREATED
    POST_SYNC_NOT_RUN
    POST_SYNC_AUDIT_NOT_CREATED
    FINAL_POST_SYNC_AUDIT_COMMIT_VERIFIER_NOT_RUN

    ORCHESTRATION_RETRY_NOT_APPROVED
    TRANSPORT_CHANGE_NOT_APPROVED
    SYNTHETIC_REBINDING_NOT_APPROVED
    REAL_PRECOMMIT_VALIDATOR_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_EXECUTION_NOT_APPROVED
    GOLD_NOT_APPROVED
    RESERVATION_NOT_APPROVED
    STAGE3B_NOT_APPROVED
