# Taiwan Semiconductor & Tech Stock Risk Dashboard

This repository contains a full-stack prototype for the Big Data Systems final project. The product is a risk monitoring dashboard for Taiwan retail investors who track semiconductor and technology stocks.

The system does not predict prices or provide buy/sell recommendations. It turns public market and fundamental data into explainable risk scores that help users inspect risk changes faster.

## Tracked Stock Universe

The first version tracks 20 Taiwan semiconductor and technology stocks:

```text
2330 TSMC
2454 MediaTek
2303 UMC
3711 ASE Technology
3034 Novatek
2379 Realtek
3443 GUC
3661 Alchip
6488 GlobalWafers
5347 Vanguard International Semiconductor
2408 Nanya Technology
2344 Winbond
2382 Quanta
2356 Inventec
3231 Wistron
2324 Compal
2357 ASUS
2308 Delta Electronics
2317 Hon Hai
3008 Largan Precision
```

## Architecture

```text
FinMind / public stock data
        |
        v
Python ingestion scripts
        |
        v
SQLite database
        |
        v
Risk scoring pipeline
        |
        v
FastAPI backend
        |
        v
React + Vite dashboard
```

Main folders:

```text
backend/app/          FastAPI app, ingestion, database, and risk processing
frontend/src/         React dashboard UI
scripts/              Local data update and scoring scripts
tests/                Backend tests
contents/             LaTeX report sections
```

## Risk Score

The dashboard uses an explainable rule-based score:

```text
Total Risk Score =
  25% volatility risk
+ 25% drawdown risk
+ 20% abnormal volume risk
+ 15% valuation risk
+ 15% fundamental risk
```

Risk levels:

```text
Low:    0-39
Medium: 40-69
High:   70-100
```

## Local Setup

Backend:

```powershell
cd D:\College\2025_fall\大數據\final_report
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python scripts\seed_demo_data.py
python scripts\compute_risk_scores.py
uvicorn backend.app.main:app --reload
```

Frontend:

```powershell
cd D:\College\2025_fall\大數據\final_report\frontend
npm install
npm run dev
```

Open the Vite URL, usually:

```text
http://localhost:5173
```

## Updating Data

For a reliable demo without API credentials:

```powershell
python scripts\seed_demo_data.py
python scripts\compute_risk_scores.py
```

For FinMind data, set a token when available:

```powershell
$env:FINMIND_TOKEN="your-token"
python scripts\update_data.py
python scripts\compute_risk_scores.py
```

The production design is a daily batch job after market close:

```text
Every trading day 19:00:
1. Fetch latest market and valuation data.
2. Check monthly revenue and financial statement updates.
3. Recompute risk scores.
4. Serve updated dashboard data through FastAPI.
```

## API Endpoints

```text
GET  /api/stocks
GET  /api/risk/latest
GET  /api/risk/history/{stock_id}
GET  /api/stocks/{stock_id}/prices
GET  /api/stocks/{stock_id}/fundamentals
GET  /api/stocks/{stock_id}/summary
POST /api/portfolio/analyze
POST /api/update-data
```

## Deployment

Recommended deployment:

- Frontend: Vercel
- Backend: Render
- Database: SQLite for prototype; PostgreSQL if persistent cloud storage is required

Set `VITE_API_BASE_URL` in Vercel to the Render backend URL.

## Tests

```powershell
pytest
```

The tests cover risk score thresholds, score range behavior, seeded API output, and unknown stock errors.

## Report

The LaTeX report uses XeLaTeX:

```powershell
xelatex main.tex
bibtex main
xelatex main.tex
xelatex main.tex
```

Final submission requirements:

- Rename the final PDF to `<student_id>.pdf`.
- Put the GitHub repository URL on the first page.
- Put the live demo URL on the first page if deployed.
