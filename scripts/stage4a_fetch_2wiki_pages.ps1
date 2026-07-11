param(
    [Parameter(Mandatory = $true)]
    [string]$CacheDir
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$dataset = "framolfese/2WikiMultihopQA"
$encodedDataset = [System.Uri]::EscapeDataString($dataset)
$expectedSha = "fe713bfbd1afbca1a65246741a75890405d56a3a"
$pageSize = 100
$cachePath = [System.IO.Path]::GetFullPath($CacheDir)

if (Test-Path -LiteralPath $cachePath) {
    if (@(Get-ChildItem -LiteralPath $cachePath -Force).Count -gt 0) {
        throw "Cache directory must be empty: $cachePath"
    }
} else {
    New-Item -ItemType Directory -Path $cachePath | Out-Null
}

Add-Type -AssemblyName System.Net.Http
$client = [System.Net.Http.HttpClient]::new()
$client.Timeout = [TimeSpan]::FromSeconds(120)
$client.DefaultRequestHeaders.UserAgent.ParseAdd("HyperGranular-RAG-Stage4A/1.0")

function Get-Bytes {
    param([string]$Url)
    return $client.GetByteArrayAsync($Url).GetAwaiter().GetResult()
}

function Get-Sha256 {
    param([byte[]]$Payload)
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($algorithm.ComputeHash($Payload))).Replace("-", "")
    } finally {
        $algorithm.Dispose()
    }
}

function Save-Bytes {
    param([string]$Name, [byte[]]$Payload)
    [System.IO.File]::WriteAllBytes((Join-Path $cachePath $Name), $Payload)
}

function Convert-BytesFromJson {
    param([byte[]]$Payload)
    $text = [System.Text.Encoding]::UTF8.GetString($Payload)
    return $text | ConvertFrom-Json
}

try {
    $metadataUrl = "https://huggingface.co/api/datasets/$dataset"
    [byte[]]$metadataBefore = Get-Bytes -Url $metadataUrl
    $metadataBeforeObject = Convert-BytesFromJson -Payload $metadataBefore
    if ([string]$metadataBeforeObject.sha -ne $expectedSha) {
        throw "Mirror SHA drift before extraction: $($metadataBeforeObject.sha)"
    }
    Save-Bytes -Name "metadata_before.json" -Payload $metadataBefore

    $sizeUrl = "https://datasets-server.huggingface.co/size?dataset=$encodedDataset"
    [byte[]]$sizePayload = Get-Bytes -Url $sizeUrl
    Save-Bytes -Name "size.json" -Payload $sizePayload

    foreach ($offset in 0, 100, 200, 300) {
        $rowsUrl = "https://datasets-server.huggingface.co/rows?dataset=$encodedDataset&config=default&split=validation&offset=$offset&length=$pageSize"
        [byte[]]$payload = Get-Bytes -Url $rowsUrl
        Save-Bytes -Name ("pilot_page_{0:D6}.json" -f $offset) -Payload $payload
    }

    $reservationPages = @()
    foreach ($offset in 400, 500, 600, 700) {
        $rowsUrl = "https://datasets-server.huggingface.co/rows?dataset=$encodedDataset&config=default&split=validation&offset=$offset&length=$pageSize"
        [byte[]]$payload = Get-Bytes -Url $rowsUrl
        $response = Convert-BytesFromJson -Payload $payload
        $ids = @($response.rows | ForEach-Object { [string]$_.row.id })
        if ($ids.Count -ne $pageSize) {
            throw "Reservation offset ${offset}: expected $pageSize IDs, found $($ids.Count)"
        }
        $reservationPages += [ordered]@{
            offset = $offset
            rows = $ids.Count
            response_sha256 = Get-Sha256 -Payload $payload
            ids = $ids
        }
        $payload = $null
        $response = $null
    }
    $reservationManifest = [ordered]@{
        reservation_content_written = $false
        pages = $reservationPages
    }
    $reservationJson = $reservationManifest | ConvertTo-Json -Depth 5
    [System.IO.File]::WriteAllText(
        (Join-Path $cachePath "reservation_ids_manifest.json"),
        $reservationJson + [Environment]::NewLine,
        [System.Text.UTF8Encoding]::new($false)
    )

    [byte[]]$metadataAfter = Get-Bytes -Url $metadataUrl
    $metadataAfterObject = Convert-BytesFromJson -Payload $metadataAfter
    if ([string]$metadataAfterObject.sha -ne [string]$metadataBeforeObject.sha) {
        throw "Mirror SHA drift during extraction"
    }
    Save-Bytes -Name "metadata_after.json" -Payload $metadataAfter

    [ordered]@{
        cache_dir = $cachePath
        pilot_payload_files = 4
        reservation_id_pages = $reservationPages.Count
        reservation_content_written = $false
        mirror_sha = [string]$metadataAfterObject.sha
        metadata_sha256_before = Get-Sha256 -Payload $metadataBefore
        metadata_sha256_after = Get-Sha256 -Payload $metadataAfter
    } | ConvertTo-Json -Depth 3
} finally {
    $client.Dispose()
}
