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
