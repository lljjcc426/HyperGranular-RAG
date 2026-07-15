# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1.3 Package Review 2

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review date: 2026-07-16
- Reviewed corrected package: `b9081b3c28c0c03e8bece797f5e05a74401f397b`
- Actual direct parent: `97a8b169835c06330a6781ab63c59a482889c6bb`
- Hard Failure 16 checkpoint ancestor: `f28fc526faf74f80fdefb96ca189769dbcf1e5e4`
- Reviewed Manifest: 321,442 bytes / `C1A11B789FD18D703AA6831BA5B513FC9ACB9767EC8A75016802030E0A0C1123`
- Decision: `REJECT_CORRECTED_AMENDMENT_5G_B_1_1_1_1_3_PACKAGE_AS_CURRENTLY_WRITTEN`
- Recovery: `RETURN_FOR_SECOND_CORRECTED_AMENDMENT_5G_B_1_1_1_1_3_PACKAGE`
- Execution authorized: No
- Other project conversations, thread tools, and global memory used: No

## Accepted Technical Package

The review accepts Package Review 1, corrected package commit and exact seven-path scope, all nine frozen source designs, all six bounded EncodedCommand envelopes, all three raw-stdin payloads, both pre/post parent-host implementations, the current-transport success-evidence contract, extended final-verifier transport gates, stale long-transport rejection logic and the reported 62/62 fixtures.

Independent canonical stdout recomputation also accepts all four new parent-host variants:

| Parent host variant | Bytes | SHA-256 |
|---|---:|---|
| Pre / `EMPTY` | 208 | `4087DA57DCBA3981FB2218AFE1B4E0B317ED0CEF49AB46F33FB9E0493353AB07` |
| Pre / exact CLIXML | 239 | `A6158C08886D53B9DB5D595C4846DED39598E03EC0DB98ACD6CADC2202D559E7` |
| Post / `EMPTY` | 200 | `1468C25C122E627AF6990E5BBD5C79163CCA836E17F301E3C7F71A7B496E69C6` |
| Post / exact CLIXML | 231 | `09CA120A1E73ECE9AF52BE630C3D80DD8E1A7204717075AC09046BE9255968E7` |

No source-design, transport, payload, evidence-schema or final-verifier defect was found.

## Only Blocking Finding: Direct-Parent Passport Contradiction

The reviewed Approval Request correctly identified `97a8b169...` as a superseded package, but labeled Hard Failure 16 checkpoint `f28fc526...` as the corrected package's direct parent. The actual lineage is:

    f28fc526...  Hard Failure 16 checkpoint
        -> 97a8b169...  original rejected bounded-stdin package
        -> b9081b3c...  rejected corrected package

Therefore `b9081b3c...` has direct parent `97a8b169...`; `f28fc526...` is a two-level ancestor. Package-bound approval and direct-child governance cannot bind a Request that contradicts its own Git lineage.

## Required Second Correction

The next package must be the single direct child of `b9081b3c...` and separately register:

- direct parent / rejected corrected package: `b9081b3c28c0c03e8bece797f5e05a74401f397b`;
- superseded original bounded-stdin package: `97a8b169835c06330a6781ab63c59a482889c6bb`;
- Hard Failure 16 checkpoint ancestor: `f28fc526faf74f80fdefb96ca189769dbcf1e5e4`.

This is a lineage-only correction. The nine sources, six envelopes, three payloads, parent-host logic, narrative schema, final verifier, 62 fixtures, six future paths, counts and one-pass order may remain unchanged.

## Explicit Non-Authorization

This review does not authorize approval governance, either parent host, any loader process, target ScriptBlock, semantics sequence/evidence, post-sync sequence/audit, final host/verifier, synthetic, real validator, formal preflight, official input/token/capture, controller, verifier, Gold, reservation or Stage3B.

## Current State

    HARD_FAILURE_16_AUDIT_ACCEPTED
    HARD_FAILURE_16_CHECKPOINT_FROZEN
    PACKAGE_REVIEW_1_ACCEPTED

    NINE_SOURCE_DESIGNS_STATICALLY_ACCEPTED
    SIX_BOUNDED_ENVELOPES_STATICALLY_ACCEPTED
    THREE_RAW_STDIN_PAYLOADS_STATICALLY_ACCEPTED
    PRE_AND_POST_PARENT_HOSTS_STATICALLY_ACCEPTED
    CURRENT_TRANSPORT_EVIDENCE_CONTRACT_ACCEPTED
    EXTENDED_FINAL_VERIFIER_STATICALLY_ACCEPTED
    62_OF_62_FIXTURE_REPORT_ACCEPTED

    ONLY_BLOCKING_CAUSE
    CURRENT_CORRECTED_REQUEST_MISIDENTIFIED_ITS_DIRECT_PARENT
    NO_SOURCE_DESIGN_DEFECT_FOUND
    NO_TRANSPORT_DEFECT_FOUND
    NO_EVIDENCE_SCHEMA_DEFECT_FOUND
    NO_FINAL_VERIFIER_DEFECT_FOUND

    RETURN_FOR_SECOND_CORRECTED_AMENDMENT_5G_B_1_1_1_1_3_PACKAGE
    CURRENT_PACKAGE_B9081B3C_NOT_APPROVED
    EXECUTION_NOT_AUTHORIZED
