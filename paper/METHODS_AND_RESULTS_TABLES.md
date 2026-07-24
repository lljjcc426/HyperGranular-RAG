# HyperGranular-RAG 方法定义与冻结结果表

状态：`STAGE4I_FINAL_VERIFICATION_PASS`
用途：论文 Methods、Results 与 Reproducibility 的统一数字入口。
证据边界：本文件只汇总已经提交并通过独立验证的 Stage4E–4I 工件；不新增统计检验，不改变任何冻结结论。

## 1. 静态 HyperGranular-RAG 方法

### 1.1 闭集 sentence-unit 检索

对 query \(q\) 的候选集合 \(U_q=\{u_i\}\)，冻结 MiniLM encoder 分别编码 query 和
`title + ". " + sentence`。向量经 L2 normalization 后，以 cosine：

\[
s(q,u_i)=\hat e_q^\top\hat e_i
\]

排序；同分时按 `unit_id` 升序。Dense 基线取前
\(K_q=\min(20, |U_q|)\) 项。Stage4E–4I 的静态方法不调用 U1/controller。

### 1.2 自适应粒球

每个 query 的候选向量从单一根集合开始递归拆分。对当前集合 \(B\)：

1. 计算并归一化 centroid；
2. 计算各 unit 到 centroid 的 cosine distance \(1-\cos(e_i,c_B)\)；
3. radius 取最大距离，compactness 为 \(1-\text{mean distance}\)；
4. 若深度小于 6、集合大小至少为 \(2\times2\)，且大小超过 3 或 radius
   超过 0.78，则选择两个确定性远端 seed，把 unit 分配给 cosine 更接近的 seed；
5. 只有两个子集大小都至少为 2 时才接受拆分，否则保留当前球。

该构造只使用 candidate embeddings，不读取答案或 supporting evidence。

### 1.3 Query-aware facet hyperedge

对每个球汇总 title/sentence 中长度大于 2 的 ASCII alphanumeric content terms，并去除冻结
stopword 集。球的 facet terms 是其 content terms 与 query terms 的交集。按
query-to-centroid cosine 选择前两个 seed balls，已覆盖 facet terms 为两个 seed 的并集。

非 seed 球必须先通过以下固定门：

- 至少引入 1 个新 query term；
- `ball_size <= 8`；
- `ball_score >= 0.12`，或与任一 seed centroid cosine `>= 0.05`；
- `units_per_new_term <= 6.0`；
- shared-term redundancy `<= 0.90`。

通过门后：

\[
\begin{aligned}
\text{facet\_score}={}&0.45\,r_{\text{new}}
+0.20\,r_{\text{total}}
+0.20\,s_{\text{ball}}\\
&+0.15\,d_{\text{seed}}
-0.20\,r_{\text{redundancy}}
-0.05\,r_{\text{size}} .
\end{aligned}
\]

保留 `facet_score >= 0.10` 的 edge，按 `(-facet_score, edge_id)` 排序，最多选择两个
edge/ball。选中球内的 unit 仍按原 MiniLM cosine 和 `unit_id` 排序；facet score 不额外改变
unit score（`w_facet_unit_bonus=0`）。

### 1.4 Dense-prefix protected insertion

```text
input:
  Dense ranking D
  selected facet-ball units E sorted by frozen MiniLM score

protected = first min(10, |D|) unique units
candidates = units in E with cosine >= 0.1957079917192459
inserted = first at most 4 candidates not already protected
ranking = protected + inserted
append remaining unique Dense units in original order
append remaining unique expanded units only if K is still unfilled
return first effective-K units
```

该操作保护 Dense Top-10，并把有限扩展放在其后；它不是对原 Dense 分数的重训练，也不是
query-adaptive controller。

## 2. Stage4E–4G 端到端结果

所有差值均定义为 `STATIC_Q25 − DENSE`。区间是冻结的 10,000 次 paired bootstrap 95%
percentile interval。

