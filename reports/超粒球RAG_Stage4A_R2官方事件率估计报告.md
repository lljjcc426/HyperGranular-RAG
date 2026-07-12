# 超粒球RAG Stage4A-R2 官方事件率估计报告

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run
- Origin Date: 2026-07-12
- Verification Status: VERIFIED_BY_STAGE4A_R2_OUTPUT_AUDIT
- Version Label: exp_result_r2_v1
- Protocol: `docs/STAGE4A_R2_PROTOCOL.md`, committed before official row extraction
- Provenance: official April 7 archive
- Gold labels used for retrieval decisions: No
- Controller fitting: No
- Generator used: No

## Run Record

- Duration: 798.15 seconds
- Exit Code: 0
- Queries / units / gold units: 4500 / 143820 / 11015
- Development ID SHA256: `6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2`
- Reservation ID SHA256: `E54610D36F77DCEDAD651DD20DFC96FD1B8324FD65EB412ABAC757D56897B941`
- Frozen q25 floor: 0.1957079917192459
- Embedding model / max length: `sentence-transformers/all-MiniLM-L6-v2` / 192

## Overall Results

| Strategy | ER@20 | CR@20 | Trigger | Avg insert | Gain | Harm | Net | Removed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| dense_fixed | 0.8982 | 0.7722 | 0.0000 | 0.0000 | 0 | 0 | 0 | 0 |
| allquery_unfiltered_p10_i4 | 0.8995 | 0.7720 | 0.5838 | 1.9736 | 101 | 102 | -1 | 0 |
| allquery_q25_p10_i4 | 0.9023 | 0.7778 | 0.5436 | 1.6133 | 94 | 69 | 25 | 2859 |

## Primary Event-rate Estimates

- Gain: 94/4500 = 0.020889; Wilson 95% [0.017101, 0.025494], half-width 0.004197.
- Harm: 69/4500 = 0.015333; Wilson 95% [0.012134, 0.019359], half-width 0.003612.
- Precision decision: `ESTIMATION_COMPLETE`.

## Secondary Paired Analysis

- q25 minus dense CR@20: 0.005556.
- Discordant queries: 163 (94 gains, 69 harms).
- Exact conditional two-sided McNemar p-value: 0.059798914.
- Paired bootstrap: 6 rows, 10000 resamples, seed 20260712.

## Interpretation Boundary

- Primary inference is the official gain/harm prevalence with interval precision, not the p-value.
- Question-type rows are descriptive and are not separate confirmatory tests.
- No q25 tuning, boundary-rule repair, controller fitting, or reservation metrics are authorized by this stage.
- Stage3B remains locked.

## Outputs

| File | Bytes |
|---|---:|
| `results\stage4a_r2_query_audit.csv` | 850817 |
| `results\stage4a_r2_strategy_summary.csv` | 5205 |
| `results\stage4a_r2_bootstrap.csv` | 1348 |
| `results\stage4a_r2_inference.json` | 1276 |
