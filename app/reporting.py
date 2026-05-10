from __future__ import annotations

from collections import Counter
from html import escape
from pathlib import Path

from app.models import BreakoutScorecard, MacroIndicator, MarketSnapshot, PatternType, ScoredCandidate


def write_html_report(
    result: tuple[MarketSnapshot, list[ScoredCandidate]], output_path: Path
) -> None:
    output_path.write_text(build_html_report(result), encoding="utf-8")


def build_html_report(result: tuple[MarketSnapshot, list[ScoredCandidate]]) -> str:
    snapshot, ranked = result
    summary = _build_market_summary(snapshot, ranked)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Market Radar</title>
  <style>
    :root {{
      --bg: #07111b;
      --panel: rgba(10, 24, 39, 0.88);
      --panel-soft: rgba(15, 30, 49, 0.78);
      --line: rgba(126, 161, 200, 0.14);
      --ink: #edf4fb;
      --muted: #8ca1b7;
      --teal: #4fd7bc;
      --amber: #f3b855;
      --rose: #f46d7e;
      --sky: #7cb8ff;
      --violet: #ab92ff;
      --lime: #87d871;
      --shadow: rgba(0, 0, 0, 0.28);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      color: var(--ink);
      font-family: "Segoe UI", "Malgun Gothic", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(79, 215, 188, 0.15) 0, transparent 26%),
        radial-gradient(circle at top right, rgba(124, 184, 255, 0.10) 0, transparent 30%),
        linear-gradient(180deg, #08111c 0%, #040a12 100%);
      min-height: 100vh;
    }}

    .page {{
      width: min(1380px, calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0 56px;
    }}

    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 26px;
      box-shadow: 0 24px 60px var(--shadow);
      backdrop-filter: blur(10px);
    }}

    .hero {{
      display: grid;
      grid-template-columns: 1.25fr 0.75fr;
      gap: 18px;
      margin-bottom: 18px;
    }}

    .hero-main {{
      padding: 28px 28px 24px;
      overflow: hidden;
      position: relative;
    }}

    .hero-main::after {{
      content: "";
      position: absolute;
      inset: auto -10% -42% 30%;
      height: 320px;
      background: radial-gradient(circle, rgba(79, 215, 188, 0.18) 0, transparent 64%);
      pointer-events: none;
    }}

    .eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(124, 184, 255, 0.11);
      color: var(--sky);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }}

    .title {{
      margin: 18px 0 12px;
      max-width: 760px;
      font-size: clamp(34px, 5vw, 58px);
      line-height: 0.95;
      letter-spacing: -0.05em;
    }}

    .subtitle {{
      max-width: 760px;
      margin: 0;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.7;
    }}

    .hero-stats {{
      margin-top: 22px;
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      position: relative;
      z-index: 1;
    }}

    .stat {{
      padding: 16px;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 18px;
    }}

    .stat-label {{
      display: block;
      margin-bottom: 8px;
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.07em;
    }}

    .stat-value {{
      font-size: 24px;
      font-weight: 800;
      letter-spacing: -0.03em;
      line-height: 1.1;
    }}

    .regime-favorable {{ color: var(--teal); }}
    .regime-neutral {{ color: var(--amber); }}
    .regime-trap {{ color: var(--rose); }}

    .hero-side {{
      padding: 24px;
      display: grid;
      gap: 14px;
      align-content: start;
    }}

    .signal-box {{
      padding: 16px;
      border-radius: 18px;
      background: var(--panel-soft);
      border: 1px solid rgba(255, 255, 255, 0.05);
    }}

    .signal-key {{
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      margin-bottom: 6px;
    }}

    .signal-value {{
      font-size: 22px;
      font-weight: 800;
      line-height: 1.15;
      letter-spacing: -0.03em;
    }}

    .signal-copy {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.55;
    }}

    .section {{
      padding: 22px;
      margin-bottom: 18px;
    }}

    .section h2 {{
      margin: 0 0 14px;
      font-size: 20px;
      letter-spacing: -0.03em;
    }}

    .macro-grid {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 14px;
    }}

    .macro-card {{
      padding: 18px;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 20px;
    }}

    .macro-group {{
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 10px;
    }}

    .macro-label {{
      font-size: 16px;
      font-weight: 700;
      margin-bottom: 6px;
    }}

    .macro-price {{
      font-size: 26px;
      font-weight: 800;
      letter-spacing: -0.04em;
      line-height: 1.1;
      margin-bottom: 8px;
    }}

    .macro-change {{
      display: inline-flex;
      align-items: center;
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      background: rgba(255, 255, 255, 0.05);
    }}

    .macro-change.up {{ color: var(--teal); }}
    .macro-change.down {{ color: var(--rose); }}
    .macro-foot {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }}

    .market-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
    }}

    .market-card {{
      padding: 18px;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 20px;
    }}

    .market-card h3 {{
      margin: 0 0 10px;
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}

    .market-big {{
      font-size: 24px;
      font-weight: 800;
      letter-spacing: -0.04em;
      line-height: 1.1;
      margin-bottom: 8px;
    }}

    .market-copy {{
      color: var(--muted);
      font-size: 13px;
      line-height: 1.6;
    }}

    .summary-grid {{
      display: grid;
      grid-template-columns: 0.9fr 1.1fr;
      gap: 18px;
    }}

    .mini-table {{
      width: 100%;
      border-collapse: collapse;
    }}

    .mini-table th,
    .mini-table td {{
      padding: 12px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      text-align: left;
      vertical-align: top;
    }}

    .mini-table th {{
      width: 34%;
      color: var(--muted);
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}

    .bias-stack {{
      display: grid;
      gap: 10px;
    }}

    .bias-card {{
      padding: 14px 16px;
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.05);
    }}

    .bias-top {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      margin-bottom: 8px;
    }}

    .bias-name {{
      font-size: 15px;
      font-weight: 700;
    }}

    .bias-score {{
      color: var(--sky);
      font-weight: 800;
    }}

    .bias-copy {{
      color: var(--muted);
      font-size: 13px;
      line-height: 1.55;
    }}

    .strategy-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
    }}

    .strategy-card {{
      padding: 18px;
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.05);
    }}

    .strategy-label {{
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }}

    .strategy-value {{
      font-size: 22px;
      font-weight: 800;
      letter-spacing: -0.03em;
      line-height: 1.1;
      margin-bottom: 8px;
    }}

    .strategy-copy {{
      color: var(--muted);
      font-size: 13px;
      line-height: 1.55;
    }}

    .candidate-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
      gap: 18px;
    }}

    .candidate {{
      padding: 22px;
      background: linear-gradient(180deg, rgba(14, 30, 48, 0.98) 0%, rgba(9, 20, 35, 0.98) 100%);
      border-radius: 24px;
      border: 1px solid rgba(255, 255, 255, 0.06);
      box-shadow: 0 18px 42px rgba(0, 0, 0, 0.26);
    }}

    .candidate-header {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 14px;
      margin-bottom: 14px;
    }}

    .candidate-symbol {{
      font-size: 28px;
      font-weight: 900;
      letter-spacing: -0.05em;
    }}

    .candidate-subtitle {{
      margin-top: 6px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }}

    .score-block {{
      text-align: right;
    }}

    .score-label {{
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}

    .score-value {{
      margin-top: 4px;
      font-size: 34px;
      font-weight: 900;
      letter-spacing: -0.05em;
    }}

    .candidate-pills {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 14px;
    }}

    .pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      min-height: 34px;
      padding: 7px 11px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.05);
      color: var(--ink);
      font-size: 12px;
      font-weight: 700;
    }}

    .pill-action-actionable {{ color: var(--teal); }}
    .pill-action-stalk {{ color: var(--amber); }}
    .pill-action-watch,
    .pill-action-too_extended,
    .pill-action-avoid {{ color: var(--rose); }}

    .candidate-layout {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      margin-bottom: 14px;
    }}

    .info-block {{
      padding: 16px;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 18px;
    }}

    .block-title {{
      margin: 0 0 10px;
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}

    .callout {{
      font-size: 20px;
      font-weight: 800;
      letter-spacing: -0.03em;
      line-height: 1.2;
      margin: 0;
    }}

    .callout-copy {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.55;
    }}

    .pillar-grid {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 14px;
    }}

    .pillar {{
      padding: 14px 12px;
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.05);
      text-align: center;
    }}

    .pillar-label {{
      display: block;
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }}

    .pillar-value {{
      display: block;
      font-size: 26px;
      font-weight: 800;
      letter-spacing: -0.04em;
    }}

    .pillar-caption {{
      display: block;
      margin-top: 6px;
      color: var(--muted);
      font-size: 11px;
    }}

    .reason-columns {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }}

    .reason-box {{
      padding: 16px;
      border-radius: 18px;
      border: 1px solid rgba(255, 255, 255, 0.05);
      background: rgba(255, 255, 255, 0.02);
    }}

    .reason-box.good {{
      box-shadow: inset 0 0 0 1px rgba(79, 215, 188, 0.08);
    }}

    .reason-box.warn {{
      box-shadow: inset 0 0 0 1px rgba(244, 109, 126, 0.08);
    }}

    .reason-box h3 {{
      margin: 0 0 10px;
      font-size: 15px;
      letter-spacing: -0.02em;
    }}

    .reason-list {{
      margin: 0;
      padding-left: 18px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.6;
    }}

    .footer-note {{
      margin-top: 18px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.6;
    }}

    @media (max-width: 1120px) {{
      .hero,
      .summary-grid,
      .candidate-layout,
      .reason-columns {{
        grid-template-columns: 1fr;
      }}

      .hero-stats,
      .macro-grid,
      .market-grid,
      .strategy-grid,
      .pillar-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}

    @media (max-width: 720px) {{
      .page {{
        width: min(100% - 20px, 1380px);
      }}

      .hero-stats,
      .macro-grid,
      .market-grid,
      .strategy-grid,
      .pillar-grid {{
        grid-template-columns: 1fr;
      }}

      .candidate-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <article class="panel hero-main">
        <div class="eyebrow">Market Radar / Market Atmosphere Board</div>
        <h1 class="title">시장 전체 분위기부터 보고, 그다음에 종목을 고른다.</h1>
        <p class="subtitle">
          이 보드는 종목 추천판이 아니라 장 전체 상황판을 먼저 보여준다.
          지금이 돌파 우호장인지, 어떤 패턴이 먹히는지, 속도형 리더를 살지 자금형 리더를 살지를 먼저 읽고
          그 아래에서 개별 종목 실행 여부를 본다.
        </p>
        <div class="hero-stats">
          <div class="stat">
            <span class="stat-label">시장 상태</span>
            <span class="stat-value regime-{escape(snapshot.regime_label)}">{escape(_regime_label(snapshot.regime_label))}</span>
          </div>
          <div class="stat">
            <span class="stat-label">주도 패턴</span>
            <span class="stat-value">{escape(snapshot.dominant_pattern)}</span>
          </div>
          <div class="stat">
            <span class="stat-label">메인 리더 모드</span>
            <span class="stat-value">{escape(summary["top_leader_mode_label"])}</span>
          </div>
          <div class="stat">
            <span class="stat-label">평균 돌파 점수</span>
            <span class="stat-value">{summary["avg_total_score"]:.1f}</span>
          </div>
        </div>
      </article>

      <aside class="panel hero-side">
        <div class="signal-box">
          <div class="signal-key">오늘의 해석</div>
          <div class="signal-value">{escape(_market_headline(snapshot, summary))}</div>
          <div class="signal-copy">{escape(_market_copy(snapshot, summary))}</div>
        </div>
        <div class="signal-box">
          <div class="signal-key">가장 좋은 시간대</div>
          <div class="signal-value">{escape(snapshot.best_time_bucket)}</div>
          <div class="signal-copy">현재 데이터 기준으로 이 시간대가 가장 높은 bias를 보인다. 장중 판단은 이 구간을 우선 참고한다.</div>
        </div>
        <div class="signal-box">
          <div class="signal-key">전략 우선순위</div>
          <div class="signal-value">{escape(_execution_mode_label(summary["execution_mode"]))}</div>
          <div class="signal-copy">{escape(_execution_mode_copy(summary["execution_mode"]))}</div>
        </div>
      </aside>
    </section>

    <section class="panel section">
      <h2>핵심 시장 지표</h2>
      <div class="macro-grid">
        {"".join(_build_macro_cards(snapshot.macro_indicators))}
      </div>
      <p class="footer-note">
        현재 지표 보드는 샘플 레퍼런스 값이다. 나중에 실시간 피드를 연결하면 같은 자리에서 국장, 미국장, 환율, 금, 코인 흐름을 바로 확인할 수 있다.
      </p>
    </section>

    <section class="panel section">
      <h2>시장 전체 상황판</h2>
      <div class="market-grid">
        <div class="market-card">
          <h3>돌파 환경</h3>
          <div class="market-big">{escape(_regime_label(snapshot.regime_label))}</div>
          <div class="market-copy">{escape(_regime_environment_copy(snapshot.regime_label, summary["actionable_count"], summary["stalk_count"]))}</div>
        </div>
        <div class="market-card">
          <h3>리더 선택</h3>
          <div class="market-big">{escape(summary["top_leader_mode_label"])}</div>
          <div class="market-copy">{escape(_leader_distribution_copy(summary["leader_counts"]))}</div>
        </div>
        <div class="market-card">
          <h3>테마 온도</h3>
          <div class="market-big">{escape(summary["top_theme_label"])}</div>
          <div class="market-copy">{escape(_theme_copy(summary["theme_counts"]))}</div>
        </div>
        <div class="market-card">
          <h3>실행 강도</h3>
          <div class="market-big">{summary["avg_minute_score"]:.1f}</div>
          <div class="market-copy">{escape(_minute_environment_copy(summary["avg_minute_score"], summary["avg_leadership_score"]))}</div>
        </div>
      </div>
    </section>

    <section class="summary-grid">
      <article class="panel section">
        <h2>시장 해석</h2>
        <table class="mini-table">
          <tbody>
            <tr>
              <th>지배 패턴</th>
              <td>{escape(_pattern_explanation(snapshot.dominant_pattern))}</td>
            </tr>
            <tr>
              <th>리더 전략</th>
              <td>{escape(_execution_hint(summary["top_leader_mode"], snapshot.regime_label))}</td>
            </tr>
            <tr>
              <th>행동 분포</th>
              <td>{escape(_action_distribution_copy(summary["action_counts"]))}</td>
            </tr>
            <tr>
              <th>최상위 후보</th>
              <td>{escape(_top_candidate_copy(summary["top_candidate"]))}</td>
            </tr>
          </tbody>
        </table>
      </article>

      <article class="panel section">
        <h2>패턴 / 시간대 Bias</h2>
        <div class="bias-stack">
          {_build_pattern_cards(snapshot)}
          {_build_time_bias_cards(snapshot)}
        </div>
      </article>
    </section>

    <section class="panel section">
      <h2>전략 패널</h2>
      <div class="strategy-grid">
        <div class="strategy-card">
          <div class="strategy-label">돌파매매</div>
          <div class="strategy-value">{escape(_regime_label(snapshot.regime_label))}</div>
          <div class="strategy-copy">현재 구현상 가장 신뢰도 높은 전략은 돌파매매다. 이 값은 현재 시장 bias와 후보 action 분포를 기반으로 해석한다.</div>
        </div>
        <div class="strategy-card">
          <div class="strategy-label">속도형 리더</div>
          <div class="strategy-value">{summary["leader_counts"].get("buy_return_leader", 0)}</div>
          <div class="strategy-copy">뉴스 초입이나 첫 가속 구간에서 빠른 종목을 우선하는 후보 수다.</div>
        </div>
        <div class="strategy-card">
          <div class="strategy-label">자금형 리더</div>
          <div class="strategy-value">{summary["leader_counts"].get("buy_turnover_leader", 0) + summary["leader_counts"].get("buy_dual_leader", 0)}</div>
          <div class="strategy-copy">돈의 집중을 더 신뢰하는 후보 수다. 확산장이나 후반 구간일수록 중요도가 올라간다.</div>
        </div>
        <div class="strategy-card">
          <div class="strategy-label">주간 성공률</div>
          <div class="strategy-value">준비 중</div>
          <div class="strategy-copy">최근 1주 돌파 / 상따 / 종베 성공률은 별도 이벤트 라벨링과 주간 집계 테이블이 연결되면 여기에 표시한다.</div>
        </div>
      </div>
    </section>

    <section class="panel section">
      <h2>개별 후보</h2>
      <div class="candidate-grid">
        {"".join(_build_candidate_card(candidate) for candidate in ranked)}
      </div>
      <p class="footer-note">
        위 시장 전체 상황판이 먼저다. 종목 카드는 그 다음 단계다.
        `테일분뉴 = 1차 선별`, `stage / action / leader choice = 2차 실행 판단`으로 읽으면 된다.
      </p>
    </section>
  </div>
</body>
</html>
"""


def _build_market_summary(
    snapshot: MarketSnapshot, ranked: list[ScoredCandidate]
) -> dict[str, object]:
    action_counts: Counter[str] = Counter()
    leader_counts: Counter[str] = Counter()
    theme_counts: Counter[str] = Counter()
    total_scores: list[float] = []
    minute_scores: list[float] = []
    leadership_scores: list[float] = []
    top_candidate = ranked[0] if ranked else None

    for candidate in ranked:
        scorecard = candidate.scorecard
        if scorecard is None:
            continue
        action_counts[scorecard.action] += 1
        leader_counts[scorecard.leader_choice] += 1
        total_scores.append(candidate.total_score)
        minute_scores.append(scorecard.minute_score)
        leadership_scores.append(scorecard.leadership_score)

        theme_name = _extract_theme_name(candidate.reasons)
        if theme_name:
            theme_counts[theme_name] += 1

    top_leader_mode = max(
        leader_counts.items(),
        key=lambda item: item[1],
        default=("wait_for_resolution", 0),
    )[0]

    actionable_count = action_counts.get("actionable", 0)
    stalk_count = action_counts.get("stalk", 0)
    watch_like_count = (
        action_counts.get("watch", 0)
        + action_counts.get("too_extended", 0)
        + action_counts.get("avoid", 0)
    )

    if actionable_count >= max(stalk_count, watch_like_count):
        execution_mode = "aggressive_breakout"
    elif stalk_count >= actionable_count:
        execution_mode = "selective_stalking"
    else:
        execution_mode = "defensive_wait"

    top_theme_label = (
        max(theme_counts.items(), key=lambda item: item[1])[0]
        if theme_counts
        else "테마 데이터 부족"
    )

    return {
        "action_counts": action_counts,
        "leader_counts": leader_counts,
        "theme_counts": theme_counts,
        "actionable_count": actionable_count,
        "stalk_count": stalk_count,
        "watch_like_count": watch_like_count,
        "avg_total_score": _safe_average(total_scores),
        "avg_minute_score": _safe_average(minute_scores),
        "avg_leadership_score": _safe_average(leadership_scores),
        "top_leader_mode": top_leader_mode,
        "top_leader_mode_label": _leader_choice_label(top_leader_mode),
        "top_theme_label": top_theme_label,
        "execution_mode": execution_mode,
        "top_candidate": top_candidate,
    }


def _build_macro_cards(indicators: list[MacroIndicator]) -> list[str]:
    cards: list[str] = []
    for indicator in indicators:
        direction = "up" if indicator.change_pct >= 0 else "down"
        cards.append(
            '<div class="macro-card">'
            f'<div class="macro-group">{escape(indicator.group)}</div>'
            f'<div class="macro-label">{escape(indicator.label)}</div>'
            f'<div class="macro-price">{escape(indicator.price_text)}</div>'
            f'<div class="macro-change {direction}">{indicator.change_pct:+.2f}%</div>'
            f'<div class="macro-foot">{escape(indicator.status_text)} · {escape(indicator.source)}</div>'
            "</div>"
        )
    return cards


def _build_pattern_cards(snapshot: MarketSnapshot) -> str:
    cards: list[str] = []
    for pattern, bias in sorted(
        snapshot.pattern_success_bias.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:3]:
        cards.append(
            '<div class="bias-card">'
            '<div class="bias-top">'
            f'<div class="bias-name">{escape(pattern.value)}</div>'
            f'<div class="bias-score">{bias:.2f}</div>'
            "</div>"
            f'<div class="bias-copy">{escape(_bias_interpretation(bias))}</div>'
            "</div>"
        )
    if not cards:
        cards.append(
            '<div class="bias-card"><div class="bias-copy">패턴 bias 데이터가 아직 없다.</div></div>'
        )
    return "".join(cards)


def _build_time_bias_cards(snapshot: MarketSnapshot) -> str:
    cards: list[str] = []
    for bucket, bias in sorted(
        snapshot.time_bucket_bias.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:2]:
        cards.append(
            '<div class="bias-card">'
            '<div class="bias-top">'
            f'<div class="bias-name">{escape(bucket)}</div>'
            f'<div class="bias-score">{bias:.2f}</div>'
            "</div>"
            f'<div class="bias-copy">{escape(_time_bias_interpretation(bucket, bias))}</div>'
            "</div>"
        )
    if not cards:
        cards.append(
            '<div class="bias-card"><div class="bias-copy">시간대 bias 데이터가 아직 없다.</div></div>'
        )
    return "".join(cards)


def _build_candidate_card(candidate: ScoredCandidate) -> str:
    scorecard = candidate.scorecard
    features = candidate.features

    if scorecard is None:
        return (
            '<article class="candidate">'
            f'<div class="candidate-symbol">{escape(candidate.symbol)}</div>'
            '<div class="candidate-subtitle">scorecard unavailable</div>'
            "</article>"
        )

    positive_reasons = _unique_items(scorecard.reasons)[:5]
    warning_reasons = _unique_items(scorecard.warnings)[:5]

    return (
        '<article class="candidate">'
        '<div class="candidate-header">'
        '<div>'
        f'<div class="candidate-symbol">{escape(candidate.symbol)}</div>'
        f'<div class="candidate-subtitle">{escape(_candidate_subtitle(candidate))}</div>'
        "</div>"
        '<div class="score-block">'
        '<div class="score-label">Total Score</div>'
        f'<div class="score-value">{candidate.total_score:.1f}</div>'
        "</div>"
        "</div>"
        f'<div class="candidate-pills">{_build_pills(candidate)}</div>'
        '<div class="candidate-layout">'
        '<div class="info-block">'
        '<div class="block-title">실행 판단</div>'
        f'<p class="callout">{escape(_action_label(scorecard.action))}</p>'
        f'<div class="callout-copy">{escape(_action_copy(scorecard, features.dist_to_day_high_pct))}</div>'
        "</div>"
        '<div class="info-block">'
        '<div class="block-title">대장주 선택</div>'
        f'<p class="callout">{escape(_leader_choice_label(scorecard.leader_choice))}</p>'
        f'<div class="callout-copy">{escape(_leader_choice_copy(scorecard.leader_choice))}</div>'
        "</div>"
        "</div>"
        f'<div class="pillar-grid">{_build_pillars(scorecard)}</div>'
        '<div class="reason-columns">'
        '<div class="reason-box good">'
        '<h3>진입 근거</h3>'
        f'<ul class="reason-list">{_build_reason_items(positive_reasons, "강한 근거가 아직 부족함")}</ul>'
        "</div>"
        '<div class="reason-box warn">'
        '<h3>주의할 점</h3>'
        f'<ul class="reason-list">{_build_reason_items(warning_reasons, "눈에 띄는 경고 없음")}</ul>'
        "</div>"
        "</div>"
        "</article>"
    )


def _build_pills(candidate: ScoredCandidate) -> str:
    scorecard = candidate.scorecard
    features = candidate.features
    assert scorecard is not None

    items = [
        f'<span class="pill pill-action-{escape(scorecard.action)}">{escape(_action_label(scorecard.action))}</span>',
        f'<span class="pill">{escape(candidate.pattern.name.value)}</span>',
        f'<span class="pill">{escape(_stage_label(scorecard.stage.value))}</span>',
        f'<span class="pill">{escape(features.time_bucket)}</span>',
        f'<span class="pill">program {features.program_net_buy_3m:.1f}</span>',
        f'<span class="pill">{escape(_leader_choice_label(scorecard.leader_choice))}</span>',
    ]
    if features.turnover_3m_sustain_flag:
        items.append('<span class="pill">3분 대금 유지</span>')
    if features.is_leader_stock:
        items.append('<span class="pill">리더 플래그</span>')
    return "".join(items)


def _build_pillars(scorecard: BreakoutScorecard) -> str:
    pillars = [
        ("Theme", scorecard.theme_score, "테마"),
        ("Daily", scorecard.daily_score, "일봉"),
        ("Minute", scorecard.minute_score, "분봉"),
        ("News", scorecard.news_score, "뉴스"),
        ("Leader", scorecard.leadership_score, "대장"),
    ]
    return "".join(
        '<div class="pillar">'
        f'<span class="pillar-label">{escape(short)}</span>'
        f'<span class="pillar-value">{value:.0f}</span>'
        f'<span class="pillar-caption">{escape(label)}</span>'
        "</div>"
        for short, value, label in pillars
    )


def _build_reason_items(items: list[str], fallback: str) -> str:
    if not items:
        return f"<li>{escape(fallback)}</li>"
    return "".join(f"<li>{escape(item)}</li>" for item in items)


def _market_headline(snapshot: MarketSnapshot, summary: dict[str, object]) -> str:
    return (
        f"{_regime_label(snapshot.regime_label)} / "
        f"{_leader_choice_label(str(summary['top_leader_mode']))} / "
        f"{snapshot.dominant_pattern}"
    )


def _market_copy(snapshot: MarketSnapshot, summary: dict[str, object]) -> str:
    return (
        f"현재 장은 {_regime_label(snapshot.regime_label)} 쪽이다. "
        f"리더 선택은 {_leader_choice_label(str(summary['top_leader_mode']))} 우세이고, "
        f"{snapshot.best_time_bucket} 구간이 가장 좋은 시간대로 집계된다."
    )


def _execution_hint(top_leader_mode: str, regime_label: str) -> str:
    if regime_label == "trap":
        return (
            f"{_leader_choice_label(top_leader_mode)}라도 바로 추격하지 말고 "
            "holding 안착과 3분 대금 유지를 먼저 확인한다."
        )
    return (
        f"{_leader_choice_label(top_leader_mode)} 우위 장세다. "
        "다만 1차 점수보다 stage와 leader choice가 더 중요하다."
    )


def _execution_mode_label(execution_mode: str) -> str:
    labels = {
        "aggressive_breakout": "공격적 돌파 대응",
        "selective_stalking": "선별 추적 대응",
        "defensive_wait": "방어적 대기",
    }
    return labels.get(execution_mode, execution_mode)


def _execution_mode_copy(execution_mode: str) -> str:
    copies = {
        "aggressive_breakout": "즉시 실행 가능한 후보가 상대적으로 많다. 다만 과열 추격은 여전히 분리해야 한다.",
        "selective_stalking": "좋은 종목은 보이지만 타점 확정이 덜 됐다. 리더 고정과 안착을 기다리는 편이 낫다.",
        "defensive_wait": "장 자체가 깔끔하지 않다. 지금은 시장 해석과 리더 분화 확인이 먼저다.",
    }
    return copies.get(execution_mode, "")


def _regime_environment_copy(regime_label: str, actionable_count: int, stalk_count: int) -> str:
    if regime_label == "favorable":
        return f"실행 후보 {actionable_count}개, 대기 후보 {stalk_count}개. 돌파가 비교적 잘 이어질 수 있는 환경이다."
    if regime_label == "trap":
        return f"대기 후보 {stalk_count}개 대비 실행 후보 {actionable_count}개가 적다. 돌파 실패 전환을 더 경계해야 한다."
    return f"실행 후보 {actionable_count}개, 대기 후보 {stalk_count}개. 선택적으로 선별 대응하는 편이 좋다."


def _leader_distribution_copy(leader_counts: Counter[str]) -> str:
    ordered = leader_counts.most_common(2)
    if not ordered:
        return "리더 분포 데이터가 아직 부족하다."
    first_label = _leader_choice_label(ordered[0][0])
    if len(ordered) == 1:
        return f"현재는 {first_label} 중심으로 해석된다."
    second_label = _leader_choice_label(ordered[1][0])
    return f"{first_label} 우위이고, 그다음은 {second_label} 쪽이다."


def _theme_copy(theme_counts: Counter[str]) -> str:
    if not theme_counts:
        return "현재 후보군에서 테마 데이터를 추출할 수 없다."
    top = theme_counts.most_common(3)
    joined = ", ".join(f"{name} ({count})" for name, count in top)
    return f"현재 후보군 중심 테마는 {joined} 순이다."


def _minute_environment_copy(avg_minute_score: float, avg_leadership_score: float) -> str:
    if avg_minute_score >= 75 and avg_leadership_score >= 65:
        return "분봉 구조와 리더 분화가 같이 받쳐준다. 종목보다 실행 타이밍만 잘 고르면 되는 환경에 가깝다."
    if avg_minute_score >= 60:
        return "분봉은 어느 정도 받쳐주지만 리더 고정은 더 확인해야 한다."
    return "분봉 구조 자체가 아직 약하다. 돌파 추격보다 대기 우선 쪽이 맞다."


def _action_distribution_copy(action_counts: Counter[str]) -> str:
    actionable = action_counts.get("actionable", 0)
    stalk = action_counts.get("stalk", 0)
    watch = action_counts.get("watch", 0)
    return f"지금 후보군은 실행 {actionable}, 대기 {stalk}, 관찰 {watch} 분포다."


def _top_candidate_copy(candidate: ScoredCandidate | None) -> str:
    if candidate is None or candidate.scorecard is None:
        return "상위 후보가 아직 없다."
    return (
        f"{candidate.symbol}이 현재 최상위다. "
        f"{_leader_choice_label(candidate.scorecard.leader_choice)} 기준이며 "
        f"action은 {_action_label(candidate.scorecard.action)}."
    )


def _candidate_subtitle(candidate: ScoredCandidate) -> str:
    scorecard = candidate.scorecard
    if scorecard is None:
        return "데이터 부족"
    return (
        f"{_leader_choice_label(scorecard.leader_choice)} / "
        f"{_stage_label(scorecard.stage.value)} / "
        f"{_regime_label(candidate.market_alignment)}"
    )


def _action_label(action: str) -> str:
    labels = {
        "actionable": "지금 볼 자리",
        "stalk": "대기 후 추적",
        "watch": "관찰 우선",
        "too_extended": "추격 금지",
        "avoid": "제외",
    }
    return labels.get(action, action)


def _action_copy(scorecard: BreakoutScorecard, dist_to_day_high_pct: float) -> str:
    if scorecard.action == "actionable":
        return "돌파 상태와 대금 유지가 같이 맞아 들어간다. 지금은 진입 판단까지 검토할 수 있는 구간이다."
    if scorecard.action == "stalk":
        return "좋은 종목이지만 아직 타점 확정이 덜 됐다. 고가 안착이나 재유입을 기다리는 편이 낫다."
    if scorecard.action == "too_extended":
        return f"고가 대비 {dist_to_day_high_pct:.2f}% 위라 속도는 강하지만 추격 리스크가 크다."
    if scorecard.action == "avoid":
        return "현재 상태로는 돌파 실패나 시장 부적합 가능성이 커서 제외하는 편이 좋다."
    return "조건이 일부 맞지만 확신하기엔 이르다. 계속 관찰하면서 리더 분화를 확인한다."


def _leader_choice_label(choice: str) -> str:
    labels = {
        "buy_dual_leader": "돈과 속도 동시 선두",
        "buy_return_leader": "상승률 리더 우선",
        "buy_turnover_leader": "거래대금 리더 우선",
        "wait_for_resolution": "리더 확정 대기",
    }
    return labels.get(choice, choice)


def _leader_choice_copy(choice: str) -> str:
    copies = {
        "buy_dual_leader": "같은 종목에 돈과 속도가 함께 붙었다. 가장 이상적인 대장 구조다.",
        "buy_return_leader": "초입 뉴스와 첫 가속 구간이라면 제일 빠른 종목을 우선 본다.",
        "buy_turnover_leader": "테마가 퍼졌거나 후반 구간이면 속도보다 실제 돈의 집중을 더 신뢰한다.",
        "wait_for_resolution": "상승률과 거래대금 리더가 갈려 있다. 먼저 누가 주도권을 고정하는지 본다.",
    }
    return copies.get(choice, "")


def _stage_label(stage: str) -> str:
    labels = {
        "wait": "대기",
        "probing": "돌파 시도",
        "breaking": "돌파 진입",
        "holding": "돌파 유지",
        "extended": "과열 확장",
        "failed": "실패",
    }
    return labels.get(stage, stage)


def _regime_label(regime_label: str) -> str:
    labels = {
        "favorable": "돌파 우호",
        "neutral": "중립",
        "trap": "함정",
        "strong": "강함",
        "weak": "약함",
    }
    return labels.get(regime_label, regime_label)


def _bias_interpretation(bias: float) -> str:
    if bias >= 0.65:
        return "최근 집계 기준으로 비교적 강한 우위가 있다."
    if bias <= 0.48:
        return "실패나 함정 전환 가능성을 경계해야 한다."
    return "확실한 우위보다는 선별 대응이 필요한 중립 구간이다."


def _time_bias_interpretation(bucket: str, bias: float) -> str:
    return f"{bucket} 구간 bias는 {bias:.2f}다. 현재 장세에서 이 시간대 대응 우선순위가 높다."


def _pattern_explanation(dominant_pattern: str) -> str:
    explanations = {
        PatternType.HIGH_52W.value: "52주 신고가형이 상대적으로 가장 깔끔하게 이어지는 흐름이다.",
        PatternType.DAY_HIGH.value: "당일 고가 돌파형이 계속 시도되는 장세다.",
        PatternType.PREV_DAY_HIGH.value: "전일 고가 돌파형이 가장 자연스럽게 이어지는 흐름이다.",
        PatternType.REBREAK.value: "첫 돌파보다 눌림 이후 재돌파가 더 유리한 흐름이다.",
        PatternType.PRE_VI.value: "VI 직전 압축형이 의미 있게 작동하는 장세다.",
        PatternType.NONE.value: "아직 지배적인 패턴이 뚜렷하게 보이지 않는다.",
    }
    return explanations.get(dominant_pattern, "패턴 해석 데이터가 아직 부족하다.")


def _extract_theme_name(reasons: list[str]) -> str | None:
    for reason in reasons:
        if reason.startswith("theme="):
            return reason.split("=", 1)[1]
    return None


def _safe_average(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 1)


def _unique_items(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            ordered.append(item)
            seen.add(item)
    return ordered
