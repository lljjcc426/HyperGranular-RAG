param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('PRE')]
    [string]$Mode
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ManifestRelativePath = 'docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6_MANIFEST.json'
$ExpectedRequestId = 'STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6'
$ExpectedPackageRevision = 'NESTED_DURABLE_RESULT_CAPTURE_PRE_ONLY_DIAGNOSTIC'
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

function Assert-RegisteredSource($Registry, [string]$RepositoryRoot, [string]$Label) {
    $path = Join-Path $RepositoryRoot ([string]$Registry.path)
    $bytes = [IO.File]::ReadAllBytes($path)
    if ($bytes.Length -ne [int]$Registry.source_bytes -or (Get-ExactSha256Hex $bytes) -cne [string]$Registry.source_sha256) { throw ($Label + ' source identity mismatch') }
    $tokens = $null
    $errors = $null
    [void][Management.Automation.Language.Parser]::ParseInput($Utf8.GetString($bytes), [ref]$tokens, [ref]$errors)
    if ($errors.Count -ne [int]$Registry.static_parse_errors) { throw ($Label + ' parser identity mismatch') }
}

function Get-RawLayer($Manifest, [string]$Layer) {
    foreach ($candidate in $Manifest.nested_raw_contract.layers) {
        if ([string]$candidate.layer -ceq $Layer) { return $candidate }
    }
    throw ('Raw layer contract missing: ' + $Layer)
}

function Get-RegisteredPowerShellStderrClass([byte[]]$Actual, $Frozen) {
    if ($Actual.Length -eq 0) { return 'EMPTY' }
    if ($Actual.Length -ne [int]$Frozen.bytes -or (Get-ExactSha256Hex $Actual) -cne [string]$Frozen.sha256) { return $null }
    Assert-ExactBytes $Actual ([Convert]::FromBase64String([string]$Frozen.base64)) 'Capture-host stderr'
    return 'EXACT_FROZEN_382_BYTE_STARTUP_CLIXML'
}

function Assert-RawRecord([string]$Path, [string]$Magic, [uint32]$LayerCode, [bool]$RequireZeroExit) {
    [byte[]]$bytes = [IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -lt 48) { throw ('Raw record is shorter than the fixed header: ' + $Path) }
    if ($Ascii.GetString($bytes, 0, 8) -cne $Magic) { throw ('Raw record magic mismatch: ' + $Path) }
    if ([BitConverter]::ToUInt32($bytes, 8) -ne 1 -or [BitConverter]::ToUInt32($bytes, 12) -ne 48) { throw ('Raw record format mismatch: ' + $Path) }
    if ([BitConverter]::ToUInt32($bytes, 16) -ne $LayerCode -or [BitConverter]::ToUInt32($bytes, 20) -ne 15) { throw ('Raw record layer or flags mismatch: ' + $Path) }
    $exitCode = [BitConverter]::ToInt32($bytes, 24)
    if ($RequireZeroExit -and $exitCode -ne 0) { throw ('Successful PRE chain contains nonzero raw exit: ' + $Path) }
    if ([BitConverter]::ToUInt32($bytes, 28) -ne 0) { throw ('Raw record reserved field mismatch: ' + $Path) }
    [uint64]$stdoutLength = [BitConverter]::ToUInt64($bytes, 32)
    [uint64]$stderrLength = [BitConverter]::ToUInt64($bytes, 40)
    if ([uint64]$bytes.Length -ne [uint64]48 + $stdoutLength + $stderrLength) { throw ('Raw record length mismatch: ' + $Path) }
}

if (-not [BitConverter]::IsLittleEndian) { throw 'Nested raw format requires a little-endian runtime' }
$ExpectedPackageCommit = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_PACKAGE_COMMIT', [EnvironmentVariableTarget]::Process)
$ExpectedApprovalGovernance = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT', [EnvironmentVariableTarget]::Process)
Assert-Binding $ExpectedPackageCommit 'Expected package commit'
Assert-Binding $ExpectedApprovalGovernance 'Expected approval-governance commit'

$RepositoryRoot = (Resolve-Path -LiteralPath '.').Path
$manifestBytes = [IO.File]::ReadAllBytes((Join-Path $RepositoryRoot $ManifestRelativePath))
$manifest = ConvertFrom-Json -InputObject ($Utf8.GetString($manifestBytes))
if ([string]$manifest.request_id -cne $ExpectedRequestId -or [string]$manifest.package_revision -cne $ExpectedPackageRevision) { throw 'Nested diagnostic Manifest identity mismatch' }

