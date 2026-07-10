# Stage2D Protected Dense Reranking Report

## Material Passport

- Stage: Stage2D protected dense reranking
- Units: `E:\科研\超粒球RAG_数据\processed\stage1_sample400_units.jsonl`
- Queries: `E:\科研\超粒球RAG_数据\processed\stage1_sample400_queries.jsonl`
- Embedding cache: `E:\科研\超粒球RAG_数据\processed\stage2_dense_allminilm_embeddings.npz`
- Gold labels used for indexing: No
- Generator used: No
- Strategy: preserve dense-fixed prefix, insert a budgeted number of hyperedge expansion units, then fill with dense-fixed ranking.

## ALL Summary

| Strategy | Method | Protect | Insert | ER@10 | CR@10 | ER@15 | CR@15 | ER@20 | CR@20 | False insert |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed | fixed | 0 | 0 | 0.7788 | 0.5625 | 0.8591 | 0.7075 | 0.9209 | 0.8250 | 0.0000 |
| protected_insert | facet | 5 | 2 | 0.8045 | 0.6125 | 0.8712 | 0.7300 | 0.9313 | 0.8425 | 0.8836 |
| protected_insert | facet | 10 | 8 | 0.7788 | 0.5625 | 0.8917 | 0.7750 | 0.9525 | 0.9000 | 0.9347 |
| protected_insert | gated | 5 | 2 | 0.8029 | 0.6100 | 0.8734 | 0.7325 | 0.9313 | 0.8425 | 0.8727 |
| protected_insert | gated | 5 | 4 | 0.8053 | 0.6125 | 0.8894 | 0.7650 | 0.9445 | 0.8725 | 0.8984 |
| protected_insert | gated | 10 | 2 | 0.7788 | 0.5625 | 0.8765 | 0.7400 | 0.9332 | 0.8475 | 0.8972 |
| protected_insert | gated | 10 | 4 | 0.7788 | 0.5625 | 0.8908 | 0.7675 | 0.9497 | 0.8850 | 0.9048 |

## Best Observed Rows

- Best ALL CR@10: protected_insert / facet / protect=5 / insert=2 / CR@10=0.6125.
- Best ALL CR@20: protected_insert / facet / protect=10 / insert=8 / CR@20=0.9000.

## Query-Level CR Delta vs Dense Fixed

| Method | Protect | Insert | Metric | Improved | Same | Regressed |
|---|---:|---:|---|---:|---:|---:|
| gated | 5 | 2 | chain_recall_at_1 | 0 | 400 | 0 |
| gated | 5 | 2 | chain_recall_at_3 | 0 | 400 | 0 |
| gated | 5 | 2 | chain_recall_at_5 | 0 | 400 | 0 |
| gated | 5 | 2 | chain_recall_at_10 | 23 | 373 | 4 |
| gated | 5 | 2 | chain_recall_at_15 | 10 | 390 | 0 |
| gated | 5 | 2 | chain_recall_at_20 | 8 | 391 | 1 |
| gated | 5 | 4 | chain_recall_at_1 | 0 | 400 | 0 |
| gated | 5 | 4 | chain_recall_at_3 | 0 | 400 | 0 |
| gated | 5 | 4 | chain_recall_at_5 | 0 | 400 | 0 |
| gated | 5 | 4 | chain_recall_at_10 | 36 | 348 | 16 |
| gated | 5 | 4 | chain_recall_at_15 | 25 | 373 | 2 |
| gated | 5 | 4 | chain_recall_at_20 | 20 | 379 | 1 |
| gated | 10 | 2 | chain_recall_at_1 | 0 | 400 | 0 |
| gated | 10 | 2 | chain_recall_at_3 | 0 | 400 | 0 |
| gated | 10 | 2 | chain_recall_at_5 | 0 | 400 | 0 |
| gated | 10 | 2 | chain_recall_at_10 | 0 | 400 | 0 |
| gated | 10 | 2 | chain_recall_at_15 | 14 | 385 | 1 |
| gated | 10 | 2 | chain_recall_at_20 | 10 | 389 | 1 |
| gated | 10 | 4 | chain_recall_at_1 | 0 | 400 | 0 |
| gated | 10 | 4 | chain_recall_at_3 | 0 | 400 | 0 |
| gated | 10 | 4 | chain_recall_at_5 | 0 | 400 | 0 |
| gated | 10 | 4 | chain_recall_at_10 | 0 | 400 | 0 |
| gated | 10 | 4 | chain_recall_at_15 | 29 | 366 | 5 |
| gated | 10 | 4 | chain_recall_at_20 | 25 | 374 | 1 |

## Evidence-Grounded Reading

- This report only describes the produced CSV metrics; it does not claim generator answer quality.
- A protected-prefix strategy is useful only if its chain recall does not regress against dense fixed at the target K.
- If protect=10, CR@10 is structurally constrained to equal dense fixed because no inserted unit can enter Top-10.
- False insert rate measures inserted non-gold units among inserted units, not among all expanded candidates.
