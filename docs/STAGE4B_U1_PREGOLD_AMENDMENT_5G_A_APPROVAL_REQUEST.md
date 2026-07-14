# Stage4B-U1-D Pre-Gold Amendment 5G-A Approval Request

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-14
- Request ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_A_DERIVED_EXECUTION_HEAD_BINDING_HELPER_IMPLEMENTATION_AND_SYNTHETIC_ONLY`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_MANIFEST.json`
- Current state: `RETURN_FOR_AMENDMENT_5G_A_PACKAGE`
- Requested mode: `IMPLEMENTATION_AND_SYNTHETIC_VERIFICATION_ONLY`
- Package itself authorizes implementation or execution: No
- Formal preflight/helper official calls/official inputs/token/capture: `NOT_APPROVED`
- Other project conversations, thread tools, and global memory used: No

## Binding History

```text
Hard Failure 8 audit/status:
0f35ec895c756348e8a10803c6dd961a37344fb0

Amendment 5F-B rebinding/governance:
052e8ecc04f566b75666d5cc96df74d2ed5061e4

Amendment 5F-B approval governance:
84d39707dee15729dc0c35c85a16f4e31dac89e4

Amendment 5F-B package:
f33ee70233ea4098b2d7a17cfde3d266081ee693

Amendment 5F-A implementation/evidence:
e7b688d4b67db596df1d447e2cf70f12f0ea5d0b

Amendment 5F-A approval governance:
273341960858930246ae0c1441440aede0403a65

Amendment 5F-A package:
2b82ba3f0ac9756091d74567f4aed8df5cdf626d

Hard Failure 7:
f18d551b17f1bbed645ac159ebe52b7d6b9d8e54

Hard Failure 4:
b21852a174b537c90a848699deb4d26d6f169506

v2.3.1 implementation:
34349c70ee24b8240fd169393134d4280968b790
```

Any approval must explicitly bind the future commit containing this request, its Manifest, Hard Failure 8 Review 1, and the corresponding final approval-governance bytes. Approval that omits that package commit is invalid.

## Accepted Baseline

Independent review accepts Hard Failure 8 and preserves the 5F-B post-approval rebinding evidence:

```text
tests: 205/205
typed-policy tests: 44
failures/errors/skips: 0/0/0
official access: 0
path-helper official invocation: 0
formal preflight invocation: 0
token use: 0
capture invocation: 0
tracked files: 26
tracked-byte digest:
0BA07EC11A82125DE5B11C12ED618096106E3802FA7E897CAB302508AC739DD5
evidence bytes: 51922
evidence SHA-256:
829289F10B1C7B39BBE6B37ACF51DCB265764FD10A8DA55892F60D50F6D2CB09
byte-identical: true
```

The accepted review is `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_8_REVIEW_1.md`.

## Requested Implementation Scope

Only these implementation/test paths may change after a future explicit approval:

```text
scripts/stage4b_u1_preflight_execution_head_binding.py       new
tests/test_stage4b_u1_preflight_execution_head_binding.py   new
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
```

The runner may change only to bind 5G-A governance, discover the new tests, require the new active proofs and emit deterministic evidence. No existing test file may change.

## Derived Execution-HEAD Helper Contract

The helper must be a deterministic, standard-library-only, value-free validator over Git facts supplied by its caller. It must not execute Git, access the filesystem, open governance files, inspect official paths or invoke another helper or command.

The helper may expose a function equivalent to:

```python
validate_execution_head_binding(
    local_head,
    origin_main,
    github_main,
    head_parent,
    approval_governance_commit,
    changed_paths,
    allowed_rebinding_paths,
    required_ancestor_commits,
    observed_ancestor_commits,
    worktree_clean,
    governance_binding,
    expected_package_commit,
    expected_approval_commit,
)
```

The exact public signature may be simplified during implementation, but all frozen semantics below must remain explicit and testable.

The helper must:

