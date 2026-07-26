# HyperGranular-RAG: Structured Evidence Completion for Compact Multi-Hop Retrieval

Manuscript status: `CURRENT_EVIDENCE_MANUSCRIPT_COMPLETE`
Submission status: `SUBMISSION_METADATA_PENDING`
Evidence cutoff: Stage5A-BNH, commit
`02128346cf2b0c088e388f8ea796fadfb9d596b4`

## Abstract

Multi-hop retrieval-augmented generation must assemble complementary evidence
within a fixed context budget, yet relevance-only rankings may omit bridge
evidence and unconstrained expansion may displace useful items. We introduce
HyperGranular-RAG, an inference-time evidence-completion framework that
organizes candidate sentences into adaptive granular balls, connects
query-relevant balls with facet hyperedges, and inserts a small number of
candidates after a protected dense prefix. Across three closed-candidate
HotpotQA and MuSiQue evaluations with Qwen2.5-1.5B-Instruct,
HyperGranular-RAG improves answer F1 over a compact MiniLM retriever by
`+0.01478 [0.00020, 0.02988]`, `+0.01140 [0.00450, 0.01835]`, and
`+0.01357 [0.00491, 0.02233]`. A matched ablation further shows a
`+0.01336 [0.00341, 0.02343]` gain for facet-conditioned selection over
centroid-only expansion. With BGE large-en-v1.5, the original system
underperforms the strong dense baseline, while cross-space and BGE-native
extensions yield no statistically resolved improvement. Holding the inserted
set fixed, protected placement improves over unprotected placement. These
findings show that structured evidence completion can recover evidence gaps for
a compact retrieval backbone, while its marginal value contracts with a
stronger retriever. Paired bootstrap intervals, pre-specified evaluation
settings, and independent artifact verification support these scoped
conclusions.

## 1. Introduction

Retrieval-augmented generation (RAG) gives language models access to
non-parametric evidence at inference time [@lewis2020rag; @guu2020realm].
Dense passage retrieval provides an effective learned relevance ordering
[@karpukhin2020dpr], but multi-hop questions introduce a joint-coverage
requirement: the selected context must contain multiple pieces of evidence, not
merely high-scoring passages considered independently. HotpotQA and MuSiQue make
this requirement explicit through multi-hop questions and supporting evidence
annotations [@yang2018hotpotqa; @trivedi2022musique].

Under a fixed Top-k budget, recovering a missing bridge necessarily competes
with evidence already selected by the retriever. If individually similar units
occupy much of the ranking, a complementary bridge may remain outside the
generator context. Expansion can recover that bridge, but every insertion can
displace an item that the base retriever ranked highly. Moreover,
retrieved evidence is not uniformly useful to a generator: position, redundancy,
prompt construction, and the generator itself affect whether a retrieved item
changes the answer [@liu2024lostmiddle; @ram2023incontext]. Evidence coverage,
ranking placement, and answer utility must therefore be measured separately.

HyperGranular-RAG (HGRAG) is a structured evidence-completion layer for dense
retrieval under this fixed context budget. It organizes sentence units into
adaptive granular balls, identifies cross-ball relations through query-aware
facet hyperedges, and inserts at most four eligible units after a protected
Dense Top-10 prefix while preserving an effective Top-20. After
development-time configuration, retrieval on confirmation data proceeds
without access to answers, supporting-fact labels, generator outputs, or
downstream scores. Development labels are used only for designated
configuration selection and remain separate from confirmation evaluation.
Granular balls act as adaptive local clusters in embedding space, while
hyperedges represent higher-order relations involving more than pairwise
adjacency [@xia2019granularball; @feng2019hgnn].

We evaluate whether structured evidence completion improves compact dense
retrieval and whether the same mechanism provides additional value with a
stronger retriever. The study covers pre-specified HotpotQA and MuSiQue
closed-candidate settings, matched component contrasts, one additional
generator configuration, a BGE large-en-v1.5 baseline, a cross-space BGE
sidecar, and a BGE-native reconstruction. Development choices remain separate
from confirmation, and independent verifiers reconstruct the reported
comparisons.

Our study yields three main findings. First, static HGRAG repeatedly improves
answer F1 over the compact MiniLM Dense backbone in the three Qwen evaluations.
Second, facet-conditioned selection improves over the specific centroid-only
NoFacet ablation within that system. Third, when the cross-space sidecar holds
the inserted candidate set constant, protected placement improves over direct
unprotected placement. The gains are backbone-dependent: the original system
falls below BGE, and neither tested BGE extension yields a statistically
resolved answer-quality improvement. Our conclusions are restricted to the
evaluated closed-candidate settings; open-domain retrieval, broader generator
transfer, and the independent necessity of granular balls remain open
questions.

