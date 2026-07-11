# Stage3C Statistical Validation Report

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validate
- Origin Date: 2026-07-11
- Verification Status: VERIFIED
- Version Label: validation_v1
- Analysis Status: EXPLORATORY RETROSPECTIVE FEASIBILITY AUDIT

## Validation Report

- **Source**: stage3c_target_feasibility_audit_2000
- **Overall Confidence**: CAUTION
- **Stage3B Status**: LOCKED; no metrics read
- **Scope Decision**: BUDGET_AWARE_GAIN_SELECTION_EVENT_FEASIBLE

### Statistical Findings

| Scope | Event | Count / queries | Prevalence | Wilson 95% CI | Confidence |
|---|---|---:|---:|---:|---|
| ALL | Gain | 69/2,000 | 0.0345 | [0.02735, 0.04343] | CAUTION |
| ALL | Harm | 8/2,000 | 0.0040 | [0.00203, 0.00787] | CAUTION |
| HotpotQA | Gain | 69/1,000 | 0.0690 | [0.05488, 0.08641] | CAUTION |
| HotpotQA | Harm | 8/1,000 | 0.0080 | [0.00406, 0.01571] | CAUTION |
| MuSiQue | Gain | 0/1,000 | 0.0000 | [0.00000, 0.00383] | CAUTION |
| MuSiQue | Harm | 0/1,000 | 0.0000 | [0.00000, 0.00383] | CAUTION |

All 69 gains and all 8 harms occur in HotpotQA. MuSiQue dense-fixed CR@20 is 1.0000 in every observed partition and supplies no Top-20 completion target variation.

### Event-Count Planning

- At the pooled harm prevalence of 0.0040, the descriptive point projection is 5,000 queries for 20 harms and 12,500 for 50 harms.
- At the HotpotQA harm prevalence of 0.0080, the corresponding projections are 2,500 and 6,250 queries.
- These are arithmetic projections from observed prevalence, not power calculations or guarantees about future samples.
- No observed partition has at least 5 harms, so the frozen two-partition risk-feasibility requirement fails.

### Warnings

| Type | Detail | Affected |
|---|---|---|
| Retrospective reuse | All Stage2H/Stage3A labels were previously observed. | Every event estimate |
| Dataset concentration | Events occur only in HotpotQA; pooled rates mix an informative dataset with a saturated one. | ALL estimates and controller scope |
| Rare harms | Eight harms are insufficient for stable multivariate harm modeling. | Risk-aware utility target |
| Endpoint saturation | MuSiQue CR@20 is 1.0000, but this does not imply saturation at other K values or answer-generation metrics. | MuSiQue interpretation |
| Point projection | Required-query projections assume future event prevalence matches observed prevalence. | Sample planning |

### Fallacy Scan

- **Coverage**: 11/11 fallacy types checked

| Fallacy | Severity | Finding |
|---|---|---|
| Simpson's paradox | CAUTION | Pooled event rates hide that HotpotQA contains every event and MuSiQue contains none; dataset-specific rows govern interpretation. |
| Ecological fallacy | NOTE | Event definitions and inference are query-level; no aggregate-to-query causal inference is made. |
| Berkson's paradox | CAUTION | Contiguous benchmark dev slices are a selected population and may not represent train, open-domain, or other benchmarks. |
| Collider bias | NOTE | Opportunity-conditioned precision/rates can differ from per-query prevalence; both denominators are reported. |
| Base-rate neglect | NOTE | Raw counts, per-query prevalence, opportunity rates, and Wilson intervals are all reported. |
| Regression to the mean | NOTE | No extreme-score pre/post design is used. |
| Survivorship bias | NOTE | All 2,000 declared rows are included, with zero cross-stage overlap. |
| Look-elsewhere effect | NOTE | No significance search is performed; event definitions and scope rules were fixed before the combined audit. |
| Garden of forking paths | CAUTION | The combined protocol was committed first, but its component datasets and prior stage results were already known; findings remain exploratory. |
| Correlation is not causation | NOTE | Event concentration is described without a causal claim about dataset construction. |
| Reverse causality | NOTE | No directional causal relationship is claimed. |

### Reproducibility

- **Method**: deterministic re-run from the two frozen query-audit files, Stage3A model artifact, and Stage3 reservation manifest
- **Verdict**: REPRODUCIBLE

| File | SHA-256 | Status |
|---|---|---|
| `stage3c_event_feasibility_summary.csv` | `92441830C11A22C8797542EFD340CEE85A911630492E77D35DEA602D72D492CA` | MATCH |
| `stage3c_target_feasibility_decision.json` | `02CA6F731241456BDEA4DEA20EC46D0EAA00D231B251016465B7E673B39059F9` | MATCH |

## Validation Boundary

The audit supports retiring the current risk-aware dual-head target and retaining budget-aware gain selection as a development scope. It does not show that a gain selector generalizes, and it does not validate 2WikiMultiHopQA until a separately frozen pilot is run.
