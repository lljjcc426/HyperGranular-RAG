# 超粒球 RAG Stage 0 数据探针报告

## Material Passport

- 项目方向：自适应粒球作为知识单元 + 边界不确定性驱动检索决策
- 当前阶段：Stage 0 Dataset Probe
- 日期：2026-07-08
- 执行范围：HotpotQA dev distractor + MuSiQue ans dev
- 目标：确认首轮数据集是否可下载、可解析、可映射 gold evidence，并生成统一样本格式

## 1. 本次执行结论

Stage 0 已跑通。HotpotQA 和 MuSiQue 都能支撑第一轮 retrieval-only MVP。

核心结论：

- HotpotQA dev distractor 已下载成功，并解析出 7405 条原始样本。
- MuSiQue v1.0 官方 zip 已下载成功，并解析出 2417 条 ans dev 样本。
- 两个数据集各抽样 200 条，均已转换为统一 JSON 格式。
- gold evidence 文本映射成功，抽样中没有空 evidence 文本。
- 这两个数据集可以进入下一步：固定 chunk baseline 与粒球检索 baseline。

## 2. 数据下载与来源

### HotpotQA

- 官方主页：https://hotpotqa.github.io/
- 官方 GitHub：https://github.com/hotpotqa/hotpot
- 论文页：https://aclanthology.org/D18-1259/
- 官方源尝试：`http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json`
- 实际结果：官方源本次返回 502 Bad Gateway。
- 备用源：Hugging Face 镜像 `namlh2004/hotpotqa`
- 本地文件：`E:\科研\超粒球RAG_数据\raw\hotpot_dev_distractor_v1.json`
- 文件大小：61065698 bytes

### MuSiQue

- 官方 GitHub：https://github.com/stonybrooknlp/musique
- 论文页：https://aclanthology.org/2022.tacl-1.31/
- 官方下载脚本：`download_data.sh`
- 官方 Google Drive 文件 ID：`1tGdADlNjWFaHLeZZGShh2IRcpO6Lv24h`
- 本地 zip：`E:\科研\超粒球RAG_数据\raw\musique\musique_v1.0.zip`
- zip 文件大小：272049578 bytes

## 3. 本地文件

### 原始数据

| Dataset | File | Size |
|---|---|---:|
| HotpotQA | `E:\科研\超粒球RAG_数据\raw\hotpot_dev_distractor_v1.json` | 61065698 |
| MuSiQue zip | `E:\科研\超粒球RAG_数据\raw\musique\musique_v1.0.zip` | 272049578 |
| MuSiQue ans dev | `E:\科研\超粒球RAG_数据\raw\musique\data\musique_ans_v1.0_dev.jsonl` | 30439728 |
| MuSiQue full dev | `E:\科研\超粒球RAG_数据\raw\musique\data\musique_full_v1.0_dev.jsonl` | 59422562 |

### 统一样本

| Dataset | Unified Sample | Rows |
|---|---|---:|
| HotpotQA | `E:\科研\超粒球RAG_数据\processed\hotpotqa_dev_distractor_sample200_unified.json` | 200 |
| MuSiQue | `E:\科研\超粒球RAG_数据\processed\musique_ans_dev_sample200_unified.json` | 200 |

### 探针报告

| Dataset | Report |
|---|---|
| HotpotQA | `E:\科研\超粒球RAG_数据\reports\hotpotqa_stage0_probe.md` |
| MuSiQue | `E:\科研\超粒球RAG_数据\reports\musique_ans_stage0_probe.md` |

## 4. 字段诊断

### HotpotQA

- 原始样本数：7405
- 抽样统一样本数：200
- 原始字段：`_id`, `answer`, `question`, `supporting_facts`, `context`, `type`, `level`
- 平均 context 数：9.96
- 平均 gold evidence 数：2.44
- 抽样缺失 gold evidence 的样本数：0
- gold evidence 总数：487
- gold evidence 空文本数：0

判断：HotpotQA 的 sentence-level supporting facts 可以直接用于 supporting fact recall。

### MuSiQue

- 原始 ans dev 样本数：2417
- 抽样统一样本数：200
- 原始字段：`id`, `paragraphs`, `question`, `question_decomposition`, `answer`, `answer_aliases`, `answerable`
- 平均 context 数：20.00
- 平均 gold evidence 数：2.00
- 抽样缺失 gold evidence 的样本数：0
- gold evidence 总数：400
- gold evidence 空文本数：0

判断：MuSiQue 的 paragraph-level support 信息可以用于 evidence chain recall；`question_decomposition` 后续可用于分析跨粒球推理链。

## 5. 统一格式

当前统一样本格式如下：

```json
{
  "id": "...",
  "dataset": "...",
  "question": "...",
  "answer": "...",
  "contexts": [
    {
      "doc_id": "...",
      "title": "...",
      "sentences": ["..."]
    }
  ],
  "gold_evidence": [
    {
      "doc_id": "...",
      "sentence_id": 0,
      "text": "..."
    }
  ],
  "metadata": {}
}
```

## 6. 当前限制

- HotpotQA 本次未从官方 CMU 源下载成功，而是使用 Hugging Face 镜像；论文中正式实验时应记录数据来源与校验方式。
- MuSiQue 当前探针使用 `musique_ans_v1.0_dev.jsonl`，尚未比较 `musique_full_v1.0_dev.jsonl` 是否更适合 retrieval-only。
- 当前只抽样 200 条，用于字段探针，不代表最终实验统计结果。
- 还没有构建 chunk、embedding、粒球或超边。

## 7. 下一步

进入 Stage 1 Retrieval-only MVP。

建议执行顺序：

1. 写 `stage1_build_corpus.py`：把统一样本展开为 evidence units/chunks。
2. 写 `stage1_dense_baseline.py`：先做 fixed chunk + TF-IDF/BM25 或 embedding top-k baseline。
3. 写 `stage1_granular_ball_index.py`：在 embedding space 生成初版语义粒球。
4. 写 `stage1_eval_retrieval.py`：计算 supporting fact recall、evidence chain recall、context token count。
5. 只在 retrieval 指标稳定后再接 LLM 生成。

推荐先做最小 baseline：

- 数据：HotpotQA sample200 + MuSiQue sample200
- 检索器：TF-IDF baseline
- 指标：Recall@5、Recall@10、gold evidence recall、context count

