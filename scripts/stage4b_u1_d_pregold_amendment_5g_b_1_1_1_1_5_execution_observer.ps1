param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('PRE', 'POST', 'FINAL', 'TERMINAL')]
    [string]$Mode
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ManifestRelativePath = 'docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_5_MANIFEST.json'
$ExpectedRequestId = 'STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_5'
$ExpectedPackageRevision = 'FROZEN_OUTER_OBSERVER_DURABLE_RAW_RECOVERY'
$ExpectedDescriptor = 'QUOTED_FILE_NAME_SPACE_ARGUMENTS_TERMINAL_NULL'
$Utf8 = New-Object Text.UTF8Encoding($false, $true)
$Ascii = New-Object Text.ASCIIEncoding

function Get-ExactSha256Hex([byte[]]$Bytes) {
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($algorithm.ComputeHash($Bytes))).Replace('-', '') }
    finally { $algorithm.Dispose() }
}

function Assert-ExactBytes([byte[]]$Actual, [byte[]]$Expected, [string]$Label) {
    if ($Actual.Length -ne $Expected.Length) { throw ($Label + ' length mismatch') }
    for ($index = 0; $index -lt $Actual.Length; $index++) {
        if ($Actual[$index] -ne $Expected[$index]) { throw ($Label + ' byte mismatch at ' + $index) }
    }
}

function Assert-Binding([string]$Value, [string]$Label) {
    if ($Value -cnotmatch '\A[0-9a-f]{40}\z') { throw ($Label + ' is missing or invalid') }
}

function Get-ModeContract($Observer, [string]$RequestedMode) {
    foreach ($candidate in $Observer.modes) {
        if ([string]$candidate.mode -ceq $RequestedMode) { return $candidate }
    }
    throw ('Observer mode contract is missing: ' + $RequestedMode)
}

function Get-CaptureInvocation($CaptureHost, [string]$RequestedStage) {
    foreach ($candidate in $CaptureHost.invocation_variants) {
        if ([string]$candidate.stage -ceq $RequestedStage) { return $candidate }
    }
    throw ('Capture-host invocation is missing: ' + $RequestedStage)
}

function Get-RegisteredPowerShellStderrClass([byte[]]$Actual, $Frozen) {
    if ($Actual.Length -eq 0) { return 'EMPTY' }
    if ($Actual.Length -ne [int]$Frozen.bytes) { return $null }
    if ((Get-ExactSha256Hex $Actual) -cne [string]$Frozen.sha256) { return $null }
    Assert-ExactBytes $Actual ([Convert]::FromBase64String([string]$Frozen.base64)) 'Observed child stderr'
    return 'EXACT_FROZEN_382_BYTE_STARTUP_CLIXML'
}

$shaCommand = Get-Command Get-ExactSha256Hex -ErrorAction Stop
if ($shaCommand.CommandType -ne [Management.Automation.CommandTypes]::Function) { throw 'Exact SHA helper command type mismatch' }
if (-not [BitConverter]::IsLittleEndian) { throw 'Outer observation format requires little-endian runtime' }

$RepositoryRoot = (Resolve-Path -LiteralPath '.').Path
$manifestPath = Join-Path $RepositoryRoot $ManifestRelativePath
$manifestBytes = [IO.File]::ReadAllBytes($manifestPath)
$manifest = ConvertFrom-Json -InputObject ($Utf8.GetString($manifestBytes))
if ([string]$manifest.request_id -cne $ExpectedRequestId -or [string]$manifest.package_revision -cne $ExpectedPackageRevision) { throw 'Observer Manifest identity mismatch' }
$baseBytes = [IO.File]::ReadAllBytes((Join-Path $RepositoryRoot ([string]$manifest.base_manifest.path)))
if ($baseBytes.Length -ne [int]$manifest.base_manifest.bytes -or (Get-ExactSha256Hex $baseBytes) -cne [string]$manifest.base_manifest.sha256) { throw 'Observer base Manifest identity mismatch' }
$baseManifest = ConvertFrom-Json -InputObject ($Utf8.GetString($baseBytes))

$observer = $manifest.execution_observer
$observerBytes = [IO.File]::ReadAllBytes((Join-Path $RepositoryRoot ([string]$observer.path)))
if ($observerBytes.Length -ne [int]$observer.source_bytes -or (Get-ExactSha256Hex $observerBytes) -cne [string]$observer.source_sha256) { throw 'Observer tracked-file identity mismatch' }
$observerTokens = $null
$observerErrors = $null
[void][Management.Automation.Language.Parser]::ParseInput($Utf8.GetString($observerBytes), [ref]$observerTokens, [ref]$observerErrors)
if ($observerErrors.Count -ne [int]$observer.static_parse_errors) { throw 'Observer parser identity mismatch' }

