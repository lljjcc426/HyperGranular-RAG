# NC-final-polish-v2.0 — final edit log

SPEC_ID: `HGRAG-NEUCOM-LITERATURE-GROUNDED-FINAL-POLISH-20261006`

Base: `853bd08673a572376fc22ff3a549e8b1f5b808ff`

Delivery status: `AUTHOR_REVIEW_READY`.

## Actual scientific and language editing

| Location | Change and retained boundary |
|---|---|
| Abstract (217 words), Introduction | Reorganized around set discrimination → selected support → same-question answers. Highlighted the joint decomposition; runtime remains auxiliary. Kept the feasible-reference gap, model-dependent response, and development-only status. |
| Related work | Replaced publication-precedent self-defense with concrete comparisons of selection objects and supervision. Removed the persuasive-dialogue citation from the argument; did not import the 12-paper style pool as a citation list. Nineteen cited entries retain their existing bibliographic fields. |
| Method | Defined head/order symbols and conditional coefficients, separated common input design from separately trained parameters, retained all eight equations unchanged. Preserved finite-beam and exact-bound limits. |
| Data and interventions | Clarified disjoint top-level groups versus nested MINE/DEV-SELECT/QA. Initial TUNE includes QA. Continuation changes examples, preference losses, and checkpoint criteria together; replay matches optimizer updates, not all computation. Round-two pair availability moved to supplementary method notes. |
| RQ1 | Kept static pair accuracy, matched-length diagnostic, feasible-reference support losses, and missing per-question reference scores/sets. Selected sigmoid bins remain descriptive, not independent calibration. |
| RQ2 | Promoted joint support–F1 changes and full-panel contributions. Preserved Dense, MMR, low-order, DeepSets, replay, both seeds, and all 128 questions. No causal attribution from transition groups. |
| Cases | EOS/no-output-limit finding is explicitly restricted to 32 answers in 16 inspected pairs. Acronym and date-role observations retain saved canonical scores. “Independent questions” in the new supplement text became “distinct development questions.” |
| RQ3 | Replaced broad “complete costs” language with measured selection scopes. Kept CPU overlap, nested tokenizer timing, absent refined per-query distributions, and no observed speedup. Historical overall costs remain in supplementary method notes. |
| Discussion / Conclusion (165 words) | Removed repeated development chronology and editorial defense. Conclusions answer the research questions without claiming higher order inherently succeeds/fails. Source overlap, answer-panel exposure, shared ceiling versus unequal realized length, and missing records remain explicit. |
| Disclosures / submission materials | Research AI assistance is in Methods; writing assistance is separately disclosed. Confirmed no-funding/COI statements are integrated. Confirmed author order, sole correspondence, and CRediT are in local private assets and same-source authored PDF. |

Academic-research-suite guided the question-to-comparison structure and claim-strength review; the PDF/document workflow was used for actual rendering and inspection. The final mentor-style check asked whether each RQ has an answer; the reviewer-style check asked whether its control supports the wording. These were internal editorial perspectives, not independent peer review.

## Figures and tables

- Figure 1: same saved H4 bins; all occupied-bin counts labeled, empty bins explicit, shared axes, no smoothing or invented intervals. Marker area increases with square-root count.
- Figure 2: same 4×3 paired counts, both seeds with N=128, common color scale and written support-state transitions. Table 5 supplies signed sums, group means, and full-panel contributions.
- Figure 3: means only, seconds/question, distinct method shapes and direct labels. Medians appear in editable Table 6; no median mark resembles an error bar.
- Six tables now use clearer denominators, units, and multiline headers. Table 6 presents the already measured refined-subset means/medians instead of the broader development-resource ledger; the ledger was relocated, not discarded.
- All three figures are vector PDFs with embedded fonts plus PNG previews and reproducible scripts. No image generator was used.

## Numerical and build checks actually completed

`analysis/FINAL_CHECK.json` records the results. Twenty-one numerical/reconstruction files are byte-identical to conversion v1. Clean extraction and execution of the existing reconstruction script reproduced all four derived CSVs exactly: 2,688 saved numeric observations, 1,024 paired records, 128 distinct questions. These are reused records, not new samples or predictions.

Checks tied the displayed QA, paired, decomposition, feasible-reference, and cost cells to those saved files. The roles table was read against the existing roles/overlap tables. Key H4 endpoints remain 55→57 and 0.4181→0.3766 for seed 1729, and 53→57 and 0.4304→0.3831 for seed 2026. Eight equation environments and all three bibliography source files are unchanged. No inference, answer rescoring, new test, or favorable alias correction was performed.

The final neutral PDF has 24 pages: title/abstract p.1; main text and declarations pp.2–21; references pp.22–24. The local authored PDF also has 24 pages, with front matter spanning pp.1–2, CRediT p.21, and references beginning on p.22. These are actual build lengths, not a claim of verified journal page-limit compliance.

All final neutral pages were rendered and visually inspected; all authored pages were inspected, including the subsequently adjusted reference pages. Six Word assets were opened through LibreOffice and their six resulting pages inspected. Tables, formulas, captions, reference numbers, embedded fonts, and page breaks were checked. The authored version uses positive 6-point inter-reference spacing to avoid a one-reference trailing page; the scientific text, tables, and figures are identical to the neutral source. No font-size or negative-spacing compression was used.

The flat source ZIP was independently extracted into a new directory and compiled successfully; its text and pagination match the delivered neutral PDF. Final LaTeX logs contain no overfull boxes, unresolved references, or LaTeX errors. The Office XSD validator could not start because its environment lacked `defusedxml`; no schema PASS is claimed. All six DOCX XML structures parsed, actual LibreOffice PDF conversion succeeded, and their rendered pages were reviewed.

## Scope, costs, and remaining human actions

New training/model forward/reader/retrieval/embedding/answer rescoring/statistical tests/GPU/paid calls: **0**. Retained task files occupied about 58.7 MB at final numerical checking, including local renders and intermediate builds; the small input extraction is additional. Recorded final TeX builds used 12.83 CPU seconds in total; other retained build logs and plotting/rendering records are separate. Some superseded editorial-build invocations, Node/LibreOffice, and shell overhead were not fully metered, so this is not a complete task-CPU total and unmeasured time is not reported as zero. No models, corpora, or runtime stacks were downloaded.

Author roles, no funding, and no relevant conflicts are confirmed. ECIR749 is handled as author-confirmed withdrawn; no new receipt or account check was requested. Final approval of this newly edited manuscript and live journal-specific submission fields remain human actions. The official Neurocomputing guide/options pages returned 403 during this task; generic Elsevier policy is not substituted for unknown journal-specific rules (see the file map).

All additions are under this new version directory. No historical file was deleted or overwritten, and unrelated dirty files are excluded from the commit. Only public neutral materials are synchronized; private metadata, authored assets, build directories, and the full input package stay local. The task ends here without a new experiment or research-upgrade round.
