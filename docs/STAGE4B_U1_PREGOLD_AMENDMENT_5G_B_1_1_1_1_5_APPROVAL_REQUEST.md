# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1.5 Approval Request

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Package date: 2026-07-16
- Direct parent / Hard Failure 18 checkpoint: `a3812d000b8af07196ea3a824988703a3ff132d3`
- Consumed 1.1.4 approval governance: `677df53f014ab194e08042e4f605b5f879b9fa32`
- Approved 1.1.4 package: `683d17bd70cc32dca2e495836bb6b16160a79f79`
- Future package commit: `MUST_BIND_THE_ACTUAL_COMMIT_CREATED_FROM_THIS_EXACT_PACKAGE`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_5_MANIFEST.json`
- Manifest bytes: 37,645
- Manifest SHA-256: `303A347368E4BFBF4CEBBB71DFE07E244328A60BC4DBE996A0444A5C56E45BF9`
- Package status: `AMENDMENT_5G_B_1_1_1_1_5_FROZEN_OUTER_OBSERVER_DURABLE_RAW_CAPTURE_PACKAGE_AWAITING_APPROVAL`
- Package authorizes execution: No
- Other project conversations, thread tools, and global memory used: No

## Requested Decision

```text
APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_5_FROZEN_OUTER_OBSERVER_AND_DURABLE_RAW_CAPTURE_CHAIN_ONLY

