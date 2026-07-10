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
