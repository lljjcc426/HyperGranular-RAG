# Roadmap

## Material Passport

- Project: HyperGranular-RAG
- Current stage: Stage4A-R2 precision-based official event-rate protocol approved and frozen before extraction; no R2 metrics yet; Stage3B remains locked
- Data used so far: HotpotQA and MuSiQue development slices; invalidated 2Wiki mirror pilot; official April 7 archive used for source reconciliation only; no restarted Stage4A metrics
- Generator used: No
- Gold labels used for indexing: No

## Prior-stage Audit Decision

The full integrity and methodology audit is recorded in `docs/PRIOR_STAGE_METHOD_AUDIT.md` and `docs/PRIOR_STAGE_AUDIT.json`.

- Computational integrity through Stage3C: passed, including disjoint slice checks, zero missing gold, no gold-driven retrieval selection, and byte-identical reruns for Stage2F-Stage3C.
- Stage0-Stage2E: reproducible exploratory development only because no independent pre-result protocol was committed.
- Stage2F: narrow internal evidence only; the primary CR@10 gate failed and the 400-query test had no a priori power calculation.
- Stage2G: valid negative mechanism result; the current boundary rule is unsupported.
- Stage2H: diagnostic only. Stage3A: failed development. Stage3C: descriptive planning only.
- Restarted Stage4A `n=2,800`: exact event-count arithmetic is correct, but 20 gains is a planning heuristic. The number is not an approved effect-power or controller-training sample size.
- Research position: `BETWEEN_STAGE3C_AND_STAGE4A_DESIGN`; no next experiment is authorized.

## Completed Execution History

The items below are preserved as execution history. Their evidence class is governed by the audit above; “completed” does not mean confirmatory validation.

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

## Completed Experiment: Stage2G Boundary-Decision Mechanism Audit

Protocol frozen in `docs/STAGE2G_PROTOCOL.md` before extracting or evaluating the `[400:600)` test slice.

1. Freeze a new unseen slice before evaluation, preferably source rows `[400:600)` for both datasets.
2. Compare dense fixed, all-query expansion, and boundary-only expansion under the same frozen q25 score floor and insertion budget.
3. Primary mechanism endpoint: whether boundary-only triggering lowers false insert relative to all-query expansion without reducing CR@20.
4. Report trigger coverage, positive-chain-completion precision, ER/CR, context tokens, and dataset-specific bootstrap intervals.
5. Do not search new score thresholds in Stage2G; threshold optimization, if needed, belongs to a separate development stage.

## Stage2G Observed Results

- Independent test: HotpotQA `[400:600)` + MuSiQue `[400:600)`, 400 queries, 12,122 candidate units, 882 gold units, zero overlap with Stage2E and Stage2F.
- Boundary prevalence = 0.8100 in both datasets; p10 trigger rate fell from 0.5225 to 0.4450 under boundary-only.
- Primary p10/i4 false-insert delta boundary-minus-all = +0.0043, 95% CI [-0.0054, 0.0150].
- Primary p10/i4 CR@20 delta = -0.0075, 95% CI [-0.0200, 0.0025]; the frozen -0.01 non-inferiority margin was not met.
- Secondary p5/i4 false-insert/CR@10 deltas = -0.0011/-0.0075; both frozen conditions failed.
- Predictive completion-precision delta boundary-minus-non-boundary = -0.0686, 95% CI [-0.4000, 0.2337], based on 34 versus 12 opportunities.
- All pre-registered mechanism gates: NOT SUPPORTED.
- Reproducibility: deterministic rerun produced byte-identical summary and bootstrap CSV files.

Interpretation boundary: q25 protected insertion can still improve retrieval relative to dense fixed, but the current OR-composed boundary rule is not validated as a selective benefit predictor.

## Completed Experiment: Stage2H Boundary-Rule Failure Diagnosis

Diagnostic plan fixed in `docs/STAGE2H_DIAGNOSTIC_PLAN.md`; this stage is explicitly post-hoc and will not tune a replacement threshold.

