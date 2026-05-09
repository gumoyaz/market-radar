from __future__ import annotations

from app.breakout_logic import build_breakout_scorecard
from app.detectors import detect_pattern
from app.features import build_feature_snapshot
from app.models import MarketSnapshot, ScoredCandidate, SymbolInput


def _bucket_alignment(snapshot: MarketSnapshot, bucket: str) -> tuple[str, float]:
    success_rate = snapshot.time_bucket_bias.get(bucket, 0.5)
    if success_rate >= 0.62:
        return "strong", 10.0
    if success_rate <= 0.48:
        return "weak", 2.0
    return "neutral", 6.0


def score_watchlist(
    watchlist: list[SymbolInput],
    market_snapshot: MarketSnapshot,
    current_time_bucket: str = "09:10-09:20",
) -> list[ScoredCandidate]:
    ranked: list[ScoredCandidate] = []

    for symbol_input in watchlist:
        features = build_feature_snapshot(symbol_input, current_time_bucket)
        pattern = detect_pattern(features)
        bucket_alignment, time_score = _bucket_alignment(market_snapshot, features.time_bucket)
        scorecard = build_breakout_scorecard(
            symbol_input.theme_context,
            symbol_input.daily_context,
            symbol_input.news_context,
            symbol_input.leadership_context,
            features,
            market_snapshot,
            pattern,
        )

        total_score = round(min(scorecard.total_score + (time_score - 6.0), 100.0), 1)
        reasons = list(scorecard.reasons)
        reasons.append(f"time alignment={bucket_alignment}")
        reasons.append(f"market regime={market_snapshot.regime_label}")
        reasons.append(
            "T/D/M/N/L="
            f"{scorecard.theme_score:.0f}/"
            f"{scorecard.daily_score:.0f}/"
            f"{scorecard.minute_score:.0f}/"
            f"{scorecard.news_score:.0f}/"
            f"{scorecard.leadership_score:.0f}"
        )
        reasons.append(f"action={scorecard.action}")
        reasons.append(f"leader_choice={scorecard.leader_choice}")
        if pattern.name.value != "none":
            reasons.append(f"pattern={pattern.name.value}")
        for warning in scorecard.warnings:
            reasons.append(f"warn:{warning}")

        ranked.append(
            ScoredCandidate(
                symbol=symbol_input.profile.symbol,
                features=features,
                pattern=pattern,
                total_score=total_score,
                market_alignment=bucket_alignment,
                reasons=reasons,
                scorecard=scorecard,
            )
        )

    ranked.sort(key=lambda candidate: candidate.total_score, reverse=True)
    return ranked
