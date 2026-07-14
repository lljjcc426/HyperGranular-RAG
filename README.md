# HyperGranular-RAG

以自适应粒球为知识单元、以超边表达跨粒球高阶关系，并通过受保护插入控制检索扩展的多跳 RAG 研究仓库。

## 当前状态

| 项目 | 状态 |
|---|---|
| 当前阶段 | Amendment 5D-A 已完成 synthetic 验证；implementation/evidence 等待提交 |
| 获批执行协议 | 5D-A implementation/synthetic 范围已消费；无 official execution 授权 |
| 设计文件 | `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_A_IMPLEMENTATION_AUDIT.md` |
| 协议状态 | `AMENDMENT_5D_A_SYNTHETICALLY_VERIFIED` |
| 当前数据状态 | 4,500 queries / 143,820 units / 11,015 gold；R2 指标与确定性复跑已验证 |
| Stage3B | `KEEP_LOCKED` |
| Controller | v2.3.1 单次运行在 pending decisions 的 v2.2 字节等价门停止；未提升正式工件 |
| 当前 boundary-only 规则 | Stage2G 未支持，已停用 |

第一次官方提取在预注册映射硬门处停止：基础区间 `[800:5300)` 的 11,003 个 supporting facts 中有 19 个 sentence index 越界，影响 19 条查询；该失败没有生成 gain/harm 或检索指标。Amendment 1 随后采用仅由标注完整性决定的确定性替换，从 `[9800:9819)` 补入 19 条有效记录。最终 11,015/11,015 supporting facts 完整映射，development/reservation 零重叠。

Stage4A-R2 最终估计：q25 gain `94/4500 = 2.089%`，harm `69/4500 = 1.533%`，两者 Wilson 95% 区间半宽均通过 0.5 个百分点精度门。Dense/q25 CR@20 为 `0.77222/0.77778`；平均增益 `+0.00556`，exact McNemar `p=0.0598`，因此不能主张确认性平均 CR 提升。q25 false-insert rate 仍为 `0.92163`。

Stage4B-U1 v2 架构已获原则接受，但原执行包因 official boundary、配置冻结、独立复算、insert 推导、完整代码绑定、pre-Gold 门和 Stage4A-R2 基线等价门不足而退回。v2.1 不改变 score、q25 或 60% 预算，已通过 20 项合成测试，其中审批指定的 11 类失败注入全部被拒绝；批准现严格限于 official channel、Gold-free controller、工件冻结和 `VERIFIED_PRE_GOLD`。Gold evaluation、reservation 与 Stage3B 继续锁定。

Amendment 1 批准治理状态提交后，20 项 synthetic binding verification 连续两次字节一致，历史 checkpoint SHA-256 为 `9AA0D0499ECF613F7FEAED0F078BB7534CB837C22465AA1F13F29D715BBE8A6A`。该复跑没有访问 official development、official source audit、reservation 或 Stage3B。

正式 preflight 随后发现旧 Stage4A-R2 embedding cache 缺少 `unit_ids`、`query_ids` 和 `max_length`，无法满足 v2.1 的 ID-bound cache 硬门，因此执行立即停止。没有生成 official channel、Gold map、decision、ranking、policy、`VERIFIED_PRE_GOLD` 或任何 U1-D 指标。失败审计见 `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_1.md`。Amendment 1 已批准：旧 cache 原样保留，获批后只允许在新路径单次生成并独立核查 ID-bound cache。

