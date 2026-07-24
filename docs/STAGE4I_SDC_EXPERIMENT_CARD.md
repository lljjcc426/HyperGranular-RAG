# Stage4I-SDC 强稠密检索互补性实验卡

状态：`STAGE4I_SDC_EXPERIMENT_CARD_FROZEN`

日期：2026-07-24

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: plan → run → validate
- Verification Status: PRE-REGISTERED
- Version Label: stage4i_sdc_card_v1

## 1. 唯一问题与主张边界

在新的、与全部历史正式 query ID 零重叠的 HotpotQA 和 MuSiQue
closed-candidate 边界上，以事前绑定的 BGE strong-dense Top-20 为主干时，冻结的
MiniLM-HGRAG sidecar 是否带来额外端到端 answer-F1；该变化是否依赖 protected
placement 与 facet-hyperedge。

本阶段只检验一个 BGE 配置下的增量互补性，不重新比较 MiniLM/BGE，不搜索 encoder、
generator、threshold、prefix、budget、controller 或 BGE-native HGRAG，不进行
full-wiki/open-domain 评价。

## 2. 新数据边界

| 数据集 | 样本 | Gold 粒度 |
|---|---:|---|
| HotpotQA train distractor v1.1 | 1,000 | official supporting sentence |
| MuSiQue-Answerable train v1.0 | 1,500 | official supporting paragraph |

先汇总全部登记历史正式 IDs，再加入 Stage4H blind 的 2,500 个 native IDs。对剩余源
IDs 按：

```text
SHA256("stage4i_sdc_v1\0" + dataset_key + NUL + native_id), native_id
```

升序选择。选择只能使用 dataset/native ID，不读取 answer、support、hop、type、
difficulty、历史表现或模型输出。样本量是资源和区间精度边界，不是 power guarantee。

输入冻结为 Blind / Gold / Metadata 三通道。MuSiQue 只使用 supporting paragraph，
不得制造 sentence-level Gold。

## 3. 固定模型与语义空间

### 3.1 BGE 主干

唯一 strong-dense backbone：

```text
BAAI/bge-large-en-v1.5
revision = d4aa6901d3a41ba39fb536a557fa166f842b0e09
```

完全继承 Stage4H 的 query instruction、document encoding、`[CLS]` pooling、L2
normalization、512-token cap、cosine 和 `unit_id` tie-break。

### 3.2 HGRAG sidecar

粒球、facet-hyperedge、centroid-only no-facet 与 q25 eligibility 均在冻结
`sentence-transformers/all-MiniLM-L6-v2@1110a243...` 空间计算：

```text
BGE = 主排名
MiniLM-HGRAG = 独立结构化 sidecar 候选
q25 floor = 0.1957079917192459，只过滤 sidecar
```

不得把 q25 floor 当作 BGE 分数，不进行 MiniLM/BGE score fusion。

### 3.3 Generator

固定 `Qwen/Qwen2.5-1.5B-Instruct@989aa798...`、FP16、batch 1、4096-token
input cap、greedy、`max_new_tokens=32`。system prompt：

```text
Answer the question using only the provided evidence. Return only the shortest final answer. If the evidence is insufficient, return UNKNOWN.
```

输出只做首尾 whitespace strip。

## 4. 四个方法臂

1. `BGE_TOP20`：冻结 BGE Top-20。
2. `BGE_HGRAG_PROTECTED_TOP20`：保护 BGE Top-10；使用 MiniLM-HGRAG facet
   candidates；先排除 BGE Top-20 duplicates，再插入最多 4 个；按原 BGE 顺序补齐。
3. `BGE_HGRAG_UNPROTECTED_TOP20`：使用与 protected 臂完全相同的 deduplicated
   candidate sequence 和 realized inserted set；将它们放在 BGE ranking 前部，再按
   原 BGE 顺序补齐。
4. `BGE_HGRAG_NO_FACET_TOP20`：保留 BGE 主干、MiniLM 粒球、q25、Top-10
   protection、budget 4，只把 facet-hyperedge 换成 Stage4H 冻结的 centroid-only
   expansion。

所有 arm 共享 query universe、candidate pool、effective-K、prompt 和 generator。最终
ranking 必须唯一、属于同 query candidate pool，长度为 `min(20, pool size)`。

## 5. Blind-only eligibility gate

正式 Gold 读取前报告每数据集：

- eligible-query rate；
- eligible candidates/query 分布；
- 与 BGE Top-20 / protected Top-10 overlap；
- post-dedup candidates/query；
- realized insertion count；
- zero-insertion rate；
- full-budget insertion rate。

最低可检验门：

```text
each dataset insertable-query rate >= 0.10
combined insertable-query rate >= 0.15
```

