# Stage4B-U1-D Pre-Gold Amendment 5D-B Official Decisions-Only Diagnostic Approval Request

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-14
- Request ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_5D_B_SINGLE_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_B_MANIFEST.json`
- Current state: `AMENDMENT_5D_A_SYNTHETICALLY_VERIFIED`
- Hard Failure 4 diagnosis: `INCOMPLETE`
- Official capture retry: `NOT_APPROVED`
- Controller rerun: `NOT_APPROVED`
- Verifier: `NOT_APPROVED`
- Gold: `NOT_APPROVED`
- Other project conversations, thread tools, and global memory used: No

## Binding Commits And Evidence

```text
Amendment 5D-A implementation and evidence:
02f46447e4cd69a15d2af14ee1fc62f9eb4f8bb9

Amendment 5D-A package:
33ce115f78840956fcc7bda0c3f4e172579350e7

Amendment 5D-A approval governance:
7f879a628fc313e24e805d9bdc5a81b06c37304a

Amendment 5C-B final diagnostic and audit:
e5f28f664449c02b12a129aaa2a011bad84dab91

Amendment 5C-B package:
e5a6c5479dbd125ebb58b95e9594fadde6b6719d

Amendment 5C-B approval governance:
fce67da87d155b1026cbe0670f606201ede0ac4b

Amendment 5C-B rebinding and governance:
b09668f47cd31df2be73446cadacf84d996418f9

Hard Failure 5:
deccd203059d05dc27ba80aca1ddb1e2ea8f616f

Amendment 5B v2 package:
f43e22ef079701139d4437849be8ad57654f80d7

Amendment 5B v2 approval governance:
2ddf6e044c27e47385a558bdaca80cb6c31c4ffe

Amendment 5B v2 rebinding and governance:
4c10ad942a75af42b910b860fd4897b672160d5d

Hard Failure 4:
b21852a174b537c90a848699deb4d26d6f169506

Failed controller execution HEAD:
8e0bab13ad20c06795dffd5ca71f167a814cdfb0

v2.3.1 implementation:
34349c70ee24b8240fd169393134d4280968b790
```

The final 5D-A evidence is 29,643 bytes with SHA-256 `08695B4305D9919049DFE86870772B9E9F66751DA6D2FF4D43CEF2A912A62008`. It records 143/143 tests, zero failures/errors/skips/official-path accesses, and byte-identical complete reruns. The implementation audit is 7,959 bytes with SHA-256 `D5468E8D57C0E52361D52B0EB7BF54C87DA91D453A2FACBE2AEA57F766CE3794`.

Any approval must explicitly bind the commit containing this request and Manifest. Approval of an earlier 5B package, or approval that omits the future 5D-B package commit, cannot authorize any command.

## Scientific Purpose

Hard Failure 5 has been explained: the v2.2 reference decisions contain two legal row schemas that differ only by nullable controller fields, while comparator v1 rejected any file-level schema heterogeneity before pairwise comparison. Amendment 5D-A removed only that file-level rejection and verified comparator v2 synthetically.

Hard Failure 4 remains unclassified because the prior temporary v2.3.1 decisions were deleted before a comparison completed. This request asks for one tightly bounded regeneration of temporary decisions and one aggregate comparison against the frozen v2.2 reference decisions. The purpose is only to classify the byte difference as serialization, row/query ordering, schema/type, discrete, finite-float/ULP, or decision-semantic difference.

Raw byte equality remains the controlling frozen gate. Canonical or semantic equality may explain a difference but may not replace, relax, or redefine byte equality.

## Package Has No Execution Authority

This request and Manifest are governance material only. Until an independent decision explicitly binds their package commit:

- the old 5B v2 authorization is consumed and cannot be reused;
- the CLI token string remains inert;
- no official path may be opened;
- no preflight or capture may run.

## Requested Ordered Authorization

Request approval for exactly this sequence:

1. Create and push a 5D-B approval decision and final approved `AGENTS.md`, explicitly binding this package commit and the implementation/evidence commit above.
2. On those final governance bytes, run the complete 143-test 5D-A synthetic suite twice. Both runs must pass 143/143 with zero failure/error/skip/official-path access and byte-identical complete evidence. Any failure stops without retry.
3. Create and push a governance-binding JSON and narrative audit that hash this request, this Manifest, the approval decision, final `AGENTS.md`, the 5D-A implementation/evidence, and the post-approval rebinding evidence.
4. Run one read-only formal preflight. It may only perform the registered Git, path-metadata, byte-hash, frozen-boundary, implementation, and output-absence checks. Any failure stops without capture or retry.
5. If and only if preflight passes every gate, run the exact official decisions-only capture command once.
6. Independently confirm temporary cleanup; all five permitted inputs' post-run fingerprints; aggregate-only machine output; and continued absence of formal decisions, rankings, policy, controller audit, and `VERIFIED_PRE_GOLD`.
7. Write one 5D-B narrative audit, commit and push the machine/narrative audits, verify `origin/main`, and stop immediately.

## Frozen Official Read Boundary

After all approval, rebinding, governance-binding, and preflight gates pass, only these five files may be read:

| Input | Exact path | Expected fingerprint |
|---|---|---|
| v2.3.1 unlabeled units | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_units.jsonl` | SHA-256 `114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA` |
| v2.3.1 unlabeled queries | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_queries.jsonl` | SHA-256 `6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B` |
| v2.3.1 controller channel audit | `E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_v2_3_1_controller_channel_audit.json` | SHA-256 `D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA` |
| existing ID-bound embedding cache | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_minilm_idbound_embeddings.npz` | SHA-256 `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D`; 210,714,667 bytes |
| frozen v2.2 reference decisions | `E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_decisions.jsonl` | SHA-256 `6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7` |