| 阶段 / generator | 数据边界 | n | Dense F1 | q25 F1 | ΔF1 [95% CI] | ΔEM [95% CI] | 冻结判定 |
|---|---|---:|---:|---:|---:|---:|---|
| Stage4E / Qwen2.5-1.5B-Instruct FP16 | HotpotQA closed distractor | 1,000 | 0.42150 | 0.43628 | +0.01478 [0.00020, 0.02988] | +0.01000 [-0.00500, 0.02500] | `STATIC_HGRAG_E2E_SUPPORTED` |
| Stage4F / Qwen2.5-1.5B-Instruct FP16 | MuSiQue closed candidate | 3,000 | 0.13595 | 0.14735 | +0.01140 [0.00450, 0.01835] | +0.01000 [0.00333, 0.01667] | `STATIC_HGRAG_XDR_SUPPORTED` |
| Stage4G / Gemma 4 E2B official mobile-QAT | HotpotQA frozen Stage4E input | 1,000 | 0.34978 | 0.36243 | +0.01265 [-0.00220, 0.02744] | — | dataset-specific descriptive |
| Stage4G / Gemma 4 E2B official mobile-QAT | MuSiQue frozen Stage4F input | 3,000 | 0.04476 | 0.04244 | -0.00232 [-0.00685, 0.00208] | — | dataset-specific descriptive |
| Stage4G / Gemma 4 E2B official mobile-QAT | dataset-equal-weight | 4,000 | — | — | +0.00516 [-0.00262, 0.01295] | +0.00233 [-0.00567, 0.01033] | `GENERATOR_TRANSFER_INCONCLUSIVE` |

Stage4G 只能解释为一个额外预指定、官方 mobile-QAT 可部署配置下的迁移测试。其架构、
量化/数值格式和运行实现效应不可分离，不能用于 Qwen/Gemma 基础架构能力排名，也不能据此
声称 Gemma 不适合 RAG。

## 3. Stage4H 核心消融

### 3.1 七臂绝对指标

| 数据集 | 方法 | Answer F1 | EM | CR@20 | ER@20 |
|---|---|---:|---:|---:|---:|
| HotpotQA | Historical MiniLM Dense | 0.45585 | 0.39600 | 0.73900 | 0.88259 |
| HotpotQA | Static q25 full | 0.47654 | 0.41200 | 0.79900 | 0.91065 |
| HotpotQA | q25 no protection | 0.46988 | 0.41200 | 0.79900 | 0.91065 |
| HotpotQA | q25 no facet-hyperedge | 0.45176 | 0.39300 | 0.75500 | 0.88905 |
| HotpotQA | BM25 | 0.49390 | 0.43300 | 0.84700 | 0.93698 |
| HotpotQA | Dense–BM25 hybrid | 0.48596 | 0.42000 | 0.84300 | 0.93441 |
| HotpotQA | BGE strong dense | 0.52247 | 0.46000 | 0.92200 | 0.96931 |
| MuSiQue | Historical MiniLM Dense | 0.15307 | 0.11333 | 0.59333 | 0.80800 |
| MuSiQue | Static q25 full | 0.15951 | 0.11600 | 0.64533 | 0.84250 |
| MuSiQue | q25 no protection | 0.15910 | 0.11467 | 0.64533 | 0.84250 |
| MuSiQue | q25 no facet-hyperedge | 0.15759 | 0.11600 | 0.60000 | 0.81200 |
| MuSiQue | BM25 | 0.15725 | 0.11400 | 0.62000 | 0.82478 |
| MuSiQue | Dense–BM25 hybrid | 0.15650 | 0.11600 | 0.65867 | 0.84494 |
| MuSiQue | BGE strong dense | 0.19355 | 0.14933 | 0.78600 | 0.90872 |

HotpotQA 的 CR/ER 使用 official supporting sentences；MuSiQue 使用 official supporting
paragraphs。二者不能混写成同一种 sentence-level Gold。

### 3.2 数据集等权主要比较

| 比较（左−右） | ΔF1 [95% CI] | Holm p | ΔEM [95% CI] | 冻结判定 |
|---|---:|---:|---:|---|
| Full − historical Dense | +0.01357 [0.00491, 0.02233] | 0.00520 | +0.00933 [0.00083, 0.01783] | `SUPPORTED` |
| Full − BGE strong dense | -0.03998 [-0.05393, -0.02621] | 1.00000 | -0.04067 [-0.05483, -0.02683] | `NEGATIVE` |
| Full − no protection | +0.00354 [-0.00675, 0.01389] | 0.49695 | +0.00067 [-0.00983, 0.01133] | `INCONCLUSIVE` |
| Full − no facet-hyperedge | +0.01336 [0.00341, 0.02343] | 0.01200 | +0.00950 [-0.00017, 0.01917] | `SUPPORTED` |

BM25 和 hybrid 是全量支持性基线，不进入四比较 Holm family：Full−BM25 等权 F1
`-0.00755 [-0.02259,0.00773]`，Full−Hybrid 为
`-0.00320 [-0.01591,0.00942]`。

