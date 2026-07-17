# Stage4B U1-D Pre-Gold Amendment 5G-B.1.1.1.1.8 Approval Decision

## Decision

```text
APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_8
BOUNDED_REMOTE_VERIFICATION_TRANSPORT_POLICY_ONLY

HARD_FAILURE_21_REVIEW_1_ACCEPTED
AMENDMENT_5G_B_1_1_1_1_8_PACKAGE_APPROVED

ONE_NEW_PACKAGE_BOUND_APPROVAL_GOVERNANCE_COMMIT_APPROVED
ONE_POST_GOVERNANCE_LOCAL_TRACKING_STATIC_GATE_APPROVED
ONE_BOUNDED_REMOTE_GATE_HELPER_PROCESS_APPROVED

ONE_PRIMARY_GIT_LS_REMOTE_CALL_APPROVED
AT_MOST_ONE_CONDITIONAL_GITHUB_REST_CALL_APPROVED
SAME_METHOD_RETRY_ZERO_REQUIRED
TOTAL_REMOTE_CALLS_AT_MOST_TWO_REQUIRED

ONE_POST_REMOTE_PASS_OBSERVER_PARSER_STATIC_GATE_APPROVED
ONE_COMMAND_LINE_DIAGNOSTIC_OBSERVER_PROCESS_APPROVED
ONE_COMPLETE_HGRAGC17_RESULT_APPROVED
ONE_EXACT_ONE_PATH_RESULT_COMMIT_AND_PUSH_APPROVED

CAPTURE_HOST_AND_ALL_NESTED_CHILD_STARTS_ZERO_REQUIRED
IMMEDIATE_STOP_FOR_INDEPENDENT_BYTE_REVIEW_REQUIRED
```

## Approval Material Passport

- Independent approval attachment bytes: 11,725
- Independent approval attachment line endings: 441 CRLF
- Independent approval attachment SHA-256: `171D7661837A15386B677D9150604DBAF8E32F79461DB5AFDC96363C2F900A43`
- The attachment's policy-label line contains a literal citation-rendering artifact. The exact approval ID, package-approved statement, binding identities, call limits, ordered gates, failure rules, and required completion state remain explicit and are transcribed below.
- This decision records the user-supplied independent approval and does not broaden it.

## Binding Package And Lineage

- Package commit: `90438287eeb77c2d383d7073315276a322b5670d`
- Direct parent / Hard Failure 21 checkpoint: `c4ac4b90ea57c18502766b5cba288f67cc46e60b`
- Hard Failure 21 Review 1: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_21_REVIEW_1.md`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_8_MANIFEST.json`
- Manifest bytes: 12,757
- Manifest SHA-256: `672FBD0CCE7A43C747645FEC43ABFA4C1EF85084E5164F840F15EE67ECBFDC75`
- Bounded helper: `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_8_bounded_remote_gate.py`
- Helper lines / bytes: 294 LF / 9,964
- Helper SHA-256: `7EBC6F40C58D479774B6C083157E5ECB429E02ED0B261FCECF1ADB58551C4567`
- Consumed approval `f5a9ce38d10d419f8bc92772030f0d7cb77914cb` remains terminated and non-reusable.

## Frozen Bounded-Helper Invocation

Executable:

```text
C:\ProgramData\anaconda3\python.exe
```

Complete arguments:

```text
-I -B scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_8_bounded_remote_gate.py
```

- Complete arguments characters / ASCII bytes: 82 / 82
- Complete arguments ASCII SHA-256: `D3529D3449AD623A811FC93F64DC4BB1251CA16DE4439E7F985039431800440E`
- Complete arguments UTF-16LE bytes: 164
- Complete arguments UTF-16LE SHA-256: `BF32888752D6119FAA82E0E5EBD03AF4F794EC584392D9A4D108107B38D3682C`

The helper process must receive exactly these process-scoped bindings:

```text
HGRAG_EXPECTED_PACKAGE_COMMIT=90438287eeb77c2d383d7073315276a322b5670d
HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT=<actual new approval-governance commit SHA>
```

## Bounded Remote Contract

Primary is exactly one invocation of:

```text
C:\Program Files\Git\cmd\git.exe
ls-remote --heads https://github.com/lljjcc426/HyperGranular-RAG.git refs/heads/main
```

Primary success requires exit 0, exact empty stderr, and exactly one strict UTF-8 line matching `<lowercase 40-character SHA><TAB>refs/heads/main`. The SHA must equal the actual approval-governance commit.

