param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('PRE')]
    [string]$Stage
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
    Assert-ExactBytes $Actual ([Convert]::FromBase64String([string]$Frozen.base64)) 'Adapter stderr'
    return 'EXACT_FROZEN_382_BYTE_STARTUP_CLIXML'
}

$ExpectedPackageCommit = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_PACKAGE_COMMIT', [EnvironmentVariableTarget]::Process)
$ExpectedApprovalGovernance = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT', [EnvironmentVariableTarget]::Process)
Assert-Binding $ExpectedPackageCommit 'Expected package commit'
Assert-Binding $ExpectedApprovalGovernance 'Expected approval-governance commit'

$RepositoryRoot = (Resolve-Path -LiteralPath '.').Path
$manifestBytes = [IO.File]::ReadAllBytes((Join-Path $RepositoryRoot $ManifestRelativePath))
$manifest = ConvertFrom-Json -InputObject ($Utf8.GetString($manifestBytes))
if ([string]$manifest.request_id -cne $ExpectedRequestId -or [string]$manifest.package_revision -cne $ExpectedPackageRevision) { throw 'Nested diagnostic Manifest identity mismatch' }

$self = $manifest.pre_nested_capture_host
$adapter = $manifest.pre_nested_adapter
Assert-RegisteredSource $self $RepositoryRoot 'PRE nested capture host'
Assert-RegisteredSource $adapter $RepositoryRoot 'PRE nested adapter'
$fileName = [string]$manifest.process_start_info_contract.file_name
$selfInvocation = $self.invocation
$selfArguments = [string]$selfInvocation.complete_arguments
$selfModeled = '"' + $fileName + '" ' + $selfArguments + [char]0
if ($selfArguments.Length -ne [int]$selfInvocation.complete_arguments_characters -or (Get-ExactSha256Hex $Ascii.GetBytes($selfArguments)) -cne [string]$selfInvocation.complete_arguments_ascii_sha256) { throw 'PRE nested capture-host arguments mismatch' }
if ($selfModeled.Length -ne [int]$selfInvocation.modeled_command_characters_including_terminal_null -or (Get-ExactSha256Hex $Ascii.GetBytes($selfModeled)) -cne [string]$selfInvocation.modeled_command_ascii_sha256_including_terminal_null) { throw 'PRE nested capture-host modeled command mismatch' }
if (([Environment]::CommandLine + [char]0) -cne $selfModeled) { throw 'PRE nested capture-host actual process command line mismatch' }

$adapterArguments = [string]$adapter.complete_arguments
$adapterModeled = '"' + $fileName + '" ' + $adapterArguments + [char]0
if ($adapterArguments.Length -ne [int]$adapter.complete_arguments_characters -or (Get-ExactSha256Hex $Ascii.GetBytes($adapterArguments)) -cne [string]$adapter.complete_arguments_ascii_sha256) { throw 'PRE nested adapter arguments mismatch' }
if ($adapterModeled.Length -ne [int]$adapter.modeled_command_characters_including_terminal_null -or (Get-ExactSha256Hex $Ascii.GetBytes($adapterModeled)) -cne [string]$adapter.modeled_command_ascii_sha256_including_terminal_null) { throw 'PRE nested adapter modeled command mismatch' }

$adapterLayer = Get-RawLayer $manifest 'ADAPTER_CHILD'
$adapterRawPath = Join-Path $RepositoryRoot ([string]$adapterLayer.repository_path)
if ([IO.File]::Exists($adapterRawPath) -or [IO.Directory]::Exists($adapterRawPath)) { throw 'PRE adapter raw path collision' }

$processContract = $manifest.process_start_info_contract
$processStartInfo = New-Object Diagnostics.ProcessStartInfo
$processStartInfo.FileName = $fileName
$processStartInfo.Arguments = $adapterArguments
$processStartInfo.WorkingDirectory = [string]$processContract.working_directory
$processStartInfo.UseShellExecute = [bool]$processContract.use_shell_execute
$processStartInfo.RedirectStandardInput = [bool]$processContract.redirect_standard_input
$processStartInfo.RedirectStandardOutput = [bool]$processContract.redirect_standard_output
$processStartInfo.RedirectStandardError = [bool]$processContract.redirect_standard_error
$processStartInfo.CreateNoWindow = [bool]$processContract.create_no_window
$processStartInfo.EnvironmentVariables['HGRAG_EXPECTED_PACKAGE_COMMIT'] = $ExpectedPackageCommit
$processStartInfo.EnvironmentVariables['HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT'] = $ExpectedApprovalGovernance