$modeContract = Get-ModeContract $observer $Mode
$processContract = $manifest.adapter_invocation_contract
if ([string]$processContract.modeled_command_descriptor -cne $ExpectedDescriptor) { throw 'Observer modeled-command descriptor mismatch' }
$fileName = [string]$processContract.file_name
if ($fileName -cne 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe') { throw 'Observer executable path mismatch' }
if ([string]$processContract.working_directory -cne $RepositoryRoot) { throw 'Observer working-directory mismatch' }
if ([bool]$processContract.use_shell_execute -or [bool]$processContract.redirect_standard_input -or -not [bool]$processContract.redirect_standard_output -or -not [bool]$processContract.redirect_standard_error -or -not [bool]$processContract.create_no_window) { throw 'Observer redirect or window contract mismatch' }

$observerArguments = [string]$modeContract.observer_complete_arguments
$observerModeled = '"' + $fileName + '" ' + $observerArguments + [char]0
if ($observerArguments.Length -ne [int]$modeContract.observer_complete_arguments_characters -or (Get-ExactSha256Hex $Ascii.GetBytes($observerArguments)) -cne [string]$modeContract.observer_complete_arguments_ascii_sha256) { throw 'Observer invocation arguments mismatch' }
if ($observerModeled.Length -ne [int]$modeContract.observer_modeled_characters_including_terminal_null -or (Get-ExactSha256Hex $Ascii.GetBytes($observerModeled)) -cne [string]$modeContract.observer_modeled_ascii_sha256_including_terminal_null) { throw 'Observer modeled command mismatch' }
if (([Environment]::CommandLine + [char]0) -cne $observerModeled) { throw 'Observer actual process command line mismatch' }

$bindingNames = @(
    'HGRAG_EXPECTED_PACKAGE_COMMIT',
    'HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT',
    'HGRAG_EXPECTED_SEMANTICS_EVIDENCE_COMMIT',
    'HGRAG_EXPECTED_POST_SYNC_AUDIT_COMMIT',
    'HGRAG_EXPECTED_FINAL_ADAPTER_ATTESTATION_COMMIT'
)
$bindingValues = @{}
foreach ($bindingName in $bindingNames) {
    $bindingValues[$bindingName] = [Environment]::GetEnvironmentVariable($bindingName, [EnvironmentVariableTarget]::Process)
}
foreach ($requiredName in $modeContract.required_environment_bindings) {
    Assert-Binding ([string]$bindingValues[[string]$requiredName]) ([string]$requiredName)
}

$childRegistryProperty = $manifest.PSObject.Properties[[string]$modeContract.child_registry_key]
if ($null -eq $childRegistryProperty) { throw 'Observer child registry entry is missing' }
$childRegistry = $childRegistryProperty.Value
if ([string]$modeContract.child_kind -ceq 'CAPTURE_HOST') {
    $childInvocation = Get-CaptureInvocation $childRegistry ([string]$modeContract.child_stage)
}
elseif ([string]$modeContract.child_kind -ceq 'TERMINAL_VERIFIER') {
    $childInvocation = $childRegistry.terminal_invocation
}
else { throw 'Observer child kind is invalid' }

$childBytes = [IO.File]::ReadAllBytes((Join-Path $RepositoryRoot ([string]$childRegistry.path)))
if ($childBytes.Length -ne [int]$childRegistry.source_bytes -or (Get-ExactSha256Hex $childBytes) -cne [string]$childRegistry.source_sha256) { throw 'Observer child source identity mismatch' }
$childTokens = $null
$childErrors = $null
[void][Management.Automation.Language.Parser]::ParseInput($Utf8.GetString($childBytes), [ref]$childTokens, [ref]$childErrors)
if ($childErrors.Count -ne [int]$childRegistry.static_parse_errors) { throw 'Observer child parser identity mismatch' }

$childArguments = [string]$childInvocation.complete_arguments
$childModeled = '"' + $fileName + '" ' + $childArguments + [char]0
if ($childArguments.Length -ne [int]$childInvocation.complete_arguments_characters -or (Get-ExactSha256Hex $Ascii.GetBytes($childArguments)) -cne [string]$childInvocation.complete_arguments_ascii_sha256) { throw 'Observer child arguments mismatch' }
if ($childModeled.Length -ne [int]$childInvocation.modeled_command_characters_including_terminal_null -or (Get-ExactSha256Hex $Ascii.GetBytes($childModeled)) -cne [string]$childInvocation.modeled_command_ascii_sha256_including_terminal_null) { throw 'Observer child modeled command mismatch' }

$observationPath = Join-Path $RepositoryRoot ([string]$modeContract.repository_observation_path)
if ([IO.File]::Exists($observationPath) -or [IO.Directory]::Exists($observationPath)) { throw ('Outer observation path collision: ' + $observationPath) }

$processStartInfo = New-Object Diagnostics.ProcessStartInfo
$processStartInfo.FileName = $fileName
$processStartInfo.Arguments = $childArguments
$processStartInfo.WorkingDirectory = [string]$processContract.working_directory
$processStartInfo.UseShellExecute = [bool]$processContract.use_shell_execute
$processStartInfo.RedirectStandardInput = [bool]$processContract.redirect_standard_input
$processStartInfo.RedirectStandardOutput = [bool]$processContract.redirect_standard_output
$processStartInfo.RedirectStandardError = [bool]$processContract.redirect_standard_error
$processStartInfo.CreateNoWindow = [bool]$processContract.create_no_window
foreach ($bindingName in $bindingNames) { [void]$processStartInfo.EnvironmentVariables.Remove($bindingName) }
foreach ($requiredName in $modeContract.required_environment_bindings) {
    $processStartInfo.EnvironmentVariables[[string]$requiredName] = [string]$bindingValues[[string]$requiredName]
}

$childProcess = New-Object Diagnostics.Process
$childProcess.StartInfo = $processStartInfo
try { $processStarted = $childProcess.Start() }
catch { $childProcess.Dispose(); throw }
if (-not $processStarted) { $childProcess.Dispose(); throw 'Observer child Process.Start returned false' }

$stdoutBuffer = New-Object IO.MemoryStream
$stderrBuffer = New-Object IO.MemoryStream
$stdoutDrain = $childProcess.StandardOutput.BaseStream.CopyToAsync($stdoutBuffer)
$stderrDrain = $childProcess.StandardError.BaseStream.CopyToAsync($stderrBuffer)
$childProcess.WaitForExit()
[Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($stdoutDrain, $stderrDrain))
$childExitCode = [int]$childProcess.ExitCode
[byte[]]$childStdoutBytes = $stdoutBuffer.ToArray()
[byte[]]$childStderrBytes = $stderrBuffer.ToArray()
$childProcess.Dispose()
$stdoutBuffer.Dispose()
$stderrBuffer.Dispose()

# No hash, classification, helper dispatch, or serializer is allowed between
# obtaining the raw byte arrays above and completing this CreateNew record.
[byte[]]$magic = $Ascii.GetBytes('HGRAGO15')
[uint32]$formatVersion = 1
[uint32]$headerBytes = 48
[uint32]$modeCode = [uint32]$modeContract.binary_mode_code
[uint32]$completionFlags = 15
[uint32]$reserved = 0
[uint64]$stdoutLength = [uint64]$childStdoutBytes.Length
[uint64]$stderrLength = [uint64]$childStderrBytes.Length
$observationStream = New-Object IO.FileStream($observationPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
try {
    $observationStream.Write($magic, 0, $magic.Length)
    [byte[]]$field = [BitConverter]::GetBytes($formatVersion); $observationStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($headerBytes); $observationStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($modeCode); $observationStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($completionFlags); $observationStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($childExitCode); $observationStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($reserved); $observationStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($stdoutLength); $observationStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($stderrLength); $observationStream.Write($field, 0, $field.Length)
    $observationStream.Write($childStdoutBytes, 0, $childStdoutBytes.Length)
    $observationStream.Write($childStderrBytes, 0, $childStderrBytes.Length)
    $observationStream.Flush($true)
}
finally { $observationStream.Dispose() }

if ($childExitCode -ne 0) { throw ('Observed child nonzero exit: ' + $childExitCode) }
$expectedChildStdout = $Utf8.GetBytes([string]$childInvocation.fixed_success_stdout)
if ($childStdoutBytes.Length -ne [int]$childInvocation.fixed_success_stdout_bytes -or (Get-ExactSha256Hex $childStdoutBytes) -cne [string]$childInvocation.fixed_success_stdout_sha256) { throw 'Observed child stdout identity mismatch' }
Assert-ExactBytes $childStdoutBytes $expectedChildStdout 'Observed child stdout'
$childStderrClass = Get-RegisteredPowerShellStderrClass $childStderrBytes $baseManifest.frozen_powershell_startup_stderr
if ($null -eq $childStderrClass) { throw 'Observed child stderr is not registered' }

$observerSuccessBytes = $Utf8.GetBytes([string]$modeContract.fixed_success_stdout)
if ($observerSuccessBytes.Length -ne [int]$modeContract.fixed_success_stdout_bytes -or (Get-ExactSha256Hex $observerSuccessBytes) -cne [string]$modeContract.fixed_success_stdout_sha256) { throw 'Observer success stdout identity mismatch' }
$standardOutput = [Console]::OpenStandardOutput()
$standardOutput.Write($observerSuccessBytes, 0, $observerSuccessBytes.Length)
$standardOutput.Flush()
