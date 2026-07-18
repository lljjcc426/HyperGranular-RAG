# Stage4B-U1-D Simplified Execution Protocol v1

## Status and scope

- Status: `LEVEL_A_PROTOCOL_ACCEPTED`
- Stage state after the approved compatibility correction: `LEVEL_B_IMPLEMENTATION_AUTHORIZED`
- Scope: Stage4B-U1-D development slice only, 4,500 queries and 143,820 unlabeled units.
- Reservation, Stage3B, Gold evaluation, official execution, and result interpretation remain locked.
- This document freezes the execution contract and authorizes synthetic-only Level B implementation. It does not authorize official preflight/execution, Gold evaluation, reservation access, or a retry of any retired approval chain.

This protocol is the minimal replacement for the retired Amendment 1.1.7–1.1.9 PowerShell launcher, remote gate, observer, and nested PRE route. Those files remain immutable historical evidence but are not an execution dependency of this protocol.

## 1. Review level and activation rule

This protocol is a Level A scientific-critical artifact because it fixes the data boundary, Gold boundary, algorithm, ranking semantics, outputs, evaluation gates, and stop rules.

Activation requires all of the following, in order:

1. independent Level A acceptance of the protocol, including the one approved evaluator effective-K compatibility correction (satisfied by the review bound to corrected commit `76dc179acbb657633fc1da1e4c5fbd398169e284` and the correction recorded below);
2. a later minimal implementation commit and Level B integrity review;
3. a later config-freeze commit containing `configs/stage4b_u1_d_official.json` with no placeholder values;
4. explicit user approval binding the protocol, implementation, config, inputs, cache, and output paths before any official preflight.

No step is implicitly approved by completion of the previous step.

## 2. Minimal process architecture

The future pre-Gold route has five components:

1. one frozen JSON config: `configs/stage4b_u1_d_official.json`;
2. one direct Python preflight: `scripts/stage4b_u1_simplified_preflight.py`;
3. one Gold-free controller entry point: `scripts/stage4b_u1_simplified_runner.py`;
4. one independent verifier entry point: `scripts/stage4b_u1_independent_verifier.py`;
5. the existing evaluator, invoked only after a separately approved Gold connection: `scripts/stage4b_u1_evaluate.py`.

The preflight, controller, and verifier are direct Python processes. They must not call a PowerShell launcher, query GitHub, compare command-line bytes, inspect terminal NUL behavior, require empty stderr, or start observer/adapter/parent/loader process layers.

## 3. Config freeze contract

### 3.1 Commit binding without a self-reference

The implementation must be committed before the config is created. The later config field `implementation.code_commit` must equal that full 40-character implementation commit. The config is then committed separately. At execution time, every bound implementation file in the worktree must have the same Git blob bytes as at `implementation.code_commit`.

The config must also bind this protocol by path and SHA-256. Placeholder values such as `TBD`, `TO_BE_BOUND`, empty strings, or all-zero hashes are invalid.

### 3.2 Required top-level sections

The exact top-level key set is:

```text
schema_version
run_id
mode
protocol
implementation
environment
inputs
embedding_cache
retrieval
controller
outputs
verification
evaluation_contract
retry_policy
```

The fixed scalar values are:

| Field | Frozen value |
|---|---|
| `schema_version` | `stage4b_u1_simplified_execution_v1` |
| `run_id` | `stage4b_u1_d_official_dev4500_simplified_v1` |
| `mode` | `development` |
| `protocol.path` | `docs/STAGE4B_U1_SIMPLIFIED_EXECUTION_PROTOCOL_V1.md` |
| `controller.evaluation_labels_loaded` | `false` |
| `controller.embedding_cache_mode` | `require-existing` |
| `retry_policy.automatic_retries` | `0` |

`protocol.sha256`, `implementation.code_commit`, `implementation.files[*].sha256`, and the SHA-256 of the complete config are bound only after the relevant bytes exist. The config-freeze review must reject a mismatch.

