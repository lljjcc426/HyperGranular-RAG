# Stage4B U1-D Pre-Gold Amendment 5G-B.1.1.1.1.7 Approval Decision

## Decision

```text
APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_7
DURABLE_OBSERVER_COMMAND_LINE_OBSERVATION_AND_EQUALITY_GATE_DIAGNOSTIC_ONLY

HARD_FAILURE_20_REVIEW_1_ACCEPTED
AMENDMENT_5G_B_1_1_1_1_7_PACKAGE_APPROVED

ONE_NEW_PACKAGE_BOUND_APPROVAL_GOVERNANCE_COMMIT_APPROVED
ONE_POST_GOVERNANCE_PARSER_AND_STATIC_CONTRACT_GATE_APPROVED
ONE_COMMAND_LINE_DIAGNOSTIC_OBSERVER_EXECUTION_APPROVED
ONE_HGRAGC17_OBSERVATION_APPROVED
ONE_EXACT_ONE_PATH_RESULT_COMMIT_AND_PUSH_APPROVED

CAPTURE_HOST_STARTS_ZERO_REQUIRED
ADAPTER_PARENT_LOADER_TARGET_STARTS_ZERO_REQUIRED
IMMEDIATE_STOP_FOR_INDEPENDENT_BYTE_REVIEW_REQUIRED
```

## Approval Material Passport

- Independent approval attachment bytes: 9,072
- Independent approval attachment SHA-256: `1F2662A034DB14D12C4D53A635853ADE97526330F9F85719BA84749AD5CD9BE2`
- This decision records the user-supplied independent approval and does not broaden it.

## Binding Package And Lineage

- Package commit: `8e274060baf844dd1d761e7635bbc6c43ef9d4b6`
- Direct parent / Hard Failure 20 checkpoint: `d0dbc5533ddc464c7f7f1433d660ee7ddc355e07`
- Hard Failure 20 Review 1: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_20_REVIEW_1.md`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_7_MANIFEST.json`
- Manifest bytes: 13,336
- Manifest SHA-256: `968C3D598840CA25A0DFB2F8006027158B5AFD9EDD48F78BEAE9C7363AFE8A3C`
- Observer: `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_diagnostic.ps1`
- Observer lines: 98 LF
- Observer bytes: 5,603
- Observer SHA-256: `545A5A6E72D82C65B086F08D2FC64F3C359B1A0E453F271D1481013D62FC7307`
- Consumed Amendment 1.1.6 approval is non-reusable.

## Frozen Invocation

Executable:

```text
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
```

Complete arguments:

```text
-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_diagnostic.ps1" -Mode COMMAND_LINE_DIAGNOSTIC
```

- Complete arguments characters: 187 ASCII characters
- Complete arguments ASCII SHA-256: `C4F5D93B17DBB3A31DFEA8D0F78B7FE23E16E5999F1E6EF1BA25E517FF95EC5A`
- Complete arguments UTF-16LE bytes: 374
- Complete arguments UTF-16LE SHA-256: `CCC055FB3EC15BB283BB03B9B48F21E17FFB884E12A2A6D83556F6C68059B9D8`
- Modeled command characters including terminal U+0000: 248 UTF-16 code units
- Modeled command UTF-16LE bytes: 496
- Modeled command UTF-16LE SHA-256: `9EB29E9C6C2ABFB8B45208648BE84756EC58F492B15A6489DCD69182EA16238E`

The future observer process must receive exactly these process-scoped bindings:

```text
HGRAG_EXPECTED_PACKAGE_COMMIT=8e274060baf844dd1d761e7635bbc6c43ef9d4b6
HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT=<actual approval-governance commit SHA>
```

## HGRAGC17 Contract

The only approved observation path is:

```text
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_observation.bin
```

The fixed 88-byte little-endian header contains exactly 13 fields: one 8-byte `HGRAGC17` magic, four uint32 values, and eight uint64 values. The registered offsets and fields are:

| Offset | Type | Field |
|---:|---|---|
| 0 | ASCII 8 | magic |
| 8 | uint32 | format version |
| 12 | uint32 | header bytes |
| 16 | uint32 | completion flags |
| 20 | uint32 | reserved |
| 24 | uint64 | actual character count |
| 32 | uint64 | modeled character count |
| 40 | uint64 | file-name character count |
| 48 | uint64 | arguments character count |
| 56 | uint64 | actual UTF-16LE byte length |
| 64 | uint64 | modeled UTF-16LE byte length |
| 72 | uint64 | file-name UTF-16LE byte length |
| 80 | uint64 | arguments UTF-16LE byte length |

