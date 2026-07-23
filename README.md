# HyperGranular-RAG

以自适应粒球组织知识单元、以 query-aware 超边补充跨粒球关系，并通过受保护插入控制检索扩展的多跳 RAG 研究仓库。

## 当前状态

| 项目 | 当前事实 |
|---|---|
| 研究阶段 | Stage4E、Stage4F-XDR 与 Stage4G-GTR 均已完成、验证并冻结 |
| 状态 | `STAGE4G_GTR_FINAL_VERIFICATION_PASS`；`GENERATOR_TRANSFER_INCONCLUSIVE` |
| 已用数据边界 | 2Wiki development 4,500；HotpotQA train 1,000；MuSiQue train 新 ID 3,000 |
| 当前证据 | Qwen 下的静态 q25 answer-F1 增益已在两个冻结 closed-candidate 数据集上得到支持；一个额外 Gemma mobile-QAT 配置的迁移复制结果不确定 |
| Gold | 仅在 Gold-free main/rerun 与 pre-Gold verification 后使用；未进入检索、prompt、生成或排序 |
| Reservation / Stage3B | `KEEP_LOCKED` |

Stage4E 正式结果：

- 在 RTX 4060 Laptop 8GB、固定短答案 RAG prompt、4,096-token 上限和可实际部署格式下，Qwen2.5-1.5B-Instruct FP16 在冻结 200-query development 上取得更高 F1/EM 及更低时间/显存，并按预登记规则成为唯一 Stage4E 生成器；Gemma 4 E2B 使用官方 mobile-QAT，结果不作纯架构解释；
- Static q25 answer F1 为 `0.43628`，Dense 为 `0.42150`，成对差为 `+0.01478 [0.00020, 0.02988]`；
- answer EM 差为 `+0.01000 [-0.00500, 0.02500]`，通过预定 EM non-inferiority guard；
- retrieval CR@20 从 `0.737` 提高到 `0.798`，ER@20 从 `0.87860` 提高到 `0.90818`；
- main/rerun predictions 与 prompt audits 同字节，pre-Gold 和 post-Gold 独立验证均通过；
- 冻结决策为 `STATIC_HGRAG_E2E_SUPPORTED`，但边界仍限于 HotpotQA same-domain closed distractor。

Stage4F-XDR 跨数据集复制结果：

- MuSiQue-Answerable train 的 3,000 个 ID-only hash-selected query 与历史 MuSiQue IDs overlap 0；
- Static q25 / Dense answer F1 为 `0.14735/0.13595`，paired delta 为 `+0.01140 [0.00450,0.01835]`；
- answer EM delta 为 `+0.01000 [0.00333,0.01667]`；supporting-paragraph CR@20 从 `0.589` 提高到 `0.650`；
- 12,000 次生成均无失败，main/rerun predictions 与 prompt audits 同字节；pre-Gold 和 final independent verification 均通过；
- 冻结决策为 `STATIC_HGRAG_XDR_SUPPORTED`。这是跨数据集 closed-candidate 复制，不是 full-wiki、open-domain 或跨生成器确认。

Stage4G-GTR 生成器迁移复制结果：

- 唯一新因素为事前绑定的 `google/gemma-4-E2B-it-qat-mobile-transformers@dd693ff...` 官方 mobile-QAT 配置；Stage4E/4F 的 blind inputs、Dense/static-q25 rankings、prompt 与 evaluator 均直接复用；
- HotpotQA answer-F1 delta 为 `+0.01265 [-0.00220,0.02744]`，MuSiQue 为 `-0.00232 [-0.00685,0.00208]`；
- 数据集等权 F1 delta 为 `+0.00516 [-0.00262,0.01295]`，低于 `+0.010` 支持门且区间跨 0；没有触发预注册负向门；
- 正式 main 8,000 calls 零失败；预哈希分层 subset 400 calls 与 main 精确复现；Gold 隔离、4,000-query scoring、10,000 bootstrap、interaction 和 decision 均通过独立重建；
- 冻结决策为 `GENERATOR_TRANSFER_INCONCLUSIVE`。Gemma 的架构与 mobile-QAT 效应不可分离，不能解释为纯架构比较或普遍 generator robustness。