We make three contributions:

1. We introduce a structured evidence-completion layer that combines adaptive
   granular-ball organization, query-aware facet hyperedges, and protected
   budget-constrained insertion under a fixed Top-k budget.
2. Through controlled HotpotQA and MuSiQue evaluations, we establish repeatable
   answer-F1 gains over a compact MiniLM retriever and matched evidence for
   facet-conditioned selection over centroid-only expansion.
3. Through component, placement, generator-transfer, and strong-retriever
   studies, we characterize when structural completion provides marginal value
   and when that value contracts, with independently verifiable artifacts
   supporting the reported scope.

## 2. Related Work

### 2.1 Dense and multi-hop retrieval

Dense passage retrieval learns dual-encoder representations for efficient
passage ranking [@karpukhin2020dpr]. Multi-hop variants extend retrieval from
independent passages to evidence chains. Multi-Hop Dense Retrieval conditions
later retrieval on preceding evidence [@xiong2021mdr], while BeamDR uses beam
search over dense reasoning paths [@zhao2021beamdr]. PullNet iteratively expands
from retrieved entities over text and knowledge bases [@sun2019pullnet], and
IRCoT interleaves retrieval with chain-of-thought reasoning
[@trivedi2023ircot]. HGRAG is not an iterative question-rewriting method.
Within each fixed closed candidate set, it performs a single bounded
completion of an existing ranking.

### 2.2 Graph, hypergraph, and hierarchical retrieval

Structure-aware retrieval represents relations that a flat relevance ordering
can miss. RAPTOR retrieves from a tree of recursively summarized text
[@sarthi2024raptor]. HippoRAG combines a knowledge graph with personalized
propagation [@gutierrez2024hipporag], and GNN-RAG uses graph-neural retrieval
over knowledge graphs [@mavromatis2025gnnrag]. GraphRAG targets
query-focused summarization using graph communities and is currently documented
as a preprint [@edge2024graphrag]. HGRAG differs in its evidence unit, relation,
and budget contract: adaptive balls organize local sentence units; facets define
query-conditioned cross-ball hyperedges; and insertion preserves a dense prefix
instead of replacing the complete ranking. These graph systems address broader
construction and retrieval settings, whereas our study isolates bounded
completion within a fixed candidate set; direct comparison is left to future
work.

### 2.3 Evidence expansion under context budgets

Retrieval-enhanced language models can expose far more external evidence than
the model parameters alone [@lewis2020rag; @guu2020realm], but the generator
still consumes a finite context. RECOMP explicitly studies selective and
compressed augmentation [@xu2024recomp]. Long-context studies show that
evidence position affects model use even when the information is present
[@liu2024lostmiddle]. HGRAG treats this as a ranking constraint: an expansion
candidate must pass a fixed eligibility floor, insertion is capped, and the
base ranking's first ten unique units are protected.

### 2.4 Retrieval–generation interaction

Retrieval quality and answer quality are coupled but not interchangeable.
Fusion-in-Decoder demonstrates the importance of how multiple passages are
consumed by the generator [@izacard2021fid], while in-context RALM shows that
retrieved text can condition language models without parameter updates
[@ram2023incontext]. Our endpoint is therefore paired answer F1, with retrieval
complete recall and evidence recall as supporting measurements. Post hoc gold
transitions describe a mechanism but do not determine efficacy.

A simpler completion rule could combine relevance with diversity or uncovered
query-term coverage without constructing higher-order relations. The NoFacet arm
in this study is narrower: it preserves granular-ball geometry and selects up
to two eligible balls by query-to-centroid score. It is therefore a matched
test of the pre-specified facet-conditioned selector against centroid-only ball
expansion, not a comparison with all relevance–diversity or coverage
objectives.

### 2.5 Evaluation, reproducibility, and negative evidence

KILT emphasizes provenance-aware evaluation in knowledge-intensive tasks
[@petroni2021kilt]. Machine-learning reproducibility guidance motivates explicit
dependencies, artifacts, and reporting boundaries
[@pineau2021reproducibility]. Statistical uncertainty is not resolved by
relabelling an interval crossing zero as “no effect” or equivalence
[@amrhein2019retire]. We therefore report comparisons as supported, negative,
statistically unresolved, or without a matched estimand.

