# Stage 4B U1-D Pre-Gold Amendment 5G-B.1.1.1.1.4 Approval Decision

## Decision

```text
APPROVE_SECOND_CORRECTED_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4_STAGE_COMMIT_ANCHORED_CANONICAL_BYTE_ADAPTER_ATTESTATION_CHAIN_ONLY

SECOND_CORRECTED_PACKAGE_APPROVED
PACKAGE_REVIEW_2_ACCEPTED
SCHEME_A_STAGE_ANCHORING_ACCEPTED

ONE_NEW_PACKAGE_BOUND_APPROVAL_GOVERNANCE_COMMIT_APPROVED
ONE_PRE_CAPTURE_HOST_EXECUTION_APPROVED
ONE_PRE_ADAPTER_EXECUTION_APPROVED
ONE_PRE_PARENT_LOADER_TARGET_SEMANTICS_CHAIN_APPROVED
ONE_EXACT_THREE_PATH_SEMANTICS_COMMIT_APPROVED
ONE_POST_CAPTURE_HOST_EXECUTION_APPROVED
ONE_POST_ADAPTER_EXECUTION_APPROVED
ONE_POST_PARENT_LOADER_TARGET_AUDIT_CHAIN_APPROVED
ONE_EXACT_THREE_PATH_POST_SYNC_COMMIT_APPROVED
ONE_FINAL_CAPTURE_HOST_EXECUTION_APPROVED
ONE_FINAL_ADAPTER_EXECUTION_APPROVED
ONE_PRE_ATTESTATION_VERIFIER_EXECUTION_APPROVED
ONE_EXACT_ONE_PATH_FINAL_ATTESTATION_COMMIT_APPROVED
ONE_TERMINAL_VERIFIER_EXECUTION_APPROVED

SYNTHETIC_REBINDING_NOT_APPROVED
REAL_PRECOMMIT_VALIDATOR_NOT_APPROVED
FORMAL_PREFLIGHT_NOT_APPROVED
OFFICIAL_INPUT_OR_TOKEN_ACCESS_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_VERIFIER_GOLD_NOT_APPROVED
RESERVATION_NOT_APPROVED
STAGE3B_NOT_APPROVED
```

Approval received: 2026-07-16 (Asia/Shanghai).

Approval source SHA-256: `E1E41FAEADDCA9455E8736D2A945DE2BB35F96CA87BE7F1EACB100131ABBFCA3`.

## Package-bound material passport

| Material | Frozen identity |
|---|---|
| Package commit | `683d17bd70cc32dca2e495836bb6b16160a79f79` |
| Direct parent | `61cfce1d3c11891ad0d8c2953fd855c2c3d0f9a8` |
| Manifest | `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4_MANIFEST.json`; 48,629 bytes; SHA-256 `E764A188AB11F49152B272F041CAC8FAC9477929C30475576D6349791E67373B` |
| Canonical builder | `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_adapter_attestation_canonical_builder.ps1`; 50 content lines; 4,361 bytes; SHA-256 `4409E8AFF4EFECE2A69404F42ED39C355CACE0BE2DFD2ACB6033D045142AF55D` |
| Capture host | `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_adapter_capture_attestation_host.ps1`; 211 content lines; 13,697 bytes; SHA-256 `74E5155D9488CC06C035E285E1D4B5715AFD0608350FD11E8021199441DA7A0C` |
| Dual-mode verifier | `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_terminal_adapter_attestation_commit_verifier.ps1`; 388 content lines; 33,878 bytes; SHA-256 `8D7BDF3224197C65CFB9A486DAA8E048AA0C86C88A87F75019036BF4A9D313D5` |

The rejected packages `7d2dcd5fe525c86ab2b91e7ed2dfb17b1e6228ac` and `61cfce1d3c11891ad0d8c2953fd855c2c3d0f9a8`, and the superseded approval `1afdd8075169e70d385e617ade480880cf3eb718`, are non-reusable.

## Adapter identities and registered stdout classes