$prior = $manifest.prior_hard_failure_19
$priorPath = Join-Path $RepositoryRoot ([string]$prior.raw_repository_path)
$priorBytes = [IO.File]::ReadAllBytes($priorPath)
if ($priorBytes.Length -ne [int]$prior.raw_bytes -or (Get-ExactSha256Hex $priorBytes) -cne [string]$prior.raw_sha256) { throw 'Hard Failure 19 preserved raw identity mismatch' }
Assert-RawRecord $priorPath ([string]$prior.magic) ([uint32]$prior.layer_code) $false
if ([BitConverter]::ToInt32($priorBytes, 24) -ne [int]$prior.exit_code -or [BitConverter]::ToUInt64($priorBytes, 32) -ne [uint64]$prior.stdout_bytes -or [BitConverter]::ToUInt64($priorBytes, 40) -ne [uint64]$prior.stderr_bytes) { throw 'Hard Failure 19 preserved raw field mismatch' }

$self = $manifest.pre_nested_observer
$captureHost = $manifest.pre_nested_capture_host
Assert-RegisteredSource $self $RepositoryRoot 'PRE nested observer'
Assert-RegisteredSource $captureHost $RepositoryRoot 'PRE nested capture host'
$fileName = [string]$manifest.process_start_info_contract.file_name
$selfInvocation = $self.invocation
$selfArguments = [string]$selfInvocation.complete_arguments
$selfModeled = '"' + $fileName + '" ' + $selfArguments + [char]0
if ($selfArguments.Length -ne [int]$selfInvocation.complete_arguments_characters -or (Get-ExactSha256Hex $Ascii.GetBytes($selfArguments)) -cne [string]$selfInvocation.complete_arguments_ascii_sha256) { throw 'PRE nested observer arguments mismatch' }
if ($selfModeled.Length -ne [int]$selfInvocation.modeled_command_characters_including_terminal_null -or (Get-ExactSha256Hex $Ascii.GetBytes($selfModeled)) -cne [string]$selfInvocation.modeled_command_ascii_sha256_including_terminal_null) { throw 'PRE nested observer modeled command mismatch' }
if (([Environment]::CommandLine + [char]0) -cne $selfModeled) { throw 'PRE nested observer actual process command line mismatch' }

$captureInvocation = $captureHost.invocation
$captureArguments = [string]$captureInvocation.complete_arguments
$captureModeled = '"' + $fileName + '" ' + $captureArguments + [char]0
if ($captureArguments.Length -ne [int]$captureInvocation.complete_arguments_characters -or (Get-ExactSha256Hex $Ascii.GetBytes($captureArguments)) -cne [string]$captureInvocation.complete_arguments_ascii_sha256) { throw 'PRE nested capture-host arguments mismatch' }
if ($captureModeled.Length -ne [int]$captureInvocation.modeled_command_characters_including_terminal_null -or (Get-ExactSha256Hex $Ascii.GetBytes($captureModeled)) -cne [string]$captureInvocation.modeled_command_ascii_sha256_including_terminal_null) { throw 'PRE nested capture-host modeled command mismatch' }

foreach ($layer in $manifest.nested_raw_contract.layers) {
    $path = Join-Path $RepositoryRoot ([string]$layer.repository_path)
    if ([IO.File]::Exists($path) -or [IO.Directory]::Exists($path)) { throw ('PRE nested raw path collision: ' + $layer.repository_path) }
}
$outerLayer = Get-RawLayer $manifest 'OUTER_CAPTURE_HOST'
$outerRawPath = Join-Path $RepositoryRoot ([string]$outerLayer.repository_path)

$processContract = $manifest.process_start_info_contract
$processStartInfo = New-Object Diagnostics.ProcessStartInfo
$processStartInfo.FileName = $fileName
$processStartInfo.Arguments = $captureArguments
$processStartInfo.WorkingDirectory = [string]$processContract.working_directory
$processStartInfo.UseShellExecute = [bool]$processContract.use_shell_execute
$processStartInfo.RedirectStandardInput = [bool]$processContract.redirect_standard_input
$processStartInfo.RedirectStandardOutput = [bool]$processContract.redirect_standard_output
$processStartInfo.RedirectStandardError = [bool]$processContract.redirect_standard_error
$processStartInfo.CreateNoWindow = [bool]$processContract.create_no_window
foreach ($bindingName in @('HGRAG_EXPECTED_PACKAGE_COMMIT', 'HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT', 'HGRAG_EXPECTED_SEMANTICS_EVIDENCE_COMMIT', 'HGRAG_EXPECTED_POST_SYNC_AUDIT_COMMIT', 'HGRAG_EXPECTED_FINAL_ADAPTER_ATTESTATION_COMMIT')) {
    [void]$processStartInfo.EnvironmentVariables.Remove($bindingName)
}
$processStartInfo.EnvironmentVariables['HGRAG_EXPECTED_PACKAGE_COMMIT'] = $ExpectedPackageCommit
$processStartInfo.EnvironmentVariables['HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT'] = $ExpectedApprovalGovernance

