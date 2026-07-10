# HyperGranular-RAG

自适应粒球作为知识单元、边界不确定性驱动检索决策的 RAG 实验仓库。

本仓库用于跟进“超粒球 RAG”方向：以粒球作为可检索知识单元，以查询相关的高阶关系或超边补充跨粒球证据，并用边界不确定性控制扩展噪声。

## 当前研究问题

在多跳开放域问答中，是否可以用“粒球知识单元 + 查询相关超边/边界门控”提升证据链召回，同时控制非金证据扩展？

当前实验场景：

- HotpotQA sample200
- MuSiQue sample200
- 400 queries
- 12,304 candidate units
- 887 gold evidence units

数据文件和大体积中间结果未纳入仓库。当前本地实验数据位于：

- `E:\科研\超粒球RAG_数据\processed`
- `E:\科研\超粒球RAG_数据\reports`

## 主要结论快照

Stage1 TF-IDF 空间：

| Method | ER@10 | CR@10 | Notes |
|---|---:|---:|---|
| Fixed TF-IDF | 0.6187 | 0.3125 | 固定窗口基线 |
| Facet-aware hyperedge | 0.6345 | 0.3725 | 提升证据链召回，但扩展噪声高 |
| Boundary gated hyperedge | 0.6335 | 0.3725 | 保持 CR@10，同时降低 false expansion |

Stage2 dense 空间：

| Method | ER@10 | CR@10 | ER@20 | CR@20 | Notes |
|---|---:|---:|---:|---:|---|
| Dense fixed | 0.7788 | 0.5625 | 0.9209 | 0.8250 | dense baseline 很强 |
| Original dense gated | 0.7234 | 0.4750 | 0.7700 | 0.5625 | 不能替代 dense fixed |
| Fill + facet | 0.7875 | 0.5925 | 0.9468 | 0.9000 | 召回最好，噪声高 |
| Fill + gated | 0.7750 | 0.5650 | 0.9472 | 0.8900 | 适合作为 Top-20 证据补全 |
| Protect10 + gated | 0.7788 | 0.5625 | 0.9476 | 0.8875 | Top-10 保守，Top-20 补证据 |

Stage2D protected dense reranking：

| Method | Protect | Insert | ER@10 | CR@10 | ER@20 | CR@20 | Notes |
|---|---:|---:|---:|---:|---:|---:|---|
| Dense fixed | 0 | 0 | 0.7788 | 0.5625 | 0.9209 | 0.8250 | dense baseline |
| Facet insert | 5 | 2 | 0.8045 | 0.6125 | 0.9313 | 0.8425 | 当前 CR@10 最好 |
| Gated insert | 5 | 2 | 0.8029 | 0.6100 | 0.9313 | 0.8425 | Top-10 增益接近 facet，false insert 较低 |
| Gated insert | 5 | 4 | 0.8053 | 0.6125 | 0.9445 | 0.8725 | Top-20 更强，但 false insert 更高 |
| Facet insert | 10 | 8 | 0.7788 | 0.5625 | 0.9525 | 0.9000 | 当前 CR@20 最好，Top-10 被保护 |

当前可支撑的谨慎表述：

> dense 空间里，超粒球/超边扩展不适合替代 dense fixed Top-10；但作为受保护的 Top-20 证据补全机制是有效的。

## 仓库结构

```text
scripts/   实验、审计、汇总脚本
reports/   阶段性 Markdown 研究报告
results/   关键 CSV 汇总表和审计表
docs/      路线图与复现实验说明
```

## 复现入口

核心脚本：

- `scripts/stage1_build_corpus.py`
- `scripts/stage1_tfidf_baseline.py`
- `scripts/stage1_facet_noise_gate.py`
- `scripts/stage2_bootstrap_reliability.py`
- `scripts/stage2_dense_replication.py`
- `scripts/stage2_dense_protection_compare.py`
- `scripts/stage2d_protected_rerank.py`

注意：部分脚本目前仍使用本地绝对路径或需要显式传入 `--units`、`--queries`、`--output-prefix`、`--embedding-cache`。后续应优先完成路径参数化和一键复现实验入口。

## 下一步

下一轮实验重点不是继续堆超边数量，而是做 dense reranking 保护策略：

1. 固定 dense Top-5 或 Top-10 为保护区。
2. 只允许高置信边界扩展单元进入 rank 6-20。
3. 对 K=10/15/20 分别报告 ER、CR、context units、context tokens、false expansion。
4. 对 HotpotQA 与 MuSiQue 分开分析，避免只看 ALL 平均值。

详细路线见 `docs/ROADMAP.md`。
