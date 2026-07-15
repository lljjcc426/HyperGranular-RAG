# Stage4B-U1-D Pre-Gold Amendment 5G-B.1.1.1.1.3 Package Review 1

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Review date: 2026-07-16
- Reviewed package: `97a8b169835c06330a6781ab63c59a482889c6bb`
- Direct parent / Hard Failure 16 checkpoint: `f28fc526faf74f80fdefb96ca189769dbcf1e5e4`
- Reviewed Manifest: 203,974 bytes / `DF088593BA620CE235419B2B759247914771FCFCE63B49A099A788AD29D5FC1C`
- Decision: `REJECT_AMENDMENT_5G_B_1_1_1_1_3_PACKAGE_AS_CURRENTLY_WRITTEN`
- Recovery: `RETURN_FOR_CORRECTED_AMENDMENT_5G_B_1_1_1_1_3_PACKAGE`
- Execution authorized: No
- Other project conversations, thread tools, and global memory used: No

## Accepted Findings

The review accepts Hard Failure 16 Review 1, package commit and exact seven-path scope, the three target-specific loader source designs, bounded command-line identities, raw-stdin payload identities, loader internal validation logic, rebound final-verifier static design, revised final-host static design and the reported 30/30 loader fixtures.

The accepted Hard Failure 16 boundary remains one static reconstruction, one consumed `Process.Start` attempt, zero created runner/downstream processes, zero evidence creations and zero retries. The 38,599-character transport is consumed and non-reusable.

These static acceptances do not approve the package or authorize execution.

## Blocking Finding 1: Pre/Post Parent Hosts Are Unfrozen

The reviewed Manifest contains seven source designs: three loaders, two targets, one rebound final verifier and one revised final host. It does not freeze executable parent source for launching the pre and post loaders.

The missing `PRE_AND_SEMANTICS_STDIN_TRANSPORT_HOST` and `POST_SYNC_STDIN_TRANSPORT_HOST` must each freeze source lines/bytes/SHA, parser state, UTF-16LE/Base64, complete arguments, modeled command line, loader/target reconstruction, `ProcessStartInfo`, raw drains, raw stdin write/flush/close, gate order, path preconditions, commit bindings, counts and fixed success stdout.

Hard Failure 16 occurred at this parent `Process.Start` layer. It cannot be implemented ad hoc in an approval decision.

## Blocking Finding 2: Success Evidence Attests Rejected Transport

The reviewed pre/post targets still read the prior `.1.1.1.1.2` Manifest and write the prior outer-runner complete-arguments fingerprints into their narratives. Those values describe the rejected long EncodedCommand transport, including pre SHA `53D27DD17FC3D4E6E8708E970C2BEFA4932AAE511A99D6EDF4A0BDFA9B498753` and post SHA `D55D3A04713814348752C5081F91B4FB41C52E68936657CC77905B5F9FC20ABC`.

A corrected success narrative must instead attest the current parent host, loader, modeled command line, stdin payload and decoded target identities. Execution with a new transport and evidence claiming the old transport is not an acceptable state.

## Blocking Finding 3: Final Verifier Does Not Reject Stale Attestation

The reviewed final verifier only requires the semantics narrative to be nonempty and checks three class/binding lines in the post narrative. It does not validate the new pre/post transport identities and would permit stale long-EncodedCommand fingerprints to reach terminal success.

The corrected final verifier must validate the current pre/post parent, loader and payload identities; validate final parent/loader identities; and reject either rejected long-transport fingerprint in success evidence.

## Corrected Package Requirements

The corrected package must:

1. freeze at least nine source designs by adding the two pre/post parent hosts;
2. choose a closed evidence scheme—either revise pre/post targets to attest current transport in existing narratives or add separately versioned `CreateNew` attestations and update all path/commit contracts;
3. extend final-verifier gates to exact current transport evidence and explicit stale-transport rejection;
4. update source, process, ScriptBlock, evidence, commit-parent and exact-path counts;
5. remain fully non-executing until a new approval binds the corrected package commit.

## Explicit Non-Authorization

This review does not authorize approval governance, either parent host, any loader process, any target ScriptBlock, inner pre/post verifier, bootstrap, harness, wrapper, Python, semantics evidence, post-sync audit, revised final host, final verifier, synthetic rebinding, real validator, formal preflight, official input/token/capture, controller, verifier, Gold, reservation or Stage3B.

## Current State

    HARD_FAILURE_16_AUDIT_ACCEPTED
    HARD_FAILURE_16_CHECKPOINT_FROZEN
    ROOT_CAUSE_ESTABLISHED_ENCODED_COMMAND_COMMAND_LINE_OVERFLOW

    THREE_STDIN_LOADER_INTERNAL_DESIGNS_STATICALLY_ACCEPTED
    RAW_STDIN_PAYLOAD_IDENTITIES_STATICALLY_ACCEPTED
    REVISED_FINAL_HOST_STATICALLY_ACCEPTED
    30_OF_30_FIXTURE_REPORT_ACCEPTED

    PRE_TRANSPORT_PARENT_HOST_UNFROZEN
    POST_TRANSPORT_PARENT_HOST_UNFROZEN
    PRE_NARRATIVE_ATTESTS_REJECTED_LONG_TRANSPORT
    POST_NARRATIVE_ATTESTS_REJECTED_LONG_TRANSPORT
    FINAL_VERIFIER_DOES_NOT_REJECT_STALE_TRANSPORT_ATTESTATION
    RETURN_FOR_CORRECTED_AMENDMENT_5G_B_1_1_1_1_3_PACKAGE

    CURRENT_PACKAGE_97A8B169_NOT_APPROVED
    TRANSPORT_EXECUTION_NOT_APPROVED
    SEMANTICS_SEQUENCE_NOT_APPROVED
    POST_SYNC_NOT_APPROVED
    FINAL_VERIFIER_NOT_APPROVED
    SYNTHETIC_NOT_APPROVED
    OFFICIAL_EXECUTION_NOT_APPROVED
    GOLD_NOT_APPROVED
