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
        f"Macro board: {', '.join(f'{item.label} {item.price_text} ({item.change_pct:+.2f}%)' for item in snapshot.macro_indicators[:6])}",
        "",
        "Top candidates",
        "-" * 80,
    ]

    for idx, candidate in enumerate(ranked, start=1):
        features = candidate.features
        scorecard = candidate.scorecard
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
        if scorecard is not None:
            lines.append(
                "    scorecard: "
                f"theme={scorecard.theme_score:.1f} "
                f"daily={scorecard.daily_score:.1f} "
                f"minute={scorecard.minute_score:.1f} "
                f"news={scorecard.news_score:.1f} "
                f"leadership={scorecard.leadership_score:.1f} "
                f"stage={scorecard.stage.value} "
                f"action={scorecard.action} "
                f"leader_choice={scorecard.leader_choice}"
            )

    return "\n".join(lines)
