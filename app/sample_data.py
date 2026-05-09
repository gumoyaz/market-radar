from __future__ import annotations

from app.models import MinuteBar, PatternType, SizeGroup, SymbolInput, SymbolProfile, TimeBucketStat


def build_sample_watchlist() -> list[SymbolInput]:
    return [
        SymbolInput(
            profile=SymbolProfile(
                symbol="ALPHA",
                name="Alpha Robotics",
                size_group=SizeGroup.SMALL,
                day_high=101_000,
                prev_day_high=99_500,
                high_52w=101_000,
                vi_price=107_000,
                is_leader_stock=True,
            ),
            recent_bars=[
                MinuteBar(close=99_800, turnover_billion=31.0, program_net_buy_billion=1.3, source="sample"),
                MinuteBar(close=100_400, turnover_billion=34.5, program_net_buy_billion=1.6, source="sample"),
                MinuteBar(close=101_300, turnover_billion=38.2, program_net_buy_billion=2.4, source="sample"),
            ],
            time_bucket_stats=[
                TimeBucketStat("09:05-09:10", PatternType.DAY_HIGH, 0.61, 0.24),
                TimeBucketStat("09:10-09:20", PatternType.HIGH_52W, 0.72, 0.18),
                TimeBucketStat("09:30-10:00", PatternType.REBREAK, 0.68, 0.21),
            ],
        ),
        SymbolInput(
            profile=SymbolProfile(
                symbol="BETA",
                name="Beta Energy",
                size_group=SizeGroup.MID,
                day_high=52_000,
                prev_day_high=51_500,
                high_52w=58_000,
                vi_price=55_800,
                is_leader_stock=True,
            ),
            recent_bars=[
                MinuteBar(close=50_900, turnover_billion=63.0, program_net_buy_billion=0.8, source="sample"),
                MinuteBar(close=50_300, turnover_billion=66.5, program_net_buy_billion=0.9, source="sample"),
                MinuteBar(close=51_700, turnover_billion=71.1, program_net_buy_billion=1.7, source="sample"),
            ],
            time_bucket_stats=[
                TimeBucketStat("09:10-09:20", PatternType.REBREAK, 0.69, 0.19),
                TimeBucketStat("09:20-09:30", PatternType.DAY_HIGH, 0.55, 0.27),
                TimeBucketStat("10:00-10:30", PatternType.REBREAK, 0.64, 0.20),
            ],
        ),
        SymbolInput(
            profile=SymbolProfile(
                symbol="GAMMA",
                name="Gamma Bio",
                size_group=SizeGroup.SMALL,
                day_high=21_800,
                prev_day_high=21_700,
                high_52w=24_000,
                vi_price=23_100,
                is_leader_stock=False,
            ),
            recent_bars=[
                MinuteBar(close=21_100, turnover_billion=28.0, program_net_buy_billion=-0.4, source="sample"),
                MinuteBar(close=21_500, turnover_billion=29.5, program_net_buy_billion=-0.1, source="sample"),
                MinuteBar(close=21_750, turnover_billion=32.0, program_net_buy_billion=0.2, source="sample"),
            ],
            time_bucket_stats=[
                TimeBucketStat("09:10-09:20", PatternType.DAY_HIGH, 0.44, 0.40),
                TimeBucketStat("09:30-10:00", PatternType.PRE_VI, 0.47, 0.35),
            ],
        ),
    ]
