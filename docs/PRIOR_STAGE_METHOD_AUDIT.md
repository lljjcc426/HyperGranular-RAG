# Prior-Stage Method And Integrity Audit

## Material Passport

- Audit date: 2026-07-11
- Audited commit: `bbc7279e07b066e925074d1fd60d193876de5296`
- Skill workflow: `academic-research-suite` experiment validation and methodology review
- Evidence boundary: current repository, current local datasets, deterministic reruns, and primary dataset pages checked in this task
- Other conversations, thread tools, and memory files used: No
- Overall status: `COMPUTATIONALLY_REPRODUCIBLE_WITH_METHOD_SCOPE_CORRECTIONS`

This audit separates execution integrity from scientific strength. A byte-identical rerun shows that a result is reproducible; it does not turn an exploratory, adaptively selected comparison into confirmatory evidence.

## Executive Decision

Not every earlier stage is problem-free.

- Data slices, query IDs, gold mappings, embeddings, and deterministic outputs through Stage3C passed the integrity checks.
- No retrieval selection or ranking path was found to use gold labels. Gold fields are attached only for evaluation and diagnostic summaries.
- Stage0 through Stage2E did not have independently committed pre-result protocols. They are reproducible exploratory development, not confirmatory experiments.
- Stage2F and Stage2G used disjoint, frozen test slices. Stage2F's primary CR@10 gate failed; Stage2G rejected the current boundary rule.
- Stage2H is post-hoc diagnosis. Stage3A is a failed development attempt, not a validated controller. Stage3C is a valid retrospective planning audit, not model validation.
- The original Stage4A remains scientifically invalidated because its 400-query size lacked an operating-characteristic basis and its mirror content was not equivalent to the official April 7 archive.
- The proposed restarted Stage4A `n=2,800` calculation is arithmetically correct but is only an event-count lower bound. Its target of 20 gains is a frozen planning heuristic, not a power analysis or proof of adequate controller-training data. The draft is returned for design revision.

The last retained completed stage is therefore Stage3C, with a descriptive-planning evidence class. The next executable experiment is not authorized. Work must resume at Stage4A design, while Stage3B stays locked.

## Stage Classification

| Stage | Integrity | Evidence class | Audit decision | Permitted conclusion |
|---|---|---|---|---|
| Stage0 | Passed with provenance limit | Data engineering | `RETAIN_WITH_SOURCE_SCOPE` | HotpotQA and MuSiQue can be mapped to the common evidence schema. HotpotQA is the pinned mirror file; official byte equivalence was not independently certified. |
| Stage1 | Passed | Exploratory | `RETAIN_EXPLORATORY_ONLY` | The observed 400-query development slice generated useful mechanism hypotheses. It cannot establish general superiority. |
| Stage2A | Passed | Post-selection uncertainty analysis | `RETAIN_EXPLORATORY_ONLY` | The paired interval describes the adaptively selected Stage1 comparison. The pooled gain is heterogeneous by dataset. |
| Stage2B-C | Passed | Exploratory dense replication and protection search | `RETAIN_EXPLORATORY_ONLY` | Dense fixed is the stronger baseline; protected insertion is a candidate mechanism. |
| Stage2D-E | Passed | Exploratory configuration search | `RETAIN_EXPLORATORY_ONLY` | q25 is a transferable candidate threshold, not an optimum. |
| Stage2F | Passed and byte-identical | Preregistered internal test, caution | `RETAIN_NARROW_INTERNAL_EVIDENCE` | The primary q25 p5/i4 CR@10 effect was not supported. Small false-insert and p10 CR@20 effects were supported only within the same datasets and encoder. |
| Stage2G | Passed and byte-identical | Preregistered mechanism test | `RETAIN_VALID_NEGATIVE_RESULT` | The current OR-composed boundary rule is not a validated selective trigger and must not be carried forward. |
| Stage2H | Passed and byte-identical | Post-hoc diagnosis | `RETAIN_DIAGNOSTIC_ONLY` | Existing boundary components show weak predictive signal; no replacement threshold is validated. |
| Stage3A | Passed and byte-identical | Preregistered development | `RETAIN_FAILED_DEVELOPMENT` | The sparse-target fallback caused the promotion gate to fail. No controller is validated and Stage3B cannot be opened. |
| Stage3C | Passed and byte-identical | Retrospective planning audit | `RETAIN_DESCRIPTIVE_ONLY` | Gains are available in HotpotQA and absent in saturated MuSiQue at CR@20. The 20-event rule is a planning heuristic. |
| Original Stage4A | Reproducible mirror run; official equivalence failed | Invalidated pilot | `ARCHIVE_INVALIDATED` | No scientific conclusion about official 2Wiki feasibility is allowed. |
| Restarted Stage4A draft | Calculation reproducible; design inadequate for execution | Planning draft | `RETURN_FOR_DESIGN_REVISION` | `n=2,800` may be cited only as the lower bound for observing 20 events under `p=0.01`; it is not an approved sample size. |

