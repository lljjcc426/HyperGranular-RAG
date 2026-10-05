# Complete alternative manuscripts for the v6 closeout

## Current editorial submission alternatives

- [Conference PDF, submission edit](../submission_edit/anonymous_conference/Set_Selection_Conference_V6_Submission_Edit.pdf) and [flat editable source](../submission_edit/anonymous_conference/main.tex).
- [Journal PDF, submission edit](../submission_edit/submission_bundle/Evidence_Selection_Journal_V6_Submission_Edit.pdf) and [flat editable source](../submission_edit/submission_bundle/main.tex).
- [Editorial changes and delivery](../submission_edit/EDITORIAL_CHANGES.md), [actual build/page checks](../submission_edit/EDITORIAL_CHECK.md), and [anonymous numerical supplement](../submission_edit/anonymous_supplement/README.md).

The internal `conference/main.tex`, `journal/main.tex`, and shared inputs now contain the submission edit. The older named PDFs below remain unchanged; their corresponding pre-edit sources remain in Git at `b7c91fde94d1de7213ab50382ba4f50f313187c3`. Use `../submission_edit/build_submission.py` for the new deliverables; the older `build.py` is the earlier build entry. Status: READY_FOR_AUTHOR_CHECK, not submitted.

## Preserved pre-edit PDFs

- Conference: [PDF](conference/HyperGranular-RAG_Conference_V6.pdf), [LaTeX](conference/main.tex). A focused empirical paper in LNCS format for a conditional ECIR 2027 Short submission.
- Journal: [PDF](journal/HyperGranular-RAG_Journal_V6.pdf), [LaTeX](journal/main.tex). A fuller empirical study prepared with the Springer Nature class for possible JIIS submission.
- Shared numerical tables and bibliography: `shared/`.
- Build command and environment: [REPRODUCE.md](../REPRODUCE.md).
- Actual page-by-page scope, page counts and remaining human checks: [FINAL_MANUSCRIPT_CHECK.md](../FINAL_MANUSCRIPT_CHECK.md).
- Submission dates and unverified registration status: [SUBMISSION_WINDOW.md](../SUBMISSION_WINDOW.md).

Both are full English papers, not an experiment proposal. They investigate the gap between proxy prediction, actual evidence selection, answer quality and computational cost. The journal additionally preserves the relevant original completion/placement evidence and standard search derivation, while keeping those historical methods distinct from learned paragraph selection.

These manuscripts are alternatives covering the same research and must not be submitted simultaneously. Neither file establishes submission eligibility or acceptance. Authors, affiliations, declarations, licensing, anonymity and final submission are human decisions. The anonymous placeholders do not assert that every venue-specific anonymity requirement has been met.

Only new v6 paper files are created. Older dual manuscripts, revision2/final editorial copies, frozen results, figures and plotting scripts are preserved. No old workflow illustration is reused to depict the new learned selector. A new schematic is optional future editorial work; no image changes were authorized in this task.
