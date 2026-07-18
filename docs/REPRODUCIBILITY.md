# Reproducibility

本文件只保留当前有效的复现入口。完整历史命令与旧治理链快照见 [归档版本](archive/REPRODUCIBILITY_PRE_REORGANIZATION_2026-07-18.md)。

## 当前复现状态

```text
VERIFIED_POST_GOLD
STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED
RESERVATION_REQUIRES_PAUSE
```

Pre-Gold 和本次获授权的 Gold evaluation 均已完成，不应重复运行。主运行与预注册复跑同字节，独立验证器已重建 4,500 条逐查询审计、汇总和 development 决策。

## 运行环境

```text
Python: D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe
Version: 3.12.0
NumPy: 2.5.1
```

当前 direct entry point 使用普通脚本目录导入，只保留 `-B`；不要加入会移除 sibling-module 路径的 `-I`。

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

这两个文件位于登记数据目录 `E:\科研\超粒球RAG_数据\processed`，不提交 Git。Gold 在 decisions、rankings、policy 和 `VERIFIED_PRE_GOLD` 冻结后才由 evaluator 读取。

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

## 后续复现边界

本次 Gold transaction 已结束且失败停止规则已触发：

1. 不重复运行该 transaction；
2. 不在同一 development 上修改特征、公式、预算、阈值、排序或检验后重跑；
3. 不由该结果打开 reservation 或 Stage3B；
4. 后续新研究必须先形成独立问题、协议、样本边界和停止规则，再读取新结果；
5. Reservation、Stage3B、再次 Gold 执行和科学语义修改仍需单独协议与明确授权。

本次冻结负结果只否定当前 U1-D controller 的晋级主张，不否定 HyperGranular-RAG 整体研究方向。后续新 controller 必须作为新的科学语义和新的 development 协议处理。
