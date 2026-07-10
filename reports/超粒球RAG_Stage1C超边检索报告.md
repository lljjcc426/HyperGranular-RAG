# 超粒球 RAG Stage 1C 超边检索报告

## Material Passport

- 项目方向：自适应粒球作为知识单元 + 边界不确定性驱动检索决策
- 当前阶段：Stage 1C Hyperedge-aware Retrieval-only MVP
- 日期：2026-07-08
- 数据：HotpotQA sample200 + MuSiQue sample200
- 检索空间：每个问题的候选 context units
- 向量空间：纯 Python TF-IDF
- Gold labels 是否用于索引：否
- 生成模型：未使用

## 1. 本轮做了什么

本轮在 Stage 1 粒球 baseline 上加入无监督超边扩展。

超边构建信号：

1. title token overlap
2. granular-ball center keyword overlap
3. ball-center similarity

检索策略：

1. 先构建每个问题候选 evidence units 的自适应粒球。
2. 根据 query 与球心相似度选择 seed balls。
3. 若 query 处于边界/低置信/球选择不确定状态，则沿超边扩展相邻 balls。
4. 在 seed + expanded balls 内重新按 query-unit 相似度排序。

注意：当前仍是 per-query candidate retrieval，不是 full-corpus index。

## 2. 对照基线

Fixed unit TF-IDF baseline：

| Dataset | ER@5 | CR@5 | ER@10 | CR@10 |
|---|---:|---:|---:|---:|
| HotpotQA | 0.4838 | 0.1700 | 0.6498 | 0.3300 |
| MuSiQue | 0.4825 | 0.1600 | 0.5875 | 0.2950 |
| ALL | 0.4832 | 0.1650 | 0.6187 | 0.3125 |

此前最佳 boundary fallback：

| Dataset | ER@5 | CR@5 | ER@10 | CR@10 |
|---|---:|---:|---:|---:|
| ALL | 0.4755 | 0.1600 | 0.6193 | 0.3200 |

## 3. 主超边配置结果

主配置：

- seed_balls = 1
- expansion_hops = 1
- title_overlap_min = 1
- keyword_overlap_min = 2
- center_similarity_min = 0.30
- decision_boundary_margin = 0.50
- decision_score_margin = 0.10
- decision_min_ball_score = 0.20

结果：

| Dataset | Hyperedge Rate | Avg Edges | Expansion Yield | False Expansion | ER@5 | CR@5 | ER@10 | CR@10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| HotpotQA | 0.885 | 47.29 | 0.0517 | 0.9483 | 0.4513 | 0.1450 | 0.6103 | 0.2900 |
| MuSiQue | 0.770 | 5.71 | 0.1124 | 0.8876 | 0.4525 | 0.1700 | 0.5950 | 0.3450 |
| ALL | 0.8275 | 26.50 | 0.0638 | 0.9362 | 0.4519 | 0.1575 | 0.6026 | 0.3175 |

判断：

- 主配置整体 CR@10 = 0.3175，略高于 fixed TF-IDF 的 0.3125。
- MuSiQue CR@10 = 0.3450，高于 fixed 的 0.2950。
- HotpotQA 明显没有获益。
- false expansion rate 很高，说明超边过密，扩展噪声大。

## 4. 参数扫描

### 4.1 保留 title overlap 的扫描

| Config | Hyperedge Rate | Avg Edges | Yield | False | ER@5 | CR@5 | ER@10 | CR@10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| he_kw3_sim030_seed1 | 0.812 | 25.64 | 0.0636 | 0.9364 | 0.4521 | 0.1575 | 0.6053 | 0.3200 |
| he_kw3_sim045_seed1 | 0.802 | 25.12 | 0.0633 | 0.9367 | 0.4488 | 0.1550 | 0.6091 | 0.3275 |
| he_kw4_sim045_seed1 | 0.782 | 24.75 | 0.0628 | 0.9372 | 0.4538 | 0.1575 | 0.6070 | 0.3275 |
| he_kw3_sim030_seed2 | 0.800 | 25.64 | 0.0549 | 0.9451 | 0.4630 | 0.1575 | 0.6316 | 0.3550 |
| he_kw4_sim045_seed2 | 0.760 | 24.75 | 0.0544 | 0.9456 | 0.4668 | 0.1650 | 0.6410 | 0.3700 |

