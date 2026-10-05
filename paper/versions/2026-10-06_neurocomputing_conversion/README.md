# Neurocomputing conversion — NC-manuscript-conversion-v1.0

SPEC_ID=HGRAG-NEUROCOMPUTING-CONVERSION-20261006

Status: **READY_FOR_AUTHOR_REVIEW / CONTENT_READY_REQUIREMENTS_PENDING**. This is not a submitted or approved-for-submission article.

## Read and use

- [Complete English manuscript, 23 pages](Manuscript_Neurocomputing_Review.pdf)
- [Editable Elsevier source](manuscript/main.tex) and [flat source ZIP](Neurocomputing_Source.zip)
- [Numerical supplement ZIP](Reproducibility_Supplement.zip), [reconstruction instructions](supplement/README.md)
- [Highlights](Highlights.docx), [competing interests declaration](Declaration_of_Competing_Interests.docx), [data availability](Data_Availability.md)
- [Final findings and unresolved matters](FINAL_STATUS.md), [editorial/build check](EDITORIAL_CHECK.md)
- [Official requirements checks](JOURNAL_REQUIREMENTS.md), [literature and reading scope](LITERATURE_AND_STYLE.md)

The manuscript investigates the gap between scoring supplied evidence sets, selecting evidence, answering, and measured computation. It uses completed static and search-aligned development runs. It does not relabel older static-q25 results as evidence for the learned selector.

## Public and local materials

This directory is the only publication allowlist for this task. The `private/`, `submission_local/`, and `build/` directories are ignored. The separately stored local author page, cover-letter draft and author checklist are not included in either public archive. The input ZIP, original questions, answers, source IDs, weights and withdrawal documentation are not published here.

All changes are additive in this new directory. No historical result, earlier manuscript, existing drawing script, or unrelated working-tree file was edited or deleted. Build fixes here added scalable fonts, narrowed a table, moved a plot annotation and corrected a bibliography layout note; no numerical endpoint changed.

## Reconstruction and build

For numerical reconstruction, unzip the supplement into an empty directory and run `python reconstruct.py` with Python 3. This requires only its standard library. It joins saved scores; it does not rescore answers or run models.

For the manuscript, unzip the source archive and run `pdflatex main.tex`, `bibtex main`, `pdflatex main.tex`, `pdflatex main.tex`. A normal TeX installation with the packages used in `main.tex` is required. The template class and bibliography style are included; font files and build logs are not bundled. A separate extraction was actually compiled in this task.

The preparation scripts in `analysis/` additionally depend on authorized historical local records and, for PDF checks/plots, PyMuPDF and Matplotlib. `documents.js` reads private metadata only to create local author documents. It is not needed for public numerical reconstruction. Final local check results are in [DELIVERY_CHECK.json](analysis/DELIVERY_CHECK.json).
