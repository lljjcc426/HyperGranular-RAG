# 超粒球 RAG Stage4H-CBE 核心组件消融与强基线评估报告

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run + validate
- Origin Date: 2026-07-24
- Verification Status: VERIFIED
- Version Label: stage4h_cbe_report_v1
- Source: `stage4h_cbe_v1`
- Overall Confidence: CAUTION

## 1. 结论

Stage4H-CBE 已完成 Gold-free retrieval/generation、确定性 subset rerun、pre-Gold reconstruction、Gold evaluation、10,000 次 bootstrap、Holm 校正和 final independent verification。最终状态为：

```text
STAGE4H_FINAL_VERIFICATION_PASS
```

分项冻结结论为：

```text
FULL_METHOD_VS_DENSE             SUPPORTED
FULL_METHOD_VS_STRONG_DENSE      NEGATIVE
PROTECTED_INSERTION_ABLATION     INCONCLUSIVE
FACET_HYPEREDGE_ABLATION         SUPPORTED
GRANULAR_BALL_ABLATION           NOT_FAIRLY_DEFINED
```

因此，Stage4H 支持两个收窄后的结论：

1. static-q25 full 在新的 HotpotQA/MuSiQue 等权 closed-candidate 边界上仍优于历史 MiniLM Dense，并支持 facet-hyperedge 在冻结系统中的增量价值；
2. static-q25 full 明确低于事前绑定的 BGE strong-dense，对 protected insertion 的独立增量证据不确定，粒球 flat-unit 对照无法在不引入任意启发式的情况下公平定义。

这不支持“完整 HyperGranular-RAG 优于强稠密检索器”，也不支持“protected insertion 已被证明必要”或“粒球结构已被单独确认”。Stage4E/4F 的正结果仍然有效，但应解释为相对历史 MiniLM Dense 的 closed-candidate 结果。

## 2. 新数据边界

| 数据集 | 样本 | 历史 ID | source 中可用新 ID | candidate units | Gold 粒度 |
|---|---:|---:|---:|---:|---|
| HotpotQA train distractor v1.1 | 1,000 | 2,000 | 89,447 | 41,153 | official supporting sentence |
| MuSiQue-Answerable v1.0 train | 1,500 | 4,000 | 16,938 | 109,332 | official supporting paragraph |
| 合计 | 2,500 | 6,000 | — | 150,485 | 保持数据集官方粒度 |

选择仅使用 `dataset + native query ID` 和冻结 salt。两组正式 sample IDs 与全部登记历史正式边界的交集均为 0。Blind/Gold/Metadata 三通道分别冻结；Gold 未进入样本选择、encoder/baseline 选择、candidate generation、ranking、prompt、生成、失败处理或配置取舍。

关键输入身份：

| 工件 | Bytes | SHA-256 |
|---|---:|---|
| Blind channel | 73,895,304 | `19E2659B190E91A4FC6350698C921C8F3FFA86B793BA89F3D726C004C5EA9B64` |
| Gold channel | 812,450 | `02407A306C0728024CB3D515C7427610C2AFB4898C75FEE9EDA9BA890A22B92F` |
| Metadata channel | 697,917 | `6A4461955F8D83C1F71B9C996CBC7CC824A1185D685F15E660BB66312E7F5B6C` |
| MiniLM embedding cache | 275,898,280 | `26EE26A63B320A94ECF9ED3E7E8C9719FEB48BB4A44E44C318167F94E3657337` |
| BGE embedding cache | 667,539,988 | `653CB33F0FA3D253048845A983F1C1F7517DBFCCD69AC72496155FCC58B83E7E` |

## 3. 冻结方法

### 3.1 七个 P0 方法臂

| 方法 | 冻结定义 |
|---|---|
| `DENSE_TOP20` | Stage4E/4F MiniLM Dense Top-20 |
| `STATIC_Q25_FULL` | 自适应粒球 + facet-aware hyperedge + q25 floor + Dense Top-10 protection + insert budget 4 |
| `Q25_NO_PROTECTION` | 保持 full 的已选插入集合，将其整体提前到 Dense 前部；只改变 placement |
| `Q25_NO_FACET_HYPEREDGE` | 保持粒球、保护、预算和 floor，仅使用 centroid-only ball expansion |
| `BM25_TOP20` | 同 candidate units；ASCII alnum lowercase；`k1=1.5`、`b=0.75` |
| `DENSE_BM25_HYBRID_TOP20` | query-local min-max 后 `0.5 × Dense + 0.5 × BM25` |
| `STRONG_DENSE_TOP20` | `BAAI/bge-large-en-v1.5@d4aa6901...`，CLS pooling、L2 normalization |

所有方法共享相同 query universe、candidate units、effective Top-20、Qwen prompt/decode 和 4,096-token cap。