## 3. HyperGranular-RAG

### 3.1 Problem formulation

For a query \(q\), let \(U_q=\{u_i\}\) be the closed candidate set of sentence
units. A fixed encoder maps the query and each `title + ". " + sentence` unit
to an L2-normalized representation. The base relevance score is cosine similarity,

\[
s(q,u_i)=\hat e_q^\top \hat e_i.
\]

Ties are resolved by ascending `unit_id`. The Dense baseline returns the first
\(K_q=\min(20, |U_q|)\) unique units. HGRAG constructs an additional ordered set
of eligible units but must return the same effective \(K_q\). No answer, gold
supporting unit, or generator output enters this construction.

### 3.2 Adaptive granular balls

Each query's candidate embeddings begin as one root set. For a current ball
\(B\),

\[
c_B=\operatorname{norm}\left(\frac{1}{|B|}\sum_{i\in B}\hat e_i\right),
\qquad d_i=1-\hat e_i^\top c_B,
\]

with radius \(r_B=\max_{i\in B}d_i\) and compactness
\(1-|B|^{-1}\sum_{i\in B}d_i\). In the compact MiniLM variant, \(B\) is split
iff its depth is below 6, \(|B|\ge 4\), and either \(|B|>3\) or \(r_B>0.78\).
The first seed is the unit farthest from \(c_B\); the second has minimum cosine
similarity to the first. Each unit is assigned to the seed with higher cosine
similarity. A split is retained only when both children contain at least two
units. Ties preserve candidate order. We keep these parameters fixed across
evaluation settings; they are not learned from confirmation data.

### 3.3 Query-aware facet hyperedges

Each ball aggregates content terms from titles and sentences after the fixed
ASCII-alphanumeric and stop-word rules. Its facet terms are the intersection
between ball terms and query terms. The two balls with highest
query-to-centroid cosine become seeds. A non-seed ball can form an expansion
hyperedge only if it introduces a new query term and passes fixed gates on ball
size, ball score or seed proximity, units per new term, and shared-term
redundancy.

We use *facet hyperedge* for this query-conditioned relation between the seed
balls and an expansion ball that contributes new query-term coverage.

For a candidate ball \(B\), let \(n_B\) be the number of query terms newly
covered beyond the seeds, \(t_B\) the total number of query terms in \(B\),
\(m\) the query-term count, \(b_B=\hat e_q^\top c_B\), \(a_B\) the maximum
cosine to a seed centroid, and \(\rho_B\) the fraction of \(B\)'s facet terms
already covered. The compact-variant score is

\[
h_B =
0.45\frac{n_B}{\max(m,1)}
+0.20\frac{t_B}{\max(m,1)}
+0.20b_B
+0.15(1-a_B)
-0.20\rho_B
-0.05\frac{|B|}{8}.
\]

A candidate must introduce at least one new term, contain at most 8 units,
satisfy \(b_B\ge0.12\) or \(a_B\ge0.05\), have at most 6 units per new term,
obey \(\rho_B\le0.90\), and have \(h_B\ge0.10\). Candidates are ordered by
descending \(h_B\) and then `edge_id`; at most two distinct balls are selected.
Units inside an accepted ball remain ordered by original MiniLM cosine and
`unit_id`; the fixed unit-level facet bonus is zero. Thus the hyperedge selects
candidate regions rather than learning a new dense ranker.

### 3.4 Protected bounded insertion

The compact variant protects the first ten unique Dense units. HGRAG units
whose cosine is at least `0.1957079917192459` are considered in the
pre-specified order. At most four candidates absent from the protected prefix are
inserted immediately after that prefix. Remaining Dense units are appended in
their original order, followed only if necessary by unfilled expansion units,
and the result is truncated to \(K_q\).

We set the candidate-score floor to `0.1957079917192459`, the 25th percentile
selected during earlier development, and keep it fixed in all subsequent
evaluations. We do not treat it as a theoretically privileged or independently
optimized value.

Protected insertion reduces the risk of displacing highly ranked evidence, but
it does not guarantee that an inserted candidate is useful. This distinction
motivates the placement and BGE comparisons below.

### 3.5 Compact-dense, sidecar, and native variants

The **compact variant** uses MiniLM embeddings for the base ranking, ball
geometry, facet gates, and unit ordering. The **cross-space sidecar** keeps BGE
Top-20 as the primary ranking while using the fixed MiniLM-HGRAG structure to
propose eligible candidates; no score fusion is introduced. The **BGE-native
variant** reconstructs candidate geometry and structural selection in the BGE
space under one configuration selected during development and then fixed for
confirmation. We evaluate the three variants separately because each isolates
a different interaction between structural completion and the base retriever.