The remaining structural key sets are:

- `protocol`: `path`, `sha256`;
- `implementation`: `code_commit`, `files`;
- `inputs`: `unlabeled_units`, `unlabeled_queries`, `channel_audit`, `query_count`, `unit_count`, `sample_id_sha256`, `query_id_sha256`, `query_id_namespace_rule`; each file input has exactly `path`, `sha256`;
- `embedding_cache`: `path`, `sha256`, `bytes`, `members`, `unit_embeddings_shape`, `query_embeddings_shape`, `dtype`, `model_name`, `max_length`;
- `controller`: `script`, `embedding_cache_mode`, `evaluation_labels_loaded`; `script` is `scripts/stage4b_u1_simplified_runner.py`;
- `outputs`: `decisions`, `rankings`, `policy`;
- `verification`: `script`, `decisions_input`, `rankings_input`, `policy_input`, `output`; `script` is `scripts/stage4b_u1_independent_verifier.py` and its three inputs equal the corresponding `outputs` values;
- `retry_policy`: `automatic_retries`.

### 3.3 Python environment

The exact `environment` key set is `python_executable`, `python_version`, and `required_packages`. The science-relevant runtime frozen for the first implementation is:

| Field | Frozen value | Preflight gate |
|---|---|---|
| `environment.python_executable` | `D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe` | exact |
| `environment.python_version` | `3.12.0` | exact |
| `environment.required_packages.numpy` | `2.5.1` | exact |

The same interpreter was observed on 2026-07-18 with PyTorch 2.12.1, Transformers 5.9.0, and no separate `sentence-transformers` distribution. These three observations are not preflight gates because `require-existing` returns through cache validation before the local model-encoding function imports PyTorch or Transformers. The encoder identifier remains `sentence-transformers/all-MiniLM-L6-v2`; it is a model identifier recorded inside the frozen cache. The simplified official path must not download or rebuild the model/cache.

### 3.4 Frozen unlabeled inputs and cache

