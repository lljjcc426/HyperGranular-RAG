# Stage4E-E2E：静态 HyperGranular-RAG 端到端答案质量 Level A 协议

## Material Passport

- Origin Skill: academic-research-suite / academic-pipeline / experiment-agent
- Origin Mode: plan
- Origin Date: 2026-07-20
- Protocol Status: `LEVEL_A_ACCEPTED_FOR_INPUT_BINDING_AND_LEVEL_B_IMPLEMENTATION`
- Execution Status: `OFFICIAL_E2E_NOT_AUTHORIZED`
- Data Access During Drafting: no HotpotQA train download or read; no Stage4E Gold/model/embedding/result access

## 1. 科学问题

在一个此前未读、与既有开发查询 ID 完全不重叠的 HotpotQA distractor 边界上，使用同一固定生成器与同一输入 token 上限时，不带 U1 或任何 learned controller 的静态 all-query q25 protected insertion，是否相对 Dense Top-20 提升端到端答案质量？

本阶段检验的是静态检索方法对答案质量的影响，不是 controller 选择性，不修改或重开 Stage4B/4C/4D。Stage4D 的关闭声明见 [STAGE4D_CMA_CLOSURE](STAGE4D_CMA_CLOSURE.md)。

## 2. 研究角色与可主张边界

- 数据边界：官方 HotpotQA training set 中确定性抽取的 1,000 个 query IDs。
- 任务边界：每个问题随数据提供的 distractor paragraphs 内进行 sentence-unit 检索，再生成短答案。
- 泛化边界：这是对本项目研究流程此前未读的 **new-ID same-domain holdout**，不是新数据集、跨域外部验证、full-wiki/open-domain retrieval 或线上 RAG；公开的 2018 数据不能保证未进入生成器预训练语料。
- 模型边界：固定现成 instruction model，零训练、零微调、零提示搜索、零阈值搜索。
- 方法边界：只比较 `DENSE_TOP20` 与 `STATIC_Q25_TOP20`；不包含 U1、Stage4D candidate model、oracle、动态预算或新 controller。
- 结果边界：本协议只支持对所冻结数据、encoder、generator、prompt 和 closed candidate pool 的成对比较。

## 3. 数据来源与全新边界

### 3.1 来源

- 官方主页：<https://hotpotqa.github.io/>
- 官方仓库：<https://github.com/hotpotqa/hotpot>
- 官方文件名：`hotpot_train_v1.1.json`
- 官方数据许可：CC BY-SA 4.0；代码许可：Apache 2.0。
- 官方 schema：`_id`、`question`、`answer`、`supporting_facts`、`context`；`type`/`level` 只允许在所有主分析结束后作描述性审计。

Level A 接受前必须把下载 URL、下载日期、Bytes、SHA-256 和官方来源证据写入独立 Stage4E config。若官方文件身份无法固定，Stage4E 不执行。

### 3.2 确定性样本

冻结目标样本量：`n=1000`。对源文件中的每个原生非空字符串 `_id` 计算：

```text
selection_key = SHA256(UTF8("stage4e_e2e_v1\0" + _id))
```

按 `(selection_key, _id)` 升序取前 1,000 条。不得按答案、supporting facts、问题类型、难度、上下文长度、Dense/q25 表现或生成结果筛选。样本量是固定资源边界，不是 power guarantee；不允许根据区间宽度或结果继续抽样。

必须验证：

- 1,000 个 `_id` 唯一；
- 与仓库所有既用 HotpotQA query IDs 零重叠；
- 与 Stage4A-D 的 2Wiki namespace 零混用；
- 原始顺序、hash 排序规则和最终 ID-list SHA-256 可独立重建；
- 每条 query 至少有一个非空 context sentence；
- source row、blind row 与 Gold row 保持一一对应。
- 每个 `(supporting_title, sentence_index)` 必须唯一映射到同 query 的一个 `unit_id`；缺失或歧义均 fail closed，不丢弃 query。

### 3.3 Blind / Gold 通道

一次最小 source-custodian transaction 将冻结样本拆为：

```text
Channel A blind input:
  dataset, sample_id, query_id, question, context only

Channel B evaluation target:
  dataset, sample_id, query_id, answer, supporting_facts only

Channel C sealed descriptive metadata:
  dataset, sample_id, query_id, type, level only
```

