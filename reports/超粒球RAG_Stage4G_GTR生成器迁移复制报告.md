# HyperGranular-RAG Stage4G-GTR 生成器迁移复制报告

## Material Passport

- Origin Skill: academic-research-suite / academic-pipeline / experiment-agent
- Origin Mode: run + validate + report
- Origin Date: 2026-07-23
- Verification Status: VERIFIED
- Version Label: stage4g_gtr_result_v1
- Scientific Decision: `GENERATOR_TRANSFER_INCONCLUSIVE`

## 1. 科学问题与结论

Stage4G-GTR 只检验一个预注册问题：完全复用 Stage4E 与 Stage4F 的冻结 blind inputs、Dense/static-q25 rankings、prompt 语义和评分规则，把唯一新因素改为一个结果无关、事前绑定的第二生成器后，static-q25 相对 Dense 的 answer-F1 增益是否在 HotpotQA 与 MuSiQue 上保持同方向，并通过数据集等权联合判定门。

最终独立验证状态为 `STAGE4G_GTR_FINAL_VERIFICATION_PASS`，科学判定为：

```text
GENERATOR_TRANSFER_INCONCLUSIVE
```

HotpotQA 的 F1 点差为正，但区间跨 0；MuSiQue 的 F1 点差轻微为负，区间也跨 0。数据集等权 F1 点差为 `+0.00516396`，低于预注册的 `+0.010` 支持门，95% 区间也跨 0；与此同时，没有任何预注册负向门被触发。因此，当前结果既不支持“已在第二生成器上复制”，也不支持“迁移结果明确为负”。

可写结论是：

> Under one additional pre-specified generator configuration, the generator-transfer result was inconclusive.

不得写成该方法具有普遍 generator robustness，也不得把本阶段解释为 Gemma 与 Qwen 的纯架构比较。

## 2. 第二生成器与冻结边界

| 项目 | 冻结值 |
|---|---|
| model | `google/gemma-4-E2B-it-qat-mobile-transformers` |
| revision | `dd693ff40353f057ca5f07e945ad867f4afbf2ec` |
| runtime | Google official mobile-QAT Transformers snapshot |
| weight | 2,458,111,846 bytes；SHA-256 `EFAB429012B97AB986C4D4838A46FF3AD95D618B42CE514771CA40FADC76A9A4` |
| thinking | disabled |
| hardware | NVIDIA GeForce RTX 4060 Laptop GPU 8GB |
| prompt | 与 Stage4E/4F 相同的 evidence-only 最短答案语义合同 |
| decoding | 4,096-token cap；greedy；beams 1；max new tokens 32；batch 1 |
| HotpotQA | Stage4E 冻结 1,000-query blind inputs 与两臂 rankings |
| MuSiQue | Stage4F 冻结 3,000-query blind inputs 与两臂 rankings |

该生成器在读取任何 Stage4G Gold 前完成唯一绑定。选择依据是不同模型家族、固定 revision、可部署的官方 mobile-QAT 格式、当前 RTX 4060 Laptop 8GB 上的可运行性和无 Gold 工程资格，而不是 Stage4G 答案表现。

Gemma 4 E2B 在本阶段以官方 mobile-QAT 格式运行，模型架构、量化方式和数值格式的影响不可分离。Stage4E 的 generator-selection development 结果没有进入 Stage4G 的成功/失败判定。

## 3. 数据集级主要结果

| 数据集 | 指标 | Dense Top-20 | Static q25 Top-20 | q25 − Dense / 95% paired interval |
|---|---|---:|---:|---:|
| HotpotQA | Answer F1 | 0.34978145 | 0.36242892 | `+0.01264746 [-0.00219589, 0.02744367]` |
| HotpotQA | Answer EM | 0.30500000 | 0.31100000 | `+0.00600000 [-0.00900000, 0.02100000]` |
| MuSiQue | Answer F1 | 0.04476359 | 0.04244406 | `-0.00231954 [-0.00684890, 0.00207553]` |
| MuSiQue | Answer EM | 0.03333333 | 0.03200000 | `-0.00133333 [-0.00566667, 0.00300000]` |

统计单位为 query。每个数据集独立执行 10,000 次 paired query bootstrap，使用 NumPy PCG64、seed `20260724` 和 95% percentile interval。

## 4. 数据集等权联合结果

主要联合统计量对两个数据集等权：

| 指标 | 点估计 | 95% dataset-stratified interval |
|---|---:|---:|
| Equal-weight delta answer F1 | +0.00516396 | `[-0.00262300, 0.01295045]` |
| Equal-weight delta answer EM | +0.00233333 | `[-0.00566667, 0.01033333]` |

