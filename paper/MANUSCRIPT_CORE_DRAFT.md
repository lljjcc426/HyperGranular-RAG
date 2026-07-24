# Protected High-Order Evidence Completion for Compact Dense Multi-Hop Retrieval

Draft status:

```text
STAGE5_PMC_INTERNAL_EVIDENCE_DRAFT
EXTERNAL_CITATIONS_NOT_YET_BOUND
NOT_SUBMISSION_READY
```

Curly-brace citation slots such as `{{CITE: ...}}` are unresolved literature requirements, not references. They must be replaced only after source verification.

## Abstract

Dense retrieval provides a strong relevance ordering for retrieval-augmented generation, but a constrained Top-k context may still omit complementary passages required for multi-hop reasoning. We study HyperGranular-RAG, a Gold-free structured evidence-completion layer that organizes candidate sentence units into adaptive granular balls, links complementary balls with query-aware facet hyperedges, and inserts a bounded number of expansion units after a protected dense prefix. Across frozen closed-candidate HotpotQA and MuSiQue evaluations using Qwen2.5-1.5B-Instruct, the static method repeatedly improved answer F1 over a historical MiniLM dense backbone. The paired answer-F1 difference was +0.01478 [0.00020, 0.02988] on a 1,000-query HotpotQA boundary and +0.01140 [0.00450, 0.01835] on a 3,000-query MuSiQue boundary. A separate component evaluation again supported the full method over MiniLM Dense and supported the incremental value of facet hyperedges within the frozen system. These gains did not extend to a pre-specified BGE strong-dense baseline: the full method was lower by −0.03998 [−0.05393, −0.02621] in a dataset-equal-weight comparison. Adding the frozen HGRAG system as a BGE sidecar yielded inconclusive complementarity, whereas protected placement outperformed unprotected placement for an identical inserted set by +0.01122 [0.00129, 0.02104]. Transfer to one official Gemma mobile-QAT configuration was also inconclusive. The evidence therefore supports HyperGranular-RAG as bounded evidence completion for compact dense backbones, not as a universal replacement for strong dense retrieval.

## 1. Introduction

Retrieval-augmented generation depends on two linked but non-identical properties: the retriever must rank individually relevant items, and the selected context must jointly contain the evidence needed to answer the question. This distinction is especially important for multi-hop questions, where no single sentence or paragraph may express the complete reasoning chain. Dense retrievers are effective relevance models, yet a fixed Top-k ranking can omit a complementary item even when several locally similar items occupy the context budget. {{CITE: dense retrieval for open-domain and multi-hop QA}} {{CITE: retrieval-augmented generation under constrained context}}

Structure-aware retrieval offers a possible remedy by representing relations among candidate units. Graph and hypergraph approaches can connect evidence that is not adjacent in a single relevance ordering, but expansion also creates a displacement risk: every inserted unit may remove another unit from a fixed-size context. {{CITE: graph or hypergraph retrieval for multi-hop QA}} {{CITE: evidence aggregation and context displacement in RAG}} A useful structure-aware method must therefore answer two questions. First, can it identify complementary evidence without using answer labels or supporting-fact annotations at retrieval time? Second, can it place that evidence without destabilizing the strongest part of the base ranking?

We investigate these questions through HyperGranular-RAG, a structured evidence-completion layer for compact dense retrieval backbones. The method constructs adaptive granular balls over sentence-unit embeddings, derives query-aware facet hyperedges across balls, and inserts at most four eligible expansion units after a protected Dense Top-10 prefix. The output remains bounded by an effective Top-20. Candidate construction, hyperedge selection and ranking are Gold-free.

Our evaluation is designed around claim boundaries rather than a single favorable benchmark. We first test whether static protected expansion improves answer quality over a historical MiniLM Dense backbone across frozen HotpotQA and MuSiQue closed-candidate boundaries. We then test component value, an independently selected BGE strong-dense baseline, one additional generator configuration, and a sidecar formulation that preserves BGE as the primary ranking. All positive, negative, inconclusive and undefined comparisons are retained.

