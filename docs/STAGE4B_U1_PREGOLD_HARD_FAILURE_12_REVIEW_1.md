# Stage4B-U1-D Pre-Gold Hard Failure 12 Review 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review date: 2026-07-15
- Reviewed checkpoint: 8002dac6fa37e0009f0e0bc78858b467bbff675e
- Review decision: ACCEPT_HARD_FAILURE_12_AUDIT
- Recovery decision: RETURN_FOR_AMENDMENT_5G_B_1_1_1_SOURCE_VERIFICATION_RECOVERY_PACKAGE
- Official execution: NOT_APPROVED
- Other project conversations, thread tools, and global memory used: No

## Bound History

    5G-B.1.1 package:
    c4101cfafbc08d518cd4b56e5d199f9d5937294b

    approval governance:
    e18dcb13b64e8a50d764fc9eacbabcdea7c5393f

    Hard Failure 12 checkpoint:
    8002dac6fa37e0009f0e0bc78858b467bbff675e

The Git history is ordered package, approval governance, then Hard Failure 12. The approval-governance commit is the exact two-path direct child required by the approved package.

## Accepted Findings

The pre-execution gate confirmed the frozen Python source has 46 lines and 2,284 UTF-8 bytes. It then failed while converting the computed SHA-256 byte array through `[System.Convert]::ToHexString(...)` under Windows PowerShell 5.1.

The direct cause is a runtime compatibility defect in the source-verification command:

    WINDOWS_POWERSHELL_5_1_INCOMPATIBLE_HEX_FORMATTING_API
    SYSTEM_CONVERT_TOHEXSTRING_METHOD_NOT_AVAILABLE

No source hash mismatch was observed. The failure does not establish drift or defects in the frozen 122-line PowerShell semantics wrapper, 46-line embedded Python source, nine fixtures, 789-byte expected stdout or 195-line real precommit validator.

The wrapper was not started and no Python process was created. Synthetic, real-validator, evidence, direct-child, helper, preflight, official input, token and capture counters remained zero. The fail-closed stop and absence of retry were correct.

## Frozen Unchanged Artifacts

The recovery package must not modify the following frozen values:

| Artifact | Lines | Bytes | SHA-256 |
|---|---:|---:|---|
| PowerShell semantics wrapper | 122 | 7,890 | DFA95A904CE371F283B8DBA8BB4D98CC048F345F536C0E7D0D6DB8073DF9E16C |
| Embedded Python source | 46 | 2,284 | D0D3D6FC37AD0C2649A7A7F88EFA944C357033E3F0E956BE0E27C4374653D602 |
| Real precommit validator | 195 | 15,966 | 0F066387B8523B0EA387444076A1113913082D283C28C2DE3FFB33872D558249 |

The expected semantics-wrapper stdout remains 789 bytes with SHA-256 `EDBD4614B790256E314F4A8963128A5FB5A190FAC197437FB349D4C33C606135`.

## Minimal Recovery Boundary

Amendment 5G-B.1.1.1 may only freeze a Windows PowerShell 5.1-compatible source verifier. Its SHA formatter must use `System.Security.Cryptography.SHA256`, `System.BitConverter`, hyphen removal and deterministic uppercase output. It must reject runtimes other than Windows PowerShell 5.1 Desktop.

The verifier may read only the frozen 5G-B.1.1 Manifest. It must verify that Manifest's own path, bytes and SHA before parsing, then check the Python source, PowerShell wrapper, embedded Python equality and expected stdout. It must not read official inputs or invoke project helpers.

The recovery package itself authorizes no verifier invocation, wrapper, Python process or evidence creation. A future package-bound approval may authorize one compatible source-verifier invocation and, only after exact success, one unchanged semantics wrapper with one Python process and two new versioned evidence paths.

## Current State

    HARD_FAILURE_12_AUDIT_ACCEPTED
    HARD_FAILURE_12_CHECKPOINT_FROZEN
    APPROVAL_GOVERNANCE_GATE_PASSED
    WINDOWS_POWERSHELL_5_1_HEX_API_COMPATIBILITY_FAILURE
    NO_SOURCE_HASH_MISMATCH_OBSERVED
    RETURN_FOR_AMENDMENT_5G_B_1_1_1_PACKAGE

    CURRENT_5G_B_1_1_APPROVAL_CONSUMED
    SOURCE_VERIFICATION_RETRY_NOT_APPROVED
    VALIDATOR_SEMANTICS_WRAPPER_NOT_APPROVED
    FRESH_SYNTHETIC_REBINDING_NOT_APPROVED
    REAL_PRECOMMIT_VALIDATOR_EXECUTION_NOT_APPROVED
    FRESH_THREE_PATH_DIRECT_CHILD_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_INPUT_ACCESS_NOT_APPROVED
    AUTHORIZATION_TOKEN_USE_NOT_APPROVED
    OFFICIAL_CAPTURE_NOT_APPROVED
    CONTROLLER_RERUN_NOT_APPROVED
    VERIFIER_NOT_APPROVED
    GOLD_NOT_APPROVED
