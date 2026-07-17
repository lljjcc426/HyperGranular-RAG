# Stage4B U1-D Pre-Gold Amendment 5G-B.1.1.1.1.9 Approval Request

## Request

```text
REQUEST_APPROVAL_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_9
TRACKED_AND_PREPARSED_BOUNDED_HELPER_LAUNCHER_FOR_EXISTING_REMOTE_GATE_AND_COMMAND_LINE_DIAGNOSTIC_CHAIN_ONLY

ONE_NEW_PACKAGE_BOUND_APPROVAL_GOVERNANCE_COMMIT_REQUESTED
ONE_POST_APPROVAL_TRACKED_LAUNCHER_PARSER_STATIC_GATE_REQUESTED
ONE_POST_APPROVAL_EXISTING_HELPER_AST_STATIC_GATE_REQUESTED
AT_MOST_ONE_TRACKED_LAUNCHER_PROCESS_REQUESTED
AT_MOST_ONE_BOUNDED_HELPER_PROCESS_REQUESTED
ONE_PRIMARY_GIT_REMOTE_QUERY_REQUESTED
AT_MOST_ONE_CONDITIONAL_GITHUB_REST_QUERY_REQUESTED
SAME_METHOD_RETRY_ZERO_REQUIRED
ONE_POST_REMOTE_SUCCESS_OBSERVER_PARSER_STATIC_GATE_REQUESTED
AT_MOST_ONE_COMMAND_LINE_DIAGNOSTIC_OBSERVER_PROCESS_REQUESTED
ONE_COMPLETE_HGRAGC17_RESULT_REQUESTED
ONE_EXACT_ONE_PATH_RESULT_COMMIT_AND_PUSH_REQUESTED

CAPTURE_HOST_AND_ALL_NESTED_CHILD_STARTS_ZERO_REQUIRED
IMMEDIATE_STOP_FOR_INDEPENDENT_BYTE_REVIEW_REQUIRED
```

This package requests future authorization only. It does not authorize an approval-governance commit, post-approval parser, launcher/helper execution, remote call, observer parser/process, evidence creation, result commit, or downstream action.

## Binding Lineage

