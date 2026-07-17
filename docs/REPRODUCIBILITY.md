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

## Stage4B-U1 v2.2 Synthetic-only Execution Hardening

This command uses generated fixtures under the OS temporary directory. It does not read official U1-D, reservation, or Stage3B data:

```powershell
& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" `
  scripts\stage4b_u1_run_synthetic_verification.py
```

Expected result: 24 tests, 0 failures, 0 errors, 0 skipped. Expected SHA-256 for `results/stage4b_u1_synthetic_verification.json`:

`8B3057238D67EBE874017068C125126974062C61FAF3D79595E884F16A876D7D`

The v2.2 runner preserves the v2.1 Gold isolation, legacy-ranking equivalence, numeric boundaries, exact ECDF behavior, 60% prefix allocation, dense/q25 identity, synthetic reservation-ECDF reuse, and all prior failure injections. Four additional tests reject formal sample-ID drift, runtime query-ID drift, malformed `query_id == dataset::sample_id`, and controller-audit dual-digest drift. This remains implementation evidence only and cannot authorize U1-D execution.

The SHA above is the final post-Amendment-2 implementation binding rerun after governance commit `437b35e`. It binds the final `AGENTS.md`, protocol, implementation, runner, and 24-test suite bytes and reproduced byte-identically twice. The evidence reports no official-development, official-source-audit, reservation, or Stage3B access. Historical SHAs `9AA0D0499ECF613F7FEAED0F078BB7534CB837C22465AA1F13F29D715BBE8A6A`, `6F97EE054EFEACEC0BD50414D1A3133CB23D9B6FC57462356147C06AF804C7A5`, and `799E2AE73F24C223FA28AB104AF5C830F2E4D7678795B5CB5C8F51DC32D39AC3` remain recorded in prior checkpoints.

The package-style command `python -m unittest tests.test_stage4b_u1_goldfree -v` is not valid under the pinned Python 3.12 runtime because `tests` is not a package. For direct verbose testing, use:

```powershell
& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" `
  -m unittest discover -s tests -p "test_stage4b_u1_goldfree.py" -v
```

## Stage4B-U1-D Pre-Gold Hard Failure 1

The approved official preflight stopped before channel preparation. The legacy Stage4A-R2 cache had SHA-256 `746FC1130038C789190F2A37CB911BBFC46905CFCC138E361C1F6CF991A45F02` and exposed only:

```text
model_name
query_embeddings
unit_embeddings
```

It lacked `unit_ids`, `query_ids`, and `max_length`, so it failed the v2.1 ID-bound cache gate. The failure audit is `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_1.md`.

Do not patch, migrate, overwrite, or delete the legacy cache. The fresh-cache procedure in `docs/STAGE4B_U1_PREGOLD_AMENDMENT_1_DRAFT.md` was approved on 2026-07-13, bound to amendment commit `a7e121584d9f512bb7b4abaabdb9c93913ad560d` and implementation commit `dd1f8a9893ccb1e760068ad21d48e0e8938cc7f9`.

The single approved new path is:

```text
E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_minilm_idbound_embeddings.npz
```

Amendment 1 required approval governance and post-amendment synthetic binding evidence to be pushed before formal preflight; both were completed. That preflight then stopped at Hard Failure 2 below. The new cache path remained absent.

## Stage4B-U1-D Pre-Gold Hard Failure 2

The Amendment 1 formal preflight stopped before channel preparation because two ID representations were compared as if they were identical:

| ID representation | SHA-256 |
|---|---|
| official `_id` / processed `sample_id` | `6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2` |
| processed `query_id = 2wikimultihopqa::<sample_id>` | `8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6` |

The full failure record is `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_2.md`. No channel, cache, controller artifact, verifier artifact, or metric was generated. Do not rerun official preflight under Amendment 1.

`docs/STAGE4B_U1_PREGOLD_AMENDMENT_2_DRAFT.md` freezes a dual-ID boundary correction. Its first approval would authorize implementation and synthetic verification only; official development remains locked pending a later implementation-bound approval.

Amendment 2 implementation and synthetic verification were approved on 2026-07-13, bound to commit `dde5a28fec476fddd0ac82ebad39d9eeab0bea1e`. This approval does not permit reading official development or running any official Stage4B-U1 command. After implementation, the complete synthetic suite and deterministic evidence must be committed and pushed before a new official-resumption approval is requested.

The Amendment 2 implementation checkpoint is `stage4b_u1_v2_2`. The suite contains the original 20 tests plus four dual-ID boundary hardening tests. The current expected SHA is `8B3057238D67EBE874017068C125126974062C61FAF3D79595E884F16A876D7D`. Official development remains locked.

The implementation-bound official pre-Gold resumption request is `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_2_APPROVAL_REQUEST.md`, with machine-readable binding in `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_2_MANIFEST.json`. These files do not authorize execution. Do not run official commands until the package commit and implementation commit `ca2cca332292f7bd6af12e2a429100be11da5549` are explicitly approved.

## Stage4B-U1-D v2.2 Official Pre-Gold Resumption Approval

The user approved `APPROVE_STAGE4B_U1_D_V2_2_OFFICIAL_PREGOLD_RESUMPTION` on 2026-07-13, binding request-package commit `fae181564504f1a69bcebfd5d5201eea7e2d9abf` and implementation commit `ca2cca332292f7bd6af12e2a429100be11da5549`. The approval decision is `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_2_APPROVAL_DECISION.md`.

The approval first requires a committed and pushed governance state, followed by two complete 24-test synthetic binding runs whose output bytes are identical. Only after that hard gate may one dual-ID formal preflight access the registered official development inputs. The remaining authorized sequence is one channel preparation, one fresh ID-bound cache and Gold-free controller run, an independent read-only cache audit, committed channel/controller artifacts, and an independent verifier producing `VERIFIED_PRE_GOLD` with `evaluation=null`.

Any formal preflight, cache audit, commit, or push hard-gate failure stops execution without automatic retry. Gold evaluation, U1-D metric access or interpretation, promotion, reservation, Stage3B, and implementation or parameter changes remain prohibited.

The approval governance state was committed and pushed as `c13be1f`. On those governance bytes, the complete 24-test synthetic binding runner was executed twice. Both runs passed with zero failures, errors, or skips and produced byte-identical canonical output with SHA-256 `9B01C80F66096F01C763C25E44E4D079C40B681F6C52F0CC55F70492689EAAB1`. All 12 implementation/governance hashes in the evidence match current bytes. The rebinding audit is `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_2_SYNTHETIC_REBINDING_AUDIT.md`; the next authorized operation is one read-only dual-ID formal preflight.

The single dual-ID formal preflight passed and is recorded in `docs/STAGE4B_U1_PREGOLD_V2_2_FORMAL_PREFLIGHT_AUDIT.md`. It verified repository alignment, 143,820 unique unit IDs, 4,500 unique sample/query IDs, the exact per-row namespace relation, both frozen digests, source-audit SHA, unchanged legacy cache SHA, and absence of all ten fresh output paths before channel execution.

The channel preparer and Gold-free controller were each run once. The controller used `sentence-transformers/all-MiniLM-L6-v2`, `max_length=192`, and `batch_size=64`; it produced 4,500 decisions and rankings with policy status `POLICY_FROZEN_BEFORE_EVALUATION` and `evaluation_labels_loaded=false`. The execution audit is `docs/STAGE4B_U1_PREGOLD_V2_2_CONTROLLER_EXECUTION_AUDIT.md`.

The fresh cache was independently checked without the controller cache loader. Its six members, exact ID order, dual digests, metadata, `float32` shapes, finite values, normalization, byte size, and SHA-256 all passed. The audit is `docs/STAGE4B_U1_PREGOLD_V2_2_CACHE_AUDIT.md`. The fresh cache remains untracked in the registered data directory; the legacy cache remains unchanged.

## Stage4B-U1-D Pre-Gold Hard Failure 3

The independent verifier was executed once on committed artifact commit `9207bd78eea44d2ea3291fe9b6748526969a3224`, without Gold or evaluator arguments. It failed before writing output because `derive_q25_inserted` required exactly 20 dense/q25 IDs for every query. The first failed query had 17 candidate units and 17 dense/q25/final IDs.

A post-stop Gold-free structural scan read only `num_candidate_units` and ranking list lengths. It found 628/4,500 queries below 20 candidates, with minimum 10. Every controller ranking length was exactly `min(20, num_candidate_units)`; the effective-K mismatch count was zero. This does not validate score, allocation, ranking order, or efficacy. Full evidence and the no-retry boundary are in `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_3.md`.

`VERIFIED_PRE_GOLD` was not generated. Existing artifacts remain committed but are `UNVERIFIED_INVALID_FOR_GOLD`. Amendment 3 in `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_DRAFT.md` proposes an effective-K verifier invariant and requests implementation/synthetic authorization only. No official command may resume before a new approval and a later implementation-bound resumption approval.

The implementation/synthetic-only approval request is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_APPROVAL_REQUEST.md`, with machine-readable scope in `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_MANIFEST.json`. It is bound to failure/audit commit `8b43de72418ccda85af3015f758c39bce9d31411`. The package itself does not authorize implementation or any execution.

Amendment 3 implementation and synthetic hardening were approved on 2026-07-13, binding approval-package commit `42747507d6f37c3d5713949de443311b35262a2d` and failure-audit commit `8b43de72418ccda85af3015f758c39bce9d31411`. The decision is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_APPROVAL_DECISION.md`. Authorization is limited to effective-K protocol/checkpoint/verifier/runner/test changes, synthetic fixtures, two byte-identical complete evidence runs, implementation audit, and a new implementation-bound resumption request. Official development, source audit, official rankings, official commands, caches, Gold, reservation, and Stage3B remain prohibited.

## Stage4B-U1-D Pre-Gold Amendment 3 Synthetic Verification

The implementation checkpoint is `stage4b_u1_v2_3`. The independent verifier now computes `K_q=min(20,|C_q|)` and `P_q=min(10,K_q)` from its independently reconstructed candidate pool. It hard-fails empty pools, candidate-count drift, wrong effective-K lengths, duplicate IDs, non-candidate IDs, protected-prefix drift, insertion-range/derivation drift, and final-selector drift.

The original 24 tests were retained and nine effective-K/candidate-pool tests were added. A targeted discovery run passed 9/9, and a complete verbose run passed 33/33 with zero failures, errors, or skips. The deterministic evidence runner then executed twice on unchanged governance, protocol, implementation, and test bytes. Both outputs have SHA-256 `38DDA409C866AAAC6C2AEDBA0D0716DA6F483854E9A6019E9040B9B2B1FA40B5` and are stored at `results/stage4b_u1_d_pregold_amendment_3_synthetic_verification.json`.

The old `results/stage4b_u1_synthetic_verification.json` was not overwritten and retains SHA-256 `9B01C80F66096F01C763C25E44E4D079C40B681F6C52F0CC55F70492689EAAB1`. No official development, source audit, official ranking, cache, verifier, evaluator, Gold, reservation, or Stage3B access occurred. Full file hashes and the failed command-entry record are in `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_IMPLEMENTATION_AUDIT.md`. This result does not authorize official execution.

The implementation and evidence were committed and pushed as `a1d9ea0c517fcbad1ef27e78e760738d5c04d8b3`. The implementation-bound resumption request is `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_APPROVAL_REQUEST.md`, with machine-readable scope in `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_MANIFEST.json`. It requests new versioned channel/controller/verifier paths, read-only reuse of the audited fresh cache, byte-identical decisions/rankings against the frozen v2.2 artifacts, and policy drift limited to registered binding fields. The package is not an execution approval; all official commands remain locked until the user explicitly approves the package commit and implementation commit.

## Stage4B-U1-D v2.3 Resumption Review 1

Package commit `dbb4e057405069aceda5a7c5d88d9d39a4d14775` was returned for protocol and cache fail-closed revision. The review found three blockers: it omitted a complete two-run synthetic rebinding after approval governance is committed; it did not enumerate all ten versioned artifact paths; and the current controller falls back to embedding generation and cache writing when the cache path is absent. External pre/post checks alone do not encode a true no-build invariant inside the controller.

The review is `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_REVIEW_1.md`. Amendment 4 in `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_CACHE_FAIL_CLOSED_DRAFT.md` requests implementation/synthetic-only authorization for an existing-cache-only controller mode, frozen cache SHA and strict pre/post fingerprint validation, dynamic governance-file binding in the synthetic runner, and an exact ten-path artifact registry. Its approval request and manifest are `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_APPROVAL_REQUEST.md` and `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_MANIFEST.json`. No implementation or official execution is authorized yet.

Amendment 4 implementation and synthetic hardening were approved on 2026-07-13, binding package commit `e5a0e2187e770c9d7b9e9a85a6b8e91067ed2af1`, returned package `dbb4e057405069aceda5a7c5d88d9d39a4d14775`, and baseline implementation `a1d9ea0c517fcbad1ef27e78e760738d5c04d8b3`. The decision is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_APPROVAL_DECISION.md`. Authorization covers only checkpoint/cache fail-closed/pending-output/runner-binding/protocol/test changes and synthetic evidence. Official data, official cache, official commands, Gold, reservation, and Stage3B remain prohibited.

## Stage4B-U1-D Pre-Gold Amendment 4 Synthetic Verification

The implementation checkpoint is `stage4b_u1_v2_3_1`. Formal controller mode now rejects load-or-build before input reads, validates the frozen existing cache without calling embedding or cache-write paths, writes candidate outputs only under an OS temporary directory, rechecks the cache fingerprint, enforces frozen v2.2 decision/ranking bytes and a registered policy structural diff, and uses exclusive promotion with rollback. The exact ten v2.3.1 paths are shared by code and manifest.

The original 33 synthetic tests were retained and 17 cache/governance tests were added. The targeted 17-test class and the complete 50-test suite passed with zero failures, errors, or skips. The complete deterministic evidence runner then executed twice on unchanged governance, protocol, implementation, runner, and test bytes. Both outputs have SHA-256 `24F287F9B71C974ABEF9E03AA55BCCA0C4AF9809AB2ADC44705A42EC3889F657` and are stored at `results/stage4b_u1_d_pregold_amendment_4_synthetic_verification.json`.

No official development, source audit, official ranking, v2.2 policy content, real cache, verifier, evaluator, Gold, reservation, or Stage3B access occurred. The prior Amendment 3 evidence remains unchanged. Full hashes and test coverage are in `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_IMPLEMENTATION_AUDIT.md`. This result does not authorize official execution.

The v2.3.1 implementation and evidence were committed and pushed as `34349c70ee24b8240fd169393134d4280968b790`. The implementation-bound resumption request is `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_APPROVAL_REQUEST.md`, with machine-readable scope in `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_MANIFEST.json`.

The package requires approval governance to be committed first, followed by two complete 50-test runs that dynamically bind the committed request, manifest, approval decision, and final `AGENTS.md`. The rebinding evidence and audit must be pushed before formal preflight. It then requests one exact-path channel, one require-existing/no-build controller run with cache pre/post fingerprints and frozen v2.2 equivalence, committed artifacts, and one independent pre-Gold verifier. The package itself is not execution approval.

## Stage4B-U1-D v2.3.1 Official Pre-Gold Resumption Approval

The user approved `APPROVE_STAGE4B_U1_D_V2_3_1_OFFICIAL_PREGOLD_RESUMPTION` on 2026-07-13, binding request-package commit `e76c921454697d1784b0d76a9d9677113051f0f6` and implementation commit `34349c70ee24b8240fd169393134d4280968b790`. The decision is `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_APPROVAL_DECISION.md`.

Execution remains gated on a new committed governance state and two complete 50-test synthetic rebinding runs with byte-identical evidence. The runs must bind the request, manifest, approval decision, and final `AGENTS.md`; their evidence and audit must be committed and pushed before the single formal preflight. The remaining authorized sequence is one exact-path channel, one require-existing controller with frozen cache and v2.2 equivalence gates, committed controller artifacts, and one independent verifier. The endpoint is only `VERIFIED_PRE_GOLD` with `evaluation=null`; Gold, U1-D metrics, reservation, Stage3B, implementation changes, cache writes, and automatic retries remain prohibited.

## Stage4B-U1-D v2.3.1 Post-Approval Synthetic Rebinding

On approval-governance commit `53850f58e57f51b3c6067ed3108edff6b99a2dfc`, the complete 50-test binding runner executed twice with the request, manifest, and approval decision registered as dynamic governance bindings. Both runs passed 50/50 with zero failures, errors, or skips. Both complete evidence outputs are 11,640 bytes and have SHA-256 `9D40C0B9B0C8F03CBC5545CA8F2390CCE9EABDC3B08B041B092FB3A76492FF34`.

The evidence records 22 implementation hashes, including the final approved `AGENTS.md`, and exact hashes for all three dynamic governance files. It reports no official development, source-audit, reservation, or Stage3B access. Both runs emitted a captured optional-dependency warning from the local NumPy 2.4.6/`numexpr` ABI mismatch, but exited zero and produced byte-identical all-pass evidence. The complete command and warning record is in `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_SYNTHETIC_REBINDING_AUDIT.md`. Formal preflight remains blocked until this evidence and audit are committed and pushed.

