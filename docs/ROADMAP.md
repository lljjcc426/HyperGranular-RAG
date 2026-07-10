# Roadmap

## Material Passport

- Project: HyperGranular-RAG
- Current stage: Stage2D completed
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

## Next Experiment: Stage2E Evidence-Aware Noise Control

Stage2D 证实保护式插入能提高 CR@10/CR@20，但 false insert rate 仍高。下一步应针对插入候选做更强约束，而不是继续增加插入预算。

建议实验：

1. 只允许 boundary query 触发插入，同时比较 non-boundary query 的稳定性。
2. 对插入候选加入 dense score floor、facet score floor、seed similarity floor。
3. 对 insert_budget=1/2/4 分别报告 CR 增益和 false insert rate。
4. 做 query-level 审计：新增完整证据链的 query 与被破坏完整证据链的 query 分别列出。
5. 如果 false insert 无法下降，把论文主张收窄为 protected evidence completion，而不是 noise suppression。
