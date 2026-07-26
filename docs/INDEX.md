# 文档索引

本索引将当前科研入口、可复现证据和历史治理材料分开。日常工作优先阅读“当前有效”部分；历史文件用于追溯，不自动构成当前执行门。

## 当前有效

| 文件 | 用途 |
|---|---|
| [README](../README.md) | 项目定位、当前研究问题、证据等级和下一步 |
| [项目 AGENTS](../AGENTS.md) | 当前治理、暂停边界和 GitHub 规则 |
| [REPRODUCIBILITY](REPRODUCIBILITY.md) | 当前环境、冻结 SHA、工件与复现边界 |
| [ROADMAP](ROADMAP.md) | 完整研究时间线与阶段状态 |
| [Stage6-SVE program draft](STAGE6_SVE_STRONG_VALUE_EVIDENCE_PROGRAM_DRAFT.md) | 现代强检索器、匹配控制、full-wiki 与结构化 RAG 公平对比的分阶段 Level A 草案；当前未授权执行 |
| [Stage5R revision card](STAGE5R_PMR_MANUSCRIPT_REVISION_CARD.md) | Stage5A 后论文重构范围、派生输出、测试、锁与完成状态 |
| [Reviewer-responsive anonymous ACL draft PDF](../paper/latex/main.pdf) | 13 页匿名论文稿；正文第 1–8 页，back matter/参考文献第 9–10 页，附录图表第 11–13 页 |
| [Anonymous ACL LaTeX source](../paper/latex/main.tex) | 使用官方 ACL 样式快照、冻结 Stage5A 证据和已核验参考文献的投稿格式源码 |
| [LaTeX draft build status](../paper/latex/DRAFT_BUILD_STATUS.md) | 初稿 Bytes/SHA、编译环境、引用、匿名性和视觉检查结果 |
| [Weak-reject revision record](../paper/WEAK_REJECT_REVISION_2026-07-26.md) | 四项审核缺口、已完成修订、仍需新实验的证据边界 |
| [Manuscript-level evaluation response](../paper/MANUSCRIPT_LEVEL_EVALUATION_RESPONSE_2026-07-26.md) | 论文水平评估意见、已落实修订和需要新实验的边界 |
| [Stage5R English manuscript](../paper/MANUSCRIPT_CORE_DRAFT_STAGE5R.md) | 纳入 Stage5A 后的完整英文核心稿；当前科学证据完整，投稿元数据待作者绑定 |
| [Stage5R blueprint](../paper/STAGE5R_MANUSCRIPT_BLUEPRINT.md) | 唯一推荐标题、中心论点、主张层级与完成边界 |
| [Stage5R core tables](../paper/STAGE5R_CORE_TABLES.md) | 从冻结 JSON/JSONL/CSV 自动生成的六张核心表 |
| [Stage5R figures and captions](../paper/figures_stage5r/FIGURE_CONTRACTS_AND_CAPTIONS.md) | 五组 Python 图、caption、CSV 与 Bytes/SHA 追溯 |
| [Stage5R joint audit](../paper/STAGE5R_PRE_SUBMISSION_AUDIT.md) | evidence/citation/figure/language/reproducibility 联合审计 |
| [Verified literature corpus](../paper/references/VERIFIED_LITERATURE_CORPUS.md) | 23 条外部文献的官方来源、审阅状态和允许引用用途 |
| [Author and submission metadata](../paper/AUTHOR_AND_SUBMISSION_METADATA.yaml) | 人工确认的作者、单位、投稿、许可与 AI 披露字段；未确认字段禁止自动推断 |
| [Metadata confirmation history](../paper/AUTHOR_AND_SUBMISSION_METADATA_HISTORY.md) | 作者顺序、通讯作者、基金、许可和目标场所等人工变更的追加式记录 |
| [LaTeX identity switch](../paper/latex/README.md) | 默认匿名、显式 camera-ready 的 fail-closed 使用说明与构建入口 |
| [Venue matrix](../paper/submission/VENUE_TARGET_MATRIX.md) | TACL、ACL/EMNLP、TMLR、Cambridge NLP 与 Findings 适配分析 |
| [Submission blockers](../paper/submission/SUBMISSION_BLOCKERS.md) | 作者、基金、COI、venue、许可和格式的显式待办 |
| [Stage5A-BNH experiment card](STAGE5A_BNH_EXPERIMENT_CARD.md) | 已冻结 BGE-native development/confirmation、停止规则与主张边界 |
| [Stage5A final verification](../results/stage5a_bnh_final_verification.json) | BGE-native 核心/placement/facet 结论与工件身份的最终独立验证 |
| [Stage5-PMC 阶段卡](STAGE5_PMC_PAPER_MANUSCRIPT_CONSOLIDATION_CARD.md) | 当前非实验论文整合阶段、主张层级、交付物与锁边界 |
| [Stage5-PMC manuscript blueprint](../paper/STAGE5_PMC_MANUSCRIPT_BLUEPRINT.md) | Stage5A 前的首轮冻结论文蓝图 |
| [Stage5-PMC manuscript core draft](../paper/MANUSCRIPT_CORE_DRAFT.md) | Stage5A 前的首轮英文稿；保留为历史基线 |
| [Stage5 core tables](../paper/SUBMISSION_CORE_TABLES.md) | 主结果、外部稳健性、消融、效率与完整性四张核心表 |
| [Stage5 figure contracts](../paper/figures/FIGURE_CONTRACTS_AND_CAPTIONS.md) | Python 图形合同、caption、source-data 与 QA 追溯 |
| [Stage5 pre-submission audit](../paper/STAGE5_PMC_PRE_SUBMISSION_AUDIT.md) | evidence/claim/caption 一致性与剩余非科学投稿缺口 |
| [Stage4D-CMA closure](STAGE4D_CMA_CLOSURE.md) | Stage4D 与当前 controller 分支的冻结关闭范围 |
| [Stage4E-E2E Level A protocol](STAGE4E_STATIC_HGRAG_E2E_ANSWER_QUALITY_LEVEL_A_PROTOCOL.md) | 已完成的静态 Dense-vs-q25 端到端答案质量协议 |
| [Stage4E official config](../configs/stage4e_e2e_official_train1000_v1.json) | 1,000-query 输入、模型、环境、实现与输出路径绑定 |
| [Stage4E rebound input verification](../results/stage4e_e2e_official_train1000_v1_verified_input_rebind.json) | source、三通道、历史零重叠、Qwen 环境与协议的独立只读验证 |
| [Stage4E 生成器选择报告](../reports/超粒球RAG_Stage4E生成模型选择报告.md) | Qwen-vs-Gemma 冻结对比、选择规则与限制 |
| [Stage4E E2E 报告](../reports/超粒球RAG_Stage4E_E2E答案质量报告.md) | answer F1/EM、retrieval secondary、bootstrap、subgroup caution 与谬误扫描 |
| [Stage4E final verification](../results/stage4e_e2e_official_train1000_v1_final_verification.json) | `STATIC_HGRAG_E2E_SUPPORTED` 的独立 post-Gold 重算与工件身份 |
| [Stage4E Level B implementation report](STAGE4E_E2E_LEVEL_B_IMPLEMENTATION_REPORT.md) | 输入、模型、环境、代码、测试、双授权锁与下一边界 |
| [Stage4E Level B review request](STAGE4E_E2E_LEVEL_B_REVIEW_REQUEST.md) | 一次集中完整性审核请求；本身不授权 official 执行 |
| [Stage4F-XDR 实验卡](STAGE4F_XDR_EXPERIMENT_CARD.md) | MuSiQue 跨数据集复制的 source、新 ID、两臂、模型、终点、门与停止规则 |
| [Stage4F official config](../configs/stage4f_xdr_official.json) | 3,000-query A/B/C、环境、实现、授权与已完成结果绑定 |
| [Stage4F input manifest](../results/stage4f_xdr_musique_train3000_v1_input_manifest.json) | source-only 选择、候选池、历史 overlap 与三通道身份 |
| [Stage4F input verification](../results/stage4f_xdr_musique_train3000_v1_verified_input.json) | source/channel/model/environment 独立重建通过的执行前快照 |
| [Stage4F 跨数据集复制报告](../reports/超粒球RAG_Stage4F_XDR跨数据集复制报告.md) | MuSiQue answer F1/EM、retrieval、成本、Channel C、验证与 11 类谬误扫描 |
| [Stage4F evaluation summary](../results/stage4f_xdr_musique_train3000_v1_evaluation_summary.json) | 3,000-query official metrics、10,000 bootstrap 与 supporting-paragraph retrieval |
| [Stage4F final verification](../results/stage4f_xdr_musique_train3000_v1_final_verification.json) | source/model/environment、query audit、overall metrics、bootstrap、decision 与工件身份独立重建 |
| [Stage4F artifact manifest](../results/stage4f_xdr_musique_train3000_v1_artifact_manifest.json) | 正式工件与本地 embedding cache 的 Bytes/SHA 清单 |
| [Stage4G-GTR 实验卡](STAGE4G_GTR_EXPERIMENT_CARD.md) | 单一额外生成器、冻结输入/rankings、等权联合统计、判定门和确定性合同 |
| [Stage4G official config](../configs/stage4g_gtr_official.json) | Gemma revision/runtime、Stage4E/4F 输入身份、代码和正式输出路径绑定 |
| [Stage4G 生成器迁移复制报告](../reports/超粒球RAG_Stage4G_GTR生成器迁移复制报告.md) | 数据集级/等权 F1/EM、interaction、运行资源、验证和主张边界 |
| [Stage4G pre-Gold verification](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_verified_pregold.json) | 8,000-call main、400-call subset、prompt/ranking/Gold 隔离与精确复现 |
| [Stage4G dataset summaries](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_dataset_summaries.json) | HotpotQA 与 MuSiQue 的绝对指标、paired bootstrap 和 interaction |
| [Stage4G equal-weight summary](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_equal_weight_summary.json) | 数据集等权主要联合统计与 query-weighted 描述量 |
| [Stage4G final verification](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_final_verification.json) | 4,000-query scoring、bootstrap、interaction 和 decision 独立重建 |
| [Stage4G artifact manifest](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_artifact_manifest.json) | 13 个前置正式工件的 Bytes/SHA 清单 |
| [Stage4H-CBE 实验卡](STAGE4H_CBE_EXPERIMENT_CARD.md) | 新零重叠边界、七臂、强 Dense 选择、四个主要比较、Holm、确定性与锁边界 |
| [Stage4H official config](../configs/stage4h_cbe_official.json) | source/history/model/code/cache、正式工件与 Stage4H complete 状态绑定 |
| [Stage4H 核心消融与强基线报告](../reports/超粒球RAG_Stage4H_CBE核心消融与强基线报告.md) | 七臂绝对指标、主要比较、资源、工程修复、工件 SHA 和 11 类谬误扫描 |
| [Stage4H equal-weight summary](../results/stage4h_cbe_hotpot1000_musique1500_v1_equal_weight_summary.json) | 10,000-bootstrap、Holm 与四个主要/两个支持性比较 |
| [Stage4H final verification](../results/stage4h_cbe_hotpot1000_musique1500_v1_final_verification.json) | query metrics、bootstrap、Holm、decision 与锁状态独立重建 |
| [Stage4H artifact manifest](../results/stage4h_cbe_hotpot1000_musique1500_v1_artifact_manifest.json) | 16 个核心正式工件的 Bytes/SHA 清单 |
| [Stage4I-SDC 实验卡](STAGE4I_SDC_EXPERIMENT_CARD.md) | 新零重叠边界、BGE 主干、MiniLM-HGRAG sidecar、四臂、eligibility gate、bootstrap 与锁边界 |
| [Stage4I official config](../configs/stage4i_sdc_official.json) | parent/model/code/cache、正式工件和 complete 状态绑定 |
| [Stage4I 强稠密检索互补性报告](../reports/超粒球RAG_Stage4I_SDC强稠密检索互补性报告.md) | eligibility、四臂 F1/EM、placement/facet、Gold transitions、完整性修复与主张边界 |
| [Stage4I equal-weight summary](../results/stage4i_sdc_hotpot1000_musique1500_v1_equal_weight_summary.json) | 10,000-bootstrap 核心与支持性比较 |
| [Stage4I final verification](../results/stage4i_sdc_hotpot1000_musique1500_v1_final_verification.json) | metrics、bootstrap、decision、mechanism 与锁状态独立重建 |
| [Stage4I artifact manifest](../results/stage4i_sdc_hotpot1000_musique1500_v1_artifact_manifest.json) | 18 个前置正式工件与 final verification 的 Bytes/SHA 清单 |
| [消融与强基线设计/结果](../paper/ABLATION_AND_STRONG_BASELINE_PLAN.md) | 保留事前设计并登记 Stage4H–4I verified outcomes |
| [方法定义与冻结结果表](../paper/METHODS_AND_RESULTS_TABLES.md) | 静态方法、Stage4E–4G 统一结果、Stage4H 消融/强基线、Stage4I sidecar 及资源表 |
| [论文材料入口](../paper/README.md) | 论文结构、证据主张台账和待补结果 |
| [论文证据与主张台账](../paper/EVIDENCE_AND_CLAIM_LEDGER.md) | 将可写主张、证据等级、来源与限制逐项绑定 |
| [Simplified execution protocol](STAGE4B_U1_SIMPLIFIED_EXECUTION_PROTOCOL_V1.md) | Stage4B-U1-D 科学与 pre-Gold 执行合同 |
| [Official config](../configs/stage4b_u1_d_official.json) | 冻结输入、代码、cache、参数和输出绑定 |
| [Gold evaluation config](../configs/stage4b_u1_d_gold_evaluation.json) | 已授权 Gold 输入、命令、复跑、验证和停止规则绑定 |
| [Stage4B-U1-D 统计验证报告](../reports/超粒球RAG_Stage4B_U1_D_Gold评估与统计验证报告.md) | Gold 结果、门判定、复现与 11 类谬误扫描 |
| [Stage4C-U1-FMA protocol](STAGE4C_U1_FAILURE_MECHANISM_AUDIT_PROTOCOL.md) | post-Gold 探索性失败机制诊断的冻结合同 |
| [Stage4C-U1-FMA 报告](../reports/超粒球RAG_Stage4C_U1失败机制诊断报告.md) | 特征、decile、all-on/off、OOF 与 11 类谬误扫描 |
| [Stage4D-CMA protocol](STAGE4D_CANDIDATE_MARGINAL_UTILITY_AUDIT_PROTOCOL.md) | candidate marginal-utility attribution、固定 probe 与 decision 合同 |
| [Stage4D 固定依赖](../requirements-stage4d.txt) | CPython 3.12.0 下的精确 NumPy/SciPy/scikit-learn 运行绑定 |
| [Stage4D-CMA 报告](../reports/超粒球RAG_Stage4D_CMA候选边际效用归因审计报告.md) | 候选标签、固定 OOF、provenance、decision 与 11 类谬误扫描 |

