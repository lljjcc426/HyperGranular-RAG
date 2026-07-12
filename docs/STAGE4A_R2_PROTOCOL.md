# Stage4A-R2 Official 2Wiki Event-Rate Estimation Protocol

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Mode: plan
- Approval date: 2026-07-12
- Protocol Status: FROZEN_APPROVED_BEFORE_OFFICIAL_ROW_EXTRACTION
- Metrics Status: NOT COMPUTED
- Source extraction status: NOT STARTED
- Other conversations, thread tools, and memory files used: No

## Research Question

On fresh rows from the official April 7 2WikiMultiHopQA development archive, what are the query-level gain and harm prevalences of the frozen all-query q25 protected-insertion policy relative to dense fixed retrieval at CR@20, and is dense fixed retrieval saturated at that depth?

This stage estimates event availability on the official source. It does not fit or validate a controller, optimize the q25 threshold, revive the failed boundary-only rule, or open Stage3B.

## Design

- Study type: retrieval-only paired benchmark study
- Primary estimands: q25 gain prevalence and q25 harm prevalence per query
- Primary intervals: Wilson 95% confidence intervals
- Precision target: interval half-width at most `0.005` when prevalence is at most `0.03`
- Exact minimum at planning prevalence `0.03`: `4,497`
- Frozen development sample: `4,500`
- Question-type analyses: descriptive only
- Generator: none

The planning prevalence is a bounded sensitivity value, not an assumed official result. If an observed primary prevalence exceeds `0.03`, its actual interval width is reported and the precision target may fail without changing the sample or rerunning another fresh slice.

## Secondary Paired Analysis

- Endpoint: q25 minus dense-fixed CR@20
- Test: exact conditional two-sided McNemar
- Alpha: `0.05`
- Minimum planned net gain: `0.01`
- Planning total discordance: `0.05`
- Exact power at `n=4,500`: approximately `0.838`
- Paired bootstrap: 10,000 descriptive resamples, seed `20260712`

The McNemar analysis is secondary. Statistical significance cannot replace the gain/harm prevalence estimates or practical effect size.

## Source Of Truth

- Archive: author-released `data_ids_april7.zip`
- Archive SHA-256: `95DF2BF56FDABE034E27AEBC580E02264232203CF52552F9EFE8A919E5529EEF`
- `dev.json` SHA-256: `79F77AE104088EA8E25B1A65DBECE768D45771194663BC5660EC9A98070DADF5`
- Official dev rows: `12,576`
- Repository license: Apache-2.0
- Mirror content: prohibited for Stage4A-R2 data, embeddings, and metrics

## Frozen Data Boundary

| Role | Official dev rows | Queries | Access rule |
|---|---:|---:|---|
| Excluded prior material | `[0:800)` | 800 | Never used in Stage4A-R2 metrics |
| Stage4A-R2 development estimation | `[800:5300)` | 4,500 | Extract only after this protocol and execution code are committed |
| Future independent reservation | `[5300:9800)` | 4,500 | IDs and digest only; no content file, embeddings, retrieval, or outcomes |
| Unused remainder | `[9800:12576)` | 2,776 | Do not access for Stage4A-R2 |

The extractor must write only normalized development rows. Reservation questions, answers, contexts, evidence, types, embeddings, and metrics must not be persisted. Development and reservation IDs must be unique and disjoint.

## Frozen Mapping

- One non-empty official context sentence becomes one candidate unit.
- Unit identity is `(query_id, context_title, sentence_index)`.
- Gold units are mapped only from official `supporting_facts` title and sentence index.
- All selected development rows are retained.
- Every supporting fact must map; any missing-gold query is a hard failure.
- Gold labels and `evidences` are forbidden from embedding, ball construction, edge construction, candidate filtering, ranking, and insertion decisions.

## Frozen Retrieval Configuration

- Dense model: `sentence-transformers/all-MiniLM-L6-v2`
- Maximum sequence length: 192
- Evaluation depth: 20
- Granular-ball and facet parameters: unchanged from Stage2F-G and archived Stage4A
- Candidate threshold: frozen q25 floor `0.1957079917192459`
- Protection zone: dense Top-10
- Insertion budget: at most 4 units into ranks 11-20
- Boundary suppression: disabled because Stage2G did not validate it

Strategies:

| Strategy | Score floor | Protect | Insert | Role |
|---|---:|---:|---:|---|
| `dense_fixed` | none | 0 | 0 | Saturation baseline |
| `allquery_unfiltered_p10_i4` | none | 10 | 4 | Candidate-availability control |
| `allquery_q25_p10_i4` | 0.1957079917 | 10 | 4 | Frozen transferred policy |

## Outcomes

Primary:

- q25 gain events: dense CR@20 changes from 0 to 1
- q25 harm events: dense CR@20 changes from 1 to 0
- gain and harm prevalence with Wilson 95% intervals and observed half-widths

Secondary:

- Dense, unfiltered, and q25 ER@20 and CR@20
- q25 net completed-chain change
- Trigger rate, completion opportunities, completion precision
- Inserted units, insert yield, conditional false-insert rate
- Exact McNemar p-value for q25 versus dense CR@20
- Descriptive paired-bootstrap intervals for ER@20 and CR@20

## Completion Rules

Stage4A-R2 is `ESTIMATION_COMPLETE` only if:

1. official archive and `dev.json` hashes match the frozen values;
2. exactly 4,500 unique development IDs and 4,500 unique reservation IDs are present with zero overlap;
3. no reservation content or metric is written;
4. supporting-fact mapping rate is 1.0 and no query lacks mapped gold;
5. q25 gain and harm Wilson interval half-widths are each at most `0.005`.

If condition 5 fails because prevalence exceeds the planning range, report `ESTIMATION_PRECISION_NOT_MET`; do not add rows, tune the policy, or inspect the reservation. This stage never directly authorizes controller fitting. Any next controller study requires a new model-specific protocol using the observed official event rates.

## Expected Outputs

Tracked:

- `docs/STAGE4A_R2_SAMPLE_SIZE_PLAN.json`
- `docs/STAGE4A_R2_SOURCE_AUDIT.json`
- `results/stage4a_r2_query_audit.csv`
- `results/stage4a_r2_strategy_summary.csv`
- `results/stage4a_r2_bootstrap.csv`
- `results/stage4a_r2_inference.json`
- `results/stage4a_r2_verification.json`
- `reports/超粒球RAG_Stage4A_R2官方事件率估计报告.md`

Local untracked:

- normalized official development JSON
- units and queries JSONL
- MiniLM embedding cache
- corpus mapping report

## Monitoring And Stop Rules

- Extraction timeout: 15 minutes
- Corpus construction timeout: 15 minutes
- Embedding and retrieval timeout: 120 minutes
- Hard failures: source hash mismatch, ZIP CRC failure, row-boundary mismatch, duplicate or overlapping IDs, persisted reservation content, mapping loss, embedding mismatch, q25 drift, unexpected output schema, or non-zero exit code
- No automatic threshold change or rerun after outcome inspection
- Stage3B remains locked
