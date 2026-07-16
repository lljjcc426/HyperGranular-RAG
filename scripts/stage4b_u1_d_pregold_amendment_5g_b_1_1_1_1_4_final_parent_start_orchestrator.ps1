$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$CorrectedManifestRelativePath = 'docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4_MANIFEST.json'
$ExpectedRequestId = 'STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_4'
$ExpectedPackageRevision = 'CORRECTED_AFTER_PACKAGE_REVIEW_1'
$ExpectedDescriptor = 'QUOTED_FILE_NAME_SPACE_ARGUMENTS_TERMINAL_NULL'
$Utf8 = New-Object Text.UTF8Encoding($false, $true)
$Ascii = New-Object Text.ASCIIEncoding

function Get-Sha256Hex([byte[]]$Bytes) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace('-', '') }
    finally { $sha.Dispose() }
}

function Assert-ExactBytes([byte[]]$Actual, [byte[]]$Expected, [string]$Label) {
    if ($Actual.Length -ne $Expected.Length) { throw ($Label + ' length mismatch') }
    for ($i = 0; $i -lt $Expected.Length; $i++) {
        if ($Actual[$i] -ne $Expected[$i]) { throw ($Label + ' byte mismatch at ' + $i) }
    }
}

function Assert-AsciiText([string]$Value, [string]$Label) {
    foreach ($character in $Value.ToCharArray()) {
        if ([int]$character -gt 127) { throw ($Label + ' contains non-ASCII data') }
    }
}

function Get-RegisteredPowerShellStderrClass([byte[]]$Actual, $Frozen) {
    if ($Actual.Length -eq 0) { return 'EMPTY' }
    if ($Actual.Length -ne [int]$Frozen.bytes -or (Get-Sha256Hex $Actual) -cne [string]$Frozen.sha256) { return $null }
    Assert-ExactBytes $Actual ([Convert]::FromBase64String([string]$Frozen.base64)) 'FINAL verifier stderr'
    return 'EXACT_FROZEN_382_BYTE_STARTUP_CLIXML'
}

function Assert-Binding([string]$Value, [string]$Label) {
    if ($Value -cnotmatch '\A[0-9a-f]{40}\z') { throw ($Label + ' is missing or invalid') }
}

$ExpectedPackageCommit = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_PACKAGE_COMMIT', [EnvironmentVariableTarget]::Process)
$ExpectedApprovalGovernance = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT', [EnvironmentVariableTarget]::Process)
$ExpectedSemanticsEvidence = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_SEMANTICS_EVIDENCE_COMMIT', [EnvironmentVariableTarget]::Process)
$ExpectedPostSyncAudit = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_POST_SYNC_AUDIT_COMMIT', [EnvironmentVariableTarget]::Process)
Assert-Binding $ExpectedPackageCommit 'Expected package commit'
Assert-Binding $ExpectedApprovalGovernance 'Expected approval-governance commit'
Assert-Binding $ExpectedSemanticsEvidence 'Expected semantics-evidence commit'
Assert-Binding $ExpectedPostSyncAudit 'Expected post-sync audit commit'

$RepositoryRoot = (Resolve-Path -LiteralPath '.').Path
$correctedManifestBytes = [IO.File]::ReadAllBytes((Join-Path $RepositoryRoot $CorrectedManifestRelativePath))
$manifest = ConvertFrom-Json -InputObject ($Utf8.GetString($correctedManifestBytes))
if ([string]$manifest.request_id -cne $ExpectedRequestId -or [string]$manifest.package_revision -cne $ExpectedPackageRevision) { throw 'Corrected Manifest identity mismatch' }
$baseBytes = [IO.File]::ReadAllBytes((Join-Path $RepositoryRoot ([string]$manifest.base_manifest.path)))
if ($baseBytes.Length -ne [int]$manifest.base_manifest.bytes -or (Get-Sha256Hex $baseBytes) -cne [string]$manifest.base_manifest.sha256) { throw 'Base Manifest identity mismatch' }
$baseManifest = ConvertFrom-Json -InputObject ($Utf8.GetString($baseBytes))

