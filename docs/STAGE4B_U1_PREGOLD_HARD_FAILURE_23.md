# Stage4B-U1-D Pre-Gold Hard Failure 23

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Failure date: 2026-07-18
- Amendment 5G-B.1.1.1.1.9 package: `046ac17282e1a4dcdedb7f6d744899dedf44d4b5`
- Hard Failure 22 checkpoint: `a740f669d535ab3a148c42f6839de6837eec9c15`
- Approval governance: `ef9ba5b3aabfb0be8deeaf569b46e58c3cdf68aa`
- Approval-governance direct parent: `046ac17282e1a4dcdedb7f6d744899dedf44d4b5`
- Independent approval attachment bytes: 11,908
- Independent approval attachment SHA-256: `32CC9147967054BE1650A5616E2DC436CF88FF2472C515F590720DF53B41D8BD`
- Established failure boundary: `POST_GOVERNANCE_TRACKED_LAUNCHER_NONZERO_EXIT_WITH_ZERO_STDOUT_AND_503_BYTE_NON_DURABLE_STDERR`
- Other project conversations, thread tools, and global memory used: No

## Valid Approval-Governance Commit

Approval governance `ef9ba5b3aabfb0be8deeaf569b46e58c3cdf68aa` is the single direct child of package `046ac17282e1a4dcdedb7f6d744899dedf44d4b5`. It changed exactly:

```text
AGENTS.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_9_APPROVAL_DECISION.md
```

There were zero deletions. The Approval Decision bound the HF22 checkpoint, 16,536-byte Manifest, 7,952-byte tracked launcher, unchanged 9,964-byte helper, unchanged observer and observer Manifest, exact launcher/helper invocations, remote policy, PASS contract, failure rules, and single-path result contract.

The governance commit was pushed successfully:

```text
To https://github.com/lljjcc426/HyperGranular-RAG.git
   046ac17..ef9ba5b  main -> main
```

## Passed Post-Governance Gates

Without a direct remote query, the local gate confirmed:

```text
HEAD = local main = origin/main tracking
= ef9ba5b3aabfb0be8deeaf569b46e58c3cdf68aa
worktree clean = true
observation path absent = true
approval changed paths = 2
approval deletions = 0
package/launcher/helper/observer/Manifest/invocation identities = exact
```

The one authorized tracked-launcher parser/static gate then passed:

```text
PowerShell parser invocations = 1
parser errors = 0
tokens = 1,195
launcher source bytes/LF/SHA = exact
helper Start sites = 1 and outside loops
raw CopyToAsync drains = 2
WaitForExit calls = 1
WaitAll calls = 1
interpolation-variable-followed-by-colon tokens = 0
repository write API = absent
launcher/helper/remote/observer/evidence executions = 0
```

The one authorized helper AST/static gate also passed:

```text
Python runtime = 3.11.5
AST parses = 1
helper source bytes/LF/SHA = exact
subprocess.run calls = 1
urllib Request calls = 1
opener.open calls = 1
remote calls in loops = 0
repository write API = absent
helper execution = 0
remote calls = 0
```

No tracked-launcher or helper static defect was established by these gates.

## Exact Authorized Attempt And Failure Boundary

After both gates passed, the exact frozen tracked-launcher command was started once with package binding `046ac17282e1a4dcdedb7f6d744899dedf44d4b5` and approval binding `ef9ba5b3aabfb0be8deeaf569b46e58c3cdf68aa`.

The outer executor waited for the launcher and recorded:

```text
tracked launcher process starts = 1
tracked launcher exit code = 1
tracked launcher stdout bytes = 0
tracked launcher stderr bytes = 503
outer PASS gate = failed
terminal classification = TRACKED_LAUNCHER_NONZERO_EXIT_1_STDOUT_BYTES_0_STDERR_BYTES_503
```

The 503 stderr bytes were captured only in process memory. They were not written to a registered raw/log path and were not preserved as durable byte evidence. The audit therefore records only the byte count and terminal classification; it does not reconstruct, quote, hash, classify, or infer the missing stderr content.

The available evidence does not establish whether the launcher failed before starting the helper or after the helper started. Consequently, the helper process count and all remote-call counts are unconfirmed. The failure must not be relabeled as a helper failure, primary or alternate transport failure, remote-ref mismatch, PASS-framing defect, launcher source defect, or package defect.

Because the outer PASS gate failed, the observer parser/static gate and observer process were not invoked. The registered `HGRAGC17` path remained absent.

No second launcher, direct helper bypass, remote query, observer action, or post-failure experimental diagnostic command followed. Subsequent commands were limited to read-only Git/path state capture and audit-document assembly.

## Frozen Execution Counts

