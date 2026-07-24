# Stage5A-BNH：BGE-Native HyperGranular Retrieval

状态：

```text
STAGE5A_LEVEL_A_SCIENTIFIC_CARD_FROZEN
FULL_STAGE5A_TRANSACTION_AUTHORIZED
STAGE5_PMC_FIRST_ROUND_REMAINS_FROZEN
FULL_WIKI_NOT_AUTHORIZED
RESERVATION_LOCKED
STAGE3B_LOCKED
U2_NOT_AUTHORIZED
```

## 1. 唯一科研问题

本阶段只检验：

> 在固定的 closed-candidate Top-20 多跳问答边界中，以
> `BAAI/bge-large-en-v1.5` 同时承担基础排序与结构空间时，BGE-native
> 自适应粒球、query-aware facet hyperedge 和 protected insertion 的完整
> HyperGranular-RAG，能否相对同一个冻结 BGE Top-20 获得可确认的端到端
> answer-F1 增益？

本阶段不是 MiniLM 与 BGE 的比较，不重启 Stage4I MiniLM sidecar，不搜索第二个
强检索器，不搜索生成器，不运行 full-wiki，不恢复 controller、U2、reservation
或 Stage3B。

## 2. 冻结模型与生成合同

- 检索器：`BAAI/bge-large-en-v1.5`
- revision：`d4aa6901d3a41ba39fb536a557fa166f842b0e09`
- 查询前缀：
  `Represent this sentence for searching relevant passages: `
- 文档输入：`title + ". " + sentence`
- pooling：CLS 后 L2 normalize
- max length：512
- 生成器：`Qwen/Qwen2.5-1.5B-Instruct`
- revision：`989aa7980e4cf806f80c7fef2b1adb7bc71aa306`
- 输入上限：4096 tokens
- `do_sample=false`
- `num_beams=1`
- `max_new_tokens=32`
- batch size：1
- 后处理：仅 `.strip()`

系统提示词固定为：

```text
Answer the question using only the provided evidence. Return only the shortest final answer. If the evidence is insufficient, return UNKNOWN.
```

## 3. 全新数据边界

数据只来自：

- HotpotQA train distractor v1.1；
- MuSiQue-Answerable v1.0 train。

ID 选择只使用 dataset、native ID 和固定 salt。先排除 Stage0–Stage4I 的全部历史
ID，再选择 development；confirmation 从排除历史和 development 后的剩余 ID
中独立选择。选择过程不得读取答案、supporting evidence 或元数据。

样本量固定为：

| 边界 | HotpotQA | MuSiQue | 合计 |
|---|---:|---:|---:|
| development | 500 | 750 | 1,250 |
| confirmation | 1,000 | 1,500 | 2,500 |

这些数量是资源和精度边界，不是功效充分性保证；confirmation 数量不根据
development 效应调整。

三个物理通道保持分离：

- Channel A：query identity、question、candidate units；
- Channel B：answer aliases、official supporting evidence；
- Channel C：level/type/hop 等描述性元数据。

Development Gold 只在 16 个候选配置的排名、prompt、main/subset determinism
及独立 pre-Gold verification 冻结后读取。Confirmation Gold 只在唯一配置、
四臂排名、prompt、main/subset determinism 及独立 pre-Gold verification 冻结后
读取。

## 4. BGE-native 结构定义

### 4.1 自适应粒球

对每个 query 的 candidate pool 使用同一份 L2-normalized BGE unit embeddings。
根球通过 deterministic farthest-pair seeds 递归二分：

1. 第一个 seed 是与当前球 centroid 最不相似的 unit；
2. 第二个 seed 是与第一个 seed 最不相似的 unit；
3. unit 分配给更相似的 seed，完全相等时用
   `SHA256(ball_id + NUL + unit_id)` 的最低位决定；
4. 仅当两个 child 的最小占比至少为 `0.20`，且 size-weighted child
   compactness 严格提高超过 `1e-10` 时接受 split；
5. depth 上限为 8；
6. 叶球大小候选只允许 4 或 6。

该定义没有复用 MiniLM 的绝对相似度、radius、compactness、q25 或 density
门限。

### 4.2 query-local 相对量

每个 query 内独立计算：

