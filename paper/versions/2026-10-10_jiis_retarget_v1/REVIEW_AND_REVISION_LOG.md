# One bounded mentor / JIIS-reviewer editorial review

Task: JIIS-bounded-retarget-v1.0. Baseline: 9111010802958a2cfb3d4d8df8d05ab03a81b06d. These are two editorial perspectives applied in this task, not external peer review or independent reviewers.

## Mentor perspective

| Location | Issue and judgment | Implemented revision / retained boundary |
|---|---|---|
| Abstract, Introduction | A neural-model framing obscured the information-access question. Change. | Lead with the interface between learned set scores, selected contexts and reader answers. Retain feasible-reference, joint outcomes and actual time as the three empirical checks. |
| Introduction contributions | Neither factorization nor indexing is new. Change. | Describe a linked empirical comparison, not a new retrieval architecture or theorem. |
| Related work 2.3 | Venue fit should be substantive, not a citation quota. Change. | Add two narrowly scoped JIIS comparisons concerning downstream embedding evaluation and distinct recommendation endpoints. Their tasks are explicitly different. No external performance numbers are imported. |
| Study design 3.1–3.4 | Indexes could be mistaken for semantic evidence grouping. Retain explicit definition. | Preserve all eight equations and distinguish conditional score-space indexes from semantic organization. |
| Data 4.1, checkpoint 4.4 | QA was exposed during initial selection. Cannot repair through editing. | Retain TUNE/QA dependence, source overlap, same-question seeds and later DEV-SELECT distinction. |
| Results 5.2 / Discussion | Support increase is not a demonstrated cause of answer loss. Retain and sharpen interpretation. | Keep the per-question decomposition and all-question denominator; explicitly describe associations, not causal effects. |
| Practical implications 6.3 | A general framework claim exceeds this study. Change. | Present three usable checks as lessons from this tested system, not a universally validated protocol. |
| Conclusion | Extra experiments are not authorized. No escalation. | Keep low-order gains, MMR competitiveness, H4/DeepSets losses and no acceleration; no new study is proposed as completed. |

## Strict JIIS-reviewer perspective

| Location | Issue and judgment | Implemented revision / unresolved limit |
|---|---|---|
| Abstract and 1 | Information-system relevance must be clear. Change. | Motivation now starts from evidence selection as an information-access decision, not presumed high-order superiority. |
| 3.3, 5.2, 6.2 | Equal token ceilings do not imply equal context lengths or cardinalities. Retain. | Dense/MMR and K6 references remain explicitly different comparisons. No matched-length answer experiment is invented. |
| 4.1 / 6.2 | No independent generalization test; only one reader. Unresolved. | Retained prominently as a substantive acceptance risk. No relabeling of development data. |
| Table 5 / Figure 4 | Joint decomposition can be mistaken for attribution. Retain qualified explanation. | Denominator remains 128; no significance, mediation or causal claims added. |
| 5.2.2 | Sixteen outcome-stratified cases do not establish population error rates. Retain. | EOS/truncation conclusion remains restricted to those 32 paired outputs. |
| 5.3 / Table 6 | Aggregate timing and absent per-query records limit cost claims. Retain. | No invented distributions/error bars; nested tokenizer timing and overlapping CPU/reader execution remain disclosed. |
| 4.6, declarations, Online Resources | Numerical reconstruction is not full prediction reproduction. Change. | Explicitly name unavailable raw source identities/manifests/weights and document saved-score-only reconstruction, licensing and author approval. |
| Template, references and private title matter | Submission packaging differs from Elsevier. Change. | Official Springer class, numbered references, flat archive, Online Resource metadata and local author declarations prepared. Final author approval, full affiliation address and live submission fields remain manual checks. |

No opinion requiring new training, inference, scoring or an inferential test was implemented. The manuscript remains a bounded empirical study with potentially insufficient breadth for acceptance; retargeting does not resolve that risk.
