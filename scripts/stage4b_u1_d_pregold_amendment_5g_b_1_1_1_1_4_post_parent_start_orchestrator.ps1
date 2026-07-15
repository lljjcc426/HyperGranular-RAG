$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ExpectedDescriptor = 'QUOTED_FILE_NAME_SPACE_ARGUMENTS_TERMINAL_NULL'
$ExpectedFileName = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$ExpectedBaseManifestBytes = 323607
$ExpectedBaseManifestSha256 = '804B4F8607532D6CE17EDE043D5A9511C7E855F4EB444C25F461381B6EDDA73D'
$BaseManifestRelativePath = 'docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3_MANIFEST.json'
$ArgumentPrefix = '-NoLogo -NoProfile -NonInteractive -EncodedCommand '
$Utf8 = New-Object Text.UTF8Encoding($false, $true)
$Ascii = New-Object Text.ASCIIEncoding
$Unicode = New-Object Text.UnicodeEncoding($false, $false, $true)

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

function Assert-AsciiText([string]$Text, [string]$Label) {
    foreach ($character in $Text.ToCharArray()) {
        if ([int]$character -gt 127) { throw ($Label + ' contains non-ASCII character') }
    }
}

function Test-RegisteredStdout([byte[]]$Actual, $Variants) {
    foreach ($variant in $Variants) {
        $expected = $Utf8.GetBytes([string]$variant.stdout)
        if ($Actual.Length -eq [int]$variant.stdout_bytes -and (Get-Sha256Hex $Actual) -ceq [string]$variant.stdout_sha256) {
            Assert-ExactBytes $Actual $expected 'Parent stdout'
            return $true
        }
    }
    return $false
}

function Test-RegisteredPowerShellStderr([byte[]]$Actual, $Frozen) {
    if ($Actual.Length -eq 0) { return $true }
    if ($Actual.Length -ne [int]$Frozen.bytes -or (Get-Sha256Hex $Actual) -cne [string]$Frozen.sha256) { return $false }
    Assert-ExactBytes $Actual ([Convert]::FromBase64String([string]$Frozen.base64)) 'Parent stderr'
    return $true
}

$ExpectedPackageCommit = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_PACKAGE_COMMIT', [EnvironmentVariableTarget]::Process)
$ExpectedApprovalGovernance = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT', [EnvironmentVariableTarget]::Process)
$ExpectedSemanticsEvidence = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_SEMANTICS_EVIDENCE_COMMIT', [EnvironmentVariableTarget]::Process)
foreach ($binding in @($ExpectedPackageCommit, $ExpectedApprovalGovernance, $ExpectedSemanticsEvidence)) {
    if ($binding -cnotmatch '\A[0-9a-f]{40}\z') { throw 'Expected POST orchestration commit binding is missing or invalid' }
}

$RepositoryRoot = (Resolve-Path -LiteralPath '.').Path
$BaseManifestPath = Join-Path $RepositoryRoot $BaseManifestRelativePath
$manifestBytes = [IO.File]::ReadAllBytes($BaseManifestPath)
if ($manifestBytes.Length -ne $ExpectedBaseManifestBytes -or (Get-Sha256Hex $manifestBytes) -cne $ExpectedBaseManifestSha256) { throw 'Base Manifest identity mismatch' }
$manifest = ConvertFrom-Json -InputObject ($Utf8.GetString($manifestBytes))
if ($manifest.request_id -cne 'STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_3') { throw 'Base Manifest request identity mismatch' }

$contract = $manifest.process_start_info_contract
$parent = $manifest.post_sync_stdin_transport_host
if ([string]$parent.modeled_createprocess_command_line -cne $ExpectedDescriptor) { throw 'POST modeled command descriptor mismatch' }
$fileName = [string]$contract.file_name
if ($fileName -cne $ExpectedFileName) { throw 'POST executable path mismatch' }
foreach ($forbidden in @([string]$parent.runtime, [string]$parent.host_name, [string]$parent.transport_role)) {
    if (-not [string]::IsNullOrEmpty($forbidden) -and $fileName -ceq $forbidden) { throw 'POST executable path came from a forbidden label field' }
}
if ([string]$contract.working_directory -cne $RepositoryRoot) { throw 'POST working directory mismatch' }
if ([bool]$contract.use_shell_execute -or -not [bool]$contract.redirect_standard_input -or -not [bool]$contract.redirect_standard_output -or -not [bool]$contract.redirect_standard_error -or -not [bool]$contract.create_no_window) { throw 'POST redirect or window contract mismatch' }

