# Stage4B-U1-D Pre-Gold Amendment 5C-B Official Schema Scan Approval Request

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-14
- Request ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_5C_B_SINGLE_REFERENCE_SCHEMA_ONLY_SCAN`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_B_MANIFEST.json`
- 5C-A implementation audit: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_IMPLEMENTATION_AUDIT.md`
- Current state: `AMENDMENT_5C_A_SYNTHETICALLY_VERIFIED`
- Package state: `AWAITING_AMENDMENT_5C_B_APPROVAL`
- Other project conversations, thread tools, and global memory used: No

## Binding History

```text
Amendment 5C-A package:
a8caa2a3b26ae13d0b149e4995e3a017e8edb2e7

Amendment 5C-A approval governance:
a680c0358ac351a5e80c9829d48a7b8e88950f4c

Amendment 5C-A implementation/evidence:
492a59b2f4daccd3e123f2b6cc49cd896d5009d1

Hard Failure 5 audit/status:
deccd203059d05dc27ba80aca1ddb1e2ea8f616f

Amendment 5B v2 rebinding/governance:
4c10ad942a75af42b910b860fd4897b672160d5d

Amendment 5B v2 approval governance:
2ddf6e044c27e47385a558bdaca80cb6c31c4ffe

Amendment 5B v2 package:
f43e22ef079701139d4437849be8ad57654f80d7

v2.3.1 implementation:
34349c70ee24b8240fd169393134d4280968b790
```

Any approval must also bind the commit containing this request, its Manifest, and the corresponding final `AGENTS.md`. An approval that does not bind that package commit is invalid.

## Verified 5C-A Implementation Boundary

The approved implementation added only the independent inventory, deterministic runner, and isolated tests. All eight approval-frozen existing implementation/test files retained their exact baseline hashes.

The final 5C-A complete suite ran twice on unchanged final governance/implementation bytes. Both runs passed 131/131, including 24 inventory tests, with zero failures, errors, skips, or official-path access attempts. Both evidence outputs were 22,234 bytes with SHA-256:

```text
0D13392B5C96BAD7EC4D67C22A7515B4A6D211C8EFBB3A4486F9BA5531A1EF7C
```

The two outputs were byte-identical. No official reference, unit, query, channel, source-audit, cache, ranking, policy, evaluator, Gold, reservation, or Stage3B path was opened.

## Requested Authorization

Approval is requested only for this sequence:

1. Write a package-bound 5C-B approval decision and final approved `AGENTS.md`, commit, and push them.
2. On those final approval-governance bytes, run the complete 131-test schema-inventory synthetic runner twice. Both runs must pass 131/131 with zero failures/errors/skips/official access and byte-identical evidence.
3. Create a governance-binding JSON over this request, the Manifest, the 5C-B approval decision, final approved `AGENTS.md`, implementation commit `492a59b2...`, original 5C-A evidence, and post-approval rebinding evidence. Commit and push the rebinding evidence, binding JSON, and narrative rebinding audit.
4. Run one read-only formal preflight. It may compute the frozen reference file SHA-256 but may not parse JSONL or inventory schemas.
5. Only if every preflight gate passes, run one exact-command semantic schema scan of the one frozen reference file.
6. Independently validate the machine audit against the registered value-free schema and source-integrity boundary; create one aggregate-only narrative audit.
7. Commit and push the machine/narrative audits, verify GitHub synchronization, and stop immediately.

Any rebinding, governance-binding, preflight, scan, validation, commit, or push failure must stop without automatic retry.

## Frozen Official Input

Only this file may be read:

```text
Path:
E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_decisions.jsonl

