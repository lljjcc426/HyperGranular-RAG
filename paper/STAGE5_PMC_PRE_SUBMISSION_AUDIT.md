# Stage5-PMC Pre-Submission Audit

## Audit status

```text
STAGE5_PMC_INTERNAL_EVIDENCE_CONSOLIDATION_PASS
STAGE5_PMC_FIGURE_TRACE_PASS
MANUSCRIPT_NOT_YET_SUBMISSION_READY
EXTERNAL_REFERENCE_CORPUS_PENDING
VENUE_AND_AUTHOR_METADATA_PENDING
NO_NEW_EXPERIMENT_REQUIRED_BY_CURRENT_EVIDENCE_AUDIT
```

## 1. Evidence-to-claim consistency

| Audit item | Status | Finding |
|---|---|---|
| Stage4E/4F compact-dense positive results retained | PASS | Exact absolute F1/EM and paired intervals are present in the core tables and forest plot |
| Stage4H Full−Dense and Full−NoFacet positive results retained | PASS | Both are represented as frozen system-specific support |
| Stage4H Full−BGE negative result visible | PASS | Included in main robustness table, forest plot, evidence map and applicability boundary |
| Stage4H protection interval crosses zero | PASS | Written as inconclusive, never equivalent or ineffective |
| Flat granular-ball control | PASS | Written as `NOT_FAIRLY_DEFINED`, not as positive or negative evidence |
| Stage4I Protected−BGE interval crosses zero | PASS | Written as complementarity inconclusive |
| Stage4I placement evidence hierarchy | PASS | Protected−Unprotected is supporting evidence and does not replace Protected−BGE |
| Stage4I facet evidence | PASS | Written as inconclusive on the BGE sidecar |
| Gemma transfer | PASS | Written as one-configuration inconclusive; mobile-QAT confounding retained |
| Full-wiki/open-domain | PASS | Explicitly not evaluated and deferred |
| Controller line | PASS | Kept separate, frozen and closed |

## 2. Numerical trace audit

- Figure generation verifies exact SHA-256 identities for 14 tracked Stage4E–Stage4I source artifacts before reading their JSON content.
- Core table values are traceable to tracked evaluation summaries, dataset summaries, equal-weight summaries, telemetry and reports.
- Figure source data are stored as seven UTF-8 CSV files.
- Five figure groups are exported to SVG, PDF, TIFF and PNG.
- `paper/figures/STAGE5_PMC_FIGURE_MANIFEST.json` records source/output bytes and SHA-256.
- Stage5 performs no retrieval, generation, Gold read, bootstrap, threshold selection or scientific decision reconstruction.
- `python scripts/stage5_pmc_verify_materials.py` returns `STAGE5_PMC_MATERIALS_VERIFIED` after checking 14 frozen inputs, 27 derived files, five figure groups, seven source-data CSV files, core claim strings and local links.
- Two consecutive Python figure builds produced zero byte changes across all 29 files under `paper/figures/` (including contracts and manifest).
- The Stage4E–Stage4I regression suite remains `89 passed`.

## 3. Caption and visual audit

| Risk | Status | Control |
|---|---|---|
| Color-only interpretation | PASS | Labels, sign, position and hatching duplicate color meaning |
| Hidden negative result | PASS | Strong-dense negative appears in Figure 2 and Figure 5 |
| Inconclusive written as equivalence | PASS | “Inconclusive/uncertain” is used explicitly |
| Descriptive Gold transition treated as causal | PASS | Figure 3 labels it post-decision descriptive |
| Placement support used as sidecar efficacy | PASS | Captions separate the two contrasts |
| Method schematic misstates protection | PASS | Figure 1 states Dense Top-10 protection and bounded Top-20 output |
| Non-editable primary figure | PASS | SVG text remains editable |

## 4. Prohibited-claim scan

The current Stage5 materials do not claim:

- universal superiority over strong dense retrieval;
- full-wiki/open-domain effectiveness;
- universal cross-generator robustness;
- independently confirmed granular-ball necessity;
- equivalence from a non-significant interval;
- pure Qwen-versus-Gemma architecture superiority;
- that Gemma is unsuitable for RAG;
- that Qwen is more efficient on all devices;
- that the current controller failure invalidates static HyperGranular-RAG.

## 5. Remaining submission blockers

These are manuscript-production gaps, not scientific failures:

1. Target venue, manuscript template and length limits are unknown.
2. Author order, affiliations, corresponding author, funding and conflict-of-interest statements are unknown.
3. A verified external literature corpus and bibliography have not yet been assembled.
4. Dataset/model/software license statements need venue-specific wording.
5. The evidence-bound English core draft exists, but unresolved `{{CITE: ...}}` slots require verified references and final language polishing.
6. Supplementary-material packaging and repository archival DOI have not been selected.

Until these items are resolved, the repository must not label the manuscript “submission ready.” No additional algorithm experiment is required by the present evidence audit.

## 6. Recommended next writing transaction

```text
TARGET_VENUE_AND_AUTHOR_METADATA
→ VERIFIED_LITERATURE_CORPUS
→ CITATION_BOUND_ENGLISH_DRAFT
→ TABLE/FIGURE PLACEMENT
→ REFERENCE_AND_CLAIM AUDIT
→ VENUE_FORMATTING
→ FINAL SUBMISSION PACKAGE
```

Full-wiki remains optional and non-blocking. It should only be reconsidered if the completed draft and target venue reveal a concrete review requirement that cannot be met by the existing frozen evidence.
