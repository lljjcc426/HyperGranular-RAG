# Stage5R Pre-Submission Audit

Status:

```text
STAGE5R_PMR_COMPLETE
CURRENT_EVIDENCE_MANUSCRIPT_COMPLETE
ACL_ANONYMOUS_FIRST_DRAFT_COMPLETE
WEAK_REJECT_REVISION_COMPLETE
ACL_FINDINGS_LANGUAGE_REVISION_COMPLETE
VERIFIED_LITERATURE_CORPUS_COMPLETE
FIGURE_AND_TABLE_AUDIT_PASS
CLAIM_AND_CITATION_AUDIT_PASS
SUBMISSION_METADATA_PENDING
SUBMISSION_READY = FALSE
```

Audit date: 2026-07-26

## 0. Weak-reject revision audit

PASS for the current frozen evidence.

- The revision record is
  [`WEAK_REJECT_REVISION_2026-07-26.md`](WEAK_REJECT_REVISION_2026-07-26.md).
- The manuscript now states directly that the frozen evidence does not
  establish granular-ball necessity, generic diversity/coverage-selector
  superiority, improvement over strong BGE, or open-domain deployment value.
- The supported Stage4H Full−NoFacet contrast is identified as
  facet-conditioned selection versus centroid-only ball expansion, not as a
  comparison with every simpler diversity/coverage objective.
- The main Results expose the existing BM25 and Dense−BM25 hybrid rows, the BGE
  negative result, and both statistically unresolved BGE extension families.
- The component table includes compact, sidecar, BGE-native, and unmatched-flat
  outcomes without converting unresolved or unmatched evidence into support.
- The method section now records the frozen ball construction, split rules,
  facet score and gates, redundancy constraint, expansion budget, protected
  prefix, q25 floor, and insertion cap.
- The Discussion and appendix now separate static gains from controller
  selection failure, reversed query-score direction, below-gate candidate
  probing, and strong-retriever displacement.
- No experiment, result artifact, scientific decision, or claim state was
  changed.

## 1. Evidence audit

PASS.

- Stage4E–Stage5A frozen input SHA-256 values are checked before every Stage5R
  build.
- All main numerical claims are generated from or checked against formal JSON
  artifacts.
- Stage5A dataset, equal-weight, placement, facet, EM, development, and
  post-decision Gold values match the frozen evidence ledger.
- Development `C10 +0.003143` is described only as configuration-selection
  evidence and is not pooled with confirmation.
- The Stage4H Full−BGE negative result remains visible in the abstract, Results,
  Discussion, tables, and forest plot.
- Stage4I and Stage5A intervals crossing zero remain `INCONCLUSIVE` in the
  evidence ledger and are described as statistically unresolved in the paper;
  neither is described as equivalence, success, or established harm.
- The Stage4I placement result is not used to claim sidecar efficacy over BGE.
- The Stage4H facet result is not transported into BGE-native space.
- Post-decision Gold transitions are labelled descriptive and do not control an
  advancement claim.

## 2. Citation audit

PASS.

- The bibliography contains 23 unique works.
- Every manuscript citation key exists in
  `paper/references/verified_references.bib`.
- Every cited work appears in the verified literature corpus with title,
  authors, year, venue, persistent identity, official source, review status,
  and permitted use.
- No `{{CITE: ...}}` placeholder remains.
- Peer-reviewed versions are preferred when available; GraphRAG and BGE
  technical records are identified as preprints.
- External citations support prior-work or reporting statements, not project
  effect sizes.
- No duplicate DOI is present in the bibliography.

## 3. Figure and table audit

PASS.

- Five figure groups are tracked. The active workflow overview is the approved
  replacement PNG, while the analytical figures retain their deterministic
  Matplotlib exports.
- Each figure has SVG, PDF, 600-dpi TIFF, and PNG exports.
- SVG text remains editable.
- Twelve CSV files provide figure/table source data.
- The effect-size forest includes all required compact, transfer, component,
  sidecar, and BGE-native contrasts and shows the zero line.
- Strong-retriever negative and inconclusive results are visually explicit.
- Figure 3 states that its three absolute-score groups are separate evaluation
  settings and are not pooled.
- Gold transitions are marked `POST_DECISION_DESCRIPTIVE_ONLY`.
- Five core tables are rebuilt from frozen JSON/CSV, not typed from memory.
- The current figure manifest SHA-256 is
  `0C6318A997F6C636B08CCE5C04E2C4E34690530FCB79D18F110D3F1E2D239E47`;
  all 34 derived-file identities pass the read-only verifier.

## 4. Language audit

PASS.

- The manuscript does not claim SOTA, universal improvement, strong-dense
  superiority, full-wiki/open-domain validity, or broad generator robustness.
- “Supported,” “negative,” “statistically unresolved,” and “no matched
  estimand” are kept distinct in manuscript prose.
- Effects are described as small where appropriate.
- The Gemma result is explicitly deployment-bound and is not a pure
  architecture comparison.
- The abstract, Results, Discussion, Limitations, and Conclusion share the same
  strong-retriever boundary.
