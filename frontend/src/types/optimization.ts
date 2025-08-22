export interface EfficientFrontierPoint {
  return_pct: number;
  volatility_pct: number;
  weights_pct: number[];
  tickers: string[];
}

export interface MaxSharpePoint {
  return_pct: number;
  volatility_pct: number;
  weights_pct: number[];
  sharpe_ratio: number;
  tickers: string[];
}

export interface PortfolioOptimizationResponse {
  frontier_points: EfficientFrontierPoint[];
  max_sharpe_point: MaxSharpePoint;
  risk_free_rate_pct: number;
}
