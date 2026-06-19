const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

async function request(path, options) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

export const api = {
  stocks: () => request("/api/stocks"),
  latestRisk: () => request("/api/risk/latest"),
  riskHistory: (stockId) => request(`/api/risk/history/${stockId}`),
  prices: (stockId) => request(`/api/stocks/${stockId}/prices`),
  fundamentals: (stockId) => request(`/api/stocks/${stockId}/fundamentals`),
  summary: (stockId) => request(`/api/stocks/${stockId}/summary`),
  portfolio: (holdings) =>
    request("/api/portfolio/analyze", {
      method: "POST",
      body: JSON.stringify({ holdings })
    }),
  updateDemoData: () => request("/api/update-data?use_demo_data=true", { method: "POST" })
};
