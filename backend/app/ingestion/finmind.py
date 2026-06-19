from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable

import pandas as pd
import requests

from ..config import FINMIND_API_URL, FINMIND_TOKEN
from ..database import get_connection, init_db
from ..stocks import STOCK_IDS


class FinMindClient:
    def __init__(self, token: str = FINMIND_TOKEN, timeout: int = 30) -> None:
        self.token = token
        self.timeout = timeout

    def fetch(self, dataset: str, stock_id: str | None = None, start_date: str | None = None, end_date: str | None = None) -> pd.DataFrame:
        params = {"dataset": dataset}
        if stock_id:
            params["data_id"] = stock_id
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        response = requests.get(FINMIND_API_URL, params=params, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data") or []
        return pd.DataFrame(data)


def default_start_date(days: int = 420) -> str:
    return (date.today() - timedelta(days=days)).isoformat()


def upsert_daily_prices(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    rename = {
        "Trading_Volume": "volume",
        "Trading_money": "trading_value",
        "open": "open",
        "max": "high",
        "min": "low",
        "close": "close",
    }
    work = df.rename(columns=rename)
    rows = []
    for _, row in work.iterrows():
        rows.append(
            {
                "stock_id": str(row.get("stock_id")),
                "date": str(row.get("date")),
                "open": _num(row.get("open")),
                "high": _num(row.get("high")),
                "low": _num(row.get("low")),
                "close": _num(row.get("close")),
                "volume": _num(row.get("volume")),
                "trading_value": _num(row.get("trading_value")),
            }
        )
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO daily_prices (stock_id, date, open, high, low, close, volume, trading_value)
            VALUES (:stock_id, :date, :open, :high, :low, :close, :volume, :trading_value)
            ON CONFLICT(stock_id, date) DO UPDATE SET
                open = excluded.open,
                high = excluded.high,
                low = excluded.low,
                close = excluded.close,
                volume = excluded.volume,
                trading_value = excluded.trading_value
            """,
            rows,
        )
    return len(rows)


def upsert_valuation(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    rows = []
    for _, row in df.iterrows():
        rows.append(
            {
                "stock_id": str(row.get("stock_id")),
                "date": str(row.get("date")),
                "per": _first_num(row, ["PER", "per"]),
                "pbr": _first_num(row, ["PBR", "pbr"]),
                "dividend_yield": _first_num(row, ["dividend_yield", "殖利率"]),
            }
        )
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO valuation_metrics (stock_id, date, per, pbr, dividend_yield)
            VALUES (:stock_id, :date, :per, :pbr, :dividend_yield)
            ON CONFLICT(stock_id, date) DO UPDATE SET
                per = excluded.per,
                pbr = excluded.pbr,
                dividend_yield = excluded.dividend_yield
            """,
            rows,
        )
    return len(rows)


def upsert_monthly_revenue(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    rows = []
    for _, row in df.iterrows():
        rows.append(
            {
                "stock_id": str(row.get("stock_id")),
                "date": str(row.get("date")),
                "revenue": _first_num(row, ["revenue", "Revenue"]),
                "revenue_mom": _first_num(row, ["revenue_month", "revenue_mom"]),
                "revenue_yoy": _first_num(row, ["revenue_year", "revenue_yoy"]),
            }
        )
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO monthly_revenue (stock_id, date, revenue, revenue_mom, revenue_yoy)
            VALUES (:stock_id, :date, :revenue, :revenue_mom, :revenue_yoy)
            ON CONFLICT(stock_id, date) DO UPDATE SET
                revenue = excluded.revenue,
                revenue_mom = excluded.revenue_mom,
                revenue_yoy = excluded.revenue_yoy
            """,
            rows,
        )
    return len(rows)


def upsert_financials(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    pivot = df.pivot_table(index=["stock_id", "date"], columns="type", values="value", aggfunc="last").reset_index()
    rows = []
    for _, row in pivot.iterrows():
        rows.append(
            {
                "stock_id": str(row.get("stock_id")),
                "date": str(row.get("date")),
                "eps": _first_num(row, ["EPS"]),
                "gross_profit": _first_num(row, ["GrossProfit"]),
                "operating_income": _first_num(row, ["OperatingIncome"]),
                "net_income": _first_num(row, ["IncomeAfterTaxes"]),
            }
        )
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO financial_metrics (stock_id, date, eps, gross_profit, operating_income, net_income)
            VALUES (:stock_id, :date, :eps, :gross_profit, :operating_income, :net_income)
            ON CONFLICT(stock_id, date) DO UPDATE SET
                eps = excluded.eps,
                gross_profit = excluded.gross_profit,
                operating_income = excluded.operating_income,
                net_income = excluded.net_income
            """,
            rows,
        )
    return len(rows)


def update_from_finmind(stock_ids: Iterable[str] = STOCK_IDS, start_date: str | None = None, end_date: str | None = None) -> dict:
    init_db()
    client = FinMindClient()
    start = start_date or default_start_date()
    counts = {"daily_prices": 0, "valuation_metrics": 0, "monthly_revenue": 0, "financial_metrics": 0}
    for stock_id in stock_ids:
        counts["daily_prices"] += upsert_daily_prices(client.fetch("TaiwanStockPrice", stock_id, start, end_date))
        counts["valuation_metrics"] += upsert_valuation(client.fetch("TaiwanStockPER", stock_id, start, end_date))
        counts["monthly_revenue"] += upsert_monthly_revenue(client.fetch("TaiwanStockMonthRevenue", stock_id, start, end_date))
        counts["financial_metrics"] += upsert_financials(client.fetch("TaiwanStockFinancialStatements", stock_id, start, end_date))
    return counts


def _num(value) -> float | None:
    if pd.isna(value):
        return None
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def _first_num(row, keys: list[str]) -> float | None:
    for key in keys:
        if key in row:
            value = _num(row.get(key))
            if value is not None:
                return value
    return None
