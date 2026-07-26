# Manuscript-Level Evaluation Response — 2026-07-26

Status:

```text
MANUSCRIPT_LEVEL_EVALUATION_READ
PAPER_ONLY_CORRECTIONS_APPLIED
FROZEN_SCIENTIFIC_RESULTS_UNCHANGED
NEW_EXPERIMENTS_NOT_AUTHORIZED
```

## Scope

This response maps `HyperGranular_RAG_论文水平评估与优化路线.md` to the
current repository manuscript. The evaluation describes a 12-page version,
whereas the repository already contained a later 13-page revision at commit
`2c775bdf5f9bfbdfa6770a07df26b632058e7328`. Several concerns in the evaluation
had therefore already been addressed before this response.

The external assessment is treated as review input, not as authorization to
open a new scientific stage. Frozen Stage4E–Stage5A results were read only.

## Resolution Map

| Evaluation concern | Current disposition | Action in this revision |
|---|---|---|
| Strong BGE boundary hidden or understated | Already resolved | Main text retains the negative Full−BGE result and both inconclusive BGE extensions; an absolute strong-boundary table is added in the appendix |
| Granular-ball necessity implied without ablation | Already resolved | Abstract, limitations, conclusion, and claim table explicitly state that necessity is not established |
| Hyperedge superiority over generic diversity/coverage | Already resolved | The manuscript explicitly states that MMR/coverage-style alternatives were not tested |
| “Gold-free” is ambiguous | Resolved now | Replaced by “inference-time label-free after development-time configuration freeze”; development Gold, confirmation Gold, and inference execution are separated |
| Method definition and threshold provenance incomplete | Resolved or bounded now | Added three deterministic procedures, exact gates and tie-breaking, complexity, and the Stage2E calibration origin of the exact q25 floor |
| Absolute metrics missing | Resolved now | Added F1/EM/CR@20/ER@20 for compact and strong boundaries, plus average inserted units and answer-F1 gain/harm query counts reconstructed from frozen artifacts |
| Internal Stage identifiers dominate the narrative | Resolved now | Main body uses semantic boundary names; Stage IDs remain only where useful for appendix provenance |
| Evidence-state map, applicability map, and claim table are repetitive | Resolved now | The evidence-state figure is no longer included in the paper; its source/export remains tracked and is not deleted |
| Mechanism explanation is shallow | Partially resolved | Existing frozen displacement, controller, and candidate-probe audits remain visible; no post-hoc case taxonomy is presented as confirmation |
| Closed-candidate external validity | Already explicit | Full-wiki, ANN recall, corpus noise, indexing cost, and open-domain effectiveness remain limitations |

## Frozen Derived Analysis Added

The paper-material builder now verifies and reads the frozen compact rankings
and query audits to reconstruct descriptive quantities:

| Boundary | Queries | Avg. inserted units | Answer-F1 gain/harm queries |
|---|---:|---:|---:|
| MiniLM / HotpotQA confirmation | 1,000 | 1.9300 | 47/34 |
| MiniLM / MuSiQue confirmation | 3,000 | 2.4110 | 125/77 |
| MiniLM / joint component confirmation | 2,500 | 2.1628 | 102/73 |

These are descriptive reconstructions from already frozen artifacts. They do
not change any endpoint, bootstrap interval, decision, or scientific claim.
Average insertions include all queries.

## Items That Require a New Scientific Stage

The following review suggestions are experiments, not manuscript edits:

- matched Dense+MMR, lexical-coverage, K-means, and random-insertion baselines;
- BGE-native Top-5/Top-10 evaluation;
- low-confidence triggering or dynamic insertion budgets;
- a new utility predictor or reranker;
- confirmatory parameter sensitivity;
- a third dataset or a second strong retriever;
- full-wiki/open-domain evaluation;
- a post-hoc case taxonomy selected using answer or Gold outcomes.

Running any of these would introduce a new comparator, endpoint boundary,
candidate policy, data source, or scientific interpretation. Under the current
repository rules, they require a new lightweight experiment card and a fresh
development/confirmation boundary. None was run in this revision.

If a new stage is later authorized, the highest-information first question is
whether the frozen structural selector outperforms matched simple completion
controls under the same candidate set, protected prefix, insertion budget,
generator, prompt, and Top-k. Strong-retriever Top-5/Top-10 should remain a
separate question so that comparator necessity is not conflated with a changed
context budget.

## Claim Boundary After Revision

The defensible paper claim remains:

> HyperGranular-RAG is a structured evidence-completion layer for compact
> dense retrieval under a fixed context budget. It repeatedly improves the
> frozen historical MiniLM backbone, while the original method is weaker than
> strong BGE and the tested BGE extensions do not establish incremental
> answer-quality value. The frozen evidence does not establish granular-ball
> necessity, generic hyperedge superiority, broad generator robustness, or
> open-domain effectiveness.
