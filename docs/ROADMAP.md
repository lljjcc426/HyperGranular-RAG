# Roadmap

## Material Passport

- Project: HyperGranular-RAG
- Current stage: Stage4A-R2 official event-rate estimation completed and independently verified; next controller study not yet authorized; Stage3B remains locked
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

### Stage4A-R2 Amendment 1

The first official extraction stopped before writing outputs because 19/11,003 supporting facts in 19 base queries had out-of-range sentence indices after the April 7 segmentation update. No embeddings or retrieval metrics were produced.

The approved amendment removes those 19 label-incomplete base records and selects the earliest 19 fully mappable rows from official replacement pool `[9800:12576)`. Selection uses source-label integrity only. The final sample remains 4,500; reservation `[5300:9800)` remains IDs/digest only. See `docs/STAGE4A_R2_AMENDMENT_1.md`.

Amendment extraction result: the earliest 19 replacement rows were `[9800:9819)` with zero additional replacement failures. The final source audit contains 4,500 development IDs and 4,500 reservation IDs with zero overlap, 11,015/11,015 mapped supporting facts, zero missing-gold queries, and no supporting fact attached to a duplicated context title. The corpus contains 143,820 candidate units. No embeddings or retrieval metrics had been computed at this checkpoint.

### Stage4A-R2 Verified Results

- Primary q25 gain prevalence: 94/4,500 = 0.020889, Wilson 95% [0.017101, 0.025494], half-width 0.004197.
- Primary q25 harm prevalence: 69/4,500 = 0.015333, Wilson 95% [0.012134, 0.019359], half-width 0.003612.
- Precision decision: `ESTIMATION_COMPLETE`; both frozen half-width gates passed.
- Dense/q25 CR@20: 0.77222/0.77778; delta +0.00556.
- Secondary exact McNemar: `p=0.05980`; average CR improvement is not confirmed and is below the planned +0.01 practical target.
- q25 vs dense ER@20 delta: +0.00407, descriptive bootstrap [0.00147, 0.00674].
- q25 vs unfiltered CR@20 delta: +0.00578, descriptive bootstrap [0.00311, 0.00867].
- q25 conditional false-insert rate: 0.92163; noise remains high.
- Type net gain: bridge-comparison +15, comparison +25, compositional -3, inference -12.
- Independent verifier passed all query, summary, inference, and bootstrap checks; deterministic rerun produced byte-identical query audit, summary, bootstrap, and inference files.
- Controller fitting remains unauthorized. A new model-specific protocol is required before using these labels for controller development.

## Draft Stage4B-U1: Label-free Boundary-Uncertainty Controller

Protocol draft: `docs/STAGE4B_U1_PROTOCOL_DRAFT.md`. This branch is not yet authorized for execution.

1. Project governance prohibits Gold labels from entering feature selection, model fitting, threshold selection, or retrieval decisions; therefore the prior supervised gain/harm-controller direction is not reused.
2. U1 uses four label-free quantities fixed by the retrieval mechanism: ball-score margin, normalized ball-boundary margin, selected-hyperedge count, and insertable q25 candidate count.
3. Feature scaling uses development empirical distributions only. The score formula has fixed equal uncertainty weights and a readiness product; its threshold is the median feasible-query score, selected solely to impose an approximately 50% feasible-query resource budget.
4. A Gold-free policy artifact must be independently verified, committed, and pushed before any development Gold evaluation.
5. Stage4A-R2's 94 gains and 69 harms are used only as conditional power-planning anchors and frozen-policy evaluation events, never as controller inputs.
6. U1-D is retrospective internal development. The official `[5300:9800)` reservation remains locked unless every promotion gate passes and the user separately approves U1-R.
7. No feature extraction, policy calibration, controller evaluation, reservation access, or Stage3B access is authorized by the draft.

Power-plan generator: `scripts/stage4b_u1_plan_power.py`; artifact: `docs/STAGE4B_U1_POWER_PLAN.json`.