## Stage4B-U1-D v2.3.1 Formal Preflight

After the rebinding evidence commit was pushed, one independent read-only formal preflight ran on HEAD `a963befd812658972b156d2a7a26a488ac3c4482`. It verified GitHub synchronization, all four bound commits, 22 implementation hashes, three dynamic governance hashes, the 4,500-query/143,820-unit dual-ID boundary, source audit, fresh and legacy caches, all three frozen v2.2 reference hashes, and absence of all ten registered v2.3.1 outputs.

The fresh cache remained 210,714,667 bytes with SHA-256 `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D` before and after full member/ID/model/dtype/shape/finite/normalization validation. No controller, evaluator, retrieval metric, Gold metric, reservation, Stage3B, model encoding, or cache-write path was invoked. Full results are in `docs/STAGE4B_U1_PREGOLD_V2_3_1_FORMAL_PREFLIGHT_AUDIT.md`. The next authorized action is one exact-path versioned channel preparation.

## Stage4B-U1-D v2.3.1 Channel Preparation And Hard Failure 4

One exact-path versioned channel preparation ran on HEAD `8e0bab13ad20c06795dffd5ca71f167a814cdfb0`. Independent validation confirmed 4,500 queries, 143,820 units, both frozen ID digests, no prohibited controller keys, byte-identical unlabeled units/queries relative to v2.2, and unchanged fresh-cache SHA. Evaluator-only Gold files were created at their manifest paths, but the evaluator was not run and no retrieval/Gold metric was computed. The channel audit is `docs/STAGE4B_U1_PREGOLD_V2_3_1_CHANNEL_PREPARATION_AUDIT.md`.

The single approved require-existing controller then wrote pending artifacts only under an OS temporary directory, passed the post-computation cache fingerprint, and hard-failed at the first frozen v2.2 equivalence check with `ValueError: v2.3.1 decisions differ from the frozen v2.2 bytes`. No formal decisions, rankings, policy, controller audit, or `VERIFIED_PRE_GOLD` was promoted. Post-failure read-only checks confirmed unchanged fresh/legacy cache and v2.2 decisions/rankings/reference-policy hashes. No automatic rerun, verifier, evaluator, Gold metric, reservation, or Stage3B access occurred. Full evidence is in `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_4.md`; further diagnosis or execution requires a newly approved review/Amendment.

## Stage4B-U1-D Pre-Gold Amendment 5A Approval

Amendment 5A implementation and synthetic verification were approved on 2026-07-13, binding package commit `81d8c34f1cf2539a4c0b81c6148047bc666e2f82` and the six historical commits listed in `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_APPROVAL_DECISION.md`. Authorization covers only a fail-closed decisions comparator, synthetic-only OS-temporary decisions capture, at least 24 new hardening tests, two byte-identical complete-suite runs, implementation audit/evidence, and creation of an implementation-bound 5B package.

The existing 50 Stage4B-U1 tests must remain, so the full suite must contain at least 74 tests. Tests must actively intercept official paths and ranking/policy calls, distinguish JSON/Python numeric types and signed zero, reject non-finite JSON floats, and freeze a platform-independent binary64 ULP mapping. No official units, queries, source audit, cache, decisions, rankings, comparator/capture, controller, verifier, evaluator, Gold, reservation, or Stage3B access is authorized. Completion of 5A does not authorize official diagnosis.

## Stage4B-U1-D Pre-Gold Amendment 5A Synthetic Verification

The implementation left `scripts/stage4b_u1_goldfree_controller.py` unchanged and added three isolated diagnostic scripts plus 48 synthetic hardening tests. The comparator separates raw-byte, row/query-ID, canonical JSON, schema, discrete, finite-float/ULP, and decision-semantic layers while retaining raw byte equality as the mandatory equivalence gate. Incomparable within-file schemas, duplicate or missing query IDs, invalid JSON, non-finite values, and unsupported types fail closed. Pre-5B static review also froze exact official input/output paths, the OS temp parent, an absent audit output, the v2.2 reference SHA, registered source-audit digest validation without opening the source-audit file, and a cache post-computation fingerprint.

The original 50 tests and 48 new tests passed together as 98/98 with zero failures, errors, or skips. The complete deterministic runner executed twice on unchanged tracked bytes. Both evidence outputs are 16,389 bytes with SHA-256 `3D44C14B82E911DDD37501731772A7594D7616BF12FE278D2D4CCC103533057E`. Its process-wide path guard recorded zero official-path accesses, and active tests proved temporary decisions cleanup on success and exception, official-mode lockout, exact-path rejection before reads, synthetic allowlist rejection, and no full-controller/ranking/policy path.

The local environment emitted the already observed NumPy 2.4.6/`numexpr` ABI warning through the pre-existing import chain, but every verification command exited zero and the two evidence files were byte-identical. Full hashes, the explicit big-endian binary64 ULP mapping, and the initial fixture-only failures are recorded in `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_IMPLEMENTATION_AUDIT.md`. Official diagnosis, controller rerun, verifier, evaluator, Gold, reservation, and Stage3B remain unapproved.

## Stage4B-U1-D Pre-Gold Amendment 5B Package

The implementation-bound request and machine-readable Manifest are `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_OFFICIAL_DIAGNOSTIC_APPROVAL_REQUEST.md` and `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_MANIFEST.json`. They bind final 5A commit `9a060bd31e9c33be587f7ef5e64f86206922e59e`, evidence SHA `3D44C14B82E911DDD37501731772A7594D7616BF12FE278D2D4CCC103533057E`, exact input/output paths, the authorization token, the OS temp parent, cache/v2.2 decisions hashes, and a diagnosis-only stop state.

The requested sequence requires approval-governance commit/push, two byte-identical 98-test post-approval rebinding runs, a governance-binding JSON over the 5B request/Manifest/decision/final `AGENTS.md`, one read-only preflight, and one official decisions-only capture. The capture may read only v2.3.1 unlabeled units/queries/channel audit, the existing cache, and v2.2 decisions. It may not open the source-audit file, rankings, policy, evaluator/Gold, reservation, or Stage3B. No 5B command is authorized or has run.

## Stage4B-U1-D Amendment 5B Review 1 And Amendment 5A.1 Request

The 5B package at commit `ceb755252540cf223aa18ac721443154c29cd07a` was returned on 2026-07-14 as `RETURN_AMENDMENT_5B_FOR_CHANNEL_INPUT_HASH_BINDING`. Its only blocking gap was the absence of package-external expected SHA-256 values for the three v2.3.1 channel inputs. Internal channel-audit-to-input consistency does not freeze the three-file input state independently.

The required external values are units `114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA`, queries `6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B`, and controller channel audit `D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA`. A future approved 5A.1 implementation must hash all three before semantic parsing/computation and again after diagnostic computation immediately before machine-audit exclusive-create. Any mismatch must leave no machine audit and must clean temporary decisions.

The 5A.1 request and machine-readable scope are `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_1_APPROVAL_REQUEST.md` and `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_1_MANIFEST.json`. The package does not authorize implementation, tests, official input access, 5B preflight/capture, controller rerun, verifier, evaluator, or Gold. Current status is `AMENDMENT_5A_1_AWAITING_APPROVAL`.

## Stage4B-U1-D Pre-Gold Amendment 5A.1 Approval

The user approved Amendment 5A.1 implementation and synthetic verification on 2026-07-14, strictly binding package commit `3137ace0328dd24908f95737ea1dcbe0c8fe045e` and the seven historical commits registered in its Manifest. The decision is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_1_APPROVAL_DECISION.md`.

Authorized changes are limited to the diagnostic capture, its deterministic synthetic runner, and diagnostic tests. The implementation must add three required expected-SHA arguments, check all three channel inputs before semantic parsing/cache loading/computation, and recheck them after diagnostic computation immediately before machine-audit exclusive-create. Any mismatch must leave no audit and must clean temporary decisions. The existing 98 tests must remain, at least six tests must be added, and two complete runs of at least 104 tests must pass with zero failures/errors/skips/official-path access and byte-identical evidence.

No official file may be opened during 5A.1. The rejected 5B token, official preflight/capture, controller, verifier, evaluator, Gold, reservation, Stage3B, cache mutation, and algorithm/equivalence changes remain prohibited. After implementation audit, deterministic evidence, and a revised implementation-bound 5B v2 package are pushed, execution must stop for independent approval.

## Stage4B-U1-D Pre-Gold Amendment 5A.1 Synthetic Verification

The implementation added the three required expected-SHA arguments and a shared regular-file/SHA gate. In official mode, the caller-provided expected values must equal the three externally frozen values before actual-file hashing. All three actual hashes are checked before JSON/JSONL parsing, cache loading, or diagnostic computation, and checked again after temporary-decisions comparison and cleanup immediately before audit creation. Any mismatch raises before audit output. The old 5B token was not used by the synthetic suite.

The controller, retrieval, common, and comparator files retained their prior SHA-256 values. Nine tests were added to the existing 98, covering all three pre-gate mismatches, all three computation-time drifts, regular-file enforcement, valid synthetic hashes, and the independent official expected-value freeze. The capture class passed 22/22, and the preliminary complete suite passed 107/107.

The deterministic runner then executed the complete suite twice on unchanged tracked bytes. Each run passed 107/107 with zero failures, errors, skips, or official-path access attempts. Both complete evidence outputs were 20,495 bytes and had SHA-256 `81A8A5960395F729B643A42505E7F947962B338CD97ADD0506636D3AA2020A67`; direct byte comparison returned true. The evidence is `results/stage4b_u1_d_pregold_amendment_5a_1_synthetic_verification.json` and the full audit is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_1_IMPLEMENTATION_AUDIT.md`.

The previously observed NumPy 2.4.6/`numexpr` ABI warning was emitted by the existing optional import chain in each run, but all commands exited zero. No official input, cache, decisions, rankings, policy, evaluator/Gold, reservation, or Stage3B path was opened. This verification does not authorize official diagnosis or controller resumption.

## Stage4B-U1-D Pre-Gold Amendment 5B v2 Package

The revised request and machine-readable scope are `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_V2_OFFICIAL_DIAGNOSTIC_APPROVAL_REQUEST.md` and `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_V2_MANIFEST.json`. They bind implementation/evidence commit `e566eb861ec6028ca89a40c9aca7d06737f1eb8e`, the 5A.1 audit and evidence hashes, all frozen implementation hashes, and the exact external SHA-256 values for units, queries, and controller channel audit.

The requested execution remains diagnosis-only: approval governance and two byte-identical 107-test rebinding runs must be pushed before one read-only preflight; the preflight must externally hash all three channel inputs, cache, and reference decisions before one exact capture. The capture rechecks the channel inputs after temporary-decisions cleanup and before exclusive audit creation. Only aggregate comparison evidence may be committed, followed by immediate stop.

The existing CLI token string is inert without a future decision that explicitly binds the 5B v2 package commit. It was not passed during 5A.1. No post-approval rebinding, preflight, official capture, controller, verifier, evaluator, Gold, reservation, or Stage3B command is authorized by the package itself. Current status is `AMENDMENT_5B_V2_AWAITING_APPROVAL`.

## Stage4B-U1-D Pre-Gold Amendment 5B v2 Approval

The user approved one official decisions-only diagnosis on 2026-07-14, strictly binding package commit `f43e22ef079701139d4437849be8ad57654f80d7` and the seven historical commits registered in its Manifest. The decision is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_V2_APPROVAL_DECISION.md`.

Execution remains gated on a pushed approval-governance state, two complete 107-test rebinding runs with byte-identical evidence and zero official access, and a pushed governance-binding JSON/audit. Only then may one read-only preflight examine the five permitted inputs. Capture is authorized once only if that preflight passes every frozen path, SHA, bytes, boundary, implementation, output-absence, and Git gate.

The endpoint remains a diagnosis-only aggregate audit. No full controller, ranking/reference-policy/source-audit read, verifier, evaluator/Gold, reservation, Stage3B, implementation/equivalence change, cache mutation, retry, or automatic pre-Gold resumption is authorized. Current status is `AMENDMENT_5B_V2_APPROVED_REBINDING_REQUIRED`.

## Stage4B-U1-D Pre-Gold Amendment 5B v2 Post-Approval Rebinding

Approval governance commit `2ddf6e044c27e47385a558bdaca80cb6c31c4ffe` was pushed before synthetic execution. On those governance bytes, the complete 107-test runner executed twice. Both runs passed 107/107 with zero failures, errors, skips, or official-path access attempts. Both complete outputs were 20,495 bytes with SHA-256 `7D9C3527480ECDFFA87C943589538BCEFEFA3610A6D415719429CDE5D222D12E`; direct byte comparison was true.

The governance-binding JSON independently hashes the v2 request, Manifest, approval decision, final approved `AGENTS.md`, and the rebinding evidence, and records implementation commit `e566eb861ec6028ca89a40c9aca7d06737f1eb8e`. The evidence and binding are `results/stage4b_u1_d_pregold_amendment_5b_v2_synthetic_rebinding.json` and `results/stage4b_u1_d_pregold_amendment_5b_v2_governance_binding.json`; the narrative record is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_V2_SYNTHETIC_REBINDING_AUDIT.md`.

The existing NumPy 2.4.6/`numexpr` ABI warning remained visible, but both runs exited zero. No official input was opened. After these artifacts are committed and pushed, the next and only authorized action is one read-only preflight; capture remains blocked unless that preflight passes every gate.

## Stage4B-U1-D Pre-Gold Hard Failure 5

One read-only preflight ran on synchronized HEAD `4c10ad942a75af42b910b860fd4897b672160d5d`. It passed all governance, implementation, GitHub, five-input regular-file, three external channel SHA, cache SHA/bytes, reference-decisions SHA, 4,500-query/143,820-unit, dual-ID, namespace, channel-audit, source-digest, and output-absence checks. It did not open rankings, policy, source audit, Gold, reservation, or Stage3B.

The exact approved capture command then ran once. It completed channel pre-gates, loaded the require-existing cache, computed temporary decisions, and stopped in the comparator while loading the frozen v2.2 reference decisions. The observed exception was `DecisionsDiagnosticError: Incomparable heterogeneous decisions schema at line 2`. Because comparison did not complete, no machine aggregate audit was exclusive-created and no byte/canonical/semantic classification is available.

Independent read-only post-failure checks found no remaining `stage4b_u1_decisions_diag_*` temporary entry, no machine/narrative audit, and no formal v2.3.1 decisions/rankings/policy/controller-audit/`VERIFIED_PRE_GOLD` output. The three channel SHA values, cache SHA and 210,714,667-byte size, and reference-decisions SHA remained exactly frozen. No retry occurred. Full evidence is `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_5.md`; current status is `AMENDMENT_5B_V2_OFFICIAL_DIAGNOSTIC_STOPPED_HARD_FAILURE_5`.

## Stage4B-U1-D Hard Failure 5 Review And Amendment 5C-A Package

The review at `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_5_REVIEW_1.md` returned official schema-diagnostic execution because commit `deccd203059d05dc27ba80aca1ddb1e2ea8f616f` contained only the failure audit/status and no package-bound schema-inventory implementation protocol. The consumed capture cannot be retried. Comparator changes, normalization, controller rerun, verifier, and Gold remain unapproved.

The new request and machine-readable scope are `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_APPROVAL_REQUEST.md` and `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_MANIFEST.json`. They bind Hard Failure 5 and the relevant 5B/5A.1/v2.3.1 history, but the package itself authorizes no code or execution.

If independently approved, 5C-A is limited to three new isolated files: a read-only value-free JSONL schema inventory, a deterministic complete-suite runner, and inventory tests. The inventory contract rejects duplicate keys, invalid/non-object JSONL rows, and non-finite numbers; distinguishes all frozen JSON type classes; recursively inventories nested structure without array values/order/multiplicity/length; separates object-field order-only from structural differences; and chooses a main ordered schema by row-count mode with a lexicographic ordered-signature tie-break. It must not call or modify the existing comparator/capture/controller.

The existing 107 tests remain the baseline. The minimum 12 additions correspond to the nine required parser/schema categories plus no-value leakage, official-path interception, and deterministic cleanup/output, producing a traceable complete-suite minimum of 119. Two runs must pass with zero failures/errors/skips/official-path access and byte-identical evidence. Official reference decisions and every other official input remain unopened until a later implementation-bound 5C-B package is separately approved.

## Stage4B-U1-D Pre-Gold Amendment 5C-A Approval