此前 U1-D Gold 结果：

- U1 将 q25 插入量从 7,260 降至 4,354，减少 `40.0275%`；
- gain retention 为 `47/94=0.5000`，harm retention 为 `53/69=0.7681`，retention gap 为 `-0.2681`；
- U1 CR@20 为 `0.77089`，相对 Dense 为 `-0.00133`，相对 q25 为 `-0.00689`；
- 6 项 development 晋级门通过 2 项、失败 4 项；按冻结停止规则关闭 U1 分支；
- 主运行与预注册复跑同字节，独立验证对 4,500 queries 的重算全部通过；
- 结果生成提交为 `c06761f0c55cbeecf75564211a59f4540cfbae06`；正式 summary 原始字节修复提交为 `b500184bc581d73a381de65c32cf3b72e9758cc9`。

这是当前冻结 U1-D controller 的可复现 development 负结果：U1-D 当前冻结形式未获得支持。它不是执行失败，也不能推导 HyperGranular-RAG 整体无效；它不支持 U1 优于 Dense、保留更多 gain than harm、进入 reservation 或具备跨数据集泛化能力。

## 当前研究问题

Stage4A-R2 已确认：q25 超边扩展在官方 2WikiMultiHopQA 上存在可测的 query-level gain/harm 事件，但平均 CR 提升尚未确认，且 query 类型存在明显异质性。

Stage4B-U1-D 回答的问题是：在不使用 Gold 参与检索决策的前提下，基于无标签边界不确定性的 U1 controller，能否减少 q25 插入成本，同时保留足够的检索收益并控制伤害。冻结实验的答案是否定的：成本门通过，但选择性机制和 CR@20 门未通过。

Stage4C-U1-FMA 进一步审计其失败机制：raw U1 score 对 GAIN-vs-HARM 的 AUROC 为 `0.39269 [0.30558, 0.48150]`，92/94 个 gain query 为 mixed gain/noise，69/69 个 harm query 为 displacement harm；但固定 OOF panels 均未达到稳定信号门，最终决策为 `MECHANISM_EVIDENCE_INCONCLUSIVE`。

Stage4D-CMA 将问题下沉到 candidate 级：8,467 个 eligible candidates 经 standardized first-slot insertion、`LOO_NO_BACKFILL` 和 `LOO_WITH_BACKFILL` 归因后，固定 Task-C combined panel 的 AUROC 为 `0.64310 [0.55520, 0.72974]`、AP 为 `0.72198`。它存在部分符号信号，但 AUROC 未达到 `0.65` 且 Brier 未优于 prevalence baseline，最终为 `CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE`。

Stage4D 和当前 controller 分支已经冻结关闭。Stage4E-E2E 在此前未读的 HotpotQA train ID-hash 边界上支持静态 q25 改善 answer F1；Stage4F-XDR 又在 MuSiQue-Answerable train 新 ID、同一 encoder/Qwen/prompt 与两条静态检索臂上通过冻结跨数据集复制门。Stage4G-GTR 在一个额外、事前指定的 Gemma mobile-QAT 配置下得到 `GENERATOR_TRANSFER_INCONCLUSIVE`：HotpotQA 保持正向点估计，MuSiQue 轻微负向，数据集等权联合支持门未通过且负向门也未触发。下一科研问题尚未定义，不能把现有结果自动扩展到 full-wiki、open-domain、普遍生成器鲁棒性或 controller。

## 冻结方法边界

- Dense Top-10 受保护；最终 effective-K 为 `K_q=min(20, |C_q|)`。
- q25 floor：`0.1957079917192459`。
- 每查询最多插入 4 个 q25 单元。
- Stage4E proposed static arm 对所有 query 直接使用 q25 ranking，不调用 controller。
- U1 score 使用四项无标签 ECDF-midrank 输入及冻结 tie-break。
- 全局使用 60% planned-insert ordered-prefix budget。
- Controller 不接收 Gold、reservation 或 Stage3B 输入。
- Gold evaluator 与 controller 分离；本次只在用户明确授权后连接冻结 Gold map。

