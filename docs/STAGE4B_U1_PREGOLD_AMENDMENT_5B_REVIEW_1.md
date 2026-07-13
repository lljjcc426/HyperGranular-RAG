# Stage4B-U1-D Pre-Gold Amendment 5B Review 1

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Review date: 2026-07-14
- Reviewed package commit: `ceb755252540cf223aa18ac721443154c29cd07a`
- Review source: current HyperGranular-RAG project conversation
- Other project conversations, thread tools, and global memory used: No

## Decision

```text
RETURN_AMENDMENT_5B_FOR_CHANNEL_INPUT_HASH_BINDING
OFFICIAL_DIAGNOSIS_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

The 5A implementation remains accepted at its existing evidence boundary: the controller was not modified, 98 tests passed in both complete runs, the evidence bytes were identical, and the recorded official-path access-attempt count was zero. This review does not reinterpret or extend that evidence.

## Sole Blocking Issue

The rejected 5B Manifest froze the embedding cache SHA, reference-decisions SHA, ID digests, and registered source-audit digest. It registered the following three files only by absolute path:

1. v2.3.1 unlabeled units;
2. v2.3.1 unlabeled queries;
3. v2.3.1 controller channel audit.

The capture checked units/queries against hashes stored inside the controller channel audit. That proves internal consistency but not an independent package binding: coordinated changes to all three files could remain internally consistent while preserving counts, ID digests, and registered source-audit fields.

## Frozen Channel Input Hashes

```text
unlabeled units SHA-256
114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA

unlabeled queries SHA-256
6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B

controller channel audit SHA-256
D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA
```

These values come from the single audited v2.3.1 channel preparation and are the only values a revised package may accept.

## Required Amendment 5A.1

A package-bound Amendment 5A.1 must request implementation and synthetic-verification authority only for:

1. registering the three expected SHA-256 values in a machine-readable Manifest and the diagnostic interface;
2. hashing and matching all three files before semantic parsing or diagnostic computation;
3. hashing and matching all three files again after diagnostic computation and immediately before machine-audit exclusive-create;
4. failing closed with no machine audit and complete temporary-decisions cleanup on any mismatch;
5. retaining the existing 98 tests and adding coverage for each pre-check drift, computation-time drift, the valid three-hash path, and cleanup on failure;
6. running the complete suite twice with zero failures/errors/skips and byte-identical evidence;
7. producing implementation audit/evidence and a revised implementation-bound 5B package, then stopping.

The only preliminary access permitted by a future approved implementation before the three gates pass is reading bytes needed to compute each SHA-256. Semantic JSON/JSONL parsing and diagnostic computation must not begin until all three expected hashes match.

## Retained 5B Boundaries

The following parts of the rejected 5B design may be retained in a revised package:

- one decisions-only capture;
- frozen reference-decisions and require-existing cache hashes;
- source-audit file remains unopened;
- aggregate-only machine audit with salted query-ID hashes;
- no official rankings, policy, Gold, reservation, or Stage3B access;
- no formal decisions, rankings, policy, or `VERIFIED_PRE_GOLD` output;
- no equivalence relaxation, automatic retry, or automatic official resumption.

## Current Stop State

The rejected 5B authorization token must not be used. No 5B preflight or capture has been authorized. The only current action is preparation and push of the 5A.1 approval request and Manifest. Implementation and synthetic verification require a new approval that explicitly binds the commit containing that package.
