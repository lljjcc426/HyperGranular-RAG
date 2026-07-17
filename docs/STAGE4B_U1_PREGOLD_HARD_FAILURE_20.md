# Stage4B-U1-D Pre-Gold Hard Failure 20

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Failure date: 2026-07-17
- Independent audit date: 2026-07-17
- Corrected Amendment 5G-B.1.1.1.1.6 package: `0efbea018f4ad0e8650e254d313fb9cc85d2a28c`
- Approval governance: `1eb73132d47d5b21fceca9c88a42607ee3dff98d`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6_MANIFEST.json`
- Manifest bytes: 17,536
- Manifest SHA-256: `6C5E027B4B4F337B3CB61BDD381F00715D284B3269B5F39F0BE3A2E75259BAC5`
- Established failure boundary: `PRE_NESTED_OBSERVER_ACTUAL_PROCESS_COMMAND_LINE_MISMATCH`
- Exact actual-versus-modeled difference: `UNCONFIRMED`
- PRE observer processes: 1
- PRE capture-host/adapter/parent/loader processes: 0/0/0/0
- Target ScriptBlock invocations: 0
- New raw and semantics creations: 0
- Automatic retries: 0
- Independent audit attachment bytes: 7,645
- Independent audit attachment SHA-256: `21B9D96526492BDDF51C96D8C9F109200471F0F674A70ECA7181F2921FA657A3`
- Other project conversations, thread tools, and global memory used: No

## Independent Audit Decision

The user-supplied independent audit accepted the PRE diagnostic failure boundary and confirmed all of the following:

```text
ACCEPT_PRE_DIAGNOSTIC_FAILURE_BOUNDARY
CONFIRM_APPROVAL_GOVERNANCE_COMMIT_VALID
CONFIRM_POST_GOVERNANCE_STATIC_GATE_126_OF_126
CONFIRM_EXACTLY_ONE_PRE_OBSERVER_PROCESS_EXECUTED
CONFIRM_FAILURE_OCCURRED_AT_OBSERVER_ACTUAL_COMMAND_LINE_GATE
CONFIRM_FAILURE_OCCURRED_BEFORE_CAPTURE_HOST_PROCESS_START
CONFIRM_FAILURE_OCCURRED_BEFORE_ALL_NEW_RAW_CREATENEW_OPERATIONS
CONFIRM_FAILURE_BRANCH_ZERO_COMMIT_ZERO_PUSH_COMPLIANCE
CONFIRM_NO_RETRY_AND_NO_POST_FAILURE_DIAGNOSTIC_EXECUTION
```

The consumed approval is not reusable. The authorized next step is this separately governed Hard Failure 20 audit package, not an observer change or PRE retry.

## Approval-Governance And Static Gates

Approval governance `1eb73132d47d5b21fceca9c88a42607ee3dff98d` is the direct child of corrected package `0efbea018f4ad0e8650e254d313fb9cc85d2a28c`. It changed exactly:

```text
AGENTS.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6_APPROVAL_DECISION.md
```

There were zero deletions. The governance commit was pushed before any frozen-source execution. Local `HEAD`, local `main`, tracked `origin/main`, and direct GitHub `main` then matched the governance commit; the worktree was clean and all six result paths were absent.

The approved post-governance read-only static gate passed:

```text
source/Manifest/invocation/stdout registry: 56/56
four-boundary durable ordering:            36/36
binary/path/prior-HF19:                     24/24
Package Review 1 blockers:                  10/10
total:                                     126/126

