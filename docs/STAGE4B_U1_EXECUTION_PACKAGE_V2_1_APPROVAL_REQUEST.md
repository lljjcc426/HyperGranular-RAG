# Stage4B-U1-D v2.1 前 Gold 执行重新审批请求

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request ID: `STAGE4B_U1_D_V2_1_PREGOLD`
- Request date: 2026-07-13
- Package commit: `dd1f8a9893ccb1e760068ad21d48e0e8938cc7f9`
- Machine-readable manifest: `docs/STAGE4B_U1_EXECUTION_PACKAGE_V2_1_MANIFEST.json`
- Protocol architecture: `ACCEPTED_IN_PRINCIPLE`
- Current execution approval: `NOT_APPROVED`
- Requested gate: official U1-D pre-Gold execution only
- Other project conversations or global memory used: No

## 审批请求

请求批准状态：

```text
APPROVE_STAGE4B_U1_D_PREGOLD_EXECUTION_V2_1
```

该批准只授权完成官方 U1-D 的无标签通道、controller policy/ranking/decision 冻结和独立 `VERIFIED_PRE_GOLD`。完成并推送 pre-Gold 工件后必须停止，不得在同一授权下连接 Gold 或计算任何 U1-D 指标。

## 本次包已满足的前置条件

1. v2 科研架构已获原则接受；score、ECDF、q25、60% planned-insert 预算、on/off ranking 和统计门没有在硬化中改变。
2. 退回审查的 7 项阻断问题均已落实为程序硬门，闭环见 `docs/STAGE4B_U1_IMPLEMENTATION_AUDIT_V2_1.md`。
3. Python 3.12 下 20 项合成测试全部通过；审批指定的 11 类失败注入全部被拒绝。
4. 完整 runner 连续两次得到相同证据 SHA-256：`799E2AE73F24C223FA28AB104AF5C830F2E4D7678795B5CB5C8F51DC32D39AC3`。
5. Package commit 已推送至 GitHub `origin/main`，组包时本地 HEAD 与 remote 一致且工作树干净。
6. 测试未读取官方 development 内容、reservation 或 Stage3B；只使用临时 synthetic fixture。

## 批准后允许的唯一执行序列

1. 将项目 `AGENTS.md` 与协议状态改为仅批准 U1-D pre-Gold，并继续锁定 Gold evaluation、reservation 和 Stage3B。
2. 提交并推送治理状态；因协议字节变化，重新运行 20 项 synthetic verification，更新并推送新的绑定证据。
3. 使用 `docs/STAGE4A_R2_SOURCE_AUDIT.json` 强制核验 official source-audit SHA、4,500 条 development 和 query-ID digest。
4. 运行 channel preparer，产生 controller-only unlabeled files、evaluator-only Gold map 和隔离 audit；此时不运行 evaluator。
5. 使用冻结 MiniLM、max length 192、batch 64 和完整默认 retrieval config 运行 Gold-free controller。
6. 将 channel audit、decisions、rankings 和 policy 提交并推送；raw/processed corpus、Gold map 和 embedding cache 不进入 Git。
7. 在上述工件已提交的 commit 上运行独立 verifier，产生 `VERIFIED_PRE_GOLD` 且 `evaluation=null`。
8. 提交并推送 pre-Gold verification，核对 GitHub 后立即停止并汇报。

任何步骤硬失败均停止，不自动重跑，不调整参数。若需要修改协议、阈值、数据边界、实现或停止规则，必须形成新的 Amendment 并重新审批。

## 本次明确不请求授权

- 不请求运行 `stage4b_u1_evaluate.py`。
- 不请求加载 Gold map 计算 dense/q25/U1 ER@20、CR@20、gain、harm、retention 或 false-insert。
- 不请求作出 U1-D 晋级或停止结论。
- 不请求读取 reservation 内容、embedding、decision、ranking 或指标。
- 不请求访问 Stage3B。
- 不请求调整模型、max length、batch size、q25、score、ECDF、预算、统计门或问题类型规则。

## Pre-Gold 硬失败

以下任一情况停止于 pre-Gold，且不生成正式 policy 或不进入下一步：

- source-audit SHA、development 数量或 ID digest 不一致；
- 模型、max length、batch size、run role 或 retrieval config 不一致；
- unlabeled schema 含 Gold/answer/question-type 字段；
- embedding cache 的 unit/query ID 顺序或模型元数据不一致；
- 无 feasible query、预算为空或最大前缀为空；
- NaN/Inf、异常 Top-20、insert 推导不一致或非唯一 ranking；
- protocol/source/input/output/Git commit 任一 hash 不一致；
- verifier 独立复算 tie hash、ECDF、score、order、cutoff、预算或 trigger 失败；
- Git commit/push 失败。

## 后续独立审批门

只有 `VERIFIED_PRE_GOLD` 已提交并推送、工件 hash 核对完成后，才可另行提交 U1-D Gold evaluation 审批请求。该后续请求必须再次明确 Stage4A-R2 baseline equivalence gate 和一次性 Gold join；本文件不提供该授权。

## 审批输出

批准时请明确写出：

```text
批准 Stage4B-U1-D v2.1 前 Gold 执行
```

其他措辞若未明确授权官方 pre-Gold 执行，默认仍保持 `NOT_APPROVED`。
