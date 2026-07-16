# Stage4B-U1-D Pre-Gold Hard Failure 19

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Failure date: 2026-07-16
- Amendment 5G-B.1.1.1.1.5 package: `f634a1ca766cc2885017f63f94ef9b87cab9a765`
- Approval governance: `950b56e83de8a87b7afe75eb3f021819e19516c8`
- Failure status: `AMENDMENT_5G_B_1_1_1_1_5_PRE_CAPTURE_HOST_CHILD_NONZERO_STOPPED_HARD_FAILURE_19`
- Established failure boundary: `PRE_CAPTURE_HOST_REPORTED_ADAPTER_NONZERO_EXIT_1`
- Deeper adapter/parent root cause: `UNCONFIRMED`
- PRE observer executions: 1
- PRE capture-host executions: 1
- Automatic retries: 0
- Other project conversations, thread tools, and global memory used: No

## Approval-Governance Gate

The independent approval accepted the Hard Failure 18 review and bound only the frozen outer-observer/durable-raw chain to:

```text
package:
f634a1ca766cc2885017f63f94ef9b87cab9a765

direct package parent:
a3812d000b8af07196ea3a824988703a3ff132d3

Manifest:
37645 bytes
303A347368E4BFBF4CEBBB71DFE07E244328A60BC4DBE996A0444A5C56E45BF9
```

The required approval-governance commit was created and pushed before any frozen-source execution:

```text
approval governance:
950b56e83de8a87b7afe75eb3f021819e19516c8

direct parent:
f634a1ca766cc2885017f63f94ef9b87cab9a765

exact changed paths:
AGENTS.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_5_APPROVAL_DECISION.md
```

After the push, local HEAD, `origin/main`, and direct GitHub `main` all equaled the approval commit. The worktree was clean and all eleven future evidence paths were absent.

The old approval `677df53f014ab194e08042e4f605b5f879b9fa32` was not reused.

## Post-Governance Static Gates

All approved read-only static gates passed before the PRE observer process start:

```text
source identities: 7/7
invocation identities: 12/12
fixed stdout identities: 15/15
source/invocation/stdout total: 34/34

source and alias fixtures: 12/12
binary-format fixtures: 16/16
observer invocation/success/anchor/integration fixtures: 15/15
observer fixture total: 43/43

process starts during static gates: 0
file writes during static gates: 0
```

The static gates matched the registered source bytes/SHA/LF/ASCII/parser identities, all adapter/capture-host/verifier/observer command envelopes, all fixed stdout identities, the explicit `Get-ExactSha256Hex` helper contract, and the `HGRAGO15` binary format.

## Single Authorized PRE Observer Execution

The only approved PRE observer was started once with the frozen executable and exact arguments:

```text
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_5_execution_observer.ps1" -Mode PRE
```

Only these dynamic bindings were supplied:

```text
HGRAG_EXPECTED_PACKAGE_COMMIT=f634a1ca766cc2885017f63f94ef9b87cab9a765
HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT=950b56e83de8a87b7afe75eb3f021819e19516c8
```

The outer execution monitor observed:

```text
observer exit code: 1
observer stdout bytes: 0
observer stderr bytes: 492
observer stderr leading failure: Observed child nonzero exit: 1
```

The observer was not retried.

## Durable Raw Machine Evidence

Before enforcing the child exit/stdout/stderr success gates, the observer completed a `CreateNew` durable record at the registered PRE path:

```text
path:
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_5_pre_capture_outer_observation.bin

bytes:
520

SHA-256:
4ABEB26000DDC77E8293DB1616682E6748E2290A9608959A2A040B1CD2780A70
```

Read-only decoding of the fixed header established:

```text
magic: HGRAGO15
version: 1
header bytes: 48
mode code: 1 (PRE)
completion flags: 15
child exit code: 1
reserved: 0
raw stdout length: 0
raw stderr length: 472
actual total bytes: 520
expected total bytes: 48 + 0 + 472 = 520
```

The record is structurally complete, not a truncated partial write. Its child stdout is exact zero bytes. The persisted child stderr has SHA-256:

```text
9E8393DD9738C73FCA928BD28E0031A6B8EABF4FABE9147FA0F101ED969D56EB
```

The decoded capture-host stderr reports:

```text
Adapter nonzero exit: 1
```

