# Stage4B-U1-D Pre-Gold Amendment 5G-B.1 Approval Request

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-15
- Request ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_GOVERNANCE_KEYSET_VALIDATION_REPAIR_AND_FRESH_REBINDING_DIRECT_CHILD_ONLY`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_MANIFEST.json`
- Current state: `RETURN_FOR_CORRECTED_AMENDMENT_5G_B_1_PACKAGE`
- Requested mode: `GOVERNANCE_VALIDATOR_SEMANTICS_CHECK_AND_FRESH_REBINDING_DIRECT_CHILD_ONLY`
- Package itself authorizes correction or execution: No
- Official execution: `NOT_APPROVED`
- Other project conversations, thread tools, and global memory used: No

## Binding History

```text
5G-B package:
f281864b424c406b42718c4ec58d7266ecafd9a3

5G-B approval governance:
79e69eab874f669d79d433fa965f5f5f48659332

Hard Failure 10 checkpoint:
aab591b92804fd1226a62751c38d056918f71b41

5G-A.1 implementation/evidence:
c21f3f58b2b1d4ccf235daba9c85937daedf4e3b

Hard Failure 9:
d1c7cf9d78563e30a1e0fe0d6812b36d15b95a9a

Hard Failure 8:
0f35ec895c756348e8a10803c6dd961a37344fb0
```

Any future approval must explicitly bind the package commit containing this Request and its Manifest. An approval omitting that package commit is invalid.

The first 5G-B.1 package commit:

```text
9536ffb4ce845aeff9db3552f890612ca6e9e2a3
```

is explicitly superseded and is not approvable. Its validator used case-insensitive sort/comparison, could not reject duplicate keys in raw governance JSON before object materialization, and did not freeze the complete real precommit validator. Package Review 1 records that decision at `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_PACKAGE_REVIEW_1.md` (2,835 bytes; SHA-256 `975D67C0A54FE919C81E60569F8C3096E1AC0F2464BECE40A478117B47E856C7`).

## Accepted Failure Evidence And Frozen History

Independent Review 1 accepts Hard Failure 10 and the two 5G-B runs only as historical failure evidence. It freezes:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_10.md` | 6,207 | `1B92A16EE4B9D14BA09C3345337A9E5026DAA2C577B4E123870C0C8895EE8497` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_SYNTHETIC_REBINDING_AUDIT.md` | 3,973 | `50D125193CDD49B2A33ADF4EFC3A5F4A0F74A4029EE640AA032B4FEE990B3054` |
| `results/stage4b_u1_d_pregold_amendment_5g_b_governance_binding.json` | 5,317 | `12BF30F3EF70D0420237DCF0A6C6D5D06C05990DDF637EA4CF31B7C3C7655730` |
| `results/stage4b_u1_d_pregold_amendment_5g_b_synthetic_rebinding.json` | 69,144 | `00281BED7BC0DF10D47382CC47D0884BFCD331F0CB92EFC0B51F0FF176827A2A` |

Historical rebinding facts:

```text
complete runs: 2
tests each: 246/246
execution-head tests: 41
typed-policy tests: 44
failures/errors/skips: 0/0/0
tracked files: 33
tracked digest:
50D3BCDDAE42961ECCDDC30ADE683D6180F9CDFC319D085BEC762B8985A17041
evidence bytes: 69144
evidence SHA-256:
00281BED7BC0DF10D47382CC47D0884BFCD331F0CB92EFC0B51F0FF176827A2A
all official/helper/preflight/token/capture counts: 0
```

These files must not be modified, overwritten, deleted, migrated or used as a new active execution binding.

## Frozen Implementation Surface

| Role | Path | Bytes | SHA-256 |
|---|---|---:|---|
| deterministic runner | `scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py` | 22,416 | `83816A962EDC8F06B53B5826E3F7519BD72D2CA0DF91C46751A9B12215867F28` |
| execution-head helper | `scripts/stage4b_u1_preflight_execution_head_binding.py` | 6,318 | `517C5C4DB22A82B4CBCA3D8BB751AAE60C0DCC5B5948CC8419D8770A9CC3D174` |
| typed helper | `scripts/stage4b_u1_preflight_argument_policy.py` | 7,082 | `CCDC70D2E66E9D69CD64899676EA5150FEE0381E74F4C9DEED2A0FFB5EE436F4` |
| path helper | `scripts/stage4b_u1_preflight_path_equivalence.py` | 3,543 | `1A17C0E750F91CEF2F638A0B0C6FD381110692E6B2D467C1F5243ADF3F35B3FF` |
| capture | `scripts/stage4b_u1_capture_diagnostic_decisions.py` | 20,221 | `7C7B159911384B436FDCC1B20D26F2F545F2DC55EAD1F7B2B134B273110ED40A` |
| comparator | `scripts/stage4b_u1_compare_decisions.py` | 12,854 | `42FA3F74679672B0595CC76B519D59C03CB193415DD03F56E37260A961D94014` |

