# Stage4A 2Wiki Feasibility Pilot Report

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run
- Origin Date: 2026-07-11
- Verification Status: VERIFIED_BY_STAGE4A_OUTPUT_AUDIT
- Version Label: exp_result_v1
- Protocol: `docs/STAGE4A_PROTOCOL.md`, committed before data extraction and metrics
- Provenance status: PROVENANCE_DOWNGRADED
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

## Wilson Intervals

- q25 gain prevalence: 0.0200, 95% Wilson [0.0102, 0.0390].
- q25 harm prevalence: 0.0125, 95% Wilson [0.0054, 0.0289].
- q25 completion precision among 60 triggered baseline-incomplete queries: 0.1333.

## Bootstrap Boundary

- Paired bootstrap rows: 6; 10,000 resamples; seed 20260714.
- Intervals are descriptive pilot estimates; no p-values or confirmatory significance claims are made.

## Interpretation Boundary

- This pilot evaluates mapping, saturation, and gain-event availability only; it does not validate a controller.
- The reserved Stage4B slice was not embedded or evaluated.
- Results remain provenance-downgraded until reconciliation with the official archive.
- Stage3B remains locked and is not affected by this pilot.
