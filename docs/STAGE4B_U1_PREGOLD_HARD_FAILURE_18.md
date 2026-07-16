# Stage4B-U1-D Pre-Gold Hard Failure 18

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Failure date: 2026-07-16
- Approved second-corrected package: `683d17bd70cc32dca2e495836bb6b16160a79f79`
- Package direct parent: `61cfce1d3c11891ad0d8c2953fd855c2c3d0f9a8`
- Approval governance: `677df53f014ab194e08042e4f605b5f879b9fa32`
- Manifest: 48,629 bytes / `E764A188AB11F49152B272F041CAC8FAC9477929C30475576D6349791E67373B`
- Approval source: 12,016 bytes / `E1E41FAEADDCA9455E8736D2A945DE2BB35F96CA87BE7F1EACB100131ABBFCA3`
- Failure status: `AMENDMENT_5G_B_1_1_1_1_4_PRE_CAPTURE_OBSERVATION_UNRECOVERABLE_HARD_FAILURE_18`
- Failure boundary: `AFTER_PRE_CAPTURE_HOST_PROCESS_COMPLETION_BEFORE_OUTER_RESULT_GATE_PERSISTENCE`
- Registered failure: `OUTER_OBSERVER_H_ALIAS_RESOLVED_TO_GET_HISTORY`
- PRE capture-host process starts: 1
- Automatic retries: 0
- Other project conversations, thread tools, and global memory used: No

## Approval-governance Gate

The package-bound approval was recorded as exact two-path commit:

```text
approval governance:
677df53f014ab194e08042e4f605b5f879b9fa32

direct parent:
683d17bd70cc32dca2e495836bb6b16160a79f79

changed paths:
AGENTS.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4_APPROVAL_DECISION.md
```

The commit was pushed successfully. Immediately after push, local HEAD, tracked `origin/main`, and direct GitHub `main` all equaled `677df53f014ab194e08042e4f605b5f879b9fa32`; the worktree was clean; and all seven future evidence paths were absent.

## Post-governance Static Gate

The approved static gate read but did not execute the six tracked PowerShell sources:

```text
canonical builder
capture-attestation host
PRE adapter
POST adapter
FINAL adapter
dual-mode terminal verifier
```

For each source, actual byte count, SHA-256, LF content-line count, terminal LF, zero CR, ASCII domain, and parser-error count matched the bound Manifest. The same gate reconstructed and checked:

```text
3 adapter invocation envelopes
3 capture-host invocation envelopes
2 verifier-mode invocation envelopes
all registered fixed success stdout identities
```

Every arguments character count/SHA and every modeled-command character count/SHA matched. Result:

```text
static checks: 106
passed: 106
failed: 0
source executions: 0
```

## Single PRE Process Boundary

The outer observer built one `ProcessStartInfo` with the frozen capture-host PRE invocation:

```text
FileName:
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe

Arguments:
-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_adapter_capture_attestation_host.ps1" -Stage PRE

WorkingDirectory:
E:\科研\HyperGranular-RAG

Environment bindings:
HGRAG_EXPECTED_PACKAGE_COMMIT=683d17bd70cc32dca2e495836bb6b16160a79f79
HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT=677df53f014ab194e08042e4f605b5f879b9fa32
```

`UseShellExecute=false`, stdout/stderr redirects, and `CreateNoWindow=true` were set. The process start returned true. Concurrent copies from `StandardOutput.BaseStream` and `StandardError.BaseStream` to memory were started. `WaitForExit()` returned, and both copy tasks completed.

Exactly one approved PRE capture-host process was therefore started and awaited. No second start occurred.

## Observation Failure

After the process and both copy tasks completed, the observer converted the two memory streams to byte arrays and attempted to compute SHA-256 through a helper named `H`:

```text
$outHash=H $outBytes
$errHash=H $errBytes
```

PowerShell command precedence selected the existing alias `H`, whose target is `Get-History`, instead of the helper function. The outer observer raised:

```text
H : Cannot locate the history for Id 65.
FullyQualifiedErrorId:
GetHistoryNoHistoryForId,Microsoft.PowerShell.Commands.GetHistoryCommand
```

`$ErrorActionPreference` was `Stop`, so the observer terminated before it printed or persisted:

```text
child exit code
raw stdout byte count/SHA/content
raw stderr byte count/SHA/class
outer exact-success gate result
```

