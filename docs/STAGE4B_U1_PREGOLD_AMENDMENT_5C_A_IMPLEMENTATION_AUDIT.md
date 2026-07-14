# Stage4B-U1-D Pre-Gold Amendment 5C-A Implementation Audit

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-14
- Package commit: `a8caa2a3b26ae13d0b149e4995e3a017e8edb2e7`
- Approval governance commit: `a680c0358ac351a5e80c9829d48a7b8e88950f4c`
- Requested mode: implementation and synthetic verification only
- Official reference/schema scan: Not accessed or executed
- Comparator/capture/controller/verifier/evaluator/Gold: Not executed by the inventory path
- Other project conversations, thread tools, and global memory used: No

## Implemented Scope

Only the three approved files were added:

```text
scripts/stage4b_u1_inventory_decision_schemas.py
scripts/stage4b_u1_run_schema_inventory_synthetic_verification.py
tests/test_stage4b_u1_decision_schema_inventory.py
```

The inventory module uses only Python standard-library imports. It does not import or call the existing comparator, capture, controller, retrieval, verifier, evaluator, ranking, or policy code.

The implementation enforces:

- UTF-8 JSONL with one nonblank object per physical line;
- duplicate-key rejection at every object nesting level;
- hard failure on invalid JSON, blank/non-object rows, `NaN`, `Infinity`, `-Infinity`, and overflow-created non-finite floats;
- distinct `null`, `bool`, `integer`, finite `number`, `string`, `array`, and `object` schemas;
- recursive object and array-element schemas without retaining values;
- sorted, deduplicated array element-schema sets with an empty-array marker and no element order, multiplicity, or array length;
- deterministic ordered and order-insensitive structural signatures from canonical UTF-8 schema JSON;
- separate field-order-only classification;
- main ordered schema selection by maximum row count and lexicographically smallest ordered signature tie-break;
- value-free aggregate output with row counts, first/last line numbers, field names/types/nesting, and differences from the main schema;
- exclusive output creation, pre/post input SHA equality, and cleanup of staging/partial output after failure;
- rejection of the frozen future official reference path before file open unless a future 5C-B token and exact frozen SHA are supplied. The token was not used in 5C-A.

## Test Coverage

The approved minimum was 107 existing plus at least 12 new tests, for at least 119 total. The implementation added 24 isolated tests, producing 131 total.

The new tests cover homogeneous schemas, field additions/removals, field-order-only differences, bool/integer/finite-number separation, nested object/array structure, array value/order/multiplicity/length exclusion, empty arrays, top-level and nested duplicate keys, invalid/blank/non-object/invalid-UTF-8 input, non-finite numbers, value/ID leakage, deterministic main-schema selection, deterministic bytes, exclusive output, success/failure cleanup, input drift, existing-output pre-gate, future official-path pre-open rejection, and prohibited import/call absence.

## Command Record

### Targeted inventory suite

```text
python -m unittest discover -s tests -p test_stage4b_u1_decision_schema_inventory.py -v
```

Result: 24/24 passed, zero failures/errors/skips.

### Preliminary complete-run failure

The first preliminary complete runner exited nonzero before writing evidence:

```text
ValueError: A required schema inventory proof test is missing or duplicated
```

Cause: the new runner matched required proof-test suffixes across the entire 131-test suite, where an older module contained a duplicate suffix. Direct inventory-module discovery confirmed all 24 new test IDs existed exactly once. The runner was corrected to match required suffixes only inside `test_stage4b_u1_decision_schema_inventory`. No inventory, test, official path, or frozen file behavior changed. The failed command produced no evidence and performed zero official access.

### Preliminary complete suite after correction

Result: 131/131 passed, 24 inventory tests, zero failures/errors/skips/official-path access.

### Final governance-bound deterministic runs

The final two complete runs used unchanged implementation and final `AGENTS.md` bytes:

| Gate | Run 1 | Run 2 |
|---|---:|---:|
| Tests | 131/131 | 131/131 |
| Inventory tests | 24 | 24 |
| Failures | 0 | 0 |
| Errors | 0 | 0 |
| Skips | 0 | 0 |
| Official-path access attempts | 0 | 0 |
| Evidence bytes | 22,234 | 22,234 |
| Evidence SHA-256 | `0D13392B5C96BAD7EC4D67C22A7515B4A6D211C8EFBB3A4486F9BA5531A1EF7C` | `0D13392B5C96BAD7EC4D67C22A7515B4A6D211C8EFBB3A4486F9BA5531A1EF7C` |

