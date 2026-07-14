# Stage4B-U1-D Pre-Gold Amendment 5G-A.1 Approval Request

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-14
- Request ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_A_1_ACTIVE_PROOF_GLOBAL_UNIQUENESS_REPAIR_AND_SYNTHETIC_RETRY_ONLY`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_A_1_MANIFEST.json`
- Current state: `RETURN_FOR_AMENDMENT_5G_A_1_PACKAGE`
- Requested mode: `MINIMAL_IMPLEMENTATION_REPAIR_AND_SYNTHETIC_VERIFICATION_RETRY_ONLY`
- Package itself authorizes modification or execution: No
- Official execution: `NOT_APPROVED`
- Other project conversations, thread tools, and global memory used: No

## Binding History

```text
5G-A package:
86ae4a83d55e61653f3cce9260a00852b4aaebda

5G-A approval governance:
fd50bc30f5acbf4955e3a051fbee70062e6e168c

Hard Failure 9 checkpoint:
d1c7cf9d78563e30a1e0fe0d6812b36d15b95a9a

Hard Failure 8:
0f35ec895c756348e8a10803c6dd961a37344fb0

5F-B rebinding/governance:
052e8ecc04f566b75666d5cc96df74d2ed5061e4

5F-B approval governance:
84d39707dee15729dc0c35c85a16f4e31dac89e4

5F-B package:
f33ee70233ea4098b2d7a17cfde3d266081ee693

Hard Failure 4:
b21852a174b537c90a848699deb4d26d6f169506

v2.3.1 implementation:
34349c70ee24b8240fd169393134d4280968b790
```

Any approval must explicitly bind the future package commit containing this request, its Manifest, Hard Failure 9 audit, Review 1 and final package-governance bytes. Approval that omits that package commit is invalid.

## Accepted Failure Evidence

Hard Failure 9 audit:

```text
path: docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_9.md
bytes: 5778
SHA-256: 91EDCBB01CC119EE72EB79108BC89C36F88FCAA03BD059ED9BCF7589B99D6643
```

Independent Review 1:

```text
path: docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_9_REVIEW_1.md
bytes: 4292
SHA-256: 2330EEF8C641C67313D96F59679C503AFC360D9626D8CA6E9B9376BDC3536F61
```

The accepted boundary is:

- execution-head targeted tests: 41/41, zero failure/error/skip;
- preliminary runner invocations: 1;
- complete-suite tests actually run by that invocation: 0;
- preliminary output/evidence created: No;
- synthetic retry after failure: 0;
- official/helper/preflight/token/capture actions: 0;
- frozen hashes: 24/24 unchanged.

## Frozen Failed Checkpoint

| Path | Bytes | SHA-256 | 5G-A.1 status |
|---|---:|---|---|
| `scripts/stage4b_u1_preflight_execution_head_binding.py` | 6,318 | `517C5C4DB22A82B4CBCA3D8BB751AAE60C0DCC5B5948CC8419D8770A9CC3D174` | frozen; no modification |
| `tests/test_stage4b_u1_preflight_execution_head_binding.py` | 11,550 | `52C0983E623D126F8A8E631DE7C8F08F14F04DA26484763CA6939B84236EC747` | only two test names may change |
| `scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py` | 22,351 | `EBCCA245F2B4D07CCF061DDD88D70E83C76563F4F4D547EEFF711307F92B0BB1` | only registered suffixes, tuple-uniqueness gate and exact counts may change |

## Requested Modification Scope

Only these two paths may change after a future explicit package-bound approval:

```text
tests/test_stage4b_u1_preflight_execution_head_binding.py
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
```

The helper must remain byte-identical at its frozen SHA. No existing test file may change.

## Exact Test-Name Repair

Only these two function names may change in the new execution-head module:

```text
test_missing_governance_binding_is_rejected
->
test_execution_head_missing_governance_binding_is_rejected

test_helper_uses_only_python_standard_library
->
test_execution_head_helper_uses_only_python_standard_library
```

The two test bodies, assertions, fixtures, inputs, call counts and helper semantics must remain byte-for-byte equivalent except for the function-name tokens. No test may be added, removed, skipped, split, merged or parameterized.

