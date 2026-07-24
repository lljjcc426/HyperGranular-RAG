# HyperGranular-RAG Stage4I-SDC 强稠密检索互补性报告

状态：`STAGE4I_FINAL_VERIFICATION_PASS`

日期：2026-07-24

## 1. 研究问题

Stage4I-SDC 检验一个比 Stage4H 更窄的问题：在新的、与全部历史正式 query ID
零重叠的 HotpotQA/MuSiQue closed-candidate 边界上，冻结的
MiniLM-HGRAG 能否作为事前绑定的 BGE large-en-v1.5 Top-20 的结构化 sidecar，
提高端到端答案质量；若有变化，它是否依赖 protected placement 或
facet-hyperedge。

本阶段不比较 MiniLM 与 BGE 的基础模型能力，不搜索强检索器，不进行 score fusion，
也不访问 full-wiki、Reservation、Stage3B、U2 或 controller。q25 floor 只过滤
MiniLM sidecar candidates，不是 BGE threshold。

## 2. 冻结设计

数据边界：

- HotpotQA train distractor v1.1：1,000 queries；
- MuSiQue-Answerable train v1.0：1,500 queries；
- 与全部历史正式 ID overlap：0；
- candidate units：HotpotQA 41,353，MuSiQue 109,296；
- Blind/Gold/Metadata 三通道分离，ID-only hash selection 不使用 Gold 或 metadata。

四个方法臂：

1. `BGE_TOP20`；
2. `BGE_HGRAG_PROTECTED_TOP20`；
3. `BGE_HGRAG_UNPROTECTED_TOP20`；
4. `BGE_HGRAG_NO_FACET_TOP20`。

Protected 与 unprotected 使用完全相同的 facet candidate sequence 和 realized
inserted set，只改变 placement。主比较为 Protected−BGE，主要终点为
dataset-equal-weight answer F1，EM 使用 `-0.010` guard。统计使用 seed
`20260726`、10,000 次分数据集成对/等权分层 bootstrap。

## 3. Blind-only activation

冻结最低门为每个数据集 insertable-query rate 至少 0.10、合并至少 0.15。正式结果：

| 数据集 | eligible-query rate | insertable-query rate | full-budget rate | zero-insertion rate |
|---|---:|---:|---:|---:|
| HotpotQA | 0.6450 | 0.4580 | 0.1140 | 0.5420 |
| MuSiQue | 0.8253 | 0.7133 | 0.2420 | 0.2867 |
| 合并 | — | 0.6112 | — | — |

因此 `STAGE4I_SIDECAR_ELIGIBILITY_GATE_PASS`。这是可运行性最低门，不是功效保证，
也不构成 sidecar 有效性证据。

## 4. 端到端结果

### 4.1 主要比较：Protected−BGE

| 边界 | Δ answer F1 [95% CI] | Δ answer EM [95% CI] |
|---|---:|---:|
| HotpotQA | -0.00298 [-0.01453, 0.00870] | -0.00200 [-0.01400, 0.01000] |
| MuSiQue | -0.00215 [-0.01082, 0.00658] | -0.00267 [-0.01067, 0.00533] |
| 数据集等权 | -0.00256 [-0.00998, 0.00458] | -0.00233 [-0.00983, 0.00467] |

两数据集 F1 点估计均为负，但区间均跨 0；等权 F1/EM 未触发预注册负向门，也未满足
支持门。冻结核心状态为：

```text
STRONG_DENSE_COMPLEMENTARITY_INCONCLUSIVE
```

### 4.2 placement 与 facet 支持性比较

| 比较 | 等权 Δ answer F1 [95% CI] | 等权 Δ answer EM [95% CI] | 状态 |
|---|---:|---:|---|
| Protected−Unprotected | +0.01122 [0.00129, 0.02104] | +0.01300 [0.00333, 0.02283] | `PROTECTED_PLACEMENT_SUPPORTED` |
| Unprotected−BGE | -0.01379 [-0.02440, -0.00339] | -0.01533 [-0.02617, -0.00500] | 支持性负向背景 |
| Protected−NoFacet | -0.00743 [-0.01616, 0.00132] | -0.00600 [-0.01483, 0.00283] | `BGE_FACET_INCREMENT_INCONCLUSIVE` |

这组结果表明：在 sidecar 被激活的当前冻结系统中，保护 BGE 前缀优于把同一插入集合
置于 ranking 前部；但 protected sidecar 本身没有显示优于 BGE-only。facet 比较也未提供
独立正向证据。支持性比较不得覆盖核心 `INCONCLUSIVE` 状态。

### 4.3 绝对指标

HotpotQA：

- BGE：F1 0.51952，EM 0.440，CR@20 0.926；
- Protected：F1 0.51655，EM 0.438，CR@20 0.917；
- Unprotected：F1 0.50723，EM 0.428，CR@20 0.917；
- NoFacet：F1 0.52370，EM 0.444，CR@20 0.905。

MuSiQue：