Alternate is permitted exactly once only after primary returns no ref and one registered class:

```text
TLS_CONNECT_FAILURE
DNS_RESOLUTION_FAILURE
CONNECTION_RESET_BEFORE_REF
HTTP_TRANSPORT_UNAVAILABLE
```

The alternate is one unauthenticated Python `urllib` GET to:

```text
https://api.github.com/repos/lljjcc426/HyperGranular-RAG/git/ref/heads/main
```

It disables proxies and redirects, fixes timeout 30 seconds and body cap 65,536 bytes, requires HTTP 200, identity encoding, strict UTF-8, duplicate-key-free JSON, exact `refs/heads/main`, object type `commit`, and an exact lowercase 40-character SHA equal to the approval-governance commit.

```text
primary calls maximum:       1
alternate calls maximum:     1
total remote calls maximum:  2
same-method retries:         0
```

Any returned SHA mismatch, ambiguous/multiple ref, authentication/authorization rejection, malformed response, unregistered primary failure, or alternate failure is terminal.

## Exact Helper Success Contract

The helper must exit 0, write exact zero stderr bytes, and write exactly one strict UTF-8 JSON line with exactly these keys:

```text
alternate_calls
approval_governance_commit
final_normalized_ref
final_normalized_sha
gate_outcome
package_commit
primary_calls
primary_result_class
same_method_retries
schema
successful_method
total_remote_calls
```

Common required values:

```text
schema = HGRAG_BOUNDED_REMOTE_GATE_V1
gate_outcome = PASS
package_commit = 90438287eeb77c2d383d7073315276a322b5670d
approval_governance_commit = actual approval-governance SHA
final_normalized_ref = refs/heads/main
final_normalized_sha = actual approval-governance SHA
primary_calls = 1
same_method_retries = 0
```

Primary success requires `successful_method=PRIMARY_GIT`, `primary_result_class=SUCCESS`, `alternate_calls=0`, and `total_remote_calls=1`. Alternate success requires `successful_method=ALTERNATE_GITHUB_REST`, one registered transport class, `alternate_calls=1`, and `total_remote_calls=2`.

The helper writes no repository file and no persistent remote attestation.

## Reused Observer And Invocation

