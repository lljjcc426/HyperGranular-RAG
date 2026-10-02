# Manuscript evidence and historical-version ledger

Writing release: 2026-10-02. This is a manuscript-specific reconciliation, not a repeated repository audit or independent recomputation of experimental metrics.

## Evidence families actually included

All paths below are relative to the repository root. Exact point estimates and interval endpoints are retained in shared/effects.json, with a source path on every row. Presentation macros in shared/numbers.tex round the score-scale values to five decimals; plots multiply by 100 to display percentage points.

| Scientific role | Historical record | Configuration | Aggregate result |
|---|---|---|---|
| Initial compact HotpotQA, 1,000 questions | Stage4E; compact MiniLM/static-q25, Qwen FP16 | configs/stage4e_e2e_official_train1000_v1.json | results/stage4e_e2e_official_train1000_v1_evaluation_summary.json |
| Initial compact MuSiQue, 3,000 questions | Stage4F; same compact policy, paragraph-level support | configs/stage4f_xdr_official.json | results/stage4f_xdr_musique_train3000_v1_evaluation_summary.json |
| Generator transfer | Stage4G; reuses initial rankings/questions, Gemma mobile-QAT | configs/stage4g_gtr_official.json | results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_equal_weight_summary.json |
| Joint components and stronger baselines, 1,000/1,500 questions | Stage4H; seven historical arms including original compact Full | configs/stage4h_cbe_official.json | results/stage4h_cbe_hotpot1000_musique1500_v1_equal_weight_summary.json |
| BGE cross-space sidecar, 1,000/1,500 questions | Stage4I; BGE ranking plus frozen MiniLM structure | configs/stage4i_sdc_official.json | results/stage4i_sdc_hotpot1000_musique1500_v1_equal_weight_summary.json |
| BGE-native confirmation, 1,000/1,500 questions | Stage5A; native geometry/scoring, selected C10 | configs/stage5a_bnh_official.json | results/stage5a_bnh_confirmation_equal_weight_summary.json |

Native development used 500/750 questions and a fixed 16-configuration family. The selected C10 has leaf target 6, insert budget 4, unit percentile floor .50, BROAD gates. The selected development F1 difference is +.0031433109374285895; the best pre-tie-selection value is a different number. Neither development number is confirmation evidence. Selection source: results/stage5a_bnh_development_selected_config.json.

The dataset counts and evaluations are not pooled across these boundaries. Joint summaries average the two dataset means equally. Insertion counts described over 2,500 questions can instead be query-weighted; the papers identify that difference.

## Shared central claims

| Contrast | Answer-F1 difference | Recorded 95% interval | Permitted interpretation |
|---|---:|---|---|
| Compact Full − MiniLM, initial HotpotQA | +.01478 | [.00020, .02988] | Improvement under the recorded setup; lower bound close to zero |
| Compact Full − MiniLM, initial MuSiQue | +.01140 | [.00450, .01835] | Improvement under the recorded setup |
| Compact Full − MiniLM, joint | +.01357 | [.00491, .02233] | Repeated compact-system improvement; legacy scoring |
| Compact Full − NoFacet | +.01336 | [.00341, .02343] | Advantage over that particular centroid-only selector |
| Compact Full − NoProtection | +.00354 | [−.00675, .01389] | Unresolved protection contrast |
| Original compact Full − BGE | −.03998 | [−.05393, −.02621] | Original system below BGE on that boundary |
| Sidecar Protected − BGE | −.00256 | [−.00998, .00458] | Increment not established; not an equivalence test |
| Sidecar Protected − Unprotected | +.01122 | [.00129, .02104] | Placement-policy contrast, not isolated prompt-order causality |
| Native Protected − BGE | −.00305 | [−.00688, .00063] | Increment not established; not proof all native methods fail |
| Full − Dense with Gemma | +.00516 | [−.00262, .01295] | Transfer unresolved for that deployment configuration |

The remaining BM25, hybrid, facet, and unprotected contrasts are also preserved in the 17-row machine-readable ledger and manuscript discussion. We do not replace the recorded bootstrap with a new test. The prose describes interval direction and uncertainty; it does not promote historical uncentered-tail values into newly validated p-values.

## Historical implementation identity matters

