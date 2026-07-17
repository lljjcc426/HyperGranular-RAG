param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('BOUNDED_REMOTE_GATE')]
    [string]$Mode
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PythonExecutable = 'C:\ProgramData\anaconda3\python.exe'
$HelperRelativePath = 'scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_8_bounded_remote_gate.py'
$HelperArguments = '-I -B scripts/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_8_bounded_remote_gate.py'
$HelperArgumentsCharacters = 82
$HelperArgumentsAsciiSha256 = 'D3529D3449AD623A811FC93F64DC4BB1251CA16DE4439E7F985039431800440E'
$HelperSourceBytes = 9964
$HelperSourceLfCount = 294
$HelperSourceSha256 = '7EBC6F40C58D479774B6C083157E5ECB429E02ED0B261FCECF1ADB58551C4567'
$ObservationRelativePath = 'results/stage4b_u1_d_pregold_amendment_5g_b_1_1_1_1_7_observer_command_line_observation.bin'

$Ascii = New-Object Text.ASCIIEncoding
$Utf8 = New-Object Text.UTF8Encoding($false, $true)

function Get-ExactSha256Hex {
    param([byte[]]$Bytes)

    $algorithm = [Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($algorithm.ComputeHash($Bytes))).Replace('-', '')
    }
    finally {
        $algorithm.Dispose()
    }
}

function Assert-CommitBinding {
    param(
        [AllowNull()]
        [string]$Value,
        [string]$Label
    )

    if ([string]::IsNullOrEmpty($Value) -or $Value -cnotmatch '^[0-9a-f]{40}$') {
        throw ('INVALID_COMMIT_BINDING_' + $Label)
    }
}

function New-ExpectedSuccessJson {
    param(
        [string]$PackageCommit,
        [string]$ApprovalCommit,
        [string]$SuccessfulMethod,
        [string]$PrimaryResultClass,
        [int]$AlternateCalls,
        [int]$TotalRemoteCalls
    )

    $invariant = [Globalization.CultureInfo]::InvariantCulture
    return '{"alternate_calls":' + $AlternateCalls.ToString($invariant) +
        ',"approval_governance_commit":"' + $ApprovalCommit +
        '","final_normalized_ref":"refs/heads/main"' +
        ',"final_normalized_sha":"' + $ApprovalCommit +
        '","gate_outcome":"PASS"' +
        ',"package_commit":"' + $PackageCommit +
        '","primary_calls":1' +
        ',"primary_result_class":"' + $PrimaryResultClass +
        '","same_method_retries":0' +
        ',"schema":"HGRAG_BOUNDED_REMOTE_GATE_V1"' +
        ',"successful_method":"' + $SuccessfulMethod +
        '","total_remote_calls":' + $TotalRemoteCalls.ToString($invariant) + '}'
}

$ExpectedPackageCommit = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_PACKAGE_COMMIT', 'Process')
$ExpectedApprovalGovernance = [Environment]::GetEnvironmentVariable('HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT', 'Process')
Assert-CommitBinding $ExpectedPackageCommit 'PACKAGE_COMMIT'
Assert-CommitBinding $ExpectedApprovalGovernance 'APPROVAL_GOVERNANCE_COMMIT'

$RepositoryRoot = (Get-Item -LiteralPath '.').FullName
$GitDirectory = Join-Path $RepositoryRoot '.git'
$HelperPath = Join-Path $RepositoryRoot $HelperRelativePath
$ObservationPath = Join-Path $RepositoryRoot $ObservationRelativePath
if (-not (Test-Path -LiteralPath $GitDirectory -PathType Container)) { throw 'REPOSITORY_ROOT_NOT_CONFIRMED' }
if (-not (Test-Path -LiteralPath $PythonExecutable -PathType Leaf)) { throw 'FROZEN_PYTHON_EXECUTABLE_MISSING' }
if (-not (Test-Path -LiteralPath $HelperPath -PathType Leaf)) { throw 'FROZEN_HELPER_SOURCE_MISSING' }
if (Test-Path -LiteralPath $ObservationPath) { throw 'OBSERVATION_PATH_ALREADY_EXISTS' }

$helperBytes = [IO.File]::ReadAllBytes($HelperPath)
$helperLfCount = 0
$helperCrCount = 0
foreach ($helperByte in $helperBytes) {
    if ($helperByte -eq 10) { $helperLfCount++ }
    if ($helperByte -eq 13) { $helperCrCount++ }
}
if ($helperBytes.Length -ne $HelperSourceBytes) { throw 'FROZEN_HELPER_SOURCE_BYTE_COUNT_MISMATCH' }
if ($helperLfCount -ne $HelperSourceLfCount -or $helperCrCount -ne 0) { throw 'FROZEN_HELPER_SOURCE_LINE_ENDING_MISMATCH' }
if ($helperBytes[$helperBytes.Length - 1] -ne 10) { throw 'FROZEN_HELPER_SOURCE_TRAILING_NEWLINE_MISSING' }
if ((Get-ExactSha256Hex $helperBytes) -cne $HelperSourceSha256) { throw 'FROZEN_HELPER_SOURCE_SHA256_MISMATCH' }
if ($HelperArguments.Length -ne $HelperArgumentsCharacters) { throw 'FROZEN_HELPER_ARGUMENT_CHARACTER_COUNT_MISMATCH' }
if ((Get-ExactSha256Hex ($Ascii.GetBytes($HelperArguments))) -cne $HelperArgumentsAsciiSha256) { throw 'FROZEN_HELPER_ARGUMENT_SHA256_MISMATCH' }

