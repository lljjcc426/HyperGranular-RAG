# 超粒球RAG Stage4B-U1-D Gold 评估与统计验证报告

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validate
- Origin Date: 2026-07-18
- Verification Status: `VERIFIED`
- Version Label: `stage4b_u1_d_gold_validation_v1`
- Scientific protocol: `docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md`
- Execution protocol: `docs/STAGE4B_U1_SIMPLIFIED_EXECUTION_PROTOCOL_V1.md`
- Gold authorization binding: commit `1bfcf7b108dd4a8db17ba97a4d3b97a6f274f983`
- Result generation commit: `c06761f0c55cbeecf75564211a59f4540cfbae06`
- Summary byte-preservation correction: `b500184bc581d73a381de65c32cf3b72e9758cc9`
- Evidence boundary: current conversation, current repository, registered `E:\科研\超粒球RAG_数据` data root, and frozen project artifacts
- Other project conversations, global memory, reservation metrics, and Stage3B used: No

## Validation Report

- Source: `stage4b_u1_d_official_dev4500_simplified_v1_gold_evaluation`
- Overall Confidence: `CAUTION`（总体停止决定在当前 development batch 内为 `SOLID`；类型区间报告与跨数据外推仍受限）

### Validation Verdict

- Computational integrity: `PASS`.
- Deterministic reproducibility: `REPRODUCIBLE`，主运行与复跑同字节。
- Development advancement: `FAIL`，6 项冻结门通过 2 项、失败 4 项。
- Frozen decision: `STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED`.
- Confidence in the negative stop decision: `SOLID` within the audited 4,500-query development batch.
- Generalization confidence: `CAUTION`；不能外推到 reservation、其他数据集或在线系统。
- Reporting completeness: `CAUTION`；冻结 evaluator/validator 缺少协议要求的 question-type 区间。

这是有效的科研负结果，不是运行失败：U1-D 当前冻结形式未获得支持。U1 达到了资源削减门，但没有证明其更偏向保留 gain 而不是 harm，且 CR@20 未满足相对 Dense 和 q25 的冻结要求。

## Authorization And Gold Isolation

- 用户授权范围仅为 Stage4B-U1-D development Gold evaluation；reservation 未授权。
- Decisions、rankings、policy 和 `VERIFIED_PRE_GOLD` 在 Gold evaluator 连接前已冻结并提交。
- Gold map 只由 evaluator 使用，没有进入索引、候选、粒球、超边、ECDF、score、budget、ranking 或 controller。
- Ranking、policy 和 pre-Gold verification SHA-256 分别为 `ED289D23...E03CB`、`657E5F25...D868B` 和 `39EAD86A...D7818`。
- Stage4A-R2 baseline equivalence 通过：4,500 queries、Dense CR@20 `0.772222`、q25 CR@20 `0.777778`、94 gains、69 harms 均与冻结参考一致。

## Execution And Independent Verification

| Check | Result |
|---|---|
| Primary evaluation | exit 0；51.6 秒 |
| Deterministic rerun | exit 0；56.9 秒 |
| Query-audit byte equality | PASS；两份均 2,600,121 bytes / `8616C28C...F938313` |
| Summary byte equality | PASS；两份均 7,662 bytes / `7F82056F...7F89DE` |
| Query audit independent recomputation | PASS；4,500/4,500 |
| Overall and type point-summary recomputation | PASS |
| Advancement-decision recomputation | PASS |
| Bootstrap identity | PASS；10,000 iterations / seed `20260712` |
| `VERIFIED_POST_GOLD` | 2,293 bytes / `44BF3E8B...20ECD` |
| Summary Git byte binding | PASS；local/index/commit/GitHub 均 7,662 bytes / `7F82056F...7F89DE` |

独立验证器不导入 evaluator。它从冻结 ranking、policy、pre-Gold verification 和 Gold map 重建逐查询记录、总体汇总、类型点估计、基线等价与决策。

初始结果提交 `c06761f...` 受本机 `core.autocrlf=true` 影响，将两份 summary 的 CRLF tracked blob 规范化为 LF。发现后按正式工件不一致边界暂停；授权修复 `b500184...` 只增加两个精确 `-text` 路径并重新加入现有原始字节。其他三个 Gold 工件、rankings、policy 和 pre-Gold verification 均未改变。

## Frozen Development Gates

| Gate | Frozen threshold | Observed | Margin to threshold | Result |
|---|---:|---:|---:|---|
| Inserted-unit reduction | >= 0.400000 | 0.400275 | +0.000275 | PASS |
| Gain retention - harm retention | >= +0.150000 | -0.268116 | -0.418116 | FAIL |
| One-sided Fisher exact | p < 0.050000 | p = 0.999889 | — | FAIL |
| U1 CR@20 delta vs Dense | >= +0.005000 | -0.001333 | -0.006333 | FAIL |
| U1 CR@20 delta vs q25 | >= -0.005000 | -0.006889 | -0.001889 | FAIL |
| Conditional false-insert-rate delta | <= +0.010000 | +0.002582 | 0.007418 headroom | PASS |

