# Bounded upgrade: selection value, context budget, and backbone strength

## Material Passport
Type: unexecuted experimental proposal, retained for traceability. Date: 2026-10-02. Base: `7a91fa1a4029d5fde85a4277bca1856fc45b306e`.
Status: **D_CONFIRMATION_INDEPENDENCE_UNVERIFIED_FALLBACK_TO_WRITING**. No new outcome has been read. This is not an execution lock or a completed preregistration.
Authority: current user request and `CODEX_BOUNDED_UPGRADE_AND_FALLBACK_ZH.md`.
This scoped authorization supersedes the earlier manuscript-only pause, but not reservation/Stage3B restrictions.

## Disposition after clarification and literature review
The user accepted GPU 12 h / CPU 24 h / new disk 10 GB / paid cost 0, but answered “不记得了” to prior confirmation exposure. Independence therefore cannot be established. No new formal experiment, synthetic GPU calibration, development selection, or confirmation evaluation was started. Do not replace the confirmation set. This is an eligibility limitation, **not method failure**.

The finite nearest-neighbor review is in `literature_refresh/2026-10-02_bounded/`. Its decision is **C_NOVELTY_OR_ACCESS_UNRESOLVED** for a stronger algorithmic novelty claim: two key granular-ball papers are only partially accessible. Available primary sources rule out a generic first combination / first hypergraph-RAG claim. The manuscript can still make the narrower, evidence-backed empirical contribution.

The sections below preserve the pre-outcome comparison proposal; their pending-language describes the initial proposal, not current execution authority. They are not adopted scientific semantics. The review retains matched MMR, actual-sentence coverage, ordinary grouping, Dense40/token controls, and a shared strong score as the right questions, but does not authorize execution. The F=C duplication and path-dependent bridge term cannot establish a distinct high-order objective. A future design must justify or remove those terms before locking; this round does not add a module to rescue novelty.

## Questions and estimands
Q1: Does structured selection improve answer F1 over matched simple selectors on the compact MiniLM backbone?
Q2: Does it improve the quality/cost trade-off over a larger Dense list and under a shared token cap?
Q3: Does the same target algorithm add value to the existing Qwen3 embedding + reranker backbone?
The primary unit is a query. HotpotQA and MuSiQue receive equal weights, irrespective of their sample counts.
This is a new dynamic joint selector, **BU-v2**, not the historical static-q25 algorithm. Neither successful synthetic tests nor new BU-v2 outcomes explain old static-q25 scores. Old artifacts and both editorial-final manuscripts remain intact.

## Data and exposure gate
Use only the existing Stage6 HotpotQA/MuSiQue channels; exclude 2Wiki entirely. Development: 200 queries per dataset, the first IDs sorted by SHA-256(`bounded-upgrade-dev-v1\0` + query ID) within the already bound development channel. These are development data, irrespective of earlier exposure. No outcome-dependent subsampling.
Confirmation, if eligible: the existing 800 HotpotQA + 1,200 MuSiQue queries, once only, all queries as denominators. No new confirmation collection or additional sample. Reuse the recorded historical-ID exclusions and check development/confirmation query identity disjointness from the blind channels.
The repository contains development main/rerun and pre-Gold verification, but no evaluation, selection lock, or confirmation outputs. **This absence is not proof of non-exposure.** A single user provenance clarification is pending regarding use outside this workspace. Confirmation labels remain unread until eligibility is documented, the selected configurations and complete predictions are fixed, and independent pre-Gold verification passes. If prior confirmation outcomes informed design, do not call this independent confirmation; stop that route and report D. No reservation, Stage3B, sealed metadata, new source corpus, or old unified Gold reads.