The evidence supports three bounded contributions. First, static HyperGranular-RAG repeatedly improves answer F1 over the compact MiniLM Dense backbone under the frozen Qwen boundaries. Second, facet hyperedges have incremental value within the frozen MiniLM system. Third, when the inserted candidate set is held identical, protected placement is better than unprotected placement. The same evidence also establishes clear limits. The full system is inferior to BGE strong dense, BGE-sidecar complementarity is inconclusive, transfer to one Gemma mobile-QAT configuration is inconclusive, and a fair flat-unit control for isolating granular-ball structure was not available. We therefore do not claim universal retrieval superiority, full-wiki effectiveness, broad generator robustness or an independently confirmed granular-ball contribution.

## 2. Method

### 2.1 Candidate units and compact dense retrieval

For each question \(q\), let \(U_q=\{u_i\}\) be its closed candidate set of sentence units. The frozen compact dense backbone encodes the question and each `title + sentence` unit with `sentence-transformers/all-MiniLM-L6-v2`. L2-normalized embeddings are ranked by cosine similarity, with `unit_id` as the deterministic tie-break. The Dense baseline returns

\[
K_q=\min(20, |U_q|)
\]

units.

This study separates the static method from the unsuccessful adaptive-controller branch. No U1 score, learned candidate selector, Gold label, answer text or supporting-evidence annotation enters the static ranking.

### 2.2 Adaptive granular balls

The candidate embedding set starts as a single root ball. A deterministic recursive procedure calculates a normalized centroid, the cosine-distance radius and a compactness value for each ball. A ball can split only when it satisfies the frozen depth, size and radius conditions and both resulting children contain at least two units. Two deterministic remote seeds define the candidate partition, and a split is rejected if it produces an undersized child.

The granular-ball representation has two roles. It preserves local groups of semantically related sentence units, and it supplies the nodes over which higher-order facet relations are defined. Construction uses only candidate embeddings and metadata available before Gold evaluation.

### 2.3 Query-aware facet hyperedges

Each ball contributes content terms from its titles and sentences after frozen token filtering. Query terms shared with a ball define its query-relevant facets. The two balls with the highest query-to-centroid cosine are treated as seeds. A non-seed ball becomes an expansion candidate only if it introduces a new query term and passes frozen size, similarity, redundancy and units-per-new-term gates.

Candidate facet hyperedges are scored by a frozen weighted combination of new-facet coverage, total facet coverage, ball similarity, seed diversity, redundancy and size. At most two edges or balls are selected. Within a selected ball, sentence units retain the original MiniLM cosine order; the facet score does not create an additional per-unit score bonus.

### 2.4 Protected bounded insertion

The first ten unique Dense units form a protected prefix. Expansion candidates must exceed the frozen MiniLM q25 floor of 0.1957079917192459. Up to four candidates not already present in the protected prefix are then inserted. Remaining Dense units preserve their original order, and additional expansion units are used only if the effective Top-k is not filled. The final ranking is truncated to \(K_q\).

This placement separates evidence completion from base-rank replacement. It prevents expansion from displacing the Dense Top-10 while preserving a fixed context budget.

## 3. Experimental design

### 3.1 Data boundaries

The confirmatory answer-quality program uses deterministic, frozen, closed-candidate boundaries from HotpotQA and MuSiQue. Each later boundary was selected by ID-only hashing and verified to have zero overlap with earlier official project IDs. The candidate pools are supplied by the benchmark instances; the experiments do not retrieve from full Wikipedia or an open-domain index.

The principal compact-dense evaluations include 1,000 HotpotQA queries and 3,000 MuSiQue queries. Component and strong-baseline evaluations use a separate HotpotQA 1,000 plus MuSiQue 1,500 boundary. The strong-dense sidecar study uses another zero-overlap HotpotQA 1,000 plus MuSiQue 1,500 boundary.

### 3.2 Retrieval and generator conditions

