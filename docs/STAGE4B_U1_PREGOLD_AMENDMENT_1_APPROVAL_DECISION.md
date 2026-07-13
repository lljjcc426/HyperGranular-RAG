# Stage4B-U1-D Pre-Gold Amendment 1 批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-13
- Amendment ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_1`
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_1`
- Bound amendment commit: `a7e121584d9f512bb7b4abaabdb9c93913ad560d`
- Bound implementation commit: `dd1f8a9893ccb1e760068ad21d48e0e8938cc7f9`
- Gold evaluation: `NOT_AUTHORIZED`
- Reservation: `KEEP_LOCKED`
- Stage3B: `KEEP_LOCKED`
- Other project conversations, thread tools, and global memory used: No

## 批准范围

本批准严格限于：

1. 保留旧 Stage4A-R2 cache，不覆盖、不删除、不迁移；
2. 执行前确认新的 U1-D cache 路径不存在；
3. 使用 official U1-D Gold-free channel 输入；
4. 使用冻结的 `sentence-transformers/all-MiniLM-L6-v2`、`max_length=192`、`batch_size=64`；
5. 单次生成包含 embeddings、ID 顺序和模型元数据的新 cache；
6. 对新 cache 执行 Amendment 1 冻结的独立只读完整性核查；
7. 核查通过后继续完成原批准范围内的 controller、policy/ranking/decision 冻结和 `VERIFIED_PRE_GOLD`；
8. 推送 `VERIFIED_PRE_GOLD` 后立即停止。

新 cache 路径冻结为：

```text
E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_minilm_idbound_embeddings.npz
```

## 执行前置顺序

1. 本批准决定、协议状态与项目治理状态先提交并推送；
2. 因协议字节变化，未修改的 v2.1 实现重新运行 20 项 synthetic binding verification，并在继续 official development 前提交推送；
3. 再次核查 source audit、4,500-query boundary、query-ID digest 和新 cache 路径不存在；
4. 严格按 Amendment 1 的单次顺序执行 channel、controller、独立 cache 核查、工件提交和 pre-Gold verifier。

## 未授权事项

- 不运行 Gold evaluation；
- 不读取或解释任何 U1-D retrieval metric、gain/harm、retention、CR/ER 或 false-insert；
- 不访问 reservation 内容、embedding、decision、ranking 或指标；
- 不访问 Stage3B；
- 不修改实现、模型、max length、batch size、score、ECDF、q25、预算、endpoint 或停止规则；
- 不在任一硬失败后自动重跑。

若新 cache 路径在执行前已经存在，或独立核查任一项失败，立即停止并重新提交审批。
