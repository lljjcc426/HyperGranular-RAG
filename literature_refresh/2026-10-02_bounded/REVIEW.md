# 最近邻、主张定位与有限比较复核

2026-10-02；基线 `7a91fa1a4029d5fde85a4277bca1856fc45b306e`。这是同一助手的导师/审稿人双视角，不是两位真人独立背书。来源、日期和阅读深度见 [registry](literature_registry.json)。

## 判断

**任务上最近的是 HGRAG (Wang et al., AAAI 2026)**；构造层面，SAGHL/MGHRL 和粒球模糊粗糙超图特征选择已覆盖“粒球＋超图”的泛化组合。HyperGraphRAG 与 Hyper-RAG 已覆盖实体多元事实的超图 RAG。不能再以这些组合的首次出现定位本项目。

更强算法新颖性判断为 **C_NOVELTY_OR_ACCESS_UNRESOLVED**：SAGHL/TKDE 完整算法和证明尚未取得，不能据摘要宣称同构，也不能排除先行覆盖。已读内容足以收窄主张，不足以宣布本项目重复。

本轮执行决定另为 **D_CONFIRMATION_INDEPENDENCE_UNVERIFIED**：用户接受资源上限，但无法回忆旧确认集是否已影响设计。因此不启动正式计算，不替换确认集。不是方法失败；也没有获得任何新增优势数字。以下比较是建议，不是已锁定/已运行实验。

## 方法对象与可比性矩阵

| 方法 | 输入、对象、构造 | 训练/查询/最终选择 | 评价、成本及对照资格 |
|---|---|---|---|
| SAGHL | 静态同质图；节点是原图对象，拓扑粒球产生层级超边；预览描述中心性 hub 与 modularity-density 分裂 | 多尺度特征融合、分类与对比训练；非 QA 查询选择。完整停止式未读 | 引文/社交图分类、噪声鲁棒性；完整调参、成本、消融未知。构造谱系，非直接 QA baseline |
| TKDE 粒球散度模糊粗糙超图 | 特征选择；GB 散度与模糊粗糙判别关系构建特征超图 | 重要性保留/冗余剪枝、动态加权覆盖；具体标签用法和更新式未取得 | 不能把分类判别性当 QA utility。仅概念比较；移植需另定义特征/证据映射 |
| MGHRL v1 | 输入带特征原图；原节点保留，球成员成超边；高 degree 中心、BFS 最短路分配，约 sqrt(N) 初始中心；Q=2|E|/|V| | 二分与 Q 比较；原文“停止/继续”措辞有歧义，未擅自选实现。多列可逆连接 HGNN，交叉熵监督训练 | 七个节点分类数据集，6:2:2，V100 环境；引言称八个而表列七个，不能照搬宽泛表述。分组/网络两类消融不隔离 QA 选择。无 reader/token 预算 |
| HGRAG (Wang et al., AAAI 2026) | 实体节点、段落超边，LLM 抽实体；语料级 incidence；query 实体/段落相似度决定扩散 | 加权 Laplacian 多步扩散，与原语义分数残差混合；保留 Top-5 并从 Top-10 取共享实体邻段 | H/M/2Wiki 各 1,000 问题的 pooled passage corpus；NV-Embed-v2、Llama-3.3-70B，训练集100问选参数。检索模块计时不等于含抽取全成本。最近直接 QA 邻居；本轮 conceptual only |
| HyperGraphRAG | LLM 抽取实体与带描述的 n-ary 事实超边；二部 incidence 存储、实体/超边向量库 | query 实体及超边双路检索、邻接扩展，融合原 chunks；无需本文这种粒球分裂 | GPT-4o-mini、text-embedding-3-small，实体/边各 Top-60、chunks Top-5；五领域自建问答、F1/语义与LLM评分，另有长度/成本研究。非本项目同池/同 reader 实测；conceptual |
| Hyper-RAG | LLM 抽实体、低阶/高阶关系及描述，合并重复项；原 chunks 保留 | query 实体/关系关键词检索与扩展，Lite 去掉关系检索支路；不属于粒球算法 | 专业领域语料、六种 reader；评分/投票及专家分析，不是本项目 canonical EM/F1。补充预算/抽取成本未完整核实；conceptual |
| 已评估 HyperGranular-RAG static-q25 | benchmark 每问句子候选；embedding 几何分球，query 词面 facets；compact min=2/max=3 下 radius 门冗余 | 无新参数训练/LLM 事实抽取；相对 seeds 一次打分，受保护插入。group-union 不等于实际选中句子 coverage | 20条目、4096输入上限分别约束；MiniLM 正向、Full-BGE 负向、BGE扩展未决。不能用新定义解释旧成绩 |
| 未评估 BU-v2 提案 | 同 backbone Top-100、实际组数/组大小匹配；逐次重算 sentence coverage | 参数显式纯消融；F=C 重复，bridge 项路径依赖；不是已证实的高阶集合目标 | 没有本轮正式预测或确认。既有 v2 synthetic 原型也不等于该提案正式实现/结果 |

