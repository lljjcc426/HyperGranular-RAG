# Neurocomputing final polish v2

SPEC_ID: `HGRAG-NEUCOM-LITERATURE-GROUNDED-FINAL-POLISH-20261006`

Status: `AUTHOR_REVIEW_READY` — editorial work completed; no submission performed.

The article follows supplied-set discrimination, actual evidence selection, and answers on the same questions. Runtime is a supporting observation. This version edits and redraws the completed empirical study; it adds no experiment, answer score, or statistical test.

- [Final neutral review PDF](Manuscript_Neurocomputing_FinalReview.pdf): 24 pages, including references.
- [Editable main text](manuscript/main.tex), six LaTeX tables, and three vector figures.
- [Flat source archive](Neurocomputing_Final_Source.zip): compiled after clean extraction.
- [Numerical supplement](Reproducibility_Supplement.zip): unchanged numerical files; deterministic reconstruction checked.
- [Highlights](Highlights.docx), [plain text](Highlights.txt).
- [Final edit log](FINAL_EDIT_LOG.md) and [submission file map](SUBMISSION_FILE_MAP.md).
- [Reading and evidence scope](READING_AND_EVIDENCE.md).

The locally ignored `submission_local/Manuscript_Neurocomputing_WithAuthors_FinalReview.pdf` is the same scientific text with confirmed authors and CRediT. The local folder also contains the author page, declarations, cover-letter draft, and final author checklist. It is not part of the public source archive or numerical supplement.

## Local reproduction

The numerical supplement requires only Python's standard library: extract it and run `python reconstruct.py`. The source ZIP builds with `pdflatex main`, `bibtex main`, and two further `pdflatex main` passes. Its class and bibliography style are included. This does not reproduce model training or reader predictions.

`analysis/make_tables.py` and `figures/plot_results.py` rebuild displays from the saved numerical files. `analysis/check_delivery.py` records the delivered-version checks, using the adjacent conversion-v1 directory and the clean extraction directories from this task. The figures were rendered with Python 3.11.5 and Matplotlib 3.11.2; PDF inspection used PyMuPDF 1.28.2. Private document construction additionally requires the user-provided metadata and the existing local Node/docx runtime.

Previous conversion and experimental artifacts remain intact. This task creates files only in this version directory; it does not resolve or commit unrelated workspace edits.
