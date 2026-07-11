# Stage4R Official-Source Feasibility Repair Protocol

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Mode: plan
- Date: 2026-07-11
- Protocol Status: DRAFT_AWAITING_USER_APPROVAL
- Metrics Status: NOT COMPUTED
- Source extraction status: NOT STARTED
- Other conversations, thread tools, and memory files used: No

## Study Identity

- **Name**: Stage4R official-source and event-count design repair
- **Objective**: Re-estimate official 2Wiki dense saturation and frozen q25 protected-insertion gain availability after correcting the Stage4A source and sample-size defects.
- **Type**: independent retrieval-only feasibility study
- **Controller fitting**: prohibited
- **Stage3B status**: locked and unrelated

Stage4R is not a rerun of Stage4A and is not the stopped Stage4B branch. It uses fresh official rows and a sample size fixed from explicit event-count operating characteristics.

## Source of Truth

- Archive: author-released `data_ids_april7.zip`
- Archive SHA-256: `95DF2BF56FDABE034E27AEBC580E02264232203CF52552F9EFE8A919E5529EEF`
- `dev.json` SHA-256: `79F77AE104088EA8E25B1A65DBECE768D45771194663BC5660EC9A98070DADF5`
- Official `dev.json` rows: 12,576
- License: Apache-2.0 repository license
- Mirror data: prohibited for Stage4R extraction, embeddings, and metrics

## Sample-size Design

Primary planning endpoint: observe at least 20 q25 gain events, matching the Stage3C budget-aware selector event-feasibility threshold.

Frozen assumptions proposed for approval:

- Minimum scientifically relevant gain prevalence: 0.0100
- Target probability of observing at least 20 gains when prevalence is at least 0.0100: 0.95
- Model: exact binomial event count
- Exact minimum sample size: 2,784
- Rounded development sample size: 2,800
- Achieved probability at `n=2,800`: 0.9530
- Expected gains at prevalence 0.0100: 28

The 0.0100 prevalence is rounded below the Stage4A mirror Wilson lower bound of 0.0102. This is a conservative planning assumption, not an official-data effect claim.

## Proposed Data Boundary

| Role | Official dev rows | Queries | Access rule |
|---|---:|---:|---|
| Excluded prior material | `[0:800)` | 800 | Never used in Stage4R metrics |
| Stage4R development feasibility | `[800:3600)` | 2,800 | Extract only after protocol approval and commit |
| Future reservation | `[3600:6400)` | 2,800 | IDs/digest only; no embeddings or retrieval metrics |
| Unused remainder | `[6400:12576)` | 6,176 | No Stage4R access |

Contiguous rows are proposed because the official archive has no documented random ordering guarantee that would justify stratified reshuffling without inspecting labels. Question-type distribution will be reported descriptively after extraction and will not alter the sample.

## Frozen Retrieval Configuration

- Dense model: `sentence-transformers/all-MiniLM-L6-v2`
- Maximum sequence length: 192
- Evaluation depth: 20
- Granular-ball and hyperedge parameters: identical to Stage3A/Stage4A
- Candidate score floor: `0.1957079917192459`
- Protection zone: dense Top-10
- Insertion budget: 4 units into ranks 11-20
- Boundary suppression: disabled

The q25 floor is transferred as a fixed independently tested policy from Stage2F. It is not claimed to be optimal for 2Wiki and must not be tuned on Stage4R labels.

Frozen strategies:

| Strategy | Score floor | Protect | Insert | Role |
|---|---:|---:|---:|---|
| `dense_fixed` | none | 0 | 0 | Official saturation baseline |
| `allquery_unfiltered_p10_i4` | none | 10 | 4 | Candidate-availability control |
| `allquery_q25_p10_i4` | 0.1957079917 | 10 | 4 | Transferred frozen policy |

## Metrics

- ER@20 and CR@20 for all three strategies
- Trigger rate and inserted-unit counts
- Gain events: dense CR@20 0 to strategy CR@20 1
- Harm events: dense CR@20 1 to strategy CR@20 0
- Net completed-chain change
- Gain and harm prevalence with Wilson 95% intervals
- Completion precision among triggered baseline-incomplete queries
- Question-type descriptive breakdown
- 10,000 paired bootstrap resamples for ER@20 and CR@20 deltas, seed `20260715`

All intervals are descriptive feasibility estimates. No p-value or confirmatory treatment-effect claim is permitted.

## Proposed Decision Rules

Stage4R supports a separately designed selector-development study only if all conditions hold:

1. Official supporting-fact mapping rate is at least 0.99 and zero queries have missing mapped gold.
2. Dense-fixed CR@20 is below 0.95.
3. q25 triggers at least 10% of queries.
4. q25 produces at least 20 gain events.
5. q25 net completed-chain change is positive.
6. The q25 floor removes at least one expansion candidate.

Failure has bounded interpretation:

- Fewer than 20 gains means the data do not support selector-development feasibility under this frozen policy and the assumed 1% minimum prevalence design.
- It does not prove that HyperGranular RAG, other thresholds, or other retrieval policies are universally infeasible.
- No threshold may be modified and rerun on the same 2,800 labels.

## Required Outputs After Approval

- Official extraction audit and query-ID digests
- Local official unified JSON, units, queries, and embeddings
- Query-level audit CSV
- Strategy and question-type summary CSV
- Paired bootstrap CSV
- Independent verification JSON
- Stage4R report with explicit provenance and bounded decision

## Approval Gate

No extraction, embedding, or retrieval command may run until the user explicitly approves:

`n=2,800; official rows [800:3600); reserve [3600:6400); 20 gains; p_min=0.01; target probability=0.95.`
