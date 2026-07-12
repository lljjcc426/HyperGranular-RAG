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

## Stage3C Target-Feasibility Audit

Stage3C reads only tracked Stage2H and Stage3A artifacts. It does not require raw datasets, embeddings, network access, or Stage3B files.

```powershell
& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" `
  scripts/stage3c_target_feasibility_audit.py `
  --stage2h-audit results/stage2h_boundary_query_audit.csv `
  --stage3a-audit results/stage3a_utility_controller_query_audit.csv `
  --stage3a-model results/stage3a_utility_controller_model.json `
  --reservation docs/STAGE3_DATA_RESERVATION.json `
  --summary-output results/stage3c_event_feasibility_summary.csv `
  --decision-output results/stage3c_target_feasibility_decision.json `
  --report "reports\超粒球RAG_Stage3C_TargetFeasibilityAudit报告.md"
```

Expected tracked outputs:

- `results/stage3c_event_feasibility_summary.csv`
- `results/stage3c_target_feasibility_decision.json`
- `docs/STAGE3C_DATASET_SCREEN.md`
- `reports/超粒球RAG_Stage3C_TargetFeasibilityAudit报告.md`
- `reports/超粒球RAG_Stage3C_StatisticalValidation.md`

The internal audit is deterministic. The summary CSV and decision JSON must match byte-for-byte; source-linked dataset screening is separately verified against the authoritative pages recorded in `docs/STAGE3C_DATASET_SCREEN.md`.

## Stage4A 2Wiki Feasibility Pilot

Stage4A uses validation rows `[0:400)` for the pilot and reads rows `[400:800)` only to record reservation IDs. The PowerShell transport writes raw payloads for the pilot pages but writes no reservation questions, answers, contexts, or evidence. Use an empty cache directory:

```powershell
& .\scripts\stage4a_fetch_2wiki_pages.ps1 `
  -CacheDir "E:\科研\超粒球RAG_数据\temp\stage4a_api_cache_fresh"

& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" `
  scripts\stage4a_fetch_2wiki_pilot.py `
  --api-cache-dir "E:\科研\超粒球RAG_数据\temp\stage4a_api_cache_fresh" `
  --pilot-output "E:\科研\超粒球RAG_数据\processed\stage4a_2wiki_pilot400_unified.json" `
  --source-audit docs\STAGE4A_SOURCE_AUDIT.json

& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" `
  scripts\stage1_build_corpus.py `
  --inputs "E:\科研\超粒球RAG_数据\processed\stage4a_2wiki_pilot400_unified.json" `
  --units-output "E:\科研\超粒球RAG_数据\processed\stage4a_2wiki_pilot400_units.jsonl" `
  --queries-output "E:\科研\超粒球RAG_数据\processed\stage4a_2wiki_pilot400_queries.jsonl" `
  --report "E:\科研\超粒球RAG_数据\processed\stage4a_2wiki_pilot400_corpus_report.md"

& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" `
  scripts\stage4a_2wiki_feasibility.py `
  --units "E:\科研\超粒球RAG_数据\processed\stage4a_2wiki_pilot400_units.jsonl" `
  --queries "E:\科研\超粒球RAG_数据\processed\stage4a_2wiki_pilot400_queries.jsonl" `
  --source-audit docs\STAGE4A_SOURCE_AUDIT.json `
  --embedding-cache "E:\科研\超粒球RAG_数据\processed\stage4a_2wiki_pilot400_minilm_embeddings.npz" `
  --output-dir results `
  --report "reports\超粒球RAG_Stage4A_2WikiFeasibilityPilot报告.md"

& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" `
  scripts\stage4a_verify_outputs.py `
  --query-audit results\stage4a_2wiki_query_audit.csv `
  --summary results\stage4a_2wiki_strategy_summary.csv `
  --bootstrap results\stage4a_2wiki_bootstrap.csv `
  --source-audit docs\STAGE4A_SOURCE_AUDIT.json `
  --report "reports\超粒球RAG_Stage4A_2WikiFeasibilityPilot报告.md" `
  --output results\stage4a_2wiki_verification.json
