# Fixed retrospective scoring and manuscript revision plan

Base: d52d480ef7377133a382992ec5d505775387031d. User authorization: historical Stage4E–Stage5A scoring/interpretation review and dual-manuscript revision only.

Before reading historical prediction scores in this round, fix these choices:

1. Preserve all original files. Read only completed, open Stage4E–Stage5A boundaries (including Stage5A development for descriptive scoring, never reselection). Verify each Gold file against its existing frozen identity before parsing. Missing/mismatched inputs block that boundary, not unrelated writing.
2. Independently reconstruct legacy per-prediction EM/F1, method means and original paired percentile intervals. Compare with archived query scores and summaries before interpreting canonical migration.
3. Use pinned official HotpotQA and MuSiQue answer scoring, including their distinct special-answer/empty-token rules and answer-alias handling. Fixed predictions, query order, methods, and equal dataset weights. No prediction postprocessing beyond the historical stored string.
4. Reuse the original 10,000 bootstrap resampling indices/seeds for legacy and canonical scores, including original dataset stratification. Report both. This is retrospective scorer migration, not new confirmation. Do not introduce or select a new hypothesis test: historical uncentered-tail p-values/Holm decisions remain archived and are not recertified as canonical significance.
5. Audit every Stage4I query for outside-Top20 insertions, m<=4, prefix=10, effective K, and identical Protected/Unprotected final membership. Reconstruct each arm's serialized prompt from bound historical inputs where available, checking its own hash and visible evidence content rather than equality of reordered whole prompts. Record truncation and all unresolved fields.
6. Summarize token min/median/p95/max and observed cap/drop/partial-truncation rates for all available historical main prompt audits. Separate the 20-entry budget from the 4,096-token cap.
7. Create new complete conference/journal sources and PDFs, preserving historical method versions and all negative/inconclusive evidence. Move unevaluated-extension counterexamples to the journal appendix. Do not alter authors/licensing or claim submission readiness.

Write allowlist: this directory only, plus a narrowly scoped new README navigation block at final delivery. No Stage6 source/config/results, raw Gold, models, or unrelated audit work in commits. No new training/retrieval/generation/model selection. Reservation and Stage3B stay locked.

Skill application: academic-research-suite revision/fidelity; localized LaTeX patches and a revision log preserve the old sources. User explicitly authorizes the specified body/appendix restructuring and new versioned complete outputs; no additional approval chain is introduced.
