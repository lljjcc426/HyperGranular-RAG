# Stage4B-U1-D v2.3.1 Synthetic Rebinding Audit

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-13
- Request-package commit: `e76c921454697d1784b0d76a9d9677113051f0f6`
- Implementation commit: `34349c70ee24b8240fd169393134d4280968b790`
- Approval-governance commit: `53850f58e57f51b3c6067ed3108edff6b99a2dfc`
- Evidence: `results/stage4b_u1_d_pregold_resumption_v2_3_1_synthetic_rebinding.json`
- Evidence bytes: `11640`
- Evidence SHA-256: `9D40C0B9B0C8F03CBC5545CA8F2390CCE9EABDC3B08B041B092FB3A76492FF34`
- Result: `SYNTHETIC_REBINDING_VERIFIED`
- Formal preflight executed: No
- Official development/source audit/cache/ranking accessed: No
- Gold/reservation/Stage3B accessed: No

## 执行命令

以下命令在同一批准治理提交上完整执行两次：

```text
python scripts/stage4b_u1_run_synthetic_verification.py \
  --output results/stage4b_u1_d_pregold_resumption_v2_3_1_synthetic_rebinding.json \
  --governance-binding docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_APPROVAL_REQUEST.md \
  --governance-binding docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_MANIFEST.json \
  --governance-binding docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_APPROVAL_DECISION.md
```

第一遍开始前，本地 HEAD、`origin/main` 与 GitHub `main` 均为批准治理提交，tracked worktree clean，evidence 路径不存在。第二遍仍使用同一 HEAD 和未修改的治理/实现字节；唯一新增工作区文件是第一遍生成的目标 evidence，第二遍按预注册路径重写该 synthetic evidence。

## 双次结果

| 项目 | 第一遍 | 第二遍 |
|---|---:|---:|
| tests run | 50 | 50 |
| failures | 0 | 0 |
| errors | 0 | 0 |
| skipped | 0 | 0 |
| evidence bytes | 11640 | 11640 |
| evidence SHA-256 | `9D40C0B9B0C8F03CBC5545CA8F2390CCE9EABDC3B08B041B092FB3A76492FF34` | `9D40C0B9B0C8F03CBC5545CA8F2390CCE9EABDC3B08B041B092FB3A76492FF34` |

两次完整 evidence 字节一致。两次均报告：

- `official_development_data_accessed = false`
- `official_source_audit_loaded_by_tests = false`
- `reservation_data_accessed = false`
- `stage3b_accessed = false`
- `synthetic_artifacts_persisted = false`

## 治理与实现绑定

Evidence 记录 22 个 implementation file hashes，其中批准后最终：

```text
AGENTS.md
61100B48AA236A523E55A44A53FD6240F5089AF827FC08DFFBDC4DFC8F1787BF
```

动态治理绑定为：

```text
docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_APPROVAL_REQUEST.md
6340983A03DA2EBB1468E230B0E5474254B7FDF461E1E3504FC301B59443CDBA

docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_MANIFEST.json
19C7EA88218CF5A01A824AD603E02FFF6C8B8B0C72CECCA304267B23DA859F85

docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_APPROVAL_DECISION.md
CDA72DED67108DC1AA0D77E7BC37809871295D7A246B90CA2C1676BA652D2F09
```

只读复算确认四项实际文件 hash 均与 evidence 一致。

## 命令与环境记录

1. 批准治理提交后的首次前置核对错误地硬编码了不存在的完整 SHA `53850f583de07f330199ec6b45d0d8f87d746aac`，因此命令最终退出 `1`。同一输出已经证明本地、tracking、GitHub 实际提交均为 `53850f58e57f51b3c6067ed3108edff6b99a2dfc`，worktree clean 且 evidence 路径不存在；没有写文件或调用实验入口。后续均绑定 Git 实际返回的完整 SHA。
2. 两次 runner 均在 stderr 输出 NumPy 2.4.6 与当前 `numexpr` 二进制 ABI 不兼容的导入警告堆栈。该异常由 pandas optional-dependency 路径捕获，runner 两次 exit code 均为 `0`，50 项 unittest 结果均为零 failure/error/skip，完整 evidence 字节一致。该环境警告没有触发 official 数据或 cache 访问。
3. Evidence 的 `status` 保留冻结 runner 的 implementation-stage 常量 `AMENDMENT_4_CACHE_FAIL_CLOSED_SYNTHETICALLY_HARDENED_AWAITING_OFFICIAL_RESUMPTION_APPROVAL`。它不是当前治理授权状态；当前批准由已提交 approval decision 的动态 hash 和批准治理提交共同证明。未修改 runner 或 evidence schema 来改写该冻结实现字段。

## 结论与下一门

批准后的 synthetic rebinding 硬门通过。只有本 evidence、audit 与状态更新提交并推送至 `main` 后，才允许按批准运行一次只读 formal preflight。此结论不授权 Gold evaluation、U1-D 指标、reservation、Stage3B、cache 写入、实现变更或自动重跑。

本阶段新增本 audit 和 rebinding evidence；修改 README、Roadmap 与复现状态。没有删除文件，也没有改动 `AGENTS.md`、approval request、manifest、approval decision 或实现文件。
