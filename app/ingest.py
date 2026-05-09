from __future__ import annotations

import csv
import sqlite3
from collections import defaultdict
from pathlib import Path

from app.models import (
    DailyContext,
    MinuteBar,
    NewsContext,
    PatternType,
    SizeGroup,
    SymbolInput,
    SymbolProfile,
    ThemeContext,
    TimeBucketStat,
)


def seed_sample_database(conn: sqlite3.Connection, watchlist: list[SymbolInput]) -> None:
    conn.execute("DELETE FROM time_bucket_stats")
    conn.execute("DELETE FROM minute_bars")
    conn.execute("DELETE FROM symbol_profiles")

    for symbol_input in watchlist:
        _insert_symbol_profile(
            conn,
            symbol_input.profile,
            symbol_input.theme_context,
            symbol_input.daily_context,
            symbol_input.news_context,
        )
        _insert_minute_bars(conn, symbol_input.profile.symbol, symbol_input.recent_bars)
        _insert_time_bucket_stats(conn, symbol_input.profile.symbol, symbol_input.time_bucket_stats)

    conn.commit()


def import_csv_directory(conn: sqlite3.Connection, directory: Path) -> None:
    profiles_path = directory / "symbol_profiles.csv"
    minute_bars_path = directory / "minute_bars.csv"
    time_stats_path = directory / "time_bucket_stats.csv"

    if not profiles_path.exists():
        raise FileNotFoundError(f"Missing {profiles_path}")
    if not minute_bars_path.exists():
        raise FileNotFoundError(f"Missing {minute_bars_path}")
    if not time_stats_path.exists():
        raise FileNotFoundError(f"Missing {time_stats_path}")

    conn.execute("DELETE FROM time_bucket_stats")
    conn.execute("DELETE FROM minute_bars")
    conn.execute("DELETE FROM symbol_profiles")

    with profiles_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            profile = SymbolProfile(
                symbol=row["symbol"],
                name=row["name"],
                size_group=SizeGroup(row["size_group"]),
                day_high=float(row["day_high"]),
                prev_day_high=float(row["prev_day_high"]),
                high_52w=float(row["high_52w"]),
                vi_price=float(row["vi_price"]),
                is_leader_stock=row["is_leader_stock"].strip().lower() in {"1", "true", "yes", "y"},
            )
            theme_context = ThemeContext(
                theme_name=row.get("theme_name", ""),
                strength_percentile=_float_value(row.get("theme_strength_percentile"), 0.0),
                breadth_ratio=_float_value(row.get("theme_breadth_ratio"), 0.0),
                leader_count=_int_value(row.get("theme_leader_count"), 0),
                turnover_share_pct=_float_value(row.get("theme_turnover_share_pct"), 0.0),
                persistence_days=_int_value(row.get("theme_persistence_days"), 0),
            )
            daily_context = DailyContext(
                distance_to_52w_high_pct=_float_value(row.get("daily_distance_to_52w_high_pct"), 100.0),
                consolidation_days=_int_value(row.get("daily_consolidation_days"), 0),
                consolidation_range_pct=_float_value(row.get("daily_consolidation_range_pct"), 100.0),
                daily_turnover_ratio=_float_value(row.get("daily_turnover_ratio"), 0.0),
                close_position_pct=_float_value(row.get("daily_close_position_pct"), 0.0),
            )
            news_context = NewsContext(
                has_news=_bool_value(row.get("news_has_news"), False),
                headline_strength=_float_value(row.get("news_headline_strength"), 0.0),
                source_count=_int_value(row.get("news_source_count"), 0),
                minutes_since_release=_int_value(row.get("news_minutes_since_release"), 9_999),
                catalyst=row.get("news_catalyst", ""),
                is_confirmed=_bool_value(row.get("news_is_confirmed"), False),
                is_theme_aligned=_bool_value(row.get("news_is_theme_aligned"), False),
            )
            _insert_symbol_profile(conn, profile, theme_context, daily_context, news_context)

    with minute_bars_path.open("r", encoding="utf-8-sig", newline="") as handle:
        grouped: defaultdict[str, list[tuple[str, MinuteBar]]] = defaultdict(list)
        for row in csv.DictReader(handle):
            grouped[row["symbol"]].append(
                (
                    row["ts"],
                    MinuteBar(
                        close=float(row["close"]),
                        turnover_billion=float(row["turnover_billion"]),
                        program_net_buy_billion=float(row["program_net_buy_billion"]),
                        source=row.get("source", "unknown"),
                    ),
                )
            )

    for symbol, items in grouped.items():
        items.sort(key=lambda item: item[0])
        _insert_minute_bars(conn, symbol, [item[1] for item in items], [item[0] for item in items])

    with time_stats_path.open("r", encoding="utf-8-sig", newline="") as handle:
        grouped_stats: defaultdict[str, list[TimeBucketStat]] = defaultdict(list)
        for row in csv.DictReader(handle):
            grouped_stats[row["symbol"]].append(
                TimeBucketStat(
                    bucket=row["bucket"],
                    pattern=PatternType(row["pattern"]),
                    success_rate=float(row["success_rate"]),
                    trap_rate=float(row["trap_rate"]),
                )
            )

    for symbol, stats in grouped_stats.items():
        _insert_time_bucket_stats(conn, symbol, stats)

    conn.commit()


