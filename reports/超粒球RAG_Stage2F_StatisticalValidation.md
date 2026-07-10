# Stage2F Statistical Validation Report

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validate
- Origin Date: 2026-07-10
- Verification Status: VERIFIED
- Version Label: validation_v1

## Validation Report

- Source: `stage2f_frozen_threshold_unseen400`
- Protocol: `docs/STAGE2F_PROTOCOL.md`, committed as `229d0f6` before test evaluation
- Overall Confidence: CAUTION
- Reproducibility class: deterministic
- Unit of analysis: query
- Test set: 400 unseen queries, 200 HotpotQA and 200 MuSiQue

### Statistical Findings

| Finding | Test | Value | Effect Size | Confidence |
|---|---|---:|---|---|
| Primary q25 p5/i4 vs dense fixed CR@10 | Stratified paired bootstrap, 10,000 resamples | delta 0.0175, 95% CI [-0.0125, 0.0475] | +1.75 percentage points; small and uncertain | CAUTION |
| q25 p5/i4 vs unfiltered p5/i4 false insert | Stratified paired ratio bootstrap, 10,000 resamples | delta -0.0129, 95% CI [-0.0206, -0.0055] | -1.29 percentage points; small | CAUTION |
| q25 p5/i4 vs unfiltered p5/i4 CR@10 | Stratified paired bootstrap, 10,000 resamples | delta 0.0075, 95% CI [-0.0075, 0.0225] | +0.75 percentage points; uncertain | CAUTION |
| q25 p10/i4 vs dense fixed CR@20 | Stratified paired bootstrap, 10,000 resamples | delta 0.0175, 95% CI [0.0025, 0.0350] | +1.75 percentage points; small | CAUTION |
| Exploratory q50 p5/i2 vs unfiltered p5/i2 false insert | Stratified paired ratio bootstrap, 10,000 resamples | delta -0.0512, 95% CI [-0.0783, -0.0259] | -5.12 percentage points; moderate retrieval trade-off | CAUTION |
| Exploratory q50 p5/i2 vs unfiltered p5/i2 CR@10 | Stratified paired bootstrap, 10,000 resamples | delta -0.0025, 95% CI [-0.0200, 0.0125] | -0.25 percentage points; uncertain | CAUTION |

The pre-registered primary support rule was not met because the CR@10 interval includes zero. The q25 noise gate was met under its frozen rule: false insert decreased and the observed CR@10 delta was non-negative. The long-context CR@20 gate was met, but its dataset split shows HotpotQA delta +0.0350 with CI [0.0050, 0.0700] and MuSiQue delta 0.0000 because MuSiQue CR@20 was already 1.0000.

### Base-Rate Context

| Dataset | Candidate Units | Gold Units | Gold Base Rate | q25 p5/i4 Insert Yield |
|---|---:|---:|---:|---:|
| HotpotQA | 8,334 | 482 | 0.0578 | 0.1043 |
| MuSiQue | 3,999 | 400 | 0.1000 | 0.0602 |
| ALL | 12,333 | 882 | 0.0715 | 0.0912 |

The ALL q25 insertion yield is above the corpus candidate gold base rate, but the relationship reverses by dataset: it is higher than base rate on HotpotQA and lower on MuSiQue. This limits any dataset-general noise-suppression claim.

### Warnings

| Type | Detail | Affected |
|---|---|---|
| Primary uncertainty | The primary CR@10 CI crosses zero, so the confirmatory recall claim is not supported. | Primary endpoint |
| Small effects | Supported retrieval deltas are 1.29-1.75 percentage points. Practical value must be assessed with downstream generation and cost. | q25 noise and CR@20 gates |
| Dataset saturation | MuSiQue dense fixed CR@20 is 1.0000, so combined Top-20 gains are entirely attributable to HotpotQA. | CR@20 |
| Dataset heterogeneity | q25 false-insert reduction is clear for HotpotQA but the MuSiQue CI includes zero; insertion yield is below MuSiQue's candidate gold base rate. | Noise-control claim |
| Multiple comparisons | The CSV contains 69 bootstrap intervals. One primary endpoint and frozen decision gates were specified; remaining secondary/exploratory intervals have no family-wise correction. | Secondary and exploratory findings |
| Scope | Queries are independent of Stage2E but come from later slices of the same two dev sets and use the same encoder. | External validity |

