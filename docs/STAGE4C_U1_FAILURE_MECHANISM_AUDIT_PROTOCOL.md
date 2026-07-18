# Stage4C-U1-FMA U1 Failure Mechanism Audit Protocol

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: plan
- Origin Date: 2026-07-18
- Verification Status: `FROZEN_BEFORE_STAGE4C_DIAGNOSTIC_STATISTICS`
- Version Label: `stage4c_u1_fma_protocol_v1`
- Study role: post-Gold exploratory mechanism diagnosis
- Data role: 2WikiMultiHopQA development, 4,500 queries
- Reservation / Stage3B access: prohibited
- New controller efficacy claim: prohibited

## 1. Experiment Overview

- Title: `Stage4C-U1-FMA — U1 Failure Mechanism Audit`
- Objective: explain why the frozen U1 query-level score retained harm more often than gain, and assess whether fixed deployment-time unlabeled signals justify a separate future controller hypothesis.
- Type: exploratory diagnostic analysis plus low-capacity out-of-fold learnability probe.
- Evidence class: post-Gold exploratory diagnosis; not confirmatory validation, U1-D repair, U2 development, or efficacy evidence.

Research questions:

1. Why did the frozen U1 features fail to produce gain-over-harm selection?
2. Does the fixed allowed artifact set contain stable deployment-time unlabeled signal that could justify a new candidate-level or path-level controller protocol?

The following claims are immutable inputs, not hypotheses to be reopened:

```text
q25 gain events = 94
q25 harm events = 69
retained gains = 47
retained harms = 53
gain retention = 0.500000
harm retention = 0.768116
retention gap = -0.268116
U1 CR@20 delta vs Dense = -0.001333
U1 CR@20 delta vs all-query q25 = -0.006889
inserted-unit reduction = 0.400275
STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED
```

Stage4B-U1-D remains a valid negative result regardless of every Stage4C result.

## 2. Authority And Prohibitions

This protocol authorizes one continuous Stage4C transaction after this document is committed and pushed:

1. implement the frozen diagnostic script and tests;
2. commit and push the implementation before the first diagnostic run;
3. run the diagnostic once on the seven exact allowed artifacts;
4. validate, interpret, report, commit, and push the results.

It does not authorize:

- reservation, Stage3B, or any test-set access;
- the Stage4B controller, evaluator, or deterministic Gold rerun;
- Gold map or evaluator-audit access;
- new Gold joins or candidate-level Gold reconstruction;
- U1 score, weight, budget, protect/insert, q25 floor, ranking, endpoint, or threshold searches;
- a new official controller, U2 development, or efficacy claim;
- question-type selection as a deployment rule;
- deletion, overwrite, or reinterpretation of any Stage4B artifact.

Gold-derived fields may define diagnostic targets only. No Gold-derived field, question type, query ID, sample ID, unit ID, or label may enter a probe feature matrix.

## 3. Frozen Inputs

Only these committed paths may be opened by the Stage4C implementation:

| Role | Path | Bytes | SHA-256 |
|---|---|---:|---|
| U1 decisions | `results/stage4b_u1_d_official_dev4500_simplified_v1_decisions.jsonl` | 2,684,439 | `4B2AD2E5707B20FD46B6250FDA5395433F52E55FB1281F1499412C8C749A456A` |
| frozen rankings | `results/stage4b_u1_d_official_dev4500_simplified_v1_rankings.jsonl` | 18,235,604 | `ED289D234F6F4FEC58A48168CB6CA78950489CD5F5640E977068CA6A786E03CB` |
| U1 policy | `results/stage4b_u1_d_official_dev4500_simplified_v1_policy.json` | 261,587 | `657E5F25A94224D8B020780F3E7335942B16BC6D8C7939FB74D1BBAA9A9D868B` |
| pre-Gold verification | `results/stage4b_u1_d_official_dev4500_simplified_v1_verified_pre_gold.json` | 3,479 | `39EAD86A3A835983DCB67BAF656255F51569BCEE5B9AC2E16FACF404281D7818` |
| Gold query audit | `results/stage4b_u1_d_official_dev4500_simplified_v1_query_audit.jsonl` | 2,600,121 | `8616C28C71D190E3287CCE3725EDC0B1FD0DFB41DF47C739F4A84A573F938313` |
| Gold summary | `results/stage4b_u1_d_official_dev4500_simplified_v1_evaluation_summary.json` | 7,662 | `7F82056FB14F9D8D73E668A82CB5304B28385E62A01C428599F23260AB7F89DE` |
| post-Gold verification | `results/stage4b_u1_d_official_dev4500_simplified_v1_verified_post_gold.json` | 2,293 | `44BF3E8B0B036958633E237186A458B13090D8073F587657D831656FB7720ECD` |