1. require every commit value to be a full lowercase 40-character hexadecimal SHA;
2. reject uppercase, 39/41-character, non-hexadecimal, empty and non-text SHA inputs;
3. require `local_head == origin_main == github_main`;
4. return that validated current HEAD rather than compare it with a separately supplied future expected-HEAD literal;
5. prohibit any `expected_head`, future rebinding SHA or equivalent pre-transcribed-current-HEAD input;
6. require the current HEAD's direct parent to equal the approval-governance commit exactly;
7. require the changed-path set to equal the caller-supplied allowed rebinding/governance path set exactly, rejecting missing and extra paths;
8. require all package, approval and historical implementation commits supplied as required ancestors to appear in the caller-supplied observed ancestor set;
9. require a clean worktree fact;
10. require governance-binding metadata to identify the exact expected package and approval commits and to report required rebinding/governance artifacts present;
11. reject duplicate, non-text, absolute, parent-traversal or non-repository-relative changed paths;
12. return only value-free validation metadata and the validated execution HEAD; it must not return governance file contents or changed-file contents.

Core principle:

```text
derive and validate the future rebinding HEAD
not pre-transcribe the future rebinding HEAD
```

## Synthetic Verification

The accepted 205-test suite is the baseline. A future approved implementation must add at least 16 execution-head-binding tests and run a complete suite of at least 221 tests twice on identical tracked bytes.

Required coverage includes:

- identical full local/origin/GitHub SHA values pass;
- each of the three mismatch positions rejects;
- same short prefix with different full SHA rejects;
- 39-character, 41-character, non-hexadecimal, uppercase, empty and non-text SHA rejects;
- direct parent not equal to approval commit rejects;
- an extra intermediate commit rejects through the direct-parent gate;
- an extra or missing changed path rejects;
- code, existing test, result, cache or experiment path in changed paths rejects;
- missing governance-binding or rebinding-evidence presence rejects;
- exact allowed changed-path set passes;
- missing required ancestor rejects;
- dirty worktree fact rejects;
- package/approval mismatch inside governance-binding metadata rejects;
- no fixed future rebinding SHA appears in helper source;
- helper performs no filesystem, Git/subprocess, official-path, typed-helper, path-helper, token or capture operation;
- output is value-free and does not leak governance or changed-file contents.

Both complete runs must satisfy:

```text
tests >= 221
execution-head-binding tests >= 16
failures/errors/skips = 0/0/0
official access = 0
typed-helper official invocation = 0
path-helper official invocation = 0
formal preflight invocation = 0
token use = 0
capture invocation = 0
evidence byte-identical = true
```

## Frozen Existing Surface

The following remain frozen:

- typed argument-policy helper;
- Windows path-equivalence helper;
- capture and comparator;
- common, controller and retrieval implementations;
- every existing test file;
- exact 32-element capture argv and raw-byte controlling gate;
- data, cache, model, batch size, max length, effective-K, q25, score, ECDF, budget, trigger, ranking, endpoint and stop rules.

The Manifest records the exact existing frozen hashes. No scientific behavior is requested to change.

## Explicitly Not Authorized

This package does not authorize:

- creating or modifying the proposed helper, test or runner;
- running synthetic verification;
- real Git/GitHub execution-head validation;
- a second formal preflight;
- typed/path helper official calls;
- official input metadata/content access;
- authorization token use or capture;
- controller, verifier, evaluator/Gold, reservation or Stage3B;
- code/test changes outside the three proposed paths;
- 5G-B package assembly;
- automatic recovery of Hard Failure 8.

After a future approved 5G-A implementation/evidence push, execution must stop for independent review. Only a later explicit review may authorize assembly of a 5G-B official diagnostic package.

## Requested Completion State

```text
AMENDMENT_5G_A_SYNTHETICALLY_VERIFIED
HARD_FAILURE_8_DIRECT_CAUSE_CONFIRMED
HARD_FAILURE_4_DIAGNOSIS_INCOMPLETE

SECOND_FORMAL_PREFLIGHT_NOT_APPROVED
TYPED_HELPER_OFFICIAL_CALL_NOT_APPROVED
PATH_HELPER_OFFICIAL_CALL_NOT_APPROVED
OFFICIAL_INPUT_ACCESS_NOT_APPROVED
AUTHORIZATION_TOKEN_USE_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
