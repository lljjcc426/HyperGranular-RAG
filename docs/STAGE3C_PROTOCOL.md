# Stage3C Target-Feasibility And Data-Strategy Audit Protocol

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent + deep-research
- Origin Mode: plan + fact-check
- Origin Date: 2026-07-11
- Verification Status: UNVERIFIED
- Version Label: code_plan_v1
- Analysis Status: EXPLORATORY FEASIBILITY AUDIT
- Protocol Status: FROZEN BEFORE COMBINED EVENT AUDIT

## Experiment Overview

- **Title**: Feasibility audit for gain, harm, and dataset targets in HyperGranular-RAG
- **Objective**: Determine whether the failed Stage3A harm head reflects insufficient sample size, a saturated dataset, or a structurally rare event under protect-10 insertion, and choose the scientifically supportable scope for the next controller branch.
- **Type**: retrospective analysis plus source-verified dataset screening
- **Stage3B status**: locked; no embeddings, retrieval scores, or outcome labels may be computed

Stage3C does not fit a controller or select a threshold. All internal labels have already been observed, so every numerical finding is diagnostic rather than confirmatory.

## Internal Inputs

| Input | Queries | Role |
|---|---:|---|
| `results/stage2h_boundary_query_audit.csv` | 1,200 | Stage2E-G all-query q25/protect-10/insert-4 counterfactual |
| `results/stage3a_utility_controller_query_audit.csv` | 800 | Stage3A fitting and threshold-selection counterfactual |
| `results/stage3a_utility_controller_model.json` | 800 | Fallback and predictive-event audit |

The two query-audit files must have zero query-ID overlap. Stage3C must not read any row from the reserved `[1000:1400)` Stage3B range except the already committed ID digest in `docs/STAGE3_DATA_RESERVATION.json`.

## Unified Event Definitions

All internal rows use the same frozen retrieval counterfactual: q25 candidate floor `0.1957079917192459`, protect dense Top-10, insert at most 4 units, evaluate at Top-20.

- Gain event: all-query expansion changes CR@20 from 0 to 1.
- Harm event: all-query expansion changes CR@20 from 1 to 0.
- Triggered query: at least one candidate unit is inserted.
- Completion opportunity: triggered query with dense-fixed CR@20 = 0.
- Harm opportunity: triggered query with dense-fixed CR@20 = 1.
- Saturated scope: dense-fixed CR@20 at least `0.95`.

## Internal Analysis

Report rows for every observed slice or partition, each dataset within that scope, dataset-pooled totals, and the full 2,000-query audit:

- Query and trigger counts
- Dense-fixed and all-query CR@20
- Completion-opportunity, gain-event, harm-opportunity, and harm-event counts
- Gain prevalence per query and completion precision per opportunity
- Harm prevalence per query and harm rate per opportunity
- Inserted units, non-gold insertions per query, and conditional false-insert rate
- Wilson 95% confidence intervals for gain and harm prevalence
- Descriptive projected query counts needed to observe 20 and 50 events at the pooled point prevalence; report `NA` when the observed prevalence is zero

No p-values, threshold search, model refit, or multiple-comparison claim is allowed.

## Scope-Feasibility Rules

Apply the following rules to the full observed audit and separately to each dataset:

1. **Risk-aware expected utility is event-feasible** only if there are at least 20 gain events and 20 harm events overall, with at least 5 harm events in two disjoint observed partitions.
2. **Budget-aware gain selection is event-feasible** if there are at least 20 gain events overall but the harm criterion above fails.
3. **Current controller learning is event-infeasible** if there are fewer than 20 gain events overall.
4. A dataset with dense-fixed CR@20 at least 0.95 is marked saturated for Top-20 chain-completion development even if it remains useful for other endpoints.

These are planning rules, not universal machine-learning sample-size laws.

## External Dataset Screening

Predeclared candidates:

1. HotpotQA train
2. MuSiQue train
3. 2WikiMultiHopQA
4. IIRC
5. HoVer

Only primary or authoritative sources are admissible: the dataset paper, official project page, official repository, or official dataset card maintained by the dataset authors or host organization.

Scoring rubric, maximum 10 points:

| Criterion | Points | Evidence requirement |
|---|---:|---|
| Explicit gold supporting evidence | 3 | Sentence/paragraph/document evidence labels described by an authoritative source |
| Candidate contexts or reconstructable retrieval corpus | 2 | Distractors, linked documents, or an official corpus mapping |
| Genuine multi-hop reasoning design | 2 | Dataset construction explicitly targets multiple supporting facts or documents |
| At least 10,000 training/development examples | 1 | Authoritative count |
| QA task alignment | 1 | Answer generation or extractive QA rather than only verification/classification |
| Stable public access and stated terms | 1 | Working official access path and license/terms evidence |

Unknown items score zero and remain `UNVERIFIED`; no point may be inferred from third-party summaries. Retrieval saturation under the current MiniLM pipeline cannot be established from documentation and must be marked `PILOT_REQUIRED`.

## Dataset Recommendation Rule

- Recommend a new pilot only for candidates scoring at least 7/10 with explicit gold evidence and usable candidate contexts.
- Prefer a candidate independent of HotpotQA/MuSiQue when scores are tied.
- Existing local data may be recommended for event expansion, but cannot establish cross-dataset generalization.
- No dataset download or pilot run occurs in Stage3C.

## Expected Outputs

| Output | Path | Format | Success Criterion |
|---|---|---|---|
| Event feasibility summary | `results/stage3c_event_feasibility_summary.csv` | CSV | All slices/partitions, datasets, pooled rows, and Wilson intervals |
| Feasibility decision | `results/stage3c_target_feasibility_decision.json` | JSON | Frozen rules applied with event counts and scope decision |
| Dataset screen | `docs/STAGE3C_DATASET_SCREEN.md` | Markdown | Source-linked rubric for all five candidates |
| Audit report | `reports/超粒球RAG_Stage3C_TargetFeasibilityAudit报告.md` | Markdown | Internal findings, external synthesis, limitations, and next-scope decision |

## Monitoring Configuration

- Timeout: 10 minutes for internal audit and 30 minutes for source verification
- Hard failures: Stage2H/Stage3A query overlap, unexpected row counts, inconsistent event definitions, malformed source citation, use of non-authoritative evidence for scoring, or any Stage3B metric access
- Reproducibility: deterministic internal outputs must match byte-for-byte on rerun

## Interpretation Boundary

Stage3C can decide whether the next research branch should target risk-aware utility, budget-aware gain selection, or no controller. It can nominate a dataset for a future pilot. It cannot validate retrieval improvement, estimate performance on Stage3B, or claim that documentation alone guarantees a non-saturated benchmark.