Amendment 1 后的正式 preflight 又在 query-ID digest 硬门停止：source audit 的 `6B21...` 绑定原始 `sample_id`，processed runtime `query_id` 是 `2wikimultihopqa::<sample_id>`，其结构性 digest 为 `8895...`；v2.1 错误地直接比较了不同 ID 表示。其余 preflight 门全部通过，未生成 channel、cache 或 official 工件。失败审计见 `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_2.md`，最小修订见 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_2_DRAFT.md`。

Amendment 2 实现将 checkpoint 更新为 `stage4b_u1_v2_2`，分别冻结 sample-ID 与 runtime query-ID digest，并在 preparer/controller/verifier 中逐条检查 `query_id == dataset::sample_id`。原 20 项测试全部保留，新增 4 项失败注入后共 24 项全部通过；最终 binding evidence 连续两次 SHA-256 均为 `8B3057238D67EBE874017068C125126974062C61FAF3D79595E884F16A876D7D`。official development、source audit、reservation 与 Stage3B 均未被测试访问。

用户已批准 v2.2 official pre-Gold 恢复，绑定审批包提交 `fae181564504f1a69bcebfd5d5201eea7e2d9abf` 与实现提交 `ca2cca332292f7bd6af12e2a429100be11da5549`。批准顺序只到 `VERIFIED_PRE_GOLD` 且 `evaluation=null`；Gold evaluation、U1-D 指标、reservation 与 Stage3B 继续锁定。

批准治理提交 `c13be1f` 推送后，24 项 synthetic binding verification 在新治理字节上完整运行两次，两次均为 24/24 且输出 SHA-256 均为 `9B01C80F66096F01C763C25E44E4D079C40B681F6C52F0CC55F70492689EAAB1`。两次运行均未访问 official development、official source audit、reservation 或 Stage3B。审计见 `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_2_SYNTHETIC_REBINDING_AUDIT.md`。

一次 dual-ID formal preflight 与一次 official channel preparation 均通过。随后单次 Gold-free controller 以冻结 MiniLM `192/64` 生成 4,500 条 decisions/rankings 和 fresh ID-bound cache；policy 报告 `evaluation_labels_loaded=false`。独立只读 cache 核查确认成员、ID 同序、双 digest、形状、dtype、有限值、归一化、bytes 与 SHA 全部门通过。该时点尚未运行 independent verifier，也未进行 Gold evaluation 或指标解释。

independent verifier 随后在已提交工件上单次运行，并因固定要求列表长度恰好为 20 而硬失败。official development 中 628 个查询的候选池少于 20，controller 对全部 4,500 条查询都产生了长度 `min(20, num_candidate_units)` 的列表；首个失败查询候选数与列表长度均为 17。`VERIFIED_PRE_GOLD` 未生成，Gold/evaluator 参数未传入。失败审计见 `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_3.md`，effective-K 最小修订草案见 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_DRAFT.md`。

Amendment 3 已获 implementation/synthetic-only 批准，绑定审批包提交 `42747507d6f37c3d5713949de443311b35262a2d` 与失败审计提交 `8b43de72418ccda85af3015f758c39bce9d31411`。批准只允许冻结 `K_q=min(20,|C_q|)`、`P_q=min(10,K_q)`，更新 v2.3 verifier 与 synthetic tests；不授权任何 official 数据读取或命令。

Amendment 3 已按批准边界实现：checkpoint 为 `stage4b_u1_v2_3`，verifier 独立检查 effective-K 长度、唯一性、候选成员、protected prefix、insertion 推导和 final selector。原 24 项测试保留，新增 9 项后共 33 项全部通过；完整 evidence runner 连续两次输出字节一致，SHA-256 均为 `38DDA409C866AAAC6C2AEDBA0D0716DA6F483854E9A6019E9040B9B2B1FA40B5`。全过程未访问 official development、source audit、official ranking、cache、Gold、reservation 或 Stage3B。实现审计见 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_IMPLEMENTATION_AUDIT.md`。

v2.3 official-resumption 包 `dbb4e057...` 经审查退回：缺少批准治理后的 synthetic rebinding、十项新工件准确路径，以及 controller 内 cache require-existing/no-build 与前后 SHA 门。代码核查确认当前 cache 缺失会进入编码写入分支，因此不能仅靠文字 preflight 修复。审查见 `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_REVIEW_1.md`；新的 Amendment 4 仅申请 cache fail-closed 与恢复协议 hardening 的 implementation/synthetic 授权，不申请 official execution。

Amendment 4 已获 implementation/synthetic-only 批准，绑定 package `e5a0e218...`、returned package `dbb4e057...` 和 baseline implementation `a1d9ea0c...`。批准只允许 checkpoint `stage4b_u1_v2_3_1`、existing-cache-only、前后指纹、pending outputs、governance rebinding、十路径 registry 和 synthetic tests；official 数据、真实 cache 和全部 official 命令继续锁定。

Amendment 4 实现已完成：formal controller 强制 existing-cache-only 与冻结 SHA，严格核验 cache 内容并在 OS 临时目录生成 pending outputs；cache 后指纹、v2.2 decisions/rankings bytes 和限定 policy diff 全部通过后才提升，复制或后指纹失败会回滚本次输出。runner 支持登记治理文件绑定，manifest/shared constants 的十路径逐项一致。原 33 项测试保留，新增 17 项后共 50 项全部通过；两次完整 evidence SHA-256 均为 `24F287F9B71C974ABEF9E03AA55BCCA0C4AF9809AB2ADC44705A42EC3889F657`。实现审计见 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_IMPLEMENTATION_AUDIT.md`。

