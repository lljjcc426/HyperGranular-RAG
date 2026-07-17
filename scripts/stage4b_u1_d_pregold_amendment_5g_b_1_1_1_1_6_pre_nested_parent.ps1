$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ManifestRelativePath = 'docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6_MANIFEST.json'
$ExpectedRequestId = 'STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_6'
$ExpectedPackageRevision = 'NESTED_DURABLE_RESULT_CAPTURE_PRE_ONLY_DIAGNOSTIC'
$Utf8 = New-Object Text.UTF8Encoding($false, $true)
$Ascii = New-Object Text.ASCIIEncoding
$Unicode = New-Object Text.UnicodeEncoding($false, $false, $true)

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
    Assert-ExactBytes $Actual ([Convert]::FromBase64String([string]$Frozen.base64)) 'Loader stderr'
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

$self = $manifest.pre_nested_parent
Assert-RegisteredSource $self $RepositoryRoot 'PRE nested parent'
$fileName = [string]$manifest.process_start_info_contract.file_name
$arguments = [string]$self.complete_arguments
$modeled = '"' + $fileName + '" ' + $arguments + [char]0
if ($arguments.Length -ne [int]$self.complete_arguments_characters -or (Get-ExactSha256Hex $Ascii.GetBytes($arguments)) -cne [string]$self.complete_arguments_ascii_sha256) { throw 'PRE nested parent arguments mismatch' }
if ($modeled.Length -ne [int]$self.modeled_command_characters_including_terminal_null -or (Get-ExactSha256Hex $Ascii.GetBytes($modeled)) -cne [string]$self.modeled_command_ascii_sha256_including_terminal_null) { throw 'PRE nested parent modeled command mismatch' }
if (([Environment]::CommandLine + [char]0) -cne $modeled) { throw 'PRE nested parent actual process command line mismatch' }

$basePath = Join-Path $RepositoryRoot ([string]$manifest.transport_base_manifest.path)
$baseBytes = [IO.File]::ReadAllBytes($basePath)
if ($baseBytes.Length -ne [int]$manifest.transport_base_manifest.bytes -or (Get-ExactSha256Hex $baseBytes) -cne [string]$manifest.transport_base_manifest.sha256) { throw 'Transport base Manifest identity mismatch' }
$baseManifest = ConvertFrom-Json -InputObject ($Utf8.GetString($baseBytes))
$loader = $baseManifest.pre_and_semantics_stdin_loader
$target = $baseManifest.pre_and_semantics_target
$frozenStderr = $baseManifest.frozen_powershell_startup_stderr

$loaderSource = [string]::Join([char]10, [string[]]@($loader.source_lines))
$loaderSourceBytes = $Utf8.GetBytes($loaderSource)
if ($loaderSourceBytes.Length -ne [int]$loader.source_utf8_bytes -or (Get-ExactSha256Hex $loaderSourceBytes) -cne [string]$loader.source_sha256) { throw 'PRE loader source identity mismatch' }
$loaderTokens = $null
$loaderErrors = $null
[void][Management.Automation.Language.Parser]::ParseInput($loaderSource, [ref]$loaderTokens, [ref]$loaderErrors)
if ($loaderErrors.Count -ne [int]$loader.static_parse_errors) { throw 'PRE loader parser identity mismatch' }
$loaderArguments = '-NoLogo -NoProfile -NonInteractive -EncodedCommand ' + [Convert]::ToBase64String($Unicode.GetBytes($loaderSource))
if ($loaderArguments.Length -ne [int]$loader.complete_arguments_characters -or (Get-ExactSha256Hex $Ascii.GetBytes($loaderArguments)) -cne [string]$loader.complete_arguments_ascii_sha256) { throw 'PRE loader arguments mismatch' }
$loaderModeled = '"' + $fileName + '" ' + $loaderArguments + [char]0
if ($loaderModeled.Length -ne [int]$loader.modeled_createprocess_characters_including_terminal_null -or (Get-ExactSha256Hex $Ascii.GetBytes($loaderModeled)) -cne [string]$loader.modeled_createprocess_ascii_sha256_including_terminal_null) { throw 'PRE loader modeled command mismatch' }

$targetSource = [string]::Join([char]10, [string[]]@($target.source_lines))
$targetSourceBytes = $Utf8.GetBytes($targetSource)
if ($targetSourceBytes.Length -ne [int]$target.source_utf8_bytes -or (Get-ExactSha256Hex $targetSourceBytes) -cne [string]$target.source_sha256) { throw 'PRE target source identity mismatch' }
$targetTokens = $null
$targetErrors = $null
[void][Management.Automation.Language.Parser]::ParseInput($targetSource, [ref]$targetTokens, [ref]$targetErrors)
if ($targetErrors.Count -ne [int]$target.static_parse_errors) { throw 'PRE target parser identity mismatch' }
$payloadBytes = $Ascii.GetBytes([Convert]::ToBase64String($Unicode.GetBytes($targetSource)))
if ($payloadBytes.Length -ne [int]$target.stdin_payload.ascii_bytes -or (Get-ExactSha256Hex $payloadBytes) -cne [string]$target.stdin_payload.ascii_sha256) { throw 'PRE target stdin payload mismatch' }

