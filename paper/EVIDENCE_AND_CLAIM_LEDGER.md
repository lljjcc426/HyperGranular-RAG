# HyperGranular-RAG 证据与主张台账

## 当前总论边界

静态 q25 protected insertion 与 adaptive controller 是两个不同主张。Stage4E 支持前者在冻结 HotpotQA same-domain closed-distractor 边界上的端到端答案质量增益，Stage4F 又在冻结 MuSiQue closed-candidate 边界复制该 answer-F1 方向与支持门；Stage4G 在一个额外、事前指定的 Gemma mobile-QAT 配置下得到 inconclusive generator-transfer 结果。Stage4H 在两组新的零重叠 closed-candidate 边界上支持 full 相对历史 MiniLM Dense 和 no-facet ablation 的增益，但 full 明确低于 BGE strong dense，protected insertion 贡献不确定，flat-unit 对照未公平定义。Stage4I 进一步把冻结 HGRAG 作为 BGE 主排名上的独立 sidecar：核心 protected sidecar 相对 BGE 的 answer-F1 差异不确定；在完全相同插入集合下，protected placement 优于 unprotected placement；facet 相对 no-facet 的增量仍不确定。当前 U1/Stage4D controller 线仍保持关闭。

## 可写主张

| 主张 | 证据等级 | 核心证据 | 论文表述边界 |
|---|---|---|---|
| protected insertion 能在 Dense 主干后补充证据 | 有限内部独立验证 | Stage2F q25 p10/i4 相对 Dense CR@20 `+0.0175 [0.0025, 0.0350]` | 只限既有 HotpotQA/MuSiQue slice 与冻结 encoder/K；主 CR@10 gate 失败 |
| 官方 2Wiki development 上存在 q25 gain/harm 事件 | 官方来源 development 事件率估计 | Stage4A-R2 与 Stage4B Gold audit：94 gain / 69 harm queries | 不等同于平均 answer-quality 提升或外部泛化 |
| 当前 U1-D controller 降低资源但选择方向失败 | verified development negative result | 插入量 `-40.0275%`；gain retention `0.5000`；harm retention `0.7681`；CR@20 低于 Dense/q25 | 可写为当前 controller 的有效负结果；不能写成 HGRAG 整体无效 |
| raw U1 score 对 gain/harm 方向错误且 all-on/off 受限 | post-Gold exploratory，`CAUTION` | Stage4C raw score AUROC `0.39269 [0.30558, 0.48150]`；92/94 gain query 为 mixed gain/noise | 机制诊断，不是新 controller efficacy |
| candidate deployable features 含部分 gain/harm 符号信号，但不足以晋级 | post-Gold exploratory，`CAUTION` | Stage4D Task-C combined AUROC `0.64310 [0.55520, 0.72974]`，Brier 未优于 prevalence baseline | 结论必须是 inconclusive；不授权 U2、selector 或阈值 |
| 静态 HGRAG 在冻结 same-domain closed-distractor 边界上改善端到端答案质量 | verified official positive result | Stage4E：answer F1 `0.42150→0.43628`；paired delta `+0.01478 [0.00020,0.02988]`；final verification PASS | 仅限 HotpotQA deterministic 1,000-query、Qwen2.5-1.5B、Top-20；F1 下界接近 0，不写成大幅或普遍提升 |
| 静态 HGRAG 的 answer-F1 增益在新的 MuSiQue 边界上复现 | verified cross-dataset replication | Stage4F：answer F1 `0.13595→0.14735`；paired delta `+0.01140 [0.00450,0.01835]`；EM guard 与 final verification PASS | 可写为两个 frozen closed-candidate 多跳 QA 数据集上的复制；不可写成 full-wiki/open-domain、跨生成器或普遍有效 |
| 静态 HGRAG 的 retrieval gain 在一个额外预指定生成器配置下未获得明确复制或负向证据 | verified generator-transfer replication，inconclusive | Stage4G：HotpotQA F1 delta `+0.01265 [-0.00220,0.02744]`；MuSiQue `-0.00232 [-0.00685,0.00208]`；equal-weight `+0.00516 [-0.00262,0.01295]`；final verification PASS | 只能写为 one-additional-generator inconclusive；Gemma 架构与 mobile-QAT 效应不可分离；不建立普遍鲁棒性或架构排名 |
| Static q25 full 相对历史 MiniLM Dense 的增益在两个新边界上再次出现，且 facet-hyperedge 有系统内增量价值 | verified component/baseline evaluation | Stage4H：Full−Dense 等权 F1 `+0.01357 [0.00491,0.02233]`；Full−NoFacet `+0.01336 [0.00341,0.02343]`；Holm 后均通过 | 只限固定 Qwen、两个 closed-candidate 新边界和冻结实现；消融支持增量价值，不自动证明一般因果机制 |
| Full 方法不优于事前绑定的 BGE strong dense | verified negative strong-baseline result | Stage4H：Full−StrongDense 等权 F1 `-0.03998 [-0.05393,-0.02621]`；EM `-0.04067 [-0.05483,-0.02683]` | 必须如实保留；不得用 Full−MiniLM Dense 正结果声称优于强稠密检索 |
| Protected insertion 的独立贡献未确定，粒球 flat 对照未公平定义 | verified inconclusive/design boundary | Stage4H：Full−NoProtection F1 `+0.00354 [-0.00675,0.01389]`；flat=`NOT_FAIRLY_DEFINED` | 不得写成保护无作用、等价或已确认；不得把缺失 flat 对照当作粒球贡献证据 |
| 当前冻结 HGRAG sidecar 没有建立相对 BGE strong dense 的互补增益 | verified strong-dense sidecar result，inconclusive | Stage4I：Protected−BGE 等权 F1 `-0.00256 [-0.00998,0.00458]`；EM `-0.00233 [-0.00983,0.00467]`；final verification PASS | 只能写成该 BGE、Qwen、Top-20 和两个新 closed-candidate 边界下证据不确定；不能写成增益、伤害或等价 |
| 在相同 HGRAG 插入集合下，protected placement 优于 unprotected placement | verified supporting placement result | Stage4I：Protected−Unprotected 等权 F1 `+0.01122 [0.00129,0.02104]`；EM `+0.01300 [0.00333,0.02283]` | 只支持冻结 sidecar 内部的位置设计；不得据此声称 protected sidecar 优于 BGE |
| BGE sidecar 中 facet 相对 no-facet 的增量未确定 | verified supporting ablation，inconclusive | Stage4I：Protected−NoFacet 等权 F1 `-0.00743 [-0.01616,0.00132]`；EM `-0.00600 [-0.01483,0.00283]` | 不得写成 facet 有效、无效、等价或一般机制证据 |

