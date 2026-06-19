import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import MetricTile from "../components/MetricTile.jsx";
import RiskBadge from "../components/RiskBadge.jsx";

export default function Overview({ latestRisk, stocks, onSelectStock }) {
  const highRisk = latestRisk.filter((item) => item.risk_level === "High");
  const mediumRisk = latestRisk.filter((item) => item.risk_level === "Medium");
  const topRisk = latestRisk.slice(0, 8);
  const avgScore = latestRisk.length
    ? (latestRisk.reduce((sum, item) => sum + item.total_score, 0) / latestRisk.length).toFixed(1)
    : "N/A";

  return (
    <div className="page-stack">
      <header className="page-header">
        <div>
          <h2>Risk Overview</h2>
          <p>Daily risk ranking for the tracked Taiwan semiconductor and technology stock universe.</p>
        </div>
      </header>

      <div className="metric-grid">
        <MetricTile label="Tracked Stocks" value={stocks.length} detail="Semiconductor and technology names" />
        <MetricTile label="Average Risk Score" value={avgScore} detail="Weighted rule-based score" />
        <MetricTile label="High Risk" value={highRisk.length} detail="Score >= 70" />
        <MetricTile label="Medium Risk" value={mediumRisk.length} detail="Score 40-69" />
      </div>

      <section className="panel">
        <div className="panel-header">
          <h3>Highest Risk Stocks</h3>
        </div>
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={topRisk}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="stock_id" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="total_score" fill="#d15b3f" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <h3>Stock Risk Ranking</h3>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Stock</th>
                <th>Industry</th>
                <th>Close</th>
                <th>Risk</th>
                <th>Level</th>
              </tr>
            </thead>
            <tbody>
              {latestRisk.map((item) => (
                <tr key={item.stock_id} onClick={() => onSelectStock(item.stock_id)}>
                  <td>
                    <strong>{item.stock_id}</strong>
                    <span>{item.stock_name}</span>
                  </td>
                  <td>{item.industry}</td>
                  <td>{Number(item.close || 0).toFixed(2)}</td>
                  <td>{Number(item.total_score).toFixed(1)}</td>
                  <td><RiskBadge level={item.risk_level} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