完整语义见 [Stage4B-U1 simplified execution protocol](docs/STAGE4B_U1_SIMPLIFIED_EXECUTION_PROTOCOL_V1.md)。

## 证据等级

| 阶段 | 证据等级 | 保留结论 |
|---|---|---|
| Stage2F | 有限内部独立验证 | 主 CR@10 gate 失败；保留窄范围 q25/Top-20 证据 |
| Stage2G | 有效负结果 | boundary-only 规则不受支持 |
| Stage3A | 失败的预注册开发 | 稀疏事件触发 fallback；Stage3B 未开放 |
| Stage4A-R2 | 官方内部验证完成 | 事件率精度达标；平均 CR 提升未确认；异质性明显 |
| Stage4B-U1-D | development Gold 评估与独立验证完成 | 资源门单项通过，但联合晋级门失败；U1 分支停止 |
| Stage4C-U1-FMA | post-Gold 探索性诊断，`CAUTION` | query-level score 方向错误且 all-on/off 受限；不足以授权 U2 |
| Stage4D-CMA | post-Gold exploratory official audit，`CAUTION`；已关闭 | candidate-level 部分信号未过联合晋级门；不授权 U2 |
| Stage4E-E2E | new-ID same-domain official transaction；独立验证完成 | static q25 answer F1 `+0.01478 [0.00020, 0.02988]`；`STATIC_HGRAG_E2E_SUPPORTED` |
| Stage4F-XDR | MuSiQue cross-dataset replication；独立验证完成 | answer F1 `+0.01140 [0.00450,0.01835]`；`STATIC_HGRAG_XDR_SUPPORTED` |
| Stage4G-GTR | one-additional-generator controlled replication；独立验证完成 | equal-weight F1 `+0.00516 [-0.00262,0.01295]`；`GENERATOR_TRANSFER_INCONCLUSIVE` |

完整研究轨迹见 [ROADMAP](docs/ROADMAP.md) 和 [文档索引](docs/INDEX.md)。

## 数据与来源边界

- 官方外部数据：2WikiMultiHopQA `data_ids_april7.zip`，来源和 SHA 已冻结。
- Stage4B-U1-D development：4,500 queries / 143,820 units。
- Gold 仅由已授权 evaluator 在 ranking 冻结后使用，未进入索引、候选、排序、过滤或 controller。
- Reservation 仅保留登记的 ID 摘要边界，不读取内容、embedding 或指标。
- Stage4E boundary 是 HotpotQA `hotpot_train_v1.1.json` 的确定性 1,000-query 样本；source 和三个隔离通道已冻结且历史 ID 重叠为 0；正式结果与独立验证已提交。
- Stage4F boundary 是官方 MuSiQue-Answerable v1.0 train 的确定性 3,000-query 样本；与历史 MuSiQue dev 1,000 ID 交集为 0，A/B/C、正式结果与 final verification 已冻结。
- Stage4G 不建立新数据边界；它只在上述两个冻结边界和 rankings 上更换为唯一事前绑定的 Gemma mobile-QAT 生成器，main、subset rerun、Gold evaluation 与 final verification 已冻结。
- Raw data、processed corpus、embedding cache、模型和密钥不进入 Git。

## 仓库结构

```text
AGENTS.md          当前项目约束与强制暂停边界
configs/           冻结执行配置
docs/              当前协议、索引、路线图与历史证据
reports/           阶段性科研报告
results/           可提交的审计、汇总与冻结工件
scripts/           数据、检索、controller、验证和评估脚本
tests/             研究代码回归测试
paper/             论文结构、证据主张台账与待补材料
```

日常阅读从 [docs/INDEX.md](docs/INDEX.md) 开始。历史 Amendment、Hard Failure 和 PowerShell 边界材料保留用于追溯，但不再是当前执行入口。

## 复现

当前环境、冻结 SHA、Gold 结果与复现边界见 [REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md)。主要当前文件：

