# Stage4H-CBE 核心组件消融与强基线实验卡

状态：`STAGE4H_CBE_EXPERIMENT_CARD_FROZEN_INPUTS_BOUND`  
日期：2026-07-24  
性质：新零重叠数据边界上的静态 HyperGranular-RAG 组件归因与强基线评估。

## 1. 研究问题与边界

研究问题：在新的 HotpotQA 与 MuSiQue closed-candidate 样本上，静态 q25 的端到端短答案质量相对 Dense 的变化是否可复制；若可复制，该变化是否依赖：

1. Dense Top-10 protected insertion；
2. facet-hyperedge 候选扩展；
3. granular-ball 结构；
4. 以及相对 lexical、hybrid 和更强 dense retriever 是否仍有优势。

本阶段不是 full-wiki/open-domain 评估，不搜索新生成器、prompt、controller、U2 或 subgroup 规则，不读取 reservation 或 Stage3B。Stage4E、Stage4F、Stage4G 的正式工件只作为历史 ID 边界与方法来源，不覆盖、不重跑。

## 2. 数据与零重叠抽样

### 2.1 数据源

| 数据集 | 冻结源 | Bytes | SHA-256 | 许可 |
|---|---|---:|---|---|
| HotpotQA train distractor v1.1 | `hotpot_train_v1.1.json` | 566,426,227 | `26650CF50234EF5FB2E664ED70BBECDFD87815E6BFFC257E068EFEA5CF7CD316` | CC BY-SA 4.0 |
| MuSiQue answerable train v1.0 | `musique_ans_v1.0_train.jsonl` | 241,046,755 | `83A75B1E11E4E9BB8F8308E72AC40CA617AE4431B3A0D955B61CAB259248490A` | CC BY 4.0 |

### 2.2 样本与选择

- HotpotQA：1,000 queries。
- MuSiQue：1,500 queries。
- 选择 salt：`stage4h_cbe_v1\0`。
- 对每个数据集先排除全部既往唯一 native ID，再按
  `SHA256(salt + dataset_key + NUL + native_id), native_id`
  升序选取。
- 既往边界必须覆盖 Stage1/2F/2G/3A、Stage4E generator-selection、Stage4E、Stage4F 与复用相同输入的 Stage4G。
- 抽样不得读取或使用 answer、support、difficulty、hop、question type、历史效果或任何模型输出。
- 1,000/1,500 是事前资源约束下采用的最低建议规模，不是功效保证。

正式输入拆为：

- Channel A Blind：问题与 closed candidate units；
- Channel B Gold：答案和 supporting evidence；
- Channel C Metadata：difficulty/type/hop/source row 等描述字段。

MuSiQue 只使用官方 supporting-paragraph Gold；不得制造 sentence-level Gold。

资源审计的盲态结果为：HotpotQA 约 41,159 candidate sentence units，MuSiQue 约 111,338，总计约 152,497。7 个 P0 arm 的 main generation 为 17,500 calls；确定性子集复跑为每数据集 100 queries、共 1,400 calls。P1 effect-cost curve 会额外增加至少 7,500 calls，因此在任何 Gold 读取前冻结为 `NOT_RUN_RESOURCE_BOUNDED`。

## 3. 固定生成器与 prompt

唯一生成器：

```text
Qwen/Qwen2.5-1.5B-Instruct
revision = 989aa7980e4cf806f80c7fef2b1adb7bc71aa306
dtype = FP16
```

固定生成合同：

- system：`Answer the question using only the provided evidence. Return only the shortest final answer. If the evidence is insufficient, return UNKNOWN.`
- evidence：`[{rank}] {title}: {sentence}`；
- user：`Evidence:\n...\n\nQuestion: <question>\nFinal answer:`；
- `input_token_cap=4096`；
- `do_sample=false`、`num_beams=1`、`max_new_tokens=32`、`batch_size=1`；
- 仅去除输出首尾空白；
- 所有方法使用相同 Top-20/effective-K、prompt 与 context budget。

## 4. P0 方法臂

### 4.1 `DENSE_TOP20`