The user approved implementation and synthetic verification on 2026-07-14, strictly binding package commit `a8caa2a3b26ae13d0b149e4995e3a017e8edb2e7` and the eight historical commits registered in its Manifest. The decision is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_APPROVAL_DECISION.md`.

Authorization is restricted to three new isolated files: the value-free schema inventory, its deterministic complete-suite runner, and inventory tests. No existing implementation/test may change. The complete suite must retain all 107 prior tests, add at least 12, and execute twice on identical tracked bytes with all tests passing, zero failures/errors/skips/official-path accesses, and byte-identical evidence.

No official reference or other official input may be opened during 5C-A. The existing comparator/capture/controller, raw byte-equivalence and schema acceptance behavior, model/retrieval parameters, official artifacts, prior evidence/failures, verifier/evaluator/Gold, reservation, and Stage3B remain locked. Completion permits only implementation/evidence push and creation of an implementation-bound 5C-B package, followed by immediate stop.

## Stage4B-U1-D Pre-Gold Amendment 5C-A Synthetic Verification

Implementation added only `scripts/stage4b_u1_inventory_decision_schemas.py`, `scripts/stage4b_u1_run_schema_inventory_synthetic_verification.py`, and `tests/test_stage4b_u1_decision_schema_inventory.py`. The inventory module is standard-library-only and has no import or call path to the existing comparator, capture, controller, retrieval, ranking, policy, verifier, or evaluator.

Twenty-four new tests exercise every approved schema/parser/access/cleanup boundary. Together with all 107 prior tests, the complete suite contains 131 tests. A preliminary runner invocation exited before evidence creation because its required-proof matcher searched all test modules and found an older duplicate test-name suffix. Restricting that matcher to the new inventory module corrected the runner-only defect; the failed command and correction are retained in the implementation audit.

On final `AGENTS.md` and unchanged implementation bytes, the complete runner executed twice. Each run passed 131/131 with zero failures, errors, skips, or official-path access attempts. Each complete evidence output was 22,234 bytes with SHA-256 `0D13392B5C96BAD7EC4D67C22A7515B4A6D211C8EFBB3A4486F9BA5531A1EF7C`, and direct byte comparison returned true. The evidence contains SHA-256 values for 17 governance/implementation/test files and independently rechecks the eight approval-frozen files against their baseline hashes.

The unchanged legacy import chain emitted the known NumPy 2.4.6/`numexpr` 1.x ABI warning in each complete run, but all accepted commands exited zero. No environment or frozen source was changed. The process-wide guard recorded zero access to the reference decisions, official channel/cache/source-audit/formal-output/ranking/policy/evaluator/Gold/reservation/Stage3B paths. Full details are in `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_IMPLEMENTATION_AUDIT.md`. Official 5C-B scanning remains unapproved.

## Stage4B-U1-D Pre-Gold Amendment 5C-B Package

The implementation-bound request and machine-readable scope are `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_B_OFFICIAL_SCHEMA_SCAN_APPROVAL_REQUEST.md` and `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_B_MANIFEST.json`. They bind implementation/evidence commit `492a59b2f4daccd3e123f2b6cc49cd896d5009d1`, all 17 evidence-bound hashes, the final 5C-A evidence SHA/bytes/counts, and the one frozen reference path/SHA.

The package requests no immediate read. A future package-bound approval must first be committed and pushed, followed by two byte-identical 131-test rebinding runs with zero official access and a governance binding over the request, Manifest, decision, final `AGENTS.md`, implementation evidence, and rebinding evidence. Only after those artifacts are pushed may one byte-only SHA preflight examine the reference file. One semantic JSONL schema scan is requested only if preflight passes.

The exact scan uses the frozen standard-library inventory and a currently inert token. Output is restricted to value-free schema metadata, aggregate counts/line ranges/differences, and pre/post SHA/cleanup gates. No raw/salted ID, row, field or float value, question/text, ranking, policy, Gold, or generated decision is permitted. Other official inputs, comparator/capture/controller/verifier/evaluator, U1-D metrics, reservation, Stage3B, retries, and automatic resumption remain prohibited. Current status is `AMENDMENT_5C_B_AWAITING_APPROVAL`.

## Stage4B-U1-D Pre-Gold Amendment 5C-B Completed Diagnostic

The package-bound approval is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_B_APPROVAL_DECISION.md`. Approval governance commit `fce67da87d155b1026cbe0670f606201ede0ac4b` was pushed before execution. The complete 131-test suite then ran twice on the final governance bytes; both runs passed 131/131 with 24 inventory tests and zero failures/errors/skips/official-path accesses. The two 22,234-byte evidence outputs were byte-identical with SHA-256 `F16C91BF170ABDFC6784F368D6247E0AA8CDC9ECFB6671C71DFA9BD35CCF297C`. Rebinding and governance binding were pushed in commit `b09668f47cd31df2be73446cadacf84d996418f9`.

One formal preflight ran on that synchronized commit. It verified all registered Git/governance/implementation/output-absence gates and read the reference decisions only as bytes for SHA-256. The file was 2,684,401 bytes and matched `6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7`; no JSONL schema parse occurred in preflight.

The following exact command then ran once and must **not** be rerun under the consumed authorization:

```powershell
python scripts\stage4b_u1_inventory_decision_schemas.py `
  --input "E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_decisions.jsonl" `
  --output "E:\科研\HyperGranular-RAG\results\stage4b_u1_d_pregold_amendment_5c_b_reference_schema_inventory.json" `
  --expected-input-sha256 6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7 `
  --official-authorization-token APPROVE_STAGE4B_U1_D_AMENDMENT_5C_B_SINGLE_REFERENCE_SCHEMA_SCAN
```

It exited zero and created a 17,229-byte machine inventory with SHA-256 `FA56AC3CB78EE746BF71AF0CEF40606E56B9D13C120F10A2A87400EA42CE3A5E`. Independent validation read only this output, recomputed schema digests/counts/main selection, enforced the exact recursive value-free whitelist, checked the pre/post source-SHA declarations, and confirmed exclusive-create cleanup and continued absence of all five formal outputs.

The aggregate result is two ordered/structural schemas over 4,500 rows, with row counts 2,446 and 2,054. Field set/order/nesting are identical; eight field paths differ only by `integer/finite_number` versus `null` type. Full value-free evidence is in `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_B_OFFICIAL_SCHEMA_SCAN_AUDIT.md` and `results/stage4b_u1_d_pregold_amendment_5c_b_reference_schema_inventory.json`.

Current state is `REFERENCE_DECISIONS_SCHEMA_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW`. Comparator changes, normalization, official capture retry, controller rerun, verifier, and Gold require new separately approved Amendments.

## Stage4B-U1-D Pre-Gold Amendment 5C-B Review And Amendment 5D-A Package

The independent review at `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_B_REVIEW_1.md` accepts the 5C-B diagnostic and binds final commit `e5f28f664449c02b12a129aaa2a011bad84dab91`. It confirms Hard Failure 5's direct cause: the reference's legal nullable schema begins on physical line 2, while `load_decisions_jsonl()` freezes the first row's full type signature and rejects any later row schema change before per-query comparison.

The scan did not create or compare v2.3.1 temporary decisions, so Hard Failure 4 remains unclassified. No byte, canonical, query-order, nullable/numeric, float/ULP, discrete, or semantic equivalence conclusion follows from 5C-B.

The next implementation/synthetic-only request is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_A_APPROVAL_REQUEST.md`, with machine-readable scope in `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_A_MANIFEST.json`. It permits no action by itself.

If separately approved, 5D-A would modify only the comparator, its diagnostic synthetic runner, and diagnostic tests. The comparator may stop enforcing file-level complete-schema homogeneity, but must preserve strict row parsing, unique query IDs, per-query field/type/discrete/float/ULP/semantic comparison, aggregate no-raw-value output, and raw byte equality as the controlling gate. Null values may not be normalized or imputed.

The complete-suite baseline is the verified 131 tests. At least 12 new tests make the minimum 143. Final evidence requires two executions on identical tracked bytes, each with zero failures/errors/skips/official-path accesses and byte-identical outputs. Official inputs, capture/controller/verifier/evaluator, Gold, reservation, and Stage3B remain prohibited. A future 5D-B official diagnostic requires a separate implementation-bound package and approval.

## Stage4B-U1-D Pre-Gold Amendment 5D-A Approval

The user approved implementation and synthetic verification on 2026-07-14, strictly binding package commit `33ce115f78840956fcc7bda0c3f4e172579350e7` and the historical commits registered in its Manifest. The decision is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_A_APPROVAL_DECISION.md`.

Only `scripts/stage4b_u1_compare_decisions.py`, `scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py`, and `tests/test_stage4b_u1_decisions_diagnostic.py` may change. The comparator may bump to v2 and remove only the file-level complete-schema homogeneity rejection. Strict parsing, unique query IDs, all per-query comparison layers, aggregate output keys, raw-byte control, and the absence of nullable normalization remain mandatory.

The complete suite must retain the 131-test baseline, add at least 12 heterogeneous-schema tests, and finish with at least 143 tests. Final evidence requires two runs on identical tracked bytes with zero failure/error/skip/official-path access and byte-identical outputs. No official input, official comparator/capture, controller, verifier, evaluator, Gold, reservation, or Stage3B action is authorized.

## Stage4B-U1-D Pre-Gold Amendment 5D-A Synthetic Verification

The comparator now reports `stage4b_u1_decisions_diagnostic_v2` / `stage4b_u1_decisions_diag_v2`. Its only behavioral code change removes the loader's file-level full-type-signature homogeneity rejection. Strict row parsing, duplicate/non-finite rejection, unique query IDs, all per-query comparison layers, aggregate output keys, no-raw-ID/row output, and the raw-byte controlling gate remain unchanged.

The diagnostic tests add 12 cases for legal nullable heterogeneity, null/integer and null/float classification, float/ULP exclusion, semantic differences, field set/order/nesting preservation, strict invalid-row rejection, no normalization, no leakage, and raw-byte control. The complete suite increased from 131 to 143 tests.

The final deterministic runner command was executed twice on identical runner-bound bytes:

```powershell
python scripts\stage4b_u1_run_decisions_diagnostic_synthetic_verification.py `
  --output results\stage4b_u1_d_pregold_amendment_5d_a_synthetic_verification.json
```

Both runs passed 143/143 with zero failures, errors, skips, or official-path accesses. Both outputs were 29,643 bytes with SHA-256 `08695B4305D9919049DFE86870772B9E9F66751DA6D2FF4D43CEF2A912A62008`; direct byte comparison was true.

The runner hashes the request, Manifest, approval decision, 5C-B review/audit, final `AGENTS.md`, all three allowed files, and all 13 frozen files. It blocks the 5C-B machine inventory and registered official paths. The accepted baseline still contains synthetic capture fixture unit tests under OS temporary directories, but no official capture command/path was used. Full commands, the one test-only regex failure, the pre-run command syntax failure, exact hashes, and boundaries are in `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_A_IMPLEMENTATION_AUDIT.md`.

This evidence authorizes no official action. Hard Failure 4 remains unclassified; 5D-B requires a new implementation-bound package and explicit approval.

## Stage4B-U1-D Pre-Gold Amendment 5D-B Package

The implementation-bound request is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_B_OFFICIAL_DIAGNOSTIC_APPROVAL_REQUEST.md`, and the machine-readable registry is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_B_MANIFEST.json`. Both bind 5D-A implementation/evidence commit `02f46447e4cd69a15d2af14ee1fc62f9eb4f8bb9`, the 29,643-byte evidence SHA-256 `08695B4305D9919049DFE86870772B9E9F66751DA6D2FF4D43CEF2A912A62008`, all evidence-bound implementation hashes, and the full 5C-B/Hard-Failure history.

The package requests no immediate command. A future package-bound approval must first be committed and pushed. The complete 143-test suite must then run twice on final approved governance bytes, with both outputs byte-identical and each reporting 143/143, zero failure/error/skip, and zero official-path access. A separate governance-binding JSON must hash the request, Manifest, approval decision, final `AGENTS.md`, 5D-A implementation/evidence, and the post-approval rebinding evidence before any preflight.

Only one read-only preflight and one exact official capture are requested. The exact five-input boundary, SHA-256 values, cache bytes, dual-ID digests, model settings, output absences, authorization-token semantics, and command are frozen in the request and Manifest. The unchanged capture requires its historical `results/stage4b_u1_d_pregold_amendment_5b_official_decisions_diagnostic.json` output path; because Hard Failure 5 created no machine audit, preflight must require that path to remain absent and capture must use exclusive create.

The diagnostic may report aggregate byte/canonical/query-order/schema/discrete/float/ULP/semantic differences only. Raw byte equality remains the controlling gate, nullable values are not normalized, and no raw ID/row/value, ranking, policy, source-audit content, 5C-B machine inventory, Gold, or U1-D effect metric may enter the audit. After an approved successful diagnosis, the process must push the aggregate evidence and stop; controller rerun, verifier, evaluator/Gold, reservation, and Stage3B remain unapproved.

Current status is `AMENDMENT_5D_B_AWAITING_APPROVAL`. No 5D-B rebinding, preflight, or official capture has run.

## Stage4B-U1-D Pre-Gold Amendment 5D-B Approval And Rebinding

The package-bound approval is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_B_APPROVAL_DECISION.md`. The approval decision and final approved `AGENTS.md` were pushed at final governance HEAD `1c46dc1b69f8381598aacb9f3b1e27561c7f9ee2` before synthetic execution.

The frozen 143-test command then ran twice. Each invocation exited zero and produced a 29,643-byte evidence file with SHA-256 `264200C2EBEDA1D0B214F824B77C89FC5BBE82D3BE0836FAAB9486EACAACF368`. Both reported 143/143, zero failure/error/skip, zero official-path access, comparator checkpoint `stage4b_u1_decisions_diag_v2`, and no official capture/controller/verifier/evaluator/Gold/reservation/Stage3B action. Direct byte comparison was true.

The known NumPy 2.4.6 versus old `numexpr` ABI warning remained visible on stderr, but both accepted commands exited zero and the complete evidence passed every approved hard gate. The temporary first-run comparison copy was deleted after equality verification; no project file or historical artifact was deleted.

The final evidence is `results/stage4b_u1_d_pregold_amendment_5d_b_synthetic_rebinding.json`. The governance-binding JSON and narrative audit are `results/stage4b_u1_d_pregold_amendment_5d_b_governance_binding.json` and `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_B_SYNTHETIC_REBINDING_AUDIT.md`.

No official input has been opened. After these artifacts are committed and pushed, the only next authorized action is one read-only formal preflight. Capture remains blocked unless every preflight gate passes.

## Stage4B-U1-D Pre-Gold Hard Failure 6

The single authorized formal preflight ran once on clean synchronized HEAD `2447ad234c160c6e615d81b33dc4ede7ecaa18da`. It passed Git/GitHub, ancestry, Manifest implementation hashes, seven governance-bound hashes/byte counts, final `AGENTS.md`, frozen command/configuration, output absence, and diagnostic-temp absence gates.

It then stopped at this expression before any official input file check or read:

```powershell
[System.IO.Path]::GetFullPath($tempParent) -eq
  [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
```

The observed exception was `OS temp parent differs`. The comparison retained the trailing-separator difference between the Manifest path and `.NET GetTempPath()`. Because the formal preflight failed, its one authorized invocation is consumed even though both strings may resolve to the same directory.

The failure preceded regular-file checks, SHA reads, units/queries parsing, and channel-audit parsing. No official input, source audit, 5C-B machine inventory, ranking, policy, Gold, reservation, or Stage3B file was opened. The authorization token was not passed and official capture did not run.

A metadata-only post-failure check found no machine/narrative audit, zero of five formal outputs, and no `stage4b_u1_decisions_diag_*` residue. Full evidence is `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_6.md`. Current status is `AMENDMENT_5D_B_OFFICIAL_DIAGNOSTIC_STOPPED_HARD_FAILURE_6`; no second preflight or capture is authorized.

## Stage4B-U1-D Hard Failure 6 Review And Amendment 5E-A Package

Review 1 at `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_6_REVIEW_1.md` accepts the Hard Failure 6 audit and returns the project for a new implementation/synthetic-only Amendment. It confirms that 5D-B preflight authorization is consumed and that no official input was opened before the path-comparison failure.

The 5E-A request and machine-readable scope are `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5E_A_APPROVAL_REQUEST.md` and `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5E_A_MANIFEST.json`. They request only a tracked standard-library Windows directory-equivalence helper, a new synthetic test module, and deterministic-runner binding. The helper must require absolute existing non-reparse directories, canonicalize/trim separators for comparison only, use ordinal case-insensitive exact equality, and reject parent/child/prefix/unrelated/relative/missing/file/reparse paths.

The existing 143 tests and 29,643-byte evidence SHA-256 `264200C2EBEDA1D0B214F824B77C89FC5BBE82D3BE0836FAAB9486EACAACF368` form the traceable baseline. At least 12 additions require a complete suite of at least 155 tests. Final evidence would require two runs on identical tracked bytes with zero failure/error/skip/official access, zero formal preflight/token/capture use, and byte-identical outputs.

The package itself authorizes no implementation or command. Capture, comparator, controller, retrieval, common, data, model, parameters, exact capture command, raw-byte equivalence, formal preflight, official access, verifier/evaluator/Gold, reservation and Stage3B remain locked pending a future package-bound 5E-A approval.

## Stage4B-U1-D Pre-Gold Amendment 5E-A Implementation

Approval governance is commit `461939434206764555b917c5971956e6951ff4dd`, binding package `19f16f559f0b1f3b59ef24a04e368f99ae3635e3`. Implementation added `scripts/stage4b_u1_preflight_path_equivalence.py`, added `tests/test_stage4b_u1_preflight_path_equivalence.py`, and updated only the approved decisions-diagnostic synthetic runner.

