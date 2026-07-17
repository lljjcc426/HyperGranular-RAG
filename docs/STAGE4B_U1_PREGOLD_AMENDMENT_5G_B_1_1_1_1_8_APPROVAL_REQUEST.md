# Stage4B U1-D Pre-Gold Amendment 5G-B.1.1.1.1.8 Approval Request

## Request

```text
REQUEST_APPROVAL_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_8
BOUNDED_REMOTE_VERIFICATION_TRANSPORT_POLICY_FOR_COMMAND_LINE_DIAGNOSTIC_GOVERNANCE_ONLY

ONE_NEW_PACKAGE_BOUND_APPROVAL_GOVERNANCE_COMMIT_REQUESTED
ONE_BOUNDED_REMOTE_GATE_HELPER_PROCESS_REQUESTED
ONE_PRIMARY_GIT_REMOTE_QUERY_REQUESTED
AT_MOST_ONE_CONDITIONAL_GITHUB_REST_QUERY_REQUESTED
SAME_METHOD_RETRY_ZERO_REQUIRED
ONE_POST_REMOTE_SUCCESS_OBSERVER_PARSER_STATIC_GATE_REQUESTED
ONE_COMMAND_LINE_DIAGNOSTIC_OBSERVER_PROCESS_REQUESTED
ONE_HGRAGC17_RESULT_REQUESTED
ONE_EXACT_ONE_PATH_RESULT_COMMIT_AND_PUSH_REQUESTED

CAPTURE_HOST_AND_ALL_NESTED_CHILD_STARTS_ZERO_REQUIRED
IMMEDIATE_STOP_FOR_INDEPENDENT_BYTE_REVIEW_REQUIRED
```

This package requests future authorization only. It does not authorize any approval-governance commit, helper execution, remote call, observer parser, observer process, evidence creation, result commit, or downstream action.

## Binding Lineage

- Hard Failure 21 checkpoint: `c4ac4b90ea57c18502766b5cba288f67cc46e60b`
- Consumed and non-reusable approval governance: `f5a9ce38d10d419f8bc92772030f0d7cb77914cb`
- Amendment 1.1.7 package: `8e274060baf844dd1d761e7635bbc6c43ef9d4b6`
- Hard Failure 21 audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_21.md`
- Hard Failure 21 Review 1: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_21_REVIEW_1.md`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_8_MANIFEST.json`
- Manifest bytes: 12,757
- Manifest SHA-256: `672FBD0CCE7A43C747645FEC43ABFA4C1EF85084E5164F840F15EE67ECBFDC75`

The future approval must bind the actual Amendment 1.1.8 package commit. Neither `f5a9ce38...` nor its unexercised observer process quota may be reused.

## New Bounded Remote-Gate Helper

- Path: `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_8_bounded_remote_gate.py`
- Lines: 294 LF
- Bytes: 9,964
- Encoding: ASCII-compatible UTF-8 without BOM
- SHA-256: `7EBC6F40C58D479774B6C083157E5ECB429E02ED0B261FCECF1ADB58551C4567`
- Package-stage Python AST parser invocations: 4
- Package-stage helper executions: 0
- Package-stage remote calls: 0
- Package-stage read-only helper failures: 3 (`rg.exe` start access denied; PowerShell empty-pipe parse failure before file read; PowerShell `H`/`Get-History` alias collision during final read-only validation)

Both failed helper attempts performed zero project writes, bounded-helper/observer executions, remote calls, or evidence creation. Corrected PowerShell-only checks completed without expanding the package scope.

Frozen helper invocation:

```text
C:\ProgramData\anaconda3\python.exe
-I -B scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_8_bounded_remote_gate.py
```

- Arguments characters / ASCII bytes: 82 / 82
- Arguments ASCII SHA-256: `D3529D3449AD623A811FC93F64DC4BB1251CA16DE4439E7F985039431800440E`
- Arguments UTF-16LE bytes: 164
- Arguments UTF-16LE SHA-256: `BF32888752D6119FAA82E0E5EBD03AF4F794EC584392D9A4D108107B38D3682C`

The helper requires these process-scoped bindings:

```text
HGRAG_EXPECTED_PACKAGE_COMMIT=<actual Amendment 1.1.8 package commit>
HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT=<actual new approval-governance commit>
```

## Primary Transport

The primary call is fixed to exactly one process invocation:

```text
C:\Program Files\Git\cmd\git.exe
ls-remote --heads https://github.com/lljjcc426/HyperGranular-RAG.git refs/heads/main
```

Its maximum call count is 1. A successful response must have exit 0, empty stderr, and exactly one strict UTF-8 line:

```text
<40-character lowercase SHA><TAB>refs/heads/main
```

The SHA must equal the actual new approval-governance commit. Any returned mismatch, extra/multiple line, noncanonical ref, malformed SHA, or nonempty success stderr is an immediate hard stop with zero alternate calls.

## Conditional Alternate Transport

Alternate is allowed only when primary exits without a ref and matches exactly one registered transport class:

```text
TLS_CONNECT_FAILURE
DNS_RESOLUTION_FAILURE
CONNECTION_RESET_BEFORE_REF
HTTP_TRANSPORT_UNAVAILABLE
```

It uses Python `urllib`, not Git, with one unauthenticated GET to:

```text
https://api.github.com/repos/lljjcc426/HyperGranular-RAG/git/ref/heads/main
```

Headers are fixed to GitHub JSON, identity encoding, a package-specific user agent, and API version `2026-03-10`. Proxy use and redirects are disabled. Timeout is 30 seconds and response size is capped at 65,536 bytes.

GitHub's official documentation identifies this endpoint as returning one reference, permits unauthenticated access for public resources, recommends `application/vnd.github+json`, and returns `ref` plus `object.type`/`object.sha`: https://docs.github.com/en/rest/git/refs#get-a-reference

The response must be HTTP 200, strict UTF-8, duplicate-key-free JSON, exact `refs/heads/main`, object type `commit`, and a lowercase 40-character SHA equal to the new approval-governance commit.

## Alternate-Forbidden Outcomes

The helper must not enter alternate after:

```text
PRIMARY_REMOTE_REF_SHA_MISMATCH
PRIMARY_REF_RESPONSE_NOT_EXACTLY_ONE_LINE
PRIMARY_REF_RESPONSE_MALFORMED
PRIMARY_SUCCESS_STDERR_NONEMPTY
PRIMARY_AUTHENTICATION_OR_AUTHORIZATION_REJECTION
PRIMARY_NON_REGISTERED_FAILURE
```

An alternate HTTP error, transport error, redirect, oversized body, invalid UTF-8/JSON, duplicate key, ref/object/SHA mismatch, or malformed response stops immediately. There is no second alternate call.

## Call-Count Contract

```text
primary calls maximum:       1
alternate calls maximum:     1
total remote calls maximum:  2
same-method retries:         0
```

If primary succeeds, alternate calls must be 0. If a registered primary transport failure occurs, alternate calls must be exactly 1. Both methods normalize to `refs/heads/main` plus a lowercase 40-character SHA, which must equal the actual new approval-governance commit.

## No Remote Attestation File

This request adopts the narrower pre-execution-gate design. A successful remote gate writes one deterministic JSON line to captured stdout but creates no repository file. A failed gate creates no attestation or result commit and stops for a separately governed Hard Failure audit. No failed transport bytes may be reconstructed afterward.

## Reused Observer And Result Path

No observer defect was established. The following identities remain byte-for-byte unchanged:

- Observer: `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_diagnostic.ps1`
- Observer lines / bytes: 98 LF / 5,603
- Observer SHA-256: `545A5A6E72D82C65B086F08D2FC64F3C359B1A0E453F271D1481013D62FC7307`
- Observer Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_7_MANIFEST.json`
- Observer Manifest bytes / SHA-256: 13,336 / `968C3D598840CA25A0DFB2F8006027158B5AFD9EDD48F78BEAE9C7363AFE8A3C`
- Frozen executable: `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`
- Frozen arguments characters / ASCII SHA-256: 187 / `C4F5D93B17DBB3A31DFEA8D0F78B7FE23E16E5999F1E6EF1BA25E517FF95EC5A`
- Modeled command UTF-16 code units / bytes / SHA-256: 248 / 496 / `9EB29E9C6C2ABFB8B45208648BE84756EC58F492B15A6489DCD69182EA16238E`