## Stage4B-U1 Protocol Review 1 And Revision 2

Review decision: `RETURN_FOR_PROTOCOL_REVISION`. U1-D execution was not approved; feature extraction, policy freezing, Gold evaluation, reservation access, and Stage3B access remain prohibited.

Mandatory revisions recorded in `docs/STAGE4B_U1_PROTOCOL_REVIEW_1.md`:

1. Replace legacy Gold-bearing candidate/ball objects with separate unlabeled units, unlabeled queries, and evaluator-only Gold map files.
2. Replace the ambiguous median threshold with a unique score/hash ordered-prefix rule.
3. Allocate at most 60% of all-query q25 planned insert units, mechanically guaranteeing at least 40% insertion reduction.
4. Freeze no-ball, one-ball, zero-radius, float, NaN/Inf, ECDF equality, and extrapolation behavior.
5. Define U1 strictly as an on/off selector between byte-identical dense and all-query q25 Top-20 rankings.
6. Use correct zero-null statistical language and a single joint intersection-union claim with each component tested at alpha 0.05.

Revision 2 design: `docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md`. At the review commit its status was `REVISION_2_DESIGN_ONLY_IMPLEMENTATION_PENDING`; the subsequent synthetic implementation checkpoint below supersedes that implementation-pending status without authorizing execution.

### Stage4B-U1 Synthetic Implementation Checkpoint

- Added separate channel preparer, Gold-free retrieval/controller, evaluator, independent verifier, and deterministic synthetic verification runner.
- Controller and evaluator receive separate manifests; the controller process does not receive a Gold-map hash or labeled-source hash.
- Seven synthetic tests pass with zero failures/errors/skips.
- Gold-free dense, selected-edge, candidate, and q25 rankings match the legacy frozen algorithm on the same synthetic input.
- The 60% planned-insert ordered-prefix budget, reservation ECDF reuse, ranking subset relation, corruption rejection, and byte-identical rerun are verified.
- Evidence: `docs/STAGE4B_U1_IMPLEMENTATION_AUDIT.md` and `results/stage4b_u1_synthetic_verification.json`.
- No official U1-D data, reservation data, Stage3B data, or official metrics were accessed.
- Current status: `REVISION_2_IMPLEMENTED_SYNTHETICALLY_VERIFIED_AWAITING_EXECUTION_APPROVAL`.

### Stage4B-U1-D Execution Package Review 1 And v2.1 Hardening

- Execution-package decision: `RETURN_EXECUTION_PACKAGE_FOR_HARDENING`; v2 architecture remains `ACCEPTED_IN_PRINCIPLE`.
- Official U1-D channel preparation, U1-D Gold evaluation, reservation, and Stage3B remained unauthorized/locked.
- Review record: `docs/STAGE4B_U1_EXECUTION_PACKAGE_REVIEW_1.md`.
- The v2.1 hardening specification was frozen before new tests in `docs/STAGE4B_U1_EXECUTION_HARDENING_V2_1.md`.
- Formal channel preparation now requires the verified Stage4A-R2 source-audit SHA, 4,500 development queries, and the frozen development ID digest.
- Formal controller execution now freezes MiniLM, max length 192, batch size 64, development role, and the complete retrieval configuration.
- Policy binding now covers Git commit, protocol, common/retrieval/controller/preparer/verifier source, unlabeled inputs, channel audit, embedding cache, and source audit.
- The verifier independently recomputes tie hashes, four ECDF outputs, uncertainty, readiness, score, ordered rank, cutoff, budget, trigger set, and ranking/insert structure.
- The evaluator requires a committed `VERIFIED_PRE_GOLD` artifact and derives inserted IDs from Top-20 structure.
- A Stage4A-R2 baseline-equivalence hard gate runs before U1 summaries; drift raises `HARD_FAILURE_IMPLEMENTATION_DRIFT`.
- Python 3.12 synthetic validation: 20 tests, 0 failures/errors/skips; all 11 required failure injections were rejected.
- Deterministic evidence SHA-256: `799E2AE73F24C223FA28AB104AF5C830F2E4D7678795B5CB5C8F51DC32D39AC3` on two complete runs.
- Current status: `V2_1_SYNTHETICALLY_HARDENED_AWAITING_REAPPROVAL`; this is not U1-D execution authorization.