Stage4F-XDR 已完成 MuSiQue train 3,000 个新 ID 的完整事务并通过独立 final verification。它支持“Stage4E 的静态 answer-F1 增益在第二个冻结数据集边界上复现”。Stage4G-GTR 又在同一两个数据边界上测试一个额外 Gemma mobile-QAT 配置，得到 `GENERATOR_TRANSFER_INCONCLUSIVE`；所以不能将 Stage4E/4F 的 Qwen 结果扩大为所有生成器或开放域有效。

## 不可写主张

- “HyperGranular-RAG 在所有任务或 full-wiki 环境提高最终答案准确率”；Stage4E 只支持冻结的 HotpotQA same-domain closed-distractor 边界。
- “q25 在 2Wiki 上平均优于 Dense”；现有 Stage4A/4B 证据没有建立该总体现象。
- “U1 能保留 gain 并过滤 harm”；冻结结果方向相反。
- “Stage4D 已学会可部署 candidate selector”；唯一 advancement panel 未过联合门。
- “当前结果已 full-wiki、open-domain 或普遍跨生成器泛化”；Stage4G 只测试一个额外 Gemma mobile-QAT 配置，且联合判定 inconclusive。
- “完整 HyperGranular-RAG 优于强稠密检索器”或“强基线比较支持完整方法”；Stage4H 对 BGE strong dense 为明确负向。
- “protected insertion 已被独立证明必要/无效”或“粒球结构已通过 flat 消融”；Stage4H 的前者不确定，后者未公平定义。
- “HGRAG sidecar 改善/损害 BGE strong dense”或“二者等价”；Stage4I 核心区间跨 0，冻结结论为 `STRONG_DENSE_COMPLEMENTARITY_INCONCLUSIVE`。
- “protected placement 获得支持，所以 HGRAG sidecar 优于 BGE”；Stage4I placement 是同一插入集合内的支持性比较，不是核心 advancement comparison。
- “Stage4I 证明 facet 在 BGE backbone 上有效/无效”；Protected−NoFacet 区间跨 0。
- “Gemma 4 E2B 不适合 RAG”“Qwen 基础模型能力显著更强”或“Gemma 架构质量较差”；Stage4G 不是纯架构比较，mobile-QAT 效应不可分离。
- “Stage4E 是对生成器未见数据的无污染测试”；它只保证未被本项目读取，公开 HotpotQA train 可能进入过模型预训练语料。
- “不显著说明方法等价”；所有未过正/负门的结果都应写为 inconclusive。

