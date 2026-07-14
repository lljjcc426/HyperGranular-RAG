# Stage4B-U1-D Pre-Gold Hard Failure 8

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-14
- Failure code: `HARD_FAILURE_8_FORMAL_PREFLIGHT_A_GATE_EXPECTED_HEAD_LITERAL_MISMATCH`
- Amendment 5F-B package: `f33ee70233ea4098b2d7a17cfde3d266081ee693`
- Amendment 5F-B approval governance: `84d39707dee15729dc0c35c85a16f4e31dac89e4`
- Amendment 5F-B rebinding/governance: `052e8ecc04f566b75666d5cc96df74d2ed5061e4`
- Formal preflight invocation: `1 / 1, consumed`
- Official capture invocation: `0 / 1`
- Other project conversations, thread tools, and global memory used: No

## Failure Summary

The single authorized 5F-B formal preflight stopped at the first A-gate assertion. The repository state itself was synchronized and clean:

```text
actual local HEAD:
052e8ecc04f566b75666d5cc96df74d2ed5061e4

actual origin/main:
052e8ecc04f566b75666d5cc96df74d2ed5061e4

actual GitHub main:
052e8ecc04f566b75666d5cc96df74d2ed5061e4
```

The preflight wrapper incorrectly asserted this different full literal:

```text
052e8ece1839ff253f8aeb84d5f828377be74829
```

Both values share the short prefix `052e8ec`. The incorrect full literal was transcribed into the wrapper without first resolving the newly created rebinding commit to its full SHA. The A gate therefore raised:

```text
RuntimeError: A gate Git mismatch:
052e8ecc04f566b75666d5cc96df74d2ed5061e4
052e8ecc04f566b75666d5cc96df74d2ed5061e4
052e8ecc04f566b75666d5cc96df74d2ed5061e4
```

This is a formal-preflight command construction/transcription defect. It is not GitHub drift, network failure, governance-file drift, helper failure, OS-temp path failure, official-input failure, cache failure or capture failure.

## Exact Stop Boundary

The exception occurred immediately after reading the three Git commit values and before all later A-gate checks. Consequently:

```text
remaining A-gate hash/output checks: not reached inside formal preflight
typed argument-policy helper import/call: 0
path-equivalence helper import/call: 0
official input metadata/content access: 0
authorization token use: 0
official capture invocation: 0
controller/verifier/evaluator invocation: 0
```

No B, C or D gate ran. No token was passed to capture. No decisions comparator or diagnostic computation ran.

## Post-Failure Metadata-Only Check

After stopping, a separate metadata-only check inspected only the registered output and OS-temp residue locations. It did not access any of the five official input paths.

```text
machine audit exists: false
narrative audit exists: false
formal outputs existing count: 0
diagnostic temp residue count: 0
worktree clean before audit write: true
```

The successful 5F-B post-approval rebinding evidence and governance binding remain unchanged. No cache, historical evidence, official artifact, code or test file was modified or deleted.

## Governance Consequence

The only 5F-B formal-preflight authorization is consumed. The apparent correction is a one-literal wrapper change, but it may not be applied and rerun under the existing approval.

Any future attempt must first receive a new package-bound Amendment that explicitly freezes how the execution HEAD is obtained or bound. No second preflight, typed-helper official call, path-helper official call or capture is authorized now.

## Current State

```text
AMENDMENT_5F_B_FORMAL_PREFLIGHT_STOPPED_HARD_FAILURE_8
FORMAL_PREFLIGHT_CONSUMED_FAILED
TYPED_HELPER_NOT_RUN
PATH_HELPER_NOT_RUN
OFFICIAL_INPUTS_NOT_ACCESSED
AUTHORIZATION_TOKEN_NOT_USED
OFFICIAL_CAPTURE_NOT_RUN
HARD_FAILURE_4_DIAGNOSIS_INCOMPLETE
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