Payload order is actual `[Environment]::CommandLine` without an appended NUL, modeled command including terminal U+0000, registered executable, and complete arguments. All payloads are strict UTF-16LE without BOM. Every byte length must equal twice its UTF-16 code-unit count, and total file length must close exactly.

The observer must complete `CreateNew`, header and payload writes, `Flush(true)`, and close before constructing `actual + U+0000` and performing the case-sensitive equality gate. Equality maps only to exit 0 or exit 1. Either exit is eligible for the one-path result commit if and only if the record is structurally complete.

## Approval-Governance Commit Contract

The approval-governance commit must be the direct child of package commit `8e274060baf844dd1d761e7635bbc6c43ef9d4b6` and change exactly these two paths with zero deletions:

```text
AGENTS.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_7_APPROVAL_DECISION.md
```

The commit must be pushed before any parser invocation, observer execution, or evidence write. After the push, local `HEAD`, local `main`, `origin/main`, and direct GitHub `main` must agree; the worktree must be clean; and the observation path must remain absent.

## Authorized Execution Order

1. Commit and push the exact two-path approval-governance change.
2. Verify local/tracking/direct-GitHub equality, clean worktree, and observation-path absence.
3. Invoke the PowerShell parser exactly once and complete the static source/Manifest/invocation/binary/durable-order contract gate with observer execution and evidence writes still zero.
4. If and only if every static gate passes, start the frozen observer at most once with the actual approval-governance SHA and the package SHA in the process-scoped bindings.
5. Preserve the resulting path exactly as created. Do not start capture host, adapter, parent, loader, target ScriptBlock, or any other child.
6. Check only record structural completeness. Do not compute or report difference semantics.
7. If the record is complete, commit exactly the one observation path as a direct child of the actual approval-governance commit, push it, verify remote equality and clean worktree, and stop.
8. If the record is incomplete or any gate fails, do not retry, overwrite, clean up, or create a result commit; stop for a separately governed Hard Failure audit.

## Result Commit Contract

A structurally complete `HGRAGC17` record authorizes exactly one commit and one push even when the observer equality exit is 1. The commit must be the direct child of the actual approval-governance commit and change only:

```text
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_observation.bin
```

No status document, audit narrative, difference interpretation, or other path may enter the result commit. Its commit message must not state or infer the difference type.

## Failure Boundary

Any approval parent/path mismatch, remote/worktree mismatch, parser/static failure, source/invocation/binding mismatch, path collision, `CreateNew`/write/flush/close failure, incomplete header/payload, second process attempt, result-scope mismatch, commit failure, or push failure is a hard stop.

```text
OBSERVER_RETRY_FORBIDDEN
CAPTURE_HOST_STARTS_ZERO_REQUIRED
PARTIAL_RECORD_PRESERVE_AS_CREATED
INCOMPLETE_RECORD_RESULT_COMMIT_ZERO
INCOMPLETE_RECORD_RESULT_PUSH_ZERO
NO_CLEANUP_OR_OVERWRITE
NO_POST_FAILURE_DIAGNOSTIC_EXECUTION
```

## Explicitly Not Approved

```text
NESTED_PRE_CHAIN_NOT_APPROVED
CAPTURE_HOST_NOT_APPROVED
ADAPTER_NOT_APPROVED
PARENT_NOT_APPROVED
LOADER_NOT_APPROVED
TARGET_SCRIPTBLOCK_NOT_APPROVED
POST_NOT_APPROVED
FINAL_NOT_APPROVED
TERMINAL_NOT_APPROVED
SYNTHETIC_REBINDING_NOT_APPROVED
REAL_PRECOMMIT_VALIDATOR_NOT_APPROVED
FORMAL_PREFLIGHT_NOT_APPROVED
OFFICIAL_EXECUTION_NOT_APPROVED
GOLD_NOT_APPROVED
RESERVATION_NOT_APPROVED
STAGE3B_NOT_APPROVED
```

## Required Completion State

```text
AMENDMENT_5G_B_1_1_1_1_7_COMMAND_LINE_OBSERVATION_COMMITTED_AWAITING_INDEPENDENT_REVIEW
HGRAGC17_COMMITTED
ACTUAL_AND_MODELED_UTF16LE_BYTES_DURABLE
CAPTURE_HOST_STARTS_ZERO
DIFFERENCE_TYPE_NOT_YET_INTERPRETED
NESTED_PRE_CHAIN_NOT_RUN
POST_NOT_RUN
FINAL_NOT_RUN
TERMINAL_NOT_RUN
STAGE3B_KEEP_LOCKED
```
