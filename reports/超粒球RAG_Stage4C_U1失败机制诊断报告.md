# Stage4C-U1-FMA：U1 Failure Mechanism Audit

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validate
- Origin Date: 2026-07-19
- Verification Status: ANALYZED
- Version Label: stage4c_u1_fma_validation_v1

## 结论

```text
MECHANISM_EVIDENCE_INCONCLUSIVE
```

Stage4C 找到了清楚但不足以晋级的机制证据：冻结 U1 raw score 对 GAIN-vs-HARM 的方向错误，AUROC 为 `0.39269`，95% bootstrap interval 为 `[0.30558, 0.48150]`；92/94 个 gain query 同时插入 Gold 与 non-Gold 单元，而全部 69 个 harm query 都属于 displacement harm，因此 query-level 全开/全关是可信的结构性限制。不过，三个固定 OOF panel 均未达到预先规定的稳定信号门，且冻结工件不含 candidate Gold identity/rank、candidate score 或支持/相似度特征，无法判断 candidate-level selector 是否可学。

因此，本阶段不支持启动正式 U2 development，也不支持停止 HyperGranular-RAG 整体方向。若未来继续 candidate-level 方向，必须先获得新的 Level A 协议与独立授权。

## 研究角色与不变边界

- 角色：post-Gold exploratory diagnosis，不是 confirmatory efficacy evaluation。
- 数据：同一批 4,500-query development；没有读取 reservation、Stage3B 或其他测试集。
- Gold 用途：只定义诊断标签和描述性 composition；没有进入 OOF feature matrix。
- 没有重跑 Stage4B controller、Gold evaluator 或 deterministic Gold rerun。
- 没有修改 U1-D 特征、公式、预算、threshold、ranking 或既有结果。
- Stage4B 决策保持 `STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED`。

协议提交为 `2e925063175a6402a21ade3fc0ab4a27faaa6dd7`；实现提交为 `1bbe8a571d4e0c4aa965b4f0fa71b1de5901b2a7`。两者都在首次诊断运行前推送至 GitHub main。

## 冻结输入

| 输入 | Bytes | SHA-256 |
|---|---:|---|
| decisions | 2,684,439 | `4B2AD2E5707B20FD46B6250FDA5395433F52E55FB1281F1499412C8C749A456A` |
| rankings | 18,235,604 | `ED289D234F6F4FEC58A48168CB6CA78950489CD5F5640E977068CA6A786E03CB` |
| policy | 261,587 | `657E5F25A94224D8B020780F3E7335942B16BC6D8C7939FB74D1BBAA9A9D868B` |
| VERIFIED_PRE_GOLD | 3,479 | `39EAD86A3A835983DCB67BAF656255F51569BCEE5B9AC2E16FACF404281D7818` |
| query audit | 2,600,121 | `8616C28C71D190E3287CCE3725EDC0B1FD0DFB41DF47C739F4A84A573F938313` |
| evaluation summary | 7,662 | `7F82056FB14F9D8D73E668A82CB5304B28385E62A01C428599F23260AB7F89DE` |
| VERIFIED_POST_GOLD | 2,293 | `44BF3E8B0B036958633E237186A458B13090D8073F587657D831656FB7720ECD` |

正式运行再次核对了七个工作文件的长度、SHA、Git tracked 状态和 summary 内部聚合。运行后七个 SHA 保持不变。

## 执行与输出完整性

正式命令：

```powershell
& 'D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe' -B scripts/stage4c_u1_failure_mechanism_audit.py --output-dir results
```

- 工作目录：`E:\科研\HyperGranular-RAG`
- 运行时间：2026-07-19 00:11:26 至 00:21:25（约 599 秒）
- terminal marker：`STAGE4C_U1_FMA_PASS queries=4500 decision=MECHANISM_EVIDENCE_INCONCLUSIVE`
- stderr：0 bytes
- 监控期间 CPU 持续增长，RSS 约 66–70 MiB；无 crash、stall 或资源异常。
- 六个工件在结束时由 pending area 一次性提升；没有部分正式输出。

