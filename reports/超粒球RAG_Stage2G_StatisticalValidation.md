# Stage2G Statistical Validation Report

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validate
- Origin Date: 2026-07-10
- Verification Status: VERIFIED
- Version Label: validation_v1

## Validation Report

- Source: `stage2g_boundary_mechanism_unseen400`
- Protocol: `docs/STAGE2G_PROTOCOL.md`, committed as `06794d1` before test extraction and evaluation
- Overall Confidence: CAUTION
- Reproducibility class: deterministic
- Unit of analysis: query
- Test set: 400 unseen queries, 200 HotpotQA and 200 MuSiQue

### Statistical Findings

| Finding | Test | Value | Effect Size | Confidence |
|---|---|---:|---|---|
| Primary p10/i4 boundary vs all-query false insert | Stratified paired ratio bootstrap, 10,000 resamples | delta +0.0043, 95% CI [-0.0054, 0.0150] | +0.43 percentage points; uncertain and opposite the hypothesis | CAUTION |
| Primary p10/i4 boundary vs all-query CR@20 | Stratified paired bootstrap, 10,000 resamples | delta -0.0075, 95% CI [-0.0200, 0.0025] | -0.75 percentage points; non-inferiority margin not met | CAUTION |
| Primary p10/i4 boundary vs all-query trigger rate | Stratified paired bootstrap, 10,000 resamples | delta -0.0775, 95% CI [-0.1050, -0.0525] | -7.75 percentage points; clear coverage reduction | CAUTION |
| Secondary p5/i4 boundary vs all-query false insert | Stratified paired ratio bootstrap, 10,000 resamples | delta -0.0011, 95% CI [-0.0105, 0.0086] | -0.11 percentage points; uncertain | CAUTION |
| Secondary p5/i4 boundary vs all-query CR@10 | Stratified paired bootstrap, 10,000 resamples | delta -0.0075, 95% CI [-0.0200, 0.0050] | -0.75 percentage points; non-inferiority margin not met | CAUTION |
| Boundary vs non-boundary completion precision@20 | Stratified ratio bootstrap under all-query policy | delta -0.0686, 95% CI [-0.4000, 0.2337] | -6.86 percentage points; very imprecise | CAUTION |

The pre-registered primary, secondary, and predictive mechanism gates all failed. Boundary-only triggering reduced how often insertion occurred, but it did not lower the conditional false-insert rate at p10/i4 and did not satisfy the `-0.01` recall non-inferiority margin. Under the all-query counterfactual, boundary queries had completion precision 0.2647 across 34 opportunities, versus 0.3333 across 12 non-boundary opportunities.

### Query-Level Direction

- Primary CR@20 policy comparison: 1 query improved, 395 unchanged, 4 regressed when moving from all-query to boundary-only.
- Secondary CR@10 policy comparison: 2 improved, 393 unchanged, 5 regressed.
- Boundary prevalence was 0.8100 in both datasets; the primary trigger rate fell from 0.5225 to 0.4450.
- All-query q25 p10/i4 CR@20 was 0.8925; boundary-only was 0.8850; dense fixed was 0.8700.

### Base-Rate Context

| Dataset | Candidate Units | Gold Units | Gold Base Rate | All-query p10 Insert Yield | Boundary p10 Insert Yield |
|---|---:|---:|---:|---:|---:|
| HotpotQA | 8,122 | 482 | 0.0593 | 0.0888 | 0.0838 |
| MuSiQue | 4,000 | 400 | 0.1000 | 0.0738 | 0.0727 |
| ALL | 12,122 | 882 | 0.0728 | 0.0855 | 0.0811 |

Both p10 policies select gold above the combined candidate base rate, but boundary-only has lower insert yield than all-query overall and within each dataset. This is consistent with the failed false-insert gate.

### Warnings

