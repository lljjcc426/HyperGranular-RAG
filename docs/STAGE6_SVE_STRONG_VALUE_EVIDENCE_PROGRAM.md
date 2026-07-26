# Stage6-SVE：Strong-Backbone and Structural-Value Evidence Program

状态：

```text
STAGE6_SVE_LEVEL_A_PROGRAM_ACCEPTED
STAGE6A_SMC_FULL_TRANSACTION_AUTHORIZED
STAGE6A_EXECUTION_PENDING
STAGE6B_FULL_WIKI_CONDITIONAL_NOT_AUTHORIZED
STAGE6C_DIRECT_COMPARISON_CONDITIONAL_NOT_AUTHORIZED
RESERVATION_LOCKED
STAGE3B_LOCKED
U2_NOT_AUTHORIZED
```

日期：2026-07-26

## 1. 研究目标与非预设原则

Stage6 不以“证明方法必然有效”为预设结论，而以以下可证伪问题为目标：

> 在现代强检索器、匹配的简单选择器、真实 corpus-scale 检索和可公平复现的
> 结构化 RAG 方法面前，HyperGranular-RAG 是否仍能产生具有实际量级、跨数据集
> 一致且独立确认的 answer-quality 增益；若不能，哪些结构主张应停止？

所有正、负和不确定结果均冻结。不得：

- 以 confirmation、full-wiki 或外部方法结果继续调参；
- 删除失败数据集、失败方法或失败 seed；
- 把区间跨 0 写成等价；
- 把资源不可行写成方法失败，或把方法失败写成运行失败；
- 在看到结果后更换强检索器、主要终点、比较族或成功门。

Stage6 是三段式、有条件停止的研究计划，不是一次无边界模型搜索：

| 子阶段 | 解决的核心缺口 | 是否自动开始 |
|---|---|---|
| Stage6A-SMC | 强检索器增量；粒球/超边相对匹配控制；三数据集广度 | 需一次阶段级授权 |
| Stage6B-FWE | full-wiki 外部效度、ANN、规模、效率 | 仅 Stage6A 通过后另行定稿 |
| Stage6C-DFC | 与 2–3 个结构化/多步 RAG 的公平直接对比 | 仅可复现性与 Stage6A/B 门通过后另行定稿 |

## 2. Material Passport

### 2.1 现有冻结材料

- Stage4E–Stage5A 的正式输入、ranking、prediction、Gold、decision 和 verifier
  工件全部只读，不覆盖、不重跑；
- 历史 BGE、MiniLM、Qwen2.5 和 Gemma 结果只作为先验边界与历史 ID 排除源；
- Stage4D candidate labels/OOF probability 不得进入 Stage6 ranking 或训练；
- Stage3 reservation 的内容、embedding、Gold 和指标保持不可访问。

### 2.2 新模型候选的唯一预指定

Stage6A 只允许：

```text
Qwen/Qwen3-Embedding-0.6B
Qwen/Qwen3-Reranker-0.6B
```

两者均为 0.6B，官方系列提供 embedding/reranking 配对、32K 上限和 instruction-aware
接口。Stage6A-0 只允许进行无 Gold 的下载、许可、revision、文件 SHA、显存、
batch、数值有限性和确定性 smoke test。不得在任何 Stage6 query 上比较第二个
新强检索器。

官方来源：

- <https://github.com/QwenLM/Qwen3-Embedding>
- <https://huggingface.co/Qwen/Qwen3-Embedding-0.6B>
- <https://huggingface.co/Qwen/Qwen3-Reranker-0.6B>

若任一模型不能在 RTX 4060 Laptop 8GB 上以单模型串行方式完成冻结 smoke test，
Stage6A 暂停为 `MODEL_RESOURCE_INFEASIBLE`；不得用 Stage6 Gold 选择替代模型。

### 2.3 生成合同

所有 answer-quality 比较继续使用唯一固定生成器：

```text
Qwen/Qwen2.5-1.5B-Instruct
revision = 989aa7980e4cf806f80c7fef2b1adb7bc71aa306
dtype = FP16
input cap = 4096 tokens
do_sample = false
num_beams = 1
max_new_tokens = 32
batch_size = 1
```

prompt、evidence serialization、截断和 `.strip()` 后处理与 Stage4H/5A 相同。
Stage6 不进行 generator search。这样能把主要差异限制在检索和结构选择，而不是
新生成器。

### 2.4 审计与派生材料

每个正式子阶段必须产生：

