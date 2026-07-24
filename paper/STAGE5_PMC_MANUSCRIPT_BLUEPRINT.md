# Stage5-PMC Manuscript Blueprint

## Working title

**Protected High-Order Evidence Completion for Compact Dense Multi-Hop Retrieval**

备选：

- **HyperGranular-RAG: Structured Evidence Completion under Constrained Retrieval Budgets**
- **When Structured Expansion Helps—and When It Does Not: A Verified Study of HyperGranular Retrieval-Augmented Generation**

## Central thesis

HyperGranular-RAG 不是强稠密检索器的通用替代品，而是面向紧凑稠密检索主干的结构化证据补全层。自适应粒球组织局部单元，query-aware facet hyperedge 建模跨粒球关系，protected insertion 在固定 Top-k 预算中限制结构扩展。该组合在多个冻结 closed-candidate 多跳 QA 边界上稳定改善历史 MiniLM Dense；facet-hyperedge 的系统内增量价值和 protected placement 的相对优势获得支持。与此同时，完整方法明确弱于 BGE strong dense，强检索 sidecar 互补性和额外生成器迁移均不确定。

## Argument chain

1. 多跳回答需要的不只是单点相关性，还需要在有限上下文中补全跨段证据。
2. HyperGranular-RAG 将结构扩展限制为 Gold-free、bounded、prefix-protected 的 evidence-completion 操作。
3. 在 Qwen 和历史 MiniLM Dense 边界中，Static q25 的小幅 answer-F1 增益跨 HotpotQA、MuSiQue 和 Stage4H 新样本重复出现。
4. Stage4H 说明 facet-hyperedge 在冻结系统内有增量价值，但也明确揭示 Full 低于 BGE strong dense。
5. Stage4I 进一步区分“候选是否有互补价值”和“同一候选如何放置”：前者不确定，后者支持 protected placement。
6. 因此，允许的结论是受边界约束的 compact-dense evidence completion，而不是普遍检索优势。

## Abstract scaffold

### Background

Dense retrieval ranks locally relevant evidence effectively, but a constrained Top-k context can still omit complementary passages needed for multi-hop reasoning. Structure-aware expansion may recover such evidence, yet it can also displace stronger ranked items.

### Method

We introduce HyperGranular-RAG, a Gold-free structured evidence-completion layer that combines adaptive granular-ball organization, query-aware facet hyperedges, and bounded insertion after a protected dense prefix.

### Results

Across frozen closed-candidate HotpotQA and MuSiQue evaluations with Qwen2.5-1.5B-Instruct, the static method repeatedly improved answer F1 over a historical MiniLM dense backbone. A component study supported the incremental contribution of facet hyperedges within the frozen MiniLM system. However, the full method was inferior to a pre-specified BGE strong-dense baseline. Adding the same HGRAG system as a BGE sidecar yielded inconclusive complementarity, while protected placement outperformed unprotected placement for an identical inserted set. Transfer to one official Gemma mobile-QAT configuration was also inconclusive.

### Conclusion

The evidence supports HyperGranular-RAG as a bounded evidence-completion layer for compact dense backbones, not as a universal replacement for strong dense retrieval. Positive, negative, inconclusive, and undefined component evidence are reported together.

## IMRaD structure

### 1. Introduction

- 问题：有限 Top-k 中的相关性排序与多跳证据完备性存在张力。
- 方法定位：structured evidence-completion layer for compact dense backbones。
- 贡献：
  1. 自适应粒球局部组织；
  2. query-aware facet hyperedge；
  3. protected bounded insertion；
  4. 跨冻结数据边界的端到端验证；
  5. 强基线负结果、互补性不确定和不可公平消融的完整报告。
- 明确声明：不是普遍 strong-dense 优越性或 full-wiki/open-domain 结论。

### 2. Related Work

需要经正式文献检索与引用核验后写入：

- dense passage retrieval and multi-hop retrieval；
- graph/hypergraph and structure-aware retrieval；
- retrieval augmentation under context budgets；
- RAG evaluation, answer faithfulness and evidence coverage；
- negative-result and reproducibility practices。

当前不得填入未经核验的引用或 DOI。

### 3. Method

#### 3.1 Problem definition

定义 query \(q\)、closed candidate unit set \(U_q\)、Dense ranking \(D_q\) 和 effective Top-k。

#### 3.2 Adaptive granular balls

描述 deterministic split、centroid、radius、compactness、minimum child size 和 Gold-free 输入。

#### 3.3 Query-aware facet hyperedges

描述 query facets、seed balls、cross-ball candidate edges、frozen gates 和 unit ordering。

#### 3.4 Protected bounded insertion

