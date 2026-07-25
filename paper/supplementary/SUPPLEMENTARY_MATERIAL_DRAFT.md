# Supplementary Material

Status: `SUPPLEMENTARY_DRAFT_COMPLETE_FOR_CURRENT_EVIDENCE`

This document contains protocol and provenance detail intentionally omitted from
the main narrative. It does not introduce new experiments or reinterpret frozen
decisions.

## A. Full experimental governance

The experimental program separates scientific authorization from engineering
execution. Each formal stage freezes its question, inputs, comparisons,
endpoints, decision rules, and permitted channels before official results are
opened. Routine engineering corrections do not change the scientific contract.
Stage4E through Stage5A are closed and frozen; Stage5R is a manuscript-only
transaction.

Static HGRAG and the adaptive controller are distinct claims. The controller
line reduced resources but failed its selection-direction gate; later mechanism
studies were negative or inconclusive. These results prohibit advancing that
controller but do not overwrite the static method's answer-quality evidence.

## B. Dataset boundaries and zero-overlap audits

The project uses frozen closed-candidate subsets of HotpotQA train distractor
v1.1 and MuSiQue answerable train v1.0. IDs are selected deterministically,
frozen before Gold evaluation, and checked against prior formal boundaries.
Stage4E, Stage4F, Stage4H, Stage4I, and Stage5A use the query counts reported in
the main paper. The sidecar and native confirmation boundaries each contain
1,000 HotpotQA and 1,500 MuSiQue queries and have zero overlap with the earlier
project boundaries.

“Zero overlap” is a project-boundary property. It does not imply that the
questions were absent from language-model pretraining.

## C. Model and environment identities

- Compact retriever: frozen MiniLM revision recorded in stage manifests.
- Strong retriever: `BAAI/bge-large-en-v1.5` at frozen revision
  `d4aa6901...`.
- Primary generator: `Qwen/Qwen2.5-1.5B-Instruct` at revision
  `989aa798...`, FP16.
- Transfer generator:
  `google/gemma-4-E2B-it-qat-mobile-transformers` at revision
  `dd693ff4...`, official mobile-QAT, thinking disabled.
- Recorded Stage5A environment: CPython 3.12.0, PyTorch 2.12.1+cu130,
  Transformers 5.14.1, NumPy 2.5.1, RTX 4060 Laptop GPU.

The generator comparison is not a pure architecture comparison because model
format and runtime differ.

## D. Full method definitions

For each query, sentence units are encoded and cosine-ranked. Adaptive balls are
deterministically split from a root set using centroids, radius, compactness,
minimum child size, and a maximum depth. Query-aware facet terms select
cross-ball hyperedges through frozen novelty, size, relevance, redundancy, and
score gates. The compact ranker protects the first ten Dense units, accepts
eligible expansion units above the frozen q25 floor, inserts at most four, and
truncates to effective Top-20. Full formulas and algorithm prose are maintained
in [`METHODS_AND_RESULTS_TABLES.md`](../METHODS_AND_RESULTS_TABLES.md).

The Stage4I sidecar preserves BGE as the primary ranking and uses the frozen
MiniLM structure only for candidate eligibility. Stage5A reconstructs the
geometry and expansion in BGE space. Neither uses answer labels during
retrieval.

## E. Development configuration tables

Stage5A evaluates a finite pre-registered BGE-native family on a development
boundary. Geometry feasibility is Gold-free. Eligible development configurations
are evaluated under fixed answer metrics and selection rules; `C10` is frozen
for confirmation. Its development answer-F1 difference `+0.003143` records the
selection process only. It is not pooled with or used to reinterpret
confirmation.

The exact configuration inventory, gates, and hashes are in
[`docs/STAGE5A_BNH_EXPERIMENT_CARD.md`](../../docs/STAGE5A_BNH_EXPERIMENT_CARD.md)
and `results/stage5a_bnh_development_selected_config.json`.

## F. Complete dataset-level results

The machine-readable full results are:

- `results/stage4e_e2e_official_train1000_v1_evaluation_summary.json`;
- `results/stage4f_xdr_musique_train3000_v1_evaluation_summary.json`;
- `results/stage4g_gtr_gemma_hotpot1000_musique3000_v1_dataset_summaries.json`;
- `results/stage4h_cbe_hotpot1000_musique1500_v1_dataset_summaries.json`;
- `results/stage4i_sdc_hotpot1000_musique1500_v1_dataset_summaries.json`;
- `results/stage5a_bnh_confirmation_dataset_summaries.json`.