The raw record was fingerprinted again after diagnostics and remained byte-for-byte unchanged at the same 520-byte length and SHA-256.

## Established And Unestablished Boundaries

The durable record establishes all of the following:

```text
the PRE observer started exactly one registered capture-host child
the capture-host child completed with exit code 1
the capture host emitted zero stdout bytes
the capture host emitted the preserved 472-byte stderr payload
the capture host reported that its adapter child returned exit code 1
the outer observer persisted the raw result before applying success gates
```

The record does not establish the deeper reason why the adapter returned `1`. No adapter attestation was created, and the adapter's own raw stdout/stderr were not persisted as repository evidence. Therefore the following remain unconfirmed rather than inferred:

```text
adapter internal failure cause
parent process exit/stdout/stderr
loader invocation result
target/semantics invocation result
inner parent/loader/target process counts
package source defect
transport defect
```

The exact failure boundary is consequently `PRE_CAPTURE_HOST_REPORTED_ADAPTER_NONZERO_EXIT_1`, not a deeper root-cause claim.

## Future-Path Preservation Audit

Immediately after the hard stop, exactly one of the eleven registered future paths existed:

```text
PRESENT:
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_5_pre_capture_outer_observation.bin

ABSENT:
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_VALIDATOR_SEMANTICS_AUDIT.md
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_5_pre_adapter_execution_attestation.json
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_validator_semantics.json
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_POST_SYNC_TRANSPORT_AUDIT.md
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_5_post_adapter_execution_attestation.json
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_5_post_capture_outer_observation.bin
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_post_sync_transport_attestation.json
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_5_final_adapter_execution_attestation.json
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_5_final_capture_outer_observation.bin
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_5_terminal_verifier_outer_observation.bin
```

The PRE raw record is failure evidence only. It is not a successful PRE outer observation, cannot satisfy the four-path semantics success commit, and must not be overwritten, deleted, renamed, retried, or reused.

## Read-Only Diagnostic Anomalies

Two post-failure read-only helper attempts failed without changing repository evidence:

1. A diagnostic helper was named `H`; PowerShell again resolved it to the built-in `Get-History` alias after header fields had been printed.
2. A corrected digest helper encountered an ambiguous `ComputeHash` overload while handling the zero-byte stdout array.

Both attempts performed zero file writes and zero external child-process starts. A final explicit, fully named read-only decoder then recovered the persisted stderr length, SHA-256, and text. The raw file SHA-256 remained unchanged.

## Fail-Closed Stop

The PRE authorization was consumed at the nonzero-child gate. The following did not occur:

```text
PRE observer retry
alternate observer/capture host/adapter
source or runtime substitution
semantics narrative creation
semantics machine creation
PRE adapter attestation creation
four-path semantics success commit
POST observer
FINAL observer
PRE_ATTESTATION verifier
TERMINAL observer or verifier
evidence cleanup or overwrite
synthetic rebinding
real precommit validator
formal preflight
official input/token/capture
controller/verifier/Gold
reservation
Stage3B
```

Before the failure-audit checkpoint, local HEAD, `origin/main`, and direct GitHub `main` remained equal to approval governance `950b56e83de8a87b7afe75eb3f021819e19516c8`; the only worktree path was the preserved raw record.

## Conclusion

```text
HARD_FAILURE_19
PRE_CAPTURE_HOST_CHILD_EXIT_1
CAPTURE_HOST_STDOUT_EXACT_ZERO_BYTES
CAPTURE_HOST_STDERR_PRESERVED_472_BYTES
CAPTURE_HOST_REPORTED_ADAPTER_NONZERO_EXIT_1
DEEPER_ADAPTER_PARENT_ROOT_CAUSE_UNCONFIRMED
PRE_RAW_RECORD_PRESERVED_UNCHANGED
SEMANTICS_SUCCESS_COMMIT_NOT_CREATED
POST_FINAL_TERMINAL_NOT_STARTED
CURRENT_APPROVAL_CONSUMED_AND_NON_REUSABLE
```

Current state: `AMENDMENT_5G_B_1_1_1_1_5_PRE_CAPTURE_HOST_CHILD_NONZERO_STOPPED_HARD_FAILURE_19`. Independent review and a new amendment/package-bound approval are required before any further frozen-source execution.
