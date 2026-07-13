# Stage4B-U1-D Pre-Gold Amendment 3 实现审计

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Mode: implementation validation, synthetic-only
- Audit date: 2026-07-13
- Amendment ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_3`
- Approval-package commit: `42747507d6f37c3d5713949de443311b35262a2d`
- Failure-audit commit: `8b43de72418ccda85af3015f758c39bce9d31411`
- Approval-governance commit: `c185cebc0ac81346cdcf0c0f5ff70d7ef41e18e2`
- Implementation checkpoint: `stage4b_u1_v2_3`
- Status: `SYNTHETICALLY_VERIFIED_OFFICIAL_EXECUTION_NOT_AUTHORIZED`
- Official development accessed: No
- Official source audit accessed: No
- Existing official ranking content accessed: No
- Official cache accessed or modified: No
- Reservation accessed: No
- Stage3B accessed: No
- Gold evaluation: Not run
- Other project conversations, thread tools, and global memory used: No

## 实现结论

Amendment 3 的 effective-K verifier 修正已经完成。independent verifier 现在从每条查询的候选池 `C_q` 独立计算：

```text
K_q = min(20, |C_q|)
P_q = min(10, K_q)
```

verifier 对 dense、q25、final 的实际长度、列表内唯一性、候选池成员关系、effective protected prefix、planned insertion 范围、inserted-ID 独立推导和 trigger 对应的 final selector 执行硬门。空候选池继续硬失败；query schema 中的 `num_candidate_units` 必须等于 verifier 从 units 独立计数得到的候选数。

本修订只修正 verifier 对既有 controller 输出的结构验证，不修改 candidate generation、retrieval、controller、evaluator、模型、`max_length`、batch size、q25、score、ECDF、预算、trigger、ranking、endpoint 或停止规则。

## 文件级变更

| 文件 | 变更 |
|---|---|
| `AGENTS.md` | 冻结 v2.3 effective-K 实现边界、33 项 synthetic suite 和 official 停止门 |
| `docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md` | 写入 `K_q`、`P_q`、长度/唯一性/成员/前缀/插入/final selector 规则 |
| `scripts/stage4b_u1_common.py` | implementation checkpoint 更新为 `stage4b_u1_v2_3` |
| `scripts/stage4b_u1_verify.py` | 独立构造并核验候选池；按 effective-K 验证 ranking 结构和 insertion 推导 |
| `scripts/stage4b_u1_run_synthetic_verification.py` | 绑定 Amendment 3 治理文件、状态、属性和专用 evidence 路径 |
| `tests/test_stage4b_u1_goldfree.py` | 保留原 24 项并新增 9 项 effective-K/candidate-pool hardening tests |

`scripts/stage4b_u1_prepare_channels.py`、`scripts/stage4b_u1_goldfree_retrieval.py`、`scripts/stage4b_u1_goldfree_controller.py` 和 `scripts/stage4b_u1_evaluate.py` 均未修改。commit `9207bd78eea44d2ea3291fe9b6748526969a3224` 中的失败工件、fresh cache 和 legacy cache 均未覆盖、删除或迁移。

## Synthetic 验证

新增 hardening 覆盖：

1. 合法 `K=17`；
2. 合法 `K=10` 与零 insertion 容量；
3. 错误列表长度；
4. 重复 unit ID；
5. 非候选 unit ID；
6. candidate count 漂移；
7. 空候选池；
8. effective protected prefix 漂移；
9. insertion 推导漂移。

有效的定向 discovery 运行结果：

```text
9 tests
0 failures
0 errors
0 skipped
```

完整 verbose suite 结果：

```text
33 tests
0 failures
0 errors
0 skipped
```

完整 evidence runner 在最终 `AGENTS.md`、协议、实现和测试字节上连续运行两次。两次均为 33/33，且完整 evidence 字节一致：

```text
38DDA409C866AAAC6C2AEDBA0D0716DA6F483854E9A6019E9040B9B2B1FA40B5
```

Evidence 文件：`results/stage4b_u1_d_pregold_amendment_3_synthetic_verification.json`。旧 `results/stage4b_u1_synthetic_verification.json` 未覆盖，其 SHA-256 仍为 `9B01C80F66096F01C763C25E44E4D079C40B681F6C52F0CC55F70492689EAAB1`。

## 失败命令记录

第一次定向命令错误地把非 package 的 `tests/` 当作 `tests.test_stage4b_u1_goldfree` 导入，产生 9 个 `ModuleNotFoundError`；测试方法没有执行。确认原因为命令入口后，改用仓库既有的 `unittest discover -s tests` 入口。随后 9 项定向测试、33 项完整 suite 和两次完整 evidence runner 全部通过。该入口错误不计入正式 complete-suite evidence，但在此保留，不作删除或隐瞒。

## Evidence 绑定的文件 Hash

| 文件 | SHA-256 |
|---|---|
| `AGENTS.md` | `AB71999E867E5C7B5C8C3E629392F8503BBEBDC79C62152F29AB29103D86C94B` |
| `docs/STAGE4B_U1_EXECUTION_HARDENING_V2_1.md` | `A85420942DC8A5DF8EAF468464B94E0DD2826AE7EBFC6318D503FDA2D40E4873` |
| `docs/STAGE4B_U1_EXECUTION_PACKAGE_REVIEW_1.md` | `D7028F83B99AF171DCBD1CCCC40AA3F0A8C39849BCCCED7C262303EFC76DC28A` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_APPROVAL_DECISION.md` | `3857B9F693450624095370C822CC3F71F3552880D7623FFA0D3CE14B335C9B8B` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_APPROVAL_REQUEST.md` | `642A086F46DDD1B953C67EE4D42705C3B704B3D3FD993E4E568EF54BD6E88048` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_DRAFT.md` | `D4D71058EA82D3CCA795F271E0A533254C8EF3585F58F6EC2C1A426AD54B2430` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_MANIFEST.json` | `E382646AC91B0206CFD5A15433EBC84686C5FE8BC2B7C15D8DF034FFD5901102` |
| `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_3.md` | `A30D003267D87CF8604530C54480C238F5DE71FC0B9B238DC1AA3F387641B996` |
| `docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md` | `AB2D4C389492D509740D6CE8F7462C44A7A0B6A5BF04B65B210123AF93EE785B` |
| `scripts/stage4b_u1_common.py` | `09032D7B68194E3FB4152B103D5779496B6935B9A73EA06D33CBC8270A6D08D2` |
| `scripts/stage4b_u1_evaluate.py` | `343BC9D2478042FF582DAA5DE716498124166C72A520A35DAE53F56C976F2E31` |
| `scripts/stage4b_u1_goldfree_controller.py` | `713BC1DF19472EFE692A2A042A39F96DEE2DCB93187B177EE10DDB5AD7C7A752` |
| `scripts/stage4b_u1_goldfree_retrieval.py` | `3B50FAFD057E2565167ED09288D61829B3FBD044991F139F734F819955038A3B` |
| `scripts/stage4b_u1_prepare_channels.py` | `BF629382DCD93F9FD64F0DEB0D441DC775725040E51CE4155884023CE29FD76C` |
| `scripts/stage4b_u1_run_synthetic_verification.py` | `5DD0DFFF648139C77A7B6D5AFACE837BB05D5D23706495BD606E4034A3A4A32C` |
| `scripts/stage4b_u1_verify.py` | `DC134B51A07C14A553746C303EA31D83990BA0EFAD30EFC3A1722F1A141E66EC` |
| `tests/test_stage4b_u1_goldfree.py` | `BA956F88E310D28C5758BB7C7E30079D81424209483B5C8D8478A0F18535876B` |

## 证据边界与停止门

- 所有测试只使用 OS 临时目录中的 synthetic fixtures；
- 未读取 official development、official source audit 或现有 official ranking 内容；
- 未运行 official preflight、channel preparer、controller、cache 流程、official verifier 或 evaluator；
- 未读取或解释 Gold/U1-D 指标，未访问 reservation 或 Stage3B；
- 未创建、覆盖、删除或迁移 official 工件与 cache；
- 本审计不构成 `VERIFIED_PRE_GOLD`，也不授权 official execution。

v2.3 实现与 synthetic evidence 提交推送后，只能创建 implementation-bound official pre-Gold 恢复审批包。审批包推送后必须停止，等待用户明确批准。
