from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .config import DB_PATH
from .stocks import TRACKED_STOCKS


SCHEMA = """
CREATE TABLE IF NOT EXISTS stocks (
    stock_id TEXT PRIMARY KEY,
    stock_name TEXT NOT NULL,
    industry TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_prices (
    stock_id TEXT NOT NULL,
    date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    trading_value REAL,
    PRIMARY KEY (stock_id, date),
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id)
);

CREATE TABLE IF NOT EXISTS valuation_metrics (
    stock_id TEXT NOT NULL,
    date TEXT NOT NULL,
    per REAL,
    pbr REAL,
    dividend_yield REAL,
    PRIMARY KEY (stock_id, date),
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id)
);

CREATE TABLE IF NOT EXISTS monthly_revenue (
    stock_id TEXT NOT NULL,
    date TEXT NOT NULL,
    revenue REAL,
    revenue_mom REAL,
    revenue_yoy REAL,
    PRIMARY KEY (stock_id, date),
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id)
);

CREATE TABLE IF NOT EXISTS financial_metrics (
    stock_id TEXT NOT NULL,
    date TEXT NOT NULL,
    eps REAL,
    gross_profit REAL,
    operating_income REAL,
    net_income REAL,
    PRIMARY KEY (stock_id, date),
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id)
);

CREATE TABLE IF NOT EXISTS risk_scores (
    stock_id TEXT NOT NULL,
    date TEXT NOT NULL,
    total_score REAL NOT NULL,
    volatility_score REAL NOT NULL,
    drawdown_score REAL NOT NULL,
    volume_score REAL NOT NULL,
    valuation_score REAL NOT NULL,
    fundamental_score REAL NOT NULL,
    risk_level TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (stock_id, date),
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id)
);

CREATE TABLE IF NOT EXISTS update_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT,
    updated_at TEXT NOT NULL
);
"""


def ensure_parent(path: Path = DB_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def connect(path: Path = DB_PATH) -> sqlite3.Connection:
    ensure_parent(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_connection(path: Path = DB_PATH) -> Iterator[sqlite3.Connection]:
    conn = connect(path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(path: Path = DB_PATH) -> None:
    with get_connection(path) as conn:
        conn.executescript(SCHEMA)
        conn.executemany(
            """
            INSERT INTO stocks (stock_id, stock_name, industry, category)
            VALUES (:stock_id, :stock_name, :industry, :category)
            ON CONFLICT(stock_id) DO UPDATE SET
                stock_name = excluded.stock_name,
                industry = excluded.industry,
                category = excluded.category
            """,
            TRACKED_STOCKS,
        )


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict]:
    return [dict(row) for row in rows]