The helper uses `os.lstat`, Windows path canonicalization, trailing-separator trimming for comparison only, and `CompareStringOrdinal` with case-insensitive exact equality. It does not contain command, token or capture logic and does not normalize the future exact command argument.

The new test module contributes 18 tests. A targeted run passed 18/18. A preliminary complete run passed 161/161 and its temporary evidence was deleted after inspection. The final static gate bound 24 files with digest `68E0F934E171F763793942F7B1CEC78638A3F31FF185AAE3A5321E35C1AD541C` and verified all 15 frozen hashes.

Two consecutive final runs on identical bound bytes both passed 161/161 with zero failure/error/skip, zero official metadata/content access, and zero formal-preflight/token/capture invocation. Both outputs were 36,518 bytes with SHA-256 `84C58CBA9801A6EB8DFAF4ED6688BB5FCBD5777729FD833083E16CB630FFED83`; direct byte comparison passed. Final evidence is `results/stage4b_u1_d_pregold_amendment_5e_a_synthetic_verification.json`.

The environment continued to emit the known NumPy 2.4.6/old `numexpr` ABI warning during complete-suite imports, but all runner commands exited zero. No official input or effect metric was accessed. The only next permitted action after implementation/evidence push is assembly of an implementation-bound 5E-B request/Manifest; 5E-B execution requires separate approval.

## Stage4B-U1-D Pre-Gold Amendment 5E-B Package

The implementation-bound request and machine-readable scope are `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5E_B_OFFICIAL_DIAGNOSTIC_APPROVAL_REQUEST.md` and `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5E_B_MANIFEST.json`. They bind 5E-A implementation/evidence commit `a8b064a4a2133aea27cbe9b85978237fc3dae661` and preserve the historical 5E-A `AGENTS.md` hash separately from any future approval-governance hash.

The package asks only for a future sequence of approval governance, two 161-test deterministic rebinding runs, governance binding, one helper-bound formal preflight, and conditionally one unchanged exact decisions-only capture. The preflight must verify helper bytes/SHA and directly import/call `windows_directories_equivalent()` on the raw runtime `GetTempPath()` string and exact registered expected directory before any official input metadata/content operation.

The five-input read boundary, cache/reference fingerprints, model, max length, batch size, controller/comparator checkpoints, token string, output path, exact capture command, aggregate-only output policy and raw-byte control gate remain unchanged. The package itself authorizes no command; a future approval must bind the package commit explicitly.

## Stage4B-U1-D Pre-Gold Hard Failure 7

5E-B approval governance was pushed at `f2f2e249e4e7a52fcc44b61a2245d8d50d79106d`. Two post-approval 161-test rebinding runs passed with zero failure/error/skip/official access/formal-preflight/token/capture and byte-identical 36,518-byte evidence SHA-256 `BF4C668C76C4B8545882C894F241038765AFD8DD263B4195D9E2D654B7B9FC1A`. Rebinding/governance artifacts were pushed at `3185c3bd4ffd3eb2bc61b52fdf18a3367b9dca76`.

The single authorized formal preflight passed its project/governance A gate. In B, after confirming all output and temporary-residue absence, a raw case-insensitive substring denylist treated `gold` inside the approved path segment `pregold` as a prohibited Gold input. It raised `Prohibited argument supplied: gold` and stopped.

The helper gate C and official-input gate D were never reached. No official input metadata/content was accessed, no token was used and capture did not run. A corrected metadata-only post-failure check found no machine/narrative audit, no formal output and no diagnostic residue. Full evidence is `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_7.md`.

The 5E-B preflight authorization is consumed. The raw-substring check cannot be corrected and rerun under 5E-B; a new package-bound Amendment is required before any helper official-boundary check, preflight or diagnostic capture.

## Stage4B-U1-D Pre-Gold Amendment 5F-A Package

Hard Failure 7 Review 1 accepts the stop and audit at `f18d551b17f1bbed645ac159ebe52b7d6b9d8e54`. It confirms that the 5E-B preflight is consumed and that helper, official-input access, token, and capture counts remained zero.

The implementation/synthetic-only request and machine-readable scope are `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5F_A_APPROVAL_REQUEST.md` and `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5F_A_MANIFEST.json`. The package binds the confirmed chain `e387d2707ede9024571249face71bf7ca3afd4e0` -> `f2f2e249e4e7a52fcc44b61a2245d8d50d79106d` -> `3185c3bd4ffd3eb2bc61b52fdf18a3367b9dca76` -> `f18d551b17f1bbed645ac159ebe52b7d6b9d8e54` and the 5E-A implementation/evidence baseline.

The requested helper must validate the unchanged capture argv through exact equality, a fixed ordered flag/value structure, typed values, seven externally frozen path roles, exact token binding, and explicit prohibited-role rejection. It must accept the exact `pregold` audit-output path and must not classify arbitrary values with a raw `gold` substring rule. The helper is standard-library-only and may not access files, hash paths, call the path helper, execute subprocesses, use the token, or invoke capture.

The verified baseline is the 161-test 5E-B rebinding evidence at `results/stage4b_u1_d_pregold_amendment_5e_b_synthetic_rebinding.json`, 36,518 bytes, SHA-256 `BF4C668C76C4B8545882C894F241038765AFD8DD263B4195D9E2D654B7B9FC1A`. A future approved 5F-A implementation must add at least 16 tests and produce two byte-identical complete runs of at least 177 tests with zero failure/error/skip/official access/path-helper official invocation/preflight/token/capture. Its implementation/evidence push must then stop for independent review; a 5F-B package cannot be assembled until that review explicitly accepts 5F-A.

This package itself authorizes no implementation or command. A future approval must explicitly bind the commit containing the request, Manifest, Hard Failure 7 audit, Review 1, and final governance bytes.

## Stage4B-U1-D Pre-Gold Amendment 5F-A Implementation

Approval governance was committed and pushed at `273341960858930246ae0c1441440aede0403a65` before implementation. Changes to implementation/tests were limited to the new typed argument-policy helper, new 44-test module, and the approved deterministic runner. All 17 frozen file hashes remained unchanged.

`validate_capture_argv(actual_argv, approved_argv)` performs no Manifest or filesystem read. Exact argv equality is controlling; fixed executable/script, 32-element shape, 15 ordered flags, typed values, seven exact path-role bindings, exact token binding and explicit prohibited-role rejection are then enforced fail-closed. AST and runtime tests prove no filesystem/hash/subprocess/capture/token/path-helper call and no raw `gold` value-substring denylist.

The first module-style targeted command failed before discovery because `tests` is not a Python package. The corrected discovery command passed 44/44. One preliminary complete run passed 205/205 and its OS-temp evidence was deleted. The first final wrapper attempt failed at PowerShell parse time before either runner invocation because its generic `SequenceEqual[byte]` syntax was unsupported.

The corrected final wrapper ran the complete suite twice on 26 identical tracked files. Both runs passed 205/205 with zero failure/error/skip/official access/path-helper official invocation/preflight/token/capture. Tracked-byte digest was `B58E85239F001B532B5CF378998B804B1202C5D6FF148311EF939DC4B3B4EA34`. Both evidence files were 51,922 bytes with SHA-256 `A5B97077AD9A0C62EBFCAE9D70FC8B5BFAD19CCB32FF3A53E1FCF4BDB216D189`, and direct byte comparison passed. The first-run OS-temp evidence was then deleted; final evidence is `results/stage4b_u1_d_pregold_amendment_5f_a_synthetic_verification.json`.

No official input metadata/content, real OS-temp helper check, formal preflight, authorization token, official capture/comparator, controller, verifier, evaluator/Gold, reservation or Stage3B was accessed or run. The implementation/evidence push must stop for independent review; 5F-B cannot be assembled under this approval.

## Stage4B-U1-D Pre-Gold Amendment 5F-A Review 1

Independent review accepts the 5F-A implementation/evidence commit `e7b688d4b67db596df1d447e2cf70f12f0ea5d0b`. It preserves the accepted 205/205 dual-run evidence, 51,922-byte output, SHA-256 `A5B97077AD9A0C62EBFCAE9D70FC8B5BFAD19CCB32FF3A53E1FCF4BDB216D189`, tracked-byte digest `B58E85239F001B532B5CF378998B804B1202C5D6FF148311EF939DC4B3B4EA34`, and zero official access/path-helper official invocation/preflight/token/capture counters.

The review authorizes only assembly of an implementation-bound 5F-B request and Manifest. It does not authorize a new synthetic run, helper call, preflight, token use, official input access, capture, controller, verifier or Gold. The review record is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5F_A_REVIEW_1.md`.

## Stage4B-U1-D Pre-Gold Amendment 5F-B Package

The request and machine-readable scope are `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5F_B_OFFICIAL_DIAGNOSTIC_APPROVAL_REQUEST.md` and `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5F_B_MANIFEST.json`. The package binds the 5F-A package, approval governance, accepted implementation/evidence, Hard Failure 7 chain, frozen helper bytes, five official input fingerprints and the unchanged capture boundary. For accepted 5F-A hashes, the implementation-time `AGENTS.md` is verified from the `e7b688d...` Git blob while the other 25 files are recomputed against the current tree; post-approval evidence must separately bind and support recomputation of all 26 current hashes including final governance `AGENTS.md`.

The Manifest's `exact_capture_command` was parsed successfully and compared element by element with the hash-bound 5E-B Manifest command: both contain exactly 32 elements and 15 ordered flags and are identical. This comparison reads only tracked governance files; it does not access official input paths or execute either helper.

A future package-bound approval is requested for exactly: approval governance; two complete 205-test rebinding runs on final governance bytes with byte-identical evidence; governance binding and audit push; one A/B/C/D formal preflight; conditionally one unchanged exact capture; aggregate-only audit push and immediate stop. Gate B must hash-bind and directly call `validate_capture_argv`; gate C must hash-bind and directly call `windows_directories_equivalent`; gate D is the first point at which the five Manifest-registered official inputs may be inspected.

The package itself authorizes no command. Until a new approval explicitly binds the 5F-B package commit, post-approval rebinding, helper invocation, formal preflight, token use, official input metadata/content access, capture, controller, verifier, evaluator/Gold, reservation and Stage3B remain prohibited.

## Stage4B-U1-D Pre-Gold Amendment 5F-B Approval And Rebinding

Approval governance was committed and pushed at `84d39707dee15729dc0c35c85a16f4e31dac89e4`. On those final governance bytes, the frozen runner completed exactly two runs. Each run passed 205/205 tests including 44 typed-policy tests, with zero failure/error/skip/official access/path-helper official invocation/formal preflight/token/capture.

The two complete evidence files were byte-identical at 51,922 bytes and SHA-256 `829289F10B1C7B39BBE6B37ACF51DCB265764FD10A8DA55892F60D50F6D2CB09`. The first OS-temp snapshot was deleted only after direct comparison. The formal evidence, governance binding and audit were committed and pushed at `052e8ecc04f566b75666d5cc96df74d2ed5061e4`.

## Stage4B-U1-D Pre-Gold Hard Failure 8

The single authorized formal preflight failed at the first A-gate assertion. The command read local HEAD, origin/main and GitHub main as the same correct value `052e8ecc04f566b75666d5cc96df74d2ed5061e4`, but compared them to the incorrectly transcribed literal `052e8ece1839ff253f8aeb84d5f828377be74829`. The two values share only the short prefix `052e8ec`.

The failure occurred before the remaining A checks and before B/C/D. Typed helper calls, path-helper calls, official input metadata/content access, token use and capture invocation all remained zero. A post-failure metadata-only check found no machine/narrative audit, no formal output and no diagnostic temp residue.

This is a wrapper commit-literal construction defect, not network drift, GitHub divergence, helper failure, path-equivalence failure, official-input drift, cache failure or capture failure. The one formal-preflight authorization is consumed; correcting the literal and rerunning requires a new package-bound Amendment. Full evidence is `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_8.md`.

## Stage4B-U1-D Hard Failure 8 Review And Amendment 5G-A Package

Independent review accepts the Hard Failure 8 audit and the 5F-B post-approval rebinding evidence. It confirms that the only formal preflight invocation stopped at the first A-gate literal comparison and that typed/path helpers, official inputs, token and capture were not reached. The review record is `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_8_REVIEW_1.md`.

The implementation/synthetic-only request and machine-readable scope are `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_APPROVAL_REQUEST.md` and `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_MANIFEST.json`. They bind Hard Failure 8, 5F-B package/approval/rebinding, the accepted 51,922-byte rebinding evidence SHA-256 `829289F10B1C7B39BBE6B37ACF51DCB265764FD10A8DA55892F60D50F6D2CB09`, the governance binding SHA-256 `954A623C38668E0975C72ECF399AAA6B1AD9AF2F212CB006A0F95369BCAFCF9B`, 24 frozen implementation/test hashes and the unchanged 32-element capture command boundary.

A future package-bound approval would permit only a pure caller-fact execution-head validator, its synthetic tests and deterministic evidence binding. The validator must require complete lowercase 40-character SHAs, local/origin/GitHub equality, direct approval parentage, exact changed-path set, required ancestors, clean-worktree and governance/evidence presence. It must not read the filesystem, run Git/subprocess, access official paths, call existing helpers, use a token, invoke capture, accept a pre-transcribed future expected HEAD or contain a fixed future rebinding SHA.

The verified baseline is 205 tests. A future approved 5G-A implementation must add at least 16 tests and produce two byte-identical complete runs of at least 221 tests on identical tracked bytes, with zero failure/error/skip/official access/helper official invocation/preflight/token/capture. The package itself authorizes no implementation or command and does not authorize 5G-B assembly. Current status is `AMENDMENT_5G_A_AWAITING_APPROVAL`.

## Stage4B-U1-D Pre-Gold Hard Failure 9

5G-A approval governance was committed and pushed at `fd50bc30f5acbf4955e3a051fbee70062e6e168c` before implementation. The helper, new tests and runner changes were limited to the three approved paths, and all 24 Manifest-frozen hashes remained unchanged.

In-memory syntax compilation passed. The only targeted command passed 41/41 execution-head tests with zero failure/error/skip. The only preliminary complete-runner invocation then exited 1 before `unittest.TextTestRunner.run()` with `ValueError: Required active access/cleanup proof test is missing or duplicated`.

Read-only source comparison confirmed two global test-name collisions: `test_missing_governance_binding_is_rejected` matched the new module and an existing goldfree test; `test_helper_uses_only_python_standard_library` matched the new module and the existing path-equivalence module and also appeared twice in the runner tuple. Therefore the active-proof uniqueness gate correctly failed closed.

The preliminary OS-temp path was never created, complete-suite tests run was 0, and no evidence file was produced or deleted. No official input, helper official boundary, real execution-head check, preflight, token, capture, controller, verifier, evaluator/Gold, reservation or Stage3B action occurred. The failed runner was not retried and the names/suffixes were not corrected.

Full evidence is `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_9.md`. Current status is `AMENDMENT_5G_A_SYNTHETIC_VERIFICATION_STOPPED_HARD_FAILURE_9`; a new package-bound Amendment is required before any correction or synthetic retry.

## Stage4B-U1-D Hard Failure 9 Review And Amendment 5G-A.1 Package

Independent review accepts the Hard Failure 9 audit and freezes failed checkpoint `d1c7cf9d78563e30a1e0fe0d6812b36d15b95a9a` for minimal repair. The review record is `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_9_REVIEW_1.md`.

The implementation/synthetic-retry-only request and machine-readable scope are `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_1_APPROVAL_REQUEST.md` and `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_1_MANIFEST.json`. They bind the 5G-A package, approval governance, Hard Failure 9 checkpoint, Hard Failure 8 and 5F-B rebinding/governance, plus the exact audit/review and failed helper/test/runner bytes and SHA-256 values.

The helper is frozen at 6,318 bytes and SHA-256 `517C5C4DB22A82B4CBCA3D8BB751AAE60C0DCC5B5948CC8419D8770A9CC3D174`. A future package-bound approval may permit only two execution-head test-name token changes, corresponding runner suffix changes, one pre-discovery suffix-tuple uniqueness gate and exact count gates of 246 total, 41 execution-head and 44 typed-policy tests. Test bodies, existing tests, evidence schema/output path and all scientific/official behavior remain unchanged.

The requested future sequence explicitly excludes a preliminary complete runner. It requires one source-only inventory, one 41/41 targeted run and exactly two final 246/246 complete runs on stable tracked bytes, followed by direct evidence comparison, audit/push and immediate stop. Any failed gate stops without repair or retry.

Current status is `AMENDMENT_5G_A_1_AWAITING_APPROVAL`. The package itself authorizes no code/test change, inventory, synthetic execution, real execution-head check, preflight, official input, token, capture, controller, verifier, Gold or 5G-B assembly.

## Stage4B-U1-D Amendment 5G-A.1 Minimal Repair And Synthetic Verification

Approval governance was committed and pushed at `3d818cee86e1faca16c2bdab3baf4fd5411cff75` before repair. Relative to Hard Failure 9 checkpoint `d1c7cf9d78563e30a1e0fe0d6812b36d15b95a9a`, only the approved execution-head test module and deterministic runner changed.

The test diff was exactly two function-name token replacements. The runner diff was limited to the corresponding suffixes, retaining the generic path-helper suffix once, adding a pre-discovery tuple uniqueness gate, and requiring exact 246 total, 41 execution-head and 44 typed-policy tests. The helper and all 24 frozen hashes remained unchanged.

One source-only AST inventory scanned six test files and found 246 definitions, 135 unique required suffixes and 135/135 exact global matches without importing or running tests. The execution-head targeted module then ran once and passed 41/41.

No preliminary complete runner was invoked. Two final runs on the same 33 tracked files each passed exactly 246/246 with zero failure/error/skip and zero official/helper/preflight/token/capture counts. Both tracked digests were `88338760CE2EC767D7F93279F4F3B82E916B0CBE4882257B8CF9133591EA8AE0`. Both evidence files were 69,144 bytes with SHA-256 `A6285498FCFE767297D7156B87CA6034A993B2DFBB167EF7DFA813E9ADD55292`; direct comparison was true. The run-1 OS-temp evidence was deleted only after equality passed.

Formal evidence is `results/stage4b_u1_d_pregold_amendment_5g_a_synthetic_verification.json`; full recovery evidence is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_1_IMPLEMENTATION_AUDIT.md`. Current status is `AMENDMENT_5G_A_1_SYNTHETICALLY_VERIFIED`, awaiting independent review. No 5G-B, preflight or official action is authorized.