## Exact Runner Repair

The runner may only:

1. replace the two execution-head active-proof suffixes with the two unique names above;
2. retain generic `test_helper_uses_only_python_standard_library` exactly once for the existing path-equivalence test;
3. before test discovery, enforce:

```python
len(REQUIRED_ACTIVE_PROOF_SUFFIXES) == len(set(REQUIRED_ACTIVE_PROOF_SUFFIXES))
```

4. raise a dedicated duplicate-suffix error if that gate fails;
5. require exact final counts of 246 total tests, 41 execution-head tests and 44 typed-policy tests.

The runner must not change test-discovery pattern, other active-proof suffixes, official-path guard, tracked-file set, evidence schema, evidence output path, access counters, verified scientific properties or any existing helper semantics.

## Future Authorized Sequence Requested

After a future package-bound approval, request authorization only for this sequence:

1. create and push 5G-A.1 approval governance;
2. run one source-only active-proof inventory before importing or running tests;
3. require the suffix tuple itself to have no duplicates;
4. require every suffix to match exactly one globally discovered `test_*` definition;
5. run the execution-head targeted module exactly once and require 41/41;
6. on final stable tracked bytes, run the complete suite exactly twice;
7. require each complete run to be exactly 246/246 with 41 execution-head tests and 44 typed-policy tests;
8. directly compare both complete evidence files byte-for-byte;
9. write implementation/recovery audit, commit, push and immediately stop.

No preliminary complete runner is requested. Any inventory, targeted or final hard-gate failure must stop without correction or retry.

## Exact Final Synthetic Gates

Both complete runs must satisfy:

```text
tests = 246
execution-head tests = 41
typed-policy tests = 44
failures = 0
errors = 0
skipped = 0

official access = 0
typed-helper official invocation = 0
path-helper official invocation = 0
real Git/GitHub execution-head validation = 0
formal preflight invocation = 0
authorization token use = 0
official capture invocation = 0

tracked bytes identical = true
evidence byte-identical = true
```

Formal evidence path remains unchanged from the failed runner and must be absent before the future first final run:

```text
results/stage4b_u1_d_pregold_amendment_5g_a_synthetic_verification.json
```

## Frozen Surface

The execution-head helper, all 24 5G-A Manifest frozen files, every existing test, exact 32-element capture argv, raw-byte controlling gate, data, cache, model, batch size, max length, effective-K, q25, score, ECDF, budget, trigger, ranking, endpoint and stop rules remain frozen.

The two failed-checkpoint files may change only as explicitly stated. No scientific behavior or official execution behavior is requested to change.

## Required Audit

The future implementation/recovery audit must record:

- exact two-file diff against `d1c7cf9d78563e30a1e0fe0d6812b36d15b95a9a`;
- helper and 24 frozen-file bytes/SHA;
- source-only inventory command/output;
- the single targeted command and 41/41 result;
- both exact 246/246 complete runs;
- tracked-file count and digest for each run;
- evidence bytes/SHA and direct byte equality;
- all failed commands, if any;
- all official/helper/preflight/token/capture counters at zero;
- confirmation that no preliminary runner was invoked.

## Explicitly Not Authorized

This package does not authorize:

- renaming either test now;
- modifying the runner now;
- synthetic retry now;
- modifying the execution-head helper;
- modifying any other code, test, result or experiment artifact;
- real Git/GitHub execution-head validation;
- second formal preflight;
- typed/path helper official calls;
- official input metadata/content access;
- token, capture, comparator, controller, verifier or evaluator/Gold;
- reservation or Stage3B;
- 5G-B package assembly;
- automatic recovery of Hard Failure 9.

## Requested Completion State

```text
AMENDMENT_5G_A_1_SYNTHETICALLY_VERIFIED
HARD_FAILURE_9_DIRECT_CAUSE_CONFIRMED
HARD_FAILURE_8_DIRECT_CAUSE_CONFIRMED
HARD_FAILURE_4_DIAGNOSIS_INCOMPLETE

SECOND_FORMAL_PREFLIGHT_NOT_APPROVED
OFFICIAL_INPUT_ACCESS_NOT_APPROVED
AUTHORIZATION_TOKEN_USE_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
