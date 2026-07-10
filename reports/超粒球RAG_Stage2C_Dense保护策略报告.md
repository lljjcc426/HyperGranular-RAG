# Stage2C Dense Protection Strategy Report

## Material Passport

- Stage: Stage2C dense protection recalibration
- Corpus: HotpotQA sample200 + MuSiQue sample200, 400 queries, 12,304 candidate units
- Embedding cache: `E:\科研\超粒球RAG_数据\processed\stage2_dense_allminilm_embeddings.npz`
- Gold labels used for indexing: No
- Generator used: No
- Scripts changed: `E:\科研\超粒球RAG_实验脚本\stage2_dense_replication.py`
- New comparison script: `E:\科研\超粒球RAG_实验脚本\stage2_dense_protection_compare.py`
- Environment note: runs completed with the same NumPy/numexpr/pandas compatibility warnings observed in Stage2B.

## ALL Metrics

| Strategy | Method | ER@10 | CR@10 | ER@20 | CR@20 | Ctx@20 | False expansion | Delta CR@10 vs dense_fixed | Delta CR@20 vs dense_fixed |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| original | fixed | 0.7788 | 0.5625 | 0.9209 | 0.8250 | 19.9650 | 0.0000 | +0.0000 | +0.0000 |
| original | facet | 0.7559 | 0.5350 | 0.8123 | 0.6400 | 11.8300 | 0.9054 | -0.0275 | -0.1850 |
| original | gated | 0.7234 | 0.4750 | 0.7700 | 0.5625 | 10.4375 | 0.8857 | -0.0875 | -0.2625 |
| fill | facet | 0.7875 | 0.5925 | 0.9468 | 0.9000 | 19.9650 | 0.9054 | +0.0300 | +0.0750 |
| fill | gated | 0.7750 | 0.5650 | 0.9472 | 0.8900 | 19.9650 | 0.8857 | +0.0025 | +0.0650 |
| merge | facet | 0.7788 | 0.5625 | 0.9209 | 0.8250 | 19.9650 | 0.9054 | +0.0000 | +0.0000 |
| merge | gated | 0.7788 | 0.5625 | 0.9209 | 0.8250 | 19.9650 | 0.8857 | +0.0000 | +0.0000 |
| protect10_fill | facet | 0.7788 | 0.5625 | 0.9535 | 0.9050 | 19.9650 | 0.9054 | +0.0000 | +0.0800 |
| protect10_fill | gated | 0.7788 | 0.5625 | 0.9476 | 0.8875 | 19.9650 | 0.8857 | +0.0000 | +0.0625 |

## Query-Level Delta Counts vs Original Dense Fixed

| Strategy | Method | Metric | Improved | Same | Regressed |
|---|---|---|---:|---:|---:|
| fill | facet | CR10 | 45 | 322 | 33 |
| fill | facet | CR20 | 42 | 346 | 12 |
| fill | gated | CR10 | 41 | 319 | 40 |
| fill | gated | CR20 | 36 | 354 | 10 |
| merge | facet | CR10 | 0 | 400 | 0 |
| merge | facet | CR20 | 0 | 400 | 0 |
| merge | gated | CR10 | 0 | 400 | 0 |
| merge | gated | CR20 | 0 | 400 | 0 |
| protect10_fill | facet | CR10 | 0 | 400 | 0 |
| protect10_fill | facet | CR20 | 40 | 352 | 8 |
| protect10_fill | gated | CR10 | 0 | 400 | 0 |
| protect10_fill | gated | CR20 | 33 | 359 | 8 |

## Evidence-Grounded Reading

- `merge-fixed` at ER/CR@10 and @20 is identical to original dense fixed in ALL metrics, because selected hyperedge units are merged and then re-sorted by the same dense score.
- `fill-with-fixed` repairs the Stage2B truncation problem: context_units@20 becomes 19.965 for ball/facet/gated instead of the earlier ball-only 7.9225.
- `fill + facet` gives the strongest ALL recall here: CR@10 0.5925 and CR@20 0.9000, but its false expansion rate is 0.9054.
- `fill + gated` reduces false expansion to 0.8857 and keeps CR@20 at 0.8900, but CR@10 is only 0.5650, barely above dense_fixed 0.5625.
- `protect10 + fill` forces Top-10 to match dense_fixed, so CR@10 cannot show hyperedge gains; its value is mainly in Top-20 evidence completion.

## Next Gate

Stage2C supports a narrower claim: dense-space hyperedge expansion is useful as a protected Top-20 supplement, not as a replacement for dense fixed Top-10 ranking. The next experiment should test a reranking rule that inserts only high-confidence expanded units into ranks 6-20, then reports budgeted context performance at K=10/15/20.
