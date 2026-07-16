param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('PRE_ATTESTATION', 'TERMINAL')]
    [string]$Mode
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ExpectedRequestId = 'STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_5'
$ExpectedPackageRevision = 'FROZEN_OUTER_OBSERVER_DURABLE_RAW_RECOVERY'
$ManifestRelativePath = 'docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_5_MANIFEST.json'
$ApprovalDecisionRelativePath = 'docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_5_APPROVAL_DECISION.md'
$GitExe = 'C:\Program Files\Git\cmd\git.exe'
$Utf8 = New-Object Text.UTF8Encoding($false, $true)
$Ascii = New-Object Text.ASCIIEncoding
$Unicode = New-Object Text.UnicodeEncoding($false, $false, $true)
$GitProcesses = 0

function Get-Sha256Hex([byte[]]$Bytes) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace('-', '') }
    finally { $sha.Dispose() }
}

function Assert-ExactBytes([byte[]]$Actual, [byte[]]$Expected, [string]$Label) {
    if ($Actual.Length -ne $Expected.Length) { throw ($Label + ' length mismatch') }
    for ($i = 0; $i -lt $Actual.Length; $i++) {
        if ($Actual[$i] -ne $Expected[$i]) { throw ($Label + ' byte mismatch at ' + $i) }
    }
}

function Assert-Binding([string]$Value, [string]$Label) {
    if ($Value -cnotmatch '\A[0-9a-f]{40}\z') { throw ($Label + ' is missing or invalid') }
}

function Get-Snapshot([string]$Path, [string]$Label) {
    if (-not [IO.File]::Exists($Path) -or [IO.Directory]::Exists($Path)) { throw ($Label + ' is missing') }
    $bytes = [IO.File]::ReadAllBytes($Path)
    return [pscustomobject]@{ Path = $Path; Bytes = $bytes; Length = $bytes.Length; Sha256 = Get-Sha256Hex $bytes; Label = $Label }
}

function Assert-StableSnapshot($Snapshot) {
    $bytes = [IO.File]::ReadAllBytes([string]$Snapshot.Path)
    if ($bytes.Length -ne [int]$Snapshot.Length -or (Get-Sha256Hex $bytes) -cne [string]$Snapshot.Sha256) { throw ([string]$Snapshot.Label + ' changed during verification') }
    Assert-ExactBytes $bytes ([byte[]]$Snapshot.Bytes) ([string]$Snapshot.Label)
}

function Invoke-GitBytes([string]$Arguments, [string]$Label) {
    $script:GitProcesses++
    $psi = New-Object Diagnostics.ProcessStartInfo
    $psi.FileName = $GitExe
    $psi.Arguments = $Arguments
    $psi.WorkingDirectory = $RepositoryRoot
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true
    $process = New-Object Diagnostics.Process
    $process.StartInfo = $psi
    try { $started = $process.Start() }
    catch { $process.Dispose(); throw }
    if (-not $started) { $process.Dispose(); throw ($Label + ' Process.Start returned false') }
    $stdoutBuffer = New-Object IO.MemoryStream
    $stderrBuffer = New-Object IO.MemoryStream
    $stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync($stdoutBuffer)
    $stderrTask = $process.StandardError.BaseStream.CopyToAsync($stderrBuffer)
    $process.WaitForExit()
    [Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($stdoutTask, $stderrTask))
    $exitCode = $process.ExitCode
    $stdout = [byte[]]$stdoutBuffer.ToArray()
    $stderr = [byte[]]$stderrBuffer.ToArray()
    $process.Dispose()
    $stdoutBuffer.Dispose()
    $stderrBuffer.Dispose()
    if ($exitCode -ne 0) { throw ($Label + ' nonzero exit: ' + $exitCode) }
    if ($stderr.Length -ne 0) { throw ($Label + ' emitted stderr') }
    return $stdout
}

function Get-GitText([string]$Arguments, [string]$Label) {
    [byte[]]$bytes = Invoke-GitBytes $Arguments $Label
    return $Utf8.GetString($bytes).TrimEnd([char[]]@("`r", "`n"))
}

function Assert-ExactPathText([string]$Actual, [string[]]$Expected, [string]$Label) {
    $expectedText = [string]::Join("`n", $Expected)
    if ($Actual -cne $expectedText) { throw ($Label + ' changed-path set mismatch') }
}

function Get-StageContract($Manifest, [string]$Stage) {
    foreach ($candidate in $Manifest.adapter_execution_attestation_contract.stages) {
        if ([string]$candidate.stage -ceq $Stage) { return $candidate }
    }
    throw ('Stage contract is missing: ' + $Stage)
}

function Get-CaptureInvocation($CaptureHost, [string]$Stage) {
    foreach ($candidate in $CaptureHost.invocation_variants) {
        if ([string]$candidate.stage -ceq $Stage) { return $candidate }
    }
    throw ('Capture-host invocation is missing: ' + $Stage)
}

function Get-ObserverModeContract($Observer, [string]$RequestedMode) {
    foreach ($candidate in $Observer.modes) {
        if ([string]$candidate.mode -ceq $RequestedMode) { return $candidate }
    }
    throw ('Observer mode contract is missing: ' + $RequestedMode)
}

function Assert-TrackedSource($Registry, [string]$Label) {
    $path = Join-Path $RepositoryRoot ([string]$Registry.path)
    $bytes = [IO.File]::ReadAllBytes($path)
    if ($bytes.Length -ne [int]$Registry.source_bytes -or (Get-Sha256Hex $bytes) -cne [string]$Registry.source_sha256) { throw ($Label + ' tracked-file identity mismatch') }
    $text = $Utf8.GetString($bytes)
    foreach ($character in $text.ToCharArray()) { if ([int]$character -gt 127) { throw ($Label + ' is not ASCII-only') } }
    $tokens = $null
    $errors = $null
    [void][Management.Automation.Language.Parser]::ParseInput($text, [ref]$tokens, [ref]$errors)
    if ($errors.Count -ne [int]$Registry.static_parse_errors) { throw ($Label + ' parser identity mismatch') }
}

