# Stage4B-U1-D Pre-Gold Amendment 5F-A Approval Request

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-14
- Request ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_5F_A_TYPED_CAPTURE_ARGUMENT_POLICY_IMPLEMENTATION_SYNTHETIC_ONLY`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5F_A_MANIFEST.json`
- Current state: `AMENDMENT_5E_B_FORMAL_PREFLIGHT_STOPPED_HARD_FAILURE_7`
- Package state: `AWAITING_AMENDMENT_5F_A_APPROVAL`
- Formal preflight retry: `NOT_APPROVED`
- Official capture: `NOT_APPROVED`
- Other project conversations, thread tools, and global memory used: No

## Binding History

```text
Hard Failure 7 audit/status:
f18d551b17f1bbed645ac159ebe52b7d6b9d8e54

Amendment 5E-B rebinding/governance:
3185c3bd4ffd3eb2bc61b52fdf18a3367b9dca76

Amendment 5E-B approval governance:
f2f2e249e4e7a52fcc44b61a2245d8d50d79106d

Amendment 5E-B package:
e387d2707ede9024571249face71bf7ca3afd4e0

Amendment 5E-A implementation/evidence:
a8b064a4a2133aea27cbe9b85978237fc3dae661

Amendment 5E-A approval governance:
461939434206764555b917c5971956e6951ff4dd

Amendment 5E-A package:
19f16f559f0b1f3b59ef24a04e368f99ae3635e3

Hard Failure 6 audit/status:
bebfeb5664f26795b8d3472f3729ca1bb9abf889

Hard Failure 4:
b21852a174b537c90a848699deb4d26d6f169506

v2.3.1 implementation:
34349c70ee24b8240fd169393134d4280968b790
```

Any approval must explicitly bind the future commit containing this request, its Manifest, the Hard Failure 7 audit and Review 1, and the corresponding governance state. Approval that omits that package commit is invalid.

## Accepted Failure Review

`docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_7_REVIEW_1.md` accepts the Hard Failure 7 audit and confirms that the 5E-B preflight count is consumed. It returns the project for a new implementation/synthetic-only Amendment rather than permitting a preflight retry or direct argument-policy edit.

The preflight A gate proved that the runtime argv was element-by-element identical to the approved exact capture command. The B gate then treated every argv value as an untyped string and matched the raw substring `gold` inside the allowed protocol term `pregold` in the frozen machine-audit output path. The failure occurred before the path-equivalence helper, official-input metadata/content access, token use, or capture. It is an argument-classification defect rather than evidence of scientific or runtime drift.

## Requested Authorization

Approval is requested only for these implementation/test paths:

```text
scripts/stage4b_u1_preflight_argument_policy.py                 new file
tests/test_stage4b_u1_preflight_argument_policy.py             new file
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
```

The first two paths must not exist before implementation. The runner may change only to bind 5F-A governance, include the new test module and active proof tests, raise the complete-suite minimum to 177, add typed-policy access/call evidence, and emit deterministic 5F-A evidence.

No other implementation or existing test file may change.

## Typed Capture-Argument Policy Contract

The tracked helper must be deterministic, fail-closed, and standard-library-only. It must expose a reusable function that validates an actual capture argv against an externally frozen approved argv without accessing the filesystem or executing the command.

The controlling structure is:

```text
exact argv equality
typed flag allowlist
per-role exact value binding
explicit prohibited-role rejection
```

The helper must:

1. Fix the executable to `python` and the capture script to `scripts/stage4b_u1_capture_diagnostic_decisions.py`.
2. Fix the 15 allowed flags, their order, and the total 32-element argv shape registered by the frozen 5E-B Manifest.
3. Require every allowed flag exactly once.
4. Reject unknown flags, duplicate flags, missing flags, missing values, extra values, and additional positional arguments.
5. Validate each value by its typed role without opening or statting any path.
6. Bind the seven path roles (`--units`, `--queries`, `--channel-audit`, `--embedding-cache`, `--reference-decisions`, `--audit-output`, and `--temp-parent`) to their exact corresponding values in the externally frozen 5E-B `exact_capture_command`.
7. Bind `--official-authorization-token` to its exact externally frozen token value.
8. Accept the exact frozen `--audit-output` value even though its filename contains `pregold`.
9. Explicitly reject prohibited roles including `--rankings`, `--policy`, `--gold-map`, `--source-audit`, `--evaluator`, `--reservation`, and `--stage3b`.
10. Never scan arbitrary values with `contains("gold")`, `IndexOf("gold")`, a regular-expression bare substring, or equivalent keyword matching.
11. Never call `open`, `stat`, `lstat`, hashing APIs, subprocesses, the capture module, or the existing path-equivalence helper.
12. Never use a token, execute a command, or embed official execution authority.
13. Return only deterministic validation metadata or raise a deterministic policy error.

