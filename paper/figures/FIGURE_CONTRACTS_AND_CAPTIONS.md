# Stage5-PMC Figure Contracts, Captions and Trace

## Global contract

- Backend: Python only (`scripts/stage5_pmc_build_figures.py`).
- Primary editable format: SVG with live text.
- Additional exports: PDF, 600-dpi LZW TIFF and 300-dpi PNG.
- Final width: 183 mm (`7.2047 in`) unless the target venue later requires reflow.
- Typography: 7–9 pt publication-scale sans serif; no rasterized labels in SVG/PDF.
- Data boundary: only tracked and SHA-verified Stage4E–Stage4I frozen summaries/telemetry.
- Prohibited: model inference, retrieval rerun, bootstrap rerun, threshold selection, post-hoc significance change or manual movement of data marks.
- Trace: each figure has a CSV in `paper/figures/source_data/`; input/output hashes are in `STAGE5_PMC_FIGURE_MANIFEST.json`.

## Figure 1. Method overview

**Question.** How does HyperGranular-RAG supplement a compact dense ranking without replacing its protected prefix?

**Visual form.** Three-panel schematic: compact dense retrieval; adaptive granular balls with query-aware facet hyperedges; protected bounded insertion.

**Caption.** HyperGranular-RAG as a structured evidence-completion layer. A compact dense backbone ranks sentence units (a). Adaptive granular balls organize local evidence, while query-aware facet hyperedges identify complementary cross-ball candidates without Gold input (b). The final ranking preserves the Dense Top-10 prefix, inserts at most four eligible HGRAG units after the protected prefix, and truncates to an effective Top-20 (c).

**Trace.** `source_data/figure1_method_overview.csv`; frozen method definition in `paper/METHODS_AND_RESULTS_TABLES.md`.

## Figure 2. Frozen answer-quality effects

**Question.** Which Stage4E–Stage4I answer-F1 comparisons are positive, negative or inconclusive?

**Visual form.** Forest plot of paired answer-F1 point differences and frozen 95% bootstrap intervals.

**Caption.** Frozen paired answer-F1 effects across Stage4E–Stage4I. Static q25 repeatedly improves over the historical MiniLM Dense backbone under the frozen Qwen closed-candidate boundaries, and the Stage4H facet comparison and Stage4I placement comparison are positive. The full Stage4H system is lower than BGE strong dense. Generator transfer, protected-sidecar complementarity, the independent protection ablation and the BGE-sidecar facet comparison remain inconclusive. Intervals and decisions are taken directly from independently verified result artifacts; no Stage5 re-estimation was performed.

**Trace.** `source_data/figure2_effect_size_forest.csv`; Stage4E/4F summaries, Stage4G dataset summaries, Stage4H/4I equal-weight summaries.

## Figure 3. Strong-dense placement and evidence displacement

**Question.** How do BGE, Protected and Unprotected rankings differ in answer quality when Protected and Unprotected use the same inserted set, and what Gold evidence is added or displaced?

**Visual form.** Dataset-stratified answer-F1 bars and signed added/displaced Gold transition bars.

**Caption.** Strong-dense placement comparison and post-decision evidence transitions. Protected and Unprotected use the same HGRAG inserted set; only placement differs. Protected placement yields higher answer F1 than Unprotected on both frozen datasets, but Protected remains close to and does not significantly improve over BGE. The same inserted set adds and displaces equal numbers of Gold units under Protected and Unprotected; net Gold change is −8 for HotpotQA and +9 for MuSiQue. The transition panel is descriptive and was not a confirmatory endpoint.

**Trace.** `source_data/figure3a_strong_dense_absolute_metrics.csv`, `source_data/figure3b_evidence_displacement.csv`; Stage4I dataset summary and evidence-transition audit.

## Figure 4. Evidence map

**Question.** What is the final evidence class of each principal scientific statement?

**Visual form.** Categorical evidence map with positive, negative, inconclusive and undefined columns.

**Caption.** Evidence map for the frozen experimental program. Positive evidence is confined to compact-dense answer-quality gains, facet value within the frozen MiniLM system and protected placement for an identical inserted set. The strong-dense replacement comparison is negative. Generator transfer, independent protection, strong-dense sidecar complementarity and BGE-sidecar facet increment are inconclusive. A flat-unit granular-ball comparison is undefined because no fair control was available.

**Trace.** `source_data/figure4_evidence_map.csv`; `paper/EVIDENCE_AND_CLAIM_LEDGER.md`.

## Figure 5. Applicability boundary

**Question.** Where can the frozen evidence support a claim, and where must interpretation stop?

**Visual form.** Boundary-to-interpretation flow diagram.

**Caption.** Applicability boundary of the verified evidence. The supported core scope is structured evidence completion over a compact MiniLM dense backbone in closed-candidate multi-hop QA with Qwen. The method is not competitive with the frozen BGE strong-dense replacement; BGE-sidecar complementarity and transfer to one Gemma mobile-QAT configuration remain uncertain. Full-wiki/open-domain retrieval was not evaluated and is deferred future work.

**Trace.** `source_data/figure5_applicability_boundary.csv`; Stage5-PMC card and evidence ledger.

## Accessibility and QA checklist

- [x] Meaning does not depend on color alone: position, labels, signs and hatching carry the same information.
- [x] Every figure has a concise takeaway and explicit scope.
- [x] Forest plot uses a visible zero reference.
- [x] Inconclusive is not labeled equivalent.
- [x] Strong-dense negative is displayed in the main effect figure.
- [x] Evidence displacement is labeled post-decision descriptive.
- [x] Full-wiki is labeled not evaluated/deferred.
- [x] SVG keeps text editable.
- [x] PNG previews were visually inspected at generated resolution.
