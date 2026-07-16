# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1.4 Second-corrected Approval Request

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Package date: 2026-07-16
- Direct parent / rejected corrected package: `61cfce1d3c11891ad0d8c2953fd855c2c3d0f9a8`
- Rejected corrected package direct parent: `7d2dcd5fe525c86ab2b91e7ed2dfb17b1e6228ac`
- Hard Failure 17 checkpoint ancestor: `6c741c251dce55236b06dc5c06fd834b7649f8b2`
- Consumed approval governance: `1afdd8075169e70d385e617ade480880cf3eb718`
- Approved base package: `ef87f0379f4f31c54881c4a0e23a3f7ad8c8c35b`
- Rejected corrected Manifest: 41,597 bytes / `E0C0E8B329720C8B99130598E820E244E80707BAA628C1063688E209D067121A`
- Amendment title: Stage-commit-anchored canonical-byte adapter attestations with persisted capture-host invocations only
- Package revision: `SECOND_CORRECTED_AFTER_PACKAGE_REVIEW_2`
- Current status: `SECOND_CORRECTED_AMENDMENT_5G_B_1_1_1_1_4_STAGE_ANCHORED_CANONICAL_BYTE_ADAPTER_PACKAGE_AWAITING_APPROVAL`
- Execution authorized by this package: No
- Other project conversations, thread tools, and global memory used: No

## Package Review 2 Disposition And Second-correction Boundary

Package Review 2 accepts Package Review 1, corrected package `61cfce1d...` and its exact twelve-path scope, six class-bearing adapter stdout variants, the capture-host static design, the dual-mode verifier static design, the 1.1.4 Approval Decision compatibility correction, the four- and five-layer Git-chain designs, 30/30 inherited schema fixtures, reported 32/32 corrected fixtures, and the zero-execution assembly boundary.

It rejects corrected package `61cfce1d...` because PRE/POST attestations were not stage-commit anchored, OS-temp pending attestations remained mutable, canonical JSON bytes were not enforced, semantically equivalent or extended JSON could pass, capture-host stage invocation identity was not persisted, and the three capture-host invocation variants were not terminally validated.

This second correction selects the review-recommended Scheme A and changes only the adapter-attestation persistence and verification layer:

1. PRE attestation is directly created in the repository and included in the exact semantics commit;
2. POST attestation is directly created in the repository and included in the exact post-sync commit;
3. FINAL attestation is directly created in the repository and is the only path in the final-attestation commit;
4. one shared tracked canonical byte builder is loaded by both capture host and terminal verifier;
5. the terminal verifier rebuilds and byte-compares the unique canonical JSON and rejects alternate serialization; and
6. each stage attestation persists the stage-specific capture-host invocation identity, while the terminal verifier validates all three invocation envelopes.

It does not authorize approval governance or execution.

## Rejected Corrected Manifest Identity

    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4_MANIFEST.json
    41597 bytes
    E0C0E8B329720C8B99130598E820E244E80707BAA628C1063688E209D067121A

The identity above belongs to rejected corrected package `61cfce1d...`; it is preserved only as the review binding. Any future approval must bind the actual second-corrected package commit containing this Request, the final second-corrected Manifest, Package Review 2, six tracked PowerShell trust roots, and four updated navigation/governance documents. This Request does not authorize that approval-governance commit or any execution.

## Second-corrected Manifest Identity

    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4_MANIFEST.json
    48629 bytes
    E764A188AB11F49152B272F041CAC8FAC9477929C30475576D6349791E67373B

## Exact Second-corrected Package Scope

The second-corrected package commit must be the single direct child of rejected corrected package `61cfce1d3c11891ad0d8c2953fd855c2c3d0f9a8` and must change exactly eleven paths:

1. `AGENTS.md`;
2. `README.md`;
3. `docs/REPRODUCIBILITY.md`;
4. `docs/ROADMAP.md`;
5. `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4_APPROVAL_REQUEST.md`;
6. `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4_MANIFEST.json`;
7. `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4_PACKAGE_REVIEW_2.md`;
8. `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_adapter_attestation_canonical_builder.ps1`;
9. `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_adapter_capture_attestation_host.ps1`;
10. `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_final_parent_start_orchestrator.ps1`; and
11. `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_terminal_adapter_attestation_commit_verifier.ps1`.

No tracked file deletion is permitted.

## Unchanged Base Technical Registry

The 323,607-byte base Manifest with SHA-256 `804B4F8607532D6CE17EDE043D5A9511C7E855F4EB444C25F461381B6EDDA73D` remains immutable. The original nine source identities, six bounded envelopes, three raw-stdin payloads, parent/loader/target implementations, canonical parent outputs, frozen 382-byte CLIXML, original semantics and post evidence schemas, inherited final verifier, and 62/62 inherited fixtures are unchanged.

