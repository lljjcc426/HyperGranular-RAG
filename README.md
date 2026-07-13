# HyperGranular-RAG

以自适应粒球为知识单元、以超边表达跨粒球高阶关系，并通过受保护插入控制检索扩展的多跳 RAG 研究仓库。

## 当前状态

| 项目 | 状态 |
|---|---|
| 当前阶段 | Stage4B-U1-D v2.1 pre-Gold 执行已批准，尚未开始 official channel |
| 获批执行协议 | 仅 U1-D channel/controller/artifact freeze/`VERIFIED_PRE_GOLD` |
| 设计文件 | `docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md` |
| 协议状态 | `FROZEN_FOR_U1_D_PREGOLD_EXECUTION`；Gold evaluation 未批准 |
| 当前数据状态 | 4,500 queries / 143,820 units / 11,015 gold；R2 指标与确定性复跑已验证 |
| Stage3B | `KEEP_LOCKED` |
| Controller | 20 项 v2.1 合成硬化测试已通过；官方 U1-D 仅获批运行至 `VERIFIED_PRE_GOLD` |
| 当前 boundary-only 规则 | Stage2G 未支持，已停用 |

第一次官方提取在预注册映射硬门处停止：基础区间 `[800:5300)` 的 11,003 个 supporting facts 中有 19 个 sentence index 越界，影响 19 条查询；该失败没有生成 gain/harm 或检索指标。Amendment 1 随后采用仅由标注完整性决定的确定性替换，从 `[9800:9819)` 补入 19 条有效记录。最终 11,015/11,015 supporting facts 完整映射，development/reservation 零重叠。

Stage4A-R2 最终估计：q25 gain `94/4500 = 2.089%`，harm `69/4500 = 1.533%`，两者 Wilson 95% 区间半宽均通过 0.5 个百分点精度门。Dense/q25 CR@20 为 `0.77222/0.77778`；平均增益 `+0.00556`，exact McNemar `p=0.0598`，因此不能主张确认性平均 CR 提升。q25 false-insert rate 仍为 `0.92163`。

Stage4B-U1 v2 架构已获原则接受，但原执行包因 official boundary、配置冻结、独立复算、insert 推导、完整代码绑定、pre-Gold 门和 Stage4A-R2 基线等价门不足而退回。v2.1 不改变 score、q25 或 60% 预算，已通过 20 项合成测试，其中审批指定的 11 类失败注入全部被拒绝；批准现严格限于 official channel、Gold-free controller、工件冻结和 `VERIFIED_PRE_GOLD`。Gold evaluation、reservation 与 Stage3B 继续锁定。

## 研究问题

长期问题：

> 在证据密集型多跳问答中，粒球知识单元与跨粒球超边能否在保护强 dense 主干的同时，提高完整证据链召回，并用可验证的查询级决策控制扩展成本和风险？

当前 Stage4A-R2 只回答：

1. 官方 April 7 版 2WikiMultiHopQA 上 dense fixed 的 CR@20 是否饱和；
2. 冻结 q25、protect-10、insert-4 策略的 query-level gain/harm prevalence 是多少；
3. 这些事件率能否以预注册精度估计，为后续模型特定的 controller 设计提供依据。

Stage4A-R2 不优化阈值、不修复 boundary rule、不训练 controller，也不读取 Stage3B。

## 方法概览

- **知识单元**：将候选上下文句子嵌入后组织为自适应粒球。
- **高阶关系**：使用 query-aware facet hyperedge 表达跨粒球证据补全候选。
- **强基线保护**：保留 dense Top-10，仅允许最多 4 个扩展单元进入 Top-20。
- **冻结过滤**：迁移 Stage2E 产生并在 Stage2F 独立测试的 q25 score floor `0.1957079917192459`。
- **当前策略**：已验证基线为 all-query q25；Stage4B-U1 v2 设计定义连续边界不确定性、超边 readiness 与 60% planned-insert 预算的无标签组合。
- **当前主终点**：U1 gain/harm retention gap、相对 dense 的 CR@20 delta 与插入成本下降。

## 证据等级

| 阶段 | 证据等级 | 保留结论 |
|---|---|---|
| Stage0–Stage2E | 可复现探索性开发 | 生成机制与冻结候选，不作确认性主张 |
| Stage2F | 有限内部独立验证 | 主 CR@10 gate 失败；保留窄范围 q25/Top-20 证据 |
| Stage2G | 有效负结果 | 当前 boundary-only 规则不受支持 |
| Stage2H | 事后诊断 | 不产生替代阈值 |
| Stage3A | 失败的预注册开发 | 稀疏事件触发 fallback；Stage3B 不开放 |
| Stage3C | 描述性规划 | HotpotQA 有 gain，MuSiQue CR@20 饱和；20-event 仅为启发式 |
| 原 Stage4A | 已失效镜像 pilot | 不允许推断官方 2Wiki 可行性 |
| Stage4A-R2 | 官方内部验证完成 | 事件率精度达标；平均 CR 提升未确认；类型异质性明显 |
| Stage4B-U1 | v2.1 pre-Gold 执行批准 | 尚无官方 U1-D 指标；Gold evaluation 未授权 |

