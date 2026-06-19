# Evidence Register

| Fact Or Claim | Source Type | Source Link Or Path | Retrieved Or Observed | Confidence | Notes |
| --- | --- | --- | --- | --- | --- |
| Product is a risk monitoring dashboard, not investment advice or price prediction. | Local documentation | `README.md` | 2026-06-19 | High | Repeated in project positioning. |
| Dashboard tracks a fixed 20-stock Taiwan semiconductor and technology universe. | Local code and docs | `backend/app/stocks.py`, `README.md` | 2026-06-19 | High | Code is canonical for current app. |
| Risk score weights are 25/25/20/15/15 across volatility, drawdown, volume, valuation, and fundamental components. | Local code | `backend/app/processing/risk.py` | 2026-06-19 | High | `WEIGHTS` constant is canonical. |
| Risk levels are Low below 40, Medium 40-69, High 70+. | Local code and docs | `backend/app/processing/risk.py`, `README.md` | 2026-06-19 | High | Tests cover thresholds. |
| Main SQLite tables are `stocks`, `daily_prices`, `valuation_metrics`, `monthly_revenue`, `financial_metrics`, `risk_scores`, and `update_log`. | Local code | `backend/app/database.py` | 2026-06-19 | High | Schema defines primary keys and columns. |
| Live data source design uses FinMind datasets for price, PER/PBR, monthly revenue, and financial statements. | Local code and docs | `backend/app/ingestion/finmind.py`, `README.md` | 2026-06-19 | Medium | Live sample validation still open. |
| Demo mode uses deterministic generated data and should not be treated as live market facts. | Local code | `backend/app/ingestion/seed.py` | 2026-06-19 | High | Generator uses fixed random seed. |
