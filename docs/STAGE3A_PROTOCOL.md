# Stage3A Utility-Calibrated Controller Development Protocol

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: plan
- Origin Date: 2026-07-11
- Verification Status: UNVERIFIED
- Version Label: code_plan_v1
- Protocol Status: FROZEN BEFORE DEVELOPMENT METRICS

## Experiment Overview

- **Title**: Development of a query-level expected-utility controller for protected hyperedge insertion
- **Objective**: Replace the broad Stage2G OR rule with an interpretable controller that estimates whether q25 protected insertion is likely to improve rather than harm CR@20.
- **Hypothesis**: A multivariate controller using label-free retrieval and granular-ball signals can retain most useful chain completions while reducing unnecessary non-gold insertions relative to all-query expansion.
- **Type**: analysis and deterministic model development

Stage3A is a development experiment. It may select model parameters and an operating threshold only within the declared development slice. It cannot provide the final confirmatory result.

## Source Audit And Data Reservation

| Dataset | Source | Rows | SHA-256 |
|---|---|---:|---|
| HotpotQA | `hotpot_dev_distractor_v1.json` | 7,405 | `E3DA074DF24E8369009918AA5CDBDD254DADCDE4C63F7569D36AFD6F2268CAA8` |
| MuSiQue | `musique/data/musique_ans_v1.0_dev.jsonl` | 2,417 | `15FA63794D18A94CE12411ACA6E2327E65B6E83B0B1490EFAB3F1962E48ABF3B` |

Frozen source-row boundaries:

| Role | HotpotQA rows | MuSiQue rows | Queries | Metric access |
|---|---|---|---:|---|
| Prior Stage2E-H evidence | `[0:600)` | `[0:600)` | 1,200 | Already observed |
| Stage3A development | `[600:1000)` | `[600:1000)` | 800 | Allowed after this protocol is committed |
| Stage3B frozen test | `[1000:1400)` | `[1000:1400)` | 800 | Prohibited until the Stage3A controller is frozen |

All query IDs must be pairwise disjoint across prior, development, and reserved-test ranges. Missing mapped gold evidence is a hard failure and must not be replaced by later rows.

## Development Split

The 800 Stage3A queries are divided within each dataset by sorting the SHA-256 digest of `stage3a_split_20260713::<query_id>`:

- First 60% per dataset: model-fitting partition, 240 HotpotQA + 240 MuSiQue = 480 queries.
- Remaining 40% per dataset: threshold-selection partition, 160 HotpotQA + 160 MuSiQue = 320 queries.
- Dataset identity is not a model feature.
- No Stage3B query may be embedded, scored, or used to handle a development failure.

## Frozen Retrieval Counterfactual

- Dense model: `sentence-transformers/all-MiniLM-L6-v2`
- Candidate construction: existing all-query gated-hyperedge expansion
- Candidate score floor: Stage2E q25 = `0.1957079917192459`
- Protection zone: dense Top-10
- Insertion budget: 4 units into ranks 11-20
- Maximum evaluation depth: 20
- Gold labels are used only after rankings are produced to construct development outcomes and metrics

## Controller Inputs

Only the following signals, all available before gold evaluation, are permitted:

1. `top_ball_score`
2. `ball_score_margin`
3. `top_ball_radius`
4. `query_to_top_ball_distance`
5. `boundary_margin`
6. `log1p(num_candidates)`
7. `log1p(selected_edge_count)`
8. `log1p(raw_candidate_count)`
9. `log1p(filtered_candidate_count)`

Continuous features are standardized using fitting-partition means and standard deviations only. A zero-variance feature is set to zero after centering. Query ID, dataset ID, question text, gold count, gold insertions, retrieval outcomes, and Stage2E-H labels are prohibited features.

## Model And Utility Score

Two deterministic L2-regularized logistic heads are fitted with NumPy:

- Gain head target: `1` when all-query q25 insertion has `delta_chain_recall_at_20 > 0`, otherwise `0`.
- Harm head target: `1` when all-query q25 insertion has `delta_chain_recall_at_20 < 0`, otherwise `0`.
- Regularization: lambda `1.0`; intercept is not penalized.
- Optimizer: Newton updates, maximum 100 iterations, coefficient-change tolerance `1e-9`.
- Utility score: `P(gain) - P(harm)`, corresponding to expected signed CR@20 change.

If either target has fewer than 5 positive or fewer than 5 negative fitting examples, that head falls back to a Laplace-smoothed intercept-only probability `(positives + 1) / (n + 2)`. This fallback must be reported.

## Frozen Comparators

