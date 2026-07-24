# 论文材料入口

本目录只组织可由仓库证据支持的论文内容，不保存原始数据、模型、embedding cache 或未验证结果。

当前阶段为 `STAGE5_PMC_ACTIVE`：Stage4E–Stage4I 科学实验线已经完成并冻结，当前只进行论文整合、图表生成、引用准备和一致性审计，不启动新算法实验。

当前文件：

- [Stage5-PMC manuscript blueprint](STAGE5_PMC_MANUSCRIPT_BLUEPRINT.md)：中心论点、摘要框架、IMRaD、主表/主图和投稿缺口；
- [Stage5 manuscript core draft](MANUSCRIPT_CORE_DRAFT.md)：基于冻结证据的英文核心稿；外部引用尚未绑定，当前不可投稿；
- [Stage5-PMC core tables](SUBMISSION_CORE_TABLES.md)：主结果、外部稳健性、消融、效率与完整性四张核心表；
- [Stage5-PMC pre-submission audit](STAGE5_PMC_PRE_SUBMISSION_AUDIT.md)：内部 evidence/claim/caption 一致性与剩余投稿缺口；
- [Stage5 figure contracts](figures/FIGURE_CONTRACTS_AND_CAPTIONS.md)：五组论文图的 visual contract、caption、CSV trace 与 QA；
- [Stage5 figure manifest](figures/STAGE5_PMC_FIGURE_MANIFEST.json)：14 个 frozen input 和全部派生图/CSV 的 Bytes/SHA；
- [EVIDENCE_AND_CLAIM_LEDGER](EVIDENCE_AND_CLAIM_LEDGER.md)：把每项可写主张、证据等级、来源工件和限制对应起来；
- [MANUSCRIPT_OUTLINE](MANUSCRIPT_OUTLINE.md)：按科研问题而不是执行治理历史组织论文结构；
- [Stage4E Level A 协议](../docs/STAGE4E_STATIC_HGRAG_E2E_ANSWER_QUALITY_LEVEL_A_PROTOCOL.md)：已完成的端到端答案质量验证设计；
- [Stage4E E2E 报告](../reports/超粒球RAG_Stage4E_E2E答案质量报告.md)：两臂绝对指标、成对区间、独立验证、限制与谬误扫描；
- [Stage4E final verification](../results/stage4e_e2e_official_train1000_v1_final_verification.json)：正式结果工件身份与独立决策重算；
- [Stage4F-XDR 报告](../reports/超粒球RAG_Stage4F_XDR跨数据集复制报告.md)：MuSiQue 跨数据集复制、Channel C、复现与谬误扫描；
- [Stage4F final verification](../results/stage4f_xdr_musique_train3000_v1_final_verification.json)：source/model/environment、3,000-query metrics、bootstrap 与 decision 独立重建。
- [Stage4G-GTR 报告](../reports/超粒球RAG_Stage4G_GTR生成器迁移复制报告.md)：一个额外 Gemma mobile-QAT 配置下的数据集级/等权结果、interaction、确定性和主张边界；
- [Stage4G final verification](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_final_verification.json)：4,000-query scores、分层 bootstrap、interaction 与 `GENERATOR_TRANSFER_INCONCLUSIVE` 独立重建；
- [Stage4H-CBE 报告](../reports/超粒球RAG_Stage4H_CBE核心消融与强基线报告.md)：两个新零重叠边界上的七臂绝对结果、四个主要比较、资源、验证与谬误扫描；
- [Stage4H final verification](../results/stage4h_cbe_hotpot1000_musique1500_v1_final_verification.json)：2,500-query metrics、10,000-bootstrap、Holm 与分项 decision 独立重建；
- [Stage4I-SDC 报告](../reports/超粒球RAG_Stage4I_SDC强稠密检索互补性报告.md)：BGE 主排名 + MiniLM-HGRAG sidecar 的四臂绝对结果、核心互补性、placement、facet、资源与验证；
- [Stage4I final verification](../results/stage4i_sdc_hotpot1000_musique1500_v1_final_verification.json)：2,500-query metrics、10,000-bootstrap、evidence transition、decision 与工件身份独立重建；
- [方法定义与冻结结果表](METHODS_AND_RESULTS_TABLES.md)：静态方法公式/伪代码、Stage4E–4G 统一结果、Stage4H 消融/强基线、Stage4I strong-dense sidecar 以及资源与完整性表；
- [消融与强基线设计/结果](ABLATION_AND_STRONG_BASELINE_PLAN.md)：保留事前设计并登记 Stage4H strong-baseline 边界与 Stage4I sidecar/placement/facet 结果。

写作规则：

- verified negative、inconclusive 与 positive evidence 分开表述；
- 不把 retrieval coverage 直接等同于 answer quality；
- 不把同一 development 上的 Stage4C/4D 机制审计写成外部 efficacy validation；
- 不把 U1-D controller 的失败外推为 HyperGranular-RAG 整体失败；
- Stage4E 可写为冻结 HotpotQA same-domain closed-distractor 正结果；Stage4F 可写为在冻结 MuSiQue closed-candidate 边界上的跨数据集复制；两者都不得外推到 full-wiki/open-domain、其他生成器或 controller；
- Stage4G 必须写成一个额外预指定生成器配置下的 inconclusive transfer test：HotpotQA F1 点差为正、MuSiQue 为轻微负向、数据集等权门未通过；不得写成普遍 generator robustness、显著负向迁移或模型架构排名；
- Stage4H 必须同时写明 Full−Dense `SUPPORTED`、Full−StrongDense `NEGATIVE`、NoProtection `INCONCLUSIVE`、NoFacet `SUPPORTED`、flat `NOT_FAIRLY_DEFINED`；不得只保留有利消融；
- Stage4I 必须把 Protected−BGE `INCONCLUSIVE`、Protected−Unprotected `SUPPORTED` 与 Protected−NoFacet `INCONCLUSIVE` 分层写明；placement 支持不得替代核心 strong-dense comparison；
- 所有数字必须能定位到 tracked result/report，或明确标记为 protocol parameter。