## Shared inputs and exact arms
Compact: the existing all-MiniLM-L6-v2 snapshot, normalized embeddings and cosine score; common pool is the first min(100,N) unique candidate sentences in stable score/ID order. Strong: existing Qwen3-Embedding-0.6B Top-min(100,N), all scored once by the existing Qwen3-Reranker-0.6B. Every selector within a backbone sees exactly that pool and those scores. No method gets extra model calls or candidates. Use the already bound Qwen2.5-1.5B-Instruct FP16 generator, greedy, beam=1, max-new-tokens=32, batch=1, fixed short-answer prompt, single-thread numerical environment.

Entry-budget contract: K=20; protected prefix p=10 compact, p=8 strong; mutable suffix K-p; **four optimized picks for every non-Dense selector**, at most four genuinely new IDs outside baseline Top-20, then fill in baseline order. A pick already inside Top-20 is a promotion, not new evidence. No group-count cap. Short candidate pools use effective K=min(K,N) and min(4,K-p) picks. Group count, optimized picks, new IDs, promotions, displacements and deduplication are separate fields.

| Family | Development settings per backbone | Confirmation rule |
|---|---|---|
| Dense20 / Dense40 | one each, no optimized picks | both retained |
| MMR | lambda in {0, .5, .7, .85} | best development setting |
| Actual sentence coverage | lambda in {0, .5, .7, .85} | best development setting |
| BU-v2 Full | lambda in {.7,.85} x leaf in {4,6} | best development setting |
| Spherical k-means | same four lambda/leaf pairs; k equals actual granular group count for that leaf | best development setting; count matching also reported |
| Size-matched random grouping | same four pairs, fixed seed 1729; exact granular group-size multiset | setting matched to selected Full, not seed search |
| Pure NoFacet / pure NoHyperedge | each of the four Full settings | paired with selected Full, not retuned |
| Dense-token / Full-token | Dense one; Full same four settings | Full's entry-budget-selected setting, no token-specific tuning |

Total: 35 configurations per backbone; 70 across two backbones. Full uses R's empirical percentile plus dynamic secondary terms: lambda R + (1-lambda)[.25 D + .25 C + .5(N+F+B)/3]. D is cosine diversity, C actual selected-sentence query-term coverage; N group novelty/distance; F actual selected-sentence facet gain; B degree-normalized two-group activation. With actual-sentence scope F=C: this overlap is explicit, not evidence of an independent higher-order mechanism. Pure NoFacet zeros F's coefficient; pure NoHyperedge zeros F and B; other coefficients, lambda, leaf and budgets stay unchanged. Group-union facets and phantom coverage are diagnostics, never counted as delivered sentence coverage. Bridge gain is a heuristic with known path dependence, not an exact submodular marginal or an answer-F1 guarantee.

K-means and random controls share the target score formula and differ only in grouping at matched settings. Independently tuned k-means compares pipelines, not pure grouping attribution. Report the matched-setting development contrasts separately. No unbounded model, seed or coefficient search. Static-q25 remains a historical anchor only; no new static-q25 run is planned.

## Real prompt and cost contract
Entry arms use at most 20 or 40 ranked sentences with a 4,096-token serialized-input cap, including question and chat template. Token arms use the complete min(100,N) ordered pool, with the same p and four optimized picks; after this prefix, baseline fill, **1,024 total serialized input tokens for both arms**. This is an identical enforced cap, not a claim of equal realized token counts. Stop at the first sentence that would exceed the cap; only an oversized first sentence may be partially truncated, matching the existing renderer. Record actual input IDs, visible evidence IDs/text spans/token offsets, omitted units, partial truncation and visible facets. Those exact input IDs must reach model.generate. Do not infer context exhaustion from Top-20 displacement.
Report EM/F1, token distribution, visible sentence counts, truncation, embedding/rerank/selection/render/generation times, peak GPU memory, and actual new calls. No inference deduplication in this bounded round: every logical prediction is a real call; the independent subset rerun bypasses all generation caches. Reuse validated embeddings/scores only, preserving vector-row IDs and content/model/preprocessing/runtime provenance. Report warm-cache and attributable cold preprocessing costs separately.

