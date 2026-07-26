# Stage5R Figure Contracts and Captions

## Figure 1

**Verified HyperGranular-RAG workflow and study boundaries.** Candidate units
are ranked by a frozen dense retriever, organized into adaptive granular balls,
connected through query-aware facet hyperedges, and inserted under a protected,
bounded Top-k policy before frozen answer generation. Compact, cross-space
sidecar, and BGE-native variants are evaluated separately rather than pooled.
The right column distinguishes supported, negative, inconclusive, and
not-fairly-defined outcomes, while the bottom row summarizes the scientific
controls applied to the verified experiments.

## Figure 2

**Frozen answer-F1 effect sizes.** Points are paired answer-F1 differences and
bars are the pre-specified 95% bootstrap confidence intervals. The zero line is
shown explicitly and the x-axis is not truncated around positive effects.
`INCONCLUSIVE` means that the interval crosses zero; it is not an equivalence
claim.

## Figure 3

**Strong-retriever boundary and evidence displacement.** Panel A compares each
structural method only with BGE inside its own frozen Stage4H, Stage4I, or
Stage5A boundary; the three groups are not pooled or treated as a common
head-to-head sample. Panel B reports post-decision descriptive Gold evidence
added and displaced. These counts did not control selection or advancement and
do not replace end-to-end answer evaluation.

## Figure 4

**Evidence-state map.** Supported, negative, inconclusive, and not-fairly-defined
outcomes are kept distinct. Component findings are system-dependent and are not
transported across semantic spaces without confirmation.

## Figure 5

**Applicability boundary.** Repeated small gains are established only for the
historical compact MiniLM backbone under closed-candidate Top-20 evaluation.
The original system is negative against strong BGE, the tested sidecar and
BGE-native extensions are inconclusive, and full-wiki/open-domain operation was
not evaluated.

Each figure is exported as editable SVG, PDF, 600-dpi TIFF, and 300-dpi PNG.
Every plotted value has a CSV source file, and every export is byte/SHA bound in
`STAGE5R_FIGURE_MANIFEST.json`.