The primary comparisons use MiniLM Dense Top-20 and static HyperGranular-RAG Top-20 with a frozen Qwen2.5-1.5B-Instruct FP16 generator, a fixed short-answer RAG prompt and a 4,096-token input cap. BGE large-en-v1.5 is the pre-specified strong-dense baseline in the component and sidecar studies.

Generator transfer is evaluated with one additional pre-specified configuration: `google/gemma-4-E2B-it-qat-mobile-transformers` in the official mobile-QAT format. The Qwen and Gemma executions therefore do not isolate pure model architecture. The generator-selection development result is reported only within the RTX 4060 Laptop 8GB, fixed-prompt, 4,096-token and deployable-format boundary.

### 3.3 Endpoints and integrity controls

The primary answer endpoint is the paired query-level answer-F1 difference. Answer exact match, retrieval complete recall at 20 and evidence recall at 20 are supporting endpoints. Frozen comparisons use 10,000 query bootstrap samples and stage-specific pre-registered decision rules. A non-significant interval is interpreted as inconclusive, never as equivalence.

Retrieval, prompt construction and generation are completed before Gold access. Independent verifiers reconstruct query identity, metrics, bootstrap results and scientific decisions. Stage4E and Stage4F use full byte-identical main/rerun transactions. Stage4G–Stage4I use pre-hash stratified deterministic subsets that reproduce the corresponding main outputs exactly. All formal calls completed without generation failure.

## 4. Results

### 4.1 Static evidence completion repeatedly improves over compact MiniLM Dense

On the frozen 1,000-query HotpotQA boundary, Dense and static HyperGranular-RAG achieved answer F1 values of 0.42150 and 0.43628. The paired difference was +0.01478 [0.00020, 0.02988]. Exact match increased from 0.356 to 0.366, with a paired difference of +0.01000 [−0.00500, 0.02500]. Retrieval CR@20 increased from 0.737 to 0.798, and ER@20 increased from 0.87860 to 0.90818. The frozen decision was `STATIC_HGRAG_E2E_SUPPORTED`. The F1 interval lower bound is close to zero, so the result supports a small, boundary-specific gain rather than a large improvement.

The MuSiQue replication preserved this direction on 3,000 new queries. Dense and static HyperGranular-RAG achieved answer F1 values of 0.13595 and 0.14735, respectively, for a paired difference of +0.01140 [0.00450, 0.01835]. Exact match increased by +0.01000 [0.00333, 0.01667], and supporting-paragraph CR@20 increased from 0.589 to 0.650. The frozen decision was `STATIC_HGRAG_XDR_SUPPORTED`.

A later component boundary again supported the full method over MiniLM Dense. The dataset-equal-weight answer-F1 difference was +0.01357 [0.00491, 0.02233]. Dataset-specific differences were +0.02070 [0.00570, 0.03565] on HotpotQA and +0.00644 [−0.00301, 0.01568] on MuSiQue. Thus, the combined result was supported even though the later MuSiQue dataset-specific interval crossed zero.

### 4.2 Facet value is supported within the frozen MiniLM system, while other component claims remain bounded

Removing facet hyperedges from the Stage4H system reduced the dataset-equal-weight answer F1. The Full−NoFacet difference was +0.01336 [0.00341, 0.02343], supporting an incremental contribution of facet hyperedges within that frozen system.

The independent protected-insertion ablation was not decisive. Full−NoProtection was +0.00354 [−0.00675, 0.01389]. This interval neither confirms a positive contribution nor establishes no difference. A flat-unit replacement intended to isolate granular-ball structure could not be fairly defined because the counterfactual changed more than the targeted component. It is therefore recorded as `NOT_FAIRLY_DEFINED`, and we make no independent granular-ball efficacy claim.

### 4.3 The full compact-backbone system is inferior to BGE strong dense

