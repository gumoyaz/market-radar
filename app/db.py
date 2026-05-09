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
    conn.commit()
