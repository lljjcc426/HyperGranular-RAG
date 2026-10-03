# Evidence delivery repair — fixed exploratory development study

Material Passport: code experiment + descriptive diagnosis; 2026-10-03;
user-specified design; starting HEAD ed7d96a0c1a1aa823c71662bf40260bfb3e5f682.
This authorization supersedes the previous confirmation-only stop for this
historically exposed development study. No independent confirmation is claimed.

## Inputs and fixed comparisons

Only opened Stage4E HotpotQA 1,000 and Stage4F MuSiQue 3,000 blind queries,
MiniLM caches, archived rankings/prompts/predictions, and opened target maps.
Stage4H/I/5A provide background only. No Stage6 confirmation, reservation,
Stage3B, new data, new reader or reranker. Original files remain read-only.
Inputs and exact IDs are recorded in DATA_ROLES.json / manifest.json.
Historical Windows paths are mapped read-only from E:/科研 to E:/SCIENCE.

All 4,000 queries: reconstruct H0 and diagnose support losses; support means
annotated Hotpot sentence or MuSiQue paragraph, not exhaustive valid evidence.
Generation: exactly 200 per dataset, smallest SHA256 of UTF-8
`evidence-delivery-repair-v1\0` + dataset + `\0` + query_id.
Rerun: first 10 per dataset under independent hash prefix
`evidence-delivery-repair-rerun-v1\0`, within the 200 selected queries.
No outcome-based sampling or replacement. Main denominators stay 200/200.

Thirteen arms: Dense20, Dense40, H0; R1, R2, Flat-R2, KMeans-R2, Matched-MMR
each at lambda .85 (primary) and .70 (sensitivity), both reported without selection.
MiniLM and Qwen2.5-1.5B-Instruct FP16 snapshots and runtime come from original
bindings. Original prompt, greedy beam=1, max_new_tokens=32, batch=1,
4096 total input-token cap; real rendered input IDs directly reach generate.

## Exact selection contract

Full original query candidate universe, no Top100 cut. Base score uses original
float32 dot product; r(u)=count(s(v)<=s(u))/N. T(u) uses the original tokenizer
on title and sentence, intersected with question terms. K=min(20,N),
p=min(10,K), b=min(4,K-p). Phi=lambda*sum(r)/K+(1-lambda)*coverage/max(1,|Tq|).
Phi is computed in float64, with deterministic sum order. Numeric ties mean
exact computed equality, not a tunable tolerance. Empty Tq has zero coverage.

H0 uses the unchanged original ball split, gates, static edge scores, score/ID
sentence ordering, q25 floor 0.1957079917192459 and protected placement.
R1 keeps its selected balls, filters their sentences by the same floor and removes
P. At each of b steps, maximize actual filled-list Phi difference; tie by base
score descending then unit_id ascending. Continue even for nonpositive gain.
All insertion segments are output in original Dense score/ID order.
R2 keeps corresponding R1 I and P, enumerates removals of a=|I\D| from
D\(P union I), and maximizes Phi((D\R) union I). Prefer R1's eviction set on a
maximum tie, else lexicographically smallest sorted removed-ID tuple. If a=0,
return R1 exactly. At most C(10,4)=210 combinations; this guarantees only proxy
nondecrease. No no-op gate, dynamic ball reselection, bridge term, controller.

Flat-R2 applies R1 then R2 to all floor-eligible nonprefix sentences. Its proposal
count differs from ball-filtered methods and is reported. KMeans-R2 uses actual
H0 group count k, spherical k-means seed1729, max20 iterations, float32 vectors;
initialize k distinct candidate positions with NumPy PCG64 choice, no seed search.
Assignment ties choose lowest cluster index. Empty clusters are repaired in index
order by moving the least-similar-to-own-center unit from a cluster of size>1,
ties by unit_id. Centers are normalized means; zero center stays zero. Stop on
unchanged assignments. Record k, sizes, iterations and repair count; never silently
reduce k. Apply unchanged original facet gates to these groups, then R1/R2.
Matched-MMR greedily maximizes lambda*r(u)-(1-lambda)*max cosine(u,v), v in P+I;
empty max=0, same score/ID tie rule; original placement/fill, no eviction optimizer.
Dense40 uses min(40,N); it is a different entry budget, not a pure matched ablation.

## Design check and interpretation

Mentor perspective: isolate ball-to-sentence delivery, then fixed-insertion eviction;
the two repairs cannot recover balls excluded upstream. Reviewer perspective:
Gold is evaluation-only; actual sentences, complete filled lists, prefix and
budget must be tested; ordinary grouping/Flat/MMR can explain any benefit.
These are two perspectives of this assistant, not external independent approval.
Observed legacy code supports the stated static scoring and zero sentence bonus.
Radius cannot independently trigger splitting at min_size2/max_size3; unchanged.

## Execution, resource and stopping contract

Compile/test and commit implementation before new generation/scoring.
Maximum 5200 main logical predictions +260 real uncached reruns +4 synthetic calls.
No historical prediction reuse: regenerate Dense20/H0 in this namespace. Identical
input IDs within this run may reuse a completion only after two identical synthetic
calls establish determinism; report logical/actual calls separately. Reruns always
bypass this cache and compare per-method inputs, output token IDs and text.
Process remains foreground; no arbitrary timeout. Safe-call-boundary stop on
remaining budget, actual resource exhaustion or integrity failure. Preserve partial
outputs. No outcome-based changes, extra samples or second tuning round.

Inherited cumulative ceilings: GPU process-wall12h, CPU process-time24h, disk10GB,
paid0. Previous bounded-upgrade manifest records experiment GPU0/calls0;
prior document CPU time is unknown, not zero. Begin process CPU accounting now,
record this gap, and charge all current processes. Historical Stage6 generation
predates this budget and is cost reference only, not newly charged twice.
Historical Stage4F main: 6000 calls/1947.37s recorded, not a runtime guarantee.
Use at most4 synthetic calls for present resource calibration before real answers.
Store full prompts/targets-derived per-query diagnostics locally under ignored local/;
publish no raw Gold, corpus, embedding or weight. Publish derived counts/ID recipe.

## Analysis fixed before new outcomes

Use revision2 pinned official Hotpot and MuSiQue answer functions, dataset-specific
aliases/categorical/empty rules. Report each dataset and equal-weight means,
paired EM/F1 differences, gain/same/harm, changes, coverage, additions/promotions/
evictions, visible evidence, tokens and timings. Bootstrap:10000 paired query draws
within each dataset, PCG64 seed20261003, shared indices across all arms; descriptive
percentile95% intervals. No p-values, significance PASS, equivalence or confirmation.
Titles' shared-document components are described, not claimed statistically solved.
Cases: smallest sampling hash among improved, harmed and unchanged R2(.85)-H0;
if a class is absent report absent. No selected-subgroup replacement of main table.

Decision A/B/C/D exactly as user attachment: repair signal worth confirming;
simple selectors explain signal; current local repair unsupported; or blocked/too
imprecise. +.005 F1 is magnitude reference only. Do not edit manuscripts/PDFs/figures.