| Type | Detail | Affected |
|---|---|---|
| Core mechanism not supported | All three pre-registered gates failed. The current boundary rule cannot be presented as a validated benefit predictor. | Boundary-decision claim |
| Weak selectivity | The rule labels 81% of queries as boundary, limiting its ability to isolate a small high-uncertainty subset. | Trigger policy |
| Low predictive denominator | Completion-precision comparison uses 34 boundary and 12 non-boundary opportunities, producing a wide interval. | Predictive gate |
| Dataset saturation | MuSiQue dense fixed CR@20 is 1.0000; p10 policy recall differences come from HotpotQA. | CR@20 |
| Dataset heterogeneity | Secondary false-insert direction is negative on HotpotQA and positive on MuSiQue, while ALL is near zero. | p5/i4 noise result |
| Multiple comparisons | The bootstrap CSV contains 60 intervals. Only frozen gates are confirmatory; other rows are descriptive without family-wise correction. | Secondary output |
| Scope | The audit uses later slices of the same two dev sets and the same encoder. | External validity |

### Fallacy Scan

- Coverage: 11/11 fallacy types checked

| Fallacy | Severity | Detail | Recommendation |
|---|---|---|---|
| Simpson's Paradox | CAUTION | Primary false-insert direction is positive in both datasets and CR@20 is negative or zero, so there is no primary reversal. Secondary false-insert directions differ across datasets, making the near-zero ALL estimate incomplete by itself. | Keep dataset-specific directions beside ALL. |
| Ecological Fallacy | NOTE | Policy comparisons and bootstrap resampling operate at query level, matching the unit of inference. | Do not generalize query-level retrieval behavior to users or deployed systems. |
| Berkson's Paradox | CAUTION | Samples come from selected HotpotQA distractor and MuSiQue answerable dev populations. | Require external-dataset validation before broad mechanism claims. |
| Collider Bias | NOTE | No covariate adjustment is used; boundary status is the policy signal under direct audit rather than a conditioned control variable. | Reassess if future models condition jointly on difficulty, retrieval success, and boundary status. |
| Base Rate Neglect | CAUTION | Only 7.28% of candidate units are gold, and base rates differ from 5.93% to 10.00% by dataset. | Report insert yield and candidate prevalence with false insert. |
| Regression to the Mean | NOTE | The test slice is fixed by source order and was not selected for extreme prior performance. | Preserve the frozen slice and comparisons. |
| Survivorship Bias | NOTE | All 400 selected queries were retained; prior overlap, duplicates, and missing mapped gold were zero. | Report any future exclusions explicitly. |
| Look-Elsewhere Effect | CAUTION | Sixty intervals exist, although primary, secondary, and predictive gates were frozen before evaluation. | Treat non-gate intervals as descriptive. |
| Garden of Forking Paths | NOTE | Data slice, q25 floor, strategies, margins, seed, and gates were committed before extraction. | Put any redesigned uncertainty rule in a new development stage. |
| Correlation != Causation | NOTE | The paired policy intervention supports statements about tested ranking behavior, not causal claims about answer quality or general RAG systems. | Restrict interpretation to the tested retrieval setup. |
| Reverse Causality | NOTE | No directional observational exposure-outcome relation is asserted. | Not applicable unless later work models observational predictors. |

### Reproducibility

- Method: deterministic re-run with identical data, code, q25 floor, embedding cache, bootstrap seed, and Python environment
- Environment: Windows 11; Python 3.12.0; NumPy 2.5.1; PyTorch 2.12.1+cpu; Transformers 5.9.0
- Verdict: REPRODUCIBLE

| Artifact / Metric | Original | Re-run | Diff | Status |
|---|---|---|---:|---|
| `stage2g_boundary_mechanism_summary.csv` SHA256 | `878D7C00818555BFE0CC27E067C4523ACAA7B70FD8CFD109E0E52BBE9745AB4B` | same | 0 | MATCH |
| `stage2g_boundary_mechanism_bootstrap.csv` SHA256 | `552A8CD5CD40C994F2E3AA8E590BE5CD5C41DBD5E98DDC4E8E583151439D1167` | same | 0 | MATCH |
| Primary false-insert delta | 0.0043141946 | 0.0043141946 | 0 | MATCH |
| Primary CR@20 delta | -0.0075 | -0.0075 | 0 | MATCH |
| Predictive completion-precision delta | -0.0686274510 | -0.0686274510 | 0 | MATCH |

Timing was not compared because wall-clock duration is not a deterministic scientific output.
