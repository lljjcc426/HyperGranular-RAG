# Stage4B-U1-D v2.3 Official Pre-Gold 恢复包审查 1

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Review mode: protocol and reproducibility validation
- Review date: 2026-07-13
- Reviewed package commit: `dbb4e057405069aceda5a7c5d88d9d39a4d14775`
- Bound implementation commit: `a1d9ea0c517fcbad1ef27e78e760738d5c04d8b3`
- Decision: `RETURN_FOR_PROTOCOL_AND_CACHE_FAIL_CLOSED_REVISION`
- v2.3 effective-K implementation: `PASS_WITHOUT_NEW_IMPLEMENTATION_FINDING`
- Official execution: `NOT_AUTHORIZED`
- Official data, ranking, cache, Gold, reservation, or Stage3B accessed in this review: No
- Other project conversations, thread tools, and global memory used: No

## 总体结论

Amendment 3 的 effective-K 实现与 33 项 synthetic evidence 维持有效；本次没有发现新的 effective-K 实现阻断。恢复审批包 `dbb4e057405069aceda5a7c5d88d9d39a4d14775` 不能直接批准，必须先补齐三项硬门。

## Finding 1：批准后的 synthetic rebinding 缺失

当前包在批准治理提交后直接进入 formal preflight。批准落盘通常会改变 `AGENTS.md` 和治理状态字节，现有 evidence SHA-256：

```text
38DDA409C866AAAC6C2AEDBA0D0716DA6F483854E9A6019E9040B9B2B1FA40B5
```

不能继续代表实际 official execution 时的完整治理绑定。

后续恢复包必须冻结以下顺序：

1. 写入并推送批准治理；
2. 在批准后的最终治理字节上完整运行 synthetic suite 两次；
3. 两次均须全部通过、`0 failure / 0 error / 0 skip`，完整 evidence 字节一致；
4. 提交并推送新的 synthetic rebinding audit 和 evidence；
5. 然后才允许 formal preflight。

future runner 必须把恢复审批请求、manifest、批准决定和 `AGENTS.md` 纳入该次 evidence 的实际 hash 绑定。

## Finding 2：v2.3 新工件路径未逐项冻结

原包只要求使用“new versioned paths”，没有登记全部准确路径，导致“执行前不存在”无法独立复算。

修订必须逐项冻结：unlabeled units、unlabeled queries、controller channel audit、evaluator Gold map、evaluator audit、decisions、rankings、policy、controller execution audit 和 `VERIFIED_PRE_GOLD` verifier output。每个路径均须在 formal preflight 时不存在；任一路径碰撞立即硬停止。

## Finding 3：cache 只读复用未在 controller 内 fail-closed

当前 `scripts/stage4b_u1_goldfree_controller.py::load_or_build_embeddings` 的实际逻辑是：cache 存在时加载，不存在时编码并写入。代码没有 formal `require-existing` 模式，也没有对冻结 cache SHA-256 执行 controller 内前后核验。

因此仅在外部做一次 preflight 不能完全落实“禁止编码、重建或覆盖”。下一实现修订至少必须：

- formal controller 显式启用 require-existing/no-build 模式；
- cache 不存在、不是普通文件或 SHA 不等于冻结值时，在任何编码和 output write 前硬失败；
- 核验 exact NPZ members、unit/query ID 顺序、模型元数据、dtype、shape、finite、normalization 和 bytes；
- controller 完成后再次核验 cache path、SHA、bytes 和 members 不变；
- 后核验通过前不得把 pending controller outputs 提升为正式 versioned outputs；
- synthetic failure injection 必须证明 cache 缺失或漂移时 `embed_texts` 不会被调用。

这构成实现修改，不能在现有 official-resumption 包下直接执行，必须先获得新的 implementation/synthetic-only 批准。

## 审查后的停止门

- `dbb4e057...` 保留为被退回的历史审批包，不删除、不改写；
- 不批准或执行该包中的 formal preflight/channel/controller/cache/verifier 顺序；
- 先审批并完成 cache fail-closed implementation/synthetic Amendment；
- 新实现提交后重新形成 implementation-bound official pre-Gold 恢复审批包。
