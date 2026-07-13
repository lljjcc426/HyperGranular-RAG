# Stage4B-U1-D v2.3.1 Formal Preflight 审计

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-13
- Mode: run / independent read-only formal preflight
- Execution count: `1`
- Verification Status: `PASS_V2_3_1_FORMAL_PREFLIGHT`
- Request-package commit: `e76c921454697d1784b0d76a9d9677113051f0f6`
- Implementation commit: `34349c70ee24b8240fd169393134d4280968b790`
- Approval-governance commit: `53850f58e57f51b3c6067ed3108edff6b99a2dfc`
- Rebinding-evidence commit / execution HEAD: `a963befd812658972b156d2a7a26a488ac3c4482`
- Gold metrics read or computed: No
- Reservation accessed: No
- Stage3B accessed: No

## Git 与 Rebinding 门

| 硬门 | 结果 |
|---|---|
| `HEAD == origin/main == GitHub main` | 通过，`a963befd812658972b156d2a7a26a488ac3c4482` |
| 工作树干净 | 通过 |
| 四个绑定提交存在且为 `main` 祖先 | 通过 |
| Rebinding evidence 已提交 | 通过 |
| Rebinding evidence SHA-256 | `9D40C0B9B0C8F03CBC5545CA8F2390CCE9EABDC3B08B041B092FB3A76492FF34` |
| 22 个 implementation hashes | 全部通过 |
| 3 个 dynamic governance hashes | 全部通过 |

## Official 身份边界

| 硬门 | 结果 |
|---|---|
| official queries | 4,500，`query_id` 与 `sample_id` 分别唯一 |
| official units | 143,820，`unit_id` 唯一 |
| dataset | 仅 `2wikimultihopqa` |
| namespace | 逐条 `query_id == dataset::sample_id` |
| sample-ID SHA-256 | `6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2` |
| runtime query-ID SHA-256 | `8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6` |
| source-audit SHA-256 | `1496FF0CE08093AD38258FD5049068D6C4ED74FCEBF63E94E6E486F3478C7AEE` |
| source units SHA-256 | `B6989F94BB8393C427F559B6CC9C0F916B812EBCC14F0C5F47EB0209B620D9B4` |
| source queries SHA-256 | `117976A1987EA89018490A306385FF17B47AC4ADCA675DA2ECC242AA98FC8C89` |

核验只提取 identity fields、计数和 hash，没有计算 retrieval/Gold 指标。

## Cache 硬门

| 硬门 | 结果 |
|---|---|
| fresh cache regular file | 通过 |
| fresh cache bytes | `210714667` |
| fresh cache SHA before | `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D` |
| fresh cache SHA after | `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D` |
| exact members | `unit_embeddings`、`query_embeddings`、`unit_ids`、`query_ids`、`model_name`、`max_length` |
| unit/query ID order | 与 official source 精确同序 |
| model / max length | `sentence-transformers/all-MiniLM-L6-v2` / `192` |
| unit embeddings | `(143820, 384)` / `float32` / 全有限 |
| query embeddings | `(4500, 384)` / `float32` / 全有限 |
| unit max norm error | `1.1920928955078125e-07` |
| query max norm error | `1.1920928955078125e-07` |
| legacy cache SHA-256 | `746FC1130038C789190F2A37CB911BBFC46905CFCC138E361C1F6CF991A45F02` |

Preflight 以只读 `np.load(..., allow_pickle=False)` 独立核验 cache，没有调用 controller、模型加载、编码、`mkdir` 或 cache 写入路径。

## v2.2 等价门与十路径

| 硬门 | 结果 |
|---|---|
| v2.2 decisions SHA-256 | `6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7` |
| v2.2 rankings SHA-256 | `ED289D234F6F4FEC58A48168CB6CA78950489CD5F5640E977068CA6A786E03CB` |
| reference policy SHA-256 | `829E8A0DB7E4108C4D23F2D0CE3DD0C227F329E9EDF77BB4ED49C20544EC07DC` |
| manifest registry | 10 个唯一绝对路径 |
| 正式路径碰撞 | 0；十个路径全部不存在 |

## 结论与停止边界

唯一一次 v2.3.1 formal preflight 全部门通过。允许按 manifest 准确路径运行一次 versioned channel preparation。该结论不授权 evaluator、Gold evaluation、U1-D 指标、reservation、Stage3B、cache 写入、实现/参数变更或自动重跑。

本阶段只新增本 audit 并更新 README、Roadmap 与复现状态；没有删除文件，没有修改 official 文件、cache、v2.2 失败工件、治理绑定或实现文件。