`FLAT_UNIT_PROTECTED_INSERTION` 在冻结参数下没有唯一、公平的 seed/budget/gate 映射，因此
`GRANULAR_BALL_ABLATION=NOT_FAIRLY_DEFINED`。这不是粒球有效或无效的统计证据。P1
effect-cost curve 在 Gold 前因资源边界冻结为 `NOT_RUN_RESOURCE_BOUNDED`。

## 4. Strong-dense 边界

Stage4H 的 strong retriever 是在 Gold 前唯一绑定的
`BAAI/bge-large-en-v1.5@d4aa6901d3a41ba39fb536a557fa166f842b0e09`，MIT license；
使用官方 query instruction、`[CLS]` pooling、L2 normalization、cosine 和 512-token cap。

Stage4H 结果同时支持两项不同强度的陈述：

1. static q25 相对项目历史 MiniLM Dense 在新零重叠 closed-candidate 边界上保持小幅 F1
   增益；
2. static q25 明确低于 BGE strong dense。

因此论文不能声称 HyperGranular-RAG 优于强 dense retriever；现有证据更接近“在较弱历史
Dense 主干上进行结构化补全有价值，但强 encoder 可覆盖更多相关证据”。

## 5. Stage4I BGE sidecar 互补性

Stage4I 在另一组历史正式 ID overlap 为 0 的 HotpotQA 1,000 + MuSiQue 1,500 上，以
BGE Top-20 为主排名，以冻结 MiniLM-HGRAG 为独立 sidecar。q25 只决定 sidecar candidate
eligibility，不进行 BGE/MiniLM score fusion。Protected 与 Unprotected 使用完全相同的插入
集合，唯一差异是插入位置。

### 5.1 四臂绝对指标

| 数据集 | 方法 | Answer F1 | EM | CR@20 | ER@20 |
|---|---|---:|---:|---:|---:|
| HotpotQA | BGE Top-20 | 0.51952 | 0.44000 | 0.92600 | 0.96872 |
| HotpotQA | BGE + protected HGRAG sidecar | 0.51655 | 0.43800 | 0.91700 | 0.96478 |
| HotpotQA | BGE + unprotected HGRAG sidecar | 0.50723 | 0.42800 | 0.91700 | 0.96478 |
| HotpotQA | BGE + no-facet protected sidecar | 0.52370 | 0.44400 | 0.90500 | 0.96043 |
| MuSiQue | BGE Top-20 | 0.16650 | 0.12000 | 0.77333 | 0.90317 |
| MuSiQue | BGE + protected HGRAG sidecar | 0.16435 | 0.11733 | 0.77000 | 0.90439 |
| MuSiQue | BGE + unprotected HGRAG sidecar | 0.15122 | 0.10133 | 0.77000 | 0.90439 |
| MuSiQue | BGE + no-facet protected sidecar | 0.17206 | 0.12333 | 0.75933 | 0.89772 |

### 5.2 数据集等权冻结比较

| 比较（左−右） | ΔF1 [95% CI] | ΔEM [95% CI] | 冻结判定 |
|---|---:|---:|---|
| Protected sidecar − BGE | -0.00256 [-0.00998, 0.00458] | -0.00233 [-0.00983, 0.00467] | `STRONG_DENSE_COMPLEMENTARITY_INCONCLUSIVE` |
| Protected − Unprotected | +0.01122 [0.00129, 0.02104] | +0.01300 [0.00333, 0.02283] | `PROTECTED_PLACEMENT_SUPPORTED` |
| Unprotected sidecar − BGE | -0.01379 [-0.02440, -0.00339] | -0.01533 [-0.02617, -0.00500] | supporting placement evidence |
| Protected − NoFacet | -0.00743 [-0.01616, 0.00132] | -0.00600 [-0.01483, 0.00283] | `BGE_FACET_INCREMENT_INCONCLUSIVE` |

Stage4I 的核心 comparison 只有 Protected sidecar−BGE。Placement 与 facet 是支持性诊断，
不能单独触发 advancement。核心区间跨 0，因此既不能声称 sidecar 改善或损害 BGE，也不能
声称等价。

## 6. 统一资源与确定性

