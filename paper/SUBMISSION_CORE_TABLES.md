# Stage5-PMC Submission Core Tables

状态：`DERIVED_FROM_FROZEN_STAGE4E_I_EVIDENCE`

本文件只重排已冻结结果，不新增 bootstrap、显著性检验或科学判定。区间均为对应阶段冻结的 95% query-bootstrap interval；“等权”表示 HotpotQA/MuSiQue 数据集等权，而不是 query 数加权。

## Table 1. Main answer-quality results over the compact MiniLM dense backbone

| Boundary / generator | Queries | Dense F1 | Full/static-q25 F1 | Paired ΔF1 [95% CI] | Dense EM | Full EM | Frozen interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| HotpotQA / Qwen (Stage4E) | 1,000 | 0.42150 | 0.43628 | +0.01478 [0.00020, 0.02988] | 0.35600 | 0.36600 | Supported; lower bound near zero |
| MuSiQue / Qwen (Stage4F) | 3,000 | 0.13595 | 0.14735 | +0.01140 [0.00450, 0.01835] | 0.10033 | 0.11033 | Supported cross-dataset replication |
| HotpotQA new boundary / Qwen (Stage4H) | 1,000 | 0.45585 | 0.47654 | +0.02070 [0.00570, 0.03565] | 0.39600 | 0.41200 | Dataset component of supported equal-weight comparison |
| MuSiQue new boundary / Qwen (Stage4H) | 1,500 | 0.15307 | 0.15951 | +0.00644 [-0.00301, 0.01568] | 0.11333 | 0.11600 | Dataset interval crosses zero |
| Stage4H dataset equal-weight | 2,500 | — | — | +0.01357 [0.00491, 0.02233] | — | — | `FULL_METHOD_VS_DENSE_SUPPORTED` |

Source:

- `results/stage4e_e2e_official_train1000_v1_evaluation_summary.json`
- `results/stage4f_xdr_musique_train3000_v1_evaluation_summary.json`
- `results/stage4h_cbe_hotpot1000_musique1500_v1_dataset_summaries.json`
- `results/stage4h_cbe_hotpot1000_musique1500_v1_equal_weight_summary.json`

Interpretation boundary: these are closed-candidate evaluations. They do not establish full-wiki/open-domain efficacy, universal generator robustness, or superiority over strong dense retrieval.

## Table 2. External robustness and strong-dense boundary

| Evaluation | Contrast | Paired ΔF1 [95% CI] | Frozen interpretation |
|---|---|---:|---|
| Gemma mobile-QAT / HotpotQA | Static q25 − MiniLM Dense | +0.01265 [-0.00220, 0.02744] | Dataset interval crosses zero |
| Gemma mobile-QAT / MuSiQue | Static q25 − MiniLM Dense | -0.00232 [-0.00685, 0.00208] | Dataset interval crosses zero |
| Gemma mobile-QAT / dataset equal-weight | Static q25 − MiniLM Dense | +0.00516 [-0.00262, 0.01295] | `GENERATOR_TRANSFER_INCONCLUSIVE` |
| Qwen / Stage4H equal-weight | Full − BGE strong dense | -0.03998 [-0.05393, -0.02621] | `FULL_METHOD_VS_STRONG_DENSE_NEGATIVE` |
| Qwen / Stage4I equal-weight | Protected HGRAG sidecar − BGE | -0.00256 [-0.00998, 0.00458] | `STRONG_DENSE_COMPLEMENTARITY_INCONCLUSIVE` |
| Qwen / Stage4I equal-weight | Unprotected HGRAG sidecar − BGE | -0.01379 [-0.02440, -0.00339] | Supporting placement evidence, not a separate advancement claim |

Stage4I absolute answer F1:

| Dataset | BGE | Protected | Unprotected | No-facet sidecar |
|---|---:|---:|---:|---:|
| HotpotQA | 0.51952 | 0.51655 | 0.50723 | 0.52370 |
| MuSiQue | 0.16650 | 0.16435 | 0.15122 | 0.17206 |

