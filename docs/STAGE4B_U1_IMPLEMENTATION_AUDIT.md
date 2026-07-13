# Stage4B-U1 Gold-free Implementation Audit

> Historical v2 checkpoint. The execution package was subsequently returned for hardening. The current audit is `docs/STAGE4B_U1_IMPLEMENTATION_AUDIT_V2_1.md`; this file is retained without rewriting its original evidence.

## Status

- Audit date: 2026-07-12
- Protocol: `docs/STAGE4B_U1_PROTOCOL_REVISION_2_DRAFT.md`
- Implementation status: `SYNTHETIC_IMPLEMENTATION_VERIFIED`
- U1-D execution approval: `NOT_APPROVED`
- Official development data accessed: No
- Reservation accessed: No
- Stage3B accessed: No
- Origin Skill: `academic-research-suite / experiment-agent`

## Implemented Boundaries

1. `stage4b_u1_prepare_channels.py` is the only component that accepts labeled units and queries.
2. It writes separate controller and evaluator channels plus separate audit manifests. The controller audit contains no Gold-map hash or labeled-source hash.
3. `stage4b_u1_goldfree_controller.py` has no Gold-map argument and does not import the channel preparer or evaluator.
4. `stage4b_u1_goldfree_retrieval.py` implements new unit, ball, edge, candidate, dense, q25, ECDF, and budget paths without `is_gold` or Gold counts.
5. `stage4b_u1_evaluate.py` refuses a synthetic policy unless `--synthetic-test-mode` is explicit and joins labels only after validating the frozen ranking digest.
6. `stage4b_u1_verify.py` independently recomputes the ordered-prefix budget, dense/q25 selector relation, event subset relation, and evaluation summaries.

## Synthetic Verification

Command:

```powershell
& "D:\Users\cc\AppData\Local\Programs\Python\Python312\python.exe" `
  scripts\stage4b_u1_run_synthetic_verification.py
```

Tracked evidence: `results/stage4b_u1_synthetic_verification.json`

- Tests: 7 run, 0 failures, 0 errors, 0 skipped.
- Deterministic rerun: byte-identical.
- Evidence SHA-256: `ECA7C539D5C93D6CC8DB04309474A0A7E83C23C10E705DA8BDCE0956652B53A1`.
- All temporary channel, embedding, ranking, policy, Gold-map, and evaluation fixtures were written only under an OS temporary directory and removed by the test harness.

Verified properties:

1. Labeled inputs split into process-separated controller/evaluator files.
2. Controller channel and its audit contain neither evaluation-label fields nor Gold-map metadata.
3. Reintroduced `is_gold` is rejected before retrieval.
4. Empty-ball, single-ball, zero-radius, NaN/Inf, and ECDF boundary rules are deterministic.
5. The allocator selects the largest score/hash prefix whose cumulative planned inserts do not exceed 60% of all-query planned inserts; it does not skip an over-budget high-ranked query.
6. Final Top-20 is byte-for-byte dense when not triggered and frozen q25 when triggered.
7. Reservation-mode synthetic execution reuses development ECDF references and records the parent-policy hash.
8. A corrupted final ranking is rejected by the independent verifier.
9. Two complete controller subprocess runs are byte-identical.
10. On the same synthetic input, the Gold-free rewrite matches the legacy frozen algorithm's dense order, hyperedge candidate order, selected edge IDs, and q25 Top-20 order.

## Remaining Evidence Boundary

- Synthetic equivalence does not establish official-corpus equivalence or scientific validity.
- No official Stage4B feature distribution, score, cutoff, trigger, ranking, gain/harm, CR/ER, or false-insert metric exists.
- U1 remains a batch heuristic, not a validated online controller.
- Before U1-D runs, the revised protocol must receive explicit user approval, be marked frozen, and be committed with the updated project `AGENTS.md`.
