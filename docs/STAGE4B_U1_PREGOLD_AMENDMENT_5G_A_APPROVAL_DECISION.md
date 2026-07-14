# Stage4B-U1-D Pre-Gold Amendment 5G-A 批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-14
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_A_DERIVED_EXECUTION_HEAD_BINDING_HELPER_IMPLEMENTATION_SYNTHETIC_ONLY`
- Amendment 5G-A package commit: `86ae4a83d55e61653f3cce9260a00852b4aaebda`
- Hard Failure 8: `0f35ec895c756348e8a10803c6dd961a37344fb0`
- Amendment 5F-B rebinding/governance: `052e8ecc04f566b75666d5cc96df74d2ed5061e4`
- Amendment 5F-B approval governance: `84d39707dee15729dc0c35c85a16f4e31dac89e4`
- Amendment 5F-B package: `f33ee70233ea4098b2d7a17cfde3d266081ee693`
- Amendment 5F-A implementation/evidence: `e7b688d4b67db596df1d447e2cf70f12f0ea5d0b`
- Amendment 5F-A approval governance: `273341960858930246ae0c1441440aede0403a65`
- Amendment 5F-A package: `2b82ba3f0ac9756091d74567f4aed8df5cdf626d`
- Hard Failure 7: `f18d551b17f1bbed645ac159ebe52b7d6b9d8e54`
- Hard Failure 4: `b21852a174b537c90a848699deb4d26d6f169506`
- v2.3.1 implementation: `34349c70ee24b8240fd169393134d4280968b790`
- Official execution: `NOT_AUTHORIZED`
- Other project conversations, thread tools, and global memory used: No

## 正式审批结论

批准 Stage4B-U1-D Pre-Gold Amendment 5G-A：Derived Execution-HEAD Binding Helper 的实现与 synthetic verification。

本批准严格绑定 package commit `86ae4a83d55e61653f3cce9260a00852b4aaebda` 及上述历史提交。未绑定该 package commit 的批准无效。

## 唯一允许的实现范围

只允许修改：

```text
scripts/stage4b_u1_preflight_execution_head_binding.py
tests/test_stage4b_u1_preflight_execution_head_binding.py
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
```

前两个必须为新文件。Runner 只允许绑定 5G-A request、Manifest、本批准决定、新测试和 active proofs，更新完整 suite 下限，输出 deterministic 5G-A evidence，并记录新增 helper 的零访问、零执行证明。不得修改既有测试文件。

## Helper 冻结契约

Helper 必须为 deterministic、standard-library-only、fail-closed 的纯值校验器。Git、GitHub、文件系统和治理事实只能由 caller 取得并传入；helper 自身不得获取这些事实。

Helper 必须：

1. 对全部 commit 值要求严格小写 40 位十六进制字符串；
2. 拒绝短 SHA、39/41 位、非十六进制、大写、空值和非字符串；
3. 要求 `local_head == origin_main == github_main`，并返回该经验证的 current HEAD；
4. 不得接收 `expected_head`、future rebinding SHA 或任何同义预填 current HEAD；
5. 要求 `head_parent == approval_governance_commit`，不得以祖先关系替代直接 parent；
6. 要求 changed paths 与 caller 提供的 allowed path set 精确集合相等；
7. 要求全部 required ancestors 出现在 observed ancestor set；
8. 要求 worktree clean；
9. 要求 governance binding 的 package/approval commit 精确匹配，并报告 rebinding evidence、governance binding、rebinding audit 等必要工件存在；
10. 返回 value-free metadata，不得泄漏治理文件或 changed-file 内容。

核心原则为：

```text
derive and validate the current execution HEAD
not pre-transcribe the future execution HEAD
```

## Changed-Path 策略

Changed paths 必须是 repository-relative text，按精确集合比较，并拒绝：

- duplicate；
- absolute path；
- `..` parent traversal；
- missing 或 extra path；
- code、existing test、results、cache 或 experiment artifact path 混入未来 rebinding commit。

未来 official package 中的 `allowed_rebinding_paths` 必须来自已哈希绑定、package-bound 的 Manifest，不得由 wrapper 临时构造、扩展或缩减。

## 禁止的 Helper 行为

Helper 不得访问 filesystem 或治理文件，不得运行 Git、`gh`、subprocess 或 GitHub API，不得访问 official paths，不得调用 typed argument-policy helper、path-equivalence helper、capture 或 comparator，不得使用 authorization token。

源码、默认参数、常量和测试 fixture 均不得固定任何未来 rebinding commit。

## Synthetic 硬门

冻结基线为 205 tests，其中 typed-policy tests 为 44。至少新增 16 项 execution-head-binding tests，最终完整 suite 不少于 221 项。

测试必须覆盖三方完整 SHA 相等和逐位置漂移、同短前缀完整 SHA 不同、全部 malformed SHA、direct-parent、changed-path exact set、duplicate/absolute/traversal/forbidden paths、required ancestor、clean worktree、governance package/approval、必要工件存在、public API 无 `expected_head`、源码无固定 future SHA、no-filesystem/Git/subprocess/helper/token/capture active proofs 和 value-free output。

完整 suite 必须在完全相同 tracked bytes 上连续运行两次，两次均满足：

```text
tests >= 221
execution-head-binding tests >= 16
failures = 0
errors = 0
skipped = 0
official access = 0
typed-helper official invocation = 0
path-helper official invocation = 0
formal preflight invocation = 0
authorization token use = 0
official capture invocation = 0
evidence byte-identical = true
```

## Implementation Audit

审计必须记录三个获批文件的精确 diff，允许文件和 24 个冻结文件的 bytes/SHA，全部执行及失败命令，定向测试，两轮完整 suite、tracked-byte digest、evidence bytes/SHA 与直接字节比较，以及 no-fixed-future-HEAD 和全部零访问/调用证明。

## 冻结边界

Typed helper、path helper、capture、comparator、common、controller、retrieval、全部既有 tests、32-element exact capture command、raw-byte controlling gate、数据、cache、模型和科研参数全部冻结。Manifest 登记的 frozen hashes 和 exact-command boundary 不得漂移。

## 明确不授权

- real Git/GitHub execution-head validation；
- 第二次 formal preflight；
- typed/path helper official call；
- official input metadata/content access；
- authorization token 或 official capture；
- controller、verifier、evaluator/Gold；
- reservation、Stage3B 或 5G-B package assembly；
- implementation/evidence 审核前自动恢复 Hard Failure 8。

## 强制停止状态

实现、两轮 synthetic evidence、audit、commit 和 push 完成后必须立即停止等待独立审核。允许状态仅为：

```text
AMENDMENT_5G_A_SYNTHETICALLY_VERIFIED
HARD_FAILURE_8_DIRECT_CAUSE_CONFIRMED
HARD_FAILURE_4_DIAGNOSIS_INCOMPLETE

SECOND_FORMAL_PREFLIGHT_NOT_APPROVED
TYPED_HELPER_OFFICIAL_CALL_NOT_APPROVED
PATH_HELPER_OFFICIAL_CALL_NOT_APPROVED
OFFICIAL_INPUT_ACCESS_NOT_APPROVED
AUTHORIZATION_TOKEN_USE_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
