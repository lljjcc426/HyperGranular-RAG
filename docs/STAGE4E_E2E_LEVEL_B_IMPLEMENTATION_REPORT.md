# Stage4E-E2E Level B 实现与输入绑定报告

## 结论

```text
STAGE4E_LEVEL_A_PROTOCOL_ACCEPTED
STAGE4E_INPUTS_BOUND
STAGE4E_INPUT_CHANNELS_VERIFIED
STAGE4E_LEVEL_B_IMPLEMENTATION_READY
STAGE4E_SYNTHETIC_TESTS_PASSED
STAGE4E_OFFICIAL_EXECUTION_NOT_AUTHORIZED
STAGE4E_GOLD_EVALUATION_NOT_AUTHORIZED
RESERVATION_REMAINS_LOCKED
STAGE3B_REMAINS_LOCKED
U2_NOT_AUTHORIZED
```

本报告只确认 source/model/environment/config、Level B 代码和 synthetic contracts 已完成。它不包含 official retrieval、embedding、generation、answer metric 或科学结论。

## 输入边界

| 工件 | Bytes | SHA-256 |
|---|---:|---|
| HotpotQA `hotpot_train_v1.1.json` | 566,426,227 | `26650CF50234EF5FB2E664ED70BBECDFD87815E6BFFC257E068EFEA5CF7CD316` |
| blind queries | 6,487,688 | `CB30B9764ADF256A5C5E130F1B78F6AA1EC30613C529FDB554F0F2F29C873958` |
| Gold targets | 500,814 | `7FE6824DA2B46D76DDAF3C0D65C7DBBEC7D0788BD363A4AFC819AAC5F71D6907` |
| descriptive metadata | 187,106 | `CB2DAA864F8B341B186C1DBB7770DF205111CDB8EF54EE3BBABB3A2D370345E2` |
| input manifest | 241,648 | `87C5666D484274BBCDDEC1DA78C4397E9921733736C7D15788197BD72B9EAE32` |

抽样严格使用 `SHA256(UTF8("stage4e_e2e_v1\0" + _id))` 排序前 1,000。与四个登记历史 HotpotQA query 输入的重叠为 0。独立 verifier 从 90,447 条 source rows 重建 selection、三通道逐行身份、context sentence index、supporting-fact unit mapping、通道字节和历史重叠，返回 `STAGE4E_INPUT_CHANNELS_VERIFIED`。

官方 CMU 文件主机在三次有界连接中超时；本地 source 来自固定 revision `7e54db4656209750ff487f6fdf8e39a66dba136b` 的传输镜像，只有在 Bytes 和 SHA-256 与 canonical metadata 完全一致后才提升为 raw source。许可绑定为 CC BY-SA 4.0。

## 模型与环境

- encoder：`sentence-transformers/all-MiniLM-L6-v2@1110a243fdf4706b3f48f1d95db1a4f5529b4d41`；13 个实际 snapshot 文件；file-list digest `766AD566460F0494963F3DF1DEBC5A3B15B219F95C305C54859C2E330C064782`；
- generator：`Qwen/Qwen2.5-1.5B-Instruct@989aa7980e4cf806f80c7fef2b1adb7bc71aa306`；7 个实际 snapshot 文件；file-list digest `29726780E76777165E4E7B462356A18E374FEC4DBFF02A0BC8E4F5ACD09468C4`；
- 环境：CPython 3.12.0、torch 2.12.1+cu130、CUDA 13.0、cuDNN 92000、transformers 5.9.0、NumPy 2.5.1；
- GPU：NVIDIA GeForce RTX 4060 Laptop GPU，8,585,216,000 bytes；
- 确定性：两个 synthetic encoder rerun 的 float32 embedding 同字节；两个 synthetic generator rerun 的 completion token 同字节；
- 精确依赖：`requirements-stage4e.txt`；`pip check` 为 `No broken requirements found`。

环境审计最初两次在未写输出前发现 Transformers 5.9 `BatchEncoding` 返回合同不同于旧接口假设；修正为通用映射取 `input_ids`，并显式传入 attention mask。最终审计通过。该修正同时覆盖正式 runner 和独立 verifier 的 tokenizer 调用，不改变 prompt 文本、token cap、decode kwargs 或科学语义。

## Level B 实现

实现冻结提交：`712077edbe3f85d15da7d4290d294ab05bbdc9fc`。

- `stage4e_e2e_freeze_inputs.py`：deterministic ID selection 与 blind/Gold/metadata 三通道原子冻结；
- `stage4e_e2e_freeze_models.py`：snapshot 实际文件 Bytes/SHA manifest；
- `stage4e_e2e_environment_audit.py`：synthetic-only CUDA/model determinism audit；
- `stage4e_e2e_goldfree_runner.py`：只接受 blind input；复用冻结 Stage4B Gold-free retrieval；固定 Dense/static-q25、prompt、token cap 和 Qwen decode；
- `stage4e_e2e_evaluate.py`：在独立 pre-Gold pass 后才允许读取 Gold；按 pinned HotpotQA answer semantics、paired bootstrap 与冻结门生成 pending decision；
- `stage4e_e2e_independent_verifier.py`：不导入 evaluator；独立完成 input、pre-Gold 和 post-Gold 三阶段重建；
- 所有正式写入使用同目录 pending、身份校验、no-overwrite 和失败回滚。

official config：`configs/stage4e_e2e_official_train1000_v1.json`，16,247 bytes，SHA-256 `59E155A231AD83BFC408C76C2A2D93AFF23C03E35D0519C8E99D0C4ACB453C6D`。其中：

```text
official_execution.authorized = false
gold_evaluation.authorized = false
```

## 测试与验证

定向 suite：19/19 PASS。覆盖：

- Level A 状态与 official lock；
- deterministic sample/channel isolation、历史重叠和 support mapping；
- native JSON type、空 sentence index、ambiguous mapping；
- no-overwrite 与 multi-file rollback；
- blind unit 构造与原 sentence index；
- official/Gold authorization 在输入打开前 fail closed；
- query-hash method order；
- Transformers 5.9 mapping-style chat-template output；
- 4096-token cap、rank-1 truncation 和 prompt 无 method marker；
- pinned Hotpot answer EM/F1；
- evaluator/verifier 独立 score 一致；
- paired bootstrap determinism 与三类 scientific decision gate。
- config/implementation/model/environment binding 与双授权锁；
- official 输出在首次运行前均不存在，只有 input verification 已生成。

执行记录：

```powershell
& 'temp\stage4e_env\Scripts\python.exe' -m pip check
& 'temp\stage4e_env\Scripts\python.exe' -B -m unittest discover -s tests -p 'test_stage4e_e2e.py' -v
```

input verifier 工件为 1,309 bytes / `B3A3B0CBCFD2A33474172AEFFF902B74106074267E7CDCE690A432B68BDA007E`。

## 下一授权边界

下一步只能在用户确认精确命令后把 config 的 `official_execution.authorized` 和 transaction confirmation digest 更新为已授权值，然后连续执行：

```text
main Gold-free retrieval/generation
→ rerun Gold-free retrieval/generation
→ prediction/prompt byte identity
→ independent pre-Gold verification
→ Git synchronization
→ 在首次 Gold 读取前暂停
```

Gold evaluator、reservation、Stage3B、U2 和任何科学语义修改均不在当前授权内。