| Config field | Path | SHA-256 / identity |
|---|---|---|
| `inputs.unlabeled_units.path` / `.sha256` | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_units.jsonl` | `114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA` |
| `inputs.unlabeled_queries.path` / `.sha256` | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_queries.jsonl` | `6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B` |
| `inputs.channel_audit.path` / `.sha256` | `results/stage4b_u1_d_official_dev4500_v2_3_1_controller_channel_audit.json` | `D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA` |
| `embedding_cache.path` / `.sha256` | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_minilm_idbound_embeddings.npz` | `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D` |

Additional fixed identities are:

- `inputs.query_count`: `4500`;
- `inputs.unit_count`: `143820`;
- `inputs.sample_id_sha256`: `6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2`;
- `inputs.query_id_sha256`: `8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6`;
- `inputs.query_id_namespace_rule`: `query_id == dataset + "::" + sample_id` for every query;
- `embedding_cache.bytes`: `210714667`;
- `embedding_cache.members`, exactly: `unit_embeddings`, `query_embeddings`, `unit_ids`, `query_ids`, `model_name`, `max_length`;
- `unit_embeddings`: shape `[143820, 384]`, dtype `float32`;
- `query_embeddings`: shape `[4500, 384]`, dtype `float32`;
- cache model name: `sentence-transformers/all-MiniLM-L6-v2`;
- cache `max_length`: `192`;
- cache policy: require existing, no write, no rebuild, no download.

The config must contain no Gold-map path, Gold-map hash, labeled-source hash, answer, supporting-fact label, reservation path, or reservation metric.

## 4. Frozen retrieval and controller semantics

### 4.1 Retrieval parameters

The config must serialize every value explicitly; implementation defaults are not an acceptable substitute.

| Field | Value | Field | Value |
|---|---:|---|---:|
| `min_size` | 2 | `max_size` | 3 |
| `radius_threshold` | 0.78 | `max_depth` | 6 |
| `boundary_width` | 0.2 | `top_center_terms` | 8 |
| `seed_balls` | 2 | `top_facet_edges` | 2 |
| `max_expanded_balls` | 2 | `min_new_terms` | 1 |
| `min_facet_score` | 0.10 | `max_candidate_ball_size` | 8 |
| `min_ball_score` | 0.12 | `min_seed_similarity` | 0.05 |
| `max_units_per_new_term` | 6.0 | `max_redundancy` | 0.90 |
| `w_new` | 0.45 | `w_total` | 0.20 |
| `w_ball` | 0.20 | `w_diversity` | 0.15 |
| `w_redundancy` | 0.20 | `w_size` | 0.05 |
| `w_facet_unit_bonus` | 0.0 | `q25_floor` | 0.1957079917192459 |
| `protect_n` | 10 | `insert_budget` | 4 |
| `max_k` | 20 | `budget_fraction` | 0.60 |
| `model_name` | `sentence-transformers/all-MiniLM-L6-v2` | `max_length` | 192 |
| `batch_size` | 64 | `embedding_dtype` | `float32` |
| `scalar_dtype` | `float64` |  |  |

For query `q`, the effective lengths are:

```text
K_q = min(20, |C_q|)
P_q = min(10, K_q)
0 <= planned_insert_count <= min(4, K_q - P_q)
```

An empty candidate pool is a hard failure. Legacy output field names containing `top20` retain that name for schema compatibility, but their required length is `K_q`, not always 20.

### 4.2 U1-D score

Only feasible rows (`selected_edge_count > 0` and `planned_insert_count > 0`) fit the development ECDFs. Each ECDF is the exact float64 midrank:

```text
F(x) = (count_less(x) + 0.5 * count_equal(x)) / n
```

The four inputs and formula are:

```text
u_margin    = 1 - F_dev(ball_score_margin)
u_boundary  = 1 - F_dev(boundary_margin)
r_edge      = F_dev(log1p(selected_edge_count))
r_candidate = F_dev(log1p(planned_insert_count))
uncertainty = (u_margin + u_boundary) / 2
readiness   = sqrt(r_edge * r_candidate)
score       = uncertainty * readiness
```

All inputs and derived numerical values must be finite. Infeasible rows have `null` ECDF/score fields, `ordered_rank=null`, and `trigger_u1=0`.

Tie-breaking is ascending SHA-256 of the UTF-8 string `stage4b_u1_v2::<query_id>`. Feasible rows are ordered by `(-score, tie_hash)`. The planned-insert budget is `floor(sum(planned_insert_count over feasible rows) * 0.60)`. Selection is the longest non-empty ordered prefix whose cumulative planned inserts do not exceed that budget; rows may not be skipped.

If `trigger_u1=0`, final ranking equals dense ranking and final inserted IDs are empty. If `trigger_u1=1`, final ranking equals q25 ranking and final inserted IDs equal the independently derived q25 inserted IDs.

## 5. Frozen algorithm baseline and semantic-equivalence gate

The parent baseline is commit `e12907d5501cb9e3fe9eaec5590e517d3ef93e30`. The first four identities below are unchanged pre-Gold baseline sources; the evaluator identity is the approved Level A effective-K compatibility correction:

| File | SHA-256 |
|---|---|
| `scripts/stage4b_u1_common.py` | `CDF7EAD6007DABE389ED0BD18983496F75290C32243FE6DF84716810CDE92CE4` |
| `scripts/stage4b_u1_goldfree_retrieval.py` | `3B50FAFD057E2565167ED09288D61829B3FBD044991F139F734F819955038A3B` |
| `scripts/stage4b_u1_goldfree_controller.py` | `C18AD3B672649BA846C5E191D0DBBAC7644A926D4B8CCD39176127175BBA7C1F` |
| `scripts/stage4b_u1_verify.py` | `DC134B51A07C14A553746C303EA31D83990BA0EFAD30EFC3A1722F1A141E66EC` |
| `scripts/stage4b_u1_evaluate.py` | `D7B96E29AD5AB2F6652FFC14D73048D36C205F78ABA7FA8FCB501818A1A89BBB` |

The later `implementation.files` object must bind the exact paths and SHA-256 values for the first four pre-Gold baseline files above plus the three new preflight/runner/verifier entry points. It may not bind a directory glob. `evaluation_contract.evaluator_script` and `.evaluator_script_sha256` bind `stage4b_u1_evaluate.py` separately so that the pre-Gold controller never imports or invokes it.

The minimal implementation may change orchestration, config loading, output-path binding, and verification wrappers. Any change to retrieval candidates, score, ECDF, budget, trigger, ranking, q25, protected prefix, insert semantics, or evaluation endpoints is a new Level A protocol change, not a Level B implementation change.

Before config freeze, synthetic-only tests must establish semantic equivalence between the baseline algorithm and the simplified route for:

- query order and IDs;
- field types and nullability;
- `ball_score_margin`, `boundary_margin`, `selected_edge_count`, and `planned_insert_count`;
- ECDF references and all derived scores;
- tie hash, ordered rank, allocation prefix, and trigger;
- dense IDs, q25 IDs, independently derived inserted IDs, and final ranking IDs.

Equivalence is semantic and field-wise. Byte equality of files, PowerShell command lines, JSON indentation, absolute output paths, GitHub visibility, stderr framing, or observer records is not required. The semantic test must use synthetic fixtures only and must not open any official input, official cache, prior official ranking, Gold, or reservation file.

## 6. Output paths and schemas

### 6.1 Pre-Gold output paths

The config fields `outputs.decisions`, `outputs.rankings`, `outputs.policy`, and `verification.output` have the following frozen values, and all four paths must be absent at future preflight start:

```text
results/stage4b_u1_d_official_dev4500_simplified_v1_decisions.jsonl
results/stage4b_u1_d_official_dev4500_simplified_v1_rankings.jsonl
results/stage4b_u1_d_official_dev4500_simplified_v1_policy.json
results/stage4b_u1_d_official_dev4500_simplified_v1_verified_pre_gold.json
```

The controller creates only the first three. The verifier creates only the fourth after the first three are committed.

### 6.2 Decisions JSONL

There is exactly one row per query in query-input order. The exact key set is:

```text
query_id, dataset, sample_id,
ball_score_margin, boundary_margin,
selected_edge_count, planned_insert_count, feasible,
u_margin, u_boundary, r_edge, r_candidate,
uncertainty, readiness, score,
tie_hash, ordered_rank, trigger_u1
```

IDs are non-empty strings. Counts, `feasible`, `ordered_rank`, and `trigger_u1` are JSON integers; `feasible` and `trigger_u1` are restricted to 0/1. Numerical fields are finite JSON numbers when applicable. Only the seven ECDF/score fields and `ordered_rank` may be `null`, and only for infeasible rows.

### 6.3 Rankings JSONL

There is exactly one row per query in the same order. The exact key set is:

```text
query_id, dataset, sample_id, trigger_u1, planned_insert_count,
dense_top20_unit_ids, q25_top20_unit_ids, q25_inserted_unit_ids,
final_top20_unit_ids, final_inserted_unit_ids
```

All ranking members are unique non-empty unit-ID strings and members of that query's candidate pool. Dense, q25, and final list lengths are exactly `K_q`. The q25 prefix of length `P_q` equals the dense prefix. Inserted lists contain no protected-prefix ID and are independently derivable from the eligible q25 slice.

### 6.4 Policy JSON

The exact required top-level keys are:

```text
schema_version, implementation_checkpoint, execution_profile,
protocol, protocol_sha256,
simplified_execution_protocol, simplified_execution_protocol_sha256,
execution_config, execution_config_sha256,
status, run_role, git_commit_sha, code_commit_sha,
sample_id_sha256, query_id_sha256, queries, units,
model_name, max_length, batch_size, retrieval_config,
ecdf_definition, ecdf_references, allocation,
input_hashes, output_hashes, implementation_hashes,
controller_source_sha256, parent_development_policy_sha256,
evaluation_labels_loaded
```

For compatibility with the evaluator's retained legacy contract, the frozen values are:

- `schema_version=stage4b_u1_v2`;
- `implementation_checkpoint=stage4b_u1_v2_3_1`, identifying the unchanged scientific algorithm checkpoint rather than the new orchestration profile;
- `protocol=docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md` and its exact SHA-256, because the evaluator retains the hard check for that legacy scientific-protocol field;
- `simplified_execution_protocol=docs/STAGE4B_U1_SIMPLIFIED_EXECUTION_PROTOCOL_V1.md` and the exact SHA-256 bound by the config;
- `execution_profile=stage4b_u1_simplified_v1`;
- `status=POLICY_FROZEN_BEFORE_EVALUATION`, `run_role=development`, `parent_development_policy_sha256=null`, and `evaluation_labels_loaded=false`.

The legacy `protocol` field is retained only as evaluator compatibility; it does not reactivate any old launcher or governance chain. The policy additionally records the config SHA, current execution HEAD, bound implementation commit, all implementation/input/output hashes, exact retrieval config, ECDF references, and allocation summary. It contains no evaluation metric or Gold identity.

### 6.5 Verified pre-Gold JSON

The exact top-level key set is:

```text
schema_version, implementation_checkpoint, execution_profile, status,
synthetic_test_mode, frozen_commit_sha,
simplified_execution_protocol, simplified_execution_protocol_sha256,
execution_config, execution_config_sha256, code_commit_sha,
independent_verifier_source, independent_verifier_source_sha256,
static_controller_boundary, implementation_hashes,
identity_boundary, policy_and_ranking, checks,
gold_inputs_loaded, evaluation, artifact_hashes
```

The exact `checks` key set is:

```text
identity, input_schema, output_schema, numeric_finiteness,
ecdf_and_score, allocation_and_trigger, effective_k,
ranking_membership, protected_prefix_and_inserts, final_selector,
ranking_query_set, committed_artifact_set, gold_isolation
```

Every check value is `PASS`. For compatibility with the evaluator's retained legacy contract, fixed values include `schema_version=stage4b_u1_v2`, `implementation_checkpoint=stage4b_u1_v2_3_1`, `synthetic_test_mode=false`, `status=VERIFIED_PRE_GOLD`, `gold_inputs_loaded=false`, and `evaluation=null`.

`frozen_commit_sha` is the commit containing the exact decisions/rankings/policy set. `artifact_hashes` has exactly `channel_audit`, `decisions`, `rankings`, and `policy`, because the evaluator independently compares those fields. `implementation_hashes` must equal the policy field. `identity_boundary` records 4,500 queries, 143,820 units, both ID digests, and the namespace check. The additional simplified-protocol/config/verifier fields bind the new route without removing evaluator-required legacy keys. The file is deterministic and contains no timestamp or host-specific temporary path.

## 7. Direct Python preflight

The preflight performs only science-relevant checks:

1. strict JSON parse with duplicate-key rejection and exact config schema;
2. protocol/config/code commit and file SHA binding;
3. exact Python and required package versions;
4. exact input/cache paths, bytes, SHA-256, counts, ID digests, namespace rule, and query/unit linkage;
5. exact channel-audit identity and prohibited-label-key absence;
6. exact cache member set, shapes, dtypes, ID order, model name, max length, and finite matrices;
7. exact retrieval/controller constants and Gold-free config boundary;
8. absence of all six registered future output paths;
9. no Gold, reservation, prior official ranking, reference-policy, or evaluator input is opened.

Failure returns nonzero before the controller is called and creates no output. A pass emits only one concise canonical status line to stdout; it does not create a preflight artifact.

## 8. Controller and independent-verifier gates

The controller must use exclusive create for a same-filesystem pending directory, validate all three pending artifacts, confirm cache SHA/bytes unchanged, and then promote decisions/rankings/policy as one guarded group with mandatory rollback on a partial promotion. This is not represented as a filesystem-wide atomic primitive: consumer-level atomicity comes from accepting only the later exact three-path Git commit. A partial set is a hard stop and may not be committed or verified. Existing final paths are never overwritten.

After a successful controller run:

1. commit and push exactly decisions, rankings, and policy at their three frozen paths;
2. stop if commit or push fails;
3. run the independent verifier only against the committed artifact commit;
4. commit and push `VERIFIED_PRE_GOLD` separately;
5. stop immediately.

The verifier must independently recompute or validate, without calling the controller:

- exact config/code/protocol/input/cache/output identities;
- complete and unique query IDs and exact row/key/type/nullability contracts;
- finite numerical values and the four ECDF references;
- score, tie hash, ordered rank, budget, cumulative prefix, and trigger;
- `K_q`, `P_q`, candidate count, ranking length, uniqueness, and membership;
- protected prefix, planned insert bound, independently derived inserted IDs, and final selector;
- ranking query set is exactly the frozen development query set;
- decisions, rankings, and policy are committed together and unchanged;
- controller/config/policy/outputs contain no prohibited Gold or label payload;
- evaluator has not run and evaluation is null.

Any failed gate prevents `VERIFIED_PRE_GOLD` and stops the branch. There is no automatic rerun.

## 9. Separate Gold evaluator boundary

The exact `evaluation_contract` keys are `authorized`, `evaluator_script`, `evaluator_script_sha256`, `inputs`, and `outputs`. The pre-Gold config freezes only these evaluator-side non-Gold values:

```text
inputs:
  rankings = results/stage4b_u1_d_official_dev4500_simplified_v1_rankings.jsonl
  policy = results/stage4b_u1_d_official_dev4500_simplified_v1_policy.json
  verified_pre_gold = results/stage4b_u1_d_official_dev4500_simplified_v1_verified_pre_gold.json