function Assert-InvocationEnvelope($Registry, [string]$Label) {
    $arguments = [string]$Registry.complete_arguments
    $modeled = '"' + [string]$manifest.adapter_invocation_contract.file_name + '" ' + $arguments + [char]0
    if ($arguments.Length -ne [int]$Registry.complete_arguments_characters -or (Get-Sha256Hex $Ascii.GetBytes($arguments)) -cne [string]$Registry.complete_arguments_ascii_sha256) { throw ($Label + ' arguments identity mismatch') }
    if ($modeled.Length -ne [int]$Registry.modeled_command_characters_including_terminal_null -or (Get-Sha256Hex $Ascii.GetBytes($modeled)) -cne [string]$Registry.modeled_command_ascii_sha256_including_terminal_null) { throw ($Label + ' modeled command identity mismatch') }
}

function Assert-ModeInvocation($Invocation, [string]$Label) {
    $arguments = [string]$Invocation.complete_arguments
    $modeled = '"' + [string]$manifest.adapter_invocation_contract.file_name + '" ' + $arguments + [char]0
    if ($arguments.Length -ne [int]$Invocation.complete_arguments_characters -or (Get-Sha256Hex $Ascii.GetBytes($arguments)) -cne [string]$Invocation.complete_arguments_ascii_sha256) { throw ($Label + ' arguments identity mismatch') }
    if ($modeled.Length -ne [int]$Invocation.modeled_command_characters_including_terminal_null -or (Get-Sha256Hex $Ascii.GetBytes($modeled)) -cne [string]$Invocation.modeled_command_ascii_sha256_including_terminal_null) { throw ($Label + ' modeled command identity mismatch') }
    $successBytes = $Utf8.GetBytes([string]$Invocation.fixed_success_stdout)
    if ($successBytes.Length -ne [int]$Invocation.fixed_success_stdout_bytes -or (Get-Sha256Hex $successBytes) -cne [string]$Invocation.fixed_success_stdout_sha256) { throw ($Label + ' success stdout identity mismatch') }
}

function Assert-ObserverInvocation($Invocation, [string]$Label) {
    $arguments = [string]$Invocation.observer_complete_arguments
    $modeled = '"' + [string]$manifest.adapter_invocation_contract.file_name + '" ' + $arguments + [char]0
    if ($arguments.Length -ne [int]$Invocation.observer_complete_arguments_characters -or (Get-Sha256Hex $Ascii.GetBytes($arguments)) -cne [string]$Invocation.observer_complete_arguments_ascii_sha256) { throw ($Label + ' arguments identity mismatch') }
    if ($modeled.Length -ne [int]$Invocation.observer_modeled_characters_including_terminal_null -or (Get-Sha256Hex $Ascii.GetBytes($modeled)) -cne [string]$Invocation.observer_modeled_ascii_sha256_including_terminal_null) { throw ($Label + ' modeled command identity mismatch') }
    $successBytes = $Utf8.GetBytes([string]$Invocation.fixed_success_stdout)
    if ($successBytes.Length -ne [int]$Invocation.fixed_success_stdout_bytes -or (Get-Sha256Hex $successBytes) -cne [string]$Invocation.fixed_success_stdout_sha256) { throw ($Label + ' success stdout identity mismatch') }
}

function Assert-RegisteredEncodedTransport($Entry, [string]$Label) {
    $source = [string]::Join("`n", [string[]]@($Entry.source_lines))
    $sourceBytes = $Utf8.GetBytes($source)
    if ($sourceBytes.Length -ne [int]$Entry.source_utf8_bytes -or (Get-Sha256Hex $sourceBytes) -cne [string]$Entry.source_sha256) { throw ($Label + ' source identity mismatch') }
    $tokens = $null
    $errors = $null
    [void][Management.Automation.Language.Parser]::ParseInput($source, [ref]$tokens, [ref]$errors)
    if ($errors.Count -ne 0 -or [int]$Entry.static_parse_errors -ne 0) { throw ($Label + ' parser state mismatch') }
    $encoded = [Convert]::ToBase64String($Unicode.GetBytes($source))
    $arguments = '-NoLogo -NoProfile -NonInteractive -EncodedCommand ' + $encoded
    if ($arguments.Length -ne [int]$Entry.complete_arguments_characters -or (Get-Sha256Hex $Ascii.GetBytes($arguments)) -cne [string]$Entry.complete_arguments_ascii_sha256) { throw ($Label + ' arguments identity mismatch') }
    $modeled = '"' + [string]$baseManifest.process_start_info_contract.file_name + '" ' + $arguments + [char]0
    if ($modeled.Length -ne [int]$Entry.modeled_createprocess_characters_including_terminal_null -or (Get-Sha256Hex $Ascii.GetBytes($modeled)) -cne [string]$Entry.modeled_createprocess_ascii_sha256_including_terminal_null -or $modeled.Length -ge 32767) { throw ($Label + ' modeled command mismatch') }
}

function Assert-RegisteredPayload($Target, [string]$Label) {
    $source = [string]::Join("`n", [string[]]@($Target.source_lines))
    $decoded = $Unicode.GetBytes($source)
    $payload = $Ascii.GetBytes([Convert]::ToBase64String($decoded))
    if ($payload.Length -ne [int]$Target.stdin_payload.ascii_bytes -or (Get-Sha256Hex $payload) -cne [string]$Target.stdin_payload.ascii_sha256) { throw ($Label + ' stdin payload identity mismatch') }
    if ($decoded.Length -ne [int]$Target.stdin_payload.decoded_utf16le_bytes -or (Get-Sha256Hex $decoded) -cne [string]$Target.stdin_payload.decoded_utf16le_sha256 -or [string]$Target.stdin_payload.decoded_source_sha256 -cne [string]$Target.source_sha256) { throw ($Label + ' decoded target identity mismatch') }
}

