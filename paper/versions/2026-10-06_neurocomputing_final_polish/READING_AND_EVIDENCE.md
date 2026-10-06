# Reading and evidence scope

This task used the supplied final-polish specification, style-evidence review, targeted rewrites/figure brief, publication register, official-rules register, evidence anchors, and private author records. The three editing documents and registers were read completely. The actual conversion-v1 manuscript was read in full, with its six tables, three figures, supplementary navigation, case report, and relevant numeric inputs. The edited manuscript and final rendered pages were also reviewed in full.

The supplied **12-paper survey is inherited research**, not twelve fresh full-paper reads in this task. Its declared depth is six full-text-available targeted readings, five publisher partial-text readings, and one abstract-only reading. Availability is not equivalent to complete page-by-page reading. Only the supplied register's P10 had published-PDF visual inspection; it would be inaccurate to claim a visual survey of all twelve published layouts. The register's versions and limitations were used as stated. The pool informed problem-led organization and figure readability; no sentences, images, performance claims, or compulsory citations were copied.

## Evidence used in the edit

| Editorial point | Authoritative existing material | Check / treatment |
|---|---|---|
| H4 endpoints and all controls | `supplement/observations.csv`, `derived/QA_SUMMARY.csv` | Existing scores retained; displayed rows checked; no answer scoring |
| Joint support–answer association | `paired_numeric.csv`, `derived/PAIRED_TRANSITIONS.csv`, `derived/ENDPOINT_DECOMPOSITION.csv` | Counts and signed contributions reproduced with the original full-128 denominator |
| Feasible-reference gap | `reference_gaps.csv` | Existing aggregate only; missing per-query scores/sets remain missing |
| Selected-score display | `selected_scores.csv`, `derived/SELECTED_SCORE_BINS.csv` | Original fixed bins, counts, empty bins; no calibration or new intervals |
| Runtime scope | `index_cost_refined64.csv`, original738 timings, cost JSON files | Distinct scopes retained; means/medians shown without fabricated distributions |
| Data dependencies | `data_roles.csv`, `role_overlap.csv`, `DATA_AND_REPRODUCTION.md` | TUNE includes QA; only later DEV-SELECT excludes QA |
| Case interpretation | `CASE_ANALYSIS.md` and previous saved review | All 16 case observations retained; no new raw-data interpretation or rescoring |
| Current author declarations | User-supplied private metadata and declaration source | Confirmed fields incorporated locally; private source not published |

The supplied EVIDENCE_ANCHORS base commit agrees with the actual starting HEAD, `853bd08673a572376fc22ff3a549e8b1f5b808ff`. Its rounded anchors were cross-checked against existing numeric files rather than used as a substitute for full-precision records. No discrepancy requiring an experimental change was found. The eight displayed equations and bibliography source fields were preserved. Removed prose about negative-result publication precedent does not remove any experiment.

Journal-specific official pages remained inaccessible in the fresh check; the accessible general publisher AI policy and the unresolved boundaries are recorded in `SUBMISSION_FILE_MAP.md`. No claim of a new exhaustive literature review, independent scientific peer review, or full experimental reproduction is made.
