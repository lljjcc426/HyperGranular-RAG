# Stage4B-U1-D Pre-Gold Amendment 5E-A Implementation Audit

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-14
- Approved package commit: `19f16f559f0b1f3b59ef24a04e368f99ae3635e3`
- Approval governance commit: `461939434206764555b917c5971956e6951ff4dd`
- Status: `AMENDMENT_5E_A_SYNTHETICALLY_VERIFIED`
- Hard Failure 6: `DIRECT_CAUSE_CONFIRMED`
- Hard Failure 4 diagnosis: `INCOMPLETE`
- Official execution: `NOT_AUTHORIZED_AND_NOT_EXECUTED`
- Other project conversations, thread tools, and global memory used: No

## 实现范围

获批实现/测试变化严格限于：

```text
scripts/stage4b_u1_preflight_path_equivalence.py
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
tests/test_stage4b_u1_preflight_path_equivalence.py
```

项目级 `AGENTS.md` 只同步批准、实现基线和最终 evidence 条件。批准决定、implementation audit、evidence 及导航文档属于获批治理工件。没有修改其他实现或既有测试，没有删除任何仓库文件。

## Helper 精确实现

`scripts/stage4b_u1_preflight_path_equivalence.py` 是新增的标准库模块：

1. `windows_directories_equivalent(actual, expected)` 在 normalization 前用 Windows path semantics 拒绝相对路径；
2. 对两端分别执行 `os.lstat()`，要求调用时存在、为目录且 leaf 不是 symlink/junction/reparse point；
3. 使用 `ntpath.normpath()` 与 `ntpath.abspath()` 计算完整 Windows 规范路径并折叠点段、统一分隔符；
4. 仅对比较值移除非根路径末尾分隔符；
5. 通过 Windows `CompareStringOrdinal(..., TRUE)` 执行 ordinal-ignore-case 精确相等；
6. 不使用 `startswith()` 或其他 prefix acceptance；
7. 不包含 command、`--temp-parent`、token、capture 或执行授权逻辑，也不读取文件内容。

因此 helper 只改变比较实现，不重写或规范化未来 exact capture command 的原始参数。

## Synthetic Hardening

新增测试模块包含 18 项，无 skip：

- 接受相同绝对目录、末尾分隔符、大小写变体、正反斜杠变体和末尾点段；
- 拒绝父目录、子目录、无关目录和 `CaseProbe2` 前缀碰撞；
- 对相对路径、缺失路径、文件和 reparse-point leaf 硬失败；
- AST 主动证明不存在 `startswith()` 接受调用；
- AST 主动证明 helper 仅导入 Python 标准库；
- 源码主动证明不含 command/token/capture 逻辑；
- patch 主动证明 leaf probe 只接收测试创建的 synthetic 路径；
- 非文本路径 fail closed。

Reparse-point 测试使用 patch 强制 leaf attribute 分支，不依赖系统创建 junction 的权限，因此没有 skip。

## Runner 精确变化

Runner baseline/current：

```text
baseline bytes: 12061
baseline SHA-256: 3F97A26169D1056EF76176EE03D7EC938497B3D6EC06D9DAF737B9CC89F1946E

current bytes: 14083
current SHA-256: C4D11EFA0E89D03159A282A3295469609973A907CAFAA16C9DC5706CFF8A4AAC
```

变化仅用于：

- 绑定 5E-A request、Manifest、approval decision、Hard Failure 6 audit/Review、最终 `AGENTS.md`；
- 绑定 helper、runner、new tests 和 Manifest 15 个 frozen files；
- 加入 18 项 helper active proofs；
- 将 baseline/minimum 从 131/143 更新为 143/155；
- 将 evidence 路径和状态更新为 5E-A；
- 使用不查询文件系统 metadata 的 lexical Windows key 构造 official forbidden set；
- 记录 official metadata/content、formal preflight、token、official capture、exact-command 与 raw-byte gate 证据。

没有修改测试发现 pattern、既有测试、capture、comparator、controller、retrieval、common 或任何科研参数。