| Stage | Adapter | Frozen identity | Registered class-bearing stdout variants |
|---|---|---|---|
| PRE | `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_pre_parent_start_orchestrator.ps1` | 136 content lines; 8,222 bytes; SHA-256 `6D9466FD227E8DA1ADB6A24CFC170BF9880C87718CB6244CC5847774BEBB8A02` | PRE / `EMPTY`; PRE / `EXACT_FROZEN_382_BYTE_STARTUP_CLIXML` |
| POST | `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_post_parent_start_orchestrator.ps1` | 138 content lines; 8,509 bytes; SHA-256 `89828EB855B64DACF98A76CFB2CAB956FEA29D2B6B80B187AE3BDA3A33EF9CC5` | POST / `EMPTY`; POST / `EXACT_FROZEN_382_BYTE_STARTUP_CLIXML` |
| FINAL | `scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_final_parent_start_orchestrator.ps1` | 125 content lines; 8,254 bytes; SHA-256 `3974D559EB41815E3E833AC15267A15A6F88AC289FA586148198211AAD246817` | FINAL / `EMPTY`; FINAL / `EXACT_FROZEN_382_BYTE_STARTUP_CLIXML` |

The six variants above bind the exact stdout byte-count/SHA registrations in the package-bound Manifest. No unregistered byte sequence or stderr class is permitted.

## Capture-host invocation bindings

All three invocations use `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` and the tracked capture-host source. The modeled command is the quoted executable, one space, the exact arguments, and terminal NUL.

| Stage | Exact arguments identity | Exact modeled-command identity | Fixed success stdout identity |
|---|---|---|---|
| PRE | 168 characters; SHA-256 `7E0C1B58AABB4DFAB04CD1E44E5382D8596440E90C5965FD94C74210589428EE` | 229 characters including terminal NUL; SHA-256 `5B596C77D5CBC4BD74D817C8CDCF79E01C09DC6BA1B79F41EA36C434F8EAD684` | 113 bytes; SHA-256 `C27FCA7A1D97D471F4797A897795541986FF78DEABAB63B934319176748FA7A6` |
| POST | 169 characters; SHA-256 `9BB4F5A4901C1F272336DC0658FCC76B8144682B85372730C28E8BF71C9A7004` | 230 characters including terminal NUL; SHA-256 `A74364D9D5D24128B1FDB93AA0433DE2A51D882AE224E6817BCB066D788507C0` | 114 bytes; SHA-256 `BBDF43E3376C0214F0A5781AF9AE6F0F464D22808BEB8D49F23A4123866C4757` |
| FINAL | 170 characters; SHA-256 `4E3FCAEFF4E4696252B0786F2993587BD269717C76E61AE1C36E1AA32EFF85B5` | 231 characters including terminal NUL; SHA-256 `803A476D94C89406C86BE2AF56C22238F3222F0A33159FE1F4FADCBD7C8640C6` | 115 bytes; SHA-256 `9A5FE24E095D1B03F69A028377946158703CC957BB10F175478E0A813D3468EB` |

The exact stage argument strings and invocation variant identifiers are the corresponding PRE, POST, and FINAL entries in the bound Manifest and are incorporated here without alteration.

## Verifier-mode invocation bindings

| Mode | Exact arguments identity | Exact modeled-command identity | Exact success stdout identity | Frozen process count |
|---|---|---|---|---|
| `PRE_ATTESTATION` | 191 characters; SHA-256 `A52FEF2C5FEB9B5FC8AEBB9E500FC4D2471D7D1B75C914A8F9375523A4B83DA8` | 252 characters including terminal NUL; SHA-256 `791D41E767A42DA66792689C919D9B63FC04E2E463B88F3F6EFD84B1DC5F0B70` | 265 bytes; SHA-256 `020A4546EE06325BBEE7EB78487DB0DF5DB0063CED2F7C0D16BE1393553A2F43` | verifier 1; Git children 12 |
| `TERMINAL` | 184 characters; SHA-256 `4803299461BFE530339695C0BB4B2C728763EE05A5E366160D9B319221169130` | 245 characters including terminal NUL; SHA-256 `B4F55D2EAF7D7835552DA584C05301E56CD1F359D6CC181D2C0F2D4E6689564E` | 279 bytes; SHA-256 `A27C36DDDE01616C351A169292A61362D2D20F0277969183325DAFA4154F1220` | verifier 1; Git children 14 |

## Exact stage anchoring

The approval-governance commit must have direct parent `683d17bd70cc32dca2e495836bb6b16160a79f79` and exactly these two paths:

```text
AGENTS.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4_APPROVAL_DECISION.md
```