沿用历史 `sentence-transformers/all-MiniLM-L6-v2@1110a243...`。标题和句子拼接后 mean pooling、L2 normalization、query cosine；`max_length=192`；按 `(-score, unit_id)`。

### 4.2 `STATIC_Q25_FULL`

完整复用 Stage4E/4F 静态 q25 参数、granular-ball 构造、facet-hyperedge、q25 floor、Top-10 protection、最多 4 个插入和 Top-20/effective-K。

### 4.3 `Q25_NO_PROTECTION`

先用完整方法生成与 `STATIC_Q25_FULL` 完全相同的 inserted unit set。随后只改变位置：

```text
full_inserted_units
→ dense ranking excluding those units
→ remaining full-q25 units not yet present
→ truncate at effective Top-20
```

因此候选生成、候选集合、insert budget、q25 floor 和 tie-break 不变；唯一删除的是 Dense Top-10 protected prefix。

### 4.4 `Q25_NO_FACET_HYPEREDGE`

保留完全相同的 granular-ball 构造、query/ball embeddings、seed balls、q25 floor、Top-10 protection、insert budget 和最终排序。删除 lexical facet term、new/shared-term、facet score 与 hyperedge 选择。非 seed granular balls 按：

```text
(-query_to_ball_centroid_cosine, ball_id)
```

排序，并仅保留：

- `ball_size <= 8`；
- `ball_score >= 0.12` 或相对任一 seed ball 的 centroid cosine `>= 0.05`；
- 最多 2 个 ball。

选中 ball 内 unit 仍按冻结 MiniLM cosine 和 `unit_id` 排序。该 arm 是 `CENTROID_ONLY_BALL_EXPANSION`，用于隔离 facet-hyperedge，而不是移除 granular-ball。

### 4.5 `BM25_TOP20`

- tokenizer：Unicode-independent ASCII `[A-Za-z0-9]+`，lowercase；
- document：`title + ". " + sentence`；
- query：原问题；
- `k1=1.5`、`b=0.75`；
- IDF：`log(1 + (N - df + 0.5) / (df + 0.5))`；
- 每个 query 的 closed candidate pool 独立建索引；
- tie-break：`unit_id` 升序。

### 4.6 `DENSE_BM25_HYBRID_TOP20`

对同一 query 的全部候选分别执行 query-local min-max normalization：

```text
normalized = (score - min) / (max - min)
```

若全体分数相同则该分支全部设为 0。最终分数：

```text
0.5 * normalized_minilm_cosine + 0.5 * normalized_bm25
```

按 `(-hybrid_score, unit_id)`。

### 4.7 `STRONG_DENSE_TOP20`

唯一事前选择模型：

```text
BAAI/bge-large-en-v1.5
revision = d4aa6901d3a41ba39fb536a557fa166f842b0e09
license = MIT
```

选择依据仅为官方模型卡的公开 retrieval 能力、标准 Transformers 可重建性、MIT 许可和 RTX 4060 Laptop 8GB 的工程可行性。没有读取 Stage4H Gold，也没有在 Stage4H query 上比较候选模型。

冻结编码：

- query prefix：`Represent this sentence for searching relevant passages: `；
- passage 不加 instruction；
- document：`title + ". " + sentence`；
- `[CLS]` pooling、L2 normalization、cosine；
- `max_length=512`、FP16 GPU inference、float32 cache；
- tie-break：`unit_id` 升序。

官方证据：

- <https://huggingface.co/BAAI/bge-large-en-v1.5>
- <https://github.com/FlagOpen/FlagEmbedding>

## 5. granular-ball P1 消融判定

`FLAT_UNIT_PROTECTED_INSERTION` 在当前冻结参数下不存在唯一、公平映射：

- ball seed count 无唯一的 unit seed 对应；
- 一个 facet hyperedge 可贡献多个 unit，而 flat edge 的预算换算不唯一；
- `min_size`、ball radius、compactness 与 boundary 不存在 flat 等价物。

任意实现都必须新增 seed/budget/gate 语义。因此本阶段在 Gold 前将：