联合 bootstrap 在 HotpotQA 和 MuSiQue 内分别有放回抽样，再取两个数据集 delta 的等权平均；迭代 10,000 次，seed `20260724`。

作为描述性补充，按 4,000 queries 直接加权的结果为：

| 指标 | Query-weighted delta |
|---|---:|
| Answer F1 | +0.00142221 |
| Answer EM | +0.00050000 |

该描述量中 MuSiQue 权重为 75%，不进入主判定。

## 5. 预注册判定门

`GENERATOR_TRANSFER_SUPPORTED` 未触发，原因包括：

- equal-weight F1 点差 `0.00516396 < 0.010`；
- equal-weight F1 区间下界 `-0.00262300 <= 0`；
- MuSiQue F1 点差 `-0.00231954 <= 0`。

`GENERATOR_TRANSFER_NEGATIVE` 也未触发：

- equal-weight、HotpotQA 和 MuSiQue 的 F1 区间上界均不小于 0；
- equal-weight、HotpotQA 和 MuSiQue 的 EM 区间上界均不小于 `-0.010`。

所以按冻结互斥规则进入 `GENERATOR_TRANSFER_INCONCLUSIVE`。该判定不是 integrity failure，也不能改写为“无显著差异即等价”。

## 6. Generator interaction（描述性）

interaction 定义为：

```text
second-generator retrieval delta - frozen Qwen retrieval delta
```

| 数据集/联合 | F1 interaction / 95% interval | EM interaction / 95% interval |
|---|---:|---:|
| HotpotQA | `-0.00213229 [-0.02198996, 0.01727582]` | `-0.00400000 [-0.02400000, 0.01600000]` |
| MuSiQue | `-0.01372096 [-0.02186437, -0.00565804]` | `-0.01133333 [-0.01900000, -0.00366667]` |
| Dataset equal-weight | `-0.00792663 [-0.01869574, 0.00285589]` | `-0.00766667 [-0.01866667, 0.00300000]` |

HotpotQA interaction 区间跨 0；MuSiQue 的 F1/EM interaction 均为负且区间不跨 0，说明在该数据集与当前第二生成器配置下，static-q25 相对 Dense 的检索效应较冻结 Qwen 结果衰减。等权 interaction 仍跨 0。该分析只解释生成器与检索臂的效应差异，不进入 Stage4G 主判定，也不授权修改模型、prompt 或检索参数。

## 7. 支持性运行指标

| 数据集/方法 | UNKNOWN rate | Mean completion tokens | Mean input tokens | Mean evidence units | Truncation |
|---|---:|---:|---:|---:|---:|
| HotpotQA Dense | 0.466000 | 3.914000 | 899.164000 | 19.939 | 0 |
| HotpotQA static-q25 | 0.445000 | 4.080000 | 900.923000 | 19.939 | 0 |
| MuSiQue Dense | 0.868667 | 2.634333 | 882.081667 | 20.000 | 0 |
| MuSiQue static-q25 | 0.875667 | 2.601000 | 885.454667 | 20.000 | 0 |

正式 main 完成 8,000 次生成，失败调用为 0，记录的累计 runner wall time 为 56,501.842 秒，GPU peak allocated memory 为 7,885,933,056 bytes（约 7.34 GiB）。预哈希分层 subset rerun 完成 400 次生成，失败调用为 0，wall time 为 2,037.901 秒，GPU peak allocated memory 为 7,853,514,240 bytes（约 7.31 GiB）。

## 8. 确定性、Gold 隔离与独立验证

资源评估后事前选择确定性合同 B：

```text
full official main
+ pre-hash-selected, dataset-stratified rerun subset
```

subset 在两个数据集和两个方法臂各包含 100 次调用，共 400 次；没有使用 Gold 或结果选择。独立 verifier 逐行确认 subset prediction 与 prompt audit 相对 main 完全一致，证据等级明确为 `STRATIFIED_SUBSET_NOT_FULL_RERUN`。

Pre-Gold verifier 在 `gold_opened=false` 状态下确认：

- main 8,000 calls 与 subset 400 calls 身份、配对和顺序正确；
- evidence 是对应冻结 ranking 的连续前缀；
- prompt 语义内容可独立重建；
- Gold、答案和方法标签没有进入 prompt；
- completion token IDs、token cap 和 truncation 状态有效；
- subset prediction 与 audit 精确复现。

