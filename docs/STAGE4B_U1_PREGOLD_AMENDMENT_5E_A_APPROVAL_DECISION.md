# Stage4B-U1-D Pre-Gold Amendment 5E-A 批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-14
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5E_A_WINDOWS_TEMP_PATH_EQUIVALENCE_IMPLEMENTATION_SYNTHETIC_ONLY`
- Amendment 5E-A package commit: `19f16f559f0b1f3b59ef24a04e368f99ae3635e3`
- Hard Failure 6: `bebfeb5664f26795b8d3472f3729ca1bb9abf889`
- Amendment 5D-B rebinding/governance: `2447ad234c160c6e615d81b33dc4ede7ecaa18da`
- Amendment 5D-B approval governance: `1c46dc1b69f8381598aacb9f3b1e27561c7f9ee2`
- Amendment 5D-B package: `f67061e753b03a5cf46d7a7c92b5a95fc79b0ef8`
- Amendment 5D-A implementation/evidence: `02f46447e4cd69a15d2af14ee1fc62f9eb4f8bb9`
- Amendment 5D-A package: `33ce115f78840956fcc7bda0c3f4e172579350e7`
- Amendment 5D-A approval governance: `7f879a628fc313e24e805d9bdc5a81b06c37304a`
- Amendment 5C-B final diagnostic/audit: `e5f28f664449c02b12a129aaa2a011bad84dab91`
- Hard Failure 5: `deccd203059d05dc27ba80aca1ddb1e2ea8f616f`
- Hard Failure 4: `b21852a174b537c90a848699deb4d26d6f169506`
- v2.3.1 implementation: `34349c70ee24b8240fd169393134d4280968b790`
- Official execution: `NOT_AUTHORIZED`
- Other project conversations, thread tools, and global memory used: No

## 正式审批结论

批准 Stage4B-U1-D Pre-Gold Amendment 5E-A：Windows OS-temp path-equivalence helper 实现与 synthetic 验证。

本批准严格绑定 package commit `19f16f559f0b1f3b59ef24a04e368f99ae3635e3` 及上述历史提交。未绑定该 package commit 的批准无效。

## 允许修改文件

```text
scripts/stage4b_u1_preflight_path_equivalence.py
tests/test_stage4b_u1_preflight_path_equivalence.py
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
```

前两个路径必须新增。现有 runner 只允许绑定 5E-A 治理与获批文件、加入新测试及 active proof、将完整 suite 下限提高到 155、记录 helper/访问边界证据并生成 5E-A deterministic evidence。不得修改其他现有实现或测试文件。

## Helper 冻结契约

Helper 必须仅使用 Python 标准库并 fail closed：

1. normalization 前拒绝相对路径；
2. 两个路径均必须存在且为目录；
3. 拒绝 leaf symlink、junction 和 `FILE_ATTRIBUTE_REPARSE_POINT`；
4. 计算完整规范路径、折叠点段并统一 Windows 分隔符语义；
5. 仅为比较移除末尾目录分隔符；
6. 使用 Windows ordinal case-insensitive 精确相等；
7. 拒绝父目录、子目录、兄弟目录、无关目录和字符串前缀碰撞；
8. 禁止使用 prefix acceptance；
9. 不读取文件内容或 official 输入；
10. 不包含 token、capture 或执行授权逻辑。

比较可以规范化，但 official exact command 与 `--temp-parent` 的原始冻结字符串不得修改、重写或替换。

## Synthetic 硬门

冻结基线为 143 项、29,643 bytes、SHA-256 `264200C2EBEDA1D0B214F824B77C89FC5BBE82D3BE0836FAAB9486EACAACF368`。至少新增 12 项，最终完整 suite 必须不少于 155 项。

必须在完全相同 tracked bytes 上连续运行两次，且两次均满足：

```text
failures = 0
errors = 0
skipped = 0
official-path access attempts = 0
formal preflight invocations = 0
authorization token uses = 0
official capture invocations = 0
complete evidence byte-identical = true
```

Runner 必须绑定 5E-A request、Manifest、本批准决定、Hard Failure 6 audit、Hard Failure 6 Review 1、最终批准版 `AGENTS.md`、三个允许路径及 Manifest 全部 frozen files。

## 完成后允许工件

- 本批准决定；
- 5E-A implementation audit；
- deterministic synthetic evidence；
- 一次 implementation/evidence commit 与 push；
- implementation-bound 5E-B request 与 Manifest；
- 必要的 `AGENTS.md`、`README.md`、`ROADMAP.md`、`REPRODUCIBILITY.md` 状态同步。

5E-B package 推送后必须立即停止等待独立审批。

## 明确不授权

- 对真实 OS-temp boundary 运行 formal preflight；
- 打开、哈希、解析或检查任何 official 输入 metadata/content；
- 传入或嵌入 capture authorization token；
- 运行 official comparator/capture、controller、verifier 或 evaluator；
- 生成 temporary 或 formal official decisions、rankings、policy 或 `VERIFIED_PRE_GOLD`；
- 读取 source audit、5C-B inventory、Gold、U1-D 指标、reservation 或 Stage3B；
- 修改 capture、comparator、controller、retrieval、common、数据、模型、参数或 raw-byte equivalence；
- 创建、重建、覆盖、迁移或删除 cache、official artifact、历史 evidence 或 failure record；
- 重试 5D-B preflight 或 capture；
- 自动运行或批准 5E-B。

## 完成后状态

```text
AMENDMENT_5E_A_SYNTHETICALLY_VERIFIED
HARD_FAILURE_6_DIRECT_CAUSE_CONFIRMED
HARD_FAILURE_4_DIAGNOSIS_INCOMPLETE

FORMAL_PREFLIGHT_RETRY_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
