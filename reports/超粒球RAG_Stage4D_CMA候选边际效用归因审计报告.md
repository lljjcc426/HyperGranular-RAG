# Stage4D-CMA：候选边际效用归因审计

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validate
- Origin Date: 2026-07-20
- Verification Status: VERIFIED
- Version Label: stage4d_cma_official_development_v1

## 结论

```text
CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE
```

Stage4D-CMA 在完整 eligible candidate universe 上完成了候选级反事实归因与固定 grouped OOF probe。唯一可触发晋级的 `COMBINED_DEPLOYABLE_28` 在 Task C（`MARGINAL_GAIN` vs `DISPLACEMENT_HARM`）得到 AUROC `0.64310`，query-cluster bootstrap 95% interval 为 `[0.55520, 0.72974]`；AP 为 `0.72198`，prevalence 为 `0.53052`。该 panel 显示出部分候选符号可分性，但 AUROC 未达到冻结的 `0.65` 门，Brier `0.26321` 也未优于 training-prevalence baseline 的 `0.25338`，因此不能进入 U2。

四个固定 panel 又没有全部满足 stop rule，所以本阶段也不能得出“candidate-level 机制不可学习”的结论。冻结 decision rule 的剩余分支是 `CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE`。这不改写 Stage4B-U1-D 的有效 development 负结果，不授权 U2、reservation、Stage3B 或新 controller。

## 研究角色与边界

- 角色：同一 4,500-query development 上的 post-Gold exploratory candidate-mechanism audit，不是外部确认性 efficacy evaluation。
- Channel A 在 Gold-free 边界内生成 4,500 条 query trace 和 8,467 条 candidate trace；Channel B 只在 ranking/trace 冻结后连接既有 development Gold map形成反事实标签。
- 特征矩阵不含 Gold identity、question type、marginal label、counterfactual delta、candidate ID 或其他禁止字段。
- Task C 只使用 `MARGINAL_GAIN` 与 `DISPLACEMENT_HARM`；ER-only、interaction、redundant 和 neutral 候选没有混入正负符号任务。
- 唯一 advancement panel 是 `COMBINED_DEPLOYABLE_28`；其他三个 panel 只作全量报告。
- 没有访问 reservation、Stage3B、新 Gold 或外部测试集；没有起草或实现 U2。
- 没有修改候选生成、Dense/q25 ranking、feature panels、labels、fold、model、bootstrap、threshold 或 decision gate。

## 冻结输入与工件

### Channel A/B 输入

| 工件 | Bytes | SHA-256 |
|---|---:|---|
| query trace | 13,084,375 | `3436B194A460601A4815AEABE637655DC103290CC940CD094FFEB16F84240D7D` |
| candidate trace | 17,237,780 | `F89E189D22DC09FA083C0F9C334FDB381BBAAD4470F8A98089088E98CD2A3E07` |
| Channel A manifest | 1,318 | `0DE37CDBFF96C461BCE7521EA9CBC4BCC75087DACE2BBA4D8A656D614748D5A6` |
| Channel A verification | 313 | `03C1B66D848604F0AAF17620D39926B85764B0753198508F901DCF445A3DAAA5` |
| candidate labels | 6,229,542 | `E206895E36FB7472502E8FEA082C1AEA7C7AD2CB7E198F37200B271E7164F9E3` |
| counterfactual summary | 5,189 | `37A57AD7AB2760C8C9E368F359C80B378F51C6B5C38629BDC0A75ECEB5D6C9F1` |

### Probe 工件

| 工件 | Rows | Bytes | SHA-256 |
|---|---:|---:|---|
| fold assignments | 2,446 queries | 141,871 | `9B80923965407838105BA182E45B685EF5CD60ABC148B49061576EFDAF6FA650` |
| OOF predictions | 68,588 | 13,335,718 | `29EC13EC6AEAB28837C3EBBE24F99AF496A98B0793475DADF2BA071FFEE7ECDC` |
| metrics | — | 117,023 | `22C843E248D0EB44893E42FB61D207061E8F9E07744A4C808AB8F55D63226999` |

## 候选归因结果

8,467 个候选分为原插入集合 7,260 个和预算外 eligible candidates 1,207 个。标签保持七类互斥合同：

| Primary label | Candidates | Distinct query clusters |
|---|---:|---:|
| `MARGINAL_GAIN` | 113 | 113 |
| `DISPLACEMENT_HARM` | 100 | 45 |
| `EVIDENCE_GAIN_ONLY` | 86 | 72 |
| `EVIDENCE_HARM_ONLY` | 42 | 18 |
| `INTERACTION_DEPENDENT` | 103 | 50 |
| `REDUNDANT_GOLD` | 413 | 381 |
| `NEUTRAL_NOISE` | 7,610 | 2,378 |