| 阶段 | Generator/runtime | Main calls | Determinism transaction | Main wall time (s) | Main GPU peak (bytes) | 零失败 |
|---|---|---:|---|---:|---:|---|
| Stage4E | Qwen FP16 | 2,000 | full main + full rerun（另 2,000） | 854.833 | 3,509,613,568 | 是 |
| Stage4F | Qwen FP16 | 6,000 | full main + full rerun（另 6,000） | 1,947.368 | 4,268,833,280 | 是 |
| Stage4G | Gemma official mobile-QAT | 8,000 | full main + pre-hash subset（400） | 56,501.842 | 7,885,933,056 | 是 |
| Stage4H | Qwen FP16 | 17,500 | full main + pre-hash subset（1,400） | 6,265.001 | 4,174,117,888 | 是 |
| Stage4I | Qwen FP16 | 10,000 | full main + pre-hash subset（800） | 4,999.069 | 4,356,265,984 | 是 |

Stage4E embedding cache 为 75,756,384 bytes；Stage4F 为 399,838,172 bytes；Stage4H 的
MiniLM/BGE caches 分别为 275,898,280 / 667,539,988 bytes。Stage4G 表中的时间和显存来自
mobile-QAT runtime，不能外推为 Gemma 架构在所有设备上的效率。

Stage4E/4F 的完整复跑和 Stage4G/4H 的预哈希分层 subset 均通过冻结的精确重现合同；
Stage4H subset 的 200 queries / 1,400 predictions 与 main 投影逐字节一致。Stage4I 的
MiniLM/BGE caches 分别为 276,194,136 / 668,255,684 bytes；其 200-query / 800-prediction
subset 与 main 投影逐字节一致。

## 7. 完整性、主张与限制

- Stage4H HotpotQA 1,000 + MuSiQue 1,500 样本与全部历史正式 ID overlap 为 0；选择只使用
  native IDs 和预注册 hash salt。
- Blind、Gold、Metadata 三通道分离；ranking、prompt audit 与确定性验证在 Gold 读取前完成。
- Stage4H final verifier 独立重建 query metrics、dataset/equal-weight summaries、10,000
  bootstrap、Holm、decision 和 artifact manifest，状态为
  `STAGE4H_FINAL_VERIFICATION_PASS`。
- Stage4E/4F/4H 是 closed-candidate 结果，不是 full-wiki/open-domain 结果。
- Stage4H 的保护插入比较区间跨 0，只能写为证据不足；facet-hyperedge 的结论限于当前冻结
  系统，不能推广为普遍因果机制。
- Stage4I 在独立零重叠样本上以 BGE 为主排名；core sidecar comparison 为 inconclusive，
  placement supporting comparison 为 supported，facet supporting comparison 为 inconclusive。
- Stage4I verifier 独立重建 query metrics、dataset/equal-weight summaries、10,000
  bootstrap、evidence transitions 和 decision，状态为 `STAGE4I_FINAL_VERIFICATION_PASS`。
- Stage4I cache roundtrip 修正只消除了已归一化 float32 cache 的二次归一化；正式 cache、
  ranking、candidate trace 和科学定义均未改变。
- post-decision metadata 只允许描述，不能转化为新的确认性 subgroup 结论。
- controller 负结果属于独立研究分支，不能用于修改或否定静态方法的已冻结结果。

## 8. 证据定位

- Stage4E/4F/4G/4H/4I 结果与限制：对应 `reports/` 阶段报告；
- Stage4H 逐数据集绝对指标：`results/stage4h_cbe_hotpot1000_musique1500_v1_dataset_summaries.json`；
- Stage4H 主要比较：`results/stage4h_cbe_hotpot1000_musique1500_v1_equal_weight_summary.json`；
- Stage4H 决策：`results/stage4h_cbe_hotpot1000_musique1500_v1_scientific_decision.json`；
- Stage4H 独立验证：`results/stage4h_cbe_hotpot1000_musique1500_v1_final_verification.json`；
- Stage4I 主要比较：`results/stage4i_sdc_hotpot1000_musique1500_v1_equal_weight_summary.json`；
- Stage4I placement/facet：`results/stage4i_sdc_hotpot1000_musique1500_v1_placement_summary.json` 与 `results/stage4i_sdc_hotpot1000_musique1500_v1_facet_summary.json`；
- Stage4I 决策/独立验证：`results/stage4i_sdc_hotpot1000_musique1500_v1_scientific_decision.json` 与 `results/stage4i_sdc_hotpot1000_musique1500_v1_final_verification.json`；
- 精确算法实现：`scripts/stage4f_xdr_retrieval.py`、`scripts/stage4h_cbe_retrieval.py` 与 `scripts/stage4i_sdc_retrieval.py`。
