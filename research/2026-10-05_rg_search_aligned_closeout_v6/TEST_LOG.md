# Actual scoped test record

Before the first mining/training run, the v6 CPU test command was executed with the existing Python environment:

```text
.\temp\stage4e_env\Scripts\python.exe research/2026-10-05_rg_search_aligned_closeout_v6/test_aligned.py
test_empty_pairs_are_masked ... ok
test_parent_pair_and_no_false_positive ... ok
test_partial_coverage_trains_deployed_logit ... ok
test_sampling_not_outcome_and_group_intact ... ok
Ran 4 tests in 1.589s
OK
```

This is a transcription of the actual tool output, not a newly executed test suite. The tests check the introduced preference gradient and sampling semantics. They are not evidence of QA improvement or independent confirmation. Unchanged v5 search-index correctness experiments were not rerun.

Actual training metrics are in `TRAINING.csv` and `SEARCH_ALIGNED_RESULTS.csv`; completed reader results and cache-bypassing checks are reported separately. Build logs are the actual compiler stdout/stderr in each new manuscript's ignored `build/command_*.log`. Visual inspection is documented in `FINAL_MANUSCRIPT_CHECK.md`, not inferred from successful compilation alone.

The eight prescribed reader checks were actually executed with cache bypass. All eight reproduced both the original input identity and complete output-token sequence (`READER_RERUN.json`). They include both datasets and multiple aligned/replay methods. This checks the sampled generation identities; it does not establish deterministic training or constitute a second QA experiment. No additional repeat of unchanged v5 ball-index checks was run.