With precomputed \(d\)-dimensional embeddings, Dense scoring and sorting cost
\(O(|U_q|d+|U_q|\log |U_q|)\). Recursive ball assignment costs
\(O(H|U_q|d)\) for maximum depth \(H\), because every unit is compared with two
seeds at each visited depth. Facet scoring costs
\(O(|U_q|+|\mathcal{B}_q|d+|\mathcal{B}_q|\log|\mathcal{B}_q|)\) apart from
tokenization, and bounded insertion is linear in ranking length. Working
memory is \(O(|U_q|d+|U_q|+|\mathcal{B}_q|)\). These bounds exclude encoder and
generator inference and describe the closed candidate set used here.

The static method is also distinct from the closed adaptive-controller line.
The controller attempted query-level insertion selection and produced negative
or inconclusive evidence. Its failure does not alter the static ranking or the
static method's confirmed comparisons.

## 4. Experiments

### 4.1 Datasets and evaluation settings

HotpotQA provides diverse multi-hop questions and supporting facts
[@yang2018hotpotqa]; MuSiQue composes single-hop questions to reduce shortcut
solutions [@trivedi2022musique]. We evaluate retrieval within the candidate sets
supplied by each benchmark; corpus-scale indexing is outside the scope of this
study.

We evaluate the compact variant on 1,000 HotpotQA queries, 3,000 MuSiQue
queries, and a separate component set with 1,000 HotpotQA and 1,500 MuSiQue
queries. The cross-space sidecar and BGE-native confirmation studies each use a
separate, zero-overlap set with 1,000 HotpotQA and 1,500 MuSiQue queries. Query
selection is deterministic, and we verify dataset and query identities.

### 4.2 Retrievers and generators

The compact baseline is the fixed MiniLM dense retriever used throughout the
original development program. BGE
large-en-v1.5 is the pre-specified strong dense baseline; the broader BGE family
is documented by Xiao et al. [@xiao2023bge], while the exact model revision is
bound in repository manifests.

The main generator is Qwen2.5-1.5B-Instruct FP16 with a fixed short-answer RAG
prompt and a 4,096-token input cap. One additional transfer evaluation uses
`google/gemma-4-E2B-it-qat-mobile-transformers` in its official mobile-QAT
format. Because Qwen and Gemma use different numerical formats and runtimes,
this comparison characterizes the tested deployment configurations rather than
intrinsic architectural quality or cross-device efficiency.

### 4.3 Experimental design

We specify all method and decision parameters before evaluating the
corresponding confirmation split. The BGE-native development study selected
configuration `C10` with a development answer-F1 difference of `+0.003143`.
We use this development result only to select C10 and report its confirmation
performance separately. The pre-registered confirmation outcome ended the
BGE-native configuration search.

### 4.4 Metrics and statistical decisions

The primary endpoint is paired query-level answer-F1 difference. Answer exact
match (EM), retrieval complete recall at 20 (CR@20), and evidence recall at 20
(ER@20) are supporting endpoints. Each comparison uses 10,000 paired bootstrap
samples and pre-specified decision rules. Dataset-joint comparisons assign
equal weight to HotpotQA and MuSiQue. An interval crossing zero is
statistically unresolved and is not interpreted as equivalence because no
equivalence margin or formal equivalence test was specified.

The sample sizes define available resource and interval precision. They are not
presented as a formal power guarantee.

### 4.5 Label access and evaluation integrity

On confirmation data, candidate construction, retrieval, prompting, and
generation proceed without access to answer labels, supporting-fact
annotations, or evaluation feedback. Designated development labels may select
a configuration, including BGE-native C10, whereas confirmation labels remain
inaccessible until rankings, prompts, and predictions are fixed and are not
reused for selection. Thus “label-free” refers to retrieval execution rather
than the entire research process.

Evaluators verify gold identity before parsing it, and independent verifiers
reconstruct query order, metrics, bootstrap summaries, decisions, and artifact
identities. Main/rerun evaluations are either byte-identical in full or use a
pre-hash deterministic subset whose selected outputs match the corresponding
main outputs exactly. The manuscript reads the completed scientific decisions
and manifests without recomputation.

## 5. Results

### 5.1 Repeated gains over compact dense retrieval