foreach ($path in @($manifest.pre_diagnostic_paths.semantics_narrative, $manifest.pre_diagnostic_paths.semantics_machine)) {
    $absolute = Join-Path $RepositoryRoot ([string]$path)
    if ([IO.File]::Exists($absolute) -or [IO.Directory]::Exists($absolute)) { throw ('PRE semantics path collision: ' + $path) }
}
$loaderLayer = Get-RawLayer $manifest 'LOADER_CHILD'
$loaderRawPath = Join-Path $RepositoryRoot ([string]$loaderLayer.repository_path)
if ([IO.File]::Exists($loaderRawPath) -or [IO.Directory]::Exists($loaderRawPath)) { throw 'PRE loader raw path collision' }

$processContract = $manifest.process_start_info_contract
$processStartInfo = New-Object Diagnostics.ProcessStartInfo
$processStartInfo.FileName = $fileName
$processStartInfo.Arguments = $loaderArguments
$processStartInfo.WorkingDirectory = [string]$processContract.working_directory
$processStartInfo.UseShellExecute = [bool]$processContract.use_shell_execute
$processStartInfo.RedirectStandardInput = $true
$processStartInfo.RedirectStandardOutput = $true
$processStartInfo.RedirectStandardError = $true
$processStartInfo.CreateNoWindow = [bool]$processContract.create_no_window
$processStartInfo.EnvironmentVariables['HGRAG_EXPECTED_PACKAGE_COMMIT'] = $ExpectedPackageCommit
$processStartInfo.EnvironmentVariables['HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT'] = $ExpectedApprovalGovernance

$loaderProcess = New-Object Diagnostics.Process
$loaderProcess.StartInfo = $processStartInfo
try { $started = $loaderProcess.Start() }
catch { $loaderProcess.Dispose(); throw }
if (-not $started) { $loaderProcess.Dispose(); throw 'PRE loader Process.Start returned false' }
$stdoutBuffer = New-Object IO.MemoryStream
$stderrBuffer = New-Object IO.MemoryStream
$stdoutDrain = $loaderProcess.StandardOutput.BaseStream.CopyToAsync($stdoutBuffer)
$stderrDrain = $loaderProcess.StandardError.BaseStream.CopyToAsync($stderrBuffer)
$stdinStream = $loaderProcess.StandardInput.BaseStream
$stdinStream.Write($payloadBytes, 0, $payloadBytes.Length)
$stdinStream.Flush()
$stdinStream.Close()
$loaderProcess.WaitForExit()
[Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($stdoutDrain, $stderrDrain))
$loaderExitCode = [int]$loaderProcess.ExitCode
[byte[]]$loaderStdoutBytes = $stdoutBuffer.ToArray()
[byte[]]$loaderStderrBytes = $stderrBuffer.ToArray()
$loaderProcess.Dispose()
$stdoutBuffer.Dispose()
$stderrBuffer.Dispose()

# No hash, classification, helper dispatch, or serializer is allowed between
# raw byte materialization above and completion of this CreateNew record.
[byte[]]$magic = $Ascii.GetBytes('HGRAGL16')
[uint32]$formatVersion = 1
[uint32]$headerBytes = 48
[uint32]$layerCode = [uint32]$loaderLayer.layer_code
[uint32]$completionFlags = 15
[uint32]$reserved = 0
[uint64]$stdoutLength = [uint64]$loaderStdoutBytes.Length
[uint64]$stderrLength = [uint64]$loaderStderrBytes.Length
$rawStream = New-Object IO.FileStream($loaderRawPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
try {
    $rawStream.Write($magic, 0, $magic.Length)
    [byte[]]$field = [BitConverter]::GetBytes($formatVersion); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($headerBytes); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($layerCode); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($completionFlags); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($loaderExitCode); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($reserved); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($stdoutLength); $rawStream.Write($field, 0, $field.Length)
    [byte[]]$field = [BitConverter]::GetBytes($stderrLength); $rawStream.Write($field, 0, $field.Length)
    $rawStream.Write($loaderStdoutBytes, 0, $loaderStdoutBytes.Length)
    $rawStream.Write($loaderStderrBytes, 0, $loaderStderrBytes.Length)
    $rawStream.Flush($true)
}
finally { $rawStream.Dispose() }

if ($loaderExitCode -ne 0) { throw ('PRE loader nonzero exit: ' + $loaderExitCode) }
$expectedLoaderStdout = $Utf8.GetBytes([string]$target.fixed_success_stdout)
if ($loaderStdoutBytes.Length -ne [int]$target.fixed_success_stdout_bytes -or (Get-ExactSha256Hex $loaderStdoutBytes) -cne [string]$target.fixed_success_stdout_sha256) { throw 'PRE loader stdout identity mismatch' }
Assert-ExactBytes $loaderStdoutBytes $expectedLoaderStdout 'PRE loader stdout'
$loaderStderrClass = Get-RegisteredPowerShellStderrClass $loaderStderrBytes $frozenStderr
if ($null -eq $loaderStderrClass) { throw 'PRE loader stderr is not registered' }

$successBytes = $Utf8.GetBytes([string]$self.fixed_success_stdout)
if ($successBytes.Length -ne [int]$self.fixed_success_stdout_bytes -or (Get-ExactSha256Hex $successBytes) -cne [string]$self.fixed_success_stdout_sha256) { throw 'PRE nested parent success stdout identity mismatch' }
$standardOutput = [Console]::OpenStandardOutput()
$standardOutput.Write($successBytes, 0, $successBytes.Length)
$standardOutput.Flush()
