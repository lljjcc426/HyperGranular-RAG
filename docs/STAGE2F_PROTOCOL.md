# Stage2F Frozen-Threshold Independent Validation Protocol

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: plan
- Origin Date: 2026-07-10
- Verification Status: UNVERIFIED
- Version Label: code_plan_v1
- Protocol Status: FROZEN BEFORE TEST EVALUATION

## Experiment Overview

- Title: Frozen-threshold validation of protected hyperedge evidence completion
- Objective: Test whether Stage2E retrieval gains and insertion-noise trade-offs reproduce on queries not used by Stage2E.
- Hypothesis: A mild calibration-derived dense-score floor preserves protected evidence-completion gains while reducing non-gold insertions.
- Type: analysis

## Data Boundary

Calibration data already used in Stage2E:

- HotpotQA dev distractor raw rows `[0:200)`
- MuSiQue answerable dev raw rows `[0:200)`

Independent Stage2F test data:

- HotpotQA dev distractor raw rows `[200:400)`
- MuSiQue answerable dev raw rows `[200:400)`

The test slice is deterministic and must not be changed after metrics are seen. Query IDs must have zero overlap with the Stage2E calibration corpus. All selected queries are retained; missing or unmapped gold evidence counts must be reported rather than silently replaced.

## Frozen Retrieval Configuration

- Dense model: `sentence-transformers/all-MiniLM-L6-v2`
- Granular-ball and gated-hyperedge parameters: identical to Stage2E defaults
- Boundary-only expansion: enabled
- Score q25 floor from Stage2E calibration candidates: `0.1957079917192459`
- Score q50 floor from Stage2E calibration candidates: `0.31666630506515503`
- Test-set candidate quantiles must not be used to alter either floor
- Gold labels must not affect indexing, filtering, ranking, or threshold selection

Frozen strategies:

| Strategy ID | Filter | Protect | Insert | Role |
|---|---|---:|---:|---|
| `dense_fixed` | none | 0 | 0 | Primary baseline |
| `unfiltered_p5_i2` | none | 5 | 2 | Stage2D reference |
| `unfiltered_p5_i4` | none | 5 | 4 | Matched control for q25 Top-10 test |
| `score_q25_p5_i4` | score >= 0.1957079917 | 5 | 4 | Primary Stage2F strategy |
| `unfiltered_p10_i4` | none | 10 | 4 | Matched control for q25 Top-20 test |
| `score_q25_p10_i4` | score >= 0.1957079917 | 10 | 4 | Secondary long-context strategy |
| `score_q50_p5_i2` | score >= 0.3166663051 | 5 | 2 | Secondary noise-control strategy |

The Stage2E `score_q50 + facet_q50` row is excluded because its low insertion coverage made it unsuitable for a confirmatory noise-control claim.

## Analysis Plan

Primary endpoint:

- Paired query-level delta in `chain_recall_at_10` for `score_q25_p5_i4` versus `dense_fixed` on the combined 400-query test set.

Primary support rule:

- Observed delta must be positive and the stratified paired-bootstrap 95% percentile CI lower bound must be at least zero.

Secondary endpoints:

- `score_q25_p5_i4` versus `unfiltered_p5_i4`: false-insert-rate delta must be negative while CR@10 delta is non-negative.
- `score_q25_p10_i4` versus `dense_fixed`: observed CR@20 delta must be positive with a 95% CI lower bound at least zero.
- `score_q50_p5_i2` versus `unfiltered_p5_i2`: report false-insert and CR@10 deltas without promoting this exploratory comparison to a primary claim.
- Report ER@10, ER@20, CR@10, CR@20, context tokens, average inserted units, and false insert rate for every frozen strategy.

Bootstrap procedure:

- 10,000 paired resamples
- Seed: `20260710`
- Combined-set resampling is stratified by dataset to preserve the 200/200 mixture
- Dataset-specific intervals are also reported
- Percentile 95% CIs; no p-values and no family-wise significance claim

## Expected Outputs

| Output | Path | Format | Success Criterion |
|---|---|---|---|
| Test units | local processed data directory | JSONL | 400-query corpus builds with zero ID overlap |
| Test embeddings | local processed data directory | NPZ | Cache exists and matches test corpus dimensions |
| Strategy summary | `results/stage2f_frozen_threshold_summary.csv` | CSV | ALL, HotpotQA, and MuSiQue rows present |
| Bootstrap comparisons | `results/stage2f_frozen_threshold_bootstrap.csv` | CSV | Frozen comparisons and 10,000-resample CIs present |
| Validation report | `reports/超粒球RAG_Stage2F_FrozenThreshold验证报告.md` | Markdown | Material Passport, data audit, metrics, and decision gates present |

## Monitoring Configuration

- Timeout: 30 minutes per command
- Monitor files: only the declared Stage2F processed-data, embedding-cache, result, and report paths
- Experiment type: analysis
- Hard failure conditions: non-zero query-ID overlap, missing test slice, zero evaluable queries, embedding/corpus dimension mismatch, or non-zero process exit code

## Interpretation Boundary

Stage2F is an independent query-level validation within the same two source datasets and the same dense encoder. It does not establish cross-dataset or cross-encoder generalization, and it does not evaluate answer generation quality.
