# Stage4B-U1-D Pre-Gold Amendment 5A.1 Approval Request

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-14
- Request ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_5A_1_CHANNEL_INPUT_HASH_BINDING`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_1_MANIFEST.json`
- Review record: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_REVIEW_1.md`
- Current official state: `PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_4`
- Package state: `AWAITING_AMENDMENT_5A_1_APPROVAL`
- Other project conversations, thread tools, and global memory used: No

## Binding History

```text
Returned Amendment 5B package:
ceb755252540cf223aa18ac721443154c29cd07a

Amendment 5A final implementation and evidence:
9a060bd31e9c33be587f7ef5e64f86206922e59e

Amendment 5A package:
81d8c34f1cf2539a4c0b81c6148047bc666e2f82

Amendment 5A approval governance:
a0bf91b3a34daaf5b1ee50700d8356e1383e9a9c

Hard Failure 4:
b21852a174b537c90a848699deb4d26d6f169506

Failed controller execution HEAD:
8e0bab13ad20c06795dffd5ca71f167a814cdfb0

v2.3.1 implementation:
34349c70ee24b8240fd169393134d4280968b790
```

Any approval must also bind the commit containing this request, its Manifest, the 5B review record, and the corresponding final `AGENTS.md`. An approval that does not bind that package commit is invalid.

## Reason For Amendment

The returned 5B package did not externally freeze the SHA-256 values of the unlabeled units, unlabeled queries, and controller channel audit that would enter official diagnostic computation. Comparing units and queries only with hash values stored inside the channel audit is an internal consistency check and does not rule out coordinated three-file drift.

Amendment 5A.1 is therefore a minimal implementation/synthetic hardening request. It does not request official diagnosis or any official input read.

## Frozen Inputs For The Future Diagnostic

| Input | Exact path | Expected SHA-256 |
|---|---|---|
| v2.3.1 unlabeled units | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_units.jsonl` | `114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA` |
| v2.3.1 unlabeled queries | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_queries.jsonl` | `6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B` |
| v2.3.1 controller channel audit | `E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_v2_3_1_controller_channel_audit.json` | `D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA` |

## Requested Authorization

Approval is requested only for the following implementation and synthetic-verification work:

1. Add three required diagnostic CLI arguments: `--expected-units-sha256`, `--expected-queries-sha256`, and `--expected-channel-audit-sha256`.
2. In official capture mode, require each channel input to exist as a regular file and match its expected external SHA before semantic parsing, cache loading, or diagnostic computation. Before this gate passes, only byte reads needed to calculate the three SHA-256 values are allowed.
3. After diagnostic computation and temporary-decisions comparison/cleanup, rehash all three inputs immediately before machine-audit exclusive-create. Any mismatch must fail closed and leave no machine audit.
4. Preserve temporary-decisions cleanup on all validation and computation exceptions.
5. Keep `scripts/stage4b_u1_goldfree_controller.py`, retrieval behavior, comparator semantics, byte-equivalence, model, parameters, score, ECDF, budget, trigger, ranking, endpoint, and stop rules unchanged.
6. Retain the existing 98 synthetic tests and add at least six tests covering units drift, queries drift, channel-audit drift, computation-time channel-input drift with no audit, the valid three-hash path, and temporary cleanup on validation failure. The complete suite must contain at least 104 tests.
7. Run the complete suite twice on unchanged bytes. Both runs must pass all tests with zero failures/errors/skips, record zero official-path accesses, and produce byte-identical complete evidence.
8. Produce an implementation audit with complete SHA-256 values, commit and push the implementation/evidence, create a revised implementation-bound Amendment 5B request and Manifest, push them, and stop.

## Allowed Files

Implementation authority, if approved, is limited to:

- `scripts/stage4b_u1_capture_diagnostic_decisions.py`;
- `scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py` only as needed to bind the new implementation/governance/tests;
- `tests/test_stage4b_u1_decisions_diagnostic.py`;
- Amendment 5A.1 governance, audit, deterministic evidence, and revised 5B package files;
- `AGENTS.md`, `README.md`, `docs/ROADMAP.md`, and `docs/REPRODUCIBILITY.md` for exact state synchronization.

The controller, retrieval module, common scoring module, decisions comparator, official channel preparer, verifier, evaluator, and existing official or failure artifacts are outside the allowed edit scope.

## Synthetic Hard Gates

The new tests must actively prove:

- each wrong expected/pre-read SHA is rejected before semantic parsing or computation;
- a channel input changed during diagnostic computation is rejected before audit creation;
- no machine audit exists after either pre-gate or post-gate failure;
- temporary decisions are deleted after success and every injected failure;
- the correct three expected SHAs pass with synthetic fixtures;
- official paths remain blocked and are never opened by the synthetic suite;
- official rankings, policy builder, controller CLI, verifier, evaluator, Gold, reservation, and Stage3B are not invoked.

Synthetic fixtures must use synthetic paths and content. The three official files and their content must not be opened, copied, sampled, or used as fixtures.

## Explicitly Not Authorized

This request does not authorize:

- reading official units, queries, controller channel audit, source audit, cache, decisions, rankings, policy, evaluator files, or Gold;
- using the rejected 5B authorization token;
- running 5B preflight, official capture/comparator, controller, verifier, or evaluator;
- generating official decisions, rankings, policy, machine audit, controller audit, or `VERIFIED_PRE_GOLD`;
- changing or relaxing byte equivalence or any retrieval/controller/evaluator algorithm;
- changing data, model, `max_length`, batch size, effective-K, q25, score, ECDF, budget, trigger, ranking, endpoint, or stop rule;
- creating, rebuilding, overwriting, deleting, or migrating any cache or official/failure artifact;
- reading any U1-D effect metric or accessing reservation or Stage3B;
- automatic retry or automatic resumption of Hard Failure 4.

## Requested Completion State

After approved implementation, deterministic synthetic evidence, audit, and a revised 5B package are pushed, execution must stop in this state:

```text
AMENDMENT_5A_1_SYNTHETICALLY_VERIFIED
OFFICIAL_DIAGNOSIS_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

The current package itself authorizes none of those implementation or test actions. Until a new approval explicitly binds the package commit, the state remains `AMENDMENT_5A_1_AWAITING_APPROVAL`.
