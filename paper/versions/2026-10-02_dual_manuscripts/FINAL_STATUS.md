# 双版本论文成稿：本地交付状态

首先阅读：

- [会议版完整英文论文，8 页](conference/HyperGranular-RAG_Conference.pdf)；[LaTeX](conference/main.tex)。
- [期刊版完整英文论文，19 页](journal/HyperGranular-RAG_Journal.pdf)；[LaTeX](journal/main.tex)。

状态：FULL_ENGLISH_DRAFTS_COMPLETE / BOTH_PDFS_BUILT / ALL_PAGES_VISUALLY_REVIEWED。

两版从标题与摘要到结论、参考文献和附录均有实际正文。会议版聚焦 compact evidence completion 的主要收益、组件证据和强主干边界；期刊版增加同一证据体系下的严格定义、证明与反例、置换机制、案例和成本分析。扩展论证不被计作新增正式实验。

## 已完成并可本地核对

1. 按学术写作技能流程，将正文按科学问题重组；按 PDF 阅读技能渲染和逐页检查两版。没有借技能恢复逐步审批，也没有冒称独立多人审稿。
2. 复用上轮审计交付，没有重新启动全仓审计。旧 compact/static-q25、cross-space sidecar、native C10 和后来 v2 合成原型分开表述。
3. 共享数字、区间、术语和主张边界；核对既有聚合与派生表格，记录于 shared/evidence_check.json 和 shared/manuscript_consistency.json。
4. 完整阅读五篇一手论文文本，其余引用如实标明元数据/摘要或局部核对级别；保留上轮正确的 MuSiQue 作者及正式 HyperGraphRAG 文献身份。
5. 实际本地编译两份 PDF，保留真实日志、逐页渲染和人工式视觉检查记录；修正新稿中发现的公式宽度和分页问题。
6. 旧论文与历史工件未覆盖；无文件删除；初次本地交付时未 commit 或 push。用户随后要求持续同步 GitHub，本论文包据此进入提交与推送；未对外投稿。

## 交接入口

- [中文故事链与两版差异](STORY_AND_VERSION_DIFFERENCES_ZH.md)
- [证据与历史版本台账](EVIDENCE_AND_VERSION_LEDGER.md)
- [文献阅读与引用范围](LITERATURE_READING_AND_CITATION_NOTES.md)
- [构建与逐页检查](BUILD_AND_PAGE_REVIEW.md)
- [文件变更说明](FILE_CHANGES.md)

## 剩余事项

两版为完整可读初稿，不是已获投稿批准的最终包。作者、机构、基金、利益冲突、许可及匿名分发需人工确认；期刊目标未指定。两版属于同一研究的备选呈现，不能把扩写当作无重叠的新工作。

科学层面仍有明确边界：legacy scorer 对真实预测的影响尚未量化；历史统计尾比例的通用 p 值校准未确立；粒球必要性、预算匹配简单控制、纯位置因果效应和 strong-dense 增量尚缺相应正式证据。两版已经收窄主张并披露这些限制，未自行重算历史结果。

最小补评价/补实验审批集中在中文交接的最后一节。没有自动开启这些事项，正式实验及原受限数据边界继续暂停。

指定附件 CODEX_NEXT_PHASE_DUAL_MANUSCRIPTS_ZH (1).md 在提供位置不存在，同名搜索未找到，且未收到补充内容；本轮按用户消息正文完成。该附件仍是材料缺口，不能声明已读或已满足其中未知的额外要求。
