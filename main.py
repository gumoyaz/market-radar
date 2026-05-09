from __future__ import annotations

import argparse
from pathlib import Path

from app.analysis import analyze_watchlist, render_analysis
from app.db import connect_db, ensure_schema
from app.ingest import import_csv_directory, load_watchlist_from_db, seed_sample_database
from app.sample_data import build_sample_watchlist


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Breakout analyzer")
    parser.add_argument(
        "--db-path",
        default="data/breakout.db",
        help="SQLite database path",
    )
    parser.add_argument(
        "--source",
        choices=("sample", "db"),
        default="sample",
        help="Choose analysis source",
    )
    parser.add_argument(
        "--seed-sample-db",
        action="store_true",
        help="Seed SQLite with bundled sample watchlist",
    )
    parser.add_argument(
        "--import-csv-dir",
        help="Import CSV files from a directory into SQLite before analysis",
    )
    parser.add_argument(
        "--time-bucket",
        default="09:10-09:20",
        help="Current market time bucket label",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_path = Path(args.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if args.source == "sample" and not args.seed_sample_db and not args.import_csv_dir:
        watchlist = build_sample_watchlist()
        print(render_analysis(analyze_watchlist(watchlist, args.time_bucket)))
        return

    with connect_db(db_path) as conn:
        ensure_schema(conn)

        if args.seed_sample_db:
            seed_sample_database(conn, build_sample_watchlist())

        if args.import_csv_dir:
            import_csv_directory(conn, Path(args.import_csv_dir))

        watchlist = load_watchlist_from_db(conn)
        if not watchlist:
            raise SystemExit(
                "No watchlist data found in the database. Use --seed-sample-db or --import-csv-dir first."
            )

        print(render_analysis(analyze_watchlist(watchlist, args.time_bucket)))


if __name__ == "__main__":
    main()
