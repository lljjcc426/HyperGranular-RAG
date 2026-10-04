# Running this development implementation

Run from the repository root with the existing `temp/stage4e_env` Python environment. `DATA_AND_MODELS.json` records the exact opened inputs and existing local models; `RUNTIME.json` records the executed package versions. This is not a standalone public data release: source text, support targets, query/source mappings, embeddings, checkpoints and reader predictions remain in the ignored `local/` directory.

The public implementation does not acquire datasets, model weights or restricted labels. A new machine needs the same authorized Stage4E/F inputs and model snapshots. Local paths are centralized in `common.py`; changing a model, tokenizer, source content or preprocessing requires rebuilding its dependent encoding/cache, not reusing the old identity.

```powershell
$py = '.\temp\stage4e_env\Scripts\python.exe'
$run = 'research/2026-10-04_rg_learned_set_v5'
& $py "$run/test_v5.py"
& $py "$run/data.py" prepare
& $py "$run/data.py" encode
& $py "$run/dataset.py"
& $py "$run/calibrate.py"
& $py "$run/train.py" 1729
& $py "$run/diagnostics.py" 1729
& $py "$run/length_control.py" 1729
& $py "$run/evaluate.py" 1729 main
& $py "$run/qa.py" 1729 main
```

The fixed continuation order is seed2026 training/selection/QA, seed426 training/selection/QA, seed1729 `sensitivity` selection/QA, then seed1729 `closed` selection/QA. Before proceeding, account for already consumed resources; the specification's caps are cumulative, not renewed by starting another command. `evaluate.py` and `qa.py` skip existing logical rows. Do not delete completed artifacts to force a rerun. `qa.py rerun` is the explicit eight-call cache-bypass check, not a full new evaluation.

Finally, `report_stats.py` derives strata/failure/latency summaries and `finalize.py` derives descriptive QA differences and the resource ledger. Neither performs retrieval, training or inference. Main seed profiling measures every TUNE query with all exact indexes. Later seeds and sensitivity compare learned scores with H4-Flat and do not claim repeated index profiling.

All selection implementations use one CPU thread for score/search timing; the reader and training use the GPU in separate processes. Reported timings include the actual tokenizer work and per-query tree construction. They are workstation measurements, sometimes overlapping CPU selection and GPU reading, not an isolated hardware benchmark. Logical cache-hit rows reuse prior measured generation duration for descriptive per-prompt cost; actual calls/time are reported separately in `RESOURCE_SUMMARY.json`.

All selected sets, including MMR, are rendered in the same original BGE candidate order. MMR chooses membership with lambda0.7; its selection sequence is not a separate reader-ordering treatment. The learned selectors use at most six complete blocks; Dense/MMR use only the token cap. Report the associated block/token counts rather than treating the method contrast as a pure interaction-order ablation against those two nonlearned baselines. H1/H2/H4/DeepSets share the six-block beam framework.

`bind_existing_encoding.py` documents the initial run's post-execution array-order binding. It is not a general cache repair command and must not be used to bless an unknown or reordered embedding array. The current encoder writes its own identity on creation.

No command above grants access to Stage6 confirmation, reservation or Stage3B. This run is exposed development, not independent confirmation.
