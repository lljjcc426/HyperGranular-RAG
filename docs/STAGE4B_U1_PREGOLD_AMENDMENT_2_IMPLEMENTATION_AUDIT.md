# Stage4B-U1-D Pre-Gold Amendment 2 实现审计

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Mode: implementation validation
- Audit date: 2026-07-13
- Amendment ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_2`
- Approval governance commit: `437b35e`
- Status: `SYNTHETICALLY_VERIFIED_AWAITING_OFFICIAL_RESUMPTION_APPROVAL`
- Official development accessed: No
- Official source audit loaded by tests: No
- Reservation accessed: No
- Stage3B accessed: No
- Gold evaluation: Not run
- Other project conversations, thread tools, and global memory used: No

## 实现结论

Amendment 2 的双重 ID 边界修正已经完成。Stage4B-U1 现在分别绑定：

```text
sample_id SHA-256 = 6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2
query_id SHA-256  = 8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6
```

Formal preparer、controller 和 verifier 均要求每条 `query_id == dataset::sample_id`，并分别复算 sample-ID 与 runtime query-ID digest。Implementation checkpoint 从 `stage4b_u1_v2_1` 更新为 `stage4b_u1_v2_2`。

## 文件级变更

| 文件 | 变更 |
|---|---|
| `scripts/stage4b_u1_common.py` | 分离冻结 sample-ID/query-ID digest，增加 official dataset，更新 checkpoint |
| `scripts/stage4b_u1_prepare_channels.py` | formal 双 digest、dataset、唯一性与逐条 namespace 关系硬门；audit 记录两种 digest |
| `scripts/stage4b_u1_goldfree_controller.py` | 对 unlabeled queries 和 channel audit 独立验证双 digest 与 namespace；policy 绑定 sample-ID digest |
| `scripts/stage4b_u1_verify.py` | 独立复算双 digest、namespace、source-audit sample digest 与 policy/channel 绑定 |
| `tests/test_stage4b_u1_goldfree.py` | 保留原 20 项并新增四类失败注入 |
| `scripts/stage4b_u1_run_synthetic_verification.py` | evidence 状态与 verified properties 更新为 Amendment 2 |

`scripts/stage4b_u1_goldfree_retrieval.py`、`scripts/stage4b_u1_evaluate.py`、模型、数据、cache、score、ECDF、预算、ranking、endpoint 和停止规则均未修改。

## Synthetic 验证

Verbose suite：

```text
24 tests
0 failures
0 errors
0 skipped
```

新增失败注入：

1. formal processed sample-ID digest 漂移；
2. formal runtime query-ID digest 漂移；
3. `query_id != dataset::sample_id`；
4. controller channel audit 的 sample-ID/query-ID digest 漂移。

完整 evidence runner 在最终 AGENTS/协议字节上连续运行两次，输出字节一致：

```text
8B3057238D67EBE874017068C125126974062C61FAF3D79595E884F16A876D7D
```

Evidence 状态为 `AMENDMENT_2_SYNTHETICALLY_HARDENED_AWAITING_OFFICIAL_RESUMPTION_APPROVAL`。

## 文件 Hash

| 文件 | SHA-256 |
|---|---|
| `AGENTS.md` | `81E1FD1A0B8C6F5D0E868CEBB4CA9F2F7AE6529305D81A767418025B6A7131A6` |
| `docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md` | `F880B2D26D9D60B433C694E08DB3081F10A70F6BBB5C022E694BE0A3067EBFAE` |
| `docs/STAGE4B_U1_EXECUTION_HARDENING_V2_1.md` | `A85420942DC8A5DF8EAF468464B94E0DD2826AE7EBFC6318D503FDA2D40E4873` |
| `docs/STAGE4B_U1_EXECUTION_PACKAGE_REVIEW_1.md` | `D7028F83B99AF171DCBD1CCCC40AA3F0A8C39849BCCCED7C262303EFC76DC28A` |
| `scripts/stage4b_u1_common.py` | `EE4394086A96424CC4663BADE8030DF959950413DB7F09A17076C70A3DE5C627` |
| `scripts/stage4b_u1_prepare_channels.py` | `BF629382DCD93F9FD64F0DEB0D441DC775725040E51CE4155884023CE29FD76C` |
| `scripts/stage4b_u1_goldfree_controller.py` | `713BC1DF19472EFE692A2A042A39F96DEE2DCB93187B177EE10DDB5AD7C7A752` |
| `scripts/stage4b_u1_goldfree_retrieval.py` | `3B50FAFD057E2565167ED09288D61829B3FBD044991F139F734F819955038A3B` |
| `scripts/stage4b_u1_evaluate.py` | `343BC9D2478042FF582DAA5DE716498124166C72A520A35DAE53F56C976F2E31` |
| `scripts/stage4b_u1_verify.py` | `889F4E1F5D5E70E3169E4A856C5A86294F8FA28996910AE51BCC4EF1F076A180` |
| `scripts/stage4b_u1_run_synthetic_verification.py` | `DA8FB1D6E898E4417EC172FFAAC81CD3DB688FAF51930F826A1B25BCB139EA6E` |
| `tests/test_stage4b_u1_goldfree.py` | `8388F6DAB255BBB5419DC2C3DAE099AC427709CC20466758D125FA1D5165EFAB` |

## 证据边界

- 所有测试只使用 OS 临时目录中的 synthetic fixture；
- 没有读取 official development 或 official source audit；
- 没有创建 official channel、cache、decision、ranking、policy 或 verifier 工件；
- 没有运行 Gold evaluator；
- 没有访问 reservation 或 Stage3B；
- synthetic 临时工件没有持久化。

## 当前停止门

实现与 synthetic evidence 完成不构成 official execution 授权。提交推送后必须停止，并以新的 implementation commit 提交 official pre-Gold 恢复审批。用户批准前不得重新读取 official development。
