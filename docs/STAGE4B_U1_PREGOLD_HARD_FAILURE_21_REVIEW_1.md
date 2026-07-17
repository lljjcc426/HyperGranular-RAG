# Stage4B-U1-D Pre-Gold Hard Failure 21 Review 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review date: 2026-07-17
- Hard Failure 21 checkpoint: `c4ac4b90ea57c18502766b5cba288f67cc46e60b`
- Consumed approval governance: `f5a9ce38d10d419f8bc92772030f0d7cb77914cb`
- Amendment 1.1.7 package: `8e274060baf844dd1d761e7635bbc6c43ef9d4b6`
- Independent review attachment bytes: 8,977
- Independent review attachment SHA-256: `8D7941DEAFC3014F97EC60F261879CA57167B4EADD2CEA7C0D7E0E8CEE2D0771`
- Other project conversations, thread tools, and global memory used: No

## Independent Review Decision

```text
ACCEPT_HARD_FAILURE_21_AUDIT
CONFIRM_HARD_FAILURE_21_CHECKPOINT_VALID
CONFIRM_APPROVAL_GOVERNANCE_COMMIT_VALID
CONFIRM_APPROVAL_GOVERNANCE_PUSH_SUCCEEDED
CONFIRM_POST_GOVERNANCE_DIRECT_GITHUB_QUERY_ATTEMPTED_ONCE
CONFIRM_DIRECT_QUERY_RETURNED_NO_REMOTE_REF
CONFIRM_FAILURE_CLASS_IS_TLS_TRANSPORT_FAILURE
CONFIRM_REMOTE_REF_MISMATCH_NOT_ESTABLISHED
CONFIRM_PUSH_FAILURE_NOT_ESTABLISHED
CONFIRM_PARSER_INVOCATIONS_ZERO
CONFIRM_STATIC_OBSERVER_GATES_ZERO
CONFIRM_OBSERVER_STARTS_ZERO
CONFIRM_ALL_CHILD_STARTS_ZERO
CONFIRM_HGRAGC17_CREATIONS_ZERO
CONFIRM_RESULT_COMMITS_AND_PUSHES_ZERO
CONFIRM_NO_RETRY_OR_POST_FAILURE_DIAGNOSTIC

RETURN_FOR_AMENDMENT_5G_B_1_1_1_1_8
BOUNDED_REMOTE_VERIFICATION_TRANSPORT_POLICY_ONLY
```

## Accepted Checkpoint

Checkpoint `c4ac4b90ea57c18502766b5cba288f67cc46e60b` is the exact five-path, zero-deletion direct child of approval governance `f5a9ce38d10d419f8bc92772030f0d7cb77914cb`. The failure remains a direct-query TLS transport failure that returned no ref. Remote mismatch, wrong SHA, push failure, and package/observer defect remain unestablished.

The frozen execution counts remain parser 0, static observer gate 0, observer and all child starts 0, `HGRAGC17` creation 0, result commit/push 0, and retry 0. The observer process quota was not exercised, but the terminated approval chain is non-reusable.

## Authorized Package-Assembly Scope

This review authorizes assembly of Amendment 5G-B.1.1.1.1.8 only. Its narrow purpose is a bounded remote-verification transport policy for future command-line diagnostic governance.

The package may add one helper that freezes:

```text
primary Git ls-remote call maximum:       1
conditional alternate GitHub REST call:  1
total remote calls maximum:              2
same-method retry maximum:               0
```

Package assembly may parse and statically inspect the new helper but may not execute it or issue either remote query.

## Design Choice: Preserve The Observer

No independent observer-source defect was found. Amendment 1.1.8 therefore keeps the existing 1.1.7 observer, Manifest contract, `HGRAGC17` bytes, invocation, and still-absent observation path unchanged. This follows the review's allowed compatibility option and avoids changing the observer solely to rename a path.

The old approval chain owns no result because the path was never created. A future 1.1.8 package-bound approval may rebind the unchanged path only through the new package and a new approval-governance commit.

## Bounded Transport Policy

Primary is the fixed Git executable and exact `ls-remote --heads` query. It may transition to alternate only after one of four registered transport classes before any ref is returned:

```text
TLS_CONNECT_FAILURE
DNS_RESOLUTION_FAILURE
CONNECTION_RESET_BEFORE_REF
HTTP_TRANSPORT_UNAVAILABLE
```

Alternate is an unauthenticated, read-only Python `urllib` request to GitHub's official single-reference REST endpoint. It disables proxies and redirects, fixes the API version and response size, requires strict UTF-8 and duplicate-key-free JSON, and accepts only exact `refs/heads/main` plus a lowercase 40-character commit SHA.

No alternate is allowed after a returned SHA mismatch, multiple/ambiguous refs, repository/ref identity mismatch, authentication/authorization rejection, malformed response, or an unregistered primary failure.

## No Attestation File

The package uses the review's narrower no-attestation option. Remote-gate success creates no repository file. Any failure stops before the observer and must later be represented only by a separately governed Hard Failure audit; no post-hoc transport evidence may be fabricated.

## Package Boundary

The Amendment 1.1.8 package must be the single direct child of checkpoint `c4ac4b90ea57c18502766b5cba288f67cc46e60b`, change exactly eight paths, delete none, and contain no result file.

The frozen Manifest is 12,757 bytes with SHA-256 `672FBD0CCE7A43C747645FEC43ABFA4C1EF85084E5164F840F15EE67ECBFDC75`.

The package itself authorizes no approval governance, helper execution, remote call, observer parser/static gate, observer start, `HGRAGC17`, result commit, capture host, nested PRE, official operation, Gold, reservation, or Stage3B.

## Current State

```text
HARD_FAILURE_21_AUDIT_ACCEPTED
HARD_FAILURE_21_CHECKPOINT_FROZEN
CURRENT_APPROVAL_CHAIN_TERMINATED_AND_NON_REUSABLE
AMENDMENT_5G_B_1_1_1_1_8_BOUNDED_REMOTE_TRANSPORT_PACKAGE_AWAITING_INDEPENDENT_APPROVAL
```
