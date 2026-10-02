# Final editorial check — bounded literature refresh, 2026-10-02

## Delivered manuscripts

- [Conference: complete English manuscript, 10 total pages](conference/HyperGranular-RAG_Conference.pdf)
- [Journal: complete English manuscript, 23 total pages](journal/HyperGranular-RAG_Journal.pdf)

Derived from `paper/versions/2026-10-02_editorial_final/` at starting HEAD
`7a91fa1a4029d5fde85a4277bca1856fc45b306e`. Previous manuscripts and results
were not overwritten. These are alternative presentations of the same evidence.

## Substantive changes and locations

| Location | Change |
|---|---|
| Both introductions and related work | Frame the contribution around evidence selection and arrangement; distinguish HyperGranular-RAG from Wang et al.'s Cross-Granularity HGRAG. |
| Conference related work, p. 2; journal related work, pp. 2–3 | Add the six requested nearest neighbors with task/representation differences and publication status; MGHRL remains a preprint. |
| Journal Table 1, p. 3 | Conceptual comparison of structure, supervision and retrieval; no cross-paper numerical ranking. |
| Conference Table 2, p. 6; journal Table 9, p. 18 | Separate measured findings from uncompleted matched controls and quality–cost comparisons. |
| Journal theory/discussion | Explain that incidence can be represented as a bipartite graph and that other papers' guarantees do not establish answer-F1 guarantees here. |
| Both discussion/limitations | Preserve the unresolved grouping, pure-component, MMR/coverage and strong-backbone claims. Lack of completed controls is not a negative experimental result. |
| Both provenance appendices | Record the unexecuted follow-up proposal and unverified confirmation independence without treating either as a scientific failure. |
| Conference ending | Place Conclusion before Limitations and ethics; retain the complete limitations. |
| Shared bibliography | Add five entries; reuse the existing HyperGraphRAG entry. Preserve existing references. |

The story remains: bounded structured completion improves the compact MiniLM
setting in repeated comparisons; evidence selection and placement are distinct
decisions. The fixed-visible-evidence placement contrast supports its specified
ordering policy, not an internal attention mechanism. Original Full is below BGE;
BGE extensions and generator transfer remain unresolved.

## Numerical and version checks

`DOCUMENT_CHECK.json` passed. All 15 non-bibliography shared files are byte-identical
to the preserved baseline, including numeric macros, data tables and figure assets.
Displayed equation blocks, inline-math multisets and all old table bodies are
unchanged in both sources. Existing citations are retained; new citation keys and
DOIs are unique and cited keys resolve. New tables contain conceptual distinctions,
not new scores. All figures/tables have source references.

Canonical scores, original comparison populations and intervals remain unchanged.
74,750 denotes prediction records, not independent observations. Stage4I uses all
2,500 paired queries, with identical visible evidence established by revision2;
the 1,528 changed-order cases do not replace that denominator. Top-20 entry count
and the 4,096-token cap remain separate. Repaired prototypes do not explain old
static-q25 results. No predictions or Gold were rescored in this revision.

## Actual build and page review

Both PDFs were built locally using the preserved Python build workflow and MiKTeX
pdfTeX. Five final build commands exited zero for each version. The final logs have
no overfull-box, undefined-reference/citation or rerun-required warnings. Real
command logs, main.log, main.blg and extracted PDF text remain under each `build/`.
An extra LaTeX pass was added to resolve an observed journal cross-reference warning;
this changes the document build only.

All 10 conference and 23 journal pages were visually checked in rendered contact
sheets for pagination, blank/missing output, clipping and overlap. Individual
high-resolution pages were additionally inspected: conference 2, 3, 6, 8; journal
3, 7, 18. These cover new related-work text, conceptual tables, numerical displays,
equations and references. The final journal p. 18 and pp. 19–23 contact sheet were
rechecked after the final Table 9 reference. No obvious layout defect was found
within this scope. This is not a claim that every page was inspected at full zoom.
`BUILD_STATUS.json` records page dimensions/text counts and links this manual scope;
build success alone is not counted as visual inspection.

Conference: main text through Conclusion, Limitations and ethics ends on p. 7;
references begin p. 8; appendices span pp. 8–10. Journal: main text and ethics end
on p. 19; references span pp. 19–20; appendices span pp. 21–23. Total page counts
include all of these. Figures and plotting scripts were not edited.

## Human decisions and unresolved items

No author, institution, license, funding, conflict or submission metadata was
invented; both sources retain Anonymous authors. Venue-specific template and
anonymity requirements, submission declarations and reviewer registration need
human confirmation. The journal is still a generic article layout; 23 pages here
does not certify the final venue's page limit. The two manuscripts must not be
submitted concurrently as independent work.

SAGHL and the TKDE paper were not available in complete legal full text during the
bounded pass; their detailed algorithms/proofs remain explicitly unverified.
The literature registry distinguishes full, partial and metadata-only reading.
No new independent confirmation, matched-control win, stronger-backbone gain or
cost superiority is claimed. See `../TARGETS_AND_STORY.md` for the realistic venue
choice and `../FINAL_STATUS.md` for the execution stop and remaining boundaries.
