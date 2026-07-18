# 文档索引

本索引将当前科研入口、可复现证据和历史治理材料分开。日常工作优先阅读“当前有效”部分；历史文件用于追溯，不自动构成当前执行门。

## 当前有效

| 文件 | 用途 |
|---|---|
| [README](../README.md) | 项目定位、当前研究问题、证据等级和下一步 |
| [项目 AGENTS](../AGENTS.md) | 当前治理、暂停边界和 GitHub 规则 |
| [REPRODUCIBILITY](REPRODUCIBILITY.md) | 当前环境、冻结 SHA、工件与复现边界 |
| [ROADMAP](ROADMAP.md) | 完整研究时间线与阶段状态 |
| [Simplified execution protocol](STAGE4B_U1_SIMPLIFIED_EXECUTION_PROTOCOL_V1.md) | Stage4B-U1-D 科学与 pre-Gold 执行合同 |
| [Official config](../configs/stage4b_u1_d_official.json) | 冻结输入、代码、cache、参数和输出绑定 |
| [Gold evaluation config](../configs/stage4b_u1_d_gold_evaluation.json) | 已授权 Gold 输入、命令、复跑、验证和停止规则绑定 |
| [Stage4B-U1-D 统计验证报告](../reports/超粒球RAG_Stage4B_U1_D_Gold评估与统计验证报告.md) | Gold 结果、门判定、复现与 11 类谬误扫描 |

## 当前正式工件

| 文件 | 状态 |
|---|---|
| [decisions](../results/stage4b_u1_d_official_dev4500_simplified_v1_decisions.jsonl) | 已冻结 |
| [rankings](../results/stage4b_u1_d_official_dev4500_simplified_v1_rankings.jsonl) | 已冻结 |
| [policy](../results/stage4b_u1_d_official_dev4500_simplified_v1_policy.json) | 已冻结 |
| [VERIFIED_PRE_GOLD](../results/stage4b_u1_d_official_dev4500_simplified_v1_verified_pre_gold.json) | 独立验证通过 |
| [Gold query audit](../results/stage4b_u1_d_official_dev4500_simplified_v1_query_audit.jsonl) | 4,500 queries；已提交 |
| [Gold evaluation summary](../results/stage4b_u1_d_official_dev4500_simplified_v1_evaluation_summary.json) | development 门判定：失败 |
| [deterministic rerun summary](../results/stage4b_u1_d_official_dev4500_simplified_v1_evaluation_summary_rerun.json) | 与主摘要同字节 |
| [VERIFIED_POST_GOLD](../results/stage4b_u1_d_official_dev4500_simplified_v1_verified_post_gold.json) | 独立重算与复跑核验通过 |

结果状态为 `STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED`。结果生成提交为 `c06761f0c55cbeecf75564211a59f4540cfbae06`，正式 summary 原始字节修复提交为 `b500184bc581d73a381de65c32cf3b72e9758cc9`。

## 科学设计与阶段证据

- Stage4A-R2 的样本、映射、估计和验证协议保留在对应 `STAGE4A_R2_*` 文档中。
- Stage4B-U1 的科学设计源为 `STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md`。
- 当前 simplified 协议是在不改变科学语义的前提下替代旧多层 PowerShell 执行链。
- 方法审计见 [PRIOR_STAGE_METHOD_AUDIT](PRIOR_STAGE_METHOD_AUDIT.md)。
- 阶段性结果说明位于 `reports/`。

## 历史治理证据

以下文件族继续保留原路径，以避免破坏既有 SHA、交叉引用和科研轨迹：

- `STAGE4B_U1_PREGOLD_AMENDMENT_*`
- `STAGE4B_U1_PREGOLD_HARD_FAILURE_*`
- `STAGE4B_U1_*_REVIEW_*`
- `STAGE4B_U1_*_APPROVAL_*`
- 旧 PowerShell launcher、remote gate、observer、command-line capture 与 nested PRE 相关源码/审计。

这些材料记录了失败、修订和治理演化，但不应被用作当前命令入口，也不得据此恢复已经退役的逐步骤审批链。

## 归档快照

仓库整理前的长入口文档按原字节归档于 [archive](archive/README.md)：

- 旧长版 README；
- 旧累计式项目 AGENTS；
- 旧累计式 REPRODUCIBILITY。

归档快照中的链接按原文件位置书写，可能不适合作为当前导航；当前链接以本索引为准。

## 文档维护规则

- README 只保留当前状态、研究问题、证据等级、方法概览、限制和下一步。
- ROADMAP 承载按时间追加的完整阶段历史。
- REPRODUCIBILITY 只保留当前可执行/可核验入口；旧命令进入归档。
- 不为每次普通测试、push 或 Level C 问题创建独立审批文档。
- 科学协议、失败证据和正式结果不删除、不覆盖、不改写。
- 新增历史证据时优先更新 ROADMAP 和本索引，不向 README 堆叠全过程。

## 当前下一步

当前状态为 `VERIFIED_POST_GOLD` 与 `STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED`。后续应先形成新的研究问题和预注册协议；不得在同一 development 上事后调整 U1 并重跑，reservation 与 Stage3B 继续锁定。
