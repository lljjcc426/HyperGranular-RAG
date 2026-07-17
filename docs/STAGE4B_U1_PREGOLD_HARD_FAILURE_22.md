# Stage4B-U1-D Pre-Gold Hard Failure 22

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Failure date: 2026-07-17
- Amendment 5G-B.1.1.1.1.8 package: `90438287eeb77c2d383d7073315276a322b5670d`
- Hard Failure 21 checkpoint: `c4ac4b90ea57c18502766b5cba288f67cc46e60b`
- Approval governance: `4d9886be1291133c7a8f94c3a4b35a14f26e0a8d`
- Approval-governance direct parent: `90438287eeb77c2d383d7073315276a322b5670d`
- Independent approval attachment bytes: 11,725
- Independent approval attachment SHA-256: `171D7661837A15386B677D9150604DBAF8E32F79461DB5AFDC96363C2F900A43`
- Established failure boundary: `POST_GOVERNANCE_BOUNDED_HELPER_LAUNCH_WRAPPER_POWERSHELL_PARSE_FAILURE_BEFORE_PROCESS_START`
- Other project conversations, thread tools, and global memory used: No

## Valid Approval-Governance Commit

Approval governance `4d9886be1291133c7a8f94c3a4b35a14f26e0a8d` is the single direct child of package `90438287eeb77c2d383d7073315276a322b5670d`. It changed exactly:

```text
AGENTS.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_8_APPROVAL_DECISION.md
```

There were zero deletions. The Approval Decision bound the HF21 checkpoint, 12,757-byte Manifest, 9,964-byte bounded helper, exact helper invocation, primary/alternate policies, deterministic PASS schema, unchanged observer/Manifest/`HGRAGC17`, reused observation path, failure rules, and one-path result contract.

The governance commit was pushed successfully:

```text
To https://github.com/lljjcc426/HyperGranular-RAG.git
   9043828..4d9886b  main -> main
```

## Passed Post-Governance Gates

Without a direct remote query, the local gate confirmed:

```text
HEAD = local main = origin/main tracking
= 4d9886be1291133c7a8f94c3a4b35a14f26e0a8d
worktree clean = true
observation path absent = true
package/helper/observer/Manifest/invocation identities = exact
```

The one authorized bounded-helper AST/static gate then ran once and passed. It verified:

```text
Python runtime = 3.11.5
helper source bytes/LF/SHA = exact
helper invocation identities = exact
subprocess.run calls = 1
urllib Request calls = 1
opener.open calls = 1
remote loops/retry calls = 0
timeout partial-stdout guard = present
authentication rejection before fallback = present
success JSON key set = exact
repository write API = absent
helper execution = 0
remote calls = 0
```

No helper source or static-contract defect was established.

## Exact Failure Boundary

The next authorized action was one in-memory-capture wrapper intended to start the bounded helper. PowerShell parsed the complete wrapper before executing any statement and stopped at this source line:

```text
throw "BOUNDED_HELPER_NONZERO_EXIT:$exitCode:$stderrText"
```

The terminal reported:

```text
Variable reference is not valid. ':' was not followed by a valid variable name character.
Consider using ${} to delimit the name.
FullyQualifiedErrorId : InvalidVariableReferenceWithDrive
```

The exact classification is:

```text
POWERSHELL_LAUNCH_WRAPPER_PARSE_FAILURE
INTERPOLATED_VARIABLE_FOLLOWED_BY_COLON
FAILURE_BEFORE_ANY_WRAPPER_STATEMENT
FAILURE_BEFORE_PROCESS_START
```

Because PowerShell rejected the entire command during parsing, none of its pre-start statements ran and no `System.Diagnostics.Process.Start()` call occurred. The bounded Python helper did not start, so it could not start Git or issue the REST request.

The error text is audit-recorded from terminal output and has no separate raw/log artifact:

```text
AUDIT_RECORDED
NOT_SEPARATELY_DURABLE_BYTE_EVIDENCE
```

No corrected wrapper or post-failure experimental, source, or runtime diagnostic command was executed. Subsequent commands were limited to read-only Git/path state capture and audit-document assembly.

## Frozen Execution Counts

```text
approval-governance commits:             1
approval-governance pushes:              1

post-governance local gates:             1 pass
post-governance helper AST parses:       1 pass
post-governance helper static gates:     1 pass

helper launch-wrapper parse attempts:    1
helper launch-wrapper executions:        0
helper launch-wrapper retries:           0
bounded helper process starts:           0

primary Git remote calls:                0
alternate GitHub REST calls:             0
total remote verification calls:         0
same-method retries:                     0

observer parser invocations:             0
observer static gates:                   0
observer process starts:                 0
capture-host starts:                     0
adapter starts:                          0
parent starts:                           0
loader starts:                           0
target ScriptBlock invocations:          0

HGRAGC17 creations:                      0
result commits:                          0
result pushes:                           0
difference interpretations:              0
```