| 输出 | Rows | Bytes | SHA-256 |
|---|---:|---:|---|
| `stage4c_u1_fma_query_features.csv` | 4,500 | 1,205,296 | `311D4AE15F80A14A5C3BEBE427E894E445C76F17045709CE62E15F89A138E142` |
| `stage4c_u1_fma_feature_separability.csv` | 48 | 10,057 | `BE1FA4F74BE8A059E7DB92326BD22084D5817901F106D2B367F2249B1F2C8CE9` |
| `stage4c_u1_fma_score_deciles.csv` | 10 | 1,813 | `04CE6F940473439C6CBA8D52CF518602D3725B4561E5711F437519E042056180` |
| `stage4c_u1_fma_candidate_mechanisms.csv` | 4,500 | 772,763 | `FA5C378F6A8E69CAC52859D49918912B6822F0F97C29BB63C0ADCD1D655A23EF` |
| `stage4c_u1_fma_oof_predictions.csv` | 27,489 | 3,671,149 | `BEE06C3FBE69FED3D30C0C33126F37E218268BEC9C327DA0BE1C2B654AE09866` |
| `stage4c_u1_fma_summary.json` | — | 108,940 | `7B6D8C8B85EC32D596250137CC676B4C732C964C64714F7EF5EE6B3E86E7B0C6` |

只读独立检查确认：CSV schema/行数正确，LF/UTF-8 合同成立，query ID 与 OOF `(task, panel, query_id)` 均唯一，概率均有限且位于 `[0,1]`，summary 内五个 CSV SHA 与实际文件一致，JSON 没有非有限数值。

## 标签重建与 Stage4B 对账

| 项目 | 复核值 |
|---|---:|
| Queries | 4,500 |
| GAIN | 94 |
| HARM | 69 |
| NEUTRAL | 4,337 |
| Retained GAIN | 47 |
| Retained HARM | 53 |

该对账与冻结 Gold summary 完全一致。Stage4B 的有效负结果没有被重解释或覆盖。

## 原 U1 特征的 GAIN-vs-HARM 可分性

正类为 GAIN；AUROC 不翻转方向。Task-A GAIN prevalence 为 `94/163=0.57669`。

| Feature | AUROC | 95% interval | AP | 方向 |
|---|---:|---|---:|---|
| ball_score_margin | 0.60947 | [0.51881, 0.69658] | 0.65763 | GAIN_HIGH |
| boundary_margin | 0.43278 | [0.34489, 0.52128] | 0.54418 | HARM_HIGH |
| selected_edge_count | 0.40225 | [0.33989, 0.46508] | 0.53428 | HARM_HIGH |
| planned_insert_count | 0.48821 | [0.41883, 0.56005] | 0.57249 | HARM_HIGH |
| u_margin | 0.39053 | [0.30496, 0.47965] | 0.51011 | HARM_HIGH |
| u_boundary | 0.56722 | [0.47857, 0.65588] | 0.65651 | GAIN_HIGH |
| r_edge | 0.40225 | [0.34135, 0.46701] | 0.53428 | HARM_HIGH |
| r_candidate | 0.48821 | [0.41883, 0.55920] | 0.57249 | HARM_HIGH |
| uncertainty | 0.47695 | [0.38883, 0.56692] | 0.58652 | HARM_HIGH |
| readiness | 0.42908 | [0.35422, 0.50655] | 0.54527 | HARM_HIGH |
| score | 0.39269 | [0.30558, 0.48150] | 0.55398 | HARM_HIGH |
| ordered_rank | 0.60731 | [0.51835, 0.69458] | 0.68724 | GAIN_HIGH |

最直接的失败机制是：高 raw U1 score 更倾向于 HARM，而不是 GAIN。ball margin 与最终 ordered rank 有中等偏弱的 gain-high 方向，但其信号没有被 U1 乘法 score 保存下来。

## 排序方向与十等分审计

可行 queries 为 2,446。冻结模式判定为 `D_LOCALIZED_OR_IRREGULAR_SIGNAL`。

| Decile | GAIN | HARM | 累计 GAIN retention | 累计 HARM retention | 累计 gap |
|---:|---:|---:|---:|---:|---:|
| 1 | 14 | 11 | 0.14894 | 0.15942 | -0.01048 |
| 2 | 15 | 11 | 0.30851 | 0.31884 | -0.01033 |
| 3 | 4 | 17 | 0.35106 | 0.56522 | -0.21415 |
| 4 | 6 | 8 | 0.41489 | 0.68116 | -0.26627 |
| 5 | 10 | 7 | 0.52128 | 0.78261 | -0.26133 |
| 6 | 11 | 3 | 0.63830 | 0.82609 | -0.18779 |
| 7 | 16 | 5 | 0.80851 | 0.89855 | -0.09004 |
| 8 | 7 | 5 | 0.88298 | 0.97101 | -0.08804 |
| 9 | 8 | 1 | 0.96809 | 0.98551 | -0.01742 |
| 10 | 3 | 1 | 1.00000 | 1.00000 | 0.00000 |

