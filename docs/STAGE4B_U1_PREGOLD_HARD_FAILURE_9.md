# Stage4B-U1-D Pre-Gold Hard Failure 9

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Failure date: 2026-07-14
- Approved package: `86ae4a83d55e61653f3cce9260a00852b4aaebda`
- Approval governance: `fd50bc30f5acbf4955e3a051fbee70062e6e168c`
- Failure status: `AMENDMENT_5G_A_SYNTHETIC_VERIFICATION_STOPPED_HARD_FAILURE_9`
- Failure boundary: `PRELIMINARY_RUNNER_ACTIVE_PROOF_UNIQUENESS_GATE_BEFORE_TEST_EXECUTION`
- Official execution: `NOT_AUTHORIZED_AND_NOT_EXECUTED`
- Other project conversations, thread tools, and global memory used: No

## Approved Scope Reached Before Failure

The 5G-A approval decision and `AGENTS.md` were committed and pushed before implementation at approval-governance commit `fd50bc30f5acbf4955e3a051fbee70062e6e168c`.

Implementation changes were limited to the three approved paths:

| Path | Bytes | SHA-256 at failure checkpoint |
|---|---:|---|
| `scripts/stage4b_u1_preflight_execution_head_binding.py` | 6,318 | `517C5C4DB22A82B4CBCA3D8BB751AAE60C0DCC5B5948CC8419D8770A9CC3D174` |
| `tests/test_stage4b_u1_preflight_execution_head_binding.py` | 11,550 | `52C0983E623D126F8A8E631DE7C8F08F14F04DA26484763CA6939B84236EC747` |
| `scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py` | 22,351 | `EBCCA245F2B4D07CCF061DDD88D70E83C76563F4F4D547EEFF711307F92B0BB1` |

All 24 Manifest-frozen existing files retained their exact SHA-256 values before and after the failed command.

## Commands Before Failure

### Syntax compilation

The three approved implementation/test paths were compiled in memory without writing bytecode:

```powershell
& 'D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe' -c "from pathlib import Path; paths=['scripts/stage4b_u1_preflight_execution_head_binding.py','tests/test_stage4b_u1_preflight_execution_head_binding.py','scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py']; [compile(Path(p).read_text(encoding='utf-8'), p, 'exec') for p in paths]; print('SYNTAX_COMPILE=PASS')"
```

Result: `SYNTAX_COMPILE=PASS`.

### Targeted synthetic tests

```powershell
& 'D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe' `
  -m unittest discover `
  -s tests `
  -p 'test_stage4b_u1_preflight_execution_head_binding.py' `
  -v
```

Result: 41/41 passed, zero failure/error/skip. This was the only targeted invocation; no corrected retry occurred.

## Failed Preliminary Command

The runner was invoked once with a newly generated OS-temporary output path:

```powershell
& 'D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe' `
  scripts\stage4b_u1_run_decisions_diagnostic_synthetic_verification.py `
  --output 'C:\Users\cc\AppData\Local\Temp\stage4b_u1_5g_a_preliminary_0c7dae92304d4afcbae18456c870e2ce.json'
```

The process exited 1 before `unittest.TextTestRunner.run()`:

```text
ValueError: Required active access/cleanup proof test is missing or duplicated
```

The preliminary path was never created. No evidence file was written and no temporary file was deleted. The complete suite test count for this invocation is 0 because the runner stopped at active-proof discovery/uniqueness validation before test execution.

## Read-Only Direct-Cause Diagnosis

A source-only comparison of runner suffixes against `def test_*` names found two non-unique active-proof names:

```text
test_missing_governance_binding_is_rejected
  tests/test_stage4b_u1_goldfree.py
  tests/test_stage4b_u1_preflight_execution_head_binding.py

test_helper_uses_only_python_standard_library
  tests/test_stage4b_u1_preflight_path_equivalence.py
  tests/test_stage4b_u1_preflight_execution_head_binding.py
```

The runner's `REQUIRED_ACTIVE_PROOF_SUFFIXES` also contains `test_helper_uses_only_python_standard_library` twice: once for the existing path-equivalence proof and once for the new execution-head proof. Because the runner requires every suffix to resolve to exactly one discovered test ID, the gate correctly failed closed.

The direct cause is therefore a 5G-A synthetic-runner active-proof naming/registration collision. It is not a helper semantic failure, frozen-file drift, official input failure, Git/GitHub drift, formal-preflight failure, cache failure or capture failure.

## Access And Output Boundary

- official input metadata/content access: 0;
- typed-helper official invocation: 0;
- path-helper official invocation: 0;
- real Git/GitHub execution-head helper validation: 0;
- formal preflight invocation: 0;
- authorization token use: 0;
- official capture/comparator invocation: 0;
- controller/verifier/evaluator/Gold invocation: 0;
- reservation/Stage3B access: 0;
- formal decisions/rankings/policy/controller audit/`VERIFIED_PRE_GOLD`: absent and untouched;
- official cache or historical evidence modification/deletion: 0.

## Stop Decision

No test was renamed, no runner suffix was corrected and no preliminary or final suite was rerun after the failure. The failed implementation checkpoint and this audit must be committed and pushed before any revision.

A correction requires a new package-bound Amendment before execution. The minimal candidate scope is limited to collision-free execution-head test names and their corresponding runner active-proof suffixes, followed by a fresh targeted run and complete synthetic verification. No such correction or rerun is authorized by this audit.

Current state:

```text
AMENDMENT_5G_A_SYNTHETIC_VERIFICATION_STOPPED_HARD_FAILURE_9
HARD_FAILURE_8_DIRECT_CAUSE_CONFIRMED
HARD_FAILURE_4_DIAGNOSIS_INCOMPLETE

SYNTHETIC_RETRY_NOT_APPROVED
SECOND_FORMAL_PREFLIGHT_NOT_APPROVED
OFFICIAL_INPUT_ACCESS_NOT_APPROVED
AUTHORIZATION_TOKEN_USE_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