### Stage4B-U1-D v2.1 Pre-Gold Reapproval Package

- Approval request: `docs/STAGE4B_U1_EXECUTION_PACKAGE_V2_1_APPROVAL_REQUEST.md`.
- Machine-readable package binding: `docs/STAGE4B_U1_EXECUTION_PACKAGE_V2_1_MANIFEST.json`.
- Bound implementation commit: `dd1f8a9893ccb1e760068ad21d48e0e8938cc7f9`.
- Requested authorization is intentionally narrower than Gold evaluation: official channel preparation, Gold-free controller, artifact commit, and `VERIFIED_PRE_GOLD` only.
- Required stop: pre-Gold verification committed and pushed; a separate user approval is required before evaluator/Gold join.
- Current decision remains `NOT_APPROVED` until the user explicitly approves this package.

### Stage4B-U1-D v2.1 Pre-Gold Approval

- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_EXECUTION_V2_1` on 2026-07-13.
- Approval decision: `docs/STAGE4B_U1_EXECUTION_PACKAGE_V2_1_APPROVAL_DECISION.md`.
- Bound commits: request `2f6c7067c686bf1f4c13328bd1fc04ab3990f767`; implementation `dd1f8a9893ccb1e760068ad21d48e0e8938cc7f9`.
- Authorized: official U1-D channel, Gold-free controller, policy/ranking/decision commit, and committed `VERIFIED_PRE_GOLD`.
- Not authorized: evaluator/Gold join, U1-D metrics or interpretation, reservation, Stage3B, parameter changes, or automatic retry.
- Required stop: immediately after `VERIFIED_PRE_GOLD` is committed and pushed.
- Approval governance commit `d327193` was pushed before official data access.
- The unchanged 20-test synthetic runner was rerun twice against the approved AGENTS/protocol bytes; both outputs had SHA-256 `6F97EE054EFEACEC0BD50414D1A3133CB23D9B6FC57462356147C06AF804C7A5`.
- The binding rerun recorded no official-development, reservation, or Stage3B access.

### Stage4B-U1-D Pre-Gold Hard Failure 1

- Failure audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_1.md`.
- Status: `PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_1` on 2026-07-13.
- The formal preflight confirmed 143,820 unit rows, 4,500 query rows, and legacy cache SHA-256 `746FC1130038C789190F2A37CB911BBFC46905CFCC138E361C1F6CF991A45F02`.
- The legacy Stage4A-R2 NPZ contains only `model_name`, `query_embeddings`, and `unit_embeddings`; it lacks the v2.1-required `unit_ids`, `query_ids`, and `max_length`.
- This triggered `HARD_FAILURE_EMBEDDING_CACHE_METADATA` before official channel preparation.
- No official channel, Gold map, controller, decision, ranking, policy, `VERIFIED_PRE_GOLD`, or U1-D metric was generated or read. Reservation and Stage3B were not accessed.
- No cache was rebuilt, migrated, patched, overwritten, or deleted; execution did not auto-retry.

### Stage4B-U1-D Pre-Gold Amendment 1 Draft

