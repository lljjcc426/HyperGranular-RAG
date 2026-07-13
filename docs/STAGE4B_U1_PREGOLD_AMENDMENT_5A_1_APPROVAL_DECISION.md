# Stage4B-U1-D Pre-Gold Amendment 5A.1 批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-14
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5A_1_CHANNEL_INPUT_HASH_BINDING_IMPLEMENTATION_SYNTHETIC_ONLY`
- Amendment 5A.1 package commit: `3137ace0328dd24908f95737ea1dcbe0c8fe045e`
- Returned Amendment 5B package: `ceb755252540cf223aa18ac721443154c29cd07a`
- Amendment 5A final implementation/evidence: `9a060bd31e9c33be587f7ef5e64f86206922e59e`
- Amendment 5A package: `81d8c34f1cf2539a4c0b81c6148047bc666e2f82`
- Amendment 5A approval governance: `a0bf91b3a34daaf5b1ee50700d8356e1383e9a9c`
- Hard Failure 4: `b21852a174b537c90a848699deb4d26d6f169506`
- Failed controller execution HEAD: `8e0bab13ad20c06795dffd5ca71f167a814cdfb0`
- v2.3.1 implementation: `34349c70ee24b8240fd169393134d4280968b790`
- Official diagnosis: `NOT_AUTHORIZED`
- Controller rerun: `NOT_AUTHORIZED`
- Verifier: `NOT_AUTHORIZED`
- Gold: `NOT_AUTHORIZED`
- Other project conversations, thread tools, and global memory used: No

## 正式审批结论

批准 Stage4B-U1-D Pre-Gold Amendment 5A.1：channel-input 外部 SHA 前后硬绑定，仅授权实现与 synthetic 验证。

## 冻结的三项输入

```text
unlabeled units SHA-256
114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA

unlabeled queries SHA-256
6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B

controller channel audit SHA-256
D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA
```

路径与 SHA 均以 package commit `3137ace0328dd24908f95737ea1dcbe0c8fe045e` 中的请求和 Manifest 为准。

## 授权范围

1. 增加 `--expected-units-sha256`、`--expected-queries-sha256`、`--expected-channel-audit-sha256` 三个必需参数。
2. Official 模式在任何 JSON/JSONL 语义解析、cache 加载或诊断计算前，核验三路径均为普通文件并逐项匹配外部 SHA；三项全通过前只能读取计算 SHA 所需字节。
3. 诊断计算及临时 decisions 比较、清理后，在 machine audit exclusive-create 前再次核验三项 SHA。
4. 任一前置或后置不匹配时硬失败、不生成 machine audit、清理临时 decisions 且不自动重试。
5. 保留 98 项测试并新增至少 6 项，完整 suite 不少于 104 项；连续运行两次且均为全通过、零 failure/error/skip/official-path access、完整 evidence 字节一致。
6. 形成并推送 implementation audit、deterministic evidence 和新版 implementation-bound 5B v2 审批包，随后立即停止。

## 允许修改的文件

```text
scripts/stage4b_u1_capture_diagnostic_decisions.py
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
tests/test_stage4b_u1_decisions_diagnostic.py
```

以及 package Manifest 已登记的对应治理、审计、evidence 和新版 5B v2 文件。

## 必须保持不变

```text
scripts/stage4b_u1_goldfree_controller.py
scripts/stage4b_u1_goldfree_retrieval.py
scripts/stage4b_u1_common.py
scripts/stage4b_u1_compare_decisions.py
controller checkpoint = stage4b_u1_v2_3_1
```

Comparator 语义与 raw byte-equivalence 的控制地位不得改变。数据、模型、effective-K、q25、score、ECDF、预算、trigger、ranking、endpoint 和停止规则不得修改。

## 明确不授权

- 读取任何 official units、queries、channel audit、source audit、cache、decisions、rankings、policy 或 evaluator 文件；
- 使用已退回 5B token，运行 5B preflight、official capture/comparator、controller、verifier 或 evaluator；
- 生成 official decisions、rankings、policy、diagnostic audit、controller audit 或 `VERIFIED_PRE_GOLD`；
- 修改或放宽 byte equivalence；
- 创建、重建、覆盖、删除或迁移 cache；
- 读取 U1-D 效果指标，访问 reservation 或 Stage3B；
- 自动重试或自动恢复 Hard Failure 4。

## 完成后状态

```text
AMENDMENT_5A_1_SYNTHETICALLY_VERIFIED
OFFICIAL_DIAGNOSIS_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

新版 5B v2 包推送后必须停止，等待下一次独立审批。