Channel A 的 schema 明确禁止 `answer`、`supporting_facts`、`type`、`level` 及其派生字段。检索、embedding、ranking、prompt 构造和生成只能读取 blind input。Gold target 在两臂 main/rerun predictions 冻结后才由 evaluator 读取；Gold 不得参与单位构造、排序、截断、提示、解码、样本选择或错误重试。Channel C 只能在总指标、bootstrap 和主 decision 冻结后读取，用于预列出的描述性 subgroup rows。

## 4. 固定检索臂

### 4.1 公共 unit 与 encoder

- unit：每个 supplied context paragraph 的非空 sentence；不跨 query 建池。
- `unit_id = query_id + "::c" + context_index + "::s" + sentence_index`。
- encoder 输入文本：`(title + ". " + normalized_sentence).strip()`；sentence 空白只做确定性单空格规范化。
- encoder：[sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)。
- proposed revision：`1110a243fdf4706b3f48f1d95db1a4f5529b4d41`。
- `max_length=192`，batch size `64`，embedding 与 cosine-normalized matrix 为 `float32`；科学标量为 `float64`。
- Level A 接受前必须绑定模型 snapshot 的全部实际文件 Bytes/SHA-256、sentence-transformers/transformers/torch 精确版本和 embedding cache schema。

### 4.2 `DENSE_TOP20`

对 query embedding 与同 query sentence embeddings 计算 cosine similarity，按 `(-score, unit_id)` 排序，输出 `K_q=min(20, |C_q|)`。

### 4.3 `STATIC_Q25_TOP20`

直接复用已冻结的 Gold-free granular-ball / facet-hyperedge / protected-rerank 语义，不读取或调用 controller：

| 参数 | 冻结值 |
|---|---:|
| min/max ball size | `2 / 3` |
| radius threshold / max depth | `0.78 / 6` |
| boundary width | `0.20` |
| top center terms | `8` |
| seed balls / top facet edges / max expanded balls | `2 / 2 / 2` |
| min new terms / min facet score | `1 / 0.10` |
| max candidate ball size / min ball score | `8 / 0.12` |
| min seed similarity | `0.05` |
| max units per new term / max redundancy | `6.0 / 0.90` |
| `w_new / w_total / w_ball / w_diversity / w_redundancy / w_size` | `0.45 / 0.20 / 0.20 / 0.15 / 0.20 / 0.05` |
| facet-unit bonus | `0.0` |
| q25 floor | `0.1957079917192459` |
| protected Dense prefix / insert budget / effective K | `10 / 4 / min(20, |C_q|)` |

静态臂对每个 query 使用 `q25_top20_unit_ids`，不调用 ECDF、U1 score、tie-break、60% ordered-prefix budget、Stage4D feature panel 或 learned model。现有 retrieval source 的 SHA-256 为 `3B50FAFD057E2565167ED09288D61829B3FBD044991F139F734F819955038A3B`；Stage4E implementation commit 形成后必须重新绑定实际调用源码及独立 verifier SHA。

## 5. 固定生成器

### 5.1 模型与环境

- model：[Qwen/Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct)。
- proposed revision：`989aa7980e4cf806f80c7fef2b1adb7bc71aa306`。
- license：Apache 2.0。
- 推理：本地 `transformers`，不调用在线 API，不训练或量化搜索。
- dtype：GPU 可用时 `float16`；如果 exact CUDA/PyTorch 组合不能在现有硬件上稳定运行，必须在 Level A 接受前改写并重新审核，不能在 official transaction 中临时回退。
- Level A 接受前冻结：CPython、PyTorch/CUDA、transformers、tokenizers、safetensors、accelerate、NumPy 的精确版本；GPU 名称；全部模型/tokenizer 文件 Bytes/SHA-256；确定性环境变量和线程设置。

### 5.2 Prompt 与上下文序列化

System message：

```text
Answer the question using only the provided evidence. Return only the shortest final answer. If the evidence is insufficient, return UNKNOWN.
```

User message：

```text
Evidence:
[1] <title>: <sentence>
...

Question: <question>
Final answer:
```

单位按各检索臂的冻结 rank 顺序加入。输入上限为 `4096` tokenizer tokens（包含 chat template、system、question 和 answer cue）：逐个加入完整 unit，下一 unit 超限即停止，不跳过低 rank unit；若 rank 1 单独超限，仅把 rank 1 截断到剩余 token。两臂使用同一 serializer 和同一规则。

### 5.3 解码

```text
do_sample = false
num_beams = 1
max_new_tokens = 32
return only decoded completion after the prompt
```