The approved contract did not authorize an extra raw-capture file, and none was written. The in-memory byte arrays disappeared with the failed observer process. They cannot be recovered or reconstructed.

## Evidence Boundary

The following facts are established:

```text
PRE capture-host process start: 1
PRE capture-host WaitForExit returned: yes
stdout BaseStream copy completed: yes
stderr BaseStream copy completed: yes
outer observer completed result gates: no
automatic retry: 0
```

The following are not established and must remain `UNCONFIRMED`:

```text
capture-host exit code
capture-host exact stdout
capture-host exact stderr class
capture-host internal gate reached
PRE adapter process count
PRE parent process count
PRE loader process count
PRE target ScriptBlock count
PRE semantics sequence count
Git-child count inside the PRE chain
```

No package source/runtime defect is inferred from the observer failure. Conversely, no capture-host success is inferred from process completion. The exact capture-host runtime outcome remains unknown.

## Post-failure Preservation Audit

After the stop, local HEAD, tracked `origin/main`, and direct GitHub `main` still equaled `677df53f014ab194e08042e4f605b5f879b9fa32`; the worktree was clean. All seven future paths were absent:

```text
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_VALIDATOR_SEMANTICS_AUDIT.md
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_pre_adapter_execution_attestation.json
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_validator_semantics.json
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_POST_SYNC_TRANSPORT_AUDIT.md
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_post_adapter_execution_attestation.json
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_post_sync_transport_attestation.json
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_final_adapter_execution_attestation.json
```

There is no partial repository evidence to delete, overwrite, normalize, or commit. Absence of those paths is not used to infer the unobserved internal process counts.

One post-failure read-only inventory helper first stopped on a PowerShell missing-closing-brace parser error. It started no frozen process and performed no write; the corrected read-only inventory then established the preservation state above. The earlier pre-governance `rg.exe` path-list helper was denied before producing output and also caused zero writes or frozen-process executions. Both helper failures are disclosed and are not retries of PRE.

## Exact Stop Boundary

```text
approval-governance commits: 1
approval-governance pushes: 1
post-governance static gates: 1
static checks passed: 106/106
PRE capture-host process starts: 1
PRE capture-host process retries: 0
PRE downstream process counts: UNCONFIRMED
PRE evidence creations: 0 observed; all three paths absent
semantics evidence commits: 0
POST capture-host/adapter/parent/loader/target processes: 0
POST evidence creations/commits: 0
FINAL capture-host/adapter/PRE_ATTESTATION verifier processes: 0
FINAL attestation creations/commits: 0
TERMINAL verifier processes: 0
synthetic rebinding: 0
real precommit validator: 0
formal preflight: 0
official input accesses: 0
authorization-token uses: 0
official captures: 0
controller/verifier/Gold operations: 0
reservation operations: 0
Stage3B operations: 0
```

## Stop Rule

The single PRE capture-host authorization was consumed. No retry, fallback, temporary script, alternate adapter, source/runtime substitution, evidence cleanup, reset, rebase, force-push, semantics commit, POST, FINAL, or TERMINAL action occurred.

Independent review and a new Amendment with new package-bound approval are required before any further frozen-source execution.

```text
AMENDMENT_5G_B_1_1_1_1_4_PRE_CAPTURE_OBSERVATION_UNRECOVERABLE_HARD_FAILURE_18
APPROVAL_GOVERNANCE_COMMITTED_AND_PUSHED
STATIC_SOURCE_AND_INVOCATION_GATES_PASSED_106_OF_106
ONE_PRE_CAPTURE_HOST_PROCESS_STARTED_AND_AWAITED
OUTER_RESULT_OBSERVER_ALIAS_COLLISION
CHILD_EXIT_AND_RAW_STREAMS_UNRECOVERABLE
PRE_RUNTIME_OUTCOME_UNCONFIRMED
ALL_SEVEN_FUTURE_EVIDENCE_PATHS_ABSENT
SEMANTICS_COMMIT_NOT_CREATED
POST_NOT_RUN
FINAL_NOT_RUN
TERMINAL_NOT_RUN

RETRY_NOT_APPROVED
SYNTHETIC_REBINDING_NOT_APPROVED
REAL_PRECOMMIT_VALIDATOR_NOT_APPROVED
FORMAL_PREFLIGHT_NOT_APPROVED
OFFICIAL_EXECUTION_NOT_APPROVED
GOLD_NOT_APPROVED
RESERVATION_NOT_APPROVED
STAGE3B_NOT_APPROVED
```
