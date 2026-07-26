# Stage5R Manuscript Blueprint

Status: `WEAK_REJECT_REVISION_COMPLETE`

## Recommended title

**HyperGranular-RAG: Structured Evidence Completion for Compact Multi-Hop
Retrieval**

This title foregrounds the method and its intended compact-retriever setting.
The strong-retriever result and external-validity limits remain explicit in the
abstract, Results, Discussion, and Limitations rather than dominating the
paper's first impression.

## Bounded alternatives

1. **HyperGranular-RAG: Structured Evidence Completion under Fixed Retrieval
   Budgets**
2. **Protected Higher-Order Evidence Completion for Compact Dense Retrieval**

## Central thesis

> HyperGranular-RAG is a protected higher-order evidence-completion framework
> for constrained multi-hop retrieval. It provides repeatable answer-F1 gains
> over a compact MiniLM backbone across pre-specified HotpotQA and MuSiQue
> evaluations. Controlled component studies support facet-conditioned selection
> and fixed-set protected placement, while the BGE studies show that the
> method's marginal value depends on the strength and representation space of
> the base retriever. Together, these results distinguish evidence addition,
> evidence placement, and end-to-end answer utility.

## Claim hierarchy

### Core positive claims

- Static HGRAG improves the compact MiniLM dense Top-20 backbone in three
  independent Qwen evaluations, with answer-F1 differences between
  `+0.01140` and `+0.01478`.
- Facet-conditioned selection exceeds the fixed centroid-only NoFacet ball
  selector in the Stage4H MiniLM system:
  `+0.01336 [0.00341, 0.02343]` for Full−NoFacet. This does not establish
  granular-ball necessity or superiority over an untested generic
  diversity/coverage selector.
- When the Stage4I inserted set is held constant, protected placement exceeds
  unprotected placement: `+0.01122 [0.00129, 0.02104]`.

### Strong-retriever boundary claims

- Original Full is below strong BGE:
  `-0.03998 [-0.05393, -0.02621]`.
- The MiniLM-derived sidecar remains statistically unresolved relative to BGE:
  `-0.00256 [-0.00998, 0.00458]`.
- BGE-native Protected remains statistically unresolved relative to BGE:
  `-0.003046 [-0.006880, 0.000631]`.
- Stage5A placement and facet contrasts are also statistically unresolved; Stage4I
  component support is therefore not transported into BGE-native space.

### Required interpretive distinction

Evidence addition, evidence placement, and end-to-end answer utility are
separate empirical objects. Stage5A records net Gold `+1` on each dataset while
the answer-F1 point estimates are negative and uncertain.

## Evidence roles

- **Confirmation:** all pre-specified Stage4E–Stage5A primary comparisons.
- **Development only:** Stage5A `C10` selection difference `+0.003143`.
- **Post-decision descriptive:** Gold added/displaced/net audits.
- **Not evaluated:** full-wiki/open-domain.
- **Not fairly defined:** flat granular-ball ablation.
- **Not established:** granular-ball necessity.
- **Not tested:** facet hyperedges versus a matched generic
  diversity/coverage selector.

## Main-text allocation

1. Introduction — problem, contribution, bounded thesis.
2. Related Work — five scientific families, not a paper list.
3. Method — common formulation and three integration variants.
4. Experiments — evaluation settings, development–confirmation separation,
   statistics, and label access.
5. Results — evidence hierarchy rather than project chronology.
6. Discussion — compact-retriever benefit, strong-retriever contraction,
   coverage versus utility, and failure modes.
7. Limitations — all external-validity and undefined-control boundaries.
8. Reproducibility — identities, deterministic evaluations, and artifact
   traceability.
9. Conclusion — contribution, evidence scope, and implications.

Controller and diagnostic work is summarized in the main Discussion and
documented in an appendix failure-analysis table.

## Completion boundary

The scientific manuscript is complete for current evidence. Author identities,
funding, conflicts, acknowledgements, a unique venue, and final venue formatting
remain explicit submission metadata blockers. Therefore the package status is
`SUBMISSION_METADATA_PENDING`, not `SUBMISSION_READY`.