完整审计见 [`docs/PRIOR_STAGE_METHOD_AUDIT.md`](docs/PRIOR_STAGE_METHOD_AUDIT.md)，阶段历史见 [`docs/ROADMAP.md`](docs/ROADMAP.md)。

## 数据与来源边界

| 数据 | 用途 | 状态 |
|---|---|---|
| HotpotQA dev distractor | 早期开发与内部验证 | 固定镜像 SHA；官方字节等价性未认证 |
| MuSiQue answerable dev | 早期开发与内部验证 | 官方归档 |
| 2WikiMultiHopQA `data_ids_april7.zip` | Stage4A-R2 官方外部数据 | SHA-256 已冻结；本地数据不入 Git |

Stage4A-R2 样本量为 4,500；基础区间、替换规则、保留集和未使用区由协议及 Amendment 控制。Reservation 仅允许 ID digest，不允许内容文件、embedding 或指标。

## 仓库结构

```text
AGENTS.md      项目隔离、科研和 GitHub 治理约束
docs/          协议、审计、路线图和复现说明
reports/       阶段性研究报告
results/       可跟踪的汇总、query audit 和验证产物
scripts/       数据映射、检索、统计和独立验证脚本
README.md      当前项目入口；不承载全部历史细节
```

Raw data、processed corpus、embedding cache 和模型文件不进入仓库。

## 复现

验证过的实验解释器：

```text
D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe
```

完整命令、输入输出路径和期望 SHA 见 [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md)。核心 R2 脚本：

- `scripts/stage4a_r2_plan_sample_size.py`
- `scripts/stage4a_r2_extract_official.py`
- `scripts/stage4a_r2_official_estimation.py`
- `scripts/stage4a_r2_verify_outputs.py`

Stage4B-U1 当前仅有不访问 reservation 的功效规划入口：`scripts/stage4b_u1_plan_power.py`。

Gold-free v2.1 合成验证入口：`scripts/stage4b_u1_run_synthetic_verification.py`；当前审计见 `docs/STAGE4B_U1_IMPLEMENTATION_AUDIT_V2_1.md`，历史 v2 审计继续保留。

当前批准决定：`docs/STAGE4B_U1_EXECUTION_PACKAGE_V2_1_APPROVAL_DECISION.md`。授权仅覆盖官方 U1-D pre-Gold 通道、controller 与独立验证，不包含 Gold evaluation。

默认 Anaconda Python 3.11 当前存在 NumPy/二进制扩展不兼容，不作为本项目验证运行时。

## 科研治理

- 项目与其他项目会话隔离；禁止读取项目外会话或全局 Codex 记忆。
- 协议、样本量、主要终点和执行代码必须先提交 GitHub，再读取结果。
- Gold 标签禁止进入索引、候选选择、排序、过滤或检索决策。
- 硬失败不得自动放宽或重跑；必须形成 Amendment 并在重跑前提交。
- 失败、失效和负结果保留在历史中，不通过删除文件改写研究轨迹。
- 每个结果阶段必须独立复算并进行统计解释与 11 类谬误检查。

详细约束见 [`AGENTS.md`](AGENTS.md)。

## 已知限制

- 当前方法只评估检索，不含生成器答案质量。
- q25 阈值来自原始两数据集，不能声称对 2Wiki 最优。
- Stage4A-R2 使用确定性数据边界和标注完整性 QC，推断范围需按最终来源审计限定。
- 当前没有经过验证的 query-level boundary/controller。
- Stage4B-U1 v2 是有限 benchmark batch 的启发式资源分配设计，尚不能主张为在线逐查询 controller。

## 下一步

1. 提交推送批准治理状态，并在新协议字节上重跑 20 项 synthetic binding verification。
2. 运行一次 official U1-D channel 和 Gold-free controller，提交 policy/ranking/decision 后独立生成 `VERIFIED_PRE_GOLD`。
3. 推送 `VERIFIED_PRE_GOLD` 后立即停止；Gold evaluation、reservation 与 Stage3B 继续锁定并等待独立审批。

## GitHub

仓库：<https://github.com/lljjcc426/HyperGranular-RAG>

重要协议、失败审计、修订、验证结果和阶段状态均按里程碑同步到 `main`。
