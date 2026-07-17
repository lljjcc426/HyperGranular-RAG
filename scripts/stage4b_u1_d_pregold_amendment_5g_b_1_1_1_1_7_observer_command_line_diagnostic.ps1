param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('COMMAND_LINE_DIAGNOSTIC')]
    [string]$Mode
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ManifestRelativePath = 'docs/STAGE4B_U1_PREGOLD_AMENDMENT_5G_B_1_1_1_1_7_MANIFEST.json'
$ExpectedRequestId = 'STAGE4B_U1_D_PREGOLD_AMENDMENT_5G_B_1_1_1_1_7'
$ExpectedPackageRevision = 'DURABLE_OBSERVER_COMMAND_LINE_OBSERVATION_EQUALITY_GATE_DIAGNOSTIC_ONLY'
$ExpectedFileName = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$ExpectedArguments = '-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_diagnostic.ps1" -Mode COMMAND_LINE_DIAGNOSTIC'
$ExpectedObservationPath = 'results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_observation.bin'
$Utf8 = New-Object Text.UTF8Encoding($false, $true)
$Utf16Le = New-Object Text.UnicodeEncoding($false, $false, $true)
$Ascii = New-Object Text.ASCIIEncoding

function Assert-CommitBinding([string]$Value, [string]$Label) {
    if ($Value -cnotmatch '\A[0-9a-f]{40}\z') { throw ($Label + ' is missing or invalid') }
}

function Write-UInt32LittleEndian([IO.Stream]$Stream, [uint32]$Value) {
    [byte[]]$bytes = [BitConverter]::GetBytes($Value)
    $Stream.Write($bytes, 0, $bytes.Length)
}

function Write-UInt64LittleEndian([IO.Stream]$Stream, [uint64]$Value) {
    [byte[]]$bytes = [BitConverter]::GetBytes($Value)
    $Stream.Write($bytes, 0, $bytes.Length)
}

if (-not [BitConverter]::IsLittleEndian) { throw 'Command-line observation requires a little-endian runtime' }

$ExpectedPackageCommit = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_PACKAGE_COMMIT', [EnvironmentVariableTarget]::Process)
$ExpectedApprovalGovernance = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT', [EnvironmentVariableTarget]::Process)
Assert-CommitBinding $ExpectedPackageCommit 'Expected package commit'
Assert-CommitBinding $ExpectedApprovalGovernance 'Expected approval-governance commit'

$RepositoryRoot = (Resolve-Path -LiteralPath '.').Path
$manifestPath = Join-Path $RepositoryRoot $ManifestRelativePath
$manifestBytes = [IO.File]::ReadAllBytes($manifestPath)
$manifest = ConvertFrom-Json -InputObject ($Utf8.GetString($manifestBytes))
if ([string]$manifest.request_id -cne $ExpectedRequestId) { throw 'Command-line diagnostic request identity mismatch' }
if ([string]$manifest.package_revision -cne $ExpectedPackageRevision) { throw 'Command-line diagnostic package revision mismatch' }
if ([string]$manifest.process_start_info_contract.file_name -cne $ExpectedFileName) { throw 'Registered executable mismatch' }
if ([string]$manifest.process_start_info_contract.working_directory -cne $RepositoryRoot) { throw 'Registered working directory mismatch' }

$observer = $manifest.command_line_diagnostic_observer
$registeredArguments = [string]$observer.invocation.complete_arguments
$registeredObservationPath = [string]$manifest.command_line_observation_contract.repository_path
if ($registeredArguments -cne $ExpectedArguments) { throw 'Registered observer arguments mismatch' }
if ($registeredObservationPath -cne $ExpectedObservationPath) { throw 'Registered observation path mismatch' }

$observationPath = Join-Path $RepositoryRoot $registeredObservationPath
if ([IO.File]::Exists($observationPath) -or [IO.Directory]::Exists($observationPath)) { throw 'Command-line observation path collision' }

$modeledCommandLine = '"' + $ExpectedFileName + '" ' + $registeredArguments + [char]0
$actualCommandLine = [Environment]::CommandLine

[byte[]]$actualBytes = $Utf16Le.GetBytes($actualCommandLine)
[byte[]]$modeledBytes = $Utf16Le.GetBytes($modeledCommandLine)
[byte[]]$fileNameBytes = $Utf16Le.GetBytes($ExpectedFileName)
[byte[]]$argumentsBytes = $Utf16Le.GetBytes($registeredArguments)

[byte[]]$magic = $Ascii.GetBytes('HGRAGC17')
[uint32]$formatVersion = 1
[uint32]$headerBytes = 88
[uint32]$completionFlags = 15
[uint32]$reserved = 0

$observationStream = New-Object IO.FileStream($observationPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
try {
    $observationStream.Write($magic, 0, $magic.Length)
    Write-UInt32LittleEndian $observationStream $formatVersion
    Write-UInt32LittleEndian $observationStream $headerBytes
    Write-UInt32LittleEndian $observationStream $completionFlags
    Write-UInt32LittleEndian $observationStream $reserved
    Write-UInt64LittleEndian $observationStream ([uint64]$actualCommandLine.Length)
    Write-UInt64LittleEndian $observationStream ([uint64]$modeledCommandLine.Length)
    Write-UInt64LittleEndian $observationStream ([uint64]$ExpectedFileName.Length)
    Write-UInt64LittleEndian $observationStream ([uint64]$registeredArguments.Length)
    Write-UInt64LittleEndian $observationStream ([uint64]$actualBytes.Length)
    Write-UInt64LittleEndian $observationStream ([uint64]$modeledBytes.Length)
    Write-UInt64LittleEndian $observationStream ([uint64]$fileNameBytes.Length)
    Write-UInt64LittleEndian $observationStream ([uint64]$argumentsBytes.Length)
    $observationStream.Write($actualBytes, 0, $actualBytes.Length)
    $observationStream.Write($modeledBytes, 0, $modeledBytes.Length)
    $observationStream.Write($fileNameBytes, 0, $fileNameBytes.Length)
    $observationStream.Write($argumentsBytes, 0, $argumentsBytes.Length)
    $observationStream.Flush($true)
}
finally { $observationStream.Dispose() }

$actualEqualityOperand = $actualCommandLine + [char]0
if ($actualEqualityOperand -cne $modeledCommandLine) { exit 1 }
exit 0
