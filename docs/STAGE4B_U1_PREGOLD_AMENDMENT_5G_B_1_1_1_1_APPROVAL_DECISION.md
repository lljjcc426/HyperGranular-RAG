# Stage4B-U1-D Pre-Gold Corrected Amendment 5G-B.1.1.1.1 Approval Decision

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Approval date: 2026-07-15
- Decision: APPROVE_CORRECTED_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_FROZEN_PRE_AND_POST_SYNCHRONIZATION_RECOVERY_AND_UNCHANGED_BOOTSTRAP_SEMANTICS_ONLY
- Corrected package: 3d37c8a65888c2093403a71375bfa94dd51bac2e
- Superseded package: 93cc76ae97043077d2d3dae93e2569833ea3ab59 (NOT_APPROVABLE, NOT_EXECUTABLE, NOT_REUSABLE)
- Official execution: NOT_APPROVED
- Other project conversations, thread tools, and global memory used: No

## Approval-Governance Boundary

This approval-governance commit must be the direct child of `3d37c8a65888c2093403a71375bfa94dd51bac2e` and change exactly:

    AGENTS.md
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_APPROVAL_DECISION.md

It must be pushed before either synchronization verifier or any semantics process is started. The direct-parent and exact changed-path contract must be independently checked before execution.

## Frozen Pre-Execution Synchronization Verifier

    source lines: 74
    source UTF-8 bytes: 4114
    source SHA-256: 4A5A4BBE08661D588673C4B4A1A7ABAB88FEB2999699658CBC91E8081266EB66
    complete arguments SHA-256: 1ED8A00D773578DD5EBCE903CE8FF4E2413E18D9FA7E82DB4D2268A0CE62C4C5
    fixed success stdout bytes: 122
    fixed success stdout SHA-256: BCDF0010147E5952AD0372ADF39EDA0A18D349B02107C340DEF05BAFE18C0F09

It may start exactly five Git children, in the Manifest order. Success requires all zero exits, empty stderr, exact output grammar, local/fetched-origin/direct-remote SHA equality, clean worktree and all four evidence paths absent before and after execution.

Authorized counts:

    pre-execution synchronization-verifier PowerShell processes: 1
    pre-execution Git child processes: 5

## Frozen Bootstrap And Semantics Chain

    bootstrap:
    58 lines
    3909 bytes
    F8A452CEBEC06326E1D8BA4DEB4FC8915210F3FF9BBF53DA2D22B9675773C81D

    recovery harness:
    77 lines
    6246 bytes
    B34E7AE012AC0314AD44590603575194C8881CE58C17E6C8ED6568A5FA373048

    compatible verifier:
    59 lines
    3512 bytes
    1A30DC70AD0C01CDACBC3279F1CFD707EA4DAB457BE9C6C30A5C6D6495FA81BF

    compatible verifier stdout:
    190 bytes
    D05B3B2A147C51FB3A9FFFC3BEB802439E01AEFC34B708FE14C298978F2BFBB3

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

Authorized counts:

    bootstrap PowerShell processes: 1
    recovery-harness PowerShell processes: 1
    compatible-verifier PowerShell processes: 1
    semantics-wrapper PowerShell processes: 1
    Python processes: 1

The real precommit validator remains frozen and must not be invoked.

## Evidence Boundary

The unchanged bootstrap may exclusive-create only:

    results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_validator_semantics.json

After exact bootstrap success, the host may exclusive-create only:

    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_VALIDATOR_SEMANTICS_AUDIT.md

The machine file must be the exact captured 789 semantics bytes. The evidence commit must be the direct child of this approval-governance commit and change exactly those two evidence paths. It must not update `AGENTS.md`, README, ROADMAP, REPRODUCIBILITY or any other path.

Authorized counts:

    evidence commits: 1

## Frozen Post-Evidence Synchronization Verifier

    source lines: 107
    source UTF-8 bytes: 7130
    source SHA-256: 8877E18F75A94EE6DA326B09C3791E6641B6B9B32D42744BA23E033A20735A67
    UTF-16LE bytes: 14220
    Base64 characters: 18960
    Base64 SHA-256: 89F51EC73B762A7E8E9E661D0D2B81CAF6EB330A3C4C4789B375E72F2930DDE1
    complete arguments characters: 19011
    complete arguments SHA-256: 17327F58C123664224B95FABD85E7553B3E32F4F86659D9A17D13C68AD9FEB02
    fixed success stdout bytes: 194
    fixed success stdout SHA-256: 2ED3F942961C4DA1F7A9D71C3B8A50E6E00275DBBE4038C594B8834B7499AB0F

The parent process must set `HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT` only in the post-verifier child process to the exact lowercase SHA of this approval-governance commit. It must not use a package, evidence or historical approval SHA.

The verifier may start exactly seven Git children, in the Manifest order. Success requires all zero exits, empty stderr, exact output grammar, three-way SHA equality, clean worktree, evidence-commit parent equality, exact two-path evidence diff, target regular files, exact 789-byte machine evidence SHA, non-empty stable narrative audit and continued absence of both older paths.

Authorized counts:

    post-evidence synchronization-verifier PowerShell processes: 1
    post-evidence Git child processes: 7

## Unique Authorized Sequence

1. Commit and push the exact-two-path approval-governance direct child.
2. Statically reconstruct and fingerprint the pre-execution verifier and its transport.
3. Launch exactly one pre-execution verifier and exactly five Git children.
4. Require exact 122-byte success, three-way equality, clean worktree and four absent paths.
5. Statically reconstruct and verify the unchanged bootstrap and all downstream transports.
6. Launch exactly one bootstrap, harness, compatible verifier, wrapper and Python process in the frozen nested order.
7. Require exact 190-byte source-verifier success and exact 789-byte 9-of-9 semantics success with empty stderr and zero exits at every layer.
8. Exclusive-create machine evidence and narrative audit.
9. Commit and push exactly the two evidence paths as the direct child of approval governance.
10. Statically reconstruct and fingerprint the post-evidence verifier.
11. Set the exact process-scoped approval-parent environment binding.
12. Launch exactly one post-evidence verifier and exactly seven Git children.
13. Require exact 194-byte success and stop immediately.

Any failure consumes the corresponding ordered authorization. Command replacement, runtime switching, repair, fallback or retry is forbidden.

## Explicitly Not Authorized

- complete synthetic rebinding;
- real precommit validator or fresh three-path direct-child;
- execution-HEAD helper or formal preflight;
- official input, authorization token or official capture;
- controller, verifier, evaluator/Gold, rankings or policy;
- source audit, 5C-B inventory, reservation or Stage3B;
- `gh`, REST, browser or extra Git fallback;
- reset, rebase, force-push or continuation after post-verifier success.

## Approved Completion State

    CORRECTED_AMENDMENT_5G_B_1_1_1_1_VALIDATOR_SEMANTICS_VERIFIED_AWAITING_REVIEW
    HARD_FAILURE_13_AUDIT_ACCEPTED

    PRE_EXECUTION_THREE_WAY_GITHUB_MAIN_SYNCHRONIZATION_VERIFIED
    POST_EVIDENCE_THREE_WAY_GITHUB_MAIN_SYNCHRONIZATION_VERIFIED
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