- [Gold authorization config](configs/stage4b_u1_d_gold_evaluation.json)
- [evaluation summary](results/stage4b_u1_d_official_dev4500_simplified_v1_evaluation_summary.json)
- [VERIFIED_POST_GOLD](results/stage4b_u1_d_official_dev4500_simplified_v1_verified_post_gold.json)
- [统计验证报告](reports/超粒球RAG_Stage4B_U1_D_Gold评估与统计验证报告.md)
- [Stage4C 诊断协议](docs/STAGE4C_U1_FAILURE_MECHANISM_AUDIT_PROTOCOL.md)
- [Stage4C summary](results/stage4c_u1_fma_summary.json)
- [Stage4C 失败机制诊断报告](reports/超粒球RAG_Stage4C_U1失败机制诊断报告.md)
- [Stage4D-CMA Level A 协议](docs/STAGE4D_CANDIDATE_MARGINAL_UTILITY_AUDIT_PROTOCOL.md)
- [Stage4D 固定依赖](requirements-stage4d.txt)
- [Stage4D final verification](results/stage4d_cma_verified_final.json)
- [Stage4D 候选边际效用归因报告](reports/超粒球RAG_Stage4D_CMA候选边际效用归因审计报告.md)
- [Stage4D 关闭声明](docs/STAGE4D_CMA_CLOSURE.md)
- [Stage4E-E2E Level A 协议](docs/STAGE4E_STATIC_HGRAG_E2E_ANSWER_QUALITY_LEVEL_A_PROTOCOL.md)
- [Stage4E official config](configs/stage4e_e2e_official_train1000_v1.json)
- [Stage4E input manifest](results/stage4e_e2e_official_train1000_v1_input_manifest.json)
- [Stage4E model snapshot manifest](results/stage4e_e2e_model_snapshot_manifest.json)
- [Stage4E environment manifest](results/stage4e_e2e_environment_manifest.json)
- [Stage4E Level B 实现报告](docs/STAGE4E_E2E_LEVEL_B_IMPLEMENTATION_REPORT.md)
- [Stage4E 生成模型选择报告](reports/超粒球RAG_Stage4E生成模型选择报告.md)
- [Stage4E E2E 答案质量报告](reports/超粒球RAG_Stage4E_E2E答案质量报告.md)
- [Stage4E final verification](results/stage4e_e2e_official_train1000_v1_final_verification.json)
- [Stage4F-XDR 实验卡](docs/STAGE4F_XDR_EXPERIMENT_CARD.md)
- [Stage4F official config](configs/stage4f_xdr_official.json)
- [Stage4F input verification](results/stage4f_xdr_musique_train3000_v1_verified_input.json)
- [Stage4F evaluation summary](results/stage4f_xdr_musique_train3000_v1_evaluation_summary.json)
- [Stage4F final verification](results/stage4f_xdr_musique_train3000_v1_final_verification.json)
- [Stage4F 跨数据集复制报告](reports/超粒球RAG_Stage4F_XDR跨数据集复制报告.md)
- [Stage4G-GTR 实验卡](docs/STAGE4G_GTR_EXPERIMENT_CARD.md)
- [Stage4G official config](configs/stage4g_gtr_official.json)
- [Stage4G pre-Gold verification](results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_verified_pregold.json)
- [Stage4G dataset summaries](results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_dataset_summaries.json)
- [Stage4G equal-weight summary](results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_equal_weight_summary.json)
- [Stage4G final verification](results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_final_verification.json)
- [Stage4G 生成器迁移复制报告](reports/超粒球RAG_Stage4G_GTR生成器迁移复制报告.md)
- [消融与强基线计划](paper/ABLATION_AND_STRONG_BASELINE_PLAN.md)
- [论文证据与主张台账](paper/EVIDENCE_AND_CLAIM_LEDGER.md)

## 科研治理

```text
STAGE_LEVEL_AUTHORIZATION_ACTIVE
ONE_RESEARCH_STAGE_ONE_AUTHORIZATION
STEP_LEVEL_APPROVAL_DISABLED
CHANNEL_LEVEL_REAPPROVAL_DISABLED
ENGINEERING_WORK_AUTONOMOUS
STAGE_INTERNAL_EXECUTION_CONTINUOUS
EXCEPTION_BASED_PAUSE_ONLY
SCIENTIFIC_INTEGRITY_CONTROLS_RETAINED
```