## Data And Split Integrity

Raw source checks:

| Dataset | Rows | SHA-256 | Result |
|---|---:|---|---|
| HotpotQA dev distractor | 7,405 | `E3DA074DF24E8369009918AA5CDBDD254DADCDE4C63F7569D36AFD6F2268CAA8` | Matches the pinned local source and Hugging Face mirror metadata |
| MuSiQue answerable dev | 2,417 | `15FA63794D18A94CE12411ACA6E2327E65B6E83B0B1490EFAB3F1962E48ABF3B` | Matches the Stage3 reservation record |

Processed-slice checks:

| Slice | Source rows per dataset | Queries | Units | Gold units | Missing gold | Pairwise overlap |
|---|---|---:|---:|---:|---:|---:|
| Stage1/2E | `[0:200)` | 400 | 12,304 | 887 | 0 | 0 |
| Stage2F | `[200:400)` | 400 | 12,333 | 882 | 0 | 0 |
| Stage2G | `[400:600)` | 400 | 12,122 | 882 | 0 | 0 |
| Stage3A | `[600:1000)` | 800 | 24,415 | 1,774 | 0 | 0 |
| Stage3B reservation | `[1000:1400)` | 800 | Not computed | Not computed | Not read | 0 |

Every processed query ID matched its declared raw-source slice. Unit query sets matched query files, flagged gold counts matched query gold IDs, and embedding shapes matched the corresponding query and unit counts. The Stage3B ID digest matched `docs/STAGE3_DATA_RESERVATION.json`; no Stage3B retrieval metric was computed or read.

## Deterministic Reproduction

