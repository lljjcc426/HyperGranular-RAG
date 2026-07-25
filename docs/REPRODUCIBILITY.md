# Reproducibility

本文件只保留当前有效的复现入口。完整历史命令与旧治理链快照见 [归档版本](archive/REPRODUCIBILITY_PRE_REORGANIZATION_2026-07-18.md)。

## 当前 Stage5R-PMR 边界

Stage4E–Stage5A 科学实验线已完成、独立验证并冻结。Stage5R-PMR 只整理论文，不重跑 retrieval、generation、Gold evaluation、bootstrap 或 scientific decision。论文图由 `scripts/stage5r_build_materials.py` 使用 Python/Matplotlib 从 20 个 SHA-verified frozen JSON 工件派生；11 个 CSV source-data、五组 SVG/PDF/600-dpi TIFF/PNG 和完整 Bytes/SHA manifest 位于 `paper/figures_stage5r/`。原 `paper/figures/` Stage5-PMC 图和 source-data 保持不变。

当前状态：

```text
STAGE4I_CLOSED_AND_FROZEN
STAGE5A_BNH_COMPLETE_AND_FROZEN
BGE_NATIVE_HGRAG_INCONCLUSIVE
CORE_ALGORITHM_EXPERIMENTS_CLOSED
STAGE5R_PMR_COMPLETE
CURRENT_EVIDENCE_MANUSCRIPT_COMPLETE
VERIFIED_LITERATURE_CORPUS_COMPLETE
FIGURE_AND_TABLE_AUDIT_PASS
CLAIM_AND_CITATION_AUDIT_PASS
SUBMISSION_METADATA_PENDING
FULL_WIKI_NOT_AUTHORIZED
RESERVATION_LOCKED
STAGE3B_LOCKED
U2_NOT_AUTHORIZED
```

Stage5R 的可复现入口是 [英文核心稿](../paper/MANUSCRIPT_CORE_DRAFT_STAGE5R.md)、[核心表](../paper/STAGE5R_CORE_TABLES.md)、[图形合同](../paper/figures_stage5r/FIGURE_CONTRACTS_AND_CAPTIONS.md)、[figure manifest](../paper/figures_stage5r/STAGE5R_FIGURE_MANIFEST.json) 和 [联合审计](../paper/STAGE5R_PRE_SUBMISSION_AUDIT.md)。所有 Stage4E–Stage5A 正式工件保持只读。

```powershell
python scripts\stage5r_build_materials.py
python scripts\stage5r_build_materials.py
python scripts\stage5r_verify_materials.py
```

前两条命令分别先验证 20 个 frozen source SHA，再派生图、表与 CSV。连续两次构建的 manifest SHA 均为 `EFCED94CC12FDDA26360AE958E40EE1C7C2D88FC4B5853CC63B27DCD91ED246A`，33 个 derived-file SHA 全部相同。第三条命令只读核对 source/derived Bytes/SHA、CSV 数值、五张表、23 个 BibTeX 条目、citation keys、主张边界、SVG editable text、本地链接、license 状态和旧 Stage5-PMC verifier；当前结果为 `STAGE5R_PMR_MATERIALS_VERIFIED`。

### Stage5A 与 Stage5R 关键身份

| 工件 | Bytes | SHA-256 |
|---|---:|---|
| `results/stage5a_bnh_evidence_ledger.json` | 7,858 | `9D97B4100C9BCD31E421595EC18BA2C7318D9E6709AE9106446388C9CA63ABE4` |
| `results/stage5a_bnh_confirmation_equal_weight_summary.json` | tracked manifest | `D38608EB73FF1A7741A6EBE2DE2E08B0F7FC7D0305067F6FE7D60F8B8C83983F` |
| `results/stage5a_bnh_confirmation_dataset_summaries.json` | tracked manifest | `F4893C526AC45C5622A93B44BDCFAA50A484C896F4F7984AF0E4150F79763546` |
| `results/stage5a_bnh_confirmation_mechanism_audit.json` | tracked manifest | `0AEEA7C41680E10A417E036CD1C6DC2D86BF60BAAD337218AE07F6DE697027F1` |
| `results/stage5a_bnh_final_verification.json` | tracked manifest | `145B51FB194BA0DE5B00D294FE4D8F8EAC9FD9D2E7C1F39F741D7AFEDDF0BA09` |
| `paper/figures_stage5r/STAGE5R_FIGURE_MANIFEST.json` | derived | `EFCED94CC12FDDA26360AE958E40EE1C7C2D88FC4B5853CC63B27DCD91ED246A` |

Bytes 标记为 `tracked manifest` 的 Stage5A 项由 `results/stage5a_bnh_artifact_manifest.json` 与 Stage5R verifier 双重核对；这里不复制可能随展示方式产生歧义的长度。Stage5R manifest 的 derived 长度由自身清单逐文件绑定。

## 文件系统迁移

自 2026-07-19 起，项目根目录由 `E:\科研` 迁移为 `E:\SCIENCE`；当前仓库和登记数据目录分别为 `E:\SCIENCE\HyperGranular-RAG` 与 `E:\SCIENCE\超粒球RAG_数据`。冻结配置、协议、审计清单、归档快照和既有实验报告中的 `E:\科研` 是执行时路径记录，并参与既有 SHA/证据绑定，因此保留原字节；读取这些历史记录时按 `E:\科研` → `E:\SCIENCE` 映射定位现有文件，不据此重新运行已经完成或锁定的实验。

## 当前复现状态

