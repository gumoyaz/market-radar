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


class BreakoutStage(str, Enum):
    WAIT = "wait"
    PROBING = "probing"
    BREAKING = "breaking"
    HOLDING = "holding"
    EXTENDED = "extended"
    FAILED = "failed"


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
class ThemeContext:
    theme_name: str = ""
    strength_percentile: float = 0.0
    breadth_ratio: float = 0.0
    leader_count: int = 0
    turnover_share_pct: float = 0.0
    persistence_days: int = 0


@dataclass(frozen=True)
class DailyContext:
    distance_to_52w_high_pct: float = 100.0
    consolidation_days: int = 0
    consolidation_range_pct: float = 100.0
    daily_turnover_ratio: float = 0.0
    close_position_pct: float = 0.0


@dataclass(frozen=True)
class NewsContext:
    has_news: bool = False
    headline_strength: float = 0.0
    source_count: int = 0
    minutes_since_release: int = 9_999
    catalyst: str = ""
    is_confirmed: bool = False
    is_theme_aligned: bool = False


@dataclass(frozen=True)
class LeadershipContext:
    theme_member_count: int = 0
    turnover_rank: int = 99
    return_rank: int = 99
    turnover_share_pct: float = 0.0
    intraday_return_pct: float = 0.0
    gap_from_next_turnover_pct: float = 0.0
    gap_from_next_return_pct: float = 0.0
    move_persistence_minutes: int = 0
    is_news_leader: bool = False


@dataclass(frozen=True)
class MacroIndicator:
    code: str
    label: str
    group: str
    price_text: str
    change_pct: float
    status_text: str = ""
    source: str = "sample"


@dataclass(frozen=True)
class SymbolInput:
    profile: SymbolProfile
    recent_bars: list[MinuteBar]
    time_bucket_stats: list[TimeBucketStat] = field(default_factory=list)
    theme_context: ThemeContext = field(default_factory=ThemeContext)
    daily_context: DailyContext = field(default_factory=DailyContext)
    news_context: NewsContext = field(default_factory=NewsContext)
    leadership_context: LeadershipContext = field(default_factory=LeadershipContext)


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
    macro_indicators: list[MacroIndicator] = field(default_factory=list)


@dataclass(frozen=True)
class BreakoutScorecard:
    theme_score: float
    daily_score: float
    minute_score: float
    news_score: float
    leadership_score: float
    total_score: float
    stage: BreakoutStage
    action: str
    leader_choice: str
    reasons: list[str]
    warnings: list[str]


@dataclass(frozen=True)
class ScoredCandidate:
    symbol: str
    features: FeatureSnapshot
    pattern: PatternSignal
    total_score: float
    market_alignment: str
    reasons: list[str]
    scorecard: BreakoutScorecard | None = None
