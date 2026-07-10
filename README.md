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

## 历史计划：Stage2D

下一轮实验重点不是继续堆超边数量，而是做 dense reranking 保护策略：

1. 固定 dense Top-5 或 Top-10 为保护区。
2. 只允许高置信边界扩展单元进入 rank 6-20。
3. 对 K=10/15/20 分别报告 ER、CR、context units、context tokens、false expansion。
4. 对 HotpotQA 与 MuSiQue 分开分析，避免只看 ALL 平均值。

详细路线见 `docs/ROADMAP.md`。

## Stage2E 结果

Stage2E 对 gated 超边插入候选做了无标签分位筛选。阈值只由候选的稠密相似度和 facet 分数计算，金标仅用于最终评测。

| Method | Protect | Insert | ER@10 | CR@10 | ER@20 | CR@20 | False insert | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Dense fixed | 0 | 0 | 0.7788 | 0.5625 | 0.9209 | 0.8250 | 0.0000 | baseline |
| Gated, unfiltered | 5 | 2 | 0.8029 | 0.6100 | 0.9313 | 0.8425 | 0.8727 | 完全复现 Stage2D 对应行 |
| Gated, score q25 | 5 | 4 | 0.8058 | 0.6125 | 0.9441 | 0.8700 | 0.8774 | 保持最高 CR@10，同时较无筛选 insert=4 降低误插率 |
| Gated, score q25 | 10 | 4 | 0.7788 | 0.5625 | 0.9493 | 0.8825 | 0.8733 | 当前筛选条件下最高 CR@20 |
| Gated, score q50 | 5 | 2 | 0.7958 | 0.5950 | 0.9292 | 0.8375 | 0.8407 | 更低误插率，但召回增益收缩 |

当前证据支持“轻度候选筛选可以改善保护式证据补全的精度-召回折中”，不支持“已经解决噪声”。分位阈值和评测来自同一批 400 queries，因此属于探索性结果，还需要冻结阈值后的独立测试。

## Stage2F 独立验证结果

Stage2F 在测试前提交冻结协议，并使用两个原始 dev 文件中未被 Stage2E 使用的 `[200:400)` 切片，共 400 queries。测试集与校准集 query ID 交集为 0，q25/q50 阈值没有根据测试集重估。

| Gate | Delta | 95% CI | Decision |
|---|---:|---:|---|
| q25 protect5/insert4 vs dense fixed CR@10 | +0.0175 | [-0.0125, 0.0475] | 主终点未通过 |
| q25 protect5/insert4 vs unfiltered false insert | -0.0129 | [-0.0206, -0.0055] | 通过；CR@10 observed delta +0.0075 |
| q25 protect10/insert4 vs dense fixed CR@20 | +0.0175 | [0.0025, 0.0350] | 通过 |
| q50 protect5/insert2 vs unfiltered false insert | -0.0512 | [-0.0783, -0.0259] | 探索性；CR@10 delta -0.0025 |

确定性复跑的两份 CSV 与首次运行 SHA256 完全一致。当前证据不支持“稳定提升 Top-10 证据链召回”，但支持较窄的结论：冻结的候选过滤能降低误插，且保护式插入能在未见 HotpotQA 查询上改善 Top-20 证据补全。MuSiQue 的 dense fixed CR@20 已为 1.0000，不能贡献 Top-20 增益。

## 下一步

Stage2G 将预注册“边界决策机制审计”，使用下一段未见查询比较 boundary-only 与相同阈值下的 all-query expansion，检验边界不确定性是否真的提高触发精度，而不再继续搜索更有利的 q25/q50 阈值。
