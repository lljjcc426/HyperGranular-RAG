# Stage4B-U1-D Pre-Gold Amendment 5A Implementation Audit

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-13
- Approval package: `81d8c34f1cf2539a4c0b81c6148047bc666e2f82`
- Approval governance: `a0bf91b3a34daaf5b1ee50700d8356e1383e9a9c`
- Diagnostic checkpoint: `stage4b_u1_decisions_diag_v1`
- Controller checkpoint: `stage4b_u1_v2_3_1` (unchanged)
- Official diagnosis executed: No
- Other project conversations, thread tools, and global memory used: No

## Scope Audit

Amendment 5A added a decisions-only JSONL comparator, a synthetic capture path that writes decisions only inside a managed temporary directory, a deterministic synthetic verification runner, and 48 diagnostic hardening tests. `scripts/stage4b_u1_goldfree_controller.py` was not modified. No retrieval, controller, evaluator, model, score, ECDF, budget, trigger, ranking, policy, endpoint, or byte-equivalence rule changed.

The comparator keeps raw byte equality as the controlling equivalence result. Canonical and semantic comparisons are diagnostic layers only. It rejects invalid JSON, duplicate object keys, missing or duplicate query IDs, non-finite values, unsupported value types, and heterogeneous within-file schemas. The CLI exits nonzero and does not create an output report for an incomparable input schema.

The capture reuses the existing controller input validator and existing-cache-only loader but does not call the full controller. Synthetic paths are constrained to an explicit temporary-root allowlist. Official mode remains locked unless a future Amendment 5B authorization token is supplied. Even with that token, exact registered input/output paths, the OS temp parent, an absent audit output, the frozen v2.2 decisions SHA, the registered channel source-audit digest, and the cache post-computation fingerprint must pass. The diagnostic validator does not open the Stage4A-R2 source-audit file. Tests patch the full controller and file access, while the complete runner installs a process-wide audit hook over the registered official paths.

After implementation/evidence commit `739c14a51475190948e511eee00804b490d94aab` was pushed, static 5B package assembly found that the first capture version passed `source_audit_path=None` to the official controller channel validator. That would have made a future authorized diagnostic fail before comparison. Before creating any 5B package or reading any official input, the independent capture module was hardened with a diagnostic-specific registered-digest validator and exact-path gates. Four synthetic tests were added, and the complete deterministic evidence was regenerated twice. Commit `739c14a...` remains in history as the transparently superseded intermediate implementation.

## Binary64 ULP Rule

The platform-independent mapping is frozen as follows:

```text
bits(x) = unpack_big_endian_uint64(pack_big_endian_binary64(x))

key(x) =
  (~bits(x)) & ((1 << 64) - 1),  when the sign bit is 1
  bits(x) | (1 << 63),           when the sign bit is 0

ulp_distance(a, b) = abs(key(a) - key(b))
```

This explicitly uses IEEE-754 binary64 with big-endian byte order, orders negative values below nonnegative values, distinguishes `-0.0` from `+0.0`, and yields a signed-zero distance of one. `bool`, `int`, and `float` remain distinct types.

## Synthetic Verification

The first targeted development run executed 43 new tests and reported one error plus one failure. The error came from a test fixture that serialized indented multi-line JSON into a JSONL file; it was corrected to a single-line whitespace-only difference. The failure came from a reference fixture that bypassed the existing cache loader's normalization step; it was corrected to apply the same `normalize_matrix` path. No official input was accessed. The corrected 43-test run passed, the incomparable-schema hardening increased the new suite to 44 tests, and the pre-5B exact-path/source-digest/cache-fingerprint hardening increased it to 48 tests.

Final checks on unchanged implementation bytes were:

