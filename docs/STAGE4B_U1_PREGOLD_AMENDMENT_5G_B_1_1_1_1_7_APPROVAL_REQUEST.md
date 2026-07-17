# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1.7 Approval Request

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Package date: 2026-07-17
- Direct parent / accepted Hard Failure 20 checkpoint: `d0dbc5533ddc464c7f7f1433d660ee7ddc355e07`
- Consumed approval governance: `1eb73132d47d5b21fceca9c88a42607ee3dff98d`
- Corrected 1.1.6 package: `0efbea018f4ad0e8650e254d313fb9cc85d2a28c`
- Future package commit: `MUST_BIND_THE_ACTUAL_COMMIT_CREATED_FROM_THIS_EXACT_PACKAGE`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_7_MANIFEST.json`
- Manifest bytes: 13,336
- Manifest SHA-256: `968C3D598840CA25A0DFB2F8006027158B5AFD9EDD48F78BEAE9C7363AFE8A3C`
- Package status: `AMENDMENT_5G_B_1_1_1_1_7_COMMAND_LINE_DIAGNOSTIC_PACKAGE_AWAITING_INDEPENDENT_APPROVAL`
- Package authorizes execution: No
- Other project conversations, project-external threads, and global memory used: No

## Requested Decision

```text
APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_7
DURABLE_OBSERVER_COMMAND_LINE_OBSERVATION_AND_EQUALITY_GATE_DIAGNOSTIC_ONLY

ONE_NEW_PACKAGE_BOUND_APPROVAL_GOVERNANCE_COMMIT
ONE_COMMAND_LINE_DIAGNOSTIC_OBSERVER_EXECUTION
ONE_COMMAND_LINE_OBSERVATION_RESULT
ZERO_CAPTURE_HOST_STARTS
IMMEDIATE_STOP_FOR_INDEPENDENT_REVIEW
```

This package does not itself authorize source parsing, source execution, actual-command-line reconstruction, observation creation, or any child process. A future approval must bind the actual package commit and this exact Manifest identity.

## Research And Failure Boundary

Hard Failure 20 established only that the prior observer process reached its own actual-command-line equality gate and exited 1. It did not preserve either operand. The failure occurred before capture-host invocation reconstruction, `ProcessStartInfo`, `Process.Start()`, or any new raw `CreateNew`.

This Amendment does not repair or retry the nested PRE chain. It only makes the two equality operands and their registered source strings durable for independent byte-level diagnosis.

## Exact Package Scope

The package commit must be the single direct child of `d0dbc5533ddc464c7f7f1433d660ee7ddc355e07` and change exactly these eight paths with zero deletions:

```text
AGENTS.md
README.md
docs/REPRODUCIBILITY.md
docs/ROADMAP.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_7_APPROVAL_REQUEST.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_7_MANIFEST.json
docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_20_REVIEW_1.md
scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_diagnostic.ps1
```

The future observation and Approval Decision paths must remain absent from this package.

## Frozen Diagnostic Observer

```text
path:
scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_diagnostic.ps1

