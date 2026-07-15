# Stage4B-U1-D Pre-Gold Amendment 5G-B Official Diagnostic Approval Request

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Request date: 2026-07-15
- Request ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_DERIVED_EXECUTION_HEAD_BOUND_SINGLE_PREFLIGHT_AND_OFFICIAL_DECISIONS_ONLY_DIAGNOSTIC`
- Manifest: `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_MANIFEST.json`
- Current state: `AMENDMENT_5G_A_1_IMPLEMENTATION_AND_EVIDENCE_ACCEPTED`
- Package state: `AWAITING_AMENDMENT_5G_B_APPROVAL`
- Package assembly authorization: `AUTHORIZED_BY_5G_A_1_REVIEW_1`
- Package itself authorizes any execution: No
- Other project conversations, thread tools, and global memory used: No

## Binding History

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

5F-B approval governance:
84d39707dee15729dc0c35c85a16f4e31dac89e4

5F-B package:
f33ee70233ea4098b2d7a17cfde3d266081ee693

Hard Failure 4:
b21852a174b537c90a848699deb4d26d6f169506

v2.3.1 implementation:
34349c70ee24b8240fd169393134d4280968b790
```

Any approval must explicitly bind the future package commit containing this request and its Manifest. An approval that omits that package commit is invalid.

## Accepted 5G-A.1 Checkpoint

Independent review accepts commit `c21f3f58b2b1d4ccf235daba9c85937daedf4e3b` and the following frozen files:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `scripts/stage4b_u1_preflight_execution_head_binding.py` | 6,318 | `517C5C4DB22A82B4CBCA3D8BB751AAE60C0DCC5B5948CC8419D8770A9CC3D174` |
| `scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py` | 22,416 | `83816A962EDC8F06B53B5826E3F7519BD72D2CA0DF91C46751A9B12215867F28` |
| `tests/test_stage4b_u1_preflight_execution_head_binding.py` | 11,580 | `EA39A9ECEBA36FE2BAA108B2C4B1C98981C8A5E3FE241F59F22F5D49458E02B8` |
| `results/stage4b_u1_d_pregold_amendment_5g_a_synthetic_verification.json` | 69,144 | `A6285498FCFE767297D7156B87CA6034A993B2DFBB167EF7DFA813E9ADD55292` |

The accepted evidence records 246/246 tests, 41 execution-head tests, 44 typed-policy tests, zero failure/error/skip, 33 tracked files, tracked digest `88338760CE2EC767D7F93279F4F3B82E916B0CBE4882257B8CF9133591EA8AE0`, and zero official/helper/preflight/token/capture action. Hard Failure 4 remains undiagnosed.

## Requested Future Authorization

This package requests a new, separately approved execution sequence. It does not authorize that sequence by being committed or pushed.

### 1. Package-Bound Approval Governance

Create and push exactly one approval-governance commit whose only changed paths are:

```text
AGENTS.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_APPROVAL_DECISION.md
```

The decision must bind the final 5G-B package commit, all historical commits above, and this Manifest. No rebinding, helper call, preflight, official input access, token or capture may occur before that push is confirmed.

### 2. Post-Approval Deterministic Rebinding

On the final approval-governance bytes, invoke the frozen complete synthetic runner exactly twice. No preliminary complete run, targeted run, repair or retry is requested.

Each run must satisfy exactly:

```text
tests: 246/246
execution-head tests: 41
typed-policy tests: 44
failures/errors/skips: 0/0/0
tracked files: 33
official access: 0
typed-helper official invocation: 0
path-helper official invocation: 0
execution-head filesystem/Git/subprocess call: 0
formal preflight invocation: 0
authorization token use: 0
official capture invocation: 0
```

The two complete evidence files must be byte-identical. Run 1 must use a unique OS-temporary evidence path and may be deleted only after both runs and direct byte comparison pass. Run 2 must exclusively create:

```text
results/stage4b_u1_d_pregold_amendment_5g_b_synthetic_rebinding.json
```

The future governance binding and narrative audit must be created before one rebinding/governance commit. That commit must be the direct child of the approval-governance commit and must change exactly these three paths:

```text
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_SYNTHETIC_REBINDING_AUDIT.md
results/stage4b_u1_d_pregold_amendment_5g_b_governance_binding.json
results/stage4b_u1_d_pregold_amendment_5g_b_synthetic_rebinding.json
```

No status document, code, test, prior evidence or experiment artifact may be included in that direct-child commit. After it is pushed, its actual synchronized commit is the candidate execution HEAD; no future execution-HEAD literal may be manually pre-transcribed.

### 3. Derived Execution-HEAD Validation

