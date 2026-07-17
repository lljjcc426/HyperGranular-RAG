# Stage4B U1-D Pre-Gold Amendment 5G-B.1.1.1.1.6 Approval Decision

## Decision

```text
APPROVE_CORRECTED_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6_NESTED_DURABLE_RESULT_CAPTURE_PRE_ONLY_DIAGNOSTIC

CORRECTED_PACKAGE_APPROVED
PACKAGE_REVIEW_1_CORRECTIONS_ACCEPTED
ONE_NEW_PACKAGE_BOUND_APPROVAL_GOVERNANCE_COMMIT_APPROVED
ONE_PRE_NESTED_OBSERVER_CHAIN_AT_MOST_ONCE_APPROVED

SUCCESS_BRANCH:
ONE_EXACT_SIX_PATH_PRE_EVIDENCE_COMMIT_AND_PUSH_APPROVED

FAILURE_BRANCH:
ZERO_COMMITS_APPROVED
ZERO_PUSHES_APPROVED
UNCOMMITTED_RAW_PREFIX_PRESERVATION_REQUIRED
IMMEDIATE_STOP_FOR_HARD_FAILURE_AUDIT_REQUIRED
```

## Approval Material Passport

- Independent approval attachment bytes: 11,112
- Independent approval attachment SHA-256: `6A7CEC1D72CA8E39D009CA4CE5AD162FBFDDB078359773A2024F9D24B5D6A721`
- This decision records the user-supplied independent approval; it does not broaden it.

## Binding Package and Lineage

