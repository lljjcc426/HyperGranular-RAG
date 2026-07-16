# Stage4B-U1-D Pre-Gold Hard Failure 18 Review 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review date: 2026-07-16
- Review source bytes: 11,408
- Review source SHA-256: `591C38AB7904AF8EA841F29B9B4884D8F1450448D1A83D36345ABF7D554AFF65`
- Approved 1.1.4 package: `683d17bd70cc32dca2e495836bb6b16160a79f79`
- Consumed approval governance: `677df53f014ab194e08042e4f605b5f879b9fa32`
- Hard Failure 18 checkpoint: `a3812d000b8af07196ea3a824988703a3ff132d3`
- Review status: `ACCEPT_HARD_FAILURE_18_AUDIT`
- Required return: `AMENDMENT_5G_B_1_1_1_1_5_FROZEN_OUTER_RESULT_OBSERVER_AND_DURABLE_RAW_CAPTURE_RECOVERY_ONLY`
- Other project conversations, thread tools, and global memory used: No

## Accepted Audit Boundary

The independent review accepts all of the following as established:

```text
APPROVAL_GOVERNANCE_COMMIT_VALID
POST_GOVERNANCE_STATIC_GATE_PASSED_106_OF_106
EXACTLY_ONE_PRE_CAPTURE_HOST_PROCESS_STARTED
PRE_CAPTURE_HOST_PROCESS_WAS_AWAITED
BOTH_RAW_BASESTREAM_COPY_TASKS_COMPLETED
FAILURE_OCCURRED_IN_OUTER_RESULT_OBSERVER
CHILD_RESULT_WAS_NOT_DURABLY_OBSERVED
ALL_SEVEN_FUTURE_EVIDENCE_PATHS_ABSENT
FAIL_CLOSED_STOP_BOUNDARY_CONFIRMED
```

The exact root cause is:

```text
OUTER_OBSERVER_H_ALIAS_RESOLVED_TO_GET_HISTORY
```

The review does not establish a canonical-builder, capture-host, adapter, parent transport, loader, target, or semantics defect. It also does not establish capture-host success. The child exit code, stdout, stderr, stderr class, internal gate position, PRE downstream process counts, and internal Git-child count remain `UNCONFIRMED`.

## Consumed Authorization

The PRE authorization under approval governance `677df53f014ab194e08042e4f605b5f879b9fa32` was consumed by the actual capture-host process start. That approval is not reusable.

There was no retry, fallback, temporary script, alternate adapter, evidence cleanup, reset, rebase, force-push, semantics commit, POST, FINAL, TERMINAL, synthetic, real-validator, formal-preflight, official, Gold, reservation, or Stage3B action.

## Required Amendment Boundary

Amendment 5G-B.1.1.1.1.5 is limited to:

```text
TRACKED_FROZEN_OUTER_RESULT_OBSERVER
DURABLE_RAW_CHILD_STDOUT_STDERR_PRESERVATION
ALIAS_COLLISION_REJECTION
RESULT_READ_ORDER_FIX
NEW_PACKAGE_AND_GIT_CHAIN_COMPATIBILITY
```

The amendment must not claim that the 1.1.4 inner package transport failed. Canonical schema 2.0, the canonical builder, PRE/POST adapters, inherited parent/loader/target sources, six class-bearing stdout variants, and the underlying evidence semantics remain unchanged.

## Observer Requirements

The tracked observer must support `PRE`, `POST`, `FINAL`, and `TERMINAL`, and freeze source identity, parser state, mode-specific `-File` arguments, modeled command, ProcessStartInfo, environment bindings, child stdout/stderr contracts, fixed observer stdout, and process counts.

Single-character or alias-sensitive helpers such as `H`, `G`, `S`, and `F` are forbidden. The SHA helper must use the explicit name `Get-ExactSha256Hex`, and unfiltered `Get-Command` must establish that the command that would actually resolve is a function.

The required post-child order is:

```text
Process.Start
start both BaseStream drains
WaitForExit
WaitAll drains
read ExitCode
materialize stdout/stderr byte arrays
CreateNew durable raw record before any hash/class/helper/serializer
then hash, classify, and apply exact success gates
```

## Durable Raw Record

The amendment selects a fixed binary record instead of JSON serialization. Its success-path records are versioned repository artifacts and use `CreateNew`. Any partial record created during failure must be preserved and never cleaned or overwritten.

PRE, POST, FINAL, and TERMINAL all use the same binary format and policy. The corresponding stage scopes change from `3/3/1` to `4/4/2/1` so every successful raw observation becomes Git-anchored at its stage.

## Current State

```text
HARD_FAILURE_18_AUDIT_ACCEPTED
HARD_FAILURE_18_CHECKPOINT_FROZEN
CURRENT_PRE_AUTHORIZATION_CONSUMED
CURRENT_APPROVAL_NOT_REUSABLE

RETURN_FOR_AMENDMENT_5G_B_1_1_1_1_5
FROZEN_OUTER_RESULT_OBSERVER_AND_DURABLE_RAW_CAPTURE_PACKAGE

PRE_NOT_APPROVED
POST_NOT_APPROVED
FINAL_NOT_APPROVED
TERMINAL_NOT_APPROVED
SYNTHETIC_REBINDING_NOT_APPROVED
FORMAL_PREFLIGHT_NOT_APPROVED
OFFICIAL_EXECUTION_NOT_APPROVED
GOLD_NOT_APPROVED
RESERVATION_NOT_APPROVED
STAGE3B_NOT_APPROVED
```
