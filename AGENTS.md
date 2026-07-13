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
12. v2.3 official-resumption package commit `dbb4e057405069aceda5a7c5d88d9d39a4d14775` 已被审查退回，状态为 `RETURN_FOR_PROTOCOL_AND_CACHE_FAIL_CLOSED_REVISION`，不得据此执行 official preflight 或后续命令。
13. Amendment 4 已获 implementation/synthetic-only 批准，绑定 package `e5a0e2187e770c9d7b9e9a85a6b8e91067ed2af1`、returned package `dbb4e057405069aceda5a7c5d88d9d39a4d14775` 与 baseline implementation `a1d9ea0c517fcbad1ef27e78e760738d5c04d8b3`。仅允许 checkpoint、cache fail-closed、pending outputs、runner governance binding、十路径 registry、测试和 evidence 修订。
14. Amendment 4 implementation baseline 为 `stage4b_u1_v2_3_1`：formal controller 强制 require-existing/no-build、cache 前后 fingerprint、OS-temp pending outputs、v2.2 decisions/rankings/policy 等价门和 exclusive promotion rollback；runner 支持登记治理文件绑定；十路径以 Amendment 4 manifest 为唯一 registry。
15. synthetic suite 保留原 33 项并新增 17 项 cache/governance hardening，共 50 项。最终 evidence 必须在本条及全部绑定文件的稳定字节上连续运行两次，全部通过且字节一致。
16. Amendment 4 测试只能使用 synthetic cache；禁止读取 official development/source audit/official ranking/official cache，禁止运行 official preflight/channel/controller/cache audit/verifier/evaluator。
17. fresh ID-bound cache 与旧 Stage4A-R2 cache 必须原样保留；U1-D Gold evaluation、任何 U1-D 指标读取或解释、U1-D 晋级、reservation 和 Stage3B 全部锁定。
18. Stage4B-U1-D v2.3.1 official pre-Gold 恢复已获批准，严格绑定恢复审批包提交 `e76c921454697d1784b0d76a9d9677113051f0f6` 与实现提交 `34349c70ee24b8240fd169393134d4280968b790`。批准决定为 `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_APPROVAL_DECISION.md`。
19. 唯一允许顺序为：批准治理提交推送 -> 两次 50 项 governance-bound synthetic rebinding 并提交推送 -> 一次 formal preflight -> 一次 versioned channel -> 一次 require-existing controller -> 工件提交推送 -> 一次 independent verifier -> 推送 `VERIFIED_PRE_GOLD` 后立即停止。任一硬失败不得自动重跑。
20. 本批准不授权 Gold evaluation、U1-D 指标读取或解释、U1-D 结论、reservation、Stage3B、实现/参数变更、cache 写入或 v2.2 失败工件改写。
21. v2.3.1 唯一一次 formal preflight 与唯一一次 channel preparation 均通过；唯一一次 require-existing controller 在 pending decisions 的 v2.2 字节等价门触发 `HARD_FAILURE_V2_3_1_DECISIONS_EQUIVALENCE`。当前状态为 `PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_4`。
22. Hard Failure 4 未提升 decisions/rankings/policy，未生成 controller execution audit 或 `VERIFIED_PRE_GOLD`，fresh/legacy cache 与 v2.2 工件 hash 均未变化。禁止自动重跑、运行 verifier 或诊断 official ranking 内容；后续必须先形成并批准新的审查/Amendment。
23. Amendment 5A implementation/synthetic-only 已获批准，绑定 package `81d8c34f1cf2539a4c0b81c6148047bc666e2f82` 及 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_APPROVAL_DECISION.md` 中六个历史提交。只允许 decisions comparator、synthetic-only temp capture、至少 24 项新增测试、双次 deterministic evidence、implementation audit 和 5B 审批包。
24. 5A 禁止读取 official units/queries/source audit/cache/decisions/rankings，禁止 official comparator/capture、controller、verifier、evaluator、Gold、reservation、Stage3B 和 byte-equivalence 放宽。测试必须主动拦截这些路径与 ranking/policy 调用。
25. 5A 完成后状态只能为 `AMENDMENT_5A_SYNTHETICALLY_VERIFIED` 且 official diagnosis/controller rerun/verifier 均未批准；5B package 推送后必须立即停止。

## GitHub 与文档

- 协议/代码提交必须先于数据提取和指标读取。
- 结果提交必须包含独立验证、Roadmap 和 README 状态更新。
- 不提交 raw/processed 数据、embedding、模型缓存或本地临时文件。
- README 保持当前状态；完整历史由 `docs/ROADMAP.md`、`docs/*PROTOCOL*` 和 `reports/` 承载。
