# Stage4B-U1-D Pre-Gold Amendment 5C-B Post-Approval Synthetic Rebinding Audit

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-14
- Package commit: `e5a6c5479dbd125ebb58b95e9594fadde6b6719d`
- Approval governance commit: `fce67da87d155b1026cbe0670f606201ede0ac4b`
- 5C-A implementation/evidence commit: `492a59b2f4daccd3e123f2b6cc49cd896d5009d1`
- Status: `AMENDMENT_5C_B_POST_APPROVAL_SYNTHETIC_REBINDING_VERIFIED`
- Other project conversations, thread tools, and global memory used: No

## 执行结果

在批准决定与最终项目级 `AGENTS.md` 已提交并推送后，使用冻结 runner：

```text
scripts/stage4b_u1_run_schema_inventory_synthetic_verification.py
```

对同一 tracked implementation/governance 工作树连续完整运行两次。两次均得到：

```text
tests: 131/131
inventory tests: 24
failures: 0
errors: 0
skipped: 0
official-path access attempts: 0
```

两次完整 evidence 均为 22,234 bytes，SHA-256 均为：

```text
F16C91BF170ABDFC6784F368D6247E0AA8CDC9ECFB6671C71DFA9BD35CCF297C
```

逐字节比较结果为 `true`。

## 治理绑定

机器可读治理绑定位于：

```text
results/stage4b_u1_d_pregold_amendment_5c_b_governance_binding.json
```

它逐项记录并绑定 5C-B request、Manifest、批准决定、最终批准 `AGENTS.md`、原始 5C-A evidence 与本次 post-approval rebinding evidence 的路径、字节数和 SHA-256，并绑定 package、批准治理及 5C-A implementation/evidence commits。

## 运行环境记录

两轮进程均以退出码 0 完成。测试发现阶段重复出现已知的 NumPy 2.4.6 与旧版 numexpr ABI 警告；该警告没有形成 unittest failure/error/skip，也未改变两轮 evidence。这里按实际日志保留，不将其解释为测试通过之外的额外有效性证据。

## 边界核验

- 未打开 official reference decisions 或其他 official 输入；
- 未运行 official schema scan、capture、controller、verifier 或 evaluator；
- 未读取 rankings、policy、Gold、reservation 或 Stage3B；
- 未修改 comparator、capture、controller、retrieval、common、模型、参数或等价门；
- 未创建 machine schema inventory 或 narrative official audit；
- 未删除或覆盖任何历史文件。

## 下一硬门

只有本 evidence、governance binding 与本审计提交并推送后，才允许执行唯一一次 read-only formal preflight。该 preflight 失败不得重试，也不得消费 schema scan 授权。

