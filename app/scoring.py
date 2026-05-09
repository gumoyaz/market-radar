from __future__ import annotations

from app.detectors import detect_pattern
from app.features import build_feature_snapshot
from app.models import MarketSnapshot, PatternType, ScoredCandidate, SymbolInput


def _bucket_alignment(snapshot: MarketSnapshot, bucket: str) -> tuple[str, float]:
    success_rate = snapshot.time_bucket_bias.get(bucket, 0.5)
    if success_rate >= 0.62:
        return "strong", 10.0
    if success_rate <= 0.48:
        return "weak", 2.0
    return "neutral", 6.0


def _pattern_score(pattern_name: PatternType) -> float:
    base = {
        PatternType.HIGH_52W: 24.0,
        PatternType.DAY_HIGH: 22.0,
        PatternType.PREV_DAY_HIGH: 18.0,
        PatternType.REBREAK: 21.0,
        PatternType.PRE_VI: 16.0,
        PatternType.NONE: 0.0,
    }
    return base[pattern_name]


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

        liquidity_score = min(features.turnover_vs_threshold_ratio * 12.0, 30.0)
        sustain_score = 15.0 if features.turnover_3m_sustain_flag else 0.0
        program_score = min(max(features.program_net_buy_3m, 0.0) * 1.5, 10.0)
        leader_score = 8.0 if features.is_leader_stock else 0.0
        pattern_score = _pattern_score(pattern.name)
        market_pattern_bonus = market_snapshot.pattern_success_bias.get(pattern.name, 0.5) * 12.0

        total_score = (
            liquidity_score
            + sustain_score
            + program_score
            + leader_score
            + pattern_score
            + time_score
            + market_pattern_bonus
        )

        reasons = []
        if features.turnover_3m_sustain_flag:
            reasons.append("3분 거래대금 지속")
        if pattern.name != PatternType.NONE:
            reasons.append(f"패턴={pattern.name.value}")
        if features.program_net_buy_3m > 0:
            reasons.append("프로그램 순매수 우위")
        if features.is_leader_stock:
            reasons.append("주도주 필터 통과")
        reasons.append(f"시간대 적합도={bucket_alignment}")
        reasons.append(f"시장상태={market_snapshot.regime_label}")

        ranked.append(
            ScoredCandidate(
                symbol=symbol_input.profile.symbol,
                features=features,
                pattern=pattern,
                total_score=round(total_score, 1),
                market_alignment=bucket_alignment,
                reasons=reasons,
            )
        )

    ranked.sort(key=lambda candidate: candidate.total_score, reverse=True)
    return ranked
