# HyperGranular-RAG 项目约束

本仓库继承 `E:\SCIENCE\AGENTS.md` 的全部规则；冲突时采用更严格的规则。

## 1. 项目范围

- 仓库：`E:\SCIENCE\HyperGranular-RAG`
- GitHub：`https://github.com/lljjcc426/HyperGranular-RAG.git`
- 登记数据根目录：`E:\SCIENCE\超粒球RAG_数据`
- 研究范围：粒球/超边多跳检索、静态 q25 protected insertion、已关闭的 U1/candidate-controller 审计线、独立验证，以及 Stage4E 端到端答案质量评估。
- 禁止读取其他项目会话、全局 Codex memory 或项目外中间产物。

## 2. 当前权威入口

- 当前项目状态：`README.md`
- 文档导航：`docs/INDEX.md`
- 当前复现边界：`docs/REPRODUCIBILITY.md`
- 完整研究时间线：`docs/ROADMAP.md`
- 当前 Stage4E 协议：`docs/STAGE4E_STATIC_HGRAG_E2E_ANSWER_QUALITY_LEVEL_A_PROTOCOL.md`
- Stage4D 关闭声明：`docs/STAGE4D_CMA_CLOSURE.md`
- 已完成 Stage4D 协议：`docs/STAGE4D_CANDIDATE_MARGINAL_UTILITY_AUDIT_PROTOCOL.md`
- 已完成诊断协议：`docs/STAGE4C_U1_FAILURE_MECHANISM_AUDIT_PROTOCOL.md`
- 冻结 Stage4B 执行协议：`docs/STAGE4B_U1_SIMPLIFIED_EXECUTION_PROTOCOL_V1.md`
- 冻结配置：`configs/stage4b_u1_d_official.json`
- Gold 授权与执行配置：`configs/stage4b_u1_d_gold_evaluation.json`
- 当前诊断报告：`reports/超粒球RAG_Stage4D_CMA候选边际效用归因审计报告.md`

历史 Amendment、Approval、Review、Hard Failure 和 PowerShell 执行文件是不可改写的证据，不是当前日常执行规则。不得从历史文件恢复已退役的 launcher、remote gate、observer、stderr framing 或 nested PRE 链。

## 3. 当前科研状态

```text
LEVEL_B_IMPLEMENTATION_ACCEPTED
VERIFIED_PRE_GOLD_COMMITTED
GOLD_EVALUATION_COMPLETED
VERIFIED_POST_GOLD
STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED
STAGE4C_U1_FMA_COMPLETED
MECHANISM_EVIDENCE_INCONCLUSIVE
STAGE4D_LEVEL_A_PROTOCOL_ACCEPTED
STAGE4D_IMPLEMENTATION_READY
STAGE4D_SYNTHETIC_TESTS_PASSED
STAGE4D_CHANNEL_A_VERIFIED
STAGE4D_CHANNEL_B_LABELS_VERIFIED
EXISTING_OFFICIAL_PROBE_ARTIFACTS_PROVENANCE_VERIFIED
STAGE4D_PROBE_VERIFIED
STAGE4D_FINAL_VERIFICATION_PASSED
CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE
STAGE4D_CMA_CLOSED
CURRENT_CONTROLLER_BRANCH_FROZEN_CLOSED
NO_ACTIVE_CONTROLLER_DEVELOPMENT
STAGE4E_LEVEL_A_PROTOCOL_ACCEPTED
STAGE4E_INPUT_BINDING_AUTHORIZED
STAGE4E_LEVEL_B_IMPLEMENTATION_AUTHORIZED
STAGE4E_INPUTS_BOUND
STAGE4E_LEVEL_B_IMPLEMENTATION_READY
STAGE4E_SYNTHETIC_TESTS_PASSED
STAGE4E_INPUT_CHANNELS_VERIFIED
STAGE4E_OFFICIAL_EXECUTION_NOT_AUTHORIZED
RESERVATION_REQUIRES_PAUSE
U2_NOT_AUTHORIZED
SCIENTIFIC_SEMANTIC_CHANGE_REQUIRES_PAUSE
```

