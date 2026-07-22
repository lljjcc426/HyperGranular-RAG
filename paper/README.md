# 论文材料入口

本目录只组织可由仓库证据支持的论文内容，不保存原始数据、模型、embedding cache 或未验证结果。

当前文件：

- [EVIDENCE_AND_CLAIM_LEDGER](EVIDENCE_AND_CLAIM_LEDGER.md)：把每项可写主张、证据等级、来源工件和限制对应起来；
- [MANUSCRIPT_OUTLINE](MANUSCRIPT_OUTLINE.md)：按科研问题而不是执行治理历史组织论文结构；
- [Stage4E Level A 协议](../docs/STAGE4E_STATIC_HGRAG_E2E_ANSWER_QUALITY_LEVEL_A_PROTOCOL.md)：已完成的端到端答案质量验证设计；
- [Stage4E E2E 报告](../reports/超粒球RAG_Stage4E_E2E答案质量报告.md)：两臂绝对指标、成对区间、独立验证、限制与谬误扫描；
- [Stage4E final verification](../results/stage4e_e2e_official_train1000_v1_final_verification.json)：正式结果工件身份与独立决策重算；
- [Stage4F-XDR 报告](../reports/超粒球RAG_Stage4F_XDR跨数据集复制报告.md)：MuSiQue 跨数据集复制、Channel C、复现与谬误扫描；
- [Stage4F final verification](../results/stage4f_xdr_musique_train3000_v1_final_verification.json)：source/model/environment、3,000-query metrics、bootstrap 与 decision 独立重建。

写作规则：

- verified negative、inconclusive 与 positive evidence 分开表述；
- 不把 retrieval coverage 直接等同于 answer quality；
- 不把同一 development 上的 Stage4C/4D 机制审计写成外部 efficacy validation；
- 不把 U1-D controller 的失败外推为 HyperGranular-RAG 整体失败；
- Stage4E 可写为冻结 HotpotQA same-domain closed-distractor 正结果；Stage4F 可写为在冻结 MuSiQue closed-candidate 边界上的跨数据集复制；两者都不得外推到 full-wiki/open-domain、其他生成器或 controller；
- 所有数字必须能定位到 tracked result/report，或明确标记为 protocol parameter。
