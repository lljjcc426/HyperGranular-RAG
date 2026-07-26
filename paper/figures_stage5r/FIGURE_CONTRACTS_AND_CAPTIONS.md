# Stage5R Figure Contracts and Captions

## Figure contract

- **Core conclusion:** structured evidence completion repeatedly improves the
  compact MiniLM retriever, whereas the evaluated strong-BGE extensions do not
  establish incremental answer-quality gains.
- **Archetype:** Figure 2 is a quantitative hero composite; Figures 3 and 4 are
  quantitative grids; Figure 5 is an asymmetric qualitative comparison.
- **Backend:** Python/Matplotlib only.
- **Target:** ACL/EMNLP Findings, double-column figures at approximately 175 mm.
- **Statistics:** confirmatory answer-F1 panels report the frozen paired 10,000
  sample bootstrap 95% confidence intervals. Mechanism and qualitative panels
  are explicitly descriptive.
- **Reviewer risk:** Stage4H, Stage4I, and Stage5A strong-retriever rows are
  separate frozen boundaries and are never pooled or connected as a monotonic
  retriever-strength experiment.

## Figure 1

**Overview of HyperGranular-RAG and the evaluated retrieval variants.**
Candidate units are ranked by a fixed dense retriever, organized into adaptive
granular balls, connected through query-aware facet hyperedges, and inserted
under a protected, bounded Top-k policy before answer generation. Compact,
cross-space sidecar, and BGE-native variants are evaluated separately rather
than pooled.

## Figure 2

**Main performance and paired answer-F1 effects.** Panels a and b use paired
dumbbells to compare absolute answer F1 only within each frozen boundary.
Panel c reports all confirmatory paired answer-F1 differences with 95%
bootstrap confidence intervals. Hollow points denote intervals crossing zero;
they are not equivalence claims. Strong-retriever boundaries are shown as
separate settings rather than a connected trend.

## Figure 3

**Coverage, answer utility, components, and evidence turnover.** Panels a and b
relate matched changes in CR@20 and ER@20 to answer-F1 changes without fitting a
trend line. Panel c reports matched component effects with frozen 95%
confidence intervals. Panel d normalizes post-decision added and displaced
Gold evidence events per 1,000 queries; raw counts and query denominators remain
in the source CSV. Panel d is descriptive and did not control selection.

## Figure 4

**Gold-free retrieval mechanism.** Panels a and b show dataset-equal-weight
query percentages for facet-hyperedge selection, insertion, query-facet supply,
and eligible structural candidates. Panel c reports bounded insertion-count
distributions separately for compact, sidecar, and BGE-native settings. Panel d
decomposes sidecar-eligible candidates by overlap with BGE Top-20. These panels
describe frozen retrieval behavior and do not establish causal mediation.

## Figure 5

**Representative success and failure cases.** The success case requires a
positive Full-minus-Dense answer-F1 change, a CR@20 increase, and insertion of a
supporting unit. The failure case requires a negative Original-Full-minus-BGE
answer-F1 change and displacement of a supporting unit. Within each eligible
HotpotQA sentence-level event set, the query closest to the median answer-F1
change is selected, with query ID as a deterministic tie-break. These examples
are post-decision descriptive illustrations, not confirmatory evidence. The
source CSV preserves the frozen text verbatim; the rendered panel replaces
Khmer-script spans with a neutral script label when the publication font lacks
those glyphs.

Each figure is exported as editable SVG, PDF, 600-dpi TIFF, and 300-dpi PNG.
Every plotted value has a CSV source file, and every export is byte/SHA bound in
`STAGE5R_FIGURE_MANIFEST.json`.
