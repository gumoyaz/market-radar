from __future__ import annotations

from app.models import (
    BreakoutScorecard,
    BreakoutStage,
    DailyContext,
    FeatureSnapshot,
    LeadershipContext,
    MarketSnapshot,
    NewsContext,
    PatternSignal,
    ThemeContext,
)


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(value, high))


def _scale(value: float, good_floor: float, good_ceiling: float) -> float:
    if good_ceiling <= good_floor:
        return 0.0
    normalized = ((value - good_floor) / (good_ceiling - good_floor)) * 100.0
    return _clamp(normalized)


def _inverse_scale(value: float, ideal_floor: float, ideal_ceiling: float) -> float:
    if value <= ideal_floor:
        return 100.0
    if value >= ideal_ceiling:
        return 0.0
    span = ideal_ceiling - ideal_floor
    if span <= 0:
        return 0.0
    normalized = (1.0 - ((value - ideal_floor) / span)) * 100.0
    return _clamp(normalized)


def _rank_score(rank: int, worst_rank: int = 5) -> float:
    if rank <= 1:
        return 100.0
    if rank <= 2:
        return 86.0
    if rank <= 3:
        return 72.0
    if rank <= worst_rank:
        return 52.0
    return 18.0


def score_theme_context(theme: ThemeContext) -> tuple[float, list[str], list[str]]:
    rank_score = _clamp(theme.strength_percentile)
    breadth_score = _clamp(theme.breadth_ratio * 100.0)
    leader_score = _scale(theme.leader_count, 0.0, 4.0)
    turnover_score = _scale(theme.turnover_share_pct, 5.0, 30.0)
    persistence_score = _scale(theme.persistence_days, 0.0, 4.0)

    total = (
        rank_score * 0.30
        + breadth_score * 0.20
        + leader_score * 0.15
        + turnover_score * 0.20
        + persistence_score * 0.15
    )

    reasons: list[str] = []
    warnings: list[str] = []

    if theme.theme_name:
        reasons.append(f"theme={theme.theme_name}")
    if theme.strength_percentile >= 70:
        reasons.append("theme percentile strong")
    else:
        warnings.append("theme percentile not strong enough")
    if theme.breadth_ratio >= 0.40:
        reasons.append("theme breadth healthy")
    else:
        warnings.append("theme breadth narrow")
    if theme.persistence_days >= 2:
        reasons.append("theme persistence confirmed")
    else:
        warnings.append("theme persistence still shallow")

    return round(total, 1), reasons, warnings


def score_daily_context(daily: DailyContext) -> tuple[float, list[str], list[str]]:
    high_proximity_score = _inverse_scale(daily.distance_to_52w_high_pct, 0.0, 8.0)
    base_days_score = _scale(daily.consolidation_days, 5.0, 40.0)
    compression_score = _inverse_scale(daily.consolidation_range_pct, 8.0, 35.0)
    turnover_score = _scale(daily.daily_turnover_ratio, 1.0, 3.5)
    close_score = _clamp(daily.close_position_pct)

    total = (
        high_proximity_score * 0.30
        + base_days_score * 0.20
        + compression_score * 0.15
        + turnover_score * 0.20
        + close_score * 0.15
    )

    reasons: list[str] = []
    warnings: list[str] = []

    if daily.distance_to_52w_high_pct <= 3.0:
        reasons.append("daily near 52-week high")
    else:
        warnings.append("daily too far from 52-week high")
    if daily.consolidation_days >= 20:
        reasons.append("daily base long enough")
    else:
        warnings.append("daily base still short")
    if daily.daily_turnover_ratio >= 2.0:
        reasons.append("daily turnover expansion confirmed")
    else:
        warnings.append("daily turnover expansion weak")

    return round(total, 1), reasons, warnings


def classify_breakout_stage(features: FeatureSnapshot) -> BreakoutStage:
    if features.turnover_3m_sustain_flag and features.dist_to_day_high_pct >= 1.5:
        return BreakoutStage.EXTENDED
    if features.turnover_3m_sustain_flag and features.dist_to_day_high_pct >= 0.2:
        return BreakoutStage.HOLDING
    if features.turnover_3m_sustain_flag and features.is_breaking_day_high:
        return BreakoutStage.BREAKING
    if features.turnover_vs_threshold_ratio >= 1.0 and features.dist_to_day_high_pct >= -0.7:
        return BreakoutStage.PROBING
    if features.dist_to_day_high_pct <= -1.2 and features.turnover_vs_threshold_ratio < 1.0:
        return BreakoutStage.FAILED
    return BreakoutStage.WAIT


