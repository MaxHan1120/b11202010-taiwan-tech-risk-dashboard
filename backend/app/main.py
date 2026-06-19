from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .database import get_connection, init_db, rows_to_dicts
from .ingestion.finmind import update_from_finmind
from .ingestion.seed import seed_demo_data
from .processing.risk import compute_all_risk_scores

app = FastAPI(title="Taiwan Tech Stock Risk Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PortfolioHolding(BaseModel):
    stock_id: str
    weight: float = Field(gt=0)


class PortfolioRequest(BaseModel):
    holdings: list[PortfolioHolding]


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/stocks")
def stocks() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM stocks ORDER BY stock_id").fetchall()
    return rows_to_dicts(rows)


@app.get("/api/risk/latest")
def latest_risk() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT s.stock_id, s.stock_name, s.industry, s.category,
                   r.date, r.total_score, r.volatility_score, r.drawdown_score,
                   r.volume_score, r.valuation_score, r.fundamental_score,
                   r.risk_level, r.updated_at,
                   p.close, p.volume
            FROM risk_scores r
            JOIN stocks s ON s.stock_id = r.stock_id
            LEFT JOIN daily_prices p ON p.stock_id = r.stock_id AND p.date = r.date
            WHERE r.date = (SELECT MAX(r2.date) FROM risk_scores r2 WHERE r2.stock_id = r.stock_id)
            ORDER BY r.total_score DESC
            """
        ).fetchall()
    return rows_to_dicts(rows)


@app.get("/api/risk/history/{stock_id}")
def risk_history(stock_id: str) -> list[dict[str, Any]]:
    require_stock(stock_id)
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM risk_scores WHERE stock_id = ? ORDER BY date",
            (stock_id,),
        ).fetchall()
    return rows_to_dicts(rows)


@app.get("/api/stocks/{stock_id}/prices")
def prices(stock_id: str) -> list[dict[str, Any]]:
    require_stock(stock_id)
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM daily_prices WHERE stock_id = ? ORDER BY date",
            (stock_id,),
        ).fetchall()
    return rows_to_dicts(rows)


@app.get("/api/stocks/{stock_id}/fundamentals")
def fundamentals(stock_id: str) -> dict[str, Any]:
    require_stock(stock_id)
    with get_connection() as conn:
        valuation = rows_to_dicts(conn.execute("SELECT * FROM valuation_metrics WHERE stock_id = ? ORDER BY date", (stock_id,)).fetchall())
        revenue = rows_to_dicts(conn.execute("SELECT * FROM monthly_revenue WHERE stock_id = ? ORDER BY date", (stock_id,)).fetchall())
        financials = rows_to_dicts(conn.execute("SELECT * FROM financial_metrics WHERE stock_id = ? ORDER BY date", (stock_id,)).fetchall())
    return {"valuation": valuation, "monthly_revenue": revenue, "financial_metrics": financials}


@app.get("/api/stocks/{stock_id}/summary")
def stock_summary(stock_id: str) -> dict[str, Any]:
    require_stock(stock_id)
    with get_connection() as conn:
        stock = conn.execute("SELECT * FROM stocks WHERE stock_id = ?", (stock_id,)).fetchone()
        latest_risk_row = conn.execute(
            "SELECT * FROM risk_scores WHERE stock_id = ? ORDER BY date DESC LIMIT 1",
            (stock_id,),
        ).fetchone()
        latest_price = conn.execute(
            "SELECT * FROM daily_prices WHERE stock_id = ? ORDER BY date DESC LIMIT 1",
            (stock_id,),
        ).fetchone()
        latest_valuation = conn.execute(
            "SELECT * FROM valuation_metrics WHERE stock_id = ? ORDER BY date DESC LIMIT 1",
            (stock_id,),
        ).fetchone()
        latest_revenue = conn.execute(
            "SELECT * FROM monthly_revenue WHERE stock_id = ? ORDER BY date DESC LIMIT 1",
            (stock_id,),
        ).fetchone()
        latest_financials = conn.execute(
            "SELECT * FROM financial_metrics WHERE stock_id = ? ORDER BY date DESC LIMIT 1",
            (stock_id,),
        ).fetchone()
    return {
        "stock": dict(stock),
        "risk": dict(latest_risk_row) if latest_risk_row else None,
        "price": dict(latest_price) if latest_price else None,
        "valuation": dict(latest_valuation) if latest_valuation else None,
        "revenue": dict(latest_revenue) if latest_revenue else None,
        "financials": dict(latest_financials) if latest_financials else None,
    }


@app.post("/api/portfolio/analyze")
def portfolio_analyze(request: PortfolioRequest) -> dict[str, Any]:
    if not request.holdings:
        raise HTTPException(status_code=400, detail="Portfolio must include at least one holding.")
    weight_sum = sum(item.weight for item in request.holdings)
    if weight_sum <= 0:
        raise HTTPException(status_code=400, detail="Portfolio weights must be positive.")

    stock_ids = [item.stock_id for item in request.holdings]
    with get_connection() as conn:
        placeholders = ",".join("?" for _ in stock_ids)
        rows = rows_to_dicts(
            conn.execute(
                f"""
                SELECT s.stock_id, s.stock_name, s.industry, s.category,
                       r.total_score, r.risk_level
                FROM stocks s
                LEFT JOIN risk_scores r ON r.stock_id = s.stock_id
                 AND r.date = (SELECT MAX(date) FROM risk_scores WHERE stock_id = s.stock_id)
                WHERE s.stock_id IN ({placeholders})
                """,
                stock_ids,
            ).fetchall()
        )
    found = {row["stock_id"]: row for row in rows}
    missing = [stock_id for stock_id in stock_ids if stock_id not in found]
    if missing:
        raise HTTPException(status_code=404, detail=f"Unknown stock_id values: {', '.join(missing)}")

    normalized = []
    weighted_score = 0.0
    exposure: dict[str, float] = {}
    for holding in request.holdings:
        row = found[holding.stock_id]
        weight = holding.weight / weight_sum
        risk = row.get("total_score") or 35
        weighted_score += weight * risk
        exposure[row["industry"]] = exposure.get(row["industry"], 0) + weight
        normalized.append({**row, "input_weight": holding.weight, "normalized_weight": round(weight * 100, 2)})

    return {
        "portfolio_score": round(weighted_score, 2),
        "risk_level": portfolio_level(weighted_score),
        "weight_sum": weight_sum,
        "industry_exposure": [{"industry": key, "weight": round(value * 100, 2)} for key, value in sorted(exposure.items(), key=lambda item: item[1], reverse=True)],
        "holdings": sorted(normalized, key=lambda row: row.get("total_score") or 0, reverse=True),
    }


@app.post("/api/update-data")
def update_data(use_demo_data: bool = False) -> dict[str, Any]:
    try:
        counts = seed_demo_data() if use_demo_data else update_from_finmind()
        risk_counts = compute_all_risk_scores()
        status = "ok"
        message = "updated"
    except Exception as exc:
        counts = seed_demo_data()
        risk_counts = compute_all_risk_scores()
        status = "fallback_demo_data"
        message = f"FinMind update failed; demo data seeded instead: {exc}"
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO update_log (source, status, message, updated_at) VALUES (?, ?, ?, ?)",
            ("finmind" if not use_demo_data else "demo", status, message, datetime.now(timezone.utc).isoformat()),
        )
    return {"status": status, "message": message, "ingestion": counts, "processing": risk_counts}


def require_stock(stock_id: str) -> None:
    with get_connection() as conn:
        row = conn.execute("SELECT stock_id FROM stocks WHERE stock_id = ?", (stock_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Unknown stock_id: {stock_id}")


def portfolio_level(score: float) -> str:
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"
