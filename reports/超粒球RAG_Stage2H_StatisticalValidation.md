# Stage2H Statistical Validation Report

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validate
- Origin Date: 2026-07-11
- Verification Status: VERIFIED
- Version Label: validation_v1
- Analysis Status: EXPLORATORY POST-HOC DIAGNOSIS

## Validation Report

- **Source**: stage2h_boundary_failure_diagnosis_1200
- **Overall Confidence**: CAUTION
- **Reason**: the analysis is deterministic and reproducible, but it reuses previously observed labels, tests several related diagnostics, and yields wide confidence intervals.

### Statistical Findings

| Finding | Estimate | 95% CI / support | Confidence |
|---|---:|---:|---|
| Radius true-minus-false completion precision@20 | -0.0976 | [-0.2628, 0.0658] | CAUTION |
| Score-margin true-minus-false completion precision@20 | +0.1292 | [-0.0517, 0.2985] | CAUTION |
| OR-gate true-minus-false completion precision@20 | +0.0512 | [-0.1737, 0.2564] | CAUTION |
| Radius completion predictor | AUROC 0.4912 | AP 0.3411; 133 opportunities, 48 positives | CAUTION |
| Score-margin completion predictor | AUROC 0.5223 | AP 0.4043; 133 opportunities, 48 positives | CAUTION |
| Top-score completion predictor | AUROC 0.3821 | AP 0.3031; 133 opportunities, 48 positives | CAUTION |

All three principal component contrasts include zero. The score-margin component has the strongest descriptive association, but AUROC 0.5223 is only slightly above chance and does not validate a replacement controller. The low-top-score component fires for only 1 of 1,200 queries, so its contrast is not substantively interpretable despite the numerical bootstrap interval.

### Warnings

| Type | Detail | Affected |
|---|---|---|
| Post-hoc reuse | Stage2H reuses Stage2E-F-G labels that were already observed. | All mechanism findings |
| Multiple diagnostics | Components, overlap masks, scopes, and three outcomes were inspected without confirmatory multiplicity control. | Component contrasts and subgroup results |
| Sparse opportunities | Completion prediction uses 133 opportunities with 48 successes; some component/scope cells are much smaller. | AUROC, AP, completion precision |
| Degenerate component | `low_top_score` is true for 1 query and never triggers insertion. | Low-top-score contrasts |
| Limited external validity | Data are limited to HotpotQA and MuSiQue slices with one frozen encoder/indexing pipeline. | Generalization claims |

### Fallacy Scan

- **Coverage**: 11/11 fallacy types checked

| Fallacy | Severity | Finding |
|---|---|---|
| Simpson's paradox | NOTE | Dataset and slice breakdowns were inspected; no aggregate-to-subgroup reversal is used as a conclusion. |
| Ecological fallacy | NOTE | Analysis and inference are both at query level; no group-to-individual inference is made. |
| Berkson's paradox | CAUTION | Predictive metrics condition on triggered, baseline-incomplete queries, so they describe that selected opportunity set only. |
| Collider bias | NOTE | Conditioning on baseline incompleteness could distort associations, but no causal interpretation is made. |
| Base-rate neglect | NOTE | Component prevalence, opportunity counts, positives, precision, and false-insert rates are reported. |
| Regression to the mean | NOTE | No extreme-score pre/post comparison is used. |
| Survivorship bias | NOTE | All 1,200 planned queries are present; there is no attrition. |
| Look-elsewhere effect | CAUTION | Many exploratory component, mask, scope, and outcome comparisons are shown without adjusted inference. |
| Garden of forking paths | CAUTION | The diagnostic plan was committed before this run, but the underlying Stage2E-F-G outcomes were already known; findings remain exploratory. |
| Correlation is not causation | NOTE | Results are framed as associations and diagnostic signals, not causal effects. |
| Reverse causality | NOTE | No directional causal claim is made. |

### Reproducibility

- **Method**: deterministic re-run with the same script, three corpus slices, frozen embedding caches, q25 calibration summary, 10,000 stratified bootstrap iterations, and seed 20260712
- **Verdict**: REPRODUCIBLE
- **Equality rule**: byte-for-byte SHA-256 match for all tracked CSV outputs

| File | SHA-256 original | SHA-256 re-run | Status |
|---|---|---|---|
| `stage2h_boundary_query_audit.csv` | `9773436E05A875032720EB0AF75088A6DAE5D57231DE37854B18BCE195B0399F` | same | MATCH |
| `stage2h_boundary_component_summary.csv` | `67A64880C583C6FBBFD94740696FFCD2F5E0C47C6E1B17643AA7DD81015360B5` | same | MATCH |
| `stage2h_boundary_predictive_metrics.csv` | `12836AEB6C00B1992DDFA3A494A4A31D9374DFE1385853D8CF18B3C88C127BF4` | same | MATCH |

Timing and report paths are excluded from equality checks because they vary by run location and wall-clock execution.

## Validation Boundary

Stage2H explains why the frozen OR rule failed to select expansion benefit reliably. It does not establish a new threshold, a new controller, or a confirmatory performance gain. Any replacement controller must be developed on new data and evaluated once on a separately reserved test slice.