The Stage4A-R2 source-audit file must remain unopened; only its already registered digest may be validated from the frozen channel audit. The 5C-B machine schema inventory is also outside the read boundary and must not be used as a fixture or comparison input.

Official rankings, reference policy, evaluator files/Gold, reservation, and Stage3B remain prohibited.

## Frozen Boundary And Implementation

- dataset: `2wikimultihopqa`
- queries: 4,500
- units: 143,820
- sample-ID SHA-256: `6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2`
- runtime query-ID SHA-256: `8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6`
- namespace relation: `query_id == dataset::sample_id`
- registered source-audit SHA-256: `1496FF0CE08093AD38258FD5049068D6C4ED74FCEBF63E94E6E486F3478C7AEE`
- controller checkpoint: `stage4b_u1_v2_3_1`
- comparator checkpoint: `stage4b_u1_decisions_diag_v2`
- model: `sentence-transformers/all-MiniLM-L6-v2`
- max length: 192
- batch size: 64

The capture implementation must remain SHA-256 `7C7B159911384B436FDCC1B20D26F2F545F2DC55EAD1F7B2B134B273110ED40A`. Comparator v2 must remain SHA-256 `42FA3F74679672B0595CC76B519D59C03CB193415DD03F56E37260A961D94014`. All implementation hashes are registered in the Manifest.

## Authorization Token Semantics

The unchanged capture implementation contains this token string:

```text
APPROVE_STAGE4B_U1_D_AMENDMENT_5B_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC
```

The string is only an implementation gate. The authorization granted under Amendment 5B v2 was consumed by the failed one-shot capture and cannot authorize 5D-B. This request asks a future package-bound 5D-B decision to reactivate that unchanged gate for one exact invocation only. It does not request a source change or a second invocation.

## Exact Official Command

```powershell
python scripts\stage4b_u1_capture_diagnostic_decisions.py `
  --units "E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_units.jsonl" `
  --queries "E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_queries.jsonl" `
  --channel-audit "E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_v2_3_1_controller_channel_audit.json" `
  --embedding-cache "E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_minilm_idbound_embeddings.npz" `
  --reference-decisions "E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_decisions.jsonl" `
  --audit-output "E:\科研\HyperGranular-RAG\results\stage4b_u1_d_pregold_amendment_5b_official_decisions_diagnostic.json" `
  --temp-parent "C:\Users\cc\AppData\Local\Temp" `
  --model-name "sentence-transformers/all-MiniLM-L6-v2" `
  --batch-size 64 `
  --max-length 192 `
  --expected-units-sha256 114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA `
  --expected-queries-sha256 6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B `
  --expected-channel-audit-sha256 D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA `
  --expected-embedding-cache-sha256 69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D `
  --official-authorization-token APPROVE_STAGE4B_U1_D_AMENDMENT_5B_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC
```

No argument may be added, omitted, renamed, reordered semantically, or changed.

The machine output retains the historical `amendment_5b` filename because the frozen capture implementation enforces that exact path. Hard Failure 5 created no machine output at that path. Preflight must require it to be absent; if present, execution stops. This package does not authorize overwriting or renaming it.

## Required Post-Approval Synthetic Rebinding

Before preflight, the complete suite must run twice with:

```powershell
python scripts\stage4b_u1_run_decisions_diagnostic_synthetic_verification.py `
  --output results\stage4b_u1_d_pregold_amendment_5d_b_synthetic_rebinding.json
```

