# Stage4B-U1-D 执行包审批记录 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review type: execution-integrity review
- Review date: 2026-07-13
- Protocol architecture decision: `ACCEPTED_IN_PRINCIPLE`
- Execution package decision: `RETURN_EXECUTION_PACKAGE_FOR_HARDENING`
- Official U1-D channel preparation: `NOT_AUTHORIZED`
- U1-D Gold evaluation: `NOT_AUTHORIZED`
- Reservation: `KEEP_LOCKED`
- Stage3B: `KEEP_LOCKED`
- Other project conversations or global memory used: No

## 审批边界

Stage4B-U1 v2 的科研架构原则上通过。Gold 进程/文件隔离、唯一 score/hash 预算前缀、60% planned-insert 成本上限（即至少 40% 机械成本削减）、异常数值规则、dense/q25 on-off ranking、IUT 语言和问题类型描述性审计不再重新设计。

当前执行包仍有阻断性完整性缺口。在这些缺口修复、仅合成失败注入通过、形成 v2.1 implementation checkpoint 并再次获得用户批准前，不得运行官方 U1-D channel，不得连接 Gold，也不得读取 reservation 或 Stage3B 指标。

## 七项阻断问题

1. 官方 development 边界未被程序强制：正式 channel preparer 必须要求 `--source-audit`、自动读取 development digest、强制 4,500 queries，并核验 source-audit 文件 SHA-256。
2. 正式 controller 可通过 CLI 改写 encoder 和 max length：非 synthetic 模式必须固定 `sentence-transformers/all-MiniLM-L6-v2`、`max_length=192`、`mode=development`；batch size 同时冻结并写入 policy。
3. verifier 仅检查内部一致：必须独立复算 tie hash、四个 ECDF、uncertainty、readiness、score、ordered rank 及 cutoff。
4. 插入成本可与 ranking 脱钩：verifier 和 evaluator 必须从 q25 Top-20 结构推导插入 ID，并检查 Top-20 长度、唯一性及 dense Top-10 保护区。
5. formal policy 未绑定完整实现：必须绑定 Git commit、协议、common、retrieval、controller、channel preparer、verifier、无标签输入、embedding cache 和 source audit。
6. evaluator 未强制 pre-Gold 工件：必须要求状态为 `VERIFIED_PRE_GOLD` 的独立验证工件，并核验 policy/ranking/decision/channel audit hash、evaluation 为 `null` 及冻结 commit。
7. 正式 Gold join 缺少 Stage4A-R2 基线等价硬门：U1 晋级计算前必须完全复现 dense/q25 ER@20、CR@20 以及 q25 gain=94、harm=69；否则停止为 `HARD_FAILURE_IMPLEMENTATION_DRIFT`。

## v2.1 最低失败注入

仅合成测试必须覆盖：缺失 source audit、错误 development digest、错误 model name、错误 max length、tie hash 篡改、score 篡改、ECDF reference 篡改、q25/final 同步篡改、inserted-ID 与 Top-20 脱钩、缺失 pre-Gold verification、任一实现文件 hash 不匹配。

## 审批后的唯一下一门

完成 `docs/STAGE4B_U1_EXECUTION_HARDENING_V2_1.md` 后，只能提交 v2.1 implementation checkpoint 复审。该 checkpoint 不是官方 U1-D 执行授权。
