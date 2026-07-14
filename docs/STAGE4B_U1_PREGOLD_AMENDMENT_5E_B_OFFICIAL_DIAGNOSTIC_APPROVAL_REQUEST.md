# Stage4B-U1-D Pre-Gold Amendment 5E-B Official Decisions-Only Diagnostic Approval Request

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-14
- Request ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_5E_B_SINGLE_PREFLIGHT_AND_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5E_B_MANIFEST.json`
- Current state: `AMENDMENT_5E_A_SYNTHETICALLY_VERIFIED`
- Hard Failure 4 diagnosis: `INCOMPLETE`
- Formal preflight retry: `NOT_APPROVED`
- Official capture: `NOT_APPROVED`
- Controller rerun: `NOT_APPROVED`
- Verifier: `NOT_APPROVED`
- Gold: `NOT_APPROVED`
- Other project conversations, thread tools, and global memory used: No

## Binding Commits

```text
Amendment 5E-A implementation/evidence:
a8b064a4a2133aea27cbe9b85978237fc3dae661

Amendment 5E-A approval governance:
461939434206764555b917c5971956e6951ff4dd

Amendment 5E-A package:
19f16f559f0b1f3b59ef24a04e368f99ae3635e3

Hard Failure 6:
bebfeb5664f26795b8d3472f3729ca1bb9abf889

Amendment 5D-B rebinding/governance:
2447ad234c160c6e615d81b33dc4ede7ecaa18da

Amendment 5D-B approval governance:
1c46dc1b69f8381598aacb9f3b1e27561c7f9ee2

Amendment 5D-B package:
f67061e753b03a5cf46d7a7c92b5a95fc79b0ef8

Amendment 5D-A implementation/evidence:
02f46447e4cd69a15d2af14ee1fc62f9eb4f8bb9

Hard Failure 5:
deccd203059d05dc27ba80aca1ddb1e2ea8f616f

Hard Failure 4:
b21852a174b537c90a848699deb4d26d6f169506

v2.3.1 implementation:
34349c70ee24b8240fd169393134d4280968b790
```

任何批准必须显式绑定未来包含本 request 与 Manifest 的 5E-B package commit。5D-B 或更早的授权已经消耗，不能授权 5E-B 命令。

## 5E-A Implementation Evidence

5E-A final evidence：

```text
path: results/stage4b_u1_d_pregold_amendment_5e_a_synthetic_verification.json
bytes: 36518
SHA-256: 84C58CBA9801A6EB8DFAF4ED6688BB5FCBD5777729FD833083E16CB630FFED83
tests: 161/161
failure/error/skip: 0/0/0
official metadata/content access: 0
formal preflight/token/capture: 0/0/0
byte-identical complete runs: true
```

Implementation audit 为 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5E_A_IMPLEMENTATION_AUDIT.md`，SHA-256 `AC33D652837589DE17FD7EB90DEED1DE53DAEF6F98A61D8ADB1A6798348439BF`，10,030 bytes。

Helper 冻结为：

```text
path: scripts/stage4b_u1_preflight_path_equivalence.py
bytes: 3543
SHA-256: 1A17C0E750F91CEF2F638A0B0C6FD381110692E6B2D467C1F5243ADF3F35B3FF
function: windows_directories_equivalent
```

## Scientific Purpose

Hard Failure 6 已确认为 preflight 对两个等价 OS-temp 目录字符串未归一化尾分隔符。5E-A 已实现并合成验证 fail-closed Windows path-equivalence helper。Hard Failure 4 仍未分类，因为没有生成新的 temporary decisions，也没有完成 v2.3.1 与 v2.2 decisions 的聚合比较。

本请求只申请一次新的只读 preflight，以及在其全部通过后一次原 exact-command decisions-only capture，用于完成 Hard Failure 4 的聚合分类。Raw byte equality 继续是唯一控制门；canonical 或 semantic equality 只能解释差异，不能替代或放宽 raw byte equality。

## Package Has No Execution Authority

本 request/Manifest 仅为治理材料。在新的 package-bound 批准明确通过前：

- 不得运行 post-approval rebinding；
- 不得运行 formal preflight 或 helper official-boundary check；
- 不得传入 token；
- 不得运行 capture、controller、verifier 或 Gold；
- 不得打开任何 official 输入。

## Requested Ordered Authorization

仅请求未来审批以下顺序：

1. 创建并推送绑定 5E-B package commit 与 `a8b064a...` 的批准决定和最终 `AGENTS.md`。
2. 在最终批准治理字节上连续运行两次完整 161-test 5E-A suite；两次必须全通过、零 failure/error/skip/official access/formal-preflight/token/capture，完整 evidence 字节一致。任一失败立即停止，不得自动重试。
3. 创建并推送 governance-binding JSON 与 narrative audit，绑定 request、Manifest、approval decision、最终 `AGENTS.md`、5E-A implementation/evidence 和 post-approval rebinding evidence。
4. 运行唯一一次只读 formal preflight。该 preflight 必须先核验 helper 文件 SHA/bytes，再直接 import/call `windows_directories_equivalent()`；禁止复制新的内联 PowerShell path-equivalence 逻辑。
5. Helper gate 通过后，preflight 才可检查五项 permitted official inputs 的 metadata、SHA 和冻结边界。任一失败立即停止，不得 capture 或重试。
6. 只有 preflight 全部通过后，运行一次完全不变的 exact official decisions-only capture command。
7. 独立核验 temporary cleanup、五输入 post-run fingerprints、aggregate-only machine audit，以及五项 formal outputs 继续不存在。
8. 形成 machine/narrative audit，提交推送、核对 GitHub 后立即停止。

## Required Helper-Bound Preflight Gate

