# Stage4B-U1-D v2.3 Official Pre-Gold 恢复审批请求

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-13
- Request ID: `STAGE4B_U1_D_V2_3_PREGOLD_RESUMPTION`
- Amendment 3 approval-package commit: `42747507d6f37c3d5713949de443311b35262a2d`
- Amendment 3 implementation commit: `a1d9ea0c517fcbad1ef27e78e760738d5c04d8b3`
- Failed v2.2 controller-artifact commit: `9207bd78eea44d2ea3291fe9b6748526969a3224`
- Machine-readable manifest: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_MANIFEST.json`
- Current execution approval: `NOT_APPROVED`
- Requested gate: official U1-D pre-Gold resumption only
- Gold evaluation: `NOT_REQUESTED`
- Reservation: `KEEP_LOCKED`
- Stage3B: `KEEP_LOCKED`
- Other project conversations, thread tools, and global memory used: No

## 审批请求

请求批准：

```text
APPROVE_STAGE4B_U1_D_V2_3_OFFICIAL_PREGOLD_RESUMPTION
```

本请求只恢复 official U1-D 的 pre-Gold 顺序：批准治理、一次只读 formal preflight、新的 versioned channel、只读复用现有 ID-bound cache 的单次 Gold-free controller、与 v2.2 失败工件的独立等价核验、工件冻结提交和一次 independent verifier。目标只到：

```text
status = VERIFIED_PRE_GOLD
evaluation = null
```

提交推送后必须立即停止，不接触 Gold evaluation。

## Hard Failure 3 闭环

v2.2 controller 对每条查询生成 `min(20, candidate_count)` 个候选，但旧 verifier 无条件要求 20 个 ID。Amendment 3 已在 implementation commit `a1d9ea0c517fcbad1ef27e78e760738d5c04d8b3` 修正为：

```text
K_q = min(20, |C_q|)
P_q = min(10, K_q)
```

verifier 独立检查候选池非空与计数、dense/q25/final 的 exact `K_q` 长度、列表内唯一性、候选成员关系、`P_q` 前缀、insertion 范围与推导、trigger/final selector。retrieval、controller 和 evaluator 算法未修改。

## Implementation Evidence

- Implementation checkpoint: `stage4b_u1_v2_3`
- Implementation commit: `a1d9ea0c517fcbad1ef27e78e760738d5c04d8b3`
- Audit: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_IMPLEMENTATION_AUDIT.md`
- Synthetic evidence: `results/stage4b_u1_d_pregold_amendment_3_synthetic_verification.json`
- Evidence SHA-256: `38DDA409C866AAAC6C2AEDBA0D0716DA6F483854E9A6019E9040B9B2B1FA40B5`
- Complete suite: 33 tests, 0 failures, 0 errors, 0 skipped
- Determinism: two complete runner outputs byte-identical
- Official development/source audit/ranking/cache accessed by tests: No
- Gold, reservation, or Stage3B accessed: No

原 24 项测试全部保留，新增 9 项覆盖合法 `K=17`、合法 `K=10`、错误长度、重复 ID、非候选 ID、candidate-count 漂移、空候选池、protected-prefix 漂移和 insertion 推导漂移。

## 请求批准后的唯一执行顺序

