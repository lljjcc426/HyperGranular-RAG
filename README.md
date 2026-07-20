# HyperGranular-RAG

以自适应粒球组织知识单元、以 query-aware 超边补充跨粒球关系，并通过受保护插入控制检索扩展的多跳 RAG 研究仓库。

## 当前状态

| 项目 | 当前事实 |
|---|---|
| 研究阶段 | Stage4D-CMA 已验证并关闭；Stage4E-E2E 输入、模型、环境和 Level B 实现已冻结 |
| 状态 | `STAGE4E_INPUT_CHANNELS_VERIFIED`；`STAGE4E_LEVEL_B_IMPLEMENTATION_READY`；`STAGE4E_OFFICIAL_EXECUTION_NOT_AUTHORIZED` |
| 已用数据边界 | 2WikiMultiHopQA development：4,500 queries / 143,820 unlabeled units |
| 当前证据 | U1-D 是有效 development 负结果；Stage4D candidate 机制证据不确定；静态 HGRAG 的答案质量尚未测试 |
| Gold | 仅在 ranking 冻结后由独立 evaluator 使用；未进入 controller 或排序 |
| Reservation / Stage3B | `KEEP_LOCKED` |

当前 Gold 结果：

- U1 将 q25 插入量从 7,260 降至 4,354，减少 `40.0275%`；
- gain retention 为 `47/94=0.5000`，harm retention 为 `53/69=0.7681`，retention gap 为 `-0.2681`；
- U1 CR@20 为 `0.77089`，相对 Dense 为 `-0.00133`，相对 q25 为 `-0.00689`；
- 6 项 development 晋级门通过 2 项、失败 4 项；按冻结停止规则关闭 U1 分支；
- 主运行与预注册复跑同字节，独立验证对 4,500 queries 的重算全部通过；
- 结果生成提交为 `c06761f0c55cbeecf75564211a59f4540cfbae06`；正式 summary 原始字节修复提交为 `b500184bc581d73a381de65c32cf3b72e9758cc9`。

这是当前冻结 U1-D controller 的可复现 development 负结果：U1-D 当前冻结形式未获得支持。它不是执行失败，也不能推导 HyperGranular-RAG 整体无效；它不支持 U1 优于 Dense、保留更多 gain than harm、进入 reservation 或具备跨数据集泛化能力。

## 当前研究问题

Stage4A-R2 已确认：q25 超边扩展在官方 2WikiMultiHopQA 上存在可测的 query-level gain/harm 事件，但平均 CR 提升尚未确认，且 query 类型存在明显异质性。

Stage4B-U1-D 回答的问题是：在不使用 Gold 参与检索决策的前提下，基于无标签边界不确定性的 U1 controller，能否减少 q25 插入成本，同时保留足够的检索收益并控制伤害。冻结实验的答案是否定的：成本门通过，但选择性机制和 CR@20 门未通过。

Stage4C-U1-FMA 进一步审计其失败机制：raw U1 score 对 GAIN-vs-HARM 的 AUROC 为 `0.39269 [0.30558, 0.48150]`，92/94 个 gain query 为 mixed gain/noise，69/69 个 harm query 为 displacement harm；但固定 OOF panels 均未达到稳定信号门，最终决策为 `MECHANISM_EVIDENCE_INCONCLUSIVE`。

Stage4D-CMA 将问题下沉到 candidate 级：8,467 个 eligible candidates 经 standardized first-slot insertion、`LOO_NO_BACKFILL` 和 `LOO_WITH_BACKFILL` 归因后，固定 Task-C combined panel 的 AUROC 为 `0.64310 [0.55520, 0.72974]`、AP 为 `0.72198`。它存在部分符号信号，但 AUROC 未达到 `0.65` 且 Brier 未优于 prevalence baseline，最终为 `CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE`。

Stage4D 和当前 controller 分支现已冻结关闭。Stage4E-E2E 转向独立问题：在此前未读的 HotpotQA train ID-hash 边界上，用同一固定生成器比较 Dense Top-20 与不带 controller 的静态 q25 Top-20，主要评价 answer F1。Level A 已接受；1,000-query blind/Gold/metadata 通道、模型 snapshot、CUDA 环境、config、runner/evaluator/verifier 和合成测试现已完成绑定，但尚未运行 official retrieval、generation 或 Gold evaluation。

## 冻结方法边界

- Dense Top-10 受保护；最终 effective-K 为 `K_q=min(20, |C_q|)`。
- q25 floor：`0.1957079917192459`。
- 每查询最多插入 4 个 q25 单元。
- Stage4E proposed static arm 对所有 query 直接使用 q25 ranking，不调用 controller。
- U1 score 使用四项无标签 ECDF-midrank 输入及冻结 tie-break。
- 全局使用 60% planned-insert ordered-prefix budget。
- Controller 不接收 Gold、reservation 或 Stage3B 输入。
- Gold evaluator 与 controller 分离；本次只在用户明确授权后连接冻结 Gold map。

