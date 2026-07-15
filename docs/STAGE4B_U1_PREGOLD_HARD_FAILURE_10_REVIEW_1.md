# Stage4B-U1-D Pre-Gold Hard Failure 10 Review 1

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Review date: 2026-07-15
- Reviewed checkpoint: `aab591b92804fd1226a62751c38d056918f71b41`
- Decision: `ACCEPT_HARD_FAILURE_10_AUDIT`
- Historical evidence decision: `ACCEPT_5G_B_TWO_RUN_REBINDING_AS_HISTORICAL_FAILURE_EVIDENCE_ONLY`
- Next action: `RETURN_FOR_AMENDMENT_5G_B_1_PACKAGE`
- Other project conversations, thread tools, and global memory used: No

## Review Decision

The independent review accepts the Hard Failure 10 audit, freezes checkpoint `aab591b92804fd1226a62751c38d056918f71b41`, and accepts the two 5G-B rebinding runs only as deterministic evidence inside the historical failed checkpoint.

Current authorization state:

```text
ACCEPT_HARD_FAILURE_10_AUDIT
ACCEPT_5G_B_TWO_RUN_REBINDING_AS_HISTORICAL_FAILURE_EVIDENCE_ONLY
FREEZE_HARD_FAILURE_10_CHECKPOINT
RETURN_FOR_AMENDMENT_5G_B_1_PACKAGE

CURRENT_5G_B_APPROVAL_REUSE_NOT_APPROVED
CURRENT_REBINDING_EVIDENCE_AS_EXECUTION_BINDING_NOT_APPROVED
PRECOMMIT_VALIDATOR_CORRECTION_NOT_APPROVED
THREE_PATH_DIRECT_CHILD_NOT_APPROVED
DERIVED_EXECUTION_HEAD_VALIDATION_NOT_APPROVED
FORMAL_PREFLIGHT_NOT_APPROVED
OFFICIAL_INPUT_ACCESS_NOT_APPROVED
AUTHORIZATION_TOKEN_USE_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

## Bound History

```text
5G-B package:
f281864b424c406b42718c4ec58d7266ecafd9a3

5G-B approval governance:
79e69eab874f669d79d433fa965f5f5f48659332

Hard Failure 10 checkpoint:
aab591b92804fd1226a62751c38d056918f71b41
```

The approval-governance commit preceded synthetic execution, changed exactly `AGENTS.md` and the 5G-B approval decision, and was synchronized across local, origin and GitHub.

## Accepted Historical Rebinding Evidence

The frozen runner was invoked exactly twice, without preliminary, targeted, repair, retry or third invocation. Both runs passed:

```text
tests: 246/246
execution-head tests: 41
typed-policy tests: 44
failures/errors/skips: 0/0/0
tracked files: 33
tracked digest:
50D3BCDDAE42961ECCDDC30ADE683D6180F9CDFC319D085BEC762B8985A17041
official/helper/preflight/token/capture counters: 0
```

Both evidence files were 69,144 bytes with SHA-256 `00281BED7BC0DF10D47382CC47D0884BFCD331F0CB92EFC0B51F0FF176827A2A`, and direct byte equality passed. The run-1 OS-temporary file was deleted only after all equality gates passed.

These bytes cannot become an active execution binding because they bind approval commit `79e69eab...`, the approved exact-three-path direct child was never created, and any new approval governance changes runner-tracked governance bytes.

## Confirmed Direct Cause

The governance binding actually contains the 11 expected `bound_files` properties. The failed expression was:

```powershell
$g.bound_files.psobject.Properties.Count -ne 11
```

PowerShell member enumeration returned an 11-element `System.Object[]` containing one `1` per property instead of scalar cardinality 11. The nonempty comparison result was treated as true and failed closed.

The direct cause is therefore:

```text
PRECOMMIT GOVERNANCE VALIDATOR
COLLECTION-CARDINALITY EXPRESSION DEFECT
```

It was not a missing governance key, evidence drift, runner/test failure, execution-head helper failure, GitHub drift, official input failure, cache failure or capture failure.

## Preserved Historical Files

| Path | Bytes | SHA-256 |
|---|---:|---|
| `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_10.md` | 6,207 | `1B92A16EE4B9D14BA09C3345337A9E5026DAA2C577B4E123870C0C8895EE8497` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_SYNTHETIC_REBINDING_AUDIT.md` | 3,973 | `50D125193CDD49B2A33ADF4EFC3A5F4A0F74A4029EE640AA032B4FEE990B3054` |
| `results/stage4b_u1_d_pregold_amendment_5g_b_governance_binding.json` | 5,317 | `12BF30F3EF70D0420237DCF0A6C6D5D06C05990DDF637EA4CF31B7C3C7655730` |
| `results/stage4b_u1_d_pregold_amendment_5g_b_synthetic_rebinding.json` | 69,144 | `00281BED7BC0DF10D47382CC47D0884BFCD331F0CB92EFC0B51F0FF176827A2A` |

The three rebinding artifacts are historical failure records. Checkpoint `aab591b...` changed eight paths and cannot be interpreted as the approved exact-three-path direct child. Rewriting, resetting or force-pushing history to manufacture the missing direct child is forbidden.

## Required Amendment 5G-B.1 Direction

Only a new package may be assembled now:

```text
Stage4B-U1-D Pre-Gold Amendment 5G-B.1
Governance Binding Cardinality Validation Repair
And Fresh Rebinding Direct-Child Only
```

It must use fresh paths:

```text
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_SYNTHETIC_REBINDING_AUDIT.md
results/stage4b_u1_d_pregold_amendment_5g_b_1_governance_binding.json
results/stage4b_u1_d_pregold_amendment_5g_b_1_synthetic_rebinding.json
```

The corrected validator must use explicit array materialization and compare the exact unique key set derived from the Manifest. Cardinality alone is insufficient.

A future package-bound approval may request only: approval governance, one pure in-memory validator semantics check, exactly two fresh complete rebinding runs, fresh three-path artifact generation, one corrected real precommit validation, one exact-three-path direct-child commit, GitHub synchronization, and immediate stop.

It must not authorize execution-head helper calls, formal preflight, official input access, token, capture, controller, verifier or Gold. Those require a later separately reviewed package.

## Current Boundary

The current 5G-B approval is consumed. The current three historical files must remain byte-identical. Until a new package-bound 5G-B.1 approval is granted, validator correction, semantics checks, synthetic execution and direct-child creation remain prohibited.
