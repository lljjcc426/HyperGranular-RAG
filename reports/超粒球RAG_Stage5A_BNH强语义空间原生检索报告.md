# 超粒球 RAG Stage5A-BNH 强语义空间原生检索报告

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run + validate
- Origin Date: 2026-07-25
- Verification Status: VERIFIED
- Version Label: stage5a_bnh_report_v1

## 结论

Stage5A-BNH 已完成冻结的 BGE-native Gold-free 几何可行性、独立 development、唯一配置冻结、独立 confirmation、正式生成、Gold evaluation、10,000 次 paired bootstrap、机制与效率审计及最终独立验证。

最终状态为：

```text
STAGE5A_BGE_NATIVE_GEOMETRY_FEASIBILITY_PASS
STAGE5A_DEVELOPMENT_UNIQUE_CONFIGURATION_FROZEN
BGE_NATIVE_HGRAG_INCONCLUSIVE
BGE_NATIVE_PROTECTED_PLACEMENT_INCONCLUSIVE
BGE_NATIVE_FACET_INCREMENT_INCONCLUSIVE
STAGE5A_FINAL_INDEPENDENT_VERIFICATION_PASS
```

在冻结的 BGE-large-en-v1.5、Qwen2.5-1.5B-Instruct、closed-candidate Top-20 和 HotpotQA/MuSiQue confirmation 边界上，Protected 相对 BGE 的两个数据集 answer-F1 点估计均略为负，置信区间均跨 0；因此既不满足支持门，也不满足负向门。Stage5A 没有建立 BGE-native HGRAG 相对 BGE Top-20 的可确认增量价值。

按照预登记停止规则，不继续 BGE-native 参数搜索，不自动进入 Stage5B-MSB、full-wiki、新生成器或第二个 strong retriever。Stage5-PMC 首轮基线及 Stage4E–Stage4I 的既有证据保持不变。

## 1. 冻结边界

| 项目 | 冻结值 |
|---|---|
| Retriever | `BAAI/bge-large-en-v1.5` @ `d4aa6901d3a41ba39fb536a557fa166f842b0e09` |
| Generator | `Qwen/Qwen2.5-1.5B-Instruct` @ `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` |
| Development | HotpotQA 500 + MuSiQue 750 |
| Confirmation | HotpotQA 1,000 + MuSiQue 1,500 |
| Top-k / protected prefix | 20 / 10 |
| Confirmation arms | BGE、Protected、Unprotected、NoFacet |
| Primary endpoint | paired answer F1 |
| Joint estimand | dataset-equal-weight |
| Bootstrap | 10,000，PCG64 seed `20260727` |

输入审计确认：

- development 与 confirmation query ID 重叠为 0；
- 与历史正式边界重叠为 0；
- ID 选择未使用 Gold 或 metadata；
- Blind Channel 不含 Gold 字段；
- Stage4E–Stage5-PMC 冻结清单中的 161 个文件在最终验证时均未变化。

## 2. Stage5A-0 Gold-free 几何可行性

预登记 16 个尺度无关候选配置中，`C01`、`C02`、`C09`、`C10` 通过最低几何门，同时覆盖 leaf size 4 和 6。

| 配置 | HotpotQA insertable rate | MuSiQue insertable rate | Combined |
|---|---:|---:|---:|
| C01 | 0.1280 | 0.2907 | 0.2256 |
| C02 | 0.1280 | 0.2907 | 0.2256 |
| C09 | 0.1020 | 0.2867 | 0.2128 |
| C10 | 0.1020 | 0.2867 | 0.2128 |

Development BGE embedding cache 为 330,797,652 bytes，SHA-256 为
`BD4423C6397839086F13FE99D86B71643E54D9913FCC6ABB6BB9E545D7992244`。加载或构建耗时 231.994 秒，检索构建耗时 21.791 秒。

该 PASS 只说明 blind-only 的几何定义可执行、非系统性退化并满足最低激活门；它不是答案质量证据，也不是功效充分性保证。

## 3. Development 与唯一配置

四个 selection-eligible 配置的 dataset-equal-weight 结果为：

| 配置 | Δ answer F1 | Δ answer EM | 平均增量输入 tokens |
|---|---:|---:|---:|
| C01 | +0.002494 | +0.001667 | -1.420 |
| C02 | +0.005032 | +0.004000 | -0.508 |
| C09 | +0.002443 | +0.001000 | -1.285 |
| C10 | +0.003143 | +0.002000 | -1.127 |

最佳 F1 为 C02。根据冻结规则，处于最佳值 0.002 范围内的配置继续按更低平均增量输入 token 等层级选择，最终唯一冻结：

```text
C10
facet_gate = BROAD
insert_budget = 4
leaf_size = 6
unit_score_percentile = 0.50
```