```

Expected tracked outputs:

- `docs/STAGE4A_SOURCE_AUDIT.json`
- `results/stage4a_2wiki_query_audit.csv`
- `results/stage4a_2wiki_strategy_summary.csv`
- `results/stage4a_2wiki_bootstrap.csv`
- `results/stage4a_2wiki_verification.json`
- `reports/超粒球RAG_Stage4A_2WikiFeasibilityPilot报告.md`

The verifier independently recomputes all query events, 15 ALL/type summary rows, Wilson intervals, and six paired-bootstrap rows with 10,000 resamples and seed `20260714`. The verified decision is `STOP`; reproduction must preserve the frozen q25 threshold and must not evaluate the reserved Stage4B slice.

### Official April 7 Archive Reconciliation

The official archive is supplied locally by the user and is never committed. Reconciliation is source-only and does not rerun retrieval metrics:

```powershell
& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" `
  scripts\stage4a_reconcile_official_archive.py `
  --official-zip "C:\Users\cc\Downloads\data_ids_april7.zip" `
  --mirror-cache "E:\科研\超粒球RAG_数据\temp\stage4a_api_cache_20260711" `
  --pilot-unified "E:\科研\超粒球RAG_数据\processed\stage4a_2wiki_pilot400_unified.json" `
  --output docs\STAGE4A_OFFICIAL_RECONCILIATION.json
```

Additional tracked audit outputs:

- `docs/STAGE4A_OFFICIAL_RECONCILIATION.json`
- `docs/STAGE4A_DESIGN_AUDIT.md`

The expected official ZIP SHA-256 is `95DF2BF56FDABE034E27AEBC580E02264232203CF52552F9EFE8A919E5529EEF`. Reconciliation must preserve the observed 7 context-content mismatches, 5 gold-evidence text mismatches, and exact ordered reservation-ID match. These findings supersede the earlier assumption that the pinned mirror was content-equivalent to the official April 7 archive.

## Restarted Stage4A Event-count Lower Bound

The restarted Stage4A has not started data extraction. The returned draft's event-count lower bound is generated deterministically:

```powershell
& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" `
  scripts\stage4a_restart_plan_sample_size.py `
  --event-target 20 `
  --minimum-prevalence 0.01 `
  --target-probability 0.95 `
  --round-to 100 `
  --excluded-prefix 800 `
  --official-dev-rows 12576 `
  --expected-base-invalid 19 `
  --output docs\STAGE4A_RESTART_SAMPLE_SIZE_PLAN.json
```

Expected SHA-256 for `docs/STAGE4A_RESTART_SAMPLE_SIZE_PLAN.json`:

`92B080D66D67A6B6B3708AF03D9272F2F7564FAA719639B1FACFDDB2431DECCC`

The exact minimum is 2,784 and the rounded lower bound is 2,800, yielding probability 0.952994 of at least 20 gains when true prevalence is 0.01. The prior-stage audit established that 20 is a planning heuristic and 0.01 is a sensitivity assumption informed by the invalidated mirror pilot. This is not retrieval-effect power, prevalence-precision design, or controller-training adequacy. `docs/STAGE4A_RESTART_PROTOCOL_DRAFT.md` is returned for design revision and cannot be approved for execution in its current form.

## Stage4A-R2 Official Event-rate Estimation

Generate the frozen precision and secondary paired-power design:

```powershell
& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" scripts\stage4a_r2_plan_sample_size.py `
  --planning-prevalence 0.03 `
  --target-halfwidth 0.005 `
  --development-n 4500 `
  --reservation-n 4500 `
  --excluded-prefix 800 `
  --official-dev-rows 12576 `
  --mcnemar-discordance 0.05 `
  --mcnemar-net-gain 0.01 `
  --alpha 0.05 `
  --target-power 0.80 `
  --output docs\STAGE4A_R2_SAMPLE_SIZE_PLAN.json