## 证据入口

| 主题 | 入口 |
|---|---|
| 完整时间线 | `docs/ROADMAP.md` |
| 方法与证据审计 | `docs/PRIOR_STAGE_METHOD_AUDIT.md` |
| U1-D Gold 负结果 | `reports/超粒球RAG_Stage4B_U1_D_Gold评估与统计验证报告.md` |
| Stage4C 失败机制 | `reports/超粒球RAG_Stage4C_U1失败机制诊断报告.md` |
| Stage4D candidate 机制 | `reports/超粒球RAG_Stage4D_CMA候选边际效用归因审计报告.md` |
| Stage4D final verification | `results/stage4d_cma_verified_final.json` |
| Stage4D 关闭边界 | `docs/STAGE4D_CMA_CLOSURE.md` |
| Stage4E generator selection | `reports/超粒球RAG_Stage4E生成模型选择报告.md`；`results/stage4e_generator_selection_verified.json` |
| Stage4E official E2E result | `reports/超粒球RAG_Stage4E_E2E答案质量报告.md`；`results/stage4e_e2e_official_train1000_v1_evaluation_summary.json`；`results/stage4e_e2e_official_train1000_v1_final_verification.json` |
| Stage4F cross-dataset preregistration | `docs/STAGE4F_XDR_EXPERIMENT_CARD.md`；`configs/stage4f_xdr_official.json`；`results/stage4f_xdr_musique_train3000_v1_verified_input.json` |
| Stage4F verified replication | `reports/超粒球RAG_Stage4F_XDR跨数据集复制报告.md`；`results/stage4f_xdr_musique_train3000_v1_evaluation_summary.json`；`results/stage4f_xdr_musique_train3000_v1_final_verification.json` |
| Stage4G generator-transfer preregistration | `docs/STAGE4G_GTR_EXPERIMENT_CARD.md`；`configs/stage4g_gtr_official.json`；`results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_input_model_manifest.json` |
| Stage4G verified generator transfer | `reports/超粒球RAG_Stage4G_GTR生成器迁移复制报告.md`；`results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_equal_weight_summary.json`；`results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_final_verification.json` |
| Stage4H component/strong-baseline evaluation | `docs/STAGE4H_CBE_EXPERIMENT_CARD.md`；`reports/超粒球RAG_Stage4H_CBE核心消融与强基线报告.md`；`results/stage4h_cbe_hotpot1000_musique1500_v1_equal_weight_summary.json`；`results/stage4h_cbe_hotpot1000_musique1500_v1_final_verification.json` |
| Stage4I strong-dense sidecar complementarity | `docs/STAGE4I_SDC_EXPERIMENT_CARD.md`；`reports/超粒球RAG_Stage4I_SDC强稠密检索互补性报告.md`；`results/stage4i_sdc_hotpot1000_musique1500_v1_equal_weight_summary.json`；`results/stage4i_sdc_hotpot1000_musique1500_v1_final_verification.json` |

## Stage4E 写入规则

Stage4E 已完成，可写两臂绝对 F1/EM、成对差值与区间、retrieval secondary metrics、确定性/独立验证状态和冻结决策。必须同段保留 new-ID same-domain closed-distractor、公开 train 可能存在预训练污染、F1 下界接近零、subgroup 仅 `CAUTION` 的限制。不得把 Stage4E 正结果用于恢复 U1/Stage4D controller，或推断跨数据集/full-wiki 泛化。

