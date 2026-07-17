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
    Assert-ExactBytes $Actual ([Convert]::FromBase64String([string]$Frozen.base64)) 'Parent stderr'
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

$self = $manifest.pre_nested_adapter
$parent = $manifest.pre_nested_parent
Assert-RegisteredSource $self $RepositoryRoot 'PRE nested adapter'
Assert-RegisteredSource $parent $RepositoryRoot 'PRE nested parent'
$fileName = [string]$manifest.process_start_info_contract.file_name
$selfArguments = [string]$self.complete_arguments
$selfModeled = '"' + $fileName + '" ' + $selfArguments + [char]0
if ($selfArguments.Length -ne [int]$self.complete_arguments_characters -or (Get-ExactSha256Hex $Ascii.GetBytes($selfArguments)) -cne [string]$self.complete_arguments_ascii_sha256) { throw 'PRE nested adapter arguments mismatch' }
if ($selfModeled.Length -ne [int]$self.modeled_command_characters_including_terminal_null -or (Get-ExactSha256Hex $Ascii.GetBytes($selfModeled)) -cne [string]$self.modeled_command_ascii_sha256_including_terminal_null) { throw 'PRE nested adapter modeled command mismatch' }
if (([Environment]::CommandLine + [char]0) -cne $selfModeled) { throw 'PRE nested adapter actual process command line mismatch' }

$parentArguments = [string]$parent.complete_arguments
$parentModeled = '"' + $fileName + '" ' + $parentArguments + [char]0
if ($parentArguments.Length -ne [int]$parent.complete_arguments_characters -or (Get-ExactSha256Hex $Ascii.GetBytes($parentArguments)) -cne [string]$parent.complete_arguments_ascii_sha256) { throw 'PRE nested parent arguments mismatch' }
if ($parentModeled.Length -ne [int]$parent.modeled_command_characters_including_terminal_null -or (Get-ExactSha256Hex $Ascii.GetBytes($parentModeled)) -cne [string]$parent.modeled_command_ascii_sha256_including_terminal_null) { throw 'PRE nested parent modeled command mismatch' }

$parentLayer = Get-RawLayer $manifest 'PARENT_CHILD'
$parentRawPath = Join-Path $RepositoryRoot ([string]$parentLayer.repository_path)
if ([IO.File]::Exists($parentRawPath) -or [IO.Directory]::Exists($parentRawPath)) { throw 'PRE parent raw path collision' }

$processContract = $manifest.process_start_info_contract
$processStartInfo = New-Object Diagnostics.ProcessStartInfo
$processStartInfo.FileName = $fileName
$processStartInfo.Arguments = $parentArguments
$processStartInfo.WorkingDirectory = [string]$processContract.working_directory
$processStartInfo.UseShellExecute = [bool]$processContract.use_shell_execute
$processStartInfo.RedirectStandardInput = [bool]$processContract.redirect_standard_input
$processStartInfo.RedirectStandardOutput = [bool]$processContract.redirect_standard_output
$processStartInfo.RedirectStandardError = [bool]$processContract.redirect_standard_error
$processStartInfo.CreateNoWindow = [bool]$processContract.create_no_window
$processStartInfo.EnvironmentVariables['HGRAG_EXPECTED_PACKAGE_COMMIT'] = $ExpectedPackageCommit
$processStartInfo.EnvironmentVariables['HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT'] = $ExpectedApprovalGovernance

$parentProcess = New-Object Diagnostics.Process
$parentProcess.StartInfo = $processStartInfo
try { $started = $parentProcess.Start() }
catch { $parentProcess.Dispose(); throw }
if (-not $started) { $parentProcess.Dispose(); throw 'PRE parent Process.Start returned false' }
$stdoutBuffer = New-Object IO.MemoryStream
$stderrBuffer = New-Object IO.MemoryStream
$stdoutDrain = $parentProcess.StandardOutput.BaseStream.CopyToAsync($stdoutBuffer)
$stderrDrain = $parentProcess.StandardError.BaseStream.CopyToAsync($stderrBuffer)
$parentProcess.WaitForExit()
[Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($stdoutDrain, $stderrDrain))
$parentExitCode = [int]$parentProcess.ExitCode
[byte[]]$parentStdoutBytes = $stdoutBuffer.ToArray()
[byte[]]$parentStderrBytes = $stderrBuffer.ToArray()
$parentProcess.Dispose()
$stdoutBuffer.Dispose()
$stderrBuffer.Dispose()

# No hash, classification, helper dispatch, or serializer is allowed between
# raw byte materialization above and completion of this CreateNew record.
[byte[]]$magic = $Ascii.GetBytes('HGRAGP16')
[uint32]$formatVersion = 1
[uint32]$headerBytes = 48
[uint32]$layerCode = [uint32]$parentLayer.layer_code
[uint32]$completionFlags = 15
[uint32]$reserved = 0
[uint64]$stdoutLength = [uint64]$parentStdoutBytes.Length
[uint64]$stderrLength = [uint64]$parentStderrBytes.Length
$rawStream = New-Object IO.FileStream($parentRawPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
try {
    $rawStream.Write($magic, 0, $magic.Length)
    [byte[]]$field = [BitConverter]::GetBytes($formatVersion); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($headerBytes); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($layerCode); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($completionFlags); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($parentExitCode); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($reserved); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($stdoutLength); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($stderrLength); $rawStream.Write($field, 0, $field.Length)
    $rawStream.Write($parentStdoutBytes, 0, $parentStdoutBytes.Length)
    $rawStream.Write($parentStderrBytes, 0, $parentStderrBytes.Length)
    $rawStream.Flush($true)
}
finally { $rawStream.Dispose() }

if ($parentExitCode -ne 0) { throw ('PRE parent nonzero exit: ' + $parentExitCode) }
$expectedParentStdout = $Utf8.GetBytes([string]$parent.fixed_success_stdout)
if ($parentStdoutBytes.Length -ne [int]$parent.fixed_success_stdout_bytes -or (Get-ExactSha256Hex $parentStdoutBytes) -cne [string]$parent.fixed_success_stdout_sha256) { throw 'PRE nested parent stdout identity mismatch' }
Assert-ExactBytes $parentStdoutBytes $expectedParentStdout 'PRE nested parent stdout'
$parentStderrClass = Get-RegisteredPowerShellStderrClass $parentStderrBytes $manifest.transport_base_frozen_stderr
if ($null -eq $parentStderrClass) { throw 'PRE nested parent stderr is not registered' }

$successBytes = $Utf8.GetBytes([string]$self.fixed_success_stdout)
if ($successBytes.Length -ne [int]$self.fixed_success_stdout_bytes -or (Get-ExactSha256Hex $successBytes) -cne [string]$self.fixed_success_stdout_sha256) { throw 'PRE nested adapter success stdout identity mismatch' }
$standardOutput = [Console]::OpenStandardOutput()
$standardOutput.Write($successBytes, 0, $successBytes.Length)
$standardOutput.Flush()