## 已完成的冻结正式工件

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

### Stage4C-U1-FMA 诊断工件

| 文件 | 状态 |
|---|---|
| [query features](../results/stage4c_u1_fma_query_features.csv) | 4,500 queries；严格对账通过 |
| [feature separability](../results/stage4c_u1_fma_feature_separability.csv) | 12 个预设特征的分布与 GAIN/HARM 可分性 |
| [score deciles](../results/stage4c_u1_fma_score_deciles.csv) | 10 个冻结 ordered-rank deciles |
| [candidate mechanisms](../results/stage4c_u1_fma_candidate_mechanisms.csv) | query-level all-on/off composition；不含 candidate Gold identity |
| [OOF predictions](../results/stage4c_u1_fma_oof_predictions.csv) | 3 tasks × 3 fixed panels |
| [Stage4C summary](../results/stage4c_u1_fma_summary.json) | `MECHANISM_EVIDENCE_INCONCLUSIVE` |

### Stage4D-CMA 正式工件

| 文件 | 状态 |
|---|---|
| [Channel A candidate trace](../results/stage4d_cma_candidate_trace.jsonl) | 8,467 个 Gold-free eligible candidates；独立重建通过 |
| [Channel B candidate labels](../results/stage4d_cma_candidate_labels.jsonl) | 七类 candidate marginal labels；独立反事实验证通过 |
| [counterfactual summary](../results/stage4d_cma_counterfactual_summary.json) | 94/69 q25 gain/harm query 对账 |
| [fold assignments](../results/stage4d_cma_fold_assignments.json) | 2,446 个 candidate-bearing queries 的固定 5 folds |
| [OOF predictions](../results/stage4d_cma_oof_predictions.csv) | 68,588 行；3 tasks × 4 panels |
| [metrics](../results/stage4d_cma_metrics.json) | 10,000 次 query-cluster bootstrap 与 budget-region 分层 |
| [decision](../results/stage4d_cma_decision.json) | `CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE` |
| [final verification](../results/stage4d_cma_verified_final.json) | provenance、内容级重算与独立验证通过 |

