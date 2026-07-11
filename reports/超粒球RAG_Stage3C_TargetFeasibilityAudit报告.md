# Stage3C Target-Feasibility Audit Report

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run
- Origin Date: 2026-07-11
- Verification Status: UNVERIFIED
- Version Label: exp_result_v1
- Analysis Status: EXPLORATORY RETROSPECTIVE FEASIBILITY AUDIT
- Protocol: `docs/STAGE3C_PROTOCOL.md`
- Stage3B metrics read: No

## Input Audit

- Stage2H/Stage3A rows: 1200/800
- Total observed queries: 2000
- Query-ID overlap: 0
- Stage3B action: KEEP_LOCKED

## Pooled Event Audit

| Scope | Queries | Dense CR@20 | Gain events | Gain prevalence | Harm events | Harm prevalence | Saturated |
|---|---:|---:|---:|---:|---:|---:|---:|
| ALL | 2000 | 0.8670 | 69 | 0.0345 | 8 | 0.0040 | 0 |
| hotpotqa | 1000 | 0.7340 | 69 | 0.0690 | 8 | 0.0080 | 0 |
| musique | 1000 | 1.0000 | 0 | 0.0000 | 0 | 0.0000 | 1 |

## Feasibility Decision

- ALL: `BUDGET_AWARE_GAIN_SELECTION_EVENT_FEASIBLE` (69 gains, 8 harms).
- hotpotqa: `BUDGET_AWARE_GAIN_SELECTION_EVENT_FEASIBLE` (69 gains, 8 harms).
- musique: `CURRENT_CONTROLLER_LEARNING_EVENT_INFEASIBLE` (0 gains, 0 harms).

## External Dataset Screen

The source-verified rubric is recorded in `docs/STAGE3C_DATASET_SCREEN.md`.

| Candidate | Score | Decision |
|---|---:|---|
| HotpotQA train | 10/10 | Same-domain event expansion only |
| MuSiQue train | 10/10 | Not justified for unchanged CR@20 because observed dev is saturated |
| 2WikiMultiHopQA | 10/10 | Primary independent pilot candidate |
| IIRC | 9/10 | Secondary candidate; official access/terms require remediation |
| HoVer | 9/10 | Retrieval-robustness candidate with a fact-verification task shift |

Documentation scores do not establish retrieval difficulty. A future 2Wiki pilot must freeze its slice and endpoint before computing MiniLM metrics.

## Scope Decision

- Retire the current risk-aware expected-utility target: 8 observed harms are insufficient and no two partitions contain at least 5 harms.
- Preserve budget-aware gain selection as the supported development scope: 69 observed gains exceed the frozen event threshold.
- Use 2WikiMultiHopQA for the first independent feasibility pilot; HotpotQA train may increase same-domain event count but cannot establish external validity.
- Keep Stage3B locked because the Stage3A branch did not pass promotion.

## Interpretation Boundary

This report diagnoses event availability in already observed data. It does not validate a controller, does not estimate Stage3B performance, and does not make a confirmatory cross-dataset claim.