Before analysis, the implementation must verify bytes and SHA-256, `VERIFIED_PRE_GOLD`, `VERIFIED_POST_GOLD`, the frozen decision, and exact row identities. It must reject duplicate or missing `query_id`, dataset/sample mismatches, unequal 4,500-row sets, non-finite values, or unexpected key/type/nullability contracts.

The implementation must expose no CLI argument capable of replacing an input path. All seven paths are repository-relative constants. The only runtime option is `--output-dir`, used for the registered result directory and synthetic tests.

## 4. Protocol-Time Availability Boundary

The pre-statistic schema inspection establishes the following without computing new Stage4C results:

Available:

- query-level U1 margins, ECDF transforms, readiness components, score, rank, feasibility, trigger, and planned insert count;
- Dense/q25/final unit-ID sequences;
- q25/final inserted unit-ID sequences and insertion positions;
- query-level q25/U1 inserted gold and non-gold counts;
- Dense/q25/U1 ER@20 and CR@20 outcomes and question type for descriptive audit.

Unavailable in the seven allowed artifacts:

- candidate-level Gold identity and gold-candidate eligible-slice rank;
- dense, q25, facet, or candidate numeric scores;
- seed-candidate similarity;
- seed, granular-ball, facet, or hyperedge support counts;
- cross-ball support, entity/bridge overlap, path length, semantic redundancy, or candidate-to-candidate support;
- features of the displaced original ranking unit beyond its unit ID.

Unit IDs may be used only for deterministic list/position/set diagnostics and must never be model inputs. Missing candidate-level fields must be reported as `NOT_AVAILABLE_IN_FROZEN_ALLOWED_ARTIFACTS`; the implementation must not open a Gold map, corpus, embedding cache, candidate cache, or source dataset to fill them.

## 5. Exact Joins And Diagnostic Labels

Rows are joined one-to-one by native non-empty string `query_id`. For every joined row, `dataset` and `sample_id` must match exactly across decisions, rankings, and query audit.

Labels are derived only as follows:

```text
GAIN    := dense_cr20 == 0 and q25_cr20 == 1
HARM    := dense_cr20 == 1 and q25_cr20 == 0
NEUTRAL := all other valid binary pairs
```

Required frozen reconciliation before all downstream analysis:

```text
GAIN = 94
HARM = 69
trigger_u1 AND GAIN = 47
trigger_u1 AND HARM = 53
```

The script must also reconcile q25/U1 inserted counts, summary metrics, and `STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED`. Any mismatch is terminal before output promotion. It must not retry or relax a check.

## 6. Query-Feature Audit

Pre-specified features:

```text
ball_score_margin
boundary_margin
selected_edge_count
planned_insert_count
u_margin
u_boundary
r_edge
r_candidate
uncertainty
readiness
score
ordered_rank
```

For each feature and each of GAIN, HARM, and NEUTRAL, report:

- total rows, finite rows, missing count, non-finite count;
- mean, sample standard deviation (`ddof=1`), median;
- q10, q25, q50, q75, q90 using NumPy linear quantiles;
- query-stratified bootstrap 95% percentile intervals for mean and median.

GAIN-vs-HARM separability is computed on finite complete cases only:

- `auroc_gain_high`: tie-aware Mann-Whitney AUROC where a higher raw feature predicts GAIN;
- `average_precision_gain_high`: tie-group threshold AP with GAIN positive;
- direction: `GAIN_HIGH` if AUROC > 0.5, `HARM_HIGH` if AUROC < 0.5, `NO_DIRECTION` if exactly 0.5;
- distribution overlap: fixed 20 equal-width bins on the combined finite GAIN/HARM range, sum of the minimum normalized bin masses; constant features have overlap 1.0;
- 10,000 query-unit stratified bootstrap resamples, independently resampling GAIN and HARM at their observed sizes;
- seed `20260718`;
- percentile 95% intervals for AUROC and AP.

No AUROC is direction-flipped. `max(AUROC, 1-AUROC)` may be included only as a clearly named descriptive magnitude and never replaces the raw direction.

