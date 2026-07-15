# Stage4B-U1-D Pre-Gold Amendment 5G-B.1 Package Review 1

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Review date: 2026-07-15
- Reviewed package commit: `9536ffb4ce845aeff9db3552f890612ca6e9e2a3`
- Review status: `REJECT_AMENDMENT_5G_B_1_PACKAGE_AS_CURRENTLY_WRITTEN`
- Required next action: `RETURN_FOR_CORRECTED_AMENDMENT_5G_B_1_PACKAGE`
- Official execution authorized: No
- Other project conversations, thread tools, and global memory used: No

## Accepted Scope

The reviewed package changed exactly seven governance/documentation paths relative to Hard Failure 10 checkpoint `aab591b92804fd1226a62751c38d056918f71b41`. It did not change scripts, tests, `results/`, official artifacts, historical failure records, data, cache, model, parameters or stop rules, and it deleted no file.

The following future boundaries remain acceptable:

- approval governance changes exactly `AGENTS.md` and the 5G-B.1 approval decision;
- exactly one validator-semantics gate before synthetic execution;
- exactly two fresh complete `246/246` rebinding runs;
- exactly three fresh `5g_b_1` artifacts;
- exactly one real precommit validation;
- exactly one three-path direct-child commit followed by immediate stop;
- no execution-HEAD, formal preflight, official input, token, capture, controller, verifier or Gold access.

## Blocking Findings

The package commit is not approvable because its validator contract has three fail-closed gaps:

1. `Sort-Object -Unique` and `Compare-Object` were not case-sensitive, so case-only key drift could be accepted.
2. The validator inspected `PSObject.Properties` only after `ConvertFrom-Json`; duplicate raw JSON keys could already have been collapsed.
3. Only a key-set fragment was frozen; the complete real precommit validator command and its bytes/SHA were not frozen.

## Required Correction

The corrected package must retain the 5G-B.1 name but supersede `9536ffb4ce845aeff9db3552f890612ca6e9e2a3` as an approvable package. It must freeze:

- `Sort-Object -CaseSensitive -Unique`;
- `Compare-Object -CaseSensitive`;
- case-only actual and expected collision fixtures;
- raw JSON duplicate-key rejection before object materialization;
- raw JSON case-only collision rejection;
- the complete real precommit validator source as Manifest bytes and SHA-256.

## Current State

```text
AMENDMENT_5G_B_1_PACKAGE_REJECTED_FOR_VALIDATOR_GAPS
RETURN_FOR_CORRECTED_AMENDMENT_5G_B_1_PACKAGE

VALIDATOR_SEMANTICS_CHECK_NOT_APPROVED
FRESH_SYNTHETIC_REBINDING_NOT_APPROVED
FRESH_THREE_PATH_DIRECT_CHILD_NOT_APPROVED
DERIVED_EXECUTION_HEAD_VALIDATION_NOT_APPROVED
FORMAL_PREFLIGHT_NOT_APPROVED
OFFICIAL_INPUT_ACCESS_NOT_APPROVED
AUTHORIZATION_TOKEN_USE_NOT_APPROVED
OFFICIAL_CAPTURE_NOT_APPROVED
CONTROLLER_RERUN_NOT_APPROVED
VERIFIER_NOT_APPROVED
GOLD_NOT_APPROVED
```