- Amendment 1.1.8 package: `90438287eeb77c2d383d7073315276a322b5670d`
- Consumed and non-reusable approval governance: `4d9886be1291133c7a8f94c3a4b35a14f26e0a8d`
- Hard Failure 22 checkpoint: `a740f669d535ab3a148c42f6839de6837eec9c15`
- Hard Failure 22 audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_22.md`
- Hard Failure 22 Review 1: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_22_REVIEW_1.md`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_9_MANIFEST.json`
- Manifest bytes: 16,536
- Manifest SHA-256: `35F4E35E6206DAA6C693F2EA7336A468626B50DC7737E471FBEFA154304D4FF2`

The future approval must bind the actual Amendment 1.1.9 package commit. Approval governance `4d9886be...` and every unexercised quota attached to its failed ordered gate are not reusable.

## Tracked And Preparsed Launcher

- Path: `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_9_bounded_remote_gate_launcher.ps1`
- Lines: 184 LF
- Bytes: 7,952
- Encoding: ASCII-compatible UTF-8 without BOM
- SHA-256: `898BDB48E89CF27A74785D3AD0D67F8F2D129DFDB6FFDF016849C6AFCDB0BC3D`
- Package-stage PowerShell parser invocations: 1
- Package-stage parser errors: 0
- Package-stage parser tokens: 1,195
- Package-stage launcher executions: 0
- Package-stage bounded-helper executions: 0
- Package-stage remote calls: 0

Static inspection confirms exactly one `.Start()` site, one stdout and one stderr `CopyToAsync`, one `WaitForExit`, one `WaitAll`, zero interpolation-variable-followed-by-colon tokens, and zero repository-write API tokens.

Frozen launcher invocation:

```text
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_9_bounded_remote_gate_launcher.ps1" -Mode BOUNDED_REMOTE_GATE
```

- Arguments characters / ASCII bytes: 179 / 179
- Arguments ASCII SHA-256: `4B788226FBFC6825D53A05CD4C23612286CC2F8BFFE40E4095DD3BB522F2E7EA`
- Arguments UTF-16LE bytes: 358
- Arguments UTF-16LE SHA-256: `E9ECBBB54862B5A2F49D7E6E000C0FF0BAFB2F39BF91CCE67BB7B666A9015EEC`
- Modeled command characters including terminal NUL: 240
- Modeled command UTF-16LE bytes: 480
- Modeled command UTF-16LE SHA-256: `6E369AA089C897C7EC7493E0DBF1C50AB0318FE1F20E0483714EE02D579F512A`

The parser result and invocation identities are package records only. The launcher has not run.

## Reused Bounded Helper Invocation

The launcher reuses the unchanged helper:

```text
C:\ProgramData\anaconda3\python.exe
-I -B scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_8_bounded_remote_gate.py
```

- Helper lines / bytes: 294 / 9,964
- Helper SHA-256: `7EBC6F40C58D479774B6C083157E5ECB429E02ED0B261FCECF1ADB58551C4567`
- Arguments characters / ASCII bytes: 82 / 82
- Arguments ASCII SHA-256: `D3529D3449AD623A811FC93F64DC4BB1251CA16DE4439E7F985039431800440E`
- Arguments UTF-16LE bytes: 164
- Arguments UTF-16LE SHA-256: `BF32888752D6119FAA82E0E5EBD03AF4F794EC584392D9A4D108107B38D3682C`

The launcher requires and passes these process-scoped bindings:

```text
HGRAG_EXPECTED_PACKAGE_COMMIT=<actual Amendment 1.1.9 package commit>
HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT=<actual new approval-governance commit>
```

Both values must be lowercase 40-character commit SHAs. The still-absent observation path is checked before helper start.

## Raw Stream And Exit Gate

The launcher uses one `System.Diagnostics.Process` for the helper. Standard input is not redirected. Standard output and standard error are redirected and drained concurrently from `BaseStream` into separate memory streams before `WaitForExit` and `WaitAll` complete.

The helper may pass only when:

```text
exit code = 0
stderr bytes = 0
stdout = exactly one strict-UTF-8 line
line ending = one terminal LF and no CR
JSON bytes = one registered canonical PASS variant
```

On success, the launcher forwards the already-validated raw stdout bytes. It emits no additional stdout and creates no repository file. Any start, drain, exit, stderr, framing, UTF-8, or PASS-gate failure stops before observer parsing.

## Exact PASS JSON Gate

The accepted key order is fixed to the helper's canonical `sort_keys=True` encoding:

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

Exactly five byte-equivalent value variants are registered:

1. Primary success: `SUCCESS`, `PRIMARY_GIT`, calls `1/0/1`, retries 0.
2. Alternate success after `TLS_CONNECT_FAILURE`: `ALTERNATE_GITHUB_REST`, calls `1/1/2`, retries 0.
3. Alternate success after `DNS_RESOLUTION_FAILURE`: same bounded counts.
4. Alternate success after `CONNECTION_RESET_BEFORE_REF`: same bounded counts.
5. Alternate success after `HTTP_TRANSPORT_UNAVAILABLE`: same bounded counts.

Every variant requires schema `HGRAG_BOUNDED_REMOTE_GATE_V1`, outcome `PASS`, exact `refs/heads/main`, package/approval fields equal to the process bindings, and final SHA equal to the new approval-governance binding. No additional key, whitespace form, output line, transport class, method, call count, or retry count is accepted.

## Unchanged Transport Policy

Primary remains exactly one fixed Git `ls-remote --heads` query. Alternate remains exactly one unauthenticated, proxy-disabled, redirect-disabled Python `urllib` request to GitHub's single-reference REST endpoint and is available only after one registered no-ref primary transport failure.

```text
primary calls maximum:       1
alternate calls maximum:     1
total remote calls maximum:  2
same-method retries:         0
```

Returned ref/SHA mismatch, malformed or multiple output, authentication/authorization rejection, unregistered primary failure, or any alternate failure remains terminal. Amendment 1.1.9 changes neither the helper nor the transport policy.

## Reused Observer And Result Path

No observer or `HGRAGC17` defect was established. These identities remain unchanged:

- Observer: `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_diagnostic.ps1`
- Observer lines / bytes: 98 / 5,603
- Observer SHA-256: `545A5A6E72D82C65B086F08D2FC64F3C359B1A0E453F271D1481013D62FC7307`
- Observer Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_7_MANIFEST.json`
- Observer Manifest bytes / SHA-256: 13,336 / `968C3D598840CA25A0DFB2F8006027158B5AFD9EDD48F78BEAE9C7363AFE8A3C`