Gold isolation、ranking-subset validation、independent verification 和 deterministic rerun 也均通过，但冻结规则要求所有发展门同时通过。4 项失败已经充分触发停止决定，不能由 2 项通过抵消。

## Statistical Findings

### Selection mechanism

- q25 gain events：94；U1 retained gains：47；gain retention：`0.500000`。
- q25 harm events：69；U1 retained harms：53；harm retention：`0.768116`。
- Retention gap：`-0.268116`，10,000 次 paired query bootstrap 95% percentile interval `[-0.409057,-0.118309]`。
- 一侧 Fisher exact 检验的零假设是 gain retention 不高于 harm retention；`p=0.999889`，不能拒绝零假设。

区间整体位于 0 以下，点估计也远低于预注册的 `+0.15` 实际意义门。正确解释是“冻结 U1 没有表现出预期的 gain-over-harm 选择性”，而不是 Fisher 检验证明 gap 等于某个负值。

### Retrieval outcome

| Strategy | ER@20 | CR@20 | Inserted units |
|---|---:|---:|---:|
| Dense | 0.898204 | 0.772222 | 0 |
| all-query q25 | 0.902270 | 0.777778 | 7,260 |
| U1 | 0.898815 | 0.770889 | 4,354 |

- U1 vs Dense CR@20 delta：`-0.001333`；bootstrap 95% interval `[-0.005778,0.003111]`。
- U1 vs q25 CR@20 delta：`-0.006889`；bootstrap 95% interval `[-0.010444,-0.003333]`。
- U1 vs Dense discordances：47 gains、53 harms；two-sided exact McNemar `p=0.617299`。

McNemar p-value 在 U1-D development 决策中不是独立晋级门，只作描述性核对。`p=0.617299` 不能解释为两策略等价；观察 delta 和冻结实际意义门已经独立判定失败。

### Cost and insertion noise

- U1 比 q25 少插入 2,906 units，减少 `40.0275%`，仅比 40% 门高 `0.0275` 个百分点。
- q25 inserted gold/non-gold units：569/6,691；conditional false-insert rate `0.921625`。
- U1 inserted gold/non-gold units：330/4,024；conditional false-insert rate `0.924208`。
- U1 false-insert rate 相对 q25 增加 `0.002582`，未超过允许的 `0.01`。

资源削减和 false-insert-rate 门通过，但两者不证明检索效益。两种扩展策略的插入仍以 non-gold units 为主。

## Descriptive Question-Type Audit

| Type | n | Gain retention | Harm retention | Gap | U1-Dense CR@20 | U1-q25 CR@20 | Insert reduction | Protocol caution |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| bridge_comparison | 1,001 | 0.5143 | 0.7000 | -0.1857 | +0.0040 | -0.0110 | 0.3558 | No |
| comparison | 1,132 | 0.5484 | 0.8333 | -0.2849 | +0.0106 | -0.0115 | 0.3994 | No |
| compositional | 1,789 | 0.3913 | 0.7692 | -0.3779 | -0.0061 | -0.0045 | 0.4523 | Yes：20 harms > 9 gains |
| inference | 578 | 0.6000 | 0.8235 | -0.2235 | -0.0190 | +0.0017 | 0.3748 | Yes：14 harms > 3 gains |

四类 retention gap 均为负；CR@20 方向存在异质性。`compositional` 和 `inference` 的 `SUBGROUP_CAUTION` 与冻结 summary 一致。这些行是描述性风险审计，不支持类型特异性 efficacy 主张，也不能作为事后 controller 规则。

### Reporting-completeness caution

科学协议第 259–263 行要求按 question type 报告点估计与区间，但冻结 evaluator 和独立 validator 只生成、重算了点估计和 caution 标记。Gold 已读取后再选择一种未冻结的类型级区间算法会引入研究者自由度，因此本报告不事后补算。该缺口限制类型层解释，但不影响总体四个失败门或 `STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED`。

## Assumptions And Multiplicity

- Pairing：Dense、q25 和 U1 在同一 4,500 queries 上逐查询比较。
- Query identity：独立验证确认 4,500 条 row identity 与 frozen query 一致。
- Fisher：使用 94 gain 与 69 harm 条件事件中的 retained counts；没有使用大样本近似。
- McNemar：对 U1 vs Dense 的 47/53 discordances 使用 exact two-sided test。
- Bootstrap：以 query 为重采样单位，10,000 次、冻结 seed；共享 benchmark contexts 仍可能使严格独立性只是近似。
- Multiplicity：development 晋级是预注册的全条件联合门，不从多个结果中挑选显著项；question-type p-values不作总体结论。summary 中的类型 McNemar/Fisher 值保持描述性，未进行多重比较校正。
- Effect size：本研究使用预注册的绝对 retention/CR/resource 门，不以事后标准化效应等级替代实际意义门。

