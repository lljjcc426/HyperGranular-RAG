# HyperGranular-RAG 消融与强基线计划（非执行性）

状态：`DESIGN_ONLY_NO_NEW_DATA_OR_GOLD_OPENED`
日期：2026-07-23

本文仅整理投稿前证据缺口、实验依赖和优先级，不授权执行、不读取新 Gold，也不改变 Stage4G-GTR 的联合判定。

## 1. 目标

现有 Stage4E/Stage4F 证据回答“冻结 static-q25 相对冻结 Dense 是否改善 Qwen 下的 closed-candidate answer quality”；Stage4G 在一个额外 Gemma mobile-QAT 配置下得到 `GENERATOR_TRANSFER_INCONCLUSIVE`。后续消融需把整体效果拆成可解释组件；强基线需判断增益是否仍能超越更强的传统/稠密/混合检索器。两类问题不得混入或事后改写 Stage4G 的单因素 generator-transfer 结果。

## 2. 组件消融

| 组件 | 最小对照 | 主要读数 | 可否复用现有 rankings | 风险/边界 | 优先级 |
|---|---|---|---|---|---|
| protected insertion | 保持候选与 score，仅取消 Dense Top-10 保护 | answer F1/EM；CR/ER；displacement harm | 否；最终顺序改变 | 需要新 ranking 与新阶段卡 | P0 |
| 粒球结构 | 以单 unit 或固定窗口替代粒球聚合，其余不变 | 候选覆盖、冗余、answer F1/EM | 否；候选与 score 改变 | 不得在当前 Gold 上调粒度 | P0 |
| facet-hyperedge | 移除 facet edge，只保留球内/普通超边 | 新证据覆盖、跨文档桥接、answer F1 | 否 | 需要重新候选生成 | P1 |
| q25 floor | 固定多个事前 floor 或无 floor | 效果—成本曲线、插入率、F1 | 否 | 多参数比较须独立 development 设计 | P1 |
| protected Dense prefix | 事前固定 prefix 0/5/10/15 | displacement 与 evidence gain | 否 | 与 insertion budget 有交互，需限制主要比较 | P0 |
| insertion budget | 事前固定 0/1/2/4/8 | F1/EM、CR/ER、tokens、latency | 部分：budget≤4 或可由完整候选 trace 重构时可复用；否则否 | 先确认现有 trace 是否含完整有序候选 | P0 |

## 3. 强基线

| 基线 | 最小实现 | 可否复用现有数据边界 | 可否复用现有 rankings | 说明 | 优先级 |
|---|---|---|---|---|---|
| BM25 | 相同 candidate units 上词法 Top-20 | 可复用 blind/Gold 分离边界 | 否 | 需冻结 tokenizer、参数和 tie-break | P0 |
| Dense + BM25 hybrid | 事前固定归一化与融合权重 | 可复用边界 | 否 | 权重必须在独立 development 冻结 | P0 |
| stronger dense retriever | 单一事前选定 encoder、相同 Top-20 | 可复用边界 | 否 | 模型选择不能看正式 Gold | P0 |
| cross-encoder reranking | 冻结候选池上 Top-N rerank | 可复用边界 | 否 | 需报告额外延迟/显存 | P1 |
| graph/non-HGRAG expansion | 等预算的相邻/共现扩展 | 可复用边界 | 否 | 预算与 protected prefix 必须对齐 | P1 |

## 4. 可复用资产与必须新建的资产

可直接复用而不改变语义：

- Stage4E/Stage4F 的 blind query 与 candidate-unit 内容；
- query IDs、数据集边界、Gold 隔离方法和官方答案 evaluator；
- 固定 Qwen 与 Stage4G 第二生成器的 prompt/decode 合同（若新阶段明确选择复用）；
- 现有 Dense/static-q25 rankings 作为历史基线输入；
- 已冻结的 answer/query audit 用于描述既有效果，不用于选择新参数。

必须建立新科研阶段或新数据边界：

- 任何会改变 candidate generation、encoder、ranking、protected prefix、floor 或 budget 的消融；
- BM25/hybrid/stronger dense/cross-encoder 的参数选择；
- 在同一正式 Gold 上比较多个配置后选优；
- full-wiki/open-domain、Reservation、Stage3B 或新 benchmark；
- 任何用于确认 subgroup、controller 或动态预算的实验。

## 5. 投稿前证据缺口优先级

1. `P0`：protected insertion、protected prefix 与 insertion budget 的独立贡献及效果—成本曲线；
2. `P0`：BM25、事前冻结 hybrid 和一个更强 dense retriever；
3. `P0`：至少一个不与现有两个数据集重合的新测试边界，或明确限定论文为双数据集 closed-candidate 研究；
4. `P1`：粒球结构与 facet-hyperedge 的独立消融；
5. `P1`：加入延迟、显存、prompt tokens 和索引成本的统一资源表；
6. `P2`：更细 subgroup 与机制分析，仅在样本量和多重比较控制足够时进入主文。

## 6. 解释纪律

- 消融回答组件贡献，不自动建立因果机制；
- 强基线失败或成功均不得改写已冻结 Stage4E/Stage4F/Stage4G 结果；
- 同一正式 Gold 不得同时承担参数选择和确认；
- generator、retriever、数据集、prompt 与开放域边界每次只改变实验卡允许的因素；
- Reservation、Stage3B、U2 和 controller 保持锁定，除非新的阶段级科学授权明确开放。
