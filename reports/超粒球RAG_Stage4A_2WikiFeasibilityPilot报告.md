# Stage4A 2Wiki Feasibility Pilot Report

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run
- Origin Date: 2026-07-11
- Verification Status: VERIFIED_INTERNAL_METRICS; OFFICIAL_SOURCE_MISMATCH
- Version Label: exp_result_v1
- Protocol: `docs/STAGE4A_PROTOCOL.md`, committed before data extraction and metrics
- Provenance status: OFFICIAL_MISMATCH_DETECTED
- Gold labels used for indexing, ranking, score filtering, expansion, or threshold selection: No
- Controller fitting: No
- Generator used: No

## Run Record

- Duration: 88.96 seconds
- Exit Code: 0
- Queries / units / gold units: 400 / 12721 / 982
- Pilot ID SHA256: `6E00E3FA59C930DB1ABDA099A90A919A0FA4C1F6C8FA816812ABFD51FC9CA2F4`
- Frozen q25 floor: 0.1957079917192459
- Embedding model / max length: `sentence-transformers/all-MiniLM-L6-v2` / 192

## Outputs

| File | Bytes |
|---|---:|
| `results\stage4a_2wiki_query_audit.csv` | 76532 |
| `results\stage4a_2wiki_strategy_summary.csv` | 4485 |
| `results\stage4a_2wiki_bootstrap.csv` | 1116 |

## Overall Results

| Strategy | ER@20 | CR@20 | Trigger | Avg insert | Gain | Harm | Net | Removed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| dense_fixed | 0.8831 | 0.7450 | 0.0000 | 0.0000 | 0 | 0 | 0 | 0 |
| allquery_unfiltered_p10_i4 | 0.8890 | 0.7475 | 0.5450 | 1.7450 | 9 | 8 | 1 | 0 |
| allquery_q25_p10_i4 | 0.8902 | 0.7525 | 0.5050 | 1.3750 | 8 | 5 | 3 | 213 |

## Promotion Gate

| Condition | Result |
|---|---|
| Mapping >= 0.99 and zero missing gold | PASS |
| Dense CR@20 < 0.95 | PASS |
| q25 trigger rate >= 0.10 | PASS |
| q25 gain events >= 10 | FAIL |
| q25 net completed-chain change > 0 | PASS |
| q25 score floor removes candidates | PASS |

- Overall Stage4B development-branch decision: STOP.

This is the procedural decision for the pinned mirror pilot. The post-hoc design audit found that 400 was not supported by a power or event-count analysis, so this decision must not be interpreted as evidence that the research direction is infeasible.

- Scientific feasibility conclusion: `INCONCLUSIVE_PENDING_STAGE4R`.
- Research-direction status: OPEN.

## Wilson Intervals

- q25 gain prevalence: 0.0200, 95% Wilson [0.0102, 0.0390].
- q25 harm prevalence: 0.0125, 95% Wilson [0.0054, 0.0289].
- q25 completion precision among 60 triggered baseline-incomplete queries: 0.1333.

## Bootstrap Boundary

- Paired bootstrap rows: 6; 10,000 resamples; seed 20260714.
- Intervals are descriptive pilot estimates; no p-values or confirmatory significance claims are made.

## Post-run Official Archive Reconciliation

- Official archive SHA-256: `95DF2BF56FDABE034E27AEBC580E02264232203CF52552F9EFE8A919E5529EEF`.
- Pilot IDs, questions, answers, types, evidences, and supporting facts match the official April 7 archive.
- Context order changed for 393/400 queries; after order normalization, 7/400 still have content differences.
- Gold-evidence text differs for 5/400 queries.
- Candidate-unit count is 12,718 in the official archive versus 12,721 in the mirror pilot.
- Therefore, all metrics in this report are mirror-specific and are not official April 7 retrieval results.
- No retrieval metric was recomputed during reconciliation.
- Full audit: `docs/STAGE4A_OFFICIAL_RECONCILIATION.json`; design correction: `docs/STAGE4A_DESIGN_AUDIT.md`.

## Interpretation Boundary

- This pilot evaluates mapping, saturation, and gain-event availability only; it does not validate a controller.
- The reserved Stage4B slice was not embedded or evaluated.
- Official reconciliation detected retrieval-content mismatches; the result is not eligible as paper-grade external evidence.
- Stage3B remains locked and is not affected by this pilot.
