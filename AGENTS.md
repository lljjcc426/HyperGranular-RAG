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
8. Stage4B-U1-D v2.1 的原 pre-Gold 批准已在 `HARD_FAILURE_EMBEDDING_CACHE_METADATA` 处停止；未运行 official channel/controller，当前状态为 `PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_1`。
9. 在 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_1_DRAFT.md` 获用户批准、提交并推送前，official channel、controller、verifier、U1-D Gold evaluation、任何 U1-D 指标读取或解释、reservation 和 Stage3B 全部锁定；不得自动重跑、迁移或重建 embedding cache。

## GitHub 与文档

- 协议/代码提交必须先于数据提取和指标读取。
- 结果提交必须包含独立验证、Roadmap 和 README 状态更新。
- 不提交 raw/processed 数据、embedding、模型缓存或本地临时文件。
- README 保持当前状态；完整历史由 `docs/ROADMAP.md`、`docs/*PROTOCOL*` 和 `reports/` 承载。