核心实现提交为 `b4dfa52d0a38409dfc19444d21beec59606088e1`，guarded transaction 补全提交为 `730daea1350616bfdcb6a11832b361c4d574d985`，zero-candidate repair 为 `080cc44781cddc7d25584812fee5dea2158142e9`。probe source blob 在 repair 与当前协议提交 `b8bd1eafd51507e0d272a701219b7f7833c35704` 中相同。

### Stage4F-XDR 正式工件

| 文件 | 状态 |
|---|---|
| [rankings](../results/stage4f_xdr_musique_train3000_v1_rankings.jsonl) | 3,000 queries；独立 Gold-free reconstruction 通过 |
| [predictions main/rerun](../results/stage4f_xdr_musique_train3000_v1_predictions_main.jsonl) | 两份各 1,106,316 bytes / `68F95245...34E62E`；同字节 |
| [prompt audits main/rerun](../results/stage4f_xdr_musique_train3000_v1_prompt_audit_main.jsonl) | 两份各 8,573,108 bytes / `D27D24E7...FF132E`；同字节 |
| [pre-Gold verification](../results/stage4f_xdr_musique_train3000_v1_verified_pregold.json) | `STAGE4F_PRE_GOLD_ARTIFACTS_VERIFIED` |
| [query audit](../results/stage4f_xdr_musique_train3000_v1_query_audit.jsonl) | 3,000-query answer/retrieval/context audit；独立重建通过 |
| [scientific decision](../results/stage4f_xdr_musique_train3000_v1_scientific_decision.json) | `STATIC_HGRAG_XDR_SUPPORTED` |
| [descriptive subgroups](../results/stage4f_xdr_musique_train3000_v1_descriptive_subgroups.json) | post-decision hop-count audit；全行 `SUBGROUP_CAUTION` |