The semantics commit must have the actual approval-governance commit as direct parent and exactly these three paths:

```text
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_VALIDATOR_SEMANTICS_AUDIT.md
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_pre_adapter_execution_attestation.json
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_validator_semantics.json
```

The post-sync commit must have the actual semantics commit as direct parent and exactly these three paths:

```text
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_POST_SYNC_TRANSPORT_AUDIT.md
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_post_adapter_execution_attestation.json
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_post_sync_transport_attestation.json
```

The final-attestation commit must have the actual post-sync commit as direct parent and exactly this one path:

```text
results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_4_final_adapter_execution_attestation.json
```

This is the frozen Scheme A `3/3/1` stage anchoring. Pending files, promotion, delayed anchoring, overwrite, or evidence cleanup are forbidden.

## Fixture registration

The approval binds the package registrations exactly as follows:

```text
INHERITED_SCHEMA_SEMANTICS_FIXTURES_30_OF_30
CORRECTED_PACKAGE_STATIC_FIXTURES_32_OF_32
SECOND_CORRECTED_PACKAGE_STATIC_FIXTURES_18_OF_18
```

These registrations are static package evidence only; they do not substitute for the approved one-pass runtime chain.

## Dynamic commit bindings

```text
HGRAG_EXPECTED_PACKAGE_COMMIT
= 683d17bd70cc32dca2e495836bb6b16160a79f79

HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT
= actual full SHA created and pushed in this execution

HGRAG_EXPECTED_SEMANTICS_EVIDENCE_COMMIT
= actual full SHA created and pushed in this execution

HGRAG_EXPECTED_POST_SYNC_AUDIT_COMMIT
= actual full SHA created and pushed in this execution

HGRAG_EXPECTED_FINAL_ADAPTER_ATTESTATION_COMMIT
= actual full SHA created and pushed in this execution
```

No future SHA may be guessed, prefilled, substituted, or reused.

## Only authorized order

1. Create and push the exact-two-path approval-governance commit.
2. Only after that push, validate the six tracked PowerShell sources, exact arguments, modeled commands, and parser state.
3. Execute the frozen PRE capture-host invocation once, producing the PRE canonical attestation and the inherited semantics evidence.
4. Create and push the exact-three-path semantics commit.
5. Execute the frozen POST capture-host invocation once, producing the POST canonical attestation and the inherited post-sync evidence.
6. Create and push the exact-three-path post-sync commit.
7. Execute the frozen FINAL capture-host invocation once; it starts the `PRE_ATTESTATION` verifier once and creates the FINAL canonical attestation.
8. Create and push the exact-one-path final-attestation commit.
9. Execute the same tracked verifier in `TERMINAL` mode once and require exact terminal success stdout.
10. Create no further file or commit and stop immediately.

## Failure handling

Any source, arguments, modeled-command, parser, actual command-line, process-start, exit-code, stdout/stderr registration, `CreateNew`, canonical-byte, commit-parent/path, push, chain, worktree, remote-triplet, or snapshot-stability failure immediately consumes the corresponding authorization and stops the chain.

Retry, fallback, temporary script, alternate adapter, source/runtime substitution, evidence overwrite or cleanup, reset, rebase, force-push, and partial continuation are prohibited.

## Success state and boundary

```text
AMENDMENT_5G_B_1_1_1_1_4_STAGE_ANCHORED_CANONICAL_BYTE_CHAIN_AWAITING_RESULT_REVIEW

PRE_CANONICAL_ATTESTATION_COMMITTED
SEMANTICS_EVIDENCE_COMMITTED_AND_PUSHED
POST_CANONICAL_ATTESTATION_COMMITTED
POST_SYNC_AUDIT_COMMITTED_AND_PUSHED
FINAL_CANONICAL_ATTESTATION_COMMITTED
TERMINAL_FIVE_LAYER_CHAIN_VERIFIED

SYNTHETIC_REBINDING_NOT_STARTED
REAL_PRECOMMIT_VALIDATOR_NOT_RUN
FORMAL_PREFLIGHT_NOT_STARTED
OFFICIAL_EXECUTION_NOT_STARTED
GOLD_NOT_APPROVED
```

After a successful one-pass chain, the only permitted next action is submission of the complete execution result for independent review. Fresh Synthetic Rebinding must not start automatically.