`delta_standardized_single_cr` 只表示统一首个 post-protection position 的 standardized first-slot insertion utility，不表示候选在历史 q25 位置的实际贡献。原插入集合同时报告 `LOO_NO_BACKFILL`（主要 set-context attribution）和 `LOO_WITH_BACKFILL`（相对下一 eligible candidate 的 replacement sensitivity）；with-backfill 没有决定 primary label。

候选级重建与 query-level q25 对账仍为 94 个 CR-gain queries、69 个 CR-harm queries。8,467 条标签、displacement、双 LOO、replacement subtype 和 budget region 已由独立验证器从冻结 trace/Gold target 重新核对。

## 固定 OOF learnability probe

三个任务均达到“最低可行性阈值”，该阈值不是 power guarantee。Task C 包含 113 个 gain candidates、100 个 harm candidates，来自 113/45 个独立 query clusters；五个 fold 均至少包含 5/5 个正负 query clusters。

| Task | Panel | AUROC | 95% interval | AP | Prevalence |
|---|---|---:|---|---:|---:|
| Gain vs all | `COMBINED_DEPLOYABLE_28` | 0.87852 | [0.85554, 0.90033] | 0.11745 | 0.01335 |
| Harm vs all | `COMBINED_DEPLOYABLE_28` | 0.79720 | [0.75910, 0.83752] | 0.03054 | 0.01181 |
| Gain vs harm | `RELEVANCE_RANK_8` | 0.51088 | [0.42444, 0.60164] | 0.59741 | 0.53052 |
| Gain vs harm | `SUPPORT_STRUCTURE_10` | 0.56912 | [0.46715, 0.66752] | 0.61615 | 0.53052 |
| Gain vs harm | `COMPLEMENTARITY_RISK_10` | 0.59929 | [0.51467, 0.68488] | 0.69236 | 0.53052 |
| Gain vs harm | `COMBINED_DEPLOYABLE_28` | 0.64310 | [0.55520, 0.72974] | 0.72198 | 0.53052 |

Gain-vs-all 和 harm-vs-all 说明 deployable features 可以识别稀少的候选事件，但这种“事件 vs 大量非事件”的能力不能替代 Task C 的 gain/harm 符号选择。Task A/B prevalence 仅 `1.3346%` 和 `1.1811%`，因此不能只凭 AUROC 表述为可部署 selector；其 AP 分别仅为 `0.11745` 和 `0.03054`。

## 唯一 advancement panel 的冻结门

`COMBINED_DEPLOYABLE_28` 的 Task C 结果：

- AUROC `0.64310`，未达到 `0.65`：FAIL。
- AUROC interval lower `0.55520 > 0.50`：PASS。
- AP `0.72198 >= prevalence + 0.05`：PASS。
- AP interval lower `0.62384 > prevalence`：PASS。
- AUROC minus original U1 `0.26345 >= 0.05`，interval lower `0.13282 > 0`：PASS。
- 五个 fold AUROC 为 `0.59524 / 0.54667 / 0.71961 / 0.63617 / 0.72273`，5/5 高于 0.50 且全部不低于 0.45：PASS。
- Brier `0.26321` 高于 training-prevalence baseline `0.25338`：FAIL。

因此 combined panel 缺少晋级所需的两个联合条件。另一方面，各 panel 的 Task C AUROC 并非全部 `<=0.55`，不满足全 panel stop rule。冻结规则不允许选择表现较好的分层、修改阈值或增加模型以改变结论。

## 预算区域审计

Task C combined panel 的原插入集合包含 154 个 gain/harm candidates，AUROC `0.67417 [0.57724, 0.76521]`、AP `0.79074`；预算外区域包含 59 个，AUROC `0.50737 [0.31579, 0.68991]`、AP `0.45930`。登记的 `beyond_budget_driven_signal=false`，整体部分信号不是由预算外低排名候选驱动。

该分层是预冻结披露，不是新的 advancement route。原插入集合的较好点估计不能单独触发 `PROCEED`，也不能据此事后缩小 candidate universe。

## Provenance 与内容级验证

- zero-candidate query 合同修正提交：`080cc44781cddc7d25584812fee5dea2158142e9`。
- 当前运行协议提交：`b8bd1eafd51507e0d272a701219b7f7833c35704`。
- 两个提交中的 probe source Git blob 均为 `a1dc95ceeb819320ed938ae38bc6dbde61d80e59`；协议修订没有改变 probe 源码。
- 第一轮 shell timeout 只结束外层等待；Python 子进程继续完成两次冻结 probe、main/rerun 字节一致性检查、内部 independent verification 和三工件原子提升。
- 后续 no-timeout 进程同样完成 main/rerun 与内部验证，但 no-overwrite guard 在 promotion 阶段拒绝覆盖已有三工件；它没有修改现有工件。
- bounded provenance audit 在原地重建 probe 容器；`render_json(folds)`、`render_oof_csv(OOF)` 和 `render_json(metrics)` 与现有文件逐字节一致。
- 结构审计确认 fold 仅覆盖 2,446 个 candidate-bearing queries、fold 值为 0–4、OOF 唯一键/identity/region/label/Task-C 边界/概率范围和 68,588 行推导计数全部一致。
- 现有 `verify_probe_outputs()` 对重建容器返回 `STAGE4D_PROBE_VERIFIED`。
- 未重新拟合 OOF 模型；直接从冻结 probabilities 重算 overall/fold/region metrics、baselines、original U1 对照、paired AUROC difference、calibration 与 `beyond_budget_driven_signal`。
- 使用 seed `20260719`、原生 `query_id` cluster 和每区块 10,000 次迭代，精确重算 12 个 task-panel 的 overall/两 budget-region 共 36 个 bootstrap 区块；登记 interval、requested/valid samples 全部一致。
- 审计前后五项受保护工件 Bytes/SHA 完全相同；审计结束时没有 active probe process 或 Stage4D pending transaction。

