# Stage4B-U1-D Pre-Gold Hard Failure 22 Review 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review date: 2026-07-18
- Hard Failure 22 checkpoint: `a740f669d535ab3a148c42f6839de6837eec9c15`
- Consumed approval governance: `4d9886be1291133c7a8f94c3a4b35a14f26e0a8d`
- Amendment 1.1.8 package: `90438287eeb77c2d383d7073315276a322b5670d`
- Independent review attachment bytes: 9,485
- Independent review attachment SHA-256: `E95E341ABF1497AC8C555C2C82C74F90384C76AC000DFC78FE2ED33A6200B309`
- Other project conversations, thread tools, and global memory used: No

## Independent Review Decision

```text
ACCEPT_HARD_FAILURE_22_AUDIT
CONFIRM_HARD_FAILURE_22_CHECKPOINT_VALID

CONFIRM_APPROVAL_GOVERNANCE_COMMIT_VALID
CONFIRM_POST_GOVERNANCE_LOCAL_TRACKING_IDENTITY_GATE_PASSED
CONFIRM_BOUNDED_HELPER_AST_STATIC_GATE_PASSED_ONCE

CONFIRM_FAILURE_OCCURRED_IN_POWERSHELL_LAUNCH_WRAPPER_PARSE
CONFIRM_FAILURE_OCCURRED_BEFORE_ANY_WRAPPER_STATEMENT_EXECUTED
CONFIRM_FAILURE_OCCURRED_BEFORE_PROCESS_START
CONFIRM_BOUNDED_HELPER_PROCESS_STARTS_ZERO
CONFIRM_PRIMARY_AND_ALTERNATE_REMOTE_CALLS_ZERO
CONFIRM_OBSERVER_PARSER_AND_PROCESS_COUNTS_ZERO
CONFIRM_HGRAGC17_AND_RESULT_COUNTS_ZERO

ROOT_CAUSE_ESTABLISHED:
POWERSHELL_EXPANDABLE_STRING_VARIABLE_FOLLOWED_BY_COLON
INVALID_VARIABLE_REFERENCE_WITH_DRIVE

BOUNDED_REMOTE_HELPER_DEFECT_NOT_ESTABLISHED
REMOTE_TRANSPORT_RESULT_NOT_ESTABLISHED
OBSERVER_OR_HGRAGC17_DEFECT_NOT_ESTABLISHED

CURRENT_APPROVAL_GOVERNANCE_CHAIN_TERMINATED
CURRENT_APPROVAL_NOT_REUSABLE

RETURN_FOR_AMENDMENT_5G_B_1_1_1_1_9
TRACKED_AND_PREPARSED_BOUNDED_HELPER_LAUNCHER_ONLY
```

## Accepted Checkpoint

Checkpoint `a740f669d535ab3a148c42f6839de6837eec9c15` is the exact five-path, zero-deletion direct child of approval governance `4d9886be1291133c7a8f94c3a4b35a14f26e0a8d`. The approval-governance commit is the valid exact two-path direct child of package `90438287eeb77c2d383d7073315276a322b5670d`, and its push succeeded.

The post-governance local/tracking/clean/path/source-identity gate and the one bounded-helper AST/static gate passed. The later wrapper parse failure happened before any wrapper statement and before `Process.Start()`. Frozen counts remain bounded-helper starts 0, primary/alternate remote calls 0/0, observer parser/process 0/0, `HGRAGC17` creations 0, result commits/pushes 0/0, and retries 0.

The established root cause is the expandable-string token `$exitCode:`. PowerShell treated the following colon as variable scope/drive syntax and raised `InvalidVariableReferenceWithDrive` while parsing the complete inline wrapper. This establishes a transient orchestration-wrapper defect only; it does not establish a Python helper, remote transport/ref, observer, `HGRAGC17`, or package defect.

## Authorized Package-Assembly Scope

This review authorizes assembly of Amendment 5G-B.1.1.1.1.9 only. Its narrow purpose is to replace the temporary inline wrapper with one tracked and preparsed bounded-helper launcher.

The package does not change:

```text
bounded Python helper
primary or alternate transport policy
1.1.7 command-line observer
HGRAGC17 format
observation result path
```

Package assembly may parse and statically inspect the new launcher. It may not execute the launcher or helper, issue a remote query, parse or execute the observer, or create evidence.

## Tracked Launcher Contract

The tracked launcher is:

```text
scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_9_bounded_remote_gate_launcher.ps1
```

- Source lines / bytes: 184 LF / 7,952
- Source SHA-256: `898BDB48E89CF27A74785D3AD0D67F8F2D129DFDB6FFDF016849C6AFCDB0BC3D`
- Package-stage parser invocations / errors / tokens: 1 / 0 / 1,195
- Package-stage launcher/helper executions / remote calls: 0 / 0 / 0

It freezes its source bytes, LF count, SHA-256, parser result, PowerShell executable and arguments, Python executable and helper arguments, package/approval environment bindings, raw stdout/stderr capture, helper exit gate, and the exact allowed PASS JSON variants.

No expandable string contains an interpolation variable immediately followed by a colon. The launcher contains exactly one helper `Process.Start()` site, concurrently drains raw stdout and stderr, requires helper exit 0 and empty stderr, accepts exactly one strict-UTF-8 LF-terminated canonical PASS JSON line, and forwards only those already-validated stdout bytes. It has no repository-file write API.

## Reused Remote And Observer Contracts

The launcher invokes the unchanged 9,964-byte Amendment 1.1.8 Python helper with the unchanged `-I -B` arguments. Primary remains at most one Git `ls-remote`; alternate remains at most one GitHub REST call only after a registered no-ref transport failure. Same-method retries remain 0 and total remote calls remain at most 2.

Only a remote PASS bound to the actual new approval-governance commit may unlock one observer parser/static gate and at most one unchanged 1.1.7 observer. The result path remains:

```text
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_observation.bin
```

A complete `HGRAGC17` may form one exact one-path result commit and push, followed by immediate independent byte review. An incomplete record or any earlier failure produces no result commit or push.

## Package Boundary

The Amendment 1.1.9 package must be the single direct child of checkpoint `a740f669d535ab3a148c42f6839de6837eec9c15`, change exactly eight paths, delete none, and contain no result file.

The frozen Manifest is 16,536 bytes with SHA-256 `35F4E35E6206DAA6C693F2EA7336A468626B50DC7737E471FBEFA154304D4FF2`.

The package itself authorizes no approval-governance commit, launcher/helper execution, remote call, observer parser/static gate, observer start, `HGRAGC17`, result commit, capture host, nested PRE, POST, FINAL, TERMINAL, synthetic, official, Gold, reservation, or Stage3B action.

## Current State

```text
HARD_FAILURE_22_AUDIT_ACCEPTED
HARD_FAILURE_22_CHECKPOINT_FROZEN
CURRENT_APPROVAL_CHAIN_TERMINATED_AND_NON_REUSABLE
AMENDMENT_5G_B_1_1_1_1_9_TRACKED_PREPARSED_LAUNCHER_PACKAGE_AWAITING_INDEPENDENT_APPROVAL
```
