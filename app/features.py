from __future__ import annotations

from app.models import FeatureSnapshot, SymbolInput, SizeGroup


SMALL_TURNOVER_THRESHOLD = 30.0
MID_LARGE_TURNOVER_THRESHOLD = 60.0


def threshold_for_size(size_group: SizeGroup) -> float:
    if size_group == SizeGroup.SMALL:
        return SMALL_TURNOVER_THRESHOLD
    return MID_LARGE_TURNOVER_THRESHOLD


def _safe_distance_pct(current: float, anchor: float) -> float:
    if anchor <= 0:
        return 0.0
    return ((current - anchor) / anchor) * 100.0


def build_feature_snapshot(symbol_input: SymbolInput, time_bucket: str) -> FeatureSnapshot:
    bars = symbol_input.recent_bars[-3:]
    latest = bars[-1]
    threshold = threshold_for_size(symbol_input.profile.size_group)
    sustain_count = sum(1 for bar in bars if bar.turnover_billion >= threshold)
    turnover_3m_avg = sum(bar.turnover_billion for bar in bars) / len(bars)
    turnover_3m_sustain_flag = sustain_count == 3
    current_price = latest.close

    closes = [bar.close for bar in bars]
    max_close = max(closes)
    min_close = min(closes)
    pullback_depth_pct = 0.0
    if max_close > 0:
        pullback_depth_pct = ((max_close - min_close) / max_close) * 100.0

    is_breaking_day_high = current_price >= symbol_input.profile.day_high
    is_breaking_prev_day_high = current_price >= symbol_input.profile.prev_day_high
    is_breaking_52w_high = current_price >= symbol_input.profile.high_52w
    is_pre_vi_setup = current_price < symbol_input.profile.vi_price and _safe_distance_pct(
        symbol_input.profile.vi_price, current_price
    ) <= 2.0

    rebreak_after_pullback_flag = (
        current_price >= closes[0]
        and pullback_depth_pct >= 0.8
        and turnover_3m_sustain_flag
    )

    return FeatureSnapshot(
        symbol=symbol_input.profile.symbol,
        size_group=symbol_input.profile.size_group,
        minute_turnover=latest.turnover_billion,
        turnover_3m_avg=turnover_3m_avg,
        turnover_3m_sustain_flag=turnover_3m_sustain_flag,
        turnover_vs_threshold_ratio=latest.turnover_billion / threshold,
        program_net_buy_3m=sum(bar.program_net_buy_billion for bar in bars),
        dist_to_day_high_pct=_safe_distance_pct(current_price, symbol_input.profile.day_high),
        dist_to_prev_day_high_pct=_safe_distance_pct(current_price, symbol_input.profile.prev_day_high),
        dist_to_52w_high_pct=_safe_distance_pct(current_price, symbol_input.profile.high_52w),
        dist_to_vi_pct=_safe_distance_pct(symbol_input.profile.vi_price, current_price),
        is_breaking_day_high=is_breaking_day_high,
        is_breaking_prev_day_high=is_breaking_prev_day_high,
        is_breaking_52w_high=is_breaking_52w_high,
        pullback_depth_pct=pullback_depth_pct,
        rebreak_after_pullback_flag=rebreak_after_pullback_flag,
        is_pre_vi_setup=is_pre_vi_setup,
        is_leader_stock=symbol_input.profile.is_leader_stock,
        time_bucket=time_bucket,
        data_source=latest.source,
    )
