# Stage4B-U1-D Pre-Gold Amendment 5B v2 Official Decisions-Only Diagnostic Approval Request

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-14
- Request ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_5B_V2_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_V2_MANIFEST.json`
- Current official state: `PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_4`
- Amendment 5A.1 state: `AMENDMENT_5A_1_SYNTHETICALLY_VERIFIED`
- Official diagnosis: `NOT_APPROVED`
- Controller rerun: `NOT_APPROVED`
- Verifier: `NOT_APPROVED`
- Gold: `NOT_APPROVED`
- Other project conversations, thread tools, and global memory used: No

## Binding Commits And Evidence

```text
Amendment 5A.1 package:
3137ace0328dd24908f95737ea1dcbe0c8fe045e

Amendment 5A.1 approval governance:
d34835159fd600c8b629114946afee9e943d143c

Amendment 5A.1 implementation and evidence:
e566eb861ec6028ca89a40c9aca7d06737f1eb8e

Returned Amendment 5B package:
ceb755252540cf223aa18ac721443154c29cd07a

Hard Failure 4:
b21852a174b537c90a848699deb4d26d6f169506

Failed controller execution HEAD:
8e0bab13ad20c06795dffd5ca71f167a814cdfb0

v2.3.1 implementation:
34349c70ee24b8240fd169393134d4280968b790
```

The 5A.1 deterministic evidence is 20,495 bytes with SHA-256 `81A8A5960395F729B643A42505E7F947962B338CD97ADD0506636D3AA2020A67`. The implementation audit SHA-256 is `37819C123D45D7D5026B5A3229C1CEB3729920A048B711FE14757FF062DB6289`.

Any approval must also bind the commit containing this v2 request, its Manifest, and the corresponding `AGENTS.md`. An approval that does not bind that package commit is invalid.

## Reason For v2

The first 5B package at `ceb755...` was returned because its three channel inputs were checked only for internal consistency with the controller channel audit. Amendment 5A.1 now implements an external fail-closed binding before semantic parsing/computation and again after temporary-decisions cleanup immediately before audit creation.

The revised package preserves every other accepted diagnosis-only boundary from the returned package. It does not request a controller rerun, ranking access, equivalence relaxation, or official resumption.

## Externally Frozen Channel Inputs

| Input | Exact path | Expected SHA-256 |
|---|---|---|
| v2.3.1 unlabeled units | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_units.jsonl` | `114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA` |
| v2.3.1 unlabeled queries | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_queries.jsonl` | `6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B` |
| v2.3.1 controller channel audit | `E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_v2_3_1_controller_channel_audit.json` | `D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA` |

Before all three pass, official capture may perform only path metadata checks and byte reads needed to calculate these SHA-256 values. It may not parse JSON/JSONL, load the cache, hash reference decisions, or begin diagnostic computation.

## Requested Authorization

Request approval for this single ordered sequence:

1. Commit and push a 5B v2 approval decision and final governance state.
2. Run the complete 107-test synthetic suite twice on the approved governance bytes. Both runs must pass 107/107 with zero failure/error/skip/official access and byte-identical complete evidence.
3. Create and push a governance-binding JSON over this request, this Manifest, the approval decision, final `AGENTS.md`, implementation commit `e566eb8...`, and post-approval rebinding evidence.
4. Run one read-only exact-boundary preflight. Any failure stops without retry and prohibits capture.
5. Run the exact decisions-only capture command once.
6. Confirm the temporary decisions were deleted, the post-computation three-SHA gate passed, the machine audit is aggregate-only, and no unregistered output exists.
7. Create one narrative audit without raw query IDs/rows, commit and push both audit outputs, verify GitHub synchronization, and stop.

## Exact Official Read Boundary

Only the following five files may be read after all preflight gates pass:

- the three externally frozen channel inputs above;
- existing ID-bound embedding cache `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_minilm_idbound_embeddings.npz`, SHA-256 `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D`, 210,714,667 bytes;
- frozen v2.2 decisions `E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_decisions.jsonl`, SHA-256 `6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7`.

The Stage4A-R2 source-audit file remains unopened; only its already registered digest may be validated from the externally frozen channel audit. Official rankings, reference policy, evaluator files/Gold, reservation, and Stage3B are outside the boundary.

## Authorization Token Semantics

The capture implementation contains this CLI token string:

```text
APPROVE_STAGE4B_U1_D_AMENDMENT_5B_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC
```

The string is an implementation gate, not authorization by itself. It was not used during Amendment 5A.1 and remains inert now. Passing it is requested only if a future decision explicitly approves and binds this v2 package commit after independent review.

## Exact Diagnostic Command

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

No argument may be omitted, added, renamed, or changed.

## Required Preflight

The single read-only preflight must confirm:

- clean `HEAD` equals synchronized `origin/main` and contains the package, implementation, approval governance, post-approval evidence, and governance binding;
- all implementation hashes equal the v2 Manifest and post-approval evidence;
- all five permitted inputs exist as regular non-symlink files;
- all three channel paths and SHA-256 values equal the external registry before any semantic parsing;
- cache SHA/bytes remain `69ED...06F7D` / 210,714,667 and v2.2 decisions SHA remains `6FB6...23C7`;
- 4,500 queries, 143,820 units, sample-ID digest `6B21...8FB2`, runtime query-ID digest `8895...5CD6`, namespace relation, registered source-audit digest, model, max length, and batch size remain frozen;
- machine/narrative audit outputs are absent and OS temp parent is exact;
- formal v2.3.1 decisions/rankings/policy/controller-audit/`VERIFIED_PRE_GOLD` outputs remain absent;
- no ranking, policy, evaluator/Gold, reservation, or Stage3B input is supplied.

Any preflight failure must be committed as a hard-failure audit and execution must stop without capture or retry.

## Output Boundary

The machine audit may contain only aggregate counts, registered file hashes/sizes, terminal-newline flags, canonical digests, schema/discrete/float/ULP summaries, decision-semantic counts, channel pre/post gate status, temporary cleanup status, and at most salted query-ID hashes. It must not contain raw query IDs, decision rows, questions/text, rankings, policy, or Gold content.

Raw byte equality remains the controlling frozen gate. Canonical or semantic equality may explain a difference but cannot replace byte equivalence.

## Explicitly Not Requested

This request does not authorize:

- reading or comparing any official ranking or reference policy;
- opening the Stage4A-R2 source-audit file;
- reading evaluator files, Gold, or any U1-D effect metric;
- generating formal decisions, rankings, policy, controller audit, or `VERIFIED_PRE_GOLD`;
- running the full controller, verifier, evaluator, reservation, or Stage3B;
- modifying code, data, model, parameters, score, ECDF, budget, trigger, ranking, endpoint, stop rule, or equivalence;
- creating, rebuilding, overwriting, deleting, or migrating any cache;
- overwriting/deleting v2.2, v2.3.1, Hard Failure 4, or prior 5B artifacts;
- retrying after any rebinding, preflight, capture, cleanup, commit, or push failure;
- automatically resuming official pre-Gold execution after diagnosis.

## Mandatory Stop

After the diagnostic audit is pushed, execution must stop in this state:

```text
AMENDMENT_5B_V2_OFFICIAL_DECISIONS_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

The package itself authorizes no command. Current state remains `AMENDMENT_5B_V2_AWAITING_APPROVAL` until a new decision explicitly binds the package commit.
