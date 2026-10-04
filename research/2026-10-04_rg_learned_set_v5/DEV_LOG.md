# Development log

- Adopted the user's v5 specification from `C:/Users/cc/Downloads/CODEX_RG_LEARNED_SET_V5_ZH.md`; reference HEAD c051b785769bac2d507164edd45ab15d9e4daa2e. Existing unrelated dirty files are excluded from this task's commits.
- New implementation lives here; v1-v4 are read-only dependencies for data roles, P2 serialization/runtime and canonical scoring. No files deleted.
- Shared paragraph retrieval, supervised set selection and exact conditional-space search replace online relation extraction for this round. These change the algorithm and cannot explain historical static-q25 scores.
- Corpus construction produced 9,791 Hotpot and 31,130 MuSiQue blocks, 3,166 FIT queries, 738 TUNE, 96 historical DEV. The 128-query panel has exactly the requested 48/16 and 32/32 strata. Corpus documents overlap FIT/TUNE; this is explicitly a fixed-corpus development study.
- BGE encoding completed in 931.260 measured GPU-process seconds. The first execution kept the encoder allocated during the following CPU retrieval (23.637 s); this residency is conservatively added to GPU accounting below. Subsequent implementation releases it before retrieval. No encoding rerun is needed.
- Added H1/H2/H4 and DeepSets, shared supervised subset construction, exact Flat/GB/KM, separate one-representative approximation, common P2 QA and actual-input checks. No historical files modified or deleted.
- Current training epoch selection uses TUNE loss (same-size pair accuracy is recorded); five epochs without loss improvement stop training before the 30-epoch ceiling. This common compute-saving rule is fixed before any training results.
- Actual CPU synthetic run after adding the same-leaf multiple-member check: 9 tests, 0.824 seconds, OK; 2,016 parent-state parity checks. This establishes implementation algebra only.
