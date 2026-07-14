# Stage4B-U1-D Pre-Gold Amendment 5C-B 批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-14
- Decision: `APPROVE_STAGE4B_U1_D_AMENDMENT_5C_B_SINGLE_REFERENCE_SCHEMA_SCAN`
- Amendment 5C-B package commit: `e5a6c5479dbd125ebb58b95e9594fadde6b6719d`
- Amendment 5C-A package: `a8caa2a3b26ae13d0b149e4995e3a017e8edb2e7`
- Amendment 5C-A approval governance: `a680c0358ac351a5e80c9829d48a7b8e88950f4c`
- Amendment 5C-A implementation/evidence: `492a59b2f4daccd3e123f2b6cc49cd896d5009d1`
- Hard Failure 5 audit/status: `deccd203059d05dc27ba80aca1ddb1e2ea8f616f`
- Amendment 5B v2 rebinding/governance: `4c10ad942a75af42b910b860fd4897b672160d5d`
- Amendment 5B v2 approval governance: `2ddf6e044c27e47385a558bdaca80cb6c31c4ffe`
- Amendment 5B v2 package: `f43e22ef079701139d4437849be8ad57654f80d7`
- v2.3.1 implementation: `34349c70ee24b8240fd169393134d4280968b790`
- Controller rerun: `NOT_AUTHORIZED`
- Verifier/Gold: `NOT_AUTHORIZED`
- Other project conversations, thread tools, and global memory used: No

## 正式审批结论

批准 Stage4B-U1-D Pre-Gold Amendment 5C-B：单次 official reference-decisions value-free schema-only scan。

本批准严格绑定 package commit `e5a6c5479dbd125ebb58b95e9594fadde6b6719d` 及上述八个历史提交。未绑定该 package commit 的批准无效。

## 唯一允许顺序

1. 提交并推送本批准决定及最终批准治理字节。
2. 在最终批准治理字节上完整运行 131 项 synthetic suite 两次；两次均须 `131/131`、零 failure/error/skip/official access，完整 evidence 字节一致。
3. 生成并推送 post-approval rebinding evidence、governance-binding JSON 与 narrative rebinding audit。
4. 只运行一次只读 formal preflight；对冻结 reference decisions 仅允许按字节计算 SHA-256，不得解析 JSONL。
5. 仅在 preflight 全部通过后，运行一次 Manifest 登记的 exact-command schema-only scan。
6. 独立核验 machine audit 的字段白名单、value-free 边界、输入前后 SHA、exclusive-create 与 staging cleanup；生成 aggregate-only narrative audit。
7. 提交并推送 machine/narrative audit，核对 GitHub 后立即停止。

任一 rebinding、binding、preflight、scan、validation、commit 或 push 硬门失败，必须立即停止且不得自动重试。

## 冻结 Official 输入

唯一允许读取的 official 文件为：

```text
E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_decisions.jsonl
SHA-256: 6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7
```

Preflight 只能进行 SHA-256 字节读取。唯一一次正式 scan 只能执行实现冻结的 pre-hash、一次 JSONL schema parse、post-hash 和 exclusive-create 输出，不得保留或输出任何字段值。

## Exact Command

```powershell
python scripts\stage4b_u1_inventory_decision_schemas.py `
  --input "E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_decisions.jsonl" `
  --output "E:\科研\HyperGranular-RAG\results\stage4b_u1_d_pregold_amendment_5c_b_reference_schema_inventory.json" `
  --expected-input-sha256 6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7 `
  --official-authorization-token APPROVE_STAGE4B_U1_D_AMENDMENT_5C_B_SINGLE_REFERENCE_SCHEMA_SCAN
```

参数不得增加、遗漏、重命名或修改；token 只能在 post-approval rebinding、governance binding 和唯一一次 formal preflight 全部通过后使用一次。

## 输出边界

Machine audit 只能包含 Manifest 冻结的 value-free schema metadata、聚合行数/签名计数、主 schema 选择、各 schema 的聚合计数与首次/末次物理行号、字段名/顺序/类型/嵌套 schema、相对主 schema 的结构差异，以及输入前后 SHA 和 exclusive-create/staging-cleanup 布尔值。

禁止输出 raw/salted query ID、原始行、字段值、float 值、question/text、rankings、policy、Gold 或新 decisions。Narrative audit 只能总结同一聚合边界，不得解释检索质量、U1-D 效果或 decision 值。

## 明确不授权

- 读取冻结 reference decisions 以外的任何 official 文件；
- 读取 units、queries、channel audit、source audit、cache、rankings、policy、evaluator 或 Gold；
- 调用或修改 comparator、capture、controller、verifier 或 evaluator；
- 生成 decisions、rankings、policy、controller audit 或 `VERIFIED_PRE_GOLD`；
- 修改 schema normalization、raw byte equivalence、数据、模型、参数、effective-K、q25、score、ECDF、budget、trigger、ranking、endpoint 或 stop rules；
- 创建、重建、覆盖、迁移或删除 cache、official artifact、历史 evidence 或 failure record；
- 访问 U1-D 指标、reservation 或 Stage3B；
- 任一硬失败后的重试，或 scan 后自动恢复 5B capture / official pre-Gold execution。

## 完成后状态

```text
REFERENCE_DECISIONS_SCHEMA_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW
OFFICIAL_CAPTURE_RETRY_NOT_APPROVED
COMPARATOR_CHANGE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