由此建立：

```text
EXISTING_OFFICIAL_PROBE_ARTIFACTS_PROVENANCE_VERIFIED
STAGE4D_PROBE_VERIFIED
```

## 统计解释与证据等级

总体置信等级：`CAUTION`。

优点是 candidate universe、标签、fold、features、四个 panels、模型、seed、10,000 次 query-cluster bootstrap 和 decision gates 均在结果前冻结；main/rerun 同字节，独立 verifier 和事后 bounded content audit 均通过。限制是全部结果仍来自同一 development，Task C 只有 113/100 candidates 和 113/45 query clusters，最低 feasibility threshold 不是正式 power guarantee；四 panel 的探索性结果没有外部验证，也没有为多重比较提供确认性校正。

### 11 类统计谬误扫描

覆盖：`11/11 checked`。

| 谬误 | 严重度 | 本阶段判断 |
|---|---|---|
| Simpson's paradox | CAUTION | 原插入集合与预算外区域的 Task C 表现差异明显；已分层全量报告，未把分层点估计转成新规则。 |
| Ecological fallacy | NOTE | attribution 与预测单位是 candidate，bootstrap/fold cluster 是 query；没有把 query 均值误作候选因果效应。 |
| Berkson's paradox | CAUTION | Task C 条件化于 gain/harm event candidates，可能改变特征相关结构；结论限于该冻结任务。 |
| Collider bias | CAUTION | 对 standardized CR 变化的条件化可能形成选择碰撞；不把 OOF 关联解释为因果机制。 |
| Base rate neglect | CAUTION | Task A/B 极低 prevalence；已同时报告 AP、Brier、calibration 和 confusion，未用高 AUROC 代替部署价值。 |
| Regression to the mean | NOTE | 没有按极端预测值选择后再重测；同一冻结 OOF 只用于预注册门判定。 |
| Survivorship bias | NOTE | 完整 8,467 eligible candidate universe 和两个 budget regions 均保留；零候选 queries 只不进入 candidate-fold 表，不被伪造为候选。 |
| Look-elsewhere effect | CAUTION | 四 panel 全量报告，只有 combined panel 可晋级；没有选择最优 panel 触发结论。 |
| Garden of forking paths | NOTE | labels、tasks、panels、model、threshold 和 decision rule 在 official 结果前冻结；没有结果后改道。 |
| Correlation != causation | CAUTION | OOF 可分性表明预测关联，不证明某个 feature 导致 gain 或 harm。 |
| Reverse causality | NOTE | deployable features 在 Gold label 前可得，但 counterfactual label 是后验定义；报告不声称时间因果方向。 |

## 可复现性

- 固定环境：CPython `3.12.0`、NumPy `2.5.1`、SciPy `1.18.0`、scikit-learn `1.9.0`、joblib `1.5.3`、threadpoolctl `3.6.0`、narwhals `2.24.0`。
- `PYTHONHASHSEED=0`，BLAS/OpenMP 相关六个线程变量均为 `1`。
- official transaction 的 main/rerun 三工件同字节，并在 promotion 前完成内部独立验证。
- bounded provenance audit 不生成新 probe、不覆盖旧工件、不调用 `run_official_probe_transaction()` 或 `run_synthetic_probe()`，只从现有 OOF probabilities 复算内容。
- ARS reproducibility verdict：`VERIFIED`。

## 限制与下一步边界

1. Combined Task C 接近但未达到冻结 AUROC 门，且 Brier 未胜 prevalence baseline；不能把“部分信号”表述为 controller 已可部署。
2. Original-insert-set 分层表现优于 beyond-budget，但分层不能单独触发 advancement，也不能据此事后重定义候选池。
3. Gain-vs-all/harm-vs-all 的高 AUROC 不回答 gain-vs-harm 的符号选择问题。
4. 本阶段没有外部或 reservation 验证，不能推断跨数据集泛化。
5. `CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE` 不授权 U2；任何新 controller、feature、model 或 threshold 都是新的科学语义，必须另建 Level A development 协议。

```text
Stage4B-U1-D remains a valid negative result.
Reservation and Stage3B remain locked.
U2 remains not authorized.
No candidate controller efficacy has been established.
```