## Evidence And Inference Boundary

The approved observation path remains absent:

```text
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_observation.bin
```

No remote PASS or failure result exists because neither remote method ran. No `HGRAGC17`, remote attestation, observer output, result commit, or difference interpretation exists.

This failure establishes only the transient PowerShell orchestration wrapper's parse defect. It does not establish:

```text
BOUNDED_HELPER_SOURCE_OR_STATIC_DEFECT
PRIMARY_TRANSPORT_FAILURE_OR_SUCCESS
ALTERNATE_TRANSPORT_FAILURE_OR_SUCCESS
REMOTE_REF_MATCH_OR_MISMATCH
APPROVAL_PUSH_FAILURE
OBSERVER_DEFECT
HGRAGC17_DEFECT
PACKAGE_DEFECT
```

## Fail-Closed Compliance

After the wrapper parse failure:

```text
corrected wrapper attempts: 0
bounded helper starts: 0
remote calls: 0
observer parser/static calls: 0
observer starts: 0
HGRAGC17 creations: 0
result commits/pushes: 0/0
cleanup/overwrite: 0
post-failure experimental diagnostic execution: 0
```

No retry, fallback, runtime substitution, helper/observer source change, capture host, nested child, nested PRE, POST, FINAL, TERMINAL, synthetic rebinding, formal preflight, official execution, Gold, reservation, or Stage3B action followed.

## Authorization Accounting

At the process and call-count level:

```text
BOUNDED_HELPER_PROCESS_AUTHORIZATION_NOT_EXERCISED
PRIMARY_REMOTE_CALL_AUTHORIZATION_NOT_EXERCISED
ALTERNATE_REMOTE_CALL_AUTHORIZATION_NOT_EXERCISED
OBSERVER_PARSER_AUTHORIZATION_NOT_EXERCISED
OBSERVER_PROCESS_AUTHORIZATION_NOT_EXERCISED
```

At the governance level:

```text
CURRENT_APPROVAL_GOVERNANCE_CHAIN_TERMINATED
CURRENT_APPROVAL_NOT_REUSABLE
```

Unspent process and call quotas cannot be separated from the failed ordered gate or transferred into a later attempt.

## Audit-Package Scope

This Hard Failure 22 audit package must be the direct child of approval governance `4d9886be1291133c7a8f94c3a4b35a14f26e0a8d` and change exactly five paths with zero deletions:

```text
AGENTS.md
README.md
docs/REPRODUCIBILITY.md
docs/ROADMAP.md
docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_22.md
```

It contains no result file, helper/observer modification, new Approval Decision, parser output, remote attestation, wrapper source, or post-hoc diagnostic artifact.

## Future Governance Boundary

No corrected-wrapper attempt, helper process, remote query, observer parser/process, or reuse of `4d9886be...` is authorized by this audit. Independent review must first accept the Hard Failure 22 checkpoint.

Any future resumption requires a separately assembled, reviewed, package-bound Amendment and a new approval-governance commit before another process attempt. This audit does not implement or approve that future change.

## Conclusion

```text
HARD_FAILURE_22
POST_GOVERNANCE_BOUNDED_HELPER_LAUNCH_WRAPPER_POWERSHELL_PARSE_FAILURE_BEFORE_PROCESS_START
APPROVAL_GOVERNANCE_COMMIT_VALID
APPROVAL_PUSH_SUCCEEDED
LOCAL_TRACKING_IDENTITY_GATE_PASSED
BOUNDED_HELPER_AST_STATIC_GATE_PASSED_ONCE
BOUNDED_HELPER_NOT_STARTED
PRIMARY_REMOTE_CALLS_ZERO
ALTERNATE_REMOTE_CALLS_ZERO
OBSERVER_PARSER_NOT_RUN
OBSERVER_NOT_STARTED
HGRAGC17_NOT_CREATED
RESULT_COMMIT_ZERO
RESULT_PUSH_ZERO
CURRENT_APPROVAL_CHAIN_TERMINATED_AND_NON_REUSABLE
```

Current state: `AMENDMENT_5G_B_1_1_1_1_8_POST_GOVERNANCE_HELPER_LAUNCH_WRAPPER_PARSE_STOPPED_HARD_FAILURE_22`. The audit package awaits independent review. All experimental execution remains locked.
