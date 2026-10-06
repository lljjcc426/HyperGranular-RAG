# Neurocomputing visual narrative final

TASK_ID: `NC-visual-narrative-final-v2.0`  
SPEC_ID: `HGRAG-NEUCOM-VISUAL-NARRATIVE-FINAL-20261006`  
Starting commit: `3e9c3ebdc6d7e798abcbff6bd90985795b70e0eb`

## Deliverables

- [Neutral manuscript, 26 pages](Manuscript_Neurocomputing_VisualNarrativeFinal.pdf)
- [Self-contained LaTeX source ZIP](Neurocomputing_VisualNarrativeFinal_Source.zip)
- [Five editable/vector figures and previews](figures/)
- [Unchanged numerical supplement](Reproducibility_Supplement.zip)
- [Highlights](Highlights.docx)
- [Visual review and change record](VISUAL_QC.md)
- [Motivating-case provenance](CASE_FIGURE_TRACE.md)

The separately compiled authored manuscript is local only:
`submission_local/Manuscript_Neurocomputing_WithAuthors_VisualNarrativeFinal.pdf`.
The same ignored directory retains the confirmed title page, author declarations,
funding/competing-interest statements, draft cover letter, and final author checklist.
It is not part of the public source ZIP or repository.

This revision adds the C12/C10 motivating figure, replaces the study schematic,
and harmonizes the three existing result plots. Six tables, all result values,
references, Highlights, and the numerical supplement are unchanged. No historical
file was removed or replaced. No new experiment, inference, scoring, or statistical
test was run. The work is complete; no further research or visual iteration is opened.

## Build

The source ZIP includes the five vector PDFs, two editable TikZ sources, six
table inputs, bibliographies, and existing Elsevier class/style files. Extract it
into a new directory, then run:

```text
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Rebuilding the manuscript does not require redrawing the figures or Arial locally;
the supplied vector PDFs embed their fonts. To redraw, `analysis/build_figures.py`
uses XeLaTeX/TikZ, fontspec, installed Arial, and PyMuPDF; `figures/plot_results.py`
uses Matplotlib, Arial, and the three saved CSVs in `plot_data/`. Font files are not
distributed. Run these scripts from this version directory or by absolute path.
`analysis/build.py` wraps the manuscript build and records Windows process timing;
the direct LaTeX commands above are portable. `analysis/package.py` also stages
the private build and therefore requires the locally retained author inputs.

`analysis/DELIVERY_CHECK.json` records actual build exit codes, figure/table pages,
embedded-font checks and unchanged-data comparisons. Local page renders and
actual-width/75%-scale/grayscale previews are retained under ignored `build/`.
Final author approval and live submission-system requirements remain human actions;
this package has not been submitted.
