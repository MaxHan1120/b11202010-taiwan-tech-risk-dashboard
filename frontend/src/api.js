import {
  analyzeDemoPortfolio,
  demoLatestRisk,
  demoStocks,
  getDemoFundamentals,
  getDemoPrices,
  getDemoRiskHistory,
  getDemoSummary
} from "./demoData.js";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

async function request(path, fallback, options) {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options
    });
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.detail || `Request failed: ${response.status}`);
    }
    return response.json();
  } catch (error) {
    if (fallback) {
      return typeof fallback === "function" ? fallback() : fallback;
    }
    throw error;
  }
}

export const api = {
  stocks: () => request("/api/stocks", demoStocks),
  latestRisk: () => request("/api/risk/latest", demoLatestRisk),
  riskHistory: (stockId) => request(`/api/risk/history/${stockId}`, () => getDemoRiskHistory(stockId)),
  prices: (stockId) => request(`/api/stocks/${stockId}/prices`, () => getDemoPrices(stockId)),
  fundamentals: (stockId) => request(`/api/stocks/${stockId}/fundamentals`, () => getDemoFundamentals(stockId)),
  summary: (stockId) => request(`/api/stocks/${stockId}/summary`, () => getDemoSummary(stockId)),
  portfolio: (holdings) =>
    request("/api/portfolio/analyze", () => analyzeDemoPortfolio(holdings), {
      method: "POST",
      body: JSON.stringify({ holdings })
    }),
  updateDemoData: () => request("/api/update-data?use_demo_data=true", { status: "static_demo" }, { method: "POST" })
};
