# Stage4B-U1-D v2.2 Official Pre-Gold 恢复审批请求

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-13
- Request ID: `STAGE4B_U1_D_V2_2_PREGOLD_RESUMPTION`
- Amendment 2 commit: `dde5a28fec476fddd0ac82ebad39d9eeab0bea1e`
- Implementation commit: `ca2cca332292f7bd6af12e2a429100be11da5549`
- Machine-readable manifest: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_2_MANIFEST.json`
- Current execution approval: `NOT_APPROVED`
- Requested gate: official U1-D pre-Gold resumption only
- Gold evaluation: `NOT_REQUESTED`
- Reservation: `KEEP_LOCKED`
- Stage3B: `KEEP_LOCKED`
- Other project conversations, thread tools, and global memory used: No

## 审批请求

请求批准：

```text
APPROVE_STAGE4B_U1_D_V2_2_OFFICIAL_PREGOLD_RESUMPTION
```

本请求只恢复 official U1-D 的 pre-Gold 顺序：dual-ID formal preflight、channel preparation、单次 fresh ID-bound cache/controller、独立 cache 核查、policy/ranking/decision 冻结和 `VERIFIED_PRE_GOLD`。完成提交推送后必须立即停止。

## 两次硬失败的闭环

### Hard Failure 1

旧 Stage4A-R2 cache 缺少 `unit_ids`、`query_ids` 与 `max_length`。Amendment 1 已冻结新路径，要求旧 cache 原样保留，并由 controller 单次创建 fresh ID-bound cache。

### Hard Failure 2

v2.1 把 source-audit `sample_id` digest 与 namespaced runtime `query_id` digest 直接比较。Amendment 2 的 v2.2 实现现在分别冻结：

| 表示 | SHA-256 |
|---|---|
| official `_id` / processed `sample_id` | `6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2` |
| runtime `query_id = 2wikimultihopqa::<sample_id>` | `8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6` |

Preparer、controller 和 independent verifier 均逐条验证 `query_id == dataset::sample_id`，并分别复算两个 digest。

## Implementation Evidence

- Implementation checkpoint: `stage4b_u1_v2_2`
- Implementation commit: `ca2cca332292f7bd6af12e2a429100be11da5549`
- Audit: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_2_IMPLEMENTATION_AUDIT.md`
- Synthetic evidence: `results/stage4b_u1_synthetic_verification.json`
- Evidence SHA-256: `8B3057238D67EBE874017068C125126974062C61FAF3D79595E884F16A876D7D`
- Complete suite: 24 tests, 0 failures, 0 errors, 0 skipped
- Determinism: two complete runner outputs byte-identical
- Official development accessed by tests: No
- Official source audit loaded by tests: No
- Reservation accessed: No
- Stage3B accessed: No

原 20 项测试全部保留。新增四类失败注入覆盖 formal sample-ID drift、runtime query-ID drift、namespace 关系错误和 channel audit 双 digest 漂移；controller 与 verifier 均拒绝 audit digest 漂移。

## 请求批准后的唯一执行顺序

1. 写入用户批准决定，绑定本 request package commit 与 implementation commit `ca2cca332292f7bd6af12e2a429100be11da5549`；
2. 提交并推送批准治理状态；因 AGENTS/协议字节变化，重新运行 24 项 synthetic binding verification，两次字节一致后提交推送；
3. 正式只读 preflight 同时核验 source-audit SHA、4,500 queries、143,820 units、sample-ID digest、runtime query-ID digest、逐条 namespace 关系、旧 cache 原样保留、全部新路径不存在；
4. 任一 preflight 门失败立即停止，不运行 channel，不自动重跑；
5. 运行一次 official U1-D channel preparer，生成隔离的 controller/evaluator channel，但不运行 evaluator；
6. 使用冻结的 MiniLM、`max_length=192`、`batch_size=64` 和新路径运行一次 Gold-free controller；
7. 在提交 policy/ranking/decision 前，独立只读核查新 cache 的六项成员、ID 同序、双 digest、模型元数据、dtype、shape、有限值、bytes 和 SHA-256；
8. 核查通过后提交并推送 channel audit、decision、ranking 和 policy；
9. 在已提交工件上运行 independent verifier，不传入任何 Gold/evaluator 参数，生成 `status=VERIFIED_PRE_GOLD` 且 `evaluation=null`；
10. 提交并推送 `VERIFIED_PRE_GOLD`，核对 GitHub 后立即停止。

## 请求继续冻结的内容

- Encoder: `sentence-transformers/all-MiniLM-L6-v2`
- Maximum sequence length: `192`
- Batch size: `64`
- Embedding dtype and normalization: `float32`
- q25 floor: `0.1957079917192459`
- Protect / insert: `10 / 4`
- Budget fraction: `0.60`
- Score、ECDF、tie hash、ranking、endpoint 与停止规则：不变
- Fresh cache path: `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_minilm_idbound_embeddings.npz`
- Legacy cache: 保留，不覆盖、不删除、不迁移

## 明确不请求授权

- 不运行 Gold evaluation；
- 不读取或解释任何 U1-D retrieval metric、gain/harm、retention、CR/ER 或 false-insert；
- 不作出 U1-D 晋级、停止或有效性结论；
- 不访问 reservation 内容、embedding、decision、ranking 或指标；
- 不访问 Stage3B；
- 不修改数据、实现、模型、参数、score、ECDF、预算、ranking、endpoint 或停止规则；
- 不在任一硬失败后自动重跑。

## 审批输出

批准时请明确绑定本审批包提交和实现提交 `ca2cca332292f7bd6af12e2a429100be11da5549`，并写出：

```text
批准 Stage4B-U1-D v2.2 official pre-Gold 恢复执行
```

其他措辞若未明确授权该 official pre-Gold 顺序，默认保持 `NOT_APPROVED`。
