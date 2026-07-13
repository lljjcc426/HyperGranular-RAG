# Stage4B-U1-D Pre-Gold Amendment 5A 审批请求

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-13
- Request ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_5A_DECISIONS_DIAGNOSTIC_TOOL`
- Draft: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_DECISIONS_DIAGNOSTIC_DRAFT.md`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_MANIFEST.json`
- Current state: `PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_4`
- Current official diagnosis approval: `NOT_APPROVED`
- Current controller rerun approval: `NOT_APPROVED`
- Current verifier approval: `NOT_APPROVED`
- Other project conversations, thread tools, and global memory used: No

## 绑定提交

```text
Hard Failure 4:
b21852a174b537c90a848699deb4d26d6f169506

v2.3.1 implementation:
34349c70ee24b8240fd169393134d4280968b790

original resumption package:
e76c921454697d1784b0d76a9d9677113051f0f6

approval governance:
53850f58e57f51b3c6067ed3108edff6b99a2dfc

synthetic rebinding:
a963befd812658972b156d2a7a26a488ac3c4482

failed controller execution HEAD:
8e0bab13ad20c06795dffd5ca71f167a814cdfb0
```

审批时还必须绑定本 5A package 所在的新提交。未绑定 package commit 的批准无效。

## 请求批准

请求批准：

```text
批准 Stage4B-U1-D Pre-Gold Amendment 5A：
decisions 等价差异诊断工具实现与 synthetic 验证，
不授权 official 诊断、controller 重跑或 verifier
```

本请求仅授权实现和 synthetic hardening：

1. 新增 decisions-only comparator；
2. 新增只在 OS temporary directory 捕获 decisions 的诊断入口；
3. 必要时仅机械提取现有 controller 的共享 decisions 纯函数，不改变任何检索或决策语义；
4. 冻结 raw bytes、row/query-ID、canonical JSON、schema、discrete、float/ULP 和 decision semantics 七层比较；
5. 保留现有 50 项 synthetic tests，并新增至少 24 项 5A hardening tests；
6. 完整 synthetic suite 连续运行两次，全部通过、零 failure/error/skip 且 evidence 字节一致；
7. 形成 implementation audit、完整文件 SHA-256 和 deterministic evidence；
8. 提交推送实现/evidence 后，创建 implementation-bound Amendment 5B official decisions-only diagnostic 审批请求与 Manifest；
9. 推送 5B 请求后立即停止。

## 诊断工具的强制隔离

- Comparator 输入类型只能是 decisions JSONL；任何 ranking/policy/evaluator 参数必须在参数解析阶段拒绝。
- Diagnostic capture 不得构造、读取、保存或比较 rankings，不得调用 policy builder。
- 5A synthetic fixture 必须全部位于测试临时目录；不得使用 manifest 登记 official 路径。
- Synthetic runner 必须证明 official units/queries/cache/decisions/rankings 路径均未访问。
- Official capture 默认禁用；没有 future 5B approval binding 时必须 fail-closed。
- Official audit schema 只允许聚合计数、hash、float error/ULP 上界和 salted query-ID hash，不得输出 raw rows、question/text、Gold 或 ranking。

## 明确不请求授权

- 不读取 official units、queries、source audit 或 cache；
- 不读取 v2.2 decisions 内容；
- 不读取或比较 official rankings；
- 不生成 official decisions、rankings 或 policy；
- 不运行 official diagnostic、controller、verifier 或 evaluator；
- 不修改或放宽 byte-equivalence 门；
- 不修改 retrieval/controller/evaluator 算法、模型或参数；
- 不读取 Gold/U1-D 效果指标；
- 不访问 reservation 或 Stage3B；
- 不自动重跑 Hard Failure 4。

## 完成门

5A 完成不代表 Hard Failure 4 已解释，也不恢复 official execution。完成后状态只能是：

```text
AMENDMENT_5A_SYNTHETICALLY_VERIFIED
OFFICIAL_DIAGNOSIS_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
```

只有新的 5B package 获得独立明确批准后，才允许单次 official decisions-only 诊断。
