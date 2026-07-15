# Stage4B-U1-D Pre-Gold Corrected Amendment 5G-B.1.1.1.1.3 Approval Request

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Package date: 2026-07-16
- Supersedes rejected package: 97a8b169835c06330a6781ab63c59a482889c6bb
- Direct parent / Hard Failure 16 checkpoint: f28fc526faf74f80fdefb96ca189769dbcf1e5e4
- Package revision: CORRECTED_AFTER_HARD_FAILURE_16_PACKAGE_REVIEW_1
- Current status: AWAITING_PACKAGE_BOUND_APPROVAL
- Execution authorized by this package: No
- Other project conversations, thread tools, and global memory used: No

## Independent Review Disposition

The package accepts ACCEPT_HARD_FAILURE_16_REVIEW_1, the seven-path scope, the three loader designs, bounded command lines, raw-stdin payload identities, revised final host and 30/30 loader fixtures. It also accepts the rejection of package 97a8b169... for three blocking causes: missing pre/post parent hosts, stale success evidence that attested rejected long EncodedCommand transports, and a terminal verifier that did not reject that stale evidence.

This corrected package uses review option A. Pre/post target sources are revised to load this Manifest and write the current parent-host, loader, modeled command-line and stdin-payload identities into their existing versioned narratives. No new evidence path is added.

## Corrected Manifest Identity

    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_MANIFEST.json
    321442 bytes
    C1A11B789FD18D703AA6831BA5B513FC9ACB9767EC8A75016802030E0A0C1123

Any approval must explicitly bind the future corrected package commit containing this Request and Manifest. The rejected package 97a8b169... is not approved and cannot be reused.

## Nine Frozen Source Designs

| Source | Lines | UTF-8 bytes | SHA-256 |
|---|---:|---:|---|
| Pre target | 209 | 16383 | `B46C57D8B2198307A78412FB002EB9D326DF9CA6427E25047548B9F6C6303B71` |
| Pre stdin loader | 44 | 2727 | `E96B049EC651AED51D36741DF8C270A79C6AD3D2A2E1AC448F1C3D933B7D1AA8` |
| Pre parent host | 96 | 7922 | `8F11033CD306D118C4211109EACF8F0C1E9A90BCAEA8E19F99C933DC1C0858A7` |
| Post target | 180 | 13884 | `597AA12B964FAD400841F5113636758D6B6298E870F61CBB10B5DDB6D7A01FC4` |
| Post stdin loader | 44 | 2719 | `79F2F61B6578FFB929815ED9E0C74695CACAF8950E027F06006CC6BAB126B33C` |
| Post parent host | 99 | 8588 | `DC0234BE67CFCC4DDF18A135D65DC96222973F2B8736CBA487161869587C12DB` |
| Final verifier | 228 | 21120 | `6C2A6033E33E0F20839A2DC7D713DA49FEB69564AA3CC47B30EB495D0307BCCF` |
| Final stdin loader | 44 | 2724 | `6BC6A432344A6D2EB5C0E4C21BEE2E7C792A999CE5AEA4C562510EB57546B032` |
| Final parent host | 92 | 7377 | `48E4907AC8E02E3506FAE183534B356E1E647B1F62FC44610A421CF7C366F185` |

All nine sources use LF joining, no trailing newline and zero static parser errors. Package assembly invoked none of them.

## Six Bounded EncodedCommand Envelopes

| Envelope | Arguments chars | Arguments SHA-256 | Full command line chars including null | Full command line SHA-256 | Margin to 32,767 |
|---|---:|---|---:|---|---:|
| Pre stdin loader | 7323 | `7303F8B804ADE8AC0F0B2C9F31DC921F2018EAA96D832D997051992D617D57A4` | 7384 | `4E7455516368C4D806363FD14C83BFA5D61947C6F7EA2DB3E9184B7D97084FC0` | 25383 |
| Pre parent host | 21115 | `00B201AA16F7A1CF106ADACADBE35DDF44FF67E08FE4A2A8434A8912F4106E67` | 21176 | `E8247D1AF7D1CC5F6FEBF32F9102D49A37076FA19602906D7C9121E45EC808F0` | 11591 |
| Post stdin loader | 7303 | `799B50D27B408E4F07B39C1347AC9EC2AA902B0EB0C55AAFC2EC34B6EF2DDD61` | 7364 | `0695E3B6D4F8B7B2197540D30335293CCAFB630FA5FCA3BE897E65F0CD95C8E1` | 25403 |
| Post parent host | 22867 | `C069968B0E33D043EBEBCB7046144A07BD72D3E05770C59D0F798C3EBF95F2DC` | 22928 | `8791A392570A25CE2E46300EC5D05EA58A7AC4D2A27DCA38BAA106B6F87E7DA8` | 9839 |
| Final stdin loader | 7315 | `D23BC265A2620316F471681A6EC4A05855540DE9FDF804BBCD92AA00133726B6` | 7376 | `70ACA41557795DABA37889E8A438610F47A342A2E0D75553C830BC319301B2DA` | 25391 |
| Final parent host | 19703 | `0F124C3E07DF9CE51247F99A1B9245AB9AF1BA64C274245C30E4B2177CF8EC8C` | 19764 | `D621A0C6935D21D27E03784B252020814307D95BE9F9B85A432B2F06C4FA88AA` | 13003 |