- 这是项目长期、全局的现行治理基线，适用于当前及未来全部科研阶段，不是本次任务或 Stage4E 的临时规则。预注册数据边界、主要终点和停止规则先于结果读取提交；一个科学阶段只授权一次。除非实验卡明确排除，授权覆盖实现、测试、预定义 Channel/数据读取、正式运行、固定分析、verifier、rerun、报告、文档、Git 同步和远端验证。
- Channel A/B 与 Gold-free/Gold-only 继续技术隔离，但不形成重复审批点；精确命令、脚本、环境变量、文件或提交不是科学审批对象。
- 阶段内工程问题自主最小修复、测试、记录并继续。只在新科学问题/阶段、冻结科学语义变化、使用授权外新证据源，或严重科研完整性异常时暂停。
- 逐命令、逐脚本、逐文件、逐提交、逐通道审批，以及重复 review、单独 synthetic 授权、普通修复 Amendment、逐次 approval record 和 nested approval chain 均已取消。
- 新阶段默认使用 1–3 页轻量实验卡，固定研究问题、假设、数据边界、方法、主要终点、成功/停止/证据不足规则、Gold/独立测试/reservation 边界和禁止事项；长协议仅用于高风险例外。
- 历史审批链只用于证据追溯，不再构成当前执行规则。已有科学协议、技术隔离、完整性检查、结果和停止结论不变。
- 全局规则不自动扩大既有阶段明确排除的科学范围。Stage4E、Stage4F 与 Stage4G 均已在各自阶段授权下连续完成；下一科学问题仍需新的阶段卡，而不是复用既有授权。

## 已知限制

- Stage4E 是 HotpotQA same-domain closed distractor 证据，不是跨域、full-wiki 或生成器未污染验证；F1 区间下界仅略高于 0。
- q25 阈值来自早期数据，不能声称对 2Wiki 最优。
- Stage4B-U1 是单一 development benchmark batch 的资源分配实验，不能主张为在线 controller。
- 插入量减少刚超过 `40%` 门槛，但不能抵消 retention、Fisher 和 CR 门失败。
- 问题类型结果仅为描述性审计；`compositional` 与 `inference` 被标记为 `SUBGROUP_CAUTION`。
- 冻结 evaluator 未输出协议所写的类型级区间；该报告完整性缺口不改变总体停止决定，但限制类型层解释。
- Stage4C 不含 candidate Gold identity/rank 或 candidate score/support/similarity 特征；candidate-level 方向只能作为未来假设。
- Stage4C 是同一 development 上的 post-Gold 探索性诊断，不建立新 controller efficacy。
- Stage4D 仍是同一 development 上的探索性 candidate audit；最低事件门不是 power guarantee，也没有 reservation 或外部验证。
- Stage4E proposed HotpotQA train 边界属于 new-ID same-domain closed distractor evaluation，不是新数据集、full-wiki 或跨域外部验证；拟定 `n=1000` 也不是 power guarantee。
- Stage4F 的 `n=3000` 是资源/精度边界，不是 power guarantee；MuSiQue 只提供 supporting-paragraph 标签，不能伪称具有 supporting-sentence Gold；其结果仍是 closed-candidate、单生成器复制。
- Stage4G 只测试一个额外的 Gemma official mobile-QAT 配置；HotpotQA 与 MuSiQue 的 F1 点差方向不一致，等权联合门未通过。该结果不能证明等价、普遍 generator robustness、Gemma 不适合 RAG，或 Qwen/Gemma 的纯架构能力排序。

## 下一步

Stage4G-GTR 已完成 8,000-call official main、400-call 分层确定性复跑、pre-Gold、Gold、10,000 次分层 bootstrap、generator interaction 和 final verification，冻结为 `GENERATOR_TRANSFER_INCONCLUSIVE`。下一步需先定义新的科学问题与轻量实验卡；消融、强基线、full-wiki/open-domain、新生成器、controller、Reservation、Stage3B 或 U2 均不得自动开展。

仓库：<https://github.com/lljjcc426/HyperGranular-RAG>
