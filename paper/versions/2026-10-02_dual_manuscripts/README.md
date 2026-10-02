# HyperGranular-RAG: two complete manuscript drafts

2026-10-02. Complete writing release. Initially delivered locally under a no-push instruction; the user's subsequent continuous GitHub synchronization authorization now covers publication of this manuscript package. No new formal experiment or external submission is authorized.

## Read the manuscripts

- [Conference manuscript — PDF](conference/HyperGranular-RAG_Conference.pdf), 8 pages including references and appendix; [LaTeX](conference/main.tex).
- [Journal manuscript — PDF](journal/HyperGranular-RAG_Journal.pdf), 19 pages including references and appendices; [LaTeX](journal/main.tex).
- [中文故事链、两版差异与剩余事项](STORY_AND_VERSION_DIFFERENCES_ZH.md).
- [Evidence and historical-version ledger](EVIDENCE_AND_VERSION_LEDGER.md).
- [Primary-literature reading and citation notes](LITERATURE_READING_AND_CITATION_NOTES.md).
- [Build and page review](BUILD_AND_PAGE_REVIEW.md).
- [File changes](FILE_CHANGES.md) and [final status](FINAL_STATUS.md).

Both papers contain a title, abstract, introduction, related work, method, experimental design, results, analysis, limitations, conclusion, references, and provenance material. The journal additionally develops mathematical arguments, mechanism summaries, cases, and cost analysis. These are alternative presentations of the same empirical record, not independent studies.

## Shared assets

The shared directory contains generated numerical macros, source-bound effect estimates, vector figures, copied historical figure/table CSVs, a bibliography, and the existing ACL style files. Figures reuse recorded intervals; no bootstrap is rerun. The tables retain each historical evaluator's interpretation.

The bibliography preserves all 27 entries from the preceding corrected reference file, but each manuscript actually cites 13. Uncited entries do not appear in the compiled reference lists.

## Local build

From the repository root, the executed command is:

    temp/dual_manuscripts_env/Scripts/python.exe paper/versions/2026-10-02_dual_manuscripts/build_manuscripts.py conference journal

The script runs pdfLaTeX, BibTeX, and two further pdfLaTeX passes, then copies the resulting PDFs and renders every page. It uses the local Windows MiKTeX installation. Each build/command_N.log is real captured process output. Each page_review directory contains page PNGs and contact sheets. A fresh rebuild marks visual review pending; the signed-off review below pertains to the delivered build.

Document-only Python environment: Python 3.11.5, PyMuPDF 1.28.2, Pillow 12.3.0, matplotlib 3.11.2, NumPy 2.4.6. These packages are in the isolated ignored temp/dual_manuscripts_env directory and do not change the scientific experiment environment. Existing vector figures can be compiled without rebuilding assets.

Asset derivation, if intentionally needed:

    temp/dual_manuscripts_env/Scripts/python.exe paper/versions/2026-10-02_dual_manuscripts/build_assets.py

Aggregate transcription check:

    temp/dual_manuscripts_env/Scripts/python.exe paper/versions/2026-10-02_dual_manuscripts/check_manuscript_evidence.py

The check reads aggregate summaries and existing plotting CSVs; it does not recompute answer metrics from Gold or run scientific validation. The old manuscript identities recorded at writing start are retained in shared/evidence_check.json.