ONE_NEW_PACKAGE_BOUND_APPROVAL_GOVERNANCE_COMMIT
ONE_PRE_OBSERVER_CHAIN_THEN_EXACT_FOUR_PATH_SEMANTICS_COMMIT
ONE_POST_OBSERVER_CHAIN_THEN_EXACT_FOUR_PATH_POST_SYNC_COMMIT
ONE_FINAL_OBSERVER_CHAIN_THEN_EXACT_TWO_PATH_FINAL_COMMIT
ONE_TERMINAL_OBSERVER_CHAIN_THEN_EXACT_ONE_PATH_TERMINAL_OBSERVATION_COMMIT
IMMEDIATE_STOP_AFTER_PUSH_AND_REMOTE_TRIPLET_GATE
```

No action above is authorized by this request itself. A new independent approval must bind the actual future package commit and this exact Manifest identity.

## Hard Failure 18 Disposition

Independent Review 1 accepts the Hard Failure 18 audit and freezes the root cause as:

```text
OUTER_OBSERVER_H_ALIAS_RESOLVED_TO_GET_HISTORY
```

It does not establish a package-source or capture-host runtime defect and does not establish capture-host success. PRE downstream counts remain `UNCONFIRMED`. The old approval was consumed and cannot be reused.

This amendment therefore changes the untracked outer observation layer and the Git-chain compatibility required by the new package. It does not reinterpret the missing 1.1.4 result.

## Exact Package Scope

The future package commit must be the direct child of `a3812d000b8af07196ea3a824988703a3ff132d3` and contain exactly these eleven paths, in Git path order:

```text
AGENTS.md
README.md
docs/REPRODUCIBILITY.md
docs/ROADMAP.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_5_APPROVAL_REQUEST.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_5_MANIFEST.json
docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_18_REVIEW_1.md
scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_5_adapter_capture_attestation_host.ps1
scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_5_execution_observer.ps1
scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_5_final_parent_start_orchestrator.ps1
scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_5_terminal_adapter_attestation_commit_verifier.ps1
```

No file is deleted.

## Inherited Content Kept Unchanged

The following tracked source bytes remain unchanged and are registered directly:

| Source | Lines | Bytes | SHA-256 |
|---|---:|---:|---|
| Canonical builder | 50 | 4,361 | `4409E8AFF4EFECE2A69404F42ED39C355CACE0BE2DFD2ACB6033D045142AF55D` |
| PRE adapter | 136 | 8,222 | `6D9466FD227E8DA1ADB6A24CFC170BF9880C87718CB6244CC5847774BEBB8A02` |
| POST adapter | 138 | 8,509 | `89828EB855B64DACF98A76CFB2CAB956FEA29D2B6B80B187AE3BDA3A33EF9CC5` |

The inherited 1.1.3 parent/loader/target registry remains 323,607 bytes / `804B4F8607532D6CE17EDE043D5A9511C7E855F4EB444C25F461381B6EDDA73D`. Canonical schema 2.0, six class-bearing adapter stdout variants, evidence semantics, and parent/loader/target process design are unchanged.

## Versioned Compatibility Sources

The new package contains versioned compatibility sources because the 1.1.4 terminal verifier correctly binds the old package path set and cannot validate a new package commit.

| Source | Lines | Bytes | SHA-256 | Change boundary |
|---|---:|---:|---|---|
| Capture-attestation host 1.1.5 | 211 | 13,700 | `A65692BEB36A53BB907D4380618250BE95E2CB98900B4CC055EEAA9C26B9ADF4` | New Manifest/request identity and versioned evidence paths; inner adapter logic unchanged |
| FINAL adapter 1.1.5 | 125 | 8,257 | `487FFF96B6C51A9F9EE56A3AB7A6A480F5C8380A984B0889D90342D3A573CE0A` | New Manifest and new PRE_ATTESTATION verifier binding |
| Dual-mode verifier 1.1.5 | 460 | 40,389 | `1A1D500B03F65DCAB754C5B18C108DBD58D03E88D24BF465FF74A30FB34FBC1A` | New package/path sets plus fixed binary outer-observation validation |
| Frozen execution observer | 203 | 13,186 | `67DCCD6B2AFD10164924CB98DCC99B93BD2150FB77DC9438496440373D0FF325` | New top-level result observer and durable raw writer |

All seven registered PowerShell sources are ASCII-only, LF-only, terminal-LF, and parser-zero.

## Frozen Observer Contract

The observer supports exactly four modes:

```text
PRE
POST
FINAL
TERMINAL
```

For every mode it validates its own tracked bytes/parser and actual `[Environment]::CommandLine + NUL`, validates the selected child source and invocation, removes all five dynamic binding variables from the inherited ProcessStartInfo environment, restores only the mode-required bindings, and starts exactly one child.

The helper name is `Get-ExactSha256Hex`. The source performs unfiltered `Get-Command Get-ExactSha256Hex` and requires the actually resolved command type to be `Function`. `H`, `G`, `S`, and `F` are explicitly forbidden helper names.

## Result Read And Preservation Order

The frozen order is:

```text
1. Process.Start
2. start stdout BaseStream.CopyToAsync
3. start stderr BaseStream.CopyToAsync
4. WaitForExit
5. WaitAll both drains
6. read and retain ExitCode
7. materialize stdout and stderr byte arrays
8. CreateNew and flush the raw binary observation
9. only then compute SHA, classify stderr, and apply exact child success gates
10. emit fixed observer success stdout
```

Between steps 7 and 8, the tracked source contains no hash, class, helper dispatch, or serializer call.

## Fixed Binary Format

Every mode uses the same no-serializer, little-endian format:

```text
offset  size  field
0       8     ASCII magic HGRAGO15
8       4     uint32 version = 1
12      4     uint32 header bytes = 48
16      4     uint32 mode code: PRE=1, POST=2, FINAL=3, TERMINAL=4
20      4     uint32 completion flags = 15
24      4     int32 child exit code
28      4     uint32 reserved = 0
32      8     uint64 stdout length
40      8     uint64 stderr length
48      N     raw stdout
48+N    M     raw stderr
```

Completion bits mean process started, wait completed, stdout drain completed, and stderr drain completed. The file is `CreateNew`, flushed to disk, and never overwritten or cleaned. A partial file from any failure must remain available for independent review.

## Observer Invocation Identities

| Mode | Arguments chars / SHA-256 | Modeled chars / SHA-256 | Observer success bytes / SHA-256 |
|---|---|---|---|
| PRE | 153 / `A6B61CDD94757CF51928FC5CD3C036EAC72F1F0C93E25BBF39D690BEFE4BB18A` | 214 / `A4ADCE73BAB8CF5549A67D31D5B291A7C4FD8BDC8C2A12E142713CFC6BCB7AC0` | 114 / `79836E6F06FCBF8579FC4AC59E4F08D87556478500A616522802E7D0FC9B360C` |
| POST | 154 / `9CE8FE00B385D7B27645DF02C859E61D4039675359931F1D289DAB38E2966901` | 215 / `78FB121C4C08520DE829F9643C46B19150963F770315C0DFB07400308B362702` | 115 / `1E06F6BAC497F641EB045DEF8B408EAB12B47A44EFC07F1F4B6B27856C03063B` |
| FINAL | 155 / `1530FB234404A833A7DA32B2BDEDE58AB53A4420C01EACA401BA2C8A3324A4D1` | 216 / `893130C0A2BA0D50C398E625B84453CD1C3857E41ADFE9D9CFFAB7F3AF20F306` | 116 / `68903497343804DEBE67BC93B3CEC88DD5D143D9EA0ECB515C3ACD13D7D1DADB` |
| TERMINAL | 158 / `F03D2F58393951C9EC5F307D3AECCC463572F7AF108CD6C4E6B94AA4CAECBC3D` | 219 / `96A1CD6A2ABB81DB71AB6EBB541C5852224B388F3F091572C88CD95F58B24A1F` | 119 / `914D22184BF04AF3F22389CAF69B4488E8A0DEF739DBC1EA4AE571ACC2AC97EC` |

## Stage Anchoring

The successful stage path sets are:

```text
PRE semantics commit: 4 paths
- semantics narrative
- PRE adapter canonical attestation
- PRE outer raw observation
- semantics machine

