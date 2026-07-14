# Stage4B-U1-D Pre-Gold Amendment 5F-A Implementation Audit

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-14
- Approved package commit: `2b82ba3f0ac9756091d74567f4aed8df5cdf626d`
- Approval governance commit: `273341960858930246ae0c1441440aede0403a65`
- Status: `AMENDMENT_5F_A_SYNTHETICALLY_VERIFIED`
- Hard Failure 7: `DIRECT_CAUSE_CONFIRMED`
- Hard Failure 4 diagnosis: `INCOMPLETE`
- Official execution: `NOT_AUTHORIZED_AND_NOT_EXECUTED`
- 5F-B package assembly: `NOT_AUTHORIZED_AND_NOT_PERFORMED`
- Other project conversations, thread tools, and global memory used: No

## 实现范围

获批实现/测试变化严格限于：

```text
scripts/stage4b_u1_preflight_argument_policy.py
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
tests/test_stage4b_u1_preflight_argument_policy.py
```

项目级 `AGENTS.md` 只同步批准、实现基线、preliminary 结果与最终 evidence 条件。批准决定、implementation audit、evidence 及导航文档属于获批治理工件。没有修改其他实现或既有测试，没有删除任何仓库文件。

## 精确 Diff

相对批准治理 commit `273341960858930246ae0c1441440aede0403a65`，三个获批路径的精确行级范围为：

| Path | Additions | Deletions | Result |
|---|---:|---:|---|
| `scripts/stage4b_u1_preflight_argument_policy.py` | 209 | 0 | new file |
| `scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py` | 100 | 22 | modified |
| `tests/test_stage4b_u1_preflight_argument_policy.py` | 382 | 0 | new file |

包含本审计的 implementation/evidence commit 是上述精确 diff 的 Git authority；文件 bytes 与 SHA-256 见下文。

## Helper 实现

`validate_capture_argv(actual_argv, approved_argv)` 只接收调用方提供的两个字符串序列，不读取 Manifest 或任何路径。控制逻辑为：

1. 将两组输入 fail-closed 转换为非空 text tuple；
2. exact argv equality 是首个控制门，不一致时只允许进入拒绝分类，不存在接受路径；
3. 固定 `python`、capture script、32 元素与 15 个有序 flag；
4. 拒绝 unknown、duplicate、missing、reordered、extra positional/value 与七个显式 prohibited roles；
5. 七个路径角色要求 Windows 绝对路径语法，并逐角色精确绑定 approved value；
6. model 为非空精确文本，batch/max-length 为 canonical positive decimal，四个 SHA 为 64 位大写十六进制，token 只做精确绑定；
7. `pregold` audit-output 和普通 value 中的 `gold` 不触发角色禁令；
8. 返回值仅含 deterministic、value-free 验证元数据。

Helper 只导入 `ntpath` 与 `collections.abc`。AST 与 runtime patch 主动证明其不调用 filesystem metadata/content、hash、subprocess、capture、token-use 或 path-equivalence helper，也不存在裸 `gold` value-substring denylist。

## Synthetic Hardening

新增 test module 共 44 项，无 skip，覆盖：

- exact approved argv、`pregold` audit-output 和普通 `gold` value substring 的合法路径；
- executable、script、unknown、duplicate、missing、reordered、extra arguments；
- units、queries、channel audit、embedding cache、reference decisions、audit output、temp parent 七个路径角色逐项漂移；
- model 与 token 漂移；
- canonical positive decimal 与四个 SHA 类型错误；
- `--rankings`、`--policy`、`--gold-map`、`--source-audit`、`--evaluator`、`--reservation`、`--stage3b` 逐项拒绝；
- 非 sequence、非 text、relative Windows path；
- standard-library、no-filesystem/hash/execution、no-capture/path-helper import、no-raw-gold-denylist AST proofs；
- runtime no-filesystem/hash/subprocess/capture/path-helper/token-use proofs；
- value-free metadata 输出。

## Runner 变化

Runner baseline/current：

```text
baseline bytes: 14083
baseline SHA-256: C4D11EFA0E89D03159A282A3295469609973A907CAFAA16C9DC5706CFF8A4AAC

current bytes: 18120
current SHA-256: 31F2233CA9ACF7F156C24B6CD2F0268F7816CC3DE745E783711C2E58E7459D7F
```

变化仅用于：