来源：[SAGHL](https://doi.org/10.1016/j.engappai.2026.115428)、[TKDE](https://doi.org/10.1109/TKDE.2026.3716345)、[MGHRL](https://arxiv.org/abs/2609.05574v1)、[AAAI](https://doi.org/10.1609/aaai.v40i39.40623)、[NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2025/hash/df55ee6e59f8ac4a625219e11fe9ddba-Abstract-Conference.html)、[Nature](https://doi.org/10.1038/s41467-026-71411-1)。未读的完整参数/成本/消融明确留空，不用相邻文章补全。

## 证明与归因的边界

- MGHRL 的图最短路径论证依赖图距离条件；不连通图、定向边需要另处理。一般有限覆盖不能自动成为任意邻域的基。本文 embedding 的 `1-cos` 不是普遍度量：单位向量夹角依次0°/60°/120°时，端点距离1.5，大于两段0.5+0.5。不能移植最短路径定理。
- HyperGraphRAG Appendix B.1 比较的是丢失关系身份的 clique 编码；B.2 明确 incidence 二部编码可无损恢复成员。换成二部存储不是“去掉高阶”的消融。B.3 的信息、噪声及生成质量单调关系不是本项目已满足的假设，更不构成固定 reader 的答案 F1 保证。
- SAGHL 分类学习、TKDE 特征判别、QA 证据效用是不同目标。任务不同不是无关的理由，也不是证明方法不可替代的理由。
- 历史 compact Facet vs NoFacet 支持那一条具体 selector 对照，不能替代 MMR/coverage/普通分组。球紧致度在任意划分下的性质不是新颖语义分裂证明。固定可见证据的 placement 效应不是内部 attention 机制。

## Claim-to-prior-art 与剩余检验

| 拟议主张 | 先行覆盖/现有证据 | 有意义的剩余问题 | 本轮决定 |
|---|---|---|---|
| 首次粒球＋超图 | SAGHL、MGHRL、特征选择已经覆盖一般组合 | 哪种分组在同预算 QA 选择中有增量 | 不作首创；实际 k/size matched 普通/随机组是必要控制 |
| 首次跨粒度超图 RAG | AAAI 实体—段落，另两篇多元事实 RAG | 无事实抽取的局部句子补全是否超过简单选择 | 差异可描述，不等于增益或理论创新；MMR/实际 coverage 保留 |
| 表示完整所以答案更好 | 各论文在不同假设、语料和 reader 下评价 | 候选质量与放置策略各贡献多少 | 已有固定内容 placement 支持特定策略；证据集合实验仍缺 |
| 粒球/超边独立不可替代 | 历史 NoFacet 不能排除一般覆盖解释 | 纯权重消融、匹配普通组、actual facets vs union | v2未评估，不据其 synthetic 写旧机制成立 |
| 更低成本仍更好 | Top-20 不等于 token 公平；缓存不等于独立生成 | Dense40、共同 cap 下质量—成本 | 保留为未执行比较；历史计时不足以确认 Pareto 优势 |
| 改善现代强检索 | 原 Full 弱于 BGE；两扩展 CI 跨0 | 同候选/同基础分数下结构是否有增量 | 本轮无独立性合格确认，不执行、不判失败 |

## 对照分类与资源资格

**Exact reproduction：本轮没有。** AAAI 原系统的70B抽取/reader，NeurIPS/Nature 的API抽取及语料构建，均未建立本地8GB、零付费、12 GPU小时的可行合同；不自动下载部署。别人的表格分数不拼入本项目排行榜。

**Adapted controlled baseline：仅提案。** 可考察同候选的实体—段落扩散，但若换成词面实体/本地抽取器、固定Top-20、共享reader，即改变抽取与预算；必须标改编，不能称复现AAAI。SAGHL/MGHRL移植还需先定义从句子构图的邻接、开销和监督，不能只换名字。当前确认限制下均不运行。

**Conceptual comparison：本轮已完成上述六者的有读深度限制比较。** 核心实验卡保留简单控制，不把这些昂贵系统的缺席伪装成已胜出。资源可用于哪些实际调用尚未校准；历史耗时只作为计划参考，不承诺73844次一定在上限内。

## 双视角处理与写作落实

导师：采用“选择哪些证据＋如何安排证据”的窄问题；拒绝泛化组合首创；部分采用移植扩散建议，因预算/独立性不具执行资格。审稿人：采用最近邻与命名纠正、对照公平性要求；拒绝“未找到一模一样便是新方法”以及“所有结构化方法已等同”的推断。

因此本轮不提高投稿级别承诺。以已有正向、负向及未决证据完成会议/期刊分析型稿件，完整方法和局限保留。两版新源码在 `research/2026-10-02_bounded_upgrade/manuscripts/`，新 bibliography 去重文件为其 `shared/references.bib`；本目录 `MANUSCRIPT_DIFF.patch` 记录相对旧终稿的文字/表格差异（构建收尾生成）。

显示映射：我们的正文使用 **HyperGranular-RAG**；AAAI用 **HGRAG (Wang et al., AAAI 2026)**；NeurIPS用 **HyperGraphRAG (Luo et al., 2025)**；Nature用 **Hyper-RAG (Feng et al., 2026)**。历史 IDs、缓存、代码不替换。图片/绘图脚本不改；当前稿沿用的 workflow 已写 closed candidates，检查未发现必须改图才能区分两方法的裸 HGRAG 标签。未回溯重做历史所有图形；以后若使用更早图片，需另行检查命名，不全仓替换。
