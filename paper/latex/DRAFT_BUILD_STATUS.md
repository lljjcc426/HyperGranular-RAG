# Reviewer-Responsive Anonymous ACL Draft Build Status

Build date: 2026-07-26

Status:

```text
ACL_ANONYMOUS_FIRST_DRAFT_COMPLETE
WEAK_REJECT_REVISION_COMPLETE
SCIENTIFIC_EVIDENCE_CUTOFF = STAGE5A_BNH
SUBMISSION_METADATA_PENDING
SUBMISSION_READY = FALSE
```

## Deliverables

| File | Bytes | SHA-256 |
|---|---:|---|
| `main.tex` | 39,766 | `203869F37E81EFBF0430DAA7AA8879C209E4CAF4C411F2D197842E2C8AFC2750` |
| `main.pdf` | 206,123 | `E6B1BDB3B337597AC5A4C5E4B272C7E32C0B7B74C02495DF5476D836E49743F1` |
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

- 13 pages total: main text on pages 1–8, ethics/data/AI-disclosure back matter
  and references on pages 9–10, and appendix figures/tables on pages 11–13;
- 23 unique citation keys, all present in the 23-entry verified BibTeX file;
- no unresolved citations, unresolved references, overfull boxes, LaTeX
  errors, `TBD`, `TODO`, `{{CITE: ...}}`, or `??` markers;
- no confirmed author names or affiliation strings in the anonymous source or
  extracted PDF text;
- two clean builds with the fixed `SOURCE_DATE_EPOCH=1784950406` produced
  byte-identical 206,123-byte PDFs with SHA-256
  `E6B1BDB3B337597AC5A4C5E4B272C7E32C0B7B74C02495DF5476D836E49743F1`;
- all 13 rendered pages were visually inspected; the final method-equation and
  page-limit boundary pages were re-rendered after the last source change; no
  clipping, overlap, or missing figure/table content was found;
- one non-blocking BibTeX style warning remains for the `feng2019hgnn` record
  containing both `volume` and `number`; it does not change the resolved
  citation or manuscript content.

## Boundary

This is a reviewer-responsive anonymous draft for the currently frozen
evidence, not a portal-ready submission. The weak-reject revision narrows
component claims, exposes the complete available baseline/ablation record,
adds exact frozen method definitions, and deepens the failure analysis. It does
not establish granular-ball necessity, superiority over generic
diversity/coverage selectors, strong-retriever improvement, or open-domain
value. Author order, English publication names,
affiliations, corresponding-author details, funding, conflicts, contributions,
acknowledgements, final AI disclosure, target venue, and repository/artifact
licenses remain governed by
[`../AUTHOR_AND_SUBMISSION_METADATA.yaml`](../AUTHOR_AND_SUBMISSION_METADATA.yaml)
and require human confirmation.

No retrieval, generation, Gold evaluation, bootstrap, model search, or
scientific decision was rerun to produce this draft.
