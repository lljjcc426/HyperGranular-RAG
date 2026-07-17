# Stage4B-U1-D Pre-Gold Hard Failure 20 Review 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review date: 2026-07-17
- Independent review attachment bytes: 7,773
- Independent review attachment SHA-256: `114E48282272C7AC4C2AA7555149B44B0B6FE0A1D32D6AAF71A74D9700AF1BE6`
- Reviewed checkpoint: `d0dbc5533ddc464c7f7f1433d660ee7ddc355e07`
- Direct parent / consumed approval governance: `1eb73132d47d5b21fceca9c88a42607ee3dff98d`
- Corrected 1.1.6 package: `0efbea018f4ad0e8650e254d313fb9cc85d2a28c`
- Review decision: `ACCEPT_HARD_FAILURE_20_AUDIT`
- Recovery disposition: `RETURN_FOR_AMENDMENT_5G_B_1_1_1_1_7_COMMAND_LINE_ONLY_DURABLE_DIAGNOSTIC_PACKAGE`
- Other project conversations, project-external threads, and global memory used: No

## Accepted Audit Boundary

The independent review accepts the Hard Failure 20 checkpoint and confirms:

```text
approval governance valid
post-governance static gate 126/126
PRE observer processes 1
observer exit 1
failure at actual-command-line equality gate
capture host / adapter / parent / loader starts 0/0/0/0
target ScriptBlock invocations 0
all six new result paths absent
Hard Failure 19 raw unchanged
result commits / pushes 0/0
retry and post-failure diagnostic execution 0/0
```

The established failure is exactly:

```text
PRE_NESTED_OBSERVER_ACTUAL_PROCESS_COMMAND_LINE_MISMATCH
```

The actual characters, length, SHA-256, first differing code unit, common prefix/suffix, and difference category were not durably preserved. Executable quoting, path representation, argument escaping, PowerShell normalization, separator modeling, terminal-NUL modeling, package-source defect, and nested-transport defect remain unestablished.

## Evidence Stability

The four 1.1.6 nested raw paths and two semantics paths remain absent. The immutable Hard Failure 19 raw remains:

```text
path: results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_5_pre_capture_outer_observation.bin
bytes: 520
SHA-256: 4ABEB26000DDC77E8293DB1616682E6748E2290A9608959A2A040B1CD2780A70
```

The Hard Failure 20 observer exit and error remain `AUDIT_RECORDED / NOT_SEPARATELY_DURABLE_BYTE_EVIDENCE`. No post hoc command-line raw may be reconstructed or presented as evidence.

## Accepted Next-Package Boundary

The review returns the project only for a separately governed Amendment 5G-B.1.1.1.1.7 package. The package may freeze one command-line-only diagnostic observer and one new versioned binary observation path. It must not authorize or execute the nested PRE chain.

The intended future authorization is limited to:

```text
ONE_NEW_PACKAGE_BOUND_APPROVAL_GOVERNANCE_COMMIT
ONE_COMMAND_LINE_DIAGNOSTIC_OBSERVER_EXECUTION
ONE_COMMAND_LINE_OBSERVATION_RESULT
ZERO_CAPTURE_HOST_STARTS
IMMEDIATE_STOP_FOR_INDEPENDENT_REVIEW
```

Before the equality gate, the future observer must materialize and durably persist the UTF-16LE bytes for the actual `[Environment]::CommandLine`, the modeled command line, the registered executable, and the registered complete arguments. It must complete `CreateNew`, `Flush(true)`, and close before comparing. It must not construct or start the capture host.

## Independent Result Calculations

The later independent result review, not package assembly or the observer, must derive from raw bytes:

```text
actual and modeled character counts and SHA-256
first differing UTF-16 code-unit position
actual and modeled differing code units
common prefix and suffix lengths
whether the only raw difference is a terminal NUL
```

No difference type may be predicted in this package.

## Governance Decision

The 1.1.7 package must be the single direct child of `d0dbc5533ddc464c7f7f1433d660ee7ddc355e07`. The package itself does not authorize parsing or executing the new observer, reconstructing the actual command line, creating the observation, running the capture host, modifying the old raw, or entering the nested PRE chain.

The consumed 1.1.6 approval is non-reusable. POST, FINAL, TERMINAL, synthetic rebinding, formal preflight, official execution, Gold, reservation, and Stage3B remain unapproved.
