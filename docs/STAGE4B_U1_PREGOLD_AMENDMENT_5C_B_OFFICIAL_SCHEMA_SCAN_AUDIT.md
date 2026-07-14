# Stage4B-U1-D Pre-Gold Amendment 5C-B Official Schema Scan Audit

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-14
- Package commit: `e5a6c5479dbd125ebb58b95e9594fadde6b6719d`
- Approval governance commit: `fce67da87d155b1026cbe0670f606201ede0ac4b`
- Post-approval rebinding/governance commit: `b09668f47cd31df2be73446cadacf84d996418f9`
- Status: `REFERENCE_DECISIONS_SCHEMA_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW`
- Other project conversations, thread tools, and global memory used: No

## 授权与前置门

5C-B 批准决定严格绑定 package commit `e5a6c547...`、5C-A implementation/evidence commit `492a59b2...` 及批准决定登记的历史提交。批准治理先以 commit `fce67da...` 推送。

随后在最终批准治理字节上连续运行两次完整 131 项 synthetic suite。两次均为 131/131，包含 24 项 inventory tests，且 failure/error/skip/official-path access 均为 0。两份 evidence 均为 22,234 bytes、SHA-256 `F16C91BF170ABDFC6784F368D6247E0AA8CDC9ECFB6671C71DFA9BD35CCF297C`，逐字节一致。Rebinding、governance binding 与 narrative audit 已由 commit `b09668f...` 推送。

唯一一次 formal preflight 在同步 HEAD `b09668f...` 上通过。它核验了：

- `HEAD == origin/main == GitHub main`；
- package、implementation、approval 与 rebinding commits 的祖先关系；
- implementation commit 上 17 个 evidence-bound Git blob hash；
- 当前 8 个冻结既有实现/测试 hash；
- 6 个 governance-binding 文件的路径、bytes 与 SHA-256；
- exact command、checkpoint、token、冻结输入和 exclusive-create/cleanup 实现边界；
- machine/narrative outputs 与 5 个禁止正式输出均不存在；
- reference decisions 为普通非符号链接文件，2,684,401 bytes，SHA-256 精确为 `6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7`。

Preflight 对 reference decisions 只进行一次 SHA-256 字节读取，没有解析 JSONL，未消费 semantic scan。

## 单次 Official Scan

Manifest 登记的 exact command 仅运行一次并以退出码 0 完成。未增加、遗漏、重命名或修改参数；未发生自动重试。

Machine inventory：

```text
path: results/stage4b_u1_d_pregold_amendment_5c_b_reference_schema_inventory.json
bytes: 17229
SHA-256: FA56AC3CB78EE746BF71AF0CEF40606E56B9D13C120F10A2A87400EA42CE3A5E
```

## Value-Free Schema 结果

扫描覆盖 4,500 行，得到 2 个 ordered schema signatures 和 2 个 structural schema signatures：

| Ordered signature | Rows | First line | Last line | Main |
|---|---:|---:|---:|---|
| `27F687A132A253BB9388AC7241F32C701161A24E99749535148FDE2A1C815A60` | 2,446 | 1 | 4,500 | Yes |
| `D0E34B90FB69B4F765209FEEEE044B8729F706B8C4665E219E914A40E7D8BB71` | 2,054 | 2 | 4,498 | No |

两类 schema 的顶层字段集合与字段顺序相同。相对 main schema，第二类只有以下 8 个 field paths 的 JSON 类型发生变化：

```text
$/ordered_rank
$/r_candidate
$/r_edge
$/readiness
$/score
$/u_boundary
$/u_margin
$/uncertainty
```

其中 `ordered_rank` 从 `integer` 变为 `null`；其余 7 个字段从 `finite_number` 变为 `null`。Added、removed、nesting-changed 与 order-only field paths 的计数均为 0。

这些结论只描述 reference-decisions 文件内部的 value-free schema metadata，不包含或解释任何 decision 值、query ID、question/text、ranking、policy 或 Gold。

## 独立核验

Scan 后的独立验证只读取新生成的 machine inventory，没有再次打开 reference decisions。验证通过：

- 顶层 keys 精确等于 Manifest 白名单；
- 每个 schema entry 精确等于 allowed schema metadata 白名单；
- 递归 schema node 只含冻结类型与结构 keys，不含字段值；
- ordered/structural signature 均由所附 schema metadata 独立复算匹配；
- schema row counts 合计为 4,500，main schema 选择规则独立复算匹配；
- source-integrity 中 pre/post SHA 均精确匹配冻结 SHA，`unchanged=true`；
- `exclusive_create=true`、`temporary_staging_cleaned=true`，无 staging file 残留；
- 5 个正式 decisions/rankings/policy/controller-audit/`VERIFIED_PRE_GOLD` 输出仍不存在；
- narrative audit 在核验前不存在，避免覆盖。

## 证据边界与停止状态

- 未读取 reference decisions 以外的 official 文件；
- 未读取 units、queries、channel audit、source audit、cache、rankings、policy、evaluator 或 Gold；
- 未调用 comparator、capture、controller、verifier 或 evaluator；
- 未生成 decisions、rankings、policy、controller audit 或 `VERIFIED_PRE_GOLD`；
- 未访问 U1-D 效果指标、reservation 或 Stage3B；
- 未修改代码、数据、模型、参数、schema normalization 或 raw byte-equivalence；
- 未删除、覆盖或迁移 cache、official artifact、历史 evidence 或 failure record。

当前必须停止在：

```text
REFERENCE_DECISIONS_SCHEMA_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW
OFFICIAL_CAPTURE_RETRY_NOT_APPROVED
COMPARATOR_CHANGE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

本结果不自动授权 comparator 修改、normalization、5B capture 重试、controller 重跑、verifier 或 Gold。任何后续动作必须基于本聚合 schema 审计建立新的独立 Amendment 并获得批准。

