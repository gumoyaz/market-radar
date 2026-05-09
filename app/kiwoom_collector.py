from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from app.kiwoom_openapi import (
    KiwoomDependencyError,
    KiwoomLiveAdapter,
    KiwoomRuntimeError,
)


SYMBOL_PROFILE_FIELDS = [
    "종목코드",
    "종목명",
    "시총구분",
    "당일고가",
    "전일고가",
    "52주고가",
    "VI가격",
    "주도주여부",
]

MINUTE_BAR_FIELDS = [
    "종목코드",
    "체결시각",
    "현재가",
    "분당거래대금_억",
    "프로그램순매수_억",
    "데이터출처",
]

TIME_BUCKET_FIELDS = [
    "종목코드",
    "시간대",
    "패턴",
    "성공률",
    "함정비율",
]


@dataclass(frozen=True)
class KiwoomSeedSymbol:
    symbol: str
    name: str
    size_group_ko: str
    day_high: float
    prev_day_high: float
    high_52w: float
    vi_price: float
    is_leader_stock: bool
    base_price: float
    base_turnover_billion: float
    base_program_net_buy_billion: float
    patterns: list[dict[str, str | float]]


@dataclass(frozen=True)
class KiwoomCollectorConfig:
    mode: str
    output_dir: Path
    watchlist_path: Path
    interval_sec: int
    cycles: int
    time_bucket: str
    login_timeout_sec: int
    real_screen_no: str
    debug_log_path: Path | None


def load_collector_config(config_path: Path) -> KiwoomCollectorConfig:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return KiwoomCollectorConfig(
        mode=data.get("mode", "mock"),
        output_dir=Path(data["output_dir"]),
        watchlist_path=Path(data["watchlist_path"]),
        interval_sec=int(data.get("interval_sec", 60)),
        cycles=int(data.get("cycles", 1)),
        time_bucket=data.get("time_bucket", "09:10-09:20"),
        login_timeout_sec=int(data.get("login_timeout_sec", 60)),
        real_screen_no=str(data.get("real_screen_no", "1000")),
        debug_log_path=Path(data["debug_log_path"]) if data.get("debug_log_path") else None,
    )


def run_collection(config: KiwoomCollectorConfig) -> dict[str, Path]:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    seed_symbols = _load_watchlist(config.watchlist_path)

    if config.mode == "mock":
        return _run_mock_collection(config, seed_symbols)

    if config.mode == "live":
        return _run_live_collection(config, seed_symbols)

    raise ValueError(f"Unsupported collector mode: {config.mode}")


def _run_mock_collection(
    config: KiwoomCollectorConfig,
    seed_symbols: list[KiwoomSeedSymbol],
) -> dict[str, Path]:
    last_outputs: dict[str, Path] = {}
    run_count = 0
    while True:
        run_count += 1
        payload = _build_mock_payload(seed_symbols, config.time_bucket, run_count)
        last_outputs = _write_raw_csv_bundle(config.output_dir, payload)

        if config.cycles and run_count >= config.cycles:
            return last_outputs

        time.sleep(config.interval_sec)


def _run_live_collection(
    config: KiwoomCollectorConfig,
    seed_symbols: list[KiwoomSeedSymbol],
) -> dict[str, Path]:
    try:
        adapter = KiwoomLiveAdapter(
            screen_no=config.real_screen_no,
            login_timeout_sec=config.login_timeout_sec,
            debug_log_path=str(config.debug_log_path) if config.debug_log_path else None,
        )
    except KiwoomDependencyError as exc:
        raise RuntimeError(
            "Kiwoom live mode requires Kiwoom OpenAPI+ on Windows and a Python "
            "environment with PyQt5/QAxContainer available."
        ) from exc

    try:
        adapter.connect()
        adapter.register_symbols([item.symbol for item in seed_symbols])

        last_outputs: dict[str, Path] = {}
        run_count = 0
        while True:
            run_count += 1
            adapter.pump(config.interval_sec)
            payload = _build_live_payload(seed_symbols, config.time_bucket, adapter)
            last_outputs = _write_raw_csv_bundle(config.output_dir, payload)

            if config.cycles and run_count >= config.cycles:
                return last_outputs
    except KiwoomRuntimeError as exc:
        raise RuntimeError(f"Kiwoom live collection failed: {exc}") from exc
    finally:
        adapter.close()


def _load_watchlist(path: Path) -> list[KiwoomSeedSymbol]:
    data = json.loads(path.read_text(encoding="utf-8"))
    symbols: list[KiwoomSeedSymbol] = []
    for item in data["symbols"]:
        symbols.append(
            KiwoomSeedSymbol(
                symbol=item["symbol"],
                name=item["name"],
                size_group_ko=item["size_group_ko"],
                day_high=float(item["day_high"]),
                prev_day_high=float(item["prev_day_high"]),
                high_52w=float(item["high_52w"]),
                vi_price=float(item["vi_price"]),
                is_leader_stock=bool(item["is_leader_stock"]),
                base_price=float(item["base_price"]),
                base_turnover_billion=float(item["base_turnover_billion"]),
                base_program_net_buy_billion=float(item["base_program_net_buy_billion"]),
                patterns=list(item["patterns"]),
            )
        )
    return symbols