```text
approval-governance commits:             1
approval-governance pushes:              1

post-governance local gates:             1 pass
post-governance launcher parser gates:   1 pass
post-governance helper AST gates:        1 pass

tracked launcher process starts:         1
tracked launcher retries:                0
tracked launcher exit code:              1
tracked launcher stdout bytes:           0
tracked launcher stderr bytes:           503
launcher PASS results:                   0

bounded helper process starts:           UNCONFIRMED
primary Git remote calls:                UNCONFIRMED
alternate GitHub REST calls:             UNCONFIRMED
total remote verification calls:         UNCONFIRMED
same-method remote retries:              UNCONFIRMED

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

The zero launcher retry is directly established by the single outer process attempt. It does not convert unknown helper or remote activity inside that process into zero.

## Evidence And Inference Boundary

The approved observation path remains absent:

```text
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_observation.bin
```

No durable launcher stdout/stderr record, remote attestation, `HGRAGC17`, observer output, result commit, or difference interpretation exists.

This failure establishes only:

```text
ONE_TRACKED_LAUNCHER_PROCESS_STARTED
TRACKED_LAUNCHER_EXITED_1
TRACKED_LAUNCHER_STDOUT_WAS_0_BYTES
TRACKED_LAUNCHER_STDERR_WAS_503_BYTES_BUT_NOT_DURABLY_PRESERVED
OUTER_PASS_GATE_FAILED
OBSERVER_WAS_NOT_REACHED
```

It does not establish:

```text
LAUNCHER_EXACT_ERROR_TEXT_OR_ERROR_CLASS
FAILURE_BEFORE_OR_AFTER_HELPER_START
BOUNDED_HELPER_PROCESS_COUNT
PRIMARY_OR_ALTERNATE_REMOTE_CALL_COUNTS
REMOTE_TRANSPORT_OR_REF_OUTCOME
PASS_JSON_OR_FRAMING_ROOT_CAUSE
LAUNCHER_OR_HELPER_SOURCE_DEFECT
OBSERVER_OR_HGRAGC17_DEFECT
PACKAGE_DEFECT
```

## Fail-Closed Compliance

After the tracked launcher returned nonzero:

```text
second launcher attempts: 0
direct helper-bypass attempts: 0
observer parser/static calls: 0
observer starts: 0
HGRAGC17 creations: 0
result commits/pushes: 0/0
cleanup/overwrite: 0
post-failure experimental diagnostic execution: 0
```

No retry, alternate launcher, inline wrapper, source change, raw reconstruction, cleanup, nested child continuation, nested PRE, POST, FINAL, TERMINAL, synthetic rebinding, formal preflight, official execution, Gold, reservation, or Stage3B action followed.

## Authorization Accounting

At the governance level:

```text
CURRENT_APPROVAL_GOVERNANCE_CHAIN_TERMINATED
CURRENT_APPROVAL_NOT_REUSABLE
```

Because helper and remote activity inside the terminated launcher was not durably observed, their quota consumption cannot be reconstructed or transferred. The observer parser/process quotas were not exercised, but they cannot be detached from the failed ordered gate or reused.

## Audit-Package Scope

This Hard Failure 23 audit package must be the direct child of approval governance `ef9ba5b3aabfb0be8deeaf569b46e58c3cdf68aa` and change exactly five paths with zero deletions:

```text
AGENTS.md
README.md
docs/REPRODUCIBILITY.md
docs/ROADMAP.md
docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_23.md
```

It contains no result file, launcher/helper/observer modification, new Approval Decision, parser output, reconstructed stderr, remote attestation, or post-hoc diagnostic artifact.

## Future Governance Boundary

No second launcher, direct helper execution, remote query, observer parser/process, or reuse of `ef9ba5b3...` is authorized by this audit. Independent review must first accept the Hard Failure 23 checkpoint.

Any future resumption requires a separately assembled, reviewed, package-bound Amendment and a new approval-governance commit. A future design may address durable outer-process evidence, but this audit neither diagnoses the missing stderr nor implements or approves a correction.

## Conclusion

```text
HARD_FAILURE_23
POST_GOVERNANCE_TRACKED_LAUNCHER_NONZERO_EXIT_WITH_ZERO_STDOUT_AND_503_BYTE_NON_DURABLE_STDERR
APPROVAL_GOVERNANCE_COMMIT_VALID
APPROVAL_PUSH_SUCCEEDED
LOCAL_TRACKING_IDENTITY_GATE_PASSED
TRACKED_LAUNCHER_PARSER_STATIC_GATE_PASSED_ONCE
BOUNDED_HELPER_AST_STATIC_GATE_PASSED_ONCE
TRACKED_LAUNCHER_STARTED_ONCE
TRACKED_LAUNCHER_EXIT_1
TRACKED_LAUNCHER_STDOUT_BYTES_0
TRACKED_LAUNCHER_STDERR_BYTES_503_NOT_DURABLY_PRESERVED
HELPER_AND_REMOTE_COUNTS_UNCONFIRMED
OBSERVER_PARSER_NOT_RUN
OBSERVER_NOT_STARTED
HGRAGC17_NOT_CREATED
RESULT_COMMIT_ZERO
RESULT_PUSH_ZERO
CURRENT_APPROVAL_CHAIN_TERMINATED_AND_NON_REUSABLE
```

Current state: `AMENDMENT_5G_B_1_1_1_1_9_TRACKED_LAUNCHER_NONZERO_STOPPED_HARD_FAILURE_23`. The audit package awaits independent review. All experimental execution remains locked.
