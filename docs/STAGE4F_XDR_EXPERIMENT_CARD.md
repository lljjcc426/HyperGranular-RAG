# Stage4F-XDR：静态 HyperGranular-RAG 跨数据集端到端复制实验卡

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: plan
- Origin Date: 2026-07-22
- Verification Status: SOURCE AND INPUT BOUNDARY VERIFIED; OFFICIAL EXECUTION NOT AUTHORIZED
- Version Label: stage4f_xdr_v1
- Status: `STAGE4F_XDR_EXPERIMENT_CARD_FROZEN`

## 1. 唯一问题与解释边界

唯一问题：Stage4E 在 HotpotQA new-ID closed distractor 上观察到的 static all-query q25 protected insertion 相对 Dense Top-20 的 answer-F1 增益，能否在此前未用于该 E2E 结论、具有多跳问题和明确证据标注的 MuSiQue 上复现？

本实验只比较 `DENSE_TOP20` 与 `STATIC_Q25_TOP20`。它不是模型、prompt、K、q25 参数或 subgroup 搜索，不开发 U1/U2、controller、candidate selector，也不评价 full-wiki/open-domain。Stage4E、Reservation 和 Stage3B 工件不读取、不覆盖。

## 2. 官方来源、许可证与新 ID 边界

主数据集固定为 MuSiQue-Answerable v1.0 train。作者仓库为 `StonyBrookNLP/musique@922ac98f19a201998dbdae6d7f2887a5258dbdeb`，官方下载脚本绑定 Google Drive 文件 `1tGdADlNjWFaHLeZZGShh2IRcpO6Lv24h`，许可证为 CC BY 4.0，下载/核验日期为 2026-07-22。

| 对象 | Bytes | SHA-256 / 规模 |
|---|---:|---|
| `musique_v1.0.zip` | 272,049,578 | `98F839BF2FD5319F5C688AED77901A6D5C30B3B9F9F691AB9A8ECAFB045EE0CD` |
| `musique_ans_v1.0_train.jsonl` | 241,046,755 | `83A75B1E11E4E9BB8F8308E72AC40CA617AE4431B3A0D955B61CAB259248490A` |
| train schema | 19,938 rows | 19,938 个唯一原生 ID；字段含 `id/question/paragraphs/question_decomposition/answer/answer_aliases/answerable` |
| 官方 evaluator | 4,257 | `evaluate_v1.0.py` SHA `F5FE66AE...E74B7` |
| 官方 answer metric | 2,837 | `metrics/answer.py` SHA `10368F61...FE974` |

历史 MuSiQue 正式输入完整边界为 answerable dev `[0:1000)`：Stage0/1 `[0:200)`、Stage2F `[200:400)`、Stage2G `[400:600)`、Stage3A `[600:1000)`，共 1,000 个唯一原生 ID，排序后摘要为 `8521C1F623B7C15601A76CBFE52164E64B6D090C269C152F04100E4B86993E5B`。Stage3B dev `[1000:1400)` 保持锁定且未读取。官方 train 与上述 1,000 个历史 ID 的交集为 0。

样本量固定为 3,000。样本选择只使用 dataset 与原生 ID，不使用 answer、support 或 metadata：

```text
SHA256(UTF8("stage4f_xdr_v1\0" + dataset + "\0" + native_query_id))
```

按 `(digest, native_query_id)` 升序取前 3,000；不合格 Gold 不以后续行替换，而是整项事务停止。选择顺序的原生 ID 摘要为 `7B0111DE65479428E2686A9E116F18D1AB0B1AB8A688103AD4CF53E6DCC14A74`，历史交集为 0。

### Candidate-unit 兼容性

MuSiQue 每题固定 20 个段落；若整段作为单元，两臂在 Top-20 会退化为同一全集。为继承 Stage4E 的句子单元语义，Stage4F 在任何 Gold 读取前使用冻结的 `stage4f_regex_sentence_splitter_v1`：规范空白后，在 `[.!?]`（可带结束引号）与下一英文大写字母/数字起始片段之间切分。unit ID 为 `query_id::p<paragraph_idx>::s<sentence_idx>`。

该规则不声称是语言学最优分句，只是预注册、确定且 source-only 的候选构造。3,000 个冻结 query 共有 218,698 个单元，单题 27–151、均值 72.90；因此 Top-20 两臂可定义。官方 Gold 仍严格解释为 supporting paragraph：ER/CR 以 Top-20 是否覆盖 supporting paragraph 计算。MuSiQue v1.0 没有 supporting-sentence 标注，`supporting_fact_sentence_recall` 必须报告为 unavailable，不得把 supporting paragraph 内所有句子伪称为 supporting facts。

## 3. 固定方法、模型与通道

`DENSE_TOP20` 使用 `sentence-transformers/all-MiniLM-L6-v2@1110a243fdf4706b3f48f1d95db1a4f5529b4d41`，max length 192、cosine-normalized float32 embeddings、float64 科学标量，按 `(-score, unit_id)` 排序，`K_q=min(20,candidate_count)`。