The correction changes the top-level adapter/evidence/terminal layer only. Gold, reservation, Stage3B, official input, and all scientific data remain outside the package.

## Three Class-bearing Tracked Adapters

Each adapter remains ASCII-only UTF-8 with terminal LF and zero parser errors:

| Adapter | Content lines | Bytes | SHA-256 |
|---|---:|---:|---|
| PRE | 136 | 8,222 | `6D9466FD227E8DA1ADB6A24CFC170BF9880C87718CB6244CC5847774BEBB8A02` |
| POST | 138 | 8,509 | `89828EB855B64DACF98A76CFB2CAB956FEA29D2B6B80B187AE3BDA3A33EF9CC5` |
| FINAL | 125 | 8,254 | `3974D559EB41815E3E833AC15267A15A6F88AC289FA586148198211AAD246817` |

The previously accepted `-File` invocation envelopes are unchanged:

| Adapter | Arguments chars / SHA-256 | Modeled chars including NUL / SHA-256 |
|---|---|---|
| PRE | 154 / `B01B7C9EC04B0D8D7953FD7FA9AF0CD85BAD69E3F0FCF5F39E761B1C39550726` | 215 / `34C461A85DA49F993A9461A5D016A5B7C424116C7E167EA098586EAEF7CFCF3C` |
| POST | 155 / `548F8440860C4B072672CFCAA65D39832EDABF2E1D9873FF80AEFAEF0099BB49` | 216 / `A178835B70993A7C35022BF0E6FA7C3B029070CE124DCC89AAA64265C296783F` |
| FINAL | 156 / `D8187DD2B190C6282D9D357A3FF0D33434F4AA77ACE68516DF6836C578F28C88` | 217 / `117BA16CE3ABB3205966F1B81866E8057A0CC410390CD9C488FFB85E65571F9D` |

Each adapter now emits the actual adapter-to-parent class. The six exact stdout variants are:

| Stage / parent class | Bytes | SHA-256 |
|---|---:|---|
| PRE / `EMPTY` | 164 | `7283CBBF86826C94E7E6DD19E1DF1270FF7C4F8E78E66B0F2C23D27645984371` |
| PRE / `EXACT_FROZEN_382_BYTE_STARTUP_CLIXML` | 195 | `820EDC7F9527298055FE2D9402096E764F0BF7F3537311919A3BF3E8C537168B` |
| POST / `EMPTY` | 165 | `BCAA66EBD85F334FE144B5AC5E22F360CFEF0AA6F88A63E4279EEDE20D565E78` |
| POST / `EXACT_FROZEN_382_BYTE_STARTUP_CLIXML` | 196 | `364D3838EF30B7744220DB5ABEE6C8E539CE61A37042834A2399A22F679F73C2` |
| FINAL / `EMPTY` | 166 | `EB17E3E3766359A64B558DAB8B9255E71A8E4060C68872AFEBE2D74E06D47101` |
| FINAL / `EXACT_FROZEN_382_BYTE_STARTUP_CLIXML` | 197 | `BBF6A971E601F4DC757F916F35B12998B7FF6B404B3F45168E043030C6843CFE` |

## Canonical Builder And Adapter Capture-attestation Host

The shared tracked canonical builder is 50 content lines / 4,361 bytes / SHA-256 `4409E8AFF4EFECE2A69404F42ED39C355CACE0BE2DFD2ACB6033D045142AF55D`. It emits strict UTF-8 without BOM or trailing newline, fixes schema `2.0`, field order, JSON escaping, integer rendering, null rendering, and the complete field set. Both capture host and terminal verifier validate and load this exact builder.

The tracked capture host is 211 content lines / 13,697 bytes / SHA-256 `74E5155D9488CC06C035E285E1D4B5715AFD0608350FD11E8021199441DA7A0C`, ASCII-only with terminal LF and zero parser errors. It is parameterized only by `PRE`, `POST`, or `FINAL` and must run exactly once per stage after a future package-bound approval.

For each stage it:

1. validates its own, the canonical builder's, and the selected adapter's tracked bytes/SHA;
2. validates the stage-specific capture-host invocation identity, requires `[Environment]::CommandLine + NUL` to equal that modeled command exactly, and validates the selected adapter's exact `-File` arguments/modeled-command identity;
3. starts exactly one selected adapter with the stage-appropriate frozen commit bindings;
4. concurrently captures raw adapter stdout/stderr;
5. accepts only a registered class-bearing stdout and exact-zero or frozen-382-byte outer stderr;
6. serializes canonical-builder, capture-host source and stage-invocation, adapter source and invocation, observed stdout, both observed stderr classes, commit bindings, and process counts through the shared canonical builder; and
7. directly writes exactly one stage repository attestation with `CreateNew`.