### Stage4G-GTR 正式工件

| 文件 | 状态 |
|---|---|
| [input/model manifest](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_input_model_manifest.json) | Stage4E/4F frozen inputs/rankings 与 Gemma mobile-QAT snapshot 身份通过 |
| [predictions main](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_predictions_main.jsonl) | 8,000 calls；零失败；1,508,328 bytes / `E6B0A50C...D31709` |
| [predictions rerun subset](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_predictions_rerun_subset.jsonl) | 2 datasets × 2 arms × 100 calls；相对 main 精确复现 |
| [prompt audits main](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_prompt_audit_main.jsonl) | 14,058,957 bytes / `E8227941...54F8F1`；独立重建通过 |
| [pre-Gold verification](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_verified_pregold.json) | `STAGE4G_GTR_PRE_GOLD_VERIFIED` |
| [query scores](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_query_scores.jsonl) | 4,000 paired queries；独立重建通过 |
| [dataset summaries](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_dataset_summaries.json) | HotpotQA F1 `+0.01265`；MuSiQue F1 `-0.00232` |
| [equal-weight summary](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_equal_weight_summary.json) | F1 `+0.00516 [-0.00262,0.01295]` |
| [scientific decision](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_scientific_decision.json) | `GENERATOR_TRANSFER_INCONCLUSIVE` |
| [final verification](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_final_verification.json) | `STAGE4G_GTR_FINAL_VERIFICATION_PASS` |

