# Stage4B-U1-D Pre-Gold Amendment 5F-B Synthetic Rebinding Audit

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-14
- 5F-B package: `f33ee70233ea4098b2d7a17cfde3d266081ee693`
- 5F-B approval governance: `84d39707dee15729dc0c35c85a16f4e31dac89e4`
- Evidence: `results/stage4b_u1_d_pregold_amendment_5f_b_synthetic_rebinding.json`
- Governance binding: `results/stage4b_u1_d_pregold_amendment_5f_b_governance_binding.json`
- Status: `AMENDMENT_5F_B_POST_APPROVAL_SYNTHETIC_REBINDING_VERIFIED`
- Other project conversations, thread tools, and global memory used: No

## 执行顺序

1. 将 5F-B 批准决定和最终批准版 `AGENTS.md` 提交并推送；
2. 核对本地 `HEAD`、GitHub `main` 均为 `84d39707...`，工作区干净；
3. 核验冻结 runner 为 18,120 bytes、SHA-256 `31F2233C...59D7F`；
4. 确认正式 rebinding evidence 路径不存在；
5. 在同一最终治理字节上连续运行两次完整 suite；
6. 第一轮写入全新 OS 临时快照，第二轮写入正式 5F-B evidence；
7. 两轮成功后直接比较完整字节；
8. 字节一致后删除第一轮 OS 临时快照。

没有运行第三次 suite，也没有自动重试。

## 两轮结果

```text
run 1 exit: 0
run 2 exit: 0
tests each run: 205/205
typed-policy tests each run: 44
failures/errors/skips: 0/0/0
official metadata/content access: 0
path-helper official invocations: 0
formal preflight invocations: 0
authorization token uses: 0
official capture invocations: 0
tracked file count: 26
tracked-byte digest:
0BA07EC11A82125DE5B11C12ED618096106E3802FA7E897CAB302508AC739DD5
evidence bytes: 51922
run 1 SHA-256:
829289F10B1C7B39BBE6B37ACF51DCB265764FD10A8DA55892F60D50F6D2CB09
run 2 SHA-256:
829289F10B1C7B39BBE6B37ACF51DCB265764FD10A8DA55892F60D50F6D2CB09
direct byte comparison: true
run 1 OS-temp snapshot deleted: true
```

Runner 的 evidence stage/status 继续使用冻结的 5F-A 命名；本审计不修改 runner 字节。该 evidence 在本阶段的职责是绑定最终批准治理下的当前 26 项 runner-tracked 字节。

## Governance Binding

机器绑定文件逐项登记以下八项的 bytes 与 SHA-256：

- 5F-B request；
- 5F-B Manifest；
- 5F-B approval decision；
- 最终批准版 `AGENTS.md`；
- 5F-A Review 1；
- 5F-A implementation audit；
- 5F-A deterministic evidence；
- 5F-B synthetic rebinding evidence。

职责严格分离：205-test evidence 绑定当前 26 项 runner-tracked 实现/治理字节；governance-binding JSON 额外绑定 5F-B package/approval/rebinding 材料。没有声称冻结 runner 直接包含全部 5F-B package 文件。

## 边界

- 未访问任何 official input metadata/content；
- 未调用 typed helper official boundary、path helper official boundary 或 formal preflight；
- 未使用 authorization token；
- 未运行 capture、comparator、controller、verifier 或 evaluator/Gold；
- 未读取 rankings、reference policy、source-audit 文件、5C-B inventory、reservation 或 Stage3B；
- 未修改任何代码、测试、科研参数、equivalence、cache 或历史工件；
- 未删除仓库文件。唯一删除项是完成逐字节比较后的第一轮 OS 临时 evidence 快照。

下一步只有在本 evidence、governance binding 和本审计提交并推送后，才允许运行唯一一次 A→B→C→D formal preflight。
