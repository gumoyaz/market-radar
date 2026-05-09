from __future__ import annotations

import argparse
from pathlib import Path

from app.kiwoom_runtime import load_kiwoom_runtime, run_kiwoom_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run breakout analyzer with Kiwoom-oriented settings")
    parser.add_argument(
        "--config",
        default="config/kiwoom_runtime.json",
        help="Kiwoom runtime config path",
    )
    parser.add_argument(
        "--workspace",
        default="kiwoom_workspace",
        help="Workspace directory for pipeline outputs",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    workspace = Path(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    runtime = load_kiwoom_runtime(config_path)
    outputs = run_kiwoom_pipeline(runtime, workspace)

    print("Kiwoom pipeline complete")
    for label, path in outputs.items():
        print(f"- {label}: {path}")


if __name__ == "__main__":
    main()