```text
VERIFIED_POST_GOLD
STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED
STAGE4C_U1_FMA_COMPLETED
MECHANISM_EVIDENCE_INCONCLUSIVE
STAGE4D_LEVEL_A_PROTOCOL_ACCEPTED
STAGE4D_IMPLEMENTATION_READY
STAGE4D_SYNTHETIC_TESTS_PASSED
STAGE4D_CHANNEL_A_VERIFIED
STAGE4D_CHANNEL_B_LABELS_VERIFIED
EXISTING_OFFICIAL_PROBE_ARTIFACTS_PROVENANCE_VERIFIED
STAGE4D_PROBE_VERIFIED
STAGE4D_FINAL_VERIFICATION_PASSED
CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE
STAGE4D_CMA_CLOSED
CURRENT_CONTROLLER_BRANCH_FROZEN_CLOSED
STAGE4E_LEVEL_A_PROTOCOL_ACCEPTED
STAGE4E_INPUT_BINDING_AUTHORIZED
STAGE4E_LEVEL_B_IMPLEMENTATION_AUTHORIZED
STAGE4E_INPUTS_BOUND
STAGE4E_LEVEL_B_IMPLEMENTATION_READY
STAGE4E_SYNTHETIC_TESTS_PASSED
STAGE4E_INPUT_CHANNELS_VERIFIED
STAGE4E_GENERATOR_SELECTION_VERIFIED
STAGE4E_GENERATOR_QWEN_SELECTED
STAGE4E_PRE_GOLD_ARTIFACTS_VERIFIED
STAGE4E_GOLD_EVALUATION_COMPLETED
STAGE4E_FINAL_VERIFICATION_PASS
STATIC_HGRAG_E2E_SUPPORTED
STAGE4F_XDR_EXPERIMENT_CARD_FROZEN
STAGE4F_SOURCE_BOUND
STAGE4F_INPUT_BOUNDARY_VERIFIED
STAGE4F_MODEL_ENVIRONMENT_BOUND
STAGE4F_LEVEL_B_IMPLEMENTATION_READY
STAGE4F_SYNTHETIC_TESTS_PASSED
STAGE4F_PRE_GOLD_ARTIFACTS_VERIFIED
STAGE4F_GOLD_EVALUATION_COMPLETED
STAGE4F_FINAL_VERIFICATION_PASS
STAGE4F_DESCRIPTIVE_SUBGROUPS_FROZEN
STATIC_HGRAG_XDR_SUPPORTED
STAGE4G_GTR_EXPERIMENT_CARD_FROZEN
STAGE4G_GTR_INPUT_MODEL_BINDING_VERIFIED
STAGE4G_GTR_MAIN_COMPLETE
STAGE4G_GTR_PRE_GOLD_VERIFIED
STAGE4G_GTR_GOLD_EVALUATION_COMPLETE
STAGE4G_GTR_FINAL_VERIFICATION_PASS
STAGE4G_GTR_ARTIFACT_MANIFEST_FROZEN
GENERATOR_TRANSFER_INCONCLUSIVE
STAGE4H_CBE_EXPERIMENT_CARD_FROZEN
STAGE4H_PRE_GOLD_VERIFICATION_PASS
STAGE4H_GOLD_EVALUATION_COMPLETE
STAGE4H_FINAL_VERIFICATION_PASS
FULL_METHOD_VS_DENSE_SUPPORTED
FULL_METHOD_VS_STRONG_DENSE_NEGATIVE
PROTECTED_INSERTION_ABLATION_INCONCLUSIVE
FACET_HYPEREDGE_ABLATION_SUPPORTED
GRANULAR_BALL_ABLATION_NOT_FAIRLY_DEFINED
STAGE4I_FINAL_VERIFICATION_PASS
STRONG_DENSE_COMPLEMENTARITY_INCONCLUSIVE
PROTECTED_PLACEMENT_SUPPORTED
BGE_FACET_INCREMENT_INCONCLUSIVE
STAGE5A_FINAL_INDEPENDENT_VERIFICATION_PASS
BGE_NATIVE_HGRAG_INCONCLUSIVE
BGE_NATIVE_PROTECTED_PLACEMENT_INCONCLUSIVE
BGE_NATIVE_FACET_INCREMENT_INCONCLUSIVE
CORE_ALGORITHM_EXPERIMENTS_CLOSED
STAGE5R_PMR_COMPLETE
CURRENT_EVIDENCE_MANUSCRIPT_COMPLETE
VERIFIED_LITERATURE_CORPUS_COMPLETE
FIGURE_AND_TABLE_AUDIT_PASS
CLAIM_AND_CITATION_AUDIT_PASS
SUBMISSION_METADATA_PENDING
RESERVATION_REQUIRES_PAUSE
U2_NOT_AUTHORIZED
```

Pre-Gold 和本次获授权的 Gold evaluation 均已完成，不应重复运行。主运行与预注册复跑同字节，独立验证器已重建 4,500 条逐查询审计、汇总和 development 决策。

Stage4C-U1-FMA 也已完成一次冻结的 post-Gold exploratory diagnosis。它不是新的 Gold evaluation，不改变 Stage4B 负结果，也不授权 U2 或 reservation。

Stage4D-CMA 已在获授权边界内完成 Gold-free Channel A、development-Gold Channel B、固定 official probe、独立验证和 bounded provenance audit。唯一 advancement panel 未通过全部联合门，冻结结论为 `CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE`。现有工件不得覆盖或重跑；reservation、Stage3B 与 U2 仍未授权。

Stage4D 和当前 controller 分支已按 [STAGE4D_CMA_CLOSURE](STAGE4D_CMA_CLOSURE.md) 冻结关闭。Stage4E-E2E [Level A 协议](STAGE4E_STATIC_HGRAG_E2E_ANSWER_QUALITY_LEVEL_A_PROTOCOL.md) 已完成：生成器选择、1,000-query Gold-free main/rerun、pre-Gold verification、Gold evaluation 与 final verification 均通过。冻结决策为 `STATIC_HGRAG_E2E_SUPPORTED`；现有事务不应覆盖或重跑。

Stage4F-XDR 已完成 [实验卡](STAGE4F_XDR_EXPERIMENT_CARD.md) 预定义的完整 official 事务。3,000-query main/rerun、pre-Gold verification、Gold evaluation、10,000 bootstrap、final verification 与 post-decision Channel C 均完成；冻结结果为 `STATIC_HGRAG_XDR_SUPPORTED`。现有 Stage4F 工件不得覆盖或重跑。

Stage4G-GTR 已完成 [实验卡](STAGE4G_GTR_EXPERIMENT_CARD.md) 预定义的完整 generator-transfer 事务。它复用 Stage4E/4F frozen inputs 与 rankings，只更换为一个事前指定的 Gemma official mobile-QAT 配置。8,000-call main、400-call 分层 subset rerun、pre-Gold verification、Gold evaluation、10,000 次 dataset-stratified bootstrap、generator interaction 与 final verification 均完成；冻结结果为 `GENERATOR_TRANSFER_INCONCLUSIVE`。现有 Stage4G 工件不得覆盖或重跑。

Stage4H-CBE 已完成 [实验卡](STAGE4H_CBE_EXPERIMENT_CARD.md) 预定义的完整 component/strong-baseline 事务。新的 HotpotQA 1,000 + MuSiQue 1,500 边界与全部历史正式 IDs overlap 0；17,500-call main、1,400-call pre-hash subset、pre-Gold reconstruction、Gold evaluation、10,000-bootstrap、Holm 和 final verification 均完成。Full−Dense/NoFacet 受支持，Full−StrongDense 为负，Full−NoProtection 不确定，flat-unit 未公平定义。现有 Stage4H 工件不得覆盖或重跑。

Stage4I-SDC 已完成 [实验卡](STAGE4I_SDC_EXPERIMENT_CARD.md) 的 BGE 主排名 + MiniLM-HGRAG sidecar 事务。Protected−BGE 不确定；同一插入集合的 protected placement 受支持；facet 增量不确定。Stage5A-BNH 又在 BGE-native 语义空间完成 development/confirmation 与 final independent verification；核心、placement、facet 三项均不确定。两阶段正式工件均不得覆盖或重跑。

Stage5R-PMR 只读派生论文材料。Stage4E–Stage4I 回归 89/89、Stage5A 9/9、Stage5-PMC verifier 和 Stage5R joint verifier 均通过。作者/venue/license 元数据尚未绑定，因此当前是科学稿完整而非正式可投稿状态。