Development 只用于配置选择。其正向点估计不能与 confirmation 合并，也不能作为 confirmation 支持证据。

## 4. Confirmation 绝对结果

### HotpotQA（n = 1,000）

| 方法 | Answer F1 | Answer EM | CR@20 | ER@20 | Input tokens |
|---|---:|---:|---:|---:|---:|
| BGE | 0.513521 | 0.430000 | 0.938000 | 0.976100 | 931.196 |
| Protected | 0.510613 | 0.426000 | 0.940000 | 0.976433 | 931.338 |
| Unprotected | 0.506550 | 0.425000 | 0.940000 | 0.976433 | 931.338 |
| NoFacet | 0.510447 | 0.426000 | 0.939000 | 0.976350 | 931.508 |

### MuSiQue（n = 1,500）

| 方法 | Answer F1 | Answer EM | CR@20 | ER@20 | Input tokens |
|---|---:|---:|---:|---:|---:|
| BGE | 0.177856 | 0.140000 | 0.785333 | 0.909667 | 911.295 |
| Protected | 0.174672 | 0.136667 | 0.784667 | 0.909333 | 910.895 |
| Unprotected | 0.172002 | 0.134000 | 0.784667 | 0.909333 | 910.895 |
| NoFacet | 0.173577 | 0.132667 | 0.780000 | 0.907111 | 908.639 |

## 5. 冻结统计判定

### 5.1 核心：Protected − BGE

| 层级 | Δ answer F1 | 95% CI |
|---|---:|---:|
| HotpotQA | -0.002907 | [-0.008682, 0.002652] |
| MuSiQue | -0.003184 | [-0.008486, 0.001863] |
| Dataset-equal-weight | -0.003046 | [-0.006880, 0.000631] |

Dataset-equal-weight answer-EM delta 为 -0.003667，95% CI 为
[-0.007667, 0.000004]。

两个数据集的 F1 点估计方向一致但略为负，区间均跨 0；equal-weight F1 和 EM 也均未越过预登记负向门。因此核心状态为：

```text
BGE_NATIVE_HGRAG_INCONCLUSIVE
```

### 5.2 Protected placement

Protected − Unprotected 的 dataset-equal-weight answer-F1 delta 为
+0.003367，95% CI 为 [-0.001285, 0.008026]；answer-EM delta 为
+0.001833，95% CI 为 [-0.003167, 0.006833]。

```text
BGE_NATIVE_PROTECTED_PLACEMENT_INCONCLUSIVE
```

点估计倾向 protected，但区间跨 0，不能写成独立支持。

### 5.3 Facet increment

Protected − NoFacet 的 dataset-equal-weight answer-F1 delta 为
+0.000631，95% CI 为 [-0.004220, 0.005365]；answer-EM delta 为
+0.002000，95% CI 为 [-0.002833, 0.006833]。

```text
BGE_NATIVE_FACET_INCREMENT_INCONCLUSIVE
```

该结果不改变 Stage4H 在不同冻结系统边界中的 facet 正向证据，也不能把 Stage4H 的结论外推到本次 BGE-native 系统。

## 6. Gold 后机制审计

Protected 的 added / displaced / net Gold 为：

| 数据集 | Added Gold | Displaced BGE Gold | Net Gold |
|---|---:|---:|---:|
| HotpotQA | 3 | 2 | +1 |
| MuSiQue | 16 | 15 | +1 |

净 Gold 略为正，但 answer-F1 没有获得可确认增益。这说明插入证据的数量变化不能替代端到端答案质量判定。该机制审计发生在核心 decision 冻结后，只作描述，不用于重新调参或选择配置。

## 7. 效率与成本

| 项目 | 结果 |
|---|---:|
| Confirmation embedding cache | 670,420,228 bytes |
| Cache SHA-256 | `DC09AEEE113F702BC0F5800ACE5369C8C80905F8C991203DAB27D12982477325` |
| Retrieval reconstruction | 8.544 秒 |
| BGE generation | 887.650 秒 |
| Protected generation | 884.198 秒 |
| Unprotected generation | 888.282 秒 |
| NoFacet generation | 886.058 秒 |
| GPU peak memory | 3,856,969,216 bytes |
| Failed calls | 0 |

Protected 的生成时间没有增加，但核心效果点估计为负且不确定，不能据此定义正向“每单位 F1 增益成本”。

## 8. 确定性、独立验证与统计完整性

- Confirmation main 覆盖 2,500 queries × 4 arms，共 10,000 次生成调用；
- 预哈希 subset 覆盖 200 queries × 4 arms，共 800 次独立复跑；
- subset prediction 与 prompt 均逐字节一致；
- BGE baseline、BGE-native balls、ECDF、facet、eligibility、四臂 placement、prompt、F1/EM、10,000 次 bootstrap、decision、Gold transition 和效率摘要均由独立 verifier 重建；
- 最终返回 `STAGE5A_FINAL_INDEPENDENT_VERIFICATION_PASS`；
- 161 个既有冻结文件均与 Stage5A 前基线一致。

