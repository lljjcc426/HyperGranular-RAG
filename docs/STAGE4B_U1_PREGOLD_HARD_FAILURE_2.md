# Stage4B-U1-D Pre-Gold 硬失败审计 2

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Mode: run / hard-failure audit
- Audit date: 2026-07-13
- Verification Status: `STOPPED_HARD_FAILURE`
- Failure ID: `STAGE4B_U1_D_PREGOLD_HARD_FAILURE_2`
- Failure code: `HARD_FAILURE_QUERY_ID_REPRESENTATION_MISMATCH`
- Amendment 1 commit: `a7e121584d9f512bb7b4abaabdb9c93913ad560d`
- Amendment 1 approval governance commit: `19bb733`
- Post-Amendment binding evidence commit: `d25e7e9`
- Bound implementation commit at failure: `dd1f8a9893ccb1e760068ad21d48e0e8938cc7f9`
- Gold evaluation: `NOT_RUN_NOT_AUTHORIZED`
- Reservation: `NOT_ACCESSED_KEEP_LOCKED`
- Stage3B: `NOT_ACCESSED_KEEP_LOCKED`
- Other project conversations, thread tools, and global memory used: No

## 结论

Amendment 1 批准后的正式只读 preflight 在 query-ID digest 硬门处停止。official processed queries 的 4,500 个运行时 `query_id` digest 为：

```text
8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6
```

冻结 source audit 的 development digest 为：

```text
6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2
```

两者不一致，触发 `HARD_FAILURE_QUERY_ID_REPRESENTATION_MISMATCH`。执行在 official channel preparation 前停止；没有生成新 cache 或任何 official Stage4B-U1 工件。

## 正式 Preflight 结果

| 硬门 | 实际结果 |
|---|---|
| `HEAD == origin/main` | 通过，均为 `d25e7e9ddebdb00cc3d7674fb3fdede26f16a13f` |
| 工作树干净 | 通过 |
| official units | 通过，143,820 行 |
| official queries | 通过，4,500 行 |
| source-audit SHA-256 | 通过，`1496FF0CE08093AD38258FD5049068D6C4ED74FCEBF63E94E6E486F3478C7AEE` |
| 旧 cache 原样保留 | 通过，SHA-256 `746FC1130038C789190F2A37CB911BBFC46905CFCC138E361C1F6CF991A45F02` |
| 新 cache 不存在 | 通过 |
| 全部拟生成 official 输出不存在 | 通过 |
| official processed `query_id` digest | 失败，实际 `8895D4D2...A25CD6`，冻结比较值 `6B21FD1D...458FB2` |

preflight 只解析了 query 文件的 `query_id` 字段并计算结构性 digest；没有读取或计算 answer、Gold、gain/harm、CR/ER、retention、false-insert、score、ranking 或预算。

## 仓库代码级原因核查

硬失败后没有再次读取 official development。仅检查已提交代码即可确定两个 digest 对应不同 ID 表示：

1. `scripts/stage4a_r2_extract_official.py` 从官方 `_id` 构造 development ID digest；
2. `scripts/stage1_build_corpus.py` 将 `sample_id = sample["id"]`，再构造 `query_id = f"{dataset}::{sample_id}"`；
3. `scripts/stage4a_r2_official_estimation.py` 明确使用 `digest_ids(sample_ids)` 与 source audit 的 `development_query_id_sha256` 比较；
4. `scripts/stage4b_u1_prepare_channels.py`、controller 和 verifier 却使用带 dataset 前缀的运行时 `query_id` digest 与同一个 source-audit `sample_id` digest 比较。

因此该失败是 Stage4B v2.1 把 `sample_id` 边界 digest 与运行时 namespaced `query_id` digest 混为一谈。现有证据不能据此声称样本集合改变；但在双重绑定实现修正并重新审批前，也不能继续 official execution。

## 停止边界

- 未运行 `scripts/stage4b_u1_prepare_channels.py`；
- 未生成 unlabeled channel、Gold map、controller/evaluator audit；
- 未运行 controller，未创建新 ID-bound cache；
- 未生成 decision、ranking、policy 或 `VERIFIED_PRE_GOLD`；
- 未运行 evaluator，未读取任何 U1-D 指标；
- 旧 cache 未覆盖、删除、迁移或修改；
- 未访问 reservation 或 Stage3B；
- 未自动重跑正式 preflight。

当前状态：

```text
PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_2
```

恢复前必须先批准 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_2_DRAFT.md`，完成最小实现修正与合成验证，再对新的实现提交单独申请 official pre-Gold 恢复审批。