function Assert-LineExactlyOnce([string[]]$Lines, [string]$Expected, [string]$Label) {
    $count = @($Lines | Where-Object { $_ -ceq $Expected }).Count
    if ($count -ne 1) { throw ($Label + ' exact line count mismatch') }
}

function Resolve-PostMachineAttestation([byte[]]$Bytes) {
    foreach ($postHostClass in @('EMPTY', 'EXACT_FROZEN_382_BYTE_STARTUP_CLIXML')) {
        foreach ($postVerifierClass in @('EMPTY', 'EXACT_FROZEN_382_BYTE_STARTUP_CLIXML')) {
            $candidate = '{"status":"POST_SYNC_TRANSPORT_VERIFIED","post_host_stderr_class":"' + $postHostClass + '","post_verifier_stderr_class":"' + $postVerifierClass + '","post_host_processes":1,"post_verifier_processes":1,"post_verifier_git_processes":7,"official_accesses":0}'
            $candidateBytes = $Utf8.GetBytes($candidate)
            if ($Bytes.Length -eq $candidateBytes.Length -and (Get-Sha256Hex $Bytes) -ceq (Get-Sha256Hex $candidateBytes)) {
                Assert-ExactBytes $Bytes $candidateBytes 'Post-sync machine attestation'
                return [pscustomobject]@{ PostHost = $postHostClass; PostVerifier = $postVerifierClass }
            }
        }
    }
    throw 'Post-sync machine attestation is not registered'
}

