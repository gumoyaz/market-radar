from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from app.normalize import TARGET_SPECS


@dataclass(frozen=True)
class CsvHeaderInfo:
    filename: str
    columns: list[str]
    sample_count: int


def inspect_csv_directory(raw_dir: Path) -> list[CsvHeaderInfo]:
    infos: list[CsvHeaderInfo] = []
    for path in sorted(raw_dir.glob("*.csv")):
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            rows = list(reader)

        if not rows:
            infos.append(CsvHeaderInfo(filename=path.name, columns=[], sample_count=0))
            continue

        header = rows[0]
        sample_count = max(len(rows) - 1, 0)
        infos.append(CsvHeaderInfo(filename=path.name, columns=header, sample_count=sample_count))

    return infos


def write_report(
    inspection: list[CsvHeaderInfo],
    report_path: Path,
    mapping_path: Path,
) -> None:
    report_path.write_text(_build_markdown_report(inspection), encoding="utf-8")
    mapping_path.write_text(
        json.dumps(_build_starter_mapping(inspection), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _build_markdown_report(inspection: list[CsvHeaderInfo]) -> str:
    lines = [
        "# CSV Header Report",
        "",
        "실제 원본 CSV를 표준 포맷에 연결하기 전에 헤더를 정리한 보고서다.",
        "",
    ]

    if not inspection:
        lines.append("CSV 파일을 찾지 못했다.")
        return "\n".join(lines)

    for info in inspection:
        lines.extend(
            [
                f"## {info.filename}",
                "",
                f"- rows: {info.sample_count}",
                f"- columns: {len(info.columns)}",
                "",
            ]
        )

        if info.columns:
            for column in info.columns:
                lines.append(f"- `{column}`")
        else:
            lines.append("- empty file")

        lines.append("")

    lines.extend(
        [
            "## Next Step",
            "",
            f"1. `{mapping_path_hint(mapping_path=None)}` 대신 생성된 `starter-mapping.json`을 열기",
            "2. 각 target field에 맞는 원본 컬럼명으로 수정하기",
            "3. 수정 후 `normalize_csv.py`에 넣어서 표준 포맷 CSV를 생성하기",
        ]
    )

    return "\n".join(lines)


def _build_starter_mapping(inspection: list[CsvHeaderInfo]) -> dict:
    starter: dict[str, object] = {
        "value_maps": {
            "size_group": {
                "소형": "small",
                "중형": "mid",
                "대형": "large",
            },
            "is_leader_stock": {
                "Y": "true",
                "N": "false",
            },
            "pattern": {
                "52주신고가": "high_52w",
                "당일고가": "day_high",
                "전일고가": "prev_day_high",
                "재돌파": "rebreak",
                "VI직전": "pre_vi",
            },
        }
    }

    file_lookup = {info.filename: info for info in inspection}
    used_filenames: set[str] = set()

    for target_name, (_, fields) in TARGET_SPECS.items():
        guessed_file = _guess_source_file(target_name, file_lookup, used_filenames)
        used_filenames.add(guessed_file)
        info = file_lookup.get(guessed_file)
        guessed_fields = _guess_field_mapping(fields, info.columns if info else [])
        starter[target_name] = {
            "source": guessed_file,
            "fields": guessed_fields,
        }

    return starter


def _guess_source_file(
    target_name: str,
    file_lookup: dict[str, CsvHeaderInfo],
    used_filenames: set[str],
) -> str:
    keyword_map = {
        "symbol_profiles": ["profile", "symbol", "master", "info", "종목"],
        "minute_bars": ["minute", "bar", "tick", "intraday", "분봉"],
        "time_bucket_stats": ["time", "bucket", "stats", "pattern", "성과", "시간대"],
    }

    candidates = []
    for filename in file_lookup:
        lowered = filename.lower()
        score = sum(1 for keyword in keyword_map[target_name] if keyword in lowered)
        if filename in used_filenames:
            score -= 1
        candidates.append((score, filename))

    if candidates:
        candidates.sort(reverse=True)
        best_score, best_file = candidates[0]
        if best_score > 0:
            return best_file

    return next(iter(file_lookup), f"{target_name}.csv")


def _guess_field_mapping(target_fields: list[str], source_columns: list[str]) -> dict[str, str]:
    aliases = {
        "symbol": ["symbol", "종목코드", "티커", "code"],
        "name": ["name", "종목명", "명칭"],
        "size_group": ["size_group", "시총구분", "size", "cap_group"],
        "day_high": ["day_high", "당일고가", "금일고가"],
        "prev_day_high": ["prev_day_high", "전일고가", "전고"],
        "high_52w": ["high_52w", "52주고가", "52주신고가", "52w_high"],
        "vi_price": ["vi_price", "VI가격", "vi"],
        "is_leader_stock": ["is_leader_stock", "주도주여부", "leader", "leader_flag"],
        "ts": ["ts", "체결시각", "timestamp", "time"],
        "close": ["close", "현재가", "종가", "price"],
        "turnover_billion": ["turnover_billion", "분당거래대금_억", "거래대금", "turnover"],
        "program_net_buy_billion": ["program_net_buy_billion", "프로그램순매수_억", "program", "순매수"],
        "bucket": ["bucket", "시간대", "time_bucket"],
        "pattern": ["pattern", "패턴"],
        "success_rate": ["success_rate", "성공률", "win_rate"],
        "trap_rate": ["trap_rate", "함정비율", "failure_rate"],
    }

    mapping: dict[str, str] = {}
    lowered_columns = {column.lower(): column for column in source_columns}

    for field in target_fields:
        chosen = ""
        for alias in aliases.get(field, [field]):
            alias_lower = alias.lower()
            if alias_lower in lowered_columns:
                chosen = lowered_columns[alias_lower]
                break
            for source_column in source_columns:
                if alias_lower in source_column.lower():
                    chosen = source_column
                    break
            if chosen:
                break

        mapping[field] = chosen

    return mapping


def mapping_path_hint(mapping_path: Path | None) -> str:
    if mapping_path is None:
        return "output/starter-mapping.json"
    return str(mapping_path)
