# 超粒球 RAG Stage 1D 查询感知超边报告

## Material Passport

- 项目方向：自适应粒球作为知识单元 + 边界不确定性驱动检索决策
- 当前阶段：Stage 1D Query-aware Hyperedge Scoring
- 日期：2026-07-09
- 数据：HotpotQA sample200 + MuSiQue sample200
- 检索空间：每个问题的候选 context units
- 向量空间：纯 Python TF-IDF
- Gold labels 是否用于索引：否
- 生成模型：未使用

## 1. 本轮目标

Stage 1C 的最佳超边配置提升了 Top-10 chain recall，但 false expansion rate 很高。

本轮目标是验证一个更克制的策略：

1. 不扩展所有相邻超边。
2. 先对超边进行 query-aware scoring。
3. 只选择 top-n 条 query-aware 超边。
4. 限制 expanded balls 数量。
5. 观察是否能在保留 chain recall 的同时降低 false expansion rate。

## 2. 新增方法

新增脚本：

- `E:\科研\超粒球RAG_实验脚本\stage1_query_aware_hyperedge.py`

查询感知超边分数：

```text
edge_score =
  w_query   * query_edge_term_match
+ w_title   * title_overlap_score
+ w_keyword * keyword_overlap_score
+ w_center  * ball_center_similarity
+ w_ball    * incident_ball_query_score
```

默认权重：

| Component | Weight |
|---|---:|
| query match | 0.35 |
| title overlap | 0.15 |
| keyword overlap | 0.20 |
| center similarity | 0.15 |
| incident ball score | 0.15 |

新增预算参数：

- `top_edges`
- `max_expanded_balls`
- `min_edge_score`
- `fill_with_fixed`

## 3. 对照基线

| Method | ALL ER@5 | ALL CR@5 | ALL ER@10 | ALL CR@10 | Avg Tokens@10 |
|---|---:|---:|---:|---:|---:|
| fixed TF-IDF | 0.4832 | 0.1650 | 0.6187 | 0.3125 | 486.1 |
| boundary fallback | 0.4755 | 0.1600 | 0.6193 | 0.3200 | 约 486.7 |
| Stage 1C best hyperedge | 0.4668 | 0.1650 | 0.6410 | 0.3700 | 未单独优化 token |

Stage 1D 的目标是接近或超过 Stage 1C best，同时降低误扩展。

## 4. Query-aware 参数扫描

整体结果：

| Config | HE Rate | Selected Edges | Expanded Balls | Yield | False | ER@5 | CR@5 | ER@10 | CR@10 | Tokens@10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qa_fill_e2_b2_t025 | 0.650 | 1.06 | 1.06 | 0.0646 | 0.9354 | 0.4186 | 0.1425 | 0.5669 | 0.3075 | 486.1 |
| qa_fill_e3_b3_t025 | 0.650 | 1.41 | 1.41 | 0.0621 | 0.9379 | 0.4307 | 0.1475 | 0.5767 | 0.3100 | 487.5 |
| qa_fill_e3_b3_t040 | 0.357 | 0.63 | 0.63 | 0.0502 | 0.9498 | 0.4109 | 0.1450 | 0.5625 | 0.2925 | 484.4 |
| qa_fill_e4_b4_t020 | 0.713 | 1.93 | 1.93 | 0.0641 | 0.9359 | 0.4346 | 0.1450 | 0.5890 | 0.3225 | 487.8 |
| qa_nofill_e3_b3_t020 | 0.713 | 1.57 | 1.57 | 0.0673 | 0.9327 | 0.4332 | 0.1425 | 0.5573 | 0.2825 | 437.1 |

## 5. 分数据集观察

### HotpotQA

最佳 query-aware 配置在 HotpotQA 上仍然低于 fixed TF-IDF。

| Config | HE Rate | Yield | False | ER@5 | CR@5 | ER@10 | CR@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| qa_fill_e4_b4_t020 | 0.885 | 0.0513 | 0.9487 | 0.3967 | 0.1100 | 0.5405 | 0.2400 |
| fixed TF-IDF | N/A | N/A | N/A | 0.4838 | 0.1700 | 0.6498 | 0.3300 |

判断：

- HotpotQA 上 query-aware 超边没有带来收益。
- 误扩展率仍高，说明 HotpotQA 的候选上下文中 title/keyword overlap 对 gold evidence 的区分度不足。

### MuSiQue

MuSiQue 仍然是更适合超边方向的数据集。

| Config | HE Rate | Yield | False | ER@5 | CR@5 | ER@10 | CR@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| qa_fill_e4_b4_t020 | 0.540 | 0.1132 | 0.8868 | 0.4725 | 0.1800 | 0.6375 | 0.4050 |
| fixed TF-IDF | N/A | N/A | N/A | 0.4825 | 0.1600 | 0.5875 | 0.2950 |
| Stage 1C best | 0.635 | 0.1152 | 0.8848 | 0.4775 | 0.1800 | 0.6500 | 0.4150 |

判断：

- Query-aware 版本在 MuSiQue 上仍高于 fixed TF-IDF。
- 但相比 Stage 1C best，ER@10 和 CR@10 略低。
- false expansion rate 没有实质下降。

## 6. 当前结论

本轮结果是一个有价值的负结果。

支持的判断：

1. 单纯 query-aware edge scoring 不能解决超边噪声。
2. 扩展预算可以降低 token 成本，但会明显损失 recall。
3. MuSiQue 的 connected reasoning 结构仍然对超边扩展友好。
4. HotpotQA 上当前超边构建信号不够干净。

不支持的判断：

1. 不支持“只要给超边加 query-aware 排序就能降低 false expansion rate”。
2. 不支持当前 title/keyword/center overlap 超边已经足够好。
3. 不支持继续靠参数调优作为主要科研路径。

## 7. 对研究方向的影响

这一步把问题定位得更清楚了：

目前瓶颈不是“扩展多少条边”，而是“候选超边本身质量不够”。

因此下一步应该从超边生成机制入手，而不是继续微调排序权重。

更准确的研究表述应调整为：

> 超粒球 RAG 的关键不只是以超边连接粒球，而是构建可由查询和边界不确定性共同约束的高阶证据关系；只有当超边质量足够高时，边界扩展才能提高 evidence chain recall 而不显著放大噪声。

## 8. 下一步

进入 Stage 1E：Evidence-aware Hyperedge Construction。

但这里的 evidence-aware 不能使用 gold label 泄漏。建议使用以下无监督信号：

1. Query-aware entity overlap：
   - 从 query 中抽取关键词/实体近似项。
   - 只保留与 query 关键词相关的 title overlap。
2. Bridge-term hyperedge：
   - 连接包含 query 中不同关键实体/短语的粒球。
   - 多跳问题通常需要覆盖多个 query facets。
3. Cross-ball complementarity：
   - 惩罚两个球内容过于相似的边。
   - 奖励两个球分别覆盖 query 的不同 term group。
4. Expansion budget by uncertainty：
   - 边界越不确定，扩展预算越高。
   - 核心区 query 不扩展或少扩展。

Stage 1E 的目标：

- 保持 MuSiQue CR@10 大于 fixed baseline。
- 将 false expansion rate 从约 0.88-0.94 降下来。
- 尝试让 Top-5 指标不低于 fixed baseline。