完整语义见 [Stage4B-U1 simplified execution protocol](docs/STAGE4B_U1_SIMPLIFIED_EXECUTION_PROTOCOL_V1.md)。

## 证据等级

| 阶段 | 证据等级 | 保留结论 |
|---|---|---|
| Stage2F | 有限内部独立验证 | 主 CR@10 gate 失败；保留窄范围 q25/Top-20 证据 |
| Stage2G | 有效负结果 | boundary-only 规则不受支持 |
| Stage3A | 失败的预注册开发 | 稀疏事件触发 fallback；Stage3B 未开放 |
| Stage4A-R2 | 官方内部验证完成 | 事件率精度达标；平均 CR 提升未确认；异质性明显 |
| Stage4B-U1-D | development Gold 评估与独立验证完成 | 资源门单项通过，但联合晋级门失败；U1 分支停止 |
| Stage4C-U1-FMA | post-Gold 探索性诊断，`CAUTION` | query-level score 方向错误且 all-on/off 受限；不足以授权 U2 |
| Stage4D-CMA | post-Gold exploratory official audit，`CAUTION`；已关闭 | candidate-level 部分信号未过联合晋级门；不授权 U2 |
| Stage4E-E2E | Level A accepted；输入与 Level B 实现已验证 | 计划检验静态 q25 是否转化为答案质量收益；official 执行未授权，当前无答案质量结果 |

完整研究轨迹见 [ROADMAP](docs/ROADMAP.md) 和 [文档索引](docs/INDEX.md)。

## 数据与来源边界

- 官方外部数据：2WikiMultiHopQA `data_ids_april7.zip`，来源和 SHA 已冻结。
- Stage4B-U1-D development：4,500 queries / 143,820 units。
- Gold 仅由已授权 evaluator 在 ranking 冻结后使用，未进入索引、候选、排序、过滤或 controller。
- Reservation 仅保留登记的 ID 摘要边界，不读取内容、embedding 或指标。
- Stage4E boundary 是 HotpotQA `hotpot_train_v1.1.json` 的确定性 1,000-query 样本；source 和三个隔离通道已冻结且历史 ID 重叠为 0，但未执行 retrieval、generation 或 Gold metric。
- Raw data、processed corpus、embedding cache、模型和密钥不进入 Git。

## 仓库结构

```text
AGENTS.md          当前项目约束与强制暂停边界
configs/           冻结执行配置
docs/              当前协议、索引、路线图与历史证据
reports/           阶段性科研报告
results/           可提交的审计、汇总与冻结工件
scripts/           数据、检索、controller、验证和评估脚本
tests/             研究代码回归测试
paper/             论文结构、证据主张台账与待补材料
```

日常阅读从 [docs/INDEX.md](docs/INDEX.md) 开始。历史 Amendment、Hard Failure 和 PowerShell 边界材料保留用于追溯，但不再是当前执行入口。

## 复现

当前环境、冻结 SHA、Gold 结果与复现边界见 [REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md)。主要当前文件：

- [Gold authorization config](configs/stage4b_u1_d_gold_evaluation.json)
- [evaluation summary](results/stage4b_u1_d_official_dev4500_simplified_v1_evaluation_summary.json)
- [VERIFIED_POST_GOLD](results/stage4b_u1_d_official_dev4500_simplified_v1_verified_post_gold.json)
- [统计验证报告](reports/超粒球RAG_Stage4B_U1_D_Gold评估与统计验证报告.md)
- [Stage4C 诊断协议](docs/STAGE4C_U1_FAILURE_MECHANISM_AUDIT_PROTOCOL.md)
- [Stage4C summary](results/stage4c_u1_fma_summary.json)
- [Stage4C 失败机制诊断报告](reports/超粒球RAG_Stage4C_U1失败机制诊断报告.md)
- [Stage4D-CMA Level A 协议](docs/STAGE4D_CANDIDATE_MARGINAL_UTILITY_AUDIT_PROTOCOL.md)
- [Stage4D 固定依赖](requirements-stage4d.txt)
- [Stage4D final verification](results/stage4d_cma_verified_final.json)
- [Stage4D 候选边际效用归因报告](reports/超粒球RAG_Stage4D_CMA候选边际效用归因审计报告.md)
- [Stage4D 关闭声明](docs/STAGE4D_CMA_CLOSURE.md)
- [Stage4E-E2E Level A 协议](docs/STAGE4E_STATIC_HGRAG_E2E_ANSWER_QUALITY_LEVEL_A_PROTOCOL.md)
- [Stage4E official config](configs/stage4e_e2e_official_train1000_v1.json)
- [Stage4E input manifest](results/stage4e_e2e_official_train1000_v1_input_manifest.json)
- [Stage4E model snapshot manifest](results/stage4e_e2e_model_snapshot_manifest.json)
- [Stage4E environment manifest](results/stage4e_e2e_environment_manifest.json)
- [Stage4E Level B 实现报告](docs/STAGE4E_E2E_LEVEL_B_IMPLEMENTATION_REPORT.md)
- [论文证据与主张台账](paper/EVIDENCE_AND_CLAIM_LEDGER.md)

