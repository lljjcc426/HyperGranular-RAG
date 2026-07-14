# Stage4B-U1-D Pre-Gold Amendment 5D-B Post-Approval Synthetic Rebinding Audit

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-14
- Package commit: `f67061e753b03a5cf46d7a7c92b5a95fc79b0ef8`
- Implementation/evidence commit: `02f46447e4cd69a15d2af14ee1fc62f9eb4f8bb9`
- Final approval-governance HEAD: `1c46dc1b69f8381598aacb9f3b1e27561c7f9ee2`
- Status: `POST_APPROVAL_SYNTHETIC_REBINDING_VERIFIED`
- Official preflight/capture: `NOT_RUN`
- Other project conversations, thread tools, and global memory used: No

## Governance Sequence

The 5D-B package was already synchronized at `f67061e753b03a5cf46d7a7c92b5a95fc79b0ef8`. The approval decision and final approved `AGENTS.md` were committed before any rebinding command. The approval-governance sequence is:

```text
b4dec0bade12f16e6a13e3245bd67ce53496e2a2  approval decision and AGENTS
1c46dc1b69f8381598aacb9f3b1e27561c7f9ee2  remove one trailing blank line from the decision
```

The second commit only normalized the decision file's final newline area before push. It did not modify `AGENTS.md`, implementation, tests, data, parameters, or evidence. Final approval governance was pushed and `HEAD == origin/main` before rebinding.

## Frozen Command And Results

The exact approved command ran twice:

```powershell
python scripts\stage4b_u1_run_decisions_diagnostic_synthetic_verification.py `
  --output results\stage4b_u1_d_pregold_amendment_5d_b_synthetic_rebinding.json
```

Both invocations exited zero. Each complete evidence reported:

```text
tests_run = 143
failures = 0
errors = 0
skipped = 0
official_path_access_guard.blocked_or_attempted_access_count = 0
diagnostic_checkpoint = stage4b_u1_decisions_diag_v2
official_capture_executed = false
official_comparator_executed = false
controller_rerun = false
verifier_executed = false
gold_accessed = false
reservation_accessed = false
stage3b_accessed = false
```

Each evidence stream was 29,643 bytes with SHA-256 `264200C2EBEDA1D0B214F824B77C89FC5BBE82D3BE0836FAAB9486EACAACF368`. A direct byte-array comparison returned true.

The unchanged legacy import chain emitted the known NumPy 2.4.6 versus old `numexpr` ABI warning and traceback text on stderr during both runs. This was not a test failure: both processes exited zero and both complete evidence outputs met every approved hard gate. No command was retried.

The first evidence stream was preserved temporarily only for direct comparison at `C:\Users\cc\AppData\Local\Temp\stage4b_u1_5d_b_rebinding_run1_1c46dc1.json`. After byte equality was established, that temporary copy was deleted. The tracked final evidence remains unchanged.

## Governance Binding

`results/stage4b_u1_d_pregold_amendment_5d_b_governance_binding.json` binds the following final bytes:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| 5D-B request | 14,873 | `655AB508B4D5D838E781DCD3A88A68A345111E189F2F8A4EA0FDAA74D22F92B6` |
| 5D-B Manifest | 15,577 | `AB0FBD463B1E10F141F8E18B981F1E1B2E7740B230EE3DBAAAC96AEF6CC12F16` |
| 5D-B approval decision | 10,136 | `424587F6DE4112AE8A1D009DC84A1D0B4A3A7EAB99696B15585D2F5DEE2B7CFB` |
| Final approved `AGENTS.md` | 21,553 | `95BD32C540D63DF4CB79C624F0C38D59658FE4D36325E28DDCBD27E865537AEE` |
| 5D-A implementation audit | 7,959 | `D5468E8D57C0E52361D52B0EB7BF54C87DA91D453A2FACBE2AEA57F766CE3794` |
| 5D-A evidence | 29,643 | `08695B4305D9919049DFE86870772B9E9F66751DA6D2FF4D43CEF2A912A62008` |
| 5D-B rebinding evidence | 29,643 | `264200C2EBEDA1D0B214F824B77C89FC5BBE82D3BE0836FAAB9486EACAACF368` |

The governance binding also records that the approval token has not been consumed under 5D-B and that no formal preflight or official capture has run.

## Access Boundary

No official units, queries, channel audit, cache, reference decisions, source audit, 5C-B machine inventory, rankings, policy, evaluator/Gold, reservation, or Stage3B path was opened during post-approval rebinding. Synthetic fixture tests ran only under their registered temporary test roots.

No implementation, comparator semantics, controller logic, model, parameter, cache, official artifact, prior failure record, or historical evidence was modified or deleted.

## Next Hard Gate

The next and only authorized action after this audit and its machine binding are committed and pushed is one read-only formal preflight. Official capture remains prohibited unless that single preflight passes every registered gate.

Current state:

```text
AMENDMENT_5D_B_APPROVED_REBINDING_VERIFIED_PREFLIGHT_PENDING
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
