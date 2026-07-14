# Stage4B-U1-D Pre-Gold Amendment 5D-B 批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-14
- Decision: `APPROVE_STAGE4B_U1_D_AMENDMENT_5D_B_SINGLE_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC`
- Amendment 5D-B package commit: `f67061e753b03a5cf46d7a7c92b5a95fc79b0ef8`
- Amendment 5D-A implementation/evidence: `02f46447e4cd69a15d2af14ee1fc62f9eb4f8bb9`
- Amendment 5D-A package: `33ce115f78840956fcc7bda0c3f4e172579350e7`
- Amendment 5D-A approval governance: `7f879a628fc313e24e805d9bdc5a81b06c37304a`
- Amendment 5C-B final diagnostic/audit: `e5f28f664449c02b12a129aaa2a011bad84dab91`
- Amendment 5C-B package: `e5a6c5479dbd125ebb58b95e9594fadde6b6719d`
- Amendment 5C-B approval governance: `fce67da87d155b1026cbe0670f606201ede0ac4b`
- Amendment 5C-B rebinding/governance: `b09668f47cd31df2be73446cadacf84d996418f9`
- Hard Failure 5: `deccd203059d05dc27ba80aca1ddb1e2ea8f616f`
- Amendment 5B v2 package: `f43e22ef079701139d4437849be8ad57654f80d7`
- Amendment 5B v2 approval governance: `2ddf6e044c27e47385a558bdaca80cb6c31c4ffe`
- Amendment 5B v2 rebinding/governance: `4c10ad942a75af42b910b860fd4897b672160d5d`
- Hard Failure 4: `b21852a174b537c90a848699deb4d26d6f169506`
- Failed controller execution HEAD: `8e0bab13ad20c06795dffd5ca71f167a814cdfb0`
- v2.3.1 implementation: `34349c70ee24b8240fd169393134d4280968b790`
- Controller rerun: `NOT_AUTHORIZED`
- Verifier/Gold: `NOT_AUTHORIZED`
- Other project conversations, thread tools, and global memory used: No

## 正式审批结论

批准 Stage4B-U1-D Pre-Gold Amendment 5D-B：单次 official decisions-only diagnostic，仅用于完成 Hard Failure 4 的聚合差异分类。

本批准严格绑定 package commit `f67061e753b03a5cf46d7a7c92b5a95fc79b0ef8`、5D-A implementation/evidence commit `02f46447e4cd69a15d2af14ee1fc62f9eb4f8bb9` 及上述历史提交。旧 5B v2 授权已经消耗；只有本决定在最终批准治理、post-approval rebinding、governance binding 和 formal preflight 全部通过后，才重新激活冻结技术 token 一次。

## 唯一允许顺序

1. 提交并推送本批准决定及最终批准版 `AGENTS.md`。
2. 在最终批准治理字节上完整运行 143 项 synthetic suite 两次；两次均须 `143/143`、零 failure/error/skip/official-path access，完整 evidence 字节一致。
3. 生成 governance-binding JSON，绑定 5D-B request、Manifest、本批准决定、最终 `AGENTS.md`、5D-A implementation audit/evidence 和 post-approval rebinding evidence。
4. 提交并推送 rebinding evidence、governance binding 与 narrative rebinding audit。
5. 仅运行一次只读 formal preflight；任一门失败均停止，不得运行 capture 或第二次 preflight。
6. 仅在 preflight 全部门通过后，运行一次 Manifest 登记的 exact-command official capture。
7. 进行一次仅字节哈希/元数据级 post-run 独立核验，写入 aggregate-only narrative audit。
8. 提交并推送 machine/narrative audit，核对 GitHub 后立即停止。

任一 rebinding、binding、preflight、capture、cleanup、validation、commit 或 push 失败，必须记录为新 Hard Failure，且不得自动重试。

## Post-Approval Rebinding

冻结命令为：

```powershell
python scripts\stage4b_u1_run_decisions_diagnostic_synthetic_verification.py `
  --output results\stage4b_u1_d_pregold_amendment_5d_b_synthetic_rebinding.json
```

两次输出必须同时报告：

```text
tests_run = 143
failures = 0
errors = 0
skipped = 0
official_path_access_guard.blocked_or_attempted_access_count = 0
diagnostic_checkpoint = stage4b_u1_decisions_diag_v2
```

两份完整 evidence 必须字节一致，并继续确认没有 official comparator/capture、controller、verifier、evaluator、Gold、reservation 或 Stage3B 访问。

## 冻结 Official 输入

只有以下五项可在 formal preflight 全部通过后读取：

| 输入 | 路径 | 冻结指纹 |
|---|---|---|
| unlabeled units | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_units.jsonl` | SHA-256 `114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA` |
| unlabeled queries | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_queries.jsonl` | SHA-256 `6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B` |
| controller channel audit | `E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_v2_3_1_controller_channel_audit.json` | SHA-256 `D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA` |
| existing embedding cache | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_minilm_idbound_embeddings.npz` | SHA-256 `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D`; 210,714,667 bytes |
| v2.2 reference decisions | `E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_decisions.jsonl` | SHA-256 `6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7` |