| Strategy | Role |
|---|---|
| `dense_fixed` | No-insertion retrieval baseline |
| `allquery_q25_p10_i4` | Maximum-coverage protected-insertion control |
| `stage2g_or_q25_p10_i4` | Failed frozen OR boundary rule |
| `score_margin_q25_p10_i4` | Strongest Stage2H single-component diagnostic baseline using the unchanged `<= 0.10` rule |
| `utility_controller_q25_p10_i4` | Stage3A learned selector |

## Threshold Selection

Candidate finite thresholds are the sorted unique utility scores above the minimum observed score on the 320-query threshold-selection partition, applied with `utility_score >= threshold`. Explicit expand-none and expand-all endpoints are evaluated separately; this prevents the minimum finite threshold from silently duplicating expand-all.

Thresholds are selected lexicographically:

1. Retain at least 80% of the successful CR@20 improvements produced by all-query expansion on the threshold-selection partition.
2. Among eligible thresholds, minimize inserted non-gold units.
3. Break ties by fewer harm events, then more successful improvements, then fewer triggered queries, then the higher threshold.
4. If no finite threshold retains 80% of improvements, use the expand-all endpoint and mark controller development as failed.

The selected threshold and fitted coefficients are frozen after Stage3A and must be serialized before any Stage3B metric is computed.

## Development Metrics

Report fitting and threshold-selection partitions separately, plus dataset-specific rows:

- ER@20 and CR@20
- Delta ER@20 and delta CR@20 versus dense fixed and all-query expansion
- Trigger rate and average inserted units
- Inserted gold and non-gold units per query
- False insert rate and insertion yield
- Successful completion count, harm count, and net completed-chain change
- Gain-head and harm-head AUROC and average precision
- Controller coefficient table, standardization statistics, fallback status, and selected threshold

Bootstrap intervals on the threshold-selection partition are descriptive because the threshold is selected on that partition:

- 10,000 paired resamples stratified by dataset
- Seed: `20260713`
- Percentile 95% confidence intervals
- No p-values or confirmatory significance language

## Promotion Gate To Stage3B

Stage3A qualifies for a separately frozen Stage3B evaluation only if all observed threshold-selection conditions hold:

1. At least 80% of all-query successful CR@20 improvements are retained.
2. Non-gold inserted units per query fall by at least 20% relative to all-query expansion.
3. Controller CR@20 is no more than 0.01 below all-query CR@20.
4. Controller net completed-chain change relative to dense fixed is positive.
5. The controller does not reduce to expand-all, and no target head uses the sparse-target fallback.

Failure of this gate ends the current controller branch. It must not trigger inspection of Stage3B labels or post-hoc modification on the reserved test slice.

## Expected Outputs

| Output | Path | Format | Success Criterion |
|---|---|---|---|
| Stage3A unified slices | Local processed-data directory | JSON | 400 rows per dataset at frozen offsets |
| Stage3A units and queries | Local processed-data directory | JSONL | 800 queries, zero prior overlap, zero missing gold |
| Stage3A embeddings | Local processed-data directory | NPZ | Dimensions match corpus and model metadata |
| Query audit | `results/stage3a_utility_controller_query_audit.csv` | CSV | 800 rows with split, features, outcomes, scores, and strategy decisions |
| Model artifact | `results/stage3a_utility_controller_model.json` | JSON | Feature order, scaling, coefficients, fallback flags, and threshold |
| Strategy summary | `results/stage3a_utility_controller_summary.csv` | CSV | Partition and dataset metrics for all frozen comparators |
| Bootstrap audit | `results/stage3a_utility_controller_bootstrap.csv` | CSV | Declared threshold-selection contrasts and 10,000-resample CIs |
| Run report | `reports/超粒球RAG_Stage3A_UtilityController开发报告.md` | Markdown | Material Passport, audits, metrics, promotion decision, and interpretation boundary |

## Monitoring Configuration

- Timeout: 30 minutes for extraction/corpus steps and 60 minutes for embedding or controller analysis
- Monitor only declared Stage3A outputs and existing Stage2 calibration artifacts
- Hard failures: source hash mismatch, wrong row count, any prior/test overlap, missing mapped gold, q25 mismatch, embedding/corpus mismatch, prohibited feature use, non-convergence without declared fallback, or non-zero exit code

## Interpretation Boundary

Stage3A can develop and freeze a controller and decide whether it is eligible for Stage3B. Because model fitting and threshold selection occur on Stage3A labels, all Stage3A performance estimates are developmental. Only the untouched Stage3B slice can support a confirmatory controller claim.