- Draft: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_1_DRAFT.md`.
- Status at draft submission: `DRAFT_NOT_APPROVED_NOT_EXECUTABLE`; superseded by the approval checkpoint below.
- The sole requested change is a fresh, non-existing U1-D-specific ID-bound cache path created once by the unchanged approved controller.
- Model, max length, batch size, data boundary, q25, score, ECDF, 60% budget, endpoints, implementation, Gold isolation, and stop rules remain frozen.
- At draft submission, official U1-D pre-Gold remained locked pending explicit approval, governance push, and a new synthetic binding verification.

### Stage4B-U1-D Pre-Gold Amendment 1 Approval

- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_1` on 2026-07-13.
- Approval decision: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_1_APPROVAL_DECISION.md`.
- Bound commits: amendment `a7e121584d9f512bb7b4abaabdb9c93913ad560d`; implementation `dd1f8a9893ccb1e760068ad21d48e0e8938cc7f9`.
- Authorized: preserve the legacy cache, require a new path to be absent, create one fresh ID-bound cache with the frozen encoder, independently validate it, and complete the already approved pre-Gold artifacts and `VERIFIED_PRE_GOLD`.
- Not authorized: Gold evaluation, U1-D metrics, reservation, Stage3B, implementation or parameter changes, or automatic retry.
- Governance and new synthetic binding evidence must be pushed before official-development execution resumes.

### Stage4B-U1-D Post-Amendment Synthetic Binding

- Approval governance commit `19bb733` was pushed before this rerun.
- The unchanged 20-test runner completed twice with zero failures, errors, or skips.
- Both complete outputs had SHA-256 `9AA0D0499ECF613F7FEAED0F078BB7534CB837C22465AA1F13F29D715BBE8A6A`.
- The evidence reports no official-development data, official source audit, reservation, or Stage3B access.
- The frozen runner's historical `V2_1_SYNTHETICALLY_HARDENED_AWAITING_REAPPROVAL` text is not the governance state; current authorization remains the committed Amendment 1 approval.

### Stage4B-U1-D Pre-Gold Hard Failure 2

- Failure audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_2.md`.
- Status: `PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_2` on 2026-07-13.
- The formal preflight passed Git, 143,820-unit, 4,500-query, source-audit, legacy-cache, and all-new-path-absent gates.
- It hard-failed because the processed runtime query-ID digest was `8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6`, while v2.1 compared it with source audit digest `6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2`.
- Repository code review showed that `6B21...` binds raw official IDs represented as `sample_id`; runtime `query_id` is deterministically namespaced as `2wikimultihopqa::<sample_id>`.
- No channel, Gold map, controller, new cache, decision, ranking, policy, verifier, or metric was produced. Reservation and Stage3B were not accessed.
- Formal preflight was not automatically rerun.

### Stage4B-U1-D Pre-Gold Amendment 2 Draft

- Draft: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_2_DRAFT.md`.
- Status: `DRAFT_NOT_APPROVED_NOT_EXECUTABLE`.
- The proposal freezes both sample-ID and runtime query-ID digests and requires an exact per-row `query_id == dataset::sample_id` relation.
- The first approval would authorize only minimal implementation changes and synthetic hardening. Official development remains locked until a new implementation commit is separately approved.

### Stage4B-U1-D Pre-Gold Amendment 2 Approval

- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_2_IMPLEMENTATION_SYNTHETIC_ONLY` on 2026-07-13.
- Approval decision: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_2_APPROVAL_DECISION.md`.
- Bound amendment commit: `dde5a28fec476fddd0ac82ebad39d9eeab0bea1e`.
- Authorized: dual sample-ID/runtime-query-ID binding implementation, per-row namespace validation, corresponding failure injections, complete synthetic suite, deterministic evidence, audit, commit, and push.
- Not authorized: official development, preflight, channel, controller, cache, formal verifier, Gold evaluation, metrics, reservation, or Stage3B.
- Required stop: after the implementation and synthetic evidence are pushed; official execution requires a new implementation-bound approval.

### Stage4B-U1-D Amendment 2 Synthetic Implementation

- Implementation checkpoint: `stage4b_u1_v2_2`.
- Audit: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_2_IMPLEMENTATION_AUDIT.md`.
- The frozen official sample-ID digest remains `6B21FD1D2EFBD6A467C8DAEE9225AA43113FC328CD114F813DD79E6A44458FB2`.
- The namespaced runtime query-ID digest is separately frozen as `8895D4D2EF2A34DE123525011C36A1DF092D27B7588E17E9816ABAB8F1A25CD6`.
- Preparer, controller, and independent verifier require exact per-row `query_id == dataset::sample_id` and bind both digests.
- The original 20 tests remain, with four additional dual-ID failure injections; all 24 pass.
- The final runner was byte-identical twice with SHA-256 `8B3057238D67EBE874017068C125126974062C61FAF3D79595E884F16A876D7D`.
- No official development, official source audit, reservation, Stage3B, Gold evaluation, or official artifact was accessed or generated.
- Current state: awaiting a new implementation-bound official pre-Gold resumption approval.

