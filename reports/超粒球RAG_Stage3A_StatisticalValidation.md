# Stage3A Statistical Validation Report

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validate
- Origin Date: 2026-07-11
- Verification Status: VERIFIED
- Version Label: validation_v1
- Analysis Status: DEVELOPMENT; NOT CONFIRMATORY

## Validation Report

- **Source**: stage3a_utility_controller_dev800
- **Overall Confidence**: CAUTION
- **Promotion Decision**: FAIL
- **Stage3B Status**: LOCKED; no retrieval metrics or embeddings computed

The failure decision is determined by the frozen protocol: the harm head had only 2 positive fitting examples and used the declared intercept-only fallback. Descriptive gains on the threshold-selection partition do not override that gate.

### Statistical Findings

| Finding | Observed result | Descriptive 95% CI | Confidence |
|---|---:|---:|---|
| Utility controller CR@20 vs all-query | -0.00625 | [-0.015625, 0.000000] | CAUTION |
| Utility controller ER@20 vs all-query | -0.00417 | [-0.00990, 0.00000] | CAUTION |
| Trigger-rate delta vs all-query | -0.24063 | [-0.28750, -0.19687] | CAUTION |
| Non-gold insertions/query delta vs all-query | -0.55313 | [-0.67813, -0.43437] | CAUTION |
| False-insert-rate delta vs all-query | -0.00626 | [-0.03365, 0.02112] | CAUTION |
| Utility controller CR@20 vs dense fixed | +0.03125 | [0.01250, 0.05000] | CAUTION |

The controller retained 10 of 12 all-query gains, selected 68 of 320 threshold-selection queries, and reduced non-gold insertions per query from 1.1656 to 0.6125. These estimates are optimistic development estimates because the same 320 queries selected the threshold.

### Predictive Audit

- Gain fitting events: 9/480; gain-head fitting AUROC/AP = 0.9038/0.2835.
- Gain threshold-selection events: 12/320; aggregate AUROC/AP = 0.8482/0.1126.
- HotpotQA-only threshold-selection AUROC/AP = 0.6864/0.1132.
- MuSiQue has zero gain events in both partitions, so dataset-specific AUROC/AP are undefined.
- Harm fitting events: 2/480; the harm head used the predeclared fallback probability `0.006224`.
- Harm threshold-selection events: 0/320; harm discrimination cannot be evaluated.

The high aggregate gain AUROC is partly driven by dataset composition: all observed gains occur in HotpotQA while MuSiQue contributes only negatives. It must not be interpreted as broad cross-dataset discrimination.

### Warnings

| Type | Detail | Affected |
|---|---|---|
| Sparse targets | Only 9 fitting gains and 2 fitting harms; the harm head cannot be fitted as specified. | Utility score and promotion gate |
| Threshold reuse | The 320-query partition both selects and reports the operating threshold. | All threshold-selection intervals |
| Dataset heterogeneity | MuSiQue has zero gain or harm events; useful events are confined to HotpotQA. | Aggregate AUROC and generalization |
| Metric distinction | Non-gold insertions decrease, but conditional false-insert rate changes little and its CI includes zero. | Noise-control interpretation |
| External validity | One encoder, two benchmark dev sets, and one retrieval budget are evaluated. | General claims |

### Fallacy Scan

- **Coverage**: 11/11 fallacy types checked

| Fallacy | Severity | Finding |
|---|---|---|
| Simpson's paradox | CAUTION | Aggregate AUROC exceeds HotpotQA-only AUROC while MuSiQue has no positives; aggregate discrimination is composition-sensitive. |
| Ecological fallacy | NOTE | Analysis and intended inference are both query-level; no group-to-query inference is used. |
| Berkson's paradox | CAUTION | Results concern contiguous benchmark development slices and cannot be generalized beyond the selected benchmark population. |
| Collider bias | NOTE | Model fitting uses all development queries rather than conditioning on observed success; no collider control is introduced. |
| Base-rate neglect | CAUTION | Positive base rates are extremely low; AP and event counts are therefore reported alongside AUROC. |
| Regression to the mean | NOTE | No extreme-score pre/post comparison is used. |
| Survivorship bias | NOTE | All 800 planned queries are retained and missing-gold count is zero. |
| Look-elsewhere effect | NOTE | Metrics and promotion gates were fixed before development outcomes; bootstrap results remain descriptive. |
| Garden of forking paths | NOTE | Protocol, data reservation, threshold rule, and code were committed before metrics; no post-hoc branch was substituted. |
| Correlation is not causation | NOTE | Predictive associations are not stated as causal mechanisms. |
| Reverse causality | NOTE | No directional causal claim is made. |

### Reproducibility

- **Method**: deterministic re-run using the same corpus, embedding cache, source hashes, reservation manifest, model code, bootstrap seed, and frozen q25 floor
- **Verdict**: REPRODUCIBLE
- **Equality rule**: byte-for-byte SHA-256 match for all four core artifacts

| File | SHA-256 | Status |
|---|---|---|
| `stage3a_utility_controller_query_audit.csv` | `8CEBBEB91536B131FC87A46A5B8744E462F1732986723A787349074147834561` | MATCH |
| `stage3a_utility_controller_model.json` | `53223FC5384ECC828ED312DFDBF048E58CFE8FC071DEE894F657B8B9524403C7` | MATCH |
| `stage3a_utility_controller_summary.csv` | `D32C500381E18AEEC86899D052FD87CAC2921CB1A3229C9C90761C3C5F61A3B8` | MATCH |
| `stage3a_utility_controller_bootstrap.csv` | `FCE4ECDAA6DF7461B82D7CCB06E40BDC76B01509F215A916A544E2A396B208E4` | MATCH |

Timing and report paths are excluded from equality checks.

## Validation Boundary

Stage3A shows that a sparse linear gain selector can reduce expansion volume while retaining most observed HotpotQA gains. It does not establish a risk-aware controller because harm is too rare to model or evaluate. Under the frozen protocol, the current branch ends here and Stage3B remains untouched.
