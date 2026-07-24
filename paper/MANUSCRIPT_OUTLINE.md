# HyperGranular-RAG 论文结构草案

## 暂定中心问题

静态、受保护的超边证据补全能否在保留 Dense 主干的同时改善多跳证据覆盖，并最终转化为答案质量收益；若按 query/candidate 选择性削减扩展，为什么当前无标签 controller 没有成功？

## 1. Introduction

- 多跳 RAG 的核心张力：Dense relevance、跨证据链补全与上下文成本。
- 静态方法贡献：粒球组织、query-aware facet hyperedge、Dense prefix protection、bounded insertion。
- controller 作为独立失败研究：资源下降不等于选择有效。
- 明确贡献层级：retrieval evidence、negative controller evidence、mechanism diagnosis、Stage4E E2E validation、Stage4F cross-dataset replication、Stage4G one-additional-generator transfer test，以及 Stage4H component/strong-baseline boundary。

## 2. Method

### 2.1 Sentence units and dense retrieval

定义 per-query unit pool、encoder、cosine ranking 与 effective-K。

### 2.2 Granular balls and query-aware hyperedges

给出 ball split、facet term、candidate edge 与 Gold-free 约束。

### 2.3 Static protected insertion

定义 Dense Top-10 protection、q25 floor、最多四项插入和 final Top-20。静态方法不含 U1/controller。

### 2.4 Adaptive-controller branch

将 U1-D、Stage4C、Stage4D 作为单独研究线描述，避免把失败 controller 混入静态方法定义。

## 3. Experimental Design

- Stage2F：内部 frozen-threshold retrieval evidence。
- Stage4A-R2 / Stage4B：官方 2Wiki development 的 gain/harm 与 controller 评价。
- Stage4C/4D：同一 development 上预冻结的 exploratory mechanism audits。
- Stage4E：此前未读 HotpotQA train ID-hash sample，Dense vs static q25，同一固定 generator；主 endpoint 为 paired answer F1。
- Stage4F：预注册 MuSiQue train 新 ID 跨数据集复制；3,000-query official transaction 与独立 final verification 已完成。
- Stage4G：完全复用 Stage4E/4F frozen inputs/rankings，只更换为一个事前指定的 Gemma official mobile-QAT 配置；数据集等权联合统计和独立 final verification 已完成。
- Stage4H：新的 HotpotQA 1,000 + MuSiQue 1,500 零重叠边界；固定 Qwen；七个 P0 retrieval/ablation arms；四个 Holm-adjusted 主要比较；full main + 预哈希分层 subset rerun；final verification 已完成。
- 每阶段列出数据角色、Gold 隔离、复现绑定、样本/功效限制和停止规则。

## 4. Results

### 4.1 Retrieval evidence

只写已验证 Stage2F、Stage4A-R2 与 Stage4B retrieval 结果，区分 primary gate 与 secondary evidence。

### 4.2 Controller negative result

完整报告 40% 资源目标、retention gap、Fisher、Dense/q25 CR 对照与 2/6 gates。

### 4.3 Failure mechanisms

Stage4C 写 query-level composition；Stage4D 写 candidate labels、Task-C AUROC/AP/Brier 与 budget-region audit。两节都标记 `CAUTION`。

### 4.4 End-to-end answer quality

报告 Stage4E verified final：Dense/static-q25 answer F1 `0.42150/0.43628`，paired delta `+0.01478 [0.00020,0.02988]`；EM `0.356/0.366`，delta `+0.01000 [-0.00500,0.02500]`；CR@20 `0.737/0.798`。写明 `STATIC_HGRAG_E2E_SUPPORTED`、F1 下界接近 0、subgroup 仅 `CAUTION`，并报告 main/rerun 与 independent verifier。

### 4.5 Cross-dataset replication

报告 Stage4F verified final：MuSiQue Dense/static-q25 answer F1 `0.13595/0.14735`，paired delta `+0.01140 [0.00450,0.01835]`；EM delta `+0.01000 [0.00333,0.01667]`；supporting-paragraph CR@20 `0.589/0.650`。写明 `STATIC_HGRAG_XDR_SUPPORTED`、与 Stage4E 方向一致、12,000 calls 零失败、main/rerun 字节一致及 final independent verification；hop-count 只作 `SUBGROUP_CAUTION`。

### 4.6 Generator-transfer replication

报告 Stage4G verified final：

- Gemma HotpotQA Dense/static-q25 F1 `0.34978/0.36243`，delta `+0.01265 [-0.00220,0.02744]`；
- Gemma MuSiQue Dense/static-q25 F1 `0.04476/0.04244`，delta `-0.00232 [-0.00685,0.00208]`；
- dataset-equal-weight F1 delta `+0.00516 [-0.00262,0.01295]`，EM delta `+0.00233 [-0.00567,0.01033]`；
- `GENERATOR_TRANSFER_INCONCLUSIVE`、8,000-call main 零失败、400-call stratified subset 精确复现和 final independent verification；
- 与冻结 Qwen retrieval delta 的 interaction 只作描述性解释，不进入主判定。