生成器选择的唯一规范表述是：在 RTX 4060 Laptop 8GB、固定短答案 RAG prompt、4,096-token 输入上限和可实际部署格式下，Qwen2.5-1.5B-Instruct FP16 在 200-query generator-selection development 上取得更高 answer F1/EM 和更低运行时间/显存，并按预登记规则成为 Stage4E 唯一生成器。Gemma 4 E2B 以官方 mobile-QAT 格式运行，因此该结果不能用于分离或评价纯基础模型架构能力。

## Stage4F 写入规则

Stage4F 可写两臂绝对 F1/EM、paired intervals、supporting-paragraph ER/CR、上下文与运行成本、确定性/独立验证和 `STATIC_HGRAG_XDR_SUPPORTED`。必须同段保留：MuSiQue 只有 paragraph-level Gold；`n=3000` 不是 power guarantee；候选来自题内给定 paragraphs；生成器仍为单一 Qwen；Channel C 仅 `SUBGROUP_CAUTION`。不得把 Stage4F 用于恢复 controller、访问 Reservation/Stage3B/U2，或声称 full-wiki/open-domain 与跨生成器泛化。

## Stage4G 写入规则

Stage4G 可写两个数据集的 Gemma Dense/static-q25 绝对 F1/EM、paired intervals、数据集等权联合统计、query-weighted 描述量、generator interaction、运行资源、确定性合同 B、Gold 隔离和 `STAGE4G_GTR_FINAL_VERIFICATION_PASS`。必须把冻结决策写为 `GENERATOR_TRANSFER_INCONCLUSIVE`，并同段说明：HotpotQA F1 点估计为正、MuSiQue 为轻微负向、支持门和负向门均未触发；只测试一个额外生成器配置；Gemma 架构、mobile-QAT 和数值格式效应不可分离；interaction 不进入主判定。不得写成普遍 generator robustness、显著负向迁移、等价、纯架构比较，或用于重开 controller/Reservation/Stage3B/U2。

## Stage4H 写入规则

Stage4H 可写七臂绝对 F1/EM/CR/ER、四个主要等权比较、Holm p、BM25/hybrid 支持性比较、插入/资源、pre-hash subset determinism、Gold 隔离和 `STAGE4H_FINAL_VERIFICATION_PASS`。必须同时保留：

- Full−Dense 为 `SUPPORTED`，但对照是历史 MiniLM Dense；
- Full−StrongDense 为 `NEGATIVE`，因此不能声称 full 优于强稠密检索；
- Full−NoFacet 为 `SUPPORTED`，只表示冻结系统内的增量价值；
- Full−NoProtection 为 `INCONCLUSIVE`，不能解释成有效、无效或等价；
- granular-ball flat 对照为 `NOT_FAIRLY_DEFINED`；
- P1 effect-cost curve 为 `NOT_RUN_RESOURCE_BOUNDED`；
- 全部结果限于固定 Qwen、closed-candidate HotpotQA/MuSiQue 新边界，不是 full-wiki/open-domain。

## Stage4I 写入规则

Stage4I 可写四臂绝对 F1/EM/CR/ER、Protected−BGE 的数据集级与等权差异、完全相同插入集合下的 Protected−Unprotected 支持性比较、Protected−NoFacet 支持性消融、added/displaced/net Gold 的 post-decision 描述、资源、pre-hash subset determinism、Gold 隔离和 `STAGE4I_FINAL_VERIFICATION_PASS`。必须同时保留：

- 核心结论为 `STRONG_DENSE_COMPLEMENTARITY_INCONCLUSIVE`，不能写成 sidecar 改善、损害或等价于 BGE；
- placement 结论为 `PROTECTED_PLACEMENT_SUPPORTED`，但只说明同一候选集合的排序位置重要，不能触发核心 advancement；
- unprotected sidecar 相对 BGE 的等权 F1 为 `-0.01379 [-0.02440,-0.00339]`，用于解释 placement，而不是另立事后主结论；
- facet 结论为 `BGE_FACET_INCREMENT_INCONCLUSIVE`；
- HGRAG 使用独立 MiniLM sidecar，q25 只决定 sidecar eligibility，不与 BGE 分数融合；
- 全部结果限于一个事前冻结的 BGE large-en-v1.5 backbone、固定 Qwen、Top-20 和两个新零重叠 closed-candidate 边界，不是普遍 strong-retriever、full-wiki 或 open-domain 结论。