The result path remains absent and unchanged:

```text
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_observation.bin
```

A future new package-bound approval must explicitly rebind this path. Remote success still creates no attestation file.

## Requested Future Governance And Execution Order

1. Create and push one exact two-path approval-governance commit as the direct child of the actual 1.1.9 package commit.
2. Without a direct remote query, confirm local `HEAD`, local `main`, tracked `origin/main`, clean worktree, result-path absence, and every frozen package/launcher/helper/observer/Manifest/invocation identity.
3. Parse and statically validate the tracked launcher exactly once with launcher/helper executions and remote calls still zero.
4. Parse and statically validate the unchanged Python helper exactly once with helper execution and remote calls still zero.
5. Start the tracked launcher at most once with the actual package and approval bindings.
6. The launcher may start the bounded helper at most once. The helper retains primary at most 1, alternate at most 1, total remote calls at most 2, and same-method retry 0.
7. Require the launcher's exact PASS JSON for the actual new approval SHA. Any other outcome stops.
8. Only after PASS, invoke the unchanged observer parser/static gate at most once.
9. Only after every static gate passes, start the unchanged command-line observer at most once. Capture host and all nested child starts remain 0.
10. If a complete `HGRAGC17` exists, commit and push exactly the one unchanged result path regardless of observer equality exit 0/1.
11. Verify local/tracking state and clean worktree, then stop for independent byte review without interpreting the difference.

## Failure Rules

Any parent/path, local/tracking/worktree/path, source/invocation, launcher parser/static, helper AST/static, launcher/helper exit, remote/PASS, observer parser/static/record, result scope/commit, or push failure is a hard stop.

```text
NO_SECOND_LAUNCHER_PROCESS
NO_SECOND_HELPER_PROCESS
NO_SAME_METHOD_RETRY
NO_THIRD_REMOTE_CALL
NO_OBSERVER_AFTER_REMOTE_GATE_FAILURE
NO_CAPTURE_HOST_OR_NESTED_CHILD
NO_PARTIAL_RECORD_CLEANUP_OR_OVERWRITE
NO_RESULT_COMMIT_IF_HGRAGC17_INCOMPLETE
NO_POST_FAILURE_DIAGNOSTIC_EXECUTION
```

## Package-Assembly Audit

Package assembly ran the tracked-launcher PowerShell parser exactly once and received zero errors. It did not parse the existing Python helper or observer, execute any frozen source, issue a remote call, or create evidence.

Five read-only support checks failed without project writes or experimental execution. An initial context read used a nonexistent shortened HF22 filename before reading the actual path. Local `rg.exe` could not start with `Access is denied`, after which `Get-ChildItem` located the exact files. A launcher metrics check used unavailable static `.NET SHA256.HashData`, after which the established `SHA256.Create().ComputeHash()` method returned the frozen identity. The first final cross-file validator found that Review 1 omitted the launcher's full SHA and stopped; the identity was added. A later recursive stale-reference scan exceeded the exact eight paths because PowerShell included tracked historical result files. Its recursive candidate set also included tracked reservation metadata and test source paths, but no matching content from those paths was returned and no reservation/test or historical-result value was used for a package decision. The scan read no project-external path and was replaced by an exact-eight-path scan. In all five failures, launcher/helper/observer executions, remote calls, evidence creations, and project writes were 0.

## Explicitly Not Requested

```text
OLD_APPROVAL_REUSE
INLINE_TEMPORARY_LAUNCH_WRAPPER
PYTHON_HELPER_SOURCE_CHANGE
REMOTE_TRANSPORT_POLICY_CHANGE
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
AMENDMENT_5G_B_1_1_1_1_9_COMMAND_LINE_OBSERVATION_COMMITTED_AWAITING_INDEPENDENT_REVIEW
```