Before formal preflight, independently collect the current local HEAD, `origin/main`, GitHub `main`, direct parent, changed paths, required ancestors, clean-worktree fact and governance-binding JSON. Hash-verify the execution-head helper before import and call `validate_execution_head_binding(...)` exactly once.

The call must use:

- the actual three independently obtained HEAD values;
- the actual direct parent;
- the exact three-path allowed set frozen in the Manifest;
- every required known ancestor plus the future package and approval commits;
- the hash-bound governance binding with package/approval commits and all three required artifacts present;
- no pre-transcribed expected execution HEAD.

It must return `VALIDATED_EXECUTION_HEAD_BINDING`, three-way equality, direct-parent verification, exact changed-path verification, required ancestry, three required artifacts and clean worktree. Failure consumes the one invocation and stops without formal preflight or retry.

### 4. One A/B/C/D Formal Preflight

Only after derived execution-HEAD validation passes may one formal preflight begin.

#### A. Git, governance, hashes and output absence

- re-confirm local/origin/GitHub equality and clean worktree without a handwritten expected HEAD;
- verify package, approval, accepted implementation/evidence and rebinding/governance ancestry;
- verify the 5G-A.1 evidence bytes/SHA;
- verify historical `AGENTS.md` from Git blob at `c21f3f5...` against the evidence-recorded SHA;
- verify the other 32 current tracked paths against accepted 5G-A.1 evidence;
- verify all 33 current post-approval hashes against the new rebinding evidence;
- verify request, Manifest, approval decision, final `AGENTS.md`, review, implementation audit and both evidence files through governance binding;
- verify execution-head, typed-policy, path-equivalence, capture, comparator, runner and test bytes/SHA;
- verify machine/narrative audit, five formal outputs and OS-temp diagnostic residue are absent.

Gate A must not access official input metadata or content.

#### B. Typed capture-argument policy helper

Hash-verify and directly call the frozen typed helper once on the 5G-B exact command and the independently hash-bound 5F-B exact command. Require exact 32-element equality, 15 flags, seven path roles and zero prohibited roles. No inline implementation, fallback or substring policy is allowed.

#### C. Windows path-equivalence helper

Only after B passes, hash-verify and directly call the frozen path helper once on the raw `.NET System.IO.Path.GetTempPath()` result and exact expected directory `C:\Users\cc\AppData\Local\Temp`. Do not trim, normalize, replace or rewrite either value.

#### D. Five official inputs

Only after A, B and C pass may the preflight inspect the five Manifest-registered official inputs: units, queries, controller channel audit, ID-bound embedding cache and v2.2 reference decisions. Verify path, regular-file status, SHA and every registered boundary/cache property. Do not open source audit, rankings, reference policy, 5C-B inventory, evaluator/Gold, reservation or Stage3B.

### 5. Conditional Single Unchanged Capture

Only if derived execution-HEAD validation and every A/B/C/D gate pass may the unchanged 32-element exact command run once. It must use the frozen token string and existing decisions-only capture. It may create only the existing aggregate machine-audit path; no formal decisions, rankings, policy, controller audit or `VERIFIED_PRE_GOLD` may be created or promoted.

Raw byte equality remains the controlling gate. Canonical or semantic equality may explain a difference but cannot replace raw equality. No code, schema normalization, model, parameter, endpoint, equivalence or stop-rule change is requested.

After capture, verify aggregate-only output, input/cache pre/post fingerprints, temporary cleanup, no prohibited content and continued formal-output absence. Write one narrative audit, commit/push the machine and narrative audits, confirm GitHub, and stop.

## Exact One-Time Limits

```text
post-approval complete synthetic runs: 2
derived execution-head helper official-boundary calls: 1
formal preflight invocations: 1
typed-helper official-boundary calls: 1
path-helper official-boundary calls: 1
official capture invocations: 1
automatic retry: false
```

Any hard-gate failure immediately stops execution. No failed stage may be retried under the same approval.

## Explicitly Not Authorized By This Package

- any approval-governance write before package-bound approval;
- post-approval rebinding or governance binding now;
- real Git/GitHub execution-head helper validation now;
- formal preflight or helper official-boundary call now;
- official input metadata/content access now;
- authorization token use or capture now;
- code, test, data, model, parameter, cache, equivalence or stop-rule change;
- full controller, verifier, evaluator/Gold or formal-output promotion;
- rankings, reference policy, source-audit file, 5C-B inventory, reservation or Stage3B access;
- modification, deletion, overwrite or migration of cache, official artifacts, historical evidence or failure records;
- automatic recovery or continuation after diagnosis.

## Requested Success State

```text
AMENDMENT_5G_B_OFFICIAL_DECISIONS_DIAGNOSTIC_COMPLETE_AWAITING_REVIEW
HARD_FAILURE_4_DIAGNOSIS_COMPLETE_AWAITING_REVIEW

CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
