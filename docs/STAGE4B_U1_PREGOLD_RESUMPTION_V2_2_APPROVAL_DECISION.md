# Stage4B-U1-D v2.2 Official Pre-Gold 恢复批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-13
- Request ID: `STAGE4B_U1_D_V2_2_PREGOLD_RESUMPTION`
- Decision: `APPROVE_STAGE4B_U1_D_V2_2_OFFICIAL_PREGOLD_RESUMPTION`
- Bound request-package commit: `fae181564504f1a69bcebfd5d5201eea7e2d9abf`
- Bound implementation commit: `ca2cca332292f7bd6af12e2a429100be11da5549`
- Gold evaluation: `NOT_AUTHORIZED`
- U1-D metric access or interpretation: `NOT_AUTHORIZED`
- Reservation: `KEEP_LOCKED`
- Stage3B: `KEEP_LOCKED`
- Other project conversations, thread tools, and global memory used: No

## 批准范围与唯一顺序

本批准仅允许依次执行：

1. 将本批准治理状态提交并推送；
2. 在新的治理字节上运行 24 项 synthetic binding verification 两次，两次完整输出必须字节一致；
3. 运行一次只读 dual-ID formal preflight；
4. preflight 全部通过后，运行一次 official channel preparation；
5. 使用冻结配置运行一次 Gold-free controller，并在预注册新路径创建 fresh ID-bound cache；
6. 对新 cache 执行独立只读核查；
7. 冻结并提交推送 channel audit、decision、ranking 和 policy；
8. 在已提交工件上运行 independent verifier；
9. 生成并推送 `status = VERIFIED_PRE_GOLD`、`evaluation = null`；
10. 核对 GitHub 后立即停止。

冻结边界包括：

- 4,500 development queries 与 143,820 units；
- sample-ID SHA-256：`6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2`；
- runtime query-ID SHA-256：`8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6`；
- 逐条 `query_id == dataset::sample_id`；
- encoder `sentence-transformers/all-MiniLM-L6-v2`、`max_length=192`、`batch_size=64`；
- fresh cache 路径 `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_minilm_idbound_embeddings.npz`；
- 旧 Stage4A-R2 cache 原样保留，不覆盖、不删除、不迁移。

## 硬停止规则

formal preflight、cache 独立核查、commit 或 push 的任一硬门失败时立即停止，不运行后续步骤，也不自动重跑。任何恢复都必须形成新的审计或 Amendment 并获得用户批准。

## 继续禁止

- 不运行 Gold evaluation；
- 不读取或解释任何 U1-D retrieval metric、gain/harm、retention、CR/ER 或 false-insert；
- 不作出 U1-D 晋级或有效性结论；
- 不访问 reservation；
- 不访问 Stage3B；
- 不修改数据、实现、模型、阈值、score、ECDF、预算、ranking、endpoint 或停止规则；
- 不在 `VERIFIED_PRE_GOLD` 推送后继续执行。
