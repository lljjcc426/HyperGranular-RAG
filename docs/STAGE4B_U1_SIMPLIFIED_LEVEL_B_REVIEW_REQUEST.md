# Stage4B-U1-D Simplified Level B Review Request

## Material Passport

- ID: `HGRAG-STAGE4B-U1-LEVEL-B-REVIEW-20260718`
- Type: implementation-integrity and synthetic-equivalence review
- Status: `AWAITING_INDEPENDENT_LEVEL_B_REVIEW`
- Scientific protocol: `docs/STAGE4B_U1_SIMPLIFIED_EXECUTION_PROTOCOL_V1.md`
- Accepted Level A correction commit: `e8dd4885dac6198f37261a6955dc62daf821dc57`
- Implementation commit: `2dade07843194635f814ef53d0880f0ea7207451`
- Config commit: `47a189f3e092aee616dbf13ed397230b8ccb8371`
- Evidence/status commit before this request: `78766994ee4985ea0b733f96e3713854b81705a9`
- Official execution authorization: absent
- Gold evaluation authorization: absent
- Reservation authorization: absent

## Requested decision

Please return one primary verdict:

```text
ACCEPT_LEVEL_B_IMPLEMENTATION
```

or:

```text
RETURN_FOR_MINIMAL_LEVEL_B_CORRECTION
```

If returning the implementation, identify the exact code/config integrity defect and whether it can affect data identity, Gold isolation, ranking, output integrity, or reproducibility. Ordinary command presentation, remote visibility, terminal framing, and wrapper behavior are Level C unless they cause one of those effects.

Acceptance confirms only implementation integrity and synthetic semantic equivalence. It does not authorize official preflight, official controller execution, Gold evaluation, reservation access, or scientific efficacy claims.

## Review scope

The implementation commit adds exactly four files and deletes none:

- `scripts/stage4b_u1_simplified_preflight.py`
- `scripts/stage4b_u1_simplified_runner.py`
- `scripts/stage4b_u1_independent_verifier.py`
- `tests/test_stage4b_u1_simplified.py`

The separate config commit adds exactly:

- `configs/stage4b_u1_d_official.json`

The config SHA-256 is:

```text
56F7A177C428BCDA783F1B1B33706B9ED2C0A6A88F08BAE3D7347BA3DA377D21
```

Its direct parent is the implementation commit. `implementation.code_commit` binds that same full commit and seven exact implementation files.

The following protocol-pinned algorithm files were not modified and retain their recorded SHA-256 values:

| File | SHA-256 |
|---|---|
| `scripts/stage4b_u1_common.py` | `CDF7EAD6007DABE389ED0BD18983496F75290C32243FE6DF84716810CDE92CE4` |
| `scripts/stage4b_u1_goldfree_retrieval.py` | `3B50FAFD057E2565167ED09288D61829B3FBD044991F139F734F819955038A3B` |
| `scripts/stage4b_u1_goldfree_controller.py` | `C18AD3B672649BA846C5E191D0DBBAC7644A926D4B8CCD39176127175BBA7C1F` |
| `scripts/stage4b_u1_verify.py` | `DC134B51A07C14A553746C303EA31D83990BA0EFAD30EFC3A1722F1A141E66EC` |

## Integrity questions

The independent review should determine whether:

1. strict config parsing rejects duplicate keys, non-finite constants, placeholders, unknown fields, wrong fixed values, and any evaluation authorization;
2. code, protocol, evaluator, config, input, cache, and output paths are bound as frozen;
3. formal cache handling is require-existing only and has no model download, rebuild, or write path;
4. the runner uses the frozen retrieval, ECDF, score, ordered-prefix allocation, effective-K, and ranking functions without invoking the evaluator;
5. pending decisions/rankings/policy are validated and promoted as a guarded group with rollback on partial failure or post-computation cache drift;
6. the verifier does not call the runner and independently reconstructs candidate membership, score, allocation, effective-K, protected prefix, inserted IDs, and final selection;
7. the verifier accepts only an exact committed decisions/rankings/policy artifact set before writing `VERIFIED_PRE_GOLD`;
8. config, runner, policy, and pre-Gold outputs remain Gold-free and evaluator authorization remains false;
9. the retained legacy policy and `VERIFIED_PRE_GOLD` fields remain compatible with the corrected evaluator;
10. no Level B change modifies data, candidate generation, grain-ball or hyperedge logic, q25, U1 inputs/formula, budget, ranking, endpoint, or statistics.

## Synthetic evidence

Targeted Level B command:

```powershell
& 'D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe' -I -B -m unittest discover -s tests -p 'test_stage4b_u1_simplified.py' -v
```

Result: 11/11 passed.

Complete Stage4B-U1 command on final implementation bytes:

```powershell
& 'D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe' -I -B -m unittest discover -s tests -p 'test_stage4b_u1*.py'
```

Result: 270/270 passed in 12.196 seconds.

The end-to-end synthetic fixture produced field-wise identical decisions and rankings from the simplified runner and the frozen algorithm route. Failure tests cover duplicate/non-finite config, implementation drift, missing cache, pre-existing outputs, partial promotion, candidate membership, final selector, and config/policy binding.

Post-config checks confirmed strict schema validity, current-file SHA values, implementation Git blobs at the bound code commit, tracked config/protocol/evaluator identities, and zero registered future outputs. These checks did not call the official preflight.

## Locked boundary

No official preflight, official runner, official verifier, historical official ranking, Gold, reservation, or Stage3B action was performed during implementation or review-package preparation. The six registered future output paths remain absent.

After an `ACCEPT_LEVEL_B_IMPLEMENTATION` verdict, a separate explicit authorization must still bind the accepted implementation/config and permit the first official input/cache read. Until then the state remains:

```text
LEVEL_B_REVIEW_REQUEST_SUBMITTED_AWAITING_INDEPENDENT_REVIEW
OFFICIAL_EXECUTION_NOT_YET_AUTHORIZED
GOLD_EVALUATION_NOT_AUTHORIZED
RESERVATION_NOT_AUTHORIZED
```
