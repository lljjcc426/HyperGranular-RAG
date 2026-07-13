# Stage4B-U1-D v2.1 Pre-Gold 硬失败审计 1

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Mode: run / hard-failure audit
- Audit date: 2026-07-13
- Verification Status: `STOPPED_HARD_FAILURE`
- Failure ID: `STAGE4B_U1_D_PREGOLD_HARD_FAILURE_1`
- Failure code: `HARD_FAILURE_EMBEDDING_CACHE_METADATA`
- Approval request commit: `2f6c7067c686bf1f4c13328bd1fc04ab3990f767`
- Bound implementation commit: `dd1f8a9893ccb1e760068ad21d48e0e8938cc7f9`
- Approval governance commit: `d327193`
- Post-approval binding evidence commit: `504a302`
- Gold evaluation: `NOT_RUN_NOT_AUTHORIZED`
- Reservation: `NOT_ACCESSED_KEEP_LOCKED`
- Stage3B: `NOT_ACCESSED_KEEP_LOCKED`
- Other project conversations, thread tools, and global memory used: No

## 结论

正式 U1-D preflight 在 embedding cache 元数据硬门处停止。旧 Stage4A-R2 cache 不包含 v2.1 controller 要求的 ID-bound 元数据，不能证明 embedding 行序与当前 143,820 个 units 和 4,500 个 queries 的顺序一致。

因此本次 pre-Gold 授权没有进入 channel preparation、Gold-free controller、policy/ranking/decision 冻结或 `VERIFIED_PRE_GOLD`。没有生成或读取任何 U1-D 检索指标，也没有访问 reservation 或 Stage3B。

## 已执行的只读 Preflight

| 项目 | 实际结果 |
|---|---|
| `stage4a_r2_official_dev4500_units.jsonl` | 存在；66,784,334 bytes；143,820 行 |
| `stage4a_r2_official_dev4500_queries.jsonl` | 存在；3,720,072 bytes；4,500 行 |
| `stage4a_r2_official_dev4500_minilm_embeddings.npz` | 存在；209,964,061 bytes |
| 旧 cache SHA-256 | `746FC1130038C789190F2A37CB911BBFC46905CFCC138E361C1F6CF991A45F02` |
| 冻结 development query-ID digest | `6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2` |

行数核查只统计记录边界，没有解析查询、答案、supporting facts 或 Gold 字段。cache 核查只读取 NPZ 成员名，没有将 embedding 数组用于相似度、排序、score 或预算计算。

## 命令与异常记录

第一次 NPZ 元数据核查把含中文的 Windows 路径直接放入 Python stdin 脚本。该路径在传输中变为 `??`，命令在打开文件前失败。这是命令传输失败，不是科研硬门；未据此重试实验，也未产生工件。

随后仅修正路径传输方式，将 cache 路径通过环境变量传给同一只读元数据检查。该检查成功打开文件并返回：

```json
{"files":["model_name","query_embeddings","unit_embeddings"],"required_metadata_present":false}
```

v2.1 controller 在 `scripts/stage4b_u1_goldfree_controller.py` 中要求以下六个成员全部存在：

```text
unit_embeddings
query_embeddings
unit_ids
query_ids
model_name
max_length
```

旧 cache 实际缺少 `unit_ids`、`query_ids` 和 `max_length`。这直接命中审批请求中“embedding cache 的 unit/query ID 顺序或模型元数据不一致”的 pre-Gold 硬失败规则。

## 停止边界

硬失败后立即停止，并确认：

- 未运行 `scripts/stage4b_u1_prepare_channels.py`；
- 未生成 controller-only unlabeled channel、evaluator-only Gold map 或 channel audit；
- 未运行 `scripts/stage4b_u1_goldfree_controller.py`；
- 未生成或读取 official decision、ranking、policy、score、budget 或 retrieval metric；
- 未运行 `scripts/stage4b_u1_verify.py`，未生成 `VERIFIED_PRE_GOLD`；
- 未运行 `scripts/stage4b_u1_evaluate.py`；
- 未重建、迁移、补写或覆盖旧 cache；
- 未访问 reservation 内容、embedding、decision、ranking 或指标；
- 未访问 Stage3B。

文件名清点结果为：本地 processed 目录没有 `stage4b_u1*` 文件；仓库 `results/` 中仅有先前的 `stage4b_u1_synthetic_verification.json`；`reports/` 中没有 `stage4b_u1*` 文件。

## 当前决策

状态为：

```text
PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_1
```

不得在原授权下继续或自动重跑。恢复执行必须先批准、提交并推送 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_1_DRAFT.md` 所定义的修订；在此之前 official channel、controller、verifier、Gold evaluation、reservation 和 Stage3B 全部锁定。
