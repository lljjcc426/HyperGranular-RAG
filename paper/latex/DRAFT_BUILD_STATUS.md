# Reviewer-Responsive Anonymous ACL Draft Build Status

Build date: 2026-07-26

Status:

```text
ACL_ANONYMOUS_FIRST_DRAFT_COMPLETE
WEAK_REJECT_REVISION_COMPLETE
MANUSCRIPT_LEVEL_EVALUATION_REVISION_COMPLETE
SCIENTIFIC_EVIDENCE_CUTOFF = STAGE5A_BNH
SUBMISSION_METADATA_PENDING
SUBMISSION_READY = FALSE
```

## Deliverables

| File | Bytes | SHA-256 |
|---|---:|---|
| `main.tex` | 44,606 | `CBBFF413F618B87385EC16BAF7B14A800A0FFDE7E24DA42AFCA8A19798C9A784` |
| `main.pdf` | 198,547 | `822AA85CD1A3A825FACC4B6C6CF638AF50E705E68DF5CD4F58AD6A12B82C3BD3` |
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
- 26 frozen scientific inputs, 12 machine-readable table/figure source CSVs,
  and 34 derived-file identities pass the read-only Stage5R verifier;
- no unresolved citations, unresolved references, overfull boxes, LaTeX
  errors, `TBD`, `TODO`, `{{CITE: ...}}`, or `??` markers;
- no confirmed author names or affiliation strings in the anonymous source or
  extracted PDF text;
- two clean builds with the fixed `SOURCE_DATE_EPOCH=1784950406` produced
  byte-identical 198,547-byte PDFs with SHA-256
  `822AA85CD1A3A825FACC4B6C6CF638AF50E705E68DF5CD4F58AD6A12B82C3BD3`;
- all 13 rendered pages were visually inspected; the final method-equation and
  page-limit boundary pages were re-rendered after the last source change; no
  clipping, overlap, or missing figure/table content was found;
- one non-blocking BibTeX style warning remains for the `feng2019hgnn` record
  containing both `volume` and `number`; it does not change the resolved
  citation or manuscript content.

## Boundary

This is a reviewer-responsive anonymous draft for the currently frozen
evidence, not a portal-ready submission. The review revisions narrow component
claims, expose the complete available baseline/ablation record, add
deterministic algorithms and frozen parameters, report absolute and paired
metrics, distinguish inference-time label-free execution from development, and
deepen the failure analysis. They do not establish granular-ball necessity,
superiority over generic diversity/coverage selectors, strong-retriever
improvement, or open-domain value. Author order, English publication names,
affiliations, corresponding-author details, funding, conflicts, contributions,
acknowledgements, final AI disclosure, target venue, and repository/artifact
licenses remain governed by
[`../AUTHOR_AND_SUBMISSION_METADATA.yaml`](../AUTHOR_AND_SUBMISSION_METADATA.yaml)
and require human confirmation.

No retrieval, generation, Gold evaluation, bootstrap, model search, or
scientific decision was rerun to produce this draft.