No implementation or test file may change under this Amendment.

## Requested Future Approval-Governance Commit

After a future explicit package-bound approval, first create and push one approval-governance commit whose changed-path set is exactly:

```text
AGENTS.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_APPROVAL_DECISION.md
```

No semantics check or synthetic command may run before local HEAD, `origin/main` and GitHub `main` are confirmed equal at that approval commit with a clean worktree.

## Frozen Corrected Validator Contract

The corrected validator uses three fail-closed layers in this order:

1. Read the governance binding once as strict UTF-8 bytes.
2. Pass those bytes on stdin to the Manifest-embedded Python 3.12 standard-library parser. Its `object_pairs_hook` rejects exact duplicate raw keys before object materialization at every JSON level, and it separately rejects case-fold collisions inside `bound_files`.
3. Materialize the parser's bound-file name report and the Manifest expected names as arrays, reject duplicates on either side, and require case-sensitive exact-set equality.

The key-set operation is frozen as:

```powershell
$actualNames = @(
    $inspection.bound_file_entries |
    ForEach-Object { [string]$_.name }
)

$expectedNames = @(
    $manifest.future_governance_binding_contract.bound_files_required |
    ForEach-Object { [string]$_ }
)

if ($actualNames.Count -ne $expectedNames.Count) {
    throw 'bound file count failed'
}

$uniqueActual = @(
    $actualNames |
    Sort-Object -CaseSensitive -Unique
)

$uniqueExpected = @(
    $expectedNames |
    Sort-Object -CaseSensitive -Unique
)

if ($uniqueActual.Count -ne $actualNames.Count) {
    throw 'duplicate actual bound file name'
}

if ($uniqueExpected.Count -ne $expectedNames.Count) {
    throw 'duplicate expected bound file name'
}

$delta = @(
    Compare-Object `
        -ReferenceObject $uniqueExpected `
        -DifferenceObject $uniqueActual `
        -CaseSensitive
)

if ($delta.Count -ne 0) {
    throw 'bound file exact key set failed'
}
```

Case-insensitive sorting, comparison, normalization, aliasing and cardinality-only acceptance are forbidden.

## Complete Real Precommit Validator Freeze

The complete Windows PowerShell 5.1 command is frozen verbatim in the Manifest as a 195-line `source_lines` array joined by LF with no trailing newline:

```text
source bytes:
15966

