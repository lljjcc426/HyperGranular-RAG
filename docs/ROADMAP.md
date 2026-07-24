# Roadmap

## Material Passport

- Project: HyperGranular-RAG
- Current stage: Stage4D-CMA/controller are closed; Stage4E–4I are complete with independent final verification; Stage4I finds strong-dense sidecar complementarity inconclusive, protected placement supported, and facet increment inconclusive
- Current governance: project-wide and durable across all current/future stages; one research stage receives one authorization; stage-internal predefined work is continuous; step/channel reapproval is disabled; only new scientific boundaries or serious integrity anomalies pause execution
- Data used so far: HotpotQA and MuSiQue development slices; invalidated 2Wiki mirror pilot; official April 7 archive development batch through verified Stage4D-CMA; deterministic new-ID HotpotQA train 1,000 and MuSiQue train 3,000 in Stage4E/4F; separate zero-overlap HotpotQA 1,000 + MuSiQue 1,500 boundaries in Stage4H and Stage4I; reservation and Stage3B were not accessed
- Generators used: Qwen2.5-1.5B-Instruct in verified Stage4E/4F/4H; one pre-specified Gemma 4 E2B official mobile-QAT configuration in verified Stage4G
- Gold labels used for indexing: No

## Prior-stage Audit Decision

The full integrity and methodology audit is recorded in `docs/PRIOR_STAGE_METHOD_AUDIT.md` and `docs/PRIOR_STAGE_AUDIT.json`.

- Computational integrity through Stage3C: passed, including disjoint slice checks, zero missing gold, no gold-driven retrieval selection, and byte-identical reruns for Stage2F-Stage3C.
- Stage0-Stage2E: reproducible exploratory development only because no independent pre-result protocol was committed.
- Stage2F: narrow internal evidence only; the primary CR@10 gate failed and the 400-query test had no a priori power calculation.
- Stage2G: valid negative mechanism result; the current boundary rule is unsupported.
- Stage2H: diagnostic only. Stage3A: failed development. Stage3C: descriptive planning only.
- Restarted Stage4A `n=2,800`: exact event-count arithmetic is correct, but 20 gains is a planning heuristic. The number is not an approved effect-power or controller-training sample size.
- Research position: `STAGE4D_CMA_CLOSED` and `CURRENT_CONTROLLER_BRANCH_FROZEN_CLOSED`; Stage4E/4F support static q25 relative to historical Dense under Qwen, while Stage4G returns `GENERATOR_TRANSFER_INCONCLUSIVE`. Stage4H again supports Full vs historical Dense but is negative vs BGE strong dense. Stage4I tests the narrower BGE+HGRAG sidecar formulation: the core comparison is inconclusive, protected placement is supported, and facet increment is inconclusive. U2, reservation, Stage3B, new controllers, full-wiki Gold, and new generator/strong-retriever search are not authorized.

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

### Stage4B-U1-D v2.3.1 Official Pre-Gold Resumption Request

- Implementation commit: `34349c70ee24b8240fd169393134d4280968b790`.
- Request: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_MANIFEST.json`.
- Approval must first be committed and pushed, followed by two byte-identical 50-test synthetic runs binding the request, manifest, decision, and final `AGENTS.md`; formal preflight is blocked until rebinding evidence is pushed.
- The exact ten artifact paths, frozen cache, v2.2 decision/ranking/policy equivalence, pending-output promotion, and all stop rules are machine-registered.
- Gold, U1-D metrics, reservation, Stage3B, implementation changes, cache writes, and automatic retries remain prohibited.
- Current status: `AWAITING_V2_3_1_OFFICIAL_PREGOLD_RESUMPTION_APPROVAL`.

### Stage4B-U1-D v2.3.1 Official Pre-Gold Resumption Approval

- Decision: `APPROVE_STAGE4B_U1_D_V2_3_1_OFFICIAL_PREGOLD_RESUMPTION` on 2026-07-13.
- Bound request-package commit: `e76c921454697d1784b0d76a9d9677113051f0f6`.
- Bound implementation commit: `34349c70ee24b8240fd169393134d4280968b790`.
- Decision file: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_APPROVAL_DECISION.md`.
- The mandatory first execution gate is two complete, byte-identical 50-test synthetic runs on committed post-approval governance bytes, followed by committed and pushed rebinding evidence and audit.
- Only after that gate may one formal preflight, one exact-path channel, one require-existing controller, committed controller artifacts, and one independent pre-Gold verifier run in order.
- Authorized endpoint: `VERIFIED_PRE_GOLD` with `evaluation=null`; Gold, U1-D metrics, reservation, Stage3B, cache writes, implementation changes, and automatic retries remain prohibited.
- Current status: `APPROVED_GOVERNANCE_PENDING_SYNTHETIC_REBINDING`.

### Stage4B-U1-D v2.3.1 Post-Approval Synthetic Rebinding

- Approval-governance commit: `53850f58e57f51b3c6067ed3108edff6b99a2dfc`.
- Two complete runs each passed 50/50 with zero failures, errors, or skips.
- Both complete evidence outputs are 11,640 bytes with SHA-256 `9D40C0B9B0C8F03CBC5545CA8F2390CCE9EABDC3B08B041B092FB3A76492FF34`.
- Evidence binds 22 implementation files, including final approved `AGENTS.md`, plus the committed request, manifest, and approval decision.
- No official development, source audit, official ranking/cache, Gold, reservation, or Stage3B access occurred.
- Audit: `docs/STAGE4B_U1_PREGOLD_RESUMPTION_V2_3_1_SYNTHETIC_REBINDING_AUDIT.md`.
- Current status after this evidence commit is pushed: `SYNTHETIC_REBINDING_VERIFIED_FORMAL_PREFLIGHT_AUTHORIZED`.

### Stage4B-U1-D v2.3.1 Formal Preflight

- Execution count: one.
- Execution HEAD: `a963befd812658972b156d2a7a26a488ac3c4482`.
- All Git, 22 implementation-hash, three governance-hash, 4,500/143,820 dual-ID, source-audit, fresh/legacy cache, v2.2 equivalence, and ten-path absence gates passed.
- Fresh cache SHA before and after remained `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D`.
- No retrieval/Gold metric was read or computed; reservation and Stage3B were not accessed.
- Audit: `docs/STAGE4B_U1_PREGOLD_V2_3_1_FORMAL_PREFLIGHT_AUDIT.md`.
- Current status: `PASS_V2_3_1_FORMAL_PREFLIGHT_CHANNEL_AUTHORIZED`.

### Stage4B-U1-D v2.3.1 Channel And Hard Failure 4

- One exact-path channel preparation passed; unlabeled units/queries are byte-identical to v2.2 and contain no prohibited controller keys.
- Channel audit: `docs/STAGE4B_U1_PREGOLD_V2_3_1_CHANNEL_PREPARATION_AUDIT.md`.
- The single require-existing controller run passed its post-computation cache fingerprint, then stopped before promotion because pending decisions differed from frozen v2.2 bytes.
- Failure code: `HARD_FAILURE_V2_3_1_DECISIONS_EQUIVALENCE`.
- No decisions, rankings, policy, controller execution audit, or `VERIFIED_PRE_GOLD` was created; fresh/legacy cache and all v2.2 reference hashes remain unchanged.
- Failure audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_4.md`.
- No verifier, evaluator, Gold metric, reservation, or Stage3B access occurred.
- Current status: `PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_4`; diagnosis or rerun requires a new approved review/Amendment.

### Stage4B-U1-D Pre-Gold Amendment 5A Approval

- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5A_IMPLEMENTATION_SYNTHETIC_ONLY` on 2026-07-13.
- Package commit: `81d8c34f1cf2539a4c0b81c6148047bc666e2f82`.
- Scope: decisions-only comparator, synthetic-only OS-temp capture, seven comparison layers, at least 24 new diagnostic tests, two byte-identical complete-suite runs, implementation audit/evidence, and an implementation-bound 5B package.
- Existing 50 tests must remain, so the complete suite must contain at least 74 tests.
- Official units/queries/source audit/cache/decisions/rankings, controller rerun, verifier, evaluator, Gold, reservation, and Stage3B remain prohibited.
- Controller modification is permitted only as a necessary mechanical extraction with unchanged checkpoint/CLI/formal/cache/pending/retrieval/ranking/policy behavior and explicit regression proof.
- Current status: `AMENDMENT_5A_APPROVED_IMPLEMENTATION_SYNTHETIC_ONLY`.

### Stage4B-U1-D Pre-Gold Amendment 5A Implementation And Synthetic Verification

- The controller remained byte-unchanged at checkpoint `stage4b_u1_v2_3_1`.
- Added a decisions-only seven-layer comparator, synthetic temporary capture, and a process-wide official-path guard.
- Added 48 diagnostic tests while retaining the original 50 tests; the complete suite passed 98/98 with zero failures, errors, or skips.
- Pre-5B static review added exact official input/output paths, registered source-digest validation without source-audit file access, an OS-temp gate, frozen v2.2 reference SHA, and a cache post-computation fingerprint.
- Two final complete evidence runs on unchanged tracked bytes were byte-identical with SHA-256 `3D44C14B82E911DDD37501731772A7594D7616BF12FE278D2D4CCC103533057E`.
- The official-path guard recorded zero blocked or attempted accesses. No official comparator/capture, controller, verifier, evaluator, Gold, reservation, or Stage3B action occurred.
- Audit: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_IMPLEMENTATION_AUDIT.md`.
- Current status: `AMENDMENT_5A_SYNTHETICALLY_VERIFIED`; official diagnosis, controller rerun, and verifier remain unapproved.
- Next gate: an implementation-bound Amendment 5B approval request and Manifest must be pushed, then execution stops for independent review.

### Stage4B-U1-D Pre-Gold Amendment 5B Package

- Final Amendment 5A implementation/evidence binding: `9a060bd31e9c33be587f7ef5e64f86206922e59e`.
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_OFFICIAL_DIAGNOSTIC_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_MANIFEST.json`.
- Requested scope: post-approval 98-test rebinding, governance digest, one read-only preflight, one exact-path decisions-only capture, aggregate audit commit, and immediate stop.
- Official rankings, source-audit file, policy, evaluator/Gold, full controller, verifier, reservation, Stage3B, implementation changes, and retries remain prohibited.
- Current status: `AMENDMENT_5B_AWAITING_APPROVAL`; no 5B command has run.

### Stage4B-U1-D Amendment 5B Review 1 And Amendment 5A.1 Package

- Review date: 2026-07-14.
- Reviewed 5B package commit: `ceb755252540cf223aa18ac721443154c29cd07a`.
- Decision: `RETURN_AMENDMENT_5B_FOR_CHANNEL_INPUT_HASH_BINDING`.
- Sole blocker: the v2.3.1 unlabeled units, unlabeled queries, and controller channel audit were registered by absolute path but not independently frozen by expected SHA-256; audit-to-input consistency was therefore not an external package binding.
- Frozen units SHA-256: `114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA`.
- Frozen queries SHA-256: `6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B`.
- Frozen controller channel-audit SHA-256: `D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA`.
- The retained 5B boundaries remain decisions-only, aggregate-only, no rankings/policy/Gold/source-audit access, no formal artifacts, and immediate stop after a future approved diagnosis.
- Amendment 5A.1 requests implementation/synthetic-only authority for direct pre-read and post-computation/pre-audit checks of those three hashes, cleanup/no-audit failure behavior, at least six additional tests, two byte-identical complete-suite runs, and a revised implementation-bound 5B package.
- Current status: `AMENDMENT_5A_1_AWAITING_APPROVAL`. No 5B token, official preflight/capture, code modification, or synthetic run is authorized by this package.

### Stage4B-U1-D Pre-Gold Amendment 5A.1 Approval

- Decision date: 2026-07-14.
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5A_1_CHANNEL_INPUT_HASH_BINDING_IMPLEMENTATION_SYNTHETIC_ONLY`.
- Bound package commit: `3137ace0328dd24908f95737ea1dcbe0c8fe045e`.
- Authorized scope: add three required expected-SHA arguments, fail closed on three external channel-input hashes before semantic parsing/computation and again after diagnostic computation immediately before audit exclusive-create, retain cleanup/no-audit behavior, add at least six synthetic tests, and run at least 104 tests twice with byte-identical evidence.
- Allowed implementation files are limited to the capture, diagnostic synthetic runner, and diagnostic test file registered in the 5A.1 Manifest.
- Controller, retrieval, common, comparator, model/parameters, equivalence, ranking, endpoint, and stop rules remain frozen.
- Official inputs, rejected 5B token/preflight/capture, controller, verifier, evaluator, Gold, reservation, and Stage3B remain prohibited.
- Decision record: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_1_APPROVAL_DECISION.md`.
- Current status: `AMENDMENT_5A_1_APPROVED_IMPLEMENTATION_SYNTHETIC_ONLY`.

### Stage4B-U1-D Pre-Gold Amendment 5A.1 Implementation And Synthetic Verification

- The capture now requires three expected channel-input SHA arguments and validates regular-file status, frozen official expected values, and actual bytes before semantic parsing/cache loading/computation.
- The three channel-input SHA values are rechecked after diagnostic computation and temporary-decisions comparison/cleanup, immediately before audit creation; drift leaves no audit and temporary decisions remain cleaned.
- The controller, retrieval, common, and comparator files remain byte-unchanged; controller checkpoint remains `stage4b_u1_v2_3_1` and raw byte equivalence remains controlling.
- The original 98 tests remain and nine tests were added, for 107 total. Targeted capture tests passed 22/22 and the preliminary complete suite passed 107/107.
- Two final complete runner executions each passed 107/107 with zero failures/errors/skips and zero official-path access attempts.
- Both final evidence outputs were 20,495 bytes with SHA-256 `81A8A5960395F729B643A42505E7F947962B338CD97ADD0506636D3AA2020A67`; byte comparison was exact.
- The existing NumPy 2.4.6/`numexpr` ABI warning remained visible, but every test and evidence command exited zero.
- Audit: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_1_IMPLEMENTATION_AUDIT.md`.
- Current status: `AMENDMENT_5A_1_SYNTHETICALLY_VERIFIED`; official diagnosis, controller rerun, verifier, and Gold remain unapproved.
- Next gate: push this implementation/evidence commit, then create and push an implementation-bound 5B v2 package and stop.

### Stage4B-U1-D Pre-Gold Amendment 5B v2 Package

- Bound 5A.1 implementation/evidence commit: `e566eb861ec6028ca89a40c9aca7d06737f1eb8e`.
- Bound evidence: 20,495 bytes, SHA-256 `81A8A5960395F729B643A42505E7F947962B338CD97ADD0506636D3AA2020A67`, 107/107, zero failure/error/skip/official access.
- The units, queries, and controller channel-audit exact paths and external SHA-256 values are registered independently from channel-audit content.
- Requested sequence: approval governance commit/push, two 107-test post-approval rebinding runs, governance-binding commit/push, one read-only preflight, one exact decisions-only capture, aggregate audit commit/push, and immediate stop.
- Existing implementation token remains inert unless a future decision explicitly binds and approves this v2 package.
- Official rankings, policy, source-audit file, evaluator/Gold, full controller, verifier, reservation, Stage3B, code changes, cache mutation, equivalence relaxation, and retries remain prohibited.
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_V2_OFFICIAL_DIAGNOSTIC_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_V2_MANIFEST.json`.
- Current status: `AMENDMENT_5B_V2_AWAITING_APPROVAL`; no v2 command has run.

### Stage4B-U1-D Pre-Gold Amendment 5B v2 Approval

- Decision date: 2026-07-14.
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5B_V2_SINGLE_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC`.
- Bound package commit: `f43e22ef079701139d4437849be8ad57654f80d7`.
- Required order: approval governance push, two byte-identical 107-test rebinding runs, governance-binding/audit push, one read-only preflight, one exact decisions-only capture, aggregate audit push, and immediate stop.
- The three channel-input SHA values, cache SHA/bytes, and v2.2 reference-decisions SHA remain externally frozen.
- Full controller, rankings, policy, source-audit file, verifier, evaluator/Gold, reservation, Stage3B, implementation changes, cache mutation, retries, and automatic resumption remain prohibited.
- Approval decision: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_V2_APPROVAL_DECISION.md`.
- Current status: `AMENDMENT_5B_V2_APPROVED_REBINDING_REQUIRED`; no rebinding, preflight, or capture has run under this approval.

### Stage4B-U1-D Pre-Gold Amendment 5B v2 Post-Approval Rebinding

- Approval governance commit: `2ddf6e044c27e47385a558bdaca80cb6c31c4ffe`.
- The complete 107-test suite ran twice on the approved governance bytes; both runs passed 107/107 with zero failures/errors/skips and zero official-path access attempts.
- Both outputs were 20,495 bytes with SHA-256 `7D9C3527480ECDFFA87C943589538BCEFEFA3610A6D415719429CDE5D222D12E`; direct byte comparison passed.
- Governance binding covers the v2 request, Manifest, approval decision, final approved `AGENTS.md`, implementation commit `e566eb8...`, and rebinding evidence.
- The existing NumPy 2.4.6/`numexpr` ABI warning was emitted, but both commands exited zero.
- Evidence: `results/stage4b_u1_d_pregold_amendment_5b_v2_synthetic_rebinding.json`.
- Governance binding: `results/stage4b_u1_d_pregold_amendment_5b_v2_governance_binding.json`.
- Audit: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_V2_SYNTHETIC_REBINDING_AUDIT.md`.
- Current status after this evidence is committed and pushed: `AMENDMENT_5B_V2_REBINDING_VERIFIED_PREFLIGHT_AUTHORIZED`.

### Stage4B-U1-D Pre-Gold Hard Failure 5

- The only approved read-only preflight ran once on HEAD `4c10ad942a75af42b910b860fd4897b672160d5d` and passed every Git, governance, implementation, channel/cache/reference hash, count, dual-ID, namespace, source-digest, and output-absence gate.
- The only approved exact-command capture then generated decisions under an OS temporary directory and reached the decisions comparator.
- The comparator stopped while loading the frozen v2.2 reference decisions with `Incomparable heterogeneous decisions schema at line 2`.
- Failure code: `HARD_FAILURE_5_INCOMPARABLE_HETEROGENEOUS_REFERENCE_DECISIONS_SCHEMA`.
- No aggregate machine audit or narrative diagnostic audit was created, so no byte/canonical/schema/value/semantic difference classification is available.
- Post-failure checks confirmed zero temporary diagnostic entries, unchanged three channel hashes, unchanged cache SHA/210,714,667 bytes, unchanged reference-decisions SHA, and zero formal-output files.
- No ranking, policy, source-audit file, verifier, evaluator/Gold, reservation, or Stage3B access occurred.
- Audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_5.md`.
- Current status: `AMENDMENT_5B_V2_OFFICIAL_DIAGNOSTIC_STOPPED_HARD_FAILURE_5`; capture may not be retried without a new package-bound Amendment.

### Stage4B-U1-D Hard Failure 5 Review 1