POST sync commit: 4 paths
- post narrative
- POST adapter canonical attestation
- POST outer raw observation
- post machine

FINAL commit: 2 paths
- FINAL adapter canonical attestation
- FINAL outer raw observation

TERMINAL observation commit: 1 path
- TERMINAL verifier outer raw observation
```

The verifier runs inside the TERMINAL observer while the terminal raw path is still absent and validates the five-layer package → approval → semantics → post → final chain. The observer writes the terminal raw record only after the verifier exits; that one path is then committed and pushed as the sixth layer. No circular self-verification is claimed. The terminal raw commit is reviewed by the next independent result review, and no further in-run verifier is authorized.

## Verifier Extension

`PRE_ATTESTATION` validates committed PRE and POST canonical attestations plus their exact binary outer observations, requires FINAL and TERMINAL observations absent, and checks the four-layer Git chain with 12 Git children.

`TERMINAL` validates PRE, POST, and FINAL canonical attestations and binary outer observations, requires the TERMINAL observation absent before its own process returns, and checks the five-layer chain with 14 Git children.

The fixed verifier stdout registrations are:

```text
PRE_ATTESTATION: 288 bytes / 6200026BD1307BAD32E81DF4EB274B3DCEBA221BA4B8E42AC14D44B45F2E14F8
TERMINAL:        302 bytes / 2E8086DC7196E3BE0A1A99A9D216CDD3B05F047411B54D5141B3242D31381FF5
```

## Static Validation

Package assembly performed:

```text
source/invocation/stdout identity checks: 34/34
source and alias fixtures: 12/12
binary format fixtures: 16/16
observer invocation/success/anchor/verifier integration fixtures: 15/15
total registered observer fixtures: 43/43
```

The binary fixtures reject wrong magic, version, header length, mode, completion flags, exit code, reserved value, stdout/stderr length underflow or overflow, truncation, trailing bytes, and stdout/stderr mutation.

No source was dot-sourced. Observer, capture host, adapter, parent, loader, target, verifier mode, frozen Git child, Python, evidence, synthetic, real-validator, preflight, official, Gold, reservation, and Stage3B execution counts are all zero.

Five package-validation helper attempts failed before a complete final result: one compact `foreach` parser error, one `return$false` command-resolution error, one modeled-command quote-construction error (`22/34`), one PowerShell automatic `$args` variable collision (`22/34`), and one diagnostic `Replace` new-character argument error. All five performed zero file writes and zero process starts. Corrected helpers passed source/invocation/stdout `34/34` and observer fixtures `12/12 + 16/16 + 15/15 = 43/43`.

## Required Future Approval Governance

Before any source/arguments/modeled-command reconstruction or execution, a new approval-governance commit must be created and pushed as the direct child of the actual package commit, with exactly:

```text
AGENTS.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_5_APPROVAL_DECISION.md
```

Before that push, only package commit identity, Manifest file identity, worktree/future-path state, and local/origin/direct-main equality may be checked.

## Only Requested Future Order

```text
1. New package-bound approval-governance commit and push.
2. Static source/invocation/parser gates.
3. PRE observer once.
4. Exact four-path semantics commit and push.
5. POST observer once.
6. Exact four-path post-sync commit and push.
7. FINAL observer once, including PRE_ATTESTATION verifier.
8. Exact two-path final commit and push.
9. TERMINAL observer once, including TERMINAL verifier.
10. Exact one-path terminal-observation commit and push.
11. Verify local/origin/direct main equality and clean worktree.
12. Create no further file or commit and stop.
```

All dynamic commit bindings must use actual full SHAs created and pushed in this future run. No future SHA may be guessed or reused.

## Failure Rule

Any source, parser, invocation, actual command line, binding, process start, drain, exit, `CreateNew`, binary write, raw length, stdout/stderr, classification, commit parent/path, push, chain, worktree, remote-triplet, or snapshot-stability failure consumes the applicable authorization and stops the chain.

Any partial raw observation must remain untouched. Retry, fallback, temporary script, alternate observer/adapter, source/runtime substitution, evidence overwrite or cleanup, reset, rebase, force-push, and partial continuation are forbidden.

## Explicitly Not Requested

```text
SYNTHETIC_REBINDING
REAL_PRECOMMIT_VALIDATOR
FORMAL_PREFLIGHT
OFFICIAL_INPUT_OR_TOKEN_ACCESS
OFFICIAL_CAPTURE
CONTROLLER_OR_VERIFIER_GOLD
RESERVATION
STAGE3B
```

## Requested Completion State

```text
AMENDMENT_5G_B_1_1_1_1_5_OUTER_OBSERVED_DURABLE_RAW_CHAIN_AWAITING_RESULT_REVIEW
```

The only permitted next action after a fully successful future chain is submission of the committed package, four stage records, and execution result for independent review.