- source/model/environment/input manifest；
- Gold-free rankings/candidate trace/prompt audit；
- main 与预哈希 subset deterministic rerun；
- independent pre-Gold verifier；
- Gold-only query score、bootstrap 和 decision；
- independent final verifier；
- artifact manifest、报告和 Git/GitHub 字节核验。

Raw corpus、模型、embedding、ANN index、cache 和密钥不进入 Git。

## 3. Stage6A-SMC：Strong Retriever and Matched Controls

### 3.1 唯一主要问题

> 在三个历史零重叠的 closed-candidate 多跳 QA confirmation 边界上，以同一
> Qwen3 dense first stage、同一 Qwen3 cross-encoder score、同一候选池、Top-20、
> token budget 和生成器为条件，HGRAG joint structural selection 是否同时优于：
> （1）强 reranker Top-20；（2）最强匹配的通用 diversity/coverage selector；
> （3）最强匹配的非粒球局部结构控制？

该问题将“更大的候选池”“更强的 reranker”和“结构选择”分离。所有 arm 都得到
同一候选 universe 和同一 cross-encoder score，HGRAG 不因独占额外候选而获益。

### 3.2 全新数据边界

ID 选择只使用 dataset key、native ID、source row 和固定 salt，不读取 question、
answer、support、hop/type、历史效果或模型输出。先排除 Stage0–Stage5A 的全部
正式 ID，再分 development 与 confirmation。

| 数据集 | development | confirmation | 来源边界 |
|---|---:|---:|---|
| HotpotQA train distractor | 400 | 800 | 既有官方源中历史未使用 ID |
| MuSiQue-Answerable train | 600 | 1,200 | 既有官方源中历史未使用 ID |
| 2WikiMultiHopQA official dev | 400 | 800 | 仅 rows 9819:12576 的历史未使用 ID |
| 合计 | 1,400 | 2,800 | 三数据集等权进入主要统计 |

salt：

```text
stage6a_smc_v1\0
```

2Wiki 的 rows 5300:9800 reservation 仍不可读取；rows 9800:9819 的历史 replacement
也不得复用。若排除历史 ID 后任一数据集不足表中数量，必须在生成样本内容前暂停，
不得缩样、借用 reservation 或换 salt。

三个物理通道：

- Channel A：identity、question、candidate units；
- Channel B：answer aliases、official supporting evidence；
- Channel C：hop/type/source metadata，仅在核心 decision 冻结后描述。

### 3.3 共同强检索合同

单位文本固定为：

```text
title + ". " + unit_text
```

Qwen3 query instruction 固定为：

```text
Given a web search query, retrieve relevant passages that answer the query
```

对每个 query：

1. Qwen3 embedding 对全部 closed candidates 排序；
2. common pool 为 dense Top-`min(100, candidate_count)`；
3. Qwen3 reranker 对 common pool 的全部 `(query, unit)` pair 打分；
4. 所有方法 arm 只能从同一 common pool 选择相同 effective-K；
5. score tie 使用原生非空 string `unit_id` 升序；
6. embedding、reranker score 和全部派生数值保存为 finite float32。

Stage6A-0 在任何正式 query 执行前绑定模型 revision、实际文件 SHA、tokenizer、
pooling、instruction serialization、max length、dtype、batch 和线程环境。

### 3.4 匹配方法族

共同 Top-k 为 20。每个 arm 先保留 reranker Top-8，随后从 common pool 贪心填充
12 个位置。所有 novelty 均相对于已选集合计算，完全相等时用 `unit_id`。

query-local 特征：

```text
R = reranker-score ECDF
D = 1 - max cosine(unit, selected units)
C = newly covered normalized question-term fraction
```

固定 ASCII/Unicode alphanumeric lowercase term tokenizer；去除冻结 stopword；
长度小于 3 的 term 不进入 `C`。

所有 group-based arms 共用以下严格接口。对 grouping `P`：

```text
centroid(g) = L2-normalized mean embedding of units in group g
N_P(i | S) =
  0.5 * I[group_P(i) has no selected unit]
  + 0.5 * (1 - max cosine(centroid(group_P(i)),
                          centroids of groups represented in S)) / 2
```

`S` 尚无 group 时第二项固定为 1。Question facets 使用上面的冻结 tokenizer；
`F_g` 是 group 内出现的 question-facet set。每个 facet `t` 定义一个 query-aware
hyperedge：

```text
H_t = {g : t in F_g}
```

只有 `|H_t| >= 2` 才是 eligible hyperedge。对候选 `i`：

