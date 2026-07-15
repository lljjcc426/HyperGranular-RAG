# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1.3 Bounded-STDIN Transport Recovery Approval Request

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Request date: 2026-07-15
- Requested decision: APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_BOUNDED_COMMAND_LINE_RAW_STDIN_BASE64_SOURCE_TRANSPORT_RECOVERY_ONLY
- Current checkpoint: f28fc526faf74f80fdefb96ca189769dbcf1e5e4
- Current execution authority: NONE UNTIL A NEW APPROVAL BINDS THE FUTURE PACKAGE COMMIT
- Official execution: NOT_REQUESTED
- Other project conversations, thread tools and global memory used: No

## Review Basis

Hard Failure 16 Review 1 accepts package `945f655b95cfee9e55ad2d20e7bd5018f9aee1e2`, approval governance `72783071c17f6e3cab347823a8da080171c1a883`, checkpoint `f28fc526faf74f80fdefb96ca189769dbcf1e5e4`, the one static reconstruction and the one consumed process-start attempt. The PowerShell process was never created; every downstream process and evidence count remained zero.

The established root cause is the frozen 38,599-character EncodedCommand transport exceeding the Windows process command-line limit. Microsoft documents a maximum `CreateProcessW` command-line string of 32,767 characters including the terminating null: [CreateProcessW documentation](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw).

Windows PowerShell 5.1 documents redirected standard-input command handling: [about_PowerShell_exe](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_powershell_exe?view=powershell-5.1). This package does not send target source as implicit text. It freezes a short target-specific loader in EncodedCommand and sends the large target source as strict ASCII Base64 through `StandardInput.BaseStream`.

## Bound Commits And Manifest

    approved second corrected package:
    945f655b95cfee9e55ad2d20e7bd5018f9aee1e2

    consumed approval governance:
    72783071c17f6e3cab347823a8da080171c1a883

    Hard Failure 16 checkpoint:
    f28fc526faf74f80fdefb96ca189769dbcf1e5e4

    unchanged source Manifest:
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_2_MANIFEST.json
    227242 bytes
    69CA3DAD8664F12213933A603D0AE0955C8AC17E483E5DC433859839AD49086E

    Amendment 5G-B.1.1.1.1.3 Manifest:
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_MANIFEST.json
    203974 bytes
    DF088593BA620CE235419B2B759247914771FCFCE63B49A099A788AD29D5FC1C

Any approval that does not explicitly bind the future package commit containing this Request and Manifest is invalid. The consumed approval at `72783071...` cannot be reused.

## Frozen Historical Evidence And Classifier

