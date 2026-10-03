# Relation-feedback granularity pilot v1

Material Passport: 2026-10-04; implementation/development research; user specification
RG-refinement-pilot-v1; reference dab1e35. No independent confirmation or paper revision.
Existing historical files and unrelated dirty work are preserved. New namespace only.

## Question and prior art

Can paid local relation observations improve subsequent partition refinement and
evidence search? Binding, provenance, decomposition and bundles are shared correctness
infrastructure. Their presence is not a granular-ball contribution.

| Source and reading depth | Objects and procedure | Feedback/cost distinction from this pilot |
|---|---|---|
| [TaSR-RAG v1](https://arxiv.org/html/2603.09341v1), methods 3.2–3.6, partial full text | Retrieved documents become triples and taxonomy types; hybrid matching and sequential variable binding guide context selection. | It extracts candidate relations before matching. This pilot charges each requested local probe and tests whether observations alter geometric partitions. Relation decomposition/binding are adopted prior techniques. |
| [HKVM-RAG v2](https://arxiv.org/html/2606.07218v2), III and IV-A–E, partial full text | Shared cached tuples form bridge-centered answer-path keys, with source addresses and weighted diffusion; a separate dense-aware controller uses rank/score features. | Key-space comparison assumes an existing tuple cache. This pilot neither claims answer-path organization as new nor hides extraction preprocessing; no controller is implemented. |
| [FlexStructRAG v1](https://arxiv.org/html/2604.16312v1), 3.1 construction paragraphs, partial full text | Document-local chunking, bounded sliding windows, extracted relations and original source spans support multiple graph granularities. | Its reviewed construction precedes online retrieval. Here the candidate windows are fixed and only search partitions are refined after paid observations. HTML displays a February date inconsistent with the April identifier; no guessed publication date. |
| [SetR](https://aclanthology.org/2025.acl-long.861.pdf), §§3.1–3.3, ACL 2025 | Information requirements guide joint passage subset selection; GPT-4o selections from Top-20 train a distilled Llama model. | Requirement-aware selection is prior art. This pilot has no distillation, no claim of exact SetR reproduction, and measures bounded local extraction rather than set selection over already presented passages. |
| HGRAG (Wang et al., AAAI 2026), reused bounded registry/method reading | Entity–passage incidence, semantic/query activation and diffusion. | Not evidence that our query-time refinement is new; no same-budget external reproduction claimed. |
| SAGHL, reused publisher preview/registry only | Topological granular balls and hierarchical hypergraph learning. | Full split/stopping equations remain unread; cannot rule out related adaptive ideas. No QA extraction-budget identity established. |
| [GBGC](https://www.ijcai.org/proceedings/2025/0388.pdf), refinement equations 7–10 and framework, partial | Graph-degree seeds, BFS assignment, topology quality controls coarse-to-fine graph coarsening. | Refinement itself is prior art. Pilot feedback is observed slot/binding differences, and geometry uses normalized embedding Euclidean distance. No topology theorem is transferred. |
| [MORSE context ordering v2](https://arxiv.org/html/2609.27380v2), §3 and motivation, partial | Reverse query scoring compares orderings and compressed outputs under a token budget. | Evidence retention and cost-matched search matter here too, but this pilot allocates window probes, not compression permutations. The acronym also names a distinct subset-evolution paper; neither is silently merged. |

AAAI/SAGHL details and access limits are inherited from
../../literature_refresh/2026-10-02_bounded/literature_registry.json.
That registry contained no GBGC/MORSE record; their bounded primary-source checks
above are new. No full-paper reading claim, acceptance inference from a template,
or exhaustive novelty search. These readings did not establish an identical paid
observation/partition trigger; absence in reviewed sections is not proof of novelty.

## Design check (two perspectives of the same assistant)

Mentor: isolate refinement from shared relation processing using fixed, uniform,
feedback, flat and KMeans controls. Keep original text and budget costs visible.
Reviewer: first establish usable parser/verifier/reader capability. A false binding
can produce a misleading complete bundle in every method; geometric refinement
cannot repair its truth. Oracle synthetic results are not natural QA evidence.
Continue to the fixed capability check; no stronger claim or external deployment.

## Fixed behavior and limitations

Eight pipelines, BGE window Top-min(64,N), 320-token single window, 1024 serialized
reader tokens, 8/16/32 snapshots, QA only 16/32, 4 hypotheses, 32 conditional strings,
4 initial groups, 16 leaves, depth8, seed1729, at most20 KM updates. Two-source
connections are not proof of high-order representational necessity.

Witness v1 conservatively accepts exact body spans only. Explicit alias/coreference
is not inferred from title or surname; unsupported referents remain UNKNOWN. Unique
complete page-name matches bridge sources; otherwise identities remain source-local.
This deliberately shared restriction can reduce recall and must appear in D0 errors.
Positive relation facts only are connected; negated/uncertain propositions are not
silently turned into positive edges. Conditions stay in the verified directed claim.

Conditional on correct slots, identities and facts, the connector checks an existing
variable assignment before each extension. Induction over accepted extensions
therefore preserves binding consistency. Splitting only repartitions member IDs;
facts remain in the observation store and require a requested probe. Neither property
guarantees factual extraction, semantic completeness, optimal search or answer F1.
Zero vector normalization returns zero. Euclidean distance, not 1-cosine, defines
the split geometry. Standard properties are not claimed as new theorems.

## Decision and resource rules

D0 dev16/check16; at most one global prompt revision on dev; thresholds .5/.7/.9,
precision≥.90 and ≥10 accepted on decidable dev records, then highest recall,
tie higher threshold. D0 check is used once; >.20 accepted error, near-zero usable
bindings, or inability to answer with supplied support triggers capability diagnosis.
D1 remains historically exposed development even though disjoint from D0.

The user fixed A/B/C/D interpretations. Do not force natural comparison after a
capability/resource failure. No result-dependent extra seeds, samples or model search.
No paper/PDF/image changes, no locked data, no old scoring/generation reruns.
