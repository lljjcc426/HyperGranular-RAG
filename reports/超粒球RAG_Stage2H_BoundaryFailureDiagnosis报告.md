# Stage2H Boundary-Rule Failure Diagnosis Report

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run
- Origin Date: 2026-07-11
- Verification Status: UNVERIFIED
- Version Label: exp_result_v1
- Analysis Status: EXPLORATORY POST-HOC DIAGNOSIS
- Plan: `docs/STAGE2H_DIAGNOSTIC_PLAN.md`
- Gold labels used for ranking or boundary classification: No
- Generator used: No

## Experiment Result

- ID: stage2h_boundary_failure_diagnosis_1200
- Type: analysis
- Status: completed
- Working Directory: `E:\科研\HyperGranular-RAG`
- Duration: 9.79 seconds
- Exit Code: 0

### Output Files

| File | Size |
|---|---:|
| `results\stage2h_boundary_query_audit.csv` | 325578 bytes |
| `results\stage2h_boundary_component_summary.csv` | 19752 bytes |
| `results\stage2h_boundary_predictive_metrics.csv` | 18432 bytes |

### Anomalies Detected

None during the completed run.

## Corpus Audit

- Slices: 3
- Total pairwise-disjoint queries: 1200
- Frozen q25 score floor: 0.1957079917
- stage2e: 400 queries, 12304 units, 887 gold units, overlap=0.
- stage2f: 400 queries, 12333 units, 882 gold units, overlap=0.
- stage2g: 400 queries, 12122 units, 882 gold units, overlap=0.

## OR-Component Coverage

| Component | Queries | Prevalence | Trigger | Completion P@20 | Harm@20 | False insert |
|---|---:|---:|---:|---:|---:|---:|
| radius | 604 | 0.5033 | 0.4139 | 0.3000 | 0.0050 | 0.9058 |
| score_margin | 699 | 0.5825 | 0.5823 | 0.3939 | 0.0130 | 0.9011 |
| low_top_score | 1 | 0.0008 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| or_gate | 970 | 0.8083 | 0.5134 | 0.3694 | 0.0129 | 0.9035 |

## Exclusive Overlap Masks

| Mask | Queries | Prevalence | Completion P@20 | Harm@20 | False insert |
|---|---:|---:|---:|---:|---:|
| S | 365 | 0.3042 | 0.4262 | 0.0214 | 0.9014 |
| RS | 333 | 0.2775 | 0.3421 | 0.0000 | 0.9005 |
| R | 271 | 0.2258 | 0.1667 | 0.0127 | 0.9159 |
| none | 230 | 0.1917 | 0.3182 | 0.0141 | 0.8906 |
| SL | 1 | 0.0008 | 0.0000 | 0.0000 | 0.0000 |

## Continuous Predictive Audit

AUROC and average precision use triggered queries whose dense-fixed chain is incomplete at 20.

| Predictor | Opportunities | Positives | AUROC | Average precision |
|---|---:|---:|---:|---:|
| neg_boundary_margin | 133 | 48 | 0.4912 | 0.3411 |
| neg_ball_score_margin | 133 | 48 | 0.5223 | 0.4043 |
| neg_top_ball_score | 133 | 48 | 0.3821 | 0.3031 |

## Component Contrasts

| Component | Outcome | True | False | Delta | 95% CI |
|---|---|---:|---:|---:|---:|
| radius | completion_precision_at_20 | 0.3000 | 0.3976 | -0.0976 | [-0.2628, 0.0658] |
| radius | harm_rate_at_20 | 0.0050 | 0.0194 | -0.0144 | [-0.0348, 0.0042] |
| radius | false_insert_rate | 0.9058 | 0.8986 | 0.0072 | [-0.0235, 0.0357] |
| score_margin | completion_precision_at_20 | 0.3939 | 0.2647 | 0.1292 | [-0.0517, 0.2985] |
| score_margin | harm_rate_at_20 | 0.0130 | 0.0133 | -0.0003 | [-0.0247, 0.0205] |
| score_margin | false_insert_rate | 0.9011 | 0.9025 | -0.0014 | [-0.0315, 0.0306] |
| low_top_score | completion_precision_at_20 | 0.0000 | 0.3609 | -0.3609 | [-0.4435, -0.2817] |
| low_top_score | harm_rate_at_20 | 0.0000 | 0.0131 | -0.0131 | [-0.0244, -0.0043] |
| low_top_score | false_insert_rate | 0.0000 | 0.9015 | -0.9015 | [-0.9160, -0.8864] |
| or_gate | completion_precision_at_20 | 0.3694 | 0.3182 | 0.0512 | [-0.1737, 0.2564] |
| or_gate | harm_rate_at_20 | 0.0129 | 0.0141 | -0.0012 | [-0.0355, 0.0223] |
| or_gate | false_insert_rate | 0.9035 | 0.8906 | 0.0129 | [-0.0249, 0.0526] |

## Evidence-Grounded Diagnosis

- The highest-coverage individual component is `score_margin` with prevalence 0.5825.
- The current OR gate covers 0.8083 of the 1,200 diagnostic queries.
- Predictive metrics and bootstrap contrasts are descriptive. They do not validate a replacement gate or justify selecting a new threshold on these labels.

## Interpretation Boundary

- Stage2H reuses labels already observed in Stage2E-F-G and is therefore post-hoc.
- A component with a favorable descriptive association still requires development on new data and a separately reserved frozen test.
- False insert is not a hallucination metric, and no answer generator is evaluated.
