# JIIS requirements and verification limits — 2026-10-10

Primary sources used:

- https://link.springer.com/journal/10844/submission-guidelines
- https://www.springernature.com/gp/authors/campaigns/latex-author-support
- https://link.springer.com/journal/10844/aims-and-scope
- https://link.springer.com/journal/10844/how-to-publish-with-us

The submission-guideline body and Springer LaTeX support/template were retrieved in this task. Initial browser/locally proxied requests for other pages failed. A bounded direct connection subsequently returned usable official HTML for all three journal pages; their scope and publishing-option bodies were read. The verification record identifies exact URLs, titles and retrieval date. No global proxy setting was changed.

| Requirement | Actual handling |
|---|---|
| At most 25 pages including figures, tables and references | Authored article: 22 pages including declarations and references; no hidden appended main-manuscript appendix. |
| LaTeX, editable source and PDF | Actual official sn-jnl class, sn-basic numbered style; source plus compiled PDF. |
| Template option | Official template package version 3.1 (December 2024). Older guideline mentions smallcondensed; it is not a supported option of this class, so it was not silently added. Default class geometry/type size retained; no negative-spacing or margin compression. |
| 150–250 abstract words, 4–6 keywords | 212 words by the documented tokenizer; six keywords. |
| Numbered references, full DOI links where available | 21 rendered references; 14 DOI metadata records checked via Crossref; remaining seven use primary publication/release URLs and the existing reference register. Not all 21 papers were reread in full this turn. |
| Figures and captions | Five embedded-font vector figures; normal insertion widths, ordered citations. Caption terminal full stops removed. Fig.1/2 panel letters converted to lowercase only. No scientific diagram relationship changed. |
| Tables | Six original tabular blocks unchanged. |
| Flat source upload | Every ZIP entry is root-level; actual independent extraction and full LaTeX/BibTeX build succeeded. |
| Supplementary metadata and references | Main text cites Online Resources 1/2; private versions contain title, journal, authors and correspondence. They may be published as supplied; approval remains required. |
| Author, funding, interests, data and AI disclosures | Confirmed local author order/sole correspondence/ORCIDs/CRediT imported, not guessed. No funding/conflict as confirmed. Research assistance disclosed in Methods, preparation assistance in declarations. |
| City/state/postal affiliation details | Institution and country retained from confirmed material. Full address fields should be confirmed by authors before upload; not guessed from an institution name. |
| Publication model | Subscription intended. The freshly retrieved official publishing-options page explicitly states that no APC applies to subscription publishing. This is not a guarantee that every optional service is free. No paid option selected. |

## Narrow literature reading record

Gerber et al., DOI 10.1007/s10844-025-00954-4: accessible publisher HTML sections on motivation, downstream tasks and evaluation inspected; Crossref metadata checked. Online 2025 and issue 2026 are distinguished in the bibliography. This is not a claim of line-by-line full-PDF reading.

Zoralioglu and Yalcin, DOI 10.1007/s10844-026-01025-y: publisher HTML obtained by direct connection; introduction/contribution and feedback-framework sections inspected, including user/item grouping, per-user and group-level endpoints, and simulated consumption. Crossref metadata checked. The manuscript uses the narrow multi-endpoint recommendation-feedback distinction, not a detailed algorithm comparison or borrowed result. This is targeted section reading, not a claim to have reread every equation, experiment and reference.

Ram and Gray / BGE bibliography entries were normalized to their published records using primary DOI metadata. Lin and Bilmes metadata was checked against ACL Anthology. No additional paper's empirical findings are treated as this project's evidence.