- Observer: `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_diagnostic.ps1`
- Observer lines / bytes: 98 LF / 5,603
- Observer SHA-256: `545A5A6E72D82C65B086F08D2FC64F3C359B1A0E453F271D1481013D62FC7307`
- Observer Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_7_MANIFEST.json`
- Observer Manifest bytes: 13,336
- Observer Manifest SHA-256: `968C3D598840CA25A0DFB2F8006027158B5AFD9EDD48F78BEAE9C7363AFE8A3C`
- `HGRAGC17` format and result path remain unchanged.

Observer executable:

```text
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
```

Observer complete arguments:

```text
-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_diagnostic.ps1" -Mode COMMAND_LINE_DIAGNOSTIC
```

- Complete arguments characters: 187 ASCII characters
- Complete arguments ASCII SHA-256: `C4F5D93B17DBB3A31DFEA8D0F78B7FE23E16E5999F1E6EF1BA25E517FF95EC5A`
- Complete arguments UTF-16LE bytes: 374
- Complete arguments UTF-16LE SHA-256: `CCC055FB3EC15BB283BB03B9B48F21E17FFB884E12A2A6D83556F6C68059B9D8`
- Modeled command characters including terminal U+0000: 248
- Modeled command UTF-16LE bytes / SHA-256: 496 / `9EB29E9C6C2ABFB8B45208648BE84756EC58F492B15A6489DCD69182EA16238E`

The future observer process must receive:

```text
HGRAG_EXPECTED_PACKAGE_COMMIT=90438287eeb77c2d383d7073315276a322b5670d
HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT=<actual new approval-governance commit SHA>
```

## HGRAGC17 Contract

The only approved observation path is:

```text
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_observation.bin
```

The fixed 88-byte little-endian header contains exact magic `HGRAGC17`, format version 1, header bytes 88, completion flags 15, reserved 0, four UTF-16 code-unit counts, and four UTF-16LE byte lengths. Payload order is actual command line, modeled command including terminal U+0000, registered executable, and complete arguments. Every byte length must equal twice its character count and total file length must close exactly.

The observer must finish `CreateNew`, all writes, `Flush(true)`, and close before the case-sensitive equality gate. Equality maps only to exit 0 or 1. Either exit is eligible for the result commit only when the record is structurally complete. Difference semantics must not be computed or reported in this execution round.

## Approval-Governance Commit Contract

The approval-governance commit must be the direct child of package `90438287eeb77c2d383d7073315276a322b5670d`, change exactly these two paths, and delete none:

```text
AGENTS.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_8_APPROVAL_DECISION.md
```

It must be pushed before any new helper AST parse, bounded helper execution, remote call, observer parser/static gate, observer process, or evidence write.

## Authorized Execution Order

1. Commit and push the exact two-path approval-governance change.
2. Without a direct remote query, verify local `HEAD`, local `main`, `origin/main` tracking, clean worktree, observation-path absence, and all package/helper/observer/Manifest/invocation identities.
3. Invoke the Python AST parser at most once for the bounded helper and complete its static contract gate with helper execution and remote calls still zero.
4. Start the bounded helper exactly once with the actual approval-governance SHA and package SHA bindings.
5. Validate the exact PASS JSON and exact empty stderr. Any failure stops before the observer.
6. Only after remote PASS, invoke the unchanged observer PowerShell parser exactly once and complete the static source/Manifest/invocation/13-field binary/durable-order contract gate.
7. Only after that static gate passes, start the unchanged observer at most once with the actual approval-governance and package bindings.
8. Require capture host, adapter, parent, loader, target ScriptBlock, and all nested child starts to remain zero.
9. Check only `HGRAGC17` structural completeness. Do not interpret the command-line difference.
10. If complete, commit and push exactly the single observation path as a direct child of the actual approval-governance commit, verify local/tracking and clean worktree, and stop for independent byte review.

## Result Commit Contract

The complete record authorizes one commit and one push even when observer equality exit is 1. The result commit must be the direct child of the actual approval-governance commit and change only:

```text
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_observation.bin
```

No status document, audit narrative, remote attestation, parser output, or difference interpretation may enter the result commit. The commit message must not state or infer the difference type.

## Failure Boundary

Any approval parent/path mismatch, local/tracking/worktree/path mismatch, helper source/invocation/parser/static failure, returned remote mismatch, authentication or unregistered primary failure, alternate failure, helper nonzero/stderr/PASS-contract failure, observer parser/static failure, incomplete record, result-scope mismatch, commit failure, or push failure is a hard stop.

```text
NO_SECOND_HELPER_PROCESS
NO_SAME_METHOD_REMOTE_RETRY
NO_THIRD_REMOTE_CALL
NO_OBSERVER_AFTER_REMOTE_GATE_FAILURE
NO_CAPTURE_HOST_OR_NESTED_CHILD
PARTIAL_HGRAGC17_PRESERVE_AS_CREATED
INCOMPLETE_RECORD_RESULT_COMMIT_ZERO
INCOMPLETE_RECORD_RESULT_PUSH_ZERO
NO_CLEANUP_OR_OVERWRITE
NO_POST_FAILURE_DIAGNOSTIC_EXECUTION
```

## Explicitly Not Approved

```text
NESTED_PRE_CHAIN_NOT_APPROVED
POST_NOT_APPROVED
FINAL_NOT_APPROVED
TERMINAL_NOT_APPROVED
SYNTHETIC_REBINDING_NOT_APPROVED
REAL_PRECOMMIT_VALIDATOR_NOT_APPROVED
FORMAL_PREFLIGHT_NOT_APPROVED
OFFICIAL_EXECUTION_NOT_APPROVED
GOLD_NOT_APPROVED
RESERVATION_NOT_APPROVED
STAGE3B_NOT_APPROVED
```

## Required Completion State

```text
AMENDMENT_5G_B_1_1_1_1_8_COMMAND_LINE_OBSERVATION_COMMITTED_AWAITING_INDEPENDENT_REVIEW
BOUNDED_REMOTE_GATE_PASSED
PRIMARY_CALLS_ONE
ALTERNATE_CALLS_ZERO_OR_ONE
SAME_METHOD_RETRIES_ZERO
TOTAL_REMOTE_CALLS_ONE_OR_TWO
HGRAGC17_COMMITTED
CAPTURE_HOST_AND_NESTED_CHILD_STARTS_ZERO
COMMAND_LINE_DIFFERENCE_NOT_YET_INTERPRETED
NESTED_PRE_NOT_RUN
POST_NOT_RUN
FINAL_NOT_RUN
TERMINAL_NOT_RUN
STAGE3B_KEEP_LOCKED
```
