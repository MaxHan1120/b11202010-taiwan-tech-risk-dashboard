# Source Inventory

## Coverage

- Coverage level: Directional
- Sources checked: local README, backend SQLite schema, stock universe code, risk scoring implementation, FastAPI implementation, frontend page structure.
- Missing high-value lanes: live FinMind sample validation, official TWSE/MOPS schema comparison, deployed production logs, user demand evidence sources.
- Rejected or lower-confidence candidates: generated demo SQLite rows were not treated as market truth; frontend labels were treated as UI context, not canonical metric definitions.

## Sources

| Source | Type | Locator | Connector Or Tool | Permission Status | Last Checked | Supports | Gaps Or Caveats | Automation Eligible | Update Boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Project README | Local documentation | `README.md` | Local filesystem | User workspace | 2026-06-19 | Product positioning, architecture, run instructions, formula summary | High-level; implementation can diverge | Yes | May draft updates only |
| SQLite schema | Local code | `backend/app/database.py` | Local filesystem | User workspace | 2026-06-19 | Canonical table names, columns, primary keys, join keys | No row-level data validation | Yes | May draft updates only |
| Stock universe | Local code | `backend/app/stocks.py` | Local filesystem | User workspace | 2026-06-19 | 20 tracked stocks, labels, industries, categories | Fixed prototype universe | Yes | May draft updates only |
| Risk score implementation | Local code | `backend/app/processing/risk.py` | Local filesystem | User workspace | 2026-06-19 | Component definitions, weights, thresholds, fallback defaults | Prototype rules; no statistical calibration | Yes | May draft updates only |
| API implementation | Local code | `backend/app/main.py` | Local filesystem | User workspace | 2026-06-19 | Endpoint behavior, latest ranking query, portfolio analysis | Response schemas are code-defined, not OpenAPI-reviewed | Yes | May draft updates only |
| FinMind ingestion code | Local code | `backend/app/ingestion/finmind.py` | Local filesystem | User workspace | 2026-06-19 | Intended FinMind datasets and upsert behavior | Live field mappings should be validated with token-backed samples | Yes | May draft updates only |
| Demo seed generator | Local code | `backend/app/ingestion/seed.py` | Local filesystem | User workspace | 2026-06-19 | Deterministic fallback data shape | Not real market evidence | Yes | May draft updates only |
| Frontend pages | Local code | `frontend/src/pages` | Local filesystem | User workspace | 2026-06-19 | Dashboard surfaces and user workflows | UI labels are not canonical definitions | Yes | May draft updates only |
