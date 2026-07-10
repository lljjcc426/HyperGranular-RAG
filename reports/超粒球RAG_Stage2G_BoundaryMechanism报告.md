# Stage2G Boundary-Decision Mechanism Audit Report

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run
- Origin Date: 2026-07-10
- Verification Status: UNVERIFIED
- Version Label: exp_result_v1
- Protocol: `docs/STAGE2G_PROTOCOL.md` committed before Stage2G test extraction and evaluation
- Gold labels used for indexing, boundary classification, filtering, ranking, or threshold selection: No
- Generator used: No

## Experiment Result

- ID: stage2g_boundary_mechanism_unseen400
- Type: analysis
- Status: completed
- Command: `python scripts/stage2g_boundary_mechanism_audit.py --units "E:\科研\超粒球RAG_数据\processed\stage2g_unseen400_units.jsonl" --queries "E:\科研\超粒球RAG_数据\processed\stage2g_unseen400_queries.jsonl" --prior-queries ... --calibration-summary "results\stage2e_insert_noise_control_summary.csv" --embedding-cache "E:\科研\超粒球RAG_数据\processed\stage2g_dense_allminilm_embeddings.npz" --output-dir "results" --report "reports\超粒球RAG_Stage2G_BoundaryMechanism报告.md"`
- Working Directory: `E:\科研\HyperGranular-RAG`
- Duration: 128.31 seconds
- Exit Code: 0

### Output Files

| File | Size |
|---|---:|
| `results\stage2g_boundary_mechanism_summary.csv` | 9500 bytes |
| `results\stage2g_boundary_mechanism_bootstrap.csv` | 12124 bytes |

### Anomalies Detected

None during the completed run.

## Independent-Test Audit

- Test queries: 400 (200 HotpotQA, 200 MuSiQue)
- Test retrieval units: 12122
- Test gold units: 882
- Prior-slice query-ID overlaps: [0, 0]
- Queries missing mapped gold: 0
- Frozen q25 score floor: 0.1957079917

## ALL Strategy Summary

| Strategy | Boundary policy | Trigger | Avg inserted | CR@10 | CR@20 | False insert | Complete P@20 | Harm@20 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dense_fixed | none | 0.0000 | 0.0000 | 0.6025 | 0.8700 | 0.0000 | 0.0000 | 0.0000 |
| allquery_q25_p5_i4 | all-query | 0.5725 | 1.6875 | 0.6375 | 0.8900 | 0.8844 | 0.2553 | 0.0220 |
| boundary_q25_p5_i4 | boundary-only | 0.4875 | 1.4150 | 0.6300 | 0.8850 | 0.8834 | 0.2571 | 0.0187 |
| allquery_q25_p10_i4 | all-query | 0.5225 | 1.3750 | 0.6025 | 0.8925 | 0.9145 | 0.2826 | 0.0245 |
| boundary_q25_p10_i4 | boundary-only | 0.4450 | 1.1400 | 0.6025 | 0.8850 | 0.9189 | 0.2647 | 0.0208 |

## Dataset Split

| Dataset | Strategy | Boundary rate | Trigger | CR@10 | CR@20 | False insert |
|---|---|---:|---:|---:|---:|---:|
| hotpotqa | dense_fixed | 0.8100 | 0.0000 | 0.5050 | 0.7400 | 0.0000 |
| hotpotqa | allquery_q25_p5_i4 | 0.8100 | 0.7600 | 0.5700 | 0.7800 | 0.8781 |
| hotpotqa | boundary_q25_p5_i4 | 0.8100 | 0.6300 | 0.5600 | 0.7700 | 0.8734 |
| hotpotqa | allquery_q25_p10_i4 | 0.8100 | 0.7300 | 0.5050 | 0.7850 | 0.9112 |
| hotpotqa | boundary_q25_p10_i4 | 0.8100 | 0.6100 | 0.5050 | 0.7700 | 0.9162 |
| musique | dense_fixed | 0.8100 | 0.0000 | 0.7000 | 1.0000 | 0.0000 |
| musique | allquery_q25_p5_i4 | 0.8100 | 0.3850 | 0.7050 | 1.0000 | 0.9005 |
| musique | boundary_q25_p5_i4 | 0.8100 | 0.3450 | 0.7000 | 1.0000 | 0.9064 |
| musique | allquery_q25_p10_i4 | 0.8100 | 0.3150 | 0.7000 | 1.0000 | 0.9262 |
| musique | boundary_q25_p10_i4 | 0.8100 | 0.2800 | 0.7000 | 1.0000 | 0.9273 |

## Pre-Registered Decision Gates

| Gate | False-insert delta [95% CI] | Recall delta [95% CI] | Decision |
|---|---:|---:|---|
| Primary p10/i4 boundary vs all | 0.0043 [-0.0054, 0.0150] | CR@20 -0.0075 [-0.0200, 0.0025] | NOT SUPPORTED |
| Secondary p5/i4 boundary vs all | -0.0011 [-0.0105, 0.0086] | CR@10 -0.0075 [-0.0200, 0.0050] | NOT SUPPORTED |

## Predictive Mechanism Gate

- Boundary completion precision@20: 0.2647 (34 opportunities).
- Non-boundary completion precision@20: 0.3333 (12 opportunities).
- Boundary-minus-non-boundary delta: -0.0686, 95% CI [-0.4000, 0.2337].
- Decision: NOT SUPPORTED.

## Interpretation Boundary

- Policy comparisons differ only in whether non-boundary queries may expand; score floor, candidate construction, ranking, and budgets are identical.
- Completion precision is conditional on a triggered query whose dense-fixed chain is incomplete at the target K.
- False insert is not a hallucination metric, and the audit does not evaluate answer generation.
- A failed predictive gate means the current boundary rule is not validated as a benefit predictor; it does not prove that all uncertainty signals are useless.
