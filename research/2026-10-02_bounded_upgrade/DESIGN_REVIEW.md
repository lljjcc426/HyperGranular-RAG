# One design review, two perspectives

Material Passport: prospective internal design review; 2026-10-02; no new outcome inspected. These are two reasoning perspectives of the same assistant, **not two independent human reviewers or external approvals**.

| Perspective | Concern | Disposition and resulting design |
|---|---|---|
| Mentor | More experiments must resolve a claim, not chase a venue | Adopted: compact attribution first, then a single fixed strong backbone; no further model search |
| Mentor | Existing v2 implementation changes the method | Adopted: BU-v2 explicitly distinct from static-q25; old scores stay attached to old code |
| Mentor | Resources and available confirmation are not established by intent | Adopted: one consolidated budget/provenance clarification; synthetic calibration only while pending |
| Mentor | A strong setting without compact benefit wastes compute | Adopted: preregistered compact development gate precedes strong development |
| Reviewer | Generic 12 vs structural 4 optimized slots confounds attribution | Adopted: all selectors get four optimized picks and four new-ID maximum; group count separately recorded |
| Reviewer | Matching leaf target is not matching actual groups | Adopted: per-setting k equals actual target group count; random matches exact group-size multiset |
| Reviewer | Ablations silently change all weights | Adopted: pure zeros without renormalization; same lambda/leaf/budget; separate tuned-pipeline comparison |
| Reviewer | Group-union coverage can be phantom | Adopted: actual selected-sentence facets drive F; group-union/visible facets remain distinct diagnostics. Explicitly acknowledge F=C in this version |
| Reviewer | Top-20 is an artificial bottleneck; 4096 cap alone does not match realized budgets | Adopted: Dense40 and complete-pool ordering under shared 1024-token renderer cap; actual lengths reported, no equality claim |
| Reviewer | Cache hits masquerade as deterministic generation | Adopted: no generation cache; independent subset uses real calls |
| Reviewer | Uncentered bootstrap tails and shared selector bugs invalidate assurance | Adopted: existing centered proposal with stated assumptions; independent semantic reconstruction; mutation tests |
| Reviewer | Confirmation file absence proves neither independence nor non-exposure | Adopted: provenance clarification and actual blind-ID exclusions; labels remain closed |
| Reviewer | Fixed small sample may lack precision | Adopted: effect-independent variance feasibility rule, one fixed maximum confirmation, no sample extension |
| Reviewer | "Same quality cheaper" could be a post-hoc rescue | Rejected as a confirmatory claim this round: no noninferiority design; costs are descriptive supporting evidence |
| Reviewer | Full coefficient F duplicates C when using actual sentence facets | Partially adopted: expose the algebra and pure NoFacet control; do not silently redesign coefficients or call F uniquely high-order |

Initial disposition: a conditional proposal, never an execution-ready lock. Final disposition: **D — confirmation independence unverified**. The user accepted the proposed resource ceilings but could not recall prior exposure. No calibration, development selection or confirmation was started; do not obtain another confirmation set to continue this round.

## Literature-first addition to the same review
These remain two perspectives of one assistant, not independent expert approvals. See the linked `literature_refresh/2026-10-02_bounded/REVIEW.md` for evidence and access limits.

| Perspective | Recommendation | Resolution |
|---|---|---|
| Mentor | Retain the distinction between selecting evidence and arranging identical visible evidence | Adopt: this is supported by actual comparisons, not by naming the structure |
| Mentor | Claim a first combination of granular balls and hypergraphs | Reject: SAGHL, MGHRL and feature-selection work already cover the combination |
| Mentor | Treat different tasks as making all construction prior art irrelevant | Reject: distinguish construction novelty from task-specific value |
| Reviewer | Address Wang et al. AAAI HGRAG before claiming multi-granularity RAG novelty | Adopt: closest task-level neighbor; its entity-passage diffusion and corpus boundary are different |
| Reviewer | Run published 70B/API systems within the present budget | Reject automatic execution: no aligned reader/corpus/budget or approved resource path; conceptual comparison only |
| Reviewer | Add a small adapted diffusion baseline | Partially adopt as a possible later control, not an exact reproduction; no execution while confirmation independence is unresolved |
| Reviewer | Preserve MMR/coverage/ordinary grouping and larger-context controls | Adopt as unanswered questions; literature does not remove them or produce new results |
| Reviewer | Declare v2 novel despite partial access and duplicated coverage terms | Reject: novelty/access C; the current manuscript must stay empirical and bounded |

Novelty disposition **C_NOVELTY_OR_ACCESS_UNRESOLVED** and execution disposition **D** answer different questions. Neither says that the historical method failed. The fallback is actual revision and compilation of both manuscripts, with no new algorithm experiment.

The existing audit's no-hyperedge, radius and path-dependence findings are retained; they are not repaired retroactively. Existing figures and plotting scripts are outside this round's edit scope.