```text
F(i | S) =
  |F_group(i) - facets covered by selected groups| / max(1, |question facets|)

B(i | S) =
  newly activated eligible hyperedges incident to group(i)
  / max(1, number of eligible hyperedges incident to group(i))

S_group_no_hyperedge = N_P
S_group_with_hyperedge = (N_P + F + B) / 3

joint_score =
  lambda * R
  + (1 - lambda) * (0.25 * D + 0.25 * C + 0.50 * S_group)
```

“activated” 指当前加入 `i` 后，某个 `H_t` 首次同时包含 `group(i)` 和至少一个已有
selected unit 所属的不同 group。所有 arm 使用相同计算、归一化、tie-break 和
贪心重算；只允许 grouping `P` 或是否启用 `F/B` 不同。

完整 development 方法：

1. `QWEN3_RERANK_TOP20`：纯 reranker 前 20；
2. `MMR_TOP20`：`lambda*R + (1-lambda)*D`；
3. `MAX_QUERY_COVERAGE_TOP20`：`lambda*R + (1-lambda)*C`；
4. `RELEVANCE_DIVERSITY_COVERAGE_TOP20`：
   `lambda*R + (1-lambda)*(0.5*D + 0.5*C)`；
5. `FIXED_WINDOW_STRUCTURE_TOP20`：按
   `(document_id, paragraph_id, floor(sentence_index / 4))` 形成不重叠固定窗口；
6. `SPHERICAL_KMEANS_STRUCTURE_TOP20`：确定性 spherical k-means，cluster 数与
   同 query 的 HGRAG leaf-ball 数匹配；
7. `HIERARCHICAL_CLUSTER_STRUCTURE_TOP20`：确定性 cosine average-linkage，
   cut 后 group 数同样匹配；
8. `GRANULAR_BALL_NO_HYPEREDGE_TOP20`：保留 adaptive granular balls，
   只用 ball novelty，不使用 facet hyperedge；
9. `HGRAG_JOINT_TOP20`：adaptive granular balls + facet hyperedge gain。

fixed-window、k-means、hierarchical 和 HGRAG 都启用相同 `F/B` 与 joint score，
因此 HGRAG 对最佳 non-ball structure 的差异只在 grouping。Ball-only 使用同一
adaptive grouping 和 joint score，但把 `S_group` 换为 `N_P`，因此 Full 对
ball-only 的差异只在 group-level facet/hyperedge。全部结构量均在 `[0,1]`，只能
改变后 12 个位置的选择，不改变 common pool、reranker score、Top-8 或 token cap。

HGRAG adaptive grouping 复用 Stage5A 的确定性 farthest-pair split 合同：

1. seed 1 为离当前 group centroid 最远的 unit；
2. seed 2 为离 seed 1 最远的 unit；
3. unit 分给 cosine 更高的 seed，完全相等时用
   `SHA256(group_id + NUL + unit_id)`；
4. 两个 child 占比均至少 `0.20` 且 size-weighted compactness 改善严格大于
   `1e-10` 才接受 split；
5. depth 上限 8，leaf target 只允许 4 或 6。

Spherical k-means 使用相同 unit embeddings、`k = HGRAG leaf count`、farthest-first
初始化、最多 100 次 Lloyd 更新、assignment 不再变化即停止；空 cluster 用当前
最大 cluster 中离 centroid 最远的 unit 重置。Hierarchical 使用 cosine distance、
average linkage、`(distance, min_member_id, max_member_id)` tie-break，并切到相同
group count。这样 cluster 数和候选资源完全匹配。

有限参数族：

```text
lambda ∈ {0.70, 0.85}
HGRAG leaf target ∈ {4, 6}
maximum selected structural groups = 4
```

generic selectors 各 2 个配置，替代结构各 2 个 `lambda` 配置，HGRAG/ball-only
各 4 个配置。不得增加 weight、leaf、prefix、pool size、seed、threshold、模型
或手工规则。

### 3.5 Development 选择

Development 对全部配置报告 F1、EM、CR@20、ER@20、tokens、latency、GPU peak、
gain/same/harm 和失败率。每一方法族只按下列统一层级选一个配置：

1. integrity、determinism 和 pre-Gold verification 通过；
2. 三数据集 F1 point 不出现一正一负的明显方向冲突；
3. 三数据集等权 EM delta 相对 `QWEN3_RERANK_TOP20` 不低于 `-0.010`；
4. 最大化三数据集等权 answer-F1；
5. 差值不超过 `0.002` 时依次选更高 `lambda`、更大 leaf target、lexical config ID。

进入 confirmation 的五臂：

