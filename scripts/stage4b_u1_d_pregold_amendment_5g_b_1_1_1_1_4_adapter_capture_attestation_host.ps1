param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('PRE', 'POST', 'FINAL')]
    [string]$Stage
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ManifestRelativePath = 'docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4_MANIFEST.json'
$ExpectedRequestId = 'STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4'
$ExpectedPackageRevision = 'CORRECTED_AFTER_PACKAGE_REVIEW_1'
$Utf8 = New-Object Text.UTF8Encoding($false, $true)
$Ascii = New-Object Text.ASCIIEncoding

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

function Get-RegisteredPowerShellStderrClass([byte[]]$Actual, $Frozen) {
    if ($Actual.Length -eq 0) { return 'EMPTY' }
    if ($Actual.Length -ne [int]$Frozen.bytes -or (Get-Sha256Hex $Actual) -cne [string]$Frozen.sha256) { return $null }
    Assert-ExactBytes $Actual ([Convert]::FromBase64String([string]$Frozen.base64)) 'Adapter stderr'
    return 'EXACT_FROZEN_382_BYTE_STARTUP_CLIXML'
}

function Get-JsonString([string]$Value) {
    return '"' + $Value.Replace('\', '\\').Replace('"', '\"') + '"'
}

function Write-CreateNew([string]$Path, [byte[]]$Bytes) {
    $stream = New-Object IO.FileStream($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try {
        $stream.Write($Bytes, 0, $Bytes.Length)
        $stream.Flush()
    }
    finally { $stream.Dispose() }
}

function Assert-Binding([string]$Value, [string]$Label) {
    if ($Value -cnotmatch '\A[0-9a-f]{40}\z') { throw ($Label + ' is missing or invalid') }
}

function Get-StageContract($Manifest, [string]$RequestedStage) {
    foreach ($candidate in $Manifest.adapter_execution_attestation_contract.stages) {
        if ([string]$candidate.stage -ceq $RequestedStage) { return $candidate }
    }
    throw ('Stage contract is missing: ' + $RequestedStage)
}

function Assert-PendingAttestation($Attestation, $Contract, [string]$PackageCommit, [string]$ApprovalCommit, [string]$SemanticsCommit, [string]$PostCommit) {
    if ([string]$Attestation.request_id -cne $ExpectedRequestId -or [string]$Attestation.stage -cne [string]$Contract.stage) { throw 'Pending attestation request or stage mismatch' }
    if ([string]$Attestation.package_commit -cne $PackageCommit -or [string]$Attestation.approval_governance_commit -cne $ApprovalCommit) { throw 'Pending attestation package or approval binding mismatch' }
    if ([string]$Contract.stage -ceq 'PRE') {
        if ($null -ne $Attestation.semantics_evidence_commit -or $null -ne $Attestation.post_sync_audit_commit) { throw 'PRE pending attestation has premature commit bindings' }
    }
    elseif ([string]$Contract.stage -ceq 'POST') {
        if ([string]$Attestation.semantics_evidence_commit -cne $SemanticsCommit -or $null -ne $Attestation.post_sync_audit_commit) { throw 'POST pending attestation commit binding mismatch' }
    }
    else {
        if ([string]$Attestation.semantics_evidence_commit -cne $SemanticsCommit -or [string]$Attestation.post_sync_audit_commit -cne $PostCommit) { throw 'FINAL pending attestation commit binding mismatch' }
    }
    if ([int]$Attestation.adapter_processes -ne 1 -or [int]$Attestation.parent_processes -ne 1) { throw 'Pending attestation process counts mismatch' }
    if ([string]$Attestation.adapter_stderr_class -notin @('EMPTY', 'EXACT_FROZEN_382_BYTE_STARTUP_CLIXML')) { throw 'Pending adapter stderr class is not registered' }
    if ([string]$Attestation.adapter_to_parent_stderr_class -notin @('EMPTY', 'EXACT_FROZEN_382_BYTE_STARTUP_CLIXML')) { throw 'Pending parent stderr class is not registered' }
}

$ExpectedPackageCommit = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_PACKAGE_COMMIT', [EnvironmentVariableTarget]::Process)
$ExpectedApprovalGovernance = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT', [EnvironmentVariableTarget]::Process)
$ExpectedSemanticsEvidence = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_SEMANTICS_EVIDENCE_COMMIT', [EnvironmentVariableTarget]::Process)
$ExpectedPostSyncAudit = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_POST_SYNC_AUDIT_COMMIT', [EnvironmentVariableTarget]::Process)
Assert-Binding $ExpectedPackageCommit 'Expected package commit'
Assert-Binding $ExpectedApprovalGovernance 'Expected approval-governance commit'
if ($Stage -in @('POST', 'FINAL')) { Assert-Binding $ExpectedSemanticsEvidence 'Expected semantics-evidence commit' }
if ($Stage -ceq 'FINAL') { Assert-Binding $ExpectedPostSyncAudit 'Expected post-sync audit commit' }

$RepositoryRoot = (Resolve-Path -LiteralPath '.').Path
$manifestBytes = [IO.File]::ReadAllBytes((Join-Path $RepositoryRoot $ManifestRelativePath))
$manifest = ConvertFrom-Json -InputObject ($Utf8.GetString($manifestBytes))
if ([string]$manifest.request_id -cne $ExpectedRequestId -or [string]$manifest.package_revision -cne $ExpectedPackageRevision) { throw 'Corrected Manifest identity mismatch' }
$baseBytes = [IO.File]::ReadAllBytes((Join-Path $RepositoryRoot ([string]$manifest.base_manifest.path)))
if ($baseBytes.Length -ne [int]$manifest.base_manifest.bytes -or (Get-Sha256Hex $baseBytes) -cne [string]$manifest.base_manifest.sha256) { throw 'Base Manifest identity mismatch' }
$baseManifest = ConvertFrom-Json -InputObject ($Utf8.GetString($baseBytes))
$frozenStderr = $baseManifest.frozen_powershell_startup_stderr

$stageContract = Get-StageContract $manifest $Stage
$adapterProperty = $manifest.PSObject.Properties[[string]$stageContract.adapter_registry_key]
if ($null -eq $adapterProperty) { throw 'Adapter registry entry is missing' }
$adapter = $adapterProperty.Value
$captureHost = $manifest.adapter_capture_attestation_host

$captureHostBytes = [IO.File]::ReadAllBytes((Join-Path $RepositoryRoot ([string]$captureHost.path)))
if ($captureHostBytes.Length -ne [int]$captureHost.source_bytes -or (Get-Sha256Hex $captureHostBytes) -cne [string]$captureHost.source_sha256) { throw 'Capture-host tracked-file identity mismatch' }
$adapterBytes = [IO.File]::ReadAllBytes((Join-Path $RepositoryRoot ([string]$adapter.path)))
if ($adapterBytes.Length -ne [int]$adapter.source_bytes -or (Get-Sha256Hex $adapterBytes) -cne [string]$adapter.source_sha256) { throw 'Adapter tracked-file identity mismatch' }

$fileName = [string]$manifest.adapter_invocation_contract.file_name
$arguments = [string]$adapter.complete_arguments
$modeled = '"' + $fileName + '" ' + $arguments + [char]0
if ($arguments.Length -ne [int]$adapter.complete_arguments_characters -or (Get-Sha256Hex $Ascii.GetBytes($arguments)) -cne [string]$adapter.complete_arguments_ascii_sha256) { throw 'Adapter invocation arguments mismatch' }
if ($modeled.Length -ne [int]$adapter.modeled_command_characters_including_terminal_null -or (Get-Sha256Hex $Ascii.GetBytes($modeled)) -cne [string]$adapter.modeled_command_ascii_sha256_including_terminal_null) { throw 'Adapter modeled command mismatch' }

$psi = New-Object Diagnostics.ProcessStartInfo
$psi.FileName = $fileName
$psi.Arguments = $arguments
$psi.WorkingDirectory = [string]$manifest.adapter_invocation_contract.working_directory
$psi.UseShellExecute = [bool]$manifest.adapter_invocation_contract.use_shell_execute
$psi.RedirectStandardInput = [bool]$manifest.adapter_invocation_contract.redirect_standard_input
$psi.RedirectStandardOutput = [bool]$manifest.adapter_invocation_contract.redirect_standard_output
$psi.RedirectStandardError = [bool]$manifest.adapter_invocation_contract.redirect_standard_error
$psi.CreateNoWindow = [bool]$manifest.adapter_invocation_contract.create_no_window
$psi.EnvironmentVariables['HGRAG_EXPECTED_PACKAGE_COMMIT'] = $ExpectedPackageCommit
$psi.EnvironmentVariables['HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT'] = $ExpectedApprovalGovernance
if ($Stage -in @('POST', 'FINAL')) { $psi.EnvironmentVariables['HGRAG_EXPECTED_SEMANTICS_EVIDENCE_COMMIT'] = $ExpectedSemanticsEvidence }
if ($Stage -ceq 'FINAL') { $psi.EnvironmentVariables['HGRAG_EXPECTED_POST_SYNC_AUDIT_COMMIT'] = $ExpectedPostSyncAudit }

$process = New-Object Diagnostics.Process
$process.StartInfo = $psi
try { $started = $process.Start() }
catch { $process.Dispose(); throw }
if (-not $started) { $process.Dispose(); throw 'Adapter Process.Start returned false' }
$stdoutBuffer = New-Object IO.MemoryStream
$stderrBuffer = New-Object IO.MemoryStream
$stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync($stdoutBuffer)
$stderrTask = $process.StandardError.BaseStream.CopyToAsync($stderrBuffer)
$process.WaitForExit()
[Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($stdoutTask, $stderrTask))
$exitCode = $process.ExitCode
$stdoutBytes = [byte[]]$stdoutBuffer.ToArray()
$stderrBytes = [byte[]]$stderrBuffer.ToArray()
$process.Dispose()
$stdoutBuffer.Dispose()
$stderrBuffer.Dispose()
if ($exitCode -ne 0) { throw ('Adapter nonzero exit: ' + $exitCode) }

$matchedVariant = $null
foreach ($variant in $adapter.success_stdout_variants) {
    $expectedStdout = $Utf8.GetBytes([string]$variant.stdout)
    if ($stdoutBytes.Length -ne [int]$variant.stdout_bytes -or (Get-Sha256Hex $stdoutBytes) -cne [string]$variant.stdout_sha256) { continue }
    Assert-ExactBytes $stdoutBytes $expectedStdout 'Adapter stdout'
    $matchedVariant = $variant
    break
}
if ($null -eq $matchedVariant) { throw 'Adapter stdout is not a registered class-bearing variant' }
$adapterStderrClass = Get-RegisteredPowerShellStderrClass $stderrBytes $frozenStderr
if ($null -eq $adapterStderrClass) { throw 'Adapter stderr is not registered' }

$semanticsJson = 'null'
$postJson = 'null'
if ($Stage -in @('POST', 'FINAL')) { $semanticsJson = Get-JsonString $ExpectedSemanticsEvidence }
if ($Stage -ceq 'FINAL') { $postJson = Get-JsonString $ExpectedPostSyncAudit }
$attestation = '{' +
    '"schema_version":"1.0",' +
    '"request_id":' + (Get-JsonString $ExpectedRequestId) + ',' +
    '"stage":' + (Get-JsonString $Stage) + ',' +
    '"package_commit":' + (Get-JsonString $ExpectedPackageCommit) + ',' +
    '"approval_governance_commit":' + (Get-JsonString $ExpectedApprovalGovernance) + ',' +
    '"semantics_evidence_commit":' + $semanticsJson + ',' +
    '"post_sync_audit_commit":' + $postJson + ',' +
    '"capture_host_path":' + (Get-JsonString ([string]$captureHost.path)) + ',' +
    '"capture_host_source_bytes":' + [string]$captureHost.source_bytes + ',' +
    '"capture_host_source_sha256":' + (Get-JsonString ([string]$captureHost.source_sha256)) + ',' +
    '"adapter_path":' + (Get-JsonString ([string]$adapter.path)) + ',' +
    '"adapter_source_bytes":' + [string]$adapter.source_bytes + ',' +
    '"adapter_source_sha256":' + (Get-JsonString ([string]$adapter.source_sha256)) + ',' +
    '"adapter_arguments_characters":' + [string]$adapter.complete_arguments_characters + ',' +
    '"adapter_arguments_sha256":' + (Get-JsonString ([string]$adapter.complete_arguments_ascii_sha256)) + ',' +
    '"adapter_modeled_characters_including_terminal_null":' + [string]$adapter.modeled_command_characters_including_terminal_null + ',' +
    '"adapter_modeled_sha256_including_terminal_null":' + (Get-JsonString ([string]$adapter.modeled_command_ascii_sha256_including_terminal_null)) + ',' +
    '"adapter_stdout_variant":' + (Get-JsonString ([string]$matchedVariant.id)) + ',' +
    '"adapter_stdout_bytes":' + [string]$stdoutBytes.Length + ',' +
    '"adapter_stdout_sha256":' + (Get-JsonString (Get-Sha256Hex $stdoutBytes)) + ',' +
    '"adapter_stderr_bytes":' + [string]$stderrBytes.Length + ',' +
    '"adapter_stderr_sha256":' + (Get-JsonString (Get-Sha256Hex $stderrBytes)) + ',' +
    '"adapter_stderr_class":' + (Get-JsonString $adapterStderrClass) + ',' +
    '"adapter_to_parent_stderr_class":' + (Get-JsonString ([string]$matchedVariant.parent_stderr_class)) + ',' +
    '"adapter_processes":1,' +
    '"parent_processes":1' +
    '}'
$attestationBytes = $Utf8.GetBytes($attestation)

$pendingRoot = Join-Path ([IO.Path]::GetTempPath()) ([string]$manifest.adapter_execution_attestation_contract.pending_root_directory_name)
[void][IO.Directory]::CreateDirectory($pendingRoot)
$pendingPath = Join-Path $pendingRoot ([string]$stageContract.pending_file_name)
Write-CreateNew $pendingPath $attestationBytes

if ($Stage -ceq 'FINAL') {
    $pendingRecords = New-Object Collections.Generic.List[object]
    foreach ($contract in $manifest.adapter_execution_attestation_contract.stages) {
        $sourcePath = Join-Path $pendingRoot ([string]$contract.pending_file_name)
        $bytes = [IO.File]::ReadAllBytes($sourcePath)
        $record = ConvertFrom-Json -InputObject ($Utf8.GetString($bytes))
        Assert-PendingAttestation $record $contract $ExpectedPackageCommit $ExpectedApprovalGovernance $ExpectedSemanticsEvidence $ExpectedPostSyncAudit
        $targetPath = Join-Path $RepositoryRoot ([string]$contract.repository_path)
        if ([IO.File]::Exists($targetPath) -or [IO.Directory]::Exists($targetPath)) { throw ('Repository adapter attestation path collision: ' + $targetPath) }
        $pendingRecords.Add([pscustomobject]@{ TargetPath = $targetPath; Bytes = $bytes })
    }
    foreach ($pendingRecord in $pendingRecords) { Write-CreateNew ([string]$pendingRecord.TargetPath) ([byte[]]$pendingRecord.Bytes) }
    $success = '{"status":"FINAL_ADAPTER_ATTESTATIONS_PROMOTED","adapter_processes":1,"pending_attestations_verified":3,"repository_attestations_created":3}'
}
else {
    $success = '{"status":"' + $Stage + '_ADAPTER_ATTESTATION_PENDING_CREATED","adapter_processes":1,"pending_attestations_created":1,"repository_attestations_created":0}'
}
$successBytes = $Utf8.GetBytes($success)
$standardOutput = [Console]::OpenStandardOutput()
$standardOutput.Write($successBytes, 0, $successBytes.Length)
$standardOutput.Flush()
