# Stage4B-U1-D Pre-Gold Hard Failure 16 Review 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review date: 2026-07-15
- Hard Failure 16 checkpoint: f28fc526faf74f80fdefb96ca189769dbcf1e5e4
- Approved package: 945f655b95cfee9e55ad2d20e7bd5018f9aee1e2
- Approval governance: 72783071c17f6e3cab347823a8da080171c1a883
- Decision: ACCEPT_HARD_FAILURE_16_AUDIT
- Recovery: RETURN_FOR_AMENDMENT_5G_B_1_1_1_1_3_BOUNDED_STDIN_SOURCE_TRANSPORT_RECOVERY_PACKAGE
- Execution authorized: No
- Other project conversations, thread tools and global memory used: No

## Accepted Failure Boundary

The review accepts the approval-governance commit, the one static reconstruction, the one consumed process-start attempt and the fail-closed stop. The frozen pre/semantics source passed its Manifest, source, parser, complete-arguments and expected-stdout identities. The first `Process.Start()` call then raised `System.ComponentModel.Win32Exception: The filename or extension is too long` before a PowerShell process was created.

The accepted counts are:

    static reconstructions: 1
    Process.Start attempts: 1
    runner processes created: 0
    PID / exit / stdout / stderr: unavailable
    all downstream PowerShell processes: 0
    frozen-chain Git children: 0
    Python processes: 0
    future evidence creations: 0
    automatic retries: 0

All three historical machine files remain byte-for-byte unchanged and all six semantics/post-sync paths remain absent.

## Established Root Cause

The frozen `ProcessStartInfo.Arguments` was 38,599 characters before the executable token and terminating null were considered. Microsoft documents that the `CreateProcessW` command-line string has a maximum length of 32,767 characters including the terminating null. The observed failure therefore establishes:

    FROZEN_OUTER_TRANSPORT_START_DEFECT
    ENCODED_COMMAND_COMMAND_LINE_OVERFLOW

This is not evidence of a pre host, pre verifier, bootstrap, harness, compatible verifier, semantics wrapper, Python, stderr classifier or Git synchronization defect because none of those components ran.

Authoritative source: [Microsoft CreateProcessW documentation](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw).

## Consumed Authorization

The approval at `72783071c17f6e3cab347823a8da080171c1a883` is consumed. It cannot authorize another `Process.Start`, shorter arguments, `-File`, stdin transport, temporary script, runtime switch or modified `ProcessStartInfo`. The 38,599-character transport is not reusable.

## Amendment 5G-B.1.1.1.1.3 Requirements

The next package may freeze a bounded-command-line, raw-stdin Base64 source transport. It must not execute a loader during package assembly.

Three target-specific loaders are required:

    PRE_AND_SEMANTICS_STDIN_LOADER
    POST_SYNC_STDIN_LOADER
    FINAL_VERIFIER_STDIN_LOADER

Each loader must have a short frozen EncodedCommand and a complete modeled CreateProcess command-line identity including the terminating null. That command line must remain materially below 32,767 characters.

The parent transport order must be frozen as:

1. Start the short loader process.
2. Immediately start concurrent raw stdout/stderr BaseStream drains.
3. Write the exact ASCII Base64 payload to `StandardInput.BaseStream`.
4. Flush and close stdin.
5. Wait for process and both drain tasks.
6. Apply exit, exact target stdout and exact PowerShell stderr-class gates.

The loader must read raw stdin to EOF, reject non-ASCII bytes, require the exact payload byte count and SHA, Base64-decode to strict UTF-16LE, require the decoded source identities and zero parser errors, create one ScriptBlock and invoke it once in the same PowerShell process. The loader must add no stdout of its own.

PowerShell's standard-input command behavior is documented by [Microsoft about_PowerShell_exe](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_powershell_exe?view=powershell-5.1). The recovery package uses raw BaseStream ASCII Base64 instead of direct source text to remove implicit text-encoding ambiguity.

## Required Integration Scope

The 194-line pre/semantics and 166-line post-sync target sources may retain their byte identities. The final verifier must be rebound to the new Amendment Manifest and approval-decision path without changing its Git, schema, artifact-stability or fixed-success semantics. The final host must be revised to launch the final verifier through the target-specific stdin loader.

Process accounting must distinguish a loader-backed PowerShell process from the target ScriptBlock invocation inside that same process.

## Required Static And Negative Fixtures

For every loader, package assembly must register without executing the loader:

- complete modeled command line below the limit;
- exact stdin payload accepted by the independent reference validator;
- truncated payload rejected;
- appended byte rejected;
- same-length mutation rejected;
- invalid Base64 rejected;
- decoded UTF-16LE mutation rejected;
- source SHA mismatch rejected;
- extra bytes after the payload rejected;
- parser-error payload rejected.

## Explicit Non-Authorization

This review does not authorize loader execution, target ScriptBlock invocation, approval governance, pre synchronization, bootstrap, semantics, evidence creation, post synchronization, final verification, synthetic rebinding, real validator, formal preflight, official input/token/capture, controller, verifier, Gold, reservation or Stage3B.

## Current State

    HARD_FAILURE_16_AUDIT_ACCEPTED
    HARD_FAILURE_16_CHECKPOINT_FROZEN
    APPROVAL_GOVERNANCE_COMMIT_VALID
    PRE_RUNNER_STATIC_RECONSTRUCTION_PASSED
    PRE_RUNNER_START_ATTEMPT_CONSUMED
    PRE_RUNNER_PROCESS_NOT_CREATED
    ROOT_CAUSE_ESTABLISHED_ENCODED_COMMAND_COMMAND_LINE_OVERFLOW
    CURRENT_APPROVAL_CONSUMED
    CURRENT_LONG_ENCODED_COMMAND_TRANSPORT_NOT_REUSABLE

    RETURN_FOR_AMENDMENT_5G_B_1_1_1_1_3
    BOUNDED_STDIN_SOURCE_TRANSPORT_RECOVERY_PACKAGE

    TRANSPORT_RETRY_NOT_APPROVED
    SEMANTICS_SEQUENCE_NOT_APPROVED
    POST_SYNC_NOT_APPROVED
    FINAL_VERIFIER_NOT_APPROVED
    SYNTHETIC_REBINDING_NOT_APPROVED
    FORMAL_PREFLIGHT_NOT_APPROVED
    OFFICIAL_EXECUTION_NOT_APPROVED
    GOLD_NOT_APPROVED
