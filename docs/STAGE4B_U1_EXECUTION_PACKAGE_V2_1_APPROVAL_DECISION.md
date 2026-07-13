# Stage4B-U1-D v2.1 前 Gold 执行批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-13
- Request ID: `STAGE4B_U1_D_V2_1_PREGOLD`
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_EXECUTION_V2_1`
- Approval request commit: `2f6c7067c686bf1f4c13328bd1fc04ab3990f767`
- Bound implementation commit: `dd1f8a9893ccb1e760068ad21d48e0e8938cc7f9`
- Gold evaluation: `NOT_AUTHORIZED`
- Reservation: `KEEP_LOCKED`
- Stage3B: `KEEP_LOCKED`
- Other project conversations or global memory used: No

## 批准范围

本批准严格限于：

1. 官方 U1-D channel preparation；
2. Gold-free controller；
3. policy、ranking、decision 冻结并提交推送；
4. 独立生成、提交并推送 `VERIFIED_PRE_GOLD`；
5. 完成后立即停止。

`VERIFIED_PRE_GOLD` 必须保持 `evaluation = null`，并确认正式 U1-D boundary、冻结 encoder 配置、已提交工件、独立 score/预算/ranking 检查。

## 未授权事项

- 不运行 Gold evaluation；
- 不读取或解释任何 U1-D retrieval metric、gain/harm、retention、CR/ER 或 false-insert；
- 不访问 reservation 内容、embedding、decision、ranking 或指标；
- 不访问 Stage3B；
- 不调整参数、阈值、score、预算、endpoint 或停止规则；
- 硬门失败后不自动重跑。

任何硬门失败均立即停止并重新申请审批。

## 执行顺序

执行严格遵循 `docs/STAGE4B_U1_EXECUTION_PACKAGE_V2_1_APPROVAL_REQUEST.md` 的八步 pre-Gold 顺序。批准治理状态必须先提交推送；协议字节变化后必须重跑并推送 20 项 synthetic binding verification；之后才允许接触 official development。
