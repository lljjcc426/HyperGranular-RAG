# Reproducing the bounded continuation

This directory implements RG-search-aligned-closeout-v6.0, SPEC_ID HGRAG-SEARCH-ALIGNED-CLOSEOUT-V6-20261005. It depends read-only on the completed `../2026-10-04_rg_learned_set_v5/` implementation and local artifacts. It is not a standalone distribution of benchmark text, answers, embeddings, weights, or caches.

## Required existing inputs

- v5 `local/corpus.json`, `queries.json`, `targets.json`, `retrieved.json`, `subsets.json`, normalization and embedding identity records, block/query arrays, and corresponding H1/H2/H4/DeepSets checkpoints.
- The existing local BGE and Qwen2.5-3B-Instruct snapshots and tokenizer; the v4 P2 reader protocol and canonical dataset scorers used by v5.
- Python environment `temp/stage4e_env`, with the already installed PyTorch, Transformers, NumPy and lm-format-enforcer packages. No package upgrade, model download or adapter training is needed.

Observed research environment: CPython 3.12.0, PyTorch 2.12.1+cu130, Transformers 5.14.1, NumPy 2.5.1, lm-format-enforcer 0.11.3, Pillow 12.3.0; existing RTX 4060 Laptop 8 GB. Existing one-thread BLAS/OpenMP and deterministic Torch settings are inherited from v5. PDF work uses the separate, already available `temp/dual_manuscripts_env` (PyMuPDF 1.28.2, Pillow 12.3.0); no dependency was installed into the research environment.

Paths are resolved from the repository by the existing v5 configuration. Local dataset/model locations must be supplied consistently with those inputs on another machine. Public CSVs are reproducible summaries, not substitutes for the required original source licenses and access.

## Model commands

Run from the repository root. These are reproduction commands, not permission to restart completed experiments. Consult `RESULTS_AND_SUBMISSION_DECISION.md` for actual completed rounds and seeds and the resource cap.

```powershell
$py = '.\temp\stage4e_env\Scripts\python.exe'
$v6 = 'research/2026-10-05_rg_search_aligned_closeout_v6'
& $py "$v6/test_aligned.py"
& $py "$v6/aligned.py" baseline 1 1729
& $py "$v6/aligned.py" mine 1 1729
& $py "$v6/aligned.py" train 1 1729
& $py "$v6/aligned.py" mine 2 1729
& $py "$v6/aligned.py" train 2 1729
& $py "$v6/qa.py" select 1729
& $py "$v6/qa.py" run 1729
```

The primary model sequence is H1, H2, DeepSets, H4, then equal-update H4 replay. Selection chooses checkpoints using support completeness, coverage and original development loss; it does not inspect QA scores. All 128 QA questions remain in every method's denominator. Optional seed 2026 uses all four aligned architectures; it is not an outcome-selected winner rerun.

`qa.py rerun` performs the specified eight real cache-bypassing checks, and `finalize.py` derives public tables from completed local rows. The original canonical scorers and full P2 generation identity are reused. Cache hits do not count as fresh model calls. `cost.jsonl` is append-only phase accounting; interpreter startup and older unmeasured CPU time are not retroactively invented.

## Manuscripts without model execution

The checked-in shared TeX tables allow a paper build without Gold, weights or a GPU:

```powershell
$paperPy = '.\temp\dual_manuscripts_env\Scripts\python.exe'
& $paperPy "$v6/manuscripts/build.py" conference journal
```

The build driver uses the user's installed Windows MiKTeX path, PyMuPDF and Pillow. On another system the source can be compiled using the supplied LNCS or Springer Nature class with `pdflatex`, `bibtex`, and repeated `pdflatex` passes from each manuscript directory; `../shared` contains bibliography styles, bibliography and tables. Build products and page images go to ignored `build/` directories. New named PDFs are generated in the v6 manuscript directories only.

No historical manuscript or image is replaced. The conference and journal are alternative versions of one study and must not be submitted simultaneously. Final author identity, statements, registration and submission remain manual.
