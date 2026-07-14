# Stage4B-U1-D Pre-Gold Amendment 5E-B 批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-14
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5E_B_SINGLE_HELPER_BOUND_PREFLIGHT_AND_CONDITIONAL_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC`
- Amendment 5E-B package: `e387d2707ede9024571249face71bf7ca3afd4e0`
- Amendment 5E-A implementation/evidence: `a8b064a4a2133aea27cbe9b85978237fc3dae661`
- Amendment 5E-A approval governance: `461939434206764555b917c5971956e6951ff4dd`
- Amendment 5E-A package: `19f16f559f0b1f3b59ef24a04e368f99ae3635e3`
- Hard Failure 6: `bebfeb5664f26795b8d3472f3729ca1bb9abf889`
- Amendment 5D-B rebinding/governance: `2447ad234c160c6e615d81b33dc4ede7ecaa18da`
- Amendment 5D-B approval governance: `1c46dc1b69f8381598aacb9f3b1e27561c7f9ee2`
- Amendment 5D-B package: `f67061e753b03a5cf46d7a7c92b5a95fc79b0ef8`
- Amendment 5D-A implementation/evidence: `02f46447e4cd69a15d2af14ee1fc62f9eb4f8bb9`
- Hard Failure 5: `deccd203059d05dc27ba80aca1ddb1e2ea8f616f`
- Hard Failure 4: `b21852a174b537c90a848699deb4d26d6f169506`
- v2.3.1 implementation: `34349c70ee24b8240fd169393134d4280968b790`
- Controller/verifier/Gold: `NOT_AUTHORIZED`
- Other project conversations, thread tools, and global memory used: No

## 正式审批结论

批准 Stage4B-U1-D Pre-Gold Amendment 5E-B：单次 helper-bound formal preflight，以及仅在全部门通过后执行一次 unchanged official decisions-only diagnostic。

本批准严格绑定 package commit `e387d2707ede9024571249face71bf7ca3afd4e0`、5E-A implementation/evidence commit `a8b064a4a2133aea27cbe9b85978237fc3dae661` 及上述治理历史。更早授权均已消耗，不能用于本次执行。

## 唯一执行顺序

1. 提交并推送本批准决定及最终批准版 `AGENTS.md`；
2. 在最终治理字节上连续运行两次完整 161-test suite；
3. 两次均须零 failure/error/skip/official access/formal-preflight/token/capture，完整 evidence 字节一致；
4. 提交并推送 rebinding evidence、governance-binding JSON 和 narrative audit；
5. 运行唯一一次 A→B→C→D formal preflight；
6. 只有全部 preflight 门通过后运行一次 unchanged exact capture；
7. 独立执行 post-run fingerprint、cleanup、aggregate-only 和 formal-output absence 核验；
8. 提交推送 machine/narrative audit，核对 GitHub 后立即停止。

任一阶段硬失败必须立即停止、记录新 Hard Failure，禁止第二次 preflight、第二次 capture 或自动重试。

## Formal Preflight 冻结顺序

### A. 项目与治理门

- `HEAD == origin/main == GitHub main` 且工作树干净；
- package、approval、implementation、rebinding、governance binding 均为祖先；
- implementation/governance SHA 与 bytes 精确匹配；
- exact capture argv 精确匹配；
- helper 为普通 tracked 文件。

### B. 输出与残留缺失门

在任何 official input metadata/content 操作前确认：

- historical machine audit 不存在；
- 5E-B narrative audit 不存在；
- 五项 formal outputs 全部不存在；
- `stage4b_u1_decisions_diag_*` 临时残留不存在；
- 不存在禁止输入参数。

任一不满足时不得运行 helper、读取 official input 或 capture。

### C. Helper hash 与调用门

Helper 必须精确为：

```text
scripts/stage4b_u1_preflight_path_equivalence.py
bytes: 3543
SHA-256: 1A17C0E750F91CEF2F638A0B0C6FD381110692E6B2D467C1F5243ADF3F35B3FF
```

只能使用 Manifest 冻结的 direct import/call：runtime path 必须是未经 trim/replace/normalize 的 `.NET GetTempPath()` 原始返回值，expected 必须保持 `C:\Users\cc\AppData\Local\Temp`。禁止复制内联 PowerShell path-equivalence 算法。`False`、异常或 Python 非零退出均为 Hard Failure。

### D. Official input 门

仅在 A/B/C 全通过后检查五项 permitted inputs。路径、SHA、cache bytes、4,500 queries、143,820 units、dual-ID digests、namespace、source digest、controller/comparator checkpoints、模型、`max_length=192` 和 `batch_size=64` 必须全部精确匹配。

Stage4A-R2 source-audit 文件与 5C-B machine inventory 不得打开。Official rankings、reference policy、evaluator/Gold、reservation 和 Stage3B 继续禁止。

## Conditional Single Capture

只有唯一 preflight 全部门通过后，才允许 request/Manifest 中的 exact capture command 运行一次。参数、参数语义顺序、token string、`--temp-parent` 原始值、machine audit 历史路径、capture/comparator/controller/runtime hashes 均不得变化。

Token `APPROVE_STAGE4B_U1_D_AMENDMENT_5B_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC` 仅作为冻结实现 gate，本批准只重新授权其在该 exact invocation 中使用一次。

## Post-Run 核验

- temporary decisions 已删除；
- 五项 input post-run SHA 与 cache bytes 不变；
- machine audit 为 exclusive-created 且只含允许的 aggregate metadata；
- 五项 formal outputs 继续不存在；
- 无 diagnostic temporary residue；
- 无 rankings、policy、Gold、reservation 或 Stage3B 访问。

不得重新解析 reference decisions 做独立核验，只允许 machine audit 与字节 fingerprint。

## 明确不授权

- 修改或重新内联 helper；
- 修改 exact capture command、token 或 `--temp-parent`；
- 第二次 preflight/capture 或失败后自动重试；
- official rankings、reference policy、source-audit 文件或 5C-B inventory；
- full controller、verifier、evaluator/Gold、reservation 或 Stage3B；
- formal output promotion；
- 修改 raw-byte equivalence、数据、模型、参数、effective-K、q25、score、ECDF、budget、trigger、ranking、endpoint 或 stop rule；
- 诊断后自动恢复 pre-Gold execution。

## 强制停止状态

成功后只能停止在：

```text
AMENDMENT_5E_B_OFFICIAL_DECISIONS_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW
HARD_FAILURE_4_DIAGNOSIS_COMPLETE_AWAITING_REVIEW
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
