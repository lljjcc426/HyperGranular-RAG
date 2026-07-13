# Stage4B-U1-D v2.3.1 Channel Preparation 审计

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-13
- Mode: run / exact-path official channel preparation
- Execution count: `1`
- Verification Status: `PASS_V2_3_1_CHANNEL_PREPARATION_AUDIT`
- Execution HEAD: `8e0bab13ad20c06795dffd5ca71f167a814cdfb0`
- Evaluator executed: No
- Retrieval/Gold metrics read or computed: No
- Reservation accessed: No
- Stage3B accessed: No

## 执行边界

唯一一次 `scripts/stage4b_u1_prepare_channels.py` 使用冻结 official units、queries 和 `docs/STAGE4A_R2_SOURCE_AUDIT.json`，以 `--mode development` 写入 manifest 登记的五个 v2.3.1 channel 路径。未传 `--synthetic-test-mode`，未运行 evaluator。

## 独立核验

| 项目 | 结果 |
|---|---|
| queries / units | 4,500 / 143,820 |
| sample-ID SHA-256 | `6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2` |
| runtime query-ID SHA-256 | `8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6` |
| namespace | 逐条 `query_id == dataset::sample_id` |
| unlabeled units SHA-256 | `114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA` |
| unlabeled queries SHA-256 | `6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B` |
| v2.2 bytes equivalence | units 与 queries 均通过 |
| controller channel audit SHA-256 | `D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA` |
| evaluator Gold map SHA-256 | `76D15A88C218C9EDF36A9F9F52B0D2D9877463E5653EC8AB1E5C94542E99B30B` |
| evaluator audit SHA-256 | `220FD7310AA187840A5E9D95174EBAF5BD4BDF6097BC58BACD28413D85377C17` |
| controller prohibited keys | 全部不存在 |
| retrieval metrics computed | `false` |
| fresh cache SHA after channel | `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D` |
| 后续五个正式路径 | controller 前全部不存在 |

Gold map 只写入 evaluator channel 路径，没有传给 controller、policy 或 verifier。独立核验只读取 controller channel 与 evaluator audit/hash，不计算 Gold 指标。

## 文件记录

本次新增以下登记文件：

- `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_units.jsonl`
- `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_unlabeled_queries.jsonl`
- `E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_v2_3_1_controller_channel_audit.json`
- `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_gold_map.json`
- `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_v2_3_1_evaluator_channel_audit.json`

没有覆盖、删除或改写 v2.2 channel、失败工件、fresh/legacy cache 或其他文件。