If either class has fewer than 20 finite rows for a feature, separability metrics are emitted as null with `INSUFFICIENT_FINITE_EVENTS`.

## 7. Frozen Ranking-Decile Audit

Population: rows with `feasible == 1` and positive integer `ordered_rank`. Ranks must be unique and contiguous from 1 to the feasible count.

Fixed decile assignment:

```text
decile = min(10, floor((ordered_rank - 1) * 10 / feasible_count) + 1)
```

No decile boundary is result-selected. For each decile, and for cumulative prefixes 1 through that decile, report:

- queries, gains, harms, gain/query rate, harm/query rate;
- cumulative gain and harm counts;
- cumulative gain retention and harm retention relative to 94/69;
- cumulative retention gap;
- cumulative inserted units if that fixed prefix were on and the remainder dense;
- cumulative CR@20 delta versus Dense;
- cumulative CR@20 delta versus all-query q25;
- actual `trigger_u1` query and inserted-unit counts inside the decile.

The cumulative rows are fixed diagnostic counterfactuals, not candidate policies. No prefix may be selected as “best” or used to revise U1-D.

One descriptive pattern is assigned by this priority order:

1. `B_HIGH_SIGNAL_THEN_BUDGET_DEGRADATION`: at least one cumulative prefix among deciles 1–3 has positive retention gap, while the actual U1 trigger set has negative retention gap.
2. `A_HIGH_SCORE_HARM_DOMINANT`: decile 1 harms are at least gains and the cumulative decile-2 retention gap is non-positive.
3. `C_NEAR_NO_SEPARATION`: at least 8 of 10 deciles have absolute `(gain_rate - harm_rate) < 0.01`.
4. `D_LOCALIZED_OR_IRREGULAR_SIGNAL`: all remaining cases.

This label describes the fixed decile table only and is not a new threshold claim.

## 8. Uncertainty/Readiness Decomposition

The implementation independently verifies, within floating tolerance `1e-12`:

```text
uncertainty == (u_margin + u_boundary) / 2
readiness == sqrt(r_edge * r_candidate)
score == uncertainty * readiness
```

Mechanism diagnostics:

- compare raw AUROC/AP and bootstrap intervals for uncertainty, readiness, score, selected-edge count, and planned-insert count;
- report fixed score decile gain/harm rates and Spearman correlation between decile index and `(gain_rate - harm_rate)`;
- `READINESS_PUSHES_HARM_HIGH` only if readiness AUROC point < 0.5 and its 95% upper bound < 0.5;
- `MULTIPLICATION_AMPLIFIES_WRONG_DIRECTION` only if readiness is harm-high and the query-bootstrap 95% upper bound of `(score AUROC - uncertainty AUROC)` is below 0;
- `EXPANSION_SCALE_NOT_BENEFIT_SIGNAL` for a count feature only if its AUROC interval contains 0.5 and its absolute Spearman correlation with q25 inserted count is at least 0.5;
- score monotonicity is descriptive and uses all ten fixed deciles; no subrange is selected.

These flags cannot change the U1 formula.

## 9. Query-Level All-On/All-Off Mechanism Categories

For every query, define:

```text
G = q25_inserted_gold_units
N = q25_inserted_non_gold_units
T = q25_inserted_units = G + N = len(q25_inserted_unit_ids)
```

Mutually exclusive category rules, applied in this order:

1. `DISPLACEMENT_HARM_QUERY`: label is HARM. `T` must be positive.
2. `PURE_GAIN_QUERY`: label is GAIN, `G > 0`, and `N == 0`.
3. `MIXED_GAIN_NOISE_QUERY`: label is GAIN, `G > 0`, and `N > 0`.
4. `PURE_NOISE_QUERY`: label is NEUTRAL, `T > 0`, `G == 0`, and `N == T`.
5. `NO_EFFECT_QUERY`: every remaining NEUTRAL query.

A GAIN row outside rules 2–3 or a HARM row with `T == 0` is an integrity failure.

Additional fixed descriptors:

- composition: `NO_INSERT`, `GOLD_ONLY`, `MIXED_GOLD_NON_GOLD`, or `NON_GOLD_ONLY`;
- q25 inserted positions within q25 Top-20: min, mean, max;
- count of q25 inserted IDs already present in Dense Top-20 and Dense protected Top-10;
- Dense/q25 Top-20 Jaccard overlap;
- actual U1 trigger and final inserted count;
- `candidate_gold_rank_available = 0` for all rows, with the frozen reason above.

