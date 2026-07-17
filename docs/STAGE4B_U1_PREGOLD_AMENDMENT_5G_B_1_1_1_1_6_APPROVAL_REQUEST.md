# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1.6 Corrected Approval Request

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Package date: 2026-07-17
- Direct parent / rejected package: `1e0973e3036af6f54aaf68e0699e35a34d2b78cd`
- Hard Failure 19 checkpoint ancestor: `96e9677d4779b9d4b3be59fbb319e0b4c6670732`
- Rejected Manifest: 13,802 bytes / `7DA3418D8BF7F4CF49D82088294D78CFB6FB6C8E7F66229F18624FE60A929937`
- Consumed 1.1.5 approval governance: `950b56e83de8a87b7afe75eb3f021819e19516c8`
- Approved 1.1.5 package: `f634a1ca766cc2885017f63f94ef9b87cab9a765`
- Future package commit: `MUST_BIND_THE_ACTUAL_COMMIT_CREATED_FROM_THIS_EXACT_PACKAGE`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6_MANIFEST.json`
- Manifest bytes: 17,536
- Manifest SHA-256: `6C5E027B4B4F337B3CB61BDD381F00715D284B3269B5F39F0BE3A2E75259BAC5`
- Package correction revision: `CORRECTED_AFTER_PACKAGE_REVIEW_1`
- Package status: `CORRECTED_AMENDMENT_5G_B_1_1_1_1_6_NESTED_DURABLE_PRE_DIAGNOSTIC_PACKAGE_AWAITING_INDEPENDENT_APPROVAL`
- Package authorizes execution: No
- Other project conversations, thread tools, and global memory used: No

## Requested Decision

```text
APPROVE_CORRECTED_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6_NESTED_DURABLE_RESULT_CAPTURE_PRE_ONLY_DIAGNOSTIC