1. The compact root includes all candidate units. Its split eligibility requires at least four members, while the size disjunction already fires above three; the radius threshold is therefore redundant under that configuration. A failed child-size constraint can retain a larger leaf. The manuscript does not call three a guaranteed maximum leaf size.
2. Historical compact facet candidates are scored once relative to the seed facets. The accepted set does not trigger true marginal recomputation. The later dynamic prototype is a different algorithm.
3. Compact insertion accepts at most four candidates after ten protected dense entries, deduplicates, fills from dense order, and truncates to effective K. An accepted candidate can already be in Dense ranks 11–20. Placement count is not a count of genuinely new evidence.
4. Cross-space sidecar uses BGE ranks with MiniLM geometry. BGE-native changes grouping rules, percentile features, gates, and score coefficients. It is not an encoder-only intervention.
5. Native NoFacet changes coefficients as well as removing facet eligibility. The manuscript labels this a pipeline contrast, not a pure component ablation.
6. Fixed insertion candidates do not by themselves certify identity of the final token-limited prompt. The placement interpretation remains correspondingly narrow.

Relevant frozen implementations were read for these writing claims: scripts/stage4e_e2e_evaluate.py, stage4f_xdr_evaluate.py, stage4g_gtr_evaluate.py, and stage5a_bnh_retrieval.py; the preceding audit supplies the broader claim/protocol/code mapping. None was changed this round.

## Scoring and inference lineage

The initial HotpotQA and generator-transfer scorer retain the special-answer exception for yes/no/noanswer. The initial MuSiQue scorer uses its recorded answer-alias convention. Joint component, sidecar, and native results use the frozen legacy alias-max normalized token-overlap implementation without that HotpotQA exception. We do not state that the legacy numbers reproduce official HotpotQA leaderboard scoring. Their real-prediction discrepancy remains unquantified.

CR@20 means coverage of the full annotated support set; ER@20 means the covered fraction. HotpotQA support is sentence-level; MuSiQue support is paragraph-level. Neither is automatically answer F1 or a complete reasoning-chain metric. All retrieval results are conditional on benchmark-supplied closed candidates.

Percentile intervals are reproduced from existing files, not recomputed. They reflect the recorded paired query-resampling model, not uncertainty over development selection, model training, or shared source documents. Historical p-value and Holm decision artifacts remain unchanged and are not re-certified by manuscript reconciliation.

## Descriptive and cost evidence

- shared/figure3c_evidence_displacement.csv: existing post-decision added/displaced counts. Sidecar 21/29 and 59/50; native 3/2 and 16/15. Dataset-specific support granularity is retained.
- shared/figure4c_insertion_distribution.csv: existing insertion-count distribution, explicitly not a matched intervention-rate experiment.
- shared/figure5_qualitative_cases.csv: two previously selected representative examples. The failure compares original compact Full with BGE, not protected sidecar evicting BGE rank two. Cases are post-outcome illustrations, not prevalence estimates.
- results/stage5a_bnh_confirmation_efficiency_summary.json and stage5a_bnh_confirmation_telemetry_main.json: historical time/memory/cache/call counts. The 10,000 transaction-wide calls and 2,000 final-process calls are distinct fields. No new generation or rerun is claimed.

## Checks completed for this manuscript release

shared/evidence_check.json records 17 aggregate-bound effects and the exact match of 13 pre-existing forest-plot rows. shared/manuscript_consistency.json records 48 absolute metric cells checked against historical summaries or equal-weight dataset means, 13 resolved citation keys per manuscript, and the preservation of the three old manuscript/reference identities. This is transcription consistency, not independent recomputation from predictions/Gold.

Existing final-verification records are historical evidence of the checks originally performed. Later audit fixes do not retroactively certify the older runs. Some aggregate status fields predate separate final verification; those files are not rewritten to conceal their history.

## Explicitly excluded from empirical claims

Stage6 development outputs, repaired selector/verifier behavior, v2 synthetic tests, new matched controls, corrected official-score evaluations, new significance tests, and open-domain/external-method experiments supply no empirical row in these papers. Theoretical arguments imported from THEORY_AND_COUNTEREXAMPLES.md are analytical clarifications, not performance measurements or new guarantees for the old heuristic.

The original paper and frozen experiment files remain in place. The new manuscripts retain all material positive, negative, and unresolved comparisons within their stated Stage4E–Stage5A empirical scope.
