# Stage5R Manuscript Blueprint

Status: `CURRENT_EVIDENCE_MANUSCRIPT_COMPLETE`

## Recommended title

**When Structured Evidence Completion Helps—and When It Does Not: A Verified
Study of HyperGranular Retrieval-Augmented Generation**

This is the recommended title because it exposes both the positive compact-dense
evidence and the strong-retriever boundary without implying SOTA, universal
improvement, or open-domain validation.

## Bounded alternatives

1. **Protected High-Order Evidence Completion under Strong-Retriever
   Saturation**
2. **HyperGranular-RAG: Reproducible Gains for Compact Dense Retrieval and
   Boundaries under Strong Retrievers**

## Central thesis

> HyperGranular-RAG is a protected high-order evidence-completion framework for
> constrained multi-hop retrieval. It repeatedly improves a compact historical
> MiniLM dense backbone across frozen HotpotQA and MuSiQue boundaries. However,
> the full method underperforms a pre-specified BGE strong-dense retriever,
> while neither cross-space sidecar integration nor BGE-native reconstruction
> establishes incremental answer-quality gains over BGE. These results identify
> a strong-retriever boundary for the tested structural expansion and
> demonstrate that evidence addition, evidence placement, and end-to-end answer
> utility are distinct phenomena.

## Claim hierarchy

### Core positive claims

- Static HGRAG improves the historical MiniLM dense Top-20 backbone on three
  independent frozen Qwen boundaries, with answer-F1 differences between
  `+0.01140` and `+0.01478`.
- Removing facet hyperedges in the frozen Stage4H MiniLM system reduces
  answer F1: `+0.01336 [0.00341, 0.02343]` for Full−NoFacet.
- When the Stage4I inserted set is held constant, protected placement exceeds
  unprotected placement: `+0.01122 [0.00129, 0.02104]`.

### Strong-retriever boundary claims

- Original Full is below strong BGE:
  `-0.03998 [-0.05393, -0.02621]`.
- The MiniLM-derived sidecar does not establish an increment over BGE:
  `-0.00256 [-0.00998, 0.00458]`, inconclusive.
- BGE-native Protected does not establish an increment over BGE:
  `-0.003046 [-0.006880, 0.000631]`, inconclusive.
- Stage5A placement and facet contrasts are also inconclusive; Stage4I
  component support is therefore not transported into BGE-native space.

### Required interpretive distinction

Evidence addition, evidence placement, and end-to-end answer utility are
separate empirical objects. Stage5A records net Gold `+1` on each dataset while
the answer-F1 point estimates are negative and uncertain.

## Evidence roles

- **Confirmation:** all frozen Stage4E–Stage5A primary comparisons.
- **Development only:** Stage5A `C10` selection difference `+0.003143`.
- **Post-decision descriptive:** Gold added/displaced/net audits.
- **Not evaluated:** full-wiki/open-domain.
- **Not fairly defined:** flat granular-ball ablation.

## Main-text allocation

1. Introduction — problem, contribution, bounded thesis.
2. Related Work — five scientific families, not a paper list.
3. Method — common formulation and three integration variants.
4. Experimental Protocol — frozen boundaries, separation, statistics, Gold
   isolation.
5. Results — evidence hierarchy rather than project chronology.
6. Discussion — compact benefit, strong-retriever saturation, coverage versus
   utility, stopping rule.
7. Limitations — all external-validity and undefined-control boundaries.
8. Reproducibility and Integrity — identities, deterministic transactions,
   artifact traceability.
9. Conclusion — bounded scientific result.

Controller and diagnostic work is limited to one paragraph in the main text and
is documented in the supplementary material.

## Completion boundary

The scientific manuscript is complete for current evidence. Author identities,
funding, conflicts, acknowledgements, a unique venue, and final venue formatting
remain explicit submission metadata blockers. Therefore the package status is
`SUBMISSION_METADATA_PENDING`, not `SUBMISSION_READY`.