### Stage4B-U1-D v2.2 Official Pre-Gold Resumption Package

- Request: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_2_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_2_MANIFEST.json`.
- Bound implementation commit: `ca2cca332292f7bd6af12e2a429100be11da5549`.
- Requested scope: governance rebinding, one dual-ID formal preflight, one official separated channel, one fresh ID-bound cache/controller run, independent cache audit, committed policy/ranking/decision, and committed `VERIFIED_PRE_GOLD` with `evaluation=null`.
- Gold evaluation, U1-D metrics, reservation, Stage3B, implementation changes, parameter changes, and automatic retry remain outside the request.
- Current status: `APPROVED`; execution is gated on a fresh governance-byte synthetic rebinding.

### Stage4B-U1-D v2.2 Official Pre-Gold Resumption Approval

- Decision: `APPROVE_STAGE4B_U1_D_V2_2_OFFICIAL_PREGOLD_RESUMPTION` on 2026-07-13.
- Approval decision: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_2_APPROVAL_DECISION.md`.
- Bound request-package commit: `fae181564504f1a69bcebfd5d5201eea7e2d9abf`.
- Bound implementation commit: `ca2cca332292f7bd6af12e2a429100be11da5549`.
- Authorized sequence ends at committed and pushed `VERIFIED_PRE_GOLD` with `evaluation=null`.
- Gold evaluation, U1-D metrics or interpretation, promotion, reservation, Stage3B, implementation changes, parameter changes, and automatic retry remain prohibited.
- Status at approval entry: `OFFICIAL_PREGOLD_RESUMPTION_APPROVED_AWAITING_SYNTHETIC_REBINDING`.

### Stage4B-U1-D v2.2 Synthetic Rebinding

- Approval governance commit: `c13be1f`.
- Audit: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_2_SYNTHETIC_REBINDING_AUDIT.md`.
- Two complete 24-test runs passed with 0 failures, errors, or skips.
- Both complete outputs have SHA-256 `9B01C80F66096F01C763C25E44E4D079C40B681F6C52F0CC55F70492689EAAB1` and are byte-identical.
- The tests accessed no official development, official source audit, reservation, or Stage3B data.
- Status after this gate: `SYNTHETIC_REBINDING_VERIFIED_READY_FOR_DUAL_ID_FORMAL_PREFLIGHT`.

### Stage4B-U1-D v2.2 Formal Preflight and Controller

- One read-only dual-ID formal preflight passed all Git, count, source-audit, dual-digest, namespace, legacy-cache, and new-path gates.
- One official channel preparation produced separated controller/evaluator channels with no retrieval metrics.
- One Gold-free controller run produced a frozen policy and 4,500 decision/ranking rows with `evaluation_labels_loaded=false`.
- Fresh ID-bound cache SHA-256: `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D`.
- The independent cache audit passed exact ID order, dual digests, metadata, dtype, shape, finite-value, normalization, byte-size, and SHA checks.
- Audits: `docs/STAGE4B_U1_PREGOLD_V2_2_FORMAL_PREFLIGHT_AUDIT.md`, `docs/STAGE4B_U1_PREGOLD_V2_2_CONTROLLER_EXECUTION_AUDIT.md`, and `docs/STAGE4B_U1_PREGOLD_V2_2_CACHE_AUDIT.md`.
- No Gold evaluation, U1-D metric interpretation, reservation, or Stage3B access occurred.
- Controller artifact commit: `9207bd78eea44d2ea3291fe9b6748526969a3224`.
- Current status after the next gate: `PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_3`.

### Stage4B-U1-D Pre-Gold Hard Failure 3

- Independent verifier was run once on committed artifacts without Gold/evaluator arguments.
- It stopped at the first ranking structure check because the verifier required exactly 20 IDs while the query had only 17 candidate units.
- Gold-free structural diagnosis found 628/4,500 queries with fewer than 20 candidates, minimum 10; all controller list lengths equal `min(20, candidate_count)`.
- No `VERIFIED_PRE_GOLD` was written, and no Gold evaluation, U1-D effect metric, reservation, or Stage3B access occurred.
- Audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_3.md`.
- Existing controller artifacts are retained as `UNVERIFIED_INVALID_FOR_GOLD`.

