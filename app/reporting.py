from __future__ import annotations

from html import escape
from pathlib import Path

from app.models import MarketSnapshot, PatternType, ScoredCandidate


def write_html_report(
    result: tuple[MarketSnapshot, list[ScoredCandidate]], output_path: Path
) -> None:
    output_path.write_text(build_html_report(result), encoding="utf-8")


def build_html_report(result: tuple[MarketSnapshot, list[ScoredCandidate]]) -> str:
    snapshot, ranked = result
    pattern_rows = _build_pattern_rows(snapshot)
    time_rows = _build_time_rows(snapshot)
    candidate_cards = "\n".join(_build_candidate_card(candidate) for candidate in ranked)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Breakout Analyzer Dashboard</title>
  <style>
    :root {{
      --bg: #f4f0e8;
      --panel: #fffaf2;
      --ink: #1e1a16;
      --muted: #6b6258;
      --line: #d9ccb8;
      --accent: #cc5f2f;
      --accent-soft: #f3d6c7;
      --good: #1f7a5c;
      --warn: #d98e04;
      --bad: #b53d2f;
      --shadow: rgba(52, 37, 24, 0.08);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      font-family: "Segoe UI", "Malgun Gothic", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, #fff5e7 0, transparent 34%),
        linear-gradient(135deg, #f7f1e6 0%, #efe4d0 100%);
      min-height: 100vh;
    }}

    .page {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 32px 20px 56px;
    }}

    .hero {{
      display: grid;
      grid-template-columns: 1.4fr 1fr;
      gap: 18px;
      margin-bottom: 18px;
    }}

    .panel {{
      background: rgba(255, 250, 242, 0.92);
      border: 1px solid var(--line);
      border-radius: 22px;
      padding: 22px;
      box-shadow: 0 18px 40px var(--shadow);
      backdrop-filter: blur(8px);
    }}

    .title {{
      margin: 0 0 10px;
      font-size: 34px;
      line-height: 1.1;
      letter-spacing: -0.03em;
    }}

    .eyebrow {{
      display: inline-block;
      padding: 7px 12px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      margin-bottom: 14px;
    }}

    .subtitle {{
      margin: 0;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.6;
    }}

    .metrics {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      margin-top: 18px;
    }}

    .metric {{
      padding: 16px;
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 18px;
    }}

    .metric-label {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .metric-value {{
      font-size: 23px;
      font-weight: 700;
      line-height: 1.2;
    }}

    .regime-favorable {{ color: var(--good); }}
    .regime-neutral {{ color: var(--warn); }}
    .regime-trap {{ color: var(--bad); }}

    .grid {{
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 18px;
      margin-bottom: 18px;
    }}

    h2 {{
      margin: 0 0 12px;
      font-size: 22px;
      letter-spacing: -0.02em;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}

    th, td {{
      text-align: left;
      padding: 11px 10px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }}

    th {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
    }}

    .candidate {{
      background: linear-gradient(180deg, #fffdf7 0%, #fff7ea 100%);
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 18px;
      box-shadow: 0 8px 20px rgba(54, 40, 26, 0.06);
    }}

    .candidate-top {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }}

    .symbol {{
      font-size: 22px;
      font-weight: 800;
      letter-spacing: -0.03em;
    }}

    .score {{
      font-size: 26px;
      font-weight: 800;
      color: var(--accent);
    }}

    .tag-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }}

    .tag {{
      display: inline-flex;
      align-items: center;
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      background: #fff;
      border: 1px solid var(--line);
      color: var(--ink);
    }}

    .reason-list {{
      margin: 0;
      padding-left: 18px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
    }}

    .footer-note {{
      margin-top: 18px;
      color: var(--muted);
      font-size: 13px;
    }}

    @media (max-width: 900px) {{
      .hero, .grid {{
        grid-template-columns: 1fr;
      }}

      .metrics {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <div class="panel">
        <div class="eyebrow">Breakout Market Lens</div>
        <h1 class="title">돌파 시장 상태와 후보 종목을 한 화면에서 확인</h1>
        <p class="subtitle">
          거래대금 3분 지속, 신고가/당일 고가/재돌파 패턴, 시간대 적합도, 시장 상태를 같이 반영한 1차 대시보드야.
        </p>
        <div class="metrics">
          <div class="metric">
            <span class="metric-label">Market Regime</span>
            <span class="metric-value regime-{escape(snapshot.regime_label)}">{escape(snapshot.regime_label)}</span>
          </div>
          <div class="metric">
            <span class="metric-label">Dominant Pattern</span>
            <span class="metric-value">{escape(snapshot.dominant_pattern)}</span>
          </div>
          <div class="metric">
            <span class="metric-label">Best Time Bucket</span>
            <span class="metric-value">{escape(snapshot.best_time_bucket)}</span>
          </div>
        </div>
      </div>
      <div class="panel">
        <h2>해석 포인트</h2>
        <table>
          <tbody>
            <tr>
              <th>장 상태</th>
              <td>{escape(_regime_explanation(snapshot.regime_label))}</td>
            </tr>
            <tr>
              <th>주도 패턴</th>
              <td>{escape(_pattern_explanation(snapshot.dominant_pattern))}</td>
            </tr>
            <tr>
              <th>최적 시간대</th>
              <td>{escape(snapshot.best_time_bucket)} 구간이 최근 통계상 가장 유리한 흐름이야.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="grid">
      <div class="panel">
        <h2>패턴 강도</h2>
        <table>
          <thead>
            <tr>
              <th>Pattern</th>
              <th>Bias</th>
              <th>Interpretation</th>
            </tr>
          </thead>
          <tbody>
            {pattern_rows}
          </tbody>
        </table>
      </div>
      <div class="panel">
        <h2>시간대 강도</h2>
        <table>
          <thead>
            <tr>
              <th>Time Bucket</th>
              <th>Bias</th>
            </tr>
          </thead>
          <tbody>
            {time_rows}
          </tbody>
        </table>
      </div>
    </section>

    <section class="panel">
      <h2>실시간 후보 종목</h2>
      <div class="cards">
        {candidate_cards}
      </div>
      <p class="footer-note">
        이 점수는 룰 기반 1차 버전이야. 실제 운영에선 장마감 라벨링, 백테스트, 실시간 수집기를 붙여서 계속 고도화하면 돼.
      </p>
    </section>
  </div>
</body>
</html>
"""


def _build_pattern_rows(snapshot: MarketSnapshot) -> str:
    if not snapshot.pattern_success_bias:
        return '<tr><td colspan="3">No data</td></tr>'

    rows = []
    for pattern, bias in sorted(
        snapshot.pattern_success_bias.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        rows.append(
            "<tr>"
            f"<td>{escape(pattern.value)}</td>"
            f"<td>{bias:.2f}</td>"
            f"<td>{escape(_bias_interpretation(bias))}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def _build_time_rows(snapshot: MarketSnapshot) -> str:
    if not snapshot.time_bucket_bias:
        return '<tr><td colspan="2">No data</td></tr>'

    rows = []
    for bucket, bias in sorted(
        snapshot.time_bucket_bias.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        rows.append(
            "<tr>"
            f"<td>{escape(bucket)}</td>"
            f"<td>{bias:.2f}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def _build_candidate_card(candidate: ScoredCandidate) -> str:
    features = candidate.features
    tags = [
        f'<span class="tag">{escape(candidate.pattern.name.value)}</span>',
        f'<span class="tag">time {escape(features.time_bucket)}</span>',
        f'<span class="tag">source {escape(features.data_source)}</span>',
        f'<span class="tag">fit {escape(candidate.market_alignment)}</span>',
        f'<span class="tag">program {features.program_net_buy_3m:.1f}</span>',
    ]
    if features.turnover_3m_sustain_flag:
        tags.append('<span class="tag">3m sustain</span>')
    if features.is_leader_stock:
        tags.append('<span class="tag">leader</span>')

    reasons = "\n".join(
        f"<li>{escape(reason)}</li>"
        for reason in candidate.reasons
    )

    return (
        '<article class="candidate">'
        '<div class="candidate-top">'
        f'<div class="symbol">{escape(candidate.symbol)}</div>'
        f'<div class="score">{candidate.total_score:.1f}</div>'
        "</div>"
        f'<div class="tag-row">{"".join(tags)}</div>'
        "<ul class=\"reason-list\">"
        f"{reasons}"
        "</ul>"
        "</article>"
    )


def _bias_interpretation(bias: float) -> str:
    if bias >= 0.65:
        return "최근 통계상 강한 우위"
    if bias <= 0.48:
        return "함정 가능성 높음"
    return "중립권"


def _regime_explanation(regime_label: str) -> str:
    if regime_label == "favorable":
        return "돌파가 비교적 잘 유지되는 장세"
    if regime_label == "trap":
        return "돌파 시도는 나와도 꺾일 가능성이 높은 장세"
    return "패턴별 선별이 필요한 중립 장세"


def _pattern_explanation(dominant_pattern: str) -> str:
    explanations = {
        PatternType.HIGH_52W.value: "52주 신고가 돌파가 상대적으로 강한 흐름",
        PatternType.DAY_HIGH.value: "당일 고가 돌파가 자주 시도되는 흐름",
        PatternType.PREV_DAY_HIGH.value: "전일 고가 돌파가 많이 나오는 흐름",
        PatternType.REBREAK.value: "눌림 뒤 재돌파가 잘 먹히는 흐름",
        PatternType.PRE_VI.value: "VI 직전 압축 패턴이 유효한 흐름",
        PatternType.NONE.value: "뚜렷한 우세 패턴이 아직 없음",
    }
    return explanations.get(dominant_pattern, "패턴 설명 없음")
