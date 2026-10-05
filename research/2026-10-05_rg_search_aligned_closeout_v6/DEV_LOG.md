# RG-search-aligned-closeout-v6.0

SPEC_ID=HGRAG-SEARCH-ALIGNED-CLOSEOUT-V6-20261005

## Before execution (2026-10-05)

Reference: 1463755cc56d84622e875607f67fc063298a1833. Existing unrelated working-tree changes remain untouched. The attachment is the active specification; historical v5 files, weights and scores are read-only dependencies. No paper figures or plotting scripts change.

Shared implementation: existing BGE Top128, whole paragraphs, original FP16 3B/P2, actual 1024 input-token limit, K<=6, width-four vectorized Flat search. No new model or index optimization.

MINE512 uses at most 256 FIT queries per dataset, allocated proportionally by existing strata using largest remainders, then group-hash order with prefix rg-v6-mine. Groups are kept together; an overflowing group is omitted rather than split. DEV_SELECT uses the same procedure (prefix rg-v6-select), at most 64 per dataset, excluding every QA-panel group. All boundaries are development, not confirmation.

Continued training uses these same MINE queries for all models, with four static and four mined sets per query (plus sampled ranking pairs). The static sets may contain FIT-only support injection from v5; mined candidates never do. This is a bounded continuation on the mined FIT subset, not an additional epoch over every original FIT query. H4 replay uses the same query order, eight static sets, optimizer and update count, with its original loss. Four aligned architectures share each merged pool. At most two rounds, eight epochs each; evaluate epochs 2/4/8. Checkpoint selection is lexicographic dataset-equal actual full support, coverage, negative original development loss, earlier epoch; QA is excluded.

The aligned loss retains the original point/full/coverage/static ranking terms and adds 0.5 each for final-set and frontier preferences, using the deployment logit and margin 0.2 times the annotated utility difference. Query normalization and missing-pair masks prevent large pools dominating. Per-query pool <=64; deterministic replacements <=8 per model trajectory. Frontiers prioritize same-parent, same-depth extensions; final pairs prioritize same size and token length ratio within [0.8,1.25], then other same-size pairs when necessary. Dense-K6/MMR-K6 remain candidates.

Resource starting point: v5 reports cumulative GPU 24114.6555248 seconds; CPU lower bound 29061.828 seconds, with older unknown CPU not imputed as zero. This round caps GPU at 7200 seconds, measured CPU at 10800 seconds, new disk 1 GB, new reader calls 1200, payment zero. At least 1800 GPU seconds reserved for primary QA. Stop model experiments by 2026-10-07. Use complete common stages before optional round two/seed two; no outcome-based method omission.

Mentor design check: directly testing the score/search mismatch is distinguishable from adding interactions. Mined partial comparisons must train the deployed logit, and replay separates added updates from changed examples/objective.

Reviewer design check: high support coverage is not answer utility; MMR and low-order/general-set controls are mandatory. Exposed QA cannot confirm generalization. Existing no-speedup results remain relevant and no tree rerun is needed. This bounded repair cannot validate older static-q25 mechanisms retrospectively.

## Completed development checkpoints

Round 1 completed all four aligned models and the H4 static-replay control (8 epochs each). Selected aligned epochs: H1=2, H2=8, DeepSets=2, H4=4. Dataset-equal selected support completeness is respectively 0.5078125, 0.5000000, 0.5078125, 0.5156250. These are checkpoint-panel measurements, not QA results. Later epochs did not improve every model, so training loss alone is not used to select a checkpoint. Round 2 re-mines all four selected models within the remaining budget.

Clarification of the pre-execution shorthand above: Dense-K6 and MMR-K6 are both retained in the mining reference pool. Only Dense-K6 is included as an additional final deployment candidate, exactly as in v5; MMR-K6 has not been added to the deployed decoder.

The first source tests exercised direct gradients from partial-coverage preferences, empty-pair masking, same-parent pair construction, and intact grouped sampling: four tests passed. Manuscript work creates only new v6 copies; old papers, figures, and plotting scripts are untouched. A missing LaTeX backslash in the new conference preference equation was corrected before compilation.

Primary-seed round 2 completed all five models. Each aligned model's globally selected checkpoint remains from round 1; the full second-round decline is retained. No loss weight, beam, data boundary or checkpoint criterion changed after these observations.

The optional seed-2026 baseline and common mining were started after the round-1 selection improvements were observed, before any new QA score existed. The trigger is the specified development-selection improvement and available resources, not a favorable answer result. All four architectures receive the same continuation procedure. Some CPU mining/selection overlaps small-model work; phase wall times therefore are conservatively additive and are not isolated latency benchmarks. Primary QA remains reserved.

Primary QA completed all 1,024 logical method/question rows, using 571 new calls and 453 identity-matched cache hits. Aligned H4 F1 is 0.3765887605, versus original H4 0.4181066176, replay 0.4046393557 and MMR 0.4302903974. H1/H2 improve relative to their own static checkpoints while DeepSets/H4 decline; none exceeds MMR for this seed. These answer observations did not change the second-seed training, selection criterion or planned common comparison.

The eight specified uncached reader checks reproduced the same input and output token IDs. The new summary driver initially resolved `qa` to the read-only v5 module because that directory precedes the current directory on `sys.path`; it was changed to load the exact v6 file under a distinct module name. This affected a failed summary invocation only, not experiment inputs, training or generation. No old result was rewritten.

New manuscript-only build repairs added outline fonts for the observed microtype bitmap-font error, a local unmodified `cuted` dependency and URL line breaking for bibliography underscores. The new conference keywords were shortened to remove an observed line overflow. Existing paper sources and figures were not edited. The official dependency origins and retained license notices are recorded in `manuscripts/TEMPLATE_PROVENANCE.md`.

Seed 2026 completed all four models in both rounds and all 512 logical QA rows. Every selected checkpoint is again from round one. Its aligned mean F1 values are H1 0.4125690106, H2 0.4173253676, DeepSets 0.3521343954, H4 0.3830991772. Both seeds' aligned models remain below common MMR in point estimate; H2 improves slightly against its own static model in both seeds. No QA result changed any checkpoint choice. The two-round cap has been reached and all new model experiments are closed.

Combined comparison output is 1,536 logical rows, 558 exact-identity cache hits and 978 new comparison generations. Eight separate uncached checks bring actual reader calls to 986. There are zero invalid answer fields and zero output-limit hits in the comparison rows. GPU process-wall expenditure is 4,513.0656322 seconds; measured research CPU is 6,997.0625 seconds, with manuscript-build CPU accounted separately. No paid compute, new model download, locked-data access, or old artifact modification occurred.