1. `QWEN3_RERANK_TOP20`；
2. development 最佳 generic selector（2–4 中选一）；
3. development 最佳 non-ball structure（5–7 中选一）；
4. development 最佳 `GRANULAR_BALL_NO_HYPEREDGE_TOP20`；
5. development 唯一锁定 `HGRAG_JOINT_TOP20`。

Development 结果不与 confirmation 合并，不据其 effect 调整 confirmation 数量。

### 3.6 Confirmation 主要终点与强证据门

主要终点：paired answer F1。支持性 guard：answer EM。每个数据集独立报告；主要
决策使用三数据集等权分层 bootstrap。

三个 primary contrast：

1. `HGRAG_JOINT - QWEN3_RERANK`；
2. `HGRAG_JOINT - BEST_GENERIC_SELECTOR`；
3. `HGRAG_JOINT - BEST_NON_BALL_STRUCTURE`。

`HGRAG_JOINT - GRANULAR_BALL_NO_HYPEREDGE` 是预登记 supporting contrast，用于
facet-hyperedge 增量，不代替前三项。

统计固定：

```text
bootstrap_iterations = 10000
bootstrap_seed = 20260728
NumPy generator = PCG64
percentile = linear
family = three primary F1 contrasts
multiple comparison = Holm step-down, alpha 0.05
```

只有同时满足以下条件，Stage6A 才给出
`STRONG_BACKBONE_AND_STRUCTURAL_VALUE_SUPPORTED`：

- 对 Qwen3 rerank 的等权 F1 point `>= +0.010`；
- 三项 primary contrast 的等权 F1 95% CI lower 均 `> 0` 且 Holm-adjusted
  one-sided p 均 `<= 0.05`；
- 三个数据集的 HGRAG−Qwen3 rerank F1 point 均 `> 0`；
- 任一数据集均不存在该 contrast 的 F1 CI upper `< 0`；
- 三项 contrast 的等权 EM CI lower 均 `>= -0.010`；
- main/subset、Gold 隔离、输入/模型 SHA 和 independent verifier 全部通过。

解释状态：

- 完整满足：`STRONG_BACKBONE_AND_STRUCTURAL_VALUE_SUPPORTED`；
- HGRAG−Qwen3 明确为负：`STRONG_BACKBONE_INCREMENT_NEGATIVE`；
- 强主干有增益但任一结构对照未过：`INCREMENT_SUPPORTED_STRUCTURE_NOT_ISOLATED`；
- 数据集方向明显异质：`CROSS_DATASET_HETEROGENEOUS`；
- 其余：`STAGE6A_EVIDENCE_INCONCLUSIVE`；
- 完整性失败：`NO_SCIENTIFIC_DECISION`。

只有第一个状态允许起草 Stage6B/6C 的正式执行卡。其他状态停止“强有效性”
方法论文扩展，不以 full-wiki 或外部方法搜索救援同一假设。

## 4. Stage6B-FWE：Full-Wikipedia External Validity

本节只冻结下一步设计边界，不授权下载或运行。

### 4.1 数据与语料

- query：HotpotQA official fullwiki 可评分 split 中历史零重叠 ID；
- development 500，confirmation 1,500，ID-only 预哈希选择；
- corpus：2017-10-01 English Wikipedia introductory paragraphs；
- 官方压缩包：1,553,565,403 bytes；
- 官方 MD5：`01edf64cd120ecc03a2745352779514c`；
- 许可：CC BY-SA 4.0；
- 下载后必须再绑定本地 SHA-256、解包流、article count 和 title identity。

官方来源：<https://hotpotqa.github.io/wiki-readme.html>

### 4.2 corpus-scale 管线

```text
Qwen3 dense ANN Top-200
→ Top-20 的一跳 Wikipedia hyperlink neighbors
→ common pool cap 1000
→ Qwen3 reranker
→ same five-arm matched selection
→ final Top-20
→ frozen Qwen2.5 generator
```

所有 arms 共享 ANN 结果、hyperlink-expanded common pool、reranker score、Top-20、
token cap 和 generator。不得让 HGRAG 独享 hyperlink neighbor。

在全文索引前进行 Gold-free 100,000-passage engineering feasibility：

- 精确版本与 ANN 参数可重建；
- exact-vs-ANN recall audit 可定义；
- extrapolated build 不超过 96 GPU-hours；
- index/cache/working storage 不超过 200 GB；
- 峰值 RAM/GPU 不发生资源耗尽；
- 100-query deterministic ranking rerun 同内容。

不通过时状态为 `FULL_WIKI_RESOURCE_INFEASIBLE`，不得看 Gold、换 encoder 或缩 corpus
制造成功。

必须报告：

