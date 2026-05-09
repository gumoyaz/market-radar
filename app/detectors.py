from __future__ import annotations

from app.models import FeatureSnapshot, PatternSignal, PatternType


def detect_pattern(features: FeatureSnapshot) -> PatternSignal:
    triggers: list[str] = []
    confidence = 0.0
    pattern = PatternType.NONE

    if features.is_breaking_52w_high:
        pattern = PatternType.HIGH_52W
        confidence = 0.95
        triggers.append("52w high breakout")
    elif features.is_breaking_day_high:
        pattern = PatternType.DAY_HIGH
        confidence = 0.9
        triggers.append("day high breakout")
    elif features.is_breaking_prev_day_high:
        pattern = PatternType.PREV_DAY_HIGH
        confidence = 0.82
        triggers.append("previous day high breakout")
    elif features.rebreak_after_pullback_flag:
        pattern = PatternType.REBREAK
        confidence = 0.88
        triggers.append("re-break after pullback")
    elif features.is_pre_vi_setup:
        pattern = PatternType.PRE_VI
        confidence = 0.78
        triggers.append("pre-VI compression")

    if features.turnover_3m_sustain_flag:
        triggers.append("3-minute turnover sustain")
        confidence += 0.03

    if features.program_net_buy_3m > 0:
        triggers.append("positive program net buy")
        confidence += 0.02

    if features.is_leader_stock:
        triggers.append("leader stock")
        confidence += 0.02

    return PatternSignal(
        name=pattern,
        confidence=min(confidence, 1.0),
        triggers=triggers,
    )