- Review date: 2026-07-14.
- Reviewed commit: `deccd203059d05dc27ba80aca1ddb1e2ea8f616f`.
- Decision: `RETURN_FOR_REFERENCE_DECISIONS_SCHEMA_DIAGNOSTIC_AMENDMENT_PACKAGE`.
- Schema diagnostic execution, comparator change, official capture retry, controller rerun, verifier, and Gold remain unapproved.
- The review preserves the strict observed boundary: line-2 within-file schema rejection occurred before any byte/canonical/value/semantic comparison; it does not identify fields or justify normalization.
- The next work must be split into 5C-A implementation/synthetic authority and a later separately approved 5C-B single official schema-only scan.
- Review: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_5_REVIEW_1.md`.

### Stage4B-U1-D Pre-Gold Amendment 5C-A Package

- The request and machine-readable boundary are `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_APPROVAL_REQUEST.md` and `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_MANIFEST.json`.
- Requested implementation is isolated to one value-free JSONL schema inventory tool, one deterministic runner, and one new test file; existing comparator, capture, controller, retrieval, common, runners/tests, equivalence, and parameters remain frozen.
- The schema contract distinguishes null/bool/integer/finite-number/string/array/object, recursively inventories value-free nested structure, rejects duplicate keys/invalid or non-finite JSON, separates order-only differences, and selects the modal ordered signature with a lexicographic ordered-signature tie-break.
- The existing 107 tests must remain; at least 12 new tests make the complete-suite minimum 119. Two unchanged-byte runs must be all-pass with zero failure/error/skip/official access and byte-identical evidence.
- No official file read, schema scan, comparator/capture/controller execution, verifier, evaluator/Gold, reservation, or Stage3B access is requested.
- Current status: `AMENDMENT_5C_A_AWAITING_APPROVAL`. The package itself authorizes no implementation or test command.

### Stage4B-U1-D Pre-Gold Amendment 5C-A Approval

- Decision date: 2026-07-14.
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5C_A_REFERENCE_SCHEMA_INVENTORY_IMPLEMENTATION_SYNTHETIC_ONLY`.
- Bound package commit: `a8caa2a3b26ae13d0b149e4995e3a017e8edb2e7` plus the eight historical commits registered in its Manifest.
- Authorized scope is limited to three new independent files for value-free schema inventory, deterministic complete-suite verification, and isolated tests, plus approval/audit/evidence/future 5C-B governance outputs.
- Existing 107 tests must remain; at least 12 additions make the complete-suite minimum 119. Two unchanged-byte runs must pass with zero failures/errors/skips/official access and byte-identical evidence.
- Existing implementation/tests, official inputs/artifacts, prior evidence/failures, comparator/capture/controller, verifier/evaluator/Gold, reservation, and Stage3B remain frozen.
- Approval decision: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_APPROVAL_DECISION.md`.
- Current status: `AMENDMENT_5C_A_APPROVED_IMPLEMENTATION_SYNTHETIC_ONLY`.

### Stage4B-U1-D Pre-Gold Amendment 5C-A Implementation And Synthetic Verification

- Added only the approved inventory, deterministic runner, and isolated test files; no existing implementation/test or official/historical artifact was modified or deleted.
- The inventory is value-free, detects nested duplicate keys and non-finite JSON, distinguishes all frozen JSON types, recursively represents object/array element schemas, separates ordered/structural signatures, and deterministically selects the main ordered schema.
- The original 107 tests remain and 24 inventory tests were added, for 131 total.
- One preliminary complete run initially failed only because the new runner matched required proof-test suffixes globally and found an older duplicate suffix. The runner-only matcher was scoped to the new test module; no evidence was written and no official path was accessed on the failed command.
- The final governance-bound complete suite ran twice on unchanged implementation bytes. Both runs passed 131/131 with zero failures/errors/skips and zero official-path access attempts.
- Both final evidence outputs were 22,234 bytes with SHA-256 `0D13392B5C96BAD7EC4D67C22A7515B4A6D211C8EFBB3A4486F9BA5531A1EF7C`; direct byte comparison passed.
- The known NumPy 2.4.6/`numexpr` 1.x ABI warning remained visible through the unchanged legacy import chain, but every accepted run exited zero.
- Evidence: `results/stage4b_u1_d_pregold_amendment_5c_a_synthetic_verification.json`.
- Audit: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_A_IMPLEMENTATION_AUDIT.md`.
- Current status: `AMENDMENT_5C_A_SYNTHETICALLY_VERIFIED`; official schema scan and all comparator/capture/controller/verifier/Gold actions remain unapproved.

### Stage4B-U1-D Pre-Gold Amendment 5C-B Package

- Bound implementation/evidence commit: `492a59b2f4daccd3e123f2b6cc49cd896d5009d1`.
- Bound 5C-A evidence: 22,234 bytes, SHA-256 `0D13392B5C96BAD7EC4D67C22A7515B4A6D211C8EFBB3A4486F9BA5531A1EF7C`, 131/131 with 24 inventory tests and zero failure/error/skip/official access.
- Requested sequence: package-bound approval governance, two 131-test post-approval rebinding runs, governance-binding push, one SHA-only preflight, one exact-command value-free official schema scan, aggregate audit push, and immediate stop.
- The sole requested official input is the frozen v2.2 reference decisions file with SHA-256 `6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7`.
- Machine output is restricted to schema names/types/nesting/signatures, aggregate counts/line ranges/differences, and pre/post SHA/cleanup gates. Values, raw/salted IDs, rows, rankings, policy, Gold, and new decisions are prohibited.
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_B_OFFICIAL_SCHEMA_SCAN_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_B_MANIFEST.json`.
- Current status: `AMENDMENT_5C_B_AWAITING_APPROVAL`; no 5C-B command has run.

### Stage4B-U1-D Pre-Gold Amendment 5C-B Approval And Rebinding

- Decision date: 2026-07-14.
- Decision: `APPROVE_STAGE4B_U1_D_AMENDMENT_5C_B_SINGLE_REFERENCE_SCHEMA_SCAN`.
- Bound package commit: `e5a6c5479dbd125ebb58b95e9594fadde6b6719d` plus the eight historical commits registered in the approval decision.
- Approval governance commit: `fce67da87d155b1026cbe0670f606201ede0ac4b`.
- The complete 131-test suite ran twice on the final approved governance bytes; both runs passed 131/131 with 24 inventory tests and zero failure/error/skip/official access.
- Both rebinding outputs were 22,234 bytes with SHA-256 `F16C91BF170ABDFC6784F368D6247E0AA8CDC9ECFB6671C71DFA9BD35CCF297C`; direct byte comparison passed.
- Rebinding/governance commit: `b09668f47cd31df2be73446cadacf84d996418f9`.
- The known NumPy 2.4.6/`numexpr` ABI warning remained visible, but both commands exited zero.

### Stage4B-U1-D Pre-Gold Amendment 5C-B Official Schema Scan

- The only read-only formal preflight passed on synchronized HEAD `b09668f47cd31df2be73446cadacf84d996418f9`.
- Preflight verified 17 implementation blobs, eight current frozen files, six governance-bound files, the exact command and five absent formal outputs. It read the frozen reference only as bytes for SHA-256 and did not parse JSONL.
- The only exact-command official schema scan exited zero without retry.
- The 4,500 rows contain two ordered and two structural schemas: 2,446 rows in the main schema and 2,054 rows in the second schema.
- The schemas have the same field set and order. The second schema differs only at eight field paths: `ordered_rank` is `null` instead of `integer`, and seven numeric controller fields are `null` instead of `finite_number`.
- Added, removed, nesting-changed, and order-only path counts are all zero.
- Machine inventory: 17,229 bytes, SHA-256 `FA56AC3CB78EE746BF71AF0CEF40606E56B9D13C120F10A2A87400EA42CE3A5E`.
- Independent validation passed the exact whitelist, recursive value-free schema, digest/count/main-selection, source-integrity, exclusive-create/cleanup, and five-formal-output absence gates without reopening the reference.
- Audit: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_B_OFFICIAL_SCHEMA_SCAN_AUDIT.md`.
- Current status: `REFERENCE_DECISIONS_SCHEMA_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW`. Comparator change, capture/controller rerun, verifier, and Gold remain unapproved.

### Stage4B-U1-D Pre-Gold Amendment 5C-B Review 1

- Review date: 2026-07-14.
- Reviewed final commit: `e5f28f664449c02b12a129aaa2a011bad84dab91`.
- Decision: `ACCEPT_AMENDMENT_5C_B_REFERENCE_SCHEMA_DIAGNOSTIC`.
- Hard Failure 5 direct cause is confirmed: the comparator's file-level complete-schema homogeneity assumption rejects the legal nullable schema that first appears on line 2.
- The evidence excludes corruption, missing fields, field-order drift, or nesting drift as the direct line-2 cause.
- Hard Failure 4 remains unclassified because no new v2.3.1 temporary decisions were generated or compared.
- Comparator change, capture/controller rerun, verifier, and Gold remain unapproved.
- Review: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5C_B_REVIEW_1.md`.

### Stage4B-U1-D Pre-Gold Amendment 5D-A Package

- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_A_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_A_MANIFEST.json`.
- Requested implementation is limited to the comparator, diagnostic synthetic runner, and diagnostic tests.
- The only allowed comparator semantic delta is removing the file-level homogeneous complete-type-signature rejection and bumping the diagnostic version/checkpoint.
- Per-query field set/order/type/discrete/float/ULP/semantic comparison, aggregate output, raw-byte controlling gate, no-normalization, capture/controller, all parameters, and all official boundaries remain frozen.
- The current 131 tests are the traceable baseline. At least 12 heterogeneous-schema additions require a complete-suite minimum of 143, followed by two byte-identical all-pass runs with zero official access.
- Current status: `AMENDMENT_5D_A_AWAITING_APPROVAL`. The package authorizes no implementation, synthetic execution, or official read.

### Stage4B-U1-D Pre-Gold Amendment 5D-A Approval

- Decision date: 2026-07-14.
- Decision: `APPROVE_STAGE4B_U1_D_PREGOLD_AMENDMENT_5D_A_HETEROGENEOUS_SCHEMA_COMPARATOR_IMPLEMENTATION_SYNTHETIC_ONLY`.
- Bound package commit: `33ce115f78840956fcc7bda0c3f4e172579350e7` plus the twelve historical commits registered in its Manifest.
- Allowed implementation is limited to the comparator, diagnostic synthetic runner, and diagnostic tests.
- Comparator changes are limited to version/checkpoint v2 and removal of the loader's file-level complete-schema homogeneity rejection.
- Per-query comparison, aggregate keys, raw-byte controlling gate, no-normalization, capture/controller and all scientific parameters remain frozen.
- The 131-test baseline must remain; at least 12 additions require a minimum complete suite of 143 and two byte-identical all-pass runs with zero official access.
- Approval decision: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_A_APPROVAL_DECISION.md`.
- Current status: `AMENDMENT_5D_A_APPROVED_IMPLEMENTATION_SYNTHETIC_ONLY`.

### Stage4B-U1-D Pre-Gold Amendment 5D-A Implementation And Synthetic Verification

- Comparator schema/checkpoint are now `stage4b_u1_decisions_diagnostic_v2` / `stage4b_u1_decisions_diag_v2`.
- The comparator diff only updates those identifiers and removes the loader's file-level complete-schema homogeneity rejection; per-query comparison code and output keys remain unchanged.
- Twelve heterogeneous-schema tests were added to the accepted 131-test baseline, producing 143 complete tests.
- Comparator targeted verification passed 46/46 after one test-only regex correction recorded in the audit.
- One preliminary complete run and both final complete runs passed 143/143 with zero failures/errors/skips and zero official-path access attempts.
- Both final evidence outputs were 29,643 bytes with SHA-256 `08695B4305D9919049DFE86870772B9E9F66751DA6D2FF4D43CEF2A912A62008`; direct byte comparison passed.
- All 13 Manifest frozen files retained their exact hashes. The 5C-B machine inventory was explicitly blocked and not used as a fixture.
- The known NumPy 2.4.6/`numexpr` ABI warning remained visible, but all accepted test commands exited zero.
- Audit: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_A_IMPLEMENTATION_AUDIT.md`.
- Current status: `AMENDMENT_5D_A_SYNTHETICALLY_VERIFIED`; Hard Failure 4 remains unclassified and all official execution remains unapproved.

### Stage4B-U1-D Pre-Gold Amendment 5D-B Package

- Bound implementation/evidence commit: `02f46447e4cd69a15d2af14ee1fc62f9eb4f8bb9`.
- Bound 5D-A evidence: 29,643 bytes, SHA-256 `08695B4305D9919049DFE86870772B9E9F66751DA6D2FF4D43CEF2A912A62008`, 143/143 with zero failure/error/skip/official access and byte-identical final reruns.
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_B_OFFICIAL_DIAGNOSTIC_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_B_MANIFEST.json`.
- Requested sequence: package-bound approval governance, two 143-test post-approval rebinding runs, governance-binding push, one read-only preflight, one exact-command official decisions-only capture, aggregate audit push, and immediate stop.
- The five permitted inputs retain the externally frozen channel, cache, and v2.2 reference-decisions fingerprints. Rankings, policy, source audit, 5C-B machine inventory, evaluator/Gold, reservation, and Stage3B remain outside the read boundary.
- The unchanged capture enforces the historical `stage4b_u1_d_pregold_amendment_5b_official_decisions_diagnostic.json` machine-output path. Hard Failure 5 left it absent; 5D-B preflight must hard-fail if it exists, and no overwrite or rename is requested.
- Raw byte equality remains controlling. Comparator v2 may only provide aggregate classification of any difference; no normalization or equivalence relaxation is requested.
- Current status: `AMENDMENT_5D_B_AWAITING_APPROVAL`. The package authorizes no synthetic rebinding, official preflight, capture, controller, verifier, evaluator, or Gold action.

### Stage4B-U1-D Pre-Gold Amendment 5D-B Approval And Rebinding

- Approval binds package `f67061e753b03a5cf46d7a7c92b5a95fc79b0ef8` and implementation/evidence `02f46447e4cd69a15d2af14ee1fc62f9eb4f8bb9`.
- Final approval-governance HEAD before rebinding: `1c46dc1b69f8381598aacb9f3b1e27561c7f9ee2`.
- The complete 143-test suite ran twice on the final approved governance bytes. Both runs passed 143/143 with zero failure/error/skip/official access.
- Both complete outputs were 29,643 bytes with SHA-256 `264200C2EBEDA1D0B214F824B77C89FC5BBE82D3BE0836FAAB9486EACAACF368`; direct byte comparison passed.
- The known NumPy 2.4.6/old `numexpr` ABI warning remained visible, but both commands exited zero.
- Governance binding: `results/stage4b_u1_d_pregold_amendment_5d_b_governance_binding.json`.
- Audit: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5D_B_SYNTHETIC_REBINDING_AUDIT.md`.
- Current status: `AMENDMENT_5D_B_APPROVED_REBINDING_VERIFIED_PREFLIGHT_PENDING`. No official input has been opened and the single formal preflight has not run.

### Stage4B-U1-D Pre-Gold Hard Failure 6

- The only formal preflight ran once on synchronized clean HEAD `2447ad234c160c6e615d81b33dc4ede7ecaa18da`.
- Git, ancestry, implementation, governance binding, final `AGENTS.md`, exact command, output absence, and temp-residue gates passed.
- The preflight then failed at the OS temp parent equality expression because the comparison did not normalize a trailing directory separator before string equality.
- Failure occurred before regular-file checks, SHA reads, or semantic parsing of any of the five official inputs. The capture token was not passed and capture invocation count remains zero.
- Post-failure metadata confirmed no machine/narrative audit, no formal output, and no diagnostic temporary residue.
- Audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_6.md`.
- Current status: `AMENDMENT_5D_B_OFFICIAL_DIAGNOSTIC_STOPPED_HARD_FAILURE_6`; the 5D-B preflight authorization is consumed and Hard Failure 4 remains unclassified.

### Stage4B-U1-D Hard Failure 6 Review And Amendment 5E-A Package

- Review: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_6_REVIEW_1.md`.
- Decision: `ACCEPT_HARD_FAILURE_6_AUDIT` and `RETURN_FOR_AMENDMENT_5E_A_PACKAGE`.
- The failure is classified as an untested preflight path-equivalence implementation defect: trailing directory separators were not normalized before string equality. It is not evidence of official input, cache, comparator, capture, or controller drift.
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5E_A_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5E_A_MANIFEST.json`.
- Requested implementation is limited to one new standard-library Windows directory-equivalence helper, one new synthetic test module, and deterministic-runner governance/count/evidence binding.
- The verified 143-test 5D-B rebinding evidence is the baseline. At least 12 additions require a complete-suite minimum of 155, two byte-identical all-pass runs, zero official access, and zero formal-preflight/token/capture invocation.
- Capture, comparator, controller, retrieval, common, scientific parameters, exact capture command and raw-byte gate remain frozen.
- Current status: `AMENDMENT_5E_A_AWAITING_APPROVAL`. The package authorizes no implementation, synthetic execution, official access, formal preflight, token use, or capture.

### Stage4B-U1-D Pre-Gold Amendment 5E-A Implementation And Synthetic Verification

- Approval binds package `19f16f559f0b1f3b59ef24a04e368f99ae3635e3`; approval governance commit is `461939434206764555b917c5971956e6951ff4dd`.
- Added a standard-library fail-closed Windows directory-equivalence helper and 18 synthetic tests; only the approved deterministic runner was modified.
- The helper accepts exact canonical ordinal-ignore-case directory equality and rejects relative, missing, file, reparse, parent, child, unrelated, and prefix-collision paths.
- The complete suite increased from 143 to 161 tests. Both final runs passed 161/161 with zero failure/error/skip/official access and zero formal-preflight/token/capture invocation.
- Both evidence files were 36,518 bytes with SHA-256 `84C58CBA9801A6EB8DFAF4ED6688BB5FCBD5777729FD833083E16CB630FFED83`; direct byte comparison passed.
- All 15 Manifest frozen files retained their registered SHA. Exact capture command and raw-byte equivalence remained unchanged.
- Evidence: `results/stage4b_u1_d_pregold_amendment_5e_a_synthetic_verification.json`.
- Audit: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5E_A_IMPLEMENTATION_AUDIT.md`.
- Current status: `AMENDMENT_5E_A_SYNTHETICALLY_VERIFIED`. Hard Failure 4 remains incomplete; 5E-B preflight/capture, controller, verifier and Gold are not approved.

### Stage4B-U1-D Pre-Gold Amendment 5E-B Package

- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5E_B_OFFICIAL_DIAGNOSTIC_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5E_B_MANIFEST.json`.
- The package binds 5E-A implementation/evidence commit `a8b064a4a2133aea27cbe9b85978237fc3dae661` and the Hard Failure 6/5D-B history.
- A future approved preflight must hash-check and directly import/call the tested helper before any permitted official input metadata/content check; copied inline path-equivalence logic is prohibited.
- The requested capture command, five-input read boundary, model/parameters, token string, comparator semantics and raw-byte gate are unchanged from 5D-B.
- A future approval must first require two byte-identical 161-test post-approval rebinding runs and governance binding.
- Current status: `AMENDMENT_5E_B_AWAITING_APPROVAL`. This package authorizes no rebinding, preflight, token, capture, controller, verifier, evaluator or Gold action.

### Stage4B-U1-D Pre-Gold Hard Failure 7

- Approval governance commit: `f2f2e249e4e7a52fcc44b61a2245d8d50d79106d`.
- Post-approval rebinding/governance commit: `3185c3bd4ffd3eb2bc61b52fdf18a3367b9dca76`.
- Two 161-test rebinding runs passed with byte-identical 36,518-byte evidence SHA-256 `BF4C668C76C4B8545882C894F241038765AFD8DD263B4195D9E2D654B7B9FC1A`.
- The only formal preflight passed A, then failed in B because a raw `gold` substring denylist matched the approved `pregold` machine-audit output path.
- The failure preceded helper import/call and every official input metadata/content operation. Helper, official access, token and capture counts remained zero.
- Post-failure checks found no machine/narrative audit, no formal output and no diagnostic residue.
- Audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_7.md`.
- Current status: `AMENDMENT_5E_B_FORMAL_PREFLIGHT_STOPPED_HARD_FAILURE_7`; Hard Failure 4 remains unclassified and 5E-B cannot be retried.

### Stage4B-U1-D Pre-Gold Amendment 5F-A Package