这是 minimum feasibility threshold，不是 power guarantee。若任一门失败，判
`STAGE4I_SIDECAR_ACTIVATION_DEGENERATE`，在读取 Gold 前暂停并重新定义新协议；不得
试跑多个 threshold 的 Gold 后挑选。近乎全开只作为 selectivity caution，不自动修改参数。

## 6. 统计与判定

主要比较：

```text
BGE_HGRAG_PROTECTED_TOP20 - BGE_TOP20
```

主要终点是 paired answer F1；支持性 guard 是 paired answer EM。分别报告 HotpotQA、
MuSiQue 和数据集等权分层 bootstrap：

```text
iterations = 10000
seed = 20260726
NumPy generator = PCG64
percentile method = linear
```

核心判定按下列顺序：

1. integrity failure → `NO_SCIENTIFIC_DECISION`
2. equal-weight F1 CI upper `<0` 或 EM CI upper `<-0.010`
   → `STRONG_DENSE_COMPLEMENTARITY_NEGATIVE`
3. 未达 negative，且两数据集 F1 点估计异号，或任一数据集 F1 CI upper `<0`
   → `STRONG_DENSE_COMPLEMENTARITY_CROSS_DATASET_HETEROGENEOUS`
4. equal-weight F1 CI lower `>0`、点估计 `>=0.010`、两数据集 F1 点估计均
   `>0`、equal-weight EM CI lower `>=-0.010`
   → `STRONG_DENSE_COMPLEMENTARITY_SUPPORTED`
5. 上述条件相同但 `0 < equal-weight F1 < 0.010`
   → `STRONG_DENSE_COMPLEMENTARITY_SUPPORTED_SMALL_EFFECT`
6. 其余 → `STRONG_DENSE_COMPLEMENTARITY_INCONCLUSIVE`

支持性比较不覆盖核心状态，也不触发晋级：

- Protected−Unprotected：placement state；
- Unprotected−BGE、Protected−BGE：placement context；
- Protected−NoFacet：facet state。

placement/facet 的 `SUPPORTED` 要求等权 F1 CI lower `>0` 且 EM CI lower
`>=-0.010`；`NEGATIVE` 要求 F1 CI upper `<0` 或 EM CI upper `<-0.010`；其余为
`INCONCLUSIVE`。这些支持性比较不做新的 threshold/model 选择。

## 7. 确定性与工件事务

冻结：

```text
full main = 2,500 queries × 4 arms = 10,000 calls
rerun subset = 100 queries/dataset × 4 arms = 800 calls
rerun selection = SHA256("stage4i_sdc_rerun_v1\0" + dataset + NUL + query_id)
```

subset 只使用 ID。checkpoint 只能恢复合法执行前缀；正式工件使用 no-overwrite
pending/atomic promotion。main/subset 对应 prediction 和 prompt audit 必须精确一致。

## 8. Gold 后机制审计

只有 rankings/predictions 冻结、pre-Gold verifier 通过、Gold evaluation 与核心 decision
冻结后，才计算每 query：

- added Gold evidence；
- displaced BGE Gold evidence；
- `net_gold_evidence_change = added - displaced`；
- CR/ER change；
- added/displaced non-Gold；
- insertion count；
- answer gain/same/harm × net Gold positive/zero/negative。

HotpotQA 按 supporting unit，MuSiQue 按 supporting paragraph。机制审计只作描述，不用于
candidate、threshold、placement、晋级或 controller。

## 9. 独立验证与停止边界

独立 verifier 必须自行重建 ID selection、通道身份、BGE ranking、MiniLM-HGRAG
facet/no-facet candidates、q25、去重、共同 inserted set、protected/unprotected
placement、budget、membership、prompt、determinism、F1/EM、bootstrap、全部状态、
Gold evidence transition、artifact identities、环境/代码绑定，并确认 Stage4E–4H
工件未变。不得直接调用 runner 的最终四臂选择函数替代重建。

只在以下实质问题暂停：历史 ID overlap、source/model/channel 身份不可信、Gold 泄漏、
activation gate 失败、四臂不共享 universe/pool、protected/unprotected candidate set
不一致、需要改变冻结科学语义、正式工件不可恢复、verifier 无法重建，或需要访问
Reservation/Stage3B/U2/controller/full-wiki Gold。

## 10. 锁定

```text
Reservation = LOCKED
Stage3B = LOCKED
U2/controller = NOT_AUTHORIZED
new generator/strong-dense search = NOT_AUTHORIZED
full-wiki Gold = NOT_AUTHORIZED
Stage4E–Stage4H overwrite/rerun = PROHIBITED
```
