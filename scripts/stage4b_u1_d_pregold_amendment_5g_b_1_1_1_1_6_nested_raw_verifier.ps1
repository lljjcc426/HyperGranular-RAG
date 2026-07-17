param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('PRE_DIAGNOSTIC')]
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

function Read-RawRecord([string]$Path, [string]$Magic, [uint32]$LayerCode) {
    [byte[]]$bytes = [IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -lt 48) { throw ('Raw record is shorter than the fixed header: ' + $Path) }
    if ($Ascii.GetString($bytes, 0, 8) -cne $Magic) { throw ('Raw record magic mismatch: ' + $Path) }
    if ([BitConverter]::ToUInt32($bytes, 8) -ne 1 -or [BitConverter]::ToUInt32($bytes, 12) -ne 48) { throw ('Raw record format mismatch: ' + $Path) }
    if ([BitConverter]::ToUInt32($bytes, 16) -ne $LayerCode -or [BitConverter]::ToUInt32($bytes, 20) -ne 15) { throw ('Raw record layer or flags mismatch: ' + $Path) }
    if ([BitConverter]::ToUInt32($bytes, 28) -ne 0) { throw ('Raw record reserved field mismatch: ' + $Path) }
    [uint64]$stdoutLength = [BitConverter]::ToUInt64($bytes, 32)
    [uint64]$stderrLength = [BitConverter]::ToUInt64($bytes, 40)
    if ([uint64]$bytes.Length -ne [uint64]48 + $stdoutLength + $stderrLength) { throw ('Raw record length mismatch: ' + $Path) }
    return [pscustomobject]@{
        exit_code = [BitConverter]::ToInt32($bytes, 24)
        stdout_bytes = $stdoutLength
        stderr_bytes = $stderrLength
        total_bytes = $bytes.Length
        sha256 = Get-ExactSha256Hex $bytes
    }
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

$self = $manifest.nested_raw_verifier
Assert-RegisteredSource $self $RepositoryRoot 'Nested raw verifier'
$fileName = [string]$manifest.process_start_info_contract.file_name
$invocation = $self.invocation
$arguments = [string]$invocation.complete_arguments
$modeled = '"' + $fileName + '" ' + $arguments + [char]0
if ($arguments.Length -ne [int]$invocation.complete_arguments_characters -or (Get-ExactSha256Hex $Ascii.GetBytes($arguments)) -cne [string]$invocation.complete_arguments_ascii_sha256) { throw 'Nested raw verifier arguments mismatch' }
if ($modeled.Length -ne [int]$invocation.modeled_command_characters_including_terminal_null -or (Get-ExactSha256Hex $Ascii.GetBytes($modeled)) -cne [string]$invocation.modeled_command_ascii_sha256_including_terminal_null) { throw 'Nested raw verifier modeled command mismatch' }
if (([Environment]::CommandLine + [char]0) -cne $modeled) { throw 'Nested raw verifier actual process command line mismatch' }

$prior = $manifest.prior_hard_failure_19
$priorPath = Join-Path $RepositoryRoot ([string]$prior.raw_repository_path)
$priorRecord = Read-RawRecord $priorPath ([string]$prior.magic) ([uint32]$prior.layer_code)
if ($priorRecord.total_bytes -ne [int]$prior.raw_bytes -or [string]$priorRecord.sha256 -cne [string]$prior.raw_sha256 -or $priorRecord.exit_code -ne [int]$prior.exit_code -or $priorRecord.stdout_bytes -ne [uint64]$prior.stdout_bytes -or $priorRecord.stderr_bytes -ne [uint64]$prior.stderr_bytes) { throw 'Hard Failure 19 preserved raw identity or field mismatch' }

$observed = New-Object Collections.Generic.List[object]
$missingSeen = $false
foreach ($layer in $manifest.nested_raw_contract.layers) {
    $path = Join-Path $RepositoryRoot ([string]$layer.repository_path)
    $exists = [IO.File]::Exists($path)
    if (-not $exists) { $missingSeen = $true; continue }
    if ($missingSeen) { throw ('Nested raw path set is not an outer-to-inner prefix: ' + $layer.repository_path) }
    $record = Read-RawRecord $path ([string]$layer.magic) ([uint32]$layer.layer_code)
    [void]$observed.Add([pscustomobject]@{
        layer = [string]$layer.layer
        repository_path = [string]$layer.repository_path
        exit_code = [int]$record.exit_code
        stdout_bytes = [uint64]$record.stdout_bytes
        stderr_bytes = [uint64]$record.stderr_bytes
        total_bytes = [int]$record.total_bytes
        sha256 = [string]$record.sha256
    })
}
if ($observed.Count -eq 0) { throw 'PRE diagnostic verifier requires the new outer raw observation' }

$result = [ordered]@{
    status = 'PRE_NESTED_RAW_PREFIX_BYTE_VALID'
    request_id = $ExpectedRequestId
    package_commit = $ExpectedPackageCommit
    approval_governance_commit = $ExpectedApprovalGovernance
    preserved_hard_failure_19_sha256 = [string]$priorRecord.sha256
    observed_layer_count = $observed.Count
    deepest_observed_layer = [string]$observed[$observed.Count - 1].layer
    records = @($observed)
}
$outputBytes = $Utf8.GetBytes(($result | ConvertTo-Json -Depth 6 -Compress))
$standardOutput = [Console]::OpenStandardOutput()
$standardOutput.Write($outputBytes, 0, $outputBytes.Length)
$standardOutput.Flush()
