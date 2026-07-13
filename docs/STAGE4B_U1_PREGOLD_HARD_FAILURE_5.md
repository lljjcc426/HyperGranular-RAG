# Stage4B-U1-D Pre-Gold Hard Failure 5

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Audit date: 2026-07-14
- Failure code: `HARD_FAILURE_5_INCOMPARABLE_HETEROGENEOUS_REFERENCE_DECISIONS_SCHEMA`
- 5B v2 package: `f43e22ef079701139d4437849be8ad57654f80d7`
- Approval governance: `2ddf6e044c27e47385a558bdaca80cb6c31c4ffe`
- Rebinding/governance evidence: `4c10ad942a75af42b910b860fd4897b672160d5d`
- Capture execution HEAD: `4c10ad942a75af42b910b860fd4897b672160d5d`
- Capture execution count: 1
- Capture retry count: 0
- Controller rerun: No
- Verifier/evaluator/Gold: Not accessed
- Other project conversations, thread tools, and global memory used: No

## State Before Capture

The approved governance and two complete 107-test post-approval rebinding runs were committed and pushed before official access. Both rebinding runs passed 107/107 with zero failures/errors/skips and zero official-path access attempts; both outputs were 20,495 bytes with SHA-256 `7D9C3527480ECDFFA87C943589538BCEFEFA3610A6D415719429CDE5D222D12E`.

The only read-only preflight then ran once and passed:

- clean synchronized GitHub HEAD and all required commit ancestry;
- governance binding and eight implementation hashes;
- three channel regular-file paths and external SHA-256 values;
- cache SHA-256 `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D` and 210,714,667 bytes;
- v2.2 reference decisions SHA-256 `6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7`;
- 143,820 units, 4,500 queries, both frozen ID digests, namespace relation, candidate counts, channel audit, registered source-audit digest, and frozen encoder configuration;
- absence of machine/narrative audit and all five formal outputs.

The preflight did not open or hash rankings, did not open reference policy or the Stage4A-R2 source-audit file, and did not access Gold, reservation, or Stage3B.

## Single Capture Command

The exact command registered in `docs/STAGE4B_U1_PREGOLD_AMENDMENT_5B_V2_OFFICIAL_DIAGNOSTIC_APPROVAL_REQUEST.md` ran once with all three external channel expected-SHA arguments, the frozen cache SHA, exact paths/configuration, and the approved token. No argument was added, omitted, or changed.

## Observed Failure

The capture passed its input-path/token/configuration gates, three channel pre-hash gates, semantic channel validation, require-existing cache validation, decisions computation, and cache post-computation fingerprint. It wrote pending decisions only in an OS temporary directory and then invoked the decisions-only comparator.

The comparator raised while loading the left/frozen v2.2 reference decisions:

```text
stage4b_u1_compare_decisions.DecisionsDiagnosticError:
Incomparable heterogeneous decisions schema at line 2
```

Trace boundary:

```text
run_diagnostic_capture
  -> compare_decisions_files(reference_decisions_path, captured_path)
  -> load_decisions_jsonl(left_path)
  -> DecisionsDiagnosticError at line 2
```

No row content, raw query ID, question/text, ranking, policy, or Gold content was emitted or inspected for this audit. The observed exception establishes only that the current strict comparator rejected within-file schema heterogeneity at line 2 of the frozen reference file. It does not establish the fields involved or whether the unobserved decision values would otherwise be byte-, canonical-, or semantically equivalent.

## Output And Cleanup Boundary

The exception occurred before comparison completed and before the post-computation channel recheck/audit exclusive-create block. Python's `TemporaryDirectory` cleanup ran during exception unwinding.

Independent read-only post-failure checks confirmed:

| Check | Result |
|---|---|
| temporary `stage4b_u1_decisions_diag_*` entries | 0 |
| machine diagnostic audit exists | No |
| narrative diagnostic audit exists | No |
| formal v2.3.1 outputs exist | 0 of 5 |
| units SHA-256 | `114D28A7C9842079BF80C292274D7DBBBC718F05CBE8F4435487C245238427FA` |
| queries SHA-256 | `6EE942C680EAC86D0410FC25BCC302CA7312A0E253E318025A957D51A09B4B6B` |
| controller channel-audit SHA-256 | `D134CDE168C833784F238B61420B4738C1F65B9FCA995945EB04E8B99EAAB2FA` |
| cache SHA-256 | `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D` |
| cache bytes | 210,714,667 |
| v2.2 reference decisions SHA-256 | `6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7` |

No cache, official input, failure artifact, or prior result was created, overwritten, deleted, or migrated.

## Scientific Boundary

This failed execution produced no aggregate diagnostic report. It therefore cannot answer whether Hard Failure 4 was caused by serialization, row order, schema, discrete values, floating-point values, or decision semantics. The only supported finding is the comparator hard failure above.

The existing raw byte-equivalence gate remains unchanged. No comparator, normalization, controller, model, parameter, retrieval, ranking, evaluator, or stop-rule change was made.

## Stop State

```text
AMENDMENT_5B_V2_OFFICIAL_DIAGNOSTIC_STOPPED_HARD_FAILURE_5
OFFICIAL_DIAGNOSIS_INCOMPLETE
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

The approved capture count is exhausted. No retry is permitted. Any next action that reads the frozen reference decisions for schema-only diagnosis, changes comparator acceptance, normalizes records, or reruns capture/controller requires a new package-bound Amendment and independent approval.
