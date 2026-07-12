# 超粒球RAG Stage4A-R2 统计与复现验证报告

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Mode: validate
- Date: 2026-07-12
- Verification Status: VERIFIED
- Active protocol: `docs/STAGE4A_R2_PROTOCOL.md` + `docs/STAGE4A_R2_AMENDMENT_1.md`
- Evidence boundary: current conversation, current repository, official April 7 archive, and project-local experiment artifacts
- Other project conversations, global memory, and project-external threads used: No

## Validation Verdict

- Computational verdict: `EXACTLY_REPRODUCIBLE`.
- Primary estimation verdict: `ESTIMATION_COMPLETE`.
- Primary internal confidence: `SOLID_WITHIN_AUDITED_QC_SAMPLE`.
- Generalization confidence: `CAUTION`; the sample uses a deterministic contiguous base pool with documented label-completeness replacement.
- Secondary average CR@20 improvement: `NOT_CONFIRMED`.
- Controller training: `NOT_AUTHORIZED_BY_STAGE4A_R2`.

Stage4A-R2 successfully estimates official q25 gain and harm prevalence with the predeclared precision. It does not establish that q25 improves mean CR@20 by the predeclared practically meaningful 1 percentage point.

## Integrity And Reproduction

| Check | Result |
|---|---|
| Official archive / `dev.json` SHA | Matched frozen values |
| Final development / reservation | 4,500 / 4,500 unique IDs, zero overlap |
| Amendment 1 | 19 base failures, replacements `[9800:9819)`, zero replacement failures |
| Supporting facts | 11,015/11,015 mapped; zero missing-gold queries |
| Gold-title ambiguity | Zero supporting facts attached to duplicated context titles |
| Corpus | 143,820 units, 11,015 gold units |
| Query audit | 4,500 unique IDs and zero duplicate normalized questions |
| Independent output verifier | Passed summary, inference, bootstrap, and report checks |
| Deterministic rerun | Four core artifacts matched byte-for-byte |
| Reservation metrics | Not accessed |

Core SHA-256 values:

| Artifact | SHA-256 |
|---|---|
| Query audit | `766D7344A8093D2CBA10507B0DEE83A42575D9EDE986DD3212822BC96701034A` |
| Strategy summary | `7BF79CC057CDD0565100B1D95F35C95BFBEAA338E9B1EF63D9E81F029BB42B12` |
| Bootstrap | `FF1D47BBCDF969C7CCDFCF66FA5AAFB1F655C3393590C492C33E46C5C706F5F0` |
| Inference | `9AE75704BDC18628AD13BE29FBEF5CC42A498478D5DE02154BC5B10ECCD7A38F` |

The first source extraction hard failure and the later PowerShell hash-display syntax error are documented. Neither produced or changed retrieval metrics.

## Primary Estimates

| Event | Count | Prevalence | Wilson 95% CI | Half-width | Precision gate |
|---|---:|---:|---:|---:|---|
| q25 gain | 94/4,500 | 0.020889 | [0.017101, 0.025494] | 0.004197 | PASS |
| q25 harm | 69/4,500 | 0.015333 | [0.012134, 0.019359] | 0.003612 | PASS |

Both half-widths are below the frozen `0.005` target. The gain and harm events are therefore available at measurable, non-zero rates in this official QC sample.

## Secondary Results

| Comparison | Endpoint | Delta | Interval / test | Interpretation |
|---|---|---:|---|---|
| q25 vs dense | CR@20 | +0.005556 | Bootstrap [0.000000, 0.011111]; exact McNemar `p=0.05980` | Not confirmed at alpha 0.05; observed effect is below the planned +0.01 practical target |
| q25 vs dense | ER@20 | +0.004067 | Bootstrap [0.001467, 0.006744] | Small positive descriptive effect |
| unfiltered vs dense | CR@20 | -0.000222 | Bootstrap [-0.006444, 0.006000] | No net benefit |
| q25 vs unfiltered | CR@20 | +0.005778 | Bootstrap [0.003111, 0.008667] | Frozen filtering descriptively improves indiscriminate expansion |

Dense fixed CR@20 is `0.77222`, so the official QC sample is not saturated. q25 changes CR@20 to `0.77778`, with 94 gains and 69 harms. The non-significant McNemar result must not be reframed as a trend or proof of improvement.