Table 1 and Figure 2 show three Qwen comparisons. On 1,000
HotpotQA queries, Full−Dense answer F1 is
`+0.01478 [0.00020, 0.02988]`. On 3,000 MuSiQue queries, the difference is
`+0.01140 [0.00450, 0.01835]`. The separate joint component evaluation again
supports Full−Dense with a dataset-equal-weight difference of
`+0.01357 [0.00491, 0.02233]`.

| Setting | F1 Dense/Full | EM Dense/Full | CR@20 Dense/Full | ER@20 Dense/Full | Avg. inserted units | F1 gain/harm queries | ΔF1 [95% CI] |
|---|---:|---:|---:|---:|---:|---:|---:|
| HotpotQA confirmation | 0.42150/0.43628 | 0.35600/0.36600 | 0.73700/0.79800 | 0.87860/0.90818 | 1.9300 | 47/34 | `+0.01478 [0.00020, 0.02988]` |
| MuSiQue confirmation | 0.13595/0.14735 | 0.10033/0.11033 | 0.58900/0.65000 | 0.80553/0.84128 | 2.4110 | 125/77 | `+0.01140 [0.00450, 0.01835]` |
| Joint component confirmation | 0.30446/0.31803 | 0.25467/0.26400 | 0.66617/0.72217 | 0.84529/0.87657 | 2.1628 | 102/73 | `+0.01357 [0.00491, 0.02233]` |

The gain/harm and insertion columns are descriptive reconstructions from the
fixed rankings and query records. Average insertions include all queries. The
Joint absolute metrics are dataset-equal-weighted; its counts use all 2,500
queries.

HGRAG improves answer F1 in all three compact-retriever evaluations, with
effect sizes from `+0.01140` to `+0.01478`. These gains apply to the MiniLM
backbone, Qwen generator, fixed prompt, closed candidates, and Top-20 budget;
the strong-retriever experiments below evaluate whether the pattern extends to
BGE.

### 5.2 Component evidence

Within the fixed MiniLM system, Full−NoFacet is
`+0.01336 [0.00341, 0.02343]`, supporting an incremental role for facet
conditioning relative to the specific centroid-only ball selector. This matched
contrast isolates facet conditioning within the granular-ball candidate pool;
generic relevance–diversity and coverage selectors remain outside the present
comparison.
Full−NoProtection is
`+0.00354 [-0.00675, 0.01389]`, so the independent contribution of protection
is statistically unresolved in that setting. We do not report a flat-unit
granular-ball ablation because ball seeds, split gates, edge budgets, and radii
have no unique matched counterparts at the unit level. This missing matched
estimand provides no evidence for or against a granular-ball effect.

In the cross-space sidecar, the inserted set is identical between protected and
unprotected conditions. Protected−Unprotected is
`+0.01122 [0.00129, 0.02104]`, which supports the placement rule within that
specific sidecar. However, Protected−NoFacet is
`-0.00743 [-0.01616, 0.00132]`, statistically unresolved. In BGE-native space,
Protected−Unprotected is `+0.003367 [-0.001285, 0.008026]`, and
Protected−NoFacet is `+0.000631 [-0.004220, 0.005365]`; both are
statistically unresolved. Component effects are therefore system-dependent.

The complete ablation state is:

| Contrast | Answer-F1 difference [95% CI] | State |
|---|---:|---|
| MiniLM Full−NoFacet | `+0.01336 [0.00341, 0.02343]` | Supported |
| MiniLM Full−NoProtection | `+0.00354 [-0.00675, 0.01389]` | Statistically unresolved |
| Sidecar Protected−Unprotected | `+0.01122 [0.00129, 0.02104]` | Supported |
| Sidecar Protected−NoFacet | `-0.00743 [-0.01616, 0.00132]` | Statistically unresolved |
| BGE-native Protected−Unprotected | `+0.003367 [-0.001285, 0.008026]` | Statistically unresolved |
| BGE-native Protected−NoFacet | `+0.000631 [-0.004220, 0.005365]` | Statistically unresolved |
| Flat granular-ball control | — | No matched estimand |

### 5.3 Comparison with a strong dense retriever

The pre-specified BGE baseline outperforms original Full. The
dataset-equal-weight Full−BGE difference is
`-0.03998 [-0.05393, -0.02621]`. The complete interval lies below zero,
distinguishing this negative result from a statistically unresolved contrast.
On this evaluation, the original MiniLM-based HGRAG system performs below the
BGE baseline.

