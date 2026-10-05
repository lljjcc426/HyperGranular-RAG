# Data, configuration, and reconstruction scope

## Data sources and roles

- HotpotQA training distractor release v1.1, `hotpot_train_v1.1.json`: [official dataset](https://hotpotqa.github.io/). The study reuses an already evaluated 1,000-question historical cohort.
- MuSiQue-Ans v1.0, `musique_ans_v1.0_train.jsonl`: [official repository and data instructions](https://github.com/StonyBrookNLP/musique). The study reuses an already evaluated 3,000-question historical cohort.
- The study's input cohort is not the entirety of either public training set. Obtaining the source releases alone does not reconstruct the historical cohort. Exact historical cohort manifests and legal redistribution/access arrangements are additional prerequisites for a full model rerun; they are not distributed as identifiable records in this anonymous numerical package.
- The resulting 4,000 queries are exposed development data, not a new test set. `data_roles.csv` and `role_overlap.csv` give the actual role counts and query overlaps. FIT and TUNE also share 57 HotpotQA and 4,753 MuSiQue source blocks; question-group separation is not document separation.

## Implemented preparation rules

Starting with the historical cohort, join nonempty original sentences in source order into complete titled paragraphs and retain original sentence-to-paragraph spans. HotpotQA supporting-fact coverage remains sentence-based; MuSiQue coverage remains annotated-paragraph-based. Deduplicate paragraphs by dataset, case-folded whitespace-normalized title and text. The two development corpora contain 9,791 and 31,130 blocks.

Union queries sharing an exact normalized question or the same dataset/source question ID. For each group, choose the lexicographically smallest dataset + NUL + normalized-question key. Hash the string `rg-learned-set-v5-split` + NUL + key using SHA-256. A group containing any of the 96 previously exposed interface-development questions has DEV precedence; otherwise the first eight hexadecimal digits modulo five select TUNE when zero, FIT otherwise. Hashes are used here to describe the existing split, not as new integrity tests.

The QA panel is chosen within TUNE by stable group-hash ordering with the existing `v5-panel` salt: 48 bridge/16 comparison HotpotQA and 32 two-hop/32 longer-hop MuSiQue questions. MINE is a stratified 256+256 subset of FIT; DEV_SELECT is a stratified 64+64 subset of TUNE excluding QA groups. Their salts are `rg-v6-mine` and `rg-v6-select`. Quotas use integer proportional allocation with largest-remainder correction and deterministic group order. FIT=3,166 questions/3,165 groups; TUNE=738; DEV=96. The pre-existing DEV membership and historical cohort are required to reproduce this split exactly.

## Models, search, and reader

- Encoder: [BAAI/bge-large-en-v1.5](https://huggingface.co/BAAI/bge-large-en-v1.5), revision `d4aa6901d3a41ba39fb536a557fa166f842b0e09`; FP32 CLS pooling followed by L2 normalization, 512-token encoder ceiling. Exact dense Top128 over the relevant development paragraph corpus, no Gold insertion into evaluation candidates.
- Reader: [Qwen/Qwen2.5-3B-Instruct](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct), revision `aa8e72537993ba99e69dfaafa59ed015b17504d1`, unadapted FP16. Same tokenizer and constrained answer-field protocol, greedy, maximum 128 new tokens, complete input ceiling 1,024 tokens. Selected whole paragraphs appear in BGE order; no individual paragraph is truncated to force feasibility.
- Learned search: maximum six paragraphs, width-four beam with feasible Dense-K6 included in the final candidates. Only the full-support logit ranks sets. Exact ball/k-means variants preserve this beam procedure, not a global optimum.
- Dense-budget/MMR-budget share the 1,024-token ceiling but may use more than six short blocks. MMR relevance weight is 0.7. K6 variants are used for matched-cardinality support diagnostics.
- Main models H1/H2/H4 and DeepSets share support supervision and query–paragraph features. HOFM factors have rank 32, common representation width 128. Continuation uses two rounds at most, shared 64-set-per-query mined pools, learning rate 0.0003, AdamW weight decay 0.0001, batch eight queries, gradient norm one, and at most eight epochs per round. Checkpoints at epochs 2/4/8 maximize DEV_SELECT completeness, then coverage, then minimize original development loss, then prefer earlier epochs. It changes examples, loss and checkpoint selection together.
- Static H4 replay matches optimizer updates, not all forward evaluations. QA does not choose the continuation checkpoint. Seed repetition uses the same panel; it supplies no additional independent questions.
- Observed research software: CPython 3.12.0, PyTorch 2.12.1+cu130, Transformers 5.14.1, NumPy 2.5.1, lm-format-enforcer 0.11.3. OMP/MKL/OpenBLAS/NumExpr threads were one, tokenizer parallelism disabled; GPU was RTX 4060 Laptop 8 GB. The numerical reconstruction here requires none of these research packages.

## Results to implementation map

| Evidence | Supplement input | Reproduction scope |
|---|---|---|
| Same-panel Full/F1/EM, both seeds, paired counts | `qa_records.csv` | `reconstruct.py`, complete numerical derivation |
| FIT/TUNE/MINE/DEV_SELECT/QA roles | `data_roles.csv`, `role_overlap.csv` | Existing cohort membership counts, no query IDs distributed |
| Original selected support | `static_selection.csv` | Existing aggregate output from paragraph selection evaluation; model rerun not included |
| Checkpoint-selected support trajectory | `checkpoint_selection.csv` | Existing aggregate output from shared-pool continuation; not an independent QA result |
| Actual index timing | `index_cost.csv` | Recorded 32+32-query timing; no new benchmark, includes factor/index/token checks and some CPU/GPU overlap |

The experiment implementation separates corpus construction, supervision, scorer, feasible search, continuation training, and reader evaluation. Equations and selection/training rules appear in the manuscripts. Full reruns additionally need the original implementation, cohort manifests, source mappings, authorized labels, checkpoints, and prompt/decoder identity. This package is intentionally sufficient for the reported numerical summaries, not for independently regenerating all model predictions.
