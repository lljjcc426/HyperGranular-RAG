# Stage4B-U1-D Pre-Gold Amendment 5G-A.1 批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-14
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_A_1_ACTIVE_PROOF_GLOBAL_UNIQUENESS_MINIMAL_REPAIR_AND_SYNTHETIC_RETRY`
- Amendment 5G-A.1 package commit: `d02b19dfd5a527d0159b930662f5a868c8235d35`
- Amendment 5G-A package: `86ae4a83d55e61653f3cce9260a00852b4aaebda`
- Amendment 5G-A approval governance: `fd50bc30f5acbf4955e3a051fbee70062e6e168c`
- Hard Failure 9 checkpoint: `d1c7cf9d78563e30a1e0fe0d6812b36d15b95a9a`
- Hard Failure 8: `0f35ec895c756348e8a10803c6dd961a37344fb0`
- Amendment 5F-B rebinding/governance: `052e8ecc04f566b75666d5cc96df74d2ed5061e4`
- Hard Failure 4: `b21852a174b537c90a848699deb4d26d6f169506`
- v2.3.1 implementation: `34349c70ee24b8240fd169393134d4280968b790`
- Official execution: `NOT_AUTHORIZED`
- Other project conversations, thread tools, and global memory used: No

## 正式审批结论

批准 Stage4B-U1-D Pre-Gold Amendment 5G-A.1：active-proof 全局唯一性最小修复与 synthetic verification retry。

本批准严格绑定 package commit `d02b19dfd5a527d0159b930662f5a868c8235d35` 及上述历史提交。未绑定该 package commit 的批准无效。

## 唯一允许修改的文件

```text
tests/test_stage4b_u1_preflight_execution_head_binding.py
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
```

Execution-head helper 不得修改，冻结为 6,318 bytes、SHA-256 `517C5C4DB22A82B4CBCA3D8BB751AAE60C0DCC5B5948CC8419D8770A9CC3D174`。

## 精确测试名修复

只允许：

```text
test_missing_governance_binding_is_rejected
-> test_execution_head_missing_governance_binding_is_rejected

test_helper_uses_only_python_standard_library
-> test_execution_head_helper_uses_only_python_standard_library
```

两个测试的 body、assertion、fixture、input、调用次数和语义必须保持不变。不得新增、删除、拆分、合并、参数化或 skip 测试。

## 精确 Runner 修复

Runner 只允许：

1. 同步更新上述两个 execution-head suffix；
2. 通用 `test_helper_uses_only_python_standard_library` 只保留一次并只对应既有 path-equivalence test；
3. 在任何 test discovery 或 test import 前增加 suffix tuple 自身唯一性门；
4. duplicate suffix 使用专用 fail-closed error；
5. 将计数门冻结为 total `246`、execution-head `41`、typed-policy `44`。

不得修改 discovery pattern、其他 active-proof suffix、official-path guard、tracked-file set、evidence schema/output path、access counters、scientific verified properties、helper 或实验语义。

## 唯一执行顺序

1. 提交并推送本批准决定和最终批准治理；
2. 应用精确两文件修复；
3. 在最终修复字节上运行一次 source-only active-proof inventory；
4. inventory 必须证明 tuple 无重复、每个 suffix 全局精确匹配一个 test definition、两个 execution-head 专属名称各一次、通用 path-helper 名称一次；
5. execution-head 定向测试只运行一次且必须 41/41；
6. 在最终稳定且完全相同 tracked bytes 上运行完整 suite 两次；
7. 两轮必须分别精确 246/246；
8. 两份 evidence 逐字节比较；
9. 写 implementation/recovery audit；
10. commit、push、核对 GitHub 后立即停止。

禁止 preliminary complete runner。任一 inventory、targeted、final run、byte comparison、audit、commit 或 push gate 失败，必须停止且不得现场修正或重试。

## 最终 Synthetic 硬门

```text
tests = 246
execution-head tests = 41
typed-policy tests = 44
failures/errors/skips = 0/0/0

official access = 0
typed-helper official invocation = 0
path-helper official invocation = 0
real Git/GitHub execution-head validation = 0
formal preflight invocation = 0
authorization token use = 0
official capture invocation = 0

tracked bytes identical = true
evidence byte-identical = true
```

第一轮写入唯一 OS 临时路径，第二轮写入正式路径 `results/stage4b_u1_d_pregold_amendment_5g_a_synthetic_verification.json`。只有两轮均成功且完整字节相等后，才可删除第一轮临时 evidence。

## Required Audit

Recovery audit 必须记录相对 `d1c7cf9...` 的精确两文件 diff、两个 test-name token-only 证明、runner 限定变化、helper 与 24/24 frozen hashes、source-only inventory 命令/输出、唯一 41/41 定向测试、两轮 246/246、每轮 tracked digest、evidence bytes/SHA/直接相等、无 preliminary runner，以及全部访问/调用计数为 0。

## 冻结与禁止边界

Execution-head helper、24 个 frozen files、全部既有测试、32-element exact capture argv、raw-byte controlling gate、数据、cache、模型、科研参数和 official stop rules 全部冻结。

本批准不授权其他代码/测试/results 修改、preliminary runner、real execution-head check、第二次 formal preflight、typed/path helper official call、official input、token、capture/comparator、controller、verifier、evaluator/Gold、reservation、Stage3B 或 5G-B package assembly。

## 完成后状态

```text
AMENDMENT_5G_A_1_SYNTHETICALLY_VERIFIED
HARD_FAILURE_9_DIRECT_CAUSE_CONFIRMED
HARD_FAILURE_8_DIRECT_CAUSE_CONFIRMED
HARD_FAILURE_4_DIAGNOSIS_INCOMPLETE

SECOND_FORMAL_PREFLIGHT_NOT_APPROVED
OFFICIAL_INPUT_ACCESS_NOT_APPROVED
AUTHORIZATION_TOKEN_USE_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

实现/evidence 推送后必须停止等待独立审核，不得组装 5G-B。