### Stage4H-CBE 正式工件

| 文件 | 状态 |
|---|---|
| [input manifest](../results/stage4h_cbe_hotpot1000_musique1500_v1_input_manifest.json) | HotpotQA 1,000 + MuSiQue 1,500；全部历史正式 ID overlap 0 |
| [strong-dense selection](../results/stage4h_cbe_strong_dense_selection_manifest.json) | BGE strong dense 在 Gold 前唯一绑定 |
| [rankings](../results/stage4h_cbe_hotpot1000_musique1500_v1_rankings.jsonl) | 2,500 queries × 7 arms；独立重建通过 |
| [predictions main](../results/stage4h_cbe_hotpot1000_musique1500_v1_predictions_main.jsonl) | 17,500 calls；零失败 |
| [predictions subset](../results/stage4h_cbe_hotpot1000_musique1500_v1_predictions_rerun_subset.jsonl) | 200-query/1,400-pair pre-hash subset；与 main 精确复现 |
| [pre-Gold verification](../results/stage4h_cbe_hotpot1000_musique1500_v1_verified_pregold.json) | selection/ranking/prompt/determinism reconstruction PASS |
| [dataset summaries](../results/stage4h_cbe_hotpot1000_musique1500_v1_dataset_summaries.json) | 七臂 HotpotQA/MuSiQue 绝对 F1/EM/CR/ER |
| [equal-weight summary](../results/stage4h_cbe_hotpot1000_musique1500_v1_equal_weight_summary.json) | Full−Dense/NoFacet supported；StrongDense negative；NoProtection inconclusive |
| [scientific decision](../results/stage4h_cbe_hotpot1000_musique1500_v1_scientific_decision.json) | 五项分项结论冻结 |
| [final verification](../results/stage4h_cbe_hotpot1000_musique1500_v1_final_verification.json) | `STAGE4H_FINAL_VERIFICATION_PASS` |

