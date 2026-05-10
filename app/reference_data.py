from __future__ import annotations

from app.models import MacroIndicator


def build_reference_macro_indicators() -> list[MacroIndicator]:
    return [
        MacroIndicator(
            code="KOSPI",
            label="코스피",
            group="국장",
            price_text="2,742.3",
            change_pct=0.82,
            status_text="risk-on",
        ),
        MacroIndicator(
            code="KOSDAQ",
            label="코스닥",
            group="국장",
            price_text="879.4",
            change_pct=1.34,
            status_text="growth",
        ),
        MacroIndicator(
            code="SPX",
            label="S&P 500",
            group="미국장",
            price_text="5,196.8",
            change_pct=0.41,
            status_text="broad risk",
        ),
        MacroIndicator(
            code="NDX",
            label="나스닥 100",
            group="미국장",
            price_text="18,212.5",
            change_pct=0.76,
            status_text="tech beta",
        ),
        MacroIndicator(
            code="DXY",
            label="달러 인덱스",
            group="환율",
            price_text="104.6",
            change_pct=-0.18,
            status_text="usd tone",
        ),
        MacroIndicator(
            code="USDKRW",
            label="달러/원",
            group="환율",
            price_text="1,364.2",
            change_pct=-0.27,
            status_text="krw firm",
        ),
        MacroIndicator(
            code="XAUUSD",
            label="금",
            group="원자재",
            price_text="2,356.4",
            change_pct=0.63,
            status_text="hedge bid",
        ),
        MacroIndicator(
            code="WTI",
            label="WTI",
            group="원자재",
            price_text="78.4",
            change_pct=-0.52,
            status_text="energy",
        ),
        MacroIndicator(
            code="BTC",
            label="비트코인",
            group="코인",
            price_text="63,820",
            change_pct=1.48,
            status_text="risk proxy",
        ),
        MacroIndicator(
            code="ETH",
            label="이더리움",
            group="코인",
            price_text="3,082",
            change_pct=1.12,
            status_text="alt beta",
        ),
    ]