outputs:
  query_audit = results/stage4b_u1_d_official_dev4500_simplified_v1_query_audit.jsonl
  evaluation_summary = results/stage4b_u1_d_official_dev4500_simplified_v1_evaluation_summary.json
authorized = false
evaluator_script = scripts/stage4b_u1_evaluate.py
evaluator_script_sha256 = D7B96E29AD5AB2F6652FFC14D73048D36C205F78ABA7FA8FCB501818A1A89BBB
```

Gold-map and evaluator-audit paths/hashes are intentionally absent from the pre-Gold config so that the controller process cannot receive them. Only after rankings and `VERIFIED_PRE_GOLD` are committed/pushed, independently reviewed, and separately approved may a Gold-specific authorization bind and pass evaluator-only values for `gold_map_path`, `evaluator_audit_path`, `stage4a_r2_verification_path`, `stage4a_r2_strategy_summary_path`, `bootstrap_iterations`, `bootstrap_seed`, and `run_role=development`. That later authorization does not permit reservation access.

The frozen U1-D advancement gates remain:

- insertion-cost reduction at least 40%;
- retention gap at least +0.15;
- one-sided Fisher exact `p < 0.05`;
- CR@20 versus dense at least +0.005;
- CR@20 versus all-q25 at least -0.005;
- conditional false-insert rate not worse by more than 0.01;
- Gold isolation, ranking-subset validation, independent verification, and deterministic rerun all pass.

Failure yields `STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED`. Passing U1-D still does not open reservation; reservation requires a new protocol and explicit approval.

The deterministic rerun gate is not an automatic retry and is not part of the initial pre-Gold route. Its versioned output paths and comparison contract must be frozen in the later Gold-phase Level A authorization; advancement is withheld until that separately approved check passes.

## 10. Review and test requirements

- Protocol and any scientific semantic change: Level A.
- Config loader, cache/schema/effective-K checks, atomic promotion, Gold scan, verifier wrapper, and output schema implementation: Level B.
- Command quoting, local permissions, stdout/stderr presentation, TLS, GitHub visibility, aliases, and tooling messages: Level C unless they corrupt data/config, expose Gold, alter rankings/metrics, or leave partial official outputs.

The implementation review must include targeted config/preflight/verifier failure tests and synthetic semantic-equivalence tests. If ranking, verifier, or schema code changes, run the complete synthetic suite once. No official input or cache is used in implementation tests.

## 11. Stop and retry rules

- Automatic retries: zero.
- A config, code, input, cache, Gold-boundary, ranking, output-integrity, or verifier failure stops immediately and is recorded at the corresponding review level.
- A Level C failure before official input is opened and before any output exists may be corrected only after reporting it and obtaining explicit user confirmation; any code/config byte change requires renewed binding and the applicable review.
- No retry may reuse the terminated `ef9ba5b3...` approval chain or any 1.1.7–1.1.9 launcher/observer artifact.

## 12. Material passport

- Governance parent: `e12907d5501cb9e3fe9eaec5590e517d3ef93e30`.
- User direction source: `C:\Users\cc\.codex\attachments\85baf725-8eaa-4a9d-9cb6-f7a646e3afec\pasted-text.txt`, 9,153 bytes, SHA-256 `628AAF9993DA8A981245D167A8DE3FEF861DB559B4AEC61575054F59CA5046D0`.
- Scientific design source: `docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md`.
- Governance contraction source: `docs/STAGE4B_U1_EXECUTION_GOVERNANCE_SIMPLIFICATION_AMENDMENT.md`.
- Input/cache identity sources: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_MANIFEST.json` and the tracked controller channel audit listed above.
- Initial protocol freeze commit: `8657709fe492455587d1e473ed22ee7793c0b995`.
- Corrected protocol commit reviewed at Level A: `76dc179acbb657633fc1da1e4c5fbd398169e284`.
- Level A review source: `C:\Users\cc\.codex\attachments\ab7328dd-72d9-4325-8cfc-7ed983755fbd\pasted-text.txt`, 13,594 bytes, SHA-256 `3982BC0329FFBA82E24834B64491E37F053B6C9684C332762D4A51CF38F30AE6`.
- Author-side ARS validation found, before independent Level A review, that the initial policy and `VERIFIED_PRE_GOLD` schemas were incompatible with the unchanged evaluator's legacy field checks. This corrected freeze retains the evaluator-required schema/checkpoint/protocol and pre-Gold artifact keys while adding separate simplified-route bindings.
- The Level A review returned exactly one compatibility correction: replace the evaluator's fixed-20 checks with the frozen effective-K rules. The evaluator now enforces `1 <= K_q <= 20`, equal effective lengths, per-list uniqueness, `P_q=min(10,K_q)`, bounded insertion, protected-prefix preservation, trigger/final selection, derived inserted IDs, and a required independently verified ranking-structure/candidate-membership attestation. It does not change candidates, q25, score, allocation, ranking, endpoints, or any Gold input.
- Targeted evaluator tests passed 13/13 for candidate sizes 20, 17, 10, 9, and 1 plus the required failure cases. The complete synthetic suite passed 63/63. Both runs used synthetic fixtures only.
- No external official input, Gold map, Gold metric, reservation metric, prior official ranking content, or evaluator output was opened to create this protocol.

Current states: `LEVEL_A_PROTOCOL_ACCEPTED`, `LEVEL_B_IMPLEMENTATION_AUTHORIZED`, `OFFICIAL_EXECUTION_NOT_YET_AUTHORIZED`, `GOLD_EVALUATION_NOT_AUTHORIZED`, and `RESERVATION_NOT_AUTHORIZED`.
