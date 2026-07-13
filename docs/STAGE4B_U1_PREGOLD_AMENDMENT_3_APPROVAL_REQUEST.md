# Stage4B-U1-D Pre-Gold Amendment 3 审批请求

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-13
- Request ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_3_IMPLEMENTATION_SYNTHETIC`
- Trigger failure: `STAGE4B_U1_D_PREGOLD_HARD_FAILURE_3`
- Bound failure/audit commit: `8b43de72418ccda85af3015f758c39bce9d31411`
- Failed controller artifact commit: `9207bd78eea44d2ea3291fe9b6748526969a3224`
- Amendment draft: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_DRAFT.md`
- Machine-readable manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_MANIFEST.json`
- Requested gate: implementation and synthetic verification only
- Official development execution: `NOT_REQUESTED`
- Gold evaluation: `NOT_REQUESTED`
- Reservation: `KEEP_LOCKED`
- Stage3B: `KEEP_LOCKED`
- Other project conversations, thread tools, and global memory used: No

## 请求批准

请求批准：

```text
批准 Stage4B-U1-D Pre-Gold Amendment 3：effective-K verifier 修正，仅授权实现与合成验证
```

## 硬失败证据

independent verifier 在已提交工件上单次运行，未传 Gold/evaluator 参数，并因固定长度 20 假设停止。Gold-free 结构诊断确认：

- 628/4,500 个查询的候选池少于 20；
- 最小候选数为 10；
- 全部 4,500 条 dense/q25/final 列表长度均等于 `min(20, num_candidate_units)`；
- effective-K 长度 mismatch 为 0；
- `VERIFIED_PRE_GOLD` 未生成；
- Gold、U1-D 效果指标、reservation 与 Stage3B 均未访问。

## 本次请求范围

仅请求：

1. 冻结 `K_q=min(20, |C_q|)` 与 `P_q=min(10,K_q)`；
2. 将 implementation checkpoint 更新为 `stage4b_u1_v2_3`；
3. 修改协议、共享 checkpoint、independent verifier、synthetic runner 绑定和对应测试；
4. 不改变 channel preparer、retrieval、controller 或 evaluator 算法；
5. 保留原 24 项测试并新增 short-pool effective-K 硬化测试；
6. 使用 synthetic fixture 运行完整 suite，两次完整 evidence 必须字节一致；
7. 形成实现审计、完整文件 hash 和新的 implementation-bound official-resumption 审批包；
8. 推送后立即停止。

## 明确不请求授权

- 不重新读取 official development、source audit 或 official ranking 内容；
- 不运行 official preflight、channel、controller、cache 或 verifier；
- 不运行 Gold evaluation或读取、解释任何 U1-D 指标；
- 不覆盖、删除、改写或重新生成 commit `9207bd78eea44d2ea3291fe9b6748526969a3224` 的失败工件；
- 不重建、覆盖、删除或迁移 fresh/legacy cache；
- 不访问 reservation 或 Stage3B；
- 不修改模型、max length、batch、q25、score、ECDF、预算、trigger、ranking、endpoint 或停止规则；
- 不在 synthetic hardening 后自动恢复 official execution。

## 后续门

即使本请求获批并完成实现，也仍不得接触 official development。必须提交并推送新的 v2.3 implementation evidence，再单独申请 implementation-bound official pre-Gold 恢复审批。
