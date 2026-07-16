# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1.4 Package Review 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review received: 2026-07-16
- Reviewed package: `7d2dcd5fe525c86ab2b91e7ed2dfb17b1e6228ac`
- Direct parent / Hard Failure 17 checkpoint: `6c741c251dce55236b06dc5c06fd834b7649f8b2`
- Reviewed Manifest: 24,293 bytes / SHA-256 `921B7BB63B0CF8E7B51CC6ED51A74C98A915E6C8E5FB2211E8235D7A378DE928`
- Decision: `REJECT_AMENDMENT_5G_B_1_1_1_1_4_PACKAGE_AS_CURRENTLY_WRITTEN`
- Recovery: `RETURN_FOR_CORRECTED_AMENDMENT_5G_B_1_1_1_1_4_PACKAGE`
- Approval governance authorized: No
- Execution authorized: No
- Other project conversations, thread tools, and global memory used: No

## Accepted Findings

The independent review accepts:

1. Hard Failure 17 Review 1;
2. the package commit and exact ten-path scope;
3. all three tracked ASCII adapter static designs;
4. schema-descriptor and executable-path binding;
5. the unique quoted-file / single-space / arguments / terminal-null modeled-command formula;
6. all three adapter `-File` invocation envelopes;
7. the reported 30/30 schema-semantics fixtures; and
8. the zero-execution package-assembly boundary.

The review independently confirmed that package `7d2dcd5f...` was the single direct child of the Hard Failure 17 checkpoint, changed exactly ten paths, deleted no file, matched GitHub `main`, and did not create any future semantics or post-sync evidence path.

## Blocking Causes

The reviewed package is nevertheless rejected for five blocking causes:

    ADAPTER_TO_PARENT_ACTUAL_STDERR_CLASS_NOT_EXPOSED
    MANDATORY_ADAPTER_EXECUTION_NOT_DURABLY_ATTESTED
    FINAL_VERIFIER_DOES_NOT_BIND_OR_VALIDATE_5G_B_1_1_1_1_4_ADAPTERS
    UNCHANGED_EVIDENCE_SCHEMA_CANNOT_PROVE_ADAPTER_MEDIATED_EXECUTION
    FINAL_ADAPTER_ATTESTATION_ORDER_NOT_CLOSED

### Actual parent stderr class was collapsed

Each adapter distinguished `EMPTY` from `EXACT_FROZEN_382_BYTE_STARTUP_CLIXML` internally, but emitted only `parent_stderr_registered=true`. The actual adapter-to-parent class therefore could not be recovered from the registered success stdout.

### Adapter execution was not durable evidence

The package preserved the old evidence schema and persisted none of the following actual runtime facts:

- adapter tracked-file bytes and SHA-256;
- adapter `-File` arguments SHA-256;
- adapter modeled command-line SHA-256;
- observed adapter stdout bytes and SHA-256;
- observed adapter stderr class; and
- observed adapter-to-parent stderr class.

### The old final verifier did not know the adapters

The inherited 1.1.3 final verifier validated the original six bounded envelopes, three payloads, semantics/post evidence, Git chain, path sets, artifact stability, and clean/synchronized repository state. It did not bind or validate the three 1.1.4 adapters, their three invocation envelopes, their actual outputs, or their six adapter-level stderr classes. Directly starting an original parent could therefore evade the declared mandatory adapter trust root while still satisfying the old terminal state.

### FINAL ordering could not persist its class

The old order required immediate stop after FINAL parent/verifier success. The FINAL adapter class only exists after that return, so the order left no permitted file/commit/verifier step in which to persist and independently validate the FINAL adapter observation.

## Minimum Corrected-package Requirements

The corrected package must:

1. freeze two exact class-bearing stdout variants for each PRE/POST/FINAL adapter, six total;
2. durably attest actual adapter source identity, invocation identity, observed stdout, adapter stderr class, and adapter-to-parent stderr class;
3. add a package-bound terminal verifier for the three adapters, three invocation envelopes, three execution attestations, six actual classes, mandatory mediation, Git chain, and path sets; and
4. create and push a versioned final-adapter attestation commit after the FINAL adapter returns, then run a read-only terminal commit verifier.

The original nine sources, six bounded envelopes, three raw-stdin payloads, parent/loader/target chain, 30/30 schema fixtures, 62/62 inherited fixtures, and strict pre-approval sequencing may remain unchanged.

## Current State

    HARD_FAILURE_17_AUDIT_ACCEPTED
    HARD_FAILURE_17_CHECKPOINT_FROZEN

    THREE_TRACKED_ADAPTER_STATIC_DESIGNS_ACCEPTED
    SCHEMA_SEMANTICS_BINDING_ACCEPTED
    ADAPTER_INVOCATION_ENVELOPES_ACCEPTED
    SCHEMA_FIXTURES_30_OF_30_ACCEPTED
    PACKAGE_ASSEMBLY_ZERO_EXECUTION_ACCEPTED

    ADAPTER_ACTUAL_STDERR_CLASSES_UNOBSERVABLE_IN_REJECTED_PACKAGE
    ADAPTER_EXECUTION_NOT_DURABLY_ATTESTED_IN_REJECTED_PACKAGE
    FINAL_VERIFIER_UNAWARE_OF_1_1_4_ADAPTERS_IN_REJECTED_PACKAGE
    FINAL_ADAPTER_ATTESTATION_ORDER_NOT_CLOSED_IN_REJECTED_PACKAGE

    RETURN_FOR_CORRECTED_AMENDMENT_5G_B_1_1_1_1_4_PACKAGE
    CURRENT_PACKAGE_7D2DCD5F_NOT_APPROVED

    APPROVAL_GOVERNANCE_NOT_APPROVED
    PRE_NOT_APPROVED
    POST_NOT_APPROVED
    FINAL_NOT_APPROVED
    SYNTHETIC_REBINDING_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_EXECUTION_NOT_APPROVED
    GOLD_NOT_APPROVED
    RESERVATION_NOT_APPROVED
    STAGE3B_NOT_APPROVED
