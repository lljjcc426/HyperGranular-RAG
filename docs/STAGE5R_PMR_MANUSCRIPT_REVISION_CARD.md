# Stage5R-PMR Manuscript Revision Card

状态：

```text
STAGE5A_BNH_COMPLETE_AND_FROZEN
CORE_ALGORITHM_EXPERIMENTS_CLOSED
STAGE5R_PMR_COMPLETE
CURRENT_EVIDENCE_MANUSCRIPT_COMPLETE
VERIFIED_LITERATURE_CORPUS_COMPLETE
FIGURE_AND_TABLE_AUDIT_PASS
CLAIM_AND_CITATION_AUDIT_PASS
SUBMISSION_METADATA_PENDING
```

## 研究角色

Stage5R-PMR 是 Stage5A 后的论文重构，不是算法实验。它只读取
Stage4E–Stage5A 已冻结并通过独立验证的 evidence ledger、summary、mechanism、
efficiency 和 verification 工件。

## 中心主张

HyperGranular-RAG 在历史 compact MiniLM Dense 主干上重复获得小幅答案质量增益；
在事前指定 BGE strong dense 边界下，original Full 明确较弱，而 cross-space
sidecar 与 BGE-native reconstruction 均未建立增量答案质量。Evidence addition、
placement 和 end-to-end utility 是不同现象。

## 派生输出

- 完整英文核心稿与蓝图；
- 23 条经核验外部文献、BibTeX 与 citation–claim map；
- 五张自动生成核心表；
- 五组 SVG/PDF/600-dpi TIFF/PNG 图与 11 个 CSV；
- supplementary material；
- venue、author metadata、license 与 blockers；
- 联合 evidence/citation/figure/language/reproducibility audit。

## 完整性

- 20 个冻结输入在构建前逐项核对 SHA-256；
- 两次完整构建 manifest 同为
`EFCED94CC12FDDA26360AE958E40EE1C7C2D88FC4B5853CC63B27DCD91ED246A`；
- 33 个 derived-file identity 同字节；
- Stage4E–Stage4I 回归 89/89 PASS；
- Stage5A regression 9/9 PASS；
- Stage5-PMC verifier PASS；
- Stage5R joint verifier：`STAGE5R_PMR_MATERIALS_VERIFIED`。

## 未执行事项

本阶段没有执行 retrieval、generation、Gold evaluation、bootstrap、model search、
parameter search 或新算法实验；没有修改 Stage4E–Stage5A 正式工件，也没有修改
Stage5-PMC 冻结图形源数据。

## 锁边界

```text
FULL_WIKI_NOT_AUTHORIZED
NEW_GENERATOR_NOT_AUTHORIZED
NEW_STRONG_RETRIEVER_SEARCH_NOT_AUTHORIZED
CONTROLLER_LINE_CLOSED
RESERVATION_LOCKED
STAGE3B_LOCKED
U2_NOT_AUTHORIZED
```

作者、基金、COI、唯一 venue 和项目 license 是必须由人类提供或选择的提交元数据；
在这些事项完成前不得标记 `SUBMISSION_READY`。