function Assert-OriginalEvidence($StableSnapshots) {
    foreach ($item in @(
        [pscustomobject]@{ Path = 'results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stdout.bin'; Bytes = 122; Sha256 = 'BCDF0010147E5952AD0372ADF39EDA0A18D349B02107C340DEF05BAFE18C0F09' },
        [pscustomobject]@{ Path = 'results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_stderr.bin'; Bytes = 382; Sha256 = '4F2B6B3ED9201CA459DB2DD042E0A137C4E58BFE8E15A068E45AD8535FA5B1EF' },
        [pscustomobject]@{ Path = 'results/stage4b_u1_d_pregold_hard_failure_14_pre_sync_diagnostic.json'; Bytes = 944; Sha256 = 'F4022C8B4DF507D9A63085698B846358FF6D33F2A67B55B0C54EB871E8EB101B' }
    )) {
        $snapshot = Get-Snapshot (Join-Path $RepositoryRoot ([string]$item.Path)) 'Historical evidence'
        if ($snapshot.Length -ne [int]$item.Bytes -or $snapshot.Sha256 -cne [string]$item.Sha256) { throw 'Historical evidence identity mismatch' }
        $StableSnapshots.Add($snapshot)
    }

    $semanticsMachine = Get-Snapshot (Join-Path $RepositoryRoot ([string]$manifest.semantics_evidence_paths.target_machine)) 'Semantics machine evidence'
    if ($semanticsMachine.Length -ne 789 -or $semanticsMachine.Sha256 -cne 'EDBD4614B790256E314F4A8963128A5FB5A190FAC197437FB349D4C33C606135') { throw 'Semantics machine evidence identity mismatch' }
    $StableSnapshots.Add($semanticsMachine)
    $semanticsNarrative = Get-Snapshot (Join-Path $RepositoryRoot ([string]$manifest.semantics_evidence_paths.target_narrative)) 'Semantics narrative evidence'
    $StableSnapshots.Add($semanticsNarrative)
    $semanticsText = $Utf8.GetString([byte[]]$semanticsNarrative.Bytes)
    $semanticsLines = [string[]]($semanticsText -split "`n")
    Assert-LineExactlyOnce $semanticsLines ('- Package commit binding: `' + $ExpectedPackageCommit + '`') 'Pre package binding'
    Assert-LineExactlyOnce $semanticsLines ('- Approval-governance binding: `' + $ExpectedApprovalGovernance + '`') 'Pre approval binding'
    Assert-LineExactlyOnce $semanticsLines ('- pre stdin transport host source SHA-256: `' + [string]$baseManifest.pre_and_semantics_stdin_transport_host.source_sha256 + '`') 'Pre parent source'
    Assert-LineExactlyOnce $semanticsLines ('- pre stdin transport host complete-arguments SHA-256: `' + [string]$baseManifest.pre_and_semantics_stdin_transport_host.complete_arguments_ascii_sha256 + '`') 'Pre parent arguments'
    Assert-LineExactlyOnce $semanticsLines ('- pre stdin transport host modeled-command-line SHA-256: `' + [string]$baseManifest.pre_and_semantics_stdin_transport_host.modeled_createprocess_ascii_sha256_including_terminal_null + '`') 'Pre parent modeled command'
    Assert-LineExactlyOnce $semanticsLines ('- pre stdin loader source SHA-256: `' + [string]$baseManifest.pre_and_semantics_stdin_loader.source_sha256 + '`') 'Pre loader source'
    Assert-LineExactlyOnce $semanticsLines ('- pre stdin loader complete-arguments SHA-256: `' + [string]$baseManifest.pre_and_semantics_stdin_loader.complete_arguments_ascii_sha256 + '`') 'Pre loader arguments'
    Assert-LineExactlyOnce $semanticsLines ('- pre stdin loader modeled-command-line SHA-256: `' + [string]$baseManifest.pre_and_semantics_stdin_loader.modeled_createprocess_ascii_sha256_including_terminal_null + '`') 'Pre loader modeled command'
    Assert-LineExactlyOnce $semanticsLines ('- pre stdin payload ASCII bytes / SHA-256: `' + [string]$baseManifest.pre_and_semantics_target.stdin_payload.ascii_bytes + ' / ' + [string]$baseManifest.pre_and_semantics_target.stdin_payload.ascii_sha256 + '`') 'Pre stdin payload'
    Assert-LineExactlyOnce $semanticsLines ('- pre stdin payload decoded target SHA-256: `' + [string]$baseManifest.pre_and_semantics_target.stdin_payload.decoded_source_sha256 + '`') 'Pre decoded target'

    $postMachine = Get-Snapshot (Join-Path $RepositoryRoot ([string]$manifest.post_sync_audit_paths.target_machine)) 'Post-sync machine attestation'
    $StableSnapshots.Add($postMachine)
    $classes = Resolve-PostMachineAttestation ([byte[]]$postMachine.Bytes)
    $postNarrative = Get-Snapshot (Join-Path $RepositoryRoot ([string]$manifest.post_sync_audit_paths.target_narrative)) 'Post-sync narrative audit'
    $StableSnapshots.Add($postNarrative)
    $postText = $Utf8.GetString([byte[]]$postNarrative.Bytes)
    $postLines = [string[]]($postText -split "`n")
    Assert-LineExactlyOnce $postLines ('- Package commit binding: `' + $ExpectedPackageCommit + '`') 'Post package binding'
    Assert-LineExactlyOnce $postLines ('- Approval-governance binding: `' + $ExpectedApprovalGovernance + '`') 'Post approval binding'
    Assert-LineExactlyOnce $postLines ('- Semantics-evidence binding: `' + $ExpectedSemanticsEvidence + '`') 'Post semantics binding'
    Assert-LineExactlyOnce $postLines ('| post-sync outer runner -> post host | `' + $classes.PostHost + '` |') 'Post host class'
    Assert-LineExactlyOnce $postLines ('| post host -> unchanged post verifier | `' + $classes.PostVerifier + '` |') 'Post verifier class'
    Assert-LineExactlyOnce $postLines ('- post stdin transport host source SHA-256: `' + [string]$baseManifest.post_sync_stdin_transport_host.source_sha256 + '`') 'Post parent source'
    Assert-LineExactlyOnce $postLines ('- post stdin transport host complete-arguments SHA-256: `' + [string]$baseManifest.post_sync_stdin_transport_host.complete_arguments_ascii_sha256 + '`') 'Post parent arguments'
    Assert-LineExactlyOnce $postLines ('- post stdin transport host modeled-command-line SHA-256: `' + [string]$baseManifest.post_sync_stdin_transport_host.modeled_createprocess_ascii_sha256_including_terminal_null + '`') 'Post parent modeled command'
    Assert-LineExactlyOnce $postLines ('- post stdin loader source SHA-256: `' + [string]$baseManifest.post_sync_stdin_loader.source_sha256 + '`') 'Post loader source'
    Assert-LineExactlyOnce $postLines ('- post stdin loader complete-arguments SHA-256: `' + [string]$baseManifest.post_sync_stdin_loader.complete_arguments_ascii_sha256 + '`') 'Post loader arguments'
    Assert-LineExactlyOnce $postLines ('- post stdin loader modeled-command-line SHA-256: `' + [string]$baseManifest.post_sync_stdin_loader.modeled_createprocess_ascii_sha256_including_terminal_null + '`') 'Post loader modeled command'
    Assert-LineExactlyOnce $postLines ('- post stdin payload ASCII bytes / SHA-256: `' + [string]$baseManifest.post_sync_target.stdin_payload.ascii_bytes + ' / ' + [string]$baseManifest.post_sync_target.stdin_payload.ascii_sha256 + '`') 'Post stdin payload'
    Assert-LineExactlyOnce $postLines ('- post stdin payload decoded target SHA-256: `' + [string]$baseManifest.post_sync_target.stdin_payload.decoded_source_sha256 + '`') 'Post decoded target'

    foreach ($rejected in @([string]$baseManifest.rejected_transport.pre_runner_complete_arguments_sha256, [string]$baseManifest.rejected_transport.post_runner_complete_arguments_sha256)) {
        if ($semanticsText.Contains($rejected) -or $postText.Contains($rejected)) { throw 'Evidence contains rejected transport success fingerprint' }
    }
}

