# 双稿编辑终稿验收

基准：`790cbb38de60b98d71074756b3e72b8f1a0f4ce4`；写作依据为已接受的 revision2。状态：`EDITORIAL_FINAL_BUILT_AND_REVIEWED / SUBMISSION_METADATA_PENDING`。

## 稿件与实质修改

- [会议版](conference/HyperGranular-RAG_Conference.pdf)：聚焦完成层的答案质量、具体 selector 比较及固定可见证据的 placement 对照。
- [期刊版](journal/HyperGranular-RAG_Journal.pdf)：同一证据主线，保留完整方法差异、直接相关的数学解释、证据置换、案例与成本。没有新增实验贡献。

| 修改位置 | 修改内容 |
|---|---|
| 两稿 Abstract、Introduction | 以“选择证据—安排证据”为主线；将完整管线、指定 selector、固定内容下的 ordering 三类比较明确对应到不同主张。摘要保留正、负及未决结果，移出评分纠错与未评估原型的过程叙述。 |
| 会议 §8 Conclusion | 将 “does not make its candidates useful relative to BGE” 改为未建立相对 BGE 的答案质量增益。 |
| 期刊 §8.3、§10 | 将 “Protected does not improve on BGE” 及同类否定改为比较未建立增益；不把跨零区间写成无效或等效。 |
| 期刊 §8.1 | 删除 “why granular-ball organization is the best way” 的预设，明确尚未证明优于普通聚类或直接选择规则。 |
| 会议 §5.2、§6.4；期刊 §5.1、§7.1、§8.3 | 位置对照为固定可见证据的排序/放置策略；原始全体查询仍为效应分母，不作 attention 机制推断。 |
| 两稿方法、实验说明及附录 A | 减少重复 historical/frozen/repaired 叙述；保留 static seed-relative、半径门冗余、native 几何/打分差异和非纯 NoFacet 消融。评分谱系与具体更正明细集中到附录，正文保留实质影响及统计限制。 |
| 两稿图表引用；期刊附录 A | 补正文到已有 workflow、effects、strong-results、case、cost 图表的引用；长 scorer 版本号显式换行，修复超出版心。 |

中文故事链：有限条目预算下，补入桥接事实既涉及选择，也涉及排序和挤出。完整管线在测试的 MiniLM 边界有重复增益，指定 facet selector 比较有支持；这些比较尚不能证明粒球或高阶关系不可替代。固定可见证据的 sidecar 对照支持 protected 相对 front insertion 的排序收益，但不能替代其相对 BGE 的未决比较。原 Full 弱于 BGE、两种 BGE 扩展与生成器迁移未决共同限定适用范围。

## 数值与证据未变

`check_editorial_invariants.py` 实际执行通过，输出见 [EDITORIAL_INVARIANTS.json](EDITORIAL_INVARIANTS.json)。两稿显示公式、行内数学表达式多重集、表体、引用键与 revision2 一致；整个 `shared/` 逐文件字节一致，包括数值宏、canonical effect 数据、所有图表、参考文献及复现说明。全部带编号的正文图表均有引用。

人工核对：MiniLM 三个 F1 增益仍为 +0.01478、+0.01140、+0.01357；Full−BGE 为 −0.03998；sidecar−BGE 为 −0.00256；native−BGE 为 −0.00305；Gemma 为 +0.00516；Protected−Unprotected 为 +0.01122。各自区间、比较集合与权重沿用 revision2，图中百分点与正文 0–1 分数尺度已区分。

74,750 明确为预测记录数；53,500 条确认/迁移记录评分不变、开发集同一道题的 17 条更正不改变方法差值，均为 revision2 的已接受发现，本轮未重新执行。Stage4I 沿用全部 2,500 对固定可见证据、无截断的核查；不缩减为排序改变的事后子集。Top-20 条目预算与 4,096-token 输入上限分开说明。

## 实际构建及逐页检查范围

MiKTeX pdfLaTeX/BibTeX 实际生成两份新 PDF，所有构建命令退出 0。最终日志无 undefined citation/reference、multiply-defined label 或 overfull box；会议模板保留若干 underfull 间距提示，目视未发现裁切或重叠。

| 版本/页码 | 已查看内容 |
|---|---|
| 会议 1、2、3 | 标题/匿名占位、摘要/贡献、引用、方法公式与 gate、预算/版本差异。 |
| 会议 4、5、6 | workflow、评分/区间解释、主表及结果、forest plot、固定内容位置归因、结论。 |
| 会议 7、8、9 | component plot、伦理与参考文献、native 定义、评分计数、几何解释、复现附录。 |
| 期刊 1、2、3 | 标题/匿名占位、摘要/引言、相关工作、方法定义。 |
| 期刊 4、5、6 | static selector、placement、workflow、native 差异、compactness 证明与稳定性说明。 |
| 期刊 7、8、9 | 标准覆盖界、边界表、生成/评分/统计定义、非新增确认的说明。 |
| 期刊 10、11、12 | 主结果、组件图、BGE 绝对分数与区间、效应图、固定成员与 prompt 证据的论证。 |
| 期刊 13、14、15 | token 表、置换与插入图、案例、成本表/单位、非机制推断边界。 |
| 期刊 16、17、18 | 讨论与三处指定措辞、局限/结论、伦理与参考文献。 |
| 期刊 19、20、21 | 历史映射与更正明细、长版本号换行、术语表、未评估扩展反例、复现细节。 |

检查方式：两稿所有页面均渲染并逐页查看；局部修正后重新构建，复查最终分页联系图和改动区域的单页图。图注、公式和引用结合源文件与提取文本核对。原始页面图、最终构建日志均随稿保存。本轮不是对引用文献全文或原始预测的再次审计。

会议版共 **9 页**：摘要/正文至结论在 1–6 页，正文图3与伦理说明在第7页；参考文献在 7–8 页；附录在 8–9 页。期刊版共 **21 页**：摘要/正文（含局限、结论）在 1–17 页，伦理说明在第18页，参考文献在 18–19 页，附录在 19–21 页。共享页面不能按这些区间简单相加。

## 文件范围与人工待办

新增 `paper/versions/2026-10-02_editorial_final/`，含两稿、复用的展示资产、实际构建/视觉记录及本说明；根 README 仅更新论文导航。没有删除文件、覆盖 revision2、改写历史结果或修改实验源码。工作区原有审计/工程 dirty changes 保留，不纳入本轮提交。

需人工确认：作者及排序、单位、基金/利益冲突、许可、AI 使用披露的最终措辞、匿名材料分发方式、具体 venue/track 及其模板/篇幅规则。会议稿沿用 ACL review 模板，其 “Anonymous ACL submission” 是模板占位，不代表已经决定或执行投稿。期刊稿为通用 article 排版，不宣称符合某一期刊格式。

本轮没有新实验、受限数据读取、确认配置更改、统计决策替换或对外投稿；Git 仅同步上述 allowlist。编辑交付后停止，不自动建立下一轮研究任务。
