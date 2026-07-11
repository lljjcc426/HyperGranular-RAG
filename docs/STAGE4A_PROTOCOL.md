# Stage4A 2WikiMultiHopQA Feasibility Pilot Protocol

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent + deep-research + huggingface-datasets
- Origin Mode: plan + source verification
- Origin Date: 2026-07-11
- Verification Status: UNVERIFIED
- Version Label: code_plan_v1
- Protocol Status: FROZEN BEFORE PILOT RETRIEVAL METRICS
- Analysis Status: DEVELOPMENT FEASIBILITY PILOT

## Experiment Overview

- **Title**: Independent 2WikiMultiHopQA mapping, saturation, and gain-event feasibility pilot
- **Objective**: Determine whether 2WikiMultiHopQA can be mapped into the granular-ball retrieval schema without evidence loss, whether dense-fixed CR@20 is non-saturated, and whether frozen protected insertion produces enough gain events to justify a later budget-aware selector branch.
- **Type**: dataset conversion and retrieval-only pilot
- **Model fitting**: prohibited
- **Stage3B status**: locked and unrelated to this pilot

Stage4A is not a controller test and cannot validate cross-dataset generalization. It only decides whether a larger, separately frozen 2Wiki branch is worth developing.

## Source And Provenance Audit

Authoritative upstream:

- Paper: Ho et al., COLING 2020, `10.18653/v1/2020.coling-main.580`
- Official repository: `https://github.com/Alab-NII/2wikimultihop`
- Frozen official repository commit: `13800e5be57df1b4040b9b1588c6c811779e69e9`
- Repository license: Apache License 2.0
- Official corrected archive in README: `data_ids_april7.zip` on Dropbox

Environment limitation:

- The official Dropbox host was reachable through web metadata inspection but direct HTTPS download from the experiment shell timed out on 2026-07-11.
- No official archive checksum is published in the repository README.

Pinned mirror used only for this pilot:

- Hugging Face dataset: `framolfese/2WikiMultihopQA`
- Frozen mirror commit: `fe713bfbd1afbca1a65246741a75890405d56a3a`
- Mirror statement: schema-only repackaging of original data with questions, answers, and contexts unaltered
- Dataset Viewer size: 192,606 rows; validation split: 12,576 rows
- Mirror validation parquet object ID: `5db5d6e1162d08d05f2d2a72aa0d9736b70dd1c6`

The mirror is not author-maintained. Stage4A therefore carries `PROVENANCE_DOWNGRADED` status. A later paper-grade experiment must reconcile the mirror against the official archive by query ID and content hash once the archive is obtainable.

## Frozen Data Boundary

Use the mirror validation split in repository order:

| Role | Rows | Queries | Metric access |
|---|---|---:|---|
| Stage4A pilot | `[0:400)` | 400 | Allowed after protocol and code are committed |
| Stage4B reservation | `[400:800)` | 400 | Query IDs only; no embeddings or retrieval metrics |
| Unused validation remainder | `[800:12576)` | 11,776 | No access in Stage4A |

The Dataset Viewer API returns complete row objects. The extraction script may receive rows `[400:800)` to compute the reservation ID digest, but must discard question, answer, context, evidence, and type fields immediately and must not write them to disk.

Required integrity checks:

- Mirror repository SHA is unchanged before and after extraction.
- Pilot and reservation each contain 400 unique IDs with zero overlap.
- The raw API payload for each 100-row page is hashed and recorded.
- Only the 400 pilot records are stored locally.

## Mapping Procedure

Mirror fields are mapped as follows:

| 2Wiki field | Unified field |
|---|---|
| `id` | `id`; query ID becomes `2wikimultihopqa::<id>` |
| `question` | `question` |
| `answer` | `answer` |
| `context.title` + `context.sentences` | ordered candidate contexts and sentence units |
| `supporting_facts.title` + `supporting_facts.sent_id` | gold evidence units |
| `type` | metadata question type |
| `evidences` | metadata reasoning path; not used for retrieval ranking |

Mapping diagnostics:

- Missing or duplicate query IDs
- Mismatched context title/sentence arrays
- Supporting-fact title absent from context
- Supporting-fact sentence index out of range
- Duplicate supporting-fact references
- Queries with zero mapped gold evidence
- Supporting-fact mapping rate

