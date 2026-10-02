# 有限升级与文献刷新：最终交付

## 先看论文

- [会议版完整英文稿 PDF：10页](manuscripts/conference/HyperGranular-RAG_Conference.pdf)
- [期刊版完整英文稿 PDF：23页](manuscripts/journal/HyperGranular-RAG_Journal.pdf)
- [源码、构建与数值检查](manuscripts/README.md)
- [实际编辑与逐页检查范围](manuscripts/FINAL_EDITORIAL_CHECK.md)

本轮没有新增实验优势，因此没有依据升级投稿目标。完成的科学价值是澄清
先行工作覆盖、实际方法差异和仍未验证的归因，而不是补出正向性能数字。
保留 MiniLM 正结果、原 Full 弱于 BGE、BGE 扩展与生成器迁移未决；不把
未运行的匹配对照写成方法失败。

## 两个不同的决定

1. `C_NOVELTY_OR_ACCESS_UNRESOLVED`：更强的算法新颖性尚未建立。
   任务上最近的是 Wang 等的 Cross-Granularity HGRAG (AAAI 2026)；
   SAGHL/MGHRL/特征选择工作已覆盖一般“粒球＋超图”组合，
   HyperGraphRAG/Hyper-RAG 已覆盖实体多元关系 RAG。不能宣称这些组合首创。
   SAGHL、TKDE 完整正文未取得，不据摘要断言本项目与之相同，也不排除覆盖。
2. `D_CONFIRMATION_INDEPENDENCE_UNVERIFIED`：执行资格不足。
   用户接受本机 GPU 12小时、CPU 24小时、新增磁盘10GB、付费0的累计上限；
   对旧 confirmation 是否在其他工具/人工分析中被查看并影响设计，回答“不记得了”。
   仓库没有相应成绩不能证明未暴露。本轮未运行开发选择或正式确认，也未另找确认集。
   这不等于确认集已经污染，更不等于方法失败。

导师/审稿人双视角由同一助手分别分析，不冒称两位独立专家认可。
采用 academic-research-suite 的设计复核、来源分级和修订流程；
文献检查到有限范围即结束，不扩大为新一轮全仓审计。

## 本轮三项问题的实际状态

| 问题 | 保留的最小比较 | 状态 |
|---|---|---|
| 原有效设置的额外价值 | MMR、实际句子 coverage、实际组数/组大小匹配、纯组件对照 | 未执行；现有 NoFacet 不能替代这些对照 |
| 质量—成本 | Dense40、共同 token cap、真实模型调用与可见证据 | 未执行；Top-20 和平均 tokens 不证明逐题预算相同 |
| 强检索增量 | 共享候选与基础分数的现有 Qwen3 设置 | 未执行；没有新独立确认结论 |

`UPGRADE_PROTOCOL.md` 保留一次有限提案及最终停止说明，不是事后登记的已执行协议。
其 F=C 重复与路径依赖 bridge 项需要科学定义处理；没有为维护名称添加模块。
旧 static-q25、BGE-native 和未评估 BU-v2 不混写。

## 文献与稿件交付

- [有限检索日志](../../literature_refresh/2026-10-02_bounded/SEARCH_LOG.md)：一次定向搜索和一次引文/版本追溯。
- [来源、发表状态、日期与阅读深度登记](../../literature_refresh/2026-10-02_bounded/literature_registry.json)：未知日期留空；Crossref 创建日期不冒充首次在线日期；MGHRL 仅为预印本。
- [比较矩阵与双视角审核](../../literature_refresh/2026-10-02_bounded/REVIEW.md)：任务、结构对象、构造、训练、事实抽取、候选选择、预算、评价、成本、定理及消融边界。
- [正文与文献差异](../../literature_refresh/2026-10-02_bounded/MANUSCRIPT_DIFF.patch)。

两稿以“选择什么证据—怎样安排证据”为主线，新增概念比较和证据缺口表，
未改已有数值表。新正文区分 HyperGranular-RAG 与 HGRAG (Wang et al., 2026)；
历史 method IDs、缓存、结果、图及绘图脚本均不改。
所有外部方法比较均为 conceptual comparison；没有把改编建议标成 exact reproduction。

## 投稿回退与人工信息

[目标核实及中文故事链](TARGETS_AND_STORY.md) 以官方范围和作者指南为依据。
优先候选是 Journal of Intelligent Information Systems 的完整研究稿；
会议备选为 ARR long paper → NAACL 2027 的受控经验分析路线。
不宣称录用保证、顶刊升级或已核实 NAACL Findings 分流。
两稿为同一证据的替代稿，不可作为两篇独立工作同时投稿。

作者、单位、许可、声明、最终模板、匿名要求及截止日期须人工确认。
当前 10/23 页包含参考文献和附录，不意味着已经符合最终 venue 模板要求。
没有对外投稿、注册或付费。

## 实际检查、成本和文件范围

两版实际编译；全部33页做 contact-sheet 版面检查，选定页面另做高清检查，
精确范围见编辑记录。文档检查通过：15个非文献 shared 文件与旧版完全一致，
公式、旧表格、引文、匿名信息和交叉引用检查通过。未做算法测试或真实重评分，
因为本轮没有算法改动；不存在虚构的实验 PASS。

新增生成调用0、reranker调用0、实验 GPU时间0、付费0。文献下载、写作和
LaTeX 构建产生少量本地文件；文档 CPU 时间未连续计量，不填造累计小时数。
资源上限与计划调用上界见 `budget_manifest.json`；其中计划量不是已发生量。

新增文件只在本轮 research 与 literature_refresh 目录；README 顶部增加当前入口。
构建脚本仅对本轮副本补充一次 LaTeX 引用收敛 pass；增加文档不变量检查脚本。
没有删除文件。旧论文、冻结工件及本轮开始时的未提交工程/审计工作保留。
Git 提交范围限上述新目录和 README 新增入口，不混入既有 dirty diff。
提交前对照本轮起始快照确认67个既有本地文件保留；README 仅增加顶部入口，
其原有未提交修改仍留在工作区。暂存 allowlist 检查通过，删除文件数为0。

## 停止边界

本轮按升级证据不足/资格未核实的回退分支完成文稿，不自动恢复实验。
受限数据、reservation、Stage3B、Stage6B/C、full-wiki、付费 API、
大型外部方法部署和新 controller 均未解锁。
将来若要解决缺少的实证控制，需要先解决独立确认来源和科学定义；
本轮没有寻找替代确认集，也没有把旧授权扩展成新实验授权。
