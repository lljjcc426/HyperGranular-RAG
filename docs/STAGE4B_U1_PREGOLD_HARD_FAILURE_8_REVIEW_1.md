# Stage4B-U1-D Pre-Gold Hard Failure 8 Review 1

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Review date: 2026-07-14
- Reviewed Hard Failure 8 commit: `0f35ec895c756348e8a10803c6dd961a37344fb0`
- Amendment 5F-B rebinding/governance: `052e8ecc04f566b75666d5cc96df74d2ed5061e4`
- Amendment 5F-B approval governance: `84d39707dee15729dc0c35c85a16f4e31dac89e4`
- Amendment 5F-B package: `f33ee70233ea4098b2d7a17cfde3d266081ee693`
- Decision: `ACCEPT_HARD_FAILURE_8_AUDIT`
- Rebinding decision: `ACCEPT_AMENDMENT_5F_B_POST_APPROVAL_REBINDING_EVIDENCE`
- Next action: `RETURN_FOR_AMENDMENT_5G_A_PACKAGE`
- Other project conversations, thread tools, and global memory used: No

## Review Decision

Hard Failure 8 的停止处理与审计均被接受。5F-B post-approval rebinding evidence 继续有效；5F-B formal preflight 授权已经消费失败，不能修正完整 SHA 字面量后直接重跑。

当前授权状态：

```text
ACCEPT_HARD_FAILURE_8_AUDIT
ACCEPT_AMENDMENT_5F_B_POST_APPROVAL_REBINDING_EVIDENCE
RETURN_FOR_AMENDMENT_5G_A_PACKAGE

EXECUTION_HEAD_BINDING_FIX_NOT_APPROVED
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

## Accepted Evidence

```text
tests: 205/205
typed-policy tests: 44
failures/errors/skips: 0/0/0
official access: 0
path-helper official invocation: 0
formal preflight invocation: 0
token use: 0
capture invocation: 0
tracked files: 26
tracked-byte digest:
0BA07EC11A82125DE5B11C12ED618096106E3802FA7E897CAB302508AC739DD5
evidence bytes: 51922
evidence SHA-256:
829289F10B1C7B39BBE6B37ACF51DCB265764FD10A8DA55892F60D50F6D2CB09
byte-identical: true
```

Synthetic evidence 绑定当前 26 项 runner-tracked bytes；governance binding 额外绑定 5F-B request、Manifest、approval、最终 `AGENTS.md`、5F-A review/evidence 和 5F-B rebinding evidence。Hard Failure 8 不否定这些结果。

## Confirmed Direct Cause

Formal preflight 读取的 local HEAD、origin/main 与 GitHub main 均为：

```text
052e8ecc04f566b75666d5cc96df74d2ed5061e4
```

Wrapper 手工填写的完整字面量为：

```text
052e8ece1839ff253f8aeb84d5f828377be74829
```

两者只共享短前缀 `052e8ec`。直接原因是 formal-preflight command construction/transcription defect，不是 GitHub/网络漂移、治理 hash、helper、official input、cache 或 capture 失败。

## Required Amendment 5G-A Direction

下一包应为：

```text
Stage4B-U1-D Pre-Gold Amendment 5G-A
Derived Execution-HEAD Binding Helper
Implementation And Synthetic Verification Only
```

建议唯一实现范围：

```text
scripts/stage4b_u1_preflight_execution_head_binding.py
tests/test_stage4b_u1_preflight_execution_head_binding.py
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
```

新 helper 必须从 local/origin/GitHub HEAD、直接 parent、approval commit、changed paths、allowed rebinding paths 和 governance binding 中推导并验证 execution HEAD，不得接收或比较一个事先手抄的未来 rebinding SHA literal。

以当前 205 项为基线，建议新增至少 16 项，使完整 suite 不少于 221 项，并连续运行两次，要求零 failure/error/skip/official access/typed-helper official call/path-helper official call/preflight/token/capture，且 evidence 字节一致。

## Current Boundary

本 review 当前只允许组装 5G-A 审批包，不授权 5G-A implementation 或 synthetic execution，也不授权 5G-B package assembly。

```text
NO REAL FORMAL PREFLIGHT
NO TYPED HELPER OFFICIAL CALL
NO PATH HELPER OFFICIAL CALL
NO OFFICIAL INPUT ACCESS
NO TOKEN
NO CAPTURE
NO CONTROLLER
NO VERIFIER
NO GOLD
NO 5G-B PACKAGE ASSEMBLY
```
