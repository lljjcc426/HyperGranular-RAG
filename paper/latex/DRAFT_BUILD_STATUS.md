# Anonymous ACL Draft Build Status

Build date: 2026-07-25

Status:

```text
ACL_ANONYMOUS_FIRST_DRAFT_COMPLETE
SCIENTIFIC_EVIDENCE_CUTOFF = STAGE5A_BNH
SUBMISSION_METADATA_PENDING
SUBMISSION_READY = FALSE
```

## Deliverables

| File | Bytes | SHA-256 |
|---|---:|---|
| `main.tex` | 35,057 | `1A74ACF038F6DAF49B2246672994F13E73B5DAEACD946A6B76DD570F1A455C2C` |
| `main.pdf` | 194,076 | `3DC0B6D98B2027EC4B67BDFD343CC53A959C79ABF1A5CF1D9AAD2EF423102157` |
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

- 12 pages total: main text on pages 1–8, references on pages 9–10, and
  appendix content on pages 11–12;
- 23 unique citation keys, all present in the 23-entry verified BibTeX file;
- no unresolved citations, unresolved references, overfull boxes, LaTeX
  errors, `TBD`, `TODO`, `{{CITE: ...}}`, or `??` markers;
- no confirmed author names or affiliation strings in the anonymous source or
  extracted PDF text;
- two clean builds with the fixed `SOURCE_DATE_EPOCH=1784950406` produced
  byte-identical 194,076-byte PDFs with SHA-256
  `3DC0B6D98B2027EC4B67BDFD343CC53A959C79ABF1A5CF1D9AAD2EF423102157`;
- all 12 rendered pages were visually inspected; no clipping, overlap, or
  missing figure/table content was found;
- one non-blocking BibTeX style warning remains for the `feng2019hgnn` record
  containing both `volume` and `number`; it does not change the resolved
  citation or manuscript content.

## Boundary

This is a complete anonymous first draft for the currently frozen evidence,
not a portal-ready submission. Author order, English publication names,
affiliations, corresponding-author details, funding, conflicts, contributions,
acknowledgements, final AI disclosure, target venue, and repository/artifact
licenses remain governed by
[`../AUTHOR_AND_SUBMISSION_METADATA.yaml`](../AUTHOR_AND_SUBMISSION_METADATA.yaml)
and require human confirmation.

No retrieval, generation, Gold evaluation, bootstrap, model search, or
scientific decision was rerun to produce this draft.