source lines: 98
source bytes: 5,603
source SHA-256: 545A5A6E72D82C65B086F08D2FC64F3C359B1A0E453F271D1481013D62FC7307
encoding: ASCII-compatible UTF-8, LF, terminal LF
package-stage parser invocations: 0
parser status: NOT_RUN_PRE_APPROVAL_BY_REVIEW_BOUNDARY
```

The source contains no `ProcessStartInfo`, `Diagnostics.Process`, `Start-Process`, `.Start(`, capture-host path, or `Invoke-Expression` token. This is a text-level scope check, not a PowerShell syntax execution or parser claim.

The observer reads only the new Manifest and process-scoped package/approval commit bindings. It creates only the registered command-line observation. It contains no child-process construction or launch path.

## Frozen Invocation

```text
FileName:
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe

Arguments:
-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_diagnostic.ps1" -Mode COMMAND_LINE_DIAGNOSTIC

Arguments characters: 187
Arguments ASCII SHA-256: C4F5D93B17DBB3A31DFEA8D0F78B7FE23E16E5999F1E6EF1BA25E517FF95EC5A
Arguments UTF-16LE bytes: 374
Arguments UTF-16LE SHA-256: CCC055FB3EC15BB283BB03B9B48F21E17FFB884E12A2A6D83556F6C68059B9D8

Modeled command characters including terminal NUL: 248
Modeled command UTF-16LE bytes: 496
Modeled command UTF-16LE SHA-256: 9EB29E9C6C2ABFB8B45208648BE84756EC58F492B15A6489DCD69182EA16238E
```

The modeled string is exact quoted `FileName`, one U+0020 separator, complete `Arguments`, and one terminal U+0000. The stored actual string is the exact `.NET` `[Environment]::CommandLine` value without an added NUL. After durable close, the equality gate compares `actual + U+0000` against the modeled string, matching the prior gate semantics.

## `HGRAGC17` Binary Contract

The only future result path is:

```text
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_observation.bin
```

The fixed 88-byte little-endian header is:

| Offset | Type | Field |
|---:|---|---|
| 0 | 8 ASCII bytes | magic `HGRAGC17` |
| 8 | uint32 | format version `1` |
| 12 | uint32 | header bytes `88` |
| 16 | uint32 | completion flags `15` |
| 20 | uint32 | reserved `0` |
| 24 | uint64 | actual `.NET String.Length` |
| 32 | uint64 | modeled `.NET String.Length` |
| 40 | uint64 | executable `.NET String.Length` |
| 48 | uint64 | arguments `.NET String.Length` |
| 56 | uint64 | actual UTF-16LE byte length |
| 64 | uint64 | modeled UTF-16LE byte length |
| 72 | uint64 | executable UTF-16LE byte length |
| 80 | uint64 | arguments UTF-16LE byte length |

Payload order is actual, modeled, executable, arguments. Every string is encoded with strict UTF-16LE, no BOM. Character counts mean UTF-16 code units as returned by `.NET String.Length`. A complete record must satisfy all byte-length fields, every byte length must equal twice its character count, and total file length must close exactly.

## Durable Order And Equality Outcome

The future observer order is frozen as:

```text
1. load the registered FileName and complete Arguments
2. reconstruct the modeled string
3. read [Environment]::CommandLine without adding a NUL
4. materialize actual, modeled, executable, and arguments UTF-16LE bytes
5. CreateNew the observation path
6. write the fixed header and four raw payloads
7. Flush(true) and close
8. construct actual + U+0000 and perform the case-sensitive equality gate
9. exit 0 if equal or exit 1 if different
10. start no capture host or other child and stop
```

No SHA, first-difference calculation, prefix/suffix calculation, classification, or narrative is produced by the observer.

## Package Assembly Note

One read-only strict-JSON duplicate-key helper failed before opening the Manifest because Windows PowerShell corrupted double-quoted Python `-c` literals, producing a Python `<string>` syntax error. It performed zero project-file reads/writes, zero observer parser/execution, zero frozen-process starts, and zero evidence creation. The corrected helper used single-quoted Python literals and returned `STRICT_JSON_OK`; no duplicate key was found. This helper was not the observer and did not reconstruct an actual command line.

A second read-only helper failed before scanning any file because the local `rg.exe` process could not start (`Access is denied`). PowerShell `Select-String` then completed the same package-identity reference scan on the exact eight package paths. The failed launch performed zero project-file reads/writes, observer parser/execution, frozen-process starts, or evidence creation.

A third read-only final-validation helper used an incorrect assertion of 12 binary-header fields, while the registered 88-byte `HGRAGC17` contract correctly contains 13 fields: magic, version, header bytes, flags, reserved, four character counts, and four byte lengths. The helper read the exact eight package paths and failed only that assertion; it performed zero project-file writes, observer parser/execution, frozen-process starts, or evidence creation. The corrected 13-field assertion passed as part of the final static validation.

The first staged whitespace check found one extra blank line at EOF in the new Hard Failure 20 Review 1 document. It read the staged eight-path package and performed zero project-file writes, observer parser/execution, frozen-process starts, or evidence creation. The single blank line was removed; the corrected staged diff check is clean and no file was deleted.

The accompanying staged-index identity diagnostic correctly returned the Manifest and observer bytes/SHA-256 identities, but its optional line-ending counters matched literal backslash-plus-letter sequences and printed unusable `0/0` counts. Those counts are discarded. The helper read only those two staged blobs and performed zero project-file writes, observer parser/execution, frozen-process starts, or evidence creation; corrected counters use byte values 10 and 13.

## Requested Future Governance And Execution Order

If independently approved, the approval-governance commit must be the package's direct child and change exactly `AGENTS.md` plus the new Approval Decision. It must be pushed and synchronized before any observer parsing or execution.

Only after that push may the future approval authorize:

1. one PowerShell parser/static-contract gate with zero observer execution and zero evidence writes;
2. one observer process with actual package and approval-governance bindings;
3. zero capture-host, adapter, parent, loader, target, POST, FINAL, or TERMINAL processes;
4. preservation of the observation irrespective of equality exit 0 or 1;
5. if and only if the record is structurally complete, one exact one-path result commit and push as the approval-governance commit's direct child;
6. immediate stop for independent byte-level result review without calculating or asserting the difference type.

If the parser/static gate fails, the process does not start. If the observer fails before a complete durable record exists, result commit and push counts remain zero and the project stops for a separately governed hard-failure audit.

## Independent Review Contract

The next result review must calculate from raw bytes, not from package assumptions:

```text
actual and modeled character counts and SHA-256
first differing UTF-16 code-unit index
actual and modeled differing code units
common prefix and suffix lengths
whether the only raw difference is a terminal NUL
```

This package makes no prediction about those values.

## Explicitly Not Requested

```text
NESTED_PRE_CHAIN
CAPTURE_HOST
ADAPTER
PARENT
LOADER
TARGET_SCRIPTBLOCK
POST
FINAL
TERMINAL
SYNTHETIC_REBINDING
REAL_PRECOMMIT_VALIDATOR
FORMAL_PREFLIGHT
OFFICIAL_INPUT_OR_EXECUTION
CONTROLLER_OR_FORMAL_VERIFIER
GOLD
RESERVATION
STAGE3B
```

## Requested Completion State

```text
AMENDMENT_5G_B_1_1_1_1_7_COMMAND_LINE_OBSERVATION_COMMITTED_AWAITING_INDEPENDENT_REVIEW
```