## 科研治理

```text
STAGE_LEVEL_AUTHORIZATION_ACTIVE
ONE_RESEARCH_STAGE_ONE_AUTHORIZATION
STEP_LEVEL_APPROVAL_DISABLED
CHANNEL_LEVEL_REAPPROVAL_DISABLED
ENGINEERING_WORK_AUTONOMOUS
STAGE_INTERNAL_EXECUTION_CONTINUOUS
EXCEPTION_BASED_PAUSE_ONLY
SCIENTIFIC_INTEGRITY_CONTROLS_RETAINED
```

- 这是项目长期、全局的现行治理基线，适用于当前及未来全部科研阶段，不是本次任务或 Stage4E 的临时规则。预注册数据边界、主要终点和停止规则先于结果读取提交；一个科学阶段只授权一次。除非实验卡明确排除，授权覆盖实现、测试、预定义 Channel/数据读取、正式运行、固定分析、verifier、rerun、报告、文档、Git 同步和远端验证。
- Channel A/B 与 Gold-free/Gold-only 继续技术隔离，但不形成重复审批点；精确命令、脚本、环境变量、文件或提交不是科学审批对象。
- 阶段内工程问题自主最小修复、测试、记录并继续。只在新科学问题/阶段、冻结科学语义变化、使用授权外新证据源，或严重科研完整性异常时暂停。
- 逐命令、逐脚本、逐文件、逐提交、逐通道审批，以及重复 review、单独 synthetic 授权、普通修复 Amendment、逐次 approval record 和 nested approval chain 均已取消。
- 新阶段默认使用 1–3 页轻量实验卡，固定研究问题、假设、数据边界、方法、主要终点、成功/停止/证据不足规则、Gold/独立测试/reservation 边界和禁止事项；长协议仅用于高风险例外。
- 历史审批链只用于证据追溯，不再构成当前执行规则。已有科学协议、技术隔离、完整性检查、结果和停止结论不变。
- 全局规则不自动扩大既有阶段明确排除的科学范围。当前 Stage4E 既有授权明确止于输入绑定和 Level B 实现，因此 official 仍未授权；下一边界是扩展阶段授权范围，不是分别确认 retrieval/generation 与 Gold 命令。

## 已知限制

- 已完成证据只评估检索/controller 机制；Stage4E 尚未运行，因此当前没有生成器答案质量证据。
- q25 阈值来自早期数据，不能声称对 2Wiki 最优。
- Stage4B-U1 是单一 development benchmark batch 的资源分配实验，不能主张为在线 controller。
- 插入量减少刚超过 `40%` 门槛，但不能抵消 retention、Fisher 和 CR 门失败。
- 问题类型结果仅为描述性审计；`compositional` 与 `inference` 被标记为 `SUBGROUP_CAUTION`。
- 冻结 evaluator 未输出协议所写的类型级区间；该报告完整性缺口不改变总体停止决定，但限制类型层解释。
- Stage4C 不含 candidate Gold identity/rank 或 candidate score/support/similarity 特征；candidate-level 方向只能作为未来假设。
- Stage4C 是同一 development 上的 post-Gold 探索性诊断，不建立新 controller efficacy。
- Stage4D 仍是同一 development 上的探索性 candidate audit；最低事件门不是 power guarantee，也没有 reservation 或外部验证。
- Stage4E proposed HotpotQA train 边界属于 new-ID same-domain closed distractor evaluation，不是新数据集、full-wiki 或跨域外部验证；拟定 `n=1000` 也不是 power guarantee。

## 下一步

Stage4E-E2E 的输入、模型、环境、命令、verifier 与 Level B 实现已经绑定。下一步是决定是否一次性扩展 Stage4E 阶段授权以覆盖冻结的 official 事务；若授权范围包含预定义 Gold-free 和 Gold 通道，则按协议完整性门连续执行。Stage4D、当前 controller、Reservation、Stage3B 和 U2 保持关闭或锁定。

仓库：<https://github.com/lljjcc426/HyperGranular-RAG>