### Stage4B-U1-D Pre-Gold Amendment 3 Draft

- Draft: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_DRAFT.md`.
- Proposed rule: `K_q=min(20, candidate_count_q)` with exact length, uniqueness, candidate membership, protected-prefix, insertion, and final-ranking verification.
- First requested authorization is implementation and synthetic verification only; no official development command is requested.
- Current status: `DRAFT_NOT_APPROVED_NOT_EXECUTABLE`.

### Stage4B-U1-D Pre-Gold Amendment 3 Approval Request

- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_MANIFEST.json`.
- Bound failure/audit commit: `8b43de72418ccda85af3015f758c39bce9d31411`.
- Requested scope is effective-K protocol/verifier implementation and synthetic hardening only.
- Official development, source audit, controller/verifier reruns, Gold, U1-D metrics, reservation, Stage3B, and cache changes remain prohibited.
- Status at request entry: `AWAITING_AMENDMENT_3_IMPLEMENTATION_SYNTHETIC_APPROVAL`.

### Stage4B-U1-D Pre-Gold Amendment 3 Approval

- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_3_IMPLEMENTATION_SYNTHETIC_ONLY` on 2026-07-13.
- Approval decision: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_APPROVAL_DECISION.md`.
- Bound approval-package commit: `42747507d6f37c3d5713949de443311b35262a2d`.
- Bound failure-audit commit: `8b43de72418ccda85af3015f758c39bce9d31411`.
- Authorized: effective-K protocol/checkpoint/verifier/runner/test implementation, complete synthetic suite, two byte-identical evidence runs, audit, hashes, and a new official-resumption request.
- Not authorized: any official data read, official command, failed-artifact/cache mutation, Gold, U1-D metrics, reservation, Stage3B, retrieval/controller/evaluator or parameter changes.
- Current status: `AMENDMENT_3_APPROVED_IMPLEMENTATION_SYNTHETIC_ONLY`.

### Stage4B-U1-D Pre-Gold Amendment 3 Implementation

