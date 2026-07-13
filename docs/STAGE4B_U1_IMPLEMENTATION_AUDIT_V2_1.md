# Stage4B-U1-D v2.1 执行硬化审计

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit mode: implementation validation
- Audit date: 2026-07-13
- Trigger review: `docs/STAGE4B_U1_EXECUTION_PACKAGE_REVIEW_1.md`
- Frozen hardening specification: `docs/STAGE4B_U1_EXECUTION_HARDENING_V2_1.md`
- Protocol architecture: `ACCEPTED_IN_PRINCIPLE`
- Checkpoint status: `V2_1_SYNTHETICALLY_HARDENED_AWAITING_REAPPROVAL`
- Official U1-D execution approval: `NOT_APPROVED`
- Reservation and Stage3B: `KEEP_LOCKED`
- Other project conversations or global memory used: No

## 审批问题闭环

| 阻断问题 | v2.1 实现 | 合成失败注入 |
|---|---|---|
| Official development 边界可绕过 | formal preparer/controller 必须绑定冻结 source-audit SHA、4,500 queries 和 development digest | 缺失 source audit、错误 digest 均拒绝 |
| Encoder/max length 可改写 | formal 模式固定 MiniLM、192、batch 64、development | 错误 model 与 max length 均拒绝 |
| Verifier 信任 score/tie hash | verifier 独立实现 tie hash、midrank ECDF、score、rank、cutoff 和预算复算 | tie hash、score、ECDF 篡改均拒绝 |
| Insert ID 与 ranking 脱钩 | verifier/evaluator 从 q25 Top-20 结构重新推导 q25/final inserts | q25/final 同步篡改与 inserted-list 单独篡改均拒绝 |
| Policy 只绑定 controller | policy 绑定 Git commit、协议、5 个实现文件、无标签输入、channel audit、embedding 和 source audit | 任一实现 hash 不匹配即拒绝 |
| Gold 可在 pre-Gold 验证前连接 | evaluator 强制 `--pre-gold-verification`，要求 `VERIFIED_PRE_GOLD`、`evaluation=null` 和四类工件 hash | 省略 pre-Gold 工件即拒绝 |
| Official rewrite 无基线硬门 | evaluator 在 U1 汇总前核验 Stage4A-R2 dense/q25 ER/CR 及 94/69 | 基线漂移触发 `HARD_FAILURE_IMPLEMENTATION_DRIFT`，不写 summary |

v2 的 score 公式、四个特征、ECDF 定义、tie salt、q25 阈值、60% planned-insert 前缀、on/off ranking 和统计晋级门均未改变。

## 合成验证

正确命令：

```powershell
& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" `
  scripts\stage4b_u1_run_synthetic_verification.py
```

结果：

- Runtime: Python 3.12.0。
- Tests: 20 run, 0 failures, 0 errors, 0 skipped。
- 审批要求的 11 类失败注入：全部被拒绝。
- 额外 Stage4A-R2 baseline drift 注入：在 query audit/summary 写出前硬失败。
- 两次完整 runner 输出 SHA-256 均为 `799E2AE73F24C223FA28AB104AF5C830F2E4D7678795B5CB5C8F51DC32D39AC3`。
- 证据文件：`results/stage4b_u1_synthetic_verification.json`。
- 所有 synthetic channel、Gold map、embedding、decision、ranking、policy、pre-Gold 和 evaluation 工件只存在于 OS 临时目录，测试结束后清除。

首次 Python 3.12 手工验证命令：

```text
python -m unittest tests.test_stage4b_u1_goldfree -v
```

该命令因 `tests` 目录没有 `__init__.py` 而在发现测试前失败，未执行任何测试。随后改用 `unittest discover` 成功；没有修改测试、阈值或停止规则。

## 代码边界

1. Channel preparer 是唯一接收 labeled units/queries 的进程；controller audit 不记录 Gold-map 或 labeled-source hash。
2. Formal controller 只对 source audit 做字节 SHA 核验，不解析其中的 Gold/类型字段。
3. Controller CLI 没有 Gold-map 参数，也不导入 evaluator 或 channel preparer。
4. Formal policy 只能在协议与绑定实现文件和当前 Git commit 一致时生成。
5. Formal pre-Gold verifier 要求 channel audit、decisions、rankings 和 policy 已在仓库 commit 中冻结。
6. Formal evaluator 要求 pre-Gold 工件本身已提交，并记录 evaluator source hash。

## 文件操作说明

- 新增审批记录、v2.1 硬化规格和本审计文件。
- 修改 Stage4B-U1 common、channel preparer、retrieval allocation、controller、verifier、evaluator、synthetic runner 和测试。
- `stage4b_u1_verify.py` 与 `test_stage4b_u1_goldfree.py` 在原路径整体重写，Git 最终状态为文件修改，不是删除。
- 未修改 Stage4A-R2 结果、Stage3B 文件、reservation 内容或旧阶段检索脚本。
- 未删除任何仓库文件。

## 证据边界

- 20 项测试证明的是执行包对已知绕过与篡改的防护，不证明 U1 在官方 development 上有效。
- 本轮没有运行官方 U1-D channel、embedding、controller allocation 或 Gold evaluation。
- 本轮测试没有加载官方 development 内容、Stage4A-R2 source audit 内容、reservation 内容或 Stage3B。
- 尚不存在官方 U1 score、cutoff、trigger、retention、CR/ER 或 false-insert 结果。
- 下一门只能是用户重新审批 v2.1 execution package；通过本 checkpoint 不自动授权官方执行。
