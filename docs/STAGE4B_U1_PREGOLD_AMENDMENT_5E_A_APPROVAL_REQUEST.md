# Stage4B-U1-D Pre-Gold Amendment 5E-A Approval Request

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-14
- Request ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_5E_A_WINDOWS_TEMP_PATH_EQUIVALENCE_IMPLEMENTATION_SYNTHETIC_ONLY`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5E_A_MANIFEST.json`
- Current state: `AMENDMENT_5D_B_OFFICIAL_DIAGNOSTIC_STOPPED_HARD_FAILURE_6`
- Package state: `AWAITING_AMENDMENT_5E_A_APPROVAL`
- Formal preflight retry: `NOT_APPROVED`
- Official capture: `NOT_APPROVED`
- Other project conversations, thread tools, and global memory used: No

## Binding History

```text
Hard Failure 6 audit/status:
bebfeb5664f26795b8d3472f3729ca1bb9abf889

Amendment 5D-B rebinding/governance:
2447ad234c160c6e615d81b33dc4ede7ecaa18da

Amendment 5D-B final approval governance:
1c46dc1b69f8381598aacb9f3b1e27561c7f9ee2

Amendment 5D-B package:
f67061e753b03a5cf46d7a7c92b5a95fc79b0ef8

Amendment 5D-A implementation/evidence:
02f46447e4cd69a15d2af14ee1fc62f9eb4f8bb9

Amendment 5D-A package:
33ce115f78840956fcc7bda0c3f4e172579350e7

Amendment 5D-A approval governance:
7f879a628fc313e24e805d9bdc5a81b06c37304a

Amendment 5C-B final diagnostic/audit:
e5f28f664449c02b12a129aaa2a011bad84dab91

Hard Failure 5:
deccd203059d05dc27ba80aca1ddb1e2ea8f616f

Hard Failure 4:
b21852a174b537c90a848699deb4d26d6f169506

v2.3.1 implementation:
34349c70ee24b8240fd169393134d4280968b790
```

Any approval must explicitly bind the future commit containing this request, its Manifest, the Hard Failure 6 review, and the corresponding governance state. Approval that omits that package commit is invalid.

## Accepted Failure Review

`docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_6_REVIEW_1.md` accepts the Hard Failure 6 audit and confirms that the 5D-B preflight count is consumed. It returns the project for a new implementation/synthetic-only Amendment rather than permitting a retry.

The failure expression compared an exact Manifest directory without a trailing separator to `.NET GetTempPath()`, which returns a trailing separator. Both identify the same directory, but the inline expression performed string equality without first trimming ending separators. The failure occurred before any of the five official inputs was opened or hashed and is not evidence of input, cache, comparator, capture, or controller drift.

## Requested Authorization

Approval is requested only for these implementation/test paths:

```text
scripts/stage4b_u1_preflight_path_equivalence.py                 new file
tests/test_stage4b_u1_preflight_path_equivalence.py             new file
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
```

The first two paths must not exist before implementation. The runner may change only to bind 5E-A governance, include the new test module and active proof tests, raise the complete-suite minimum, add helper-specific access/call evidence, and emit 5E-A deterministic evidence.

No other implementation or existing test file may change.

## Path-Equivalence Helper Contract

The tracked helper must be standard-library-only and expose a reusable fail-closed function that compares an actual directory path with an expected directory path. The function must:

1. Require both inputs to be absolute before normalization.
2. Require both paths to exist at call time.
3. Require both paths to be directories rather than files.
4. Reject a leaf path carrying Windows `FILE_ATTRIBUTE_REPARSE_POINT`, including symlink and junction aliases.
5. Compute full normalized paths, collapse `.` segments and separator spelling, and trim ending directory separators for comparison only.
6. Compare the normalized Windows path strings using ordinal case-insensitive semantics.
7. Require exact normalized-directory equality; parent, child, sibling and prefix relationships are not equality.
8. Never use string-prefix acceptance such as `startswith`.
9. Never broaden the accepted directory to an arbitrary parent or child.
10. Never rewrite, mutate, or replace the exact official capture command or its `--temp-parent` argument.
11. Never read a file's content or inspect any official input.
12. Return or emit only deterministic path-validation metadata; no authorization token or execution authority may be embedded in the helper.

