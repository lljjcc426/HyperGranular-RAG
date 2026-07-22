# Stage4E 生成模型选择报告

日期：2026-07-22  
状态：`STAGE4E_GENERATOR_SELECTION_VERIFIED`  
结论：`SELECT_QWEN2_5_1_5B_INSTRUCT`

## 1. 研究问题与边界

本实验在项目实际部署环境 NVIDIA GeForce RTX 4060 Laptop GPU 8GB 上，对比：

- `Qwen/Qwen2.5-1.5B-Instruct@989aa7980e4cf806f80c7fef2b1adb7bc71aa306`，CUDA FP16；
- `google/gemma-4-E2B-it-qat-mobile-transformers@dd693ff40353f057ca5f07e945ad867f4afbf2ec`，Google 官方 mobile-QAT Transformers 形式，关闭 thinking。

实验严格使用冻结实验卡定义的 HotpotQA development 200-query 边界、相同 Stage4E 短答案提示合同、各模型自身 tokenizer 的 4,096-token 上限、greedy decoding 和 32 个最大新 token。该数据此前已用于项目开发，因此本实验仅作生成器选择，不构成独立 efficacy 证据，也不进入 Stage4E 正式 1,000-query 结果。

冻结 source：1,699,596 bytes，SHA-256 `0818FCB2E130C3BCC207912F59F9ACE14B534321AD93686378E6923FF7405AC5`。Gold 与 blind channel 分离；生成器只读取 blind channel，两个模型的 main/rerun 工件冻结后才由 evaluator 读取 Gold。

## 2. 固定环境与确定性

- CPython 3.12.0；
- PyTorch 2.12.1+cu130；
- Transformers 5.14.1；
- safetensors 0.8.0；
- Pillow 12.3.0；
- torchvision 0.27.1+cu130；
- 单 GPU、单线程 BLAS/OpenMP、`CUBLAS_WORKSPACE_CONFIG=:4096:8`；
- 两个模型均完成 200/200 queries，无 OOM、CPU offload 或 query failure；
- 两个模型的 predictions 与 prompt audit 均实现 main/rerun 字节一致；
- 独立 verifier 重建数据通道、指标、10,000 次 paired bootstrap 和冻结选择规则，返回 `STAGE4E_GENERATOR_SELECTION_VERIFIED`。

Transformers 5.9.0 不能识别 Gemma 官方量化 snapshot 的 `quant_method`，该兼容性问题发生在任何正式 query 输出前。环境随后精确固定到 Transformers 5.14.1，并重新从零执行两个模型的完整事务；它不改变提示、数据、指标或选择规则。

## 3. 结果

| 模型 | Answer F1 | Answer EM | main/rerun 平均 wall time | peak GPU memory |
|---|---:|---:|---:|---:|
| Qwen2.5-1.5B-Instruct | **0.440913** | **0.320000** | **170.925 s** | **5,264,665,600 bytes** |
| Gemma 4 E2B mobile-QAT | 0.335698 | 0.245000 | 1,782.282 s | 7,930,366,464 bytes |

配对差值以 `Gemma - Qwen` 表示：

- Answer F1：`-0.105214`，95% percentile interval `[-0.180537, -0.028153]`；
- Answer EM：`-0.075000`，95% percentile interval `[-0.150000, 0.000000]`；
- bootstrap：10,000 iterations，seed `20260722`。

冻结规则首先检查绝对 F1 差是否至少为 0.010。本次差值为 0.105214，故在第一条规则直接选择 Qwen；效率和显存结果只作补充，不参与覆盖该决定。

## 4. 科学解释

结论限定为：在本项目固定提示、固定 200-query development 边界、RTX 4060 Laptop 8GB 和可部署格式下，Qwen2.5-1.5B-Instruct 是 Stage4E 更合适的唯一生成器。

该结果不能推出：

- Qwen 在其他任务、硬件、prompt 或数据上普遍优于 Gemma；
- Gemma 4 架构本身低于 Qwen，因为本机只能运行官方 mobile-QAT 形式，架构与量化效应未被分离；
- 当前分数是 Stage4E 的正式 Dense-vs-q25 端到端结果；
- 生成器差异解释了 HyperGranular-RAG 检索方法的因果效应。

## 5. 偏差与谬误检查

1. 数据复用：明确标记为 development model selection，不当作独立验证。
2. 事后规则：选择门、主次指标和 bootstrap 在运行前冻结，未按结果修改。
3. 多重搜索：只比较用户指定的两个模型，没有追加模型或超参数搜索。
4. Gold 泄漏：runner 只读取 blind channel；Gold 在模型工件冻结后进入 evaluator。
5. 量化混杂：Gemma 使用官方 mobile-QAT，报告中不把结果解释为纯架构比较。
6. 硬件外推：结论限定于 RTX 4060 Laptop 8GB。
7. 统计夸大：报告点估计和区间，不把 bootstrap 区间写成模型普遍优越证明。
8. 选择性报告：F1、EM、时间、显存和两个模型完整 main/rerun 均保留。
9. 确定性：只以字节一致的 predictions/audit 为确定性证据，不以 `random_state` 或单次运行代替。
10. 因果归因：没有把生成器对比解释成检索器或超边方法的因果结论。
11. 失败隐藏：记录了运行前的 Transformers 兼容性问题及其零输出边界。

## 6. 后续处置

- Stage4E 当前生成器继续绑定 Qwen2.5-1.5B-Instruct；
- Gemma 不进入 Stage4E active config、runner、requirements 或模型缓存；
- Gemma 的实验卡、predictions、prompt audit、telemetry、逐 query scores、summary、独立验证与本报告永久保留为对比证据；
- 后续 Stage4E 正式实验不得依据本开发集再选择生成器。

