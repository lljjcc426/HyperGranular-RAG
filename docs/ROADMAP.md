# Roadmap

## Material Passport

- Project: HyperGranular-RAG
- Current stage: Stage2G protocol frozen before mechanism test evaluation
- Data used so far: HotpotQA sample200 + MuSiQue sample200
- Generator used: No
- Gold labels used for indexing: No

## Completed

1. Stage0 数据探针：确认 HotpotQA 与 MuSiQue 可统一成 evidence-intensive QA 格式。
2. Stage1 固定 TF-IDF 基线：ALL CR@10 = 0.3125。
3. Stage1 粒球基线：单纯粒球替代固定检索没有优势。
4. Stage1 facet-aware 超边：ALL CR@10 = 0.3725。
5. Stage1 boundary gated 超边：保持 CR@10 = 0.3725，并降低 false expansion。
6. Stage2A bootstrap：Stage1F 相对 TF-IDF 的 ALL CR@10 增益为 +0.0600，95% CI [0.0125, 0.1050]。
7. Stage2B dense 复现：dense fixed 明显更强，原始 dense gated 不能替代 dense fixed。
8. Stage2C dense 保护策略：fill/protect 策略显示 Top-20 证据补全价值。
9. Stage2D protected dense reranking：保护 dense fixed 前缀后插入预算化超边扩展单元。ALL dense fixed CR@10/CR@20 = 0.5625/0.8250；facet protect=5 insert=2 达到 CR@10 = 0.6125；facet protect=10 insert=8 达到 CR@20 = 0.9000；gated protect=5 insert=2 达到 CR@10 = 0.6100。

## Completed Experiment: Stage2D Protected Dense Reranking

目标：验证“边界不确定性驱动的超粒球扩展”是否能在不破坏 dense Top-k 主干的情况下提升证据链召回。

实验条件：

- Baseline: dense fixed
- Candidate expansion: facet hyperedge, gated hyperedge
- Protection zone: fixed Top-5, Top-10
- Insertion zone: ranks 6-20 或 11-20
- Budgets: K=10, K=15, K=20

必须报告：

- ER@K
- CR@K
- Hit@K
- MRR
- context_units@K
- context_tokens@K
- false_expansion_rate
- query-level improved/same/regressed counts
- HotpotQA/MuSiQue split metrics

判定门槛：

- 若 CR@10 不低于 dense fixed，且 CR@20 明显高于 dense fixed，可主张“protected evidence completion”。
- 若 CR@10 下降，则不能写成 dense 检索增强，只能写成长上下文补全策略。
- 若 false expansion 仍高，需要把门控目标改为“预算内证据完成”，而不是“噪声显著抑制”。

## Engineering Tasks

1. 把脚本中的本地绝对路径全部参数化。
2. 增加 `configs/`，保存 Stage1F、Stage2C、Stage2D 的参数。
3. 增加一键运行脚本，只复现 summary CSV，不默认生成大体积 JSONL。
4. 增加结果校验脚本，检查报告中的关键数字是否能从 CSV 复算。
5. 在 README 中补数据下载和处理步骤。

## Completed Experiment Plan: Stage2E Evidence-Aware Noise Control

Stage2D 证实保护式插入能提高 CR@10/CR@20，但 false insert rate 仍高。下一步应针对插入候选做更强约束，而不是继续增加插入预算。

建议实验：

1. 只允许 boundary query 触发插入，同时比较 non-boundary query 的稳定性。
2. 对插入候选加入 dense score floor、facet score floor、seed similarity floor。
3. 对 insert_budget=1/2/4 分别报告 CR 增益和 false insert rate。
4. 做 query-level 审计：新增完整证据链的 query 与被破坏完整证据链的 query 分别列出。
5. 如果 false insert 无法下降，把论文主张收窄为 protected evidence completion，而不是 noise suppression。

## Stage2E Observed Results