## 当前授权治理

```text
STAGE_LEVEL_AUTHORIZATION_ACTIVE
ONE_RESEARCH_STAGE_ONE_AUTHORIZATION
STEP_LEVEL_APPROVAL_DISABLED
CHANNEL_LEVEL_REAPPROVAL_DISABLED
ENGINEERING_WORK_AUTONOMOUS
STAGE_INTERNAL_EXECUTION_CONTINUOUS
EXCEPTION_BASED_PAUSE_ONLY
SCIENTIFIC_INTEGRITY_CONTROLS_RETAINED
```

这是项目长期、全局的现行治理基线，适用于当前及未来全部科研阶段，不是单次复现事务或 Stage4E 的临时规则。阶段授权默认连续覆盖实验卡中预定义的实现、测试、数据/Channel、正式运行、固定分析、独立验证、确定性复跑、报告和 Git/远端核验。Channel 与 Gold 隔离仍是可复现性和防泄漏合同，但不自动形成重复审批点；本文登记的命令、环境、SHA 和路径用于重建与核验，不是逐命令授权凭证。

普通工程异常自主最小修复并继续。只有新科学问题或阶段、冻结科学语义变化、使用当前授权外的新证据源、或严重完整性异常才暂停。历史审批链与旧命令保留为证据，不构成当前执行规则。Stage4E–4I 已按各自阶段授权完成；这些授权不延伸到 full-wiki Gold、open-domain、新生成器、新 strong-retriever search、reservation、Stage3B、U2 或新 controller。

## Stage4E 已冻结复现边界

| 项目 | 冻结值 / 当前状态 |
|---|---|
| 数据 | `hotpot_train_v1.1.json`；566,426,227 bytes；`26650CF...CD316` |
| 样本 | `SHA256("stage4e_e2e_v1\0" + _id)` 排序前 1,000；历史 HotpotQA ID 重叠 0 |
| 研究角色 | new-ID same-domain closed distractor holdout；不是外部数据集/full-wiki |
| retrieval arms | `DENSE_TOP20` vs 无 controller 的 `STATIC_Q25_TOP20` |
| encoder | `sentence-transformers/all-MiniLM-L6-v2` revision `1110a243...`；13 个实际文件已绑定 |
| generator | `Qwen/Qwen2.5-1.5B-Instruct` revision `989aa798...`；7 个实际文件已绑定 |
| 环境 | CPython 3.12.0；torch 2.12.1+cu130；CUDA 13.0；transformers 5.14.1；safetensors 0.8.0；RTX 4060 Laptop GPU |
| primary | paired `delta_answer_f1 = +0.014780 [0.000203,0.029883]`；10,000 query bootstrap |
| secondary | `delta_answer_em = +0.010000 [-0.005000,0.025000]`；CR@20 `0.737→0.798` |
| decision | `STATIC_HGRAG_E2E_SUPPORTED`；`STAGE4E_FINAL_VERIFICATION_PASS` |

精确绑定见 [official config](../configs/stage4e_e2e_official_train1000_v1.json)、[input manifest](../results/stage4e_e2e_official_train1000_v1_input_manifest.json)、[model manifest](../results/stage4e_e2e_model_snapshot_manifest.json)、[environment manifest](../results/stage4e_e2e_environment_manifest.json) 与 [rebound input verification](../results/stage4e_e2e_official_train1000_v1_verified_input_rebind.json)。正式结果见 [evaluation summary](../results/stage4e_e2e_official_train1000_v1_evaluation_summary.json)、[scientific decision](../results/stage4e_e2e_official_train1000_v1_scientific_decision.json)、[final verification](../results/stage4e_e2e_official_train1000_v1_final_verification.json) 和 [Stage4E 报告](../reports/超粒球RAG_Stage4E_E2E答案质量报告.md)。Stage4D 的环境和命令不自动成为 Stage4E 环境。

关键冻结 SHA-256：

- rankings：`AA6CBAD5D37BD66424DCAC6472FEBA8AC5FBAA769B789D968103AAB7CFDD1455`；
- predictions main/rerun：`FE9D6716BBB2D83DD3407CB5A042CB9F888912256C478FA501DE9F5457945D58`；
- prompt audit main/rerun：`130B78B896EDDBF0250E60736B223029163C30BBA6A492C6D4978D57E2556055`；
- evaluation summary：`BC6D6EF89A47B7314AEA12966894750E5733449ED76241582116451E4BFFF05E`；
- query audit：`ACDB9D22C14B9D10FEA0867DFFB2B87DBD4D1B4E07FCDBA8277638E3AB638C19`；
- scientific decision：`9692B1E3B6BC1DFEEF596FBC8C42CB5DC67649D426F85299D7162CEB346B2B9B`；
- final verification 文件：`310B0A53F54B043BBFDA027FDCA3A18901AAFE890716EC6F5919A31B4229931D`。

## Stage4F 已完成并冻结的复现边界

| 项目 | 冻结值 / 当前状态 |
|---|---|
| source | MuSiQue-Answerable v1.0 train；241,046,755 bytes；`83A75B1E...248490A`；CC BY 4.0 |
| 样本 | ID-only hash 前 3,000；历史 MuSiQue dev 1,000 ID overlap 0 |
| candidate units | 固定 regex 句界；218,698 units；单题 27–151；Gold 仍为官方 supporting paragraph |
| channels | blind `90,210,161 / C8D73F6F...EC4C5`；Gold `2,194,235 / E53E3AF3...60B2D`；metadata `817,266 / 8CBA7F1C...ECAA3` |
| model/environment | Stage4E 的 MiniLM revision `1110a243...`、Qwen revision `989aa798...` 与 CPython 3.12/CUDA 13 精确重绑定 |
| methods | `DENSE_TOP20` vs 无 U1/controller 的 `STATIC_Q25_TOP20`；Stage4E q25 参数不变 |
| statistics | paired answer F1；10,000 bootstrap；seed 20260723；EM non-inferiority guard |
| implementation | source validation、A/B/C、retrieval/generation、official MuSiQue scoring、bootstrap、decision、independent verifier、atomic/no-overwrite |
| tests | 初始 24/24 synthetic PASS；final-verifier 完整性修正后 27/27 PASS |
| primary | answer F1 `0.135952→0.147354`；delta `+0.011401 [0.004495,0.018352]` |
| supportive | answer EM delta `+0.010000 [0.003333,0.016667]`；CR@20 `0.589→0.650` |
| determinism | predictions main/rerun 同为 `1,106,316 / 68F95245...34E62E`；prompt audits 同为 `8,573,108 / D27D24E7...FF132E` |
| decision | `STATIC_HGRAG_XDR_SUPPORTED`；`STAGE4F_FINAL_VERIFICATION_PASS` |
| authorization | `AUTHORIZE_STAGE4F_XDR_FULL_OFFICIAL_EXECUTION` 已完整执行并关闭 |