1. 写入用户批准决定，明确绑定本 request package 所在提交和 implementation commit `a1d9ea0c517fcbad1ef27e78e760738d5c04d8b3`，提交并推送；
2. 运行一次只读 formal preflight：核对 Git ancestry、实现/evidence hash、source-audit 与 official development 双 ID 边界、旧失败工件仍等于 commit `9207bd78eea44d2ea3291fe9b6748526969a3224`、fresh/legacy cache SHA、fresh cache ID/模型元数据，以及全部 v2.3 输出路径执行前不存在；
3. 任一 preflight 门失败立即停止，不运行 channel，不自动重跑；
4. 运行一次 official U1-D channel preparer，写入新的 v2.3 versioned controller/evaluator channel；不得覆盖 v2.2 channel 或失败工件，不运行 evaluator；
5. 独立核验新 unlabeled units/queries 与 v2.2 冻结字节相同，双 ID digest 与逐条 namespace 关系不变；
6. 在已存在且 SHA-256 严格等于 `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D` 的 fresh ID-bound cache 上运行一次 Gold-free controller；cache 只能只读加载，禁止编码、重建、覆盖、删除或迁移；
7. 新 decisions 与 rankings 必须分别与 v2.2 冻结 SHA-256 `6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7`、`ED289D234F6F4FEC58A48168CB6CA78950489CD5F5640E977068CA6A786E03CB` 字节一致；任一不一致立即停止；
8. 新 policy 与 v2.2 policy 进行结构化差分，只允许 `implementation_checkpoint`、`git_commit_sha`、`protocol_sha256`、`implementation_hashes.common_source_sha256`、`implementation_hashes.verifier_source_sha256` 和 `input_hashes.channel_audit` 发生已登记变化；其余字段必须一致；
9. 独立等价核验通过后，提交并推送新 v2.3 channel audit、decision、ranking、policy 与审计；
10. 在已提交工件上运行一次 independent verifier，不传入 Gold/evaluator 参数；
11. verifier 只有在全部 v2.3 边界、effective-K、score/ECDF/预算/ranking 复算与 Git 工件绑定通过时，才可写出 `VERIFIED_PRE_GOLD` 且 `evaluation=null`；
12. 提交并推送 verifier 工件，核对 GitHub 后立即停止。

## 新旧工件规则

- v2.2 commit `9207bd78eea44d2ea3291fe9b6748526969a3224` 中的 channel audit、decision、ranking、policy 保持 `UNVERIFIED_INVALID_FOR_GOLD`，不得覆盖、删除、改写或提升证据等级；
- 所有 v2.3 channel/controller/verifier 文件使用新的 versioned 路径；执行前必须不存在；
- fresh ID-bound cache 只读复用，不创建新 cache；legacy cache 只核对 SHA，不读取 embedding 内容；
- 新 channel 的 Gold map 只能保留在 evaluator channel，不得传给 controller、policy 或 pre-Gold verifier；
- 新 verifier 通过不回溯改变 v2.2 失败记录，只形成独立的 v2.3 `VERIFIED_PRE_GOLD` 工件。

## 请求继续冻结的内容

- Dataset / boundary: `2wikimultihopqa`, 4,500 queries, 143,820 units
- Sample-ID SHA-256: `6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2`
- Runtime query-ID SHA-256: `8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6`
- Encoder: `sentence-transformers/all-MiniLM-L6-v2`
- Maximum sequence length / batch size: `192 / 64`
- Embedding dtype and normalization: `float32`, normalized
- q25 floor: `0.1957079917192459`
- `MAX_K / PROTECT_N / INSERT_BUDGET`: `20 / 10 / 4`
- Budget fraction: `0.60`
- Score、ECDF、tie hash、trigger、ranking、endpoint 与停止规则：不变
- Fresh cache path: `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_minilm_idbound_embeddings.npz`
- Fresh cache SHA-256: `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D`
- Legacy cache SHA-256: `746FC1130038C789190F2A37CB911BBFC46905CFCC138E361C1F6CF991A45F02`

## 明确不请求授权

- 不运行 Gold evaluation；
- 不读取或解释任何 U1-D retrieval metric、gain/harm、retention、CR/ER 或 false-insert；
- 不作出 U1-D 晋级、停止或有效性结论；
- 不访问 reservation 内容、embedding、decision、ranking 或指标；
- 不访问 Stage3B；
- 不修改数据、实现、模型、参数、score、ECDF、预算、trigger、ranking、endpoint 或停止规则；
- 不创建、重建、覆盖、删除或迁移 fresh/legacy cache；
- 不覆盖或删除任何 v2.2 失败工件；
- 不在任一硬失败后自动重跑。

## 审批输出

批准时请明确绑定本审批包所在提交和实现提交 `a1d9ea0c517fcbad1ef27e78e760738d5c04d8b3`，并写出：

```text
批准 Stage4B-U1-D v2.3 official pre-Gold 恢复执行
```

其他措辞若未明确授权该 official pre-Gold 顺序，默认保持 `NOT_APPROVED`。
