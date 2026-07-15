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
