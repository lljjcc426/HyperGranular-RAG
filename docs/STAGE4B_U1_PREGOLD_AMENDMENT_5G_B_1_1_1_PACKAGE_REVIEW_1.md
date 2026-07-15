# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1 Package Review 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review date: 2026-07-15
- Reviewed package: d1876bd9ccc198285808795f7f1809c4d1a48e1c
- Decision: REJECT_AMENDMENT_5G_B_1_1_1_PACKAGE_AS_CURRENTLY_WRITTEN
- Recovery: RETURN_FOR_CORRECTED_AMENDMENT_5G_B_1_1_1_PACKAGE
- Execution authorized: No
- Other project conversations, thread tools, and global memory used: No

## Accepted Scope And Content

The package commit correctly follows Hard Failure 12 checkpoint `8002dac6fa37e0009f0e0bc78858b467bbff675e`, changes only governance documents and contains no script, test, result, historical-artifact or deletion drift.

The 59-line compatible verifier is statically acceptable:

    source bytes: 3512
    source SHA-256: 1A30DC70AD0C01CDACBC3279F1CFD707EA4DAB457BE9C6C30A5C6D6495FA81BF
    stdout bytes: 190
    stdout SHA-256: D05B3B2A147C51FB3A9FFFC3BEB802439E01AEFC34B708FE14C298978F2BFBB3

It correctly replaces `Convert.ToHexString()` with SHA256, BitConverter and hyphen removal. The old semantics wrapper, embedded Python, expected stdout and real precommit validator remain frozen.

## Blocking Findings

The package does not freeze the command that reconstructs and hash-checks the compatible verifier itself. That leaves the Hard Failure 12 layer open to another runtime, encoding, line-ending or hexadecimal-conversion defect.

The package also does not freeze how the verifier and semantics wrapper are launched as Windows PowerShell 5.1 processes. `-NoProfile`, source encoding and transport, process arguments, redirected stdout/stderr, exit-code capture and temporary-file policy are not bound.

Because the original wrapper writes through `[Console]::Out.Write`, an unspecified in-session invocation cannot prove that saved machine evidence is the exact raw 789-byte wrapper stdout.

## Corrected Package Requirements

The corrected package must supersede `d1876bd9ccc198285808795f7f1809c4d1a48e1c` and freeze:

1. A small Windows PowerShell 5.1 bootstrap whose source in the package commit and Manifest is the governance trust root.
2. A complete recovery execution harness with independently registered source lines, bytes and SHA-256.
3. Exact child executable, process arguments, UTF-16LE Base64 `EncodedCommand` transport, `-NoLogo`, `-NoProfile`, `-NonInteractive`, redirected stdin/stdout/stderr and no-window settings.
4. Exactly one verifier PowerShell child and one semantics-wrapper PowerShell child; the wrapper may start exactly one Python process.
5. Exact verifier 190-byte and wrapper 789-byte stdout identities, empty stderr and zero exit codes.
6. No temporary `.ps1` files and no official or project-helper access.

The bootstrap may trust its own package-committed source and the corrected Manifest as the recursion terminus. It must use the compatible SHA256 + BitConverter implementation to reconstruct, hash-check and start the recovery harness. The harness must then independently reconstruct and verify the compatible verifier and unchanged semantics wrapper before starting each child.

## Current State

    RECOVERY_VERIFIER_CONTENT_STATICALLY_ACCEPTABLE
    RECOVERY_EXECUTION_ENVELOPE_INCOMPLETE
    RETURN_FOR_CORRECTED_AMENDMENT_5G_B_1_1_1_PACKAGE

    CURRENT_PACKAGE_D1876BD_NOT_APPROVED
    COMPATIBLE_SOURCE_VERIFIER_NOT_APPROVED
    VALIDATOR_SEMANTICS_WRAPPER_NOT_APPROVED
    FRESH_SYNTHETIC_REBINDING_NOT_APPROVED
    REAL_PRECOMMIT_VALIDATOR_EXECUTION_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_INPUT_ACCESS_NOT_APPROVED
    AUTHORIZATION_TOKEN_USE_NOT_APPROVED
    OFFICIAL_CAPTURE_NOT_APPROVED
    CONTROLLER_RERUN_NOT_APPROVED
    VERIFIER_NOT_APPROVED
    GOLD_NOT_APPROVED
