# Stage4B-U1-D Pre-Gold Amendment 5F-A Review 1

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Review date: 2026-07-14
- Reviewed implementation/evidence commit: `e7b688d4b67db596df1d447e2cf70f12f0ea5d0b`
- Amendment 5F-A package: `2b82ba3f0ac9756091d74567f4aed8df5cdf626d`
- Amendment 5F-A approval governance: `273341960858930246ae0c1441440aede0403a65`
- Decision: `ACCEPT_AMENDMENT_5F_A_IMPLEMENTATION_AND_SYNTHETIC_EVIDENCE`
- Next authorization: `AUTHORIZE_AMENDMENT_5F_B_PACKAGE_ASSEMBLY_ONLY`
- Other project conversations, thread tools, and global memory used: No

## Review Decision

The Amendment 5F-A implementation and deterministic synthetic evidence are accepted. The only newly authorized action is assembly of an implementation-bound Amendment 5F-B approval package.

Current authorization state:

```text
ACCEPT_AMENDMENT_5F_A_IMPLEMENTATION_AND_SYNTHETIC_EVIDENCE
AUTHORIZE_AMENDMENT_5F_B_PACKAGE_ASSEMBLY_ONLY

FORMAL_PREFLIGHT_RETRY_NOT_APPROVED
PATH_HELPER_OFFICIAL_BOUNDARY_CHECK_NOT_APPROVED
AUTHORIZATION_TOKEN_USE_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

## Accepted Commit Chain

```text
5F-A package:
2b82ba3f0ac9756091d74567f4aed8df5cdf626d

5F-A approval governance:
273341960858930246ae0c1441440aede0403a65

5F-A implementation/evidence:
e7b688d4b67db596df1d447e2cf70f12f0ea5d0b
```

The implementation/test diff is limited to the typed argument-policy helper, its new test module, and the approved deterministic runner. All other changes are audit, evidence, or project-status documentation. No 5F-B package existed at the reviewed commit.

## Accepted Typed-Policy Semantics

The helper fixes the executable, capture script, 32-element argv shape and 15 ordered flags. Exact argv equality is the only acceptance path. Typed classification reinforces rejection for structural, path, integer, SHA-256, text, token, unknown and prohibited-role differences; it cannot relax exact equality.

The helper does not read a Manifest or hard-code the official argv. It accepts the approved `pregold` output spelling and uses explicit flag roles rather than arbitrary value-substring classification. Static and runtime tests establish no filesystem, hash, subprocess, capture, token-use or path-helper invocation and no raw `gold` value-substring denylist.

## Accepted Evidence

```text
tests: 205/205
typed-policy tests: 44
failures/errors/skips: 0/0/0
official metadata/content access: 0
path-helper official invocation: 0
formal preflight invocation: 0
authorization token use: 0
official capture invocation: 0
tracked-byte digest:
B58E85239F001B532B5CF378998B804B1202C5D6FF148311EF939DC4B3B4EA34
evidence bytes: 51922
evidence SHA-256:
A5B97077AD9A0C62EBFCAE9D70FC8B5BFAD19CCB32FF3A53E1FCF4BDB216D189
direct byte comparison: true
```

The accepted implementation hashes are:

```text
argument-policy helper:
CCDC70D2E66E9D69CD64899676EA5150FEE0381E74F4C9DEED2A0FFB5EE436F4

synthetic runner:
31F2233CA9ACF7F156C24B6CD2F0268F7816CC3DE745E783711C2E58E7459D7F

argument-policy tests:
9B338292E1A8CCAED0EFD114999999B1C884B7CC8861EBCB9BA8029D4D1498E2
```

All 17 Manifest frozen files retained their registered SHA-256.

## Required 5F-B Preflight Order

Any future 5F-B request must preserve this order:

```text
A. Git / governance / hashes / outputs absent
B. hash-bind and call the typed argument-policy helper
C. hash-bind and call the existing path-equivalence helper
D. only after B and C pass, access the five permitted official inputs
E. only after the complete preflight passes, run one unchanged capture
```

The package may request a future approval for that sequence, but package assembly itself authorizes none of the steps.

## Current State

```text
AMENDMENT_5F_A_IMPLEMENTATION_AND_EVIDENCE_ACCEPTED
AMENDMENT_5F_B_PACKAGE_ASSEMBLY_ALLOWED

FORMAL_PREFLIGHT_RETRY_NOT_APPROVED
PATH_HELPER_OFFICIAL_BOUNDARY_CHECK_NOT_APPROVED
AUTHORIZATION_TOKEN_USE_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
