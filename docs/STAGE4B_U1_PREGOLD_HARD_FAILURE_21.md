# Stage4B-U1-D Pre-Gold Hard Failure 21

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Failure date: 2026-07-17
- Independent audit date: 2026-07-17
- Amendment 5G-B.1.1.1.1.7 package: `8e274060baf844dd1d761e7635bbc6c43ef9d4b6`
- Approval governance: `f5a9ce38d10d419f8bc92772030f0d7cb77914cb`
- Approval-governance direct parent: `8e274060baf844dd1d761e7635bbc6c43ef9d4b6`
- Established failure boundary: `POST_GOVERNANCE_DIRECT_GITHUB_MAIN_QUERY_TLS_CONNECT_FAILURE`
- Independent audit attachment bytes: 6,919
- Independent audit attachment SHA-256: `20233E8D330C6F62FCF61C6FD08AF1F028A43B7F34EA768D8877863377EBDF7E`
- Other project conversations, thread tools, and global memory used: No

## Independent Audit Decision

The user-supplied independent audit accepted the post-governance remote-gate hard failure and confirmed:

```text
ACCEPT_POST_GOVERNANCE_REMOTE_GATE_HARD_FAILURE
CONFIRM_APPROVAL_GOVERNANCE_COMMIT_VALID
CONFIRM_APPROVAL_COMMIT_EXACT_TWO_PATH_SCOPE
CONFIRM_APPROVAL_COMMIT_PUSHED
CONFIRM_FAILURE_OCCURRED_AT_POST_GOVERNANCE_DIRECT_GITHUB_MAIN_QUERY
CONFIRM_FAILURE_OCCURRED_BEFORE_PARSER_INVOCATION
CONFIRM_FAILURE_OCCURRED_BEFORE_OBSERVER_PROCESS_START
CONFIRM_HGRAGC17_CREATIONS_ZERO
CONFIRM_RESULT_COMMITS_AND_PUSHES_ZERO
CONFIRM_NO_RETRY_AND_FAIL_CLOSED_STOP
```

The current approval-governance chain is terminated and non-reusable. The observer process quota was not exercised, but that fact does not authorize continuation after network recovery.

## Valid Approval-Governance Commit

Approval governance `f5a9ce38d10d419f8bc92772030f0d7cb77914cb` is the single direct child of package `8e274060baf844dd1d761e7635bbc6c43ef9d4b6`. It changed exactly:

```text
AGENTS.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_7_APPROVAL_DECISION.md
```

There were zero deletions. The Approval Decision correctly bound the package/checkpoint, 13,336-byte Manifest, 5,603-byte observer, frozen invocation, modeled command, `HGRAGC17` contract, zero-child boundary, and one-path result contract.

The governance commit was pushed successfully:

```text
To https://github.com/lljjcc426/HyperGranular-RAG.git
   8e27406..f5a9ce3  main -> main
```

The independent reviewer later verified through a separate GitHub connector that remote `main` pointed to `f5a9ce38...`. That later observation establishes neither success of the failed query nor permission to continue the terminated approval chain.

## Exact Failure Boundary

After the governance push, the ordered post-governance gate attempted to establish local `HEAD`, local `main`, `origin/main`, direct GitHub `main`, clean worktree, and observation-path absence before parser invocation.

The direct GitHub query failed at transport:

```text
fatal: unable to access 'https://github.com/lljjcc426/HyperGranular-RAG.git/':
TLS connect error: error:00000000:lib(0)::reason(0)
```

The exact classification is:

```text
DIRECT_GITHUB_MAIN_QUERY_TRANSPORT_FAILURE
TLS_CONNECT_ERROR_DURING_DIRECT_GITHUB_MAIN_QUERY
```

Because the query returned no remote ref, it did not establish any SHA comparison. Therefore none of the following is established:

```text
DIRECT_GITHUB_MAIN_MISMATCH
REMOTE_MAIN_WRONG_SHA
APPROVAL_PUSH_FAILED
PACKAGE_OR_OBSERVER_DEFECT
```

The error text is audit-recorded from the failed command output and has no separate raw/log artifact:

```text
AUDIT_RECORDED
NOT_SEPARATELY_DURABLE_BYTE_EVIDENCE
```