- 绑定 5F-A request、Manifest、approval decision、Hard Failure 7 audit/Review 与最终 `AGENTS.md`；
- 绑定 helper、runner、new tests 和 Manifest 17 个 frozen files；
- 加入 44 项 typed argument-policy active proofs；
- 将 baseline/minimum 从 143/155 更新为 161/177；
- 记录实际新增 argument-policy test 数量；
- 输出 26 个 tracked files 的确定性 digest；
- 记录 official access、path-helper official invocation、formal preflight、token、capture 和 no-raw-gold-denylist 证据；
- 将 evidence 路径与状态更新为 5F-A。

没有修改测试发现 pattern、既有测试、path helper、capture、comparator、common、controller、retrieval 或任何科研参数。

## 命令与失败记录

### 1. 批准治理

批准决定与 `AGENTS.md` 形成独立 commit：

```text
273341960858930246ae0c1441440aede0403a65
```

该提交已在实现开始前推送至 `origin/main`。

### 2. 首次定向测试命令失败

```powershell
& 'D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe' `
  -m unittest tests.test_stage4b_u1_preflight_argument_policy -v
```

仓库的 `tests` 目录不是 Python package，命令在 test discovery 前以 `ModuleNotFoundError: No module named 'tests.test_stage4b_u1_preflight_argument_policy'` 退出。没有测试、official access 或文件操作发生。

改用获支持的 discovery 入口：

```powershell
& 'D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe' `
  -m unittest discover -s tests -p 'test_stage4b_u1_preflight_argument_policy.py' -v
```

结果为 44/44，零 failure/error/skip。

### 3. Preliminary 完整 suite

Runner 输出至唯一 OS 临时文件。结果为 205/205、44 项 argument-policy tests、零 failure/error/skip/official access；51,732 bytes，SHA-256 `20C0D248085FD8582F776842D8DD9B6DA2DB7BDA83D4204E587736ECA8F91C83`。该 preliminary 运行早于 tracked-digest evidence 字段的最终 runner 修改，不作为最终 evidence；检查后已删除临时文件。

### 4. 最终 pre-run 静态门

```text
frozen hashes: 17/17
worktree implementation/test scope: approved three paths only
py_compile: helper, runner and test all pass
final evidence path before run: absent
```

### 5. 首次最终启动命令解析失败

第一版双轮 PowerShell wrapper 使用 `[System.Linq.Enumerable]::SequenceEqual[byte](...)`。当前 PowerShell 无法解析该泛型调用语法，整段命令在 parser 阶段退出；两轮 runner 均未启动，未创建 evidence 或临时文件。

修正版使用两个 byte arrays 的 Base64 表示做精确相等比较；这不改变 runner、tracked bytes 或 evidence 内容。

### 6. 两轮最终完整 evidence

在完全相同的 26 个 runner-bound tracked files 上连续运行两次：

```text
run 1 tests: 205
run 2 tests: 205
argument-policy tests: 44
failures: 0
errors: 0
skipped: 0
official metadata/content access attempts: 0
path-helper official invocations: 0
formal preflight invocations: 0
authorization token uses: 0
official capture invocations: 0
tracked-byte digest: B58E85239F001B532B5CF378998B804B1202C5D6FF148311EF939DC4B3B4EA34
bytes: 51922
run 1 SHA-256: A5B97077AD9A0C62EBFCAE9D70FC8B5BFAD19CCB32FF3A53E1FCF4BDB216D189
run 2 SHA-256: A5B97077AD9A0C62EBFCAE9D70FC8B5BFAD19CCB32FF3A53E1FCF4BDB216D189
direct byte comparison: true
```

第一轮最终 OS 临时 evidence 在直接比较后已删除。正式 evidence：

```text
results/stage4b_u1_d_pregold_amendment_5f_a_synthetic_verification.json
```

## 文件 Hash

### 允许文件与 evidence

| Path | Bytes | SHA-256 |
|---|---:|---|
| `scripts/stage4b_u1_preflight_argument_policy.py` | 7,082 | `CCDC70D2E66E9D69CD64899676EA5150FEE0381E74F4C9DEED2A0FFB5EE436F4` |
| `scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py` | 18,120 | `31F2233CA9ACF7F156C24B6CD2F0268F7816CC3DE745E783711C2E58E7459D7F` |
| `tests/test_stage4b_u1_preflight_argument_policy.py` | 15,759 | `9B338292E1A8CCAED0EFD114999999B1C884B7CC8861EBCB9BA8029D4D1498E2` |
| `results/stage4b_u1_d_pregold_amendment_5f_a_synthetic_verification.json` | 51,922 | `A5B97077AD9A0C62EBFCAE9D70FC8B5BFAD19CCB32FF3A53E1FCF4BDB216D189` |

### 17 个 Frozen Files