- Hard Failure 7 Review 1 accepts commit `f18d551b17f1bbed645ac159ebe52b7d6b9d8e54` and returns the project for an implementation/synthetic-only Amendment.
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5F_A_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5F_A_MANIFEST.json`.
- Requested implementation scope is limited to one new typed argument-policy helper, one new synthetic test module, and governance/evidence-only updates to the existing diagnostic deterministic runner.
- The helper contract freezes exact argv equality, an ordered typed flag allowlist, per-role exact value binding, explicit prohibited-role rejection, and no raw `gold` value-substring denylist.
- The 161-test 5E-B rebinding is the baseline. A future approved implementation must add at least 16 tests and run a complete suite of at least 177 tests twice with byte-identical evidence and zero official access/path-helper official invocation/preflight/token/capture.
- A future 5F-A implementation/evidence push must stop for independent review. A 5F-B package may be assembled only after that review explicitly accepts 5F-A.
- Current status: `AMENDMENT_5F_A_AWAITING_APPROVAL`. This package authorizes no implementation, synthetic execution, official access, helper official-boundary check, preflight, token, capture, controller, verifier, evaluator, or Gold action.

### Stage4B-U1-D Pre-Gold Amendment 5F-A Implementation

- Approval governance commit: `273341960858930246ae0c1441440aede0403a65`.
- Added a standard-library typed capture-argument policy helper and 44 synthetic tests; modified only the approved deterministic runner among existing implementation/test files.
- Exact argv equality remains controlling. The helper fixes 32 elements and 15 ordered flags, applies typed/per-role exact binding, accepts the frozen `pregold` output spelling, explicitly rejects prohibited roles, and has no raw `gold` value-substring denylist.
- Targeted tests passed 44/44. Two final complete runs passed 205/205 with zero failure/error/skip/official access/path-helper official invocation/preflight/token/capture.
- Both final outputs were 51,922 bytes with SHA-256 `A5B97077AD9A0C62EBFCAE9D70FC8B5BFAD19CCB32FF3A53E1FCF4BDB216D189`; direct byte comparison passed. Tracked-byte digest: `B58E85239F001B532B5CF378998B804B1202C5D6FF148311EF939DC4B3B4EA34`.
- All 17 Manifest frozen files retained their exact SHA. Exact argv, token, scientific parameters and raw-byte equivalence remained unchanged.
- Audit: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5F_A_IMPLEMENTATION_AUDIT.md`.
- Evidence: `results/stage4b_u1_d_pregold_amendment_5f_a_synthetic_verification.json`.
- Current status: `AMENDMENT_5F_A_SYNTHETICALLY_VERIFIED`, awaiting independent review. 5F-B package assembly and all official execution remain unapproved.

### Stage4B-U1-D Pre-Gold Amendment 5F-A Review 1

- Independent review accepts the implementation/evidence commit `e7b688d4b67db596df1d447e2cf70f12f0ea5d0b` and the two byte-identical 205-test runs.
- Accepted evidence remains 51,922 bytes, SHA-256 `A5B97077AD9A0C62EBFCAE9D70FC8B5BFAD19CCB32FF3A53E1FCF4BDB216D189`, with zero official access/path-helper official invocation/preflight/token/capture.
- The review authorizes only assembly of an implementation-bound 5F-B package. It does not authorize rebinding, helper calls, preflight, token, capture, controller, verifier or Gold.
- Review: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5F_A_REVIEW_1.md`.

### Stage4B-U1-D Pre-Gold Amendment 5F-B Package

- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5F_B_OFFICIAL_DIAGNOSTIC_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5F_B_MANIFEST.json`.
- The package binds the accepted 5F-A implementation/evidence and freezes the typed helper, existing path helper, 25 unchanged current-tree hashes plus the historical implementation-time `AGENTS.md` Git blob, five official inputs, unchanged 32-element capture argv and aggregate-only output boundary. Post-approval evidence must separately bind all 26 current hashes including final governance `AGENTS.md`.
- A future approval is requested for approval governance, two byte-identical 205-test rebinding runs, governance binding, one A/B/C/D preflight, conditionally one unchanged capture, aggregate audit push and immediate stop.
- Preflight order is fixed: A Git/governance/hashes/output absence; B hash-bind and directly call the typed helper; C hash-bind and directly call the path helper; D only then access five official inputs. Capture is conditional on all gates passing.
- Current status: `AMENDMENT_5F_B_AWAITING_APPROVAL`. The package authorizes no rebinding, helper invocation, preflight, token, official access, capture, controller, verifier, evaluator or Gold action.

### Stage4B-U1-D Pre-Gold Amendment 5F-B Approval And Rebinding

- Approval governance commit: `84d39707dee15729dc0c35c85a16f4e31dac89e4`.
- Two post-approval complete suites passed 205/205 with 44 typed-policy tests and zero failure/error/skip/official access/path-helper official invocation/preflight/token/capture.
- Both outputs were 51,922 bytes with SHA-256 `829289F10B1C7B39BBE6B37ACF51DCB265764FD10A8DA55892F60D50F6D2CB09`; direct byte comparison passed.
- Rebinding/governance commit: `052e8ecc04f566b75666d5cc96df74d2ed5061e4`.

### Stage4B-U1-D Pre-Gold Hard Failure 8

- The single formal preflight stopped at the first A-gate comparison.
- Local HEAD, origin/main and GitHub main were all correctly synchronized at `052e8ecc04f566b75666d5cc96df74d2ed5061e4`.
- The wrapper incorrectly asserted `052e8ece1839ff253f8aeb84d5f828377be74829`; both values share the short prefix `052e8ec`.
- B/C/D, both helpers, all five official inputs, token and capture were not reached. Post-failure output/residue metadata checks were all clear.
- Audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_8.md`.
- Current status: `AMENDMENT_5F_B_FORMAL_PREFLIGHT_STOPPED_HARD_FAILURE_8`. The preflight authorization is consumed and no retry is allowed without a new package-bound Amendment.

### Stage4B-U1-D Hard Failure 8 Review And Amendment 5G-A Package

- Independent review accepts the Hard Failure 8 audit and the 5F-B post-approval rebinding evidence. Review: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_8_REVIEW_1.md`.
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_MANIFEST.json`.
- The requested implementation is limited to one pure execution-head binding validator, one new synthetic test module, and governance/evidence-only deterministic-runner changes.
- The proposed helper accepts caller-supplied Git/governance facts only. It must validate full lowercase 40-character SHAs, three-way head equality, direct approval parentage, exact changed paths, required ancestry, clean-worktree and governance/evidence presence without filesystem, Git, subprocess, official-path, helper, token or capture access.
- The accepted baseline is 205 tests. A future approved implementation must add at least 16 tests and run at least 221 tests twice on identical tracked bytes, with byte-identical evidence and all execution/access counters at zero.
- Current status: `AMENDMENT_5G_A_AWAITING_APPROVAL`. This package authorizes no implementation, synthetic execution, real Git/GitHub check, second preflight, helper official call, official input access, token, capture, controller, verifier, Gold or 5G-B assembly.

### Stage4B-U1-D Pre-Gold Hard Failure 9

- 5G-A approval governance was committed and pushed at `fd50bc30f5acbf4955e3a051fbee70062e6e168c` before implementation.
- The new pure-value helper, new test module and runner update remained within the three approved paths; all 24 frozen hashes remained unchanged.
- The only targeted execution-head test invocation passed 41/41 with zero failure/error/skip.
- The only preliminary complete-runner invocation stopped before test execution because required active-proof suffixes were not globally unique.
- `test_missing_governance_binding_is_rejected` collided with an existing goldfree test; `test_helper_uses_only_python_standard_library` collided with the existing path-equivalence test and was also registered twice in the runner tuple.
- No evidence path was created, complete-suite tests run was 0, and official/helper/preflight/token/capture counters remained zero.
- Audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_9.md`.
- Current status: `AMENDMENT_5G_A_SYNTHETIC_VERIFICATION_STOPPED_HARD_FAILURE_9`. No correction or synthetic retry is allowed without a new package-bound Amendment.

### Stage4B-U1-D Hard Failure 9 Review And Amendment 5G-A.1 Package

- Independent review accepts the Hard Failure 9 audit and freezes checkpoint `d1c7cf9d78563e30a1e0fe0d6812b36d15b95a9a`. Review: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_9_REVIEW_1.md`.
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_1_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_1_MANIFEST.json`.
- The helper remains frozen at 6,318 bytes and SHA-256 `517C5C4DB22A82B4CBCA3D8BB751AAE60C0DCC5B5948CC8419D8770A9CC3D174`.
- A future approved repair is limited to two execution-head test-name tokens, their corresponding runner suffixes, a pre-discovery tuple-uniqueness gate and exact 246/41/44 count gates.
- The requested sequence has no preliminary runner: approval governance, one source-only inventory, one 41/41 targeted run, two final 246/246 runs, byte comparison, audit/push and stop.
- Current status: `AMENDMENT_5G_A_1_AWAITING_APPROVAL`. This package authorizes no repair, inventory, test, synthetic retry or official action.

### Stage4B-U1-D Amendment 5G-A.1 Minimal Repair And Synthetic Verification

- Approval governance commit: `3d818cee86e1faca16c2bdab3baf4fd5411cff75`.
- The only test changes were two execution-head-specific function-name tokens; the runner changed only the corresponding suffixes, tuple uniqueness gate and exact 246/41/44 counts.
- The helper remained 6,318 bytes with SHA-256 `517C5C4DB22A82B4CBCA3D8BB751AAE60C0DCC5B5948CC8419D8770A9CC3D174`; all 24 frozen hashes remained unchanged.
- One source-only inventory passed with 246 definitions and 135/135 globally unique required suffixes. The only targeted run passed 41/41.
- No preliminary runner was used. Both final complete runs passed exactly 246/246 with 41 execution-head and 44 typed-policy tests.
- Both evidence files were 69,144 bytes with SHA-256 `A6285498FCFE767297D7156B87CA6034A993B2DFBB167EF7DFA813E9ADD55292`; direct byte comparison passed.
- Audit: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_1_IMPLEMENTATION_AUDIT.md`.
- Current status: `AMENDMENT_5G_A_1_SYNTHETICALLY_VERIFIED`, awaiting independent review. Official execution and 5G-B remain unapproved.

### Stage4B-U1-D Amendment 5G-A.1 Review And Amendment 5G-B Package

- Independent review accepts implementation/evidence commit `c21f3f58b2b1d4ccf235daba9c85937daedf4e3b`; review: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_1_REVIEW_1.md`.
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_OFFICIAL_DIAGNOSTIC_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_MANIFEST.json`.
- The package freezes the accepted helper/runner/test/evidence hashes, unchanged 32-element capture command, future approval changed paths and exact three-path rebinding/governance direct-child set.
- A future approval may authorize two exact 246-test rebinding runs, one derived actual execution-HEAD validation, one ordered A/B/C/D preflight and one unchanged capture only if every earlier gate passes.
- Current status: `AMENDMENT_5G_B_AWAITING_APPROVAL`. The package itself authorizes no rebinding, real execution-head check, preflight, official input access, token, capture, controller, verifier or Gold.

### Stage4B-U1-D Pre-Gold Hard Failure 10

- Approval governance was committed and pushed at `79e69eab874f669d79d433fa965f5f5f48659332` with the exact approved two-path set.
- The complete runner was invoked exactly twice. Both runs passed 246/246 with 41 execution-head tests, 44 typed-policy tests, zero failure/error/skip and zero official/helper/preflight/token/capture counters.
- Both 69,144-byte evidence files had SHA-256 `00281BED7BC0DF10D47382CC47D0884BFCD331F0CB92EFC0B51F0FF176827A2A`; direct byte equality passed.
- Before the authorized three-path commit, governance validation failed because `$g.bound_files.psobject.Properties.Count` returned an 11-element array of per-property counts rather than scalar collection cardinality.
- Read-only diagnosis confirmed the governance object actually contains the 11 required bound-file properties. The validation was not corrected or rerun.
- No authorized three-path direct child, derived execution-HEAD call, preflight, official input access, token or capture occurred.
- Audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_10.md`.
- Current status: `AMENDMENT_5G_B_REBINDING_GOVERNANCE_STOPPED_HARD_FAILURE_10`. A new independent review and package-bound recovery Amendment are required.

### Stage4B-U1-D Hard Failure 10 Review And Amendment 5G-B.1 Package

- Independent review accepts the Hard Failure 10 audit and freezes checkpoint `aab591b92804fd1226a62751c38d056918f71b41`.
- The two 246/246 runs and SHA `00281BED...` are accepted only as historical failure evidence, not as an active execution binding.
- Review: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_10_REVIEW_1.md`.
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_MANIFEST.json`.
- The first package commit `9536ffb4ce845aeff9db3552f890612ca6e9e2a3` was independently rejected: its sort/comparison was case-insensitive, parsed `PSObject.Properties` could not prove raw JSON duplicate-key absence, and the complete real precommit command was not frozen. It is not approvable.
- Package Review 1: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_PACKAGE_REVIEW_1.md`.
- The corrected package freezes strict UTF-8 raw ingestion, Python `object_pairs_hook` duplicate rejection before object materialization, bound-file case-fold collision rejection, and PowerShell `Sort-Object -CaseSensitive -Unique` plus `Compare-Object -CaseSensitive`.
- The complete 195-line real validator is frozen at 15,966 bytes and SHA-256 `0F066387B8523B0EA387444076A1113913082D283C28C2DE3FFB33872D558249`; future approval must contain the package commit, decimal byte token and exact SHA, and may not add a wrapper expression.
- A future corrected-package-bound approval may authorize one in-memory semantics wrapper, exactly two fresh 246-test runs, one frozen real precommit validation and one exact-three-path direct-child, followed by immediate stop.
- Current status: `CORRECTED_AMENDMENT_5G_B_1_PACKAGE_AWAITING_APPROVAL`. No validator semantics, synthetic run, direct-child, execution-head helper, preflight or official action is authorized by the package itself.

### Stage4B-U1-D Pre-Gold Hard Failure 11

- Corrected package `48a9c143...` was approved, and approval-governance commit `0e28fba6647bfd98634ebb8d1565e862dcf16920` was pushed as its exact two-path direct child.
- Local HEAD, origin/main and GitHub main matched and the worktree was clean before the one-time semantics wrapper.
- The wrapper was invoked exactly once and started exactly one Python parser process. That process emitted stderr at its string-source line 6; PowerShell terminated the wrapper as `NativeCommandError`, so no nine-fixture success summary was produced.
- The wrapper was not corrected or rerun. Complete synthetic runs, fresh artifacts, real validator invocations and fresh direct-child commits all remained zero.
- All three fresh paths remained absent. The three historical 5G-B artifacts retained their frozen bytes and SHA values.
- Audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_11.md`.
- Current status: `AMENDMENT_5G_B_1_VALIDATOR_SEMANTICS_STOPPED_HARD_FAILURE_11`. A new independent review and package-bound Amendment are required.

### Stage4B-U1-D Hard Failure 11 Review And Amendment 5G-B.1.1 Package

- Independent review accepts the Hard Failure 11 audit and confirms that the one-time semantics gate was consumed correctly.
- The line-aligned evidence supports, but does not fully prove without the missing traceback, that an expected negative raw-JSON rejection escaped as an unhandled Python exception and reached PowerShell as native stderr.
- Review: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_11_REVIEW_1.md`.
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_MANIFEST.json`.
- The real 195-line precommit validator remains frozen at 15,966 bytes and SHA-256 `0F066387B8523B0EA387444076A1113913082D283C28C2DE3FFB33872D558249`.
- The package separately freezes a 122-line, 7,890-byte PowerShell semantics wrapper with SHA-256 `DFA95A904CE371F283B8DBA8BB4D98CC048F345F536C0E7D0D6DB8073DF9E16C` and a byte-identical embedded 46-line, 2,284-byte Python source with SHA-256 `D0D3D6FC37AD0C2649A7A7F88EFA944C357033E3F0E956BE0E27C4374653D602`.
- A future package-bound approval may authorize one isolated wrapper invocation only. Success requires wrapper 1, Python process 1, PowerShell 7/7, raw JSON 2/2, total 9/9, exit 0, stderr 0 and exact 789-byte stdout with SHA-256 `EDBD4614B790256E314F4A8963128A5FB5A190FAC197437FB349D4C33C606135`.
- Current status: `AMENDMENT_5G_B_1_1_PACKAGE_AWAITING_APPROVAL`. The package authorizes no semantics, synthetic, real validator, direct-child, helper, preflight or official execution.

### Stage4B-U1-D Pre-Gold Hard Failure 12

- Amendment 5G-B.1.1 approval governance was committed and pushed at `e18dcb13b64e8a50d764fc9eacbabcdea7c5393f` as the exact two-path direct child of package `c4101cfafbc08d518cd4b56e5d199f9d5937294b`.
- Three-way HEAD synchronization, clean worktree and absence of both future evidence paths passed before source verification.
- The required read-only source gate reconstructed the registered sources and confirmed the Python source count of 46 lines and 2,284 UTF-8 bytes.
- The gate then failed because Windows PowerShell 5.1 does not provide `[System.Convert]::ToHexString()`. Python SHA equality and all later source/output checks were not reached.
- This is a verification-command runtime compatibility failure, not an observed frozen-source hash mismatch.
- The frozen wrapper was not invoked; Python processes, synthetic runs, real-validator calls, evidence paths, preflight, official access, token and capture all remained zero.
- Audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_12.md`.
- Current status: `AMENDMENT_5G_B_1_1_SOURCE_HASH_VERIFICATION_STOPPED_HARD_FAILURE_12`. Source verification and semantics execution require a new independent review and package-bound recovery Amendment.

### Stage4B-U1-D Hard Failure 12 Review And Amendment 5G-B.1.1.1 Package

- Independent review accepts Hard Failure 12 and confirms that approval governance passed, the failure occurred before wrapper execution and no source hash mismatch was observed.
- Review: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_12_REVIEW_1.md`.
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_MANIFEST.json`.
- The recovery verifier is frozen for Windows PowerShell 5.1 Desktop at 59 lines, 3,512 bytes and SHA-256 `1A30DC70AD0C01CDACBC3279F1CFD707EA4DAB457BE9C6C30A5C6D6495FA81BF`.
- It may read only the prior 24,248-byte 5G-B.1.1 Manifest with SHA-256 `B5953058270B4A8C715D38D5CF92CC65DCB7F90C6149EA1DC5B3E02C14B1A68E`; its exact success stdout is 190 bytes with SHA-256 `D05B3B2A147C51FB3A9FFFC3BEB802439E01AEFC34B708FE14C298978F2BFBB3`.
- The original semantics wrapper, embedded Python, fixtures, 789-byte output and real precommit validator remain unchanged and unexecuted.
- Current status: `AMENDMENT_5G_B_1_1_1_PACKAGE_AWAITING_APPROVAL`. The package itself authorizes no source verification, wrapper, Python process, evidence or official execution.

### Stage4B-U1-D Corrected Amendment 5G-B.1.1.1 Package

- Package Review 1 rejects commit `d1876bd9ccc198285808795f7f1809c4d1a48e1c` because its accepted 59-line verifier lacked a frozen bootstrap, child-process transport and raw-output evidence path.
- Review: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_PACKAGE_REVIEW_1.md`.
- The corrected Request and Manifest supersede that unapproved package without changing scripts, tests, results or frozen semantics content.
- The recovery harness is frozen at 77 lines, 6,246 bytes and SHA-256 `B34E7AE012AC0314AD44590603575194C8881CE58C17E6C8ED6568A5FA373048`.
- The bootstrap trust root is frozen at 58 lines, 3,909 bytes and SHA-256 `F8A452CEBEC06326E1D8BA4DEB4FC8915210F3FF9BBF53DA2D22B9675773C81D`.
- Child transport is Windows PowerShell 5.1 with `-NoLogo -NoProfile -NonInteractive -EncodedCommand`, UTF-16LE Base64, redirected stdin/stdout/stderr and no temporary script.
- The bootstrap validates the harness, the harness validates and runs one verifier child and then one unchanged wrapper child, and the wrapper may run one Python process. Every layer requires exit 0 and empty stderr.
- Exact wrapper stdout is carried unchanged through harness and bootstrap; bootstrap writes its captured 789 bytes directly to the versioned machine evidence with `FileMode.CreateNew`.
- Current status: `CORRECTED_AMENDMENT_5G_B_1_1_1_PACKAGE_AWAITING_APPROVAL`. No bootstrap, verifier, wrapper or official execution is authorized by the package itself.

### Stage4B-U1-D Pre-Gold Hard Failure 13

