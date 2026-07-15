# Stage4B-U1-D Pre-Gold Amendment 5G-B 批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-15
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_DERIVED_EXECUTION_HEAD_BOUND_SINGLE_PREFLIGHT_AND_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC`
- Package commit: `f281864b424c406b42718c4ec58d7266ecafd9a3`
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_OFFICIAL_DIAGNOSTIC_APPROVAL_REQUEST.md`
- Request SHA-256: `7EC6120EF92967D3B882723D97A723B3C580D24042E503089A3CC9667CD73ED6`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_MANIFEST.json`
- Manifest SHA-256: `DE5CB3486CBE4A7D3F9884472C258B267AE6BBD8CE8A477D54ACB9109A8B059F`
- Controller/verifier/Gold: `NOT_AUTHORIZED`
- Other project conversations, thread tools, and global memory used: No

## 正式审批结论

批准 Stage4B-U1-D Pre-Gold Amendment 5G-B：derived execution-HEAD 绑定、单次 formal preflight，以及仅在全部先决门通过后执行一次 unchanged official decisions-only diagnostic。

本批准严格绑定 package commit `f281864b424c406b42718c4ec58d7266ecafd9a3`、上述 Request/Manifest 和以下历史提交：

```text
5G-A.1 package:
d02b19dfd5a527d0159b930662f5a868c8235d35

5G-A.1 approval governance:
3d818cee86e1faca16c2bdab3baf4fd5411cff75

5G-A.1 implementation/evidence:
c21f3f58b2b1d4ccf235daba9c85937daedf4e3b

Hard Failure 9:
d1c7cf9d78563e30a1e0fe0d6812b36d15b95a9a

Hard Failure 8:
0f35ec895c756348e8a10803c6dd961a37344fb0

5F-B rebinding/governance:
052e8ecc04f566b75666d5cc96df74d2ed5061e4

5F-B approval governance:
84d39707dee15729dc0c35c85a16f4e31dac89e4

5F-B package:
f33ee70233ea4098b2d7a17cfde3d266081ee693

Hard Failure 4:
b21852a174b537c90a848699deb4d26d6f169506

v2.3.1 implementation:
34349c70ee24b8240fd169393134d4280968b790
```

## 冻结实现与 Evidence

```text
execution-head helper:
517C5C4DB22A82B4CBCA3D8BB751AAE60C0DCC5B5948CC8419D8770A9CC3D174

deterministic runner:
83816A962EDC8F06B53B5826E3F7519BD72D2CA0DF91C46751A9B12215867F28

execution-head tests:
EA39A9ECEBA36FE2BAA108B2C4B1C98981C8A5E3FE241F59F22F5D49458E02B8

