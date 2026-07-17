# Stage4B U1-D Pre-Gold Amendment 5G-B.1.1.1.1.9 Approval Decision

## Decision

```text
APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_9
TRACKED_AND_PREPARSED_BOUNDED_HELPER_LAUNCHER_ONLY

HARD_FAILURE_22_REVIEW_1_ACCEPTED
AMENDMENT_5G_B_1_1_1_1_9_PACKAGE_APPROVED

ONE_NEW_PACKAGE_BOUND_APPROVAL_GOVERNANCE_COMMIT_APPROVED
ONE_POST_APPROVAL_TRACKED_LAUNCHER_PARSER_STATIC_GATE_APPROVED
ONE_POST_APPROVAL_EXISTING_HELPER_AST_STATIC_GATE_APPROVED
AT_MOST_ONE_TRACKED_LAUNCHER_PROCESS_APPROVED
AT_MOST_ONE_BOUNDED_HELPER_PROCESS_APPROVED

ONE_PRIMARY_GIT_REMOTE_QUERY_APPROVED
AT_MOST_ONE_CONDITIONAL_GITHUB_REST_QUERY_APPROVED
TOTAL_REMOTE_CALLS_AT_MOST_TWO_REQUIRED
SAME_METHOD_RETRY_ZERO_REQUIRED

ONE_POST_REMOTE_PASS_OBSERVER_PARSER_STATIC_GATE_APPROVED
AT_MOST_ONE_COMMAND_LINE_DIAGNOSTIC_OBSERVER_PROCESS_APPROVED
ONE_COMPLETE_HGRAGC17_RESULT_APPROVED
ONE_EXACT_ONE_PATH_RESULT_COMMIT_AND_PUSH_APPROVED

CAPTURE_HOST_AND_ALL_NESTED_CHILD_STARTS_ZERO_REQUIRED
IMMEDIATE_STOP_FOR_INDEPENDENT_BYTE_REVIEW_REQUIRED
```

## Approval Material Passport

- Independent approval attachment bytes: 11,908
- Independent approval attachment line endings: 453 CRLF
- Independent approval attachment SHA-256: `32CC9147967054BE1650A5616E2DC436CF88FF2472C515F590720DF53B41D8BD`
- This decision records the user-supplied independent approval and does not broaden it.
- Other project conversations, thread tools, and global memory used: No

## Binding Package And Lineage

- Package commit: `046ac17282e1a4dcdedb7f6d744899dedf44d4b5`
- Direct parent / Hard Failure 22 checkpoint: `a740f669d535ab3a148c42f6839de6837eec9c15`
- Hard Failure 22 Review 1: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_22_REVIEW_1.md`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_9_MANIFEST.json`
- Manifest bytes: 16,536
- Manifest SHA-256: `35F4E35E6206DAA6C693F2EA7336A468626B50DC7737E471FBEFA154304D4FF2`
- Tracked launcher: `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_9_bounded_remote_gate_launcher.ps1`
- Launcher lines / bytes: 184 LF / 7,952
- Launcher SHA-256: `898BDB48E89CF27A74785D3AD0D67F8F2D129DFDB6FFDF016849C6AFCDB0BC3D`
- Consumed approval `4d9886be1291133c7a8f94c3a4b35a14f26e0a8d` remains terminated and non-reusable.

## Frozen Launcher Invocation

Executable:

```text
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
```

Complete arguments:

```text
-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_9_bounded_remote_gate_launcher.ps1" -Mode BOUNDED_REMOTE_GATE
```

- Complete arguments characters / ASCII bytes: 179 / 179
- Complete arguments ASCII SHA-256: `4B788226FBFC6825D53A05CD4C23612286CC2F8BFFE40E4095DD3BB522F2E7EA`
- Complete arguments UTF-16LE bytes: 358
- Complete arguments UTF-16LE SHA-256: `E9ECBBB54862B5A2F49D7E6E000C0FF0BAFB2F39BF91CCE67BB7B666A9015EEC`
- Modeled command characters including terminal U+0000: 240
- Modeled command UTF-16LE bytes / SHA-256: 480 / `6E369AA089C897C7EC7493E0DBF1C50AB0318FE1F20E0483714EE02D579F512A`

The launcher process must receive exactly these process-scoped bindings:

