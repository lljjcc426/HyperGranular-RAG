# Reproducibility

本文件只保留当前有效的复现入口。完整历史命令与旧治理链快照见 [归档版本](archive/REPRODUCIBILITY_PRE_REORGANIZATION_2026-07-18.md)。

## 当前复现状态

```text
VERIFIED_PRE_GOLD_COMMITTED
GOLD_EVALUATION_REQUIRES_PAUSE
RESERVATION_REQUIRES_PAUSE
```

Pre-Gold 流程已经完成，不应在没有新科研理由时重复运行。

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
| `docs/STAGE4B_U1_SIMPLIFIED_EXECUTION_PROTOCOL_V1.md` | `ABED88FAC906748CE9D93F04C0D4BA35B62BB6819F61A2D84273687BE35C724C` |
| `scripts/stage4b_u1_evaluate.py` | `D7B96E29AD5AB2F6652FFC14D73048D36C205F78ABA7FA8FCB501818A1A89BBB` |

Config 继续绑定 implementation commit `8ab5e193d00733e0ae617b2c17f02da4ce01594f` 及七个 implementation 文件 SHA。Evaluator `authorized=false`；config 不含 Gold map、Gold hash、reservation 或 Stage3B 输入。

## 冻结 pre-Gold 工件

| 工件 | Bytes | SHA-256 |
|---|---:|---|
| `results/stage4b_u1_d_official_dev4500_simplified_v1_decisions.jsonl` | 2,684,439 | `4B2AD2E5707B20FD46B6250FDA5395433F52E55FB1281F1499412C8C749A456A` |
| `results/stage4b_u1_d_official_dev4500_simplified_v1_rankings.jsonl` | 18,235,604 | `ED289D234F6F4FEC58A48168CB6CA78950489CD5F5640E977068CA6A786E03CB` |
| `results/stage4b_u1_d_official_dev4500_simplified_v1_policy.json` | 261,587 | `657E5F25A94224D8B020780F3E7335942B16BC6D8C7939FB74D1BBAA9A9D868B` |
| `results/stage4b_u1_d_official_dev4500_simplified_v1_verified_pre_gold.json` | 3,479 | `39EAD86A3A835983DCB67BAF656255F51569BCEE5B9AC2E16FACF404281D7818` |

三项 controller 工件提交：`9357c157217f85008fa93df07d321a2f4c6a2bc1`。

Verified 单路径提交：`83d172bc89efbb31782eee308bac5293aa24457b`。

## 已完成命令

以下命令是已完成流程的复现记录，不是当前重跑指令：

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

Verified 文件记录 `gold_inputs_loaded=false`、`evaluation=null`，全部 checks 为 `PASS`。Gold query audit 与 evaluation summary 不存在。

## 测试证据

- Strict-row-contract 定向测试：18/18 PASS。
- 最终 `test_stage4b_u1*.py` suite：277/277 PASS，完整 suite 只运行一次。
- 本轮仓库整理不改代码、配置、协议或结果，不需要运行算法 suite。

## 后续复现边界

进入 Gold evaluation 前必须：

1. 获得用户单独明确授权；
2. 只向 evaluator 提供 Gold 专属输入；
3. 保持 controller、rankings、policy 与 verified 工件冻结；
4. 版本化记录 Gold 输入身份、evaluator 命令、query audit 和 evaluation summary；
5. 完成独立统计核验、11 类谬误检查和协议要求的确定性复跑。

Reservation、Stage3B 和任何科学语义修改仍需单独协议或授权。