所有文件必须为普通非符号链接文件，路径与 Manifest 精确一致。Stage4A-R2 source-audit 文件、5C-B machine inventory、official rankings、reference policy、evaluator/Gold、reservation 和 Stage3B 均在读取边界外。

## 冻结实现与边界

```text
capture SHA-256:
7C7B159911384B436FDCC1B20D26F2F545F2DC55EAD1F7B2B134B273110ED40A

comparator v2 SHA-256:
42FA3F74679672B0595CC76B519D59C03CB193415DD03F56E37260A961D94014

diagnostic checkpoint:
stage4b_u1_decisions_diag_v2

controller checkpoint:
stage4b_u1_v2_3_1
```

其余 implementation hashes 必须逐项匹配 Manifest。数据边界继续为 4,500 queries、143,820 units、冻结双 ID digest、`query_id == dataset::sample_id`、冻结 source-audit digest、MiniLM、`max_length=192`、`batch_size=64`。不得打开 source-audit 文件。

Comparator v2 仅取消文件级 row-schema 同构拒绝；逐 query 字段集合、字段顺序、递归 schema、canonical、discrete、finite-float、ULP 和 semantic comparison 保持冻结。Raw-byte equality 仍为唯一控制性门。`null` 不得填充、转换或 normalization。

## Exact Official Command

```powershell
python scripts\stage4b_u1_capture_diagnostic_decisions.py `
  --units "E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_units.jsonl" `
  --queries "E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_queries.jsonl" `
  --channel-audit "E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_v2_3_1_controller_channel_audit.json" `
  --embedding-cache "E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_minilm_idbound_embeddings.npz" `
  --reference-decisions "E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_decisions.jsonl" `
  --audit-output "E:\科研\HyperGranular-RAG\results\stage4b_u1_d_pregold_amendment_5b_official_decisions_diagnostic.json" `
  --temp-parent "C:\Users\cc\AppData\Local\Temp" `
  --model-name "sentence-transformers/all-MiniLM-L6-v2" `
  --batch-size 64 `
  --max-length 192 `
  --expected-units-sha256 114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA `
  --expected-queries-sha256 6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B `
  --expected-channel-audit-sha256 D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA `
  --expected-embedding-cache-sha256 69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D `
  --official-authorization-token APPROVE_STAGE4B_U1_D_AMENDMENT_5B_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC
```

参数不得增加、遗漏、重命名或实质重排。技术 token 本次最多使用一次；不得运行第二次 capture。

## Formal Preflight 与 Post-Run Gate

唯一一次 preflight 必须确认 Git/GitHub 同步、所有治理/实现 ancestor、Manifest hash、最终 `AGENTS.md` binding、五输入普通文件与冻结指纹、channel 内部边界、machine/narrative/formal 输出不存在、精确 OS temp parent，以及没有任何禁止输入参数。

Capture 完成后只允许一次独立的字节哈希/元数据核验：temporary decisions 已删除，五输入 SHA 未变化，cache bytes 未变化，machine audit 仅含允许聚合字段，五项正式输出继续不存在，且没有 staging/temp 残留。不得再次解析 reference decisions 或读取字段值。

历史 machine output 路径继续为：

```text
results/stage4b_u1_d_pregold_amendment_5b_official_decisions_diagnostic.json
```

Preflight 必须要求该路径不存在。Capture 只能 exclusive-create，不得覆盖、删除、改名或绕过。

## Machine Audit 边界

允许输出 raw-byte 相等状态/字节数/SHA/terminal-newline flags、canonical digest/difference counts、row counts、query-ID set/order difference counts、field/schema/discrete/float/ULP/semantic difference counts、pre/post integrity、temporary cleanup 和最多一个 salted query-ID hash。

禁止输出原始文件字节内容、raw query ID、raw decision row、字段值、question/text、rankings、policy、source-audit 内容、Gold 或 U1-D effect。`null` 与 integer/float 必须继续作为明确 type/discrete difference，适用时计入 semantic difference。

## 明确不授权

- 第二次 preflight 或 capture；
- official rankings/reference policy 的读取、比较或哈希；
- 打开 Stage4A-R2 source-audit 文件或 5C-B machine inventory；
- 运行完整 controller、verifier、evaluator、reservation 或 Stage3B；
- 生成或提升正式 decisions、rankings、policy、controller audit 或 `VERIFIED_PRE_GOLD`；
- 修改代码、数据、模型、参数、comparator semantics、byte-equivalence 或停止规则；
- 创建、重建、覆盖、删除或迁移 cache/历史工件；
- 读取或解释 Gold/U1-D effect metrics；
- 任一失败后的重试或诊断后的自动 pre-Gold 恢复。

## 完成后状态

```text
AMENDMENT_5D_B_OFFICIAL_DECISIONS_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW
HARD_FAILURE_4_DIAGNOSIS_COMPLETE_AWAITING_REVIEW
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
