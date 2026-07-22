# HyperGranular-RAG 证据与主张台账

## 当前总论边界

静态 q25 protected insertion 与 adaptive controller 是两个不同主张。Stage4E 现已支持前者在冻结 HotpotQA same-domain closed-distractor 边界上的端到端答案质量增益，同时当前 U1/Stage4D controller 线仍保持关闭。论文不得用 controller 负结果覆盖静态方法，也不得用静态 Stage4E 正结果替 controller 晋级。

## 可写主张

| 主张 | 证据等级 | 核心证据 | 论文表述边界 |
|---|---|---|---|
| protected insertion 能在 Dense 主干后补充证据 | 有限内部独立验证 | Stage2F q25 p10/i4 相对 Dense CR@20 `+0.0175 [0.0025, 0.0350]` | 只限既有 HotpotQA/MuSiQue slice 与冻结 encoder/K；主 CR@10 gate 失败 |
| 官方 2Wiki development 上存在 q25 gain/harm 事件 | 官方来源 development 事件率估计 | Stage4A-R2 与 Stage4B Gold audit：94 gain / 69 harm queries | 不等同于平均 answer-quality 提升或外部泛化 |
| 当前 U1-D controller 降低资源但选择方向失败 | verified development negative result | 插入量 `-40.0275%`；gain retention `0.5000`；harm retention `0.7681`；CR@20 低于 Dense/q25 | 可写为当前 controller 的有效负结果；不能写成 HGRAG 整体无效 |
| raw U1 score 对 gain/harm 方向错误且 all-on/off 受限 | post-Gold exploratory，`CAUTION` | Stage4C raw score AUROC `0.39269 [0.30558, 0.48150]`；92/94 gain query 为 mixed gain/noise | 机制诊断，不是新 controller efficacy |
| candidate deployable features 含部分 gain/harm 符号信号，但不足以晋级 | post-Gold exploratory，`CAUTION` | Stage4D Task-C combined AUROC `0.64310 [0.55520, 0.72974]`，Brier 未优于 prevalence baseline | 结论必须是 inconclusive；不授权 U2、selector 或阈值 |
| 静态 HGRAG 在冻结 same-domain closed-distractor 边界上改善端到端答案质量 | verified official positive result | Stage4E：answer F1 `0.42150→0.43628`；paired delta `+0.01478 [0.00020,0.02988]`；final verification PASS | 仅限 HotpotQA deterministic 1,000-query、Qwen2.5-1.5B、Top-20；F1 下界接近 0，不写成大幅或普遍提升 |

## 不可写主张

- “HyperGranular-RAG 在所有任务或 full-wiki 环境提高最终答案准确率”；Stage4E 只支持冻结的 HotpotQA same-domain closed-distractor 边界。
- “q25 在 2Wiki 上平均优于 Dense”；现有 Stage4A/4B 证据没有建立该总体现象。
- “U1 能保留 gain 并过滤 harm”；冻结结果方向相反。
- “Stage4D 已学会可部署 candidate selector”；唯一 advancement panel 未过联合门。
- “当前结果已跨数据集或 full-wiki 泛化”；Stage4E proposed boundary 仍是 HotpotQA same-domain closed distractor setting。
- “Stage4E 是对生成器未见数据的无污染测试”；它只保证未被本项目读取，公开 HotpotQA train 可能进入过模型预训练语料。
- “不显著说明方法等价”；所有未过正/负门的结果都应写为 inconclusive。

## 证据入口

| 主题 | 入口 |
|---|---|
| 完整时间线 | `docs/ROADMAP.md` |
| 方法与证据审计 | `docs/PRIOR_STAGE_METHOD_AUDIT.md` |
| U1-D Gold 负结果 | `reports/超粒球RAG_Stage4B_U1_D_Gold评估与统计验证报告.md` |
| Stage4C 失败机制 | `reports/超粒球RAG_Stage4C_U1失败机制诊断报告.md` |
| Stage4D candidate 机制 | `reports/超粒球RAG_Stage4D_CMA候选边际效用归因审计报告.md` |
| Stage4D final verification | `results/stage4d_cma_verified_final.json` |
| Stage4D 关闭边界 | `docs/STAGE4D_CMA_CLOSURE.md` |
| Stage4E generator selection | `reports/超粒球RAG_Stage4E生成模型选择报告.md`；`results/stage4e_generator_selection_verified.json` |
| Stage4E official E2E result | `reports/超粒球RAG_Stage4E_E2E答案质量报告.md`；`results/stage4e_e2e_official_train1000_v1_evaluation_summary.json`；`results/stage4e_e2e_official_train1000_v1_final_verification.json` |

## Stage4E 写入规则

Stage4E 已完成，可写两臂绝对 F1/EM、成对差值与区间、retrieval secondary metrics、确定性/独立验证状态和冻结决策。必须同段保留 new-ID same-domain closed-distractor、公开 train 可能存在预训练污染、F1 下界接近零、subgroup 仅 `CAUTION` 的限制。不得把 Stage4E 正结果用于恢复 U1/Stage4D controller，或推断跨数据集/full-wiki 泛化。

生成器选择的唯一规范表述是：在 RTX 4060 Laptop 8GB、固定短答案 RAG prompt、4,096-token 输入上限和可实际部署格式下，Qwen2.5-1.5B-Instruct FP16 在 200-query generator-selection development 上取得更高 answer F1/EM 和更低运行时间/显存，并按预登记规则成为 Stage4E 唯一生成器。Gemma 4 E2B 以官方 mobile-QAT 格式运行，因此该结果不能用于分离或评价纯基础模型架构能力。
