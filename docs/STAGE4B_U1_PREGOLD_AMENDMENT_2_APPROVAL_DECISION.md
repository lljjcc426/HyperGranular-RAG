# Stage4B-U1-D Pre-Gold Amendment 2 批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-13
- Amendment ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_2`
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_2_IMPLEMENTATION_SYNTHETIC_ONLY`
- Bound amendment commit: `dde5a28fec476fddd0ac82ebad39d9eeab0bea1e`
- Official development execution: `NOT_AUTHORIZED`
- Gold evaluation: `NOT_AUTHORIZED`
- Reservation: `KEEP_LOCKED`
- Stage3B: `KEEP_LOCKED`
- Other project conversations, thread tools, and global memory used: No

## 批准范围

本批准仅允许：

1. 修正 `sample_id` 与 runtime `query_id` 的双重 digest 绑定；
2. 增加逐条 `query_id == dataset::sample_id` 校验；
3. 更新对应 common constants、channel preparer、controller、pre-Gold verifier 和测试；
4. 仅使用 synthetic fixture 完成新增硬化测试与完整 suite；
5. 形成实现审计、完整文件 hash 和确定性 evidence；
6. 将实现与 synthetic evidence 提交并推送；
7. 提交新的 implementation-bound official pre-Gold 恢复审批请求后立即停止。

双重边界冻结为：

| 表示 | SHA-256 |
|---|---|
| official `_id` / processed `sample_id` | `6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2` |
| runtime `query_id = 2wikimultihopqa::<sample_id>` | `8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6` |

## 未授权事项

- 不重新读取 official development；
- 不运行 official preflight、channel、controller、cache 或 verifier；
- 不运行 Gold evaluation 或读取任何 U1-D 指标；
- 不访问 reservation；
- 不访问 Stage3B；
- 不修改数据、样本、模型、参数、score、ECDF、预算、ranking、endpoint 或停止规则；
- 不在实现与 synthetic evidence 推送后自动恢复 official execution。

实现与 evidence 推送后必须停止。只有新的实现提交获得用户单独批准，才可重新接触 official development。