5G-A.1 deterministic evidence:
A6285498FCFE767297D7156B87CA6034A993B2DFBB167EF7DFA813E9ADD55292
```

Typed helper、path helper、capture、comparator、32-element exact command、数据边界、cache、模型、参数、raw-byte controlling gate 与停止规则均按 Manifest 冻结。

## 唯一执行顺序

1. 提交并推送本批准决定与最终批准版 `AGENTS.md`；
2. 在最终批准治理字节上运行恰好两次完整 246-test suite；
3. 两轮均须 246/246、41 execution-head、44 typed-policy、零 failure/error/skip/official/helper/preflight/token/capture，并且完整 evidence 字节一致；
4. 创建并推送唯一三路径 rebinding/governance direct-child commit；
5. 从实际 local/origin/GitHub/parent/paths/ancestors/worktree/governance facts 调用一次冻结 execution-head helper；
6. helper 通过后运行唯一一次 A/B/C/D formal preflight；
7. 只有全部先决门通过后运行一次 Manifest 中 unchanged 32-element capture；
8. 只核验 aggregate machine audit、pre/post fingerprints、temporary cleanup、内容边界与 formal-output absence；
9. 提交并推送精确两路径 final diagnostic audit，确认 GitHub 后立即停止。

## Approval-Governance Scope

本提交 changed-path set 必须精确为：

```text
AGENTS.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_APPROVAL_DECISION.md
```

该提交推送并确认 local HEAD、`origin/main`、GitHub `main` 三方一致前，禁止运行 synthetic、helper、preflight、official input、token 或 capture。

## Post-Approval Rebinding

冻结 runner 必须恰好运行两次，不得 preliminary、targeted、修复性运行或第三次运行。每轮必须精确满足：

```text
tests = 246/246
execution-head tests = 41
typed-policy tests = 44
failures/errors/skips = 0/0/0
tracked files = 33
official/helper/preflight/token/capture counters = 0
```

Run 1 写唯一 OS-temp evidence；run 2 exclusive-create `results/stage4b_u1_d_pregold_amendment_5g_b_synthetic_rebinding.json`。两轮必须使用相同 tracked bytes，且 evidence 完整逐字节一致。Run 1 只有在两轮及直接字节比较全部通过后才可删除。

## Rebinding/Governance Direct Child

两轮通过后，只允许创建一个 approval-governance commit 的直接子提交，changed-path set 精确为：

```text
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_SYNTHETIC_REBINDING_AUDIT.md
results/stage4b_u1_d_pregold_amendment_5g_b_governance_binding.json
results/stage4b_u1_d_pregold_amendment_5g_b_synthetic_rebinding.json
```

Governance binding 必须登记 package/approval commit、三个 required artifact presence，以及 Manifest 要求的 11 项 bound files 的 path/bytes/SHA。不得登记自己的 SHA；execution-head commit 作为外部内容绑定。

## Derived Execution-HEAD Validation

三路径 direct-child 推送同步后，先 hash-verify helper，再从实际环境独立取得 local HEAD、`origin/main`、GitHub `main`、direct parent、changed paths、observed ancestors、clean worktree 和 committed governance binding。`validate_execution_head_binding(...)` 只能调用一次，禁止 expected/future/rebinding HEAD 字面量、inline implementation 或 fallback。

必须验证三方 HEAD 相等、parent 为本批准治理 commit、changed paths 精确三项、已知 ancestors 与 package/approval ancestors 齐全、worktree clean、governance package/approval 匹配、三个 artifacts 为 true，并返回 `VALIDATED_EXECUTION_HEAD_BINDING`。失败即停止，不得进入 preflight。

## Single A/B/C/D Formal Preflight

Derived HEAD validation 通过后，只允许一次 formal preflight：

- A：验证 Git/governance/ancestry、历史 `AGENTS.md` Git blob、其余 32 项 accepted hashes、post-approval 全部 33 hashes、governance binding、helper/capture/comparator/runner/test hashes，以及所有输出与 temp residue 缺失；A 不得读取 official input metadata/content。
- B：hash-bind typed helper 与 5F-B Manifest，直接调用一次 `validate_capture_argv(actual, approved)`，要求 32 elements、15 flags、7 path roles、0 prohibited roles、actual 等于 approved。
- C：hash-bind path helper，以原始 `.NET System.IO.Path.GetTempPath()` 和精确 `C:\Users\cc\AppData\Local\Temp` 调用一次；禁止 trim/replace/rewrite/手工规范化。
- D：仅在 A/B/C 通过后读取 units、queries、controller channel audit、ID-bound cache 和 v2.2 reference decisions，按 Manifest 核验路径、regular-file、SHA、boundary、cache metadata 与 pre/post fingerprints。

Source-audit file、rankings、reference policy、5C-B inventory、evaluator/Gold、reservation 与 Stage3B 禁止访问。

## Conditional Single Capture And Final Audit

仅当 approval、两轮 rebinding、byte comparison、三路径 direct-child、derived HEAD validation 和 A/B/C/D 全部通过时，才可使用冻结 token 运行一次 unchanged capture。只允许 exclusive-create：

```text
results/stage4b_u1_d_pregold_amendment_5b_official_decisions_diagnostic.json
```

不得生成或提升 formal decisions、rankings、policy、controller audit 或 `VERIFIED_PRE_GOLD`。Raw-byte equality 继续为唯一控制门；canonical/semantic 只能解释差异。

成功后的最终提交 changed-path set 精确为：

```text
results/stage4b_u1_d_pregold_amendment_5b_official_decisions_diagnostic.json
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_OFFICIAL_DIAGNOSTIC_AUDIT.md
```

不得在该提交修改任何治理状态文件、脚本、测试、Manifest 或历史 evidence。

## 一次性调用与失败规则

```text
post-approval complete synthetic runs: 2
preliminary/targeted synthetic runs: 0
derived execution-head helper official call: 1
formal preflight: 1
typed helper official call: 1
path helper official call: 1
official capture: 1
automatic retry: false
```

任何 gate 失败都立即消耗对应授权并停止。禁止第三次 synthetic、第二次 helper、第二次 preflight、第二次 capture 或现场修改后重试。失败审计只能记录失败前已获准访问的事实，不得越过尚未开放的后续边界。

## 明确不授权

- 任何代码、测试、数据、模型、参数、cache、equivalence 或 stop-rule 修改；
- full controller、verifier、evaluator/Gold 或 formal-output promotion；
- official rankings、reference policy、source-audit file、5C-B inventory、reservation 或 Stage3B；
- 修改、覆盖、迁移或删除 cache、official artifacts、历史 evidence 或 failure records；
- 失败后自动恢复或诊断完成后自动继续 official pre-Gold。

## 成功后的强制状态

```text
AMENDMENT_5G_B_OFFICIAL_DECISIONS_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW
HARD_FAILURE_4_DIAGNOSIS_COMPLETE_AWAITING_REVIEW

CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
