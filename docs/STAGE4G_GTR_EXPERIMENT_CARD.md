# Stage4G-GTR Generator-Transfer Replication 实验卡

状态：`STAGE4G_GTR_STAGE_LEVEL_AUTHORIZED`  
日期：2026-07-23  
性质：固定 Stage4E/Stage4F 检索结果上的单一新增生成器受控复制；不是新数据集独立验证、模型排名或开放域实验。

## 1. 唯一科学问题

在完全复用 Stage4E HotpotQA 与 Stage4F MuSiQue 的 blind inputs、`DENSE_TOP20`、`STATIC_Q25_TOP20` 和数据集各自官方答案评分规则时，使用一个结果无关、事前绑定的第二生成器，static-q25 相对 Dense 的 answer-F1 增益是否在两个数据集上保持同方向，并通过数据集等权联合判定门？

允许的论文主张上限为：

> The retrieval gain was replicated under one additional pre-specified generator configuration.

不得外推为普遍 generator robustness、纯架构优劣或 full-wiki/open-domain 证据。

## 2. 唯一第二生成器

- snapshot：`google/gemma-4-E2B-it-qat-mobile-transformers`
- revision：`dd693ff40353f057ca5f07e945ad867f4afbf2ec`
- runtime：Google official mobile-QAT Transformers snapshot
- thinking：disabled
- target：RTX 4060 Laptop 8GB，单 GPU、无 CPU offload

选择依据与正式结果无关：该配置属于不同于 Qwen 的模型家族，revision 与文件身份可固定，且已在同一硬件上完成 200-query greedy、thinking-off、main/rerun 确定性资格验证。Gemma 的架构、mobile-QAT 数值格式和量化实现效应不可分离。本阶段不重新开展 Gold 模型选择，也不搜索量化、prompt 或 decoding 组合。

## 3. 冻结复用边界

直接读取且只读：

- Stage4E frozen HotpotQA blind inputs（1,000 queries）；
- Stage4E frozen Dense/static-q25 rankings；
- Stage4F frozen MuSiQue blind inputs（3,000 queries）；
- Stage4F frozen Dense/static-q25 rankings；
- Gold 阶段才读取两数据集冻结 Gold targets 与冻结 Qwen query audits。

禁止重跑 embedding、Dense/q25 retrieval、粒球、超边、protected reranking 或 q25 参数计算；禁止覆盖或重新生成 Stage4E/Stage4F 正式工件。

## 4. 生成合同与 Gold 隔离

```text
System:
Answer the question using only the provided evidence. Return only the shortest final answer. If the evidence is insufficient, return UNKNOWN.

input_token_cap = 4096
do_sample = false
num_beams = 1
max_new_tokens = 32
batch_size = 1
postprocess = strip outer whitespace only
```

允许使用 Gemma 官方 tokenizer、chat template 和特殊 token。每条 prompt audit 固定记录 query/dataset/method、冻结 ranking source SHA、ranking-list SHA、连续 ranking prefix 中实际纳入的 unit IDs、input tokens、语义内容 SHA、completion token IDs、prediction 与 truncation state。语义内容不包含 Gold 或方法标签；`method` 仅作为工件行元数据存在。

执行顺序固定为：完整 Gold-free main → 事前 hash-selected rerun subset → 独立 pre-Gold reconstruction/verification → Gold evaluation。任何 Gold 不得进入模型绑定、prompt、截断、生成、失败重试或 rerun subset 选择。

## 5. 确定性合同 B

采用：`B_FULL_MAIN_PLUS_PREHASH_STRATIFIED_SUBSET_RERUN`。

- full main：4,000 queries × 2 retrieval arms = 8,000 calls；
- rerun：每数据集事前选择 100 queries，并覆盖两臂，共 400 calls；
- selection key：`SHA256("stage4g_gtr_rerun_v1\0" + dataset + "\0" + query_id)`，每数据集按 digest、query_id 升序取前 100；
- subset 不读取 Gold 或输出；不得事后替换异常 query；
- subset predictions 与完整 prompt audits 必须逐行等于 full main 对应行。

既有 Gemma 资格运行约 9.7 秒/调用；完整 main 约 8,000 calls，完整双次运行的信息增益不足以抵消约翻倍的执行成本。因此冻结合同 B，以保证完整正式结果和跨两数据集/两臂的确定性证据。其确定性等级明确低于 full rerun，报告不得写成全量 byte-identical rerun。

## 6. 统计设计

统计单位为 query。HotpotQA 与 MuSiQue 分别报告两臂绝对 F1/EM、`static_q25 - Dense` 点估计及 95% paired query bootstrap percentile interval。

主要联合量为数据集等权：

```text
delta_equal_weight = (delta_hotpotqa + delta_musique) / 2
```

联合区间使用 dataset-stratified paired bootstrap：两个数据集内分别有放回抽样，每次取两数据集 delta 的等权平均。冻结 `iterations=10000`、`seed=20260724`、NumPy PCG64、linear percentile。直接混合 4,000 queries 的 query-weighted 结果仅作描述性补充，并标明 MuSiQue 权重为 75%。

## 7. 联合判定门

`GENERATOR_TRANSFER_SUPPORTED` 当且仅当：

```text
equal_weight_f1_point >= 0.010
and equal_weight_f1_lower > 0
and hotpot_f1_point > 0
and musique_f1_point > 0
and equal_weight_em_lower >= -0.010
and hotpot_em_upper >= -0.010
and musique_em_upper >= -0.010
```

`GENERATOR_TRANSFER_NEGATIVE` 当以下任一成立：

```text
equal_weight_f1_upper < 0
or hotpot_f1_upper < 0
or musique_f1_upper < 0
or equal_weight_em_upper < -0.010
or hotpot_em_upper < -0.010
or musique_em_upper < -0.010
```

其余为 `GENERATOR_TRANSFER_INCONCLUSIVE`。Gold isolation、query pairing、artifact identity 或 independent verification 任一失败时为 `NO_SCIENTIFIC_DECISION`，不放宽门槛。

## 8. 支持性分析

完整报告每数据集/方法的绝对 F1/EM、UNKNOWN rate、completion length、input tokens、included units、truncation、failed calls、wall time、peak GPU memory 与 subset determinism。另报告：

```text
interaction_delta = second_generator_retrieval_delta - frozen_qwen_retrieval_delta
```

交互项分别给出数据集 paired interval 与等权 stratified summary，仅用于解释，不进入主判定。

## 9. 完整性与停止规则

所有正式输出采用 no-overwrite、pending 写入和完成后原子提升。独立 verifier 必须重建输入身份、ranking membership、prompt prefix/语义 SHA/token 数、completion decode、subset determinism、两套官方答案分数、dataset/bootstrap/equal-weight/interaction 与最终 decision。

仅在冻结输入身份不匹配、Gold 泄漏、query/arm pairing 无法验证、需要改变科学语义、正式工件不可恢复异常或 independent reconstruction 失败时暂停。普通依赖、路径、缓存、日志与性能问题按最小工程修复继续。

## 10. 保持锁定

```text
Reservation = LOCKED
Stage3B = LOCKED
U2 = NOT_AUTHORIZED
controller branch = FROZEN_CLOSED
```
