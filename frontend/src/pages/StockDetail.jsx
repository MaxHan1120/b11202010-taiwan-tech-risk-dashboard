import { useEffect, useState } from "react";
import { Area, AreaChart, Bar, CartesianGrid, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api.js";
import MetricTile from "../components/MetricTile.jsx";
import RiskBadge from "../components/RiskBadge.jsx";

export default function StockDetail({ stocks, selectedStock, setSelectedStock }) {
  const [summary, setSummary] = useState(null);
  const [prices, setPrices] = useState([]);
  const [riskHistory, setRiskHistory] = useState([]);
  const [fundamentals, setFundamentals] = useState({ valuation: [], monthly_revenue: [], financial_metrics: [] });
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      setError("");
      try {
        const [summaryRow, priceRows, riskRows, fundamentalRows] = await Promise.all([
          api.summary(selectedStock),
          api.prices(selectedStock),
          api.riskHistory(selectedStock),
          api.fundamentals(selectedStock)
        ]);
        setSummary(summaryRow);
        setPrices(priceRows.slice(-120));
        setRiskHistory(riskRows.slice(-120));
        setFundamentals(fundamentalRows);
      } catch (err) {
        setError(err.message);
      }
    }
    if (selectedStock) load();
  }, [selectedStock]);

  const stock = summary?.stock;
  const risk = summary?.risk;
  const valuation = summary?.valuation;
  const revenue = summary?.revenue;
  const financials = summary?.financials;

  return (
    <div className="page-stack">
      <header className="page-header">
        <div>
          <h2>Stock Detail</h2>
          <p>Price movement, risk trend, valuation, and basic fundamental signals for one tracked stock.</p>
        </div>
        <select value={selectedStock} onChange={(event) => setSelectedStock(event.target.value)}>
          {stocks.map((item) => (
            <option key={item.stock_id} value={item.stock_id}>{item.stock_id} {item.stock_name}</option>
          ))}
        </select>
      </header>

      {error && <div className="error-banner">{error}</div>}
      {stock && (
        <>
          <div className="metric-grid five">
            <MetricTile label="Stock" value={`${stock.stock_id} ${stock.stock_name}`} detail={stock.industry} />
            <MetricTile label="Risk Score" value={risk ? Number(risk.total_score).toFixed(1) : "N/A"} detail={risk && <RiskBadge level={risk.risk_level} />} />
            <MetricTile label="Close" value={summary.price ? Number(summary.price.close).toFixed(2) : "N/A"} detail={summary.price?.date} />
            <MetricTile label="PER / PBR" value={valuation ? `${num(valuation.per)} / ${num(valuation.pbr)}` : "N/A"} detail="Latest valuation" />
            <MetricTile label="Revenue YoY" value={revenue ? `${num(revenue.revenue_yoy)}%` : "N/A"} detail="Latest monthly revenue" />
          </div>

          <section className="panel">
            <div className="panel-header"><h3>Price and Volume</h3></div>
            <div className="chart-wrap">
              <ResponsiveContainer width="100%" height={300}>
                <ComposedChart data={prices}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" minTickGap={28} />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Bar yAxisId="right" dataKey="volume" fill="#9db6b1" />
                  <Line yAxisId="left" type="monotone" dataKey="close" stroke="#245c73" dot={false} strokeWidth={2} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </section>

          <section className="panel">
            <div className="panel-header"><h3>Risk Score Trend</h3></div>
            <div className="chart-wrap">
              <ResponsiveContainer width="100%" height={260}>
                <AreaChart data={riskHistory}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" minTickGap={28} />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Area type="monotone" dataKey="total_score" stroke="#d15b3f" fill="#f3c3b6" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </section>

          <section className="panel">
            <div className="panel-header"><h3>Risk Breakdown and Fundamentals</h3></div>
            <div className="breakdown-grid">
              {risk && ["volatility_score", "drawdown_score", "volume_score", "valuation_score", "fundamental_score"].map((key) => (
                <div className="score-row" key={key}>
                  <span>{label(key)}</span>
                  <div><i style={{ width: `${risk[key]}%` }} /></div>
                  <strong>{Number(risk[key]).toFixed(1)}</strong>
                </div>
              ))}
            </div>
            <div className="mini-table-grid">
              <MiniTable title="Valuation" rows={fundamentals.valuation.slice(-5)} columns={["date", "per", "pbr", "dividend_yield"]} />
              <MiniTable title="Monthly Revenue" rows={fundamentals.monthly_revenue.slice(-5)} columns={["date", "revenue", "revenue_mom", "revenue_yoy"]} />
              <MiniTable title="Financials" rows={fundamentals.financial_metrics.slice(-5)} columns={["date", "eps", "gross_profit", "net_income"]} />
            </div>
          </section>
        </>
      )}
    </div>
  );
}

function MiniTable({ title, rows, columns }) {
  return (
    <div className="mini-table">
      <h4>{title}</h4>
      <table>
        <thead>
          <tr>{columns.map((col) => <th key={col}>{col}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={`${title}-${row.date}`}>
              {columns.map((col) => <td key={col}>{typeof row[col] === "number" ? Number(row[col]).toFixed(2) : row[col]}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function num(value) {
  return value === null || value === undefined ? "N/A" : Number(value).toFixed(2);
}

function label(key) {
  return key.replace("_score", "").replace("_", " ");
}
