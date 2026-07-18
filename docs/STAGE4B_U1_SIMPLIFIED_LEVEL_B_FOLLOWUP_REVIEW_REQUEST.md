# Stage4B-U1-D Simplified Level B Follow-up Review Request

## Material Passport

- ID: `HGRAG-STAGE4B-U1-LEVEL-B-FOLLOWUP-20260718`
- Type: minimal verifier-integrity correction review
- Status: `AWAITING_LEVEL_B_FOLLOWUP_REVIEW`
- Returned review scope: strict row identity, JSON type, nullability, and raw ranking-ID contracts
- Returned review HEAD: `048b6bc3d66cdcdd498082cc83183df5dfb2de27`
- Corrected implementation commit: `8ab5e193d00733e0ae617b2c17f02da4ce01594f`
- Rebound config commit: `fba85c990efb0e3009a4c9fb0ca486ba1485c1f9`
- Official execution authorization: absent
- Gold evaluation authorization: absent
- Reservation authorization: absent

## Requested decision

Please confirm whether the single returned Level B defect is closed:

```text
ACCEPT_LEVEL_B_IMPLEMENTATION
```

or return an exact remaining Level B integrity defect. Acceptance still does not authorize official preflight/input/cache access, official controller/verifier execution, Gold evaluation, or reservation access.

## Minimal correction

Implementation correction `8ab5e193d00733e0ae617b2c17f02da4ce01594f` changes exactly:

- `scripts/stage4b_u1_independent_verifier.py`
- `tests/test_stage4b_u1_simplified.py`

No file was deleted. The verifier now validates, before any downstream `str()`, `int()`, or `float()` conversion:

1. decision/ranking `query_id`, `dataset`, and `sample_id` are native non-empty JSON strings and exactly equal the corresponding frozen query row;
2. `selected_edge_count`, `planned_insert_count`, `feasible`, `ordered_rank`, and `trigger_u1` obey strict JSON-integer rules with bool excluded;
3. non-negative counts, `feasible/trigger_u1 in {0,1}`, and positive feasible `ordered_rank`;
4. finite non-bool JSON numbers for margins and feasible ECDF/score fields;
5. exact feasible/infeasible nullability, including null derived fields and `ordered_rank` for infeasible rows;
6. native non-empty string elements in dense, q25, final, q25-inserted, and final-inserted ranking arrays.

Existing independent score, allocation, effective-K, membership, protected-prefix, insert derivation, final-selector, Gold-isolation, and artifact-commit checks remain in place.

## Required failure injections

Seven new targeted tests reject:

- decision `sample_id` drift;
- ranking `dataset` drift;
- float `planned_insert_count`;
- boolean `trigger_u1`;
- numeric ranking unit ID;
- non-null score on an infeasible row;
- boolean feasible `ordered_rank`.

Every test also confirms the configured `VERIFIED_PRE_GOLD` output remains absent.

Targeted result:

```text
18/18 passed in 6.549 seconds
```

Single complete-suite result on final implementation bytes:

```text
277/277 passed in 14.954 seconds
```

No second complete-suite run was performed.

## Rebinding

Config commit `fba85c990efb0e3009a4c9fb0ca486ba1485c1f9` is the direct child of the corrected implementation commit. It changes only:

- `implementation.code_commit` to `8ab5e193d00733e0ae617b2c17f02da4ce01594f`;
- the independent verifier SHA-256 to `920F0EAD0A270581826646B48A54E508F4E8BEB8FB02F3C5D1B902399CE15A91`.

Corrected config SHA-256:

```text
8481D856F27D422B81CFBFDC57C59FD3F8A8E7C0C85A01DC6DD3D0F05F57DDB1
```

Schema, code-commit, seven-file Git-blob, tracked config/protocol/evaluator bindings all passed. Evaluator SHA, scientific protocol, data/cache identities, retrieval/q25/U1/budget/ranking/statistical parameters, and all output paths remain unchanged.

## Locked boundary

No official preflight, official input/cache, official runner/verifier, historical official ranking, Gold, reservation, or Stage3B path was opened. All six future output paths remain absent.

Current state:

```text
LEVEL_B_STRICT_ROW_CONTRACT_CORRECTION_SUBMITTED_AWAITING_FOLLOWUP_REVIEW
OFFICIAL_EXECUTION_NOT_AUTHORIZED
GOLD_EVALUATION_NOT_AUTHORIZED
RESERVATION_NOT_AUTHORIZED
```