最佳整体配置：`he_kw4_sim045_seed2`

| Dataset | ER@5 | CR@5 | ER@10 | CR@10 |
|---|---:|---:|---:|---:|
| HotpotQA | 0.4561 | 0.1500 | 0.6319 | 0.3250 |
| MuSiQue | 0.4775 | 0.1800 | 0.6500 | 0.4150 |
| ALL | 0.4668 | 0.1650 | 0.6410 | 0.3700 |

相对 fixed TF-IDF：

- ALL ER@10：0.6410 vs 0.6187，提升 +0.0223。
- ALL CR@10：0.3700 vs 0.3125，提升 +0.0575。
- MuSiQue CR@10：0.4150 vs 0.2950，提升 +0.1200。
- HotpotQA ER@10/CR@10 仍略低于 fixed。

### 4.2 禁用 title overlap 的扫描

| Config | Hyperedge Rate | Avg Edges | Yield | False | ER@5 | CR@5 | ER@10 | CR@10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| he_notitle_kw2_sim030_seed1 | 0.703 | 6.53 | 0.0643 | 0.9357 | 0.4012 | 0.1325 | 0.5348 | 0.2625 |
| he_notitle_kw3_sim030_seed1 | 0.598 | 4.38 | 0.0654 | 0.9346 | 0.4022 | 0.1375 | 0.5409 | 0.2725 |
| he_notitle_kw3_sim045_seed1 | 0.425 | 2.15 | 0.0705 | 0.9295 | 0.3952 | 0.1425 | 0.5617 | 0.3025 |
| he_notitle_kw3_sim045_seed2 | 0.458 | 2.15 | 0.0557 | 0.9443 | 0.4069 | 0.1450 | 0.5550 | 0.2875 |
| he_notitle_kw4_sim045_seed2 | 0.315 | 1.20 | 0.0563 | 0.9437 | 0.4057 | 0.1475 | 0.5644 | 0.3000 |

判断：

- 禁用 title overlap 后，超边数量减少，但检索指标明显下降。
- 当前 MVP 中，title overlap 虽然带来噪声，但确实贡献了可用连接。
- 后续不能简单移除 title overlap，而应给 title overlap 加权或与 query-aware 条件组合。

## 5. 实验结论

当前证据支持：

1. 超边扩展对 MuSiQue 更有效，尤其能提升 full chain recall。
2. `seed_balls=2` 明显优于 `seed_balls=1`，说明多跳问题常需要从多个语义区域同时启动检索。
3. 只用粒球不够，超边扩展确实提供了额外证据链补全能力。

当前证据不支持：

1. 超边策略已经全面优于 fixed TF-IDF。
2. 当前超边构建足够干净。
3. HotpotQA 上已经形成稳定优势。

最重要的实证发现：

- 在 ALL 上，最佳超边配置把 CR@10 从 0.3125 提升到 0.3700。
- 在 MuSiQue 上，最佳超边配置把 CR@10 从 0.2950 提升到 0.4150。
- 这和研究假设一致：超边更适合 connected reasoning 数据集。

## 6. 风险

主要风险是 false expansion rate 高：

- 最佳配置 expansion yield = 0.0544。
- false expansion rate = 0.9456。

这说明扩展单元中大多数不是 gold evidence。虽然 Top-10 chain recall 提升了，但代价是搜索空间中引入大量噪声。论文中不能只报 recall，必须同时报告 expansion yield 和 false expansion rate。

## 7. 下一步

进入 Stage 1D：Query-aware Hyperedge Scoring。

最小改进：

1. 超边打分从静态 overlap 改为 query-aware：
   - edge_score = ball_score + overlap_score + query-edge keyword match
2. 扩展不再扩展所有邻居：
   - 只扩展 top-m hyperedges。
3. 加入 expansion budget：
   - 限制 expanded balls 数量。
   - 限制 expanded units token budget。
4. 保留三类消融：
   - fixed unit TF-IDF
   - granular ball only
   - hyperedge expansion
   - query-aware hyperedge expansion

下一阶段目标：

- 保持 MuSiQue CR@10 提升。
- 把 false expansion rate 降下来。
- 尝试让 ER@5/CR@5 不低于 fixed baseline。

