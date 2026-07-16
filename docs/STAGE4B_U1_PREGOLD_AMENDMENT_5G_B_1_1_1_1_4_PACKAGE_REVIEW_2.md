# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1.4 Package Review 2

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review received: 2026-07-16
- Reviewed corrected package: `61cfce1d3c11891ad0d8c2953fd855c2c3d0f9a8`
- Direct parent / rejected package: `7d2dcd5fe525c86ab2b91e7ed2dfb17b1e6228ac`
- Reviewed Manifest: 41,597 bytes / SHA-256 `E0C0E8B329720C8B99130598E820E244E80707BAA628C1063688E209D067121A`
- Decision: `REJECT_CORRECTED_AMENDMENT_5G_B_1_1_1_1_4_PACKAGE_AS_CURRENTLY_WRITTEN`
- Recovery: `RETURN_FOR_SECOND_CORRECTED_AMENDMENT_5G_B_1_1_1_1_4_PACKAGE`
- Selected recovery design: `SCHEME_A_STAGE_ATTESTATION_IMMEDIATELY_INCLUDED_IN_CORRESPONDING_COMMIT`
- Approval governance authorized: No
- Capture, adapter, PRE, POST, FINAL, evidence, or terminal execution authorized: No
- Other project conversations, thread tools, and global memory used: No

## Accepted Findings

The independent review accepts:

1. Package Review 1;
2. corrected package commit `61cfce1d...` and its exact twelve-path scope;
3. all six class-bearing adapter stdout variants;
4. the adapter capture-attestation host static design;
5. the dual-mode PRE_ATTESTATION and TERMINAL verifier static design;
6. the corrected 1.1.4 Approval Decision path compatibility fix;
7. the four-layer and five-layer Git chain designs;
8. the 30/30 inherited schema fixtures;
9. the reported 32/32 corrected static fixtures; and
10. the zero-execution package-assembly boundary.

The review confirms that these changes closed the five blockers from Package Review 1. These accepted components are retained in the second correction.

## Blocking Causes

Corrected package `61cfce1d...` is nevertheless rejected for six blocking causes:

    PRE_AND_POST_RUNTIME_ATTESTATIONS_REMAIN_UNANCHORED_UNTIL_FINAL
    PENDING_TEMP_ATTESTATIONS_ARE_MUTABLE_AND_NOT_STAGE_COMMIT_BOUND
    ATTESTATION_JSON_CANONICAL_BYTES_NOT_ENFORCED
    SEMANTICALLY_EQUIVALENT_OR_EXTENDED_JSON_CAN_PASS_TERMINAL_VERIFIER
    CAPTURE_HOST_STAGE_INVOCATION_IDENTITY_NOT_PERSISTED
    CAPTURE_HOST_INVOCATION_VARIANTS_NOT_TERMINALLY_VALIDATED

### PRE and POST observations lacked immediate Git anchors

The rejected corrected package wrote PRE and POST attestations to mutable OS-temp pending files. Neither observation entered its corresponding semantics or post-sync commit. `CreateNew` prevented only an initial collision; it did not make a closed pending file immutable.

### Promotion validated semantics rather than original bytes

FINAL promoted the then-current pending bytes after partial field checks. It did not prove that the repository file was the exact byte string emitted at the original capture time.

### Terminal verification accepted noncanonical JSON

The verifier decoded JSON and compared selected fields. It did not rebuild the one frozen serialization and byte-compare it with the raw file. Extra fields, reordered keys, whitespace, alternate escaping, duplicate keys, a trailing newline, or other semantic-equivalent encodings could therefore pass field-level checks.

### Capture-host invocation identity was incomplete

Attestations included the capture-host source identity but omitted the stage-specific `-File ... -Stage PRE|POST|FINAL` arguments and modeled-command identity. The terminal verifier likewise did not validate all three capture-host invocation variants.

## Required Second Correction

The independent review recommends Scheme A:

1. PRE capture directly creates the PRE repository attestation; the exact semantics commit contains semantics machine, semantics narrative, and PRE attestation.
2. POST capture directly creates the POST repository attestation; the exact post-sync commit contains post machine, post narrative, and POST attestation.
3. PRE_ATTESTATION validates the already committed PRE and POST attestations and requires FINAL absence.
4. FINAL capture directly creates only the FINAL repository attestation; the final-attestation commit contains only that path.
5. TERMINAL validates all three attestations and the five-layer Git chain.
6. No pending or promotion path remains.

Capture host and terminal verifier must share one frozen canonical byte builder. The verifier must reconstruct the full stage-specific canonical record and compare raw bytes byte-for-byte. It must reject extra or missing fields, field reorder, whitespace changes, alternate escapes, duplicate keys, trailing newline, semantic-equivalent encodings, and same-length mutations.

Each attestation must also persist, and the terminal verifier must stage-select and validate:

- `capture_host_invocation_variant`;
- `capture_host_arguments_characters`;
- `capture_host_arguments_sha256`;
- `capture_host_modeled_characters_including_terminal_null`; and
- `capture_host_modeled_sha256_including_terminal_null`.

## Non-authorization

This review does not approve approval governance, capture-host execution, adapter execution, PRE/POST/FINAL execution, attestation creation, evidence commits, terminal verifier execution, synthetic rebinding, formal preflight, official execution, Gold, reservation, or Stage3B.

## Current State

    HARD_FAILURE_17_AUDIT_ACCEPTED
    HARD_FAILURE_17_CHECKPOINT_FROZEN
    PACKAGE_REVIEW_1_ACCEPTED

    SIX_CLASS_BEARING_ADAPTER_VARIANTS_STATICALLY_ACCEPTED
    CAPTURE_ATTESTATION_HOST_STATICALLY_ACCEPTED
    DUAL_MODE_VERIFIER_STATICALLY_ACCEPTED
    FOUR_AND_FIVE_LAYER_GIT_CHAIN_STATICALLY_ACCEPTED
    APPROVAL_DECISION_PATH_COMPATIBILITY_FIX_ACCEPTED

    PRE_POST_ATTESTATIONS_NOT_STAGE_COMMIT_ANCHORED_IN_61CFCE1D
    PENDING_ATTESTATION_MUTABILITY_NOT_CLOSED_IN_61CFCE1D
    ATTESTATION_CANONICAL_BYTES_NOT_VERIFIED_IN_61CFCE1D
    CAPTURE_HOST_INVOCATION_NOT_DURABLY_ATTESTED_IN_61CFCE1D

    RETURN_FOR_SECOND_CORRECTED_AMENDMENT_5G_B_1_1_1_1_4_PACKAGE
    CURRENT_PACKAGE_61CFCE1D_NOT_APPROVED

    APPROVAL_GOVERNANCE_NOT_APPROVED
    CAPTURE_EXECUTION_NOT_APPROVED
    PRE_NOT_APPROVED
    POST_NOT_APPROVED
    FINAL_NOT_APPROVED
    TERMINAL_VERIFIER_NOT_APPROVED
    SYNTHETIC_REBINDING_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_EXECUTION_NOT_APPROVED
    GOLD_NOT_APPROVED
    RESERVATION_NOT_APPROVED
    STAGE3B_NOT_APPROVED
