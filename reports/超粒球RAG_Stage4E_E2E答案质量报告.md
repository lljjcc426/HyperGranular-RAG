# Stage4E-E2E 静态 HyperGranular-RAG 答案质量报告

日期：2026-07-22  
状态：`STAGE4E_FINAL_VERIFICATION_PASS`  
冻结决策：`STATIC_HGRAG_E2E_SUPPORTED`

## 1. 科学问题与边界

Stage4E 在 HotpotQA train distractor 的确定性 new-ID same-domain 1,000-query 边界上，比较相同 encoder、相同 Qwen2.5-1.5B-Instruct 生成器、相同 prompt 与 4,096-token 上限下的：

- `DENSE_TOP20`；
- 不含 U1、Stage4D model 或任何 learned controller 的 `STATIC_Q25_TOP20`。

主终点是在 query 级成对计算的 answer F1 差：

```text
delta_answer_f1 = mean(F1_STATIC_Q25 - F1_DENSE)
```

本阶段是同域、closed distractor candidate pool 的静态检索臂比较，不是 full-wiki、跨数据集或生成器未污染验证。公开 HotpotQA train 可能进入过生成器预训练语料，因此结果只能按冻结边界解释。

## 2. 完整性与执行

- source：566,426,227 bytes，SHA-256 `26650CF50234EF5FB2E664ED70BBECDFD87815E6BFFC257E068EFEA5CF7CD316`；
- 样本：`SHA256("stage4e_e2e_v1\0" + _id)` 排序前 1,000，历史 HotpotQA query ID 重叠为 0；
- generator：`Qwen/Qwen2.5-1.5B-Instruct@989aa7980e4cf806f80c7fef2b1adb7bc71aa306`；
- runtime：CPython 3.12.0、PyTorch 2.12.1+cu130、CUDA 13.0、Transformers 5.14.1、safetensors 0.8.0；
- Gold-free main/rerun 各 2,000 次 generate calls，均为 0 failed calls；
- predictions main/rerun：419,866 bytes，SHA-256 均为 `FE9D6716BBB2D83DD3407CB5A042CB9F888912256C478FA501DE9F5457945D58`；
- prompt audit main/rerun：3,337,447 bytes，SHA-256 均为 `130B78B896EDDBF0250E60736B223029163C30BBA6A492C6D4978D57E2556055`；
- independent pre-Gold verifier 返回 `STAGE4E_PRE_GOLD_ARTIFACTS_VERIFIED` 后才读取 Gold；
- independent post-Gold verifier 独立重算答案指标、retrieval 指标、bootstrap 和决策，返回 `STAGE4E_FINAL_VERIFICATION_PASS`。

运行资源仅作复现记录：main/rerun 生成 wall time 分别为 854.833 秒与 767.337 秒；GPU peak memory 分别为 3,509,613,568 与 3,508,564,992 bytes。

## 3. 主结果

| 指标 | Dense Top-20 | Static q25 Top-20 | q25 - Dense |
|---|---:|---:|---:|
| Answer F1 | 0.421498 | **0.436278** | **+0.014780** |
| Answer EM | 0.356000 | **0.366000** | **+0.010000** |
| Retrieval CR@20 | 0.737000 | **0.798000** | **+0.061000** |
| Retrieval ER@20 | 0.878600 | **0.908183** | **+0.029583** |
| UNKNOWN rate | 0.354000 | **0.331000** | -0.023000 |

10,000 次 query-paired percentile bootstrap（seed `20260720`）：

- `delta_answer_f1 = +0.014780`，95% interval `[+0.000203, +0.029883]`；
- `delta_answer_em = +0.010000`，95% interval `[-0.005000, +0.025000]`。

冻结 positive gate 要求：F1 点估计至少 +0.010、F1 interval lower 严格大于 0、EM interval lower 至少 -0.010。本次三项均通过，故决策为 `STATIC_HGRAG_E2E_SUPPORTED`。

需要同时强调：F1 区间下界只略高于 0，支持结论成立但证据裕量有限，不应表述为大幅或普遍改善。

## 4. 查询级与运行审计

- answer F1：q25 gain 70 queries、harm 9 queries、same 921 queries；
- q25 实际平均插入 1.93 个单位；插入数 0/1/2/3/4 的 query 数为 358/89/125/121/307；
- 两臂平均实际 prompt evidence units 均为 19.939；
- Dense/q25 平均 input tokens 为 899.19/901.04，最大均为 1,576；
- 两臂 rank-1 truncation 均为 0。

这些审计表明本次答案差异不是由不同生成器、不同 token cap、失败 query 删除或 rank-1 截断造成。q25 的平均 token 数略高属于冻结插入排序产生的文本长度差异，不是额外放宽上下文上限。

## 5. 描述性 subgroup

以下仅为冻结后的 `SUBGROUP_CAUTION` 点估计，不含 confirmatory subgroup interval，也不得改变总决策：

| subgroup | n | Dense F1 | q25 F1 | q25 - Dense |
|---|---:|---:|---:|---:|
| bridge | 783 | 0.454657 | 0.475330 | +0.020673 |
| comparison | 217 | 0.301850 | 0.295364 | -0.006485 |
| easy | 209 | 0.501119 | 0.540228 | +0.039109 |
| hard | 172 | 0.401532 | 0.409626 | +0.008094 |
| medium | 619 | 0.400162 | 0.408585 | +0.008423 |

不能据这些点估计声称 q25 对 bridge/easy 有确认性异质收益，或对 comparison 有确认性伤害；它们只形成后续独立研究问题的候选线索。

## 6. 11 类谬误检查

1. 相关当因果：只主张冻结检索臂在同一生成器下的成对差异。
2. 小样本强结论：1,000 是冻结资源边界，不声称充分功效。
3. 多重比较：唯一主终点是总样本 answer F1；subgroup 不触发决策。
4. 不显著当相同：EM 区间跨 0，仅作为预定 non-inferiority guard。
5. 忽略效应量：同时报告绝对指标、点差和区间。
6. 基线不当：Dense 与 q25 共用 encoder、generator、prompt、K 和 token cap。
7. 数据泄漏：Gold 在 pre-Gold verifier 通过后才读取，未进入 ranking/prompt/generation。
8. 测试集调参：正式 1,000-query 边界未用于选择生成器、prompt、q25 参数或判定门。
9. 过度外推：限定 HotpotQA same-domain closed distractor，不写成跨域/full-wiki 结论。
10. 缺失值处理：2,000 calls 全部成功，没有 complete-case 删除或单臂补跑。
11. 选择性报告：保留总结果、secondary、subgroup、gain/harm/same、资源和全部验证工件。

## 7. 可写结论与限制

可写结论：在冻结 HotpotQA new-ID same-domain distractor 边界、Qwen2.5-1.5B-Instruct 和 Top-20 预算下，不带 controller 的静态 q25 protected insertion 相对 Dense Top-20 获得 +0.01478 answer F1，冻结 positive gate 与独立验证均通过。

不可写结论：

- q25 在所有问题类型、数据集、生成器或 full-wiki 环境普遍优于 Dense；
- Stage4B U1 controller 或 Stage4D candidate selector 获得支持；
- subgroup 点估计已经证明机制或异质性；
- 生成器未见过 HotpotQA；
- 当前结果授权 reservation、Stage3B、U2 或重开 controller 线。

Stage4E 已完成并冻结。任何跨数据集复制、full-wiki 验证、其他生成器复现或 subgroup/机制确认，均是新的科学问题，需要新的轻量实验卡和阶段授权。