不得设置或搜索 temperature、top-p、repetition penalty、beam width、stop phrase、few-shot example 或 answer postprocessor。只允许去除首尾空白；不得根据 Gold 修复答案。UNKNOWN 作为普通预测参与评分。

每个 `(query_id, method)` 是独立 generate call。方法顺序按 query hash 奇偶交替，以避免系统性运行顺序偏差；方法标识不进入 prompt。

## 6. 终点与统计

### 6.1 主要终点

使用官方 HotpotQA answer normalization/evaluation semantics；官方 evaluation source 必须绑定到 `hotpotqa/hotpot` commit `3635853403a8735609ee997664e1528f4480762a` 或 Level A 接受时另行记录的明确官方 commit。

```text
delta_answer_f1 = mean(F1_STATIC_Q25 - F1_DENSE)
```

统计单元是 query。使用 paired query bootstrap：seed `20260720`，10,000 次，以 query IDs 有放回抽样，同时携带两臂结果；报告 percentile 95% interval。主分析不做 subgroup 选择或 multiple-endpoint 替换。

### 6.2 Answer EM guard

```text
delta_answer_em = mean(EM_STATIC_Q25 - EM_DENSE)
```

使用同一 bootstrap draws 报告 95% interval。EM 是支持性 non-inferiority guard，不是可替换 F1 的第二晋级通道。

### 6.3 次要与描述性终点

- 两臂 answer F1、EM、UNKNOWN rate；
- retrieval supporting-fact ER@20、CR@20；
- q25 insertion count 和 gain/same/harm query counts；
- 实际进入 prompt 的 evidence units、input tokens、truncation rate；
- 生成 wall time、GPU peak memory、失败/重试计数；
- `bridge/comparison` 与 `easy/medium/hard` 仅在冻结总结果后报告点估计和明确的 `SUBGROUP_CAUTION`，不得改变总决策。

Latency 和硬件资源不进入答案质量主门。发生单条运行错误时整个 transaction fail closed；不得只重跑失败臂或丢弃 query。

### 6.4 冻结判定

在全部 integrity、Gold-isolation、main/rerun 和 independent-verification 门通过后：

```text
STATIC_HGRAG_E2E_SUPPORTED
  delta_answer_f1 >= 0.010
  and F1 interval lower > 0
  and EM interval lower >= -0.010

STATIC_HGRAG_E2E_NEGATIVE
  F1 interval upper < 0
  or EM interval upper < -0.010

STATIC_HGRAG_E2E_INCONCLUSIVE
  otherwise
```

`0.010` 表示预先声明的一点 answer-F1 最小实际增益；`-0.010` 是 EM 非劣界。两者在 Level A 接受后不得修改。任何 integrity 或 determinism 门失败均为 `NO_SCIENTIFIC_DECISION`，不得映射为正/负科研结果。

## 7. 执行与工件事务

计划分四个连续但有边界的事务：

1. `INPUT_FREEZE`：官方 source provenance、确定性 ID manifest、blind/Gold split、模型和环境文件身份；不计算 retrieval/generation/Gold metric。
2. `GOLD_FREE_RETRIEVAL_AND_GENERATION`：构造 units/embeddings，两臂 rankings，main/rerun predictions；只读取 blind input。
3. `GOLD_EVALUATION`：在 predictions 全部冻结后读取 Gold target，计算逐 query audit、summary 和 decision。
4. `INDEPENDENT_VERIFICATION`：独立重建 ID selection、schema、unit/ranking、prompt tokenization、prediction identity、official metrics、bootstrap 与 decision，并核对 local/index/commit/origin/GitHub bytes。

所有正式工件使用同目录 pending files、校验后原子 promotion 和 no-overwrite guard。raw data、blind/Gold local corpus、embedding cache、模型与 Python environment 不进 Git，只在 config/manifest 登记路径、Bytes 和 SHA-256。可提交工件至少包括 config、ID manifest、rankings、predictions、query audit、summary、decision 和 final verification；大文件是否提交由 Level B 设计按仓库策略决定，但不能缺失身份绑定。

## 8. 确定性与独立验证

- 固定原始 row order、hash selection、unit order、batch order、method order、dtype、tokenizer、chat template 和 generation kwargs。
- main 与 rerun 必须分别完成两臂全量运行；prediction artifacts 必须 byte-identical。
- 不允许在 rerun 之间修改 cache、环境、代码、GPU setting 或输出 renderer。
- verifier 不导入 evaluator 的 decision function；它独立实现 answer normalization、F1/EM、bootstrap 和判定。
- verifier 必须确认 Channel A 工件不含 Gold、type/level、method-specific prompt marker 或 Stage4D label/probability。
- verifier 必须确认 Channel C 在总指标与主 decision 冻结前未被 evaluator 或任一检索/生成入口读取。
- verifier 必须确认 Dense/q25 共用 query universe、generator、prompt、token cap 和 decoding；每条 ranking ID 均来自对应 query candidate pool。

