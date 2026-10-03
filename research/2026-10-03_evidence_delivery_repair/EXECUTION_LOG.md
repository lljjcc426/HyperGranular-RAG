# Actual execution record

This is a concise record assembled from completed command results and the process
telemetry, not a verbatim terminal transcript. Scientific commands below exited
successfully. The raw synthetic-test output is retained in TEST_OUTPUT.txt and
TEST_ADDITIONAL_OUTPUT.txt; machine-readable execution measurements are retained
in RESOURCE_LEDGER.jsonl and GENERATION_SUMMARY.json.

Working directory: E:/SCIENCE/HyperGranular-RAG. Interpreter:
temp/stage4e_env/Scripts/python.exe. Script paths are relative to
research/2026-10-03_evidence_delivery_repair/. PYTHONHASHSEED=0; numerical thread
settings and exact dependencies are bound in GENERATION_BINDING.json.

| Executed script | Actual outcome | CPU seconds | Wall seconds |
|---|---|---:|---:|
| prepare.py | 4,000 historical H0 rankings reproduced; fixed 400-query pilot prepared | 16.968750 | 17.217305 |
| verify_rankings.py | Independent real-query R1/R2 checks passed | 6.843750 | 7.032415 |
| delivery_details.py | Historical body/title/final/visible facet accounting completed | 3.437500 | 3.675550 |
| generate.py | 5,200 logical main predictions; 260 uncached reruns matched; zero failed calls | 602.703125 | 845.473423 |
| analyze.py | All 13 configurations scored; all fixed contrasts reported | 1.265625 | 1.328385 |
| verify_results.py | Complete grid, cache provenance, rerun equality and official-score aggregates passed | 0.203125 | 0.192522 |
| proxy_review.py | Aligned proxy-reference correction derived from existing rankings | 2.546875 | 2.550489 |

Initial synthetic suite: six tests passed before pilot execution. The added
title-only/duplicate-facet case increased the suite to seven passing tests; it
did not change the production selector. No generation was rerun for this test.

Two identical synthetic calibration calls preceded the pilot, within the bound
of four. They produced identical output. The 2,283 total actual model calls include
these two calls, 2,021 main calls and 260 uncached reruns. There were 3,179 logical
main cache hits, not additional model executions. No new embedding or reranker
calls were made.

The interpretation-stage proxy cross-tab correction is explained in
ENGINEERING_NOTES.md and PROXY_REFERENCE_CORRECTION.json. Scores, rankings,
predictions and bootstrap intervals did not change. Final manifest assembly is
bookkeeping; it is not a new scientific run. Prior document CPU remains unmetered,
and the above measured process CPU is not presented as a complete historical total.

The earlier quote error and Git TLS retry are recorded in ENGINEERING_NOTES.md.
They were not model, scoring or scientific-integrity failures. No locked data was
read and no historical artifact, manuscript or figure was changed by this round.
