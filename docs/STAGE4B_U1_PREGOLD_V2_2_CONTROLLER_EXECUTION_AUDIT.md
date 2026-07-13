# Stage4B-U1-D v2.2 Gold-Free Controller 执行审计

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-13
- Mode: run / official development pre-Gold
- Approval decision: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_2_APPROVAL_DECISION.md`
- Formal preflight: `PASS_DUAL_ID_FORMAL_PREFLIGHT`
- Channel preparation count: `1`
- Controller execution count: `1`
- Controller start: `2026-07-13T14:22:03.3670736+08:00`
- Controller finish: `2026-07-13T14:37:17.3450870+08:00`
- Policy Status: `POLICY_FROZEN_BEFORE_EVALUATION`
- Evaluation labels loaded: No
- Retrieval metrics computed by channel: No
- Gold evaluation: Not run
- Reservation accessed: No
- Stage3B accessed: No

## 冻结配置与边界

- queries / units: `4,500 / 143,820`
- encoder: `sentence-transformers/all-MiniLM-L6-v2`
- max length / batch size: `192 / 64`
- sample-ID SHA-256: `6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2`
- runtime query-ID SHA-256: `8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6`
- policy-bound commit: `10ed570fae9528ffbf02efbe7ede9916044ef1f4`

## 工件绑定

| 工件 | SHA-256 |
|---|---|
| controller channel audit | `A463AE50A2EF8F8E4ED1AA74727E559088739BA0560D96016F2C0FE559A3C515` |
| unlabeled units（本地，不提交） | `114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA` |
| unlabeled queries（本地，不提交） | `6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B` |
| fresh ID-bound cache（本地，不提交） | `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D` |
| decisions，4,500 行 | `6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7` |
| rankings，4,500 行 | `ED289D234F6F4FEC58A48168CB6CA78950489CD5F5640E977068CA6A786E03CB` |
| policy | `829E8A0DB7E4108C4D23F2D0CE3DD0C227F329E9EDF77BB4ED49C20544EC07DC` |
| evaluator audit（本地，不提交） | `A148C94A2B49A92D3D2C6C26CCC5515EA98AAECBFBD76C1ADD61638994E672CC` |
| Gold map（本地，不提交、不评估） | `76D15A88C218C9EDF36A9F9F52B0D2D9877463E5653EC8AB1E5C94542E99B30B` |

提交前结构检查确认：policy 的输入、输出、实现和协议 hash 全部匹配；decision/ranking query-ID 集合一致；controller 禁止字段不存在；`evaluation_labels_loaded=false`。本审计不解释 score、allocation、ranking 或任何 U1-D 效果。
