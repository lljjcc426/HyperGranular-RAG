from __future__ import annotations

import json
import os
import re
import socket
import ssl
import subprocess
import sys
import urllib.error
import urllib.request


GIT_EXE = r"C:\Program Files\Git\cmd\git.exe"
REMOTE_URL = "https://github.com/lljjcc426/HyperGranular-RAG.git"
REMOTE_REF = "refs/heads/main"
REST_URL = "https://api.github.com/repos/lljjcc426/HyperGranular-RAG/git/ref/heads/main"
REST_API_VERSION = "2026-03-10"
TIMEOUT_SECONDS = 30
MAX_REST_BODY_BYTES = 65536
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

PRIMARY_COMMAND = (
    GIT_EXE,
    "ls-remote",
    "--heads",
    REMOTE_URL,
    REMOTE_REF,
)

AUTH_FAILURE_TOKENS = (
    "authentication failed",
    "authorization failed",
    "repository not found",
    "permission denied",
    "could not read username",
    "terminal prompts disabled",
    "http 401",
    "http 403",
    "error: 401",
    "error: 403",
    "error: 404",
)

REGISTERED_TRANSPORT_TOKENS = (
    (
        "TLS_CONNECT_FAILURE",
        (
            "tls connect error",
            "ssl connect error",
            "schannel: failed to receive handshake",
            "gnutls_handshake() failed",
            "certificate verify failed",
        ),
    ),
    (
        "DNS_RESOLUTION_FAILURE",
        (
            "could not resolve host",
            "could not resolve hostname",
            "name or service not known",
            "temporary failure in name resolution",
        ),
    ),
    (
        "CONNECTION_RESET_BEFORE_REF",
        (
            "connection reset",
            "recv failure: connection was reset",
            "remote end closed connection without response",
        ),
    ),
    (
        "HTTP_TRANSPORT_UNAVAILABLE",
        (
            "failed to connect",
            "couldn't connect to server",
            "connection timed out",
            "operation timed out",
            "network is unreachable",
            "empty reply from server",
            "the requested url returned error: 502",
            "the requested url returned error: 503",
            "the requested url returned error: 504",
        ),
    ),
)


class GateFailure(Exception):
    pass


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def require_commit(value: str | None, label: str) -> str:
    if value is None or COMMIT_RE.fullmatch(value) is None:
        raise GateFailure(f"{label}_MISSING_OR_INVALID")
    return value


def decode_utf8(raw: bytes, label: str) -> str:
    try:
        return raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise GateFailure(f"{label}_NOT_STRICT_UTF8") from exc


def parse_primary_success(stdout_text: str, stderr_text: str) -> str:
    if stderr_text != "":
        raise GateFailure("PRIMARY_SUCCESS_STDERR_NONEMPTY")
    lines = stdout_text.splitlines()
    if len(lines) != 1:
        raise GateFailure("PRIMARY_REF_RESPONSE_NOT_EXACTLY_ONE_LINE")
    match = re.fullmatch(r"([0-9a-f]{40})\trefs/heads/main", lines[0])
    if match is None:
        raise GateFailure("PRIMARY_REF_RESPONSE_MALFORMED")
    return match.group(1)


def classify_primary_transport(stdout_text: str, stderr_text: str) -> str | None:
    if stdout_text != "" or stderr_text == "":
        return None
    lowered = stderr_text.casefold()
    for result_class, tokens in REGISTERED_TRANSPORT_TOKENS:
        if any(token in lowered for token in tokens):
            return result_class
    return None


