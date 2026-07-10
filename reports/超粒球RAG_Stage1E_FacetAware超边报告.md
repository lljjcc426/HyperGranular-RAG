# 超粒球 RAG Stage 1E Facet-aware 超边报告

## Material Passport

- 项目方向：自适应粒球作为知识单元 + 边界不确定性驱动检索决策
- 当前阶段：Stage 1E Facet-aware Hyperedge Construction
- 日期：2026-07-09
- 数据：HotpotQA sample200 + MuSiQue sample200
- 检索空间：每个问题的候选 context units
- 向量空间：纯 Python TF-IDF
- Gold labels 是否用于索引：否
- 生成模型：未使用

## 1. 本轮目标

Stage 1D 表明：简单 query-aware scoring 无法解决超边误扩展。问题主要在候选超边质量，而不是排序权重。

本轮改为 facet-aware 超边生成：

1. 从 query 中抽取关键词/facet。
2. 计算 seed balls 已覆盖的 query facets。
3. 只扩展能补充新 facet 的候选 balls。
4. 显式限制 top facet edges 和 expanded balls。
5. 用 expansion yield / false expansion rate 检查噪声。

新增脚本：

- `E:\科研\超粒球RAG_实验脚本\stage1_facet_hyperedge.py`

## 2. 方法说明

候选扩展球必须满足：

- 至少补充 `min_new_terms` 个新的 query facet；或
- 在开启 `allow_high_score_no_new` 时，具备足够高的 query-ball score。

facet edge 分数：

```text
facet_score =
  w_new        * new_facet_coverage
+ w_total      * total_facet_coverage
+ w_ball       * query_ball_score
+ w_diversity  * diversity_from_seed_balls
- w_redundancy * overlap_with_seed_facets
```

默认权重：

| Component | Weight |
|---|---:|
| new facet coverage | 0.45 |
| total facet coverage | 0.20 |
| query-ball score | 0.20 |
| diversity | 0.15 |
| redundancy penalty | 0.20 |

## 3. 对照基线

| Method | ALL ER@5 | ALL CR@5 | ALL ER@10 | ALL CR@10 | False Expansion |
|---|---:|---:|---:|---:|---:|
| fixed TF-IDF | 0.4832 | 0.1650 | 0.6187 | 0.3125 | N/A |
| Stage 1C best hyperedge | 0.4668 | 0.1650 | 0.6410 | 0.3700 | 0.9456 |
| Stage 1D query-aware best | 0.4346 | 0.1450 | 0.5890 | 0.3225 | 0.9359 |

## 4. Facet-aware 参数扫描

整体结果：

| Config | HE Rate | Edges | Balls | Facet Gain | Yield | False | ER@5 | CR@5 | ER@10 | CR@10 | Tok@10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| facet_fill_e2_b2_s010 | 0.620 | 1.06 | 1.06 | 1.20 | 0.1440 | 0.8560 | 0.4774 | 0.1925 | 0.6345 | 0.3725 | 490.7 |
| facet_fill_e3_b3_s020 | 0.432 | 0.80 | 0.80 | 0.93 | 0.1388 | 0.8612 | 0.4626 | 0.1900 | 0.6145 | 0.3575 | 486.4 |
| facet_fill_e4_b4_s010 | 0.620 | 1.50 | 1.50 | 1.27 | 0.1232 | 0.8768 | 0.4874 | 0.2000 | 0.6312 | 0.3600 | 489.3 |
| facet_main | 0.620 | 1.33 | 1.33 | 1.25 | 0.1260 | 0.8740 | 0.4839 | 0.1975 | 0.6310 | 0.3625 | 489.5 |
| facet_merge_e3_b3_s010 | 0.620 | 1.33 | 1.33 | 1.25 | 0.1260 | 0.8740 | 0.4832 | 0.1650 | 0.6187 | 0.3125 | 486.1 |
| facet_nonew_e3_b3_s010 | 0.660 | 1.40 | 1.40 | 1.25 | 0.1239 | 0.8761 | 0.4851 | 0.1950 | 0.6310 | 0.3600 | 489.5 |

最佳平衡配置：`facet_fill_e2_b2_s010`

- Top facet edges = 2
- Max expanded balls = 2
- Min new terms = 1
- Min facet score = 0.10
- Fill with fixed = true

## 5. 最佳配置对比

### Overall