## Statistical Fallacy Scan

Coverage: 11/11 checked.

| Fallacy | Result | Detail |
|---|---|---|
| Simpson's paradox | Not detected; heterogeneity caution | Retention gap 在总体与四类型均为负；CR 方向混合，但不存在所有分层方向与总体完全反转。必须同时保留总体与分层事实。 |
| Ecological fallacy | Not detected | 主要门以 query 为分析单位；类型汇总未用于推断单个 query 必然受益。 |
| Berkson's paradox | CAUTION boundary | 样本是经审计的官方 development QC batch；选择边界限制外推，但本报告不作相关性主张。 |
| Collider bias | Not detected | 没有拟合因果调整模型或控制共同结果变量。 |
| Base-rate neglect | Avoided | 同时报告 gain/harm 基数、retention 分母、gold/non-gold 插入和 false-insert rate。 |
| Regression to the mean | Not applicable | 没有按极端结果选择 pre/post 组。 |
| Survivorship bias | Not detected | 4,500/4,500 queries 进入主运行和复跑；没有未披露 attrition。 |
| Look-elsewhere effect | Avoided for decision | 所有晋级门在 Gold 前冻结；没有从类型结果中挑选一个替代总体失败。 |
| Garden of forking paths | Controlled; reporting caution | 方法、阈值、seed 和停止规则先于结果提交；类型区间方法未冻结，因此没有在 Gold 后补算。 |
| Correlation implies causation | Boundary enforced | 这是同一 benchmark 上冻结检索策略的配对比较，不支持真实世界 RAG 或生成质量的因果主张。 |
| Reverse causality | Not applicable | 没有横截面方向性因果模型。 |

## Reproducibility Verdict

- Method: deterministic rerun with identical code, data identities, parameters and seed; only output paths differ.
- Verdict: `REPRODUCIBLE`.

| Artifact | Primary | Rerun | Diff | Status |
|---|---|---|---:|---|
| Query audit | `8616C28C...F938313` | `8616C28C...F938313` | 0 bytes | MATCH |
| Evaluation summary | `7F82056F...7F89DE` | `7F82056F...7F89DE` | 0 bytes | MATCH |

### Non-scientific diagnostic anomalies

- 两次只读 PowerShell hash-format 辅助命令因 `EmptyPipeElement` 解析错误退出；修正后的只读命令通过，未修改实验工件。
- 一次 PowerShell 内存 HTTP 远端核验命令被本地策略在执行前拦截；随后使用 GitHub `fetch_file` 读取同一 commit blob并完成 bytes/SHA 核验，无项目写入。
- `git diff --check` 将冻结 CRLF 中的 `CR` 报为 trailing whitespace；该非零结果是 `-text` 原始字节保护的表现，没有据此改写 summary。
- 首次文档提交范围检查使用 Git 默认的 Unicode 转义路径与字面路径比较，产生一次假 `STAGED_SCOPE_MISMATCH`；改用 `core.quotepath=false` 后精确六路径检查通过，未改变 staged scope。

完整 SHA、bytes、命令和输入身份见 `docs/REPRODUCIBILITY.md` 与 `configs/stage4b_u1_d_gold_evaluation.json`。

## Permitted Conclusions

1. 冻结 U1 controller 在审计的 4,500-query development batch 上把 q25 插入成本降低了约 40%。
2. U1 保留 harm 的比例高于保留 gain 的比例，未通过机制 gap 和 Fisher 门。
3. U1 CR@20 低于 Dense 与 all-query q25 的观察值，未通过两个 development CR 门。
4. 该结果按预注册规则停止 U1 分支并保持 reservation 锁定。
5. 计算结果具有同字节复现和独立重算证据；类型级区间缺失必须作为报告限制保留。

## Prohibited Interpretations And Next Boundary

- 不得把资源门通过解释为 U1 总体有效。
- 不得把当前 U1-D 的失败外推为 HyperGranular-RAG 整体无效。
- 不得把非显著 p-value解释为策略等价。
- 不得从描述性类型结果构造事后类型规则并在同一 development 上重跑。
- 不得访问 reservation 或 Stage3B，也不得将本结果视为其授权。
- 后续若提出新 controller，必须视为新的科学语义，先提出新的问题、development 边界、主要终点和停止规则并提交新协议；本次 U1-D transaction 不再重复。