function Assert-Attestation($Contract, $Adapter, [string]$ExpectedStage) {
    $snapshot = Get-Snapshot (Join-Path $RepositoryRoot ([string]$Contract.repository_path)) ($ExpectedStage + ' adapter attestation')
    $record = ConvertFrom-Json -InputObject ($Utf8.GetString([byte[]]$snapshot.Bytes))
    if ([string]$record.schema_version -cne '2.0' -or [string]$record.request_id -cne $ExpectedRequestId -or [string]$record.stage -cne $ExpectedStage) { throw ($ExpectedStage + ' attestation schema mismatch') }
    if ([string]$record.package_commit -cne $ExpectedPackageCommit -or [string]$record.approval_governance_commit -cne $ExpectedApprovalGovernance) { throw ($ExpectedStage + ' attestation package binding mismatch') }
    if ($ExpectedStage -ceq 'PRE') {
        if ($null -ne $record.semantics_evidence_commit -or $null -ne $record.post_sync_audit_commit) { throw 'PRE attestation has premature commit bindings' }
    }
    elseif ($ExpectedStage -ceq 'POST') {
        if ([string]$record.semantics_evidence_commit -cne $ExpectedSemanticsEvidence -or $null -ne $record.post_sync_audit_commit) { throw 'POST attestation commit binding mismatch' }
    }
    else {
        if ([string]$record.semantics_evidence_commit -cne $ExpectedSemanticsEvidence -or [string]$record.post_sync_audit_commit -cne $ExpectedPostSyncAudit) { throw 'FINAL attestation commit binding mismatch' }
    }
    if ([string]$record.canonical_builder_path -cne [string]$manifest.adapter_attestation_canonical_builder.path -or [int]$record.canonical_builder_source_bytes -ne [int]$manifest.adapter_attestation_canonical_builder.source_bytes -or [string]$record.canonical_builder_source_sha256 -cne [string]$manifest.adapter_attestation_canonical_builder.source_sha256) { throw ($ExpectedStage + ' canonical-builder attestation mismatch') }
    if ([string]$record.capture_host_path -cne [string]$manifest.adapter_capture_attestation_host.path -or [int]$record.capture_host_source_bytes -ne [int]$manifest.adapter_capture_attestation_host.source_bytes -or [string]$record.capture_host_source_sha256 -cne [string]$manifest.adapter_capture_attestation_host.source_sha256) { throw ($ExpectedStage + ' capture-host attestation mismatch') }
    $captureInvocation = Get-CaptureInvocation $manifest.adapter_capture_attestation_host $ExpectedStage
    if ([string]$Contract.capture_host_invocation_id -cne [string]$captureInvocation.id) { throw ($ExpectedStage + ' stage-contract capture-host invocation mismatch') }
    if ([string]$record.capture_host_invocation_variant -cne [string]$captureInvocation.id) { throw ($ExpectedStage + ' capture-host invocation variant mismatch') }
    if ([int]$record.capture_host_arguments_characters -ne [int]$captureInvocation.complete_arguments_characters -or [string]$record.capture_host_arguments_sha256 -cne [string]$captureInvocation.complete_arguments_ascii_sha256) { throw ($ExpectedStage + ' capture-host arguments attestation mismatch') }
    if ([int]$record.capture_host_modeled_characters_including_terminal_null -ne [int]$captureInvocation.modeled_command_characters_including_terminal_null -or [string]$record.capture_host_modeled_sha256_including_terminal_null -cne [string]$captureInvocation.modeled_command_ascii_sha256_including_terminal_null) { throw ($ExpectedStage + ' capture-host modeled-command attestation mismatch') }
    if ([string]$record.adapter_path -cne [string]$Adapter.path -or [int]$record.adapter_source_bytes -ne [int]$Adapter.source_bytes -or [string]$record.adapter_source_sha256 -cne [string]$Adapter.source_sha256) { throw ($ExpectedStage + ' adapter source attestation mismatch') }
    if ([int]$record.adapter_arguments_characters -ne [int]$Adapter.complete_arguments_characters -or [string]$record.adapter_arguments_sha256 -cne [string]$Adapter.complete_arguments_ascii_sha256) { throw ($ExpectedStage + ' adapter arguments attestation mismatch') }
    if ([int]$record.adapter_modeled_characters_including_terminal_null -ne [int]$Adapter.modeled_command_characters_including_terminal_null -or [string]$record.adapter_modeled_sha256_including_terminal_null -cne [string]$Adapter.modeled_command_ascii_sha256_including_terminal_null) { throw ($ExpectedStage + ' adapter modeled-command attestation mismatch') }
    $variant = $null
    foreach ($candidate in $Adapter.success_stdout_variants) { if ([string]$candidate.id -ceq [string]$record.adapter_stdout_variant) { $variant = $candidate; break } }
    if ($null -eq $variant) { throw ($ExpectedStage + ' adapter stdout variant is unregistered') }
    if ([int]$record.adapter_stdout_bytes -ne [int]$variant.stdout_bytes -or [string]$record.adapter_stdout_sha256 -cne [string]$variant.stdout_sha256 -or [string]$record.adapter_to_parent_stderr_class -cne [string]$variant.parent_stderr_class) { throw ($ExpectedStage + ' adapter stdout or parent class attestation mismatch') }
    if ([string]$record.adapter_stderr_class -ceq 'EMPTY') {
        if ([int]$record.adapter_stderr_bytes -ne 0 -or [string]$record.adapter_stderr_sha256 -cne 'E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855') { throw ($ExpectedStage + ' empty adapter stderr attestation mismatch') }
    }
    elseif ([string]$record.adapter_stderr_class -ceq 'EXACT_FROZEN_382_BYTE_STARTUP_CLIXML') {
        if ([int]$record.adapter_stderr_bytes -ne 382 -or [string]$record.adapter_stderr_sha256 -cne '4F2B6B3ED9201CA459DB2DD042E0A137C4E58BFE8E15A068E45AD8535FA5B1EF') { throw ($ExpectedStage + ' CLIXML adapter stderr attestation mismatch') }
    }
    else { throw ($ExpectedStage + ' adapter stderr class is unregistered') }
    if ([string]$record.adapter_to_parent_stderr_class -notin @('EMPTY', 'EXACT_FROZEN_382_BYTE_STARTUP_CLIXML')) { throw ($ExpectedStage + ' parent stderr class is unregistered') }
    if ([int]$record.adapter_processes -ne 1 -or [int]$record.parent_processes -ne 1) { throw ($ExpectedStage + ' mandatory adapter mediation process counts mismatch') }
    [byte[]]$canonicalBytes = Build-CanonicalAdapterAttestationBytes $record
    Assert-ExactBytes ([byte[]]$snapshot.Bytes) $canonicalBytes ($ExpectedStage + ' canonical attestation bytes')
    return $snapshot
}

