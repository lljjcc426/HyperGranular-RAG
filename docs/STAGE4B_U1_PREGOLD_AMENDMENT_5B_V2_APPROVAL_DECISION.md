# Stage4B-U1-D Pre-Gold Amendment 5B v2 批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-14
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5B_V2_SINGLE_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC`
- 5B v2 package: `f43e22ef079701139d4437849be8ad57654f80d7`
- Amendment 5A.1 package: `3137ace0328dd24908f95737ea1dcbe0c8fe045e`
- Amendment 5A.1 approval governance: `d34835159fd600c8b629114946afee9e943d143c`
- Amendment 5A.1 implementation/evidence: `e566eb861ec6028ca89a40c9aca7d06737f1eb8e`
- Returned Amendment 5B package: `ceb755252540cf223aa18ac721443154c29cd07a`
- Hard Failure 4: `b21852a174b537c90a848699deb4d26d6f169506`
- Failed controller execution HEAD: `8e0bab13ad20c06795dffd5ca71f167a814cdfb0`
- v2.3.1 implementation: `34349c70ee24b8240fd169393134d4280968b790`
- Controller rerun: `NOT_AUTHORIZED`
- Verifier: `NOT_AUTHORIZED`
- Gold: `NOT_AUTHORIZED`
- Other project conversations, thread tools, and global memory used: No

## 正式审批结论

批准 Stage4B-U1-D Pre-Gold Amendment 5B v2：单次 official decisions-only 诊断。

## 唯一授权顺序

1. 创建本批准决定并同步最终批准治理字节，提交推送。
2. 在最终批准治理字节上完整运行 107 项 synthetic suite 两次；均须 107/107、零 failure/error/skip/official access，且完整 evidence 字节一致。
3. 生成 governance-binding JSON，绑定 v2 request、Manifest、本批准决定、最终 `AGENTS.md`、`e566eb...` 实现/evidence 和 post-approval rebinding evidence。
4. 将 rebinding evidence、governance binding 和 audit 提交推送后，运行唯一一次只读 preflight。
5. Preflight 全部通过后，运行唯一一次 v2 request 中登记的 exact-command official decisions-only capture。
6. 核验 temporary cleanup、三项 channel SHA 前后不变、cache SHA/bytes 前后不变、machine audit 聚合边界和正式输出持续不存在。
7. 提交推送 machine/narrative audit，核对 GitHub 后立即停止。

任一 rebinding、binding、preflight、capture、cleanup、commit 或 push 硬门失败均须停止，不得自动重试。

## 冻结输入

```text
unlabeled units SHA-256
114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA

unlabeled queries SHA-256
6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B

controller channel audit SHA-256
D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA

embedding cache SHA-256
69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D

embedding cache bytes
210714667

v2.2 reference decisions SHA-256
6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7
```

Official capture 必须显式传入三个新增 expected-SHA 参数，不得仅依赖 channel audit 内部记录。

## 输出边界

允许 machine/narrative audit 报告 raw file bytes/size/SHA、canonical digest、query-ID 集合与顺序的一致性及差异计数、schema/字段顺序/类型、离散值、float absolute/ULP、三项决策语义差异计数、最多一个 salted query-ID hash，以及 channel/cache/cleanup 布尔核验。

禁止输出原始 query ID、原始 decision 行、question/text、ranking、policy、Gold 或效果指标。Raw byte equality 继续是冻结控制门；canonical/semantic equality 只能解释差异。

## 明确不授权

- 完整 controller 或正式 decisions/rankings/policy 提升；
- official ranking hash/读取/比较或 v2.2 reference policy；
- Stage4A-R2 source-audit 文件；
- verifier、`VERIFIED_PRE_GOLD`、evaluator、Gold 或 U1-D 效果指标；
- reservation 或 Stage3B；
- 代码、数据、模型、参数、effective-K、q25、score、ECDF、预算、trigger、ranking、endpoint、等价定义或停止规则修改；
- cache 创建、重建、覆盖、迁移或删除；
- 硬失败后的自动重试；
- 诊断后的自动 pre-Gold 恢复。

## 完成后状态

```text
AMENDMENT_5B_V2_OFFICIAL_DECISIONS_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

Hard Failure 4 的修复、byte-equivalence 修改和 controller 重跑均须等待诊断结果独立审核和下一次单独审批。
