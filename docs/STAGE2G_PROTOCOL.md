# Stage2G Boundary-Decision Mechanism Audit Protocol

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: plan
- Origin Date: 2026-07-10
- Verification Status: UNVERIFIED
- Version Label: code_plan_v1
- Protocol Status: FROZEN BEFORE TEST EVALUATION

## Experiment Overview

- Title: Independent audit of boundary uncertainty as a retrieval trigger
- Objective: Test whether the existing boundary decision improves the precision of protected hyperedge insertion relative to applying the same expansion policy to every query.
- Hypothesis: Boundary-only triggering reduces false insertions while remaining non-inferior in evidence-chain recall.
- Type: analysis

## Data Boundary

Previously evaluated source slices:

- Stage2E calibration: HotpotQA and MuSiQue raw rows `[0:200)`
- Stage2F independent validation: HotpotQA and MuSiQue raw rows `[200:400)`

Independent Stage2G test slice:

- HotpotQA dev distractor raw rows `[400:600)`
- MuSiQue answerable dev raw rows `[400:600)`

The test slice is deterministic and must not be changed after metrics are seen. Stage2G query IDs must have zero overlap with both earlier slices. All selected queries are retained; missing mapped gold evidence must be reported rather than silently replaced.

## Frozen Retrieval Configuration

- Dense model: `sentence-transformers/all-MiniLM-L6-v2`
- Score floor: Stage2E calibration q25 = `0.1957079917192459`
- Granular-ball, facet-hyperedge, and gate parameters: identical to Stage2F
- Gold labels must not affect indexing, boundary classification, candidate filtering, ranking, or threshold selection
- No q50, facet-floor, or new threshold configuration is allowed in Stage2G

Frozen strategies:

| Strategy ID | Boundary Policy | Protect | Insert | Role |
|---|---|---:|---:|---|
| `dense_fixed` | none | 0 | 0 | Retrieval baseline |
| `allquery_q25_p5_i4` | expand eligible candidates for every query | 5 | 4 | Top-10 matched control |
| `boundary_q25_p5_i4` | expand only boundary queries | 5 | 4 | Top-10 boundary policy |
| `allquery_q25_p10_i4` | expand eligible candidates for every query | 10 | 4 | Top-20 matched control |
| `boundary_q25_p10_i4` | expand only boundary queries | 10 | 4 | Primary boundary policy |

## Mechanism Metrics

- Trigger rate: queries with at least one inserted unit divided by all queries.
- False insert rate: inserted non-gold units divided by all inserted units.
- Completion precision at K: among triggered queries whose dense-fixed chain is incomplete at K, the share whose strategy retrieves the complete chain at K.
- Harm rate at K: among triggered queries whose dense-fixed chain is complete at K, the share whose strategy makes the chain incomplete at K.
- Boundary prevalence and dataset-specific trigger coverage must be reported.

## Analysis Plan

Primary policy comparison:

- `boundary_q25_p10_i4` versus `allquery_q25_p10_i4`.
- False-insert delta must be negative with the stratified paired ratio-bootstrap 95% CI upper bound below zero.
- CR@20 non-inferiority margin is `-0.01`; the paired-bootstrap 95% CI lower bound for boundary minus all-query must be at least `-0.01`.
- The primary mechanism gate is supported only if both conditions hold.

Secondary policy comparison:

- `boundary_q25_p5_i4` versus `allquery_q25_p5_i4`.
- Apply the same false-insert condition and a CR@10 non-inferiority margin of `-0.01`.

Predictive mechanism comparison:

- Under `allquery_q25_p10_i4`, compare completion precision at 20 between boundary and non-boundary queries.
- Support requires a positive boundary-minus-non-boundary delta with 95% CI lower bound at least zero.
- Harm-rate differences are descriptive because the number of baseline-complete triggered queries may be small.

Bootstrap procedure:

- 10,000 resamples
- Seed: `20260711`
- ALL resampling is stratified by dataset
- Policy comparisons are paired at query level
- Ratio statistics are recomputed within every resample
- Percentile 95% CIs; no p-values and no family-wise significance claim

## Expected Outputs

| Output | Path | Format | Success Criterion |
|---|---|---|---|
| Test units and queries | local processed data directory | JSONL | 400 queries, zero prior-slice overlap, zero missing mapped gold |
| Test embeddings | local processed data directory | NPZ | Cache dimensions match the Stage2G corpus |
| Strategy summary | `results/stage2g_boundary_mechanism_summary.csv` | CSV | ALL, HotpotQA, and MuSiQue rows for five frozen strategies |
| Bootstrap audit | `results/stage2g_boundary_mechanism_bootstrap.csv` | CSV | Frozen policy and predictive comparisons with 10,000-resample CIs |
| Run report | `reports/超粒球RAG_Stage2G_BoundaryMechanism报告.md` | Markdown | Material Passport, overlap audit, metrics, and frozen gate decisions |

## Monitoring Configuration

- Timeout: 30 minutes per command
- Monitor files: only declared Stage2G processed data, embedding cache, CSV, and report paths
- Experiment type: analysis
- Hard failure conditions: prior-slice overlap, unexpected dataset counts, missing mapped gold, frozen-floor mismatch, embedding/corpus mismatch, or non-zero exit code

## Interpretation Boundary

Stage2G tests whether the current boundary rule is a useful selective trigger under one encoder, one q25 filter, and two existing datasets. It does not optimize the boundary thresholds, establish cross-encoder generalization, or evaluate generated answers.