统计谬误检查覆盖 11/11：

- Simpson、生态谬误、Berkson、collider：主要 estimand 预先按数据集等权定义，且两个数据集分别报告；未用结果驱动筛样或协变量控制；
- base-rate neglect、regression-to-mean、survivorship：不适用于本次配对固定 query 评价，且无完成样本丢失；
- look-elsewhere、forking paths：16 个 development 配置及唯一选择层级在 Gold 前冻结，confirmation 未重调；
- correlation-causation、reverse causality：报告只陈述冻结系统在指定边界中的配对性能差异，不作观察性因果外推。

总体统计信心标记为 `CAUTION`：完整性和可重复性通过，但核心区间跨 0，证据结论是不确定而非支持。

## 9. 工程异常与最小修复

Development 初次长进程运行出现 CUDA/cache 长时进程性能退化。诊断确认同一 4,052-token 调用在新进程中恢复正常，未发现数据、模型、ranking、prompt 或 Gold 边界异常。处理为：

1. 保留未完成事务到 `temp/stage5a_bnh_interrupted_timing_incomplete_20260725/`；
2. 修正 checkpoint 恢复后的生成耗时聚合；
3. 增加不改变任务顺序或输出的 `process_call_limit=2000`，在进程边界释放 CUDA cache；
4. 重新执行正式事务，并确认新旧已完成 predictions/prompts 字节一致；
5. 通过定向测试、Stage5A 完整测试和最终独立重建。

该异常属于运行时性能与 telemetry 完整性问题，没有改变科学语义、样本、模型、配置、预测或统计判定。中断目录和诊断脚本位于 `.gitignore` 覆盖的 `temp/`，不作为科研工件提交。

## 10. 正式结果身份

| 工件 | Bytes | SHA-256 |
|---|---:|---|
| `stage5a_bnh_confirmation_query_audit.jsonl` | 4,375,509 | `A8AB7176504AB8C84466F69AC80873C8D5CD62C93B25B15B76DE65C7374FEDBD` |
| `stage5a_bnh_confirmation_dataset_summaries.json` | 2,649 | `F4893C526AC45C5622A93B44BDCFAA50A484C896F4F7984AF0E4150F79763546` |
| `stage5a_bnh_confirmation_equal_weight_summary.json` | 6,165 | `D38608EB73FF1A7741A6EBE2DE2E08B0F7FC7D0305067F6FE7D60F8B8C83983F` |
| `stage5a_bnh_confirmation_mechanism_audit.json` | 3,595 | `0AEEA7C41680E10A417E036CD1C6DC2D86BF60BAAD337218AE07F6DE697027F1` |
| `stage5a_bnh_confirmation_efficiency_summary.json` | 757 | `A79140BC374A12F9EF887DFEEA32042F45E6FEDC3E31A1072B445194BACCE1D8` |
| `stage5a_bnh_scientific_decision.json` | 477 | `9C453E0FB2CE8BF3224DD949B620DA1C17567C7AC8A5A7CF5CC109DA978459A0` |
| `stage5a_bnh_final_verification.json` | 386 | `145B51FB194BA0DE5B00D294FE4D8F8EAC9FD9D2E7C1F39F741D7AFEDDF0BA09` |

完整 Stage5A 工件及外部 cache/channel 的 Bytes/SHA 见
`results/stage5a_bnh_artifact_manifest.json`。

## 11. 论文主张边界与后续路线

可以写：

> 在一个预指定的 BGE strong-dense backbone、两个新 ID-only confirmation 边界、固定 Qwen 生成合同和 closed-candidate Top-20 预算下，BGE-native HyperGranular retrieval 的增量 answer-F1 证据不确定；两个数据集点估计均略为负，置信区间跨 0。

不能写：

- BGE-native HGRAG 已优于 BGE strong dense；
- BGE-native HGRAG 已被证明无效或等价；
- HyperGranular-RAG 整体无效；
- facet 或 protected placement 在所有检索空间中无效；
- full-wiki、开放域、其他 strong retriever 或其他生成器会得到相同结果。

阶段路线冻结为：

```text
STAGE5A_BNH_COMPLETE_AND_FROZEN
BGE_NATIVE_HGRAG_INCONCLUSIVE
AUTOMATIC_BGE_NATIVE_PARAMETER_SEARCH_STOPPED
STAGE5B_MSB_NOT_STARTED
FULL_WIKI_NOT_AUTHORIZED
STAGE5_PMC_FIRST_ROUND_BASELINE_PRESERVED
RESERVATION_LOCKED
STAGE3B_LOCKED
U2_NOT_AUTHORIZED
```