- Implementation checkpoint: `stage4b_u1_v2_3`.
- Effective-K rules: `K_q=min(20,|C_q|)` and `P_q=min(10,K_q)`.
- The verifier independently enforces candidate count, non-empty pools, exact effective-K lengths, per-list uniqueness, candidate membership, protected-prefix equality, insertion range/derivation, and final selector consistency.
- The original 24 synthetic tests remain; nine effective-K/candidate-pool tests were added, for 33 total.
- The complete 33-test evidence runner passed twice with zero failures, errors, or skips; both outputs have SHA-256 `38DDA409C866AAAC6C2AEDBA0D0716DA6F483854E9A6019E9040B9B2B1FA40B5`.
- Audit: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_3_IMPLEMENTATION_AUDIT.md`.
- No official development, source audit, official ranking, cache, Gold, reservation, or Stage3B access occurred.
- Current status: `SYNTHETICALLY_VERIFIED_OFFICIAL_EXECUTION_NOT_AUTHORIZED`.
- Next gate: commit and push this implementation, then create an implementation-bound v2.3 official pre-Gold resumption approval package and stop.

### Stage4B-U1-D v2.3 Official Pre-Gold Resumption Request

- Implementation commit: `a1d9ea0c517fcbad1ef27e78e760738d5c04d8b3`.
- Request: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_MANIFEST.json`.
- Requested execution uses new versioned channel/controller/verifier paths and preserves all v2.2 failure artifacts.
- The audited fresh ID-bound cache may only be reused read-only; no encoding, rebuild, overwrite, deletion, or migration is requested.
- New decisions/rankings must be byte-identical to the frozen v2.2 outputs; policy differences are limited to registered v2.3 binding fields.
- Gold, U1-D metrics, reservation, Stage3B, implementation changes, and automatic retries remain prohibited.
- Current status: `AWAITING_V2_3_OFFICIAL_PREGOLD_RESUMPTION_APPROVAL`.

### Stage4B-U1-D v2.3 Resumption Review 1

- Reviewed package commit: `dbb4e057405069aceda5a7c5d88d9d39a4d14775`.
- Review: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_REVIEW_1.md`.
- Decision: `RETURN_FOR_PROTOCOL_AND_CACHE_FAIL_CLOSED_REVISION`.
- Blocking gates: post-approval synthetic rebinding, exact ten-path artifact registry, and controller-enforced require-existing/no-build cache reuse with pre/post fingerprint checks.
- Code inspection confirmed the current controller builds and writes a cache when the path is absent; package-only wording cannot make this fail-closed.
- No official data, ranking, cache, Gold, reservation, or Stage3B access occurred.

### Stage4B-U1-D Pre-Gold Amendment 4 Request

- Draft: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_CACHE_FAIL_CLOSED_DRAFT.md`.
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_MANIFEST.json`.
- Proposed checkpoint: `stage4b_u1_v2_3_1`.
- Requested scope: controller cache fail-closed mode, governance rebinding support, exact artifact registry, tests, deterministic evidence, and implementation audit only.
- Official execution, official data/cache access, Gold, reservation, and Stage3B remain prohibited.
- Approval decision: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_APPROVAL_DECISION.md`.
- Bound package commit: `e5a0e2187e770c9d7b9e9a85a6b8e91067ed2af1`.
- Decision: `APPROVE_CACHE_FAIL_CLOSED_IMPLEMENTATION_SYNTHETIC_ONLY`.
- Current status: `AMENDMENT_4_APPROVED_IMPLEMENTATION_SYNTHETIC_ONLY`.

### Stage4B-U1-D Pre-Gold Amendment 4 Implementation

- Implementation checkpoint: `stage4b_u1_v2_3_1`.
- Formal controller now requires an existing frozen cache, performs strict pre/post fingerprints, writes pending outputs only in an OS temporary directory, enforces v2.2 decision/ranking bytes and registered policy drift, and rolls back partial promotions.
- Synthetic runner supports registered, committed, repo-relative governance bindings and rejects missing, outside-repo, duplicate, or unregistered paths.
- The ten v2.3.1 artifact paths are identical between shared constants and the Amendment 4 manifest.
- The original 33 tests remain; 17 cache/governance hardening tests were added, for 50 total.
- Two complete 50-test evidence runs passed with zero failures, errors, or skips and identical SHA-256 `24F287F9B71C974ABEF9E03AA55BCCA0C4AF9809AB2ADC44705A42EC3889F657`.
- Audit: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_IMPLEMENTATION_AUDIT.md`.
- No official data, ranking, cache, Gold, reservation, or Stage3B access occurred.
- Current status: `SYNTHETICALLY_VERIFIED_OFFICIAL_EXECUTION_NOT_AUTHORIZED`.
- Next gate: commit/push implementation and evidence, then create a new implementation-bound resumption package and stop.