在任何 official input metadata/content 操作前，preflight 必须：

1. 核验 helper 为普通 tracked 文件，bytes 为 3,543，SHA-256 为 `1A17C0E...F35B3FF`；
2. 从 `.NET [System.IO.Path]::GetTempPath()` 获取 runtime OS-temp 字符串，不先裁剪或改写；
3. 保持 Manifest expected 字符串为 `C:\Users\cc\AppData\Local\Temp`；
4. 使用项目 Python 直接 import/call 已哈希绑定函数；
5. 只有函数返回 `True` 且 Python exit code 为 0 才通过；异常、`False` 或非零退出均为硬失败。

冻结调用形式：

```powershell
$runtimeTemp = [System.IO.Path]::GetTempPath()
$env:PYTHONPATH = "E:\科研\HyperGranular-RAG\scripts"
python -c "import sys; from stage4b_u1_preflight_path_equivalence import windows_directories_equivalent; raise SystemExit(0 if windows_directories_equivalent(sys.argv[1], sys.argv[2]) else 1)" `
  $runtimeTemp `
  "C:\Users\cc\AppData\Local\Temp"
```

该调用只验证 OS-temp directory equivalence，不接受父/子/前缀目录，不修改 capture command 的 `--temp-parent` 参数。

## Frozen Official Read Boundary

Helper gate 通过后，formal preflight 与 conditional capture 的读取边界仍严格限于 5D-B 已冻结的五项：

| Input | Exact path | Expected fingerprint |
|---|---|---|
| unlabeled units | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_units.jsonl` | `114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA` |
| unlabeled queries | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_queries.jsonl` | `6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B` |
| controller channel audit | `E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_v2_3_1_controller_channel_audit.json` | `D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA` |
| ID-bound embedding cache | `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_minilm_idbound_embeddings.npz` | `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D`; 210,714,667 bytes |
| v2.2 reference decisions | `E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_decisions.jsonl` | `6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7` |

Stage4A-R2 source-audit 文件和 5C-B machine inventory 不得打开；只可核验 channel audit 中已登记的 source digest。Official rankings、reference policy、evaluator/Gold、reservation 和 Stage3B 继续禁止。

## Frozen Scientific And Implementation Boundary

```text
dataset: 2wikimultihopqa
queries: 4500
units: 143820
sample-ID SHA-256: 6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2
query-ID SHA-256: 8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6
namespace: query_id == dataset::sample_id
source-audit digest: 1496FF0CE08093AD38258FD5049068D6C4ED74FCEBF63E94E6E486F3478C7AEE
controller checkpoint: stage4b_u1_v2_3_1
comparator checkpoint: stage4b_u1_decisions_diag_v2
model: sentence-transformers/all-MiniLM-L6-v2
max_length: 192
batch_size: 64
```

Capture SHA 必须保持 `7C7B1599...ED40A`，comparator SHA 必须保持 `42FA3F74...94014`。Capture、comparator、controller、retrieval、common、helper、runner、tests 及其他 Manifest implementation hashes 全部冻结，不请求代码修改。

## Exact Official Capture Command Remains Unchanged

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

参数、顺序语义、token string、`--temp-parent` 原始值与历史 machine output path 均不得修改。5E-B 只请求未来 package-bound 决定对该实现 gate 授权一次，不请求代码或 token string 变更。

## Required Post-Approval Synthetic Rebinding

未来批准治理落盘后，必须在最终治理字节上连续运行两次：

```powershell
python scripts\stage4b_u1_run_decisions_diagnostic_synthetic_verification.py `
  --output results\stage4b_u1_d_pregold_amendment_5e_b_synthetic_rebinding.json
```

两次必须 161/161、零 failure/error/skip/official access/formal-preflight/token/capture，完整 evidence 字节一致。Governance binding 必须覆盖 request、Manifest、approval decision、最终 `AGENTS.md`、5E-A implementation audit/evidence 和 5E-B rebinding evidence。

## Diagnostic Output Boundary

Machine audit 仍只允许 raw bytes/size/SHA、canonical digest、query-set/order counts、schema/type/discrete/float/ULP/semantic aggregate counts、最多一个 salted query-ID hash，以及 fingerprints/cleanup booleans。不得输出 raw query ID、raw decision row、field value、question/text、ranking、policy、source-audit content、Gold 或 U1-D effect metrics。不得对 `null` 做填充、转换或 normalization。

## Explicitly Not Requested

本请求不授权：

- 在新的 5E-B package-bound 批准前执行任何命令；
- 超过一次 formal preflight 或一次 exact capture，或任何失败后的自动重试；
- 修改 helper、preflight helper call、capture command、token string、comparator 或任何代码/数据/模型/参数；
- 使用 inline PowerShell 重写 path-equivalence 算法；
- 读取或 hash official rankings、reference policy、source-audit 文件、5C-B inventory、evaluator/Gold、reservation 或 Stage3B；
- 完整 controller、verifier、evaluator 或正式输出提升；
- 修改 raw-byte equivalence、effective-K、q25、score、ECDF、budget、trigger、ranking、endpoint 或 stop rule；
- 创建、重建、覆盖、迁移或删除 cache、official artifact、历史 evidence 或 failure record；
- 诊断后自动恢复 pre-Gold execution。

## Mandatory Stop

若未来成功完成，状态只能是：

```text
AMENDMENT_5E_B_OFFICIAL_DECISIONS_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW
HARD_FAILURE_4_DIAGNOSIS_COMPLETE_AWAITING_REVIEW
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

本 package 当前状态仍为：

```text
AMENDMENT_5E_A_SYNTHETICALLY_VERIFIED
AMENDMENT_5E_B_AWAITING_APPROVAL
FORMAL_PREFLIGHT_RETRY_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
