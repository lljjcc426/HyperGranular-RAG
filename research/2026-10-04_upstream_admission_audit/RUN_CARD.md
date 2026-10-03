# Upstream admission audit v1

Material Passport: retrospective CPU diagnosis; HISTORICALLY_EXPOSED_EXPLORATORY;
2026-10-04; reference aa4edbfc1ae3a3a6e0d7c77da7ac4e814d85519d.
The user's named attachment defines this task. Prior answers/results informed its
design; the implementation commit is not prospective independent confirmation.

## Fixed computation

Full history: HotpotQA 1,000 / MuSiQue 3,000 original granular-ball groups, all six
gate truth values, first-failure reconciliation and lexical saturation. Pilot:
reuse exactly the previous 200+200 sample IDs; GB and previous spherical KMeans
(actual k, seed1729, max20 iterations, unchanged empty-cluster repair).
G0 disables nothing; G1 new-term; G2 redundancy; G3 both; G4 additionally ratio;
G5 additionally score threshold. Seed exclusion, size, anchor, original h_B order,
two groups, q25, prefix10, insertion4, effective K20 remain fixed. All diagnostic
lists use original H0 placement; no R1/R2 search. 4,800 lists, no answers.
COUNT_MATCHED_DENSE matches each proposal pool's inside/outside Dense20 counts
using highest original-score candidates in the same floor-eligible nonprefix pool.
It does not match group meaning, identities or token length. F and Dense20/40
are coverage references, not answer oracles. All rows report NOT_GENERATED.

Targets come from prior local loss diagnostics: sentence IDs for Hotpot; paragraph
IDs for MuSiQue, reconstructed to their candidate member IDs. No original answers
are rescored. A paragraph passes a layer only if at least one same member sentence
reaches that layer; no cross-sentence splicing of favorable gate conditions.
Gold-derived labels never enter core gate/selector functions. Original archived
H0 ranks/insertion sequence must match. Prior KMeans sizes, iterations, repair
counts and proposal counts are checked; old member hashes were not saved and
will not be claimed verified.

For all gates, record independent truth plus original short-circuit reason.
Group budget is recomputed per mask, not an intrinsic gate. Record four layers:
all eligible members, selected-two members, floor/nonprefix proposals, final list.
At each layer report target additions/losses relative to same-group G0; final
also relative to Dense20. Report query mean ER/CR separately from total hits/targets.
Joint-failure denominators distinguish all groups, nonseed groups, and nonseed
groups containing Dense-missing targets; overlapping counts are not summed.

## Cases and proof

Within each dataset, A then B then C, up to3 unseen queries/class ordered by
SHA256('upstream-admission-audit-v1\0'+dataset+'\0'+query_id). A: nonseed, nonempty
facets, new0, floor-passing member from a Dense-missing annotated target. B: GB
G5-new proposals with some unannotated-support members. C: GB/KMeans G0 final
member difference. Present up to2 eligible candidates in original Dense/ID order.
B uses the new unannotated-support members; C uses the symmetric final difference.
Read the question, all Dense20 texts, and chosen candidates. This assistant's
review is nonblind, not human double annotation or a population prevalence estimate.
Keep source text/IDs local; publish short paraphrases and explicit unknowns.

Prove Dense optimality for the specified Phi only when it covers every observable
query facet. Test tolerance 1e-12 for numeric checks; no tolerance changes ranking
ties. Check both previous fixed lambdas and existing fixed pilot rankings only;
do not rerun their generation, scoring, bootstrap or optimizer.

## Resource, implementation and stop

Use existing Python3.12 / NumPy2.5.1 CPU runtime, numerical threads1. CUDA devices
disabled; no model imports/weight loads or network in the analysis process.
New calls0/GPU0/paid0. CPU limit7200 seconds and disk1GB, within original cumulative
24CPUh/10GB limits; previous measured CPU633.96875 seconds, past document CPU
unknown. Track actual current process CPU/wall. Check budgets at query boundaries,
retain partial outputs if exhausted; no deleting queries or silently restarting.
Stream full group records compressed under ignored local/, reuse each grouping
across all six masks. Old inputs remain read-only; no monkey-patched output roots.

Inline design check: the mentor view isolates jointly binding lexical gates;
the reviewer view requires competition losses, count matching, paragraph path
integrity and no answer claims. Both are this assistant's views, not external review.
Use focused synthetic tests and real G0 reconciliation, not old experiment suites.
Publish code/card before new counts, then derived summaries and verified reports.
Decision A/B/C follows the attachment; no count threshold automatically authorizes
new mechanism, model, generation, confirmation, paper edit or direction change.
Existing unrelated dirty changes remain outside this round's commits.