- The controller line is described as a separate failed/inconclusive selection
  claim and does not overwrite the static results.
- The title, abstract, introduction, method terminology, experimental
  description, results, discussion, limitations, reproducibility statement,
  conclusion, figure captions, and appendix claim table use a consistent
  method-first ACL/EMNLP Findings narrative.
- The abstract follows a problem–gap–method–result–implication structure and is
  190 words.
- “Evidence completion,” “adaptive granular ball,” “facet hyperedge,” and
  “protected bounded insertion” are defined on first use and used consistently.
- Audit-oriented implementation language is retained only where it is needed
  for reproducibility or evidence provenance.

## 5. Reproducibility audit

PASS for the current evidence/manuscript package.

- `scripts/stage5_pmc_verify_materials.py` remains PASS for the frozen Stage5-PMC
  package.
- The current Stage4E–Stage4I regression files passed 19/19, 27/27, 9/9,
  15/15, and 19/19, respectively: 89/89 total.
- The current Stage5A targeted suite passed 9/9.
- `scripts/stage5r_build_materials.py` performs no retrieval, generation, Gold
  evaluation, bootstrap, model search, or scientific re-analysis.
- `scripts/stage5r_verify_materials.py` is read-only and checks inputs, derived
  bytes, CSV values, tables, citation keys, claim wording, links, license state,
  and the Stage5-PMC verifier.
- Frozen experimental results and the original Stage5-PMC figure source data
  were not modified.

## 6. License and availability audit

PASS with one explicit author-level blocker.

- HotpotQA, MuSiQue, BGE, Qwen, Gemma, and Stage5R package-license statements
  are linked to official sources.
- Original benchmark data, model weights, and large caches are not represented
  as redistributed repository assets.
- The repository contains no project license file. It is therefore accurately
  labelled `NO_REPOSITORY_LICENSE_DECLARED`.
- Selecting a repository/derived-artifact license remains a rights-holder
  decision and blocks final public-reuse wording.

## 7. Submission readiness

The scientific package and the reviewer-responsive anonymous ACL draft are
complete for current evidence, but the package is not ready for a submission
portal. The tracked draft comprises `paper/latex/main.tex` and a visually
inspected PDF; exact identities and build checks are recorded
in [`latex/DRAFT_BUILD_STATUS.md`](latex/DRAFT_BUILD_STATUS.md). The canonical
partial metadata record is
[`AUTHOR_AND_SUBMISSION_METADATA.yaml`](AUTHOR_AND_SUBMISSION_METADATA.yaml).
It confirms the first two Chinese author names and positions, their shared
university affiliation, and the advisor's corresponding-author role. The
following still require human facts or choices:

- English publication names; advisor identity/order/affiliation; exact
  school/department; emails; ORCIDs; and whether additional authors exist;
- funding, conflicts, contributions, acknowledgements, and final AI disclosure;
- a unique target venue and venue-specific format;
- repository and derived-artifact licenses;
- any APC/waiver decision.

The append-only confirmation record is
[`AUTHOR_AND_SUBMISSION_METADATA_HISTORY.md`](AUTHOR_AND_SUBMISSION_METADATA_HISTORY.md);
the detailed remaining checklist is
[`submission/SUBMISSION_BLOCKERS.md`](submission/SUBMISSION_BLOCKERS.md).

## 8. Frozen continuation boundary

```text
CORE_ALGORITHM_EXPERIMENTS_CLOSED
FULL_WIKI_NOT_AUTHORIZED
NEW_GENERATOR_NOT_AUTHORIZED
NEW_STRONG_RETRIEVER_SEARCH_NOT_AUTHORIZED
CONTROLLER_LINE_CLOSED
RESERVATION_LOCKED
STAGE3B_LOCKED
U2_NOT_AUTHORIZED
```

No new algorithm experiment is required by this audit.

## 9. ACL/EMNLP language-revision verification

PASS.

- The revision changes narrative organization and wording only; no dataset,
  ranking, prediction, metric, confidence interval, ablation state, or
  scientific conclusion changed.
- `scripts/stage5r_verify_materials.py` returns
  `STAGE5R_PMR_MATERIALS_VERIFIED` for 26 scientific inputs, 12 source CSVs,
  34 derived files, 20 figure exports, and 23 bibliography entries.
- `scripts/stage5_pmc_verify_materials.py` returns
  `STAGE5_PMC_MATERIALS_VERIFIED`.
- Two clean Tectonic 0.16.9 builds with
  `SOURCE_DATE_EPOCH=1784950406` produced byte-identical 1,582,631-byte PDFs
  with SHA-256
  `90F02983291DAEBE3E6EF1027D0B765FB8849935716E13E8731AF9A710CF8D8C`.
- The 14-page anonymous PDF was inspected on the title/abstract page, method
  figure page, conclusion/back-matter page, and final claim-table page. No
  clipping, overlap, missing panel, unresolved citation/reference, overfull
  box, identity disclosure, `TBD`, `TODO`, `{{CITE: ...}}`, or `??` marker was
  found. Ordinary underfull-box warnings remain non-blocking.
