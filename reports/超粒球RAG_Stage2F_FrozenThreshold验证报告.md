# Stage2F Frozen-Threshold Independent Validation Report

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run
- Origin Date: 2026-07-10
- Verification Status: UNVERIFIED
- Version Label: exp_result_v1
- Protocol: `docs/STAGE2F_PROTOCOL.md` committed before test evaluation
- Gold labels used for indexing, filtering, ranking, or threshold selection: No
- Generator used: No

## Experiment Result

- ID: stage2f_frozen_threshold_unseen400
- Type: analysis
- Status: completed
- Command: `python scripts/stage2f_frozen_threshold_validation.py --units "E:\科研\超粒球RAG_数据\processed\stage2f_unseen400_units.jsonl" --queries "E:\科研\超粒球RAG_数据\processed\stage2f_unseen400_queries.jsonl" --calibration-queries "E:\科研\超粒球RAG_数据\processed\stage1_sample400_queries.jsonl" --calibration-summary "results\stage2e_insert_noise_control_summary.csv" --embedding-cache "E:\科研\超粒球RAG_数据\processed\stage2f_dense_allminilm_embeddings.npz" --output-dir "results" --report "reports\超粒球RAG_Stage2F_FrozenThreshold验证报告.md" --expand-boundary-only`
- Working Directory: `E:\科研\HyperGranular-RAG`
- Duration: 131.67 seconds
- Exit Code: 0

### Output Files

| File | Size |
|---|---:|
| `results\stage2f_frozen_threshold_summary.csv` | 8937 bytes |
| `results\stage2f_frozen_threshold_bootstrap.csv` | 11610 bytes |

### Anomalies Detected

None during the completed run.

## Independent-Test Audit

- Test queries: 400 (200 HotpotQA, 200 MuSiQue)
- Test retrieval units: 12333
- Test gold units: 882
- Calibration/test query-ID overlap: 0
- Queries missing mapped gold: 0
- Frozen q25/q50 score floors: 0.1957079917 / 0.3166663051

## ALL Strategy Summary

| Strategy | Protect | Insert | Retain | Avg inserted | ER@10 | CR@10 | ER@20 | CR@20 | False insert |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| dense_fixed | 0 | 0 | 0.0000 | 0.0000 | 0.7762 | 0.5650 | 0.9473 | 0.8850 | 0.0000 |
| unfiltered_p5_i2 | 5 | 2 | 1.0000 | 0.9700 | 0.7950 | 0.5875 | 0.9531 | 0.8950 | 0.8892 |
| unfiltered_p5_i4 | 5 | 4 | 1.0000 | 1.7225 | 0.7875 | 0.5750 | 0.9552 | 0.8950 | 0.9216 |
| score_q25_p5_i4 | 5 | 4 | 0.7788 | 1.3975 | 0.7924 | 0.5825 | 0.9546 | 0.8950 | 0.9088 |
| unfiltered_p10_i4 | 10 | 4 | 1.0000 | 1.5525 | 0.7762 | 0.5650 | 0.9590 | 0.9025 | 0.9308 |
| score_q25_p10_i4 | 10 | 4 | 0.7788 | 1.1750 | 0.7762 | 0.5650 | 0.9583 | 0.9025 | 0.9170 |
| score_q50_p5_i2 | 5 | 2 | 0.4474 | 0.5400 | 0.7932 | 0.5850 | 0.9513 | 0.8925 | 0.8380 |

## Dataset Split

| Dataset | Strategy | ER@10 | CR@10 | ER@20 | CR@20 | False insert |
|---|---|---:|---:|---:|---:|---:|
| hotpotqa | dense_fixed | 0.7524 | 0.5150 | 0.8946 | 0.7700 | 0.0000 |
| hotpotqa | score_q25_p5_i4 | 0.7773 | 0.5400 | 0.9092 | 0.7900 | 0.8957 |
| hotpotqa | score_q25_p10_i4 | 0.7524 | 0.5150 | 0.9167 | 0.8050 | 0.9118 |
| hotpotqa | score_q50_p5_i2 | 0.7814 | 0.5500 | 0.9025 | 0.7850 | 0.8161 |
| musique | dense_fixed | 0.8000 | 0.6150 | 1.0000 | 1.0000 | 0.0000 |
| musique | score_q25_p5_i4 | 0.8075 | 0.6250 | 1.0000 | 1.0000 | 0.9398 |
| musique | score_q25_p10_i4 | 0.8000 | 0.6150 | 1.0000 | 1.0000 | 0.9346 |
| musique | score_q50_p5_i2 | 0.8050 | 0.6200 | 1.0000 | 1.0000 | 0.9286 |

## Pre-Registered Decision Gates

| Gate | Delta | 95% CI | Decision |
|---|---:|---:|---|
| Primary: q25 p5/i4 vs fixed CR@10 | 0.0175 | [-0.0125, 0.0475] | NOT SUPPORTED |
| Noise: q25 p5/i4 vs unfiltered false insert | -0.0129 | [-0.0206, -0.0055] | SUPPORTED; CR@10 delta=0.0075 |
| Long context: q25 p10/i4 vs fixed CR@20 | 0.0175 | [0.0025, 0.0350] | SUPPORTED |
| Exploratory q50 p5/i2 vs unfiltered false insert | -0.0512 | [-0.0783, -0.0259] | descriptive; CR@10 delta=-0.0025 |

## Interpretation Boundary

- The primary and secondary gate labels follow the rules frozen in the protocol; they are not selected after seeing test results.
- Bootstrap intervals use 10,000 paired resamples with dataset-stratified resampling for ALL.
- False insert is the aggregate share of inserted units that are not labelled gold, not a hallucination metric.
- This is independent query-level validation within HotpotQA and MuSiQue using the same encoder. It does not establish cross-dataset, cross-encoder, or answer-generation generalization.
