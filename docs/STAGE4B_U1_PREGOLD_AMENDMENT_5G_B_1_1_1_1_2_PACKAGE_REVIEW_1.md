# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1.2 Package Review 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review date: 2026-07-15
- Reviewed package: 7f92c000bb3c22337c83dc28e32779f4eb9cfdf8
- Direct parent / Hard Failure 15 checkpoint: 95f68e7b2afdf6ed46c4eebe604d13744b26760a
- Decision: REJECT_AMENDMENT_5G_B_1_1_1_1_2_PACKAGE_AS_CURRENTLY_WRITTEN
- Recovery: RETURN_FOR_CORRECTED_AMENDMENT_5G_B_1_1_1_1_2_PACKAGE
- Execution authorized: No
- Other project conversations, thread tools, and global memory used: No

## Accepted Package Content

The package is the single direct child of Hard Failure 15 checkpoint `95f68e7b2afdf6ed46c4eebe604d13744b26760a`. It changes exactly seven governance paths, deletes no file and does not modify scripts, tests, result implementations or the three preserved raw machine files.

Hard Failure 15 Review 1, the raw machine evidence and the root-cause classification are accepted. The frozen stderr payload remains exactly 382 bytes with SHA-256 `4F2B6B3ED9201CA459DB2DD042E0A137C4E58BFE8E15A068E45AD8535FA5B1EF`. The only accepted PowerShell-child stderr classes are exact zero bytes and byte-for-byte equality with that payload. The six classifier fixtures are accepted as 6/6. Git, Python and every non-PowerShell child continue to require zero stderr.

The four inner envelope designs are accepted as static package content:

| Source | Lines | UTF-8 bytes | SHA-256 |
|---|---:|---:|---|
| Pre host/classifier | 96 | 6,787 | `0E028228BA9EC6F18E61DA26967DEE70C70F89B4D88D5254D12163980FAE0672` |
| Revised bootstrap | 98 | 7,146 | `E3458CE92A0C574034C9AC3CECDEBE9068D827671C5DDBA9E49B03FB0818317B` |
| Revised recovery harness | 91 | 7,654 | `12315561F64EBB748E9A7B18D71226B85941D1AAB870423DEC5B3FCE85EC9CDA` |
| Post host/classifier | 86 | 6,347 | `4757F3C83A71106BA837451F6FBD241E39D38AB2D717F37874ABC90575EDA5F0` |

These acceptances do not authorize any process start or evidence creation.

## Blocking Findings

### 1. Top-Level Execution Runner Is Not Frozen

The package says an outer host must launch and classify the pre host, revised bootstrap and post host, but it does not freeze the source that performs those operations. Missing governance fields include source lines and fingerprints, UTF-16LE/Base64 transport, complete arguments, ProcessStartInfo, raw BaseStream capture, exact classifier invocation, stdout/stderr/exit ordering, process counts and post-host environment assignment.

The four accepted sources are children of that missing runner. The runner cannot be invented in an approval decision because that would introduce new executable source after package review.

### 2. Inner Boundary Classes Are Not Observable Or Persisted

The pre host, revised bootstrap, recovery harness and post host calculate specific stderr classes, but their current outputs expose only `stderr_allowed=true` or the unchanged 789-byte semantics payload. A future narrative therefore cannot truthfully record whether each boundary observed `EMPTY` or `EXACT_FROZEN_382_BYTE_STARTUP_CLIXML`.

The corrected package must freeze an independent class-attestation transmission contract while leaving the final 789-byte semantics machine evidence unchanged.

### 3. Post Boundary Audit Order Is Impossible

The current order creates, commits and pushes the narrative before the post host runs, yet the narrative is required to record every PowerShell boundary, including the post-host and post-verifier boundaries. Those classes do not exist when the narrative is committed. Immediate stop after post success also prevents a later update without creating a dirty worktree or an unregistered commit.

The corrected package must separate pre/semantics attestation from post-sync attestation or otherwise redesign the frozen commit contract so every recorded observation exists before its audit artifact is created.

## Corrected Package Requirements

The corrected package must explicitly supersede `7f92c000bb3c22337c83dc28e32779f4eb9cfdf8` and must freeze:

1. A finite top-level pre/semantics runner and a finite top-level post-sync runner.
2. Each runner's complete source and transport fingerprints, fixed ProcessStartInfo, concurrent raw stdout/stderr BaseStream capture, exact stdout gates, exact stderr classifier, exit ordering, environment binding and process counts.
3. A per-boundary class transmission contract that carries only `EMPTY` or `EXACT_FROZEN_382_BYTE_STARTUP_CLIXML` and preserves the final 789-byte machine evidence unchanged.
4. A pre/semantics narrative contract limited to boundaries that already exist when the evidence commit is created.
5. Separate versioned post-sync machine and narrative audit paths created only after post-host success, followed by a separately counted exact-path audit commit and push.
6. Exact CreateNew rules, commit parents, changed-path sets, process counts, artifact-creation counts, push gates and final stop state.

## Explicit Non-Authorization

This review does not authorize an approval-governance commit, outer runner execution, pre host, pre verifier, Git children, revised bootstrap, revised harness, compatible verifier, wrapper, Python, machine evidence, narrative evidence, evidence commit, post host, post verifier, post-sync audit, synthetic execution, real validator, formal preflight, official input, token, capture, controller, verifier, Gold, reservation or Stage3B.

## Current State

    HARD_FAILURE_15_AUDIT_ACCEPTED
    HARD_FAILURE_15_CHECKPOINT_FROZEN
    RAW_MACHINE_EVIDENCE_ACCEPTED
    ROOT_CAUSE_ESTABLISHED
    EXACT_382_BYTE_CLASSIFIER_LOGIC_ACCEPTED
    FOUR_INNER_ENVELOPE_DESIGNS_STATICALLY_ACCEPTED

    TOP_LEVEL_OUTER_RUNNER_UNFROZEN
    INNER_BOUNDARY_CLASSES_UNOBSERVABLE
    POST_BOUNDARY_AUDIT_ORDER_IMPOSSIBLE
    RETURN_FOR_CORRECTED_AMENDMENT_5G_B_1_1_1_1_2_PACKAGE

    CURRENT_PACKAGE_7F92C000_NOT_APPROVED
    TRANSPORT_RECOVERY_EXECUTION_NOT_APPROVED
    PRE_SYNC_RERUN_NOT_APPROVED
    BOOTSTRAP_NOT_APPROVED
    SEMANTICS_SEQUENCE_NOT_APPROVED
    SEMANTICS_EVIDENCE_NOT_APPROVED
    POST_EVIDENCE_SYNC_NOT_APPROVED
    OFFICIAL_EXECUTION_NOT_APPROVED