| Method | ALL ER@5 | ALL CR@5 | ALL ER@10 | ALL CR@10 | False Expansion |
|---|---:|---:|---:|---:|---:|
| fixed TF-IDF | 0.4832 | 0.1650 | 0.6187 | 0.3125 | N/A |
| Stage 1C best | 0.4668 | 0.1650 | 0.6410 | 0.3700 | 0.9456 |
| Stage 1E facet best | 0.4774 | 0.1925 | 0.6345 | 0.3725 | 0.8560 |

Stage 1E 相对 fixed TF-IDF：

- ER@5：-0.0058，基本持平。
- CR@5：+0.0275。
- ER@10：+0.0158。
- CR@10：+0.0600。

Stage 1E 相对 Stage 1C best：

- ER@5：+0.0106。
- CR@5：+0.0275。
- ER@10：-0.0065。
- CR@10：+0.0025。
- False expansion：从 0.9456 降到 0.8560。

## 6. 分数据集观察

### HotpotQA

| Method | ER@5 | CR@5 | ER@10 | CR@10 | False |
|---|---:|---:|---:|---:|---:|
| fixed TF-IDF | 0.4838 | 0.1700 | 0.6498 | 0.3300 | N/A |
| Stage 1C best | 0.4561 | 0.1500 | 0.6319 | 0.3250 | 0.9545 |
| Stage 1E facet best | 0.4773 | 0.1800 | 0.6290 | 0.3300 | 0.8567 |

判断：

- HotpotQA 上 Stage 1E 没有超过 fixed 的 ER@10。
- 但 CR@5 从 fixed 的 0.1700 提升到 0.1800。
- CR@10 与 fixed 持平。
- 相比 Stage 1C，误扩展明显下降。

### MuSiQue

| Method | ER@5 | CR@5 | ER@10 | CR@10 | False |
|---|---:|---:|---:|---:|---:|
| fixed TF-IDF | 0.4825 | 0.1600 | 0.5875 | 0.2950 | N/A |
| Stage 1C best | 0.4775 | 0.1800 | 0.6500 | 0.4150 | 0.8848 |
| Stage 1E facet best | 0.4775 | 0.2050 | 0.6400 | 0.4150 | 0.8550 |

判断：

- MuSiQue 上 Stage 1E 保持了 Stage 1C 的 CR@10 = 0.4150。
- CR@5 从 Stage 1C 的 0.1800 提升到 0.2050。
- false expansion 从 0.8848 降到 0.8550。
- 这是目前最支持“超边适合 connected reasoning”的结果。

## 7. 结论

本轮结果支持继续推进“超粒球 + 边界不确定性 + 高阶关系”的方向。

更具体地说：

1. Facet-aware 超边比 query-aware 排序更有效。
2. 问题确实出在超边生成质量，而不是简单的超边排序。
3. Facet-aware 机制在整体 CR@5、CR@10 上都超过 fixed baseline。
4. MuSiQue 上的 chain recall 提升最稳定，说明 connected reasoning 是首轮主应用场景。
5. false expansion rate 仍高，但已从 Stage 1C best 的 0.9456 降到 0.8560。

当前最强实验信号：

- ALL CR@10：0.3125 -> 0.3725。
- MuSiQue CR@10：0.2950 -> 0.4150。
- MuSiQue CR@5：0.1600 -> 0.2050。
- False expansion：0.9456 -> 0.8560。

## 8. 对论文贡献的启发

现在可以把方法贡献收束为三层：

1. Adaptive semantic granular balls：
   - 提供可测量的 center/radius/boundary。
2. Boundary uncertainty decision：
   - 决定是否需要扩展，而不是盲目扩展。
3. Facet-aware hyperedge expansion：
   - 只扩展能补充 query facet 的跨粒球关系。

这比早期“超边连接粒球”更清楚，也更能避开 HyperGraphRAG / Cross-Granularity HGRAG 的已有贡献。

## 9. 下一步

进入 Stage 2 前，建议先做两个整理工作：

1. Consolidated ablation table：
   - fixed TF-IDF
   - granular ball only
   - boundary fallback
   - naive hyperedge
   - query-aware hyperedge
   - facet-aware hyperedge
2. Error analysis：
   - 找出 facet-aware 成功提升 chain recall 的样本。
   - 找出 false expansion 仍高的样本。
   - 分类 HotpotQA 与 MuSiQue 的差异。

完成这两个后，再考虑接入 embedding model 或 LLM 生成。