Amendment 5A 已按批准边界实现，未修改 controller。新增 decisions-only 七层 comparator、synthetic allowlist 与临时 decisions capture；5B 组包前静态核查又补齐 official 精确路径、登记 source digest、OS temp、v2.2 reference SHA 与 cache 后指纹门。48 项新诊断测试与原 50 项合计 98 项全部通过。完整 evidence 连续两次输出字节一致，SHA-256 均为 `3D44C14B82E911DDD37501731772A7594D7616BF12FE278D2D4CCC103533057E`，official 路径访问尝试为 0。实现审计见 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_IMPLEMENTATION_AUDIT.md`。这不授权 official 诊断、controller 重跑或 verifier。

Amendment 5B 审批包 commit `ceb755252540cf223aa18ac721443154c29cd07a` 已退回：units、queries 和 controller channel audit 只有路径与内部自洽校验，没有由 package 外部冻结各自 SHA-256。当前禁止使用 5B token、运行 preflight/capture、重跑 controller 或运行 verifier。退回记录见 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_REVIEW_1.md`。

Amendment 5A.1 仅申请实现与 synthetic 验证三项 channel-input SHA 前后硬门；冻结值分别为 units `114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA`、queries `6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B`、controller channel audit `D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA`。请求与 Manifest 见 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_1_APPROVAL_REQUEST.md`、`docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_1_MANIFEST.json`；在 package-bound 明确批准前不得修改实现或运行 synthetic。

Amendment 5A.1 已按批准范围实现：capture 要求三个 expected-SHA 参数，official 路径在语义解析/cache/计算前逐项核验普通文件、外部冻结值和实际 SHA，并在临时 decisions 比较与清理后、audit exclusive-create 前再次核验。原 98 项测试全部保留，新增 9 项后完整 suite 为 107 项；两次最终 evidence 均为 107/107、零 failure/error/skip/official access，20,495 bytes 且 SHA-256 均为 `81A8A5960395F729B643A42505E7F947962B338CD97ADD0506636D3AA2020A67`。审计见 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_1_IMPLEMENTATION_AUDIT.md`。这不授权 official 诊断或恢复 Hard Failure 4。

新版 Amendment 5B v2 包已组装，严格绑定 5A.1 implementation/evidence commit `e566eb861ec6028ca89a40c9aca7d06737f1eb8e`、evidence SHA 和三项 channel-input 外部 SHA。请求仅覆盖批准治理后的 107 项双次 rebinding、一次只读 preflight、一次 decisions-only capture、聚合审计提交与立即停止。请求与机器边界见 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_V2_OFFICIAL_DIAGNOSTIC_APPROVAL_REQUEST.md`、`docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_V2_MANIFEST.json`；在明确绑定 v2 package commit 的批准前不得运行。

5B v2 获批后，两次 107 项 rebinding 与唯一一次只读 preflight 全部通过。唯一一次 exact-command capture 随后在 comparator 读取冻结 v2.2 reference decisions 时因 `Incomparable heterogeneous decisions schema at line 2` 硬失败；没有产生聚合 machine audit，不能判断 byte/canonical/semantic 差异。临时 decisions 已清理，channel/cache/reference hash 与 cache bytes 不变，正式 outputs 仍不存在。失败审计见 `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_5.md`；任何后续 schema 诊断或重跑必须另行批准。

Hard Failure 5 的独立审查已退回 schema 诊断执行请求：当前只允许准备 Amendment 5C-A 治理包。该包申请新增独立、只读、value-free 的 JSONL schema inventory 工具和 synthetic 验证；现有 comparator/capture/controller 全部冻结。原 107 项测试必须保留，至少新增 12 项后完整 suite 不少于 119 项并连续两次字节一致。审查和申请分别见 `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_5_REVIEW_1.md` 与 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_APPROVAL_REQUEST.md`；在明确绑定 5C-A package commit 的批准前不得实现或运行。