On the same joint component setting, BM25 and a Dense–BM25 hybrid provide
additional reference points.
Full−BM25 is `-0.00755 [-0.02259, 0.00773]`, and Full−Dense–BM25 hybrid is
`-0.00320 [-0.01591, 0.00942]`. Both comparisons are statistically unresolved.
BGE remains the decisive strong baseline because the entire
Full−BGE interval is negative.

### 5.4 Cross-space sidecar evaluation

The cross-space sidecar asks whether the fixed MiniLM structural expansion can
add complementary candidates while BGE retains the primary ranking. Its core
Protected−BGE difference is `-0.00256 [-0.00998, 0.00458]`. The sidecar
comparison therefore remains statistically unresolved relative to BGE. The
positive protected-placement contrast answers a different question: better
placement of a fixed inserted set does not show that the set itself improves
BGE.

### 5.5 BGE-native reconstruction

The BGE-native study removes the cross-space mismatch by rebuilding candidate
geometry and facets in BGE space. Its confirmation comparison remains
statistically unresolved. The
dataset-equal-weight Protected−BGE answer-F1 difference is
`-0.003046 [-0.006880, 0.000631]`; the EM difference is
`-0.003667 [-0.007667, 0.000004]`. Dataset-specific F1 differences are
`-0.002907 [-0.008682, 0.002652]` for HotpotQA and
`-0.003184 [-0.008486, 0.001863]` for MuSiQue. Both point estimates are slightly
negative, but all intervals cross zero. The tested BGE-native reconstruction
therefore provides no statistically resolved answer-quality improvement over
BGE in this setting.

The positive C10 development difference is not pooled with this result:
development selected the configuration, and the separate confirmation split
evaluated it.

### 5.6 Generator transfer

Under the single pre-specified Gemma mobile-QAT configuration, the
dataset-equal-weight Full−Dense difference is
`+0.00516 [-0.00262, 0.01295]`, which is statistically unresolved. This
transfer result applies only to the tested Qwen FP16 and Gemma mobile-QAT
deployment configurations on the recorded RTX 4060 Laptop 8GB, fixed
short-answer prompt, and 4,096-token cap.

### 5.7 Efficiency and evidence displacement

These measurements describe the recorded hardware rather than cross-device
efficiency. For the BGE-native confirmation run, retrieval reconstruction took
`8.544` seconds; BGE and BGE-native Protected generation took `887.650` and
`884.198` seconds, respectively; recorded GPU peak memory was `3.592 GiB`.

Post hoc supporting-evidence analysis clarifies why coverage and answer quality
diverge. In the BGE-native Protected condition, HotpotQA adds 3 gold units, displaces 2,
and has net `+1`; MuSiQue adds 16, displaces 15, and also has net `+1`.
Nevertheless, answer-F1 point estimates relative to BGE are negative. In the
cross-space sidecar, HotpotQA has 21 added, 29 displaced, and net `-8`, whereas
MuSiQue has 59 added, 50 displaced, and net `+9`. These counts are
post-decision descriptive analyses and were not used to retune the method. They show
that an evidence-count increment is not an efficacy endpoint.

## 6. Discussion

### 6.1 Why compact dense retrieval can benefit

The repeated MiniLM gains support a focused interpretation: when a compact
representation leaves recoverable evidence
gaps, local candidate organization plus query-conditioned cross-ball expansion
can expose complementary units that a flat ranking omits. The joint component
confirmation's facet contrast supports the contribution of facet-mediated
candidate selection within that implementation. We therefore interpret the
repeated gains as evidence that structured completion can recover complementary
units omitted by this compact retriever.

### 6.2 Why the increment contracts under strong BGE

BGE begins with substantially higher answer quality than the original MiniLM
system. The original Full ranking is clearly worse than BGE, and both tested
extensions around BGE yield narrow intervals around small negative point
estimates. A stronger representation may already rank much of the recoverable
evidence highly, leaving a smaller marginal opportunity for structural
expansion. Additional units then compete with already strong evidence. These
results show that the marginal value of the tested structural completion
contracts with BGE; they do not determine whether other structure-aware
approaches can complement strong retrievers.

### 6.3 Evidence addition is not evidence utility

The BGE-native confirmation is especially informative: net gold evidence
increases slightly, but answer quality does not. A unit can be gold-labelled yet redundant with retained
context, weakly positioned, difficult for the generator to use, or offset by a
different displacement. Conversely, a non-gold unit can affect the answer.
Therefore CR/ER, gold transitions, and answer F1 answer different questions.

### 6.4 Placement matters but cannot substitute for efficacy