The two complete evidence byte streams must be identical and each must report 143 tests, zero failures/errors/skips, zero official-path accesses, comparator checkpoint `stage4b_u1_decisions_diag_v2`, no official capture/comparator/controller/verifier/evaluator/Gold/reservation/Stage3B access, and unchanged implementation hashes. The governance-binding JSON separately binds the 5D-B request, Manifest, approval decision, final `AGENTS.md`, 5D-A implementation/evidence, and final rebinding evidence.

The 5D-A evidence records pre-package `AGENTS.md` SHA-256 `2C5D369AB0FA72AF884A787E985EEEE3230C87938DDD3079253E24811060480B` as historical provenance. A future 5D-B approval may update `AGENTS.md`; that expected governance change must be captured by the two post-approval evidence outputs and the governance-binding JSON. It is not an implementation-hash drift and must not be resolved by rewriting the 5D-A evidence.

## Required Single Preflight

The only read-only preflight must confirm:

- clean `HEAD` equals synchronized `origin/main` and contains this package, 5D-A implementation/evidence, approval governance, rebinding evidence, and governance binding as ancestors;
- all registered frozen implementation files match the Manifest; post-approval evidence and governance binding record the final approved `AGENTS.md` hash separately;
- the five permitted inputs are regular non-symlink files and match every frozen path/SHA/byte gate;
- the channel audit still binds 4,500 queries, 143,820 units, dual ID digests, namespace relation, registered source digest, controller checkpoint, model, max length, and batch size;
- the Stage4A-R2 source-audit file and 5C-B machine inventory are not opened;
- machine and narrative 5D-B outputs are absent before capture;
- the five formal v2.3.1 outputs remain absent;
- OS temp parent is exactly `C:\Users\cc\AppData\Local\Temp`;
- no ranking, policy, evaluator/Gold, reservation, or Stage3B path is supplied.

Any failure must be recorded as a new hard-failure audit and execution must stop without capture or retry.

## Diagnostic Output Boundary

The machine audit may contain only:

- raw file bytes, sizes, SHA-256 values, and terminal-newline flags;
- canonical digests and canonical-difference counts;
- row counts and query-ID set/order difference counts;
- field-set, field-order, schema-type, and nested-schema difference counts;
- discrete-field difference counts;
- finite-float comparison counts, maximum absolute error, maximum binary64 ULP, and signed-zero counts;
- `planned_insert_count`, `ordered_rank`, `trigger_u1`, and other registered decision-semantic difference counts;
- pre/post channel/cache/reference fingerprints and temporary-cleanup booleans;
- at most one salted query-ID hash.

It must not contain raw query IDs, raw decision rows, field values, questions/text, rankings, policy, source-audit content, Gold, or U1-D effect metrics. A `null` versus integer/float mismatch must remain an explicit type/discrete/semantic difference where applicable; no filling, coercion, or normalization is allowed.

## Explicitly Not Requested

This request does not authorize:

- any command before a future 5D-B package-bound approval;
- more than one preflight or one exact official capture;
- reading, comparing, or hashing official rankings or reference policy;
- reading the Stage4A-R2 source-audit file or 5C-B machine inventory;
- running the full controller, verifier, evaluator, reservation, or Stage3B;
- generating or promoting formal decisions, rankings, policy, controller audit, or `VERIFIED_PRE_GOLD`;
- modifying code, data, model, parameters, effective-K, q25, score, ECDF, budget, trigger, ranking, endpoint, stop rule, comparator semantics, or byte-equivalence;
- creating, rebuilding, overwriting, deleting, or migrating any cache or historical artifact;
- reading or interpreting Gold or any U1-D effect metric;
- retrying after any rebinding, preflight, capture, cleanup, commit, or push failure;
- automatically resuming pre-Gold execution after diagnosis.

## Mandatory Stop

After a successful aggregate audit is pushed, execution must stop in this state:

```text
AMENDMENT_5D_B_OFFICIAL_DECISIONS_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW
HARD_FAILURE_4_DIAGNOSIS_COMPLETE_AWAITING_REVIEW
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

If any authorized gate fails, execution must stop at a newly recorded hard failure. The package itself leaves the current state as:

```text
AMENDMENT_5D_A_SYNTHETICALLY_VERIFIED
AMENDMENT_5D_B_AWAITING_APPROVAL
OFFICIAL_CAPTURE_RETRY_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