ONE_NEW_PACKAGE_BOUND_APPROVAL_GOVERNANCE_COMMIT
ONE_PRE_OBSERVER_CHAIN_AT_MOST_ONCE
ONE_EXACT_SIX_PATH_PRE_SUCCESS_COMMIT_OR_ZERO_FAILURE_COMMITS
IMMEDIATE_STOP_FOR_INDEPENDENT_REVIEW
```

This request does not itself authorize any source reconstruction or execution. A new independent approval must bind the actual future package commit and this exact Manifest identity. It must not authorize POST, FINAL, or TERMINAL.

## Package Review 1 Disposition And Correction Boundary

Package Review 1 accepts the rejected package's twelve-path scope, immutable Hard Failure 19 raw binding, PRE-only direction, four nested raw layers, observer/capture-host/adapter durable ordering, 116/116 original fixtures, and zero-execution boundary. It rejects package `1e0973e3...` because loader stdin delivery could fail after `Process.Start` but before `HGRAGL16`, the failure commit paths were not frozen, and the requested completion state still described the pre-approval state.

This corrected package changes only:

1. nested-parent stdin access/write/flush/close failures are captured locally and thrown only after the loader result is awaited and `HGRAGL16` is durably flushed;
2. review-recommended Scheme A freezes exactly one six-path commit on success and exactly zero commits/pushes on failure; and
3. success, failure, and unified post-attempt review states are explicitly registered.

The other four new sources, their invocation envelopes, the four raw formats/paths, the inherited loader/target transport, fixed success stdout, and Hard Failure 19 evidence remain unchanged.

## Hard Failure 19 Disposition

Independent Review 1 accepts the 520-byte `HGRAGO15` record and freezes the established boundary as:

```text
PRE_CAPTURE_HOST_REPORTED_ADAPTER_NONZERO_EXIT_1
```

The record proves one capture-host child exit 1 with zero stdout and 472 stderr bytes. It also proves that the capture host started and awaited one adapter process which exited 1. It does not preserve the adapter's raw streams and does not establish the adapter's internal gate, parent start/result, loader start/result, target invocation, semantics start, or a package/transport/loader/target defect.

The old approval is consumed and cannot be reused. The old raw record remains immutable at 520 bytes / `4ABEB26000DDC77E8293DB1616682E6748E2290A9608959A2A040B1CD2780A70`.

## Exact Package Scope

The corrected package commit must be the direct child of rejected package `1e0973e3036af6f54aaf68e0699e35a34d2b78cd` and contain exactly these eight Git paths:

```text
AGENTS.md
README.md
docs/REPRODUCIBILITY.md
docs/ROADMAP.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6_APPROVAL_REQUEST.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6_MANIFEST.json
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6_PACKAGE_REVIEW_1.md
scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_pre_nested_parent.ps1
```

No file is deleted and no new result file is included in the package commit.

## Versioned PRE-Only Sources

| Source | Lines | Bytes | SHA-256 | Actual boundary |
|---|---:|---:|---|---|
| Nested parent | 197 | 12,769 | `B117878F04565A686BAAE4B4655386E260540CAAC2F1FB871465234A657B45F2` | Starts inherited PRE loader, delays stdin failure, and preserves loader result |
| Nested adapter | 150 | 9,752 | `0C97760D26FF4D00D75FCB8847170578AD2DDAA797A588F8FC1844380B3BF3F1` | Starts nested parent and preserves parent result |
| Nested capture host | 157 | 10,023 | `FD9C6261CEF905EFF2826D025ECE453863BC43AB5C2AEABA9C74C8EB55A8F73A` | Starts nested adapter and preserves adapter result |
| Nested observer | 195 | 13,263 | `C37CBF70AA91A0FC8341400DF74B5D883796F6EFEB6AC25A5DBA260716716D52` | Starts capture host and preserves outer result |
| Raw verifier | 114 | 6,882 | `FF990722ECC7AFAC0C4C1B8778A6743197814F0A1480A5BA0417FFB71A8E47AF` | Byte-validates old raw plus a contiguous new outer-to-inner prefix; writes no repository file |

All five files are LF/terminal-LF and parser-zero. The inherited 1.1.3 transport Manifest remains exactly 323,607 bytes / `804B4F8607532D6CE17EDE043D5A9511C7E855F4EB444C25F461381B6EDDA73D`. The loader and target source/payload identities and bytes remain unchanged; only the parent-side delivery-failure ordering changes.

## Frozen Invocation Envelopes

| Source | Arguments chars / SHA-256 | Modeled chars including NUL / SHA-256 |
|---|---|---|
| Parent | 142 / `AAF1D4AF60CBE85C1B50EC501C409D3C8F2A3DA1254AAA98092828AC8B5B4F86` | 203 / `B9085E62AE155C2740230EC0DB9E0324F2F44F21DA475B96BDD9C57656646540` |
| Adapter | 143 / `0EC365E890EF9AABE89C2ABB3C1D26BC34B9A10EC16393061A04B7EFF45B9081` | 204 / `2785ED776C4C63891E286E749AC7283F2930DCF5D7A415569BB1B09C0BA75142` |
| Capture host `-Stage PRE` | 159 / `D5A7E3BDD7A430CC434A46A2441338E6FECDA024D02E4518FCEB6A4AB239F4A6` | 220 / `ACEAFA7F2024EE2B0C55C0F6B33FFDF3A5D7F4170A9CCE607CD7C3EA776BE754` |
| Observer `-Mode PRE` | 154 / `4FC3F941A84FC3972BCAD8860F1AA688329C691A044428F4F651884FA6E8506A` | 215 / `C2F7EF9D26B73B107B874733BA744A222561D52032652ADA6AC764FE29F18681` |
| Verifier `-Mode PRE_DIAGNOSTIC` | 165 / `89FD80DC3F32C77C6C57D4E32F5FF664BC6CB353EC234F03F50256985B9FE691` | 226 / `D50A0BA16D9A50E86771635C71465294C03ADD7BE9DF7414681E40728FDE65D4` |

The executable is fixed to `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`; all tracked `-File` boundaries redirect stdout/stderr and do not redirect stdin. Only the parent-to-inherited-loader boundary overrides stdin redirection to deliver the already-registered target payload.

## Result Read and Persistence Order

Every new `Process.Start` boundary freezes this order:

```text
1. start exactly one child
2. start stdout and stderr BaseStream.CopyToAsync drains
3. WaitForExit
4. WaitAll both drains
5. read ExitCode and materialize both raw byte arrays
6. CreateNew the boundary-specific raw record
7. write fixed header, raw stdout, and raw stderr
8. Flush(true) and close
9. only then apply exit, SHA, byte, stdout, and stderr-class gates
10. emit the registered fixed success stdout only if all gates pass
```

No hash, classification, helper dispatch, or serializer occurs between raw-array materialization and completed durable write.

### Loader stdin-delivery correction

After loader start and both raw drains, the parent uses the fixed failure codes `BASE_STREAM_ACCESS`, `WRITE`, `FLUSH`, and `CLOSE`. It records the first delivery failure without throwing, always attempts close when a stream was obtained, waits for the loader and both drains, materializes exit/stdout/stderr, completes `HGRAGL16` through `Flush(true)`, and only then throws:

```text
PRE loader stdin delivery failure after Process.Start: <FIXED_CODE>; HGRAGL16 preserved
```

That normalized parent failure is then preserved by `HGRAGP16`. Therefore an absent `HGRAGL16` once again means the parent did not complete a post-start loader record; a caught stdin-delivery failure after loader start cannot escape without that loader record.

## Four Fixed Raw Records

All records use a 48-byte little-endian header: eight-byte magic, format version 1, header length 48, layer code, completion flags 15, signed exit code, zero reserved field, uint64 stdout length, and uint64 stderr length, followed by the two raw streams.

| Layer | Magic | Code | New versioned path |
|---|---|---:|---|
| Outer observer -> capture host | `HGRAGO16` | 1 | `results/...1_1_1_1_6_pre_capture_outer_observation.bin` |
| Capture host -> adapter | `HGRAGA16` | 2 | `results/...1_1_1_1_6_pre_adapter_child_observation.bin` |
| Adapter -> parent | `HGRAGP16` | 3 | `results/...1_1_1_1_6_pre_parent_child_observation.bin` |
| Parent -> loader | `HGRAGL16` | 4 | `results/...1_1_1_1_6_pre_loader_child_observation.bin` |

The target ScriptBlock runs in the loader process, so no target-process record exists. Failure evidence may contain only an outer-to-inner contiguous prefix of the four paths. Every created file is preserved; no overwrite, cleanup, or retry is permitted.

## Fixed Success Stdout Identities

| Source | Bytes | SHA-256 |
|---|---:|---|
| Parent | 155 | `51BF91217973F3C26FE4BFE56AADA7DB00C54B511A9061D22B2EB8ADDE4FD5C6` |
| Adapter | 156 | `B555E95E959EFA847F3A14A599A7C93BA0EDB1BE0FCB7B53CF17E2F93C8ED59A` |
| Capture host | 165 | `E805318A390586345981FE6BABCC307FA39E90E6FBD2587B3D0895C9A2486B56` |
| Observer | 132 | `8A2BC8B29E5161E055ADD9A993C9A673B2CEEE89DAFC8EAF5FA25ABE65CC07A1` |

At each boundary, stderr is independently accepted only as exact zero bytes or the inherited exact 382-byte frozen PowerShell startup CLIXML. The class is derived only after the raw record has been durably completed.

## Static Package Validation

Package assembly performed read-only validation without dot-sourcing or invoking any new frozen source:

```text
source/Manifest/invocation/stdout registry checks    56/56
four-boundary durable ordering fixtures              36/36
binary/path/prior-HF19 fixtures                       24/24
corrected Package Review 1 blocker fixtures           10/10
total                                                126/126
```

New observer, capture host, adapter, parent, loader, target, and raw-verifier execution counts are zero. Evidence writes are zero. Synthetic, real-validator, formal-preflight, official input/token/capture, controller, Gold, reservation, and Stage3B counts are zero.

The four previously reported read-only original-package helper failures remain disclosed. Corrected-package validation introduced no additional helper failure. All helper failures created no project file and started no experimental or frozen-source process.

## Required Future Approval Governance

The package must first be committed and pushed. Before approval push, only package commit, Manifest identity, preserved Hard Failure 19 raw identity, future-path absence, worktree state, and local/origin/direct-main equality may be checked. Source joining, AST parsing, invocation reconstruction, dot-sourcing, and execution are forbidden in that interval.

The future approval-governance commit must be the direct child of the actual package commit, bind its full SHA and this Manifest identity, be pushed before any new source reconstruction, and modify exactly:

```text
AGENTS.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6_APPROVAL_DECISION.md
```

## Only Requested Future Order

```text
1. Create and push the exact package-bound approval-governance commit.
2. After that push, run the approved static identity/parser/invocation gates.
3. Run the PRE observer chain at most once with the actual package and approval commit bindings.
4. Preserve the complete outer-to-inner raw prefix on any outcome.
5. On success, commit and push exactly the two PRE semantics files plus all four new raw records as the direct child of the approval-governance commit.
6. On failure, create zero commits and perform zero pushes; preserve the raw prefix and any partial semantics files uncommitted, then stop for a separately governed Hard Failure audit package.
7. Stop immediately for independent review. Do not run POST, FINAL, or TERMINAL.
```

The standalone raw verifier is frozen for byte-level review but is not requested as an extra post-failure process in this one-pass chain. A failure consumes the authorization before any such follow-up source execution.

## Failure Rule

Any identity, binding, parser, actual command line, path collision, process start, drain, wait, raw materialization, `CreateNew`, durable flush, exit, stdout, stderr, class, evidence path, commit, push, worktree, or remote-triplet failure consumes the authorization and stops the chain.

Retry, fallback, alternate script, source reconstruction after failure, evidence overwrite or cleanup, failure-branch commit/push, reset, rebase, force-push, threshold/data change, and partial continuation are forbidden.

## Explicitly Not Requested

```text
POST
FINAL
TERMINAL
SYNTHETIC_REBINDING
REAL_PRECOMMIT_VALIDATOR
FORMAL_PREFLIGHT
OFFICIAL_INPUT_OR_TOKEN_ACCESS
OFFICIAL_CAPTURE
CONTROLLER_OR_FORMAL_VERIFIER_EXECUTION
GOLD
RESERVATION
STAGE3B
```

## Requested Completion State

```text
Unified:
AMENDMENT_5G_B_1_1_1_1_6_PRE_DIAGNOSTIC_ATTEMPT_COMPLETED_AWAITING_INDEPENDENT_REVIEW

Success branch:
AMENDMENT_5G_B_1_1_1_1_6_PRE_DIAGNOSTIC_SUCCESS_EVIDENCE_COMMITTED_AWAITING_INDEPENDENT_REVIEW

Failure branch:
AMENDMENT_5G_B_1_1_1_1_6_PRE_DIAGNOSTIC_FAILURE_PREFIX_PRESERVED_UNCOMMITTED_AWAITING_HARD_FAILURE_AUDIT
```
