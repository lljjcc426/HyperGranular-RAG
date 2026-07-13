# Stage4B-U1-D Pre-Gold Amendment 4 实现审计

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Mode: implementation validation, synthetic-only
- Audit date: 2026-07-13
- Amendment ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_4`
- Amendment 4 package commit: `e5a0e2187e770c9d7b9e9a85a6b8e91067ed2af1`
- Approval-governance commit: `f227156f086023aa3f1beae0859818ef8d89821d`
- Returned v2.3 package: `dbb4e057405069aceda5a7c5d88d9d39a4d14775`
- Baseline implementation: `a1d9ea0c517fcbad1ef27e78e760738d5c04d8b3`
- Implementation checkpoint: `stage4b_u1_v2_3_1`
- Status: `SYNTHETICALLY_VERIFIED_OFFICIAL_EXECUTION_NOT_AUTHORIZED`
- Official development/source audit/ranking/cache accessed: No
- Gold evaluation: Not run
- Reservation accessed: No
- Stage3B accessed: No
- Other project conversations, thread tools, and global memory used: No

## 实现结论

Amendment 4 已完成 cache fail-closed、pending outputs、恢复等价门、governance binding 和十路径 registry 实现。formal controller 现在强制：

```text
--embedding-cache-mode require-existing
--expected-embedding-cache-sha256 <frozen SHA>
```

formal `load-or-build` 会在输入文件读取前硬失败。require-existing 模式在任何模型加载、编码或正式输出前核验 cache path、SHA、bytes、exact six members、unit/query ID 同序、model/max-length、dtype、shape、finite 和 normalization；该分支不调用 `embed_texts`、`Path.mkdir` 或 `np.savez_compressed`。

controller 只在 OS temporary directory 生成 pending decisions/rankings/policy。cache 后指纹、v2.2 decisions/rankings byte-equivalence、reference-policy SHA 和限定字段 policy diff 全部通过后，才以 exclusive-create 提升正式 outputs。复制失败或提升后 cache 漂移会回滚本次新建的正式 outputs。

## 文件级变更

| 文件 | 变更 |
|---|---|
| `AGENTS.md` | 冻结 v2.3.1、50 项 suite 与 official 停止门 |
| `docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md` | 写入 cache、pending/equivalence、十路径和 post-approval rebinding 规则 |
| `scripts/stage4b_u1_common.py` | checkpoint、cache 指纹、v2.2 等价 hash 与十路径常量 |
| `scripts/stage4b_u1_goldfree_controller.py` | require-existing、strict cache validation、pending outputs、policy diff、promotion rollback |
| `scripts/stage4b_u1_run_synthetic_verification.py` | Amendment 4 tracked hashes、registered governance binding 与专用 evidence |
| `tests/test_stage4b_u1_goldfree.py` | 保留原 33 项并新增 17 项 cache/governance hardening |

`scripts/stage4b_u1_prepare_channels.py`、`scripts/stage4b_u1_goldfree_retrieval.py`、`scripts/stage4b_u1_verify.py` 和 `scripts/stage4b_u1_evaluate.py` 未修改。v2.2 失败工件、fresh cache、legacy cache 和全部 official paths 未读取、覆盖、删除或迁移。

## Cache 与 Pending Hardening

新增验证覆盖：

1. 正确 synthetic existing cache 通过，且 `embed_texts`、`Path.mkdir`、`np.savez_compressed` 均未调用；
2. cache 缺失时在正式输出前失败；
3. SHA/bytes 漂移拒绝；
4. exact member drift 拒绝；
5. unit/query ID 顺序漂移拒绝；
6. model、max-length、dtype、shape、finite、normalization 漂移拒绝；
7. 计算期间 cache 后指纹漂移阻止正式输出提升；
8. 正式 load-or-build 在输入读取前拒绝；
9. policy 只允许登记 binding fields 漂移；
10. promotion 复制中断会删除本次部分输出。

## Governance Binding Hardening

runner 的附加治理 binding：

- 只接受登记的 repo-relative path；
- 拒绝缺失、repo 外、重复、未登记或未提交到当前 HEAD 的文件；
- evidence 记录 canonical repo-relative path 和 SHA-256；
- Amendment 4 实现 evidence 的动态 binding 集为空，因为本次 request/manifest/approval decision 已固定进入 22 个 `implementation_hashes`；
- future official-resumption 批准后必须显式绑定新的 approval request、manifest、approval decision，并先于 formal preflight 完成两次 rebinding。

manifest 与 shared constants 对十个 `v2_3_1` artifact paths 的逐项相等测试通过。

## Synthetic 验证

定向 hardening：

```text
17 tests
0 failures
0 errors
0 skipped
```

完整 suite：

```text
50 tests
0 failures
0 errors
0 skipped
```

完整 evidence runner 在最终 AGENTS、协议、实现、runner 和测试字节上连续运行两次。两次均为 50/50，完整 evidence 字节一致：

```text
24F287F9B71C974ABEF9E03AA55BCCA0C4AF9809AB2ADC44705A42EC3889F657
```

Evidence：`results/stage4b_u1_d_pregold_amendment_4_synthetic_verification.json`。旧 Amendment 3 evidence 未覆盖，SHA-256 仍为 `38DDA409C866AAAC6C2AEDBA0D0716DA6F483854E9A6019E9040B9B2B1FA40B5`。

## Evidence 绑定的文件 Hash

| 文件 | SHA-256 |
|---|---|
| `AGENTS.md` | `5C1A0BB9D23D9B3E49D9C3555D92AD093EF947AF7CA4E3D39D6FC5D6FFB4C77E` |
| `docs/STAGE4B_U1_EXECUTION_HARDENING_V2_1.md` | `A85420942DC8A5DF8EAF468464B94E0DD2826AE7EBFC6318D503FDA2D40E4873` |
| `docs/STAGE4B_U1_EXECUTION_PACKAGE_REVIEW_1.md` | `D7028F83B99AF171DCBD1CCCC40AA3F0A8C39849BCCCED7C262303EFC76DC28A` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_APPROVAL_DECISION.md` | `3857B9F693450624095370C822CC3F71F3552880D7623FFA0D3CE14B335C9B8B` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_APPROVAL_REQUEST.md` | `642A086F46DDD1B953C67EE4D42705C3B704B3D3FD993E4E568EF54BD6E88048` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_DRAFT.md` | `D4D71058EA82D3CCA795F271E0A533254C8EF3585F58F6EC2C1A426AD54B2430` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_MANIFEST.json` | `E382646AC91B0206CFD5A15433EBC84686C5FE8BC2B7C15D8DF034FFD5901102` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_APPROVAL_DECISION.md` | `25D4733885A31872D9F768593B0A8E3A5E6B340A01262CB8293D684B81B2452F` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_APPROVAL_REQUEST.md` | `F321AE118DFAAB9B8361FD9102F944AED117947AA698F0C51308A23C613D4B1F` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_CACHE_FAIL_CLOSED_DRAFT.md` | `53B6E8A6EDBA8E476D8DBFA0836CAFD946B453BFA224EC5517A2ADA735CCBEDB` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_MANIFEST.json` | `CDC3F08582CFE7D10DA4AF2AB8B470FDE3522CAEDA353C36251CD3018F4A8E92` |
| `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_3.md` | `A30D003267D87CF8604530C54480C238F5DE71FC0B9B238DC1AA3F387641B996` |
| `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_REVIEW_1.md` | `F89D923AB1B5E8D5AA6A1CAE328B6ACF5218372180A28D744DBA7A674079EB90` |
| `docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md` | `6C71F646667FDA22259B37FCE75334DC9D6A7DC006791AC8946AA9DC7325C56F` |
| `scripts/stage4b_u1_common.py` | `CDF7EAD6007DABE389ED0BD18983496F75290C32243FE6DF84716810CDE92CE4` |
| `scripts/stage4b_u1_evaluate.py` | `343BC9D2478042FF582DAA5DE716498124166C72A520A35DAE53F56C976F2E31` |
| `scripts/stage4b_u1_goldfree_controller.py` | `C18AD3B672649BA846C5E191D0DBBAC7644A926D4B8CCD39176127175BBA7C1F` |
| `scripts/stage4b_u1_goldfree_retrieval.py` | `3B50FAFD057E2565167ED09288D61829B3FBD044991F139F734F819955038A3B` |
| `scripts/stage4b_u1_prepare_channels.py` | `BF629382DCD93F9FD64F0DEB0D441DC775725040E51CE4155884023CE29FD76C` |
| `scripts/stage4b_u1_run_synthetic_verification.py` | `3C7DE76E0CC54102E47017A2114C0E3206D03BE8E81F916E806E4E6AECE72026` |
| `scripts/stage4b_u1_verify.py` | `DC134B51A07C14A553746C303EA31D83990BA0EFAD30EFC3A1722F1A141E66EC` |
| `tests/test_stage4b_u1_goldfree.py` | `CA61B466C7DDF583D827FD2D99C024D646BA3962C80B9137D480C84DEA374C71` |

## 证据边界与停止门

- 所有测试只使用 OS 临时目录中的 synthetic fixtures 和 synthetic caches；
- 未读取 official development、source audit、official ranking、v2.2 policy 内容或真实 official cache；
- 未运行 official preflight、channel preparer、controller、cache audit、verifier 或 evaluator；
- 未创建、覆盖、删除或迁移 official cache 与 v2.2 失败工件；
- 未运行 Gold evaluation，未读取 U1-D 指标，未访问 reservation 或 Stage3B；
- 本结果不构成 `VERIFIED_PRE_GOLD`，也不授权 official execution。

实现/evidence 提交推送后，只能创建新的 implementation-bound official pre-Gold 恢复审批包。该包推送后必须停止，等待新的明确批准。