The still-absent result path is reused without changing the observer:

```text
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_observation.bin
```

The old approval produced no result and has no committed path ownership. A future new package-bound approval must explicitly rebind this unchanged path.

## Requested Future Governance And Execution Order

1. Create and push one new exact two-path approval-governance commit as the direct child of the actual 1.1.8 package commit.
2. Confirm local `HEAD`, local `main`, tracked `origin/main`, clean worktree, result-path absence, and all frozen source identities without a direct remote query outside the bounded helper.
3. Parse and statically validate the bounded helper with helper executions and remote calls still zero.
4. Start the bounded helper process exactly once with the actual package and new approval-governance bindings.
5. If primary returns the correct SHA, require alternate calls 0. If primary returns one registered transport failure, permit exactly one alternate call. Any other outcome stops.
6. Only after the helper returns a valid PASS for the new approval SHA, invoke the unchanged observer parser/static gate exactly once.
7. Only after every static gate passes, start the unchanged command-line observer at most once with the new package and approval bindings.
8. Require capture host and every nested child start to remain 0.
9. If a complete `HGRAGC17` exists, commit and push exactly the one unchanged result path regardless of observer equality exit 0/1.
10. Verify local/tracking state and clean worktree, then stop for independent byte review without interpreting the difference.

## Failure Rules

Any package/approval parent or path mismatch, local/tracking/worktree/path gate failure, helper identity/parser/static failure, unregistered primary failure, returned ref mismatch, alternate failure, helper nonzero, observer parser/static failure, observer incomplete record, result-scope mismatch, commit failure, or push failure is a hard stop.

```text
NO_SAME_METHOD_RETRY
NO_THIRD_REMOTE_CALL
NO_OBSERVER_AFTER_REMOTE_GATE_FAILURE
NO_CAPTURE_HOST_OR_NESTED_CHILD
NO_PARTIAL_RECORD_CLEANUP_OR_OVERWRITE
NO_RESULT_COMMIT_IF_HGRAGC17_INCOMPLETE
NO_POST_FAILURE_DIAGNOSTIC_EXECUTION
```

## Explicitly Not Requested

```text
OLD_APPROVAL_REUSE
REMOTE_ATTESTATION_FILE
OBSERVER_SOURCE_CHANGE
HGRAGC17_FORMAT_CHANGE
CAPTURE_HOST
NESTED_PRE_CHAIN
POST
FINAL
TERMINAL
SYNTHETIC_REBINDING
REAL_PRECOMMIT_VALIDATOR
FORMAL_PREFLIGHT
OFFICIAL_EXECUTION
GOLD
RESERVATION
STAGE3B
```

## Requested Completion State

```text
AMENDMENT_5G_B_1_1_1_1_8_COMMAND_LINE_OBSERVATION_COMMITTED_AWAITING_INDEPENDENT_REVIEW
```