$sourceLines = [string[]]$parent.source_lines
if ($sourceLines.Length -ne [int]$parent.source_line_count) { throw 'POST parent source line-count mismatch' }
$source = [string]::Join("`n", $sourceLines)
if ($source.EndsWith("`n")) { throw 'POST parent source trailing-newline mismatch' }
$sourceBytes = $Utf8.GetBytes($source)
if ($sourceBytes.Length -ne [int]$parent.source_utf8_bytes -or (Get-Sha256Hex $sourceBytes) -cne [string]$parent.source_sha256) { throw 'POST parent source identity mismatch' }
$tokens = $null
$parseErrors = $null
[void][Management.Automation.Language.Parser]::ParseInput($source, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count -ne 0 -or [int]$parent.static_parse_errors -ne 0) { throw 'POST parent parser mismatch' }

$encodedSource = [Convert]::ToBase64String($Unicode.GetBytes($source))
$arguments = $ArgumentPrefix + $encodedSource
Assert-AsciiText $arguments 'POST complete arguments'
$argumentBytes = $Ascii.GetBytes($arguments)
if ($arguments -cne [string]$parent.complete_arguments -or $arguments.Length -ne [int]$parent.complete_arguments_characters -or (Get-Sha256Hex $argumentBytes) -cne [string]$parent.complete_arguments_ascii_sha256) { throw 'POST complete-arguments identity mismatch' }

$modeledCommandLine = '"' + $fileName + '" ' + $arguments + [char]0
Assert-AsciiText $modeledCommandLine 'POST modeled command line'
$modeledBytes = $Ascii.GetBytes($modeledCommandLine)
if ($modeledCommandLine.Length -ne [int]$parent.modeled_createprocess_characters_including_terminal_null -or (Get-Sha256Hex $modeledBytes) -cne [string]$parent.modeled_createprocess_ascii_sha256_including_terminal_null) { throw 'POST modeled command-line identity mismatch' }

$psi = New-Object Diagnostics.ProcessStartInfo
$psi.FileName = $fileName
$psi.Arguments = $arguments
$psi.WorkingDirectory = [string]$contract.working_directory
$psi.UseShellExecute = [bool]$contract.use_shell_execute
$psi.RedirectStandardInput = [bool]$contract.redirect_standard_input
$psi.RedirectStandardOutput = [bool]$contract.redirect_standard_output
$psi.RedirectStandardError = [bool]$contract.redirect_standard_error
$psi.CreateNoWindow = [bool]$contract.create_no_window
$psi.EnvironmentVariables['HGRAG_EXPECTED_PACKAGE_COMMIT'] = $ExpectedPackageCommit
$psi.EnvironmentVariables['HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT'] = $ExpectedApprovalGovernance
$psi.EnvironmentVariables['HGRAG_EXPECTED_SEMANTICS_EVIDENCE_COMMIT'] = $ExpectedSemanticsEvidence

$process = New-Object Diagnostics.Process
$process.StartInfo = $psi
try { $started = $process.Start() }
catch { $process.Dispose(); throw }
if (-not $started) { $process.Dispose(); throw 'POST parent Process.Start returned false' }
$stdoutBuffer = New-Object IO.MemoryStream
$stderrBuffer = New-Object IO.MemoryStream
$stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync($stdoutBuffer)
$stderrTask = $process.StandardError.BaseStream.CopyToAsync($stderrBuffer)
$process.StandardInput.BaseStream.Close()
$process.WaitForExit()
[Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($stdoutTask, $stderrTask))
$exitCode = $process.ExitCode
$stdoutBytes = [byte[]]$stdoutBuffer.ToArray()
$stderrBytes = [byte[]]$stderrBuffer.ToArray()
$process.Dispose()
$stdoutBuffer.Dispose()
$stderrBuffer.Dispose()
if ($exitCode -ne 0) { throw ('POST parent nonzero exit: ' + $exitCode) }
if (-not (Test-RegisteredStdout $stdoutBytes $parent.success_stdout_variants)) { throw 'POST parent stdout is not registered' }
if (-not (Test-RegisteredPowerShellStderr $stderrBytes $manifest.frozen_powershell_startup_stderr)) { throw 'POST parent stderr is not registered' }

$success = '{"status":"POST_PARENT_START_ORCHESTRATOR_VERIFIED","parent_processes":1,"parent_stdout_registered":true,"parent_stderr_registered":true,"schema_semantics_bound":true}'
$successBytes = $Utf8.GetBytes($success)
$standardOutput = [Console]::OpenStandardOutput()
$standardOutput.Write($successBytes, 0, $successBytes.Length)
$standardOutput.Flush()
