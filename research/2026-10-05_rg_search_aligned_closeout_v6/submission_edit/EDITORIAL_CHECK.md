# Editorial check — 2026-10-05

Status: **READY_FOR_AUTHOR_CHECK**. No registration, submission, or payment was made.

## Evidence and numerical checks

- Existing per-query numeric records confirm primary-seed static/aligned H4 annotated full support of **55/128 and 57/128**, with canonical answer F1 **0.4181066176470588 and 0.3765887605042017**. MMR remains **0.4302903974089636**.
- Paired support: 4 gains, 2 losses, 122 unchanged. Paired F1: 10 gains, 14 losses, 104 unchanged. These counts do not establish a causal relation between the endpoints.
- Second-seed H4: 53/128→57/128; F1 0.43038340336134456→0.38309917717086833. Lower-order improvements and seed-dependent outcomes remain reported.
- The portable package reconstructs **19 method/seed groups from 2,432 numeric result rows**. These rows are repeated measurements, not 2,432 independent questions. Maximum absolute difference from the editorial derivation is 5.55e-17 (floating-point summation order). See NUMERIC_PACKAGE_CHECK.json.
- The checkpoint-selection panel and QA panel are separate 128-question subsets of exposed TUNE data. The role/overlap files distinguish query/group separation from shared source blocks.
- Historical confidence intervals, original result files, predictions, and scientific decisions were not replaced. No prediction rescoring, new statistical test, bootstrap, or significance claim was performed.
- An initial derivation encountered an explicit KeyError because the stored static method ID is H4-Flat. The mapping was corrected to that existing ID, and the completed derivation used the actual 128 paired records; no scientific data were edited.

## Actual builds and reproducibility scope

Both flat source packages were compiled with pdflatex, bibtex, pdflatex, pdflatex; all eight final commands exited 0. The final conference build took 2.5129 s wall time; journal 3.7185 s. Final measured compiler CPU times were 1.921875 s and 2.421875 s. Earlier layout builds and lightweight derivations are separately retained in EDITORIAL_COST.jsonl; these timings are not a measurement of total interactive editorial labor.

- Conference: **7 PDF pages: 6 body pages, no appendix, 1 reference page**; 3 tables; 11 cited entries resolved.
- Journal: **19 PDF pages total**: pages 1–16 main text/tables, page 17 declarations and start of references, pages 18–19 remaining references; 7 tables; 20 cited entries resolved.
- No overfull boxes, missing glyphs, undefined references, or unresolved citations were reported in the final logs. Remaining warnings concern the LNCS math accent/PDF title line break and journal PDF bookmark levels; no corresponding visible text defect was found.
- Git's whitespace check reports pre-existing whitespace/line-ending conventions in the copied publisher class/style files (cuted.sty, sn-jnl.cls and sn-mathphys-num.bst). These third-party files were preserved rather than reformatted; both bundles compiled with them.
- Journal submission_bundle contains no subdirectories or ../shared dependencies. PDF author metadata is blank. Anonymous text/source checks covered 17 relevant files and found none of the checked personal paths, original question identifiers, or project self-identifiers.
- The anonymous supplement was actually executed in a separate output directory using only Python's standard library. It reconstructs numeric tables, not raw-prediction scores or full model experiments. Licensed source data, exact cohort manifests, model files and the full execution environment are additional prerequisites for model-level reproduction; no one-command model-reproduction claim is made.

## Actual visual inspection

Codex rendered and inspected **all 26 final pages** using per-page renderings arranged in contact sheets. Conference pages 2, 3, 5 and journal pages 7, 11, 14 were additionally viewed individually at larger size for equations, main tables and historical comparisons. This is the assistant's inspection, not a claim that the instruction author, a human author, or an independent expert inspected the PDFs.

| PDF pages | Inspection coverage |
|---|---|
| Conference 1 | Title, abstract, opening narrative and anonymity |
| Conference 2–3 | Equations, method, continuation objective and experimental-setting flow |
| Conference 4 | Data-role table, protocol and transition into results |
| Conference 5 | Static-support and same-QA-panel tables, counts, units and captions |
| Conference 6 | System observation, limitations, conclusion and disclosure; body ends here |
| Conference 7 | Complete reference page, numbering and layout |
| Journal 1–3 | Title/abstract, introduction and related-work flow |
| Journal 4 | Data-role table and interpretation |
| Journal 5–6 | Set-score definitions, constraints and method layout |
| Journal 7–8 | Exact bound, continuation objective and associated equations |
| Journal 9 | Experimental protocol and transitions |
| Journal 10 | Static-selection table and surrounding interpretation |
| Journal 11 | Checkpoint-panel and same-QA-panel tables clearly separated |
| Journal 12 | Answer diagnostics and context-length distinctions |
| Journal 13 | Actual-cost table and scope of timing claims |
| Journal 14 | Historical effects/intervals and fixed-visible-evidence interpretation |
| Journal 15–16 | Discussion, limitations and conclusion |
| Journal 17–19 | Availability/AI disclosure and complete references |

No clipped content, overlapping text, unreadable formula, broken table or accidental blank page was observed. Tables, equations and references were checked against the source/derived values, not solely by image appearance. No new figures were created or historical plotting scripts modified.

## Author checks still required

ECIR abstract registration receipt remains **UNKNOWN**. Official Short deadlines are October 5/12; the Short page does not state a timezone, so the actual system/receipt governs. A six-page body alone does not establish submission eligibility.

The journal's 19-page build is below the stated 25-page total limit in the current template; the submission system/editor must settle the Springer Nature versus legacy smallcondensed instructions. Author identities, affiliations, contributions, funding/conflicts, permissions, submission consent and final declarations remain for the author. They are listed in ignored private/HANDOFF.md rather than fabricated in the manuscript. IEEE Access conversion is not performed or implied. The two papers are alternatives, not simultaneous submissions.

New model calls = **0**; training = **0**; paid expenditure = **0**. No locked data access. The completed editorial task does not authorize another research round.
