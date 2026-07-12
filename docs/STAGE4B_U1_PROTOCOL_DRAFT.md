# Stage4B-U1 无标签边界不确定性控制器协议草案

> Status: `RETURN_FOR_PROTOCOL_REVISION`. This v1 draft was returned by `docs/STAGE4B_U1_PROTOCOL_REVIEW_1.md` and is superseded for design work by `docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md`. It does not authorize execution.

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Mode: plan
- Draft date: 2026-07-12
- Protocol Status: `DRAFT_AWAITING_USER_APPROVAL`
- Reservation metrics status: `PROHIBITED_NOT_ACCESSED`
- Other conversations, thread tools, and global memory used: No

## 治理纠偏

Stage4A-R2 已验证得到 94 个 q25 gain 和 69 个 q25 harm。这些 Gold 派生事件只允许用于可行性、功效规划和冻结策略后的评估，不得用于模型拟合、特征筛选、权重学习、阈值选择或逐查询检索决策。

因此，Stage3A 的监督式 gain/harm logistic controller 不在 Stage4B-U1 复用。Stage4B-U1 采用完全由检索几何和资源预算确定的无标签控制器。`question_type`、问题答案、supporting facts、gold unit、gain/harm、CR/ER 和任何插入 Gold 计数均不是控制器输入。

## 研究问题

在官方 April 7 版 2WikiMultiHopQA 上，一个由粒球边界不确定性与超边可执行性共同决定、且不使用 Gold 训练或选阈值的查询级控制器，能否相对 all-query q25 策略显著减少插入，同时更倾向保留 gain 而抑制 harm，并相对 dense fixed 获得有实际意义的 CR@20 提升？

## 阶段划分与数据边界

| 子阶段 | 数据 | 允许操作 | 证据等级 |
|---|---|---|---|
| Stage4B-U1-D | 已验证的 4,500 条 development | 仅用无标签特征构造经验分布和冻结阈值；冻结后才连接 Gold 评估 | 回顾性内部开发 |
| Stage4B-U1-R | 官方 `[5300:9800)` 的 4,500 条 reservation | 仅在 U1-D 通过、策略工件已提交并由用户再次批准后执行一次 | 独立确认性验证 |

Stage4B-U1-D 与 reservation 的 ID digest 必须继续匹配 `docs/STAGE4A_R2_SOURCE_AUDIT.json`。Stage3B 保持 `KEEP_LOCKED`。本草案未授权任何 reservation 内容提取、embedding、检索或指标读取。

## 冻结检索基础

- Encoder: `sentence-transformers/all-MiniLM-L6-v2`
- Maximum sequence length: 192
- 粒球构造、facet hyperedge 和候选打分参数：与 Stage4A-R2 完全相同
- q25 score floor: `0.1957079917192459`，仅作为冻结迁移策略，不声称对 2Wiki 最优
- Dense protected prefix: Top-10
- Maximum inserted units: 4
- Evaluation depth: 20

## Gold 隔离实现要求

控制器构造必须先生成不含下列字段的 `decision_view`：`is_gold`、`gold_unit_ids`、`supporting_facts`、`answer`、`question_type`、`num_gold_units`、所有 ER/CR、gain/harm 和 Gold 插入计数。

控制器完成逐查询决策并写出不可变 ranking/decision digest 后，评估器才可单独连接 Gold。独立验证器必须确认：

1. 控制器函数的输入 schema 不含 Gold 字段；
2. 策略工件只含无标签分布、变换、阈值、参数和 digest；
3. Gold 连接发生在决策和排名冻结之后；
4. reservation 在 U1-D 阶段仍只有 ID digest。

## 控制器定义

### 可执行门

只有同时满足以下条件的查询才是 feasible：

1. `selected_edge_count > 0`；
2. q25 过滤后至少存在一个不在 dense Top-10 中的可插入候选，即 `insertable_q25_count > 0`。

其余查询强制不扩展。两个条件均在 Gold 连接前计算。

### 四个无标签输入

1. `ball_score_margin`：第一与第二粒球相似度差；越小表示竞争越强。
2. `boundary_margin = abs(top_ball_radius - query_to_top_ball_distance) / top_ball_radius`：越小表示越接近当前粒球边界。
3. `log1p(selected_edge_count)`：可用高阶关系数量。
4. `log1p(insertable_q25_count)`：冻结 q25 下可执行的插入候选数量。

特征集来自索引机制定义，不按 Stage4A-R2 的 gain/harm 关联筛选。`query_to_top_ball_distance` 不单独加入，因为它与 `top_ball_score` 确定性互补；`boundary_margin` 已显式包含 radius 与 distance 的相对关系。

### 无标签标度与分数

在 U1-D 的 feasible queries 上，仅由四个无标签特征分别建立经验累积分布函数 `F_dev`：