The pre/post parent hosts are now complete executable designs. Each reconstructs the registered loader and target, validates source and parser identities, reconstructs the raw-stdin payload, starts one loader-backed PowerShell child, begins concurrent raw stdout/stderr drains, writes payload bytes through StandardInput.BaseStream, flushes/closes stdin, waits for process/tasks, and applies exit, exact stdout and exact stderr-class gates in that order.

The pre parent requires package and approval-governance process bindings. The post parent additionally requires the semantics-evidence binding. These bindings are passed process-scoped to the loader/target process.

## Corrected Success Evidence Contract

The revised pre narrative must contain exactly one line for each package/approval binding and each of: pre parent source, parent arguments, parent modeled command line, loader source, loader arguments, loader modeled command line, stdin payload ASCII bytes/SHA and decoded target SHA.

The revised post narrative must contain the analogous post identities plus package, approval-governance and semantics-evidence bindings. Existing two-path semantics and two-path post audit commits remain unchanged.

The rejected successful-transport fingerprints are forbidden from both narratives:

- pre long EncodedCommand: 53D27DD17FC3D4E6E8708E970C2BEFA4932AAE511A99D6EDF4A0BDFA9B498753;
- post long EncodedCommand: D55D3A04713814348752C5081F91B4FB41C52E68936657CC77905B5F9FC20ABC.

## Extended Final Verifier

Before its eleven Git operations, the final verifier now independently reconstructs and validates all six registered encoded envelopes and all three raw-stdin payloads. It then requires the exact current pre/post evidence lines listed above and rejects either forbidden long-EncodedCommand fingerprint in either narrative. The final host/final loader identities are therefore checked from the package-bound Manifest before terminal success.

The terminal Git chain remains package -> exact two-path approval governance -> exact two-path semantics evidence -> exact two-path post audit. Artifact stability, worktree cleanliness and local/origin/direct-main equality remain mandatory.

## Static And Negative Validation

- loader payload/decoder/parser fixtures: 30/30;
- newly frozen pre/post parent-host fixtures: 20/20;
- terminal transport-attestation fixtures: 12/12;
- total: 62/62;
- source executions, child processes, evidence creations and official operations during assembly: 0.

The Manifest preserves three corrected-package read-only helper failures. The first Windows PowerShell 5.1 `-File` load misdecoded the UTF-8 no-BOM research path and stopped before any project-file read. The second strict-mode in-memory construction treated a literal `$GitExe` comparison as a generator-variable expansion and stopped before any Manifest/Request write. The third final-validation helper used the single-letter function name `H`, which PowerShell resolved to the `Get-History` alias, and stopped at the Manifest hash assertion before source reconstruction. All three failures created zero child processes, invoked zero frozen sources and created zero evidence.

## Requested Approval-Governance Commit

A future approval-governance commit must be the single direct child of the corrected package commit and must change exactly:

1. AGENTS.md;
2. docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_APPROVAL_DECISION.md.

The Decision must bind the corrected package commit, this Manifest byte count/SHA, all nine source identities, all six bounded envelopes, all three payloads, exact future counts and the one-pass order. It must explicitly authorize the sequence before any command is reconstructed or invoked.

## Explicit Non-Authorization

This Request does not authorize approval governance, either pre/post parent host, any loader process, any target ScriptBlock, inner verifier/bootstrap/harness/wrapper/Python, evidence creation, evidence commit, post audit, final host/verifier, synthetic rebinding, real validator, formal preflight, official input/token/capture, controller, verifier, Gold, reservation or Stage3B.

## Current State

    HARD_FAILURE_16_AUDIT_ACCEPTED
    HARD_FAILURE_16_CHECKPOINT_FROZEN
    ROOT_CAUSE_ESTABLISHED_ENCODED_COMMAND_COMMAND_LINE_OVERFLOW
    REJECTED_PACKAGE_97A8B169_REVIEWED

    PRE_AND_POST_PARENT_HOSTS_FROZEN
    CURRENT_TRANSPORT_IDENTITIES_REQUIRED_IN_SUCCESS_EVIDENCE
    STALE_LONG_ENCODED_COMMAND_SUCCESS_CLAIMS_REJECTED
    FINAL_VERIFIER_TRANSPORT_ATTESTATION_GATES_EXTENDED
    NINE_SOURCE_DESIGNS_STATICALLY_FROZEN
    62_OF_62_STATIC_FIXTURES_PASS

    CORRECTED_AMENDMENT_5G_B_1_1_1_1_3_PACKAGE_AWAITING_APPROVAL
    EXECUTION_NOT_AUTHORIZED
