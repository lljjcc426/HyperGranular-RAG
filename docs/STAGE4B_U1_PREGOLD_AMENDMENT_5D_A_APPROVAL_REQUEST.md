# Stage4B-U1-D Pre-Gold Amendment 5D-A Approval Request

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-14
- Request ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_5D_A_HETEROGENEOUS_SCHEMA_COMPARATOR_IMPLEMENTATION_SYNTHETIC_ONLY`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_A_MANIFEST.json`
- Current state: `AMENDMENT_5C_B_REVIEW_ACCEPTED`
- Package state: `AWAITING_AMENDMENT_5D_A_APPROVAL`
- Other project conversations, thread tools, and global memory used: No

## Binding History

```text
Amendment 5C-B final diagnostic/audit:
e5f28f664449c02b12a129aaa2a011bad84dab91

Amendment 5C-B package:
e5a6c5479dbd125ebb58b95e9594fadde6b6719d

Amendment 5C-B approval governance:
fce67da87d155b1026cbe0670f606201ede0ac4b

Amendment 5C-B rebinding/governance:
b09668f47cd31df2be73446cadacf84d996418f9

Amendment 5C-A implementation/evidence:
492a59b2f4daccd3e123f2b6cc49cd896d5009d1

Hard Failure 5:
deccd203059d05dc27ba80aca1ddb1e2ea8f616f

Amendment 5B v2 package:
f43e22ef079701139d4437849be8ad57654f80d7

Amendment 5B v2 approval governance:
2ddf6e044c27e47385a558bdaca80cb6c31c4ffe

Amendment 5B v2 rebinding/governance:
4c10ad942a75af42b910b860fd4897b672160d5d

Hard Failure 4:
b21852a174b537c90a848699deb4d26d6f169506

Failed controller execution HEAD:
8e0bab13ad20c06795dffd5ca71f167a814cdfb0

v2.3.1 implementation:
34349c70ee24b8240fd169393134d4280968b790
```

Any approval must bind the commit containing this request and Manifest. An approval that omits the future 5D-A package commit is invalid.

## Evidence Basis

5C-B independently established that the frozen v2.2 reference decisions contain two legal row schemas differing only by eight numeric-or-null type positions. The nullable schema begins at physical line 2, exactly matching Hard Failure 5. The 5C-B review therefore confirms the direct failure cause but leaves Hard Failure 4 unclassified because no new temporary decisions were generated or compared.

Current comparator inspection confirms that the only pre-comparison blocker is its file-level `file_schema` homogeneity requirement. Its later per-query field-set, field-order, schema-type, discrete, finite-float/ULP and semantic comparison layers already exist.

## Requested Authorization

Approval is requested only to modify:

```text
scripts/stage4b_u1_compare_decisions.py
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
tests/test_stage4b_u1_decisions_diagnostic.py
```

The implementation may make only these semantic changes:

1. Update comparator schema/checkpoint identifiers to `stage4b_u1_decisions_diagnostic_v2` and `stage4b_u1_decisions_diag_v2`.
2. Remove the loader's requirement that every row within one decisions JSONL file have an identical complete JSON type signature.
3. Continue validating every row independently as a strict JSON object with no duplicate key or non-finite value and with one unique, non-empty string `query_id`.
4. Preserve per-query comparison of field set, field order, recursive type/structure, canonical bytes, discrete values, binary64 exact bits/absolute error/ULP, and the three semantic fields.
5. Treat `null <-> integer` and `null <-> finite float` as explicit per-query schema-type and discrete-value differences. `ordered_rank` differences must also remain semantic differences.
6. Never fill, coerce, impute, cast, normalize, or otherwise convert `null` to a numeric value.
7. Keep raw file byte equality as the primary controlling equivalence gate. Canonical or semantic equality remains diagnostic only and cannot replace raw equality.
8. Preserve the existing aggregate output keys and no-raw-ID/no-row boundary, apart from the frozen schema/checkpoint version updates.

No capture, controller, retrieval, evaluator, verifier, official-data, model, parameter, cache, ranking, policy or endpoint change is requested.

## Synthetic Verification Plan

The accepted 5C-B baseline contains 131 Stage4B-U1 tests. This is the traceable starting count. At least 12 new heterogeneous-schema comparator tests are required, so the complete suite must contain at least 143 tests.

The new tests must actively cover:

- legal nullable heterogeneity within the left file;
- legal nullable heterogeneity within the right file;
- legal heterogeneity in both files with the same per-query types;
- `null <-> integer` schema/discrete classification;
- `null <-> finite float` schema/discrete classification;
- `null` exclusion from finite-float absolute-error and ULP aggregation;
- `ordered_rank null <-> integer` semantic classification;
- continued field-set difference reporting under heterogeneous files;
- continued field-order difference reporting under heterogeneous files;
- continued nested type/structure reporting under heterogeneous files;
- strict rejection of invalid JSON, duplicate keys, non-finite values, missing/duplicate query IDs and unsupported values;
- raw-byte gate preservation, no normalization, no raw-ID/row leakage and active official-path blocking.

The updated deterministic runner must bind this request, its Manifest, the future package-bound approval decision, the 5C-B review/audit, final `AGENTS.md`, all three allowed implementation/test files and all frozen files registered in the Manifest.

After implementation and preliminary synthetic checks, the final complete suite must run twice on identical tracked bytes. Both runs must satisfy:

```text
tests >= 143
failures = 0
errors = 0
skipped = 0
official-path access attempts = 0
complete evidence byte-identical = true
```

The implementation audit must record every file hash, all commands including failed commands, the exact comparator diff and proof that no non-approved file changed.

## Completion Boundary

After two final deterministic runs, approval would permit only:

- a 5D-A implementation audit;
- deterministic synthetic evidence;
- one implementation/evidence commit and push;
- an implementation-bound 5D-B official decisions-only diagnostic request and Manifest;
- necessary README/ROADMAP/REPRODUCIBILITY/AGENTS status synchronization.

After the 5D-B package is pushed, execution must stop for independent approval.

## Explicitly Not Requested

This request does not authorize:

- opening any official units, queries, channel audit, source audit, cache, decisions, rankings, policy, evaluator or Gold file;
- reading the 5C-B machine inventory as implementation input or fixture data;
- running official comparator/capture, controller, verifier or evaluator;
- generating official or temporary decisions;
- modifying capture, controller, retrieval, common, channel preparation, verifier, evaluator, inventory implementation or any non-registered test;
- schema normalization, nullable imputation, type coercion or byte-equivalence relaxation;
- model, `max_length`, batch size, effective-K, q25, score, ECDF, budget, trigger, ranking, endpoint or stop-rule changes;
- creating, rebuilding, overwriting, migrating or deleting cache, official artifacts, historical evidence or failure records;
- reading or interpreting U1-D effects, reservation or Stage3B;
- automatically creating or running 5D-B official execution after synthetic verification.

## Requested Completion State

```text
AMENDMENT_5D_A_SYNTHETICALLY_VERIFIED
HARD_FAILURE_5_DIRECT_CAUSE_CONFIRMED
HARD_FAILURE_4_DIAGNOSIS_STILL_INCOMPLETE

OFFICIAL_CAPTURE_RETRY_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

