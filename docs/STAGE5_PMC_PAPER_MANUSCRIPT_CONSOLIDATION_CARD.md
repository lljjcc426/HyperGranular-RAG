# Stage5-PMC Paper Manuscript Consolidation Card

## 1. 阶段性质

```text
STAGE5_PMC_ACTIVE
PAPER_MANUSCRIPT_CONSOLIDATION_ONLY
NO_NEW_SCIENTIFIC_EXPERIMENT
```

Stage5-PMC 不是新的算法、模型或数据实验阶段。它只把 Stage0–Stage4I 已冻结且可追溯的证据整合为论文主张、核心表、论文图、正文蓝图和投稿前一致性审计。不得借论文整理重新计算冻结统计、改变判定门、覆盖正式工件或选择性隐藏负结果。

## 2. 当前研究状态

```text
STAGE4I_CLOSED_AND_FROZEN
CORE_EXPERIMENTAL_PROGRAM_COMPLETE
NEXT_PHASE = STAGE5_PAPER_MANUSCRIPT_CONSOLIDATION
FULL_WIKI = OPTIONAL_AND_DEFERRED
NEW_MODEL_SEARCH = NOT_AUTHORIZED
CONTROLLER_LINE = CLOSED
RESERVATION = LOCKED
STAGE3B = LOCKED
U2 = NOT_AUTHORIZED
```

Stage4E–Stage4I 的正式 rankings、predictions、prompt audits、Gold summaries、scientific decisions、final verifications 和 manifests 均保持只读。Stage5 不读取 reservation 或 Stage3B，不启动 full-wiki，不搜索新生成器或新 strong retriever。

## 3. 论文定位

推荐定位：

> HyperGranular-RAG is a structured evidence-completion layer for compact dense retrieval backbones. It combines adaptive granular-ball organization, query-aware facet hyperedges, and protected bounded insertion to supplement multi-hop evidence under a fixed retrieval budget.

论文不定位为新的通用强检索器或 SOTA 系统。核心故事同时保留：

1. 相对历史 MiniLM Dense 的重复 answer-F1 正结果；
2. facet-hyperedge 在冻结 MiniLM 系统内的增量价值；
3. protected placement 相对相同插入集合的 unprotected placement 的支持性结果；
4. Full 明确弱于 BGE strong dense；
5. BGE sidecar 互补性与 Gemma generator transfer 均不确定；
6. 粒球 flat-unit 独立消融未公平定义。

## 4. 主张层级

### 4.1 核心正向主张

- Static q25 相对 MiniLM Dense 的 answer-F1 增益在 HotpotQA、MuSiQue 和 Stage4H 新边界上重复出现。
- facet-hyperedge 在 Stage4H 冻结系统内具有增量价值。
- protected placement 在 Stage4I 的相同插入集合比较中优于 unprotected placement。

### 4.2 重要边界结果

- Full 明确弱于 BGE strong dense。
- HGRAG sidecar 相对 BGE 的互补增益不确定。
- Gemma official mobile-QAT 配置下的生成器迁移不确定。
- protected insertion 的独立必要性未确定。
- granular-ball flat-unit 对照未公平定义。

### 4.3 禁止主张

- 普遍优于 strong dense 或所有检索器；
- full-wiki/open-domain 有效；
- 普遍跨生成器鲁棒；
- granular-ball 结构已被独立消融确认；
- HGRAG sidecar 与 BGE 等价、必然有益或必然有害；
- Qwen2.5-1.5B 的基础架构能力显著强于 Gemma 4 E2B；
- Gemma 4 E2B 不适合 RAG、在所有设备上效率更低或架构质量较差。

生成器选择的唯一规范表述为：在 RTX 4060 Laptop 8GB、固定短答案 RAG prompt、4,096-token 输入上限和可实际部署格式下，Qwen2.5-1.5B-Instruct FP16 在冻结 200-query generator-selection development 上取得更高 answer F1/EM，同时具有更低运行时间与显存占用，因此按预登记规则成为 Stage4E 唯一生成器；Gemma 4 E2B 使用官方 mobile-QAT 格式，结果不能解释为纯模型架构比较。

## 5. Stage5 交付物

- 论文中心论点、IMRaD 结构与段落级证据映射；
- 四张核心表：主结果、外部稳健性、消融、效率与完整性；
- 五组论文图：方法结构、effect-size forest、strong-dense placement/evidence displacement、证据地图、适用边界；
- 每张图的 Python 生成脚本、CSV 源数据、SVG/PDF/TIFF/PNG 导出和 SHA manifest；
- 投稿前 evidence/claim/caption 一致性审计；
- README、AGENTS、INDEX、ROADMAP、REPRODUCIBILITY 与 paper 入口同步。

## 6. 完成与暂停边界

Stage5 内部可连续完成结构整理、表格、图、文字、引用核验、格式化、审计、Git 提交/推送和远端核验。只有以下情况暂停：

- 需要改变 Stage4E–Stage4I 冻结科学结论；
- 需要读取新的实验数据、Gold、reservation 或 Stage3B；
- 准备启动 full-wiki、U2、新 controller、新生成器或新 strong-retriever search；
- 发现论文数字无法由 tracked frozen evidence 重建；
- 需要确定目标期刊/会议、作者顺序、单位或投稿许可，而仓库中没有相应信息。

Full-wiki 当前为可选且不阻塞投稿的未来工作。只有完成论文初稿后，目标投稿标准明确要求开放域可行性证据时，才另行定义 Gold-free feasibility 阶段。