## 命令与异常记录

### 1. 只读文件枚举失败

```powershell
rg --files docs scripts tests results | rg '5D_A|5D_B|5E_A|HARD_FAILURE_6|decisions_diagnostic|path_equivalence'
```

系统返回 `Access is denied`。未产生文件变更；后续改用 PowerShell 原生枚举。

### 2. 批准治理自检失败

第一次治理 scope 检查使用 `git diff --name-only`，该命令不包含未跟踪的新 approval decision，因而误报 `Unexpected governance diff scope`。失败发生在 `git add`/commit 前；改用 `git status --porcelain` 后通过。批准治理 commit 为 `461939434206764555b917c5971956e6951ff4dd`，已推送并与远端一致。

### 3. 初版合并补丁失败

第一次将 helper、test 和 runner 合并提交给 `apply_patch` 时，runner 默认输出路径的上下文未精确匹配，补丁在写入前整体拒绝。随后拆分补丁；没有遗留部分文件。

### 4. 静态门与定向测试

三个获批 Python 文件均通过 AST parse；diff scope 为三个获批实现路径，15 个 frozen SHA 全匹配。

```powershell
$env:PYTHONPATH='scripts;tests'
python -m unittest -v test_stage4b_u1_preflight_path_equivalence
```

结果：18/18，零 failure/error/skip。

### 5. Preliminary 完整 suite

Runner 输出至唯一 OS 临时文件。结果为 161/161、零 failure/error/skip/official access、零 formal-preflight/token/capture；36,518 bytes，SHA-256 `BE783FF6E9C35753BABCD9E993AB99BA3BEF0B5EEF3E3043EC9CE059DBEB620D`。核验后已删除该 preliminary 临时文件。

### 6. 最终 pre-run 静态门兼容失败

第一次摘要命令因当前旧 .NET 不提供 `SHA256.HashData` 停止；第二次因不提供 `Convert.ToHexString` 停止。两次均发生在最终 suite 启动前，没有写入 evidence。改用 `SHA256.Create().ComputeHash()` 与 `BitConverter` 后通过。

最终静态门确认：

```text
runner-bound files: 24
bound bytes digest: 68E0F934E171F763793942F7B1CEC78638A3F31FF185AAE3A5321E35C1AD541C
frozen hashes: 15/15
final evidence path before run: absent
```

### 7. 两轮最终完整 evidence

在完全相同的 24 个 runner-bound tracked bytes 上连续运行两次：

```text
run 1 tests: 161
run 2 tests: 161
failures: 0
errors: 0
skipped: 0
official metadata/content access attempts: 0
formal preflight invocations: 0
authorization token uses: 0
official capture invocations: 0
bytes: 36518
run 1 SHA-256: 84C58CBA9801A6EB8DFAF4ED6688BB5FCBD5777729FD833083E16CB630FFED83
run 2 SHA-256: 84C58CBA9801A6EB8DFAF4ED6688BB5FCBD5777729FD833083E16CB630FFED83
direct byte comparison: true
```

第一轮最终临时 evidence 在逐字节比较后已删除。正式 evidence：

```text
results/stage4b_u1_d_pregold_amendment_5e_a_synthetic_verification.json
```

Preliminary 与两轮最终完整 suite 均继续输出环境既有的 NumPy 2.4.6/旧 `numexpr` ABI 警告；三个 runner 命令退出码均为 0，警告没有形成 unittest failure/error/skip，也未影响最终 evidence 字节一致性。

## 文件 Hash

### 允许文件

| Path | Bytes | SHA-256 |
|---|---:|---|
| `scripts/stage4b_u1_preflight_path_equivalence.py` | 3,543 | `1A17C0E750F91CEF2F638A0B0C6FD381110692E6B2D467C1F5243ADF3F35B3FF` |
| `scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py` | 14,083 | `C4D11EFA0E89D03159A282A3295469609973A907CAFAA16C9DC5706CFF8A4AAC` |
| `tests/test_stage4b_u1_preflight_path_equivalence.py` | 6,200 | `1A601A06F44C959A1885CE17A1F224DE491589B161B0A6899C1EBB7028DBA7F2` |