The cross-space sidecar placement result isolates ranking position because
protected and unprotected conditions contain the same inserted set. It supports
the principle that preserving high-ranked evidence can reduce harm under a
fixed budget. However, the BGE-native confirmation does not independently
confirm the placement increment, and neither placement experiment establishes
that Protected exceeds BGE. Placement is a mechanism control, not an efficacy
substitute.

### 6.5 Facet effects depend on semantic space and comparator

Facet-conditioned selection beats the centroid-only NoFacet arm in the fixed
MiniLM system, but its increments are statistically unresolved in the cross-space and
BGE-native studies. The query-to-ball geometry, seed identities, facet
eligibility, and competition with the base ranking all depend on representation
space. The joint-component effect is therefore neither transported to BGE nor
interpreted as superiority over untested diversity/coverage selectors.

### 6.6 Selection and displacement explain failure modes

Post hoc controller analyses explain why a useful static arm did not yield a
reliable adaptive policy. A resource-constrained controller retained 47 of 94
gain queries but 53 of 69 harm queries (retention gap `-0.26812`) and passed
only two of six advancement gates. Its raw query score was directionally
reversed for gain versus harm (AUROC `0.39269 [0.30558, 0.48150]`). A later
candidate-level probe recovered partial separation (AUROC
`0.64310 [0.55520, 0.72974]`; AP `0.72198`), but missed the `0.65` gate and had
worse Brier score than the prevalence baseline (`0.26321` vs `0.25338`). These
post-label development analyses are explanatory, not confirmation; they show that
detecting complementary candidates and avoiding displacement remain unresolved.

### 6.7 Separating development from confirmation

The positive BGE-native development result motivated one pre-specified
confirmation evaluation. It did not license retroactive configuration search
after confirmation. We therefore report the confirmation result without
further tuning on the confirmation set.

### 6.8 Interpreting statistically unresolved comparisons

The sidecar, BGE-native, and generator-transfer intervals cross zero. Without a
pre-specified equivalence margin and an equivalence test, these results cannot
be called equal. They also do not establish harm. The current data and
pre-specified tests do not resolve the direction within their
intervals.

## 7. Limitations

First, evaluation is closed-candidate rather than full-wiki or open-domain; it
does not measure indexing, approximate-nearest-neighbor recall, or corpus-scale
noise. Second, the repeated positive evidence uses one Qwen generator, and the
only additional generator is a single Gemma mobile-QAT configuration. Third,
only one strong BGE backbone is tested. Fourth, the BGE-native configuration
family is finite and development-selected; untested variants remain unknown.

Fifth, a scientifically matched flat granular-ball control was not defined, so
the granular-ball structure lacks an independent ablation claim. Sixth,
protected insertion has inconsistent independent evidence: cross-space sidecar
placement is supported, while the joint-component and BGE-native
protection-related contrasts are statistically unresolved. Seventh, facet evidence is representation- and
implementation-dependent. No matched relevance–diversity, maximum-coverage, or
other simple completion selector was evaluated, so the hyperedge representation
has not been shown necessary or superior to such alternatives.

Eighth, the HotpotQA training split may have appeared in generator pretraining.
The project can guarantee only that its own retrieval and evaluation respected
the pre-specified data separation. Ninth, post hoc mechanism analyses are descriptive, not
confirmatory causal analyses. Tenth, the sample sizes reflect available
resources and interval precision, not a formal power design. Finally, no
statistically unresolved result is evidence of equivalence.

## 8. Reproducibility

The repository records exact dataset and model revisions, configurations,
rankings, predictions, and evaluation outputs. Independent scripts reconstruct
the reported metrics and decisions from these artifacts. Each figure has
machine-readable source data and deterministic exports, and the manuscript
build is deterministic. Dataset and model licenses are recorded separately,
while the repository's missing code license remains a submission blocker.

## 9. Conclusion

HyperGranular-RAG provides repeatable answer-F1 gains for the compact MiniLM
retriever across three closed-candidate evaluations, and facet-conditioned
selection improves over its centroid-only comparator. The BGE experiments show
that this increment is backbone-dependent: the original MiniLM-based system
performs below BGE, while the cross-space and BGE-native extensions remain
statistically unresolved. Protected placement can improve the ordering of a
fixed candidate set, but candidate selection remains central to end-to-end
answer quality. Overall, structured evidence completion is useful in the
evaluated compact retrieval setting, while its value with stronger retrievers
remains an open methodological problem.

