# HyperGranular-RAG 双稿二修

- [会议版英文 PDF（9 页）](conference/HyperGranular-RAG_Conference.pdf) · [LaTeX](conference/main.tex)
- [期刊版英文 PDF（21 页）](journal/HyperGranular-RAG_Journal.pdf) · [LaTeX](journal/main.tex)

两稿均已实际编译并逐页检查。53,500 条确认/迁移预测在 canonical 评分下不变；开发集同一道题的 17 条输出 F1 更正不改变任何方法差值。Stage4I 全部 2,500 对排名和可见证据内容一致，5,000 个实际 prompt 重建通过；两臂均无截断，位置对照可准确表述为固定可见证据的排序/放置策略比较。

阅读入口：[评分谱系与迁移](SCORER_LINEAGE_AND_MIGRATION.md)、[主张影响](CLAIM_IMPACT.md)、[位置/可见证据及预算](PLACEMENT_AND_VISIBLE_CONTEXT_AUDIT.md)、[中文故事链和二修改动](REVISION_LOG.md)、[构建/逐页记录](BUILD_AND_PAGE_REVIEW.md)、[文件说明](FILE_CHANGES.md)、[交付状态](FINAL_STATUS.md)。

机器可读结果位于 `scoring/`，包括全部阶段/数据集/方法的双评分、paired deltas 和区间、受影响预测清单、token 分布与发生率。历史结果仍在原位置；本目录是追加式更正和解释复核，不能视为新实验。两稿共用 `shared/numbers.tex` 和来自 canonical 重算的 effect-size 图；workflow、证据置换与既有案例保留历史来源。

本轮没有训练、检索、生成、模型选择或新正式算法实验，没有读取 Stage6 Gold、reservation 或 Stage3B。后续正式实验继续暂停；本轮论文交付按授权同步 GitHub。作者、许可、匿名分发及具体投稿对象仍由人工确认，不对外投稿。