- Corrected Amendment 5G-B.1.1.1 approval governance was committed at `f46afbf565beca5672ef443bccb67c33ebd26876` as the exact two-path direct child of package `e37400707a65d11c9f038d13e7be0ec2a19d27a4`.
- The push to GitHub and following `git fetch origin main` succeeded; local HEAD and fetched `origin/main` both equal the approval-governance commit.
- The separately required GitHub-main API check failed before source reconstruction because the environment does not provide the `gh` executable.
- This is a local verification-tool availability failure, not a network failure and not evidence of remote drift. The approved three-way synchronization gate nevertheless remains incomplete.
- No replacement API client, `git ls-remote` or browser verification was used, and no retry occurred.
- Static source reconstruction, bootstrap, all nested PowerShell/Python processes, semantics evidence, synthetic, real validator, preflight, official input, token and capture remained at zero.
- Audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_13.md`.
- Current status: `CORRECTED_AMENDMENT_5G_B_1_1_1_APPROVAL_GOVERNANCE_SYNC_VERIFICATION_STOPPED_HARD_FAILURE_13`. Recovery requires a new independent review and package-bound Amendment.

### Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1 Package

- Hard Failure 13 Review 1 accepts the failure audit and freezes checkpoint `e159558b621f516598dc4fd2aede151c84472950`.
- The package adds no script, test, result or experiment implementation. It freezes a pre-reconstruction synchronization verifier inside the Request and Manifest.
- The verifier source is 74 LF lines, 4,114 UTF-8 bytes and SHA-256 `4A5A4BBE08661D588673C4B4A1A7ABAB88FEB2999699658CBC91E8081266EB66`; static PowerShell parsing found zero errors, and no execution occurred.
- It uses the environment-confirmed `C:\Program Files\Git\cmd\git.exe` and exactly five child commands: fetch, local rev-parse, fetched-origin rev-parse, direct `ls-remote`, and porcelain status.
- Success requires exact output grammar, five zero exits, empty stderr, local/origin/direct-remote SHA equality, clean worktree and all four evidence paths absent. `gh`, REST, browser, fallback and automatic retry are forbidden.
- The fixed 122-byte success stdout has SHA-256 `BCDF0010147E5952AD0372ADF39EDA0A18D349B02107C340DEF05BAFE18C0F09`.
- The corrected Manifest is rebound at 30,174 bytes and SHA-256 `A5AA1E9B4CB022AFCCF401E9C2193FC06FD45830151154E049DC7B59BB77E6AE`; bootstrap and all downstream semantics fingerprints remain unchanged.
- Review: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_13_REVIEW_1.md`.
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_MANIFEST.json`.
- Current status: `AMENDMENT_5G_B_1_1_1_1_PACKAGE_AWAITING_APPROVAL`. No verifier, bootstrap, semantics or official execution is authorized by the package itself.

### Corrected Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1 Package

- Package Review 1 accepts the seven-path scope and the 74-line pre-execution verifier but rejects package `93cc76ae97043077d2d3dae93e2569833ea3ab59` because its final synchronization gate was unfrozen and its invocation wording contradicted its one-time counts.
- Review: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_PACKAGE_REVIEW_1.md`.
- The corrected package supersedes that commit while preserving the accepted pre-execution verifier byte-for-byte.
- A separate post-evidence verifier is frozen at 107 LF lines, 7,130 UTF-8 bytes and SHA-256 `8877E18F75A94EE6DA326B09C3791E6641B6B9B32D42744BA23E033A20735A67`.
- Its fixed transport complete-arguments SHA-256 is `17327F58C123664224B95FABD85E7553B3E32F4F86659D9A17D13C68AD9FEB02`; fixed 194-byte success stdout SHA-256 is `2ED3F942961C4DA1F7A9D71C3B8A50E6E00275DBBE4038C594B8834B7499AB0F`.
- It starts exactly seven Git children and requires three-way SHA equality, clean worktree, exact approval parent and evidence path set, target regular files, exact machine evidence fingerprint, narrative stability and old-path absence.
- Pre/post counts are separately frozen as `1 PowerShell + 5 Git` and `1 PowerShell + 7 Git`. Both static parsers and all fingerprint checks passed; neither source was invoked.
- Original bootstrap, harness, compatible verifier, wrapper, Python and real-validator fingerprints remain unchanged.
- Current status: `CORRECTED_AMENDMENT_5G_B_1_1_1_1_PACKAGE_AWAITING_APPROVAL`. No execution is authorized by the corrected package itself.

### Stage4B-U1-D Pre-Gold Hard Failure 14

- Corrected package `3d37c8a65888c2093403a71375bfa94dd51bac2e` was approved, and exact-two-path approval governance was committed and pushed at `ba50d75e41f6046c2b0380462c3d7480542e15c4`.
- Static reconstruction passed every frozen pre-execution source, transport, complete-arguments and expected-stdout fingerprint before process start.
- The single authorized pre-execution verifier PowerShell process started and returned exit code 0, but the host then detected non-empty stderr and fail-closed.
- Exact stderr and stdout bytes were captured only in memory and were not persisted before the outer command threw. Their content and the internal Git-child completion count cannot be recovered or reported as passed.
- No retry, runtime switch, `gh`, REST, browser or extra Git fallback was used.
- Static bootstrap reconstruction, bootstrap, harness, compatible verifier, wrapper, Python, evidence creation/commit and post-evidence verifier all remained zero. Four evidence paths remain absent and the worktree remains clean.
- Audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_14.md`.
- Current status: `CORRECTED_AMENDMENT_5G_B_1_1_1_1_PRE_EXECUTION_SYNC_STOPPED_HARD_FAILURE_14`. A new independent review must define any diagnostic or recovery scope.

### Stage4B-U1-D Pre-Gold Hard Failure 14 Review And Amendment 5G-B.1.1.1.1.1 Package

- Hard Failure 14 Review 1 accepts checkpoint `e12b0961492897d1940cf0cf2ce45fa45abb99b8`, the valid approval-governance commit and the fail-closed stop.
- The accepted evidence boundary is one original pre-verifier process with exit code 0 and non-empty stderr. Raw stdout/stderr are unrecoverable, the internal Git-child count is unconfirmed, accepted 122-byte successes remain zero and root cause is not established.
- Review: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_14_REVIEW_1.md`.
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_1_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_1_MANIFEST.json`.
- The package freezes a 161-line, 9,684-byte Windows PowerShell 5.1 raw-stream launcher with source SHA-256 `4FA9DABF8701F67554F6D0D100EFD72DF78477F80F600057F5C26A9886471DD6` and complete-arguments SHA-256 `86E326DBB39ED099A5AA4BD8CA46002656D2766768C731A88F15C784F88946C1`.
- The launcher statically parses with zero errors. It and the original pre verifier were not invoked during package assembly.
- A future approved launcher would concurrently drain the unchanged original verifier's raw stdout/stderr streams, persist both with `FileMode.CreateNew` before comparison, then persist value-free metadata. Internal Git-child count remains unconfirmed pending independent review.
- The four diagnostic evidence paths are new and the four semantics paths must remain absent. Bootstrap, semantics, post verifier, synthetic and all official operations remain unauthorized.
- Current status: `AMENDMENT_5G_B_1_1_1_1_1_RAW_STREAM_DIAGNOSTIC_PACKAGE_AWAITING_APPROVAL`.

### Stage4B-U1-D Pre-Gold Hard Failure 15

- Package `d6d8a76abcb903b74307ed68f5ceabc42d8be8e3` received package-bound approval, and exact-two-path approval governance was committed and pushed at `ee84988fa6ccf5e7f3524bc2c2a5f94065abf918`.
- The single static launcher reconstruction passed every frozen Manifest, source, parser, UTF-16LE/Base64, complete-arguments and fixed-stdout fingerprint.
- Exactly one launcher process started exactly one unchanged original pre verifier. The launcher returned exit code 0 and exact frozen 122-byte stdout, but its stderr contained 382 bytes with SHA-256 `4F2B6B3ED9201CA459DB2DD042E0A137C4E58BFE8E15A068E45AD8535FA5B1EF`; the empty-stderr hard gate failed.
- The frozen launcher had already created raw stdout, raw stderr and value-free metadata. Their byte counts are 122, 382 and 944; their SHA-256 values are `BCDF0010...C0F09`, `4F2B6B3E...5B1EF` and `F4022C8B...B101B`. All three are preserved byte-for-byte.
- The approved narrative success audit was not created. All four semantics paths remain absent; no success evidence commit, retry, bootstrap, semantics, post verifier, synthetic, real validator or official action occurred.
- Metadata keeps the internal Git-child count null/unconfirmed and accepted three-way synchronization successes at zero. No raw payload interpretation or synchronization acceptance is made.
- Audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_15.md`.
- Current status: `AMENDMENT_5G_B_1_1_1_1_1_RAW_STREAM_DIAGNOSTIC_STOPPED_HARD_FAILURE_15`. Independent review and a new package-bound Amendment are required for any further action.

### Hard Failure 15 Review And Amendment 5G-B.1.1.1.1.2 Package

- Hard Failure 15 Review 1 accepts checkpoint `95f68e7b2afdf6ed46c4eebe604d13744b26760a` and the three preserved raw machine files.
- The 382-byte stderr is established as Windows PowerShell startup progress CLIXML. Its SHA-256 is `4F2B6B3E...5B1EF`; its 512-character Base64 SHA-256 is `1A3D87C5...8700B`.
- Exact 122-byte pre-verifier stdout proves five strict-zero-stderr Git children, three-way SHA equality, a clean worktree and four absent semantics paths for historical commit `ee84988...`. The old outer zero-stderr contract remains failed and consumed.
- The new classifier accepts only exact zero bytes or byte-for-byte equality with the frozen payload at PowerShell boundaries. Git, Python and every non-PowerShell child retain strict zero stderr.
- Unchanged sources remain 74-line pre verifier, 107-line post verifier, 59-line compatible verifier, 122-line wrapper, 46-line Python and 195-line real validator.
- New/revised sources are a 96-line pre host, 98-line bootstrap, 91-line harness and 86-line post host. All four static parsers report zero errors; all source, UTF-16LE/Base64 and complete-arguments fingerprints are frozen in the Manifest.
- Package assembly invoked no frozen source and created no semantics evidence. A future approval must bind the new package commit and rerun synchronization against its new approval-governance child; historical `ee84988...` synchronization cannot be reused.
- Review: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_15_REVIEW_1.md`.
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_2_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_2_MANIFEST.json`.
- Current status: `AMENDMENT_5G_B_1_1_1_1_2_TRANSPORT_RECOVERY_PACKAGE_AWAITING_APPROVAL`.

### Amendment 5G-B.1.1.1.1.2 Package Review 1 And Corrected Package

- Package Review 1 accepts Hard Failure 15, the three raw machine files, the exact 382-byte classifier, 6/6 classifier fixtures, package commit scope and four inner envelope designs as static content.
- It rejects package `7f92c000bb3c22337c83dc28e32779f4eb9cfdf8` because the top-level runner was not frozen, inner stderr classes were not exposed or persisted, and post classes could exist only after the narrative had already been committed.
- The corrected package freezes six sources with zero static parser errors: 96-line pre host, 91-line revised harness, 109-line revised bootstrap, 86-line post host, 194-line pre/semantics outer runner and 166-line post-sync outer runner. All source, UTF-16LE/Base64, complete arguments, raw BaseStream, classifier, exact stdout and count contracts are in the corrected Manifest.
- Exact canonical stdout variants carry only `EMPTY` or `EXACT_FROZEN_382_BYTE_STARTUP_CLIXML`. The harness carries the unchanged 789-byte semantics payload as exact Base64; the bootstrap writes the original 789 bytes unchanged. Git, Python and non-PowerShell stderr remain strict zero.
- The semantics commit remains exactly the machine evidence plus a pre/semantics-only narrative. Post success then creates a separate machine attestation and narrative audit, followed by a separate exact-two-path audit commit whose parent is the semantics evidence commit.
- Corrected package assembly invoked no frozen source and created no evidence. The first temporary generator attempt stopped before Manifest write on a Windows PowerShell 5.1 UTF-8 no-BOM path-decoding error; the strict-UTF8 corrective invocation and zero-execution boundary are recorded.
- Package Review: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_2_PACKAGE_REVIEW_1.md`.
- Corrected Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_2_APPROVAL_REQUEST.md`.
- Corrected Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_2_MANIFEST.json`.
- Current status: `CORRECTED_AMENDMENT_5G_B_1_1_1_1_2_PACKAGE_AWAITING_APPROVAL`; no execution is authorized before a new package-bound approval.

### Amendment 5G-B.1.1.1.1.2 Package Review 2 And Second Corrected Package

- Package Review 2 accepts first corrected commit `44e56ab955dfe5fe89cc8ec4343870b59d008c9a`, its seven-path scope, Hard Failure 15/raw evidence binding, exact classifier, six source designs, canonical class channel and pre/post audit separation.
- It rejects that package as written because no frozen verifier runs after the final exact-two-path post-sync audit commit is pushed; final three-way GitHub main, parent/path semantics and artifact stability were therefore unverified.
- The second corrected Manifest preserves those six sources and adds a 164-line / 12,934-byte final verifier (`C0D96FD1...D2B2B`) plus an 81-line / 6,024-byte final host (`C843B63E...91131`). All eight static parsers report zero errors and no frozen source was executed during assembly.
- The final verifier freezes eleven Git children and verifies local/fetched/direct GitHub main equality, the package -> approval -> semantics -> final ancestry, three exact two-path commit scopes, canonical post machine/narrative agreement and before/after stability of historical, semantics and post artifacts.
- The final host freezes raw BaseStream capture, exact child stdout, exact PowerShell stderr classification and two canonical host stdout variants. Exact success is terminal: no file, status document or commit may be created afterward.
- Review: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_2_PACKAGE_REVIEW_2.md`.
- Second corrected Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_2_APPROVAL_REQUEST.md`.
- Second corrected Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_2_MANIFEST.json` (227,242 bytes; SHA-256 `69CA3DAD8664F12213933A603D0AE0955C8AC17E483E5DC433859839AD49086E`).
- Current status: `SECOND_CORRECTED_AMENDMENT_5G_B_1_1_1_1_2_PACKAGE_AWAITING_APPROVAL`; no execution is authorized before a new package-bound approval.

### Stage4B-U1-D Pre-Gold Hard Failure 16

- Second corrected package `945f655b95cfee9e55ad2d20e7bd5018f9aee1e2` received package-bound approval. Exact-two-path approval governance was committed and pushed at `72783071c17f6e3cab347823a8da080171c1a883` before any source reconstruction.
- The post-push gate confirmed local/fetched/direct GitHub main equality, clean worktree, unchanged historical evidence and six absent semantics/post-sync paths.
- The only pre/semantics outer-runner reconstruction passed its 194-line / 14,491-byte source SHA, zero parser errors, 38,599-character complete-arguments SHA and 170-byte expected-stdout identity.
- The first `Process.Start()` attempt failed before process creation with `Win32Exception: The filename or extension is too long`. No PID, exit code, stdout or stderr exists; runner and all nested process counts are zero.
- No retry, shorter command, temporary script, runtime switch, source modification or cleanup occurred. Historical evidence remains unchanged and all six future paths remain absent.
- Audit: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_16.md`.
- Current status: `AMENDMENT_5G_B_1_1_1_1_2_PRE_RUNNER_START_STOPPED_HARD_FAILURE_16`. Independent review and a new package-bound Amendment are required for any transport recovery.

### Hard Failure 16 Review 1 And Amendment 5G-B.1.1.1.1.3 Package

- Independent Review 1 accepts Hard Failure 16 checkpoint `f28fc526faf74f80fdefb96ca189769dbcf1e5e4`, the valid approval governance, the one static reconstruction, the consumed start attempt, zero created processes/evidence and the fail-closed stop.
- The root cause is frozen as `ENCODED_COMMAND_COMMAND_LINE_OVERFLOW`: 38,599-character arguments exceed the Microsoft-documented 32,767-character `CreateProcessW` command-line limit including the terminating null.
- The new package freezes three 44-line target-specific loaders. Their modeled full command lines are 7,384, 7,364 and 7,376 characters, with margins greater than 25,000 characters.
- Large target sources are transported as exact ASCII Base64 through raw stdin. The loader validates raw bytes, decoded UTF-16LE, source identities and parser state before one in-process ScriptBlock invocation; it adds no stdout.
- Pre/post target sources remain unchanged. The final verifier is rebound to the new governance files, and the 92-line revised final host launches it through the final stdin loader while retaining the terminal Git/schema/artifact gates.
- Three static fixture groups pass 30/30. Package assembly executed zero loader/target/process and created zero evidence. Four read-only helper failures (malformed `throw`, denied `rg.exe` start, invalid PowerShell exclusion regex and an incorrect revision-label assertion before source reconstruction) are recorded with zero writes, zero created child processes and zero frozen-source invocations.
- Review: `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_16_REVIEW_1.md`.
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_MANIFEST.json` (203,974 bytes; SHA-256 `DF088593BA620CE235419B2B759247914771FCFCE63B49A099A788AD29D5FC1C`).
- Current status: `AMENDMENT_5G_B_1_1_1_1_3_BOUNDED_STDIN_TRANSPORT_PACKAGE_AWAITING_APPROVAL`; no execution is authorized.

### Amendment 5G-B.1.1.1.1.3 Package Review 1 And Corrected Package

- Package Review 1 binds and rejects package `97a8b169835c06330a6781ab63c59a482889c6bb` / 203,974-byte Manifest `DF088593...5FC1C`, while accepting Hard Failure 16 Review 1, three loader/payload designs, bounded command lines, revised final host and 30/30 loader fixtures.
- Blocking causes are two unfrozen pre/post parent hosts, success narratives that still attest rejected long EncodedCommand fingerprints, and a terminal verifier that does not reject the stale evidence.
- The corrected package selects the existing-narrative closure: revised pre/post targets write current package bindings, parent, loader, modeled command line, payload and decoded target identities. No evidence path or exact-path commit scope is added.
- Nine source designs are frozen. Newly added pre/post parent hosts are 96 / 99 lines and their modeled full command lines are 21,176 / 22,928 characters. All six loader/parent envelopes remain below 32,767.
- The 228-line final verifier recomputes six envelopes and three payloads, requires exact current pre/post transport lines and rejects the two stale long-transport hashes before its eleven Git children.
- Static validation passes 9/9 sources, 6/6 envelopes, 3/3 payloads, 62/62 fixtures and 6/6 absent future paths. Assembly execution/evidence/official counts are zero; three zero-write read-only helper failures are preserved.
- Review: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_PACKAGE_REVIEW_1.md`.
- Corrected Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_APPROVAL_REQUEST.md`.
- Corrected Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_MANIFEST.json` (321,442 bytes; SHA-256 `C1A11B789FD18D703AA6831BA5B513FC9ACB9767EC8A75016802030E0A0C1123`).
- Current status: `CORRECTED_AMENDMENT_5G_B_1_1_1_1_3_PACKAGE_AWAITING_APPROVAL`; no execution is authorized.

### Amendment 5G-B.1.1.1.1.3 Package Review 2 And Second Correction

- Package Review 2 accepts corrected package `b9081b3c28c0c03e8bece797f5e05a74401f397b` technical content: 9 sources, 6 bounded envelopes, 3 payloads, both parent hosts, current evidence schema, extended final verifier, stale-transport rejection and 62/62 fixtures.
- The only blocking cause is lineage: `b9081b3c...` directly descends from `97a8b169...`, while `f28fc526...` is the Hard Failure 16 ancestor. The corrected Request had mislabeled the ancestor as direct parent.
- The second correction separately records direct parent `b9081b3c...`, superseded original package `97a8b169...` and checkpoint ancestor `f28fc526...`.
- No frozen source, transport, payload, evidence schema, verifier, fixture, future path, count or one-pass order changes.
- Review: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_PACKAGE_REVIEW_2.md`.
- Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_APPROVAL_REQUEST.md`.
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_MANIFEST.json` (323,607 bytes; SHA-256 `804B4F8607532D6CE17EDE043D5A9511C7E855F4EB444C25F461381B6EDDA73D`).
- Current status: `SECOND_CORRECTED_AMENDMENT_5G_B_1_1_1_1_3_PACKAGE_AWAITING_APPROVAL`; no execution is authorized.

### Hard Failure 17: Pre Parent Modeled-command Static Gate