Gold evidence and `evidences` must not affect embedding, indexing, candidate construction, ranking, score filtering, or expansion decisions.

## Frozen Retrieval Configuration

- Dense model: `sentence-transformers/all-MiniLM-L6-v2`
- Maximum sequence length: 192
- Maximum evaluation depth: 20
- Granular-ball and hyperedge parameters: identical to Stage3A
- Transferred candidate score floor: Stage2E q25 = `0.1957079917192459`
- Protection zone: dense Top-10
- Insertion budget: 4 units into ranks 11-20
- Boundary suppression: disabled; expansion candidates are constructed for every query

Frozen strategies:

| Strategy | Score floor | Protect | Insert | Role |
|---|---:|---:|---:|---|
| `dense_fixed` | none | 0 | 0 | Saturation baseline |
| `allquery_unfiltered_p10_i4` | none | 10 | 4 | Candidate-availability control |
| `allquery_q25_p10_i4` | 0.1957079917 | 10 | 4 | Transferred protected-insertion pilot |

No threshold may be estimated from Stage4A labels.

## Pilot Metrics

- ER@20 and CR@20 for all three strategies
- Dense baseline saturation status
- Trigger rate, average inserted units, insertion yield, and conditional false-insert rate
- Gain events: dense CR@20 0 to strategy CR@20 1
- Harm events: dense CR@20 1 to strategy CR@20 0
- Net completed-chain change
- Gain prevalence per query and completion precision among triggered baseline-incomplete queries
- Question-type breakdown for mapping, saturation, and gain counts
- Wilson 95% intervals for gain and harm prevalence
- 10,000 dataset-level paired bootstrap resamples for ER@20 and CR@20 deltas, seed `20260714`

All intervals are descriptive pilot estimates. No p-values or confirmatory significance language is allowed.

## Promotion Gate

Stage4A supports a later, newly frozen Stage4B development branch only if all conditions hold:

1. Supporting-fact mapping rate is at least 0.99 and zero queries have missing mapped gold.
2. Dense-fixed CR@20 is below 0.95.
3. `allquery_q25_p10_i4` triggers at least 10% of pilot queries.
4. `allquery_q25_p10_i4` produces at least 10 gain events.
5. Its net completed-chain change is positive.
6. The q25 strategy does not fall back to unfiltered behavior: at least one candidate is removed by the score floor.

Failure of any condition stops the 2Wiki budget-aware selector branch. Stage4A labels must not be used to modify the transferred q25 floor and rerun the same pilot.

## Expected Outputs

| Output | Path | Format | Success Criterion |
|---|---|---|---|
| Source audit | `docs/STAGE4A_SOURCE_AUDIT.json` | JSON | Official/mirror SHAs, page hashes, split counts, and provenance status |
| Pilot unified data | Local processed-data directory | JSON | Exactly 400 pilot records only |
| Pilot units and queries | Local processed-data directory | JSONL | 400 queries, zero missing gold |
| Pilot embeddings | Local processed-data directory | NPZ | Cache dimensions match corpus |
| Query audit | `results/stage4a_2wiki_query_audit.csv` | CSV | 400 rows with mapping and frozen-strategy outcomes |
| Strategy summary | `results/stage4a_2wiki_strategy_summary.csv` | CSV | ALL and question-type rows for three strategies |
| Bootstrap audit | `results/stage4a_2wiki_bootstrap.csv` | CSV | Frozen q25/unfiltered comparisons with 10,000-resample CIs |
| Run report | `reports/超粒球RAG_Stage4A_2WikiFeasibilityPilot报告.md` | Markdown | Provenance, mapping, metrics, gate decision, and limitations |

## Monitoring Configuration

- Timeout: 10 minutes for API extraction/conversion and 60 minutes for embedding/retrieval analysis
- Monitor only declared Stage4A local and tracked outputs
- Hard failures: mirror SHA drift, API page truncation, ID overlap, unexpected row count, any saved reservation content beyond IDs/digest, mapping loss below the hard zero-missing-gold requirement, embedding mismatch, q25 mismatch, or non-zero exit code

## Interpretation Boundary

Stage4A may establish technical and event feasibility for a future 2Wiki development branch. It cannot validate a controller, use the reserved 400-query slice, support a Stage3B claim, or serve as paper-grade external evidence until official-archive reconciliation is complete.