## Stage4B-U1-D Amendment 5G-A.1 Review And Amendment 5G-B Package

Independent review accepts final implementation/evidence commit `c21f3f58b2b1d4ccf235daba9c85937daedf4e3b`. The review record is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_1_REVIEW_1.md`; it authorizes only assembly of a new 5G-B approval package.

The new request and machine-readable protocol are `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_OFFICIAL_DIAGNOSTIC_APPROVAL_REQUEST.md` and `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_MANIFEST.json`. They bind 5G-A.1 package/approval/implementation, Hard Failures 9 and 8, 5F-B rebinding/governance, the accepted 6,318-byte execution-head helper, final runner/tests and 69,144-byte deterministic evidence.

The future approval protocol freezes exactly two approval-governance changed paths and exactly three rebinding/governance direct-child changed paths. The actual local/origin/GitHub execution HEAD must be derived after that direct-child commit from independently collected Git facts and validated through the hash-bound pure-value helper; a manually transcribed future expected HEAD is forbidden.

Only after derived HEAD validation may one ordered A/B/C/D preflight run. Only after every gate passes may the unchanged 32-element decisions-only capture run once. Any failure stops without retry. Current status is `AMENDMENT_5G_B_AWAITING_APPROVAL`; this package authorizes no rebinding, real execution-head check, preflight, official input access, token, capture, controller, verifier or Gold.

## Stage4B-U1-D Pre-Gold Hard Failure 10

The package-bound approval-governance commit `79e69eab874f669d79d433fa965f5f5f48659332` changed exactly `AGENTS.md` and the 5G-B approval decision and was synchronized across local, origin and GitHub before synthetic execution.

The frozen complete runner then ran exactly twice with no preliminary, targeted, repair or retry invocation. Both runs passed 246/246, including 41 execution-head and 44 typed-policy tests, with 33 tracked files, tracked digest `50D3BCDDAE42961ECCDDC30ADE683D6180F9CDFC319D085BEC762B8985A17041`, and zero failure/error/skip/official/helper/preflight/token/capture counts. Both 69,144-byte evidence files had SHA-256 `00281BED7BC0DF10D47382CC47D0884BFCD331F0CB92EFC0B51F0FF176827A2A` and were byte-identical.

The precommit governance-validation wrapper then evaluated `$g.bound_files.psobject.Properties.Count -ne 11`. PowerShell member enumeration returned an 11-element `System.Object[]` containing one `1` per property instead of scalar collection cardinality. The nonempty comparison result triggered `bound file count failed`. Read-only diagnosis confirmed `@($g.bound_files.psobject.Properties).Count` is 11 and listed exactly the 11 Manifest-required bound-file keys.

The failed validation was not corrected or rerun. The authorized three-path direct child was not created, and derived execution-HEAD validation, formal preflight, official input access, helper calls, token and capture remained at zero. The generated rebinding evidence, governance binding and narrative audit are preserved unchanged in the failure checkpoint. Full evidence is `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_10.md`.

Current status is `AMENDMENT_5G_B_REBINDING_GOVERNANCE_STOPPED_HARD_FAILURE_10`. The current approval is consumed; any recovery requires independent review and a new package-bound Amendment.

## Stage4B-U1-D Hard Failure 10 Review And Amendment 5G-B.1 Package

Independent review accepts the Hard Failure 10 audit and freezes checkpoint `aab591b92804fd1226a62751c38d056918f71b41`. It accepts the old two-run rebinding evidence only as deterministic evidence within the failed checkpoint. The three old 5G-B artifacts must remain byte-identical and cannot be reused as an active execution binding.

The review is `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_10_REVIEW_1.md`. The recovery request and machine-readable protocol are `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_APPROVAL_REQUEST.md` and `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_MANIFEST.json`.

The first 5G-B.1 package commit `9536ffb4ce845aeff9db3552f890612ca6e9e2a3` is not approvable. Independent package review found three validator gaps: default case-insensitive PowerShell set operations, inability to detect duplicate raw JSON keys after `ConvertFrom-Json`, and the absence of a frozen complete real precommit command. The review is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_PACKAGE_REVIEW_1.md`.

The corrected validator reads strict UTF-8 governance bytes and sends them to a frozen Python 3.12 standard-library parser on stdin. `object_pairs_hook` rejects exact duplicate keys before object materialization at every level; an explicit case-fold gate rejects case-only `bound_files` collisions. The reported actual names and Manifest expected names are then materialized with `@(...)`, deduplicated with `Sort-Object -CaseSensitive -Unique`, and compared with `Compare-Object -CaseSensitive`. Cardinality-only or case-insensitive acceptance is forbidden.

The complete real precommit validator is frozen inside the Manifest as 195 LF-joined source lines with no trailing newline: 15,966 bytes, SHA-256 `0F066387B8523B0EA387444076A1113913082D283C28C2DE3FFB33872D558249`. It covers package/approval parentage, approval-decision binding of package/source bytes/SHA, strict artifact booleans, the exact 15-name path registry, every path/bytes/SHA record, historical 5G-B 3/3 hashes, fresh 246/41/44 and zero-counter gates, exact three-path worktree status and absence of extra paths. No post-approval expression may extend or replace it.

A future corrected-package-bound approval may authorize one in-memory semantics wrapper covering exact/missing/extra/duplicate/case-only/raw-duplicate fixtures, exactly two fresh complete rebinding runs on final approval-governance bytes, one frozen real precommit validation, one fresh exact-three-path direct-child commit, GitHub synchronization and immediate stop. Fresh paths use the `5g_b_1` namespace and may not overwrite the historical 5G-B files.

Current status is `CORRECTED_AMENDMENT_5G_B_1_PACKAGE_AWAITING_APPROVAL`. Validator semantics, synthetic execution, direct-child creation, execution-head helper calls, formal preflight, official inputs, token, capture, controller, verifier and Gold remain unapproved.

## Stage4B-U1-D Pre-Gold Hard Failure 11

Corrected package `48a9c1438166eaf895104358b2d8cd8c9b043020` received package-bound approval. Approval-governance commit `0e28fba6647bfd98634ebb8d1565e862dcf16920` was its direct child, changed exactly `AGENTS.md` and the approval decision, and was synchronized across local, origin and GitHub with a clean worktree before semantics execution.

The one-time in-memory semantics wrapper was invoked exactly once. Its seven PowerShell fixture calls reached the raw-parser stage, then the only Python parser process emitted stderr beginning at its string-source line 6. With the wrapper's fail-closed error policy, PowerShell terminated it as `NativeCommandError` before a nine-fixture success summary was produced. The captured output did not include the remaining Python diagnostic, so this checkpoint does not claim a deeper parser root cause.

No correction or retry occurred. Python process count remained one; complete synthetic runs, fresh artifact creation, frozen real-validator invocations and fresh direct-child commits remained zero. The three fresh paths were absent after failure, and all three historical 5G-B artifacts matched their frozen bytes and SHA values. Full evidence is `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_11.md`.

Current status is `AMENDMENT_5G_B_1_VALIDATOR_SEMANTICS_STOPPED_HARD_FAILURE_11`. The consumed approval cannot authorize any further semantics, synthetic, direct-child, execution-head, preflight or official action.

## Stage4B-U1-D Amendment 5G-B.1.1 Reproducibility Boundary

The accepted Hard Failure 11 review is `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_11_REVIEW_1.md`. It treats the line-6 negative-fixture escape as a high-confidence diagnosis rather than a fully proven parser root cause because the complete Python traceback was not preserved.

The approval request and Manifest freeze the future semantics harness as source bytes rather than an editable command sketch:

- PowerShell wrapper: 122 LF-joined lines, no trailing newline, 7,890 bytes, SHA-256 `DFA95A904CE371F283B8DBA8BB4D98CC048F345F536C0E7D0D6DB8073DF9E16C`.
- Embedded Python: 46 LF-joined lines, no trailing newline, 2,284 bytes, SHA-256 `D0D3D6FC37AD0C2649A7A7F88EFA944C357033E3F0E956BE0E27C4374653D602`.
- Exact success stdout: 789 bytes, SHA-256 `EDBD4614B790256E314F4A8963128A5FB5A190FAC197437FB349D4C33C606135`, no trailing newline.
- Frozen real precommit validator remains unchanged at 195 lines, 15,966 bytes and SHA-256 `0F066387B8523B0EA387444076A1113913082D283C28C2DE3FFB33872D558249`.

The wrapper uses one `System.Diagnostics.Process` with redirected stdout/stderr and an environment-bound embedded source. Expected negative fixtures are caught inside Python and represented as deterministic pass/fail records rather than native stderr. The required success counts are wrapper 1, Python process 1, PowerShell 7/7, raw JSON 2/2 and total 9/9, with exit 0, stderr 0 and all filesystem/Git/GitHub/helper/official/token/capture counters at 0.

At package assembly time the harness is not executed. The fresh result paths `results/stage4b_u1_d_pregold_amendment_5g_b_1_1_validator_semantics.json` and `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_VALIDATOR_SEMANTICS_AUDIT.md` must remain absent until a new approval explicitly binds the package commit and authorizes the single invocation.

Current status is `AMENDMENT_5G_B_1_1_PACKAGE_AWAITING_APPROVAL`. No synthetic, real validator, direct-child, execution-head, preflight or official action is authorized.

## Stage4B-U1-D Pre-Gold Hard Failure 12

The package-bound approval was recorded in `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_APPROVAL_DECISION.md`. Approval-governance commit `e18dcb13b64e8a50d764fc9eacbabcdea7c5393f` is the exact two-path direct child of package `c4101cfafbc08d518cd4b56e5d199f9d5937294b` and was synchronized across local, origin and GitHub before the pre-execution source gate.

The source gate used Windows PowerShell only and did not invoke Python. It reconstructed the Manifest sources with LF/no trailing newline and confirmed the Python source has 46 lines and 2,284 UTF-8 bytes. It then computed the SHA-256 byte array but failed when converting it with `[System.Convert]::ToHexString()`, which is unavailable in Windows PowerShell 5.1. The observed exception was `MethodNotFound`.

No source hash mismatch was observed. Python hash equality, PowerShell line/byte/hash equality, embedded-source equality and expected-stdout equality were not reached. No compatible conversion was substituted, and the gate was not retried.

The frozen wrapper was not part of the failed command. Wrapper invocations and Python processes remained 0. The machine evidence and narrative audit remained absent, and no synthetic, real validator, direct-child, helper, preflight, official input, token, capture or downstream action occurred.

Full evidence is `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_12.md`. Current status is `AMENDMENT_5G_B_1_1_SOURCE_HASH_VERIFICATION_STOPPED_HARD_FAILURE_12`; recovery requires a new package-bound approval.

## Stage4B-U1-D Amendment 5G-B.1.1.1 Reproducibility Boundary

The accepted review is `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_12_REVIEW_1.md`. It confirms a Windows PowerShell 5.1 API compatibility failure before wrapper execution and explicitly does not classify the failure as source drift.

The recovery Request and Manifest freeze a complete source verifier as 59 LF-joined lines with no trailing newline, 3,512 UTF-8 bytes and SHA-256 `1A30DC70AD0C01CDACBC3279F1CFD707EA4DAB457BE9C6C30A5C6D6495FA81BF`. Its runtime is exactly Windows PowerShell 5.1 Desktop; `pwsh.exe` is rejected. SHA formatting uses `System.Security.Cryptography.SHA256`, `System.BitConverter` and hyphen removal.

The verifier's only readable file is `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_MANIFEST.json`, frozen at 24,248 bytes and SHA-256 `B5953058270B4A8C715D38D5CF92CC65DCB7F90C6149EA1DC5B3E02C14B1A68E`. It checks the unchanged Python 46/2,284/`D0D3D6...`, PowerShell 122/7,890/`DFA95A...`, embedded-byte equality and expected stdout 789/`EDBD46...` gates.

Exact compatible-verifier success stdout is 190 bytes with SHA-256 `D05B3B2A147C51FB3A9FFFC3BEB802439E01AEFC34B708FE14C298978F2BFBB3`. Static PowerShell syntax parsing passed during package assembly, but the verifier was not invoked.

The future versioned evidence paths use the `5g_b_1_1_1` namespace. Both old ungenerated `5g_b_1_1` paths and both new paths must remain absent until a new approval binds the package commit. Current status is `AMENDMENT_5G_B_1_1_1_PACKAGE_AWAITING_APPROVAL`; no execution is authorized.

## Corrected 5G-B.1.1.1 Execution Envelope

Package Review 1 accepts the 59-line verifier but rejects package `d1876bd9ccc198285808795f7f1809c4d1a48e1c` because the verifier bootstrap and process transport were not frozen. The corrected package supersedes it.

The recovery harness is 77 LF-joined lines, 6,246 UTF-8 bytes, SHA-256 `B34E7AE012AC0314AD44590603575194C8881CE58C17E6C8ED6568A5FA373048`. It starts exactly one compatible-verifier and one unchanged semantics-wrapper Windows PowerShell child, each through the same ProcessStartInfo contract. The wrapper may start exactly one Python process.

The bootstrap trust root is 58 lines, 3,909 bytes, SHA-256 `F8A452CEBEC06326E1D8BA4DEB4FC8915210F3FF9BBF53DA2D22B9675773C81D`. Its source-to-command transport is frozen as 7,770 UTF-16LE bytes, 10,360 Base64 characters, Base64 SHA-256 `06CD60CDBD63E5AB9B017487285077C68581829D4309DC1AD6C964F22B9236C2`, and complete-arguments SHA-256 `5EF7120B1005A027D408CF7DCAB525768376F2DAD213D91E69D73E1326D6F05D`.

All child invocations use `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`, `-NoLogo -NoProfile -NonInteractive -EncodedCommand`, UTF-16LE Base64 source, redirected stdin/stdout/stderr, no window and no temporary `.ps1`. The bootstrap reads the corrected Manifest as its governance trust root, hash-checks the harness, captures its exact output and writes the raw 789 bytes directly to machine evidence with `FileMode.CreateNew` only after every nested gate succeeds.

Static source reconstruction, fingerprint checks and PowerShell syntax parsing are package-assembly checks only; none of the three frozen sources has been invoked. Current status is `CORRECTED_AMENDMENT_5G_B_1_1_1_PACKAGE_AWAITING_APPROVAL`.

## Stage4B-U1-D Pre-Gold Hard Failure 13

The corrected package-bound approval was recorded in `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_APPROVAL_DECISION.md`. Approval-governance commit `f46afbf565beca5672ef443bccb67c33ebd26876` is the exact two-path direct child of package `e37400707a65d11c9f038d13e7be0ec2a19d27a4`.

`git push origin main` succeeded and the following fetch succeeded. Local HEAD and fetched `origin/main` were both `f46afbf565beca5672ef443bccb67c33ebd26876`. The separate GitHub-main API check then failed because the current environment has no `gh` executable. This is a local verification-tool availability failure, not a network failure or proof of remote-branch drift, but it leaves the approved three-way gate incomplete.

No alternative API client or remote check was substituted, and the gate was not retried. Static source reconstruction, transport fingerprinting, bootstrap, harness, compatible verifier, wrapper and Python all remained unstarted. All four old/new semantics evidence paths remained absent.

Full evidence is `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_13.md`. Current status is `CORRECTED_AMENDMENT_5G_B_1_1_1_APPROVAL_GOVERNANCE_SYNC_VERIFICATION_STOPPED_HARD_FAILURE_13`; recovery requires a new independent review and package-bound approval.

## Amendment 5G-B.1.1.1.1 Synchronization Recovery Package

Hard Failure 13 Review 1 accepts the checkpoint and confirms that retrospective GitHub history proves the approval commit was pushed but cannot replace the failed runtime gate. The consumed corrected 5G-B.1.1.1 approval remains unusable.

