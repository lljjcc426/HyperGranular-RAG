# Stage4B-U1-D Pre-Gold Amendment 5C-A Approval Request

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-14
- Request ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_5C_A_REFERENCE_SCHEMA_INVENTORY`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_MANIFEST.json`
- Review record: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_5_REVIEW_1.md`
- Current official state: `AMENDMENT_5B_V2_OFFICIAL_DIAGNOSTIC_STOPPED_HARD_FAILURE_5`
- Package state: `AWAITING_AMENDMENT_5C_A_APPROVAL`
- Other project conversations, thread tools, and global memory used: No

## Binding History

```text
Hard Failure 5 audit/status:
deccd203059d05dc27ba80aca1ddb1e2ea8f616f

Amendment 5B v2 rebinding/governance evidence:
4c10ad942a75af42b910b860fd4897b672160d5d

Amendment 5B v2 approval governance:
2ddf6e044c27e47385a558bdaca80cb6c31c4ffe

Amendment 5B v2 package:
f43e22ef079701139d4437849be8ad57654f80d7

Amendment 5A.1 implementation/evidence:
e566eb861ec6028ca89a40c9aca7d06737f1eb8e

Hard Failure 4:
b21852a174b537c90a848699deb4d26d6f169506

Failed controller execution HEAD:
8e0bab13ad20c06795dffd5ca71f167a814cdfb0