### Stage4I-SDC 正式工件

| 文件 | 状态 |
|---|---|
| [input manifest](../results/stage4i_sdc_hotpot1000_musique1500_v1_input_manifest.json) | HotpotQA 1,000 + MuSiQue 1,500；全部历史正式 ID overlap 0 |
| [eligibility audit](../results/stage4i_sdc_hotpot1000_musique1500_v1_eligibility_audit.json) | combined insertable rate 0.6112；blind-only gate PASS |
| [rankings](../results/stage4i_sdc_hotpot1000_musique1500_v1_rankings.jsonl) | 2,500 queries × 4 arms；独立重建通过 |
| [candidate trace](../results/stage4i_sdc_hotpot1000_musique1500_v1_candidate_trace.jsonl) | facet/no-facet eligibility、dedup 与 inserted set |
| [predictions main](../results/stage4i_sdc_hotpot1000_musique1500_v1_predictions_main.jsonl) | 10,000 calls；零失败 |
| [predictions subset](../results/stage4i_sdc_hotpot1000_musique1500_v1_predictions_rerun_subset.jsonl) | 200-query/800-pair pre-hash subset；与 main 精确复现 |
| [pre-Gold verification](../results/stage4i_sdc_hotpot1000_musique1500_v1_verified_pregold.json) | selection/cache/ranking/prompt/determinism reconstruction PASS |
| [equal-weight summary](../results/stage4i_sdc_hotpot1000_musique1500_v1_equal_weight_summary.json) | Protected−BGE inconclusive；Protected−Unprotected supported；facet inconclusive |
| [evidence transition audit](../results/stage4i_sdc_hotpot1000_musique1500_v1_evidence_transition_audit.json) | added/displaced/net Gold 与 answer-change 描述表 |
| [scientific decision](../results/stage4i_sdc_hotpot1000_musique1500_v1_scientific_decision.json) | `STRONG_DENSE_COMPLEMENTARITY_INCONCLUSIVE` |
| [final verification](../results/stage4i_sdc_hotpot1000_musique1500_v1_final_verification.json) | `STAGE4I_FINAL_VERIFICATION_PASS` |
| [artifact manifest](../results/stage4i_sdc_hotpot1000_musique1500_v1_artifact_manifest.json) | 19 项工件身份冻结 |

## 科学设计与阶段证据

