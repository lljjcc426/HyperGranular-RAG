# Stage4B-U1-D Pre-Gold Amendment 4：Cache Fail-Closed 与恢复协议硬化草案

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Mode: experiment protocol planning
- Draft date: 2026-07-13
- Amendment ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_4`
- Trigger review: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_REVIEW_1.md`
- Returned package commit: `dbb4e057405069aceda5a7c5d88d9d39a4d14775`
- Baseline implementation commit: `a1d9ea0c517fcbad1ef27e78e760738d5c04d8b3`
- Proposed implementation checkpoint: `stage4b_u1_v2_3_1`
- Status: `DRAFT_NOT_APPROVED_NOT_EXECUTABLE`
- Requested first authorization: implementation and synthetic verification only
- Official development/source audit/ranking/cache access: `NOT_REQUESTED`
- Gold evaluation: `NOT_REQUESTED`
- Reservation: `KEEP_LOCKED`
- Stage3B: `KEEP_LOCKED`

## 目的与非目的

本 Amendment 只补齐恢复执行的 fail-closed 与可追溯性硬门：批准后 synthetic rebinding、完整 versioned path registry，以及 controller 的 existing-cache-only 模式。它不改变 candidate generation、retrieval、effective-K、q25、score、ECDF、预算、trigger、ranking、evaluator、模型或数据边界。

## 拟授权实现 1：Existing-Cache-Only Controller Mode

formal controller 增加显式模式，例如：

```text
--embedding-cache-mode require-existing
--expected-embedding-cache-sha256 69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D
```

冻结语义：

1. `require-existing` 模式下 cache path 必须已存在且为普通文件；
2. 在模型加载、编码或任何 output write 前，SHA-256 必须精确等于冻结值；
3. NPZ members 必须严格等于 `unit_embeddings`、`query_embeddings`、`unit_ids`、`query_ids`、`model_name`、`max_length`，不得缺失或多出成员；
4. unit/query IDs 必须与当前 controller channel 精确同序；
5. model/max length 必须为 `sentence-transformers/all-MiniLM-L6-v2` / `192`；
6. embeddings 必须为 `float32`、shape `(143820,384)` / `(4500,384)`、全部有限且满足冻结 normalization tolerance；
7. cache bytes 必须为 `210714667`；
8. `require-existing` 模式永远不得调用 `embed_texts`、`mkdir` 或 `np.savez_compressed`；
9. controller 计算完成后、正式 outputs 提升前，重新核验 path、SHA、bytes 和 members；
10. 任一前后门失败均不生成正式 decisions/rankings/policy，立即硬停止且不得自动重跑。

原 `load-or-build` 行为只能保留给 synthetic fixture 或未来单独批准的 cache-creation 流程；official development 恢复必须强制 `require-existing`。

## 拟授权实现 2：Post-Approval Synthetic Rebinding

synthetic runner 增加可审计的附加治理文件绑定入口。后续 official-resumption 获批后，必须把以下文件连同既有实现文件一起写入 evidence hashes：

```text
AGENTS.md
official-resumption approval request
official-resumption manifest
official-resumption approval decision
```

future official-resumption 的冻结顺序为：

1. 批准治理提交推送；
2. 最终治理字节上的完整 synthetic suite 运行两次；
3. 两次全部通过且 evidence 字节一致；
4. rebinding audit/evidence 提交推送；
5. formal preflight 才可开始。

runner 必须拒绝缺失、repo 外、重复或未登记的 binding path，并在 evidence 中记录每个文件的 repo-relative path 与 SHA-256。

## 冻结 Versioned Artifact Registry

下一次 implementation-bound official-resumption 只能使用以下 `v2_3_1` 路径：

| 工件 | 冻结绝对路径 |
|---|---|
| unlabeled units | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_units.jsonl` |
| unlabeled queries | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_queries.jsonl` |
| controller channel audit | `E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_v2_3_1_controller_channel_audit.json` |
| evaluator Gold map | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_gold_map.json` |
| evaluator audit | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_evaluator_channel_audit.json` |
| decisions | `E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_v2_3_1_decisions.jsonl` |
| rankings | `E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_v2_3_1_rankings.jsonl` |
| policy | `E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_v2_3_1_policy.json` |
| controller execution audit | `E:\科研\HyperGranular-RAG\docs\STAGE4B_U1_PREGOLD_V2_3_1_CONTROLLER_EXECUTION_AUDIT.md` |
| VERIFIED_PRE_GOLD output | `E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_v2_3_1_verified_pre_gold.json` |

formal preflight 必须对上述十个路径逐项执行 `Test-Path == false`；任一路径已存在即硬停止。不得把临时文件写到这些正式路径；pending outputs 使用 OS 临时目录，且只有 cache 后核验和等价核验通过后才可提升。

## Synthetic Hardening 要求

保留现有 33 项测试，并新增至少覆盖：

1. 正确 existing cache + exact SHA 通过且 `embed_texts` 未调用；
2. cache 缺失时在任何输出前失败且 `embed_texts` 未调用；
3. cache SHA 错误拒绝；
4. NPZ member drift 拒绝；
5. unit/query ID 顺序漂移拒绝；
6. model/max-length/dtype/shape/finite/normalization/bytes 任一漂移拒绝；
7. controller 运行期间 cache 后指纹漂移拒绝，正式 outputs 不提升；
8. synthetic runner 对附加治理 binding 的正常、缺失、repo 外与重复路径行为。

完整 suite 运行两次，必须全部通过、`0 failure / 0 error / 0 skip` 且完整 evidence 字节一致。形成 implementation audit、完整 SHA-256 和新的 implementation-bound official-resumption 包后停止。

## 本 Amendment 明确不授权

- 不读取 official development、official source audit、现有 official rankings 或 cache 内容；
- 不运行 formal preflight、channel preparer、controller、cache audit、verifier 或 evaluator；
- 不修改或覆盖 v2.2 失败工件；
- 不创建、重建、覆盖、删除或迁移 fresh/legacy cache；
- 不读取或解释 Gold/U1-D 指标；
- 不访问 reservation 或 Stage3B；
- 不修改 retrieval/controller 决策算法、effective-K、模型或任何冻结参数；
- 不在 synthetic hardening 后自动恢复 official execution。