The implementation may offer a small CLI for later preflight use, but the CLI must call the same tested function. It must not contain official data paths, official SHA values, capture logic, or a capture authorization token.

## Required Accepted And Rejected Forms

On Windows, synthetic tests must prove that these spellings of the same existing directory are accepted:

```text
C:\Users\cc\AppData\Local\Temp
C:\Users\cc\AppData\Local\Temp\
c:\users\cc\appdata\local\temp
C:/Users/cc/AppData/Local/Temp/
C:\Users\cc\AppData\Local\Temp\.\
```

Tests must construct their own synthetic existing directory and derive equivalent variants from it; they must not open the official units, queries, channel audit, cache, reference decisions, source audit, or any other official path.

These categories must fail closed:

```text
parent directory
child directory
sibling or prefix-collision directory such as Temp2
unrelated directory
relative path
nonexistent path
file path
symlink, junction, or reparse-point path
```

Reparse-point behavior must be tested deterministically without requiring elevated Windows privileges or permitting a skipped test. Mocking or patching the helper's leaf-attribute probe is allowed for this synthetic proof.

## Synthetic Verification Plan

The verified baseline is the 143-test 5D-B post-approval suite:

```text
path: results/stage4b_u1_d_pregold_amendment_5d_b_synthetic_rebinding.json
bytes: 29643
SHA-256: 264200C2EBEDA1D0B214F824B77C89FC5BBE82D3BE0836FAAB9486EACAACF368
tests: 143
failures/errors/skips/official access: 0
```

At least 12 new path-equivalence/preflight tests are required, so the complete deterministic suite must contain at least 155 tests. The new tests must cover all accepted/rejected categories above, exact equality rather than prefix logic, CLI/function consistency if a CLI exists, no exact-command mutation, deterministic metadata, and no official-path access.

The updated runner must bind:

- this request and Manifest;
- the future package-bound approval decision;
- Hard Failure 6 audit and Review 1;
- final approved `AGENTS.md`;
- all three allowed implementation/test paths;
- every frozen file hash in the Manifest.

The final complete suite must run twice on identical tracked bytes. Both runs must satisfy:

```text
tests >= 155
failures = 0
errors = 0
skipped = 0
official-path access attempts = 0
formal preflight invocations = 0
authorization token uses = 0
official capture invocations = 0
complete evidence byte-identical = true
```

The implementation audit must record every command, including failed commands; every allowed/frozen file SHA-256; the exact helper/runner/test diff; proof that no official path was opened; and proof that capture/comparator/controller/common/retrieval remained unchanged.

## Completion Boundary

If independently approved and all synthetic gates pass, 5E-A may produce only:

- the helper implementation and synthetic tests;
- the updated deterministic runner;
- one implementation audit;
- deterministic 5E-A evidence;
- one implementation/evidence commit and GitHub push;
- one implementation-bound Amendment 5E-B request/Manifest;
- necessary governance, README, ROADMAP and reproducibility status updates.

After the 5E-B package is pushed, execution must stop for independent approval.

## Explicitly Not Requested

This request does not authorize:

- implementing any file before a future package-bound 5E-A approval;
- opening, hashing, parsing or performing metadata checks on any official input;
- running a formal preflight or path-check against the real official temp boundary;
- passing or embedding any capture authorization token;
- running capture, comparator on official decisions, controller, verifier or evaluator;
- generating temporary or formal official decisions, rankings, policy, controller audit or `VERIFIED_PRE_GOLD`;
- reading rankings, reference policy, source audit, 5C-B machine inventory, evaluator/Gold, reservation or Stage3B;
- modifying capture, comparator, controller, retrieval, common, prepare, evaluator, verifier, model, parameters, effective-K, q25, score, ECDF, budget, trigger, ranking, endpoint, raw-byte equivalence or stop rules;
- creating, rebuilding, overwriting, deleting or migrating any cache, official artifact, prior evidence or failure record;
- retrying 5D-B preflight/capture or automatically starting 5E-B.

## Requested Completion State

```text
AMENDMENT_5E_A_SYNTHETICALLY_VERIFIED
HARD_FAILURE_6_DIRECT_CAUSE_CONFIRMED
HARD_FAILURE_4_DIAGNOSIS_INCOMPLETE

FORMAL_PREFLIGHT_RETRY_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