- Controller 三工件提交：`9357c157217f85008fa93df07d321a2f4c6a2bc1`。
- `VERIFIED_PRE_GOLD` 提交：`83d172bc89efbb31782eee308bac5293aa24457b`。
- Gold 结果提交：`c06761f0c55cbeecf75564211a59f4540cfbae06`。
- Summary 原始字节修复提交：`b500184bc581d73a381de65c32cf3b72e9758cc9`；本地/index/commit/GitHub 四方均为 7,662 bytes / `7F82056F...7F89DE`。
- Evaluation summary SHA-256：`7F82056FB14F9D8D73E668A82CB5304B28385E62A01C428599F23260AB7F89DE`。
- `VERIFIED_POST_GOLD` SHA-256：`44BF3E8B0B036958633E237186A458B13090D8073F587657D831656FB7720ECD`。
- 主运行与确定性复跑同字节，独立验证通过；6 项 development 晋级门仅通过 2 项。
- 冻结 evaluator/validator 未生成或核对协议要求的 question-type 区间；不得事后选取区间算法补算或据类型点估计形成 efficacy 主张。
- 这是当前冻结 U1-D controller 的有效负结果，不等于 HyperGranular-RAG 整体无效，不授权 reservation，也不允许在同一 development 上调整后重跑。
- Stage4C 协议提交：`2e925063175a6402a21ade3fc0ab4a27faaa6dd7`；实现提交：`1bbe8a571d4e0c4aa965b4f0fa71b1de5901b2a7`。
- Stage4C 仅形成 post-Gold 探索性 `CAUTION` 证据；raw U1 score 方向错误且 all-on/off 受限，但固定 OOF panels 未达到稳定门，不授权 U2 或任何新 efficacy 主张。
- Stage4D-CMA Level A 协议与核心 implementation/synthetic 提交：`b4dfa52d0a38409dfc19444d21beec59606088e1`；guarded artifact transaction 补全提交：`730daea1350616bfdcb6a11832b361c4d574d985`；固定环境为 CPython 3.12.0 / scikit-learn 1.9.0，定向 suite 为 16/16 PASS。
- Stage4D official Channel A、Channel B、固定 probe、bounded provenance audit 与 final verification 均已完成。8,467 个候选和 68,588 条 OOF 预测通过身份、内容、bootstrap 与独立验证；combined Task-C AUROC 为 `0.64310 [0.55520,0.72974]`，最终为 `CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE`。
- 现有 Stage4D transaction 不得重复，probe 三工件不得覆盖；该结果不授权 reservation/Stage3B、U2 或新 candidate controller。
- Stage4D 与当前 controller 线已冻结关闭。Stage4E 是不含 U1/Stage4D model 的静态 Dense-vs-q25 E2E 评价，不得读取 Stage4D labels/probabilities 形成 ranking。
- Stage4E Level A 已接受；HotpotQA train provenance/通道身份、encoder/generator snapshot、CUDA 环境、config 和 Level B 实现已冻结并通过输入独立验证。仍不允许运行 1,000-query official retrieval/generation/Gold evaluation。

## 4. 科研不可变边界

未经新的 Level A 协议或明确授权，不得修改或事后选择：

- development/reservation 数据边界；
- 候选生成、粒球、超边或 facet；
- Dense/q25 ranking、q25 floor、protect/insert、effective-K；
- U1 输入、ECDF、score、tie-break 或 60% budget；
- 主要终点、统计检验、bootstrap、确定性复跑或晋级门；
- 已冻结 decisions、rankings、policy、`VERIFIED_PRE_GOLD`。
- 已验证的 Gold query audit、evaluation summary、复跑和 `VERIFIED_POST_GOLD` 工件。

Gold 不得进入 controller、索引、候选、排序、过滤或阈值选择。Reservation 和 Stage3B 继续锁定。

Stage4E 中，Gold 还不得进入 blind input、embedding、Dense/q25 ranking、prompt、生成、截断或重试。静态 q25 必须保持 all-query 语义，不得借 Stage4E 重新引入 U1、Stage4D feature panel/model 或动态阈值。

## 5. 授权与暂停

Level B/C 的普通工程工作、测试、文档、提交和推送不逐项暂停，也不建立逐提交审批链。根据变更影响自主完成最小修正、适量测试、必要绑定与 GitHub 同步。

本次获授权的 Gold evaluation 已结束，不得自行再次运行。必须暂停并报告：

1. 准备再次连接或运行 Gold evaluator；
2. 准备读取 reservation 或 Stage3B；
3. 准备改变科学语义、数据边界、终点或统计规则；
4. 发现错误 official 输入/cache、Gold 泄漏、不可信 ranking；
5. 正式输出部分生成且不能可靠回滚，或本地/tracked/remote 工件字节不一致；
6. verifier 无法确认正式工件完整性。
7. 准备首次运行 1,000-query Stage4E official retrieval/generation 或 Stage4E Gold evaluation，而 Level B 绑定与精确命令确认尚未完成。

临时 push/remote visibility、路径、权限、日志、依赖或零正式输出时的普通 preflight 错误默认是 Level C，不自动升级为科研 Hard Failure。

## 6. 测试与执行

- 科学算法变化：完整相关 suite，并按协议执行关键确定性验证。
- Ranking/verifier/schema 变化：定向测试 + 一次完整 `test_stage4b_u1*.py` suite。
- 文档、索引、README、普通路径或日志变化：静态检查即可，不运行算法 suite。
- 禁止为形式性治理重复运行完整 suite。
- 禁止盲目重复未变化的失败命令；先诊断和修正再继续。
- 不自行重新运行已完成的 official pre-Gold transaction。
- 不自行重新运行已完成的 Stage4B-U1-D Gold transaction。
- 不自行重新运行或覆盖已完成的 Stage4D Channel A、Channel B 和 official probe transaction。
- Stage4E Level B 阶段只做 source/model/environment identity binding、实现与 synthetic tests；不运行 1,000-query official retrieval/generation/evaluation。

## 7. GitHub 与文件

- 科研协议、代码、结果、独立验证和阶段状态按单一职责提交并推送 `main`。
- 不提交 raw/processed 数据、embedding、模型、缓存、密钥或临时文件。
- 不改写 Git 历史掩盖失败；失败和负结果保留在 `docs/ROADMAP.md`、历史证据文件与 Git 历史。
- README 保持简洁和当前；详细历史不再追加到 README。
- 新增、修改、移动、归档和删除文件都必须向用户说明。

## 8. 下一科研门

Stage4B-U1、Stage4C、Stage4D 和当前 controller 线均已停止或关闭，不自动创建 U2。当前唯一科研门是 Stage4E-E2E：固定 Dense 与静态 all-query q25、固定生成器，在 new-ID same-domain 边界上评价答案 F1/EM。Level A 与 Level B 绑定已完成；下一边界是首次 official Gold-free retrieval/generation 的精确命令确认。Gold evaluation 只能在 main/rerun 与 pre-Gold 独立验证通过后另行确认。Reservation、Stage3B、再次既有 Gold 执行和任何新 controller 继续锁定。