The recovery package freezes a 74-line, 4,114-byte Windows PowerShell 5.1 synchronization verifier with SHA-256 `4A5A4BBE08661D588673C4B4A1A7ABAB88FEB2999699658CBC91E8081266EB66`. Its UTF-16LE EncodedCommand transport is 8,188 bytes and 10,920 Base64 characters; complete-arguments SHA-256 is `1ED8A00D773578DD5EBCE903CE8FF4E2413E18D9FA7E82DB4D2268A0CE62C4C5`. Static parser errors were zero, and the verifier was not invoked during assembly.

The verifier starts exactly five `C:\Program Files\Git\cmd\git.exe` children through fixed ProcessStartInfo fields: fetch, local revision, fetched-origin revision, direct `ls-remote`, and porcelain status. It requires zero exits, empty stderr, exact single-line SHA grammars, three-way equality, clean worktree and absence of all four old/target evidence paths. Its fixed success stdout is 122 bytes with SHA-256 `BCDF0010147E5952AD0372ADF39EDA0A18D349B02107C340DEF05BAFE18C0F09`.

The corrected 5G-B.1.1.1 Manifest is externally rebound at 30,174 bytes and SHA-256 `A5AA1E9B4CB022AFCCF401E9C2193FC06FD45830151154E049DC7B59BB77E6AE`. The 58-line bootstrap and all downstream frozen sources remain unchanged and unexecuted.

Request, Manifest and review are governance materials only. Current status is `AMENDMENT_5G_B_1_1_1_1_PACKAGE_AWAITING_APPROVAL`; synchronization verification, source reconstruction, bootstrap, evidence and all official actions remain unapproved.

## Corrected Amendment 5G-B.1.1.1.1 Package

Package Review 1 accepts the original seven-path package scope and the 74-line pre-execution verifier but rejects commit `93cc76ae97043077d2d3dae93e2569833ea3ab59`. Its required final synchronization gate had no frozen source or process contract, and its text referred to first/second invocations while limits authorized only one verifier and five Git children.

The corrected package preserves the accepted pre-execution verifier byte-for-byte and separately freezes a 107-line post-evidence verifier. The new source is 7,130 UTF-8 bytes with SHA-256 `8877E18F75A94EE6DA326B09C3791E6641B6B9B32D42744BA23E033A20735A67`. Its UTF-16LE source is 14,220 bytes; EncodedCommand Base64 is 18,960 characters with SHA-256 `89F51EC73B762A7E8E9E661D0D2B81CAF6EB330A3C4C4789B375E72F2930DDE1`; complete arguments SHA-256 is `17327F58C123664224B95FABD85E7553B3E32F4F86659D9A17D13C68AD9FEB02`.

Post-evidence success stdout is fixed at 194 bytes with SHA-256 `2ED3F942961C4DA1F7A9D71C3B8A50E6E00275DBBE4038C594B8834B7499AB0F`. The verifier uses seven exact Git children and a process-scoped `HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT` binding. It requires local/origin/direct-remote equality, clean worktree, evidence-commit parent equality, exact two-path diff, both target regular files, unchanged pre/post file fingerprints, exact 789-byte machine evidence SHA, non-empty narrative audit and continued absence of both old paths.

Static PowerShell parsing and all source/transport/stdout fingerprint recomputations passed for both verifiers. Neither verifier was invoked. Counts are now unambiguous: pre-execution `1+5`, post-evidence `1+7`.

Current status is `CORRECTED_AMENDMENT_5G_B_1_1_1_1_PACKAGE_AWAITING_APPROVAL`. No synchronization verifier, bootstrap, semantics source, evidence path or official operation is authorized by the package itself.

## Stage4B-U1-D Pre-Gold Hard Failure 14

Corrected package `3d37c8a65888c2093403a71375bfa94dd51bac2e` received package-bound approval. Approval-governance commit `ba50d75e41f6046c2b0380462c3d7480542e15c4` is its exact two-path direct child and was pushed successfully.

The 74-line pre-execution verifier source, UTF-16LE/Base64 transport, complete arguments and expected 122-byte stdout identities all passed static reconstruction before process start. Exactly one verifier PowerShell process was then launched.

The process exit code was zero. The next host gate detected non-empty stderr and stopped before stdout length, SHA and exact-byte comparisons. The captured streams were not persisted, and the command threw before emitting its summary, so exact stderr content/length, stdout content/length and the internal Git-child completion count cannot be recovered or accepted. No retry or fallback occurred.

The worktree remained clean at approval commit `ba50d75...`, and all four old/target evidence paths remained absent. Static bootstrap reconstruction, bootstrap, harness, compatible verifier, wrapper, Python, evidence commit and post-evidence verifier all remained unstarted.

Full audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_14.md`. Current status is `CORRECTED_AMENDMENT_5G_B_1_1_1_1_PRE_EXECUTION_SYNC_STOPPED_HARD_FAILURE_14`; recovery requires a new independent review and package-bound Amendment.

## Amendment 5G-B.1.1.1.1.1 Raw-Stream Diagnostic Package

Hard Failure 14 Review 1 accepts the checkpoint and confirms that the original pre-verifier process exited zero but failed the outer non-empty-stderr gate before stdout validation. Raw stream payloads are unrecoverable, the internal Git-child count is unconfirmed, accepted exact success count is zero and synchronization remains unverified.

The new package freezes, but does not run, a Windows PowerShell 5.1 diagnostic launcher:

    source lines: 161
    source UTF-8 bytes: 9684
    source SHA-256: 4FA9DABF8701F67554F6D0D100EFD72DF78477F80F600057F5C26A9886471DD6
    UTF-16LE bytes: 19288
    Base64 characters: 25720
    Base64 SHA-256: F8095A51A5A4C550383112D13A335EB44B9B06E7F8655D5DA6441D201A1C97D5
    complete arguments characters: 25771
    complete arguments SHA-256: 86E326DBB39ED099A5AA4BD8CA46002656D2766768C731A88F15C784F88946C1
    fixed launcher stdout bytes: 122
    fixed launcher stdout SHA-256: 4B7803B9C64F467F42356292B015BE1866156F2F22111E6393B913B1CEF8B80C
    static parser errors: 0

The launcher revalidates the frozen corrected Manifest and original 74-line verifier transport before process start. A future approved invocation would start one unchanged pre verifier, concurrently drain `StandardOutput.BaseStream` and `StandardError.BaseStream`, then exclusive-create raw stdout and raw stderr before computing or writing metadata. It does not decode or reserialize either raw payload for storage.

The proposed machine paths are:

    results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stdout.bin
    results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stderr.bin
    results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_diagnostic.json

The proposed narrative path is:

    docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_14_PRE_SYNC_DIAGNOSTIC_AUDIT.md

Package assembly invoked neither the launcher nor the original verifier and created none of these paths. The package does not authorize execution. Current status is `AMENDMENT_5G_B_1_1_1_1_1_RAW_STREAM_DIAGNOSTIC_PACKAGE_AWAITING_APPROVAL`; bootstrap, semantics, post verifier and all official operations remain locked.

## Stage4B-U1-D Pre-Gold Hard Failure 15

Package `d6d8a76abcb903b74307ed68f5ceabc42d8be8e3` received package-bound approval. Approval-governance commit `ee84988fa6ccf5e7f3524bc2c2a5f94065abf918` is its exact two-path direct child and was pushed before execution.

The host reconstructed the frozen launcher exactly once. Its 161-line source, 9,684 UTF-8 bytes, source SHA-256, static parse, UTF-16LE/Base64 transport, complete arguments and expected 122-byte stdout all matched the package Manifest. Exactly one launcher process was then started, and it started exactly one unchanged original pre verifier.

The launcher exit code was zero and its stdout was the exact frozen 122 bytes with SHA-256 `4B7803B9C64F467F42356292B015BE1866156F2F22111E6393B913B1CEF8B80C`. Its stderr was not empty: 382 bytes, SHA-256 `4F2B6B3ED9201CA459DB2DD042E0A137C4E58BFE8E15A068E45AD8535FA5B1EF`. The empty-stderr hard gate therefore failed and consumed the authorization.

Before that outer gate, the frozen launcher exclusive-created and persisted:

    results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stdout.bin
      bytes: 122
      SHA-256: BCDF0010147E5952AD0372ADF39EDA0A18D349B02107C340DEF05BAFE18C0F09

    results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stderr.bin
      bytes: 382
      SHA-256: 4F2B6B3ED9201CA459DB2DD042E0A137C4E58BFE8E15A068E45AD8535FA5B1EF

    results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_diagnostic.json
      bytes: 944
      SHA-256: F4022C8B4DF507D9A63085698B846358FF6D33F2A67B55B0C54EB871E8EB101B

These files are preserved byte-for-byte. The approved narrative success audit was not created. Metadata records one original pre-verifier process with exit zero, exact stdout true, stderr empty false, internal Git-child count null/unconfirmed, accepted three-way synchronization successes zero and all downstream counts zero.

No raw payload was decoded or interpreted for the failure checkpoint. No retry, repair, replacement, bootstrap, semantics process, success evidence commit, post verifier, synthetic run, real validator, formal preflight or official operation occurred. Full audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_15.md`.

Current status is `AMENDMENT_5G_B_1_1_1_1_1_RAW_STREAM_DIAGNOSTIC_STOPPED_HARD_FAILURE_15`. Any further diagnostic or recovery action requires independent review and a new package-bound Amendment.

## Hard Failure 15 Review And Amendment 5G-B.1.1.1.1.2

Independent Review 1 accepts Hard Failure 15 and all three preserved machine files. The 382-byte stderr is a Windows PowerShell startup progress CLIXML record, not Git stderr or a verifier exception. Its exact identity is SHA-256 `4F2B6B3ED9201CA459DB2DD042E0A137C4E58BFE8E15A068E45AD8535FA5B1EF`, strict UTF-8 invalid, 512 Base64 characters and Base64 SHA-256 `1A3D87C52A5EB3036EE762D586A05D21A3080106A0E38AE3B75DC0C44BC8700B`.

The preserved stdout is the exact frozen 122-byte core-success JSON. Because the unchanged 74-line verifier can emit it only after all five Git children pass with empty Git stderr, the review accepts five completed Git children, three-way SHA equality, a clean worktree and four absent semantics paths for `ee84988fa6ccf5e7f3524bc2c2a5f94065abf918`. This does not repair the old outer launcher: its zero-byte stderr contract failed and its approval is consumed.

Amendment 5G-B.1.1.1.1.2 freezes an exact classifier. A PowerShell child passes only with zero stderr bytes or byte-for-byte equality with the frozen 382-byte payload. The classifier rejects truncation, append, duplicate payload and same-length mutation fixtures. Git, Python and every non-PowerShell child continue to require zero stderr.

The unchanged sources remain:

    pre verifier: 74 lines / 4114 bytes / 4A5A4BBE...26EB66
    post verifier: 107 lines / 7130 bytes / 8877E18F...35A67
    compatible verifier: 59 lines / 3512 bytes / 1A30DC70...A81BF
    semantics wrapper: 122 lines / 7890 bytes / DFA95A90...9E16C
    embedded Python: 46 lines / 2284 bytes / D0D3D6FC...3D602
    real validator: 195 lines / 15966 bytes / 0F066387...8249

The package adds only frozen parent-envelope definitions in its Manifest:

    pre host: 96 lines / 6787 bytes / 0E028228...E0672
    revised bootstrap: 98 lines / 7146 bytes / E3458CE9...8317B
    revised harness: 91 lines / 7654 bytes / 12315561...9CDA
    post host: 86 lines / 6347 bytes / 4757F3C8...A5F0

All four static parsers report zero errors. Their source, UTF-16LE/Base64, complete arguments, raw BaseStream capture, exact stdout and child-count contracts are registered in `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_2_MANIFEST.json`. Package assembly did not invoke any of them.

A future approval must bind the package commit, create a new exact-two-path approval-governance child, rerun pre synchronization for that new HEAD, execute the revised semantics chain, commit the exact two evidence paths, run post synchronization and stop. Historical synchronization for `ee84988...` cannot replace this future gate.

Current status is `AMENDMENT_5G_B_1_1_1_1_2_TRANSPORT_RECOVERY_PACKAGE_AWAITING_APPROVAL`. No transport process, bootstrap, semantics evidence, post verifier, synthetic, formal preflight or official operation is authorized by the package itself.

## Amendment 5G-B.1.1.1.1.2 Package Review 1 And Corrected Package

Independent Package Review 1 accepts the Hard Failure 15 checkpoint, preserved raw evidence, exact 382-byte classifier, 6/6 classifier fixtures, seven-path package scope and four inner envelope designs as static content. It rejects package `7f92c000bb3c22337c83dc28e32779f4eb9cfdf8`: no top-level source froze the actual launch/capture/classify operations; inner PowerShell stderr classes were reduced to Boolean acceptance; and the required narrative was committed before the post-host and post-verifier classes could exist.

The corrected package supersedes that unapproved commit and freezes six complete sources:

    pre host: 96 lines / 6816 bytes / 61EA2A37...5E50FB
    revised harness: 91 lines / 7857 bytes / DD11F1E6...73931
    revised bootstrap: 109 lines / 8325 bytes / 84D6868A...1FEB7
    post host: 86 lines / 6377 bytes / 430C0F64...E8853D
    pre/semantics outer runner: 194 lines / 14491 bytes / 6B24A6F2...CE124
    post-sync outer runner: 166 lines / 12149 bytes / 0BC1EDF0...DD35A

Every source uses LF joining with no trailing newline and has a frozen UTF-16LE/Base64 transport, complete-arguments fingerprint and zero static parser errors. The two outer runners contain the complete child ProcessStartInfo, concurrent raw BaseStream capture, exact stdout-variant gate, exact stderr classifier, exit order, process counts and post approval-governance environment assignment. Package assembly invoked zero frozen sources and created zero evidence.

The class-attestation channel is independent of the final semantics machine file. The pre host has two exact stdout variants; the revised harness has four exact envelopes carrying two classes plus the exact 789-byte semantics Base64; the bootstrap accepts only those raw bytes, writes the unchanged 789-byte evidence and has eight exact class variants; the post host has two exact variants. All complete variants and hashes are registered in the corrected Manifest. Only `EMPTY` and `EXACT_FROZEN_382_BYTE_STARTUP_CLIXML` are allowed.

The evidence order is now executable. The original two semantics paths remain the exact-two-path direct child of approval governance. Their narrative records only the six pre/semantics boundaries that already exist. After that evidence commit is pushed, the post-sync outer runner performs the post gate and then exclusive-creates:

    results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_post_sync_transport_attestation.json
    docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_POST_SYNC_TRANSPORT_AUDIT.md

Those two paths form a separate exact-two-path direct child of the semantics evidence commit and are pushed before the final stop. This package requests one approval-governance commit, one semantics evidence commit and one post-sync audit commit; any failure consumes the ordered authorization and forbids retry or cleanup.

The first temporary generator invocation stopped before any Manifest write because Windows PowerShell 5.1 decoded a UTF-8 no-BOM package-assembly script path as ANSI. The corrective invocation explicitly read strict UTF-8 bytes into a ScriptBlock. No frozen source or child process was invoked in either attempt; the event is recorded in the Manifest.

Current status is `CORRECTED_AMENDMENT_5G_B_1_1_1_1_2_PACKAGE_AWAITING_APPROVAL`. Approval governance, top-level runner reconstruction/execution, semantics evidence, post-sync audit, synthetic, real validator, formal preflight and every official/Gold action remain unapproved.

## Amendment 5G-B.1.1.1.1.2 Package Review 2 And Second Corrected Package

Independent Package Review 2 accepts first corrected commit `44e56ab955dfe5fe89cc8ec4343870b59d008c9a` and its seven-path scope, Hard Failure 15/raw evidence binding, exact classifier, six source designs, canonical class channel and pre/post audit separation. It rejects that package as written because the final post-sync audit commit was created and pushed after the last frozen synchronization verifier; local/fetched/direct GitHub main, final parent/path scope and final artifact stability therefore had no frozen terminal verifier.

The second corrected Manifest retains the accepted six sources and adds:

    final post-sync audit commit verifier: 164 lines / 12934 bytes / C0D96FD1...D2B2B
    complete arguments: 34447 chars / FB42C188...AF5B2
    fixed stdout: 195 bytes / 3EFE3ED5...6DE5

    final verifier host: 81 lines / 6024 bytes / C843B63E...91131
    complete arguments: 16095 chars / 74D0EB12...E6272
    canonical host stdout variants: 187 bytes / 731D2969...2716 and 218 bytes / E6360311...4A9

The final host binds the future package, approval-governance and semantics-evidence commits through three process-scoped environment variables and starts exactly one final verifier. The verifier launches exactly eleven frozen Git children: fetch; local, tracking and direct-remote revision reads; porcelain status; three ancestor reads; and three changed-path reads. Every Git stderr is strict zero and every stdout follows a command-specific exact grammar.

