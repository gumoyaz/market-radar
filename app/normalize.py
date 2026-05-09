from __future__ import annotations

import csv
import json
from pathlib import Path


TARGET_SPECS: dict[str, tuple[str, list[str]]] = {
    "symbol_profiles": (
        "symbol_profiles.csv",
        [
            "symbol",
            "name",
            "size_group",
            "day_high",
            "prev_day_high",
            "high_52w",
            "vi_price",
            "is_leader_stock",
        ],
    ),
    "minute_bars": (
        "minute_bars.csv",
        [
            "symbol",
            "ts",
            "close",
            "turnover_billion",
            "program_net_buy_billion",
            "source",
        ],
    ),
    "time_bucket_stats": (
        "time_bucket_stats.csv",
        [
            "symbol",
            "bucket",
            "pattern",
            "success_rate",
            "trap_rate",
        ],
    ),
}


def normalize_csv_directory(
    raw_dir: Path,
    mapping_path: Path,
    output_dir: Path,
) -> list[Path]:
    config = json.loads(mapping_path.read_text(encoding="utf-8"))
    value_maps = config.get("value_maps", {})
    written_paths: list[Path] = []

    for target_name, (filename, fieldnames) in TARGET_SPECS.items():
        target_config = config.get(target_name)
        if not target_config:
            continue

        source_path = raw_dir / target_config["source"]
        rows = _read_csv(source_path)
        normalized_rows = [
            _normalize_row(row, target_config["fields"], value_maps)
            for row in rows
        ]

        output_path = output_dir / filename
        _write_csv(output_path, fieldnames, normalized_rows)
        written_paths.append(output_path)

    return written_paths


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _normalize_row(
    row: dict[str, str],
    field_mapping: dict[str, str | dict[str, str]],
    value_maps: dict[str, dict[str, str]],
) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for target_field, source in field_mapping.items():
        if isinstance(source, dict) and "const" in source:
            raw_value = str(source["const"])
        else:
            raw_value = row[str(source)]

        mapped_value = value_maps.get(target_field, {}).get(raw_value, raw_value)
        normalized[target_field] = mapped_value

    return normalized