```

Expected SHA-256 after approved Amendment 1: `84C9AD227F5D75BA2D3060D9AF3D285230DCE1799D96E88D21338813E41BFA5E`.

After the protocol, Amendment 1, and amended code commit, extract the 4,481 valid base rows plus 19 deterministic QC replacements; retain reservation IDs only:

```powershell
& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" scripts\stage4a_r2_extract_official.py `
  --official-zip "C:\Users\cc\Downloads\data_ids_april7.zip" `
  --development-output "E:\科研\超粒球RAG_数据\processed\stage4a_r2_official_dev4500_unified.json" `
  --source-audit docs\STAGE4A_R2_SOURCE_AUDIT.json

& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" scripts\stage1_build_corpus.py `
  --inputs "E:\科研\超粒球RAG_数据\processed\stage4a_r2_official_dev4500_unified.json" `
  --units-output "E:\科研\超粒球RAG_数据\processed\stage4a_r2_official_dev4500_units.jsonl" `
  --queries-output "E:\科研\超粒球RAG_数据\processed\stage4a_r2_official_dev4500_queries.jsonl" `
  --report "E:\科研\超粒球RAG_数据\processed\stage4a_r2_official_dev4500_corpus_report.md"
```

Run the frozen retrieval and inference:

```powershell
& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" scripts\stage4a_r2_official_estimation.py `
  --units "E:\科研\超粒球RAG_数据\processed\stage4a_r2_official_dev4500_units.jsonl" `
  --queries "E:\科研\超粒球RAG_数据\processed\stage4a_r2_official_dev4500_queries.jsonl" `
  --source-audit docs\STAGE4A_R2_SOURCE_AUDIT.json `
  --sample-plan docs\STAGE4A_R2_SAMPLE_SIZE_PLAN.json `
  --embedding-cache "E:\科研\超粒球RAG_数据\processed\stage4a_r2_official_dev4500_minilm_embeddings.npz" `
  --output-dir results `
  --report "reports\超粒球RAG_Stage4A_R2官方事件率估计报告.md"
```

Independently verify every tracked metric:

```powershell
& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" scripts\stage4a_r2_verify_outputs.py `
  --query-audit results\stage4a_r2_query_audit.csv `
  --summary results\stage4a_r2_strategy_summary.csv `
  --bootstrap results\stage4a_r2_bootstrap.csv `
  --inference results\stage4a_r2_inference.json `
  --source-audit docs\STAGE4A_R2_SOURCE_AUDIT.json `
  --report "reports\超粒球RAG_Stage4A_R2官方事件率估计报告.md" `
  --output results\stage4a_r2_verification.json
```

Local unified data, JSONL corpora, mapping report, and embedding cache remain untracked. The reservation contributes only an ID digest and is never embedded or scored.

Verified Stage4A-R2 SHA-256 values:

| Artifact | SHA-256 |
|---|---|
| `results/stage4a_r2_query_audit.csv` | `766D7344A8093D2CBA10507B0DEE83A42575D9EDE986DD3212822BC96701034A` |
| `results/stage4a_r2_strategy_summary.csv` | `7BF79CC057CDD0565100B1D95F35C95BFBEAA338E9B1EF63D9E81F029BB42B12` |
| `results/stage4a_r2_bootstrap.csv` | `FF1D47BBCDF969C7CCDFCF66FA5AAFB1F655C3393590C492C33E46C5C706F5F0` |
| `results/stage4a_r2_inference.json` | `9AE75704BDC18628AD13BE29FBEF5CC42A498478D5DE02154BC5B10ECCD7A38F` |

A deterministic rerun using the frozen embedding cache must reproduce all four hashes exactly. Report duration is excluded from byte-level comparison.
