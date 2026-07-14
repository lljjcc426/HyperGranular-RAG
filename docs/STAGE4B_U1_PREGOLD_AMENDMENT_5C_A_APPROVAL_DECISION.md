# Stage4B-U1-D Pre-Gold Amendment 5C-A 批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-14
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5C_A_REFERENCE_SCHEMA_INVENTORY_IMPLEMENTATION_SYNTHETIC_ONLY`
- Amendment 5C-A package commit: `a8caa2a3b26ae13d0b149e4995e3a017e8edb2e7`
- Hard Failure 5 audit/status: `deccd203059d05dc27ba80aca1ddb1e2ea8f616f`
- Amendment 5B v2 rebinding/governance: `4c10ad942a75af42b910b860fd4897b672160d5d`
- Amendment 5B v2 approval governance: `2ddf6e044c27e47385a558bdaca80cb6c31c4ffe`
- Amendment 5B v2 package: `f43e22ef079701139d4437849be8ad57654f80d7`
- Amendment 5A.1 implementation/evidence: `e566eb861ec6028ca89a40c9aca7d06737f1eb8e`
- Hard Failure 4: `b21852a174b537c90a848699deb4d26d6f169506`
- Failed controller execution HEAD: `8e0bab13ad20c06795dffd5ca71f167a814cdfb0`
- v2.3.1 implementation: `34349c70ee24b8240fd169393134d4280968b790`
- Official schema scan: `NOT_AUTHORIZED`
- Comparator/capture/controller: `NOT_AUTHORIZED`
- Verifier/Gold: `NOT_AUTHORIZED`
- Other project conversations, thread tools, and global memory used: No

## 正式审批结论

批准 Stage4B-U1-D Pre-Gold Amendment 5C-A：reference-decisions schema 异质性诊断工具实现与 synthetic 验证。不授权 official reference 读取、comparator 修改、capture 重跑或 controller。

## 授权范围

只允许新增：

```text
scripts/stage4b_u1_inventory_decision_schemas.py
scripts/stage4b_u1_run_schema_inventory_synthetic_verification.py
tests/test_stage4b_u1_decision_schema_inventory.py
```

以及本批准决定、implementation audit、deterministic synthetic evidence、未来 implementation-bound 5C-B request/Manifest 和必要治理状态同步文件。任何现有实现、测试、official artifact、历史 evidence 或 failure record 均不得修改或删除。

Schema inventory 必须严格实现 package Manifest 冻结的 value-free JSONL schema 契约：所有层级重复 key 检测；blank/invalid/non-object/non-finite 硬失败；JSON 类型严格区分；object/array element schema 递归表示；array 不保留值、顺序、multiplicity 或 length；ordered 与 order-insensitive signature 并存；field-order-only 差异独立；main schema 按 ordered signature 行数众数及字典序 tie-break 选择。

## Synthetic 验证门

- 保留现有 107 项测试；
- 至少新增 12 项，完整 suite 不少于 119 项；
- 在相同 tracked bytes 上连续完整运行两次；
- 两次均须全部通过，`0 failure / 0 error / 0 skip / 0 official-path access`；
- 两次完整 evidence 必须字节一致；
- 测试必须主动证明 no-value/no-ID leakage、临时清理、official path 阻断，以及 comparator/capture/controller/rankings/policy/verifier/evaluator/Gold/reservation/Stage3B 均未调用。

## 必须保持不变

```text
scripts/stage4b_u1_compare_decisions.py
scripts/stage4b_u1_capture_diagnostic_decisions.py
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
scripts/stage4b_u1_goldfree_controller.py
scripts/stage4b_u1_goldfree_retrieval.py
scripts/stage4b_u1_common.py
tests/test_stage4b_u1_decisions_diagnostic.py
tests/test_stage4b_u1_goldfree.py
```

Raw byte-equivalence、schema acceptance/normalization、模型、`max_length`、batch size、effective-K、q25、score、ECDF、budget、trigger、ranking、endpoint 与 stop rules 全部冻结。

## 明确不授权

- 打开冻结 v2.2 reference decisions 或任何 official units/queries/channel audit/source audit/cache/rankings/policy/evaluator/Gold；
- official schema scan、现有 comparator 调用/修改、official capture 运行/重试、新 decisions 生成；
- controller、verifier、evaluator、U1-D 指标、reservation 或 Stage3B；
- normalization、byte-equivalence 放宽或任何科研算法/参数修改；
- cache、official artifact、历史 evidence 或 failure record 的创建、覆盖、迁移或删除；
- 自动恢复 Hard Failure 5。

## 完成后状态

```text
AMENDMENT_5C_A_SYNTHETICALLY_VERIFIED
OFFICIAL_SCHEMA_SCAN_NOT_APPROVED
COMPARATOR_CHANGE_NOT_APPROVED
OFFICIAL_CAPTURE_RETRY_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

5C-A implementation/evidence 推送后只能组装并推送 implementation-bound 5C-B 包，随后立即停止，等待独立审批。
