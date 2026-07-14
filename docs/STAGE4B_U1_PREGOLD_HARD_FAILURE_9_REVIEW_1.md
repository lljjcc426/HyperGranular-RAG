# Stage4B-U1-D Pre-Gold Hard Failure 9 Review 1

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Review date: 2026-07-14
- Hard Failure 9 checkpoint: `d1c7cf9d78563e30a1e0fe0d6812b36d15b95a9a`
- 5G-A approval governance: `fd50bc30f5acbf4955e3a051fbee70062e6e168c`
- 5G-A package: `86ae4a83d55e61653f3cce9260a00852b4aaebda`
- Decision: `RETURN_FOR_AMENDMENT_5G_A_1_PACKAGE`
- Official execution: `NOT_AUTHORIZED`
- Other project conversations, thread tools, and global memory used: No

## Independent Review Decision

```text
ACCEPT_HARD_FAILURE_9_AUDIT
FREEZE_5G_A_FAILED_CHECKPOINT_FOR_MINIMAL_REPAIR
RETURN_FOR_AMENDMENT_5G_A_1_PACKAGE

TEST_NAME_AND_SUFFIX_REPAIR_NOT_APPROVED
SYNTHETIC_RETRY_NOT_APPROVED
REAL_EXECUTION_HEAD_CHECK_NOT_APPROVED
SECOND_FORMAL_PREFLIGHT_NOT_APPROVED
OFFICIAL_INPUT_ACCESS_NOT_APPROVED
AUTHORIZATION_TOKEN_USE_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

Hard Failure 9 的停止处理和审计均被接受。当前只授权组装 5G-A.1 审批包，不授权直接修改或重跑。

## Accepted Chain And Failed Checkpoint

```text
5G-A package:
86ae4a83d55e61653f3cce9260a00852b4aaebda

5G-A approval governance:
fd50bc30f5acbf4955e3a051fbee70062e6e168c

Hard Failure 9 checkpoint:
d1c7cf9d78563e30a1e0fe0d6812b36d15b95a9a

Hard Failure 8:
0f35ec895c756348e8a10803c6dd961a37344fb0

5F-B rebinding/governance:
052e8ecc04f566b75666d5cc96df74d2ed5061e4
```

批准治理只新增批准决定并更新 `AGENTS.md`。批准后到失败 checkpoint 的实现变化严格限于原获批三个路径；其余变化仅为失败审计和状态文档。没有修改其他脚本、既有测试、results、数据或实验工件。

## Confirmed Failure Boundary

- 唯一一次 execution-head 定向测试：41/41，零 failure/error/skip；
- 唯一一次 preliminary runner 在 `unittest.TextTestRunner.run()` 前停止；
- 完整 suite 实际执行数：0；
- 临时 output 未创建；
- evidence 未写入或删除；
- 24 个 Manifest frozen files 保持原 SHA；
- official/helper/preflight/token/capture/controller/verifier/Gold/reservation/Stage3B 访问或调用均为 0。

两个全局重名测试为：

```text
test_missing_governance_binding_is_rejected
test_helper_uses_only_python_standard_library
```

第二个 suffix 还在 runner 的 `REQUIRED_ACTIVE_PROOF_SUFFIXES` 中重复登记。Runner 的 uniqueness 门正确 fail-closed，没有任意选择同名测试。

## Frozen Helper Baseline

对 failed checkpoint 中 helper 的源码审核未发现独立 blocker。它继续冻结为最小修正包的只读实现基线：

```text
path:
scripts/stage4b_u1_preflight_execution_head_binding.py

bytes:
6318

SHA-256:
517C5C4DB22A82B4CBCA3D8BB751AAE60C0DCC5B5948CC8419D8770A9CC3D174
```

5G-A.1 不得修改该 helper。

## Permitted Package Request Direction

未来 5G-A.1 只应申请修改：

```text
tests/test_stage4b_u1_preflight_execution_head_binding.py
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
```

允许申请的修正仅限：

1. 将两个冲突测试改为 execution-head 专属名称，不改 assertion、fixture、input 或 helper semantics；
2. 同步修改 runner 对应 suffix；
3. 通用 `test_helper_uses_only_python_standard_library` 只保留给既有 path-equivalence test 一次；
4. 在 test discovery 前加入 suffix tuple 自身唯一性硬门；
5. 将最终门冻结为精确 246 tests、41 execution-head tests、44 typed-policy tests。

未来执行不得安排 preliminary runner。获批后顺序只能是：approval governance 提交推送、source-only active-proof inventory、一次 41/41 定向测试、最终稳定字节上的两轮 246/246、直接 evidence 字节比较、audit/commit/push、立即停止。

## Current Boundary

本 Review 1 只允许组装 5G-A.1 package。以下继续禁止：

```text
NO TEST RENAME
NO RUNNER REPAIR
NO SYNTHETIC RETRY
NO HELPER CHANGE
NO REAL EXECUTION-HEAD CHECK
NO SECOND FORMAL PREFLIGHT
NO OFFICIAL INPUT ACCESS
NO TOKEN OR CAPTURE
NO CONTROLLER OR VERIFIER OR GOLD
NO 5G-B PACKAGE
```

Current state:

```text
HARD_FAILURE_9_AUDIT_ACCEPTED
5G_A_FAILED_CHECKPOINT_FROZEN
RETURN_FOR_AMENDMENT_5G_A_1_PACKAGE
```
