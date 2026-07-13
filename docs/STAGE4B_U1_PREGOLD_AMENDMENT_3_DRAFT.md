# Stage4B-U1-D Pre-Gold Amendment 3：Effective-K Verifier 修正草案

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Draft date: 2026-07-13
- Amendment ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_3`
- Trigger: `STAGE4B_U1_D_PREGOLD_HARD_FAILURE_3`
- Trigger audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_3.md`
- Status: `DRAFT_NOT_APPROVED_NOT_EXECUTABLE`
- Requested first authorization: implementation and synthetic verification only
- Official development execution: `NOT_REQUESTED`
- Gold evaluation: `NOT_REQUESTED`
- Reservation: `KEEP_LOCKED`
- Stage3B: `KEEP_LOCKED`

## 问题定义

协议使用“Top-20”描述 retrieval depth，但 official development 中有 628 个查询的 Gold-free 候选池少于 20。controller 的冻结实现自然返回至多 20 个候选；verifier 却无条件要求列表长度恰好为 20，导致诚实的短候选池输出被拒绝。

该失败不涉及 Gold、score、ECDF、预算、trigger 或 ranking 顺序的改变。现有证据只支持修正 verifier 的列表长度不变量，不能放宽其他门。

## 冻结修正规则

对每个查询 `q`，由 controller-channel units 独立计算：

```text
C_q = set of unit_ids bound to query q
K_q = min(MAX_K, |C_q|)
P_q = min(PROTECT_N, K_q)
```

其中 `MAX_K=20`、`PROTECT_N=10` 保持不变。verifier 必须：

1. 要求 dense、q25 与 final 列表长度都严格等于 `K_q`；
2. 要求每个列表内 ID 唯一，且全部属于 `C_q`；
3. 要求 `q25[:P_q] == dense[:P_q]`；
4. 要求 `planned_insert_count` 位于 `0..min(4, K_q-P_q)`；
5. 从 `q25[P_q:P_q+planned_insert_count]` 独立推导插入 ID；
6. 继续逐条核验 trigger=false 时 final 等于 dense、trigger=true 时 final 等于 q25；
7. `|C_q|=0` 仍为硬失败，不得用 effective-K 接受空候选池；
8. Evaluation depth 仍为 20；当候选池不足 20 时，“Top-20”明确解释为“最多 20，即 K_q”。

## 第一阶段拟授权实现

第一阶段只允许：

1. 在协议中加入上述 effective-K 定义；
2. 将实现 checkpoint 更新为 `stage4b_u1_v2_3`；
3. 修改 independent verifier 及必要的共享常量/测试绑定，不改变 retrieval/controller/evaluator 算法；
4. 保留原 24 项 synthetic tests；
5. 新增至少以下 hardening：诚实 `K=17` 通过、`K=10` 通过、错误长度拒绝、重复或越界 unit ID 拒绝、candidate-count 漂移拒绝、错误 effective-prefix/insertion 推导拒绝；
6. 完整 synthetic suite 连续两次字节一致；
7. 形成 implementation audit、全部文件 hash 和新的 official-resumption 审批包后停止。

## 第一阶段明确禁止

- 不重新读取 official development、source audit 或现有 official rankings；
- 不运行 formal preflight、channel preparer、controller、cache 或 verifier；
- 不修改或覆盖 commit `9207bd78eea44d2ea3291fe9b6748526969a3224` 中的失败工件；
- 不重建、覆盖、删除或迁移 fresh/legacy cache；
- 不运行 Gold evaluation，不读取或解释任何 U1-D 指标；
- 不访问 reservation 或 Stage3B；
- 不修改模型、max length、batch、q25、score、ECDF、预算、trigger、ranking、endpoint 或停止规则。

## 后续 official 恢复的预期边界

第一阶段完成后仍需新的 implementation-bound 批准。后续请求应使用新的 versioned channel/controller 工件路径，保留 v2.2 失败工件；允许复用且只读加载 SHA 已核验的 fresh ID-bound cache，不重新编码。新的 controller decision/ranking 必须与 v2.2 失败工件逐字节一致，否则硬停止；新 policy 仅允许因 checkpoint、commit 和实现 hash 绑定发生预期变化。随后才可再次运行 independent verifier。

本草案本身不授权任何实现或执行。
