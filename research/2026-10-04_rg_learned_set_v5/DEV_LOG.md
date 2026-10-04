# Development log

- Adopted the user's v5 specification from `C:/Users/cc/Downloads/CODEX_RG_LEARNED_SET_V5_ZH.md`; reference HEAD c051b785769bac2d507164edd45ab15d9e4daa2e. Existing unrelated dirty files are excluded from this task's commits.
- New implementation lives here; v1-v4 are read-only dependencies for data roles, P2 serialization/runtime and canonical scoring. No files deleted.
- Shared paragraph retrieval, supervised set selection and exact conditional-space search replace online relation extraction for this round. These change the algorithm and cannot explain historical static-q25 scores.