def _build_mock_payload(
    symbols: list[KiwoomSeedSymbol],
    time_bucket: str,
    run_count: int,
) -> dict[str, list[dict[str, str]]]:
    now = datetime.now()
    symbol_profiles = _symbol_profiles_rows(symbols)
    minute_bars: list[dict[str, str]] = []

    for index, item in enumerate(symbols):
        for offset in range(3):
            ts = now.replace(second=0, microsecond=0)
            ts = ts.replace(minute=max(0, ts.minute - (2 - offset)))
            turnover = item.base_turnover_billion + (run_count - 1) * 1.2 + offset * 2.4 + index
            program = item.base_program_net_buy_billion + offset * 0.4 + (run_count - 1) * 0.2
            price = item.base_price + offset * 100 + (run_count - 1) * 50
            minute_bars.append(
                _minute_bar_row(
                    symbol=item.symbol,
                    timestamp=ts.isoformat(),
                    price=price,
                    turnover_billion=turnover,
                    program_net_buy_billion=program,
                    source="mock",
                )
            )

    return {
        "raw_symbol_profiles.csv": symbol_profiles,
        "raw_minute_bars.csv": minute_bars,
        "raw_time_bucket_stats.csv": _time_bucket_rows(symbols, time_bucket),
    }


def _build_live_payload(
    symbols: list[KiwoomSeedSymbol],
    time_bucket: str,
    adapter: KiwoomLiveAdapter,
) -> dict[str, list[dict[str, str]]]:
    symbol_profiles = _symbol_profiles_rows(symbols)
    minute_bars: list[dict[str, str]] = []

    for item in symbols:
        snapshot = adapter.get_symbol_snapshot(item.symbol)
        if snapshot is None:
            minute_bars.extend(_fallback_rows_for_symbol(item))
            continue

        minute_bars.append(
            _minute_bar_row(
                symbol=item.symbol,
                timestamp=snapshot["ts"],
                price=float(snapshot["price"]),
                turnover_billion=float(snapshot["turnover_billion"]),
                program_net_buy_billion=item.base_program_net_buy_billion,
                source="live",
            )
        )

    return {
        "raw_symbol_profiles.csv": symbol_profiles,
        "raw_minute_bars.csv": minute_bars,
        "raw_time_bucket_stats.csv": _time_bucket_rows(symbols, time_bucket),
    }


def _symbol_profiles_rows(symbols: list[KiwoomSeedSymbol]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in symbols:
        rows.append(
            {
                "종목코드": item.symbol,
                "종목명": item.name,
                "시총구분": item.size_group_ko,
                "당일고가": _fmt_number(item.day_high),
                "전일고가": _fmt_number(item.prev_day_high),
                "52주고가": _fmt_number(item.high_52w),
                "VI가격": _fmt_number(item.vi_price),
                "주도주여부": "Y" if item.is_leader_stock else "N",
            }
        )
    return rows


def _time_bucket_rows(
    symbols: list[KiwoomSeedSymbol],
    default_bucket: str,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in symbols:
        for pattern in item.patterns:
            rows.append(
                {
                    "종목코드": item.symbol,
                    "시간대": str(pattern.get("bucket", default_bucket)),
                    "패턴": str(pattern["pattern"]),
                    "성공률": f"{float(pattern['success_rate']):.2f}",
                    "함정비율": f"{float(pattern['trap_rate']):.2f}",
                }
            )
    return rows


def _fallback_rows_for_symbol(item: KiwoomSeedSymbol) -> list[dict[str, str]]:
    now = datetime.now().replace(second=0, microsecond=0)
    rows: list[dict[str, str]] = []
    for offset in range(3):
        ts = now.replace(minute=max(0, now.minute - (2 - offset)))
        rows.append(
            _minute_bar_row(
                symbol=item.symbol,
                timestamp=ts.isoformat(),
                price=item.base_price + offset * 100,
                turnover_billion=item.base_turnover_billion + offset * 1.5,
                program_net_buy_billion=item.base_program_net_buy_billion,
                source="fallback",
            )
        )
    return rows


def _minute_bar_row(
    symbol: str,
    timestamp: str,
    price: float,
    turnover_billion: float,
    program_net_buy_billion: float,
    source: str,
) -> dict[str, str]:
    return {
        "종목코드": symbol,
        "체결시각": timestamp,
        "현재가": _fmt_number(price),
        "분당거래대금_억": f"{turnover_billion:.1f}",
        "프로그램순매수_억": f"{program_net_buy_billion:.1f}",
        "데이터출처": source,
    }


def _write_raw_csv_bundle(
    output_dir: Path,
    payload: dict[str, list[dict[str, str]]],
) -> dict[str, Path]:
    outputs: dict[str, Path] = {}
    for filename, rows in payload.items():
        output_path = output_dir / filename
        fieldnames = _fieldnames_for_file(filename)
        _write_csv(output_path, fieldnames, rows)
        outputs[filename] = output_path
    return outputs


def _fieldnames_for_file(filename: str) -> list[str]:
    mapping = {
        "raw_symbol_profiles.csv": SYMBOL_PROFILE_FIELDS,
        "raw_minute_bars.csv": MINUTE_BAR_FIELDS,
        "raw_time_bucket_stats.csv": TIME_BUCKET_FIELDS,
    }
    return mapping[filename]


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _fmt_number(value: float) -> str:
    return str(int(value)) if value == int(value) else f"{value:.2f}"
