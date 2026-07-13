# Stage4B-U1-D Pre-Gold Amendment 5A 批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-13
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5A_IMPLEMENTATION_SYNTHETIC_ONLY`
- Amendment 5A package commit: `81d8c34f1cf2539a4c0b81c6148047bc666e2f82`
- Hard Failure 4: `b21852a174b537c90a848699deb4d26d6f169506`
- v2.3.1 implementation: `34349c70ee24b8240fd169393134d4280968b790`
- Original resumption package: `e76c921454697d1784b0d76a9d9677113051f0f6`
- Approval governance: `53850f58e57f51b3c6067ed3108edff6b99a2dfc`
- Synthetic rebinding: `a963befd812658972b156d2a7a26a488ac3c4482`
- Failed controller execution HEAD: `8e0bab13ad20c06795dffd5ca71f167a814cdfb0`
- Official diagnosis: `NOT_AUTHORIZED`
- Controller rerun: `NOT_AUTHORIZED`
- Verifier: `NOT_AUTHORIZED`

## 正式审批结论

批准 Stage4B-U1-D Pre-Gold Amendment 5A：decisions 等价差异诊断工具实现与 synthetic 验证；不授权 official 诊断、controller 重跑或 verifier。

## 授权范围

1. 新增 decisions-only JSONL comparator；
2. 新增仅用于 synthetic fixture 的 OS-temporary decisions capture；
3. 实现 raw bytes、row/query-ID、canonical JSON、schema、discrete values、finite float/absolute error/binary64 ULP 和 decision semantics 七层比较；
4. 保留原 50 项 Stage4B-U1 synthetic tests，新增不少于 24 项诊断测试，完整 suite 不少于 74 项；
5. 完整 suite 连续运行两次，全部通过、零 failure/error/skip 且完整 evidence 字节一致；
6. 生成并推送 5A implementation audit、deterministic evidence 和完整实现文件 SHA-256；
7. 创建并推送 implementation-bound Amendment 5B 审批请求与 Manifest；
8. 推送 5B 包后立即停止。

## 附加实现硬门

- `scripts/stage4b_u1_goldfree_controller.py` 原则上不得修改；仅当共享 decisions 纯函数无法复用时才允许机械提取。
- 若修改 controller，checkpoint 必须保持 `stage4b_u1_v2_3_1`，CLI、formal 路径、cache 门、pending-output、score、ECDF、预算、trigger、ranking、policy 和 endpoint 行为均不得改变；必须新增提取前后 canonical bytes 与字段值一致的 synthetic regression，并在 audit 单列 diff。
- Comparator 必须严格区分 `bool`/`int`、`int`/`float`、`+0.0`/`-0.0`、跨符号 ULP，并显式拒绝 JSON `NaN`、`Infinity`、`-Infinity`。
- ULP 映射公式、字节序和符号排序规则必须在实现审计冻结，不得依赖平台默认行为。
- 重复/缺失 query ID、非法 JSON、非有限浮点、未知类型和不可比较 schema 必须非零失败。
- 测试必须以路径 allowlist、mock/patch 或文件访问拦截主动证明 official units/queries/cache/v2.2 decisions/rankings 未打开、policy builder 未调用，并证明 temporary decisions 在成功和异常退出后均删除。

## 明确不授权

- 读取 official units、queries、source audit、fresh/legacy cache；
- 读取、保存或比较 official v2.2/v2.3.1 decisions；
- 读取或比较 official rankings；
- 运行 official comparator、diagnostic capture、controller、verifier 或 evaluator；
- 生成 official decisions、rankings 或 policy；
- 修改或放宽 byte-equivalence 门，或以 canonical/semantic equality 替代 byte equality；
- 修改 retrieval/controller/evaluator 算法、模型、参数或 endpoint；
- Gold、U1-D 效果指标、reservation、Stage3B 或自动恢复 Hard Failure 4。

5A 完成后的状态只能是：

```text
AMENDMENT_5A_SYNTHETICALLY_VERIFIED
OFFICIAL_DIAGNOSIS_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
```