### Fallacy Scan

- Coverage: 11/11 fallacy types checked

| Fallacy | Severity | Detail | Recommendation |
|---|---|---|---|
| Simpson's Paradox | NOTE | Primary CR@10 deltas are positive in both datasets, so no direction reversal occurs. The long-context effect is present only in HotpotQA because MuSiQue is saturated. | Always retain dataset-split reporting beside ALL. |
| Ecological Fallacy | NOTE | Metrics and paired resampling operate at query level, matching the unit of inference. | Do not generalize query-level retrieval effects to users or deployed systems. |
| Berkson's Paradox | CAUTION | Both datasets are selected dev-set task populations: HotpotQA distractor and MuSiQue answerable. | Validate on additional datasets or official test settings before broad claims. |
| Collider Bias | NOTE | No post-treatment covariate adjustment or conditioning model is used. | Recheck if future analyses condition on query difficulty or expansion success. |
| Base Rate Neglect | CAUTION | False insert is high partly because only 7.15% of candidate units are gold; dataset-specific base rates differ materially. | Report insert yield together with candidate gold prevalence. |
| Regression to the Mean | NOTE | Test queries were selected by fixed source order, not by extreme Stage2E performance, and comparisons share the same unseen queries. | Preserve the fixed unseen slice for all Stage2F analyses. |
| Survivorship Bias | NOTE | All 400 selected queries were retained; duplicate IDs, overlap, and missing mapped gold were all zero. | Continue reporting exclusions explicitly if later datasets require filtering. |
| Look-Elsewhere Effect | CAUTION | Sixty-nine intervals are available, although only one primary endpoint and frozen secondary gates were pre-registered. | Treat non-gate rows as descriptive and avoid selecting only favorable intervals. |
| Garden of Forking Paths | NOTE | The protocol, thresholds, strategies, seed, and decision rules were committed before test evaluation. Strategy discovery in Stage2E remains exploratory. | Keep future changes in a new stage rather than revising Stage2F post hoc. |
| Correlation != Causation | NOTE | The paired intervention is an algorithmic ranking comparison, but it does not support causal claims about answer quality, users, or general RAG systems. | Restrict claims to retrieval behavior under the tested setup. |
| Reverse Causality | NOTE | No directional observational exposure-outcome claim is made. | Not applicable unless future work introduces observational predictors. |

### Reproducibility

- Method: deterministic re-run with identical data, code, thresholds, embedding cache, bootstrap seed, and Python environment
- Environment: Windows 11; Python 3.12.0; NumPy 2.5.1; PyTorch 2.12.1+cpu; Transformers 5.9.0
- Verdict: REPRODUCIBLE

| Artifact / Metric | Original | Re-run | Diff | Status |
|---|---|---|---:|---|
| `stage2f_frozen_threshold_summary.csv` SHA256 | `2B04939494CE22FF5F6CFB9C5AF8644B73F0C41957FA46CE8262342BE1A45297` | same | 0 | MATCH |
| `stage2f_frozen_threshold_bootstrap.csv` SHA256 | `8298E8348158D12AB0988432689984D6C4FED6A7C99C044B426888C24AC11252` | same | 0 | MATCH |
| Primary CR@10 delta | 0.0175 | 0.0175 | 0 | MATCH |
| q25 false-insert delta | -0.0128598913 | -0.0128598913 | 0 | MATCH |
| q25 CR@20 delta | 0.0175 | 0.0175 | 0 | MATCH |

Timing was not compared because wall-clock duration is not a deterministic scientific output.