### 4.7 Component ablation and strong baselines

报告 Stage4H verified final：

- Full−historical Dense 等权 F1 `+0.01357 [0.00491,0.02233]`，`SUPPORTED`；
- Full−BGE strong dense 等权 F1 `-0.03998 [-0.05393,-0.02621]`，`NEGATIVE`；
- Full−NoProtection `+0.00354 [-0.00675,0.01389]`，`INCONCLUSIVE`；
- Full−NoFacet `+0.01336 [0.00341,0.02343]`，`SUPPORTED`；
- flat-unit granular-ball ablation 为 `NOT_FAIRLY_DEFINED`；P1 effect-cost curve 为 `NOT_RUN_RESOURCE_BOUNDED`；
- BM25/hybrid 全量报告但不触发 advancement；
- 17,500-call main、1,400-call subset、Gold 隔离与 final independent verification。

## 5. Discussion

- retrieval gain 在 HotpotQA 与 MuSiQue 两个冻结边界上转化为小幅 answer-F1 gain；讨论 evidence sufficiency、context ordering、generator utilization 与多数 query answer-F1 不变的现象。
- 静态扩展与动态选择的不同难度。
- 当前 controller 的 displacement harm 与 mixed gain/noise 结构。
- 两个数据集仍是 closed candidate pool；Stage4G 只增加一个 Gemma mobile-QAT 配置且迁移判定 inconclusive，对外部效度和 generator robustness 的限制。
- 讨论 MuSiQue 上 negative generator interaction，但不得从该描述性结果推导模型架构优劣或调整 retrieval。
- Stage4H 表明论文主张必须区分“相对历史 MiniLM Dense 的小幅增益”与“相对 BGE strong dense 的明确不足”；讨论强 encoder 能否吸收静态扩展所补充的信号。
- facet-hyperedge 在冻结系统中有增量价值，但 protected insertion 的独立贡献不确定；不得把消融写成普遍因果机制。

## 6. Reproducibility and Integrity

- 代码/config/data/model SHA；
- blind/Gold channel；
- Stage4E/4F full main/rerun byte identity 与 Stage4G pre-hash stratified subset exact reproduction；
- independent verifier；
- negative/inconclusive result preservation；
- 11 类统计谬误扫描。

## 7. Limitations

- 当前静态 retrieval 阈值来自早期开发数据；
- Stage4B-D 共享同一 2Wiki development，不是外部验证；
- Stage4E boundary 是 HotpotQA same-domain distractor candidate pool，不是 full-wiki；
- Stage4E/4F 的正结果来自单一 Qwen；Stage4G 只测试一个额外 Gemma mobile-QAT 配置且联合结果 inconclusive，仍不能外推到所有 LLM；
- `n=1000` 是资源边界，不是正式功效保证。
- HotpotQA train 只保证对本项目研究流程未读，不能保证对预训练生成器无污染；参数化记忆可能压低或改变 retrieval-arm 差异。
- Stage4F 的 `n=3000` 同样只是资源/精度边界；MuSiQue Gold 为 supporting paragraph，不支持句子级 Gold 主张。
- Stage4F 是跨数据集而非 full-wiki/open-domain；Stage4G 也不能把一个额外配置的 inconclusive 结果概括为普遍生成器鲁棒性。
- Stage4G 中 Gemma 架构、mobile-QAT 与数值格式效应不可分离，不能进行纯基础模型架构排名。
- Stage4H 仍是 closed-candidate；BGE negative 结果限制当前方法相对强检索器的竞争力。
- flat-unit 对照没有公平定义，不能单独确认 granular-ball 结构；protected insertion 区间跨 0。
- Stage4H 的 P1 效果—成本曲线因资源边界未运行，不能给出新的最优 prefix/budget。

## 下一步论文材料

- Figure：Dense 与 static q25 的 answer F1/EM paired difference；
- Figure：retrieval CR change 与 answer F1 change 的 query-level joint audit（描述性，不作因果）；
- Figure：Stage4E/4F Qwen 与 Stage4G Gemma 的 dataset-specific retrieval delta 及区间；只展示交互，不作模型能力排名。
- 将 Stage4E/4F/4G 的 exact data/model/environment SHA、绝对指标、区间、context tokens、runtime、prompt、schema、decision gate、determinism 与 independent verification 整理为主文表和附录。
- 将 Stage4H 七臂结果整理为主文消融/强基线表；正文明确保留 strong-dense negative、no-protection inconclusive 与 flat not-defined。
- 下一阶段仅起草 `Stage4I-FWF` full-wiki feasibility：索引、ANN、candidate reachability、延迟、成本和可验证合同；不直接启动 full-wiki Gold。
