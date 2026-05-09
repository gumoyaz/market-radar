from __future__ import annotations

import argparse
import time
from datetime import datetime
from pathlib import Path

from app.analysis import analyze_watchlist
from app.db import connect_db, ensure_schema
from app.ingest import import_csv_directory, load_watchlist_from_db
from app.reporting import write_html_report
from app.serializers import write_json_snapshot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Breakout analyzer monitor loop")
    parser.add_argument(
        "--db-path",
        default="data/live.db",
        help="SQLite database path",
    )
    parser.add_argument(
        "--import-csv-dir",
        default="data/sample_csv",
        help="Directory containing CSV files to ingest",
    )
    parser.add_argument(
        "--output-html",
        default="output/live-dashboard.html",
        help="Output HTML report path",
    )
    parser.add_argument(
        "--output-json",
        default="output/live-dashboard.json",
        help="Output JSON snapshot path",
    )
    parser.add_argument(
        "--time-bucket",
        default="09:10-09:20",
        help="Current market time bucket label",
    )
    parser.add_argument(
        "--interval-sec",
        type=int,
        default=60,
        help="Seconds between refresh cycles",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="Number of refresh cycles to run. Use 0 for infinite loop.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_path = Path(args.db_path)
    html_path = Path(args.output_html)
    json_path = Path(args.output_json)
    csv_dir = Path(args.import_csv_dir)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    run_count = 0
    while True:
        run_count += 1
        run_started = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with connect_db(db_path) as conn:
            ensure_schema(conn)
            import_csv_directory(conn, csv_dir)
            watchlist = load_watchlist_from_db(conn)

        if not watchlist:
            raise SystemExit("No watchlist data loaded from CSV directory.")

        result = analyze_watchlist(watchlist, args.time_bucket)
        write_html_report(result, html_path)
        write_json_snapshot(result, json_path, generated_at=run_started)

        snapshot, ranked = result
        top_name = ranked[0].symbol if ranked else "N/A"
        top_score = f"{ranked[0].total_score:.1f}" if ranked else "0.0"
        print(
            f"[{run_started}] cycle={run_count} "
            f"regime={snapshot.regime_label} top={top_name} score={top_score} "
            f"html={html_path} json={json_path}"
        )

        if args.cycles and run_count >= args.cycles:
            break

        time.sleep(args.interval_sec)


if __name__ == "__main__":
    main()
