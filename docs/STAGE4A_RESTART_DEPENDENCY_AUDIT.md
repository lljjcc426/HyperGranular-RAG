# Restarted Stage4A Dependency and Conclusion Audit

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Mode: validate + plan
- Date: 2026-07-11
- Verification Status: ANALYZED
- Evidence boundary: current conversation, current repository artifacts, and the official 2Wiki archive supplied by the user
- Other conversations, thread tools, and memory files used: No

## Purpose

This audit identifies which earlier conclusions remain supported, which require narrower wording, and which must be superseded before a new 2Wiki experiment begins. It does not recompute retrieval metrics.

## Dependency Matrix

| Prior result | Audited evidence | Status | Permitted conclusion |
|---|---|---|---|
| Stage2E q25 floor selection | The q25 floor was selected and evaluated on the same 400 queries. | RETAIN_AS_EXPLORATORY_ONLY | The value `0.1957079917192459` is a candidate transfer threshold, not an independently established optimum. |
| Stage2F q25 p10/i4 validation | Disjoint 400-query HotpotQA+MuSiQue test; q25 p10/i4 versus dense CR@20 delta `+0.0175`, paired-bootstrap interval `[0.0025, 0.0350]`, 9 gains and 2 regressions. | RETAIN_WITH_DOMAIN_SCOPE | The frozen q25 policy has independent support on the original two-domain test, but not as an optimal 2Wiki threshold. |
| Stage2G all-query p10/i4 mechanism | Disjoint 400-query test; all-query p10/i4 versus dense CR@20 delta `+0.0225`, interval `[0.0025, 0.0425]`; boundary suppression did not improve the policy. | RETAIN_WITH_DOMAIN_SCOPE | All-query protected insertion remains the supported transferred mechanism; the old boundary-only rule remains unsupported. |
| Stage3A utility controller | Sparse targets forced a harm-head fallback and the promotion gate failed. | RETAIN | The controller is not validated; Stage3B remains locked. |
| Stage3C target-feasibility audit | 2,000 observed development queries produced 69 gains and 8 harms; 69 gains were concentrated in HotpotQA. | RETAIN_AS_DESCRIPTIVE | Budget-aware gain selection is an event-rich development scope in HotpotQA. It is not cross-dataset validation and does not establish a 2Wiki event rate. |
| Stage4A mirror mapping | 982/982 mirror supporting facts mapped with zero missing gold. | RETAIN_FOR_MIRROR_ONLY | The conversion code maps the pinned mirror without internal evidence loss. |
| Stage4A official mapping equivalence | Official reconciliation found 7 context-content and 5 gold-text mismatches in 400 queries. | SUPERSEDE | The mirror is not content-equivalent to the April 7 official archive. |
| Stage4A dense non-saturation | Mirror dense CR@20 was 0.7450. | INCONCLUSIVE_FOR_OFFICIAL_DATA | The mirror pilot is non-saturated; official-archive saturation has not been measured. |
| Stage4A q25 gain prevalence | Mirror observed 8/400 gains. The 400-query size had no event-count operating-characteristic justification. | PLANNING_SIGNAL_ONLY | The 0.0200 point estimate and 0.0102 Wilson lower bound may inform a fresh sample-size plan but cannot validate feasibility. |
| Stage4A `STOP` | The mirror pilot missed the 10-gain gate by two events; official content differs and the gate was under-designed. | SCIENTIFICALLY_INCONCLUSIVE | Preserve `STOP` only as the procedural output of the old frozen protocol. It cannot stop the research direction. |

## Resolved Dependency Rules

1. The restarted Stage4A may transfer q25 p10/i4 as a fixed policy because Stage2F independently tested it; the restarted Stage4A must not claim the threshold is 2Wiki-optimal.
2. The restarted Stage4A uses all-query expansion because Stage2G did not validate boundary suppression.
3. The restarted Stage4A adopts the Stage3C threshold of at least 20 gain events for selector-development feasibility; the invalidated Stage4A threshold of 10 is superseded for scientific planning.
4. The restarted Stage4A uses the official April 7 archive only.
5. Invalidated Stage4A rows `[0:400)` and its old reservation `[400:800)` are excluded from restarted Stage4A development and reservation data.
6. Stage3B remains locked and is not affected by the restarted Stage4A.

## Current Scientific State

- HyperGranular RAG direction: OPEN.
- Official 2Wiki dense saturation: UNRESOLVED.
- Official 2Wiki q25 gain-event feasibility: UNRESOLVED.
- Existing mirror metrics: REPRODUCIBLE_BUT_SOURCE_SCOPED.
- New controller fitting: NOT AUTHORIZED.

The project stage is rolled back to Stage3C completed. The next valid action is approval and freezing of `docs/STAGE4A_RESTART_PROTOCOL_DRAFT.md`, followed by source-only extraction from the official archive. No retrieval metric should be computed before that approval.
