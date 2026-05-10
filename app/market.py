from __future__ import annotations

from collections import Counter, defaultdict

from app.detectors import detect_pattern
from app.features import build_feature_snapshot
from app.models import MarketSnapshot, PatternType, SymbolInput
from app.reference_data import build_reference_macro_indicators


def build_market_snapshot(watchlist: list[SymbolInput], current_time_bucket: str = "09:10-09:20") -> MarketSnapshot:
    pattern_counter: Counter[PatternType] = Counter()
    pattern_success_sum: defaultdict[PatternType, float] = defaultdict(float)
    pattern_success_count: defaultdict[PatternType, int] = defaultdict(int)
    time_bucket_success_sum: defaultdict[str, float] = defaultdict(float)
    time_bucket_success_count: defaultdict[str, int] = defaultdict(int)

    for symbol_input in watchlist:
        features = build_feature_snapshot(symbol_input, current_time_bucket)
        signal = detect_pattern(features)
        if signal.name != PatternType.NONE:
            pattern_counter[signal.name] += 1

        for stat in symbol_input.time_bucket_stats:
            pattern_success_sum[stat.pattern] += stat.success_rate
            pattern_success_count[stat.pattern] += 1
            time_bucket_success_sum[stat.bucket] += stat.success_rate
            time_bucket_success_count[stat.bucket] += 1

    pattern_bias = {
        pattern: pattern_success_sum[pattern] / pattern_success_count[pattern]
        for pattern in pattern_success_count
    }
    time_bias = {
        bucket: time_bucket_success_sum[bucket] / time_bucket_success_count[bucket]
        for bucket in time_bucket_success_count
    }

    avg_pattern_bias = sum(pattern_bias.values()) / len(pattern_bias) if pattern_bias else 0.5
    if avg_pattern_bias >= 0.62:
        regime_label = "favorable"
    elif avg_pattern_bias <= 0.48:
        regime_label = "trap"
    else:
        regime_label = "neutral"

    dominant_pattern = pattern_counter.most_common(1)[0][0].value if pattern_counter else PatternType.NONE.value
    best_time_bucket = (
        max(time_bias.items(), key=lambda item: item[1])[0] if time_bias else current_time_bucket
    )

    return MarketSnapshot(
        regime_label=regime_label,
        dominant_pattern=dominant_pattern,
        best_time_bucket=best_time_bucket,
        pattern_success_bias=pattern_bias,
        time_bucket_bias=time_bias,
        macro_indicators=build_reference_macro_indicators(),
    )
