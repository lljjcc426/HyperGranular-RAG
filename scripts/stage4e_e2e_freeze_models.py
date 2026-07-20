"""Freeze exact local file identities for the two Stage4E model snapshots."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from stage4e_e2e_common import (
    ENCODER_ID,
    ENCODER_REVISION,
    GENERATOR_ID,
    GENERATOR_REVISION,
    SCHEMA_VERSION,
    file_identity,
    render_json,
    sha256_bytes,
    write_new_files_atomically,
)


def snapshot_binding(root: Path, model_id: str, revision: str) -> dict[str, Any]:
    if not root.is_dir():
        raise FileNotFoundError(f"Model snapshot directory is absent: {root}")
    files: list[dict[str, Any]] = []
    for path in sorted((value for value in root.rglob("*") if value.is_file())):
        relative = path.relative_to(root).as_posix()
        files.append({"path": relative, **file_identity(path)})
    if not files:
        raise ValueError(f"Model snapshot is empty: {root}")
    return {
        "files": files,
        "files_sha256": sha256_bytes(render_json(files)),
        "license": "Apache-2.0",
        "model_id": model_id,
        "revision": revision,
        "snapshot_path": str(root.resolve()),
        "source_url": f"https://huggingface.co/{model_id}/tree/{revision}",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--encoder-snapshot", required=True, type=Path)
    parser.add_argument("--generator-snapshot", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = {
        "download_date": "2026-07-20",
        "models": {
            "encoder": snapshot_binding(
                args.encoder_snapshot, ENCODER_ID, ENCODER_REVISION
            ),
            "generator": snapshot_binding(
                args.generator_snapshot, GENERATOR_ID, GENERATOR_REVISION
            ),
        },
        "schema_version": SCHEMA_VERSION,
        "status": "STAGE4E_MODEL_SNAPSHOTS_FROZEN_NO_OFFICIAL_INFERENCE",
    }
    write_new_files_atomically(((args.output, render_json(manifest)),))
    print(
        "STAGE4E_MODEL_SNAPSHOTS_FROZEN "
        f"encoder_files={len(manifest['models']['encoder']['files'])} "
        f"generator_files={len(manifest['models']['generator']['files'])}"
    )


if __name__ == "__main__":
    main()
