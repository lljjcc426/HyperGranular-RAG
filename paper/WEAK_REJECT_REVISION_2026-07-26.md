# Weak-Reject Revision Record

Revision date: 2026-07-26

Status:

```text
WEAK_REJECT_REVISION_COMPLETE
SCIENTIFIC_EVIDENCE_CUTOFF = STAGE5A_BNH
NO_NEW_EXPERIMENTAL_RESULT
SUBMISSION_METADATA_PENDING
SUBMISSION_READY = FALSE
```

## 1. Scope

This revision responds to an external `Weak Reject` assessment of the anonymous
ACL draft. It changes manuscript framing, method detail, result visibility,
failure analysis, and claim boundaries. It does not rerun retrieval,
generation, Gold evaluation, bootstrap, or model selection, and it does not
modify any frozen Stage4E--Stage5A result.

The reviewer recognized the repeated compact-MiniLM gains and the manuscript's
reporting integrity, but identified four claims that the current evidence does
not establish:

1. granular balls are a necessary component;
2. facet hyperedges outperform generic diversity/coverage selection;
3. the method improves a modern strong retriever;
4. the method has demonstrated scalable open-domain RAG value.

The revision does not manufacture evidence for these claims. It states each
boundary explicitly and narrows the supported claims to the exact frozen
comparisons.

## 2. Review-to-revision mapping

| Review issue | Revision | Current evidential status |
|---|---|---|
| Granular-ball necessity is unproven | The abstract, component analysis, limitations, conclusion, and claim--evidence table now state that the flat granular-ball control was not fairly defined and necessity is not established. The method section now gives the exact ball construction and split rules. | `NOT_ESTABLISHED`; a scientifically matched flat control would require a new experiment |
| Hyperedge superiority over simple diversity/coverage is unproven | The related-work/control paragraph now defines NoFacet precisely as centroid-only ball selection. Every component claim is restricted to facet-conditioned selection versus that comparator. Generic relevance--diversity, maximum-coverage, or other simple selectors are explicitly untested. | `NOT_TESTED`; no matched alternative selector exists in the frozen program |
| Improvement over a modern strong retriever is unproven | The main Results now display the BGE negative result together with BM25 and Dense--BM25 hybrid comparisons, the BGE sidecar result, and BGE-native confirmation. The abstract and conclusion retain the negative/inconclusive strong-retriever boundary. | Original Full versus BGE is `NEGATIVE`; sidecar and BGE-native increments are `INCONCLUSIVE` |
| Open-domain scalability/value is unproven | The abstract, limitations, conclusion, and claim--evidence table now state that all answer-quality evaluations are closed-candidate and that full-wiki indexing, ANN recall, corpus noise, and open-domain operation were not evaluated. | `NOT_TESTED` |

## 3. Requested manuscript improvements

### Stronger baseline visibility

The revised main Results report all available frozen Stage4H baseline evidence:

- Full minus BGE strong dense:
  `-0.03998 [-0.05393, -0.02621]`, `NEGATIVE`;
- Full minus BM25:
  `-0.00755 [-0.02259, 0.00773]`, `INCONCLUSIVE`;
- Full minus Dense--BM25 hybrid:
  `-0.00320 [-0.01591, 0.00942]`, `INCONCLUSIVE`;
- cross-space Protected minus BGE:
  `-0.00256 [-0.00998, 0.00458]`, `INCONCLUSIVE`;
- BGE-native Protected minus BGE:
  `-0.00305 [-0.00688, 0.00063]`, `INCONCLUSIVE`.

These rows do not support a strong-retriever improvement claim.

### Component evidence completeness

The revised component table keeps all available frozen contrasts together:

- compact Full minus NoFacet: supported;
- compact Full minus NoProtection: inconclusive;
- sidecar Protected minus Unprotected: supported;
- sidecar Protected minus NoFacet: inconclusive;
- BGE-native placement and facet increments: inconclusive;
- flat granular-ball control: not fairly defined.

The supported NoFacet contrast is not relabelled as a generic hyperedge
superiority result.

### Method precision

The manuscript now specifies:

- normalized ball centroids, cosine distance, radius, and compactness;
- split depth, size, radius, seed selection, assignment, and minimum-child
  rules;
- the complete facet score with all fixed coefficients;
- seed count, eligibility gates, redundancy gate, candidate order, and
  expansion budget;
- the protected prefix, q25 floor, insertion cap, and effective Top-20 rule.

### Failure analysis

The main Discussion and a supplementary failure-audit table now distinguish:

- repeated static expansion gains;
- the failed resource controller, whose retained set contained harm more often
  than gain;
- the reversed query-score direction;
- the below-gate candidate learnability probe;
- strong-retriever evidence displacement that did not yield positive
  answer-quality change.

These mechanism audits remain exploratory or post-decision descriptive where
applicable.

## 4. Remaining scientific work

The following would require a new scientific protocol and new data execution;
they are not silently treated as completed:

- a matched flat-unit or alternative local-structure control that isolates
  granular-ball necessity;
- pre-specified relevance--diversity, maximum-coverage, or other simple
  completion selectors under the same candidate and Top-k budget;
- a fresh strong-retriever confirmation family rather than post-hoc search;
- full-wiki/open-domain indexing, ANN recall, latency/storage, and end-to-end
  answer-quality evaluation.

The current manuscript is therefore a bounded positive/negative Findings-style
study, not a universal strong-retriever or open-domain improvement claim.