$contract = $manifest.adapter_invocation_contract
if ([string]$contract.modeled_command_descriptor -cne $ExpectedDescriptor) { throw 'FINAL modeled command descriptor mismatch' }
$fileName = [string]$contract.file_name
if ($fileName -cne 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe') { throw 'FINAL executable path mismatch' }
if ([string]$contract.working_directory -cne $RepositoryRoot) { throw 'FINAL working directory mismatch' }
if ([bool]$contract.use_shell_execute -or [bool]$contract.redirect_standard_input -or -not [bool]$contract.redirect_standard_output -or -not [bool]$contract.redirect_standard_error -or -not [bool]$contract.create_no_window) { throw 'FINAL redirect or window contract mismatch' }

$verifier = $manifest.terminal_adapter_attestation_commit_verifier
$sourceBytes = [IO.File]::ReadAllBytes((Join-Path $RepositoryRoot ([string]$verifier.path)))
if ($sourceBytes.Length -ne [int]$verifier.source_bytes -or (Get-Sha256Hex $sourceBytes) -cne [string]$verifier.source_sha256) { throw 'FINAL verifier source identity mismatch' }
$source = $Utf8.GetString($sourceBytes)
Assert-AsciiText $source 'FINAL verifier source'
$tokens = $null
$errors = $null
[void][Management.Automation.Language.Parser]::ParseInput($source, [ref]$tokens, [ref]$errors)
if ($errors.Count -ne [int]$verifier.static_parse_errors) { throw 'FINAL verifier parser identity mismatch' }

$invocation = $verifier.pre_attestation_invocation
$arguments = [string]$invocation.complete_arguments
Assert-AsciiText $arguments 'FINAL verifier complete arguments'
if ($arguments.Length -ne [int]$invocation.complete_arguments_characters -or (Get-Sha256Hex $Ascii.GetBytes($arguments)) -cne [string]$invocation.complete_arguments_ascii_sha256) { throw 'FINAL verifier arguments identity mismatch' }
$modeled = '"' + $fileName + '" ' + $arguments + [char]0
Assert-AsciiText $modeled 'FINAL verifier modeled command'
if ($modeled.Length -ne [int]$invocation.modeled_command_characters_including_terminal_null -or (Get-Sha256Hex $Ascii.GetBytes($modeled)) -cne [string]$invocation.modeled_command_ascii_sha256_including_terminal_null) { throw 'FINAL verifier modeled command identity mismatch' }

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
$psi.EnvironmentVariables['HGRAG_EXPECTED_POST_SYNC_AUDIT_COMMIT'] = $ExpectedPostSyncAudit

$process = New-Object Diagnostics.Process
$process.StartInfo = $psi
try { $started = $process.Start() }
catch { $process.Dispose(); throw }
if (-not $started) { $process.Dispose(); throw 'FINAL verifier Process.Start returned false' }
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
if ($exitCode -ne 0) { throw ('FINAL verifier nonzero exit: ' + $exitCode) }
$expectedStdout = $Utf8.GetBytes([string]$invocation.fixed_success_stdout)
if ($stdoutBytes.Length -ne [int]$invocation.fixed_success_stdout_bytes -or (Get-Sha256Hex $stdoutBytes) -cne [string]$invocation.fixed_success_stdout_sha256) { throw 'FINAL verifier stdout identity mismatch' }
Assert-ExactBytes $stdoutBytes $expectedStdout 'FINAL verifier stdout'
$parentStderrClass = Get-RegisteredPowerShellStderrClass $stderrBytes $baseManifest.frozen_powershell_startup_stderr
if ($null -eq $parentStderrClass) { throw 'FINAL verifier stderr is not registered' }

$success = '{"status":"FINAL_PARENT_START_ORCHESTRATOR_VERIFIED","parent_processes":1,"parent_stdout_registered":true,"parent_stderr_class":"' + $parentStderrClass + '","schema_semantics_bound":true}'
$successBytes = $Utf8.GetBytes($success)
$standardOutput = [Console]::OpenStandardOutput()
$standardOutput.Write($successBytes, 0, $successBytes.Length)
$standardOutput.Flush()
