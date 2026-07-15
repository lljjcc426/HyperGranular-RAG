# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1.2 Second Corrected Approval Decision

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Approval date: 2026-07-15
- Decision: APPROVE_SECOND_CORRECTED_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_2_FROZEN_EIGHT_SOURCE_TRANSPORT_RECOVERY_AND_FINAL_POST_SYNC_AUDIT_COMMIT_VERIFICATION_ONLY
- Package: 945f655b95cfee9e55ad2d20e7bd5018f9aee1e2
- Hard Failure 15 checkpoint: 95f68e7b2afdf6ed46c4eebe604d13744b26760a
- Synthetic rebinding: NOT_APPROVED
- Real precommit validator: NOT_APPROVED
- Formal preflight: NOT_APPROVED
- Official execution and Gold: NOT_APPROVED
- Other project conversations, thread tools and global memory used: No

## Frozen Governance Trust Root

This approval strictly binds:

    second corrected package:
    945f655b95cfee9e55ad2d20e7bd5018f9aee1e2

    direct parent / rejected first corrected package:
    44e56ab955dfe5fe89cc8ec4343870b59d008c9a

    rejected original package:
    7f92c000bb3c22337c83dc28e32779f4eb9cfdf8

    Manifest:
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_2_MANIFEST.json
    227242 bytes
    69CA3DAD8664F12213933A603D0AE0955C8AC17E483E5DC433859839AD49086E

The two rejected packages remain not approvable, not executable and not reusable. No source, transport, argument, classifier, stdout, evidence path, process count or order outside the bound package and Manifest is authorized.

## Approval-Governance Commit

The first and only approval-governance commit must be the direct child of `945f655b95cfee9e55ad2d20e7bd5018f9aee1e2` and change exactly:

    AGENTS.md
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_2_APPROVAL_DECISION.md

It must be pushed before any frozen `source_lines` are reconstructed or any process starts. After push, the worktree must be clean, all three historical machine files must retain their exact identities, and all four semantics paths plus both post-sync audit paths must remain absent.

## Frozen Historical Evidence And Classifier

