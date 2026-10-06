# Supplementary method and cost notes

These notes relocate existing details from the first Neurocomputing draft. They introduce no new observations, inference, scores, or tests. All numeric files retain their prior contents.

## Preference availability

MINE contains 256 HotpotQA and 256 MuSiQue FIT questions. The primary-seed shared pool does not supply every preference category for every question; missing categories are masked, while base supervision remains available.

| Category / round | HotpotQA unavailable / 256 | MuSiQue unavailable / 256 |
|---|---:|---:|
| Final pair, round 1 | 171 | 115 |
| Frontier pair, round 1 | 17 | 42 |
| Final pair, round 2 | 196 | 135 |
| Frontier pair, round 2 | 19 | 59 |

These counts are the existing primary-seed reports, not an estimate pooled across seeds. Checkpoints were compared at epochs 2, 4, and 8; all selected aligned models came from round 1. The static third seed is not a continuation replicate.

## Historical measured cost ledger

Source: unchanged `cost_static.json` and `cost_aligned.json`. These totals include their original broader development, sensitivity and repeat work, not just the 128-question answer table.

| Recorded quantity | Static study | Continuation study |
|---|---:|---:|
| Model-residency GPU process wall seconds | 4,350.28 | 4,513.07 |
| Measured CPU process seconds | 10,541.75 | 7,035.50 |
| New reader calls | 2,287 | 986 |
| Logical answer rows | 3,520 | 1,536 |
| Cache hits | 1,241 | 558 |
| Measured generation seconds | 2,532.22 | 867.94 |
| Peak allocated GPU memory, GiB | 6.63 | 6.11 |

Each study includes eight reader reruns bypassing inference reuse; new calls plus cache hits exceed logical rows by eight. Cache reuse is neither independent generation nor evidence of deployment acceleration. Dividing these totals by 128 would not estimate a serving cost. Earlier unrecorded CPU time is unknown. Static replay matches optimizer-update count, not the extra evaluations of the aligned preference losses.

The selector comparison in the manuscript instead uses `index_cost_refined64.csv`: 32 fixed questions per dataset, with means and medians. Its per-question timing distribution was not retained. `index_cost_original738.csv` belongs to a separate original 738-question index check. Tokenizer time is nested within total selector time and must not be added again. Some CPU timing overlapped reader execution.

## Missing reference records

`reference_gaps.csv` retains the existing two-row aggregate Dense-K6 diagnostic. Per-question Dense-K6 logits and selected sets, and paired MMR-K6 scores, were not saved. No model was loaded to replace them, and no paired score-gap distribution was constructed.

## Editorial and data role

The second Neurocomputing edit changes prose, table presentation, and plots from existing numbers only. No answer was rescored, no prediction was regenerated, and no new bootstrap or hypothesis test was performed. All questions remain in their existing denominators. Sixteen distinct outcome-stratified cases are illustrative, not a frequency estimate or independent expert adjudication.
