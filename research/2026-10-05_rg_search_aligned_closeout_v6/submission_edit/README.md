# v6 submission edit

Status: **READY_FOR_AUTHOR_CHECK**.

- [Conference PDF](anonymous_conference/Set_Selection_Conference_V6_Submission_Edit.pdf) — 6 body pages + 1 reference page.
- [Journal PDF](submission_bundle/Evidence_Selection_Journal_V6_Submission_Edit.pdf) — 19 pages including references and declarations.
- [Editorial changes](EDITORIAL_CHANGES.md), [actual numerical/build/page checks](EDITORIAL_CHECK.md), [reference checks](REFERENCE_CHECK.md).
- [Current abstract](ABSTRACT_READY.md). Registration receipt: UNKNOWN.

Upload candidates (author review required): Conference_Anonymous_Source.zip, JIIS_Submission_Bundle.zip, Anonymous_Numerical_Supplement.zip. Each ZIP has a flat root. The manuscript bundles contain editable source, necessary class/style files, bibliography and the actual new PDF. The numerical supplement contains no raw question text or answers.

To build a manuscript, extract its source ZIP and run `pdflatex main`, `bibtex main`, `pdflatex main`, `pdflatex main` in that directory using a working TeX distribution. To reconstruct numerical summaries, extract the supplement and run `python reconstruct.py --out reproduced` with standard-library Python. This is numerical-table reproduction, not model reproduction or prediction rescoring.

Internal editing sources remain in ../manuscripts. `build_submission.py` prepares and compiles the two flat bundles; it requires PyMuPDF and Pillow only for page rendering. Its `package` target creates the three ZIPs without running a compiler or model. Build renderings/logs and private/HANDOFF.md are local ignored material. BUILD_*.json records final compiler and page-inspection outcomes.

Prior v6 PDFs and research artifacts remain intact. No file was deleted; no new scientific result was generated.
