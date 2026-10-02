# HyperGranular-RAG 双版本编辑终稿

- [会议版 PDF（总计 9 页）](conference/HyperGranular-RAG_Conference.pdf) · [LaTeX 正文](conference/main.tex)
- [期刊版 PDF（总计 21 页）](journal/HyperGranular-RAG_Journal.pdf) · [LaTeX 正文](journal/main.tex)
- [编辑验收、修改位置与逐页检查](FINAL_EDITORIAL_CHECK.md)

本轮以 `790cbb38de60b98d71074756b3e72b8f1a0f4ce4` 的 revision2 为基线，仅做论文编辑与本地构建。两稿围绕“选择什么证据”和“怎样安排证据”组织论证，修正过强否定与“最佳”的预设，保留 MiniLM 正结果、原 Full 弱于 BGE、BGE 扩展及生成器迁移未决的结论。

数值与解释依据：[revision2 主张影响](../2026-10-02_revision2/CLAIM_IMPACT.md)、[评分核查](../2026-10-02_revision2/SCORER_LINEAGE_AND_MIGRATION.md)、[固定可见证据与预算核查](../2026-10-02_revision2/PLACEMENT_AND_VISIBLE_CONTEXT_AUDIT.md)。本轮没有重新评分、重建 prompt 或运行实验。74,750 是跨方法的预测记录数，不是独立样本量。

两稿共用未改动的 `shared/` 数值、图表、参考文献和复现细节。`EDITORIAL_INVARIANTS.json` 记录与 revision2 的源文件静态对照；`conference/` 和 `journal/` 下保存实际构建日志、文本提取、逐页图像及 `BUILD_STATUS.json`。

本地构建命令（仓库根目录，已有 MiKTeX 与 Python 文档环境）：

```powershell
.\temp\dual_manuscripts_env\Scripts\python.exe paper/versions/2026-10-02_editorial_final/check_editorial_invariants.py
.\temp\dual_manuscripts_env\Scripts\python.exe paper/versions/2026-10-02_editorial_final/build_manuscripts.py conference journal
```

重新构建会将自动生成的视觉检查字段重置为 `PENDING`；只有实际查看新 PDF 后才能更新。当前交付已完成该检查。

页数包含摘要、正文、图表、伦理说明、参考文献与附录，具体分布见验收记录。作者、单位、许可、匿名材料分发及具体 venue 待人工确认；“编辑终稿”不代表已满足任何尚未选定 venue 的格式/篇幅要求。旧稿与 revision2 均保留，本轮结束，不自动启动新实验或审计。
