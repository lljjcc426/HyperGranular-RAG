# HyperGranular-RAG

以自适应粒球组织知识单元、以 query-aware 超边补充跨粒球关系，并通过受保护插入控制检索扩展的多跳 RAG 研究仓库。

## 当前状态

| 项目 | 当前事实 |
|---|---|
| 研究阶段 | Stage4B-U1-D official pre-Gold 已完成并独立验证 |
| 状态 | `VERIFIED_PRE_GOLD_COMMITTED` |
| 数据边界 | 2WikiMultiHopQA development：4,500 queries / 143,820 unlabeled units |
| 当前证据 | 实现完整性与正式 ranking 冻结证据；尚无 U1-D Gold 效果结论 |
| Gold | 未读取、未评估；进入 Gold evaluation 需要用户单独明确授权 |
| Reservation / Stage3B | `KEEP_LOCKED` |

当前冻结结果：

- Gold-free controller 覆盖 4,500 queries，`selected=1195`；
- decisions、rankings、policy 已在提交 `9357c157217f85008fa93df07d321a2f4c6a2bc1` 冻结；
- independent verifier 已对 4,500 queries 独立重算并通过；
- `VERIFIED_PRE_GOLD` 提交为 `83d172bc89efbb31782eee308bac5293aa24457b`；
- verified 记录为 `gold_inputs_loaded=false`、`evaluation=null`，全部 checks 为 `PASS`。

这些事实不能解释为 U1-D 有效、优于 Dense、通过晋级门或具备跨数据集泛化能力。

## 当前研究问题

Stage4A-R2 已确认：q25 超边扩展在官方 2WikiMultiHopQA 上存在可测的 query-level gain/harm 事件，但平均 CR 提升尚未确认，且 query 类型存在明显异质性。

Stage4B-U1-D 当前要回答：在不使用 Gold 参与检索决策的前提下，基于无标签边界不确定性的 U1 controller，能否减少 q25 插入成本，同时保留足够的检索收益并控制伤害。

## 冻结方法

- Dense Top-10 受保护；最终 effective-K 为 `K_q=min(20, |C_q|)`。
- q25 floor：`0.1957079917192459`。
- 每查询最多插入 4 个 q25 单元。
- U1 score 使用四项无标签 ECDF-midrank 输入及冻结 tie-break。
- 全局使用 60% planned-insert ordered-prefix budget。
- Controller 不接收 Gold、reservation 或 Stage3B 输入。
- Gold evaluator 与 controller 分离，只能在新的 Level A 授权后运行。

完整语义见 [Stage4B-U1 simplified execution protocol](docs/STAGE4B_U1_SIMPLIFIED_EXECUTION_PROTOCOL_V1.md)。

## 证据等级

| 阶段 | 证据等级 | 保留结论 |
|---|---|---|
| Stage2F | 有限内部独立验证 | 主 CR@10 gate 失败；保留窄范围 q25/Top-20 证据 |
| Stage2G | 有效负结果 | boundary-only 规则不受支持 |
| Stage3A | 失败的预注册开发 | 稀疏事件触发 fallback；Stage3B 未开放 |
| Stage4A-R2 | 官方内部验证完成 | 事件率精度达标；平均 CR 提升未确认；异质性明显 |
| Stage4B-U1-D | 正式 pre-Gold 验证完成 | ranking 与 Gold 隔离已验证；方法效果仍待 Gold evaluation |

完整研究轨迹见 [ROADMAP](docs/ROADMAP.md) 和 [文档索引](docs/INDEX.md)。

## 数据与来源边界

- 官方外部数据：2WikiMultiHopQA `data_ids_april7.zip`，来源和 SHA 已冻结。
- Stage4B-U1-D development：4,500 queries / 143,820 units。
- Gold 仅可用于后续单独授权的 evaluator，不得进入索引、候选、排序、过滤或 controller。
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

当前环境、冻结 SHA、pre-Gold 结果与后续可执行边界见 [REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md)。主要当前文件：

- [official config](configs/stage4b_u1_d_official.json)
- [decisions](results/stage4b_u1_d_official_dev4500_simplified_v1_decisions.jsonl)
- [rankings](results/stage4b_u1_d_official_dev4500_simplified_v1_rankings.jsonl)
- [policy](results/stage4b_u1_d_official_dev4500_simplified_v1_policy.json)
- [VERIFIED_PRE_GOLD](results/stage4b_u1_d_official_dev4500_simplified_v1_verified_pre_gold.json)

## 科研治理

- 预注册协议、样本量、主要终点和停止规则先于结果读取提交。
- Level B/C 工程问题按影响做最小修正和适量测试，不恢复逐步骤审批链。
- 必须暂停：Gold/evaluator、reservation、科学语义变化，以及错误 official 输入/cache、Gold 泄漏、不可信 ranking 或正式工件完整性异常。
- 每日方向复核是非阻塞检查，不要求每日创建审核文档。
- 旧 PowerShell launcher、remote gate、observer、stderr framing 和 nested PRE 链只作为历史失败实现保留。

## 已知限制

- 当前研究只评估检索，不包含生成器答案质量。
- q25 阈值来自早期数据，不能声称对 2Wiki 最优。
- Stage4B-U1 是有限 benchmark batch 的资源分配设计，尚不能主张为在线 controller。
- `selected=1195` 是无标签选择数量，不是 gain、CR、显著性或效果结论。

## 下一步

下一科研门是单独授权的 Gold evaluation。授权前保持 rankings、policy 与 `VERIFIED_PRE_GOLD` 冻结，不运行 evaluator、不读取 Gold/reservation、不解释 U1-D 指标。

仓库：<https://github.com/lljjcc426/HyperGranular-RAG>
