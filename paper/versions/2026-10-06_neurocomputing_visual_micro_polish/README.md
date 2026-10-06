# Neurocomputing — final Figure 1/2 micro-polish

This visual revision implements `NC-visual-micro-polish-v3.0` from baseline `b1886d2`. It changes only Figures 1–2 and the necessary Figure 2 caption. Scientific content and Figures 3–5/Tables 1–6 are unchanged.

- [Neutral manuscript](Manuscript_Neurocomputing_VisualMicroPolish.pdf)
- [Self-contained LaTeX source ZIP](Neurocomputing_VisualMicroPolish_Source.zip)
- [Visual inspection and change record](VISUAL_MICRO_QC.md)
- [Figure 1 editable source](figures/motivating_examples.tex), [vector PDF](figures/motivating_examples.pdf), [PNG](figures/motivating_examples.png)
- [Figure 2 editable source](figures/study_design.tex), [vector PDF](figures/study_design.pdf), [PNG](figures/study_design.png)
- [Unchanged numerical supplement](Reproducibility_Supplement.zip)

The authored PDF is local only: `submission_local/Manuscript_Neurocomputing_WithAuthors_VisualMicroPolish.pdf`. Confirmed author metadata and declarations remain unchanged and excluded from public packages. Prior versions remain available in their original directories.

## Rebuild

Extract the source ZIP into an empty directory; run `pdflatex main.tex`, `bibtex main`, and `pdflatex main.tex` twice. Prebuilt vector figures are included, so rebuilding the manuscript does not require regenerating figures. To edit/rebuild either figure separately, compile its TEX with XeLaTeX and the locally installed Arial family; no font files are included.

The existing workflow is retained in `analysis/`: `build_figures.py` builds only Figures 1–2; `build.py` compiles a manuscript; `package.py` packages neutral sources and stages the private authored build when its local inputs exist. `check_delivery.py` compares frozen assets and creates width/scale/grayscale previews. It requires the preserved baseline directory. No result-plot script was run for this revision.

Both delivered manuscripts contain 26 pages including declarations and references. This directory is a final visual delivery, not a new scientific experiment or a submitted manuscript.