- Independent approval bound second-corrected package `ef87f0379f4f31c54881c4a0e23a3f7ad8c8c35b` and its 323,607-byte Manifest SHA-256 `804B4F8607532D6CE17EDE043D5A9511C7E855F4EB444C25F461381B6EDDA73D`.
- Exact two-path approval governance `1afdd8075169e70d385e617ade480880cf3eb718` was committed and pushed as the package's direct child. Remote triplet, clean-worktree, six-absent-future-path and three-stable-historical-file gates passed.
- The approved PRE static reconstruction passed source, parser and 21,115-character arguments identities, then stopped before `Process.Start()` at `PRE_PARENT_MODELED_COMMAND_TEXT_MISMATCH`.
- Root cause is frozen as `ORCHESTRATOR_SCHEMA_DESCRIPTOR_MISINTERPRETATION`: the helper treated `QUOTED_FILE_NAME_SPACE_ARGUMENTS_TERMINAL_NULL` as literal command text and used the runtime label instead of `process_start_info_contract.file_name`.
- Read-only post-stop recomputation with the registered executable path produced the exact frozen 21,176 characters / `E8247D1AF7D1CC5F6FEBF32F9102D49A37076FA19602906D7C9121E45EC808F0`; no package transport defect is established by this run.
- `Process.Start()` attempts and actual PRE parent/loader/target processes are 0. Semantics/POST/FINAL evidence and processes are 0; all six future paths remain absent and historical machine evidence remains unchanged.
- No retry, fallback, cleanup or downstream action occurred. Current state: `AMENDMENT_5G_B_1_1_1_1_3_PRE_PARENT_MODELED_COMMAND_GATE_STOPPED_HARD_FAILURE_17`; independent review and new approval are required.

### Hard Failure 17 Review 1 And Amendment 5G-B.1.1.1.1.4

- Review 1 accepts Hard Failure 17 checkpoint `6c741c251dce55236b06dc5c06fd834b7649f8b2`, valid approval governance `1afdd807...`, zero Process.Start/runtime/evidence boundary, preserved historical evidence, and six absent future paths.
- Root cause is `ORCHESTRATOR_SCHEMA_DESCRIPTOR_MISINTERPRETATION`; current evidence establishes neither package source nor bounded parent transport defect. The old approval is consumed and cannot be reused.
- The new package preserves all 9 source identities, 6 bounded envelopes, 3 raw-stdin payloads, parent/loader/evidence/final-verifier logic, and inherited 62/62 fixtures.
- Three tracked ASCII-only top-level trust roots are added: PRE 135 lines / 8,118 bytes / `4EDC7E67...AC0C7E`; POST 137 / 8,405 / `D32FC6E8...F904569`; FINAL 137 / 8,421 / `203DCA76...8734EC`. Parser errors are 0/0/0 and assembly executions are 0.
- Each adapter binds the descriptor as schema, obtains the executable only from `process_start_info_contract.file_name`, uses the unique quoted-file/single-space/arguments/NUL formula, validates count/SHA before `ProcessStartInfo`, and applies exact raw parent stdout/stderr gates.
- New schema-semantics fixtures pass 30/30 across PRE/POST/FINAL. Package assembly ran no orchestrator, parent, loader, target, Git child, Python, evidence, synthetic, or official operation.
- Before future approval-governance push, frozen source-line join/parser/reconstruction is prohibited; only commit/Manifest/worktree/path/remote identity checks are allowed.
- Manifest is 24,293 bytes / `921B7BB63B0CF8E7B51CC6ED51A74C98A915E6C8E5FB2211E8235D7A378DE928`. Current state: `AMENDMENT_5G_B_1_1_1_1_4_FROZEN_TOP_LEVEL_ORCHESTRATION_ADAPTER_PACKAGE_AWAITING_APPROVAL`; execution remains unauthorized.

### Amendment 5G-B.1.1.1.1.4 Package Review 1 And Correction

- Package Review 1 binds package `7d2dcd5fe525c86ab2b91e7ed2dfb17b1e6228ac`, direct parent `6c741c251dce55236b06dc5c06fd834b7649f8b2`, and Manifest 24,293 bytes / `921B7BB6...DE928`.
- It accepts the exact ten-path scope, all three tracked ASCII adapter designs, schema/executable binding, unique modeled-command formula, all three `-File` invocation envelopes, 30/30 schema fixtures, and the zero-execution assembly boundary.
- It rejects the package because actual parent stderr class was not emitted, adapter execution was not durable evidence, the inherited final verifier did not validate adapters, the old evidence schema could not prove mediation, and FINAL attestation order was not closed.
- Corrected PRE/POST/FINAL adapters are 136/138/125 lines, 8,222/8,509/8,247 bytes, with SHA-256 `6D9466FD...B8A02`, `89828EB8...F9CC5`, and `364473BA...1AC8E`; each freezes exact `EMPTY` and `EXACT_FROZEN_382_BYTE_STARTUP_CLIXML` stdout variants.
- A new tracked 216-line / 14,152-byte capture-attestation host (`589134A5...D0CA`) validates and invokes exactly one stage adapter, captures raw streams, and uses `CreateNew` pending records outside the repository. FINAL validates and promotes all three records to versioned repository paths.
- The three adapter attestations must be committed and pushed in an exact three-path commit after the exact two-path post audit.
- Compatibility inspection found that the inherited final verifier hard-coded the 1.1.3 Approval Decision path. The FINAL adapter now starts a tracked dual-mode verifier in `PRE_ATTESTATION` mode, which validates the inherited six envelopes, three payloads, seven evidence artifacts and corrected four-layer chain with 12 Git children.
- The same 362-line / 30,827-byte dual-mode verifier (`75A62A89...A222D`) later runs in `TERMINAL` mode and validates three adapters, three invocation envelopes, three execution attestations, six actual stderr classes, mandatory mediation, the five-layer Git chain, exact changed paths, artifact stability, clean worktree and local/origin/direct main with 14 Git children.
- The original 9 sources, 6 bounded envelopes, 3 payloads, parent/loader/target sources, semantics/post evidence, inherited final-verifier source, and 62 fixtures remain unchanged. Schema fixtures remain 30/30; corrected-package static fixtures are 32/32.
- Package assembly ran zero capture host, adapter, verifier mode, parent, loader, target, Git child from frozen source, Python, evidence, synthetic, or official operations. Six corrected-package read-only helper failures produced zero writes and are disclosed. Current source bytes are LF; exact source gates fail closed if Git rewrites them under the repository's `core.autocrlf=true` configuration.
- Corrected Manifest is 41,597 bytes / `E0C0E8B329720C8B99130598E820E244E80707BAA628C1063688E209D067121A`.
- Current state: `CORRECTED_AMENDMENT_5G_B_1_1_1_1_4_PACKAGE_AWAITING_APPROVAL`; approval governance and all execution remain unauthorized.

### Amendment 5G-B.1.1.1.1.4 Package Review 2 And Second Correction