1. Generate per-query mechanism details for the already evaluated slices without changing Stage2G gate decisions.
2. Decompose the OR gate into `boundary_margin`, `ball_score_margin`, and `top_ball_score` trigger components.
3. Measure each component's prevalence, overlap, completion precision, harm rate, and false-insert yield.
4. Treat all Stage2H findings as exploratory diagnostics; do not tune and evaluate a replacement rule on the same queries.
5. If a replacement uncertainty controller is justified, develop it on a new `[600:1000)` slice and reserve a later slice for one final frozen test.

## Stage2H Observed Results

- Audit population: three pairwise-disjoint Stage2E-F-G slices, 1,200 queries, with zero missing gold units.
- Current OR-gate prevalence = 0.8083; `score_margin`/`radius`/`low_top_score` prevalence = 0.5825/0.5033/0.0008.
- On 133 triggered baseline-incomplete opportunities with 48 successful completions, continuous AUROC is 0.5223 for negative score margin, 0.4912 for negative radius margin, and 0.3821 for negative top score.
- Completion-precision true-minus-false contrasts are +0.1292 for score margin, -0.0976 for radius, and +0.0512 for the OR gate; every corresponding 95% CI includes zero.
- The score-only overlap mask has the highest descriptive completion precision (0.4262), while radius-only is 0.1667; these are post-hoc subgroup estimates, not controller-selection evidence.
- Deterministic rerun produced byte-identical query-audit, component-summary, and predictive-metrics CSV files.
- Validation confidence: CAUTION because outcomes were previously observed, multiple diagnostics were inspected, and useful-event counts are limited.

Interpretation boundary: the current OR rule is broad because the score-margin and radius conditions jointly cover most queries; score margin carries the strongest but weak signal, radius adds little selectivity, and the low-top-score branch is inert. No replacement threshold is validated.

## Completed Experiment: Stage3A Utility-Calibrated Controller Development

1. Use only a new development slice, provisionally source rows `[600:1000)`, for feature selection, calibration, and threshold choice.
2. Reserve a later, non-overlapping slice before development metrics are inspected; evaluate it once after freezing the controller.
3. Predict query-level utility from label-free retrieval signals, with separate targets for chain completion, Top-20 harm, and false-insert cost.
4. Compare the learned/calibrated controller with dense fixed, all-query q25 insertion, and the frozen Stage2G OR gate under identical budgets.
5. Keep Stage2E-H as diagnostic history only; do not reuse their labels for fitting or threshold selection.

Protocol: `docs/STAGE3A_PROTOCOL.md`. Stage3A uses source rows `[600:1000)` for development and reserves `[1000:1400)` for a later frozen Stage3B test. Stage3B metrics remain inaccessible until the Stage3A model artifact and threshold are committed.

## Stage3A Observed Results

- Data audit: 800 development queries and 24,415 units; zero missing gold, zero overlap with Stage2E-G, and zero overlap with the reserved Stage3B IDs.
- Fitting partition: 9 gain events and 2 harm events among 480 queries. The harm head used the predeclared sparse-target fallback.
- Threshold-selection partition: 12 gain events and 0 harm events among 320 queries. The selected threshold retained 10 gains and triggered 68 queries.
- Utility controller versus all-query: trigger-rate delta -0.2406, non-gold insertions/query delta -0.5531, CR@20 delta -0.00625.
- Utility controller versus dense fixed: CR@20 delta +0.03125, descriptive 95% CI [0.01250, 0.05000].
- False-insert-rate delta versus all-query = -0.00626, descriptive 95% CI [-0.03365, 0.02112]; fewer insertions do not establish better conditional precision.
- Promotion gate: FAIL because the no-fallback condition failed. The other four observed conditions passed.
- Reproducibility: query audit, model JSON, summary CSV, and bootstrap CSV are byte-identical on deterministic rerun.

Interpretation boundary: Stage3A supports a development-only volume/recall trade-off on HotpotQA, not a validated risk-aware controller. MuSiQue produced no gain or harm events, and Stage3B remains locked under the frozen stop rule.

