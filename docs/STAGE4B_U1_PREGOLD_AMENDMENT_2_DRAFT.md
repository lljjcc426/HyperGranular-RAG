# Stage4B-U1-D Pre-Gold Amendment 2 草案

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Mode: protocol amendment / implementation plan
- Draft date: 2026-07-13
- Amendment ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_2`
- Status: `DRAFT_NOT_APPROVED_NOT_EXECUTABLE`
- Trigger: `HARD_FAILURE_QUERY_ID_REPRESENTATION_MISMATCH`
- Failure audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_2.md`
- Parent Amendment 1 commit: `a7e121584d9f512bb7b4abaabdb9c93913ad560d`
- Current implementation commit: `dd1f8a9893ccb1e760068ad21d48e0e8938cc7f9`
- Requested authorization: implementation and synthetic verification only
- Official development execution: `NOT_REQUESTED_KEEP_STOPPED`
- Gold evaluation: `NOT_AUTHORIZED`
- Reservation: `KEEP_LOCKED`
- Stage3B: `KEEP_LOCKED`
- Other project conversations, thread tools, and global memory used: No

## 修订原因

Stage4A source audit 的 development digest 绑定官方原始 `_id`，在 processed corpus 中对应 `sample_id`。Stage4B-U1 的运行时 `query_id` 则由 `dataset::sample_id` 构成。现有 v2.1 实现错误地把 namespaced `query_id` digest 与 source-audit `sample_id` digest 直接比较。

本修订不改变 4,500 条 development 样本集合，也不以 retrieval 或 Gold 结果调整边界。它把同一集合的两个确定性 ID 表示分别绑定，并要求逐条验证两者的构造关系。

## 冻结的双重 ID 边界

| 表示 | 定义 | 冻结 digest |
|---|---|---|
| Official sample ID | official `_id`，processed `sample_id` | `6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2` |
| Runtime query ID | `2wikimultihopqa::<sample_id>` | `8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6` |

两者均按现有 `id_digest` 规则计算：字符串排序、以换行连接并在末尾追加换行，再取 UTF-8 SHA-256。

## 最小实现修正

获批后仅允许修改以下 Stage4B-U1 边界绑定代码和对应测试：

1. `scripts/stage4b_u1_common.py`
   - 将 `6B21...` 明确命名为 official development `sample_id` digest；
   - 新增冻结的 runtime `query_id` digest `8895...`；
   - 不修改模型、检索、score、ECDF、预算或 ranking 常量。
2. `scripts/stage4b_u1_prepare_channels.py`
   - formal development 同时读取 `dataset`、`sample_id` 与 `query_id`；
   - 要求 4,500 个 dataset 全部精确为 `2wikimultihopqa`；
   - 要求 sample IDs 与 query IDs 分别唯一；
   - 要求每条 `query_id == f"{dataset}::{sample_id}"`；
   - 要求 sample-ID digest 等于 source audit 的 `6B21...`；
   - 要求 runtime query-ID digest 等于 `8895...`；
   - controller audit 同时记录两个 digest，且仍不得包含 Gold-map 或 labeled-source hash。
3. `scripts/stage4b_u1_goldfree_controller.py`
   - formal channel 同时验证 controller audit 的 sample-ID digest 与 query-ID digest；
   - 运行时 queries 再独立复算两种 digest 和逐条 namespace 关系。
4. `scripts/stage4b_u1_verify.py`
   - pre-Gold verifier 独立复算 sample-ID digest、query-ID digest、dataset 与 namespace 关系；
   - 继续执行现有 score、预算、ranking、commit 和 encoder 配置验证。
5. `tests/test_stage4b_u1_goldfree.py` 与 synthetic runner evidence
   - 保留原 20 项测试；
   - 新增至少四类硬化测试：错误 sample-ID digest、错误 runtime query-ID digest、畸形 `dataset::sample_id` 关系、controller audit 双 digest 漂移；
   - 重新运行完整 synthetic suite 两次并要求 evidence 字节一致。

不得修改 `scripts/stage4b_u1_goldfree_retrieval.py`、`scripts/stage4b_u1_evaluate.py`、任何 Stage4A 结果、数据文件或 cache。

## 保持冻结的科研内容

- development 样本量仍为 4,500，units 仍为 143,820；
- source-audit SHA-256 仍为 `1496FF0CE08093AD38258FD5049068D6C4ED74FCEBF63E94E6E486F3478C7AEE`；
- 新 cache 路径与 Amendment 1 完全不变，且 official 重启前仍必须不存在；
- encoder、max length 192、batch 64、float32、q25、protect=10、insert=4、score、ECDF、0.60 预算、ranking、endpoint 与停止规则全部不变；
- Gold 隔离、reservation 边界与 Stage3B 锁定不变。

## 获批后允许的唯一工作

本 Amendment 的第一次批准只允许：

1. 写入批准治理状态并提交推送；
2. 实现上述最小双重 ID 绑定；
3. 只使用 synthetic fixture 运行新增测试和完整 suite；
4. 形成实现审计、完整文件 hash、确定性 evidence，提交并推送；
5. 提交新的 official pre-Gold 恢复审批请求，绑定新的实现 commit。

在新的实现提交获得用户第二次明确批准前，不得重新读取 official development，不得运行 channel/controller，不得创建新 cache。

## 明确不授权

- 不授权任何 official U1-D preflight、channel、controller、cache 或 verifier；
- 不授权 Gold evaluation 或 U1-D 指标；
- 不授权 reservation 或 Stage3B；
- 不授权修改数据边界、样本、参数、score、ECDF、预算、ranking、endpoint 或停止规则；
- 不授权自动重跑硬失败步骤。

## 审批要求

当前草案不可执行。第一阶段最小批准语句为：

```text
批准 Stage4B-U1-D Pre-Gold Amendment 2：修正 sample_id/query_id 双重边界绑定，仅授权实现与合成验证
```

批准必须绑定本草案所在 Git commit。实现与 synthetic evidence 推送后，项目将再次停止并提交 official pre-Gold 恢复审批，不会自动接触 official development。