精确入口为 [experiment card](STAGE4F_XDR_EXPERIMENT_CARD.md)、[official config](../configs/stage4f_xdr_official.json)、[input manifest](../results/stage4f_xdr_musique_train3000_v1_input_manifest.json)、[input verification](../results/stage4f_xdr_musique_train3000_v1_verified_input.json)、[evaluation summary](../results/stage4f_xdr_musique_train3000_v1_evaluation_summary.json)、[final verification](../results/stage4f_xdr_musique_train3000_v1_final_verification.json)、[artifact manifest](../results/stage4f_xdr_musique_train3000_v1_artifact_manifest.json) 与 [正式报告](../reports/超粒球RAG_Stage4F_XDR跨数据集复制报告.md)。Raw/processed A/B/C 和 embedding cache 不进入 Git。

关键冻结 SHA-256：

- rankings：`732A10DE74E8F97E5CECFDBFBBC3B49E5EF053C6F190948CD5C0B66D71D6AEDD`；
- predictions main/rerun：`68F9524542B91C8FD93C7A4B0B3549BFE168DF1EB5D94E6479149E5B4534E62E`；
- prompt audit main/rerun：`D27D24E79F79758F860884C2B36D2AC509D0FFA4B587E90E8EE596F10FFF132E`；
- evaluation summary：`839E946A5BA5AEB5502D10867647B26B9DBA1001BF7BC27EF740056312CE6C50`；
- query audit：`EA7634EE7354A959A1D03D1E9DD7A220BA39F3F7CF2D6F168D17E3EC53C66ADF`；
- scientific decision：`7406AD4525FF8422515DA31027C68D75864B4C24385F2D942703A6CD577BBED2`；
- final verification：`86A2EC634981BF9FB4E7DAFBF94CEF59AC2EFAA2B0BEBAD5C3A33711233E6B8F`；
- descriptive subgroups：`405465EAABC4B333E4A7BA8E1CA798E1E7B11B60DD570667E6B0D3C1F5AD6467`。

## Stage4G 已完成并冻结的复现边界

| 项目 | 冻结值 / 当前状态 |
|---|---|
| 新因素 | 一个事前指定生成器配置；不改变数据、ranking、prompt 语义或 evaluator |
| generator | `google/gemma-4-E2B-it-qat-mobile-transformers@dd693ff40353f057ca5f07e945ad867f4afbf2ec` |
| runtime | Google official mobile-QAT Transformers；thinking disabled |
| weight | 2,458,111,846 bytes；`EFAB4290...76A9A4` |
| inputs | Stage4E HotpotQA 1,000 + Stage4F MuSiQue 3,000 frozen blind inputs/rankings |
| methods | `DENSE_TOP20` vs `STATIC_Q25_TOP20`；不重跑 retrieval |
| generation | 4,096-token cap；greedy；beams 1；max new tokens 32；batch 1 |
| determinism | B：full main 8,000 calls + pre-hash dataset-stratified 400-call subset rerun；精确复现 |
| statistics | dataset-specific paired bootstrap + dataset-equal-weight stratified bootstrap；10,000；seed 20260724 |
| HotpotQA | F1 delta `+0.012647 [-0.002196,0.027444]`；EM delta `+0.006000 [-0.009000,0.021000]` |
| MuSiQue | F1 delta `-0.002320 [-0.006849,0.002076]`；EM delta `-0.001333 [-0.005667,0.003000]` |
| equal-weight | F1 delta `+0.005164 [-0.002623,0.012950]`；EM delta `+0.002333 [-0.005667,0.010333]` |
| query-weighted | F1 `+0.001422`；EM `+0.000500`；MuSiQue weight 75%；描述性 |
| execution | main/subset 共 8,400 calls；零失败；零 truncation |
| decision | `GENERATOR_TRANSFER_INCONCLUSIVE`；`STAGE4G_GTR_FINAL_VERIFICATION_PASS` |

精确入口为 [experiment card](STAGE4G_GTR_EXPERIMENT_CARD.md)、[official config](../configs/stage4g_gtr_official.json)、[input/model manifest](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_input_model_manifest.json)、[pre-Gold verification](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_verified_pregold.json)、[dataset summaries](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_dataset_summaries.json)、[equal-weight summary](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_equal_weight_summary.json)、[final verification](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_final_verification.json)、[artifact manifest](../results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_artifact_manifest.json) 与 [正式报告](../reports/超粒球RAG_Stage4G_GTR生成器迁移复制报告.md)。

关键冻结 SHA-256：

- input/model manifest：`5B4070AF14F2DBBEB4D69EFA1FA445017DB6F1BF7B071DCE73D9D7498E7DAEC5`；
- predictions main：`E6B0A50CB3090A7268E838EC5BBB0DD6C5FE90440A75DA0B103D2E0906D31709`；
- predictions rerun subset：`43CDF730152032D752956D359E707FF92C17C8517EBE0B8AA1DEB72855688FA9`；
- prompt audit main：`E8227941D1AF5E3C893AC538E1E5DD61C2FE818F879D0EA6D45FB7137E54F8F1`；
- prompt audit rerun subset：`75947C6F15168F49E552A5B99388354E39490349E30BDC034D79B9F4B75ADFA4`；
- verified pre-Gold：`5F9C26A6D0F80B423FFD500FA2ECFCF5815F60815F36E639BEEE11E5AA1ABAB4`；
- query scores：`8796DC8033CC9B3993BC02A224CD8585AE89C46E7CDAB20DA1447E9C6B0241BE`；
- dataset summaries：`1656CEAC063EB53D4854481C83A1A4046D6257B442A3C376EDC851B5436D6E3B`；
- equal-weight summary：`0BF7E2658521510438545BC077DBAA1EA7C902C2FD35FFBE4013D209D7890239`；
- scientific decision：`246FE8B1DFC157551E570994059306315C03AA050B23AC3F9FD31780D710FBF5`；
- final verification：`3BB9A87C3BD62FCF8CE663F4EEA7A28A6D0C8E1ECC0AB8FBF8C015212137E65B`；
- artifact manifest：`E61FADC265D2F2AA937E7E66F78011BDD6B45E67CB61BDCF03FF320C5DB0FDD1`。

## Stage4H 已完成并冻结的复现边界