- BGE：F1 0.16650，EM 0.120，CR@20 0.77333；
- Protected：F1 0.16435，EM 0.11733，CR@20 0.77000；
- Unprotected：F1 0.15122，EM 0.10133，CR@20 0.77000；
- NoFacet：F1 0.17206，EM 0.12333，CR@20 0.75933。

## 5. post-decision 机制审计

机制统计在核心 decision 冻结后计算，只作描述：

| 数据集 / 方法 | added Gold | displaced BGE Gold | net Gold |
|---|---:|---:|---:|
| HotpotQA / Protected | 21 | 29 | -8 |
| HotpotQA / Unprotected | 21 | 29 | -8 |
| HotpotQA / NoFacet | 6 | 28 | -22 |
| MuSiQue / Protected | 59 | 50 | +9 |
| MuSiQue / Unprotected | 59 | 50 | +9 |
| MuSiQue / NoFacet | 43 | 62 | -19 |

Protected 与 unprotected 的 Gold 集合统计相同，符合“同候选集合、只改变顺序”的合同；
它们的答案质量差异说明 generator utilization 对 placement 敏感。HotpotQA 与 MuSiQue 的
net-Gold 方向不同，但这不是事前主要判定，也不能用于事后调整 threshold、facet 或 prefix。

## 6. 完整性、确定性与资源

- full main：2,500 queries × 4 arms = 10,000 calls，失败 0；
- pre-hash subset：200 queries × 4 arms = 800 calls，失败 0；
- subset 的 800 个 predictions 与 prompt audits 均与 main 对应 pair 精确一致；
- main wall time：4,999.07 s；GPU peak：4,356,265,984 bytes；
- MiniLM/BGE caches：276,194,136 / 668,255,684 bytes；
- pre-Gold verifier 独立重建输入选择、cache、四臂、prompt 与 determinism；
- final verifier 独立重算 query metrics、bootstrap、decisions、机制表与工件身份。

eligibility 后首次 main 在生成前发现 cache loader 对已经 L2-normalized 的 float32 矩阵
再次归一化，最大改变 `2.98e-08`，导致一个 MuSiQue no-facet ranking 中两个近并列 BGE
单元交换。最小修正只保留缓存原始 float32，同时继续严格验证形状、有限性、ID 顺序和
L2 范数。原缓存重建与已冻结 rankings 完全一致；缓存、rankings、trace 和 eligibility
工件均未删除、覆盖或重建。修正后 implementation 重新绑定，main 才开始生成。

外层工具在 main 运行约一小时后返回 timeout，但 Python 父/子进程仍存活并继续写同一
checkpoint；没有启动第二个事务。原进程完成 10,000 calls 后一次性提升三项正式 main
工件。

## 7. 结论与论文边界

允许的结论：

> 在一个事前绑定的 BGE large-en-v1.5、Qwen2.5-1.5B-Instruct 和两个新的
> closed-candidate 数据边界上，冻结 MiniLM-HGRAG protected sidecar 相对 BGE-only 的
> 等权 answer-F1 差为 -0.00256，95% CI [-0.00998, 0.00458]，因此强稠密检索互补性
> 证据不充分。对同一插入集合，protected placement 明确优于 unprotected placement，
> 但该支持性结果不能改写核心 inconclusive 结论。

不得写成：

- HyperGranular-RAG 已经优于强稠密检索器；
- MiniLM-HGRAG sidecar 已经无效或等价于 BGE；
- protected placement 使 sidecar 优于 BGE；
- facet-hyperedge 在强 BGE 上已经有效或无效；
- 结果可外推到其他强 encoder、生成器、full-wiki 或 open-domain。

本阶段不改变 Stage4E/4F 的静态 q25 相对历史 MiniLM Dense 正结果，也不改变 Stage4H
的 Full−BGE 负结果。它进一步限定论文主张：结构化补全在较弱历史 Dense 主干上的收益
没有在当前强 BGE sidecar 形式下转化为可确认的额外答案质量。

## 8. 冻结入口

- 实验卡：`docs/STAGE4I_SDC_EXPERIMENT_CARD.md`
- official config：`configs/stage4i_sdc_official.json`
- eligibility：`results/stage4i_sdc_hotpot1000_musique1500_v1_eligibility_audit.json`
- equal-weight summary：`results/stage4i_sdc_hotpot1000_musique1500_v1_equal_weight_summary.json`
- evidence transitions：`results/stage4i_sdc_hotpot1000_musique1500_v1_evidence_transition_audit.json`
- scientific decision：`results/stage4i_sdc_hotpot1000_musique1500_v1_scientific_decision.json`
- final verification：`results/stage4i_sdc_hotpot1000_musique1500_v1_final_verification.json`
- artifact manifest：`results/stage4i_sdc_hotpot1000_musique1500_v1_artifact_manifest.json`

Reservation、Stage3B、U2/controller、full-wiki Gold 和新 strong-retriever search 继续锁定。