前两个高分 decile 没有正 retention gap，第三 decile 出现 4 GAIN / 17 HARM，之后才出现局部 gain-rich 区域。decile index 与 `(gain_rate-harm_rate)` 的 Spearman 为 `0.18788`，不支持单调的“分数越高、收益越大”。冻结实际预算覆盖 decile 1–4 和 decile 5 的 216 个 query；没有据结果挑选新阈值。

## uncertainty/readiness 分解

- `uncertainty` AUROC：`0.47695`。
- `readiness` AUROC：`0.42908`，但上界 `0.50655`；因此冻结旗标 `READINESS_PUSHES_HARM_HIGH=false`。
- `score` AUROC：`0.39269`。
- `score AUROC - uncertainty AUROC` 的 paired bootstrap interval：`[-0.16482, -0.00709]`，说明乘法后的 score 可分性低于 uncertainty；但 readiness 的 harm-high 前置条件未通过，所以冻结复合旗标 `MULTIPLICATION_AMPLIFIES_WRONG_DIRECTION=false`。
- planned insert count 与 q25 inserted count 的 Spearman 为 `1.0`，其 AUROC interval 包含 0.5；`EXPANSION_SCALE_NOT_BENEFIT_SIGNAL=true`。
- selected-edge count 与 q25 inserted count 的 Spearman 为 `0.84029`，但其 AUROC interval 完全低于 0.5；冻结的“仅规模、无收益”旗标为 false，因为它表现为 harm-high，而不是无方向。

这些结果只诊断冻结公式，不能据此修改 U1 公式或重跑同一 development。

## 全开/全关机制

| 类别 | Queries |
|---|---:|
| DISPLACEMENT_HARM_QUERY | 69 |
| MIXED_GAIN_NOISE_QUERY | 92 |
| PURE_GAIN_QUERY | 2 |
| PURE_NOISE_QUERY | 1,862 |
| NO_EFFECT_QUERY | 2,475 |

`MIXED_GAIN_NOISE_QUERY + DISPLACEMENT_HARM_QUERY = 161/163` 个 gain/harm events，且两类都超过冻结下限，因此 `ALL_ON_OFF_LIMITATION_EVIDENCE=true`。这说明 query-level 开关会把同一 query 中的潜在有益候选与噪声一起打开，或造成 displacement harm。它支持“candidate-level 是更合理的后续假设单位”，但不证明 candidate-level selector 可实现或有效。

冻结工件没有 candidate Gold identity/rank、candidate numeric score、support count、similarity、facet/hyperedge 或 displaced-unit feature。所有这些字段均记录为 `NOT_AVAILABLE_IN_FROZEN_ALLOWED_ARTIFACTS`，没有从 Gold map、corpus 或 cache 回填。

## 固定 OOF learnability probes

### Task A：GAIN vs HARM

| Panel | OOF AUROC | 95% interval | AP | 95% interval | Folds AUROC > 0.5 | Stable |
|---|---:|---|---:|---|---:|---|
| ORIGINAL_U1_8 | 0.60762 | [0.52189, 0.69735] | 0.65560 | [0.58862, 0.74555] | 5/5 | false |
| RANK_STRUCTURE_6 | 0.54001 | [0.44742, 0.63252] | 0.58283 | [0.52874, 0.66528] | 4/5 | false |
| COMBINED_14 | 0.61810 | [0.52744, 0.70537] | 0.65008 | [0.58249, 0.73763] | 5/5 | false |

ORIGINAL 和 COMBINED 存在部分 OOF 信号，但 AUROC 都低于冻结的 `0.65` 稳定门；RANK_STRUCTURE interval 包含 0.5。各 question type 的 Task-A AUROC 也不一致，例如 ORIGINAL 的 comparison 为 `0.46237`、compositional 为 `0.69398`。这些差异只作异质性警示，不用于类型特定规则。

### Task B/C：事件 vs 非事件

| Task | Panel | AUROC | AP | Prevalence |
|---|---|---:|---:|---:|
| GAIN vs non-GAIN | COMBINED_14 | 0.90681 | 0.12915 | 0.02089 |
| HARM vs non-HARM | RANK_STRUCTURE_6 | 0.88054 | 0.06989 | 0.01533 |

Task B/C 显示扩展事件与大量 neutral query 在结构上可区分，但这不能解决 gain 与 harm 的符号选择问题。低 prevalence 下必须同时看 AP；这些结果不构成 controller efficacy。