The three Hard Failure 15 machine files retain their exact registered identities:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stdout.bin` | 122 | `BCDF0010147E5952AD0372ADF39EDA0A18D349B02107C340DEF05BAFE18C0F09` |
| `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stderr.bin` | 382 | `4F2B6B3ED9201CA459DB2DD042E0A137C4E58BFE8E15A068E45AD8535FA5B1EF` |
| `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_diagnostic.json` | 944 | `F4022C8B4DF507D9A63085698B846358FF6D33F2A67B55B0C54EB871E8EB101B` |

The only accepted PowerShell stderr classes remain `EMPTY` and `EXACT_FROZEN_382_BYTE_STARTUP_CLIXML`. Exact byte count and byte-for-byte equality are required. Git, Python and every non-PowerShell child stderr remain strict zero.

## Unchanged Business And Verification Sources

The bounded-stdin recovery does not modify these accepted source identities:

| Source | Lines | UTF-8 bytes | SHA-256 |
|---|---:|---:|---|
| Pre/semantics outer runner | 194 | 14,491 | `6B24A6F25B5ABF4212A14D16E58EB569015C1D41EEB5587E70C9CD6C5E3CE124` |
| Post-sync outer runner | 166 | 12,149 | `0BC1EDF07495CEAF01502EBF0FCEAA2C77E08A857A2B91AE4AA2E0DB451DD35A` |
| Pre host | 96 | 6,816 | `61EA2A37C66EF5D59299F91E045F918D5A8DD02E961DE278142584E7515E50FB` |
| Revised recovery harness | 91 | 7,857 | `DD11F1E6592CAD904ED5B25CD007AE46474319B7FD6036166C390BB28EB73931` |
| Revised bootstrap | 109 | 8,325 | `84D6868A4DF279D4EA755E64986CC9549FB86B45998848CA3278A1A6B871FEB7` |
| Post host | 86 | 6,377 | `430C0F64ECD940BDDA7CDE098E156629F914027023EE6306ED9084AB72E8853D` |
| Pre verifier | 74 | 4,114 | `4A5A4BBE08661D588673C4B4A1A7ABAB88FEB2999699658CBC91E8081266EB66` |
| Post verifier | 107 | 7,130 | `8877E18F75A94EE6DA326B09C3791E6641B6B9B32D42744BA23E033A20735A67` |
| Compatible verifier | 59 | 3,512 | `1A30DC70AD0C01CDACBC3279F1CFD707EA4DAB457BE9C6C30A5C6D6495FA81BF` |
| Semantics wrapper | 122 | 7,890 | `DFA95A904CE371F283B8DBA8BB4D98CC048F345F536C0E7D0D6DB8073DF9E16C` |
| Embedded Python | 46 | 2,284 | `D0D3D6FC37AD0C2649A7A7F88EFA944C357033E3F0E956BE0E27C4374653D602` |

The real precommit validator remains unchanged but is not authorized to run.

## Rebound Final Verifier

The final verifier keeps its eleven Git commands, strict schemas, exact path sets, artifact-stability gates and fixed success stdout. Its package Manifest identity and approval-decision path are rebound to Amendment 5G-B.1.1.1.1.3 so that the future approval commit can use a new immutable Decision file.

    lines: 164
    UTF-8 bytes: 12955
    source SHA-256: AAF4B1C0638DDC10D7D8C4B0BC64A4BBFAE8E3B22EB47622E0E3F19C28D07AA0
    static parser errors: 0

    fixed success stdout bytes: 195
    fixed success stdout SHA-256: 3EFE3ED534AB9DFE39DA5C8DA3297C7AB43C513D4032B061DF09C474E9946DE5

The old 34,447-character final-verifier EncodedCommand transport is marked non-reusable. The rebound source is transported only through `FINAL_VERIFIER_STDIN_LOADER`.

## Three Target-Specific Loaders

Each loader is a complete LF-joined, no-trailing-newline Windows PowerShell 5.1 source with zero static parser errors. Its own short source is transported by EncodedCommand; the target source is not placed on the command line.

| Loader | Lines | UTF-8 bytes | Source SHA-256 | Arguments chars / SHA-256 | Modeled full command line chars / SHA-256 | Margin to 32,767 |
|---|---:|---:|---|---|---|---:|
| `PRE_AND_SEMANTICS_STDIN_LOADER` | 44 | 2,727 | `87B30CA96AD94C9DA865F4BCA9D9BE5C32728AF758BE4D2B6F8B9FAB7E6C5049` | 7,323 / `5C0A0101BD24118AD8E338158134DE1F64C8248142211D671ED1947344388B7F` | 7,384 / `DA89A4F1CA7B2D59F3872CFEA2020E8A7A78B54774AF97522C6DA16644228323` | 25,383 |
| `POST_SYNC_STDIN_LOADER` | 44 | 2,719 | `9184297CD2A42B9D78B542DFC73F71BADD7C65E36F701DE793A88EFF831C5BB4` | 7,303 / `6D87AA8CD65EC8D9D2434CF1D40FEA80103F74BAF36941ABDEA5ECAE5B28E360` | 7,364 / `27354A8BD335EA045966407A5D847E01D097FAE098BA8E308C36597A9C1135E8` | 25,403 |
| `FINAL_VERIFIER_STDIN_LOADER` | 44 | 2,724 | `F965E9B183F6EDBF11B8842E2353AE12B34AB967578DFECE85FEF2F136BEA0C6` | 7,315 / `6DF16FFCED9F411CC4668DBBE23895CE4BFEB294EC15CBD7CD4E8FBD73FF8131` | 7,376 / `C3685BD869692BC2FFE19E32FDB4F20C18AF6569BB8EFDF10AFD527A9B1D4C1A` | 25,391 |

The modeled full command line is exactly `"<FileName>" <Arguments><terminal-null>`. Its character count and ASCII SHA include the terminal null. Every loader is materially below the documented limit.

## Frozen Raw-STDIN Payloads

The target source is encoded as UTF-16LE, converted to Base64, then written as exact ASCII bytes to raw stdin. EOF must follow the registered payload with zero extra bytes.

| Target | ASCII/Base64 bytes | ASCII SHA-256 | Decoded UTF-16LE bytes / SHA-256 | Decoded source identity |
|---|---:|---|---|---|
| Pre/semantics runner | 38,548 | `7B58717F69699A7D8B48F58D680196A99A14B1F602FFE8C340C899D73849BFF2` | 28,910 / `7261310F0A8FDBA756D449B9B3CA7B4318280E4DB4BC62AA9B96679F7D767DB9` | 194 lines / 14,491 bytes / `6B24A6F2...CE124` |
| Post-sync runner | 32,280 | `B9822E0E8A27C1870CAD4D3D3F3768AB989271090DE5CBEB318F0A96236D9AEA` | 24,210 / `FC5C73EDA20F6115A395ADBDE09B7695D9FB15DD40B3CB7BDF1EA768DA31D0ED` | 166 lines / 12,149 bytes / `0BC1EDF0...DD35A` |
| Final verifier | 34,452 | `D77B9C5682042E67AA87A6A581FF3A99A0F12DE849D1AEAE371028EE3FD218EC` | 25,838 / `75220E606D9BD4D73A6AFB7AE63550C414D51E679BD8AA7552C2197224E41641` | 164 lines / 12,955 bytes / `AAF4B1C0...07AA0` |

The loader reads stdin raw bytes to EOF, rejects non-ASCII, requires the exact raw byte count and SHA, Base64-decodes, requires decoded UTF-16LE count/SHA, decodes with strict Unicode, requires target line/UTF-8 byte/SHA identities, requires zero parser errors, creates one ScriptBlock and invokes it once in the same PowerShell process. The loader adds no stdout.

## Frozen Parent Transport Order

For pre/semantics and post-sync top-level transport, the future host must execute exactly:

1. Reconstruct and verify the target-specific loader source, EncodedCommand arguments and modeled full command line.
2. Reconstruct and verify the target source and exact stdin payload.
3. Start one loader-backed PowerShell process.
4. Immediately start concurrent raw stdout/stderr BaseStream drains.
5. Write the exact ASCII Base64 bytes to `StandardInput.BaseStream`.
6. Flush and close stdin.
7. Wait for the process and both drain tasks.
8. Require exit zero, exact unchanged target stdout and an allowed exact PowerShell stderr class.

`StreamWriter` and implicit text encoding are prohibited. No temporary `.ps1`, `-File`, command shortening or alternate runtime is allowed.

## Revised Final Host

The revised host reconstructs the rebound final verifier and `FINAL_VERIFIER_STDIN_LOADER` from the new Manifest. It verifies loader source/arguments/full modeled command line, builds and verifies the exact final-verifier stdin payload, sets the three process-scoped commit bindings, starts one loader-backed child, starts both raw output drains, writes stdin via BaseStream, closes stdin and then applies the original fixed verifier-output and exact stderr-class gates.

    lines: 92
    UTF-8 bytes: 7373
    source SHA-256: F3AE0903C7E8923179D6EE721467F772D6EAAC165BE0CC3B4016A280DA13CDC9
    static parser errors: 0

    complete arguments characters: 19691
    complete arguments SHA-256: 644F8784738ED6F490B8FE623EC1C5B73378293A4B90E6791217112DAC1EE58D
    modeled full command line characters: 19752
    modeled full command line SHA-256: 98C1CB4CBFB3E0D29D71D38626C522BC3EDD7EE1834AF12CB0C4EA6F39477EA4
    margin to limit: 13015

Its two canonical success stdout variants remain 187 bytes / `731D29698B85F99FC2612219DE22F836935E4566918B7109C3407B85D2672716` and 218 bytes / `E63603112054AD24A55CE81ABDFEF95D25DD95AEEDF0AA879734999F86E194A9`.

## Transport-Only Static And Negative Fixtures

Package assembly used an independent in-memory reference validator and did not execute a loader or ScriptBlock. For each of the three loaders, all ten registered fixtures passed:

1. short modeled full command line below 32,767;
2. exact stdin payload accepted;
3. truncated payload rejected;
4. appended byte rejected;
5. same-length mutation rejected;
6. invalid Base64 rejected;
7. decoded UTF-16LE mutation rejected;
8. source SHA mismatch rejected;
9. extra bytes after the payload rejected;
10. parser-error payload rejected.

Total result: 30/30. A negative fixture may be rejected by an earlier exact raw-identity gate before reaching a later defense-in-depth parser gate; no mutated payload is accepted.

Four read-only package-assembly helper failures are preserved in the Manifest: a missing space after PowerShell's `throw` keyword stopped the first final-validation helper before its validation body; a later identity-location command completed its `Select-String` step but could not start `rg.exe` because access was denied; its PowerShell-only retry used an invalid trailing-backslash exclusion regex, so its emitted search errors made that search unusable despite exit zero; and the first complete validation body expected a short revision label rather than the frozen descriptive revision and stopped at that identity assertion before source reconstruction. Across all four failures there were zero file writes, zero created child processes, zero frozen-source invocations, zero evidence creations and zero official operations.

No transport probe execution is requested in this package.

## Requested Approval-Governance Commit

If approved, the first future commit must be the exact two-path direct child of the future Amendment 5G-B.1.1.1.1.3 package and change only:

    AGENTS.md
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_APPROVAL_DECISION.md

It must be pushed before any loader or target source reconstruction.

## Requested One-Time Order

1. Create and push the exact-two-path approval-governance direct child.
2. Reconstruct and run one pre/semantics loader-backed PowerShell process; invoke the pre/semantics target ScriptBlock once and require its exact success.
3. Allow the unchanged pre host/verifier and bootstrap/harness/compatible-verifier/wrapper/Python chain only within that exact successful target invocation.
4. Exclusive-create the exact 789-byte machine evidence and pre/semantics narrative.
5. Create and push the exact-two-path semantics evidence direct child of approval governance.
6. Reconstruct and run one post-sync loader-backed PowerShell process with the actual approval-governance SHA; invoke the post target ScriptBlock once and require exact success.
7. Exclusive-create the two post-sync audit paths.
8. Create and push the exact-two-path post-sync audit direct child of the semantics evidence commit.
9. Reconstruct and run one revised final host with actual package, approval-governance and semantics-evidence SHAs.
10. The final host starts one final-verifier loader-backed child, which invokes the final verifier ScriptBlock once and exactly eleven Git children.
11. Require one exact final-host success variant; create no file or commit and stop immediately.

Any failure consumes the ordered authorization. No retry, fallback, transport substitution, source modification, cleanup, overwrite, reset, rebase or force-push is allowed.

## Requested Counts

    approval-governance commits: 1
    pre loader-backed PowerShell processes: 1
    pre target ScriptBlock invocations: 1
    pre host / pre verifier processes: 1 / 1
    pre-verifier Git children: 5
    bootstrap / harness / compatible verifier / wrapper / Python: 1 / 1 / 1 / 1 / 1
    semantics machine / narrative creations: 1 / 1
    semantics evidence commits: 1

    post loader-backed PowerShell processes: 1
    post target ScriptBlock invocations: 1
    post host / post verifier processes: 1 / 1
    post-verifier Git children: 7
    post machine / narrative creations: 1 / 1
    post audit commits: 1

    revised final-host processes: 1
    final-verifier loader-backed PowerShell children: 1
    final-verifier ScriptBlock invocations: 1
    final-verifier Git children: 11
    files or commits after final success: 0

    synthetic rebinding: 0
    real precommit validator: 0
    formal preflight: 0
    official input accesses: 0
    authorization token uses: 0
    official captures: 0
    controller/verifier/Gold operations: 0
    automatic retries: 0

## Package-Assembly Audit

    source designs: 7
    source static parser errors: 0
    transport fixture groups: 3
    fixtures per group: 10
    fixtures passed: 30
    loader processes: 0
    target ScriptBlock invocations: 0
    PowerShell/Git/Python child processes: 0
    evidence creations: 0
    official operations: 0

The seven source designs are three target-specific loaders, two unchanged outer targets, the rebound final verifier and the revised final host. Package assembly did not execute any of them.

## Three Dynamic Environment Bindings

The revised final host must receive:

    HGRAG_EXPECTED_PACKAGE_COMMIT
    = future approved Amendment 5G-B.1.1.1.1.3 package commit

    HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT
    = actual future approval-governance commit

    HGRAG_EXPECTED_SEMANTICS_EVIDENCE_COMMIT
    = actual pushed and post-verified semantics evidence commit

No value may be guessed or substituted.

## Explicitly Not Requested

- execution during package assembly;
- reuse of the consumed `72783071...` approval;
- modification of the unchanged pre/post target logic or inner sources;
- temporary `.ps1`, `-File`, direct source text on stdin or StreamWriter transport;
- a transport probe execution;
- synthetic rebinding, real validator, fresh three-path or derived-HEAD work;
- formal preflight, official input/token/capture;
- controller, formal verifier, evaluator/Gold, reservation or Stage3B.

## Current Stop State

Until an independent approval explicitly binds the future package commit:

    HARD_FAILURE_16_AUDIT_ACCEPTED
    HARD_FAILURE_16_CHECKPOINT_FROZEN
    ROOT_CAUSE_ESTABLISHED_ENCODED_COMMAND_COMMAND_LINE_OVERFLOW
    CURRENT_APPROVAL_CONSUMED
    CURRENT_LONG_ENCODED_COMMAND_TRANSPORT_NOT_REUSABLE

    AMENDMENT_5G_B_1_1_1_1_3_BOUNDED_STDIN_TRANSPORT_PACKAGE_AWAITING_APPROVAL
    APPROVAL_GOVERNANCE_NOT_APPROVED
    LOADER_EXECUTION_NOT_APPROVED
    TARGET_SCRIPTBLOCK_INVOCATION_NOT_APPROVED
    SEMANTICS_SEQUENCE_NOT_APPROVED
    POST_SYNC_NOT_APPROVED
    FINAL_VERIFIER_NOT_APPROVED
    SYNTHETIC_REBINDING_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_EXECUTION_NOT_APPROVED
    GOLD_NOT_APPROVED