def score_minute_context(
    features: FeatureSnapshot,
    market_snapshot: MarketSnapshot,
    pattern: PatternSignal,
) -> tuple[float, BreakoutStage, list[str], list[str]]:
    stage = classify_breakout_stage(features)

    stage_score_map = {
        BreakoutStage.WAIT: 20.0,
        BreakoutStage.PROBING: 55.0,
        BreakoutStage.BREAKING: 78.0,
        BreakoutStage.HOLDING: 88.0,
        BreakoutStage.EXTENDED: 72.0,
        BreakoutStage.FAILED: 5.0,
    }
    stage_score = stage_score_map[stage]
    sustain_score = 100.0 if features.turnover_3m_sustain_flag else 25.0
    turnover_score = _clamp(features.turnover_vs_threshold_ratio * 40.0)
    program_score = _scale(features.program_net_buy_3m, 0.0, 4.0)
    market_fit_score = _clamp(market_snapshot.time_bucket_bias.get(features.time_bucket, 0.5) * 100.0)
    pattern_score = _clamp(pattern.confidence * 100.0)

    total = (
        stage_score * 0.30
        + sustain_score * 0.20
        + turnover_score * 0.15
        + program_score * 0.10
        + market_fit_score * 0.10
        + pattern_score * 0.15
    )

    reasons: list[str] = [f"minute stage={stage.value}"]
    warnings: list[str] = []

    if features.turnover_3m_sustain_flag:
        reasons.append("3-minute turnover sustain confirmed")
    else:
        warnings.append("3-minute turnover sustain missing")
    if features.program_net_buy_3m > 0:
        reasons.append("program net buy supportive")
    else:
        warnings.append("program net buy not supportive")
    if stage == BreakoutStage.EXTENDED:
        warnings.append("already extended above day high")
    if stage == BreakoutStage.FAILED:
        warnings.append("breakout attempt currently weak")

    return round(total, 1), stage, reasons, warnings


def score_news_context(news: NewsContext) -> tuple[float, list[str], list[str]]:
    if not news.has_news:
        return 15.0, ["no major fresh news"], ["catalyst not confirmed by news"]

    strength_score = _clamp(news.headline_strength)
    source_score = _scale(news.source_count, 1.0, 5.0)
    if news.minutes_since_release <= 30:
        recency_score = 100.0
    elif news.minutes_since_release <= 120:
        recency_score = 80.0
    elif news.minutes_since_release <= 360:
        recency_score = 60.0
    elif news.minutes_since_release <= 1_440:
        recency_score = 40.0
    else:
        recency_score = 20.0
    alignment_score = 100.0 if news.is_theme_aligned else 40.0
    confirmation_score = 100.0 if news.is_confirmed else 50.0

    total = (
        strength_score * 0.35
        + source_score * 0.15
        + recency_score * 0.20
        + alignment_score * 0.15
        + confirmation_score * 0.15
    )

    reasons: list[str] = []
    warnings: list[str] = []

    if news.catalyst:
        reasons.append(f"catalyst={news.catalyst}")
    if news.headline_strength >= 70:
        reasons.append("news strength high")
    else:
        warnings.append("news strength moderate")
    if news.is_theme_aligned:
        reasons.append("news aligned with theme")
    else:
        warnings.append("news not clearly aligned with theme")

    return round(total, 1), reasons, warnings


