# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1.6 Approval Request

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Package date: 2026-07-17
- Direct parent / Hard Failure 19 checkpoint: `96e9677d4779b9d4b3be59fbb319e0b4c6670732`
- Consumed 1.1.5 approval governance: `950b56e83de8a87b7afe75eb3f021819e19516c8`
- Approved 1.1.5 package: `f634a1ca766cc2885017f63f94ef9b87cab9a765`
- Future package commit: `MUST_BIND_THE_ACTUAL_COMMIT_CREATED_FROM_THIS_EXACT_PACKAGE`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6_MANIFEST.json`
- Manifest bytes: 13,802
- Manifest SHA-256: `7DA3418D8BF7F4CF49D82088294D78CFB6FB6C8E7F66229F18624FE60A929937`
- Package status: `AMENDMENT_5G_B_1_1_1_1_6_NESTED_DURABLE_RESULT_CAPTURE_PRE_ONLY_DIAGNOSTIC_PACKAGE_AWAITING_APPROVAL`
- Package authorizes execution: No
- Other project conversations, thread tools, and global memory used: No

## Requested Decision

```text
APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6_NESTED_DURABLE_RESULT_CAPTURE_PRE_ONLY_DIAGNOSTIC

ONE_NEW_PACKAGE_BOUND_APPROVAL_GOVERNANCE_COMMIT
ONE_PRE_OBSERVER_CHAIN_AT_MOST_ONCE
ONE_PRE_FAILURE_OR_SUCCESS_EVIDENCE_COMMIT
IMMEDIATE_STOP_FOR_INDEPENDENT_REVIEW
```

This request does not itself authorize any source reconstruction or execution. A new independent approval must bind the actual future package commit and this exact Manifest identity. It must not authorize POST, FINAL, or TERMINAL.

## Hard Failure 19 Disposition

Independent Review 1 accepts the 520-byte `HGRAGO15` record and freezes the established boundary as:

```text
PRE_CAPTURE_HOST_REPORTED_ADAPTER_NONZERO_EXIT_1
```

The record proves one capture-host child exit 1 with zero stdout and 472 stderr bytes. It also proves that the capture host started and awaited one adapter process which exited 1. It does not preserve the adapter's raw streams and does not establish the adapter's internal gate, parent start/result, loader start/result, target invocation, semantics start, or a package/transport/loader/target defect.

The old approval is consumed and cannot be reused. The old raw record remains immutable at 520 bytes / `4ABEB26000DDC77E8293DB1616682E6748E2290A9608959A2A040B1CD2780A70`.

## Exact Package Scope

The package commit must be the direct child of `96e9677d4779b9d4b3be59fbb319e0b4c6670732` and contain exactly these twelve Git paths:

```text
AGENTS.md
README.md
docs/REPRODUCIBILITY.md
docs/ROADMAP.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6_APPROVAL_REQUEST.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6_MANIFEST.json
docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_19_REVIEW_1.md
scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_nested_raw_verifier.ps1
scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_pre_nested_adapter.ps1
scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_pre_nested_capture_host.ps1
scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_pre_nested_observer.ps1
scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_6_pre_nested_parent.ps1
```

No file is deleted and no new result file is included in the package commit.

## Versioned PRE-Only Sources

| Source | Lines | Bytes | SHA-256 | Actual boundary |
|---|---:|---:|---|---|
| Nested parent | 182 | 12,118 | `91EC38326A39C8A4C9072821B34D4FE92D8423323B0051E027EF3348B56AA19E` | Starts inherited PRE loader and preserves loader result |
| Nested adapter | 150 | 9,752 | `0C97760D26FF4D00D75FCB8847170578AD2DDAA797A588F8FC1844380B3BF3F1` | Starts nested parent and preserves parent result |
| Nested capture host | 157 | 10,023 | `FD9C6261CEF905EFF2826D025ECE453863BC43AB5C2AEABA9C74C8EB55A8F73A` | Starts nested adapter and preserves adapter result |
| Nested observer | 195 | 13,263 | `C37CBF70AA91A0FC8341400DF74B5D883796F6EFEB6AC25A5DBA260716716D52` | Starts capture host and preserves outer result |
| Raw verifier | 114 | 6,882 | `FF990722ECC7AFAC0C4C1B8778A6743197814F0A1480A5BA0417FFB71A8E47AF` | Byte-validates old raw plus a contiguous new outer-to-inner prefix; writes no repository file |

All five files are LF/terminal-LF and parser-zero. The inherited 1.1.3 transport Manifest remains exactly 323,607 bytes / `804B4F8607532D6CE17EDE043D5A9511C7E855F4EB444C25F461381B6EDDA73D`. The loader and target source/payload identities are revalidated by the nested parent before a future start; their behavior is not changed by this package.

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
total                                                116/116
```

New observer, capture host, adapter, parent, loader, target, and raw-verifier execution counts are zero. Evidence writes are zero. Synthetic, real-validator, formal-preflight, official input/token/capture, controller, Gold, reservation, and Stage3B counts are zero.

Four read-only package-helper attempts failed before final validation: one orchestration JavaScript parse error before shell launch, one PowerShell `ForEach-Object`/`-join` binding error after read-only property inspection, and two empty-pipe parser errors in report formatting. They created no files and started no experimental or frozen-source process.

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
5. On success, commit and push the two PRE semantics files plus all four new raw records as the one PRE evidence commit.
6. On failure, do not form a semantics success commit; preserve and Git-anchor the failure raw prefix and any already-created partial semantics evidence in the failure audit.
7. Stop immediately for independent review. Do not run POST, FINAL, or TERMINAL.
```

The standalone raw verifier is frozen for byte-level review but is not requested as an extra post-failure process in this one-pass chain. A failure consumes the authorization before any such follow-up source execution.

## Failure Rule

Any identity, binding, parser, actual command line, path collision, process start, drain, wait, raw materialization, `CreateNew`, durable flush, exit, stdout, stderr, class, evidence path, commit, push, worktree, or remote-triplet failure consumes the authorization and stops the chain.

Retry, fallback, alternate script, source reconstruction after failure, evidence overwrite or cleanup, reset, rebase, force-push, threshold/data change, and partial continuation are forbidden.

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
AMENDMENT_5G_B_1_1_1_1_6_NESTED_DURABLE_PRE_DIAGNOSTIC_PACKAGE_AWAITING_INDEPENDENT_APPROVAL
```
