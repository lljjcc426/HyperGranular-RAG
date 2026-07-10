# Stage2E Evidence-Aware Insertion Noise Control Report

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run
- Origin Date: 2026-07-10
- Verification Status: UNVERIFIED
- Version Label: exp_result_v1
- Stage: Stage2E evidence-aware insertion noise control
- Units: `E:\科研\超粒球RAG_数据\processed\stage1_sample400_units.jsonl`
- Queries: `E:\科研\超粒球RAG_数据\processed\stage1_sample400_queries.jsonl`
- Embedding cache: `E:\科研\超粒球RAG_数据\processed\stage2_dense_allminilm_embeddings.npz`
- Gold labels used for indexing: No
- Generator used: No
- Strategy: preserve a dense-fixed prefix, then insert only hyperedge candidates that meet label-free score thresholds.

## Experiment Result

- ID: stage2e_insert_noise_control_sample400
- Type: analysis
- Status: completed
- Command: `python scripts/stage2e_insert_noise_control.py --units "E:\科研\超粒球RAG_数据\processed\stage1_sample400_units.jsonl" --queries "E:\科研\超粒球RAG_数据\processed\stage1_sample400_queries.jsonl" --embedding-cache "E:\科研\超粒球RAG_数据\processed\stage2_dense_allminilm_embeddings.npz" --output-dir "results" --report "reports\超粒球RAG_Stage2E_InsertNoiseControl报告.md" --expand-boundary-only`
- Working Directory: `E:\科研\HyperGranular-RAG`
- Duration: 2.21 seconds
- Exit Code: 0

### Output Files

| File | Size |
|---|---:|
| `results\stage2e_insert_noise_control_summary.csv` | 46114 bytes |
| `results\stage2e_insert_noise_control_delta.csv` | 11017 bytes |

### Anomalies Detected

None during the successful Python 3.12 run. The default Anaconda Python 3.11 environment was excluded after a separate pre-run import diagnostic exposed a NumPy binary-compatibility warning.

## Threshold Protocol

- Thresholds are computed separately for each method from all selected expansion candidates using only dense similarity and selected-edge facet score.
- The filter grid is: none; score q25/q50/q75; score q50 + facet q50; score q75 + facet q50.
- This is an exploratory sensitivity analysis: the same 400 queries supply the candidate-pool quantiles and the labelled evaluation, so it is not a held-out hyperparameter test.

## ALL Summary

| Strategy | Filter | Protect | Insert | Score floor | Facet floor | Retain | Fill | ER@10 | CR@10 | ER@20 | CR@20 | False insert |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed | fixed | 0 | 0 | - | - | 0.0000 | 0.0000 | 0.7788 | 0.5625 | 0.9209 | 0.8250 | 0.0000 |
| protected_insert_filtered | none | 5 | 2 | - | - | 1.0000 | 0.4713 | 0.8029 | 0.6100 | 0.9313 | 0.8425 | 0.8727 |
| protected_insert_filtered | score_q25 | 5 | 4 | 0.1957 | - | 0.7500 | 0.3312 | 0.8058 | 0.6125 | 0.9441 | 0.8700 | 0.8774 |
| protected_insert_filtered | score_q25 | 10 | 4 | 0.1957 | - | 0.7500 | 0.2762 | 0.7788 | 0.5625 | 0.9493 | 0.8825 | 0.8733 |
| protected_insert_filtered | score_q50 | 5 | 2 | 0.3167 | - | 0.5000 | 0.2825 | 0.7958 | 0.5950 | 0.9292 | 0.8375 | 0.8407 |

## Observed Rows

- Unfiltered gated reference (protect=5, insert=2): CR@10=0.6100, CR@20=0.8425, false insert=0.8727.
- Best filtered CR@10: score_q25 / protect=5 / insert=4 / CR@10=0.6125.
- Best filtered CR@20: score_q25 / protect=10 / insert=4 / CR@20=0.8825.
- Lowest false insert among filtered rows with CR@10 no lower than dense fixed and at least 0.5 inserted units/query: score_q50 / protect=5 / insert=2 / false insert=0.8407.

## Query-Level CR Delta vs Dense Fixed

| Filter | Protect | Insert | Metric | Improved | Same | Regressed |
|---|---:|---:|---|---:|---:|---:|
| none | 5 | 2 | chain_recall_at_10 | 23 | 373 | 4 |
| none | 5 | 2 | chain_recall_at_20 | 8 | 391 | 1 |
| none | 5 | 4 | chain_recall_at_10 | 36 | 348 | 16 |
| none | 5 | 4 | chain_recall_at_20 | 20 | 379 | 1 |
| score_q50 | 5 | 2 | chain_recall_at_10 | 14 | 385 | 1 |
| score_q50 | 5 | 2 | chain_recall_at_20 | 5 | 395 | 0 |
| score_q50 | 5 | 4 | chain_recall_at_10 | 20 | 372 | 8 |
| score_q50 | 5 | 4 | chain_recall_at_20 | 11 | 389 | 0 |
| score_q50_facet_q50 | 5 | 2 | chain_recall_at_10 | 14 | 385 | 1 |
| score_q50_facet_q50 | 5 | 2 | chain_recall_at_20 | 6 | 394 | 0 |
| score_q50_facet_q50 | 5 | 4 | chain_recall_at_10 | 16 | 382 | 2 |
| score_q50_facet_q50 | 5 | 4 | chain_recall_at_20 | 10 | 390 | 0 |
| score_q75 | 5 | 2 | chain_recall_at_10 | 7 | 392 | 1 |
| score_q75 | 5 | 2 | chain_recall_at_20 | 3 | 397 | 0 |
| score_q75 | 5 | 4 | chain_recall_at_10 | 9 | 387 | 4 |
| score_q75 | 5 | 4 | chain_recall_at_20 | 4 | 396 | 0 |

## Interpretation Boundary

- The CSV records retrieval metrics only; no answer generator is evaluated.
- False insert rate is the share of inserted units that are not labelled gold. It is not a measure of generative hallucination.
- A noise-control claim requires a lower false insert rate together with the target-K chain-recall comparison. A lower false insert rate caused only by empty insertion is not sufficient evidence.
