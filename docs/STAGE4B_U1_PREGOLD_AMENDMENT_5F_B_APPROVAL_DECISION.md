# Stage4B-U1-D Pre-Gold Amendment 5F-B 批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-14
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5F_B_SINGLE_TYPED_POLICY_PATH_EQUIVALENCE_HELPER_BOUND_PREFLIGHT_AND_CONDITIONAL_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC`
- Amendment 5F-B package: `f33ee70233ea4098b2d7a17cfde3d266081ee693`
- Amendment 5F-A implementation/evidence: `e7b688d4b67db596df1d447e2cf70f12f0ea5d0b`
- Amendment 5F-A approval governance: `273341960858930246ae0c1441440aede0403a65`
- Amendment 5F-A package: `2b82ba3f0ac9756091d74567f4aed8df5cdf626d`
- Hard Failure 7: `f18d551b17f1bbed645ac159ebe52b7d6b9d8e54`
- Amendment 5E-B rebinding/governance: `3185c3bd4ffd3eb2bc61b52fdf18a3367b9dca76`
- Amendment 5E-B approval governance: `f2f2e249e4e7a52fcc44b61a2245d8d50d79106d`
- Amendment 5E-B package: `e387d2707ede9024571249face71bf7ca3afd4e0`
- Hard Failure 4: `b21852a174b537c90a848699deb4d26d6f169506`
- v2.3.1 implementation: `34349c70ee24b8240fd169393134d4280968b790`
- Controller/verifier/Gold: `NOT_AUTHORIZED`
- Other project conversations, thread tools, and global memory used: No

## 正式审批结论

批准 Stage4B-U1-D Pre-Gold Amendment 5F-B：单次 typed-policy/path-equivalence helper-bound formal preflight，以及仅在全部门通过后执行一次 unchanged official decisions-only diagnostic。

本批准严格绑定 package commit `f33ee70233ea4098b2d7a17cfde3d266081ee693` 与上述实现、治理和失败历史。任何未绑定该 package commit 的授权无效。

## 唯一执行顺序

1. 提交并推送本批准决定及最终批准版 `AGENTS.md`；
2. 在最终治理字节上连续运行两次完整 205-test suite；
3. 两次均须 205/205、44 项 typed-policy tests、零 failure/error/skip/official access/path-helper official invocation/formal preflight/token/capture，且完整 evidence 字节一致；
4. 提交并推送 rebinding evidence、governance-binding JSON 和 synthetic rebinding audit；
5. 运行唯一一次 A→B→C→D formal preflight；
6. 只有全部 preflight 门通过后，运行一次 Manifest 中 unchanged 32-element exact capture；
7. 只核验 aggregate machine audit、五项输入 pre/post fingerprint、cache bytes/SHA、temporary cleanup 和 formal-output absence；
8. 提交推送 machine/narrative audit，核对 GitHub 后立即停止。

任一阶段硬失败必须立即停止并形成新的 Hard Failure 审计；禁止第二次 preflight、第二次 typed-helper/path-helper official call、第二次 capture或自动重试。

## Post-Approval Synthetic Rebinding

冻结 runner：

```text
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
bytes: 18120
SHA-256:
31F2233CA9ACF7F156C24B6CD2F0268F7816CC3DE745E783711C2E58E7459D7F
```

Rebinding evidence 负责绑定当前 26 项实现/治理字节；governance-binding JSON 额外绑定 5F-B request、Manifest、approval decision 和 rebinding evidence。不得声称冻结 runner 自身直接包含全部 5F-B package 文件。

## Formal Preflight 冻结顺序

### A. 项目、治理、哈希与输出缺失

- `HEAD == origin/main == GitHub main` 且工作树干净；
- package、approval、implementation、rebinding/governance 为祖先；
- 5F-A evidence bytes/SHA 正确；
- `e7b688d...` 历史 `AGENTS.md` Git blob 匹配旧 evidence hash；
- 当前树其余 25 项 accepted hashes 正确；
- post-approval evidence 的全部 26 项 current hashes 正确；
- typed helper、path helper、capture、comparator、runner、tests bytes/SHA 正确；
- machine/narrative audit、五项 formal outputs 和 OS-temp residue 均不存在。

A 不得访问五项 official input 路径。最终治理 `AGENTS.md` 不得与历史 5F-A hash 直接比较。

### B. Typed Argument-Policy Helper

先核验 helper：

```text
scripts/stage4b_u1_preflight_argument_policy.py
bytes: 7082
SHA-256:
CCDC70D2E66E9D69CD64899676EA5150FEE0381E74F4C9DEED2A0FFB5EE436F4
```

再核验冻结 5E-B Manifest 的 17,286 bytes 与 SHA，从 5F-B/5E-B Manifest 分别读取 actual/approved argv，并直接调用 `validate_capture_argv(actual_argv, approved_argv)`。必须返回 `VALID`、exact equality、32 elements、15 flags、7 path roles、0 prohibited roles及全部 no-access/no-execution 元数据。禁止内联、fallback 或关键词扫描；helper 获批的纯词法 Windows 绝对路径语法检查必须保留。

### C. Windows Path-Equivalence Helper

只有 B 通过后，先核验：

```text
scripts/stage4b_u1_preflight_path_equivalence.py
bytes: 3543
SHA-256:
1A17C0E750F91CEF2F638A0B0C6FD381110692E6B2D467C1F5243ADF3F35B3FF
```

再直接调用 `windows_directories_equivalent(runtime_get_temp_path, r"C:\Users\cc\AppData\Local\Temp")`。Runtime 值必须来自未改写的 `.NET System.IO.Path.GetTempPath()`；不得 trim、replace、normalize 或改写 capture `--temp-parent`。

### D. 五项 Official Inputs

只有 B、C 均通过后才允许访问 Manifest 登记的 unlabeled units、unlabeled queries、controller channel audit、ID-bound embedding cache 和 v2.2 reference decisions。必须核验冻结路径、regular-file、SHA、计数、dual-ID、cache bytes/members/shapes/dtype/model/max length/finite/normalization 和 reference fingerprint。

Stage4A-R2 source-audit 文件、rankings、reference policy、5C-B inventory、Gold、reservation 和 Stage3B 不得访问。

## Conditional Single Capture

只有 A/B/C/D 全部门通过后，才允许 Manifest 中完全不变的 32-element exact command 使用冻结 token 运行一次。Capture 必须保持 decisions-only；不得读取或生成 rankings、构建 policy、运行 full controller/verifier/evaluator 或提升 formal outputs。

Raw-byte equality 继续为控制门；canonical/semantic equality 只能解释差异。Post-run 不得再次语义解析 reference decisions 或 temporary decisions，只能使用 aggregate machine audit 与 fingerprint。

## 明确不授权

- 任何代码或测试修改；
- 第二次 preflight/helper/capture 或失败后自动重试；
- full controller rerun、verifier、evaluator/Gold 或 formal-output promotion；
- rankings、reference policy、source-audit 文件、5C-B inventory、reservation 或 Stage3B；
- 科研参数、equivalence、数据、模型、endpoint 或 stop rule 修改；
- cache、历史工件或失败证据的修改、覆盖、迁移或删除；
- 诊断后自动继续。

## 成功后的强制停止状态

```text
AMENDMENT_5F_B_OFFICIAL_DECISIONS_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW
HARD_FAILURE_4_DIAGNOSIS_COMPLETE_AWAITING_REVIEW
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
