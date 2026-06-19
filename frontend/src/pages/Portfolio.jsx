import { useMemo, useState } from "react";
import { Pie, PieChart, ResponsiveContainer, Tooltip, Cell } from "recharts";
import { api } from "../api.js";
import MetricTile from "../components/MetricTile.jsx";
import RiskBadge from "../components/RiskBadge.jsx";

const COLORS = ["#245c73", "#d15b3f", "#799f6f", "#d8a54a", "#5f6f89", "#8f6a9a"];

export default function Portfolio({ stocks, latestRisk }) {
  const [rows, setRows] = useState([
    { stock_id: "2330", weight: 35 },
    { stock_id: "2454", weight: 20 },
    { stock_id: "2308", weight: 20 },
    { stock_id: "2317", weight: 15 },
    { stock_id: "2382", weight: 10 }
  ]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const highRiskHoldings = useMemo(() => result?.holdings?.filter((item) => item.risk_level === "High") || [], [result]);

  async function analyze() {
    setError("");
    try {
      const holdings = rows.filter((row) => row.stock_id && Number(row.weight) > 0).map((row) => ({ stock_id: row.stock_id, weight: Number(row.weight) }));
      setResult(await api.portfolio(holdings));
    } catch (err) {
      setError(err.message);
    }
  }

  function updateRow(index, patch) {
    setRows((current) => current.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  }

  return (
    <div className="page-stack">
      <header className="page-header">
        <div>
          <h2>Portfolio Watchlist</h2>
          <p>Estimate portfolio-level risk from the latest stock risk scores and industry concentration.</p>
        </div>
      </header>
      {error && <div className="error-banner">{error}</div>}

      <section className="panel">
        <div className="panel-header">
          <h3>Holdings</h3>
          <button className="primary-button" onClick={analyze}>Analyze</button>
        </div>
        <div className="portfolio-editor">
          {rows.map((row, index) => (
            <div className="holding-row" key={index}>
              <select value={row.stock_id} onChange={(event) => updateRow(index, { stock_id: event.target.value })}>
                {stocks.map((stock) => <option key={stock.stock_id} value={stock.stock_id}>{stock.stock_id} {stock.stock_name}</option>)}
              </select>
              <input type="number" min="0" value={row.weight} onChange={(event) => updateRow(index, { weight: event.target.value })} />
              <span>%</span>
            </div>
          ))}
        </div>
      </section>

      {result && (
        <>
          <div className="metric-grid">
            <MetricTile label="Portfolio Risk" value={Number(result.portfolio_score).toFixed(1)} detail={<RiskBadge level={result.risk_level} />} />
            <MetricTile label="Weight Sum" value={`${Number(result.weight_sum).toFixed(1)}%`} detail="Weights are normalized for scoring" />
            <MetricTile label="High Risk Holdings" value={highRiskHoldings.length} detail="Latest stock-level risk" />
            <MetricTile label="Tracked Universe" value={latestRisk.length} detail="Available scored stocks" />
          </div>

          <section className="panel two-column">
            <div>
              <div className="panel-header"><h3>Industry Exposure</h3></div>
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie data={result.industry_exposure} dataKey="weight" nameKey="industry" outerRadius={96}>
                    {result.industry_exposure.map((_, index) => <Cell key={index} fill={COLORS[index % COLORS.length]} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div>
              <div className="panel-header"><h3>Holding Risk</h3></div>
              <div className="factor-list">
                {result.holdings.map((item) => (
                  <button key={item.stock_id}>
                    <span><strong>{item.stock_id}</strong>{item.stock_name}</span>
                    <span>{Number(item.total_score || 35).toFixed(1)}</span>
                    <RiskBadge level={item.risk_level} />
                  </button>
                ))}
              </div>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