- unit BGE score ECDF；
- ball query-centroid score ECDF；
- relative radius ECDF；
- compactness ECDF；
- normalized local density ECDF。

所有 eligibility 和 rerank 只使用 query-local ECDF、rank、固定结构大小与确定性
ID tie-break，不使用跨模型绝对阈值。

### 4.3 facet hyperedge

Question facet 是移除固定 stopword 后、长度至少 3 的字母数字 term。每个粒球的
facet 是其 title/text 中出现的 question facet。按 ball query-score ECDF、
density ECDF 和 ball ID 选择两个 seed balls。Facet expansion 只允许带来至少
一个 seed 尚未覆盖 facet 的非 seed ball。

两种冻结 facet gate：

- `BROAD`：ball query-score ECDF ≥ 0.35，density ECDF ≥ 0.25；
- `STRICT`：ball query-score ECDF ≥ 0.50，density ECDF ≥ 0.50。

最多扩展 4 个 eligible balls。Unit eligibility 只允许 BGE unit-score ECDF
≥ 0.50 或 ≥ 0.75，且必须不在原 BGE Top-20。

Facet unit rerank 固定为：

```text
0.45 * unit_score_ecdf
+ 0.25 * ball_query_score_ecdf
+ 0.15 * ball_density_ecdf
+ 0.10 * ball_compactness_ecdf
+ 0.05 * capped_new_facet_fraction
```

No-facet 使用相同 balls、gate、unit eligibility、budget 和 protection，移除
new-facet 条件与 facet bonus，固定为 centroid/local-ball-only：

```text
0.50 * unit_score_ecdf
+ 0.30 * ball_query_score_ecdf
+ 0.10 * ball_density_ecdf
+ 0.10 * ball_compactness_ecdf
```

### 4.4 placement

- Top-k 固定为 20；
- protected prefix 固定为 10；
- insert budget 候选只允许 2 或 4；
- inserted unit 必须不在原 BGE Top-20；
- protected 和 unprotected 必须共享完全相同的 eligible sequence、realized
  inserted set 和 budget，唯一差异是 placement；
- protected 把 inserted set 放在首个 post-protection position；
- unprotected 把相同 inserted set 放在 rank 1 起始位置。

## 5. 预登记候选族

候选族是以下笛卡尔积，共 16 个配置，不得扩展：

```text
leaf_size              ∈ {4, 6}
facet_gate             ∈ {BROAD, STRICT}
unit_score_percentile  ∈ {0.50, 0.75}
insert_budget          ∈ {2, 4}
```

配置 ID `C01`–`C16` 按上述冻结 JSON 顺序绑定。Development 不做连续参数搜索、
可视化挑选、subgroup 挑选、单数据集挑选或 seed 搜索。

## 6. Stage5A-0 Gold-free geometry feasibility

只用 development Channel A。每个配置报告：

- 每数据集及合并 insertable query rate；
- eligible ball count；
- realized insert count；
- split、balance、compactness stop 统计；
- query facet 覆盖；
- protected/unprotected 的共享插入集合合同。

单配置 feasibility 最低门：

```text
each-dataset insertable rate >= 0.10
combined insertable rate >= 0.15
```

Stage5A-0 通过还要求至少 4 个配置通过，且 leaf size 4 和 6 均有通过配置。这只是
最低几何可行性门，不是答案质量或功效保证。若不通过，必须暂停，不得读取
development Gold 或扩大搜索空间。

## 7. Development 选择

Development methods 为一个共享 `BGE_TOP20` 和 16 个 protected 配置。唯一配置
选择层级：

1. 输入、实现、排名、prompt、determinism 和独立 verifier 全部通过；
2. Stage5A-0 geometry feasible；
3. 两数据集 answer-F1 point delta 不得符号相反；
4. dataset-equal-weight answer-EM delta ≥ -0.010；
5. 最大化 dataset-equal-weight answer-F1 delta；
6. 与最佳值相差不超过 0.002 时，依次选择更低 mean incremental input tokens、
   更小 insert budget、更大的 leaf size、`STRICT`、更高 unit percentile；
7. 最后按 config ID lexical order tie-break。

若没有 eligible configuration，Stage5A 停止，不以 post-hoc 规则补选。

## 8. Confirmation 四臂与统计决策

四臂固定为：