function Assert-OuterObservation([string]$ExpectedMode) {
    $modeContract = Get-ObserverModeContract $manifest.execution_observer $ExpectedMode
    $snapshot = Get-Snapshot (Join-Path $RepositoryRoot ([string]$modeContract.repository_observation_path)) ($ExpectedMode + ' outer observation')
    [byte[]]$bytes = $snapshot.Bytes
    if (-not [BitConverter]::IsLittleEndian) { throw 'Outer observation verification requires little-endian runtime' }
    if ($bytes.Length -lt 48) { throw ($ExpectedMode + ' outer observation is shorter than the fixed header') }
    if ($Ascii.GetString($bytes, 0, 8) -cne 'HGRAGO15') { throw ($ExpectedMode + ' outer observation magic mismatch') }
    if ([BitConverter]::ToUInt32($bytes, 8) -ne 1) { throw ($ExpectedMode + ' outer observation version mismatch') }
    if ([BitConverter]::ToUInt32($bytes, 12) -ne 48) { throw ($ExpectedMode + ' outer observation header-length mismatch') }
    if ([BitConverter]::ToUInt32($bytes, 16) -ne [uint32]$modeContract.binary_mode_code) { throw ($ExpectedMode + ' outer observation mode-code mismatch') }
    if ([BitConverter]::ToUInt32($bytes, 20) -ne 15) { throw ($ExpectedMode + ' outer observation completion-flags mismatch') }
    if ([BitConverter]::ToInt32($bytes, 24) -ne 0) { throw ($ExpectedMode + ' observed child exit is nonzero') }
    if ([BitConverter]::ToUInt32($bytes, 28) -ne 0) { throw ($ExpectedMode + ' outer observation reserved field mismatch') }
    [uint64]$stdoutLength = [BitConverter]::ToUInt64($bytes, 32)
    [uint64]$stderrLength = [BitConverter]::ToUInt64($bytes, 40)
    if ($stdoutLength -gt [int]::MaxValue -or $stderrLength -gt [int]::MaxValue) { throw ($ExpectedMode + ' outer observation stream length exceeds verifier limit') }
    [uint64]$expectedLength = [uint64]48 + $stdoutLength + $stderrLength
    if ([uint64]$bytes.Length -ne $expectedLength) { throw ($ExpectedMode + ' outer observation total-length mismatch') }
    [byte[]]$stdoutBytes = New-Object byte[] ([int]$stdoutLength)
    [byte[]]$stderrBytes = New-Object byte[] ([int]$stderrLength)
    [Array]::Copy($bytes, 48, $stdoutBytes, 0, [int]$stdoutLength)
    [Array]::Copy($bytes, 48 + [int]$stdoutLength, $stderrBytes, 0, [int]$stderrLength)
    if ([string]$modeContract.child_kind -ceq 'CAPTURE_HOST') {
        $childInvocation = Get-CaptureInvocation $manifest.adapter_capture_attestation_host ([string]$modeContract.child_stage)
    }
    elseif ([string]$modeContract.child_kind -ceq 'TERMINAL_VERIFIER') {
        $childInvocation = $manifest.terminal_adapter_attestation_commit_verifier.terminal_invocation
    }
    else { throw ($ExpectedMode + ' outer observation child kind mismatch') }
    [byte[]]$expectedStdout = $Utf8.GetBytes([string]$childInvocation.fixed_success_stdout)
    if ($stdoutBytes.Length -ne [int]$childInvocation.fixed_success_stdout_bytes -or (Get-Sha256Hex $stdoutBytes) -cne [string]$childInvocation.fixed_success_stdout_sha256) { throw ($ExpectedMode + ' outer observation stdout identity mismatch') }
    Assert-ExactBytes $stdoutBytes $expectedStdout ($ExpectedMode + ' outer observation stdout')
    if ($stderrBytes.Length -eq 0) { }
    elseif ($stderrBytes.Length -eq [int]$baseManifest.frozen_powershell_startup_stderr.bytes -and (Get-Sha256Hex $stderrBytes) -ceq [string]$baseManifest.frozen_powershell_startup_stderr.sha256) {
        Assert-ExactBytes $stderrBytes ([Convert]::FromBase64String([string]$baseManifest.frozen_powershell_startup_stderr.base64)) ($ExpectedMode + ' outer observation stderr')
    }
    else { throw ($ExpectedMode + ' outer observation stderr is unregistered') }
    return $snapshot
}

$ExpectedPackageCommit = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_PACKAGE_COMMIT', [EnvironmentVariableTarget]::Process)
$ExpectedApprovalGovernance = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT', [EnvironmentVariableTarget]::Process)
$ExpectedSemanticsEvidence = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_SEMANTICS_EVIDENCE_COMMIT', [EnvironmentVariableTarget]::Process)
$ExpectedPostSyncAudit = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_POST_SYNC_AUDIT_COMMIT', [EnvironmentVariableTarget]::Process)
$ExpectedFinalAttestationCommit = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_FINAL_ADAPTER_ATTESTATION_COMMIT', [EnvironmentVariableTarget]::Process)
foreach ($binding in @($ExpectedPackageCommit, $ExpectedApprovalGovernance, $ExpectedSemanticsEvidence, $ExpectedPostSyncAudit)) { Assert-Binding $binding 'Expected commit binding' }
if ($Mode -ceq 'TERMINAL') { Assert-Binding $ExpectedFinalAttestationCommit 'Expected final adapter-attestation commit' }

$RepositoryRoot = (Resolve-Path -LiteralPath '.').Path
$manifestSnapshot = Get-Snapshot (Join-Path $RepositoryRoot $ManifestRelativePath) 'Second-corrected Manifest'
$manifest = ConvertFrom-Json -InputObject ($Utf8.GetString([byte[]]$manifestSnapshot.Bytes))
if ([string]$manifest.request_id -cne $ExpectedRequestId -or [string]$manifest.package_revision -cne $ExpectedPackageRevision) { throw 'Second-corrected Manifest request identity mismatch' }
$baseSnapshot = Get-Snapshot (Join-Path $RepositoryRoot ([string]$manifest.base_manifest.path)) 'Base Manifest'
if ($baseSnapshot.Length -ne [int]$manifest.base_manifest.bytes -or $baseSnapshot.Sha256 -cne [string]$manifest.base_manifest.sha256) { throw 'Base Manifest identity mismatch' }
$baseManifest = ConvertFrom-Json -InputObject ($Utf8.GetString([byte[]]$baseSnapshot.Bytes))
$builderPath = Join-Path $RepositoryRoot ([string]$manifest.adapter_attestation_canonical_builder.path)
Assert-TrackedSource $manifest.adapter_attestation_canonical_builder 'Canonical attestation builder'
. $builderPath
if ($null -eq (Get-Command Build-CanonicalAdapterAttestationBytes -CommandType Function -ErrorAction SilentlyContinue)) { throw 'Canonical-builder function is unavailable' }

