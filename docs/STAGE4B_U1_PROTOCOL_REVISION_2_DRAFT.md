# Stage4B-U1 无标签边界不确定性资源分配协议修订草案 v2

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Mode: protocol revision
- Revision date: 2026-07-12
- Review source: `docs/STAGE4B_U1_PROTOCOL_REVIEW_1.md`
- Execution-package review: `docs/STAGE4B_U1_EXECUTION_PACKAGE_REVIEW_1.md`
- v2.1 hardening specification: `docs/STAGE4B_U1_EXECUTION_HARDENING_V2_1.md`
- Pre-Gold approval decision: `docs/STAGE4B_U1_EXECUTION_PACKAGE_V2_1_APPROVAL_DECISION.md`
- Pre-Gold hard-failure audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_1.md`
- Approved amendment: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_1_DRAFT.md`
- Amendment approval decision: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_1_APPROVAL_DECISION.md`
- Pre-Gold hard-failure audit 2: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_2.md`
- Approved amendment 2: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_2_DRAFT.md`
- Amendment 2 approval decision: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_2_APPROVAL_DECISION.md`
- Amendment 2 implementation audit: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_2_IMPLEMENTATION_AUDIT.md`
- Protocol architecture status: `FROZEN_FOR_U1_D_PREGOLD_EXECUTION`
- Execution review decision: `RETURN_EXECUTION_PACKAGE_FOR_HARDENING`
- Execution package status: `AMENDMENT_2_SYNTHETICALLY_HARDENED_AWAITING_OFFICIAL_RESUMPTION_APPROVAL`
- Historical execution approval: `APPROVE_STAGE4B_U1_D_PREGOLD_EXECUTION_V2_1`
- Current execution authorization: `NOT_APPROVED`
- Approval date: 2026-07-13
- Approval request commit: `2f6c7067c686bf1f4c13328bd1fc04ab3990f767`
- Bound implementation commit: `dd1f8a9893ccb1e760068ad21d48e0e8938cc7f9`
- Bound amendment commit: `a7e121584d9f512bb7b4abaabdb9c93913ad560d`
- Bound amendment 2 commit: `dde5a28fec476fddd0ac82ebad39d9eeab0bea1e`
- Gold evaluation approval: `NOT_APPROVED`
- Reservation metrics status: `PROHIBITED_NOT_ACCESSED`
- Other conversations, thread tools, and global memory used: No

## 研究定位

U1 是一个机制驱动、无标签、待确认的启发式批量资源分配策略，不是已有证据支持的预测模型。Stage2G 已否定旧 boundary-only OR gate；Stage2H 中 score margin 与 boundary margin 的预测信号接近随机。U1 的新信息仅来自连续不确定性、超边可执行性和硬资源预算的组合，其有效性必须重新检验。

Stage4A-R2 的 94 个 q25 gain 和 69 个 q25 harm 只允许用于条件功效规划和策略完全冻结后的评估。它们不得进入特征筛选、权重、经验分布、预算、排序、cutoff 或逐查询决策。

## 研究问题

在官方 April 7 版 2WikiMultiHopQA 上，一个严格 Gold-free 的粒球边界不确定性与超边 readiness 批量分配策略，能否在机械保证 q25 插入单元至少减少 40% 的条件下，更高比例保留 gain 而不是 harm，并相对 dense fixed 获得统计证据与预声明的观察效应？

## 数据边界与证据等级

| 子阶段 | 数据 | 允许操作 | 证据等级 |
|---|---|---|---|
| Stage4B-U1-D | 已验证的 4,500 条 development | Gold-free 策略构造；策略冻结后才允许评估 | 回顾性内部开发 |
| Stage4B-U1-R | 官方 `[5300:9800)` 的 4,500 条 reservation | U1-D 晋级、策略冻结、用户再次批准后执行一次 | 独立确认性验证 |

U1-D 与 reservation 的 ID digest 必须匹配 `docs/STAGE4A_R2_SOURCE_AUDIT.json`。Stage3B 始终保持 `KEEP_LOCKED`。本修订草案不授权 U1-D 特征提取、策略冻结、Gold 评估或任何 reservation 内容访问。

## 进程级与文件级 Gold 隔离

### 三个独立数据通道

通道准备器是唯一允许读取原始带标签 corpus 的组件，并一次性生成：

1. `stage4b_u1_unlabeled_units.jsonl`：只含 `dataset`、`query_id`、`unit_id`、`title`、`text` 及无标签定位字段；禁止 `is_gold` 和 Gold 计数。
2. `stage4b_u1_unlabeled_queries.jsonl`：只含 `dataset`、`query_id`、`sample_id`、`question` 和无标签候选计数；禁止 answer、supporting facts、type、gold IDs 和 Gold 计数。
3. `stage4b_u1_gold_map.json`：只供独立 evaluator 使用，按 `query_id` 保存 `gold_unit_ids`；`question_type` 可作为 evaluator-only 描述性分层字段。

三者均为本地未跟踪文件并记录 SHA-256。通道准备器不得生成检索指标。

通道准备器还必须写出两个彼此隔离的 manifest：

1. controller audit：只含 unlabeled units/queries 的 SHA-256、数量与 query-ID digest，不得包含 Gold-map hash 或 labeled-source hash；
2. evaluator audit：包含 Gold-map hash 与 labeled-source hash，只能由 evaluator/verifier 接收。

### Controller 进程限制

Controller 命令行只能接收 unlabeled units、unlabeled queries、无标签 embedding cache、冻结源审计和策略配置。它不得接收、查找、导入或加载 `gold_map`，也不得复用含 `is_gold`、`gold_units`、`inserted_gold_units` 的旧 candidate、ball 或 edge 对象。

必须实现新的 Gold-free candidate/ball/hyperedge 数据类型或入口。仅在旧对象末端删除 Gold 字段不合格。

Controller 只能写出：

- `stage4b_u1_decision_audit.jsonl`：无标签特征、score、planned inserts、排序位置和 trigger；
- `stage4b_u1_rankings.jsonl`：每个 query 的 dense Top-20、q25 Top-20 和 final Top-20 `unit_id`，不得含 `is_gold` 或 Gold 指标；
- `stage4b_u1_policy.json`：开发 ECDF、固定公式、预算比例、排序规则、输入与输出 digest；
- canonical byte-level ranking SHA-256。

Evaluator 只能在 ranking 文件及其 digest 已冻结、独立验证并提交后，按 `unit_id` 连接 `gold_map`。

## 冻结检索基础

- Encoder: `sentence-transformers/all-MiniLM-L6-v2`
- Embedding storage and normalization: `float32`
- Scalar feature and policy arithmetic: convert to IEEE-754 `float64`
- Maximum sequence length: 192
- 粒球、facet hyperedge 与 candidate scoring 参数：与 Stage4A-R2 相同，但对象必须 Gold-free
- q25 score floor: `0.1957079917192459`
- Dense protected prefix: Top-10
- Maximum inserted units: 4
- Evaluation depth: 20

q25 只是冻结迁移策略，不代表 2Wiki 最优阈值。

## 数值与异常规则

1. 候选单元为空或粒球列表为空：硬失败，不写策略工件。
2. 只有一个粒球：`second_score = -1.0`，与现有冻结实现一致。
3. `query_to_top_ball_distance = 1.0 - top_ball_score`。
4. `top_ball_radius > 0` 时，`boundary_margin = abs(radius - distance) / (radius + 1e-9)`。
5. `top_ball_radius == 0` 时，`boundary_margin = 999.0`。
6. 任一输入、embedding、score、radius、margin、ECDF 输出或最终 score 为 NaN/Inf：硬失败。
7. 所有计数必须为非负整数；违反时硬失败。
8. float 相等采用转换为 `float64` 后的精确数值相等，不使用容差分箱。

开发经验分布对每个特征单独冻结。对 development 参考值集合 `V`：

```text
F_dev(x) = (# {v in V: v < x} + 0.5 * # {v in V: v == x}) / |V|
```

- `x < min(V)` 时为 `0.0`；`x > max(V)` 时为 `1.0`。
- 相等判断遵循上面的精确 `float64` 规则。
- U1-R 只能使用 U1-D 冻结的参考数组，禁止用 reservation 重新拟合 ECDF。
- 参考数组为空、未排序、含 NaN/Inf 或 digest 不符均为硬失败。

## Feasible Gate 与四个输入

先生成冻结 dense Top-20 与 all-query q25 Top-20。对每条查询：

```text
insertable_q25 = q25 candidate order 中排除 dense Top-10 unit IDs 后的候选
planned_insert_count = min(4, len(insertable_q25))
feasible = selected_edge_count > 0 and planned_insert_count > 0
```

四个输入均在 Gold 连接前计算：

1. `ball_score_margin`
2. `boundary_margin`
3. `log1p(selected_edge_count)`
4. `log1p(planned_insert_count)`

特征集由机制定义固定，不根据任何 gain/harm 关联筛选。

## 冻结 Score

仅在 U1-D feasible queries 上拟合四个 `F_dev`：

```text
u_margin    = 1 - F_dev(ball_score_margin)
u_boundary  = 1 - F_dev(boundary_margin)
r_edge      = F_dev(log1p(selected_edge_count))
r_candidate = F_dev(log1p(planned_insert_count))

uncertainty = (u_margin + u_boundary) / 2
readiness   = sqrt(r_edge * r_candidate)
score       = uncertainty * readiness
```

权重、变换和乘法形式均不可根据 U1-D 或 U1-R Gold 结果修改。

## 唯一资源分配规则

U1 是有限 benchmark batch 上的资源分配器，本阶段不主张其已验证为在线逐查询 controller。

对 U1-D 和获批后的 U1-R 分别执行同一算法：

```text
allquery_planned_inserts = sum(planned_insert_count over feasible queries)
budget_fraction = 0.60
budget_units = floor(allquery_planned_inserts * budget_fraction)
tie_hash = SHA256("stage4b_u1_v2::<query_id>")
order feasible queries by (-score, tie_hash), ascending
m = largest prefix length whose cumulative planned_insert_count <= budget_units
trigger exactly the first m queries; all remaining queries do not trigger
```

不得跳过高排名高成本查询去选择更低排名查询。若 feasible 集为空、`budget_units < 1` 或不存在非空合法前缀，硬失败。

该规则唯一使用 `rank_position <= m`，不存在 `>`/`>=` 浮点阈值歧义。每个 batch 的决策工件必须保存：

- `budget_fraction = 0.60`
- `n_feasible`
- `allquery_planned_inserts`
- `budget_units`
- `selected_queries = m`
- `selected_planned_inserts`
- `cutoff_score`
- `cutoff_hash`
- `score_direction = descending`
- `selection_operator = ordered_prefix_cumulative_cost_lte_budget`

U1-R 使用 U1-D 冻结的 ECDF 和全部公式，但按同一个固定 `0.60` 规则在 reservation batch 上机械计算预算与前缀；这不是结果驱动调参。U1-R 的无标签 decision/ranking digest 必须在连接 reservation Gold 前单独冻结、验证、提交和推送。

## 最终 Ranking 的正式定义

```text
if trigger_u1:
    final_top20_unit_ids = frozen_allquery_q25_p10_i4_top20_unit_ids
else:
    final_top20_unit_ids = frozen_dense_fixed_top20_unit_ids
```

U1 只控制 on/off。它不得重新排序 q25 候选，不得改变 candidate generation、q25 floor、protect=10、insert=4 或 dense fill。Feasible 但未被前缀选中的查询必须逐字节采用 dense Top-20。

因此，U1 相对 dense 的 gain/harm 必须是 all-query q25 gain/harm 的选择性子集。Verifier 必须逐查询验证该子集关系和 Top-20 unit-ID 序列。

## U1-D 冻结后评估与晋级门

比较 `dense_fixed`、`allquery_q25_p10_i4` 与 `stage4b_u1_v2`。U1-D 只形成回顾性内部开发证据。

全部条件必须通过：

1. `selected_planned_inserts <= floor(0.60 * allquery_planned_inserts)`，且 evaluator 观测插入单元与冻结 planned count 完全一致；
2. gain retention - harm retention 至少为 `+0.15`；
3. gain retention > harm retention 的一侧 Fisher exact `p < 0.05`；
4. U1 相对 dense fixed 的观察 CR@20 delta 至少为 `+0.005`；
5. U1 相对 all-query q25 的观察 CR@20 delta 不低于 `-0.005`；
6. U1 conditional false-insert rate 不高于 all-query q25 超过 `0.01`；
7. Gold 隔离、ranking 子集、独立验证和确定性复跑全部通过。

任一失败即 `STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED`。不得在同一 development 上改特征、公式、预算比例、排序或检验后重跑。

## U1-R 单一联合确认性结论

U1-R 只检验一个联合研究结论：U1 同时具有选择性机制证据和相对 dense 的检索改善证据。采用 intersection-union testing：

1. 机制组件：一侧 Fisher exact，零假设为 gain retention 不高于 harm retention，`alpha = 0.05`；
2. 检索组件：两侧 exact McNemar，零假设为 U1 与 dense 的 CR@20 相等，`alpha = 0.05`。

只有两项都拒绝各自零假设，且同时满足以下观察实际效应门，才记为 `CONFIRMED_JOINT_CLAIM`：

- observed retention gap >= `+0.15`；
- observed CR@20 delta vs dense >= `+0.005`；
- 插入单元至少减少 40%。

正确结论语言是：“两项相对零差异均有统计证据，且观察效应达到预注册实际意义门。”不得声称 Fisher 统计确认 gap 至少 0.15，也不得声称 McNemar 统计确认 CR 提升至少 0.005。若只有一个组件通过，不形成单独确认性主张。

## Question-Type 风险审计

`question_type` 只由 evaluator 在 Gold join 后读取。必须按 bridge comparison、comparison、compositional、inference 报告查询数、gain/harm retention、CR@20 delta、插入成本与区间。

任何类型出现 CR@20 delta <= `-0.02` 或 retained harms > retained gains，标记 `SUBGROUP_CAUTION`。该标记不改变总体预注册检验，但总体成功不得解释为所有类型均有效，也不得形成类型特异性 efficacy 主张。

## 功效规划边界

`scripts/stage4b_u1_plan_power.py` 只使用固定 reservation `n=4500` 与已发布 development 94/69 作为条件事件数锚点。功效是条件情景，不是 reservation 结果预测，不参与策略构造。

## 两级批准与执行顺序

v2 原实现通过 7 项合成验证后，执行包审批仍因 7 项完整性缺口退回。v2.1 按 `docs/STAGE4B_U1_EXECUTION_HARDENING_V2_1.md` 完成 20 项合成测试，包括审批指定的 11 类失败注入和 Stage4A-R2 基线漂移硬失败。证据见 `docs/STAGE4B_U1_IMPLEMENTATION_AUDIT_V2_1.md` 与 `results/stage4b_u1_synthetic_verification.json`。用户随后批准了严格限于 pre-Gold 的执行，但正式 preflight 在旧 embedding cache 缺少 ID-bound 元数据处硬失败并停止。

1. v2 设计架构已获原则接受；
2. 原执行包已退回，并在运行新测试前冻结 v2.1 hardening specification；
3. v2.1 只用合成 fixture 完成 20 项测试，不运行官方 U1-D；
4. 将审批记录、硬化规格、实现、测试证据和状态更新提交并推送；
5. 用户重新显式批准 U1-D execution package；已完成；
6. 获批后的 preflight 命中 `HARD_FAILURE_EMBEDDING_CACHE_METADATA`，在 official channel 前停止；
7. `docs/STAGE4B_U1_PREGOLD_AMENDMENT_1_DRAFT.md` 已获批准；批准状态与新 synthetic binding evidence 提交推送后才可恢复官方 U1-D pre-Gold；
8. 策略工件先冻结、独立验证、提交并推送，之后仍须单独批准才允许一次 U1-D Gold 评估；
9. U1-D 全部门通过且用户再次批准，才允许 U1-R。

当前 `AGENTS.md` 已同步为 Amendment 1 单次恢复状态；U1-D Gold、U1-R 与 Stage3B 继续锁定。

## Pre-Gold 硬失败 1

旧 Stage4A-R2 cache 的 SHA-256 为 `746FC1130038C789190F2A37CB911BBFC46905CFCC138E361C1F6CF991A45F02`，实际 NPZ 成员只有 `model_name`、`query_embeddings` 和 `unit_embeddings`。它缺少 v2.1 必需的 `unit_ids`、`query_ids` 与 `max_length`，不能证明 embedding 行序与 official U1-D 输入一致。

该失败发生在 official channel preparation 前。未生成 channel、Gold map、decision、ranking、policy、`VERIFIED_PRE_GOLD` 或 U1-D 指标；未访问 reservation 或 Stage3B。完整记录见 `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_1.md`。

## Pre-Gold 硬失败 2

Amendment 1 批准后的 preflight 发现 source audit 的 `6B21...` digest 对应 processed `sample_id`，而 Stage4B 运行时 `query_id` 是 `dataset::sample_id`，实际 digest 为 `8895...`。现有 v2.1 在 formal preparer/controller/verifier 中错误地把两种表示直接比较。

该失败发生在 official channel preparation 和新 cache 创建前；其余 source SHA、计数、旧 cache、新路径不存在及 Git hard gates 均通过。未生成 official 工件或指标。完整记录见 `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_2.md`。

## 当前禁止事项

- Amendment 2 实现与 synthetic verification 已完成；禁止 official U1-D preflight、channel、controller、cache 或 verifier，直至新的实现提交获得批准；
- 不连接 U1-D Gold；
- 不创建或读取 reservation 内容、embedding、decision、ranking 或指标；
- 不访问 Stage3B；
- 不迁移、补写、覆盖或删除旧 embedding cache，不在 pre-Gold 硬失败后自动重跑或修改参数；
- `VERIFIED_PRE_GOLD` 提交推送后立即停止，Gold evaluation 必须另行批准。