The following files must remain byte-for-byte unchanged before, during and after the authorized chain:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stdout.bin` | 122 | `BCDF0010147E5952AD0372ADF39EDA0A18D349B02107C340DEF05BAFE18C0F09` |
| `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stderr.bin` | 382 | `4F2B6B3ED9201CA459DB2DD042E0A137C4E58BFE8E15A068E45AD8535FA5B1EF` |
| `results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_diagnostic.json` | 944 | `F4022C8B4DF507D9A63085698B846358FF6D33F2A67B55B0C54EB871E8EB101B` |

The only accepted PowerShell stderr classes are exact zero bytes (`EMPTY`) and byte-for-byte equality with the frozen 382-byte payload (`EXACT_FROZEN_382_BYTE_STARTUP_CLIXML`). The payload SHA-256 is `4F2B6B3ED9201CA459DB2DD042E0A137C4E58BFE8E15A068E45AD8535FA5B1EF`; its 512-character Base64 SHA-256 is `1A3D87C52A5EB3036EE762D586A05D21A3080106A0E38AE3B75DC0C44BC8700B`. Git, Python and every non-PowerShell child stderr remain strict zero.

## Eight Frozen Sources And Transports

Every source is LF-joined with no trailing newline, transported only through Windows PowerShell 5.1 `-NoLogo -NoProfile -NonInteractive -EncodedCommand <UTF-16LE Base64>`, and must statically parse with zero errors before its one authorized start.

| Source | Lines | UTF-8 bytes | Source SHA-256 | Complete arguments chars | Complete arguments SHA-256 |
|---|---:|---:|---|---:|---|
| Pre host | 96 | 6,816 | `61EA2A37C66EF5D59299F91E045F918D5A8DD02E961DE278142584E7515E50FB` | 18,131 | `3E607852CC486C83A141A6B1FEC84D27DB90762C178DC44EDA11E74EDA1C9C26` |
| Revised recovery harness | 91 | 7,857 | `DD11F1E6592CAD904ED5B25CD007AE46474319B7FD6036166C390BB28EB73931` | 20,971 | `0D67DD29A0BA9392A141C007E9A348A1CF01BC0A6C752A789FE725F826ACE427` |
| Revised bootstrap | 109 | 8,325 | `84D6868A4DF279D4EA755E64986CC9549FB86B45998848CA3278A1A6B871FEB7` | 22,155 | `262AAA9D6B1D6D234C273ECC7302DDFF8BE7AFD568547EE66F9DCD68E71C4F58` |
| Post host | 86 | 6,377 | `430C0F64ECD940BDDA7CDE098E156629F914027023EE6306ED9084AB72E8853D` | 17,003 | `0180906B8EF51BC45BA4303FC545E9591A5E51529D27E7309A0B6BAF403BC5A3` |
| Pre/semantics outer runner | 194 | 14,491 | `6B24A6F25B5ABF4212A14D16E58EB569015C1D41EEB5587E70C9CD6C5E3CE124` | 38,599 | `53D27DD17FC3D4E6E8708E970C2BEFA4932AAE511A99D6EDF4A0BDFA9B498753` |
| Post-sync outer runner | 166 | 12,149 | `0BC1EDF07495CEAF01502EBF0FCEAA2C77E08A857A2B91AE4AA2E0DB451DD35A` | 32,331 | `D55D3A04713814348752C5081F91B4FB41C52E68936657CC77905B5F9FC20ABC` |
| Final post-sync audit commit verifier | 164 | 12,934 | `C0D96FD117FF3387497FF622524F1D9A0C025FB8502BBBD83F0CC32DD96D2B2B` | 34,447 | `FB42C1883064B15FEEEB2FAE98D3A9680FA573644A29B0B586562EF8A8BAF5B2` |
| Final verifier host | 81 | 6,024 | `C843B63E79EED1882E7A47EB063268A3DBCEE2CC1621E7C790F5830A7A691131` | 16,095 | `74D0EB12BAA4B23C46314130084F88678C24A2C073ECE075FE8A60CA20FE6272` |

The unchanged pre verifier, post verifier, compatible verifier, semantics wrapper, embedded Python and real validator remain bound exactly as registered in the Manifest. The real validator is not authorized to run.

## Canonical Stdout Registry

Raw stdout must equal one registered byte sequence. Semantic JSON equivalence is insufficient.

| Boundary | Variant byte counts / SHA-256 |
|---|---|
| Pre host | `163 / 978F5FD4948478C02CA63F5DBDC825B47BB1E058291FAD405D159D6B7E356A2B`; `194 / EE73196CDF4567218E6D4236E33CEFD989EC5A0226F422FD921BF58F4097E695` |
| Harness | `1213 / 0AF1D8CDA248153CFBD82714EFE6B5FF3ABDA22F65604F6F51DB1885148F7EF4`; `1244 / 0FB92E7AA00557ED43125AC946CD421DE571B62CB21BD9F84310A50A16A4E7B0`; `1244 / 098041C0326E1A19B73F73F93012A65069956557F89209FC9E27BDB04F6B2DF1`; `1275 / 9B37793023DCA4E8F0D83473C78ACAA2E17DB6D6CECFCD7ADF6D118EFD6FC643` |
| Bootstrap | `194 / 7957FCEB25C6E5F5DE02E52DB6C2B911A13FBFBB045E2EED22F18498E20340DD`; `225 / 26C64CC10C0D45A4D1B1D1C1BE34C4B1894588C6609D7E6B2182FC6F7D78B667`; `225 / B3E190CFD23736C39A3BC2A7E4DBE988E3AE164C7E6D4395E96B566EC9BC16BA`; `256 / 75B0F6B08811042585A3698BE9EF1FFBC9C7023BA61ACE4BF05DD95E1969209B`; `225 / E35B18B588A50C2B4E52FCA83CB12ED8E86EC31843BBD8B50E1F6EEC0CF39C81`; `256 / D074CFEA4B768F7E1280F8848D1ACF99F4129BCA71E975A4FE03B5A6CDEB2031`; `256 / 735EF5EFF5C176AACC20CDCFA49A0AF71237BA986B649067657D6DD0E43EB780`; `287 / 494045F58BF50FA49F1B27E9BA2421C29143D298904A272C4383F5BF7465BE9A` |
| Post host | `166 / 89CD7C0C751C9B159865A95643C24118185D7B50068E1BEC3CE172A6E739B8BE`; `197 / 39406A391BD1D75938F5EFDAF76C6AA697CEC02C7E6ADD6A3B9D43AB6BFDEF77` |
| Final host | `187 / 731D29698B85F99FC2612219DE22F836935E4566918B7109C3407B85D2672716`; `218 / E63603112054AD24A55CE81ABDFEF95D25DD95AEEDF0AA879734999F86E194A9` |

The fixed top-level success outputs are:

| Source | Bytes | SHA-256 |
|---|---:|---|
| Pre/semantics outer runner | 170 | `E9AF80CBD27E3CE3D04FE6ED8FD2E81102E53AA0D33663E4B1BF203C40BC8F29` |
| Post-sync outer runner | 175 | `4573EB7B0A66477D4CD3CA4CBE257CBB9E9D2B26DE29E000DB4D348CB032A01F` |
| Final verifier | 195 | `3EFE3ED534AB9DFE39DA5C8DA3297C7AB43C513D4032B061DF09C474E9946DE5` |

## Authorized One-Time Order And Counts

Only the following ordered chain is authorized:

1. Create and push the exact-two-path approval-governance direct child.
2. Reconstruct and run one pre/semantics outer runner.
3. The runner may start one pre host, one unchanged pre verifier with five Git children, one revised bootstrap, one revised harness, one compatible verifier, one semantics wrapper and one embedded Python process.
4. On exact success only, `CreateNew` the exact 789-byte machine evidence and pre/semantics narrative.
5. Create and push one exact-two-path semantics evidence commit as the direct child of approval governance.
6. Reconstruct and run one post-sync outer runner with the actual approval-governance SHA in process scope.
7. The runner may start one post host, one unchanged post verifier and seven Git children.
8. On exact success only, `CreateNew` the post-sync machine attestation and post-sync narrative audit.
9. Create and push one exact-two-path post-sync audit commit as the direct child of the semantics evidence commit.
10. Reconstruct and run one final verifier host with the actual package, approval-governance and semantics-evidence SHAs in process scope.
11. The host may start one final verifier, which may start exactly eleven frozen Git children.
12. Require exact terminal success, then create no file, status document or commit and stop immediately.

The three final process-scoped environment bindings are:

    HGRAG_EXPECTED_PACKAGE_COMMIT
    = 945f655b95cfee9e55ad2d20e7bd5018f9aee1e2

    HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT
    = actual commit created by step 1

    HGRAG_EXPECTED_SEMANTICS_EVIDENCE_COMMIT
    = actual pushed and post-verified commit created by step 5

No binding may be guessed, substituted or inferred to bypass the recorded commits.

## Package-Assembly Count Clarification

The package records five read-only helper failures. The first four started zero processes. The fifth started four read-only `git diff` processes. Accurate package-assembly counts are:

    frozen execution Git children during package assembly: 0
    read-only helper Git diff processes: 4
    file writes from failed helpers: 0
    frozen source invocations: 0

The four read-only Git processes are not part of the authorized frozen execution chain and do not change its one-time counts.

## Fail-Closed Rule

Any source, transport, Manifest, path, historical evidence, classifier, stdout, stderr, exit, count, `CreateNew`, parent, changed-path, push, three-way GitHub-main, ancestry, post-schema, narrative-agreement, stability or final-host gate failure consumes the corresponding ordered authorization and requires immediate stop. Retry, fallback, source modification, command replacement, cleanup, overwrite, runtime switch, reset, rebase and force-push are prohibited.

## Explicitly Not Authorized

- complete synthetic rebinding;
- real precommit validator;
- fresh three-path direct child or derived execution-HEAD validation;
- formal preflight;
- official input, authorization token or official capture;
- controller rerun, formal verifier, evaluator or Gold;
- reservation or Stage3B.

## Success State

Exact success of the full authorized chain must stop at:

    AMENDMENT_5G_B_1_1_1_1_2_COMPLETE_TRANSPORT_CHAIN_VERIFIED_AWAITING_REVIEW
    PRE_EXECUTION_SYNC_VERIFIED
    VALIDATOR_SEMANTICS_PASSED
    SEMANTICS_EVIDENCE_COMMITTED_AND_PUSHED
    POST_EVIDENCE_SYNC_VERIFIED
    POST_SYNC_AUDIT_COMMITTED_AND_PUSHED
    FINAL_POST_SYNC_AUDIT_COMMIT_VERIFIED

    REAL_PRECOMMIT_VALIDATOR_NOT_RUN
    SYNTHETIC_REBINDING_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_EXECUTION_NOT_STARTED
    GOLD_NOT_APPROVED

This decision does not itself establish success. It authorizes exactly one fail-closed attempt at the frozen chain after the approval-governance commit is pushed.
