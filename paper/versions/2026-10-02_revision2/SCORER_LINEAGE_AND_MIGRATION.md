# Historical scorer reconstruction and canonical migration

Scope: Stage4E–Stage5A completed, opened historical boundaries only. Base commit: `d52d480ef7377133a382992ec5d505775387031d`. This is retrospective reanalysis of fixed predictions, not a new independent confirmation or official leaderboard submission. The plan was fixed in commit `7c4109a` before inspecting prediction scores in this round.

## Actual reconstruction

`rescore.py` reads every stored prediction in scope and the corresponding frozen reference file. Prediction and Gold bytes match their recorded historical identities before scoring. It independently reconstructs all archived per-query answer EM/F1 and method means, then the original paired percentile intervals and generator-interaction intervals (tolerance 1e-12). The implementation does not import production evaluators. Legacy and canonical columns use the same 10,000 bootstrap indices, seeds, dataset order, and equal-dataset weighting. Development had no original confidence intervals; its interval fields remain empty rather than inventing a new inferential analysis.

| Boundary | Questions | Methods | Predictions | Changed predictions |
|---|---:|---:|---:|---:|
| Stage4E compact HotpotQA | 1,000 | 2 | 2,000 | 0 |
| Stage4F compact MuSiQue | 3,000 | 2 | 6,000 | 0 |
| Stage4G generator transfer | 4,000 | 2 | 8,000 | 0 |
| Stage4H joint components | 2,500 | 7 | 17,500 | 0 |
| Stage4I cross-space sidecar | 2,500 | 4 | 10,000 | 0 |
| Stage5A development | 1,250 | 17 | 21,250 | 17 |
| Stage5A confirmation | 2,500 | 4 | 10,000 | 0 |
| Total prediction records (not unique questions) | — | — | 74,750 | 17 |

## Dataset-specific sources and rules

The actual official pure functions, extracted from the pinned source AST, are executed. This avoids replacing them with a remembered approximation or executing their unrelated command-line code.

- [HotpotQA official evaluator](https://github.com/hotpotqa/hotpot/blob/3635853403a8735609ee997664e1528f4480762a/hotpot_evaluate_v1.py): revision `3635853403a8735609ee997664e1528f4480762a`; SHA-256 `D35FC91A6DB21D791DBDDA11DAF3856E9359F5701D54E3EEFBA20D88FECC02C0`.
- [MuSiQue official answer metric](https://github.com/StonyBrookNLP/musique/blob/922ac98f19a201998dbdae6d7f2887a5258dbdeb/metrics/answer.py): revision `922ac98f19a201998dbdae6d7f2887a5258dbdeb`; SHA-256 `10368F619B4D5EF5D83748C05A96C0AFD332A14AB5C010740C98D58DFAEFE974`.

| Scorer lineage | Categorical exception | Empty normalized pair | Aliases |
|---|---|---|---|
| Initial HotpotQA legacy | yes/no/noanswer mismatch => F1 0 | EM 1, F1 0 | Single reference |
| Initial MuSiQue legacy | No Hotpot exception | EM/F1 1 | Independent max for EM and F1 |
| Generator-transfer legacy | Hotpot exception only on HotpotQA | EM/F1 1 | Dataset's stored references |
| Joint/sidecar/native legacy | No categorical exception | EM/F1 1 | Stored references |
| Canonical HotpotQA | Official categorical exception | EM 1, F1 0 | Single reference |
| Canonical MuSiQue | No categorical exception | EM/F1 1 | Independent max over answer and aliases |

Normalization lowercases, removes ASCII punctuation and English articles, and normalizes whitespace, using each pinned implementation. The frozen MuSiQue preparation retains the answer and nonempty raw aliases; aliases that become empty after normalization are not silently discarded. No raw corpus is newly searched, no answers are inferred from aggregates, and no prediction is rewritten. This checks answer metrics against the verified frozen reference channel, not every task in either official evaluation CLI.

## Measured effect, not a hypothetical example

All 17 changes concern `hotpotqa_train_distractor_v1_1::5a839c645542990548d0b1ff` in native development. All methods output the identical affirmative sentence recorded in `scoring/AFFECTED_PREDICTIONS.csv`. Legacy token F1 is 0.20; canonical HotpotQA F1 is 0. EM stays zero. Consequently every HotpotQA development method mean falls by 0.0004, and its two-dataset equal-weight mean falls by 0.0002. These are actual per-prediction corrections. Their equality across arms was checked, not assumed; every paired method difference is unchanged. C10 was not reselected and no confirmation score was used for tuning.

The other 74,733 records are unchanged. In particular, all 53,500 confirmation/transfer predictions are unchanged, along with their paired deltas and reconstructed intervals. Empty-normalization differences cause zero observed score changes; this does not mean empty strings or aliases are absent. There are 100 normalized-empty predictions in generator transfer. The CSV reports empty-reference and multi-reference counts per dataset/method. Alias maximization improves at least one answer metric over using only the first reference on 146/75/319/144/236/197 prediction records in Stage4F/4G/4H/4I/5A-development/5A-confirmation, respectively. These alias benefits already existed in legacy scores and are not migration changes.

## Outputs and interpretation limits

- `scoring/LEGACY_VS_CANONICAL_SCORES.csv`: every stage/dataset/method, denominator, changes by reason, aliases/empty strings, both absolute EM/F1 means.
- `scoring/PAIRED_COMPARISONS.csv`: both deltas, both intervals, delta shift, original bootstrap seed; includes generator interaction and descriptive development contrasts.
- `scoring/INPUT_IDENTITIES.json`: historical files actually read, bytes/SHA and whether an existing frozen binding was checked. Aggregate JSON was consulted only to check independently reconstructed quantities.
- `scoring/RECONSTRUCTION_STATUS.json` and `rescore_execution.txt`: actual completion record.

No new p-value test was introduced. Archived uncentered-tail/Holm decisions are not overwritten or recertified. The original percentile interval and its assumptions are separate from null calibration of a tail probability. Document-level dependence, multiplicity, development selection, and pretraining uncertainty remain limitations; scorer migration does not cure them. No score-dependent choice of scorer, comparison family, threshold, or statistical method occurred.
