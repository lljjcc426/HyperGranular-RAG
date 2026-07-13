# Stage4B-U1-D v2.2 Dual-ID Formal Preflight 审计

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-13
- Mode: run / read-only formal preflight
- Approval decision: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_2_APPROVAL_DECISION.md`
- Execution count: `1`
- Verification Status: `PASS_DUAL_ID_FORMAL_PREFLIGHT`
- HEAD and origin/main: `10ed570fae9528ffbf02efbe7ede9916044ef1f4`
- Gold metrics read or computed: No
- Reservation accessed: No
- Stage3B accessed: No

## 硬门结果

| 硬门 | 结果 |
|---|---|
| `HEAD == origin/main` | 通过，均为 `10ed570fae9528ffbf02efbe7ede9916044ef1f4` |
| 工作树干净 | 通过 |
| v2.2 implementation 相对 `ca2cca332292f7bd6af12e2a429100be11da5549` 无漂移 | 通过 |
| official units | 通过，143,820 行且 `unit_id` 唯一 |
| official queries | 通过，4,500 行，`sample_id` 与 `query_id` 均唯一 |
| dataset | 通过，仅 `2wikimultihopqa` |
| 逐条 namespace 关系 | 通过，`query_id == dataset::sample_id` |
| sample-ID SHA-256 | `6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2` |
| runtime query-ID SHA-256 | `8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6` |
| source-audit SHA-256 | `1496FF0CE08093AD38258FD5049068D6C4ED74FCEBF63E94E6E486F3478C7AEE` |
| legacy cache SHA-256 | `746FC1130038C789190F2A37CB911BBFC46905CFCC138E361C1F6CF991A45F02` |
| fresh cache 与拟生成路径 | 通过，10 个路径全部不存在 |
| synthetic rebinding evidence SHA-256 | `9B01C80F66096F01C763C25E44E4D079C40B681F6C52F0CC55F70492689EAAB1` |

该 preflight 只读取身份边界、文件 hash、计数与路径存在性。没有生成 channel、cache、decision、ranking、policy 或指标；没有读取或计算 Gold 评价结果。
