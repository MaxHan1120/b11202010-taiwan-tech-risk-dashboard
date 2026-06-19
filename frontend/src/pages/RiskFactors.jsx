import RiskBadge from "../components/RiskBadge.jsx";

const factors = [
  ["volatility_score", "Volatility"],
  ["drawdown_score", "Drawdown"],
  ["volume_score", "Abnormal Volume"],
  ["valuation_score", "Valuation"],
  ["fundamental_score", "Fundamental"]
];

export default function RiskFactors({ latestRisk, onSelectStock }) {
  return (
    <div className="page-stack">
      <header className="page-header">
        <div>
          <h2>Risk Factors</h2>
          <p>Rank stocks by the component that is driving risk instead of only the total score.</p>
        </div>
      </header>
      <div className="factor-grid">
        {factors.map(([key, title]) => (
          <section className="panel" key={key}>
            <div className="panel-header"><h3>{title}</h3></div>
            <div className="factor-list">
              {[...latestRisk].sort((a, b) => b[key] - a[key]).slice(0, 8).map((item) => (
                <button key={`${key}-${item.stock_id}`} onClick={() => onSelectStock(item.stock_id)}>
                  <span>
                    <strong>{item.stock_id}</strong>
                    {item.stock_name}
                  </span>
                  <span>{Number(item[key]).toFixed(1)}</span>
                  <RiskBadge level={item.risk_level} />
                </button>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
