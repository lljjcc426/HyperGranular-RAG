# Stage4B-U1-D Pre-Gold Hard Failure 6

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-14
- Failure code: `HARD_FAILURE_6_FORMAL_PREFLIGHT_OS_TEMP_PATH_COMPARISON`
- Amendment 5D-B package: `f67061e753b03a5cf46d7a7c92b5a95fc79b0ef8`
- Amendment 5D-B final approval-governance HEAD: `1c46dc1b69f8381598aacb9f3b1e27561c7f9ee2`
- Amendment 5D-B rebinding/governance HEAD: `2447ad234c160c6e615d81b33dc4ede7ecaa18da`
- Formal preflight invocation count: 1
- Formal preflight retry count: 0
- Official capture invocation count: 0
- Controller/verifier/evaluator/Gold: Not run
- Other project conversations, thread tools, and global memory used: No

## State Before Preflight

Approval governance was pushed before synthetic execution. The complete 143-test post-approval suite then ran twice on the final approved governance bytes. Both runs passed 143/143 with zero failures, errors, skips, or official-path access attempts. Both complete outputs were 29,643 bytes with SHA-256 `264200C2EBEDA1D0B214F824B77C89FC5BBE82D3BE0836FAAB9486EACAACF368`, and direct byte comparison passed.

The rebinding evidence, governance binding, and narrative audit were committed and pushed at `2447ad234c160c6e615d81b33dc4ede7ecaa18da`. Before the formal preflight, `HEAD == origin/main`, the worktree was clean, and the registered machine output path did not exist.

## Non-Invocation Tooling Error

The first attempt to submit the inline preflight through `functions.exec` did not call `shell_command`: the JavaScript wrapper failed to parse a PowerShell backtick escape at wall time 0.0 seconds. No PowerShell process or formal preflight started and no official path was accessed. The wrapper expression was corrected before the single formal preflight invocation below. This launch-preparation error is not counted as a formal preflight invocation, but is retained here for completeness.

## Single Formal Preflight Failure

The only formal preflight started once on synchronized clean HEAD `2447ad234c160c6e615d81b33dc4ede7ecaa18da`. It completed these project-only and metadata gates before stopping:

- exact HEAD, GitHub synchronization, clean worktree, and required commit ancestry;
- all Manifest implementation hashes;
- all seven governance-bound file hashes and byte counts;
- final approved `AGENTS.md` SHA-256;
- comparator/controller/model/max-length/batch-size Manifest values;
- exact-command argument vector;
- absence of the registered machine/narrative audit paths;
- absence of all five formal outputs;
- absence of `stage4b_u1_decisions_diag_*` temporary residue.

It then failed at the OS temporary-directory equality expression:

```powershell
[System.IO.Path]::GetFullPath($tempParent) -eq
  [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
```

Observed exception:

```text
OS temp parent differs
```

The Manifest value is `C:\Users\cc\AppData\Local\Temp`. The comparison did not normalize a trailing directory separator before ordinal string equality; `.NET GetTempPath()` returns a directory path with a trailing separator. The formal gate therefore stopped before any official input file check or read. Regardless of whether both strings resolve to the same directory, the approved preflight invocation failed and is consumed. It must not be rerun without a new package-bound Amendment.

## Official Access Boundary

The failure occurred before these statements in the preflight command:

- regular-file/reparse-point checks for the five official inputs;
- SHA-256 reads of units, queries, channel audit, cache, or reference decisions;
- JSONL parsing of units or queries;
- JSON parsing of the controller channel audit.

Therefore this preflight did not open or hash any of the five official inputs. It also did not open the Stage4A-R2 source-audit file, 5C-B machine inventory, rankings, reference policy, evaluator/Gold, reservation, or Stage3B.

No authorization token was passed and the exact official capture command did not run.

## Post-Failure Metadata Check

One project/output metadata-only check after failure confirmed:

| Check | Result |
|---|---|
| HEAD | `2447ad234c160c6e615d81b33dc4ede7ecaa18da` |
| worktree clean | Yes |
| machine audit exists | No |
| narrative audit exists | No |
| formal v2.3.1 outputs existing | 0 of 5 |
| diagnostic temporary residue | 0 |
| official capture invocations | 0 |
| second preflight invocations | 0 |

This check did not hash or parse any official input.

## Scientific Boundary

Hard Failure 4 remains unclassified. No temporary v2.3.1 decisions were generated and no reference/captured comparison occurred. There is no new byte, canonical, query-order, schema, discrete, float/ULP, or semantic evidence.

Comparator v2, raw-byte equivalence, controller logic, data, model, parameters, cache, official artifacts, prior evidence, and historical failures remain unchanged.

## Stop State

```text
AMENDMENT_5D_B_OFFICIAL_DIAGNOSTIC_STOPPED_HARD_FAILURE_6
FORMAL_PREFLIGHT_CONSUMED_FAILED
OFFICIAL_CAPTURE_NOT_RUN
HARD_FAILURE_4_DIAGNOSIS_INCOMPLETE
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

No second preflight or capture is permitted under the consumed 5D-B approval. Any corrected path-equivalence preflight or official diagnostic attempt requires a new package-bound Amendment and explicit approval.
