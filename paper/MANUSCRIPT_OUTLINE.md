# HyperGranular-RAG 论文结构草案

## 暂定中心问题

静态、受保护的超边证据补全能否在保留 Dense 主干的同时改善多跳证据覆盖，并最终转化为答案质量收益；若按 query/candidate 选择性削减扩展，为什么当前无标签 controller 没有成功？

## 1. Introduction

- 多跳 RAG 的核心张力：Dense relevance、跨证据链补全与上下文成本。
- 静态方法贡献：粒球组织、query-aware facet hyperedge、Dense prefix protection、bounded insertion。
- controller 作为独立失败研究：资源下降不等于选择有效。
- 明确贡献层级：retrieval evidence、negative controller evidence、mechanism diagnosis、Stage4E E2E validation。

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
- Stage4F：预注册 MuSiQue train 新 ID 跨数据集复制；当前仅 source/input/Level B 就绪，无正式结果，不进入 Results。
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

## 5. Discussion

- retrieval gain 在本次冻结边界上转化为小幅 answer-F1 gain；讨论 evidence sufficiency、context ordering、generator utilization 与 921/1000 query answer-F1 不变的现象。
- 静态扩展与动态选择的不同难度。
- 当前 controller 的 displacement harm 与 mixed gain/noise 结构。
- same-domain closed candidate pool 对外部效度的限制。

## 6. Reproducibility and Integrity

- 代码/config/data/model SHA；
- blind/Gold channel；
- main/rerun byte identity；
- independent verifier；
- negative/inconclusive result preservation；
- 11 类统计谬误扫描。

## 7. Limitations

- 当前静态 retrieval 阈值来自早期开发数据；
- Stage4B-D 共享同一 2Wiki development，不是外部验证；
- Stage4E boundary 是 HotpotQA same-domain distractor candidate pool，不是 full-wiki；
- 生成器固定为单一小型模型时，结论不能外推到所有 LLM；
- `n=1000` 是资源边界，不是正式功效保证。
- HotpotQA train 只保证对本项目研究流程未读，不能保证对预训练生成器无污染；参数化记忆可能压低或改变 retrieval-arm 差异。
- Stage4F 的 `n=3000` 同样只是资源/精度边界；MuSiQue Gold 为 supporting paragraph，不支持句子级 Gold 主张。

## 下一步论文材料

- Figure：Dense 与 static q25 的 answer F1/EM paired difference；
- Figure：retrieval CR change 与 answer F1 change 的 query-level joint audit（描述性，不作因果）；
- 将已冻结的 exact data/model/environment SHA、绝对指标、区间、context tokens、runtime、prompt、schema、decision gate、determinism 与 independent verification 从 Stage4E 报告整理为主文表和附录。
