# Stage4D-CMA 关闭声明

## Material Passport

- Origin Skill: academic-research-suite / academic-pipeline
- Origin Mode: plan
- Origin Date: 2026-07-20
- Verification Status: VERIFIED CLOSURE OF EXISTING EVIDENCE
- Scientific Result: `CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE`

## 冻结状态

```text
STAGE4D_FINAL_VERIFICATION_PASSED
STAGE4D_CMA_CLOSED
CURRENT_CONTROLLER_BRANCH_FROZEN_CLOSED
NO_ACTIVE_CONTROLLER_DEVELOPMENT
RESERVATION_REMAINS_LOCKED
STAGE3B_REMAINS_LOCKED
U2_NOT_AUTHORIZED
```

Stage4D-CMA 已完成 Gold-free Channel A、development-Gold Channel B、固定 grouped OOF probe、确定性复跑、独立验证、bounded provenance audit 与 final verification。唯一 advancement panel 的 Task-C `COMBINED_DEPLOYABLE_28` 得到 AUROC `0.64310 [0.55520, 0.72974]`、AP `0.72198`、Brier `0.26321`；它没有同时通过冻结 AUROC 与 Brier 门，也没有触发全 panel stop rule。因此最终结论保持 `CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE`。

该结果是同一 4,500-query development 上的有效探索性机制证据，不是执行失败，也不是外部 efficacy 验证。它不能支持 U2、部署 candidate selector、访问 reservation/Stage3B，或否定静态 HyperGranular-RAG 本身。

## 关闭范围

以下工作线在当前语义下关闭：

- Stage4B-U1-D 的 query-level 无标签 controller；
- Stage4C 基于同一 development 的 query-level failure-mechanism 延伸；
- Stage4D 基于同一 development 的 candidate-level panel/model/threshold 延伸；
- 根据既有 Stage4D 结果事后筛选 budget region、feature panel、candidate subset 或阈值；
- 在未建立全新 Level A 科学语义时创建 U2 或 replacement controller。

以下边界保持不变：

- 不重跑或覆盖 Stage4D Channel A、Channel B、probe、decision、report 和 final verification；
- 不修改 8,467 candidate labels、2,446 query folds、68,588 OOF predictions 或 36 个 bootstrap 区块；
- 不访问 reservation、Stage3B 或任何新 Gold；
- 不把 Task A/B 的事件识别能力表述为 gain/harm selector efficacy。

## 冻结证据入口

| 证据 | 路径 / 身份 |
|---|---|
| Level A protocol | `docs/STAGE4D_CANDIDATE_MARGINAL_UTILITY_AUDIT_PROTOCOL.md` |
| candidate labels | `6,229,542` bytes / `E206895E36FB7472502E8FEA082C1AEA7C7AD2CB7E198F37200B271E7164F9E3` |
| counterfactual summary | `5,189` bytes / `37A57AD7AB2760C8C9E368F359C80B378F51C6B5C38629BDC0A75ECEB5D6C9F1` |
| OOF predictions | `13,335,718` bytes / `29EC13EC6AEAB28837C3EBBE24F99AF496A98B0793475DADF2BA071FFEE7ECDC` |
| metrics | `117,023` bytes / `22C843E248D0EB44893E42FB61D207061E8F9E07744A4C808AB8F55D63226999` |
| decision | `120` bytes / `7EE774CA97722353DEC7D71E5B461FEF17ADA08DDCB96568C988A1497B72FA68` |
| final verification | `results/stage4d_cma_verified_final.json` |
| scientific report | `reports/超粒球RAG_Stage4D_CMA候选边际效用归因审计报告.md` |

## 与 Stage4E 的隔离

Stage4E-E2E 不是 controller 的继续训练或修补。它只比较两条固定检索臂：Dense 与不带 U1/controller 的静态 all-query q25 protected insertion，并在相同生成器、相同提示、相同上下文预算和一条此前未读的数据边界上评价答案质量。

Stage4E 不读取或利用 Stage4D label、OOF probability、feature panel、candidate decision 或 Gold target 来生成 ranking。Stage4D 关闭结论不会因 Stage4E 的正、负或不确定结果而被改写。