- Package Review 2 binds and rejects corrected package `61cfce1d3c11891ad0d8c2953fd855c2c3d0f9a8` / 41,597-byte Manifest `E0C0E8B...121A`, while accepting its exact twelve-path scope, six class-bearing variants, capture-host and dual-mode-verifier static designs, Approval Decision compatibility fix, four/five-layer Git designs, 30/30 inherited fixtures, reported 32/32 corrected fixtures, and zero-execution boundary.
- Blocking causes are unanchored PRE/POST observations in mutable OS-temp pending files, absent canonical-byte enforcement, terminal acceptance of semantic-equivalent/extended JSON, and missing persisted/terminally-validated capture-host stage invocation identity.
- The second correction selects Scheme A: PRE attestation joins the exact three-path semantics commit; POST joins the exact three-path post-sync commit; FINAL alone forms the exact one-path final-attestation commit. Pending and promotion are removed.
- A shared 50-line / 4,361-byte canonical builder (`4409E8AF...F55D`) fixes schema 2.0 and the unique UTF-8 byte representation. The 211-line / 13,697-byte capture host (`74E5155D...7A0C`) requires its actual `[Environment]::CommandLine + NUL` to equal the selected stage modeled command before child execution, then persists builder, capture source/stage invocation, adapter source/invocation, observed outputs/classes, bindings, and process counts.
- The 388-line / 33,878-byte dual-mode verifier (`8D7BDF32...13D5`) validates all three capture-host envelopes and rebuilds every attestation for byte-for-byte comparison. PRE_ATTESTATION validates committed PRE/POST and FINAL absence; TERMINAL validates all three plus the five-layer chain.
- Six second-corrected sources pass exact identity/LF/parser-zero checks. Static fixtures are 30/30 inherited, 32/32 previously corrected, and 18/18 second-corrected. Assembly ran no frozen source or evidence/experimental operation; seven read-only helper attempts (`rg.exe` denied, two empty-pipe parser errors, two compact `foreach` whitespace errors, one `H`/`Get-History` alias collision, and one invalid inline-`try` helper) caused zero writes/processes/evidence before corrected helpers passed.
- Review: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4_PACKAGE_REVIEW_2.md`.
- Second-corrected Request: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4_APPROVAL_REQUEST.md`.
- Second-corrected Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4_MANIFEST.json` (48,629 bytes; SHA-256 `E764A188AB11F49152B272F041CAC8FAC9477929C30475576D6349791E67373B`).
- Current status: `SECOND_CORRECTED_AMENDMENT_5G_B_1_1_1_1_4_STAGE_ANCHORED_CANONICAL_BYTE_ADAPTER_PACKAGE_AWAITING_APPROVAL`; approval governance and all execution remain unauthorized.

### Hard Failure 18: PRE Capture Result Observation Was Not Recoverable

- Independent approval bound package `683d17bd70cc32dca2e495836bb6b16160a79f79` and Manifest 48,629 bytes / `E764A188AB11F49152B272F041CAC8FAC9477929C30475576D6349791E67373B`.
- Exact two-path approval governance `677df53f014ab194e08042e4f605b5f879b9fa32` was committed and pushed as the package's direct child. The local/tracking/direct remote triplet, clean worktree, and seven absent future paths passed.
- Post-governance static validation passed 106/106 checks across six tracked source byte/SHA/LF/ASCII/parser identities, three adapter invocations, three capture-host invocations, two verifier-mode invocations, and all registered success stdout identities.
- The one authorized PRE capture-host process started. `WaitForExit()` returned and both raw `BaseStream.CopyToAsync()` tasks completed.
- Before the outer observer could persist or print the child exit code and raw stdout/stderr identities, its helper command `H $errBytes` resolved to the built-in `Get-History` alias and raised `Cannot locate the history for Id 65`.
- The child exit code, exact stdout bytes, and exact stderr bytes/class were therefore not preserved and cannot be reconstructed. No package or capture-host runtime result is claimed.
- All three PRE evidence paths and all four POST/FINAL paths remained absent; the worktree stayed clean at `677df53f...`. PRE adapter/parent/loader/target/semantics counts are unconfirmed rather than inferred from absence.
- No retry, fallback, evidence cleanup, semantics commit, POST, FINAL, TERMINAL, synthetic, real-validator, preflight, official, Gold, reservation, or Stage3B action occurred.
- Current state: `AMENDMENT_5G_B_1_1_1_1_4_PRE_CAPTURE_OBSERVATION_UNRECOVERABLE_HARD_FAILURE_18`. The one-pass authorization is consumed; independent review and a new amendment/package-bound approval are required before any further frozen-source execution.

### Hard Failure 18 Review 1 And Amendment 5G-B.1.1.1.1.5

- Review 1 accepts checkpoint `a3812d000b8af07196ea3a824988703a3ff132d3`, valid approval governance, 106/106 static checks, one PRE capture-host start/await, both completed BaseStream drains, seven absent future paths and fail-closed stop.
- Root cause is `OUTER_OBSERVER_H_ALIAS_RESOLVED_TO_GET_HISTORY`. Neither a 1.1.4 package-source/capture-host defect nor capture-host success is established; PRE downstream counts remain `UNCONFIRMED` and the old approval is non-reusable.
- Amendment 1.1.1.1.5 freezes a 203-line / 13,186-byte tracked observer (`67DCCD6B...F325`) with PRE/POST/FINAL/TERMINAL modes, explicit helper-name resolution gate, exact source/invocation/ProcessStartInfo/environment contracts, and one-child process counts.
- After WaitForExit/WaitAll and raw-array materialization, the observer writes a no-serializer `HGRAGO15` binary through `CreateNew` before hash/classification. The 48-byte header records version, mode, completion flags, exit code and both stream lengths; raw stdout/stderr follow. Partial files are preserved.
- Every successful mode uses a repository raw artifact. Stage path scopes are `4/4/2/1`; the terminal verifier checks the five-layer chain before the terminal observer creates its record, then that record forms a sixth one-path commit for later independent review.
- PRE/POST adapters and the canonical builder are unchanged. Versioned capture host, FINAL adapter and dual-mode verifier only bind the 1.1.5 Manifest/new path sets and validate outer records.
- Static package validation passes 34/34 source/invocation/stdout checks and 43/43 observer fixtures. Two zero-write/zero-process helper attempts stopped on compact PowerShell syntax/name-resolution issues before corrected split helpers passed.
- Manifest: 37,645 bytes / `303A347368E4BFBF4CEBBB71DFE07E244328A60BC4DBE996A0444A5C56E45BF9`.
- Current state: `AMENDMENT_5G_B_1_1_1_1_5_FROZEN_OUTER_OBSERVER_DURABLE_RAW_CAPTURE_PACKAGE_AWAITING_APPROVAL`; no execution is authorized.

### Hard Failure 19: PRE Capture Host Reported Adapter Nonzero Exit

- Independent approval was committed and pushed in exact two-path governance commit `950b56e83de8a87b7afe75eb3f021819e19516c8`, directly after package `f634a1ca766cc2885017f63f94ef9b87cab9a765`.
- Before PRE, local/origin/direct GitHub main were equal, the worktree was clean, all eleven future paths were absent, and the approved post-governance gates passed `34/34 + 43/43` with zero process starts/writes.
- The single PRE observer execution returned exit 1 with zero stdout and 492 stderr bytes after its child returned nonzero. It was not retried.
- The observer first completed the registered PRE `HGRAGO15` raw record: 520 bytes / `4ABEB26000DDC77E8293DB1616682E6748E2290A9608959A2A040B1CD2780A70`.
- The fixed header is complete and records child exit 1, zero stdout and 472 stderr bytes. Persisted stderr SHA-256 is `9E8393DD9738C73FCA928BD28E0031A6B8EABF4FABE9147FA0F101ED969D56EB` and reports `Adapter nonzero exit: 1`.
- The deeper adapter/parent/loader/target cause and counts remain `UNCONFIRMED`. No package-source or transport defect is inferred from the generic nonzero boundary.
- Ten other future paths remained absent. No PRE attestation, semantics success commit, POST, FINAL, PRE_ATTESTATION, TERMINAL or downstream experimental action occurred.
- Two read-only diagnostic helpers failed without writes/external processes; final explicit decoding passed and the raw SHA remained unchanged.
- Current state: `AMENDMENT_5G_B_1_1_1_1_5_PRE_CAPTURE_HOST_CHILD_NONZERO_STOPPED_HARD_FAILURE_19`. The approval is consumed; the raw is immutable failure evidence and independent review plus a new Amendment are required.

### Hard Failure 19 Review 1 And Amendment 5G-B.1.1.1.1.6

- Review 1 accepts package `f634a1ca...`, approval `950b56e8...`, checkpoint `96e9677d...`, the post-governance 34/34 + 43/43 gates, exactly one PRE observer, and the structurally complete 520-byte `HGRAGO15` record.
- The exact boundary is `PRE_CAPTURE_HOST_REPORTED_ADAPTER_NONZERO_EXIT_1`. The adapter started once, was awaited, and exited 1. Its raw streams and the parent/loader/target/semantics cause remain `UNCONFIRMED`; package-source and transport defects are not established.
- Amendment 1.1.1.1.6 adds four versioned raw records at every actual nested Process.Start boundary: `HGRAGO16`, `HGRAGA16`, `HGRAGP16`, and `HGRAGL16`. Each record is completed through `CreateNew` and `Flush(true)` before any exit/hash/classification gate. The target is a loader-process ScriptBlock and gets no fictitious process record.
- The new parent, adapter, capture host, observer, and raw verifier are 182/150/157/195/114 lines and 12,118/9,752/10,023/13,263/6,882 bytes, all parser-zero. The inherited 323,607-byte transport Manifest remains unchanged.
- Read-only package assembly passes 56/56 registry, 36/36 durable-order, and 24/24 binary/path fixtures, 116/116 total. No new source was dot-sourced or executed; evidence and experimental writes are zero. Four failed read-only helpers had zero writes and zero frozen-source/experimental starts.
- The package scope is exactly twelve paths with no deletions. Manifest is 13,802 bytes / `7DA3418D8BF7F4CF49D82088294D78CFB6FB6C8E7F66229F18624FE60A929937`.
- Current state: `AMENDMENT_5G_B_1_1_1_1_6_NESTED_DURABLE_PRE_DIAGNOSTIC_PACKAGE_AWAITING_INDEPENDENT_APPROVAL`. The next approval may authorize one PRE-only chain and one failure-or-success evidence commit, then must stop; POST, FINAL, and TERMINAL are not requested.

### Amendment 5G-B.1.1.1.1.6 Package Review 1 And Correction

- Package Review 1 accepts package `1e0973e3...` lineage/scope, HF19 raw binding, PRE-only direction, four raw layers, observer/capture/adapter ordering, reported 116/116 fixtures, and zero execution/evidence boundary, but does not approve governance or PRE.
- It rejects the package because loader stdin access/write/flush/close can fail after start but before `HGRAGL16`, failure commits have no finite exact-path contract, and the requested completion state is still a pre-approval state.
- The corrected parent captures fixed `BASE_STREAM_ACCESS/WRITE/FLUSH/CLOSE` codes, attempts close, awaits the loader and both drains, completes `HGRAGL16` with `Flush(true)`, and only then throws normalized stdin-delivery failure. It is 197 lines / 12,769 bytes / `B117878F...B45F2` and parser-zero.
- The correction adopts Scheme A: exact six-path success commit as the approval commit's direct child; zero failure commits and zero failure pushes, with raw prefix/partial semantics left uncommitted for a separately governed Hard Failure audit package.
- Success, failure, and unified post-attempt review states are frozen. Ten corrected blocker fixtures cover stdin ordering, Scheme A Git branches, and completion states; they join the accepted original 116 checks for 126/126 total. No new source or evidence flow runs during assembly.
- The corrected package is an exact eight-path, zero-deletion direct child of rejected package `1e0973e3...`. Corrected Manifest is 17,536 bytes / `6C5E027B4B4F337B3CB61BDD381F00715D284B3269B5F39F0BE3A2E75259BAC5`.
- Current state: `CORRECTED_AMENDMENT_5G_B_1_1_1_1_6_NESTED_DURABLE_PRE_DIAGNOSTIC_PACKAGE_AWAITING_INDEPENDENT_APPROVAL`; approval governance, PRE, POST, FINAL, TERMINAL, synthetic, official, Gold, reservation, and Stage3B are not approved.

### Hard Failure 20: PRE Observer Actual Command-Line Gate

- Corrected package `0efbea018f4ad0e8650e254d313fb9cc85d2a28c` was approved through exact two-path direct-child governance commit `1eb73132d47d5b21fceca9c88a42607ee3dff98d`; the commit was pushed before frozen-source execution.
- Post-governance local/tracking/direct main, clean worktree, and six-path absence gates passed. Static validation passed 56/56 registry, 36/36 durable-order, 24/24 binary/path/HF19, and 10/10 Review 1 blocker checks, 126/126 total, with zero frozen process starts or evidence writes.
- The single approved PRE observer process reached its own actual-command-line equality gate and exited 1 with `PRE nested observer actual process command line mismatch`.
- The gate precedes capture-host invocation reconstruction and `Process.Start()`. Frozen counts are observer 1, capture host 0, adapter 0, parent 0, loader 0, and target ScriptBlock 0.
- All four new 1.1.6 raw paths and both semantics paths remained absent. The old 520-byte HF19 raw / `4ABEB260...80A70` remained unchanged.
- Actual and modeled command-line bytes were not persisted before comparison. Exact characters, count, SHA, first differing position, and difference category are `UNCONFIRMED`; no executable-quoting, normalization, package-source, or nested-transport root cause is claimed.
- Failure-branch compliance is zero result commits, zero result pushes, zero retries, zero standalone verifier, and zero post-failure diagnostic execution. The approval is consumed and non-reusable.
- Current state: `AMENDMENT_5G_B_1_1_1_1_6_PRE_OBSERVER_ACTUAL_COMMAND_LINE_GATE_STOPPED_HARD_FAILURE_20`. A future command-line-only diagnostic requires a separately governed Amendment/package-bound approval and must not start the capture host.

### Hard Failure 20 Review 1 And Amendment 5G-B.1.1.1.1.7

- Independent Review 1 accepts checkpoint `d0dbc5533ddc464c7f7f1433d660ee7ddc355e07`, its five-path/zero-deletion scope, approval governance, 126/126 static gate, observer 1/capture-host 0 boundary, six-path absence, immutable HF19 raw, and zero-retry/zero-result-commit compliance.
- The only established failure remains `PRE_NESTED_OBSERVER_ACTUAL_PROCESS_COMMAND_LINE_MISMATCH`. Exact bytes, lengths, first difference, common prefix/suffix, and difference category remain unconfirmed; no package-source or nested-transport defect is inferred.
- Amendment 1.1.7 freezes one 98-line / 5,603-byte / `545A5A6E...FC7307` ASCII/LF observer and one new `HGRAGC17` observation path. Package-stage PowerShell parser and observer execution counts are both zero under the review's pre-approval restriction.
- `HGRAGC17` uses an 88-byte little-endian header and saves actual `[Environment]::CommandLine`, modeled command, executable, and arguments as strict UTF-16LE/no-BOM payloads. It records code-unit counts and byte lengths; the observer performs no diff interpretation.
- Durable order is modeled reconstruction -> actual read -> four raw-array materializations -> CreateNew -> header/payload write -> Flush(true) -> close -> equality gate. Equality compares `actual + U+0000` with modeled and maps only to exit 0/1. No capture host or child process can start.
- The package is an exact eight-path, zero-deletion direct child of HF20. Manifest is 13,336 bytes / `968C3D59...AFE8A3C`. It contains no result file and authorizes no parser or execution. A future approved complete observation may enter one exact one-path result commit regardless of equality exit 0/1, followed by immediate independent review.
- One strict-JSON read-only helper failed at Python `-c` syntax before opening the Manifest because of native double-quote transport; the corrected single-quoted helper returned `STRICT_JSON_OK`. Both attempts had zero observer parsing/execution, frozen-process starts, project writes, and evidence creation.
- A second read-only helper failed before file scanning because `rg.exe` could not start (`Access is denied`); PowerShell `Select-String` completed the same reference scan on the exact eight package paths. The failed launch had zero project reads/writes and zero frozen-source activity.
- A third read-only final-validation helper incorrectly expected 12 binary-header fields instead of the registered 13. It read the exact eight package paths but performed zero writes, observer parser/execution, frozen-process starts, or evidence creation; the corrected 13-field assertion passed in the final static validation.
- The first staged whitespace check found one extra blank line at EOF in the new Hard Failure 20 Review 1 document. It performed zero writes or frozen-source activity; the line was removed without deleting a file, and the corrected staged diff check is clean.
- A staged-index identity helper correctly returned both registered bytes/SHA-256 identities, but its optional line-ending counters matched literal backslash sequences and produced unusable 0/0 values. Those counters are discarded; the two-blob helper made zero writes or frozen-source starts, and the final check uses byte values 10/13.
- Current state: `AMENDMENT_5G_B_1_1_1_1_7_COMMAND_LINE_DIAGNOSTIC_PACKAGE_AWAITING_INDEPENDENT_APPROVAL`. Nested PRE, POST, FINAL, TERMINAL, synthetic, official, Gold, reservation, and Stage3B remain locked.

### Hard Failure 21: Post-Governance Direct GitHub TLS Transport Gate

- Amendment 1.1.7 approval governance `f5a9ce38d10d419f8bc92772030f0d7cb77914cb` is the valid exact two-path, zero-deletion direct child of package `8e274060baf844dd1d761e7635bbc6c43ef9d4b6`; its push succeeded.
- The ordered post-governance gate made exactly one direct GitHub main query. It returned a TLS connect error before yielding a remote ref, so the established boundary is transport failure rather than ref mismatch, wrong SHA, push failure, or package/observer defect.
- Independent review later observed remote main at `f5a9ce38...` through a separate connector. That later fact does not retroactively pass the failed gate and does not permit continuation.
- Counts are direct-query attempts 1, successes 0, retries 0; parser/static observer gates 0; observer/capture host/adapter/parent/loader/target starts 0; `HGRAGC17` creations 0; result commits/pushes 0; difference interpretations 0.
- The observer process quota was not exercised, but the approval-governance chain terminated at the failed ordered gate and is non-reusable.
- Hard Failure 21 audit is an exact five-path, zero-deletion direct child of `f5a9ce38...`. It contains no raw, observer change, Approval Decision, parser output, or post-hoc remote diagnostic artifact.
- Current state: `AMENDMENT_5G_B_1_1_1_1_7_POST_GOVERNANCE_DIRECT_GITHUB_QUERY_STOPPED_HARD_FAILURE_21`. A new bounded remote-transport policy requires a separately reviewed and approved Amendment before any parser or observer action.

### Hard Failure 21 Review 1 And Amendment 5G-B.1.1.1.1.8

- Independent Review 1 accepts checkpoint `c4ac4b90ea57c18502766b5cba288f67cc46e60b`, its exact five-path scope, valid approval/push, TLS transport boundary, zero retry/parser/observer/evidence counts, and terminated non-reusable approval chain.
- Amendment 1.1.8 adds one 294-line / 9,964-byte / `7EBC6F40...1C4567` ASCII/LF Python helper. Package assembly performs four AST parses but zero helper executions and zero primary/alternate remote calls.
- Primary is one fixed Git `ls-remote --heads` query. Only TLS, DNS, connection-reset-before-ref, or HTTP-transport-unavailable with no returned ref may transition to one Python-urllib GitHub REST query. Same-method retries are zero and total remote calls are at most two.
- Any returned SHA mismatch, ambiguous/multiple ref, auth rejection, malformed response, unregistered primary failure, or alternate failure is terminal before observer parsing or execution.
- The package keeps the existing 1.1.7 observer, Manifest, invocation, `HGRAGC17` format, and absent result path byte-for-byte unchanged. It selects the narrower no-attestation design; remote success writes no repository file.
- The package is an exact eight-path, zero-deletion direct child of HF21. Manifest is 12,757 bytes / `672FBD0C...CBFDC75`; the package authorizes no remote call or execution. Current state is `AMENDMENT_5G_B_1_1_1_1_8_BOUNDED_REMOTE_TRANSPORT_PACKAGE_AWAITING_INDEPENDENT_APPROVAL`.

### Hard Failure 22: Bounded-Helper Launch Wrapper Parse Stop

- Amendment 1.1.8 approval governance `4d9886be1291133c7a8f94c3a4b35a14f26e0a8d` is the valid exact two-path, zero-deletion direct child of package `90438287...`; its push succeeded.
- The post-governance local/tracking/clean/path/identity gate passed without a direct remote query. The one authorized bounded-helper AST/static gate also passed with helper execution and remote calls still zero.
- The next PowerShell launch wrapper failed at parse time because `$exitCode:` inside a double-quoted string was treated as an invalid variable reference. No wrapper statement ran and no `Process.Start()` occurred.
- Counts are launch-wrapper parse attempts 1, helper starts 0, primary/alternate calls 0/0, observer parser/process 0/0, `HGRAGC17` creations 0, result commits/pushes 0, retries 0, and difference interpretations 0.
- This establishes an orchestration wrapper parse defect only. It does not establish a bounded-helper source/static defect, remote transport/ref outcome, observer defect, or package defect.
- The approval chain is terminated and non-reusable despite its unexercised process/call quotas. The exact five-path, zero-deletion HF22 audit contains no result or execution-source change.
- Current state: `AMENDMENT_5G_B_1_1_1_1_8_POST_GOVERNANCE_HELPER_LAUNCH_WRAPPER_PARSE_STOPPED_HARD_FAILURE_22`. All execution remains locked pending independent review.

### Hard Failure 22 Review 1 And Amendment 5G-B.1.1.1.1.9

- Independent Review 1 accepts checkpoint `a740f669d535ab3a148c42f6839de6837eec9c15`, its exact five-path scope, valid approval governance/push, passed local identity and helper AST/static gates, and the zero-process/remote/observer/evidence boundary.
- The established root cause is the temporary expandable-string token `$exitCode:`. PowerShell raised `InvalidVariableReferenceWithDrive` while parsing the whole wrapper before any statement or `Process.Start()`; no Python-helper or remote/observer defect is inferred.
- Amendment 1.1.9 adds one tracked 184-LF / 7,952-byte / `898BDB48...DB0BC3D` ASCII PowerShell launcher. Its package-stage parser ran exactly once with 0 errors and 1,195 tokens; launcher/helper executions and remote calls remained zero.
- Static inspection records exactly one helper `.Start()`, two raw `CopyToAsync` drains, one `WaitForExit`, one `WaitAll`, no interpolation-variable-followed-by-colon token, and no repository-write API.
- The launcher freezes its 179-character PowerShell invocation, the unchanged 82-character Python-helper invocation, package/approval environment bindings, absent observation path, raw stdout/stderr capture, exit/stderr/framing gates, and five exact canonical PASS JSON variants.
- The package does not alter the 1.1.8 Python helper or transport policy, the 1.1.7 observer/Manifest, the `HGRAGC17` format, or the still-absent result path.
- The package is an exact eight-path, zero-deletion direct child of HF22. Manifest is 16,536 bytes / `35F4E35E...304D4FF2`; it contains no result file and authorizes no approval governance, post-approval parser, process, remote call, or evidence.
- Five read-only support checks failed without writes or experimental execution: nonexistent shortened HF22 path, local `rg.exe` access denial, unavailable static `.NET SHA256.HashData`, a cross-file stop on Review 1's omitted full launcher SHA, and a recursive reference scan that exceeded the exact package paths and read tracked historical result files. The last scan's candidate set also contained tracked reservation metadata and test source paths, but no matching content from those paths was returned and no reservation/test or historical-result value informed a package decision; no project-external path was read. Corrected actual-path, `Get-ChildItem`, `SHA256.Create().ComputeHash()`, Review identity, and exact-eight-path checks passed.
- Current state: `AMENDMENT_5G_B_1_1_1_1_9_TRACKED_PREPARSED_LAUNCHER_PACKAGE_AWAITING_INDEPENDENT_APPROVAL`. A future approval must bind the actual package commit before any new parser or execution.

### Hard Failure 23: Tracked Launcher Nonzero Exit

- Amendment 1.1.9 package `046ac17282e1a4dcdedb7f6d744899dedf44d4b5` was approved through exact two-path, zero-deletion direct-child governance commit `ef9ba5b3aabfb0be8deeaf569b46e58c3cdf68aa`; the commit was pushed before post-approval parsing or execution.
- The no-direct-remote local/tracking/clean/path/source identity gate passed. The unique tracked-launcher PowerShell parser/static gate and unique helper AST/static gate also passed with zero process, remote, observer, and evidence activity during those gates.
- The exact tracked launcher was started once and returned exit 1. The outer executor observed stdout 0 bytes, stderr 503 bytes, and no PASS.
- The raw stderr content was not durably preserved. Its text, SHA, error class, and root cause are unavailable and must not be reconstructed.
- Evidence does not establish whether the helper started; helper start, primary/alternate/total remote call, and same-method retry counts are `UNCONFIRMED`. No helper, transport, remote-ref, PASS-framing, launcher-source, or package defect is claimed.
- Observer parser/static/process counts are zero because the outer PASS gate failed. `HGRAGC17`, result commits, and result pushes are zero, and the registered observation path remains absent.
- No second launcher, direct helper bypass, cleanup, overwrite, stderr reconstruction, or post-failure experimental diagnostic execution occurred. The approval chain is terminated and non-reusable.
- The Hard Failure 23 audit is an exact five-path, zero-deletion direct child of `ef9ba5b3...`; it contains no source, result, raw, parser output, or post-hoc diagnostic artifact.
- Current state: `AMENDMENT_5G_B_1_1_1_1_9_TRACKED_LAUNCHER_NONZERO_STOPPED_HARD_FAILURE_23`. Independent review and a separately governed Amendment are required before any resumption.

### Hard Failure 23 Closure And Governance Simplification

- Independent Review 1 accepts checkpoint `c09f5ee5018ed48d63f28aef11ad5ddccffa7406`, the valid approval lineage, launcher 1/exit 1/stdout 0/stderr 503 non-durable facts, observer/result zero boundary, and no-retry compliance.
- Helper start and primary/alternate/total remote-call exact counts remain unconfirmed; their structural bounds are 0–1, 0–1, 0–1, and 0–2. Same-method retries are exactly zero from the frozen non-loop single-call structure.
- The project declines the proposed Amendment 1.1.10 nested stderr capture. The unpreserved 503-byte payload will not be reconstructed or investigated further.
- The 1.1.7–1.1.9 PowerShell launcher, remote verification, command-line observer, and nested PRE chain remain immutable historical failed implementations and are removed from the planned execution route.
- Governance now uses Level A scientific-critical review, Level B integrity review, and Level C runtime-infrastructure logging. Scientific hard gates remain focused on data, Gold isolation, algorithm/ranking behavior, outputs, metrics, and statistical conclusions.
- The planned replacement is one frozen JSON config, one direct Python preflight/controller, one independent verifier, committed rankings, and a separate Gold evaluator. Scientific settings and advancement gates remain unchanged.
- No replacement runner or official execution is authorized by this governance record. Current state: `STAGE4B_U1_HF23_CLOSED_GOVERNANCE_SIMPLIFICATION_ADOPTED_IMPLEMENTATION_PENDING`.

### Simplified Execution Protocol v1 Freeze

- `docs/STAGE4B_U1_SIMPLIFIED_EXECUTION_PROTOCOL_V1.md` freezes the Level A contract for one pre-Gold JSON config, direct Python preflight/controller, committed decisions/rankings/policy, one independent verifier, and a separately approved Gold evaluator.
- It binds the 4,500-query/143,820-unit unlabeled boundary, exact input/cache identities, Python 3.12.0 environment, full retrieval config, q25/protect/insert/effective-K rules, U1 ECDF score, 0.60 ordered-prefix budget, output schemas, verifier gates, and unchanged U1-D advancement gates.
- Semantic equivalence replaces PowerShell/file-byte equivalence and is restricted to synthetic fixtures during implementation review. No command-line bytes, TLS, GitHub-main query, stderr framing, observer, or nested process topology is a scientific gate.
- The pre-Gold config intentionally contains no Gold-map/hash or reservation identity. Gold-specific inputs may be passed only to the evaluator after committed `VERIFIED_PRE_GOLD`, independent review, and separate approval.
- This freeze adds no config, implementation, result, Gold access, reservation access, or execution authorization. Current state: `STAGE4B_U1_SIMPLIFIED_EXECUTION_PROTOCOL_V1_FROZEN_AWAITING_LEVEL_A_REVIEW`.
- An author-side `academic-research-suite` compatibility validation found that initial freeze `8657709...` replaced policy and pre-Gold keys that the unchanged evaluator hard-checks. Before independent Level A review, the protocol was corrected to retain legacy `stage4b_u1_v2` / `stage4b_u1_v2_3_1` / scientific-protocol fields and evaluator-required `synthetic_test_mode`, `frozen_commit_sha`, `implementation_hashes`, and `artifact_hashes`, while adding separate simplified-route bindings.
- The same correction completes the later evaluator interface without placing Gold identities in the pre-Gold config. It does not constitute independent acceptance or authorize implementation/execution; state remains `STAGE4B_U1_SIMPLIFIED_EXECUTION_PROTOCOL_V1_FROZEN_AWAITING_LEVEL_A_REVIEW`.

### Level A Effective-K Compatibility Correction

- Independent Level A review bound corrected commit `76dc179acbb657633fc1da1e4c5fbd398169e284`, accepted the simplified protocol direction, and returned exactly one compatibility correction: remove the evaluator's fixed-20 assumption while preserving the frozen effective-K semantics.
- `scripts/stage4b_u1_evaluate.py` now derives `K_q` from the dense list, accepts only `1..20`, uses `P_q=min(10,K_q)`, checks equal lengths and uniqueness, bounds planned insertion by `min(4,K_q-P_q)`, derives inserted IDs from the effective slice, enforces protected-prefix and final-selector rules, and requires the independently verified ranking-structure/candidate-membership attestation before Gold evaluation.
- The correction does not delete or pad short-candidate queries and does not change data, candidate generation, grain balls, hyperedges, q25, score, ECDF, allocation, ranking, endpoints, Gold inputs, or statistics. Evaluator SHA-256 is now `D7B96E29AD5AB2F6652FFC14D73048D36C205F78ABA7FA8FCB501818A1A89BBB`.
- Targeted synthetic tests passed 13/13 for candidate sizes 20, 17, 10, 9, and 1 plus overflow, prefix, duplicate, selector, inserted-ID, empty-pool, and attestation failures. The required complete synthetic suite passed 63/63. No official, Gold, reservation, Stage3B, or historical official ranking content was read.
- Current states: `LEVEL_A_PROTOCOL_ACCEPTED`, `LEVEL_B_IMPLEMENTATION_AUTHORIZED`, `OFFICIAL_EXECUTION_NOT_YET_AUTHORIZED`, `GOLD_EVALUATION_NOT_AUTHORIZED`, and `RESERVATION_NOT_AUTHORIZED`.

### Simplified Level B Implementation And Config Freeze

- Implementation commit `2dade07843194635f814ef53d0880f0ea7207451` adds exactly three direct Python entry points plus one synthetic test module: strict config/preflight, Gold-free runner, independent verifier, and Level B tests. It does not modify the four frozen pre-Gold algorithm sources and does not import or invoke the evaluator from the runner.
- The runner reuses the frozen retrieval, ECDF, score, ordered-prefix allocation, and ranking functions; it requires the existing ID-bound cache, writes three pending artifacts, verifies cache stability, and performs guarded promotion with rollback. The verifier independently reloads candidates and recomputes score/allocation/effective-K/membership/prefix/inserts/final selection without calling the runner.
- Config commit `47a189f3e092aee616dbf13ed397230b8ccb8371` separately freezes `configs/stage4b_u1_d_official.json`, SHA-256 `56F7A177C428BCDA783F1B1B33706B9ED2C0A6A88F08BAE3D7347BA3DA377D21`, binding implementation commit `2dade078...`, seven exact source hashes, the accepted protocol, evaluator, official unlabeled inputs/cache identities, absent future outputs, and `authorized=false` for evaluation.
- Eleven targeted Level B synthetic tests passed. The final repository-wide `test_stage4b_u1*.py` suite passed 270/270 in 12.196 seconds. Semantic-equivalence coverage confirms decisions and rankings are field-wise identical to the frozen route on the same synthetic inputs; failure coverage includes duplicate/non-finite config, implementation drift, require-existing cache, pre-existing/partial outputs, candidate membership, final selector, and config binding.
- Only config schema/code/Git-blob/tracked-file bindings and the absence of all six registered future outputs were checked after config freeze. No official preflight, runner, verifier, development input/cache, historical official ranking, Gold, reservation, or Stage3B path was opened. Current state: `LEVEL_B_IMPLEMENTATION_COMPLETE_AWAITING_INDEPENDENT_REVIEW`.

### Simplified Level B Review Submission

- `docs/STAGE4B_U1_SIMPLIFIED_LEVEL_B_REVIEW_REQUEST.md` submits implementation commit `2dade078...` and config commit `47a189f...` for one concentrated integrity and synthetic-equivalence review.
- The requested verdict is either `ACCEPT_LEVEL_B_IMPLEMENTATION` or `RETURN_FOR_MINIMAL_LEVEL_B_CORRECTION` with an exact integrity defect. The request does not recreate an Amendment chain or classify ordinary Level C presentation/tooling issues as scientific failures.
- Review-package preparation performed only project-source/hash/history and future-output-absence checks. It did not run official preflight/controller/verifier or read official development/cache, historical official rankings, Gold, reservation, or Stage3B.
- Current state: `LEVEL_B_REVIEW_REQUEST_SUBMITTED_AWAITING_INDEPENDENT_REVIEW`. Even acceptance will require a later explicit execution authorization before the first official input or cache read.

### Strict Row-Contract Level B Correction

- Independent Level B review returned one integrity defect: the simplified verifier checked key sets and converted query/count/ranking values before fully enforcing the protocol's native JSON types, row identities, nullability, and raw ranking-ID strings.
- Correction commit `8ab5e193d00733e0ae617b2c17f02da4ce01594f` changes exactly the verifier and simplified test module. Strict checks now run before downstream conversion and cover frozen row identity, native non-empty strings, bool-excluding integers, finite JSON numbers, feasible nullability, positive ordered rank, and all ranking-array element types.
- Seven requested failures were added to the retained 11 tests. Targeted results are 18/18; the required single complete `test_stage4b_u1*.py` run passed 277/277 in 14.954 seconds. No double rerun occurred.
- Direct-child config rebind `fba85c990efb0e3009a4c9fb0ca486ba1485c1f9` updates only the code commit and verifier SHA. Config SHA-256 is now `8481D856F27D422B81CFBFDC57C59FD3F8A8E7C0C85A01DC6DD3D0F05F57DDB1`; evaluator/protocol/scientific/input/cache/output bindings are unchanged.
- Follow-up review is `docs/STAGE4B_U1_SIMPLIFIED_LEVEL_B_FOLLOWUP_REVIEW_REQUEST.md`. No official or Gold boundary was crossed and all six future outputs remain absent. Current state: `LEVEL_B_STRICT_ROW_CONTRACT_CORRECTION_SUBMITTED_AWAITING_FOLLOWUP_REVIEW`.

### Standing Pre-Gold Execution Authorization

- The independent Level B follow-up accepts correction commit `8ab5e193d00733e0ae617b2c17f02da4ce01594f`, config rebind `fba85c990efb0e3009a4c9fb0ca486ba1485c1f9`, and the accepted config SHA-256 `8481D856F27D422B81CFBFDC57C59FD3F8A8E7C0C85A01DC6DD3D0F05F57DDB1` before the governance-only protocol-hash synchronization.
- Execution governance now treats official preflight, the Gold-free controller, the exact three-artifact commit/push, the independent verifier, and the separate `VERIFIED_PRE_GOLD` commit/push as one standing-authorized transaction. There is no per-step pause, per-commit review, or per-run authorization inside this route.
- Level B/C engineering defects may be corrected, tested, rebound when bytes change, committed, pushed, and resumed without a new Amendment when scientific semantics, Gold isolation, registered input/cache identity, and official-artifact integrity remain unchanged. Daily direction review is enabled and non-blocking.
- Mandatory pause boundaries remain Gold/evaluator access, reservation, scientific-semantic change, and formal integrity anomalies such as Gold leakage, a wrong official input/cache, untrusted rankings, partial/inconsistent output promotion, local/tracked/remote artifact-byte mismatch, or verifier inability to confirm integrity. Temporary push/remote-visibility, path, permission, dependency, logging, or preflight-before-output failures remain non-blocking Level C work.
- The governance update changes no data, candidate generation, grain-ball or hyperedge logic, q25, effective-K, U1 score, allocation budget, ranking rule, endpoint, evaluator, or statistical rule. Current states: `LEVEL_B_IMPLEMENTATION_ACCEPTED`, `STANDING_PREGOLD_EXECUTION_AUTHORIZATION_GRANTED`, `DAILY_DIRECTION_REVIEW_ENABLED`, `GOLD_EVALUATION_REQUIRES_PAUSE`, `RESERVATION_REQUIRES_PAUSE`, and `SCIENTIFIC_SEMANTIC_CHANGE_REQUIRES_PAUSE`.
- Because official preflight hard-checks the simplified-protocol SHA, the required protocol governance edit synchronizes only `protocol.sha256` to `ABED88FAC906748CE9D93F04C0D4BA35B62BB6819F61A2D84273687BE35C724C`; the resulting config SHA-256 is `176FF6747680DD597DB01E174619CABF7112BF4B91FF8BF2402F5B02754A5F58`. Implementation commit/file hashes, evaluator, scientific settings, input/cache identities, and output paths are unchanged.

### Simplified Official Pre-Gold Completion

- Governance commit `f7859dd1c6aa0d81170ea6ce87e3b9ffc5c733cb` was pushed before official access. An initial unnecessary `-I` invocation failed during sibling-module import before config/official input/cache access and before any output; direct `-B` entry-point import checks passed and the Level C command correction was pushed as `138f2fd4047d262352b9c7489dfc2110887e88fb` without implementation/config/scientific changes.
- Official preflight passed with config SHA-256 `176FF6747680DD597DB01E174619CABF7112BF4B91FF8BF2402F5B02754A5F58`. The Gold-free controller covered 4,500 queries and selected 1,195; it produced only decisions, rankings, and policy.
- The exact three-artifact commit is `9357c157217f85008fa93df07d321a2f4c6a2bc1`. Decisions/rankings/policy SHA-256 values are `4B2AD2E5...A456A`, `ED289D23...E03CB`, and `657E5F25...D868B` respectively.
- The independent verifier recomputed all 4,500 queries and passed. `VERIFIED_PRE_GOLD` is 3,479 bytes / SHA-256 `39EAD86A3A835983DCB67BAF656255F51569BCEE5B9AC2E16FACF404281D7818`, with `gold_inputs_loaded=false`, `evaluation=null`, and every check equal to PASS; its single-path commit is `83d172bc89efbb31782eee308bac5293aa24457b`.
- Gold query audit and evaluation summary remain absent. Current state: `VERIFIED_PRE_GOLD_COMMITTED`, `GOLD_EVALUATION_REQUIRES_PAUSE`, `RESERVATION_REQUIRES_PAUSE`, and `SCIENTIFIC_SEMANTIC_CHANGE_REQUIRES_PAUSE`. No U1-D efficacy or metric conclusion is authorized from pre-Gold evidence alone.

### Repository Entry-Point Reorganization

- The repository separated current scientific entry points from cumulative execution-governance history after verified pre-Gold completion. No scientific protocol, config, implementation, formal result, historical Amendment, Review, Approval, or Hard Failure artifact was deleted or rewritten.
- The pre-reorganization long-form `README.md`, project `AGENTS.md`, and `docs/REPRODUCIBILITY.md` were preserved byte-for-byte under `docs/archive/`. Concise current versions now cover only the active research question, evidence level, frozen artifacts, current governance, reproduction boundary, and next scientific gate.
- `docs/INDEX.md` now distinguishes current normative files, current formal artifacts, scientific design evidence, and historical governance file families. Existing historical evidence remains at its original path to preserve SHA and link stability.
- The reorganization changes no implementation/config/protocol/result bytes and therefore requires link/static/binding checks rather than an algorithm suite. Current scientific state remains `VERIFIED_PRE_GOLD_COMMITTED`; Gold evaluation and reservation remain locked.

### Stage4B-U1-D Gold Evaluation And Branch Stop

- The user explicitly authorized only the frozen Stage4B-U1-D development Gold evaluation on 2026-07-18. Gold authorization/config/verifier commit `1bfcf7b108dd4a8db17ba97a4d3b97a6f274f983` was pushed before metric execution; reservation and Stage3B were not authorized.
- The evaluator used the already committed ranking/policy/`VERIFIED_PRE_GOLD` identities, the registered 4,500-query development Gold map, evaluator audit, Stage4A-R2 baseline references, 10,000 bootstrap iterations, and seed `20260712`. No Gold value entered controller construction, candidate generation, score, allocation, or ranking.
- Primary evaluation exited 0 in 51.6 seconds. The preregistered deterministic rerun exited 0 in 56.9 seconds. Query-audit and summary pairs matched byte-for-byte: SHA-256 `8616C28C...F938313` and `7F82056F...7F89DE` respectively.
- The independent Gold verifier did not import the evaluator. It rebuilt 4,500 query rows, overall/type summaries, Stage4A baseline equivalence, advancement gates, and output identities; all integrity checks passed. `VERIFIED_POST_GOLD` is 2,293 bytes / SHA-256 `44BF3E8B0B036958633E237186A458B13090D8073F587657D831656FB7720ECD`.
- U1 reduced inserted units from 7,260 to 4,354 (`40.0275%`) and kept conditional false-insert-rate worsening to `+0.002582`, so those two gates passed. Gain retention was `47/94=0.5000`, harm retention was `53/69=0.7681`, retention gap was `-0.2681`, and the one-sided Fisher p-value was `0.999889`; both mechanism gates failed.
- U1 CR@20 was `0.77089`, delta `-0.00133` versus Dense and `-0.00689` versus q25; both development CR gates failed. The retention-gap bootstrap interval was `[-0.4091,-0.1183]`, the U1-vs-Dense interval was `[-0.00578,0.00311]`, and the U1-vs-q25 interval was `[-0.01044,-0.00333]`.
- `compositional` and `inference` were marked `SUBGROUP_CAUTION`; type rows remain descriptive and do not override the overall frozen decision.
- A post-result protocol-completeness audit found that the scientific protocol asks for question-type intervals, while the frozen evaluator/verifier only emitted and checked type-level point estimates and caution flags. No post-Gold interval method was selected or retrofitted. This is a reporting-completeness `CAUTION`; it does not affect the four failed aggregate development gates or the branch-stop decision.
- The 6 development gates passed 2 and failed 4. The exact frozen outcome is `STOP_U1_BRANCH_KEEP_RESERVATION_LOCKED`. This is a verified negative scientific result, not an execution failure, and it forbids post-result adjustment/re-execution on the same development batch.
- The five verified result artifacts were first committed and pushed as `c06761f0c55cbeecf75564211a59f4540cfbae06`. `core.autocrlf=true` normalized the two 7,662-byte CRLF summaries to 7,467-byte LF tracked blobs, while the JSONL and verification blobs stayed exact. This formal byte mismatch was reported and paused before documentation commit.
- Authorized correction commit `b500184bc581d73a381de65c32cf3b72e9758cc9` adds exactly two `.gitattributes -text` paths and re-adds only the existing frozen summary bytes. Local, index, commit, and directly fetched GitHub blobs are all 7,662 bytes / `7F82056FB14F9D8D73E668A82CB5304B28385E62A01C428599F23260AB7F89DE`; primary and rerun remain byte-identical. The other three Gold result objects, rankings, policy, and pre-Gold verification did not change.
- Reservation metrics and Stage3B were not accessed. The result rejects only the frozen U1-D controller, not HyperGranular-RAG as a whole. Any future controller is a new scientific-semantic proposal requiring a new development protocol and explicit authorization; this result is not permission to open reservation.

### Stage4C-U1-FMA Failure Mechanism Audit

- The user authorized a post-Gold exploratory diagnosis of the frozen Stage4B-U1-D failure without reopening U1-D, running a new efficacy evaluation, or accessing reservation/Stage3B. Protocol commit `2e925063175a6402a21ade3fc0ab4a27faaa6dd7` was pushed before diagnostic statistics.
- Implementation commit `1bbe8a571d4e0c4aa965b4f0fa71b1de5901b2a7` adds one NumPy-based diagnostic script and one targeted suite. The corrected discover invocation passed 16/16 tests; an earlier dotted-module invocation loaded no tests because `tests/` is not a package.
- The one official Stage4C run covered 4,500 queries and atomically produced six artifacts. Frozen reconciliation is 94 GAIN, 69 HARM, 4,337 NEUTRAL, 47 retained GAIN, and 53 retained HARM. All seven Stage4B input SHA-256 identities remained unchanged.
- Raw U1 score is harm-high for GAIN-vs-HARM: AUROC `0.39269`, 95% bootstrap interval `[0.30558,0.48150]`. Score-minus-uncertainty AUROC difference interval is `[-0.16482,-0.00709]`, but the preregistered multiplication flag remains false because readiness's harm-high interval criterion did not pass.
- The fixed rank audit is `D_LOCALIZED_OR_IRREGULAR_SIGNAL`: the first two deciles have slightly negative retention gaps, decile 3 contains 4 gains and 17 harms, and later gains are localized rather than monotonically concentrated at the top.
- Query-level composition is structurally limiting: 92 `MIXED_GAIN_NOISE_QUERY`, 2 `PURE_GAIN_QUERY`, and 69 `DISPLACEMENT_HARM_QUERY`; `ALL_ON_OFF_LIMITATION_EVIDENCE=true`. Candidate Gold identity/rank and candidate score/support/similarity/facet/hyperedge fields are unavailable in the seven allowed artifacts and were not backfilled.
- Fixed Task-A OOF AUROCs are `0.60762` for ORIGINAL_U1_8, `0.54001` for RANK_STRUCTURE_6, and `0.61810` for COMBINED_14. None reaches the frozen stable-signal rule; the partial ORIGINAL/COMBINED signal also prevents classification as uniformly insufficient.
- The final frozen decision is `MECHANISM_EVIDENCE_INCONCLUSIVE`. Evidence confidence is `CAUTION`: this is same-development post-Gold exploration with complete prespecification but no multiplicity correction and no candidate-level target identity. No U2 protocol draft or implementation was created.
- Stage4B-U1-D remains a valid negative result. Reservation remains locked. No new controller efficacy has been established.

### Stage4D-CMA Candidate Marginal-Utility Attribution Audit

- Level A accepted the complete eligible candidate universe, explicit `ORIGINAL_INSERT_SET`/`BEYOND_ORIGINAL_BUDGET` reporting, standardized first-slot insertion utility, primary `LOO_NO_BACKFILL`, replacement-only `LOO_WITH_BACKFILL`, seven mutually exclusive labels, combined-only advancement panel, fixed L2 logistic v1 probe, and the minimum-feasibility-not-power interpretation.
- The draft was promoted with `git mv` to `docs/STAGE4D_CANDIDATE_MARGINAL_UTILITY_AUDIT_PROTOCOL.md`. The core implementation/synthetic commit is `b4dfa52d0a38409dfc19444d21beec59606088e1`; guarded Channel-B/probe artifact transactions were completed in `730daea1350616bfdcb6a11832b361c4d574d985`.
- Channel A code constructs a Gold-free full candidate trace, retains budget-external eligible candidates, checks all frozen Stage4B input identities, and has a separate strict verifier that independently rebuilds candidate availability, Dense/q25 rankings, source ball/edge fields, and deployable numeric features.
- Channel B code uses Gold only for targets, implements standardized-single and both LOO counterfactuals, keeps ER-only labels outside Task C, strips question type, and reports events and deltas overall and by budget region.
- The fixed probe uses exact GroupKFold query grouping, fold-local preprocessing, L2 logistic regression only, 4 predeclared panels, same-OOF budget stratification, 10,000-query-cluster bootstrap semantics, and a combined-only advancement decision function. Determinism is bound to CPython 3.12.0, NumPy 2.5.1, SciPy 1.18.0, scikit-learn 1.9.0, joblib 1.5.3, threadpoolctl 3.6.0, narwhals 2.24.0, float64 inputs, fixed order, and one-thread settings.
- The final synthetic suite passed 16/16, including complete-pool reconstruction, strict schema/type/leakage rejection, all seven labels, dual-LOO separation, fixed fold reuse, Task-C ER-only exclusion, same-OOF stratum checks, combined-only advancement, deterministic LF CSV rendering, exact environment binding, fail-closed official entry points/transactions, and byte-identical synthetic rerun.
- No official 4,500-query Channel A run occurred. No official unit/embedding trace, Stage4D Gold access, Channel B run, formal Stage4D artifact, reservation/Stage3B access, or U2 implementation occurred. The mandatory pause is immediately before the first official Channel A execution.

### Stage4D-CMA Official Attribution, Probe, And Final Decision

- Authorized Gold-free Channel A produced and independently reconstructed 4,500 query traces and 8,467 candidate traces. Channel B then built the seven-label counterfactual attribution over the frozen development Gold target map; its 8,467 labels reconcile to 94 q25 CR-gain queries and 69 q25 CR-harm queries.
- Candidate labels comprise 113 `MARGINAL_GAIN`, 100 `DISPLACEMENT_HARM`, 86 `EVIDENCE_GAIN_ONLY`, 42 `EVIDENCE_HARM_ONLY`, 103 `INTERACTION_DEPENDENT`, 413 `REDUNDANT_GOLD`, and 7,610 `NEUTRAL_NOISE`. The complete universe retains 7,260 `ORIGINAL_INSERT_SET` and 1,207 `BEYOND_ORIGINAL_BUDGET` candidates.
- The official fixed probe used CPython 3.12.0 and the pinned one-thread environment. It produced 2,446 query fold assignments, 68,588 OOF predictions, and the registered metrics. The first transaction completed two probe runs, byte identity, internal independent verification, and atomic promotion after its outer shell wait timed out; a later no-timeout transaction completed its computation but the no-overwrite guard rejected promotion and changed no existing artifact.
- A separately authorized read-only provenance audit reconstructed the existing probe container, passed all canonical byte, identity, fold, Task-C label, probability, fixed-panel, expected-row, and existing independent-verifier checks, and recomputed every overall/fold/budget-region metric. It repeated 36 registered query-cluster bootstrap blocks with seed 20260719 and 10,000 iterations per block; all intervals and sample counts matched. Five protected artifact identities were unchanged before/after.
- The only advancement panel, Task-C `COMBINED_DEPLOYABLE_28`, obtained AUROC `0.64310 [0.55520,0.72974]`, AP `0.72198`, prevalence `0.53052`, and Brier `0.26321`. It failed the AUROC `>=0.65` gate and the Brier-versus-prevalence-baseline gate, while the four panels did not jointly meet the stop rule.
- The frozen final decision is `CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE`. Stage4B-U1-D remains a valid negative result; reservation, Stage3B, U2, and any new controller remain locked pending a new Level A scientific protocol and explicit authorization.

### Stage4D Closure And Stage4E-E2E Level A Draft

- Stage4D-CMA is formally closed after `STAGE4D_FINAL_VERIFICATION_PASSED`. Its frozen decision remains `CANDIDATE_MECHANISM_EVIDENCE_INCONCLUSIVE`; no existing Channel A, Channel B, probe, decision, report, or verification artifact is deleted, rewritten, or rerun.
- The current adaptive-controller line is frozen closed. Stage4B-U1-D remains a verified development negative result, while Stage4C and Stage4D remain exploratory mechanism evidence. No U2, replacement controller, feature/panel selection, threshold tuning, reservation, or Stage3B access follows from them.
- Stage4E-E2E asks a distinct question: whether the static all-query q25 protected-insertion ranking, without U1 or any learned controller, improves end-to-end answer quality relative to Dense under one fixed generator and one previously unread query boundary.
- The proposed new boundary is a deterministic 1,000-query, ID-hash-selected subset of official HotpotQA `hotpot_train_v1.1.json` in the closed distractor-context setting. It is a new-ID same-domain holdout, not a new benchmark and not external-domain validation. The raw source bytes/SHA, selected-ID digest, blind/Gold channel split, model files, exact environment, commands, and output paths must be bound before Level A acceptance.
- The draft freezes one primary endpoint, paired answer F1 difference (`static q25 - Dense`), with 10,000 paired query bootstrap iterations; answer EM is a non-inferiority guard. Retrieval coverage, context tokens, latency, and subgroup rows are secondary/descriptive and cannot replace the primary gate.
- No HotpotQA train file, Stage4E model, Stage4E embedding, Stage4E Gold value, or Stage4E result was read or generated while drafting. Level A was accepted on 2026-07-20 for input binding and Level B implementation. Current state: `STAGE4E_LEVEL_A_PROTOCOL_ACCEPTED`, `STAGE4E_INPUT_BINDING_AUTHORIZED`, `STAGE4E_LEVEL_B_IMPLEMENTATION_AUTHORIZED`, and `STAGE4E_OFFICIAL_EXECUTION_NOT_AUTHORIZED`.

### Stage4E-E2E Input Binding And Level B Implementation

- Canonical HotpotQA train identity is 566,426,227 bytes / `26650CF...CD316`. The canonical host timed out in three bounded attempts; an exact-revision transport mirror was accepted only after byte and SHA-256 equality. The deterministic hash sample contains 1,000 IDs with zero overlap against all registered historical HotpotQA query inputs.
- Source custody produced aligned blind, Gold-target, and sealed descriptive-metadata channels. Independent verification reconstructed the source selection, every row identity, context normalization, supporting-fact-to-unit mapping, channel bytes, historical zero-overlap, model snapshots, and environment manifest. Status is `STAGE4E_INPUT_CHANNELS_VERIFIED`; no retrieval, generation, or metric was computed by input freezing.
- The encoder snapshot binds 13 actual files at revision `1110a243...`; the Qwen generator binds 7 files at revision `989aa798...`. The isolated environment is CPython 3.12.0 / torch 2.12.1+cu130 / CUDA 13.0 / transformers 5.9.0 on an RTX 4060 Laptop GPU. Two synthetic encoder runs were byte-identical and two synthetic generator runs were token-identical.
- Level B implements a Gold-free blind-only runner, frozen Dense/static-q25 rankings, fixed Qwen prompt/decode, main/rerun artifacts, a separately locked Gold evaluator, and an independent verifier that does not import the evaluator. Nineteen targeted tests pass, including authorization-before-input, channel leakage, strict types, prompt cap, official answer scoring, deterministic bootstrap, decision gates, config binding, future-output absence, and atomic rollback.
- Both `official_execution.authorized` and `gold_evaluation.authorized` remain false in the config. The next boundary is exact-command confirmation for the first official Gold-free retrieval/generation transaction. Gold remains sealed until byte-identical predictions and `STAGE4E_PRE_GOLD_ARTIFACTS_VERIFIED` exist.

### Research Authorization Governance Simplification (2026-07-20)

- This is the durable project-wide governance baseline for every current and future research stage, not a temporary exception for this documentation task or Stage4E. Current governance is `STAGE_LEVEL_AUTHORIZATION_ACTIVE`, `ONE_RESEARCH_STAGE_ONE_AUTHORIZATION`, `STEP_LEVEL_APPROVAL_DISABLED`, `CHANNEL_LEVEL_REAPPROVAL_DISABLED`, `ENGINEERING_WORK_AUTONOMOUS`, `STAGE_INTERNAL_EXECUTION_CONTINUOUS`, `EXCEPTION_BASED_PAUSE_ONLY`, and `SCIENTIFIC_INTEGRITY_CONTROLS_RETAINED`.
- One stage authorization now covers all predefined implementation, tests, Channels/data reads, formal runs, fixed analyses, verifiers, deterministic reruns, reports, documentation, commits, pushes, and remote verification unless the experiment card explicitly excludes an item. Technical Channel/Gold isolation remains unchanged and no longer creates a separate approval gate.
- Exact commands, scripts, files, environment variables, commits, synthetic-test completion, and routine engineering corrections are not scientific approval objects. Routine faults are fixed minimally, tested, recorded, and execution continues.
- Execution pauses only for a new scientific question/stage/controller, a frozen scientific-semantic change, a new evidence source outside the current authorization, or a serious scientific-integrity anomaly. Historical approval chains remain immutable trace evidence but no longer define current execution.
- Existing Stage4E authorization was explicitly limited to input binding and Level B implementation, so official execution remains unauthorized without retroactive scope expansion. Its future boundary is stage-authorization scope, not exact-command confirmation; a scope that includes both predefined Gold-free and Gold Channels proceeds continuously through their frozen integrity gates.
- No scientific protocol, parameter, data boundary, algorithm, result, artifact SHA, or frozen conclusion changed in this governance-only update. No experiment or new data/Gold/reservation/Stage3B access occurred.

### Stage4E Generator Selection (2026-07-22)

- A frozen 200-query HotpotQA development comparison evaluated `Qwen/Qwen2.5-1.5B-Instruct` against the official `google/gemma-4-E2B-it-qat-mobile-transformers` format on the project RTX 4060 Laptop 8GB target. Both models completed main/rerun with byte-identical predictions and prompt audits; an independent verifier reconstructed channels, answer metrics, 10,000 paired bootstrap draws, and the selection rule.
- Under the RTX 4060 Laptop 8GB, fixed short-answer RAG prompt, 4,096-token cap, and actually deployable formats, Qwen2.5-1.5B-Instruct FP16 obtained answer F1/EM `0.44091/0.32000`, while Gemma 4 E2B official mobile-QAT obtained `0.33570/0.24500`. Qwen also used less wall time and peak VRAM, and the preregistered rule selected it as the sole Stage4E generator. Because Gemma ran in official mobile-QAT format, this result is a comparison of deployable systems under the frozen target environment, not an isolated comparison of base-model architectures.
- Gemma's local 2.5GB snapshot/cache and the temporary comparison runtime/adapters were removed after the evidence was committed. The experiment card, both models' predictions/audits/telemetry, query scores, summary, verification and report remain tracked; Git history retains the retired comparison implementation.
- The active Qwen environment was rebound to CPython 3.12.0 / torch 2.12.1+cu130 / CUDA 13.0 / transformers 5.14.1 / safetensors 0.8.0. Synthetic encoder bytes and generator token bytes remained identical to the earlier environment manifest.

### Stage4E-E2E Official Result (2026-07-22)

- The deterministic 1,000-query HotpotQA train distractor sample retained zero overlap with registered historical HotpotQA IDs. Gold-free main/rerun each completed 2,000 generation calls with zero failures. Predictions were byte-identical at 419,866 bytes / `FE9D6716...945D58`, and prompt audits were byte-identical at 3,337,447 bytes / `130B78B8...56055`.
- Independent pre-Gold verification reconstructed rankings, prompt contracts, identities, implementation/environment binding and the embedding cache before Gold was opened. Gold evaluation then used the frozen official HotpotQA answer scorer; independent post-Gold verification recomputed every query metric, bootstrap and decision.
- Dense vs static q25 answer F1 was `0.42150` vs `0.43628`; paired delta was `+0.01478 [0.00020,0.02988]`. Answer EM was `0.356` vs `0.366`; delta was `+0.01000 [-0.00500,0.02500]`. Retrieval CR@20 improved from `0.737` to `0.798`, and ER@20 from `0.87860` to `0.90818`.
- All preregistered positive gates passed, producing `STATIC_HGRAG_E2E_SUPPORTED` and `STAGE4E_FINAL_VERIFICATION_PASS`. The F1 interval lower bound is only slightly above zero, so the result is supportive but not a large or universal effect claim.
- Descriptive subgroup points suggest positive bridge/easy and slightly negative comparison directions, but they remain `SUBGROUP_CAUTION` without confirmatory intervals and cannot change the overall result. Stage4E is limited to a same-domain closed distractor boundary and does not authorize full-wiki, external replication, reservation, Stage3B, U2, or a renewed controller line.

### Stage4F-XDR Cross-Dataset Replication Card And Level B (2026-07-22)

- Stage4F asks one new question: whether Stage4E's static all-query q25 answer-F1 gain replicates on MuSiQue under the same MiniLM encoder, Qwen generator, prompt, Top-20 arms and q25 parameters. It is not a controller, model/prompt/K search, full-wiki experiment or subgroup confirmation.
- The official source is MuSiQue-Answerable v1.0 train: 19,938 unique rows, 241,046,755 bytes / `83A75B1E...248490A`, distributed under CC BY 4.0. The project previously used only answerable dev `[0:1000)`; all 1,000 historical native IDs were audited without opening the locked Stage3B slice. Train/history overlap is zero.
- ID-only deterministic selection froze 3,000 new queries. MuSiQue's 20 paragraph contexts would make paragraph-unit Top-20 degenerate, so a preregistered source-only regex sentence splitter preserves Stage4E sentence-unit semantics. The selected boundary contains 218,698 units, 27–151 per query; official evidence remains paragraph-level and no sentence-level Gold is invented.
- Source custody created aligned blind, Gold and sealed metadata channels. Independent verification reconstructed all three from the source, checked the selected-ID digest, historical overlap, source/archive identities, MiniLM/Qwen snapshot files, requirements/environment manifests and absence of every formal output. Status is `STAGE4F_INPUT_BOUNDARY_VERIFIED`.
- Level B implements source/input freezing, Gold-free Dense/static-q25 retrieval and Qwen main/rerun generation, official MuSiQue answer/alias scoring, paired 10,000-bootstrap decision logic, post-decision metadata handling, independent verification and guarded atomic/no-overwrite transactions. Twenty-four synthetic tests pass without official Stage4F data.
- Current state is `STAGE4F_XDR_EXPERIMENT_CARD_FROZEN`, `STAGE4F_SOURCE_BOUND`, `STAGE4F_INPUT_BOUNDARY_VERIFIED`, `STAGE4F_MODEL_ENVIRONMENT_BOUND`, `STAGE4F_LEVEL_B_IMPLEMENTATION_READY`, `STAGE4F_SYNTHETIC_TESTS_PASSED`, and `STAGE4F_OFFICIAL_EXECUTION_NOT_AUTHORIZED`. No official embedding, ranking, generation, metric, bootstrap, decision or Channel C result exists. Reservation, Stage3B and U2 remain locked.

### Stage4F-XDR Official Cross-Dataset Replication (2026-07-22)

- Stage-level authorization commit `a45e42303215b0c146538dfb1a34f9b3f0a05689` opened the complete frozen transaction. Main and rerun each produced 6,000 paired generation calls with zero failures. Predictions were byte-identical at 1,106,316 bytes / `68F95245...34E62E`; prompt audits were byte-identical at 8,573,108 bytes / `D27D24E7...FF132E`.
- Independent pre-Gold verification reconstructed all 3,000 Dense/static-q25 rankings from the frozen Blind Channel and embedding cache. Gold evaluation then used official MuSiQue answer/alias normalization. The strengthened final verifier independently rebuilt source channels, historical zero-overlap, model/environment binding, telemetry, prompt/ranking contracts, every query audit row, overall metrics, bootstrap, decision and artifact identities.
- Dense vs static-q25 answer F1 was `0.13595240` vs `0.14735383`; paired delta was `+0.01140143 [0.00449534,0.01835158]`. Answer EM was `0.10033333` vs `0.11033333`; delta was `+0.01000000 [0.00333333,0.01666667]`. Supporting-paragraph CR@20 improved from `0.589` to `0.650`, and ER@20 from `0.80553` to `0.84128`.
- All preregistered support gates passed, producing `STATIC_HGRAG_XDR_SUPPORTED` and `STAGE4F_FINAL_VERIFICATION_PASS`. q25 inserted 7,233 units across 2,336 queries; both arms retained 20 prompt units without rank-1 truncation. Hop-count Channel C rows are all `SUBGROUP_CAUTION` and cannot alter the primary decision.
- During finalization, a bounded implementation correction expanded `verify_postgold()` from bootstrap/decision-only coverage to the full frozen final-verification contract. Commits `ba3f1740bdd31f25b171e6c076072c7ce96b51e7` and `c890eda2fbc0bde048dcb4dfbb5a4a6abcd98e42` changed only the verifier, targeted tests and binding. Existing scientific artifacts were preserved; 27/27 tests passed; no model, data, ranking, evaluator, threshold, bootstrap or decision semantics changed.
- The result is a verified cross-dataset replication across two closed-candidate multi-hop QA boundaries with one frozen generator. It is not full-wiki/open-domain or cross-generator confirmation and does not reopen controller, reservation, Stage3B or U2.

### Stage4G-GTR Generator-Transfer Replication (2026-07-23)

- Stage4G asks whether the frozen static-q25 retrieval gain transfers to one additional result-independent, pre-specified generator configuration while reusing Stage4E/4F blind inputs, Dense/static-q25 rankings, prompt semantics and evaluators. It does not create a new dataset, rerun retrieval, compare multiple generators on official Gold, or test full-wiki/open-domain behavior.
- The bound generator is `google/gemma-4-E2B-it-qat-mobile-transformers@dd693ff40353f057ca5f07e945ad867f4afbf2ec`, run with Google's official mobile-QAT Transformers snapshot and thinking disabled. The 2,458,111,846-byte weight file has SHA-256 `EFAB4290...76A9A4`. Architecture, quantization and numerical-format effects are inseparable.
- Resource assessment froze determinism contract B before official output: one full 8,000-call main plus a pre-hash-selected, dataset-stratified 400-call rerun subset covering both datasets and both arms. The main completed with zero failures and zero truncation; the independent pre-Gold verifier established exact subset prediction/audit reproduction, ranking-prefix reconstruction, prompt semantics and Gold isolation.
- After `STAGE4G_GTR_PRE_GOLD_VERIFIED`, Gold evaluation scored 4,000 paired queries. HotpotQA Dense/static-q25 F1 was `0.349781/0.362429`, delta `+0.012647 [-0.002196,0.027444]`; MuSiQue was `0.044764/0.042444`, delta `-0.002320 [-0.006849,0.002076]`.
- Dataset-stratified equal-weight F1 delta was `+0.005164 [-0.002623,0.012950]`; equal-weight EM delta was `+0.002333 [-0.005667,0.010333]`. The support gate failed because the F1 point was below `+0.010`, its lower bound was non-positive, and the MuSiQue point was non-positive. No registered negative gate fired.
- The final decision is `GENERATOR_TRANSFER_INCONCLUSIVE`, with `STAGE4G_GTR_FINAL_VERIFICATION_PASS`. Independent verification rebuilt query scores, dataset and equal-weight bootstraps, the descriptive generator interaction and the exact decision.
- Descriptive F1 interaction (`Gemma retrieval delta - frozen Qwen retrieval delta`) was `-0.002132 [-0.021990,0.017276]` on HotpotQA, `-0.013721 [-0.021864,-0.005658]` on MuSiQue, and `-0.007927 [-0.018696,0.002856]` under dataset equal weighting. Interaction does not enter the primary decision.
- The only defensible transfer statement is that evidence under one additional pre-specified generator configuration is inconclusive. The result does not establish universal generator robustness, model-architecture ranking, Gemma unsuitability for RAG, or device-general efficiency. Reservation, Stage3B, U2 and the controller branch remain locked.
- A non-executional `paper/ABLATION_AND_STRONG_BASELINE_PLAN.md` records protected insertion/prefix/budget and structural ablations plus BM25, hybrid and stronger-dense baselines. It does not authorize new data, Gold, ranking or model runs.

### Stage4H-CBE Core Component Ablation And Strong Baseline Evaluation (2026-07-24)

- A stage-level continuous authorization opened a new HotpotQA/MuSiQue closed-candidate evaluation without changing Stage4E/4F/4G. ID-only salted selection excluded every registered historical formal query before choosing HotpotQA 1,000 and MuSiQue 1,500 rows. The final boundary contains 150,485 candidate units and zero historical ID overlap.
- Seven P0 arms were frozen before Gold: historical MiniLM Dense, Static q25 Full, no protection, no facet-hyperedge, BM25, fixed 0.5/0.5 Dense-BM25 hybrid, and one BGE strong dense. The generator remained Qwen2.5-1.5B-Instruct with the Stage4E/4F prompt/decode contract.
- `BAAI/bge-large-en-v1.5@d4aa6901...` was selected without Stage4H Gold based on official model-card retrieval use, MIT licensing, standard Transformers reconstruction and local synthetic determinism. The flat-unit arm was declared `NOT_FAIRLY_DEFINED` before Gold; the P1 effect-cost curve was `NOT_RUN_RESOURCE_BOUNDED`.
- The full main completed 17,500 calls with zero failures in 6,265.00 seconds; a pre-hash dataset-stratified subset completed 1,400 calls with zero failures. Subset predictions and prompt audits exactly matched their main projections.
- Independent pre-Gold verification reconstructed source-only selection, historical zero-overlap, cache identities, all 2,500 seven-arm rankings, 17,500 prompts and subset determinism. Gold was read only after this artifact passed.
- Four primary comparisons used dataset-specific paired bootstrap, dataset-equal-weight stratified bootstrap, 10,000 iterations, seed 20260725 and Holm correction. Full−Dense F1 was `+0.01357 [0.00491,0.02233]` (`SUPPORTED`); Full−StrongDense was `-0.03998 [-0.05393,-0.02621]` (`NEGATIVE`); Full−NoProtection was `+0.00354 [-0.00675,0.01389]` (`INCONCLUSIVE`); Full−NoFacet was `+0.01336 [0.00341,0.02343]` (`SUPPORTED`).
- BM25 and hybrid were fully reported as supporting baselines. Full−BM25 and Full−Hybrid equal-weight F1 were `-0.00755 [-0.02259,0.00773]` and `-0.00320 [-0.01591,0.00942]`; they did not enter advancement.
- Final verification independently rebuilt query metrics, bootstrap, Holm, decisions, artifacts and lock state, producing `STAGE4H_FINAL_VERIFICATION_PASS`.
- Three bounded engineering corrections preserved science and formal outputs: a pre-prediction no-facet ID serialization fix (`8f89148`), verifier cache-load renormalization (`5e811b1`), and prompt-audit projection comparison (`b406424`). An outer 180-second wait returned while pre-Gold verification continued normally; no duplicate transaction was started.
- The updated paper claim is deliberately narrower: Static q25 Full improves over the historical MiniLM Dense and benefits from facet-hyperedge within the frozen system, but it does not outperform BGE strong dense; protection remains inconclusive and granular-ball contribution lacks a fair flat control.
- The previously proposed `Stage4I-FWF` label was not opened; Stage4I was instead defined and executed as SDC under a separate frozen card. Full-wiki Gold, Reservation, Stage3B, U2, controller and new-generator/strong-retriever search remain locked.

### Stage4I-SDC Strong-Dense Complementarity (2026-07-24)

- A new ID-only salted sample selected HotpotQA 1,000 and MuSiQue 1,500 queries after excluding every historical formal ID. The boundary contains 150,649 candidate units and historical overlap 0.
- Four arms froze BGE Top-20, BGE+MiniLM-HGRAG protected, the same realized facet inserted set placed unprotected, and a protected no-facet sidecar. q25 remained exclusively in the MiniLM sidecar score space; no BGE threshold or score fusion was introduced.
- The blind-only eligibility gate passed: insertable-query rate was 0.458 on HotpotQA, 0.71333 on MuSiQue and 0.6112 combined.
- The full main completed 10,000 calls with zero failures; the pre-hash 200-query subset completed 800 calls with zero failures and reproduced every corresponding prediction and prompt audit exactly.
- The primary Protected−BGE equal-weight F1 delta was `-0.00256 [-0.00998,0.00458]`; EM delta was `-0.00233 [-0.00983,0.00467]`. Neither support nor negative gates fired, producing `STRONG_DENSE_COMPLEMENTARITY_INCONCLUSIVE`.
- Protected−Unprotected F1 was `+0.01122 [0.00129,0.02104]` with EM `+0.01300 [0.00333,0.02283]`, producing `PROTECTED_PLACEMENT_SUPPORTED`. Protected−NoFacet F1 was `-0.00743 [-0.01616,0.00132]`, producing `BGE_FACET_INCREMENT_INCONCLUSIVE`.
- The post-decision evidence audit found Protected net Gold `-8` on HotpotQA and `+9` on MuSiQue. The same candidate set under unprotected placement had identical added/displaced Gold totals but worse answer quality, consistent with placement-sensitive generator utilization; this remains descriptive.
- Independent pre-Gold and final verifiers rebuilt selection, caches, four-arm rankings, prompts, determinism, query metrics, 10,000-bootstrap, decisions, evidence transitions and artifact identities. Final status is `STAGE4I_FINAL_VERIFICATION_PASS`.
- A bounded cache round-trip correction preserved the exact stored float32 embeddings instead of re-normalizing them a second time; existing caches/rankings/trace/eligibility artifacts were not overwritten. An outer command timeout returned while the original main process continued; no duplicate process was launched.
- The paper claim is now narrower: structural expansion has verified value relative to the historical MiniLM Dense in Stage4E/4F/4H, but current evidence does not establish additional answer-quality value when the frozen MiniLM-HGRAG sidecar is attached to the pre-specified BGE strong backbone. Protected placement matters within the sidecar design, but does not make the sidecar superior to BGE-only.
- No next scientific stage is active. Starting full-wiki, a new retriever/generator search, Reservation, Stage3B, U2 or a controller requires a new stage-level scientific definition and authorization.