The positive MiniLM comparisons did not extend to the pre-specified strong-dense baseline. In Stage4H, Full−BGE produced a dataset-equal-weight answer-F1 difference of −0.03998 [−0.05393, −0.02621] and an exact-match difference of −0.04067 [−0.05483, −0.02683]. The frozen decision was `FULL_METHOD_VS_STRONG_DENSE_NEGATIVE`.

This result changes the interpretation of the method. HyperGranular-RAG can supplement a compact historical dense backbone under the tested boundaries, but the frozen full system is not competitive with BGE as a standalone retrieval ranking. The MiniLM-positive results cannot be used to claim superiority over strong dense retrieval.

### 4.4 BGE-sidecar complementarity is inconclusive, but protected placement matters

We next preserved BGE as the primary ranking and used MiniLM-HGRAG as a separate sidecar. In the dataset-equal-weight primary comparison, Protected sidecar−BGE was −0.00256 [−0.00998, 0.00458] for answer F1 and −0.00233 [−0.00983, 0.00467] for exact match. The frozen decision was `STRONG_DENSE_COMPLEMENTARITY_INCONCLUSIVE`. These intervals do not establish improvement, harm or equivalence.

Protected and Unprotected sidecar rankings used exactly the same inserted candidate set and differed only in placement. Protected−Unprotected was +0.01122 [0.00129, 0.02104] for answer F1 and +0.01300 [0.00333, 0.02283] for exact match. The supporting decision was `PROTECTED_PLACEMENT_SUPPORTED`. Unprotected−BGE was −0.01379 [−0.02440, −0.00339], which helps explain why placement matters but does not create a separate post-hoc advancement claim.

A post-decision evidence transition audit illustrates the displacement tradeoff. Protected insertion added 21 and displaced 29 Gold units on HotpotQA, for a net change of −8. On MuSiQue it added 59 and displaced 50, for a net change of +9. Protected and Unprotected have identical transition counts because their inserted sets are identical. Their answer-quality difference therefore reflects placement and context use rather than different evidence membership. These transition counts are descriptive and were not confirmatory endpoints.

Facet value did not transfer clearly to the BGE-sidecar setting. Protected−NoFacet was −0.00743 [−0.01616, 0.00132], giving the frozen supporting decision `BGE_FACET_INCREMENT_INCONCLUSIVE`.

### 4.5 Transfer to one additional generator configuration is inconclusive

With the official Gemma mobile-QAT configuration, the HotpotQA Static-q25−Dense answer-F1 difference was +0.01265 [−0.00220, 0.02744], whereas the MuSiQue difference was −0.00232 [−0.00685, 0.00208]. The dataset-equal-weight difference was +0.00516 [−0.00262, 0.01295], below the pre-registered support threshold and crossing zero. The frozen decision was `GENERATOR_TRANSFER_INCONCLUSIVE`.

This result does not show that Gemma is unsuitable for RAG, that Qwen has a universally stronger base architecture, or that either model is more efficient on all hardware. The Gemma architecture, official mobile-QAT format and numeric representation are not separable in this execution.

### 4.6 Efficiency and reproducibility

The two primary compact-dense replications required only small context changes. Mean inserted units per query were 1.930 on Stage4E HotpotQA and 2.411 on Stage4F MuSiQue. Mean input tokens changed from 899.19 to 901.04 and from 880.61 to 884.09, respectively.

Across Stage4E–Stage4I, the frozen main transactions contained 2,000, 6,000, 8,000, 17,500 and 10,000 generation calls, all with zero failed calls. Observed wall times and GPU memory are reported in Table 4, but they are not used for pure model-architecture ranking because the generator format, method count and transaction structure differ. Full-rerun or pre-hash-subset determinism and independent verification passed for every included stage.

## 5. Discussion

The repeated MiniLM result suggests that structured expansion can repair evidence omissions left by a compact dense ranker. The gains are small but consistent across multiple frozen boundaries. This pattern is compatible with an evidence-completion interpretation: most queries do not change, but a limited subset receives a complementary unit that improves the generator's answer.