- supporting-document/passage reachability@20/100/200；
- ANN recall@200 的预哈希 exact audit；
- answer F1/EM、CR/ER；
- index build time、index bytes、embedding bytes、storage peak；
- ANN、neighbor expansion、rerank、structure、generation latency；
- prompt tokens、GPU peak、failure rate、UNKNOWN rate；
- 相同 candidate set 下 added/displaced Gold 和 answer gain/harm。

Stage6B 的强支持门不得低于 Stage6A 的 `+0.010` F1 practical threshold、CI lower
`>0` 和 EM non-inferiority guard。

## 5. Stage6C-DFC：Direct Fair Comparison

本节只登记候选与公平性门，不授权外部代码运行。

候选方法：

1. Q-RAG official pretrained HotpotQA/MuSiQue checkpoint；
2. HippoRAG 2 official code + author-released corpus/OpenIE artifact；
3. MDR/iterative dense retrieval official checkpoint；
4. Stage6A/6B 的 HGRAG 与 Qwen3 rerank baseline。

来源：

- Q-RAG：<https://github.com/griver/Q-RAG>；
- Q-RAG checkpoints：<https://huggingface.co/Q-RAG>；
- HippoRAG 2：<https://github.com/OSU-NLP-Group/HippoRAG>；
- MDR paper：<https://arxiv.org/abs/2009.12756>。

正式卡之前必须完成只读 eligibility audit：

- official repository、commit、license、checkpoint 与数据身份可绑定；
- checkpoint 可在本机只做推理，或作者提供可核验 retrieval outputs；
- 不需要在本机重训 A100-80GB 级模型；
- 不需要私有 API、未披露 prompt 或不可获得 corpus；
- 能在同 query/corpus、Top-20、token cap 和 Qwen2.5 generator 下比较；
- 任何 adapter、模型替换或预处理变化均显式标为 adapted，不能称 exact reproduction。

Q-RAG 官方已发布 HotpotQA/MuSiQue checkpoint，但其完整训练建议 A100-80GB；本项目
只考虑官方 checkpoint 推理。HippoRAG 2 默认论文复现使用 70B LLM、多 GPU 和
NV-Embed-v2，作者目前明确提供的 OpenIE 示例集中在 MuSiQue；若不能在相同数据上
复用官方工件，它不得成为“公平 exact baseline”，只能排除或作为 adapted secondary。

至少两个方法通过 eligibility，且至少一个是 graph/structured RAG，Stage6C 才能
执行。否则记录 `DIRECT_COMPARISON_ARTIFACTS_INSUFFICIENT`，不使用论文表中不可比的
作者点估计替代实验。

## 6. 广泛科学发现的判定边界

只有 Stage6A 支持且 Stage6B 或 Stage6C 至少一个独立支持，论文才可升级为：

> 在三个 closed-candidate 多跳 QA 数据集和至少一个 corpus-scale 或独立结构化
> RAG 边界上，HGRAG 在匹配的现代强 reranker、通用 selector 和替代局部结构之上
> 获得了可确认的结构增量。

即使如此，仍不得主张：

- 普遍优于所有 strong retriever 或所有 RAG；
- granular ball/hyperedge 在所有任务中不可替代；
- 开放域所有语料和语言均有效；
- Qwen3、BGE 或模型架构的一般排名；
- 未执行的 generator、Top-k、语言、领域和成本边界。

若 Stage6A 未通过，论文继续保留 Stage4E–Stage5A 的 bounded positive/negative
故事，不得以 Stage6 development 的局部正值改写 confirmation 结论。

## 7. 授权、执行和停止边界

本协议已获得用户一次阶段级接受与执行授权。授权按全局治理连续覆盖 Stage6A-0、
实现、synthetic tests、三通道、development、configuration lock、confirmation、
Gold、verifier、报告和 Git 同步，不恢复逐命令审批。授权保证完整执行与如实冻结，
不保证统计结果为正，也不允许为了“通过”修改成功门。

Stage6A 授权不自动覆盖：

- Stage6B full-wiki corpus 下载/索引/Gold；
- Stage6C 外部代码、checkpoint 或作者工件；
- reservation、Stage3B、U2、controller；
- 新 generator、第二个新 strong retriever；
- 改变本卡的样本、method family、endpoint、statistics 或 success gate。

只有以下实质问题暂停：数据/模型身份不符、历史 ID overlap、Gold/metadata 泄漏、
本机资源不支持唯一预指定模型、共同候选池合同无法实现、main/rerun 不一致、独立
verifier 失败、正式工件被覆盖，或需要改变本卡科学语义。
