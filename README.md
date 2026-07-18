# HyperGranular-RAG

以自适应粒球组织知识单元、以 query-aware 超边补充跨粒球关系，并通过受保护插入控制检索扩展的多跳 RAG 研究仓库。

## 当前状态

| 项目 | 当前事实 |
|---|---|
| 研究阶段 | Stage4B-U1-D development Gold evaluation 已完成并独立验证 |
| 状态 | `STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED` |
| 数据边界 | 2WikiMultiHopQA development：4,500 queries / 143,820 unlabeled units |
| 当前证据 | 冻结 U1 controller 的 development Gold 负结果；计算完整性已验证 |
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

## 冻结方法

- Dense Top-10 受保护；最终 effective-K 为 `K_q=min(20, |C_q|)`。
- q25 floor：`0.1957079917192459`。
- 每查询最多插入 4 个 q25 单元。
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

完整研究轨迹见 [ROADMAP](docs/ROADMAP.md) 和 [文档索引](docs/INDEX.md)。

## 数据与来源边界

- 官方外部数据：2WikiMultiHopQA `data_ids_april7.zip`，来源和 SHA 已冻结。
- Stage4B-U1-D development：4,500 queries / 143,820 units。
- Gold 仅由已授权 evaluator 在 ranking 冻结后使用，未进入索引、候选、排序、过滤或 controller。
- Reservation 仅保留登记的 ID 摘要边界，不读取内容、embedding 或指标。
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
```

日常阅读从 [docs/INDEX.md](docs/INDEX.md) 开始。历史 Amendment、Hard Failure 和 PowerShell 边界材料保留用于追溯，但不再是当前执行入口。

## 复现

当前环境、冻结 SHA、Gold 结果与复现边界见 [REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md)。主要当前文件：

- [Gold authorization config](configs/stage4b_u1_d_gold_evaluation.json)
- [evaluation summary](results/stage4b_u1_d_official_dev4500_simplified_v1_evaluation_summary.json)
- [VERIFIED_POST_GOLD](results/stage4b_u1_d_official_dev4500_simplified_v1_verified_post_gold.json)
- [统计验证报告](reports/超粒球RAG_Stage4B_U1_D_Gold评估与统计验证报告.md)

## 科研治理

- 预注册协议、样本量、主要终点和停止规则先于结果读取提交。
- Level B/C 工程问题按影响做最小修正和适量测试，不恢复逐步骤审批链。
- 必须暂停：Gold/evaluator、reservation、科学语义变化，以及错误 official 输入/cache、Gold 泄漏、不可信 ranking 或正式工件完整性异常。
- 已完成的 U1-D Gold evaluation 不自行重复；不得在同一 development 结果后改特征、阈值、预算或检验再包装重跑。
- 每日方向复核是非阻塞检查，不要求每日创建审核文档。
- 旧 PowerShell launcher、remote gate、observer、stderr framing 和 nested PRE 链只作为历史失败实现保留。

## 已知限制

- 当前研究只评估检索，不包含生成器答案质量。
- q25 阈值来自早期数据，不能声称对 2Wiki 最优。
- Stage4B-U1 是单一 development benchmark batch 的资源分配实验，不能主张为在线 controller。
- 插入量减少刚超过 `40%` 门槛，但不能抵消 retention、Fisher 和 CR 门失败。
- 问题类型结果仅为描述性审计；`compositional` 与 `inference` 被标记为 `SUBGROUP_CAUTION`。
- 冻结 evaluator 未输出协议所写的类型级区间；该报告完整性缺口不改变总体停止决定，但限制类型层解释。

## 下一步

Stage4B-U1 分支按预注册规则停止，reservation 继续锁定。后续若提出新 controller，必须作为新的科学语义，先形成新的开发问题和预注册协议；不得在同一 development 上事后调整 U1 并重跑，也不得因本结果直接打开 reservation。

仓库：<https://github.com/lljjcc426/HyperGranular-RAG>
