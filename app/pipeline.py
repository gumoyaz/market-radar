from __future__ import annotations

from datetime import datetime
from pathlib import Path

from app.analysis import analyze_watchlist, render_analysis
from app.db import connect_db, ensure_schema
from app.header_inspector import inspect_csv_directory, write_report
from app.ingest import import_csv_directory, load_watchlist_from_db
from app.normalize import normalize_csv_directory
from app.reporting import write_html_report
from app.serializers import write_json_snapshot


def run_pipeline(
    raw_dir: Path,
    mapping_path: Path,
    workspace: Path,
    time_bucket: str,
) -> dict[str, Path]:
    reports_dir = workspace / "reports"
    normalized_dir = workspace / "normalized"
    db_dir = workspace / "db"
    snapshots_dir = workspace / "snapshots"

    reports_dir.mkdir(parents=True, exist_ok=True)
    normalized_dir.mkdir(parents=True, exist_ok=True)
    db_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    header_report_path = reports_dir / "csv-header-report.md"
    starter_mapping_path = reports_dir / "starter-mapping.json"
    inspection = inspect_csv_directory(raw_dir)
    write_report(inspection, header_report_path, starter_mapping_path)

    normalized_paths = normalize_csv_directory(raw_dir, mapping_path, normalized_dir)
    if not normalized_paths:
        raise ValueError("No normalized CSV files were written. Check the mapping file.")

    db_path = db_dir / "breakout.db"
    with connect_db(db_path) as conn:
        ensure_schema(conn)
        import_csv_directory(conn, normalized_dir)
        watchlist = load_watchlist_from_db(conn)

    if not watchlist:
        raise ValueError("No watchlist data loaded after normalization and import.")

    analysis_result = analyze_watchlist(watchlist, time_bucket)
    console_report_path = reports_dir / "analysis.txt"
    console_report_path.write_text(render_analysis(analysis_result), encoding="utf-8")

    html_path = snapshots_dir / "dashboard.html"
    json_path = snapshots_dir / "dashboard.json"
    write_html_report(analysis_result, html_path)
    write_json_snapshot(
        analysis_result,
        json_path,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    return {
        "header_report": header_report_path,
        "starter_mapping": starter_mapping_path,
        "normalized_dir": normalized_dir,
        "database": db_path,
        "analysis_report": console_report_path,
        "dashboard_html": html_path,
        "dashboard_json": json_path,
    }
