from __future__ import annotations

import argparse
from pathlib import Path

from app.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run breakout analyzer raw-data pipeline")
    parser.add_argument(
        "--raw-dir",
        required=True,
        help="Directory containing raw CSV files",
    )
    parser.add_argument(
        "--mapping",
        required=True,
        help="JSON mapping file path",
    )
    parser.add_argument(
        "--workspace",
        default="pipeline_output",
        help="Directory for normalized CSV, DB, reports, and snapshots",
    )
    parser.add_argument(
        "--time-bucket",
        default="09:10-09:20",
        help="Current market time bucket label",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workspace = Path(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    result = run_pipeline(
        raw_dir=Path(args.raw_dir),
        mapping_path=Path(args.mapping),
        workspace=workspace,
        time_bucket=args.time_bucket,
    )

    print("Pipeline complete")
    for label, path in result.items():
        print(f"- {label}: {path}")


if __name__ == "__main__":
    main()