| Check | Result |
|---|---|
| Python compilation | pass |
| Original Stage4B-U1 suite | 50/50 pass |
| New Amendment 5A suite | 48/48 pass |
| Complete discovery | 98/98 pass, 0 failure, 0 error, 0 skip |
| Deterministic evidence run 1 | pass |
| Deterministic evidence run 2 | pass, byte-identical to run 1 |
| Evidence bytes | `16389` |
| Evidence SHA-256 | `3D44C14B82E911DDD37501731772A7594D7616BF12FE278D2D4CCC103533057E` |
| Official path blocked/attempted accesses | `0` |

The local Python environment emitted the existing optional-dependency warning that a NumPy 1.x-built `numexpr` module is incompatible with NumPy 2.4.6, ending in the captured text `AttributeError: _ARRAY_API not found`. The warning arose through the pre-existing transformers/sklearn/pandas import chain. Every listed test command exited zero, and both complete evidence files remained byte-identical.

## Bound File Hashes

| File | SHA-256 |
|---|---|
| `AGENTS.md` | `BF7F2DE2CCCA5DD05610548F0E2CE2FF3BDB9B6EB7EFD4F112DBD6C4FFBD41B0` |
| `docs/STAGE4B_U1_PREGOLD_HARD_FAILURE_4.md` | `2F53A1ED1AEC248413EDE36808DD1E171A75769C8504C23E7E75B329CC04BDE8` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_DECISIONS_DIAGNOSTIC_DRAFT.md` | `3918595593E4B265DF2E9EDD634D6DCBC68B52B7FF99EF37089C4E6DA2FB6A01` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_APPROVAL_REQUEST.md` | `003147A4C5DE08644F03A32F789F39DEFBFD1C475EC096669754598843016835` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_MANIFEST.json` | `EA8288B97285072C7792228F43D0D1D20975E5D31DA9E43651CABDB3F2F9217D` |
| `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5A_APPROVAL_DECISION.md` | `6E640F08505499AC05777AD042DB6807D55656D4222242B5C5D1180D6E76B2C4` |
| `scripts/stage4b_u1_common.py` | `CDF7EAD6007DABE389ED0BD18983496F75290C32243FE6DF84716810CDE92CE4` |
| `scripts/stage4b_u1_goldfree_retrieval.py` | `3B50FAFD057E2565167ED09288D61829B3FBD044991F139F734F819955038A3B` |
| `scripts/stage4b_u1_goldfree_controller.py` | `C18AD3B672649BA846C5E191D0DBBAC7644A926D4B8CCD39176127175BBA7C1F` |
| `scripts/stage4b_u1_compare_decisions.py` | `FF4D623DF86FE42EB4ACDFF9D3321FCA768E03B64597C6CC88931359CEDB2DD4` |
| `scripts/stage4b_u1_capture_diagnostic_decisions.py` | `1D30E8129C9E9E228EE8E1BB2C21A2E8D196C0F5B91D16E9E8061AD7B1DA0EFC` |
| `scripts/stage4b_u1_run_decisions_diagnostic_synthetic_verification.py` | `03C29EABAEB5D57CEF6D1A6B13235475FC0CCCCFC65E13A118BCD44EB60D57C4` |
| `tests/test_stage4b_u1_goldfree.py` | `CA61B466C7DDF583D827FD2D99C024D646BA3962C80B9137D480C84DEA374C71` |
| `tests/test_stage4b_u1_decisions_diagnostic.py` | `1105016D8128615D0DA1B9612D5CAD3FCB2B796A3B8424D27B46BDD83C1CB7D4` |
| `results/stage4b_u1_d_pregold_amendment_5a_synthetic_verification.json` | `3D44C14B82E911DDD37501731772A7594D7616BF12FE278D2D4CCC103533057E` |

## Boundary And Status

The evidence records no access to official units, queries, source audit, fresh or legacy cache, official decisions, official rankings, policy, Gold, reservation, or Stage3B. It did not run an official comparator, diagnostic capture, controller, verifier, or evaluator. No file was deleted.

```text
AMENDMENT_5A_SYNTHETICALLY_VERIFIED
OFFICIAL_DIAGNOSIS_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
```

The only next permitted step is to create and push an implementation-bound Amendment 5B approval request and Manifest, then stop.
