# Reproducibility

本文件只保留当前有效的复现入口。完整历史命令与旧治理链快照见 [归档版本](archive/REPRODUCIBILITY_PRE_REORGANIZATION_2026-07-18.md)。

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
STAGE4E_OFFICIAL_EXECUTION_NOT_AUTHORIZED
RESERVATION_REQUIRES_PAUSE
U2_NOT_AUTHORIZED
```

Pre-Gold 和本次获授权的 Gold evaluation 均已完成，不应重复运行。主运行与预注册复跑同字节，独立验证器已重建 4,500 条逐查询审计、汇总和 development 决策。

Stage4C-U1-FMA 也已完成一次冻结的 post-Gold exploratory diagnosis。它不是新的 Gold evaluation，不改变 Stage4B 负结果，也不授权 U2 或 reservation。

Stage4D-CMA 已在获授权边界内完成 Gold-free Channel A、development-Gold Channel B、固定 official probe、独立验证和 bounded provenance audit。唯一 advancement panel 未通过全部联合门，冻结结论为 `CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE`。现有工件不得覆盖或重跑；reservation、Stage3B 与 U2 仍未授权。

Stage4D 和当前 controller 分支已按 [STAGE4D_CMA_CLOSURE](STAGE4D_CMA_CLOSURE.md) 冻结关闭。Stage4E-E2E [Level A 协议](STAGE4E_STATIC_HGRAG_E2E_ANSWER_QUALITY_LEVEL_A_PROTOCOL.md) 已接受；source/model/environment/config/verifier 绑定和 Level B implementation 已完成。尚未运行 1,000-query official retrieval/generation/Gold evaluation，也没有 Stage4E 科研结果。

## Stage4E 已冻结复现边界

| 项目 | 冻结值 / 当前状态 |
|---|---|
| 数据 | `hotpot_train_v1.1.json`；566,426,227 bytes；`26650CF...CD316` |
| 样本 | `SHA256("stage4e_e2e_v1\0" + _id)` 排序前 1,000；历史 HotpotQA ID 重叠 0 |
| 研究角色 | new-ID same-domain closed distractor holdout；不是外部数据集/full-wiki |
| retrieval arms | `DENSE_TOP20` vs 无 controller 的 `STATIC_Q25_TOP20` |
| encoder | `sentence-transformers/all-MiniLM-L6-v2` revision `1110a243...`；13 个实际文件已绑定 |
| generator | `Qwen/Qwen2.5-1.5B-Instruct` revision `989aa798...`；7 个实际文件已绑定 |
| 环境 | CPython 3.12.0；torch 2.12.1+cu130；CUDA 13.0；transformers 5.9.0；RTX 4060 Laptop GPU |
| primary | paired `delta_answer_f1`，10,000 query bootstrap；未运行 |
| decision | supported / negative / inconclusive / no-scientific-decision；未判定 |

精确绑定见 [official config](../configs/stage4e_e2e_official_train1000_v1.json)、[input manifest](../results/stage4e_e2e_official_train1000_v1_input_manifest.json)、[model manifest](../results/stage4e_e2e_model_snapshot_manifest.json)、[environment manifest](../results/stage4e_e2e_environment_manifest.json) 与 [input verification](../results/stage4e_e2e_official_train1000_v1_verified_input.json)。这些是输入与工程验证，不是 official 科研结果。Stage4D 的环境和命令不自动成为 Stage4E 环境。

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

## 后续复现边界

本次 Gold transaction 已结束且失败停止规则已触发：

1. 不重复运行该 transaction；
2. 不在同一 development 上修改特征、公式、预算、阈值、排序或检验后重跑；
3. 不由该结果打开 reservation 或 Stage3B；
4. 后续新研究必须先形成独立问题、协议、样本边界和停止规则，再读取新结果；
5. Reservation、Stage3B、再次 Gold 执行和科学语义修改仍需单独协议与明确授权。

Stage4D 的冻结 transaction 已完成；不得再次运行 Channel A/B/probe、覆盖三项 probe 工件、降低 bootstrap 或在同一 development 上结果后修改模型/feature/threshold。`CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE` 不授权 U2。Reservation、Stage3B、新 Gold 和任何新 candidate controller 仍需新的科学协议与明确授权。

本次冻结负结果只否定当前 U1-D controller 的晋级主张，不否定 HyperGranular-RAG 整体研究方向。Stage4C 的 `MECHANISM_EVIDENCE_INCONCLUSIVE` 不自动创建 U2；后续新 controller 必须作为新的科学语义和新的 Level A development 协议处理。

当前下一项科研工作是审核并完成 Stage4E-E2E 的 Level A/Level B 绑定。Stage4E 是静态方法的全新 E2E 问题，不允许利用 Stage4D labels、OOF probabilities、feature panels 或 decision 来选择 ranking。首次 official source/model/Gold 读取前必须停在协议检查点；当前文档提交不构成执行授权。