## Cost And Noise

- q25 trigger rate: `0.54356`.
- Average inserted units/query: `1.61333`.
- Conditional false-insert rate: `0.92163`.
- Insert yield: `0.07837`.
- Completion opportunities: `707`; completion precision: `0.13296`.
- The q25 floor removed 2,859 candidates.

q25 is more selective than unfiltered expansion, but the remaining inserted units are still predominantly non-gold. Stage4A-R2 does not support a claim that insertion noise is solved.

## Descriptive Heterogeneity

| Type | Queries | Gain | Harm | Net | q25 minus dense CR@20 |
|---|---:|---:|---:|---:|---:|
| bridge_comparison | 1,001 | 35 | 20 | +15 | +0.01499 |
| comparison | 1,132 | 31 | 6 | +25 | +0.02208 |
| compositional | 1,789 | 23 | 26 | -3 | -0.00168 |
| inference | 578 | 5 | 17 | -12 | -0.02076 |

These rows were predeclared as descriptive. They show that the pooled positive delta combines two positive and two non-positive type strata. Benchmark type labels must not be used as a deployable controller input without a separate protocol and inference-time type mechanism.

## Amendment Sensitivity

- Nineteen replacement rows contributed zero q25 gains and zero q25 harms.
- The 4,481 valid base rows contain all 94 gains and 69 harms.
- Invalid base records were 11 compositional and 8 inference queries; replacements were 4 compositional, 2 inference, 7 comparison, and 6 bridge-comparison queries.
- The amendment therefore did not create the observed net gain, but it slightly changes the question-type mix. Inference is restricted to the final audited QC sample.

## Assumption And Multiplicity Audit

- Pairing: every strategy is evaluated on the same 4,500 queries.
- Binary paired test: exact conditional McNemar avoids large-sample normal approximation for CR discordances.
- Independence: query IDs and normalized question texts are unique; shared benchmark contexts may still make strict query independence approximate.
- Interval target: Wilson intervals are appropriate for the predeclared binomial event-rate estimands.
- Multiplicity: one secondary McNemar test was predeclared. Question-type rows and six bootstrap comparisons are descriptive and receive no confirmatory significance interpretation.
- Practical significance: observed CR@20 delta `0.00556` is below the planned `0.01` minimum net gain.

## Statistical Fallacy Scan

Coverage: 11/11 checked.

| Fallacy | Result |
|---|---|
| Simpson's paradox | No full direction reversal across every stratum, but pooled positive CR masks negative inference and compositional net outcomes; stratified reporting is mandatory. |
| Ecological fallacy | Not detected; primary events are query-level. Type-level summaries are not used to infer individual-query benefit. |
| Berkson's paradox | Not detected as a correlation claim. Label-completeness QC is a documented selection boundary and limits generalization. |
| Collider bias | Not detected; no causal adjustment model is fitted. |
| Base-rate neglect | Avoided for primary claims by reporting gain/harm prevalence, opportunities, completion precision, and false-insert rate. |
| Regression to the mean | Not applicable; there is no extreme-score pre/post selection. |
| Survivorship bias | No hidden attrition. Nineteen ineligible base records and all replacements are explicitly audited. |
| Look-elsewhere effect | Primary estimands and one McNemar test were frozen. Type and bootstrap comparisons remain descriptive. |
| Garden of forking paths | R2 protocol and execution code preceded metrics; Amendment 1 was approved and committed after source QC failure but before embeddings or outcomes. |
| Correlation implies causation | Paired strategy effects are valid for the audited benchmark sample; no broader causal claim about real-world RAG is allowed. |
| Reverse causality | Not applicable to the paired retrieval intervention. |

## Permitted Conclusions

1. Official 2Wiki provides measurable gain and harm events for the frozen q25 protected-insertion policy in the audited QC sample.
2. Dense CR@20 is not saturated in that sample.
3. q25 is descriptively better than unfiltered expansion and reduces harms from 102 to 69 while retaining 94 gains.
4. The average q25-versus-dense CR@20 improvement is not confirmed at alpha 0.05 and is smaller than the planned 1 percentage point practical target.
5. Strong type heterogeneity and high false-insert rate justify research on a new, low-complexity query-level decision model, but Stage4A-R2 itself does not validate or authorize that model.
