# Citation–Claim Map

Status: `CLAIM_AND_CITATION_BINDING_COMPLETE`

This map distinguishes external-literature support from project evidence.
External citations establish prior methods, datasets, or reporting principles;
they do not support HyperGranular-RAG effect sizes. All project results are
bound to frozen repository artifacts in
[`EVIDENCE_AND_CLAIM_LEDGER.md`](../EVIDENCE_AND_CLAIM_LEDGER.md).

| Manuscript claim | Citation keys | What the sources support | What they do not support |
|---|---|---|---|
| Retrieval-augmented generation conditions generation on non-parametric evidence. | `lewis2020rag`, `guu2020realm`, `ram2023incontext` | Established retrieval-augmented language-model families. | Any HGRAG gain or strong-retriever result. |
| Dense passage retrieval is a standard learned retrieval baseline. | `karpukhin2020dpr` | Dense dual-encoder passage retrieval. | That MiniLM is universally weak or BGE universally superior. |
| Multi-hop QA requires retrieving multiple evidence pieces. | `yang2018hotpotqa`, `trivedi2022musique` | Dataset definitions and multi-hop evidence motivation. | Open-domain/full-wiki validity of this study. |
| Iterative retrievers construct evidence chains or interleave retrieval and reasoning. | `xiong2021mdr`, `zhao2021beamdr`, `sun2019pullnet`, `trivedi2023ircot` | Representative iterative and multi-step retrieval mechanisms. | Direct comparative performance versus HGRAG. |
| Structure-aware retrieval can use hierarchical or graph organization. | `sarthi2024raptor`, `gutierrez2024hipporag`, `mavromatis2025gnnrag`, `edge2024graphrag` | Representative tree/graph retrieval designs. | That HGRAG is better than GraphRAG families. |
| Hypergraphs express relations involving more than pairwise adjacency. | `feng2019hgnn` | General high-order relation motivation. | The correctness or superiority of the specific facet-hyperedge construction. |
| Granular-ball computing supplies an adaptive coarse-to-fine grouping precedent. | `xia2019granularball` | Origin of granular-ball computing. | A confirmed independent granular-ball effect in this QA system. |
| Evidence quantity and position need not map directly to generator utility. | `liu2024lostmiddle`, `xu2024recomp`, `izacard2021fid`, `ram2023incontext` | Context position, selection/compression, and retrieval–generation coupling. | A causal explanation for the observed HGRAG outcomes. |
| Provenance and artifact transparency are important for knowledge-intensive evaluation. | `petroni2021kilt`, `pineau2021reproducibility` | Provenance-aware evaluation and reproducibility practices. | That the project governance itself guarantees external validity. |
| An interval crossing zero should not be rewritten as equivalence or absence of effect. | `amrhein2019retire` | General caution about dichotomous statistical language. | A formal equivalence test or power guarantee. |
| BGE is the pre-specified strong embedding family used here. | `xiao2023bge` plus frozen model card/commit | Background and identity of the BGE family. | Cross-device efficiency or universal strong-retriever ranking. |

## In-text citation audit rules

1. Every `[@key]` used in the manuscript must exist in
   [`verified_references.bib`](verified_references.bib).
2. Project numbers are never attributed to external literature.
3. Preprints are named as preprints.
4. A citation to related work is not a claim of a fair head-to-head comparison.
5. No citation is used to convert an inconclusive confidence interval into an
   equivalence claim.
