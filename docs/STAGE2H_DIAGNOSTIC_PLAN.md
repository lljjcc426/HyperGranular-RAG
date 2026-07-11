# Stage2H Boundary-Rule Failure Diagnosis Plan

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: plan
- Origin Date: 2026-07-11
- Verification Status: UNVERIFIED
- Version Label: code_plan_v1
- Analysis Status: EXPLORATORY POST-HOC DIAGNOSIS

## Experiment Overview

- Title: Component-level diagnosis of the failed OR-composed boundary rule
- Objective: Identify which uncertainty condition causes the 81% boundary prevalence and whether any current component contains useful benefit-prediction signal.
- Hypothesis: None is treated as confirmatory; all associations are exploratory after the Stage2G mechanism-gate failure.
- Type: analysis

## Inputs

| Slice | Source Rows | Queries | Embedding Cache |
|---|---|---:|---|
| Stage2E | HotpotQA/MuSiQue `[0:200)` | 400 | `stage2_dense_allminilm_embeddings.npz` |
| Stage2F | HotpotQA/MuSiQue `[200:400)` | 400 | `stage2f_dense_allminilm_embeddings.npz` |
| Stage2G | HotpotQA/MuSiQue `[400:600)` | 400 | `stage2g_dense_allminilm_embeddings.npz` |

The three slices must remain pairwise disjoint. Stage2H reuses already evaluated queries and therefore does not provide a new independent test.

## Frozen Retrieval Counterfactual

- Dense model: `sentence-transformers/all-MiniLM-L6-v2`
- Expansion policy: all-query gated-hyperedge candidate construction without boundary suppression
- Score floor: Stage2E q25 = `0.1957079917192459`
- Protection/insertion: protect `10`, insert budget `4`
- Target retrieval metric: CR@20
- Gold labels are used only after ranking to identify completion benefit, harm, and false insertions

## Existing OR Components

| Component | Condition | Short ID |
|---|---|---|
| Radius boundary | `boundary_margin <= 0.50` | `radius` |
| Competing-ball ambiguity | `ball_score_margin <= 0.10` | `score_margin` |
| Low top-ball confidence | `top_ball_score < 0.20` | `low_top_score` |
| Current gate | logical OR of all three conditions | `or_gate` |

All seven non-empty component-overlap masks must be reported. No threshold may be added, removed, or tuned in Stage2H.

## Diagnostic Metrics

- Component prevalence and exclusive-overlap prevalence
- Trigger rate and average inserted units under the all-query q25 counterfactual
- False insert rate and insertion yield
- Completion opportunity: triggered query with dense-fixed CR@20 = 0
- Completion precision: share of completion opportunities reaching CR@20 = 1
- Harm opportunity: triggered query with dense-fixed CR@20 = 1
- Harm rate: share of harm opportunities falling to CR@20 = 0
- Net CR@20 delta versus dense fixed
- AUROC and average precision for each continuous uncertainty score when predicting successful completion among triggered, baseline-incomplete queries

Continuous scores are oriented so larger means more uncertain:

- `-boundary_margin`
- `-ball_score_margin`
- `-top_ball_score`

## Statistical Procedure

- 10,000 stratified bootstrap resamples
- Seed: `20260712`
- Resampling strata: slice x dataset
- For each binary component, compare true versus false completion precision, harm rate, and false insert rate
- Report percentile 95% CIs without p-values
- No multiple-comparison correction; every interval is exploratory and must be labelled as such

## Expected Outputs

| Output | Path | Format | Success Criterion |
|---|---|---|---|
| Query audit | `results/stage2h_boundary_query_audit.csv` | CSV | 1,200 aligned query rows with component flags and retrieval outcomes |
| Component summary | `results/stage2h_boundary_component_summary.csv` | CSV | OR components, true/false groups, and overlap masks reported |
| Predictive metrics | `results/stage2h_boundary_predictive_metrics.csv` | CSV | AUROC/AP and bootstrap component contrasts present |
| Diagnostic report | `reports/超粒球RAG_Stage2H_BoundaryFailureDiagnosis报告.md` | Markdown | Material Passport, coverage decomposition, predictive audit, and interpretation boundary |

## Monitoring Configuration

- Timeout: 30 minutes
- Experiment type: analysis
- Monitor only declared Stage2H CSV/report paths and the three existing embedding caches
- Hard failure conditions: slice overlap, unexpected query counts, frozen-floor mismatch, embedding/corpus mismatch, missing mapped gold, or non-zero exit code

## Interpretation Boundary

Stage2H may explain why the current boundary rule failed and may motivate a new development-stage controller. It cannot validate a replacement rule, because all outcome labels in these 1,200 queries have already been observed during Stage2E-F-G.
