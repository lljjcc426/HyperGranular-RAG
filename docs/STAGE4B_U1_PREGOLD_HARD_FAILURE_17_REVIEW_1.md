# Stage4B-U1-D Pre-Gold Hard Failure 17 Review 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review date: 2026-07-16
- Approved base package: `ef87f0379f4f31c54881c4a0e23a3f7ad8c8c35b`
- Valid approval governance: `1afdd8075169e70d385e617ade480880cf3eb718`
- Reviewed checkpoint: `6c741c251dce55236b06dc5c06fd834b7649f8b2`
- Decision: `ACCEPT_HARD_FAILURE_17_AUDIT`
- Recovery: `RETURN_FOR_AMENDMENT_5G_B_1_1_1_1_4_FROZEN_TOP_LEVEL_PARENT_HOST_ORCHESTRATION_ADAPTER_AND_SCHEMA_SEMANTICS_BINDING_ONLY`
- Execution authorized: No
- Other project conversations, thread tools, and global memory used: No

## Accepted Boundaries

The review confirms that approval-governance commit `1afdd807...` is the exact two-path direct child of package `ef87f037...` and was pushed before the approved PRE reconstruction. It accepts the following passed static identities:

| Gate | Accepted identity |
|---|---|
| PRE parent source | 96 lines / 7,922 UTF-8 bytes / `8F11033CD306D118C4211109EACF8F0C1E9A90BCAEA8E19F99C933DC1C0858A7` |
| PRE parent parser | 0 errors |
| PRE complete arguments | 21,115 characters / `00B201AA16F7A1CF106ADACADBE35DDF44FF67E08FE4A2A8434A8912F4106E67` |

The failure occurred before `Process.Start()`. Process-start attempts, PRE parent/loader/target, inner PRE chain, POST, FINAL, and all evidence counts are zero. PID, exit code, stdout, stderr, and stderr class are therefore `NOT_AVAILABLE_PROCESS_NOT_STARTED`.

## Root Cause

The three Manifest fields have different semantics:

- `runtime = Windows PowerShell 5.1 Desktop` is a runtime label;
- `process_start_info_contract.file_name = C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` is the executable path;
- `modeled_createprocess_command_line = QUOTED_FILE_NAME_SPACE_ARGUMENTS_TERMINAL_NULL` is a schema descriptor.

The helper used the runtime label as the executable path and compared a generated command with the descriptor as though it were literal command text. Correct read-only recomputation with the registered executable, one separator space, registered arguments, quotes, and terminal null produced the registered 21,176 characters and SHA-256 `E8247D1AF7D1CC5F6FEBF32F9102D49A37076FA19602906D7C9121E45EC808F0`.

The root cause is therefore:

    ORCHESTRATOR_SCHEMA_DESCRIPTOR_MISINTERPRETATION

No frozen source or bounded parent transport defect is established.

## Preservation And Stop

All six future evidence paths remain absent. The three historical machine files remain 122 / 382 / 944 bytes with their registered SHA-256 values. No partial evidence exists, and no retry, fallback, transport change, cleanup, reset, rebase, or force-push occurred.

The disclosed pre-governance source-lines inspection is accepted as `DISCLOSED_PRE_GOVERNANCE_READ_ONLY_INSPECTION`, not as the approved PRE reconstruction. Future approval sequencing must forbid source-line join, parser, or reconstruction before package-bound approval governance is pushed.

## Required Amendment 5G-B.1.1.1.1.4

The next package may preserve all nine sources, six bounded envelopes, three payloads, both parent-host paths, evidence schema, extended final verifier, and 62 fixtures. It must add three finite tracked trust roots:

1. `PRE_PARENT_START_ORCHESTRATOR`;
2. `POST_PARENT_START_ORCHESTRATOR`;
3. `FINAL_PARENT_START_ORCHESTRATOR`.

Each must require the exact descriptor, forbid using it as command text, take the executable only from `process_start_info_contract.file_name`, reject runtime/host/role labels as executable sources, apply the unique quoted-file/single-space/arguments/NUL formula, verify character count and SHA before creating `ProcessStartInfo`, use frozen process fields and environment bindings, and capture and validate exact parent stdout/stderr.

Required negative fixtures independently cover PRE, POST, and FINAL: runtime label as executable, descriptor as literal text, wrong descriptor/path, missing quotes/space/null, appended character, same-length mutation, and exact formula acceptance.

## Current State

    HARD_FAILURE_17_AUDIT_ACCEPTED
    HARD_FAILURE_17_CHECKPOINT_FROZEN
    APPROVAL_GOVERNANCE_COMMIT_VALID
    PRE_PARENT_SOURCE_PARSER_ARGUMENT_IDENTITIES_PASSED
    PRE_PARENT_MODELED_COMMAND_GATE_FAILED_BEFORE_PROCESS_START

    ROOT_CAUSE_ESTABLISHED_ORCHESTRATOR_SCHEMA_DESCRIPTOR_MISINTERPRETATION
    PACKAGE_SOURCE_DEFECT_NOT_ESTABLISHED
    PACKAGE_BOUNDED_TRANSPORT_DEFECT_NOT_ESTABLISHED
    ALL_RUNTIME_AND_EVIDENCE_COUNTS_ZERO

    CURRENT_APPROVAL_CONSUMED
    CURRENT_APPROVAL_RETRY_NOT_APPROVED
    RETURN_FOR_AMENDMENT_5G_B_1_1_1_1_4

    PRE_NOT_APPROVED
    POST_NOT_APPROVED
    FINAL_NOT_APPROVED
    SYNTHETIC_REBINDING_NOT_APPROVED
    REAL_PRECOMMIT_VALIDATOR_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_EXECUTION_NOT_APPROVED
    GOLD_NOT_APPROVED
    RESERVATION_NOT_APPROVED
    STAGE3B_NOT_APPROVED
