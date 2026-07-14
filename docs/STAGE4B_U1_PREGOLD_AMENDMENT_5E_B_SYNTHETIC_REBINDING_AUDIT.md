# Stage4B-U1-D Pre-Gold Amendment 5E-B Synthetic Rebinding Audit

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-14
- 5E-B package: `e387d2707ede9024571249face71bf7ca3afd4e0`
- 5E-B approval governance: `f2f2e249e4e7a52fcc44b61a2245d8d50d79106d`
- 5E-A implementation/evidence: `a8b064a4a2133aea27cbe9b85978237fc3dae661`
- Status: `AMENDMENT_5E_B_POST_APPROVAL_SYNTHETIC_REBINDING_VERIFIED`
- Formal preflight/token/capture: `0/0/0`
- Other project conversations, thread tools, and global memory used: No

## 执行顺序

1. 5E-B approval decision 与最终批准版 `AGENTS.md` 先形成 commit `f2f2e249e4e7a52fcc44b61a2245d8d50d79106d` 并推送；
2. 确认 `HEAD == origin/main`、工作树干净、5E-B package 与 5E-A implementation/evidence 均为祖先；
3. 核验 23 个 Manifest implementation hashes 及 runner SHA；
4. 确认 rebinding output 在运行前不存在；
5. 在同一批准治理字节上连续运行两次冻结 runner command；
6. 保存第一轮 OS 临时字节快照，第二轮后直接逐字节比较；
7. 比较通过后删除第一轮临时快照。

没有在两轮之间修改 tracked 文件。

## Rebinding 结果

```text
run 1 tests: 161
run 2 tests: 161
failures: 0
errors: 0
skipped: 0
official metadata/content access: 0
formal preflight invocations: 0
authorization token uses: 0
official capture invocations: 0
bytes: 36518
run 1 SHA-256: BF4C668C76C4B8545882C894F241038765AFD8DD263B4195D9E2D654B7B9FC1A
run 2 SHA-256: BF4C668C76C4B8545882C894F241038765AFD8DD263B4195D9E2D654B7B9FC1A
direct byte comparison: true
```

Evidence：

```text
results/stage4b_u1_d_pregold_amendment_5e_b_synthetic_rebinding.json
```

两轮继续出现环境既有的 NumPy 2.4.6/旧 `numexpr` ABI warning，但 runner 均退出 0，警告未形成 unittest failure/error/skip，也未影响 evidence 字节一致性。

## Governance Binding

Machine binding：

```text
results/stage4b_u1_d_pregold_amendment_5e_b_governance_binding.json
```

它绑定以下七项的 SHA-256 与 bytes：

```text
5E-B request
5E-B Manifest
5E-B approval decision
final approved AGENTS.md
5E-A implementation audit
5E-A synthetic evidence
5E-B post-approval rebinding evidence
```

最终批准版 `AGENTS.md` SHA-256 为 `8A8B0CDDD2F8930ABCCA9D6200375D5935C1C10FDF7A30982C59B959736C2D90`。

## 执行边界

- 未运行 formal preflight 或 helper official-boundary check；
- 未传入或使用 authorization token；
- 未运行 official capture/comparator、controller、verifier 或 evaluator；
- 未读取或检查任何 official input metadata/content；
- 未读取 rankings、reference policy、source-audit 文件、5C-B inventory、Gold、reservation 或 Stage3B；
- 未生成 official temporary/formal decisions、rankings、policy 或 `VERIFIED_PRE_GOLD`；
- 未修改 helper、capture、comparator、controller、runtime、exact command 或 raw-byte equivalence；
- 没有删除仓库文件。第一轮 rebinding OS 临时快照在逐字节核验后已删除。

## 下一硬门

本 evidence、governance binding 与 narrative audit 提交推送并核对 GitHub 后，下一项且唯一允许动作是一次 helper-bound read-only formal preflight。Preflight 必须严格执行 A→B→C→D 顺序；任一失败立即停止，不得 capture 或重试。
