# 超粒球 RAG Stage 1 粒球基线报告

## Material Passport

- 项目方向：自适应粒球作为知识单元 + 边界不确定性驱动检索决策
- 当前阶段：Stage 1 Retrieval-only MVP
- 日期：2026-07-08
- 数据：HotpotQA sample200 + MuSiQue sample200
- 检索空间：每个问题的候选 context units
- 向量空间：纯 Python TF-IDF
- 生成模型：未使用

## 1. 本次执行内容

本轮完成三类 retrieval-only 实验：

1. Fixed unit TF-IDF baseline：直接按 query-unit TF-IDF 相似度排序。
2. Naive granular-ball retrieval：先选粒球，再展开球内单元。
3. Boundary fallback retrieval：先判断 query 是否处于粒球边界/低置信状态，边界时回退到 fixed unit 检索。

当前实验仍是 MVP，不是最终超粒球方法。它的作用是确认：

- 粒球组织是否天然优于固定 evidence unit。
- 边界不确定性是否有必要。
- 后续是否应继续投入超边和边界策略。

## 2. Fixed Unit TF-IDF Baseline

| k | Evidence Recall | Hit Rate | Full Chain Recall | Avg Tokens |
|---:|---:|---:|---:|---:|
| 1 | 0.2577 | 0.5550 | 0.0000 | 46.70 |
| 3 | 0.4222 | 0.7525 | 0.1225 | 143.74 |
| 5 | 0.4832 | 0.8175 | 0.1650 | 236.60 |
| 10 | 0.6187 | 0.9200 | 0.3125 | 486.12 |
| 20 | 0.9195 | 0.9975 | 0.8225 | 992.15 |

这是当前要击败的地板线。

## 3. Naive Granular-Ball Retrieval

主配置：

- min_size = 2
- max_size = 5
- radius_threshold = 0.78
- max_depth = 6
- boundary_width = 0.2

整体结果：

| k | Evidence Recall | Full Chain Recall | Avg Tokens |
|---:|---:|---:|---:|
| 1 | 0.2009 | 0.0000 | 45.76 |
| 3 | 0.2773 | 0.0600 | 141.42 |
| 5 | 0.3592 | 0.1275 | 238.32 |
| 10 | 0.5450 | 0.2950 | 484.65 |
| 20 | 0.8594 | 0.7225 | 986.52 |

球结构诊断：

- Avg balls/query：7.31
- Avg ball size：5.24
- Avg ball radius：0.4503
- Avg boundary units/query：22.10

结论：单纯“按球心选球再展开”整体输给 fixed unit。原因从结果上看很明确：粒球引入了结构约束，但还没有使用边界不确定性和超边补偿，所以低预算 top-k 会漏掉一些直接相关 evidence units。

## 4. 粒球参数扫描

整体指标：

| Config | Avg Balls | Avg Ball Size | ER@5 | CR@5 | ER@10 | CR@10 |
|---|---:|---:|---:|---:|---:|---:|
| ms3_r060 | 8.87 | 4.58 | 0.3688 | 0.1375 | 0.5363 | 0.2950 |
| ms3_r078 | 8.87 | 4.58 | 0.3688 | 0.1375 | 0.5363 | 0.2950 |
| ms8_r078 | 5.44 | 6.56 | 0.3370 | 0.1050 | 0.5365 | 0.2925 |
| ms12_r078 | 4.08 | 8.38 | 0.3483 | 0.0925 | 0.5007 | 0.2600 |
| ms20_r078 | 2.73 | 14.03 | 0.3929 | 0.1175 | 0.5050 | 0.2200 |

观察：

- 只调粒球大小和半径阈值，无法稳定超过 fixed unit baseline。
- 球更碎时 Top-10 chain recall 略好，但 Top-5 仍低。
- 球更大时更接近 fixed unit，但粒球结构贡献变弱。

## 5. Boundary Fallback Retrieval

策略：

- 若 query 到 top ball 的距离接近球半径，判为边界不确定。
- 若 top1/top2 ball score 差距过小，判为选择不确定。
- 若 top ball score 过低，判为低置信。
- 触发不确定时回退到 fixed unit 检索；否则使用粒球展开。

