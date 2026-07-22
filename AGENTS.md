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
- 当前正式报告：`reports/超粒球RAG_Stage4E_E2E答案质量报告.md`

历史 Amendment、Approval、Review、Hard Failure 和 PowerShell 执行文件是不可改写的证据，不是当前日常执行规则。不得从历史文件恢复已退役的 launcher、remote gate、observer、stderr framing 或 nested PRE 链。

## 3. 当前科研状态

```text
STAGE_LEVEL_AUTHORIZATION_ACTIVE
ONE_RESEARCH_STAGE_ONE_AUTHORIZATION
STEP_LEVEL_APPROVAL_DISABLED
CHANNEL_LEVEL_REAPPROVAL_DISABLED
ENGINEERING_WORK_AUTONOMOUS
STAGE_INTERNAL_EXECUTION_CONTINUOUS
EXCEPTION_BASED_PAUSE_ONLY
SCIENTIFIC_INTEGRITY_CONTROLS_RETAINED
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
STAGE4E_GENERATOR_SELECTION_VERIFIED
STAGE4E_GENERATOR_QWEN_SELECTED
STAGE4E_PRE_GOLD_ARTIFACTS_VERIFIED
STAGE4E_GOLD_EVALUATION_COMPLETED
STAGE4E_FINAL_VERIFICATION_PASS
STATIC_HGRAG_E2E_SUPPORTED
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
- Stage4E 已完成：Qwen2.5-1.5B-Instruct 经冻结选择后成为唯一生成器；1,000-query Gold-free main/rerun、pre-Gold verification、Gold evaluation 和 final verification 均通过。Static q25 相对 Dense 的 answer F1 差为 `+0.01478 [0.00020,0.02988]`，冻结决策为 `STATIC_HGRAG_E2E_SUPPORTED`。
- Stage4E 工件不得覆盖或重跑；该结果限于 HotpotQA same-domain closed distractor，不授权 reservation、Stage3B、U2 或重开 controller。

## 4. 科研不可变边界

未经新的阶段级科学协议/实验卡与授权，不得修改或事后选择：

- development/reservation 数据边界；
- 候选生成、粒球、超边或 facet；
- Dense/q25 ranking、q25 floor、protect/insert、effective-K；
- U1 输入、ECDF、score、tie-break 或 60% budget；
- 主要终点、统计检验、bootstrap、确定性复跑或晋级门；
- 已冻结 decisions、rankings、policy、`VERIFIED_PRE_GOLD`。
- 已验证的 Gold query audit、evaluation summary、复跑和 `VERIFIED_POST_GOLD` 工件。

Gold 不得进入 controller、索引、候选、排序、过滤或阈值选择。Reservation 和 Stage3B 继续锁定。

Stage4E 中，Gold 还不得进入 blind input、embedding、Dense/q25 ranking、prompt、生成、截断或重试。静态 q25 必须保持 all-query 语义，不得借 Stage4E 重新引入 U1、Stage4D feature panel/model 或动态阈值。
已冻结的 Stage4E rankings、predictions、prompt audits、query audit、evaluation summary、scientific decision 与 final verification 也属于不可覆盖工件。

## 5. 授权与暂停

本节是 HyperGranular-RAG 项目长期、全局的现行治理基线，适用于当前及未来全部科研阶段，不是单次任务或单一 Stage 的临时规则，也不因阶段切换而失效。一个已定义的科研阶段只进行一次阶段级授权。除非实验卡或用户明确排除，授权默认连续覆盖：协议/实验卡定稿、实现、测试、所有预定义 Channel、所有预定义数据读取（包括已在实验卡中授权的 Gold）、正式运行、固定统计或 probe、独立 verifier、确定性复跑、报告、状态文档、Git 提交/推送和远端一致性验证。不得因切换脚本、通道、命令、工件或提交而重复请求批准。

Channel A/Channel B、Gold-free/Gold-only 的代码、输入、依赖和工件仍须严格隔离；技术隔离不等于审批隔离。当前阶段授权若覆盖两条通道，前一通道及完整性门通过后直接进入后一通道。精确 CLI、参数、环境变量、输出路径和依赖版本属于冻结执行细节，不是独立科学审批对象。

全局治理生效不等于自动扩大任何既有阶段明确排除的科学范围。Stage4E 已在 2026-07-22 的用户扩展授权下连续完成；该授权不延伸到新的数据集、full-wiki、reservation、Stage3B、U2、subgroup 确认或新 controller。当前与未来阶段一律按本节判断授权覆盖与暂停边界。

阶段内默认自主完成：代码编写/重构、单元/集成/synthetic tests、普通依赖安装与固定、路径/CLI/编码/序列化/环境/运行时修复、已授权 Gold-free 或 Gold evaluator 事务、固定统计/probe、rerun、verifier、schema/SHA/身份/泄漏检查、报告与五个治理入口更新，以及 commit、push 和远端字节验证。普通工程异常按“定位 → 判断是否改变科学语义 → 最小修复 → 必要测试 → 记录 → 继续”处理，不升级为新的科学审核。

只在以下四类情形暂停并请求一次集中决策：

1. 启动新的科学问题、Stage、controller 或主要假设；
2. 修改已冻结科学语义，包括候选/标签/Gold 用法/主要特征或模型/数据切分/主要终点/晋级门/停止规则/确认性统计；
3. 使用当前阶段授权未覆盖的新证据源，包括新的独立测试、reservation、Stage3B、外部 benchmark 或未登记 Gold；
4. 出现严重科研完整性异常，包括 Gold、question-type 或身份泄漏，输入/Gold SHA 不一致，ranking/candidate trace/关键工件不可重建，main/rerun 不一致，需要改变科学语义才能修复的 verifier 失败，正式结果被覆盖、部分生成或不可恢复，或必须修改冻结正式结论。

除此之外不得暂停。临时 push/remote visibility、路径、权限、日志、依赖、PowerShell/环境变量包装、普通性能问题或零正式输出的 preflight 错误均属工程问题。

取消逐命令、逐脚本、逐文件、逐提交、逐通道审批；取消实现后的重复科学审核、synthetic tests 后的单独授权、正式运行前复述固定授权语句、普通修复 Amendment、同阶段重复 review request、逐次运行 approval record 和嵌套审批链。不得只为记录一次授权新增治理文档。历史 Amendment/Approval/Review 链仅用于证据追溯，不构成现行执行规则。

新科学阶段默认使用 1–3 页轻量实验卡，固定研究问题、假设、数据边界、主要方法、主要终点、成功/停止/证据不足规则、Gold/独立测试/reservation 边界和禁止事项。只有高风险确认性实验、一次性独立 reservation、复杂多源泄漏风险、多主要终点或不可逆外部提交才使用长协议。

## 6. 测试与执行

- 科学算法变化：完整相关 suite，并按协议执行关键确定性验证。
- Ranking/verifier/schema 变化：定向测试 + 一次完整 `test_stage4b_u1*.py` suite。
- 文档、索引、README、普通路径或日志变化：静态检查即可，不运行算法 suite。
- 禁止为形式性治理重复运行完整 suite。
- 禁止盲目重复未变化的失败命令；先诊断和修正再继续。
- 不自行重新运行已完成的 official pre-Gold transaction。
- 不自行重新运行已完成的 Stage4B-U1-D Gold transaction。
- 不自行重新运行或覆盖已完成的 Stage4D Channel A、Channel B 和 official probe transaction。
- 不自行重新运行或覆盖已完成的 Stage4E Gold-free、Gold evaluation 和 final verification transaction。

## 7. GitHub 与文件

- 科研协议、代码、结果、独立验证和阶段状态按单一职责提交并推送 `main`。
- 不提交 raw/processed 数据、embedding、模型、缓存、密钥或临时文件。
- 不改写 Git 历史掩盖失败；失败和负结果保留在 `docs/ROADMAP.md`、历史证据文件与 Git 历史。
- README 保持简洁和当前；详细历史不再追加到 README。
- 新增、修改、移动、归档和删除文件都必须向用户说明。

## 8. 下一科研门

Stage4B-U1、Stage4C、Stage4D 和当前 controller 线均已停止或关闭，不自动创建 U2。Stage4E-E2E 也已完成并冻结，支持静态 all-query q25 在当前 HotpotQA same-domain closed distractor 边界上改善 answer F1。下一科研门必须是新定义的科学问题；跨数据集复制、full-wiki 验证、subgroup/机制确认、其他生成器复现或任何新 controller 均需新的轻量实验卡和阶段授权。Reservation、Stage3B、既有 Gold 重跑和 U2 继续锁定。
