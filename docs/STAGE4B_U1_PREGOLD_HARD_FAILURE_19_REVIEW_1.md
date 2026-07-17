# Stage4B-U1-D Pre-Gold Hard Failure 19 Review 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review date: 2026-07-17
- Independent review source: user-supplied `pasted-text.txt`
- Review source bytes: 12,538
- Review source SHA-256: `1A06242761DBC64C0FE83AA49E931CEEFCCFCC92851195B37A952CD061BF6506`
- Approved 1.1.5 package: `f634a1ca766cc2885017f63f94ef9b87cab9a765`
- Consumed approval governance: `950b56e83de8a87b7afe75eb3f021819e19516c8`
- Hard Failure 19 checkpoint: `96e9677d4779b9d4b3be59fbb319e0b4c6670732`
- Review status: `ACCEPT_HARD_FAILURE_19_AUDIT`
- Required return: `AMENDMENT_5G_B_1_1_1_1_6_NESTED_DURABLE_RESULT_CAPTURE_PRE_ONLY_DIAGNOSTIC_PACKAGE`
- Other project conversations, thread tools, and global memory used: No

## Accepted Audit Boundary

The independent review accepts:

```text
APPROVAL_GOVERNANCE_COMMIT_VALID
POST_GOVERNANCE_STATIC_GATES_34_OF_34_AND_43_OF_43
EXACTLY_ONE_PRE_OBSERVER_EXECUTION
DURABLE_RAW_PRESERVATION_COMPLETED_BEFORE_SUCCESS_GATE
HGRAGO15_RECORD_STRUCTURALLY_COMPLETE
PRE_CAPTURE_HOST_CHILD_EXIT_1
PRE_CAPTURE_HOST_STDOUT_ZERO_BYTES
PRE_CAPTURE_HOST_STDERR_472_BYTES
CAPTURE_HOST_REPORTED_ADAPTER_NONZERO_EXIT_1
ADAPTER_PROCESS_STARTED_ONCE_AND_EXITED_1
FAIL_CLOSED_STOP_AND_NO_RETRY
```

The established failure boundary is:

```text
PRE_CAPTURE_HOST_REPORTED_ADAPTER_NONZERO_EXIT_1
```

The adapter's raw stdout/stderr, its internal failure gate, parent start/result, loader start/result, target ScriptBlock invocation, semantics start, and internal Git/Python counts remain `UNCONFIRMED`. No package-source, parent-transport, loader, target, or semantics defect is established.

## Independently Accepted Machine Evidence

The preserved record is immutable:

```text
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_5_pre_capture_outer_observation.bin
520 bytes
4ABEB26000DDC77E8293DB1616682E6748E2290A9608959A2A040B1CD2780A70
```

Independent byte decoding established:

```text
magic              HGRAGO15
format version     1
header bytes       48
mode               1 / PRE
completion flags   15
child exit         1
reserved           0
stdout bytes       0
stderr bytes       472
total              48 + 0 + 472 = 520
```

The persisted 472-byte stderr has SHA-256 `9E8393DD9738C73FCA928BD28E0031A6B8EABF4FABE9147FA0F101ED969D56EB` and reports `Adapter nonzero exit: 1`. The separately audit-recorded 492-byte outer-observer stderr has no additional outer binary record and is not claimed as independently byte-verifiable.

## Validated Recovery and Consumed Authorization

The 1.1.5 outer observer performed `WaitForExit`, both stream drains, exit/raw-array materialization, `CreateNew`, fixed-header/raw-payload write, and `Flush(true)` before applying the child exit gate. Therefore:

```text
FROZEN_OUTER_OBSERVER_RECOVERY_DESIGN_VALIDATED
DURABLE_RAW_BEFORE_CLASSIFICATION_VALIDATED
HARD_FAILURE_18_OBSERVABILITY_GAP_CLOSED
```

The authorization under `950b56e83de8a87b7afe75eb3f021819e19516c8` was consumed and is not reusable. There was no retry, fallback, evidence cleanup, semantics success commit, POST, FINAL, TERMINAL, synthetic, real-validator, formal-preflight, official, Gold, reservation, or Stage3B action.

## Required Amendment Boundary

Amendment 5G-B.1.1.1.1.6 is limited to a new package-bound approval and one PRE-only diagnostic chain. It must add durable raw preservation before the exit/success gate at these actual `Process.Start` boundaries:

```text
outer observer -> capture host       required and versioned
capture host -> adapter              required
adapter -> parent                    included to prevent another opaque stop
parent -> loader                     included to prevent another opaque stop
```

The target ScriptBlock runs inside the loader process. No fictitious target-process record may be created.

Each boundary must preserve the exit code and both raw streams through an exclusive versioned file, complete `Flush(true)`, and only then apply hash, classification, helper, serializer, exit, stdout, or stderr gates. The old Hard Failure 19 record must not be deleted, overwritten, renamed, or reused.

## Approval and Lineage Boundary

The new package must be the single direct child of `96e9677d4779b9d4b3be59fbb319e0b4c6670732`. Before the new package-bound approval is committed and pushed, only package/Manifest identity, preserved Hard Failure 19 raw identity, future-path absence, worktree status, and local/origin/direct-main equality may be checked.

Joining, parsing, reconstructing, dot-sourcing, or executing the new observer, capture host, adapter, parent, or loader is forbidden before that approval. The next approval must not authorize POST, FINAL, or TERMINAL.

## Current State

```text
HARD_FAILURE_19_AUDIT_ACCEPTED
HARD_FAILURE_19_CHECKPOINT_FROZEN
CURRENT_PRE_AUTHORIZATION_CONSUMED
CURRENT_APPROVAL_NOT_REUSABLE

RETURN_FOR_AMENDMENT_5G_B_1_1_1_1_6
NESTED_DURABLE_RESULT_CAPTURE_PRE_ONLY_DIAGNOSTIC_PACKAGE

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
