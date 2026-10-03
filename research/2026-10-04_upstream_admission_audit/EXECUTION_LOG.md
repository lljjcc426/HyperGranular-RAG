# Actual execution and change record

Material Passport: completed CPU analysis, 2026-10-04. This is a concise record
assembled from actual command results, not a verbatim terminal transcript.
Working directory: E:/SCIENCE/HyperGranular-RAG. Existing interpreter:
temp/stage4e_env/Scripts/python.exe. No installation or model loading occurred.

1. tests.py: exit0; nine focused tests passed, process CPU0.359375 seconds.
   Actual stdout/stderr is retained in TEST_OUTPUT.txt. Tests cover the requested
   logical conditions, competition, paragraph paths, count composition, saturation,
   poisoned label fields and original-H0 agreement; these are not efficacy tests.
2. Implementation/card committed and pushed as e8c8537 before new counts.
3. With PYTHONHASHSEED=0, audit.py: exit0, COMPLETE; 4,000 original H0 matches,
   400 KMeans recorded metadata matches, 4,800 diagnostic lists, 199 saturated
   pilot queries, 4,776 existing-ranking property checks. CPU139.328125 seconds,
   wall142.061239 seconds; 292,317,319 output bytes at the run checkpoint.
4. verify_and_summarize.py: exit0, PASS; checked 41,248 new=0 redundancy cases,
   all4,800 matched compositions/stage contracts, and independently recounted
   144 aggregate rows. CPU12.375 seconds. It reads completed records only; it does
   not rerun retrieval, generation, answer scoring, bootstrap or R1/R2 optimization.
5. Read all18 selected case packets (question + entire Dense20 + up to2 candidates)
   and their recorded per-mask paths. inspect_results.py initially hit a GBK stdout
   UnicodeEncodeError partway through displaying case5; only the display stream
   was changed to UTF-8, then the incomplete/new cases were read. No scientific
   output was changed, overwritten or recalculated to address this display error.

Measured main/test/output-verification CPU subtotal:152.0625 seconds. Prior
measured subtotal:633.96875 seconds. Past document CPU and incidental display/Git
process overhead are not metered; they are not recorded as zero. No process was
killed or dataset pruned. Supplemental notes and manifest completion are local
bookkeeping after the completed computation.

New code, derived summaries, test output, case interpretation, proof and reports
are confined to this round's directory; root README changes only current navigation.
Prior local repair files, historical artifacts and manuscripts were not edited.
No files were deleted. Full group centers/members, annotation-derived target paths,
query-level rankings and case source text remain under ignored local/.

No changed scientific definitions during execution, no extra G6, no threshold,
seed, model or sample search, no new hypotheses tested with answers. New model
calls0; GPU0; paid0; answer experiments0. The analysis process confirmed torch,
transformers and sentence_transformers were not loaded. Further execution is not
authorized by a positive recovery count or this record.