阈值扫描整体结果：

| Config | Fallback Rate | ER@5 | CR@5 | ER@10 | CR@10 |
|---|---:|---:|---:|---:|---:|
| bf_b010_s002_m005 | 0.335 | 0.4092 | 0.1375 | 0.5632 | 0.2900 |
| bf_b025_s005_m012 | 0.667 | 0.4591 | 0.1500 | 0.6022 | 0.3075 |
| bf_b025_s010_m020 | 0.828 | 0.4678 | 0.1475 | 0.6099 | 0.3075 |
| bf_b050_s005_m012 | 0.805 | 0.4701 | 0.1600 | 0.6110 | 0.3150 |
| bf_b050_s010_m020 | 0.917 | 0.4755 | 0.1600 | 0.6193 | 0.3200 |

对比 fixed unit：

- Fixed ER@5 = 0.4832；当前最佳 boundary fallback ER@5 = 0.4755。
- Fixed CR@5 = 0.1650；当前最佳 boundary fallback CR@5 = 0.1600。
- Fixed ER@10 = 0.6187；当前最佳 boundary fallback ER@10 = 0.6193。
- Fixed CR@10 = 0.3125；当前最佳 boundary fallback CR@10 = 0.3200。

结论：边界 fallback 在 Top-10 上略微超过 fixed unit，但 Top-5 尚未超过。这个结果不能作为强贡献，但足以说明“边界不确定性驱动决策”比 naive 粒球展开更合理。

## 6. 分数据集观察

### HotpotQA

最佳 boundary fallback 配置 `bf_b050_s010_m020`：

- Fallback rate：0.920
- ER@5：0.4736
- CR@5：0.1650
- ER@10：0.6411
- CR@10：0.3250

HotpotQA 上，边界 fallback 的 Top-10 指标接近 fixed unit，但没有超过：

- Fixed HotpotQA ER@10 = 0.6498，boundary fallback ER@10 = 0.6411，略低。
- Fixed HotpotQA CR@10 = 0.3300，boundary fallback CR@10 = 0.3250，略低。

因此 HotpotQA 上当前没有形成优势。

### MuSiQue

粒球对 MuSiQue 更友好。部分配置下 naive 粒球或 boundary fallback 的 chain recall 有提升：

- Naive `ms8_r078`：MuSiQue ER@10 = 0.6125，CR@10 = 0.4200。
- Fixed MuSiQue ER@10 = 0.5875，CR@10 = 0.2950。

这说明 MuSiQue 中 connected reasoning 的证据结构更适合被粒球组织捕捉。这个信号和我们的研究设想一致，但还需要更严谨的机制设计。

## 7. 当前判断

证据状态：

- 不支持“粒球单元天然优于 fixed unit top-k”。
- 支持“边界不确定性策略是必要的”。
- 支持“MuSiQue 这类 connected reasoning 数据集更适合验证超粒球方向”。
- 暂不支持把 naive granular-ball retrieval 作为主方法。

对研究方向的影响：

当前结果没有否定方向，反而把贡献边界变清楚了：

1. 不能只提出“用粒球替代 chunk”。
2. 必须突出“边界不确定性驱动检索决策”。
3. 下一步必须加入超边，因为单个粒球只能组织局部语义，不能主动补全跨粒球证据链。

## 8. 下一步

进入 Stage 1C：Hyperedge-aware retrieval。

最小实现路线：

1. 以 gold-free 方式构建候选超边：
   - 同题候选 context 内共享实体/标题词。
   - query 与多个球有相近相似度时，连接这些边界球。
   - 支持按 title overlap / noun phrase overlap / TF-IDF keyword overlap 建边。
2. 检索策略：
   - core query：使用 top ball。
   - boundary query：沿超边扩展到相邻 ball。
   - low confidence query：fallback fixed unit。
3. 评估：
   - expansion yield
   - false expansion rate
   - evidence recall
   - full chain recall
   - token cost

当前最值得保留的实验目标：

- 在 MuSiQue 上优先证明 hyperedge expansion 能提升 chain recall。
- 在 HotpotQA 上控制 false expansion，避免过度扩展。
