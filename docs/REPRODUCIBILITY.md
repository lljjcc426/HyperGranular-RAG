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
