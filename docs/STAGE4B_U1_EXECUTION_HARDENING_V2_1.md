# Stage4B-U1-D 执行硬化规格 v2.1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Mode: implementation validation plan
- Parent architecture: `docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md`
- Trigger review: `docs/STAGE4B_U1_EXECUTION_PACKAGE_REVIEW_1.md`
- Specification status: `FROZEN_BEFORE_V2_1_SYNTHETIC_TEST_RUN`
- Official data execution: `PROHIBITED`
- Gold evaluation: `PROHIBITED`
- Reservation and Stage3B: `KEEP_LOCKED`
- Other project conversations or global memory used: No

## 目标

不改变 v2 的研究问题、score 公式、ECDF 定义、0.60 预算比例、q25 阈值或统计晋级门，只修复执行完整性。所有验证使用测试文件中的合成 fixture 和临时目录；不得读取官方 development 内容、reservation 内容或 Stage3B 数据。

## 冻结正式边界

- 数据角色：当前正式 controller 仅允许 `development`。
- development queries：4,500。
- development query digest：从已验证 `docs/STAGE4A_R2_SOURCE_AUDIT.json` 的 `data_boundary.development_query_id_sha256` 读取。
- source-audit SHA-256：`1496FF0CE08093AD38258FD5049068D6C4ED74FCEBF63E94E6E486F3478C7AEE`。
- encoder：`sentence-transformers/all-MiniLM-L6-v2`。
- max length：192。
- embedding batch size：64；本 checkpoint 将其冻结以消除正式复现命令的自由度。
- retrieval configuration：`RetrievalConfig()` 的全部字段，保持 v2 不变。

只有显式 `--synthetic-test-mode` 可以跳过官方 query 数量和 source-audit 边界；synthetic policy 永远不得进入正式 evaluator。

## Verifier 独立复算

Verifier 以 decision 的原始无标签量和 policy ECDF reference 为输入，独立实现 midrank ECDF 与 score 复算，不信任 decision 中提供的派生值。逐 query 核验：

`tie_hash`、`u_margin`、`u_boundary`、`r_edge`、`r_candidate`、`uncertainty`、`readiness`、`score`、`ordered_rank` 和 `trigger_u1`。

批量核验：ECDF reference、预算定义、largest-prefix、cutoff score/hash、frozen retrieval config、完整实现 hash 和输入 hash。

## Ranking 与插入推导

每个正式/合成 ranking 均必须满足：

1. dense Top-20 与 q25 Top-20 长度均为 20，ID 各自唯一；
2. `q25_top20[:10] == dense_top20[:10]`；
3. `q25_inserted_unit_ids == q25_top20[10:10 + planned_insert_count]`；
4. 插入 ID 不得出现在 dense Top-10；
5. final Top-20 由 trigger 在 dense/q25 之间唯一选择；
6. final inserted IDs 由 trigger 和 q25 Top-20 结构重新推导。

Evaluator 使用同一结构检查后自行推导插入 ID，不把 controller 的 inserted-ID 字段作为事实来源。

## Policy 与 pre-Gold 冻结

Formal policy 必须记录：

- `git_commit_sha`；
- `protocol_sha256`；
- common、retrieval、controller、channel preparer、verifier source SHA-256；
- unlabeled units、unlabeled queries、channel audit、embedding cache、source audit SHA-256；
- model name、max length、batch size及完整 retrieval config。

正式 pre-Gold verifier 只能在 decisions、rankings、policy 和 channel audit 已提交后运行，并记录包含这些工件的 `frozen_commit_sha`。Evaluator 必须接收已提交且状态为 `VERIFIED_PRE_GOLD` 的验证工件，核验 `evaluation == null` 和全部相关 hash 后才能加载 Gold。

## Stage4A-R2 基线等价硬门

正式 evaluator 在任何 U1 汇总或晋级判定前，必须对照已验证 Stage4A-R2 工件核验：

| 指标 | 冻结值 |
|---|---:|
| dense ER@20 | 0.8982037037037036 |
| dense CR@20 | 0.7722222222222223 |
| q25 ER@20 | 0.9022703703703704 |
| q25 CR@20 | 0.7777777777777778 |
| q25 gains | 94 |
| q25 harms | 69 |

任一不匹配立即抛出 `HARD_FAILURE_IMPLEMENTATION_DRIFT`，不得生成 U1 晋级解释，不得自动重跑。

## 合成验收矩阵

除保留原有 7 项性质外，必须注入并拒绝以下 11 类故障：

1. official channel 缺失 source audit；
2. source audit 的 development digest 错误；
3. formal controller model name 错误；
4. formal controller max length 不等于 192；
5. decision tie hash 被修改且同步更新 policy output hash；
6. decision score 被修改且同步更新 policy allocation/output hash；
7. policy ECDF reference 被修改；
8. q25 ranking 被修改并同步修改 final ranking；
9. inserted-ID list 被修改而 Top-20 不变；
10. evaluator 未提供 pre-Gold verification；
11. policy 中任一实现文件 hash 不匹配。

额外测试 evaluator 的 Stage4A 基线漂移硬失败。所有测试必须在临时目录执行，不持久化合成 channel、Gold map、embedding 或 ranking。

## 停止规则

- 任一失败注入未被拒绝：checkpoint 状态为 `FAILED`，停止并记录，不得放宽检查。
- 任一原有合成等价/确定性测试回归：checkpoint 状态为 `FAILED`。
- 只有全部测试通过且独立验证工件确定性复现，才可记为 `V2_1_SYNTHETICALLY_HARDENED_AWAITING_REAPPROVAL`。
- 即使 checkpoint 通过，官方 U1-D 仍不获授权；必须重新提交用户审批。

## 合成执行结果

- Runtime: `D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe` (`Python 3.12.0`)
- Correct test entry: `python -m unittest discover -s tests -p test_stage4b_u1_goldfree.py -v`
- Result: 20 tests, 0 failures, 0 errors, 0 skipped。
- Checkpoint result: `V2_1_SYNTHETICALLY_HARDENED_AWAITING_REAPPROVAL`。
- Official development content, reservation content, Stage3B, and official U1-D metrics accessed by tests: No。
- Synthetic artifacts persisted outside the test temporary directory: No。

首次 Python 3.12 验证命令使用包路径 `python -m unittest tests.test_stage4b_u1_goldfree -v`，因 `tests` 目录没有 `__init__.py` 而在测试发现前失败；未执行测试。随后使用上述 discover 入口成功，未修改测试门槛或实验代码。