Source:

- `results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_dataset_summaries.json`
- `results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_equal_weight_summary.json`
- `results/stage4h_cbe_hotpot1000_musique1500_v1_equal_weight_summary.json`
- `results/stage4i_sdc_hotpot1000_musique1500_v1_dataset_summaries.json`
- `results/stage4i_sdc_hotpot1000_musique1500_v1_equal_weight_summary.json`

Gemma 使用官方 mobile-QAT 格式；该表不能解释为纯基础模型架构比较、普遍 RAG 适用性判断或跨设备效率排名。

## Table 3. Component and placement evidence

| Boundary | Contrast | Paired ΔF1 [95% CI] | Evidence class | Permitted conclusion |
|---|---|---:|---|---|
| Stage4H MiniLM system | Full − NoFacet | +0.01336 [0.00341, 0.02343] | Supported | Facet-hyperedge has incremental value within the frozen system |
| Stage4H MiniLM system | Full − NoProtection | +0.00354 [-0.00675, 0.01389] | Inconclusive | Independent protection contribution remains uncertain |
| Stage4H MiniLM system | Granular ball − flat unit | Not defined | `NOT_FAIRLY_DEFINED` | No independent granular-ball claim |
| Stage4I BGE sidecar | Protected − Unprotected | +0.01122 [0.00129, 0.02104] | Supported | Protected placement is better for the identical inserted set |
| Stage4I BGE sidecar | Protected − NoFacet | -0.00743 [-0.01616, 0.00132] | Inconclusive | Facet increment on BGE sidecar remains uncertain |

Placement support does not imply that Protected sidecar outperforms BGE. The advancement comparison remains Protected−BGE and is inconclusive.

Source:

- `results/stage4h_cbe_hotpot1000_musique1500_v1_equal_weight_summary.json`
- `results/stage4h_cbe_hotpot1000_musique1500_v1_scientific_decision.json`
- `results/stage4i_sdc_hotpot1000_musique1500_v1_equal_weight_summary.json`
- `results/stage4i_sdc_hotpot1000_musique1500_v1_scientific_decision.json`

## Table 4. Efficiency and integrity

| Stage | Queries × methods | Generation calls | Failed calls | Main wall time | GPU peak memory | Determinism contract |
|---|---:|---:|---:|---:|---:|---|
| Stage4E | 1,000 × 2 | 2,000 | 0 | 854.83 s | 3.51 GB | Full main/rerun byte identity |
| Stage4F | 3,000 × 2 | 6,000 | 0 | 1,947.37 s | 4.27 GB | Full main/rerun byte identity |
| Stage4G | 4,000 × 2 | 8,000 | 0 | 56,501.84 s | 7.89 GB | 400-call pre-hash subset exact |
| Stage4H | 2,500 × 7 | 17,500 | 0 | 6,265.00 s | 4.17 GB | 1,400-call pre-hash subset exact |
| Stage4I | 2,500 × 4 | 10,000 | 0 | 4,999.07 s | 4.36 GB | 800-call pre-hash subset exact |

Context and insertion cost for the two primary compact-dense replications:

| Boundary | Mean inserted units/query | Dense mean input tokens | Static-q25 mean input tokens |
|---|---:|---:|---:|
| Stage4E HotpotQA | 1.930 | 899.19 | 901.04 |
| Stage4F MuSiQue | 2.411 | 880.61 | 884.09 |

Source:

- `results/stage4e_e2e_official_train1000_v1_telemetry_main.json`
- `results/stage4f_xdr_musique_train3000_v1_telemetry_main.json`
- `results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_telemetry_main.json`
- `results/stage4h_cbe_hotpot1000_musique1500_v1_telemetry_main.json`
- `results/stage4i_sdc_hotpot1000_musique1500_v1_telemetry_main.json`
- corresponding frozen Stage4E/4F reports for insertion and token summaries.

Wall time and GPU memory are observed within each frozen runtime transaction. Because model format, method count and transaction structure differ, the table does not support a pure architecture or universal hardware-efficiency ranking.
