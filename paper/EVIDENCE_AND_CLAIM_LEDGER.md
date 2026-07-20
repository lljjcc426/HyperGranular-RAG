# HyperGranular-RAG 证据与主张台账

## 当前总论边界

静态 q25 protected insertion 与 adaptive controller 是两个不同主张。现有证据支持继续检验前者的端到端答案质量，但已经关闭当前 U1/Stage4D controller 线。论文不得用 controller 负结果覆盖静态方法，也不得用静态 retrieval 的局部增益替 controller 晋级。

## 可写主张

| 主张 | 证据等级 | 核心证据 | 论文表述边界 |
|---|---|---|---|
| protected insertion 能在 Dense 主干后补充证据 | 有限内部独立验证 | Stage2F q25 p10/i4 相对 Dense CR@20 `+0.0175 [0.0025, 0.0350]` | 只限既有 HotpotQA/MuSiQue slice 与冻结 encoder/K；主 CR@10 gate 失败 |
| 官方 2Wiki development 上存在 q25 gain/harm 事件 | 官方来源 development 事件率估计 | Stage4A-R2 与 Stage4B Gold audit：94 gain / 69 harm queries | 不等同于平均 answer-quality 提升或外部泛化 |
| 当前 U1-D controller 降低资源但选择方向失败 | verified development negative result | 插入量 `-40.0275%`；gain retention `0.5000`；harm retention `0.7681`；CR@20 低于 Dense/q25 | 可写为当前 controller 的有效负结果；不能写成 HGRAG 整体无效 |
| raw U1 score 对 gain/harm 方向错误且 all-on/off 受限 | post-Gold exploratory，`CAUTION` | Stage4C raw score AUROC `0.39269 [0.30558, 0.48150]`；92/94 gain query 为 mixed gain/noise | 机制诊断，不是新 controller efficacy |
| candidate deployable features 含部分 gain/harm 符号信号，但不足以晋级 | post-Gold exploratory，`CAUTION` | Stage4D Task-C combined AUROC `0.64310 [0.55520, 0.72974]`，Brier 未优于 prevalence baseline | 结论必须是 inconclusive；不授权 U2、selector 或阈值 |
| 静态 HGRAG 改善端到端答案质量 | **尚无证据** | Stage4E-E2E 仅有 Level A 草案 | 在 final verification 前不得写结果、方向或效果量 |

## 不可写主张

- “HyperGranular-RAG 已提高最终答案准确率”；尚未运行生成器答案质量实验。
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
| Stage4E planned evaluation | `docs/STAGE4E_STATIC_HGRAG_E2E_ANSWER_QUALITY_LEVEL_A_PROTOCOL.md` |

## Stage4E 写入规则

Stage4E 完成前，论文只能写：研究问题、冻结比较、new-ID same-domain 边界、generator/prompt、主终点和判定门。完成后必须先登记：两臂绝对 F1/EM、成对差值与区间、retrieval secondary metrics、确定性/独立验证状态、数据与模型 SHA、负或不确定结果，以及 11 类谬误检查；之后才能更新摘要、结果和结论。
