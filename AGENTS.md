# HyperGranular-RAG 项目约束

本仓库继承 `E:\科研\AGENTS.md` 的全部规则。发生冲突时采用更严格的规则。

## 项目边界

- 代码与文档：`E:\科研\HyperGranular-RAG`
- 本地未跟踪数据：`E:\科研\超粒球RAG_数据`
- GitHub：`https://github.com/lljjcc426/HyperGranular-RAG`
- 允许的会话上下文：当前对话，以及用户明确指定的同一 HyperGranular-RAG 项目内部会话
- 禁止：其他项目会话、全局 Codex 记忆、项目外研究参数或结论

## 当前科研硬约束

1. `docs/PRIOR_STAGE_METHOD_AUDIT.md` 规定既有阶段的证据等级。
2. Stage3B 始终锁定，除非新的预注册协议和用户明确批准同时满足。
3. Stage2G 未验证 boundary-only 规则，不得把它作为已支持机制复活。
4. 原 Stage4A 镜像 pilot 已失效，只能保留为历史记录。
5. Stage4A-R2 已完成并独立验证；Stage4B-U1 v2 架构仅为 `ACCEPTED_IN_PRINCIPLE`。
6. q25 阈值 `0.1957079917192459` 只能作为冻结迁移策略使用，不得声称是 2Wiki 最优阈值。
7. 任何硬失败后的修订必须先批准、写入、提交并推送，再执行。
8. Stage4B-U1-D v2.2 official pre-Gold 已在 independent verifier 命中 `HARD_FAILURE_VERIFIER_FIXED_TOP20_ASSUMPTION` 并停止；当前状态为 `PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_3`，未生成 `VERIFIED_PRE_GOLD`。
9. 现有 commit `9207bd78eea44d2ea3291fe9b6748526969a3224` 中的 channel audit/decision/ranking/policy 必须保留为失败证据，状态为 `UNVERIFIED_INVALID_FOR_GOLD`，不得覆盖、删除、解释或用于 Gold。
10. Amendment 3 已获 implementation/synthetic-only 批准，绑定审批包提交 `42747507d6f37c3d5713949de443311b35262a2d` 与失败审计提交 `8b43de72418ccda85af3015f758c39bce9d31411`。仅允许 effective-K 协议、checkpoint、verifier、synthetic runner 绑定和测试修订。
11. Amendment 3 implementation baseline 为 `stage4b_u1_v2_3`；independent verifier 必须使用 `K_q=min(20,|C_q|)`、`P_q=min(10,K_q)` 并执行候选池、长度、唯一性、成员、前缀、插入与 final selector 硬门。synthetic suite 为原 24 项加 9 项 effective-K hardening，共 33 项。
12. v2.3 official-resumption package commit `dbb4e057405069aceda5a7c5d88d9d39a4d14775` 已被审查退回，状态为 `RETURN_FOR_PROTOCOL_AND_CACHE_FAIL_CLOSED_REVISION`，不得据此执行 official preflight 或后续命令。
13. Amendment 4 已获 implementation/synthetic-only 批准，绑定 package `e5a0e2187e770c9d7b9e9a85a6b8e91067ed2af1`、returned package `dbb4e057405069aceda5a7c5d88d9d39a4d14775` 与 baseline implementation `a1d9ea0c517fcbad1ef27e78e760738d5c04d8b3`。仅允许 checkpoint、cache fail-closed、pending outputs、runner governance binding、十路径 registry、测试和 evidence 修订。
14. Amendment 4 implementation baseline 为 `stage4b_u1_v2_3_1`：formal controller 强制 require-existing/no-build、cache 前后 fingerprint、OS-temp pending outputs、v2.2 decisions/rankings/policy 等价门和 exclusive promotion rollback；runner 支持登记治理文件绑定；十路径以 Amendment 4 manifest 为唯一 registry。
15. synthetic suite 保留原 33 项并新增 17 项 cache/governance hardening，共 50 项。最终 evidence 必须在本条及全部绑定文件的稳定字节上连续运行两次，全部通过且字节一致。
16. Amendment 4 测试只能使用 synthetic cache；禁止读取 official development/source audit/official ranking/official cache，禁止运行 official preflight/channel/controller/cache audit/verifier/evaluator。
17. fresh ID-bound cache 与旧 Stage4A-R2 cache 必须原样保留；U1-D Gold evaluation、任何 U1-D 指标读取或解释、U1-D 晋级、reservation 和 Stage3B 全部锁定。
18. Stage4B-U1-D v2.3.1 official pre-Gold 恢复已获批准，严格绑定恢复审批包提交 `e76c921454697d1784b0d76a9d9677113051f0f6` 与实现提交 `34349c70ee24b8240fd169393134d4280968b790`。批准决定为 `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_APPROVAL_DECISION.md`。
19. 唯一允许顺序为：批准治理提交推送 -> 两次 50 项 governance-bound synthetic rebinding 并提交推送 -> 一次 formal preflight -> 一次 versioned channel -> 一次 require-existing controller -> 工件提交推送 -> 一次 independent verifier -> 推送 `VERIFIED_PRE_GOLD` 后立即停止。任一硬失败不得自动重跑。
20. 本批准不授权 Gold evaluation、U1-D 指标读取或解释、U1-D 结论、reservation、Stage3B、实现/参数变更、cache 写入或 v2.2 失败工件改写。
21. v2.3.1 唯一一次 formal preflight 与唯一一次 channel preparation 均通过；唯一一次 require-existing controller 在 pending decisions 的 v2.2 字节等价门触发 `HARD_FAILURE_V2_3_1_DECISIONS_EQUIVALENCE`。当前状态为 `PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_4`。
22. Hard Failure 4 未提升 decisions/rankings/policy，未生成 controller execution audit 或 `VERIFIED_PRE_GOLD`，fresh/legacy cache 与 v2.2 工件 hash 均未变化。禁止自动重跑、运行 verifier 或诊断 official ranking 内容；后续必须先形成并批准新的审查/Amendment。
23. Amendment 5A implementation/synthetic-only 已获批准，绑定 package `81d8c34f1cf2539a4c0b81c6148047bc666e2f82` 及 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_APPROVAL_DECISION.md` 中六个历史提交。只允许 decisions comparator、synthetic-only temp capture、至少 24 项新增测试、双次 deterministic evidence、implementation audit 和 5B 审批包。
24. 5A 禁止读取 official units/queries/source audit/cache/decisions/rankings，禁止 official comparator/capture、controller、verifier、evaluator、Gold、reservation、Stage3B 和 byte-equivalence 放宽。测试必须主动拦截这些路径与 ranking/policy 调用。
25. 5A 完成后状态只能为 `AMENDMENT_5A_SYNTHETICALLY_VERIFIED` 且 official diagnosis/controller rerun/verifier 均未批准；5B package 推送后必须立即停止。
26. Amendment 5B package commit `ceb755252540cf223aa18ac721443154c29cd07a` 已按 `RETURN_AMENDMENT_5B_FOR_CHANNEL_INPUT_HASH_BINDING` 退回。不得使用 5B authorization token，不得运行 5B preflight、official capture、controller、verifier 或 Gold evaluation。
27. 后续 5A.1 及新版 5B 必须外部冻结三项 channel 输入：units SHA-256 `114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA`、queries SHA-256 `6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B`、controller channel audit SHA-256 `D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA`。
28. 当前仅可组装并推送 Amendment 5A.1 审批请求和 Manifest。该 package 本身不授权代码修改、synthetic 验证或任何 official 文件访问；实现必须等待明确绑定 5A.1 package commit 的新批准。
29. 未来 5A.1 只能修改 decisions diagnostic capture 的三 SHA 前后硬门、对应 synthetic tests/evidence 及治理绑定；controller、retrieval、comparator 语义、byte-equivalence、模型、参数、score、ECDF、预算、trigger、ranking、endpoint 和停止规则必须保持不变。完成并推送新版 5B package 后必须停止。
30. Amendment 5A.1 implementation/synthetic-only 已获批准，严格绑定 package commit `3137ace0328dd24908f95737ea1dcbe0c8fe045e` 及其 Manifest 中七个历史提交。批准决定为 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_1_APPROVAL_DECISION.md`。
31. 5A.1 只允许修改 Manifest 登记的三个实现/测试文件，保留原 98 项并新增至少 6 项测试，完整 suite 至少 104 项且连续两次字节一致、零 failure/error/skip/official access。禁止读取任何 official 输入、使用已退回 5B token、运行 official capture/controller/verifier/evaluator 或接触 Gold/reservation/Stage3B；新版 5B v2 包推送后立即停止。
32. Amendment 5A.1 已完成并通过 synthetic 验证，implementation/evidence commit 为 `e566eb861ec6028ca89a40c9aca7d06737f1eb8e`。原 98 项全部保留，新增 9 项后共 107 项；两次最终 evidence 均为 20,495 bytes、SHA-256 `81A8A5960395F729B643A42505E7F947962B338CD97ADD0506636D3AA2020A67`，且零 failure/error/skip/official access。
33. 新版 Amendment 5B v2 仅为审批请求，文件为 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_V2_OFFICIAL_DIAGNOSTIC_APPROVAL_REQUEST.md` 与 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_V2_MANIFEST.json`。在明确绑定其 package commit 的新批准前，不得运行 post-approval rebinding、preflight、official capture、controller、verifier、evaluator 或 Gold。
34. capture 中现有 `APPROVE_STAGE4B_U1_D_AMENDMENT_5B_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC` 仅是实现参数，不是自足授权；5A.1 中未使用。只有未来 package-bound 5B v2 批准明确激活后才可传入，且仍须逐项匹配三项外部冻结 SHA、cache/reference SHA、精确路径和一次性停止边界。
35. Amendment 5B v2 单次 official decisions-only 诊断已获批准，严格绑定 package commit `f43e22ef079701139d4437849be8ad57654f80d7` 及其七个历史提交。批准决定为 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_V2_APPROVAL_DECISION.md`。
36. 唯一允许顺序为：批准治理提交推送 -> 两次 107 项 post-approval rebinding -> governance-binding 与 rebinding audit 提交推送 -> 唯一一次只读 preflight -> 通过后唯一一次 exact-command capture -> 聚合边界核验与 machine/narrative audit 提交推送 -> 立即停止。任一硬失败不得自动重试。
37. 本批准不授权完整 controller、official ranking/reference policy、source-audit 文件、verifier、evaluator/Gold、reservation、Stage3B、代码/参数/等价门修改、cache 写入或正式 decisions/rankings/policy 提升。capture token 只有在 rebinding 和 preflight 全部通过后才可在获批 exact command 中传入一次。
38. 5B v2 批准治理 commit `2ddf6e044c27e47385a558bdaca80cb6c31c4ffe` 与 rebinding/governance commit `4c10ad942a75af42b910b860fd4897b672160d5d` 已推送；两次 107 项 rebinding 均全通过且 evidence SHA-256 为 `7D9C3527480ECDFFA87C943589538BCEFEFA3610A6D415719429CDE5D222D12E`。唯一一次只读 preflight 全部通过。
39. 唯一一次 official capture 在 comparator 读取冻结 v2.2 reference decisions 时触发 `HARD_FAILURE_5_INCOMPARABLE_HETEROGENEOUS_REFERENCE_DECISIONS_SCHEMA`，错误边界为 `Incomparable heterogeneous decisions schema at line 2`。当前状态为 `AMENDMENT_5B_V2_OFFICIAL_DIAGNOSTIC_STOPPED_HARD_FAILURE_5`，不得重跑 capture 或继续读取 official decisions 内容。
40. Hard Failure 5 未生成 machine/narrative audit，temporary decisions 已清理，三项 channel/cache/reference SHA 与 cache bytes 未变化，五项正式输出仍不存在。后续任何 schema-only 诊断、comparator 修改、reference normalization 或 capture/controller 重跑均须新的 package-bound Amendment 批准。
41. Hard Failure 5 审查决定为 `RETURN_FOR_REFERENCE_DECISIONS_SCHEMA_DIAGNOSTIC_AMENDMENT_PACKAGE`。schema diagnostic、comparator change、official capture retry、controller rerun、verifier 与 Gold 均未批准；当前 official diagnosis 仍为 incomplete。
42. 当前唯一允许动作是组装并推送 Amendment 5C-A 审批请求与机器可读 Manifest。该 package 本身不授权实现、synthetic 执行或任何 official 文件读取；任何批准必须显式绑定 package commit。
43. 未来 5C-A 如获批准，只能新增独立 schema inventory、独立 deterministic runner 与独立 tests；现有 comparator、capture、controller、retrieval、common、现有 runner/tests、byte-equivalence 和全部科研参数必须保持不变。原 107 项测试必须保留，至少新增 12 项后完整 suite 不少于 119 项，并连续两次全通过、零 official access、evidence 字节一致。
44. 未来 5C-B 必须另行组包和批准，且最多只允许对冻结路径/SHA 的 v2.2 reference decisions 做一次 schema-only scan。5C-A 完成不得自动读取 official reference、修改 comparator、normalization、重跑 capture/controller、运行 verifier 或接触 Gold/reservation/Stage3B。
45. Amendment 5C-A implementation/synthetic-only 已获批准，严格绑定 package commit `a8caa2a3b26ae13d0b149e4995e3a017e8edb2e7` 及其 Manifest 中八个历史提交。批准决定为 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_APPROVAL_DECISION.md`。
46. 5C-A 只允许新增 Manifest 登记的 schema inventory、deterministic runner 与 tests 三个文件，以及批准/审计/evidence/未来 5C-B package 和必要治理同步。任何现有实现、测试、official artifact、历史 evidence 或 failure record 不得修改或删除；official reference 与全部 official 输入不得打开。
47. 5C-A 必须保留 107 项并至少新增 12 项，完整 suite 不少于 119 项；相同 tracked bytes 上连续两次全通过、零 failure/error/skip/official access 且完整 evidence 字节一致。完成后状态仅为 `AMENDMENT_5C_A_SYNTHETICALLY_VERIFIED`，5C-B official scan、comparator/capture/controller/verifier/Gold 仍须另行批准。
48. 5C-A implementation baseline 仅包含三个获批新文件，并新增 24 项 inventory tests，使完整 suite 为 131 项。最终完成状态只在 `results/stage4b_u1_d_pregold_amendment_5c_a_synthetic_verification.json` 对本条及全部绑定实现字节连续两次验证均为 131/131、零 failure/error/skip/official access 且 evidence 字节一致时成立；详细 hash 和失败命令记录以 implementation audit 为准。
49. Amendment 5C-A implementation/evidence commit 为 `492a59b2f4daccd3e123f2b6cc49cd896d5009d1`。最终两次 evidence 均为 22,234 bytes、SHA-256 `0D13392B5C96BAD7EC4D67C22A7515B4A6D211C8EFBB3A4486F9BA5531A1EF7C`；131/131、24 项 inventory tests、零 failure/error/skip/official access，八个冻结文件 hash 未变化。
50. Amendment 5C-B request/Manifest 仅为单次 reference-decisions schema-only official scan 审批包。包本身不授权 token、post-approval rebinding、preflight 或 scan；必须等待明确绑定 5C-B package commit 的新批准。
51. 未来 5C-B 如获批准，顺序只能为批准治理推送 -> 两次 131 项 rebinding 与 governance binding 推送 -> 一次 SHA-only preflight -> 一次 exact-command value-free schema scan -> machine/narrative audit 推送 -> 立即停止。不得读取其他 official 文件、输出任何字段值/ID、修改 comparator/normalization、重跑 capture/controller、运行 verifier/evaluator 或接触 Gold/reservation/Stage3B。
52. Amendment 5C-B 单次 official reference-decisions value-free schema-only scan 已获批准，严格绑定 package commit `e5a6c5479dbd125ebb58b95e9594fadde6b6719d` 及批准决定登记的八个历史提交。批准决定为 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_B_APPROVAL_DECISION.md`。
53. 唯一允许顺序为：批准治理提交推送 -> 在最终批准治理字节上两次 131 项 post-approval rebinding -> governance-binding 与 rebinding audit 提交推送 -> 唯一一次 SHA-only formal preflight -> 唯一一次 exact-command schema-only scan -> machine/narrative audit 提交推送 -> 立即停止。任一 rebinding、binding、preflight、scan、validation、commit 或 push 硬门失败均不得重试。
54. 5C-B 唯一 official 输入为 `results/stage4b_u1_d_official_dev4500_decisions.jsonl`，冻结 SHA-256 为 `6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7`。Preflight 只能按字节计算 SHA；scan 只允许一次 value-free schema parse，输出严格限于 Manifest 白名单中的聚合 schema metadata。
55. 5C-B 不授权任何其他 official 文件、字段值/ID、comparator/capture/controller/verifier/evaluator、new decisions/rankings/policy、Gold/U1-D 指标、reservation、Stage3B、cache/历史工件改写或自动恢复。完成状态只能是 `REFERENCE_DECISIONS_SCHEMA_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW`，其余 capture retry、comparator change、controller rerun、verifier 与 Gold 继续锁定。
56. Amendment 5C-B 审核已接受，严格绑定最终提交 `e5f28f664449c02b12a129aaa2a011bad84dab91`。当前状态为 `AMENDMENT_5C_B_REVIEW_ACCEPTED`；Hard Failure 5 的直接原因已确认为 comparator 的文件级同构 schema 假设与合法 nullable rows 不兼容。
57. 5C-B 只确认 reference decisions 内有 2 个 schema、8 个 numeric/null 类型差异；它未生成或比较 v2.3.1 temporary decisions，因此 Hard Failure 4 diagnosis 仍为 incomplete，不得据此主张 byte/semantic 等价或恢复 controller、verifier、Gold。
58. Amendment 5D-A request/Manifest 仅为 heterogeneous-schema comparator implementation/synthetic-only 审批包。包本身不授权 comparator 修改、测试执行或任何 official 文件访问；必须等待明确绑定未来 5D-A package commit 的批准。
59. 未来 5D-A 如获批准，只能修改 comparator、decisions diagnostic synthetic runner 与对应 diagnostic tests 三个 Manifest 登记文件。允许的语义变化仅为移除全文件 complete-type-signature 同构拒绝并更新 comparator version/checkpoint；逐 query 比较、aggregate output、raw-byte 主门、no-normalization 与全部科研参数必须保持不变。
60. 5D-A 必须保留现有 131 项，至少新增 12 项 heterogeneous-schema hardening 后完整 suite 不少于 143 项，并在相同 tracked bytes 上连续两次全通过、零 failure/error/skip/official access、evidence 字节一致。5D-A 不授权 capture/controller/verifier/evaluator/Gold；未来 5D-B 必须另行组包、审批且不得自动执行。
61. Amendment 5D-A implementation/synthetic-only 已获批准，严格绑定 package commit `33ce115f78840956fcc7bda0c3f4e172579350e7` 及其 Manifest 中十二个历史提交。批准决定为 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_A_APPROVAL_DECISION.md`。
62. 5D-A 只允许修改 Manifest 登记的 comparator、decisions diagnostic synthetic runner 和 diagnostic tests。Comparator 仅可更新至 `stage4b_u1_decisions_diagnostic_v2` / `stage4b_u1_decisions_diag_v2` 并移除 loader 的全文件同构 schema 拒绝；其余逐 query 算法、aggregate keys、raw-byte 主门与 no-normalization 全部冻结。
63. 5D-A 完整 suite 必须保留 131 项并至少新增 12 项达到不少于 143 项；最终两次运行必须相同 tracked bytes、全通过、零 failure/error/skip/official access 且 evidence 字节一致。本批准不授权任何 official 输入、official comparator/capture、controller/verifier/evaluator/Gold、reservation、Stage3B 或 5D-B 执行。
64. 5D-A implementation baseline 已限定为 comparator 的 v2 version/checkpoint 更新与 `file_schema` 同构拒绝块删除、runner 的 5D-A governance/frozen-hash/143-test 门，以及 diagnostic tests 的 12 项净新增。Comparator 其余逐 query 算法、capture/controller 与 Manifest 冻结文件保持不变。
65. 5D-A 完成状态只在 `results/stage4b_u1_d_pregold_amendment_5d_a_synthetic_verification.json` 对本条及全部 runner 绑定字节连续两次验证均不少于 143/143、零 failure/error/skip/official access 且 evidence 字节一致时成立。完成后只可形成 implementation audit/evidence commit 与 5D-B package，随后停止等待审批。
66. Amendment 5D-B 单次 official decisions-only diagnostic 已获批准，严格绑定 package commit `f67061e753b03a5cf46d7a7c92b5a95fc79b0ef8`、5D-A implementation/evidence commit `02f46447e4cd69a15d2af14ee1fc62f9eb4f8bb9` 及批准决定登记的历史提交。批准决定为 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_B_APPROVAL_DECISION.md`。
67. 唯一允许顺序为：批准治理提交推送 -> 最终治理字节上两次 143 项 post-approval rebinding -> governance-binding 与 narrative rebinding audit 提交推送 -> 唯一一次只读 formal preflight -> 通过后唯一一次 exact-command capture -> 一次仅字节哈希/元数据 post-run 核验 -> aggregate machine/narrative audit 提交推送 -> 立即停止。任一硬失败不得重试。
68. 5D-B official 读取边界仅为 Manifest 冻结的 units、queries、controller channel audit、existing cache 和 v2.2 reference decisions 五项。Stage4A-R2 source-audit 文件、5C-B machine inventory、official rankings、reference policy、evaluator/Gold、reservation 和 Stage3B 均不得打开；source-audit 仅可核验 channel 中已登记 digest。
69. Capture/comparator hash、双 ID、query/unit 数、模型、`max_length=192`、`batch_size=64`、controller/diagnostic checkpoint、raw-byte 控制门和 no-normalization 全部冻结。历史 5B token 仅在本批准 exact command 中重新授权一次；禁止第二次 preflight/capture、完整 controller、verifier、正式输出提升、cache 变更或诊断后自动恢复。
70. 成功完成后状态只能为 `AMENDMENT_5D_B_OFFICIAL_DECISIONS_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW` 与 `HARD_FAILURE_4_DIAGNOSIS_COMPLETE_AWAITING_REVIEW`，controller rerun、verifier 和 Gold 继续未批准；任何诊断分类均不得自动产生有效性或晋级结论。
71. Amendment 5D-B 唯一一次 formal preflight 已在同步 clean HEAD `2447ad234c160c6e615d81b33dc4ede7ecaa18da` 消耗，并因 OS temp parent 字符串比较门触发 `HARD_FAILURE_6_FORMAL_PREFLIGHT_OS_TEMP_PATH_COMPARISON`。失败审计为 `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_6.md`。
72. Hard Failure 6 发生在五项 official 输入普通文件检查、SHA 读取和语义解析之前；official capture 未运行、token 未传入，machine/narrative audit 与五项正式输出均不存在，diagnostic temp 残留为 0。Hard Failure 4 diagnosis 继续 incomplete。
73. 5D-B preflight 次数已经耗尽；禁止第二次 preflight、capture、controller、verifier、Gold、reservation 或 Stage3B。任何修正 trailing-separator/path-equivalence 检查或恢复 official diagnostic 的动作必须形成新的 package-bound Amendment 并获得明确批准。
74. Hard Failure 6 Review 1 已接受失败审计并决定 `RETURN_FOR_AMENDMENT_5E_A_PACKAGE`，记录于 `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_6_REVIEW_1.md`。当前 path-equivalence fix、formal preflight retry、capture、controller、verifier 与 Gold 均未批准。
75. Amendment 5E-A request/Manifest 仅为 Windows OS-temp path-equivalence helper implementation/synthetic-only 审批包。包本身不授权 helper/runner/tests 修改、synthetic 执行、official metadata/content 访问、formal preflight、token 或 capture；必须等待明确绑定未来 package commit 的批准。
76. 未来 5E-A 如获批准，只能新增 `scripts/stage4b_u1_preflight_path_equivalence.py`、新增 `tests/test_stage4b_u1_preflight_path_equivalence.py` 并按 Manifest 限定修改 diagnostic deterministic runner。Capture、comparator、controller、retrieval、common 及全部科研数据/参数/等价门必须保持冻结。
77. 5E-A 必须以 143 项为基线，新增至少 12 项后完整 suite 不少于 155 项；相同 tracked bytes 上连续两次全通过、零 failure/error/skip/official access，且 formal preflight/token/capture 次数均为 0、完整 evidence 字节一致。完成后只能组装新的 5E-B package 并停止等待审批。
78. Amendment 5E-A implementation/synthetic-only 已获批准，严格绑定 package commit `19f16f559f0b1f3b59ef24a04e368f99ae3635e3` 及 Manifest 登记的治理历史。批准决定为 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5E_A_APPROVAL_DECISION.md`。
79. 5E-A 只允许新增 fail-closed Windows OS-temp path-equivalence helper、新增对应 synthetic tests，并按 Manifest 限定修改 diagnostic deterministic runner。比较可规范化，但 exact capture command 与原始 `--temp-parent` 字符串、capture/comparator/controller/retrieval/common、科研参数和 raw-byte equivalence 必须保持不变。
80. 5E-A 完整 suite 必须以 143 项为基线、至少新增 12 项达到不少于 155 项；最终相同 tracked bytes 上连续两次全通过、零 failure/error/skip/official access、零 formal-preflight/token/capture 调用且 evidence 字节一致。5E-A 不授权任何 official 读取或执行，未来 5E-B 必须另行组包和审批。
81. 5E-A implementation baseline 仅包含新 helper、新 test module 和 Manifest 限定的 deterministic runner 更新；当前新增 18 项 synthetic tests，preliminary 完整 suite 为 161/161。最终状态只能由绑定本条及全部获批/冻结字节的两轮 byte-identical evidence 确认。
82. 5E-A 完成后只允许提交 implementation audit/evidence、组装 implementation-bound 5E-B request/Manifest 并停止。5E-B 必须要求新的 formal preflight 直接 import/call 已测试且哈希绑定的 helper，不得复制新的内联路径比较逻辑；在 5E-B 获批前 formal preflight、capture、controller、verifier 与 Gold 继续锁定。
83. Amendment 5E-A implementation/evidence commit 为 `a8b064a4a2133aea27cbe9b85978237fc3dae661`。最终两轮均为 161/161、零 failure/error/skip/official access/formal-preflight/token/capture；evidence 为 36,518 bytes、SHA-256 `84C58CBA9801A6EB8DFAF4ED6688BB5FCBD5777729FD833083E16CB630FFED83` 且逐字节一致。
84. Amendment 5E-B request/Manifest 仅为一次 helper-bound formal preflight 与条件式单次原 exact-command decisions-only capture 的审批包。包本身不授权 post-approval rebinding、preflight、helper official-boundary check、token、capture、controller、verifier 或 Gold；必须等待明确绑定未来 5E-B package commit 的批准。
85. 未来 5E-B 如获批准，必须先在最终批准治理字节上完成两轮 161 项 byte-identical rebinding 与 governance binding；随后唯一 preflight 必须先核验 helper SHA/bytes 并直接 import/call `windows_directories_equivalent()`，在 helper gate 通过前不得检查任何 official 输入 metadata/content，禁止复制内联 PowerShell path-equivalence 算法。
86. 5E-B 请求中的五项 official read boundary、capture/comparator/controller checkpoints、模型/参数、raw-byte 控制门、token string 与 exact capture command 全部继承 5D-B 冻结值。任何 hard gate 失败必须停止且不得重试；成功诊断后也必须停止等待独立审核，不得自动恢复 controller、verifier 或 Gold。
87. Amendment 5E-B 已获批准，严格绑定 package commit `e387d2707ede9024571249face71bf7ca3afd4e0`、5E-A implementation/evidence `a8b064a4a2133aea27cbe9b85978237fc3dae661` 及批准决定登记的治理历史。批准决定为 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5E_B_APPROVAL_DECISION.md`。
88. 唯一顺序为：批准治理推送 -> 最终治理字节上两轮 161 项 rebinding -> governance binding 与 narrative audit 推送 -> 一次 A/B/C/D formal preflight -> 全部门通过后一次 unchanged exact capture -> post-run 核验与 aggregate audit 推送 -> 立即停止。任一 hard gate 失败不得重试。
89. Preflight 必须在任何 official input metadata/content 操作前完成治理门、输出/残留缺失门和 helper hash/direct-call 门。Helper 必须保持 3,543 bytes、SHA-256 `1A17C0E750F91CEF2F638A0B0C6FD381110692E6B2D467C1F5243ADF3F35B3FF`，runtime 参数必须是未经改写的 `.NET GetTempPath()` 原始值，禁止重新内联路径比较。
90. 只有 helper gate 通过后才允许检查五项冻结 official inputs；只有唯一 preflight 全通过后才允许一次原 exact capture。Post-run 不得重新解析 reference decisions，只可使用 machine audit 与字节 fingerprint；五项 formal outputs 必须继续不存在。
91. 本批准不授权第二次 preflight/capture、full controller、verifier、evaluator/Gold、rankings/reference policy、source-audit 文件、5C-B inventory、reservation、Stage3B、formal output promotion、equivalence/数据/模型/参数修改或诊断后自动恢复。
92. 5E-B 唯一 formal preflight 已在 clean synchronized HEAD `3185c3bd4ffd3eb2bc61b52fdf18a3367b9dca76` 消耗。A 项目/治理门通过；B 的 raw-substring prohibited-argument 检查以 `gold` 误匹配获批 machine audit 路径中的 `pregold`，触发 `HARD_FAILURE_7_FORMAL_PREFLIGHT_PROHIBITED_ARGUMENT_SUBSTRING_FALSE_POSITIVE`。
93. Hard Failure 7 发生在 helper hash/direct-call 和五项 official input metadata/content 门之前。Helper、official input access、token、capture、controller、verifier、evaluator/Gold 调用均为 0；Hard Failure 4 diagnosis 继续 incomplete。
94. 失败后 metadata-only 核验确认 machine/narrative audit 不存在、五项 formal outputs 为 0、diagnostic temp residue 为 0。没有仓库或 official artifact 被删除、覆盖或修改；详细审计为 `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_7.md`。
95. 5E-B preflight 授权已耗尽；禁止第二次 preflight、helper official-boundary check、token 或 capture。任何替代 raw-substring argument classification 或恢复 official diagnostic 的动作必须形成新的 package-bound Amendment 并获得明确批准。
96. Hard Failure 7 Review 1 已接受失败审计并决定 `RETURN_FOR_AMENDMENT_5F_A_PACKAGE`，记录于 `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_7_REVIEW_1.md`。当前 argument-policy fix、formal preflight retry、helper official-boundary check、capture、controller、verifier 与 Gold 均未批准。
97. Amendment 5F-A request/Manifest 仅为 typed capture-argument policy helper implementation/synthetic-only 审批包。包本身不授权 helper/runner/tests 修改、synthetic 执行、official metadata/content 访问、real OS-temp helper check、preflight、token 或 capture；必须等待明确绑定未来 package commit 的批准。
98. 未来 5F-A 如获批准，只能新增 `scripts/stage4b_u1_preflight_argument_policy.py`、新增 `tests/test_stage4b_u1_preflight_argument_policy.py` 并按 Manifest 限定修改 diagnostic deterministic runner。现有 path-equivalence helper、capture、comparator、common、controller、retrieval、数据、参数和 raw-byte equivalence 必须保持冻结。
99. 5F-A 必须以 161 项为基线，新增至少 16 项后完整 suite 不少于 177 项；相同 tracked bytes 上连续两次全通过、零 failure/error/skip/official access/path-helper official invocation/preflight/token/capture 且 evidence 字节一致。implementation/evidence 推送后必须停止等待独立审核；只有该审核明确接受后才能另行组装 5F-B package。
100. Amendment 5F-A implementation/synthetic-only 已获批准，严格绑定 package commit `2b82ba3f0ac9756091d74567f4aed8df5cdf626d` 及批准决定登记的历史提交；批准决定为 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5F_A_APPROVAL_DECISION.md`。
101. 5F-A 只允许新增 typed argument-policy helper、新增对应 synthetic test，并按 Manifest 限定修改 diagnostic deterministic runner。Manifest 登记的 17 个冻结文件、exact argv、token、科研参数和 raw-byte equivalence 必须保持不变。
102. typed helper 必须执行 exact argv equality、15-flag typed allowlist、per-role exact binding 和 explicit prohibited-role rejection；必须接受冻结 `pregold` 输出路径，禁止任何裸 `gold` value-substring denylist，且不得访问文件系统、hash、subprocess、capture、token 或 path helper。
103. 最终完整 suite 必须不少于 177 项并在相同 tracked bytes 上连续运行两次；两次均须零 failure/error/skip/official access/path-helper official invocation/preflight/token/capture 且完整 evidence 字节一致。
104. 5F-A completion 只允许 implementation/evidence 与必要治理状态提交推送，随后立即停止等待独立审核。本批准不授权 5F-B 组包、real OS-temp helper check、formal preflight、official capture、controller、verifier、evaluator/Gold、reservation 或 Stage3B。
105. 5F-A implementation baseline 仅包含新 typed argument-policy helper、新 test module 与 Manifest 限定的 deterministic runner 更新；新增 test module 共 44 项。首次 module-name 定向命令因 `tests` 非 Python package 而在 discovery 前失败，修正为 `unittest discover` 后定向测试 44/44 通过。
106. preliminary complete suite 为 205/205、零 failure/error/skip/official access，preliminary OS-temp evidence 已在检查后删除。该结果不是最终 evidence；最终完成状态只在本条及全部治理/实现/冻结字节稳定后连续两轮完整 suite 均为 205/205、零访问/调用且 evidence 字节一致时成立。
107. 5F-A 最终 evidence 必须记录 path-helper official invocation、formal preflight、authorization token、official capture 均为 0，并证明 typed helper 无 filesystem/hash/subprocess/capture/token/path-helper 调用及无裸 `gold` value-substring denylist。implementation/evidence 推送后必须停止等待独立审核，不得组装 5F-B。
108. 5F-A 独立审核现已接受 implementation/evidence commit `e7b688d4b67db596df1d447e2cf70f12f0ea5d0b`，并仅授权组装 implementation-bound 5F-B 审批包；审核记录为 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5F_A_REVIEW_1.md`。
109. 5F-B request/Manifest 本身不授权 post-approval synthetic rebinding、governance binding、typed helper official-command 调用、real OS-temp path helper、formal preflight、official input metadata/content、token、capture、controller、verifier 或 Gold。任何执行必须等待明确绑定未来 5F-B package commit 的新批准。
110. 未来 5F-B 如获批准，唯一顺序必须为：批准治理提交推送；相同最终治理字节上连续两轮 205/205 synthetic rebinding 且 evidence 字节一致；governance binding 与审计提交推送；一次 A/B/C/D formal preflight；全部通过后条件性运行一次 unchanged exact capture；聚合审计提交推送后立即停止。任一硬失败不得重试。
111. 5F-B formal preflight 的 A 门只检查 Git/治理/hash/输出与残留不存在，不得访问五项 official inputs。A 必须从 `e7b688d...` Git blob 核验历史 `AGENTS.md` hash、对当前树复算其余 25 项 accepted hashes，并对 post-approval evidence 复算含最终 `AGENTS.md` 的全部 26 项 current hashes；不得把最终治理 `AGENTS.md` 与历史 hash 直接比较。B 门必须先核验 typed helper SHA `CCDC70D2E66E9D69CD64899676EA5150FEE0381E74F4C9DEED2A0FFB5EE436F4` 和 5E-B Manifest SHA，再直接调用 `validate_capture_argv` 比较两份 Manifest 的 exact argv；禁止内联或 fallback，禁止裸字符串关键词扫描。
112. 只有 B 通过后，C 门才可核验 path helper SHA `1A17C0E750F91CEF2F638A0B0C6FD381110692E6B2D467C1F5243ADF3F35B3FF`，并直接调用 `windows_directories_equivalent` 比较未改写的 `.NET GetTempPath()` 与冻结目录。只有 B/C 均通过后，D 门才可访问 Manifest 登记的五项 official inputs。
113. 5F-B exact capture command 必须与 hash-bound 5E-B Manifest 的 32 个 argv 元素逐项完全一致；raw-byte equality 继续为首要冻结门。不得修改代码、测试、数据、模型、参数、equivalence 或 stop rules，不得读取 rankings、reference policy、source-audit 文件、5C-B inventory、Gold、reservation 或 Stage3B。
114. 当前状态为 `AMENDMENT_5F_B_AWAITING_APPROVAL`。5F-B package 组装提交推送后必须停止等待独立审批；formal preflight retry、path-helper official-boundary check、authorization token、official capture、controller rerun、verifier 和 Gold 均未批准。
115. Amendment 5F-B 已获 package-bound 批准，严格绑定 package commit `f33ee70233ea4098b2d7a17cfde3d266081ee693` 及批准决定登记的历史提交。批准决定为 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5F_B_APPROVAL_DECISION.md`。
116. 唯一执行顺序冻结为：批准治理提交推送；最终治理字节上两轮 205/205 synthetic rebinding；rebinding evidence/governance binding/audit 提交推送；唯一一次 A→B→C→D preflight；全部通过后一次 unchanged exact capture；聚合审计提交推送后立即停止。任一硬失败不得重试。
117. Rebinding evidence 必须绑定当前 26 项实现/治理字节；governance-binding JSON 必须额外绑定 5F-B request、Manifest、approval decision 与 rebinding evidence。不得声称 runner 自身直接包含全部 5F-B package 文件。
118. Preflight A 只能读取项目治理文件与输出路径 metadata，不得访问五项 official inputs。A 必须核验同步 clean Git、提交祖先、历史 `e7b688d...:AGENTS.md`、当前其余 25 项 accepted hashes、post-approval 全部 26 项 current hashes、helpers/capture/comparator/runner/tests hashes，以及 machine/narrative audit、五项 formal outputs和 OS-temp residue 不存在。
119. Preflight B 只允许运行一次：核验 typed helper 与 5E-B Manifest bytes/SHA，从 hash-bound 5F-B/5E-B Manifest 读取 actual/approved argv，并直接调用 `validate_capture_argv`。必须 exact equality、32 elements、15 flags、7 path roles、0 prohibited roles；禁止内联、fallback 或关键词扫描，且不得访问 argv 所指文件的 metadata/content。
120. 只有 B 通过后，Preflight C 才可核验并直接调用冻结 path helper，比对未改写的 `.NET GetTempPath()` 与精确目录 `C:\Users\cc\AppData\Local\Temp`。只有 B/C 均通过后，D 才可访问五项 official inputs并核验 Manifest 冻结的路径、SHA、计数、dual-ID 与 cache 完整性。
121. 只有 A/B/C/D 全部通过后，才允许一次 Manifest unchanged 32-element exact capture。Post-run 不得再次语义解析 reference/temporary decisions，只可核验 aggregate machine audit、input/cache fingerprints、cleanup 和 formal-output absence。
122. 本批准不授权任何代码/测试/科研参数/equivalence 修改、第二次 preflight/helper/capture、full controller、verifier、evaluator/Gold、formal output、rankings、reference policy、source-audit 文件、5C-B inventory、reservation、Stage3B、cache/历史工件修改删除或诊断后自动继续。
123. 当前进入 `AMENDMENT_5F_B_APPROVED_AWAITING_POST_APPROVAL_REBINDING`。批准治理提交推送前不得运行 synthetic；rebinding/governance 提交推送前不得运行 preflight。
124. 5F-B 批准治理已提交 `84d39707dee15729dc0c35c85a16f4e31dac89e4`；同一最终治理字节上的两轮 205/205 rebinding 均为零 failure/error/skip/official access/helper official invocation/preflight/token/capture，51,922-byte evidence SHA-256 均为 `829289F10B1C7B39BBE6B37ACF51DCB265764FD10A8DA55892F60D50F6D2CB09` 且逐字节一致。
125. Rebinding evidence、governance binding 与审计已提交推送为 `052e8ecc04f566b75666d5cc96df74d2ed5061e4`；runner evidence 绑定当前 26 项字节，governance JSON 额外绑定 5F-B request/Manifest/approval/evidence，职责分离成立。
126. 5F-B 唯一 formal preflight 在 A 门首项硬失败：local HEAD、origin/main 与 GitHub main 实际均为 `052e8ecc04f566b75666d5cc96df74d2ed5061e4`，但执行 wrapper 错误断言了同短前缀的完整字面量 `052e8ece1839ff253f8aeb84d5f828377be74829`，触发 `HARD_FAILURE_8_FORMAL_PREFLIGHT_A_GATE_EXPECTED_HEAD_LITERAL_MISMATCH`。
127. Hard Failure 8 发生在后续 A hash/output checks、B/C/D 之前；typed helper、path helper、official input access、token、capture、controller、verifier、evaluator/Gold 调用均为 0。失败后 metadata-only 核验确认 machine/narrative audit 不存在、五项 formal outputs 为 0、diagnostic temp residue 为 0。
128. 详细审计为 `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_8.md`。该失败是 preflight command 完整提交字面量转录错误，不是网络、GitHub 漂移、helper、OS-temp、official input、cache 或 capture 失败。
129. 5F-B formal preflight 授权已耗尽；禁止第二次 preflight、typed/path helper official call、official input access、token 或 capture。任何修正和恢复必须形成新的 package-bound Amendment 并获得明确批准；当前状态为 `AMENDMENT_5F_B_FORMAL_PREFLIGHT_STOPPED_HARD_FAILURE_8`。
130. Hard Failure 8 独立审核已接受失败审计与 5F-B post-approval rebinding evidence，并仅授权组装 Amendment 5G-A implementation/synthetic-only 审批包。审核记录为 `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_8_REVIEW_1.md`。
131. 5G-A request/Manifest 本身不授权实现、synthetic、real Git/GitHub execution-head check、第二次 formal preflight、typed/path helper official call、official input metadata/content、token、capture、controller、verifier 或 Gold；也不授权组装 5G-B。当前状态为 `AMENDMENT_5G_A_AWAITING_APPROVAL`。
132. 未来 5G-A 如获 package-bound 批准，只允许新增纯值校验 helper `scripts/stage4b_u1_preflight_execution_head_binding.py`、新增对应 synthetic test，并在限定范围内更新 deterministic runner。Helper 必须由 caller 提供 local/origin/GitHub、parent、changed paths、ancestry、clean-worktree 与 governance facts，不得访问 filesystem、Git、subprocess、official path、现有 helpers、token 或 capture。
133. 未来 execution-head helper 必须要求完整小写 40 位 SHA，拒绝短前缀、大小写/长度/非十六进制漂移；要求 local/origin/GitHub 完整相等、HEAD parent 等于 approval commit、changed-path set 与获批集合精确相等、所需 ancestors/治理绑定/evidence presence/clean-worktree 全部门通过，并返回经验证的当前 HEAD。禁止接受预先转录的未来 expected HEAD 或在源码中固定未来 rebinding SHA。
134. 5G-A synthetic 必须以 205 项为基线，新增至少 16 项后完整 suite 不少于 221 项；在相同 tracked bytes 上连续两次全通过、零 failure/error/skip/official access/helper official invocation/preflight/token/capture 且 evidence 字节一致。实现与 evidence 推送后必须停止等待独立审核，任何 official recovery 仍需新的 5G-B package-bound 审批。
135. Amendment 5G-A 已获 package-bound implementation/synthetic-only 批准，严格绑定 package commit `86ae4a83d55e61653f3cce9260a00852b4aaebda` 及批准决定登记的历史提交。批准决定为 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_APPROVAL_DECISION.md`。
136. 5G-A 只允许新增 execution-head pure-value helper、新增对应 test module，并按 Manifest 限定更新 deterministic runner。全部既有 tests 和 24 个 frozen files 必须保持原 SHA；不得运行 real Git/GitHub execution-head validation 或任何 official 动作。
137. 完整 suite 必须在最终稳定的 tracked bytes 上连续运行两次，均不少于 221 项且 execution-head tests 不少于 16，零 failure/error/skip/official access/typed-helper official invocation/path-helper official invocation/preflight/token/capture，并且 evidence 字节一致。
138. 5G-A implementation/evidence/audit 提交推送后必须立即停止等待独立审核；5G-B 组包、第二次 formal preflight、official input、token、capture、controller、verifier 和 Gold 均未批准。当前状态为 `AMENDMENT_5G_A_APPROVED_AWAITING_IMPLEMENTATION`。
139. 5G-A 新 helper 定向测试唯一一次运行通过 41/41；随后唯一一次 preliminary complete runner 在测试执行前的 active-proof 唯一性门触发 `HARD_FAILURE_9_5G_A_ACTIVE_PROOF_SUFFIX_COLLISION` 并停止，未生成 evidence。
140. Hard Failure 9 直接原因是两个新 test suffix 与既有测试全局重名，其中 `test_helper_uses_only_python_standard_library` 还在 runner active-proof tuple 中重复登记。完整 suite 实际运行数为 0，OS-temp output 从未创建，24 个 frozen hashes 保持 24/24。
141. Hard Failure 9 后不得改名、调整 runner 或重跑 synthetic。当前失败 checkpoint 只包含 5G-A 批准的三个实现/测试路径；详细审计为 `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_9.md`。
142. 当前状态为 `AMENDMENT_5G_A_SYNTHETIC_VERIFICATION_STOPPED_HARD_FAILURE_9`。任何最小修正必须先形成新的 package-bound Amendment 并获明确批准；synthetic retry、5G-B、第二次 preflight、official input、token、capture、controller、verifier 和 Gold 均未批准。
143. Hard Failure 9 独立审核已接受审计并冻结失败 checkpoint `d1c7cf9d78563e30a1e0fe0d6812b36d15b95a9a`，当前仅授权组装 Amendment 5G-A.1 package。审核记录为 `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_9_REVIEW_1.md`。
144. 5G-A.1 request/Manifest 本身不授权 test rename、runner repair、synthetic retry、helper 修改、real Git/GitHub execution-head check、preflight、official input、token、capture、controller、verifier、Gold 或 5G-B。
145. 未来 5G-A.1 如获 package-bound 批准，只允许重命名两个冲突的新测试、同步两个 execution-head suffix、确保通用 path-helper suffix 只登记一次、在 discovery 前增加 suffix tuple 自身唯一性门，并把完整门冻结为精确 246 tests、41 execution-head tests、44 typed-policy tests。Helper SHA `517C5C4DB22A82B4CBCA3D8BB751AAE60C0DCC5B5948CC8419D8770A9CC3D174` 不得改变。
146. 未来执行顺序必须是 approval governance 推送、一次 source-only active-proof inventory、一次 41/41 定向测试、最终稳定 tracked bytes 上两轮精确 246/246、evidence 字节比较、audit/commit/push、立即停止。禁止 preliminary complete runner；任一门失败不得修正后重跑。
147. 当前状态为 `AMENDMENT_5G_A_1_AWAITING_APPROVAL`。在新的明确批准前，测试名、runner、synthetic、official execution 和 5G-B 全部锁定。
148. Amendment 5G-A.1 已获 package-bound minimal-repair/synthetic-retry 批准，严格绑定 package commit `d02b19dfd5a527d0159b930662f5a868c8235d35` 及批准决定登记的历史提交。批准决定为 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_1_APPROVAL_DECISION.md`。
149. 只允许对新 execution-head test module 做两个函数名 token 替换，并对 runner 同步两个 suffix、移除重复通用 suffix、增加 pre-discovery tuple 唯一性门和精确 246/41/44 计数门。Helper 与其他文件不得修改。
150. 批准治理推送后，必须先完成精确两文件修复，再运行一次 source-only inventory 和一次 41/41 定向测试；全部通过后才允许运行两次最终 246/246。禁止 preliminary complete runner，任一失败立即停止且不得第三次运行。
151. 两次最终 runner 必须使用完全相同 tracked bytes，第一轮写唯一 OS-temp、第二轮写正式 evidence；只有两轮全门通过且 evidence 字节一致后才可删除第一轮临时文件。
152. 当前状态为 `AMENDMENT_5G_A_1_APPROVED_AWAITING_MINIMAL_REPAIR`。本批准不授权 real execution-head check、preflight、official input、token、capture、controller、verifier、Gold 或 5G-B。
153. 5G-A.1 精确两文件修复已完成；source-only inventory 唯一一次通过，扫描 6 个测试文件、246 个 test definitions，135/135 required suffix 精确唯一，测试 import/execution 为 0。Execution-head 定向测试唯一一次运行通过 41/41、零 failure/error/skip。
154. 最终 tracked bytes 自本条起冻结。仅当后续两次 complete runner 均精确 246/246、41 execution-head、44 typed-policy、全部访问/调用计数为 0，且 tracked digest 与 evidence bytes 完全一致时，状态才可记为 `AMENDMENT_5G_A_1_SYNTHETICALLY_VERIFIED`；否则必须记录新的 Hard Failure。
155. 正式 evidence `results/stage4b_u1_d_pregold_amendment_5g_a_synthetic_verification.json` 与 recovery audit 是最终状态 authority。Evidence 提交推送后必须停止等待独立审核，不得组装 5G-B。
156. 5G-A.1 implementation/evidence 独立审核已接受提交 `c21f3f58b2b1d4ccf235daba9c85937daedf4e3b`，当前只授权组装并推送 5G-B Request/Manifest，不授权运行其中任何步骤。
157. 5G-B package 必须冻结：未来 approval governance 只改 `AGENTS.md` 与 5G-B approval decision；其唯一 rebinding/governance direct-child 只新增 Manifest 登记的三项 evidence/binding/audit，且该提交的直接 parent 必须是 approval governance commit。
158. Future execution HEAD 禁止预先手抄字面量。只有 package-bound 批准、两轮 246/246 post-approval rebinding 及三路径 direct-child 提交推送后，才能从实际 local/origin/GitHub HEAD、parent、changed paths、ancestors、clean worktree 与 committed governance binding 推导，并通过冻结 helper 单次验证。
159. 只有 derived execution-HEAD validation 通过后才可依次运行一次 A/B/C/D formal preflight；只有全部门通过后才可运行一次 Manifest 中完全不变的 32-element decisions-only capture。任一失败立即停止，不得重试。
160. 当前状态为 `AMENDMENT_5G_B_AWAITING_APPROVAL`。新的 package-bound 批准前，post-approval rebinding、real execution-head check、preflight、helper official call、official input、token、capture、controller、verifier 与 Gold 全部锁定。
161. Amendment 5G-B 已获 package-bound 批准，严格绑定 package commit `f281864b424c406b42718c4ec58d7266ecafd9a3`、Request/Manifest 及批准决定登记的历史提交。批准决定为 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_APPROVAL_DECISION.md`。
162. 本 approval-governance commit 只允许修改 `AGENTS.md` 并新增 5G-B approval decision；推送并确认 local/origin/GitHub 三方一致前不得运行 synthetic、helper、preflight、official input、token 或 capture。
163. 推送确认后只允许运行恰好两次最终 246/246 complete runner；不得 preliminary、targeted、修复性或第三次运行。两轮必须 41 execution-head、44 typed-policy、全部访问/调用计数为 0、tracked bytes 与 evidence bytes 完全一致。
164. 两轮通过后只允许一个 approval-governance 的直接子提交，且 changed paths 精确为 Manifest 登记的 rebinding evidence、governance binding 与 narrative audit 三项。该提交推送同步后才可单次 derived execution-HEAD validation。
165. Derived HEAD helper、formal preflight、typed helper、path helper 与 capture 均为一次性授权；任一 gate 失败立即消耗授权并停止，不得现场修改或重试。只有 derived HEAD 与 A/B/C/D 全通过后才可运行一次 unchanged decisions-only capture。
166. 成功后的最终诊断提交只允许 machine audit 与 5G-B narrative audit 两个路径；不得同时更新治理状态文件。提交推送并确认 GitHub 后立即停止，controller、verifier 与 Gold 继续锁定。
167. 5G-B approval-governance commit `79e69eab874f669d79d433fa965f5f5f48659332` 已按精确两路径提交推送，local/origin/GitHub 三方一致后才开始 post-approval synthetic。
168. 两次获批 complete runner 均精确通过 246/246、41 execution-head、44 typed-policy，33 个 tracked files digest 为 `50D3BCDD...`，两份 69,144-byte evidence SHA 均为 `00281BED...` 且逐字节一致；run-1 临时文件仅在全部比较通过后删除。
169. 三路径提交前 governance validation 在 `bound file count failed` 处触发 Hard Failure 10。直接原因是 PowerShell 对 `$g.bound_files.psobject.Properties.Count` 进行成员枚举并返回 11 个 `1`，而非集合 cardinality 11；实际 bound-file property 数为 11。
170. 失败后未修正或重跑 validation，未创建获批三路径 direct-child，也未运行 derived execution-HEAD helper、preflight、official input、token 或 capture。已生成的 rebinding evidence、governance binding 与 narrative audit 原样保留。
171. 当前状态为 `AMENDMENT_5G_B_REBINDING_GOVERNANCE_STOPPED_HARD_FAILURE_10`。现有 5G-B 授权已消耗；任何 direct-child recovery、helper、preflight 或 official action 必须经过新的独立审核与 package-bound Amendment。
172. Hard Failure 10 独立审核已接受审计并冻结 checkpoint `aab591b92804fd1226a62751c38d056918f71b41`；旧两轮 `00281BED...` evidence 仅作为历史失败证据，不得作为新的 execution binding。
173. 旧 5G-B rebinding audit、governance binding 与 synthetic evidence 必须保持原 SHA，禁止覆盖、修改、删除、迁移、重提或通过 reset/force-push 制造旧 approval 的三路径 direct-child。
174. 当前只授权组装 5G-B.1 package。Request/Manifest 本身不授权 validator 修正或执行、semantics check、synthetic、fresh direct-child、helper、preflight、official input、token、capture、controller、verifier 或 Gold。
175. 未来 5G-B.1 如获 package-bound 批准，validator 必须用 `@(...)` 显式物化 actual/expected key arrays，分别拒绝重复，并以 `Compare-Object` 零 delta 验证 exact key set；只比较 cardinality 不得接受。
176. 未来恢复顺序必须隔离为：新 approval governance、一次纯内存 semantics check、两次 fresh 246/246、三项新工件、一次 corrected real precommit validation、精确三路径 direct-child、同步 GitHub、立即停止。任一失败不得修正或重跑。
177. 当前状态为 `AMENDMENT_5G_B_1_AWAITING_APPROVAL`。本阶段不申请 derived execution-HEAD helper、formal preflight 或 official diagnostic；这些必须等待 fresh direct-child 独立审核后另行组包。

## GitHub 与文档

- 协议/代码提交必须先于数据提取和指标读取。
- 结果提交必须包含独立验证、Roadmap 和 README 状态更新。
- 不提交 raw/processed 数据、embedding、模型缓存或本地临时文件。
- README 保持当前状态；完整历史由 `docs/ROADMAP.md`、`docs/*PROTOCOL*` 和 `reports/` 承载。