$stableSnapshots = New-Object Collections.Generic.List[object]
$stableSnapshots.Add($manifestSnapshot)
$stableSnapshots.Add($baseSnapshot)
$stableSnapshots.Add((Get-Snapshot (Join-Path $RepositoryRoot $ApprovalDecisionRelativePath) 'Approval Decision'))
$stableSnapshots.Add((Get-Snapshot $builderPath 'Canonical attestation builder'))

$stagePairs = @(
    @('PRE', $manifest.pre_parent_start_orchestrator),
    @('POST', $manifest.post_parent_start_orchestrator),
    @('FINAL', $manifest.final_parent_start_orchestrator)
)
foreach ($pair in $stagePairs) {
    Assert-TrackedSource $pair[1] ($pair[0] + ' adapter')
    Assert-InvocationEnvelope $pair[1] ($pair[0] + ' adapter')
    $stableSnapshots.Add((Get-Snapshot (Join-Path $RepositoryRoot ([string]$pair[1].path)) ($pair[0] + ' adapter')))
}
Assert-TrackedSource $manifest.adapter_capture_attestation_host 'Adapter capture-attestation host'
Assert-TrackedSource $manifest.terminal_adapter_attestation_commit_verifier 'Dual-mode final verifier'
Assert-TrackedSource $manifest.execution_observer 'Frozen outer result observer'
$stableSnapshots.Add((Get-Snapshot (Join-Path $RepositoryRoot ([string]$manifest.adapter_capture_attestation_host.path)) 'Adapter capture-attestation host'))
$stableSnapshots.Add((Get-Snapshot (Join-Path $RepositoryRoot ([string]$manifest.terminal_adapter_attestation_commit_verifier.path)) 'Dual-mode final verifier'))
$stableSnapshots.Add((Get-Snapshot (Join-Path $RepositoryRoot ([string]$manifest.execution_observer.path)) 'Frozen outer result observer'))
Assert-ModeInvocation $manifest.terminal_adapter_attestation_commit_verifier.pre_attestation_invocation 'Pre-attestation final verifier'
Assert-ModeInvocation $manifest.terminal_adapter_attestation_commit_verifier.terminal_invocation 'Terminal adapter-attestation verifier'
foreach ($captureInvocation in $manifest.adapter_capture_attestation_host.invocation_variants) {
    Assert-ModeInvocation $captureInvocation ([string]$captureInvocation.stage + ' capture-host invocation')
}
foreach ($observerInvocation in $manifest.execution_observer.modes) {
    Assert-ObserverInvocation $observerInvocation ([string]$observerInvocation.mode + ' observer invocation')
}

foreach ($entry in @(
    $baseManifest.pre_and_semantics_stdin_transport_host,
    $baseManifest.pre_and_semantics_stdin_loader,
    $baseManifest.post_sync_stdin_transport_host,
    $baseManifest.post_sync_stdin_loader,
    $baseManifest.revised_final_verifier_host,
    $baseManifest.final_verifier_stdin_loader
)) { Assert-RegisteredEncodedTransport $entry 'Inherited bounded envelope' }
Assert-RegisteredPayload $baseManifest.pre_and_semantics_target 'Pre target'
Assert-RegisteredPayload $baseManifest.post_sync_target 'Post target'
Assert-RegisteredPayload $baseManifest.final_post_sync_audit_commit_verifier 'Inherited final target'
Assert-OriginalEvidence $stableSnapshots

