# Stage4B-U1-D Pre-Gold Amendment 5D-A 批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-14
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5D_A_HETEROGENEOUS_SCHEMA_COMPARATOR_IMPLEMENTATION_SYNTHETIC_ONLY`
- Amendment 5D-A package commit: `33ce115f78840956fcc7bda0c3f4e172579350e7`
- Amendment 5C-B final diagnostic/audit: `e5f28f664449c02b12a129aaa2a011bad84dab91`
- Amendment 5C-B package: `e5a6c5479dbd125ebb58b95e9594fadde6b6719d`
- Amendment 5C-B approval governance: `fce67da87d155b1026cbe0670f606201ede0ac4b`
- Amendment 5C-B rebinding/governance: `b09668f47cd31df2be73446cadacf84d996418f9`
- Amendment 5C-A implementation/evidence: `492a59b2f4daccd3e123f2b6cc49cd896d5009d1`
- Hard Failure 5: `deccd203059d05dc27ba80aca1ddb1e2ea8f616f`
- Amendment 5B v2 package: `f43e22ef079701139d4437849be8ad57654f80d7`
- Amendment 5B v2 approval governance: `2ddf6e044c27e47385a558bdaca80cb6c31c4ffe`
- Amendment 5B v2 rebinding/governance: `4c10ad942a75af42b910b860fd4897b672160d5d`
- Hard Failure 4: `b21852a174b537c90a848699deb4d26d6f169506`
- Failed controller execution HEAD: `8e0bab13ad20c06795dffd5ca71f167a814cdfb0`
- v2.3.1 implementation: `34349c70ee24b8240fd169393134d4280968b790`
- Official execution: `NOT_AUTHORIZED`
- Other project conversations, thread tools, and global memory used: No

## 正式审批结论

批准 Stage4B-U1-D Pre-Gold Amendment 5D-A：heterogeneous-schema comparator 文件级同构拒绝移除，仅授权实现与 synthetic 验证。

本批准严格绑定 package commit `33ce115f78840956fcc7bda0c3f4e172579350e7` 及上述历史提交。未绑定该 package commit 的批准无效。

## 允许修改文件

```text
scripts/stage4b_u1_compare_decisions.py
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
tests/test_stage4b_u1_decisions_diagnostic.py
```

Comparator 只允许：

1. 将 `SCHEMA_VERSION` 更新为 `stage4b_u1_decisions_diagnostic_v2`；
2. 将 `DIAGNOSTIC_CHECKPOINT` 更新为 `stage4b_u1_decisions_diag_v2`；
3. 删除 `load_decisions_jsonl()` 的全文件完整类型签名同构要求；
4. 不修改其余逐 query 比较算法。

## Comparator 冻结契约

- 每行继续要求合法 JSON object；
- 所有嵌套层级继续拒绝重复 key；
- `NaN`、`Infinity`、`-Infinity` 继续拒绝；
- 每行继续要求唯一、非空字符串 `query_id`；
- 字段集合、字段顺序、recursive type/structure、canonical row、discrete value、finite binary64 exact/absolute/ULP 和三个 semantic fields 的逐 query 比较保持不变；
- aggregate output keys 保持不变，只有 version/checkpoint 值更新；
- 不输出 raw query ID 或 raw decision row；
- `null <-> integer/finite float` 计入 schema-type 和 discrete-value difference；
- `ordered_rank null <-> integer` 同时计入 semantic difference；
- `null` 不进入 finite-float absolute-error/ULP，也不得填充、转换、coerce、cast 或 normalize；
- raw file byte equality 继续是唯一控制性等价门，canonical 或 semantic 结果不能替代。

## Synthetic 硬门

现有完整 suite 基线为 131 项。至少新增 12 项 heterogeneous-schema tests，最终完整 suite 不少于 143 项。

最终必须在完全相同 tracked bytes 上运行两次完整 suite。两次均须：

```text
tests >= 143
failures = 0
errors = 0
skipped = 0
official-path access attempts = 0
complete evidence byte-identical = true
```

Runner 必须绑定 request、Manifest、本批准决定、5C-B review、5C-B official schema audit、最终批准版 `AGENTS.md`、三个允许文件和 Manifest 全部冻结文件。5C-B machine inventory 不得作为实现输入或 fixture。

## 完成后允许工件

- 本批准决定；
- 5D-A implementation audit；
- deterministic synthetic evidence；
- 一次 implementation/evidence commit 与 push；
- implementation-bound 5D-B request 与 Manifest；
- 必要的 `AGENTS.md`、`README.md`、`ROADMAP.md`、`REPRODUCIBILITY.md` 状态同步。

5D-B package 推送后必须停止等待独立审批。

## 明确不授权

- 打开任何 official units、queries、channel audit、source audit、cache、decisions、rankings、policy、evaluator 或 Gold 文件；
- 将 5C-B machine inventory 用作实现或 fixture 输入；
- 运行 official comparator/capture、controller、verifier 或 evaluator；
- 生成 official diagnostic artifacts 或执行 5D-B；
- 修改 capture、controller、retrieval、common、inventory、其他 runners/tests 或任何 Manifest 冻结文件；
- normalization、imputation、coercion、casting 或 raw byte-equivalence 放宽；
- 修改数据、模型、`max_length`、batch size、effective-K、q25、score、ECDF、budget、trigger、ranking、endpoint 或 stop rule；
- 创建、重建、覆盖、迁移或删除 cache、official artifact、历史 evidence 或 failure record；
- 读取 U1-D 效果指标、reservation 或 Stage3B；
- 自动批准或运行 5D-B。

## 完成后状态

```text
AMENDMENT_5D_A_SYNTHETICALLY_VERIFIED
HARD_FAILURE_5_DIRECT_CAUSE_CONFIRMED
HARD_FAILURE_4_DIAGNOSIS_STILL_INCOMPLETE

OFFICIAL_CAPTURE_RETRY_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

