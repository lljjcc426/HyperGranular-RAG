# HyperGranular-RAG Stage4F-XDR 跨数据集复制报告

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run + validate
- Origin Date: 2026-07-22
- Verification Status: VERIFIED
- Version Label: stage4f_xdr_result_v1
- Scientific Decision: `STATIC_HGRAG_XDR_SUPPORTED`

## 1. 科学问题与结果

Stage4F-XDR 只检验一个预注册问题：Stage4E 在 HotpotQA 上观察到的 static all-query q25 protected insertion 相对 Dense Top-20 的 answer-F1 增益，能否在新的 MuSiQue-Answerable v1.0 train 3,000-query 边界上复现。

冻结结果为 `STATIC_HGRAG_XDR_SUPPORTED`。Static-q25 的 answer F1 为 `0.14735383`，Dense 为 `0.13595240`，成对差为 `+0.01140143`，95% paired-bootstrap interval 为 `[0.00449534, 0.01835158]`。该结果通过预注册的最小效应、F1 区间和 EM guard，但只支持当前数据、模型、prompt、Top-20 和静态 q25 配置下的跨数据集复制。

## 2. Material 与冻结边界

| 项目 | 冻结值 |
|---|---|
| 数据 | MuSiQue-Answerable v1.0 train；官方仓库 `StonyBrookNLP/musique@922ac98f...`；CC BY 4.0 |
| source | 19,938 rows；241,046,755 bytes；SHA-256 `83A75B1E...248490A` |
| 样本 | 只按原生 ID hash 选择 3,000 queries；与历史 MuSiQue dev 1,000 IDs overlap 0 |
| candidate units | source-only regex sentence splitter；218,698 units；每题 27–151 |
| Gold | official answer/aliases 与 supporting paragraph；不存在 supporting-sentence Gold |
| encoder | `sentence-transformers/all-MiniLM-L6-v2@1110a243...` |
| generator | `Qwen/Qwen2.5-1.5B-Instruct@989aa798...`，FP16 |
| generation | 4,096-token cap；greedy；beams 1；max new tokens 32；batch 1 |
| arms | `DENSE_TOP20` vs `STATIC_Q25_TOP20`；无 U1/controller |
| statistics | 10,000 次 paired query bootstrap；PCG64 seed `20260723` |

Blind Channel 单独驱动 embedding、ranking、prompt 与 generation。Gold Channel 只在 `STAGE4F_PRE_GOLD_ARTIFACTS_VERIFIED` 后打开。Channel C 只在总指标、bootstrap 和 decision 冻结后读取。Gold、answer、aliases、support 和 metadata 均未进入检索、prompt、生成、截断、重试或样本选择。

## 3. 主要与支持性终点

| 指标 | Dense Top-20 | Static q25 Top-20 | q25 − Dense / 95% interval |
|---|---:|---:|---:|
| Answer F1 | 0.13595240 | 0.14735383 | `+0.01140143 [0.00449534, 0.01835158]` |
| Answer EM | 0.10033333 | 0.11033333 | `+0.01000000 [0.00333333, 0.01666667]` |
| Supporting-paragraph CR@20 | 0.58900000 | 0.65000000 | +0.06100000 |
| Supporting-paragraph ER@20 | 0.80552778 | 0.84127778 | +0.03575000 |
| UNKNOWN rate | 0.67833333 | 0.65566667 | -0.02266667 |

冻结支持门逐项通过：F1 point `0.01140143 ≥ 0.010`；F1 lower `0.00449534 > 0`；EM lower `0.00333333 ≥ -0.010`。主统计使用未四舍五入的 query-level 分数。

3,000 个 query 中，125 个 F1 增益、77 个 F1 受损、2,798 个不变。该分解是描述性结果，不替代预注册的总体 paired endpoint。

## 4. Retrieval、上下文与成本

- q25 共插入 7,233 个单元，平均每题 2.411；2,336/3,000 queries 至少插入一个单元；单题范围 0–4。
- 两臂每题均实际包含 20 个 evidence units；没有 rank-1 truncation，也没有触及 4,096-token 上限。
- Dense 平均输入 880.609 tokens，范围 501–2,785；Static-q25 平均 884.089，范围 538–2,880。
- main/rerun 各完成 6,000 generation calls，failed calls 均为 0。
- main generation wall time 为 1,947.368 秒，rerun 为 6,446.540 秒。时间差属于运行环境敏感的描述量，不影响 byte-identical 科研输出合同。
- main/rerun GPU peak allocated memory 分别为 4,268,833,280 和 4,268,636,672 bytes，约 3.98 GiB。

## 5. 确定性与独立验证

| 工件 | Main / rerun 结论 |
|---|---|
| predictions | 1,106,316 bytes；SHA-256 均为 `68F95245...34E62E`；同字节 |
| prompt audits | 8,573,108 bytes；SHA-256 均为 `D27D24E7...FF132E`；同字节 |
| embedding cache | 399,838,172 bytes；SHA-256 `5D8A1155...6D0073`；仅本地数据目录 |
| pre-Gold verifier | `STAGE4F_PRE_GOLD_ARTIFACTS_VERIFIED` |
| final verifier | `STAGE4F_FINAL_VERIFICATION_PASS` |