## Completed Experiment: Stage3C Target-Feasibility And Data-Strategy Audit

1. Do not inspect Stage3B retrieval metrics and do not reuse its reserved IDs for development.
2. Quantify gain/harm event prevalence and saturation by dataset using development data only.
3. Audit whether another evidence-intensive multi-hop benchmark supplies enough non-saturated gain and harm events for controller learning.
4. Compare two research scopes before new modeling: risk-aware expected utility versus budget-aware gain selection.
5. Freeze a new data and endpoint protocol before fitting another controller branch.

Protocol: `docs/STAGE3C_PROTOCOL.md`. This audit reuses only observed Stage2H/Stage3A labels, screens five predeclared datasets with primary sources, and does not download, embed, or evaluate Stage3B data.

## Stage3C Observed Results

- Internal audit: 2,000 pairwise-disjoint observed queries, 69 gain events, and 8 harm events.
- Dataset split: HotpotQA contains all 69 gains and 8 harms; MuSiQue contains zero events and has dense-fixed CR@20 = 1.0000.
- HotpotQA gain/harm prevalence = 0.069/0.008; pooled gain/harm prevalence = 0.0345/0.0040.
- No two observed partitions contain at least 5 harms, so the frozen risk-aware event-feasibility rule fails.
- The budget-aware gain-selection rule passes because 69 gains exceed the 20-event threshold.
- At the pooled harm point prevalence, 5,000/12,500 queries would be expected for 20/50 harm events; this is descriptive planning, not a power guarantee.
- External source screen: 2WikiMultiHopQA is the primary independent QA pilot candidate; HotpotQA train is same-domain expansion; MuSiQue is unsuitable for unchanged CR@20; IIRC needs access/terms remediation; HoVer changes the task to verification.
- Reproducibility: event summary CSV and decision JSON are byte-identical on deterministic rerun.
- Stage3B action: KEEP_LOCKED.

Interpretation boundary: Stage3C supports narrowing the research scope to budget-aware gain selection. It does not validate a selector or establish that 2Wiki is non-saturated.

## Stage4A 2WikiMultiHopQA Feasibility Pilot

1. Verify dataset archive provenance, checksum, and terms before download or extraction.
2. Freeze a small development-only sample and a separate untouched reservation before retrieval metrics are computed.
3. Map `context`, `supporting_facts`, and evidence paths into the existing unit/query schema and report mapping loss.
4. Measure dense-fixed CR@20 and q25 protect-10/insert-4 gain prevalence without fitting a controller.
5. Continue only if the pilot is non-saturated and supplies enough gain events under a preregistered threshold.

Protocol: `docs/STAGE4A_PROTOCOL.md`. Because the official Dropbox archive is not reachable from the experiment shell, the pilot uses a pinned schema-only Hugging Face mirror with `PROVENANCE_DOWNGRADED` status. Paper-grade use requires later reconciliation against the official archive.

## Stage4A Observed Results

