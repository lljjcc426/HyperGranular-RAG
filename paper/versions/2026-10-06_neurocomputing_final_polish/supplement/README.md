# Numerical reproduction for the Neurocomputing author-review manuscript

Final-polish v2: numeric inputs and derived tables are unchanged from conversion v1. See `SUPPLEMENTARY_METHOD_NOTES.md` for the relocated preference-availability and historical cost details. The six manuscript tables and three figures present these existing numbers; no new experiment or answer scoring was performed.

Scope: POST_HOC_DESCRIPTIVE_ANALYSIS_OF_EXISTING_RUNS. Python 3 standard library; no models, answer rescoring, original text, network, or new inferential test.

Run `python reconstruct.py` in this directory. Outputs go to `derived/`:

- `QA_SUMMARY.csv`: saved canonical outcomes, all 128 questions per method/seed.
- `PAIRED_TRANSITIONS.csv`: complete 4×3 tables per dataset/model/seed plus equal64+64 panels.
- `ENDPOINT_DECOMPOSITION.csv`: all four support transitions, group means/sums and sum divided by full panel N.
- `SELECTED_SCORE_BINS.csv`: fixed sigmoid bins from saved static logits, empty bins included.
- `CHECK.json`: actual reconstruction status and measured CPU.

There are 2,688 numeric method/seed records and 1,024 static/aligned pairs, all reusing 128 distinct question identities. These exposed development questions are not independent confirmation samples; source overlap is recorded separately. Dense/MMR repeats across seed are the same deterministic baseline outputs, not independent inference. No row is a newly answered question.

`reference_gaps.csv` contains two retained aggregate diagnostics, not newly recovered per-query reference logits. `index_cost_refined64.csv` contains means/medians, whereas `index_cost_original738.csv` contains a different original per-query timing panel. Do not join them as if one measurement. Component timings are nested and cannot be added to total time.

`CASE_ANALYSIS.md` contains all 16 fixed, de-identified assistant-assisted cases. Private source text, questions, predictions and true source IDs are intentionally absent. Full model reproduction additionally requires the original inputs, cohort identities, checkpoints, code and authorized data described in `DATA_AND_REPRODUCTION.md`.

`training_history.jsonl`, checkpoint and static-selection tables preserve prior completed runs, including conditions outside the main panel. Do not relabel them as independent confirmation. The initial static TUNE criterion included QA; only subsequent continuation DEV_SELECT excluded QA.