最终 independent verifier 从官方 source 重建 A/B/C 三通道与历史零重叠，逐文件核验 MiniLM/Qwen snapshots 和环境绑定，并独立检查：pre-Gold 工件未改变、main/rerun 字节一致、telemetry 为 12,000 次总调用且零失败、prompt evidence 是对应 ranking 前缀、token cap、双臂配对、Gold 隔离、3,000 条 query audit、overall metrics、10,000 bootstrap、decision 和所有正式工件 Bytes/SHA。

正式执行后发现原 `verify_postgold()` 只覆盖 bootstrap/decision，未完整覆盖上述 final-verification 合同。工程修正仅扩展 verifier 与三个定向测试，不修改 evaluator、ranking、predictions、prompt audits、Gold 工件、统计门或科学语义；27/27 Stage4F tests 通过。正式工件未删除、覆盖或重跑。

## 6. 与 Stage4E 的关系

Stage4E 在 HotpotQA 1,000-query same-domain closed-distractor 边界上的 F1 delta 为 `+0.01478 [0.00020, 0.02988]`；Stage4F 在 MuSiQue 3,000-query 边界上的 F1 delta 为 `+0.01140 [0.00450, 0.01835]`。两阶段方向一致，且分别按各自冻结规则得到 `STATIC_HGRAG_E2E_SUPPORTED` 与 `STATIC_HGRAG_XDR_SUPPORTED`。

这提高了“当前静态 protected insertion 在两个已冻结多跳 QA closed-candidate 边界上可改善 answer F1”的证据等级，但仍不是 full-wiki、open-domain、跨生成器、所有设备或所有任务的确认。也不能由此恢复 U1/Stage4D controller。

## 7. Channel C 描述性审计

| Hop count | Queries | Dense F1 | Static-q25 F1 | 点差 |
|---:|---:|---:|---:|---:|
| 2 | 2,148 | 0.15419287 | 0.16108615 | +0.00689328 |
| 3 | 665 | 0.09685759 | 0.11803439 | +0.02117681 |
| 4 | 187 | 0.06545782 | 0.09387998 | +0.02842215 |

全部行统一标记 `SUBGROUP_CAUTION`。这些是 primary decision 冻结后才读取的点估计，没有确认性区间、没有多重比较调整，也不能生成新阈值、规则或 controller。

## 8. 11 类统计谬误扫描

覆盖率：11/11。

| 谬误 | 结论 |
|---|---|
| Simpson's paradox | 总体与 2/3/4-hop 描述性方向未反转；subgroup 不参与决策 |
| Ecological fallacy | 统计单位与推断单位均为 query；不由 hop aggregate 推断单题机制 |
| Berkson's paradox | answerable-train 与 closed-candidate 选择限制外部效度；未据此声称总体任务分布 |
| Collider bias | 主要 paired analysis 未按结果后变量筛选或调整 |
| Base-rate neglect | 主要指标不是诊断分类率；同时报告绝对 F1/EM 与差值 |
| Regression to the mean | 样本不是按极端 Stage4E/Stage4F 结果筛选；无 pre/post 极端组 |
| Survivorship bias | 3,000 queries 全部双臂配对，12,000 calls 零失败，无丢弃 query |
| Look-elsewhere effect | 单一预注册 primary endpoint；Channel C 明确为 post-decision 描述性 |
| Garden of forking paths | 数据、模型、prompt、K、q25、bootstrap 与门均在结果前冻结；无结果驱动重调 |
| Correlation != causation | 结论限于同一冻结 pipeline 中两检索臂的配对比较，不外推现实因果机制 |
| Reverse causality | retrieval arm 在生成前固定，不用答案结果反向决定 ranking |

整体置信度：`SOLID`（对当前冻结边界）；外部泛化：`CAUTION`。

## 9. 限制与禁止外推

- MuSiQue 只提供 supporting-paragraph Gold；`supporting_fact_sentence_recall` 明确不可用，未伪造句子级 supporting-fact recall。
- `n=3000` 是资源/精度边界，不是正式 power guarantee。
- 本实验是跨数据集复制，但候选仍来自题内给定 paragraphs；不是 full-wiki 或 open-domain。
- 生成器只有 Qwen2.5-1.5B-Instruct；不能外推到所有 LLM、设备或部署格式。
- 公开 MuSiQue 数据可能存在于预训练语料；本项目只证明 ID 对自身既有研究流程未读与历史 overlap 0。
- `SUPPORTED` 不授权 controller、candidate selector、Reservation、Stage3B、U2、prompt/model search 或 q25 retuning。

## 10. 复现入口

- 实验卡：`docs/STAGE4F_XDR_EXPERIMENT_CARD.md`
- 配置：`configs/stage4f_xdr_official.json`
- 输入清单：`results/stage4f_xdr_musique_train3000_v1_input_manifest.json`
- pre-Gold：`results/stage4f_xdr_musique_train3000_v1_verified_pregold.json`
- 结果摘要：`results/stage4f_xdr_musique_train3000_v1_evaluation_summary.json`
- 决策：`results/stage4f_xdr_musique_train3000_v1_scientific_decision.json`
- final verification：`results/stage4f_xdr_musique_train3000_v1_final_verification.json`
- Channel C：`results/stage4f_xdr_musique_train3000_v1_descriptive_subgroups.json`
- 最终工件清单：`results/stage4f_xdr_musique_train3000_v1_artifact_manifest.json`

Reservation、Stage3B、U2 与 controller 全程保持锁定。