$adapterProcess = New-Object Diagnostics.Process
$adapterProcess.StartInfo = $processStartInfo
try { $started = $adapterProcess.Start() }
catch { $adapterProcess.Dispose(); throw }
if (-not $started) { $adapterProcess.Dispose(); throw 'PRE adapter Process.Start returned false' }
$stdoutBuffer = New-Object IO.MemoryStream
$stderrBuffer = New-Object IO.MemoryStream
$stdoutDrain = $adapterProcess.StandardOutput.BaseStream.CopyToAsync($stdoutBuffer)
$stderrDrain = $adapterProcess.StandardError.BaseStream.CopyToAsync($stderrBuffer)
$adapterProcess.WaitForExit()
[Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($stdoutDrain, $stderrDrain))
$adapterExitCode = [int]$adapterProcess.ExitCode
[byte[]]$adapterStdoutBytes = $stdoutBuffer.ToArray()
[byte[]]$adapterStderrBytes = $stderrBuffer.ToArray()
$adapterProcess.Dispose()
$stdoutBuffer.Dispose()
$stderrBuffer.Dispose()

# No hash, classification, helper dispatch, or serializer is allowed between
# raw byte materialization above and completion of this CreateNew record.
[byte[]]$magic = $Ascii.GetBytes('HGRAGA16')
[uint32]$formatVersion = 1
[uint32]$headerBytes = 48
[uint32]$layerCode = [uint32]$adapterLayer.layer_code
[uint32]$completionFlags = 15
[uint32]$reserved = 0
[uint64]$stdoutLength = [uint64]$adapterStdoutBytes.Length
[uint64]$stderrLength = [uint64]$adapterStderrBytes.Length
$rawStream = New-Object IO.FileStream($adapterRawPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
try {
    $rawStream.Write($magic, 0, $magic.Length)
    [byte[]]$field = [BitConverter]::GetBytes($formatVersion); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($headerBytes); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($layerCode); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($completionFlags); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($adapterExitCode); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($reserved); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($stdoutLength); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($stderrLength); $rawStream.Write($field, 0, $field.Length)
    $rawStream.Write($adapterStdoutBytes, 0, $adapterStdoutBytes.Length)
    $rawStream.Write($adapterStderrBytes, 0, $adapterStderrBytes.Length)
    $rawStream.Flush($true)
}
finally { $rawStream.Dispose() }

if ($adapterExitCode -ne 0) { throw ('PRE adapter nonzero exit: ' + $adapterExitCode) }
$expectedAdapterStdout = $Utf8.GetBytes([string]$adapter.fixed_success_stdout)
if ($adapterStdoutBytes.Length -ne [int]$adapter.fixed_success_stdout_bytes -or (Get-ExactSha256Hex $adapterStdoutBytes) -cne [string]$adapter.fixed_success_stdout_sha256) { throw 'PRE nested adapter stdout identity mismatch' }
Assert-ExactBytes $adapterStdoutBytes $expectedAdapterStdout 'PRE nested adapter stdout'
$adapterStderrClass = Get-RegisteredPowerShellStderrClass $adapterStderrBytes $manifest.transport_base_frozen_stderr
if ($null -eq $adapterStderrClass) { throw 'PRE nested adapter stderr is not registered' }

$successBytes = $Utf8.GetBytes([string]$self.fixed_success_stdout)
if ($successBytes.Length -ne [int]$self.fixed_success_stdout_bytes -or (Get-ExactSha256Hex $successBytes) -cne [string]$self.fixed_success_stdout_sha256) { throw 'PRE nested capture-host success stdout identity mismatch' }
$standardOutput = [Console]::OpenStandardOutput()
$standardOutput.Write($successBytes, 0, $successBytes.Length)
$standardOutput.Flush()
