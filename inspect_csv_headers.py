from __future__ import annotations

import argparse
from pathlib import Path

from app.header_inspector import inspect_csv_directory, write_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect CSV headers and generate mapping starter")
    parser.add_argument(
        "--raw-dir",
        required=True,
        help="Directory containing raw CSV files",
    )
    parser.add_argument(
        "--output-report",
        default="output/csv-header-report.md",
        help="Markdown report output path",
    )
    parser.add_argument(
        "--output-mapping",
        default="output/starter-mapping.json",
        help="Starter mapping JSON output path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_dir = Path(args.raw_dir)
    report_path = Path(args.output_report)
    mapping_path = Path(args.output_mapping)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    mapping_path.parent.mkdir(parents=True, exist_ok=True)

    inspection = inspect_csv_directory(raw_dir)
    write_report(inspection, report_path, mapping_path)

    print(f"Header report written to {report_path}")
    print(f"Starter mapping written to {mapping_path}")


if __name__ == "__main__":
    main()