if ($Mode -ceq 'PRE_ATTESTATION') {
    $preContract = Get-StageContract $manifest 'PRE'
    $postContract = Get-StageContract $manifest 'POST'
    $finalContract = Get-StageContract $manifest 'FINAL'
    $stableSnapshots.Add((Assert-Attestation $preContract $manifest.pre_parent_start_orchestrator 'PRE'))
    $stableSnapshots.Add((Assert-Attestation $postContract $manifest.post_parent_start_orchestrator 'POST'))
    $stableSnapshots.Add((Assert-OuterObservation 'PRE'))
    $stableSnapshots.Add((Assert-OuterObservation 'POST'))
    $finalPath = Join-Path $RepositoryRoot ([string]$finalContract.repository_path)
    if ([IO.File]::Exists($finalPath) -or [IO.Directory]::Exists($finalPath)) { throw 'FINAL adapter attestation exists before FINAL capture' }
    $finalObservation = Get-ObserverModeContract $manifest.execution_observer 'FINAL'
    $terminalObservation = Get-ObserverModeContract $manifest.execution_observer 'TERMINAL'
    if ([IO.File]::Exists((Join-Path $RepositoryRoot ([string]$finalObservation.repository_observation_path)))) { throw 'FINAL outer observation exists before FINAL capture' }
    if ([IO.File]::Exists((Join-Path $RepositoryRoot ([string]$terminalObservation.repository_observation_path)))) { throw 'TERMINAL outer observation exists before TERMINAL execution' }
    $head = Get-GitText 'rev-parse HEAD' 'Git post HEAD'
    $semanticsCommit = Get-GitText 'rev-parse HEAD^' 'Git semantics commit'
    $approvalCommit = Get-GitText 'rev-parse HEAD^^' 'Git approval commit'
    $packageCommit = Get-GitText 'rev-parse HEAD^^^' 'Git package commit'
    if ($head -cne $ExpectedPostSyncAudit -or $semanticsCommit -cne $ExpectedSemanticsEvidence -or $approvalCommit -cne $ExpectedApprovalGovernance -or $packageCommit -cne $ExpectedPackageCommit) { throw 'Pre-attestation four-layer commit chain mismatch' }
    Assert-ExactPathText (Get-GitText ('diff-tree --no-commit-id --name-only -r ' + $head) 'Git post paths') ([string[]]$manifest.post_sync_audit_commit.exact_changed_paths) 'Post-sync audit commit'
    Assert-ExactPathText (Get-GitText ('diff-tree --no-commit-id --name-only -r ' + $semanticsCommit) 'Git semantics paths') ([string[]]$manifest.semantics_evidence_commit.exact_changed_paths) 'Semantics evidence commit'
    Assert-ExactPathText (Get-GitText ('diff-tree --no-commit-id --name-only -r ' + $approvalCommit) 'Git approval paths') ([string[]]$manifest.future_approval_governance.exact_changed_paths) 'Approval-governance commit'
    Assert-ExactPathText (Get-GitText ('diff-tree --no-commit-id --name-only -r ' + $packageCommit) 'Git package paths') ([string[]]$manifest.package_changed_paths_exact) 'Second-corrected package commit'
    $expectedGitProcesses = 12
    $success = [string]$manifest.terminal_adapter_attestation_commit_verifier.pre_attestation_invocation.fixed_success_stdout
}
else {
    $preContract = Get-StageContract $manifest 'PRE'
    $postContract = Get-StageContract $manifest 'POST'
    $finalContract = Get-StageContract $manifest 'FINAL'
    $stableSnapshots.Add((Assert-Attestation $preContract $manifest.pre_parent_start_orchestrator 'PRE'))
    $stableSnapshots.Add((Assert-Attestation $postContract $manifest.post_parent_start_orchestrator 'POST'))
    $stableSnapshots.Add((Assert-Attestation $finalContract $manifest.final_parent_start_orchestrator 'FINAL'))
    $stableSnapshots.Add((Assert-OuterObservation 'PRE'))
    $stableSnapshots.Add((Assert-OuterObservation 'POST'))
    $stableSnapshots.Add((Assert-OuterObservation 'FINAL'))
    $terminalObservation = Get-ObserverModeContract $manifest.execution_observer 'TERMINAL'
    if ([IO.File]::Exists((Join-Path $RepositoryRoot ([string]$terminalObservation.repository_observation_path)))) { throw 'TERMINAL outer observation exists before TERMINAL execution' }

    $head = Get-GitText 'rev-parse HEAD' 'Git final attestation HEAD'
    $postCommit = Get-GitText 'rev-parse HEAD^' 'Git post commit'
    $semanticsCommit = Get-GitText 'rev-parse HEAD^^' 'Git semantics commit'
    $approvalCommit = Get-GitText 'rev-parse HEAD^^^' 'Git approval commit'
    $packageCommit = Get-GitText 'rev-parse HEAD^^^^' 'Git package commit'
    if ($head -cne $ExpectedFinalAttestationCommit -or $postCommit -cne $ExpectedPostSyncAudit -or $semanticsCommit -cne $ExpectedSemanticsEvidence -or $approvalCommit -cne $ExpectedApprovalGovernance -or $packageCommit -cne $ExpectedPackageCommit) { throw 'Terminal five-layer commit chain mismatch' }
    Assert-ExactPathText (Get-GitText ('diff-tree --no-commit-id --name-only -r ' + $head) 'Git final attestation paths') ([string[]]$manifest.final_adapter_attestation_commit.exact_changed_paths) 'Final adapter-attestation commit'
    Assert-ExactPathText (Get-GitText ('diff-tree --no-commit-id --name-only -r ' + $postCommit) 'Git post paths') ([string[]]$manifest.post_sync_audit_commit.exact_changed_paths) 'Post-sync audit commit'
    Assert-ExactPathText (Get-GitText ('diff-tree --no-commit-id --name-only -r ' + $semanticsCommit) 'Git semantics paths') ([string[]]$manifest.semantics_evidence_commit.exact_changed_paths) 'Semantics evidence commit'
    Assert-ExactPathText (Get-GitText ('diff-tree --no-commit-id --name-only -r ' + $approvalCommit) 'Git approval paths') ([string[]]$manifest.future_approval_governance.exact_changed_paths) 'Approval-governance commit'
    Assert-ExactPathText (Get-GitText ('diff-tree --no-commit-id --name-only -r ' + $packageCommit) 'Git package paths') ([string[]]$manifest.package_changed_paths_exact) 'Second-corrected package commit'
    $expectedGitProcesses = 14
    $success = [string]$manifest.terminal_adapter_attestation_commit_verifier.terminal_invocation.fixed_success_stdout
}

$status = Get-GitText 'status --porcelain=v1 --untracked-files=all' 'Git status'
if (-not [string]::IsNullOrEmpty($status)) { throw 'Verifier worktree is not clean' }
$originMain = Get-GitText 'rev-parse refs/remotes/origin/main' 'Git origin main'
$remoteUrl = Get-GitText 'remote get-url origin' 'Git remote URL'
$directMainText = Get-GitText ('ls-remote ' + $remoteUrl + ' refs/heads/main') 'Git direct main'
$directMain = ($directMainText -split '\s+')[0]
if ($originMain -cne $head -or $directMain -cne $head) { throw 'Verifier local/origin/direct-main mismatch' }
if ($GitProcesses -ne $expectedGitProcesses) { throw 'Verifier Git process count mismatch' }

foreach ($snapshot in $stableSnapshots) { Assert-StableSnapshot $snapshot }

$successBytes = $Utf8.GetBytes($success)
$standardOutput = [Console]::OpenStandardOutput()
$standardOutput.Write($successBytes, 0, $successBytes.Length)
$standardOutput.Flush()
