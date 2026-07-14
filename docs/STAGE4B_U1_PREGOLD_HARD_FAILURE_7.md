# Stage4B-U1-D Pre-Gold Hard Failure 7

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-14
- Failure code: `HARD_FAILURE_7_FORMAL_PREFLIGHT_PROHIBITED_ARGUMENT_SUBSTRING_FALSE_POSITIVE`
- Amendment 5E-B package: `e387d2707ede9024571249face71bf7ca3afd4e0`
- Amendment 5E-B approval governance: `f2f2e249e4e7a52fcc44b61a2245d8d50d79106d`
- Amendment 5E-B rebinding/governance: `3185c3bd4ffd3eb2bc61b52fdf18a3367b9dca76`
- Formal preflight invocation count: 1
- Formal preflight retry count: 0
- Helper invocation count: 0
- Official input metadata/content access count: 0
- Authorization token use count: 0
- Official capture invocation count: 0
- Controller/verifier/evaluator/Gold: Not run
- Other project conversations, thread tools, and global memory used: No

## State Before Preflight

5E-B approval governance was committed and pushed first. The complete 161-test post-approval suite then ran twice on the final approved governance bytes. Both runs passed 161/161 with zero failure/error/skip/official access/formal-preflight/token/capture. Both evidence streams were 36,518 bytes with SHA-256 `BF4C668C76C4B8545882C894F241038765AFD8DD263B4195D9E2D654B7B9FC1A`, and direct byte comparison passed.

Rebinding evidence, governance binding and narrative audit were committed and pushed at `3185c3bd4ffd3eb2bc61b52fdf18a3367b9dca76`. Before formal preflight, `HEAD == origin/main`, the worktree was clean, all 23 Manifest implementation hashes matched, and the registered rebinding output was committed.

## Single Formal Preflight Failure

The only authorized formal preflight started once on clean synchronized HEAD `3185c3bd4ffd3eb2bc61b52fdf18a3367b9dca76`.

### A Gate Passed

The preflight completed all project/governance checks:

- exact local/remote HEAD and clean worktree;
- package, approval, implementation and rebinding/governance ancestry;
- 23 Manifest implementation hashes;
- seven governance-bound SHA-256 and byte counts;
- exact capture argv equality with the 5D-B Manifest;
- helper tracked regular non-reparse file status.

Observed output:

```text
A_PROJECT_GOVERNANCE=PASS
```

### B Gate Failed

Before the failing statement, B confirmed:

- historical machine audit absent;
- 5E-B narrative audit absent;
- all five formal outputs absent;
- `stage4b_u1_decisions_diag_*` OS-temp residue absent.

It then attempted to prove that no prohibited input argument was supplied by applying raw case-insensitive substring patterns to every exact-command argument. The pattern `gold` matched the approved and frozen historical machine audit output path:

```text
E:\科研\HyperGranular-RAG\results\stage4b_u1_d_pregold_amendment_5b_official_decisions_diagnostic.json
```

The match begins inside the directory-independent filename segment `pregold`, at index 48. Observed exception:

```text
Prohibited argument supplied: gold
```

The command therefore stopped inside B. It did not print `B_OUTPUT_RESIDUE=PASS` and did not enter C or D.

## Direct Cause

The preflight implementation used this semantic shape:

```powershell
$value.IndexOf('gold', [StringComparison]::OrdinalIgnoreCase) -ge 0
```

This scans an entire argument as an untyped string. It cannot distinguish a prohibited Gold input role/path from the allowed protocol term `pregold` in the frozen machine audit output path. The exact command had already been proven byte/element equivalent to the approved 5D-B command in A; no new Gold argument was supplied.

This is a fail-closed preflight argument-classification defect. It is not evidence of official input, helper, capture, comparator, controller, cache, data, model or parameter drift. Nevertheless, the single authorized 5E-B preflight failed and is consumed. The check cannot be corrected and rerun under the same approval.

## Official Access Boundary

C was never reached, so the helper was not imported or called. D was never reached, so none of the five official inputs was checked, opened, hashed or parsed.

The preflight did not open the Stage4A-R2 source-audit file, 5C-B machine inventory, rankings, reference policy, evaluator/Gold, reservation or Stage3B. No token was passed and capture did not run.

Hard Failure 4 remains unclassified. No new temporary decisions or diagnostic comparison exists.

## Manifest-Only Diagnosis

After the stop, one project-only Manifest scan reported exactly one prohibited-pattern match:

```text
pattern=gold
index=48
argument=E:\科研\HyperGranular-RAG\results\stage4b_u1_d_pregold_amendment_5b_official_decisions_diagnostic.json
```

This scan did not inspect official paths or rerun any preflight gate.

## Post-Failure Metadata Check

The first two attempts to launch the project-output metadata check contained unmatched PowerShell parentheses and failed at parse time. Neither attempt executed any check or file operation. A corrected metadata-only command then confirmed:

| Check | Result |
|---|---|
| HEAD | `3185c3bd4ffd3eb2bc61b52fdf18a3367b9dca76` |
| worktree clean | Yes |
| machine audit exists | No |
| narrative audit exists | No |
| formal outputs existing | 0 of 5 |
| diagnostic temporary residue | 0 |
| helper invocations | 0 |
| official input metadata/content access | 0 |
| token uses | 0 |
| capture invocations | 0 |

No repository or official artifact was deleted or modified.

## Scientific Boundary

- 5E-A helper remains synthetically verified but was not exercised against the official OS-temp boundary in this preflight;
- Hard Failure 6's direct cause remains confirmed;
- Hard Failure 4 diagnosis remains incomplete;
- no byte, canonical, query-order, schema, discrete, float/ULP or decision-semantic result was generated;
- raw-byte equivalence and all scientific/runtime parameters remain frozen.

## Stop State

```text
AMENDMENT_5E_B_FORMAL_PREFLIGHT_STOPPED_HARD_FAILURE_7
FORMAL_PREFLIGHT_CONSUMED_FAILED
HELPER_NOT_RUN
OFFICIAL_INPUTS_NOT_ACCESSED
OFFICIAL_CAPTURE_NOT_RUN
HARD_FAILURE_4_DIAGNOSIS_INCOMPLETE
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

No second preflight or capture is permitted under 5E-B. Any replacement for raw-substring argument classification and any official diagnostic resumption require a new package-bound Amendment and explicit approval before execution.
