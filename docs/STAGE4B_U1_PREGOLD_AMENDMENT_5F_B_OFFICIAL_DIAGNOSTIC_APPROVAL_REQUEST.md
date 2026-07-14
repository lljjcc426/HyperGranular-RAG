# Stage4B-U1-D Pre-Gold Amendment 5F-B Official Diagnostic Approval Request

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-14
- Request ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_5F_B_TYPED_HELPER_BOUND_SINGLE_PREFLIGHT_AND_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5F_B_MANIFEST.json`
- Current state: `AMENDMENT_5F_A_IMPLEMENTATION_AND_EVIDENCE_ACCEPTED`
- Package state: `AWAITING_AMENDMENT_5F_B_APPROVAL`
- Package assembly authorization: `AUTHORIZED_BY_5F_A_REVIEW_1`
- Formal preflight: `NOT_APPROVED`
- Path-helper official-boundary check: `NOT_APPROVED`
- Authorization token use: `NOT_APPROVED`
- Official capture: `NOT_APPROVED`
- Other project conversations, thread tools, and global memory used: No

## Binding History

```text
Amendment 5F-A package:
2b82ba3f0ac9756091d74567f4aed8df5cdf626d

Amendment 5F-A approval governance:
273341960858930246ae0c1441440aede0403a65

Amendment 5F-A implementation/evidence:
e7b688d4b67db596df1d447e2cf70f12f0ea5d0b

Hard Failure 7:
f18d551b17f1bbed645ac159ebe52b7d6b9d8e54

Amendment 5E-B rebinding/governance:
3185c3bd4ffd3eb2bc61b52fdf18a3367b9dca76

Amendment 5E-B approval governance:
f2f2e249e4e7a52fcc44b61a2245d8d50d79106d

Amendment 5E-B package:
e387d2707ede9024571249face71bf7ca3afd4e0

Amendment 5E-A implementation/evidence:
a8b064a4a2133aea27cbe9b85978237fc3dae661

Hard Failure 6:
bebfeb5664f26795b8d3472f3729ca1bb9abf889

Hard Failure 4:
b21852a174b537c90a848699deb4d26d6f169506

v2.3.1 implementation:
34349c70ee24b8240fd169393134d4280968b790
```

Any approval must explicitly bind the future commit containing this request, its Manifest, Amendment 5F-A Review 1, and the corresponding governance state. Approval that omits that package commit is invalid.

## Accepted 5F-A Review

`docs/STAGE4B_U1_PREGOLD_AMENDMENT_5F_A_REVIEW_1.md` accepts the 5F-A implementation and deterministic evidence at `e7b688d4b67db596df1d447e2cf70f12f0ea5d0b`. It authorizes only assembly of this 5F-B package. It does not authorize synthetic rebinding, a real OS-temp helper call, formal preflight, token use, capture, controller, verifier, or Gold.

The accepted typed helper removes Hard Failure 7's argument-classification defect without relaxing exact argv equality. It validates explicit flag roles and typed values; it does not scan arbitrary values for the substring `gold`.

## Requested Future Authorization

This package requests a future package-bound approval for exactly this sequence:

1. commit and push 5F-B approval governance;
2. on the final approved governance bytes, run the complete 205-test synthetic suite twice and require byte-identical evidence;
3. create and push a governance-binding JSON and rebinding audit;
4. run one A/B/C/D formal preflight in the frozen order below;
5. only if every preflight gate passes, invoke the unchanged exact capture command once;
6. verify aggregate-only output, unchanged input fingerprints, temporary cleanup and continued formal-output absence;
7. create one narrative audit, commit, push, verify GitHub and stop.

This package itself authorizes none of those commands.

## Frozen Implementation

No implementation or test modification is requested. The accepted 5F-A evidence contains 26 `implementation_hashes`, including the historical `AGENTS.md` bytes at implementation commit `e7b688d4b67db596df1d447e2cf70f12f0ea5d0b`. Because this 5F-B package and any future approval governance necessarily update `AGENTS.md`, a future preflight must verify that historical `AGENTS.md` hash against the Git blob at `e7b688d...`, recompute the other 25 accepted hashes against the current tree, and separately recompute all 26 current hashes recorded by the post-approval rebinding evidence. It must not compare the final governance `AGENTS.md` to the historical 5F-A hash.

Two helpers are separately frozen:

```text
typed argument-policy helper:
scripts/stage4b_u1_preflight_argument_policy.py
bytes: 7082
SHA-256:
CCDC70D2E66E9D69CD64899676EA5150FEE0381E74F4C9DEED2A0FFB5EE436F4
function: validate_capture_argv