## Development choice and one confirmation
Within each tunable family choose the largest equal-dataset mean canonical F1, ties within 1e-12 broken by configuration ID. Keep all development outputs. Random/pure ablations inherit the selected Full parameters. Each retained backbone has 11 confirmation arms.
Continue a backbone only if selected Full minus the best of Dense20, MMR, coverage and k-means has development mean >=.005, neither dataset delta below -.005, and the fixed confirmation size can attain approximate 80% planning power for .01 F1 using 1.2 times the observed paired variances. Planning uses z=.995 quantile for a conservative five-test Bonferroni bound and z=.8 power: SE=sqrt(.25*(1.2*s_H^2/800+1.2*s_M^2/1200)); require .01/SE >= z(.995)+z(.8). This is a feasibility calculation, not proven power, and uses variance rather than the largest observed effect. If SE=0, do not assume power: require nonzero discordant outcomes, otherwise no evidence to advance.
Compact is evaluated first; only if its development gate passes is strong development undertaken. Failure to advance is insufficient support for further investment, not proof of universal ineffectiveness. Unexecuted strong comparisons are explicitly unexecuted. Confirmation size is fixed at 2,000, never increased based on its outcomes. No interim score inspection or optional stopping for significance.

## Statistics and decision
Use the pinned dataset-canonical answer functions already verified in revision2, including dataset-specific categorical, empty-answer and alias rules. No new scorer selection or legacy re-scoring.
For each retained backbone: five primary contrasts Full-Dense20, Full-MMR, Full-coverage, Full-kmeans and Full-Dense40. Use one joint Holm family over all retained-backbone primary contrasts (five or ten), alpha .05. Planning above uses five comparisons per backbone; if both advance, use z(.9975) instead and recompute feasibility before any confirmation predictions. All reported estimates retain equal dataset weights.
10,000 paired bootstrap resamples within dataset, PCG64 seed 20261002, common query indices across arms; report percentile 95% CI and centered-bootstrap one-sided p=(1+count(theta* - theta_hat >= theta_hat))/(10001) for H0 theta<=0. Degenerate paired distributions give p=1. This is an asymptotic independent-query approximation, not an exact arbitrary-dependence test; confidence intervals are not treated as exact test inversions. Independently reconstruct canonical query scores, means, contrasts, intervals, centered p, Holm and the decision. Summary+decision co-tampering must be detected.
Report shared source-document connected components derived from blind titles. Prespecified sensitivity resamples these components within dataset, retaining query-weighted means and paired methods; do not claim robust significance if intervals disagree or too few independent components remain. This does not remove unknown pretraining or source dependence.
Token-arm quality/cost and pure-component/random contrasts are supporting descriptive estimates with intervals, not a substitute primary endpoint. **No noninferiority or equal-quality efficiency claim is registered**, so a nonsignificant quality difference cannot establish an efficiency win.
A: primary compact and strong increment supported against their simple controls and larger list, consistent dataset directions and dependency sensitivity; discuss upgrade without promising acceptance. B: only a narrower supported contribution. C: completed new comparisons do not support upgrade. D: resource/integrity/eligibility prevents reliable completion. B/C/D stop algorithm expansion and trigger actual venue verification and manuscript/table revision with all adverse/unresolved evidence. No second model or confirmation search.

## Execution and stopping
Resource values and acceptance are in budget_manifest.json; long runs remain disabled while acceptance/provenance is pending. Engineering, synthetic tests and one small synthetic-only GPU cost example may proceed. Preserve immutable input/model/code identities once, not repeated whole-repository hashes. Commit/push protocol and implementation before new outcomes; allowed Git paths stay within this round plus a minimal current-state link.
Budget exhaustion stops at a safe completed-call boundary, preserves incomplete records, and gives D rather than a negative method result. A genuine runtime failure may be resumed with identical semantics and counts; no outcome-driven retries. No arbitrary per-process timeout. No paid services, full-wiki, new controller, restricted data, figure/plot-script edits or external submission.