$captureProcess = New-Object Diagnostics.Process
$captureProcess.StartInfo = $processStartInfo
try { $started = $captureProcess.Start() }
catch { $captureProcess.Dispose(); throw }
if (-not $started) { $captureProcess.Dispose(); throw 'PRE capture-host Process.Start returned false' }
$stdoutBuffer = New-Object IO.MemoryStream
$stderrBuffer = New-Object IO.MemoryStream
$stdoutDrain = $captureProcess.StandardOutput.BaseStream.CopyToAsync($stdoutBuffer)
$stderrDrain = $captureProcess.StandardError.BaseStream.CopyToAsync($stderrBuffer)
$captureProcess.WaitForExit()
[Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($stdoutDrain, $stderrDrain))
$captureExitCode = [int]$captureProcess.ExitCode
[byte[]]$captureStdoutBytes = $stdoutBuffer.ToArray()
[byte[]]$captureStderrBytes = $stderrBuffer.ToArray()
$captureProcess.Dispose()
$stdoutBuffer.Dispose()
$stderrBuffer.Dispose()

# No hash, classification, helper dispatch, or serializer is allowed between
# raw byte materialization above and completion of this CreateNew record.
[byte[]]$magic = $Ascii.GetBytes('HGRAGO16')
[uint32]$formatVersion = 1
[uint32]$headerBytes = 48
[uint32]$layerCode = [uint32]$outerLayer.layer_code
[uint32]$completionFlags = 15
[uint32]$reserved = 0
[uint64]$stdoutLength = [uint64]$captureStdoutBytes.Length
[uint64]$stderrLength = [uint64]$captureStderrBytes.Length
$rawStream = New-Object IO.FileStream($outerRawPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
try {
    $rawStream.Write($magic, 0, $magic.Length)
    [byte[]]$field = [BitConverter]::GetBytes($formatVersion); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($headerBytes); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($layerCode); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($completionFlags); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($captureExitCode); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($reserved); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($stdoutLength); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($stderrLength); $rawStream.Write($field, 0, $field.Length)
    $rawStream.Write($captureStdoutBytes, 0, $captureStdoutBytes.Length)
    $rawStream.Write($captureStderrBytes, 0, $captureStderrBytes.Length)
    $rawStream.Flush($true)
}
finally { $rawStream.Dispose() }

if ($captureExitCode -ne 0) { throw ('PRE capture-host nonzero exit: ' + $captureExitCode) }
$expectedCaptureStdout = $Utf8.GetBytes([string]$captureHost.fixed_success_stdout)
if ($captureStdoutBytes.Length -ne [int]$captureHost.fixed_success_stdout_bytes -or (Get-ExactSha256Hex $captureStdoutBytes) -cne [string]$captureHost.fixed_success_stdout_sha256) { throw 'PRE nested capture-host stdout identity mismatch' }
Assert-ExactBytes $captureStdoutBytes $expectedCaptureStdout 'PRE nested capture-host stdout'
$captureStderrClass = Get-RegisteredPowerShellStderrClass $captureStderrBytes $manifest.transport_base_frozen_stderr
if ($null -eq $captureStderrClass) { throw 'PRE nested capture-host stderr is not registered' }

foreach ($layer in $manifest.nested_raw_contract.layers) {
    $path = Join-Path $RepositoryRoot ([string]$layer.repository_path)
    if (-not [IO.File]::Exists($path)) { throw ('Successful PRE chain is missing raw layer: ' + $layer.layer) }
    Assert-RawRecord $path ([string]$layer.magic) ([uint32]$layer.layer_code) $true
}
foreach ($path in @($manifest.pre_diagnostic_paths.semantics_narrative, $manifest.pre_diagnostic_paths.semantics_machine)) {
    if (-not [IO.File]::Exists((Join-Path $RepositoryRoot ([string]$path)))) { throw ('Successful PRE chain is missing semantics evidence: ' + $path) }
}

$successBytes = $Utf8.GetBytes([string]$self.fixed_success_stdout)
if ($successBytes.Length -ne [int]$self.fixed_success_stdout_bytes -or (Get-ExactSha256Hex $successBytes) -cne [string]$self.fixed_success_stdout_sha256) { throw 'PRE nested observer success stdout identity mismatch' }
$standardOutput = [Console]::OpenStandardOutput()
$standardOutput.Write($successBytes, 0, $successBytes.Length)
$standardOutput.Flush()
