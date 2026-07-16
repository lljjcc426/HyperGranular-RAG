function ConvertTo-CanonicalJsonString([AllowNull()][object]$Value) {
    if ($null -eq $Value) { return 'null' }
    $text = [string]$Value
    foreach ($character in $text.ToCharArray()) {
        $code = [int]$character
        if ($code -lt 32 -or $code -gt 126) { throw 'Canonical attestation string is outside printable ASCII' }
    }
    return '"' + $text.Replace('\', '\\').Replace('"', '\"') + '"'
}

function Build-CanonicalAdapterAttestationBytes($Values) {
    $utf8 = New-Object Text.UTF8Encoding($false, $true)
    $json = '{' +
        '"schema_version":"2.0",' +
        '"request_id":' + (ConvertTo-CanonicalJsonString ([string]$Values.request_id)) + ',' +
        '"stage":' + (ConvertTo-CanonicalJsonString ([string]$Values.stage)) + ',' +
        '"package_commit":' + (ConvertTo-CanonicalJsonString ([string]$Values.package_commit)) + ',' +
        '"approval_governance_commit":' + (ConvertTo-CanonicalJsonString ([string]$Values.approval_governance_commit)) + ',' +
        '"semantics_evidence_commit":' + (ConvertTo-CanonicalJsonString $Values.semantics_evidence_commit) + ',' +
        '"post_sync_audit_commit":' + (ConvertTo-CanonicalJsonString $Values.post_sync_audit_commit) + ',' +
        '"canonical_builder_path":' + (ConvertTo-CanonicalJsonString ([string]$Values.canonical_builder_path)) + ',' +
        '"canonical_builder_source_bytes":' + [string][int]$Values.canonical_builder_source_bytes + ',' +
        '"canonical_builder_source_sha256":' + (ConvertTo-CanonicalJsonString ([string]$Values.canonical_builder_source_sha256)) + ',' +
        '"capture_host_path":' + (ConvertTo-CanonicalJsonString ([string]$Values.capture_host_path)) + ',' +
        '"capture_host_source_bytes":' + [string][int]$Values.capture_host_source_bytes + ',' +
        '"capture_host_source_sha256":' + (ConvertTo-CanonicalJsonString ([string]$Values.capture_host_source_sha256)) + ',' +
        '"capture_host_invocation_variant":' + (ConvertTo-CanonicalJsonString ([string]$Values.capture_host_invocation_variant)) + ',' +
        '"capture_host_arguments_characters":' + [string][int]$Values.capture_host_arguments_characters + ',' +
        '"capture_host_arguments_sha256":' + (ConvertTo-CanonicalJsonString ([string]$Values.capture_host_arguments_sha256)) + ',' +
        '"capture_host_modeled_characters_including_terminal_null":' + [string][int]$Values.capture_host_modeled_characters_including_terminal_null + ',' +
        '"capture_host_modeled_sha256_including_terminal_null":' + (ConvertTo-CanonicalJsonString ([string]$Values.capture_host_modeled_sha256_including_terminal_null)) + ',' +
        '"adapter_path":' + (ConvertTo-CanonicalJsonString ([string]$Values.adapter_path)) + ',' +
        '"adapter_source_bytes":' + [string][int]$Values.adapter_source_bytes + ',' +
        '"adapter_source_sha256":' + (ConvertTo-CanonicalJsonString ([string]$Values.adapter_source_sha256)) + ',' +
        '"adapter_arguments_characters":' + [string][int]$Values.adapter_arguments_characters + ',' +
        '"adapter_arguments_sha256":' + (ConvertTo-CanonicalJsonString ([string]$Values.adapter_arguments_sha256)) + ',' +
        '"adapter_modeled_characters_including_terminal_null":' + [string][int]$Values.adapter_modeled_characters_including_terminal_null + ',' +
        '"adapter_modeled_sha256_including_terminal_null":' + (ConvertTo-CanonicalJsonString ([string]$Values.adapter_modeled_sha256_including_terminal_null)) + ',' +
        '"adapter_stdout_variant":' + (ConvertTo-CanonicalJsonString ([string]$Values.adapter_stdout_variant)) + ',' +
        '"adapter_stdout_bytes":' + [string][int]$Values.adapter_stdout_bytes + ',' +
        '"adapter_stdout_sha256":' + (ConvertTo-CanonicalJsonString ([string]$Values.adapter_stdout_sha256)) + ',' +
        '"adapter_stderr_bytes":' + [string][int]$Values.adapter_stderr_bytes + ',' +
        '"adapter_stderr_sha256":' + (ConvertTo-CanonicalJsonString ([string]$Values.adapter_stderr_sha256)) + ',' +
        '"adapter_stderr_class":' + (ConvertTo-CanonicalJsonString ([string]$Values.adapter_stderr_class)) + ',' +
        '"adapter_to_parent_stderr_class":' + (ConvertTo-CanonicalJsonString ([string]$Values.adapter_to_parent_stderr_class)) + ',' +
        '"adapter_processes":1,' +
        '"parent_processes":1' +
        '}'
    return [byte[]]$utf8.GetBytes($json)
}