```text
GRANULAR_BALL_ABLATION = NOT_FAIRLY_DEFINED
```

不执行该 arm，不以缺失 arm 推导 granular-ball 有效或无效。

## 6. 主要终点、统计与多重比较

主要终点：paired `delta_answer_f1`。支持性终点：paired `delta_answer_em`。

主要四个 contrast 均定义为左侧减右侧：

1. `STATIC_Q25_FULL - DENSE_TOP20`；
2. `STATIC_Q25_FULL - STRONG_DENSE_TOP20`；
3. `STATIC_Q25_FULL - Q25_NO_PROTECTION`；
4. `STATIC_Q25_FULL - Q25_NO_FACET_HYPEREDGE`。

每个 contrast 报告：

- HotpotQA paired bootstrap；
- MuSiQue paired bootstrap；
- 数据集等权分层 pooled bootstrap（主要判定）；
- query-weighted pooled 仅作描述；
- point、95% percentile interval、one-sided positive-tail p。

固定：

```text
bootstrap_iterations = 10000
bootstrap_seed = 20260725
NumPy generator = PCG64
percentile method = linear
```

四个主要 pooled F1 p-value 使用 Holm step-down 校正，family-wise alpha 0.05。结论：

- `SUPPORTED`：Holm-adjusted p `<=0.05`、pooled F1 interval lower `>0`，且 pooled EM interval lower `>=-0.01`；
- `NEGATIVE`：pooled F1 interval upper `<0`，或 pooled EM interval upper `<-0.01`；
- 其余为 `INCONCLUSIVE`。

CI 穿过 0 只能表述为证据不足，不得表述为无差异。BM25 与 hybrid 全量报告，但不进入四项 Holm family，也不单独触发方法晋级。

## 7. retrieval/evidence/resource 报告

每个 arm 必须报告：

- answer F1 / EM；
- retrieval CR@20 / ER@20；
- `UNKNOWN` 率；
- 相对 full 的 gain/same/harm query 数；
- effective-K、实际进入 prompt 的 evidence count 与 input tokens；
- ranking latency、generation latency、失败调用；
- GPU peak memory；
- embedding cache/index bytes；
- main 和确定性子集复跑身份。

HotpotQA 的 CR/ER 使用 official supporting sentence；MuSiQue 使用 official supporting paragraph。

## 8. 确定性与独立验证

采用事前冻结的 `FULL_MAIN_PLUS_PREHASH_STRATIFIED_SUBSET_RERUN`：

- main：2,500 queries × 7 arms；
- rerun subset：每数据集按
  `SHA256(stage4h_cbe_rerun_v1\0 + dataset + NUL + query_id), query_id`
  选择 100 queries，重跑全部 7 arms；
- subset prediction 与 main 对应行必须逐字节内容一致；
- ranking 从冻结 embedding cache 独立重建；
- schema、身份、输入 SHA、模型 snapshot、effective-K、唯一性、membership、prompt、Gold leakage、statistics、Holm、decision 和 artifact manifest 均独立验证。

正式输出使用 no-overwrite pending/promotion；不得覆盖 Stage4E/4F/4G 工件。elapsed wall time 本身不是失败条件，不设置任意固定 hard timeout。

## 9. 最终状态

最终验证通过必须产生：

```text
STAGE4H_FINAL_VERIFICATION_PASS
FULL_METHOD_VS_DENSE = SUPPORTED | NEGATIVE | INCONCLUSIVE
FULL_METHOD_VS_STRONG_DENSE = SUPPORTED | NEGATIVE | INCONCLUSIVE
PROTECTED_INSERTION_ABLATION = SUPPORTED | NEGATIVE | INCONCLUSIVE
FACET_HYPEREDGE_ABLATION = SUPPORTED | NEGATIVE | INCONCLUSIVE
GRANULAR_BALL_ABLATION = NOT_FAIRLY_DEFINED
```

负结果和不确定结果均保留。Stage4H 不授权 full-wiki、Stage4I、Stage4J、reservation、Stage3B、U2 或 controller。