| Path | Bytes | SHA-256 |
|---|---:|---|
| `scripts/stage4b_u1_preflight_path_equivalence.py` | 3,543 | `1A17C0E750F91CEF2F638A0B0C6FD381110692E6B2D467C1F5243ADF3F35B3FF` |
| `scripts/stage4b_u1_capture_diagnostic_decisions.py` | 20,221 | `7C7B159911384B436FDCC1B20D26F2F545F2DC55EAD1F7B2B134B273110ED40A` |
| `scripts/stage4b_u1_compare_decisions.py` | 12,854 | `42FA3F74679672B0595CC76B519D59C03CB193415DD03F56E37260A961D94014` |
| `scripts/stage4b_u1_common.py` | 9,649 | `CDF7EAD6007DABE389ED0BD18983496F75290C32243FE6DF84716810CDE92CE4` |
| `scripts/stage4b_u1_evaluate.py` | 24,464 | `343BC9D2478042FF582DAA5DE716498124166C72A520A35DAE53F56C976F2E31` |
| `scripts/stage4b_u1_goldfree_controller.py` | 33,661 | `C18AD3B672649BA846C5E191D0DBBAC7644A926D4B8CCD39176127175BBA7C1F` |
| `scripts/stage4b_u1_goldfree_retrieval.py` | 23,904 | `3B50FAFD057E2565167ED09288D61829B3FBD044991F139F734F819955038A3B` |
| `scripts/stage4b_u1_inventory_decision_schemas.py` | 18,287 | `CC48C73306AB48D14E021AE69740A59F2F0218C241E47EE283ECD21E1C81F176` |
| `scripts/stage4b_u1_plan_power.py` | 5,811 | `B6BC76E13D597F06AA6494F9E41D5FFD622F9534E55406DC65AB117971900843` |
| `scripts/stage4b_u1_prepare_channels.py` | 10,021 | `BF629382DCD93F9FD64F0DEB0D441DC775725040E51CE4155884023CE29FD76C` |
| `scripts/stage4b_u1_run_schema_inventory_synthetic_verification.py` | 10,304 | `01B84D359B49AC00BD7B52100D3157A5D0BA1DA78B7D5FF3D0ABCBBE7708E7FA` |
| `scripts/stage4b_u1_run_synthetic_verification.py` | 8,553 | `3C7DE76E0CC54102E47017A2114C0E3206D03BE8E81F916E806E4E6AECE72026` |
| `scripts/stage4b_u1_verify.py` | 29,918 | `DC134B51A07C14A553746C303EA31D83990BA0EFAD30EFC3A1722F1A141E66EC` |
| `tests/test_stage4b_u1_preflight_path_equivalence.py` | 6,200 | `1A601A06F44C959A1885CE17A1F224DE491589B161B0A6899C1EBB7028DBA7F2` |
| `tests/test_stage4b_u1_decisions_diagnostic.py` | 49,428 | `0CADDB98209AE3091CF7CEDE99B612AF35A0F02793D5BBFC41F157971E96A579` |
| `tests/test_stage4b_u1_decision_schema_inventory.py` | 13,812 | `89881A70EBE12F49E63B08EE8846F78985B98710412C63EDA67CF8A695332E30` |
| `tests/test_stage4b_u1_goldfree.py` | 56,568 | `CA61B466C7DDF583D827FD2D99C024D646BA3962C80B9137D480C84DEA374C71` |

17/17 均与 5F-A Manifest 精确匹配。

## 冻结与访问边界

- 5E-B Manifest 仍为 17,286 bytes、SHA-256 `EC83E0EABF0286420E03C2A55C9E5559041C392FB0FED9B48F9A614E9720E854`；32-element exact argv、15 flags 与 token string 未变化；
- comparator SHA 未变化，raw-byte equality 继续是冻结控制门；
- 没有调用真实 OS-temp path helper；
- 没有运行 formal preflight、authorization token、official capture/comparator、controller、verifier 或 evaluator；
- 没有打开、哈希、解析或检查任何 official input metadata/content；
- 没有读取 Gold、U1-D 指标、reservation 或 Stage3B；
- 没有创建、重建、覆盖、迁移或删除 cache、official artifact、历史 evidence 或 failure record；
- Hard Failure 4 diagnosis 仍未完成。

## 下一硬门

本 implementation/evidence commit 推送后必须立即停止等待独立审核。本批准不允许组装 5F-B。只有独立审核明确接受 5F-A implementation/evidence 后，才可另行组装 5F-B package；preflight、helper official-boundary check、token、capture、controller、verifier 与 Gold 仍未批准。