Windows path-equivalence helper:
scripts/stage4b_u1_preflight_path_equivalence.py
bytes: 3543
SHA-256:
1A17C0E750F91CEF2F638A0B0C6FD381110692E6B2D467C1F5243ADF3F35B3FF
function: windows_directories_equivalent
```

No inline reimplementation or fallback is permitted for either helper.

## Post-Approval Synthetic Rebinding

Before formal preflight, a future approval must require two complete runs using the unchanged runner:

```text
runner:
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
bytes: 18120
SHA-256:
31F2233CA9ACF7F156C24B6CD2F0268F7816CC3DE745E783711C2E58E7459D7F
```

Both runs must use identical tracked bytes and satisfy:

```text
tests: 205/205
typed-policy tests: 44
failures/errors/skips: 0/0/0
official metadata/content access: 0
path-helper official invocation: 0
formal preflight invocation: 0
authorization token use: 0
official capture invocation: 0
complete evidence byte-identical: true
```

The rebinding evidence, governance-binding JSON and audit must bind at least:

- this 5F-B request and Manifest;
- the future package-bound 5F-B approval decision;
- final approved `AGENTS.md`;
- 5F-A Review 1;
- 5F-A implementation audit and deterministic evidence;
- the post-approval 5F-B rebinding evidence.

They must be committed and pushed before formal preflight.

## Single Formal Preflight

Only one 5F-B formal preflight invocation is requested. It must stop on any failure and must not be retried under the same approval.

### A. Project, Governance, Hashes And Output Absence

Before helper or official input access, A must verify:

- clean local `HEAD`, synchronized exactly with GitHub `main`;
- package, approval governance, 5F-A implementation/evidence and 5F-B rebinding/governance commits are ancestors;
- 5F-A evidence bytes/SHA match, the historical `AGENTS.md` Git blob at `e7b688d...` matches its evidence-bound hash, and the other 25 accepted implementation hashes recompute exactly against the current tree;
- all 26 current implementation hashes in the post-approval rebinding evidence, including final approved `AGENTS.md`, recompute exactly;
- 5F-B request, Manifest, approval decision, final `AGENTS.md`, rebinding evidence and governance binding match their committed hashes;
- the typed helper, path helper, capture, comparator, runner and tests match frozen bytes/SHA;
- the historical machine audit, future narrative audit, all five formal outputs and diagnostic OS-temp residue are absent;
- no 5E-B failure artifact, historical evidence or cache has been modified.

A may inspect only project/governance/output-path metadata required for those gates. It may not inspect any of the five official input paths.

### B. Typed Capture-Argument Policy Helper

B must occur before the path helper and before official input metadata/content access.

It must:

1. hash-check the typed helper before import;
2. hash-check `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5E_B_MANIFEST.json` at 17,286 bytes and SHA-256 `EC83E0EABF0286420E03C2A55C9E5559041C392FB0FED9B48F9A614E9720E854`;
3. parse `actual_argv` only from this 5F-B Manifest's `exact_capture_command`;
4. parse `approved_argv` only from the hash-bound 5E-B Manifest's `exact_capture_command`;
5. directly import and call `validate_capture_argv(actual_argv, approved_argv)`;
6. require `status=VALID`, `exact_argv_equal=true`, 32 elements, 15 flags, seven path roles, zero prohibited roles and all no-access/no-execution metadata false;
7. reject any helper exception, non-VALID result, hash drift or argv drift as a hard failure.

B must not scan arbitrary values with `gold` or any other keyword. It must not open, hash, stat or parse paths named by the argv. The token string may be compared as inert governance text but must not be passed to capture or consumed.

### C. Windows OS-Temp Path-Equivalence Helper

C may run only after B passes. It must:

1. hash-check the existing path helper before import;
2. obtain the unmodified runtime value from `.NET System.IO.Path.GetTempPath()`;
3. directly call `windows_directories_equivalent(runtime_value, "C:\\Users\\cc\\AppData\\Local\\Temp")`;
4. require `True` and zero exit status;
5. reject any exception, `False`, hash drift or inline fallback as a hard failure.

The runtime value and exact capture `--temp-parent` string must not be trimmed, rewritten or replaced before the helper call.

### D. Five Permitted Official Inputs

D may begin only after both B and C pass. It may inspect only:

1. v2.3.1 unlabeled units;
2. v2.3.1 unlabeled queries;
3. v2.3.1 controller channel audit;
4. the existing ID-bound embedding cache;
5. the frozen v2.2 reference decisions.

D must verify regular-file status, exact paths, SHA-256, cache bytes/members/IDs/model metadata/dtype/shapes/finite values/normalization, channel/source/dual-ID boundary, query/unit counts and reference decisions fingerprint exactly as frozen in the Manifest.

The Stage4A-R2 source-audit file may not be opened; only the source-audit digest already registered inside the permitted controller channel audit may be checked. Rankings, reference policy, 5C-B inventory, evaluator/Gold, reservation and Stage3B remain outside the read boundary.

### E. Conditional Single Unchanged Capture

Only if A, B, C and D all pass may the exact 32-element capture command in the Manifest run once. No element, token string, path, model, parameter, SHA, temp-parent value or output path may change.

Capture must remain decisions-only, use the existing cache, write temporary decisions under the exact OS-temp parent and delete them on success or failure. It must not read or generate rankings, build policy, run the full controller, verifier or evaluator, or promote any formal output.

## Output And Stop Boundary

The unchanged capture may create only the historical aggregate machine-audit path registered by the exact command. A new 5F-B narrative audit may summarize only approved aggregate fields and pre/post fingerprint/cleanup booleans.

Allowed machine output remains limited to:

- raw bytes, size and SHA status;
- canonical digest and query-order/set difference counts;
- schema/order/type/discrete/float/ULP/decision-semantic aggregate counts;
- at most one salted query-ID hash;
- channel/cache/reference unchanged and temporary cleanup booleans.

It must not contain raw query IDs, raw decision rows, field values, question/text, rankings, policy or Gold content. Raw-byte equality remains controlling; canonical or semantic equality may explain but cannot replace it.

After machine/narrative audit validation, commit, push and GitHub verification, execution must stop. No conclusion about controller resumption, verifier or Gold is authorized.

## Explicitly Not Authorized By This Package

Until a future approval explicitly binds the 5F-B package commit, this package does not authorize:

- post-approval rebinding or governance binding;
- typed helper import/call against the official command boundary;
- real OS-temp path-helper invocation;
- formal preflight or any official input metadata/content access;
- authorization token use or official capture/comparator execution;
- controller, verifier, evaluator/Gold, reservation or Stage3B;
- rankings, reference policy, source-audit file or 5C-B inventory access;
- code, test, data, model, parameter, endpoint, equivalence or stop-rule changes;
- cache or historical artifact creation, modification, overwrite, migration or deletion;
- retry of any 5E-B action;
- automatic retry after any future 5F-B hard failure;
- automatic continuation after diagnostic completion.

## Requested Post-Diagnostic State

```text
AMENDMENT_5F_B_OFFICIAL_DECISIONS_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW
HARD_FAILURE_4_DIAGNOSIS_COMPLETE_AWAITING_REVIEW

CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