def load_watchlist_from_db(conn: sqlite3.Connection) -> list[SymbolInput]:
    profiles = conn.execute(
        """
        SELECT
            symbol,
            name,
            size_group,
            day_high,
            prev_day_high,
            high_52w,
            vi_price,
            is_leader_stock,
            theme_name,
            theme_strength_percentile,
            theme_breadth_ratio,
            theme_leader_count,
            theme_turnover_share_pct,
            theme_persistence_days,
            daily_distance_to_52w_high_pct,
            daily_consolidation_days,
            daily_consolidation_range_pct,
            daily_turnover_ratio,
            daily_close_position_pct,
            news_has_news,
            news_headline_strength,
            news_source_count,
            news_minutes_since_release,
            news_catalyst,
            news_is_confirmed,
            news_is_theme_aligned
        FROM symbol_profiles
        ORDER BY symbol
        """
    ).fetchall()

    if not profiles:
        return []

    minute_rows = conn.execute(
        """
        SELECT symbol, ts, close, turnover_billion, program_net_buy_billion, source
        FROM minute_bars
        ORDER BY symbol, ts DESC
        """
    ).fetchall()

    minute_grouped: defaultdict[str, list[sqlite3.Row]] = defaultdict(list)
    for row in minute_rows:
        if len(minute_grouped[row["symbol"]]) < 3:
            minute_grouped[row["symbol"]].append(row)

    time_stat_rows = conn.execute(
        """
        SELECT symbol, bucket, pattern, success_rate, trap_rate
        FROM time_bucket_stats
        ORDER BY symbol, bucket
        """
    ).fetchall()

    time_stats_grouped: defaultdict[str, list[TimeBucketStat]] = defaultdict(list)
    for row in time_stat_rows:
        time_stats_grouped[row["symbol"]].append(
            TimeBucketStat(
                bucket=row["bucket"],
                pattern=PatternType(row["pattern"]),
                success_rate=row["success_rate"],
                trap_rate=row["trap_rate"],
            )
        )

    watchlist: list[SymbolInput] = []
    for row in profiles:
        latest_bars = list(reversed(minute_grouped[row["symbol"]]))
        if len(latest_bars) < 3:
            continue

        watchlist.append(
            SymbolInput(
                profile=SymbolProfile(
                    symbol=row["symbol"],
                    name=row["name"],
                    size_group=SizeGroup(row["size_group"]),
                    day_high=row["day_high"],
                    prev_day_high=row["prev_day_high"],
                    high_52w=row["high_52w"],
                    vi_price=row["vi_price"],
                    is_leader_stock=bool(row["is_leader_stock"]),
                ),
                recent_bars=[
                    MinuteBar(
                        close=bar["close"],
                        turnover_billion=bar["turnover_billion"],
                        program_net_buy_billion=bar["program_net_buy_billion"],
                        source=bar["source"],
                    )
                    for bar in latest_bars
                ],
                time_bucket_stats=time_stats_grouped[row["symbol"]],
                theme_context=ThemeContext(
                    theme_name=row["theme_name"],
                    strength_percentile=row["theme_strength_percentile"],
                    breadth_ratio=row["theme_breadth_ratio"],
                    leader_count=row["theme_leader_count"],
                    turnover_share_pct=row["theme_turnover_share_pct"],
                    persistence_days=row["theme_persistence_days"],
                ),
                daily_context=DailyContext(
                    distance_to_52w_high_pct=row["daily_distance_to_52w_high_pct"],
                    consolidation_days=row["daily_consolidation_days"],
                    consolidation_range_pct=row["daily_consolidation_range_pct"],
                    daily_turnover_ratio=row["daily_turnover_ratio"],
                    close_position_pct=row["daily_close_position_pct"],
                ),
                news_context=NewsContext(
                    has_news=bool(row["news_has_news"]),
                    headline_strength=row["news_headline_strength"],
                    source_count=row["news_source_count"],
                    minutes_since_release=row["news_minutes_since_release"],
                    catalyst=row["news_catalyst"],
                    is_confirmed=bool(row["news_is_confirmed"]),
                    is_theme_aligned=bool(row["news_is_theme_aligned"]),
                ),
            )
        )

    return watchlist