Final success requires local HEAD, fetched `origin/main` and direct GitHub main equality; `HEAD^/HEAD^^/HEAD^^^` equality with the bound semantics/approval/package commits; exact registered two-path sets for the final, semantics and approval commits; canonical post machine schema and matching narrative classes/approval binding; exact historical evidence; exact 789-byte semantics machine evidence; and before/after stability for all historical, semantics and post artifacts. After exact host success, no file or commit may be created.

The second corrected Manifest is 227,242 bytes with SHA-256 `69CA3DAD8664F12213933A603D0AE0955C8AC17E483E5DC433859839AD49086E`. All eight sources and complete transports independently recompute to their registered fingerprints and statically parse with zero errors. Package assembly invoked zero frozen sources and created zero evidence. The Manifest also records five zero-write read-only helper failures: the first four started no process, while the bounded diff preview used four read-only Git processes before its consumer closed the stream; none executed a frozen source.

Current status is `SECOND_CORRECTED_AMENDMENT_5G_B_1_1_1_1_2_PACKAGE_AWAITING_APPROVAL`. No approval governance, frozen-source execution, evidence creation, synthetic, real validator, formal preflight or official/Gold operation is authorized.

## Stage4B-U1-D Pre-Gold Hard Failure 16

Second corrected package `945f655b95cfee9e55ad2d20e7bd5018f9aee1e2` received package-bound approval. The exact-two-path approval-governance commit `72783071c17f6e3cab347823a8da080171c1a883` was created and pushed before source reconstruction. Local HEAD, fetched `origin/main` and direct GitHub main then matched; the worktree was clean, historical evidence was unchanged and all six future semantics/post-sync paths were absent.

The single authorized pre/semantics outer-runner reconstruction passed every frozen identity gate:

    source: 194 lines / 14491 bytes / 6B24A6F2...CE124
    static parser errors: 0
    complete arguments: 38599 chars / 53D27DD1...498753
    expected stdout: 170 bytes / E9AF80CB...8F29

The first `System.Diagnostics.Process.Start()` call then threw `System.ComponentModel.Win32Exception` with `The filename or extension is too long` before creating the PowerShell process. Accurate counts are one source reconstruction, one start attempt, zero runner processes, zero child processes, zero evidence creations and zero retries. PID, exit code, stdout and stderr are unavailable because no process was created.

No shorter command, temporary `.ps1`, alternate runtime, source change, fallback or retry was used. All historical machine files remain unchanged and all six future paths remain absent. Audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_16.md`.

Current status is `AMENDMENT_5G_B_1_1_1_1_2_PRE_RUNNER_START_STOPPED_HARD_FAILURE_16`. Independent review and a new package-bound Amendment are required before any transport change or new attempt. Semantics, post-sync, final verifier, synthetic, real validator, formal preflight and official/Gold operations remain locked.

## Hard Failure 16 Review 1 And Amendment 5G-B.1.1.1.1.3 Package

Independent Review 1 accepts checkpoint `f28fc526faf74f80fdefb96ca189769dbcf1e5e4`, the valid approval-governance commit, the successful static reconstruction, the one consumed start attempt, zero created processes and the fail-closed stop. Microsoft documents the `CreateProcessW` command-line limit as 32,767 characters including the terminating null. The frozen 38,599-character arguments therefore establish `ENCODED_COMMAND_COMMAND_LINE_OVERFLOW`; the old transport is not reusable.

Amendment 5G-B.1.1.1.1.3 freezes three target-specific raw-stdin loaders:

| Loader | Source | Complete arguments | Modeled full command line |
|---|---|---|---|
| Pre/semantics | 44 lines / 2,727 bytes / `87B30CA9...C5049` | 7,323 chars / `5C0A0101...8B7F` | 7,384 chars / `DA89A4F1...8323` |
| Post-sync | 44 lines / 2,719 bytes / `9184297C...C5BB4` | 7,303 chars / `6D87AA8C...E360` | 7,364 chars / `27354A8B...35E8` |
| Final verifier | 44 lines / 2,724 bytes / `F965E9B1...EA0C6` | 7,315 chars / `6DF16FFC...8131` | 7,376 chars / `C3685BD8...4C1A` |

The modeled full command line is quoted executable + space + arguments + terminating null. Margins to the documented limit are 25,383, 25,403 and 25,391 characters.

For each transport, the parent starts the short loader, immediately starts concurrent raw stdout/stderr drains, writes the exact ASCII Base64 payload through `StandardInput.BaseStream`, flushes/closes stdin and waits for all three activities. The loader reads raw bytes to EOF, requires exact ASCII byte/SHA identity, strict Base64 and UTF-16LE identities, exact target line/UTF-8/SHA identities and zero parser errors, then creates and invokes one target ScriptBlock in the same process. It emits no loader stdout.

The pre/post outer target sources remain byte-for-byte unchanged. The final verifier is rebound only to the new Manifest and Decision path and is frozen as 164 lines / 12,955 bytes / `AAF4B1C0...07AA0`; its fixed 195-byte success output is unchanged. The revised final host is 92 lines / 7,373 bytes / `F3AE0903...3CDC9`; its own modeled command line is 19,752 characters and it validates the child loader's full modeled command line before start.

All seven source designs statically parse with zero errors. Three fixture groups test command-line bounds, exact payload acceptance and nine mutation/error cases; all 30/30 pass under an independent in-memory validator. No loader, target ScriptBlock, PowerShell/Git/Python child, evidence or official operation ran during package assembly. The Manifest also preserves four zero-write read-only helper failures: a malformed `throw` statement before the final-validation body, an access-denied `rg.exe` start after a successful `Select-String`, an unusable PowerShell-only search caused by an invalid trailing-backslash exclusion regex, and a complete-validator identity assertion that expected a short revision label instead of the frozen descriptive revision and stopped before source reconstruction. None created a child process or invoked frozen source.

Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_APPROVAL_REQUEST.md`. Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_MANIFEST.json` (203,974 bytes; SHA-256 `DF088593BA620CE235419B2B759247914771FCFCE63B49A099A788AD29D5FC1C`).

Current status is `AMENDMENT_5G_B_1_1_1_1_3_BOUNDED_STDIN_TRANSPORT_PACKAGE_AWAITING_APPROVAL`. No loader execution, target invocation, evidence creation, synthetic, real validator, formal preflight or official/Gold operation is authorized.

## Amendment 5G-B.1.1.1.1.3 Package Review 1 And Corrected Package

Package Review 1 binds rejected package `97a8b169835c06330a6781ab63c59a482889c6bb` and its 203,974-byte Manifest SHA-256 `DF088593BA620CE235419B2B759247914771FCFCE63B49A099A788AD29D5FC1C`. It accepts Hard Failure 16 Review 1, the seven-path scope, all three loader/payload designs, bounded command-line identities, revised final host and 30/30 loader fixtures, but rejects the package for three blocking causes: unfrozen pre/post parent hosts, stale success evidence that attests rejected long EncodedCommand transports, and missing terminal gates for the current transport attestation.

The corrected package uses the review's option A and preserves the existing two semantics plus two post-sync evidence paths. Pre/post targets now load the corrected Manifest and write package/approval/semantics bindings plus current parent-host, loader, modeled-command-line, payload and decoded-target identities into their existing versioned narratives. The rejected pre `53D27DD1...498753` and post `D55D3A04...0ABC` fingerprints are prohibited from success evidence.

Nine source designs are frozen:

| Source | Lines / UTF-8 bytes | SHA-256 |
|---|---|---|
| Pre target | 209 / 16,383 | `B46C57D8...03B71` |
| Pre stdin loader | 44 / 2,727 | `E96B049E...D1AA8` |
| Pre parent host | 96 / 7,922 | `8F11033C...858A7` |
| Post target | 180 / 13,884 | `597AA12B...01FC4` |
| Post stdin loader | 44 / 2,719 | `79F2F61B...6B33C` |
| Post parent host | 99 / 8,588 | `DC0234BE...C12DB` |
| Final verifier | 228 / 21,120 | `6C2A6033...7BCCF` |
| Final stdin loader | 44 / 2,724 | `6BC6A432...6B032` |
| Final parent host | 92 / 7,377 | `48E4907A...6F185` |

The six loader/parent EncodedCommand full modeled command lines are 7,384, 21,176, 7,364, 22,928, 7,376 and 19,764 characters including terminal null; all are below 32,767. Both new parent hosts freeze loader/target reconstruction, parser gates, process-scoped commit bindings, concurrent raw drains, `StandardInput.BaseStream` write/flush/close and exit/stdout/stderr ordering.

The extended final verifier recomputes all six registered envelopes and three payloads before its eleven Git operations. It requires exact current transport lines in both narratives, validates the final parent/loader identities and rejects the two stale long-EncodedCommand success fingerprints.

Independent in-memory validation passes 9/9 source identities/parsers, 6/6 encoded envelopes, 3/3 raw-stdin payloads, 62/62 static/negative fixtures and 6/6 absent future paths. Package assembly ran zero frozen sources, child processes, evidence creations and official operations. Three zero-write read-only helper failures are preserved: a PowerShell 5.1 `-File` UTF-8 path decoding failure before project-file read, a strict-mode literal `$GitExe` expansion failure before Manifest/Request write, and a final-validation `H` function-name collision with the `Get-History` alias before source reconstruction.

Review: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_PACKAGE_REVIEW_1.md`. Corrected Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_APPROVAL_REQUEST.md`. Corrected Manifest: 321,442 bytes with SHA-256 `C1A11B789FD18D703AA6831BA5B513FC9ACB9767EC8A75016802030E0A0C1123`.

Current status is `CORRECTED_AMENDMENT_5G_B_1_1_1_1_3_PACKAGE_AWAITING_APPROVAL`. No parent host, loader, target, evidence, final verifier, synthetic, real validator, preflight or official/Gold operation is authorized.

## Amendment 5G-B.1.1.1.1.3 Package Review 2 And Second Correction

Package Review 2 binds corrected package `b9081b3c28c0c03e8bece797f5e05a74401f397b`, its actual parent `97a8b169835c06330a6781ab63c59a482889c6bb`, Hard Failure 16 ancestor `f28fc526faf74f80fdefb96ca189769dbcf1e5e4`, and 321,442-byte Manifest SHA-256 `C1A11B789FD18D703AA6831BA5B513FC9ACB9767EC8A75016802030E0A0C1123`.

The review accepts all nine source designs, six bounded envelopes, three raw-stdin payloads, both parent hosts, current-transport evidence schema, extended final verifier, stale long-transport rejection, 62/62 fixtures and four canonical parent-host stdout variants. It identifies no technical defect. Its only blocking cause is the corrected Request's statement that `f28fc526...` was the package direct parent; the actual chain is `f28fc526... -> 97a8b169... -> b9081b3c...`.

The second correction changes only governance lineage metadata. It records direct parent `b9081b3c...`, superseded original package `97a8b169...` and checkpoint ancestor `f28fc526...` separately. The nine `source_lines` arrays and every registered source SHA, complete-arguments SHA, modeled command-line SHA, payload identity, evidence-schema gate, fixture, future path, process count and one-pass order remain unchanged.

Review: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_PACKAGE_REVIEW_2.md`. Second-corrected Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_APPROVAL_REQUEST.md`. Manifest: 323,607 bytes with SHA-256 `804B4F8607532D6CE17EDE043D5A9511C7E855F4EB444C25F461381B6EDDA73D`.

Current status is `SECOND_CORRECTED_AMENDMENT_5G_B_1_1_1_1_3_PACKAGE_AWAITING_APPROVAL`. No execution is authorized.

## Hard Failure 17: Pre Parent Modeled-command Static Gate

Independent approval bound package `ef87f0379f4f31c54881c4a0e23a3f7ad8c8c35b` and Manifest 323,607 bytes / `804B4F8607532D6CE17EDE043D5A9511C7E855F4EB444C25F461381B6EDDA73D`. Exact two-path approval-governance commit `1afdd8075169e70d385e617ade480880cf3eb718` is its direct child and was pushed before the approved PRE command reconstruction. Local HEAD, tracked origin and direct GitHub main all equaled that commit; the worktree was clean, six future evidence paths were absent, and three historical machine-evidence files were stable.

The approved PRE reconstruction passed the 96-line / 7,922-byte source identity `8F11033CD306D118C4211109EACF8F0C1E9A90BCAEA8E19F99C933DC1C0858A7`, zero parser errors, and 21,115-character arguments identity `00B201AA16F7A1CF106ADACADBE35DDF44FF67E08FE4A2A8434A8912F4106E67`. It then failed before `Process.Start()` with `PRE_PARENT_MODELED_COMMAND_TEXT_MISMATCH`.

The failure was caused by the orchestration helper, not by a demonstrated package defect. It interpreted Manifest field `modeled_createprocess_command_line = QUOTED_FILE_NAME_SPACE_ARGUMENTS_TERMINAL_NULL` as literal command text and used `runtime = Windows PowerShell 5.1 Desktop` as an executable path label. A post-stop read-only diagnostic used `process_start_info_contract.file_name = C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` with the registered arguments and recomputed the exact registered 21,176-character modeled command line and SHA-256 `E8247D1AF7D1CC5F6FEBF32F9102D49A37076FA19602906D7C9121E45EC808F0`.

No `Process.Start()` call occurred. PRE parent, loader, target ScriptBlock, semantics chain, POST and FINAL process counts are all zero. No evidence path was created, all six future paths remain absent, all three historical machine files remain unchanged, and no retry, fallback, cleanup, source change, runtime switch, reset, rebase or force-push occurred. Earlier read-only package-inspection and precondition helpers that stopped on path lookup, unavailable `rg`, and PowerShell strict-mode empty-collection handling performed no frozen process start and no write; the pre-governance source-line/parser inspection is preserved as a sequencing limitation rather than omitted.

Current status is `AMENDMENT_5G_B_1_1_1_1_3_PRE_PARENT_MODELED_COMMAND_GATE_STOPPED_HARD_FAILURE_17`. The ordered PRE/POST/FINAL authorization is consumed and independent review plus a new package-bound approval is required before any further reconstruction or execution.

## Hard Failure 17 Review 1 And Amendment 5G-B.1.1.1.1.4 Package

Hard Failure 17 Review 1 accepts checkpoint `6c741c251dce55236b06dc5c06fd834b7649f8b2`, approval governance `1afdd8075169e70d385e617ade480880cf3eb718`, base package `ef87f0379f4f31c54881c4a0e23a3f7ad8c8c35b`, the passed PRE source/parser/arguments identities, the failure-before-Process.Start boundary, and all-zero runtime/evidence counts. Root cause is `ORCHESTRATOR_SCHEMA_DESCRIPTOR_MISINTERPRETATION`; neither a package source defect nor a bounded parent transport defect is established.

Amendment 5G-B.1.1.1.1.4 adds three tracked, ASCII-only PowerShell trust roots instead of another transient Manifest interpreter. PRE is 135 content lines / 8,118 bytes / `4EDC7E67056E12E7FA59A8BE436A12C565BBF3B1011C33C5431F06CFA1AC0C7E`; POST is 137 / 8,405 / `D32FC6E8DCC9B0393166EFCB11DC1D12BF766A5B0B6EAF06EE868F836F904569`; FINAL is 137 / 8,421 / `203DCA76C39873E833EBD0753EFDCB755C2B0F6BD44778E7F9632E77988734EC`. All three have a terminal LF and zero parser errors.

Each adapter requires descriptor `QUOTED_FILE_NAME_SPACE_ARGUMENTS_TERMINAL_NULL`, takes the executable only from `process_start_info_contract.file_name`, rejects `runtime`, `host_name`, and `transport_role` as executable sources, constructs `"` + file name + `" ` + complete arguments + terminal null, verifies exact character count and SHA, and only then creates `ProcessStartInfo`. It captures raw parent stdout/stderr concurrently and accepts only the registered parent stdout plus zero bytes or the exact frozen 382-byte PowerShell startup stderr.

Ten schema-semantics fixtures were applied independently to PRE, POST, and FINAL. Runtime-label path, descriptor-as-text, wrong descriptor/path, missing quotes/space/null, appended character, and same-length mutation all reject; only the exact formula accepts. The result is 30/30. No adapter, parent, loader, target, Git child, Python, evidence, synthetic, or official operation ran during package assembly.

The package additionally freezes a stricter pre-approval rule: before the future package-bound approval-governance commit is pushed, only package commit, Manifest file identity, worktree/path state, and local/origin/direct-main equality may be checked. Joining, parsing, or reconstructing frozen source lines, arguments, or modeled command lines is forbidden until after that push.

Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4_MANIFEST.json`, 24,293 bytes, SHA-256 `921B7BB63B0CF8E7B51CC6ED51A74C98A915E6C8E5FB2211E8235D7A378DE928`. Current state is `AMENDMENT_5G_B_1_1_1_1_4_FROZEN_TOP_LEVEL_ORCHESTRATION_ADAPTER_PACKAGE_AWAITING_APPROVAL`; the package itself authorizes no execution.

## Amendment 5G-B.1.1.1.1.4 Package Review 1 And Corrected Package