```text
HGRAG_EXPECTED_PACKAGE_COMMIT=046ac17282e1a4dcdedb7f6d744899dedf44d4b5
HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT=<actual new approval-governance commit SHA>
```

## Launcher Static And Process Contract

The package-stage parser invocation count is 1, parse errors are 0, and parser token count is 1,195. The package-stage launcher/helper/remote/observer execution counts are all 0.

The tracked source has exactly one helper `$process.Start()` site, one stdout and one stderr `CopyToAsync`, one `WaitForExit`, one `WaitAll`, zero interpolation-variable-followed-by-colon tokens, and zero repository-write API tokens. No inline wrapper, alternate launcher, or direct helper bypass is permitted.

The launcher validates the repository root, fixed Python executable, unchanged helper source bytes/LF/terminal LF/SHA, exact helper arguments, lowercase package/approval bindings, and absence of the observation path before the single helper start.

## Frozen Bounded-Helper Invocation

Executable:

```text
C:\ProgramData\anaconda3\python.exe
```

Complete arguments:

```text
-I -B scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_8_bounded_remote_gate.py
```

- Helper lines / bytes: 294 LF / 9,964
- Helper SHA-256: `7EBC6F40C58D479774B6C083157E5ECB429E02ED0B261FCECF1ADB58551C4567`
- Complete arguments characters / ASCII bytes: 82 / 82
- Complete arguments ASCII SHA-256: `D3529D3449AD623A811FC93F64DC4BB1251CA16DE4439E7F985039431800440E`
- Complete arguments UTF-16LE bytes: 164
- Complete arguments UTF-16LE SHA-256: `BF32888752D6119FAA82E0E5EBD03AF4F794EC584392D9A4D108107B38D3682C`

The launcher passes the same package and actual approval-governance bindings to the helper. The helper source and remote policy remain byte-for-byte unchanged from Amendment 1.1.8.

## Raw Stream, Exit, And PASS Gate

The launcher redirects helper stdout and stderr and begins both raw `BaseStream.CopyToAsync` drains before `WaitForExit` and `Task.WaitAll`. It materializes both raw byte arrays only after the process and drains complete.

Launcher success requires:

```text
helper exit code = 0
helper stderr bytes = 0
helper stdout nonempty
stdout LF count = 1
stdout CR count = 0
last stdout byte = LF
stdout content excluding LF = strict UTF-8
stdout content = exactly one registered canonical PASS JSON
```

The outer executor must additionally require launcher exit 0, exact zero launcher stderr bytes, and exactly one registered PASS JSON line on launcher stdout. Any other outcome is terminal before observer parsing.

## Bounded Remote Contract

Primary remains exactly one invocation of:

```text
C:\Program Files\Git\cmd\git.exe
ls-remote --heads https://github.com/lljjcc426/HyperGranular-RAG.git refs/heads/main
```

Alternate remains exactly one unauthenticated Python `urllib` request to GitHub's single-reference REST endpoint and is permitted only after the primary returns no ref and one registered class:

```text
TLS_CONNECT_FAILURE
DNS_RESOLUTION_FAILURE
CONNECTION_RESET_BEFORE_REF
HTTP_TRANSPORT_UNAVAILABLE
```

```text
primary calls maximum:       1
alternate calls maximum:     1
total remote calls maximum:  2
same-method retries:         0
```

Any returned SHA mismatch, ambiguous or malformed response, authentication/authorization rejection, unregistered primary failure, or alternate failure is terminal.

## Exact PASS JSON Contract

Exactly five canonical JSON variants are accepted: primary success, or alternate success after exactly one of the four registered primary transport classes. Every variant requires:

```text
schema = HGRAG_BOUNDED_REMOTE_GATE_V1
gate_outcome = PASS
package_commit = 046ac17282e1a4dcdedb7f6d744899dedf44d4b5
approval_governance_commit = actual approval-governance SHA
final_normalized_ref = refs/heads/main
final_normalized_sha = actual approval-governance SHA
primary_calls = 1
same_method_retries = 0
```

Primary success requires `successful_method=PRIMARY_GIT`, `primary_result_class=SUCCESS`, `alternate_calls=0`, and `total_remote_calls=1`. Alternate success requires `successful_method=ALTERNATE_GITHUB_REST`, one registered transport class, `alternate_calls=1`, and `total_remote_calls=2`.

No additional key, whitespace form, output line, method, transport class, call count, or retry count is accepted. Remote success creates no repository attestation file.

