# Stage4B-U1-D Pre-Gold Amendment 5G-A.1 Implementation And Recovery Audit

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-14
- Approved package: `d02b19dfd5a527d0159b930662f5a868c8235d35`
- Approval governance: `3d818cee86e1faca16c2bdab3baf4fd5411cff75`
- Failed checkpoint baseline: `d1c7cf9d78563e30a1e0fe0d6812b36d15b95a9a`
- Recovery status: `AMENDMENT_5G_A_1_SYNTHETICALLY_VERIFIED`
- Hard Failure 9: `DIRECT_CAUSE_CONFIRMED_AND_MINIMALLY_REPAIRED`
- Hard Failure 8: `DIRECT_CAUSE_CONFIRMED`
- Hard Failure 4 diagnosis: `INCOMPLETE`
- Official execution: `NOT_AUTHORIZED_AND_NOT_EXECUTED`
- 5G-B package: `NOT_AUTHORIZED_AND_NOT_ASSEMBLED`
- Other project conversations, thread tools, and global memory used: No

## Governance Order

The package-bound approval decision and final approval governance were committed and pushed before repair:

```text
3d818cee86e1faca16c2bdab3baf4fd5411cff75
```

Only after that push were the two approved files repaired. No test, inventory or runner command preceded the approval-governance push.

## Exact Two-File Repair

Relative to failed checkpoint `d1c7cf9d78563e30a1e0fe0d6812b36d15b95a9a`, implementation/test changes are exactly:

| Path | Additions | Deletions | Authorized result |
|---|---:|---:|---|
| `tests/test_stage4b_u1_preflight_execution_head_binding.py` | 2 | 2 | two function-name token replacements only |
| `scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py` | 11 | 9 | two suffix replacements, duplicate removal by specialization, tuple-uniqueness gate, exact 246/41/44 count gate |

The test-name replacements were exactly:

```text
test_missing_governance_binding_is_rejected
-> test_execution_head_missing_governance_binding_is_rejected

test_helper_uses_only_python_standard_library
-> test_execution_head_helper_uses_only_python_standard_library
```

No test body, assertion, fixture, input, helper call, split, merge, parameterization or skip changed. The test file still defines exactly 41 tests.

The runner changed only the corresponding execution-head suffixes, left generic `test_helper_uses_only_python_standard_library` once for the path-equivalence module, added the dedicated pre-discovery duplicate-suffix error, and changed the count gate from minima to exact total/execution-head/typed-policy counts. Test discovery pattern, all other suffixes, official guard, tracked-file set, evidence schema/output path, access counters and scientific verified properties remained unchanged.

## Frozen Helper And Existing Files

| Path | Bytes | SHA-256 |
|---|---:|---|
| `scripts/stage4b_u1_preflight_execution_head_binding.py` | 6,318 | `517C5C4DB22A82B4CBCA3D8BB751AAE60C0DCC5B5948CC8419D8770A9CC3D174` |

The helper is byte-identical to the Hard Failure 9 checkpoint. All 24 Manifest-frozen existing files independently recomputed to their registered SHA-256 values before inventory, before final execution and after final execution.

## Source-Only Active-Proof Inventory

Inventory ran exactly once after the repair and before test import/execution. It used only Python standard-library AST parsing over the runner and `tests/test_stage4b_u1*.py` sources. The command body:

```powershell
$python='D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe'
@'
import ast
from collections import Counter
from pathlib import Path

root = Path('.')
runner_path = root / 'scripts' / 'stage4b_u1_run_decisions_diagnostic_synthetic_verification.py'
runner_tree = ast.parse(runner_path.read_text(encoding='utf-8'), filename=str(runner_path))
suffixes = None
for node in runner_tree.body:
    if isinstance(node, ast.Assign) and any(
        isinstance(target, ast.Name)
        and target.id == 'REQUIRED_ACTIVE_PROOF_SUFFIXES'
        for target in node.targets
    ):
        suffixes = ast.literal_eval(node.value)
        break
if not isinstance(suffixes, tuple) or not all(isinstance(value, str) for value in suffixes):
    raise SystemExit('FAIL: suffix registry is not a literal text tuple')
if len(suffixes) != len(set(suffixes)):
    raise SystemExit('FAIL: suffix registry contains duplicates')
definitions = []
for path in sorted((root / 'tests').glob('test_stage4b_u1*.py')):
    tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test_'):
            definitions.append((node.name, path.as_posix(), node.lineno))
counts = Counter(name for name, _, _ in definitions)
bad = [(suffix, counts[suffix]) for suffix in suffixes if counts[suffix] != 1]
if bad:
    raise SystemExit('FAIL: non-unique required suffix matches: ' + repr(bad))
required_names = {
    'test_execution_head_missing_governance_binding_is_rejected': 1,
    'test_execution_head_helper_uses_only_python_standard_library': 1,
    'test_helper_uses_only_python_standard_library': 1,
}
for name, expected in required_names.items():
    if counts[name] != expected:
        raise SystemExit(f'FAIL: {name} count={counts[name]} expected={expected}')
print('SOURCE_ONLY_INVENTORY=PASS')
print(f'TEST_FILES_SCANNED={len(list((root / "tests").glob("test_stage4b_u1*.py")))}')
print(f'GLOBAL_TEST_DEFINITIONS={len(definitions)}')
print(f'REQUIRED_SUFFIXES={len(suffixes)}')
print(f'UNIQUE_REQUIRED_SUFFIXES={len(set(suffixes))}')
print(f'REQUIRED_SUFFIX_EXACT_MATCHES={len(suffixes)}/{len(suffixes)}')
for name in required_names:
    print(f'{name}={counts[name]}')
print('TEST_MODULES_IMPORTED=0')
print('TESTS_EXECUTED=0')
'@ | & $python -
```