The three frozen paths are:

- `results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_pre_adapter_execution_attestation.json`;
- `results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_post_adapter_execution_attestation.json`; and
- `results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_final_adapter_execution_attestation.json`.

No pending or promotion path exists. PRE is included in the semantics commit, POST in the post-sync commit, and FINAL alone in the final-attestation commit. Any path collision fails closed.

## Dual-mode Final Verifier, Adapter-attestation Commit, And Terminal Mode

Static compatibility inspection found that the inherited 1.1.3 final verifier hard-coded the old `...1_1_1_1_3_APPROVAL_DECISION.md` path while corrected 1.1.4 governance correctly uses `...1_1_1_1_4_APPROVAL_DECISION.md`. Reusing that inherited verifier would therefore fail its approval changed-path gate. The corrected FINAL adapter instead starts the tracked dual-mode verifier directly with `-Mode PRE_ATTESTATION` and passes package, approval, semantics, and post commit bindings.

The dual-mode verifier is 388 content lines / 33,878 bytes / SHA-256 `8D7BDF3224197C65CFB9A486DAA8E048AA0C86C88A87F75019036BF4A9D313D5`, ASCII-only with terminal LF and zero parser errors. PRE_ATTESTATION invocation is 191 characters / `A52FEF2C5FEB9B5FC8AEBB9E500FC4D2471D7D1B75C914A8F9375523A4B83DA8`; its modeled command is 252 characters including NUL / `791D41E767A42DA66792689C919D9B63FC04E2E463B88F3F6EFD84B1DC5F0B70`. Its exact 265-byte success SHA-256 is `020A4546EE06325BBEE7EB78487DB0DF5DB0063CED2F7C0D16BE1393553A2F43`.

PRE_ATTESTATION mode validates all three adapters and invocation envelopes, all three capture-host invocation envelopes, six inherited bounded envelopes, three inherited raw-stdin payloads, seven original/historical evidence artifacts, the already committed canonical PRE and POST attestations, FINAL-attestation absence, rejected-transport absence, the corrected 1.1.4 Approval Decision path, exact four-layer package/approval/semantics/post chain and path sets, clean worktree, remote triplet, and artifact stability. It creates no file.

After PRE_ATTESTATION success and the FINAL adapter class is captured, the host directly writes the canonical FINAL repository attestation. Exactly that one result path must be committed and pushed as the direct child of the exact three-path post-sync audit commit.

TERMINAL invocation is 184 characters / `4803299461BFE530339695C0BB4B2C728763EE05A5E366160D9B319221169130`; its modeled command is 245 characters including NUL / `B4F55D2EAF7D7835552DA584C05301E56CD1F359D6CC181D2C0F2D4E6689564E`.

It independently validates:

- all three tracked adapter files;
- all three adapter `-File` invocation envelopes;
- the tracked canonical builder, capture host, and terminal verifier;
- all three capture-host stage invocation envelopes;
- all three execution-attestation schemas, exact canonical bytes, and commit bindings;
- all six observed stderr classes;
- mandatory adapter and parent process counts;
- semantics/post evidence presence and older-path absence;
- the exact five-layer package -> approval -> semantics -> post -> final-attestation chain;
- all five exact changed-path sets;
- clean worktree and local/origin/direct GitHub-main equality; and
- stability of every inspected artifact.

TERMINAL mode fixed success stdout is 279 bytes / SHA-256 `A27C36DDDE01616C351A169292A61362D2D20F0277969183325DAFA4154F1220`, and it creates no file or commit.

## Tightened Pre-approval Order

Before a future package-bound approval-governance commit is pushed, only corrected package commit/Manifest byte identity, clean worktree, required/future path state, and local/origin/direct-main equality may be checked. Joining, parsing, reconstructing, or executing any frozen source, arguments, modeled command, capture host, adapter, or verifier remains forbidden before that push.

## Requested Future One-pass Order

1. Create and push a new exact two-path package-bound approval-governance commit.
2. Invoke the PRE capture host once; it invokes the PRE adapter once and directly writes one canonical PRE repository attestation.
3. Commit and push exactly the semantics machine, semantics narrative, and PRE attestation.
4. Invoke the POST capture host once; it invokes the POST adapter once and directly writes one canonical POST repository attestation.
5. Commit and push exactly the post machine, post narrative, and POST attestation.
6. Invoke the FINAL capture host once; it invokes the FINAL adapter once, which invokes the dual-mode verifier once in PRE_ATTESTATION mode to validate the committed PRE/POST canonical attestations and four-layer chain; after return the host directly writes the canonical FINAL attestation.
7. Commit and push exactly the one FINAL adapter-attestation result path.
8. Invoke the same tracked dual-mode verifier once in TERMINAL mode.
9. On exact terminal success, create no further file or commit and stop immediately.

