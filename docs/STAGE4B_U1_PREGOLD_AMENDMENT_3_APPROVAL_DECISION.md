# Stage4B-U1-D Pre-Gold Amendment 3 批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-13
- Amendment ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_3`
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_3_IMPLEMENTATION_SYNTHETIC_ONLY`
- Bound approval-package commit: `42747507d6f37c3d5713949de443311b35262a2d`
- Bound failure-audit commit: `8b43de72418ccda85af3015f758c39bce9d31411`
- Failed controller-artifact commit: `9207bd78eea44d2ea3291fe9b6748526969a3224`
- Official development execution: `NOT_AUTHORIZED`
- Gold evaluation or U1-D effect metrics: `NOT_AUTHORIZED`
- Reservation: `KEEP_LOCKED`
- Stage3B: `KEEP_LOCKED`
- Other project conversations, thread tools, and global memory used: No

## 批准规则

对每个查询 `q` 冻结：

```text
C_q = candidate unit set for q
K_q = min(20, |C_q|)
P_q = min(10, K_q)
```

`MAX_K=20`、`PROTECT_N=10`、最大插入数 `4` 保持不变。verifier 必须独立核验：

1. dense、q25、final 长度严格等于 `K_q`；
2. 列表内 unit ID 唯一且全部属于 `C_q`；
3. `q25[:P_q] == dense[:P_q]`；
4. `planned_insert_count` 位于 `0..min(4, K_q-P_q)`；
5. inserted IDs 等于 `q25[P_q:P_q+planned_insert_count]`；
6. trigger=false 时 final 等于 dense，trigger=true 时 final 等于 q25；
7. 空候选池继续硬失败。

## 仅授权的实现与验证

1. 将 implementation checkpoint 更新为 `stage4b_u1_v2_3`；
2. 仅修改协议、共享 checkpoint/必要常量、independent verifier、synthetic runner 绑定和对应测试；
3. 不修改 retrieval、controller 或 evaluator 算法；
4. 保留现有 24 项 synthetic tests；
5. 新增合法 `K=17`、合法 `K=10`、错误长度、重复 ID、非候选 ID、candidate-count 漂移、protected-prefix 错误和 insertion 推导错误测试；
6. 完整 synthetic suite 运行两次，要求全部通过、0 failure/error/skip 且完整 evidence 字节一致；
7. 形成 implementation audit、完整 SHA-256 和新的 implementation-bound official pre-Gold 恢复审批包；
8. 上述内容提交推送后立即停止。

## 继续禁止

- 不读取 official development、official source audit 或现有 official ranking 内容；
- 不运行 official preflight、channel preparer、controller、cache、independent verifier 或 evaluator；
- 不读取或解释任何 U1-D 效果指标；
- 不访问 reservation 或 Stage3B；
- 不修改、覆盖或删除 commit `9207bd78eea44d2ea3291fe9b6748526969a3224` 的失败工件；
- 不重建、覆盖、删除或迁移 fresh/legacy cache；
- 不修改模型、max length、batch、q25、score、ECDF、预算、trigger、ranking、endpoint 或停止规则；
- 不在 synthetic hardening 后自动恢复 official execution。

实施与 synthetic evidence 推送后，必须对新的 v2.3 implementation commit 单独申请 official pre-Gold 恢复批准。
