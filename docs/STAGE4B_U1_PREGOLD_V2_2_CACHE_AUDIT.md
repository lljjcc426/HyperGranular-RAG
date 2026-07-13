# Stage4B-U1-D v2.2 Fresh ID-Bound Cache 独立核查

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-13
- Mode: validate / independent read-only cache audit
- Execution count: `1`
- Verification Status: `PASS_INDEPENDENT_ID_BOUND_CACHE_AUDIT`
- Cache path: `E:\科研\超粒球RAG_数据\processed\stage4b_u1_d_official_dev4500_minilm_idbound_embeddings.npz`
- Gold or metrics accessed: No
- Reservation accessed: No
- Stage3B accessed: No

## 核查结果

| 项目 | 结果 |
|---|---|
| NPZ 成员 | `unit_embeddings`、`query_embeddings`、`unit_ids`、`query_ids`、`model_name`、`max_length`，无缺失或额外成员 |
| unit IDs | 与 143,820 个 controller-channel units 精确同序 |
| query IDs | 与 4,500 个 controller-channel queries 精确同序 |
| 逐条 namespace 关系 | 通过 |
| sample-ID SHA-256 | `6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2` |
| runtime query-ID SHA-256 | `8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6` |
| model / max length | `sentence-transformers/all-MiniLM-L6-v2` / `192` |
| unit embeddings | `(143820, 384)`，`float32`，220,907,520 bytes，全有限，最大单位范数误差 `1.1920928955078125e-07` |
| query embeddings | `(4500, 384)`，`float32`，6,912,000 bytes，全有限，最大单位范数误差 `1.1920928955078125e-07` |
| cache file bytes | `210,714,667` |
| fresh cache SHA-256 | `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D` |
| legacy cache SHA-256 | `746FC1130038C789190F2A37CB911BBFC46905CFCC138E361C1F6CF991A45F02`，保持不变 |

核查为独立只读脚本，不调用 controller 的 cache loader，不写入或修改两个 cache。fresh cache 保留在登记的本地数据目录，不提交 Git。
