from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SizeGroup(str, Enum):
    SMALL = "small"
    MID = "mid"
    LARGE = "large"


class PatternType(str, Enum):
    NONE = "none"
    DAY_HIGH = "day_high"
    PREV_DAY_HIGH = "prev_day_high"
    HIGH_52W = "high_52w"
    REBREAK = "rebreak"
    PRE_VI = "pre_vi"


@dataclass(frozen=True)
class MinuteBar:
    close: float
    turnover_billion: float
    program_net_buy_billion: float
    source: str = "unknown"


@dataclass(frozen=True)
class SymbolProfile:
    symbol: str
    name: str
    size_group: SizeGroup
    day_high: float
    prev_day_high: float
    high_52w: float
    vi_price: float
    is_leader_stock: bool


@dataclass(frozen=True)
class TimeBucketStat:
    bucket: str
    pattern: PatternType
    success_rate: float
    trap_rate: float


@dataclass(frozen=True)
class SymbolInput:
    profile: SymbolProfile
    recent_bars: list[MinuteBar]
    time_bucket_stats: list[TimeBucketStat] = field(default_factory=list)


@dataclass(frozen=True)
class FeatureSnapshot:
    symbol: str
    size_group: SizeGroup
    minute_turnover: float
    turnover_3m_avg: float
    turnover_3m_sustain_flag: bool
    turnover_vs_threshold_ratio: float
    program_net_buy_3m: float
    dist_to_day_high_pct: float
    dist_to_prev_day_high_pct: float
    dist_to_52w_high_pct: float
    dist_to_vi_pct: float
    is_breaking_day_high: bool
    is_breaking_prev_day_high: bool
    is_breaking_52w_high: bool
    pullback_depth_pct: float
    rebreak_after_pullback_flag: bool
    is_pre_vi_setup: bool
    is_leader_stock: bool
    time_bucket: str
    data_source: str


@dataclass(frozen=True)
class PatternSignal:
    name: PatternType
    confidence: float
    triggers: list[str]


@dataclass(frozen=True)
class MarketSnapshot:
    regime_label: str
    dominant_pattern: str
    best_time_bucket: str
    pattern_success_bias: dict[PatternType, float]
    time_bucket_bias: dict[str, float]


@dataclass(frozen=True)
class ScoredCandidate:
    symbol: str
    features: FeatureSnapshot
    pattern: PatternSignal
    total_score: float
    market_alignment: str
    reasons: list[str]