def _insert_symbol_profile(
    conn: sqlite3.Connection,
    profile: SymbolProfile,
    theme_context: ThemeContext | None = None,
    daily_context: DailyContext | None = None,
    news_context: NewsContext | None = None,
) -> None:
    theme_context = theme_context or ThemeContext()
    daily_context = daily_context or DailyContext()
    news_context = news_context or NewsContext()

    conn.execute(
        """
        INSERT INTO symbol_profiles (
            symbol, name, size_group, day_high, prev_day_high, high_52w, vi_price, is_leader_stock,
            theme_name, theme_strength_percentile, theme_breadth_ratio, theme_leader_count,
            theme_turnover_share_pct, theme_persistence_days,
            daily_distance_to_52w_high_pct, daily_consolidation_days, daily_consolidation_range_pct,
            daily_turnover_ratio, daily_close_position_pct,
            news_has_news, news_headline_strength, news_source_count, news_minutes_since_release,
            news_catalyst, news_is_confirmed, news_is_theme_aligned
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            profile.symbol,
            profile.name,
            profile.size_group.value,
            profile.day_high,
            profile.prev_day_high,
            profile.high_52w,
            profile.vi_price,
            int(profile.is_leader_stock),
            theme_context.theme_name,
            theme_context.strength_percentile,
            theme_context.breadth_ratio,
            theme_context.leader_count,
            theme_context.turnover_share_pct,
            theme_context.persistence_days,
            daily_context.distance_to_52w_high_pct,
            daily_context.consolidation_days,
            daily_context.consolidation_range_pct,
            daily_context.daily_turnover_ratio,
            daily_context.close_position_pct,
            int(news_context.has_news),
            news_context.headline_strength,
            news_context.source_count,
            news_context.minutes_since_release,
            news_context.catalyst,
            int(news_context.is_confirmed),
            int(news_context.is_theme_aligned),
        ),
    )


def _insert_minute_bars(
    conn: sqlite3.Connection,
    symbol: str,
    bars: list[MinuteBar],
    timestamps: list[str] | None = None,
) -> None:
    if timestamps is None:
        timestamps = [f"sample-{index:02d}" for index in range(len(bars))]

    conn.executemany(
        """
        INSERT INTO minute_bars (
            symbol, ts, close, turnover_billion, program_net_buy_billion, source
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                symbol,
                ts,
                bar.close,
                bar.turnover_billion,
                bar.program_net_buy_billion,
                bar.source,
            )
            for ts, bar in zip(timestamps, bars, strict=True)
        ],
    )


def _insert_time_bucket_stats(
    conn: sqlite3.Connection,
    symbol: str,
    stats: list[TimeBucketStat],
) -> None:
    conn.executemany(
        """
        INSERT INTO time_bucket_stats (
            symbol, bucket, pattern, success_rate, trap_rate
        ) VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                symbol,
                stat.bucket,
                stat.pattern.value,
                stat.success_rate,
                stat.trap_rate,
            )
            for stat in stats
        ],
    )


def _bool_value(value: str | None, default: bool) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "y"}


def _float_value(value: str | None, default: float) -> float:
    if value is None or value == "":
        return default
    return float(value)


def _int_value(value: str | None, default: int) -> int:
    if value is None or value == "":
        return default
    return int(float(value))
