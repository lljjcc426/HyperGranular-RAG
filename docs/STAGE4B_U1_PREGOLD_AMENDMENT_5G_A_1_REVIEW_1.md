# Stage4B-U1-D Pre-Gold Amendment 5G-A.1 Review 1

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Review date: 2026-07-15
- Reviewed implementation/evidence commit: `c21f3f58b2b1d4ccf235daba9c85937daedf4e3b`
- Decision: `ACCEPT_AMENDMENT_5G_A_1_IMPLEMENTATION_AND_SYNTHETIC_EVIDENCE`
- Next authorization: `AUTHORIZE_AMENDMENT_5G_B_PACKAGE_ASSEMBLY_ONLY`
- Other project conversations, thread tools, and global memory used: No

## Review Decision

The independent review accepts Amendment 5G-A.1 implementation and synthetic evidence. It authorizes only assembly of a new Amendment 5G-B request and machine-readable Manifest.

Current authorization state:

```text
ACCEPT_AMENDMENT_5G_A_1_IMPLEMENTATION_AND_SYNTHETIC_EVIDENCE
AUTHORIZE_AMENDMENT_5G_B_PACKAGE_ASSEMBLY_ONLY

POST_APPROVAL_REBINDING_NOT_APPROVED
REAL_EXECUTION_HEAD_CHECK_NOT_APPROVED
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

## Accepted Commit Order And Scope

```text
5G-A.1 package:
d02b19dfd5a527d0159b930662f5a868c8235d35

5G-A.1 approval governance:
3d818cee86e1faca16c2bdab3baf4fd5411cff75

5G-A.1 implementation/evidence:
c21f3f58b2b1d4ccf235daba9c85937daedf4e3b
```

Relative to approval governance, implementation/test changes were limited to:

```text
tests/test_stage4b_u1_preflight_execution_head_binding.py
scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py
```

The test diff was exactly two function-name token replacements. The runner diff was restricted to the corresponding suffix updates, retention of the generic path-helper suffix once, a pre-discovery tuple-uniqueness gate, and exact `246 / 41 / 44` count gates. The execution-head helper and all other frozen implementation files were unchanged.

## Accepted Frozen Files And Evidence

| Path | Bytes | SHA-256 |
|---|---:|---|
| `scripts/stage4b_u1_preflight_execution_head_binding.py` | 6,318 | `517C5C4DB22A82B4CBCA3D8BB751AAE60C0DCC5B5948CC8419D8770A9CC3D174` |
| `scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py` | 22,416 | `83816A962EDC8F06B53B5826E3F7519BD72D2CA0DF91C46751A9B12215867F28` |
| `tests/test_stage4b_u1_preflight_execution_head_binding.py` | 11,580 | `EA39A9ECEBA36FE2BAA108B2C4B1C98981C8A5E3FE241F59F22F5D49458E02B8` |
| `results/stage4b_u1_d_pregold_amendment_5g_a_synthetic_verification.json` | 69,144 | `A6285498FCFE767297D7156B87CA6034A993B2DFBB167EF7DFA813E9ADD55292` |

The accepted source-only inventory found 246 test definitions and 135/135 globally unique required suffix matches without test import or execution. The single targeted execution-head module run passed 41/41 with zero failure, error or skip.

Both final complete runs passed exactly:

```text
tests: 246/246
execution-head tests: 41
typed-policy tests: 44
failures/errors/skips: 0/0/0
tracked files: 33
tracked digest:
88338760CE2EC767D7F93279F4F3B82E916B0CBE4882257B8CF9133591EA8AE0
```

Both evidence files were 69,144 bytes with SHA-256 `A6285498FCFE767297D7156B87CA6034A993B2DFBB167EF7DFA813E9ADD55292`; direct byte equality passed. All official/helper/preflight/token/capture counters were zero. No preliminary complete runner was invoked.

## Required Amendment 5G-B Bindings

The future Request and Manifest must bind at least:

```text
5G-A.1 package:
d02b19dfd5a527d0159b930662f5a868c8235d35

5G-A.1 approval governance:
3d818cee86e1faca16c2bdab3baf4fd5411cff75

5G-A.1 implementation/evidence:
c21f3f58b2b1d4ccf235daba9c85937daedf4e3b

Hard Failure 9:
d1c7cf9d78563e30a1e0fe0d6812b36d15b95a9a

Hard Failure 8:
0f35ec895c756348e8a10803c6dd961a37344fb0

5F-B rebinding/governance:
052e8ecc04f566b75666d5cc96df74d2ed5061e4
```

It must also bind the four accepted hashes above. The future execution protocol must pre-freeze the only allowed post-approval rebinding/governance changed-path set, execution-HEAD direct-parent relation, required ancestors, governance-binding artifacts, unchanged 32-element capture command, helper hashes, one-time calls and no-automatic-retry rule.

## Permitted Future Request, Not Current Authorization

Amendment 5G-B may request this future sequence:

```text
package-bound approval governance
-> post-approval deterministic rebinding
-> governance binding
-> derived execution-HEAD validation
-> A/B/C/D formal preflight
-> one unchanged capture only if every prior gate passes
-> audit/push/stop
```

The 5G-B package itself cannot execute any step in that sequence.

## Current Boundary

Hard Failures 8 and 9 have confirmed direct causes. Hard Failure 4 diagnosis remains incomplete. Until a new package-bound 5G-B approval is granted, no real execution-head check, preflight, helper official-boundary call, official input access, token use, capture, controller, verifier or Gold action is allowed.