frozen process starts: 0
evidence writes: 0
dot-sources: 0
raw verifier executions: 0
```

## Single Authorized PRE Observer Execution

The observer process was started exactly once with the package and approval-governance bindings:

```text
HGRAG_EXPECTED_PACKAGE_COMMIT=0efbea018f4ad0e8650e254d313fb9cc85d2a28c
HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT=1eb73132d47d5b21fceca9c88a42607ee3dff98d
```

It exited with code 1 at:

```text
PRE nested observer actual process command line mismatch
```

The failing source gate was:

```powershell
if (([Environment]::CommandLine + [char]0) -cne $selfModeled) {
    throw 'PRE nested observer actual process command line mismatch'
}
```

The observer was not retried.

## Frozen Process Boundary

The registered observer order reconstructs and validates its own arguments and modeled command line, then compares the actual command line, and only afterward reconstructs the capture-host invocation and creates/starts the capture-host process.

The failure therefore freezes these counts:

```text
PRE observer process:              1
PRE capture-host process:          0
PRE adapter process:               0
PRE parent process:                0
PRE loader process:                0
target ScriptBlock invocation:     0
```

This was not a capture-host, adapter, parent, loader, target, or semantics runtime failure.

## Evidence-Preservation Boundary

The actual-command-line gate precedes the new raw path-collision loop, capture-host `Process.Start()`, raw stream drains, and `HGRAGO16 CreateNew`. Consequently none of the six result paths was created:

```text
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_VALIDATOR_SEMANTICS_AUDIT.md
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_validator_semantics.json
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_pre_capture_outer_observation.bin
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_pre_adapter_child_observation.bin
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_pre_parent_child_observation.bin
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_pre_loader_child_observation.bin
```

The immutable Hard Failure 19 raw remains:

```text
path:
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_5_pre_capture_outer_observation.bin

bytes:
520

SHA-256:
4ABEB26000DDC77E8293DB1616682E6748E2290A9608959A2A040B1CD2780A70
```

No post-failure raw, command-line observation, or substitute machine file was fabricated.

## Established And Unestablished Facts

Established:

```text
one PRE observer process started
the observer reached its actual-command-line equality gate
the gate raised the registered mismatch error
observer exit code was 1
capture host did not start
all four new raw paths and both semantics paths remained absent
```

Unestablished:

```text
exact [Environment]::CommandLine characters
actual command-line character count or SHA-256
first actual-versus-modeled differing character
whether the difference arose from executable quoting, path representation,
argument escaping, PowerShell normalization, separator modeling, terminal NUL,
or another character-level cause
```

The exact boundary is therefore `PRE_NESTED_OBSERVER_ACTUAL_PROCESS_COMMAND_LINE_MISMATCH`. Neither a package-source defect nor a nested-transport defect is established.

## Machine-Evidence Classification

The observer exit and error text are recorded by this audit from the accepted execution boundary:

```text
AUDIT_RECORDED
NOT_SEPARATELY_DURABLE_BYTE_EVIDENCE
```

Because the observer did not persist actual and modeled command-line bytes before comparing them, this audit must not reconstruct those bytes after the fact or represent any hypothesized difference as machine evidence.

## Fail-Closed Compliance

The approved failure branch was followed:

```text
result commits: 0
result pushes: 0
retry: 0
standalone raw verifier: 0
post-failure source reconstruction or diagnostic execution: 0
POST/FINAL/TERMINAL: 0
```

There was no cleanup, fallback, alternate observer, source/runtime substitution, partial continuation, synthetic rebinding, real precommit validator, formal preflight, official execution, Gold, reservation, or Stage3B action.

## Future Governance Boundary

No Amendment 5G-B.1.1.1.1.7 implementation or execution is authorized by this audit package. A future separately approved package may propose an observer-command-line-only diagnostic that durably records actual and modeled UTF-16LE bytes before equality checking, does not start the capture host, and stops for independent review. Until such a package and a new package-bound approval exist, all frozen-source execution remains prohibited.

## Conclusion

```text
HARD_FAILURE_20
PRE_OBSERVER_ACTUAL_COMMAND_LINE_GATE_FAILED
OBSERVER_EXIT_1
CAPTURE_HOST_NOT_STARTED
ALL_NEW_RAW_PATHS_ABSENT
ALL_SEMANTICS_PATHS_ABSENT
EXACT_COMMAND_LINE_DIFFERENCE_UNRECOVERED
PACKAGE_SOURCE_DEFECT_NOT_ESTABLISHED
NESTED_TRANSPORT_DEFECT_NOT_ESTABLISHED
CURRENT_APPROVAL_CONSUMED_AND_NON_REUSABLE
```

Current state: `AMENDMENT_5G_B_1_1_1_1_6_PRE_OBSERVER_ACTUAL_COMMAND_LINE_GATE_STOPPED_HARD_FAILURE_20`. Independent review and a separately governed Amendment/package-bound approval are required before any further frozen-source execution.