The externally frozen approved argv remains the `exact_capture_command` member of `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5E_B_MANIFEST.json`, whose tracked file is 17,286 bytes with SHA-256 `EC83E0EABF0286420E03C2A55C9E5559041C392FB0FED9B48F9A614E9720E854` at package commit `e387d2707ede9024571249face71bf7ca3afd4e0`. 5F-A does not authorize reading any path named by that argv; it only freezes the future policy input.

## Typed Value Rules

Synthetic implementation must distinguish these role classes:

- executable and capture script: exact literal equality;
- seven path values: non-empty string, syntactically absolute Windows path, and exact equality to the corresponding externally frozen value in future official use;
- model name: non-empty exact string binding;
- batch size and max length: canonical positive decimal integer strings and exact binding;
- four expected SHA-256 values: exactly 64 uppercase hexadecimal characters and exact binding;
- authorization token: non-empty exact string binding, never consumed by the helper.

Exact argv equality remains controlling. Typed and role checks explain and harden the policy but cannot relax or replace exact equality.

## Synthetic Verification Plan

The verified baseline is the 161-test 5E-B post-approval suite:

```text
path: results/stage4b_u1_d_pregold_amendment_5e_b_synthetic_rebinding.json
bytes: 36518
SHA-256: BF4C668C76C4B8545882C894F241038765AFD8DD263B4195D9E2D654B7B9FC1A
tests: 161
failures/errors/skips/official access: 0
path-helper official invocations/preflight/token/capture: 0
```

At least 16 new typed argument-policy tests are required, so the complete deterministic suite must contain at least 177 tests. The new tests must cover:

- the original frozen exact argv shape passing on a synthetic no-access policy fixture;
- `pregold` in the machine-output path passing;
- `gold` as an ordinary value substring not acting as a role denylist;
- unknown, duplicate, missing, reordered, or extra arguments failing closed;
- individual drift rejection for units, queries, channel audit, cache, reference decisions, audit output, temp parent, and token;
- explicit rejection of rankings, policy, Gold map, source audit, evaluator, reservation, and Stage3B roles;
- typed rejection for malformed integer and SHA roles;
- active proof that the helper does not call filesystem metadata/content APIs, hashing, subprocess, capture, token-use, or the path-equivalence helper;
- source/AST proof that no raw `gold` value-substring denylist is used.

The updated runner must bind:

- this request and Manifest;
- the future package-bound approval decision;
- Hard Failure 7 audit and Review 1;
- final approved `AGENTS.md`;
- all three allowed implementation/test paths;
- every frozen file hash in the Manifest.

The final complete suite must run twice on identical tracked bytes. Both runs must satisfy:

```text
tests >= 177
failures = 0
errors = 0
skipped = 0
official metadata/content access attempts = 0
path helper official invocations = 0
formal preflight invocations = 0
authorization token uses = 0
official capture invocations = 0
complete evidence byte-identical = true
```

The implementation audit must record every command, including failed commands; every allowed/frozen file SHA-256; the exact helper/runner/test diff; proof that no official path was opened; proof that the path helper, capture, comparator, common, controller, and retrieval files remained unchanged; and proof that the exact capture command and raw-byte equivalence remained unchanged.

## Completion Boundary

If independently approved and all synthetic gates pass, 5F-A may produce only:

- the typed argument-policy helper and synthetic tests;
- the updated deterministic runner;
- one implementation audit;
- deterministic 5F-A evidence;
- one implementation/evidence commit and GitHub push;
- necessary governance, README, ROADMAP, and reproducibility status updates.

After the 5F-A implementation/evidence commit is pushed, execution must stop for independent review. Amendment 5F-B may be assembled only after that independent review explicitly accepts the 5F-A implementation and evidence.

## Explicitly Not Requested

This request does not authorize:

- implementing any file before a future package-bound 5F-A approval;
- opening, hashing, parsing, or performing metadata checks on any official input;
- calling the path-equivalence helper against the real OS-temp boundary;
- running a formal preflight or using a capture authorization token;
- running capture, comparator on official decisions, controller, verifier, or evaluator;
- generating temporary or formal official decisions, rankings, policy, controller audit, or `VERIFIED_PRE_GOLD`;
- reading rankings, reference policy, source audit, 5C-B inventory, evaluator/Gold, reservation, or Stage3B;
- modifying the existing path helper, capture, comparator, common, controller, retrieval, data, model, parameters, effective-K, q25, score, ECDF, budget, trigger, ranking, endpoint, raw-byte equivalence, or stop rules;
- creating, rebuilding, overwriting, deleting, or migrating any cache, official artifact, historical evidence, or failure record;
- retrying 5E-B preflight/capture;
- automatically assembling, starting, or approving 5F-B before independent acceptance of 5F-A implementation/evidence.

## Requested Completion State

```text
AMENDMENT_5F_A_SYNTHETICALLY_VERIFIED
HARD_FAILURE_7_DIRECT_CAUSE_CONFIRMED
HARD_FAILURE_4_DIAGNOSIS_INCOMPLETE

FORMAL_PREFLIGHT_RETRY_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