def score_leadership_context(
    leadership: LeadershipContext,
    theme: ThemeContext,
    news: NewsContext,
    stage: BreakoutStage,
    market_snapshot: MarketSnapshot,
) -> tuple[float, str, list[str], list[str]]:
    turnover_rank_score = _rank_score(leadership.turnover_rank)
    return_rank_score = _rank_score(leadership.return_rank)
    turnover_share_score = _scale(leadership.turnover_share_pct, 10.0, 40.0)
    return_strength_score = _scale(leadership.intraday_return_pct, 4.0, 24.0)
    turnover_gap_score = _scale(leadership.gap_from_next_turnover_pct, 0.0, 12.0)
    return_gap_score = _scale(leadership.gap_from_next_return_pct, 0.0, 8.0)
    persistence_score = _scale(leadership.move_persistence_minutes, 2.0, 30.0)
    news_lead_score = 100.0 if leadership.is_news_leader else 45.0

    total = (
        turnover_rank_score * 0.20
        + return_rank_score * 0.20
        + turnover_share_score * 0.18
        + return_strength_score * 0.10
        + turnover_gap_score * 0.08
        + return_gap_score * 0.06
        + persistence_score * 0.10
        + news_lead_score * 0.08
    )

    reasons: list[str] = []
    warnings: list[str] = []

    if leadership.turnover_rank <= 2:
        reasons.append("theme turnover rank near top")
    else:
        warnings.append("turnover rank not leading theme")
    if leadership.return_rank <= 2:
        reasons.append("theme return rank near top")
    else:
        warnings.append("return rank not leading theme")
    if leadership.move_persistence_minutes >= 10:
        reasons.append("price leadership persisted")
    else:
        warnings.append("leadership persistence still short")

    fresh_aligned_news = (
        news.has_news
        and news.is_theme_aligned
        and news.headline_strength >= 70.0
        and news.minutes_since_release <= 60
    )
    early_theme = leadership.theme_member_count <= 3 and theme.persistence_days <= 2
    broad_theme = leadership.theme_member_count >= 5 or theme.breadth_ratio >= 0.45
    strong_turnover_lead = leadership.turnover_rank == 1 and leadership.turnover_share_pct >= 22.0
    strong_return_lead = leadership.return_rank == 1 and leadership.intraday_return_pct >= 10.0
    close_turnover = leadership.turnover_rank <= 2
    close_return = leadership.return_rank <= 2

    if strong_turnover_lead and close_return:
        leader_choice = "buy_dual_leader"
        if leadership.return_rank == 1:
            reasons.append("same symbol leads both money flow and price")
        else:
            reasons.append("money leader also remains top-tier price mover")
    elif (
        strong_return_lead
        and close_turnover
        and fresh_aligned_news
        and early_theme
        and stage in {BreakoutStage.PROBING, BreakoutStage.BREAKING, BreakoutStage.HOLDING}
    ):
        leader_choice = "buy_return_leader"
        reasons.append("fresh catalyst supports fastest mover")
    elif (
        strong_turnover_lead
        and leadership.return_rank <= 3
        and (
            broad_theme
            or not fresh_aligned_news
            or stage in {BreakoutStage.HOLDING, BreakoutStage.EXTENDED}
            or market_snapshot.regime_label == "trap"
        )
    ):
        leader_choice = "buy_turnover_leader"
        reasons.append("money concentration more trustworthy than raw speed")
    elif strong_return_lead and leadership.turnover_rank >= 4:
        leader_choice = "wait_for_resolution"
        warnings.append("top return diverges too much from money flow leader")
    elif strong_turnover_lead and leadership.return_rank >= 4:
        leader_choice = "buy_turnover_leader"
        reasons.append("lagging price but clear money leader")
    else:
        leader_choice = "wait_for_resolution"
        warnings.append("no clean leader separation inside theme yet")

    return round(_clamp(total), 1), leader_choice, reasons, warnings


def build_breakout_scorecard(
    theme: ThemeContext,
    daily: DailyContext,
    news: NewsContext,
    leadership: LeadershipContext,
    features: FeatureSnapshot,
    market_snapshot: MarketSnapshot,
    pattern: PatternSignal,
) -> BreakoutScorecard:
    theme_score, theme_reasons, theme_warnings = score_theme_context(theme)
    daily_score, daily_reasons, daily_warnings = score_daily_context(daily)
    minute_score, stage, minute_reasons, minute_warnings = score_minute_context(
        features,
        market_snapshot,
        pattern,
    )
    news_score, news_reasons, news_warnings = score_news_context(news)
    leadership_score, leader_choice, leader_reasons, leader_warnings = score_leadership_context(
        leadership,
        theme,
        news,
        stage,
        market_snapshot,
    )

    total = (
        theme_score * 0.28
        + daily_score * 0.27
        + minute_score * 0.30
        + news_score * 0.15
    )

    if theme_score >= 70 and news_score >= 70:
        total += 4.0
    if daily_score >= 70 and stage in {BreakoutStage.BREAKING, BreakoutStage.HOLDING}:
        total += 4.0
    if market_snapshot.regime_label == "favorable":
        total += 3.0
    elif market_snapshot.regime_label == "trap":
        total -= 6.0
    if news_score < 20 and theme_score < 50:
        total -= 6.0
    if stage == BreakoutStage.FAILED:
        total -= 8.0
    if leader_choice == "buy_dual_leader":
        total += 4.0
    elif leader_choice in {"buy_turnover_leader", "buy_return_leader"}:
        total += 2.0
    elif leader_choice == "wait_for_resolution":
        total -= 3.0

    total = round(_clamp(total), 1)

    if stage == BreakoutStage.FAILED or minute_score < 35:
        action = "avoid"
    elif stage == BreakoutStage.EXTENDED and total >= 70:
        action = "too_extended"
    elif leader_choice == "wait_for_resolution" and total >= 75:
        action = "stalk"
    elif total >= 80 and stage in {BreakoutStage.BREAKING, BreakoutStage.HOLDING}:
        action = "actionable"
    elif total >= 65:
        action = "stalk"
    else:
        action = "watch"

    reasons = theme_reasons + daily_reasons + minute_reasons + news_reasons + leader_reasons
    warnings = theme_warnings + daily_warnings + minute_warnings + news_warnings + leader_warnings

    return BreakoutScorecard(
        theme_score=theme_score,
        daily_score=daily_score,
        minute_score=minute_score,
        news_score=news_score,
        leadership_score=leadership_score,
        total_score=total,
        stage=stage,
        action=action,
        leader_choice=leader_choice,
        reasons=reasons,
        warnings=warnings,
    )
