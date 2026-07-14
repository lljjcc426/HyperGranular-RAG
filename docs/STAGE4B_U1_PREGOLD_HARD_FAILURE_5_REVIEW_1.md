# Stage4B-U1-D Pre-Gold Hard Failure 5 Review 1

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Review date: 2026-07-14
- Reviewed failure commit: `deccd203059d05dc27ba80aca1ddb1e2ea8f616f`
- Review source: current HyperGranular-RAG project conversation
- Other project conversations, thread tools, and global memory used: No

## Decision

```text
RETURN_FOR_REFERENCE_DECISIONS_SCHEMA_DIAGNOSTIC_AMENDMENT_PACKAGE
SCHEMA_DIAGNOSTIC_NOT_APPROVED
COMPARATOR_CHANGE_NOT_APPROVED
OFFICIAL_CAPTURE_RETRY_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

The current official state remains:

```text
AMENDMENT_5B_V2_OFFICIAL_DIAGNOSTIC_STOPPED_HARD_FAILURE_5
OFFICIAL_DIAGNOSIS_INCOMPLETE
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```

## Established Failure Boundary

- Both approved post-governance rebinding runs passed 107/107 with zero failures, errors, skips, or official-path access attempts and byte-identical complete evidence.
- The only approved read-only preflight passed.
- The only approved capture was consumed and stopped while the strict comparator loaded the frozen v2.2 reference decisions.
- The observed error was `Incomparable heterogeneous decisions schema at line 2`.
- No byte, canonical, field-value, float, or decision-semantic comparison completed.
- Temporary decisions were cleaned; machine and narrative diagnostic audits were not created; all five formal outputs remained absent.
- The three channel hashes, cache SHA/bytes, and reference-decisions SHA remained frozen.
- Raw byte equivalence and comparator behavior were not changed.

These facts establish a strict parser/comparator stop boundary only. They do not identify which fields or JSON types differ inside the reference file and do not justify normalization, comparator relaxation, capture retry, or controller rerun.

## Required Two-Level Amendment

### Amendment 5C-A

The first package may request only implementation and synthetic verification of an independent read-only JSONL schema-inventory tool. It must not call or modify `compare_decisions_files`, must not modify the existing comparator or capture, and must not read any official file.

Synthetic fixtures must cover homogeneous schemas, field-set differences, field-order differences, JSON-type differences, nested-structure differences, duplicate keys, invalid JSON, non-finite floats, deterministic output, no-value leakage, official-path blocking, and cleanup after failure.

### Amendment 5C-B

Only after 5C-A implementation and deterministic synthetic evidence are committed and pushed may a separate package request one official schema-only scan of:

```text
E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_decisions.jsonl
SHA-256: 6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7
```

Any future 5C-B output must be aggregate schema metadata only: total rows, distinct signatures, per-signature counts and first/last line numbers, field-name/type signatures, differences from a deterministically selected main schema, and pre/post SHA equality. It must contain no raw query ID, salted query-ID hash, row, field value, float value, question/text, ranking, policy, Gold, or generated decision.

Even a completed 5C-B scan would not authorize comparator changes, normalization, capture retry, controller rerun, verifier, or Gold.

## Current Permitted Action

The only permitted action is creation and push of the Amendment 5C-A approval request and machine-readable Manifest. That package is governance material only and does not authorize implementation, synthetic execution, official reference access, or any resumed Stage4B command.