```text
u_margin    = 1 - F_dev(ball_score_margin)
u_boundary  = 1 - F_dev(boundary_margin)
r_edge      = F_dev(log1p(selected_edge_count))
r_candidate = F_dev(log1p(insertable_q25_count))

uncertainty = (u_margin + u_boundary) / 2
readiness   = sqrt(r_edge * r_candidate)
score       = uncertainty * readiness
```

经验分布中的相同值采用 mid-rank。所有排序 tie 以 `SHA256("stage4b_u1_v1::<query_id>")` 升序确定，不能使用原始行号、问题类型或 Gold。

### 资源预算阈值

阈值固定为 U1-D feasible-query `score` 的中位数。这样做的唯一目的，是在可执行查询中预先规定约 50% 的扩展预算；该分位数不根据 CR、ER、gain、harm、false insert 或任何 Gold 指标调整，也不声称最优。

数值阈值、四个经验分布、tie 规则、输入 digest 和实现 commit 必须写入 `results/stage4b_u1_policy.json` 并在任何 U1-D Gold 评估前独立验证、提交、推送。

U1-R 必须逐字节复用 U1-D 策略工件中的经验分布和数值阈值；禁止在 reservation 上重新拟合经验分布、重新计算中位数、调整资源预算或更改 tie 规则。

## U1-D 冻结后评估

比较三种策略：

1. `dense_fixed`
2. `allquery_q25_p10_i4`
3. `stage4b_u1_boundary_uncertainty_q25_p10_i4`

主要机制量：

- gain retention：U1 触发的 q25 gain / all-query q25 gain
- harm retention：U1 触发的 q25 harm / all-query q25 harm
- retention gap：gain retention - harm retention
- 一侧 Fisher exact test：U1 对 gain 的保留率是否高于对 harm 的保留率

检索与成本量：CR@20、ER@20、相对 dense/q25 的 paired delta、插入查询率、插入单元/查询、conditional false-insert rate、completion precision。问题类型只作描述性审计，不参与策略或 gate。

U1-D bootstrap 使用 10,000 次 query-level paired resamples，seed `20260712`。由于 U1-D 结果已在 Stage4A-R2 中以其他策略形式被观察过，所有 U1-D 估计均标记为回顾性内部开发，不能作为独立确认性证据。

## U1-D 晋级门

只有全部满足时，才可提交 U1-D 结果并请求用户批准 U1-R：

1. U1 插入单元/查询相对 all-query q25 至少减少 40%；
2. gain retention - harm retention 至少为 `+0.15`；
3. 一侧 Fisher exact `p < 0.05`；
4. U1 相对 dense fixed 的 CR@20 delta 至少为 `+0.005`；
5. U1 相对 all-query q25 的 CR@20 delta 不低于 `-0.005`；
6. U1 conditional false-insert rate 不高于 all-query q25 超过 `0.01`；
7. 策略构造、评估、独立验证和确定性复跑均通过，且没有 Gold 泄漏。

任一门失败即 `STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED`。不得在同一 4,500 条上改权重、换特征、改分位数或搜索新阈值后重跑。

## U1-R 预声明确认性终点

U1-R 需在策略工件冻结后另行获得用户批准。Family-wise alpha 为 `0.05`，两个共同主要检验各用 `0.025`：

1. 机制终点：一侧 Fisher exact，gain retention > harm retention，且 retention gap 至少 `+0.15`；
2. 检索终点：U1 对 dense fixed 的两侧 exact McNemar，且 CR@20 delta 至少 `+0.005`。

资源硬门：插入单元/查询相对 all-query q25 至少减少 40%。只有两个主要检验、两个实际效应门和资源硬门同时通过，U1-R 才记为 `CONFIRMED`。U1 相对 q25 的非劣效、ER@20、false insert、completion precision 和类型分层均为次要或描述性结果，不能替代主要终点。

功效情景由 `scripts/stage4b_u1_plan_power.py` 生成到 `docs/STAGE4B_U1_POWER_PLAN.json`。94/69 仅是来自 U1-D 的条件规划锚点，不是 reservation 的假定结果。

## 执行顺序与停止规则

1. 用户批准本协议；
2. 将冻结协议、U1 构造代码、评估代码和独立验证代码提交并推送；
3. 仅运行 U1-D 无标签策略构造与验证；
4. 提交并推送 `stage4b_u1_policy.json`；
5. 运行一次 U1-D Gold 评估、独立复算和确定性复跑；
6. 提交结果并检查晋级门；
7. 只有晋级且用户再次批准，才允许创建 reservation 内容、embedding 和一次性指标。

硬失败包括：digest 不符、输入数量异常、Gold 字段进入 decision view、公式/分位数漂移、U1-D/reservation 重叠、提前生成 reservation 内容、embedding mismatch、非确定性输出、验证失败或非零退出码。硬失败后必须停止并形成 Amendment，批准和提交前不得重跑。

## 本草案尚未授权的操作

- 不训练监督 controller；
- 不读取 reservation 内容或指标；
- 不访问 Stage3B；
- 不执行 U1-D 特征提取、阈值校准或 Gold 评估；
- 不把 Stage4A-R2 的 94/69 用于策略构造。
