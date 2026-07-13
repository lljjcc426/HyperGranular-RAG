# Stage4B-U1-D v2.3.1 Official Pre-Gold 恢复批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-13
- Decision: `APPROVE_STAGE4B_U1_D_V2_3_1_OFFICIAL_PREGOLD_RESUMPTION`
- Request-package commit: `e76c921454697d1784b0d76a9d9677113051f0f6`
- Implementation commit: `34349c70ee24b8240fd169393134d4280968b790`
- Request: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_APPROVAL_REQUEST.md`
- Manifest: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_MANIFEST.json`
- Authorized endpoint: `VERIFIED_PRE_GOLD` with `evaluation = null`
- Gold evaluation: `NOT_AUTHORIZED`
- Reservation: `KEEP_LOCKED`
- Stage3B: `KEEP_LOCKED`

## 正式审批结论

批准 Stage4B-U1-D v2.3.1 official pre-Gold 恢复执行。本批准严格绑定上述恢复审批包提交与 v2.3.1 实现提交；未发现新的阻断问题。

## 唯一允许的执行顺序

1. 提交并推送本批准决定及批准后的最终治理状态。
2. 在 clean HEAD 上完整运行 50 项 synthetic suite 两次，同时绑定 approval request、manifest、approval decision 和最终 `AGENTS.md`；两次必须均为 50/50、零 failure/error/skip 且完整 evidence 字节一致。
3. 提交并推送 synthetic rebinding evidence 与 audit；此前不得进入 formal preflight。
4. 运行一次只读 formal preflight，核验提交同步、22 个 implementation files、4,500/143,820 双 ID 边界、fresh/legacy cache、v2.2 等价工件以及十个正式路径不存在。
5. preflight 全部通过后，仅在 manifest 登记路径运行一次 versioned channel preparation；Gold map 仅留在 evaluator channel，不运行 evaluator。
6. 以 `require-existing`、冻结 cache SHA 和冻结 reference policy 运行一次 Gold-free controller；必须通过 cache 前后指纹、v2.2 decisions/rankings 字节等价、policy 限定字段差分、pending-output 与 exclusive promotion/rollback 门。
7. 独立核验并提交推送 channel audit、decisions、rankings、policy 和 controller audit。
8. 仅在已提交工件上运行一次 independent verifier，不传入 Gold/evaluator 参数。
9. verifier 仅允许生成 `status = VERIFIED_PRE_GOLD`、`evaluation = null`；提交推送并核对 GitHub 后立即停止。

任一硬门失败必须立即停止，不得自动重跑或进入下一步。

## 冻结执行参数与等价门

```text
--embedding-cache-mode require-existing
--expected-embedding-cache-sha256 69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D
--reference-policy E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_policy.json

decisions SHA-256:
6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7

rankings SHA-256:
ED289D234F6F4FEC58A48168CB6CA78950489CD5F5640E977068CA6A786E03CB

reference policy SHA-256:
829E8A0DB7E4108C4D23F2D0CE3DD0C227F329E9EDF77BB4ED49C20544EC07DC
```

policy 仅允许 manifest 登记的八个绑定字段变化。十个正式路径必须以 manifest 的 `artifact_registry` 为唯一注册表，执行前全部不存在。

## 继续禁止

- Gold evaluation，以及任何 U1-D retrieval metric、gain/harm、retention、CR/ER 或 false-insert 的读取、解释或结论；
- U1-D 晋级、停止或有效性结论；
- reservation 与 Stage3B；
- 修改数据、实现、模型、effective-K、q25、score、ECDF、预算、trigger、ranking、endpoint 或停止规则；
- 编码、创建、重建、覆盖、删除或迁移 fresh/legacy cache；
- 覆盖、删除或改写 v2.2 失败工件；
- 任一硬失败后的自动重跑。

本决定不授权超出 `VERIFIED_PRE_GOLD` 的任何操作。

## 治理组装核验记录

- 首次 PowerShell 核对错误地对 `git diff --quiet` 的无输出结果直接取布尔反值，导致 request/manifest 被显示为 changed；该命令没有写文件。
- 改用 `$LASTEXITCODE` 后，request 与 manifest 相对绑定提交 `e76c921454697d1784b0d76a9d9677113051f0f6` 的 diff exit code 均为 `0`，确认两个绑定文件未修改。
