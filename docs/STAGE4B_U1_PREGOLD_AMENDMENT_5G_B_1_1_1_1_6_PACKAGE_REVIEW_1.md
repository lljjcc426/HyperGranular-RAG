# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1.6 Package Review 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review received: 2026-07-17
- Independent review source: user-supplied `pasted-text.txt`
- Review source bytes: 9,654
- Review source SHA-256: `9C479FB904FB54812E0DA389353E1E95BDC84DC5A878B6651E90F72317C6D3EE`
- Reviewed package: `1e0973e3036af6f54aaf68e0699e35a34d2b78cd`
- Direct parent / Hard Failure 19 checkpoint: `96e9677d4779b9d4b3be59fbb319e0b4c6670732`
- Reviewed Manifest: 13,802 bytes / SHA-256 `7DA3418D8BF7F4CF49D82088294D78CFB6FB6C8E7F66229F18624FE60A929937`
- Decision: `REJECT_AMENDMENT_5G_B_1_1_1_1_6_PACKAGE_AS_CURRENTLY_WRITTEN`
- Recovery: `RETURN_FOR_CORRECTED_AMENDMENT_5G_B_1_1_1_1_6_PACKAGE`
- Approval governance authorized: No
- PRE execution authorized: No
- Other project conversations, thread tools, and global memory used: No

## Accepted Findings

The independent review accepts:

1. Hard Failure 19 Review 1;
2. package `1e0973e3...` and its exact twelve-path, zero-deletion scope;
3. the immutable 520-byte Hard Failure 19 raw binding;
4. the PRE-only diagnostic direction;
5. the four nested raw layers `HGRAGO16`, `HGRAGA16`, `HGRAGP16`, and `HGRAGL16`;
6. the durable result order at the observer, capture-host, and adapter boundaries;
7. the reported 116/116 static validation; and
8. the zero-new-source-execution and zero-new-evidence package boundary.

The established prior failure remains `PRE_CAPTURE_HOST_REPORTED_ADAPTER_NONZERO_EXIT_1`. Adapter raw streams and parent/loader/target/semantics causes remain `UNCONFIRMED`; no package-source or transport defect is established.

## Blocking Causes

The reviewed package is rejected for exactly three causes:

```text
LOADER_STDIN_DELIVERY_FAILURE_CAN_ESCAPE_AFTER_PROCESS_START_BEFORE_HGRAGL16_PERSISTENCE
FAILURE_EVIDENCE_COMMIT_PARENT_AND_EXACT_PATH_SCOPE_NOT_FROZEN
REQUESTED_COMPLETION_STATE_INCORRECTLY_REMAINS_PRE_APPROVAL_STATE
```

### Loader stdin-delivery observability was incomplete

The nested parent started the loader and both raw drains, then performed `StandardInput.BaseStream.Write`, `Flush`, and `Close` under `$ErrorActionPreference = 'Stop'`. Any exception in those operations could terminate the parent before `WaitForExit`, `WaitAll`, raw-array materialization, and `HGRAGL16` creation. Absence of the loader raw path would therefore not distinguish a loader that never started from a loader that started but encountered stdin delivery failure.

The correction must capture stdin access/write/flush/close failures locally, ensure a close attempt, await the loader and both drains, persist and durably flush `HGRAGL16`, and only then throw a frozen normalized stdin-delivery failure before the ordinary exit/stdout/stderr success gates.

### Failure Git scope was runtime-selectable

The rejected request proposed one `failure-or-success` evidence commit but froze only the successful six paths. It did not freeze a failure-audit path, failure-commit parent, state-document paths, or every raw-prefix/partial-semantics combination.

The corrected package selects review-recommended Scheme A:

```text
SUCCESS:
commit and push exactly the two semantics files plus all four new raw records.

FAILURE:
preserve the complete outer-to-inner raw prefix and any partial semantics files;
create no commit and perform no push in the execution turn;
stop immediately for a separately governed Hard Failure audit package.
```

This removes all runtime selection among unregistered failure commit path sets.

### Completion state described the wrong gate

The rejected request and Manifest named an approval-waiting state as the requested post-execution completion state. The correction must freeze result-review states for both the success and failure branches, plus a unified attempt-completed review boundary.

## Content Allowed To Remain Unchanged

The review permits the following to remain unchanged:

- Hard Failure 19 Review 1 and checkpoint lineage;
- the old 520-byte raw record;
- the PRE-only authorization direction;
- the four raw magics, header format, and contiguous-prefix rule;
- observer, capture-host, and adapter raw-before-gate implementation;
- nested parent loader/target identities and payload reconstruction;
- standalone raw verifier prefix checks; and
- the reported 116/116 original package fixtures.

## Current State

```text
HARD_FAILURE_19_AUDIT_ACCEPTED
HARD_FAILURE_19_CHECKPOINT_FROZEN

PACKAGE_1E0973E3_SCOPE_ACCEPTED_BUT_PACKAGE_NOT_APPROVED
FOUR_LAYER_NESTED_RAW_ARCHITECTURE_ACCEPTED
OUTER_CAPTURE_ADAPTER_PARENT_DURABLE_ORDER_ACCEPTED

LOADER_STDIN_DELIVERY_OBSERVABILITY_NOT_CLOSED_IN_REJECTED_PACKAGE
FAILURE_COMMIT_PATH_SCOPE_NOT_FROZEN_IN_REJECTED_PACKAGE
POST_EXECUTION_COMPLETION_STATE_NOT_DEFINED_IN_REJECTED_PACKAGE

RETURN_FOR_CORRECTED_AMENDMENT_5G_B_1_1_1_1_6_PACKAGE

APPROVAL_GOVERNANCE_NOT_APPROVED
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
