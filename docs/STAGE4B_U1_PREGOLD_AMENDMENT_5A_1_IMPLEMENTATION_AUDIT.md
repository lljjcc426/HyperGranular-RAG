# Stage4B-U1-D Pre-Gold Amendment 5A.1 Implementation Audit

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Mode: `run / reproducibility verification`
- Audit date: 2026-07-14
- Approval package: `3137ace0328dd24908f95737ea1dcbe0c8fe045e`
- Approval governance commit: `d34835159fd600c8b629114946afee9e943d143c`
- Approval decision: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_1_APPROVAL_DECISION.md`
- Verification Status: `VERIFIED_SYNTHETIC_ONLY`
- Official diagnosis: `NOT_APPROVED`
- Controller rerun: `NOT_APPROVED`
- Verifier: `NOT_APPROVED`
- Gold: `NOT_APPROVED`
- Other project conversations, thread tools, and global memory used: No

## Implemented Scope

Only the three approved implementation/test files were changed:

1. `scripts/stage4b_u1_capture_diagnostic_decisions.py`
   - added required `--expected-units-sha256`, `--expected-queries-sha256`, and `--expected-channel-audit-sha256` arguments;
   - froze the three official expected values in the capture module;
   - added 64-hex normalization, regular-file enforcement, and exact hashing;
   - official expected values must match the external freeze before actual-file hashing;
   - all three actual hashes are checked before semantic parsing/cache loading/computation;
   - all three are checked again after temporary-decisions cleanup and immediately before audit creation;
   - reference-decisions hashing now occurs only after the three-input pre-gate;
   - pre/post failure leaves no audit and the temporary directory lifecycle performs cleanup.
2. `scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py`
   - binds the 5A.1 review, request, Manifest, and approval decision;
   - adds the three official channel paths to the process-wide access guard;
   - raises the complete-suite gate to 104 and records the 5A.1 status/evidence properties;
   - registers the new active proof tests and writes to a new 5A.1 evidence path.
3. `tests/test_stage4b_u1_decisions_diagnostic.py`
   - retains all prior tests and adds nine channel-hash hardening tests;
   - removes synthetic use of the rejected 5B authorization token while retaining direct exact-path validation.

No controller, retrieval, common, comparator, channel-preparer, verifier, evaluator, official artifact, cache, or data file was modified.

## Frozen Input Values

| Input | SHA-256 |
|---|---|
| v2.3.1 unlabeled units | `114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA` |
| v2.3.1 unlabeled queries | `6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B` |
| v2.3.1 controller channel audit | `D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA` |

These values were copied from the approved package. The official files themselves were not opened during implementation or testing.

## Implementation Hashes

| File | SHA-256 | Status |
|---|---|---|
| `scripts/stage4b_u1_capture_diagnostic_decisions.py` | `7C7B159911384B436FDCC1B20D26F2F545F2DC55EAD1F7B2B134B273110ED40A` | modified as approved |
| `scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py` | `776AAF0DF8884E79647B144A88416EFAFFFA51AFDA43520203FB7FC745A88989` | modified as approved |
| `tests/test_stage4b_u1_decisions_diagnostic.py` | `C1A7B25D1F69E58812E994B0F8ECA7BAAE38EF50DE8BFA9246F4DF1EBF038D1C` | modified as approved |
| `scripts/stage4b_u1_goldfree_controller.py` | `C18AD3B672649BA846C5E191D0DBBAC7644A926D4B8CCD39176127175BBA7C1F` | unchanged |
| `scripts/stage4b_u1_goldfree_retrieval.py` | `3B50FAFD057E2565167ED09288D61829B3FBD044991F139F734F819955038A3B` | unchanged |
| `scripts/stage4b_u1_common.py` | `CDF7EAD6007DABE389ED0BD18983496F75290C32243FE6DF84716810CDE92CE4` | unchanged |
| `scripts/stage4b_u1_compare_decisions.py` | `FF4D623DF86FE42EB4ACDFF9D3321FCA768E03B64597C6CC88931359CEDB2DD4` | unchanged |
| `tests/test_stage4b_u1_goldfree.py` | `CA61B466C7DDF583D827FD2D99C024D646BA3962C80B9137D480C84DEA374C71` | unchanged |

The controller checkpoint reported by the evidence remains `stage4b_u1_v2_3_1`. Comparator semantics and raw byte equivalence were not changed.

## Synthetic Coverage

The original 98 tests were retained. Nine tests were added, producing 107 total:

- units expected-SHA mismatch rejected before semantic parsing;
- queries expected-SHA mismatch rejected before semantic parsing;
- controller channel-audit expected-SHA mismatch rejected before semantic parsing;
- official caller-provided expected SHA must equal the external freeze;
- channel inputs must be regular files;
- correct three-hash synthetic path passes;
- units drift during computation leaves no audit and cleans temporary decisions;
- queries drift during computation leaves no audit and cleans temporary decisions;
- channel-audit drift during computation leaves no audit and cleans temporary decisions.

Existing tests continue to prove synthetic allowlist rejection before file open, official mode lockout, exact-path enforcement, no full-controller/ranking/policy call, cache post-fingerprint, comparator semantics, and temporary cleanup on success and exceptions.

## Commands And Results

### Static validation

```powershell
python -m py_compile scripts\stage4b_u1_capture_diagnostic_decisions.py scripts\stage4b_u1_run_decisions_diagnostic_synthetic_verification.py tests\test_stage4b_u1_decisions_diagnostic.py
```

Result: exit 0.

### Targeted capture tests

```powershell
python -m unittest tests.test_stage4b_u1_decisions_diagnostic.Stage4BU1DiagnosticCaptureTests -v
```

Result: 22/22 passed, zero failures/errors/skips, exit 0.

### Preliminary complete suite

```powershell
python -m unittest discover -s tests -p "test_stage4b_u1*.py" -v
```

Result: 107/107 passed, zero failures/errors/skips, exit 0.

### Final deterministic evidence

The following command ran exactly twice against unchanged tracked bytes:

```powershell
python scripts\stage4b_u1_run_decisions_diagnostic_synthetic_verification.py --output results\stage4b_u1_d_pregold_amendment_5a_1_synthetic_verification.json
```

| Gate | Run 1 | Run 2 |
|---|---:|---:|
| tests | 107/107 | 107/107 |
| failures | 0 | 0 |
| errors | 0 | 0 |
| skipped | 0 | 0 |
| official-path access attempts | 0 | 0 |
| evidence bytes | 20,495 | 20,495 |
| evidence SHA-256 | `81A8A5960395F729B643A42505E7F947962B338CD97ADD0506636D3AA2020A67` | `81A8A5960395F729B643A42505E7F947962B338CD97ADD0506636D3AA2020A67` |

Direct byte comparison: `True`.

## Anomalies And Failed Commands

- During initial read-only inspection, `rg.exe` could not start because Windows returned `Access is denied`. PowerShell `Select-String` was used as a read-only fallback. This did not access official files or affect implementation/test results.
- The first static review found two adjacent runner output-path strings that Python would concatenate. This was corrected before any runner execution; no evidence file had been created or overwritten.
- The existing optional import chain emitted the known NumPy 2.4.6/`numexpr` ABI warning during test discovery. All targeted, complete, and evidence commands nevertheless exited zero.
- No test or evidence command failed. No automatic retry occurred.

## Boundary Verification

- Process-wide official-path guard: installed.
- Blocked or attempted official-path accesses: `0` in both final runs.
- Rejected 5B authorization token used: No.
- Official diagnostic/preflight/controller/verifier/evaluator executed: No.
- Official units/queries/channel audit/source audit/cache/decisions/rankings/policy/Gold opened: No.
- Reservation or Stage3B accessed: No.
- Official or cache file created, overwritten, deleted, or migrated: No.

## Result

```text
AMENDMENT_5A_1_SYNTHETICALLY_VERIFIED
OFFICIAL_DIAGNOSIS_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

The next allowed action is to commit and push this implementation/evidence/audit, then create a revised implementation-bound Amendment 5B v2 approval package and stop.
