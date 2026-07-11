# Stage3C External Dataset Screen

## Material Passport

- Origin Skill: academic-research-suite / deep-research
- Origin Mode: fact-check
- Origin Date: 2026-07-11
- Verification Status: SOURCE-VERIFIED
- Version Label: dataset_screen_v1
- Protocol: `docs/STAGE3C_PROTOCOL.md`
- Search boundary: official papers, project pages, author repositories, and official dataset access pages only

## Screening Result

| Candidate | Gold evidence (3) | Context/corpus (2) | Multi-hop (2) | >=10K (1) | QA (1) | Access/terms (1) | Score | Saturation | Role decision |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| HotpotQA train | 3 | 2 | 2 | 1 | 1 | 1 | 10 | `PILOT_REQUIRED`; dev is not saturated on HotpotQA | Same-domain event expansion |
| MuSiQue train | 3 | 2 | 2 | 1 | 1 | 1 | 10 | Observed dev CR@20 = 1.0000 | Do not use for current Top-20 completion target |
| 2WikiMultiHopQA | 3 | 2 | 2 | 1 | 1 | 1 | 10 | `PILOT_REQUIRED` | Primary independent pilot candidate |
| IIRC | 3 | 2 | 2 | 1 | 1 | 0 | 9 | `PILOT_REQUIRED` | Secondary candidate after access/adapter audit |
| HoVer | 3 | 2 | 2 | 1 | 0 | 1 | 9 | `PILOT_REQUIRED` | Retrieval robustness only; task-shifted |

Unknown items score zero. A high documentation score does not establish non-saturation under the current MiniLM retriever.

## Evidence Cards

### HotpotQA Train

- The [official HotpotQA project page](https://hotpotqa.github.io/) describes natural multi-hop QA with strong supporting-fact supervision, downloadable train/dev data, a distractor setting with 10 paragraphs, a processed Wikipedia corpus, and CC BY-SA 4.0 terms.
- The [EMNLP paper](https://aclanthology.org/D18-1259/) reports 113K Wikipedia-based question-answer pairs and sentence-level supporting facts.
- Fit: format already matches the current pipeline and the observed HotpotQA dev baseline CR@20 is not saturated.
- Limitation: more HotpotQA improves event count but does not test cross-dataset generalization.

### MuSiQue Train

- The [official MuSiQue repository](https://github.com/stonybrooknlp/musique) provides answerable/full train, dev, and test sets, supporting-fact evaluation, and CC BY 4.0 terms.
- The [TACL paper](https://aclanthology.org/2022.tacl-1.31/) describes about 25K answerable 2-4 hop questions, 20-paragraph contexts containing supporting and BM25-retrieved distractor paragraphs, and explicit anti-shortcut construction.
- Fit: evidence labels and paragraph candidates are directly usable.
- Limitation: all 1,000 observed MuSiQue queries already have dense-fixed CR@20 = 1.0000, so more rows are not justified for the unchanged Top-20 chain-completion endpoint without a pilot demonstrating a different event rate.

### 2WikiMultiHopQA

- The [COLING paper](https://aclanthology.org/2020.coling-main.580/) states that 2WikiMultiHopQA combines structured and unstructured information, guarantees multi-hop steps through its construction process, and supplies evidence paths.
- The [official author repository](https://github.com/Alab-NII/2wikimultihop) documents HotpotQA-compatible `context` and `supporting_facts`, explicit evidence triples, four reasoning types, public data access, and an Apache-2.0 repository license.
- The paper reports 192,606 examples, satisfying the scale requirement.
- Fit: independent QA benchmark, compatible evidence representation, distractor contexts, and richer reasoning types make it the first new pilot candidate.
- Limitation: dataset-specific redistribution terms should be rechecked when downloading because the data archive is linked separately from the code repository.

### IIRC

- The [EMNLP paper](https://aclanthology.org/2020.emnlp-main.86/) reports more than 13K questions grounded in a partial Wikipedia paragraph with missing information in linked documents.
- The paper states that annotators provide gold context spans and that link/context selectors are trained from those annotations; it also reports that 70% of questions need one linked document, 23% need two, and 7% need three or more.
- Fit: low lexical overlap and linked-document retrieval are attractive for adaptive retrieval.
- Limitation: the official paper points to `https://allennlp.org/iirc`, but that entry returned an error during the 2026-07-11 audit, and no dataset-specific license was verified from an authoritative current page. Access/terms therefore score zero pending remediation.

### HoVer

- The [official HoVer project page](https://hover-nlp.github.io/) provides train/dev downloads, CC BY-SA 4.0 terms, processed-Wikipedia corpus guidance, and evaluation against ground-truth supporting facts.
- The [EMNLP Findings paper](https://aclanthology.org/2020.findings-emnlp.309/) describes 2-4 hop evidence extraction from multiple Wikipedia articles; the released split totals 26,171 claims.
- Fit: strong sentence/document evidence structure and a genuinely open retrieval corpus.
- Limitation: the target is support/refute classification rather than answer-producing QA, so it should be used only for retrieval robustness or a deliberately broadened task formulation.

## Recommendation

1. **Primary new pilot: 2WikiMultiHopQA.** It is independent of the two current datasets, retains QA alignment, and has directly compatible supporting-fact/context structure.
2. **Event expansion: HotpotQA train.** Use only if more gain events are needed for development; label the resulting evidence as same-domain.
3. **Do not extend MuSiQue for unchanged CR@20.** First change the endpoint or run a small preregistered pilot showing that the selected split is not saturated.
4. **Keep IIRC as a secondary retrieval-adaptation candidate.** Resolve official access and terms before downloading.
5. **Keep HoVer outside the primary QA claim.** It is suitable for later evidence-retrieval robustness, not direct answer-chain evaluation.

## Search Record

- Query families: dataset name + official paper + official repository/project page + license/access
- Sources checked: ACL Anthology papers, HotpotQA and HoVer project pages, and author-maintained GitHub repositories for MuSiQue and 2WikiMultiHopQA
- Third-party dataset cards and summaries were not used for scoring
- Checked: 2026-07-11

## AI-Assistance Disclosure

Codex assisted with source discovery, structured extraction, and comparison. Every scored property is linked to an authoritative source above; unresolved access or licensing evidence is explicitly marked rather than inferred.

## Interpretation Boundary

This screen verifies documented dataset properties and access evidence. It does not measure event prevalence, MiniLM saturation, or HyperGranular-RAG performance on any new dataset. Those require a separately frozen pilot protocol.
