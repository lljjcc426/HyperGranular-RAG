# HyperGranular-RAG 项目约束

本仓库继承 `E:\科研\AGENTS.md` 的全部规则。发生冲突时采用更严格的规则。

## 项目边界

- 代码与文档：`E:\科研\HyperGranular-RAG`
- 本地未跟踪数据：`E:\科研\超粒球RAG_数据`
- GitHub：`https://github.com/lljjcc426/HyperGranular-RAG`
- 允许的会话上下文：当前对话，以及用户明确指定的同一 HyperGranular-RAG 项目内部会话
- 禁止：其他项目会话、全局 Codex 记忆、项目外研究参数或结论

## 当前科研硬约束

1. `docs/PRIOR_STAGE_METHOD_AUDIT.md` 规定既有阶段的证据等级。
2. Stage3B 始终锁定，除非新的预注册协议和用户明确批准同时满足。
3. Stage2G 未验证 boundary-only 规则，不得把它作为已支持机制复活。
4. 原 Stage4A 镜像 pilot 已失效，只能保留为历史记录。
5. Stage4A-R2 已完成并独立验证；Stage4B-U1 v2 架构仅为 `ACCEPTED_IN_PRINCIPLE`。
6. q25 阈值 `0.1957079917192459` 只能作为冻结迁移策略使用，不得声称是 2Wiki 最优阈值。
7. 任何硬失败后的修订必须先批准、写入、提交并推送，再执行。
8. Stage4B-U1-D v2.2 official pre-Gold 已在 independent verifier 命中 `HARD_FAILURE_VERIFIER_FIXED_TOP20_ASSUMPTION` 并停止；当前状态为 `PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_3`，未生成 `VERIFIED_PRE_GOLD`。
9. 现有 commit `9207bd78eea44d2ea3291fe9b6748526969a3224` 中的 channel audit/decision/ranking/policy 必须保留为失败证据，状态为 `UNVERIFIED_INVALID_FOR_GOLD`，不得覆盖、删除、解释或用于 Gold。
10. Amendment 3 已获 implementation/synthetic-only 批准，绑定审批包提交 `42747507d6f37c3d5713949de443311b35262a2d` 与失败审计提交 `8b43de72418ccda85af3015f758c39bce9d31411`。仅允许 effective-K 协议、checkpoint、verifier、synthetic runner 绑定和测试修订。
11. Amendment 3 implementation baseline 为 `stage4b_u1_v2_3`；independent verifier 必须使用 `K_q=min(20,|C_q|)`、`P_q=min(10,K_q)` 并执行候选池、长度、唯一性、成员、前缀、插入与 final selector 硬门。synthetic suite 为原 24 项加 9 项 effective-K hardening，共 33 项。
12. 禁止读取 official development/source audit/official ranking，禁止重跑 official preflight/channel/controller/cache/verifier/evaluator；synthetic hardening 完成并推送后必须停止并重新申请 official pre-Gold 恢复批准。
13. fresh ID-bound cache 与旧 Stage4A-R2 cache 必须原样保留；U1-D Gold evaluation、任何 U1-D 指标读取或解释、U1-D 晋级、reservation 和 Stage3B 全部锁定。

## GitHub 与文档

- 协议/代码提交必须先于数据提取和指标读取。
- 结果提交必须包含独立验证、Roadmap 和 README 状态更新。
- 不提交 raw/processed 数据、embedding、模型缓存或本地临时文件。
- README 保持当前状态；完整历史由 `docs/ROADMAP.md`、`docs/*PROTOCOL*` 和 `reports/` 承载。