Facet hyperedges appear useful within the frozen MiniLM system because they represent cross-ball query facets that are not captured by a single local ranking. However, the BGE-sidecar facet comparison is inconclusive. A stronger dense backbone may already encode part of the relational signal, or the MiniLM-defined sidecar candidates may not align with BGE's remaining errors. The current evidence cannot distinguish these explanations.

The strong-dense and sidecar studies also show why candidate identity and candidate placement must be separated. The Stage4I Protected and Unprotected arms contain the same inserted units, yet Protected performs better. The difference is not evidence discovery but control of displacement within a fixed context. Conversely, good placement cannot make an unhelpful candidate set complementary to BGE. The primary Protected−BGE comparison remains inconclusive.

The unsuccessful adaptive-controller branch reinforces a second distinction: proving that a static expansion helps on average does not imply that a Gold-free controller can reliably identify query-level gain and harm. The frozen U1 controller reduced insertion resources by about 40% but retained a smaller fraction of gain queries than harm queries. Later mechanism probes found partial signal but did not meet their advancement rules. These results motivate the static bounded method and constrain future controller claims; they do not invalidate the static evidence.

The study's main contribution is therefore not a performance-race claim. It is a bounded method-and-evidence result: structured expansion can improve a compact dense backbone, facet relations can matter within that system, protected placement can reduce the damage of aggressive insertion, and these benefits stop short of established strong-dense superiority or complementarity.

## 6. Limitations

All answer-quality evaluations use closed candidate pools supplied by HotpotQA or MuSiQue. They do not test corpus indexing, ANN recall, supporting-document reachability or noise in a full-wiki/open-domain setting.

The primary positive results use one Qwen generator. The additional Gemma test covers one official mobile-QAT configuration and is inconclusive. It does not establish broad generator robustness or model-family ranking.

The strong-dense evidence binds one BGE large-en-v1.5 backbone. The negative replacement result and inconclusive sidecar result should not be generalized to every strong retriever.

The flat-unit granular-ball control was not fairly defined, so the granular-ball structure is not independently confirmed. The Stage4H protected-insertion ablation is inconclusive, although the later identical-set placement comparison supports protected placement within the BGE-sidecar system.

Sample sizes were fixed by resource and precision constraints, not by a formal power guarantee. The HotpotQA train boundary was unread by the project before selection, but public training data may still have appeared in generator pretraining.

Post-Gold mechanism audits and evidence-transition analyses are descriptive or exploratory. They cannot be promoted to confirmatory efficacy claims.

## 7. Reproducibility and integrity

Every included experimental stage binds its source data, ID selection, model snapshot, runtime environment, prompt schema, result schema and code identity. Gold labels are isolated from candidate construction, retrieval, ranking, prompt construction and generation. Main/rerun or deterministic subset contracts and independent verifiers protect query identity, byte identity, metric reconstruction and decision reconstruction.

The Stage5 figures do not rerun any scientific computation. A Python-only build script verifies the SHA-256 identity of 14 tracked Stage4E–Stage4I inputs, extracts already-frozen statistics, writes seven CSV source-data files and exports five figure groups as editable SVG, PDF, TIFF and PNG. A read-only Stage5 verifier checks source and derived hashes, core numerical strings, claim-boundary states, local links and editable SVG text.

## 8. Conclusion

HyperGranular-RAG provides a structured, protected and bounded mechanism for completing evidence over a compact dense retrieval backbone. Across frozen closed-candidate HotpotQA and MuSiQue evaluations, the static system repeatedly improves answer F1 over historical MiniLM Dense, and facet hyperedges contribute within the frozen MiniLM implementation. The method does not outperform BGE strong dense, and its complementarity as a BGE sidecar remains uncertain. Protected placement nevertheless improves over unprotected placement for the same inserted evidence. Taken together, the results support a narrow but reproducible claim: high-order evidence completion can help compact dense multi-hop retrieval when expansion is controlled, while stronger backbones and broader deployment settings remain explicit boundaries rather than assumed extensions.
