# Venue Target Matrix

Status: `TARGET_VENUE_PENDING`
Official-information retrieval date: 2026-07-25

This matrix is a fit analysis, not an acceptance forecast. Current conference
deadlines are recorded as facts; future cycles must be rechecked when announced.
The 2022 CCF catalogue is used only where the venue appears in the official
list. A current Chinese Academy of Sciences journal partition was not reliably
available from a public official query, so no CAS partition is invented.

## Recommended order

1. **TACL** if the core argument and five figures can fit its ten content pages.
2. **TMLR** if the priority is a complete, reproducibility-centred empirical
   account with room for bounded negative and inconclusive evidence.
3. **A future ACL/EMNLP ARR cycle** if a conference timeline is preferred.
4. **Natural Language Processing (Cambridge)** as a journal fallback if the
   Gold-OA cost or waiver is acceptable.

The unique target remains a user/author decision because timing, funding,
institutional evaluation, and desired review model are author-level facts.

## Matrix

| Tier | Channel | Current official constraints | CCF / CAS note | Fit with this manuscript | Main rejection or submission risk | Non-experimental work needed |
|---|---|---|---|---|---|---|
| High | Transactions of the Association for Computational Linguistics (TACL) | Rolling journal; original submission has 10 content pages. Current appendix policy permits limited unreviewed appendices and requires essential claims in the main paper. Broad NLP scope, including empirical and evaluation work. | TACL is B in the official 2022 CCF AI list. CAS partition: institutional/current query required. | Strong fit for a complete NLP empirical paper with careful statistical boundaries. | Five figures, complete methods, and strong-retriever negative evidence may be difficult to compress into 10 pages; appendix is not reviewed. | Convert to TACL LaTeX; compress related work/method; keep decisive BGE evidence in main; anonymize artifacts. |
| High | ACL main conference, next available cycle through ARR | The published ACL 2026 contract used 8 content pages for long papers, two-way anonymized review, limitations/ethics requirements, optional supplement, and automatic Findings consideration. ACL 2026 submission is closed. Future rules/dates are not yet bound. | ACL is CCF A. CAS is not applicable to a conference. | Retrieval-augmented language models, QA, information retrieval, evaluation, negative findings, and reproducibility are in scope. | Compact MiniLM gains are small and the method is below BGE; reviewers may ask for full-wiki or more strong retrievers. Essential evidence cannot be moved only to supplement. | Prepare 8-page version, anonymized repository snapshot, responsible-NLP checklist, limitations and artifact statement; recheck the next CFP. |
| High | EMNLP main conference, future eligible ARR cycle | EMNLP 2026 uses 8-page long papers, two-way anonymized ARR review, and explicitly welcomes negative findings and reproducibility. The May 25, 2026 ARR deadline has passed; commitment on Aug. 2 is only for already eligible ARR papers. | EMNLP is CCF B. CAS is not applicable to a conference. | The verified empirical boundary and complete negative/inconclusive reporting fit EMNLP's stated empirical scope. | The current manuscript cannot newly enter EMNLP 2026; a later cycle is required. Novelty may be judged limited without open-domain evaluation. | Prepare future-cycle ARR package, citation/integrity audit, anonymized supplement, and author reviewer-registration readiness. |
| Realistic | Transactions on Machine Learning Research (TMLR) | Rolling, double-blind open review; variable length, with main bodies over 12 pages likely slower; up to 100 MB anonymized supplement; CC BY 4.0. TMLR welcomes studies of strengths/weaknesses and reproducibility. | Not present in the official 2022 CCF directory; no CCF rank assigned. CAS partition: not applicable/not bound. | Best match for a technically correct, bounded empirical study that reports where a method helps and where it does not. | NLP-specific reviewers may prefer broader baselines; open reviews require especially exact artifact and AI-assistance disclosure. | Apply TMLR LaTeX; anonymize code/supplement; add broader-impact and AI-assistance disclosures; settle repository license. |
| Realistic | Natural Language Processing (Cambridge; formerly Natural Language Engineering) | Broad NLP scope includes IR and QA; initial PDF, LaTeX required on acceptance; ethics and competing-interest declarations; figure accessibility/alt text; wholly Gold OA. Current listed APC is GBP 2,610 / USD 3,655 absent agreement, waiver, or discount. | Current renamed title is not assigned a CCF level here; do not infer from an older title. CAS partition: institutional/current query required. | Journal format can accommodate the full methods, limitations, and reproducibility narrative. | APC funding and the need for a clear applied NLP contribution; author ORCID and declarations are mandatory. | Confirm APC coverage/waiver, add figure alt text, Cambridge reference style, ethics/COI/AI declarations, and author ORCID. |
| Fallback outcome | Findings of the Association for Computational Linguistics | Not a direct standalone target in the cited ACL 2026 process; eligible ACL main submissions may be automatically considered for Findings. Same essential-evidence and anonymization constraints follow the conference route. | The official CCF catalogue explicitly excludes Findings from counted catalogue items. | Honest bounded evidence could be suitable if reviewers value the negative and reproducibility contribution but not main-track significance. | Cannot be selected independently under every cycle; institutional value may be lower because CCF does not count Findings. | Use only as an informed conference outcome preference; recheck the relevant conference commitment form. |

## Official source record

- [ACL 2026 main conference call](https://2026.aclweb.org/calls/main_conference_papers/)
- [EMNLP 2026 main conference call](https://2026.emnlp.org/calls/main_conference_papers/)
- [ACL Rolling Review call and supplementary policy](https://aclrollingreview.org/cfp)
- [TACL submissions and scope](https://transacl.org/ojs/index.php/tacl/about/submissions)
- [TACL appendix policy](https://transacl.org/index.php/tacl/announcement/view/105)
- [TMLR author guide](https://www.jmlr.org/tmlr/author-guide.html)
- [TMLR editorial policies and scope](https://www.jmlr.org/tmlr/editorial-policies.html)
- [Cambridge Natural Language Processing scope](https://www.cambridge.org/core/journals/natural-language-processing)
- [Cambridge preparation requirements](https://www.cambridge.org/core/journals/natural-language-processing/information/author-instructions/preparing-your-materials)
- [Cambridge fees](https://www.cambridge.org/core/journals/natural-language-processing/information/author-instructions/fees-and-pricing)
- [CCF official 2022 catalogue announcement](https://www.ccf.org.cn/Academic_Evaluation/By_category/2023-03-08/787209.shtml)
- [CCF artificial-intelligence list](https://www.ccf.org.cn/Academic_Evaluation/AI/)

## Decision blockers

- author preference for conference versus rolling journal;
- institutional value assigned to CCF versus unranked venues;
- ability to pay or waive the Cambridge APC;
- willingness to use open review (TMLR);
- timing of the next eligible ARR cycle;
- final page count after LaTeX conversion.