1. `BGE_TOP20`
2. `BGE_NATIVE_HGRAG_PROTECTED_TOP20`
3. `BGE_NATIVE_HGRAG_UNPROTECTED_TOP20`
4. `BGE_NATIVE_HGRAG_NO_FACET_TOP20`

主要比较是 Protected − BGE，主要终点是 paired answer F1，EM 是 supportive
guard。HotpotQA 与 MuSiQue 各自报告，主决策使用两数据集等权平均。每项比较使用
10,000 次 paired bootstrap，seed `20260727`，NumPy PCG64，percentile
`linear`。

决策优先级：

1. integrity failure → `NO_SCIENTIFIC_DECISION`；
2. equal-weight F1 CI upper < 0，或 EM CI upper < -0.010 →
   `BGE_NATIVE_HGRAG_NEGATIVE`；
3. 未满足 negative 且两数据集 F1 point 符号相反，或任一数据集 F1 CI upper < 0
   → `BGE_NATIVE_HGRAG_CROSS_DATASET_HETEROGENEOUS`；
4. equal-weight F1 CI lower > 0、两数据集 F1 point 都 > 0、EM CI lower
   ≥ -0.010 且 F1 point ≥ 0.010 → `BGE_NATIVE_HGRAG_SUPPORTED`；
5. 同上但 0 < F1 point < 0.010 →
   `BGE_NATIVE_HGRAG_SUPPORTED_SMALL_EFFECT`；
6. 其余 → `BGE_NATIVE_HGRAG_INCONCLUSIVE`。

Protected − Unprotected 和 Protected − NoFacet 只生成
SUPPORTED/NEGATIVE/INCONCLUSIVE supporting states，不替代 core decision。

## 9. Determinism、checkpoint 与独立验证

- development：完整 main + 每数据集 50 queries 的 pre-hash subset rerun；
- confirmation：完整 main + 每数据集 100 queries 的 pre-hash subset rerun；
- checkpoint 只能是冻结 task plan 的合法前缀；
- 不覆盖已有 checkpoint 或正式工件；
- 排名、trace、prompt、预测、统计与 verifier 工件均原子提升；
- final 工件只能在 subset prediction/prompt identity 和独立 reconstruction
  通过后产生。

独立 verifier 不调用 runner 的最终 ranking 函数。它独立重建：

- source identity、ID-only selection 与历史零重叠；
- blind schema 与 Gold-free 合同；
- BGE cache identity、row order、normalization；
- adaptive balls、split/stop、query-local ECDF；
- facet hyperedge、eligibility、candidate sequence；
- protected/unprotected/no-facet placement；
- prompt 和 subset determinism；
- development selection；
- answer F1/EM、bootstrap、decision；
- post-Gold added/displaced/net Gold 与 answer change；
- Stage4E–Stage4I 和冻结 Stage5-PMC baseline 完整性。

## 10. Post-Gold 机制与效率

Core decision 冻结后才报告：

- added/displaced/net Gold evidence；
- added/displaced non-Gold units；
- CR@20、ER@20；
- answer gain/same/harm × net Gold positive/zero/negative；
- embedding/cache/storage/retrieval/generation time；
- GPU peak memory、prompt tokens、insert count、failure count；
- incremental cost per equal-weight F1 point。

这些分析均为描述性，不能重新选择配置、改变决策或创建 controller。

## 11. 解释边界与停止规则

即使结果 supported，也只能表述为：在一个冻结 BGE-large-en-v1.5、两个
closed-candidate 多跳 QA confirmation 边界、Top-20 和固定 Qwen 生成合同下，
BGE-native HGRAG 得到支持。不能外推为普遍优于强 Dense、full-wiki 有效或跨
生成器鲁棒。

- Supported：可另行提出 Stage5B-MSB，但不自动启动 full-wiki；
- Supported small：只有成本有竞争力时才允许提出 Stage5B；
- Heterogeneous/Inconclusive：停止自动扩展与搜索；
- Negative：终止当前 strong-dense expansion/full-wiki 路线，保留 Stage5-PMC。

发现 ID overlap、Gold leakage、输入或模型身份不一致、几何退化需要改变语义、
需要扩大搜索空间、confirmation retuning、arm 不能共享候选/插入集合、正式工件
完整性风险或需要访问 locked boundary 时暂停。