No post-failure TLS log or substitute remote-diagnostic file was fabricated.

## Frozen Execution Counts

```text
approval-governance commits:      1
approval-governance pushes:       1

direct GitHub gate attempts:      1
direct GitHub gate successes:     0
direct GitHub gate retries:       0

PowerShell parser invocations:    0
static observer gates:            0
observer process starts:          0
capture-host starts:              0
adapter starts:                   0
parent starts:                    0
loader starts:                    0
target ScriptBlock invocations:   0

HGRAGC17 creations:               0
result commits:                   0
result pushes:                    0
difference interpretations:       0
```

The failure occurred before any parser invocation, source execution, observer process, output `CreateNew`, or difference calculation.

## Observation And Evidence Boundary

The only approved observation path remained absent when the governance chain stopped:

```text
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_observation.bin
```

No `HGRAGC17`, parser output, observer stdout/stderr evidence, TLS diagnostic file, or result commit exists. The observer source and package were not demonstrated defective. Actual and modeled command-line bytes remain unobserved in this chain, and their difference type remains `NOT_YET_INTERPRETED`.

## Fail-Closed Compliance

The approved failure rule was followed exactly:

```text
direct GitHub query retries: 0
parser invocations: 0
observer starts: 0
capture host or nested child starts: 0
HGRAGC17 creations: 0
result commits: 0
result pushes: 0
post-failure diagnostic execution: 0
```

No retry, fallback query, parser, observer, capture host, cleanup, overwrite, source change, runtime substitution, nested PRE continuation, POST, FINAL, TERMINAL, synthetic rebinding, formal preflight, official execution, Gold, reservation, or Stage3B action followed.

## Authorization Accounting

At the process-count level:

```text
OBSERVER_PROCESS_AUTHORIZATION_NOT_EXERCISED
OBSERVER_PROCESS_STARTS_ZERO
```

At the governance level:

```text
CURRENT_APPROVAL_GOVERNANCE_CHAIN_TERMINATED
CURRENT_APPROVAL_NOT_REUSABLE
```

The unspent process quota cannot be separated from the failed ordered gate or transferred into a later attempt.

## Audit-Package Scope

This Hard Failure 21 audit package must be the direct child of approval governance `f5a9ce38d10d419f8bc92772030f0d7cb77914cb` and change exactly five paths with zero deletions:

```text
AGENTS.md
README.md
docs/REPRODUCIBILITY.md
docs/ROADMAP.md
docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_21.md
```

It contains no `HGRAGC17`, observer modification, new Approval Decision, parser output, or post-hoc remote diagnostic artifact.

## Future Governance Boundary

No remote-gate retry, parser invocation, observer execution, or reuse of `f5a9ce38...` is authorized by this audit. Independent review must first accept the Hard Failure 21 checkpoint.

A future separately assembled Amendment may propose a bounded and preregistered remote-verification transport policy with one fixed primary query, one explicitly approved alternate read-only query, exact maximum call counts, a narrow transport-error transition condition, and immediate stop on any ref mismatch. Such a policy is only a future design suggestion; it is not implemented or approved here.

## Conclusion

```text
HARD_FAILURE_21
POST_GOVERNANCE_DIRECT_GITHUB_MAIN_QUERY_TLS_CONNECT_FAILURE
APPROVAL_GOVERNANCE_COMMIT_VALID
APPROVAL_PUSH_SUCCEEDED
REMOTE_REF_MISMATCH_NOT_ESTABLISHED
PUSH_FAILURE_NOT_ESTABLISHED
PARSER_NOT_RUN
OBSERVER_NOT_STARTED
HGRAGC17_NOT_CREATED
RESULT_COMMIT_ZERO
RESULT_PUSH_ZERO
OBSERVER_PROCESS_QUOTA_UNSPENT
CURRENT_APPROVAL_CHAIN_TERMINATED_AND_NON_REUSABLE
```

Current state: `AMENDMENT_5G_B_1_1_1_1_7_POST_GOVERNANCE_DIRECT_GITHUB_QUERY_STOPPED_HARD_FAILURE_21`. The audit package awaits independent review. All experimental execution remains locked.
