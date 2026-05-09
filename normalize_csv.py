from __future__ import annotations

import argparse
from pathlib import Path

from app.normalize import normalize_csv_directory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize raw broker/export CSV files")
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
        "--output-dir",
        required=True,
        help="Directory to write normalized CSV files",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_dir = Path(args.raw_dir)
    mapping_path = Path(args.mapping)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    written = normalize_csv_directory(raw_dir, mapping_path, output_dir)
    print("Normalized files")
    for path in written:
        print(f"- {path}")


if __name__ == "__main__":
    main()
