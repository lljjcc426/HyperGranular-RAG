# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1.2 Package Review 2

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review date: 2026-07-15
- Reviewed corrected package: 44e56ab955dfe5fe89cc8ec4343870b59d008c9a
- Direct parent / superseded package: 7f92c000bb3c22337c83dc28e32779f4eb9cfdf8
- Hard Failure 15 checkpoint: 95f68e7b2afdf6ed46c4eebe604d13744b26760a
- Decision: REJECT_CORRECTED_AMENDMENT_5G_B_1_1_1_1_2_AS_CURRENTLY_WRITTEN
- Recovery: RETURN_FOR_SECOND_CORRECTED_AMENDMENT_5G_B_1_1_1_1_2_PACKAGE
- Execution authorized: No
- Other project conversations, thread tools, and global memory used: No

## Accepted Corrected-Package Content

Commit `44e56ab955dfe5fe89cc8ec4343870b59d008c9a` is the single direct child of the superseded package and changes exactly seven governance paths. It deletes no file. Package Review 1, Hard Failure 15, the three frozen raw machine files, the exact 382-byte classifier and the unchanged Git/Python stderr rules are accepted.

The six frozen source designs and their transports are statically accepted:

| Source | Lines | UTF-8 bytes | SHA-256 |
|---|---:|---:|---|
| Pre host | 96 | 6,816 | `61EA2A37C66EF5D59299F91E045F918D5A8DD02E961DE278142584E7515E50FB` |
| Revised recovery harness | 91 | 7,857 | `DD11F1E6592CAD904ED5B25CD007AE46474319B7FD6036166C390BB28EB73931` |
| Revised bootstrap | 109 | 8,325 | `84D6868A4DF279D4EA755E64986CC9549FB86B45998848CA3278A1A6B871FEB7` |
| Post host | 86 | 6,377 | `430C0F64ECD940BDDA7CDE098E156629F914027023EE6306ED9084AB72E8853D` |
| Pre/semantics outer runner | 194 | 14,491 | `6B24A6F25B5ABF4212A14D16E58EB569015C1D41EEB5587E70C9CD6C5E3CE124` |
| Post-sync outer runner | 166 | 12,149 | `0BC1EDF07495CEAF01502EBF0FCEAA2C77E08A857A2B91AE4AA2E0DB451DD35A` |

The canonical class-attestation channel is accepted. Pre host has two exact variants, harness has four, bootstrap has eight and post host has two. The independent recomputations of the pre/post variants and both outer-runner success outputs are accepted.

The pre/semantics narrative now records only six classes that already exist. The separately versioned post-sync machine and narrative artifacts are created only after the post host and unchanged post verifier complete. This removes the earlier impossible post-class ordering.

## Blocking Finding

The final post-sync audit commit has no frozen final verifier.

The unchanged 107-line post verifier runs while the semantics evidence commit is HEAD. It can prove that commit's three-way GitHub-main synchronization, approval-governance parent, exact semantics path set and target stability. The post-sync audit files are created and committed only afterward.

The current final step checks only a clean worktree and local HEAD equal to the tracking ref. It does not independently verify:

1. Local HEAD, fetched `origin/main` and direct `ls-remote` GitHub main all equal the final post-sync audit commit.
2. Final `HEAD^` equals the semantics evidence commit.
3. Final changed paths are exactly the post-sync machine and narrative audit files.
4. Both final audit paths are regular files and stable across Git operations.
5. The machine attestation matches its strict registered schema, allowed classes, `1/1/7` process counts and zero official access.
6. The narrative binds the correct approval-governance SHA and contains the same two classes as the machine attestation.
7. Historical Hard Failure 15 evidence and the 789-byte semantics machine evidence remain unchanged.

This cannot be repaired in an approval decision by adding ad hoc `ls-remote`, `diff-tree` or other Git commands because the current package freezes no final verifier source, transport, process or Git-child count.

## Second Corrected-Package Requirements

The next package must supersede `44e56ab955dfe5fe89cc8ec4343870b59d008c9a` and freeze a `FINAL_POST_SYNC_AUDIT_COMMIT_VERIFIER` that runs only after the exact-two-path final audit commit is pushed.

It must freeze source lines/bytes/SHA, UTF-16LE/Base64, complete arguments, Git child count, raw stream capture, strict-zero Git stderr, exact PowerShell-child stderr classifier, fixed success stdout and exit/stdout/stderr gate order.

At minimum it must use the registered equivalents of:

    git fetch origin main --quiet
    git rev-parse HEAD
    git rev-parse refs/remotes/origin/main
    git ls-remote --exit-code origin refs/heads/main
    git status --porcelain=v1
    git rev-parse HEAD^
    git diff-tree --no-commit-id --name-only -r HEAD

Read-only commands may be added to verify the complete package -> approval -> semantics -> final-audit ancestry and the exact changed-path sets at each governed level. All command arguments and counts must be frozen.

The verifier must validate the strict canonical post-sync machine schema, exact class agreement in the narrative, approval-governance binding, artifact regular-file identity and before/after stability, historical evidence stability and exact 789-byte semantics machine evidence. After verifier success no file, status document or commit may be created; execution must stop immediately.

## Explicit Non-Authorization

This review does not authorize approval governance, transport execution, pre-sync rerun, bootstrap, semantics sequence, semantics evidence, post-sync execution, post-sync audit creation/commit, final verifier execution, synthetic execution, real validator, formal preflight, official input/token/capture, controller, verifier, evaluator, Gold, reservation or Stage3B.

## Current State

    HARD_FAILURE_15_AUDIT_ACCEPTED
    RAW_MACHINE_EVIDENCE_ACCEPTED
    ROOT_CAUSE_ESTABLISHED
    PACKAGE_REVIEW_1_REJECTION_ACCEPTED
    EXACT_382_BYTE_CLASSIFIER_ACCEPTED
    SIX_FROZEN_SOURCE_DESIGNS_STATICALLY_ACCEPTED
    CANONICAL_CLASS_ATTESTATION_ACCEPTED
    PRE_POST_AUDIT_ORDER_ACCEPTED

    FINAL_POST_SYNC_AUDIT_COMMIT_UNVERIFIED
    FINAL_DIRECT_GITHUB_MAIN_GATE_MISSING
    FINAL_COMMIT_PARENT_AND_PATH_GATE_MISSING
    RETURN_FOR_SECOND_CORRECTED_AMENDMENT_5G_B_1_1_1_1_2_PACKAGE

    CURRENT_PACKAGE_44E56AB_NOT_APPROVED
    APPROVAL_GOVERNANCE_NOT_APPROVED
    TOP_LEVEL_RUNNER_EXECUTION_NOT_APPROVED
    SEMANTICS_EVIDENCE_NOT_APPROVED
    POST_SYNC_AUDIT_COMMIT_NOT_APPROVED
    FINAL_VERIFIER_NOT_APPROVED
    OFFICIAL_EXECUTION_NOT_APPROVED