- Corrected package: `0efbea018f4ad0e8650e254d313fb9cc85d2a28c`
- Rejected direct parent: `1e0973e3036af6f54aaf68e0699e35a34d2b78cd`
- Hard Failure 19 checkpoint ancestor: `96e9677d4779b9d4b3be59fbb319e0b4c6670732`
- Rejected package `1e0973e3...` and old approval `950b56e8...` are non-reusable.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6_MANIFEST.json`
- Manifest bytes: 17,536
- Manifest SHA-256: `6C5E027B4B4F337B3CB61BDD381F00715D284B3269B5F39F0BE3A2E75259BAC5`
- Immutable Hard Failure 19 raw: `results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_5_pre_capture_outer_observation.bin`
- Immutable Hard Failure 19 raw bytes: 520
- Immutable Hard Failure 19 raw SHA-256: `4ABEB26000DDC77E8293DB1616682E6748E2290A9608959A2A040B1CD2780A70`

## Frozen Source Identities

| Source | Lines | Bytes | SHA-256 |
|---|---:|---:|---|
| Nested parent | 197 | 12,769 | `B117878F04565A686BAAE4B4655386E260540CAAC2F1FB871465234A657B45F2` |
| Nested adapter | 150 | 9,752 | `0C97760D26FF4D00D75FCB8847170578AD2DDAA797A588F8FC1844380B3BF3F1` |
| Capture host | 157 | 10,023 | `FD9C6261CEF905EFF2826D025ECE453863BC43AB5C2AEABA9C74C8EB55A8F73A` |
| Observer | 195 | 13,263 | `C37CBF70AA91A0FC8341400DF74B5D883796F6EFEB6AC25A5DBA260716716D52` |
| Raw verifier | 114 | 6,882 | `FF990722ECC7AFAC0C4C1B8778A6743197814F0A1480A5BA0417FFB71A8E47AF` |

The raw verifier is identity-bound for a future separately governed audit only and is not approved for execution in this attempt.

## Frozen Invocation Envelopes

| Source | Arguments chars / SHA-256 | Modeled chars including NUL / SHA-256 |
|---|---|---|
| Parent | 142 / `AAF1D4AF60CBE85C1B50EC501C409D3C8F2A3DA1254AAA98092828AC8B5B4F86` | 203 / `B9085E62AE155C2740230EC0DB9E0324F2F44F21DA475B96BDD9C57656646540` |
| Adapter | 143 / `0EC365E890EF9AABE89C2ABB3C1D26BC34B9A10EC16393061A04B7EFF45B9081` | 204 / `2785ED776C4C63891E286E749AC7283F2930DCF5D7A415569BB1B09C0BA75142` |
| Capture host `-Stage PRE` | 159 / `D5A7E3BDD7A430CC434A46A2441338E6FECDA024D02E4518FCEB6A4AB239F4A6` | 220 / `ACEAFA7F2024EE2B0C55C0F6B33FFDF3A5D7F4170A9CCE607CD7C3EA776BE754` |
| Observer `-Mode PRE` | 154 / `4FC3F941A84FC3972BCAD8860F1AA688329C691A044428F4F651884FA6E8506A` | 215 / `C2F7EF9D26B73B107B874733BA744A222561D52032652ADA6AC764FE29F18681` |
| Verifier `-Mode PRE_DIAGNOSTIC` | 165 / `89FD80DC3F32C77C6C57D4E32F5FF664BC6CB353EC234F03F50256985B9FE691` | 226 / `D50A0BA16D9A50E86771635C71465294C03ADD7BE9DF7414681E40728FDE65D4` |

The executable is fixed to `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`. The approved top-level observer arguments are exactly:

```text
-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_pre_nested_observer.ps1" -Mode PRE
```

## Fixed Success Stdout Identities

| Source | Bytes | SHA-256 |
|---|---:|---|
| Parent | 155 | `51BF91217973F3C26FE4BFE56AADA7DB00C54B511A9061D22B2EB8ADDE4FD5C6` |
| Adapter | 156 | `B555E95E959EFA847F3A14A599A7C93BA0EDB1BE0FCB7B53CF17E2F93C8ED59A` |
| Capture host | 165 | `E805318A390586345981FE6BABCC307FA39E90E6FBD2587B3D0895C9A2486B56` |
| Observer | 132 | `8A2BC8B29E5161E055ADD9A993C9A673B2CEEE89DAFC8EAF5FA25ABE65CC07A1` |

## Four Durable Raw Layers

All four records use the registered 48-byte little-endian header and outer-to-inner contiguous-prefix rule.

| Boundary | Magic | Layer code | Exact path |
|---|---|---:|---|
| Observer -> capture host | `HGRAGO16` | 1 | `results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_pre_capture_outer_observation.bin` |
| Capture host -> adapter | `HGRAGA16` | 2 | `results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_pre_adapter_child_observation.bin` |
| Adapter -> parent | `HGRAGP16` | 3 | `results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_pre_parent_child_observation.bin` |
| Parent -> loader | `HGRAGL16` | 4 | `results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_pre_loader_child_observation.bin` |

The target ScriptBlock runs inside the loader process; no target-process raw record is authorized.

## Approval-Governance Commit Contract

This approval-governance commit must be the direct child of corrected package `0efbea018f4ad0e8650e254d313fb9cc85d2a28c` and change exactly these two paths with zero deletions:

```text
AGENTS.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6_APPROVAL_DECISION.md
```

On the corrected package commit, the decision path plus the six evidence paths were all absent. After this governance commit, the decision path is present by the approved two-path contract; the six evidence paths must remain absent until the single approved PRE attempt. This is the only internally consistent interpretation of the post-governance future-path gate.

## Authorized Execution Order

1. Commit and push the exact two-path approval-governance change.
2. Confirm local `HEAD`, local `main`, `origin/main`, and direct GitHub `main` equality, clean worktree, and absence of the six result paths.
3. Reconstruct and validate the approved source/parser/invocation/stdout/raw-order registry with 126/126 static checks, zero frozen-process starts, and zero evidence writes.
4. Run the PRE nested observer at most once with dynamic bindings:

```text
HGRAG_EXPECTED_PACKAGE_COMMIT=0efbea018f4ad0e8650e254d313fb9cc85d2a28c
HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT=<actual approval-governance commit SHA>
```

5. Enter exactly one of the success or failure branches below and then stop.

Each of observer, capture host, adapter, parent, loader, and target ScriptBlock may run at most once. No automatic retry is permitted.

## Success Branch Contract

Success requires observer exit 0 and every registered gate to pass. One commit and one push are then authorized. The commit must be the direct child of the actual approval-governance commit and change exactly these six paths:

```text
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_VALIDATOR_SEMANTICS_AUDIT.md
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_pre_adapter_child_observation.bin
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_pre_capture_outer_observation.bin
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_pre_loader_child_observation.bin
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_pre_parent_child_observation.bin
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_validator_semantics.json
```

No status document, extra audit, or other path may enter that commit. After push, verify remote triplet equality and clean worktree, then stop for independent review.

## Failure Branch Contract

Any observer/child nonzero result or any identity, binding, process, persistence, exit, stdout, stderr, class, path, commit, push, worktree, or remote gate mismatch consumes authorization. The attempt must preserve the outer-to-inner raw prefix and any zero, one, or two partial semantics files exactly as created.

```text
commit count = 0
push count = 0
cleanup = forbidden
retry = forbidden
standalone raw verifier = forbidden
source reconstruction or diagnostic execution after failure = forbidden
next action = SEPARATELY_GOVERNED_HARD_FAILURE_AUDIT_PACKAGE
```

## Static Registration and Completion States

- Original static validation: 116/116
- Package Review 1 blocker fixtures: 10/10
- Required post-governance static total: 126/126
- Static-stage frozen-process starts: 0
- Static-stage evidence writes: 0

Unified attempt-completed state:

```text
AMENDMENT_5G_B_1_1_1_1_6_PRE_DIAGNOSTIC_ATTEMPT_COMPLETED_AWAITING_INDEPENDENT_REVIEW
```

Success state:

```text
AMENDMENT_5G_B_1_1_1_1_6_PRE_DIAGNOSTIC_SUCCESS_EVIDENCE_COMMITTED_AWAITING_INDEPENDENT_REVIEW
```

Failure state:

```text
AMENDMENT_5G_B_1_1_1_1_6_PRE_DIAGNOSTIC_FAILURE_PREFIX_PRESERVED_UNCOMMITTED_AWAITING_HARD_FAILURE_AUDIT
```

## Explicitly Not Approved

```text
POST_NOT_APPROVED
FINAL_NOT_APPROVED
TERMINAL_NOT_APPROVED
NESTED_RAW_VERIFIER_EXECUTION_NOT_APPROVED
SYNTHETIC_REBINDING_NOT_APPROVED
REAL_PRECOMMIT_VALIDATOR_NOT_APPROVED
FORMAL_PREFLIGHT_NOT_APPROVED
OFFICIAL_EXECUTION_NOT_APPROVED
GOLD_NOT_APPROVED
RESERVATION_NOT_APPROVED
STAGE3B_NOT_APPROVED
```
