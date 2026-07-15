# Stage4B-U1-D Pre-Gold Amendment 5G-B Synthetic Rebinding Audit

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-15
- Package commit: `f281864b424c406b42718c4ec58d7266ecafd9a3`
- Approval-governance commit: `79e69eab874f669d79d433fa965f5f5f48659332`
- Status: `AMENDMENT_5G_B_POST_APPROVAL_SYNTHETIC_REBINDING_VERIFIED`
- Official execution: `NOT_STARTED`
- Other project conversations, thread tools, and global memory used: No

## Approval-Governance Gate

Approval governance was committed and pushed before any synthetic execution. The commit changed exactly:

```text
AGENTS.md
docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_APPROVAL_DECISION.md
```

After push, local HEAD, `origin/main` and GitHub `main` all equaled `79e69eab874f669d79d433fa965f5f5f48659332`, and the worktree was clean.

## Frozen Inputs

Before the first run, the frozen files matched:

```text
execution-head helper:
517C5C4DB22A82B4CBCA3D8BB751AAE60C0DCC5B5948CC8419D8770A9CC3D174

deterministic runner:
83816A962EDC8F06B53B5826E3F7519BD72D2CA0DF91C46751A9B12215867F28

execution-head tests:
EA39A9ECEBA36FE2BAA108B2C4B1C98981C8A5E3FE241F59F22F5D49458E02B8
```

The formal rebinding output did not exist. No official input metadata or content was accessed during these checks.

## Exact Two-Run Execution

One fail-closed wrapper invoked the frozen complete runner exactly twice. There was no preliminary complete run, targeted run, repair run, retry or third invocation.

Run 1 wrote a unique OS-temporary evidence file. Run 2 exclusively created:

```text
results/stage4b_u1_d_pregold_amendment_5g_b_synthetic_rebinding.json
```

Both runs used the same 33 tracked paths. The wrapper compared all tracked hashes before, between and after the two runs.

| Gate | Run 1 | Run 2 |
|---|---:|---:|
| tests | 246/246 | 246/246 |
| execution-head tests | 41 | 41 |
| typed-policy tests | 44 | 44 |
| failures/errors/skips | 0/0/0 | 0/0/0 |
| tracked files | 33 | 33 |
| tracked digest | `50D3BCDDAE42961ECCDDC30ADE683D6180F9CDFC319D085BEC762B8985A17041` | same |
| official access | 0 | 0 |
| typed-helper official invocation | 0 | 0 |
| path-helper official invocation | 0 | 0 |
| execution-head filesystem/Git/subprocess call | 0 | 0 |
| formal preflight | 0 | 0 |
| authorization token | 0 | 0 |
| official capture | 0 | 0 |

Evidence comparison:

```text
bytes: 69144
run 1 SHA-256:
00281BED7BC0DF10D47382CC47D0884BFCD331F0CB92EFC0B51F0FF176827A2A
run 2 SHA-256:
00281BED7BC0DF10D47382CC47D0884BFCD331F0CB92EFC0B51F0FF176827A2A
direct byte equality: true
tracked bytes unchanged: true
run-1 OS-temp evidence deleted after equality: true
```

The evidence schema remains the frozen 5G-A schema, so its internal status is `AMENDMENT_5G_A_SYNTHETICALLY_VERIFIED`. This audit and governance binding bind the same bytes to the approved 5G-B post-approval rebinding state.

## Governance Binding

`results/stage4b_u1_d_pregold_amendment_5g_b_governance_binding.json` binds:

- package and approval commits;
- all three required artifact-presence values;
- Request, Manifest, approval decision and final `AGENTS.md`;
- 5G-A.1 Review 1, request, Manifest, approval, implementation audit and deterministic evidence;
- the new 5G-B rebinding evidence.

The governance binding does not register its own SHA. The future direct-child execution commit is the external content binding.

## Boundary And Stop

No execution-head helper official call, formal preflight, official input access, token, capture, comparator, controller, verifier, evaluator/Gold, reservation or Stage3B action occurred. No code, test, prior evidence, official artifact or cache was modified or deleted.

The next and only allowed gate is to commit and push exactly this audit, the governance binding and the rebinding evidence as the direct child of approval commit `79e69eab874f669d79d433fa965f5f5f48659332`. Only after synchronization may one derived execution-HEAD validation run.