Package Review 1 binds rejected package `7d2dcd5fe525c86ab2b91e7ed2dfb17b1e6228ac`, its direct parent `6c741c251dce55236b06dc5c06fd834b7649f8b2`, and its 24,293-byte Manifest SHA-256 `921B7BB63B0CF8E7B51CC6ED51A74C98A915E6C8E5FB2211E8235D7A378DE928`. It accepts the exact ten-path package, three tracked ASCII adapter designs, descriptor/executable binding, unique modeled-command formula, three `-File` envelopes, 30/30 schema fixtures, and zero-execution assembly boundary.

The package is rejected because its adapters emitted only `parent_stderr_registered=true`, did not persist actual adapter execution, and were unknown to the inherited final verifier. The old four evidence paths could not prove adapter mediation, and immediate stop after FINAL left no step that could persist and independently verify the FINAL adapter observation.

The corrected package preserves all accepted base content. PRE is now 136 content lines / 8,222 bytes / `6D9466FD227E8DA1ADB6A24CFC170BF9880C87718CB6244CC5847774BEBB8A02`; POST is 138 / 8,509 / `89828EB855B64DACF98A76CFB2CAB956FEA29D2B6B80B187AE3BDA3A33EF9CC5`; FINAL is 125 / 8,247 / `364473BA69831ABA30780414390D13446AC618F73C21FF0C8DB87552C2F1AC8E`. Their top-level invocation envelopes are unchanged, but each now has two exact stdout variants carrying actual parent class `EMPTY` or `EXACT_FROZEN_382_BYTE_STARTUP_CLIXML`, six variants total.

The tracked capture-attestation host is 216 content lines / 14,152 bytes / `589134A5993BEBBCCBC6B50F5B331240103641AE8C7AC9687EA51BAB4D45D0CA`, ASCII-only, terminal-LF, parser-zero. In a future approved run it validates its own and the selected adapter's bytes/SHA and invocation envelope, starts exactly one adapter, captures raw streams concurrently, classifies outer adapter stderr, resolves the class-bearing adapter stdout, and serializes exact source/invocation/observation/commit/process fields. PRE and POST use `CreateNew` pending records outside the repository. FINAL writes its pending record after the inherited final verifier returns, validates all three, and promotes their original bytes with `CreateNew` to three versioned repository result paths.

Static compatibility inspection additionally found that the inherited 1.1.3 final verifier hard-coded `...1_1_1_1_3_APPROVAL_DECISION.md`, which cannot validate the corrected 1.1.4 approval path. The corrected FINAL adapter therefore directly starts the tracked dual-mode verifier in `PRE_ATTESTATION` mode. That mode validates six inherited envelopes, three payloads, seven evidence artifacts, rejected-transport absence, corrected four-layer Git lineage/path sets, source identities, clean worktree, remote triplet, and artifact stability with 12 Git children before FINAL attestation is created.

Those three result paths then form an exact three-path direct-child commit after the post-sync audit. The same dual-mode verifier is 362 content lines / 30,827 bytes / `75A62A892D5059B6E540275860F72D4E80BDD4E9489378245F50A38FC70A222D`, parser-zero. Its later `TERMINAL` mode validates the three adapter sources and invocation envelopes, capture host, all three execution attestations, all six observed adapter-level stderr classes, mandatory mediation process counts, original evidence, exact five-layer Git chain and changed-path sets, clean worktree, remote triplet, and artifact stability with 14 Git children. Both modes are read-only.

The corrected package contains five tracked PowerShell sources with zero parser errors, retains 30/30 schema fixtures, and passes 32/32 corrected-package static fixtures. No capture host, adapter, verifier mode, parent, loader, target, Git child from frozen source, Python, evidence, synthetic, or official process ran during assembly. Six corrected-package read-only helpers failed with zero writes/processes/evidence: `rg.exe` access denied, one nonexistent guessed review filename, one missing `if` parenthesis, `H` resolving to `Get-History`, a missing separator after `throw`, and strict-mode `.Count` on an unwrapped empty pipeline. Current source bytes are LF; because repository `core.autocrlf=true` and `.gitattributes` is absent, future source-identity gates fail closed if Git rewrites a checkout.

Corrected Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4_MANIFEST.json`, 41,597 bytes, SHA-256 `E0C0E8B329720C8B99130598E820E244E80707BAA628C1063688E209D067121A`. Current state is `CORRECTED_AMENDMENT_5G_B_1_1_1_1_4_PACKAGE_AWAITING_APPROVAL`; approval governance and all execution remain unauthorized.

## Amendment 5G-B.1.1.1.1.4 Package Review 2 And Second Correction

Package Review 2 binds rejected corrected package `61cfce1d3c11891ad0d8c2953fd855c2c3d0f9a8`, its direct parent `7d2dcd5fe525c86ab2b91e7ed2dfb17b1e6228ac`, and the 41,597-byte Manifest SHA-256 `E0C0E8B329720C8B99130598E820E244E80707BAA628C1063688E209D067121A`. It accepts Package Review 1, the exact twelve-path corrected scope, six class-bearing variants, capture-host and dual-mode-verifier static designs, the Approval Decision compatibility fix, four/five-layer Git designs, 30/30 inherited schema fixtures, reported 32/32 corrected fixtures, and zero execution.

It rejects that package because PRE/POST observations remained mutable outside Git until FINAL, the promotion gate did not establish original canonical bytes, semantically equivalent or extended JSON could pass terminal field checks, and capture-host stage invocation identity was neither persisted nor terminally validated.

The second correction selects Scheme A. The 211-line capture host directly creates each repository attestation through `CreateNew`: PRE is the third exact path in the semantics commit; POST is the third exact path in the post-sync commit; FINAL is the sole path in the final-attestation commit. No pending file or promotion step exists.

A new 50-line / 4,361-byte shared canonical builder with SHA-256 `4409E8AFF4EFECE2A69404F42ED39C355CACE0BE2DFD2ACB6033D045142AF55D` fixes schema `2.0`, the complete field set/order, escaping, integer/null rendering, strict UTF-8 without BOM, and no trailing newline. Before child execution, the capture host requires `[Environment]::CommandLine + NUL` to equal the selected stage modeled command exactly. Each record includes builder identity, capture-host source identity, that stage-specific capture-host invocation variant and arguments/modeled identities, adapter source/invocation identities, observed stdout and both stderr classes, bindings, and process counts.

The 388-line / 33,878-byte terminal verifier with SHA-256 `8D7BDF3224197C65CFB9A486DAA8E048AA0C86C88A87F75019036BF4A9D313D5` validates all three capture-host invocation envelopes. PRE_ATTESTATION validates the committed PRE/POST canonical records and FINAL absence before the FINAL capture returns; TERMINAL validates all three. Both rebuild every record through the shared builder and byte-compare raw repository bytes, rejecting extra/missing fields, reorder, whitespace, alternate escaping, duplicate keys, trailing LF, semantic-equivalent serialization, and same-length mutation.

Static assembly validates six source identities and parser-zero state, preserves 30/30 inherited and 32/32 corrected reports, and adds 18/18 second-corrected fixtures: 12 canonical-byte cases, three stage-specific capture-host invocation cases, and three stage-commit anchor/path cases. No canonical builder was dot-sourced, and no capture host, adapter, verifier mode, parent, loader, target, Git child from frozen sources, Python, evidence, synthetic, or official operation ran. Seven read-only helper attempts failed (`rg.exe` access denied; two repeated PowerShell empty-pipe parser errors; two compact `foreach` whitespace errors; one `H`/`Get-History` alias collision; and one invalid inline-`try` helper); corrected helpers passed, and all failures caused zero writes/processes/evidence.

Second-corrected Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4_MANIFEST.json`, 48,629 bytes, SHA-256 `E764A188AB11F49152B272F041CAC8FAC9477929C30475576D6349791E67373B`. Current state is `SECOND_CORRECTED_AMENDMENT_5G_B_1_1_1_1_4_STAGE_ANCHORED_CANONICAL_BYTE_ADAPTER_PACKAGE_AWAITING_APPROVAL`. Approval governance, capture, PRE/POST/FINAL, evidence commits, terminal verifier, synthetic, real validator, formal preflight, official, Gold, reservation, and Stage3B remain unauthorized.

## Hard Failure 18: PRE Capture Observer Alias Collision

The package-bound approval was recorded and pushed in exact two-path commit `677df53f014ab194e08042e4f605b5f879b9fa32`, whose direct parent is package `683d17bd70cc32dca2e495836bb6b16160a79f79`. Before PRE, local HEAD, tracked `origin/main`, and direct GitHub main were equal; the worktree was clean; and seven future evidence paths were absent.

Static validation after governance push passed 106/106 checks: all six tracked PowerShell sources matched bytes, SHA-256, LF-only ASCII encoding and parser-zero registrations; all three adapter, three capture-host and two verifier invocations matched their arguments, modeled-command and registered stdout identities.

The single approved PRE capture-host process was started through the frozen executable, arguments, working directory, redirects and package/approval environment bindings. `WaitForExit()` returned and concurrent raw stdout/stderr BaseStream copies completed. The outer observer then attempted to hash the in-memory byte arrays using a helper named `H`. PowerShell command precedence selected the existing `H` alias for `Get-History`, and `H $errBytes` failed with `Cannot locate the history for Id 65` before the child exit code or stream identities were printed or persisted.

Those in-memory raw bytes and the child exit code are no longer recoverable. They must not be represented as empty, registered, successful, or failed package output. The exact capture-host runtime failure, if any, remains unestablished. PRE adapter/parent/loader/target/semantics process counts are likewise `UNCONFIRMED`; absence of evidence is not used to infer them.

After the stop, all seven future paths were confirmed absent and the repository remained clean at `677df53f...`. The capture was not retried. No semantics commit, POST capture, FINAL capture, verifier mode, evidence cleanup, synthetic rebinding, real validator, formal preflight, official access, Gold, reservation, or Stage3B operation followed.

Current status: `AMENDMENT_5G_B_1_1_1_1_4_PRE_CAPTURE_OBSERVATION_UNRECOVERABLE_HARD_FAILURE_18`. See `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_18.md` for the full preservation boundary.

## Hard Failure 18 Review 1 And Frozen Outer Observer Package

Independent Review 1 accepts the Hard Failure 18 checkpoint and freezes the root cause as PowerShell resolving the outer helper name `H` to the `Get-History` alias after the one PRE capture-host process and both raw stream drains completed. The review does not infer child exit/stdout/stderr, capture-host success/failure, or PRE downstream process counts. The original authorization is consumed.

Amendment 5G-B.1.1.1.1.5 adds a tracked 203-line / 13,186-byte observer with SHA-256 `67DCCD6B2AFD10164924CB98DCC99B93BD2150FB77DC9438496440373D0FF325`. It supports PRE, POST, FINAL and TERMINAL and freezes each observer invocation, actual command-line gate, required dynamic bindings, child source/invocation, fixed child output, fixed observer output and process counts.

The observer reads ExitCode and materializes raw stdout/stderr immediately after WaitForExit and both drain tasks. Before any hash, classification, helper dispatch or serialization, it writes a `CreateNew` binary record and flushes it. The header is exactly 48 little-endian bytes: `HGRAGO15`, version 1, header length 48, mode code, completion flags 15, child exit, reserved zero, stdout length and stderr length. Raw stdout and stderr follow without a serializer. Any partial file is preserved.

The dual-mode verifier validates PRE/POST raw records during PRE_ATTESTATION and PRE/POST/FINAL raw records during TERMINAL, including exact header, total length, child exit, fixed stdout and registered empty/382-byte stderr. The terminal record is necessarily created after the terminal verifier exits and forms a one-path sixth-layer commit; no circular self-verification is claimed.

Static validation covered seven source identities, twelve invocation envelopes, registered stdout identities and 43 observer fixtures. Results were 34/34 identity checks and `12/12 + 16/16 + 15/15 = 43/43` fixtures. No tracked source was dot-sourced or run, and no evidence or experiment artifact was created.

Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_5_MANIFEST.json`, 37,645 bytes, SHA-256 `303A347368E4BFBF4CEBBB71DFE07E244328A60BC4DBE996A0444A5C56E45BF9`. Current status is `AMENDMENT_5G_B_1_1_1_1_5_FROZEN_OUTER_OBSERVER_DURABLE_RAW_CAPTURE_PACKAGE_AWAITING_APPROVAL`; approval governance and all execution remain unauthorized.

## Hard Failure 19: PRE Capture Host Returned Adapter Exit 1

Independent approval was recorded in exact two-path commit `950b56e83de8a87b7afe75eb3f021819e19516c8`, the direct child of package `f634a1ca766cc2885017f63f94ef9b87cab9a765`, and pushed before frozen-source execution. The local/tracking/direct GitHub triplet, clean worktree and eleven absent future paths passed. Post-governance static gates then passed 34/34 source/invocation/stdout identities and all 43/43 observer fixtures with zero static-stage process starts or writes.

The PRE observer was executed exactly once with only the frozen package and approval bindings. It returned exit code 1, zero stdout bytes and 492 stderr bytes after reporting `Observed child nonzero exit: 1`. No observer or child was retried.

Before applying that success gate, the observer created and flushed `results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_5_pre_capture_outer_observation.bin`. The file is 520 bytes with SHA-256 `4ABEB26000DDC77E8293DB1616682E6748E2290A9608959A2A040B1CD2780A70`. Its fixed header decodes to `HGRAGO15`, version 1, header length 48, PRE mode code 1, completion flags 15, child exit 1, reserved zero, stdout length zero and stderr length 472. Total length equals `48 + 0 + 472`, so the durable record is structurally complete.

The persisted capture-host stderr has SHA-256 `9E8393DD9738C73FCA928BD28E0031A6B8EABF4FABE9147FA0F101ED969D56EB` and reports `Adapter nonzero exit: 1`. This establishes the capture-host/adapter nonzero boundary but not the adapter's deeper error, parent stdout/stderr, loader/target/semantics result or inner process counts. Those remain `UNCONFIRMED`; no package-source or transport defect is inferred.

Two read-only post-failure helpers failed on a temporary `H`/`Get-History` alias collision and an ambiguous zero-byte `ComputeHash` overload. Both had zero writes and zero external child starts. The final explicit decoder succeeded, and repeated raw fingerprinting remained unchanged.

Only the PRE raw path existed. The PRE adapter attestation and semantics narrative/machine paths, all POST paths, both FINAL paths and the TERMINAL path remained absent. No four-path semantics success commit, POST, FINAL, PRE_ATTESTATION, TERMINAL, synthetic, real validator, formal preflight, official, Gold, reservation or Stage3B action followed.

Current status is `AMENDMENT_5G_B_1_1_1_1_5_PRE_CAPTURE_HOST_CHILD_NONZERO_STOPPED_HARD_FAILURE_19`. The raw record is failure evidence only and cannot be overwritten, deleted, retried, reused or represented as successful PRE evidence. Independent review and a new package-bound Amendment are required before further execution. See `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_19.md`.

## Amendment 5G-B.1.1.1.1.6 Reproducibility Boundary

Hard Failure 19 Review 1 accepts the complete 520-byte `HGRAGO15` record and limits the established runtime boundary to `PRE_CAPTURE_HOST_REPORTED_ADAPTER_NONZERO_EXIT_1`. The 1.1.5 approval is consumed. Adapter stdout/stderr, its internal gate, parent/loader/target results, and semantics progress are not reconstructed from absence.

The 1.1.6 package adds one tracked source per nested result boundary. All four writers use the same fixed no-serializer little-endian layout: 8-byte magic, uint32 version/header/layer/flags, int32 exit, zero uint32 reserved, uint64 stdout/stderr lengths, then exact raw streams. The magics/codes are `HGRAGO16/1`, `HGRAGA16/2`, `HGRAGP16/3`, and `HGRAGL16/4`. A failure may preserve only a contiguous outer-to-inner prefix. Every created record is `CreateNew`, durably flushed before classification, and never overwritten or cleaned.

The registered sources are:

```text
parent        12,118 bytes  91EC38326A39C8A4C9072821B34D4FE92D8423323B0051E027EF3348B56AA19E
adapter        9,752 bytes  0C97760D26FF4D00D75FCB8847170578AD2DDAA797A588F8FC1844380B3BF3F1
capture host  10,023 bytes  FD9C6261CEF905EFF2826D025ECE453863BC43AB5C2AEABA9C74C8EB55A8F73A
observer      13,263 bytes  C37CBF70AA91A0FC8341400DF74B5D883796F6EFEB6AC25A5DBA260716716D52
raw verifier   6,882 bytes  FF990722ECC7AFAC0C4C1B8778A6743197814F0A1480A5BA0417FFB71A8E47AF
```

Assembly validation is 116/116: 56 registry/Manifest/invocation/stdout checks, 36 durable-order checks, and 24 binary/path/HF19 checks. Validation read bytes and parsed ASTs only; no package source was dot-sourced or executed and no result path was created. Four failed read-only helper attempts caused zero writes and no frozen-source or experimental process start.

After the package commit is pushed and before a package-bound approval is pushed, do not repeat source joining, parsing, reconstruction, or execution. Only package/Manifest identity, old raw identity, future-path absence, worktree, and remote-triplet checks are allowed. The requested future run is at most one PRE observer chain followed by one failure-or-success evidence commit and immediate review stop; POST, FINAL, TERMINAL, synthetic, official, Gold, reservation, and Stage3B remain locked.
