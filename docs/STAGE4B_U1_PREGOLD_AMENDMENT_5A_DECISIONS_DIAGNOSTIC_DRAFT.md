# Stage4B-U1-D Pre-Gold Amendment 5A：Decisions 等价差异诊断工具

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Draft date: 2026-07-13
- Amendment ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_5A`
- Requested mode: implementation and synthetic verification only
- Current state: `PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_4`
- Hard Failure 4 commit: `b21852a174b537c90a848699deb4d26d6f169506`
- v2.3.1 implementation commit: `34349c70ee24b8240fd169393134d4280968b790`
- Original resumption package: `e76c921454697d1784b0d76a9d9677113051f0f6`
- Approval governance: `53850f58e57f51b3c6067ed3108edff6b99a2dfc`
- Synthetic rebinding: `a963befd812658972b156d2a7a26a488ac3c4482`
- Failed controller execution HEAD: `8e0bab13ad20c06795dffd5ca71f167a814cdfb0`
- Official diagnosis: `NOT_REQUESTED`
- Controller rerun: `NOT_REQUESTED`
- Verifier: `NOT_REQUESTED`
- Gold / reservation / Stage3B: `KEEP_LOCKED`

## 1. 触发原因与证据边界

Hard Failure 4 只证明：v2.3.1 controller 在 OS temporary directory 生成的 pending decisions 文件未通过冻结 v2.2 decisions SHA-256 等价门。pending 文件在异常退出后已删除，未提升正式 decisions、rankings 或 policy。

现有证据不能区分以下原因：

- 纯序列化或换行差异；
- JSON 字段顺序或 canonicalization 差异；
- 行数、query-ID 集合或行序差异；
- schema、字段集合或列表顺序差异；
- 浮点表示、精确值、绝对误差或 ULP 差异；
- `planned_insert_count`、`ordered_rank`、`trigger_u1` 等决策语义差异。

Amendment 5A 只实现并合成验证能够区分上述类别的 decisions-only 工具。它不得接触任何 official 输入或参考 decisions 内容。

## 2. 研究问题

在不读取 ranking、policy、Gold 或 official 数据的条件下，能否建立一个 fail-closed、确定性、只处理 decisions JSONL 的诊断工具，使未来经单独批准的 5B 能回答：

1. 两份 decisions 是否仅原始 bytes 不同而 canonical semantics 相同；
2. 首个不一致层级是文件、行/query-ID、JSON canonicalization、schema、离散字段、浮点字段还是预注册决策语义字段；
3. 浮点差异的精确值、最大绝对误差和 ULP 距离是什么；
4. 诊断是否能只输出聚合计数、hash 和受限差异分类，不泄露 question/text、Gold、ranking 或其他未授权内容。

## 3. 诊断工具边界

### 3.1 Decisions-Only Comparator

拟新增：

```text
scripts/stage4b_u1_compare_decisions.py
```

Comparator 只接受两个 decisions JSONL 路径和一个诊断 audit 输出路径。它必须按以下固定层级比较：

1. **Raw file layer**：bytes、文件大小、SHA-256、换行终止状态；
2. **Row identity layer**：非空行数、JSON 解析状态、query-ID 唯一性、query-ID 集合与顺序；
3. **Canonical JSON layer**：UTF-8、`sort_keys=True`、紧凑 separators、禁止 NaN/Infinity 的逐行 canonical bytes 与 digest；
4. **Schema layer**：字段集合、原始字段顺序、字段类型及嵌套 list/dict 结构；
5. **Discrete layer**：字符串、布尔、整数、null、ID 列表和离散列表顺序的精确差异；
6. **Float layer**：IEEE-754 binary64 精确值、绝对误差和 ULP 距离；禁止将 NaN/Infinity 当作可比较值；
7. **Decision semantics layer**：至少独立报告 `planned_insert_count`、`ordered_rank`、`trigger_u1`，并对 manifest 冻结的其他 decisions 字段执行同类型比较。

Comparator 必须 fail-closed：重复 query ID、缺少 query ID、JSON 解析失败、非有限浮点、未登记字段类型或 schema 不可比较时均返回非零，不得降级为“相同”。

### 3.2 OS-Temporary Diagnostic Capture

拟新增：

```text
scripts/stage4b_u1_capture_diagnostic_decisions.py
```

5A 只允许以 synthetic fixture 验证该入口。入口必须：

- 仅在 `tempfile.TemporaryDirectory` 内写一份 diagnostic decisions；
- 使用共享的 Gold-free decisions 计算路径，不改变 retrieval/controller 参数或排序语义；
- 不构造、不读取、不保存、不比较 rankings；
- 不调用 policy builder，不生成 policy；
- 不接受 evaluator、Gold map、reservation 或 Stage3B 参数；
- 成功和失败退出时均删除 temporary decisions；
- synthetic 模式拒绝所有 manifest 登记的 official 路径；
- official 模式默认禁用，只有 future 5B 的新批准治理和显式令牌同时存在时才可进入。

若实现共享 decisions 计算需要从现有 controller 提取纯函数，只允许机械提取，不得修改 score、ECDF、预算、trigger、q25、effective-K、ranking 或 endpoint。任何输出语义变化均视为 5A 硬失败。

## 4. 诊断输出最小化

Synthetic comparator audit 可以包含 fixture ID。Future 5B official audit 的 schema 必须预先冻结为只包含：

- 两个文件的 bytes/SHA 和行数；
- query-ID 集合/顺序是否一致及差异计数；
- canonical digest 是否一致；
- schema/字段顺序/类型差异计数；
- 每个登记字段的差异计数；
- float 字段最大绝对误差、最大 ULP 与有限值门；
- 三个语义字段的差异计数；
- 首个差异 query ID 的 salted hash，可选且不得输出原始 query ID；
- temporary cleanup、ranking-not-accessed、policy-not-generated、Gold-not-accessed 等布尔证明。

不得输出 question、text、answer、supporting facts、Gold IDs、unit ranking、raw decision rows 或未登记样本内容。

## 5. 允许的实现文件

5A 获批后只允许新增或修改：

```text
scripts/stage4b_u1_compare_decisions.py
scripts/stage4b_u1_capture_diagnostic_decisions.py
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
tests/test_stage4b_u1_decisions_diagnostic.py
scripts/stage4b_u1_goldfree_controller.py   # 仅在机械提取共享 decisions 纯函数确有必要时
AGENTS.md
README.md
docs/ROADMAP.md
docs/REPRODUCIBILITY.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_DECISIONS_DIAGNOSTIC_DRAFT.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_APPROVAL_REQUEST.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_MANIFEST.json
```

Diagnostic tool checkpoint 拟冻结为：

```text
stage4b_u1_decisions_diag_v1
```

原 controller checkpoint `stage4b_u1_v2_3_1`、retrieval 实现和全部 official 工件保持不变。

## 6. Synthetic Hardening Matrix

现有 50 项 Stage4B-U1 synthetic suite 必须完整保留。新增至少 24 项 decisions-only 测试，每个测试对应一个独立硬门：

1. 完全相同 bytes 通过；
2. 仅末尾换行不同，raw 不同但 canonical 相同；
3. 仅空白不同，raw 不同但 canonical 相同；
4. 仅 JSON 字段顺序不同，schema order 不同但 canonical 相同；
5. 行数不同；
6. query-ID 顺序不同；
7. query-ID 集合 missing/extra；
8. 重复 query ID 硬失败；
9. 缺少 query ID 硬失败；
10. 非法 JSON 硬失败；
11. schema 缺字段；
12. schema 多字段；
13. 字段类型不同；
14. 离散字符串/整数/布尔差异；
15. ID list 元素差异；
16. ID list 顺序差异；
17. float 精确相等；
18. float 值差异与最大绝对误差；
19. float ULP 距离；
20. NaN/Infinity 硬失败；
21. `planned_insert_count` 语义差异；
22. `ordered_rank` 语义差异；
23. `trigger_u1` 语义差异；
24. diagnostic capture 成功/异常清理、ranking 路径未访问、policy builder 未调用和 official 路径拒绝。

第 24 项可以拆成多个测试，但不得合并或省略任何证明。新增测试总数可以超过 24，不能少于 24。

## 7. 5A Evidence 与停止门

完整 synthetic suite 必须在最终治理与实现字节上连续运行两次：

```text
全部测试通过
0 failure
0 error
0 skip
完整 evidence 字节一致
```

预注册输出：

```text
results/stage4b_u1_d_pregold_amendment_5a_synthetic_verification.json
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_IMPLEMENTATION_AUDIT.md
```

Evidence 必须记录实现文件 hash、测试 ID、fixture 分类、official-path-denied、ranking-not-accessed、policy-not-generated、Gold-not-accessed、temporary-cleanup 和两次完整输出 SHA。

5A 实现与 synthetic evidence 提交推送后，只允许创建新的 implementation-bound Amendment 5B official decisions-only diagnostic 审批请求与 Manifest，然后立即停止。

## 8. 明确不授权

Amendment 5A 不授权：

- 读取 official units、queries、source audit、fresh/legacy cache；
- 读取、保存或比较 v2.2/v2.3.1 official decisions 内容；
- 读取或比较任何 official rankings；
- 生成 official decisions、rankings 或 policy；
- 运行 official controller、diagnostic capture、comparator、verifier 或 evaluator；
- 修改 byte-equivalence 门或把 canonical/semantic equality 替代 byte equality；
- 修改 retrieval/controller/evaluator 算法或参数；
- Gold、U1-D 效果指标、reservation、Stage3B；
- 自动重跑 Hard Failure 4 controller。

当前有效状态保持：

```text
PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_4
```