Complete output:

```text
SOURCE_ONLY_INVENTORY=PASS
TEST_FILES_SCANNED=6
GLOBAL_TEST_DEFINITIONS=246
REQUIRED_SUFFIXES=135
UNIQUE_REQUIRED_SUFFIXES=135
REQUIRED_SUFFIX_EXACT_MATCHES=135/135
test_execution_head_missing_governance_binding_is_rejected=1
test_execution_head_helper_uses_only_python_standard_library=1
test_helper_uses_only_python_standard_library=1
TEST_MODULES_IMPORTED=0
TESTS_EXECUTED=0
```

No second inventory was run.

## Targeted Verification

The execution-head module ran exactly once:

```powershell
& 'D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe' `
  -m unittest discover `
  -s tests `
  -p 'test_stage4b_u1_preflight_execution_head_binding.py' `
  -v
```

Result:

```text
tests: 41/41
failures: 0
errors: 0
skipped: 0
```

No targeted retry occurred.

## Final Two-Run Verification

No preliminary complete runner was invoked under 5G-A.1. After helper/frozen/scope/evidence-absence gates passed, the complete runner was invoked exactly twice by one fail-closed wrapper:

```text
run 1 output: unique OS-temp stage4b_u1_5g_a_1_final_run1_<runtime-guid>.json
run 2 output: results/stage4b_u1_d_pregold_amendment_5g_a_synthetic_verification.json
```

The wrapper compared all 33 runner-bound tracked file hashes before, between and after the runs. Run 2 was conditional on every run-1 gate. The run-1 OS-temp evidence was deleted only after both runs and direct byte comparison passed.

| Gate | Run 1 | Run 2 |
|---|---:|---:|
| tests | 246/246 | 246/246 |
| execution-head tests | 41 | 41 |
| typed-policy tests | 44 | 44 |
| failures/errors/skips | 0/0/0 | 0/0/0 |
| tracked files | 33 | 33 |
| tracked digest | `88338760CE2EC767D7F93279F4F3B82E916B0CBE4882257B8CF9133591EA8AE0` | same |
| official access | 0 | 0 |
| typed-helper official invocation | 0 | 0 |
| path-helper official invocation | 0 | 0 |
| execution-head filesystem/Git/subprocess calls | 0 | 0 |
| formal preflight | 0 | 0 |
| authorization token | 0 | 0 |
| official capture | 0 | 0 |

Evidence comparison:

```text
bytes: 69144
run 1 SHA-256: A6285498FCFE767297D7156B87CA6034A993B2DFBB167EF7DFA813E9ADD55292
run 2 SHA-256: A6285498FCFE767297D7156B87CA6034A993B2DFBB167EF7DFA813E9ADD55292
direct byte equality: true
run-1 OS-temp evidence deleted after equality: true
preliminary complete runner invocations: 0
```

Formal evidence:

```text
results/stage4b_u1_d_pregold_amendment_5g_a_synthetic_verification.json
```

The evidence schema remains the approved 5G-A schema, so its internal status field is `AMENDMENT_5G_A_SYNTHETICALLY_VERIFIED`. This recovery audit binds the same evidence to the approved 5G-A.1 repair and records the governing completion state as `AMENDMENT_5G_A_1_SYNTHETICALLY_VERIFIED`.

## Final File Hashes

| Path | Bytes | SHA-256 |
|---|---:|---|
| `scripts/stage4b_u1_preflight_execution_head_binding.py` | 6,318 | `517C5C4DB22A82B4CBCA3D8BB751AAE60C0DCC5B5948CC8419D8770A9CC3D174` |
| `scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py` | 22,416 | `83816A962EDC8F06B53B5826E3F7519BD72D2CA0DF91C46751A9B12215867F28` |
| `tests/test_stage4b_u1_preflight_execution_head_binding.py` | 11,580 | `EA39A9ECEBA36FE2BAA108B2C4B1C98981C8A5E3FE241F59F22F5D49458E02B8` |
| `results/stage4b_u1_d_pregold_amendment_5g_a_synthetic_verification.json` | 69,144 | `A6285498FCFE767297D7156B87CA6034A993B2DFBB167EF7DFA813E9ADD55292` |

Runner-bound final `AGENTS.md` was 48,090 bytes with SHA-256 `60EEFD995F2939EBC2EEDC606096D537CA814570288F625A23D45158DE014308`. It was not modified after final evidence generation.

## Failed Commands

No command failed under the 5G-A.1 approval. Hard Failure 9 remains preserved in its historical audit and was not overwritten or hidden.

## Boundary And Stop

- no preliminary complete runner;
- no real Git/GitHub execution-head validation through the helper;
- no official input metadata/content access;
- no typed/path helper official call;
- no formal preflight, token, capture or comparator;
- no controller, verifier, evaluator/Gold, reservation or Stage3B action;
- no cache, official artifact, historical evidence or failure-record modification/deletion;
- Hard Failure 4 diagnosis remains incomplete;
- 5G-B was not assembled.

Current state:

```text
AMENDMENT_5G_A_1_SYNTHETICALLY_VERIFIED
HARD_FAILURE_9_DIRECT_CAUSE_CONFIRMED
HARD_FAILURE_8_DIRECT_CAUSE_CONFIRMED
HARD_FAILURE_4_DIAGNOSIS_INCOMPLETE

SECOND_FORMAL_PREFLIGHT_NOT_APPROVED
OFFICIAL_INPUT_ACCESS_NOT_APPROVED
AUTHORIZATION_TOKEN_USE_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

This implementation/evidence checkpoint must be committed and pushed, then execution stops for independent review. No 5G-B package may be assembled under this approval.
