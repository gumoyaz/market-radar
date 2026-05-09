from __future__ import annotations

from app.market import build_market_snapshot
from app.models import MarketSnapshot, ScoredCandidate, SymbolInput
from app.scoring import score_watchlist


def analyze_watchlist(
    watchlist: list[SymbolInput], current_time_bucket: str
) -> tuple[MarketSnapshot, list[ScoredCandidate]]:
    snapshot = build_market_snapshot(watchlist, current_time_bucket=current_time_bucket)
    ranked = score_watchlist(watchlist, snapshot, current_time_bucket=current_time_bucket)
    return snapshot, ranked


def render_analysis(result: tuple[MarketSnapshot, list[ScoredCandidate]]) -> str:
    snapshot, ranked = result
    lines = [
        f"Market regime: {snapshot.regime_label}",
        f"Dominant pattern: {snapshot.dominant_pattern}",
        f"Best time bucket: {snapshot.best_time_bucket}",
        "",
        "Top candidates",
        "-" * 80,
    ]

    for idx, candidate in enumerate(ranked, start=1):
        features = candidate.features
        lines.append(
            f"{idx:>2}. {candidate.symbol:<8} "
            f"score={candidate.total_score:>6.1f} "
            f"pattern={candidate.pattern.name:<18} "
            f"time={features.time_bucket:<11} "
            f"source={features.data_source:<9} "
            f"3m_sustain={str(features.turnover_3m_sustain_flag):<5} "
            f"program_3m={features.program_net_buy_3m:>5.1f} "
            f"market_fit={candidate.market_alignment:<10}"
        )
        lines.append(f"    reasons: {', '.join(candidate.reasons)}")

    return "\n".join(lines)
