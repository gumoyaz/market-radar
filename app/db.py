from __future__ import annotations

import sqlite3
from pathlib import Path


def connect_db(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS symbol_profiles (
            symbol TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            size_group TEXT NOT NULL,
            day_high REAL NOT NULL,
            prev_day_high REAL NOT NULL,
            high_52w REAL NOT NULL,
            vi_price REAL NOT NULL,
            is_leader_stock INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS minute_bars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            ts TEXT NOT NULL,
            close REAL NOT NULL,
            turnover_billion REAL NOT NULL,
            program_net_buy_billion REAL NOT NULL,
            source TEXT NOT NULL DEFAULT 'unknown',
            FOREIGN KEY(symbol) REFERENCES symbol_profiles(symbol)
        );

        CREATE TABLE IF NOT EXISTS time_bucket_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            bucket TEXT NOT NULL,
            pattern TEXT NOT NULL,
            success_rate REAL NOT NULL,
            trap_rate REAL NOT NULL,
            FOREIGN KEY(symbol) REFERENCES symbol_profiles(symbol)
        );

        CREATE INDEX IF NOT EXISTS idx_minute_bars_symbol_ts
        ON minute_bars(symbol, ts);

        CREATE INDEX IF NOT EXISTS idx_time_bucket_stats_symbol
        ON time_bucket_stats(symbol);
        """
    )

    _ensure_column(conn, "symbol_profiles", "theme_name", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(conn, "symbol_profiles", "theme_strength_percentile", "REAL NOT NULL DEFAULT 0")
    _ensure_column(conn, "symbol_profiles", "theme_breadth_ratio", "REAL NOT NULL DEFAULT 0")
    _ensure_column(conn, "symbol_profiles", "theme_leader_count", "INTEGER NOT NULL DEFAULT 0")
    _ensure_column(conn, "symbol_profiles", "theme_turnover_share_pct", "REAL NOT NULL DEFAULT 0")
    _ensure_column(conn, "symbol_profiles", "theme_persistence_days", "INTEGER NOT NULL DEFAULT 0")
    _ensure_column(conn, "symbol_profiles", "daily_distance_to_52w_high_pct", "REAL NOT NULL DEFAULT 100")
    _ensure_column(conn, "symbol_profiles", "daily_consolidation_days", "INTEGER NOT NULL DEFAULT 0")
    _ensure_column(conn, "symbol_profiles", "daily_consolidation_range_pct", "REAL NOT NULL DEFAULT 100")
    _ensure_column(conn, "symbol_profiles", "daily_turnover_ratio", "REAL NOT NULL DEFAULT 0")
    _ensure_column(conn, "symbol_profiles", "daily_close_position_pct", "REAL NOT NULL DEFAULT 0")
    _ensure_column(conn, "symbol_profiles", "news_has_news", "INTEGER NOT NULL DEFAULT 0")
    _ensure_column(conn, "symbol_profiles", "news_headline_strength", "REAL NOT NULL DEFAULT 0")
    _ensure_column(conn, "symbol_profiles", "news_source_count", "INTEGER NOT NULL DEFAULT 0")
    _ensure_column(conn, "symbol_profiles", "news_minutes_since_release", "INTEGER NOT NULL DEFAULT 9999")
    _ensure_column(conn, "symbol_profiles", "news_catalyst", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(conn, "symbol_profiles", "news_is_confirmed", "INTEGER NOT NULL DEFAULT 0")
    _ensure_column(conn, "symbol_profiles", "news_is_theme_aligned", "INTEGER NOT NULL DEFAULT 0")

    conn.commit()


def _ensure_column(conn: sqlite3.Connection, table_name: str, column_name: str, ddl: str) -> None:
    columns = {
        row["name"]
        for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    }
    if column_name in columns:
        return
    conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl}")
