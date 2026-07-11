# Reproducibility Notes

## Current Data Boundary

This repository currently tracks scripts, reports, and compact CSV summaries.
It does not track raw datasets, processed JSONL corpora, dense embedding caches,
or per-query detail JSONL files.

Local paths used in the current workstation:

- Processed data: `E:\科研\超粒球RAG_数据\processed`
- Report outputs: `E:\科研\超粒球RAG_数据\reports`
- Stage reports: `E:\科研`

## Known Environment Note

Dense experiments completed with NumPy/numexpr/pandas compatibility warnings in
the current environment. The processes exited successfully and produced result
files, but a cleaner environment should pin compatible package versions before
paper-grade reproduction.

## Current Verification Commands

Syntax checks:

```powershell
python -m py_compile scripts/stage2_dense_replication.py
python -m py_compile scripts/stage2_dense_protection_compare.py
```

Stage2C comparison:

```powershell
python scripts/stage2_dense_protection_compare.py
```

The comparison script currently assumes the original local report directory:
`E:\科研\超粒球RAG_数据\reports`.

Stage2D protected reranking:

```powershell
python scripts/stage2d_protected_rerank.py `
  --units "E:\科研\超粒球RAG_数据\processed\stage1_sample400_units.jsonl" `
  --queries "E:\科研\超粒球RAG_数据\processed\stage1_sample400_queries.jsonl" `
  --embedding-cache "E:\科研\超粒球RAG_数据\processed\stage2_dense_allminilm_embeddings.npz" `
  --output-dir results `
  --report "reports\超粒球RAG_Stage2D_ProtectedDenseRerank报告.md" `
  --expand-boundary-only
```

Stage2E evidence-aware insertion filtering was run with the Python 3.12
interpreter that successfully imports the current NumPy/Torch/Transformers
stack. The default `python` command currently points to an Anaconda Python 3.11
environment with a NumPy binary-compatibility warning, so it was not used for
the final Stage2E run.

```powershell
& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" `
  scripts/stage2e_insert_noise_control.py `
  --units "E:\科研\超粒球RAG_数据\processed\stage1_sample400_units.jsonl" `
  --queries "E:\科研\超粒球RAG_数据\processed\stage1_sample400_queries.jsonl" `
  --embedding-cache "E:\科研\超粒球RAG_数据\processed\stage2_dense_allminilm_embeddings.npz" `
  --output-dir results `
  --report "reports\超粒球RAG_Stage2E_InsertNoiseControl报告.md" `
  --expand-boundary-only
```

Expected compact outputs:

- `results/stage2e_insert_noise_control_summary.csv`
- `results/stage2e_insert_noise_control_delta.csv`
- `reports/超粒球RAG_Stage2E_InsertNoiseControl报告.md`

Per-query details are not generated unless `--write-details` is supplied.

## Stage2F Independent Validation

Stage2F was pre-registered in `docs/STAGE2F_PROTOCOL.md` before test metrics were read. The test corpus uses raw rows `[200:400)` from each source dataset; the earlier `[0:200)` calibration queries are passed separately so the validation script can enforce zero query-ID overlap.

Test-slice extraction:

```powershell
& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" `
  scripts/stage0_dataset_probe.py `
  --dataset hotpotqa `
  --input "E:\科研\超粒球RAG_数据\raw\hotpot_dev_distractor_v1.json" `
  --output "E:\科研\超粒球RAG_数据\processed\stage2f_hotpotqa_unseen200_unified.json" `
  --report "E:\科研\超粒球RAG_数据\reports\stage2f_hotpotqa_unseen_probe.md" `
  --offset 200 --limit 200
```

Run the same command for MuSiQue with dataset `musique`, input `musique_ans_v1.0_dev.jsonl`, and the corresponding `stage2f_musique_*` output paths. Then combine both unified files with `scripts/stage1_build_corpus.py` into `stage2f_unseen400_units.jsonl` and `stage2f_unseen400_queries.jsonl`.

