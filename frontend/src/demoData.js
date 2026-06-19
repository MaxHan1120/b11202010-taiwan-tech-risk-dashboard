const STOCKS = [
  ["2330", "TSMC", "Semiconductor Foundry", "Semiconductor"],
  ["2454", "MediaTek", "IC Design", "Semiconductor"],
  ["2303", "UMC", "Semiconductor Foundry", "Semiconductor"],
  ["3711", "ASE Technology", "Packaging and Testing", "Semiconductor"],
  ["3034", "Novatek", "IC Design", "Semiconductor"],
  ["2379", "Realtek", "IC Design", "Semiconductor"],
  ["3443", "GUC", "IC Design", "Semiconductor"],
  ["3661", "Alchip", "IC Design", "Semiconductor"],
  ["6488", "GlobalWafers", "Silicon Wafer", "Semiconductor"],
  ["5347", "Vanguard International Semiconductor", "Semiconductor Foundry", "Semiconductor"],
  ["2408", "Nanya Technology", "Memory", "Technology"],
  ["2344", "Winbond", "Memory", "Technology"],
  ["2382", "Quanta", "Server and PC ODM", "Technology"],
  ["2356", "Inventec", "Server and PC ODM", "Technology"],
  ["3231", "Wistron", "Server and PC ODM", "Technology"],
  ["2324", "Compal", "Server and PC ODM", "Technology"],
  ["2357", "ASUS", "PC Brand", "Technology"],
  ["2308", "Delta Electronics", "Power and Components", "Technology"],
  ["2317", "Hon Hai", "EMS", "Technology"],
  ["3008", "Largan Precision", "Optics", "Technology"]
];

const BASE_PRICES = {
  "2330": 970,
  "2454": 1380,
  "2303": 52,
  "3711": 170,
  "3034": 560,
  "2379": 520,
  "3443": 1550,
  "3661": 2850,
  "6488": 430,
  "5347": 82,
  "2408": 72,
  "2344": 28,
  "2382": 285,
  "2356": 54,
  "3231": 108,
  "2324": 39,
  "2357": 610,
  "2308": 395,
  "2317": 205,
  "3008": 2680
};

const latestDate = "2026-06-18";
const updatedAt = "2026-06-19T00:30:00.000Z";

export const demoStocks = STOCKS.map(([stock_id, stock_name, industry, category]) => ({
  stock_id,
  stock_name,
  industry,
  category
}));

export const demoLatestRisk = demoStocks
  .map((stock, index) => {
    const volatility_score = clamp(28 + ((index * 11) % 66));
    const drawdown_score = clamp(22 + ((index * 17) % 72));
    const volume_score = clamp(18 + ((index * 13) % 74));
    const valuation_score = clamp(20 + ((index * 19) % 70));
    const fundamental_score = clamp(16 + ((index * 23) % 76));
    const total_score =
      volatility_score * 0.25 +
      drawdown_score * 0.25 +
      volume_score * 0.2 +
      valuation_score * 0.15 +
      fundamental_score * 0.15;
    return {
      ...stock,
      date: latestDate,
      close: Number((BASE_PRICES[stock.stock_id] * (0.96 + index * 0.006)).toFixed(2)),
      volume: 24000000 + index * 1850000,
      volatility_score,
      drawdown_score,
      volume_score,
      valuation_score,
      fundamental_score,
      total_score: Number(total_score.toFixed(2)),
      risk_level: riskLevel(total_score),
      updated_at: updatedAt
    };
  })
  .sort((a, b) => b.total_score - a.total_score);

export function getDemoPrices(stockId) {
  const base = BASE_PRICES[stockId] || 100;
  const offset = Number(stockId.slice(-2));
  return Array.from({ length: 120 }, (_, index) => {
    const trend = 1 + (index - 60) * 0.0015;
    const wave = Math.sin((index + offset) / 7) * 0.035;
    const close = base * trend * (1 + wave);
    return {
      stock_id: stockId,
      date: dateFromIndex(index),
      open: Number((close * 0.992).toFixed(2)),
      high: Number((close * 1.018).toFixed(2)),
      low: Number((close * 0.976).toFixed(2)),
      close: Number(close.toFixed(2)),
      volume: Math.round(12000000 + ((index + offset) % 35) * 720000)
    };
  });
}