$processInfo = New-Object Diagnostics.ProcessStartInfo
$processInfo.FileName = $PythonExecutable
$processInfo.Arguments = $HelperArguments
$processInfo.WorkingDirectory = $RepositoryRoot
$processInfo.UseShellExecute = $false
$processInfo.RedirectStandardInput = $false
$processInfo.RedirectStandardOutput = $true
$processInfo.RedirectStandardError = $true
$processInfo.CreateNoWindow = $true
$processInfo.EnvironmentVariables['HGRAG_EXPECTED_PACKAGE_COMMIT'] = $ExpectedPackageCommit
$processInfo.EnvironmentVariables['HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT'] = $ExpectedApprovalGovernance

$process = New-Object Diagnostics.Process
$process.StartInfo = $processInfo
$stdoutBuffer = New-Object IO.MemoryStream
$stderrBuffer = New-Object IO.MemoryStream
$stdoutBytes = [byte[]]@()
$stderrBytes = [byte[]]@()
$exitCode = -1
try {
    try {
        $started = $process.Start()
    }
    catch {
        throw ('BOUNDED_HELPER_PROCESS_START_FAILED_' + $_.Exception.GetType().Name)
    }
    if (-not $started) { throw 'BOUNDED_HELPER_PROCESS_START_RETURNED_FALSE' }

    $stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync($stdoutBuffer)
    $stderrTask = $process.StandardError.BaseStream.CopyToAsync($stderrBuffer)
    $process.WaitForExit()
    [void][Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($stdoutTask, $stderrTask))
    $exitCode = $process.ExitCode
    $stdoutBytes = [byte[]]$stdoutBuffer.ToArray()
    $stderrBytes = [byte[]]$stderrBuffer.ToArray()
}
finally {
    $process.Dispose()
    $stdoutBuffer.Dispose()
    $stderrBuffer.Dispose()
}

if ($exitCode -ne 0) {
    throw ('BOUNDED_HELPER_NONZERO_EXIT_' + $exitCode.ToString([Globalization.CultureInfo]::InvariantCulture) +
        '_STDOUT_BYTES_' + $stdoutBytes.Length.ToString([Globalization.CultureInfo]::InvariantCulture) +
        '_STDERR_BYTES_' + $stderrBytes.Length.ToString([Globalization.CultureInfo]::InvariantCulture))
}
if ($stderrBytes.Length -ne 0) { throw ('BOUNDED_HELPER_SUCCESS_STDERR_BYTES_' + $stderrBytes.Length.ToString([Globalization.CultureInfo]::InvariantCulture)) }
if ($stdoutBytes.Length -eq 0) { throw 'BOUNDED_HELPER_SUCCESS_STDOUT_EMPTY' }

$stdoutLfCount = 0
$stdoutCrCount = 0
foreach ($stdoutByte in $stdoutBytes) {
    if ($stdoutByte -eq 10) { $stdoutLfCount++ }
    if ($stdoutByte -eq 13) { $stdoutCrCount++ }
}
if ($stdoutLfCount -ne 1 -or $stdoutCrCount -ne 0 -or $stdoutBytes[$stdoutBytes.Length - 1] -ne 10) {
    throw 'BOUNDED_HELPER_SUCCESS_STDOUT_FRAMING_MISMATCH'
}
$stdoutText = $Utf8.GetString($stdoutBytes, 0, $stdoutBytes.Length - 1)

$allowedSuccessLines = New-Object 'System.Collections.Generic.List[string]'
$allowedSuccessLines.Add((New-ExpectedSuccessJson $ExpectedPackageCommit $ExpectedApprovalGovernance 'PRIMARY_GIT' 'SUCCESS' 0 1))
$registeredTransportClasses = @(
    'TLS_CONNECT_FAILURE',
    'DNS_RESOLUTION_FAILURE',
    'CONNECTION_RESET_BEFORE_REF',
    'HTTP_TRANSPORT_UNAVAILABLE'
)
foreach ($transportClass in $registeredTransportClasses) {
    $allowedSuccessLines.Add((New-ExpectedSuccessJson $ExpectedPackageCommit $ExpectedApprovalGovernance 'ALTERNATE_GITHUB_REST' $transportClass 1 2))
}

$matchedSuccessLine = $false
foreach ($allowedSuccessLine in $allowedSuccessLines) {
    if ($stdoutText -ceq $allowedSuccessLine) {
        $matchedSuccessLine = $true
        break
    }
}
if (-not $matchedSuccessLine) { throw 'BOUNDED_HELPER_SUCCESS_JSON_NOT_REGISTERED' }

$launcherStdout = [Console]::OpenStandardOutput()
$launcherStdout.Write($stdoutBytes, 0, $stdoutBytes.Length)
$launcherStdout.Flush()