| 项目 | 冻结值 / 当前状态 |
|---|---|
| samples | HotpotQA 1,000 + MuSiQue 1,500；全部历史正式 IDs overlap 0 |
| candidate units | HotpotQA 41,153 + MuSiQue 109,332 = 150,485 |
| methods | Dense、Full、NoProtection、NoFacet、BM25、Hybrid、BGE StrongDense；同 query/candidate/Top-20/Qwen |
| strong dense | `BAAI/bge-large-en-v1.5@d4aa6901d3a41ba39fb536a557fa166f842b0e09`；MIT；Gold 前绑定 |
| determinism | full main 17,500 calls + 200-query/1,400-call pre-hash dataset-stratified subset；predictions/prompts 精确复现 |
| statistics | dataset-paired + dataset-equal-weight bootstrap；10,000；seed 20260725；四个主要比较 Holm |
| Full−Dense | F1 `+0.0135685 [0.0049140,0.0223253]`；`SUPPORTED` |
| Full−StrongDense | F1 `-0.0399791 [-0.0539331,-0.0262114]`；`NEGATIVE` |
| Full−NoProtection | F1 `+0.0035400 [-0.0067456,0.0138931]`；`INCONCLUSIVE` |
| Full−NoFacet | F1 `+0.0133579 [0.0034084,0.0234257]`；`SUPPORTED` |
| flat / P1 curve | `NOT_FAIRLY_DEFINED` / `NOT_RUN_RESOURCE_BOUNDED` |
| execution | main/subset 共 18,900 calls；零失败；main wall 6,265.00 s；GPU peak 4,174,117,888 bytes |
| decision | `STAGE4H_FINAL_VERIFICATION_PASS` |

精确入口为 [experiment card](STAGE4H_CBE_EXPERIMENT_CARD.md)、[official config](../configs/stage4h_cbe_official.json)、[input manifest](../results/stage4h_cbe_hotpot1000_musique1500_v1_input_manifest.json)、[pre-Gold verification](../results/stage4h_cbe_hotpot1000_musique1500_v1_verified_pregold.json)、[dataset summaries](../results/stage4h_cbe_hotpot1000_musique1500_v1_dataset_summaries.json)、[equal-weight summary](../results/stage4h_cbe_hotpot1000_musique1500_v1_equal_weight_summary.json)、[final verification](../results/stage4h_cbe_hotpot1000_musique1500_v1_final_verification.json)、[artifact manifest](../results/stage4h_cbe_hotpot1000_musique1500_v1_artifact_manifest.json) 与 [正式报告](../reports/超粒球RAG_Stage4H_CBE核心消融与强基线报告.md)。

关键冻结 SHA-256：

- rankings：`EAECD420CEDDFD0E670892E9B78B0D6D02BB3E9BE2A84BC36631C1D985C49822`；
- predictions main：`52B9276E93AF19820B8F2E358F54BE9CDF88D4A8C6A34020AF3EDC153470E310`；
- predictions subset：`84025B63BB1C49268287DE2E0A1B85B9EF4A91821D98441658C0E7807C943C78`；
- prompt audit main：`B7B2D3E3846CD7406C4E646A0DC007F54A5CC3BBA863CAD9E0551F7AB9A5B507`；
- prompt audit subset：`BB6CA94A55F311B07F96F5B5A280D944F5117A8A3220629C4C2F7835E3119042`；
- verified pre-Gold：`ACF11E359BFFF40DB53C07DB27A39E6C5ABE61AC1C4161C8A15542397783639B`；
- query audit：`6232260E8D91D070E8A28B96A4F179538D2EB300F16FE28DB3B24168ADBD4CA9`；
- dataset/equal-weight summaries：`C9B2E163A46FE41B458321C8292CCF21A99C5B6AC666E3E28BA6798E013CB85B` / `0C8677960F2CB07526B36264CE58883ED28D12C0016F6EAD8A036D3DD0BE7FA4`；
- scientific decision：`3C4B2E4A2AAC4A5E031D8513DD88391BC378351113DF7E99E6362B85DDE8BBD5`；
- final verification：`692D7150043071580B58F1CC1F758884A6178412C98ED193C4D4D27BDB40726F`；
- artifact manifest：`6E467B17BE53F1EA75D897E1185558F1FE50C04A4302568515C831DA7641C72D`。

## Stage4I 已完成并冻结的复现边界

| 项目 | 冻结值 / 当前状态 |
|---|---|
| samples | HotpotQA 1,000 + MuSiQue 1,500；全部历史正式 IDs overlap 0 |
| candidate units | HotpotQA 41,353 + MuSiQue 109,296 = 150,649 |
| methods | BGE、BGE+HGRAG Protected、相同 inserted set Unprotected、Protected NoFacet |
| retrievers | `BAAI/bge-large-en-v1.5@d4aa6901...` 主干；`all-MiniLM-L6-v2@1110a243...` sidecar |
| q25 | `0.1957079917192459`；只用于 MiniLM sidecar eligibility；不做 score fusion |
| blind eligibility | HotpotQA 0.458；MuSiQue 0.71333；combined 0.6112；PASS |
| determinism | full main 10,000 calls + 200-query/800-call pre-hash subset；predictions/prompts 精确复现 |
| statistics | dataset-paired + dataset-equal-weight bootstrap；10,000；seed 20260726 |
| Protected−BGE | F1 `-0.0025635 [-0.0099817,0.0045765]`；`INCONCLUSIVE` |
| Protected−Unprotected | F1 `+0.0112225 [0.0012860,0.0210434]`；`SUPPORTED` |
| Protected−NoFacet | F1 `-0.0074311 [-0.0161609,0.0013248]`；`INCONCLUSIVE` |
| execution | main/subset 共 10,800 calls；零失败；main wall 4,999.07 s；GPU peak 4,356,265,984 bytes |
| decision | `STAGE4I_FINAL_VERIFICATION_PASS` |

精确入口为 [experiment card](STAGE4I_SDC_EXPERIMENT_CARD.md)、[official config](../configs/stage4i_sdc_official.json)、[input manifest](../results/stage4i_sdc_hotpot1000_musique1500_v1_input_manifest.json)、[eligibility audit](../results/stage4i_sdc_hotpot1000_musique1500_v1_eligibility_audit.json)、[pre-Gold verification](../results/stage4i_sdc_hotpot1000_musique1500_v1_verified_pregold.json)、[equal-weight summary](../results/stage4i_sdc_hotpot1000_musique1500_v1_equal_weight_summary.json)、[evidence transition audit](../results/stage4i_sdc_hotpot1000_musique1500_v1_evidence_transition_audit.json)、[final verification](../results/stage4i_sdc_hotpot1000_musique1500_v1_final_verification.json)、[artifact manifest](../results/stage4i_sdc_hotpot1000_musique1500_v1_artifact_manifest.json) 与 [正式报告](../reports/超粒球RAG_Stage4I_SDC强稠密检索互补性报告.md)。

关键冻结 SHA-256：

