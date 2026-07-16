param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('PRE', 'POST', 'FINAL')]
    [string]$Stage
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ManifestRelativePath = 'docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_5_MANIFEST.json'
$ExpectedRequestId = 'STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_5'
$ExpectedPackageRevision = 'FROZEN_OUTER_OBSERVER_DURABLE_RAW_RECOVERY'
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

function Get-CaptureInvocation($CaptureHost, [string]$RequestedStage) {
    foreach ($candidate in $CaptureHost.invocation_variants) {
        if ([string]$candidate.stage -ceq $RequestedStage) { return $candidate }
    }
    throw ('Capture-host invocation is missing: ' + $RequestedStage)
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
if ([string]$manifest.request_id -cne $ExpectedRequestId -or [string]$manifest.package_revision -cne $ExpectedPackageRevision) { throw 'Second-corrected Manifest identity mismatch' }
$baseBytes = [IO.File]::ReadAllBytes((Join-Path $RepositoryRoot ([string]$manifest.base_manifest.path)))
if ($baseBytes.Length -ne [int]$manifest.base_manifest.bytes -or (Get-Sha256Hex $baseBytes) -cne [string]$manifest.base_manifest.sha256) { throw 'Base Manifest identity mismatch' }
$baseManifest = ConvertFrom-Json -InputObject ($Utf8.GetString($baseBytes))
$frozenStderr = $baseManifest.frozen_powershell_startup_stderr

$stageContract = Get-StageContract $manifest $Stage
$adapterProperty = $manifest.PSObject.Properties[[string]$stageContract.adapter_registry_key]
if ($null -eq $adapterProperty) { throw 'Adapter registry entry is missing' }
$adapter = $adapterProperty.Value
$captureHost = $manifest.adapter_capture_attestation_host
$captureInvocation = Get-CaptureInvocation $captureHost $Stage
if ([string]$stageContract.capture_host_invocation_id -cne [string]$captureInvocation.id) { throw 'Stage contract capture-host invocation mismatch' }
$builder = $manifest.adapter_attestation_canonical_builder

$captureHostBytes = [IO.File]::ReadAllBytes((Join-Path $RepositoryRoot ([string]$captureHost.path)))
if ($captureHostBytes.Length -ne [int]$captureHost.source_bytes -or (Get-Sha256Hex $captureHostBytes) -cne [string]$captureHost.source_sha256) { throw 'Capture-host tracked-file identity mismatch' }
$adapterBytes = [IO.File]::ReadAllBytes((Join-Path $RepositoryRoot ([string]$adapter.path)))
if ($adapterBytes.Length -ne [int]$adapter.source_bytes -or (Get-Sha256Hex $adapterBytes) -cne [string]$adapter.source_sha256) { throw 'Adapter tracked-file identity mismatch' }
$builderPath = Join-Path $RepositoryRoot ([string]$builder.path)
$builderBytes = [IO.File]::ReadAllBytes($builderPath)
if ($builderBytes.Length -ne [int]$builder.source_bytes -or (Get-Sha256Hex $builderBytes) -cne [string]$builder.source_sha256) { throw 'Canonical-builder tracked-file identity mismatch' }
$builderText = $Utf8.GetString($builderBytes)
$builderTokens = $null
$builderErrors = $null
[void][Management.Automation.Language.Parser]::ParseInput($builderText, [ref]$builderTokens, [ref]$builderErrors)
if ($builderErrors.Count -ne [int]$builder.static_parse_errors) { throw 'Canonical-builder parser identity mismatch' }
. $builderPath
if ($null -eq (Get-Command Build-CanonicalAdapterAttestationBytes -CommandType Function -ErrorAction SilentlyContinue)) { throw 'Canonical-builder function is unavailable' }

$fileName = [string]$manifest.adapter_invocation_contract.file_name
$captureArguments = [string]$captureInvocation.complete_arguments
$captureModeled = '"' + $fileName + '" ' + $captureArguments + [char]0
if ($captureArguments.Length -ne [int]$captureInvocation.complete_arguments_characters -or (Get-Sha256Hex $Ascii.GetBytes($captureArguments)) -cne [string]$captureInvocation.complete_arguments_ascii_sha256) { throw 'Capture-host invocation arguments mismatch' }
if ($captureModeled.Length -ne [int]$captureInvocation.modeled_command_characters_including_terminal_null -or (Get-Sha256Hex $Ascii.GetBytes($captureModeled)) -cne [string]$captureInvocation.modeled_command_ascii_sha256_including_terminal_null) { throw 'Capture-host modeled command mismatch' }
$actualCaptureModeled = [Environment]::CommandLine + [char]0
if ($actualCaptureModeled -cne $captureModeled) { throw 'Capture-host actual process command line mismatch' }

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

$semanticsBinding = $null
$postBinding = $null
if ($Stage -in @('POST', 'FINAL')) { $semanticsBinding = $ExpectedSemanticsEvidence }
if ($Stage -ceq 'FINAL') { $postBinding = $ExpectedPostSyncAudit }
$values = [pscustomobject]@{
    request_id = $ExpectedRequestId
    stage = $Stage
    package_commit = $ExpectedPackageCommit
    approval_governance_commit = $ExpectedApprovalGovernance
    semantics_evidence_commit = $semanticsBinding
    post_sync_audit_commit = $postBinding
    canonical_builder_path = [string]$builder.path
    canonical_builder_source_bytes = [int]$builder.source_bytes
    canonical_builder_source_sha256 = [string]$builder.source_sha256
    capture_host_path = [string]$captureHost.path
    capture_host_source_bytes = [int]$captureHost.source_bytes
    capture_host_source_sha256 = [string]$captureHost.source_sha256
    capture_host_invocation_variant = [string]$captureInvocation.id
    capture_host_arguments_characters = [int]$captureInvocation.complete_arguments_characters
    capture_host_arguments_sha256 = [string]$captureInvocation.complete_arguments_ascii_sha256
    capture_host_modeled_characters_including_terminal_null = [int]$captureInvocation.modeled_command_characters_including_terminal_null
    capture_host_modeled_sha256_including_terminal_null = [string]$captureInvocation.modeled_command_ascii_sha256_including_terminal_null
    adapter_path = [string]$adapter.path
    adapter_source_bytes = [int]$adapter.source_bytes
    adapter_source_sha256 = [string]$adapter.source_sha256
    adapter_arguments_characters = [int]$adapter.complete_arguments_characters
    adapter_arguments_sha256 = [string]$adapter.complete_arguments_ascii_sha256
    adapter_modeled_characters_including_terminal_null = [int]$adapter.modeled_command_characters_including_terminal_null
    adapter_modeled_sha256_including_terminal_null = [string]$adapter.modeled_command_ascii_sha256_including_terminal_null
    adapter_stdout_variant = [string]$matchedVariant.id
    adapter_stdout_bytes = [int]$stdoutBytes.Length
    adapter_stdout_sha256 = Get-Sha256Hex $stdoutBytes
    adapter_stderr_bytes = [int]$stderrBytes.Length
    adapter_stderr_sha256 = Get-Sha256Hex $stderrBytes
    adapter_stderr_class = $adapterStderrClass
    adapter_to_parent_stderr_class = [string]$matchedVariant.parent_stderr_class
}
[byte[]]$attestationBytes = Build-CanonicalAdapterAttestationBytes $values
$targetPath = Join-Path $RepositoryRoot ([string]$stageContract.repository_path)
if ([IO.File]::Exists($targetPath) -or [IO.Directory]::Exists($targetPath)) { throw ('Repository adapter attestation path collision: ' + $targetPath) }
Write-CreateNew $targetPath $attestationBytes

$success = '{"status":"' + $Stage + '_ADAPTER_ATTESTATION_REPOSITORY_CREATED","adapter_processes":1,"repository_attestations_created":1}'
$successBytes = $Utf8.GetBytes($success)
if ($successBytes.Length -ne [int]$captureInvocation.fixed_success_stdout_bytes -or (Get-Sha256Hex $successBytes) -cne [string]$captureInvocation.fixed_success_stdout_sha256) { throw 'Capture-host success stdout identity mismatch' }
Assert-ExactBytes $successBytes ($Utf8.GetBytes([string]$captureInvocation.fixed_success_stdout)) 'Capture-host success stdout'
$standardOutput = [Console]::OpenStandardOutput()
$standardOutput.Write($successBytes, 0, $successBytes.Length)
$standardOutput.Flush()
