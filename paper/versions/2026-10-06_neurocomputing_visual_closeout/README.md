# Neurocomputing visual closeout

SPEC_ID: `HGRAG-NEUCOM-VISUAL-CLOSEOUT-20261006`

Status: `AUTHOR_REVIEW_READY`. No submission performed.

- [Updated neutral manuscript](Manuscript_Neurocomputing_VisualCloseout.pdf): 25 pages including declarations and references.
- [Public LaTeX source ZIP](Neurocomputing_VisualCloseout_Source.zip): four figures, six tables; independently extracted and compiled.
- [Overview vector PDF](figures/study_design.pdf), [editable TikZ](figures/study_design.tex), [PNG preview](figures/study_design.png).
- [Figure check](FIGURE_CHECK.md) and [local check results](analysis/CLOSEOUT_CHECK.json).
- [Numerical supplement](Reproducibility_Supplement.zip) and [Highlights](Highlights.docx): unchanged from the preceding final-polish version.

This revision adds only a study-design overview, its introduction and caption. The existing three result figures, six tables, numerical supplement, scientific text, and conclusions are retained. The joint transition plot remains paired with Table 5 rather than repeating that table in another figure.

The locally ignored `submission_local/Manuscript_Neurocomputing_WithAuthors_VisualCloseout.pdf` contains the same scientific text with confirmed author information. Its editable files are in `submission_local/authored/`. The previously confirmed author page, cover-letter draft, declarations, and author checklist are also retained locally. None are included in the public archive.

## Build

Extract the source ZIP and run `pdflatex main`, `bibtex main`, then `pdflatex main` twice. The class, bibliography style, bibliography output, and all figure PDFs are included. To edit the overview, compile `study_design.tex` separately and rebuild the article.

Within this directory, `analysis/build_overview.py` builds the original TikZ figure and its preview; `analysis/build.py` builds the article; `analysis/inspect_pdf.py` renders every page for visual review. `analysis/package.py` stages the public source and the private authored build; the latter requires the existing local author files. `analysis/check_closeout.py` checks this revision against the adjacent final-polish directory and completed local builds. It performs no scientific recomputation. PDF tooling uses the existing local Python/PyMuPDF environment and MiKTeX.

The numerical supplement and prior data-figure plotting sources remain in the [preceding version](../2026-10-06_neurocomputing_final_polish/). No historical file or unrelated local change is deleted or included in this revision.