Any failure consumes the authorization. Retry, fallback, direct-parent bypass, temporary or alternate adapter, source/runtime substitution, attestation fabrication, evidence cleanup, reset, rebase, or force-push is forbidden.

## Package Assembly Boundary

    tracked second-corrected PowerShell sources: 6
    source identities passed: 6/6
    parser errors: 0/0/0/0/0/0
    inherited schema-semantics fixtures: 30/30
    corrected static package fixtures: 32/32
    second-corrected static package fixtures: 18/18

    capture-host processes: 0
    adapter processes: 0
    parent processes: 0
    loader processes: 0
    target ScriptBlock invocations: 0
    Git children from frozen sources: 0
    Python processes: 0
    pending or repository evidence creations: 0
    synthetic runs: 0
    official operations: 0

Seven second-correction read-only helper attempts failed: local `rg.exe` returned access denied; two source-identity helper attempts repeated a PowerShell empty-pipe parser error; two compact helper attempts omitted whitespace after `in`; one fixture helper named its hash function `H`, which PowerShell resolved as `Get-History`; and one Manifest-reference helper incorrectly used `try` as an inline expression. Corrected helpers subsequently passed. All failures caused zero project writes, zero frozen processes, and zero evidence. The prior corrected/rejected-package helper failures remain preserved in the Manifest audit.

The six current working-tree sources are verified as LF. Repository `core.autocrlf=true` and no `.gitattributes` file exists; therefore every future capture/terminal source-identity gate remains exact-byte and fail-closed if Git ever rewrites a source checkout.

## Explicit Non-authorization

This second-corrected package does not authorize approval governance; any capture host, adapter, parent, loader, target, inner verifier, canonical builder at runtime, or terminal verifier; semantics, post, or repository evidence creation; any Git evidence commit; synthetic rebinding; real precommit validation; formal preflight; official input/token/capture; controller/verifier/Gold; reservation; or Stage3B.

## Current State

    HARD_FAILURE_17_AUDIT_ACCEPTED
    HARD_FAILURE_17_CHECKPOINT_FROZEN
    PACKAGE_REVIEW_1_REJECTION_PRESERVED
    PACKAGE_REVIEW_2_REJECTION_PRESERVED

    THREE_CLASS_BEARING_TRACKED_ADAPTERS_FROZEN
    SIX_CANONICAL_ADAPTER_STDOUT_VARIANTS_FROZEN
    SHARED_CANONICAL_ATTESTATION_BYTE_BUILDER_FROZEN
    ADAPTER_CAPTURE_ATTESTATION_HOST_FROZEN
    THREE_VERSIONED_ADAPTER_ATTESTATION_PATHS_FROZEN
    PRE_SEMANTICS_COMMIT_ANCHOR_FROZEN
    POST_SYNC_COMMIT_ANCHOR_FROZEN
    FINAL_ONE_PATH_ATTESTATION_COMMIT_ORDER_FROZEN
    THREE_CAPTURE_HOST_STAGE_INVOCATIONS_DURABLY_ATTESTED
    TERMINAL_ADAPTER_ATTESTATION_COMMIT_VERIFIER_FROZEN

    BASE_NINE_SOURCES_SIX_ENVELOPES_THREE_PAYLOADS_UNCHANGED
    SCHEMA_SEMANTICS_FIXTURES_30_OF_30_PASS
    CORRECTED_STATIC_PACKAGE_FIXTURES_32_OF_32_PASS
    SECOND_CORRECTED_STATIC_PACKAGE_FIXTURES_18_OF_18_PASS
    PACKAGE_ASSEMBLY_EXECUTION_COUNT_ZERO

    SECOND_CORRECTED_AMENDMENT_5G_B_1_1_1_1_4_PACKAGE_AWAITING_APPROVAL
    EXECUTION_NOT_AUTHORIZED

    PRE_NOT_APPROVED
    POST_NOT_APPROVED
    FINAL_NOT_APPROVED
    SYNTHETIC_REBINDING_NOT_APPROVED
    REAL_PRECOMMIT_VALIDATOR_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_EXECUTION_NOT_APPROVED
    GOLD_NOT_APPROVED
    RESERVATION_NOT_APPROVED
    STAGE3B_NOT_APPROVED