The audit may report the count of mixed/displacement event queries. It may not claim which individual candidate should have been selected, because candidate-level Gold identities are unavailable.

Fixed structural limitation flag:

```text
ALL_ON_OFF_LIMITATION_EVIDENCE = true
```

only if:

- `MIXED_GAIN_NOISE_QUERY + DISPLACEMENT_HARM_QUERY >= 33` (at least 20% of the 163 frozen gain/harm events), and
- each of those two categories contains at least 10 queries.

This is exploratory mechanism evidence, not candidate-controller efficacy.

## 10. Fixed Out-Of-Fold Learnability Probes

The implementation runs the probes only after all input, label, formula, and feature-integrity checks pass. No model selection or hyperparameter search occurs.

Tasks:

```text
Task A: GAIN vs HARM
Task B: GAIN vs non-GAIN
Task C: HARM vs non-HARM
```

Question type is never a model feature.

Three fixed feature panels are all reported; none is selected after seeing results:

```text
ORIGINAL_U1_8:
  ball_score_margin, boundary_margin, selected_edge_count,
  planned_insert_count, uncertainty, readiness, score, feasible

RANK_STRUCTURE_6:
  q25_eligible_count, q25_insert_position_min,
  q25_insert_position_mean, q25_insert_position_max,
  q25_inserted_dense20_overlap_count, dense_q25_top20_jaccard

COMBINED_14:
  union of ORIGINAL_U1_8 and RANK_STRUCTURE_6
```

Candidate IDs, Gold counts, labels, CR/ER outcomes, trigger outcome, ordered rank, and question type are forbidden probe features.

Model and preprocessing:

- regularized logistic regression implemented with NumPy;
- intercept unpenalized, L2 coefficient `lambda = 1.0` under summed log-loss;
- Newton/IRLS, maximum 100 iterations, convergence tolerance `1e-8`;
- no class weights;
- 5-fold stratified CV, seed `20260718`, deterministic class-wise shuffle and round-robin fold assignment;
- missing numeric values imputed with the training-fold median only;
- training-fold mean/standard deviation scaling only; zero-variance features map to zero;
- no preprocessing statistic may use a held-out fold.

Metrics:

- out-of-fold AUROC, AP, Brier score;
- fixed probability threshold 0.5 confusion matrix;
- 10 equal-width calibration bins on `[0,1]`, expected calibration error, and bin counts/rates;
- per-fold AUROC, AP, Brier, positive/negative counts;
- 10,000 stratified query-bootstrap 95% intervals for OOF AUROC, AP, and Brier, seed `20260718`;
- original raw U1 score AUROC/AP on the same task rows, without threshold optimization;
- Task-A per-question-type metrics when both classes have at least 5 rows;
- Task-A leave-one-question-type-out metrics computed from the already fixed OOF predictions, without refitting or type-based selection.

The script writes all OOF probabilities. Training-set performance must not be reported.

## 11. Pre-Specified Signal And Decision Rules

For a panel to have `STABLE_GAIN_HARM_SIGNAL` on Task A, all conditions must hold:

1. OOF AUROC point estimate at least 0.65 and bootstrap lower bound above 0.50;
2. OOF AP point estimate at least the observed Task-A GAIN prevalence plus 0.05, and bootstrap lower bound above that prevalence;
3. at least 4 of 5 fold AUROCs exceed 0.50;
4. every eligible leave-one-question-type-out AUROC exceeds 0.55;
5. no question-type label is included as a feature.

The final decision is assigned in this order:

### `PROCEED_TO_U2_CANDIDATE_LEVEL_PROTOCOL_DESIGN`

Only if at least one fixed panel has `STABLE_GAIN_HARM_SIGNAL` and `ALL_ON_OFF_LIMITATION_EVIDENCE == true`. This authorizes only a future Level A protocol draft, not implementation, ranking, Gold evaluation, or reservation access.

### `INSUFFICIENT_SIGNAL_STOP_CONTROLLER_LINE`

Only if all required fields and event counts are adequate, no panel meets the stable-signal rule, every panel has OOF AUROC at most 0.60 or a bootstrap interval containing 0.50, at most 2 of 5 fold AUROCs exceed 0.50, and the fixed all-on/off limitation flag is false.

### `MECHANISM_EVIDENCE_INCONCLUSIVE`