- 候选池：gated expansion 共 1,024 个单元；dense score q25/q50/q75 为 0.1957/0.3167/0.4231，facet score q50 为 0.2221。
- 无筛选 `protect=5, insert=2` 完全复现 Stage2D：CR@10/CR@20 = 0.6100/0.8425，false insert = 0.8727。
- `score_q25, protect=5, insert=4`：CR@10/CR@20 = 0.6125/0.8700，false insert = 0.8774；相对无筛选 insert=4 的 0.8984 有下降。
- `score_q25, protect=10, insert=4`：CR@20 = 0.8825，false insert = 0.8733。
- `score_q50, protect=5, insert=2`：CR@10/CR@20 = 0.5950/0.8375，false insert = 0.8407；噪声更低，但插入量与召回增益同时下降。
- `score_q50 + facet_q50, protect=5, insert=2` 将 false insert 降至 0.7456，但平均每查询仅插入 0.285 个单元，不能单独作为噪声抑制成功证据。
- HotpotQA 的 dense fixed CR@20 为 0.6500，仍有补全空间；MuSiQue 的 dense fixed CR@20 已为 1.0000，Top-20 指标饱和。

结论边界：Stage2E 支持轻度 score filter 改善 protected evidence completion 的精度-召回折中；由于分位阈值与评测共享同一批 400 queries，尚未通过独立测试。

## Completed Experiment: Stage2F Frozen-Threshold Validation

Protocol frozen in `docs/STAGE2F_PROTOCOL.md` before reading Stage2F test metrics.

1. 按数据集分层固定开发集/测试集，开发集只负责选择阈值，测试集只做一次最终报告。
2. 优先比较 dense fixed、unfiltered gated、`score_q25` 和 `score_q50`，固定 protect/insert 组合，避免继续扩大搜索空间。
3. 对 CR@10、CR@20、ER@10、ER@20、false insert 和平均插入数做 paired bootstrap 置信区间。
4. 分开报告 HotpotQA 与 MuSiQue；对已饱和的 MuSiQue CR@20 改看 CR@10、证据召回与上下文成本。
5. 若冻结阈值后增益不能复现，论文主张回退到“探索性的受保护证据补全机制”。

## Stage2F Observed Results

- Independent test: HotpotQA `[200:400)` + MuSiQue `[200:400)`, 400 queries, 12,333 candidate units, 882 gold units, calibration overlap = 0.
- Primary q25 p5/i4 vs dense fixed CR@10 delta = +0.0175, 95% CI [-0.0125, 0.0475]: NOT SUPPORTED.
- q25 p5/i4 vs unfiltered p5/i4 false-insert delta = -0.0129, 95% CI [-0.0206, -0.0055], with observed CR@10 delta +0.0075: SUPPORTED under the frozen gate.
- q25 p10/i4 vs dense fixed CR@20 delta = +0.0175, 95% CI [0.0025, 0.0350]: SUPPORTED.
- q50 p5/i2 vs unfiltered p5/i2 false-insert delta = -0.0512, 95% CI [-0.0783, -0.0259], with CR@10 delta -0.0025: exploratory precision-recall trade-off.
- Dataset split: HotpotQA contributes the CR@20 gain (+0.0350); MuSiQue CR@20 is saturated at 1.0000.
- Reproducibility: deterministic rerun produced byte-identical summary and bootstrap CSV files.
- Validation confidence: CAUTION because the primary endpoint failed, supported effects are small, and external validity remains limited to the same datasets and encoder.

## Next Experiment: Stage2G Boundary-Decision Mechanism Audit

Protocol frozen in `docs/STAGE2G_PROTOCOL.md` before extracting or evaluating the `[400:600)` test slice.

1. Freeze a new unseen slice before evaluation, preferably source rows `[400:600)` for both datasets.
2. Compare dense fixed, all-query expansion, and boundary-only expansion under the same frozen q25 score floor and insertion budget.
3. Primary mechanism endpoint: whether boundary-only triggering lowers false insert relative to all-query expansion without reducing CR@20.
4. Report trigger coverage, positive-chain-completion precision, ER/CR, context tokens, and dataset-specific bootstrap intervals.
5. Do not search new score thresholds in Stage2G; threshold optimization, if needed, belongs to a separate development stage.