SHA-256:
6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7
```

The preflight may read bytes only to compute SHA-256. The single scan may perform the implementation's pre-hash, one JSONL schema parse, and post-hash immediately before exclusive-create output. No row value may be retained or emitted.

## Exact Official Command

```powershell
python scripts\stage4b_u1_inventory_decision_schemas.py `
  --input "E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_decisions.jsonl" `
  --output "E:\科研\HyperGranular-RAG\results\stage4b_u1_d_pregold_amendment_5c_b_reference_schema_inventory.json" `
  --expected-input-sha256 6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7 `
  --official-authorization-token APPROVE_STAGE4B_U1_D_AMENDMENT_5C_B_SINGLE_REFERENCE_SCHEMA_SCAN
```

No argument may be added, omitted, renamed, or changed. The token is an implementation gate, not authorization by itself. It remains inert unless a future decision explicitly approves and binds this 5C-B package commit and all prior rebinding/preflight gates pass.

## Required Formal Preflight

The one preflight must verify:

- clean `HEAD` equals synchronized `origin/main` and GitHub `main`;
- package, 5C-A implementation, 5C-B approval governance, and post-approval rebinding/binding commits are ancestors of `HEAD`;
- all 17 5C-A evidence-bound governance/implementation/test hashes match the corresponding Git blobs at implementation commit `492a59b2...`, including all eight frozen existing files; the current approved `AGENTS.md` is bound separately by the post-approval governance-binding JSON;
- the exact input path exists as a regular non-symlink file and its SHA-256 equals `6FB6...23C7`;
- the machine audit, narrative audit, post-approval rebinding output, and governance-binding paths satisfy their registered existence/absence state;
- the exact inventory CLI contains the frozen checkpoint, reference path/SHA, token, value-free schema contract, pre/post SHA gate, and exclusive-create cleanup behavior;
- no other data input, official path, output path, comparator, capture, controller, verifier, evaluator, or Gold argument is supplied.

Any mismatch must be recorded as a hard-failure audit and stop before semantic parsing. The single scan authorization must not be consumed when preflight fails.

## Machine Output Boundary

The machine audit may contain only:

- schema inventory/checkpoint/status and `value_free_schema_metadata=true`;
- total row count;
- distinct ordered and structural schema-signature counts;
- deterministic main ordered signature and selection rule;
- per-schema row count and first/last physical line number;
- ordered/structural schema signatures;
- field-name set/order and JSON type/nesting schemas;
- added, removed, type-changed, nesting-changed, and order-only field paths relative to the main schema;
- input SHA-256 before/after and equality status;
- exclusive-create and staging-cleanup booleans.

It must not contain raw query IDs, salted query-ID hashes, rows, field values, float values, question/text, rankings, policy, Gold, or newly generated decisions. Field names such as `query_id` may appear only as schema field names, never with their values.

The narrative audit may summarize only the same aggregate schema metadata and integrity gates. It must not interpret retrieval quality, U1-D effectiveness, or any decision value.

## Explicitly Not Requested

This request does not authorize:

- reading any official file other than the one frozen reference decisions file;
- reading units, queries, channel audit, source audit, cache, rankings, policy, evaluator, or Gold;
- outputting any raw/salted query ID, decision row, field value, float value, question, or text;
- generating new decisions, rankings, policy, controller audit, or `VERIFIED_PRE_GOLD`;
- calling or modifying the existing comparator or capture;
- running or retrying the full controller, verifier, evaluator, reservation, or Stage3B;
- changing schema acceptance/normalization, raw byte equivalence, data, model, parameters, effective-K, q25, score, ECDF, budget, trigger, ranking, endpoint, or stop rules;
- creating, rebuilding, overwriting, deleting, or migrating any cache, official artifact, historical evidence, or failure record;
- retrying after any hard failure;
- automatically resuming 5B capture or official pre-Gold execution after the schema scan.

## Mandatory Stop

After the machine and narrative audits are committed and pushed, execution must stop in this state:

```text
REFERENCE_DECISIONS_SCHEMA_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW
OFFICIAL_CAPTURE_RETRY_NOT_APPROVED
COMPARATOR_CHANGE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

The package itself authorizes no command. Current state remains `AMENDMENT_5C_B_AWAITING_APPROVAL` until a new decision explicitly binds the package commit.