## 决策复核

- `stable_panels=[]`：没有 panel 达到全部稳定门。
- `weak_panels=[]`：ORIGINAL/COMBINED 又不是完全接近随机的弱信号。
- `ALL_ON_OFF_LIMITATION_EVIDENCE=true`。
- 所有预设 feature coverage 足够。

数据处于“部分但未达稳定门的信号 + 明确结构限制”的剩余情形，因此按冻结优先级只能是：

```text
MECHANISM_EVIDENCE_INCONCLUSIVE
```

## 统计解释与证据等级

总体置信等级：`CAUTION`。

理由：分析在结果前冻结并完整报告，bootstrap 与 OOF 均按 query 进行；但它仍是同一 development 上的 post-Gold 探索性诊断，含 12 个单变量审计和 9 个固定 probe，没有多重比较校正，Task-A 事件只有 94/69，candidate-level 关键字段缺失。区间用于描述精度和冻结门判定，不应转写为确认性机制证明。

### 11 类统计谬误扫描

覆盖：`11/11 checked`。

| 谬误 | 严重度 | 本阶段判断 |
|---|---|---|
| Simpson's paradox | CAUTION | question type 间 AUROC 方向/幅度不一致；未确认整体与所有子组反转，禁止据单一类型形成规则。 |
| Ecological fallacy | NOTE | 分析和推断单位均为 query；candidate-level 结论被明确限制为未来假设。 |
| Berkson's paradox | CAUTION | Task A 条件化于 163 个 q25 gain/harm events，事件子集选择可能改变特征相关结构。 |
| Collider bias | CAUTION | 对 q25 event 的条件化可能形成选择碰撞；因此所有关联仅作诊断，不作因果解释。 |
| Base rate neglect | CAUTION | Task B/C prevalence 仅 2.09%/1.53%；已同时报告 AP、Brier 和 calibration，不能只看高 AUROC。 |
| Regression to the mean | NOTE | 不是按极端值选择后的 pre/post 重测设计；未见该问题。 |
| Survivorship bias | NOTE | 4,500 queries 全部进入 Task B/C，GAIN/HARM 全部进入 Task A；无 attrition。 |
| Look-elsewhere effect | CAUTION | 多项特征/模型指标未做 multiplicity correction；通过预冻结、全量报告和不选最佳 panel 限制风险。 |
| Garden of forking paths | NOTE | 协议和决策门在首次运行前提交；仍是 post-Gold 研究问题，所以保持 exploratory 标签。 |
| Correlation != causation | CAUTION | score、scale 和 harm 的关系是观察性关联，不能表述为这些特征“导致”伤害。 |
| Reverse causality | NOTE | 特征在检索决策时可用，但诊断标签来自后验 Gold；报告不声称时间因果方向。 |

## 可复现性

- 分类：确定性分析；固定代码、七输入、NumPy 版本、fold、seed、bootstrap 次数和序列化格式。
- 定向测试：16/16 PASS，包括 bootstrap/fold/OOF synthetic byte determinism、严格联结、防泄漏、决策规则和原子输出。
- 首个 dotted-module unittest 命令因 `tests/` 不是 package 而未加载测试；改用精确 `unittest discover` 后 16 个用例全部通过。该失败没有执行测试体或诊断脚本。
- 完整正式重跑：未执行。正式脚本按协议拒绝覆盖已有六工件，且本阶段不以重复运行制造治理负担。
- 完整结果的 ARS reproducibility verdict：`CANNOT_VERIFY`（未进行第二次正式运行）；计算完整性由固定种子、synthetic byte determinism、输出 SHA、自描述绑定与只读结构复核支持。

## 限制与下一步

1. 本阶段只能定位 query-level score 和 all-on/off 结构问题，不能识别具体应插入的 candidate。
2. Task-A OOF 信号低于稳定门，不能据此选择 panel、阈值或新 controller。
3. Task B/C 的高 AUROC 主要回答“事件 vs neutral”，不是“gain vs harm”。
4. question-type 只作审计，不进入模型或部署规则。
5. 不创建 U2 controller，也不创建 Stage5A/U2 Level A 草案；当前决策没有授权该步骤。
6. 若用户未来选择继续，需先设计新的 Level A candidate/path-level development 协议，并另行解决 candidate-level 无标签特征与目标身份的合法冻结问题。

```text
Stage4B-U1-D remains a valid negative result.
Reservation remains locked.
No new controller efficacy has been established.
```