- input manifest：`E9933740CD7C3DDA5203DC4D993709237A249117918701DF340D04F8932634F1`；
- MiniLM/BGE caches：`C7931066992B0ACF1EAD03A6E8C8F24EAF0D7714E63E514A53EC5601B953F84C` / `2D655280095AE514291EFB521BD5A4FC32C758C76C6E8DC04D6ADEAE6F8E4EE0`；
- eligibility audit：`31623F0562B0ED83671A871D5039FE498E9359C384C6ED1549A8B0687DDBB92B`；
- rankings / candidate trace：`AACC7776AFF4BA512FE9530F366D177DEC7BF04531620F4447245C6E96682FC2` / `62AC7A2FD91997FFC72E2F0A2A0F9945D2056C0670C299CC002917B2EC4D9DA7`；
- predictions main / subset：`A6D8A4652A208E39EDEBA590CA17D9DACB05D2C9C29EC37E8E274C8AF30B2D22` / `7452A946C25E76DC6252241C3B25611863CAD751951EDC2D612A2C7549F6B3C4`；
- prompt audit main / subset：`3CECDADE511873D0951B24DB9C617042C50900A4B23123CCFFFDF199902E2EA0` / `11D2A9CE00F736D94EECA4B959A330C2A7D0084B35FD48F25669D3F663CF9D98`；
- verified pre-Gold：`30172A18E4403BE8701952918119EC2BE9606743D5CA4A5AD51456A24B08BEEC`；
- query audit：`03AE49C301AD2AB250FB79D7DFA561B936D6C5201AAF9B87131D4DFB4D70ABFB`；
- dataset/equal-weight summaries：`4487349198E34F0DA99A91423EDC991315909947036D6D2E11F3BCFD14DF95DF` / `EC1AF7077CDC6858CE39B76FE842E60283EB9BF19068C6384CDF8C282C9E1717`；
- evidence transition audit：`3DE05CBDAEC38EE216C9C0D5DC8834B6B6EC1726E4CDDC37B0A1132DC8611BE2`；
- scientific decision：`D0D10AB368A3C8ABD4EB7B6B7C3454BB3943671D04307B4A9D77B13610008726`；
- final verification：`B15620888F68EB6EF9D39DABB2295D425665F870617FD021B237B9CDA96D2019`；
- artifact manifest：`831D937749548A05D09579F5F3BB39506F762ABE6066A04273D7A34287F9292E`。

正式运行使用 Stage4E 冻结 CPython 3.12/Qwen/CUDA 环境，并在启动前设置：

```powershell
$env:CUBLAS_WORKSPACE_CONFIG=':4096:8'
$env:MKL_NUM_THREADS='1'
$env:NUMEXPR_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:PYTHONHASHSEED='0'
$env:TOKENIZERS_PARALLELISM='false'
```

实施绑定提交为 `6aea4fba476ffd6c8b437acd5f9c97214218116a`；配置重新绑定提交为
`c62577d`。修正只避免对已归一化 float32 cache 做第二次非幂等归一化，未重建或覆盖
cache、rankings、candidate trace 或 eligibility audit。

## 运行环境

```text
Python: D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe
Version: 3.12.0
NumPy: 2.5.1
```

当前 direct entry point 使用普通脚本目录导入，只保留 `-B`；不要加入会移除 sibling-module 路径的 `-I`。

### Stage4D 固定 synthetic 环境

```text
CPython: 3.12.0
NumPy: 2.5.1
SciPy: 1.18.0
scikit-learn: 1.9.0
joblib: 1.5.3
threadpoolctl: 3.6.0
narwhals: 2.24.0
```

精确依赖见 `requirements-stage4d.txt`。运行 probe 前必须把 `PYTHONHASHSEED` 设为 `0`，并把 `OMP_NUM_THREADS`、`OPENBLAS_NUM_THREADS`、`MKL_NUM_THREADS`、`NUMEXPR_NUM_THREADS`、`VECLIB_MAXIMUM_THREADS`、`BLIS_NUM_THREADS` 全部设为 `1`。核心实现提交为 `b4dfa52d0a38409dfc19444d21beec59606088e1`，guarded artifact transaction 补全提交为 `730daea1350616bfdcb6a11832b361c4d574d985`。

已完成的 synthetic-only 验证命令：

```powershell
$env:PYTHONHASHSEED='0'
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
$env:NUMEXPR_NUM_THREADS='1'
$env:VECLIB_MAXIMUM_THREADS='1'
$env:BLIS_NUM_THREADS='1'
& 'temp\stage4d_env\Scripts\python.exe' -B -m unittest discover -s tests -p 'test_stage4d_cma.py' -v
```

结果：16/16 PASS，包含 byte-identical synthetic rerun。`temp/stage4d_env` 为 `.gitignore` 覆盖的本地隔离环境，不是科研工件，不提交 Git。

## Stage4D official 工件与验证

| 工件 | Bytes | SHA-256 |
|---|---:|---|
| `stage4d_cma_candidate_labels.jsonl` | 6,229,542 | `E206895E36FB7472502E8FEA082C1AEA7C7AD2CB7E198F37200B271E7164F9E3` |
| `stage4d_cma_counterfactual_summary.json` | 5,189 | `37A57AD7AB2760C8C9E368F359C80B378F51C6B5C38629BDC0A75ECEB5D6C9F1` |
| `stage4d_cma_fold_assignments.json` | 141,871 | `9B80923965407838105BA182E45B685EF5CD60ABC148B49061576EFDAF6FA650` |
| `stage4d_cma_oof_predictions.csv` | 13,335,718 | `29EC13EC6AEAB28837C3EBBE24F99AF496A98B0793475DADF2BA071FFEE7ECDC` |
| `stage4d_cma_metrics.json` | 117,023 | `22C843E248D0EB44893E42FB61D207061E8F9E07744A4C808AB8F55D63226999` |
| `stage4d_cma_decision.json` | 120 | `7EE774CA97722353DEC7D71E5B461FEF17ADA08DDCB96568C988A1497B72FA68` |

Probe source blob `a1dc95ceeb819320ed938ae38bc6dbde61d80e59` 在 zero-candidate repair `080cc44781cddc7d25584812fee5dea2158142e9` 与当前协议提交 `b8bd1eafd51507e0d272a701219b7f7833c35704` 中相同。第一轮外层 shell timeout 后，Python 子进程完成两次 probe、同字节检查、内部验证和原子提升；后续 no-timeout 事务在完成 main/rerun 与内部验证后被 no-overwrite guard 阻止覆盖。

只读 bounded provenance audit 重新解析三 probe 工件，确认 frozen renderer 逐字节一致、68,588 行 OOF identity/region/label/fold 合同完整，`verify_probe_outputs()` 返回 `STAGE4D_PROBE_VERIFIED`。它从既有 probabilities 重算所有 overall/fold/region metrics 和 36 个 seed `20260719`、10,000 次 query-cluster bootstrap 区块；五项受保护工件审计前后完全未变。正式报告为 [Stage4D-CMA 候选边际效用归因审计报告](../reports/超粒球RAG_Stage4D_CMA候选边际效用归因审计报告.md)。

## Stage4C 冻结绑定与输出

