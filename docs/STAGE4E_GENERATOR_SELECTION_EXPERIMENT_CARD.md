# Stage4E-GENSEL 生成模型选择实验卡

状态：`STAGE4E_GENERATOR_SELECTION_AUTHORIZED`  
日期：2026-07-22  
性质：Stage4E official 运行前的开发集模型选择；不是独立测试或模型通用能力排名。

## 1. 研究问题与假设

研究问题：在本项目固定 RTX 4060 Laptop 8GB 环境和 Stage4E 短答案 RAG 提示合同下，`Qwen/Qwen2.5-1.5B-Instruct` 与 `google/gemma-4-E2B-it` 哪个更适合作为唯一冻结生成器？

假设：Gemma 4 E2B 的较新架构可能提高答案 F1，但其 5.1B 总参数和量化运行可能增加兼容性或效率成本。模型选择只由下述冻结开发实验决定，不由厂商通用 benchmark 决定。

## 2. 数据边界

- 输入：`E:\SCIENCE\超粒球RAG_数据\processed\stage2f_hotpotqa_unseen200_unified.json`。
- 身份：1,699,596 bytes；SHA-256 `0818FCB2E130C3BCC207912F59F9ACE14B534321AD93686378E6923FF7405AC5`。
- 样本：HotpotQA development `[200:400)`，200 queries；该切片已在 Stage2F 使用，本次明确降格为 generator-selection development，不再作为未来独立证据。
- 每条输入使用原始 distractor-context 顺序中的完整句子作为 evidence units；两个模型接收相同问题和相同 unit 序列，按各自 tokenizer 执行统一 4,096-token 完整-unit 截断合同。
- runner 只读取拆分后的 blind question/context；Gold answer 仅在两模型 main/rerun 预测冻结后由 evaluator 读取。
- 不读取 Stage4E 1,000-query Gold、reservation、Stage3B、Stage4B/Stage4D labels 或任何新外部 benchmark。

## 3. 模型与运行格式

| 模型臂 | 冻结仓库与 revision | 本机运行格式 |
|---|---|---|
| Qwen | `Qwen/Qwen2.5-1.5B-Instruct@989aa7980e4cf806f80c7fef2b1adb7bc71aa306` | 原官方 BF16 snapshot，以 CUDA FP16 加载 |
| Gemma | `google/gemma-4-E2B-it-qat-mobile-transformers@dd693ff40353f057ca5f07e945ad867f4afbf2ec` | Google 官方 mobile QAT Transformers snapshot；关闭 thinking |

选择 mobile-QAT 是硬件可行性要求：Google 公布的 Gemma 4 E2B BF16 静态权重需求约 11.4GB，超过本机 8GB VRAM；官方 mobile-QAT 是 E2B 的目标设备格式。由此，本实验比较“本项目目标硬件上的可部署生成器”，不分离架构与量化效应。

固定环境沿用 Stage4E：CPython 3.12.0、PyTorch 2.12.1+cu130、Transformers 5.9.0、CUDA 13.0、单 GPU、确定性算法；只允许为 Gemma 官方量化加载补充精确固定的必要运行依赖并记录版本。

## 4. 统一生成合同

- system：`Answer the question using only the provided evidence. Return only the shortest final answer. If the evidence is insufficient, return UNKNOWN.`
- evidence：`[{rank}] {title}: {sentence}`；原始 context/sentence 顺序。
- user：`Evidence:\n...\n\nQuestion: <question>\nFinal answer:`。
- `input_token_cap=4096`、`do_sample=false`、`num_beams=1`、`max_new_tokens=32`、`use_cache=true`。
- 只去除输出首尾空白；不得按 Gold 修复、抽取或重写答案。
- 每模型执行完整 main 与 rerun；200 条 prediction、prompt audit 和输出字节必须分别一致。

## 5. 主要终点与选择规则

主要终点：200-query mean HotpotQA answer F1。次要终点：answer EM、`UNKNOWN` 率、失败调用、总 wall time、tokens/s 与峰值 GPU memory。

固定 evaluator 使用 Stage4E 的 HotpotQA answer normalization/F1/EM 定义，并以 query-paired bootstrap（seed `20260722`，10,000 iterations）报告 `Gemma - Qwen` 的 F1/EM 点估计与 95% percentile interval。

先检查可行性门：模型必须在目标 GPU 完成 200/200 main 与 rerun、零失败、无 OOM/CPU offload、严格输出合同通过且复跑同字节。未通过者直接落选。

若两者均可行，按以下预定顺序选出唯一模型：

1. `abs(mean_F1_Gemma - mean_F1_Qwen) >= 0.010`：选择 mean F1 较高者；
2. 否则若 `abs(mean_EM_Gemma - mean_EM_Qwen) >= 0.010`：选择 mean EM 较高者；
3. 否则选择 main/rerun 平均 wall time 较低者；若差异小于 1%，选择峰值 GPU memory 较低者。

95% interval 用于表达不确定性，不替代上述面向部署的预定选择规则。200 queries 是开发选择样本，不是正式功效保证。

## 6. 停止、完整性与证据不足规则

- 模型 snapshot/revision、输入 SHA、row identity、prompt schema 或 Gold 隔离不符：停止。
- 两模型都不能在 8GB GPU 无 offload 完成：`NO_FEASIBLE_GENERATOR`，停止 Stage4E。
- main/rerun 不一致、evaluator/verifier 重算不一致或输出被部分覆盖：停止并保留失败证据。
- 单模型普通依赖/加载兼容问题可作最小工程修复；若修复改变量化、prompt、解码、数据或评分语义，则停止并修改实验卡。

## 7. 选择后处理

- 胜者成为 Stage4E 唯一生成器；重新绑定 model snapshot、runner、config、environment/model manifests、tests 和当前状态文档。
- 删除落选模型的现行 Stage4E 绑定、专用适配代码及本地模型 snapshot/cache；不得删除本实验卡、冻结 predictions/audits、summary、验证报告或 Git 历史。
- Stage4E official 1,000-query 结果仍须从零生成；本次开发比较不得进入其 Gold evaluator 或答案结果。

## 8. 明确禁止

- 不允许在看到结果后修改 prompt、输入顺序、token cap、decode、score normalization、选择阈值或 bootstrap。
- 不允许增加第三个模型、few-shot、thinking、beam search、answer postprocessor 或量化格式搜索。
- 不允许把该开发选择表述为 Gemma/Qwen 的通用 benchmark 结论。
- 不允许读取 Stage4E Gold、reservation、Stage3B，或借模型选择调整 Dense/q25 检索科学语义。
