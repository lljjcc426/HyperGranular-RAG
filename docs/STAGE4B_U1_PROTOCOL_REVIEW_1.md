# Stage4B-U1 Protocol Review 1

## Review Decision

- Review date: 2026-07-12
- Reviewed artifact: `docs/STAGE4B_U1_PROTOCOL_DRAFT.md`
- Decision: `RETURN_FOR_PROTOCOL_REVISION`
- U1 direction: retained
- U1-D execution: not approved
- Reservation and Stage3B: locked
- Feature extraction, policy freezing, and Gold evaluation: prohibited pending revision and approval

## Strengths Retained

1. Stage4A-R2 gain/harm outcomes are restricted to power planning and frozen-policy evaluation.
2. The 4,500-query development set is retrospective; `[5300:9800)` remains a one-shot reservation.
3. Policy decisions and ranking digests must be frozen before Gold joins.
4. Failed promotion gates stop the branch without same-data tuning.

## Mandatory Findings And Disposition

| ID | Review finding | Revision 2 disposition |
|---|---|---|
| R1 | Existing candidate and ball objects carry `is_gold`/Gold counts before controller decisions | Require separate unlabeled units, unlabeled queries, and evaluator-only Gold map; prohibit the controller process from loading the Gold map or legacy Gold-bearing objects |
| R2 | Median threshold and tie handling do not define a unique trigger set | Replace the median with a deterministic ordered-prefix allocator using `(-score, SHA256(salt::query_id))` |
| R3 | A 50% query budget cannot guarantee a 40% insertion-unit reduction | Replace it with a 60% cumulative planned-insert-unit budget, which mechanically guarantees at least 40% reduction |
| R4 | Boundary, ECDF, floating-point, and exceptional cases are underspecified | Freeze no-ball, one-ball, zero-radius, NaN/Inf, float precision, exact equality, and ECDF extrapolation behavior |
| R5 | Selective ranking behavior is incomplete | Freeze U1 as an on/off selector: triggered queries use the unchanged all-query q25 ranking; others use the unchanged dense ranking |
| R6 | Statistical tests against zero were described as if they tested practical margins | Use correct zero-null language plus separate observed practical-effect gates; define a single joint IUT claim with each component at alpha 0.05 |

## Additional Findings And Disposition

1. U1 is explicitly described as a mechanism-driven, Gold-free heuristic resource allocator with weak prior predictive evidence.
2. Question-type results are mandatory descriptive risk audits and cannot support type-specific efficacy claims.
3. `AGENTS.md` will be updated only after U1-D receives execution approval; until then there is no active Stage4B execution protocol.

## Required Approval Sequence

1. Record and commit the revised design.
2. Implement the Gold-free channel, controller, evaluator, and independent verifier without running U1-D.
3. Verify the implementation on synthetic fixtures and commit it.
4. Submit the protocol plus implementation evidence for explicit U1-D execution approval.

This review does not authorize reservation access, Stage3B access, feature extraction from the official development corpus, policy calibration, or Gold evaluation.