export function getDemoRiskHistory(stockId) {
  const latest = demoLatestRisk.find((item) => item.stock_id === stockId) || demoLatestRisk[0];
  const offset = Number(stockId.slice(-2));
  return Array.from({ length: 120 }, (_, index) => {
    const total_score = clamp(latest.total_score + Math.sin((index + offset) / 9) * 10 - 6 + index * 0.04);
    return {
      stock_id: stockId,
      date: dateFromIndex(index),
      total_score: Number(total_score.toFixed(2)),
      volatility_score: clamp(total_score + 4),
      drawdown_score: clamp(total_score - 3),
      volume_score: clamp(total_score + 8),
      valuation_score: clamp(total_score - 5),
      fundamental_score: clamp(total_score - 8),
      risk_level: riskLevel(total_score),
      updated_at: updatedAt
    };
  });
}

export function getDemoFundamentals(stockId) {
  const base = BASE_PRICES[stockId] || 100;
  const offset = Number(stockId.slice(-2));
  return {
    valuation: Array.from({ length: 8 }, (_, index) => ({
      stock_id: stockId,
      date: monthFromIndex(index),
      per: Number((14 + ((index + offset) % 18) * 0.9).toFixed(2)),
      pbr: Number((1.4 + ((index + offset) % 12) * 0.22).toFixed(2)),
      dividend_yield: Number((1.2 + ((index + offset) % 8) * 0.28).toFixed(2))
    })),
    monthly_revenue: Array.from({ length: 8 }, (_, index) => ({
      stock_id: stockId,
      date: monthFromIndex(index),
      revenue: Math.round(base * 1000000 * (1 + index * 0.018)),
      revenue_mom: Number((Math.sin((index + offset) / 3) * 8).toFixed(2)),
      revenue_yoy: Number((5 + Math.cos((index + offset) / 4) * 14).toFixed(2))
    })),
    financial_metrics: Array.from({ length: 6 }, (_, index) => ({
      stock_id: stockId,
      date: quarterFromIndex(index),
      eps: Number((1.2 + base / 650 + index * 0.16).toFixed(2)),
      gross_profit: Math.round(base * 180000 * (1 + index * 0.04)),
      operating_income: Math.round(base * 110000 * (1 + index * 0.035)),
      net_income: Math.round(base * 90000 * (1 + index * 0.03))
    }))
  };
}

export function getDemoSummary(stockId) {
  const stock = demoStocks.find((item) => item.stock_id === stockId);
  const risk = demoLatestRisk.find((item) => item.stock_id === stockId);
  const prices = getDemoPrices(stockId);
  const fundamentals = getDemoFundamentals(stockId);
  return {
    stock,
    risk,
    price: prices[prices.length - 1],
    valuation: fundamentals.valuation[fundamentals.valuation.length - 1],
    revenue: fundamentals.monthly_revenue[fundamentals.monthly_revenue.length - 1],
    financials: fundamentals.financial_metrics[fundamentals.financial_metrics.length - 1]
  };
}

export function analyzeDemoPortfolio(holdings) {
  if (!holdings.length) {
    throw new Error("Portfolio must include at least one holding.");
  }
  const weightSum = holdings.reduce((sum, item) => sum + Number(item.weight || 0), 0);
  const rows = holdings.map((holding) => {
    const risk = demoLatestRisk.find((item) => item.stock_id === holding.stock_id);
    if (!risk) {
      throw new Error(`Unknown stock_id: ${holding.stock_id}`);
    }
    return { ...risk, input_weight: holding.weight, normalized_weight: Number((holding.weight / weightSum * 100).toFixed(2)) };
  });
  const portfolioScore = rows.reduce((sum, row) => sum + row.total_score * row.normalized_weight / 100, 0);
  const exposure = rows.reduce((acc, row) => {
    acc[row.industry] = (acc[row.industry] || 0) + row.normalized_weight;
    return acc;
  }, {});
  return {
    portfolio_score: Number(portfolioScore.toFixed(2)),
    risk_level: riskLevel(portfolioScore),
    weight_sum: weightSum,
    industry_exposure: Object.entries(exposure).map(([industry, weight]) => ({ industry, weight: Number(weight.toFixed(2)) })),
    holdings: rows.sort((a, b) => b.total_score - a.total_score)
  };
}

function dateFromIndex(index) {
  const date = new Date(Date.UTC(2026, 0, 2 + index));
  return date.toISOString().slice(0, 10);
}

function monthFromIndex(index) {
  const month = String(index + 1).padStart(2, "0");
  return `2026-${month}-01`;
}

function quarterFromIndex(index) {
  const quarter = (index % 4) + 1;
  const year = 2025 + Math.floor(index / 4);
  return `${year}-Q${quarter}`;
}

function clamp(value) {
  return Math.max(0, Math.min(100, Number(value.toFixed(2))));
}

function riskLevel(score) {
  if (score >= 70) return "High";
  if (score >= 40) return "Medium";
  return "Low";
}