Frozen-threshold validation:

```powershell
& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" `
  scripts/stage2f_frozen_threshold_validation.py `
  --units "E:\科研\超粒球RAG_数据\processed\stage2f_unseen400_units.jsonl" `
  --queries "E:\科研\超粒球RAG_数据\processed\stage2f_unseen400_queries.jsonl" `
  --calibration-queries "E:\科研\超粒球RAG_数据\processed\stage1_sample400_queries.jsonl" `
  --calibration-summary results/stage2e_insert_noise_control_summary.csv `
  --embedding-cache "E:\科研\超粒球RAG_数据\processed\stage2f_dense_allminilm_embeddings.npz" `
  --output-dir results `
  --report "reports\超粒球RAG_Stage2F_FrozenThreshold验证报告.md" `
  --expand-boundary-only
```

Expected tracked outputs:

- `results/stage2f_frozen_threshold_summary.csv`
- `results/stage2f_frozen_threshold_bootstrap.csv`
- `reports/超粒球RAG_Stage2F_FrozenThreshold验证报告.md`
- `reports/超粒球RAG_Stage2F_StatisticalValidation.md`

The local test JSON/JSONL files and `stage2f_dense_allminilm_embeddings.npz` are intentionally not tracked. A deterministic rerun must produce byte-identical summary and bootstrap CSV files; timing and report paths are excluded from the equality check.

## Stage2G Boundary-Mechanism Audit

Stage2G uses raw rows `[400:600)` from each source dataset. Extract them with `scripts/stage0_dataset_probe.py --offset 400 --limit 200`, then combine them with `scripts/stage1_build_corpus.py` into `stage2g_unseen400_units.jsonl` and `stage2g_unseen400_queries.jsonl`.

Mechanism audit:

```powershell
& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" `
  scripts/stage2g_boundary_mechanism_audit.py `
  --units "E:\科研\超粒球RAG_数据\processed\stage2g_unseen400_units.jsonl" `
  --queries "E:\科研\超粒球RAG_数据\processed\stage2g_unseen400_queries.jsonl" `
  --prior-queries `
    "E:\科研\超粒球RAG_数据\processed\stage1_sample400_queries.jsonl" `
    "E:\科研\超粒球RAG_数据\processed\stage2f_unseen400_queries.jsonl" `
  --calibration-summary results/stage2e_insert_noise_control_summary.csv `
  --embedding-cache "E:\科研\超粒球RAG_数据\processed\stage2g_dense_allminilm_embeddings.npz" `
  --output-dir results `
  --report "reports\超粒球RAG_Stage2G_BoundaryMechanism报告.md"
```

Expected tracked outputs:

- `results/stage2g_boundary_mechanism_summary.csv`
- `results/stage2g_boundary_mechanism_bootstrap.csv`
- `reports/超粒球RAG_Stage2G_BoundaryMechanism报告.md`
- `reports/超粒球RAG_Stage2G_StatisticalValidation.md`

The local Stage2G JSON/JSONL files and `stage2g_dense_allminilm_embeddings.npz` remain untracked. A deterministic rerun must produce byte-identical summary and bootstrap CSV files; timing and report paths are excluded from equality checks.

## Stage2H Boundary-Rule Failure Diagnosis

Stage2H reuses the already evaluated Stage2E-F-G slices only for exploratory diagnosis. It does not fit or validate a replacement threshold. Run the diagnosis with the three existing embedding caches:

```powershell
& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" `
  scripts/stage2h_boundary_failure_diagnosis.py `
  --corpus stage2e `
    "E:\科研\超粒球RAG_数据\processed\stage1_sample400_units.jsonl" `
    "E:\科研\超粒球RAG_数据\processed\stage1_sample400_queries.jsonl" `
    "E:\科研\超粒球RAG_数据\processed\stage2_dense_allminilm_embeddings.npz" `
  --corpus stage2f `
    "E:\科研\超粒球RAG_数据\processed\stage2f_unseen400_units.jsonl" `
    "E:\科研\超粒球RAG_数据\processed\stage2f_unseen400_queries.jsonl" `
    "E:\科研\超粒球RAG_数据\processed\stage2f_dense_allminilm_embeddings.npz" `
  --corpus stage2g `
    "E:\科研\超粒球RAG_数据\processed\stage2g_unseen400_units.jsonl" `
    "E:\科研\超粒球RAG_数据\processed\stage2g_unseen400_queries.jsonl" `
    "E:\科研\超粒球RAG_数据\processed\stage2g_dense_allminilm_embeddings.npz" `
  --calibration-summary results/stage2e_insert_noise_control_summary.csv `
  --output-dir results `
  --report "reports\超粒球RAG_Stage2H_BoundaryFailureDiagnosis报告.md"
```

Expected tracked outputs:

- `results/stage2h_boundary_query_audit.csv`
- `results/stage2h_boundary_component_summary.csv`
- `results/stage2h_boundary_predictive_metrics.csv`
- `reports/超粒球RAG_Stage2H_BoundaryFailureDiagnosis报告.md`
- `reports/超粒球RAG_Stage2H_StatisticalValidation.md`

The deterministic verification uses 10,000 stratified bootstrap iterations with seed `20260712`. All three CSV files must match byte-for-byte; the verified SHA-256 values are recorded in the statistical validation report. Timing and report paths are excluded from equality checks.

## Stage3A Utility-Controller Development

Stage3A uses HotpotQA and MuSiQue source rows `[600:1000)` for development. The query IDs for `[1000:1400)` are reserved in `docs/STAGE3_DATA_RESERVATION.json`; the script verifies their digest but does not embed or score those Stage3B queries.

```powershell
& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" `
  scripts/stage3a_utility_controller.py `
  --units "E:\科研\超粒球RAG_数据\processed\stage3a_dev800_units.jsonl" `
  --queries "E:\科研\超粒球RAG_数据\processed\stage3a_dev800_queries.jsonl" `
  --prior-queries `
    "E:\科研\超粒球RAG_数据\processed\stage1_sample400_queries.jsonl" `
    "E:\科研\超粒球RAG_数据\processed\stage2f_unseen400_queries.jsonl" `
    "E:\科研\超粒球RAG_数据\processed\stage2g_unseen400_queries.jsonl" `
  --hotpot-source "E:\科研\超粒球RAG_数据\raw\hotpot_dev_distractor_v1.json" `
  --musique-source "E:\科研\超粒球RAG_数据\raw\musique\data\musique_ans_v1.0_dev.jsonl" `
  --reservation docs/STAGE3_DATA_RESERVATION.json `
  --calibration-summary results/stage2e_insert_noise_control_summary.csv `
  --embedding-cache "E:\科研\超粒球RAG_数据\processed\stage3a_dev800_dense_allminilm_embeddings.npz" `
  --output-dir results `
  --report "reports\超粒球RAG_Stage3A_UtilityController开发报告.md"
```

Expected tracked outputs:

- `results/stage3a_utility_controller_query_audit.csv`
- `results/stage3a_utility_controller_model.json`
- `results/stage3a_utility_controller_summary.csv`
- `results/stage3a_utility_controller_bootstrap.csv`
- `reports/超粒球RAG_Stage3A_UtilityController开发报告.md`
- `reports/超粒球RAG_Stage3A_StatisticalValidation.md`

The development bootstrap uses 10,000 dataset-stratified resamples with seed `20260713`. A deterministic rerun must reproduce all four core CSV/JSON artifacts byte-for-byte. Stage3A's promotion decision is `FAIL`; reproduction must preserve that decision rather than recomputing a different threshold or relaxing the sparse-target fallback gate.
