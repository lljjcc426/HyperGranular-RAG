# Stage4B-U1-D Pre-Gold Amendment 5D-A Implementation Audit

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-14
- Approved package commit: `33ce115f78840956fcc7bda0c3f4e172579350e7`
- Approval governance commit: `7f879a628fc313e24e805d9bdc5a81b06c37304a`
- Comparator schema version: `stage4b_u1_decisions_diagnostic_v2`
- Diagnostic checkpoint: `stage4b_u1_decisions_diag_v2`
- Status: `AMENDMENT_5D_A_SYNTHETICALLY_VERIFIED`
- Other project conversations, thread tools, and global memory used: No

## 实现范围

只有获批的三个文件发生实现/测试变化：

```text
scripts/stage4b_u1_compare_decisions.py
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
tests/test_stage4b_u1_decisions_diagnostic.py
```

项目级 `AGENTS.md` 只同步批准与最终 evidence 条件。Manifest 登记的 13 个 frozen implementation/test files 均保持原 SHA。

没有删除任何文件。

## Comparator 精确 Diff

Comparator 的 baseline/current 为：

```text
baseline bytes: 13207
baseline SHA-256: FF4D623DF86FE42EB4ACDFF9D3321FCA768E03B64597C6CC88931359CEDB2DD4

current bytes: 12854
current SHA-256: 42FA3F74679672B0595CC76B519D59C03CB193415DD03F56E37260A961D94014
```

实际 diff 只有：

1. `SCHEMA_VERSION` 从 `stage4b_u1_decisions_diagnostic_v1` 更新为 `stage4b_u1_decisions_diagnostic_v2`；
2. `DIAGNOSTIC_CHECKPOINT` 从 `stage4b_u1_decisions_diag_v1` 更新为 `stage4b_u1_decisions_diag_v2`；
3. 删除 `load_decisions_jsonl()` 中 `file_schema` 初始化、第一行冻结和后续 row schema 不一致时的硬拒绝块。

`compare_decisions_files()` 的逐 query 字段集合、字段顺序、recursive schema、canonical row、discrete value、finite-float exact/absolute/ULP 和 semantic-field 代码未修改。`QUERY_HASH_SALT`、aggregate output keys 和 `byte_equivalence_gate_relaxed=false` 均未修改。

## Synthetic Hardening

原 131 项完整 suite 保留。Comparator class 从 34 项增加到 46 项，净新增 12 项，完整 suite 为 143 项。

新增覆盖证明：

- 左、右及双侧文件内部合法 nullable heterogeneity；
- `null <-> integer` 的 schema/discrete/semantic 分类；
- `null <-> finite float` 的 schema/discrete 分类；
- `null` 不进入 finite-float absolute error/ULP；
- comparator 不修改或 numeric-normalize nullable input rows；
- heterogeneous files 下 field set/order/nested structure 比较仍生效；
- invalid second row 与 nested duplicate key 继续硬失败；
- raw-byte inequality 不能被 canonical equality 替代；
- report 继续不泄漏 raw query IDs/rows。

Runner 绑定 5D-A request、Manifest、批准决定、5C-B review、5C-B official schema audit、最终 `AGENTS.md`、三个允许文件及 13 个 frozen files。5C-B machine inventory 被加入 process-wide forbidden-path set，evidence 记录其访问为 `false`。

## 运行命令与异常记录

### 1. AST 静态解析

三个允许 Python 文件初版修改后通过 AST parse。

### 2. Comparator 定向运行 1

```powershell
$env:PYTHONPATH='..\scripts;.'
python -m unittest -v test_stage4b_u1_decisions_diagnostic.Stage4BU1DecisionsComparatorTests
```

结果：46 项中 45 项通过、1 项失败。失败原因是新增测试期望 regex `Invalid JSON`，而冻结实现实际错误为 `Invalid decisions JSON`。Comparator 行为正确；只修正测试 regex，未扩大实现 diff。

### 3. Comparator 定向运行 2

同一命令再次运行，46/46 通过，零 failure/error/skip。

### 4. 完整 preliminary suite

Runner 输出到唯一 OS 临时路径：

```text
C:\Users\cc\AppData\Local\Temp\stage4b_u1_5d_a_preliminary_24ae4d621ccf4f74aa720e4702375c01.json
```

结果为 143/143、零 failure/error/skip/official access；29,643 bytes，SHA-256 `C6F248BCA663F20820BF1F9DC7718E6EA3DAF4F77532E03B9E819D8D5C175E6F`。该文件不在仓库中，不作为最终 evidence。

### 5. 最终 pre-run 静态门

第一次内联 AST 核查命令因列表表达式缺少一个右方括号而在测试/evidence 前退出。该命令没有写入结果。修正命令后通过：13 个 frozen hashes 匹配、仅 `AGENTS.md` 与三个获批文件有 diff、final evidence 路径不存在、三个 Python 文件 AST parse 通过。

### 6. 两轮最终完整 evidence

在完全相同的 runner-bound bytes 上连续运行两次：

```text
run 1 tests: 143
run 2 tests: 143
failures: 0
errors: 0
skipped: 0
official-path access attempts: 0
bytes: 29643
SHA-256: 08695B4305D9919049DFE86870772B9E9F66751DA6D2FF4D43CEF2A912A62008
byte-identical: true
```

Evidence：

```text
results/stage4b_u1_d_pregold_amendment_5d_a_synthetic_verification.json
```

所有 unittest 命令均继续输出本环境既有的 NumPy 2.4.6/旧 numexpr ABI 警告；通过命令均退出 0，警告未形成 unittest failure/error/skip，也未影响 evidence 同字节结果。

## 文件 Hash

### 允许文件

| Path | Bytes | SHA-256 |
|---|---:|---|
| `scripts/stage4b_u1_compare_decisions.py` | 12,854 | `42FA3F74679672B0595CC76B519D59C03CB193415DD03F56E37260A961D94014` |
| `scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py` | 12,061 | `3F97A26169D1056EF76176EE03D7EC938497B3D6EC06D9DAF737B9CC89F1946E` |
| `tests/test_stage4b_u1_decisions_diagnostic.py` | 49,428 | `0CADDB98209AE3091CF7CEDE99B612AF35A0F02793D5BBFC41F157971E96A579` |

### Frozen files

| Path | SHA-256 |
|---|---|
| `scripts/stage4b_u1_capture_diagnostic_decisions.py` | `7C7B159911384B436FDCC1B20D26F2F545F2DC55EAD1F7B2B134B273110ED40A` |
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
| `tests/test_stage4b_u1_goldfree.py` | `CA61B466C7DDF583D827FD2D99C024D646BA3962C80B9137D480C84DEA374C71` |

## 执行边界

- Official-path access attempts 为 0；
- 5C-B machine inventory 未作为实现输入或 fixture 打开；
- 未运行 official comparator/capture、controller、verifier 或 evaluator；
- 完整 baseline 中既有 synthetic capture fixture unit tests 仅在 OS 临时目录使用 synthetic inputs；没有调用 official capture CLI 或 registered official path；
- 未生成或提升 official decisions/rankings/policy；
- 未读取 Gold、U1-D effects、reservation 或 Stage3B；
- 未修改 capture/controller/retrieval/common/inventory/evaluator/verifier 或科研参数；
- 未对 nullable 值进行 normalization/imputation/coercion/casting；
- Raw-byte equality 仍为唯一控制性等价门；
- Hard Failure 4 diagnosis 仍未完成。

## 下一硬门

本实现与 evidence 提交推送后，只允许组装 implementation-bound 5D-B request/Manifest。5D-B package 本身不授权 official capture；必须等待新的明确批准。