- Source mapping: 400 queries, 982/982 supporting facts mapped, zero queries missing gold evidence.
- Dense baseline: ER@20 = 0.8831 and CR@20 = 0.7450, so the pilot is not saturated at the preregistered threshold.
- Unfiltered p10/i4: trigger rate = 0.5450, 9 gains, 8 harms, net completed-chain change = +1.
- Transferred q25 p10/i4: ER@20 = 0.8902, CR@20 = 0.7525, trigger rate = 0.5050, 8 gains, 5 harms, net completed-chain change = +3.
- The q25 floor removed 213 candidates and therefore did not collapse to the unfiltered strategy.
- The q25 gain prevalence was 0.0200 (95% Wilson interval [0.0102, 0.0390]); q25-versus-dense CR@20 delta was +0.0075 with descriptive paired-bootstrap interval [-0.0100, 0.0250].
- Five promotion conditions passed. The preregistered requirement of at least 10 q25 gain events failed because only 8 were observed.
- Frozen-protocol decision: `STOP` for the mirror-specific Stage4B branch. Do not fit a selector, tune the q25 floor, or rerun this pilot after threshold modification.
- Post-hoc design audit: 400 was a convenience size with no recorded power or event-count operating-characteristic analysis. At the observed 0.0200 gain prevalence, 400 queries have only 0.2821 probability of reaching the 10-gain gate.
- Official archive reconciliation: IDs and non-context shared fields match, but 7/400 contexts and 5/400 gold-evidence texts differ after the April 7 sentence-segmentation corrections; official/mirror candidate units are 12,718/12,721.
- Corrected interpretation: existing metrics are deterministic mirror results, not official April 7 results. `STOP` is not evidence that HyperGranular RAG or 2Wiki is infeasible and must not justify abandoning the direction.
- Any repair study requires a new name, official-archive source hashes, a power/event-count-based sample size, and fresh rows excluding `[0:800)`.
- Stage3B remains `KEEP_LOCKED`. See `docs/STAGE4A_DESIGN_AUDIT.md` and `docs/STAGE4A_OFFICIAL_RECONCILIATION.json`.

## Stage4A Scientific Conclusion Status

- Mirror experiment reproducibility: VERIFIED.
- Official-source equivalence: FAILED.
- Sample-size justification: FAILED.
- Procedural mirror gate: STOP.
- Scientific feasibility conclusion: `INVALIDATED_NO_OFFICIAL_FEASIBILITY_DECISION`.
- Research-direction status: OPEN.

The dependency audit in `docs/STAGE4A_RESTART_DEPENDENCY_AUDIT.md` supersedes any wording that treats the archived Stage4A `STOP` as evidence against HyperGranular RAG or official 2Wiki feasibility.

## Returned Design: Restarted Stage4A Official-source Feasibility

The restarted Stage4A draft has not accessed fresh rows and is returned for design revision. Research-stage numbering remains rolled back: Stage3C is the last retained completed stage, and its evidence class is descriptive planning only.

- Historical event target: at least 20 q25 gains, aligned with a Stage3C planning heuristic.
- Minimum planning prevalence: 0.0100.
- Target probability of reaching the event target: 0.95.
- Exact binomial minimum for that event-count assumption: 2,784 queries; rounded lower bound: 2,800.
- Withdrawn development rows: official `[800:3600)`; do not extract pending redesign.
- Withdrawn ID-only reservation: official `[3600:6400)`; do not inspect pending redesign.
- Existing `[0:800)` rows are excluded.
- No extraction, controller fitting, q25 tuning, embeddings, or retrieval metrics under the current draft.

The replacement design selected official gain/harm prevalence estimation as its primary objective. The returned draft remains historical in `docs/STAGE4A_RESTART_PROTOCOL_DRAFT.md`; its event-count lower-bound calculation remains in `docs/STAGE4A_RESTART_SAMPLE_SIZE_PLAN.json`.

## Approved Stage4A-R2: Official Event-rate Estimation

Protocol: `docs/STAGE4A_R2_PROTOCOL.md`. The protocol was user-approved on 2026-07-12 and must be committed with execution and verification code before official rows `[800:5300)` are extracted.

- Primary estimands: frozen q25 gain and harm prevalence at CR@20.
- Primary precision target: Wilson 95% interval half-width at most 0.005 when prevalence is at most 0.03.
- Exact minimum: 4,497; frozen development sample: 4,500.
- Development rows: official `[800:5300)`.
- Reservation rows: official `[5300:9800)`, IDs/digest only.
- Secondary analysis: exact conditional two-sided McNemar for q25 versus dense CR@20, alpha 0.05.
- At total discordance 0.05 and net gain 0.01, exact power at 4,500 is 0.83798.
- No threshold tuning, boundary-rule repair, controller fitting, reservation metrics, or Stage3B access.

Sample-size artifact: `docs/STAGE4A_R2_SAMPLE_SIZE_PLAN.json`, generated by `scripts/stage4a_r2_plan_sample_size.py`.
