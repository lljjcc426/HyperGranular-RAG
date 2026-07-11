# Stage3A Utility-Calibrated Controller Development Report

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run
- Origin Date: 2026-07-11
- Verification Status: UNVERIFIED
- Version Label: exp_result_v1
- Analysis Status: DEVELOPMENT; NOT CONFIRMATORY
- Protocol: `docs/STAGE3A_PROTOCOL.md`
- Stage3B metrics computed: No

## Experiment Result

- ID: stage3a_utility_controller_dev800
- Type: analysis
- Status: completed
- Duration: 258.17 seconds
- Exit Code: 0

## Data Audit

- Queries/units/gold units: 800/24415/1774
- Prior overlap: [0, 0, 0]
- Stage3B overlap: 0
- Frozen q25 floor: 0.1957079917
- Development query digest: `1EC78DE5B2215668BF4F8729C5A3AC04640770FF2C0A8E35F5F9956A46A3A5BB`
- Reserved Stage3B query digest: `6B09E0358361E387E35B11C2DFF48B7F5F3A011959D5D07F0FC14D019520AFEB`

## Model Audit

- Gain head positives/negatives: 9/471
- Harm head positives/negatives: 2/478
- Gain fallback: False
- Harm fallback: True
- Threshold mode/value: finite / 0.018174305149033447

| Head | AUROC | Average precision | Positives |
|---|---:|---:|---:|
| gain | 0.8482 | 0.1126 | 12 |
| harm | NA | NA | 0 |

## Threshold-Selection Results

| Strategy | Trigger | Non-gold/query | ER@20 | CR@20 | Gains | Harms | Net | Gain retention |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| dense_fixed | 0.0000 | 0.0000 | 0.9428 | 0.8750 | 0 | 0 | 0 | 0.0000 |
| allquery_q25_p10_i4 | 0.4531 | 1.1656 | 0.9634 | 0.9125 | 12 | 0 | 12 | 1.0000 |
| stage2g_or_q25_p10_i4 | 0.3656 | 0.9500 | 0.9634 | 0.9125 | 12 | 0 | 12 | 1.0000 |
| score_margin_q25_p10_i4 | 0.3063 | 0.7937 | 0.9613 | 0.9094 | 11 | 0 | 11 | 0.9167 |
| utility_controller_q25_p10_i4 | 0.2125 | 0.6125 | 0.9592 | 0.9062 | 10 | 0 | 10 | 0.8333 |

## Promotion Gate

- Decision: FAIL
- gain_retention_at_least_0_80: PASS
- non_gold_reduction_at_least_0_20: PASS
- cr20_gap_at_least_minus_0_01: PASS
- positive_net_completed_chain_change: PASS
- not_expand_all: PASS
- no_sparse_target_fallback: FAIL

## Bootstrap Boundary

- Descriptive paired bootstrap rows: 10
- The threshold was selected on the same 320-query partition; intervals are not confirmatory.

## Interpretation Boundary

Stage3A may freeze a controller for later testing, but it cannot establish generalization. Stage3B remains locked and no Stage3B embeddings or retrieval metrics were produced.
