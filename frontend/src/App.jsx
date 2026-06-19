import { useEffect, useMemo, useState } from "react";
import { Activity, BarChart3, Briefcase, Database, RefreshCcw, Search } from "lucide-react";
import Overview from "./pages/Overview.jsx";
import StockDetail from "./pages/StockDetail.jsx";
import RiskFactors from "./pages/RiskFactors.jsx";
import Portfolio from "./pages/Portfolio.jsx";
import { api } from "./api.js";

const tabs = [
  { id: "overview", label: "Overview", icon: Activity },
  { id: "detail", label: "Stock Detail", icon: Search },
  { id: "factors", label: "Risk Factors", icon: BarChart3 },
  { id: "portfolio", label: "Portfolio", icon: Briefcase }
];

export default function App() {
  const [activeTab, setActiveTab] = useState("overview");
  const [stocks, setStocks] = useState([]);
  const [latestRisk, setLatestRisk] = useState([]);
  const [selectedStock, setSelectedStock] = useState("2330");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updating, setUpdating] = useState(false);

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      const [stockRows, riskRows] = await Promise.all([api.stocks(), api.latestRisk()]);
      setStocks(stockRows);
      setLatestRisk(riskRows);
      if (stockRows.length && !stockRows.some((item) => item.stock_id === selectedStock)) {
        setSelectedStock(stockRows[0].stock_id);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function seedDemoData() {
    setUpdating(true);
    setError("");
    try {
      await api.updateDemoData();
      await loadData();
    } catch (err) {
      setError(err.message);
    } finally {
      setUpdating(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const latestUpdate = useMemo(() => {
    const dates = latestRisk.map((item) => item.updated_at).filter(Boolean).sort();
    return dates.length ? new Date(dates[dates.length - 1]).toLocaleString() : "No scored data yet";
  }, [latestRisk]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Database size={24} />
          <div>
            <h1>Tech Risk</h1>
            <p>Taiwan semiconductor and technology watchlist</p>
          </div>
        </div>
        <nav className="tab-list">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                className={activeTab === tab.id ? "tab active" : "tab"}
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                title={tab.label}
              >
                <Icon size={18} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
        <button className="refresh-button" onClick={seedDemoData} disabled={updating} title="Seed demo data and recompute risk scores">
          <RefreshCcw size={18} />
          <span>{updating ? "Updating" : "Seed Demo Data"}</span>
        </button>
        <div className="freshness">
          <span>Latest score update</span>
          <strong>{latestUpdate}</strong>
        </div>
      </aside>

      <main className="main-panel">
        {error && <div className="error-banner">{error}</div>}
        {loading ? (
          <div className="loading">Loading dashboard data...</div>
        ) : (
          <>
            {activeTab === "overview" && (
              <Overview latestRisk={latestRisk} stocks={stocks} onSelectStock={(id) => { setSelectedStock(id); setActiveTab("detail"); }} />
            )}
            {activeTab === "detail" && (
              <StockDetail stocks={stocks} selectedStock={selectedStock} setSelectedStock={setSelectedStock} />
            )}
            {activeTab === "factors" && <RiskFactors latestRisk={latestRisk} onSelectStock={(id) => { setSelectedStock(id); setActiveTab("detail"); }} />}
            {activeTab === "portfolio" && <Portfolio stocks={stocks} latestRisk={latestRisk} />}
          </>
        )}
      </main>
    </div>
  );
}
