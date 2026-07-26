# ACL/EMNLP Findings Narrative-Polished Draft Build Status

Build date: 2026-07-26

Status:

```text
ACL_ANONYMOUS_FIRST_DRAFT_COMPLETE
WEAK_REJECT_REVISION_COMPLETE
MANUSCRIPT_LEVEL_EVALUATION_REVISION_COMPLETE
ACL_FINDINGS_LANGUAGE_REVISION_COMPLETE
FIGURE1_WORKFLOW_REPLACED
ACL_FINDINGS_EXPERIMENTAL_FIGURES_REDESIGNED
SCIENTIFIC_EVIDENCE_CUTOFF = STAGE5A_BNH
SUBMISSION_METADATA_PENDING
SUBMISSION_READY = FALSE
```

## Deliverables

| File | Bytes | SHA-256 |
|---|---:|---|
| `main.tex` | 46,867 | `C36F33AC7DC01D70EAE3781E397570FB8CC19405F30B3A418357BFD4EFE12401` |
| `main.pdf` | 1,756,382 | `9B5E42DFCE7F156C975C603D3B4069300076471B261C859F8110ED130305CC6D` |
| `../figures_stage5r/figure1_method_overview.png` | 1,508,661 | `215FBB2149B958A422B7B111395A53F32B0C423F12F61481A616BB5D81FBD969` |
| `../figures_stage5r/STAGE5R_FIGURE_MANIFEST.json` | 16,123 | `32FEBF39A9DB714175B71C399DDE6D9ABA3AA129D39C507EDD7D1F5EFE58DB4A` |
| `vendor/acl.sty` | 11,927 | `7DEF961AC900A2BBCC091DA0EE71796B277E6D14A707C9EED52B76EF5D25AE2A` |
| `acl_natbib.bst` | 47,393 | `99DBB3C8E53F0DF971AE882F02C35D37AC2BF387558518B822DB16109A799F44` |

The style-file source and upstream commit are recorded in
[`ACL_STYLE_PROVENANCE.md`](ACL_STYLE_PROVENANCE.md).

## Build and validation

The tracked PDF was compiled from `main.tex` with Tectonic 0.16.9 in the
`paper/latex/` working directory. The equivalent command is:

```powershell
$env:SOURCE_DATE_EPOCH = '1784950406'
tectonic -X compile --outdir ..\..\temp\stage5r_latex_build main.tex
```

Validation results:

- 15 pages total: the main argument occupies pages 1–8; the conclusion,
  ethics/data/AI-disclosure back matter, and references continue across pages
  9–10; appendix material begins on page 10 and continues through page 15;
- 190-word abstract in problem–gap–method–result–implication order;
- 23 unique citation keys, all present in the 23-entry verified BibTeX file;
- 32 frozen scientific inputs, 17 machine-readable table/figure source CSVs,
  and 39 derived-file identities pass the read-only Stage5R verifier;
- no unresolved citations, unresolved references, overfull boxes, LaTeX
  errors, `TBD`, `TODO`, `{{CITE: ...}}`, or `??` markers;
- no confirmed author names or affiliation strings in the anonymous source or
  extracted PDF text;
- two clean builds with the fixed `SOURCE_DATE_EPOCH=1784950406` produced
  byte-identical 1,756,382-byte PDFs with SHA-256
  `9B5E42DFCE7F156C975C603D3B4069300076471B261C859F8110ED130305CC6D`;
- the replacement Figure 1 page was rendered and visually inspected after the
  final source change; its embedded caption was clipped at inclusion time so
  the ACL caption appears exactly once, with no clipping of diagram content,
  overlap, or missing panels;
- redesigned Figures 2–5 were rendered from their Python source, inspected in
  the 15-page PDF, and checked for readable labels, intact uncertainty
  intervals, explicit boundary separation, complete captions, and non-orphaned
  appendix layout;
- one non-blocking BibTeX style warning remains for the `feng2019hgnn` record
  containing both `volume` and `number`; it does not change the resolved
  citation or manuscript content.

## Boundary

This is a narrative-polished anonymous ACL/EMNLP Findings draft for the current
evidence, not a portal-ready submission. The revision leads with the structured
evidence-completion contribution, defines the method terminology consistently,
uses conventional experimental-paper section language, and presents positive,
negative, statistically unresolved, and unmatched evidence without changing
the underlying claims. It does not establish granular-ball necessity,
superiority over generic diversity/coverage selectors, strong-retriever
improvement, or open-domain value. Author order, English publication names,
affiliations, corresponding-author details, funding, conflicts, contributions,
acknowledgements, final AI disclosure, target venue, and repository/artifact
licenses remain governed by
[`../AUTHOR_AND_SUBMISSION_METADATA.yaml`](../AUTHOR_AND_SUBMISSION_METADATA.yaml)
and require human confirmation.

No retrieval, generation, Gold evaluation, bootstrap, model search, or
scientific decision was rerun to produce this draft.
