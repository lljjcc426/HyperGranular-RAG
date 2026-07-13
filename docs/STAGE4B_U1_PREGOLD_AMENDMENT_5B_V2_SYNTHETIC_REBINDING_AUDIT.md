# Stage4B-U1-D Pre-Gold Amendment 5B v2 Synthetic Rebinding Audit

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Mode: `run / reproducibility verification`
- Audit date: 2026-07-14
- Approval package: `f43e22ef079701139d4437849be8ad57654f80d7`
- Approval governance: `2ddf6e044c27e47385a558bdaca80cb6c31c4ffe`
- Implementation/evidence: `e566eb861ec6028ca89a40c9aca7d06737f1eb8e`
- Official preflight executed: No
- Official capture executed: No
- Other project conversations, thread tools, and global memory used: No

## Command

The following command ran exactly twice against unchanged approved governance and implementation bytes:

```powershell
python scripts\stage4b_u1_run_decisions_diagnostic_synthetic_verification.py --output results\stage4b_u1_d_pregold_amendment_5b_v2_synthetic_rebinding.json
```

The first run was required to succeed before the second invocation. No failed run or retry occurred.

## Results

| Gate | Run 1 | Run 2 |
|---|---:|---:|
| tests | 107/107 | 107/107 |
| failures | 0 | 0 |
| errors | 0 | 0 |
| skipped | 0 | 0 |
| official-path access attempts | 0 | 0 |
| evidence bytes | 20,495 | 20,495 |
| evidence SHA-256 | `7D9C3527480ECDFFA87C943589538BCEFEFA3610A6D415719429CDE5D222D12E` | `7D9C3527480ECDFFA87C943589538BCEFEFA3610A6D415719429CDE5D222D12E` |

Direct full-byte comparison: `True`.

The existing optional import chain emitted the known NumPy 2.4.6/`numexpr` ABI warning in both runs. Both commands exited zero and produced byte-identical complete evidence.

## Governance Binding

`results/stage4b_u1_d_pregold_amendment_5b_v2_governance_binding.json` binds:

| Material | SHA-256 or commit |
|---|---|
| 5B v2 request | `4BD6BA49AAC4DB7A1C38356FAF1936639C5CF6D2BFCDC7E206CBC3BA37158D14` |
| 5B v2 Manifest | `96989FB3A585E5FA6229958C3A34D6E0ED58D9595E5DF30327C5419C367CB592` |
| approval decision | `EE91A6B0F1D66A1F487D54DE8BF5C907D70811C0619463EC6F2EE291B631D8B8` |
| final approved `AGENTS.md` | `FC77EF6C76EDC19F06E55C9D7E32CDAD81C98A53D8083B5458BD3CCA6EF45853` |
| implementation/evidence | `e566eb861ec6028ca89a40c9aca7d06737f1eb8e` |
| rebinding evidence | `7D9C3527480ECDFFA87C943589538BCEFEFA3610A6D415719429CDE5D222D12E` |

All implementation hashes remain equal to the approved v2 Manifest. No code changed after the package commit.

## Boundary Verification

- Official input opened: No.
- Official path access attempts: 0 in each run.
- Capture authorization token passed: No.
- Controller/verifier/evaluator run: No.
- Gold/reservation/Stage3B accessed: No.
- Cache or official artifact created, changed, deleted, or migrated: No.

## Next Gate

After this evidence, governance binding, and audit are committed and pushed to GitHub, exactly one read-only preflight is authorized. Official capture remains prohibited unless that preflight passes every registered gate.