- Stage4A-R2 的样本、映射、估计和验证协议保留在对应 `STAGE4A_R2_*` 文档中。
- Stage4B-U1 的科学设计源为 `STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md`。
- 当前 simplified 协议是在不改变科学语义的前提下替代旧多层 PowerShell 执行链。
- 方法审计见 [PRIOR_STAGE_METHOD_AUDIT](PRIOR_STAGE_METHOD_AUDIT.md)。
- 阶段性结果说明位于 `reports/`。
- Stage4D 与当前 controller 线已经按 [关闭声明](STAGE4D_CMA_CLOSURE.md) 冻结；Stage4E 不继承 controller labels、features 或 model。
- Stage4E 把 data boundary 明确限定为 HotpotQA train 的 new-ID same-domain distractor sample，不表述为跨数据集或 full-wiki external validation。正式结果为 answer F1 `+0.01478 [0.00020,0.02988]`，独立验证通过。
- Stage4F 在 MuSiQue train 3,000 个新 ID 上复制同一静态方法：answer F1 `+0.01140 [0.00450,0.01835]`，冻结为 `STATIC_HGRAG_XDR_SUPPORTED`；仍不是 full-wiki、open-domain 或跨生成器确认。
- Stage4G 只改变为一个事前指定的 Gemma official mobile-QAT 生成器配置。HotpotQA/MuSiQue F1 点差方向不一致，数据集等权 F1 为 `+0.00516 [-0.00262,0.01295]`，冻结为 `GENERATOR_TRANSFER_INCONCLUSIVE`；不能写成普遍 generator robustness 或模型架构排名。
- Stage4H 在两组新的零重叠边界上运行七个 P0 retrieval/ablation arms：Full−Dense 与 Full−NoFacet 受支持，Full−StrongDense 明确负向，Full−NoProtection 不确定，flat-unit 未公平定义。结果限制论文的强基线主张，不改变 Stage4E/4F 的历史冻结正结果。
- Stage4I 在另一组零重叠边界上把冻结 MiniLM-HGRAG 作为 BGE sidecar：Protected−BGE 不确定，Protected−Unprotected 受支持，facet increment 不确定。它进一步限制强检索器主张，但不改写 Stage4E/4F/4H 已冻结结果。

## 历史治理证据

以下文件族继续保留原路径，以避免破坏既有 SHA、交叉引用和科研轨迹：

- `STAGE4B_U1_PREGOLD_AMENDMENT_*`
- `STAGE4B_U1_PREGOLD_HARD_FAILURE_*`
- `STAGE4B_U1_*_REVIEW_*`
- `STAGE4B_U1_*_APPROVAL_*`
- 旧 PowerShell launcher、remote gate、observer、command-line capture 与 nested PRE 相关源码/审计。

这些材料记录了失败、修订和治理演化，但不应被用作当前命令入口，也不得据此恢复已经退役的逐步骤审批链。

## 当前授权治理

这是项目长期、全局的现行治理基线，适用于当前及未来全部科研阶段，不是单次任务或当前 Stage 的临时例外。现行状态为 `STAGE_LEVEL_AUTHORIZATION_ACTIVE`、`ONE_RESEARCH_STAGE_ONE_AUTHORIZATION`、`STEP_LEVEL_APPROVAL_DISABLED`、`CHANNEL_LEVEL_REAPPROVAL_DISABLED`、`ENGINEERING_WORK_AUTONOMOUS`、`STAGE_INTERNAL_EXECUTION_CONTINUOUS`、`EXCEPTION_BASED_PAUSE_ONLY` 和 `SCIENTIFIC_INTEGRITY_CONTROLS_RETAINED`。

- 一个科学阶段一次授权；除非实验卡明确排除，阶段内实现、测试、预定义数据/Channel、正式运行、固定分析、验证、复跑、报告和 Git 同步连续完成。
- 技术 Channel 隔离继续保留，不再转化为通道级复审；CLI、环境变量、路径和提交不是科学审批对象。
- 普通工程异常自主最小修复。只在新科学问题/阶段、冻结科学语义变化、授权外新证据源或严重完整性异常时暂停。
- 历史 Amendment/Approval/Review/Hard Failure 文件保持原样，仅作证据追溯。

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
- 不为普通测试、push、工程问题、单次运行或通道切换创建独立审批文档。
- 科学协议、失败证据和正式结果不删除、不覆盖、不改写。
- 新增历史证据时优先更新 ROADMAP 和本索引，不向 README 堆叠全过程。

## 当前下一步

当前状态为 `STAGE4I_FINAL_VERIFICATION_PASS`。Stage4E–4I 均已冻结；当前没有已授权的下一科学阶段。full-wiki、Reservation、Stage3B、U2/controller、新生成器和新 strong-retriever search 均须先定义新的阶段级科学边界。
