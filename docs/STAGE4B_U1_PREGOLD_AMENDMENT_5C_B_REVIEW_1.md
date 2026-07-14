# Stage4B-U1-D Pre-Gold Amendment 5C-B Review 1

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Review date: 2026-07-14
- Reviewed final commit: `e5f28f664449c02b12a129aaa2a011bad84dab91`
- Approval governance commit: `fce67da87d155b1026cbe0670f606201ede0ac4b`
- Rebinding/governance commit: `b09668f47cd31df2be73446cadacf84d996418f9`
- Review decision: `ACCEPT_AMENDMENT_5C_B_REFERENCE_SCHEMA_DIAGNOSTIC`
- Other project conversations, thread tools, and global memory used: No

## 审核结论

```text
ACCEPT_AMENDMENT_5C_B_REFERENCE_SCHEMA_DIAGNOSTIC

HARD_FAILURE_5_DIRECT_CAUSE_CONFIRMED
HARD_FAILURE_4_DIAGNOSIS_STILL_INCOMPLETE

COMPARATOR_CHANGE_NOT_APPROVED
OFFICIAL_CAPTURE_RETRY_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

5C-B 的批准治理、两轮 131 项 post-approval rebinding、governance binding、唯一一次 SHA-only preflight、唯一一次 exact-command schema scan、独立 value-free 验证和最终 GitHub 同步顺序完整闭合。Machine inventory 的 source SHA 前后均为冻结值，exclusive-create 与 staging cleanup 门通过；没有修改 comparator/capture/controller、normalization 或 raw byte-equivalence，也没有生成五项正式输出或访问其他 official 输入、Gold、reservation、Stage3B。

## Hard Failure 5 直接原因

Reference decisions 的 4,500 行由两个 schema 构成：主 schema 2,446 行，nullable schema 2,054 行。两者字段集合、字段顺序和嵌套结构相同，只有八个字段的 JSON 类型不同：

```text
$/ordered_rank: integer <-> null
$/r_candidate: finite_number <-> null
$/r_edge: finite_number <-> null
$/readiness: finite_number <-> null
$/score: finite_number <-> null
$/u_boundary: finite_number <-> null
$/u_margin: finite_number <-> null
$/uncertainty: finite_number <-> null
```

当前 comparator 在 `scripts/stage4b_u1_compare_decisions.py` 的加载阶段先冻结第一行的 `file_schema`，并在后续 row schema 不同即抛出 `Incomparable heterogeneous decisions schema`。Nullable schema 首次出现于第 2 行，与 Hard Failure 5 的 line-2 错误精确对应。

因此确认：Hard Failure 5 是 comparator 的文件级同构假设与 reference decisions 中合法 nullable 行结构不兼容造成的，不是文件损坏、字段缺失、字段顺序变化或嵌套结构变化。

## Hard Failure 4 证据边界

5C-B 没有生成新的 v2.3.1 temporary decisions，也没有比较 v2.2 与 v2.3.1 decisions。以下差异类型仍未分类：

- 原始序列化或终止换行差异；
- query 行顺序或集合差异；
- `null` 与数值类型差异；
- 数值绝对误差或 binary64 ULP 差异；
- 离散字段差异；
- `planned_insert_count`、`ordered_rank`、`trigger_u1` 语义差异。

因此 5C-B 不能证明两版 decisions 语义等价，不能放宽 byte-equivalence，不能恢复 controller、verifier 或 Gold。

## 代码边界核查

当前阻塞点位于全文件加载阶段：`file_schema` 初始化约在 comparator 第 170 行，不同 row schema 的拒绝约在第 185 行。

逐 query 的比较逻辑已经存在并保持独立：

- schema type/structure 比较约在第 235 行；
- semantic fields 比较约在第 243 行；
- finite float/absolute error/ULP 分支约在第 245 行；
- 非同型或离散值计数约在第 266 行；
- 聚合 schema difference 输出约在第 315 行。

这支持将 5D-A 限定为移除全文件同构前置拒绝，而不改写逐 query 比较算法。

## 下一治理门

下一步拆分为：

1. Amendment 5D-A：heterogeneous-schema comparator 实现与 synthetic 验证；
2. Amendment 5D-B：在 5D-A 完成并独立批准后，单次 official decisions-only diagnostic。

本审核本身不授权 5D-A 实现、任何 official 文件读取、capture/controller/verifier/evaluator、normalization、byte-equivalence 放宽、Gold、reservation 或 Stage3B。