## 9. 停止规则

立即暂停且不产生科研决策：

- 官方 source Bytes/SHA、许可或 schema 无法固定；
- HotpotQA train 已被项目历史读取、抽样或用于调参，无法证明新边界；
- selected IDs 与任何既用 query IDs 重叠；
- Gold 进入 Channel A、ranking、prompt、生成或重试逻辑；
- encoder/generator revision、环境、prompt、ranking 或判定门发生未审核变化；
- 任一臂部分输出、主/复跑不同字节、跨臂 query/order 不一致；
- verifier 无法独立复算或 local/tracked/remote 字节不一致；
- 需要访问 reservation、Stage3B、U2 或新 controller。

不得因结果不理想而切换 generator、prompt、K、q25 floor、样本或指标；任何后续方法变体必须成为新的协议。

## 10. 11 类统计谬误预防

1. **相关当因果**：只主张冻结检索臂在同一生成器下的成对性能差异。
2. **小样本强结论**：`n=1000` 是资源边界，不宣称正式功效充分。
3. **多重比较未校正**：只有一个主终点；subgroup/secondary 不触发晋级。
4. **不显著当无差异**：未满足正/负门时明确标记 inconclusive。
5. **忽略效应量**：报告 ΔF1/ΔEM 点估计、区间和绝对臂指标。
6. **基线不当**：唯一基线是相同 encoder/generator/token budget 下 Dense Top-20。
7. **数据泄漏**：blind/Gold 通道、禁止字段和独立 verifier fail closed。
8. **重复使用测试集调参**：hash-selected train holdout 只运行冻结协议一次，不在其上改 prompt/参数。
9. **过度外推**：明确限定 same-domain closed distractor candidate pool。
10. **缺失值处理不当**：任何 query 缺失、失败或跨臂不配对都使 transaction 失败，不做 complete-case 删除。
11. **选择性报告**：总结果、两臂绝对指标、全部冻结 secondary/subgroup 和负/不确定结果全部报告。

生成器可能已经见过公开 HotpotQA 训练问题，因此本阶段不主张“LLM-uncontaminated evaluation”。相同 generator 的 paired retrieval-arm comparison 可以控制模型身份，但参数化记忆可能削弱或扭曲上下文差异；该风险必须进入报告限制，不能由显著性结果消除。

## 11. Level B 完成前必须补齐的绑定

Level A 已于 2026-07-20 接受，并授权输入冻结与 Level B 实现；这不等于 official E2E 执行授权。以下项目缺一不可：

- official train file URL、Bytes、SHA-256、许可证据；
- selected 1,000 ID manifest SHA 与历史零重叠证明；
- blind/Gold split schema 和两个文件身份；
- encoder snapshot 文件身份与 embedding environment；
- generator snapshot 全文件身份、可用的精确 CUDA/PyTorch 环境和确定性证明；
- exact config、命令、工件路径、schema、atomic transaction 和 no-overwrite tests；
- synthetic fixtures 上的 retrieval、prompt、metric、bootstrap、leakage 和 byte-identical rerun tests；
- independent Level B implementation review。

这些绑定完成并通过 Level B 检查后，仍需在首次 1,000-query official retrieval/generation 和 Gold evaluation 前确认精确命令。官方 source 下载、ID-only/通道冻结和模型 snapshot 下载仅用于 provenance/identity binding，不得计算 retrieval、generation 或 Gold metric。当前状态为：

```text
STAGE4E_LEVEL_A_PROTOCOL_ACCEPTED
STAGE4E_INPUT_BINDING_AUTHORIZED
STAGE4E_LEVEL_B_IMPLEMENTATION_AUTHORIZED
STAGE4E_INPUTS_BOUND
STAGE4E_LEVEL_B_IMPLEMENTATION_READY
STAGE4E_SYNTHETIC_TESTS_PASSED
STAGE4E_INPUT_CHANNELS_VERIFIED
STAGE4E_OFFICIAL_EXECUTION_NOT_AUTHORIZED
RESERVATION_REMAINS_LOCKED
STAGE3B_REMAINS_LOCKED
U2_NOT_AUTHORIZED
```