v2.3.1 implementation:
34349c70ee24b8240fd169393134d4280968b790
```

Any approval must also bind the commit containing this request, its Manifest, the Hard Failure 5 review record, and the corresponding final `AGENTS.md`. An approval that does not bind that package commit is invalid.

## Reason For Amendment

The single approved 5B v2 capture stopped before comparison because the strict decisions comparator rejected within-file schema heterogeneity at line 2 of the frozen v2.2 reference decisions. The failure record does not reveal the differing fields or types, and the approved capture count is exhausted.

An isolated schema-inventory tool is required before any scientifically defensible proposal can be made about comparator behavior. Amendment 5C-A requests implementation and synthetic verification only. It does not request access to the frozen reference file or any other official input.

## Requested Authorization

Approval is requested only for the following implementation and synthetic-verification work:

1. Add an independent read-only JSONL schema-inventory tool at `scripts/stage4b_u1_inventory_decision_schemas.py`.
2. Add a deterministic complete-suite runner at `scripts/stage4b_u1_run_schema_inventory_synthetic_verification.py` and isolated tests at `tests/test_stage4b_u1_decision_schema_inventory.py`.
3. Parse each non-empty JSONL line as a JSON object with duplicate-key detection at every nesting level. Reject blank lines, invalid JSON, non-object rows, duplicate keys, `NaN`, `Infinity`, `-Infinity`, and any other non-finite number.
4. Inventory schema only. The implementation must never copy field values, raw rows, query IDs, salted query-ID hashes, question/text, or float values into its output.
5. Distinguish JSON `null`, `bool`, `integer`, finite `number`, `string`, `array`, and `object`. Nested objects and array element schemas must be represented recursively without retaining values. An array schema is the sorted set of distinct recursive element-schema signatures, with a separate empty-array marker; element values, element order, multiplicity, and array length are excluded.
6. Produce deterministic ordered and order-insensitive structural signatures so field-set/type/nesting differences remain separate from field-order-only differences. Signature source bytes must be UTF-8 JSON with `ensure_ascii=true`, `sort_keys=true`, compact separators, and non-finite values disabled; the digest is SHA-256 over those bytes.
7. Select the main schema by highest row count over ordered schema signatures; ties must be resolved by the lexicographically smallest ordered signature. Added, removed, type-changed, nesting-changed, and order-only differences must be derived relative to that frozen main schema.
8. Keep `scripts/stage4b_u1_compare_decisions.py`, the existing diagnostic capture, controller, retrieval, common module, existing diagnostic runner/tests, raw byte-equivalence gate, and all model/retrieval/controller parameters unchanged.
9. Retain the existing 107 Stage4B-U1 synthetic tests. Add at least 12 isolated inventory tests, giving a complete-suite minimum of 119 tests. The lower bound is the nine review-required parser/schema categories plus three cross-cutting gates for no-value leakage, official-path interception, and deterministic cleanup/output; it is derived from this Amendment's coverage, not from another project or session.
10. Run the complete suite twice on unchanged tracked bytes. Both runs must pass all tests with zero failures, errors, skips, or official-path access attempts and produce byte-identical complete evidence.
11. Produce an implementation audit with complete SHA-256 values, commit and push implementation/evidence, assemble an implementation-bound Amendment 5C-B request and Manifest, push them, and stop.

## Allowed Files

Implementation authority, if approved, is limited to:

- `scripts/stage4b_u1_inventory_decision_schemas.py`;
- `scripts/stage4b_u1_run_schema_inventory_synthetic_verification.py`;
- `tests/test_stage4b_u1_decision_schema_inventory.py`;
- `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_APPROVAL_DECISION.md`;
- `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_IMPLEMENTATION_AUDIT.md`;
- `results/stage4b_u1_d_pregold_amendment_5c_a_synthetic_verification.json`;
- the future 5C-B request and Manifest;
- `AGENTS.md`, `README.md`, `docs/ROADMAP.md`, and `docs/REPRODUCIBILITY.md` for exact state synchronization.

No existing implementation, test, official artifact, prior evidence, or failure record may be modified or deleted.

## Synthetic Hard Gates

Synthetic fixtures and access interception must actively prove:

- a homogeneous flat schema produces one deterministic signature;
- field-set additions/removals are distinguished;
- field-order-only differences are distinguished without becoming value differences;
- `bool`, `integer`, and finite `number` remain distinct;
- nested object and array element-structure differences are detected recursively;
- duplicate keys at top level or nested level fail closed;
- invalid JSON and blank/non-object rows fail closed;
- `NaN`, `Infinity`, and `-Infinity` fail closed;
- output contains schema metadata only and leaks no fixture values or IDs;
- deterministic main-schema selection and tie-breaking are stable;
- temporary synthetic inputs/outputs are cleaned after success and injected failure;
- every official project/data path is blocked and unopened;
- the comparator, official capture, controller, rankings, policy, verifier, evaluator, Gold, reservation, and Stage3B are not invoked.

Synthetic fixtures must use temporary synthetic paths and content only. Official reference decisions, units, queries, channel audit, source audit, caches, rankings, policies, evaluator files, and Gold must not be opened, copied, sampled, or used as fixtures.

## Frozen Future 5C-B Boundary

The 5C-A implementation may prepare a fail-closed code path for a later exact-file scan, but that path remains inert without a separate package-bound 5C-B approval. The only file a future 5C-B package may request to read is:

```text
E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_decisions.jsonl
SHA-256: 6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7
```

The future scan must verify the file as a regular non-symlink and match its SHA-256 before parsing, recheck SHA-256 immediately before exclusive-create audit output, and stop on any mismatch without output or retry.

Allowed future 5C-B output is limited to total row count; distinct schema-signature count; per-signature row count and first/last line number; field-name sets, field order, and JSON type/nesting signatures; differences relative to the deterministic main schema; and pre/post reference SHA equality. It must contain no raw or salted query ID, row, field value, float value, question/text, ranking, policy, Gold, or generated decision.

## Explicitly Not Authorized

This request does not authorize:

- reading official reference decisions or any official units, queries, channel audit, source audit, cache, ranking, policy, evaluator, or Gold file;
- running an official schema inventory, comparator, capture, controller, verifier, evaluator, reservation, or Stage3B command;
- modifying `scripts/stage4b_u1_compare_decisions.py`, `scripts/stage4b_u1_capture_diagnostic_decisions.py`, the controller, retrieval, common module, or existing synthetic tests/runners;
- changing schema acceptance or normalization in the comparator or capture;
- changing or relaxing raw byte equivalence;
- generating decisions, rankings, policy, diagnostic audit, controller audit, or `VERIFIED_PRE_GOLD`;
- changing data, model, `max_length`, batch size, effective-K, q25, score, ECDF, budget, trigger, ranking, endpoint, or stop rule;
- creating, rebuilding, overwriting, deleting, or migrating any cache, official artifact, evidence, or failure record;
- reading U1-D effect metrics or accessing reservation or Stage3B;
- retrying the consumed 5B v2 capture or automatically resuming Hard Failure 5.

## Requested Completion State

After approved implementation, deterministic synthetic evidence, audit, and an implementation-bound 5C-B package are pushed, execution must stop in this state:

```text
AMENDMENT_5C_A_SYNTHETICALLY_VERIFIED
OFFICIAL_SCHEMA_SCAN_NOT_APPROVED
COMPARATOR_CHANGE_NOT_APPROVED
OFFICIAL_CAPTURE_RETRY_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

The current package itself authorizes none of the implementation, test, or official-access actions above. Until a new approval explicitly binds the package commit, the state remains `AMENDMENT_5C_A_AWAITING_APPROVAL`.