The dataset-equal-weight Stage5A Protected−BGE result is
`-0.003046 [-0.006880, 0.000631]` for answer F1 and
`-0.003667 [-0.007667, 0.000004]` for EM. HotpotQA is
`-0.002907 [-0.008682, 0.002652]`; MuSiQue is
`-0.003184 [-0.008486, 0.001863]`.

## G. Bootstrap and decision rules

Formal endpoint differences use paired query bootstrap with 10,000 iterations
and frozen seeds. Joint results give equal weight to datasets rather than
queries. Stage-specific advancement rules are applied to the frozen
distributions and independently reconstructed. No Stage5R analysis recomputes
or pools bootstrap samples.

An interval containing zero is called `INCONCLUSIVE`. No equivalence margin was
registered, so equivalence is not claimed. The sample sizes are minimum
resource/precision boundaries, not power guarantees.

## H. Gold isolation and independent verifier

Each transaction separates:

1. Gold-free query/ranking construction;
2. deterministic prompt construction and generation;
3. pre-Gold artifact verification;
4. Gold identity verification and official scoring;
5. bootstrap and frozen decision;
6. independent post-Gold verification.

Verifiers reconstruct row identity, types, nullability, rankings, prompt
prefixes, metrics, resampling outputs, decisions, and artifact hashes. Gold
targets are unavailable to candidate construction and generator selection on
confirmation boundaries.

## I. Controller negative and mechanism evidence

The frozen U1-D controller achieved approximately 40% resource reduction but
retained gain queries less effectively than harm queries. Stage4C found the raw
controller score oriented in the wrong direction for gain-versus-harm
separation. Stage4D found partial candidate-level signal but failed its fixed
advancement panel. These studies support closing the controller line. They do
not imply that static HGRAG is invalid.

The detailed controller artifacts remain part of repository history but are not
used to choose any Stage4E–Stage5A ranking.

## J. Full efficiency and resource tables

Efficiency summaries report insertion counts, prompt tokens, retrieval or
reconstruction time, generation time, GPU peak memory, cache identity, and
failure counts. These are descriptive for the recorded hardware. They do not
support claims that Qwen is faster on all devices or that model architecture
alone determines resource use.

Stage5A records 8.544 seconds for retrieval reconstruction, 887.650 seconds for
BGE generation, 884.198 seconds for BGE-native Protected generation, and
3.592 GiB peak GPU memory. All four confirmation methods have the same query
set, fixed prompt contract, and zero promoted generation failure.

## K. Artifact manifests and reproducibility

The frozen stage manifests bind formal inputs and outputs by path, byte length,
and SHA-256. Stage5R adds only derived paper files. Its figure manifest binds all
inputs, source CSVs, and four exports per figure. A read-only verifier checks the
manifest and manuscript contracts.

Historical regression evidence remains:

- Stage4E–Stage4I unified suite: 89/89 PASS;
- Stage4D independent frozen environment: 17/17 PASS;
- Stage5A targeted regression: recorded anew in the Stage5R audit;
- Stage5-PMC material verifier: PASS;
- Stage5R two-build byte identity and combined material verifier: required PASS.

These counts describe their recorded suites; they are not a substitute for
artifact identity checks.

## L. Additional evidence transitions

Post-decision Gold transitions for protected expansion are:

| Boundary | Dataset | Added Gold | Displaced Gold | Net Gold | Role |
|---|---|---:|---:|---:|---|
| Cross-space sidecar | HotpotQA | 21 | 29 | -8 | Post-decision descriptive |
| Cross-space sidecar | MuSiQue | 59 | 50 | +9 | Post-decision descriptive |
| BGE-native | HotpotQA | 3 | 2 | +1 | Post-decision descriptive |
| BGE-native | MuSiQue | 16 | 15 | +1 | Post-decision descriptive |

The native net counts are positive while answer-F1 point differences are
negative. The audit therefore illustrates the manuscript's central distinction:
added evidence, retained evidence, placement, and answer utility are not the
same endpoint.

## Supplementary scope boundary

Reservation, Stage3B, U2, full-wiki, new generators, new strong retrievers, and
new controller development remain outside Stage5R. No supplementary statement
should be read as authorization to open those boundaries.