`STATIC_Q25_TOP20` 完整继承 Stage4E：ball size 2–3、radius 0.78、depth 6、boundary 0.20、center terms 8、seed balls 2、facet edges 2、expanded balls 2、new terms 1、facet score 0.10、candidate ball size 8、ball score 0.12、seed similarity 0.05、units/new-term 6.0、redundancy 0.90、权重 `0.45/0.20/0.20/0.15/0.20/0.05`、facet unit bonus 0、q25 floor `0.1957079917192459`、protected prefix 10、insert budget 4、effective-K 20。兼容性审计允许；参数重调禁止。

唯一生成器为 `Qwen/Qwen2.5-1.5B-Instruct@989aa7980e4cf806f80c7fef2b1adb7bc71aa306` FP16。system prompt 固定为：

```text
Answer the question using only the provided evidence. Return only the shortest final answer. If the evidence is insufficient, return UNKNOWN.
```

输入上限 4096，`do_sample=false`、`num_beams=1`、`max_new_tokens=32`、`use_cache=true`、batch 1；只 strip 首尾空白。环境固定为 Stage4E 已验证的 CPython 3.12.0 / torch 2.12.1+cu130 / transformers 5.14.1 / NumPy 2.5.1 / RTX 4060 Laptop 8 GB 与单线程变量；Stage4F 重新核验相同 snapshot 的逐文件 Bytes/SHA。

通道隔离：A 仅含 identity、question、candidate units；B 仅含 identity、answer/aliases、official supporting paragraph 与其 unit 映射；C 仅含 hop count、source row、候选池等描述性 metadata。A 驱动 embedding、ranking、prompt、generation；B 只在 Gold 阶段开启；C 只在总指标、bootstrap 和 decision 已冻结后开启并标记 `SUBGROUP_CAUTION`。

## 4. 主要终点、判定与次要报告

统计单位为 query。主要终点为 `mean(F1_STATIC_Q25 - F1_DENSE)`；supportive guard 为 EM delta。答案评分逐项复现 MuSiQue 官方 `metrics/answer.py`：lowercase、删除 ASCII punctuation、删除 `a/an/the`、压缩空白，对主答案与 aliases 分别取最大 EM/F1。主统计使用未四舍五入的 query 分数；同时可对账官方脚本的三位小数 aggregate。

paired query bootstrap 固定为 10,000 次、PCG64 seed `20260723`、95% percentile interval：

```text
STATIC_HGRAG_XDR_SUPPORTED:
  delta F1 >= 0.010 and F1 lower > 0 and EM lower >= -0.010
STATIC_HGRAG_XDR_NEGATIVE:
  F1 upper < 0 or EM upper < -0.010
STATIC_HGRAG_XDR_INCONCLUSIVE:
  otherwise
```

次要完整报告 answer F1/EM、UNKNOWN rate、supporting-paragraph ER@20/CR@20、q25 insert count、gain/same/harm query、input tokens、included units、truncation、wall time、GPU peak、failed calls、main/rerun determinism；句子级 Gold recall 明确为不可用。任何次要项不得替代主要判定。

## 5. 样本与资源边界

3,000 是资源与精度边界，不是正式 power guarantee。Stage4E 的 1,000-query F1 区间半宽约 0.01484；若 query-level 方差相近，按 `1/sqrt(n)` 缩放到 3,000 的近似半宽约 0.00857，因此对真实 `+0.01` 有一定分辨能力，但数据集迁移后的方差未知。

正式 main/rerun 共 `3,000 × 2 arms × 2 = 12,000` 次生成。Stage4E 实测每 2,000 calls 为 854.83 秒和 767.34 秒，线性基准约 81 分钟；考虑 218,698 个候选单元的 embedding、MuSiQue 文本长度和验证，预留 2–3 小时。Stage4E generator 峰值约 3.51 GB，模型/设备不变；embedding cache 原始 float32 向量约 0.34 GB，实际文件另含 ID/metadata。上述均是资源估算，不是性能或功效承诺。

## 6. 事务、停止与当前授权

正式事务预定义为：input identity → Gold-free main/rerun → byte identity → independent pre-Gold verification → Gold scoring/bootstrap/decision → independent final verification → Channel C descriptive report → Git/remote bytes。no-overwrite、`.pending` guarded promotion 与失败回滚为硬合同。

source/license/schema、历史 overlap、Gold leakage、support mapping、candidate pool、snapshot、main/rerun、query pairing、failed call、OOM/CPU offload、verifier 或 artifact identity 任一失败即停止且不生成科研决策。工程修复不得改变数据、模型、ranking、prompt、K、floor、指标、bootstrap 或门。

当前只授权输入绑定、Level B 与纯 synthetic tests。正式 embedding、ranking、generation、Gold、bootstrap、decision 和 Channel C 读取均未授权；配置必须保持 `official_execution.authorized=false` 与 `gold_evaluation.authorized=false`。

