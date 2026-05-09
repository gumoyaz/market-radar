from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.pipeline import run_pipeline


@dataclass(frozen=True)
class KiwoomRuntimeConfig:
    raw_dir: Path
    mapping_path: Path
    time_bucket: str
    broker: str
    notes: str


def load_kiwoom_runtime(config_path: Path) -> KiwoomRuntimeConfig:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return KiwoomRuntimeConfig(
        raw_dir=Path(data["raw_dir"]),
        mapping_path=Path(data["mapping_path"]),
        time_bucket=data.get("time_bucket", "09:10-09:20"),
        broker=data.get("broker", "kiwoom"),
        notes=data.get("notes", ""),
    )


def run_kiwoom_pipeline(
    runtime: KiwoomRuntimeConfig,
    workspace: Path,
) -> dict[str, Path]:
    if runtime.broker.lower() != "kiwoom":
        raise ValueError("This runner expects broker='kiwoom' in the config file.")

    outputs = run_pipeline(
        raw_dir=runtime.raw_dir,
        mapping_path=runtime.mapping_path,
        workspace=workspace,
        time_bucket=runtime.time_bucket,
    )

    runtime_summary = workspace / "reports" / "kiwoom-runtime-summary.txt"
    runtime_summary.write_text(
        "\n".join(
            [
                f"broker={runtime.broker}",
                f"raw_dir={runtime.raw_dir}",
                f"mapping_path={runtime.mapping_path}",
                f"time_bucket={runtime.time_bucket}",
                f"notes={runtime.notes}",
            ]
        ),
        encoding="utf-8",
    )
    outputs["runtime_summary"] = runtime_summary
    return outputs