Amendment 5C-A 现已获 implementation/synthetic-only 批准，绑定 package commit `a8caa2a3b26ae13d0b149e4995e3a017e8edb2e7`。授权仅覆盖三个全新独立文件、至少 119 项完整 suite 的两次 deterministic 验证、implementation audit/evidence 和未来 5C-B 组包。Official reference、既有 comparator/capture/controller、Gold、reservation 与 Stage3B 继续锁定。批准决定见 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_APPROVAL_DECISION.md`。

5C-A 已按批准边界实现：新增独立 value-free schema inventory、deterministic runner 和 24 项 tests，现有 107 项全部保留，完整 suite 共 131 项。最终治理绑定的两次完整运行均为 131/131、零 failure/error/skip/official access；两份 evidence 均为 22,234 bytes、SHA-256 `0D13392B5C96BAD7EC4D67C22A7515B4A6D211C8EFBB3A4486F9BA5531A1EF7C`，逐字节一致。所有冻结实现/测试 SHA 未变化，official reference 未打开。实现审计见 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_IMPLEMENTATION_AUDIT.md`。

Implementation-bound Amendment 5C-B 包已组装，请求仅在新批准后依次执行批准治理、双次 131 项 synthetic rebinding、governance binding、一次 SHA-only preflight、一次 exact-command value-free reference schema scan、聚合审计提交和立即停止。唯一输入冻结为 v2.2 reference decisions 及 SHA `6FB6...23C7`；其他 official 文件、字段值/ID、comparator/capture/controller/verifier/Gold 全部禁止。Request/Manifest 分别为 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_B_OFFICIAL_SCHEMA_SCAN_APPROVAL_REQUEST.md` 与 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_B_MANIFEST.json`。

5C-B 获批后，两次 131 项 post-approval rebinding 均全通过且 evidence 字节一致；唯一一次 SHA-only preflight 全部门通过。唯一一次 exact-command scan 对 4,500 行 reference decisions 生成 value-free schema inventory：共有 2 个 ordered/structural schemas，行数分别为 2,446 与 2,054；字段集合、顺序和嵌套无差异，异质性集中在 8 个字段的 `integer/finite_number` 与 `null` 类型差异。Machine inventory SHA-256 为 `FA56AC3CB78EE746BF71AF0CEF40606E56B9D13C120F10A2A87400EA42CE3A5E`。审计见 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_B_OFFICIAL_SCHEMA_SCAN_AUDIT.md`；这不授权 normalization、capture/controller 重跑、verifier 或 Gold。

5C-B 独立审核已接受并确认 Hard Failure 5 的直接原因：comparator 在文件加载阶段要求所有行完整 JSON 类型签名同构，而 nullable schema 首次出现于第 2 行，精确触发 line-2 拒绝。Hard Failure 4 仍未分类，因为 5C-B 未生成或比较 temporary decisions。新的 5D-A 包只申请移除该全文件同构前置拒绝、保持逐 query 比较与 raw-byte 主门，并以至少 143 项 synthetic suite 验证；在 package-bound 批准前不得修改 comparator 或运行测试。

5D-A 已按批准范围实现：comparator 只更新至 v2 并删除 loader 的 `file_schema` 同构拒绝，逐 query 比较代码未修改；runner 增加 5D-A governance/frozen-hash/official-path 门；diagnostic tests 净新增 12 项。最终完整 suite 连续两次均为 143/143、零 failure/error/skip/official access，29,643 bytes，SHA-256 `08695B4305D9919049DFE86870772B9E9F66751DA6D2FF4D43CEF2A912A62008`，逐字节一致。这不完成 Hard Failure 4 诊断，也不授权 5D-B、capture/controller、verifier 或 Gold。

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
| Stage4B-U1 | 5F-A 审批包待审 | Hard Failure 7 审计已接受；当前仅组装 typed capture-argument policy implementation/synthetic-only 包，未授权实现或执行 |

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

5E-A helper 与 5E-B post-approval rebinding 均通过 161 项双轮确定性验证。5E-B 唯一 formal preflight 的 A 门通过，但 B 门使用裸 `gold` 子串扫描，误命中冻结 machine audit 路径中的 `pregold` 并触发 Hard Failure 7；C helper、D official inputs、token 与 capture 均未运行。Hard Failure 7 Review 1 已接受该审计；5F-A request/Manifest 仅申请 typed argument-policy helper 的实现与 synthetic 验证权限。

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

1. 独立审核 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5F_A_APPROVAL_REQUEST.md` 与对应 Manifest。
2. 未获明确绑定 5F-A package commit 的批准前，不得创建 helper/test、修改 runner 或运行 synthetic suite。
3. Official metadata/content、real OS-temp helper check、preflight、token、capture、controller、verifier、Gold、U1-D 指标、reservation 与 Stage3B 继续锁定。

## GitHub

仓库：<https://github.com/lljjcc426/HyperGranular-RAG>

重要协议、失败审计、修订、验证结果和阶段状态均按里程碑同步到 `main`。