Gold evaluation 只在 `STAGE4G_GTR_PRE_GOLD_VERIFIED` 后打开冻结 Gold。最终 verifier 独立重建 4,000 个 query scores、数据集 bootstrap、等权 bootstrap、generator interaction 和 decision，得到：

```text
STAGE4G_GTR_FINAL_VERIFICATION_PASS
GENERATOR_TRANSFER_INCONCLUSIVE
```

## 9. 正式工件身份

| 工件 | Bytes | SHA-256 |
|---|---:|---|
| input/model manifest | 15,863 | `5B4070AF14F2DBBEB4D69EFA1FA445017DB6F1BF7B071DCE73D9D7498E7DAEC5` |
| predictions main | 1,508,328 | `E6B0A50CB3090A7268E838EC5BBB0DD6C5FE90440A75DA0B103D2E0906D31709` |
| predictions rerun subset | 78,362 | `43CDF730152032D752956D359E707FF92C17C8517EBE0B8AA1DEB72855688FA9` |
| prompt audit main | 14,058,957 | `E8227941D1AF5E3C893AC538E1E5DD61C2FE818F879D0EA6D45FB7137E54F8F1` |
| prompt audit rerun subset | 722,498 | `75947C6F15168F49E552A5B99388354E39490349E30BDC034D79B9F4B75ADFA4` |
| telemetry main | 1,818 | `F4B5B8E49149C692993EE4023C80A443AE608C2BBF34E627CBF256F41BDB0BA9` |
| telemetry rerun subset | 1,784 | `3F12932BD92BD054DBF7113CB96B6396DDFAF6FC43B664C33448E85FF05EA95F` |
| verified pre-Gold | 1,439 | `5F9C26A6D0F80B423FFD500FA2ECFCF5815F60815F36E639BEEE11E5AA1ABAB4` |
| query scores | 1,212,870 | `8796DC8033CC9B3993BC02A224CD8585AE89C46E7CDAB20DA1447E9C6B0241BE` |
| dataset summaries | 3,523 | `1656CEAC063EB53D4854481C83A1A4046D6257B442A3C376EDC851B5436D6E3B` |
| equal-weight summary | 1,124 | `0BF7E2658521510438545BC077DBAA1EA7C902C2FD35FFBE4013D209D7890239` |
| scientific decision | 579 | `246FE8B1DFC157551E570994059306315C03AA050B23AC3F9FD31780D710FBF5` |
| final verification | 1,302 | `3BB9A87C3BD62FCF8CE663F4EEA7A28A6D0C8E1ECC0AB8FBF8C015212137E65B` |
| artifact manifest | 3,613 | `E61FADC265D2F2AA937E7E66F78011BDD6B45E67CB61BDCF03FF320C5DB0FDD1` |

## 10. 论文主张边界

Stage4G 不是新的独立数据集验证；两个数据集和检索 rankings 都来自已冻结的 Stage4E/4F 边界。它提供的是 generator 维度的受控复制测试。

当前可写：

- static-q25 的检索增益已在 Qwen 下通过 Stage4E/4F 的两个冻结 closed-candidate 数据集验证；
- 在一个额外、事前指定的 Gemma mobile-QAT 生成器配置下，HotpotQA 保持正向点估计，但 MuSiQue 点估计为轻微负向，数据集等权联合判定为 inconclusive；
- retrieval gain 尚未获得跨生成器复制支持，也没有达到预注册的明确负向门。

当前不可写：

- HyperGranular-RAG 对生成器普遍鲁棒；
- Gemma 4 E2B 不适合 RAG；
- Qwen2.5-1.5B 的基础模型能力显著强于 Gemma 4 E2B；
- Gemma 4 的架构质量较差；
- Qwen 在所有设备上都更高效；
- 当前结果已经扩展到 full-wiki、open-domain 或新 controller。

## 11. 复现入口与锁定状态

- 实验卡：`docs/STAGE4G_GTR_EXPERIMENT_CARD.md`
- 配置：`configs/stage4g_gtr_official.json`
- 依赖：`requirements-stage4g.txt`
- input/model manifest：`results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_input_model_manifest.json`
- pre-Gold verification：`results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_verified_pregold.json`
- dataset summaries：`results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_dataset_summaries.json`
- equal-weight summary：`results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_equal_weight_summary.json`
- decision：`results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_scientific_decision.json`
- final verification：`results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_final_verification.json`
- artifact manifest：`results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_artifact_manifest.json`

Reservation、Stage3B、U2 和 controller branch 全程保持锁定。任何新生成器、开放域、强基线、消融或 controller 实验必须作为新的科学语义与新阶段处理。