### 3.2 Strong dense 的结果无关绑定

候选调查只使用官方模型卡、许可证、标准 Transformers 加载合同和本机 synthetic 资格测试，未读取 Stage4H Gold。最终选择 `BAAI/bge-large-en-v1.5`，原因是：

- 官方模型卡提供 MIT 许可证、标准 Transformers 用法、检索 query instruction 与 CLS pooling；
- 本地 RTX 4060 synthetic 两次输出同字节；
- 相比需要 `trust_remote_code` 的候选，它更适合独立重建与离线固定。

来源：[BGE official model card](https://huggingface.co/BAAI/bge-large-en-v1.5)、[FlagEmbedding official repository](https://github.com/FlagOpen/FlagEmbedding)。

### 3.3 未运行的设计项

- `FLAT_UNIT_PROTECTED_INSERTION = NOT_FAIRLY_DEFINED`：现有冻结方法没有从 granular-ball seed、radius、compactness、edge budget 和 boundary 语义到 flat units 的唯一结果无关映射；制造任意弱对照会形成 straw man。
- P1 effect-cost curve 为 `NOT_RUN_RESOURCE_BOUNDED`：三个额外配置至少增加 7,500 次生成调用。它未进入确认性门，也没有被结果选择性删除。

## 4. 统计设计

- 主要终点：paired `STATIC_Q25_FULL - comparator` answer F1；
- 支持性 guard：paired answer EM；
- HotpotQA 与 MuSiQue 分别做 query-paired bootstrap；
- 联合结果为数据集等权分层 bootstrap；
- `bootstrap_iterations=10,000`，`seed=20260725`；
- 四个主要比较使用 one-sided positive Holm step-down；
- `SUPPORTED` 要求 Holm `p≤0.05`、等权 F1 CI lower `>0`、等权 EM CI lower `≥-0.01`；
- `NEGATIVE` 要求 F1 CI upper `<0` 或 EM CI upper `<-0.01`；
- BM25/hybrid 完整报告，但不触发 advancement。

## 5. 各数据集绝对结果

### 5.1 HotpotQA，n=1,000

| 方法 | Answer F1 | EM | CR@20 | ER@20 | UNKNOWN | Mean tokens |
|---|---:|---:|---:|---:|---:|---:|
| Dense | 0.45585 | 0.396 | 0.739 | 0.88259 | 0.330 | 908.67 |
| Static q25 full | 0.47654 | 0.412 | 0.799 | 0.91065 | 0.300 | 909.91 |
| No protection | 0.46988 | 0.412 | 0.799 | 0.91065 | 0.300 | 909.91 |
| No facet-hyperedge | 0.45176 | 0.393 | 0.755 | 0.88905 | 0.329 | 909.23 |
| BM25 | 0.49390 | 0.433 | 0.847 | 0.93698 | 0.292 | 956.58 |
| Dense+BM25 hybrid | 0.48596 | 0.420 | 0.843 | 0.93441 | 0.305 | 937.33 |
| Strong dense | 0.52247 | 0.460 | 0.922 | 0.96931 | 0.285 | 933.54 |

### 5.2 MuSiQue，n=1,500

| 方法 | Answer F1 | EM | CR@20 | ER@20 | UNKNOWN | Mean tokens |
|---|---:|---:|---:|---:|---:|---:|
| Dense | 0.15307 | 0.11333 | 0.59333 | 0.80800 | 0.65333 | 862.50 |
| Static q25 full | 0.15951 | 0.11600 | 0.64533 | 0.84250 | 0.62800 | 867.09 |
| No protection | 0.15910 | 0.11467 | 0.64533 | 0.84250 | 0.61133 | 867.09 |
| No facet-hyperedge | 0.15759 | 0.11600 | 0.60000 | 0.81200 | 0.64600 | 864.97 |
| BM25 | 0.15725 | 0.11400 | 0.62000 | 0.82478 | 0.61733 | 923.86 |
| Dense+BM25 hybrid | 0.15650 | 0.11600 | 0.65867 | 0.84494 | 0.62333 | 903.63 |
| Strong dense | 0.19355 | 0.14933 | 0.78600 | 0.90872 | 0.60267 | 908.77 |

## 6. 等权主要比较

| 对照（Full − comparator） | ΔF1 [95% CI] | Holm p | ΔEM [95% CI] | 结论 |
|---|---:|---:|---:|---|
| Dense | `+0.01357 [0.00491,0.02233]` | 0.00520 | `+0.00933 [0.00083,0.01783]` | `SUPPORTED` |
| Strong dense | `-0.03998 [-0.05393,-0.02621]` | 1.00000 | `-0.04067 [-0.05483,-0.02683]` | `NEGATIVE` |
| No protection | `+0.00354 [-0.00675,0.01389]` | 0.49695 | `+0.00067 [-0.00983,0.01133]` | `INCONCLUSIVE` |
| No facet-hyperedge | `+0.01336 [0.00341,0.02343]` | 0.01200 | `+0.00950 [-0.00017,0.01917]` | `SUPPORTED` |

支持性外部基线：

| 对照（Full − comparator） | 等权 ΔF1 [95% CI] | 等权 ΔEM [95% CI] | 报告状态 |
|---|---:|---:|---|
| BM25 | `-0.00755 [-0.02259,0.00773]` | `-0.00950 [-0.02483,0.00617]` | supporting only |
| Dense+BM25 hybrid | `-0.00320 [-0.01591,0.00942]` | `-0.00400 [-0.01667,0.00867]` | supporting only |

结果说明：

- Full 对历史 Dense 的 F1 增益在两个数据集上的点估计均为正，联合门通过；
- Full 对 strong dense 在两个数据集均为负，且等权 F1/EM 区间完全低于 0；
- Full 与 no-protection 具有相同 retrieval coverage，差异主要来自上下文次序及生成器利用方式，但联合区间跨 0；
- Full 对 no-facet 的联合增益通过 Holm 门；该结果支持 facet-hyperedge 在这个冻结系统中的增量价值，不自动证明普遍因果机制；
- HotpotQA 上 BM25/hybrid 的绝对 F1 高于 Full，MuSiQue 上差异较小；支持性比较不进入主要 advancement。

## 7. 插入与资源

- Full：1,771/2,500 queries 发生插入，共 5,407 次插入；
- No-facet：2,386/2,500 queries 发生插入，共 7,843 次插入；
- Gold-free main：17,500 generation calls，失败 0，wall time 6,265.00 s；
- deterministic subset rerun：200 queries × 7 arms = 1,400 calls，失败 0，wall time 541.39 s；
- main GPU peak memory：4,174,117,888 bytes；
- MiniLM/BGE caches：275,898,280 / 667,539,988 bytes；
- retrieval wall-time 记录：Dense+Full 9.96 s、No-facet 7.27 s、BM25 2.32 s、Hybrid 0.37 s、Strong dense 0.30 s；
- 每臂生成累计时间为 805.81–860.70 s。

这些 retrieval 计时是同一冻结实现中的阶段内 telemetry，不是跨硬件基准；不能推出任一方法在所有设备上更快。

## 8. 确定性、独立验证与工程修复

确定性合同为：

```text
full main: 2,500 queries × 7 arms = 17,500 calls
pre-hash stratified rerun: 100 queries/dataset × 7 arms = 1,400 calls
```

独立 pre-Gold verifier 重建了 source-only ID selection、历史零重叠、150,485 个 candidate units、两套 embedding cache identity、2,500 个七臂 rankings、17,500 个 prompts，以及 main/subset prediction/prompt equality。final verifier 又独立重算 query metrics、dataset/equal-weight bootstrap、Holm 和 scientific decisions。

工程修复均发生在冻结科学语义内：

1. 首次 main 在 cache 已安全生成、任何 prediction 尚未提升前，暴露 no-facet insertion ID 序列化类型错误；提交 `8f89148` 修正，正式结果随后从冻结 cache 产生；
2. pre-Gold verifier 最初未重现 runner 的 cache-load 再归一化语义，极少数并列项排序不同；提交 `5e811b1` 只修正 verifier；
3. verifier 的 prompt 比较误把运行时 `input_ids` 与持久化 audit schema 直接比较；提交 `b406424` 改为相同 audit projection；
4. pre-Gold 外层工具等待达到 180 秒后返回，但 verifier 进程继续存活、CPU 持续增长并自然产出 PASS；未启动第二个事务，未覆盖任何工件。

修正后 Stage4H 定向测试为 15/15 PASS，pre-Gold 与 final verification 均通过。以上事件不是模型、数据、统计或科学失败。

## 9. 正式工件身份

| 工件 | Bytes | SHA-256 |
|---|---:|---|
| input manifest | 668,237 | `6095D8FAB5526F1F10956C1808802C4122B20840666422253B9591802DD92615` |
| rankings | 22,809,912 | `EAECD420CEDDFD0E670892E9B78B0D6D02BB3E9BE2A84BC36631C1D985C49822` |
| retrieval trace | 1,280,228 | `308D3FCF9B0D517548542C33BB241B2824446B68453697F83BC5CAA13796087F` |
| predictions main | 3,449,765 | `52B9276E93AF19820B8F2E358F54BE9CDF88D4A8C6A34020AF3EDC153470E310` |
| prompt audit main | 26,702,494 | `B7B2D3E3846CD7406C4E646A0DC007F54A5CC3BBA863CAD9E0551F7AB9A5B507` |
| telemetry main | 1,366 | `5B69B732D19A0C04337AFB05FA44362BF43977C2AB1BFD6ACF4D4DAC1520E164` |
| predictions rerun subset | 279,671 | `84025B63BB1C49268287DE2E0A1B85B9EF4A91821D98441658C0E7807C943C78` |
| prompt audit rerun subset | 2,161,571 | `BB6CA94A55F311B07F96F5B5A280D944F5117A8A3220629C4C2F7835E3119042` |
| telemetry rerun subset | 1,378 | `0EEAC0F16DF8D5F996B9F477CFFAF065D4A3DDC1F2F63C31FC9B014464707048` |
| verified pre-Gold | 4,211 | `ACF11E359BFFF40DB53C07DB27A39E6C5ABE61AC1C4161C8A15542397783639B` |
| query audit | 3,111,653 | `6232260E8D91D070E8A28B96A4F179538D2EB300F16FE28DB3B24168ADBD4CA9` |
| dataset summaries | 6,998 | `C9B2E163A46FE41B458321C8292CCF21A99C5B6AC666E3E28BA6798E013CB85B` |
| equal-weight summary | 10,465 | `0C8677960F2CB07526B36264CE58883ED28D12C0016F6EAD8A036D3DD0BE7FA4` |
| scientific decision | 691 | `3C4B2E4A2AAC4A5E031D8513DD88391BC378351113DF7E99E6362B85DDE8BBD5` |
| descriptive metadata | 3,834 | `07DA983E648E2477B09038CDF8511560B2FD1DF33E61C715CF4A8C67C5CB4B30` |
| final verification | 2,754 | `692D7150043071580B58F1CC1F758884A6178412C98ED193C4D4D27BDB40726F` |
| artifact manifest | 2,370 | `6E467B17BE53F1EA75D897E1185558F1FE50C04A4302568515C831DA7641C72D` |

## 10. 11 类统计谬误扫描

Coverage: 11/11 checked。

| 谬误 | 结论 | Stage4H 检查 |
|---|---|---|
| Simpson's paradox | NOTE | Full-vs-Dense、Full-vs-Strong、Full-vs-NoFacet 在两个数据集的点估计方向一致；主要联合结论无方向反转 |
| Ecological fallacy | NOTE | 数据集等权结果不用于推断每条 query 都受益；同时报告 gain/same/harm |
| Berkson's paradox | CAUTION | 两个样本都是 closed-candidate train 子集；结论不能外推到 full-wiki/open-domain |
| Collider bias | NOTE | primary analysis 未按 post-outcome metadata 条件化；Channel C 在 decision 后读取 |
| Base-rate neglect | NOTE | 不是诊断分类任务；仍报告 UNKNOWN、gain/same/harm 与 dataset-specific absolute metrics |
| Regression to the mean | NOTE | 新边界按 ID-only hash 选择，不按极端历史效果选择 |
| Survivorship bias | NOTE | main/subset failed calls 均为 0；2,500 queries 全覆盖 |
| Look-elsewhere effect | NOTE | 四个主要比较事前冻结并使用 Holm；BM25/hybrid 全量报告但不触发 advancement |
| Garden of forking paths | NOTE | arm、strong dense、统计门、flat/cost-curve边界均在 Gold 前冻结；不按结果换模型或定义 |
| Correlation ≠ causation | CAUTION | 消融支持“冻结系统中的增量价值”，不证明一般因果机制 |
| Reverse causality | NOTE | 同 query 的受控管线对照不涉及观察性时间反向因果；仍不作超出管线的机制推断 |

整体置信度为 `CAUTION`：结果已独立验证且多重比较受控，但相对历史 Dense 的增益较小、相对 strong dense 为负，数据仍是两个 closed-candidate 边界。

## 11. 论文主张与下一阶段

Stage4H 后可写的最强表述是：

> 在两个新的、与项目历史正式 query ID 零重叠的 closed-candidate 多跳 QA 边界上，static-q25 full 相对历史 MiniLM Dense 的数据集等权 answer-F1 增益得到支持，且 full 相对 no-facet ablation 的增益支持 facet-hyperedge 的系统内增量价值；但 full 明确低于事前绑定的 BGE strong-dense，protected insertion 的独立贡献不确定，粒球 flat 对照未能公平定义。

当前证据足以进入 `Stage4I-FWF` 的独立轻量可行性设计，但不授权直接进行 full-wiki Gold 评价。下一顺序保持：

```text
Stage4I-FWF: Full-Wiki Feasibility
→ 若索引、候选、ANN、成本与可验证合同成立
→ Stage4J-FWV: Full-Wiki Verified Evaluation
```

Reservation、Stage3B、U2、adaptive controller、新生成器实验与 full-wiki 正式 Gold 仍保持锁定。