定义 Dense Top-10 protection、q25 floor、最多四项插入和最终 effective-K ≤ 20。

#### 3.5 Separated controller branch

U1/Stage4C/Stage4D 作为独立负结果与机制诊断，只用于说明静态方法与动态选择不是同一主张。不得让 controller 失败覆盖静态方法证据。

### 4. Experimental design

- 数据：HotpotQA 与 MuSiQue 的冻结 closed-candidate 边界；
- 主干：历史 MiniLM Dense；强基线：冻结 BGE large-en-v1.5；
- 生成器：主评价使用冻结 Qwen；迁移评价使用一个官方 Gemma mobile-QAT 配置；
- 主要端点：paired answer F1；配套 EM、CR@20、ER@20；
- 统计：冻结 10,000 query bootstrap 与预登记 decision gates；
- 完整性：Gold-free retrieval/generation、独立 verifier、main/rerun 或 pre-hash subset determinism；
- 限制：非 full-wiki、非开放域、样本量是资源/精度边界而非功效保证。

### 5. Results

#### 5.1 Repeated gains over compact MiniLM Dense

用核心表 1 和 Figure 2 报告 Stage4E、Stage4F 与 Stage4H 的 Dense-vs-Full 结果。强调增益小、Stage4E 下界接近 0、所有结论限于冻结边界。

#### 5.2 Component evidence

用核心表 3 报告 facet supported、protection inconclusive、flat not fairly defined。不得把不确定写成等价。

#### 5.3 Strong-dense boundary

用核心表 2、Figure 2、Figure 3 报告 Full−BGE 明确负向与 Protected−BGE 不确定。Stage4I 的 added/displaced/net Gold 只作 post-decision 描述。

#### 5.4 Placement within an identical inserted set

报告 Protected−Unprotected 的支持性结果，并明确它不能替代 Protected−BGE 核心比较。

#### 5.5 Generator transfer

报告一个额外 Gemma official mobile-QAT 配置的联合不确定结果；不作纯架构、普遍 RAG 适用性或跨设备效率结论。

#### 5.6 Efficiency and integrity

用核心表 4 报告 calls、失败率、wall time、GPU 峰值、缓存与确定性合同。不同方法/模型/阶段的 wall time 只作实测描述，不作无控制硬件或架构排名。

### 6. Discussion

- 为什么 compact dense 可能受益：局部证据缺口与跨粒球关系；
- 为什么 strong dense 边界不同：更强主排名已吸收部分补全信号，插入同时产生新增和置换；
- placement 的作用与 sidecar efficacy 的层级差异；
- 静态扩展与学习型 controller 的不同难度；
- 负结果、不确定结果和 undefined ablation 对主张边界的约束；
- 适用范围与后续 full-wiki feasibility 的非阻塞地位。

### 7. Limitations

- closed-candidate，而非 full-wiki/open-domain；
- 主要正结果来自单一 Qwen；
- Gemma 只是一种 official mobile-QAT 配置；
- BGE 只绑定一个 strong-dense backbone；
- flat granular-ball control 未公平定义；
- protected insertion 独立消融不确定；
- post-Gold mechanism audit 不是确认性 efficacy；
- HotpotQA train 只保证未被本项目读取，不能保证不在生成器预训练语料中；
- 样本量不是正式功效保证。

### 8. Reproducibility and integrity statement

列出 source/config/model/environment SHA、Gold 隔离、确定性复跑、independent verifier、正式工件 manifest 与负/不确定结果保留规则。

## Main-table plan

1. Main results: Dense vs Full on Stage4E, Stage4F and Stage4H boundaries.
2. External robustness: Gemma transfer, BGE strong dense and BGE sidecar.
3. Ablation: facet, protection, placement and undefined flat control.
4. Efficiency and integrity: calls, failures, runtime, GPU, cache, determinism.

## Main-figure plan

1. Method overview: compact dense → granular balls/facet hyperedges → protected insertion.
2. Stage4E–Stage4I answer-F1 effect-size forest.
3. BGE/Protected/Unprotected answer quality and Gold-evidence displacement.
4. Positive/negative/inconclusive/undefined evidence map.
5. Applicability boundary: compact dense, strong dense, generator and open-domain.

## Current non-scientific submission blockers

- 目标期刊/会议和篇幅模板尚未确定；
- 作者顺序、单位、通讯作者、基金与利益冲突信息未提供；
- 外部文献 corpus、verified bibliography 与 DOI 映射尚未建立；
- 数据与模型许可在投稿格式中的声明尚未完成；
- 摘要字数、图表数量和补充材料结构需按目标 venue 调整。

这些缺口不要求新增算法实验，也不改变 Stage4E–Stage4I 结论。