source SHA-256:
0F066387B8523B0EA387444076A1113913082D283C28C2DE3FFB33872D558249
```

The future approval decision must contain the corrected package commit, the exact decimal source byte token `15966`, and source SHA-256 `0F066387B8523B0EA387444076A1113913082D283C28C2DE3FFB33872D558249`. The frozen validator checks all three bindings. No post-approval wrapper expression, source extension or replacement validator is allowed. Before execution, the source must be reconstructed exactly from the Manifest and its bytes/SHA rechecked.

The frozen command covers:

- raw JSON duplicate-key rejection before `ConvertFrom-Json`;
- raw `bound_files` case-only collision rejection;
- case-sensitive exact key sets for governance records, the 15-name path registry, approval changed paths and the fresh worktree;
- package commit as the approval commit's actual parent, approval commit as actual synchronized HEAD, and governance metadata equality;
- strict-boolean artifact presence;
- all 15 bound-file paths, byte counts and SHA-256 values;
- the three historical 5G-B artifact fingerprints;
- fresh evidence `246/41/44`, 33 tracked files, failure/error/skip zeros, all official/helper/preflight/token/capture zeros, and two-run byte equality metadata;
- the exact three untracked fresh paths and absence of every extra modified or untracked path.

The command accesses no official input and calls no project helper. Its only external processes are `git` for repository metadata/worktree status and the exact frozen Python executable for stdin-only standard-library JSON parsing.

## One Pure In-Memory Semantics Check

After approval synchronization and before synthetic execution, the corrected validator semantics may be exercised once against in-memory synthetic fixtures. That single wrapper invocation must prove:

- the exact expected key set passes;
- one missing key fails;
- one extra key fails;
- duplicate actual names fail;
- duplicate expected names fail;
- case-only actual-key drift fails;
- case-only expected-key collision fails;
- raw JSON duplicate `bound_files` keys fail before object materialization;
- raw JSON case-only key collisions fail.

The wrapper may invoke exactly one frozen Python 3.12 standard-library parser process, with all raw fixtures supplied in one in-memory stdin payload. It may not use any other subprocess, filesystem, Git, GitHub, helper, token, capture or official path.

Failure consumes the semantics-check authorization and stops without synthetic execution or retry.

## Fresh Paths

The future run must exclusively create new paths:

```text
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_SYNTHETIC_REBINDING_AUDIT.md
results/stage4b_u1_d_pregold_amendment_5g_b_1_governance_binding.json
results/stage4b_u1_d_pregold_amendment_5g_b_1_synthetic_rebinding.json
```

All three must be absent before the first run. The three historical 5G-B paths must remain unchanged before, between and after all future steps.

## Exact Two-Run Fresh Rebinding

On final 5G-B.1 approval-governance bytes, invoke the frozen complete runner exactly twice. No preliminary, targeted, repair, retry or third run is requested.

Each run must satisfy exactly:

```text
tests: 246/246
execution-head tests: 41
typed-policy tests: 44
failures/errors/skips: 0/0/0
tracked files: 33
official/helper/preflight/token/capture counts: 0
```

Run 1 writes one unique OS-temporary evidence file. Run 2 exclusively creates the new 5G-B.1 evidence path. Both runs must use identical tracked bytes and produce byte-identical complete evidence. Run 1 may be deleted only after every gate and direct comparison passes.

## Fresh Governance Binding Contract

The fresh governance binding must bind the new package/approval commit and exactly the Manifest-defined key set. It must include path/bytes/SHA for new Request, Manifest, approval decision, final `AGENTS.md`, Hard Failure 10 review/audit, the three historical 5G-B artifacts, original 5G-B Request/Manifest/approval, 5G-A.1 implementation/evidence and fresh 5G-B.1 evidence.

It must not register its own SHA. The future exact-three-path direct-child commit is the external content binding.

## Single Corrected Real Precommit Validation

After both fresh runs and all three fresh artifacts are generated, reconstruct the frozen 15,966-byte command from the Manifest, verify SHA-256 `0F066387B8523B0EA387444076A1113913082D283C28C2DE3FFB33872D558249`, and run it exactly once against the real new governance binding and Manifest. It must validate every frozen content and scope gate without additional expressions.

Failure stops without correction, second validation or commit.

## Fresh Exact-Three-Path Direct Child

Only after the single real validation passes may one commit be created as the direct child of the 5G-B.1 approval-governance commit. Its changed-path set must be exactly:

```text
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_SYNTHETIC_REBINDING_AUDIT.md
results/stage4b_u1_d_pregold_amendment_5g_b_1_governance_binding.json
results/stage4b_u1_d_pregold_amendment_5g_b_1_synthetic_rebinding.json
```

After push, confirm local/origin/GitHub equality and clean worktree, then stop immediately.

## One-Time Limits

```text
in-memory validator semantics checks: 1
post-approval complete synthetic runs: 2
real corrected precommit validations: 1
fresh direct-child commits: 1
automatic retry: false
```

Any failure consumes the current gate and stops. It must not be repaired and rerun under the same approval.

## Explicitly Not Requested Or Authorized

- any action before a package-bound 5G-B.1 approval;
- any code or test modification;
- reuse, overwrite or modification of historical 5G-B artifacts;
- execution-head helper official call;
- formal preflight, typed/path helper official call or official input access;
- token, capture, controller, verifier, evaluator/Gold, rankings, policy, source audit, 5C-B inventory, reservation or Stage3B;
- cache, data, model, parameter, equivalence or stop-rule changes;
- history rewrite, reset, force-push or automatic recovery.

## Requested Completion State

```text
AMENDMENT_5G_B_1_FRESH_REBINDING_DIRECT_CHILD_COMPLETE_AWAITING_REVIEW
HARD_FAILURE_10_DIRECT_CAUSE_CONFIRMED
HISTORICAL_5G_B_ARTIFACTS_FROZEN

DERIVED_EXECUTION_HEAD_VALIDATION_NOT_APPROVED
FORMAL_PREFLIGHT_NOT_APPROVED
OFFICIAL_INPUT_ACCESS_NOT_APPROVED
AUTHORIZATION_TOKEN_USE_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

Until a new approval explicitly binds the corrected package commit, the effective state remains:

```text
CORRECTED_AMENDMENT_5G_B_1_PACKAGE_AWAITING_APPROVAL
SUPERSEDED_PACKAGE_9536FFB_NOT_APPROVABLE

VALIDATOR_SEMANTICS_CHECK_NOT_APPROVED
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
```
