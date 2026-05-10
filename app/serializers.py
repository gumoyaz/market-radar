from __future__ import annotations

import json
from pathlib import Path

from app.models import MarketSnapshot, ScoredCandidate


def write_json_snapshot(
    result: tuple[MarketSnapshot, list[ScoredCandidate]],
    output_path: Path,
    generated_at: str,
) -> None:
    payload = build_json_snapshot(result, generated_at)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def build_json_snapshot(
    result: tuple[MarketSnapshot, list[ScoredCandidate]],
    generated_at: str,
) -> dict:
    snapshot, ranked = result
    return {
        "generated_at": generated_at,
        "market": {
            "regime_label": snapshot.regime_label,
            "dominant_pattern": snapshot.dominant_pattern,
            "best_time_bucket": snapshot.best_time_bucket,
            "macro_indicators": [
                {
                    "code": indicator.code,
                    "label": indicator.label,
                    "group": indicator.group,
                    "price_text": indicator.price_text,
                    "change_pct": indicator.change_pct,
                    "status_text": indicator.status_text,
                    "source": indicator.source,
                }
                for indicator in snapshot.macro_indicators
            ],
            "pattern_success_bias": {
                pattern.value: round(bias, 4)
                for pattern, bias in snapshot.pattern_success_bias.items()
            },
            "time_bucket_bias": {
                bucket: round(bias, 4)
                for bucket, bias in snapshot.time_bucket_bias.items()
            },
        },
        "candidates": [
            {
                "symbol": candidate.symbol,
                "score": candidate.total_score,
                "pattern": candidate.pattern.name.value,
                "pattern_confidence": round(candidate.pattern.confidence, 4),
                "market_alignment": candidate.market_alignment,
                "reasons": candidate.reasons,
                "scorecard": {
                    "theme_score": candidate.scorecard.theme_score,
                    "daily_score": candidate.scorecard.daily_score,
                    "minute_score": candidate.scorecard.minute_score,
                    "news_score": candidate.scorecard.news_score,
                    "leadership_score": candidate.scorecard.leadership_score,
                    "total_score": candidate.scorecard.total_score,
                    "stage": candidate.scorecard.stage.value,
                    "action": candidate.scorecard.action,
                    "leader_choice": candidate.scorecard.leader_choice,
                    "warnings": candidate.scorecard.warnings,
                }
                if candidate.scorecard
                else None,
                "features": {
                    "time_bucket": candidate.features.time_bucket,
                    "data_source": candidate.features.data_source,
                    "minute_turnover": candidate.features.minute_turnover,
                    "turnover_3m_avg": candidate.features.turnover_3m_avg,
                    "turnover_3m_sustain_flag": candidate.features.turnover_3m_sustain_flag,
                    "program_net_buy_3m": candidate.features.program_net_buy_3m,
                    "dist_to_day_high_pct": round(candidate.features.dist_to_day_high_pct, 4),
                    "dist_to_prev_day_high_pct": round(candidate.features.dist_to_prev_day_high_pct, 4),
                    "dist_to_52w_high_pct": round(candidate.features.dist_to_52w_high_pct, 4),
                    "dist_to_vi_pct": round(candidate.features.dist_to_vi_pct, 4),
                    "rebreak_after_pullback_flag": candidate.features.rebreak_after_pullback_flag,
                    "is_leader_stock": candidate.features.is_leader_stock,
                },
            }
            for candidate in ranked
        ],
    }
