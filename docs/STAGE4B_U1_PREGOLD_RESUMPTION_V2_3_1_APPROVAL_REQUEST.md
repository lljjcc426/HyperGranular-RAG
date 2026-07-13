# Stage4B-U1-D v2.3.1 Official Pre-Gold 恢复审批请求

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-13
- Request ID: `STAGE4B_U1_D_V2_3_1_PREGOLD_RESUMPTION`
- Amendment 4 package commit: `e5a0e2187e770c9d7b9e9a85a6b8e91067ed2af1`
- Amendment 4 implementation commit: `34349c70ee24b8240fd169393134d4280968b790`
- Returned v2.3 package: `dbb4e057405069aceda5a7c5d88d9d39a4d14775`
- Failed v2.2 artifact commit: `9207bd78eea44d2ea3291fe9b6748526969a3224`
- Machine-readable manifest: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_MANIFEST.json`
- Current execution approval: `NOT_APPROVED`
- Requested gate: official U1-D pre-Gold resumption only
- Gold evaluation: `NOT_REQUESTED`
- Reservation: `KEEP_LOCKED`
- Stage3B: `KEEP_LOCKED`
- Other project conversations, thread tools, and global memory used: No

## 审批请求

请求批准：

```text
APPROVE_STAGE4B_U1_D_V2_3_1_OFFICIAL_PREGOLD_RESUMPTION
```

本请求只恢复 official U1-D pre-Gold 顺序：批准治理、两次 governance-bound synthetic rebinding、一次只读 formal preflight、一次新 versioned channel、一次 existing-cache-only Gold-free controller、独立等价核验、工件冻结提交和一次 independent verifier。目标只到：

```text
status = VERIFIED_PRE_GOLD
evaluation = null
```

推送 verifier 工件后必须立即停止，不接触 Gold evaluation。

## Implementation Evidence

- Implementation checkpoint: `stage4b_u1_v2_3_1`
- Implementation commit: `34349c70ee24b8240fd169393134d4280968b790`
- Audit: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_IMPLEMENTATION_AUDIT.md`
- Synthetic evidence: `results/stage4b_u1_d_pregold_amendment_4_synthetic_verification.json`
- Evidence SHA-256: `24F287F9B71C974ABEF9E03AA55BCCA0C4AF9809AB2ADC44705A42EC3889F657`
- Complete suite: 50 tests, 0 failures, 0 errors, 0 skipped
- Determinism: two complete runner outputs byte-identical
- Official development/source audit/ranking/cache accessed by tests: No
- Gold, reservation, or Stage3B accessed: No

原 33 项测试全部保留，新增 17 项覆盖 cache missing/SHA/bytes/members/IDs/metadata/dtype/shape/finite/normalization/post-fingerprint、pending rollback、formal no-build、policy 限定差分和 governance binding。

## 批准后的唯一执行顺序

### 1. 批准治理与 Synthetic Rebinding

1. 写入 `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_APPROVAL_DECISION.md`，明确绑定本 request-package commit 与 implementation commit `34349c70ee24b8240fd169393134d4280968b790`；
2. 更新 `AGENTS.md`、README、Roadmap 和复现状态，提交并推送批准治理；
3. 在 clean HEAD 上运行以下完整 binding runner 两次：

```text
python scripts/stage4b_u1_run_synthetic_verification.py \
  --output results/stage4b_u1_d_pregold_resumption_v2_3_1_synthetic_rebinding.json \
  --governance-binding docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_APPROVAL_REQUEST.md \
  --governance-binding docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_MANIFEST.json \
  --governance-binding docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_APPROVAL_DECISION.md
```

4. 两次必须 50/50、`0 failure / 0 error / 0 skip`，完整 evidence 字节一致；
5. governance binding hashes 必须包含上述 request、manifest、decision，且 `AGENTS.md` 的 implementation hash 必须对应批准后的最终字节；
6. 提交并推送 rebinding evidence 与 `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_SYNTHETIC_REBINDING_AUDIT.md`；
7. 任一门失败立即停止，不进入 formal preflight，不自动重跑。

### 2. 一次只读 Formal Preflight

preflight 只能读取登记的 official development/source audit、既有 v2.2 hash-bound 工件和 cache metadata/content integrity，不读取 Gold 效果指标。必须核验：

- request-package commit、implementation commit、approval-governance commit、rebinding evidence 均在 `main` 且 GitHub 已同步；
- 22 个 implementation files 与 post-approval evidence hashes 一致；
- official 4,500 queries / 143,820 units、sample/query 双 digest 与 namespace 关系不变；
- fresh cache path、SHA、bytes、six members、ID 同序、model/max-length、dtype、shape、finite 和 normalization 全部符合冻结值；
- legacy cache SHA 不变；
- v2.2 decisions/rankings/reference policy SHA 与冻结值一致；
- Amendment 4 manifest 的十个 `v2_3_1` 绝对路径逐项 `Test-Path == false`；
- 任一路径碰撞或任一 hash/边界漂移立即停止，不运行 channel。

