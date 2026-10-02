# Claim impact under dataset-canonical scoring

All entries below concern the original evaluated method, not repaired Stage6 or synthetic v2 code. Values are answer-F1 differences on the 0–1 scale; intervals reproduce the original 10,000 paired percentile draws. Joint rows use equal dataset weights.

| Claim/comparison | Canonical estimate [95% interval] | Change from legacy | Permitted interpretation |
|---|---|---|---|
| Compact Full − Dense, initial HotpotQA | +0.01478 [0.00020, 0.02988] | None | Positive within the tested compact system |
| Compact Full − Dense, initial MuSiQue | +0.01140 [0.00450, 0.01835] | None | Positive within the tested compact system |
| Compact Full − Dense, joint | +0.01357 [0.00491, 0.02233] | None | Repeated compact benefit |
| Full − compact NoFacet | +0.01336 [0.00341, 0.02343] | None | Specific facet selector exceeds centroid-only control |
| Full − BGE | −0.03998 [−0.05393, −0.02621] | None | Original compact system is worse than BGE here |
| Sidecar Protected − BGE | −0.00256 [−0.00998, 0.00458] | None | Complementarity unresolved, not equivalence |
| Native Protected − BGE | −0.00305 [−0.00688, 0.00063] | None | Complementarity unresolved, not equivalence |
| Sidecar Protected − Unprotected | +0.01122 [0.00129, 0.02104] | None numerically; interpretation corrected | Fixed-visible-evidence ordering/placement-policy contrast |
| Gemma Full − Dense | +0.00516 [−0.00262, 0.01295] | None | Transfer unresolved |
| Native C10 development − BGE | +0.003143 (descriptive) | None | Historical selection context only; no reselection |

Every other original EM/F1 contrast, including generator interaction, is in `scoring/PAIRED_COMPARISONS.csv`. Every absolute method mean is in `scoring/LEGACY_VS_CANONICAL_SCORES.csv`. The only absolute-score correction is the same −0.0004 HotpotQA-development F1 shift for all 17 methods, produced by one query. It does not change any difference or historical configuration ordering; the selection procedure was not run again.

The previous manuscript's warning that the answer-scoring discrepancy was unquantified is now replaced by measured impact. Its suggestion that the old sidecar's final sets might differ is replaced by actual all-query membership and visible-text verification. This strengthens the precision of the placement interpretation without creating a new experiment, an attention-mechanism claim, or a positive BGE-relative claim.

Unchanged unresolved questions: granular-ball necessity, superiority over matched MMR/coverage/ordinary clusters, strong-backbone complementarity, open-domain validity, broad generator robustness, and historical p-value calibration. Standard coverage theory is background, not an HGRAG answer-quality guarantee. Historical negative results remain visible in both abstracts, main tables, figures, discussion, and conclusions.
