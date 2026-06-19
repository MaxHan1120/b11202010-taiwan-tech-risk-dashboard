from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from ..database import get_connection
from ..stocks import STOCK_IDS

WEIGHTS = {
    "volatility_score": 0.25,
    "drawdown_score": 0.25,
    "volume_score": 0.20,
    "valuation_score": 0.15,
    "fundamental_score": 0.15,
}


def compute_all_risk_scores() -> dict:
    total = 0
    for stock_id in STOCK_IDS:
        total += compute_stock_risk(stock_id)
    return {"risk_scores": total}


def compute_stock_risk(stock_id: str) -> int:
    with get_connection() as conn:
        prices = pd.read_sql_query(
            "SELECT * FROM daily_prices WHERE stock_id = ? ORDER BY date",
            conn,
            params=(stock_id,),
        )
        valuations = pd.read_sql_query(
            "SELECT * FROM valuation_metrics WHERE stock_id = ? ORDER BY date",
            conn,
            params=(stock_id,),
        )
        revenue = pd.read_sql_query(
            "SELECT * FROM monthly_revenue WHERE stock_id = ? ORDER BY date",
            conn,
            params=(stock_id,),
        )
        financials = pd.read_sql_query(
            "SELECT * FROM financial_metrics WHERE stock_id = ? ORDER BY date",
            conn,
            params=(stock_id,),
        )
    if prices.empty:
        return 0

    prices["return"] = prices["close"].pct_change()
    prices["rolling_vol_20"] = prices["return"].rolling(20).std() * (252 ** 0.5)
    latest = prices.iloc[-1]

    volatility_score = percentile_score(prices["rolling_vol_20"], latest["rolling_vol_20"])
    drawdown_score = drawdown_risk(prices["close"])
    volume_score = volume_risk(prices["volume"])
    valuation_score = latest_valuation_risk(valuations)
    fundamental_score = latest_fundamental_risk(revenue, financials)
    total = weighted_total(
        {
            "volatility_score": volatility_score,
            "drawdown_score": drawdown_score,
            "volume_score": volume_score,
            "valuation_score": valuation_score,
            "fundamental_score": fundamental_score,
        }
    )
    risk_level = risk_level_from_score(total)
    row = {
        "stock_id": stock_id,
        "date": latest["date"],
        "total_score": total,
        "volatility_score": volatility_score,
        "drawdown_score": drawdown_score,
        "volume_score": volume_score,
        "valuation_score": valuation_score,
        "fundamental_score": fundamental_score,
        "risk_level": risk_level,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO risk_scores (
                stock_id, date, total_score, volatility_score, drawdown_score,
                volume_score, valuation_score, fundamental_score, risk_level, updated_at
            )
            VALUES (
                :stock_id, :date, :total_score, :volatility_score, :drawdown_score,
                :volume_score, :valuation_score, :fundamental_score, :risk_level, :updated_at
            )
            ON CONFLICT(stock_id, date) DO UPDATE SET
                total_score = excluded.total_score,
                volatility_score = excluded.volatility_score,
                drawdown_score = excluded.drawdown_score,
                volume_score = excluded.volume_score,
                valuation_score = excluded.valuation_score,
                fundamental_score = excluded.fundamental_score,
                risk_level = excluded.risk_level,
                updated_at = excluded.updated_at
            """,
            row,
        )
    return 1


def weighted_total(scores: dict[str, float]) -> float:
    return clamp(sum(scores[key] * weight for key, weight in WEIGHTS.items()))


def risk_level_from_score(score: float) -> str:
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def percentile_score(series: pd.Series, latest_value) -> float:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty or pd.isna(latest_value):
        return 35.0
    return clamp((clean <= latest_value).mean() * 100)


def drawdown_risk(close: pd.Series) -> float:
    clean = pd.to_numeric(close, errors="coerce").dropna()
    if clean.empty:
        return 35.0
    recent = clean.tail(60)
    high = recent.max()
    if high <= 0:
        return 35.0
    drawdown = max(0, (high - recent.iloc[-1]) / high)
    return clamp(drawdown / 0.35 * 100)


def volume_risk(volume: pd.Series) -> float:
    clean = pd.to_numeric(volume, errors="coerce").dropna()
    if len(clean) < 20:
        return 35.0
    avg = clean.tail(20).mean()
    if avg <= 0:
        return 35.0
    ratio = clean.iloc[-1] / avg
    return clamp((ratio - 1) / 2 * 100)


def latest_valuation_risk(valuations: pd.DataFrame) -> float:
    if valuations.empty:
        return 35.0
    score_parts = []
    for column in ["per", "pbr"]:
        series = pd.to_numeric(valuations[column], errors="coerce").dropna() if column in valuations else pd.Series(dtype=float)
        if len(series) >= 5:
            score_parts.append(percentile_score(series, series.iloc[-1]))
    return clamp(sum(score_parts) / len(score_parts)) if score_parts else 35.0


def latest_fundamental_risk(revenue: pd.DataFrame, financials: pd.DataFrame) -> float:
    risks = []
    if not revenue.empty:
        latest_yoy = pd.to_numeric(revenue.get("revenue_yoy"), errors="coerce").dropna()
        if not latest_yoy.empty:
            value = latest_yoy.iloc[-1]
            risks.append(clamp((10 - value) / 30 * 100))
    if not financials.empty:
        financials = financials.copy()
        for column in ["eps", "gross_profit", "net_income"]:
            series = pd.to_numeric(financials.get(column), errors="coerce").dropna()
            if len(series) >= 2:
                decline = (series.iloc[-2] - series.iloc[-1]) / max(abs(series.iloc[-2]), 1)
                risks.append(clamp(decline / 0.4 * 100))
    return clamp(sum(risks) / len(risks)) if risks else 35.0


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    if pd.isna(value):
        return 35.0
    return round(max(low, min(high, float(value))), 2)
