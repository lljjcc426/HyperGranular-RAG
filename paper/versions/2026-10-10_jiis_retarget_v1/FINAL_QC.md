# Final JIIS editorial QC

SPEC_ID=HGRAG-JIIS-EMPIRICAL-RETRIEVAL-RETARGET-20261010

## Delivered state

Complete English main article, authored and neutral PDFs, flat source archive, Online Resource methods PDF and numerical ZIP, cover letter and author declarations. Main article: **22 pages total**; abstract **212 words**; **6 keywords, 5 figures, 6 tables, 8 displayed equations**. Methods supplement: **5 separate pages**. The main article is within the 25-page limit without font/margin compression. No author-final-approval or acceptance claim is made.

## Actual checks and scope

- The authored article's 22 pages were rendered and visually inspected in page order. Figures were additionally inspected at insertion size and in grayscale at 75% scale. No overlapping or clipped main-article content was found. The public copy has the same scientific text with author metadata omitted.
- Five supplementary pages were rendered; a long development-role label in the reproduction map was shortened to avoid crowded table text. This changed no data role or numeric value.
- Both article builds and an independently extracted source build completed pdflatex/BibTeX/pdflatex/pdflatex with exit 0. Independent page count and extracted page text match. No unresolved `??` references or overfull boxes. Template underfull-box warnings remain ordinary whitespace warnings, not content loss. MiKTeX's update reminder is an environment notice, not a build failure.
- All six tabular blocks and all eight displayed equations compare exactly with the converted baseline. Figures 3–5 are unchanged. Figures 1–2 differ only in panel lettering A/B/C → a/b/c; all data, geometry and scientific relationships remain unchanged. All five PDFs have embedded fonts.
- Independent numerical ZIP extraction and `reconstruct.py` succeeded: 128 unique questions, 1,024 paired rows, 2,688 numerical observations, 24 groups. The four regenerated descriptive CSV files match their retained counterparts. This uses saved scores, **not** raw-answer rescoring or a new inferential test.
- Local machine records: `build/editorial_checks.json`, `build/numeric_format_checks.json`, and build logs. The public numerical check records are copies of these outputs, not substituted PASS claims.

## Scientific content preserved

Dense-K6 remains an explicitly eligible feasible reference; TUNE completeness 0.8214/0.7092 and 0.2565/0.2232 retained. H4 completeness 55→57 / F1 0.4181→0.3766 and second-seed 53→57 / 0.4304→0.3831 retained. Paired support-preserving contributions −0.0320/−0.0477 retain N=128 denominators. MMR 0.4303, low-order and DeepSets controls, measured no-acceleration result and missing-record boundaries retained. No new comparison, scorer, statistical test or model call was run.

## Remaining academic risks

1. QA comes from exposed TUNE and participated in initial checkpoint selection; later selection separation does not turn it into independent confirmation.
2. One encoder/reader and a small same-question panel limit transfer and system breadth. Two seeds do not double the independent sample.
3. The training intervention changes examples, losses and checkpoint criteria together; replay matches optimizer updates, not every computation or causal factor.
4. Descriptive support–answer transitions and 16 inspected cases do not establish causal mechanisms or population error rates.
5. Missing per-query feasible-reference scores and refined timing records restrict reanalysis and full regeneration; no gap is filled with invented data.
6. Standard factorization and index bounds are not new theory. Editorial fit is improved, but empirical breadth/contribution may still be insufficient for JIIS acceptance.

## Manual submission checks still open

All four authors' approval of this changed manuscript and public supplementary release; full affiliation address; live system declarations/categories; no concurrent review/transfer; any optional charges. Direct retrieval resolved the initial proxy/browser issue: current official scope, submission guidelines and publishing options were obtained, and Subscription without an OA APC was confirmed. See OFFICIAL_REQUIREMENTS.md for precise reading depth; targeted paper reading is not represented as exhaustive full-text review.

## Files and cost

All changes are in this new version directory. No historical file was deleted or overwritten, and unrelated dirty work remains untouched. New files comprise the revised manuscript artifacts, two letter-case-only figure sources, submission packaging/editorial scripts and checks. Private author sources/full archive remain local. New research computation, training, inference, retrieval, scoring, tests and paid calls: **0**. Only local editorial builds, PDF rendering and descriptive saved-number reconstruction were performed.

This bounded conversion is complete; no next research or visual-polish round is launched. Authors decide whether to approve and submit.
