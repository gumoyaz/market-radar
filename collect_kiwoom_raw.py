from __future__ import annotations

import argparse
from pathlib import Path

from app.kiwoom_collector import load_collector_config, run_collection


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect Kiwoom-style raw CSV files")
    parser.add_argument(
        "--config",
        default="config/kiwoom_collector.json",
        help="Collector config path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_collector_config(Path(args.config))
    outputs = run_collection(config)

    print("Kiwoom raw collection complete")
    for label, path in outputs.items():
        print(f"- {label}: {path}")


if __name__ == "__main__":
    main()
