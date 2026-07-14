# Stage4B-U1-D Pre-Gold Amendment 5F-A 批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-14
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5F_A_TYPED_CAPTURE_ARGUMENT_POLICY_IMPLEMENTATION_SYNTHETIC_ONLY`
- Amendment 5F-A package commit: `2b82ba3f0ac9756091d74567f4aed8df5cdf626d`
- Hard Failure 7: `f18d551b17f1bbed645ac159ebe52b7d6b9d8e54`
- Amendment 5E-B rebinding/governance: `3185c3bd4ffd3eb2bc61b52fdf18a3367b9dca76`
- Amendment 5E-B approval governance: `f2f2e249e4e7a52fcc44b61a2245d8d50d79106d`
- Amendment 5E-B package: `e387d2707ede9024571249face71bf7ca3afd4e0`
- Amendment 5E-A implementation/evidence: `a8b064a4a2133aea27cbe9b85978237fc3dae661`
- Amendment 5E-A approval governance: `461939434206764555b917c5971956e6951ff4dd`
- Amendment 5E-A package: `19f16f559f0b1f3b59ef24a04e368f99ae3635e3`
- Hard Failure 6: `bebfeb5664f26795b8d3472f3729ca1bb9abf889`
- Hard Failure 4: `b21852a174b537c90a848699deb4d26d6f169506`
- v2.3.1 implementation: `34349c70ee24b8240fd169393134d4280968b790`
- Official execution: `NOT_AUTHORIZED`
- Other project conversations, thread tools, and global memory used: No

## 正式审批结论

批准 Stage4B-U1-D Pre-Gold Amendment 5F-A：typed capture-argument policy helper 实现与 synthetic 验证。

本批准严格绑定 package commit `2b82ba3f0ac9756091d74567f4aed8df5cdf626d` 及上述历史提交。未绑定该 package commit 的批准无效。

## 允许修改文件

```text
scripts/stage4b_u1_preflight_argument_policy.py
tests/test_stage4b_u1_preflight_argument_policy.py
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
```

前两个路径必须新增。现有 runner 只允许绑定 5F-A request、Manifest、本批准决定、新测试与 active proofs，将完整 suite 下限提高到 177，记录 typed-policy no-access/call evidence，并输出 deterministic 5F-A evidence。不得修改其他已有实现或测试文件。

## Helper 冻结契约

Helper 必须为标准库、deterministic、fail-closed，并接收调用方提供的 `actual_argv` 与 `approved_argv`。Helper 自身不得读取 Manifest、路径或任何文件。

控制结构固定为：

```text
exact argv equality
typed flag allowlist
per-role exact value binding
explicit prohibited-role rejection
```

Helper 必须固定 `python` executable、`scripts/stage4b_u1_capture_diagnostic_decisions.py` capture script、32 个 argv 元素和 Manifest 登记的 15 个有序 flag。每个 flag 必须恰好一次；unknown、duplicate、missing、reordered、extra value 和 extra positional argument 均须拒绝。

七个路径角色必须执行 Windows 绝对路径语法检查并精确绑定 approved value。Model 必须是非空精确字符串；batch size 与 max length 必须是 canonical positive decimal；四个 SHA 必须是 64 位大写十六进制；token 只能精确绑定，不得使用或消费。

冻结的 `pregold` audit-output 路径必须通过。禁止对任意 value 使用裸 `gold` 子串分类，包括 `in`、`find`、`contains`、`IndexOf`、正则或任何拆分、编码、包装变体。

显式禁止角色至少包括：

```text
--rankings
--policy
--gold-map
--source-audit
--evaluator
--reservation
--stage3b
```

Helper 禁止调用 `open`、`os.stat`、`os.lstat`、`Path.stat`、`hashlib`、`subprocess`、capture module 或 path-equivalence helper。不得执行命令、访问文件系统、读取 official 内容、检查路径 metadata、使用 token 或包含 execution authority。

## Synthetic 硬门

冻结基线为 161 项、36,518 bytes、SHA-256 `BF4C668C76C4B8545882C894F241038765AFD8DD263B4195D9E2D654B7B9FC1A`。至少新增 16 项，最终完整 suite 必须不少于 177 项。

必须覆盖 exact approved argv、`pregold`、普通 value 中的 `gold`、结构漂移、七路径逐项漂移、token 漂移、每个 prohibited role、malformed integer/SHA，以及 no-filesystem/hash/subprocess/capture/token/path-helper 和 no-raw-gold-denylist active proofs。

完整 suite 必须在完全相同 tracked bytes 上连续运行两次，且两次均满足：

```text
tests >= 177
failures = 0
errors = 0
skipped = 0
official metadata/content access = 0
path-helper official invocation = 0
formal preflight invocation = 0
authorization token use = 0
official capture invocation = 0
evidence byte-identical = true
```

Manifest 登记的 17 个冻结文件必须保持原 SHA。Exact argv、token、scientific parameters 和 raw-byte equivalence 继续冻结。

## Implementation Audit

审计必须记录 helper、runner、test 精确 diff，所有允许文件与 17 个冻结文件 SHA，全部命令及失败命令，定向和完整测试，两轮 tracked-byte digest、evidence bytes/SHA、直接字节比较，以及所有访问/调用计数为 0 的证明。

## 强制停止边界

5F-A 完成后只允许推送 implementation/evidence commit、同步必要治理文档，然后立即停止等待独立审核。不得在本次授权下组装 5F-B package。只有独立审核明确接受 5F-A implementation/evidence 后，才可另行组装 5F-B。

## 明确不授权

- official input metadata/content access；
- 真实 OS-temp path helper 调用；
- formal preflight、authorization token use 或 official capture；
- official comparator、controller、verifier、evaluator/Gold；
- reservation、Stage3B 或 5F-B package assembly；
- 重试 5E-B；
- 修改科研参数、cache、历史 evidence 或 failure record。

## 完成后状态

```text
AMENDMENT_5F_A_SYNTHETICALLY_VERIFIED
HARD_FAILURE_7_DIRECT_CAUSE_CONFIRMED
HARD_FAILURE_4_DIAGNOSIS_INCOMPLETE

FORMAL_PREFLIGHT_RETRY_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
