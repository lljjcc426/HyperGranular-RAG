# Stage4A Design and Provenance Audit

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Mode: validate
- Date: 2026-07-11
- Verification Status: VERIFIED_DESIGN_DEFECT_AND_SOURCE_MISMATCH
- Evidence boundary: current conversation, current repository Git history, and the user-supplied official archive only
- Other conversations, thread tools, and memory files used: No

## Why 400 Queries Were Used

The user did not specify 400 queries. Before commit `999de87`, the roadmap required only a small development sample and a separate reservation; it did not specify a sample size. Commit `999de87` first introduced pilot rows `[0:400)` and reservation rows `[400:800)`.

No power analysis, precision target, minimum detectable event prevalence, or literature-derived sample-size justification was recorded. Earlier repository stages also used 400-query slices, but that is precedent rather than scientific justification. The Stage4A sample size is therefore classified as:

`LEGACY_UNJUSTIFIED_CONVENIENCE_SIZE`

## Post-hoc Event-Count Diagnosis

The mirror pilot observed 8 q25 gain events among 400 queries, a point prevalence of 0.0200 with a 95% Wilson interval of `[0.0102, 0.0390]`.

The preregistered promotion gate required at least 10 gains. Under a binomial model:

- At event prevalence 0.0200, 400 queries have probability 0.2821 of producing at least 10 gains.
- At event prevalence 0.0200, the minimum sample sizes for 80%, 90%, and 95% probability of at least 10 gains are 625, 708, and 782.
- At the conservative Wilson lower bound 0.0102, the corresponding minimum sample sizes are 1,226, 1,391, and 1,537.

These calculations are post-hoc planning diagnostics, not a retrospective alteration of the Stage4A gate and not confirmatory evidence. They show that the 400-query gate had no documented operating-characteristic justification and could prematurely stop a viable low-prevalence branch.

## Official Archive Reconciliation

The user supplied the official `data_ids_april7.zip` archive from the dataset authors' Dropbox link.

- Archive SHA-256: `95DF2BF56FDABE034E27AEBC580E02264232203CF52552F9EFE8A919E5529EEF`
- ZIP CRC: all four entries passed
- Official `dev.json`: 12,576 rows and 12,576 unique IDs
- Official `dev.json` SHA-256: `79F77AE104088EA8E25B1A65DBECE768D45771194663BC5660EC9A98070DADF5`
- Pilot ID, question, answer, type, evidences, and supporting-fact mismatches: 0/400
- Context order-only changes: 393/400
- Context content mismatches after order normalization: 7/400
- Gold-evidence text mismatches: 5/400
- Candidate units: 12,718 official versus 12,721 mirror
- Reservation IDs `[400:800)`: exact ordered match
- Official-only fields omitted by the mirror: `answer_id`, `entity_ids`, and `evidences_id`

The seven content differences are consistent with the April 7 sentence-segmentation and punctuation-spacing corrections. Full machine-readable evidence is recorded in `docs/STAGE4A_OFFICIAL_RECONCILIATION.json`.

## Corrected Interpretation

1. The existing Stage4A CSVs remain deterministic results for the pinned Hugging Face mirror.
2. They are not retrieval results on the official April 7 archive.
3. The mirror-specific `STOP` decision remains the procedural output of the frozen protocol, but it is not evidence that HyperGranular RAG or 2Wiki is infeasible.
4. The result cannot be used as paper-grade external evidence and cannot justify abandoning the research direction.
5. The old 400-query pilot must not be rerun after threshold tuning.

## Required Guardrails for a Repair Study

1. Use the official archive as the source of truth and pin its archive and split hashes before sampling.
2. Exclude the old pilot `[0:400)` and reservation `[400:800)` from a new development sample.
3. State the event-prevalence assumption, target event count, and target probability before fixing the sample size.
4. Select a fresh range or deterministic sample only after the design protocol is committed.
5. Keep the q25 threshold and retrieval configuration frozen if the study is intended to isolate source and sample-size effects.
6. Name the repair study separately; do not relabel it as the stopped Stage4B branch.
7. Do not interpret an event-count gate without reporting its operating characteristics.

No retrieval metrics were recomputed during this audit.

## Resolution Path

The original Stage4A scientific feasibility conclusion is now `INVALIDATED_NO_OFFICIAL_FEASIBILITY_DECISION`. The project stage has rolled back to Stage3C completed, and the proposed restarted Stage4A is documented in:

- `docs/STAGE4A_RESTART_DEPENDENCY_AUDIT.md`
- `docs/STAGE4A_RESTART_SAMPLE_SIZE_PLAN.json`
- `docs/STAGE4A_RESTART_PROTOCOL_DRAFT.md`

No fresh official rows may be extracted until the restarted Stage4A sample size and data boundary receive explicit user approval.