| 项目 | 绑定 |
|---|---|
| Protocol commit | `2e925063175a6402a21ade3fc0ab4a27faaa6dd7` |
| Protocol SHA-256 | `7F1C3F78BFA5C9D36A4EA318394E8E791476215AEBAA73DFEA1B40B6D5FDD383` |
| Implementation commit | `1bbe8a571d4e0c4aa965b4f0fa71b1de5901b2a7` |
| Script SHA-256 | `274A4E01516B12EAB8A81323D612CAA5954DFB25865F189B89298466380AD670` |
| Targeted tests SHA-256 | `A59C683B741007556362603ACF9876E0F19DC25655B0FF8C08F587B63DEF9639` |

Stage4C 只读取下文已经登记的四个 pre-Gold 工件、Gold query audit、evaluation summary 和 `VERIFIED_POST_GOLD`；七个输入长度/SHA 均由脚本在读取统计前核对。

| 工件 | Bytes | SHA-256 |
|---|---:|---|
| `results/stage4c_u1_fma_query_features.csv` | 1,205,296 | `311D4AE15F80A14A5C3BEBE427E894E445C76F17045709CE62E15F89A138E142` |
| `results/stage4c_u1_fma_feature_separability.csv` | 10,057 | `BE1FA4F74BE8A059E7DB92326BD22084D5817901F106D2B367F2249B1F2C8CE9` |
| `results/stage4c_u1_fma_score_deciles.csv` | 1,813 | `04CE6F940473439C6CBA8D52CF518602D3725B4561E5711F437519E042056180` |
| `results/stage4c_u1_fma_candidate_mechanisms.csv` | 772,763 | `FA5C378F6A8E69CAC52859D49918912B6822F0F97C29BB63C0ADCD1D655A23EF` |
| `results/stage4c_u1_fma_oof_predictions.csv` | 3,671,149 | `BEE06C3FBE69FED3D30C0C33126F37E218268BEC9C327DA0BE1C2B654AE09866` |
| `results/stage4c_u1_fma_summary.json` | 108,940 | `7B6D8C8B85EC32D596250137CC676B4C732C964C64714F7EF5EE6B3E86E7B0C6` |

完成记录（不是当前重跑指令）：

```powershell
& 'D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe' -B scripts/stage4c_u1_failure_mechanism_audit.py --output-dir results
```

terminal marker：

```text
STAGE4C_U1_FMA_PASS queries=4500 decision=MECHANISM_EVIDENCE_INCONCLUSIVE
```

正式脚本拒绝覆盖已有六工件。完整正式重跑未执行；确定性证据限于固定输入/代码/seed、16/16 targeted tests 中的 synthetic byte check、summary 内置 CSV SHA 和运行后的只读结构复核。因此完整结果的 ARS reproducibility verdict 为 `CANNOT_VERIFY`，而不是虚构第二次同字节运行。

## 冻结配置

| 文件 | SHA-256 |
|---|---|
| `configs/stage4b_u1_d_official.json` | `176FF6747680DD597DB01E174619CABF7112BF4B91FF8BF2402F5B02754A5F58` |
| `configs/stage4b_u1_d_gold_evaluation.json` | `CA093EA8455B89B15F874D41A63452C8D24ADD432A540E575DBD5E11EEAB391A` |
| `docs/STAGE4B_U1_SIMPLIFIED_EXECUTION_PROTOCOL_V1.md` | `ABED88FAC906748CE9D93F04C0D4BA35B62BB6819F61A2D84273687BE35C724C` |
| `scripts/stage4b_u1_evaluate.py` | `D7B96E29AD5AB2F6652FFC14D73048D36C205F78ABA7FA8FCB501818A1A89BBB` |
| `scripts/stage4b_u1_gold_evaluation_verifier.py` | `EC9F6B7DF5AA867A2078FD271EBA691B678C9F44073C9D1FEA780DF484A58BD2` |

Pre-Gold config 继续绑定 implementation commit `8ab5e193d00733e0ae617b2c17f02da4ce01594f` 及七个 implementation 文件 SHA，且不含 Gold、reservation 或 Stage3B 输入。Gold config 的冻结提交为 `1bfcf7b108dd4a8db17ba97a4d3b97a6f274f983`，只向 evaluator 绑定 development Gold 和已冻结 ranking/policy。

## Gold 输入身份

| 输入 | Bytes | SHA-256 |
|---|---:|---|
| `stage4b_u1_d_official_dev4500_v2_3_1_gold_map.json` | 1,498,640 | `76D15A88C218C9EDF36A9F9F52B0D2D9877463E5653EC8AB1E5C94542E99B30B` |
| `stage4b_u1_d_official_dev4500_v2_3_1_evaluator_channel_audit.json` | 1,182 | `220FD7310AA187840A5E9D95174EBAF5BD4BDF6097BC58BACD28413D85377C17` |

这两个文件位于登记数据目录 `E:\SCIENCE\超粒球RAG_数据\processed`，不提交 Git。Gold 在 decisions、rankings、policy 和 `VERIFIED_PRE_GOLD` 冻结后才由 evaluator 读取。

## 冻结 pre-Gold 工件

| 工件 | Bytes | SHA-256 |
|---|---:|---|
| `results/stage4b_u1_d_official_dev4500_simplified_v1_decisions.jsonl` | 2,684,439 | `4B2AD2E5707B20FD46B6250FDA5395433F52E55FB1281F1499412C8C749A456A` |
| `results/stage4b_u1_d_official_dev4500_simplified_v1_rankings.jsonl` | 18,235,604 | `ED289D234F6F4FEC58A48168CB6CA78950489CD5F5640E977068CA6A786E03CB` |
| `results/stage4b_u1_d_official_dev4500_simplified_v1_policy.json` | 261,587 | `657E5F25A94224D8B020780F3E7335942B16BC6D8C7939FB74D1BBAA9A9D868B` |
| `results/stage4b_u1_d_official_dev4500_simplified_v1_verified_pre_gold.json` | 3,479 | `39EAD86A3A835983DCB67BAF656255F51569BCEE5B9AC2E16FACF404281D7818` |

三项 controller 工件提交：`9357c157217f85008fa93df07d321a2f4c6a2bc1`。

Verified 单路径提交：`83d172bc89efbb31782eee308bac5293aa24457b`。

## Gold 结果工件

结果生成提交：`c06761f0c55cbeecf75564211a59f4540cfbae06`。

正式 summary 原始字节修复提交：`b500184bc581d73a381de65c32cf3b72e9758cc9`。该提交只新增精确两行 `.gitattributes -text` 绑定并重新加入现有本地 summary 原始字节；没有重新生成或修改 JSON 字段。

| 工件 | Bytes | SHA-256 |
|---|---:|---|
| `results/stage4b_u1_d_official_dev4500_simplified_v1_query_audit.jsonl` | 2,600,121 | `8616C28C71D190E3287CCE3725EDC0B1FD0DFB41DF47C739F4A84A573F938313` |
| `results/stage4b_u1_d_official_dev4500_simplified_v1_evaluation_summary.json` | 7,662 | `7F82056FB14F9D8D73E668A82CB5304B28385E62A01C428599F23260AB7F89DE` |
| `results/stage4b_u1_d_official_dev4500_simplified_v1_query_audit_rerun.jsonl` | 2,600,121 | `8616C28C71D190E3287CCE3725EDC0B1FD0DFB41DF47C739F4A84A573F938313` |
| `results/stage4b_u1_d_official_dev4500_simplified_v1_evaluation_summary_rerun.json` | 7,662 | `7F82056FB14F9D8D73E668A82CB5304B28385E62A01C428599F23260AB7F89DE` |
| `results/stage4b_u1_d_official_dev4500_simplified_v1_verified_post_gold.json` | 2,293 | `44BF3E8B0B036958633E237186A458B13090D8073F587657D831656FB7720ECD` |

