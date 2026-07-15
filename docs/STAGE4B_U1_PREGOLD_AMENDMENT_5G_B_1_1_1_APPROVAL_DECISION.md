# Stage4B-U1-D Pre-Gold Corrected Amendment 5G-B.1.1.1 Approval Decision

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Approval date: 2026-07-15
- Decision: APPROVE_CORRECTED_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_FROZEN_BOOTSTRAP_RECOVERY_EXECUTION_HARNESS_SOURCE_VERIFICATION_AND_SEMANTICS_ONLY
- Corrected package: e37400707a65d11c9f038d13e7be0ec2a19d27a4
- Superseded package: d1876bd9ccc198285808795f7f1809c4d1a48e1c (NOT_APPROVABLE, NOT_EXECUTABLE, NOT_REUSABLE)
- Official execution: NOT_APPROVED
- Other project conversations, thread tools, and global memory used: No

## Frozen Bindings

    compatible verifier:
    59 lines
    3512 bytes
    1A30DC70AD0C01CDACBC3279F1CFD707EA4DAB457BE9C6C30A5C6D6495FA81BF

    compatible verifier stdout:
    190 bytes
    D05B3B2A147C51FB3A9FFFC3BEB802439E01AEFC34B708FE14C298978F2BFBB3

    recovery harness:
    77 lines
    6246 bytes
    B34E7AE012AC0314AD44590603575194C8881CE58C17E6C8ED6568A5FA373048

    bootstrap:
    58 lines
    3909 bytes
    F8A452CEBEC06326E1D8BA4DEB4FC8915210F3FF9BBF53DA2D22B9675773C81D

    bootstrap UTF-16LE bytes:
    7770

    bootstrap Base64 chars / SHA-256:
    10360
    06CD60CDBD63E5AB9B017487285077C68581829D4309DC1AD6C964F22B9236C2

    bootstrap complete arguments chars / SHA-256:
    10411
    5EF7120B1005A027D408CF7DCAB525768376F2DAD213D91E69D73E1326D6F05D

    semantics wrapper:
    122 lines
    7890 bytes
    DFA95A904CE371F283B8DBA8BB4D98CC048F345F536C0E7D0D6DB8073DF9E16C

    embedded Python:
    46 lines
    2284 bytes
    D0D3D6FC37AD0C2649A7A7F88EFA944C357033E3F0E956BE0E27C4374653D602

    semantics stdout:
    789 bytes
    EDBD4614B790256E314F4A8963128A5FB5A190FAC197437FB349D4C33C606135

    real precommit validator, frozen and not executable:
    195 lines
    15966 bytes
    0F066387B8523B0EA387444076A1113913082D283C28C2DE3FFB33872D558249

Derived complete-arguments SHA-256 values are also binding:

    recovery harness:
    19842E8DAB9CD94C4404DAC97989388B614462DDDC098A4590DA38D31F6B127B

    compatible verifier:
    DD57FC57342776A74FF4563D39BBD56AD64AFDB76B980202285ACECBB9E82026

    semantics wrapper:
    0E1CCE9C1DE11C964356F4A508F330C169F255E3CCEA460D65417D3E923D42D5

## Approval-Governance Boundary

This approval-governance commit must be the direct child of `e37400707a65d11c9f038d13e7be0ec2a19d27a4` and change exactly:

    AGENTS.md
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_APPROVAL_DECISION.md

It must be pushed and synchronized across local, origin and GitHub with a clean worktree. All four old/new evidence paths must remain absent before any source reconstruction or process launch.

## Frozen Process Contract

Every PowerShell process must use:

    C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
    -NoLogo -NoProfile -NonInteractive -EncodedCommand <UTF-16LE Base64 source>

The registered ProcessStartInfo fields are mandatory: `UseShellExecute=false`, redirected standard input/output/error, `CreateNoWindow=true`, UTF-8 stdout/stderr decoding and immediate standard-input close. Temporary `.ps1` files are forbidden.

The corrected package commit, corrected Manifest and frozen bootstrap source are the governance recursion terminus. No fourth dynamically generated verifier may be introduced.

## Authorized Sequence

1. Push and synchronize the exact approval-governance commit.
2. Statically reconstruct and verify bootstrap source, UTF-16LE/Base64 transport, complete arguments and all three derived child-arguments fingerprints without starting a process.
3. Launch the frozen bootstrap exactly once.
4. The bootstrap launches exactly one recovery-harness PowerShell process.
5. The harness launches exactly one compatible-verifier PowerShell process.
6. Only after exact 190-byte verifier success, the harness launches exactly one unchanged semantics-wrapper PowerShell process.
7. The wrapper launches exactly one Python process and must pass all 9/9 fixtures with exact 789-byte stdout.
8. Every process layer must exit 0 with empty stderr and exact stdout.
9. Bootstrap exclusive-creates machine evidence directly from its captured 789 bytes. Then exclusive-create the narrative audit.
10. Commit exactly the two evidence paths as the direct child of approval governance, push, synchronize, verify clean worktree and stop immediately.

One-time limits:

    approval-governance commits = 1
    bootstrap invocations = 1
    recovery-harness PowerShell processes = 1
    compatible-verifier PowerShell processes = 1
    semantics-wrapper PowerShell processes = 1
    Python processes = 1
    evidence commits = 1
    automatic retry = false

Any failure consumes the ordered authorization and requires a new Hard Failure checkpoint. Repair, runtime switching or retry under this approval is forbidden.

## Evidence Boundary

The only success evidence paths are:

    results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_validator_semantics.json
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_VALIDATOR_SEMANTICS_AUDIT.md

Machine evidence must be the bootstrap-created raw 789 bytes. The evidence commit must contain exactly these two paths and must not update governance or status documents.

## Explicitly Not Authorized

- complete synthetic rebinding;
- real precommit validator execution;
- fresh three-path direct-child or execution-HEAD helper;
- formal preflight, official input, authorization token or capture;
- controller, verifier, evaluator/Gold, rankings, policy or source audit;
- 5C-B inventory, reservation or Stage3B;
- reset, rebase, force-push, retry or automatic continuation after evidence commit.

## Approved Completion State

    CORRECTED_AMENDMENT_5G_B_1_1_1_VALIDATOR_SEMANTICS_VERIFIED_AWAITING_REVIEW
    HARD_FAILURE_12_AUDIT_ACCEPTED
    REAL_PRECOMMIT_VALIDATOR_REMAINS_FROZEN

    FRESH_SYNTHETIC_REBINDING_NOT_APPROVED
    FRESH_THREE_PATH_DIRECT_CHILD_NOT_APPROVED
    DERIVED_EXECUTION_HEAD_VALIDATION_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_INPUT_ACCESS_NOT_APPROVED
    AUTHORIZATION_TOKEN_USE_NOT_APPROVED
    OFFICIAL_CAPTURE_NOT_APPROVED
    CONTROLLER_RERUN_NOT_APPROVED
    VERIFIER_NOT_APPROVED
    GOLD_NOT_APPROVED