### 3. 一次 Versioned Channel Preparation

使用 manifest 中的准确路径运行一次 official channel preparer。必须：

- 写入新的 v2.3.1 unlabeled units/queries、controller channel audit、evaluator Gold map 和 evaluator audit；
- 不覆盖或删除 v2.2 channel/失败工件；
- 独立核验新 unlabeled units/queries 与 v2.2 冻结字节一致；
- Gold map 只留在 evaluator channel，不传给 controller、policy 或 pre-Gold verifier；
- 不运行 evaluator。

### 4. 一次 Existing-Cache-Only Controller

controller 必须使用：

```text
--embedding-cache-mode require-existing
--expected-embedding-cache-sha256 69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D
--reference-policy E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_policy.json
```

并使用 manifest 登记的 v2.3.1 units、queries、channel audit、decisions、rankings 和 policy 路径。模型固定为 MiniLM、`max_length=192`、`batch_size=64`。

controller 必须在正式输出前通过 cache 前指纹；只在 OS temporary directory 生成 pending outputs；通过 cache 后指纹、v2.2 decisions/rankings bytes 和 reference-policy 限定差分后，才可 exclusive-promote 正式 outputs。任何失败均不得留下三项正式输出，不得编码或写 cache，不得自动重跑。

### 5. 独立核验、提交与一次 Verifier

1. 独立核验 cache SHA/bytes/members 未变化；
2. 新 decisions/rankings SHA 必须分别等于：

```text
6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7
ED289D234F6F4FEC58A48168CB6CA78950489CD5F5640E977068CA6A786E03CB
```

3. 新 policy 只允许 checkpoint、git commit、protocol hash、common/controller/verifier hashes、top-level controller source hash 和 channel-audit input hash 变化；
4. 提交推送新 channel audit、decisions、rankings、policy 和 controller audit；
5. 在已提交工件上运行一次 independent verifier，不传入 Gold/evaluator 参数；
6. verifier 只有在 dual-ID、cache、effective-K、score/ECDF/预算/ranking 和 Git binding 全部通过时，才写 manifest 登记路径中的 `VERIFIED_PRE_GOLD`，且 `evaluation=null`；
7. 提交推送 verifier 工件，核对 GitHub 后立即停止。

## 十个冻结正式路径

十个绝对路径以 `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_MANIFEST.json` 的 `artifact_registry` 为唯一注册表，与 Amendment 4 manifest 和 shared constants 字节语义一致。不得另行命名、覆盖或复用 v2.2 路径。

## 明确不请求授权

- 不运行 Gold evaluation；
- 不读取或解释任何 U1-D retrieval metric、gain/harm、retention、CR/ER 或 false-insert；
- 不作出 U1-D 晋级、停止或有效性结论；
- 不访问 reservation 内容、embedding、decision、ranking 或指标；
- 不访问 Stage3B；
- 不修改数据、实现、模型、effective-K、q25、score、ECDF、预算、trigger、ranking、endpoint 或停止规则；
- 不编码、创建、重建、覆盖、删除或迁移 fresh/legacy cache；
- 不覆盖、删除或改写 v2.2 失败工件；
- 不在任一硬失败后自动重跑。

## 组包核对记录

- 首次只读 Python 核对误用了不存在的 manifest 键 `synthetic_rebinding`，以 `KeyError` 退出；该命令没有写文件，也没有调用实验、official 或 cache 入口。
- 后续只读文本检索因本机 `rg.exe` 返回 `Access is denied` 而退出；已改用 PowerShell `Select-String` 完成同一仓库内核对，没有写文件。
- 首次综合只读 validator 的中文批准短语经 PowerShell here-string 编码后产生假阴性；改用 Unicode 转义后，该短语及 implementation commit、approval token、`VERIFIED_PRE_GOLD`、`evaluation=null` 五项断言全部通过。
- 修正为实际键 `post_approval_synthetic_rebinding` 后核对通过：runner 允许的 3 个治理绑定路径与 manifest 完全一致。
- Python UTF-8 复核确认 frozen cache 和十个 artifact registry 绝对路径中的中文字符正确；PowerShell 默认显示产生的乱码不属于文件内容。

## 审批输出

批准时请明确绑定本审批包所在提交和 implementation commit `34349c70ee24b8240fd169393134d4280968b790`，并写出：

```text
批准 Stage4B-U1-D v2.3.1 official pre-Gold 恢复执行
```

其他措辞若未明确授权上述严格顺序，默认保持 `NOT_APPROVED`。
