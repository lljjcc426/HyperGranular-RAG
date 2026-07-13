# Stage4B-U1-D Pre-Gold Amendment 1 草案

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Mode: protocol amendment / plan
- Draft date: 2026-07-13
- Amendment ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_1`
- Status: `APPROVED_FOR_SINGLE_PREGOLD_RESUMPTION`
- Approval decision: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_1_APPROVAL_DECISION.md`
- Approval date: 2026-07-13
- Bound amendment commit: `a7e121584d9f512bb7b4abaabdb9c93913ad560d`
- Trigger: `HARD_FAILURE_EMBEDDING_CACHE_METADATA`
- Failure audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_1.md`
- Parent approval request commit: `2f6c7067c686bf1f4c13328bd1fc04ab3990f767`
- Bound implementation commit: `dd1f8a9893ccb1e760068ad21d48e0e8938cc7f9`
- Gold evaluation: `NOT_AUTHORIZED`
- Reservation: `KEEP_LOCKED`
- Stage3B: `KEEP_LOCKED`
- Other project conversations, thread tools, and global memory used: No

## 修订原因

旧 Stage4A-R2 embedding cache 只有 `unit_embeddings`、`query_embeddings` 和 `model_name`，缺少 `unit_ids`、`query_ids` 与 `max_length`。它可以支持旧阶段的确定性复跑，但不满足 v2.1 对 official U1-D cache 行序和 encoder 配置的完整绑定要求。

不得补写、迁移或覆盖旧 cache，因为事后附加 ID 不能独立证明原 embedding 行序。唯一申请的修订是：在新的、执行前必须不存在的路径上，由已批准的 Gold-free controller 使用 channel preparer 生成的无标签输入重新编码并创建 ID-bound cache。

## 唯一变更

旧 cache 继续保留且不得用于 Stage4B-U1-D：

```text
E:\科研\超粒球RAG_数据\processed\stage4a_r2_official_dev4500_minilm_embeddings.npz
```

申请使用新的 U1-D 专用 cache：

```text
E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_minilm_idbound_embeddings.npz
```

起草时该新路径实际不存在。获批执行前必须再次检查：若该路径已经存在，立即硬失败，不覆盖、不删除、不自动改名，也不继续 channel/controller。

## 保持冻结的内容

本修订不改变任何研究参数或实现：

| 项目 | 冻结值 |
|---|---|
| Implementation | `dd1f8a9893ccb1e760068ad21d48e0e8938cc7f9` |
| Encoder | `sentence-transformers/all-MiniLM-L6-v2` |
| Maximum sequence length | `192` |
| Batch size | `64` |
| Embedding storage and normalization | `float32` |
| Run role | `development` |
| Queries | `4,500` |
| Units | `143,820` |
| Query-ID digest | `6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2` |
| q25 floor | `0.1957079917192459` |
| Protected prefix / max inserts | `10 / 4` |
| Planned-insert budget fraction | `0.60` |

Score、ECDF、tie hash、feasibility、ranking、cutoff、主要终点、统计门、停止规则、Gold 隔离、数据边界及 reservation 边界均不变。

## 新 Cache 的预注册硬门

新 cache 必须由当前 v2.1 controller 从 official channel 的无标签 units/queries 按文件顺序一次性创建，并包含：

```text
unit_embeddings
query_embeddings
unit_ids
query_ids
model_name
max_length
```

在提交任何 official policy/ranking/decision 前，必须进行一次独立只读核查：

1. 六个成员全部存在，且没有 Gold、answer、question type 或指标成员；
2. `unit_ids` 与 official unlabeled units 的 143,820 个 `unit_id` 逐项、同序一致；
3. `query_ids` 与 official unlabeled queries 的 4,500 个 `query_id` 逐项、同序一致；
4. `query_ids` digest 等于冻结值 `6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2`；
5. `model_name` 精确等于冻结 encoder，`max_length` 精确等于 `192`；
6. 两个 embedding 数组均为二维 `float32`，第一维分别为 143,820 和 4,500，第二维相同且大于零；
7. 所有 embedding 值均为有限数；
8. 记录新 cache 的 bytes 和 SHA-256，并由 policy 与 verifier 绑定。

任一项失败立即停止。不得修补 cache、改参数、删除后自动重建或在同一授权下再运行一次。

## 获批后的单次执行顺序

1. 将用户批准决定写入项目文档，绑定本 Amendment 所在 commit，提交并推送；
2. 因协议字节变化，使用未修改的实现重跑 20 项 synthetic binding verification，确认字节一致后提交并推送；
3. 只读核验 official source audit、4,500-query boundary、query-ID digest，并确认新 cache 路径仍不存在；
4. 运行一次 official U1-D channel preparer，生成隔离的 controller/evaluator channel，但不运行 evaluator；
5. 运行一次 Gold-free controller，并让它在新路径创建 ID-bound cache；
6. 在提交 official 工件前执行上述独立 cache 硬门；
7. 通过后提交并推送 channel audit、decision、ranking 和 policy；
8. 在已提交工件上独立运行 verifier，生成 `evaluation = null` 的 `VERIFIED_PRE_GOLD`；
9. 提交并推送 `VERIFIED_PRE_GOLD`，核对 GitHub 后立即停止。

## 明确不授权

本 Amendment 不授权：

- 运行 Gold evaluator 或读取、解释任何 U1-D 指标；
- 访问 reservation 内容、embedding、decision、ranking 或指标；
- 访问 Stage3B；
- 修改 controller、verifier 或其他实现；
- 修改模型、max length、batch、score、ECDF、q25、预算、endpoint 或停止规则；
- 复用、补写、迁移、覆盖或删除旧 Stage4A-R2 cache；
- 在任一硬失败后自动重跑。

## 审批要求

本修订已由用户按以下语句批准：

```text
批准 Stage4B-U1-D Pre-Gold Amendment 1：重新生成 ID-bound embedding cache
```

批准绑定 commit `a7e121584d9f512bb7b4abaabdb9c93913ad560d`。批准决定、协议状态和新的 synthetic binding evidence 均推送到 `origin/main` 后，才可重新接触 official development。
