# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1 Package Review 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review date: 2026-07-15
- Reviewed package: 93cc76ae97043077d2d3dae93e2569833ea3ab59
- Decision: REJECT_AMENDMENT_5G_B_1_1_1_1_PACKAGE_AS_CURRENTLY_WRITTEN
- Recovery: RETURN_FOR_CORRECTED_AMENDMENT_5G_B_1_1_1_1_PACKAGE
- Execution authorized: No
- Other project conversations, thread tools, and global memory used: No

## Accepted Package Content

The package is the single direct child of Hard Failure 13 checkpoint `e159558b621f516598dc4fd2aede151c84472950` and changes exactly seven governance paths. It adds no script, test, result or historical-artifact mutation and deletes no file.

Hard Failure 13 Review 1 is accepted. The prior approval-governance commit is valid and was retrospectively confirmed on GitHub, while the runtime three-way gate correctly remains unpassed. The consumed corrected 5G-B.1.1.1 approval cannot be reused.

The 74-line pre-execution synchronization verifier is statically accepted:

    source bytes:
    4114

    source SHA-256:
    4A5A4BBE08661D588673C4B4A1A7ABAB88FEB2999699658CBC91E8081266EB66

    complete arguments SHA-256:
    1ED8A00D773578DD5EBCE903CE8FF4E2413E18D9FA7E82DB4D2268A0CE62C4C5

    fixed success stdout bytes:
    122

    fixed success stdout SHA-256:
    BCDF0010147E5952AD0372ADF39EDA0A18D349B02107C340DEF05BAFE18C0F09

Its exact five Git children, ProcessStartInfo contract, output grammar, three-way SHA equality, clean-worktree check and four-path-absence checks are accepted. The package-assembly ancestry-check false negative is also accepted as a recorded pre-staging command defect with zero verifier or semantics execution.

## Blocking Finding

The package requires a final synchronization and clean-worktree gate after the evidence commit but freezes only the pre-execution verifier. That verifier requires all four evidence paths to be absent before and after its five Git children. It therefore cannot run after the two target evidence paths have been created and committed.

No post-evidence source, transport, Git command set, evidence-existence contract, parent/path contract, fixed success output or process count was frozen. The Request also referred to a failed first or second synchronization invocation while its limits authorized only one verifier process and five Git children.

This cannot be repaired in an approval decision because doing so would introduce unreviewed executable source after package review.

## Corrected Package Requirements

The corrected package must supersede `93cc76ae97043077d2d3dae93e2569833ea3ab59` and preserve the accepted 74-line verifier byte-for-byte as `PRE_EXECUTION_SYNCHRONIZATION_VERIFIER`.

It must separately freeze a `POST_EVIDENCE_SYNCHRONIZATION_VERIFIER` that checks:

1. Local HEAD, fetched `origin/main` and direct `ls-remote` GitHub main are exactly equal.
2. The worktree is clean.
3. The target machine and narrative evidence are regular files.
4. The two older 5G-B.1.1 paths remain absent.
5. Machine evidence is exactly 789 bytes with SHA-256 `EDBD4614B790256E314F4A8963128A5FB5A190FAC197437FB349D4C33C606135`.
6. Evidence-commit parent equals the newly created approval-governance commit.
7. Evidence-commit changed paths are exactly the target machine and narrative files.

The corrected package must freeze the post-evidence source lines, bytes, SHA-256, EncodedCommand transport, exact Git child arguments, ProcessStartInfo fields, output grammar, expected environment binding, stdout/stderr/exit contract and process counts.

Counts must be split unambiguously:

    pre-execution verifier PowerShell processes: 1
    pre-execution Git children: 5

    post-evidence verifier PowerShell processes: 1
    post-evidence Git children: 7

## Current State

    PACKAGE_COMMIT_AND_SCOPE_ACCEPTED
    PRE_EXECUTION_SYNC_VERIFIER_STATICALLY_ACCEPTED
    PRE_EXECUTION_SYNC_VERIFIER_FINGERPRINTS_CONFIRMED

    POST_EVIDENCE_SYNC_GATE_UNFROZEN
    SYNC_INVOCATION_COUNTS_INCONSISTENT
    RETURN_FOR_CORRECTED_AMENDMENT_5G_B_1_1_1_1_PACKAGE

    CURRENT_PACKAGE_93CC76A_NOT_APPROVED
    SYNCHRONIZATION_VERIFIER_NOT_APPROVED
    STATIC_SOURCE_RECONSTRUCTION_NOT_APPROVED
    BOOTSTRAP_NOT_APPROVED
    SEMANTICS_SEQUENCE_NOT_APPROVED
    OFFICIAL_EXECUTION_NOT_APPROVED