## Reused Observer And Invocation

- Observer: `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_diagnostic.ps1`
- Observer lines / bytes: 98 LF / 5,603
- Observer SHA-256: `545A5A6E72D82C65B086F08D2FC64F3C359B1A0E453F271D1481013D62FC7307`
- Observer Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_7_MANIFEST.json`
- Observer Manifest bytes / SHA-256: 13,336 / `968C3D598840CA25A0DFB2F8006027158B5AFD9EDD48F78BEAE9C7363AFE8A3C`
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
- Complete arguments UTF-16LE bytes / SHA-256: 374 / `CCC055FB3EC15BB283BB03B9B48F21E17FFB884E12A2A6D83556F6C68059B9D8`
- Modeled command characters including terminal U+0000: 248
- Modeled command UTF-16LE bytes / SHA-256: 496 / `9EB29E9C6C2ABFB8B45208648BE84756EC58F492B15A6489DCD69182EA16238E`

The observer receives the same actual package and approval-governance bindings. Capture host, adapter, parent, loader, target ScriptBlock, and all other nested child starts must remain 0.

## HGRAGC17 And Result Contract

The only approved observation path is:

```text
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_observation.bin
```

The fixed 88-byte little-endian header contains exact magic `HGRAGC17`, version 1, header bytes 88, completion flags 15, reserved 0, four UTF-16 code-unit counts, and four UTF-16LE byte lengths. Payload order is actual command line, modeled command including terminal U+0000, registered executable, and complete arguments. Every byte length must equal twice its character count and total file length must close exactly.

The observer completes `CreateNew`, all writes, `Flush(true)`, and close before its case-sensitive equality gate. Equality exit 0 or 1 is eligible for the result commit only when the record is structurally complete. Difference semantics must not be computed, inferred, or reported in this execution round.

## Approval-Governance Commit Contract

The approval-governance commit must be the direct child of package `046ac17282e1a4dcdedb7f6d744899dedf44d4b5`, change exactly these two paths, and delete none:

```text
AGENTS.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_9_APPROVAL_DECISION.md
```

It must be pushed before any post-approval launcher parser, helper AST parser, launcher/helper process, remote call, observer parser/process, or evidence write.

## Authorized Execution Order

1. Commit and push the exact two-path approval-governance change.
2. Without a direct remote query, verify local `HEAD`, local `main`, `origin/main` tracking, clean worktree, observation-path absence, and all package/launcher/helper/observer/Manifest/invocation identities.
3. Invoke the PowerShell parser exactly once for the tracked launcher and complete its static contract gate with launcher/helper execution and remote calls still zero.
4. Invoke the Python AST parser exactly once for the existing helper and complete its static contract gate with helper execution and remote calls still zero.
5. Start the tracked launcher at most once with the actual approval-governance and package bindings.
6. Require launcher exit 0, exact zero stderr bytes, and exact registered PASS stdout. Any failure stops before the observer.
7. Only after PASS, invoke the unchanged observer PowerShell parser at most once and complete the static source/Manifest/invocation/13-field binary/durable-order gate.
8. Only after that gate passes, start the unchanged observer at most once with the actual approval-governance and package bindings.
9. Require capture host and every nested child start to remain 0.
10. Check only `HGRAGC17` structural completeness. Do not interpret the command-line difference.
11. If complete, commit and push exactly the single observation path as the direct child of the actual approval-governance commit, verify local/tracking and clean worktree, and stop for independent byte review.

## Result Commit Contract

A structurally complete record authorizes one commit and one push even when observer equality exit is 1. The result commit must be the direct child of the actual approval-governance commit and change only:

```text
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_observation.bin
```

No status document, audit narrative, remote attestation, parser output, or difference interpretation may enter the result commit. The commit message must not state or infer the difference type.

## Failure Boundary

Any approval parent/path mismatch, local/tracking/worktree/path mismatch, launcher or helper identity/parser/static failure, launcher/helper start/drain/exit failure, remote/PASS failure, observer parser/static failure, incomplete record, result-scope mismatch, commit failure, or push failure is a hard stop.

```text
NO_SECOND_LAUNCHER_PROCESS
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
AMENDMENT_5G_B_1_1_1_1_9_COMMAND_LINE_OBSERVATION_COMMITTED_AWAITING_INDEPENDENT_REVIEW
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