Fresh reruns were written outside the repository to `E:\科研\超粒球RAG_数据\temp\prior_stage_audit_bbc7279\`; tracked outputs were not overwritten.

| Output | SHA-256 | Rerun result |
|---|---|---|
| Stage2F summary | `2B04939494CE22FF5F6CFB9C5AF8644B73F0C41957FA46CE8262342BE1A45297` | Byte-identical |
| Stage2F bootstrap | `8298E8348158D12AB0988432689984D6C4FED6A7C99C044B426888C24AC11252` | Byte-identical |
| Stage2G summary | `878D7C00818555BFE0CC27E067C4523ACAA7B70FD8CFD109E0E52BBE9745AB4B` | Byte-identical |
| Stage2G bootstrap | `552A8CD5CD40C994F2E3AA8E590BE5CD5C41DBD5E98DDC4E8E583151439D1167` | Byte-identical |
| Stage2H query/component/predictive outputs | `9773436E...399F`, `67A64880...60B5`, `12836AEB...7BF4` | Byte-identical |
| Stage3A query/model/summary/bootstrap outputs | `8CEBBEB9...4561`, `53223FC5...03C7`, `D32C5003...A3B8`, `FCE4ECDA...08E4` | Byte-identical |
| Stage3C summary/decision | `92441830...92CA`, `02CA6F73...59F9` | Byte-identical |

All Stage0-Stage3C Python scripts compiled. During the audit, the first Stage2F rerun omitted the protocol-required `--expand-boundary-only` flag and correctly failed preflight before creating outputs; it was rerun with the frozen flag. A later Stage2G hash-display command had a PowerShell pipe syntax error after the experiment completed; only the comparison command was corrected. Neither incident changed scientific outputs.

## Gold-Label Leakage Audit

Static control-flow and ranking inspection covered the Stage1 facet/hyperedge scripts, dense replication, protected reranking, insertion-noise filtering, and the Stage2F-G wrappers.

- Ball construction uses text embeddings, radii, sizes, and unsupervised term features.
- Hyperedge and facet selection use similarity, new/shared terms, redundancy, diversity, boundary signals, and fixed budgets.
- Protected reranking uses dense/facet scores and identity deduplication.
- Quantile filters use candidate dense and facet scores without gold labels.
- `is_gold` and `gold_units` are carried into outputs for recall, yield, false-insert, and error analyses only.
- `stage1_gold_preserve_compare.py` is an explicit oracle diagnostic and is excluded from deployable or confirmatory method evidence.

Decision: `NO_GOLD_LABEL_USED_IN_RETRIEVAL_SELECTION_FOUND`.

## The 400-Query Problem

There was no single statistically justified reason for 400 in the earlier work.

- Stage1 used 200 HotpotQA plus 200 MuSiQue rows inherited from the Stage0 probe. This was a convenience development sample.
- Stage2F and Stage2G each used the next 200 rows per dataset to preserve disjointness and a balanced benchmark cadence. Their 400-query sizes were not selected by an a priori power or event-count calculation.
- Original Stage4A used 400 official-indexed mirror rows as a pilot convenience size. Its 10-gain gate had no recorded operating-characteristic analysis. At the observed gain prevalence of 0.02, `n=400` had probability 0.2821 of reaching 10 gains.

Consequences:

- Stage1-2E numerical results are exploratory.
- Stage2F-G remain valid frozen tests of their declared gates, but non-significant or failed gates must be interpreted with Type II error caution; they do not establish absence of a smaller effect.
- Original Stage4A's STOP cannot support a feasibility conclusion and remains invalidated.

## The 2,800-Query Problem

The exact-binomial result is correct: with event prevalence `p=0.01`, `n=2,800` gives probability 0.952994 of observing at least 20 gains. The scientific link is incomplete:

- Stage3C explicitly defines 20 as a planning rule, not a universal sample-size law.
- Twenty positive events do not by themselves establish adequate data for a controller with unspecified feature dimension, regularization, calibration, and held-out evaluation.
- The calculation is not power for a retrieval-effect endpoint and does not control precision of gain prevalence, harm risk, or cross-dataset performance.
- The `p=0.01` assumption is informed by an invalidated mirror pilot and therefore is a sensitivity assumption, not an official-data lower bound.

Before Stage4A can execute, the protocol must choose one objective and design to it:

1. Feasibility estimation: set a required confidence-interval precision for official gain and harm prevalence.
2. Retrieval-effect testing: predeclare a minimum meaningful paired CR/ER effect and compute paired-test power or simulation-based operating characteristics.
3. Selector development: predeclare the model class, feature count, train/calibration/test split, minimum positive and harm events per partition, and validate adequacy by simulation or a learning-curve pilot that is separate from final evaluation.

Until then, `2,800` is retained only as an event-collection lower bound and no official rows may be extracted for metrics.

## Statistical Fallacy Scan

Coverage: 11/11 checked using the academic-research-suite validation guide.

| Fallacy | Finding | Action |
|---|---|---|
| Simpson's paradox | No direction reversal found, but pooled Stage1/2F effects mask strong HotpotQA-MuSiQue heterogeneity. | Always report dataset splits; do not use pooled evidence as universal. |
| Ecological fallacy | Not detected. Query-level outcomes are available. | Keep inference at query and benchmark scope. |
| Berkson's paradox | Not detected, but contiguous development slices limit representativeness. | Treat external validity as unresolved. |
| Collider bias | Not detected; no causal-control model is used. | No action beyond claim discipline. |
| Base-rate neglect | Detected in the old 400-query Stage4A gate and still relevant to sparse gain/harm events. | Use prevalence-aware operating characteristics and report event counts. |
| Regression to the mean | Not detected. | No extreme-score pre/post claim is used. |
| Survivorship bias | Not detected; no queries were silently dropped and missing gold is zero. | Preserve all-row audits. |
| Look-elsewhere effect | Detected in Stage1-2E configuration search; Stage2F reports 69 intervals but only frozen gates are inferential. | Mark early work exploratory and secondary intervals descriptive. |
| Garden of forking paths | Detected in Stage1-2E because protocols and many variants were not frozen before results. | Do not promote selected early configurations to confirmatory findings. |
| Correlation implies causation | Not detected in the retrieval comparisons; Stage2H predictor associations remain diagnostic. | Avoid causal language for uncertainty features. |
| Reverse causality | Not applicable to the paired retrieval intervention. | No action. |

## Final Research State

- Last completed stage: `Stage3C`, evidence class `DESCRIPTIVE_PLANNING_ONLY`.
- Current research position: `BETWEEN_STAGE3C_AND_STAGE4A_DESIGN`.
- Stage3B: `KEEP_LOCKED`.
- Current boundary-only controller: `RETIRED_UNSUPPORTED`.
- Original Stage4A: `ARCHIVED_INVALIDATED`.
- Restarted Stage4A: `RETURNED_FOR_DESIGN_REVISION`; no extraction, embeddings, retrieval metrics, or controller fitting authorized.

No previous result file is deleted. The audit changes the allowed interpretation and the stage-control state, not the recorded execution history.
