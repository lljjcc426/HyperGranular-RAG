# Stage4B-U1-D Pre-Gold Amendment 5B Official Decisions-Only Diagnostic Approval Request

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-13
- Request ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_5B_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_MANIFEST.json`
- Current official state: `PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_4`
- Amendment 5A state: `AMENDMENT_5A_SYNTHETICALLY_VERIFIED`
- Official diagnosis: `NOT_APPROVED`
- Controller rerun: `NOT_APPROVED`
- Verifier: `NOT_APPROVED`
- Other project conversations, thread tools, and global memory used: No

## Binding Commits

```text
Hard Failure 4:
b21852a174b537c90a848699deb4d26d6f169506

v2.3.1 implementation:
34349c70ee24b8240fd169393134d4280968b790

original resumption package:
e76c921454697d1784b0d76a9d9677113051f0f6

approval governance:
53850f58e57f51b3c6067ed3108edff6b99a2dfc

synthetic rebinding:
a963befd812658972b156d2a7a26a488ac3c4482

failed controller execution HEAD:
8e0bab13ad20c06795dffd5ca71f167a814cdfb0

Amendment 5A package:
81d8c34f1cf2539a4c0b81c6148047bc666e2f82

Amendment 5A approval governance:
a0bf91b3a34daaf5b1ee50700d8356e1383e9a9c

Amendment 5A final implementation and evidence:
9a060bd31e9c33be587f7ef5e64f86206922e59e
```

The approval must also bind the commit containing this request and Manifest. An approval that does not bind that package commit is invalid.

## Requested Authorization

Request approval for one controlled official decisions-only diagnosis. Authorization would be limited to this sequence:

1. Commit and push the approval decision and final governance state.
2. On the final approved governance bytes, run the complete 98-test synthetic suite twice. Both runs must be 98/98, zero failure/error/skip, byte-identical, and record zero official-path access attempts.
3. Create and push a governance-binding JSON containing SHA-256 values for this request, this Manifest, the approval decision, final `AGENTS.md`, implementation commit `9a060bd...`, and the post-approval rebinding evidence.
4. Run one read-only diagnostic preflight. Any failure stops execution without retry.
5. Run the exact decisions-only capture command once.
6. Validate that the machine audit contains aggregate diagnostics only and that the temporary decisions file was deleted.
7. Create a short narrative audit that reports the frozen command, hashes, aggregate comparison classification, and boundary checks without raw query IDs or rows.
8. Commit and push the two audit outputs, verify GitHub, and stop.

## Exact Official Data Boundary

The single command may read only:

- v2.3.1 unlabeled units;
- v2.3.1 unlabeled queries;
- v2.3.1 controller channel audit;
- the existing ID-bound embedding cache in `require-existing` mode;
- the frozen v2.2 decisions JSONL.

The Stage4A-R2 source-audit file is not opened. The diagnostic validates only the source-audit SHA already registered in the committed controller channel audit. Evaluator Gold map/audit, official rankings, reference policy, reservation, and Stage3B are outside the allowed boundary.

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
  --expected-embedding-cache-sha256 69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D `
  --official-authorization-token APPROVE_STAGE4B_U1_D_AMENDMENT_5B_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC
```

The tool rejects any different official input/output path, cache SHA, model setting, OS temp parent, existing audit output, unregistered channel boundary, or v2.2 reference decisions SHA.

## Required Preflight

Before the single command, the read-only preflight must confirm:

- clean HEAD equals synchronized `origin/main`;
- all bound commits, the approval commit, governance-binding JSON, and post-approval synthetic evidence are ancestors of HEAD;
- diagnostic implementation hashes match the Manifest and post-approval evidence;
- the five permitted input paths exist as ordinary files;
- the machine and narrative audit output paths do not exist;
- the OS temp parent is exactly `C:\Users\cc\AppData\Local\Temp`;
- the cache SHA/bytes remain `69ED...06F7D` / `210714667`;
- v2.2 decisions SHA remains `6FB6...23C7`;
- the v2.3.1 formal decisions, rankings, policy, controller audit, and `VERIFIED_PRE_GOLD` paths remain absent;
- no evaluator, Gold, ranking, policy, reservation, or Stage3B input is supplied.

## Output Boundary

The machine audit may contain only aggregate counts, file hashes/sizes, terminal-newline flags, canonical digests, schema/discrete/float/ULP summaries, decision-semantic counts, and at most a salted first-difference query-ID hash. It must not contain raw query IDs, decision rows, question/text, ranking, policy, or Gold content.

The diagnostic does not redefine equivalence. Raw byte equality remains the frozen gate. Canonical or semantic equality may explain the byte difference but cannot replace it.

## Explicitly Not Requested

This request does not authorize:

- reading or comparing any official ranking;
- reading the v2.2 reference policy;
- reading evaluator Gold map/audit or any U1-D effect metric;
- generating formal decisions, rankings, policy, controller audit, or `VERIFIED_PRE_GOLD`;
- running the full controller, verifier, evaluator, reservation, or Stage3B;
- modifying code, data, model, parameters, score, ECDF, budget, trigger, ranking, endpoint, stop rule, or equivalence definition;
- creating, rebuilding, overwriting, deleting, or migrating any cache;
- overwriting or deleting v2.2/v2.3.1 failure artifacts;
- retrying after any preflight, capture, cleanup, commit, or push hard failure;
- automatically resuming official pre-Gold execution after diagnosis.

## Mandatory Stop

After the diagnostic audit is pushed, execution must stop in a diagnosis-only state. Hard Failure 4 remains unresolved until the result is independently reviewed and a separate amendment is approved.

```text
AMENDMENT_5B_OFFICIAL_DECISIONS_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