Direct in-memory `SequenceEqual` returned `True`. Final evidence is `results/stage4b_u1_d_pregold_amendment_5c_a_synthetic_verification.json`.

## Environment Warning

Each complete run emitted the pre-existing NumPy 2.4.6/`numexpr` 1.x ABI warning through the unchanged legacy import chain. The optional dependency warning did not abort discovery or execution; every accepted complete run exited zero and passed all 131 tests. No package, environment, or frozen source file was changed to suppress it.

## Complete Bound SHA-256 Inventory

| File | SHA-256 |
|---|---|
| `AGENTS.md` | `6C9846B5A098C58FB247E9A029B4E465DC8C25001AA1785355207AC6654B68BF` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_APPROVAL_DECISION.md` | `A9629195C7C08E5763EA839E2892980EE1EB5A165EAF08501151322F63A02A7B` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_APPROVAL_REQUEST.md` | `AF4F0AD10AF3BE52C3E706721D6993F1EB1B203AC557AAFC0EC4383C7F842600` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_MANIFEST.json` | `F0C50CAA2B47DBE5FFD2747708764E8AD38454A08EDDA70F57B8E36F81AEA81F` |
| `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_5.md` | `598D19DE1862BE8E09057834803B5B3F71FF5EDBB48BA24B9F0C454BB1685B4C` |
| `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_5_REVIEW_1.md` | `74FFE546B6922F92ECAF8343AB0DE20B5C254C638EB4AD037A8088E4917CD5E1` |
| `scripts/stage4b_u1_capture_diagnostic_decisions.py` | `7C7B159911384B436FDCC1B20D26F2F545F2DC55EAD1F7B2B134B273110ED40A` |
| `scripts/stage4b_u1_common.py` | `CDF7EAD6007DABE389ED0BD18983496F75290C32243FE6DF84716810CDE92CE4` |
| `scripts/stage4b_u1_compare_decisions.py` | `FF4D623DF86FE42EB4ACDFF9D3321FCA768E03B64597C6CC88931359CEDB2DD4` |
| `scripts/stage4b_u1_goldfree_controller.py` | `C18AD3B672649BA846C5E191D0DBBAC7644A926D4B8CCD39176127175BBA7C1F` |
| `scripts/stage4b_u1_goldfree_retrieval.py` | `3B50FAFD057E2565167ED09288D61829B3FBD044991F139F734F819955038A3B` |
| `scripts/stage4b_u1_inventory_decision_schemas.py` | `CC48C73306AB48D14E021AE69740A59F2F0218C241E47EE283ECD21E1C81F176` |
| `scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py` | `776AAF0DF8884E79647B144A88416EFAFFFA51AFDA43520203FB7FC745A88989` |
| `scripts/stage4b_u1_run_schema_inventory_synthetic_verification.py` | `01B84D359B49AC00BD7B52100D3157A5D0BA1DA78B7D5FF3D0ABCBBE7708E7FA` |
| `tests/test_stage4b_u1_decision_schema_inventory.py` | `89881A70EBE12F49E63B08EE8846F78985B98710412C63EDA67CF8A695332E30` |
| `tests/test_stage4b_u1_decisions_diagnostic.py` | `C1A7B25D1F69E58812E994B0F8ECA7BAAE38EF50DE8BFA9246F4DF1EBF038D1C` |
| `tests/test_stage4b_u1_goldfree.py` | `CA61B466C7DDF583D827FD2D99C024D646BA3962C80B9137D480C84DEA374C71` |

The eight files frozen by the approval exactly retain their registered baseline hashes. No existing implementation, test, official artifact, historical evidence, or failure record was modified or deleted.

## Access And Stop Boundary

The process-wide access guard covered the frozen reference decisions, official channel inputs, cache, source audit, registered formal outputs, rankings, policy, evaluator/Gold, reservation, and Stage3B paths. Both final runs recorded zero attempted access. The future 5C-B token was not passed.

Current state:

```text
AMENDMENT_5C_A_SYNTHETICALLY_VERIFIED
OFFICIAL_SCHEMA_SCAN_NOT_APPROVED
COMPARATOR_CHANGE_NOT_APPROVED
OFFICIAL_CAPTURE_RETRY_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

The only next permitted action is creation and push of an implementation-bound 5C-B request and Manifest, followed by immediate stop for independent approval.