For every remaining case, including partial but unstable signal, contradictory panels, inadequate events, failed finite-feature coverage, unavailable query-level inserted composition, or inability to distinguish weak signal from insufficient evidence.

The known absence of candidate-level Gold IDs/ranks and semantic/support features must be reported as a limitation. It does not by itself force one decision if the fixed query-level composition and OOF rules are otherwise evaluable.

No decision rule may be changed after execution.

## 12. Outputs And Atomicity

The primary command is:

```powershell
& 'D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe' -B scripts/stage4c_u1_failure_mechanism_audit.py --output-dir results
```

Required absent-before-run outputs:

```text
results/stage4c_u1_fma_query_features.csv
results/stage4c_u1_fma_feature_separability.csv
results/stage4c_u1_fma_score_deciles.csv
results/stage4c_u1_fma_candidate_mechanisms.csv
results/stage4c_u1_fma_oof_predictions.csv
results/stage4c_u1_fma_summary.json
```

The implementation must build all six files in a same-directory pending area, validate row counts/schema/finite values/decision, and promote all files only after every check passes. A failure must leave all six final paths absent. Existing final paths cause a pre-run failure; no overwrite is allowed.

CSV uses UTF-8, LF, comma delimiter, a fixed declared column order, and deterministic float formatting. JSON uses sorted keys, two-space indentation, UTF-8, and LF. Query order is frozen to the decision-file order. OOF rows are ordered by task, feature panel, and query order.

The report path is:

```text
reports/超粒球RAG_Stage4C_U1失败机制诊断报告.md
```

Large per-candidate data is not generated because candidate-level target identity is unavailable. Raw data, Gold map, embeddings, caches, and restricted artifacts must not be committed.

## 13. Implementation And Test Gate

Planned implementation paths:

```text
scripts/stage4c_u1_failure_mechanism_audit.py
tests/test_stage4c_u1_failure_mechanism_audit.py
```

Before the first official diagnostic run:

1. the protocol commit must be on GitHub main;
2. implementation and tests must be committed and pushed;
3. all six final outputs must be absent;
4. targeted tests must pass once;
5. no Stage4B evaluator/controller command may run.

Tests must cover:

- exact GAIN/HARM/NEUTRAL definitions and frozen-count reconciliation;
- strict joins, duplicates, missing rows, types, finite values, and identity mismatch rejection;
- quantiles, tie-aware AUROC/AP, overlap, bootstrap determinism;
- fixed decile boundaries and cumulative arithmetic;
- formula reconstruction and mechanism category priority;
- per-fold imputation/scaling without held-out leakage;
- deterministic stratified folds, logistic OOF output, calibration, and decision rules;
- forbidden Gold/ID/type/trigger features;
- exact seven-path read allowlist and absence of reservation/Stage3B/Gold-map paths;
- atomic no-overwrite outputs and deterministic synthetic output bytes.

No repository-wide Stage4B suite is required because Stage4B code is not modified. Run the new Stage4C targeted suite only.

## 14. Monitoring And Stop Rules

- Runtime class: deterministic CPU analysis.
- Timeout: 30 minutes.
- Monitor: process alive plus the six registered output paths.
- Expected behavior: no final output until atomic promotion.
- Never auto-retry a crashed or failed official diagnostic.

Immediate stop and report if:

- a frozen input hash, row identity, count, or Stage4B decision differs;
- any code path requires Gold map, evaluator audit, reservation, Stage3B, corpus, embeddings, or cache;
- the evaluator/controller would need to run;
- a scientific definition or decision rule needs post-result modification;
- any Stage4B artifact changes;
- a formal Stage4C output is partial or inconsistent.

## 15. Interpretation Boundary

The report must separate:

- pre-specified analysis from supplementary description;
- query-level feature separability from controller performance;
- OOF probe learnability from efficacy;
- observable inserted composition from unavailable per-candidate Gold rank;
- evidence from inference and future hypotheses.

The final report must run the academic-research-suite 11-type statistical fallacy scan and deterministic-output checks. It must retain these statements:

```text
Stage4B-U1-D remains a valid negative result.
Reservation remains locked.
No new controller efficacy has been established.
```

If the decision is `PROCEED_TO_U2_CANDIDATE_LEVEL_PROTOCOL_DESIGN`, Stage4C may only recommend creating `docs/STAGE5A_U2_DEVELOPMENT_PROTOCOL_DRAFT.md` in a later separately authorized scientific-design step. It must not create or implement that protocol within this transaction.