## Appendix A. Deterministic Procedures and Fixed Parameters

**Algorithm 1: adaptive granular-ball construction.** Initialize a queue with
\((U_q,0)\). For each ball \(B\) at depth \(z\), compute \(c_B\) and \(r_B\).
If the depth, size, and radius/size gates do not permit a split, emit \(B\).
Otherwise choose the first seed as the unit farthest from \(c_B\), choose the
second as the unit least similar to the first, and assign each unit to its more
similar seed. Candidate-order ties go to the earlier seed. Accept the split
only if both children have at least two units; otherwise emit \(B\). Continue
until the queue is empty. Stable candidate order and `unit_id` resolve
remaining ties.

**Algorithm 2: query-aware facet-hyperedge selection.** Tokenize the query and
every ball with the frozen rules, intersect each ball's term set with the
query-term set, and select the two highest query-to-centroid balls as seeds.
Compute newly covered terms and the frozen \(h_B\) score for every non-seed
ball. Reject balls that fail any eligibility gate. Sort survivors by
\((-h_B,\texttt{edge_id})\), retain at most two distinct balls, and order their
units by original MiniLM cosine and `unit_id`. No Gold label or answer score
enters this procedure.

**Algorithm 3: protected bounded insertion.** Let
\(K_q=\min(20,|U_q|)\) and protect the first \(\min(10,K_q)\) unique Dense
units. Traverse the eligible expansion order, retain units at or above the
frozen score floor, skip protected duplicates, and place at most four units
immediately after the prefix. Append unused Dense units in their original
order, then expansion units only if needed to fill \(K_q\). Deduplicate stably
and truncate to \(K_q\).

| Group | Frozen value | Provenance and sensitivity status |
|---|---|---|
| Ball split | depth < 6; splittable size ≥ 4; radius gate 0.78; minimum child size 2 | Frozen compact implementation; no confirmatory sensitivity sweep |
| Ball seeds and ties | farthest from centroid; then least similar to seed 1; stable candidate order | Deterministic rule, not learned |
| Facet seeds/budget | 2 seed balls; at most 2 expansion balls | Frozen compact implementation; no confirmatory budget sweep |
| Facet gates | new terms ≥ 1; ball size ≤ 8; \(b_B\ge.12\) or \(a_B\ge.05\); units/new term ≤ 6; redundancy ≤ .90; \(h_B\ge.10\) | Frozen compact implementation |
| Facet score weights | .45, .20, .20, .15, −.20, −.05; unit bonus 0 | Frozen implementation weights; no claim of global optimality |
| Insertion | protected prefix 10; budget 4; effective \(K=20\) | Frozen transferred policy |
| Candidate floor | 0.1957079917192459 | Stage2E calibration 25th percentile, transferred exactly; not an independently established optimum |
| Ordering | descending cosine or \(h_B\), then `unit_id` or `edge_id` | Fully deterministic tie-breaking |

## Appendix B. Absolute Strong-Retriever Outcomes

| Evaluation setting | Method | F1 | EM | CR@20 | ER@20 |
|---|---|---:|---:|---:|---:|
| Joint component (Stage4H) | BGE | 0.35801 | 0.30467 | 0.85400 | 0.93902 |
| Joint component (Stage4H) | Original Full | 0.31803 | 0.26400 | 0.72217 | 0.87657 |
| Cross-space sidecar (Stage4I) | BGE | 0.34301 | 0.28000 | 0.84967 | 0.93594 |
| Cross-space sidecar (Stage4I) | Protected | 0.34045 | 0.27767 | 0.84350 | 0.93459 |
| BGE-native confirmation (Stage5A) | BGE | 0.34569 | 0.28500 | 0.86167 | 0.94288 |
| BGE-native confirmation (Stage5A) | Protected | 0.34264 | 0.28133 | 0.86233 | 0.94288 |

Absolute rows are dataset-equal-weighted and comparable only within the same
evaluation setting.

## Artifact pointers

- [Stage5R core tables](STAGE5R_CORE_TABLES.md)
- [Figure contracts and captions](figures_stage5r/FIGURE_CONTRACTS_AND_CAPTIONS.md)
- [Verified literature corpus](references/VERIFIED_LITERATURE_CORPUS.md)
- [Citation–claim map](references/CITATION_CLAIM_MAP.md)
- [Supplementary material](supplementary/SUPPLEMENTARY_MATERIAL_DRAFT.md)
- [Pre-submission audit](STAGE5R_PRE_SUBMISSION_AUDIT.md)
