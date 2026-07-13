# Stage4B-U1-D v2.2 Official Pre-Gold Synthetic Rebinding 审计

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-13
- Approval decision: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_2_APPROVAL_DECISION.md`
- Approval governance commit: `c13be1f`
- Bound request-package commit: `fae181564504f1a69bcebfd5d5201eea7e2d9abf`
- Bound implementation commit: `ca2cca332292f7bd6af12e2a429100be11da5549`
- Runner: `scripts/stage4b_u1_run_synthetic_verification.py`
- Canonical evidence: `results/stage4b_u1_synthetic_verification.json`
- Gate result: `PASS_BYTE_IDENTICAL`
- Official development data accessed: No
- Official source audit loaded: No
- Reservation accessed: No
- Stage3B accessed: No

## 执行结果

批准治理提交 `c13be1f` 推送后，在该治理字节上依次运行两次完整 synthetic binding verification。两次运行均为：

- tests: `24`
- failures: `0`
- errors: `0`
- skipped: `0`
- complete output SHA-256: `9B01C80F66096F01C763C25E44E4D079C40B681F6C52F0CC55F70492689EAAB1`

两次 SHA-256 完全相同，因此完整输出字节一致。canonical evidence 中登记的 12 个 implementation/governance 文件 hash 与当前文件逐项复核，差异数为 `0`。

Runner 中的 `status` 字段仍使用实现时冻结的 synthetic 阶段标签；该字段不替代当前批准治理状态。当前执行门由批准决定与本审计共同确定为：synthetic rebinding 已通过，允许进入一次 dual-ID formal preflight。

## 边界

本审计不包含 official development、official source audit、Gold、U1-D 指标、reservation 或 Stage3B。未运行 channel preparer、controller、cache、formal verifier 或 evaluator。下一步仅允许执行批准顺序中的一次只读 dual-ID formal preflight；任一硬门失败立即停止且不得自动重跑。
