from __future__ import annotations

from datetime import date, timedelta
import math
import random

from ..database import get_connection, init_db
from ..stocks import TRACKED_STOCKS


def seed_demo_data(days: int = 260) -> dict:
    init_db()
    rng = random.Random(20260619)
    today = date.today()
    trading_dates = [today - timedelta(days=i) for i in range(days * 2) if (today - timedelta(days=i)).weekday() < 5]
    trading_dates = list(reversed(trading_dates[-days:]))

    price_rows = []
    valuation_rows = []
    revenue_rows = []
    financial_rows = []

    for index, stock in enumerate(TRACKED_STOCKS):
        stock_id = stock["stock_id"]
        base = 40 + index * 18 + rng.random() * 15
        drift = 0.0005 + (index % 5) * 0.00015
        shock = 0.01 + (index % 4) * 0.0025
        close = base
        monthly_base = 30_000_000 + index * 2_000_000

        for n, day in enumerate(trading_dates):
            seasonal = math.sin(n / 19 + index) * 0.012
            ret = drift + seasonal + rng.gauss(0, shock)
            if index in {5, 9, 14} and n > days - 25:
                ret -= 0.012
            close = max(8, close * (1 + ret))
            open_price = close * (1 + rng.gauss(0, 0.006))
            high = max(open_price, close) * (1 + abs(rng.gauss(0, 0.009)))
            low = min(open_price, close) * (1 - abs(rng.gauss(0, 0.009)))
            volume = (2_000_000 + index * 180_000) * (1 + abs(rng.gauss(0, 0.35)))
            if index in {2, 7, 17} and n > days - 10:
                volume *= 2.4
            price_rows.append((stock_id, day.isoformat(), open_price, high, low, close, volume, volume * close))

            if n % 5 == 0:
                per = max(6, 14 + (index % 8) * 2 + rng.gauss(0, 2))
                pbr = max(0.7, 1.4 + (index % 6) * 0.35 + rng.gauss(0, 0.25))
                valuation_rows.append((stock_id, day.isoformat(), per, pbr, max(0, 3.2 - pbr * 0.35)))

        for month_offset in range(14):
            month_date = today.replace(day=1) - timedelta(days=month_offset * 30)
            revenue_yoy = 8 + rng.gauss(0, 8) - (12 if index in {5, 9, 14} and month_offset < 3 else 0)
            revenue_mom = rng.gauss(0, 6)
            revenue = monthly_base * (1 + revenue_yoy / 100) * (1 + rng.gauss(0, 0.04))
            revenue_rows.append((stock_id, month_date.isoformat(), revenue, revenue_mom, revenue_yoy))

        for quarter_offset in range(8):
            q_date = today - timedelta(days=quarter_offset * 91)
            eps = max(-2, 1.2 + (index % 6) * 0.6 + rng.gauss(0, 0.7))
            if index in {5, 9, 14} and quarter_offset < 2:
                eps -= 1.4
            gross_profit = monthly_base * 2.8 * (0.25 + (index % 5) * 0.03)
            operating_income = gross_profit * (0.55 + rng.random() * 0.2)
            net_income = operating_income * (0.7 + rng.random() * 0.2)
            financial_rows.append((stock_id, q_date.isoformat(), eps, gross_profit, operating_income, net_income))

    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO daily_prices (stock_id, date, open, high, low, close, volume, trading_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(stock_id, date) DO UPDATE SET
                open = excluded.open, high = excluded.high, low = excluded.low,
                close = excluded.close, volume = excluded.volume, trading_value = excluded.trading_value
            """,
            price_rows,
        )
        conn.executemany(
            """
            INSERT INTO valuation_metrics (stock_id, date, per, pbr, dividend_yield)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(stock_id, date) DO UPDATE SET
                per = excluded.per, pbr = excluded.pbr, dividend_yield = excluded.dividend_yield
            """,
            valuation_rows,
        )
        conn.executemany(
            """
            INSERT INTO monthly_revenue (stock_id, date, revenue, revenue_mom, revenue_yoy)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(stock_id, date) DO UPDATE SET
                revenue = excluded.revenue, revenue_mom = excluded.revenue_mom, revenue_yoy = excluded.revenue_yoy
            """,
            revenue_rows,
        )
        conn.executemany(
            """
            INSERT INTO financial_metrics (stock_id, date, eps, gross_profit, operating_income, net_income)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(stock_id, date) DO UPDATE SET
                eps = excluded.eps, gross_profit = excluded.gross_profit,
                operating_income = excluded.operating_income, net_income = excluded.net_income
            """,
            financial_rows,
        )
    return {
        "daily_prices": len(price_rows),
        "valuation_metrics": len(valuation_rows),
        "monthly_revenue": len(revenue_rows),
        "financial_metrics": len(financial_rows),
    }
