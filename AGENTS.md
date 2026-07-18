# HyperGranular-RAG 项目约束

本仓库继承 `E:\科研\AGENTS.md` 的全部规则；冲突时采用更严格的规则。

## 1. 项目范围

- 仓库：`E:\科研\HyperGranular-RAG`
- GitHub：`https://github.com/lljjcc426/HyperGranular-RAG.git`
- 登记数据根目录：`E:\科研\超粒球RAG_数据`
- 研究范围：粒球/超边多跳检索、q25 扩展、U1 无标签 controller、独立验证与后续 Gold-only 评估。
- 禁止读取其他项目会话、全局 Codex memory 或项目外中间产物。

## 2. 当前权威入口

- 当前项目状态：`README.md`
- 文档导航：`docs/INDEX.md`
- 当前复现边界：`docs/REPRODUCIBILITY.md`
- 完整研究时间线：`docs/ROADMAP.md`
- 当前科学/执行协议：`docs/STAGE4B_U1_SIMPLIFIED_EXECUTION_PROTOCOL_V1.md`
- 冻结配置：`configs/stage4b_u1_d_official.json`

历史 Amendment、Approval、Review、Hard Failure 和 PowerShell 执行文件是不可改写的证据，不是当前日常执行规则。不得从历史文件恢复已退役的 launcher、remote gate、observer、stderr framing 或 nested PRE 链。

## 3. 当前科研状态

```text
LEVEL_B_IMPLEMENTATION_ACCEPTED
VERIFIED_PRE_GOLD_COMMITTED
GOLD_EVALUATION_REQUIRES_PAUSE
RESERVATION_REQUIRES_PAUSE
SCIENTIFIC_SEMANTIC_CHANGE_REQUIRES_PAUSE
```

- Controller 三工件提交：`9357c157217f85008fa93df07d321a2f4c6a2bc1`。
- `VERIFIED_PRE_GOLD` 提交：`83d172bc89efbb31782eee308bac5293aa24457b`。
- Verified 文件 SHA-256：`39EAD86A3A835983DCB67BAF656255F51569BCEE5B9AC2E16FACF404281D7818`。
- Gold query audit 与 evaluation summary 尚不存在。
- Pre-Gold 结果只证明工件/实现完整性，不证明 U1-D 有效。

## 4. 科研不可变边界

未经新的 Level A 协议或明确授权，不得修改或事后选择：

- development/reservation 数据边界；
- 候选生成、粒球、超边或 facet；
- Dense/q25 ranking、q25 floor、protect/insert、effective-K；
- U1 输入、ECDF、score、tie-break 或 60% budget；
- 主要终点、统计检验、bootstrap、确定性复跑或晋级门；
- 已冻结 decisions、rankings、policy、`VERIFIED_PRE_GOLD`。

Gold 不得进入 controller、索引、候选、排序、过滤或阈值选择。Reservation 和 Stage3B 继续锁定。

## 5. 授权与暂停

Level B/C 的普通工程工作、测试、文档、提交和推送不逐项暂停，也不建立逐提交审批链。根据变更影响自主完成最小修正、适量测试、必要绑定与 GitHub 同步。

必须暂停并报告：

1. 准备连接或运行 Gold evaluator；
2. 准备读取 reservation 或 Stage3B；
3. 准备改变科学语义、数据边界、终点或统计规则；
4. 发现错误 official 输入/cache、Gold 泄漏、不可信 ranking；
5. 正式输出部分生成且不能可靠回滚，或本地/tracked/remote 工件字节不一致；
6. verifier 无法确认正式工件完整性。

临时 push/remote visibility、路径、权限、日志、依赖或零正式输出时的普通 preflight 错误默认是 Level C，不自动升级为科研 Hard Failure。

## 6. 测试与执行

- 科学算法变化：完整相关 suite，并按协议执行关键确定性验证。
- Ranking/verifier/schema 变化：定向测试 + 一次完整 `test_stage4b_u1*.py` suite。
- 文档、索引、README、普通路径或日志变化：静态检查即可，不运行算法 suite。
- 禁止为形式性治理重复运行完整 suite。
- 禁止盲目重复未变化的失败命令；先诊断和修正再继续。
- 不自行重新运行已完成的 official pre-Gold transaction。

## 7. GitHub 与文件

- 科研协议、代码、结果、独立验证和阶段状态按单一职责提交并推送 `main`。
- 不提交 raw/processed 数据、embedding、模型、缓存、密钥或临时文件。
- 不改写 Git 历史掩盖失败；失败和负结果保留在 `docs/ROADMAP.md`、历史证据文件与 Git 历史。
- README 保持简洁和当前；详细历史不再追加到 README。
- 新增、修改、移动、归档和删除文件都必须向用户说明。

## 8. 下一科研门

当前只能整理仓库、核验 pre-Gold 工件和规划后续工作。实际 Gold evaluation 必须等待用户单独明确授权；授权前不得读取 Gold、运行 evaluator、解释 U1-D 指标或修改冻结 ranking。