def run_primary(expected_sha: str) -> tuple[str | None, str]:
    environment = os.environ.copy()
    environment["GIT_TERMINAL_PROMPT"] = "0"
    environment["GCM_INTERACTIVE"] = "Never"
    try:
        completed = subprocess.run(
            PRIMARY_COMMAND,
            check=False,
            capture_output=True,
            timeout=TIMEOUT_SECONDS,
            env=environment,
            shell=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except subprocess.TimeoutExpired as exc:
        timeout_stdout = decode_utf8(exc.stdout or b"", "PRIMARY_TIMEOUT_STDOUT")
        timeout_stderr = decode_utf8(exc.stderr or b"", "PRIMARY_TIMEOUT_STDERR")
        if timeout_stdout != "":
            raise GateFailure("PRIMARY_NON_REGISTERED_FAILURE") from exc
        if any(token in timeout_stderr.casefold() for token in AUTH_FAILURE_TOKENS):
            raise GateFailure("PRIMARY_AUTHENTICATION_OR_AUTHORIZATION_REJECTION") from exc
        return "HTTP_TRANSPORT_UNAVAILABLE", "PRIMARY_TIMEOUT_BEFORE_REF"
    except FileNotFoundError as exc:
        raise GateFailure("PRIMARY_GIT_EXECUTABLE_MISSING") from exc
    except OSError as exc:
        raise GateFailure("PRIMARY_PROCESS_START_FAILED") from exc

    stdout_text = decode_utf8(completed.stdout, "PRIMARY_STDOUT")
    stderr_text = decode_utf8(completed.stderr, "PRIMARY_STDERR")
    if completed.returncode == 0:
        returned_sha = parse_primary_success(stdout_text, stderr_text)
        if returned_sha != expected_sha:
            raise GateFailure("PRIMARY_REMOTE_REF_SHA_MISMATCH")
        return None, returned_sha

    if stdout_text == "" and any(token in stderr_text.casefold() for token in AUTH_FAILURE_TOKENS):
        raise GateFailure("PRIMARY_AUTHENTICATION_OR_AUTHORIZATION_REJECTION")
    transport_class = classify_primary_transport(stdout_text, stderr_text)
    if transport_class is None:
        raise GateFailure("PRIMARY_NON_REGISTERED_FAILURE")
    return transport_class, ""


def unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise GateFailure("ALTERNATE_DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def run_alternate(expected_sha: str) -> str:
    request = urllib.request.Request(
        REST_URL,
        method="GET",
        headers={
            "Accept": "application/vnd.github+json",
            "Accept-Encoding": "identity",
            "User-Agent": "HyperGranular-RAG-Stage4B-U1-D-Remote-Gate-1.1.8",
            "X-GitHub-Api-Version": REST_API_VERSION,
        },
    )
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        NoRedirectHandler(),
    )
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            status = response.getcode()
            raw_body = response.read(MAX_REST_BODY_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise GateFailure(f"ALTERNATE_HTTP_STATUS_{exc.code}") from exc
    except (urllib.error.URLError, socket.timeout, TimeoutError, ssl.SSLError) as exc:
        raise GateFailure("ALTERNATE_TRANSPORT_FAILURE") from exc
    except OSError as exc:
        raise GateFailure("ALTERNATE_IO_FAILURE") from exc

    if status != 200:
        raise GateFailure(f"ALTERNATE_HTTP_STATUS_{status}")
    if len(raw_body) > MAX_REST_BODY_BYTES:
        raise GateFailure("ALTERNATE_RESPONSE_TOO_LARGE")
    body_text = decode_utf8(raw_body, "ALTERNATE_BODY")
    try:
        payload = json.loads(body_text, object_pairs_hook=unique_json_object)
    except GateFailure:
        raise
    except (json.JSONDecodeError, TypeError) as exc:
        raise GateFailure("ALTERNATE_RESPONSE_NOT_JSON_OBJECT") from exc

    if not isinstance(payload, dict):
        raise GateFailure("ALTERNATE_RESPONSE_NOT_JSON_OBJECT")
    if payload.get("ref") != REMOTE_REF:
        raise GateFailure("ALTERNATE_REF_IDENTITY_MISMATCH")
    object_value = payload.get("object")
    if not isinstance(object_value, dict):
        raise GateFailure("ALTERNATE_OBJECT_MISSING_OR_INVALID")
    if object_value.get("type") != "commit":
        raise GateFailure("ALTERNATE_OBJECT_TYPE_NOT_COMMIT")
    returned_sha = object_value.get("sha")
    if not isinstance(returned_sha, str) or COMMIT_RE.fullmatch(returned_sha) is None:
        raise GateFailure("ALTERNATE_COMMIT_SHA_MALFORMED")
    if returned_sha != expected_sha:
        raise GateFailure("ALTERNATE_REMOTE_REF_SHA_MISMATCH")
    return returned_sha


def emit_success(
    package_commit: str,
    approval_commit: str,
    method: str,
    primary_result_class: str,
    alternate_calls: int,
) -> None:
    result = {
        "alternate_calls": alternate_calls,
        "approval_governance_commit": approval_commit,
        "final_normalized_ref": REMOTE_REF,
        "final_normalized_sha": approval_commit,
        "gate_outcome": "PASS",
        "package_commit": package_commit,
        "primary_calls": 1,
        "primary_result_class": primary_result_class,
        "same_method_retries": 0,
        "schema": "HGRAG_BOUNDED_REMOTE_GATE_V1",
        "successful_method": method,
        "total_remote_calls": 1 + alternate_calls,
    }
    sys.stdout.write(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")


def main() -> int:
    package_commit = require_commit(
        os.environ.get("HGRAG_EXPECTED_PACKAGE_COMMIT"),
        "EXPECTED_PACKAGE_COMMIT",
    )
    approval_commit = require_commit(
        os.environ.get("HGRAG_EXPECTED_APPROVAL_GOVERNANCE_COMMIT"),
        "EXPECTED_APPROVAL_GOVERNANCE_COMMIT",
    )
    transport_class, primary_value = run_primary(approval_commit)
    if transport_class is None:
        emit_success(package_commit, approval_commit, "PRIMARY_GIT", "SUCCESS", 0)
        return 0

    alternate_sha = run_alternate(approval_commit)
    if alternate_sha != approval_commit:
        raise GateFailure("ALTERNATE_INTERNAL_SHA_MISMATCH")
    emit_success(package_commit, approval_commit, "ALTERNATE_GITHUB_REST", transport_class, 1)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except GateFailure as exc:
        sys.stderr.write(f"REMOTE_GATE_FAILURE:{exc}\n")
        raise SystemExit(1)
    except Exception as exc:
        sys.stderr.write(f"REMOTE_GATE_FAILURE:UNEXPECTED_{type(exc).__name__}\n")
        raise SystemExit(2)