四方字节核验结果：

| 工件 | 本地 | Git index | commit blob | GitHub blob | 结论 |
|---|---|---|---|---|---|
| Primary summary | 7,662 / `7F82056F...7F89DE` | 同左 | 同左 | 同左 | PASS |
| Rerun summary | 7,662 / `7F82056F...7F89DE` | 同左 | 同左 | 同左 | PASS |

两份 summary 在四个位置均互相同字节。两个 query audit 和 `VERIFIED_POST_GOLD` 在修复提交中的 Git object 未变化，仍保持表中原 SHA；rankings、policy 和 `VERIFIED_PRE_GOLD` 也未变化。

## 已完成命令

以下 pre-Gold 命令是已完成流程的复现记录，不是当前重跑指令：

```powershell
& 'D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe' -B scripts/stage4b_u1_simplified_preflight.py --config configs/stage4b_u1_d_official.json
& 'D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe' -B scripts/stage4b_u1_simplified_runner.py --config configs/stage4b_u1_d_official.json
& 'D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe' -B scripts/stage4b_u1_independent_verifier.py --config configs/stage4b_u1_d_official.json
```

实际输出：

```text
STAGE4B_U1_SIMPLIFIED_PREFLIGHT_PASS config_sha256=176FF6747680DD597DB01E174619CABF7112BF4B91FF8BF2402F5B02754A5F58
STAGE4B_U1_SIMPLIFIED_CONTROLLER_PASS queries=4500 selected=1195
STAGE4B_U1_SIMPLIFIED_VERIFIER_PASS queries=4500 status=VERIFIED_PRE_GOLD
```

Gold evaluation 的完整 argv、输入 SHA、主运行/复跑输出路径和参数保存在 `configs/stage4b_u1_d_gold_evaluation.json`。实际执行顺序为：

```powershell
& 'D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe' -B scripts/stage4b_u1_evaluate.py <config.commands.primary_evaluation 中的冻结参数>
& 'D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe' -B scripts/stage4b_u1_evaluate.py <config.commands.rerun_evaluation 中的冻结参数>
& 'D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe' -B scripts/stage4b_u1_gold_evaluation_verifier.py --config configs/stage4b_u1_d_gold_evaluation.json
```

主运行耗时 51.6 秒、复跑耗时 56.9 秒，均 exit 0。验证器输出：

```text
STAGE4B_U1_GOLD_INDEPENDENT_VERIFICATION_PASS queries=4500 decision=STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED
```

## 测试证据

- Strict-row-contract 定向测试：18/18 PASS。
- Gold verifier 定向测试：4/4 PASS。
- Gold 绑定后的单次完整 `test_stage4b_u1*.py` suite：281/281 PASS（16.742 秒）。
- 结果层复现：query audit 与 summary 的主运行/复跑长度、SHA-256 和字节完全相等。
- 独立验证器注册的输入绑定、逐查询审计、总体/类型点估计汇总、bootstrap 身份、Stage4A 基线等价、决策和输出提交全部 PASS。
- 报告完整性限制：科学协议要求 question-type 区间，但冻结 evaluator/validator 未生成或核对类型级区间。Gold 后未临时选择新算法补算；该缺口不影响由总体预注册门触发的停止决定。
- Stage4C targeted suite：16/16 PASS；最初的 dotted-module 调用因 `tests/` 不是 package 而加载 0 个用例，随后使用精确 discover 命令完成测试。
- Stage4C 只读结果复核：4,500/48/10/4,500/27,489 CSV 行数、schema、有限值、唯一键、OOF 概率范围、五个内置 CSV SHA 和七输入 SHA 全部 PASS。
- Stage4D-CMA synthetic suite：16/16 PASS；覆盖完整候选池/预算分层、独立 trace 重建、严格 schema/type/nullability/leakage、七标签、双 LOO、固定 query folds、Task-C 类边界、同一 OOF 分层指标、combined-only advancement、确定性 LF CSV、固定环境、official transaction fail-closed 和同字节复跑。
- Stage4D official probe：main/rerun 三工件同字节，内部 independent verifier PASS；bounded provenance audit 的 canonical bytes、68,588 OOF 行、全部 metrics/baselines 和 36 个 bootstrap 区块均 PASS。
- Stage4E–4H 统一回归：在冻结 CPython 3.12.0 下以标准库 `unittest discover` 分别执行四个精确测试文件，Stage4E 19/19、Stage4F 27/27、Stage4G 9/9、Stage4H 15/15，合计 70/70 PASS。环境未安装 `pytest`，因此没有修改冻结依赖，仅改用等价的仓库既有测试入口。
- Stage4I 定向 suite：19/19 PASS；Stage4E–4I 当前统一回归：89/89 PASS。Stage4D 另在其冻结 CPython 3.12 环境保持 17/17 PASS。

## 后续复现边界

本次 Gold transaction 已结束且失败停止规则已触发：

1. 不重复运行该 transaction；
2. 不在同一 development 上修改特征、公式、预算、阈值、排序或检验后重跑；
3. 不由该结果打开 reservation 或 Stage3B；
4. 后续新研究必须先形成独立问题、协议、样本边界和停止规则，再读取新结果；
5. Reservation、Stage3B、再次既有 Gold 执行和科学语义修改不在当前阶段授权内；如需使用，必须进入新的科学边界或明确扩展阶段授权。

Stage4D 的冻结 transaction 已完成；不得再次运行 Channel A/B/probe、覆盖三项 probe 工件、降低 bootstrap 或在同一 development 上结果后修改模型/feature/threshold。`CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE` 不授权 U2。Reservation、Stage3B、新 Gold 和任何新 candidate controller 仍需新的科学协议与明确授权。

本次冻结负结果只否定当前 U1-D controller 的晋级主张，不否定 HyperGranular-RAG 整体研究方向。Stage4C 的 `MECHANISM_EVIDENCE_INCONCLUSIVE` 不自动创建 U2；后续新 controller 必须作为新的科学语义和新的 Level A development 协议处理。

Stage4E-E2E 与 Stage4F-XDR 均已完成并冻结，不允许利用 Stage4D labels、OOF probabilities、feature panels 或 decision 改写其 ranking，也不得覆盖或重跑现有正式事务。下一边界是先定义新的科学问题与轻量实验卡；Reservation、Stage3B、U2 和新 controller 继续锁定。