### Frozen files

| Path | SHA-256 |
|---|---|
| `scripts/stage4b_u1_capture_diagnostic_decisions.py` | `7C7B159911384B436FDCC1B20D26F2F545F2DC55EAD1F7B2B134B273110ED40A` |
| `scripts/stage4b_u1_compare_decisions.py` | `42FA3F74679672B0595CC76B519D59C03CB193415DD03F56E37260A961D94014` |
| `scripts/stage4b_u1_common.py` | `CDF7EAD6007DABE389ED0BD18983496F75290C32243FE6DF84716810CDE92CE4` |
| `scripts/stage4b_u1_evaluate.py` | `343BC9D2478042FF582DAA5DE716498124166C72A520A35DAE53F56C976F2E31` |
| `scripts/stage4b_u1_goldfree_controller.py` | `C18AD3B672649BA846C5E191D0DBBAC7644A926D4B8CCD39176127175BBA7C1F` |
| `scripts/stage4b_u1_goldfree_retrieval.py` | `3B50FAFD057E2565167ED09288D61829B3FBD044991F139F734F819955038A3B` |
| `scripts/stage4b_u1_inventory_decision_schemas.py` | `CC48C73306AB48D14E021AE69740A59F2F0218C241E47EE283ECD21E1C81F176` |
| `scripts/stage4b_u1_plan_power.py` | `B6BC76E13D597F06AA6494F9E41D5FFD622F9534E55406DC65AB117971900843` |
| `scripts/stage4b_u1_prepare_channels.py` | `BF629382DCD93F9FD64F0DEB0D441DC775725040E51CE4155884023CE29FD76C` |
| `scripts/stage4b_u1_run_schema_inventory_synthetic_verification.py` | `01B84D359B49AC00BD7B52100D3157A5D0BA1DA78B7D5FF3D0ABCBBE7708E7FA` |
| `scripts/stage4b_u1_run_synthetic_verification.py` | `3C7DE76E0CC54102E47017A2114C0E3206D03BE8E81F916E806E4E6AECE72026` |
| `scripts/stage4b_u1_verify.py` | `DC134B51A07C14A553746C303EA31D83990BA0EFAD30EFC3A1722F1A141E66EC` |
| `tests/test_stage4b_u1_decision_schema_inventory.py` | `89881A70EBE12F49E63B08EE8846F78985B98710412C63EDA67CF8A695332E30` |
| `tests/test_stage4b_u1_decisions_diagnostic.py` | `0CADDB98209AE3091CF7CEDE99B612AF35A0F02793D5BBFC41F157971E96A579` |
| `tests/test_stage4b_u1_goldfree.py` | `CA61B466C7DDF583D827FD2D99C024D646BA3962C80B9137D480C84DEA374C71` |

15/15 均与 5E-A Manifest 精确匹配。

## 执行边界

- 没有运行真实 OS-temp formal preflight；
- 没有传入、嵌入或使用 capture authorization token；
- 没有运行 official comparator/capture、controller、verifier 或 evaluator；
- 没有打开、哈希、解析或检查任何 official 输入 metadata/content；
- 没有生成 official temporary/formal decisions、rankings、policy 或 `VERIFIED_PRE_GOLD`；
- 没有读取 source audit、5C-B inventory、Gold、U1-D 指标、reservation 或 Stage3B；
- exact capture command 和原始 `--temp-parent` 未修改；
- raw-byte equality 继续是冻结控制门；
- Hard Failure 4 diagnosis 仍未完成。

## 下一硬门

本实现与 evidence 提交推送后，只允许组装 implementation-bound 5E-B request/Manifest。5E-B 必须要求新 formal preflight 直接 import/call 本次已测试且哈希绑定的 helper；5E-B package 本身不授权 preflight、token、capture、controller、verifier 或 Gold，必须等待新的明确批准。
