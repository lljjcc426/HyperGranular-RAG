# Stage4B-U1-D Pre-Gold Amendment 4 批准请求

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-13
- Request ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_4`
- Trigger review: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_REVIEW_1.md`
- Returned package commit: `dbb4e057405069aceda5a7c5d88d9d39a4d14775`
- Baseline implementation commit: `a1d9ea0c517fcbad1ef27e78e760738d5c04d8b3`
- Draft: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_CACHE_FAIL_CLOSED_DRAFT.md`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_MANIFEST.json`
- Current approval: `NOT_APPROVED`
- Requested scope: implementation and synthetic verification only
- Official execution: `NOT_REQUESTED`
- Gold/reservation/Stage3B: `KEEP_LOCKED`

## 请求批准

请求批准：

```text
APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_4_CACHE_FAIL_CLOSED_IMPLEMENTATION_SYNTHETIC_ONLY
```

授权范围严格限于：

1. 将 checkpoint 更新为 `stage4b_u1_v2_3_1`；
2. 为 controller 增加 formal `require-existing` cache mode 和 expected-SHA 参数；
3. 增加 cache 前后 fingerprint、strict metadata/content validation 和 no-final-output-on-failure 门；
4. 为 synthetic runner 增加显式附加治理文件 hash binding；
5. 在协议与机器 manifest 中冻结十个 `v2_3_1` official artifact paths；
6. 保留现有 33 项测试并增加 cache fail-closed 与 governance-binding failure injections；
7. 完整 synthetic suite 连续运行两次，要求全部通过且 evidence 字节一致；
8. 形成 implementation audit、完整文件 SHA、提交推送实现/evidence；
9. 创建新的 implementation-bound official pre-Gold 恢复审批包后立即停止。

## 继续禁止

- 不读取 official development、source audit、official ranking 或 cache 内容；
- 不运行 official preflight、channel、controller、cache audit、verifier 或 evaluator；
- 不运行 Gold evaluation或读取任何 U1-D 指标；
- 不访问 reservation 或 Stage3B；
- 不修改 retrieval/effective-K/q25/score/ECDF/预算/trigger/ranking/endpoint；
- 不创建、重建、覆盖、删除或迁移任何 official cache；
- 不覆盖、删除或改写 v2.2 失败工件；
- 不在 synthetic hardening 后自动恢复 official execution。

## 审批输出

批准时请明确绑定本审批包所在提交、returned package commit `dbb4e057405069aceda5a7c5d88d9d39a4d14775` 和 baseline implementation commit `a1d9ea0c517fcbad1ef27e78e760738d5c04d8b3`，并写出：

```text
批准 Stage4B-U1-D Pre-Gold Amendment 4：cache fail-closed 与恢复协议硬化，仅授权实现与 synthetic 验证
```

在该批准明确给出前，任何实现或 official execution 均保持 `NOT_APPROVED`。
